"""
BIS-Compass Lightweight FastAPI Server
Provides HTTP endpoints for querying standards without heavy model loading.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from src.pipeline import run_pipeline, get_retriever, get_reranker

load_dotenv(override=True)

# Initialize FastAPI app
app = FastAPI(
    title="BIS-Compass API",
    description="Intelligent BIS Standards Recommendation Engine",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    """Warm the shared pipeline so the first user query is fast."""
    try:
        get_retriever()
        get_reranker()
    except Exception as exc:
        print(f"Warning: startup warmup failed: {exc}")


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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "BIS-Compass API is running"}


@app.post("/query")
async def query_standards(request: QueryRequest):
    """Query for relevant BIS standards."""
    result = run_pipeline(request.query, top_k=request.top_k)
    return {
        "query": result["query"],
        "retrieved_standards": result["retrieved_standards"],
        "latency_seconds": result["latency_seconds"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
