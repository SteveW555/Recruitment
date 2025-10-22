"""
Industry Knowledge Agent - UK recruitment domain expertise.

Handles queries about:
1. UK recruitment regulations and compliance
2. Industry best practices
3. Salary trends and market data
4. Legal requirements (GDPR, IR35, right-to-work, etc.)

Always cites validated sources from sources_validated_summaries.md.
Uses Groq API for fast inference.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import os
import structlog
from groq import Groq

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


logger = structlog.get_logger()


class IndustryKnowledgeAgent(BaseAgent):
    """
    Industry Knowledge Agent for UK recruitment domain expertise.

    Specializes in:
    - UK recruitment compliance and regulations
    - Industry best practices
    - Salary and market trends
    - Legal requirements for agencies and contractors
    - Always cites validated sources

    Uses Groq API (llama-3-70b-8192) for cost-effective inference.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Industry Knowledge Agent.

        Args:
            config: Agent configuration including resources.sources_file path
        """
        super().__init__(config)

        # Initialize Groq client
        self.client = Groq()

        # Load sources file
        self.sources_file = config.get('resources', {}).get('sources_file', './sources_validated_summaries.md')
        self.sources_content = self._load_sources()

    def _load_sources(self) -> str:
        """
        Load validated sources from file.

        Returns:
            Content of sources file or empty string if not found
        """
        try:
            if os.path.exists(self.sources_file):
                with open(self.sources_file, 'r') as f:
                    content = f.read()
                logger.info("sources_loaded", file=self.sources_file)
                return content
            else:
                # Create default sources if file doesn't exist
                logger.warning("sources_file_not_found", file=self.sources_file)
                return self._get_default_sources()
        except Exception as e:
            logger.error("sources_load_error", error=str(e), file=self.sources_file)
            return self._get_default_sources()

    def _get_default_sources(self) -> str:
        """
        Provide default industry knowledge if sources file unavailable.

        Returns:
            Default industry knowledge content
        """
        return """# UK Recruitment Industry Knowledge Base

## Regulations & Compliance

### GDPR (General Data Protection Regulation)
- Applicable to all EU/UK personal data
- Candidates must provide explicit consent for CV storage
- Data must be deleted within 3 months of request (right to erasure)
- Personal data retention: maximum 1 year after last contact
- Requires Data Processing Agreements with partners
- Subject to £20 million or 4% annual turnover fines

### IR35 (Off-Payroll Working)
- Applies to contractors working through intermediaries
- Status determined by: control, mutuality of obligation, substitution
- Agency liable for tax if deemed "inside IR35"
- Determination Notice from HMRC binding
- Exceptions: genuinely self-employed, low earnings threshold

### Right to Work
- Mandatory check before hiring anyone in UK
- Must verify identity and right to work status
- EU nationals now require visa sponsorship (post-Brexit)
- Employers liable for illegal working (£15,000 per person)
- Acceptable documents: Passport, visa, work permit, BRP card

### Employment Contracts
- Written terms required for contracts >1 month
- Statutory rights: minimum wage, working time, holidays
- National Minimum Wage: £11.44/hour (over 23 years) as of April 2024
- Working Time Regulations: 48-hour max week (averaged), 11-hour rest

## Industry Best Practices

### Recruitment Process
- Typical pipeline: Sourcing → Screening → Interview → Offer → Onboarding
- Average time-to-hire: 23 days (UK average)
- Notice period: 1 week minimum by law, typically 1-3 months in practice
- Interview stages: Usually 2-3 rounds for senior roles

### Diversity & Inclusion
- Companies Act 2006: Large firms must disclose gender pay gap
- Requirement: 40% female representation on boards (FTSE 350)
- Race Report: Underrepresentation in tech, finance sectors
- Best practice: Blind CV review, diverse interview panels

### Candidate Experience
- Feedback should be provided within 5 working days
- Rejection rate: average 95%+ (only ~5% get offers)
- Offer negotiation: 10-15% salary variation typical
- Contract clarity: Written confirmation before start date

## Market Data & Trends

### Salary Information
- Tech roles: 10-15% premium over national average
- London premium: 20-25% higher than regional average
- Remote roles: 5-10% lower salary (cost of living adjustment)
- Senior roles (5+ years): 30-50% salary increase potential

### Market Trends (2024-2025)
- Shift to remote-first companies continues
- AI/ML skills: 40% salary premium
- Healthcare recruiting: Growing demand (+15% YoY)
- Financial services: Stable but competitive hiring

