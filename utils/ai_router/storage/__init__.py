"""
Storage layer for session management and routing logs.

Provides abstractions for:
- Redis session storage (30-minute TTL)
- PostgreSQL routing logs (90-day retention with anonymization)
"""

from .session_store import SessionStore

# Try to import LogRepository, but make it optional since psycopg2
# may not be available on all Python versions (e.g., Python 3.13)
try:
    from .log_repository import LogRepository
except ImportError as e:
    import warnings
    warnings.warn(f"LogRepository unavailable (psycopg2 not installed): {e}")

    # Create a stub class that does nothing
    class LogRepository:
        """Stub LogRepository when psycopg2 is unavailable."""
        def __init__(self, *args, **kwargs):
            self._available = False

        def log_routing_decision(self, *args, **kwargs):
            return False

        def get_recent_logs(self, *args, **kwargs):
            return []

        def get_accuracy_metrics(self, *args, **kwargs):
            return {}

        def get_category_distribution(self, *args, **kwargs):
            return {}

        def test_connection(self):
            return False

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

__all__ = [
    "SessionStore",
    "LogRepository",
]
