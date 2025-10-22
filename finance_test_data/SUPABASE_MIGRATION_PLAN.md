# ProActive People - Finance Data Migration to Supabase

## Executive Summary

This document outlines the comprehensive plan to migrate 20 CSV files containing 858+ financial transaction records from the local filesystem to Supabase PostgreSQL database.

**Current State:**
- 20 CSV files in `finance_test_data/financial_records/`
- 858 total records covering 2024-2026
- 6 revenue categories (290 records)
- 14 cost categories (568 records)

**Target State:**
- Supabase project: `n8n tables` (pauypyjqosrenuxveskn)
- Region: eu-north-1
- PostgreSQL 15.8.1
- Properly normalized schema with referential integrity

---

## Data Inventory

### Revenue Files (6 files, 290 records)

| File | Table Name | Records | Key Fields |
|------|------------|---------|------------|
| 01_permanent_placement_invoices.csv | `permanent_placement_invoices` | 50 | invoice_id, client_id, candidate_name, annual_salary, fee_amount |
| 02_temporary_worker_invoices.csv | `temporary_worker_invoices` | 50 | invoice_id, client_id, temp_worker_name, hours_worked, gross_margin |
| 03_training_service_invoices.csv | `training_service_invoices` | 40 | invoice_id, client_id, program_name, trainer, duration_days |
| 04_wellbeing_service_invoices.csv | `wellbeing_service_invoices` | 50 | invoice_id, client_id, service_type, sessions_included |
| 05_assessment_service_invoices.csv | `assessment_service_invoices` | 50 | invoice_id, client_id, assessment_type, number_of_candidates |
| 06_contact_centre_consultancy_invoices.csv | `contact_centre_consultancy_invoices` | 50 | invoice_id, client_id, project_type, project_duration_days |

### Cost Files (14 files, 568 records)

| File | Table Name | Records | Key Fields |
|------|------------|---------|------------|
| 07_staff_salaries.csv | `staff_salaries` | 50 | payment_id, employee_id, annual_salary, employer_ni, employer_pension |
| 08_temp_worker_payroll.csv | `temp_worker_payroll` | 50 | payment_id, worker_name, gross_pay, paye_tax, employee_ni, net_pay |
| 09_office_rent_facilities.csv | `office_rent_facilities` | 50 | expense_id, office_location, square_feet, price_per_sqft |
| 10_technology_subscriptions.csv | `technology_subscriptions` | 50 | expense_id, service_name, billing_cycle, auto_renew |
| 11_job_board_advertising.csv | `job_board_advertising` | 50 | expense_id, job_board_name, ad_type, impressions |
| 12_insurance_premiums.csv | `insurance_premiums` | 10 | expense_id, policy_type, annual_premium, coverage_period_months |
| 13_compliance_costs.csv | `compliance_costs` | 50 | expense_id, expense_type, quantity, unit_cost |
| 14_marketing_costs.csv | `marketing_costs` | 50 | expense_id, campaign_type, marketing_channel, roi_estimate |
| 15_professional_services.csv | `professional_services` | 50 | expense_id, service_provider, service_type, hourly_rate |
| 16_utilities.csv | `utilities_expenses` | 50 | expense_id, utility_type, usage_amount, unit_rate |
| 17_bank_finance_charges.csv | `bank_finance_charges` | 50 | expense_id, charge_type, transaction_count |
| 18_travel_expenses.csv | `travel_expenses` | 50 | expense_id, employee_id, travel_type, distance_miles, purpose |
| 19_vat_payments.csv | `vat_payments` | 6 | payment_id, quarter_ending, vat_collected, vat_paid, net_vat_due |
| 20_corporation_tax.csv | `corporation_tax` | 2 | payment_id, tax_year, taxable_profit, tax_due |

---

## Database Schema Design

### Design Principles

1. **Normalization**: Create separate tables for each transaction type to maintain data integrity
2. **Foreign Keys**: Link to existing `clients` table where applicable
3. **Audit Trail**: Preserve created_at/updated_at timestamps
4. **Data Types**: Use appropriate PostgreSQL types (NUMERIC for money, DATE for dates)
5. **Constraints**: Add CHECK constraints for business rules (e.g., positive amounts)
6. **Indexes**: Create indexes on frequently queried fields (dates, client_id, status)

