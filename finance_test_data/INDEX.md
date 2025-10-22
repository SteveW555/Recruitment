# ProActive People - Financial Test Data Index

## Quick Navigation

📊 **[FINANCIAL_DATA_SUMMARY.md](FINANCIAL_DATA_SUMMARY.md)** - Start here! Executive summary and overview

📖 **[FINANCIAL_TEST_DATA_README.md](FINANCIAL_TEST_DATA_README.md)** - Complete documentation with field definitions

🔍 **[verify_data.py](verify_data.py)** - Run this to verify all files and see summary

---

## Generated Files (20 CSV Files, 858 Records)

### Revenue (6 files, 290 records)
| # | File | Records | Description |
|---|------|---------|-------------|
| 01 | [permanent_placement_invoices.csv](financial_records/01_permanent_placement_invoices.csv) | 50 | Permanent placement fees (15-22% of salary) |
| 02 | [temporary_worker_invoices.csv](financial_records/02_temporary_worker_invoices.csv) | 50 | Weekly temp billing (35-42% markup) |
| 03 | [training_service_invoices.csv](financial_records/03_training_service_invoices.csv) | 40 | Training programs & coaching by Stuart Pearce |
| 04 | [wellbeing_service_invoices.csv](financial_records/04_wellbeing_service_invoices.csv) | 50 | Wellbeing sessions & packages by Emma Jane |
| 05 | [assessment_service_invoices.csv](financial_records/05_assessment_service_invoices.csv) | 50 | Psychometric testing & profiling |
| 06 | [contact_centre_consultancy_invoices.csv](financial_records/06_contact_centre_consultancy_invoices.csv) | 50 | CC setup/expansion/turnaround projects |

### Costs (14 files, 568 records)
| # | File | Records | Description |
|---|------|---------|-------------|
| 07 | [staff_salaries.csv](financial_records/07_staff_salaries.csv) | 50 | 5 staff salaries + NI + pension |
| 08 | [temp_worker_payroll.csv](financial_records/08_temp_worker_payroll.csv) | 50 | Weekly temp payroll with PAYE/NI |
| 09 | [office_rent_facilities.csv](financial_records/09_office_rent_facilities.csv) | 50 | Bristol & Weston rent + service charges |
| 10 | [technology_subscriptions.csv](financial_records/10_technology_subscriptions.csv) | 50 | Bullhorn, Broadbean, LinkedIn, etc. |
| 11 | [job_board_advertising.csv](financial_records/11_job_board_advertising.csv) | 50 | Indeed, Totaljobs, CV-Library, Reed, etc. |
| 12 | [insurance_premiums.csv](financial_records/12_insurance_premiums.csv) | 10 | PI, Employers Liability, Public Liability |
| 13 | [compliance_costs.csv](financial_records/13_compliance_costs.csv) | 50 | DBS checks, GDPR, REC membership |
| 14 | [marketing_costs.csv](financial_records/14_marketing_costs.csv) | 50 | Google Ads, LinkedIn, SEO, events |
| 15 | [professional_services.csv](financial_records/15_professional_services.csv) | 50 | Accountant, legal, IT support |
| 16 | [utilities.csv](financial_records/16_utilities.csv) | 50 | Electricity, gas, water, internet, phones |
| 17 | [bank_finance_charges.csv](financial_records/17_bank_finance_charges.csv) | 50 | Bank fees, transaction charges |
| 18 | [travel_expenses.csv](financial_records/18_travel_expenses.csv) | 50 | Mileage, trains, taxis, parking, hotels |
| 19 | [vat_payments.csv](financial_records/19_vat_payments.csv) | 6 | Quarterly VAT to HMRC |
| 20 | [corporation_tax.csv](financial_records/20_corporation_tax.csv) | 2 | Annual corporation tax payments |

---

## Quick Stats

- **Total Annual Revenue**: £750,000 - £1,070,000
- **Total Annual Costs**: £525,000 - £665,000
- **Net Profit**: £225,000 - £405,000 (30-40% margin)
- **Time Period**: 2024-2026
- **Currency**: GBP (£)
- **Regulatory Compliance**: UK 2024-2025 accurate

---

## Generator Scripts

- `generate_all_financial_records.py` - Generates files 04-10 (wellbeing, assessment, consultancy, salaries, payroll, rent, tech)
- `generate_remaining_financial_records.py` - Generates files 11-20 (job boards, insurance, compliance, marketing, etc.)

---

## Verification

Run verification script:
```bash
cd d:\Recruitment\test_data
python verify_data.py
```

---

*Generated: 2025-10-21*
