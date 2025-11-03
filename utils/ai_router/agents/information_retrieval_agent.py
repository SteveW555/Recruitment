"""
Information Retrieval Agent - Candidate database queries using NL2SQL.

Handles candidate search queries by:
1. Converting natural language to SQL using Groq
2. Executing SQL against Supabase candidates table
3. Formatting results for user
4. Returning formatted response with metadata

Uses Groq API (llama-3.3-70b-versatile) for NL2SQL conversion.
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import structlog
from groq import Groq
from supabase import create_client, Client

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


logger = structlog.get_logger()

# Set up SQL file logger
sql_log_dir = Path("logs")
sql_log_dir.mkdir(exist_ok=True)
sql_file_logger = logging.getLogger("sql_logger")
sql_file_logger.setLevel(logging.INFO)
sql_handler = logging.FileHandler(sql_log_dir / "sql.log", encoding="utf-8")
sql_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
sql_file_logger.addHandler(sql_handler)
sql_file_logger.propagate = False  # Don't propagate to root logger


class InformationRetrievalAgent(BaseAgent):
    """
    Information Retrieval Agent for candidate database queries.

    Specializes in:
    - Converting natural language to SQL
    - Querying Supabase candidates table
    - Formatting query results
    - Citing sources in responses

    Uses Groq API for fast, cost-effective NL2SQL conversion.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Information Retrieval Agent.

        Args:
            config: Agent configuration with llm_provider, llm_model, system_prompt
        """
        super().__init__(config)

        # Initialize Groq client for NL2SQL
        self.client = Groq()

        # Initialize Supabase client
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            logger.warning("supabase_credentials_missing", msg="SUPABASE_URL or SUPABASE_KEY not set")
            self.supabase: Optional[Client] = None
        else:
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("supabase_connected", url=supabase_url)

        # NL2SQL prompt will be loaded dynamically in process() based on suggested_table
        self.nl2sql_prompt = None

    def get_category(self) -> Category:
        """Return the category this agent handles."""
        return Category.INFORMATION_RETRIEVAL

    def _load_nl2sql_prompt(self, table_name: str = "candidates") -> str:
        """
        Load NL2SQL system prompt from file based on table name.

        Args:
            table_name: Database table name (candidates, clients, finance, multi)

        Returns:
            NL2SQL system prompt text
        """
        # Handle multi-table queries
        if table_name == "multi":
            prompt_path = "prompts/multi_table_nl2sql_system_prompt.txt"
        else:
            prompt_path = f"prompts/{table_name}_nl2sql_system_prompt.txt"

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
                logger.info("nl2sql_prompt_loaded", path=prompt_path, table=table_name, length=len(prompt))
                print(f"[OK] Loaded NL2SQL prompt for table: {table_name}", file=sys.stderr)
                return prompt
        except FileNotFoundError:
            logger.warning("nl2sql_prompt_not_found", path=prompt_path, table=table_name)
            print(f"[WARNING] Prompt not found: {prompt_path}, falling back to candidates", file=sys.stderr)
            # Fallback to candidates prompt
            if table_name != "candidates":
                return self._load_nl2sql_prompt("candidates")
            else:
                # Ultimate fallback if even candidates prompt is missing
                return "Convert the following natural language query to a PostgreSQL query for the candidates table."
        except Exception as e:
            logger.error("nl2sql_prompt_load_error", error=str(e), path=prompt_path)
            # Fallback minimal prompt
            return f"Convert the following natural language query to a PostgreSQL query for the {table_name} table."

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process candidate information retrieval query.

        Steps:
        1. Extract suggested table from routing decision
        2. Load appropriate NL2SQL prompt for the table
        3. Convert natural language to SQL using Groq
        4. Execute SQL against Supabase
        5. Format results
        6. Return with source citations

        Args:
            request: AgentRequest with query and context

        Returns:
            AgentResponse with query results
        """
        start_time = time.time()
        print(f"[*] InformationRetrievalAgent.process() CALLED: query={request.query[:50]}...", file=sys.stderr)

        # Extract suggested table from request (default to candidates)
        suggested_table = request.suggested_table or "candidates"

        print(f"[INFO] Using table: {suggested_table}", file=sys.stderr)

        # Load appropriate NL2SQL prompt for the table
        self.nl2sql_prompt = self._load_nl2sql_prompt(suggested_table)

        sys.stderr.flush()

        try:
            # Validate request
            if not self.validate_request(request):
                print(f"[ERROR RetrievalAgent] Invalid request", file=sys.stderr)
                return AgentResponse(
                    success=False,
                    content="",
                    metadata={'agent_latency_ms': int((time.time() - start_time) * 1000)},
                    error="Invalid request"
                )

            # Check Supabase connection
            if not self.supabase:
                print(f"[ERROR RetrievalAgent] Supabase connection not configured", file=sys.stderr)
                return AgentResponse(
                    success=False,
                    content="",
                    metadata={'agent_latency_ms': int((time.time() - start_time) * 1000)},
                    error="Supabase connection not configured"
                )

            # Step 1: Convert natural language to SQL
            print(f"[STEP 1 RetrievalAgent] Converting NL to SQL...", file=sys.stderr)
            sql_query, nl2sql_prompt_used = await self._convert_to_sql(request.query)
            print(f"[STEP 1 RetrievalAgent] SQL Generated: {sql_query[:100]}...", file=sys.stderr)

            if not sql_query:
                print(f"[ERROR RetrievalAgent] Failed to convert query to SQL", file=sys.stderr)
                return AgentResponse(
                    success=False,
                    content="",
                    metadata={
                        'agent_latency_ms': int((time.time() - start_time) * 1000),
                        'agent_prompt': nl2sql_prompt_used
                    },
                    error="Failed to convert query to SQL"
                )

            # Step 2: Execute SQL query
            print(f"[STEP 2 RetrievalAgent] Executing SQL query...", file=sys.stderr)
            results, result_count = await self._execute_sql(sql_query)
            print(f"[STEP 2 RetrievalAgent] Query returned {result_count} results", file=sys.stderr)

            # Step 3: Format results for user
            print(f"[STEP 3 RetrievalAgent] Formatting results...", file=sys.stderr)
            formatted_response, agent_prompt = await self._format_results(
                request.query,
                sql_query,
                results,
                result_count,
                suggested_table
            )
            print(f"[STEP 3 RetrievalAgent] Response formatted ({len(formatted_response)} chars)", file=sys.stderr)

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Build metadata
            metadata = {
                'agent_latency_ms': latency_ms,
                'sources': [f'Supabase {suggested_table.capitalize()} Database'],
                'table_used': suggested_table,
                'result_count': result_count,
                'sql_query': sql_query,
                'sql_results': results[:10],  # Include first 10 results for display
                'agent_prompt': agent_prompt  # Include for transparency
            }

            print(f"[RETURN RetrievalAgent] Returning response with metadata keys: {list(metadata.keys())}", file=sys.stderr)
            print(f"[RETURN RetrievalAgent] SQL query in metadata: {metadata['sql_query'][:100]}...", file=sys.stderr)
            print(f"[RETURN RetrievalAgent] Result count in metadata: {metadata['result_count']}", file=sys.stderr)
            print(f"[*] InformationRetrievalAgent.process() RETURNING: success=True, result_count={metadata['result_count']}", file=sys.stderr)
            sys.stderr.flush()

            return AgentResponse(
                success=True,
                content=formatted_response,
                metadata=metadata
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning("information_retrieval_timeout", latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error="Information retrieval timed out"
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("information_retrieval_error", error=str(e), latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error=f"Information retrieval error: {str(e)}"
            )

    async def _convert_to_sql(self, query: str) -> Tuple[str, str]:
        """
        Convert natural language query to SQL using Groq.

        Args:
            query: Natural language query

        Returns:
            Tuple of (SQL query string, NL2SQL prompt used)
        """
        print(f"[*]     ****    InformationRetrievalAgent._convert_to_sql() CALLED: query={query[:50]}...", file=sys.stderr)
        sys.stderr.flush()

        try:
            # Call Groq API for NL2SQL conversion
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": self.nl2sql_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.1,  # Low temperature for consistent SQL generation
                max_tokens=500
            )

            sql_query = completion.choices[0].message.content.strip()

            # Remove any markdown formatting if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()

            # Remove trailing semicolon (PostgreSQL EXECUTE doesn't like it)
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1].strip()
                print(f"[*]   Removed trailing semicolon from SQL", file=sys.stderr)

            # Log to terminal (stderr)
            print(f"\n{'='*80}", file=sys.stderr)
            print(f"[SQL GENERATED] Query: {query}", file=sys.stderr)
            print(f"[SQL GENERATED] SQL:\n{sql_query}", file=sys.stderr)
            print(f"{'='*80}\n", file=sys.stderr)

            # Log to file (logs/sql.log)
            sql_file_logger.info(f"QUERY: {query}")
            sql_file_logger.info(f"SQL: {sql_query}")
            sql_file_logger.info("-" * 80)

            logger.info("nl2sql_conversion", query=query[:50], sql=sql_query[:100])
            print(f"[*] InformationRetrievalAgent._convert_to_sql() RETURNING: SQL generated ({len(sql_query)} chars)", file=sys.stderr)
            sys.stderr.flush()
            return sql_query, self.nl2sql_prompt

        except Exception as e:
            logger.error("nl2sql_conversion_error", error=str(e))
            return "", self.nl2sql_prompt
    #========================================================================
    async def _execute_sql(self, sql_query: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Execute SQL query against Supabase.

        Args:
            sql_query: SQL query to execute

        Returns:
            Tuple of (results list, result count)
        """
        print(f"[*]     ****    InformationRetrievalAgent._execute_sql() CALLED: sql={sql_query[:80]}...", file=sys.stderr)
        sys.stderr.flush()

        try:
            # Execute query via Supabase RPC first
            print(f"[*]   Attempting Supabase RPC: exec_sql()", file=sys.stderr)
            sys.stderr.flush()

            # Important: Need to call .execute() on the RPC builder
            # supabase.rpc() returns a builder, not the result
            rpc_builder = self.supabase.rpc('exec_sql', {'query': sql_query})
            print(f"[*]   RPC builder created, calling .execute()...", file=sys.stderr)
            sys.stderr.flush()

            response = await asyncio.to_thread(rpc_builder.execute)

            # Debug: Show response type and structure
            print(f"[*]   RPC response type: {type(response)}", file=sys.stderr)
            print(f"[*]   RPC response hasattr('data'): {hasattr(response, 'data') if response else 'None'}", file=sys.stderr)
            if response and hasattr(response, 'data'):
                print(f"[*]   RPC response.data type: {type(response.data)}", file=sys.stderr)
                print(f"[*]   RPC response.data: {str(response.data)[:200]}...", file=sys.stderr)
            sys.stderr.flush()

            # Check if RPC succeeded and has data
            if not response or not hasattr(response, 'data') or response.data is None:
                # Parse the SQL to extract table and conditions
                # For now, try a simple select
                logger.warning("rpc_not_available", msg="Falling back to direct table query")
                print(f"[*]   RPC failed - Falling back to direct table query: supabase.table('candidates').select('*').limit(100)", file=sys.stderr)
                sys.stderr.flush()

                response = await asyncio.to_thread(
                    self.supabase.table('candidates').select('*').limit(100).execute
                )
                print(f"[*]   Using fallback method: Direct table='candidates' query", file=sys.stderr)
                results = response.data if response and hasattr(response, 'data') else []
            else:
                # Check if response contains an error from exec_sql function
                if isinstance(response.data, dict) and 'error' in response.data:
                    error_msg = response.data.get('error', 'Unknown error')
                    error_detail = response.data.get('detail', '')
                    print(f"[*]   ❌ SQL EXECUTION ERROR: {error_msg} (code: {error_detail})", file=sys.stderr)
                    logger.error("sql_execution_error", error=error_msg, detail=error_detail, sql=sql_query[:100])
                    results = []
                else:
                    print(f"[*]   Using RPC method: exec_sql() executed successfully", file=sys.stderr)
                    # RPC returns JSONB directly - it's already a list
                    results = response.data if isinstance(response.data, list) else []

            sys.stderr.flush()
            result_count = len(results)

            logger.info("sql_execution", count=result_count)
            print(f"[*] InformationRetrievalAgent._execute_sql() RETURNING: result_count={result_count}", file=sys.stderr)
            sys.stderr.flush()
            return results, result_count

        except Exception as e:
            logger.error("sql_execution_error", error=str(e), sql=sql_query[:100])
            print(f"[*] InformationRetrievalAgent._execute_sql() ERROR: {str(e)[:80]}", file=sys.stderr)
            sys.stderr.flush()
            return [], 0
    #========================================================================
    async def _format_results(
        self,
        original_query: str,
        sql_query: str,
        results: List[Dict[str, Any]],
        result_count: int,
        table_type: str = "candidates"
    ) -> Tuple[str, str]:
        """
        Format query results into user-friendly response.

        Args:
            original_query: Original natural language query
            sql_query: SQL query that was executed
            results: Query results
            result_count: Number of results
            table_type: Database table queried (candidates, clients, finance, multi)

        Returns:
            Tuple of (formatted response, agent prompt used)
        """
        # Adapt prompt based on table type
        if table_type == "clients":
            data_type = "clients"
            entity_plural = "clients"
            entity_singular = "client"
            key_details = "company names, account tiers, account managers, revenue"
        elif table_type == "finance":
            data_type = "financial records"
            entity_plural = "transactions"
            entity_singular = "transaction"
            key_details = "amounts, dates, categories, payment status"
        elif table_type == "multi":
            data_type = "records"
            entity_plural = "records"
            entity_singular = "record"
            key_details = "key relationships and combined data"
        else:  # candidates (default)
            data_type = "candidates"
            entity_plural = "candidates"
            entity_singular = "candidate"
            key_details = "names, skills, roles"

        # Build agent prompt for formatting
        agent_prompt = f"""You are a recruitment assistant helping to present {data_type} search results.

User Query: {original_query}

SQL Query Executed:
{sql_query}

Results Retrieved: {result_count} {entity_plural}

Results Data:
{self._format_results_for_llm(results[:5])}  # Show max 5 for context

Please provide a concise, professional summary of the results:
1. State how many {entity_plural} were found
2. Highlight key details from the top results ({key_details})
3. Mention any notable patterns or standout {entity_plural}
4. Keep response to 150-200 words maximum

Format the response in a clear, readable way suitable for a recruiter."""

        try:
            # Call Groq to format the response
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": agent_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Please format the {data_type} search results."
                    }
                ],
                temperature=0.3,
                max_tokens=400
            )

            formatted_response = completion.choices[0].message.content.strip()
            return formatted_response, agent_prompt

        except Exception as e:
            logger.error("format_results_error", error=str(e))
            # Fallback to simple formatting
            fallback = f"Found {result_count} {entity_plural} matching your search."
            if results:
                fallback += "\n\nTop results:\n"
                fallback += self._format_results_for_llm(results[:3])

            return fallback, agent_prompt

    def _format_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """
        Format results data for LLM context.

        Args:
            results: Query results

        Returns:
            Formatted string representation
        """
        if not results:
            return "No results found"

        formatted = []
        for result in results:
            candidate_info = []
            if 'first_name' in result and 'last_name' in result:
                candidate_info.append(f"Name: {result['first_name']} {result['last_name']}")
            if 'job_title_target' in result:
                candidate_info.append(f"Role: {result['job_title_target']}")
            if 'primary_skills' in result:
                candidate_info.append(f"Skills: {result['primary_skills']}")
            if 'current_status' in result:
                candidate_info.append(f"Status: {result['current_status']}")
            if 'desired_salary' in result:
                candidate_info.append(f"Salary: £{result['desired_salary']:,.0f}")

            formatted.append(" | ".join(candidate_info))

        return "\n".join(formatted)