### Schema Categories

#### 1. Revenue Tables (6 tables)

**Common Fields Across All Revenue Tables:**
- Primary key: `id` (BIGINT, auto-increment)
- `invoice_id` (TEXT, UNIQUE) - Original CSV identifier
- `invoice_date` (DATE)
- `client_id` (TEXT) - Foreign key to existing clients table
- `client_name` (TEXT)
- `invoice_status` (TEXT) - 'Paid', 'Outstanding', 'Projected'
- `payment_due_date` (DATE)
- `payment_received_date` (DATE, nullable)
- `payment_method` (TEXT, nullable)
- `created_at` (TIMESTAMPTZ, default NOW())
- `updated_at` (TIMESTAMPTZ, default NOW())

**Revenue-Specific Tables:**

```sql
-- 1. Permanent Placement Invoices
CREATE TABLE permanent_placement_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    candidate_name TEXT NOT NULL,
    job_title TEXT,
    annual_salary NUMERIC(10,2) NOT NULL,
    fee_percentage NUMERIC(5,2) NOT NULL,
    fee_amount NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    payment_method TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (annual_salary > 0),
    CHECK (fee_percentage > 0 AND fee_percentage <= 100),
    CHECK (fee_amount > 0)
);

-- 2. Temporary Worker Invoices
CREATE TABLE temporary_worker_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    temp_worker_name TEXT NOT NULL,
    week_ending DATE NOT NULL,
    hours_worked NUMERIC(6,2) NOT NULL,
    hourly_pay_rate NUMERIC(8,2) NOT NULL,
    total_pay NUMERIC(10,2) NOT NULL,
    markup_percentage NUMERIC(5,2) NOT NULL,
    hourly_charge_rate NUMERIC(8,2) NOT NULL,
    total_charge NUMERIC(10,2) NOT NULL,
    gross_margin NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (hours_worked > 0),
    CHECK (total_charge > total_pay)
);

-- 3. Training Service Invoices
CREATE TABLE training_service_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    program_name TEXT NOT NULL,
    trainer TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    number_participants INTEGER NOT NULL,
    program_fee NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    payment_method TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (program_fee > 0),
    CHECK (duration_days > 0),
    CHECK (number_participants > 0)
);

-- 4. Wellbeing Service Invoices
CREATE TABLE wellbeing_service_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    service_type TEXT NOT NULL,
    sessions_included INTEGER NOT NULL,
    therapist TEXT NOT NULL,
    service_fee NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    payment_method TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (service_fee > 0),
    CHECK (sessions_included > 0)
);

-- 5. Assessment Service Invoices
CREATE TABLE assessment_service_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    number_of_candidates INTEGER NOT NULL,
    price_per_assessment NUMERIC(10,2) NOT NULL,
    total_fee NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    payment_method TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (total_fee > 0),
    CHECK (number_of_candidates > 0)
);

-- 6. Contact Centre Consultancy Invoices
CREATE TABLE contact_centre_consultancy_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    project_type TEXT NOT NULL,
    project_start_date DATE NOT NULL,
    project_duration_days INTEGER NOT NULL,
    project_fee NUMERIC(12,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    payment_method TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (project_fee > 0),
    CHECK (project_duration_days > 0)
);
```

#### 2. Cost Tables (14 tables)

**Personnel Costs:**

```sql
-- 7. Staff Salaries
CREATE TABLE staff_salaries (
    id BIGSERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    annual_salary NUMERIC(10,2) NOT NULL,
    monthly_gross NUMERIC(10,2) NOT NULL,
    employer_ni NUMERIC(10,2) NOT NULL,
    employer_pension NUMERIC(10,2) NOT NULL,
    bonus NUMERIC(10,2) DEFAULT 0,
    total_cost NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (annual_salary > 0),
    CHECK (total_cost > 0)
);

-- 8. Temp Worker Payroll
CREATE TABLE temp_worker_payroll (
    id BIGSERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    worker_id TEXT NOT NULL,
    worker_name TEXT NOT NULL,
    week_ending DATE NOT NULL,
    hours_worked NUMERIC(6,2) NOT NULL,
    hourly_rate NUMERIC(8,2) NOT NULL,
    gross_pay NUMERIC(10,2) NOT NULL,
    paye_tax NUMERIC(10,2) NOT NULL,
    employee_ni NUMERIC(10,2) NOT NULL,
    net_pay NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (hours_worked > 0),
    CHECK (gross_pay > 0)
);
```

