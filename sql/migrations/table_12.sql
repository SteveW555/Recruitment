-- 12. Insurance Premiums
-- CSV: expense_id,expense_date,policy_type,annual_premium,coverage_period_months,billing_frequency,payment_status,renewal_date,payment_method
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

