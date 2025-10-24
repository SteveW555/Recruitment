# Report Generation Agent - Graph Analysis & SQL Generation Feature

## Overview

The Report Generation Agent has been enhanced with intelligent graph analysis and SQL generation capabilities. When a user requests a report, the agent automatically:

1. **Analyzes** if the query would benefit from graphical data visualization
2. **Recommends** the optimal chart type (line, bar, pie, scatter, heatmap)
3. **Generates** PostgreSQL SELECT queries to extract the required data
4. **Includes** the SQL query and visualization guidance in the report

This enhancement enables users to quickly generate reports with actionable data extraction queries, ready for visualization in tools like Plotly, Recharts, or Chart.js.

## Features

### 1. Intelligent Graph Suitability Analysis

The agent uses AI to determine if a query benefits from graphical visualization by analyzing:

- **Data Type**: Numeric vs textual data
- **Query Intent**: Trends, comparisons, distributions, compositions, relationships
- **Time Series**: Temporal patterns over time
- **Comparison Needs**: Cross-category or cross-entity comparisons
- **Single Values**: Reports with single KPIs (not suitable for graphs)

**Decision Criteria:**
- ✅ **Suitable**: Trends over time, comparisons, distributions, compositions, relationships
- ❌ **Not Suitable**: Single values, text-heavy reports, non-numeric data

### 2. Optimal Chart Type Recommendation

Based on the data characteristics, the agent recommends:

| Data Pattern | Recommended Chart | Use Case |
|--------------|-------------------|----------|
| **Trends over time** | Line chart | Monthly placements, quarterly revenue, hiring trends |
| **Comparisons** | Bar chart | Division performance, salary comparisons, top clients |
| **Composition** | Pie chart | Candidate status distribution, revenue by division |
| **Distribution** | Histogram/Box plot | Salary distributions, age demographics |
| **Relationships** | Scatter plot | Salary vs experience, placement fee vs duration |
| **Multi-dimensional** | Heatmap | Skills matrix, interview success by day/time |

### 3. PostgreSQL Query Generation

The agent generates safe, efficient SELECT queries following best practices:

**Query Characteristics:**
- ✅ **SELECT only** (no INSERT/UPDATE/DELETE)
- ✅ **Table aliases** (c for candidates, j for jobs, cl for clients, p for placements)
- ✅ **Aggregation functions** (COUNT, SUM, AVG, MIN, MAX)
- ✅ **Time filters** (last 12 months, current quarter, etc.)
- ✅ **Proper grouping** (GROUP BY relevant columns)
- ✅ **Ordering** (DESC for rankings, ASC for time series)
- ✅ **Efficiency** (LIMIT clauses where appropriate)

**Security:**
- Queries are **read-only** (SELECT statements only)
- No user input is directly interpolated (template-based generation)
- Queries are for **review purposes** before execution

### 4. Chart Library Recommendations

The agent recommends appropriate visualization libraries:

- **Plotly**: Interactive charts with zoom, pan, hover tooltips
- **Recharts**: React-friendly, responsive charts
- **Chart.js**: Lightweight, canvas-based rendering

## Usage Examples

### Example 1: Time Series Report (Graph Recommended)

**User Query:**
```
"Create a report showing placement trends over the last 12 months"
```

**Agent Response Includes:**

```markdown
## 📊 Data Visualization Recommendation

**Graph Type:** line
**Library:** Plotly
**Data:** Monthly placement counts over last 12 months

**SQL Query for Data Extraction:**
```sql
SELECT
    DATE_TRUNC('month', p.start_date) as month,
    COUNT(*) as placement_count
FROM placements p
WHERE p.start_date >= NOW() - INTERVAL '12 months'
GROUP BY month
ORDER BY month ASC
```

**Chart Configuration:**
- X-Axis: month
- Y-Axis: placement_count
- Grouping: None

**Reasoning:** Time series data showing trends over 12 months - line chart ideal for visualizing temporal patterns and identifying growth/decline trends.
```

### Example 2: Comparison Report (Graph Recommended)

**User Query:**
```
"Show revenue by division for the last quarter"
```

**Agent Response Includes:**

```markdown
## 📊 Data Visualization Recommendation

**Graph Type:** bar
**Library:** Recharts
**Data:** Total revenue by division for Q4 2024

**SQL Query for Data Extraction:**
```sql
SELECT
    cl.industry as division,
    SUM(p.fee) as total_revenue
