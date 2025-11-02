# Visualization Generation Solutions for Report Agent

## Current State Analysis

### What the Report Agent Does Now

**File:** `utils/ai_router/agents/report_generation_agent.py`

**Current Capabilities:**
- ✅ Generates markdown-formatted reports with text content
- ✅ Suggests visualization types (bar charts, line charts, pie charts)
- ✅ Provides visualization recommendations: `📊 [Chart Type]: [Description]`
- ✅ Creates markdown tables for tabular data
- ❌ **Does NOT generate actual charts/graphs**
- ❌ **Does NOT produce images or interactive visualizations**

**Example Output (Current):**
```markdown
## Advertising Costs Report

### Visualization Recommendations
📊 **Bar Chart**: Job board advertising costs by platform (Jan-Dec 2024)
📊 **Line Chart**: Monthly advertising spend trend over 12 months
📊 **Pie Chart**: Cost distribution across job boards

### Data Table
| Job Board | Total Cost | Jobs Posted |
|-----------|------------|-------------|
| Indeed    | £12,854    | 198         |
| Totaljobs | £6,541     | 156         |
...
```

**The Problem:**
- Users must manually create charts in Excel, Tableau, or PowerBI
- No embedded visualizations in the chat interface
- Limited interactivity and visual insight

---

## Solution Overview: 3 Approaches

### Approach 1: Python Visualization Libraries (Recommended)
**Best for:** Production-ready, high-quality charts with full control

### Approach 2: LLM Code Generation (GPT-4 Vision, Claude 3.5 Sonnet)
**Best for:** Dynamic, AI-generated charts with natural language

### Approach 3: Frontend Charting Libraries (Chart.js, Recharts)
**Best for:** Interactive web-based visualizations in the dashboard

---

## Approach 1: Python Visualization Libraries ⭐ RECOMMENDED

### Why This is Best

✅ **Production-Ready:** Battle-tested libraries with excellent output quality
✅ **Full Control:** Precise control over styling, colors, layouts
✅ **Fast:** Charts generated in <500ms without LLM overhead
✅ **Reliable:** No dependency on external API rate limits
✅ **Cost-Effective:** No additional API costs
✅ **Data Security:** All processing happens locally

### Libraries to Use

#### 1. **Matplotlib** (Industry Standard)
- **Best for:** Static publication-quality charts (PNG, SVG, PDF)
- **Pros:** Extremely flexible, extensive documentation, widely used
- **Cons:** Requires more code for styling

#### 2. **Plotly** (Best Choice) ⭐
- **Best for:** Interactive HTML charts with zoom, hover, pan
- **Pros:** Beautiful default styling, exports to HTML/PNG/SVG, interactive
- **Cons:** Larger file sizes for complex charts

#### 3. **Seaborn** (Statistical Plots)
- **Best for:** Complex statistical visualizations
- **Pros:** Built on Matplotlib, excellent for distributions and correlations
- **Cons:** Less control over styling

#### 4. **Altair** (Declarative)
- **Best for:** Quick, clean charts with minimal code
- **Pros:** Declarative syntax, beautiful defaults, Vega-Lite backend
- **Cons:** Less flexible for custom designs

### Recommended Stack: **Plotly**

**Why Plotly:**
1. Interactive HTML charts viewable in browsers
2. Can export to static PNG/SVG for reports
3. Beautiful defaults with minimal styling
4. Hover tooltips, zoom, pan built-in
5. Excellent documentation
6. Works seamlessly with Pandas DataFrames

### Implementation Example

