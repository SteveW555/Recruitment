# Source Copies - Reference Files for New NL2SQL Projects

This directory contains all the essential reference files from this production NL2SQL system, organized by priority for easy copying to new projects.

---

## 📁 Directory Structure

```
source_copies/
├── CRITICAL/          # Must copy exactly - core security & evaluation
├── IMPORTANT/         # Copy and adapt - templates & infrastructure
├── USEFUL/            # For reference - patterns & examples
├── OPTIONAL/          # Nice to have - advanced features
└── README.md          # This file
```

---

## 🔴 CRITICAL/ - Must Copy Exactly

### 1. `1_sanitization_function.ts`
**Source**: `src/backend/sql/promptEval/testing.ts:61-84`
**Purpose**: Prevents SQL injection and prompt manipulation
**Copy**: Exactly as-is, no modifications needed
**Usage**:
```typescript
import { sanitizeNlInputForSqlLLM } from './1_sanitization_function';

const [cleanInput, wasModified] = sanitizeNlInputForSqlLLM(userQuery);
if (wasModified) {
  console.warn('⚠️ Potential attack attempt detected');
}
```

**Security pattern**: Removes SQL comments (`--`, `/* */`), quotes, semicolons
**Time to integrate**: 5 minutes

---

### 2. `2_sql_execution_hardening.ts`
**Source**: `src/backend/sql/supabase/supabaseQuery.ts`
**Purpose**: Secure SQL execution with proper error handling
**Copy**: Pattern only, adapt to your database client
**Key patterns**:
- Trim whitespace and remove trailing semicolons
- Execute via RPC/stored procedure (NOT direct queries)
- Structured error handling (never throws)
- Detailed logging for debugging

**Modifications needed**:
```typescript
// Replace this:
const { data, error } = await supabase.rpc('execute_sql', {
  query_text: cleanedSqlQuery
});

// With your DB client:
const result = await yourDbClient.query(cleanedSqlQuery);
// OR for MySQL:
const [rows] = await connection.query(cleanedSqlQuery);
```

**Time to integrate**: 15 minutes

---

### 3. `3_llm_judge_equivalence.ts`
**Source**: `src/backend/sql/promptEval/prompts/queryEquivalenceJudge.ts`
**Purpose**: LLM-based semantic SQL equivalence checking
**Copy**: System prompt + functions
**Why critical**: Enables accepting multiple valid SQL patterns instead of exact string matching

**Key features**:
- Tolerates 11 categories of benign differences
- Accepts `SELECT *` ≡ `SELECT item_name` for simple queries
- Treats `category = 'X'` ≡ `category LIKE '%X%'`
- Applies exemptions for NULL usage, column order, aliases

**Usage**:
```typescript
import { queriesAreEquivalent } from './3_llm_judge_equivalence';

const match = await queriesAreEquivalent(expectedSQL, generatedSQL);
if (match) {
  console.log('✅ Queries are equivalent');
}
```

**Time to integrate**: 20 minutes

---

## 🟡 IMPORTANT/ - Copy and Adapt

### 1. `1_system_prompt_template.txt`
**Source**: `src/backend/sql/promptEval/prompts/sqlSysPrompt.txt`
**Purpose**: Template for your NL2SQL system prompt
**Copy**: Structure only - MUST replace content

⚠️ **This is 80% of your success - invest time here!**

**What to keep**:
- Role definition structure
- Case-insensitive matching rules
- JOIN strategy guidelines
- Output format specification

**What to replace**:
- Lines 5-32: Replace with YOUR database schema
- Lines 91-166: Replace ALL examples with YOUR domain
- Lines 59-89: Replace business logic with YOUR rules

**Required work**:
- Extract your complete schema (all tables, columns, keys)
- Write 15+ examples covering YOUR query patterns
- Add YOUR domain-specific business logic
- Test with real queries

