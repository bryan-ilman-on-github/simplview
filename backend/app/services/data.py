"""
Data processing service for file uploads and DataFrame management.
"""
import os
import pandas as pd
from typing import Optional
from pathlib import Path

from app.config import settings


class DataService:
    """
    Handles data file uploads and DataFrame management.
    """

    def __init__(self, upload_dir: str = None):
        """
        Initialize the Data Service.

        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = upload_dir or settings.upload_dir
        self._ensure_upload_dir()

        # In-memory storage: session_id -> DataFrame
        self._dataframes: dict[str, pd.DataFrame] = {}

    def _ensure_upload_dir(self):
        """Create upload directory if it doesn't exist."""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate an uploaded file.

        Args:
            filename: Name of the uploaded file
            file_size: Size in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}"

        # Check file size
        if file_size > settings.max_file_size:
            return False, f"File too large. Maximum size: {settings.max_file_size / (1024*1024)}MB"

        return True, ""

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load a CSV file into a DataFrame.

        Args:
            file_path: Path to the CSV file

        Returns:
            Loaded DataFrame
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Error reading CSV: {str(e)}")

    def load_excel(self, file_path: str) -> pd.DataFrame:
        """
        Load an Excel file into a DataFrame.

        Args:
            file_path: Path to the Excel file

        Returns:
            Loaded DataFrame
        """
        try:
            return pd.read_excel(file_path, engine="openpyxl")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")

    def load_file(self, file_path: str) -> pd.DataFrame:
        """
        Load a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            Loaded DataFrame
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".csv":
            return self.load_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            return self.load_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def store_dataframe(self, session_id: str, df: pd.DataFrame) -> None:
        """
        Store a DataFrame for a session.

        Args:
            session_id: Unique session identifier
            df: DataFrame to store
        """
        self._dataframes[session_id] = df

    def get_dataframe(self, session_id: str) -> Optional[pd.DataFrame]:
        """
        Get the DataFrame for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            DataFrame or None if not found
        """
        return self._dataframes.get(session_id)

    def has_data(self, session_id: str) -> bool:
        """Check if a session has uploaded data."""
        return session_id in self._dataframes

    def clear_session(self, session_id: str) -> bool:
        """
        Clear data for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if data was cleared, False if session didn't exist
        """
        if session_id in self._dataframes:
            del self._dataframes[session_id]
            return True
        return False

    def get_schema_summary(self, session_id: str) -> Optional[dict]:
        """
        Get a summary of the data schema for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Schema summary dict or None
        """
        df = self.get_dataframe(session_id)
        if df is None:
            return None

        return {
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "row_count": len(df),
            "sample": df.head(3).to_dict("records")
        }


# Global data service instance
data_service = DataService()
