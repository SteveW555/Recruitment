"""
Test the advertising costs report to verify graph analysis works.
"""

import asyncio
from utils.ai_router.agents.report_generation_agent import ReportGenerationAgent
from utils.ai_router.agents.base_agent import AgentRequest


async def test_advertising_report():
    """Test advertising costs report with graph analysis."""

    print("=" * 80)
    print("TESTING: Advertising Costs Report")
    print("=" * 80)

    # Configuration
    config = {
        'name': 'Report Generation',
        'priority': 3,
        'agent_class': 'utils.ai_router.agents.report_generation_agent:ReportGenerationAgent',
        'llm_provider': 'groq',
        'llm_model': 'llama-3-70b-8192',
        'timeout_seconds': 2,
        'system_prompt': 'You are a report generation specialist with data visualization expertise.',
        'enabled': True
    }

    # Initialize agent
    print("\n[OK] Initializing Report Generation Agent...")
    agent = ReportGenerationAgent(config)

    # Test query
    query = "report advertising costs over the last year"

    print(f"\nQuery: '{query}'")
    print("\n[PROCESSING] Processing request...\n")

    # Create request
    request = AgentRequest(
        query=query,
        user_id="test_user",
        session_id="test_session"
    )

    # Process
    response = await agent.process(request)

    # Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"\nSuccess: {response.success}")

    if 'graph_analysis' in response.metadata:
        ga = response.metadata['graph_analysis']
        print("\n[GRAPH ANALYSIS]")
        print(f"   Requires Graph: {ga.get('requires_graph')}")
        print(f"   Graph Type: {ga.get('graph_type')}")
        print(f"   Library: {ga.get('recommended_library')}")
        print(f"   Reasoning: {ga.get('reasoning')}")

        if ga.get('sql_query'):
            print(f"\n   SQL QUERY:")
            print("   " + "-" * 76)
            sql = ga.get('sql_query')
            # Format SQL
            sql_formatted = sql.replace('SELECT', '\n   SELECT') \
                              .replace('FROM', '\n   FROM') \
                              .replace('WHERE', '\n   WHERE') \
                              .replace('GROUP BY', '\n   GROUP BY') \
                              .replace('ORDER BY', '\n   ORDER BY')
            print(f"   {sql_formatted}")
            print("   " + "-" * 76)
    else:
        print("\n[WARNING] NO GRAPH ANALYSIS IN METADATA")

    # Check content
    print(f"\n[INFO] REPORT CONTENT LENGTH: {len(response.content)} characters")

    if 'Data Visualization Recommendation' in response.content:
        print("[OK] Visualization recommendation section PRESENT")
    elif 'No graph recommended' in response.content:
        print("[WARNING] 'No graph recommended' message found")
    else:
        print("[ERROR] NO visualization section found in content")

    # Show portion of content
    print("\n[REPORT EXCERPT] First 500 chars:")
    print("-" * 80)
    print(response.content[:500])
    print("-" * 80)

    # Show end of content (where viz section should be)
    print("\n[REPORT END] Last 800 chars:")
    print("-" * 80)
    print(response.content[-800:])
    print("-" * 80)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_advertising_report())
