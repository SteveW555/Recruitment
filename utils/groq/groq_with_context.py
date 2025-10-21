"""
GROQ Context Query Tool
Prompts GROQ with custom requests using CSV data as context

This script allows you to query the fake client database using natural language
and get AI-powered insights and analysis.
"""

import os
import sys
import csv
import json
import argparse
from typing import List, Dict, Optional
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Import the main GROQ client
try:
    from groq_client import GroqClient, CompletionConfig, Temperature
except ImportError:
    print("ERROR: groq_client.py module not found. Please ensure groq_client.py is in the same directory.")
    exit(1)


class CSVContextLoader:
    """Load and format CSV data for GROQ context"""

    def __init__(self, csv_path: str):
        """
        Initialize CSV loader

        Args:
            csv_path: Path to CSV file
        """
        self.csv_path = csv_path
        self.data: List[Dict] = []
        self.headers: List[str] = []

    def load(self) -> None:
        """Load CSV data into memory"""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.headers = reader.fieldnames or []
            self.data = list(reader)

        print(f"✓ Loaded {len(self.data)} records from {os.path.basename(self.csv_path)}")

    def get_summary(self) -> str:
        """Get a summary of the CSV data"""
        if not self.data:
            return "No data loaded"

        summary = f"""
CSV Data Summary:
- File: {os.path.basename(self.csv_path)}
- Total Records: {len(self.data)}
- Fields: {len(self.headers)}
- Columns: {', '.join(self.headers[:10])}{'...' if len(self.headers) > 10 else ''}
"""
        return summary.strip()

    def format_as_context(
        self,
        max_records: Optional[int] = None,
        selected_fields: Optional[List[str]] = None,
        compact: bool = False
    ) -> str:
        """
        Format CSV data as context string for GROQ

        Args:
            max_records: Maximum number of records to include
            selected_fields: Only include specific fields
            compact: Use compact formatting

        Returns:
            Formatted context string
        """
        if not self.data:
            return "No data available"

        records = self.data[:max_records] if max_records else self.data
        fields = selected_fields if selected_fields else self.headers

        if compact:
            # Compact JSON format
            filtered_data = [
                {k: v for k, v in record.items() if k in fields}
                for record in records
            ]
            return json.dumps(filtered_data, indent=None)
        else:
            # Human-readable format
            context_parts = [f"Total Records: {len(self.data)}\n"]

            for i, record in enumerate(records, 1):
                context_parts.append(f"\n--- Record {i} ---")
                for field in fields:
                    if field in record:
                        value = record[field]
                        if value:  # Only show non-empty values
                            context_parts.append(f"{field}: {value}")

            return "\n".join(context_parts)

    def filter_records(
        self,
        filters: Dict[str, str]
    ) -> List[Dict]:
        """
        Filter records based on criteria

        Args:
            filters: Dictionary of field:value pairs to filter by

        Returns:
            Filtered records
        """
        filtered = self.data

        for field, value in filters.items():
            filtered = [
                record for record in filtered
                if field in record and value.lower() in record[field].lower()
            ]

        return filtered


class GroqContextQuery:
    """Query GROQ with CSV context"""

    def __init__(self, csv_path: str, api_key: Optional[str] = None):
        """
        Initialize the query tool

        Args:
            csv_path: Path to CSV file
            api_key: Optional GROQ API key
        """
        self.groq_client = GroqClient(api_key)
        self.csv_loader = CSVContextLoader(csv_path)
        self.csv_loader.load()

    def query(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        max_records: Optional[int] = 50,
        selected_fields: Optional[List[str]] = None,
        temperature: float = Temperature.BALANCED.value,
        stream: bool = False,
        compact_context: bool = False
    ) -> str:
        """
        Query GROQ with CSV context

        Args:
            prompt: User's question/request
            system_context: Optional system prompt context
            max_records: Maximum records to include in context
            selected_fields: Specific fields to include
            temperature: Response creativity (0.0-2.0)
            stream: Whether to stream the response
            compact_context: Use compact JSON format for context

        Returns:
            GROQ response
        """
        # Build system prompt
        default_system = f"""You are a helpful AI assistant analyzing recruitment client data for ProActive People, a Bristol-based recruitment agency.

You have access to a client database with the following information:
{self.csv_loader.get_summary()}

Provide accurate, insightful analysis based on the data provided.
When referencing specific clients, use their company names and relevant details.
"""

        system_prompt = system_context or default_system

        # Build context from CSV
        csv_context = self.csv_loader.format_as_context(
            max_records=max_records,
            selected_fields=selected_fields,
            compact=compact_context
        )

        # Combine prompt with context
        full_prompt = f"""Based on this client database:

{csv_context}

Question/Request:
{prompt}"""

        # Create config
        config = CompletionConfig(
            temperature=temperature,
            stream=stream,
            max_tokens=4000
        )

        print(f"\n{'='*70}")
        print("🤖 Querying GROQ...")
        print(f"{'='*70}\n")

        if stream:
            # Stream the response
            print("Response: ", end="", flush=True)
            full_response = []
            for chunk in self.groq_client.complete_stream(full_prompt, system_prompt, config):
                print(chunk, end="", flush=True)
                full_response.append(chunk)
            print("\n")
            return "".join(full_response)
        else:
            # Regular completion
            response = self.groq_client.complete(full_prompt, system_prompt, config)

            print(f"Response:\n{response.content}\n")
            print(f"{'='*70}")
            print(f"Model: {response.model}")
            print(f"Tokens Used: {response.usage['total_tokens']} (Prompt: {response.usage['prompt_tokens']}, Completion: {response.usage['completion_tokens']})")
            print(f"{'='*70}\n")

            return response.content

    def analyze_clients(
        self,
        analysis_type: str = "overview"
    ) -> str:
        """
        Pre-defined analysis queries

        Args:
            analysis_type: Type of analysis (overview, revenue, industry, etc.)

        Returns:
            Analysis result
        """
        prompts = {
            "overview": "Provide a comprehensive overview of the client database, including total clients, industries represented, and key statistics.",

            "revenue": "Analyze the revenue data: identify top-performing clients, average lifetime revenue, and revenue trends by industry sector.",

            "industry": "Break down the client database by industry sector. How many clients in each sector? Which sectors are most valuable?",

            "account_tier": "Analyze clients by account tier (Platinum, Gold, Silver, Bronze). What are the characteristics of each tier?",

            "services": "Analyze which service lines are most commonly used by clients and identify cross-selling opportunities.",

            "risk": "Identify clients with payment history concerns, low engagement, or other risk factors.",

            "opportunity": "Identify growth opportunities: clients with active jobs, high hiring frequency, or expansion potential.",

            "specialties": "Analyze recruitment specialties across clients. Which specialties are in highest demand?",

            "location": "Analyze client distribution by location. Where are our clients located?",

            "engagement": "Analyze client engagement: compare first engagement dates, last placement dates, and identify inactive clients."
        }

        if analysis_type not in prompts:
            return f"Unknown analysis type. Available types: {', '.join(prompts.keys())}"

        return self.query(prompts[analysis_type], temperature=Temperature.CONSERVATIVE.value)