**Facilities Costs:**

```sql
-- 9. Office Rent & Facilities
CREATE TABLE office_rent_facilities (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    office_location TEXT NOT NULL,
    square_feet INTEGER NOT NULL,
    price_per_sqft NUMERIC(8,2) NOT NULL,
    monthly_rent NUMERIC(10,2) NOT NULL,
    service_charge NUMERIC(10,2) NOT NULL,
    total_monthly_cost NUMERIC(10,2) NOT NULL,
    lease_end_date DATE,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (total_monthly_cost > 0)
);

-- 16. Utilities
CREATE TABLE utilities_expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    utility_type TEXT NOT NULL,
    supplier TEXT NOT NULL,
    usage_amount NUMERIC(10,2),
    unit_rate NUMERIC(8,4),
    total_cost NUMERIC(10,2) NOT NULL,
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (total_cost > 0)
);
```

**Technology Costs:**

```sql
-- 10. Technology Subscriptions
CREATE TABLE technology_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    service_name TEXT NOT NULL,
    service_category TEXT NOT NULL,
    monthly_cost NUMERIC(10,2) NOT NULL,
    billing_cycle TEXT NOT NULL,
    number_licenses INTEGER NOT NULL,
    auto_renew BOOLEAN NOT NULL,
    renewal_date DATE NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (monthly_cost > 0),
    CHECK (number_licenses > 0)
);

-- 11. Job Board Advertising
CREATE TABLE job_board_advertising (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    job_board_name TEXT NOT NULL,
    ad_type TEXT NOT NULL,
    number_of_ads INTEGER NOT NULL,
    cost_per_ad NUMERIC(10,2) NOT NULL,
    total_cost NUMERIC(10,2) NOT NULL,
    impressions INTEGER,
    clicks INTEGER,
    applications INTEGER,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (total_cost > 0),
    CHECK (number_of_ads > 0)
);
```

**Professional Services:**

```sql
-- 12. Insurance Premiums
CREATE TABLE insurance_premiums (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    policy_type TEXT NOT NULL,
    annual_premium NUMERIC(10,2) NOT NULL,
    coverage_period_months INTEGER NOT NULL,
    billing_frequency TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    renewal_date DATE NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (annual_premium > 0),
    CHECK (coverage_period_months > 0)
);

-- 13. Compliance Costs
CREATE TABLE compliance_costs (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    expense_type TEXT NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_cost NUMERIC(10,2) NOT NULL,
    total_cost NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (total_cost > 0),
    CHECK (quantity > 0)
);

-- 14. Marketing Costs
CREATE TABLE marketing_costs (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT NOT NULL,
    marketing_channel TEXT NOT NULL,
    campaign_budget NUMERIC(10,2) NOT NULL,
    actual_cost NUMERIC(10,2) NOT NULL,
    roi_estimate NUMERIC(8,2),
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (actual_cost > 0)
);

-- 15. Professional Services
CREATE TABLE professional_services (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    service_provider TEXT NOT NULL,
    service_type TEXT NOT NULL,
    description TEXT NOT NULL,
    hours_or_units NUMERIC(10,2) NOT NULL,
    hourly_rate NUMERIC(10,2) NOT NULL,
    total_cost NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (total_cost > 0)
);
```

**Other Costs:**

