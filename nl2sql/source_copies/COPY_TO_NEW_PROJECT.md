# Quick Copy Guide - Transfer to New Project

**Copy this entire `source_copies/` directory to your new project for easy reference.**

---

## ✅ Files Ready to Copy (14 files total)

### 🔴 CRITICAL/ (3 files) - Must implement first
```
1_sanitization_function.ts          ← Security: Input sanitization
2_sql_execution_hardening.ts        ← Security: Safe SQL execution
3_llm_judge_equivalence.ts          ← Evaluation: Semantic SQL matching
```

### 🟡 IMPORTANT/ (3 files) - Adapt for your domain
```
1_system_prompt_template.txt        ← Template: Replace with YOUR schema
2_multi_provider_ai_client.ts       ← Infrastructure: Multi-AI support
3_clarity_evaluation.ts             ← Optional: Query clarification
```

### 🟢 USEFUL/ (4 files) - For reference & patterns
```
1_test_case_format.json             ← Template: Test case structure
2_evaluation_scorer.ts              ← Pattern: Accuracy calculation
3_schema_introspection.ts           ← Utility: Auto schema extraction
4_failure_log_example.txt           ← Example: Failure logging format
```

### 🔵 OPTIONAL/ (3 files) - Advanced features
```
1_template_generator.ts             ← Advanced: Synthetic test generation
2_full_test_runner.ts               ← Advanced: Test orchestration
3_system_prompts_functions.ts      ← Utility: Prompt loading helpers
```

### 📖 Documentation (1 file)
```
README.md                           ← Complete guide (read this first!)
```

---

## 🚀 Copy Commands

### For Linux/Mac:
```bash
# Copy entire directory
cp -r source_copies/ /path/to/your/new-project/nl2sql-reference/

# Or copy selectively (minimum viable)
mkdir -p /path/to/your-project/nl2sql/
cp source_copies/CRITICAL/*.ts /path/to/your-project/nl2sql/
cp source_copies/IMPORTANT/1_system_prompt_template.txt /path/to/your-project/nl2sql/
```

### For Windows:
```cmd
REM Copy entire directory
xcopy source_copies\ C:\path\to\your\new-project\nl2sql-reference\ /E /I

REM Or copy selectively (minimum viable)
mkdir C:\path\to\your-project\nl2sql
copy source_copies\CRITICAL\*.ts C:\path\to\your-project\nl2sql\
copy source_copies\IMPORTANT\1_system_prompt_template.txt C:\path\to\your-project\nl2sql\
```

---

## ⚡ Quick Start (4-6 hours to working system)

### Step 1: Copy CRITICAL files (10 min)
```bash
cp CRITICAL/1_sanitization_function.ts your-project/src/security/
cp CRITICAL/2_sql_execution_hardening.ts your-project/src/database/
cp CRITICAL/3_llm_judge_equivalence.ts your-project/src/evaluation/
```

**Adapt**: Only file #2 needs adaptation (replace Supabase with your DB client)

---

### Step 2: Create your system prompt (3-4 hours) ⚠️ CRITICAL
```bash
cp IMPORTANT/1_system_prompt_template.txt your-project/prompts/system.txt
```

**Edit `system.txt`**:
1. Lines 5-32: Replace schema with YOUR database tables
2. Lines 91-166: Replace ALL examples with YOUR domain queries
3. Lines 59-89: Add YOUR business logic rules

**Don't rush this step - it's 80% of your success!**

---

### Step 3: Set up AI client (30 min)
```bash
cp IMPORTANT/2_multi_provider_ai_client.ts your-project/src/ai/
```

**Install dependencies**:
```bash
npm install openai groq-sdk @anthropic-ai/sdk @google/generative-ai
```

**Configure**:
```bash
# .env file
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

---

### Step 4: Test with 5 queries (30 min)
```bash
cp USEFUL/1_test_case_format.json your-project/tests/cases.json
```

**Edit `cases.json`** with 5 simple queries from YOUR domain.

**Run first test**:
```typescript
import { convertNL2SQL } from './nl2sql';

