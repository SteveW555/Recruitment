"""
GROQ Candidates Query Tool
Natural Language to SQL query generation for recruitment candidates database

This script uses GROQ to convert natural language questions into PostgreSQL queries
for the ProActive People candidates database.
"""

import os
import sys
import csv
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Import GROQ client
try:
    from groq_client import GroqClient, CompletionConfig, Temperature
except ImportError:
    print("ERROR: groq_client.py not found. Please ensure it's in the same directory.")
    exit(1)


class CandidatesQueryTool:
    """Query candidates database using natural language via GROQ"""

    def __init__(
        self,
        system_prompt_path: str = "prompts/candidates_nl2sql_system_prompt.txt",
        csv_path: str = "Fake Data/recruitment_candidates.csv",
        api_key: Optional[str] = None
    ):
        """
        Initialize the candidates query tool

        Args:
            system_prompt_path: Path to system prompt file
            csv_path: Path to candidates CSV file
            api_key: Optional GROQ API key
        """
        self.groq_client = GroqClient(api_key)
        self.csv_path = csv_path

        # Load system prompt
        self.system_prompt = self._load_system_prompt(system_prompt_path)

        # Load CSV data for local querying
        self.candidates_data = self._load_candidates_csv()

        print(f"✓ Loaded {len(self.candidates_data)} candidates from CSV")

    def _load_system_prompt(self, path: str) -> str:
        """Load the NL2SQL system prompt"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"System prompt not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_candidates_csv(self) -> List[Dict]:
        """Load candidates data from CSV"""
        if not os.path.exists(self.csv_path):
            print(f"⚠️  Warning: CSV file not found: {self.csv_path}")
            return []

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def generate_sql(
        self,
        natural_language_query: str,
        temperature: float = Temperature.CONSERVATIVE.value
    ) -> str:
        """
        Convert natural language to SQL query

        Args:
            natural_language_query: User's question in plain English
            temperature: Response temperature (0.0-2.0)

        Returns:
            Generated SQL query
        """
        config = CompletionConfig(
            temperature=temperature,
            max_tokens=500
        )

        print(f"\n{'='*70}")
        print(f"🔍 Natural Language Query:")
        print(f"{'='*70}")
        print(f"{natural_language_query}\n")

        response = self.groq_client.complete(
            natural_language_query,
            self.system_prompt,
            config
        )

        sql_query = response.content.strip()

        # Clean up any markdown formatting that might slip through
        if sql_query.startswith("```sql"):
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query.replace("```", "").strip()

        print(f"{'='*70}")
        print(f"📝 Generated SQL Query:")
        print(f"{'='*70}")
        print(f"{sql_query}\n")
        print(f"{'='*70}")
        print(f"Model: {response.model}")
        print(f"Tokens: {response.usage['total_tokens']} (Prompt: {response.usage['prompt_tokens']}, Completion: {response.usage['completion_tokens']})")
        print(f"{'='*70}\n")

        return sql_query

    def analyze_candidates(
        self,
        natural_language_query: str,
        include_context: bool = True,
        max_candidates: int = 10
    ) -> str:
        """
        Analyze candidates database with natural language and get insights

        Args:
            natural_language_query: User's question
            include_context: Whether to include sample candidate data
            max_candidates: Max candidates to include in context

        Returns:
            GROQ analysis response
        """
        # Build context
        context_parts = [
            "You are analyzing a recruitment candidates database for ProActive People.",
            f"\nTotal Candidates in Database: {len(self.candidates_data)}",
        ]

        if include_context and self.candidates_data:
            context_parts.append("\n\nSample Candidate Records:")
            for i, candidate in enumerate(self.candidates_data[:max_candidates], 1):
                context_parts.append(f"\n--- Candidate {i} ---")
                for key, value in candidate.items():
                    if value:  # Only show non-empty values
                        context_parts.append(f"{key}: {value}")

        context = "\n".join(context_parts)

        system_prompt = """You are a recruitment data analyst for ProActive People.
Analyze the candidates database and provide insights, statistics, and recommendations.
Be specific, data-driven, and actionable in your analysis."""

        full_prompt = f"""{context}

Question:
{natural_language_query}

Provide a detailed analysis with specific examples from the data."""

        config = CompletionConfig(
            temperature=Temperature.BALANCED.value,
            max_tokens=2000
        )

        print(f"\n{'='*70}")
        print(f"🧠 Analyzing Candidates Database")
        print(f"{'='*70}")
        print(f"Query: {natural_language_query}\n")

        response = self.groq_client.complete(full_prompt, system_prompt, config)

        print(f"{'='*70}")
        print(f"Analysis:")
        print(f"{'='*70}")
        print(f"{response.content}\n")
        print(f"{'='*70}")
        print(f"Tokens: {response.usage['total_tokens']}")
        print(f"{'='*70}\n")

        return response.content

    def get_candidate_recommendations(
        self,
        job_requirements: str,
        max_candidates: int = 5
    ) -> str:
        """
        Get candidate recommendations for a job

        Args:
            job_requirements: Job description or requirements
            max_candidates: Number of recommendations

        Returns:
            Recommendations
        """
        # Include all candidate data for matching
        candidates_context = "\n\n".join([
            f"Candidate {i+1}:\n" + "\n".join([f"{k}: {v}" for k, v in c.items() if v])
            for i, c in enumerate(self.candidates_data[:50])  # Limit to avoid token overflow
        ])

        system_prompt = """You are an expert recruitment consultant.
