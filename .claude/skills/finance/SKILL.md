---
name: finance
description: Expert in ProActive People recruitment finance, covering 20 financial categories (revenue/costs), UK recruitment industry metrics, regulatory compliance, Supabase database queries, profitability analysis, cash flow management, and financial reporting. This skill should be used when working with financial data, querying finance tables, analyzing revenue/costs, understanding UK recruitment financial regulations (NI, VAT, corporation tax), calculating margins, performing P&L analysis, or answering finance-related questions about the ProActive People system.
---

# Finance Skill

## Purpose

Provide comprehensive financial expertise for the ProActive People recruitment automation system, covering:

- **20 Financial Categories**: 6 revenue streams and 14 cost categories
- **Financial Data Analysis**: Revenue, costs, profitability, margins, cash flow
- **UK Recruitment Industry**: Market benchmarks, typical fees, industry standards
- **Regulatory Compliance**: UK tax regulations, NI, VAT, corporation tax, GDPR
- **Supabase Database**: Query all finance tables, perform complex analysis
- **Financial Reporting**: P&L, cash flow forecasting, KPI tracking

**Total Financial Records**: 858 transactions spanning 2024-2026
**Target Metrics**: £750k-£1.07m revenue, 30-40% profit margin, 5-person team

---

## When to Use This Skill

Invoke this skill proactively when:

### Financial Data Queries
- Query Supabase finance tables for revenue, costs, invoices, payroll
- Analyze permanent placements, temp workers, training, wellbeing, assessments, consultancy
- Calculate totals, averages, margins, or profitability by period
- Generate financial reports (monthly P&L, quarterly summaries, annual totals)

### UK Industry Context
- Understand recruitment industry benchmarks and standards
- Compare ProActive People performance to industry averages
- Calculate typical fee percentages for permanent placements (15-22%)
- Determine standard temp worker markups (35-42%)

### Regulatory Compliance
- Calculate employer NI contributions (13.8% → 15% April 2025)
- Understand National Living Wage changes (£11.44 → £12.21 April 2025)
- Calculate VAT due (20% standard rate, quarterly returns)
- Estimate corporation tax liability (19-25% on profits)
- Apply GDPR requirements to financial data handling

### Financial Analysis
- Perform profitability analysis by service line or client
- Calculate gross margins and net profit margins
- Analyze cash flow gaps (temp payroll vs invoice payment timing)
- Forecast revenue and costs
- Track KPIs (revenue per employee, placements per consultant, etc.)

### Business Questions
- "What was our Q1 revenue?"
- "Show me profit margin for permanent placements vs temp workers"
- "Which clients are most profitable?"
- "What's the impact of the April 2025 NI increase?"
- "Are we meeting industry benchmarks?"

---

## Bundled Resources

### 1. Financial Categories Reference (`references/financial_categories.md`)

**Purpose**: Complete documentation of all 20 financial categories in the Supabase database

**Contents**:
- **Revenue Streams** (6 categories, 290 records):
  1. Permanent Placement Invoices
  2. Temporary Worker Invoices
  3. Training Service Invoices
  4. Wellbeing Service Invoices
  5. Assessment Service Invoices
  6. Contact Centre Consultancy Invoices

- **Cost Categories** (14 categories, 568 records):
  7. Staff Salaries
  8. Temp Worker Payroll
  9. Office Rent & Facilities
  10. Technology Subscriptions
  11. Job Board Advertising
  12. Insurance Premiums
  13. Compliance Costs
  14. Marketing Costs
  15. Professional Services
  16. Utilities & Expenses
  17. Bank & Finance Charges
  18. Travel Expenses
  19. VAT Payments
  20. Corporation Tax

**Each Category Includes**:
- Supabase table name
- Complete schema with data types
- Business context and typical ranges
- Common query patterns
- Table relationships and foreign keys

**When to Load**: Load this reference when:
- Writing queries against finance tables
- Understanding table schemas and relationships
- Analyzing specific financial categories
- Exploring available financial data

**Search Pattern**: If looking for specific tables or fields, grep for:
```
grep -i "table_name" references/financial_categories.md
grep -i "schema" references/financial_categories.md
grep -i "permanent_placement" references/financial_categories.md
```

---

### 2. UK Recruitment Finance Reference (`references/uk_recruitment_finance.md`)

