SELECT 
    model_version,
    COUNT(chunk_id) AS total_chunks,
    ROUND(AVG(token_count), 2) AS avg_tokens,
    MAX(token_count) AS max_tokens,
    QUANTILE_CONT(token_count, 0.95) AS p95_tokens,
    COUNT(CASE WHEN token_count > 4000 THEN 1 END) AS context_overflow_count
FROM 'data/document_chunks.parquet'
GROUP BY model_version;