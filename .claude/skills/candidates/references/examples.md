# Candidate Record Examples

This document provides example candidate records to illustrate common scenarios in the ProActive People recruitment system.

## Example 1: Active Software Engineer

**Simplified Format (Supabase):**
```
Candidate ID: C001
Name: Alex Roberts
Email: alex.roberts@email.com
Phone: 555-0101
Job Title Target: Senior Software Engineer
Primary Skills: Python, AWS, Django
Industry Experience: Software Development
Current Status: Interviewing - CLT001
Last Contact Date: 2025-10-19
Desired Salary: £120,000
Bullhorn Resume ID: R001A
Interview Notes Sentiment: Positive
GSuite Doc Attached: Yes
Recruiter Notes (External): TechNova interview feedback attached to G-Doc. Client impressed with AWS certs.
Recruiter Notes (Internal): Very strong fit for CLT001. Needs a quick offer. Check the custom benefits doc.
```

**Extended Format (CSV):**
```
Candidate ID: CAN-001
Name: Jack Williams
Email: jackwilliams@outlook.com
Phone: 07998 794 556
Date of Birth: 2000-01-19
Address: 147 Church Lane, Southville, Weston-super-Mare, Somerset BS7 QT
Current Job Title: IT Support Analyst
Years of Experience: 2
Current/Last Employer: Unemployed
Employment Status: Unemployed
Key Skills: SQL, Data Analysis, Python, Tableau, Excel
Certifications: AWS Certified Developer
Education Level: A-Level
Education Details: A-Levels in Maths, Physics, Chemistry
Desired Role: DevOps Engineer
Desired Sectors: IT Services, Software Development, FinTech
Salary Expectations: £32,162
Work Model Preference: Office
Willing to Relocate: No
Notice Period: Immediate
Available Start Date: 2025-10-31
Registration Date: 2025-02-08
Status: Active
Assigned Consultant: Sam Henderson
CV Upload Date: 2025-02-13
LinkedIn: linkedin.com/in/jack-williams-1657
Notes: Seeking new challenge
```

## Example 2: Placed Candidate (Success Case)

```
Candidate ID: C007
Name: Liam O'Connell
Email: liam.oconnell@email.com
Phone: 555-0107
Job Title Target: Supply Chain Analyst
Primary Skills: Forecasting, Inventory Mgt., SAP
Industry Experience: Agriculture/FMCG
Current Status: Placed - CLT007
Last Contact Date: 2025-07-25
Desired Salary: £80,000
Bullhorn Resume ID: R007A
Interview Notes Sentiment: Highly Positive
GSuite Doc Attached: Yes
Recruiter Notes (External): Confirmed start date: 08/01/2025. Onboarding complete. Follow up required 90 days post-placement.
Recruiter Notes (Internal): Placement confirmed. Check 90-day review schedule G-Doc.
```

## Example 3: Senior Executive (High-Value)

```
Candidate ID: C037
Name: Elena Gilbert
Email: elena.gilbert@email.com
Phone: 555-0137
Job Title Target: Chief Investment Officer (CIO)
Primary Skills: Portfolio Mgt., M&A, Due Diligence
Industry Experience: Finance/Hedge Fund
Current Status: Interviewing - CLT037
Last Contact Date: 2025-10-18
Desired Salary: £350,000
Bullhorn Resume ID: R037A
Interview Notes Sentiment: Highly Positive
GSuite Doc Attached: Yes
Recruiter Notes (External): Sent confidential background checks. Pitch deck in private G-Doc folder.
Recruiter Notes (Internal): Top C-Suite priority. Confidentiality is paramount.
```

## Example 4: Rejected Candidate

