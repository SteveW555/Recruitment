# ProActive People - Financial Categories Reference

## Overview

This reference documents all 20 financial categories in the ProActive People recruitment system, including revenue streams and cost categories. Each section includes the Supabase table name, schema, and business context.

**Total Records**: 858 transactions
**Time Period**: 2024-2026
**Currency**: GBP (£)

---

## Revenue Streams (6 Categories, 290 Records)

### 1. Permanent Placement Invoices

**Supabase Table**: `permanent_placement_invoices`
**Records**: 50
**Description**: Client invoices for permanent recruitment placements with fee ranges of 15-22% of annual salary

**Schema**:
```
invoice_id              VARCHAR(50)  PRIMARY KEY
invoice_date            DATE         NOT NULL
client_id               VARCHAR(20)  FOREIGN KEY
client_name             VARCHAR(200)
candidate_name          VARCHAR(200)
job_title               VARCHAR(200)
annual_salary           DECIMAL(10,2)
fee_percentage          DECIMAL(5,2)
fee_amount              DECIMAL(10,2)
invoice_status          VARCHAR(20)  -- Paid, Outstanding, Projected
payment_due_date        DATE
payment_received_date   DATE
payment_method          VARCHAR(50)  -- BACS, Credit Card
notes                   TEXT
```

**Business Context**:
- Fee Range: £3,600 - £15,000 per placement
- Average Fee: £8,500 (18% of £47k avg salary)
- Payment Terms: Net 30-60 days
- Payment Behavior: ~80% on-time, ~15% late (5-10 days), ~5% very late

**Common Queries**:
- Revenue by period (month, quarter, year)
- Average fee percentage by job level
- Payment aging analysis (outstanding vs paid)
- Client profitability analysis

---

### 2. Temporary Worker Invoices

**Supabase Table**: `temporary_worker_invoices`
**Records**: 50
**Description**: Weekly billing to clients for temporary worker placements with 35-42% markup on hourly rates

**Schema**:
```
invoice_id              VARCHAR(50)  PRIMARY KEY
invoice_date            DATE         NOT NULL
week_ending             DATE
client_id               VARCHAR(20)  FOREIGN KEY
client_name             VARCHAR(200)
temp_worker_name        VARCHAR(200)
hours_worked            DECIMAL(5,2)
hourly_pay_rate         DECIMAL(6,2)
hourly_charge_rate      DECIMAL(6,2)
markup_percentage       DECIMAL(5,2)
gross_margin            DECIMAL(10,2)
total_invoice_amount    DECIMAL(10,2)
invoice_status          VARCHAR(20)
payment_due_date        DATE
payment_received_date   DATE
payment_method          VARCHAR(50)
```

**Business Context**:
- Markup Range: 35-42% (average 38%)
- Gross Margin: £150 - £300 per week per worker
- Payment Terms: Net 7-14 days (faster than permanent)
- Cash Flow Critical: Workers paid weekly, clients pay 7-14 days later

**Common Queries**:
- Weekly/monthly temp revenue
- Margin analysis by worker or client
- Active vs inactive temp workers
- Cash flow gap analysis (payroll vs invoice timing)

---

### 3. Training Service Invoices

**Supabase Table**: `training_service_invoices`
**Records**: 40
**Description**: Custom training programs and coaching sessions delivered by Stuart Pearce (Finance & Training Lead)

**Schema**:
```
invoice_id              VARCHAR(50)  PRIMARY KEY
invoice_date            DATE         NOT NULL
client_id               VARCHAR(20)  FOREIGN KEY
client_name             VARCHAR(200)
program_name            VARCHAR(200)
trainer                 VARCHAR(100) -- Stuart Pearce
duration_days           INTEGER
number_participants     INTEGER
price_per_participant   DECIMAL(10,2)
total_amount            DECIMAL(10,2)
invoice_status          VARCHAR(20)
payment_due_date        DATE
payment_received_date   DATE
payment_method          VARCHAR(50)
```