FROM placements p
JOIN clients cl ON p.client_id = cl.id
WHERE p.start_date >= NOW() - INTERVAL '3 months'
GROUP BY cl.industry
ORDER BY total_revenue DESC
```

**Chart Configuration:**
- X-Axis: division
- Y-Axis: total_revenue
- Grouping: division

**Reasoning:** Comparing revenue across multiple divisions - bar chart ideal for side-by-side comparison of values.
```

### Example 3: Textual Report (No Graph)

**User Query:**
```
"Create a company profile report for client ABC Corporation"
```

**Agent Response Includes:**

```markdown
## 📊 Visualization Assessment

**No graph recommended** - Query requests textual company profile information without numeric trends or comparisons suitable for visualization. A text-based report is more appropriate.
```

## Response Metadata Structure

Every report response includes comprehensive metadata:

```json
{
  "success": true,
  "content": "Full report markdown...",
  "metadata": {
    "agent_latency_ms": 1450,
    "report_format": "markdown",
    "presentation_ready": true,
    "includes_visualizations": true,
    "graph_analysis": {
      "requires_graph": true,
      "graph_type": "line",
      "reasoning": "Time series data shows trends over 12 months",
      "recommended_library": "Plotly",
      "data_description": "Monthly placement counts over last 12 months",
      "sql_query": "SELECT DATE_TRUNC('month', p.start_date) as month...",
      "x_axis": "month",
      "y_axis": "placement_count",
      "group_by": null
    }
  }
}
```

## Available Database Tables

The agent has access to these tables for SQL generation:

| Table | Description | Key Columns |
|-------|-------------|-------------|
| **candidates** | Candidate profiles | id, name, email, skills, status, salary, location, created_at |
| **jobs** | Job postings | id, title, client_id, salary, location, status, created_at |
| **clients** | Client companies | id, name, industry, location, status, account_manager |
| **placements** | Successful placements | id, candidate_id, job_id, start_date, fee, duration |
| **applications** | Job applications | id, candidate_id, job_id, status, applied_at |
| **interviews** | Interview records | id, candidate_id, job_id, interview_date, outcome |

## Configuration

The feature is configured in [config/agents.json](../config/agents.json):

```json
{
  "REPORT_GENERATION": {
    "name": "Report Generation",
    "description": "Visualization and presentation creation with intelligent graph analysis and SQL generation",
    "tools": ["data_visualization", "report_formatting", "graph_analysis", "sql_generation"],
    "features": {
      "graph_analysis": true,
      "sql_generation": true,
      "chart_recommendation": true,
      "interactive_charts": true
    },
    "supported_chart_types": ["line", "bar", "pie", "scatter", "heatmap"],
    "supported_libraries": ["Plotly", "Recharts", "Chart.js"]
  }
}
```

## Testing

### Manual Testing

Run the manual test script:

```bash
python test_graph_analysis_manual.py
```

This tests 4 scenarios:
1. Time series report (should recommend graph)
2. Comparison report (should recommend graph)
3. Textual report (should NOT recommend graph)
4. Distribution report (should recommend graph)

### Integration Tests

Comprehensive test suite at [tests/ai_router/integration/test_report_graph_analysis.py](../tests/ai_router/integration/test_report_graph_analysis.py):

```bash
pytest tests/ai_router/integration/test_report_graph_analysis.py -v
```

**Test Coverage:**
- Graph suitability analysis for various query types
- Chart type recommendation (line, bar, pie, scatter)
- SQL query generation and validation
- Metadata structure verification
- Error handling (JSON parse errors, timeouts)
- Performance (< 2s latency target)

## Implementation Details

### Key Functions

#### `_analyze_graph_suitability(query: str) -> Dict[str, Any]`

Analyzes if a query benefits from graphical visualization.

**Parameters:**
- `query`: User's report request

**Returns:**
```python
{
    "requires_graph": bool,
    "reasoning": str,
    "graph_type": str,  # line/bar/pie/scatter/heatmap/none
    "recommended_chart_library": str,
    "data_description": str,
    "sql_query": str,  # PostgreSQL SELECT or null
    "x_axis": str,
    "y_axis": str,
    "group_by": str
}
```

