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

