# GROQ Candidates Query Tool

Query your recruitment candidates database using natural language with AI-powered SQL generation and analysis.

---

## 🚀 Quick Start

### Installation
Dependencies already installed from previous GROQ setup:
```bash
pip install groq python-dotenv
```

### Test It
```bash
python groq_candidates_query.py --query "Find available Python developers"
```

---

## 📖 Usage Modes

### 1. Interactive Mode (Recommended)
```bash
python groq_candidates_query.py
```

Then type your questions:
```
💬 Your query: Find available software engineers
💬 Your query: Show candidates with AWS skills
💬 Your query: analyze What skills are most common?
```

### 2. SQL Generation Mode
Convert natural language to SQL queries:
```bash
python groq_candidates_query.py --query "Find Python developers with AWS"
```

**Output:**
```sql
select c.first_name, c.last_name, c.primary_email, c.job_title_target
from candidates as c
where c.primary_skills ilike '%python%'
  and c.primary_skills ilike '%aws%';
```

### 3. Analysis Mode
Get AI-powered insights on your candidates:
```bash
python groq_candidates_query.py --analyze "What are the most in-demand skills?"
```

### 4. Recommendation Mode
Get candidate recommendations for job requirements:
```bash
python groq_candidates_query.py --recommend "Senior Python developer with 5+ years AWS experience"
```

---

## 💡 Example Queries

### Basic Searches
```bash
# Simple name search
python groq_candidates_query.py --query "Find candidate Alex Roberts"

# Job title search
python groq_candidates_query.py --query "Show all software engineers"

# Skills-based
python groq_candidates_query.py --query "Find Python developers"
```

### Status Filters
```bash
# Available candidates
python groq_candidates_query.py --query "Show available candidates"

# Interviewing
python groq_candidates_query.py --query "Who is currently interviewing?"

# Offer pending
python groq_candidates_query.py --query "Candidates with pending offers"
```

### Skills Combinations
```bash
# Multiple skills (AND)
python groq_candidates_query.py --query "Candidates with both Python and AWS skills"

# Multiple skills (OR)
python groq_candidates_query.py --query "Developers with Python or Java"

# Skills + Status
python groq_candidates_query.py --query "Available Python developers"
```

### Salary Queries
```bash
# Under amount
python groq_candidates_query.py --query "Candidates expecting under £100k"

# Range
python groq_candidates_query.py --query "Show candidates wanting between 80k and 120k"

# Skills + Salary
python groq_candidates_query.py --query "AWS engineers wanting over 100k"
```

### Date/Recency
```bash
# Last week
python groq_candidates_query.py --query "Candidates contacted in the last week"

# This month
python groq_candidates_query.py --query "Show candidates contacted this month"

# Cold leads
python groq_candidates_query.py --query "Candidates not contacted in 30 days"
```

### Feedback/Sentiment
```bash
# Positive feedback
python groq_candidates_query.py --query "Show candidates with positive interview feedback"

# Highly rated
python groq_candidates_query.py --query "Candidates with highly positive sentiment"
```

### Complex Multi-Filter
```bash
python groq_candidates_query.py --query "Available software engineers with Python, positive feedback, under 120k, contacted recently"
```

### Aggregations
```bash
# Count
python groq_candidates_query.py --query "How many available candidates do we have?"

# Group by
python groq_candidates_query.py --query "Count candidates by status"

# Average
python groq_candidates_query.py --query "Average desired salary for software engineers"

# Top N
python groq_candidates_query.py --query "Top 5 highest salary expectations"
```

---

## 🧠 Analysis Mode Examples

```bash
# Skill analysis
python groq_candidates_query.py --analyze "What are the most common skills?"

# Engagement analysis
python groq_candidates_query.py --analyze "Which candidates haven't been contacted recently?"

# Salary trends
python groq_candidates_query.py --analyze "What are the salary trends by role?"

# Status distribution
python groq_candidates_query.py --analyze "How are candidates distributed across pipeline stages?"

# Industry experience
python groq_candidates_query.py --analyze "Which industries do our candidates have experience in?"
```

---

## 🎯 Recommendation Mode Examples

```bash
# Technical role
python groq_candidates_query.py --recommend "Senior Python Developer, AWS, microservices, 5+ years"

# Sales role
python groq_candidates_query.py --recommend "B2B Sales Executive, CRM experience, Fintech industry"

# Multiple skills
python groq_candidates_query.py --recommend "Full Stack Developer: React, Node.js, PostgreSQL"

# Specific industry
python groq_candidates_query.py --recommend "Financial Analyst with GAAP, Excel modeling, Fintech background"
```

---

## 📋 Database Schema Reference

The tool queries candidates with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `candidate_id` | text | Unique ID (C001, C002...) |
| `first_name` | text | First name |
| `last_name` | text | Last name |
| `primary_email` | text | Email address |
| `phone_number` | text | Phone number |
| `job_title_target` | text | Desired role |
| `primary_skills` | text | Comma-separated skills |
| `industry_experience` | text | Industry background |
| `current_status` | text | Pipeline status |
| `last_contact_date` | date | Last contact |
| `desired_salary` | numeric | Salary expectation (GBP) |
| `interview_notes_sentiment` | text | Positive/Neutral/Negative |
| `recruiter_notes_external` | text | Client-facing notes |
| `recruiter_notes_internal` | text | Internal notes |

