"""
CLI Test Tool for Postcodes.io Distance Calculator

Interactive command-line interface for testing postcode lookup and distance calculations.

Usage:
    python test_postcodesio_cli.py
    python test_postcodesio_cli.py --postcode1 "BS1 4DJ" --postcode2 "SW1A 1AA"
    python test_postcodesio_cli.py --bulk "BS1 4DJ,M1 1AA,EH1 1YZ"

Author: ProActive People
Created: 2025-11-01
"""

import argparse
import sys
from typing import List
from postcodesio import PostcodesIOClient, DistanceCalculator, PostcodeLocation, PostcodeDetails


class PostcodeCliTester:
    """CLI interface for testing postcode operations."""

    def __init__(self):
        self.client = PostcodesIOClient(use_cache=True)
        self.calculator = DistanceCalculator()

    def print_header(self, text: str):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)

    def print_section(self, text: str):
        """Print a formatted section header."""
        print(f"\n--- {text} ---")

    def display_location(self, location: PostcodeLocation, indent: str = "  "):
        """Display location information in a formatted way."""
        print(f"{indent}Postcode:  {location.postcode}")
        print(f"{indent}Latitude:  {location.latitude}")
        print(f"{indent}Longitude: {location.longitude}")
        if location.district:
            print(f"{indent}District:  {location.district}")
        if location.region:
            print(f"{indent}Region:    {location.region}")
        if location.country:
            print(f"{indent}Country:   {location.country}")

    def test_single_lookup(self, postcode: str):
        """Test single postcode lookup."""
        self.print_section(f"Single Postcode Lookup: {postcode}")

        try:
            location = self.client.lookup_postcode(postcode)

            if location:
                self.display_location(location)
                print(f"\n  [OK] Lookup successful")
            else:
                print(f"  [X] Postcode not found: {postcode}")

        except ValueError as e:
            print(f"  [X] Validation Error: {e}")
        except Exception as e:
            print(f"  [X] Error: {e}")

    def test_postcode_details(self, postcode: str):
        """Test detailed postcode lookup including town/city information."""
        self.print_section(f"Detailed Postcode Information: {postcode}")

        try:
            details = self.client.get_postcode_details(postcode)

            if details:
                print(f"\n  GENERAL INFORMATION:")
                print(f"  {'-' * 60}")
                print(f"  Postcode:          {details.postcode}")
                print(f"  Town/City:         {details.town or 'N/A'}")
                print(f"  Coordinates:       {details.latitude}, {details.longitude}")

                print(f"\n  ADMINISTRATIVE AREAS:")
                print(f"  {'-' * 60}")
                print(f"  Admin District:    {details.admin_district or 'N/A'}")
                print(f"  Admin County:      {details.admin_county or 'N/A'}")
                print(f"  Admin Ward:        {details.admin_ward or 'N/A'}")
                print(f"  Parish:            {details.parish or 'N/A'}")

                print(f"\n  GEOGRAPHIC REGIONS:")
                print(f"  {'-' * 60}")
                print(f"  Region:            {details.region or 'N/A'}")
                print(f"  Country:           {details.country or 'N/A'}")

                print(f"\n  POLITICAL:")
                print(f"  {'-' * 60}")
                print(f"  Constituency:      {details.parliamentary_constituency or 'N/A'}")

                if details.ccg or details.nhs_ha:
                    print(f"\n  NHS:")
                    print(f"  {'-' * 60}")
                    if details.ccg:
                        print(f"  CCG:               {details.ccg}")
                    if details.nhs_ha:
                        print(f"  NHS HA:            {details.nhs_ha}")

                print(f"\n  COORDINATES:")
                print(f"  {'-' * 60}")
                print(f"  Eastings:          {details.eastings or 'N/A'}")
                print(f"  Northings:         {details.northings or 'N/A'}")
                print(f"  Quality:           {details.quality or 'N/A'}/9")

                print(f"\n  [OK] Details retrieved successfully")
            else:
                print(f"  [X] Postcode not found: {postcode}")

        except ValueError as e:
            print(f"  [X] Validation Error: {e}")
        except Exception as e:
            print(f"  [X] Error: {e}")

    def test_distance(self, postcode1: str, postcode2: str, unit: str = 'km'):
        """Test distance calculation between two postcodes."""
        self.print_section(f"Distance Calculation: {postcode1} <-> {postcode2}")

        try:
            # Lookup both postcodes
            print("\n  Looking up first postcode...")
            loc1 = self.client.lookup_postcode(postcode1)

            if not loc1:
                print(f"  [X] First postcode not found: {postcode1}")
                return

            print(f"  [OK] {loc1.postcode}: {loc1.region}, {loc1.country}")

            print("\n  Looking up second postcode...")
            loc2 = self.client.lookup_postcode(postcode2)

            if not loc2:
                print(f"  [X] Second postcode not found: {postcode2}")
                return

            print(f"  [OK] {loc2.postcode}: {loc2.region}, {loc2.country}")

            # Calculate distances
            distance_km = self.calculator.haversine_distance(
                loc1.latitude, loc1.longitude,
                loc2.latitude, loc2.longitude,
                unit='km'
            )

            distance_miles = self.calculator.haversine_distance(
                loc1.latitude, loc1.longitude,
                loc2.latitude, loc2.longitude,
                unit='miles'
            )

            print("\n  DISTANCE RESULTS:")
            print(f"  {'-' * 40}")
            print(f"  From:      {loc1.postcode} ({loc1.region})")
            print(f"  To:        {loc2.postcode} ({loc2.region})")
            print(f"  Distance:  {distance_km:.2f} km")
            print(f"             {distance_miles:.2f} miles")
            print(f"  {'-' * 40}")

        except ValueError as e:
            print(f"  [X] Validation Error: {e}")
        except Exception as e:
            print(f"  [X] Error: {e}")

    def test_bulk_lookup(self, postcodes: List[str]):
        """Test bulk postcode lookup."""
        self.print_section(f"Bulk Lookup: {len(postcodes)} postcodes")

        if len(postcodes) > 100:
            print(f"  [X] Error: Maximum 100 postcodes allowed (provided: {len(postcodes)})")
            return

        try:
            results = self.client.bulk_lookup(postcodes)

            print(f"\n  Results:")
            print(f"  {'-' * 66}")

            found = 0
            not_found = 0

            for postcode, location in results.items():
                if location:
                    found += 1
                    region = location.region or "N/A"
                    country = location.country or "N/A"
                    print(f"  [OK] {postcode:10s} | {region:20s} | {country}")
                else:
                    not_found += 1
                    print(f"  [X] {postcode:10s} | NOT FOUND")

            print(f"  {'-' * 66}")
            print(f"  Summary: {found} found, {not_found} not found")

        except Exception as e:
            print(f"  [X] Error: {e}")

    def test_distance_matrix(self, base_postcode: str, target_postcodes: List[str]):
        """Calculate distances from one postcode to multiple others."""
        self.print_section(f"Distance Matrix from {base_postcode}")

        try:
            base_location = self.client.lookup_postcode(base_postcode)

            if not base_location:
                print(f"  [X] Base postcode not found: {base_postcode}")
                return

            print(f"\n  Base Location: {base_location.postcode}")
            print(f"  Region: {base_location.region}, {base_location.country}")
            print(f"\n  Distances:")
            print(f"  {'-' * 66}")

            for target in target_postcodes:
                distance = DistanceCalculator.postcode_distance(
                    base_postcode,
                    target,
                    unit='km',
                    client=self.client
                )

                if distance is not None:
                    # Also get target location for region info
                    target_loc = self.client.lookup_postcode(target)
                    region = target_loc.region if target_loc else "Unknown"
                    print(f"  {target:10s} -> {distance:7.2f} km  ({region})")
                else:
                    print(f"  {target:10s} -> NOT FOUND")

            print(f"  {'-' * 66}")

        except Exception as e:
            print(f"  [X] Error: {e}")

    def interactive_mode(self):
        """Run in interactive mode with menu."""
        self.print_header("Postcodes.io CLI Test Tool - Interactive Mode")

        while True:
            print("\n" + "-" * 70)
            print("  Options:")
            print("  1. Lookup single postcode")
            print("  2. Get detailed postcode information (town/city data)")
            print("  3. Calculate distance between two postcodes")
            print("  4. Bulk lookup multiple postcodes")
            print("  5. Distance matrix (one to many)")
            print("  6. Run comprehensive test suite")
            print("  0. Exit")
            print("-" * 70)

            choice = input("\n  Enter choice (0-6): ").strip()

            if choice == "0":
                print("\n  Goodbye!")
                break

            elif choice == "1":
                postcode = input("  Enter postcode: ").strip()
                if postcode:
                    self.test_single_lookup(postcode)

            elif choice == "2":
                postcode = input("  Enter postcode: ").strip()
                if postcode:
                    self.test_postcode_details(postcode)

            elif choice == "3":
                postcode1 = input("  Enter first postcode: ").strip()
                postcode2 = input("  Enter second postcode: ").strip()
                if postcode1 and postcode2:
                    self.test_distance(postcode1, postcode2)

            elif choice == "4":
                postcodes_str = input("  Enter postcodes (comma-separated): ").strip()
                if postcodes_str:
                    postcodes = [pc.strip() for pc in postcodes_str.split(",")]
                    self.test_bulk_lookup(postcodes)

            elif choice == "5":
                base = input("  Enter base postcode: ").strip()
                targets_str = input("  Enter target postcodes (comma-separated): ").strip()
                if base and targets_str:
                    targets = [pc.strip() for pc in targets_str.split(",")]
                    self.test_distance_matrix(base, targets)

            elif choice == "6":
                self.run_comprehensive_tests()

            else:
                print("  [X] Invalid choice. Please enter 0-6.")

    def run_comprehensive_tests(self):
        """Run a comprehensive test suite."""
        self.print_header("Comprehensive Test Suite")

        # Test 1: ProActive People office (Bristol)
        self.test_single_lookup("BS1 4DJ")

        # Test 2: Distance calculations
        test_pairs = [
            ("BS1 4DJ", "SW1A 1AA"),  # Bristol to London
            ("BS1 4DJ", "CF10 1EP"),  # Bristol to Cardiff
            ("BS1 4DJ", "EH1 1YZ"),   # Bristol to Edinburgh
        ]

        for pc1, pc2 in test_pairs:
            self.test_distance(pc1, pc2)

        # Test 3: Bulk lookup
        major_cities = [
            "BS1 4DJ",   # Bristol
            "SW1A 1AA",  # London
            "M1 1AA",    # Manchester (may not exist)
            "B1 1AA",    # Birmingham
            "EH1 1YZ",   # Edinburgh
            "CF10 1EP",  # Cardiff
            "G1 1AA",    # Glasgow
        ]
        self.test_bulk_lookup(major_cities)

        # Test 4: Distance matrix
        self.test_distance_matrix("BS1 4DJ", ["SW1A 1AA", "CF10 1EP", "EH1 1YZ", "B1 1AA"])

        print("\n" + "=" * 70)
        print("  Comprehensive test suite completed!")
        print("=" * 70 + "\n")


