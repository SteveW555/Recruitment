---
name: clients
description: Expert in ProActive People's client database for querying client information, analyzing account tiers, revenue patterns, industry sectors, service utilization, and business relationships. Use this skill when working with client data, querying the Supabase 'clients' table, analyzing client portfolios, finding clients by criteria, or answering questions about ProActive People's client base.
---

# Clients Database Skill

## Purpose

This skill provides comprehensive knowledge of ProActive People's client database structure, business logic, and analytics capabilities. Use this skill to query client information, analyze account performance, understand industry distributions, and extract business insights from the 50-client portfolio stored in the Supabase 'clients' table.

## When to Use This Skill

Use this skill proactively when:
- Querying client information from the Supabase database
- Finding clients by specific criteria (tier, industry, location, services)
- Analyzing revenue patterns and account performance
- Understanding client relationships and account management
- Answering questions about hiring patterns and decision-making speeds
- Identifying cross-sell opportunities for services
- Reviewing payment terms and financial metrics
- Examining geographic or industry distributions

## Database Access

The client data is stored in a Supabase PostgreSQL database accessible via the Supabase MCP tools:

- **Table name**: `clients`
- **Total records**: 50 clients
- **Columns**: 50 fields covering identification, contacts, financials, services, and metadata

## Key Database Queries

### Basic Client Lookup

```sql
-- Get specific client by ID
SELECT * FROM clients WHERE client_id = 'CLI-001';

-- Get client by company name
SELECT * FROM clients WHERE company_name ILIKE '%TechSphere%';
```

### Filtering by Account Tier

```sql
-- Platinum tier clients (top 5)
SELECT client_id, company_name, lifetime_revenue_gbp, total_placements
FROM clients
WHERE account_tier = 'Platinum'
ORDER BY lifetime_revenue_gbp DESC;

-- Gold tier clients
SELECT client_id, company_name, industry_sector, lifetime_revenue_gbp
FROM clients
WHERE account_tier = 'Gold'
ORDER BY lifetime_revenue_gbp DESC;
```

### Industry Analysis

```sql
-- Clients by industry sector
SELECT industry_sector, COUNT(*) as client_count,
       SUM(lifetime_revenue_gbp::numeric) as total_revenue
FROM clients
GROUP BY industry_sector
ORDER BY total_revenue DESC;

-- Technology sector clients
SELECT client_id, company_name, total_placements, active_jobs
FROM clients
WHERE industry_sector ILIKE '%IT%' OR industry_sector ILIKE '%Tech%'
ORDER BY lifetime_revenue_gbp DESC;
```

### Service Line Analysis

```sql
-- Clients using multiple services
SELECT client_id, company_name, service_lines_used, lifetime_revenue_gbp
FROM clients
WHERE service_lines_used ILIKE '%,%,%'
ORDER BY lifetime_revenue_gbp DESC;

-- Clients using Wellbeing service
SELECT client_id, company_name, industry_sector
FROM clients
WHERE service_lines_used ILIKE '%Wellbeing%';

-- Clients using Assessment service
SELECT client_id, company_name, account_tier
FROM clients
WHERE service_lines_used ILIKE '%Assessment%';
```

### Geographic Queries

```sql
-- Bristol city centre clients (BS1, BS2, BS8)
SELECT client_id, company_name, postcode, industry_sector
FROM clients
WHERE postcode LIKE 'BS1%' OR postcode LIKE 'BS2%' OR postcode LIKE 'BS8%'
ORDER BY lifetime_revenue_gbp DESC;

-- All clients by city
SELECT city, COUNT(*) as client_count
FROM clients
GROUP BY city
ORDER BY client_count DESC;
```

### Active Jobs and Hiring

```sql
-- Clients with most active jobs
SELECT client_id, company_name, active_jobs, hiring_frequency
FROM clients
WHERE active_jobs > 0
ORDER BY active_jobs DESC
LIMIT 10;

-- Fast hiring clients (potential quick placements)
SELECT client_id, company_name, decision_maker_speed, interview_process_type
FROM clients
WHERE decision_maker_speed IN ('Very Fast (<1 week)', 'Fast (1-2 weeks)')
ORDER BY active_jobs DESC;
```

### Financial Queries

```sql
-- Top revenue clients
SELECT client_id, company_name, lifetime_revenue_gbp, total_placements, account_tier
FROM clients
ORDER BY lifetime_revenue_gbp DESC
LIMIT 10;

-- Payment terms analysis
SELECT preferred_payment_terms, COUNT(*) as client_count,
       AVG(lifetime_revenue_gbp::numeric) as avg_revenue
FROM clients
GROUP BY preferred_payment_terms;

-- Excellent payment history clients with credit available
SELECT client_id, company_name, credit_limit_gbp, payment_history
FROM clients
WHERE payment_history = 'Excellent'
ORDER BY credit_limit_gbp DESC;
```

### Account Management

```sql
-- Clients by account manager
SELECT account_manager, COUNT(*) as client_count,
       SUM(lifetime_revenue_gbp::numeric) as total_revenue
FROM clients
GROUP BY account_manager;

-- Sam Henderson's portfolio
SELECT client_id, company_name, account_tier, lifetime_revenue_gbp
FROM clients
WHERE account_manager = 'Sam Henderson'
ORDER BY account_tier, lifetime_revenue_gbp DESC;
```

