# ProActive People - Financial Test Data Generation Complete

## Executive Summary

✅ **Successfully generated comprehensive financial test data** for ProActive People's recruitment automation system testing.

- **Total Files**: 20 CSV files
- **Total Records**: 858 financial transactions
- **Time Period**: 2024-2025 (with 2026 projections)
- **Categories Covered**: 20+ financial transaction types
- **Format**: CSV (ready for database import)

---

## What Was Generated

### Revenue Streams (6 Files, 290 Records)

1. **Permanent Placement Invoices** - 50 records
   - Client invoices for permanent placements
   - Fee range: £3,600 - £15,000 per placement
   - 15-22% of annual salary

2. **Temporary Worker Invoices** - 50 records
   - Weekly temp worker billing
   - 35-42% markup on worker hourly rate
   - Gross margins: £150 - £300 per week

3. **Training Service Invoices** - 40 records
   - Custom training programs delivered by Stuart Pearce
   - Range: £250 (coaching session) to £12,000 (large programs)

4. **Wellbeing Service Invoices** - 50 records
   - Individual sessions and employer packages by Emma Jane
   - Range: £150 per session to £10,000 packages

5. **Assessment Service Invoices** - 50 records
   - Psychometric testing and profiling
   - Range: £75 per candidate to £4,000 for bespoke assessments

6. **Contact Centre Consultancy Invoices** - 50 records
   - Setup, expansion, and turnaround projects
   - Range: £8,000 to £95,000 per project

---

### Cost Categories (14 Files, 568 Records)

#### Personnel (2 files, 100 records)
7. **Staff Salaries** - 50 records of 5 staff members' monthly salaries
8. **Temp Worker Payroll** - 50 weekly payroll runs with PAYE/NI deductions

#### Facilities (2 files, 100 records)
9. **Office Rent & Facilities** - Bristol and Weston offices
10. **Utilities** - Electricity, gas, water, internet, phones

#### Technology (2 files, 100 records)
11. **Technology Subscriptions** - Bullhorn, Broadbean, LinkedIn Recruiter, etc.
12. **Job Board Advertising** - Indeed, Totaljobs, CV-Library, Reed, Jobsite, Jobserve

#### Professional Services (4 files, 210 records)
13. **Insurance Premiums** - PI, Employers Liability, Public Liability, Cyber
14. **Compliance Costs** - DBS checks, GDPR, REC membership
15. **Marketing Costs** - Google Ads, LinkedIn, SEO, events, hospitality
16. **Professional Services** - Accountant, legal advisor, IT support

#### Other Costs (4 files, 158 records)
17. **Utilities** - Electricity, gas, water, phone, internet
18. **Bank & Finance Charges** - Monthly fees, transaction costs
19. **Travel Expenses** - Mileage, trains, taxis, parking, hotels
20. **VAT Payments** - Quarterly VAT to HMRC
21. **Corporation Tax** - Annual tax payments

---

## Key Financial Values (All Based on 2024-2025 UK Market Data)

### Revenue
- **Annual Revenue Target**: £750,000 - £1,070,000
- **Revenue Per Consultant**: £150,000 - £200,000
- **Permanent Placement Average Fee**: £8,500 (18% of £47k avg salary)
- **Temp Worker Average Margin**: 38% markup

### Costs
- **Annual Total Costs**: £525,000 - £665,000
- **Personnel** (largest): £350,000 - £450,000 (67% of costs)
- **Office & Facilities**: £85,000 - £95,000 (14%)
- **Technology**: £45,000 - £55,000 (8%)
- **Other**: £45,000 - £65,000 (11%)

### Profitability
- **Net Profit Target**: £225,000 - £405,000
- **Profit Margin**: 30-40%

---

## Regulatory Compliance Reflected

All records accurately reflect UK regulations:

- **National Living Wage**: £11.44/hr (2024) → £12.21/hr (April 2025)
- **Employer NI**: 13.8% (2024) → 15% (April 2025)
- **NI Threshold**: £9,100 (2024) → £5,000 (April 2025)
- **Corporation Tax**: 19%
- **VAT**: 20% standard rate
- **Pension Auto-Enrollment**: 3% employer minimum

---

## Data Sources

1. **Internal Documentation**:
   - [STAFF_ROLES_AND_STRUCTURE.md](d:\Recruitment\docs_project\STAFF_ROLES_AND_STRUCTURE.md)
   - [RECRUITMENT_BUSINESS_UK.md](d:\Recruitment\docs_project\RECRUITMENT_BUSINESS_UK.md)
   - [PROACTIVE_PEOPLE_KNOWLEDGE_BASE.md](d:\Recruitment\docs_project\PROACTIVE_PEOPLE_KNOWLEDGE_BASE.md)

2. **External Market Data** (via web research):
   - REC (Recruitment & Employment Confederation) - Industry standards
   - Vincere - Recruitment software pricing benchmarks
   - Simplicity in Business - Recruitment finance data (£1.8bn funded)
   - Savills Bristol Office Market Report - Bristol office rents (£42.50/sq ft prime)
   - GOV.UK - Official National Living Wage and NI rates
   - ContractorUK - Contractor pay rates and IR35 calculations

