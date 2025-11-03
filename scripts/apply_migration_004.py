"""
Apply Migration 004: Create exec_sql RPC Function

This script creates the exec_sql PostgreSQL function in Supabase,
enabling dynamic SQL execution for NL2SQL queries.

Usage:
    python scripts/apply_migration_004.py
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def apply_migration():
    """Apply migration 004 to Supabase."""

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        return False

    print(f"📡 Connecting to Supabase: {supabase_url}")

    try:
        # Connect to Supabase
        supabase: Client = create_client(supabase_url, supabase_key)

        # Read migration file
        migration_file = project_root / "sql" / "migrations" / "004_create_exec_sql_function.sql"
        print(f"📄 Reading migration: {migration_file}")

        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Execute migration
        print("🔄 Executing migration...")

        # Note: Supabase Python client doesn't directly support executing DDL
        # You need to use the SQL Editor or PostgREST API
        print("\n" + "="*80)
        print("⚠️  Python client doesn't support DDL execution directly.")
        print("    Please apply this migration manually via Supabase SQL Editor:")
        print("="*80)
        print("\n1. Go to: https://supabase.com/dashboard")
        print("2. Open SQL Editor")
        print("3. Paste and run the contents of:")
        print(f"   {migration_file}")
        print("\n" + "="*80)

        # Alternative: Show how to verify if function exists
        print("\n✅ After applying, verify with:")
        print("   SELECT exec_sql('SELECT id, first_name FROM candidates LIMIT 5');")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Migration 004: Create exec_sql RPC Function")
    print("="*80 + "\n")

    success = apply_migration()

    if success:
        print("\n✅ Migration instructions displayed")
    else:
        print("\n❌ Migration failed")
        sys.exit(1)
