"""
RoutingDecision Model - Classification result with category, confidence, and metadata.

Represents the output of query classification and routing logic.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from .category import Category


@dataclass
class RoutingDecision:
    """
    Classification result containing assigned category, confidence, and routing metadata.

    Attributes:
        id: Unique identifier (UUID)
        query_id: Query this decision is for
        primary_category: Highest-confidence category
        primary_confidence: Confidence score for primary (0.0-1.0)
        secondary_category: Second-highest category (for multi-intent)
        secondary_confidence: Confidence score for secondary (0.0-1.0)
        reasoning: Why this category was chosen (for debugging)
        classification_latency_ms: Time taken to classify (milliseconds)
        fallback_triggered: Whether confidence < 0.7 triggered clarification
        user_override: Whether user explicitly requested category
        suggested_table: Suggested database table for INFORMATION_RETRIEVAL queries
        timestamp: When decision was made (UTC)
    """

    query_id: str
    primary_category: Category
    primary_confidence: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    secondary_category: Optional[Category] = None
    secondary_confidence: Optional[float] = None
    reasoning: Optional[str] = None
    classification_latency_ms: int = 0
    fallback_triggered: bool = False
    user_override: bool = False
    suggested_table: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate routing decision after initialization."""
        # Validate confidence scores
        if not 0.0 <= self.primary_confidence <= 1.0:
            raise ValueError(
                f"Primary confidence must be between 0.0 and 1.0, got: {self.primary_confidence}"
            )

        if self.secondary_confidence is not None:
            if not 0.0 <= self.secondary_confidence <= 1.0:
                raise ValueError(
                    f"Secondary confidence must be between 0.0 and 1.0, got: {self.secondary_confidence}"
                )

            # Secondary must be less than primary
            if self.secondary_confidence >= self.primary_confidence:
                raise ValueError(
                    f"Secondary confidence ({self.secondary_confidence}) must be less than "
                    f"primary confidence ({self.primary_confidence})"
                )

            # If secondary confidence is set, secondary category must be set
            if self.secondary_category is None:
                raise ValueError(
                    "Secondary category must be set when secondary confidence is provided"
                )

        # Validate fallback trigger logic
        # Note: Threshold varies by classifier (0.55 for Groq, 0.7 for semantic)
        # So we don't enforce strict validation here - just log a warning
        if self.fallback_triggered and self.primary_confidence >= 0.9:
            # Only warn if confidence is very high (>= 90%) but fallback triggered
            import sys
            print(f"[WARNING RoutingDecision] Fallback triggered with high confidence: {self.primary_confidence}", file=sys.stderr)

        # Validate reasoning length
        if self.reasoning and len(self.reasoning) > 500:
            self.reasoning = self.reasoning[:497] + "..."

    def to_dict(self) -> Dict:
        """
        Convert routing decision to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "query_id": self.query_id,
            "primary_category": self.primary_category.value,
            "primary_confidence": float(self.primary_confidence),
            "secondary_category": self.secondary_category.value if self.secondary_category else None,
            "secondary_confidence": float(self.secondary_confidence) if self.secondary_confidence else None,
            "reasoning": self.reasoning,
            "classification_latency_ms": self.classification_latency_ms,
            "fallback_triggered": self.fallback_triggered,
            "user_override": self.user_override,
            "suggested_table": self.suggested_table,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RoutingDecision":
        """
        Create RoutingDecision from dictionary.

        Args:
            data: Dictionary with routing decision data

        Returns:
            RoutingDecision instance
        """
        # Parse timestamp
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        # Parse categories
        primary_category = Category.from_string(data["primary_category"])
        secondary_category = None
        if data.get("secondary_category"):
            secondary_category = Category.from_string(data["secondary_category"])

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            query_id=data["query_id"],
            primary_category=primary_category,
            primary_confidence=float(data["primary_confidence"]),
            secondary_category=secondary_category,
            secondary_confidence=float(data["secondary_confidence"]) if data.get("secondary_confidence") else None,
            reasoning=data.get("reasoning"),
            classification_latency_ms=data.get("classification_latency_ms", 0),
            fallback_triggered=data.get("fallback_triggered", False),
            user_override=data.get("user_override", False),
            suggested_table=data.get("suggested_table"),
            timestamp=timestamp or datetime.utcnow(),
        )

    def is_multi_intent(self) -> bool:
        """
        Check if this is a multi-intent query.

        Returns:
            True if secondary category exists, False otherwise
        """
        return self.secondary_category is not None

    def get_multi_intent_notice(self) -> Optional[str]:
        """
        Get user notification for multi-intent queries.

        Returns:
            Notification message or None if single-intent
        """
        if not self.is_multi_intent():
            return None

        secondary_name = Category.get_description(self.secondary_category)
        return (
            f"This also relates to {secondary_name}. "
            f"Would you like me to route there instead?"
        )

    def get_confidence_percentage(self, secondary: bool = False) -> str:
        """
        Get confidence as formatted percentage.

        Args:
            secondary: If True, return secondary confidence

        Returns:
            Formatted percentage string (e.g., "92.5%")
        """
        confidence = self.secondary_confidence if secondary else self.primary_confidence
        if confidence is None:
            return "N/A"
        return f"{confidence * 100:.1f}%"

    def __str__(self) -> str:
        """String representation of routing decision."""
        return (
            f"RoutingDecision(category={self.primary_category.value}, "
            f"confidence={self.get_confidence_percentage()})"
        )

    def __repr__(self) -> str:
        """Detailed representation of routing decision."""
        return (
            f"RoutingDecision(id={self.id}, query_id={self.query_id}, "
            f"primary={self.primary_category.value}, "
            f"confidence={self.primary_confidence:.4f}, "
            f"fallback={self.fallback_triggered})"
        )
