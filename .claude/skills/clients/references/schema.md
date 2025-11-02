# Clients Table Schema

Complete database schema for the `clients` table in Supabase PostgreSQL database.

## Table: clients

**Total Columns**: 50
**Primary Key**: client_id
**Records**: 50 clients

## Column Definitions

### Identification & Basic Information (5 columns)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `client_id` | TEXT (PK) | Unique client identifier | CLI-001, CLI-002 |
| `company_name` | TEXT | Trading name of the company | TechSphere Solutions Ltd |
| `legal_entity_name` | TEXT | Official registered company name | TechSphere Solutions Limited |
| `industry_sector` | TEXT | Industry classification | IT Services & Consulting |
| `company_size` | TEXT | Employee count range | 150-200, 500+ |

### Primary Contact Information (5 columns)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `primary_contact_first_name` | TEXT | First name of main contact | Sarah |
| `primary_contact_last_name` | TEXT | Last name of main contact | Mitchell |
| `primary_contact_title` | TEXT | Job title of main contact | HR Director |
| `primary_contact_email` | TEXT | Email address | sarah.mitchell@techsphere.co.uk |
| `primary_contact_phone` | TEXT | Phone number | 0117 555 1234 |

### Secondary Contact Information (5 columns)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `secondary_contact_first_name` | TEXT | First name of backup contact | James |
| `secondary_contact_last_name` | TEXT | Last name of backup contact | Wong |
| `secondary_contact_title` | TEXT | Job title of backup contact | Technical Lead |
| `secondary_contact_email` | TEXT | Email address | james.wong@techsphere.co.uk |
| `secondary_contact_phone` | TEXT | Phone number | 0117 555 1235 |

### Address Information (6 columns)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `company_address_line_1` | TEXT | First line of address | Bristol Technology Park |
| `company_address_line_2` | TEXT | Second line of address | 3rd Floor Building A |
| `city` | TEXT | City name | Bristol |
| `county` | TEXT | County name | Bristol |
| `postcode` | TEXT | UK postcode | BS16 1QD |
| `country` | TEXT | Country | United Kingdom |

### Online Presence (2 columns)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `company_website` | TEXT | Company website URL | www.techsphere.co.uk |
| `linkedin_profile` | TEXT | LinkedIn company page | linkedin.com/company/techsphere |

### Service Details (4 columns)

| Column | Type | Description | Example | Valid Values |
|--------|------|-------------|---------|--------------|
| `service_lines_used` | TEXT | Comma-separated services | Recruitment, Assessment, Training | Recruitment, Assessment, Training, Wellbeing, Contact Centre Consultancy |
| `primary_service` | TEXT | Main service utilized | Recruitment | Same as service_lines_used |
| `account_status` | TEXT | Current account state | Active | Active, On Hold, Inactive, Churned |
| `account_tier` | TEXT | Account classification | Gold | Platinum, Gold, Silver, Bronze |

### Engagement History (4 columns)

| Column | Type | Description | Example | Notes |
|--------|------|-------------|---------|-------|
| `first_engagement_date` | DATE | Date of first business | 2019-03-15 | YYYY-MM-DD format |
| `last_placement_date` | DATE | Most recent placement | 2024-12-10 | YYYY-MM-DD format |
| `total_placements` | INTEGER | Lifetime placement count | 28 | Cumulative total |
| `active_jobs` | INTEGER | Current open positions | 3 | Real-time count |

### Financial Metrics (6 columns)

| Column | Type | Description | Example | Notes |
|--------|------|-------------|---------|-------|
| `lifetime_revenue_gbp` | NUMERIC(12,2) | Total revenue generated | 185000.00 | British Pounds Sterling |
| `average_fee_percentage` | NUMERIC(5,2) | Typical placement fee | 18.50 | Percentage (e.g., 18.5%) |
| `preferred_payment_terms` | TEXT | Payment schedule | Net 30 | Net 30, Net 45, Net 60 |
| `credit_limit_gbp` | NUMERIC(12,2) | Maximum credit allowed | 50000.00 | British Pounds Sterling |
| `payment_history` | TEXT | Payment track record | Excellent | Excellent, Good, Fair, Poor |
| `temp_margin_percent` | NUMERIC(5,2) | Temporary worker margin | 35.00 | Percentage, nullable |