```python
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

class VisualizationGenerator:
    """
    Generate chart visualizations from data.
    """

    def __init__(self, output_dir: str = "./generated_charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_bar_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        output_filename: str
    ) -> str:
        """
        Generate a bar chart from DataFrame.

        Args:
            data: Pandas DataFrame
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            title: Chart title
            output_filename: Output filename (without extension)

        Returns:
            Path to generated chart (HTML)
        """
        fig = px.bar(
            data,
            x=x_column,
            y=y_column,
            title=title,
            template='plotly_white',
            color=y_column,
            color_continuous_scale='Blues'
        )

        # Customize layout
        fig.update_layout(
            font=dict(size=14),
            title_font_size=18,
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title(),
            hovermode='x unified'
        )

        # Save as HTML (interactive)
        html_path = self.output_dir / f"{output_filename}.html"
        fig.write_html(html_path)

        # Also save as PNG (static, for reports)
        png_path = self.output_dir / f"{output_filename}.png"
        fig.write_image(png_path, width=1200, height=600)

        return str(html_path)

    def generate_line_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        output_filename: str
    ) -> str:
        """Generate a line chart from DataFrame."""
        fig = px.line(
            data,
            x=x_column,
            y=y_column,
            title=title,
            template='plotly_white',
            markers=True
        )

        fig.update_traces(line_color='#1f77b4', line_width=3)
        fig.update_layout(
            font=dict(size=14),
            title_font_size=18,
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title(),
            hovermode='x unified'
        )

        html_path = self.output_dir / f"{output_filename}.html"
        fig.write_html(html_path)

        png_path = self.output_dir / f"{output_filename}.png"
        fig.write_image(png_path, width=1200, height=600)

        return str(html_path)

    def generate_pie_chart(
        self,
        data: pd.DataFrame,
        names_column: str,
        values_column: str,
        title: str,
        output_filename: str
    ) -> str:
        """Generate a pie chart from DataFrame."""
        fig = px.pie(
            data,
            names=names_column,
            values=values_column,
            title=title,
            template='plotly_white',
            hole=0.3  # Donut chart
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font=dict(size=14),
            title_font_size=18
        )

        html_path = self.output_dir / f"{output_filename}.html"
        fig.write_html(html_path)

        png_path = self.output_dir / f"{output_filename}.png"
        fig.write_image(png_path, width=800, height=600)

        return str(html_path)


# Example Usage: Advertising Costs Report
def generate_advertising_report(csv_path: str):
    """
    Generate advertising costs report with charts.
    """
    # Load data
    df = pd.read_csv(csv_path)
    df['expense_date'] = pd.to_datetime(df['expense_date'])
    df['month'] = df['expense_date'].dt.to_period('M')

    # Initialize generator
    viz = VisualizationGenerator(output_dir="./reports/advertising_2024")

    # Chart 1: Total costs by job board
    costs_by_board = df.groupby('job_board')['amount'].sum().reset_index()
    costs_by_board = costs_by_board.sort_values('amount', ascending=False)

    chart1_path = viz.generate_bar_chart(
        data=costs_by_board,
        x_column='job_board',
        y_column='amount',
        title='Total Advertising Costs by Job Board (2024)',
        output_filename='costs_by_job_board'
    )

    # Chart 2: Monthly spending trend
    monthly_costs = df.groupby('month')['amount'].sum().reset_index()
    monthly_costs['month_str'] = monthly_costs['month'].astype(str)

    chart2_path = viz.generate_line_chart(
        data=monthly_costs,
        x_column='month_str',
        y_column='amount',
        title='Monthly Advertising Spend Trend (2024)',
        output_filename='monthly_trend'
    )

    # Chart 3: Cost distribution pie chart
    chart3_path = viz.generate_pie_chart(
        data=costs_by_board,
        names_column='job_board',
        values_column='amount',
        title='Advertising Cost Distribution by Platform (2024)',
        output_filename='cost_distribution'
    )

    return {
        'costs_by_board': chart1_path,
        'monthly_trend': chart2_path,
        'cost_distribution': chart3_path
    }
```

### Enhanced Report Generation Agent

