-- 14. Marketing Costs
-- CSV: expense_id,expense_date,marketing_activity,category,amount,frequency,payment_status,payment_method
CREATE TABLE marketing_costs (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    marketing_activity TEXT NOT NULL,
    category TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    frequency TEXT,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

