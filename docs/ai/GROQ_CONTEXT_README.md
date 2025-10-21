# GROQ Context Query Tool

Query your ProActive People client database using AI-powered natural language with GROQ.

## 🚀 Quick Start

### Prerequisites
```bash
pip install groq python-dotenv
```

Ensure your `.env` file contains:
```
GROQ_API_KEY=your_api_key_here
```

## 📖 Usage Methods

### 1. Interactive Mode (Recommended for exploring)
```bash
python groq_with_context.py
```

Then type your questions:
```
💬 Your query: Which clients have the highest revenue?
💬 Your query: Show me all IT Services clients
💬 Your query: analyze revenue
```

### 2. Single Query Mode
```bash
python groq_with_context.py --prompt "Which clients have active jobs?"
```

### 3. Pre-defined Analysis
```bash
python groq_with_context.py --analyze revenue
python groq_with_context.py --analyze opportunity
python groq_with_context.py --analyze risk
```

Available analyses:
- `overview` - Comprehensive database overview
- `revenue` - Revenue analysis and top performers
- `industry` - Industry sector breakdown
- `account_tier` - Tier comparison (Platinum/Gold/Silver/Bronze)
- `services` - Service line usage and cross-selling
- `risk` - Risk assessment and concerns
- `opportunity` - Growth opportunities and active clients
- `specialties` - Recruitment specialty demand
- `location` - Geographic distribution
- `engagement` - Client engagement and activity

### 4. Streaming Responses
```bash
python groq_with_context.py --prompt "Analyze top 10 clients" --stream
```

### 5. Custom Options
```bash
python groq_with_context.py \
  --prompt "Which clients need follow-up?" \
  --max-records 30 \
  --temperature 0.5 \
  --compact
```

## 📚 Examples

### Run Prepared Examples
```bash
python example_groq_queries.py
```

This runs 10 example queries demonstrating various use cases:
1. Top revenue clients
2. Industry breakdown
3. Account tier analysis
4. Growth opportunities
5. Service line analysis
6. Risk assessment
7. Recruitment specialties
8. Geographic distribution
9. Work model preferences
10. Pre-defined analysis

## 💡 Example Queries

### Business Intelligence
```
"Which clients generated the most revenue in 2024?"
"Compare average fee percentages across different industries"
"Show clients with the highest number of placements"
```

### Sales & Opportunities
```
"Which clients have active jobs right now?"
"Identify clients with expansion plans mentioned in notes"
"Show Bronze tier clients that could be upgraded to Silver"
"Which clients use only one service line? Suggest cross-selling opportunities"
```

### Risk Management
```
"Which clients haven't had placements in over 6 months?"
"Identify clients with 'Fair' payment history"
"Show clients with long recruitment cycles"
```

### Account Management
```
"Which clients does Sam Henderson manage?"
"Show all clients using our Wellbeing services"
"Which clients have the fastest hiring processes?"
```

### Market Analysis
```
"What are the most common recruitment specialties?"
"Which industries prefer remote work models?"
"Analyze salary ranges across different sectors"
```

## 🛠️ Programmatic Usage

```python
from groq_with_context import GroqContextQuery

# Initialize
query_tool = GroqContextQuery("Fake Data/fake_client_database_50.csv")

# Simple query
response = query_tool.query("Which clients have active jobs?")
print(response)

# Pre-defined analysis
analysis = query_tool.analyze_clients('revenue')
print(analysis)

# Custom parameters
response = query_tool.query(
    "Identify high-value opportunities",
    max_records=20,
    temperature=0.5,
    stream=False
)
```

## 📋 Command Line Options

```
--csv PATH              Path to CSV file (default: Fake Data/fake_client_database_50.csv)
--prompt TEXT           Query prompt for single-query mode
--analyze TYPE          Run pre-defined analysis
--max-records N         Maximum records in context (default: 50)
--stream                Stream the response
--compact               Use compact JSON format
--temperature N         Response creativity 0.0-2.0 (default: 0.7)
```

## 🎯 Use Cases

### For Sales Team
- Identify upselling opportunities
- Find clients with active hiring needs
- Analyze revenue by sector
- Track account tier distribution

### For Account Managers
- Review client engagement history
- Identify at-risk clients
- Find cross-selling opportunities
- Analyze service usage patterns

### For Leadership
- Revenue analysis and forecasting
- Industry sector performance
- Geographic expansion opportunities
- Service line profitability

### For Operations
- Client payment analysis
- Recruitment specialty demand
- Work model trends
- Hiring process efficiency

## 🔧 Advanced Features

### Custom Context Fields
```python
# Only include specific fields in context
response = query_tool.query(
    "Show revenue leaders",
    selected_fields=["Company Name", "Lifetime Revenue (£)", "Industry Sector"]
)
```

### Filtering Before Query
```python
# Filter records before querying
from groq_with_context import CSVContextLoader

loader = CSVContextLoader("Fake Data/fake_client_database_50.csv")
loader.load()

# Get only IT sector clients
it_clients = loader.filter_records({"Industry Sector": "IT Services"})
print(f"Found {len(it_clients)} IT clients")
```

### Conversation Mode
```python
# Maintain conversation history
query_tool.query(
    "Show me the top 5 revenue clients",
    conversation_id="analysis_session_1"
)

# Follow-up question (uses previous context)
query_tool.query(
    "Which of these have active jobs?",
    conversation_id="analysis_session_1"
)
```

## 📊 Output Format

Responses include:
- AI-generated answer based on your data
- Model used
- Token usage statistics
- Processing time

Example:
```
======================================================================
🤖 Querying GROQ...
======================================================================

Response:
Based on the client database, the top 5 clients by lifetime revenue are:

1. Call Centre Excellence Ltd - £420,000 (Contact Centre Operations)
2. Bristol Financial Group - £340,000 (Financial Services)
...

======================================================================
Model: llama-3.3-70b-versatile
Tokens Used: 1847 (Prompt: 1520, Completion: 327)
======================================================================
```

## 🎓 Tips

1. **Be specific** - More specific questions get better answers
2. **Use examples** - "Show top 5 clients" vs "Show some clients"
3. **Combine criteria** - "Show IT clients with active jobs in Bristol"
4. **Ask for recommendations** - "Suggest which clients to contact this week"
5. **Request formatting** - "Create a table of..." or "List in bullet points..."

## 🔐 Security Note

This tool uses your GROQ API key from the `.env` file. Keep your API key secure and never commit it to version control.

## 📞 Support

For issues or questions:
- Check the example queries: `python example_groq_queries.py`
- Run in interactive mode for guided exploration
- Review [groq.py](groq.py) for the full API documentation

---

**ProActive People Recruitment Automation System**
Built with GROQ AI | Bristol, UK
