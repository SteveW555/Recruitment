-- Migration 003: Align Database Tables with CSV Structure
-- Created: 2025-10-22
-- Purpose: Drop and recreate tables to match actual CSV column names

-- Drop all existing tables
DROP TABLE IF EXISTS permanent_placement_invoices CASCADE;
DROP TABLE IF EXISTS temporary_worker_invoices CASCADE;
DROP TABLE IF EXISTS training_service_invoices CASCADE;
DROP TABLE IF EXISTS wellbeing_service_invoices CASCADE;
DROP TABLE IF EXISTS assessment_service_invoices CASCADE;
DROP TABLE IF EXISTS contact_centre_consultancy_invoices CASCADE;
DROP TABLE IF EXISTS staff_salaries CASCADE;
DROP TABLE IF EXISTS temp_worker_payroll CASCADE;
DROP TABLE IF EXISTS office_rent_facilities CASCADE;
DROP TABLE IF EXISTS technology_subscriptions CASCADE;
DROP TABLE IF EXISTS job_board_advertising CASCADE;
DROP TABLE IF EXISTS insurance_premiums CASCADE;
DROP TABLE IF EXISTS compliance_costs CASCADE;
DROP TABLE IF EXISTS marketing_costs CASCADE;
DROP TABLE IF EXISTS professional_services CASCADE;
DROP TABLE IF EXISTS utilities_expenses CASCADE;
DROP TABLE IF EXISTS bank_finance_charges CASCADE;
DROP TABLE IF EXISTS travel_expenses CASCADE;
DROP TABLE IF EXISTS vat_payments CASCADE;
DROP TABLE IF EXISTS corporation_tax CASCADE;

-- ====================================
-- REVENUE TABLES (6 tables)
-- ====================================

-- 1. Permanent Placement Invoices
-- CSV: invoice_id,invoice_date,client_id,client_name,candidate_name,job_title,annual_salary,fee_percentage,fee_amount,invoice_status,payment_due_date,payment_received_date,payment_method,notes
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Temporary Worker Invoices
-- CSV: invoice_id,invoice_date,client_id,client_name,temp_worker_name,week_ending,hours_worked,hourly_pay_rate,total_pay,markup_percentage,hourly_charge_rate,total_charge,gross_margin,invoice_status,payment_due_date,payment_received_date
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Training Service Invoices
-- CSV: invoice_id,invoice_date,client_id,client_name,service_type,program_name,trainer,duration_days,number_participants,price_per_person,total_amount,invoice_status,payment_due_date,payment_received_date,notes
CREATE TABLE training_service_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    service_type TEXT NOT NULL,
    program_name TEXT NOT NULL,
    trainer TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    number_participants INTEGER NOT NULL,
    price_per_person NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Wellbeing Service Invoices
-- CSV: invoice_id,invoice_date,client_id,client_name,service_type,sessions_included,total_amount,invoice_status,payment_due_date,payment_received_date,therapist,notes
CREATE TABLE wellbeing_service_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT NOT NULL,
    service_type TEXT NOT NULL,
    sessions_included INTEGER NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    therapist TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Assessment Service Invoices
-- CSV: invoice_id,invoice_date,client_id,assessment_type,number_of_candidates,price_per_assessment,total_amount,invoice_status,payment_due_date,payment_received_date
CREATE TABLE assessment_service_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    number_of_candidates INTEGER NOT NULL,
    price_per_assessment NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Contact Centre Consultancy Invoices
-- CSV: invoice_id,invoice_date,client_id,project_type,project_start_date,project_duration_days,total_amount,invoice_status,payment_due_date,payment_received_date,consultant
CREATE TABLE contact_centre_consultancy_invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    client_id TEXT NOT NULL,
    project_type TEXT NOT NULL,
    project_start_date DATE NOT NULL,
    project_duration_days INTEGER NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,
    invoice_status TEXT NOT NULL,
    payment_due_date DATE NOT NULL,
    payment_received_date DATE,
    consultant TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ====================================
-- COST TABLES (14 tables)
-- ====================================

-- 7. Staff Salaries
-- CSV: payment_id,payment_date,employee_id,employee_name,annual_salary,monthly_gross,employer_ni,employer_pension,bonus,total_cost,payment_method,status
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
    bonus NUMERIC(10,2),
    total_cost NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Temp Worker Payroll
