# ProActive People - NL2SQL Implementation Learnings (Candidates Table)

**Project**: ProActive People Recruitment Automation System
**Database**: Supabase PostgreSQL
**Table Focus**: `candidates` (100 rows)
**Analysis Date**: 2025-10-21
**Based On**: Production NL2SQL system achieving 90%+ accuracy

---

## 📋 Document Scope

**SCOPE**: Currently focused on **`candidates` table only**
**FUTURE**: Will expand to multi-table queries (clients, jobs, placements)
**Status**: Phase 1 - Single table MVP

**Related Documents**:

- [Clients Table Learnings](PROACTIVE_PEOPLE_NL2SQL_LEARNINGS_CLIENTS.md) (separate document)
- [General Project Guide](PROACTIVE_PEOPLE_NL2SQL_PROJECT_GUIDE.md) (multi-table overview)

---

## Executive Summary

This document captures the key learnings from studying a battle-tested NL2SQL system and how they apply specifically to ProActive People's **candidates table**. The reference system achieved **90%+ accuracy** through rigorous system prompt engineering, security hardening, and continuous optimization.

**Key Takeaway**: 80% of NL2SQL accuracy comes from system prompt quality. The remaining 20% comes from security, testing, and optimization loops.

---

## Table of Contents

1. [Database Analysis - ProActive People](#database-analysis)
2. [Critical Success Factors](#critical-success-factors)
3. [System Prompt Design](#system-prompt-design)
4. [Data Patterns & Business Logic](#data-patterns--business-logic)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Security Requirements](#security-requirements)
7. [Testing Strategy](#testing-strategy)
8. [Known Challenges & Solutions](#known-challenges--solutions)
9. [Next Steps](#next-steps)

---

## Database Analysis

### Current Schema: `candidates` Table

**Location**: Supabase project `pauypyjqosrenuxveskn`
**Rows**: 100 test candidates
**Primary Key**: `candidate_id` (text, format: C001-C100)

**18 Columns:**

| Column | Type | Purpose | NL2SQL Considerations |
|--------|------|---------|----------------------|
| `candidate_id` | text PK | Unique identifier | Use for exact match queries |
| `first_name` | text | Candidate first name | **ILIKE** for case-insensitive search |
| `last_name` | text | Candidate last name | **ILIKE** for case-insensitive search |
| `primary_email` | text | Contact email | Exact or **ILIKE** depending on query |
| `phone_number` | text | Contact phone | Pattern: 555-0XXX |
| `job_title_target` | text | Desired role | **ILIKE** - handles variations |
| `primary_skills` | text | **Comma-separated** skills | **Critical**: Use `ILIKE '%skill%'` |
| `industry_experience` | text | Industry sector | **ILIKE** for sector matching |
| `current_status` | text | Pipeline status | **Contains client IDs**, use patterns |
| `last_contact_date` | date | Last contact | Date range queries common |
| `desired_salary` | numeric | Annual GBP | Comparison operators (<, >, BETWEEN) |
| `bullhorn_resume_id` | text | ATS integration ID | Format: R001A-R100A |
| `interview_notes_sentiment` | text | Sentiment category | Values: Positive, Neutral, Highly Positive, Negative |
| `gsuite_doc_attached` | text | Doc status | Values: Yes, No |
| `recruiter_notes_external` | text | Client-facing notes | Search with **ILIKE** |
| `recruiter_notes_internal` | text | Internal notes | Search with **ILIKE** |
| `created_at` | timestamptz | Record creation | Rarely queried |
| `updated_at` | timestamptz | Last update | Rarely queried |

### Future Tables (Planned)

From CLAUDE.md project context:
- `clients` - Client companies
- `jobs` - Job postings
- `placements` - Candidate placements
- `applications` - Job applications

**Implication**: System prompt will need updating as schema grows. Plan for multi-table JOINs.

---

## Critical Success Factors

Based on reference system achieving 90%+ accuracy:

### 1. System Prompt Quality (80% Impact)

**Must include:**
- ✅ Complete schema (all 18 columns documented)
- ✅ 15+ examples covering all query patterns
- ✅ Domain-specific business logic
- ✅ Case-insensitive matching rules (ILIKE)
- ✅ Output format specification (SQL only, no markdown)

**Status**: ✅ **COMPLETE** - Created at `prompts/candidates_nl2sql_system_prompt.txt` with 20 examples

### 2. Security Hardening (Non-Negotiable)

**Three-layer defense:**
1. **Input sanitization** (BEFORE LLM) - Remove SQL injection attempts
2. **Temperature control** - 0.2 for deterministic SQL generation
3. **RPC execution** - Server-side isolation via Supabase RPC

**Status**: 🟡 **PENDING** - Need to copy security files from `nl2sql/source_copies/CRITICAL/`

### 3. LLM Judge for Equivalence (Critical for 80%+ accuracy)

**Why needed**: String matching fails on semantically equivalent SQL:
```sql
-- These are equivalent but string matching rejects:
"SELECT * FROM candidates WHERE status = 'Available'"
"SELECT first_name, last_name FROM candidates WHERE status ILIKE '%available%'"
```

**LLM judge accepts both** ✅

**Status**: 🟡 **PENDING** - Need to implement from `nl2sql/source_copies/CRITICAL/3_llm_judge_equivalence.ts`

### 4. Multi-Variant Testing

Test every query with 3 versions:
- `nl_simple`: "python devs"
- `nl`: "show Python developers"
- `nl_focused`: "Retrieve all candidates with Python skills"

**Status**: 🔴 **NOT STARTED** - Need to create test cases

### 5. Failure Analysis Loop (Continuous Improvement)

**Process:**
1. Run tests → Log failures
2. Analyze patterns (e.g., capitalization issues)
3. Add failing examples to system prompt
4. Re-test to confirm improvement

**Status**: 🔴 **NOT STARTED** - Need to set up logging

---

## System Prompt Design

### Key Design Decisions

**1. Case-Insensitive Matching (Critical)**

**Problem**: User input is unpredictable
- "python" vs "Python" vs "PYTHON"
- "Software Engineer" vs "software engineer"

**Solution**: Always use `ILIKE '%value%'`
```sql
-- User says: "Python developers"
SELECT * FROM candidates
WHERE primary_skills ILIKE '%python%'
AND job_title_target ILIKE '%developer%';
```

**2. Comma-Separated Skills Handling**

**Data pattern observed:**
```csv
"Python, AWS, Django"
"Recruitment, Employee Relations, SAP HR"
"Financial Modeling, GAAP, Excel"
```

**Challenge**: Can't use exact match on comma-separated strings

**Solution**: Use `ILIKE '%skill%'` for partial matching
```sql
-- Matches "Python, AWS, Django"
WHERE primary_skills ILIKE '%aws%'
```

**Added to system prompt**: Explicit guidance on skills column structure

**3. Status with Embedded Client IDs**

**Data pattern observed:**
```csv
"Available"                    ← Simple
"Interviewing - CLT001"        ← Contains client ID
"Offer Pending - CLT003"       ← Contains client ID
"Screening"                    ← Simple
"Placed - CLT007"              ← Contains client ID
"Dormant"                      ← Simple
```

**Challenge**: Exact match fails on "Interviewing" when data is "Interviewing - CLT001"

**Solution**: Pattern matching with `ILIKE '%interview%'`
```sql
-- User says: "Who is interviewing?"
SELECT * FROM candidates
WHERE current_status ILIKE '%interview%';
```

**Added to system prompt**: Status interpretation section with examples

**4. Salary Notation Interpretation**

**User input variations:**
- "under £100k"
- "under 100k"
- "under 100000"
- "between 80-120k"

**Solution**: Interpret "k" as thousands
```sql
-- User says: "under 100k"
WHERE desired_salary < 100000
```

**Added to system prompt**: Salary queries section with notation handling

**5. Sentiment Values**

**Observed values from data:**
- "Positive" (most common)
- "Neutral"
- "Highly Positive"
- "Negative"

**Usage in queries:**
```sql
-- "Candidates with positive feedback"
WHERE interview_notes_sentiment ILIKE '%positive%'
-- Matches both "Positive" and "Highly Positive"
```

**Added to system prompt**: Sentiment analysis section

---

## Data Patterns & Business Logic

### Patterns Discovered from 100 Sample Candidates

#### 1. Status Distribution

From CSV analysis:
- **Available**: ~40% (actively seeking)
- **Interviewing - CLT###**: ~20% (in client interview process)
- **Offer Pending/Extended - CLT###**: ~5% (offer stage)
- **Screening**: ~10% (early stage)
- **Placed - CLT###**: ~5% (successfully placed)
- **Rejected**: ~3% (not suitable for role)
- **Dormant**: ~5% (on hold/inactive)

**Business Logic Encoded:**
- "Available candidates" → `current_status ILIKE '%available%'`
- "Interviewing" → `current_status ILIKE '%interview%'`
- "Offer stage" → `current_status ILIKE '%offer%'`
- "Placed candidates" → `current_status ILIKE '%placed%'`

#### 2. Skills Patterns

**Common skill combinations observed:**
- Tech: "Python, AWS, Django", "React, Node.js, MongoDB"
- Finance: "Financial Modeling, GAAP, Excel"
- Healthcare: "Patient Care, Compliance, EPIC"
- Marketing: "SEO, PPC, Content Strategy"

**Multi-skill search examples:**
```sql
-- "Python AND AWS"
WHERE primary_skills ILIKE '%python%'
AND primary_skills ILIKE '%aws%'

-- "Python OR Java"
WHERE (primary_skills ILIKE '%python%'
OR primary_skills ILIKE '%java%')
```

#### 3. Industry Sectors

**Observed values:**
- Software Development
- Fintech
- Healthcare/MedTech
- Marketing & Creative
- Finance/Insurance
- Logistics & Supply Chain
- Education
- Food & Beverage
- Aerospace/Defense
- And 15+ more

**Query pattern:**
```sql
WHERE industry_experience ILIKE '%fintech%'
```

#### 4. Salary Ranges

**Distribution observed:**
- £30k-£50k: Entry-level (servers, clerks, coordinators)
- £60k-£90k: Mid-level (analysts, managers, specialists)
- £100k-£150k: Senior (senior engineers, consultants)
- £150k-£350k: Executive (C-suite, architects, research scientists)

**Common queries:**
```sql
-- Entry-level
WHERE desired_salary < 50000

-- Mid-range professionals
WHERE desired_salary BETWEEN 60000 AND 100000

-- High earners
WHERE desired_salary > 150000
```

#### 5. Date Recency Patterns

**Business definitions:**
- "Recently contacted" = last 7-14 days
- "This week" = current week
- "This month" = current month
- "Cold leads" = not contacted in 30+ days

**Implementation:**
```sql
-- Recently contacted (last 7 days)
WHERE last_contact_date > CURRENT_DATE - INTERVAL '7 days'

-- This month
WHERE last_contact_date >= date_trunc('month', CURRENT_DATE)

-- Cold leads
WHERE last_contact_date < CURRENT_DATE - INTERVAL '30 days'
```

#### 6. Google Suite Integration

**Observed pattern**: Many notes reference G-Docs, G-Sheets, G-Drive
- "Feedback notes in shared G-Sheet 'PFG-Tracking'"
- "Resume with clearance details via secure G-Doc"
- "Budget proposal notes in G-Doc"

**Implication**: Users may ask about "candidates with Google Docs" or "G-Sheet status"

**Query pattern:**
```sql
WHERE gsuite_doc_attached = 'Yes'
-- OR
WHERE recruiter_notes_external ILIKE '%g-doc%'
OR recruiter_notes_internal ILIKE '%g-sheet%'
```

---

## Implementation Roadmap

### Phase 1: MVP (4-6 hours) ✅ PARTIALLY COMPLETE

**Completed:**
- ✅ System prompt created with 20 examples
- ✅ Schema fully documented
- ✅ Business logic encoded
- ✅ Output format specified

**Pending:**
- 🟡 Copy security files (1 hour)
- 🟡 Set up AI client (30 min)
- 🟡 Test with 5 simple queries (30 min)

**Expected result**: 60-70% accuracy

---

### Phase 2: Testing & Security (1-2 days)

**Tasks:**

1. **Security Implementation** (2 hours)
   ```bash
   # Copy from reference
   cp nl2sql/source_copies/CRITICAL/1_sanitization_function.ts \
      src/security/sanitize.ts

   cp nl2sql/source_copies/CRITICAL/2_sql_execution_hardening.ts \
      src/database/executeSQL.ts
   ```

2. **Create 30+ Test Cases** (4 hours)
   - 5 simple name/email searches
   - 5 job title searches
   - 5 skills-based searches
   - 5 status filters
   - 5 salary range queries
   - 5 combined filters
   - 3 aggregations (COUNT, AVG, GROUP BY)
   - 2 complex multi-condition queries

3. **Implement LLM Judge** (1 hour)
   ```bash
   cp nl2sql/source_copies/CRITICAL/3_llm_judge_equivalence.ts \
      src/evaluation/queryJudge.ts
   ```

4. **Set Up Failure Logging** (30 min)
   ```typescript
   function logFailure(nl: string, expected: string, generated: string) {
     fs.appendFileSync('failures.txt',
       `${nl}\n${expected}\n${generated}\n\n`);
   }
   ```

**Expected result**: 80-85% accuracy

---

### Phase 3: Optimization (Ongoing)

**Weekly process:**

1. **Run full test suite**
   ```bash
   npm run test:nl2sql
   ```

2. **Analyze failures**
   ```bash
   cat failures.txt | grep -v "SELECT" | sort | uniq -c
   ```

3. **Identify patterns** (common mistakes)

4. **Update system prompt** (add failing examples)

5. **Re-test** (verify improvement)

**Expected result**: 90%+ accuracy after 1-2 weeks

---

## Security Requirements

### Critical: Three-Layer Defense

Based on reference system security architecture:

#### Layer 1: Input Sanitization (BEFORE LLM)

**Purpose**: Prevent SQL injection and prompt manipulation

**Implementation**:
```typescript
function sanitizeNlInputForSqlLLM(userInput: string): [string, boolean] {
  let sanitized = userInput;

  // Remove SQL comment markers
  sanitized = sanitized.replace(/--.*$/gm, '');
  sanitized = sanitized.replace(/\/\*.*?\*\//gs, '');

  // Remove single quotes (injection prevention)
  sanitized = sanitized.replace(/'/g, '');

  // Remove semicolons (prevent multi-statement)
  sanitized = sanitized.replace(/;/g, '');

  sanitized = sanitized.trim();

  const wasModified = (sanitized !== userInput);
  if (wasModified) {
    console.warn('⚠️ Input sanitized - potential attack?',
      { original: userInput, sanitized });
  }

  return [sanitized, wasModified];
}
```

**Test cases**:
```typescript
// Malicious inputs that should be sanitized:
"Show ' ; DROP TABLE candidates; --"
"Find /* comment */ users"
"List candidates'; DELETE FROM candidates;--"
```

#### Layer 2: Temperature Control

**Setting**: `temperature: 0.2` (CRITICAL)

**Why**:
- Deterministic SQL generation
- Reduced hallucination
- Consistent output across runs

**Implementation**:
```typescript
const completion = await openai.chat.completions.create({
  model: 'gpt-4o-mini',
  messages: [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: cleanedInput }
  ],
  temperature: 0.2  // ← CRITICAL: Must be 0.2
});
```

#### Layer 3: RPC Execution (Server-Side Isolation)

**Purpose**: Execute SQL in controlled environment

**Implementation** (Supabase):
```typescript
export async function executeSQL(sqlQuery: string) {
  // Clean SQL
  const cleanSQL = sqlQuery.trim().replace(/;$/, '');

  try {
    // Execute via RPC (NOT direct query!)
    const { data, error } = await supabase.rpc('execute_sql', {
      query_text: cleanSQL
    });

    if (error) {
      console.error('❌ SQL execution failed:', error);
      return { data: null, error };
    }

    console.log('✅ SQL succeeded:', data?.length, 'rows');
    return { data, error: null };

  } catch (err) {
    console.error('❌ Exception:', err);
    return { data: null, error: err };
  }
}
```

**NEVER do this**:
```typescript
// ❌ DANGEROUS - Direct string concatenation
const result = await db.query(`SELECT * FROM candidates WHERE id = ${userId}`);
```

---

## Testing Strategy

### Test Case Structure

Based on reference system test format:

```json
{
  "test_name": "available_python_devs",
  "nl": "Show available Python developers",
  "nl_simple": "python devs available",
  "nl_focused": "Retrieve all candidates with Python skills who have status Available",
  "known_sql": "SELECT first_name, last_name, primary_skills FROM candidates WHERE primary_skills ILIKE '%python%' AND current_status ILIKE '%available%';",
  "difficulty": "medium",
  "complexity": 5,
  "query_type": ["SELECT", "WHERE", "AND", "ILIKE"]
}
```

### 30 Test Cases Needed

**Simple (Complexity 1-2):**
1. Find candidate by name
2. List all candidates
3. Find by email
4. Show specific job title
5. Count total candidates

**Medium (Complexity 3-5):**
6. Python developers
7. Available candidates
8. Salary under 100k
9. Recently contacted
10. Specific industry experience
11. Python AND AWS skills
12. Candidates with positive feedback
13. Status = Interviewing
14. Salary between 80k-120k
15. Fintech experience

**Complex (Complexity 6-8):**
16. Available Python devs under 120k
17. AWS engineers wanting over 100k, contacted recently
18. Count candidates by status
19. Average salary by job title
20. Top 5 highest salary expectations
21. Available fintech professionals with positive feedback
22. Python OR Java developers
23. Candidates without Bullhorn ID
24. Notes mentioning "G-Doc"
25. Interviewing candidates contacted this month

**Very Complex (Complexity 9-10):**
26. Available software engineers with Python, AWS, positive feedback, under 120k, contacted in last 14 days
27. Count candidates by industry, sorted by count
28. Average desired salary for available candidates by job title category
29. Candidates with highest skills match (multiple OR conditions)
30. Complex multi-table query (when clients/jobs tables added)

### Evaluation Metrics

**Success criteria:**

| Metric | MVP (Day 1) | Production (Week 1) | Optimized (Ongoing) |
|--------|-------------|---------------------|---------------------|
| **Accuracy** | 60-70% | 80-85% | 90%+ |
| **Test cases** | 5 | 30+ | 50+ |
| **LLM judge** | No | Yes | Yes |
| **Failure logging** | No | Yes | Yes |
| **Optimization loops** | 0 | 1-2 | Weekly |

---

## Known Challenges & Solutions

### Challenge 1: Comma-Separated Skills

**Problem**: Skills stored as "Python, AWS, Django" - can't use exact match

**Solution Applied**:
- System prompt explicitly explains comma-separated format
- All skill examples use `ILIKE '%skill%'`
- Multi-skill examples use `AND` or `OR` with multiple `ILIKE`

**Example in prompt**:
```sql
-- "Python AND AWS"
WHERE primary_skills ILIKE '%python%' AND primary_skills ILIKE '%aws%'
```

**Expected accuracy impact**: +15% on skills-based queries

---

### Challenge 2: Status Contains Client IDs

**Problem**: "Interviewing - CLT001" doesn't match exact "Interviewing"

**Solution Applied**:
- System prompt explains status pattern
- All status examples use `ILIKE '%interview%'`
- Documented status categories in prompt

**Example in prompt**:
```
Status values: "Available", "Interviewing - CLT###", "Offer Pending - CLT###"
To filter by category: current_status ILIKE '%interview%'
```

**Expected accuracy impact**: +10% on status queries

---

### Challenge 3: Salary Notation Variations

**Problem**: Users say "100k", "£100k", "100000" - all mean same thing

**Solution Applied**:
- System prompt includes salary interpretation rules
- Examples show "k" notation conversion
- Explicit guidance: interpret "k" as thousands

**Example in prompt**:
```
"Under £100k" or "under 100k" → desired_salary < 100000
```

**Expected accuracy impact**: +5% on salary queries

---

### Challenge 4: Case Sensitivity

**Problem**: "python" vs "Python" vs "PYTHON"

**Solution Applied**:
- System prompt mandates `ILIKE` for ALL text searches
- Explicit section on case-insensitive matching
- All 20 examples use `ILIKE` consistently

**Expected accuracy impact**: +20% on all text-based queries (CRITICAL)

---

### Challenge 5: Multi-Table Queries (Future)

**Problem**: When clients/jobs tables added, need to JOIN

**Current Solution**:
- Single-table system prompt (candidates only)
- When new tables added, must update prompt with:
  - Complete new table schemas
  - Foreign key relationships
  - JOIN examples (15+)

**Future Preparation**:
- Keep system prompt in version control
- Plan for systematic prompt updates
- Test multi-table queries extensively before production

---

## Next Steps

### Immediate (Today)

1. ✅ **Review system prompt** - [prompts/candidates_nl2sql_system_prompt.txt](prompts/candidates_nl2sql_system_prompt.txt)
2. 🟡 **Copy security files** from `nl2sql/source_copies/CRITICAL/`
3. 🟡 **Set up OpenAI client** with temperature = 0.2
4. 🟡 **Test with 5 queries** from CSV:
   - "Find Alex Roberts"
   - "Show Python developers"
   - "Available candidates"
   - "Candidates wanting under 100k"
   - "Who interviewed recently?"

### This Week

1. 🔴 **Create 30 test cases** (use CSV for reference)
2. 🔴 **Implement LLM judge**
3. 🔴 **Set up failure logging**
4. 🔴 **Run first full test suite**
5. 🔴 **Analyze failures** and update prompt
6. 🔴 **Achieve 80% accuracy**

### Ongoing

1. 🔴 **Weekly optimization loops**
2. 🔴 **Add clients table** (when ready)
3. 🔴 **Add jobs table** (when ready)
4. 🔴 **Multi-table JOIN examples**
5. 🔴 **Production deployment**

---

## Resources

### Reference Files

**Location**: `nl2sql/source_copies/`

**Critical (must copy):**
- `CRITICAL/1_sanitization_function.ts` - Input sanitization
- `CRITICAL/2_sql_execution_hardening.ts` - SQL execution
- `CRITICAL/3_llm_judge_equivalence.ts` - Equivalence checking

**Important (adapt):**
- `IMPORTANT/1_system_prompt_template.txt` - Template used
- `IMPORTANT/2_multi_provider_ai_client.ts` - AI integration
- `IMPORTANT/3_clarity_evaluation.ts` - Optional pre-processing

**Useful (reference):**
- `USEFUL/1_test_case_format.json` - Test structure
- `USEFUL/2_evaluation_scorer.ts` - Accuracy calculation
- `USEFUL/3_schema_introspection.ts` - Auto schema extraction

### Documentation

**Guides read:**
- `nl2sql/NL2SQL_BEST_PRACTICES.md` - Comprehensive best practices
- `nl2sql/IMPLEMENTATION_GUIDE_FOR_NEW_PROJECT.md` - Step-by-step guide
- `nl2sql/INSTRUCTIONS_FOR_AI_ASSISTANT.md` - Implementation instructions
- `nl2sql/REFERENCE_FILES_MANIFEST.md` - File descriptions
- `nl2sql/source_copies/README.md` - Reference files guide

### Supabase Project

**Project ID**: `pauypyjqosrenuxveskn`
**Database**: PostgreSQL 15.8.1.121
**Region**: eu-north-1
**Current tables**: candidates (100 rows)

---

## Conclusion

This document captures the key learnings from studying a production NL2SQL system (90%+ accuracy) and applies them specifically to ProActive People's recruitment database.

**Key Achievements:**

1. ✅ **System prompt created** with 20 recruitment-specific examples
2. ✅ **All data patterns analyzed** from 100-candidate CSV
3. ✅ **Business logic encoded** (skills, status, salary, dates)
4. ✅ **Security requirements documented** (3-layer defense)
5. ✅ **Testing strategy defined** (30 test cases planned)
6. ✅ **Implementation roadmap** (MVP → Production → Optimized)

**Next Critical Step**: Implement security layer and test with real queries.

**Expected Outcome**: 60-70% accuracy day 1, 80-85% week 1, 90%+ ongoing

---

**Document maintained by**: Claude (AI Assistant)
**Last updated**: 2025-10-21
**Version**: 1.0
**Status**: Active implementation guide
