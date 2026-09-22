"""Build a phage vault DuckDB from a multi-FASTA (.fna) file."""

import duckdb
import pandas as pd
from Bio import SeqIO
from tqdm import tqdm

from .gene_caller import call_genes
from .schema import ensure_schema, genome_hash, protein_hash


def ingest_fasta(
    con: duckdb.DuckDBPyConnection,
    fasta_path: str,
    source: str,
    call_genes_flag: bool = True,
    is_circular: bool = True,
    min_gene_len: int = 60,
) -> dict:
    ensure_schema(con)
    existing = {r[0] for r in con.execute("SELECT genome_hash FROM genomes").fetchall()}

    genomes, proteins, mappings = [], [], []
    records = list(SeqIO.parse(str(fasta_path), "fasta"))
    for idx, rec in enumerate(tqdm(records, desc=f"Ingesting {source}"), start=1):
        dna = str(rec.seq).upper()
        gh = genome_hash(dna)
        if gh in existing:
            continue

        genomes.append({
            "genome_hash": gh,
            "genome_id": str(rec.id),
            "readable_genome_id": f"{source}_{idx}",
            "dna_sequence": dna,
            "dna_length": len(dna),
            "description": str(rec.description),
            "data_source": source,
        })

        if call_genes_flag:
            for g in call_genes(dna, seq_name=str(rec.id), is_circular=is_circular, min_gene_len=min_gene_len):
                ph = protein_hash(g["sequence"])
                proteins.append({
                    "protein_hash": ph,
                    "aa_sequence": g["sequence"],
                    "aa_length": len(g["sequence"]),
                })
                mappings.append({
                    "genome_hash": gh,
                    "protein_hash": ph,
                    "protein_order": g["order"],
                    "begin_pos": g["begin"],
                    "end_pos": g["end"],
                    "strand": g["strand"],
                    "score": g["score"],
                    "confidence": g["confidence"],
                })

    if not genomes:
        return {"genomes": 0, "proteins": 0}

    genomes_df = pd.DataFrame(genomes)
    con.register("genomes_df", genomes_df)
    con.execute("""
        INSERT OR IGNORE INTO genomes
            (genome_hash, genome_id, readable_genome_id, dna_sequence, dna_length, description, data_source)
        SELECT genome_hash, genome_id, readable_genome_id, dna_sequence, dna_length, description, data_source
        FROM genomes_df
    """)

    if proteins:
        proteins_df = pd.DataFrame(proteins).drop_duplicates("protein_hash")
        con.register("proteins_df", proteins_df)
        con.execute("""
            INSERT OR IGNORE INTO proteins (protein_hash, aa_sequence, aa_length)
            SELECT protein_hash, aa_sequence, aa_length FROM proteins_df
        """)

        mappings_df = pd.DataFrame(mappings)
        con.register("mappings_df", mappings_df)
        con.execute("""
            INSERT OR IGNORE INTO genome_proteins
                (genome_hash, protein_hash, protein_order, begin_pos, end_pos, strand, score, confidence)
            SELECT genome_hash, protein_hash, protein_order, begin_pos, end_pos, strand, score, confidence
            FROM mappings_df
        """)

    return {"genomes": len(genomes), "proteins": len(proteins)}
