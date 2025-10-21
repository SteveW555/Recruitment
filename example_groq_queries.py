"""
Example GROQ Queries with Client Database Context

This script demonstrates various ways to use the groq_with_context module
to query your client database.
"""

from groq_with_context import GroqContextQuery
import os


def main():
    print("\n" + "="*80)
    print("🎯 GROQ Context Query Examples - ProActive People Client Database")
    print("="*80 + "\n")

    # Initialize the query tool
    csv_path = "Fake Data/fake_client_database_50.csv"

    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        print("Please ensure the fake client database CSV is in the correct location.")
        return

    query_tool = GroqContextQuery(csv_path)

    # Example 1: Simple query
    print("\n📊 EXAMPLE 1: Top Revenue Clients")
    print("-" * 80)
    query_tool.query(
        "List the top 5 clients by lifetime revenue. Include company name, revenue, and industry.",
        max_records=50,
        temperature=0.3
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 2: Industry analysis
    print("\n🏭 EXAMPLE 2: Industry Breakdown")
    print("-" * 80)
    query_tool.query(
        "Provide a breakdown of clients by industry sector. How many clients in each sector?",
        max_records=50,
        temperature=0.3
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 3: Account tier analysis
    print("\n🏆 EXAMPLE 3: Account Tier Analysis")
    print("-" * 80)
    query_tool.query(
        "Compare the different account tiers (Platinum, Gold, Silver, Bronze). "
        "What are the average revenues and number of placements for each tier?",
        max_records=50,
        temperature=0.3
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 4: Opportunities
    print("\n💡 EXAMPLE 4: Growth Opportunities")
    print("-" * 80)
    query_tool.query(
        "Identify clients with active jobs or expansion plans mentioned in their notes. "
        "These are immediate opportunities for placements.",
        max_records=50,
        temperature=0.5
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 5: Service usage
    print("\n🛠️  EXAMPLE 5: Service Line Analysis")
    print("-" * 80)
    query_tool.query(
        "Which clients use multiple service lines (Recruitment, Wellbeing, Training, etc.)? "
        "Identify cross-selling opportunities for clients using only one service.",
        max_records=50,
        temperature=0.5
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 6: Risk analysis
    print("\n⚠️  EXAMPLE 6: Risk Assessment")
    print("-" * 80)
    query_tool.query(
        "Identify any clients with potential risks such as 'Fair' payment history, "
        "long time since last placement, or inactive status. Suggest actions.",
        max_records=50,
        temperature=0.5
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 7: Specialist requirements
    print("\n🎓 EXAMPLE 7: Recruitment Specialties")
    print("-" * 80)
    query_tool.query(
        "What are the most common recruitment specialties across all clients? "
        "Which specialties appear most frequently?",
        max_records=50,
        temperature=0.3
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 8: Location analysis
    print("\n📍 EXAMPLE 8: Geographic Distribution")
    print("-" * 80)
    query_tool.query(
        "Analyze the geographic distribution of clients. "
        "Which cities have the most clients? Are there any regional patterns?",
        max_records=50,
        temperature=0.3
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 9: Work model trends
    print("\n🏠 EXAMPLE 9: Work Model Preferences")
    print("-" * 80)
    query_tool.query(
        "Analyze work model preferences across clients (Office, Hybrid, Remote). "
        "What are the trends? Which industries prefer which models?",
        max_records=50,
        temperature=0.5
    )

    input("\n⏸️  Press Enter to continue to next example...")

    # Example 10: Pre-defined analysis
    print("\n📈 EXAMPLE 10: Using Pre-defined Analysis")
    print("-" * 80)
    print("Running 'opportunity' analysis...\n")
    query_tool.analyze_clients('opportunity')

    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80)
    print("\nTry running 'python groq_with_context.py' for interactive mode!")
    print("Or use: python groq_with_context.py --prompt \"Your question here\"\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Examples interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
