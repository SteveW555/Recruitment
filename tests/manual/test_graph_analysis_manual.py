"""
Manual test script for Report Generation Agent graph analysis feature.

Run this to verify the graph analysis and SQL generation capabilities work.
"""

import asyncio
import json
from utils.ai_router.agents.report_generation_agent import ReportGenerationAgent
from utils.ai_router.agents.base_agent import AgentRequest


async def test_graph_analysis():
    """Test the graph analysis functionality."""

    print("=" * 80)
    print("TESTING REPORT GENERATION AGENT - GRAPH ANALYSIS FEATURE")
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
    print("\n✓ Initializing Report Generation Agent...")
    agent = ReportGenerationAgent(config)
    print("✓ Agent initialized successfully")

    # Test queries
    test_queries = [
        {
            "name": "Time Series (Should have graph)",
            "query": "Create a report showing placement trends over the last 12 months"
        },
        {
            "name": "Comparison (Should have graph)",
            "query": "Generate a report comparing revenue by division for Q4 2024"
        },
        {
            "name": "Textual Report (Should NOT have graph)",
            "query": "Create a company profile report for client ABC Corporation"
        },
        {
            "name": "Distribution (Should have graph)",
            "query": "Show candidate distribution by status for the current quarter"
        }
    ]

    results = []

    for i, test in enumerate(test_queries, 1):
        print(f"\n{'-' * 80}")
        print(f"TEST {i}/{len(test_queries)}: {test['name']}")
        print(f"Query: {test['query']}")
        print(f"{'-' * 80}")

        try:
            # Create request
            request = AgentRequest(
                query=test['query'],
                user_id="test_user",
                session_id="test_session"
            )

            # Process request
            print("\n⏳ Processing request...")
            response = await agent.process(request)

            # Extract results
            success = response.success
            has_graph_analysis = 'graph_analysis' in response.metadata

            if has_graph_analysis:
                graph_analysis = response.metadata['graph_analysis']
                requires_graph = graph_analysis.get('requires_graph', False)
                graph_type = graph_analysis.get('graph_type', 'N/A')
                sql_query = graph_analysis.get('sql_query')
                reasoning = graph_analysis.get('reasoning', 'N/A')
            else:
                requires_graph = False
                graph_type = 'N/A'
                sql_query = None
                reasoning = 'No analysis performed'

            # Display results
            print(f"\n{'✓' if success else '✗'} Status: {'SUCCESS' if success else 'FAILED'}")
            print(f"{'✓' if has_graph_analysis else '✗'} Graph Analysis: {'Present' if has_graph_analysis else 'Missing'}")

            if has_graph_analysis:
                print(f"\n📊 Graph Analysis Results:")
                print(f"   Requires Graph: {requires_graph}")
                print(f"   Graph Type: {graph_type}")
                print(f"   Reasoning: {reasoning}")

                if sql_query:
                    print(f"\n   SQL Query:")
                    print(f"   {'-' * 76}")
                    # Format SQL nicely
                    sql_formatted = sql_query.replace('SELECT', '\n   SELECT') \
                                              .replace('FROM', '\n   FROM') \
                                              .replace('WHERE', '\n   WHERE') \
                                              .replace('GROUP BY', '\n   GROUP BY') \
                                              .replace('ORDER BY', '\n   ORDER BY')
                    print(f"   {sql_formatted}")
                    print(f"   {'-' * 76}")
                else:
                    print(f"\n   SQL Query: None (graph not recommended)")

            # Check if content includes visualization section
            has_viz_section = '📊' in response.content
            print(f"\n{'✓' if has_viz_section else '✗'} Visualization Section in Report: {'Present' if has_viz_section else 'Missing'}")

            # Store result
            results.append({
                'test_name': test['name'],
                'success': success,
                'has_graph_analysis': has_graph_analysis,
                'requires_graph': requires_graph,
                'graph_type': graph_type,
                'has_sql': sql_query is not None
            })

            print(f"\n✓ Test completed")

        except Exception as e:
            print(f"\n✗ Test FAILED with error: {str(e)}")
            results.append({
                'test_name': test['name'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}\n")

    passed = sum(1 for r in results if r.get('success', False))
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")
    print(f"\nDetailed Results:")
    print(f"{'-' * 80}")

    for result in results:
        status = '✓' if result.get('success', False) else '✗'
        print(f"{status} {result['test_name']}")

        if result.get('success'):
            print(f"   - Graph Analysis: {'✓' if result.get('has_graph_analysis') else '✗'}")
            print(f"   - Requires Graph: {result.get('requires_graph')}")
            print(f"   - Graph Type: {result.get('graph_type', 'N/A')}")
            print(f"   - Has SQL: {'✓' if result.get('has_sql') else '✗'}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
        print()

    print(f"{'=' * 80}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Graph analysis feature is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the errors above.")

    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    print("\nStarting Report Generation Agent Graph Analysis Tests...")
    print("This will test the new graph suitability analysis and SQL generation features.\n")

    try:
        asyncio.run(test_graph_analysis())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
