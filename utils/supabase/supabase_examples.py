"""
Comprehensive Usage Examples for Supabase Python Module

This file demonstrates all features of the supabase.py module with
real-world examples based on the ProActive People recruitment system.

Author: ProActive People Recruitment System
Date: 2025
"""

from utils.supabase.supabase import SupabaseManager, get_supabase_client
from datetime import datetime, timedelta
import json


def example_basic_operations():
    """Basic CRUD operations examples"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Database Operations")
    print("="*60)

    # Initialize client
    manager = SupabaseManager()

    # 1. SELECT - Get all clients
    print("\n1. Select all clients:")
    clients = manager.select('clients', columns='client_id,company_name,industry_sector', limit=5)
    for client in clients.data:
        print(f"  - {client['company_name']} ({client['industry_sector']})")

    # 2. INSERT - Create a new candidate
    print("\n2. Insert new candidate:")
    new_candidate = {
        'candidate_id': f'CAND-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'primary_email': 'sarah.johnson@example.com',
        'phone_number': '+44 7700 900123',
        'job_title_target': 'Business Development Manager',
        'primary_skills': 'Sales, Negotiation, CRM (Salesforce)',
        'industry_experience': 'Technology, SaaS',
        'current_status': 'Active - Looking',
        'desired_salary': 45000.00
    }
    result = manager.insert('candidates', new_candidate)
    print(f"  Created candidate: {result.data[0]['first_name']} {result.data[0]['last_name']}")

    # 3. UPDATE - Update candidate status
    print("\n3. Update candidate status:")
    updated = manager.update(
        'candidates',
        {'current_status': 'Interviewed', 'last_contact_date': datetime.now().date().isoformat()},
        {'primary_email': 'sarah.johnson@example.com'}
    )
    print(f"  Updated {len(updated.data)} candidate(s)")

    # 4. SELECT with filters - Find active candidates in tech sector
    print("\n4. Select with advanced filters:")
    active_tech = manager.select(
        'candidates',
        columns='first_name,last_name,job_title_target,desired_salary',
        filters={
            'current_status__ilike': '%active%',
            'industry_experience__ilike': '%technology%',
            'desired_salary__gte': 35000
        },
        order_by='desired_salary',
        ascending=False,
        limit=5
    )
    print(f"  Found {len(active_tech.data)} active tech candidates:")
    for candidate in active_tech.data:
        print(f"    - {candidate['first_name']} {candidate['last_name']}: {candidate['job_title_target']} (£{candidate['desired_salary']})")

    manager.close()


def example_advanced_filters():
    """Advanced filtering examples"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Advanced Filtering")
    print("="*60)

    manager = SupabaseManager()

    # Example 1: Range queries
    print("\n1. Clients with lifetime revenue between £50k and £200k:")
    clients = manager.select(
        'clients',
        columns='company_name,lifetime_revenue_gbp,total_placements',
        filters={
            'lifetime_revenue_gbp__gte': 50000,
            'lifetime_revenue_gbp__lte': 200000
        },
        order_by='lifetime_revenue_gbp',
        ascending=False
    )
    for client in clients.data:
        print(f"  - {client['company_name']}: £{client['lifetime_revenue_gbp']:,.2f} ({client['total_placements']} placements)")

    # Example 2: Pattern matching
    print("\n2. Companies in Bristol (pattern matching):")
    bristol_clients = manager.select(
        'clients',
        columns='company_name,city,postcode',
        filters={'city__ilike': '%bristol%'}
    )
    for client in bristol_clients.data:
        print(f"  - {client['company_name']}: {client['city']}, {client['postcode']}")

    # Example 3: IN queries
    print("\n3. Clients in Sales or Contact Centre sectors:")
    sectors = ['Sales Jobs', 'Contact Centre']
    sector_clients = manager.select(
        'clients',
        columns='company_name,primary_service',
        filters={'primary_service__in': sectors}
    )
    for client in sector_clients.data:
        print(f"  - {client['company_name']}: {client['primary_service']}")

    # Example 4: Combining multiple filters
    print("\n4. High-value active clients (multiple filters):")
    premium_clients = manager.select(
        'clients',
        columns='company_name,account_status,account_tier,lifetime_revenue_gbp',
        filters={
            'account_status': 'Active',
            'account_tier': 'Premium',
            'lifetime_revenue_gbp__gte': 100000
        },
        order_by='lifetime_revenue_gbp',
        ascending=False
    )
    for client in premium_clients.data:
        print(f"  - {client['company_name']}: {client['account_tier']} (£{client['lifetime_revenue_gbp']:,.2f})")

    manager.close()


