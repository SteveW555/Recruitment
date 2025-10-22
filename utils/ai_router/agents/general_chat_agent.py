"""
General Chat Agent - Friendly fallback agent for casual conversation.

Handles:
- Greetings and casual conversation
- Off-topic queries
- Fallback when other agents fail
- General assistance

Uses Groq API for quick responses.
"""

import asyncio
import time
from typing import Dict, Any
import structlog
from groq import Groq

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


logger = structlog.get_logger()


class GeneralChatAgent(BaseAgent):
    """
    General Chat Agent for casual conversation and fallback.

    Specializes in:
    - Greeting responses
    - Off-topic conversation
    - General assistance
    - Fallback handling

    Uses Groq for friendly, conversational responses.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize General Chat Agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Initialize Groq client
        self.client = Groq()

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process casual conversation query.

        Args:
            request: AgentRequest with query and context

        Returns:
            AgentResponse with friendly response
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

            # Check if this is a fallback scenario
            is_fallback = request.metadata.get('fallback', False)

            # Generate response
            response = await self._generate_response(request.query, is_fallback)

            latency_ms = int((time.time() - start_time) * 1000)

            return AgentResponse(
                success=True,
                content=response,
                metadata={
                    'agent_latency_ms': latency_ms,
                    'fallback': is_fallback
                }
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning("general_chat_timeout", latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error="General chat timed out"
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("general_chat_error", error=str(e), latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error=f"General chat error: {str(e)}"
            )

    async def _generate_response(self, query: str, is_fallback: bool = False) -> str:
        """
        Generate casual conversation response.

        Args:
            query: User query
            is_fallback: Whether this is a fallback response

        Returns:
            Response text
        """
        if is_fallback:
            prompt = f"""The user asked a question that another specialist agent couldn't handle fully. Please provide a helpful, friendly response that:

1. Acknowledges their question
2. Explains the limitation of the previous agent
3. Offers general assistance or alternative approaches
4. Suggests they might want to ask a more specific question

User Query: {query}

Keep response to 100-150 words and be friendly and helpful."""
        else:
            prompt = f"""User Query: {query}

Please respond naturally and conversationally. Keep your response brief and friendly (under 100 words). If this seems like it might be better handled by a specialist, you can suggest that they ask about specific topics like:
- Information retrieval (job boards, candidates, market data)
- Industry knowledge (regulations, compliance, best practices)
- Problem solving (business challenges, optimization)
- Report generation (analytics, dashboards)
- Automation (workflow design)"""

        try:
            message = await asyncio.wait_for(
                asyncio.to_thread(
                    self._call_groq_api,
                    prompt
                ),
                timeout=self.timeout - 0.5
            )

            return message

        except Exception as e:
            logger.error("groq_api_error", error=str(e))
            return self._generate_fallback_response(query, is_fallback)

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
            max_tokens=300,
            temperature=0.7  # Slightly higher for friendlier conversation
        )

        return message.choices[0].message.content

    def _generate_fallback_response(self, query: str, is_fallback: bool) -> str:
        """
        Generate fallback response if API fails.

        Args:
            query: Original query
            is_fallback: Whether this is a fallback response

        Returns:
            Fallback response
        """
        if is_fallback:
            return "I apologize, but I encountered an issue processing your request. Could you try rephrasing your question or asking about something more specific? I'm here to help!"
        else:
            query_lower = query.lower()
            if any(greeting in query_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
                return "Hello! How can I assist you with your recruitment needs today?"
            elif any(question in query_lower for question in ['how are you', 'how\'s it going', 'what\'s up']):
                return "I'm doing great, thanks for asking! How can I help you?"
            elif 'joke' in query_lower:
                return "Why did the recruiter go to the bank? To check their candidate reserves!"
            elif 'weather' in query_lower:
                return "I don't have weather information, but I hope it's a great day for recruitment!"
            else:
                return f"Thanks for your message! I'd be happy to help. For recruitment-specific questions, feel free to ask about job boards, industry regulations, hiring strategies, or market insights."

    def get_category(self) -> Category:
        """Return the category this agent handles."""
        return Category.GENERAL_CHAT

    def validate_request(self, request: AgentRequest) -> bool:
        """
        Validate request for general chat agent.

        Args:
            request: Agent request

        Returns:
            True if valid, False otherwise
        """
        # General chat agent accepts anything that's non-empty
        return len(request.query.strip()) > 0
