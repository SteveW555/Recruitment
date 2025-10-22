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

