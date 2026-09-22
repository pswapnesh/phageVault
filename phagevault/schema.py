"""DuckDB schema for the phage vault: genomes, proteins, and their annotations."""

import hashlib

import duckdb


def genome_hash(dna_seq: str) -> str:
    return hashlib.sha256(dna_seq.encode()).hexdigest()


def protein_hash(aa_seq: str) -> str:
    return hashlib.sha256(aa_seq.encode()).hexdigest()


def ensure_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("SET preserve_insertion_order = false")

    con.execute("""
        CREATE TABLE IF NOT EXISTS genomes (
            genome_hash         VARCHAR PRIMARY KEY,
            genome_id           VARCHAR,
            readable_genome_id  VARCHAR,
            dna_sequence        TEXT,
            dna_length          INTEGER,
            description         TEXT,
            data_source         VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS proteins (
            protein_hash VARCHAR PRIMARY KEY,
            aa_sequence  TEXT,
            aa_length    INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS genome_proteins (
            genome_hash   VARCHAR,
            protein_hash  VARCHAR,
            protein_order INTEGER,
            begin_pos     INTEGER,
            end_pos       INTEGER,
            strand        VARCHAR,
            score         DOUBLE,
            confidence    DOUBLE,
            PRIMARY KEY (genome_hash, protein_order)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS genome_annotations (
            genome_hash VARCHAR,
            source      VARCHAR,
            key         VARCHAR,
            value       TEXT,
            PRIMARY KEY (genome_hash, source, key)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS protein_annotations (
            protein_hash VARCHAR,
            source       VARCHAR,
            key          VARCHAR,
            value        TEXT,
            PRIMARY KEY (protein_hash, source, key)
        )
    """)