**Business Context**:
- Range: £250 (coaching) to £12,000 (large programs)
- Types: One-on-one coaching, group workshops, multi-day programs
- Target: £50,000 - £100,000 annual revenue
- Peak Season: Q1 (new year planning) and Q3 (post-summer)

---

### 4. Wellbeing Service Invoices

**Supabase Table**: `wellbeing_service_invoices`
**Records**: 50
**Description**: Wellbeing support sessions and employer packages delivered by Emma Jane (Compliance Officer & Wellbeing)

**Schema**:
```
invoice_id              VARCHAR(50)  PRIMARY KEY
invoice_date            DATE         NOT NULL
client_id               VARCHAR(20)  FOREIGN KEY
client_name             VARCHAR(200)
service_type            VARCHAR(100) -- Individual Session, Monthly Package, Annual Package
sessions_included       INTEGER
therapist               VARCHAR(100) -- Emma Jane
price_per_session       DECIMAL(10,2)
total_amount            DECIMAL(10,2)
invoice_status          VARCHAR(20)
payment_due_date        DATE
payment_received_date   DATE
payment_method          VARCHAR(50)
```

**Business Context**:
- Range: £150 per session to £10,000 packages
- Target: £20,000 - £40,000 annual revenue
- Service Types: Individual sessions, monthly packages, annual employer packages

---

### 5. Assessment Service Invoices

**Supabase Table**: `assessment_service_invoices`
**Records**: 50
**Description**: Psychometric testing and profiling for candidate assessment

**Schema**:
```
invoice_id              VARCHAR(50)  PRIMARY KEY
invoice_date            DATE         NOT NULL
client_id               VARCHAR(20)  FOREIGN KEY
client_name             VARCHAR(200)
assessment_type         VARCHAR(100) -- Psychometric, Skills Test, Bespoke
number_of_candidates    INTEGER
price_per_assessment    DECIMAL(10,2)
total_amount            DECIMAL(10,2)
invoice_status          VARCHAR(20)
payment_due_date        DATE
payment_received_date   DATE
payment_method          VARCHAR(50)
```

**Business Context**:
- Range: £75 per candidate to £4,000 for bespoke assessments
- Target: £10,000 - £30,000 annual revenue
- Often bundled with recruitment services

---

### 6. Contact Centre Consultancy Invoices

**Supabase Table**: `contact_centre_consultancy_invoices`
**Records**: 50
**Description**: Major consultancy projects for contact centre setup, expansion, and turnaround

**Schema**:
```
invoice_id              VARCHAR(50)  PRIMARY KEY
invoice_date            DATE         NOT NULL
client_id               VARCHAR(20)  FOREIGN KEY
client_name             VARCHAR(200)
project_type            VARCHAR(100) -- Setup, Expansion, Turnaround
project_start_date      DATE
project_duration_days   INTEGER
consultant              VARCHAR(100)
total_amount            DECIMAL(10,2)
invoice_status          VARCHAR(20)
payment_due_date        DATE
payment_received_date   DATE
payment_method          VARCHAR(50)
notes                   TEXT
```

**Business Context**:
- Range: £8,000 to £95,000 per project
- Target: £120,000 - £200,000 annual revenue (2-3 major projects)
- Payment Terms: Net 45-60 days (largest projects)
- Project Types: New setup, expansion, turnaround/rescue

---

## Cost Categories (14 Categories, 568 Records)

### 7. Staff Salaries

**Supabase Table**: `staff_salaries`
**Records**: 50 (5 staff × 10 months)
**Description**: Monthly salaries for 5 permanent staff members including employer costs

**Schema**:
```
payment_id              VARCHAR(50)  PRIMARY KEY
payment_date            DATE         NOT NULL
employee_id             VARCHAR(20)  FOREIGN KEY
employee_name           VARCHAR(200)
annual_salary           DECIMAL(10,2)
monthly_gross           DECIMAL(10,2)
employer_ni             DECIMAL(10,2) -- 13.8% (2024) → 15% (April 2025+)
employer_pension        DECIMAL(10,2) -- 3% minimum
bonus                   DECIMAL(10,2)
total_cost              DECIMAL(10,2)
payment_method          VARCHAR(50)
status                  VARCHAR(20)
```