**Timeout:** 2 seconds (graceful fallback if exceeded)

#### `_call_groq_api_for_analysis(prompt: str) -> str`

Calls Groq API for graph analysis using llama-3-70b-8192 model.

**Configuration:**
- **Temperature:** 0.3 (low for structured output)
- **Max tokens:** 800
- **Model:** llama-3-70b-8192

### Error Handling

The feature includes robust error handling:

1. **JSON Parse Errors:** Falls back to "no graph recommended"
2. **API Timeouts:** Returns fallback response within 2s
3. **Missing Fields:** Validates required fields in analysis
4. **API Failures:** Graceful degradation (report continues without graph analysis)

### Performance

- **Graph Analysis:** < 2 seconds
- **Total Report Generation:** < 3 seconds (including graph analysis)
- **Cached Analysis:** Analysis result stored in request metadata to avoid re-computation

## Best Practices

### When to Use

✅ **Use graph analysis for:**
- Performance reports with metrics over time
- Comparison reports (divisions, clients, candidates)
- Distribution analyses (salaries, demographics)
- Trend analyses (placement rates, revenue growth)

❌ **Don't expect graphs for:**
- Company profiles or bios
- Text-heavy strategic plans
- Single KPI values
- Qualitative assessments

### SQL Query Review

**Always review generated SQL before execution:**

1. **Verify table names** match your schema
2. **Check date ranges** are appropriate
3. **Validate aggregations** match your needs
4. **Test with LIMIT** clause first
5. **Consider indexes** for performance

### Chart Integration

To use the generated SQL with charting libraries:

**Example with Plotly (Python):**

```python
import pandas as pd
import plotly.express as px
from your_db import engine

# Execute SQL from agent
sql = metadata['graph_analysis']['sql_query']
df = pd.read_sql(sql, engine)

# Create chart
fig = px.line(
    df,
    x=metadata['graph_analysis']['x_axis'],
    y=metadata['graph_analysis']['y_axis'],
    title="Placement Trends"
)
fig.show()
```

**Example with Recharts (React):**

```javascript
// Execute SQL via API
const response = await fetch('/api/execute-query', {
  method: 'POST',
  body: JSON.stringify({ sql: metadata.graph_analysis.sql_query })
});
const data = await response.json();

// Render chart
<LineChart data={data}>
  <XAxis dataKey={metadata.graph_analysis.x_axis} />
  <YAxis dataKey={metadata.graph_analysis.y_axis} />
  <Line type="monotone" dataKey={metadata.graph_analysis.y_axis} />
</LineChart>
```

## Future Enhancements

Potential improvements for future versions:

1. **Automatic Chart Generation**: Execute SQL and generate chart files
2. **Multi-Chart Reports**: Multiple visualizations in one report
3. **Interactive Filters**: Dynamic SQL with user-specified filters
4. **Custom Table Schemas**: User-provided schema for SQL generation
5. **Chart Customization**: Color schemes, axes labels, legends
6. **Export Formats**: PNG, SVG, PDF output options
7. **Real-time Data**: WebSocket updates for live dashboards

## Troubleshooting

### Issue: "No graph recommended" when expected

**Possible causes:**
- Query is too vague (add specifics like "over last 12 months")
- Data is non-numeric (agent correctly identified text-based report)
- Single value query (not suitable for trends/comparisons)

**Solution:** Rephrase query with temporal or comparative keywords

### Issue: SQL query is incorrect

**Possible causes:**
- Table/column names differ from assumptions
- Complex joins not captured in context
- Date format mismatches

**Solution:** Review and modify SQL before execution

### Issue: Analysis timeout

**Possible causes:**
- API latency spike
- Network issues

**Solution:** Retry request; agent will fallback gracefully

## Support

For issues or questions:

- **Documentation**: [AI Router README](../utils/ai_router/README.md)
- **Tests**: [test_report_graph_analysis.py](../tests/ai_router/integration/test_report_graph_analysis.py)
- **Configuration**: [agents.json](../config/agents.json)
- **Agent Implementation**: [report_generation_agent.py](../utils/ai_router/agents/report_generation_agent.py)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-23 | Initial release with graph analysis and SQL generation |

---

**Last Updated:** January 23, 2025
**Author:** ProActive People Development Team
**Status:** Production-ready ✅
