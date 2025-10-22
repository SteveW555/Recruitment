-- 16. Utilities
-- CSV: expense_id,expense_date,utility_type,location,amount,payment_status,payment_method
CREATE TABLE utilities_expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    utility_type TEXT NOT NULL,
    location TEXT,
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

