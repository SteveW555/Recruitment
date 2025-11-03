# NL2SQL Implementation Guide for New Projects

**How to implement production-grade Natural Language to SQL translation in ANY project**

---

## Overview

This guide shows you how to implement the battle-tested NL2SQL patterns from this codebase into your own project, regardless of your database schema or domain.

### What You'll Build

A complete NL2SQL system with:
- ✅ Security-hardened input processing
- ✅ Multi-provider AI support (OpenAI, Groq, Anthropic, Google)
- ✅ Automated evaluation with LLM judge
- ✅ Continuous improvement through failure analysis
- ✅ Three-stage pipeline: Clarity → Generation → Execution

### Time Investment

- **Minimum viable**: 4-6 hours (core system only)
- **Production-ready**: 2-3 days (with testing & evaluation)
- **Full implementation**: 1 week (with optimization loop)

---

## Step-by-Step Implementation

### Phase 1: System Prompt Creation (4 hours) - **MOST CRITICAL**

This is 80% of your success. Do NOT skip or rush this.

#### 1.1 Extract Your Database Schema

**Files to study as examples**:
- `src/backend/sql/schemaReporter.ts` - How to introspect schema
- `src/backend/sql/schema_representation/wishlist500_schema.json` - JSON format

**Action**: Create a schema introspection script:

```typescript
// Example: getYourSchema.ts
import { Client } from 'pg'; // or your DB client

async function introspectSchema() {
  const client = new Client({ /* your config */ });
  await client.connect();

  // Get all tables
  const tables = await client.query(`
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE'
  `);

  // For each table, get columns
  for (const table of tables.rows) {
    const columns = await client.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns
      WHERE table_schema = 'public' AND table_name = $1
      ORDER BY ordinal_position
    `, [table.table_name]);

    // Get primary keys
    const pks = await client.query(`
      SELECT kcu.column_name
      FROM information_schema.table_constraints tc
      JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
      WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_name = $1
    `, [table.table_name]);

    // Get foreign keys
    const fks = await client.query(`
      SELECT kcu.column_name, ccu.table_name AS foreign_table_name
      FROM information_schema.table_constraints AS tc
      JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
      JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
      WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = $1
    `, [table.table_name]);

    // Save to JSON
    console.log(JSON.stringify({
      table_name: table.table_name,
      columns: columns.rows,
      primary_keys: pks.rows,
      foreign_keys: fks.rows
    }, null, 2));
  }
}
```

#### 1.2 Create Your System Prompt

**PRIMARY REFERENCE FILE**: `src/backend/sql/promptEval/prompts/sqlSysPrompt.txt`

**This file is your TEMPLATE. Study it completely.**

**Structure to follow**:

```
## You are a highly skilled SQL expert...

## Database Schema:

[TABLE 1] — brief description
    column_id type PK
    column_name type FK → other_table
    column_x type nullable

[TABLE 2] — brief description
    ...

[Continue for ALL tables]

## Important Notes & Querying Logic:

**Case-Insensitive Matching:**
* Always use ILIKE '%value%' for text comparisons
* Use LOWER(column) = LOWER('value') for exact matches

**General Query Construction:**
* Always use table aliases (t1, t2, u, p, etc.)
* Only select explicitly requested columns
* Use LEFT JOIN when relationships are optional
* Use INNER JOIN only when match is required

**[YOUR DOMAIN-SPECIFIC LOGIC]:**
* [Add rules specific to YOUR business logic]
* [Example: "When user says 'active users', filter WHERE status = 'active'"]
* [Example: "Default date range is last 30 days unless specified"]

## Examples:

* **Simple Query:**
    * Natural Language: "Show all active users"
    * SQL: `select u.username, u.email from users as u where u.status = 'active';`

* **Join Query:**
    * Natural Language: "Find orders for customer John Smith"
    * SQL: `select o.order_id, o.total from orders as o join customers as c on o.customer_id = c.customer_id where c.name ilike '%john smith%';`

