"""
PostgreSQL Log Repository - Routing decision logging with 90-day retention.

Provides PostgreSQL storage for routing logs with automatic anonymization
after 30 days and deletion after 90 days.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from ..models.routing_decision import RoutingDecision
from ..models.query import Query


class LogRepository:
    """
    PostgreSQL-backed routing log storage.

    Stores routing decisions and query data with automatic retention management.
    Uses connection pooling for efficiency.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        min_connections: int = 2,
        max_connections: int = 10,
    ):
        """
        Initialize PostgreSQL log repository with connection pooling.

        Args:
            host: PostgreSQL host (defaults to POSTGRES_HOST env var)
            port: PostgreSQL port (defaults to POSTGRES_PORT env var)
            database: Database name (defaults to POSTGRES_DB env var)
            user: Database user (defaults to POSTGRES_USER env var)
            password: Database password (defaults to POSTGRES_PASSWORD env var)
            min_connections: Min connections in pool (default 2)
            max_connections: Max connections in pool (default 10)
        """
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = port or int(os.getenv("POSTGRES_PORT", "5432"))
        self.database = database or os.getenv("POSTGRES_DB", "recruitment")
        self.user = user or os.getenv("POSTGRES_USER", "postgres")
        self.password = password or os.getenv("POSTGRES_PASSWORD")

        # Create connection pool
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
        except psycopg2.Error as e:
            raise ConnectionError(
                f"Failed to connect to PostgreSQL at {self.host}:{self.port}/{self.database}. "
                f"Error: {e}"
            )

    def _get_connection(self):
        """Get connection from pool."""
        return self.pool.getconn()

    def _return_connection(self, conn):
        """Return connection to pool."""
        self.pool.putconn(conn)

    def log_routing_decision(
        self,
        query: Query,
        decision: RoutingDecision,
        agent_success: bool,
        agent_latency_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log a routing decision to the database.

        Args:
            query: Query that was routed
            decision: Routing decision made
            agent_success: Whether agent executed successfully
            agent_latency_ms: Agent execution time in milliseconds
            error_message: Error message if agent failed

        Returns:
            True if logged successfully, False otherwise
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            insert_query = """
                INSERT INTO routing_logs (
                    timestamp,
                    user_id,
                    session_id,
                    query_text,
                    query_length_words,
                    query_truncated,
                    primary_category,
                    primary_confidence,
                    secondary_category,
                    secondary_confidence,
                    classification_latency_ms,
                    agent_execution_latency_ms,
                    agent_success,
                    fallback_triggered,
                    user_override,
                    error_message
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                decision.timestamp,
                query.user_id,
                query.session_id,
                query.text,
                query.word_count,
                query.truncated,
                decision.primary_category.value,
                decision.primary_confidence,
                decision.secondary_category.value if decision.secondary_category else None,
                decision.secondary_confidence,
                decision.classification_latency_ms,
                agent_latency_ms,
                agent_success,
                decision.fallback_triggered,
                decision.user_override,
                error_message,
            )

            cursor.execute(insert_query, values)
            conn.commit()
            cursor.close()
            return True

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"Error logging routing decision: {e}")
            return False

        finally:
            if conn:
                self._return_connection(conn)

    def get_recent_logs(self, limit: int = 100, user_id: Optional[str] = None) -> List[Dict]:
        """
        Get recent routing logs.

        Args:
            limit: Maximum number of logs to return (default 100)
            user_id: Optional filter by user ID

        Returns:
            List of log dictionaries
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            if user_id:
                query = """
                    SELECT * FROM routing_logs
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """
                cursor.execute(query, (user_id, limit))
            else:
                query = """
                    SELECT * FROM routing_logs
                    ORDER BY timestamp DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))

            logs = cursor.fetchall()
            cursor.close()
            return [dict(log) for log in logs]

        except psycopg2.Error as e:
            print(f"Error fetching recent logs: {e}")
            return []

        finally:
            if conn:
                self._return_connection(conn)

    def get_accuracy_metrics(self, days: int = 7) -> Dict:
        """
        Get routing accuracy metrics for the past N days.

        Args:
            days: Number of days to analyze (default 7)

        Returns:
            Dictionary with accuracy metrics
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            since_date = datetime.utcnow() - timedelta(days=days)

            query = """
                SELECT
                    COUNT(*) as total_queries,
                    AVG(primary_confidence) as avg_confidence,
                    SUM(CASE WHEN agent_success THEN 1 ELSE 0 END) as successful_routes,
                    SUM(CASE WHEN fallback_triggered THEN 1 ELSE 0 END) as fallback_count,
                    AVG(classification_latency_ms) as avg_classification_latency,
                    AVG(agent_execution_latency_ms) as avg_agent_latency
                FROM routing_logs
                WHERE timestamp >= %s
            """

            cursor.execute(query, (since_date,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                metrics = dict(result)
                # Calculate success rate
                total = metrics.get("total_queries", 0)
                successful = metrics.get("successful_routes", 0)
                metrics["success_rate"] = (successful / total * 100) if total > 0 else 0
                return metrics

            return {}

        except psycopg2.Error as e:
            print(f"Error fetching accuracy metrics: {e}")
            return {}

        finally:
            if conn:
                self._return_connection(conn)

    def get_category_distribution(self, days: int = 7) -> Dict[str, int]:
        """
        Get distribution of queries across categories.

        Args:
            days: Number of days to analyze (default 7)

        Returns:
            Dictionary mapping category to count
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            since_date = datetime.utcnow() - timedelta(days=days)

            query = """
                SELECT primary_category, COUNT(*) as count
                FROM routing_logs
                WHERE timestamp >= %s
                GROUP BY primary_category
                ORDER BY count DESC
            """

            cursor.execute(query, (since_date,))
            results = cursor.fetchall()
            cursor.close()

            return {row[0]: row[1] for row in results}

        except psycopg2.Error as e:
            print(f"Error fetching category distribution: {e}")
            return {}

        finally:
            if conn:
                self._return_connection(conn)

    def get_logs_for_anonymization(self, days_old: int = 30) -> List[Dict]:
        """
        Get logs older than N days for anonymization.

        Args:
            days_old: Age threshold in days (default 30)

        Returns:
            List of log dictionaries to anonymize
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            query = """
                SELECT * FROM routing_logs
                WHERE timestamp < %s
                ORDER BY timestamp ASC
            """

            cursor.execute(query, (cutoff_date,))
            logs = cursor.fetchall()
            cursor.close()

            return [dict(log) for log in logs]

        except psycopg2.Error as e:
            print(f"Error fetching logs for anonymization: {e}")
            return []

        finally:
            if conn:
                self._return_connection(conn)

    def delete_old_logs(self, days_old: int = 90, table: str = "routing_logs") -> int:
        """
        Delete logs older than N days.

        Args:
            days_old: Age threshold in days (default 90)
            table: Table name ('routing_logs' or 'routing_logs_anonymized')

        Returns:
            Number of rows deleted
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            query = f"""
                DELETE FROM {table}
                WHERE timestamp < %s
            """

            cursor.execute(query, (cutoff_date,))
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()

            return deleted_count

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"Error deleting old logs: {e}")
            return 0

        finally:
            if conn:
                self._return_connection(conn)

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connected, False otherwise
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True

        except psycopg2.Error:
            return False

        finally:
            if conn:
                self._return_connection(conn)

    def close(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        return f"LogRepository(host={self.host}, database={self.database})"
