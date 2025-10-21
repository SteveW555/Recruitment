# Supabase Python Client - ProActive People

Comprehensive Supabase client modules for the ProActive People recruitment automation system. This implementation provides both synchronous and asynchronous interfaces for all Supabase operations.

## 📚 Modules

- **`supabase.py`** - Synchronous Supabase client with full CRUD, auth, storage, and realtime capabilities
- **`supabase_async.py`** - Async/await version for high-performance non-blocking operations
- **`supabase_examples.py`** - Comprehensive usage examples with real-world scenarios

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install supabase python-dotenv
```

### Environment Setup

Create a `.env` file with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # Optional, for admin operations
```

### Basic Usage (Synchronous)

```python
from supabase import SupabaseManager

# Initialize
manager = SupabaseManager()

# Select data
users = manager.select('users', columns='id,name,email', limit=10)
print(users.data)

# Insert data
new_user = manager.insert('users', {
    'name': 'John Smith',
    'email': 'john@example.com'
})

# Update data
manager.update('users', {'status': 'active'}, {'id': 1})

# Delete data
manager.delete('users', {'id': 1})

# Close connection
manager.close()
```

### Basic Usage (Async)

```python
from supabase_async import AsyncSupabaseManager
import asyncio

async def main():
    async with AsyncSupabaseManager() as manager:
        # Parallel queries
        data = await manager.batch_select(['users', 'clients', 'candidates'])

        # Single query
        active_users = await manager.select(
            'users',
            filters={'status': 'active'},
            limit=10
        )

        # Insert
        result = await manager.insert('users', {'name': 'Jane Doe'})

asyncio.run(main())
```

## 🔥 Key Features

### 1. **Advanced Filtering**

The modules support powerful filter operators using the `__` suffix pattern:

```python
# Comparison operators
manager.select('candidates', filters={
    'age__gte': 18,           # Greater than or equal
    'age__lt': 65,            # Less than
    'salary__gt': 30000,      # Greater than
    'status': 'active'        # Equals (default)
})

# Pattern matching
manager.select('clients', filters={
    'company_name__ilike': '%tech%',  # Case-insensitive LIKE
    'city__like': 'Bristol%'          # Case-sensitive LIKE
})

# List operations
manager.select('jobs', filters={
    'category__in': ['Sales', 'Marketing', 'IT']
})

# NULL checks
manager.select('users', filters={
    'deleted_at__is': 'null'
})
```

**Available Operators:**
- `eq` - Equals (default)
- `neq` - Not equals
- `gt` - Greater than
- `gte` - Greater than or equal
- `lt` - Less than
- `lte` - Less than or equal
- `like` - Pattern match (case-sensitive)
- `ilike` - Pattern match (case-insensitive)
- `in` - Value in list
- `is` - IS NULL/TRUE/FALSE
- `not` - Negation

### 2. **Bulk Operations**

```python
# Bulk insert
candidates = [
    {'name': 'John', 'email': 'john@example.com'},
    {'name': 'Jane', 'email': 'jane@example.com'},
    {'name': 'Bob', 'email': 'bob@example.com'}
]
manager.insert('candidates', candidates)

# Upsert (insert or update on conflict)
manager.insert('users', {'id': 1, 'name': 'Updated Name'}, upsert=True)
```

### 3. **Authentication**

```python
# Sign up
user = manager.sign_up('user@example.com', 'password123', {
    'first_name': 'John',
    'role': 'recruiter'
})

# Sign in
session = manager.sign_in('user@example.com', 'password123')

# OAuth
auth_url = manager.sign_in_with_oauth('google')

# Magic link / OTP
manager.sign_in_with_otp(email='user@example.com')
manager.sign_in_with_otp(phone='+447700900123')

# Get current user
user = manager.get_user()

# Update profile
manager.update_user({'data': {'phone': '+447700900123'}})

# Password reset
manager.reset_password_email('user@example.com')

# Sign out
manager.sign_out()
```

### 4. **Storage Operations**

