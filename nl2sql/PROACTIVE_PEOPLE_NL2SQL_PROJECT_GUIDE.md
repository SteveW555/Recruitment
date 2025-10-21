# ProActive People NL2SQL Implementation - General Project Guide

**Document Version**: 1.0
**Created**: 2025-01-21
**Target System**: ProActive People Recruitment Automation Platform
**Database**: Supabase PostgreSQL (Project ID: `pauypyjqosrenuxveskn`)
**Scope**: General-purpose guide for entire project (all tables)

---

## 📋 Document Scope

**SCOPE**: General-purpose NL2SQL implementation guide for the entire ProActive People project
**APPLICATION**: Applies to all tables (candidates, clients, jobs, placements, etc.)
**AUDIENCE**: Development team, AI engineers, system architects

**Related Documents**:

- [Candidates Table Learnings](PROACTIVE_PEOPLE_NL2SQL_LEARNINGS.md) - Specific to candidates table
- [Clients Table Learnings](PROACTIVE_PEOPLE_NL2SQL_LEARNINGS_CLIENTS.md) - Specific to clients table

---

## 🎯 Executive Summary

This document provides a **table-agnostic** implementation guide for Natural Language to SQL (NL2SQL) translation in the ProActive People recruitment automation system. It captures patterns, principles, and practices that apply across all database tables, enabling consistent NL2SQL implementation throughout the platform.

**Key Contents**:
- ✅ Universal NL2SQL principles for recruitment domain
- ✅ Architecture and security patterns (table-independent)
- ✅ Cross-table query strategies (JOINs, multi-table)
- ✅ System design for scalable NL2SQL
- ✅ Quality assurance and testing frameworks
- ✅ Continuous improvement methodology

**Target Outcome**: A unified NL2SQL system achieving 85-90% accuracy across all recruitment data

---

## 🏗️ System Architecture Overview

### High-Level Flow

```
┌─────────────────┐
│  User Input     │
│  (Natural       │
│   Language)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Input           │
│ Sanitization    │  ← Layer 1: Security
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Clarity         │
│ Evaluation      │  ← Optional: Ambiguity check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Translation │
│ (temp = 0.2)    │  ← Layer 2: SQL Generation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RPC-Based       │
│ SQL Execution   │  ← Layer 3: Isolated execution
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Result          │
│ Formatting      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Response to     │
│ User            │
└─────────────────┘
```

### Key Components

1. **Input Sanitization Layer**: Removes SQL injection attempts, malicious patterns
2. **Clarity Evaluation** (Optional): Scores query clarity, requests clarification if needed
3. **LLM Translation Layer**: Converts NL to SQL using table-specific system prompts
4. **Execution Layer**: Executes SQL via RPC (server-side isolation)
5. **Result Formatting**: Converts SQL results to user-friendly format
6. **Evaluation Layer**: LLM judge for test cases, accuracy tracking

---

## 🛡️ Universal Security Principles

### Three-Layer Defense Strategy

Every NL2SQL query must pass through three security layers:

#### Layer 1: Input Sanitization

**Purpose**: Remove malicious patterns before LLM sees input

**Implementation**:
```typescript
function sanitizeNlInputForSqlLLM(userInput: string): [string, boolean] {
  let sanitizedStr = userInput;

  // Remove SQL comments
  sanitizedStr = sanitizedStr.replace(/--.*$/gm, '');
  sanitizedStr = sanitizedStr.replace(/\/\*.*?\*\//gs, '');

  // Remove quotes and semicolons
  sanitizedStr = sanitizedStr.replace(/'/g, '');
  sanitizedStr = sanitizedStr.replace(/;/g, '');

  sanitizedStr = sanitizedStr.trim();

  let isSanitized = (sanitizedStr != userInput);
  return [sanitizedStr, isSanitized];
}
```

**Critical**: Apply BEFORE sending to LLM

**Log all sanitization events**: Indicates potential attack attempts

---

#### Layer 2: Temperature Control

**Purpose**: Ensure deterministic, predictable SQL generation

