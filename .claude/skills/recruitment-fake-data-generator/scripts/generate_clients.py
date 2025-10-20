#!/usr/bin/env python3
"""
Generate fake client/company data for recruitment system testing.
Produces realistic UK-focused client records matching ProActive People's business model.
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# UK-specific data
BRISTOL_POSTCODES = [
    "BS1 6DZ", "BS1 5TR", "BS1 6HG", "BS1 6EA", "BS1 4SB", "BS1 3PR", "BS1 1SE",
    "BS2 0QF", "BS2 0EJ", "BS2 0TB", "BS2 0RL", "BS2 0XS",
    "BS3 2TG", "BS3 5PE", "BS4 3QJ", "BS4 3EH", "BS4 3AT", "BS4 5QY", "BS4 3BD",
    "BS5 0QW", "BS7 8AS", "BS8 1SD", "BS8 2LR", "BS8 4EJ", "BS8 1UB", "BS8 1TH",
    "BS9 4NG", "BS10 7TB", "BS11 9YB", "BS11 8DQ", "BS11 9YA",
    "BS16 1QD", "BS16 3AF", "BS16 7FR", "BS16 1QY",
    "BS20 7XS", "BS24 9AH", "BS32 4TD", "BS48 3DY"
]

BRISTOL_STREETS = [
    ("Bristol Technology Park", "3rd Floor Building A"),
    ("One Temple Quay", "Suite 400"),
    ("Metro House", "Bristol Road"),
    ("Apex Industrial Estate", "Building 7"),
    ("Cyber Security Hub", "Floor 5 Tech Quarter"),
    ("Innovation Centre", "Tech Hub East"),
    ("Distribution Centre", "Junction 19 M5"),
    ("Creative Quarter", "Unit 3B Paintworks"),
    ("City Hall", "College Green"),
    ("Premier House", "Harbourside"),
    ("Fusion Tower", "Templemeads Business Park"),
    ("FinTech Tower", "Temple Meads"),
    ("BioScience Park", "University Enterprise Zone"),
    ("Riverside House", "The Waterfront"),
    ("Broadcasting House", "Whiteladies Road"),
    ("Construction House", "Feeder Road"),
    ("Cloud Centre", "Technology Quarter"),
    ("Analytics Hub", "Tech Quarter"),
    ("Fitness Hub", "Cabot Circus"),
    ("The Sustainable Building", "2nd Floor"),
]

COMPANY_PREFIXES = [
    "Tech", "Data", "Secure", "Premier", "Green", "Metro", "Apex", "Digital", "Cloud",
    "Smart", "Bright", "Quantum", "Fusion", "Phoenix", "Complete", "Sterling", "Velocity",
    "Heritage", "Bristol", "Coastal", "Nautilus", "FreshFood", "Skyline", "Infinity",
    "Bloom", "WellnessFirst", "AutoTech", "BioPharm", "MindCare", "Caring Hands",
    "Fashion Forward", "Culinary Delights", "Solar Power", "DataCore", "EduTech"
]

BUSINESS_TYPES = [
    "Solutions", "Systems", "Group", "Services", "Technologies", "Consulting",
    "Associates", "Holdings", "Corporation", "Enterprises", "Hub", "Studio",
    "Labs", "Research", "Centre", "Agency", "Partners", "Network", "Innovations"
]

INDUSTRY_DESCRIPTORS = [
    "Software", "Financial", "Logistics", "Energy", "Retail", "Engineering",
    "Security", "Marketing", "Property", "Healthcare", "Construction", "Legal",
    "Pharmaceutical", "Hospitality", "Telecommunications", "Broadcasting",
    "Insurance", "Manufacturing", "Distribution", "Technology"
]

LEGAL_SUFFIXES = ["Ltd", "Limited", "PLC", "LLP", "Limited"]

INDUSTRIES = {
    "IT Services & Consulting": ["Technical", "Sales"],
    "Financial Services": ["Accountancy", "Sales", "Commercial"],
    "Contact Centre Operations": ["Contact Centre"],
    "Renewable Energy": ["Technical", "Commercial", "Sales"],
    "Retail & E-commerce": ["Sales", "Commercial", "Contact Centre"],
    "Engineering & Manufacturing": ["Technical", "Commercial"],
    "Healthcare": ["Commercial", "Contact Centre"],
    "Cybersecurity": ["Technical"],
    "Software Development": ["Technical"],
    "Logistics & Distribution": ["Commercial", "Sales"],
    "Education / Higher Education": ["Technical", "Commercial", "Accountancy"],
    "Marketing & Advertising": ["Sales", "Commercial"],
    "Local Government": ["Commercial", "Technical", "Contact Centre"],
    "Maritime & Shipping": ["Technical", "Commercial"],
    "Food & Beverage": ["Commercial", "Sales", "Contact Centre"],
    "Research & Development": ["Technical"],
    "Childcare & Education": ["Commercial"],
    "Video Games Development": ["Technical"],
    "Insurance & Financial Services": ["Sales", "Accountancy", "Contact Centre"],
    "Courier & Delivery Services": ["Commercial"],
    "Retail / Garden Centres": ["Sales", "Commercial"],
    "Media & Broadcasting": ["Technical", "Commercial", "Sales"],
    "Financial Technology": ["Technical", "Sales", "Accountancy"],
    "Food Production / Bakery": ["Commercial"],
    "IT Support Services": ["Technical", "Contact Centre"],
    "Health & Fitness": ["Sales", "Commercial"],
    "Construction & Building": ["Technical", "Commercial"],
    "Cloud Infrastructure": ["Technical"],
    "Veterinary Services": ["Commercial"],
    "Telecommunications": ["Technical", "Contact Centre", "Sales"],
    "Educational Technology": ["Technical", "Sales"],
    "Dental Healthcare": ["Commercial"],
    "Automotive Services": ["Technical", "Commercial"],
    "Legal Services": ["Accountancy", "Commercial"],
    "Pharmaceuticals & Biotech": ["Technical", "Commercial"],
    "Hospitality & Hotels": ["Commercial", "Sales", "Contact Centre"],
    "Landscaping & Horticulture": ["Commercial"],
    "Data Analytics & BI": ["Technical", "Sales"],
    "Social Care & Healthcare": ["Commercial"],
    "Recruitment Agency": ["Sales"],
    "Catering & Events": ["Commercial"],
    "Mental Health Services": ["Commercial"],
    "Waste Management & Recycling": ["Commercial", "Technical"],
    "Fashion & Apparel Retail": ["Sales", "Commercial"],
    "Artificial Intelligence": ["Technical"]
}

COMPANY_SIZES = ["30-40", "45-60", "55-70", "65-80", "75-90", "80-100", "85-100", "95-120",
                 "105-120", "110-130", "120-140", "130-145", "140-160", "150-170", "150-200",
                 "170-190", "180-200", "190-210", "195-210", "200-220", "210-230", "220-250",
                 "240-260", "280-300", "300-350", "310-340", "320-350", "380-410", "420-450",
                 "450-500", "500+", "520-550", "800+", "950-1000", "1200+", "2500+", "8000+"]

FIRST_NAMES = [
    "Sarah", "James", "Michael", "Emma", "Rachel", "Mark", "David", "Sophie", "Lisa",
    "Oliver", "Andrew", "Jennifer", "Dr. Priya", "Thomas", "Aisha", "Hannah", "Paul",
    "Victoria", "Nathan", "Robert", "Zara", "Claire", "Dr. Amanda", "Simon", "Richard",
    "Ben", "Patricia", "Marcus", "Captain David", "Michelle", "Tony", "Prof. Richard",
    "Dr. Eleanor", "Karen", "Amy", "Jake", "Graham", "Fiona", "Rachel", "Susan",
    "Richard", "Yasmin", "Jonathan", "Tom", "Alan", "Natalie", "Mark", "Kelly",
    "Steve", "Linda", "Damien", "Dr. Sarah", "Anthony", "Nina", "Alex", "Dr. James",
    "Lucy", "Gary", "Michelle", "Margaret", "Dr. Helen", "Caroline", "Chef Antonio",
    "Dr. Sarah", "Malcolm", "Tracy", "Jessica", "Daniel", "Dr. Michael", "Brian", "Helen"
]

LAST_NAMES = [
    "Mitchell", "Wong", "Thompson", "Patel", "Davies", "Foster", "Kaur", "Williams",
    "Chen", "Brown", "Morgan", "Taylor", "Shah", "O'Connor", "Khan", "Roberts",
    "Green", "Lewis", "Edwards", "Singh", "Murphy", "Foster", "Baker", "Clarke",
    "Wilson", "James", "Reynolds", "Collins", "Martinez", "White", "Bennett",
    "Morrison", "Zhang", "Hughes", "McDonald", "Anderson", "Parker", "Wright",
    "Stone", "Ali", "Davis", "Kumar", "Baker", "Johnson", "Mitchell", "Robinson",
    "Phillips", "Lee", "Martin", "Ward", "Patel", "Thompson", "Howard", "Adams",
    "Stevens", "Harris", "Watson", "Barnes", "Scott", "Murphy", "Rossi", "Clark",
    "Turner", "Matthews", "Patterson", "Hughes", "Moore", "Chang", "Foster"
]

JOB_TITLES = [
    "HR Director", "Talent Acquisition Manager", "Operations Director", "Head of People",
    "Group HR Manager", "Talent Manager", "Practice Manager", "CTO", "HR Business Partner",
    "Fundraising Director", "People & Culture Lead", "Head of Talent", "Senior Resourcing Manager",
    "Fleet Operations Director", "People Director", "Research Director", "Group HR Manager",
    "Studio Manager", "Chief People Officer", "Operations Manager", "HR Manager", "Service Manager",
    "Managing Director", "CHRO", "Owner & MD", "Service Delivery Manager", "Group Operations Director",
    "Project Director", "CEO", "Co-Founder", "Principal Dentist", "Group Manager",
    "Senior Partner", "Talent Director", "Chief Operating Officer", "Clinical Director",
    "Founder & CEO", "Head of Operations", "Chief AI Officer"
]

SERVICE_LINES = [
    ["Recruitment"],
    ["Recruitment", "Assessment"],
    ["Recruitment", "Training"],
    ["Recruitment", "Wellbeing"],
    ["Recruitment", "Assessment", "Training"],
    ["Recruitment", "Wellbeing", "Assessment"],
    ["Recruitment", "Contact Centre Consultancy", "Training"],
]

WORK_MODELS = [
    ["Office"],
    ["Office", "Hybrid"],
    ["Hybrid", "Remote"],
    ["Remote", "Hybrid"],
    ["Office", "Hybrid", "Remote"],
    ["Office", "Shift Work"],
]

PAYMENT_TERMS = ["Net 30", "Net 45", "Net 60"]
PAYMENT_HISTORY = ["Excellent", "Good", "Fair"]
ACCOUNT_MANAGERS = ["Sam Henderson", "Contact Centre Specialist"]

DECISION_SPEEDS = [
    "Very Fast (<1 week)",
    "Fast (1-2 weeks)",
    "Medium (2-3 weeks)",
    "Medium (3-4 weeks)",
    "Slow (4-6 weeks)",
    "Slow (6-8 weeks)",
    "Slow (6-10 weeks)"
]

CONTRACT_PREFS = [
    ["Permanent"],
    ["Permanent", "Contract"],
    ["Permanent", "Temporary"],
    ["Permanent", "Temporary", "Contract"],
]

def generate_company_name() -> tuple:
    """Generate a realistic company name and legal entity name."""
    prefix = random.choice(COMPANY_PREFIXES)
    business_type = random.choice(BUSINESS_TYPES)
    suffix = random.choice(LEGAL_SUFFIXES)

    # Sometimes add industry descriptor
    if random.random() < 0.6:
        descriptor = random.choice(INDUSTRY_DESCRIPTORS)
        trading_name = f"{prefix} {descriptor} {business_type} {suffix}"
    else:
        trading_name = f"{prefix} {business_type} {suffix}"

    # Legal entity - expand suffix
    legal_suffix = "Limited" if suffix == "Ltd" else suffix
    legal_name = trading_name.replace(suffix, legal_suffix)

    return trading_name, legal_name

def generate_email(first_name: str, last_name: str, company_name: str) -> str:
    """Generate email address from name and company."""
    # Extract company domain from name
    domain_parts = company_name.lower().split()
    domain = domain_parts[0] if domain_parts else "company"

    # Remove common suffixes
    domain = domain.replace("ltd", "").replace("limited", "").replace("plc", "").replace("llp", "").strip()

    first_initial = first_name.lower().replace("dr. ", "").replace("prof. ", "").replace("captain ", "")[0]
    last = last_name.lower().replace("'", "")

    return f"{first_initial}.{last}@{domain}.co.uk"

def generate_phone() -> str:
    """Generate realistic Bristol area phone number."""
    area_codes = ["0117", "01934", "01275"]
    area = random.choice(area_codes)

    if area == "0117":
        return f"{area} 555 {random.randint(1000, 9999)}"
    else:
        return f"{area} 555 {random.randint(1000, 9999)}"

def generate_dates(first_engagement_years_ago: int) -> tuple:
    """Generate engagement and last placement dates."""
    today = datetime.now()
    first_date = today - timedelta(days=first_engagement_years_ago * 365 + random.randint(0, 365))

    # Last placement between first date and now
    days_range = (today - first_date).days
    last_placement_days = random.randint(0, min(days_range, 180))  # Within last 6 months typically
    last_date = today - timedelta(days=last_placement_days)

    return first_date.strftime("%Y-%m-%d"), last_date.strftime("%Y-%m-%d")

def generate_culture_note() -> str:
    """Generate a realistic company culture description."""
    cultures = [
        "Fast-paced startup culture values innovation",
        "Professional formal culture. Strong compliance focus",
        "Mission-driven collaborative culture. Flexible working champion",
        "Traditional engineering culture safety-first mindset",
        "Caring patient-focused culture. High stress environment",
        "Security-conscious remote-first culture. High trust environment",
        "Mission-driven values-led culture. Limited budget",
        "High-performance sales culture competitive environment",
        "Agile fast-paced environment. Strong learning culture",
        "Fast-moving 24/7 operations. Team-focused culture",
        "Academic professional environment. Public sector values",
        "Creative collaborative culture. Fast-paced agency environment",
        "Public sector values. Diversity and inclusion focus",
        "Maritime industry culture. Safety and compliance critical",
        "Fast-paced food industry. Quality and hygiene focus",
        "Academic research environment. Highly specialized roles",
        "Caring nurturing culture. Child safeguarding paramount",
        "Creative gaming culture. Flexible remote-first",
        "Professional regulated environment. FCA compliance critical",
        "Fast-paced delivery culture. Driver recruitment focus",
        "Family business culture. Seasonal workforce",
        "Creative media culture. Deadline-driven environment",
        "FinTech innovation culture. Fast growth environment",
        "Small family business. Traditional values",
        "Technical support culture. Customer service focus",
        "Health and wellness culture. High-energy environment",
        "Traditional construction culture. Safety paramount",
        "Cloud-first remote culture. DevOps focused",
        "Caring animal-focused culture. Clinical excellence",
        "Telecommunications culture. Fast-paced regulated environment",
        "EdTech startup culture. Mission-driven education focus",
        "Professional dental practice. Patient care excellence",
        "Automotive industry culture. Technical expertise valued",
        "Professional legal culture. Client service excellence",
        "Scientific research culture. Regulatory compliance critical",
        "Hospitality culture. Customer service excellence",
        "Outdoor work culture. Environmental values",
        "Data-driven culture. Analytics expertise valued",
        "Caring compassionate culture. CQC regulated",
        "Competitive recruitment culture. Target-driven",
        "Green energy mission. Sustainability values",
        "Aviation safety culture. 24/7 operations",
        "Creative culinary culture. Event-focused",
        "Therapeutic supportive culture. Clinical excellence",
        "Environmental recycling focus. Early starts culture",
        "Fashion retail culture. Customer experience focus",
        "Cutting-edge AI research. Academic collaboration",
        "Traditional B2B sales culture. Relationship-focused"
    ]
    return random.choice(cultures)

def generate_interview_process() -> str:
    """Generate realistic interview process description."""
    processes = [
        "1-stage (Manager interview)",
        "1-stage (Sales Director interview)",
        "1-stage (Owner interview)",
        "1-stage (Director interview)",
        "1-stage (Trial + Interview)",
        "1-stage (Practical + Interview)",
        "1-stage (Store Trial + Interview)",
        "1-stage (Trial Shift + Interview)",
        "1-stage (Interview + Licence Check)",
        "1-stage (Technical + Interview)",
        "2-stage (Technical + Culture)",
        "2-stage (Values + Skills)",
        "2-stage (Manager + Store Visit)",
        "2-stage (Interview + Screen Test)",
        "2-stage (Portfolio + Culture)",
        "2-stage (Competency + Compliance)",
        "2-stage (Technical + Medical)",
        "2-stage (Manager + Team Meet)",
        "2-stage (Interview + DBS Check)",
        "2-stage (Portfolio + Tech Test)",
        "2-stage (Clinical + Cultural)",
        "2-stage (Tech Test + Culture)",
        "2-stage (Technical + Values)",
        "2-stage (Technical Test + Culture)",
        "3-stage (HR + Technical + Director)",
        "3-stage (Technical + Presentation + Panel)",
        "3-stage (Panel + Presentation + HR)",
        "3-stage (Technical + Culture + Security Clearance)",
        "3-stage (Technical + Culture + Executive)",
        "3-stage (Partner + Technical + Client Meeting)",
        "3-stage (Clinical + Supervision + References)",
        "3-stage (Technical + Presentation + References)",
        "3-stage (Technical + Research Presentation + Panel)",
        "3-stage (Panel + Assessment Centre + References)"
    ]
    return random.choice(processes)

def generate_notes(company_name: str, industry: str, services: List[str]) -> str:
    """Generate realistic notes about the client."""
    notes_templates = [
        f"Expanding in Q{random.randint(1,4)} 2025 - expect {random.randint(3,15)} new hires",
        f"Stuart Pearce delivered {random.choice(['sales', 'leadership', 'management', 'customer service'])} training {random.choice(['Nov 2024', 'Dec 2024', 'Jan 2025'])}",
        f"Emma Jane provided wellbeing support - successful outcomes",
        f"{random.choice(['Largest', 'Major', 'Key', 'Important'])} client. {random.choice(['High volume', 'Regular', 'Strategic'])} recruitment needs",
        f"New client. {random.choice(['Growing relationship', 'Building partnership', 'Early engagement'])}",
        f"Seasonal hiring {random.choice(['peaks Q4', 'varies Q1-Q4', 'increases spring/summer'])}",
        f"All roles require {random.choice(['DBS checks', 'security clearance', 'specific certifications'])}",
        f"{random.choice(['Budget-sensitive', 'Cost-conscious', 'Value-focused'])} client. {random.choice(['Competitive rates', 'Negotiated fees', 'Long-term partnership'])}",
        f"High {random.choice(['quality', 'volume', 'specialist'])} recruitment. {random.choice(['Complex', 'Technical', 'Senior'])} roles",
        f"Growing rapidly. {random.choice(['Expansion plans', 'New projects', 'Scaling operations'])} in 2025"
    ]

    note = random.choice(notes_templates)

    # Add service-specific notes
    if "Assessment" in services:
        note += f". Assessment {random.choice(['critical for', 'used for', 'required for'])} {random.choice(['cultural fit', 'senior hires', 'all roles'])}"
    if "Training" in services:
        note += f". {random.choice(['Regular', 'Annual', 'Quarterly'])} training programs"
    if "Contact Centre Consultancy" in services:
        note += ". Contact centre setup/optimization expertise"

    return note

def generate_client(client_id: int, sector_filter: Optional[List[str]] = None) -> Dict:
    """Generate a single fake client record."""
    # Select industry
    if sector_filter:
        available_industries = {k: v for k, v in INDUSTRIES.items()
                               if any(s in v for s in sector_filter)}
        if not available_industries:
            available_industries = INDUSTRIES
    else:
        available_industries = INDUSTRIES

    industry = random.choice(list(available_industries.keys()))
    specialties = available_industries[industry]

    # Generate company details
    company_name, legal_name = generate_company_name()
    company_size = random.choice(COMPANY_SIZES)

    # Determine tier based on size and placements
    size_num = int(company_size.split("-")[0].replace("+", "").replace(",", ""))
    if size_num >= 500 or random.random() < 0.1:
        tier = "Platinum"
        revenue_range = (250000, 500000)
        placements_range = (40, 130)
        active_jobs_range = (5, 12)
    elif size_num >= 150 or random.random() < 0.25:
        tier = "Gold"
        revenue_range = (100000, 250000)
        placements_range = (15, 50)
        active_jobs_range = (2, 7)
    elif size_num >= 80 or random.random() < 0.35:
        tier = "Silver"
        revenue_range = (50000, 120000)
        placements_range = (7, 20)
        active_jobs_range = (1, 4)
    else:
        tier = "Bronze"
        revenue_range = (12000, 50000)
        placements_range = (3, 12)
        active_jobs_range = (0, 2)

    # Generate contacts
    primary_first = random.choice(FIRST_NAMES)
    primary_last = random.choice(LAST_NAMES)
    primary_title = random.choice(JOB_TITLES)
    primary_email = generate_email(primary_first, primary_last, company_name)
    primary_phone = generate_phone()

    # Secondary contact (70% chance)
    if random.random() < 0.7:
        secondary_first = random.choice([n for n in FIRST_NAMES if n != primary_first])
        secondary_last = random.choice([n for n in LAST_NAMES if n != primary_last])
        secondary_title = random.choice([t for t in JOB_TITLES if t != primary_title])
        secondary_email = generate_email(secondary_first, secondary_last, company_name)
        secondary_phone = generate_phone()
    else:
        secondary_first = secondary_last = secondary_title = secondary_email = secondary_phone = "N/A"

    # Address
    street1, street2 = random.choice(BRISTOL_STREETS)
    postcode = random.choice(BRISTOL_POSTCODES)

    # Website and LinkedIn
    domain = company_name.lower().split()[0]
    website = f"www.{domain}.co.uk"
    has_linkedin = random.random() < 0.85
    linkedin = f"linkedin.com/company/{domain}" if has_linkedin else "N/A"

    # Services
    services = random.choice(SERVICE_LINES)
    primary_service = "Contact Centre Consultancy" if "Contact Centre" in specialties and random.random() < 0.3 else "Recruitment"

    # Dates
    years_ago = random.randint(1, 9)
    first_date, last_date = generate_dates(years_ago)

    # Placements and revenue
    total_placements = random.randint(*placements_range)
    active_jobs = random.randint(*active_jobs_range)
    revenue = random.randint(*revenue_range)

    # Financial details
    fee_pct = random.randint(14, 22) + random.choice([0, 0.5])
    payment_terms = random.choice(PAYMENT_TERMS)

    if tier == "Platinum":
        credit_limit = random.randint(80000, 130000)
        payment_history = "Excellent"
    elif tier == "Gold":
        credit_limit = random.randint(45000, 80000)
        payment_history = random.choice(["Excellent", "Good"])
    elif tier == "Silver":
        credit_limit = random.randint(25000, 45000)
        payment_history = random.choice(["Good", "Fair"])
    else:
        credit_limit = random.randint(10000, 25000)
        payment_history = random.choice(["Good", "Fair"])

    # Account manager
    if "Contact Centre" in specialties and tier == "Platinum":
        account_manager = "Contact Centre Specialist"
    else:
        account_manager = "Sam Henderson"

    # Work models and salary
    work_models = random.choice(WORK_MODELS)

    # Salary range based on specialties
    if "Technical" in specialties:
        salary_min = random.randint(25, 38) * 1000
        salary_max = random.randint(55, 95) * 1000
    elif "Accountancy" in specialties:
        salary_min = random.randint(22, 32) * 1000
        salary_max = random.randint(45, 85) * 1000
    elif "Sales" in specialties:
        salary_min = random.randint(20, 30) * 1000
        salary_max = random.randint(40, 75) * 1000
    elif "Contact Centre" in specialties:
        salary_min = random.randint(18, 22) * 1000
        salary_max = random.randint(28, 55) * 1000
    else:  # Commercial
        salary_min = random.randint(19, 28) * 1000
        salary_max = random.randint(32, 65) * 1000

    salary_range = f"£{salary_min}-£{salary_max}"

    # Hiring frequency
    if tier == "Platinum":
        hiring_freq = random.choice(["Weekly", "Monthly"])
    elif tier == "Gold":
        hiring_freq = random.choice(["Monthly", "Quarterly"])
    elif tier == "Silver":
        hiring_freq = random.choice(["Quarterly", "Annually"])
    else:
        hiring_freq = random.choice(["Quarterly", "Annually"])

    # Interview process
    decision_speed = random.choice(DECISION_SPEEDS)
    interview_process = generate_interview_process()
    reference_required = random.choice(["Yes", "No"])
    assessment_required = random.choice(["Yes", "No", "Optional"])

    # Contract details
    rebate_days = random.choice([30, 60, 90, 120])
    replacement_guarantee = "Yes"
    contract_prefs = random.choice(CONTRACT_PREFS)

    # Temp margin
    if "Temporary" in contract_prefs:
        temp_margin = random.randint(35, 42)
    else:
        temp_margin = "N/A"

    # Notes
    notes = generate_notes(company_name, industry, services)

    return {
        "Client ID": f"CLI-{client_id:03d}",
        "Company Name": company_name,
        "Legal Entity Name": legal_name,
        "Industry Sector": industry,
        "Company Size": company_size,
        "Primary Contact First Name": primary_first,
        "Primary Contact Last Name": primary_last,
        "Primary Contact Title": primary_title,
        "Primary Contact Email": primary_email,
        "Primary Contact Phone": primary_phone,
        "Secondary Contact First Name": secondary_first,
        "Secondary Contact Last Name": secondary_last,
        "Secondary Contact Title": secondary_title,
        "Secondary Contact Email": secondary_email,
        "Secondary Contact Phone": secondary_phone,
        "Company Address Line 1": street1,
        "Company Address Line 2": street2,
        "City": "Bristol",
        "County": "Bristol",
        "Postcode": postcode,
        "Country": "United Kingdom",
        "Company Website": website,
        "LinkedIn Profile": linkedin,
        "Service Lines Used": ", ".join(services),
        "Primary Service": primary_service,
        "Account Status": "Active",
        "Account Tier": tier,
        "First Engagement Date": first_date,
        "Last Placement Date": last_date,
        "Total Placements": total_placements,
        "Active Jobs": active_jobs,
        "Lifetime Revenue (£)": revenue,
        "Average Fee Percentage": fee_pct,
        "Preferred Payment Terms": payment_terms,
        "Credit Limit (£)": credit_limit,
        "Payment History": payment_history,
        "Account Manager": account_manager,
        "Recruitment Specialties": ", ".join(specialties),
        "Work Models Offered": ", ".join(work_models),
        "Typical Salary Range": salary_range,
        "Hiring Frequency": hiring_freq,
        "Company Culture Notes": generate_culture_note(),
        "Decision Maker Speed": decision_speed,
        "Interview Process Type": interview_process,
        "Reference Required": reference_required,
        "Assessment Required": assessment_required,
        "Rebate Period Days": rebate_days,
        "Replacement Guarantee": replacement_guarantee,
        "Contract Type Preference": ", ".join(contract_prefs),
        "Temp Margin (%)": temp_margin,
        "Notes": notes
    }

def main():
    parser = argparse.ArgumentParser(description="Generate fake client data for recruitment system")
    parser.add_argument("--count", type=int, default=50, help="Number of clients to generate")
    parser.add_argument("--output", type=str, default="fake_clients.csv", help="Output CSV filename")
    parser.add_argument("--sectors", type=str, help="Comma-separated sectors to filter (e.g., 'Technical,Sales')")

    args = parser.parse_args()

    # Parse sector filter
    sector_filter = None
    if args.sectors:
        sector_filter = [s.strip() for s in args.sectors.split(",")]
        print(f"Filtering for sectors: {', '.join(sector_filter)}")

    print(f"Generating {args.count} fake client records...")

    clients = []
    for i in range(1, args.count + 1):
        client = generate_client(i, sector_filter)
        clients.append(client)

    # Write to CSV
    fieldnames = list(clients[0].keys())
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clients)

    print(f"[OK] Generated {len(clients)} clients")
    print(f"[OK] Saved to {args.output}")

    # Print summary stats
    tiers = {}
    for client in clients:
        tier = client["Account Tier"]
        tiers[tier] = tiers.get(tier, 0) + 1

    print("\nTier Distribution:")
    for tier in ["Platinum", "Gold", "Silver", "Bronze"]:
        if tier in tiers:
            print(f"  {tier}: {tiers[tier]} ({tiers[tier]/len(clients)*100:.1f}%)")

if __name__ == "__main__":
    main()