def example_bulk_operations():
    """Bulk insert and update examples"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Bulk Operations")
    print("="*60)

    manager = SupabaseManager()

    # Bulk insert - Multiple candidates at once
    print("\n1. Bulk insert candidates:")
    candidates = [
        {
            'candidate_id': f'CAND-BULK-001',
            'first_name': 'John',
            'last_name': 'Smith',
            'primary_email': 'john.smith@example.com',
            'job_title_target': 'Sales Executive',
            'current_status': 'Active - Looking'
        },
        {
            'candidate_id': f'CAND-BULK-002',
            'first_name': 'Emma',
            'last_name': 'Williams',
            'primary_email': 'emma.williams@example.com',
            'job_title_target': 'Account Manager',
            'current_status': 'Active - Looking'
        },
        {
            'candidate_id': f'CAND-BULK-003',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'primary_email': 'michael.brown@example.com',
            'job_title_target': 'IT Support Specialist',
            'current_status': 'Passive'
        }
    ]

    result = manager.insert('candidates', candidates)
    print(f"  Inserted {len(result.data)} candidates")

    # Upsert - Insert or update
    print("\n2. Upsert operation (update if exists, insert if not):")
    upsert_data = [
        {
            'candidate_id': 'CAND-BULK-001',  # Existing
            'first_name': 'John',
            'last_name': 'Smith',
            'current_status': 'Placed',  # Updated status
            'last_contact_date': datetime.now().date().isoformat()
        }
    ]
    result = manager.insert('candidates', upsert_data, upsert=True)
    print(f"  Upserted {len(result.data)} candidate(s)")

    manager.close()


def example_authentication():
    """Authentication examples"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Authentication & User Management")
    print("="*60)

    manager = SupabaseManager()

    try:
        # Sign up new user
        print("\n1. Sign up new recruiter:")
        user = manager.sign_up(
            'recruiter@proactivepeople.com',
            'SecurePassword123!',
            user_metadata={
                'first_name': 'Jane',
                'last_name': 'Recruiter',
                'role': 'Senior Recruiter',
                'department': 'Sales Jobs'
            }
        )
        print(f"  User created: {user.user.email if user.user else 'Success'}")

        # Sign in
        print("\n2. Sign in user:")
        session = manager.sign_in('recruiter@proactivepeople.com', 'SecurePassword123!')
        print(f"  Signed in: {session.user.email if session.user else 'Success'}")

        # Get current user
        print("\n3. Get current user:")
        current_user = manager.get_user()
        if current_user and current_user.user:
            print(f"  Current user: {current_user.user.email}")
            print(f"  Metadata: {current_user.user.user_metadata}")

        # Update user profile
        print("\n4. Update user profile:")
        updated_user = manager.update_user({
            'data': {
                'department': 'Technical Jobs',
                'phone': '+44 117 937 7199'
            }
        })
        print(f"  Profile updated")

    except Exception as e:
        print(f"  Auth example skipped: {e}")

    manager.close()


