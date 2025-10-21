# Reference Files Manifest - What to Copy for New Project

**Quick guide: Which files to copy from this codebase when implementing NL2SQL in a new project**

---

## 🔴 CRITICAL - Must Copy (Copy these exactly)

### 1. Input Sanitization Function
**File**: `src/backend/sql/promptEval/testing.ts`
**Lines**: 61-84
**Copy to**: `your-project/src/security/sanitize.ts`

**Why critical**: Prevents SQL injection and prompt manipulation attacks.

**What to copy**:
```typescript
function sanitizeNlInputForSqlLLM(userInput: string): [string, boolean] {
  // ... full function
}
```

**Modifications needed**: None - copy exactly as-is.

---

### 2. SQL Execution Hardening
**File**: `src/backend/sql/supabase/supabaseQuery.ts`
**Lines**: 35-69
**Copy to**: `your-project/src/database/executeSQL.ts`

**Why critical**: Secure SQL execution with proper error handling.

**What to copy**:
```typescript
export async function supabaseExecuteSQL(sqlQuery: string): Promise<SqlExecutionResult> {
  // ... full function
}
```

**Modifications needed**:
- Replace `supabase.rpc()` with your database client
- Keep all cleanup logic (trim, semicolon removal)
- Keep all logging

---

### 3. LLM Judge for Equivalence
**File**: `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`
**Lines**: 1-172
**Copy to**: `your-project/src/evaluation/queryJudge.ts`

**Why critical**: Enables accepting multiple valid SQL patterns instead of exact string matching.

**What to copy**:
- Full `systemPrompt` (lines 5-107)
- `queriesAreEquivalent()` function (lines 118-172)

**Modifications needed**:
- Lines 22-29: Adjust SELECT * exception rules if needed
- Lines 84-87: Add/remove equivalence exceptions for your domain

---

## 🟡 IMPORTANT - High Priority (Adapt these patterns)

### 4. System Prompt Template
**File**: `src/backend/sql/promptEval/prompts/sqlSysPrompt.txt`
**Lines**: ALL
**Copy to**: `your-project/prompts/systemPrompt.txt`

**Why important**: Template for your system prompt (80% of success).

**What to copy - STRUCTURE ONLY**:
- Lines 1-3: Role definition
- Lines 5-32: Schema section format
- Lines 34-169: All rules and guidelines

**Must replace**:
- Lines 5-32: Replace with YOUR database schema
- Lines 91-166: Replace ALL examples with YOUR domain
- Lines 59-89: Replace business logic with YOUR rules

**Keep exactly**:
- Case-insensitive matching rules (lines 36-40)
- JOIN strategy (lines 42-47)
- Output format specification (line 169)

---

### 5. Multi-Provider AI Client
**File**: `src/backend/sql/promptEval/ai.ts`
**Lines**: 1-150
**Copy to**: `your-project/src/ai/client.ts`

**Why important**: Unified interface for multiple AI providers.

**What to copy**:
- `getDevForModelName()` function (lines 63-90)
- `callAI()` unified interface (lines 150+)
- Provider detection logic

**Modifications needed**:
- Lines 70-75: Add/remove providers you'll use
- Lines 100-150: Implement only providers you need

---

### 6. Clarity Evaluation System Prompt
**File**: `src/backend/sql/promptEval/clarityEvaluator.ts`
**Lines**: 25-163
**Copy to**: `your-project/prompts/clarityPrompt.ts`

**Why important**: Pre-processes ambiguous queries (optional but valuable).

**What to copy**:
- Full `CLARITY_SYSTEM_PROMPT` (lines 25-163)
- `ClarityResult` interface (lines 13-21)
- `evaluateClarity()` function (lines 188-237)

**Modifications needed**:
- Lines 29-81: Replace schema with yours
- Lines 86-89: Add YOUR table identification rules

---

## 🟢 USEFUL - Medium Priority (For reference and patterns)

### 7. Test Case Format
**File**: `data/prompts.json`
**Lines**: ALL
**Copy to**: `your-project/tests/testCases.json`

**Why useful**: Template for test case structure.

