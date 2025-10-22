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

