"""
Application configuration module.
Loads environment variables and provides settings for the application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""

    # Gemini API
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # Server
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

    # CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {".csv", ".xlsx", ".xls"}
    upload_dir: str = "uploads"

    # Context/Memory
    max_context_messages: int = 5

    def validate(self) -> bool:
        """Validate required settings."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required. Please set it in .env file.")
        return True


settings = Settings()
