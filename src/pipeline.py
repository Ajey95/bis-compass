import time
from typing import Dict, List
from src.retrieval.retriever import HybridRetriever
from src.retrieval.reranker import Reranker
from src.generation.llm import generate_rationale

# Global singletons for lazy loading
_retriever = None
_reranker = None


def get_retriever() -> HybridRetriever:
    """Get or initialize the hybrid retriever."""
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever(persist_dir="./chroma_db")
    return _retriever


def get_reranker() -> Reranker:
    """Get or initialize the reranker."""
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker


def run_pipeline(query: str, top_k: int = 5) -> dict:
    """
    Full RAG pipeline: Retrieve → Deduplicate → Rerank → Generate Rationale
    
    Returns dict with:
    - query: input query
    - retrieved_standards: list of final top-k standards with metadata
    - latency_seconds: total execution time
    """
    
    start_time = time.time()
    
    try:
        # Step 1: Retrieve candidate documents
        retriever = get_retriever()
        candidates = retriever.retrieve(query, top_k=20)
        
        # Step 2: Deduplicate by standard number
        deduplicated = retriever.deduplicate_by_standard(candidates, top_n=10)
        
        # Step 3: Rerank using cross-encoder
        reranker = get_reranker()
        reranked = reranker.rerank(query, deduplicated, top_k=top_k)
        
        # Step 4: Generate rationales using LLM
        enriched = generate_rationale(query, reranked)
        
        # Step 5: Format final results
        retrieved_standards = []
        for std in enriched:
            retrieved_standards.append({
                "standard_number": std.get("metadata", {}).get("standard_number", ""),
                "title": std.get("metadata", {}).get("title", ""),
                "category": std.get("metadata", {}).get("category", ""),
                "rationale": std.get("rationale", ""),
                "relevance": std.get("relevance", "medium"),
                "score": std.get("rerank_score", 0.0)
            })
        
        latency = time.time() - start_time
        
        return {
            "query": query,
            "retrieved_standards": retrieved_standards,
            "latency_seconds": latency
        }
    
    except Exception as e:
        # Error handling: return empty results with latency
        latency = time.time() - start_time
        print(f"Pipeline error: {str(e)}")
        
        return {
            "query": query,
            "retrieved_standards": [],
            "latency_seconds": latency
        }
