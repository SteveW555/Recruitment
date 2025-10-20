# Schema Definitions

Complete field definitions for all recruitment data types.

## Client/Company Schema

### Identification
- **Client ID**: Unique identifier (format: CLI-001, CLI-002, etc.)
- **Company Name**: Trading name (e.g., "TechSphere Solutions Ltd")
- **Legal Entity Name**: Full legal name (e.g., "TechSphere Solutions Limited")

### Business Details
- **Industry Sector**: Primary industry (IT Services, Financial Services, Healthcare, etc.)
- **Company Size**: Employee range (30-40, 150-200, 500+, etc.)

### Primary Contact
- **Primary Contact First Name**
- **Primary Contact Last Name**
- **Primary Contact Title**: Job title (HR Director, Talent Manager, CEO, etc.)
- **Primary Contact Email**: Format businessname.co.uk
- **Primary Contact Phone**: UK format (0117 XXX XXXX)

### Secondary Contact
- **Secondary Contact First Name**
- **Secondary Contact Last Name**
- **Secondary Contact Title**
- **Secondary Contact Email**
- **Secondary Contact Phone**

Note: Some clients may not have secondary contact (use N/A)

### Address
- **Company Address Line 1**: Building/street
- **Company Address Line 2**: Additional address (floor, unit, etc.) - can be empty
- **City**: UK city
- **County**: UK county
- **Postcode**: UK postcode format (BS1 6DZ)
- **Country**: "United Kingdom"

### Online Presence
- **Company Website**: www.companyname.co.uk
- **LinkedIn Profile**: linkedin.com/company/company-name or N/A

### Service Engagement
- **Service Lines Used**: Comma-separated (e.g., "Recruitment, Assessment, Training")
  - Options: Recruitment, Assessment, Training, Wellbeing, Contact Centre Consultancy
- **Primary Service**: Main service (usually "Recruitment")

### Account Status
- **Account Status**: Active / Inactive / On Hold
- **Account Tier**: Bronze / Silver / Gold / Platinum
  - Based on revenue: Bronze (<£50k), Silver (£50-100k), Gold (£100-250k), Platinum (£250k+)

### Relationship Timeline
- **First Engagement Date**: YYYY-MM-DD format
- **Last Placement Date**: YYYY-MM-DD format
- **Total Placements**: Number of successful placements
- **Active Jobs**: Number of currently open positions

### Financial Details
- **Lifetime Revenue (£)**: Total revenue from client (no comma separator in number)
- **Average Fee Percentage**: Typical fee (15-22% range)
- **Preferred Payment Terms**: Net 30 / Net 45 / Net 60
- **Credit Limit (£)**: Maximum credit allowed
- **Payment History**: Excellent / Good / Fair / Poor

### Account Management
- **Account Manager**: Name of ProActive People consultant
  - Sam Henderson (main consultant)
  - Contact Centre Specialist (for CC clients)
  - Others as needed

### Recruitment Profile
- **Recruitment Specialties**: Comma-separated business domains
  - Options: Technical, Sales, Commercial, Accountancy, Contact Centre
- **Work Models Offered**: Comma-separated
  - Options: Office, Hybrid, Remote, Shift Work
- **Typical Salary Range**: £XX000-£XX000 format
- **Hiring Frequency**: Weekly / Monthly / Quarterly / Annually

### Company Culture
- **Company Culture Notes**: Brief description (50-100 chars)
  - Examples: "Fast-paced startup culture", "Professional formal culture", "Mission-driven values-led"

### Recruitment Process
- **Decision Maker Speed**: Very Fast (<1 week) / Fast (1-2 weeks) / Medium (2-4 weeks) / Slow (4+ weeks)
- **Interview Process Type**: Description of stages
  - Examples: "1-stage (Manager interview)", "2-stage (Technical + Culture)", "3-stage (HR + Technical + Director)"
- **Reference Required**: Yes / No
- **Assessment Required**: Yes / No / Optional

### Terms & Conditions
- **Rebate Period Days**: 30 / 60 / 90 / 120
- **Replacement Guarantee**: Yes / No
- **Contract Type Preference**: Comma-separated
  - Options: Permanent, Temporary, Contract
- **Temp Margin (%)**: 35-42 range (N/A for permanent-only clients)

### Additional Notes
- **Notes**: Detailed notes about client (100-200 chars)
  - Include: projects, training history, expansion plans, special requirements