### Account Management (5 columns)

| Column | Type | Description | Example | Notes |
|--------|------|-------------|---------|-------|
| `account_manager` | TEXT | Assigned account owner | Sam Henderson | 98% managed by Sam Henderson |
| `recruitment_specialties` | TEXT | Job categories recruited | Technical, Sales | Comma-separated |
| `work_models_offered` | TEXT | Work arrangements | Office, Hybrid, Remote | Comma-separated |
| `typical_salary_range` | TEXT | Standard compensation range | £25000-£65000 | UK currency format |
| `hiring_frequency` | TEXT | Recruitment cadence | Monthly | Weekly, Monthly, Quarterly, Annually |

### Company & Process Details (8 columns)

| Column | Type | Description | Example | Notes |
|--------|------|-------------|---------|-------|
| `company_culture_notes` | TEXT | Cultural description | Fast-paced startup culture values innovation | Free-form text |
| `decision_maker_speed` | TEXT | Time to hire decision | Fast (1-2 weeks) | Very Fast (<1 week), Fast (1-2 weeks), Medium (2-4 weeks), Slow (4-12 weeks) |
| `interview_process_type` | TEXT | Interview stages | 2-stage (Technical + Culture) | 1-stage, 2-stage, 3-stage with description |
| `reference_required` | BOOLEAN | References needed? | true | true/false |
| `assessment_required` | BOOLEAN | Assessment needed? | true | true/false, nullable for Optional |
| `rebate_period_days` | INTEGER | Rebate window | 90 | Days (60, 90, 120 typical) |
| `replacement_guarantee` | BOOLEAN | Replacement offered? | true | true/false |
| `contract_type_preference` | TEXT | Employment types | Permanent, Contract | Comma-separated |

### Metadata (2 columns)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `notes` | TEXT | Additional information | Cloud migration project starting Q2 2025 - expect 5-8 technical hires |
| `created_at` | TIMESTAMP | Record creation timestamp | 2025-10-21 06:33:49.032166+00 |
| `updated_at` | TIMESTAMP | Last update timestamp | 2025-10-21 06:33:49.032166+00 |

## Data Types Reference

### TEXT Fields
Most columns use TEXT for flexibility. Use `ILIKE` for case-insensitive searches:
```sql
WHERE company_name ILIKE '%tech%'
WHERE service_lines_used ILIKE '%Wellbeing%'
```

### NUMERIC Fields
Financial fields use NUMERIC(precision, scale). Cast explicitly for calculations:
```sql
SELECT SUM(lifetime_revenue_gbp::numeric) as total
SELECT AVG(average_fee_percentage::numeric) as avg_fee
```

### BOOLEAN Fields
Store true/false values. Filter with direct comparison:
```sql
WHERE reference_required = true
WHERE assessment_required = false
```

### DATE Fields
Use standard SQL date functions:
```sql
WHERE first_engagement_date >= '2020-01-01'
WHERE last_placement_date BETWEEN '2024-01-01' AND '2024-12-31'
```

### TIMESTAMP Fields
Automatically managed by database. Include timezone:
```sql
WHERE created_at > '2025-01-01 00:00:00+00'
ORDER BY updated_at DESC
```

## Enumerated Values

### account_tier
- `Platinum` - Top 5 clients, £285k-£475k revenue
- `Gold` - 19 clients, £89k-£268k revenue
- `Silver` - 16 clients, £38k-£87k revenue
- `Bronze` - 10 clients, £14k-£56k revenue

### account_status
- `Active` - Current business relationship (50/50 clients)
- `On Hold` - Temporarily paused (0 clients)
- `Inactive` - No recent activity (0 clients)
- `Churned` - Lost client (0 clients)

### payment_history
- `Excellent` - 27 clients (54%)
- `Good` - 21 clients (42%)
- `Fair` - 2 clients (4%)
- `Poor` - 0 clients

### preferred_payment_terms
- `Net 30` - 31 clients (62%)
- `Net 45` - 11 clients (22%)
- `Net 60` - 8 clients (16%)

### decision_maker_speed
- `Very Fast (<1 week)` - 6 clients
- `Fast (1-2 weeks)` - 17 clients
- `Medium (2-4 weeks)` - 16 clients
- `Slow (4-12 weeks)` - 11 clients