**Settings**:
- **SQL Generation**: `temperature = 0.2` (no creativity, pure logic)
- **Clarity Evaluation**: `temperature = 0.3-0.4` (slight flexibility for interpretation)

**Rationale**: SQL must be precise, repeatable, not creative

---

#### Layer 3: RPC-Based Execution

**Purpose**: Server-side isolation, no direct query execution

**Pattern**:
```typescript
// CORRECT: RPC-based execution (server-side)
const { data, error } = await supabase.rpc('execute_sql', {
  query_text: cleanedSqlQuery
});

// WRONG: Direct query execution (vulnerable)
// const { data, error } = await supabase.from('table').select('*');
```

**Benefits**:
- Server-side validation
- Query isolation
- Rate limiting enforcement
- Complete audit trail
- Prevents direct database access from client

---

### Security Checklist (Apply to All Tables)

```
[ ] Input sanitization applied BEFORE LLM
[ ] Temperature = 0.2 for all SQL generation
[ ] RPC-based execution (no direct queries)
[ ] All sanitization events logged
[ ] SQL results sanitized before display
[ ] Rate limiting implemented (per user/IP)
[ ] Audit trail for all queries
[ ] Error messages sanitized (no schema leakage)
```

---

## 🎯 Universal NL2SQL Principles

### Principle 1: Case-Insensitive Text Matching

**Rule**: ALL text searches MUST use `ILIKE` (case-insensitive)

**Rationale**: Users don't think about case sensitivity

**Examples**:
```sql
-- WRONG (case-sensitive)
WHERE first_name = 'john'

-- CORRECT (case-insensitive)
WHERE first_name ILIKE 'john'

-- CORRECT (partial match)
WHERE skills ILIKE '%python%'
```

**Application**: Every table with text columns (names, industries, statuses, skills, etc.)

---

### Principle 2: Comma-Separated Fields

**Pattern**: Many fields store lists as comma-separated text

**Examples Across Tables**:
- Candidates: `primary_skills` → "Python, AWS, Django"
- Clients: `recruitment_service_lines` → "Recruitment, Assessment, Training"
- Jobs: `required_skills` → "Java, Spring, Microservices"

**Query Strategy**:
```sql
-- Single item
WHERE primary_skills ILIKE '%Python%'

-- Multiple items (both required)
WHERE primary_skills ILIKE '%Python%'
  AND primary_skills ILIKE '%AWS%'

-- Multiple items (either acceptable)
WHERE primary_skills ILIKE '%Python%'
   OR primary_skills ILIKE '%Java%'
```

**System Prompt Requirement**: Explicit guidance with examples for each table

---

### Principle 3: Status with Embedded IDs

**Pattern**: Status fields may contain additional context

**Examples**:
- Candidates: `current_status` → "Interviewing - CLT001" (includes client ID)
- Jobs: `job_status` → "Active - 5 applicants"
- Placements: `placement_status` → "Completed - £75,000"

**Query Strategy**:
```sql
-- WRONG (exact match fails)
WHERE current_status = 'Interviewing'

-- CORRECT (pattern match)
WHERE current_status ILIKE '%Interviewing%'

-- Extract specific info (if needed)
WHERE current_status LIKE 'Interviewing - CLT%'
```

**Application**: All status fields across all tables

---

### Principle 4: Salary/Revenue with Notation Variations

**Pattern**: Users express numbers in multiple formats

**Examples**:
- "100k", "£100k", "100000", "100K" → all mean £100,000
- "1M", "1m", "1000000" → all mean £1,000,000

**Query Strategy**:
```sql
-- User says "under 100k"
WHERE desired_salary < 100000

-- User says "over £1M"
WHERE lifetime_revenue_gbp > 1000000
```

**System Prompt Requirement**: Interpretation rules:
- "k" or "K" → multiply by 1,000
- "m" or "M" → multiply by 1,000,000
- Ignore £ symbol
- Default currency: GBP

---

### Principle 5: Date Range Interpretation

**Pattern**: Date queries require context-aware interpretation

