#!/usr/bin/env python3
"""
Generate fake job posting data for recruitment system testing.
Can reference existing clients from a clients CSV file or generate standalone.
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Import client data if available
def load_clients(client_file: str) -> List[Dict]:
    """Load existing clients from CSV file."""
    clients = []
    try:
        with open(client_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            clients = list(reader)
        print(f"Loaded {len(clients)} clients from {client_file}")
    except FileNotFoundError:
        print(f"Warning: Client file {client_file} not found. Will generate standalone jobs.")
    return clients

JOB_TITLES = {
    "Technical": [
        ("Software Developer", "Develop and maintain software applications using modern frameworks"),
        ("Senior Software Engineer", "Lead development projects and mentor junior developers"),
        ("IT Support Analyst", "Provide technical support to end users and resolve IT issues"),
        ("DevOps Engineer", "Build and maintain CI/CD pipelines and cloud infrastructure"),
        ("Cloud Engineer", "Design and implement cloud-based solutions on AWS/Azure"),
        ("Systems Administrator", "Manage and maintain server infrastructure and networks"),
        ("Data Analyst", "Analyze data and create insights for business decision-making"),
        ("Network Engineer", "Design, implement and support network infrastructure"),
        ("Cybersecurity Analyst", "Monitor and protect systems from security threats"),
        ("Technical Lead", "Lead technical teams and oversee project delivery"),
        ("Full Stack Developer", "Develop both frontend and backend applications"),
        ("QA Engineer", "Test software and ensure quality standards are met"),
        ("Database Administrator", "Manage database systems and ensure data integrity"),
        ("Solutions Architect", "Design technical solutions for client requirements"),
    ],
    "Sales": [
        ("Sales Executive", "Generate new business and manage sales pipeline"),
        ("Business Development Manager", "Identify and pursue new business opportunities"),
        ("Account Manager", "Manage key client relationships and drive revenue growth"),
        ("Telesales Executive", "Make outbound calls to generate sales leads"),
        ("Field Sales Manager", "Manage territory and conduct face-to-face sales meetings"),
        ("Key Account Manager", "Manage strategic client relationships"),
        ("Sales Director", "Lead sales team and drive commercial strategy"),
        ("Inside Sales Representative", "Conduct remote sales activities and build pipeline"),
        ("Sales Team Leader", "Manage and coach sales team to achieve targets"),
    ],
    "Contact Centre": [
        ("Customer Service Advisor", "Handle customer inquiries and resolve issues"),
        ("Call Centre Agent", "Answer inbound calls and provide excellent service"),
        ("Technical Support Agent", "Provide technical support via phone and email"),
        ("Team Leader", "Supervise team of advisors and ensure quality standards"),
        ("Contact Centre Manager", "Manage operations and drive performance improvements"),
        ("Quality Analyst", "Monitor calls and ensure quality standards are maintained"),
        ("Customer Service Manager", "Lead customer service team and improve satisfaction"),
    ],
    "Accountancy": [
        ("Accounts Assistant", "Support accounts team with day-to-day bookkeeping"),
        ("Accountant", "Prepare financial statements and manage accounts"),
        ("Senior Accountant", "Oversee accounting operations and mentor junior staff"),
        ("Management Accountant", "Provide management information and financial analysis"),
        ("Financial Controller", "Oversee all financial operations and reporting"),
        ("Finance Manager", "Manage finance team and financial planning"),
        ("Tax Accountant", "Prepare tax returns and provide tax advice"),
        ("Payroll Administrator", "Process payroll and manage employee benefits"),
        ("Credit Controller", "Manage debt collection and cash flow"),
    ],
    "Commercial": [
        ("Administrator", "Provide administrative support to the team"),
        ("Office Manager", "Manage office operations and facilities"),
        ("Executive Assistant", "Provide high-level support to senior executives"),
        ("Operations Manager", "Oversee daily operations and drive efficiency"),
        ("HR Administrator", "Support HR team with admin and recruitment"),
        ("Project Manager", "Manage projects from initiation to completion"),
        ("Business Analyst", "Analyze business processes and recommend improvements"),
        ("Facilities Manager", "Manage building facilities and vendor relationships"),
        ("Procurement Manager", "Manage procurement activities and supplier relationships"),
    ]
}

REQUIRED_SKILLS = {
    "Technical": ["Python", "Java", "AWS", "Azure", "Docker", "Kubernetes", "SQL", "JavaScript", "React", "Node.js", ".NET", "Linux", "Networking", "Security"],
    "Sales": ["B2B Sales", "CRM", "Salesforce", "Lead Generation", "Negotiation", "Account Management", "Cold Calling", "Presentation Skills"],
    "Contact Centre": ["Customer Service", "CRM Systems", "Call Handling", "Multi-tasking", "Problem Solving", "Communication"],
    "Accountancy": ["Sage", "Xero", "Excel", "Financial Reporting", "VAT", "Payroll", "Tax", "Bookkeeping"],
    "Commercial": ["Microsoft Office", "Administration", "Communication", "Organization", "Project Management", "Excel"]
}

BENEFITS = [
    "Pension", "Healthcare", "25 Days Holiday", "Bonus Scheme", "Flexible Working",
    "Professional Development", "Gym Membership", "Life Insurance", "Income Protection",
    "Car Allowance", "Parking", "Work from Home", "Training Budget", "Career Progression"
]

WORK_MODELS = ["Office", "Hybrid", "Remote"]

def generate_job_id(index: int) -> str:
    """Generate job ID."""
    return f"JOB-{index:03d}"

def generate_posted_date(days_ago_max: int = 60) -> str:
    """Generate job posted date within last X days."""
    today = datetime.now()
    days_ago = random.randint(0, days_ago_max)
    posted = today - timedelta(days=days_ago)
    return posted.strftime("%Y-%m-%d")

def generate_deadline(posted_date: str) -> str:
    """Generate application deadline (2-8 weeks after posting)."""
    posted = datetime.strptime(posted_date, "%Y-%m-%d")
    days_ahead = random.randint(14, 56)
    deadline = posted + timedelta(days=days_ahead)
    return deadline.strftime("%Y-%m-%d")

def generate_start_date() -> str:
    """Generate job start date."""
    options = ["ASAP", "Flexible", "Flexible"]
    if random.random() < 0.7:
        return random.choice(options)
    else:
        today = datetime.now()
        days_ahead = random.randint(30, 90)
        start = today + timedelta(days=days_ahead)
        return start.strftime("%Y-%m-%d")

def generate_job(job_id: int, client: Optional[Dict] = None, sector_filter: Optional[List[str]] = None) -> Dict:
    """Generate a single fake job record."""

    # Determine specialty
    if client:
        client_id = client["Client ID"]
        industry = client["Industry Sector"]
        specialties = [s.strip() for s in client["Recruitment Specialties"].split(",")]
        work_models = [w.strip() for w in client["Work Models Offered"].split(",")]
        salary_range = client["Typical Salary Range"]
        fee_pct = float(client["Average Fee Percentage"])
        location_city = client["City"]
        location_county = client["County"]
        postcode_area = client["Postcode"][:3].strip()
        client_tier = client["Account Tier"]
    else:
        # Standalone job
        client_id = f"CLI-{random.randint(1, 50):03d}"
        specialties = ["Technical", "Sales", "Contact Centre", "Accountancy", "Commercial"]
        industry = "Various"
        work_models = ["Office", "Hybrid", "Remote"]
        salary_range = "£25000-£55000"
        fee_pct = random.randint(15, 20)
        location_city = "Bristol"
        location_county = "Bristol"
        postcode_area = "BS1"
        client_tier = "Gold"

    # Filter by sector if specified
    if sector_filter:
        specialties = [s for s in specialties if s in sector_filter]
        if not specialties:
            specialties = sector_filter

    specialty = random.choice(specialties)

    # Select job title and description
    title, description = random.choice(JOB_TITLES[specialty])

    # Department
    department_map = {
        "Technical": "IT",
        "Sales": "Sales",
        "Contact Centre": "Customer Service",
        "Accountancy": "Finance",
        "Commercial": random.choice(["Operations", "Administration", "HR"])
    }
    department = department_map[specialty]

    # Work model
    work_model = random.choice(work_models)
    if work_model == "Hybrid":
        hybrid_details = random.choice(["3 days office, 2 days home", "2 days office, 3 days home", "Flexible arrangement"])
    else:
        hybrid_details = ""

    # Salary
    if client:
        # Parse client salary range
        try:
            salary_parts = salary_range.replace("£", "").split("-")
            salary_min = int(salary_parts[0])
            salary_max = int(salary_parts[1])
        except:
            salary_min = 25000
            salary_max = 55000
    else:
        if specialty == "Technical":
            salary_min = random.randint(25, 45) * 1000
            salary_max = salary_min + random.randint(15, 25) * 1000
        elif specialty == "Accountancy":
            salary_min = random.randint(22, 35) * 1000
            salary_max = salary_min + random.randint(12, 20) * 1000
        elif specialty == "Sales":
            salary_min = random.randint(22, 35) * 1000
            salary_max = salary_min + random.randint(15, 25) * 1000
        elif specialty == "Contact Centre":
            salary_min = random.randint(18, 24) * 1000
            salary_max = salary_min + random.randint(6, 12) * 1000
        else:  # Commercial
            salary_min = random.randint(20, 30) * 1000
            salary_max = salary_min + random.randint(10, 18) * 1000

    salary_type = "Annual"

    # Benefits
    num_benefits = random.randint(3, 7)
    benefits = ", ".join(random.sample(BENEFITS, num_benefits))

    # Requirements
    if "Senior" in title or "Manager" in title or "Director" in title or "Lead" in title:
        exp_years = random.randint(5, 10)
    elif "Junior" in title or "Assistant" in title:
        exp_years = random.randint(0, 2)
    else:
        exp_years = random.randint(2, 5)

    # Skills
    skill_pool = REQUIRED_SKILLS[specialty]
    num_skills = random.randint(4, 8)
    required_skills = ", ".join(random.sample(skill_pool, min(num_skills, len(skill_pool))))

    # Qualifications
    if specialty == "Technical":
        qualifications = random.choice([
            "Bachelor's degree in Computer Science or related field",
            "Relevant technical qualifications",
            "Degree or equivalent experience",
            "No formal qualifications required"
        ])
    elif specialty == "Accountancy":
        qualifications = random.choice([
            "AAT qualified or studying towards",
            "ACCA/CIMA part-qualified",
            "Qualified Accountant (ACA/ACCA/CIMA)",
            "Degree in Accounting or Finance"
        ])
    else:
        qualifications = random.choice([
            "Relevant qualifications",
            "No formal qualifications required",
            "Degree preferred but not essential",
            "A-Levels or equivalent"
        ])

    nice_to_have = random.choice([
        "Industry experience",
        "Additional certifications",
        "Leadership experience",
        "Sector knowledge",
        ""
    ])

    # Contract details
    if random.random() < 0.7:  # 70% permanent
        contract_type = "Permanent"
        contract_duration = ""
    elif random.random() < 0.2:  # 20% temporary
        contract_type = "Temporary"
        contract_duration = random.choice(["3 months", "6 months", "12 months"])
    else:  # 10% contract
        contract_type = "Contract"
        contract_duration = random.choice(["6 months", "12 months", "18 months"])

    hours_per_week = random.choice([37.5, 40, 35])

    # Dates
    posted_date = generate_posted_date()
    deadline = generate_deadline(posted_date)
    start_date_val = generate_start_date()

    # Number of positions
    if client_tier == "Platinum" and specialty == "Contact Centre":
        num_positions = random.randint(1, 8)
    else:
        num_positions = random.choice([1, 1, 1, 1, 1, 2, 2, 3])

    # Status
    if random.random() < 0.7:  # 70% open
        job_status = "Open"
    elif random.random() < 0.15:  # 15% filled
        job_status = "Filled"
    else:  # 15% closed or on hold
        job_status = random.choice(["Closed", "On Hold"])

    # Recruitment details
    consultant = "Sam Henderson"
    if specialty == "Contact Centre" and client_tier == "Platinum":
        consultant = "Contact Centre Specialist"

    priority = random.choice(["Low", "Medium", "Medium", "High", "High", "Urgent"])

    # Job boards
    posted_on_boards = random.choice([True, True, False])
    broadbean = posted_on_boards
    if posted_on_boards:
        board_options = ["Indeed", "Totaljobs", "CV-Library", "Reed", "Jobsite", "Jobserve"]
        num_boards = random.randint(2, 5)
        boards = ", ".join(random.sample(board_options, num_boards))
    else:
        boards = ""

    # Notes
    notes_templates = [
        f"Urgent requirement for {location_city} office",
        f"Client seeking immediate start",
        f"Excellent opportunity for career progression",
        f"{random.choice(['Fast-track', 'Standard', 'Detailed'])} interview process",
        f"Remote working {random.choice(['available', 'negotiable', 'after probation'])}",
        f"Growing team - more opportunities expected",
        f"Replacement for leaver - like-for-like hire",
        f"New role due to business growth",
        f"Client very engaged - high fill probability",
        f"Multiple positions available if right candidates found"
    ]
    notes = random.choice(notes_templates)

    return {
        "Job ID": generate_job_id(job_id),
        "Client ID": client_id,
        "Job Title": title,
        "Job Description": description,
        "Industry Sector": industry if client else "Various",
        "Department": department,
        "Location": f"{location_city}, {location_county}",
        "Postcode Area": postcode_area,
        "Work Model": work_model,
        "Hybrid Details": hybrid_details,
        "Salary Min (£)": salary_min,
        "Salary Max (£)": salary_max,
        "Salary Type": salary_type,
        "Benefits": benefits,
        "Required Experience Years": exp_years,
        "Required Skills": required_skills,
        "Required Qualifications": qualifications,
        "Nice to Have": nice_to_have,
        "Contract Type": contract_type,
        "Contract Duration": contract_duration,
        "Hours Per Week": hours_per_week,
        "Start Date": start_date_val,
        "Posted Date": posted_date,
        "Application Deadline": deadline,
        "Number of Positions": num_positions,
        "Job Status": job_status,
        "Fee Percentage": fee_pct,
        "Assigned Consultant": consultant,
        "Priority": priority,
        "Posted on Job Boards": "Yes" if posted_on_boards else "No",
        "Broadbean Posted": "Yes" if broadbean else "No",
        "Boards Posted": boards,
        "Notes": notes
    }

def main():
    parser = argparse.ArgumentParser(description="Generate fake job posting data")
    parser.add_argument("--count", type=int, default=50, help="Number of jobs to generate")
    parser.add_argument("--output", type=str, default="fake_jobs.csv", help="Output CSV filename")
    parser.add_argument("--clients", type=str, help="Path to clients CSV file (optional)")
    parser.add_argument("--sectors", type=str, help="Comma-separated sectors (e.g., 'Technical,Sales')")

    args = parser.parse_args()

    # Load clients if provided
    clients = []
    if args.clients:
        clients = load_clients(args.clients)

    # Parse sector filter
    sector_filter = None
    if args.sectors:
        sector_filter = [s.strip() for s in args.sectors.split(",")]
        print(f"Filtering for sectors: {', '.join(sector_filter)}")

    print(f"Generating {args.count} fake job records...")

    jobs = []
    for i in range(1, args.count + 1):
        # Use client if available
        client = None
        if clients:
            client = random.choice(clients)
            # Only use client if they have active jobs
            if int(client.get("Active Jobs", 0)) == 0 and random.random() < 0.5:
                client = None

        job = generate_job(i, client, sector_filter)
        jobs.append(job)

    # Write to CSV
    fieldnames = list(jobs[0].keys())
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

    print(f"[OK] Generated {len(jobs)} jobs")
    print(f"[OK] Saved to {args.output}")

    # Print summary stats
    specialties = {}
    statuses = {}
    for job in jobs:
        # Determine specialty from title
        title = job["Job Title"]
        dept = job["Department"]

        if dept == "IT":
            spec = "Technical"
        elif dept == "Sales":
            spec = "Sales"
        elif dept == "Customer Service":
            spec = "Contact Centre"
        elif dept == "Finance":
            spec = "Accountancy"
        else:
            spec = "Commercial"

        specialties[spec] = specialties.get(spec, 0) + 1
        status = job["Job Status"]
        statuses[status] = statuses.get(status, 0) + 1

    print("\nSpecialty Distribution:")
    for spec, count in sorted(specialties.items()):
        print(f"  {spec}: {count} ({count/len(jobs)*100:.1f}%)")

    print("\nStatus Distribution:")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count} ({count/len(jobs)*100:.1f}%)")

    if clients:
        print(f"\nLinked to {len(clients)} client records")

if __name__ == "__main__":
    main()
