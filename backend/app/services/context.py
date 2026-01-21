"""
Context/Session management for multi-turn conversations.

Manages conversation history to enable follow-up questions.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
from collections import deque

from app.config import settings


class ContextManager:
    """
    Manages conversation context for multi-turn dialogues.

    Stores the last N messages per session to enable follow-up questions.
    Uses in-memory storage with optional TTL.
    """

    def __init__(self, max_messages: int = None, ttl_minutes: int = 60):
        """
        Initialize the Context Manager.

        Args:
            max_messages: Maximum messages to keep per session (default from settings)
            ttl_minutes: Time-to-live for sessions in minutes
        """
        self.max_messages = max_messages or settings.max_context_messages
        self.ttl_minutes = ttl_minutes

        # In-memory storage: session_id -> (messages dict, last_access timestamp)
        self._sessions: Dict[str, tuple[deque, datetime]] = {}

    def _cleanup_expired_sessions(self):
        """Remove sessions that haven't been accessed recently."""
        now = datetime.now()
        expired = [
            session_id
            for session_id, (_, last_access) in self._sessions.items()
            if (now - last_access) > timedelta(minutes=self.ttl_minutes)
        ]
        for session_id in expired:
            del self._sessions[session_id]

    def add_message(
        self,
        session_id: str,
        question: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a Q&A pair to the session context.

        Args:
            session_id: Unique session identifier
            question: User's question
            answer: Agent's response
            metadata: Optional metadata (chart type, plan, etc.)
        """
        self._cleanup_expired_sessions()

        if session_id not in self._sessions:
            self._sessions[session_id] = (deque(maxlen=self.max_messages), datetime.now())

        messages, _ = self._sessions[session_id]

        message = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        messages.append(message)
        # Update last access time
        self._sessions[session_id] = (messages, datetime.now())

    def get_context(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the conversation context for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            List of Q&A pairs (empty list if session doesn't exist)
        """
        self._cleanup_expired_sessions()

        if session_id not in self._sessions:
            return []

        messages, _ = self._sessions[session_id]
        # Update last access time
        self._sessions[session_id] = (messages, datetime.now())

        return list(messages)

    def clear_session(self, session_id: str) -> bool:
        """
        Clear the context for a specific session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if session was cleared, False if it didn't exist
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        self._cleanup_expired_sessions()
        return len(self._sessions)

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Session info dict or None if session doesn't exist
        """
        if session_id not in self._sessions:
            return None

        messages, last_access = self._sessions[session_id]

        return {
            "session_id": session_id,
            "message_count": len(messages),
            "max_messages": self.max_messages,
            "last_access": last_access.isoformat(),
            "messages": list(messages)
        }


# Global context manager instance
context_manager = ContextManager()
