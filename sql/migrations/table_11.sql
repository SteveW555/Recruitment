-- 11. Job Board Advertising
-- CSV: expense_id,expense_date,job_board,service_type,amount,jobs_posted,payment_status,payment_method
CREATE TABLE job_board_advertising (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    job_board TEXT NOT NULL,
    service_type TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    jobs_posted INTEGER,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