```python
class ReportGenerationAgent(BaseAgent):
    """
    Enhanced Report Generation Agent with chart generation.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = Groq()
        self.viz_generator = VisualizationGenerator()

    async def _generate_report_with_charts(
        self,
        requirement: str,
        data_source: str = None
    ) -> Dict[str, Any]:
        """
        Generate report with actual charts.

        Returns:
            {
                'report_markdown': str,
                'charts': [
                    {'type': 'bar', 'path': 'chart1.html', 'title': '...'},
                    {'type': 'line', 'path': 'chart2.html', 'title': '...'}
                ]
            }
        """
        # Step 1: Identify data source
        if "advertising" in requirement.lower():
            csv_path = "finance_test_data/financial_records/11_job_board_advertising.csv"
            df = pd.read_csv(csv_path)
        else:
            # Handle other data sources
            pass

        # Step 2: Generate charts
        charts = []

        # Generate bar chart for costs by job board
        costs_by_board = df.groupby('job_board')['amount'].sum().reset_index()
        chart_path = self.viz_generator.generate_bar_chart(
            data=costs_by_board,
            x_column='job_board',
            y_column='amount',
            title='Total Advertising Costs by Job Board',
            output_filename='advertising_costs_bar'
        )
        charts.append({
            'type': 'bar',
            'path': chart_path,
            'title': 'Total Advertising Costs by Job Board',
            'description': 'Shows total spending across all job boards in 2024'
        })

        # Generate line chart for monthly trend
        df['month'] = pd.to_datetime(df['expense_date']).dt.to_period('M')
        monthly_costs = df.groupby('month')['amount'].sum().reset_index()
        monthly_costs['month_str'] = monthly_costs['month'].astype(str)

        chart_path = self.viz_generator.generate_line_chart(
            data=monthly_costs,
            x_column='month_str',
            y_column='amount',
            title='Monthly Advertising Spend Trend',
            output_filename='advertising_trend_line'
        )
        charts.append({
            'type': 'line',
            'path': chart_path,
            'title': 'Monthly Advertising Spend Trend',
            'description': 'Shows spending trends across all 12 months of 2024'
        })

        # Step 3: Generate markdown report (using LLM)
        report_markdown = await self._generate_report(requirement, None)

        # Step 4: Embed chart references in report
        report_with_charts = self._embed_chart_references(report_markdown, charts)

        return {
            'report_markdown': report_with_charts,
            'charts': charts
        }

    def _embed_chart_references(self, report: str, charts: List[Dict]) -> str:
        """
        Embed chart references into the markdown report.
        """
        chart_section = "\n\n## 📊 Interactive Visualizations\n\n"

        for i, chart in enumerate(charts, 1):
            chart_section += f"### {i}. {chart['title']}\n\n"
            chart_section += f"![{chart['title']}]({chart['path']})\n\n"
            chart_section += f"*{chart['description']}*\n\n"
            chart_section += f"[View Interactive Chart]({chart['path']})\n\n"

        # Insert after executive summary
        parts = report.split('## Key Metrics', 1)
        if len(parts) == 2:
            return parts[0] + chart_section + '## Key Metrics' + parts[1]
        else:
            return report + chart_section
```

### Installation

```bash
pip install plotly pandas kaleido
```

**Note:** `kaleido` is required for exporting static images (PNG/SVG)

---

## Approach 2: LLM Code Generation

### Models That Support Code Generation

#### 1. **GPT-4 with Code Interpreter** (OpenAI)
- ✅ Can generate Python code for Matplotlib/Plotly
- ✅ Executes code in sandboxed environment
- ✅ Returns generated charts as images
- ❌ Requires OpenAI API (not Groq/Anthropic)
- ❌ More expensive than text-only models

#### 2. **Claude 3.5 Sonnet with Artifacts** (Anthropic)
- ✅ Excellent at generating visualization code
- ✅ Can produce HTML/JavaScript charts
- ✅ Better at understanding data context
- ✅ Available via Anthropic API
- ❌ Requires manual code execution (not sandboxed)

#### 3. **Groq Models** (Current)
- ✅ Fast inference (100+ tokens/sec)
- ❌ Cannot execute code
- ❌ Can only suggest visualization code (not run it)

### Implementation with Claude 3.5 Sonnet

```python
from anthropic import Anthropic

class AIChartGenerator:
    """
    Generate charts using Claude 3.5 Sonnet code generation.
    """

    def __init__(self):
        self.client = Anthropic()

    async def generate_chart_from_prompt(
        self,
        data: pd.DataFrame,
        prompt: str
    ) -> str:
        """
        Generate chart code using Claude, then execute it.

        Args:
            data: Pandas DataFrame with data
            prompt: Natural language description of desired chart

        Returns:
            Path to generated chart
        """
        # Convert DataFrame to JSON for context
        data_json = data.to_json(orient='records', indent=2)

        system_prompt = """You are an expert data visualization specialist.
Given data and a visualization request, generate Python code using Plotly to create the chart.

Requirements:
- Use plotly.express or plotly.graph_objects
- Code must be self-contained and executable
- Save output as HTML file
- Include proper titles, labels, and styling
- Return only the Python code, no explanations
"""

        user_prompt = f"""Data (JSON format):
{data_json}

Visualization Request:
{prompt}

Generate Python code to create this visualization using Plotly."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Extract code from response
        code = self._extract_code_block(message.content[0].text)

        # Execute code in safe environment
        chart_path = self._execute_chart_code(code, data)

        return chart_path

    def _extract_code_block(self, response: str) -> str:
        """Extract Python code from markdown code blocks."""
        import re
        match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        if match:
            return match.group(1)
        return response

    def _execute_chart_code(self, code: str, data: pd.DataFrame) -> str:
        """
        Safely execute chart generation code.
        """
        # Create isolated namespace with data
        namespace = {
            'pd': pd,
            'px': px,
            'go': go,
            'df': data,
            '__builtins__': __builtins__
        }

        # Execute code
        exec(code, namespace)

        # Return path to generated file
        return namespace.get('output_path', './generated_chart.html')
```

