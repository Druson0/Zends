# src/vector_store.py
"""FAISS vector store using SentenceTransformers embeddings.

Provides two main functions:
- ``create_or_update_index(chunks)`` – builds (or updates) a FAISS index from a list of text chunks.
- ``query_faiss(user_query, k=3)`` – searches the index and returns the top‑k matching chunks.

The index and metadata are persisted to ``vector_index.faiss`` and ``chunks.pkl`` in the
project root.
"""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# File names for persistence (saved in the same directory as this module)
INDEX_FILE = os.path.join(os.path.dirname(__file__), "..", "vector_index.faiss")
METADATA_FILE = os.path.join(os.path.dirname(__file__), "..", "chunks.pkl")

# Global cache for the model to avoid re-loading it on every request
MODEL_CACHE = None

def _get_model():
    """Load and cache the SentenceTransformer model."""
    global MODEL_CACHE
    if MODEL_CACHE is None:
        print("Loading SentenceTransformer model into memory...")
        MODEL_CACHE = SentenceTransformer('all-MiniLM-L6-v2')
    return MODEL_CACHE

def create_or_update_index(chunks: list) -> None:
    """Encode ``chunks`` and append them to the existing FAISS index.

    Parameters
    ----------
    chunks : list[str]
        List of text chunks to be indexed.
    """
    if not chunks:
        raise ValueError("No chunks provided for indexing.")

    model = _get_model()
    # 1. Generate embeddings
    print(f"Generating embeddings for {len(chunks)} chunks…")
    embeddings = model.encode(chunks, convert_to_numpy=True)
    embeddings = np.array(embeddings, dtype='float32')
    
    # 2. Check if index already exists
    if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
        print("Updating existing FAISS index...")
        index = faiss.read_index(INDEX_FILE)
        with open(METADATA_FILE, "rb") as f:
            all_chunks = pickle.load(f)
        
        # Append new chunks and embeddings
        index.add(embeddings)
        all_chunks.extend(chunks)
    else:
        print("Creating new FAISS index...")
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        all_chunks = chunks

    # 3. Persist index and metadata
    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(all_chunks, f)
    print(f"FAISS index now contains {len(all_chunks)} total vectors.")

def query_faiss(user_query: str, k: int = 3) -> list:
    """Search the FAISS index for the most similar chunks.

    Parameters
    ----------
    user_query : str
        The query string.
    k : int, optional
        Number of results to return (default 3).
    """
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError("FAISS index not found. Run indexing first.")

    model = _get_model()
    # Load index and stored chunks
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, "rb") as f:
        all_chunks = pickle.load(f)
    # Encode query
    query_vec = model.encode([user_query], convert_to_numpy=True).astype('float32')
    distances, indices = index.search(query_vec, k)
    # Retrieve corresponding text chunks
    results = [all_chunks[i] for i in indices[0]]
    return results

# Simple demo when run directly
if __name__ == "__main__":
    demo_chunks = [
        "The termination notice period is 90 days.",
        "Monthly rent is due on the 1st of every month.",
        "The security deposit is non-refundable if rules are broken."
    ]
    create_or_update_index(demo_chunks)
    print("Search demo:")
    print(query_faiss("How much notice do I need to give to end the contract?"))
