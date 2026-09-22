"""Convenience wrapper tying schema, ingestion, and annotations to one DuckDB connection."""

import duckdb

from .annotations import (
    add_genome_annotation,
    add_protein_annotation,
    get_genome_annotations,
    get_protein_annotations,
    import_genome_annotations_df,
    import_protein_annotations_df,
)
from .ingest import ingest_fasta
from .schema import ensure_schema


class PhageVault:
    def __init__(self, db_path: str):
        self.con = duckdb.connect(db_path)
        ensure_schema(self.con)

    def ingest(self, fasta_path, source, call_genes=True, is_circular=True, min_gene_len=60) -> dict:
        return ingest_fasta(
            self.con, fasta_path, source,
            call_genes_flag=call_genes, is_circular=is_circular, min_gene_len=min_gene_len,
        )

    def annotate_genome(self, genome_hash: str, source: str, key: str, value) -> None:
        add_genome_annotation(self.con, genome_hash, source, key, value)

    def annotate_protein(self, protein_hash: str, source: str, key: str, value) -> None:
        add_protein_annotation(self.con, protein_hash, source, key, value)

    def genome_annotations(self, genome_hash: str) -> dict:
        return get_genome_annotations(self.con, genome_hash)

    def protein_annotations(self, protein_hash: str) -> dict:
        return get_protein_annotations(self.con, protein_hash)

    def import_genome_annotations(self, df) -> int:
        return import_genome_annotations_df(self.con, df)

    def import_protein_annotations(self, df) -> int:
        return import_protein_annotations_df(self.con, df)

    def close(self) -> None:
        self.con.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
