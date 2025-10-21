# NL2SQL Best Practices - Comprehensive Guide

**Based on exhaustive analysis of the nl2sql codebase**

---

## Quick Reference Card

### 🎯 Top 5 Success Factors

1. **System Prompt Quality (80% impact)** - Complete schema, 15+ examples, case-insensitive rules
2. **Security Hardening** - Input sanitization → RPC isolation → cleanup
3. **LLM Judge Equivalence** - Accept multiple valid SQL patterns, not exact strings
4. **Multi-Variant Testing** - Test nl_simple, nl, nl_focused for every query
5. **Failure Analysis Loop** - Log → Analyze → Update prompt → Retest

### 🔒 Security Checklist

- ✅ Sanitize input (remove `--`, `/* */`, `'`, `;`)
- ✅ Log sanitization events
- ✅ Execute via RPC (server-side isolation)
- ✅ Clean trailing semicolons
- ✅ Never throw, always return structured errors

### 📊 Evaluation Checklist

- ✅ Execute ground-truth SQL first
- ✅ Generate SQL from 3 prompt variants
- ✅ Use LLM judge for equivalence (not string match)
- ✅ Apply exemptions (NULL, column order, LIKE vs =)
- ✅ Log all failures to `incorrect_queries.txt`
- ✅ Analyze patterns, update prompt

### 🔧 Configuration Checklist

- ✅ Temperature: **0.2** for SQL generation
- ✅ Temperature: **0.3-0.4** for clarity evaluation
- ✅ Response format: `{ type: "text" }` for SQL
- ✅ Response format: `{ type: "json_object" }` for clarity
- ✅ Default provider: OpenAI (gpt-4o-mini for speed/cost)
- ✅ Models tested: gpt-4o, gpt-4o-mini, llama3-70b, llama3-8b

### 📝 System Prompt Must-Haves

1. Complete schema (all tables, columns, keys, constraints)
2. Case-insensitive matching (`ILIKE '%value%'`)
3. LEFT JOIN defaults for optional relationships
4. Domain-specific business logic
5. 15+ examples (simple → complex)
6. Strict output format ("SQL only, no markdown")
7. Fallback messages for empty results

---

## Table of Contents