def example_storage_operations():
    """File storage examples"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Storage Operations")
    print("="*60)

    manager = SupabaseManager()

    try:
        # List buckets
        print("\n1. List storage buckets:")
        buckets = manager.list_buckets()
        for bucket in buckets:
            print(f"  - {bucket.name} (Public: {bucket.public})")

        # Create bucket
        print("\n2. Create bucket for CVs:")
        # manager.create_bucket('candidate-cvs', public=False, file_size_limit=10485760)  # 10MB
        # print("  Bucket created: candidate-cvs")

        # Upload file (example with text file)
        print("\n3. Upload file:")
        sample_cv = b"John Smith\nSenior Sales Executive\nExperience: 5 years..."
        # result = manager.upload_file(
        #     'candidate-cvs',
        #     'candidates/john-smith-cv.txt',
        #     sample_cv,
        #     {'content-type': 'text/plain'}
        # )
        # print(f"  Uploaded: candidates/john-smith-cv.txt")

        # List files
        print("\n4. List files in bucket:")
        # files = manager.list_files('candidate-cvs', 'candidates/')
        # for file in files:
        #     print(f"  - {file['name']} ({file['metadata']['size']} bytes)")

        # Create signed URL for private access
        print("\n5. Create temporary download link:")
        # signed_url = manager.create_signed_url('candidate-cvs', 'candidates/john-smith-cv.txt', expires_in=3600)
        # print(f"  Signed URL (1 hour): {signed_url['signedURL']}")

    except Exception as e:
        print(f"  Storage example info: {e}")

    manager.close()


def example_rpc_functions():
    """Remote Procedure Call (PostgreSQL functions) examples"""
    print("\n" + "="*60)
    print("EXAMPLE 6: RPC - PostgreSQL Functions")
    print("="*60)

    manager = SupabaseManager()

    try:
        # Example 1: Call custom function
        print("\n1. Call custom PostgreSQL function:")
        # Assuming you have a function like: CREATE FUNCTION get_candidate_stats(candidate_status TEXT)
        # result = manager.rpc('get_candidate_stats', {'candidate_status': 'Active - Looking'})
        # print(f"  Function result: {result.data}")

        # Example 2: Complex aggregation function
        print("\n2. Call aggregation function:")
        # result = manager.rpc('calculate_monthly_revenue', {'year': 2025, 'month': 1})
        # print(f"  Monthly revenue: {result.data}")

        print("  (Note: RPC examples require custom PostgreSQL functions to be created)")

    except Exception as e:
        print(f"  RPC example info: {e}")

    manager.close()


def example_realtime_subscriptions():
    """Real-time data subscription examples"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Real-time Subscriptions")
    print("="*60)

    manager = SupabaseManager()

    # Define callback functions
    def handle_new_candidate(payload):
        """Called when new candidate is inserted"""
        record = payload.get('record', {})
        print(f"\n  🆕 New candidate added: {record.get('first_name')} {record.get('last_name')}")

    def handle_status_update(payload):
        """Called when candidate status changes"""
        record = payload.get('record', {})
        print(f"\n  📝 Candidate updated: {record.get('candidate_id')} - Status: {record.get('current_status')}")

    def handle_new_client(payload):
        """Called when new client is added"""
        record = payload.get('record', {})
        print(f"\n  🏢 New client: {record.get('company_name')} ({record.get('industry_sector')})")

    try:
        print("\n1. Subscribe to new candidates:")
        channel1 = manager.subscribe_to_table('candidates', handle_new_candidate, event='INSERT')
        print("  ✓ Subscribed to candidate inserts")

        print("\n2. Subscribe to candidate updates:")
        channel2 = manager.subscribe_to_table('candidates', handle_status_update, event='UPDATE')
        print("  ✓ Subscribed to candidate updates")

        print("\n3. Subscribe to new clients:")
        channel3 = manager.subscribe_to_table('clients', handle_new_client, event='INSERT')
        print("  ✓ Subscribed to client inserts")

        print("\n4. Subscribe with filter (only active candidates):")
        def handle_active_candidate(payload):
            record = payload.get('record', {})
            print(f"\n  ⭐ Active candidate: {record.get('first_name')} {record.get('last_name')}")

        channel4 = manager.subscribe_to_table(
            'candidates',
            handle_active_candidate,
            event='INSERT',
            filter_column='current_status',
            filter_value='Active - Looking'
        )
        print("  ✓ Subscribed to active candidates only")

        print("\n  Listening for changes... (Press Ctrl+C to stop)")
        print("  (In production, this would run continuously)")

        # In a real application, you would keep the connection alive:
        # import time
        # while True:
        #     time.sleep(1)

    except Exception as e:
        print(f"  Realtime example info: {e}")
    finally:
        # Cleanup
        try:
            manager.unsubscribe(channel1)
            manager.unsubscribe(channel2)
            manager.unsubscribe(channel3)
            manager.unsubscribe(channel4)
            print("\n  Unsubscribed from all channels")
        except:
            pass

    manager.close()


