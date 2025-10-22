#!/usr/bin/env python3
"""
Apply Migration 003 - Align Tables with CSV Structure
This script applies the migration by executing SQL via Supabase MCP
"""

import os
import sys
from supabase import create_client

# Supabase credentials
SUPABASE_URL = 'https://njjolzejmzqpridlgplb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5qam9semVqbXpxcHJpZGxncGxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExMzgyMzQsImV4cCI6MjA3NjcxNDIzNH0.CPbhvJ50KH3TeanjpjFX76WezJm1jgtWk0KXDkfJO1E'

def main():
    print("Applying Migration 003: Align Tables with CSV Structure")
    print("="*80)

    # Read migration file
    with open('sql/migrations/003_align_tables_with_csv_structure.sql', 'r') as f:
        content = f.read()

    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Extract CREATE TABLE statements
    tables = []
    current_table = []
    in_table = False

    for line in content.split('\n'):
        if 'CREATE TABLE' in line:
            if current_table:
                tables.append('\n'.join(current_table))
            current_table = [line]
            in_table = True
        elif in_table:
            current_table.append(line)
            if line.strip().endswith(');'):
                tables.append('\n'.join(current_table))
                current_table = []
                in_table = False

    print(f"\nFound {len(tables)} tables to create\n")

    # Execute each table creation
    for i, table_sql in enumerate(tables, 1):
        table_name = table_sql.split('CREATE TABLE')[1].split('(')[0].strip()
        print(f"[{i}/{len(tables)}] Creating table: {table_name}...")

        try:
            # Use rpc to execute SQL (note: this may not work for DDL)
            result = supabase.rpc('exec_sql', {'query': table_sql}).execute()
            print(f"  ✓ Success")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "="*80)
    print("Migration application complete!")
    print("\nNote: If errors occurred, please apply the migration manually via:")
    print("  1. Supabase Dashboard SQL Editor")
    print("  2. psql command line")
    print("  3. Supabase CLI: supabase db push")

if __name__ == '__main__':
    main()