3. **Industry Sources Referenced**:
   - iSmartRecruit - AI-powered recruitment platform
   - Parim - Temp worker shift management
   - Generate FS - Contractor payroll services
   - FRP Advisory - Business financial health indicators

---

## File Locations

```
d:\Recruitment\test_data\
├── FINANCIAL_TEST_DATA_README.md (Full documentation)
├── FINANCIAL_DATA_SUMMARY.md (This file)
├── generate_all_financial_records.py (Generator script 1)
├── generate_remaining_financial_records.py (Generator script 2)
├── verify_data.py (Verification script)
└── financial_records/
    ├── 01_permanent_placement_invoices.csv
    ├── 02_temporary_worker_invoices.csv
    ├── 03_training_service_invoices.csv
    ├── 04_wellbeing_service_invoices.csv
    ├── 05_assessment_service_invoices.csv
    ├── 06_contact_centre_consultancy_invoices.csv
    ├── 07_staff_salaries.csv
    ├── 08_temp_worker_payroll.csv
    ├── 09_office_rent_facilities.csv
    ├── 10_technology_subscriptions.csv
    ├── 11_job_board_advertising.csv
    ├── 12_insurance_premiums.csv
    ├── 13_compliance_costs.csv
    ├── 14_marketing_costs.csv
    ├── 15_professional_services.csv
    ├── 16_utilities.csv
    ├── 17_bank_finance_charges.csv
    ├── 18_travel_expenses.csv
    ├── 19_vat_payments.csv
    └── 20_corporation_tax.csv
```

---

## Usage

### Verification
```bash
cd d:\Recruitment\test_data
python verify_data.py
```

### Database Import
All CSV files are ready for direct import into PostgreSQL, MySQL, MongoDB, or any database system.

### Sample SQL Import (PostgreSQL)
```sql
COPY permanent_placement_invoices
FROM 'd:/Recruitment/test_data/financial_records/01_permanent_placement_invoices.csv'
CSV HEADER;
```

---

## Business Scenarios Covered

✅ **Permanent Placement Lifecycle**
- Initial invoice generation
- Payment tracking (on-time vs. late)
- Rebate period management

✅ **Temp Worker Payment Cycle**
- Weekly timesheet collection
- Payroll processing (PAYE/NI/pension)
- Client invoicing (7-14 day terms)
- Margin calculation

✅ **Multi-Service Client**
- Same client using Recruitment + Training + Wellbeing
- Cross-service revenue tracking

✅ **Cash Flow Management**
- Temp workers paid weekly (cash out)
- Clients pay 7-30 days (cash in)
- Managing the cash flow gap

✅ **Tax Compliance**
- Quarterly VAT calculations
- Annual corporation tax
- PAYE RTI submissions (temp workers)

✅ **Seasonal Variations**
- Higher temp volumes in Q4 (Christmas retail/events)
- Training programs peak in Q1 (new year planning)
- Recruitment steady throughout year

✅ **Regulatory Changes**
- April 2025 NI and living wage increases
- Accurate reflection in payroll from April 2025

---

## Next Steps for Enhancement

Optional additional datasets that could be added:

1. **Cash Flow Reports**
   - Weekly/monthly cash position
   - Aged receivables (0-30, 31-60, 61-90, 90+ days)
   - Aged payables

2. **Transaction Details**
   - Client payment receipts (when invoices actually paid)
   - Bank reconciliation records
   - Payment method breakdown

3. **Refunds & Adjustments**
   - Placement rebates (candidate left during guarantee period)
   - Credit notes issued
   - Bad debt write-offs

4. **Additional Costs**
   - Office supplies and equipment
   - Staff training and development
   - Candidate referral bonuses
   - Contractor payments (outside IR35)

5. **Analytics Data**
   - Monthly P&L statements
   - KPI tracking (placements, revenue per head)
   - Commission calculations
   - Client profitability analysis

---

## Technical Details

### CSV Format
- **Encoding**: UTF-8
- **Delimiter**: Comma (,)
- **Headers**: First row contains column names
- **Dates**: YYYY-MM-DD format
- **Currency**: Decimal format (e.g., 1234.56, no currency symbols)
- **Line Endings**: Unix-style (LF)

### Field Conventions
- **IDs**: Prefixed format (e.g., INV-PERM-2024-001, CLT-042, EMP-003)
- **Amounts**: Always 2 decimal places
- **Status**: Paid, Outstanding, Projected
- **Payment Methods**: BACS, Credit Card, Direct Debit, HMRC Online

---

## Support & Questions

For questions about this test data:
- **System**: ProActive People Recruitment Automation System
- **Phase**: Testing & Development (Q2 2025)
- **Generated**: 2025-10-21
- **Purpose**: Database seeding, system testing, financial modeling

---

## Acknowledgments

Data values derived from:
- ProActive People operational documentation
- UK recruitment industry market data (2024-2025)
- Government sources (GOV.UK, HMRC)
- Bristol property market reports
- Recruitment software vendor benchmarks

---

**Status**: ✅ Complete
**Quality**: Production-ready realistic test data
**Coverage**: Comprehensive across all financial categories
**Compliance**: UK regulations 2024-2025 accurate

---

*Generated by Claude Code on 2025-10-21*
