# Instructions for AI Assistant: Implementing NL2SQL in New Project

**You are an AI assistant helping a developer implement Natural Language to SQL translation. These are your implementation instructions.**

---

## Your Goal

Help the user build a production-grade NL2SQL system for their database using proven patterns from this reference codebase.

---

## Phase-by-Phase Instructions

### Phase 1: System Prompt Creation (HIGHEST PRIORITY)

**This is 80% of success. Do NOT proceed until this is done correctly.**

#### Step 1.1: Extract User's Schema

Ask the user:
```
I need to understand your database schema. Please provide either:
1. Database connection details (I'll introspect)
2. Schema export/dump
3. List of tables with columns and types
```

Then create introspection script using pattern from `src/backend/sql/schemaReporter.ts`.

#### Step 1.2: Create System Prompt

**Template to follow**: `src/backend/sql/promptEval/prompts/sqlSysPrompt.txt`

**Required sections**:

1. **Role definition**:
```
## You are a highly skilled SQL expert. Your task is to translate natural language questions into valid [DATABASE_TYPE] queries.
```

2. **Complete schema**:
```
## Database Schema:

[TABLE_1] — description
    column_id TYPE PK
    column_name TYPE FK → referenced_table
    ...

[Repeat for ALL tables]
```

3. **Querying rules**:
```
**Case-Insensitive Matching:**
* Always use ILIKE '%value%' for text (PostgreSQL)
* Or LOWER(column) = LOWER('value') for exact match

**General Query Construction:**
* Always use table aliases
* Use LEFT JOIN for optional relationships
* Only select requested columns
```

4. **Domain-specific logic**:
Ask user: "What are your business rules?" Then add:
```
**[DOMAIN] Specific Logic:**
* When user says X, it means Y
* Default filters: Z
* Special cases: ...
```

5. **Examples (15+ required)**:
```
* **Simple Query:**
    * Natural Language: "..."
    * SQL: `...`

[Continue for 15+ examples covering:]
- Simple SELECT (3)
- WHERE filters (3)
- JOINs (4)
- Aggregations (3)
- Complex queries (3)
```

6. **Output format**:
```
Your response MUST contain only the raw SQL query string.
Do not include markdown, explanations, or other text.
```

**Validation checklist**:
- [ ] All tables documented?
- [ ] All columns listed?
- [ ] Primary/foreign keys marked?
- [ ] 15+ examples written?
- [ ] Case-insensitive rules added?
- [ ] Domain logic included?
- [ ] Output format specified?

### Phase 2: Security Implementation

**Critical files to reference**:
- `src/backend/sql/promptEval/testing.ts:61-84` (sanitization)
- `src/backend/sql/supabase/supabaseQuery.ts:35-69` (execution)

#### Step 2.1: Input Sanitization

Create this function EXACTLY as shown:

```typescript
export function sanitizeUserInput(input: string): [string, boolean] {
  let sanitized = input;

  // Remove SQL comments
  sanitized = sanitized.replace(/--.*$/gm, '');
  sanitized = sanitized.replace(/\/\*.*?\*\//gs, '');

  // Remove dangerous characters
  sanitized = sanitized.replace(/'/g, '');
  sanitized = sanitized.replace(/;/g, '');
  sanitized = sanitized.trim();

  const wasModified = (sanitized !== input);

  if (wasModified) {
    console.warn('⚠️ Input sanitized - potential attack?', { input, sanitized });
  }

  return [sanitized, wasModified];
}
```

**Usage**: ALWAYS sanitize before sending to LLM.

#### Step 2.2: SQL Execution Hardening

```typescript
export async function executeSQL(sql: string) {
  // Clean SQL
  const cleanSQL = sql.trim().replace(/;$/, '');

  try {
    // Execute via RPC/stored procedure (NOT direct query!)
    const result = await db.rpc('execute_sql', { query_text: cleanSQL });

    if (result.error) {
      console.error('❌ SQL failed:', result.error);
    } else {
      console.log('✅ SQL succeeded:', result.data?.length, 'rows');
    }

    return result;
  } catch (err) {
    console.error('❌ Exception:', err);
    return { data: null, error: err };
  }
}
```

**Important**: Use RPC/stored procedures, NOT string concatenation.

### Phase 3: AI Integration