## Key Contacts & Resources
- CIPD (Chartered Institute of Personnel Development) - Professional body
- ICE (Institute of Recruitment Professionals) - Industry standards
- ACAS (Advisory, Conciliation and Arbitration Service) - Employment law
- GOV.UK - Official right-to-work checks and legislation
"""

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process industry knowledge query.

        Steps:
        1. Validate request
        2. Identify relevant knowledge domains
        3. Extract relevant sources
        4. Call Groq API with source context
        5. Ensure response cites sources

        Args:
            request: AgentRequest with query and context

        Returns:
            AgentResponse with domain-specific answer and source citations
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

            # Identify relevant knowledge domains
            domains = self._identify_knowledge_domains(request.query)

            # Extract relevant sources
            relevant_sources = self._extract_relevant_sources(domains)

            # Call Groq API with source context
            response = await self._generate_response_with_sources(
                request.query,
                relevant_sources,
                request
            )

            latency_ms = int((time.time() - start_time) * 1000)

            return AgentResponse(
                success=True,
                content=response,
                metadata={
                    'agent_latency_ms': latency_ms,
                    'sources': domains,
                    'domains_matched': len(domains),
                    'source_quality': 'validated'
                }
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning("industry_knowledge_timeout", latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error="Industry knowledge lookup timed out"
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("industry_knowledge_error", error=str(e), latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error=f"Industry knowledge error: {str(e)}"
            )

    def _identify_knowledge_domains(self, query: str) -> List[str]:
        """
        Identify relevant knowledge domains from query.

        Args:
            query: User query

        Returns:
            List of relevant domain keywords
        """
        query_lower = query.lower()

        # Map keywords to knowledge domains
        domain_keywords = {
            'GDPR': ['gdpr', 'data protection', 'privacy', 'compliance', 'consent', 'storage', 'gdpr'],
            'IR35': ['ir35', 'off-payroll', 'contractor', 'intermediary', 'self-employed'],
            'Right-to-Work': ['right to work', 'visa', 'sponsorship', 'immigration', 'brexit', 'eu nationals'],
            'Employment Law': ['contract', 'employment', 'minimum wage', 'working time', 'statutory', 'legal'],
            'Diversity': ['diversity', 'gender pay gap', 'inclusion', 'discrimination', 'equal'],
            'Recruitment Process': ['process', 'pipeline', 'time-to-hire', 'offer', 'onboarding'],
            'Salary': ['salary', 'wages', 'compensation', 'pay', 'rates', 'benchmark'],
            'Market Trends': ['trend', 'market', 'demand', 'premium', 'remote', 'ai/ml'],
            'Best Practices': ['best practice', 'standard', 'guideline', 'recommendation'],
        }

        found_domains = []
        for domain, keywords in domain_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_domains.append(domain)
                    break

        return found_domains if found_domains else ['General Recruitment Knowledge']

    def _extract_relevant_sources(self, domains: List[str]) -> str:
        """
        Extract relevant sections from sources file.

        Args:
            domains: Knowledge domains to extract

        Returns:
            Relevant source content
        """
        if not self.sources_content:
            return ""

        relevant = []
        sources_lines = self.sources_content.split('\n')

        for domain in domains:
            for i, line in enumerate(sources_lines):
                if domain.lower() in line.lower():
                    # Extract section around match
                    start = max(0, i - 2)
                    end = min(len(sources_lines), i + 15)
                    section = '\n'.join(sources_lines[start:end])
                    if section not in relevant:
                        relevant.append(section)

        return '\n\n'.join(relevant) if relevant else self.sources_content[:1000]

    async def _generate_response_with_sources(
        self,
        query: str,
        sources: str,
        request: AgentRequest
    ) -> str:
        """
        Generate response using Groq API with source context.

        Args:
            query: Original user query
            sources: Relevant source material
            request: Original agent request

        Returns:
            Response with source citations
        """
        prompt = f"""You are a UK recruitment industry expert with access to validated sources.

User Query: {query}

VALIDATED SOURCES:
{sources}

Please provide a comprehensive, accurate answer to the user's question based on the validated sources above.

Requirements:
1. Answer the question directly and clearly
2. Cite specific sources when providing information
3. Include relevant regulations, best practices, or market data
4. If uncertain, indicate that the information may require professional legal advice
5. Focus on UK-specific guidance when applicable
6. Keep response to 200-250 words

Format: Use clear paragraphs and bullet points for key information."""

        try:
            message = await asyncio.wait_for(
                asyncio.to_thread(
                    self._call_groq_api,
                    prompt
                ),
                timeout=self.timeout - 0.5
            )

            return message

        except (asyncio.TimeoutError, Exception) as e:
            logger.error("groq_api_error", error=str(e))
            return self._generate_fallback_response(query)

    def _call_groq_api(self, prompt: str) -> str:
        """
        Call Groq API synchronously.

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
            temperature=0.2  # Very low temperature for factual accuracy
        )

        return message.choices[0].message.content

    def _generate_fallback_response(self, query: str) -> str:
        """
        Generate fallback response if API fails.

        Args:
            query: Original query

        Returns:
            Fallback response
        """
        return f"""Based on UK recruitment industry knowledge:

For your query: "{query}"

I recommend:
1. Consulting the CIPD (Chartered Institute of Personnel Development) for professional guidance
2. Reviewing GOV.UK official pages for regulatory requirements
3. Contacting ACAS for employment law clarification if needed
4. Seeking professional legal advice for compliance-critical matters

For current regulatory updates and best practices, please consult official sources as recruitment regulations are regularly updated."""

    def get_category(self) -> Category:
        """Return the category this agent handles."""
        return Category.INDUSTRY_KNOWLEDGE

    def validate_request(self, request: AgentRequest) -> bool:
        """
        Validate request for industry knowledge agent.

        Args:
            request: Agent request

        Returns:
            True if valid, False otherwise
        """
        # Call parent validation
        if not super().validate_request(request):
            return False

        # Check for minimum query length
        if len(request.query.strip()) < 5:
            return False

        return True