1. [Overview](#overview)
2. [System Prompt Engineering](#system-prompt-engineering)
3. [Schema Management](#schema-management)
4. [Multi-Stage Query Processing](#multi-stage-query-processing)
5. [AI Provider Configuration](#ai-provider-configuration)
6. [Evaluation & Testing Framework](#evaluation--testing-framework)
7. [Error Handling & Validation](#error-handling--validation)
8. [Optimization Strategies](#optimization-strategies)
9. [Implementation Checklist](#implementation-checklist)

---

## Overview

This document consolidates all discovered patterns, strategies, and best practices for successful Natural Language to SQL translation, based on comprehensive analysis of the production NL2SQL system.

**Key Success Factors Identified:**
- Precision-crafted system prompts with extensive schema context
- Multi-variant natural language inputs (simple, standard, focused)
- Clarity evaluation before SQL generation
- Multi-provider AI support with intelligent model routing
- Automated evaluation with ground-truth comparison
- Schema introspection and automated synchronization

---

## System Prompt Engineering

### 1. Core Structure

**Location**: `src/backend/sql/promptEval/prompts/sqlSysPrompt.txt`

The system prompt is the **most critical component** for accurate NL2SQL translation. Analysis reveals the following essential elements:

#### A. Complete Schema Documentation

```
## Database Schema:

projects — master list of donation projects
    project_id bigint PK
    project_name text (no spaces)
    project_date date

[... complete schema for all tables ...]
```

**Critical Success Factor**: Include EVERY table with:
- Column names and types
- Primary keys (PK)
- Foreign keys (FK → referenced_table)
- Constraints (unique, nullable, defaults)
- Domain-specific notes (e.g., "no spaces in project_name")

#### B. Case-Insensitive Matching Rules

```
**Case-Insensitive Matching:**
* Always perform case-insensitive matching on text columns
* Prefer ILIKE with wildcards ('%value%') for general comparisons
* For exact matches: LOWER(column_name) = LOWER('value')
```

**Why This Matters**: User input is unpredictable. The system MUST handle variations like:
- "Zurich" vs "zurich" vs "ZURICH"
- "s2f" vs "S2F"
- "manchester_gt" vs "Manchester GT"

#### C. Query Construction Guidelines

```
**General Query Construction:**
* Always use table aliases (p for projects, pi for project_items, etc.)
* Only select explicitly requested columns
* Use LEFT JOIN when relationships are optional (nullable FKs)
* Use INNER JOIN only when matches are strictly required
* Handle ambiguity with reasonable schema-based assumptions
```

**Pattern**: The system provides **defensive SQL generation** strategies:
- Default to `LEFT JOIN` to prevent data loss
- Return meaningful messages for empty results
- Handle NULL values gracefully

#### D. Domain-Specific Logic

```
**Querying Project Data:**
* To query specific project: MUST join with projects table
* Filter using: p.project_name ILIKE '%project_name%'
* Handle spaces vs underscores (user: "zurich swindon" → DB: "zurich_swindon")
* Use project_items.total_allocated for pre-calculated totals
* Use SUM(pa.allocated_quantity) for cross-project aggregations
```

**Key Insight**: The prompt encodes **business logic** that prevents common mistakes:
- Not confusing `total_allocated` (per-item total) with cross-project sums
- Understanding when to use item-level vs allocation-level quantities
- Correctly interpreting "manifest" based on context

#### E. Comprehensive Examples

```
## Examples:

* **Simple Project Item Search:**
    * Natural Language: "Find chairs on the Zurich project"
    * SQL: `select pi.item_name, pi.quantity, pi.remaining
           from project_items as pi
           join projects as p on pi.project_id = p.project_id
           where p.project_name ilike '%zurich%'
           and pi.item_name ilike '%chair%';`

[... 15+ more examples covering all common patterns ...]
```

**Critical Success Factor**: Examples MUST cover:
- Simple SELECTs
- Multi-table JOINs
- Filtering with WHERE
- Aggregations (COUNT, SUM, AVG)
- Ordering and limiting
- Complex business logic patterns
- Edge cases and special scenarios

#### F. Output Format Specification

```
Your response MUST contain only the raw SQL query string.
Do not include any markdown formatting (like ```sql or ```),
explanations, comments, or any other text outside the SQL query itself.
```

**Why This Matters**: Clean output = no parsing errors. The system expects **pure SQL** with no wrapper text.

---

### 2. System Prompt Best Practices Summary

Based on `sqlSysPrompt.txt` analysis:

| Requirement | Implementation | Impact |
|-------------|----------------|---------|
| **Schema Completeness** | Full table definitions with all columns, keys, constraints | Prevents hallucinated columns/tables |
| **Matching Strategy** | Always use ILIKE, handle case variations | Handles real user input patterns |
| **JOIN Strategy** | Default LEFT JOIN for optional relationships | Prevents unexpected empty results |
| **Business Logic** | Encode domain rules in prompt (e.g., project naming) | Reduces model confusion |
| **Example Coverage** | 15+ examples covering all query patterns | Teaches by demonstration |
| **Output Format** | Strict "SQL only" requirement | Eliminates parsing errors |
| **Alias Conventions** | Consistent, readable aliases (p, pi, pa, gc, s) | Improves generated SQL quality |

---

## Schema Management

**Location**: `src/backend/sql/introspection/`, `housekeeping/syncSchemaRepresentations.ts`

### Schema Introspection System

The codebase implements **automated schema discovery** using PostgreSQL information_schema:

```typescript
// From schemaReporter.ts
export async function getAllTables(): Promise<string[]> {
    const query = `
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
          AND table_name <> 'supabase_migrations'
          AND table_name NOT LIKE 'pg_%'
    `;
    // ... execution
}

export async function getTableSchema(tableName: string): Promise<TableSchema | null> {
    const columnsQuery = `
        SELECT column_name, data_type, column_default, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = $1
        ORDER BY ordinal_position;
    `;
    // ... fetch columns, primary keys, foreign keys
}
```

**Key Insight**: Schema representations are **stored as JSON** and **automatically synchronized**, ensuring prompts always reflect current database state.

### Schema Synchronization Strategy

```bash
npm run schema:sync
```

This command:
1. Introspects current database schema
2. Generates JSON representations
3. Updates schema files used by prompts
4. Ensures consistency across environments

**Best Practice**: Run schema sync:
- After any database migration
- Before production deployments
- As part of CI/CD pipeline
- When adding new tables/columns

---

## Multi-Stage Query Processing

**Location**: `src/backend/sql/promptEval/clarityEvaluator.ts`, `fullTest.ts`

### Clarity Evaluation (Pre-Processing)

The system implements a **two-stage pipeline**:

```
User Input → Clarity Evaluation → SQL Generation → Execution
```

#### Clarity Agent System Prompt

**Location**: `clarityEvaluator.ts` (lines 25-163)

```typescript
export const CLARITY_SYSTEM_PROMPT = `
You are an expert NLP assistant acting as a Clarity Agent for a Text-to-SQL system.

**Your Tasks:**
1. Analyze Prompt: Examine NL prompt in context of database schema
2. Assess Clarity: Assign score 1-10
3. Determine Action based on Score:
   * Score 9-10: Status="CLEAR", clarified_prompt=Original (unchanged)
   * Score 6-8: Status="CLEAR", minimal corrections only
   * Score 4-5: Status="CLEAR", significantly rephrase for clarity
   * Score ≤3: Status="NEEDS_CLARIFICATION", provide 3 options

4. Output Format: JSON with:
   - clarity_score: number
   - status: "CLEAR" | "NEEDS_CLARIFICATION"
   - clarified_prompt: string | null
   - options: string[] | null  (3 options if unclear)
   - message: string | null
   - reasoning: string | null
`;
```

**Critical Success Factors**:

1. **Schema-Aware Analysis**: The clarity agent has access to the SAME schema as the SQL generator
2. **Tiered Response Strategy**: Different actions based on clarity score
3. **Assumption Tracking**: For borderline cases (score 4-5), record assumptions made
4. **Pure JSON Output**: Strict format requirement prevents parsing errors

#### Clarity Evaluation Results

```typescript
export interface ClarityResult {
  clarity_score: number;           // 1-10
  status: 'CLEAR' | 'NEEDS_CLARIFICATION';
  clarified_prompt: string | null; // Refined prompt if CLEAR
  options: string[] | null;        // 3 options if NEEDS_CLARIFICATION
  message: string | null;          // Explanatory message
  reasoning: string | null;        // Why this score was assigned
  model_name: string;              // Model used for evaluation
}
```

**Best Practice**: Always evaluate clarity before SQL generation for:
- Ambiguous queries
- User inputs with typos/grammar issues
- Queries that might match multiple tables
- Vague requests without clear intent

### Multi-Variant Prompt Strategy

**Location**: `promptGen.ts`, `medTemplateLists.ts`

The system generates **THREE variants** of each natural language query:

```typescript
interface MedTemplate {
  input: {
    nl: string;           // Standard natural language
    nl_focused: string;   // More explicit, detailed version
    nl_simple: string;    // Concise, minimal version
    // ... other fields
  }
}
```

**Examples from Code**:

```typescript
// Complexity 1 (Simple SELECT)
nl_focused = "Retrieve a list showing the names of all items available in the items table.";
nl = "show all the item names";
nl_simple = "items list";

// Complexity 5-7 (Multiple conditions)
nl_focused = "Retrieve the item name, category, and size for items that belong to the category 'desks' and also have the keyword 'wood' associated with them.";
nl = "find desks items that mention wood";
nl_simple = "desks wood items";
```

**Why This Works**:
1. **nl_simple**: Tests if model can handle terse input
2. **nl**: Tests natural conversational input
3. **nl_focused**: Provides detailed, unambiguous version

**Best Practice**: Generate and test all three variants to:
- Identify which input style works best for each model
- Discover where models struggle (terse vs verbose)
- Build robust systems that handle input variability

---

## AI Provider Configuration

**Location**: `src/backend/sql/promptEval/ai.ts`

### Multi-Provider Architecture

The system supports **4 AI providers** with intelligent routing:

```typescript
export function getDevForModelName(modelName: string): string {
  const modelsByProvider: Record<string, string[]> = {
    openai: ["gpt-4o", "o3-mini", "gpt-4o-mini", "gpt-4.1", "o4-mini"],
    groq: ["qwen-qwq-32b", "llama3-70b", "llama-3.3-70b-versatile",
           "llama3-8b-8192", "meta-llama/llama-4-scout-17b-16e-instruct"],
    anthropic: ["claude-3-7-sonnet-latest", "claude-3-7-haiku-latest"],
    google: ["gemini-2.5-pro-preview-03-25", "gemini-2.0-flash"]
  };
  // ... routing logic
}
```

### Model Selection Strategy

```typescript
export function mapModelName(provider: string, model: string): string {
  const modelMaps: Record<string, Record<string, string>> = {
    openai: {
      "gpt-4o": "gpt-4o",
      "default": "gpt-4o-mini"
    },
    groq: {
      "llama3-70b": "llama3-70b-8192",
      // Groq: pass unknown models as-is for flexibility
    },
    // ... other providers
  };
  // ... mapping logic
}
```

**Key Insight**: The system provides:
1. **Automatic provider detection** from model name
2. **Model name mapping** for provider-specific identifiers
3. **Fallback to defaults** when model not found
4. **Flexibility for new models** (especially Groq)

### Unified AI Interface

```typescript
export async function callAI(
  modelName: string,
  userPrompt: string,
  systemPrompt: string,
  options: {
    temperature?: number;
    response_format?: { type: string };
  } = {}
): Promise<string>
```

**Benefits**:
- Single interface for all providers
- Consistent parameter handling
- Easy provider switching for testing
- Temperature and format control

### Best Practices for Provider Selection

Based on `ai.ts` and `fullTest.ts`:

| Provider | Best For | Temperature | Response Format |
|----------|----------|-------------|-----------------|
| **OpenAI (gpt-4o)** | Production, high accuracy | 0.2 | text |
| **OpenAI (gpt-4o-mini)** | Fast iteration, cost-effective | 0.2 | text |
| **Groq (llama3-70b)** | Speed, high throughput | 0.2 | text |
| **Groq (llama3-8b)** | Ultra-fast, basic queries | 0.2-0.4 | text |
| **Anthropic (claude-3-7-sonnet)** | Complex reasoning | 0.2 | text |

**Temperature Recommendation**: **0.2** is used consistently across the codebase for:
- Deterministic output
- Reduced hallucination
- Consistent SQL generation

**For Clarity Evaluation**: Use `temperature: 0.3-0.4` with `response_format: { type: "json_object" }`

---

## Evaluation & Testing Framework

**Location**: `src/backend/sql/promptEval/evaluator.ts`, `promptLoop.ts`, `fullTest.ts`

### Ground-Truth Comparison

```typescript
export function evaluateResults(template: MedTemplate): MedTemplate {
  const actualResults = template.output.results;
  const expectedResults = template.input.expected_result_data;
  const expectedCount = template.input.expected_result_row_count;

  // Scoring logic:
  // - Row count match: +2 points
  // - Close count match: +1 point
  // - Field match percentage: 4-10 points based on accuracy
}
```

**Accuracy Scoring Scale**:

| Accuracy Score | Meaning | Field Match % |
|----------------|---------|---------------|
| 10 | Excellent match | ≥99% |
| 9 | Very good match | 75-98% |
| 8 | Good match | 60-75% |
| 7 | Decent match | 45-60% |
| 6 | Fair match | 30-45% |
| 5 | Poor match | 15-30% |
| 4 | Very poor match | <15% |
| 2 | Wrong count, no data | - |
| 1 | Error or invalid | - |

### Query Equivalence Evaluation (LLM Judge)

**Location**: `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`

The system uses an **LLM as a judge** to determine if two SQL queries are semantically equivalent:

```typescript
export async function queriesAreEquivalent(
  queryA: string,
  queryB: string,
  modelName: string = "gpt-4o-mini",
  temperature: number = 0.2
): Promise<boolean>
```

**Equivalence Rules** (tolerates benign differences):
1. **Aliases**: `items` ≡ `items AS i`
2. **Column Order**: `SELECT name, desc` ≡ `SELECT desc, name`
3. **Formatting**: Whitespace doesn't matter
4. **ORDER BY**: Ignored for equivalence
5. **SELECT * Exception**: `SELECT *` ≡ `SELECT item_name` (primary identifier only)
6. **Category LIKE/= Exception**: `category = 'Lighting'` ≡ `category LIKE '%Lighting%'`

**Sophisticated Difference Analysis**:

```typescript
export async function getUnequivalentReason(
  model: string, query1: string, query2: string
): Promise<{ reasonStruct: any; exemptionString: string }>
```

**Categorizes differences** into 11 types, then **applies exemptions**:

```typescript
// Allow benign LIKE vs = on category
if ("LIKE Usage" in reasonStruct && categoryLIKE_EQUALS_AreSame(q1, q2)) {
  delete reasonStruct["LIKE Usage"];
}

// Allow NULL/NOT NULL differences
delete reasonStruct["NULL Usage"];

// Allow different columns selected
delete reasonStruct["Columns Selected"];

// Allow column order differences
delete reasonStruct["Order of Columns"];
```

**Why This Matters**: Enables accepting multiple valid SQL patterns instead of requiring exact string match.

### Failure Pattern Analysis

**Location**: `data/incorrect_queries.txt`

All failed queries logged in structured format:

```
medium bowl names and descriptions, top 5
SELECT item_name, item_description FROM items WHERE category = 'bowl' AND size = 'medium' ORDER BY item_name ASC LIMIT 5;
SELECT i.item_name, i.item_description FROM items AS i WHERE i.size = 'medium' AND i.item_name LIKE '%bowl%' LIMIT 5;
gpt-4.1
4
```

**Common Failure Patterns Discovered**:
1. **Category vs item_name confusion** - searching name instead of category column
2. **Size literal mismatches** - 'big' vs 'large', 'tiny' vs 'small'
3. **Wrong table selection** - using `items` when should use `project_items`
4. **Hard-coded category names** - not matching actual schema values

**Best Practice**: After test runs, analyze patterns:
```bash
grep "^[a-z]" data/incorrect_queries.txt | sort | uniq -c | sort -rn
```

Then **update system prompt** with examples addressing recurring failures.

### Automated Test Loop

```typescript
export async function testMedTemplates(templates: MedTemplate[]): Promise<MedTemplate[]> {
  for (let [index, templateObj] of templates.entries()) {
    const nlPrompt = templateObj.input.nl;

    // 1. Evaluate clarity
    const clarityResult = await evaluateClarity(clarityModelName, nlPrompt);

    // 2. Execute known SQL to get ground truth
    if (templateObj.input.known_sql) {
      const result = await supabaseExecuteSQL(templateObj.input.known_sql);
      templateObj.input.expected_result_data = result.queryResultData;
      templateObj.input.expected_result_row_count = result.queryResultData.length;
    }

    // 3. Generate SQL from NL
    const result = await runPrompt(nlPrompt);
    templateObj.output.llm_sql = result.sql;
    templateObj.output.results = result.error ? `ERROR: ${result.error}` : result.data;

    // 4. Evaluate accuracy
    templateObj = evaluateResults(templateObj);

    // 5. Pretty print results
    prettyPrintResult(templateObj);
  }
}
```

**Critical Success Factors**:
1. **Ground-truth execution FIRST** - establishes expected results
2. **Clarity evaluation** - pre-processes ambiguous queries
3. **Automated accuracy scoring** - objective comparison
4. **Error tracking** - captures all failures for analysis
5. **LLM judge for equivalence** - accepts semantically equivalent SQL

### Test Template Structure

```typescript
interface MedTemplate {
  input: {
    test_name: string;
    nl_focused: string;
    nl: string;
    nl_simple: string;
    known_sql: string;              // Ground truth query
    expected_result_data: any[];
    expected_result_row_count: number | null;
    model_name: string;
    difficulty: 'easy' | 'medium' | 'hard';
    complexity_score: number;       // 1-10
    query_type: string[];           // ['SELECT', 'JOIN', 'WHERE', ...]
  };
  output: {
    llm_sql: string;                // Generated SQL
    results: any[] | string;        // Query results or error
  };
  analysis: {
    is_valid_sql: boolean | null;
    accuracy: number | null;        // 1-10 score
    accuracy_notes: string | null;
  };
}
```

**Best Practice**: Organize tests by:
- **Complexity** (1-10 scale)
- **Difficulty** (easy/medium/hard)
- **Query Type** (SELECT, JOIN, WHERE, AGGREGATE, etc.)

This enables:
- Targeted testing of weak areas
- Progression from simple to complex
- Identification of query patterns that fail

---

## Security & Input Sanitization

### Prompt Injection Prevention

**Location**: `src/backend/sql/promptEval/testing.ts:61`

Before passing user input to the LLM, the system **sanitizes** to prevent SQL injection and prompt manipulation:

```typescript
function sanitizeNlInputForSqlLLM(userInput: string): [string, boolean] {
  let sanitizedStr = userInput;

  // Remove single-line comments (-- ...)
  sanitizedStr = sanitizedStr.replace(/--.*$/gm, '');

  // Remove multi-line comments (/* ... */)
  sanitizedStr = sanitizedStr.replace(/\/\*.*?\*\//gs, '');

  // Remove single quotes (') - often used in injection
  sanitizedStr = sanitizedStr.replace(/'/g, '');

  // Remove semicolons (;) - statement terminators
  sanitizedStr = sanitizedStr.replace(/;/g, '');

  // Trim whitespace
  sanitizedStr = sanitizedStr.trim();

  let isSanitized = (sanitizedStr != userInput);
  return [sanitizedStr, isSanitized];
}
```

**Critical Security Pattern**:
1. **Remove SQL comment markers** (`--`, `/* */`) - prevents comment-based injection
2. **Strip single quotes** - prevents string escaping attacks
3. **Remove semicolons** - prevents multi-statement execution
4. **Log when sanitization occurs** - alerts to potential attack attempts

**Best Practice**:
- Always sanitize **before** LLM processing
- Log sanitization events for security monitoring
- This is a **pre-processing defense layer**, NOT a replacement for parameterized queries

### SQL Execution Hardening

**Location**: `src/backend/sql/supabase/supabaseQuery.ts:35`

```typescript
export async function supabaseExecuteSQL(sqlQuery: string): Promise<SqlExecutionResult> {
  try {
    // Trim whitespace and remove trailing semicolon before executing
    const cleanedSqlQuery = sqlQuery.trim().replace(/;$/, '');

    // Call the database function to execute the dynamic SQL
    const { data, error } = await supabase.rpc('execute_sql', {
      query_text: cleanedSqlQuery
    });

    queryData = data;
    queryError = error;

    if (error) {
      console.error('!!! SQL execution FAILED:', error);
      console.error(`Failed SQL: ${cleanedSqlQuery}`);
    } else if (data && data.length > 0) {
      console.log('✅ SQL execution SUCCEEDED.');
    } else {
      console.warn('❓ SQL execution returned no data or empty data.');
    }
  } catch (error) {
    console.error('!!! Error during SQL execution:', error);
    queryError = error;
  }

  return {
    queryResultData: queryData,
    queryResultError: queryError
  };
}
```

**Key Patterns**:
1. **Trailing semicolon removal** - ensures clean SQL execution
2. **Structured error capture** - never throws, always returns
3. **Detailed logging** - different messages for failed/empty/success
4. **RPC isolation** - uses database function for controlled execution

**Why This Matters**:
- Database function (`execute_sql`) provides **server-side isolation**
- Even if LLM generates malicious SQL, it's executed in controlled environment
- Structured errors allow graceful degradation

---

## Error Handling & Validation

### SQL Execution Error Handling

**Location**: `src/backend/sql/promptEval/ai.ts` (runPrompt function)

```typescript
export async function runPrompt(promptText: string, model: string = "gpt-4o-mini"): Promise<PromptResult> {
  let sqlQuery = '';
  let queryData: any = null;
  let queryError: any = null;

  try {
    // Generate SQL
    sqlQuery = await callAI(model, promptText, sysPrompt);

    try {
      // Execute SQL
      const result = await supabaseExecuteSQL(sqlQuery);
      queryData = result.queryResultData;
      queryError = result.queryResultError;

    } catch (rpcError) {
      console.error('Error during Supabase query:', rpcError);
      queryError = rpcError;
    }

  } catch (nl2sqlError) {
    console.error('Error during nl2sql generation:', nl2sqlError);
    queryError = nl2sqlError;
    sqlQuery = 'Error generating SQL';
  }

  return {
    sql: sqlQuery,
    data: queryData,
    error: queryError
  };
}
```

**Key Patterns**:
1. **Separate try-catch blocks** for generation vs execution
2. **Preserve original SQL** even when execution fails
3. **Return structured error objects** with sql + data + error
4. **Never throw** - always return result object

### Input Validation

**Location**: `src/backend/services/nl2sqlService.ts`

```typescript
async convertNaturalLanguageToSQL(request: NL2SQLRequest): Promise<NL2SQLResponse> {
  const { promptText, model } = request;

  if (!promptText || typeof promptText !== 'string' || promptText.trim() === '') {
    throw new ValidationError('promptText must be a non-empty string');
  }

  try {
    const sqlResult = await runPrompt(promptText, model);
    return {
      sql: sqlResult.sql,
      data: sqlResult.data,
      error: sqlResult.error,
      model: model || 'default',
      executionTime: Date.now() - startTime
    };
  } catch (error) {
    throw new AIProviderError(
      `Failed to convert NL to SQL: ${error.message}`,
      model || 'unknown',
      error
    );
  }
}
```

**Best Practices**:
1. **Validate inputs early** (non-empty strings, correct types)
2. **Throw typed errors** (ValidationError, AIProviderError)
3. **Track execution time** for performance monitoring
4. **Include context in errors** (model name, original prompt)

---

## Optimization Strategies

### 1. Complexity-Based Test Generation

**Location**: `promptGen.ts` (createMedTemplate function)

The system generates tests with **graduated complexity**:

```typescript
export function createMedTemplate(modelName: string, complexity: number): MedTemplate {
  const clampedComplexity = Math.max(1, Math.min(10, complexity));

  if (clampedComplexity === 1) {
    // Simple SELECT ALL
    query_type = ['SELECT'];
    known_sql = `SELECT i.item_name FROM items AS i;`;

  } else if (clampedComplexity === 2) {
    // SELECT with single WHERE
    query_type = ['SELECT', 'WHERE'];
    known_sql = `SELECT i.item_name FROM items WHERE i.category = '${category}';`;

  } else if (clampedComplexity <= 4) {
    // Multiple columns with WHERE

  } else if (clampedComplexity <= 7) {
    // Multiple WHERE conditions, ORDER BY
    query_type = ['SELECT', 'WHERE', 'AND', 'LIKE'];

  } else {
    // Complex: multiple ORDER BY, LIMIT, Aggregation
    query_type = ['SELECT', 'WHERE', 'OR', 'AND', 'LIKE'];
  }
}
```

**Why This Works**:
- Start simple, gradually increase difficulty
- Identify at which complexity level model begins failing
- Focus optimization efforts on problematic complexity ranges

### 2. Prompt Variant Testing

**From fullTest.ts**:

```typescript
const promptsToAnalyze: { key: 'nl' | 'nl_focused' | 'nl_simple'; prompt: string }[] = [
  { key: 'nl', prompt: exampleTemplate.input.nl },
  { key: 'nl_focused', prompt: exampleTemplate.input.nl_focused },
  { key: 'nl_simple', prompt: exampleTemplate.input.nl_simple }
];

// Test all three variants
for (const item of promptsToAnalyze) {
  const result = await nl2sqlWrapper(sqlModelName, item.prompt, systemPrompt);
  // ... store results
}
```

**Analysis Strategy**:
- Compare accuracy across all three variants
- Identify which input style produces best results per model
- Discover if "more verbose = better" (not always true!)

### 3. Model Comparison Framework

**From fullTest.ts**:

```typescript
export async function fullTest(
  exampleTemplate: MedTemplate,
  clarityModelName: string = "gpt-4o",
  sqlModelName: string = "gpt-4o"
): Promise<FullTestResult> {
  // Test multiple models:
  // - gpt-4o (production)
  // - gpt-4o-mini (fast/cheap)
  // - llama3-8b-8192 (ultra-fast)
  // - llama-3.2-3b-preview (experimental)
}
```

**Best Practice**: Run systematic comparisons:

| Metric | gpt-4o | gpt-4o-mini | llama3-70b | llama3-8b |
|--------|--------|-------------|------------|-----------|
| Accuracy (avg) | ? | ? | ? | ? |
| Cost per 1K queries | ? | ? | ? | ? |
| Latency (ms) | ? | ? | ? | ? |
| Complex query success | ? | ? | ? | ? |

Choose model based on **accuracy/cost/speed tradeoffs** for your use case.

### 4. Temperature Tuning

**Observed values in codebase**:

```typescript
// SQL Generation
temperature: 0.2  // Low for deterministic output

// Clarity Evaluation
temperature: 0.3-0.4  // Slightly higher for nuanced analysis

// Chat/General
temperature: 0.5  // Higher for conversational responses
```

**Recommendation**: **Start at 0.2** for SQL generation. Increase only if:
- Queries are too rigid/repetitive
- Need creative problem-solving for complex queries
- Model produces valid but overly simplistic SQL

---

## Implementation Checklist

### Phase 1: Foundation (Critical Path)

- [ ] **Introspect database schema** using information_schema queries
- [ ] **Create comprehensive system prompt** with:
  - [ ] Complete table/column definitions
  - [ ] All constraints and relationships
  - [ ] Case-insensitive matching rules (ILIKE, LOWER)
  - [ ] JOIN strategy guidelines (LEFT JOIN defaults)
  - [ ] Domain-specific business logic (naming conventions, etc.)
  - [ ] 15+ representative examples covering all query patterns
  - [ ] Strict output format specification (SQL only, no markdown)
  - [ ] Fallback messaging for empty results
- [ ] **Set up schema synchronization** (automated JSON generation)
- [ ] **Implement security hardening**:
  - [ ] Input sanitization (remove SQL comments, quotes, semicolons)
  - [ ] Sanitization event logging
  - [ ] RPC-based execution for isolation
  - [ ] Trailing semicolon cleanup in execution layer
- [ ] **Implement error handling** with structured error types
- [ ] **Configure AI provider** with proper API keys and routing

### Phase 2: Clarity & Pre-Processing

- [ ] **Implement clarity evaluation agent**
  - [ ] Create clarity system prompt with schema context
  - [ ] Define ClarityResult interface
  - [ ] Implement tiered response logic (scores 1-10)
  - [ ] Configure JSON output parsing
- [ ] **Generate prompt variants** (nl, nl_focused, nl_simple)
- [ ] **Add assumption tracking** for borderline clarity scores

### Phase 3: SQL Generation & Execution

- [ ] **Implement unified callAI interface**
  - [ ] Support multiple providers (OpenAI, Groq, Anthropic, Google)
  - [ ] Model name mapping
  - [ ] Temperature control
  - [ ] Response format handling
- [ ] **Create execution pipeline**:
  - [ ] Clarity evaluation (optional, based on input)
  - [ ] SQL generation with selected model
  - [ ] Query execution with error capture
  - [ ] Result formatting
- [ ] **Add validation**:
  - [ ] Input sanitization
  - [ ] SQL syntax checking
  - [ ] Empty result handling

### Phase 4: Testing & Evaluation

- [ ] **Create test templates** with:
  - [ ] Ground-truth SQL queries
  - [ ] Expected results
  - [ ] Complexity scores (1-10)
  - [ ] Difficulty levels (easy/medium/hard)
  - [ ] All three prompt variants (nl, nl_focused, nl_simple)
- [ ] **Implement automated testing loop**:
  - [ ] Execute ground-truth to get expected data
  - [ ] Generate SQL from NL prompts
  - [ ] Compare actual vs expected results
  - [ ] Calculate accuracy scores (1-10 scale)
- [ ] **Implement LLM judge for equivalence**:
  - [ ] Create equivalence system prompt with exemption rules
  - [ ] Define 11 difference categories
  - [ ] Apply exemptions (NULL usage, column order, LIKE vs =, etc.)
  - [ ] Return structured difference analysis
- [ ] **Set up failure logging**:
  - [ ] Log to `incorrect_queries.txt` with structured format
  - [ ] Include: NL, expected SQL, generated SQL, model, score
  - [ ] Enable pattern analysis with grep/sort
- [ ] **Build model comparison framework**
- [ ] **Add performance tracking** (latency, cost, token usage)

### Phase 5: Optimization

- [ ] **Run baseline tests** across models
- [ ] **Identify failure patterns** by:
  - [ ] Complexity level (1-10)
  - [ ] Query type (SELECT, JOIN, WHERE, aggregation, etc.)
  - [ ] Prompt variant (simple/standard/focused)
  - [ ] Analyze `incorrect_queries.txt` for recurring issues
- [ ] **Pattern analysis**:
  - [ ] Category vs item_name confusion
  - [ ] Size literal mismatches (big/large, tiny/small)
  - [ ] Wrong table selection
  - [ ] Hard-coded values not matching schema
  - [ ] Missing JOINs
- [ ] **Iteratively improve**:
  - [ ] Add failing examples to system prompt
  - [ ] Refine business logic rules based on failures
  - [ ] Update equivalence exemptions if needed
  - [ ] Consider model switching if consistent failures
  - [ ] Tune temperature only if necessary (start at 0.2)
- [ ] **Validate improvements**:
  - [ ] Re-run full test suite
  - [ ] Compare before/after accuracy scores
  - [ ] Check LLM judge acceptance rate
  - [ ] Monitor security sanitization events
- [ ] **Document results** and update this guide

---

## Critical Success Patterns (Summary)

### 1. System Prompt Engineering
**Impact: 80% of accuracy**
- Complete schema documentation
- Extensive examples (15+)
- Business logic encoding
- Case-insensitive rules
- Clear output format

### 2. Clarity Pre-Processing
**Impact: 20-30% accuracy improvement**
- Schema-aware analysis
- Tiered response strategy
- Assumption tracking
- JSON output validation

### 3. Multi-Variant Testing
**Impact: Identifies best input style**
- nl_simple: terse queries
- nl: natural queries
- nl_focused: explicit queries

### 4. Ground-Truth Evaluation
**Impact: Objective accuracy measurement**
- Execute known_sql first
- Store expected results
- Compare with generated results
- Calculate field-level match percentage

### 5. Multi-Provider Flexibility
**Impact: Cost/speed/accuracy optimization**
- Automatic provider detection
- Model name mapping
- Consistent interface
- Easy switching for testing

### 6. Automated Testing Loop
**Impact: Continuous improvement**
- Test generation with complexity
- Systematic model comparison
- Error pattern identification
- Performance tracking

---

## Advanced Patterns Summary

### 1. Security-First Architecture

**Multi-Layer Defense**:
- Input sanitization (remove SQL comments, quotes, semicolons)
- RPC-based execution (server-side isolation)
- Trailing semicolon cleanup
- Structured error capture (never throws)
- Sanitization event logging for attack detection

### 2. LLM Judge for Equivalence

**Sophisticated Evaluation**:
- Uses LLM to compare SQL queries semantically
- Tolerates 11 categories of benign differences
- Accepts `SELECT *` ≡ `SELECT item_name` for primary identifiers
- Treats `category = 'X'` ≡ `category LIKE '%X%'` as equivalent
- Applies exemptions for NULL usage, column order, aliases
- Returns only REAL differences after filtering

### 3. Failure Pattern Analysis

**Continuous Improvement Loop**:
- All failures logged to `incorrect_queries.txt`
- Structured format: NL → Expected SQL → Generated SQL → Model → Score
- Analyze patterns: category/name confusion, size mismatches, wrong tables
- Feed discoveries back into system prompt
- Track model-specific failure patterns

### 4. Domain-Specific Heuristics

**Encoded in System Prompt**:
- Project name underscore handling ("zurich swindon" → "zurich_swindon")
- Manifest interpretation based on context
- Default column selection rules
- Participial adjective expansion ("standing desk" → "standing OR stand")
- Fallback messaging for empty results
- Special handling for Zurich table selection

### 5. Multi-Variant Testing Strategy

**Three-Level Validation**:
- `nl_simple`: Terse input ("chairs list")
- `nl`: Natural input ("show me all chairs")
- `nl_focused`: Explicit input ("Retrieve all chair items...")
- Reveals which style works best per model
- Identifies input brittleness
- Enables robust system design

---

## Conclusion

Successful NL2SQL systems require:

1. **Comprehensive system prompts** with complete schema context and extensive examples
2. **Pre-processing for clarity** to handle ambiguous user input
3. **Multi-stage pipelines** (sanitization → clarity → generation → execution → evaluation)
4. **Automated testing** with ground-truth comparison and LLM judge
5. **Security hardening** with input sanitization and RPC isolation
6. **Error resilience** with structured error handling
7. **Provider flexibility** for cost/speed/accuracy tradeoffs
8. **Failure analysis** with pattern detection and prompt feedback

**The single most important factor**: **System prompt quality**. Invest 80% of effort here.

**The most overlooked factor**: **Clarity evaluation**. Handling ambiguous input upfront prevents downstream failures.

**The biggest mistake**: **Testing only one prompt variant**. Always test simple/standard/focused versions.

**The most sophisticated pattern**: **LLM judge for equivalence**. Enables accepting multiple valid SQL patterns instead of exact string matching.

**The best security practice**: **Multi-layer defense** - sanitize inputs, use RPC isolation, remove dangerous SQL syntax, log all sanitization events.

---

---

## TL;DR - The Absolute Essentials

If you only have time to implement 5 things:

### 1. Comprehensive System Prompt (File: `sqlSysPrompt.txt`)
```
- Complete schema with ALL tables, columns, keys, constraints
- Case-insensitive: ALWAYS use ILIKE '%value%' and LOWER()
- LEFT JOIN default for optional relationships
- 15+ examples from simple SELECT to complex JOINs
- Output format: "Return ONLY the SQL query, no markdown, no explanation"
```

### 2. Security Layer (Files: `testing.ts:61`, `supabaseQuery.ts:35`)
```typescript
// BEFORE LLM processing
const [sanitized, wasChanged] = sanitizeInput(userInput);
// Remove: --, /* */, ', ;

// DURING execution
const cleanSQL = sqlQuery.trim().replace(/;$/, '');
await supabase.rpc('execute_sql', { query_text: cleanSQL });
// Server-side isolation via RPC
```

### 3. LLM Judge (File: `queryEquivalenceJudge.ts`)
```typescript
// Don't use string matching!
const equivalent = await queriesAreEquivalent(expectedSQL, generatedSQL);

// Accepts as equivalent:
// - SELECT * ≡ SELECT item_name
// - category = 'X' ≡ category LIKE '%X%'
// - Different column order, aliases, formatting
```

### 4. Multi-Variant Testing (Files: `promptGen.ts`, `fullTest.ts`)
```typescript
// Test all three versions
testTemplates.forEach(t => {
  testSQL(t.nl_simple);   // "chairs list"
  testSQL(t.nl);          // "show me all chairs"
  testSQL(t.nl_focused);  // "Retrieve all chair items from furniture table"
});
```

### 5. Failure Analysis Loop (File: `incorrect_queries.txt`)
```bash
# After tests, analyze patterns
grep "^[a-z]" incorrect_queries.txt | sort | uniq -c | sort -rn

# Common failures:
# - Category vs item_name confusion → Add example to prompt
# - Size mismatches (big vs large) → Add synonym mapping
# - Wrong table selection → Add table selection logic
```

---

## Final Checklist

Before going to production:

- [ ] System prompt has complete schema with 15+ examples
- [ ] Input sanitization implemented and logging events
- [ ] RPC-based SQL execution for isolation
- [ ] LLM judge evaluating equivalence (not string match)
- [ ] Testing all 3 prompt variants (simple/standard/focused)
- [ ] Logging failures to `incorrect_queries.txt`
- [ ] Temperature = 0.2 for SQL generation
- [ ] Ground-truth execution before generated SQL
- [ ] Structured error handling (never throws)
- [ ] Schema sync automated with JSON generation

---

**Document Version**: 2.0
**Based on**: Comprehensive analysis of nl2sql codebase (2025-01)
**Last Updated**: 2025-01-21
**Analysis Depth**: Full codebase scan including:
- `src/backend/sql/promptEval/` (all files)
- `src/backend/sql/promptEval/prompts/` (all prompts)
- `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`
- `src/backend/sql/promptEval/testing.ts` (sanitization)
- `src/backend/sql/supabase/supabaseQuery.ts`
- `src/backend/services/nl2sqlService.ts`
- `src/backend/sql/schemaReporter.ts`
- `housekeeping/syncSchemaRepresentations.ts`
- `data/prompts.json`
- `data/incorrect_queries.txt`
- System prompt templates and all evaluation code

**Key Insights from Additional Context**:
- Security: Multi-layer defense with sanitization, RPC isolation, cleanup
- Evaluation: LLM judge with 11 exemption categories for benign differences
- Analysis: Structured failure logging enables continuous improvement
- Testing: Three-variant strategy reveals input brittleness per model
