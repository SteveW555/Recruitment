-- ProActive People - Financial Tables Migration
-- Created: 2025-10-22
-- Purpose: Create 20 financial transaction tables for finance test data
-- Project: Recruitment (njjolzejmzqpridlgplb)

-- ====================================
-- REVENUE TABLES (6 tables)
-- ====================================

-- 1. Permanent Placement Invoices
CREATE TABLE IF NOT EXISTS permanent_placement_invoices (
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
CREATE TABLE IF NOT EXISTS temporary_worker_invoices (
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
CREATE TABLE IF NOT EXISTS training_service_invoices (
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
CREATE TABLE IF NOT EXISTS wellbeing_service_invoices (
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
CREATE TABLE IF NOT EXISTS assessment_service_invoices (
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
CREATE TABLE IF NOT EXISTS contact_centre_consultancy_invoices (
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

-- ====================================
-- COST TABLES (14 tables)
-- ====================================

-- 7. Staff Salaries
CREATE TABLE IF NOT EXISTS staff_salaries (
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
CREATE TABLE IF NOT EXISTS temp_worker_payroll (
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

-- 9. Office Rent & Facilities
CREATE TABLE IF NOT EXISTS office_rent_facilities (
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

-- 10. Technology Subscriptions
CREATE TABLE IF NOT EXISTS technology_subscriptions (
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
CREATE TABLE IF NOT EXISTS job_board_advertising (
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

-- 12. Insurance Premiums
CREATE TABLE IF NOT EXISTS insurance_premiums (
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
CREATE TABLE IF NOT EXISTS compliance_costs (
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
CREATE TABLE IF NOT EXISTS marketing_costs (
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
CREATE TABLE IF NOT EXISTS professional_services (
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

-- 16. Utilities
CREATE TABLE IF NOT EXISTS utilities_expenses (
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

-- 17. Bank & Finance Charges
CREATE TABLE IF NOT EXISTS bank_finance_charges (
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
CREATE TABLE IF NOT EXISTS travel_expenses (
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
CREATE TABLE IF NOT EXISTS vat_payments (
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
CREATE TABLE IF NOT EXISTS corporation_tax (
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

-- ====================================
-- INDEXES FOR PERFORMANCE
-- ====================================

-- Revenue tables indexes
CREATE INDEX IF NOT EXISTS idx_perm_placements_date ON permanent_placement_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_perm_placements_client ON permanent_placement_invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_perm_placements_status ON permanent_placement_invoices(invoice_status);

CREATE INDEX IF NOT EXISTS idx_temp_invoices_date ON temporary_worker_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_temp_invoices_week ON temporary_worker_invoices(week_ending);
CREATE INDEX IF NOT EXISTS idx_temp_invoices_client ON temporary_worker_invoices(client_id);

CREATE INDEX IF NOT EXISTS idx_training_date ON training_service_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_training_client ON training_service_invoices(client_id);

CREATE INDEX IF NOT EXISTS idx_wellbeing_date ON wellbeing_service_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_wellbeing_client ON wellbeing_service_invoices(client_id);

CREATE INDEX IF NOT EXISTS idx_assessment_date ON assessment_service_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_assessment_client ON assessment_service_invoices(client_id);

CREATE INDEX IF NOT EXISTS idx_consultancy_date ON contact_centre_consultancy_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_consultancy_client ON contact_centre_consultancy_invoices(client_id);

-- Cost tables indexes
CREATE INDEX IF NOT EXISTS idx_salaries_date ON staff_salaries(payment_date);
CREATE INDEX IF NOT EXISTS idx_salaries_employee ON staff_salaries(employee_id);

CREATE INDEX IF NOT EXISTS idx_payroll_date ON temp_worker_payroll(payment_date);
CREATE INDEX IF NOT EXISTS idx_payroll_week ON temp_worker_payroll(week_ending);

CREATE INDEX IF NOT EXISTS idx_office_date ON office_rent_facilities(expense_date);

CREATE INDEX IF NOT EXISTS idx_tech_date ON technology_subscriptions(expense_date);
CREATE INDEX IF NOT EXISTS idx_tech_renewal ON technology_subscriptions(renewal_date);

CREATE INDEX IF NOT EXISTS idx_jobboard_date ON job_board_advertising(expense_date);

CREATE INDEX IF NOT EXISTS idx_insurance_date ON insurance_premiums(expense_date);
CREATE INDEX IF NOT EXISTS idx_insurance_renewal ON insurance_premiums(renewal_date);

CREATE INDEX IF NOT EXISTS idx_compliance_date ON compliance_costs(expense_date);

CREATE INDEX IF NOT EXISTS idx_marketing_date ON marketing_costs(expense_date);

CREATE INDEX IF NOT EXISTS idx_profservices_date ON professional_services(expense_date);

CREATE INDEX IF NOT EXISTS idx_utilities_date ON utilities_expenses(expense_date);

CREATE INDEX IF NOT EXISTS idx_bank_date ON bank_finance_charges(expense_date);

CREATE INDEX IF NOT EXISTS idx_travel_date ON travel_expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_travel_employee ON travel_expenses(employee_id);

CREATE INDEX IF NOT EXISTS idx_vat_quarter ON vat_payments(quarter_ending);

CREATE INDEX IF NOT EXISTS idx_corp_tax_year ON corporation_tax(tax_year);

-- ====================================
-- COMMENTS FOR DOCUMENTATION
-- ====================================

COMMENT ON TABLE permanent_placement_invoices IS 'Revenue from permanent recruitment placements';
COMMENT ON TABLE temporary_worker_invoices IS 'Revenue from temporary worker placements';
COMMENT ON TABLE training_service_invoices IS 'Revenue from training services provided';
COMMENT ON TABLE wellbeing_service_invoices IS 'Revenue from wellbeing services provided';
COMMENT ON TABLE assessment_service_invoices IS 'Revenue from candidate assessment services';
COMMENT ON TABLE contact_centre_consultancy_invoices IS 'Revenue from contact centre consultancy projects';

COMMENT ON TABLE staff_salaries IS 'Permanent staff salary costs';
COMMENT ON TABLE temp_worker_payroll IS 'Temporary worker payroll costs';
COMMENT ON TABLE office_rent_facilities IS 'Office rent and facilities costs';
COMMENT ON TABLE technology_subscriptions IS 'Technology and software subscription costs';
COMMENT ON TABLE job_board_advertising IS 'Job board and advertising costs';
COMMENT ON TABLE insurance_premiums IS 'Business insurance premium costs';
COMMENT ON TABLE compliance_costs IS 'Compliance and regulatory costs';
COMMENT ON TABLE marketing_costs IS 'Marketing and promotional costs';
COMMENT ON TABLE professional_services IS 'External professional services costs';
COMMENT ON TABLE utilities_expenses IS 'Utilities and operational costs';
COMMENT ON TABLE bank_finance_charges IS 'Bank and finance charges';
COMMENT ON TABLE travel_expenses IS 'Employee travel and expenses';
COMMENT ON TABLE vat_payments IS 'VAT payments to HMRC';
COMMENT ON TABLE corporation_tax IS 'Corporation tax payments';