**Purpose**: UK recruitment industry financial benchmarks, regulations, and business metrics (2024-2025)

**Contents**:

**Revenue Models**:
- Permanent placement fee structures (15-22% by salary band)
- Temp worker markup ranges (35-42% by skill level)
- Retained search and consultancy pricing
- Contact centre consultancy project rates (£8k-£95k)

**Cost Benchmarks**:
- Staff salaries by role (2024-2025 UK market rates)
- Bristol office market rates (£42.50/sq ft prime)
- Technology stack costs (Bullhorn, Broadbean, LinkedIn)
- Typical cost allocations (personnel 67%, office 14%, tech 8%)

**UK Regulatory Requirements**:
- **National Insurance Changes (April 2025)**:
  - Employer NI: 13.8% → 15% (+1.2pp)
  - NI threshold: £9,100 → £5,000 (major cost increase)
- **National Living Wage**: £11.44 → £12.21 (April 2025)
- **VAT**: 20% standard rate, quarterly returns
- **Corporation Tax**: 19-25% based on profit bands
- **Pension Auto-Enrollment**: 3% employer minimum
- **GDPR**: Data protection requirements for recruitment

**Performance Metrics**:
- Revenue per employee: £150k-£200k (UK average)
- Placements per consultant: 15-25/year (permanent)
- Net profit margin targets: 30-40%
- Industry KPIs and benchmarks

**Cash Flow Management**:
- Payment cycle timing (permanent vs temp)
- Cash flow gap analysis (temp payroll weekly, invoices 7-14 days)
- Seasonal patterns (Q4 temp peak, Q1 training peak)

**When to Load**: Load this reference when:
- Comparing ProActive People to industry benchmarks
- Understanding UK recruitment business models
- Calculating regulatory compliance (NI, tax, VAT)
- Explaining fee structures or margins to users
- Analyzing profitability or performance metrics

**Search Pattern**: If looking for specific regulations or benchmarks, grep for:
```
grep -i "national insurance" references/uk_recruitment_finance.md
grep -i "living wage" references/uk_recruitment_finance.md
grep -i "fee percentage" references/uk_recruitment_finance.md
grep -i "margin" references/uk_recruitment_finance.md
```

---

### 3. Financial Queries Script (`scripts/financial_queries.sql`)

**Purpose**: Production-ready SQL queries for common financial analysis tasks in Supabase

**Contents** (8 Sections, 50+ Queries):

**Section 1: Revenue Analysis**
- Total revenue by period (monthly, quarterly, annual)
- Revenue breakdown by source (permanent, temp, training, etc.)
- Permanent placement analysis by salary band
- Top performing clients
- Temp worker margin analysis
- Active temp workers tracking

**Section 2: Cost Analysis**
- Monthly cost breakdown by category
- Personnel costs (staff + temps)
- Impact of April 2025 NI changes
- Operating costs (technology, marketing, office, etc.)
- Cost trends over time

**Section 3: Profitability Analysis**
- Monthly P&L summary
- Gross margin by service line
- Temp worker margin with payroll costs
- Net profit calculations

**Section 4: Cash Flow Analysis**
- Outstanding invoices and receivables
- Aged receivables (0-30, 31-60, 61-90, 90+ days)
- Payment behavior by client
- Payment timing distribution
- Weekly cash flow forecasts (8-week outlook)

**Section 5: Tax & Compliance Reporting**
- Quarterly VAT calculations (output tax minus input tax)
- Corporation tax estimates (annual profit × 19-25%)
- Monthly PAYE and NI summaries (staff and temps)

**Section 6: Performance Metrics & KPIs**
- Revenue per employee
- Placements per employee
- Client lifetime value (top 20)
- Client acquisition cohorts
- Average time to payment

**Section 7: Comparison & Benchmarking**
- Year-over-year revenue comparisons
- YoY cost trends
- Seasonal pattern analysis

**Section 8: Custom Analysis Templates**
- Client profitability analysis template
- Service line profitability template

**When to Use**: Use these queries when:
- Generating financial reports for users
- Analyzing revenue, costs, or profitability
- Calculating cash flow or forecasting
- Tracking KPIs or performance metrics
- Preparing tax compliance reports
- Benchmarking performance over time

