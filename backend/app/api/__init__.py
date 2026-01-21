"""
API routes module.
Exports the router and CORS setup function.
"""
from app.api.routes import router, setup_cors

__all__ = ["router", "setup_cors"]
