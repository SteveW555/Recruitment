-- 7. Staff Salaries
-- CSV: payment_id,payment_date,employee_id,employee_name,annual_salary,monthly_gross,employer_ni,employer_pension,bonus,total_cost,payment_method,status
CREATE TABLE staff_salaries (
    id BIGSERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    annual_salary NUMERIC(10,2) NOT NULL,
    monthly_gross NUMERIC(10,2) NOT NULL,
    employer_ni NUMERIC(10,2) NOT NULL,
    employer_pension NUMERIC(10,2) NOT NULL,
    bonus NUMERIC(10,2),
    total_cost NUMERIC(10,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

