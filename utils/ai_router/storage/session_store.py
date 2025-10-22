"""
Redis Session Store - Session context management with 30-minute TTL.

Provides Redis-backed storage for SessionContext with automatic expiration,
connection pooling, and error handling.
"""

import json
import os
from typing import Optional
import redis
from redis.connection import ConnectionPool

from ..models.session_context import SessionContext


class SessionStore:
    """
    Redis-backed session storage with TTL management.

    Stores SessionContext objects in Redis with automatic 30-minute expiration.
    Uses connection pooling for efficiency and handles connection errors gracefully.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None,
        db: int = 0,
        max_connections: int = 10,
    ):
        """
        Initialize Redis session store with connection pooling.

        Args:
            host: Redis host (defaults to REDIS_HOST env var or 'localhost')
            port: Redis port (defaults to REDIS_PORT env var or 6379)
            password: Redis password (defaults to REDIS_PASSWORD env var)
            db: Redis database number (default 0)
            max_connections: Max connections in pool (default 10)
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.db = db

        # Create connection pool
        self.pool = ConnectionPool(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            max_connections=max_connections,
            decode_responses=True,  # Automatically decode bytes to strings
        )

        self.client = redis.Redis(connection_pool=self.pool)

        # Test connection
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to Redis at {self.host}:{self.port}. "
                f"Ensure Redis is running. Error: {e}"
            )

    def _get_key(self, user_id: str, session_id: str) -> str:
        """
        Generate Redis key for session.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            Redis key in format 'session:{user_id}:{session_id}'
        """
        return f"session:{user_id}:{session_id}"

    def save(self, context: SessionContext) -> bool:
        """
        Save session context to Redis with TTL.

        Args:
            context: SessionContext to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            key = self._get_key(context.user_id, context.session_id)
            data = json.dumps(context.to_dict())
            ttl_seconds = context.get_ttl_seconds()

            # Save with TTL (SETEX command)
            self.client.setex(key, ttl_seconds, data)
            return True

        except (redis.RedisError, json.JSONDecodeError) as e:
            # Log error but don't crash
            print(f"Error saving session to Redis: {e}")
            return False

    def load(self, user_id: str, session_id: str) -> Optional[SessionContext]:
        """
        Load session context from Redis.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            SessionContext if found and not expired, None otherwise
        """
        try:
            key = self._get_key(user_id, session_id)
            data = self.client.get(key)

            if data is None:
                return None

            # Parse JSON and create SessionContext
            session_dict = json.loads(data)
            context = SessionContext.from_dict(session_dict)

            # Check if expired (Redis TTL might not have triggered yet)
            if context.is_expired():
                self.delete(user_id, session_id)
                return None

            return context

        except (redis.RedisError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session from Redis: {e}")
            return None

    def update(self, context: SessionContext) -> bool:
        """
        Update existing session context (refresh TTL).

        Args:
            context: SessionContext to update

        Returns:
            True if updated successfully, False otherwise
        """
        # Update is same as save (overwrites with new TTL)
        return self.save(context)

    def delete(self, user_id: str, session_id: str) -> bool:
        """
        Delete session context from Redis.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            True if deleted, False if not found or error
        """
        try:
            key = self._get_key(user_id, session_id)
            result = self.client.delete(key)
            return result > 0

        except redis.RedisError as e:
            print(f"Error deleting session from Redis: {e}")
            return False

    def exists(self, user_id: str, session_id: str) -> bool:
        """
        Check if session exists in Redis.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            True if session exists, False otherwise
        """
        try:
            key = self._get_key(user_id, session_id)
            return self.client.exists(key) > 0

        except redis.RedisError:
            return False

    def get_ttl(self, user_id: str, session_id: str) -> int:
        """
        Get remaining TTL for session in seconds.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        try:
            key = self._get_key(user_id, session_id)
            return self.client.ttl(key)

        except redis.RedisError:
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
            return self.client.expire(key, ttl_seconds)

        except redis.RedisError as e:
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
            pattern = f"session:{user_id}:*"
            keys = self.client.keys(pattern)

            # Extract session IDs from keys
            session_ids = []
            for key in keys:
                # Key format: session:{user_id}:{session_id}
                parts = key.split(":")
                if len(parts) == 3:
                    session_ids.append(parts[2])

            return session_ids

        except redis.RedisError as e:
            print(f"Error listing user sessions: {e}")
            return []

    def cleanup_expired(self) -> int:
        """
        Cleanup expired sessions (Redis should handle this automatically via TTL).

        This is a manual cleanup for any sessions that didn't expire properly.

        Returns:
            Number of sessions deleted
        """
        deleted = 0
        try:
            # Scan all session keys
            for key in self.client.scan_iter(match="session:*:*"):
                # Check TTL
                ttl = self.client.ttl(key)
                if ttl == -1:  # No TTL set (shouldn't happen)
                    self.client.delete(key)
                    deleted += 1
                elif ttl == -2:  # Key doesn't exist (already expired)
                    continue

        except redis.RedisError as e:
            print(f"Error during cleanup: {e}")

        return deleted

    def get_stats(self) -> dict:
        """
        Get Redis connection and session statistics.

        Returns:
            Dictionary with stats
        """
        try:
            info = self.client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": self.client.dbsize(),
            }
        except redis.RedisError:
            return {"connected": False}

    def ping(self) -> bool:
        """
        Test Redis connection.

        Returns:
            True if connected, False otherwise
        """
        try:
            return self.client.ping()
        except redis.RedisError:
            return False

    def close(self):
        """Close Redis connection pool."""
        if self.pool:
            self.pool.disconnect()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        return f"SessionStore(host={self.host}, port={self.port}, db={self.db})"
