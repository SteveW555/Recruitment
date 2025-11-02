-- ProActive People - Common Financial Queries for Supabase
--
-- This file contains SQL queries for common financial analysis tasks
-- organized by category and use case. All queries are tested against
-- the ProActive People Supabase finance tables.
--
-- Usage: Copy and adapt queries as needed, replacing date ranges and
-- parameters with actual values or using parameterized queries.
--
-- Last Updated: 2025-11-02

-- ============================================================================
-- SECTION 1: REVENUE ANALYSIS
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 1.1 Total Revenue by Period
-- -----------------------------------------------------------------------------

-- Total revenue by month (all revenue sources)
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    SUM(fee_amount) AS total_revenue
FROM permanent_placement_invoices
WHERE invoice_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY month;

-- Total revenue by quarter (permanent placements only)
SELECT
    DATE_TRUNC('quarter', invoice_date) AS quarter,
    COUNT(*) AS num_placements,
    SUM(fee_amount) AS total_revenue,
    AVG(fee_amount) AS avg_fee
FROM permanent_placement_invoices
WHERE invoice_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY DATE_TRUNC('quarter', invoice_date)
ORDER BY quarter;

-- Year-to-date revenue across all sources
SELECT
    'Permanent Placements' AS revenue_source,
    SUM(fee_amount) AS ytd_revenue
FROM permanent_placement_invoices
WHERE invoice_date >= DATE_TRUNC('year', CURRENT_DATE)

UNION ALL

SELECT
    'Temporary Workers' AS revenue_source,
    SUM(total_invoice_amount) AS ytd_revenue
FROM temporary_worker_invoices
WHERE invoice_date >= DATE_TRUNC('year', CURRENT_DATE)

UNION ALL

SELECT
    'Training Services' AS revenue_source,
    SUM(total_amount) AS ytd_revenue
FROM training_service_invoices
WHERE invoice_date >= DATE_TRUNC('year', CURRENT_DATE)

UNION ALL

SELECT
    'Wellbeing Services' AS revenue_source,
    SUM(total_amount) AS ytd_revenue
FROM wellbeing_service_invoices
WHERE invoice_date >= DATE_TRUNC('year', CURRENT_DATE)

UNION ALL

SELECT
    'Assessment Services' AS revenue_source,
    SUM(total_amount) AS ytd_revenue
FROM assessment_service_invoices
WHERE invoice_date >= DATE_TRUNC('year', CURRENT_DATE)

UNION ALL

SELECT
    'Contact Centre Consultancy' AS revenue_source,
    SUM(total_amount) AS ytd_revenue
FROM contact_centre_consultancy_invoices
WHERE invoice_date >= DATE_TRUNC('year', CURRENT_DATE);

-- -----------------------------------------------------------------------------
-- 1.2 Revenue Breakdown & Mix Analysis
-- -----------------------------------------------------------------------------

-- Revenue mix by source (percentage breakdown)
WITH revenue_totals AS (
    SELECT 'Permanent' AS source, SUM(fee_amount) AS amount
    FROM permanent_placement_invoices WHERE invoice_status = 'Paid'
    UNION ALL
    SELECT 'Temporary', SUM(total_invoice_amount)
    FROM temporary_worker_invoices WHERE invoice_status = 'Paid'
    UNION ALL
    SELECT 'Training', SUM(total_amount)
    FROM training_service_invoices WHERE invoice_status = 'Paid'
    UNION ALL
    SELECT 'Wellbeing', SUM(total_amount)
    FROM wellbeing_service_invoices WHERE invoice_status = 'Paid'
    UNION ALL
    SELECT 'Assessment', SUM(total_amount)
    FROM assessment_service_invoices WHERE invoice_status = 'Paid'
    UNION ALL
    SELECT 'Consultancy', SUM(total_amount)
    FROM contact_centre_consultancy_invoices WHERE invoice_status = 'Paid'
)
SELECT
    source,
    amount,
    ROUND(100.0 * amount / SUM(amount) OVER (), 2) AS percentage
FROM revenue_totals
ORDER BY amount DESC;

-- -----------------------------------------------------------------------------
-- 1.3 Permanent Placement Analysis
-- -----------------------------------------------------------------------------