Match candidates to job requirements based on skills, experience, and fit.
Provide specific recommendations with reasoning."""

        prompt = f"""Job Requirements:
{job_requirements}

Available Candidates:
{candidates_context}

Task: Recommend the top {max_candidates} candidates for this role.
For each candidate, explain:
1. Why they're a good fit
2. Key matching skills/experience
3. Any potential concerns
4. Recommended next steps"""

        config = CompletionConfig(
            temperature=Temperature.BALANCED.value,
            max_tokens=3000
        )

        print(f"\n{'='*70}")
        print(f"🎯 Finding Candidate Matches")
        print(f"{'='*70}")
        print(f"Job Requirements: {job_requirements[:100]}...\n")

        response = self.groq_client.complete(prompt, system_prompt, config)

        print(f"{'='*70}")
        print(f"Recommendations:")
        print(f"{'='*70}")
        print(f"{response.content}\n")
        print(f"{'='*70}")
        print(f"Tokens: {response.usage['total_tokens']}")
        print(f"{'='*70}\n")

        return response.content


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode(tool: CandidatesQueryTool):
    """Run in interactive mode"""
    print("\n" + "="*70)
    print("🚀 GROQ Candidates Query - Interactive Mode")
    print("="*70)
    print("\nCommands:")
    print("  - Type your question to generate SQL")
    print("  - 'analyze <question>' - Get AI analysis of candidate data")
    print("  - 'recommend <job requirements>' - Get candidate recommendations")
    print("  - 'examples' - Show example queries")
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

            if user_input.lower() == 'examples':
                show_examples()
                continue

            if user_input.lower().startswith('analyze '):
                question = user_input[8:].strip()
                tool.analyze_candidates(question)
                continue

            if user_input.lower().startswith('recommend '):
                requirements = user_input[10:].strip()
                tool.get_candidate_recommendations(requirements)
                continue

            # Default: Generate SQL
            tool.generate_sql(user_input)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def show_examples():
    """Show example queries"""
    print("\n" + "="*70)
    print("📋 Example Queries")
    print("="*70)

    examples = [
        # Basic searches
        ("Find candidate Alex Roberts", "Simple name search"),
        ("Show all software engineers", "Job title search"),
        ("Find Python developers", "Skills-based search"),

        # Status filters
        ("Show available candidates", "Filter by availability"),
        ("Who is currently interviewing?", "Interview stage"),
        ("Candidates with pending offers", "Offer stage"),

        # Skills combinations
        ("Candidates with both Python and AWS skills", "Multiple skills (AND)"),
        ("Developers with Python or Java", "Multiple skills (OR)"),
        ("Available Python developers", "Skills + Status"),

        # Salary queries
        ("Candidates expecting under £100k", "Salary filter"),
        ("Show candidates wanting between 80k and 120k", "Salary range"),
        ("AWS engineers wanting over 100k", "Skills + Salary"),

        # Date/recency
        ("Candidates contacted in the last week", "Recent contact"),
        ("Show candidates contacted this month", "This month"),

        # Sentiment/feedback
        ("Show candidates with positive interview feedback", "Interview sentiment"),
        ("Highly rated candidates", "High sentiment"),

        # Complex queries
        ("Available software engineers with Python, positive feedback, under 120k", "Multi-filter"),
        ("Top 5 highest salary expectations", "Top N with sorting"),

        # Aggregations
        ("How many available candidates do we have?", "Count"),
        ("Count candidates by status", "Group by"),
        ("Average desired salary for software engineers", "Average"),

        # Analysis mode
        ("analyze What are our strongest technical skill sets?", "Analysis query"),
        ("analyze Which candidates haven't been contacted recently?", "Engagement analysis"),

        # Recommendation mode
        ("recommend Senior Python developer, AWS, 5+ years experience", "Match candidates"),
    ]

    for i, (query, description) in enumerate(examples, 1):
        print(f"\n{i:2d}. {description}")
        print(f"    Query: {query}")

    print("\n" + "="*70 + "\n")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Query candidates database using natural language with GROQ"
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Natural language query for SQL generation'
    )

    parser.add_argument(
        '--analyze',
        type=str,
        help='Analyze candidates data with natural language'
    )

    parser.add_argument(
        '--recommend',
        type=str,
        help='Get candidate recommendations for job requirements'
    )

    parser.add_argument(
        '--csv',
        type=str,
        default='Fake Data/recruitment_candidates.csv',
        help='Path to candidates CSV file'
    )

    parser.add_argument(
        '--prompt',
        type=str,
        default='prompts/candidates_nl2sql_system_prompt.txt',
        help='Path to system prompt file'
    )

    parser.add_argument(
        '--examples',
        action='store_true',
        help='Show example queries'
    )

    args = parser.parse_args()

    # Show examples if requested
    if args.examples:
        show_examples()
        return

    # Initialize tool
    try:
        tool = CandidatesQueryTool(
            system_prompt_path=args.prompt,
            csv_path=args.csv
        )
    except Exception as e:
        print(f"❌ Error initializing: {str(e)}")
        return

    # Run based on mode
    if args.query:
        # SQL generation mode
        tool.generate_sql(args.query)

    elif args.analyze:
        # Analysis mode
        tool.analyze_candidates(args.analyze)

    elif args.recommend:
        # Recommendation mode
        tool.get_candidate_recommendations(args.recommend)

    else:
        # Interactive mode
        interactive_mode(tool)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
