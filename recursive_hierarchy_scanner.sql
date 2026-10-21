-- Write a recursive CTE to calculate the depth level and build the full lineage path string (/doc_1/chunk_1/chunk_1_1) for nested sub-chunks.
WITH RECURSIVE
    rag_lineage_cte AS (
        SELECT
            chunk_id,
            parent_chunk_id,
            doc_id,
            1 AS depth_level,
            cast(chunk_id AS varchar) AS lineage_path
        FROM
            read_parquet('data/document_chunks.parquet')
        WHERE
            parent_chunk_id IS NULL
        UNION ALL
        SELECT
            doc_chunks.chunk_id,
            doc_chunks.parent_chunk_id,
            doc_chunks.doc_id,
            cte.depth_level + 1,
            cte.lineage_path || '->' || doc_chunks.chunk_id
        FROM
            read_parquet('data/document_chunks.parquet') AS doc_chunks
            INNER JOIN rag_lineage_cte cte ON doc_chunks.parent_chunk_id = cte.chunk_id
    )
SELECT
    *
FROM
    rag_lineage_cte
ORDER BY
    doc_id,
    depth_level;