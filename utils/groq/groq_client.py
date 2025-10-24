"""
GROQ API Integration Module for ProActive People Recruitment System

This module provides a comprehensive interface to GROQ's LLM API with utilities
for recruitment-specific tasks including CV parsing, candidate matching,
job description generation, and more.

Author: ProActive People
Version: 1.0.0
"""

import os
import json
import time
from typing import List, Dict, Optional, Union, Any, Generator
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging
from functools import wraps
import asyncio

try:
    from groq import Groq, AsyncGroq
    from groq.types.chat import ChatCompletion, ChatCompletionMessage
except ImportError:
    raise ImportError("Please install groq: pip install groq")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class GroqModel(Enum):
    """Available GROQ models"""
    # Fast models (good for quick operations)
    LLAMA_3_8B = "llama-3.3-70b-versatile"
    LLAMA_3_70B = "llama-3.1-70b-versatile"

    # Specialized models
    MIXTRAL_8X7B = "mixtral-8x7b-32768"
    GEMMA_7B = "gemma-7b-it"
    GEMMA2_9B = "gemma2-9b-it"

    # Default recommended model
    DEFAULT = "llama-3.3-70b-versatile"


class Temperature(Enum):
    """Common temperature settings"""
    DETERMINISTIC = 0.0
    CONSERVATIVE = 0.3
    BALANCED = 0.7
    CREATIVE = 1.0
    VERY_CREATIVE = 1.5


class TaskType(Enum):
    """Common recruitment task types"""
    CV_PARSING = "cv_parsing"
    JOB_MATCHING = "job_matching"
    JOB_DESCRIPTION = "job_description"
    EMAIL_GENERATION = "email_generation"
    INTERVIEW_QUESTIONS = "interview_questions"
    CANDIDATE_SUMMARY = "candidate_summary"
    SKILL_EXTRACTION = "skill_extraction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    GENERAL = "general"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Message:
    """Chat message structure"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API calls"""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class CompletionConfig:
    """Configuration for completion requests"""
    model: str = GroqModel.DEFAULT.value
    temperature: float = Temperature.BALANCED.value
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    stream: bool = False
    stop: Optional[List[str]] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    n: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class GroqResponse:
    """Structured response from GROQ API"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    created_at: datetime
    raw_response: Optional[ChatCompletion] = None

    @classmethod
    def from_completion(cls, completion: ChatCompletion) -> 'GroqResponse':
        """Create GroqResponse from API completion"""
        return cls(
            content=completion.choices[0].message.content,
            model=completion.model,
            usage={
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            },
            finish_reason=completion.choices[0].finish_reason,
            created_at=datetime.fromtimestamp(completion.created),
            raw_response=completion
        )


# ============================================================================
# DECORATORS
# ============================================================================

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator for API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator


def log_completion(func):
    """Logging decorator for completions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"Completed {func.__name__} in {elapsed:.2f}s")
        return result
    return wrapper


# ============================================================================
# MAIN GROQ CLIENT CLASS
# ============================================================================

