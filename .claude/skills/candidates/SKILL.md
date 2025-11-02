---
name: candidates
description: Expert in candidate management for the ProActive People recruitment system. Specializes in candidate database operations (CRUD), searching/filtering by skills, status, industry, and salary, generating candidate reports, analyzing pipeline status, and understanding UK recruitment workflows. This skill should be used when working with candidate data, querying the candidates table, analyzing candidate pipelines, matching candidates to roles, or answering questions about candidate records in the recruitment system.
---

# Candidates Skill

## Purpose

This skill provides comprehensive guidance for working with candidate data in the ProActive People recruitment automation system. It enables effective candidate management through database operations, intelligent searching and filtering, pipeline analysis, and integration with external systems like Bullhorn ATS and Google Suite.

## When to Use This Skill

Use this skill when:

- **Searching or filtering candidates** by skills, status, industry experience, salary range, availability, or location
- **Creating new candidate records** from CVs, application forms, or manual entry
- **Updating candidate information** including status changes, contact details, notes, or interview feedback
- **Generating candidate reports** such as pipeline summaries, skill inventories, or placement statistics
- **Matching candidates to job opportunities** based on skills, experience, and preferences
- **Analyzing candidate data** for trends, sourcing effectiveness, or consultant performance
- **Managing candidate lifecycle** through recruitment pipeline stages
- **Querying the candidates table** in the Supabase database
- **Working with candidate CSV data** for imports, exports, or bulk operations
- **Answering questions about specific candidates** or candidate demographics

## Core Concepts

### Candidate Data Structures

The system uses two main candidate data formats:

1. **Supabase Database Format** - Simplified format optimized for fast queries and API operations (18 fields)
2. **Extended CSV Format** - Comprehensive format with full candidate details (33+ fields)

Both formats are fully documented in `references/schema.md`. Review this file to understand:
- Complete field definitions and data types
- Status values and their meanings
- Sentiment analysis categories
- Integration references (Bullhorn, GSuite)
- Common SQL query patterns

### Recruitment Pipeline Stages

Candidates progress through these typical stages:

```
Sourced → Screening → Submitted → Interviewing → Offer → Placed → Follow-up
```

**Status Values:**
- **Active**: Currently seeking roles
- **Available**: Ready for immediate interviews
- **Screening**: Initial assessment in progress
- **Interviewing - CLT###**: In active interview process with specific client
- **Offer Pending/Extended**: Offer made, awaiting acceptance
- **Placed - CLT###**: Successfully placed with client
- **Rejected**: Not progressed after assessment
- **Dormant**: Inactive but may be re-engaged
- **Inactive**: Not currently seeking

## How to Use This Skill

### Step 1: Understand the Data Structure

When working with candidate data, first consult `references/schema.md` to:
- Identify which fields are available in the current data format
- Understand data types and nullable constraints
- Review common query patterns for the operation needed
- Check status values and their meanings

### Step 2: Review Example Records

For context on realistic candidate data, review `references/examples.md` to see:
- Complete candidate records in both formats
- Examples across different seniority levels (entry-level to C-suite)
- Various pipeline statuses (active, placed, rejected, dormant)
- Different industries and skill sets
- Common search scenarios with expected results

### Step 3: Perform Database Operations

#### Searching and Filtering Candidates

**By Skills:**
```sql
SELECT * FROM candidates
WHERE primary_skills ILIKE '%Python%'
AND current_status IN ('Active', 'Available');
```

**By Salary Range:**
```sql
SELECT * FROM candidates
WHERE desired_salary BETWEEN 80000 AND 120000
AND current_status = 'Active'
ORDER BY desired_salary DESC;
```

**By Industry:**
```sql
SELECT * FROM candidates
WHERE industry_experience ILIKE '%FinTech%'
OR industry_experience ILIKE '%Financial Services%';
```

**By Status:**
```sql
-- All candidates in active interview processes
SELECT * FROM candidates
WHERE current_status LIKE 'Interviewing%';

-- Recently placed candidates
SELECT * FROM candidates
WHERE current_status LIKE 'Placed%'
AND last_contact_date >= CURRENT_DATE - INTERVAL '30 days';
```