**Business Context**:
- 5 Staff Members (2024-2025 salaries):
  1. Managing Director: £60,000/year
  2. Temp Consultant & CC Specialist: £45,000/year
  3. Resourcer/Admin/Tech Lead: £28,000/year
  4. Compliance Officer & Wellbeing: £38,000/year
  5. Finance & Training Lead: £42,000/year
- Total Payroll: ~£20,000-£30,000/month
- Employer NI: 13.8% (2024) → 15% (April 2025)
- Pension: 3% minimum auto-enrollment

**Regulatory Changes April 2025**:
- Employer NI increase: 13.8% → 15%
- NI threshold drop: £9,100 → £5,000 (increases total NI paid)

---

### 8. Temp Worker Payroll

**Supabase Table**: `temp_worker_payroll`
**Records**: 50
**Description**: Weekly payroll for temporary workers with PAYE tax and NI deductions

**Schema**:
```
payroll_id              VARCHAR(50)  PRIMARY KEY
payroll_date            DATE         NOT NULL
week_ending             DATE
worker_id               VARCHAR(20)  FOREIGN KEY
worker_name             VARCHAR(200)
hours_worked            DECIMAL(5,2)
hourly_rate             DECIMAL(6,2)
gross_pay               DECIMAL(10,2)
paye_tax                DECIMAL(10,2)
employee_ni             DECIMAL(10,2)
employer_ni             DECIMAL(10,2)
employer_pension        DECIMAL(10,2)
net_pay                 DECIMAL(10,2)
total_employer_cost     DECIMAL(10,2)
payment_method          VARCHAR(50)
status                  VARCHAR(20)
```

**Business Context**:
- Weekly payroll processing (workers paid weekly)
- National Living Wage: £11.44/hr (2024) → £12.21/hr (April 2025)
- Deductions: PAYE tax, employee NI, employer NI, pension
- Critical: Payroll due weekly, client invoices due 7-14 days (cash flow gap)

---

### 9. Office Rent & Facilities

**Supabase Table**: `office_rent_facilities`
**Records**: 50
**Description**: Monthly rent and service charges for Bristol and Weston offices

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
office_location         VARCHAR(100) -- Bristol HQ, Weston Office
square_feet             INTEGER
price_per_sqft          DECIMAL(6,2)
monthly_rent            DECIMAL(10,2)
service_charge          DECIMAL(10,2)
total_amount            DECIMAL(10,2)
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
landlord                VARCHAR(200)
```

**Business Context**:
- Bristol Prime Office: £42.50/sq ft
- Monthly Cost: £5,500 - £6,500 (both offices)
- Bristol Market Data: £42.50-£50/sq ft (Savills 2024 report)

---

### 10. Technology Subscriptions

**Supabase Table**: `technology_subscriptions`
**Records**: 50
**Description**: Monthly subscriptions for recruitment technology stack

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
service_name            VARCHAR(200) -- Bullhorn, Broadbean, LinkedIn Recruiter, etc.
monthly_cost            DECIMAL(10,2)
billing_cycle           VARCHAR(20)  -- Monthly, Annual
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
auto_renew              BOOLEAN
vendor                  VARCHAR(200)
```

**Business Context**:
- Monthly Cost: £2,000 - £2,500
- Key Systems:
  - Bullhorn ATS: £650/month
  - Broadbean: £450/month
  - LinkedIn Recruiter (3 licenses): £850/month
  - Microsoft 365: £50/month
  - Other tools: £200-£500/month

---

### 11. Job Board Advertising

**Supabase Table**: `job_board_advertising`
**Records**: 50
**Description**: Monthly advertising spend on major UK job boards

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
job_board               VARCHAR(100) -- Indeed, Totaljobs, CV-Library, Reed, etc.
package_type            VARCHAR(100)
monthly_cost            DECIMAL(10,2)
number_of_posts         INTEGER
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
```

**Business Context**:
- Monthly Cost: £250 - £1,200
- Major Boards: Indeed, Totaljobs, CV-Library, Reed, Jobsite, Jobserve
- Varies by recruitment volume and sector focus

---

### 12. Insurance Premiums

**Supabase Table**: `insurance_premiums`
**Records**: 10
**Description**: Annual insurance policies required for recruitment agency operations

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
policy_type             VARCHAR(100) -- PI, Employers Liability, Public Liability, Cyber
annual_premium          DECIMAL(10,2)
insurer                 VARCHAR(200)
policy_start_date       DATE
policy_end_date         DATE
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
```