def example_context_manager():
    """Using SupabaseManager with context manager"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Context Manager (Best Practice)")
    print("="*60)

    print("\n1. Using 'with' statement for automatic cleanup:")

    # Context manager automatically handles cleanup
    with SupabaseManager() as manager:
        # All operations within this block
        clients = manager.select('clients', columns='company_name,account_status', limit=3)
        print(f"  Found {len(clients.data)} clients:")
        for client in clients.data:
            print(f"    - {client['company_name']}: {client['account_status']}")

    # Manager is automatically closed when exiting the 'with' block
    print("  ✓ Client automatically closed")


def example_service_role():
    """Using service role for admin operations"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Service Role (Admin Operations)")
    print("="*60)

    print("\n1. Regular client (respects Row Level Security):")
    regular_manager = SupabaseManager(use_service_role=False)
    print(f"  Using service role: {regular_manager.is_service_role}")
    regular_manager.close()

    print("\n2. Admin client (bypasses Row Level Security):")
    admin_manager = SupabaseManager(use_service_role=True)
    print(f"  Using service role: {admin_manager.is_service_role}")

    # Admin operations that bypass RLS
    # all_data = admin_manager.select('protected_table', columns='*')

    admin_manager.close()


def example_utility_methods():
    """Utility and helper methods"""
    print("\n" + "="*60)
    print("EXAMPLE 10: Utility Methods")
    print("="*60)

    manager = SupabaseManager()

    # Count rows
    print("\n1. Count total candidates:")
    total_candidates = manager.count_rows('candidates')
    print(f"  Total candidates: {total_candidates}")

    print("\n2. Count active candidates:")
    active_count = manager.count_rows('candidates', {'current_status__ilike': '%active%'})
    print(f"  Active candidates: {active_count}")

    print("\n3. Count clients by account tier:")
    for tier in ['Premium', 'Standard', 'Basic']:
        count = manager.count_rows('clients', {'account_tier': tier})
        print(f"  {tier} clients: {count}")

    manager.close()


def example_error_handling():
    """Proper error handling examples"""
    print("\n" + "="*60)
    print("EXAMPLE 11: Error Handling")
    print("="*60)

    manager = SupabaseManager()

    # Example 1: Handle missing data
    print("\n1. Handle non-existent records gracefully:")
    try:
        result = manager.select('candidates', filters={'candidate_id': 'NON-EXISTENT-ID'})
        if not result.data:
            print("  No candidate found with that ID")
        else:
            print(f"  Found: {result.data}")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 2: Handle duplicate inserts
    print("\n2. Handle duplicate key errors:")
    try:
        duplicate = {
            'candidate_id': 'EXISTING-ID',
            'first_name': 'Test',
            'last_name': 'User'
        }
        result = manager.insert('candidates', duplicate)
        print(f"  Inserted: {result.data}")
    except Exception as e:
        print(f"  Expected error for duplicate: {type(e).__name__}")

    # Example 3: Use upsert to handle duplicates
    print("\n3. Use upsert to handle duplicates automatically:")
    try:
        result = manager.insert('candidates', duplicate, upsert=True)
        print(f"  Upserted successfully")
    except Exception as e:
        print(f"  Error: {e}")

    manager.close()


def run_all_examples():
    """Run all examples in sequence"""
    print("\n" + "="*70)
    print(" ProActive People - Supabase Python Module Examples")
    print("="*70)

    examples = [
        ("Basic Operations", example_basic_operations),
        ("Advanced Filters", example_advanced_filters),
        ("Bulk Operations", example_bulk_operations),
        ("Authentication", example_authentication),
        ("Storage", example_storage_operations),
        ("RPC Functions", example_rpc_functions),
        ("Real-time", example_realtime_subscriptions),
        ("Context Manager", example_context_manager),
        ("Service Role", example_service_role),
        ("Utility Methods", example_utility_methods),
        ("Error Handling", example_error_handling),
    ]

    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n⚠️  {name} example encountered an error: {e}")

    print("\n" + "="*70)
    print(" All Examples Complete!")
    print("="*70)


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Or run individual examples:
    # example_basic_operations()
    # example_advanced_filters()
    # example_authentication()
    # etc.