def main():
    """Main entry point for CLI tool."""
    parser = argparse.ArgumentParser(
        description="CLI Test Tool for Postcodes.io Distance Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python test_postcodesio_cli.py

  # Single postcode lookup
  python test_postcodesio_cli.py --lookup "BS1 4DJ"

  # Get detailed postcode information (town/city)
  python test_postcodesio_cli.py --details "DY11 6LF"

  # Calculate distance
  python test_postcodesio_cli.py --postcode1 "BS1 4DJ" --postcode2 "SW1A 1AA"

  # Bulk lookup
  python test_postcodesio_cli.py --bulk "BS1 4DJ,SW1A 1AA,M1 1AA"

  # Distance matrix
  python test_postcodesio_cli.py --matrix "BS1 4DJ" --targets "SW1A 1AA,CF10 1EP,EH1 1YZ"

  # Run comprehensive tests
  python test_postcodesio_cli.py --test-suite
        """
    )

    parser.add_argument(
        "--lookup",
        type=str,
        help="Lookup a single postcode"
    )

    parser.add_argument(
        "--details",
        type=str,
        help="Get detailed information about a postcode (town/city, administrative areas, etc.)"
    )

    parser.add_argument(
        "--postcode1",
        type=str,
        help="First postcode for distance calculation"
    )

    parser.add_argument(
        "--postcode2",
        type=str,
        help="Second postcode for distance calculation"
    )

    parser.add_argument(
        "--bulk",
        type=str,
        help="Comma-separated list of postcodes for bulk lookup"
    )

    parser.add_argument(
        "--matrix",
        type=str,
        help="Base postcode for distance matrix"
    )

    parser.add_argument(
        "--targets",
        type=str,
        help="Comma-separated target postcodes for distance matrix (requires --matrix)"
    )

    parser.add_argument(
        "--test-suite",
        action="store_true",
        help="Run comprehensive test suite"
    )

    parser.add_argument(
        "--unit",
        type=str,
        choices=["km", "miles"],
        default="km",
        help="Distance unit (default: km)"
    )

    args = parser.parse_args()

    tester = PostcodeCliTester()

    # Determine mode based on arguments
    if args.test_suite:
        tester.run_comprehensive_tests()

    elif args.lookup:
        tester.print_header("Single Postcode Lookup")
        tester.test_single_lookup(args.lookup)

    elif args.details:
        tester.print_header("Detailed Postcode Information")
        tester.test_postcode_details(args.details)

    elif args.postcode1 and args.postcode2:
        tester.print_header("Distance Calculation")
        tester.test_distance(args.postcode1, args.postcode2, args.unit)

    elif args.bulk:
        postcodes = [pc.strip() for pc in args.bulk.split(",")]
        tester.print_header("Bulk Postcode Lookup")
        tester.test_bulk_lookup(postcodes)

    elif args.matrix and args.targets:
        targets = [pc.strip() for pc in args.targets.split(",")]
        tester.print_header("Distance Matrix")
        tester.test_distance_matrix(args.matrix, targets)

    else:
        # No arguments provided, run interactive mode
        tester.interactive_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n  [X] Fatal Error: {e}")
        sys.exit(1)
