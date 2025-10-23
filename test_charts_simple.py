"""
Simple Chart Generation Test - No emojis for Windows compatibility.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.ai_router.visualization.chart_generator import ChartGenerator
import pandas as pd


def main():
    print("\n" + "="*80)
    print("CHART GENERATION TEST")
    print("="*80 + "\n")

    # Load data
    csv_path = "finance_test_data/financial_records/11_job_board_advertising.csv"

    if not Path(csv_path).exists():
        print(f"[ERROR] Data file not found: {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    print(f"[OK] Loaded data: {len(df)} records\n")

    # Initialize generator
    gen = ChartGenerator(output_dir="./test_charts")
    print(f"[OK] ChartGenerator initialized\n")

    # Test 1: Bar Chart
    print("[TEST] Generating Bar Chart...")
    costs_by_board = df.groupby('job_board')['amount'].sum().reset_index()
    costs_by_board = costs_by_board.sort_values('amount', ascending=False)

    chart1 = gen.bar_chart(
        data=costs_by_board,
        x_column='job_board',
        y_column='amount',
        title='Advertising Costs by Job Board',
        output_filename='test_bar_chart'
    )
    print(f"  [OK] Bar chart: {chart1['html_path']}\n")

    # Test 2: Line Chart
    print("[TEST] Generating Line Chart...")
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
    print(f"  [OK] Line chart: {chart2['html_path']}\n")

    # Test 3: Pie Chart
    print("[TEST] Generating Pie Chart...")
    chart3 = gen.pie_chart(
        data=costs_by_board,
        names_column='job_board',
        values_column='amount',
        title='Cost Distribution by Platform',
        output_filename='test_pie_chart'
    )
    print(f"  [OK] Pie chart: {chart3['html_path']}\n")

    # Verify files
    print("[VERIFY] Checking files...")
    all_exist = True
    for chart in [chart1, chart2, chart3]:
        exists = Path(chart['html_path']).exists()
        status = "[OK]" if exists else "[FAIL]"
        print(f"  {status} {Path(chart['html_path']).name}")
        if not exists:
            all_exist = False

    print("\n" + "="*80)
    if all_exist:
        print("[SUCCESS] All 3 charts generated successfully!")
        print("\nGenerated files in ./test_charts/:")
        print("  - test_bar_chart.html")
        print("  - test_line_chart.html")
        print("  - test_pie_chart.html")
        print("\nOpen these files in your browser to view interactive charts.")
    else:
        print("[FAIL] Some charts failed to generate")

    print("="*80 + "\n")

    return all_exist


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
