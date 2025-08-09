"""
Pydantic models for request and response validation
"""
from typing import List, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for hackathon API"""
    documents: str
    questions: List[str]


class QueryResponse(BaseModel):
    """Response model for hackathon API"""
    answers: List[str]


class DetailedResponse(BaseModel):
    """Detailed response model with decision logic"""
    decision: str
    amount: Optional[float] = None
    justification: str
    confidence: float
    source_clauses: List[str]


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str