```
Candidate ID: C006
Name: Olivia Kim
Email: olivia.kim@email.com
Phone: 555-0106
Job Title Target: Civil Engineer (P.E.)
Primary Skills: Structural Analysis, AutoCAD, Site Management
Industry Experience: Construction & Engineering
Current Status: Rejected
Last Contact Date: 2025-09-01
Desired Salary: £115,000
Bullhorn Resume ID: R006A
Interview Notes Sentiment: Negative
GSuite Doc Attached: No
Recruiter Notes (External): Rejected by CLT006 due to lack of specific bridge experience. Open to other roles.
Recruiter Notes (Internal): Do not pitch to Ironclad Construction again. Too junior.
```

## Example 5: Dormant Candidate (Re-engagement Opportunity)

```
Candidate ID: C019
Name: Dr. Alan Grant
Email: alan.grant@email.com
Phone: 555-0119
Job Title Target: Renewable Energy Analyst
Primary Skills: Market Analysis, Project Finance
Industry Experience: Renewable Energy
Current Status: Dormant
Last Contact Date: 2024-07-01
Desired Salary: £100,000
Bullhorn Resume ID: R019A
Interview Notes Sentiment: Negative
GSuite Doc Attached: No
Recruiter Notes (External): Hasn't responded since Fusion Energy project paused. Keep in the dormant pipeline.
Recruiter Notes (Internal): [blank]
```

## Example 6: Entry-Level Candidate

```
Candidate ID: C040
Name: Jeremy Gilbert
Email: jeremy.gilbert@email.com
Phone: 555-0140
Job Title Target: Barista/Server
Primary Skills: Customer Service, Espresso Skills
Industry Experience: Food & Beverage
Current Status: Available
Last Contact Date: 2025-10-15
Desired Salary: £30,000
Bullhorn Resume ID: R040A
Interview Notes Sentiment: Neutral
GSuite Doc Attached: No
Recruiter Notes (External): Very casual fit. Happy with small cafe work.
Recruiter Notes (Internal): Pitch for Silver Spoon Cafe.
```

## Example 7: Specialized Technical Role

```
Candidate ID: C024
Name: Cece Parekh
Email: cece.parekh@email.com
Phone: 555-0124
Job Title Target: AI Research Scientist
Primary Skills: Deep Learning, Computer Vision
Industry Experience: AI/Robotics
Current Status: Interviewing - CLT024
Last Contact Date: 2025-10-20
Desired Salary: £180,000
Bullhorn Resume ID: R024A
Interview Notes Sentiment: Highly Positive
GSuite Doc Attached: Yes
Recruiter Notes (External): Dr. Reed loves her work. Sent confidential background memo via G-Doc.
Recruiter Notes (Internal): Top priority. High fee role. Ensure all comms are discreet.
```

## Common Search Scenarios

### Scenario 1: Find Python Developers
**Query**: "Find all Python developers available for interview"

**Expected Results**: Candidates with:
- "Python" in primary_skills or key_skills
- Status: Active, Available, or similar ready states
- Example: C001 (Alex Roberts), CAN-001 (Jack Williams)

### Scenario 2: High Salary Senior Roles
**Query**: "Show me candidates earning over £100k"

**Expected Results**: Candidates with:
- desired_salary or salary_expectations > 100000
- Examples: C001 (£120k), C037 (£350k), C024 (£180k)

### Scenario 3: Recently Active Candidates
**Query**: "Who have we contacted in the last week?"

**Expected Results**: Candidates with:
- last_contact_date within past 7 days
- Ordered by most recent first

### Scenario 4: DevOps Engineers in FinTech
**Query**: "Find DevOps engineers interested in FinTech"

**Expected Results**: Candidates with:
- Skills containing "DevOps", "Kubernetes", "Docker", "CI/CD", etc.
- Industry experience or desired sectors including "FinTech" or "Financial Services"
- Example: CAN-001 (Jack Williams - DevOps target, FinTech sector)

### Scenario 5: Immediate Start Availability
**Query**: "Which candidates can start immediately?"

**Expected Results**: Candidates with:
- Notice period = "Immediate"
- Employment status = "Unemployed" or similar
- Status = "Active" or "Available"
