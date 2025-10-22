#!/usr/bin/env python3
"""
ProActive People - Finance Data Importer for Supabase
Created: 2025-10-22
Purpose: Import 20 CSV files with 858+ financial records into Supabase PostgreSQL

Usage:
    python scripts/import_finance_data_to_supabase.py

Requirements:
    pip install supabase pandas python-dotenv
"""

import os
import sys
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv
from supabase import create_client, Client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://njjolzejmzqpridlgplb.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5qam9semVqbXpxcHJpZGxncGxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExMzgyMzQsImV4cCI6MjA3NjcxNDIzNH0.CPbhvJ50KH3TeanjpjFX76WezJm1jgtWk0KXDkfJO1E')

# File mapping: CSV filename -> Supabase table name
FILE_TABLE_MAPPING = {
    '01_permanent_placement_invoices.csv': 'permanent_placement_invoices',
    '02_temporary_worker_invoices.csv': 'temporary_worker_invoices',
    '03_training_service_invoices.csv': 'training_service_invoices',
    '04_wellbeing_service_invoices.csv': 'wellbeing_service_invoices',
    '05_assessment_service_invoices.csv': 'assessment_service_invoices',
    '06_contact_centre_consultancy_invoices.csv': 'contact_centre_consultancy_invoices',
    '07_staff_salaries.csv': 'staff_salaries',
    '08_temp_worker_payroll.csv': 'temp_worker_payroll',
    '09_office_rent_facilities.csv': 'office_rent_facilities',
    '10_technology_subscriptions.csv': 'technology_subscriptions',
    '11_job_board_advertising.csv': 'job_board_advertising',
    '12_insurance_premiums.csv': 'insurance_premiums',
    '13_compliance_costs.csv': 'compliance_costs',
    '14_marketing_costs.csv': 'marketing_costs',
    '15_professional_services.csv': 'professional_services',
    '16_utilities.csv': 'utilities_expenses',
    '17_bank_finance_charges.csv': 'bank_finance_charges',
    '18_travel_expenses.csv': 'travel_expenses',
    '19_vat_payments.csv': 'vat_payments',
    '20_corporation_tax.csv': 'corporation_tax',
}

# Fields that should be treated as boolean
BOOLEAN_FIELDS = {'auto_renew'}

# Fields that should be converted to integers
INTEGER_FIELDS = {
    'duration_days', 'number_participants', 'sessions_included',
    'number_of_candidates', 'project_duration_days', 'square_feet',
    'number_licenses', 'number_of_ads', 'coverage_period_months',
    'quantity', 'impressions', 'clicks', 'applications', 'transaction_count'
}

# Fields that are nullable/optional
NULLABLE_FIELDS = {
    'job_title', 'payment_received_date', 'payment_method', 'notes',
    'bonus', 'lease_end_date', 'impressions', 'clicks', 'applications',
    'roi_estimate', 'usage_amount', 'unit_rate', 'transaction_count',
    'distance_miles', 'mileage_rate'
}


def parse_value(key: str, value: str) -> Any:
    """Parse and convert CSV values to appropriate Python types."""
    # Handle empty strings
    if value == '' or value is None:
        return None if key in NULLABLE_FIELDS else value

    # Convert boolean fields
    if key in BOOLEAN_FIELDS:
        return value.lower() in ('true', 't', 'yes', 'y', '1')

    # Convert integer fields
    if key in INTEGER_FIELDS:
        try:
            return int(float(value))  # Handle values like "50.0"
        except (ValueError, TypeError):
            return None if key in NULLABLE_FIELDS else 0

    # Return string as-is
    return value


def read_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """Read CSV file and return list of dictionaries with proper type conversion."""
    records = []

    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                # Parse each value with type conversion
                parsed_row = {key: parse_value(key, value) for key, value in row.items()}
                records.append(parsed_row)

        logger.info(f"Read {len(records)} records from {file_path.name}")
        return records

    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return []


