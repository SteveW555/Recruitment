# GROQ Quick Start Guide

**5-Minute Setup for ProActive People Recruitment System**

---

## ⚡ Installation (1 minute)

```bash
pip install groq python-dotenv
```

---

## 🔑 Setup (1 minute)

Your `.env` file should contain:
```
GROQ_API_KEY=your_api_key_here
```

✅ You're ready to go!

---

## ✅ Verify (1 minute)

```bash
python test_groq_setup.py
```

Should show:
```
✅ ALL TESTS PASSED!
🎉 Your GROQ setup is complete and working!
```

---

## 🚀 Try It Now (2 minutes)

### Query Your Client Database

**Interactive Mode:**
```bash
python groq_with_context.py
```

Then type:
```
Which clients have active jobs?
Show top 5 revenue clients
Which IT companies are we working with?
```

**Single Query:**
```bash
python groq_with_context.py --prompt "Which clients need follow-up?"
```

**Pre-defined Analysis:**
```bash
python groq_with_context.py --analyze opportunity
python groq_with_context.py --analyze revenue
python groq_with_context.py --analyze risk
```

---

## 💻 Use in Python

### Basic Example
```python
from groq_client import GroqClient

# Initialize
client = GroqClient()

# Ask anything
response = client.complete("Explain AI recruiting in 2 sentences")
print(response.content)
```

### CV Parsing
```python
from groq_client import GroqClient

client = GroqClient()

cv_text = """
John Smith
Email: john@email.com
Experience: 5 years in Sales
Skills: B2B Sales, Salesforce, Negotiation
"""

parsed = client.parse_cv(cv_text)
print(parsed)  # Returns structured JSON
```

### Candidate Matching
```python
match = client.match_candidate_to_job(
    candidate_profile={"skills": ["Python", "FastAPI"]},
    job_description="Looking for Python developer..."
)

print(f"Match Score: {match['match_score']}")
print(f"Strengths: {match['strengths']}")
print(f"Gaps: {match['gaps']}")
```

### Generate Job Description
```python
job_desc = client.generate_job_description(
    job_title="Senior Sales Executive",
    company_name="ProActive People",
    location="Bristol, UK",
    required_skills=["B2B Sales", "CRM", "Account Management"]
)

print(job_desc)
```

---

## 📋 Common Queries

### For Sales Team
```bash
python groq_with_context.py --prompt "Which clients could we upsell to?"
python groq_with_context.py --prompt "Show clients with expansion plans"
python groq_with_context.py --analyze opportunity
```

### For Account Managers
```bash
python groq_with_context.py --prompt "Which clients haven't had placements recently?"
python groq_with_context.py --prompt "Show all Sam Henderson's clients"
python groq_with_context.py --analyze engagement
```

### For Leadership
```bash
python groq_with_context.py --analyze revenue
python groq_with_context.py --analyze industry
python groq_with_context.py --prompt "What are our top performing sectors?"
```

---

## 🎯 Available Analyses

Just add `--analyze <type>`:

- `overview` - Database overview
- `revenue` - Revenue leaders
- `industry` - Sector breakdown
- `opportunity` - Growth opportunities
- `risk` - At-risk clients
- `services` - Service usage
- `specialties` - Skills in demand
- `location` - Geographic spread
- `engagement` - Client activity
- `account_tier` - Tier comparison

---

## 📚 Learn More

- **Full Guide:** `GROQ_CONTEXT_README.md`
- **Examples:** `python example_groq_queries.py`
- **Summary:** `GROQ_IMPLEMENTATION_SUMMARY.md`
- **API Docs:** See docstrings in `groq_client.py`

---

## 🆘 Troubleshooting

**Not working?**
```bash
python test_groq_setup.py
```

**Need help?**
- Check `GROQ_CONTEXT_README.md`
- Review examples in `example_groq_queries.py`
- Read docstrings in `groq_client.py`

---

## 🎉 That's It!

You now have AI-powered recruitment tools ready to use.

**Try this right now:**
```bash
python groq_with_context.py --prompt "Summarize our client database"
```

---

*ProActive People | Bristol, UK*
