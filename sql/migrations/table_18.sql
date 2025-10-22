-- 18. Travel Expenses
-- CSV: expense_id,expense_date,expense_type,employee_id,amount,purpose,reimbursement_status,payment_method
CREATE TABLE travel_expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    expense_type TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    purpose TEXT NOT NULL,
    reimbursement_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

