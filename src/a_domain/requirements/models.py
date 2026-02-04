"""
Data models for requirements extraction.

Defines the core data structures used throughout the Requirements-to-Design
Pipeline for representing requirements, priority signals, and extracted metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class RequirementType(Enum):
    """Types of requirements that can be extracted."""

    PAIN_POINT = "pain_point"
    FEATURE_REQUEST = "feature_request"
    INTEGRATION = "integration"
    TECHNICAL_CONSTRAINT = "technical_constraint"
    BUSINESS_REQUIREMENT = "business_requirement"
    UI_COMPONENT = "ui_component"
    USER_FLOW = "user_flow"


class PrioritySignalType(Enum):
    """Types of priority signals."""

    TIMELINE = "timeline"  # "ASAP", "2 weeks", "Q1"
    EXECUTIVE = "executive"  # C-level mentioned
    BUSINESS_IMPACT = "business_impact"  # "revenue blocker", "deal breaker"
    URGENCY_WORD = "urgency_word"  # "critical", "must have"
    VOLUME = "volume"  # Mentioned multiple times


class Urgency(Enum):
    """Urgency levels for priority signals."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PrioritySignal:
    """A signal indicating requirement priority/urgency."""

    type: PrioritySignalType
    value: str
    urgency: Urgency
    confidence: float = 0.5  # 0.0-1.0


@dataclass
class Speaker:
    """Speaker information from Gong call."""

    name: str
    role: Optional[str] = None
    company: Optional[str] = None


@dataclass
class SourceMetadata:
    """Metadata about requirement source."""

    call_id: Optional[str] = None
    call_title: Optional[str] = None
    call_date: Optional[str] = None
    timestamp: Optional[str] = None
    duration: Optional[str] = None
    figma_file: Optional[str] = None
    figma_node_id: Optional[str] = None


@dataclass
class Context:
    """Contextual information surrounding requirement."""

    preceding: Optional[str] = None
    following: Optional[str] = None


@dataclass
class Requirement:
    """
    A single extracted requirement.

    This is the core data structure representing a requirement extracted
    from Gong transcripts, Figma designs, or manual input.
    """

    id: str
    source_type: str  # "gong_call", "figma", "manual"
    requirement_text: str
    requirement_type: RequirementType

    # Metadata
    source_metadata: SourceMetadata = field(default_factory=SourceMetadata)
    speaker: Optional[Speaker] = None
    categories: List[str] = field(default_factory=list)
    priority_signals: List[PrioritySignal] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    sentiment: str = "neutral"  # "positive", "negative", "neutral"
    context: Optional[Context] = None

    # Processing
    extracted_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5  # 0.0-1.0

    def to_dict(self) -> Dict:
        """Convert requirement to dictionary for serialization."""
        return {
            "id": self.id,
            "source_type": self.source_type,
            "requirement_text": self.requirement_text,
            "requirement_type": self.requirement_type.value,
            "source_metadata": {
                k: v for k, v in vars(self.source_metadata).items() if v is not None
            },
            "speaker": vars(self.speaker) if self.speaker else None,
            "categories": self.categories,
            "priority_signals": [
                {
                    "type": signal.type.value,
                    "value": signal.value,
                    "urgency": signal.urgency.value,
                    "confidence": signal.confidence,
                }
                for signal in self.priority_signals
            ],
            "entities": self.entities,
            "sentiment": self.sentiment,
            "context": vars(self.context) if self.context else None,
            "extracted_at": self.extracted_at.isoformat(),
            "confidence": self.confidence,
        }
