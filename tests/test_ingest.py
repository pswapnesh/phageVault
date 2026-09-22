from pathlib import Path

from phagevault import PhageVault


def test_ingest_fasta_roundtrip(tmp_path):
    fasta = tmp_path / "toy.fna"
    fasta.write_text(
        ">phage1 toy phage\n"
        "ATGAAACGCATTAGCACCACCATTACCACCACCATCACCATTACCACAGGTAACGGTGCGGGCTGA\n"
        ">phage2 toy phage 2\n"
        "ATGAGCACAAAAAAGAAACCATTAACACAAGAGCAGCTTGAGGACGCACGTCGCCTTAAAGCAATT\n"
    )

    db_path = tmp_path / "vault.duckdb"
    with PhageVault(str(db_path)) as vault:
        stats = vault.ingest(str(fasta), source="toy")
        assert stats["genomes"] == 2

        genome_hash = vault.con.execute("SELECT genome_hash FROM genomes LIMIT 1").fetchone()[0]
        vault.annotate_genome(genome_hash, source="manual", key="note", value="test")
        assert vault.genome_annotations(genome_hash) == {("manual", "note"): "test"}

    # re-ingesting the same file is a no-op
    with PhageVault(str(db_path)) as vault:
        stats = vault.ingest(str(fasta), source="toy")
        assert stats["genomes"] == 0