-- CSV: payroll_id,week_ending,worker_id,worker_name,hours_worked,hourly_rate,gross_pay,paye_tax,employee_ni,pension_employee,net_pay,employer_ni,pension_employer,total_cost,payment_date,status
CREATE TABLE temp_worker_payroll (
    id BIGSERIAL PRIMARY KEY,
    payroll_id TEXT UNIQUE NOT NULL,
    week_ending DATE NOT NULL,
    worker_id TEXT NOT NULL,
    worker_name TEXT NOT NULL,
    hours_worked NUMERIC(6,2) NOT NULL,
    hourly_rate NUMERIC(8,2) NOT NULL,
    gross_pay NUMERIC(10,2) NOT NULL,
    paye_tax NUMERIC(10,2) NOT NULL,
    employee_ni NUMERIC(10,2) NOT NULL,
    pension_employee NUMERIC(10,2),
    net_pay NUMERIC(10,2) NOT NULL,
    employer_ni NUMERIC(10,2) NOT NULL,
    pension_employer NUMERIC(10,2),
    total_cost NUMERIC(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Office Rent & Facilities
-- CSV: expense_id,expense_date,office_location,expense_type,square_feet,price_per_sqft,amount,payment_status,payment_method,notes
CREATE TABLE office_rent_facilities (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    office_location TEXT NOT NULL,
    expense_type TEXT NOT NULL,
    square_feet INTEGER,
    price_per_sqft NUMERIC(8,2),
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. Technology Subscriptions
-- CSV: expense_id,expense_date,service_name,category,billing_cycle,amount,payment_status,payment_method,auto_renew
CREATE TABLE technology_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    service_name TEXT NOT NULL,
    category TEXT NOT NULL,
    billing_cycle TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    auto_renew TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. Job Board Advertising
-- CSV: expense_id,expense_date,job_board,service_type,amount,jobs_posted,payment_status,payment_method
CREATE TABLE job_board_advertising (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    job_board TEXT NOT NULL,
    service_type TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    jobs_posted INTEGER,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. Insurance Premiums
-- CSV: expense_id,expense_date,policy_type,annual_premium,coverage_period_months,billing_frequency,payment_status,renewal_date,payment_method
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. Compliance Costs
-- CSV: expense_id,expense_date,compliance_type,amount,candidate_or_staff,payment_status,payment_method
CREATE TABLE compliance_costs (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    compliance_type TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    candidate_or_staff TEXT,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 14. Marketing Costs
-- CSV: expense_id,expense_date,marketing_activity,category,amount,frequency,payment_status,payment_method
CREATE TABLE marketing_costs (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    marketing_activity TEXT NOT NULL,
    category TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    frequency TEXT,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 15. Professional Services
-- CSV: expense_id,expense_date,service_name,category,amount,frequency,payment_status,payment_method
CREATE TABLE professional_services (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    service_name TEXT NOT NULL,
    category TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    frequency TEXT,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 16. Utilities
-- CSV: expense_id,expense_date,utility_type,location,amount,payment_status,payment_method
CREATE TABLE utilities_expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    utility_type TEXT NOT NULL,
    location TEXT,
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 17. Bank & Finance Charges
-- CSV: expense_id,expense_date,fee_type,amount,payment_status,bank
CREATE TABLE bank_finance_charges (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    fee_type TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    bank TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 18. Travel Expenses
-- CSV: expense_id,expense_date,expense_type,employee_id,amount,purpose,reimbursement_status,payment_method
CREATE TABLE travel_expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    expense_type TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    purpose TEXT NOT NULL,
    reimbursement_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 19. VAT Payments
-- CSV: payment_id,payment_date,quarter_ending,vat_collected,vat_paid,net_vat_due,payment_status,payment_method
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 20. Corporation Tax
-- CSV: payment_id,tax_year,payment_date,taxable_profit,tax_rate,tax_due,payment_status,payment_method
CREATE TABLE corporation_tax (
    id BIGSERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    tax_year TEXT NOT NULL,
    payment_date DATE NOT NULL,
    taxable_profit NUMERIC(12,2) NOT NULL,
    tax_rate TEXT NOT NULL,  -- Store as TEXT to handle "19%" format
    tax_due NUMERIC(12,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ====================================
-- INDEXES FOR PERFORMANCE
-- ====================================

CREATE INDEX idx_perm_placements_date ON permanent_placement_invoices(invoice_date);
CREATE INDEX idx_perm_placements_client ON permanent_placement_invoices(client_id);
CREATE INDEX idx_perm_placements_status ON permanent_placement_invoices(invoice_status);

CREATE INDEX idx_temp_invoices_date ON temporary_worker_invoices(invoice_date);
CREATE INDEX idx_temp_invoices_week ON temporary_worker_invoices(week_ending);
CREATE INDEX idx_temp_invoices_client ON temporary_worker_invoices(client_id);

CREATE INDEX idx_training_date ON training_service_invoices(invoice_date);
CREATE INDEX idx_training_client ON training_service_invoices(client_id);

CREATE INDEX idx_wellbeing_date ON wellbeing_service_invoices(invoice_date);
CREATE INDEX idx_wellbeing_client ON wellbeing_service_invoices(client_id);

CREATE INDEX idx_assessment_date ON assessment_service_invoices(invoice_date);
CREATE INDEX idx_assessment_client ON assessment_service_invoices(client_id);

CREATE INDEX idx_consultancy_date ON contact_centre_consultancy_invoices(invoice_date);
CREATE INDEX idx_consultancy_client ON contact_centre_consultancy_invoices(client_id);

CREATE INDEX idx_salaries_date ON staff_salaries(payment_date);
CREATE INDEX idx_salaries_employee ON staff_salaries(employee_id);

CREATE INDEX idx_payroll_date ON temp_worker_payroll(payment_date);
CREATE INDEX idx_payroll_week ON temp_worker_payroll(week_ending);

CREATE INDEX idx_office_date ON office_rent_facilities(expense_date);

CREATE INDEX idx_tech_date ON technology_subscriptions(expense_date);

CREATE INDEX idx_jobboard_date ON job_board_advertising(expense_date);

CREATE INDEX idx_insurance_date ON insurance_premiums(expense_date);
CREATE INDEX idx_insurance_renewal ON insurance_premiums(renewal_date);

CREATE INDEX idx_compliance_date ON compliance_costs(expense_date);

CREATE INDEX idx_marketing_date ON marketing_costs(expense_date);

CREATE INDEX idx_profservices_date ON professional_services(expense_date);

CREATE INDEX idx_utilities_date ON utilities_expenses(expense_date);

CREATE INDEX idx_bank_date ON bank_finance_charges(expense_date);

CREATE INDEX idx_travel_date ON travel_expenses(expense_date);
CREATE INDEX idx_travel_employee ON travel_expenses(employee_id);

CREATE INDEX idx_vat_quarter ON vat_payments(quarter_ending);

CREATE INDEX idx_corp_tax_year ON corporation_tax(tax_year);
