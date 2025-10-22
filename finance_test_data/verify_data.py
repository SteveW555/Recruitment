"""
Quick verification and summary of generated financial test data
"""

import csv
from pathlib import Path

output_dir = Path("d:/Recruitment/test_data/financial_records")

files = sorted(output_dir.glob("*.csv"))

print("\n" + "="*80)
print("PROACTIVE PEOPLE - FINANCIAL TEST DATA SUMMARY")
print("="*80)
print(f"\nTotal CSV Files Generated: {len(files)}")
print(f"Directory: {output_dir}\n")

total_records = 0
total_revenue_records = 0
total_cost_records = 0

print(f"{'File':<50} {'Records':<10} {'Category'}")
print("-" * 80)

for file in files:
    with open(file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        row_count = sum(1 for row in reader)
        total_records += row_count

        # Determine category
        if any(x in file.name for x in ['invoice', 'consultancy', 'training', 'wellbeing', 'assessment']):
            category = "REVENUE"
            total_revenue_records += row_count
        else:
            category = "COST"
            total_cost_records += row_count

        print(f"{file.name:<50} {row_count:<10} {category}")

print("-" * 80)
print(f"{'TOTAL':<50} {total_records:<10}")
print(f"\n  Revenue Records: {total_revenue_records}")
print(f"  Cost Records: {total_cost_records}")
print("\n" + "="*80)

# Show sample from first file
print("\nSAMPLE DATA (First 3 records from permanent_placement_invoices.csv):")
print("-" * 80)

with open(output_dir / "01_permanent_placement_invoices.csv", 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 3:
            break
        print(f"\nRecord {i+1}:")
        for key, value in list(row.items())[:8]:  # Show first 8 fields
            print(f"  {key}: {value}")

print("\n" + "="*80)
print("[SUCCESS] All files verified and loaded successfully!")
print("="*80 + "\n")
