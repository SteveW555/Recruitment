# Candidate Database Schema

This document describes the candidate data structures used in the ProActive People recruitment system.

## Supabase Database Schema

The `candidates` table in Supabase contains the following columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| candidate_id | text | NO | Primary key, format: C### (e.g., C001) |
| first_name | text | YES | Candidate's first name |
| last_name | text | YES | Candidate's last name |
| primary_email | text | YES | Primary email address for contact |
| phone_number | text | YES | Contact phone number |
| job_title_target | text | YES | Desired job title/role |
| primary_skills | text | YES | Comma-separated list of key skills |
| industry_experience | text | YES | Industry background/sector experience |
| current_status | text | YES | Recruitment pipeline status (see Status Values below) |
| last_contact_date | text | YES | Date of most recent contact (YYYY-MM-DD format) |
| desired_salary | numeric | YES | Salary expectation in GBP |
| bullhorn_resume_id | text | YES | Reference ID in Bullhorn ATS system |
| interview_notes_sentiment | text | YES | Sentiment analysis of interview feedback |
| gsuite_doc_attached | text | YES | Whether Google Suite documents are attached (Yes/No) |
| recruiter_notes_external | text | YES | Notes suitable for sharing with clients |
| recruiter_notes_internal | text | YES | Internal-only notes and observations |
| created_at | timestamp with time zone | YES | Record creation timestamp |
| updated_at | timestamp with time zone | YES | Last update timestamp |

## Extended CSV Schema

The full candidate CSV files contain additional detailed fields:

### Personal Information
- **Candidate ID**: Unique identifier (format: CAN-### for extended format, C### for simplified)
- **First Name, Last Name**: Full name
- **Email**: Primary contact email
- **Phone**: Contact phone number
- **Date of Birth**: Format: YYYY-MM-DD
- **Address Line 1, Address Line 2**: Street address
- **City**: City of residence
- **County**: County/region
- **Postcode**: UK postcode
- **Country**: Country (typically "United Kingdom")

### Current Employment
- **Current Job Title**: Current or most recent position
- **Years of Experience**: Total years in the industry
- **Current/Last Employer**: Company name (or "Unemployed", "Student")
- **Employment Status**: Current status (Employed, Unemployed, Student, etc.)

### Skills & Qualifications
- **Key Skills**: Comma-separated list of technical and professional skills
- **Certifications**: Professional certifications held
- **Education Level**: Highest qualification (GCSE, A-Level, Bachelor's, Master's, PhD, etc.)
- **Education Details**: Specific degrees, subjects, institutions

### Job Preferences
- **Desired Role**: Target job title
- **Desired Sectors**: Preferred industries (comma-separated)
- **Salary Expectations (£)**: Expected annual salary in GBP
- **Work Model Preference**: Office, Remote, Hybrid
- **Willing to Relocate**: Yes/No
- **Notice Period**: Current notice period or "Immediate"
- **Available Start Date**: Earliest start date (YYYY-MM-DD)

### Recruitment Tracking
- **Registration Date**: Date added to system (YYYY-MM-DD)
- **Status**: Current recruitment pipeline status
- **Assigned Consultant**: Name of assigned recruiter
- **CV Upload Date**: Date CV was received (YYYY-MM-DD)
- **LinkedIn Profile**: LinkedIn URL
- **Portfolio URL**: Portfolio/website link
- **Notes**: General notes and observations

## Status Values

Common candidate statuses in the recruitment pipeline:

- **Active**: Actively seeking roles, available for placements
- **Inactive**: Not currently seeking, but in database
- **Available**: Ready for interviews, no current process
- **Screening**: Initial screening in progress
- **Interviewing - CLT###**: In interview process with specific client
- **Offer Pending - CLT###**: Offer extended, awaiting acceptance
- **Offer Extended**: Offer made, not yet accepted
- **Placed - CLT###**: Successfully placed with client
- **Rejected**: Not progressed after interview/screening
- **Dormant**: No activity for extended period, may be re-engaged

## Sentiment Values

Interview notes sentiment analysis:

- **Highly Positive**: Excellent candidate, strong recommendation
- **Positive**: Good candidate, recommended for progression
- **Neutral**: Acceptable candidate, no strong opinion
- **Negative**: Not recommended or concerns noted

## Integration References

- **Bullhorn Resume ID**: Format: R###A (e.g., R001A)
  - Links to candidate records in Bullhorn ATS
  - Used for bidirectional sync

- **GSuite Doc Attached**: Indicates whether supporting documents are stored in Google Drive
  - Interview feedback documents
  - Compliance forms (G-Sheet, G-Doc references)
  - Client pitch decks
  - Background check forms

## Common Query Patterns

### By Status
```sql
SELECT * FROM candidates WHERE current_status = 'Active';
SELECT * FROM candidates WHERE current_status LIKE 'Interviewing%';
```

### By Skills
```sql
SELECT * FROM candidates WHERE primary_skills ILIKE '%Python%';
SELECT * FROM candidates WHERE primary_skills ILIKE '%DevOps%' AND desired_salary <= 130000;
```

### By Industry
```sql
SELECT * FROM candidates WHERE industry_experience ILIKE '%Software Development%';
```

### By Availability
```sql
SELECT * FROM candidates
WHERE current_status IN ('Active', 'Available')
AND desired_salary BETWEEN 80000 AND 120000;
```

### Recent Contacts
```sql
SELECT * FROM candidates
WHERE last_contact_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY last_contact_date DESC;
```
