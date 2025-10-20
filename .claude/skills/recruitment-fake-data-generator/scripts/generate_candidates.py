#!/usr/bin/env python3
"""
Generate fake candidate/job seeker data for recruitment system testing.
Produces realistic UK-focused candidate records with skills, experience, and preferences.
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Reuse some data from generate_clients
FIRST_NAMES_MALE = [
    "James", "Oliver", "Jack", "Harry", "Jacob", "Charlie", "Thomas", "George", "Oscar",
    "William", "Noah", "Alfie", "Joshua", "Muhammad", "Henry", "Leo", "Archie", "Ethan",
    "Joseph", "Samuel", "Alexander", "Daniel", "Isaac", "Max", "Mohammed", "Benjamin",
    "Lucas", "Mason", "Harrison", "Theo", "Sebastian", "Jake", "Adam", "Dylan", "Riley"
]

FIRST_NAMES_FEMALE = [
    "Olivia", "Amelia", "Isla", "Ava", "Emily", "Isabella", "Mia", "Poppy", "Ella",
    "Lily", "Sophia", "Grace", "Sophie", "Freya", "Chloe", "Evie", "Florence", "Lucy",
    "Evelyn", "Charlotte", "Sienna", "Alice", "Phoebe", "Scarlett", "Ruby", "Matilda",
    "Hannah", "Jessica", "Emma", "Sarah", "Laura", "Rebecca", "Katie", "Amy", "Rachel"
]

LAST_NAMES = [
    "Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies",
    "Robinson", "Wright", "Thompson", "Evans", "Walker", "White", "Roberts", "Green",
    "Hall", "Wood", "Jackson", "Clarke", "Patel", "Khan", "Singh", "Ali", "Ahmed",
    "Hughes", "Edwards", "Thomas", "Martin", "Lewis", "Harris", "Clark", "Cooper",
    "King", "Turner", "Hill", "Scott", "Moore", "Baker", "Anderson", "Campbell",
    "Murphy", "Mitchell", "Carter", "Adams", "Phillips", "Morgan", "Bell", "Foster"
]

BRISTOL_CITIES = [
    ("Bristol", "Bristol", "BS"),
    ("Weston-super-Mare", "Somerset", "BS"),
    ("Bath", "Somerset", "BA"),
    ("Portishead", "North Somerset", "BS"),
    ("Clevedon", "North Somerset", "BS"),
]

TECHNICAL_SKILLS = [
    ["Python", "Django", "PostgreSQL", "REST APIs", "Git"],
    ["JavaScript", "React", "Node.js", "MongoDB", "TypeScript"],
    ["Java", "Spring Boot", "MySQL", "Maven", "JUnit"],
    ["C#", ".NET Core", "SQL Server", "Azure", "Entity Framework"],
    ["PHP", "Laravel", "MySQL", "Vue.js", "Composer"],
    ["AWS", "Terraform", "Docker", "Kubernetes", "Python"],
    ["Azure", "PowerShell", "ARM Templates", "DevOps", "CI/CD"],
    ["Linux", "Bash", "Ansible", "Jenkins", "Git"],
    ["Cybersecurity", "Penetration Testing", "SIEM", "Firewalls", "Python"],
    ["Network Engineering", "Cisco", "TCP/IP", "VPN", "Routing"],
    ["SQL", "Data Analysis", "Python", "Tableau", "Excel"],
    ["Cloud Architecture", "AWS", "Microservices", "Kubernetes", "Terraform"],
    ["IT Support", "Windows Server", "Active Directory", "ITIL", "Help Desk"],
    ["Data Science", "Python", "Machine Learning", "TensorFlow", "R"],
    ["QA Testing", "Selenium", "JIRA", "Test Automation", "Agile"]
]

SALES_SKILLS = [
    ["B2B Sales", "CRM (Salesforce)", "Cold Calling", "Lead Generation", "Negotiation"],
    ["Account Management", "Relationship Building", "Sales Pipeline", "HubSpot", "B2B"],
    ["Business Development", "Market Research", "Prospecting", "Presentations", "Networking"],
    ["Telesales", "Outbound Calling", "Closing Skills", "Product Knowledge", "CRM"],
    ["Field Sales", "Territory Management", "Client Meetings", "Negotiation", "Reporting"],
    ["Inside Sales", "SaaS Sales", "Salesforce", "Email Marketing", "LinkedIn Sales"],
    ["Key Account Management", "Strategic Planning", "Contract Negotiation", "Relationship Management"],
    ["Fundraising", "Donor Relations", "Charity Sector", "Telephone Fundraising", "Compliance"],
    ["Retail Sales", "Customer Service", "POS Systems", "Visual Merchandising", "Stock Management"]
]

CONTACT_CENTRE_SKILLS = [
    ["Customer Service", "Call Handling", "CRM Systems", "Conflict Resolution", "Multi-tasking"],
    ["Inbound Sales", "Upselling", "Customer Retention", "Active Listening", "Problem Solving"],
    ["Technical Support", "Troubleshooting", "Ticketing Systems", "Remote Support", "Documentation"],
    ["Outbound Calling", "Lead Qualification", "Script Adherence", "Data Entry", "KPI Management"],
    ["Team Leadership", "Quality Assurance", "Call Monitoring", "Coaching", "Performance Management"],
    ["Complaint Handling", "De-escalation", "Empathy", "Communication", "CRM"],
    ["Multi-channel Support", "Email Support", "Chat Support", "Phone Support", "Social Media"]
]

ACCOUNTANCY_SKILLS = [
    ["Accounts Payable/Receivable", "Sage", "Excel", "VAT Returns", "Reconciliation"],
    ["Management Accounting", "Financial Reporting", "Budgeting", "Forecasting", "Analysis"],
    ["Tax Compliance", "Corporation Tax", "VAT", "PAYE", "Tax Planning"],
    ["Audit", "Internal Controls", "Risk Assessment", "Compliance", "Financial Analysis"],
    ["Bookkeeping", "Xero", "QuickBooks", "Bank Reconciliation", "Invoicing"],
    ["Financial Controller", "Leadership", "Strategic Planning", "Team Management", "IFRS"],
    ["Payroll", "Payroll Software", "PAYE", "Auto-enrolment", "HR Systems"],
    ["Credit Control", "Debt Recovery", "Cash Flow Management", "Negotiation", "Communication"]
]

COMMERCIAL_SKILLS = [
    ["Administration", "Microsoft Office", "Data Entry", "Filing", "Communication"],
    ["Office Management", "Facilities", "Vendor Management", "Budget Control", "Team Coordination"],
    ["Executive Assistant", "Calendar Management", "Travel Booking", "Minute Taking", "Confidentiality"],
    ["Project Management", "MS Project", "Stakeholder Management", "Risk Management", "Agile"],
    ["HR Administration", "Recruitment", "Onboarding", "HR Systems", "Employee Relations"],
    ["Operations Management", "Process Improvement", "KPI Tracking", "Team Leadership", "Budget Management"],
    ["Procurement", "Supplier Management", "Contract Negotiation", "Cost Reduction", "ERP Systems"],
    ["Business Analysis", "Requirements Gathering", "Process Mapping", "SQL", "Stakeholder Engagement"]
]

EDUCATION_LEVELS = {
    "GCSE": ["GCSEs including Maths and English", "10 GCSEs including Maths (A*) and English (A)"],
    "A-Level": ["A-Levels in Maths, Physics, Chemistry", "A-Levels in Business, Economics, English"],
    "Bachelor's": [
        "BSc Computer Science, University of Bristol",
        "BA Business Management, University of West England",
        "BEng Software Engineering, University of Bath",
        "BSc Accounting and Finance, Bristol University",
        "BA Marketing, University of West England",
        "BSc Mathematics, University of Bristol",
        "BA Psychology, Cardiff University",
        "BEng Electrical Engineering, Bath University"
    ],
    "Master's": [
        "MSc Data Science, University of Bristol",
        "MBA, University of Bath",
        "MSc Cybersecurity, Bristol University",
        "MSc Finance, Cardiff University",
        "MA Human Resources, UWE"
    ],
    "PhD": [
        "PhD Computer Science, University of Bristol",
        "PhD Engineering, Bath University",
        "PhD Data Analytics, Bristol University"
    ],
    "Professional": [
        "ACCA Qualified Accountant",
        "CIMA Qualified",
        "ACA Chartered Accountant",
        "CIM Chartered Marketer",
        "CIPD Level 5 HR",
        "Prince2 Practitioner"
    ]
}

CERTIFICATIONS = {
    "Technical": [
        "AWS Certified Solutions Architect",
        "Microsoft Azure Fundamentals",
        "CompTIA Security+",
        "ITIL Foundation",
        "Cisco CCNA",
        "Google Cloud Certified",
        "Certified Kubernetes Administrator",
        "AWS Certified Developer"
    ],
    "Sales": [
        "HubSpot Sales Certification",
        "Salesforce Certified Administrator",
        "None"
    ],
    "Accountancy": [
        "AAT Level 4",
        "ACCA Part-Qualified",
        "CIMA Part-Qualified",
        "Xero Certified",
        "Sage Certified"
    ],
    "Commercial": [
        "Prince2 Foundation",
        "Agile Scrum Master",
        "Microsoft Office Specialist",
        "CIPD Level 3",
        "None"
    ],
    "Contact Centre": ["None"]
}

JOB_TITLES = {
    "Technical": [
        "Software Developer", "Senior Software Engineer", "IT Support Analyst", "DevOps Engineer",
        "Cloud Engineer", "Systems Administrator", "Data Analyst", "Network Engineer",
        "Cybersecurity Analyst", "Technical Lead", "Junior Developer", "QA Engineer",
        "Database Administrator", "Solutions Architect", "Full Stack Developer"
    ],
    "Sales": [
        "Sales Executive", "Business Development Manager", "Account Manager", "Sales Representative",
        "Telesales Executive", "Field Sales Manager", "Key Account Manager", "Sales Director",
        "Inside Sales Representative", "Fundraising Manager", "Sales Team Leader"
    ],
    "Contact Centre": [
        "Customer Service Advisor", "Call Centre Agent", "Customer Support Representative",
        "Technical Support Agent", "Team Leader", "Contact Centre Manager", "Quality Analyst",
        "Telephone Fundraiser", "Customer Service Manager"
    ],
    "Accountancy": [
        "Accounts Assistant", "Accountant", "Senior Accountant", "Management Accountant",
        "Financial Controller", "Finance Manager", "Tax Accountant", "Payroll Administrator",
        "Credit Controller", "Bookkeeper", "Audit Manager"
    ],
    "Commercial": [
        "Administrator", "Office Manager", "Executive Assistant", "Operations Manager",
        "HR Administrator", "Project Manager", "Business Analyst", "Facilities Manager",
        "Procurement Manager", "Receptionist", "Office Administrator"
    ]
}

EMPLOYERS = [
    "Accenture", "Deloitte", "EY", "PwC", "KPMG", "IBM", "Capgemini", "BT Group",
    "Lloyds Banking Group", "Barclays", "HSBC", "Santander", "Aviva", "Legal & General",
    "Tesco", "Sainsbury's", "Marks & Spencer", "John Lewis", "Next", "Amazon UK",
    "Bristol City Council", "NHS Bristol", "University of Bristol", "UWE Bristol",
    "Airbus", "Rolls-Royce", "BAE Systems", "GKN Aerospace", "Dyson",
    "Various SMEs", "Small Agency", "Local Business", "Startup", "Consultancy"
]

EMPLOYMENT_STATUS = ["Employed", "Employed", "Employed", "Unemployed", "Notice Period", "Notice Period"]
WORK_PREFERENCES = ["Office", "Hybrid", "Remote", "Flexible"]
NOTICE_PERIODS = ["Immediate", "1 week", "2 weeks", "1 month", "2 months", "3 months"]

def generate_email(first_name: str, last_name: str) -> str:
    """Generate realistic personal email address."""
    domains = ["gmail.com", "outlook.com", "hotmail.co.uk", "yahoo.co.uk", "icloud.com"]
    formats = [
        f"{first_name.lower()}.{last_name.lower()}",
        f"{first_name.lower()}{last_name.lower()}",
        f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}",
        f"{first_name[0].lower()}{last_name.lower()}"
    ]
    return f"{random.choice(formats)}@{random.choice(domains)}"

def generate_phone() -> str:
    """Generate UK mobile number."""
    return f"07{random.randint(700, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"

def generate_postcode(area_code: str) -> str:
    """Generate UK postcode."""
    sector = random.randint(1, 9)
    unit = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ', k=2))
    return f"{area_code}{sector} {unit}"

def generate_dob(age_range: tuple) -> str:
    """Generate date of birth based on age range."""
    age = random.randint(age_range[0], age_range[1])
    today = datetime.now()
    birth_year = today.year - age
    dob = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
    return dob.strftime("%Y-%m-%d")

def generate_experience_years(age: int) -> int:
    """Calculate realistic years of experience based on age."""
    if age < 20:
        return 0
    elif age < 23:
        return random.randint(0, 2)
    elif age < 30:
        return random.randint(2, 7)
    elif age < 40:
        return random.randint(5, 15)
    else:
        return random.randint(10, min(age - 18, 30))

def calculate_age(dob_str: str) -> int:
    """Calculate age from date of birth string."""
    dob = datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.now()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def generate_registration_date(months_ago_max: int) -> str:
    """Generate registration date within last X months."""
    today = datetime.now()
    days_ago = random.randint(0, months_ago_max * 30)
    reg_date = today - timedelta(days=days_ago)
    return reg_date.strftime("%Y-%m-%d")

def generate_cv_upload_date(registration_date: str) -> str:
    """Generate CV upload date (same or after registration)."""
    reg_date = datetime.strptime(registration_date, "%Y-%m-%d")
    days_after = random.randint(0, 30)
    cv_date = reg_date + timedelta(days=days_after)
    return cv_date.strftime("%Y-%m-%d")

def generate_start_date(status: str, notice: str) -> str:
    """Generate available start date based on status and notice."""
    today = datetime.now()

    if status == "Unemployed" or notice == "Immediate":
        days_ahead = random.randint(0, 14)
    elif notice == "1 week":
        days_ahead = random.randint(7, 14)
    elif notice == "2 weeks":
        days_ahead = random.randint(14, 21)
    elif notice == "1 month":
        days_ahead = random.randint(28, 35)
    elif notice == "2 months":
        days_ahead = random.randint(56, 70)
    else:  # 3 months
        days_ahead = random.randint(84, 98)

    start_date = today + timedelta(days=days_ahead)
    return start_date.strftime("%Y-%m-%d")

def generate_linkedin(first_name: str, last_name: str) -> str:
    """Generate LinkedIn profile URL."""
    if random.random() < 0.7:  # 70% have LinkedIn
        return f"linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(1000, 9999)}"
    return "None"

def generate_notes(specialty: str, experience: int) -> str:
    """Generate realistic candidate notes."""
    notes_templates = [
        f"Strong {specialty.lower()} candidate with {experience} years experience",
        f"Excellent communication skills. {random.choice(['Immediately available', 'Available soon', 'Notice period applies'])}",
        f"Seeking {random.choice(['progression', 'new challenge', 'career change', 'better opportunity'])}",
        f"{random.choice(['Highly motivated', 'Reliable', 'Professional', 'Ambitious'])} candidate",
        f"Good cultural fit for {random.choice(['SMEs', 'corporates', 'startups', 'established companies'])}",
        f"Looking for {random.choice(['remote role', 'hybrid working', 'office-based position', 'flexible working'])}",
        f"{random.choice(['Recent graduate', 'Career changer', 'Experienced professional', 'Senior candidate'])}. Strong references available",
        f"Specializes in {random.choice(['technical roles', 'sales positions', 'client-facing work', 'backend systems'])}",
        f"{random.choice(['Actively seeking', 'Open to opportunities', 'Considering options', 'Available immediately'])}",
        f"Excellent track record. {random.choice(['Multiple offers expected', 'Hot candidate', 'In-demand skills', 'Niche expertise'])}"
    ]
    return random.choice(notes_templates)

def generate_candidate(candidate_id: int, sector_filter: Optional[List[str]] = None) -> Dict:
    """Generate a single fake candidate record."""

    # Select specialty
    specialties = ["Technical", "Sales", "Contact Centre", "Accountancy", "Commercial"]
    if sector_filter:
        specialties = [s for s in specialties if s in sector_filter]
        if not specialties:
            specialties = ["Technical", "Sales", "Contact Centre", "Accountancy", "Commercial"]

    specialty = random.choice(specialties)

    # Generate personal details
    gender = random.choice(["M", "F"])
    first_name = random.choice(FIRST_NAMES_MALE if gender == "M" else FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)

    # Age and DOB
    if specialty == "Contact Centre":
        age_range = (18, 55)
    elif specialty == "Commercial":
        age_range = (21, 60)
    else:
        age_range = (21, 58)

    dob = generate_dob(age_range)
    age = calculate_age(dob)

    # Contact details
    email = generate_email(first_name, last_name)
    phone = generate_phone()

    # Address
    city, county, area_code = random.choice(BRISTOL_CITIES)
    postcode = generate_postcode(area_code)
    streets = [
        f"{random.randint(1, 250)} {random.choice(['High Street', 'Park Road', 'Station Road', 'Church Lane', 'Manor Drive'])}",
        f"Flat {random.randint(1, 40)}, {random.choice(['Victoria Court', 'The Maltings', 'Riverside Apartments', 'Oak House'])}"
    ]
    address1 = random.choice(streets)
    address2 = random.choice(["", "", "", "Clifton", "Redland", "Bedminster", "Southville"])

    # Professional profile
    experience_years = generate_experience_years(age)
    current_title = random.choice(JOB_TITLES[specialty])

    if experience_years == 0:
        current_employer = "Student" if age < 23 else "Unemployed"
        employment_status = "Student" if age < 23 else "Unemployed"
    elif random.random() < 0.15:  # 15% unemployed
        current_employer = "Unemployed"
        employment_status = "Unemployed"
    else:
        current_employer = random.choice(EMPLOYERS)
        employment_status = random.choice(EMPLOYMENT_STATUS)

    # Skills
    if specialty == "Technical":
        skills = random.choice(TECHNICAL_SKILLS)
    elif specialty == "Sales":
        skills = random.choice(SALES_SKILLS)
    elif specialty == "Contact Centre":
        skills = random.choice(CONTACT_CENTRE_SKILLS)
    elif specialty == "Accountancy":
        skills = random.choice(ACCOUNTANCY_SKILLS)
    else:  # Commercial
        skills = random.choice(COMMERCIAL_SKILLS)

    # Certifications
    cert_options = CERTIFICATIONS.get(specialty, ["None"])
    valid_certs = [c for c in cert_options if c != "None"]
    if valid_certs and random.random() < 0.4:  # 40% have certifications if available
        certifications = random.choice(valid_certs)
    else:
        certifications = "None"

    # Education
    if specialty == "Technical" and experience_years > 2:
        edu_level = random.choice(["Bachelor's", "Bachelor's", "Master's"])
    elif specialty == "Accountancy":
        edu_level = random.choice(["Bachelor's", "Professional", "A-Level"])
    elif specialty == "Sales" or specialty == "Contact Centre":
        edu_level = random.choice(["A-Level", "Bachelor's", "GCSE"])
    else:  # Commercial
        edu_level = random.choice(["A-Level", "Bachelor's", "GCSE"])

    education = random.choice(EDUCATION_LEVELS[edu_level])

    # Desired role and sectors
    desired_role = random.choice(JOB_TITLES[specialty])

    sector_map = {
        "Technical": "IT Services, Software Development, FinTech",
        "Sales": "B2B Services, Technology, Financial Services",
        "Contact Centre": "Contact Centres, Telecommunications, Customer Service",
        "Accountancy": "Accounting Firms, Finance, Corporate",
        "Commercial": "Various, Corporate, SMEs"
    }
    desired_sectors = sector_map[specialty]

    # Salary expectations
    if specialty == "Technical":
        base_salary = 25000 + (experience_years * 3000)
        salary_max = min(95000, base_salary + 15000)
        salary_min = min(base_salary, salary_max - 5000)
    elif specialty == "Accountancy":
        base_salary = 22000 + (experience_years * 2500)
        salary_max = min(75000, base_salary + 12000)
        salary_min = min(base_salary, salary_max - 5000)
    elif specialty == "Sales":
        base_salary = 22000 + (experience_years * 2500)
        salary_max = min(70000, base_salary + 15000)
        salary_min = min(base_salary, salary_max - 5000)
    elif specialty == "Contact Centre":
        base_salary = 18000 + (experience_years * 1500)
        salary_max = min(42000, base_salary + 8000)
        salary_min = min(base_salary, salary_max - 3000)
    else:  # Commercial
        base_salary = 20000 + (experience_years * 2000)
        salary_max = min(55000, base_salary + 12000)
        salary_min = min(base_salary, salary_max - 5000)

    salary_expectations = random.randint(int(salary_min), int(salary_max))

    # Preferences
    work_preference = random.choice(WORK_PREFERENCES)
    willing_relocate = random.choice(["No", "No", "No", "Maybe", "Yes"])

    # Notice period
    if employment_status == "Unemployed" or employment_status == "Student":
        notice_period = "Immediate"
    elif employment_status == "Notice Period":
        notice_period = random.choice(["1 week", "2 weeks", "1 month"])
    else:  # Employed
        notice_period = random.choice(["1 month", "1 month", "2 months", "3 months"])

    # Dates
    registration_date = generate_registration_date(18)  # Within last 18 months
    cv_upload_date = generate_cv_upload_date(registration_date)
    available_start = generate_start_date(employment_status, notice_period)

    # Status
    if random.random() < 0.85:  # 85% active
        candidate_status = "Active"
    elif random.random() < 0.05:  # 5% placed
        candidate_status = "Placed"
    else:  # 10% inactive or on hold
        candidate_status = random.choice(["Inactive", "On Hold"])

    # Consultant
    consultant = "Sam Henderson"

    # LinkedIn and portfolio
    linkedin = generate_linkedin(first_name, last_name)
    if specialty == "Technical" and random.random() < 0.3:
        portfolio = f"github.com/{first_name.lower()}{last_name.lower()}"
    else:
        portfolio = "None"

    # Notes
    notes = generate_notes(specialty, experience_years)

    return {
        "Candidate ID": f"CAN-{candidate_id:03d}",
        "First Name": first_name,
        "Last Name": last_name,
        "Email": email,
        "Phone": phone,
        "Date of Birth": dob,
        "Address Line 1": address1,
        "Address Line 2": address2,
        "City": city,
        "County": county,
        "Postcode": postcode,
        "Country": "United Kingdom",
        "Current Job Title": current_title,
        "Years of Experience": experience_years,
        "Current/Last Employer": current_employer,
        "Employment Status": employment_status,
        "Key Skills": ", ".join(skills),
        "Certifications": certifications,
        "Education Level": edu_level,
        "Education Details": education,
        "Desired Role": desired_role,
        "Desired Sectors": desired_sectors,
        "Salary Expectations (£)": salary_expectations,
        "Work Model Preference": work_preference,
        "Willing to Relocate": willing_relocate,
        "Notice Period": notice_period,
        "Available Start Date": available_start,
        "Registration Date": registration_date,
        "Status": candidate_status,
        "Assigned Consultant": consultant,
        "CV Upload Date": cv_upload_date,
        "LinkedIn Profile": linkedin,
        "Portfolio URL": portfolio,
        "Notes": notes
    }

def main():
    parser = argparse.ArgumentParser(description="Generate fake candidate data for recruitment system")
    parser.add_argument("--count", type=int, default=50, help="Number of candidates to generate")
    parser.add_argument("--output", type=str, default="fake_candidates.csv", help="Output CSV filename")
    parser.add_argument("--sectors", type=str, help="Comma-separated sectors (e.g., 'Technical,Sales')")

    args = parser.parse_args()

    # Parse sector filter
    sector_filter = None
    if args.sectors:
        sector_filter = [s.strip() for s in args.sectors.split(",")]
        print(f"Filtering for sectors: {', '.join(sector_filter)}")

    print(f"Generating {args.count} fake candidate records...")

    candidates = []
    for i in range(1, args.count + 1):
        candidate = generate_candidate(i, sector_filter)
        candidates.append(candidate)

    # Write to CSV
    fieldnames = list(candidates[0].keys())
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates)

    print(f"[OK] Generated {len(candidates)} candidates")
    print(f"[OK] Saved to {args.output}")

    # Print summary stats
    specialties = {}
    statuses = {}
    for candidate in candidates:
        # Determine specialty from skills
        skills = candidate["Key Skills"]
        if "Python" in skills or "Java" in skills or "AWS" in skills:
            spec = "Technical"
        elif "Sales" in skills or "CRM" in skills:
            spec = "Sales"
        elif "Customer Service" in skills or "Call" in skills:
            spec = "Contact Centre"
        elif "Accounts" in skills or "Tax" in skills:
            spec = "Accountancy"
        else:
            spec = "Commercial"

        specialties[spec] = specialties.get(spec, 0) + 1
        status = candidate["Status"]
        statuses[status] = statuses.get(status, 0) + 1

    print("\nSpecialty Distribution:")
    for spec, count in sorted(specialties.items()):
        print(f"  {spec}: {count} ({count/len(candidates)*100:.1f}%)")

    print("\nStatus Distribution:")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count} ({count/len(candidates)*100:.1f}%)")

if __name__ == "__main__":
    main()