**Common Queries**:
- "recent" → last 3 months
- "new" → last 1 year
- "this year" → `EXTRACT(YEAR FROM date) = EXTRACT(YEAR FROM NOW())`
- "last quarter" → previous 3-month period

**Query Strategy**:
```sql
-- "Recent candidates"
WHERE created_at > NOW() - INTERVAL '3 months'

-- "New clients this year"
WHERE EXTRACT(YEAR FROM first_engagement_date) = EXTRACT(YEAR FROM NOW())

-- "Placements last quarter"
WHERE placement_date >= DATE_TRUNC('quarter', NOW() - INTERVAL '3 months')
  AND placement_date < DATE_TRUNC('quarter', NOW())
```

**Application**: All tables with date fields

---

### Principle 6: Default to Active Records

**Rule**: Unless explicitly stated, assume user wants active/current records only

**Examples**:
- "Show candidates" → assume `current_status != 'Placed'`
- "Show clients" → assume `account_status = 'Active'`
- "Show jobs" → assume `job_status = 'Open'`

**Query Strategy**:
```sql
-- Default behavior (implicit active filter)
SELECT * FROM candidates
WHERE current_status NOT IN ('Placed', 'Withdrawn', 'Rejected')

-- Explicit "all" request
SELECT * FROM candidates
-- No status filter
```

**System Prompt Guidance**: Define "active" for each table

---

## 🔗 Cross-Table Query Strategies

### JOIN Patterns for Recruitment Domain

#### Pattern 1: Candidates + Jobs (Applications)

**Business Question**: "Which candidates applied for software engineering roles?"

**SQL Strategy**:
```sql
SELECT c.first_name, c.last_name, j.job_title
FROM candidates c
JOIN applications a ON c.candidate_id = a.candidate_id
JOIN jobs j ON a.job_id = j.job_id
WHERE j.job_title ILIKE '%software engineer%'
```

---

#### Pattern 2: Clients + Jobs (Open Positions)

**Business Question**: "Which clients have open roles in finance?"

**SQL Strategy**:
```sql
SELECT cl.company_name, j.job_title, j.salary_max_gbp
FROM clients cl
JOIN jobs j ON cl.client_id = j.client_id
WHERE j.job_status = 'Open'
  AND cl.industry_sector ILIKE '%finance%'
```

---

#### Pattern 3: Candidates + Placements + Clients (Placement History)

**Business Question**: "Which candidates were placed at tech companies this year?"

**SQL Strategy**:
```sql
SELECT c.first_name, c.last_name, cl.company_name, p.placement_date
FROM candidates c
JOIN placements p ON c.candidate_id = p.candidate_id
JOIN clients cl ON p.client_id = cl.client_id
WHERE cl.industry_sector ILIKE '%tech%'
  AND EXTRACT(YEAR FROM p.placement_date) = EXTRACT(YEAR FROM NOW())
```

---

#### Pattern 4: Jobs + Candidates (Matching)

**Business Question**: "Find Python developers for this job"

**SQL Strategy**:
```sql
SELECT c.first_name, c.last_name, c.primary_skills
FROM candidates c
WHERE c.primary_skills ILIKE '%Python%'
  AND c.current_status ILIKE '%Available%'
  AND c.desired_salary <= (
    SELECT salary_max_gbp FROM jobs WHERE job_id = 'J001'
  )
```

---

### Multi-Table Query Guidelines

**When to JOIN**:
1. Query explicitly mentions multiple entities ("candidates at X company")
2. Filter requires data from another table ("clients with Python jobs")
3. Aggregation spans tables ("placements per client")

**When NOT to JOIN**:
1. Single entity query ("show candidates")
2. All needed data in one table
3. Ambiguous query (start with single table)

**JOIN Performance**:
- Always use indexed columns (primary keys, foreign keys)
- Filter early (WHERE before JOIN when possible)
- Limit results (LIMIT 100 for exploratory queries)

---

## 📝 System Prompt Engineering Framework

### Universal System Prompt Structure

Every table-specific system prompt must include:

