"""Command-line interface: `phagevault ingest ...` / `phagevault stats ...`."""

import argparse

from .db import PhageVault


def cmd_ingest(args):
    with PhageVault(args.db) as vault:
        stats = vault.ingest(
            args.fasta, args.source,
            call_genes=not args.no_genes,
            is_circular=not args.linear,
            min_gene_len=args.min_gene_len,
        )
    print(f"Inserted {stats['genomes']} genomes, {stats['proteins']} proteins from '{args.source}'.")


def cmd_stats(args):
    with PhageVault(args.db) as vault:
        n_genomes = vault.con.execute("SELECT count(*) FROM genomes").fetchone()[0]
        n_proteins = vault.con.execute("SELECT count(*) FROM proteins").fetchone()[0]
        n_sources = vault.con.execute("SELECT count(DISTINCT data_source) FROM genomes").fetchone()[0]
    print(f"genomes:  {n_genomes}")
    print(f"proteins: {n_proteins}")
    print(f"sources:  {n_sources}")


def main():
    parser = argparse.ArgumentParser(prog="phagevault")
    sub = parser.add_subparsers(required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest a multi-FASTA (.fna) file into the database")
    p_ingest.add_argument("fasta", help="Path to a multi-FASTA file of phage genomes")
    p_ingest.add_argument("source", help="Name tag for this batch of genomes")
    p_ingest.add_argument("--db", required=True, help="Path to the DuckDB database file")
    p_ingest.add_argument("--no-genes", action="store_true", help="Skip gene calling, store genomes only")
    p_ingest.add_argument("--linear", action="store_true", help="Treat genomes as linear (default: circular)")
    p_ingest.add_argument("--min-gene-len", type=int, default=60)
    p_ingest.set_defaults(func=cmd_ingest)

    p_stats = sub.add_parser("stats", help="Show database counts")
    p_stats.add_argument("--db", required=True, help="Path to the DuckDB database file")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