[Add 13+ MORE examples covering YOUR domain]

Your response MUST contain only the raw SQL query string.
Do not include markdown, explanations, or any other text.
```

**CRITICAL**: You need **15+ examples** covering:
1. Simple SELECT (2-3 examples)
2. WHERE filters (2-3 examples)
3. JOINs (3-4 examples)
4. Aggregations (COUNT, SUM, AVG) (2-3 examples)
5. Complex queries (multiple JOINs, subqueries) (2-3 examples)
6. Your domain-specific edge cases (3-4 examples)

#### 1.3 Add Domain-Specific Business Logic

**Study these sections in `sqlSysPrompt.txt`**:
- Lines 59-74: "Querying Project Data"
- Lines 80-85: "Subcategory Matching"

**Your version should include**:

```
**[YOUR DOMAIN] Specific Logic:**
* When user mentions [COMMON_TERM], map to [ACTUAL_COLUMN]
* Default filters: [LIST ANY IMPLIED FILTERS]
* Special handling for [EDGE_CASES]
* Synonym mapping: [USER_TERM] → [DATABASE_VALUE]
```

**Example for e-commerce**:
```
**E-Commerce Specific Logic:**
* "Recent orders" means last 30 days: WHERE order_date > NOW() - INTERVAL '30 days'
* "Top customers" means by total spend: ORDER BY SUM(order_total) DESC
* Product search uses both product_name and product_description with ILIKE
* "Available" products means in_stock = true AND active = true
```

---

### Phase 2: Security Implementation (1 hour)

#### 2.1 Input Sanitization

**REFERENCE FILE**: `src/backend/sql/promptEval/testing.ts:61-84`

**Copy this function to your project**:

```typescript
// sanitize.ts
export function sanitizeUserInput(userInput: string): [string, boolean] {
  if (!userInput) {
    return ['', false];
  }

  let sanitized = userInput;

  // Remove SQL comment markers (prevents injection)
  sanitized = sanitized.replace(/--.*$/gm, '');
  sanitized = sanitized.replace(/\/\*.*?\*\//gs, '');

  // Remove single quotes (prevents string escaping)
  sanitized = sanitized.replace(/'/g, '');

  // Remove semicolons (prevents multi-statement execution)
  sanitized = sanitized.replace(/;/g, '');

  // Trim whitespace
  sanitized = sanitized.trim();

  const wasModified = (sanitized !== userInput);

  // IMPORTANT: Log when sanitization occurs
  if (wasModified) {
    console.warn('⚠️ User input was sanitized. Potential attack attempt?', {
      original: userInput,
      sanitized: sanitized
    });
  }

  return [sanitized, wasModified];
}
```

**Usage**:
```typescript
// Before sending to LLM
const [cleanInput, wasSanitized] = sanitizeUserInput(userRequest);

if (wasSanitized) {
  // Log to security monitoring system
  securityLog.warn('Input sanitization triggered', { userRequest });
}

// Use cleanInput for LLM processing
const sql = await generateSQL(cleanInput);
```

#### 2.2 SQL Execution Hardening

**REFERENCE FILE**: `src/backend/sql/supabase/supabaseQuery.ts:35-69`

**Pattern to implement**:

```typescript
// executeSQL.ts
export async function executeSQL(sqlQuery: string): Promise<{
  data: any[] | null;
  error: any;
}> {
  try {
    // Clean the SQL
    const cleanSQL = sqlQuery.trim().replace(/;$/, '');

    // Execute via RPC or stored procedure (NOT direct string concatenation!)
    // For PostgreSQL with Supabase:
    const { data, error } = await supabase.rpc('execute_sql', {
      query_text: cleanSQL
    });

    // For direct PostgreSQL:
    // const result = await client.query(cleanSQL);

    // For MySQL:
    // const [rows] = await connection.query(cleanSQL);

    if (error) {
      console.error('❌ SQL execution failed:', error.message);
      return { data: null, error };
    }

    if (!data || data.length === 0) {
      console.warn('⚠️ Query returned no results');
    } else {
      console.log('✅ Query succeeded:', data.length, 'rows');
    }

    return { data, error: null };

  } catch (err) {
    console.error('❌ Exception during SQL execution:', err);
    return { data: null, error: err };
  }
}
```

**IMPORTANT**: Use RPC/stored procedures, NOT string concatenation:

```typescript
// ❌ NEVER DO THIS
const result = await db.query(`SELECT * FROM users WHERE id = ${userId}`);

// ✅ DO THIS
const result = await db.rpc('execute_sql', { query_text: sqlQuery });
```

---

### Phase 3: AI Integration (2 hours)

#### 3.1 Multi-Provider Setup

**REFERENCE FILE**: `src/backend/sql/promptEval/ai.ts`

**Copy and adapt this structure**:

```typescript
// ai.ts
import OpenAI from 'openai';
import Groq from 'groq-sdk';
import Anthropic from '@anthropic-ai/sdk';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize clients
const openaiClient = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const groqClient = new Groq({ apiKey: process.env.GROQ_API_KEY });
const anthropicClient = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const googleClient = new GoogleGenerativeAI(process.env.GOOGLE_AI_KEY || '');

// Provider detection
export function getProviderForModel(modelName: string): string {
  const providers: Record<string, string[]> = {
    openai: ['gpt-4o', 'gpt-4o-mini', 'o3-mini'],
    groq: ['llama3-70b-8192', 'llama3-8b-8192', 'llama-3.3-70b-versatile'],
    anthropic: ['claude-3-7-sonnet-latest', 'claude-3-7-haiku-latest'],
    google: ['gemini-2.0-flash', 'gemini-2.5-pro-preview-03-25']
  };

  for (const [provider, models] of Object.entries(providers)) {
    if (models.some(m => modelName.includes(m))) {
      return provider;
    }
  }

  return 'openai'; // default
}

// Unified interface
export async function callAI(
  modelName: string,
  userPrompt: string,
  systemPrompt: string,
  options: {
    temperature?: number;
    response_format?: { type: string };
  } = {}
): Promise<string> {
  const provider = getProviderForModel(modelName);
  const temperature = options.temperature ?? 0.2;

  if (provider === 'openai') {
    const completion = await openaiClient.chat.completions.create({
      model: modelName,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature,
      response_format: options.response_format
    });
    return completion.choices[0]?.message?.content || '';
  }

  if (provider === 'groq') {
    const completion = await groqClient.chat.completions.create({
      model: modelName,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature,
      response_format: options.response_format
    });
    return completion.choices[0]?.message?.content || '';
  }

  // Add Anthropic, Google as needed
  throw new Error(`Provider ${provider} not implemented`);
}
```

#### 3.2 Core NL2SQL Function

**Pattern**:

```typescript
// nl2sql.ts
import { callAI } from './ai';
import { sanitizeUserInput } from './sanitize';
import { executeSQL } from './executeSQL';
import { YOUR_SYSTEM_PROMPT } from './prompts';

export async function convertNL2SQL(
  userQuery: string,
  model: string = 'gpt-4o-mini'
): Promise<{
  sql: string;
  data: any[] | null;
  error: any;
}> {
  // 1. Sanitize input
  const [cleanQuery, wasSanitized] = sanitizeUserInput(userQuery);

  try {
    // 2. Generate SQL
    const sql = await callAI(
      model,
      cleanQuery,
      YOUR_SYSTEM_PROMPT,
      { temperature: 0.2, response_format: { type: 'text' } }
    );

    console.log('Generated SQL:', sql);

    // 3. Execute SQL
    const { data, error } = await executeSQL(sql);

    return { sql, data, error };

  } catch (err) {
    console.error('NL2SQL error:', err);
    return {
      sql: 'ERROR',
      data: null,
      error: err
    };
  }
}
```

---

### Phase 4: Clarity Evaluation (Optional, 3 hours)

**REFERENCE FILE**: `src/backend/sql/promptEval/clarityEvaluator.ts`

**When to implement**: If you expect ambiguous user queries.

**System prompt to create**:

```typescript
// clarityPrompt.ts
export const CLARITY_SYSTEM_PROMPT = `
You are a clarity analyzer for a Text-to-SQL system.

Database Schema:
[YOUR SCHEMA HERE - same as main prompt]

Your task:
1. Analyze the user's query
2. Score clarity 1-10
3. Take action based on score:
   - Score 9-10: Return original unchanged
   - Score 6-8: Minor corrections only
   - Score 4-5: Rephrase for clarity
   - Score 1-3: Request clarification with 3 options

Output JSON:
{
  "clarity_score": 7,
  "status": "CLEAR" | "NEEDS_CLARIFICATION",
  "clarified_prompt": "...",
  "options": ["option1", "option2", "option3"] | null,
  "reasoning": "..."
}
`;
```

**Implementation**:

```typescript
export async function evaluateClarity(
  userQuery: string,
  model: string = 'gpt-4o-mini'
): Promise<{
  clarity_score: number;
  status: 'CLEAR' | 'NEEDS_CLARIFICATION';
  clarified_prompt: string | null;
  options: string[] | null;
}> {
  const response = await callAI(
    model,
    userQuery,
    CLARITY_SYSTEM_PROMPT,
    { temperature: 0.3, response_format: { type: 'json_object' } }
  );

  return JSON.parse(response);
}
```

**Usage**:

```typescript
// Before SQL generation
const clarity = await evaluateClarity(userQuery);

if (clarity.status === 'NEEDS_CLARIFICATION') {
  // Return options to user for selection
  return { options: clarity.options };
}

// Use clarified prompt
const result = await convertNL2SQL(clarity.clarified_prompt);
```

---

### Phase 5: Testing & Evaluation (4 hours)

#### 5.1 Create Test Cases

**REFERENCE FILES**:
- `data/prompts.json` - Simple test format
- `src/backend/sql/promptEval/prompts/promptGen.ts` - Template generator

**Your test format**:

```json
[
  {
    "test_name": "simple_select_users",
    "nl": "show all active users",
    "nl_simple": "active users",
    "nl_focused": "Retrieve all users where status is active",
    "known_sql": "SELECT * FROM users WHERE status = 'active';",
    "difficulty": "easy",
    "complexity": 1
  },
  {
    "test_name": "join_orders_customers",
    "nl": "show orders for customer John",
    "nl_simple": "john orders",
    "nl_focused": "Display all orders placed by the customer named John",
    "known_sql": "SELECT o.* FROM orders o JOIN customers c ON o.customer_id = c.id WHERE c.name ILIKE '%john%';",
    "difficulty": "medium",
    "complexity": 5
  }
]
```

**Create 20-30 test cases** covering:
- Simple SELECTs (complexity 1-2)
- WHERE filters (complexity 3-4)
- JOINs (complexity 5-7)
- Aggregations (complexity 6-8)
- Complex queries (complexity 8-10)

#### 5.2 LLM Judge for Equivalence

**REFERENCE FILE**: `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`

**Copy this pattern exactly**:

```typescript
// queryJudge.ts
const EQUIVALENCE_PROMPT = `
You are an SQL expert. Determine if two queries are semantically equivalent.

Consider equivalent:
- Table aliases (users vs u)
- Column order (SELECT a, b vs SELECT b, a)
- Whitespace/formatting
- ORDER BY (doesn't affect equivalence)
- SELECT * vs SELECT primary_column (for simple queries)
- Exact match vs LIKE with % wildcards on same value

Respond ONLY with "Equivalent" or "Not Equivalent".
`;

export async function queriesAreEquivalent(
  query1: string,
  query2: string,
  model: string = 'gpt-4o-mini'
): Promise<boolean> {
  const userPrompt = `
Query 1:
\`\`\`sql
${query1}
\`\`\`

Query 2:
\`\`\`sql
${query2}
\`\`\`

Are these equivalent?`;

  const response = await callAI(model, userPrompt, EQUIVALENCE_PROMPT, {
    temperature: 0.2
  });

  return response.trim().toLowerCase() === 'equivalent';
}
```

#### 5.3 Automated Test Runner

```typescript
// testRunner.ts
import { convertNL2SQL } from './nl2sql';
import { executeSQL } from './executeSQL';
import { queriesAreEquivalent } from './queryJudge';
import testCases from './tests.json';

interface TestResult {
  test_name: string;
  passed: boolean;
  generated_sql: string;
  expected_sql: string;
  equivalent: boolean;
  error?: string;
}

export async function runTests(model: string = 'gpt-4o-mini'): Promise<TestResult[]> {
  const results: TestResult[] = [];

  for (const test of testCases) {
    console.log(`\nTesting: ${test.test_name}`);
    console.log(`Query: "${test.nl}"`);

    try {
      // Generate SQL
      const { sql, error } = await convertNL2SQL(test.nl, model);

      if (error) {
        results.push({
          test_name: test.test_name,
          passed: false,
          generated_sql: sql,
          expected_sql: test.known_sql,
          equivalent: false,
          error: error.message
        });
        continue;
      }

      // Check equivalence
      const equivalent = await queriesAreEquivalent(sql, test.known_sql);

      results.push({
        test_name: test.test_name,
        passed: equivalent,
        generated_sql: sql,
        expected_sql: test.known_sql,
        equivalent
      });

      console.log(equivalent ? '✅ PASS' : '❌ FAIL');

    } catch (err) {
      console.error('Test error:', err);
      results.push({
        test_name: test.test_name,
        passed: false,
        generated_sql: 'ERROR',
        expected_sql: test.known_sql,
        equivalent: false,
        error: err.message
      });
    }
  }

  // Summary
  const passed = results.filter(r => r.passed).length;
  console.log(`\n📊 Results: ${passed}/${results.length} passed (${(passed/results.length*100).toFixed(1)}%)`);

  return results;
}
```

#### 5.4 Failure Logging

**REFERENCE FILE**: `data/incorrect_queries.txt`

```typescript
// logger.ts
import * as fs from 'fs';

export function logFailure(
  nl: string,
  expectedSQL: string,
  generatedSQL: string,
  model: string
) {
  const entry = `
${nl}
${expectedSQL}
${generatedSQL}
${model}

`;

  fs.appendFileSync('failures.txt', entry);
}

// Usage in test runner
if (!equivalent) {
  logFailure(test.nl, test.known_sql, sql, model);
}
```

**Analyze failures**:

```bash
# After tests, find patterns
cat failures.txt | grep -v "^$" | grep -v "SELECT" | sort | uniq -c | sort -rn
```

---

### Phase 6: Continuous Improvement (Ongoing)

#### 6.1 Failure Analysis Loop

**Process**:

1. **Run tests** → `npm run test:nl2sql`
2. **Review failures** → `cat failures.txt`
3. **Identify patterns** → Common mistakes
4. **Update system prompt** → Add failing examples
5. **Re-test** → Verify improvement

**Common patterns to look for**:
- Column name confusion (e.g., searching wrong column)
- Wrong table selection
- Missing JOINs
- Synonym issues (user says "big", DB has "large")
- Date range assumptions

#### 6.2 Adding Examples to System Prompt

When you find a failure:

```
❌ User: "show big items"
   Generated: SELECT * FROM items WHERE size = 'big'
   Expected:  SELECT * FROM items WHERE size = 'large'
```

**Add to system prompt**:

```
* **Size Synonyms:**
    * Natural Language: "show big items"
    * SQL: `SELECT * FROM items WHERE size = 'large';`
    * Note: Users may say "big" but database uses "large"
```

---

## Files to Copy as Reference

### Essential Files (Copy to your project for reference)

1. **`src/backend/sql/promptEval/prompts/sqlSysPrompt.txt`**
   - **Why**: This is your template for system prompts
   - **How to use**: Replace schema and examples with yours
   - **Keep**: Structure, rules, output format specification

2. **`src/backend/sql/promptEval/testing.ts:61-84`**
   - **Why**: Input sanitization function
   - **How to use**: Copy function exactly, use before LLM calls
   - **Keep**: All regex patterns, logging

3. **`src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`**
   - **Why**: LLM judge for SQL equivalence
   - **How to use**: Copy system prompt and function
   - **Adapt**: Add your domain-specific equivalence rules

4. **`src/backend/sql/promptEval/ai.ts`**
   - **Why**: Multi-provider AI architecture
   - **How to use**: Copy provider detection and unified interface
   - **Adapt**: Add/remove providers as needed

5. **`src/backend/sql/supabase/supabaseQuery.ts:35-69`**
   - **Why**: Secure SQL execution pattern
   - **How to use**: Adapt to your database client
   - **Keep**: Cleanup logic, error handling, logging

### Example Files (For patterns and inspiration)

6. **`src/backend/sql/promptEval/evaluator.ts`**
   - **Why**: Accuracy scoring algorithm
   - **How to use**: Understand field-level comparison
   - **Adapt**: Match your evaluation needs

7. **`src/backend/sql/promptEval/clarityEvaluator.ts`**
   - **Why**: Pre-processing ambiguous queries
   - **How to use**: Copy tiered response strategy
   - **Optional**: Only if you expect ambiguous input

8. **`data/prompts.json`**
   - **Why**: Simple test case format
   - **How to use**: Template for your tests
   - **Replace**: All NL and SQL with your domain

9. **`src/backend/sql/promptEval/promptGen.ts`**
   - **Why**: Complexity-based test generation
   - **How to use**: Understand graduated complexity
   - **Optional**: For generating synthetic tests

### Documentation Files

10. **`NL2SQL_BEST_PRACTICES.md`** (this codebase)
    - **Why**: Complete reference guide
    - **How to use**: Consult during implementation
    - **Keep**: All checklists and patterns

---

## Minimal Viable Implementation (4-6 hours)

If you have limited time, implement ONLY these:

### 1. System Prompt (3 hours)
- Extract your schema
- Write 15+ examples
- Add case-insensitive rules

### 2. Security (30 min)
- Input sanitization function
- SQL cleanup before execution

### 3. AI Integration (1 hour)
- OpenAI client setup
- Single provider (gpt-4o-mini)
- Temperature = 0.2

### 4. Basic Testing (30 min)
- 5-10 test cases
- Manual verification

**This gives you a working NL2SQL system in one day.**

---

## Production-Ready Implementation (2-3 days)

Add these for production:

### Day 1: Core System
- ✅ System prompt with 20+ examples
- ✅ Multi-provider AI support
- ✅ Security hardening
- ✅ Error handling

### Day 2: Testing & Evaluation
- ✅ 30+ test cases (all complexity levels)
- ✅ LLM judge for equivalence
- ✅ Automated test runner
- ✅ Failure logging

### Day 3: Optimization
- ✅ Run full test suite
- ✅ Analyze failures
- ✅ Update system prompt
- ✅ Re-test and validate

---

## Checklist for New Project

```
[ ] Phase 1: System Prompt Creation
    [ ] Schema introspection script written
    [ ] Schema JSON generated
    [ ] System prompt created with YOUR schema
    [ ] 15+ examples written covering YOUR domain
    [ ] Case-insensitive rules added
    [ ] Domain-specific business logic documented
    [ ] Output format specified

[ ] Phase 2: Security Implementation
    [ ] Input sanitization function copied
    [ ] Sanitization logging implemented
    [ ] SQL execution hardening added
    [ ] RPC/stored procedure setup (if using)

[ ] Phase 3: AI Integration
    [ ] OpenAI client configured
    [ ] Multi-provider support (optional)
    [ ] callAI() function implemented
    [ ] Temperature set to 0.2
    [ ] Error handling added

[ ] Phase 4: Testing & Evaluation
    [ ] 20+ test cases created (JSON format)
    [ ] LLM judge function copied
    [ ] Automated test runner written
    [ ] Failure logging implemented

[ ] Phase 5: Deployment
    [ ] Environment variables set
    [ ] API endpoint created
    [ ] Error responses standardized
    [ ] Performance monitoring added

[ ] Phase 6: Optimization (Ongoing)
    [ ] Baseline accuracy measured
    [ ] Failure patterns identified
    [ ] System prompt updated
    [ ] Re-tested and validated
```

---

## Common Pitfalls to Avoid

### ❌ Don't Do This

1. **Skip security hardening**
   - "I'll add it later" → Never happens, system gets hacked

2. **Use string matching for evaluation**
   - LLM judge is essential for accepting valid variations

3. **Write too few examples**
   - "10 should be enough" → No, you need 15-20 minimum

4. **Ignore failure logging**
   - Can't improve what you don't measure

5. **Test only happy paths**
   - Need edge cases, errors, ambiguous queries

6. **Hard-code values in system prompt**
   - Schema changes → prompt breaks

### ✅ Do This Instead

1. **Implement security from day 1**
   - Sanitization + RPC execution

2. **Use LLM judge for all evaluation**
   - Semantic equivalence, not string match

3. **Write 20+ examples minimum**
   - Cover all query types and complexity levels

4. **Log every failure**
   - Structured format for analysis

5. **Test unhappy paths extensively**
   - Ambiguous queries, typos, edge cases

6. **Auto-sync schema to prompt**
   - Introspection → JSON → Prompt generation

---

## Expected Outcomes

### After Minimal Implementation (1 day)
- ✅ 60-70% accuracy on simple queries
- ✅ Security hardening in place
- ✅ Basic AI integration working

### After Production Implementation (3 days)
- ✅ 80-85% accuracy on standard queries
- ✅ Multi-provider support
- ✅ Automated testing and evaluation
- ✅ Failure analysis pipeline

### After 1 Week of Optimization
- ✅ 90%+ accuracy on trained patterns
- ✅ Continuous improvement loop running
- ✅ Production-ready monitoring
- ✅ Model comparison data

---

## Next Steps

1. **Copy reference files** to your project:
   ```bash
   mkdir -p your-project/nl2sql/reference
   cp sqlSysPrompt.txt your-project/nl2sql/reference/
   cp testing.ts your-project/nl2sql/reference/
   cp queryEquivalenceJudge.ts your-project/nl2sql/reference/
   cp ai.ts your-project/nl2sql/reference/
   ```

2. **Start with schema introspection**:
   - Run your database introspection script
   - Generate schema JSON
   - Verify completeness

3. **Create your system prompt**:
   - Use `sqlSysPrompt.txt` as template
   - Replace schema section
   - Write 15+ YOUR domain examples
   - Add YOUR business logic rules

4. **Implement security**:
   - Copy sanitization function
   - Set up secure SQL execution
   - Test with malicious inputs

5. **Test with real queries**:
   - Start with 5-10 simple test cases
   - Gradually add complexity
   - Measure baseline accuracy

6. **Iterate based on failures**:
   - Run tests
   - Analyze failures
   - Update prompt
   - Re-test

---

## Support & Resources

**Reference this guide** whenever you:
- Add new tables to schema → Update prompt
- Find a failure pattern → Add example
- Switch AI models → Check temperature settings
- Deploy to production → Review security checklist

**Key principle**: The system prompt is 80% of your success. Invest time upfront to get it right.

---

**Good luck with your implementation!**

*This guide is based on production battle-tested patterns from a real-world NL2SQL system with 90%+ accuracy.*
