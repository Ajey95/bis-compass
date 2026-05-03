from sentence_transformers import CrossEncoder
from typing import List, Dict


class Reranker:
    """
    Cross-encoder reranker for precision boost using ms-marco-MiniLM-L-6-v2.
    This provides the final ranking for top results before LLM generation.
    """
    
    def __init__(self):
        """Initialize cross-encoder model."""
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    def rerank(self, query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Rerank candidates using cross-encoder scores.
        
        Args:
            query: Input query string
            candidates: List of candidate chunks from retriever
            top_k: Number of top results to return
        
        Returns:
            Top-k candidates sorted by cross-encoder score
        """
        
        # Create query-document pairs
        pairs = []
        for candidate in candidates:
            # Use content from candidate chunk
            content = candidate["content"]
            pairs.append([query, content])
        
        # Score all pairs
        scores = self.model.predict(pairs)
        
        # Add scores to candidates
        for idx, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(scores[idx])
        
        # Sort by rerank score descending
        reranked = sorted(
            candidates,
            key=lambda x: x["rerank_score"],
            reverse=True
        )[:top_k]
        
        return reranked
