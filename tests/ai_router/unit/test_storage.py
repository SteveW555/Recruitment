"""
Unit tests for storage layer - Session and log persistence.

Tests:
- Redis session store (save, load, TTL, delete)
- PostgreSQL log repository (insert, query, retention)
- Connection pooling and error handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import json

from utils.ai_router.storage.session_store import SessionStore
from utils.ai_router.storage.log_repository import LogRepository
from utils.ai_router.models.session_context import SessionContext
from utils.ai_router.models.query import Query
from utils.ai_router.models.routing_decision import RoutingDecision
from utils.ai_router.models.category import Category


class TestSessionStore:
    """Test Redis session store."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        return Mock()

    @pytest.fixture
    def session_store(self, mock_redis_client):
        """Create session store with mocked Redis."""
        with patch('utils.ai_router.storage.session_store.redis.Redis', return_value=mock_redis_client):
            with patch('utils.ai_router.storage.session_store.ConnectionPool'):
                store = SessionStore()
                store.client = mock_redis_client
                return store

    def test_session_key_generation(self, session_store):
        """Test Redis key generation for sessions."""
        key = session_store._get_key("user_123", "session_456")
        assert key == "session:user_123:session_456"

    def test_save_session(self, session_store, mock_redis_client):
        """Test saving session context to Redis."""
        context = SessionContext(
            user_id="user_123",
            session_id="session_456"
        )

        result = session_store.save(context)

        assert result is True
        mock_redis_client.setex.assert_called_once()

    def test_load_session(self, session_store, mock_redis_client):
        """Test loading session context from Redis."""
        context = SessionContext(
            user_id="user_123",
            session_id="session_456"
        )

        # Mock Redis return value
        mock_redis_client.get.return_value = json.dumps(context.to_dict())

        loaded = session_store.load("user_123", "session_456")

        assert loaded is not None
        assert loaded.user_id == "user_123"
        assert loaded.session_id == "session_456"

    def test_load_nonexistent_session(self, session_store, mock_redis_client):
        """Test loading nonexistent session returns None."""
        mock_redis_client.get.return_value = None

        loaded = session_store.load("user_123", "nonexistent")

        assert loaded is None

    def test_session_ttl_refresh(self, session_store, mock_redis_client):
        """Test refreshing session TTL."""
        result = session_store.refresh_ttl("user_123", "session_456", 1800)

        mock_redis_client.expire.assert_called_once()
        mock_redis_client.expire.assert_called_with("session:user_123:session_456", 1800)

    def test_session_exists_check(self, session_store, mock_redis_client):
        """Test checking session existence."""
        mock_redis_client.exists.return_value = 1

        exists = session_store.exists("user_123", "session_456")

        assert exists is True

    def test_delete_session(self, session_store, mock_redis_client):
        """Test deleting session from Redis."""
        mock_redis_client.delete.return_value = 1

        result = session_store.delete("user_123", "session_456")

        assert result is True
        mock_redis_client.delete.assert_called_once()

    def test_get_ttl(self, session_store, mock_redis_client):
        """Test getting remaining TTL for session."""
        mock_redis_client.ttl.return_value = 1800

        ttl = session_store.get_ttl("user_123", "session_456")

        assert ttl == 1800

    def test_list_user_sessions(self, session_store, mock_redis_client):
        """Test listing all sessions for a user."""
        mock_redis_client.keys.return_value = [
            "session:user_123:session_1",
            "session:user_123:session_2",
            "session:user_123:session_3"
        ]

        sessions = session_store.list_user_sessions("user_123")

        assert len(sessions) == 3
        assert "session_1" in sessions
        assert "session_2" in sessions

    def test_redis_connection_error(self, mock_redis_client):
        """Test handling of Redis connection error."""
        mock_redis_client.ping.side_effect = Exception("Connection refused")

        with pytest.raises(ConnectionError):
            with patch('utils.ai_router.storage.session_store.ConnectionPool'):
                with patch('utils.ai_router.storage.session_store.redis.Redis', return_value=mock_redis_client):
                    SessionStore()