**Query Selection Workflow**:
1. Identify the analysis type (revenue, cost, profitability, cash flow, tax, KPIs)
2. Navigate to the relevant section in `financial_queries.sql`
3. Copy and adapt the query, replacing:
   - Date ranges (`'2024-01-01'`, `CURRENT_DATE - INTERVAL '12 months'`)
   - Client IDs (`'CLT-001'`)
   - Status filters (`WHERE invoice_status = 'Paid'`)
   - Aggregation periods (`DATE_TRUNC('month', ...)`)
4. Execute using Supabase MCP tools
5. Format results for user presentation

**Example Adaptation**:
```sql
-- Original query (all permanent placements in 2024)
SELECT SUM(fee_amount) FROM permanent_placement_invoices
WHERE invoice_date BETWEEN '2024-01-01' AND '2024-12-31';

-- Adapted query (last quarter only)
SELECT SUM(fee_amount) FROM permanent_placement_invoices
WHERE invoice_date >= DATE_TRUNC('quarter', CURRENT_DATE);

-- Adapted query (specific client)
SELECT SUM(fee_amount) FROM permanent_placement_invoices
WHERE client_id = 'CLT-042'
  AND invoice_status = 'Paid';
```

---

## Workflow Instructions

### Financial Query Workflow

**When a user asks a financial question**, follow this workflow:

1. **Classify the Query Type**:
   - Revenue analysis? → Use Section 1 queries
   - Cost analysis? → Use Section 2 queries
   - Profitability? → Use Section 3 queries
   - Cash flow? → Use Section 4 queries
   - Tax/compliance? → Use Section 5 queries
   - KPIs/metrics? → Use Section 6 queries

2. **Select Appropriate Query**:
   - Open `scripts/financial_queries.sql`
   - Navigate to the relevant section
   - Choose the query that best matches the question
   - Adapt date ranges, filters, and parameters

3. **Execute Query**:
   - Use Supabase MCP tools (`mcp__supabase__execute_sql`)
   - Pass the adapted SQL query
   - Handle any errors (table not found, syntax issues)

4. **Interpret Results**:
   - Parse the returned data
   - Calculate any additional metrics needed
   - Compare to benchmarks (from `uk_recruitment_finance.md`)
   - Identify trends, anomalies, or insights

5. **Present to User**:
   - Format results in clear tables or summaries
   - Provide context and interpretation
   - Compare to industry benchmarks where relevant
   - Suggest actions or next steps

**Example**:

User: "What was our total revenue last quarter?"

```sql
-- Adapted from Section 1.1 - Total revenue by quarter
SELECT
    DATE_TRUNC('quarter', invoice_date) AS quarter,
    SUM(fee_amount) AS total_revenue
FROM permanent_placement_invoices
WHERE invoice_date >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months')
GROUP BY DATE_TRUNC('quarter', invoice_date);

-- Also query other revenue sources (temp, training, etc.)
-- then sum all sources for total quarterly revenue
```

---

### Financial Analysis Workflow

**When performing comprehensive financial analysis**:

1. **Load Financial Categories Reference**:
   - Read `references/financial_categories.md`
   - Understand which tables contain the needed data
   - Note table schemas and relationships

2. **Load Industry Reference** (if comparing to benchmarks):
   - Read `references/uk_recruitment_finance.md`
   - Note relevant benchmarks (e.g., "30-40% profit margin is healthy")
   - Understand regulatory context (e.g., April 2025 NI changes)

3. **Execute Queries**:
   - Use queries from `scripts/financial_queries.sql`
   - Run multiple queries if analyzing across categories
   - Join results as needed

4. **Calculate Derived Metrics**:
   - Profit margin = (Revenue - Costs) / Revenue × 100
   - Revenue per employee = Total Revenue / Number of Staff
   - Gross margin (temp) = Markup / Charge Rate × 100
   - Net margin = (Revenue - All Costs) / Revenue × 100

5. **Compare to Benchmarks**:
   - ProActive People vs UK industry averages
   - Current period vs prior periods (YoY, QoQ)
   - Actual vs target/budget

6. **Identify Insights**:
   - What's performing well? (e.g., "Consultancy has 50% margin")
   - What needs attention? (e.g., "Temp margin below target")
   - Trends? (e.g., "Revenue growing 15% YoY")
   - Risks? (e.g., "Cash flow gap increasing")

---

### Regulatory Compliance Workflow

**When calculating tax obligations or regulatory impacts**:

