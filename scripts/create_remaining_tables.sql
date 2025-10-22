-- All tables to be created via apply_migration

-- Table 2
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

-- Table 3
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

-- Table 4
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

-- Table 5
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

-- Table 6
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

-- Table 7
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

-- Table 8
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

-- Table 9
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

-- Table 10
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

-- Table 11
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

-- Table 12
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

-- Table 13
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

-- Table 14
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

-- Table 15
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

-- Table 16
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

-- Table 17
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

-- Table 18
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

-- Table 19
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

-- Table 20
CREATE TABLE corporation_tax (
    id BIGSERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    tax_year TEXT NOT NULL,
    payment_date DATE NOT NULL,
    taxable_profit NUMERIC(12,2) NOT NULL,
    tax_rate TEXT NOT NULL,
    tax_due NUMERIC(12,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
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