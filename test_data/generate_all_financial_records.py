"""
ProActive People - Comprehensive Financial Test Data Generator
Generates 50 records per category for all financial transaction types
Based on UK recruitment agency operations 2024-2025
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Create output directory
output_dir = Path("d:/Recruitment/test_data/financial_records")
output_dir.mkdir(parents=True, exist_ok=True)

# Helper functions
def random_date(start, end):
    """Generate random date between start and end"""
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def add_days(date, days):
    """Add days to a date"""
    return date + timedelta(days=days)

# Generate Wellbeing Service Invoices
def generate_wellbeing_invoices():
    data = []
    base_date = datetime(2024, 1, 1)

    clients = [
        ("CLT-100", "Stressed Corp"), ("CLT-101", "Burnout Solutions"),
        ("CLT-102", "Employee Care Ltd"), ("CLT-103", "Wellness First"),
        ("CLT-104", "Health Matters"), ("CLT-105", "Support Services"),
        ("CLT-106", "Team Wellbeing"), ("CLT-107", "Work Life Balance"),
        ("CLT-108", "Mental Health Pro"), ("CLT-109", "Care Solutions")
    ]

    service_types = [
        ("Individual Session", 150, 1),
        ("Individual Session", 200, 1),
        ("Package - 5 Sessions", 750, 5),
        ("Package - 10 Sessions", 1400, 10),
        ("Employer Package - Small", 2500, 8),
        ("Employer Package - Medium", 5000, 15),
        ("Employer Package - Large", 10000, 30),
        ("Return to Work Support", 1200, 6)
    ]

    for i in range(1, 51):
        inv_date = base_date + timedelta(days=i*7)
        client = random.choice(clients)
        service = random.choice(service_types)
        status = "Paid" if inv_date < datetime(2024, 11, 1) else "Outstanding" if inv_date < datetime(2025, 3, 1) else "Projected"

        due_date = inv_date + timedelta(days=30)
        paid_date = due_date + timedelta(days=random.randint(-5, 10)) if status == "Paid" else ""

        data.append({
            "invoice_id": f"INV-WELL-{inv_date.year}-{i:03d}",
            "invoice_date": inv_date.strftime("%Y-%m-%d"),
            "client_id": client[0],
            "client_name": client[1],
            "service_type": service[0],
            "sessions_included": service[2],
            "total_amount": f"{service[1]:.2f}",
            "invoice_status": status,
            "payment_due_date": due_date.strftime("%Y-%m-%d"),
            "payment_received_date": paid_date if paid_date else "",
            "therapist": "Emma Jane",
            "notes": "Free initial consultation completed" if service[2] > 1 else "Single session"
        })

    with open(output_dir / "04_wellbeing_service_invoices.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated wellbeing_service_invoices.csv")

# Generate Assessment Service Invoices
def generate_assessment_invoices():
    data = []
    base_date = datetime(2024, 1, 1)

    assessment_types = [
        ("Per-Candidate Assessment", 75, 1),
        ("Per-Candidate Assessment", 120, 1),
        ("Per-Candidate Assessment", 180, 1),
        ("Manager Profiling", 350, 1),
        ("Manager Profiling", 450, 1),
        ("Bespoke Assessment Design", 2500, 5),
        ("Bespoke Assessment Design", 4000, 8),
        ("Team Assessment Package", 1800, 10)
    ]

    for i in range(1, 51):
        inv_date = base_date + timedelta(days=i*7)
        assessment = random.choice(assessment_types)
        candidates = random.randint(1, assessment[2])
        amount = assessment[1] * candidates

        status = "Paid" if inv_date < datetime(2024, 11, 1) else "Outstanding" if inv_date < datetime(2025, 3, 1) else "Projected"
        due_date = inv_date + timedelta(days=30)
        paid_date = due_date + timedelta(days=random.randint(-5, 8)) if status == "Paid" else ""

        data.append({
            "invoice_id": f"INV-ASMT-{inv_date.year}-{i:03d}",
            "invoice_date": inv_date.strftime("%Y-%m-%d"),
            "client_id": f"CLT-{110+i%20:03d}",
            "assessment_type": assessment[0],
            "number_of_candidates": candidates,
            "price_per_assessment": f"{assessment[1]:.2f}",
            "total_amount": f"{amount:.2f}",
            "invoice_status": status,
            "payment_due_date": due_date.strftime("%Y-%m-%d"),
            "payment_received_date": paid_date if paid_date else ""
        })

    with open(output_dir / "05_assessment_service_invoices.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated assessment_service_invoices.csv")

# Generate Contact Centre Consultancy Invoices
def generate_consultancy_invoices():
    data = []
    projects = [
        ("Setup Project", 45000, 90),
        ("Setup Project", 75000, 120),
        ("Setup Project", 95000, 150),
        ("Expansion Consultancy", 25000, 60),
        ("Expansion Consultancy", 42000, 90),
        ("Turnaround Project", 35000, 75),
        ("Turnaround Project", 68000, 120),
        ("Monthly Advisory Retainer", 8000, 30),
        ("Monthly Advisory Retainer", 15000, 30)
    ]

    base_date = datetime(2024, 1, 1)

    for i in range(1, 51):
        project = random.choice(projects)
        start_date = base_date + timedelta(days=i*15)
        completion_date = start_date + timedelta(days=project[2])
        inv_date = completion_date if "Retainer" not in project[0] else start_date + timedelta(days=30*((i-1)%12))

        status = "Paid" if inv_date < datetime(2024, 11, 1) else "Outstanding" if inv_date < datetime(2025, 3, 1) else "Projected"
        due_date = inv_date + timedelta(days=45)  # Longer payment terms for consultancy
        paid_date = due_date + timedelta(days=random.randint(-10, 15)) if status == "Paid" else ""

        data.append({
            "invoice_id": f"INV-CONS-{inv_date.year}-{i:03d}",
            "invoice_date": inv_date.strftime("%Y-%m-%d"),
            "client_id": f"CLT-{130+i%15:03d}",
            "project_type": project[0],
            "project_start_date": start_date.strftime("%Y-%m-%d"),
            "project_duration_days": project[2],
            "total_amount": f"{project[1]:.2f}",
            "invoice_status": status,
            "payment_due_date": due_date.strftime("%Y-%m-%d"),
            "payment_received_date": paid_date if paid_date else "",
            "consultant": "Contact Centre Specialist"
        })

    with open(output_dir / "06_contact_centre_consultancy_invoices.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated contact_centre_consultancy_invoices.csv")

# Generate Staff Salaries
def generate_staff_salaries():
    data = []

    staff = [
        ("EMP-001", "Managing Director", 60000, 5000, 0),
        ("EMP-002", "Temp Consultant & CC Specialist", 45000, 3750, 0),
        ("EMP-003", "Resourcer/Admin/Tech Lead", 28000, 2333.33, 0),
        ("EMP-004", "Compliance Officer & Wellbeing", 38000, 3166.67, 0),
        ("EMP-005", "Finance & Training Lead", 42000, 3500, 0)
    ]

    for month in range(1, 25):  # 24 months 2024-2025
        if month <= 12:
            pay_date = datetime(2024, month, 28)
        else:
            pay_date = datetime(2025, month-12, 28)

        for emp in staff:
            # Calculate employer NI (13.8% in 2024, 15% from April 2025)
            ni_rate = 0.138 if pay_date < datetime(2025, 4, 1) else 0.15
            employer_ni = emp[2] / 12 * ni_rate

            # Pension contribution (3% minimum)
            pension = emp[2] / 12 * 0.03

            # Random bonus for person 1 and 2 (consultants) quarterly
            bonus = 0
            if emp[0] in ["EMP-001", "EMP-002"] and pay_date.month in [3, 6, 9, 12]:
                bonus = random.randint(2000, 8000)

            total_cost = emp[2]/12 + employer_ni + pension + bonus

            data.append({
                "payment_id": f"SAL-{pay_date.strftime('%Y%m')}-{emp[0]}",
                "payment_date": pay_date.strftime("%Y-%m-%d"),
                "employee_id": emp[0],
                "employee_name": emp[1],
                "annual_salary": f"{emp[2]:.2f}",
                "monthly_gross": f"{emp[2]/12:.2f}",
                "employer_ni": f"{employer_ni:.2f}",
                "employer_pension": f"{pension:.2f}",
                "bonus": f"{bonus:.2f}",
                "total_cost": f"{total_cost:.2f}",
                "payment_method": "BACS",
                "status": "Paid"
            })

    with open(output_dir / "07_staff_salaries.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:50])  # First 50 records
    print("[OK] Generated staff_salaries.csv")

# Generate Temp Worker Payroll
def generate_temp_payroll():
    data = []

    workers = [
        ("TMP-001", "John Davies", 12.00),
        ("TMP-002", "Mary Thompson", 11.44),
        ("TMP-003", "Peter Wilson", 11.44),
        ("TMP-004", "Sarah Martinez", 13.50),
        ("TMP-005", "Linda Robinson", 12.50),
        ("TMP-006", "David Garcia", 11.44),
        ("TMP-007", "Jennifer Lee", 14.00),
        ("TMP-008", "Robert Clark", 11.44),
        ("TMP-009", "Patricia Rodriguez", 13.00),
        ("TMP-010", "Michael Lewis", 14.50)
    ]

    for i in range(1, 51):
        worker = workers[i % len(workers)]
        week_ending = datetime(2024, 1, 7) + timedelta(weeks=i)
        hours = random.choice([35, 37.5, 40, 42, 45, 48])

        # Update to National Living Wage from April 2025
        hourly_rate = worker[2] if week_ending < datetime(2025, 4, 1) else 12.21

        gross_pay = hours * hourly_rate

        # PAYE tax (approximate simple calculation)
        tax = max(0, (gross_pay * 52 - 12570) / 52 * 0.20) if gross_pay * 52 > 12570 else 0

        # Employee NI (12% above threshold)
        ni_threshold = 242  # weekly
        employee_ni = max(0, (gross_pay - ni_threshold) * 0.12)

        # Employer NI
        employer_ni_rate = 0.138 if week_ending < datetime(2025, 4, 1) else 0.15
        employer_ni = max(0, (gross_pay - 175) * employer_ni_rate)

        # Pension
        pension_employee = gross_pay * 0.05
        pension_employer = gross_pay * 0.03

        net_pay = gross_pay - tax - employee_ni - pension_employee

        data.append({
            "payroll_id": f"PAY-{week_ending.strftime('%Y%m%d')}-{worker[0]}",
            "week_ending": week_ending.strftime("%Y-%m-%d"),
            "worker_id": worker[0],
            "worker_name": worker[1],
            "hours_worked": hours,
            "hourly_rate": f"{hourly_rate:.2f}",
            "gross_pay": f"{gross_pay:.2f}",
            "paye_tax": f"{tax:.2f}",
            "employee_ni": f"{employee_ni:.2f}",
            "pension_employee": f"{pension_employee:.2f}",
            "net_pay": f"{net_pay:.2f}",
            "employer_ni": f"{employer_ni:.2f}",
            "pension_employer": f"{pension_employer:.2f}",
            "total_cost": f"{gross_pay + employer_ni + pension_employer:.2f}",
            "payment_date": (week_ending + timedelta(days=3)).strftime("%Y-%m-%d"),
            "status": "Paid"
        })

    with open(output_dir / "08_temp_worker_payroll.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated temp_worker_payroll.csv")

# Generate Office Rent & Facilities
def generate_office_costs():
    data = []

    # Bristol office: 1,200 sq ft @ £42.50/sq ft = £51,000/year = £4,250/month
    # Weston office: 600 sq ft @ £25/sq ft = £15,000/year = £1,250/month

    months = []
    for month in range(1, 25):
        if month <= 12:
            months.append(datetime(2024, month, 1))
        else:
            months.append(datetime(2025, month-12, 1))

    for i, month in enumerate(months[:50]):
        # Bristol rent
        data.append({
            "expense_id": f"RENT-BRS-{month.strftime('%Y%m')}",
            "expense_date": month.strftime("%Y-%m-%d"),
            "office_location": "Bristol Office",
            "expense_type": "Rent",
            "square_feet": 1200,
            "price_per_sqft": 42.50,
            "amount": 4250.00,
            "payment_status": "Paid",
            "payment_method": "Direct Debit",
            "notes": "Monthly rent - prime location"
        })

        # Weston rent
        data.append({
            "expense_id": f"RENT-WST-{month.strftime('%Y%m')}",
            "expense_date": month.strftime("%Y-%m-%d"),
            "office_location": "Weston Office",
            "expense_type": "Rent",
            "square_feet": 600,
            "price_per_sqft": 25.00,
            "amount": 1250.00,
            "payment_status": "Paid",
            "payment_method": "Direct Debit",
            "notes": "Monthly rent - secondary office"
        })

        # Service charges Bristol
        data.append({
            "expense_id": f"SRVC-BRS-{month.strftime('%Y%m')}",
            "expense_date": month.strftime("%Y-%m-%d"),
            "office_location": "Bristol Office",
            "expense_type": "Service Charge",
            "square_feet": 1200,
            "price_per_sqft": 5.00,
            "amount": 500.00,
            "payment_status": "Paid",
            "payment_method": "Direct Debit",
            "notes": "Monthly service charge"
        })

    with open(output_dir / "09_office_rent_facilities.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:50])
    print("[OK] Generated office_rent_facilities.csv")

# Generate Technology Subscriptions
def generate_technology_costs():
    data = []

    subscriptions = [
        ("Bullhorn ATS", 650.00, "monthly", "Software"),
        ("Broadbean Multi-Posting", 450.00, "monthly", "Software"),
        ("LinkedIn Recruiter (3 licenses)", 850.00, "monthly", "Software"),
        ("Microsoft 365 (5 users)", 95.00, "monthly", "Software"),
        ("Website Hosting", 45.00, "monthly", "Hosting"),
        ("Jotform Professional", 35.00, "monthly", "Software"),
        ("Xero Accounting", 55.00, "monthly", "Software"),
        ("Payroll Software", 120.00, "monthly", "Software")
    ]

    months = []
    for month in range(1, 25):
        if month <= 12:
            months.append(datetime(2024, month, 1))
        else:
            months.append(datetime(2025, month-12, 1))

    record_count = 0
    for month in months:
        if record_count >= 50:
            break
        for sub in subscriptions:
            if record_count >= 50:
                break
            data.append({
                "expense_id": f"TECH-{month.strftime('%Y%m')}-{sub[0][:10].replace(' ', '-')}",
                "expense_date": month.strftime("%Y-%m-%d"),
                "service_name": sub[0],
                "category": sub[3],
                "billing_cycle": sub[1],
                "amount": f"{sub[1]:.2f}",
                "payment_status": "Paid",
                "payment_method": "Credit Card",
                "auto_renew": "Yes"
            })
            record_count += 1

    with open(output_dir / "10_technology_subscriptions.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated technology_subscriptions.csv")

# Run all generators
if __name__ == "__main__":
    print("Generating ProActive People Financial Test Data...")
    print("=" * 60)

    generate_wellbeing_invoices()
    generate_assessment_invoices()
    generate_consultancy_invoices()
    generate_staff_salaries()
    generate_temp_payroll()
    generate_office_costs()
    generate_technology_costs()

    print("=" * 60)
    print("[SUCCESS] Successfully generated 7 additional CSV files")
    print(f"[INFO] Output directory: {output_dir}")
    print("\n[INFO] Combined with existing files, you now have comprehensive")
    print("       financial test data across all revenue and cost categories!")