```python
# List buckets
buckets = manager.list_buckets()

# Create bucket
manager.create_bucket('candidate-cvs', public=False, file_size_limit=10485760)

# Upload file
manager.upload_file(
    'candidate-cvs',
    'candidates/john-smith-cv.pdf',
    file_data,
    {'content-type': 'application/pdf'}
)

# Download file
data = manager.download_file('candidate-cvs', 'candidates/john-smith-cv.pdf')

# List files
files = manager.list_files('candidate-cvs', 'candidates/')

# Delete files
manager.delete_files('candidate-cvs', ['old-file.pdf', 'temp.txt'])

# Move/rename file
manager.move_file('bucket', 'old/path.pdf', 'new/path.pdf')

# Get public URL
url = manager.get_public_url('public-bucket', 'image.png')

# Create signed URL (temporary access)
signed = manager.create_signed_url('private-bucket', 'doc.pdf', expires_in=3600)
```

### 5. **Real-time Subscriptions**

```python
# Define callback
def handle_new_candidate(payload):
    record = payload['record']
    print(f"New candidate: {record['name']}")

# Subscribe to inserts
channel = manager.subscribe_to_table('candidates', handle_new_candidate, event='INSERT')

# Subscribe to all events
channel = manager.subscribe_to_table('users', callback, event='*')

# Subscribe with filter
channel = manager.subscribe_to_table(
    'candidates',
    callback,
    event='UPDATE',
    filter_column='status',
    filter_value='Active'
)

# Unsubscribe
manager.unsubscribe(channel)
```

### 6. **PostgreSQL RPC (Remote Procedure Calls)**

```python
# Call custom PostgreSQL function
result = manager.rpc('get_candidate_stats', {'status': 'Active'})

# Call function without parameters
stats = manager.rpc('calculate_monthly_revenue')
```

### 7. **Utility Methods**

```python
# Count rows
total = manager.count_rows('candidates')
active = manager.count_rows('candidates', {'status': 'Active'})

# Get table schema (if custom RPC exists)
schema = manager.get_table_schema('users')
```

### 8. **Service Role (Admin Operations)**

```python
# Regular client - respects Row Level Security (RLS)
manager = SupabaseManager(use_service_role=False)

# Admin client - bypasses RLS
admin = SupabaseManager(use_service_role=True)

# Admin can access all data
all_data = admin.select('protected_table', columns='*')
```

## 🎯 Best Practices

### 1. Use Context Managers

```python
# Automatically handles cleanup
with SupabaseManager() as manager:
    users = manager.select('users')
    # ... do work ...
# Connection automatically closed
```

### 2. Async for Performance

```python
# For high-performance applications
async with AsyncSupabaseManager() as manager:
    # Parallel queries
    users, clients, jobs = await asyncio.gather(
        manager.select('users'),
        manager.select('clients'),
        manager.select('jobs')
    )
```

### 3. Error Handling

```python
from supabase import SupabaseManager

try:
    manager = SupabaseManager()
    result = manager.select('users', filters={'id': 'non-existent'})

    if not result.data:
        print("No results found")

except Exception as e:
    print(f"Error: {e}")
finally:
    manager.close()
```

### 4. Batch Operations for Efficiency

```python
# Instead of multiple single inserts
for user in users:
    manager.insert('users', user)  # ❌ Inefficient

# Use bulk insert
manager.insert('users', users)  # ✅ Efficient
```

## 📖 Complete Examples

Run the examples file to see all features in action:

```bash
python supabase_examples.py
```

The examples cover:
1. Basic CRUD operations
2. Advanced filtering
3. Bulk operations
4. Authentication flows
5. Storage management
6. Real-time subscriptions
7. RPC calls
8. Context managers
9. Service role usage
10. Utility methods
11. Error handling

## 🔐 Security Considerations

### Row Level Security (RLS)

- **Anon Key**: Use for client-side operations - respects RLS policies
- **Service Role Key**: Use for server-side admin operations - bypasses RLS

```python
# Client-side (respects RLS)
client = SupabaseManager(use_service_role=False)

# Server-side admin (bypasses RLS)
admin = SupabaseManager(use_service_role=True)
```

### Never Expose Service Role Key

```python
# ❌ NEVER do this in client-side code
# Service role key should only be used server-side

# ✅ Use environment variables
SUPABASE_SERVICE_ROLE_KEY=your-key  # In .env file, never commit to git
```

## 🚨 Common Issues

### 1. Authentication Errors

```python
# Ensure credentials are correct
manager = SupabaseManager()
print(manager.url)  # Verify URL
print(manager.is_service_role)  # Check which key is being used
```

