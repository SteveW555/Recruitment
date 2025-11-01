"""
Simple example demonstrating how to get town/city information from postcodes.

This script shows how to use the get_postcode_details() function to retrieve
detailed information about UK postcodes, including town/city names.

Author: ProActive People
Created: 2025-11-01
"""

from postcodesio import PostcodesIOClient

def main():
    """Demonstrate town/city lookup from postcodes."""

    # Initialize the client
    client = PostcodesIOClient()

    # Example postcodes to lookup
    test_postcodes = [
        "DY11 6LF",   # Kidderminster
        "BS1 4DJ",    # Bristol (ProActive People office)
        "SW1A 1AA",   # Westminster, London
        "M1 1AE",     # Manchester
        "EH1 1YZ",    # Edinburgh
    ]

    print("=" * 70)
    print("Town/City Lookup from Postcodes")
    print("=" * 70)

    for postcode in test_postcodes:
        print(f"\n{postcode}:")

        try:
            # Get detailed postcode information
            details = client.get_postcode_details(postcode)

            if details:
                # Access the town property (automatically extracted)
                print(f"  Town/City:     {details.town}")
                print(f"  District:      {details.admin_district}")
                print(f"  County:        {details.admin_county or 'N/A'}")
                print(f"  Region:        {details.region}")
                print(f"  Country:       {details.country}")
                print(f"  Constituency:  {details.parliamentary_constituency}")

                # You can also use the __str__ method for a quick summary
                print(f"  Summary:       {details}")
            else:
                print(f"  [Not Found]")

        except ValueError as e:
            print(f"  [Error] {e}")
        except Exception as e:
            print(f"  [Error] {e}")

    print("\n" + "=" * 70)
    print("Example: Using town data in candidate matching")
    print("=" * 70)

    # Example use case: Check if candidate is in the same town as job
    candidate_postcode = "BS1 4DJ"
    job_postcode = "BS2 0JA"  # Another Bristol postcode

    candidate_details = client.get_postcode_details(candidate_postcode)
    job_details = client.get_postcode_details(job_postcode)

    if candidate_details and job_details:
        print(f"\nCandidate location: {candidate_details.town}")
        print(f"Job location:       {job_details.town}")

        if candidate_details.town == job_details.town:
            print("Result: Candidate is in the same town as job location!")
        else:
            print("Result: Different towns - may need to check commute distance")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