class GroqClient:
    """
    Comprehensive GROQ API client with utilities for recruitment tasks
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GROQ client

        Args:
            api_key: GROQ API key (defaults to GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ API key not found. Set GROQ_API_KEY environment variable.")

        self.client = Groq(api_key=self.api_key)
        self.async_client = AsyncGroq(api_key=self.api_key)

        # Conversation history storage
        self.conversations: Dict[str, List[Message]] = {}

        logger.info("GroqClient initialized successfully")

    # ========================================================================
    # CORE COMPLETION METHODS
    # ========================================================================

    @retry_on_error(max_retries=3)
    @log_completion
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        config: Optional[CompletionConfig] = None,
        conversation_id: Optional[str] = None
    ) -> GroqResponse:
        """
        Generate a completion for a given prompt

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            config: Completion configuration
            conversation_id: Optional ID to maintain conversation history

        Returns:
            GroqResponse object
        """
        if config is None:
            config = CompletionConfig()

        messages = []

        # Add system prompt
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))

        # Add conversation history if exists
        if conversation_id and conversation_id in self.conversations:
            messages.extend(self.conversations[conversation_id])

        # Add current user prompt
        messages.append(Message(role="user", content=prompt))

        # Make API call
        completion = self.client.chat.completions.create(
            messages=[msg.to_dict() for msg in messages],
            **config.to_dict()
        )

        # Store in conversation history
        if conversation_id:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            self.conversations[conversation_id].append(Message(role="user", content=prompt))
            self.conversations[conversation_id].append(
                Message(role="assistant", content=completion.choices[0].message.content)
            )

        return GroqResponse.from_completion(completion)

    @retry_on_error(max_retries=3)
    def complete_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        config: Optional[CompletionConfig] = None
    ) -> Generator[str, None, None]:
        """
        Stream a completion for a given prompt

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            config: Completion configuration

        Yields:
            Content chunks as they arrive
        """
        if config is None:
            config = CompletionConfig()

        config.stream = True

        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))

        stream = self.client.chat.completions.create(
            messages=[msg.to_dict() for msg in messages],
            **config.to_dict()
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def complete_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        config: Optional[CompletionConfig] = None
    ) -> GroqResponse:
        """
        Asynchronous completion

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            config: Completion configuration

        Returns:
            GroqResponse object
        """
        if config is None:
            config = CompletionConfig()

        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))

        completion = await self.async_client.chat.completions.create(
            messages=[msg.to_dict() for msg in messages],
            **config.to_dict()
        )

        return GroqResponse.from_completion(completion)

    # ========================================================================
    # RECRUITMENT-SPECIFIC METHODS
    # ========================================================================

    def parse_cv(
        self,
        cv_text: str,
        extract_skills: bool = True,
        extract_experience: bool = True,
        extract_education: bool = True
    ) -> Dict[str, Any]:
        """
        Parse a CV and extract structured information

        Args:
            cv_text: Raw CV text
            extract_skills: Whether to extract skills
            extract_experience: Whether to extract work experience
            extract_education: Whether to extract education

        Returns:
            Structured CV data
        """
        system_prompt = """You are an expert CV parser for a recruitment agency.
Extract structured information from CVs in JSON format.
Be thorough and accurate. Extract all relevant information."""

        user_prompt = f"""Parse this CV and extract:
- Personal information (name, email, phone, location)
{"- Skills and competencies" if extract_skills else ""}
{"- Work experience (company, role, dates, responsibilities)" if extract_experience else ""}
{"- Education (institution, degree, dates)" if extract_education else ""}
- Summary/objective
- Languages
- Certifications

CV Text:
{cv_text}

Return ONLY valid JSON with the structure:
{{
  "personal_info": {{"name": "", "email": "", "phone": "", "location": ""}},
  "skills": [],
  "experience": [],
  "education": [],
  "summary": "",
  "languages": [],
  "certifications": []
}}"""

        config = CompletionConfig(
            temperature=Temperature.CONSERVATIVE.value,
            max_tokens=2000
        )

        response = self.complete(user_prompt, system_prompt, config)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse CV response as JSON")
            return {"raw_response": response.content}

    def match_candidate_to_job(
        self,
        candidate_profile: Dict[str, Any],
        job_description: str,
        return_score: bool = True
    ) -> Dict[str, Any]:
        """
        Match a candidate to a job and provide analysis

        Args:
            candidate_profile: Structured candidate data
            job_description: Job description text
            return_score: Whether to include a match score

        Returns:
            Match analysis with score and recommendations
        """
        system_prompt = """You are an expert recruitment consultant specializing in candidate-job matching.
Analyze compatibility between candidates and job requirements."""

        user_prompt = f"""Analyze the match between this candidate and job:

CANDIDATE:
{json.dumps(candidate_profile, indent=2)}

JOB DESCRIPTION:
{job_description}

Provide analysis in JSON format:
{{
  "match_score": 0-100,
  "strengths": ["list of matching qualifications"],
  "gaps": ["list of missing qualifications"],
  "recommendations": ["suggestions for interview or placement"],
  "summary": "brief assessment"
}}"""

        config = CompletionConfig(
            temperature=Temperature.BALANCED.value,
            max_tokens=1500
        )

        response = self.complete(user_prompt, system_prompt, config)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse matching response as JSON")
            return {"raw_response": response.content}

    def generate_job_description(
        self,
        job_title: str,
        company_name: str,
        department: Optional[str] = None,
        key_responsibilities: Optional[List[str]] = None,
        required_skills: Optional[List[str]] = None,
        salary_range: Optional[str] = None,
        location: Optional[str] = None,
        work_type: Optional[str] = "Full-time"
    ) -> str:
        """
        Generate a professional job description

        Args:
            job_title: Job title
            company_name: Company name
            department: Department/team
            key_responsibilities: List of main responsibilities
            required_skills: Required skills and qualifications
            salary_range: Salary information
            location: Job location
            work_type: Employment type (Full-time, Part-time, Contract, etc.)

        Returns:
            Formatted job description
        """
        system_prompt = """You are an expert recruitment copywriter.
