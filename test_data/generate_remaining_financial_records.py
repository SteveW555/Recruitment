"""
ProActive People - Additional Financial Test Data Generator
Generates remaining categories: Job boards, insurance, compliance, marketing, etc.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

output_dir = Path("d:/Recruitment/test_data/financial_records")
output_dir.mkdir(parents=True, exist_ok=True)

def generate_job_board_costs():
    """Job board advertising costs"""
    data = []
    boards = [
        ("Indeed", 800, 1200),
        ("Totaljobs", 450, 750),
        ("CV-Library", 350, 600),
        ("Reed", 400, 700),
        ("Jobsite", 300, 500),
        ("Jobserve", 250, 450)
    ]

    base_date = datetime(2024, 1, 1)
    for i in range(50):
        board = boards[i % len(boards)]
        expense_date = base_date + timedelta(days=i*7)
        amount = random.uniform(board[1], board[2])

        data.append({
            "expense_id": f"JB-{expense_date.strftime('%Y%m%d')}-{board[0][:4]}",
            "expense_date": expense_date.strftime("%Y-%m-%d"),
            "job_board": board[0],
            "service_type": "Job Credits",
            "amount": f"{amount:.2f}",
            "jobs_posted": random.randint(5, 25),
            "payment_status": "Paid" if expense_date < datetime(2024, 12, 1) else "Outstanding",
            "payment_method": "Credit Card"
        })

    with open(output_dir / "11_job_board_advertising.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated job_board_advertising.csv")

def generate_insurance_costs():
    """Insurance premiums"""
    data = []
    policies = [
        ("Professional Indemnity Insurance", 3500, 12, "Annual"),
        ("Employers Liability Insurance", 1200, 12, "Annual"),
        ("Public Liability Insurance", 850, 12, "Annual"),
        ("Office Contents Insurance", 450, 12, "Annual"),
        ("Cyber Insurance", 1800, 12, "Annual")
    ]

    for year in [2024, 2025]:
        for policy in policies:
            payment_date = datetime(year, random.randint(1, 3), random.randint(1, 28))
            data.append({
                "expense_id": f"INS-{payment_date.strftime('%Y%m')}-{policy[0][:10].replace(' ', '-')}",
                "expense_date": payment_date.strftime("%Y-%m-%d"),
                "policy_type": policy[0],
                "annual_premium": f"{policy[1]:.2f}",
                "coverage_period_months": policy[2],
                "billing_frequency": policy[3],
                "payment_status": "Paid" if year == 2024 else "Projected",
                "renewal_date": payment_date.replace(year=year+1).strftime("%Y-%m-%d"),
                "payment_method": "Direct Debit"
            })

    with open(output_dir / "12_insurance_premiums.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:50])
    print("[OK] Generated insurance_premiums.csv")

def generate_compliance_costs():
    """DBS checks, GDPR, training"""
    data = []
    base_date = datetime(2024, 1, 1)

    costs = [
        ("DBS Check - Standard", 50),
        ("DBS Check - Enhanced", 60),
        ("GDPR Compliance Software", 85),
        ("Right to Work Verification Training", 250),
        ("REC Membership", 120),
        ("Standards in Recruitment Accreditation", 800)
    ]

    for i in range(50):
        cost_type = costs[i % len(costs)]
        expense_date = base_date + timedelta(days=i*7)

        data.append({
            "expense_id": f"COMP-{expense_date.strftime('%Y%m%d')}-{i:03d}",
            "expense_date": expense_date.strftime("%Y-%m-%d"),
            "compliance_type": cost_type[0],
            "amount": f"{cost_type[1]:.2f}",
            "candidate_or_staff": "Candidate" if "DBS" in cost_type[0] else "Company",
            "payment_status": "Paid" if expense_date < datetime(2024, 12, 1) else "Outstanding",
            "payment_method": "Credit Card"
        })

    with open(output_dir / "13_compliance_costs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated compliance_costs.csv")

def generate_marketing_costs():
    """Marketing and business development"""
    data = []
    base_date = datetime(2024, 1, 1)

    marketing_items = [
        ("Google Ads", 450, "monthly"),
        ("LinkedIn Advertising", 600, "monthly"),
        ("SEO Services", 800, "monthly"),
        ("Website Maintenance", 150, "monthly"),
        ("Networking Event Fee", 125, "one-time"),
        ("Conference Attendance", 450, "one-time"),
        ("Client Hospitality", 180, "one-time"),
        ("Corporate Gifts", 220, "one-time"),
        ("Branding Design", 1200, "one-time")
    ]

    for i in range(50):
        item = marketing_items[i % len(marketing_items)]
        expense_date = base_date + timedelta(days=i*10)

        data.append({
            "expense_id": f"MKT-{expense_date.strftime('%Y%m%d')}-{i:03d}",
            "expense_date": expense_date.strftime("%Y-%m-%d"),
            "marketing_activity": item[0],
            "category": "Digital Marketing" if "Ads" in item[0] or "SEO" in item[0] or "Website" in item[0] or "LinkedIn" in item[0] else "Events & Hospitality",
            "amount": f"{item[1]:.2f}",
            "frequency": item[2],
            "payment_status": "Paid" if expense_date < datetime(2024, 12, 1) else "Outstanding",
            "payment_method": "Credit Card"
        })

    with open(output_dir / "14_marketing_costs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated marketing_costs.csv")

def generate_professional_services():
    """Accountant, legal, IT support"""
    data = []

    services = [
        ("External Accountant", 750, "monthly", "Accounting"),
        ("Legal Advisor Retainer", 450, "monthly", "Legal"),
        ("IT Support Services", 320, "monthly", "IT"),
        ("Year-End Accounts", 2500, "annual", "Accounting"),
        ("Legal Contract Review", 850, "ad-hoc", "Legal"),
        ("Network Security Audit", 1200, "annual", "IT")
    ]

    base_date = datetime(2024, 1, 1)
    for i in range(50):
        service = services[i % len(services)]
        if service[2] == "monthly":
            expense_date = base_date + timedelta(days=30*i)
        elif service[2] == "annual":
            expense_date = base_date + timedelta(days=365*(i//len(services)))
        else:
            expense_date = base_date + timedelta(days=random.randint(1, 700))

        data.append({
            "expense_id": f"PROF-{expense_date.strftime('%Y%m%d')}-{i:03d}",
            "expense_date": expense_date.strftime("%Y-%m-%d"),
            "service_name": service[0],
            "category": service[3],
            "amount": f"{service[1]:.2f}",
            "frequency": service[2],
            "payment_status": "Paid" if expense_date < datetime(2024, 12, 1) else "Outstanding",
            "payment_method": "BACS"
        })

    with open(output_dir / "15_professional_services.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:50])
    print("[OK] Generated professional_services.csv")

def generate_utilities():
    """Electricity, gas, water, internet, phones"""
    data = []

    utilities = [
        ("Electricity - Bristol", 280, 350),
        ("Gas - Bristol", 120, 180),
        ("Water - Bristol", 45, 65),
        ("Internet & Phones - Bristol", 180, 180),
        ("Electricity - Weston", 140, 180),
        ("Gas - Weston", 60, 95),
        ("Water - Weston", 25, 35),
        ("Internet & Phones - Weston", 90, 90)
    ]

    for month in range(1, 25):  # 24 months
        if month <= 12:
            bill_date = datetime(2024, month, 15)
        else:
            bill_date = datetime(2025, month-12, 15)

        for util in utilities:
            amount = random.uniform(util[1], util[2])
            data.append({
                "expense_id": f"UTIL-{bill_date.strftime('%Y%m')}-{util[0][:10].replace(' ', '-').replace('-', '')}",
                "expense_date": bill_date.strftime("%Y-%m-%d"),
                "utility_type": util[0].split(" - ")[0],
                "location": util[0].split(" - ")[1],
                "amount": f"{amount:.2f}",
                "payment_status": "Paid",
                "payment_method": "Direct Debit"
            })

    with open(output_dir / "16_utilities.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:50])
    print("[OK] Generated utilities.csv")

def generate_bank_fees():
    """Bank charges, transaction fees, factoring fees"""
    data = []
    base_date = datetime(2024, 1, 1)

    fees = [
        ("Bank Account Monthly Fee", 25),
        ("Card Transaction Fees", 85),
        ("International Payment Fee", 15),
        ("Overdraft Interest", 45),
        ("CHAPS Payment Fee", 30)
    ]

    for i in range(50):
        fee = fees[i % len(fees)]
        expense_date = base_date + timedelta(days=i*7)

        data.append({
            "expense_id": f"BANK-{expense_date.strftime('%Y%m%d')}-{i:03d}",
            "expense_date": expense_date.strftime("%Y-%m-%d"),
            "fee_type": fee[0],
            "amount": f"{fee[1]:.2f}",
            "payment_status": "Paid",
            "bank": "Business Bank Account"
        })

    with open(output_dir / "17_bank_finance_charges.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated bank_finance_charges.csv")

def generate_travel_expenses():
    """Travel, mileage, parking, accommodation"""
    data = []
    base_date = datetime(2024, 1, 1)

    for i in range(50):
        expense_date = base_date + timedelta(days=i*5)
        expense_types = [
            ("Client Visit - Mileage", random.randint(20, 150) * 0.45),  # 45p per mile
            ("Train Ticket - London", random.uniform(45, 95)),
            ("Taxi - Client Meeting", random.uniform(15, 35)),
            ("Parking", random.uniform(5, 25)),
            ("Hotel - Overnight Stay", random.uniform(80, 150)),
            ("Meals & Subsistence", random.uniform(20, 50))
        ]

        expense = random.choice(expense_types)

        data.append({
            "expense_id": f"TRVL-{expense_date.strftime('%Y%m%d')}-{i:03d}",
            "expense_date": expense_date.strftime("%Y-%m-%d"),
            "expense_type": expense[0],
            "employee_id": f"EMP-{random.randint(1,5):03d}",
            "amount": f"{expense[1]:.2f}",
            "purpose": "Client Meeting" if "Client" in expense[0] else "Business Travel",
            "reimbursement_status": "Reimbursed",
            "payment_method": "Expense Claim"
        })

    with open(output_dir / "18_travel_expenses.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("[OK] Generated travel_expenses.csv")

def generate_vat_payments():
    """Quarterly VAT payments"""
    data = []

    quarters = [
        (datetime(2024, 4, 30), 18500),
        (datetime(2024, 7, 31), 21200),
        (datetime(2024, 10, 31), 19800),
        (datetime(2025, 1, 31), 23400),
        (datetime(2025, 4, 30), 24500),
        (datetime(2025, 7, 31), 22800)
    ]

    for i, quarter in enumerate(quarters):
        data.append({
            "payment_id": f"VAT-{quarter[0].strftime('%Y-Q')}{((quarter[0].month-1)//3)+1}",
            "payment_date": quarter[0].strftime("%Y-%m-%d"),
            "quarter_ending": quarter[0].strftime("%Y-%m-%d"),
            "vat_collected": f"{quarter[1]:.2f}",
            "vat_paid": f"{quarter[1]*0.65:.2f}",
            "net_vat_due": f"{quarter[1]*0.35:.2f}",
            "payment_status": "Paid" if quarter[0] < datetime(2024, 12, 1) else "Projected",
            "payment_method": "HMRC Online"
        })

    with open(output_dir / "19_vat_payments.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:50])
    print("[OK] Generated vat_payments.csv")

def generate_corporation_tax():
    """Annual corporation tax payments"""
    data = []

    tax_years = [
        ("2023-24", datetime(2024, 9, 30), 38000),
        ("2024-25", datetime(2025, 9, 30), 42000)
    ]

    for year in tax_years:
        data.append({
            "payment_id": f"CTAX-{year[0]}",
            "tax_year": year[0],
            "payment_date": year[1].strftime("%Y-%m-%d"),
            "taxable_profit": f"{year[2]/0.19:.2f}",
            "tax_rate": "19%",
            "tax_due": f"{year[2]:.2f}",
            "payment_status": "Paid" if year[1] < datetime(2025, 1, 1) else "Projected",
            "payment_method": "HMRC Online"
        })

    with open(output_dir / "20_corporation_tax.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:50])
    print("[OK] Generated corporation_tax.csv")

if __name__ == "__main__":
    print("\nGenerating Additional Financial Records...")
    print("=" * 60)

    generate_job_board_costs()
    generate_insurance_costs()
    generate_compliance_costs()
    generate_marketing_costs()
    generate_professional_services()
    generate_utilities()
    generate_bank_fees()
    generate_travel_expenses()
    generate_vat_payments()
    generate_corporation_tax()

    print("=" * 60)
    print("[SUCCESS] Generated 10 additional CSV files")
    print(f"[INFO] Total financial record categories: 20+")