## Candidate Schema

### Identification
- **Candidate ID**: Unique identifier (format: CAN-001, CAN-002, etc.)

### Personal Details
- **First Name**
- **Last Name**
- **Email**: Format: firstname.lastname@email.com
- **Phone**: UK mobile (07XXX XXX XXX) or landline
- **Date of Birth**: YYYY-MM-DD format

### Address
- **Address Line 1**
- **Address Line 2**: Optional
- **City**
- **County**
- **Postcode**
- **Country**: "United Kingdom"

### Professional Profile
- **Current Job Title**: Most recent/current role
- **Years of Experience**: 0-30 range
- **Current/Last Employer**: Company name or "Unemployed" / "Student"
- **Employment Status**: Employed / Unemployed / Notice Period / Student

### Skills & Qualifications
- **Key Skills**: Comma-separated (5-10 skills)
  - Examples: "Python, SQL, AWS, React, Node.js" or "B2B Sales, CRM, Cold Calling, Account Management"
- **Certifications**: Comma-separated or "None"
  - Examples: "AWS Certified, ITIL Foundation" or "None"
- **Education Level**: GCSE / A-Level / Bachelor's / Master's / PhD / Professional
- **Education Details**: University/institution and subject
  - Format: "BSc Computer Science, University of Bristol"

### Job Preferences
- **Desired Role**: Target job title
- **Desired Sectors**: Comma-separated industries
  - Options: IT Services, Finance, Healthcare, Retail, Manufacturing, etc.
- **Salary Expectations (£)**: Desired annual salary
- **Work Model Preference**: Office / Hybrid / Remote / Flexible
- **Willing to Relocate**: Yes / No / Maybe

### Availability
- **Notice Period**: Immediate / 1 week / 2 weeks / 1 month / 2 months / 3 months
- **Available Start Date**: YYYY-MM-DD format

### Candidate Status
- **Registration Date**: YYYY-MM-DD format
- **Status**: Active / Placed / Inactive / On Hold
- **Assigned Consultant**: ProActive People consultant name

### CV & Documents
- **CV Upload Date**: YYYY-MM-DD format
- **LinkedIn Profile**: linkedin.com/in/name or "None"
- **Portfolio URL**: URL or "None"

### Additional Notes
- **Notes**: Brief notes about candidate, preferences, red flags, strengths (100-200 chars)

## Job Schema

### Identification
- **Job ID**: Unique identifier (format: JOB-001, JOB-002, etc.)
- **Client ID**: Reference to client (CLI-001, etc.)

### Job Details
- **Job Title**: Position title
- **Job Description**: Brief 1-2 sentence description
- **Industry Sector**: Aligned with client sector
- **Department**: Sales, IT, Finance, Operations, HR, etc.

### Location & Work Model
- **Location**: City, County
- **Postcode Area**: First part of postcode (BS1, BS16, etc.)
- **Work Model**: Office / Hybrid / Remote / Shift Work
- **Hybrid Details**: If hybrid, specify days (e.g., "3 days office, 2 days home")

### Compensation
- **Salary Min (£)**: Minimum salary
- **Salary Max (£)**: Maximum salary
- **Salary Type**: Annual / Hourly / Daily
- **Benefits**: Comma-separated list
  - Examples: "Pension, Healthcare, Bonus, Car Allowance"

### Requirements
- **Required Experience Years**: 0-15+ range
- **Required Skills**: Comma-separated (5-10 skills)
- **Required Qualifications**: Education/certifications required
- **Nice to Have**: Optional skills/experience

### Job Specifications
- **Contract Type**: Permanent / Temporary / Contract
- **Contract Duration**: If temp/contract, duration (e.g., "6 months", "12 months")
- **Hours Per Week**: 37.5, 40, 35, etc.
- **Start Date**: YYYY-MM-DD or "ASAP" or "Flexible"

### Application Details
- **Posted Date**: YYYY-MM-DD format
- **Application Deadline**: YYYY-MM-DD format
- **Number of Positions**: Usually 1, can be 2-10 for volume hiring
- **Job Status**: Open / Closed / Filled / On Hold

### Recruitment Details
- **Fee Percentage**: Client's agreed fee (15-22%)
- **Assigned Consultant**: ProActive People consultant
- **Priority**: Low / Medium / High / Urgent

