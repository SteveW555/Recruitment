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
import os
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

            # Generate response with session context for conversation history
            response, llm_error = await self._generate_response(
                request.query,
                is_fallback,
                request.context
            )

            latency_ms = int((time.time() - start_time) * 1000)

            metadata = {
                'agent_latency_ms': latency_ms,
                'fallback': is_fallback
            }

            # Add LLM error info if API failed
            if llm_error:
                metadata['llm_error'] = llm_error
                metadata['used_fallback_response'] = True

            return AgentResponse(
                success=True,
                content=response,
                metadata=metadata
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

    async def _generate_response(self, query: str, is_fallback: bool = False, context_dict = None) -> tuple:
        """
        Generate casual conversation response.

        Args:
            query: User query
            is_fallback: Whether this is a fallback response
            context_dict: Context dictionary with conversation history

        Returns:
            Tuple of (response_text, error_message_or_none)
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
                    prompt,
                    context_dict
                ),
                timeout=self.timeout - 0.5
            )

            return (message, None)  # Success - no error

        except Exception as e:
            error_msg = str(e)
            logger.error("groq_api_error", error=error_msg)
            fallback = self._generate_fallback_response(query, is_fallback)
            return (fallback, error_msg)  # Return fallback + error

    def _call_groq_api(self, prompt: str, context_dict = None) -> str:
        """
        Call Groq API synchronously with conversation history.

        Args:
            prompt: Prompt for Groq
            context_dict: Context dictionary with conversation history

        Returns:
            Response from Groq
        """
        # Build messages array with history
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        # Add conversation history if available (last 10 messages)
        if context_dict and isinstance(context_dict, dict):
            message_history = context_dict.get('message_history', [])
            # Get last 10 messages
            recent_messages = message_history[-10:] if len(message_history) > 10 else message_history
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add current query
        messages.append({
            "role": "user",
            "content": prompt
        })

        # Log summary of what's being sent to Groq (always)
        history_count = len(messages) - 2  # Exclude system prompt and current query
        logger.info(
            "groq_api_call",
            message_count=len(messages),
            history_messages=history_count,
            current_query_preview=prompt[:100] if len(prompt) > 100 else prompt
        )

        # Log detailed messages array if verbose mode enabled
        if os.environ.get('LOG_LLM_MESSAGES', 'false').lower() == 'true':
            logger.info("groq_messages_detailed", messages=messages)

        message = self.client.chat.completions.create(
            messages=messages,
            model=self.llm_model,
            max_tokens=300,
            temperature=0.7  # Slightly higher for friendlier conversation
        )

        response_content = message.choices[0].message.content

        # Log response summary
        logger.info(
            "groq_api_response",
            response_length=len(response_content),
            response_preview=response_content[:100] if len(response_content) > 100 else response_content
        )

        return response_content

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
