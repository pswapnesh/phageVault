"""Read/write helpers for the genome_annotations and protein_annotations tables.

Annotations are kept out of the genomes/proteins tables so that any number of
sources (manual curation, pharokka, blast, hmmer, ...) can attach any number
of key/value facts to a genome or protein without schema changes.
"""

import duckdb
import pandas as pd


def add_genome_annotation(con: duckdb.DuckDBPyConnection, genome_hash: str, source: str, key: str, value) -> None:
    con.execute(
        "INSERT OR REPLACE INTO genome_annotations (genome_hash, source, key, value) VALUES (?, ?, ?, ?)",
        [genome_hash, source, key, str(value)],
    )


def add_protein_annotation(con: duckdb.DuckDBPyConnection, protein_hash: str, source: str, key: str, value) -> None:
    con.execute(
        "INSERT OR REPLACE INTO protein_annotations (protein_hash, source, key, value) VALUES (?, ?, ?, ?)",
        [protein_hash, source, key, str(value)],
    )


def get_genome_annotations(con: duckdb.DuckDBPyConnection, genome_hash: str) -> dict:
    rows = con.execute(
        "SELECT source, key, value FROM genome_annotations WHERE genome_hash = ?", [genome_hash]
    ).fetchall()
    return {(source, key): value for source, key, value in rows}


def get_protein_annotations(con: duckdb.DuckDBPyConnection, protein_hash: str) -> dict:
    rows = con.execute(
        "SELECT source, key, value FROM protein_annotations WHERE protein_hash = ?", [protein_hash]
    ).fetchall()
    return {(source, key): value for source, key, value in rows}


def import_genome_annotations_df(con: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> int:
    """Bulk-load annotations from a DataFrame with genome_hash/source/key/value columns."""
    con.register("_genome_anno_df", df)
    con.execute("""
        INSERT OR REPLACE INTO genome_annotations (genome_hash, source, key, value)
        SELECT genome_hash, source, key, value FROM _genome_anno_df
    """)
    return len(df)


def import_protein_annotations_df(con: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> int:
    """Bulk-load annotations from a DataFrame with protein_hash/source/key/value columns."""
    con.register("_protein_anno_df", df)
    con.execute("""
        INSERT OR REPLACE INTO protein_annotations (protein_hash, source, key, value)
        SELECT protein_hash, source, key, value FROM _protein_anno_df
    """)
    return len(df)