```sql
-- 17. Bank & Finance Charges
CREATE TABLE bank_finance_charges (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    bank_name TEXT NOT NULL,
    charge_type TEXT NOT NULL,
    transaction_count INTEGER,
    monthly_fee NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (monthly_fee > 0)
);

-- 18. Travel Expenses
CREATE TABLE travel_expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    travel_type TEXT NOT NULL,
    distance_miles NUMERIC(10,2),
    mileage_rate NUMERIC(6,4),
    purpose TEXT NOT NULL,
    total_cost NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (total_cost > 0)
);

-- 19. VAT Payments
CREATE TABLE vat_payments (
    id BIGSERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    quarter_ending DATE NOT NULL,
    vat_collected NUMERIC(12,2) NOT NULL,
    vat_paid NUMERIC(12,2) NOT NULL,
    net_vat_due NUMERIC(12,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (vat_collected >= 0),
    CHECK (vat_paid >= 0)
);

-- 20. Corporation Tax
CREATE TABLE corporation_tax (
    id BIGSERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    tax_year TEXT NOT NULL,
    taxable_profit NUMERIC(12,2) NOT NULL,
    tax_rate NUMERIC(5,2) NOT NULL,
    tax_due NUMERIC(12,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (tax_due >= 0)
);
```

---

## Migration Strategy

### Phase 1: Schema Creation

1. **Review existing Supabase tables** - Check for any conflicts with existing `clients` and `candidates` tables
2. **Create migration file** - Single SQL migration with all 20 tables
3. **Apply migration** - Use Supabase MCP to execute migration
4. **Verify schema** - Confirm all tables created successfully

### Phase 2: Data Import

1. **Create Python import script** - Use `supabase-py` library
2. **Parse CSV files** - Read each CSV and map to table structure
3. **Data validation** - Ensure data types match, handle nulls
4. **Batch insert** - Insert records in batches of 100-500
5. **Error handling** - Log any import failures for review

### Phase 3: Verification

1. **Record counts** - Verify all 858 records imported
2. **Data quality checks** - Sample random records across tables
3. **Query testing** - Test common queries (revenue by month, etc.)
4. **Performance testing** - Ensure indexes performing well

### Phase 4: Analytics Setup

1. **Create views** - Monthly revenue, cost summaries, P&L
2. **Setup RLS policies** - If needed for multi-user access
3. **Create API endpoints** - If needed for application access

---

## Implementation Scripts

### Script 1: Migration SQL

**File**: `sql/migrations/001_create_financial_tables.sql`

This will contain all 20 CREATE TABLE statements with proper constraints and indexes.

### Script 2: Python Import Script

**File**: `scripts/import_finance_data_to_supabase.py`

```python
# Key features:
# - Read all 20 CSV files
# - Connect to Supabase using environment variables
# - Batch insert with error handling
# - Progress tracking and logging
# - Validation checks
```

### Script 3: Verification Queries

**File**: `sql/verification/check_finance_data.sql`

```sql
-- Check record counts per table
-- Sample data quality checks
-- Foreign key validation
-- Date range checks
-- Amount validation (no negatives where not allowed)
```

---

## Data Mapping Notes

### Field Naming Conventions
- CSV uses snake_case (matches PostgreSQL convention)
- No transformation needed for field names
- Keep original ID fields (invoice_id, expense_id, payment_id) as unique identifiers

### Data Type Mappings
- All monetary values → `NUMERIC(10,2)` or `NUMERIC(12,2)` for large amounts
- Dates → `DATE`
- Timestamps → `TIMESTAMPTZ`
- Text fields → `TEXT` (PostgreSQL handles variable length efficiently)
- Booleans → `BOOLEAN`
- Percentages → `NUMERIC(5,2)` (allows values like 99.99)

### Special Considerations

1. **Client Linking**: The CSV files reference `client_id` (e.g., CLT-001, CLT-051). These should eventually link to the existing `clients` table, but we'll keep them as TEXT for now since the client IDs may not match exactly.

2. **Payment Status Values**: Standardize on 'Paid', 'Outstanding', 'Projected'

3. **Date Handling**: All dates in YYYY-MM-DD format, native CSV format

4. **Null Handling**: Some fields are nullable (payment_received_date, notes, etc.)

---

## Indexing Strategy