1. **Identify Regulation**:
   - National Insurance? → April 2025 changes (13.8% → 15%, threshold £9,100 → £5,000)
   - National Living Wage? → April 2025 increase (£11.44 → £12.21)
   - VAT? → 20% standard rate, quarterly returns
   - Corporation Tax? → 19-25% based on profit level

2. **Load Industry Reference**:
   - Read `references/uk_recruitment_finance.md`
   - Navigate to "UK Regulatory Requirements" section
   - Note exact rates, thresholds, and calculation methods

3. **Query Relevant Data**:
   - Staff salaries → `staff_salaries` table
   - Temp payroll → `temp_worker_payroll` table
   - Revenue → All invoice tables
   - Expenses → All cost tables

4. **Calculate Impact**:
   - **NI Example**: For each employee, calculate increase:
     - Old NI: (Annual Salary - £9,100) × 13.8%
     - New NI: (Annual Salary - £5,000) × 15%
     - Increase: New NI - Old NI

   - **VAT Example**:
     - Output Tax: Sum(Invoice Amounts × 0.20)
     - Input Tax: Sum(Expense Amounts × 0.20)
     - Net VAT Due: Output Tax - Input Tax

5. **Present Results**:
   - Show calculations clearly
   - Explain regulatory context
   - Quantify financial impact
   - Suggest mitigation strategies if needed

---

### Cash Flow Analysis Workflow

**When analyzing or forecasting cash flow**:

1. **Identify Cash Flow Components**:
   - **Cash In**: Invoice payments (permanent, temp, training, etc.)
   - **Cash Out**: Salaries, temp payroll, rent, technology, expenses

2. **Query Outstanding Invoices**:
   - Use Section 4.1 query: "Aged receivables analysis"
   - Identify invoices by aging bucket (current, 0-30, 31-60, 61-90, 90+ days)
   - Note payment terms and expected receipt dates

3. **Query Upcoming Payments**:
   - Staff salaries (monthly, 28th of month)
   - Temp payroll (weekly)
   - Rent (monthly, 1st of month)
   - Technology subscriptions (monthly)
   - Tax payments (VAT quarterly, PAYE monthly)

4. **Calculate Cash Flow Gap**:
   - **Temp Worker Gap**: Pay workers weekly, invoice clients (7-14 day terms)
     - Example: Week 1 pay £1,000, Week 2-3 receive £1,380 (38% markup)
     - Gap: 1-2 weeks of working capital needed

   - **Permanent Placement Gap**: Invoice on placement, receive 30-60 days later
     - Gap: 1-2 months before fee received
     - Risk: Rebate if candidate leaves in guarantee period

5. **Forecast Next 8-12 Weeks**:
   - Use Section 4.3 query: "Weekly cash flow forecast"
   - Show week-by-week cash in, cash out, net flow
   - Identify pressure points (large payments due, slow collection)

6. **Recommend Actions**:
   - If negative cash flow forecast: Invoice factoring, payment terms negotiation, delay non-critical expenses
   - If slow collections: Chase overdue invoices, review client payment terms
   - If seasonal pressure: Plan ahead (e.g., Q4 temp volumes require working capital)

---

## ProActive People Context

### Financial Profile (5-Person Team)

**Annual Targets**:
- Revenue: £750,000 - £1,070,000
- Costs: £525,000 - £665,000
- Net Profit: £225,000 - £405,000 (30-40% margin)

**Revenue Mix**:
- Permanent Placements: 40-50% (£350k-£450k)
- Temp Workers: 25-35% (£200k-£250k)
- Contact Centre Consultancy: 15-25% (£120k-£200k)
- Training Services: 5-10% (£50k-£100k)
- Wellbeing Services: 2-5% (£20k-£40k)
- Assessment Services: 1-3% (£10k-£30k)

**Cost Structure**:
- Personnel (staff + temps): 67% (£350k-£450k)
- Office & Facilities: 14% (£85k-£95k)
- Technology: 8% (£45k-£55k)
- Other Costs: 11% (£45k-£65k)

**Staff**:
1. Managing Director (£60k/year)
2. Temp Consultant & CC Specialist (£45k/year)
3. Resourcer/Admin/Tech Lead (£28k/year)
4. Compliance Officer & Wellbeing (£38k/year) - Emma Jane
5. Finance & Training Lead (£42k/year) - Stuart Pearce

