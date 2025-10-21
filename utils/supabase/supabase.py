"""
Comprehensive Supabase Python Client Module

This module provides a complete interface for managing and interacting with Supabase,
including database operations, authentication, storage, real-time subscriptions, and more.

Usage:
    from supabase import SupabaseManager

    # Initialize
    manager = SupabaseManager()

    # Database operations
    users = manager.select('users', columns='*')
    manager.insert('users', {'name': 'John', 'email': 'john@example.com'})

    # Authentication
    user = manager.sign_up('user@example.com', 'password123')

    # Storage
    manager.upload_file('avatars', 'user1.png', file_data)

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
    from utils.supabase.supabase import create_client, Client
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


def handle_errors(func):
    """Decorator for consistent error handling across all methods"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper


class SupabaseManager:
    """
    Comprehensive Supabase client manager for all database, auth, storage, and realtime operations.

    This class provides a unified interface for:
    - Database CRUD operations with advanced filtering
    - User authentication and management
    - File storage operations
    - Real-time subscriptions
    - Edge Functions invocation
    - PostgreSQL RPC calls
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        service_role_key: Optional[str] = None,
        use_service_role: bool = False
    ):
        """
        Initialize Supabase client with credentials from environment or parameters.

        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: Supabase anon/public key (defaults to SUPABASE_ANON_KEY env var)
            service_role_key: Service role key for admin operations (defaults to SUPABASE_SERVICE_ROLE_KEY)
            use_service_role: If True, use service role key instead of anon key (bypasses RLS)
        """
        self.url = url or os.getenv('SUPABASE_URL')
        self.anon_key = key or os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')
        self.service_role_key = service_role_key or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.url:
            raise ValueError("SUPABASE_URL must be provided or set in environment variables")

        # Choose which key to use
        active_key = self.service_role_key if (use_service_role and self.service_role_key) else self.anon_key

        if not active_key:
            raise ValueError("Supabase API key must be provided or set in environment variables")

        # Initialize client
        self.client: Client = create_client(self.url, active_key)
        self.is_service_role = use_service_role and bool(self.service_role_key)

        logger.info(f"Supabase client initialized (Service Role: {self.is_service_role})")

    # ==================== DATABASE OPERATIONS ====================

    @handle_errors
    def select(
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
        Select data from a table with optional filtering, ordering, and pagination.

        Args:
            table: Table name
            columns: Columns to select (comma-separated or '*')
            filters: Dictionary of filters {column: value} or advanced filters
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            order_by: Column to order by
            ascending: Sort direction (True for ASC, False for DESC)
            count: Count method ('exact', 'planned', 'estimated')

        Returns:
            Response object with data and optionally count

        Example:
            # Simple select
            users = manager.select('users', columns='id,name,email')

            # With filters
            users = manager.select('users', filters={'status': 'active', 'age__gte': 18})

            # With pagination
            users = manager.select('users', limit=10, offset=20, order_by='created_at', ascending=False)
        """
        query = self.client.table(table).select(columns, count=count)

        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)

        # Apply ordering
        if order_by:
            query = query.order(order_by, desc=not ascending)

        # Apply pagination
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.range(offset, offset + (limit or 1000) - 1)

        response = query.execute()
        logger.info(f"Selected {len(response.data)} rows from {table}")
        return response

    @handle_errors
    def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        upsert: bool = False,
        on_conflict: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert one or more rows into a table.

        Args:
            table: Table name
            data: Single dict or list of dicts to insert
            upsert: If True, update on conflict instead of error
            on_conflict: Column(s) to check for conflicts (for upsert)

        Returns:
            Response object with inserted data

        Example:
            # Single insert
            result = manager.insert('users', {'name': 'John', 'email': 'john@example.com'})

            # Bulk insert
            result = manager.insert('users', [
                {'name': 'John', 'email': 'john@example.com'},
                {'name': 'Jane', 'email': 'jane@example.com'}
            ])

            # Upsert (insert or update)
            result = manager.insert('users', {'id': 1, 'name': 'John'}, upsert=True)
        """
        if upsert:
            query = self.client.table(table).upsert(data, on_conflict=on_conflict)
        else:
            query = self.client.table(table).insert(data)

        response = query.execute()
        count = len(response.data) if isinstance(response.data, list) else 1
        logger.info(f"Inserted {count} row(s) into {table}")
        return response

    @handle_errors
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update rows in a table matching the filters.

        Args:
            table: Table name
            data: Dictionary of columns to update
            filters: Dictionary of filters to match rows

        Returns:
            Response object with updated data

        Example:
            # Update all active users
            result = manager.update('users', {'status': 'inactive'}, {'status': 'active'})

            # Update specific user
            result = manager.update('users', {'name': 'John Doe'}, {'id': 1})
        """
        query = self.client.table(table).update(data)
        query = self._apply_filters(query, filters)

        response = query.execute()
        count = len(response.data) if isinstance(response.data, list) else 0
        logger.info(f"Updated {count} row(s) in {table}")
        return response

    @handle_errors
    def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Delete rows from a table matching the filters.

        Args:
            table: Table name
            filters: Dictionary of filters to match rows to delete

        Returns:
            Response object

        Example:
            # Delete specific user
            result = manager.delete('users', {'id': 1})

            # Delete all inactive users
            result = manager.delete('users', {'status': 'inactive'})
        """
        query = self.client.table(table).delete()
        query = self._apply_filters(query, filters)

        response = query.execute()
        count = len(response.data) if isinstance(response.data, list) else 0
        logger.info(f"Deleted {count} row(s) from {table}")
        return response

    @handle_errors
    def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a PostgreSQL function (Remote Procedure Call).

        Args:
            function_name: Name of the PostgreSQL function
            params: Dictionary of parameters to pass to the function

        Returns:
            Response object with function results

        Example:
            # Call function with parameters
            result = manager.rpc('get_user_stats', {'user_id': 123})

            # Call function without parameters
            result = manager.rpc('get_all_stats')
        """
        response = self.client.rpc(function_name, params or {}).execute()
        logger.info(f"Executed RPC function: {function_name}")
        return response

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Apply filters to a query using operator suffixes.

        Supported operators (append to column name with __):
        - eq: equals (default if no operator)
        - neq: not equals
        - gt: greater than
        - gte: greater than or equal
        - lt: less than
        - lte: less than or equal
        - like: pattern matching
        - ilike: case-insensitive pattern matching
        - in: value in list
        - is_: is null/true/false
        - not_: negation of condition

        Example:
            filters = {
                'age__gte': 18,
                'age__lt': 65,
                'status': 'active',
                'name__ilike': '%john%',
                'category__in': ['sales', 'marketing']
            }
        """
        for key, value in filters.items():
            # Parse operator from key
            if '__' in key:
                column, operator = key.rsplit('__', 1)
            else:
                column, operator = key, 'eq'

            # Apply the appropriate filter
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

    # ==================== AUTHENTICATION ====================

    @handle_errors
    def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Register a new user with email and password.

        Args:
            email: User email
            password: User password
            user_metadata: Additional user metadata

        Returns:
            User session data

        Example:
            user = manager.sign_up('user@example.com', 'SecurePass123!',
                                   {'first_name': 'John', 'last_name': 'Doe'})
        """
        options = {"data": user_metadata} if user_metadata else {}
        response = self.client.auth.sign_up({"email": email, "password": password, **options})
        logger.info(f"User signed up: {email}")
        return response

    @handle_errors
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in an existing user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            User session data

        Example:
            session = manager.sign_in('user@example.com', 'SecurePass123!')
        """
        response = self.client.auth.sign_in_with_password({"email": email, "password": password})
        logger.info(f"User signed in: {email}")
        return response

    @handle_errors
    def sign_in_with_otp(self, email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Sign in with one-time password (magic link or SMS).

        Args:
            email: User email for magic link
            phone: User phone for SMS OTP

        Returns:
            Response data

        Example:
            # Email magic link
            manager.sign_in_with_otp(email='user@example.com')

            # Phone OTP
            manager.sign_in_with_otp(phone='+1234567890')
        """
        if email:
            response = self.client.auth.sign_in_with_otp({"email": email})
            logger.info(f"OTP sent to email: {email}")
        elif phone:
            response = self.client.auth.sign_in_with_otp({"phone": phone})
            logger.info(f"OTP sent to phone: {phone}")
        else:
            raise ValueError("Either email or phone must be provided")

        return response

    @handle_errors
    def sign_in_with_oauth(self, provider: str, redirect_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Sign in with OAuth provider (Google, GitHub, etc.).

        Args:
            provider: OAuth provider name ('google', 'github', 'facebook', etc.)
            redirect_to: URL to redirect to after authentication

        Returns:
            OAuth URL and session data

        Example:
            auth_url = manager.sign_in_with_oauth('google', redirect_to='https://myapp.com/callback')
        """
        options = {"redirect_to": redirect_to} if redirect_to else {}
        response = self.client.auth.sign_in_with_oauth({"provider": provider, **options})
        logger.info(f"OAuth sign-in initiated with {provider}")
        return response

    @handle_errors
    def sign_out(self) -> None:
        """
        Sign out the current user.

        Example:
            manager.sign_out()
        """
        self.client.auth.sign_out()
        logger.info("User signed out")

    @handle_errors
    def get_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently authenticated user.

        Returns:
            User data or None if not authenticated

        Example:
            user = manager.get_user()
            if user:
                print(f"Current user: {user['email']}")
        """
        response = self.client.auth.get_user()
        return response

    @handle_errors
    def update_user(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the current user's attributes.

        Args:
            attributes: Dictionary of attributes to update

        Returns:
            Updated user data

        Example:
            # Update email
            user = manager.update_user({'email': 'newemail@example.com'})

            # Update metadata
            user = manager.update_user({'data': {'first_name': 'Jane'}})
        """
        response = self.client.auth.update_user(attributes)
        logger.info("User updated")
        return response

    @handle_errors
    def reset_password_email(self, email: str) -> Dict[str, Any]:
        """
        Send password reset email to user.

        Args:
            email: User email

        Returns:
            Response data

        Example:
            manager.reset_password_email('user@example.com')
        """
        response = self.client.auth.reset_password_for_email(email)
        logger.info(f"Password reset email sent to: {email}")
        return response

    # ==================== STORAGE OPERATIONS ====================

    @handle_errors
    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        List all storage buckets.

        Returns:
            List of bucket objects

        Example:
            buckets = manager.list_buckets()
            for bucket in buckets:
                print(bucket['name'])
        """
        response = self.client.storage.list_buckets()
        logger.info(f"Retrieved {len(response)} buckets")
        return response

    @handle_errors
    def create_bucket(self, name: str, public: bool = False, file_size_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new storage bucket.

        Args:
            name: Bucket name
            public: Whether bucket is publicly accessible
            file_size_limit: Maximum file size in bytes

        Returns:
            Created bucket data

        Example:
            bucket = manager.create_bucket('avatars', public=True, file_size_limit=5242880)  # 5MB
        """
        options = {"public": public}
        if file_size_limit:
            options["file_size_limit"] = file_size_limit

        response = self.client.storage.create_bucket(name, options)
        logger.info(f"Created bucket: {name}")
        return response

    @handle_errors
    def delete_bucket(self, name: str) -> Dict[str, Any]:
        """
        Delete a storage bucket.

        Args:
            name: Bucket name

        Returns:
            Response data

        Example:
            manager.delete_bucket('old-bucket')
        """
        response = self.client.storage.delete_bucket(name)
        logger.info(f"Deleted bucket: {name}")
        return response

    @handle_errors
    def upload_file(
        self,
        bucket: str,
        path: str,
        file: Union[bytes, str, Path],
        file_options: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to storage.

        Args:
            bucket: Bucket name
            path: Destination path in bucket (e.g., 'folder/file.png')
            file: File data (bytes), file path (str), or Path object
            file_options: File options including 'content-type'

        Returns:
            Upload response data

        Example:
            # Upload from bytes
            manager.upload_file('avatars', 'user1/profile.png', image_bytes,
                               {'content-type': 'image/png'})

            # Upload from file path
            manager.upload_file('documents', 'reports/2024.pdf', 'local/path/report.pdf',
                               {'content-type': 'application/pdf'})
        """
        # Read file if path is provided
        if isinstance(file, (str, Path)):
            with open(file, 'rb') as f:
                file_data = f.read()
        else:
            file_data = file

        response = self.client.storage.from_(bucket).upload(path, file_data, file_options or {})
        logger.info(f"Uploaded file to {bucket}/{path}")
        return response

    @handle_errors
    def download_file(self, bucket: str, path: str) -> bytes:
        """
        Download a file from storage.

        Args:
            bucket: Bucket name
            path: File path in bucket

        Returns:
            File data as bytes

        Example:
            data = manager.download_file('avatars', 'user1/profile.png')
            with open('profile.png', 'wb') as f:
                f.write(data)
        """
        response = self.client.storage.from_(bucket).download(path)
        logger.info(f"Downloaded file from {bucket}/{path}")
        return response

    @handle_errors
    def list_files(self, bucket: str, path: str = "", limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List files in a bucket directory.

        Args:
            bucket: Bucket name
            path: Directory path (empty for root)
            limit: Maximum files to return
            offset: Number of files to skip

        Returns:
            List of file objects

        Example:
            files = manager.list_files('avatars', 'user1/')
            for file in files:
                print(f"{file['name']} - {file['size']} bytes")
        """
        response = self.client.storage.from_(bucket).list(path, {"limit": limit, "offset": offset})
        logger.info(f"Listed {len(response)} files in {bucket}/{path}")
        return response

    @handle_errors
    def delete_files(self, bucket: str, paths: List[str]) -> Dict[str, Any]:
        """
        Delete one or more files from storage.

        Args:
            bucket: Bucket name
            paths: List of file paths to delete

        Returns:
            Response data

        Example:
            manager.delete_files('avatars', ['user1/old.png', 'user1/temp.jpg'])
        """
        response = self.client.storage.from_(bucket).remove(paths)
        logger.info(f"Deleted {len(paths)} file(s) from {bucket}")
        return response

    @handle_errors
    def move_file(self, bucket: str, from_path: str, to_path: str) -> Dict[str, Any]:
        """
        Move/rename a file within a bucket.

        Args:
            bucket: Bucket name
            from_path: Current file path
            to_path: New file path

        Returns:
            Response data

        Example:
            manager.move_file('documents', 'temp/draft.pdf', 'final/report.pdf')
        """
        response = self.client.storage.from_(bucket).move(from_path, to_path)
        logger.info(f"Moved file from {from_path} to {to_path} in {bucket}")
        return response

    @handle_errors
    def get_public_url(self, bucket: str, path: str) -> str:
        """
        Get the public URL for a file (bucket must be public).

        Args:
            bucket: Bucket name
            path: File path

        Returns:
            Public URL string

        Example:
            url = manager.get_public_url('avatars', 'user1/profile.png')
            print(f"Profile image: {url}")
        """
        response = self.client.storage.from_(bucket).get_public_url(path)
        return response

    @handle_errors
    def create_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> Dict[str, Any]:
        """
        Create a temporary signed URL for private file access.

        Args:
            bucket: Bucket name
            path: File path
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Dictionary with signedURL

        Example:
            url_data = manager.create_signed_url('private-docs', 'report.pdf', expires_in=7200)
            print(f"Temporary URL: {url_data['signedURL']}")
        """
        response = self.client.storage.from_(bucket).create_signed_url(path, expires_in)
        logger.info(f"Created signed URL for {bucket}/{path} (expires in {expires_in}s)")
        return response

    # ==================== REALTIME SUBSCRIPTIONS ====================

    @handle_errors
    def subscribe_to_table(
        self,
        table: str,
        callback: Callable,
        event: str = "*",
        schema: str = "public",
        filter_column: Optional[str] = None,
        filter_value: Optional[Any] = None
    ):
        """
        Subscribe to real-time changes on a table.

        Args:
            table: Table name
            callback: Function to call when changes occur
            event: Event type ('INSERT', 'UPDATE', 'DELETE', or '*' for all)
            schema: Database schema (default: 'public')
            filter_column: Column to filter on
            filter_value: Value to filter for

        Returns:
            Subscription channel

        Example:
            def handle_new_user(payload):
                print(f"New user: {payload['record']}")

            manager.subscribe_to_table('users', handle_new_user, event='INSERT')
        """
        channel_name = f"{table}_changes"
        channel = self.client.channel(channel_name)

        # Build filter string if provided
        filter_str = None
        if filter_column and filter_value is not None:
            filter_str = f"{filter_column}=eq.{filter_value}"

        channel.on_postgres_changes(
            event=event,
            schema=schema,
            table=table,
            callback=callback,
            filter=filter_str
        ).subscribe()

        logger.info(f"Subscribed to {event} events on {schema}.{table}")
        return channel

    @handle_errors
    def unsubscribe(self, channel):
        """
        Unsubscribe from a real-time channel.

        Args:
            channel: Channel object returned from subscribe_to_table

        Example:
            channel = manager.subscribe_to_table('users', callback)
            # Later...
            manager.unsubscribe(channel)
        """
        channel.unsubscribe()
        logger.info("Unsubscribed from channel")

    # ==================== UTILITY METHODS ====================

    @handle_errors
    def get_table_schema(self, table: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table.

        Args:
            table: Table name

        Returns:
            List of column definitions

        Example:
            schema = manager.get_table_schema('users')
            for column in schema:
                print(f"{column['column_name']}: {column['data_type']}")
        """
        query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        # Use RPC or direct SQL query if available
        # This is a placeholder - actual implementation may vary
        response = self.client.rpc('get_table_schema', {'table_name': table}).execute()
        return response.data

    @handle_errors
    def count_rows(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count rows in a table with optional filters.

        Args:
            table: Table name
            filters: Optional filters dictionary

        Returns:
            Row count

        Example:
            total_users = manager.count_rows('users')
            active_users = manager.count_rows('users', {'status': 'active'})
        """
        query = self.client.table(table).select('*', count='exact', head=True)

        if filters:
            query = self._apply_filters(query, filters)

        response = query.execute()
        return response.count

    def close(self):
        """
        Close the Supabase client connection and cleanup resources.

        Example:
            manager = SupabaseManager()
            # ... do work ...
            manager.close()
        """
        try:
            self.client.auth.sign_out()
            logger.info("Supabase client closed")
        except Exception as e:
            logger.warning(f"Error closing client: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# ==================== CONVENIENCE FUNCTIONS ====================

def get_supabase_client(use_service_role: bool = False) -> SupabaseManager:
    """
    Factory function to create a SupabaseManager instance.

    Args:
        use_service_role: If True, use service role key (bypasses RLS)

    Returns:
        Configured SupabaseManager instance

    Example:
        # Regular client (respects RLS)
        client = get_supabase_client()

        # Admin client (bypasses RLS)
        admin_client = get_supabase_client(use_service_role=True)
    """
    return SupabaseManager(use_service_role=use_service_role)


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example usage demonstration

    # Initialize manager
    manager = SupabaseManager()

    # Database operations
    print("\n=== Database Operations ===")

    # Select all users
    users = manager.select('users', limit=10)
    print(f"Users: {users.data}")

    # Insert new user
    new_user = manager.insert('users', {
        'email': 'newuser@example.com',
        'name': 'New User',
        'created_at': datetime.utcnow().isoformat()
    })
    print(f"Inserted user: {new_user.data}")

    # Update user
    updated = manager.update('users',
        {'name': 'Updated Name'},
        {'email': 'newuser@example.com'}
    )
    print(f"Updated user: {updated.data}")

    # Select with filters
    active_users = manager.select('users',
        columns='id,name,email',
        filters={'status': 'active', 'age__gte': 18},
        order_by='created_at',
        ascending=False,
        limit=5
    )
    print(f"Active users: {active_users.data}")

    # Authentication
    print("\n=== Authentication ===")

    try:
        # Sign up new user
        user = manager.sign_up('test@example.com', 'SecurePassword123!',
                               {'first_name': 'Test', 'last_name': 'User'})
        print(f"Signed up: {user}")

        # Sign in
        session = manager.sign_in('test@example.com', 'SecurePassword123!')
        print(f"Signed in: {session}")

        # Get current user
        current_user = manager.get_user()
        print(f"Current user: {current_user}")

    except Exception as e:
        print(f"Auth error: {e}")

    # Storage operations
    print("\n=== Storage Operations ===")

    try:
        # List buckets
        buckets = manager.list_buckets()
        print(f"Buckets: {buckets}")

        # Upload file
        # manager.upload_file('avatars', 'test/sample.txt', b'Hello, Supabase!',
        #                     {'content-type': 'text/plain'})

        # List files
        # files = manager.list_files('avatars', 'test/')
        # print(f"Files: {files}")

    except Exception as e:
        print(f"Storage error: {e}")

    # Clean up
    manager.close()
    print("\n=== Done ===")