### Sourcing
- **Posted on Job Boards**: Yes / No
- **Broadbean Posted**: Yes / No
- **Boards Posted**: If yes, comma-separated list
  - Options: Indeed, Totaljobs, CV-Library, Reed, Jobsite, Jobserve

### Additional Notes
- **Notes**: Special requirements, client preferences, interview process details (100-200 chars)

## Placement Schema

### Identification
- **Placement ID**: Unique identifier (format: PLC-001, PLC-002, etc.)
- **Candidate ID**: Reference (CAN-001, etc.)
- **Job ID**: Reference (JOB-001, etc.)
- **Client ID**: Reference (CLI-001, etc.)

### Placement Details
- **Job Title**: Position title (from job)
- **Contract Type**: Permanent / Temporary / Contract

### Timeline
- **Placement Date**: YYYY-MM-DD (when placement was made)
- **Start Date**: YYYY-MM-DD (candidate's first day)
- **End Date**: YYYY-MM-DD or "N/A" for permanent/ongoing
- **Expected Duration**: For temp/contract (e.g., "6 months", "Ongoing")

### Financial Details
- **Salary/Rate**: Annual salary for permanent, daily/hourly for temp/contract
- **Salary Type**: Annual / Daily / Hourly
- **Fee Amount (£)**: ProActive People's fee
- **Fee Percentage**: Percentage charged
- **Invoice Date**: YYYY-MM-DD
- **Payment Status**: Paid / Outstanding / Overdue / Partial

### Terms
- **Rebate Period Days**: 30 / 60 / 90 / 120
- **Rebate Applicable**: Yes / No
- **Guarantee Period Days**: Usually matches rebate period
- **Probation Period**: 3 months / 6 months / None

### Status Tracking
- **Placement Status**: Active / Completed / Cancelled / Rebated
- **Follow-up Date**: YYYY-MM-DD (for post-placement check-in)
- **Candidate Feedback**: Brief satisfaction note
- **Client Feedback**: Brief satisfaction note

### Account Management
- **Consultant**: ProActive People consultant who made placement

### Additional Notes
- **Notes**: Special arrangements, negotiations, issues, successes (100-200 chars)

## Data Relationships

### Referential Integrity Rules

1. **Jobs reference Clients**
   - Every Job must have a valid Client ID
   - Client must exist before Job is created

2. **Placements reference Candidates, Jobs, and Clients**
   - Candidate ID must exist
   - Job ID must exist
   - Client ID must match the Job's Client ID
   - Placement date must be after Job posted date

3. **Timeline Logic**
   - Placement Date ≥ Job Posted Date
   - Start Date ≥ Placement Date
   - End Date > Start Date (if applicable)
   - Last Placement Date for Client = most recent Placement Date

4. **Financial Consistency**
   - Client's Lifetime Revenue = sum of all placement fees
   - Placement Fee Amount = (Salary × Fee Percentage) / 100
   - Client's Total Placements = count of placements

## Data Generation Best Practices

### Realistic Distributions

**Account Tiers**:
- Bronze: 30%
- Silver: 35%
- Gold: 25%
- Platinum: 10%

**Company Sizes**:
- Small (30-100): 40%
- Medium (100-300): 35%
- Large (300-1000): 20%
- Enterprise (1000+): 5%

**Contract Types**:
- Permanent: 70%
- Temporary: 20%
- Contract: 10%

**Work Models**:
- Office only: 20%
- Hybrid: 50%
- Remote: 25%
- Shift: 5%

**Placement Success Rate**:
- 85-90% of jobs should result in placement
- 10-15% of candidates should have multiple placements
- 5-10% of placements should have issues (rebate, early leaving)

### Data Quality Rules

1. **Email domains match company names**
   - TechSphere → @techsphere.co.uk

2. **Phone area codes match locations**
   - Bristol clients → 0117 prefix
   - Weston-super-Mare → 01934 prefix

3. **Postcodes match cities**
   - Bristol → BS postcodes
   - London → postcodes appropriate to area

4. **Salaries match roles and experience**
   - Junior: Lower end of range
   - Senior: Upper end of range
   - Realistic UK market rates

5. **Dates are logical**
   - First Engagement Date < Last Placement Date
   - Registration Date < Placement Date
   - Years of Experience aligns with age

6. **Consistent specialist naming**
   - Same Account Manager appears across related records
   - Stuart Pearce for training notes
   - Emma Jane for wellbeing notes
   - Contact Centre Specialist for CC clients
