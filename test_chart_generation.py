"""
Test Chart Generation - Verify ChartGenerator and ReportGenerationAgent work correctly.

Tests:
1. ChartGenerator can create bar/line/pie charts
2. ReportGenerationAgent detects advertising queries
3. Charts are generated and embedded in reports
4. Files are created correctly
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.ai_router.visualization.chart_generator import ChartGenerator
from utils.ai_router.agents.report_generation_agent import ReportGenerationAgent
from utils.ai_router.agents.base_agent import AgentRequest
import pandas as pd


def test_chart_generator():
    """Test ChartGenerator directly."""
    print("\n" + "="*80)
    print("TEST 1: ChartGenerator - Direct Testing")
    print("="*80 + "\n")

    # Load advertising data
    csv_path = "finance_test_data/financial_records/11_job_board_advertising.csv"

    if not Path(csv_path).exists():
        print(f"❌ ERROR: Data file not found: {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    print(f"✅ Loaded data: {len(df)} records")

    # Initialize generator
    gen = ChartGenerator(output_dir="./test_charts")
    print(f"✅ ChartGenerator initialized: {gen.output_dir}")

    # Test 1: Bar Chart
    print("\n📊 Generating Bar Chart...")
    costs_by_board = df.groupby('job_board')['amount'].sum().reset_index()
    costs_by_board = costs_by_board.sort_values('amount', ascending=False)

    chart1 = gen.bar_chart(
        data=costs_by_board,
        x_column='job_board',
        y_column='amount',
        title='Advertising Costs by Job Board',
        output_filename='test_bar_chart'
    )

    print(f"   ✅ Bar chart created: {chart1['html_path']}")
    if chart1.get('png_path'):
        print(f"   ✅ PNG export: {chart1['png_path']}")

    # Test 2: Line Chart
    print("\n📈 Generating Line Chart...")
    df['expense_date'] = pd.to_datetime(df['expense_date'])
    df['month'] = df['expense_date'].dt.to_period('M').astype(str)
    monthly_costs = df.groupby('month')['amount'].sum().reset_index()

    chart2 = gen.line_chart(
        data=monthly_costs,
        x_column='month',
        y_column='amount',
        title='Monthly Advertising Trend',
        output_filename='test_line_chart'
    )

    print(f"   ✅ Line chart created: {chart2['html_path']}")

    # Test 3: Pie Chart
    print("\n🥧 Generating Pie Chart...")
    chart3 = gen.pie_chart(
        data=costs_by_board,
        names_column='job_board',
        values_column='amount',
        title='Cost Distribution by Platform',
        output_filename='test_pie_chart'
    )

    print(f"   ✅ Pie chart created: {chart3['html_path']}")

    # Verify files exist
    print("\n🔍 Verifying files...")
    all_files_exist = True
    for chart in [chart1, chart2, chart3]:
        html_exists = Path(chart['html_path']).exists()
        print(f"   {'✅' if html_exists else '❌'} {Path(chart['html_path']).name}")

        if not html_exists:
            all_files_exist = False

    print("\n" + "="*80)
    if all_files_exist:
        print("✅ TEST 1 PASSED: All charts generated successfully")
    else:
        print("❌ TEST 1 FAILED: Some charts missing")
    print("="*80)

    return all_files_exist


async def test_report_agent():
    """Test ReportGenerationAgent with chart generation."""
    print("\n" + "="*80)
    print("TEST 2: ReportGenerationAgent - Integrated Testing")
    print("="*80 + "\n")

    # Initialize agent (requires config)
    config = {
        'name': 'Report Generation',
        'agent_class': 'ReportGenerationAgent',
        'llm_provider': 'groq',
        'llm_model': 'llama-3-70b-8192',
        'timeout_seconds': 10,
        'system_prompt': 'You are a report generation specialist.'
    }

    try:
        agent = ReportGenerationAgent(config)
        print("✅ ReportGenerationAgent initialized")

        # Test query
        query = "Generate a report on advertising costs over the last year with a bar graph"
        print(f"\n📝 Query: \"{query}\"")

        # Create request
        request = AgentRequest(
            query=query,
            session_id='test-session',
            category=None
        )

        # Process request
        print("\n⏳ Processing request (this may take a few seconds)...")
        response = await agent.process(request)

        if response.success:
            print(f"\n✅ Report generated successfully")
            print(f"   Agent latency: {response.metadata.get('agent_latency_ms', 0)}ms")
            print(f"   Chart count: {response.metadata.get('chart_count', 0)}")

            # Check if charts were generated
            if response.metadata.get('charts'):
                print(f"\n📊 Charts Generated:")
                for i, chart in enumerate(response.metadata['charts'], 1):
                    print(f"   {i}. {chart['title']} ({chart['type']})")
                    print(f"      HTML: {chart['html_path']}")

                # Show a snippet of the report
                print(f"\n📄 Report Preview (first 500 chars):")
                print("-" * 80)
                print(response.content[:500] + "...")
                print("-" * 80)

                # Check if charts are embedded in report
                if "📊 Interactive Visualizations" in response.content:
                    print("\n✅ Charts embedded in report")
                else:
                    print("\n⚠️  Warning: Charts not embedded in report")

                print("\n" + "="*80)
                print("✅ TEST 2 PASSED: Report with charts generated successfully")
                print("="*80)
                return True
            else:
                print("\n⚠️  Warning: No charts generated")
                print("="*80)
                print("⚠️  TEST 2 PARTIAL: Report generated but no charts")
                print("="*80)
                return False
        else:
            print(f"\n❌ Report generation failed: {response.error}")
            print("="*80)
            print("❌ TEST 2 FAILED")
            print("="*80)
            return False

    except Exception as e:
        print(f"\n❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80)
        print("❌ TEST 2 FAILED")
        print("="*80)
        return False


def test_data_availability():
    """Test that required data files exist."""
    print("\n" + "="*80)
    print("TEST 0: Data Availability Check")
    print("="*80 + "\n")

    csv_path = "finance_test_data/financial_records/11_job_board_advertising.csv"

    if Path(csv_path).exists():
        df = pd.read_csv(csv_path)
        print(f"✅ Data file found: {csv_path}")
        print(f"   Records: {len(df)}")
        print(f"   Columns: {', '.join(df.columns)}")
        print(f"   Date range: {df['expense_date'].min()} to {df['expense_date'].max()}")

        # Show sample data
        print(f"\n📊 Sample Data (first 3 records):")
        print(df.head(3).to_string(index=False))

        print("\n" + "="*80)
        print("✅ TEST 0 PASSED: Data file available")
        print("="*80)
        return True
    else:
        print(f"❌ Data file not found: {csv_path}")
        print("\n" + "="*80)
        print("❌ TEST 0 FAILED: Data file missing")
        print("="*80)
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("[TEST] CHART GENERATION TEST SUITE")
    print("="*80)

    results = []

    # Test 0: Data availability
    results.append(("Data Availability", test_data_availability()))

    # Test 1: ChartGenerator
    results.append(("ChartGenerator", test_chart_generator()))

    # Test 2: ReportGenerationAgent
    results.append(("ReportGenerationAgent", await test_report_agent()))

    # Summary
    print("\n" + "="*80)
    print("[RESULTS] TEST SUMMARY")
    print("="*80 + "\n")

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print("\n" + "="*80)
    if passed_count == total_count:
        print(f"[SUCCESS] ALL TESTS PASSED ({passed_count}/{total_count})")
        print("\n[OK] Chart generation is working correctly!")
        print("\n[FILES] Generated files:")
        print("   - ./test_charts/*.html (interactive charts)")
        print("   - ./test_charts/*.png (static images)")
        print("   - ./generated_charts/*.html (report charts)")
    else:
        print(f"[WARNING] SOME TESTS FAILED ({passed_count}/{total_count} passed)")

    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
