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

