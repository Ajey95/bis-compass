from sentence_transformers import SentenceTransformer
import chromadb
from typing import List
from src.ingestion.chunker import Chunk
import os
import numpy as np


def build_vector_store(chunks: List[Chunk], persist_dir: str = "./chroma_db", rebuild: bool = True) -> None:
    """
    Build ChromaDB vector store with BAAI/bge-large-en-v1.5 embeddings.
    
    - Uses BAAI/bge-large-en-v1.5 model for dense retrieval
    - Persists to disk for reuse
    - Normalizes embeddings for better distance metrics
    - Batches embeddings for efficiency
    """
    
    # Initialize embedding model
    model = None
    try:
        print("Loading embedding model BAAI/bge-large-en-v1.5...")
        model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    except Exception as exc:
        print(f"Warning: failed to load embedding model, falling back to metadata-only storage: {exc}")
    
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path=persist_dir)

    # Delete existing collection if present for fresh start (only when rebuild=True)
    try:
        if rebuild:
            client.delete_collection(name="bis_standards")
    except Exception:
        pass

    # Create new collection
    collection = client.get_or_create_collection(
        name="bis_standards",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Prepare data for insertion
    ids = []
    documents = []
    metadatas = []
    embeddings = []
    
    print(f"Processing {len(chunks)} chunks for embedding...")
    
    # Add retrieval prefix to each chunk for BGE model
    for chunk in chunks:
        retrieval_text = f"Represent this document for retrieval: {chunk.content}"
        ids.append(chunk.chunk_id)
        documents.append(chunk.content)
        metadatas.append({
            "standard_number": chunk.standard_number,
            "title": chunk.title,
            "category": chunk.category,
            "chunk_type": chunk.chunk_type,
            "parent_standard": chunk.parent_standard
        })
        embeddings.append(retrieval_text)
    
    # Batch embed documents
    batch_size = 32
    embedded_list = []
    
    if model is not None:
        for i in range(0, len(embeddings), batch_size):
            batch_texts = embeddings[i:i + batch_size]
            batch_embeddings = model.encode(batch_texts, normalize_embeddings=True)
            embedded_list.extend(batch_embeddings)

            if (i + batch_size) % 160 == 0:
                print(f"  Embedded {min(i + batch_size, len(embeddings))} / {len(embeddings)} chunks")
    else:
        print("Skipping dense embedding generation; storing metadata-only records in ChromaDB")
    
    # Batch insert into ChromaDB (500 at a time)
    print("Inserting embeddings into ChromaDB...")
    insert_batch_size = 500
    
    for i in range(0, len(ids), insert_batch_size):
        end_idx = min(i + insert_batch_size, len(ids))
        batch_ids = ids[i:end_idx]
        batch_docs = documents[i:end_idx]
        batch_meta = metadatas[i:end_idx]

        if embedded_list:
            # Ensure embeddings are plain Python lists (not numpy arrays)
            batch_emb = []
            for emb in embedded_list[i:end_idx]:
                if hasattr(emb, "tolist"):
                    batch_emb.append(emb.tolist())
                elif isinstance(emb, np.ndarray):
                    batch_emb.append(emb.tolist())
                else:
                    # Fallback: coerce to list
                    batch_emb.append(list(emb))

            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
                embeddings=batch_emb
            )
        else:
            # Add without embeddings (metadata-only)
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
            )

        print(f"  Inserted {end_idx} / {len(ids)} chunks")
    
    print(f"✓ Vector store ready at {persist_dir}")
