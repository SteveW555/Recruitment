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

