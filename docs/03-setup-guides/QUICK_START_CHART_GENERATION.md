# Quick Start: Adding Chart Generation to Report Agent

## The Short Answer

**No, you don't need a better LLM model.** Your current Groq llama-3-70b-8192 is perfect for generating report text.

**What you need:** Add a Python visualization library (Plotly) to generate actual charts alongside the text.

---

## 5-Minute Setup

### Step 1: Install Dependencies (30 seconds)

```bash
pip install plotly pandas kaleido
```

### Step 2: Create Visualization Generator (2 minutes)

Create `utils/ai_router/visualization/chart_generator.py`:

```python
import plotly.express as px
import pandas as pd
from pathlib import Path

class ChartGenerator:
    def __init__(self, output_dir="./generated_charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def bar_chart(self, data: pd.DataFrame, x: str, y: str, title: str) -> str:
        """Generate bar chart, return HTML path."""
        fig = px.bar(data, x=x, y=y, title=title, template='plotly_white')

        html_path = self.output_dir / f"{title.lower().replace(' ', '_')}.html"
        fig.write_html(html_path)

        return str(html_path)

    def line_chart(self, data: pd.DataFrame, x: str, y: str, title: str) -> str:
        """Generate line chart, return HTML path."""
        fig = px.line(data, x=x, y=y, title=title, template='plotly_white', markers=True)

        html_path = self.output_dir / f"{title.lower().replace(' ', '_')}.html"
        fig.write_html(html_path)

        return str(html_path)
```

### Step 3: Enhance Report Agent (2 minutes)

Modify `utils/ai_router/agents/report_generation_agent.py`:

```python
from ..visualization.chart_generator import ChartGenerator

class ReportGenerationAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.client = Groq()
        self.chart_gen = ChartGenerator()  # Add this

    async def _generate_report_with_charts(self, requirement: str):
        # Generate text report (existing code)
        report_text = await self._generate_report(requirement, None)

        # Check if advertising report
        if "advertising" in requirement.lower():
            df = pd.read_csv("finance_test_data/financial_records/11_job_board_advertising.csv")

            # Generate bar chart
            costs_by_board = df.groupby('job_board')['amount'].sum().reset_index()
            chart_path = self.chart_gen.bar_chart(
                costs_by_board,
                x='job_board',
                y='amount',
                title='Advertising Costs by Job Board'
            )

            # Append chart link to report
            report_text += f"\n\n## 📊 Visualizations\n\n[View Interactive Chart]({chart_path})\n"

        return report_text
```

---

## Test It

```python
# Test the chart generation
from utils.ai_router.visualization.chart_generator import ChartGenerator
import pandas as pd

# Load data
df = pd.read_csv("finance_test_data/financial_records/11_job_board_advertising.csv")
costs = df.groupby('job_board')['amount'].sum().reset_index()

# Generate chart
gen = ChartGenerator()
chart_path = gen.bar_chart(costs, 'job_board', 'amount', 'Advertising Costs 2024')

print(f"Chart saved to: {chart_path}")
# Open the HTML file in your browser to see the interactive chart
```

---

## What You Get

### Before (Current State)
```
Agent Response:
"Here's your advertising report...

📊 Suggested Chart: Bar chart showing costs by job board
(You need to create this manually in Excel)"
```

### After (With Chart Generation)
```
Agent Response:
"Here's your advertising report...

📊 Interactive Chart: [View Chart](./generated_charts/advertising_costs_2024.html)
(Click to open interactive bar chart with hover tooltips, zoom, pan)"
```

---

## Model Comparison

| Model | Can Generate Text Reports? | Can Generate Charts? | Recommendation |
|-------|---------------------------|---------------------|----------------|
| **Groq llama-3-70b-8192** | ✅ Excellent | ❌ No (text only) | **Use for report text** |
| **GPT-4 Vision** | ✅ Excellent | ✅ Yes (via Code Interpreter) | Overkill + expensive |
| **Claude 3.5 Sonnet** | ✅ Excellent | ✅ Yes (code generation) | Good but slower |
| **Python Plotly** | ❌ N/A | ✅ Best quality | **Use for charts** ⭐ |

### The Right Approach

