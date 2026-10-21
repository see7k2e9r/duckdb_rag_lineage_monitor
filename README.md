# DuckDB RAG Lineage Monitor

A small analytics project that uses **DuckDB** to monitor the health of a Retrieval-Augmented
Generation (RAG) ingestion pipeline. It answers three operational questions about embedded
document chunks:

1. **Lineage** — how deep is each chunk nested, and what is its full parent chain?
2. **Embedding quality** — did any chunk produce a degenerate/near-zero embedding vector?
3. **Context budget** — which chunks blow past the model's context window, and how do token
   counts distribute per embedding model?

Everything runs directly against a single Parquet file — no server, no schema load step.

---

## Project Structure

```
duckdb_rag_lineage_monitor/
├── data/
│   └── document_chunks.parquet          # Generated dataset (committed)
├── data_generation/
│   └── generate_data.py                 # Synthetic RAG chunk generator
├── recursive_hierarchy_scanner.sql      # Recursive CTE: depth + lineage path
├── embedding_norm_anomaly_detection.sql # Rolling z-score anomaly detection
├── token_overflow_and_context_window_alert.sql # Per-model token/context stats
├── .vscode/settings.json                # DuckDB data viewer for .parquet files
└── README.md
```

## Dataset

`data/document_chunks.parquet` is produced by
[generate_data.py](data_generation/generate_data.py). Each row is one chunk of a document,
organised as a tree.

| Column | Type | Description |
|---|---|---|
| `chunk_id` | VARCHAR | Unique chunk identifier (`chunk_1`, `chunk_2`, ...) |
| `parent_chunk_id` | VARCHAR | Parent chunk; `NULL` for a document root |
| `doc_id` | VARCHAR | Owning document (`doc_001` ... `doc_050`) |
| `token_count` | INTEGER | Token length of the chunk text |
| `embedding_norm` | DOUBLE | L2 norm of the embedding vector (~1.0 for normalised vectors) |
| `model_version` | VARCHAR | `text-embedding-3-small` (1536-d) or `text-embedding-3-large` (3072-d) |
| `created_at` | TIMESTAMP | Ingestion timestamp, used as the time axis for rolling stats |

The generator builds 50 root chunks, expands each into a tree up to depth 5 (1–3 children per
node) and stops at roughly 1000 rows — 1016 rows with the default arguments. Roughly 6% of child
chunks are deliberately corrupted:

* `zero_embedding` (~3%) — `embedding_norm = 0.001`, a failed/near-zero embedding.
* `token_spike` (~3%) — `token_count = 4500`, an extreme context-length breach.

Data is deterministic (`seed = 42`), so results are reproducible.
