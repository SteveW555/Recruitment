"""
Async Supabase Python Client Module

This module provides async versions of Supabase operations for high-performance
applications that need non-blocking database operations.

Usage:
    from supabase_async import AsyncSupabaseManager
    import asyncio

    async def main():
        async with AsyncSupabaseManager() as manager:
            users = await manager.select('users', columns='*')
            await manager.insert('users', {'name': 'John'})

    asyncio.run(main())

Author: ProActive People Recruitment System
Date: 2025
Documentation: Based on latest Supabase Python SDK (supabase-py)
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from pathlib import Path
import asyncio
from functools import wraps

try:
    from supabase import create_client, Client, AClient
    from supabase.lib.client_options import ClientOptions
except ImportError:
    raise ImportError(
        "Supabase package not found. Install with: pip install supabase"
    )

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not installed. Relying on system environment variables.")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def async_handle_errors(func):
    """Decorator for consistent error handling across async methods"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper


class AsyncSupabaseManager:
    """
    Async Supabase client manager for high-performance operations.

    This class provides async versions of all database, auth, and storage operations
    for applications that require non-blocking I/O.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        service_role_key: Optional[str] = None,
        use_service_role: bool = False
    ):
        """
        Initialize async Supabase client.

        Args:
            url: Supabase project URL
            key: Supabase anon/public key
            service_role_key: Service role key for admin operations
            use_service_role: If True, use service role key
        """
        self.url = url or os.getenv('SUPABASE_URL')
        self.anon_key = key or os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')
        self.service_role_key = service_role_key or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.url:
            raise ValueError("SUPABASE_URL must be provided or set in environment variables")

        active_key = self.service_role_key if (use_service_role and self.service_role_key) else self.anon_key

        if not active_key:
            raise ValueError("Supabase API key must be provided or set in environment variables")

        # Initialize async client
        self.client: Client = create_client(self.url, active_key)
        self.is_service_role = use_service_role and bool(self.service_role_key)

        logger.info(f"Async Supabase client initialized (Service Role: {self.is_service_role})")

    # ==================== ASYNC DATABASE OPERATIONS ====================

    @async_handle_errors
    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        ascending: bool = True,
        count: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Async select data from a table.

        Args:
            table: Table name
            columns: Columns to select
            filters: Dictionary of filters
            limit: Maximum rows
            offset: Rows to skip
            order_by: Column to order by
            ascending: Sort direction
            count: Count method

        Returns:
            Response object with data

        Example:
            users = await manager.select('users', limit=10)
        """
        # Run synchronous operation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        query = self.client.table(table).select(columns, count=count)

        if filters:
            query = self._apply_filters(query, filters)

        if order_by:
            query = query.order(order_by, desc=not ascending)

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.range(offset, offset + (limit or 1000) - 1)

        # Execute in thread pool to avoid blocking
        response = await loop.run_in_executor(None, query.execute)
        logger.info(f"[Async] Selected {len(response.data)} rows from {table}")
        return response

    @async_handle_errors
    async def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        upsert: bool = False,
        on_conflict: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Async insert one or more rows.

        Args:
            table: Table name
            data: Single dict or list of dicts
            upsert: If True, update on conflict
            on_conflict: Column(s) for conflict check

        Returns:
            Response object with inserted data

        Example:
            result = await manager.insert('users', {'name': 'John'})
        """
        loop = asyncio.get_event_loop()

        if upsert:
            query = self.client.table(table).upsert(data, on_conflict=on_conflict)
        else:
            query = self.client.table(table).insert(data)

        response = await loop.run_in_executor(None, query.execute)
        count = len(response.data) if isinstance(response.data, list) else 1
        logger.info(f"[Async] Inserted {count} row(s) into {table}")
        return response

    @async_handle_errors
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Async update rows matching filters.

        Args:
            table: Table name
            data: Dictionary of columns to update
            filters: Dictionary of filters

        Returns:
            Response object with updated data

        Example:
            result = await manager.update('users', {'status': 'active'}, {'id': 1})
        """
        loop = asyncio.get_event_loop()
        query = self.client.table(table).update(data)
        query = self._apply_filters(query, filters)

        response = await loop.run_in_executor(None, query.execute)
        count = len(response.data) if isinstance(response.data, list) else 0
        logger.info(f"[Async] Updated {count} row(s) in {table}")
        return response

    @async_handle_errors
    async def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Async delete rows matching filters.

        Args:
            table: Table name
            filters: Dictionary of filters

        Returns:
            Response object

        Example:
            result = await manager.delete('users', {'id': 1})
        """
        loop = asyncio.get_event_loop()
        query = self.client.table(table).delete()
        query = self._apply_filters(query, filters)

        response = await loop.run_in_executor(None, query.execute)
        count = len(response.data) if isinstance(response.data, list) else 0
        logger.info(f"[Async] Deleted {count} row(s) from {table}")
        return response

    @async_handle_errors
    async def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Async call PostgreSQL function.

        Args:
            function_name: Function name
            params: Function parameters

        Returns:
            Response object with function results

        Example:
            result = await manager.rpc('get_user_stats', {'user_id': 123})
        """
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.rpc(function_name, params or {}).execute()
        )
        logger.info(f"[Async] Executed RPC function: {function_name}")
        return response

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to a query (same as sync version)"""
        for key, value in filters.items():
            if '__' in key:
                column, operator = key.rsplit('__', 1)
            else:
                column, operator = key, 'eq'

            if operator == 'eq':
                query = query.eq(column, value)
            elif operator == 'neq':
                query = query.neq(column, value)
            elif operator == 'gt':
                query = query.gt(column, value)
            elif operator == 'gte':
                query = query.gte(column, value)
            elif operator == 'lt':
                query = query.lt(column, value)
            elif operator == 'lte':
                query = query.lte(column, value)
            elif operator == 'like':
                query = query.like(column, value)
            elif operator == 'ilike':
                query = query.ilike(column, value)
            elif operator == 'in':
                query = query.in_(column, value)
            elif operator == 'is':
                query = query.is_(column, value)
            elif operator == 'not':
                query = query.not_(column, value)
            else:
                logger.warning(f"Unknown operator: {operator}, using eq instead")
                query = query.eq(column, value)

        return query

    # ==================== ASYNC AUTHENTICATION ====================

    @async_handle_errors
    async def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Async user sign up"""
        loop = asyncio.get_event_loop()
        options = {"data": user_metadata} if user_metadata else {}
        response = await loop.run_in_executor(
            None,
            lambda: self.client.auth.sign_up({"email": email, "password": password, **options})
        )
        logger.info(f"[Async] User signed up: {email}")
        return response

    @async_handle_errors
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Async user sign in"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.auth.sign_in_with_password({"email": email, "password": password})
        )
        logger.info(f"[Async] User signed in: {email}")
        return response

    @async_handle_errors
    async def sign_out(self) -> None:
        """Async user sign out"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.client.auth.sign_out)
        logger.info("[Async] User signed out")

    @async_handle_errors
    async def get_user(self) -> Optional[Dict[str, Any]]:
        """Get currently authenticated user (async)"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.client.auth.get_user)
        return response

    # ==================== ASYNC STORAGE OPERATIONS ====================

    @async_handle_errors
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file: Union[bytes, str, Path],
        file_options: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Async file upload.

        Args:
            bucket: Bucket name
            path: Destination path
            file: File data or path
            file_options: File options

        Returns:
            Upload response

        Example:
            result = await manager.upload_file('avatars', 'user1.png', image_bytes)
        """
        loop = asyncio.get_event_loop()

        # Read file if path is provided
        if isinstance(file, (str, Path)):
            with open(file, 'rb') as f:
                file_data = f.read()
        else:
            file_data = file

        response = await loop.run_in_executor(
            None,
            lambda: self.client.storage.from_(bucket).upload(path, file_data, file_options or {})
        )
        logger.info(f"[Async] Uploaded file to {bucket}/{path}")
        return response

    @async_handle_errors
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Async file download"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.storage.from_(bucket).download(path)
        )
        logger.info(f"[Async] Downloaded file from {bucket}/{path}")
        return response

    @async_handle_errors
    async def list_files(self, bucket: str, path: str = "", limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Async list files in bucket"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.storage.from_(bucket).list(path, {"limit": limit, "offset": offset})
        )
        logger.info(f"[Async] Listed {len(response)} files in {bucket}/{path}")
        return response

    @async_handle_errors
    async def delete_files(self, bucket: str, paths: List[str]) -> Dict[str, Any]:
        """Async delete files"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.storage.from_(bucket).remove(paths)
        )
        logger.info(f"[Async] Deleted {len(paths)} file(s) from {bucket}")
        return response

    # ==================== ASYNC UTILITY METHODS ====================

    @async_handle_errors
    async def count_rows(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Async count rows in a table.

        Args:
            table: Table name
            filters: Optional filters

        Returns:
            Row count

        Example:
            count = await manager.count_rows('users', {'status': 'active'})
        """
        loop = asyncio.get_event_loop()
        query = self.client.table(table).select('*', count='exact', head=True)

        if filters:
            query = self._apply_filters(query, filters)

        response = await loop.run_in_executor(None, query.execute)
        return response.count

    @async_handle_errors
    async def batch_select(self, tables: List[str], columns: str = "*") -> Dict[str, Any]:
        """
        Async batch select from multiple tables concurrently.

        Args:
            tables: List of table names
            columns: Columns to select from all tables

        Returns:
            Dictionary mapping table names to their data

        Example:
            data = await manager.batch_select(['users', 'clients', 'candidates'])
            print(data['users'])
            print(data['clients'])
        """
        tasks = [self.select(table, columns) for table in tables]
        results = await asyncio.gather(*tasks)

        return {table: result.data for table, result in zip(tables, results)}

    async def close(self):
        """Close async client connection"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.client.auth.sign_out)
            logger.info("[Async] Supabase client closed")
        except Exception as e:
            logger.warning(f"Error closing async client: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        return False


# ==================== ASYNC CONVENIENCE FUNCTIONS ====================

def get_async_supabase_client(use_service_role: bool = False) -> AsyncSupabaseManager:
    """
    Factory function to create an AsyncSupabaseManager instance.

    Args:
        use_service_role: If True, use service role key

    Returns:
        Configured AsyncSupabaseManager instance

    Example:
        async with get_async_supabase_client() as client:
            users = await client.select('users')
    """
    return AsyncSupabaseManager(use_service_role=use_service_role)


# ==================== EXAMPLE ASYNC USAGE ====================

async def example_async_operations():
    """Example demonstrating async operations"""
    print("\n=== Async Supabase Operations ===\n")

    # Using async context manager
    async with AsyncSupabaseManager() as manager:
        # Parallel database queries
        print("1. Fetching data from multiple tables in parallel...")
        data = await manager.batch_select(['clients', 'candidates'])

        print(f"   Clients: {len(data['clients'])} records")
        print(f"   Candidates: {len(data['candidates'])} records")

        # Single query
        print("\n2. Fetching active candidates...")
        active = await manager.select(
            'candidates',
            columns='first_name,last_name,job_title_target',
            filters={'current_status__ilike': '%active%'},
            limit=5
        )
        print(f"   Found {len(active.data)} active candidates")

        # Count operation
        print("\n3. Counting records...")
        total = await manager.count_rows('clients')
        premium = await manager.count_rows('clients', {'account_tier': 'Premium'})
        print(f"   Total clients: {total}")
        print(f"   Premium clients: {premium}")

        # Insert operation
        print("\n4. Creating new candidate...")
        new_candidate = {
            'candidate_id': f'ASYNC-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'first_name': 'Async',
            'last_name': 'User',
            'primary_email': 'async@example.com',
            'current_status': 'Active - Looking'
        }
        result = await manager.insert('candidates', new_candidate)
        print(f"   Created: {result.data[0]['first_name']} {result.data[0]['last_name']}")

    print("\n=== Async operations completed ===")


if __name__ == "__main__":
    # Run async example
    asyncio.run(example_async_operations())
