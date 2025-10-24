"""
In-memory session store - fallback when Redis unavailable.

Provides simple dict-based session storage for development environments
where Redis isn't available. Sessions expire after 30 minutes.
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
from ..models.session_context import SessionContext


class InMemorySessionStore:
    """
    In-memory session storage with TTL.

    Simple dict-based storage for development environments
    where Redis isn't available. Sessions expire after 30 minutes.

    Not suitable for production with multiple backend instances.
    """

    def __init__(self, default_ttl_seconds: int = 1800):
        """
        Initialize in-memory session store.

        Args:
            default_ttl_seconds: Default session TTL in seconds (default 1800 = 30 minutes)
        """
        self.sessions: Dict[str, tuple[SessionContext, datetime]] = {}
        self.default_ttl_seconds = default_ttl_seconds

    def _get_key(self, user_id: str, session_id: str) -> str:
        """Generate storage key for session."""
        return f"{user_id}:{session_id}"

    def save(self, context: SessionContext) -> bool:
        """
        Save session context to memory.

        Args:
            context: SessionContext to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            key = self._get_key(context.user_id, context.session_id)
            expires_at = datetime.utcnow() + timedelta(seconds=self.default_ttl_seconds)
            self.sessions[key] = (context, expires_at)
            return True
        except Exception as e:
            print(f"Error saving session to memory: {e}")
            return False

    def load(self, user_id: str, session_id: str) -> Optional[SessionContext]:
        """
        Load session context from memory.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            SessionContext if found and not expired, None otherwise
        """
        try:
            key = self._get_key(user_id, session_id)

            if key not in self.sessions:
                return None

            context, expires_at = self.sessions[key]

            # Check if expired
            if datetime.utcnow() > expires_at:
                del self.sessions[key]
                return None

            return context
        except Exception as e:
            print(f"Error loading session from memory: {e}")
            return None

    def update(self, context: SessionContext) -> bool:
        """
        Update existing session context (refresh TTL).

        Args:
            context: SessionContext to update

        Returns:
            True if updated successfully, False otherwise
        """
        return self.save(context)

    def delete(self, user_id: str, session_id: str) -> bool:
        """
        Delete session context from memory.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            True if deleted, False if not found or error
        """
        try:
            key = self._get_key(user_id, session_id)
            if key in self.sessions:
                del self.sessions[key]
                return True
            return False
        except Exception as e:
            print(f"Error deleting session from memory: {e}")
            return False

    def exists(self, user_id: str, session_id: str) -> bool:
        """
        Check if session exists in memory.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            True if session exists and not expired, False otherwise
        """
        key = self._get_key(user_id, session_id)
        if key not in self.sessions:
            return False

        # Check if expired
        _, expires_at = self.sessions[key]
        if datetime.utcnow() > expires_at:
            del self.sessions[key]
            return False

        return True

    def get_ttl(self, user_id: str, session_id: str) -> int:
        """
        Get remaining TTL for session in seconds.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            TTL in seconds, -2 if key doesn't exist
        """
        try:
            key = self._get_key(user_id, session_id)
            if key not in self.sessions:
                return -2

            _, expires_at = self.sessions[key]
            remaining = (expires_at - datetime.utcnow()).total_seconds()
            return int(remaining) if remaining > 0 else -2
        except Exception:
            return -2

    def refresh_ttl(self, user_id: str, session_id: str, ttl_seconds: int = 1800) -> bool:
        """
        Refresh TTL for existing session without modifying data.

        Args:
            user_id: User ID
            session_id: Session ID
            ttl_seconds: New TTL in seconds (default 1800 = 30 minutes)

        Returns:
            True if TTL refreshed, False otherwise
        """
        try:
            key = self._get_key(user_id, session_id)
            if key not in self.sessions:
                return False

            context, _ = self.sessions[key]
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self.sessions[key] = (context, expires_at)
            return True
        except Exception as e:
            print(f"Error refreshing TTL: {e}")
            return False

    def list_user_sessions(self, user_id: str) -> list:
        """
        List all active session IDs for a user.

        Args:
            user_id: User ID

        Returns:
            List of session IDs
        """
        try:
            now = datetime.utcnow()
            session_ids = []

            for key, (context, expires_at) in self.sessions.items():
                # Skip expired sessions
                if now > expires_at:
                    continue

                # Check if key matches user
                if context.user_id == user_id:
                    session_ids.append(context.session_id)

            return session_ids
        except Exception as e:
            print(f"Error listing user sessions: {e}")
            return []

    def cleanup_expired(self) -> int:
        """
        Cleanup expired sessions.

        Returns:
            Number of sessions deleted
        """
        deleted = 0
        try:
            now = datetime.utcnow()
            expired_keys = [
                key for key, (_, expires_at) in self.sessions.items()
                if now > expires_at
            ]

            for key in expired_keys:
                del self.sessions[key]
                deleted += 1

        except Exception as e:
            print(f"Error during cleanup: {e}")

        return deleted

    def get_stats(self) -> dict:
        """
        Get session storage statistics.

        Returns:
            Dictionary with stats
        """
        # Cleanup expired before counting
        self.cleanup_expired()

        return {
            "connected": True,
            "total_sessions": len(self.sessions),
            "type": "in-memory"
        }

    def ping(self) -> bool:
        """
        Test connection (always returns True for in-memory).

        Returns:
            True
        """
        return True

    def close(self):
        """Close session store (cleanup memory)."""
        self.sessions.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        return f"InMemorySessionStore(sessions={len(self.sessions)}, ttl={self.default_ttl_seconds}s)"
