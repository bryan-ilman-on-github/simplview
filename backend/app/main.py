"""
FastAPI application entry point for the Intelligent Data Room.

Multi-agent system for conversational data analysis.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api import router, setup_cors
from app.config import settings


# Create FastAPI app
app = FastAPI(
    title="Intelligent Data Room API",
    description="Multi-agent system for conversational data analysis using PandasAI and Gemini",
    version="1.0.0"
)

# Setup CORS
setup_cors(app)

# Include routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Intelligent Data Room API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload",
            "chat": "/api/chat",
            "session": "/api/session/{session_id}",
            "reset": "/api/reset"
        }
    }


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    # Validate settings on startup
    try:
        settings.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please set GEMINI_API_KEY in backend/.env file")
        exit(1)

    # Run the server
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
