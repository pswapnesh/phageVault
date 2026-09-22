"""Pyrodigal wrapper for calling genes on a DNA sequence."""

import hashlib
from functools import partial
from multiprocessing import Pool, cpu_count

from pyrodigal import GeneFinder


def call_genes(sequence, seq_name, is_circular=True, min_gene_len=60):
    seq_bytes = sequence.encode()
    seq_hash = hashlib.md5(seq_bytes).hexdigest()
    use_meta = len(sequence) < 100000
    custom_overlap = min(60, min_gene_len - 1)

    gf = GeneFinder(
        meta=use_meta,
        closed=is_circular,
        min_gene=min_gene_len,
        max_overlap=custom_overlap
    )
    if not use_meta:
        gf.train(seq_bytes)
    genes = gf.find_genes(seq_bytes)

    return [{
        "gene_id": f"{seq_hash}_{idx}",
        "readable_gene_id": f"{seq_name}_{idx}",
        "order": idx,
        "begin": pred.begin,
        "end": pred.end,
        "strand": "+" if pred.strand == 1 else "-",
        "score": pred.score,
        "confidence": pred.confidence(),
        "sequence": pred.translate(),
    } for idx, pred in enumerate(genes, start=1)]


def process_sequences(sequences, seq_names, **kwargs):
    with Pool(processes=cpu_count()) as pool:
        return pool.starmap(
            partial(call_genes, **kwargs),
            zip(sequences, seq_names)
        )