**Key Metrics**:
- Revenue per employee: £150k-£214k ✅ (industry average)
- Personnel costs: 35-40% of revenue ✅ (well controlled)
- Net profit margin: 30-40% ✅ (high end of industry)

---

## Important Regulatory Changes (April 2025)

**Always consider these changes when analyzing 2025+ data**:

### 1. Employer National Insurance Increase
- **Rate**: 13.8% → 15.0% (+1.2 percentage points)
- **Threshold**: £9,100/year → £5,000/year (reduced by £4,100)
- **Impact**: ~£2,000-£3,000 extra cost per employee per year
- **Applies To**: All staff salaries and eligible temp workers
- **Queries**: Check `payment_date >= '2025-04-01'` in staff_salaries table

### 2. National Living Wage Increase
- **Rate**: £11.44/hr → £12.21/hr (+77p, +6.7%)
- **Impact**: Temp worker pay increases, client charge rates must increase
- **Example**: 40-hour worker:
  - Old pay: £457.60/week
  - New pay: £488.40/week (+£30.80/week)
  - With 38% markup, client charge increases by £42.70/week
- **Queries**: Check `payroll_date >= '2025-04-01'` in temp_worker_payroll table

**Financial Impact Summary**:
- ProActive People with 5 staff + ~10 temp workers
- Additional annual NI cost: ~£15,000-£20,000
- Additional temp payroll cost: ~£16,000-£20,000 (offset by higher client charges)
- **Total impact**: ~£31,000-£40,000 additional annual costs

---

## Quick Reference

### Financial Table Names (Supabase)

**Revenue Tables**:
- `permanent_placement_invoices`
- `temporary_worker_invoices`
- `training_service_invoices`
- `wellbeing_service_invoices`
- `assessment_service_invoices`
- `contact_centre_consultancy_invoices`

**Cost Tables**:
- `staff_salaries`
- `temp_worker_payroll`
- `office_rent_facilities`
- `technology_subscriptions`
- `job_board_advertising`
- `insurance_premiums`
- `compliance_costs`
- `marketing_costs`
- `professional_services`
- `utilities_expenses`
- `bank_finance_charges`
- `travel_expenses`
- `vat_payments`
- `corporation_tax`

### Common Financial Calculations

**Profit Margin**:
```
Profit Margin % = (Revenue - Costs) / Revenue × 100
```

**Gross Margin (Temp Workers)**:
```
Gross Margin % = Markup / Charge Rate × 100
Example: 38% markup = 38% gross margin
```

**Employer NI (2024)**:
```
NI = (Annual Salary - £9,100) × 13.8%
```

**Employer NI (April 2025+)**:
```
NI = (Annual Salary - £5,000) × 15%
```

**VAT Due (Quarterly)**:
```
Net VAT = Output Tax (revenue × 20%) - Input Tax (expenses × 20%)
```

**Revenue per Employee**:
```
Revenue per Employee = Total Revenue / Number of Staff
Target: £150k-£200k per employee
```

### Payment Status Values
- **Paid**: Transaction completed (before Nov 2024)
- **Outstanding**: Invoice issued, payment pending (Nov 2024 - Feb 2025)
- **Projected**: Future transaction (March 2025+)

### Date Filtering Patterns
```sql
-- Current month
WHERE date_field >= DATE_TRUNC('month', CURRENT_DATE)

-- Last quarter
WHERE date_field >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months')

-- Year to date
WHERE date_field >= DATE_TRUNC('year', CURRENT_DATE)

-- Last 12 months
WHERE date_field >= CURRENT_DATE - INTERVAL '12 months'

-- Specific period
WHERE date_field BETWEEN '2024-01-01' AND '2024-12-31'

-- Before/after regulatory change
WHERE payment_date >= '2025-04-01'  -- April 2025 NI changes
```

---

## Examples

### Example 1: Calculate Q1 2024 Profit

**User Query**: "What was our profit in Q1 2024?"

**Workflow**:
1. Query all revenue sources for Q1 2024
2. Query all cost categories for Q1 2024
3. Calculate: Revenue - Costs = Profit
4. Calculate: Profit / Revenue × 100 = Profit Margin %
5. Compare to target (30-40% margin)