const result = await convertNL2SQL("show all active users");
console.log(result.sql);
```

---

## 📊 What You'll Have After 4-6 Hours

✅ **Security**: Input sanitization + safe SQL execution
✅ **AI Integration**: Multi-provider support (OpenAI/Groq/Anthropic/Google)
✅ **System Prompt**: Adapted for your database (80% accuracy potential)
✅ **Basic Testing**: 5 test cases with LLM judge
✅ **Working MVP**: Can generate SQL from natural language

**Baseline accuracy**: 60-70% on simple queries

---

## 🎯 Next Steps for Production (add 1-2 days)

### Day 2: Testing & Evaluation
```bash
# Copy evaluation tools
cp USEFUL/2_evaluation_scorer.ts your-project/src/evaluation/

# Create 30+ test cases
# Write tests covering:
# - Simple SELECT (10 tests)
# - WHERE filters (8 tests)
# - JOINs (7 tests)
# - Aggregations (5 tests)
```

**Expected accuracy**: 80-85%

---

### Day 3: Optimization
```bash
# Set up failure logging
cp USEFUL/4_failure_log_example.txt your-project/logs/

# Run tests, analyze failures
cat failures.txt | grep "^[a-z]" | sort | uniq -c

# Update system prompt with failing examples
# Re-test
```

**Expected accuracy**: 90%+

---

## ⚠️ Critical Reminders

### Must Do:
1. ✅ Sanitize ALL user input before LLM
2. ✅ Use RPC/stored procedures for SQL execution
3. ✅ Write 15+ examples in system prompt
4. ✅ Use LLM judge for evaluation (not string matching)
5. ✅ Log all failures for analysis

### Must NOT Do:
1. ❌ Copy domain-specific code (wishlist, organisations, etc.)
2. ❌ Skip input sanitization
3. ❌ Concatenate user input into SQL strings
4. ❌ Use exact string matching for evaluation
5. ❌ Rush the system prompt creation

---

## 🆘 Troubleshooting

**Q: Which files do I absolutely need?**
A: Minimum viable = All 3 CRITICAL files + system prompt template

**Q: How long to get working?**
A: 4-6 hours for MVP, 2-3 days for production-ready

**Q: Can I skip the LLM judge?**
A: No - it's critical for accepting valid SQL variations

**Q: Do I need all AI providers?**
A: No - start with OpenAI only if you want

**Q: How many test cases minimum?**
A: 5 for MVP, 30+ for production

---

## 📞 Where to Get Help

1. **Read first**: `README.md` in this directory
2. **Implementation guide**: `../IMPLEMENTATION_GUIDE_FOR_NEW_PROJECT.md`
3. **AI assistant guide**: `../INSTRUCTIONS_FOR_AI_ASSISTANT.md`
4. **Deep reference**: `../NL2SQL_BEST_PRACTICES.md`

---

## ✨ Success Checklist

```
Day 1 (4-6 hours):
[ ] Copied CRITICAL files
[ ] Created system prompt with MY schema
[ ] Wrote 15+ examples for MY domain
[ ] Set up AI client (OpenAI)
[ ] Tested with 5 queries
[ ] 60-70% accuracy achieved

Day 2 (add 1 day):
[ ] Created 30+ test cases
[ ] Implemented LLM judge
[ ] Set up failure logging
[ ] 80-85% accuracy achieved

Day 3 (add 1 day):
[ ] Analyzed failure patterns
[ ] Updated system prompt with failing examples
[ ] Re-tested full suite
[ ] 90%+ accuracy achieved

Production Ready:
[ ] Security tested (malicious inputs)
[ ] Error handling verified
[ ] Performance acceptable
[ ] Monitoring set up
```

---

**You're ready! Copy the files and start building. 🚀**

*Remember: System prompt quality = 80% of success. Don't rush it!*
