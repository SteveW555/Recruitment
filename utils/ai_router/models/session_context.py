"""
SessionContext Model - Conversation state tracking with Redis TTL management.

Manages session history, routing context, and user preferences with automatic expiration.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional


@dataclass
class SessionContext:
    """
    Conversation state tracking previous messages, routing decisions, and user preferences.

    Attributes:
        session_id: Unique session identifier (UUID)
        user_id: User this session belongs to
        created_at: When session started (UTC)
        last_activity_at: Last query timestamp
        expires_at: When session expires (last_activity + 30 min)
        message_history: Recent conversation turns (max 50)
        routing_history: List of routing_decision_ids in order
        user_preferences: Persistent preferences
        metadata: Additional context (location, role, etc.)
    """

    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(init=False)
    message_history: List[Dict] = field(default_factory=list)
    routing_history: List[str] = field(default_factory=list)
    user_preferences: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

    # Constants
    TTL_MINUTES: int = 30
    MAX_MESSAGES: int = 50
    MAX_ROUTING_HISTORY: int = 50

    def __post_init__(self):
        """Validate and initialize session context."""
        # Validate session_id is UUID format
        try:
            uuid.UUID(self.session_id)
        except ValueError:
            raise ValueError(f"Invalid session_id format: {self.session_id}. Must be valid UUID v4")

        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")

        # Calculate expiration time
        self.expires_at = self.last_activity_at + timedelta(minutes=self.TTL_MINUTES)

        # Trim message history if exceeds max
        if len(self.message_history) > self.MAX_MESSAGES:
            self.message_history = self.message_history[-self.MAX_MESSAGES:]

        # Trim routing history if exceeds max
        if len(self.routing_history) > self.MAX_ROUTING_HISTORY:
            self.routing_history = self.routing_history[-self.MAX_ROUTING_HISTORY:]

    def update_activity(self):
        """
        Update last activity timestamp and recalculate expiration.

        Call this whenever a new query is received to extend the session TTL.
        """
        self.last_activity_at = datetime.utcnow()
        self.expires_at = self.last_activity_at + timedelta(minutes=self.TTL_MINUTES)

    def add_message(self, role: str, content: str, category: Optional[str] = None, timestamp: Optional[datetime] = None):
        """
        Add a message to the conversation history.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            category: Optional category for routing context
            timestamp: Optional explicit timestamp (defaults to now)
        """
        if role not in ["user", "assistant"]:
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

        message = {
            "role": role,
            "content": content,
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        }

        if category:
            message["category"] = category

        self.message_history.append(message)

        # Trim if exceeds max
        if len(self.message_history) > self.MAX_MESSAGES:
            self.message_history = self.message_history[-self.MAX_MESSAGES:]

        # Update activity timestamp
        self.update_activity()

    def add_routing_decision(self, decision_id: str):
        """
        Add a routing decision ID to the history.

        Args:
            decision_id: UUID of the routing decision
        """
        self.routing_history.append(decision_id)

        # Trim if exceeds max
        if len(self.routing_history) > self.MAX_ROUTING_HISTORY:
            self.routing_history = self.routing_history[-self.MAX_ROUTING_HISTORY:]

    def get_recent_messages(self, count: int = 10) -> List[Dict]:
        """
        Get the most recent N messages.

        Args:
            count: Number of messages to return

        Returns:
            List of recent messages (most recent last)
        """
        return self.message_history[-count:]

    def get_context_for_agent(self) -> List[Dict]:
        """
        Get message history formatted for agent context.

        Returns:
            List of messages with role and content
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.message_history
        ]

    def is_expired(self) -> bool:
        """
        Check if session has expired.

        Returns:
            True if current time > expires_at
        """
        return datetime.utcnow() > self.expires_at

    def get_ttl_seconds(self) -> int:
        """
        Get remaining TTL in seconds.

        Returns:
            Seconds until expiration (0 if already expired)
        """
        if self.is_expired():
            return 0

        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))

    def set_preference(self, key: str, value):
        """
        Set a user preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self.user_preferences[key] = value

    def get_preference(self, key: str, default=None):
        """
        Get a user preference.

        Args:
            key: Preference key
            default: Default value if key not found

        Returns:
            Preference value or default
        """
        return self.user_preferences.get(key, default)

    def to_dict(self) -> Dict:
        """
        Convert session context to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "message_history": self.message_history,
            "routing_history": self.routing_history,
            "user_preferences": self.user_preferences,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SessionContext":
        """
        Create SessionContext from dictionary.

        Args:
            data: Dictionary with session data

        Returns:
            SessionContext instance
        """
        # Parse timestamps
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        last_activity_at = data.get("last_activity_at")
        if isinstance(last_activity_at, str):
            last_activity_at = datetime.fromisoformat(last_activity_at)

        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            created_at=created_at or datetime.utcnow(),
            last_activity_at=last_activity_at or datetime.utcnow(),
            message_history=data.get("message_history", []),
            routing_history=data.get("routing_history", []),
            user_preferences=data.get("user_preferences", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def create_new(cls, user_id: str, session_id: Optional[str] = None, metadata: Optional[Dict] = None) -> "SessionContext":
        """
        Create a new session context.

        Args:
            user_id: User ID
            session_id: Optional explicit session ID (generates new if not provided)
            metadata: Optional metadata

        Returns:
            New SessionContext instance
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        return cls(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {},
        )

    def __str__(self) -> str:
        """String representation of session context."""
        return (
            f"SessionContext(id={self.session_id[:8]}, user={self.user_id}, "
            f"messages={len(self.message_history)}, "
            f"ttl={self.get_ttl_seconds()}s)"
        )

    def __repr__(self) -> str:
        """Detailed representation of session context."""
        return (
            f"SessionContext(session_id={self.session_id}, user_id={self.user_id}, "
            f"created={self.created_at.isoformat()}, "
            f"expires={self.expires_at.isoformat()}, "
            f"messages={len(self.message_history)})"
        )
