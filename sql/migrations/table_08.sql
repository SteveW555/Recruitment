-- 8. Temp Worker Payroll
-- CSV: payroll_id,week_ending,worker_id,worker_name,hours_worked,hourly_rate,gross_pay,paye_tax,employee_ni,pension_employee,net_pay,employer_ni,pension_employer,total_cost,payment_date,status
CREATE TABLE temp_worker_payroll (
    id BIGSERIAL PRIMARY KEY,
    payroll_id TEXT UNIQUE NOT NULL,
    week_ending DATE NOT NULL,
    worker_id TEXT NOT NULL,
    worker_name TEXT NOT NULL,
    hours_worked NUMERIC(6,2) NOT NULL,
    hourly_rate NUMERIC(8,2) NOT NULL,
    gross_pay NUMERIC(10,2) NOT NULL,
    paye_tax NUMERIC(10,2) NOT NULL,
    employee_ni NUMERIC(10,2) NOT NULL,
    pension_employee NUMERIC(10,2),
    net_pay NUMERIC(10,2) NOT NULL,
    employer_ni NUMERIC(10,2) NOT NULL,
    pension_employer NUMERIC(10,2),
    total_cost NUMERIC(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

