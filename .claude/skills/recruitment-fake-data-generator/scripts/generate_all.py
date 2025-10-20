#!/usr/bin/env python3
"""
Orchestrator script to generate complete recruitment database with referential integrity.
Generates clients, candidates, jobs, and placements in the correct order.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name: str, args: list, description: str):
    """Run a generation script with arguments."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name

    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"ERROR: {script_name} failed with return code {result.returncode}")
        sys.exit(1)

    print(f"[OK] {description} completed successfully")

def main():
    parser = argparse.ArgumentParser(
        description="Generate complete recruitment database with referential integrity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 25 of each record type
  python generate_all.py --count 25 --output-dir ./test_data

  # Generate 50 records with specific sectors
  python generate_all.py --count 50 --sectors "Technical,Sales" --output-dir ./data

  # Generate different counts for each type
  python generate_all.py --clients 100 --candidates 200 --jobs 150 --placements 80 --output-dir ./data
        """
    )

    parser.add_argument("--count", type=int, default=25,
                       help="Number of each record type to generate (default: 25)")
    parser.add_argument("--clients", type=int,
                       help="Number of clients (overrides --count)")
    parser.add_argument("--candidates", type=int,
                       help="Number of candidates (overrides --count)")
    parser.add_argument("--jobs", type=int,
                       help="Number of jobs (overrides --count)")
    parser.add_argument("--placements", type=int,
                       help="Number of placements (overrides --count)")
    parser.add_argument("--output-dir", type=str, default=".",
                       help="Output directory for CSV files (default: current directory)")
    parser.add_argument("--sectors", type=str,
                       help="Comma-separated sectors filter (e.g., 'Technical,Sales')")

    args = parser.parse_args()

    # Determine counts
    client_count = args.clients if args.clients else args.count
    candidate_count = args.candidates if args.candidates else args.count
    job_count = args.jobs if args.jobs else args.count
    placement_count = args.placements if args.placements else args.count

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("RECRUITMENT DATABASE GENERATOR")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Clients:     {client_count}")
    print(f"  Candidates:  {candidate_count}")
    print(f"  Jobs:        {job_count}")
    print(f"  Placements:  {placement_count}")
    print(f"  Output Dir:  {output_dir.absolute()}")
    if args.sectors:
        print(f"  Sectors:     {args.sectors}")
    print()

    # Define output files
    clients_file = output_dir / "clients.csv"
    candidates_file = output_dir / "candidates.csv"
    jobs_file = output_dir / "jobs.csv"
    placements_file = output_dir / "placements.csv"

    # Step 1: Generate Clients
    client_args = [
        "--count", str(client_count),
        "--output", str(clients_file)
    ]
    if args.sectors:
        client_args.extend(["--sectors", args.sectors])

    run_script("generate_clients.py", client_args, "Step 1/4: Generating Clients")

    # Step 2: Generate Candidates
    candidate_args = [
        "--count", str(candidate_count),
        "--output", str(candidates_file)
    ]
    if args.sectors:
        candidate_args.extend(["--sectors", args.sectors])

    run_script("generate_candidates.py", candidate_args, "Step 2/4: Generating Candidates")

    # Step 3: Generate Jobs (linked to clients)
    job_args = [
        "--count", str(job_count),
        "--clients", str(clients_file),
        "--output", str(jobs_file)
    ]
    if args.sectors:
        job_args.extend(["--sectors", args.sectors])

    run_script("generate_jobs.py", job_args, "Step 3/4: Generating Jobs")

    # Step 4: Generate Placements (linked to candidates, jobs, and clients)
    placement_args = [
        "--count", str(placement_count),
        "--candidates", str(candidates_file),
        "--jobs", str(jobs_file),
        "--clients", str(clients_file),
        "--output", str(placements_file)
    ]

    run_script("generate_placements.py", placement_args, "Step 4/4: Generating Placements")

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE!")
    print(f"{'='*60}")
    print(f"\nGenerated files in: {output_dir.absolute()}")
    print(f"  - {clients_file.name}")
    print(f"  - {candidates_file.name}")
    print(f"  - {jobs_file.name}")
    print(f"  - {placements_file.name}")
    print(f"\nAll data has referential integrity:")
    print(f"  - Jobs reference Clients")
    print(f"  - Placements reference Candidates, Jobs, and Clients")
    print(f"\nReady to import into your recruitment system!")
    print()

if __name__ == "__main__":
    main()