Create compelling, professional job descriptions that attract top talent."""

        details = f"""Job Title: {job_title}
Company: {company_name}
{"Department: " + department if department else ""}
{"Location: " + location if location else ""}
{"Work Type: " + work_type if work_type else ""}
{"Salary: " + salary_range if salary_range else ""}
{"Key Responsibilities: " + json.dumps(key_responsibilities) if key_responsibilities else ""}
{"Required Skills: " + json.dumps(required_skills) if required_skills else ""}"""

        user_prompt = f"""Create a professional job description with these details:

{details}

Include:
1. Engaging company introduction
2. Role overview
3. Key responsibilities
4. Required qualifications and skills
5. Desirable qualifications
6. Benefits and perks
7. Application instructions

Make it compelling and professional."""

        config = CompletionConfig(
            temperature=Temperature.CREATIVE.value,
            max_tokens=2000
        )

        response = self.complete(user_prompt, system_prompt, config)
        return response.content

    def generate_email(
        self,
        email_type: str,
        recipient_name: str,
        context: Dict[str, Any],
        tone: str = "professional"
    ) -> str:
        """
        Generate recruitment emails

        Args:
            email_type: Type of email (e.g., 'interview_invitation', 'rejection', 'offer')
            recipient_name: Recipient's name
            context: Additional context (job title, interview details, etc.)
            tone: Email tone (professional, friendly, formal)

        Returns:
            Email content
        """
        system_prompt = f"""You are an expert recruitment communication specialist.
Write {tone} emails for various recruitment scenarios."""

        user_prompt = f"""Write a {email_type} email to {recipient_name}.

Context:
{json.dumps(context, indent=2)}

Include:
- Appropriate greeting
- Clear message body
- Professional closing
- Call to action if needed

Tone: {tone}"""

        config = CompletionConfig(
            temperature=Temperature.BALANCED.value,
            max_tokens=800
        )

        response = self.complete(user_prompt, system_prompt, config)
        return response.content

    def generate_interview_questions(
        self,
        job_title: str,
        required_skills: List[str],
        experience_level: str = "mid",
        num_questions: int = 10,
        include_behavioral: bool = True,
        include_technical: bool = True
    ) -> List[Dict[str, str]]:
        """
        Generate interview questions for a position

        Args:
            job_title: Job title
            required_skills: List of required skills
            experience_level: junior, mid, senior, or executive
            num_questions: Number of questions to generate
            include_behavioral: Include behavioral questions
            include_technical: Include technical questions

        Returns:
            List of questions with categories
        """
        system_prompt = """You are an expert interviewer and talent assessor.
Generate insightful interview questions tailored to specific roles."""

        user_prompt = f"""Generate {num_questions} interview questions for:

Job Title: {job_title}
Experience Level: {experience_level}
Required Skills: {', '.join(required_skills)}
{"Include behavioral questions" if include_behavioral else ""}
{"Include technical questions" if include_technical else ""}

Return as JSON array:
[
  {{"question": "...", "category": "technical|behavioral|situational", "skill_assessed": "..."}},
  ...
]"""

        config = CompletionConfig(
            temperature=Temperature.BALANCED.value,
            max_tokens=2000
        )

        response = self.complete(user_prompt, system_prompt, config)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse interview questions as JSON")
            return []

    def extract_skills(
        self,
        text: str,
        categorize: bool = True
    ) -> Union[List[str], Dict[str, List[str]]]:
        """
        Extract skills from text (CV, job description, etc.)

        Args:
            text: Text to analyze
            categorize: Whether to categorize skills (technical, soft, domain)

        Returns:
            List of skills or categorized dictionary
        """
        system_prompt = """You are an expert at identifying professional skills and competencies."""

        if categorize:
            user_prompt = f"""Extract and categorize all skills from this text:

{text}