**Reference file**: `src/backend/sql/promptEval/ai.ts`

#### Step 3.1: Setup AI Client

Ask user: "Which AI provider? (OpenAI/Groq/Anthropic/Google)"

Then implement:

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export async function callAI(
  model: string,
  userPrompt: string,
  systemPrompt: string,
  options = {}
): Promise<string> {
  const temp = options.temperature ?? 0.2; // IMPORTANT: Default 0.2

  const completion = await client.chat.completions.create({
    model,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    temperature: temp,
    response_format: options.response_format
  });

  return completion.choices[0]?.message?.content || '';
}
```

**Critical**: Temperature = **0.2** for SQL generation (deterministic).

#### Step 3.2: Main NL2SQL Function

```typescript
export async function convertNL2SQL(
  userQuery: string,
  model: string = 'gpt-4o-mini'
) {
  // 1. Sanitize
  const [clean, wasSanitized] = sanitizeUserInput(userQuery);

  // 2. Generate SQL
  const sql = await callAI(
    model,
    clean,
    YOUR_SYSTEM_PROMPT,
    { temperature: 0.2 }
  );

  // 3. Execute
  const { data, error } = await executeSQL(sql);

  return { sql, data, error };
}
```

### Phase 4: Testing & Evaluation

**Reference files**:
- `data/prompts.json` (test format)
- `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts` (LLM judge)

#### Step 4.1: Create Test Cases

Ask user to provide 5-10 examples:
```
Please give me natural language queries and their expected SQL:

Example:
- NL: "show active users"
- SQL: "SELECT * FROM users WHERE status = 'active'"
```

Create test file:
```json
[
  {
    "test_name": "simple_select",
    "nl": "show active users",
    "nl_simple": "active users",
    "nl_focused": "Retrieve all users with active status",
    "known_sql": "SELECT * FROM users WHERE status = 'active';",
    "difficulty": "easy",
    "complexity": 1
  }
]
```

#### Step 4.2: LLM Judge Implementation

**Copy from**: `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`

```typescript
const JUDGE_PROMPT = `
You are an SQL expert. Determine if two queries are semantically equivalent.

Consider equivalent:
- Aliases (users vs u)
- Column order
- Formatting
- ORDER BY (doesn't affect results)
- SELECT * vs SELECT id (for simple queries)

Respond ONLY: "Equivalent" or "Not Equivalent"
`;

export async function queriesAreEquivalent(q1: string, q2: string) {
  const response = await callAI(
    'gpt-4o-mini',
    `Query 1: ${q1}\n\nQuery 2: ${q2}\n\nEquivalent?`,
    JUDGE_PROMPT,
    { temperature: 0.2 }
  );

  return response.toLowerCase().includes('equivalent');
}
```

#### Step 4.3: Test Runner

```typescript
export async function runTests() {
  const tests = require('./tests.json');
  let passed = 0;

  for (const test of tests) {
    const { sql } = await convertNL2SQL(test.nl);
    const equivalent = await queriesAreEquivalent(sql, test.known_sql);

    if (equivalent) {
      console.log('✅', test.test_name);
      passed++;
    } else {
      console.log('❌', test.test_name);
      // Log failure
      logFailure(test.nl, test.known_sql, sql);
    }
  }

  console.log(`\n${passed}/${tests.length} passed`);
}
```

#### Step 4.4: Failure Logging

```typescript
import * as fs from 'fs';

export function logFailure(nl: string, expected: string, generated: string) {
  const entry = `${nl}\n${expected}\n${generated}\n\n`;
  fs.appendFileSync('failures.txt', entry);
}
```

### Phase 5: Optimization Loop

#### Step 5.1: Analyze Failures

After running tests:
```bash
cat failures.txt
```

Look for patterns:
- Same mistake repeated?
- Specific columns confused?
- Missing JOINs?

#### Step 5.2: Update System Prompt

For each pattern found, add example to system prompt:

```
Found failure: User says "big items" → Generated wrong size value

Add to prompt:
* **Size Handling:**
    * Natural Language: "show big items"
    * SQL: `SELECT * FROM items WHERE size = 'large';`
    * Note: Users say "big", database uses "large"
```

#### Step 5.3: Re-test

```
npm run test
```

Verify accuracy improved.

---

## Your Communication Strategy

### When Starting

Say:
```
I'll help you implement NL2SQL. This will take 4-6 hours minimum for a basic system, 2-3 days for production-ready.

