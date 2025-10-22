-- 13. Compliance Costs
-- CSV: expense_id,expense_date,compliance_type,amount,candidate_or_staff,payment_status,payment_method
CREATE TABLE compliance_costs (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    compliance_type TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    candidate_or_staff TEXT,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

