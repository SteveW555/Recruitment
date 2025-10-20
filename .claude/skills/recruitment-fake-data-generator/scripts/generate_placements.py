#!/usr/bin/env python3
"""
Generate fake placement/hire data for recruitment system testing.
Links candidates to jobs and clients with realistic placement details.
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def load_csv(filepath: str, name: str) -> List[Dict]:
    """Load data from CSV file."""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        print(f"Loaded {len(data)} {name} from {filepath}")
    except FileNotFoundError:
        print(f"Error: {name} file {filepath} not found!")
        exit(1)
    return data

def generate_placement_date(job_posted_date: str) -> str:
    """Generate placement date after job was posted."""
    posted = datetime.strptime(job_posted_date, "%Y-%m-%d")
    # Placement typically 2-8 weeks after posting
    days_after = random.randint(14, 56)
    placement = posted + timedelta(days=days_after)

    # Don't place in the future
    today = datetime.now()
    if placement > today:
        placement = today - timedelta(days=random.randint(0, 30))

    return placement.strftime("%Y-%m-%d")

def generate_start_date(placement_date: str, notice_period: str) -> str:
    """Generate start date based on placement and notice period."""
    placement = datetime.strptime(placement_date, "%Y-%m-%d")

    # Add notice period
    if notice_period == "Immediate":
        days_after = random.randint(3, 14)
    elif notice_period == "1 week":
        days_after = random.randint(7, 14)
    elif notice_period == "2 weeks":
        days_after = random.randint(14, 21)
    elif notice_period == "1 month":
        days_after = random.randint(28, 35)
    elif notice_period == "2 months":
        days_after = random.randint(56, 65)
    elif notice_period == "3 months":
        days_after = random.randint(84, 95)
    else:
        days_after = random.randint(14, 35)

    start = placement + timedelta(days=days_after)
    return start.strftime("%Y-%m-%d")

def generate_end_date(start_date: str, contract_type: str, duration: str) -> str:
    """Generate end date for temporary/contract roles."""
    if contract_type == "Permanent":
        return "N/A"

    start = datetime.strptime(start_date, "%Y-%m-%d")

    if duration:
        # Parse duration
        if "3 month" in duration:
            days = 90
        elif "6 month" in duration:
            days = 180
        elif "12 month" in duration:
            days = 365
        elif "18 month" in duration:
            days = 547
        else:
            days = 180  # Default 6 months
    else:
        days = random.choice([90, 180, 365])

    end = start + timedelta(days=days)
    return end.strftime("%Y-%m-%d")

def calculate_fee(salary: float, fee_percentage: float, contract_type: str) -> float:
    """Calculate placement fee."""
    if contract_type == "Permanent":
        # Percentage of annual salary
        return round(salary * (fee_percentage / 100), 2)
    else:
        # Temp/Contract: calculate based on expected duration value
        # Simplified: 10-15% of contract value
        return round(salary * random.uniform(0.10, 0.15), 2)

def generate_invoice_date(placement_date: str, start_date: str) -> str:
    """Generate invoice date (typically after start date or on placement)."""
    if random.random() < 0.6:  # 60% invoiced on start
        return start_date
    else:  # 40% invoiced on placement
        return placement_date

def generate_follow_up_date(start_date: str, status: str) -> str:
    """Generate follow-up date (typically 1-3 months after start)."""
    if status == "Cancelled":
        return ""

    start = datetime.strptime(start_date, "%Y-%m-%d")
    days_after = random.randint(30, 90)
    follow_up = start + timedelta(days=days_after)

    return follow_up.strftime("%Y-%m-%d")

def generate_feedback() -> tuple:
    """Generate candidate and client feedback."""
    candidate_feedback_options = [
        "Very happy with the role and company culture",
        "Enjoying the role, good team fit",
        "Positive feedback, settling in well",
        "Exceeded expectations, very satisfied",
        "Good start, adapting to role",
        "Happy with the opportunity",
        ""
    ]

    client_feedback_options = [
        "Excellent candidate, performing well",
        "Very satisfied with the placement",
        "Good hire, meeting expectations",
        "Strong performer, valuable addition",
        "Positive feedback from team",
        "Happy with candidate selection",
        ""
    ]

    return random.choice(candidate_feedback_options), random.choice(client_feedback_options)

def generate_placement(placement_id: int, candidates: List[Dict], jobs: List[Dict],
                      clients: List[Dict]) -> Optional[Dict]:
    """Generate a single fake placement record."""

    # Select a job (prefer Open or recently Filled jobs)
    open_jobs = [j for j in jobs if j["Job Status"] in ["Open", "Filled"]]
    if not open_jobs:
        open_jobs = jobs

    job = random.choice(open_jobs)

    # Find matching client
    client = next((c for c in clients if c["Client ID"] == job["Client ID"]), None)
    if not client:
        # Can't create placement without client
        return None

    # Select a candidate (prefer Active candidates)
    active_candidates = [c for c in candidates if c["Status"] == "Active"]
    if not active_candidates:
        active_candidates = candidates

    candidate = random.choice(active_candidates)

    # Extract details
    placement_id_str = f"PLC-{placement_id:03d}"
    candidate_id = candidate["Candidate ID"]
    job_id = job["Job ID"]
    client_id = client["Client ID"]

    job_title = job["Job Title"]
    contract_type = job["Contract Type"]
    contract_duration = job.get("Contract Duration", "")

    # Salary/Rate
    salary_min = int(job["Salary Min (£)"])
    salary_max = int(job["Salary Max (£)"])
    salary = random.randint(salary_min, salary_max)

    if contract_type == "Permanent":
        salary_type = "Annual"
    elif contract_type == "Contract":
        # Convert to daily rate
        salary = round(salary / 220)  # Approx 220 working days
        salary_type = "Daily"
    else:  # Temporary
        salary_type = "Annual"

    # Fee details
    fee_percentage = float(job["Fee Percentage"])
    fee_amount = calculate_fee(salary, fee_percentage, contract_type)

    # Dates
    placement_date = generate_placement_date(job["Posted Date"])
    notice_period = candidate.get("Notice Period", "1 month")
    start_date = generate_start_date(placement_date, notice_period)
    end_date = generate_end_date(start_date, contract_type, contract_duration)

    expected_duration = contract_duration if contract_duration else ("Ongoing" if contract_type == "Permanent" else "6 months")

    invoice_date = generate_invoice_date(placement_date, start_date)

    # Payment status
    payment_status_options = ["Paid", "Paid", "Paid", "Outstanding", "Overdue"]
    payment_status = random.choice(payment_status_options)

    # Terms
    rebate_period = int(client.get("Rebate Period Days", 90))
    rebate_applicable = "Yes"

    # Check if placement failed (small chance)
    if random.random() < 0.05:  # 5% fail
        placement_status = "Rebated"
        rebate_applicable = "No"  # Already rebated
    elif random.random() < 0.03:  # 3% cancelled before start
        placement_status = "Cancelled"
        end_date = start_date
    elif end_date != "N/A":
        # Temp/contract
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        if end_datetime < datetime.now():
            placement_status = "Completed"
        else:
            placement_status = "Active"
    else:
        # Permanent
        placement_status = "Active"

    probation = random.choice(["3 months", "6 months"])

    # Follow-up
    follow_up_date = generate_follow_up_date(start_date, placement_status)

    # Feedback
    if placement_status in ["Active", "Completed"]:
        candidate_feedback, client_feedback = generate_feedback()
    else:
        candidate_feedback = "N/A"
        client_feedback = "N/A"

    # Consultant
    consultant = job.get("Assigned Consultant", "Sam Henderson")

    # Notes
    notes_templates = [
        f"Smooth placement process. Client and candidate both very happy",
        f"Excellent match. {random.choice(['Quick', 'Standard', 'Extended'])} onboarding period",
        f"Candidate {random.choice(['exceeded', 'met', 'performing to'])} expectations",
        f"Strong hire. Client seeking similar profiles",
        f"{random.choice(['Straightforward', 'Complex', 'Challenging'])} placement. Good outcome",
        f"Candidate settled quickly. Positive feedback from both parties",
        f"Client impressed with {random.choice(['technical skills', 'cultural fit', 'experience', 'attitude'])}",
        f"Successful placement. Follow-up scheduled for {random.randint(1,3)} months",
        ""
    ]

    if placement_status == "Rebated":
        notes = "Candidate left within rebate period. Full rebate issued to client"
    elif placement_status == "Cancelled":
        notes = "Placement cancelled before start date. No fee charged"
    else:
        notes = random.choice(notes_templates)

    return {
        "Placement ID": placement_id_str,
        "Candidate ID": candidate_id,
        "Job ID": job_id,
        "Client ID": client_id,
        "Job Title": job_title,
        "Contract Type": contract_type,
        "Placement Date": placement_date,
        "Start Date": start_date,
        "End Date": end_date,
        "Expected Duration": expected_duration,
        "Salary/Rate": salary,
        "Salary Type": salary_type,
        "Fee Amount (£)": fee_amount,
        "Fee Percentage": fee_percentage,
        "Invoice Date": invoice_date,
        "Payment Status": payment_status,
        "Rebate Period Days": rebate_period,
        "Rebate Applicable": rebate_applicable,
        "Guarantee Period Days": rebate_period,
        "Probation Period": probation,
        "Placement Status": placement_status,
        "Follow-up Date": follow_up_date,
        "Candidate Feedback": candidate_feedback,
        "Client Feedback": client_feedback,
        "Consultant": consultant,
        "Notes": notes
    }

def main():
    parser = argparse.ArgumentParser(description="Generate fake placement data")
    parser.add_argument("--count", type=int, default=50, help="Number of placements to generate")
    parser.add_argument("--output", type=str, default="fake_placements.csv", help="Output CSV filename")
    parser.add_argument("--candidates", type=str, required=True, help="Path to candidates CSV file (required)")
    parser.add_argument("--jobs", type=str, required=True, help="Path to jobs CSV file (required)")
    parser.add_argument("--clients", type=str, required=True, help="Path to clients CSV file (required)")

    args = parser.parse_args()

    # Load required data
    candidates = load_csv(args.candidates, "candidates")
    jobs = load_csv(args.jobs, "jobs")
    clients = load_csv(args.clients, "clients")

    print(f"Generating {args.count} fake placement records...")

    placements = []
    for i in range(1, args.count + 1):
        placement = generate_placement(i, candidates, jobs, clients)
        if placement:
            placements.append(placement)

    if not placements:
        print("Error: No placements could be generated. Check your input files.")
        return

    # Write to CSV
    fieldnames = list(placements[0].keys())
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(placements)

    print(f"[OK] Generated {len(placements)} placements")
    print(f"[OK] Saved to {args.output}")

    # Print summary stats
    contract_types = {}
    statuses = {}
    for placement in placements:
        contract_type = placement["Contract Type"]
        contract_types[contract_type] = contract_types.get(contract_type, 0) + 1
        status = placement["Placement Status"]
        statuses[status] = statuses.get(status, 0) + 1

    print("\nContract Type Distribution:")
    for ct, count in sorted(contract_types.items()):
        print(f"  {ct}: {count} ({count/len(placements)*100:.1f}%)")

    print("\nPlacement Status Distribution:")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count} ({count/len(placements)*100:.1f}%)")

    # Calculate total fees
    total_fees = sum(float(p["Fee Amount (£)"]) for p in placements)
    print(f"\nTotal Placement Fees: £{total_fees:,.2f}")

if __name__ == "__main__":
    main()