def batch_insert(supabase: Client, table_name: str, records: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, int]:
    """Insert records in batches and return statistics."""
    stats = {
        'total': len(records),
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        try:
            response = supabase.table(table_name).insert(batch).execute()
            stats['success'] += len(batch)
            logger.info(f"  Batch {batch_num}: Inserted {len(batch)} records into {table_name}")

        except Exception as e:
            stats['failed'] += len(batch)
            error_msg = f"Batch {batch_num} failed: {str(e)}"
            stats['errors'].append(error_msg)
            logger.error(f"  {error_msg}")

            # Try individual inserts for failed batch
            for record_num, record in enumerate(batch, start=1):
                try:
                    supabase.table(table_name).insert(record).execute()
                    stats['success'] += 1
                    stats['failed'] -= 1
                except Exception as record_error:
                    logger.error(f"    Record {record_num} failed: {str(record_error)}")

    return stats


def import_all_files(base_path: Path, supabase: Client) -> Dict[str, Any]:
    """Import all CSV files and return comprehensive statistics."""
    overall_stats = {
        'files_processed': 0,
        'files_failed': 0,
        'total_records': 0,
        'successful_inserts': 0,
        'failed_inserts': 0,
        'start_time': datetime.now(),
        'file_details': {}
    }

    for csv_file, table_name in FILE_TABLE_MAPPING.items():
        file_path = base_path / csv_file

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            overall_stats['files_failed'] += 1
            continue

        logger.info(f"\nProcessing: {csv_file} -> {table_name}")

        # Read CSV file
        records = read_csv_file(file_path)
        if not records:
            overall_stats['files_failed'] += 1
            continue

        # Insert records
        stats = batch_insert(supabase, table_name, records)

        # Update overall statistics
        overall_stats['files_processed'] += 1
        overall_stats['total_records'] += stats['total']
        overall_stats['successful_inserts'] += stats['success']
        overall_stats['failed_inserts'] += stats['failed']
        overall_stats['file_details'][csv_file] = stats

        # Log file summary
        logger.info(f"  Summary: {stats['success']}/{stats['total']} records inserted successfully")
        if stats['errors']:
            logger.warning(f"  Errors encountered: {len(stats['errors'])}")

    overall_stats['end_time'] = datetime.now()
    overall_stats['duration'] = (overall_stats['end_time'] - overall_stats['start_time']).total_seconds()

    return overall_stats


def print_summary(stats: Dict[str, Any]):
    """Print comprehensive import summary."""
    print("\n" + "="*80)
    print("FINANCE DATA IMPORT SUMMARY")
    print("="*80)
    print(f"\nExecution Time: {stats['duration']:.2f} seconds")
    print(f"Start Time: {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\nFiles Processed: {stats['files_processed']}/{len(FILE_TABLE_MAPPING)}")
    print(f"Files Failed: {stats['files_failed']}")

    print(f"\nTotal Records: {stats['total_records']}")
    print(f"Successful Inserts: {stats['successful_inserts']}")
    print(f"Failed Inserts: {stats['failed_inserts']}")
    print(f"Success Rate: {(stats['successful_inserts'] / stats['total_records'] * 100):.2f}%")

    print("\nPer-File Breakdown:")
    print("-" * 80)
    for file_name, file_stats in stats['file_details'].items():
        status = "✓" if file_stats['failed'] == 0 else "⚠"
        print(f"{status} {file_name:50s} {file_stats['success']:4d}/{file_stats['total']:4d}")

    if stats['failed_inserts'] > 0:
        print("\n⚠ WARNING: Some records failed to import. Check finance_import.log for details.")
    else:
        print("\n✓ SUCCESS: All records imported successfully!")

    print("="*80 + "\n")


def verify_data(supabase: Client) -> Dict[str, int]:
    """Verify record counts in all tables."""
    print("\nVerifying data in Supabase...")
    print("-" * 80)

    table_counts = {}
    total_records = 0

    for table_name in FILE_TABLE_MAPPING.values():
        try:
            response = supabase.table(table_name).select('id', count='exact').execute()
            count = response.count if hasattr(response, 'count') else len(response.data)
            table_counts[table_name] = count
            total_records += count
            print(f"{table_name:50s} {count:4d} records")
        except Exception as e:
            logger.error(f"Error verifying {table_name}: {str(e)}")
            table_counts[table_name] = -1

    print("-" * 80)
    print(f"{'TOTAL':50s} {total_records:4d} records")
    print()

    return table_counts


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("ProActive People - Finance Data Import to Supabase")
    print("="*80 + "\n")

    # Validate environment
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        logger.error("Please create a .env file or set environment variables")
        sys.exit(1)

    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"Connected to Supabase: {SUPABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        sys.exit(1)

    # Set CSV files path
    base_path = Path(__file__).parent.parent / 'finance_test_data' / 'financial_records'

    if not base_path.exists():
        logger.error(f"Error: Directory not found: {base_path}")
        sys.exit(1)

    logger.info(f"Reading CSV files from: {base_path}\n")

    # Import all files
    stats = import_all_files(base_path, supabase)

    # Print summary
    print_summary(stats)

    # Verify data
    table_counts = verify_data(supabase)

    # Check if verification matches import
    if stats['successful_inserts'] == sum(count for count in table_counts.values() if count > 0):
        logger.info("✓ Verification passed: Record counts match!")
    else:
        logger.warning("⚠ Verification warning: Record counts do not match import stats")

    # Exit with appropriate code
    sys.exit(0 if stats['failed_inserts'] == 0 else 1)


if __name__ == '__main__':
    main()
