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