```sql
-- Revenue tables - query by date, client, status
CREATE INDEX idx_perm_placements_date ON permanent_placement_invoices(invoice_date);
CREATE INDEX idx_perm_placements_client ON permanent_placement_invoices(client_id);
CREATE INDEX idx_perm_placements_status ON permanent_placement_invoices(invoice_status);

CREATE INDEX idx_temp_invoices_date ON temporary_worker_invoices(invoice_date);
CREATE INDEX idx_temp_invoices_week ON temporary_worker_invoices(week_ending);

-- Cost tables - query by date, status
CREATE INDEX idx_salaries_date ON staff_salaries(payment_date);
CREATE INDEX idx_salaries_employee ON staff_salaries(employee_id);

-- Tax tables - query by period
CREATE INDEX idx_vat_quarter ON vat_payments(quarter_ending);
CREATE INDEX idx_corp_tax_year ON corporation_tax(tax_year);
```

---

## Post-Migration Analytics

### Key Queries to Enable

1. **Monthly Revenue by Service Line**
2. **Cost Analysis by Category**
3. **Profit & Loss Statement**
4. **Cash Flow Analysis** (invoices issued vs payments received)
5. **Client Revenue Analysis** (top clients, service mix)
6. **Temp Worker Margin Analysis**
7. **Year-over-Year Comparison**

### Potential Views

```sql
-- Monthly Revenue Summary
CREATE VIEW monthly_revenue_summary AS
SELECT
    DATE_TRUNC('month', invoice_date) as month,
    'Permanent Placements' as service_line,
    SUM(fee_amount) as revenue,
    COUNT(*) as transaction_count
FROM permanent_placement_invoices
GROUP BY DATE_TRUNC('month', invoice_date)
UNION ALL
SELECT
    DATE_TRUNC('month', invoice_date),
    'Temp Workers',
    SUM(gross_margin),
    COUNT(*)
FROM temporary_worker_invoices
GROUP BY DATE_TRUNC('month', invoice_date);
-- ... etc for other revenue sources
```

---

## Risk Mitigation

### Backup Strategy
1. Keep original CSV files as source of truth
2. Export Supabase data after migration
3. Compare record counts

### Rollback Plan
1. Drop all 20 tables if needed: `DROP TABLE IF EXISTS table_name CASCADE;`
2. Re-run migration from scratch
3. CSV files remain unchanged

### Data Quality Issues
1. **Duplicate IDs**: Check for duplicate invoice_id/expense_id before import
2. **Invalid Dates**: Validate date format during import
3. **Negative Amounts**: Validate amounts > 0 where required
4. **Missing Required Fields**: Validate no nulls in NOT NULL columns

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| **Schema Design** | Review, design, document | 2 hours (DONE) |
| **Migration Creation** | Write SQL migration file | 1 hour |
| **Schema Deployment** | Apply to Supabase, verify | 30 minutes |
| **Import Script** | Write Python import script | 2 hours |
| **Data Import** | Run import, handle errors | 1 hour |
| **Verification** | Check data quality, counts | 1 hour |
| **Analytics Setup** | Create views, test queries | 1 hour |
| **Documentation** | Finalize docs, handoff | 30 minutes |
| **TOTAL** | | ~9 hours |

---

## Success Criteria

✅ All 20 tables created in Supabase with correct schema
✅ All 858+ records successfully imported
✅ No data quality issues or validation errors
✅ Record counts match source CSV files exactly
✅ Sample queries return expected results
✅ Performance is acceptable (<100ms for simple queries)
✅ Documentation complete and clear

---

## Next Steps

1. **Review this plan** - Confirm approach with team/stakeholder
2. **Create migration SQL** - Write the DDL statements
3. **Test migration** - Apply to Supabase development environment
4. **Create import script** - Build Python script for data loading
5. **Execute migration** - Run against production Supabase project
6. **Verify & validate** - Comprehensive checks
7. **Enable analytics** - Create views and test queries

---

## Technical Requirements

### Python Environment
```bash
pip install supabase pandas python-dotenv
```

### Environment Variables
```bash
SUPABASE_URL=https://pauypyjqosrenuxveskn.supabase.co
SUPABASE_KEY=your-anon-key
```

### Supabase Project Details
- **Project ID**: pauypyjqosrenuxveskn
- **Region**: eu-north-1
- **PostgreSQL Version**: 15.8.1
- **Project Name**: n8n tables

---

*Plan created: 2025-10-22*
*Data source: ProActive People Finance Test Data*
*Total records: 858*
*Total tables: 20*