First, I need your database schema. Do you have:
1. Database connection details?
2. Schema dump/export?
3. Manual list of tables?
```

### During System Prompt Creation

Ask:
```
I'm creating your system prompt. I need:
1. List of all tables with columns
2. Primary keys for each table
3. Foreign key relationships
4. Any business logic rules (e.g., "active users means status='active'")
5. 10-15 example queries you expect users to ask
```

### During Testing

Say:
```
I've created 5 initial tests. Let's run them and see accuracy.

[Run tests]

Results: 3/5 passed (60%)

Failed queries:
1. [Query] - Expected [SQL] but got [SQL]

This is normal for first iteration. We'll analyze failures and improve the system prompt.
```

### During Optimization

Say:
```
I've identified a pattern: [PATTERN]

I'm adding this example to the system prompt:
[EXAMPLE]

Let's re-test to verify improvement.
```

---

## Critical Reminders

1. **System prompt is 80% of success**
   - Don't rush this phase
   - Get complete schema
   - Write comprehensive examples

2. **Security is non-negotiable**
   - Always sanitize input
   - Always use RPC/stored procedures
   - Always log sanitization events

3. **Use LLM judge, not string matching**
   - Semantic equivalence matters
   - Many valid SQL representations exist

4. **Test with three variants**
   - nl_simple: "active users"
   - nl: "show me active users"
   - nl_focused: "Retrieve all users with active status"

5. **Temperature = 0.2 for SQL**
   - Deterministic output
   - Reduced hallucination

6. **Iterate based on failures**
   - Every failure is a learning opportunity
   - Update prompt with failing examples

---

## Files to Reference

**Copy these patterns**:

1. `src/backend/sql/promptEval/prompts/sqlSysPrompt.txt`
   - System prompt structure
   - Example format
   - Rules and guidelines

2. `src/backend/sql/promptEval/testing.ts:61-84`
   - Input sanitization function

3. `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`
   - LLM judge implementation

4. `src/backend/sql/promptEval/ai.ts`
   - Multi-provider AI setup

5. `src/backend/sql/supabase/supabaseQuery.ts:35-69`
   - Secure SQL execution

**Study these patterns**:

6. `src/backend/sql/promptEval/evaluator.ts`
   - Accuracy scoring

7. `data/prompts.json`
   - Test case format

8. `src/backend/sql/promptEval/clarityEvaluator.ts`
   - Optional: Clarity pre-processing

---

## Success Metrics

### Minimum Viable (Day 1)
- ✅ System prompt created with 15+ examples
- ✅ Input sanitization working
- ✅ AI integration complete
- ✅ 5 test cases passing
- ✅ ~60% accuracy on simple queries

### Production Ready (Day 3)
- ✅ 30+ test cases
- ✅ LLM judge implemented
- ✅ Automated testing
- ✅ Failure logging
- ✅ ~80% accuracy

### Optimized (Week 1)
- ✅ Failure analysis complete
- ✅ System prompt refined
- ✅ ~90% accuracy on trained patterns

---

## Common User Questions

**Q: "How long will this take?"**
A: "Minimum 4-6 hours for basic system, 2-3 days for production-ready."

**Q: "What accuracy can I expect?"**
A: "60-70% initially, 80-85% after first optimization, 90%+ after a week of iteration."

**Q: "Which AI model should I use?"**
A: "Start with gpt-4o-mini (fast, cheap). Upgrade to gpt-4o if you need higher accuracy."

**Q: "Do I need all this testing?"**
A: "For production: yes. For prototype: minimum 5-10 test cases."

**Q: "Can I skip the security layer?"**
A: "No. Sanitization and RPC execution are non-negotiable for any system exposed to users."

---

## Your Action Plan

1. **Understand user's database** (30 min)
2. **Create system prompt** (3 hours)
3. **Implement security** (30 min)
4. **Set up AI integration** (1 hour)
5. **Create initial tests** (1 hour)
6. **Run first iteration** (30 min)
7. **Analyze and optimize** (ongoing)

**Total**: ~6 hours for MVP, then iterate.

---

Good luck! Follow this guide step-by-step and you'll build a production-grade NL2SQL system.