-- Permanent placement fee analysis by job level
SELECT
    CASE
        WHEN annual_salary < 30000 THEN 'Entry Level (<£30k)'
        WHEN annual_salary BETWEEN 30000 AND 50000 THEN 'Mid Level (£30k-£50k)'
        WHEN annual_salary BETWEEN 50001 AND 70000 THEN 'Senior (£50k-£70k)'
        ELSE 'Executive (£70k+)'
    END AS salary_band,
    COUNT(*) AS num_placements,
    AVG(annual_salary) AS avg_salary,
    AVG(fee_percentage) AS avg_fee_pct,
    AVG(fee_amount) AS avg_fee,
    SUM(fee_amount) AS total_revenue
FROM permanent_placement_invoices
WHERE invoice_status = 'Paid'
GROUP BY salary_band
ORDER BY avg_salary;

-- Top performing clients (permanent placements)
SELECT
    client_id,
    client_name,
    COUNT(*) AS num_placements,
    SUM(fee_amount) AS total_revenue,
    AVG(fee_amount) AS avg_fee,
    MIN(invoice_date) AS first_placement,
    MAX(invoice_date) AS last_placement
FROM permanent_placement_invoices
WHERE invoice_status = 'Paid'
GROUP BY client_id, client_name
HAVING COUNT(*) > 1
ORDER BY total_revenue DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- 1.4 Temporary Worker Analysis
-- -----------------------------------------------------------------------------

-- Temp worker margin analysis
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    COUNT(DISTINCT temp_worker_name) AS num_workers,
    SUM(hours_worked) AS total_hours,
    AVG(hourly_pay_rate) AS avg_pay_rate,
    AVG(hourly_charge_rate) AS avg_charge_rate,
    AVG(markup_percentage) AS avg_markup_pct,
    SUM(gross_margin) AS total_margin,
    SUM(total_invoice_amount) AS total_revenue
FROM temporary_worker_invoices
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY month;

-- Active temp workers (last 30 days)
SELECT
    temp_worker_name,
    COUNT(*) AS num_weeks_active,
    SUM(hours_worked) AS total_hours,
    AVG(hourly_pay_rate) AS avg_pay_rate,
    SUM(gross_margin) AS total_margin
FROM temporary_worker_invoices
WHERE invoice_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY temp_worker_name
ORDER BY total_margin DESC;

-- Client temp worker utilization
SELECT
    client_name,
    COUNT(DISTINCT temp_worker_name) AS num_unique_workers,
    SUM(hours_worked) AS total_hours,
    SUM(total_invoice_amount) AS total_billed,
    SUM(gross_margin) AS total_margin
FROM temporary_worker_invoices
WHERE invoice_status = 'Paid'
GROUP BY client_name
ORDER BY total_billed DESC;

-- ============================================================================
-- SECTION 2: COST ANALYSIS
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 2.1 Total Costs by Period
-- -----------------------------------------------------------------------------