**Pros:**
- Natural language to chart generation
- Highly flexible and adaptive
- Can handle complex requests

**Cons:**
- Slower (LLM inference + code execution)
- More expensive (Anthropic API costs)
- Code execution security concerns
- Less predictable output

---

## Approach 3: Frontend Charting Libraries

### Integration with React Dashboard

**Best Libraries:**

1. **Chart.js** - Simple, fast, canvas-based
2. **Recharts** - React-specific, composable
3. **Victory** - React Native compatible
4. **Apache ECharts** - Feature-rich, beautiful

### Implementation Example (Recharts)

```jsx
// frontend/components/ChartDisplay.jsx
import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';

export const ChartDisplay = ({ type, data, config }) => {
  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={config.xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey={config.yKey} fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={config.xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey={config.yKey} stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={data}
                dataKey={config.valueKey}
                nameKey={config.nameKey}
                cx="50%"
                cy="50%"
                outerRadius={150}
                fill="#8884d8"
                label
              />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return <div>Unknown chart type</div>;
    }
  };

  return (
    <div className="chart-container my-6 p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">{config.title}</h3>
      {renderChart()}
    </div>
  );
};
```

### Enhanced API Response with Chart Data

```javascript
// backend-api/server-fast.js - Enhanced response format
POST /api/chat

Response:
{
  "success": true,
  "message": "# Advertising Costs Report...",
  "metadata": {
    "agent": "report-generation",
    "has_visualizations": true,
    "charts": [
      {
        "id": "chart-1",
        "type": "bar",
        "title": "Costs by Job Board",
        "data": [
          {"job_board": "Indeed", "amount": 12854},
          {"job_board": "Totaljobs", "amount": 6541},
          {"job_board": "CV-Library", "amount": 5943}
        ],
        "config": {
          "xKey": "job_board",
          "yKey": "amount"
        }
      },
      {
        "id": "chart-2",
        "type": "line",
        "title": "Monthly Trend",
        "data": [
          {"month": "Jan", "amount": 3125},
          {"month": "Feb", "amount": 2085},
          ...
        ],
        "config": {
          "xKey": "month",
          "yKey": "amount"
        }
      }
    ]
  }
}
```

### Dashboard Integration

```jsx
// frontend/dashboard.jsx - Enhanced message rendering
const renderMessage = (message) => {
  if (message.type === 'ai' && message.metadata?.charts) {
    return (
      <div>
        {/* Markdown content */}
        <ReactMarkdown>{message.text}</ReactMarkdown>

        {/* Embedded charts */}
        {message.metadata.charts.map(chart => (
          <ChartDisplay
            key={chart.id}
            type={chart.type}
            data={chart.data}
            config={chart.config}
          />
        ))}
      </div>
    );
  }

  return <ReactMarkdown>{message.text}</ReactMarkdown>;
};
```

**Installation:**
```bash
cd frontend
npm install recharts
```

**Pros:**
- Interactive, responsive charts
- Rendered directly in chat interface
- No file exports needed
- Highly customizable

**Cons:**
- Requires frontend/backend coordination
- Chart data must be serialized in API response
- More complex implementation

---

## Comparison Matrix

| Feature | Python Libraries | LLM Code Gen | Frontend Libraries |
|---------|------------------|--------------|-------------------|
| **Implementation Complexity** | Medium | High | Medium |
| **Chart Quality** | Excellent | Variable | Excellent |
| **Interactivity** | Limited (HTML) | Limited | Excellent |
| **Speed** | Fast (<500ms) | Slow (2-5s) | Fast (<100ms) |
| **Cost** | Free | $$$ (API costs) | Free |
| **Flexibility** | High | Very High | High |
| **Data Security** | Secure (local) | Risk (code exec) | Secure |
| **Best Use Case** | Production reports | Exploratory analysis | Dashboard UI |

---

## Recommended Implementation Strategy

### Phase 1: Python Libraries (Quick Win) ⭐

**Timeline:** 2-3 days
**Effort:** Low-Medium
**Impact:** High

