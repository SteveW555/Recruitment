# Recruitment Fake Data Generator Skill

Generate realistic test data for recruitment automation systems with UK-specific formatting.

## Quick Start

### Generate Everything (Recommended)
```bash
python scripts/generate_all.py --count 50 --output-dir ./test_data
```

### Generate Individual Data Types

#### Clients
```bash
python scripts/generate_clients.py --count 100 --output fake_clients.csv
```

#### Candidates
```bash
python scripts/generate_candidates.py --count 200 --output fake_candidates.csv
```

#### Jobs (with client linkage)
```bash
python scripts/generate_jobs.py --count 150 --clients fake_clients.csv --output fake_jobs.csv
```

#### Placements (with full linkage)
```bash
python scripts/generate_placements.py --count 80 \
  --candidates fake_candidates.csv \
  --jobs fake_jobs.csv \
  --clients fake_clients.csv \
  --output fake_placements.csv
```

### With Sector Filtering
```bash
python scripts/generate_all.py --count 50 --sectors "Technical,Sales" --output-dir ./tech_sales_data
```

## Available Scripts

- **generate_clients.py** - Generate fake client/company records ✓ Complete
- **generate_candidates.py** - Generate fake candidate profiles ✓ Complete
- **generate_jobs.py** - Generate fake job postings ✓ Complete
- **generate_placements.py** - Generate fake placement records ✓ Complete
- **generate_all.py** - Generate all data types with referential integrity ✓ Complete

## Features

- UK-specific data (postcodes, phone numbers, addresses)
- Bristol-focused locations
- ProActive People business model alignment
- Realistic company sizes, revenues, and placement histories
- Proper referential integrity
- Customizable record counts and sector filtering

## Output Format

CSV files with UTF-8 encoding, matching the ProActive People data schema.

## Installation

No external dependencies required - uses Python standard library only.

## Requirements

- Python 3.7+
- Standard library modules: csv, random, datetime, argparse

## Example Output

See `assets/sample_output/` for example generated CSV files.

## Documentation

- `SKILL.md` - Complete skill documentation and usage instructions
- `references/uk_data.md` - UK-specific data patterns and formats
- `references/schema_definitions.md` - Complete field definitions
- `references/industry_sectors.md` - ProActive People business domains

## License

Proprietary - ProActive People Ltd.