**SQL** (adapted from financial_queries.sql):
```sql
-- Revenue
SELECT SUM(fee_amount) AS q1_revenue
FROM permanent_placement_invoices
WHERE invoice_date BETWEEN '2024-01-01' AND '2024-03-31'
AND invoice_status = 'Paid';
-- Plus similar queries for temp, training, etc.

-- Costs
SELECT SUM(total_cost) AS q1_staff_costs
FROM staff_salaries
WHERE payment_date BETWEEN '2024-01-01' AND '2024-03-31';
-- Plus similar queries for other costs

-- Profit calculation
SELECT
    (revenue_sum - costs_sum) AS profit,
    ROUND(100.0 * (revenue_sum - costs_sum) / revenue_sum, 2) AS margin_pct;
```

**Response Format**:
```
Q1 2024 Financial Summary:
- Total Revenue: £245,000
- Total Costs: £168,000
- Net Profit: £77,000
- Profit Margin: 31.4%

✅ Performance: On target (30-40% margin)
```

### Example 2: Impact of April 2025 NI Changes

**User Query**: "How much will the April 2025 NI increase cost us?"

**Workflow**:
1. Load `references/uk_recruitment_finance.md` for regulation details
2. Query staff salaries for all 5 employees
3. Calculate old NI (13.8%, £9,100 threshold)
4. Calculate new NI (15%, £5,000 threshold)
5. Show difference for each employee and total

**Calculation**:
```
Managing Director (£60,000):
- Old NI: (£60,000 - £9,100) × 13.8% = £7,024
- New NI: (£60,000 - £5,000) × 15% = £8,250
- Increase: £1,226/year

[Similar for other 4 staff...]

Total Annual Increase: ~£6,000-£8,000
```

**Response Format**:
```
April 2025 NI Changes - Financial Impact:

Employee                    Old NI    New NI   Increase
────────────────────────────────────────────────────────
Managing Director          £7,024    £8,250    +£1,226
Temp Consultant            £4,955    £6,000    +£1,045
Resourcer/Admin            £2,608    £3,450      +£842
Compliance Officer         £3,989    £4,950      +£961
Finance/Training Lead      £4,540    £5,550    +£1,010
────────────────────────────────────────────────────────
Total Annual Increase:                        +£5,084

Additionally, temp workers will incur ~£10,000-£15,000
extra NI costs annually.

**Total Impact**: £15,000-£20,000 additional annual costs

Note: This represents ~2-3% reduction in profit margin.
```

### Example 3: Client Profitability Analysis

**User Query**: "Which clients are most profitable?"

**Workflow**:
1. Query all revenue sources by client
2. Sum total revenue per client
3. Estimate cost allocation (% of revenue or time tracking)
4. Calculate gross profit per client
5. Rank by profitability

**SQL** (adapted from Section 6.2):
```sql
-- Client lifetime value with all revenue sources
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
    COALESCE(p.perm_revenue, 0) + COALESCE(t.temp_revenue, 0) AS total_revenue
FROM client_revenue p
FULL OUTER JOIN client_temp_revenue t ON p.client_id = t.client_id
ORDER BY total_revenue DESC
LIMIT 10;
```

**Response Format**:
```
Top 10 Most Profitable Clients (Lifetime Value):

Client                        Perm      Temp     Total Revenue
──────────────────────────────────────────────────────────────
Global Sales Corp          £45,200   £32,100       £77,300
TechVision Ltd             £68,400        £0       £68,400
Bristol Finance Group      £39,800   £18,500       £58,300
[...]

💡 Insights:
- Top 10 clients represent 45% of total revenue
- Global Sales Corp uses both perm + temp (diversified)
- TechVision Ltd exclusively uses permanent recruitment
- Consider upselling temp services to perm-only clients
```

---

## Summary

Invoke the finance skill when working with ProActive People financial data across all 20 categories, performing analysis, understanding UK recruitment industry context, calculating regulatory compliance, or answering finance-related questions. The skill provides:

- **Complete Financial Schemas**: All 20 tables documented
- **Production-Ready SQL**: 50+ tested queries for common analyses
- **UK Industry Context**: Benchmarks, regulations, typical margins
- **Regulatory Expertise**: NI, VAT, corporation tax, GDPR, living wage
- **Business Insights**: Profitability, cash flow, KPIs, performance tracking

Always load the appropriate reference documents (`financial_categories.md` for schemas, `uk_recruitment_finance.md` for industry context) and use the SQL queries in `financial_queries.sql` as templates for Supabase analysis.
