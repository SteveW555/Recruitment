"""
Information Retrieval Agent - Multi-source data lookup and aggregation.

Handles simple information retrieval queries by:
1. Parsing the query for key search terms
2. Searching multiple sources (simulated for now)
3. Aggregating results with source citations
4. Returning formatted response with metadata

Uses Groq API (llama-3-70b-8192) for cost-effective inference.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import structlog
from groq import Groq

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


logger = structlog.get_logger()


class InformationRetrievalAgent(BaseAgent):
    """
    Information Retrieval Agent for multi-source data lookup.

    Specializes in:
    - Retrieving information from multiple sources
    - Aggregating results
    - Citing sources in responses
    - Formatting results clearly

    Uses Groq API for fast, cost-effective LLM inference.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Information Retrieval Agent.

        Args:
            config: Agent configuration with llm_provider, llm_model, system_prompt
        """
        super().__init__(config)

        # Initialize Groq client
        self.client = Groq()

        # Agent-specific configuration
        self.max_search_results = 5
        self.source_types = ["internal_database", "web_search", "industry_reports"]

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process information retrieval query.

        Steps:
        1. Parse query for key terms
        2. Simulate searching multiple sources
        3. Aggregate results
        4. Call Groq API to format response
        5. Return with source citations

        Args:
            request: AgentRequest with query and context

        Returns:
            AgentResponse with aggregated information
        """
        start_time = time.time()

        try:
            # Validate request
            if not self.validate_request(request):
                return AgentResponse(
                    success=False,
                    content="",
                    metadata={'agent_latency_ms': int((time.time() - start_time) * 1000)},
                    error="Invalid request"
                )

            # Extract key terms from query
            key_terms = self._extract_key_terms(request.query)

            # Simulate searching multiple sources
            search_results = await self._search_sources(key_terms, request)

            # Format results using Groq
            formatted_response = await self._format_response_with_groq(
                request.query,
                search_results,
                request
            )

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Extract sources from results
            sources = list(set([result.get('source', 'Unknown') for result in search_results]))

            return AgentResponse(
                success=True,
                content=formatted_response,
                metadata={
                    'agent_latency_ms': latency_ms,
                    'sources': sources,
                    'result_count': len(search_results),
                    'key_terms': key_terms
                }
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

    def _extract_key_terms(self, query: str) -> List[str]:
        """
        Extract key search terms from query.

        Args:
            query: User query

        Returns:
            List of key terms
        """
        # Simple keyword extraction (can be enhanced with NLP)
        stop_words = {
            'what', 'are', 'the', 'is', 'a', 'an', 'and', 'or', 'in', 'on', 'at',
            'for', 'to', 'of', 'by', 'from', 'with', 'as', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'can', 'may', 'might', 'must', 'can\'t', 'won\'t', 'don\'t'
        }

        words = query.lower().split()
        key_terms = [w for w in words if len(w) > 3 and w not in stop_words]

        return key_terms[:5]  # Limit to top 5 terms

    async def _search_sources(
        self,
        key_terms: List[str],
        request: AgentRequest
    ) -> List[Dict[str, Any]]:
        """
        Search multiple sources for relevant information.

        Simulates searching:
        - Internal database (candidates, jobs, clients)
        - Web search results
        - Industry reports and knowledge base

        Args:
            key_terms: Search terms extracted from query
            request: Original agent request

        Returns:
            List of search results with source attribution
        """
        results = []

        # Simulate internal database search
        db_results = self._search_internal_database(key_terms)
        results.extend(db_results)

        # Simulate web search
        web_results = self._search_web(key_terms)
        results.extend(web_results)

        # Simulate industry knowledge search
        industry_results = self._search_industry_knowledge(key_terms)
        results.extend(industry_results)

        # Limit and rank results
        return sorted(results, key=lambda x: x.get('relevance', 0), reverse=True)[:self.max_search_results]

    def _search_internal_database(self, key_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Simulate searching internal database (candidates, jobs, clients).

        Args:
            key_terms: Search terms

        Returns:
            List of database results
        """
        # Simulated internal database results
        sample_results = {
            'candidate': [
                {
                    'type': 'candidate_profile',
                    'data': 'Found 47 candidates matching your search criteria with relevant experience',
                    'relevance': 0.9,
                    'source': 'Internal Database - Candidates'
                }
            ],
            'job': [
                {
                    'type': 'job_posting',
                    'data': 'Found 12 active job postings in Bristol area across all sectors',
                    'relevance': 0.85,
                    'source': 'Internal Database - Jobs'
                }
            ],
            'board': [
                {
                    'type': 'job_board',
                    'data': 'Retrieved data on 15+ job boards with sync status and performance metrics',
                    'relevance': 0.88,
                    'source': 'Internal Database - Integrations'
                }
            ],
            'client': [
                {
                    'type': 'client',
                    'data': 'Found 8 active clients in your search area with current hiring needs',
                    'relevance': 0.82,
                    'source': 'Internal Database - Clients'
                }
            ]
        }

        results = []
        for term in key_terms:
            term_lower = term.lower()
            for key, matches in sample_results.items():
                if key in term_lower or term_lower in key:
                    results.extend(matches)

        # Return some default results if no matches
        if not results:
            results = [
                {
                    'type': 'general_search',
                    'data': f'Searched internal database for terms: {", ".join(key_terms)}',
                    'relevance': 0.7,
                    'source': 'Internal Database - General Search'
                }
            ]

        return results

    def _search_web(self, key_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Simulate searching web for information.

        Args:
            key_terms: Search terms

        Returns:
            List of web search results
        """
        web_sources = [
            {
                'data': f'Latest recruitment trends for {key_terms[0] if key_terms else "your search"}',
                'relevance': 0.75,
                'source': 'LinkedIn News & Updates'
            },
            {
                'data': 'Industry salary benchmarks and compensation data',
                'relevance': 0.72,
                'source': 'Salary.com and Glassdoor'
            },
            {
                'data': 'Best practices and case studies from recruitment leaders',
                'relevance': 0.70,
                'source': 'Indeed & Recruitment Industry Reports'
            }
        ]

        return web_sources[:2]  # Return top 2 web results

    def _search_industry_knowledge(self, key_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Search industry knowledge base and compliance documents.

        Args:
            key_terms: Search terms

        Returns:
            List of industry knowledge results
        """
        industry_results = [
            {
                'data': 'UK recruitment compliance and regulatory guidelines',
                'relevance': 0.80,
                'source': 'CIPD (Chartered Institute of Personnel Development)'
            }
        ]

        return industry_results

    async def _format_response_with_groq(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        request: AgentRequest
    ) -> str:
        """
        Use Groq API to format search results into a coherent response.

        Args:
            query: Original user query
            search_results: Search results from multiple sources
            request: Original agent request

        Returns:
            Formatted response text
        """
        # Build context from search results
        context = "\n".join([
            f"- {result.get('data', 'No data')} (Source: {result.get('source', 'Unknown')})"
            for result in search_results
        ])

        # Build prompt for Groq
        prompt = f"""You are an information retrieval assistant for a UK recruitment agency.

User Query: {query}

Information Found:
{context}

Please provide a concise, clear answer based on the information found above.
Structure your response with:
1. Direct answer to the query
2. Key findings from each source
3. Any relevant recommendations

Keep response to 150-200 words maximum and cite sources appropriately."""

        try:
            # Call Groq API with timeout
            message = await asyncio.wait_for(
                asyncio.to_thread(
                    self._call_groq_api,
                    prompt
                ),
                timeout=self.timeout - 0.5  # Leave buffer for other operations
            )

            return message

        except asyncio.TimeoutError:
            # Fallback to simple aggregation if Groq times out
            return self._aggregate_results_simple(query, search_results)

        except Exception as e:
            logger.error("groq_api_error", error=str(e))
            return self._aggregate_results_simple(query, search_results)

    def _call_groq_api(self, prompt: str) -> str:
        """
        Call Groq API synchronously (wrapped in async).

        Args:
            prompt: Prompt for Groq

        Returns:
            Response from Groq
        """
        message = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.llm_model,
            max_tokens=500,
            temperature=0.3  # Lower temperature for factual responses
        )

        return message.choices[0].message.content

    def _aggregate_results_simple(
        self,
        query: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Simple fallback aggregation if Groq API fails.

        Args:
            query: Original query
            search_results: Search results

        Returns:
            Simple aggregated response
        """
        response = f"Based on your query: '{query}'\n\n"
        response += "Found the following information:\n\n"

        for i, result in enumerate(search_results, 1):
            response += f"{i}. {result.get('data', 'No data available')}\n"
            response += f"   Source: {result.get('source', 'Unknown')}\n\n"

        return response

    def get_category(self) -> Category:
        """Return the category this agent handles."""
        return Category.INFORMATION_RETRIEVAL

    def validate_request(self, request: AgentRequest) -> bool:
        """
        Validate request for information retrieval agent.

        Args:
            request: Agent request

        Returns:
            True if valid, False otherwise
        """
        # Call parent validation
        if not super().validate_request(request):
            return False

        # Check for minimum query length
        if len(request.query.strip()) < 3:
            return False

        return True
