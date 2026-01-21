"""
FastAPI routes for the Intelligent Data Room API.
"""
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models.schemas import (
    HealthResponse,
    UploadResponse,
    ChatRequest,
    ChatResponse,
    SessionInfo,
    ResetRequest,
    ResetResponse
)
from app.agents import PlannerAgent, ExecutorAgent
from app.services import context_manager, data_service
from app.config import settings


# Initialize routers
router = APIRouter()

# Initialize agents (lazy load when API key is available)
_planner: Optional[PlannerAgent] = None
_executor: Optional[ExecutorAgent] = None


def get_planner() -> PlannerAgent:
    """Get or create the Planner agent."""
    global _planner
    if _planner is None:
        _planner = PlannerAgent()
    return _planner


def get_executor() -> ExecutorAgent:
    """Get or create the Executor agent."""
    global _executor
    if _executor is None:
        _executor = ExecutorAgent()
    return _executor


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns the API status and version.
    """
    return HealthResponse(status="healthy", version="1.0.0")


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file.

    Validates the file and loads it into memory for the session.
    """
    # Generate new session ID
    session_id = str(uuid.uuid4())

    # Read file content
    content = await file.read()

    # Validate file
    is_valid, error_msg = data_service.validate_file(file.filename, len(content))
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Save uploaded file temporarily
    temp_path = os.path.join(data_service.upload_dir, f"{session_id}_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(content)

    try:
        # Load the file into a DataFrame
        df = data_service.load_file(temp_path)

        # Store DataFrame for this session
        data_service.store_dataframe(session_id, df)

        # Get schema info
        schema_info = {
            "filename": file.filename,
            "row_count": len(df),
            "columns": df.columns.tolist(),
            "file_size": len(content)
        }

        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            session_id=session_id,
            file_info=schema_info
        )

    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question about the uploaded data.

    Routes through the multi-agent system:
    1. Planner analyzes the question
    2. Executor executes the plan
    3. Returns answer with optional chart data
    """
    # Check if session has data
    if not data_service.has_data(request.session_id):
        raise HTTPException(
            status_code=404,
            detail="No data found for this session. Please upload a file first."
        )

    # Get the DataFrame
    df = data_service.get_dataframe(request.session_id)

    # Get context for follow-up questions
    context = context_manager.get_context(request.session_id)

    try:
        # Step 1: Planner creates execution plan
        planner = get_planner()
        plan = planner.create_plan(df, request.question, context)

        # Step 2: Executor executes the plan
        executor = get_executor()
        result = executor.execute(df, plan, request.question, context)

        # Step 3: Store this interaction in context
        context_manager.add_message(
            request.session_id,
            request.question,
            result.get("answer", ""),
            {
                "chart_type": result.get("chart_type"),
                "plan": plan
            }
        )

        # Build response
        return ChatResponse(
            success=True,
            answer=result.get("answer", ""),
            plan=plan,
            chart_data=result.get("data"),
            chart_type=result.get("chart_type", "none"),
            insights=result.get("insights", [])
        )

    except ValueError as e:
        if "API key" in str(e):
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured. Please set GEMINI_API_KEY in .env file."
            )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """
    Get information about a session.

    Returns session details including message count and data schema.
    """
    # Get context info
    context_info = context_manager.get_session_info(session_id)

    if context_info is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get schema info if data exists
    schema_info = None
    if data_service.has_data(session_id):
        schema_info = data_service.get_schema_summary(session_id)

    return SessionInfo(
        session_id=session_id,
        message_count=context_info["message_count"],
        has_data=data_service.has_data(session_id),
        schema_info=schema_info
    )


@router.post("/reset", response_model=ResetResponse)
async def reset_session(request: ResetRequest):
    """
    Reset a session, clearing all context and data.

    Use this to start a new analysis with the same session ID.
    """
    # Clear context
    context_cleared = context_manager.clear_session(request.session_id)
    # Clear data
    data_cleared = data_service.clear_session(request.session_id)

    if context_cleared or data_cleared:
        return ResetResponse(
            success=True,
            message="Session reset successfully"
        )
    else:
        return ResetResponse(
            success=False,
            message="Session not found"
        )


def setup_cors(app):
    """
    Setup CORS middleware for the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