---

## 🎓 Interactive Mode Commands

When running in interactive mode:

```bash
python groq_candidates_query.py
```

Available commands:
- **Type your question** - Generate SQL
- **`analyze <question>`** - Get AI analysis
- **`recommend <requirements>`** - Get candidate matches
- **`examples`** - Show all examples
- **`quit` or `exit`** - Exit

---

## 💻 Programmatic Usage

```python
from groq_candidates_query import CandidatesQueryTool

# Initialize
tool = CandidatesQueryTool()

# Generate SQL
sql = tool.generate_sql("Find available Python developers")
print(sql)

# Analyze data
analysis = tool.analyze_candidates("What are the most common skills?")
print(analysis)

# Get recommendations
recommendations = tool.get_candidate_recommendations(
    "Senior Python Developer, AWS, 5+ years experience"
)
print(recommendations)
```

---

## 🔧 Command-Line Options

```bash
python groq_candidates_query.py [OPTIONS]

Options:
  --query TEXT        Natural language query for SQL generation
  --analyze TEXT      Analyze candidates data
  --recommend TEXT    Get candidate recommendations
  --csv PATH          Path to candidates CSV (default: Fake Data/recruitment_candidates.csv)
  --prompt PATH       Path to system prompt (default: prompts/candidates_nl2sql_system_prompt.txt)
  --examples          Show example queries
  -h, --help          Show help message
```

---

## 🎯 Use Cases

### For Recruiters
- **Quick searches**: "Show me available React developers"
- **Skill matching**: "Python developers with AWS in fintech"
- **Status tracking**: "Who's interviewing this week?"

### For Account Managers
- **Pipeline analysis**: "Count candidates by status"
- **Engagement**: "Candidates not contacted in 30 days"
- **Salary trends**: "Average salary by role"

### For Sales Team
- **Availability**: "How many available software engineers?"
- **Skill inventory**: "Candidates with SAP skills"
- **Industry match**: "Fintech experienced candidates"

### For Leadership
- **Database insights**: "analyze skill distribution"
- **Trends**: "analyze salary expectations by industry"
- **Quality metrics**: "analyze interview feedback sentiment"

---

## 📊 Output Examples

### SQL Generation
```
======================================================================
🔍 Natural Language Query:
======================================================================
Find available Python developers with AWS skills

======================================================================
📝 Generated SQL Query:
======================================================================
select c.first_name, c.last_name, c.primary_email, c.job_title_target
from candidates as c
where c.current_status ilike '%available%'
  and c.job_title_target ilike '%developer%'
  and c.primary_skills ilike '%python%'
  and c.primary_skills ilike '%aws%';

======================================================================
Model: llama-3.3-70b-versatile
Tokens: 3101
======================================================================
```

### Analysis Output
Provides detailed insights with:
- Statistics and counts
- Specific examples from data
- Actionable recommendations
- Next steps

---

## 🔍 Query Tips

1. **Be specific**: "Python developers" vs "developers"
2. **Use natural language**: Write like you're talking to a person
3. **Combine criteria**: "Available Python developers with positive feedback"
4. **Use salary notation**: "under 100k", "between 80k and 120k"
5. **Specify timeframes**: "last week", "this month", "recently"

---

## 🛠️ Advanced Features

### Custom System Prompt
Modify [prompts/candidates_nl2sql_system_prompt.txt](prompts/candidates_nl2sql_system_prompt.txt) to customize SQL generation logic.

### Custom CSV
Use your own candidates CSV:
```bash
python groq_candidates_query.py --csv "path/to/your/candidates.csv" --query "Your question"
```

---

## 🔐 Security Notes

- Uses GROQ API key from `.env` file
- CSV data is loaded locally (not sent to GROQ for SQL generation)
- Analysis mode sends sample data to GROQ for insights
- Generated SQL is safe (read-only SELECT queries)

---

## 📞 Integration

### Use with Supabase
Copy generated SQL and run directly in Supabase:
```sql
-- Generated query ready to execute
select c.first_name, c.last_name, c.primary_email
from candidates as c
where c.primary_skills ilike '%python%';
```

### Use with Applications
```python
from groq_candidates_query import CandidatesQueryTool
import psycopg2

# Generate SQL
tool = CandidatesQueryTool()
sql = tool.generate_sql("Find available Python developers")

# Execute on real database
conn = psycopg2.connect(database_url)
cursor = conn.cursor()
cursor.execute(sql)
results = cursor.fetchall()
```

---

## 📚 Related Files

- **System Prompt**: [prompts/candidates_nl2sql_system_prompt.txt](prompts/candidates_nl2sql_system_prompt.txt)
- **Sample Data**: [Fake Data/recruitment_candidates.csv](Fake Data/recruitment_candidates.csv)
- **GROQ Client**: [groq_client.py](groq_client.py)

---

**Status:** ✅ Ready to Use
**Tested:** ✅ All modes working
**Data:** 100 sample candidates loaded

---

*ProActive People - Recruitment Automation System*
*Built with GROQ AI | Bristol, UK*