#### Section 1: Role Definition (50 words)
```
You are a SQL expert for the ProActive People recruitment database.
Your task is to translate natural language queries into valid PostgreSQL SQL.
Return ONLY the SQL query, no explanations.
Use the schema below and follow all rules strictly.
```

---

#### Section 2: Complete Schema (20-30% of prompt)
```
TABLE_NAME — purpose description

    column_name data_type CONSTRAINTS  -- Business description
    column_name data_type CONSTRAINTS  -- NL2SQL considerations
    ...
```

**Requirements**:
- Document ALL columns
- Include data types and constraints
- Add business context for each field
- Note NL2SQL considerations (e.g., "comma-separated", "may contain IDs")

---

#### Section 3: Universal Rules (15% of prompt)

**Required Rules**:
1. **Case-insensitive matching**: Use `ILIKE` for all text searches
2. **Comma-separated fields**: Use `ILIKE '%item%'` for partial matching
3. **Status fields**: Use pattern matching (may contain embedded data)
4. **Salary/Revenue**: Interpret "k" = 1000, "m" = 1000000
5. **Date ranges**: Define "recent", "new", "this year"
6. **Default filters**: Active records unless "all" specified
7. **Output format**: SQL only, no explanations
8. **NULL handling**: Consider NULL in all comparisons

---

#### Section 4: Table-Specific Business Logic (10% of prompt)

**Examples**:
- **Candidates**: Skills matching, status interpretation, recruiter workflows
- **Clients**: Account tiers, service lines, contract management
- **Jobs**: Role matching, salary ranges, application tracking
- **Placements**: Commission calculations, placement lifecycle

---

#### Section 5: 20+ Diverse Examples (40% of prompt)

**Coverage Requirements**:
- Simple filters (3 examples)
- Text searches (4 examples)
- Numeric ranges (3 examples)
- Date filters (3 examples)
- Multiple conditions (4 examples)
- Aggregations (3 examples)

**Quality Requirements**:
- Real business questions
- Variety of complexity (levels 1-10)
- Cover all common query patterns
- Show CORRECT SQL (no wrong examples)

---

#### Section 6: Output Format (5% of prompt)
```
CRITICAL: Return ONLY the SQL query. No explanations, no markdown, no comments.

Example:
User: "Show active candidates"
Assistant: SELECT * FROM candidates WHERE current_status ILIKE '%available%'
```

---

### System Prompt Quality Checklist

```
[ ] Complete schema documented (all columns)
[ ] All universal rules included
[ ] Table-specific business logic defined
[ ] 20+ examples covering all patterns
[ ] Case-insensitive rules explicit
[ ] Comma-separated field guidance
[ ] Status pattern matching shown
[ ] Date interpretation defined
[ ] Output format specification clear
[ ] Examples show CORRECT SQL only
```

---

## 🧪 Testing & Evaluation Framework

### Test Case Structure

**JSON Format** (applies to all tables):
```json
{
  "nl": "natural language query",
  "known_sql": "expected SQL result",
  "llm_sql": " ",
  "results": " "
}
```

---

### Test Coverage Requirements

**By Complexity** (for each table):
- Level 1-3 (Simple): 10 cases
- Level 4-6 (Medium): 10 cases
- Level 7-8 (Complex): 8 cases
- Level 9-10 (Very Complex): 5 cases

**Total**: 30+ test cases per table

---

### LLM Judge for Equivalence

**Why**: Many valid SQL representations exist for the same query

**Examples of Equivalent Queries**:
```sql
-- These are equivalent:
WHERE status = 'Active'
WHERE status ILIKE 'active'

-- These are equivalent:
SELECT * FROM candidates WHERE skills LIKE '%Python%'
SELECT candidate_id, first_name, last_name, skills
FROM candidates WHERE skills ILIKE '%python%'

-- These are equivalent:
ORDER BY created_at DESC LIMIT 10
ORDER BY created_at DESC FETCH FIRST 10 ROWS ONLY
```

**Implementation**: Use LLM with specialized system prompt to judge equivalence

