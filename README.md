# PhageVault

A local DuckDB database for phage genomes and their proteins, built from
multi-FASTA (`.fna`) files.

## Install

```bash
pip install git+https://github.com/<user>/PhageVault.git
```

(or, from a local clone: `pip install -e .`)

## Schema

| Table | What it holds |
|---|---|
| `genomes` | One row per DNA sequence: hash, id, sequence, length, source |
| `proteins` | One row per called protein: hash, sequence, length |
| `genome_proteins` | Maps proteins to their genome, position, strand, score |
| `genome_annotations` | `(genome_hash, source, key, value)` — arbitrary facts about a genome |
| `protein_annotations` | `(protein_hash, source, key, value)` — arbitrary facts about a protein |

Genomes and proteins are content-addressed (SHA-256 of the sequence), so
re-ingesting the same sequence is a no-op. Annotations live in their own
tables, keyed by `source`, so multiple tools (manual curation, pharokka,
blast, ...) can each attach facts without schema changes or overwriting
each other.

## Usage

### CLI

```bash
phagevault ingest genomes.fna my_batch --db vault.duckdb
phagevault ingest genomes.fna my_batch --db vault.duckdb --no-genes   # skip gene calling
phagevault stats --db vault.duckdb
```

### Python

```python
from phagevault import PhageVault

with PhageVault("vault.duckdb") as vault:
    vault.ingest("genomes.fna", source="my_batch")

    vault.annotate_genome(genome_hash, source="manual", key="host", value="E. coli")
    print(vault.genome_annotations(genome_hash))

    # vault.con is a live duckdb connection for ad-hoc queries
    vault.con.execute("SELECT readable_genome_id, dna_length FROM genomes").df()
```

### Browse with the DuckDB UI

DuckDB ships a local web UI for browsing tables and running SQL. Point it at
the vault file directly (close any other connection to it first — DuckDB
files are single-writer):

```bash
duckdb vault.duckdb -ui
```

This opens `http://localhost:4213` in your browser with `genomes`,
`proteins`, `genome_proteins`, `genome_annotations`, and `protein_annotations`
ready to explore. First run installs the `ui` extension automatically; you
can also load it manually from inside a session with:

```sql
INSTALL ui;
LOAD ui;
CALL start_ui();
```
