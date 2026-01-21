"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"


class UploadResponse(BaseModel):
    """Response for file upload."""
    success: bool
    message: str
    session_id: str
    file_info: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request for chat/question about data."""
    question: str = Field(..., description="User's question about the data")
    session_id: str = Field(..., description="Session identifier")


class VisualizationData(BaseModel):
    """Chart visualization data."""
    labels: List[str]
    values: List[float]
    additional_series: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    """Response for chat/question."""
    success: bool
    answer: str
    plan: Optional[Dict[str, Any]] = None
    chart_data: Optional[VisualizationData] = None
    chart_type: str = "none"
    insights: List[str] = []
    error: Optional[str] = None


class SessionInfo(BaseModel):
    """Session information response."""
    session_id: str
    message_count: int
    has_data: bool
    schema_info: Optional[Dict[str, Any]] = None


class ResetRequest(BaseModel):
    """Request to reset session."""
    session_id: str


class ResetResponse(BaseModel):
    """Response for session reset."""
    success: bool
    message: str