### 2. RLS Blocking Queries

```python
# If queries return empty when data exists, check RLS policies
# Option 1: Fix RLS policies in Supabase dashboard
# Option 2: Use service role for admin operations
admin = SupabaseManager(use_service_role=True)
```

### 3. Connection Issues

```python
# Test connection
try:
    manager = SupabaseManager()
    result = manager.select('users', limit=1)
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

## 📊 Performance Tips

### 1. Use Async for I/O-Bound Operations

```python
# Synchronous (blocking)
users = manager.select('users')
clients = manager.select('clients')
# Total time: ~200ms + ~200ms = 400ms

# Async (non-blocking)
async with AsyncSupabaseManager() as manager:
    users, clients = await asyncio.gather(
        manager.select('users'),
        manager.select('clients')
    )
# Total time: max(200ms, 200ms) = 200ms
```

### 2. Limit Data Retrieved

```python
# ❌ Don't retrieve all columns if not needed
manager.select('users', columns='*')

# ✅ Select only required columns
manager.select('users', columns='id,name,email')
```

### 3. Use Pagination

```python
# Get results in chunks
page_size = 100
offset = 0

while True:
    results = manager.select('users', limit=page_size, offset=offset)
    if not results.data:
        break

    process(results.data)
    offset += page_size
```

## 🧪 Testing

```python
# Mock for testing
from unittest.mock import MagicMock, patch

def test_select():
    with patch('supabase.create_client') as mock_client:
        mock_client.return_value.table.return_value.select.return_value.execute.return_value.data = [
            {'id': 1, 'name': 'Test User'}
        ]

        manager = SupabaseManager()
        result = manager.select('users')

        assert len(result.data) == 1
        assert result.data[0]['name'] == 'Test User'
```

## 📝 API Reference

### SupabaseManager (Sync)

#### Database Operations
- `select(table, columns, filters, limit, offset, order_by, ascending, count)` - Query data
- `insert(table, data, upsert, on_conflict)` - Insert rows
- `update(table, data, filters)` - Update rows
- `delete(table, filters)` - Delete rows
- `rpc(function_name, params)` - Call PostgreSQL function

#### Authentication
- `sign_up(email, password, user_metadata)` - Register user
- `sign_in(email, password)` - Sign in with password
- `sign_in_with_otp(email, phone)` - Magic link or SMS OTP
- `sign_in_with_oauth(provider, redirect_to)` - OAuth sign in
- `sign_out()` - Sign out current user
- `get_user()` - Get current user
- `update_user(attributes)` - Update user profile
- `reset_password_email(email)` - Send password reset

#### Storage
- `list_buckets()` - List all buckets
- `create_bucket(name, public, file_size_limit)` - Create bucket
- `delete_bucket(name)` - Delete bucket
- `upload_file(bucket, path, file, file_options)` - Upload file
- `download_file(bucket, path)` - Download file
- `list_files(bucket, path, limit, offset)` - List files
- `delete_files(bucket, paths)` - Delete files
- `move_file(bucket, from_path, to_path)` - Move/rename file
- `get_public_url(bucket, path)` - Get public URL
- `create_signed_url(bucket, path, expires_in)` - Create signed URL

#### Realtime
- `subscribe_to_table(table, callback, event, schema, filter_column, filter_value)` - Subscribe to changes
- `unsubscribe(channel)` - Unsubscribe from channel

#### Utilities
- `count_rows(table, filters)` - Count rows
- `close()` - Close connection

### AsyncSupabaseManager

All methods from `SupabaseManager` with `async`/`await` support, plus:

- `batch_select(tables, columns)` - Query multiple tables in parallel

## 🤝 Contributing

This module is part of the ProActive People recruitment automation system. For updates or issues:

1. Check existing documentation in `SUPABASE_README.md`
2. Review examples in `supabase_examples.py`
3. Test changes thoroughly before deployment

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client GitHub](https://github.com/supabase/supabase-py)
- [ProActive People Website](https://www.proactivepeople.com)

## 📄 License

Proprietary - ProActive People Ltd. © 2025

---

**Version:** 1.0.0
**Last Updated:** January 2025
**Verified Against:** Supabase Python SDK (supabase-py) latest version
**Documentation Source:** Context7 MCP + Supabase MCP + Official Docs