**Critical**: String matching is insufficient, use semantic equivalence

---

### Accuracy Targets

**By Query Complexity**:
- Simple (1-3): 95%+
- Medium (4-6): 85-90%
- Complex (7-8): 75-85%
- Very Complex (9-10): 65-75%

**Overall Target**: 85-90% across all queries

---

### Failure Analysis Loop

**Process**:
1. Run test suite
2. Collect all failures (incorrect SQL or results)
3. Analyze patterns:
   - Which query types fail most?
   - Common LLM mistakes?
   - Missing examples in prompt?
4. Update system prompt:
   - Add failing queries as examples
   - Clarify ambiguous rules
   - Add edge case guidance
5. Re-test
6. Repeat until accuracy target met

**Cadence**: After each batch of 10 test cases

---

## 🔄 Continuous Improvement Methodology

### Phase 1: Baseline (Week 1)

**Goals**:
- Deploy MVP with basic system prompt
- Run initial 30 test cases
- Measure baseline accuracy

**Expected**: 60-70% accuracy

---

### Phase 2: Optimization (Week 2-3)

**Goals**:
- Analyze all failures
- Update system prompt with new examples
- Add business logic clarifications
- Re-test

**Expected**: 75-85% accuracy

---

### Phase 3: Production (Week 4)

**Goals**:
- Deploy to production with monitoring
- Collect real user queries
- Log all failures
- Continuous prompt refinement

**Expected**: 85-90% accuracy

---

### Phase 4: Maintenance (Ongoing)

**Goals**:
- Weekly failure analysis
- Monthly prompt updates
- Quarterly accuracy reviews
- Schema change management

**Expected**: 90%+ accuracy maintained

---

## 📊 System Prompt Examples Library

### Cross-Table Patterns

#### Example 1: Aggregation with JOIN
```sql
-- Query: "How many placements per client this year?"
SELECT cl.company_name, COUNT(p.placement_id) AS placement_count
FROM clients cl
LEFT JOIN placements p ON cl.client_id = p.client_id
WHERE EXTRACT(YEAR FROM p.placement_date) = EXTRACT(YEAR FROM NOW())
GROUP BY cl.client_id, cl.company_name
ORDER BY placement_count DESC
```

---

#### Example 2: Filtering with Subquery
```sql
-- Query: "Show candidates qualified for this job"
SELECT c.first_name, c.last_name, c.primary_skills
FROM candidates c
WHERE c.primary_skills ILIKE '%Python%'
  AND c.desired_salary <= (
    SELECT salary_max_gbp FROM jobs WHERE job_id = 'J001'
  )
  AND c.current_status ILIKE '%available%'
```

---

#### Example 3: Date Range with Multiple Tables
```sql
-- Query: "Clients with no placements in last 6 months"
SELECT cl.company_name, cl.last_contact_date
FROM clients cl
WHERE cl.account_status = 'Active'
  AND cl.client_id NOT IN (
    SELECT p.client_id
    FROM placements p
    WHERE p.placement_date > NOW() - INTERVAL '6 months'
  )
```

---

## 🚀 Implementation Priorities

### Phase 1: Single-Table MVP (Week 1-2)

**Priority 1**: Candidates table
- Highest query volume
- Core recruitment operations
- Simpler schema (18 columns)

**Priority 2**: Clients table
- Second highest query volume
- More complex (52 columns)
- Tests pattern reusability

**Priority 3**: Jobs table
- Moderate query volume
- Connects candidates + clients

---

### Phase 2: Multi-Table Queries (Week 3-4)

**JOIN Patterns**:
1. Candidates + Jobs (applications)
2. Clients + Jobs (open positions)
3. Candidates + Placements (placement history)
4. All tables (complex reporting)

**System Prompt Updates**:
- Add JOIN examples
- Define foreign key relationships
- Document cross-table business logic

---

### Phase 3: Advanced Features (Week 5+)

**Features**:
- Aggregations (COUNT, SUM, AVG, GROUP BY)
- Subqueries (IN, NOT IN, EXISTS)
- Window functions (ROW_NUMBER, RANK)
- Complex date logic (quarter-end, fiscal year)