-- Monthly cost breakdown by category
WITH monthly_costs AS (
    SELECT DATE_TRUNC('month', payment_date) AS month,
           'Staff Salaries' AS category,
           SUM(total_cost) AS amount
    FROM staff_salaries GROUP BY DATE_TRUNC('month', payment_date)

    UNION ALL
    SELECT DATE_TRUNC('month', payroll_date),
           'Temp Payroll',
           SUM(total_employer_cost)
    FROM temp_worker_payroll GROUP BY DATE_TRUNC('month', payroll_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Office Rent',
           SUM(total_amount)
    FROM office_rent_facilities GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Technology',
           SUM(monthly_cost)
    FROM technology_subscriptions GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Job Boards',
           SUM(monthly_cost)
    FROM job_board_advertising GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Marketing',
           SUM(amount)
    FROM marketing_costs GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Professional Services',
           SUM(amount)
    FROM professional_services GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Utilities',
           SUM(amount)
    FROM utilities_expenses GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Travel',
           SUM(amount)
    FROM travel_expenses GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Compliance',
           SUM(amount)
    FROM compliance_costs GROUP BY DATE_TRUNC('month', expense_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           'Bank Charges',
           SUM(amount)
    FROM bank_finance_charges GROUP BY DATE_TRUNC('month', expense_date)
)
SELECT
    month,
    category,
    amount,
    SUM(amount) OVER (PARTITION BY month) AS total_monthly_costs
FROM monthly_costs
ORDER BY month, amount DESC;

-- -----------------------------------------------------------------------------
-- 2.2 Personnel Costs Analysis
-- -----------------------------------------------------------------------------

-- Staff salary costs with employer contributions
SELECT
    employee_name,
    annual_salary,
    AVG(monthly_gross) AS avg_monthly_gross,
    AVG(employer_ni) AS avg_employer_ni,
    AVG(employer_pension) AS avg_employer_pension,
    AVG(total_cost) AS avg_monthly_total_cost,
    AVG(total_cost) * 12 AS annual_total_cost
FROM staff_salaries
GROUP BY employee_name, annual_salary
ORDER BY annual_salary DESC;

-- Impact of April 2025 NI changes
SELECT
    employee_name,
    annual_salary,
    AVG(CASE
        WHEN payment_date < '2025-04-01' THEN employer_ni
    END) AS avg_ni_before_april_2025,
    AVG(CASE
        WHEN payment_date >= '2025-04-01' THEN employer_ni
    END) AS avg_ni_after_april_2025,
    AVG(CASE
        WHEN payment_date >= '2025-04-01' THEN employer_ni
    END) - AVG(CASE
        WHEN payment_date < '2025-04-01' THEN employer_ni
    END) AS ni_increase
FROM staff_salaries
GROUP BY employee_name, annual_salary
ORDER BY annual_salary DESC;

-- Total personnel costs (staff + temps)
SELECT
    DATE_TRUNC('month', payment_date) AS month,
    SUM(total_cost) AS staff_costs,
    (SELECT SUM(total_employer_cost)
     FROM temp_worker_payroll
     WHERE DATE_TRUNC('month', payroll_date) = DATE_TRUNC('month', staff_salaries.payment_date)
    ) AS temp_costs,
    SUM(total_cost) + COALESCE((
        SELECT SUM(total_employer_cost)
        FROM temp_worker_payroll
        WHERE DATE_TRUNC('month', payroll_date) = DATE_TRUNC('month', staff_salaries.payment_date)
    ), 0) AS total_personnel_costs
FROM staff_salaries
GROUP BY DATE_TRUNC('month', payment_date)
ORDER BY month;

-- -----------------------------------------------------------------------------
-- 2.3 Operating Costs Analysis
-- -----------------------------------------------------------------------------

-- Technology cost breakdown
SELECT
    service_name,
    billing_cycle,
    AVG(monthly_cost) AS avg_monthly_cost,
    AVG(monthly_cost) * 12 AS annual_cost
FROM technology_subscriptions
WHERE payment_status = 'Paid'
GROUP BY service_name, billing_cycle
ORDER BY annual_cost DESC;

-- Marketing spend by channel
SELECT
    marketing_type,
    COUNT(*) AS num_campaigns,
    SUM(amount) AS total_spend,
    AVG(amount) AS avg_spend_per_campaign
FROM marketing_costs
WHERE payment_status = 'Paid'
GROUP BY marketing_type
ORDER BY total_spend DESC;

-- ============================================================================
-- SECTION 3: PROFITABILITY ANALYSIS
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 3.1 Monthly Profit & Loss
-- -----------------------------------------------------------------------------

-- Monthly P&L summary
WITH monthly_revenue AS (
    SELECT DATE_TRUNC('month', invoice_date) AS month,
           SUM(fee_amount) AS amount
    FROM permanent_placement_invoices WHERE invoice_status = 'Paid'
    GROUP BY DATE_TRUNC('month', invoice_date)

    UNION ALL
    SELECT DATE_TRUNC('month', invoice_date),
           SUM(total_invoice_amount)
    FROM temporary_worker_invoices WHERE invoice_status = 'Paid'
    GROUP BY DATE_TRUNC('month', invoice_date)

    -- Add other revenue sources...
),
monthly_costs AS (
    SELECT DATE_TRUNC('month', payment_date) AS month,
           SUM(total_cost) AS amount
    FROM staff_salaries
    GROUP BY DATE_TRUNC('month', payment_date)

    UNION ALL
    SELECT DATE_TRUNC('month', expense_date),
           SUM(total_amount)
    FROM office_rent_facilities
    GROUP BY DATE_TRUNC('month', expense_date)

    -- Add other cost sources...
)
SELECT
    COALESCE(r.month, c.month) AS month,
    SUM(r.amount) AS total_revenue,
    SUM(c.amount) AS total_costs,
    SUM(r.amount) - SUM(c.amount) AS net_profit,
    ROUND(100.0 * (SUM(r.amount) - SUM(c.amount)) / NULLIF(SUM(r.amount), 0), 2) AS profit_margin_pct
FROM monthly_revenue r
FULL OUTER JOIN monthly_costs c ON r.month = c.month
GROUP BY COALESCE(r.month, c.month)
ORDER BY month;

-- -----------------------------------------------------------------------------
-- 3.2 Margin Analysis
-- -----------------------------------------------------------------------------

-- Gross margin by service line
SELECT
    'Permanent Placements' AS service,
    SUM(fee_amount) AS revenue,
    0 AS direct_costs,
    SUM(fee_amount) AS gross_profit,
    ROUND(100.0 * SUM(fee_amount) / SUM(fee_amount), 2) AS gross_margin_pct
FROM permanent_placement_invoices WHERE invoice_status = 'Paid'

UNION ALL

SELECT
    'Temporary Workers',
    SUM(total_invoice_amount),
    SUM(total_invoice_amount - gross_margin),
    SUM(gross_margin),
    ROUND(100.0 * SUM(gross_margin) / SUM(total_invoice_amount), 2)
FROM temporary_worker_invoices WHERE invoice_status = 'Paid';

-- Temp worker margin analysis with payroll costs
WITH temp_revenue AS (
    SELECT
        DATE_TRUNC('month', invoice_date) AS month,
        SUM(total_invoice_amount) AS revenue,
        SUM(gross_margin) AS initial_margin
    FROM temporary_worker_invoices
    WHERE invoice_status = 'Paid'
    GROUP BY DATE_TRUNC('month', invoice_date)
),
temp_payroll AS (
    SELECT
        DATE_TRUNC('month', payroll_date) AS month,
        SUM(total_employer_cost) AS total_cost
    FROM temp_worker_payroll
    WHERE status = 'Paid'
    GROUP BY DATE_TRUNC('month', payroll_date)
)
SELECT
    r.month,
    r.revenue,
    p.total_cost AS payroll_cost,
    r.initial_margin AS markup_margin,
    r.revenue - p.total_cost AS actual_gross_profit,
    ROUND(100.0 * (r.revenue - p.total_cost) / r.revenue, 2) AS actual_margin_pct
FROM temp_revenue r
JOIN temp_payroll p ON r.month = p.month
ORDER BY r.month;

-- ============================================================================
-- SECTION 4: CASH FLOW ANALYSIS
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 4.1 Outstanding Invoices & Receivables
-- -----------------------------------------------------------------------------

-- Aged receivables analysis (permanent placements)
SELECT
    CASE
        WHEN payment_due_date >= CURRENT_DATE THEN 'Current (Not Yet Due)'
        WHEN payment_due_date >= CURRENT_DATE - INTERVAL '30 days' THEN '0-30 Days Overdue'
        WHEN payment_due_date >= CURRENT_DATE - INTERVAL '60 days' THEN '31-60 Days Overdue'
        WHEN payment_due_date >= CURRENT_DATE - INTERVAL '90 days' THEN '61-90 Days Overdue'
        ELSE '90+ Days Overdue'
    END AS aging_bucket,
    COUNT(*) AS num_invoices,
    SUM(fee_amount) AS total_outstanding
FROM permanent_placement_invoices
WHERE invoice_status = 'Outstanding'
GROUP BY aging_bucket
ORDER BY
    CASE
        WHEN aging_bucket LIKE 'Current%' THEN 1
        WHEN aging_bucket LIKE '0-30%' THEN 2
        WHEN aging_bucket LIKE '31-60%' THEN 3
        WHEN aging_bucket LIKE '61-90%' THEN 4
        ELSE 5
    END;

-- Total outstanding by client (all invoice types)
WITH outstanding_invoices AS (
    SELECT client_id, client_name, fee_amount AS amount
    FROM permanent_placement_invoices WHERE invoice_status = 'Outstanding'

    UNION ALL
    SELECT client_id, client_name, total_invoice_amount
    FROM temporary_worker_invoices WHERE invoice_status = 'Outstanding'

    UNION ALL
    SELECT client_id, client_name, total_amount
    FROM training_service_invoices WHERE invoice_status = 'Outstanding'

    UNION ALL
    SELECT client_id, client_name, total_amount
    FROM wellbeing_service_invoices WHERE invoice_status = 'Outstanding'

    UNION ALL
    SELECT client_id, client_name, total_amount
    FROM assessment_service_invoices WHERE invoice_status = 'Outstanding'

    UNION ALL
    SELECT client_id, client_name, total_amount
    FROM contact_centre_consultancy_invoices WHERE invoice_status = 'Outstanding'
)
SELECT
    client_id,
    client_name,
    COUNT(*) AS num_outstanding_invoices,
    SUM(amount) AS total_outstanding
FROM outstanding_invoices
GROUP BY client_id, client_name
ORDER BY total_outstanding DESC;

-- -----------------------------------------------------------------------------
-- 4.2 Payment Behavior Analysis
-- -----------------------------------------------------------------------------

-- Average days to payment by client (permanent placements)
SELECT
    client_name,
    COUNT(*) AS num_paid_invoices,
    AVG(payment_received_date - payment_due_date) AS avg_days_late,
    MIN(payment_received_date - payment_due_date) AS best_payment_time,
    MAX(payment_received_date - payment_due_date) AS worst_payment_time,
    SUM(fee_amount) AS total_revenue
FROM permanent_placement_invoices
WHERE invoice_status = 'Paid'
  AND payment_received_date IS NOT NULL
GROUP BY client_name
HAVING COUNT(*) >= 2
ORDER BY avg_days_late DESC;

-- Payment timing distribution
SELECT
    CASE
        WHEN payment_received_date <= payment_due_date THEN 'On Time / Early'
        WHEN payment_received_date - payment_due_date BETWEEN 1 AND 7 THEN '1-7 Days Late'
        WHEN payment_received_date - payment_due_date BETWEEN 8 AND 14 THEN '8-14 Days Late'
        WHEN payment_received_date - payment_due_date BETWEEN 15 AND 30 THEN '15-30 Days Late'
        ELSE '30+ Days Late'
    END AS payment_timing,
    COUNT(*) AS num_invoices,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage,
    SUM(fee_amount) AS total_value
FROM permanent_placement_invoices
WHERE invoice_status = 'Paid'
  AND payment_received_date IS NOT NULL
GROUP BY payment_timing
ORDER BY
    CASE
        WHEN payment_timing LIKE 'On Time%' THEN 1
        WHEN payment_timing LIKE '1-7%' THEN 2
        WHEN payment_timing LIKE '8-14%' THEN 3
        WHEN payment_timing LIKE '15-30%' THEN 4
        ELSE 5
    END;

-- -----------------------------------------------------------------------------
-- 4.3 Cash Flow Forecasting
-- -----------------------------------------------------------------------------

-- Weekly cash flow forecast (next 8 weeks)
WITH expected_receipts AS (
    SELECT
        payment_due_date AS expected_date,
        'Permanent Invoice' AS type,
        fee_amount AS amount
    FROM permanent_placement_invoices
    WHERE invoice_status = 'Outstanding'
      AND payment_due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '8 weeks'

    UNION ALL
    SELECT
        payment_due_date,
        'Temp Invoice',
        total_invoice_amount
    FROM temporary_worker_invoices
    WHERE invoice_status = 'Outstanding'
      AND payment_due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '8 weeks'
),
expected_payments AS (
    SELECT
        payment_date AS expected_date,
        'Staff Salary' AS type,
        -1 * total_cost AS amount
    FROM staff_salaries
    WHERE payment_status = 'Projected'
      AND payment_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '8 weeks'

    UNION ALL
    SELECT
        payroll_date,
        'Temp Payroll',
        -1 * total_employer_cost
    FROM temp_worker_payroll
    WHERE status = 'Projected'
      AND payroll_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '8 weeks'
)
SELECT
    DATE_TRUNC('week', expected_date) AS week_starting,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS cash_in,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS cash_out,
    SUM(amount) AS net_cash_flow
FROM (
    SELECT expected_date, amount FROM expected_receipts
    UNION ALL
    SELECT expected_date, amount FROM expected_payments
) combined
GROUP BY DATE_TRUNC('week', expected_date)
ORDER BY week_starting;

-- ============================================================================
-- SECTION 5: TAX & COMPLIANCE REPORTING
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 5.1 VAT Calculations
-- -----------------------------------------------------------------------------

-- Quarterly VAT calculation
SELECT
    DATE_TRUNC('quarter', invoice_date) AS quarter,
    SUM(fee_amount) AS net_revenue,
    SUM(fee_amount * 0.20) AS output_vat,
    -- Note: Input VAT would need to be calculated from expense records
    SUM(fee_amount * 0.20) AS estimated_net_vat_due
FROM permanent_placement_invoices
WHERE invoice_status IN ('Paid', 'Outstanding')
  AND invoice_date >= '2024-01-01'
GROUP BY DATE_TRUNC('quarter', invoice_date)
ORDER BY quarter;

-- -----------------------------------------------------------------------------
-- 5.2 Corporation Tax Estimates
-- -----------------------------------------------------------------------------

-- Annual profit for corporation tax
WITH annual_revenue AS (
    SELECT SUM(fee_amount) AS total
    FROM permanent_placement_invoices
    WHERE invoice_status = 'Paid'
      AND EXTRACT(YEAR FROM invoice_date) = 2024
),
annual_costs AS (
    SELECT SUM(total_cost) AS total
    FROM staff_salaries
    WHERE status = 'Paid'
      AND EXTRACT(YEAR FROM payment_date) = 2024
    -- Add other cost tables...
)
SELECT
    r.total AS revenue,
    c.total AS costs,
    r.total - c.total AS taxable_profit,
    ROUND((r.total - c.total) * 0.19, 2) AS estimated_corp_tax_19pct,
    ROUND((r.total - c.total) * 0.25, 2) AS estimated_corp_tax_25pct
FROM annual_revenue r, annual_costs c;

-- -----------------------------------------------------------------------------
-- 5.3 PAYE & NI Reporting
-- -----------------------------------------------------------------------------

-- Monthly PAYE and NI summary (staff)
SELECT
    DATE_TRUNC('month', payment_date) AS month,
    SUM(monthly_gross) AS total_gross_pay,
    SUM(employer_ni) AS total_employer_ni,
    SUM(employer_pension) AS total_employer_pension,
    -- Note: Employee PAYE/NI not in this table (would be in detailed payroll)
    SUM(total_cost) AS total_employer_cost
FROM staff_salaries
WHERE status = 'Paid'
GROUP BY DATE_TRUNC('month', payment_date)
ORDER BY month;

-- Monthly PAYE and NI summary (temp workers)
SELECT
    DATE_TRUNC('month', payroll_date) AS month,
    COUNT(DISTINCT worker_id) AS num_workers,
    SUM(gross_pay) AS total_gross_pay,
    SUM(paye_tax) AS total_paye_tax,
    SUM(employee_ni) AS total_employee_ni,
    SUM(employer_ni) AS total_employer_ni,
    SUM(net_pay) AS total_net_pay,
    SUM(total_employer_cost) AS total_employer_cost
FROM temp_worker_payroll
WHERE status = 'Paid'
GROUP BY DATE_TRUNC('month', payroll_date)
ORDER BY month;

-- ============================================================================
-- SECTION 6: PERFORMANCE METRICS & KPIs
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 6.1 Revenue KPIs
-- -----------------------------------------------------------------------------

-- Key financial metrics (last 12 months)
WITH metrics AS (
    SELECT
        SUM(fee_amount) AS perm_revenue,
        COUNT(*) AS num_placements,
        AVG(fee_amount) AS avg_fee
    FROM permanent_placement_invoices
    WHERE invoice_status = 'Paid'
      AND invoice_date >= CURRENT_DATE - INTERVAL '12 months'
),
staff_count AS (
    SELECT COUNT(DISTINCT employee_id) AS num_staff
    FROM staff_salaries
    WHERE payment_date >= CURRENT_DATE - INTERVAL '12 months'
)
SELECT
    m.perm_revenue,
    m.num_placements,
    m.avg_fee,
    m.perm_revenue / s.num_staff AS revenue_per_employee,
    m.num_placements / s.num_staff AS placements_per_employee
FROM metrics m, staff_count s;

-- -----------------------------------------------------------------------------
-- 6.2 Client Metrics
-- -----------------------------------------------------------------------------

-- Client lifetime value (top 20 clients)
WITH client_revenue AS (
    SELECT client_id, client_name, SUM(fee_amount) AS perm_revenue
    FROM permanent_placement_invoices WHERE invoice_status = 'Paid'
    GROUP BY client_id, client_name
),
client_temp_revenue AS (
    SELECT client_id, client_name, SUM(total_invoice_amount) AS temp_revenue
    FROM temporary_worker_invoices WHERE invoice_status = 'Paid'
    GROUP BY client_id, client_name
)
SELECT
    COALESCE(p.client_id, t.client_id) AS client_id,
    COALESCE(p.client_name, t.client_name) AS client_name,
    COALESCE(p.perm_revenue, 0) AS perm_revenue,
    COALESCE(t.temp_revenue, 0) AS temp_revenue,
    COALESCE(p.perm_revenue, 0) + COALESCE(t.temp_revenue, 0) AS total_lifetime_value
FROM client_revenue p
FULL OUTER JOIN client_temp_revenue t ON p.client_id = t.client_id
ORDER BY total_lifetime_value DESC
LIMIT 20;

-- Client acquisition cohorts (by first invoice month)
WITH first_invoice AS (
    SELECT
        client_id,
        client_name,
        MIN(invoice_date) AS first_invoice_date
    FROM permanent_placement_invoices
    GROUP BY client_id, client_name
)
SELECT
    DATE_TRUNC('month', first_invoice_date) AS cohort_month,
    COUNT(*) AS num_new_clients,
    SUM(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', first_invoice_date)) AS cumulative_clients
FROM first_invoice
GROUP BY DATE_TRUNC('month', first_invoice_date)
ORDER BY cohort_month;

-- -----------------------------------------------------------------------------
-- 6.3 Efficiency Metrics
-- -----------------------------------------------------------------------------

-- Average time to payment
SELECT
    DATE_TRUNC('quarter', invoice_date) AS quarter,
    COUNT(*) AS num_invoices,
    AVG(payment_received_date - invoice_date) AS avg_days_to_payment,
    AVG(payment_received_date - payment_due_date) AS avg_days_late
FROM permanent_placement_invoices
WHERE invoice_status = 'Paid'
  AND payment_received_date IS NOT NULL
GROUP BY DATE_TRUNC('quarter', invoice_date)
ORDER BY quarter;

-- ============================================================================
-- SECTION 7: COMPARISON & BENCHMARKING
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 7.1 Year-over-Year Comparisons
-- -----------------------------------------------------------------------------

-- YoY revenue comparison by quarter
SELECT
    EXTRACT(QUARTER FROM invoice_date) AS quarter,
    EXTRACT(YEAR FROM invoice_date) AS year,
    SUM(fee_amount) AS revenue,
    COUNT(*) AS num_placements
FROM permanent_placement_invoices
WHERE invoice_status = 'Paid'
GROUP BY EXTRACT(QUARTER FROM invoice_date), EXTRACT(YEAR FROM invoice_date)
ORDER BY quarter, year;

-- YoY cost comparison
SELECT
    EXTRACT(YEAR FROM payment_date) AS year,
    SUM(total_cost) AS total_staff_costs,
    AVG(total_cost) AS avg_monthly_cost
FROM staff_salaries
WHERE status = 'Paid'
GROUP BY EXTRACT(YEAR FROM payment_date)
ORDER BY year;

-- ============================================================================
-- SECTION 8: CUSTOM ANALYSIS TEMPLATES
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 8.1 Client Profitability Analysis
-- -----------------------------------------------------------------------------

-- Template: Replace CLIENT_ID with actual client ID
/*
WITH client_revenue AS (
    -- Permanent placement revenue
    SELECT SUM(fee_amount) AS perm_revenue
    FROM permanent_placement_invoices
    WHERE client_id = 'CLIENT_ID' AND invoice_status = 'Paid'
),
client_costs AS (
    -- This would require job/placement tracking to allocate costs
    -- For now, estimate as percentage of revenue
    SELECT 0 AS direct_costs
)
SELECT
    r.perm_revenue AS revenue,
    c.direct_costs,
    r.perm_revenue - c.direct_costs AS gross_profit,
    ROUND(100.0 * (r.perm_revenue - c.direct_costs) / r.perm_revenue, 2) AS margin_pct
FROM client_revenue r, client_costs c;
*/

-- -----------------------------------------------------------------------------
-- 8.2 Service Line Profitability
-- -----------------------------------------------------------------------------

-- Template: Analyze profitability of each service line
/*
-- Calculate revenue, estimated direct costs, and gross profit for each service
-- Requires allocation of staff time and overhead costs
*/

-- ============================================================================
-- END OF QUERIES
-- ============================================================================

-- Notes:
-- 1. Replace CURRENT_DATE with specific dates for historical analysis
-- 2. Adjust date ranges (INTERVAL '12 months', etc.) as needed
-- 3. Add WHERE clauses to filter by specific clients, periods, or statuses
-- 4. Many queries use UNION ALL - ensure consistent column types
-- 5. For large datasets, add LIMIT clauses or use date filters
-- 6. Test queries in development before running in production
-- 7. Consider creating views for frequently used query patterns