Return JSON:
{{
  "technical": [],
  "soft_skills": [],
  "domain_knowledge": [],
  "tools_and_technologies": []
}}"""
        else:
            user_prompt = f"""Extract all skills mentioned in this text as a simple JSON array:

{text}

Return: ["skill1", "skill2", ...]"""

        config = CompletionConfig(
            temperature=Temperature.CONSERVATIVE.value,
            max_tokens=1000
        )

        response = self.complete(user_prompt, system_prompt, config)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse skills as JSON")
            return [] if not categorize else {}

    def summarize_candidate(
        self,
        candidate_data: Dict[str, Any],
        max_length: int = 200
    ) -> str:
        """
        Create a concise candidate summary

        Args:
            candidate_data: Candidate information
            max_length: Maximum words for summary

        Returns:
            Candidate summary
        """
        system_prompt = """You are an expert at creating concise, impactful candidate summaries."""

        user_prompt = f"""Create a {max_length}-word professional summary for this candidate:

{json.dumps(candidate_data, indent=2)}

Highlight:
- Key strengths
- Relevant experience
- Notable achievements
- Career trajectory"""

        config = CompletionConfig(
            temperature=Temperature.BALANCED.value,
            max_tokens=500
        )

        response = self.complete(user_prompt, system_prompt, config)
        return response.content

    def analyze_sentiment(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text (feedback, reviews, etc.)

        Args:
            text: Text to analyze
            context: Optional context

        Returns:
            Sentiment analysis
        """
        system_prompt = """You are an expert in sentiment analysis and text interpretation."""

        user_prompt = f"""Analyze the sentiment of this text:

{text}

{f"Context: {context}" if context else ""}

Return JSON:
{{
  "sentiment": "positive|negative|neutral|mixed",
  "confidence": 0.0-1.0,
  "key_themes": [],
  "emotional_tone": "",
  "summary": ""
}}"""

        config = CompletionConfig(
            temperature=Temperature.CONSERVATIVE.value,
            max_tokens=800
        )

        response = self.complete(user_prompt, system_prompt, config)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse sentiment analysis as JSON")
            return {"raw_response": response.content}

    # ========================================================================
    # AGENT ROUTING METHODS (Independent Model for Experimentation)
    # ========================================================================

    def route_query_to_agent(
        self,
        query: str,
        available_agents: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        routing_model: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Use LLM to intelligently route queries to the most appropriate agent.

        This function is INDEPENDENT of other Groq operations and uses its own
        model configuration, allowing experimentation with different models
        for routing decisions without affecting agent execution.

        Args:
            query: User query to route
            available_agents: List of agent definitions with descriptions
                Example: [
                    {
                        "name": "INFORMATION_RETRIEVAL",
                        "description": "Searches and retrieves data",
                        "examples": ["Find candidates", "Show jobs"]
                    },
                    ...
                ]
            conversation_history: Optional conversation context (last 3-5 messages)
            routing_model: Model to use for routing (default: llama-3.3-70b-versatile)
                Options: "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"
            temperature: Temperature for routing decisions (default: 0.3 for consistency)
            return_reasoning: Include reasoning in response

        Returns:
            Dict with routing decision:
            {
                "agent": "INFORMATION_RETRIEVAL",
                "confidence": 0.85,
                "reasoning": "Query asks to find candidates...",
                "is_followup": True/False,
                "model_used": "llama-3.3-70b-versatile"
            }
        """
        # Default to fast, balanced model for routing
        if routing_model is None:
            routing_model = GroqModel.DEFAULT.value

        # Build system prompt for routing
        system_prompt = """You are an intelligent query router for ProActive People, a UK recruitment agency AI system.

Your job is to analyze user queries and route them to the most appropriate specialized agent based on:

**Routing Guidelines:**
1. **INFORMATION_RETRIEVAL** - Searches, lookups, "find", "show", "get", "search" queries about candidates, jobs, clients
2. **PROBLEM_SOLVING** - Complex analysis, troubleshooting, "why", "how to solve", strategic questions
3. **REPORT_GENERATION** - Requests for reports, summaries, dashboards, analytics, "generate report"
4. **AUTOMATION** - Workflow design, process automation, "automate", "workflow"
5. **INDUSTRY_KNOWLEDGE** - UK recruitment law, GDPR, IR35, compliance, best practices
6. **GENERAL_CHAT** - Greetings, casual conversation, off-topic, unclear intent

**Context Awareness:**
- If the query is very short (1-3 words) and there's conversation history, it's likely a follow-up
- Examples: "show the first 5", "what about Manchester?", "tell me more"

**Confidence Guidelines:**
- 0.9-1.0: Obvious intent with clear keywords
- 0.7-0.9: Strong match but some ambiguity
- 0.5-0.7: Moderate match, could fit multiple agents
- Below 0.5: Unclear intent, route to GENERAL_CHAT

Return ONLY valid JSON with this structure (no markdown, no extra text):
{
  "agent": "AGENT_NAME",
  "confidence": 0.85,
  "reasoning": "Brief explanation of why this agent",
  "is_followup": false
}"""

        # Build agent descriptions
        agent_descriptions = []
        for agent in available_agents:
            desc = f"**{agent['name']}**: {agent.get('description', '')}"
            if 'examples' in agent and agent['examples']:
                examples = ', '.join(agent['examples'][:3])
                desc += f"\n  Examples: {examples}"
            agent_descriptions.append(desc)

        agents_text = "\n\n".join(agent_descriptions)

        # Build context section
        context_text = ""
        if conversation_history and len(conversation_history) > 0:
            context_text = "\n\n**CONVERSATION CONTEXT (last few messages):**\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')[:100]  # Truncate long messages
                context_text += f"- {role}: {content}\n"

        # Build user prompt
        user_prompt = f"""Route this query to the best agent:

**QUERY:** "{query}"
{context_text}

**AVAILABLE AGENTS:**
{agents_text}

Analyze the query and determine:
1. Which agent is best suited?
2. How confident are you? (0.0-1.0)
3. Is this a follow-up to the previous conversation?
4. Why is this agent the best choice?

Return ONLY the JSON response."""

        # Create independent config for routing
        routing_config = CompletionConfig(
            model=routing_model,
            temperature=temperature,
            max_tokens=300
        )

        try:
            # Call LLM for routing decision
            response = self.complete(user_prompt, system_prompt, routing_config)

            # Parse JSON response
            routing_decision = self.validate_json_response(response.content)

            if routing_decision is None:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse routing response, using fallback")
                return {
                    "agent": "GENERAL_CHAT",
                    "confidence": 0.5,
                    "reasoning": "Could not determine best agent",
                    "is_followup": False,
                    "model_used": routing_model,
                    "error": "JSON parsing failed"
                }

            # Add metadata
            routing_decision["model_used"] = routing_model
            routing_decision["tokens_used"] = response.usage.get('total_tokens', 0)

            return routing_decision

        except Exception as e:
            logger.error(f"Routing error: {str(e)}")
            return {
                "agent": "GENERAL_CHAT",
                "confidence": 0.0,
                "reasoning": f"Routing failed: {str(e)}",
                "is_followup": False,
                "model_used": routing_model,
                "error": str(e)
            }

    def compare_routing_models(
        self,
        query: str,
        available_agents: List[Dict[str, Any]],
        models_to_test: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare how different models route the same query.
        Useful for finding the best routing model for your use case.

        Args:
            query: Query to test
            available_agents: List of agent definitions
            models_to_test: Models to compare (default: 3 common models)

        Returns:
            Dict mapping model names to routing decisions
        """
        if models_to_test is None:
            models_to_test = [
                "llama-3.3-70b-versatile",  # Default, balanced
                "mixtral-8x7b-32768",        # Good at reasoning
                "gemma2-9b-it"               # Smaller, faster
            ]

        results = {}

        for model in models_to_test:
            try:
                decision = self.route_query_to_agent(
                    query=query,
                    available_agents=available_agents,
                    routing_model=model
                )
                results[model] = decision
            except Exception as e:
                results[model] = {"error": str(e)}

        return results

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def batch_complete(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        config: Optional[CompletionConfig] = None,
        max_concurrent: int = 5
    ) -> List[GroqResponse]:
        """
        Process multiple prompts in batch

        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt
            config: Completion configuration
            max_concurrent: Maximum concurrent requests

        Returns:
            List of responses
        """
        async def process_batch():
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_one(prompt):
                async with semaphore:
                    return await self.complete_async(prompt, system_prompt, config)

            tasks = [process_one(prompt) for prompt in prompts]
            return await asyncio.gather(*tasks)

        return asyncio.run(process_batch())

    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation: {conversation_id}")

    def get_conversation_history(self, conversation_id: str) -> List[Message]:
        """Get conversation history"""
        return self.conversations.get(conversation_id, [])

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        return len(text) // 4

    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = GroqModel.DEFAULT.value
    ) -> float:
        """
        Calculate approximate cost for API usage
        Note: GROQ pricing may vary, update these rates

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            model: Model used

        Returns:
            Estimated cost in USD
        """
        # Example pricing (update with actual GROQ pricing)
        pricing = {
            GroqModel.LLAMA_3_8B.value: {"prompt": 0.05 / 1_000_000, "completion": 0.08 / 1_000_000},
            GroqModel.LLAMA_3_70B.value: {"prompt": 0.59 / 1_000_000, "completion": 0.79 / 1_000_000},
            GroqModel.MIXTRAL_8X7B.value: {"prompt": 0.27 / 1_000_000, "completion": 0.27 / 1_000_000},
        }

        rates = pricing.get(model, pricing[GroqModel.DEFAULT.value])
        cost = (prompt_tokens * rates["prompt"]) + (completion_tokens * rates["completion"])
        return cost

    def validate_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Validate and parse JSON response

        Args:
            response: Response string

        Returns:
            Parsed JSON or None
        """
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"JSON validation failed: {str(e)}")
            return None

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics for the current session

        Returns:
            Usage statistics
        """
        # This would need to be implemented with proper tracking
        # Placeholder implementation
        return {
            "total_conversations": len(self.conversations),
            "total_messages": sum(len(msgs) for msgs in self.conversations.values())
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_groq_client(api_key: Optional[str] = None) -> GroqClient:
    """
    Factory function to create a GroqClient instance

    Args:
        api_key: Optional API key

    Returns:
        GroqClient instance
    """
    return GroqClient(api_key)


def quick_complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = GroqModel.DEFAULT.value,
    temperature: float = 0.7,
    api_key: Optional[str] = None
) -> str:
    """
    Quick completion helper for simple tasks

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        model: Model to use
        temperature: Temperature setting
        api_key: Optional API key

    Returns:
        Completion text
    """
    client = GroqClient(api_key)
    config = CompletionConfig(model=model, temperature=temperature)
    response = client.complete(prompt, system_prompt, config)
    return response.content


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize client
    groq = GroqClient()

    # Example 1: Simple completion
    print("=== Example 1: Simple Completion ===")
    response = groq.complete(
        "Explain the role of an AI in recruitment in 2 sentences.",
        config=CompletionConfig(max_tokens=150)
    )
    print(f"Response: {response.content}\n")
    print(f"Tokens used: {response.usage['total_tokens']}\n")

    # Example 2: CV Parsing
    print("=== Example 2: CV Parsing ===")
    sample_cv = """
    John Smith
    Email: john.smith@email.com
    Phone: +44 7700 900000

    EXPERIENCE:
    Senior Sales Manager at TechCorp (2020-2024)
    - Led team of 15 sales representatives
    - Increased revenue by 35%

    SKILLS:
    Leadership, Salesforce, B2B Sales, Negotiation

    EDUCATION:
    BSc Business Management, University of Bristol (2016-2019)
    """

    parsed_cv = groq.parse_cv(sample_cv)
    print(f"Parsed CV:\n{json.dumps(parsed_cv, indent=2)}\n")

    # Example 3: Job Description Generation
    print("=== Example 3: Job Description Generation ===")
    job_desc = groq.generate_job_description(
        job_title="Senior Sales Executive",
        company_name="ProActive People",
        location="Bristol, UK",
        required_skills=["B2B Sales", "Account Management", "CRM Systems"],
        salary_range="£35,000 - £45,000 + Commission"
    )
    print(f"Job Description:\n{job_desc}\n")

    # Example 4: Streaming completion
    print("=== Example 4: Streaming Completion ===")
    print("Streaming response: ", end="")
    for chunk in groq.complete_stream("Write a brief introduction to ProActive People recruitment agency."):
        print(chunk, end="", flush=True)
    print("\n")

    # Example 5: Interview Questions
    print("=== Example 5: Interview Questions ===")
    questions = groq.generate_interview_questions(
        job_title="Software Engineer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        experience_level="mid",
        num_questions=5
    )
    print(f"Interview Questions:\n{json.dumps(questions, indent=2)}\n")

    print("=== All examples completed successfully! ===")