✅ **Use Groq LLM for:** Report text, analysis, insights, recommendations
✅ **Use Plotly for:** Generating the actual bar/line/pie charts
✅ **Result:** Fast, high-quality, cost-effective

---

## Why Not Use LLM for Charts?

### LLM Code Generation Approach
```
User Query → LLM generates Python code → Execute code → Generate chart
Time: ~3-5 seconds
Cost: API call charges
Risk: Code execution security concerns
Reliability: Variable (code may fail)
```

### Direct Python Library Approach (Recommended)
```
User Query → Read data → Plotly generates chart → Done
Time: <500ms
Cost: $0 (no API calls)
Risk: None (safe library)
Reliability: 100% predictable
```

**The LLM generates the REPORT TEXT.**
**Plotly generates the CHARTS.**
**Together, you get text + visualizations.**

---

## Real Example: Advertising Report

### Query
```
"Show me a report on advertising costs over the last year with a bar graph"
```

### What Happens

1. **Router** classifies as `report-generation` (existing)
2. **Report Agent (LLM)** generates markdown report text (existing)
3. **Chart Generator (NEW)** creates bar chart from CSV data
4. **Response** includes both text report + interactive chart

### Output
```markdown
# Advertising Costs Report 2024

## Executive Summary
Total advertising spend across all job boards in 2024 was £40,776,
representing a 12% increase over 2023...

## Key Metrics
- **Total Spend**: £40,776
- **Job Boards Used**: 6 platforms
- **Jobs Posted**: 1,164 total
- **Cost per Job**: £35.02 average

## Findings
Indeed was the highest cost platform at £12,854 (31.5% of total),
followed by Totaljobs at £6,541 (16.0%)...

## 📊 Interactive Visualizations

[View Bar Chart: Costs by Job Board](./generated_charts/advertising_costs_bar.html)
[View Line Chart: Monthly Trend](./generated_charts/monthly_trend.html)

## Recommendations
1. Negotiate volume discounts with Indeed (31% of spend)
2. Optimize job board mix based on ROI per placement
3. Consider reducing Jobserve spend (lowest job posting volume)
```

Plus: Actual interactive HTML charts you can open and explore.

---

## Next Steps

### Option 1: Quick Prototype (2 hours)
1. Install Plotly: `pip install plotly pandas kaleido`
2. Create simple `ChartGenerator` class
3. Test with advertising CSV data
4. Generate 1-2 chart types (bar, line)

### Option 2: Production Implementation (2-3 days)
1. Full `ChartGenerator` with all chart types
2. Enhance `ReportGenerationAgent` to detect data sources
3. Add chart embeddings in markdown reports
4. Test with multiple report types
5. Add error handling and fallbacks

### Option 3: Frontend Integration (5-7 days)
1. Install Recharts: `npm install recharts`
2. Create React chart components
3. Modify API to return chart data
4. Embed interactive charts in dashboard UI
5. Add export functionality (PDF, PNG)

---

## FAQ

### Q: Do I need GPT-4 or Claude 3.5 for this?
**A:** No. Your current Groq llama-3-70b-8192 is perfect for the text. Use Plotly (Python library) for charts.

### Q: Will this slow down my agent?
**A:** No. Plotly chart generation is <500ms. LLM text generation is still 1-2s. Total: ~2s (same as now).

### Q: Can users interact with the charts?
**A:** Yes! Plotly HTML charts have hover tooltips, zoom, pan, and data point inspection built-in.

### Q: What about PDF exports?
**A:** Plotly can export to PNG/SVG/PDF. Use `fig.write_image()` for static exports.

### Q: How do I handle different data sources?
**A:** Add logic to detect query keywords ("advertising" → CSV, "placements" → database, etc.)

---

## The Bottom Line

✅ **Your current LLM model is perfect.** (Groq llama-3-70b-8192)
✅ **Add Plotly for chart generation.** (Python library, not LLM)
✅ **2-3 days implementation time.**
✅ **Zero additional API costs.**
✅ **Production-ready, high-quality charts.**

**You don't need a better model. You need a visualization library.**

---

**Created:** 2025-10-23
**Recommended:** Start with Option 1 (Quick Prototype)
**Documentation:** See VISUALIZATION_GENERATION_SOLUTIONS.md for full details
