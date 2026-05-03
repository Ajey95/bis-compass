"""
BIS-Compass FastAPI Server
Provides HTTP endpoints for querying and retrieving standards.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from src.pipeline import run_pipeline, get_retriever, get_reranker

load_dotenv(override=True)

# Verify API key is configured
if not os.getenv("GROQ_API_KEY"):
    print("Warning: GROQ_API_KEY not set in environment")

# Initialize FastAPI app
app = FastAPI(
    title="BIS-Compass API",
    description="Intelligent BIS Standards Recommendation Engine",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class StandardResult(BaseModel):
    standard_number: str
    title: str
    category: str
    rationale: str
    relevance: str
    score: float


class QueryResponse(BaseModel):
    query: str
    retrieved_standards: List[StandardResult]
    latency_seconds: float


# Initialize models on startup
@app.on_event("startup")
async def startup():
    """Load models at startup for faster first query."""
    print("Loading retriever and reranker models...")
    try:
        get_retriever()
        get_reranker()
        print("✓ Models loaded successfully")
    except Exception as e:
        print(f"Warning: Could not pre-load models: {e}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "BIS-Compass API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.post("/query", response_model=QueryResponse)
async def query_standards(request: QueryRequest):
    """
    Query the BIS standards database.
    
    Args:
        request: QueryRequest with product description and optional top_k
    
    Returns:
        QueryResponse with retrieved standards and latency
    """
    result = run_pipeline(request.query, top_k=request.top_k)
    
    # Convert to response model
    standards = [
        StandardResult(
            standard_number=std["standard_number"],
            title=std["title"],
            category=std["category"],
            rationale=std["rationale"],
            relevance=std["relevance"],
            score=std["score"]
        )
        for std in result["retrieved_standards"]
    ]
    
    return QueryResponse(
        query=result["query"],
        retrieved_standards=standards,
        latency_seconds=result["latency_seconds"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