**What to copy - FORMAT ONLY**:
```json
{
  "nl": "natural language query",
  "known_sql": "expected SQL",
  "llm_sql": " ",
  "results": " "
}
```

**Must replace**: All queries with YOUR domain examples.

---

### 8. Evaluation Logic
**File**: `src/backend/sql/promptEval/evaluator.ts`
**Lines**: 11-100
**Copy to**: `your-project/src/evaluation/scorer.ts`

**Why useful**: Accuracy scoring algorithm.

**What to copy**:
- `evaluateResults()` function
- Row count comparison logic
- Field-level matching algorithm

**Modifications needed**: Adjust scoring thresholds if needed.

---

### 9. Schema Introspection
**File**: `src/backend/sql/schemaReporter.ts`
**Lines**: 29-241
**Copy to**: `your-project/scripts/introspectSchema.ts`

**Why useful**: Automated schema extraction.

**What to copy**:
- `getAllTables()` (lines 33-67)
- `getTableSchema()` (lines 74-130)
- `getPrimaryKeys()` (lines 137-162)
- `getForeignKeys()` (lines 169-210)

**Modifications needed**:
- Replace Supabase client with your DB client
- Adjust queries for your database type (MySQL vs PostgreSQL)

---

### 10. Difference Analysis with Exemptions
**File**: `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`
**Lines**: 225-400
**Copy to**: `your-project/src/evaluation/differenceAnalyzer.ts`

**Why useful**: Detailed analysis of query differences.

**What to copy**:
- `getUnequivalentReason()` function (lines 225-400)
- Exemption categories (lines 324-391)

**Modifications needed**:
- Lines 324-391: Adjust exemptions for your domain

---

## 🔵 OPTIONAL - Low Priority (Nice to have)

### 11. Test Template Generator
**File**: `src/backend/sql/promptEval/prompts/promptGen.ts`
**Lines**: 126-300
**Copy to**: `your-project/src/testing/templateGenerator.ts`

**Why optional**: Generates synthetic test cases.

**What to copy**:
- `createMedTemplate()` function
- Complexity-based generation logic

**Modifications needed**: Completely rewrite for your domain.

---

### 12. Full Test Runner
**File**: `src/backend/sql/promptEval/fullTest.ts`
**Lines**: 198-374
**Copy to**: `your-project/src/testing/testRunner.ts`

**Why optional**: Orchestrates full test execution.

**What to copy - PATTERN ONLY**:
- Test loop structure
- Result aggregation
- Error collection

**Must adapt**: Everything - this is very specific to this codebase.

---

## 📋 Copy Checklist

```
CRITICAL (Must copy exactly):
[ ] sanitizeNlInputForSqlLLM() from testing.ts:61-84
[ ] SQL execution function from supabaseQuery.ts:35-69
[ ] queriesAreEquivalent() from queryEquivalenceJudge.ts

IMPORTANT (Copy and adapt):
[ ] System prompt STRUCTURE from sqlSysPrompt.txt
[ ] Multi-provider AI client from ai.ts
[ ] Clarity prompt from clarityEvaluator.ts

USEFUL (For reference):
[ ] Test case format from prompts.json
[ ] Evaluation logic from evaluator.ts
[ ] Schema introspection from schemaReporter.ts
[ ] Difference analysis from queryEquivalenceJudge.ts

OPTIONAL (If needed):
[ ] Template generator from promptGen.ts
[ ] Full test runner from fullTest.ts
```

---

## File Size Reference

| File | Lines | Copy Time | Adaptation Time |
|------|-------|-----------|-----------------|
| testing.ts (sanitization) | 24 | 2 min | None - copy exactly |
| supabaseQuery.ts (execution) | 35 | 3 min | 10 min (DB client) |
| queryEquivalenceJudge.ts | 172 | 10 min | 15 min (exemptions) |
| sqlSysPrompt.txt | 170 | 15 min | 2-3 hours (examples) |
| ai.ts | 150 | 10 min | 30 min (providers) |
| clarityEvaluator.ts | 163 | 10 min | 30 min (schema) |

