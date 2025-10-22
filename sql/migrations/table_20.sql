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
