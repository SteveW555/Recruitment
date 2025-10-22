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