**Total minimum**: ~1 hour copying + 3-4 hours adaptation = **4-5 hours**

---

## How to Use This Manifest

### For Minimum Viable Product (6 hours total)

Copy only:
1. ✅ Sanitization (testing.ts) - 2 min
2. ✅ SQL execution (supabaseQuery.ts) - 13 min
3. ✅ System prompt template (sqlSysPrompt.txt) - 3 hours to adapt
4. ✅ AI client (ai.ts) - 40 min

Skip: LLM judge, clarity evaluation, test automation (add later)

### For Production-Ready System (2-3 days)

Copy all CRITICAL + IMPORTANT:
1. All above
2. ✅ LLM judge (queryEquivalenceJudge.ts) - 25 min
3. ✅ Clarity evaluation (clarityEvaluator.ts) - 40 min
4. ✅ Test format (prompts.json) - 5 min
5. ✅ Evaluation logic (evaluator.ts) - 20 min

Plus: Write 30+ test cases (4 hours)

### For Fully Optimized System (1 week)

Copy everything + build:
1. All above
2. ✅ Schema introspection (schemaReporter.ts) - 30 min
3. ✅ Difference analyzer (queryEquivalenceJudge.ts lines 225-400) - 20 min
4. Build automation scripts
5. Set up continuous improvement loop

---

## Critical File Dependencies

```
sanitize.ts (no dependencies)
  ↓
executeSQL.ts (uses your DB client)
  ↓
ai.ts (uses OpenAI/Groq/etc clients)
  ↓
nl2sql.ts (uses sanitize + ai + execute)
  ↓
queryJudge.ts (uses ai.ts)
  ↓
testRunner.ts (uses nl2sql + queryJudge)
```

**Copy order**: Top to bottom (no forward dependencies).

---

## Example Copy Commands

```bash
# Create directory structure
mkdir -p your-project/src/{security,database,ai,evaluation,prompts}

# Copy critical files
cp nl2sql/src/backend/sql/promptEval/testing.ts \
   your-project/src/security/sanitize.ts

cp nl2sql/src/backend/sql/supabase/supabaseQuery.ts \
   your-project/src/database/execute.ts

cp nl2sql/src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts \
   your-project/src/evaluation/judge.ts

cp nl2sql/src/backend/sql/promptEval/prompts/sqlSysPrompt.txt \
   your-project/src/prompts/system.txt

cp nl2sql/src/backend/sql/promptEval/ai.ts \
   your-project/src/ai/client.ts
```

---

## What NOT to Copy

❌ **Do not copy these** (too specific to this codebase):

- `src/backend/services/nl2sqlService.ts` - Service layer (write your own)
- `src/backend/routes/` - API routes (write your own)
- `data/incorrect_queries.txt` - Failure logs (you'll generate your own)
- `src/frontend/` - Frontend UI (domain-specific)
- `housekeeping/` - Maintenance scripts (domain-specific)
- Any file with "wishlist", "organisations", "projects" in name

---

## Validation After Copying

After copying files, verify:

```bash
# 1. Check sanitization works
node -e "const {sanitize} = require('./src/security/sanitize'); \
  console.log(sanitize('test; DROP TABLE users;--'))"
# Should output: ["test DROP TABLE users", true]

# 2. Check AI client compiles
tsc src/ai/client.ts --noEmit

# 3. Check system prompt exists
cat src/prompts/system.txt | grep "Database Schema"

# 4. Check dependencies installed
npm list openai groq-sdk
```

---

## Next Steps After Copying

1. **Adapt system prompt** (3 hours)
   - Replace schema
   - Write 15+ examples
   - Add business logic

2. **Test security layer** (30 min)
   - Try malicious inputs
   - Verify sanitization logs

3. **Create test cases** (2 hours)
   - Write 10 simple examples
   - Write 10 complex examples

4. **Run first tests** (30 min)
   - Execute test suite
   - Measure baseline accuracy

5. **Iterate** (ongoing)
   - Analyze failures
   - Update prompt
   - Re-test

---

**Ready to start?** Begin with the CRITICAL files (should take 1 hour to copy + adapt).
