WITH rolling_stats as (
    SELECT 
        chunk_id,
        parent_chunk_id,
        doc_id,
        embedding_norm,
        model_version,
        AVG(embedding_norm) OVER w as mean,
        STDDEV_SAMP(embedding_norm) OVER w as sigma,
        COUNT(*) OVER w as baseline_chunk_count
    FROM read_parquet('data/document_chunks.parquet')
    WINDOW w as (
        PARTITION BY model_version
        ORDER BY created_at
        ROWS BETWEEN 49 PRECEDING and CURRENT ROW
    )
),
z_score_stats as (
    SELECT 
        *,
        ((embedding_norm - mean) / NULLIF(sigma, 0)) as z_score 
    FROM rolling_stats
    WHERE baseline_chunk_count > 25  -- add a check to make sure that there min number of baseline samples to calculate z score for a row
)
SELECT 
    chunk_id, parent_chunk_id, doc_id, embedding_norm, mean, sigma, z_score
FROM z_score_stats
where ABS(z_score) > 3 
ORDER BY doc_id
;