**Implementation:**
1. Install Plotly: `pip install plotly pandas kaleido`
2. Create `VisualizationGenerator` class
3. Enhance `ReportGenerationAgent` to detect data sources
4. Generate charts alongside markdown reports
5. Return chart paths in response metadata

**Pros:**
- Fast to implement
- Production-ready
- Reliable and predictable
- No additional API costs

### Phase 2: Frontend Integration (Best UX)

**Timeline:** 3-5 days
**Effort:** Medium
**Impact:** Very High

**Implementation:**
1. Install Recharts: `npm install recharts`
2. Create `ChartDisplay` component
3. Modify API response to include chart data
4. Update dashboard to render embedded charts
5. Add export functionality (PDF, PNG)

**Pros:**
- Best user experience
- Interactive charts
- No file management
- Responsive design

### Phase 3: LLM Code Generation (Advanced)

**Timeline:** 5-7 days
**Effort:** High
**Impact:** Medium

**Implementation:**
1. Integrate Claude 3.5 Sonnet for code generation
2. Build code execution sandbox
3. Add natural language chart requests
4. Implement chart customization interface

**Pros:**
- Ultimate flexibility
- Natural language control
- Handles edge cases

**Cons:**
- Security complexity
- Higher cost
- Less predictable

---

## Example: Advertising Costs Report

### Query
```
"Generate a report on advertising costs over the last year with a bar graph showing costs by job board"
```

### Output (Phase 1: Python Libraries)

**Response:**
```json
{
  "success": true,
  "message": "# Advertising Costs Report 2024\n\n## Executive Summary\n...",
  "metadata": {
    "agent": "report-generation",
    "charts": [
      {
        "type": "bar",
        "path": "./reports/advertising_2024/costs_by_job_board.html",
        "png_path": "./reports/advertising_2024/costs_by_job_board.png",
        "title": "Total Costs by Job Board"
      }
    ]
  }
}
```

**Generated Chart:** Interactive HTML file with bar graph

### Output (Phase 2: Frontend Integration)

**Response:**
```json
{
  "success": true,
  "message": "# Advertising Costs Report 2024\n\n...",
  "metadata": {
    "agent": "report-generation",
    "charts": [
      {
        "id": "chart-1",
        "type": "bar",
        "title": "Total Costs by Job Board",
        "data": [
          {"job_board": "Indeed", "amount": 12854, "jobs_posted": 198},
          {"job_board": "Totaljobs", "amount": 6541, "jobs_posted": 156},
          {"job_board": "Reed", "amount": 6257, "jobs_posted": 130},
          {"job_board": "CV-Library", "amount": 5943, "jobs_posted": 145},
          {"job_board": "Jobsite", "amount": 5062, "jobs_posted": 195},
          {"job_board": "Jobserve", "amount": 4119, "jobs_posted": 145}
        ],
        "config": {
          "xKey": "job_board",
          "yKey": "amount",
          "color": "#3b82f6"
        }
      }
    ]
  }
}
```

**Rendered:** Interactive bar chart embedded directly in chat interface

---

## Next Steps

### Immediate Actions

1. **Choose Implementation:** Start with Phase 1 (Python Libraries) for quick wins
2. **Install Dependencies:** `pip install plotly pandas kaleido`
3. **Create VisualizationGenerator class:** `utils/ai_router/visualization/generator.py`
4. **Enhance ReportGenerationAgent:** Add chart generation capability
5. **Test with advertising data:** Use `11_job_board_advertising.csv`

### Future Enhancements

- Add more chart types (scatter, heatmap, funnel, waterfall)
- Support multiple data sources (SQL databases, APIs, Excel)
- Implement chart customization (colors, themes, styles)
- Add export formats (PDF reports with embedded charts)
- Build chart template library for common reports

---

## Conclusion

✅ **Recommended Approach:** Python Libraries (Plotly) for Phase 1
✅ **Best UX:** Frontend Integration (Recharts) for Phase 2
✅ **Timeline:** 2-3 days for Phase 1, additional 3-5 days for Phase 2
✅ **Models:** No special LLM models required for Python/Frontend approaches
✅ **Cost:** Free (no additional API costs for Python/Frontend)

The current Groq LLM (llama-3-70b-8192) is perfectly suitable for generating report text. The visualization generation happens **outside** the LLM using dedicated charting libraries, which is faster, more reliable, and more cost-effective than LLM-based code generation.

---

**Last Updated:** 2025-10-23
**Recommended Start:** Phase 1 (Python Libraries with Plotly)
**Estimated Completion:** 2-3 days for working prototype
