-- 17. Bank & Finance Charges
-- CSV: expense_id,expense_date,fee_type,amount,payment_status,bank
CREATE TABLE bank_finance_charges (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    fee_type TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    bank TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