## Business Intelligence

### Account Tiers

**Platinum Tier** (5 clients, 10%):
- Revenue range: £285,000 - £475,000
- Average revenue: £379,600
- High-volume or high-value relationships
- Often use multiple services
- Top clients: Fusion Telecom (CLI-032), Call Centre Excellence (CLI-003)

**Gold Tier** (19 clients, 38%):
- Revenue range: £89,000 - £268,000
- Average revenue: £202,368
- Strong engagement with consistent placements
- Mix of sectors and services

**Silver Tier** (16 clients, 32%):
- Revenue range: £38,000 - £87,000
- Average revenue: £108,250
- Growth potential accounts
- Established businesses

**Bronze Tier** (10 clients, 20%):
- Revenue range: £14,000 - £56,000
- Average revenue: £49,300
- Newer relationships or specialist/niche sectors
- Often have excellent growth potential

### Service Lines

1. **Recruitment**: 50/50 clients (100%) - Core service
2. **Assessment**: 19/50 clients (38%) - Premium service
3. **Training**: 17/50 clients (34%) - Delivered by Stuart Pearce
4. **Wellbeing**: 7/50 clients (14%) - Delivered by Emma Jane
5. **Contact Centre Consultancy**: 2/50 clients (4%) - Specialist service

**Key Insight**: Clients using multiple services generate 2.3x higher revenue on average (£215,333 vs £93,478).

### Industry Distribution

Top sectors by client count:
1. **Technology & IT**: 11 clients (22%) - Software, Cybersecurity, Cloud
2. **Commercial/Professional Services**: Multiple clients across sectors
3. **Healthcare & Social Care**: 6 clients (12%)
4. **Retail & E-commerce**: 4 clients (8%)
5. **Financial Services**: 4 clients (8%) - High average revenue

### Geographic Insights

- **Bristol City Centre** (BS1, BS2, BS8): 32 clients (64%)
- **Bristol Outer Areas**: 12 clients (24%)
- **Weston-super-Mare**: 1 client (CLI-003 - Call Centre Excellence)
- **Other**: 5 clients (10%)

### Hiring Patterns

**Decision-Making Speed**:
- Very Fast (<1 week): 6 clients (12%)
- Fast (1-2 weeks): 17 clients (34%)
- Medium (2-4 weeks): 16 clients (32%)
- Slow (4-12 weeks): 11 clients (22%)

**Hiring Frequency**:
- Weekly: 6 clients (12%) - High-volume recruiters
- Monthly: 15 clients (30%)
- Quarterly: 21 clients (42%) - Most common
- Annually: 8 clients (16%)

## Reference Files

For detailed information, consult these reference files:

- **[schema.md](references/schema.md)** - Complete database schema with all 50 columns, data types, and field descriptions
- **[business_insights.md](references/business_insights.md)** - Comprehensive business intelligence, industry analysis, and strategic insights

## Best Practices

1. **Always use MCP tools**: Use `mcp__supabase__execute_sql` for queries, not direct database connections
2. **Case-insensitive searches**: Use `ILIKE` for text matching (e.g., `WHERE company_name ILIKE '%tech%'`)
3. **Numeric conversion**: Cast revenue fields with `::numeric` for mathematical operations
4. **Limit results**: Use `LIMIT` for large result sets to avoid overwhelming output
5. **Context is key**: Reference account tier, industry sector, and service lines for meaningful insights
6. **Account manager workload**: Note that Sam Henderson manages 98% of clients
7. **Payment terms matter**: Consider payment terms and credit limits for financial queries
8. **Service cross-sell**: Identify clients using only Recruitment as cross-sell opportunities

## Common Analysis Patterns

### Revenue Analysis
Start with account tier, then drill into industry, service lines, and geographic distribution. Compare lifetime revenue against placements to identify fee efficiency.

### Service Opportunities
Find clients using only Recruitment service (no Assessment, Training, or Wellbeing) as upsell targets. Prioritize Gold/Silver tiers for maximum ROI.

### Hiring Pipeline
Focus on clients with active jobs, fast decision-making, and simple interview processes for quick placement opportunities.

### Risk Assessment
Monitor clients with Fair payment history, identify high concentration risk (top 10 = 42% of revenue), and track client longevity.

## Examples

**Find high-potential upsell targets**:
```sql
SELECT client_id, company_name, account_tier, lifetime_revenue_gbp
FROM clients
WHERE service_lines_used NOT ILIKE '%Assessment%'
  AND service_lines_used NOT ILIKE '%Training%'
  AND account_tier IN ('Gold', 'Silver')
ORDER BY lifetime_revenue_gbp DESC
LIMIT 20;
```

**Identify quick placement opportunities**:
```sql
SELECT client_id, company_name, active_jobs, decision_maker_speed
FROM clients
WHERE active_jobs >= 3
  AND decision_maker_speed IN ('Very Fast (<1 week)', 'Fast (1-2 weeks)')
  AND payment_history = 'Excellent'
ORDER BY active_jobs DESC;
```

**Analyze account manager workload**:
```sql
SELECT account_manager,
       COUNT(*) as client_count,
       SUM(active_jobs) as total_active_jobs,
       SUM(lifetime_revenue_gbp::numeric) as total_revenue
FROM clients
GROUP BY account_manager;
```
