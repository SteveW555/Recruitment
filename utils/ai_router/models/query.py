"""
Query Model - Represents user input requiring classification and routing.

Handles query validation, word counting, and truncation per FR-001 requirements.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class Query:
    """
    User input message requiring classification and routing.

    Attributes:
        id: Unique identifier (UUID)
        text: User's question/request content (max 1000 words)
        user_id: Identifier of the user making the query
        session_id: Session this query belongs to
        timestamp: When query was received (UTC)
        word_count: Number of words in query text
        truncated: Whether query exceeded 1000 words
        context_messages: Previous messages from session for context
    """

    text: str
    user_id: str
    session_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    word_count: int = field(init=False)
    truncated: bool = field(default=False, init=False)
    context_messages: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        """Validate and process query after initialization."""
        # Validate required fields
        if not self.text or not self.text.strip():
            raise ValueError("Query text cannot be empty or whitespace-only")

        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")

        if not self.session_id:
            raise ValueError("Session ID is required")

        # Validate UUID format for session_id
        try:
            uuid.UUID(self.session_id)
        except ValueError:
            raise ValueError(f"Invalid session_id format: {self.session_id}. Must be valid UUID v4")

        # Count words and truncate if necessary
        self._process_text()

    def _process_text(self):
        """Count words and truncate text if exceeds 1000 words."""
        words = self.text.split()
        self.word_count = len(words)

        if self.word_count > 1000:
            # Truncate to first 1000 words
            truncated_words = words[:1000]
            self.text = " ".join(truncated_words)
            self.word_count = 1000
            self.truncated = True

    def to_dict(self) -> Dict:
        """
        Convert query to dictionary for serialization.

        Returns:
            Dictionary representation of query
        """
        return {
            "id": self.id,
            "text": self.text,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "word_count": self.word_count,
            "truncated": self.truncated,
            "context_messages": self.context_messages,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Query":
        """
        Create Query from dictionary.

        Args:
            data: Dictionary with query data

        Returns:
            Query instance
        """
        # Parse timestamp if it's a string
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            text=data["text"],
            user_id=data["user_id"],
            session_id=data["session_id"],
            timestamp=timestamp or datetime.utcnow(),
            context_messages=data.get("context_messages", []),
        )

    def add_context_message(self, role: str, content: str, category: Optional[str] = None):
        """
        Add a message to the context history.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            category: Optional category for routing context
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if category:
            message["category"] = category

        self.context_messages.append(message)

    def get_truncation_warning(self) -> Optional[str]:
        """
        Get warning message if query was truncated.

        Returns:
            Warning message or None if not truncated
        """
        if self.truncated:
            return (
                f"Your query was truncated to 1000 words for processing. "
                f"Original length: {self.word_count + len(self.text.split()) - 1000} words."
            )
        return None

    def __str__(self) -> str:
        """String representation of query."""
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Query(id={self.id[:8]}, user={self.user_id}, text='{preview}')"

    def __repr__(self) -> str:
        """Detailed representation of query."""
        return (
            f"Query(id={self.id}, user_id={self.user_id}, "
            f"session_id={self.session_id}, word_count={self.word_count}, "
            f"truncated={self.truncated})"
        )