**Complex Multi-Criteria Searches:**
```sql
SELECT candidate_id, first_name, last_name, job_title_target,
       primary_skills, desired_salary, current_status
FROM candidates
WHERE primary_skills ILIKE '%DevOps%'
AND (industry_experience ILIKE '%Software%' OR industry_experience ILIKE '%IT Services%')
AND desired_salary <= 130000
AND current_status IN ('Active', 'Available')
ORDER BY desired_salary ASC, last_contact_date DESC;
```

#### Creating New Candidate Records

When creating a new candidate record, ensure:
- **candidate_id** follows format: C### (e.g., C050, C051) for Supabase format or CAN-### for extended format
- **Required fields**: first_name, last_name, primary_email, current_status
- **Recommended fields**: phone_number, job_title_target, primary_skills, desired_salary
- **Set timestamps**: created_at and updated_at to current timestamp

```sql
INSERT INTO candidates (
    candidate_id, first_name, last_name, primary_email, phone_number,
    job_title_target, primary_skills, industry_experience,
    current_status, desired_salary, created_at, updated_at
) VALUES (
    'C050', 'Jane', 'Smith', 'jane.smith@email.com', '555-0150',
    'Full Stack Developer', 'React, Node.js, PostgreSQL, AWS',
    'Software Development', 'Active', 95000,
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);
```

#### Updating Candidate Records

**Status Updates:**
```sql
UPDATE candidates
SET current_status = 'Interviewing - CLT025',
    last_contact_date = CURRENT_DATE,
    updated_at = CURRENT_TIMESTAMP
WHERE candidate_id = 'C042';
```

**Adding Notes:**
```sql
UPDATE candidates
SET recruiter_notes_internal = 'Strong technical interview. Recommend progression to client meeting.',
    interview_notes_sentiment = 'Positive',
    updated_at = CURRENT_TIMESTAMP
WHERE candidate_id = 'C042';
```

**Salary Negotiations:**
```sql
UPDATE candidates
SET desired_salary = 105000,
    recruiter_notes_internal = 'Negotiated up from 100k. Client approved.',
    updated_at = CURRENT_TIMESTAMP
WHERE candidate_id = 'C013';
```

#### Generating Reports

**Pipeline Summary:**
```sql
SELECT current_status, COUNT(*) as count,
       AVG(desired_salary) as avg_salary
FROM candidates
WHERE current_status NOT IN ('Rejected', 'Dormant', 'Inactive')
GROUP BY current_status
ORDER BY count DESC;
```

**Skills Inventory:**
```sql
SELECT primary_skills, COUNT(*) as candidate_count
FROM candidates
WHERE current_status IN ('Active', 'Available')
GROUP BY primary_skills
ORDER BY candidate_count DESC
LIMIT 20;
```

**Consultant Performance:**
```sql
-- For extended format with assigned_consultant field
SELECT assigned_consultant,
       COUNT(CASE WHEN current_status LIKE 'Placed%' THEN 1 END) as placements,
       COUNT(*) as total_candidates,
       AVG(desired_salary) as avg_candidate_salary
FROM candidates
GROUP BY assigned_consultant
ORDER BY placements DESC;
```

**Recent Activity:**
```sql
SELECT candidate_id, first_name, last_name, current_status,
       last_contact_date, job_title_target
FROM candidates
WHERE last_contact_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY last_contact_date DESC;
```

### Step 4: Handle Integration References

#### Bullhorn ATS Integration

