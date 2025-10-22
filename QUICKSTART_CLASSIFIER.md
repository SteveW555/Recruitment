# Quick Start - Test AI Router Classifier

## 1. Install & Verify (30 seconds)

```bash
# Install dependencies
pip install -r requirements-ai-router.txt

# Test single query (model downloads automatically on first run)
python test_classifier.py --query "What are GDPR requirements?"
```

**Expected first-run output:**
```
Loading sentence-transformers model: all-MiniLM-L6-v2...
Downloading model... (~25MB)
✓ Model loaded successfully
```

---

## 2. Interactive Testing (Best for Manual Testing)

```bash
python test_classifier.py
```

Type queries and see instant classification:

```
Query> Find candidates with 5+ years sales experience

Primary Classification:
  Category:   INFORMATION_RETRIEVAL
  Confidence: 87.65%
  Latency:    45ms
```

**Commands:**
- `verbose on` - Show all category scores (great for debugging)
- `examples` - Show example queries from config
- `quit` - Exit

---

## 3. Batch Testing (Test Multiple Queries)

```bash
python test_classifier.py --batch test_queries.txt
```

Processes 36 sample queries and shows statistics.

---

## 4. Create Your Own Test File

```bash
cat > my_queries.txt << EOF
What are the average salaries for software engineers in London?
How can we reduce our time-to-hire?
Create a quarterly performance report
Automate candidate email follow-ups
What are IR35 compliance requirements?
Hello
EOF

python test_classifier.py --batch my_queries.txt --verbose
```

---

## 5. Understanding Results

### Confidence Colors
- 🟢 **Green (≥80%)**: High confidence, reliable
- 🟡 **Yellow (60-79%)**: Moderate confidence
- 🔴 **Red (<60%)**: Low confidence, fallback triggered

### Example Output (Verbose Mode)

```
Query: Create a quarterly report

Primary Classification:
  Category:   REPORT_GENERATION
  Confidence: 91.45%
  Latency:    38ms

All Category Scores:
  → REPORT_GENERATION       91.45% ████████████████████████████████████████
    INFORMATION_RETRIEVAL   62.34% ████████████████████████░░░░░░░░░░░░░░░
    PROBLEM_SOLVING         45.12% ██████████████████░░░░░░░░░░░░░░░░░░░░░░
    AUTOMATION              32.78% █████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░
    INDUSTRY_KNOWLEDGE      28.56% ███████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    GENERAL_CHAT            12.34% ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

---

## Files Created

| File | Purpose |
|------|---------|
| [test_classifier.py](test_classifier.py) | Main CLI test script |
| [test_queries.txt](test_queries.txt) | 36 sample test queries |
| [README_CLASSIFIER_TEST.md](README_CLASSIFIER_TEST.md) | Full documentation |
| [QUICKSTART_CLASSIFIER.md](QUICKSTART_CLASSIFIER.md) | This file |

---

## Common Commands

```bash
# Single query
python test_classifier.py --query "Your query here"

# Single query with verbose output
python test_classifier.py --query "Your query" --verbose

# Interactive mode
python test_classifier.py

# Batch mode
python test_classifier.py --batch test_queries.txt

# Custom config
python test_classifier.py --config /path/to/agents.json

# Stricter threshold (default is 0.7)
python test_classifier.py --threshold 0.85
```

---

## Next Steps

1. ✅ Run interactive mode: `python test_classifier.py`
2. ✅ Test with your own queries
3. ✅ Run batch mode: `python test_classifier.py --batch test_queries.txt --verbose`
4. 🔧 Tune example queries in [config/agents.json](config/agents.json) if needed
5. 🚀 Integrate with full AI router system

---

## Model Info

- **Name**: `all-MiniLM-L6-v2`
- **Size**: ~25MB
- **Dimensions**: 384
- **Cache Location**: `~/.cache/torch/sentence_transformers/`
- **Speed**: <100ms classification (target met ✓)

---

## Help

```bash
python test_classifier.py --help
```

For detailed documentation, see [README_CLASSIFIER_TEST.md](README_CLASSIFIER_TEST.md).