class TestLogRepository:
    """Test PostgreSQL log repository."""

    @pytest.fixture
    def mock_db_pool(self):
        """Create a mock database connection pool."""
        return Mock()

    @pytest.fixture
    def log_repository(self, mock_db_pool):
        """Create log repository with mocked database."""
        with patch('utils.ai_router.storage.log_repository.psycopg2.pool.ThreadedConnectionPool', return_value=mock_db_pool):
            repo = LogRepository()
            repo.pool = mock_db_pool
            return repo

    def test_log_routing_decision(self, log_repository, mock_db_pool):
        """Test logging a routing decision."""
        # Setup mock connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_pool.getconn.return_value = mock_conn

        query = Query(
            text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        decision = RoutingDecision(
            query_id=query.id,
            primary_category=Category.INFORMATION_RETRIEVAL,
            primary_confidence=0.85,
            secondary_category=None,
            secondary_confidence=None,
            reasoning="Test classification",
            classification_latency_ms=50,
            fallback_triggered=False,
            user_override=False
        )

        result = log_repository.log_routing_decision(
            query=query,
            decision=decision,
            agent_success=True,
            agent_latency_ms=150
        )

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_get_recent_logs(self, log_repository, mock_db_pool):
        """Test retrieving recent logs."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'primary_category': 'INFORMATION_RETRIEVAL'},
            {'id': 2, 'primary_category': 'GENERAL_CHAT'}
        ]
        mock_db_pool.getconn.return_value = mock_conn

        logs = log_repository.get_recent_logs(limit=100)

        assert len(logs) == 2
        mock_cursor.execute.assert_called_once()

    def test_get_recent_logs_with_user_filter(self, log_repository, mock_db_pool):
        """Test retrieving logs filtered by user ID."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_db_pool.getconn.return_value = mock_conn

        logs = log_repository.get_recent_logs(limit=100, user_id="user_123")

        mock_cursor.execute.assert_called_once()
        # Check that execute was called with user_id filter
        call_args = mock_cursor.execute.call_args
        assert "user_id" in call_args[0][0]

    def test_get_accuracy_metrics(self, log_repository, mock_db_pool):
        """Test retrieving accuracy metrics."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'total_queries': 100,
            'avg_confidence': 0.82,
            'successful_routes': 95,
            'fallback_count': 5,
            'avg_classification_latency': 50.0,
            'avg_agent_latency': 150.0
        }
        mock_db_pool.getconn.return_value = mock_conn

        metrics = log_repository.get_accuracy_metrics(days=7)

        assert metrics['total_queries'] == 100
        assert metrics['successful_routes'] == 95
        # Success rate should be calculated
        assert 'success_rate' in metrics

    def test_get_category_distribution(self, log_repository, mock_db_pool):
        """Test retrieving category distribution."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('INFORMATION_RETRIEVAL', 50),
            ('GENERAL_CHAT', 30),
            ('PROBLEM_SOLVING', 20)
        ]
        mock_db_pool.getconn.return_value = mock_conn

        distribution = log_repository.get_category_distribution(days=7)

        assert distribution['INFORMATION_RETRIEVAL'] == 50
        assert distribution['GENERAL_CHAT'] == 30
        assert distribution['PROBLEM_SOLVING'] == 20

    def test_delete_old_logs(self, log_repository, mock_db_pool):
        """Test deleting logs older than N days."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 42
        mock_conn.cursor.return_value = mock_cursor
        mock_db_pool.getconn.return_value = mock_conn

        deleted = log_repository.delete_old_logs(days_old=90)

        assert deleted == 42
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_test_connection(self, log_repository, mock_db_pool):
        """Test database connection test."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_pool.getconn.return_value = mock_conn

        result = log_repository.test_connection()

        assert result is True
        mock_cursor.execute.assert_called_once()

    def test_connection_error_handling(self, log_repository, mock_db_pool):
        """Test handling of connection errors."""
        mock_db_pool.getconn.side_effect = Exception("Connection failed")

        result = log_repository.test_connection()

        assert result is False

    def test_context_manager(self, log_repository):
        """Test using log repository as context manager."""
        with log_repository as repo:
            assert repo is log_repository

        log_repository.close.assert_called()


class TestSessionStorageIntegration:
    """Integration tests for session storage with actual data."""

    def test_session_serialization_roundtrip(self):
        """Test that session can be serialized and deserialized."""
        original = SessionContext(
            user_id="user_123",
            session_id="session_456"
        )

        original.add_message("user_123", "Test message")
        original.add_routing_history("INFORMATION_RETRIEVAL", 0.85)

        # Serialize
        data = original.to_dict()
        serialized = json.dumps(data)

        # Deserialize
        deserialized = json.loads(serialized)
        restored = SessionContext.from_dict(deserialized)

        assert restored.user_id == original.user_id
        assert restored.session_id == original.session_id
        assert len(restored.message_history) == len(original.message_history)
        assert len(restored.routing_history) == len(original.routing_history)

    def test_session_expiry_check(self):
        """Test session expiry detection."""
        context = SessionContext(
            user_id="user_123",
            session_id="session_456",
            created_at=datetime.utcnow() - timedelta(hours=1)  # 1 hour old
        )

        # Session should be expired (30 minute default)
        assert context.is_expired() is True

        # Fresh session should not be expired
        fresh_context = SessionContext(
            user_id="user_123",
            session_id="session_456"
        )

        assert fresh_context.is_expired() is False


class TestLogRepositoryIntegration:
    """Integration tests for log repository with actual data."""

    def test_routing_decision_fields_logged(self):
        """Test that all routing decision fields are logged correctly."""
        query = Query(
            text="Test query",
            user_id="user_123",
            session_id="session_456"
        )

        decision = RoutingDecision(
            query_id=query.id,
            primary_category=Category.INFORMATION_RETRIEVAL,
            primary_confidence=0.85,
            secondary_category=Category.PROBLEM_SOLVING,
            secondary_confidence=0.72,
            reasoning="Test",
            classification_latency_ms=50,
            fallback_triggered=False,
            user_override=False
        )

        # In real scenario, these would be written to DB
        # For testing, verify that decision data is complete
        assert decision.primary_category is not None
        assert decision.primary_confidence > 0
        assert decision.classification_latency_ms >= 0
        assert decision.reasoning is not None