**Business Context**:
- Annual Cost: ~£650
- Required Policies:
  - Professional Indemnity: £2,000-£5,000
  - Employers Liability: £500-£1,500 (legally required)
  - Public Liability: £300-£800
  - Cyber Insurance: £500-£1,500

---

### 13. Compliance Costs

**Supabase Table**: `compliance_costs`
**Records**: 50
**Description**: DBS checks, GDPR software, REC membership, and other compliance expenses

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
compliance_type         VARCHAR(100) -- DBS Check, GDPR Software, REC Membership
amount                  DECIMAL(10,2)
candidate_name          VARCHAR(200) -- For DBS checks
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
vendor                  VARCHAR(200)
```

**Business Context**:
- Monthly Range: £50 - £800
- DBS Checks: £40-£60 per check (required for many placements)
- REC Membership: Annual membership fee
- GDPR Software: Data protection compliance tools

---

### 14. Marketing Costs

**Supabase Table**: `marketing_costs`
**Records**: 50
**Description**: Digital marketing, advertising, SEO, events, and client hospitality

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
marketing_type          VARCHAR(100) -- Google Ads, LinkedIn Ads, SEO, Event, Hospitality
campaign_name           VARCHAR(200)
amount                  DECIMAL(10,2)
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
vendor                  VARCHAR(200)
notes                   TEXT
```

**Business Context**:
- Monthly Range: £150 - £1,200
- Types: Google Ads, LinkedIn campaigns, SEO services, networking events, client hospitality

---

### 15. Professional Services

**Supabase Table**: `professional_services`
**Records**: 50
**Description**: External services including accountant, legal advisor, IT support

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
service_type            VARCHAR(100) -- Accountant, Legal, IT Support
service_provider        VARCHAR(200)
amount                  DECIMAL(10,2)
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
notes                   TEXT
```

**Business Context**:
- Monthly Range: £750 - £2,500
- Services: Monthly accountant fees, legal advice, IT support, payroll services

---

### 16. Utilities & Expenses

**Supabase Table**: `utilities_expenses`
**Records**: 50
**Description**: Office utilities including electricity, gas, water, internet, phones

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
utility_type            VARCHAR(100) -- Electricity, Gas, Water, Internet, Phone
office_location         VARCHAR(100)
amount                  DECIMAL(10,2)
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
supplier                VARCHAR(200)
```

**Business Context**:
- Monthly Cost: £700 - £1,000
- Types: Electricity, gas, water, business broadband, phone systems

---

### 17. Bank & Finance Charges

