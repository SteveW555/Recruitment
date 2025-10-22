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

