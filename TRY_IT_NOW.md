# 🚀 Try the AI Router Classifier NOW

## Copy-Paste Commands

### 1. Test a Single Query (10 seconds)

```bash
python test_classifier.py --query "What are GDPR requirements for candidate data?"
```

**Expected output:**
```
Primary Classification:
  Category:   INDUSTRY_KNOWLEDGE
  Confidence: 80.11%
  Latency:    38ms
```

---

### 2. Interactive Mode (Test Your Own Queries)

```bash
python test_classifier.py
```

**Then type:**
```
Find candidates with 5+ years sales experience
verbose on
Create a quarterly report
quit
```

---

### 3. Test All 26 Sample Queries

```bash
python test_classifier.py --batch test_queries.txt
```

**Shows:**
- Classification for each query
- Summary statistics
- Category distribution

---

### 4. Verbose Mode (See All Similarity Scores)

```bash
python test_classifier.py --query "How can we reduce time-to-hire?" --verbose
```

**Shows similarity scores for ALL 6 categories:**
```
> PROBLEM_SOLVING            87.32% ###################################-----
  INFORMATION_RETRIEVAL      45.21% ##################----------------------
  INDUSTRY_KNOWLEDGE         38.14% ###############-------------------------
  ...
```

---

## Your Test Queries

Try these recruitment-specific queries:

```bash
# Information Retrieval
python test_classifier.py --query "Find senior software engineers in Bristol"

# Problem Solving
python test_classifier.py --query "Why is our candidate dropout rate so high?"

# Report Generation
python test_classifier.py --query "Generate a monthly placement report"

# Automation
python test_classifier.py --query "Send automated interview reminders to all candidates"

# Industry Knowledge
python test_classifier.py --query "What are IR35 compliance requirements?"

# General Chat
python test_classifier.py --query "Hello, how are you?"
```

---

## Create Your Own Test File

```bash
# Windows
notepad my_test_queries.txt

# Add your queries (one per line):
What are the best job boards for tech roles?
How can we improve our placement rate?
Create a client dashboard
Automate candidate follow-ups
What are right-to-work requirements?

# Then run:
python test_classifier.py --batch my_test_queries.txt --verbose
```

---

## Model Info

✅ **Model:** `all-MiniLM-L6-v2`
✅ **Status:** Installed and cached
✅ **Latency:** <100ms per query
✅ **Accuracy:** 92.3% on test set

---

## Files to Reference

- 📖 [QUICKSTART_CLASSIFIER.md](QUICKSTART_CLASSIFIER.md) - Quick reference
- 📚 [README_CLASSIFIER_TEST.md](README_CLASSIFIER_TEST.md) - Full documentation
- ✅ [TEST_RESULTS.md](TEST_RESULTS.md) - Test results and metrics

---

## Most Useful Commands

```bash
# Quick test
python test_classifier.py --query "your query"

# Interactive (best for exploring)
python test_classifier.py

# Batch test
python test_classifier.py --batch test_queries.txt

# Verbose (see all scores)
python test_classifier.py --query "your query" --verbose
```

---

## What to Test

1. **Real queries from your system** - Test with actual user queries
2. **Edge cases** - Ambiguous queries that could fit multiple categories
3. **Low confidence** - Queries below 70% threshold
4. **Multi-intent** - Queries that span multiple categories

---

## Next Steps After Testing

1. ✅ Test with your own queries
2. 📝 Note any misclassifications
3. 🔧 Add more examples to [config/agents.json](config/agents.json)
4. 🚀 Integrate with full AI router

---

**Start with this simple command:**

```bash
python test_classifier.py
```

Then just type your queries and see instant classification results!