**Supabase Table**: `bank_finance_charges`
**Records**: 50
**Description**: Bank account fees, transaction charges, overdraft interest

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
fee_type                VARCHAR(100) -- Monthly Fee, Transaction Fees, Overdraft Interest
amount                  DECIMAL(10,2)
payment_status          VARCHAR(20)
bank                    VARCHAR(200)
```

**Business Context**:
- Monthly Range: £15 - £85
- Types: Account fees, card transaction fees, international payments, overdraft interest

---

### 18. Travel Expenses

**Supabase Table**: `travel_expenses`
**Records**: 50
**Description**: Business travel including mileage, trains, taxis, parking, hotels

**Schema**:
```
expense_id              VARCHAR(50)  PRIMARY KEY
expense_date            DATE         NOT NULL
employee_id             VARCHAR(20)  FOREIGN KEY
employee_name           VARCHAR(200)
travel_type             VARCHAR(100) -- Mileage, Train, Taxi, Parking, Hotel
distance_miles          DECIMAL(6,2) -- For mileage claims
amount                  DECIMAL(10,2)
purpose                 TEXT
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)
```

**Business Context**:
- Per Expense: £5 - £150
- Mileage Rate: 45p/mile (first 10,000 miles), then 25p/mile (HMRC rates)
- Common: Client meetings, site visits, networking events

---

### 19. VAT Payments

**Supabase Table**: `vat_payments`
**Records**: 6 (quarterly)
**Description**: Quarterly VAT payments to HMRC

**Schema**:
```
payment_id              VARCHAR(50)  PRIMARY KEY
payment_date            DATE         NOT NULL
quarter                 VARCHAR(10)  -- Q1, Q2, Q3, Q4
quarter_ending          DATE
vat_collected           DECIMAL(10,2) -- VAT charged to clients
vat_paid                DECIMAL(10,2) -- VAT paid on expenses
net_vat_due             DECIMAL(10,2)
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)  -- HMRC Online
```

**Business Context**:
- Quarterly Payments: £6,000 - £9,000
- Standard VAT Rate: 20%
- Calculation: VAT collected (output tax) minus VAT paid (input tax)
- Due: Within 1 month and 7 days after quarter end

---

### 20. Corporation Tax

**Supabase Table**: `corporation_tax`
**Records**: 2 (annual)
**Description**: Annual corporation tax payments to HMRC

**Schema**:
```
payment_id              VARCHAR(50)  PRIMARY KEY
payment_date            DATE         NOT NULL
tax_year                VARCHAR(10)  -- 2024-25, 2025-26
taxable_profit          DECIMAL(10,2)
tax_rate                DECIMAL(5,2) -- 19% (2024-25 UK rate)
tax_amount              DECIMAL(10,2)
payment_status          VARCHAR(20)
payment_method          VARCHAR(50)  -- HMRC Online
```

**Business Context**:
- Annual Payments: £38,000 - £42,000
- Corporation Tax Rate: 19% (UK 2024-25)
- Due: 9 months and 1 day after accounting period end
- Based on taxable profit (revenue minus allowable expenses)

---

## Financial Summary

### Annual Targets (5-Person Team)

**Total Annual Revenue**: £750,000 - £1,070,000
- Permanent Placements: £350,000 - £450,000
- Temp Worker Fees: £200,000 - £250,000
- Training Services: £50,000 - £100,000
- Wellbeing Services: £20,000 - £40,000
- Assessment Services: £10,000 - £30,000
- CC Consultancy: £120,000 - £200,000

**Total Annual Costs**: £525,000 - £665,000
- Personnel (staff + temps): £350,000 - £450,000 (67%)
- Office & Facilities: £85,000 - £95,000 (14%)
- Technology: £45,000 - £55,000 (8%)
- Other Costs: £45,000 - £65,000 (11%)

**Net Profit Target**: £225,000 - £405,000 (30-40% margin)

---

## Table Relationships

### Primary Foreign Keys
- `client_id` → Links invoices to client records
- `employee_id` → Links salaries and expenses to staff members
- `worker_id` → Links temp payroll to worker records

### Common Query Patterns
- Join invoices with client data for profitability analysis
- Join temp invoices with payroll for margin calculation
- Aggregate by date ranges (weekly, monthly, quarterly, annual)
- Filter by payment_status for cash flow analysis

---

## Data Quality Notes

### Date Formats
- All dates: `YYYY-MM-DD` format
- Time Period: 2024-2026
- Payment status transitions: Paid (before Nov 2024), Outstanding (Nov 2024 - Feb 2025), Projected (March 2025+)

### Currency Format
- All amounts: Decimal(10,2) - two decimal places
- No currency symbols in data
- All values in GBP (£)

### ID Conventions
- Invoice IDs: `INV-[TYPE]-[YEAR]-[NUM]` (e.g., INV-PERM-2024-001)
- Client IDs: `CLT-[NUM]` (e.g., CLT-042)
- Employee IDs: `EMP-[NUM]` (e.g., EMP-003)
- Expense IDs: `[TYPE]-[DATE]-[NUM]` (e.g., BANK-20240101-000)

---

*Reference Document Version 1.0*
*Last Updated: 2025-11-02*
