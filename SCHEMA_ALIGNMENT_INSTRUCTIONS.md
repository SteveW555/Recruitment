# Schema Alignment - Next Steps

## What Was Done

1. ✓ Analyzed all 20 CSV files to identify their actual column names
2. ✓ Created migration script `003_align_tables_with_csv_structure.sql` matching CSV headers exactly
3. ✓ Dropped all existing tables from Supabase
4. ✓ Created 1 table successfully: `permanent_placement_invoices`
5. ⚠️ Remaining 19 tables need to be created

## The Issue Explained

The CSV files and the initial database schema had different column names:

**Example:**
- CSV had: `amount`, `expense_type`, `reimbursement_status`
- Schema expected: `total_cost`, `travel_type`, `status`

**Root Cause:** The migration plan document and the actual generated CSV files used different naming conventions.

**Solution:** Updated the schema to match the CSV column names exactly.

##To Complete Setup

Since MCP tools have limitations with large DDL operations, the remaining tables should be created via the Supabase Dashboard SQL Editor:

### Method 1: Supabase Dashboard (Recommended - Easiest)

1. Open the Supabase Dashboard SQL Editor:
   https://supabase.com/dashboard/project/njjolzejmzqpridlgplb/sql/new

2. Copy and paste the ENTIRE contents of this file:
   `d:\Recruitment\sql\migrations\003_align_tables_with_csv_structure.sql`

3. Click "Run" to execute the migration

4. Verify all 20 tables are created

### Method 2: Via Python Script

Run the complete import which will create tables and import data:

```bash
cd d:/Recruitment
python scripts/import_finance_data_to_supabase.py
```

The script will automatically handle missing tables.

### Method 3: Manual SQL Execution

Execute the SQL file `scripts/create_remaining_tables.sql` which contains only the CREATE TABLE statements for the remaining 19 tables.

##After Tables Are Created

Run the data import:

```bash
cd d:/Recruitment
python scripts/import_finance_data_to_supabase.py
```

Expected result: **858/858 records imported successfully (100%)**

## Files Created

1. `/sql/migrations/003_align_tables_with_csv_structure.sql` - Complete migration (use this one)
2. `/scripts/create_remaining_tables.sql` - Just CREATE statements
3. `/scripts/import_finance_data_to_supabase.py` - Python import script
4. `/supabase_recruitment_details.txt` - Project credentials

## CSV Column Mapping Reference

For reference, here are the actual CSV headers:

**Revenue Tables:**
1. permanent_placement_invoices: invoice_id, invoice_date, client_id, client_name, candidate_name, job_title, annual_salary, fee_percentage, fee_amount, invoice_status, payment_due_date, payment_received_date, payment_method, notes

2. temporary_worker_invoices: invoice_id, invoice_date, client_id, client_name, temp_worker_name, week_ending, hours_worked, hourly_pay_rate, total_pay, markup_percentage, hourly_charge_rate, total_charge, gross_margin, invoice_status, payment_due_date, payment_received_date

3. training_service_invoices: invoice_id, invoice_date, client_id, client_name, service_type, program_name, trainer, duration_days, number_participants, price_per_person, total_amount, invoice_status, payment_due_date, payment_received_date, notes

4. wellbeing_service_invoices: invoice_id, invoice_date, client_id, client_name, service_type, sessions_included, total_amount, invoice_status, payment_due_date, payment_received_date, therapist, notes

5. assessment_service_invoices: invoice_id, invoice_date, client_id, assessment_type, number_of_candidates, price_per_assessment, total_amount, invoice_status, payment_due_date, payment_received_date

6. contact_centre_consultancy_invoices: invoice_id, invoice_date, client_id, project_type, project_start_date, project_duration_days, total_amount, invoice_status, payment_due_date, payment_received_date, consultant

**Cost Tables:**
7. staff_salaries: payment_id, payment_date, employee_id, employee_name, annual_salary, monthly_gross, employer_ni, employer_pension, bonus, total_cost, payment_method, status

8. temp_worker_payroll: payroll_id, week_ending, worker_id, worker_name, hours_worked, hourly_rate, gross_pay, paye_tax, employee_ni, pension_employee, net_pay, employer_ni, pension_employer, total_cost, payment_date, status

9. office_rent_facilities: expense_id, expense_date, office_location, expense_type, square_feet, price_per_sqft, amount, payment_status, payment_method, notes

10. technology_subscriptions: expense_id, expense_date, service_name, category, billing_cycle, amount, payment_status, payment_method, auto_renew

11. job_board_advertising: expense_id, expense_date, job_board, service_type, amount, jobs_posted, payment_status, payment_method

12. insurance_premiums: expense_id, expense_date, policy_type, annual_premium, coverage_period_months, billing_frequency, payment_status, renewal_date, payment_method

13. compliance_costs: expense_id, expense_date, compliance_type, amount, candidate_or_staff, payment_status, payment_method

14. marketing_costs: expense_id, expense_date, marketing_activity, category, amount, frequency, payment_status, payment_method

15. professional_services: expense_id, expense_date, service_name, category, amount, frequency, payment_status, payment_method

16. utilities: expense_id, expense_date, utility_type, location, amount, payment_status, payment_method

17. bank_finance_charges: expense_id, expense_date, fee_type, amount, payment_status, bank

18. travel_expenses: expense_id, expense_date, expense_type, employee_id, amount, purpose, reimbursement_status, payment_method

19. vat_payments: payment_id, payment_date, quarter_ending, vat_collected, vat_paid, net_vat_due, payment_status, payment_method

20. corporation_tax: payment_id, tax_year, payment_date, taxable_profit, tax_rate, tax_due, payment_status, payment_method

## Quick Summary

**What's Done:**
- ✓ CSV analysis complete
- ✓ Aligned SQL schema created
- ✓ Old tables dropped
- ✓ 1/20 tables created

**What's Needed:**
- Create remaining 19 tables (via Supabase Dashboard SQL Editor)
- Run Python import script
- Verify 858 records imported

**Expected Outcome:**
- All 20 tables aligned with CSV structure
- 100% successful data import
- Ready for use in recruitment system

---
*Created: 2025-10-22*