**Time to adapt**: 3-4 hours (don't rush this!)

---

### 2. `2_multi_provider_ai_client.ts`
**Source**: `src/backend/sql/promptEval/ai.ts`
**Purpose**: Unified interface for multiple AI providers
**Copy**: Provider detection + unified interface
**Supports**: OpenAI, Groq, Anthropic, Google Gemini

**Key functions**:
- `getDevForModelName()` - Auto-detect provider from model name
- `mapModelName()` - Map friendly names to actual model IDs
- `callAI()` - Unified interface for all providers

**Modifications needed**:
```typescript
// Add/remove providers based on what you'll use
const providers = {
  openai: ['gpt-4o', 'gpt-4o-mini'],
  groq: ['llama3-70b-8192'],
  // Remove providers you won't use
};
```

**Time to integrate**: 30 minutes

---

### 3. `3_clarity_evaluation.ts`
**Source**: `src/backend/sql/promptEval/clarityEvaluator.ts`
**Purpose**: Pre-processes ambiguous user queries
**Copy**: System prompt + evaluation function
**Optional**: Only implement if you expect ambiguous input

**Features**:
- Scores clarity 1-10
- Tiered response strategy (clear/refine/clarify)
- Assumption tracking for borderline cases
- JSON output with structured results

**When to use**:
- User queries are often vague
- Multiple interpretations possible
- Want to improve user experience

**Time to integrate**: 45 minutes

---

## 🟢 USEFUL/ - For Reference

### 1. `1_test_case_format.json`
**Source**: `data/prompts.json`
**Purpose**: Example test case structure
**Use**: Template for YOUR test cases

**Format**:
```json
{
  "nl": "natural language query",
  "known_sql": "expected SQL result",
  "llm_sql": " ",
  "results": " "
}
```

**Replace**: All queries with YOUR domain examples

---

### 2. `2_evaluation_scorer.ts`
**Source**: `src/backend/sql/promptEval/evaluator.ts`
**Purpose**: Accuracy scoring algorithm
**Use**: Field-level result comparison

**Key algorithm**:
- Compare row counts
- Compare field values
- Calculate match percentage
- Assign 1-10 accuracy score

**Time to integrate**: 30 minutes

---

### 3. `3_schema_introspection.ts`
**Source**: `src/backend/sql/schemaReporter.ts`
**Purpose**: Automated database schema extraction
**Use**: Generate schema JSON for system prompt

**Functions**:
- `getAllTables()` - List all tables
- `getTableSchema()` - Extract columns, types, constraints
- `getPrimaryKeys()` - Get primary key columns
- `getForeignKeys()` - Get foreign key relationships

**Modifications needed**:
- Replace Supabase client with your DB client
- Adjust queries for your database type (PostgreSQL vs MySQL vs SQLite)

**Time to integrate**: 45 minutes

---

### 4. `4_failure_log_example.txt`
**Source**: `data/incorrect_queries.txt`
**Purpose**: Example of structured failure logging
**Format**:
```
[Natural Language]
[Expected SQL]
[Generated SQL]
[Model Name]
[Score]

```

**Use**: Pattern for logging YOUR test failures
**Analysis**: `grep "^[a-z]" failures.txt | sort | uniq -c`

---

## 🔵 OPTIONAL/ - Nice to Have

### 1. `1_template_generator.ts`
**Source**: `src/backend/sql/promptEval/prompts/promptGen.ts`
**Purpose**: Generates synthetic test cases with complexity levels
**Use**: Automate test case creation

**Features**:
- Complexity-based generation (1-10 scale)
- Three prompt variants (simple/standard/focused)
- Random data sampling

**Time to adapt**: 2-3 hours (domain-specific)

---

### 2. `2_full_test_runner.ts`
**Source**: `src/backend/sql/promptEval/fullTest.ts`
**Purpose**: Orchestrates complete test execution
**Use**: Pattern for test automation

**Features**:
- Multi-variant testing (nl_simple, nl, nl_focused)
- Clarity evaluation integration
- Result aggregation
- Error collection

**Time to adapt**: 1-2 hours

---

### 3. `3_system_prompts_functions.ts`
**Source**: `src/backend/sql/promptEval/sysPrompts.ts`
**Purpose**: Helper functions for loading system prompts
**Use**: Pattern for prompt management

---

## 🚀 Quick Start Guide

### For Minimum Viable Product (4-6 hours)

**Copy only**:
1. ✅ `CRITICAL/1_sanitization_function.ts` (5 min)
2. ✅ `CRITICAL/2_sql_execution_hardening.ts` (15 min adapt)
3. ✅ `IMPORTANT/1_system_prompt_template.txt` (3-4 hours adapt)
4. ✅ `IMPORTANT/2_multi_provider_ai_client.ts` (30 min)

**Skip**: LLM judge, clarity evaluation, automated testing (add later)

**Result**: Working NL2SQL with basic security in 4-6 hours

---

### For Production-Ready System (2-3 days)

**Add to MVP**:
5. ✅ `CRITICAL/3_llm_judge_equivalence.ts` (20 min)
6. ✅ `IMPORTANT/3_clarity_evaluation.ts` (45 min)
7. ✅ `USEFUL/1_test_case_format.json` (template)
8. ✅ `USEFUL/2_evaluation_scorer.ts` (30 min)

**Plus**: Write 30+ test cases (4 hours)

**Result**: Production-ready system with 80%+ accuracy

---

## 📋 Integration Checklist

```
CRITICAL FILES (Must implement):
[ ] Sanitization function integrated
[ ] SQL execution hardening implemented
[ ] LLM judge for equivalence working

IMPORTANT FILES (High priority):
[ ] System prompt created with YOUR schema
[ ] 15+ examples written for YOUR domain
[ ] AI client configured with your providers
[ ] Clarity evaluation (optional) integrated

USEFUL FILES (Recommended):
[ ] Test cases created (20+ examples)
[ ] Evaluation scorer implemented
[ ] Schema introspection automated
[ ] Failure logging set up

VALIDATION:
[ ] Security tested with malicious inputs
[ ] Basic queries working (5 test cases)
[ ] LLM judge accepting valid variations
[ ] Failures being logged correctly
```

---

## 💡 Usage Tips

### 1. Start with CRITICAL files
These are non-negotiable for security and proper evaluation.

### 2. Invest time in system prompt
Lines 5-32 (schema) and 91-166 (examples) are 80% of your accuracy.

### 3. Use LLM judge, not string matching
Many valid SQL representations exist for the same query.

### 4. Test with three variants
Every query should have: `nl_simple`, `nl`, `nl_focused` versions.

### 5. Log all failures
Every failed test is a learning opportunity - update your system prompt.

---

## 🔗 Related Documentation

- **IMPLEMENTATION_GUIDE_FOR_NEW_PROJECT.md** - Complete step-by-step guide
- **INSTRUCTIONS_FOR_AI_ASSISTANT.md** - Guide for AI assistants
- **REFERENCE_FILES_MANIFEST.md** - Detailed file descriptions
- **NL2SQL_BEST_PRACTICES.md** - Deep dive into all patterns

---

## ⚠️ Important Notes

### What NOT to copy directly:
- Service layer code (write your own)
- API routes (domain-specific)
- Frontend UI (domain-specific)
- Any code with "wishlist", "organisations", "projects" in names

### What to ALWAYS adapt:
- System prompt schema section
- All SQL examples
- Business logic rules
- Test cases

### Security reminders:
- ALWAYS sanitize input before LLM
- ALWAYS use RPC/stored procedures for execution
- NEVER concatenate user input into SQL strings
- ALWAYS log sanitization events

---

## 📊 Expected Outcomes

### After copying CRITICAL files:
- ✅ Security hardening in place
- ✅ SQL execution isolated
- ✅ Equivalence checking working

### After adapting IMPORTANT files:
- ✅ 60-70% accuracy on simple queries
- ✅ Multi-provider AI working
- ✅ Basic testing operational

### After implementing USEFUL patterns:
- ✅ 80-85% accuracy
- ✅ Automated testing
- ✅ Failure analysis pipeline

### After optimization (1 week):
- ✅ 90%+ accuracy on trained patterns
- ✅ Continuous improvement loop
- ✅ Production monitoring

---

## 🎯 Key Success Factors

1. **System prompt quality** (80% of success)
   - Complete schema documentation
   - 15+ comprehensive examples
   - Domain-specific business logic

2. **Security hardening** (Non-negotiable)
   - Input sanitization
   - RPC-based execution
   - Event logging

3. **LLM judge for evaluation** (Critical for accuracy)
   - Semantic equivalence, not string matching
   - Benign difference exemptions

4. **Failure analysis loop** (Continuous improvement)
   - Log every failure
   - Identify patterns
   - Update system prompt
   - Re-test

---

## 🆘 Troubleshooting

**Problem**: Low accuracy (<60%)
**Solution**:
1. Check system prompt has YOUR complete schema
2. Verify 15+ examples covering all query types
3. Add failing queries as examples to prompt

**Problem**: Security warnings
**Solution**:
1. Ensure sanitization is called BEFORE LLM
2. Verify RPC execution is used
3. Check logs for attack patterns

**Problem**: LLM judge rejecting valid queries
**Solution**:
1. Review exemption rules in `3_llm_judge_equivalence.ts`
2. Add domain-specific exemptions
3. Check if queries are truly equivalent

**Problem**: Slow performance
**Solution**:
1. Use gpt-4o-mini instead of gpt-4o
2. Consider Groq for ultra-fast inference
3. Cache common queries

---

## 📞 Support

If you encounter issues:
1. Consult **IMPLEMENTATION_GUIDE_FOR_NEW_PROJECT.md**
2. Review **NL2SQL_BEST_PRACTICES.md**
3. Check reference files in this directory
4. Analyze failure logs for patterns

---

**Ready to start?**

1. Copy CRITICAL files to your project
2. Adapt system prompt with your schema (3-4 hours)
3. Test with 5 simple queries
4. Iterate based on failures

**Good luck! 🚀**

---

*These reference files represent battle-tested patterns from a production NL2SQL system achieving 90%+ accuracy.*