### hiring_frequency
- `Weekly` - 6 clients (high-volume)
- `Monthly` - 15 clients
- `Quarterly` - 21 clients (most common)
- `Annually` - 8 clients

### service_lines_used (comma-separated)
- `Recruitment` - Core service (100% of clients)
- `Assessment` - 19 clients (38%)
- `Training` - 17 clients (34%), delivered by Stuart Pearce
- `Wellbeing` - 7 clients (14%), delivered by Emma Jane
- `Contact Centre Consultancy` - 2 clients (4%), specialist service

### recruitment_specialties (comma-separated)
- `Technical` - 23 clients (IT, Software, Engineering)
- `Commercial` - 28 clients (Office, Operations, Admin)
- `Sales` - 13 clients (Business Development, Account Management)
- `Contact Centre` - 10 clients (Customer Service, Telesales)
- `Accountancy` - 4 clients (Finance, Tax, Audit)

### work_models_offered (comma-separated)
- `Office` - Traditional on-site work
- `Hybrid` - Mix of office and remote
- `Remote` - Fully remote work

## Common Query Patterns

### Search by Service
```sql
-- Single service
WHERE service_lines_used ILIKE '%Wellbeing%'

-- Multiple services (cross-sell opportunities)
WHERE service_lines_used ILIKE '%,%,%'

-- Clients NOT using a service
WHERE service_lines_used NOT ILIKE '%Assessment%'
```

### Numeric Comparisons
```sql
-- Revenue thresholds
WHERE lifetime_revenue_gbp::numeric > 200000

-- Fee percentage analysis
WHERE average_fee_percentage::numeric >= 20

-- Active jobs
WHERE active_jobs >= 5
```

### Date Ranges
```sql
-- Recent placements
WHERE last_placement_date >= CURRENT_DATE - INTERVAL '30 days'

-- Long-term relationships
WHERE first_engagement_date <= '2020-01-01'

-- Client age calculation
WHERE EXTRACT(YEAR FROM AGE(CURRENT_DATE, first_engagement_date)) >= 5
```

### Geographic Filters
```sql
-- Bristol city centre
WHERE postcode LIKE 'BS1%' OR postcode LIKE 'BS2%' OR postcode LIKE 'BS8%'

-- Specific city
WHERE city = 'Bristol'

-- County-level
WHERE county = 'Somerset'
```

### Industry Searches
```sql
-- Technology sector (flexible matching)
WHERE industry_sector ILIKE '%IT%'
   OR industry_sector ILIKE '%Tech%'
   OR industry_sector ILIKE '%Software%'

-- Financial services
WHERE industry_sector ILIKE '%Financial%'
   OR industry_sector ILIKE '%Banking%'
   OR industry_sector ILIKE '%FinTech%'
```

## Nullable Fields

The following fields may contain NULL values:
- `secondary_contact_*` (5 fields) - Some clients don't provide backup contacts
- `company_address_line_2` - Not all addresses need second line
- `linkedin_profile` - Some clients don't have LinkedIn presence
- `temp_margin_percent` - Only applies to clients using temporary workers
- `assessment_required` - Can be NULL to indicate "Optional"

When querying nullable fields, handle NULL explicitly:
```sql
WHERE secondary_contact_email IS NOT NULL
WHERE temp_margin_percent IS NOT NULL
WHERE assessment_required IS NOT NULL  -- true or false, not Optional
```

## Performance Tips

1. **Index Usage**: The primary key `client_id` is indexed. Searches on this field are fastest.
2. **ILIKE Performance**: Use specific patterns when possible (`'%word%'` is slower than `'word%'`)
3. **Limit Results**: Always use `LIMIT` for exploratory queries
4. **Aggregate Carefully**: Use `GROUP BY` efficiently when aggregating large result sets
5. **Type Casting**: Cast numeric fields once in SELECT or WHERE, not repeatedly

## Data Quality Notes

- All 50 clients have `Active` status
- 96% have Good or Excellent payment history
- No duplicate client_ids (enforced by PRIMARY KEY)
- All dates are valid and within realistic business ranges (2016-2025)
- Revenue values range from £14,000 to £475,000
- This is synthetic test data for development and testing purposes