def interactive_mode(query_tool: GroqContextQuery):
    """Run in interactive mode"""
    print("\n" + "="*70)
    print("🚀 GROQ Context Query - Interactive Mode")
    print("="*70)
    print("\nCommands:")
    print("  - Type your question to query the database")
    print("  - 'analyze <type>' - Run pre-defined analysis")
    print("  - 'info' - Show database info")
    print("  - 'quit' or 'exit' - Exit")
    print("="*70 + "\n")

    while True:
        try:
            user_input = input("\n💬 Your query: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break

            if user_input.lower() == 'info':
                print("\n" + query_tool.csv_loader.get_summary())
                continue

            if user_input.lower().startswith('analyze '):
                analysis_type = user_input[8:].strip()
                query_tool.analyze_clients(analysis_type)
                continue

            # Regular query
            query_tool.query(user_input)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Query GROQ with CSV context for ProActive People client database"
    )

    parser.add_argument(
        '--csv',
        type=str,
        default='Fake Data/fake_client_database_50.csv',
        help='Path to CSV file (default: Fake Data/fake_client_database_50.csv)'
    )

    parser.add_argument(
        '--prompt',
        type=str,
        help='Query prompt (if not provided, enters interactive mode)'
    )

    parser.add_argument(
        '--analyze',
        type=str,
        choices=['overview', 'revenue', 'industry', 'account_tier', 'services', 'risk', 'opportunity', 'specialties', 'location', 'engagement'],
        help='Run a pre-defined analysis'
    )

    parser.add_argument(
        '--max-records',
        type=int,
        default=50,
        help='Maximum number of records to include in context (default: 50)'
    )

    parser.add_argument(
        '--stream',
        action='store_true',
        help='Stream the response'
    )

    parser.add_argument(
        '--compact',
        action='store_true',
        help='Use compact JSON format for context'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Response temperature 0.0-2.0 (default: 0.7)'
    )

    args = parser.parse_args()

    # Initialize query tool
    try:
        query_tool = GroqContextQuery(args.csv)
    except Exception as e:
        print(f"❌ Error initializing: {str(e)}")
        return

    # Run based on mode
    if args.analyze:
        # Pre-defined analysis
        query_tool.analyze_clients(args.analyze)

    elif args.prompt:
        # Single query mode
        query_tool.query(
            args.prompt,
            max_records=args.max_records,
            stream=args.stream,
            temperature=args.temperature,
            compact_context=args.compact
        )

    else:
        # Interactive mode
        interactive_mode(query_tool)


# Example usage functions
def example_queries():
    """Example queries for the client database"""
    examples = [
        "Which clients have the highest lifetime revenue?",
        "List all clients in the IT Services sector",
        "Which clients have active jobs right now?",
        "Show me all Platinum tier clients",
        "Which clients use multiple service lines?",
        "Identify clients with payment history concerns",
        "Which account manager has the most clients?",
        "What are the most common recruitment specialties?",
        "Which clients offer remote work?",
        "Show clients with upcoming expansion or hiring needs",
        "Which clients have the fastest hiring processes?",
        "Compare average fee percentages across industries",
        "Which clients use our wellbeing services?",
        "Identify clients that haven't had placements recently",
        "Which clients have the highest number of total placements?"
    ]

    print("\n" + "="*70)
    print("📋 Example Queries:")
    print("="*70)
    for i, example in enumerate(examples, 1):
        print(f"{i:2d}. {example}")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Show examples if run without arguments
    import sys
    if len(sys.argv) == 1:
        print("\n🎯 GROQ Context Query Tool")
        print("Query your client database using AI\n")
        example_queries()
        print("Run with --help for usage options, or run without arguments for interactive mode.\n")
        print("Starting interactive mode...\n")

    main()