---

## 📚 Reference Architecture

### File Structure

```
recruitment-automation-system/
├── nl2sql/
│   ├── prompts/
│   │   ├── candidates_nl2sql_system_prompt.txt
│   │   ├── clients_nl2sql_system_prompt.txt
│   │   ├── jobs_nl2sql_system_prompt.txt
│   │   └── ...
│   ├── security/
│   │   ├── sanitize.ts
│   │   └── execute.ts
│   ├── ai/
│   │   ├── client.ts
│   │   └── judge.ts
│   ├── evaluation/
│   │   ├── scorer.ts
│   │   └── test_runner.ts
│   └── tests/
│       ├── candidates_test_cases.json
│       ├── clients_test_cases.json
│       └── ...
```

---

### Technology Stack

**Core Components**:
- **LLM Provider**: OpenAI (gpt-4o-mini for speed) or Groq (ultra-fast)
- **Database**: Supabase PostgreSQL
- **Language**: TypeScript (Node.js)
- **Testing**: Custom LLM judge + JSON test cases

**Optional**:
- **Clarity Evaluation**: Pre-processes ambiguous queries
- **Caching**: Redis for common queries
- **Monitoring**: Logs + analytics dashboard

---

## 🎯 Success Metrics

### Technical Metrics

**Accuracy**:
- Overall: 85-90%
- Simple queries: 95%+
- Complex queries: 75%+

**Performance**:
- Response time: <700ms (95th percentile)
- Throughput: 100+ queries/second

**Reliability**:
- Uptime: 99.9%
- Error rate: <1%

---

### Business Metrics

**User Satisfaction**:
- Query success rate: 90%+
- User retry rate: <5%
- Query refinement rate: <10%

**Adoption**:
- Daily active users: 80%+ of recruiters
- Queries per user: 20+/day
- User preference: NL over manual SQL

---

## 🔧 Troubleshooting Guide

### Common Issues Across Tables

#### Issue 1: Low Accuracy on Text Searches

**Symptoms**: Failing queries with names, skills, industries

**Root Cause**: Case-sensitive matching (`=` instead of `ILIKE`)

**Fix**: Update system prompt with explicit ILIKE rules + examples

**Expected Impact**: +20% accuracy

---

#### Issue 2: Comma-Separated Field Failures

**Symptoms**: Failing queries searching for specific items in lists

**Root Cause**: Exact match instead of partial match

**Fix**: Add comma-separated field examples to prompt

**Expected Impact**: +15% accuracy

---

#### Issue 3: Status Field Mismatches

**Symptoms**: Status queries returning no results

**Root Cause**: Status contains embedded IDs (e.g., "Interviewing - CLT001")

**Fix**: Use pattern matching (`ILIKE '%status%'`) in all examples

**Expected Impact**: +10% accuracy

---

#### Issue 4: Date Range Ambiguity

**Symptoms**: Inconsistent date filtering

**Root Cause**: "Recent", "new", "this year" undefined

**Fix**: Define date interpretations explicitly in prompt

**Expected Impact**: +8% accuracy

---

#### Issue 5: Security Events Triggered

**Symptoms**: Sanitization warnings in logs

**Root Cause**: Users entering SQL-like syntax or malicious patterns

**Fix**: Expected behavior - log and continue with sanitized input

**Action**: Review logs weekly, update sanitization if needed

---

## 📖 Best Practices Summary

### System Prompt
1. **80% of success**: Invest time in quality system prompt
2. **Complete schema**: Document all columns with business context
3. **20+ examples**: Cover all query patterns with correct SQL
4. **Explicit rules**: Case-insensitivity, comma-separated, status patterns
5. **Clear output format**: SQL only, no explanations

---

### Security
1. **Three layers**: Sanitization → Temperature → RPC execution
2. **Log everything**: Sanitization events, query execution, failures
3. **Never trust input**: Sanitize BEFORE LLM, validate AFTER LLM
4. **Isolated execution**: RPC only, no direct database access