When candidates have a **bullhorn_resume_id** (format: R###A):
- This links to their record in the Bullhorn ATS system
- Used for bidirectional synchronization
- CV/resume files are stored in Bullhorn
- Update both systems when making changes to key fields

#### Google Suite Documents

When **gsuite_doc_attached = 'Yes'**:
- Interview feedback may be in Google Docs
- Compliance forms may be in Google Sheets
- Client pitch decks may be attached
- References to specific G-Docs/G-Sheets should be in notes fields
- Examples: "Interview prep notes in G-Doc", "Check 'Q4 Hiring' G-Sheet status"

### Step 5: Consider Data Quality

When working with candidate data:

**Validation Checks:**
- Email format is valid
- Phone numbers follow expected format
- Salary values are reasonable for role/seniority
- Status values match defined statuses
- Dates are in correct format (YYYY-MM-DD)

**Data Enrichment:**
- Add LinkedIn profiles when available
- Record certifications and qualifications
- Capture salary expectations early
- Note work model preferences (remote/hybrid/office)
- Document notice periods and availability

**Privacy and Compliance:**
- Candidate data is subject to GDPR regulations
- Be cautious with PII in external notes
- Ensure data retention policies are followed
- Right to erasure requests must be honored
- Audit trails should be maintained

## Common Workflows

### Workflow 1: Candidate Sourcing

1. Create new candidate record with basic details
2. Set status to 'Active' or 'Screening'
3. Assign to consultant
4. Upload CV to Bullhorn and record bullhorn_resume_id
5. Add initial notes about source and suitability

### Workflow 2: Interview Process

1. Update status to 'Interviewing - CLT###' when submitted
2. Record interview date in last_contact_date
3. Add interview feedback to recruiter_notes_external
4. Set interview_notes_sentiment based on feedback
5. Update gsuite_doc_attached if feedback doc created

### Workflow 3: Placement

1. Update status to 'Offer Pending - CLT###' when offer made
2. Record offer details in internal notes
3. When accepted, change status to 'Placed - CLT###'
4. Schedule 90-day follow-up review
5. Update last_contact_date to start date

### Workflow 4: Re-engagement of Dormant Candidates

1. Query for dormant candidates with relevant skills
2. Review last_contact_date and reason for dormancy
3. Check if new roles match their profile
4. Update status to 'Active' if successfully re-engaged
5. Record new contact date and notes

### Workflow 5: Candidate Matching

1. Receive job requirements from client
2. Search candidates by key skills and industry
3. Filter by salary range and availability
4. Review interview sentiment and notes
5. Present shortlist ordered by fit score

## Best Practices

### Searching
- Use ILIKE for case-insensitive text searches
- Use LIKE with wildcards (%) for partial matches
- Combine multiple criteria with AND/OR for precise results
- Consider NULL values in queries (IS NULL / IS NOT NULL)
- Order results by relevance (salary, last_contact_date, status)

### Data Entry
- Always update `updated_at` timestamp when modifying records
- Use consistent status values from defined list
- Keep external notes professional and client-appropriate
- Use internal notes for sensitive observations
- Record Bullhorn and GSuite references for traceability

### Performance
- Index frequently queried fields (status, skills, industry)
- Use LIMIT for large result sets
- Avoid SELECT * when only specific fields are needed
- Consider pagination for reporting queries

### Communication
- When presenting candidate lists, include key fields: name, title, skills, salary, status
- Format salary values with currency symbols (£)
- Present dates in readable format (DD/MM/YYYY for UK context)
- Highlight urgent actions (immediate availability, expiring offers)

## Troubleshooting

**Issue**: No candidates found in search
- Check if search criteria are too restrictive
- Verify status filters include appropriate values
- Test with broader skill searches (partial matches)
- Check for typos in skill names or industries

**Issue**: Duplicate candidate records
- Search by email or phone before creating new records
- Check both candidate_id formats (C### vs CAN-###)
- Review Bullhorn resume IDs for existing links

**Issue**: Missing candidate data
- Check if data exists in extended CSV format
- Verify Supabase sync is up to date
- Review bullhorn_resume_id for source of truth
- Check gsuite_doc_attached for external documents

**Issue**: Incorrect status values
- Verify status matches defined list in schema
- Check for typos or extra spaces
- Ensure client IDs are correct (CLT### format)
- Update status according to actual pipeline stage

## Quick Reference

**Most Common Queries:**
```sql
-- Active candidates with specific skill
SELECT * FROM candidates WHERE primary_skills ILIKE '%[SKILL]%' AND current_status = 'Active';

-- Recent placements
SELECT * FROM candidates WHERE current_status LIKE 'Placed%' ORDER BY last_contact_date DESC LIMIT 10;

-- High-value candidates
SELECT * FROM candidates WHERE desired_salary > 100000 ORDER BY desired_salary DESC;

-- Available for immediate start
SELECT * FROM candidates WHERE current_status = 'Available' OR current_status = 'Active';

-- Candidates by consultant
SELECT * FROM candidates WHERE assigned_consultant = '[NAME]';
```

**Key Fields for Display:**
- candidate_id, first_name, last_name
- job_title_target
- primary_skills
- desired_salary
- current_status
- last_contact_date

**Critical Actions:**
- Always update `updated_at` when modifying records
- Record contact dates to track engagement
- Use appropriate status values for pipeline tracking
- Maintain both internal and external notes
- Link to Bullhorn and GSuite references
