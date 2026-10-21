import os
import random
import numpy as np
import pandas as pd

def generate_mock_rag_dataset(num_roots=50, max_depth=5, total_target_rows=1000):
    np.random.seed(42)
    random.seed(42)
    
    records = []
    models = ["text-embedding-3-small", "text-embedding-3-large"]
    
    global_id = 1
    
    for r in range(1, num_roots + 1):
        doc_id = f"doc_{r:03d}"
        
        # Root Chunk
        root_chunk_id = f"chunk_{global_id}"
        global_id += 1
        
        model = random.choice(models)
        base_dim = 1536 if model == "text-embedding-3-small" else 3072
        
        # L2 norm usually ranges between 0.95 and 1.05 for normalized vectors
        vec_norm = float(np.random.normal(loc=1.0, scale=0.02))
        tokens = int(np.random.normal(loc=250, scale=30))
        
        records.append({
            "chunk_id": root_chunk_id,
            "parent_chunk_id": None,
            "doc_id": doc_id,
            "token_count": max(10, tokens),
            "embedding_norm": vec_norm,
            "model_version": model,
            "created_at": pd.Timestamp("2026-03-01") + pd.Timedelta(minutes=global_id * 5)
        })
        
        # Generate Children & Grandchildren
        parent_queue = [(root_chunk_id, 1)]
        
        while parent_queue and len(records) < total_target_rows:
            curr_parent, depth = parent_queue.pop(0)
            if depth >= max_depth:
                continue
                
            num_children = random.randint(1, 3)
            for _ in range(num_children):
                child_id = f"chunk_{global_id}"
                global_id += 1
                
                # Introduce Anomalies (1% - 3% rate)
                anomaly_type = random.choices(
                    ["none", "zero_embedding", "token_spike"], 
                    weights=[0.94, 0.03, 0.03]
                )[0]
                
                if anomaly_type == "zero_embedding":
                    vec_norm = 0.001  # Anomaly: near-zero magnitude
                    tokens = 200
                elif anomaly_type == "token_spike":
                    vec_norm = float(np.random.normal(loc=1.0, scale=0.02))
                    tokens = 4500  # Anomaly: extreme context length breach
                else:
                    vec_norm = float(np.random.normal(loc=1.0, scale=0.02))
                    tokens = int(np.random.normal(loc=200 / depth, scale=20))
                
                records.append({
                    "chunk_id": child_id,
                    "parent_chunk_id": curr_parent,
                    "doc_id": doc_id,
                    "token_count": max(5, tokens),
                    "embedding_norm": vec_norm,
                    "model_version": model,
                    "created_at": pd.Timestamp("2026-03-01") + pd.Timedelta(minutes=global_id * 5)
                })
                
                parent_queue.append((child_id, depth + 1))
                
    df = pd.DataFrame(records)
    
    os.makedirs("data", exist_ok=True)
    file_path = "data/document_chunks.parquet"
    df.to_parquet(file_path, index=False)
    print(f"Generated {len(df)} rows and saved to '{file_path}' successfully.")

if __name__ == "__main__":
    generate_mock_rag_dataset()