---

### Testing
1. **LLM judge**: Use semantic equivalence, not string matching
2. **30+ cases per table**: Cover all complexity levels
3. **Failure analysis loop**: Test → Analyze → Update → Re-test
4. **Continuous improvement**: Weekly reviews, monthly updates

---

### Performance
1. **Temperature = 0.2**: Deterministic SQL generation
2. **Fast models**: gpt-4o-mini or Groq for speed
3. **Caching**: Cache common queries (optional)
4. **Rate limiting**: Prevent abuse

---

## ✅ Project-Wide Implementation Checklist

### Infrastructure
- [ ] Supabase connection configured
- [ ] RPC function `execute_sql` created
- [ ] Authentication & authorization set up
- [ ] Rate limiting implemented
- [ ] Logging infrastructure ready

### Security
- [ ] Sanitization function deployed
- [ ] Temperature = 0.2 configured
- [ ] RPC-based execution enforced
- [ ] Audit trail implemented
- [ ] Security monitoring active

### Prompts (Per Table)
- [ ] Complete schema documented
- [ ] Universal rules included
- [ ] Table-specific logic defined
- [ ] 20+ examples written
- [ ] Output format specified

### Testing (Per Table)
- [ ] 30+ test cases created
- [ ] LLM judge implemented
- [ ] Test runner automated
- [ ] Baseline accuracy measured

### Production
- [ ] Monitoring dashboard deployed
- [ ] Error alerting configured
- [ ] Failure logging active
- [ ] Continuous improvement process defined

---

## 🔗 Additional Resources

### Internal Documentation
- **Candidates Table Guide**: `PROACTIVE_PEOPLE_NL2SQL_LEARNINGS.md`
- **Clients Table Guide**: `PROACTIVE_PEOPLE_NL2SQL_LEARNINGS_CLIENTS.md`
- **Reference Files**: `nl2sql/source_copies/` directory

### External Resources
- **PostgreSQL ILIKE**: https://www.postgresql.org/docs/current/functions-matching.html
- **Supabase RPC**: https://supabase.com/docs/guides/database/functions
- **OpenAI API**: https://platform.openai.com/docs/api-reference

---

## 📞 Support & Contribution

### Getting Help

**For table-specific questions**:
- Candidates: See `PROACTIVE_PEOPLE_NL2SQL_LEARNINGS.md`
- Clients: See `PROACTIVE_PEOPLE_NL2SQL_LEARNINGS_CLIENTS.md`

**For general questions**:
- Review this document
- Check reference files in `nl2sql/source_copies/`
- Consult original implementation guides

### Contributing

**When adding a new table**:
1. Create table-specific learnings document
2. Analyze data patterns (100+ rows)
3. Identify table-specific challenges
4. Write table-specific system prompt
5. Create 30+ test cases
6. Run baseline tests
7. Document findings

**When updating existing tables**:
1. Log all failures
2. Analyze failure patterns
3. Update system prompt
4. Add new test cases
5. Re-test and measure improvement
6. Document changes

---

## 🎓 Key Takeaways

1. **System Prompt Quality = 80% of Success**
   - Invest time in comprehensive examples
   - Document schema with business context
   - Make rules explicit, not implicit

2. **Security is Non-Negotiable**
   - Three-layer defense (sanitize, temperature, RPC)
   - Log everything
   - Never trust input

3. **Testing Drives Improvement**
   - Use LLM judge for semantic equivalence
   - Analyze failures systematically
   - Iterate continuously

4. **Universal Patterns Apply Across Tables**
   - Case-insensitive matching (ILIKE)
   - Comma-separated field handling
   - Status pattern matching
   - Date range interpretation

5. **Start Simple, Expand Gradually**
   - Phase 1: Single-table queries
   - Phase 2: Multi-table JOINs
   - Phase 3: Advanced aggregations
   - Phase 4: Complex analytics

---

**End of Document**

*This general-purpose guide provides the foundation for implementing consistent, secure, high-accuracy NL2SQL across the entire ProActive People recruitment platform.*
