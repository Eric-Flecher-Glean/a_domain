"""
RequirementExtractorAgent - Extracts requirements from Gong transcripts.

This agent analyzes Gong sales call transcripts using NLP techniques to identify
customer pain points, feature requests, and business requirements.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .models import (
    Context,
    PrioritySignal,
    PrioritySignalType,
    Requirement,
    RequirementType,
    Speaker,
    SourceMetadata,
    Urgency,
)


class RequirementExtractorAgent:
    """
    Agent that extracts structured requirements from Gong call transcripts.

    The agent performs NLP-based analysis to:
    - Identify pain points and feature requests
    - Detect priority signals (urgency, timeline, executive involvement)
    - Extract entities (systems, timelines, people)
    - Classify requirement types
    - Score sentiment and confidence
    """

    # Pattern matchers for NLP
    URGENCY_PATTERNS = {
        "critical": (Urgency.CRITICAL, 0.9),
        "asap": (Urgency.CRITICAL, 0.9),
        "immediately": (Urgency.CRITICAL, 0.9),
        "urgent": (Urgency.HIGH, 0.8),
        "must have": (Urgency.HIGH, 0.8),
        "need": (Urgency.MEDIUM, 0.6),
        "would like": (Urgency.LOW, 0.5),
    }

    TIMELINE_PATTERNS = [
        (r"(\d+)\s*(week|day|month)s?", Urgency.HIGH),
        (r"Q[1-4]", Urgency.MEDIUM),
        (r"this (week|month|quarter)", Urgency.HIGH),
        (r"next (week|month|quarter)", Urgency.MEDIUM),
        (r"by (Monday|Tuesday|Wednesday|Thursday|Friday)", Urgency.CRITICAL),
    ]

    EXECUTIVE_ROLES = {"ceo", "cto", "cfo", "coo", "vp", "president", "director"}

    INTEGRATION_KEYWORDS = {
        "integrate",
        "integration",
        "connect",
        "sync",
        "api",
        "webhook",
        "import",
        "export",
    }

    PAIN_POINT_INDICATORS = {
        "problem",
        "issue",
        "frustrat",
        "difficult",
        "slow",
        "manual",
        "time-consuming",
        "broken",
        "doesn't work",
    }

    FEATURE_REQUEST_INDICATORS = {
        "want",
        "need",
        "would like",
        "wish",
        "could you",
        "can you",
        "add",
        "create",
        "build",
    }

    def __init__(self):
        """Initialize the RequirementExtractorAgent."""
        self.requirement_counter = 0

    def extract_from_transcript(
        self,
        transcript: str,
        call_metadata: Optional[Dict] = None,
    ) -> List[Requirement]:
        """
        Extract requirements from a Gong call transcript.

        Args:
            transcript: Raw transcript text (with speaker labels)
            call_metadata: Optional metadata (call_id, title, date, etc.)

        Returns:
            List of extracted Requirements
        """
        requirements = []

        # Parse transcript into speaker segments
        segments = self._parse_transcript(transcript)

        # Analyze each segment
        for segment in segments:
            # Check if segment contains a requirement
            if self._is_requirement_segment(segment):
                req = self._extract_requirement_from_segment(segment, call_metadata)
                if req:
                    requirements.append(req)

        return requirements

    def _parse_transcript(self, transcript: str) -> List[Dict]:
        """
        Parse transcript into speaker segments.

        Expects format:
        [00:15:42] John Smith (CTO, Acme Corp): We need to integrate with Salesforce

        Returns:
            List of dicts with {speaker, role, company, timestamp, text}
        """
        segments = []
        pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s+([^(]+?)(?:\(([^)]+)\))?:\s*(.+)"

        for line in transcript.split("\n"):
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line)
            if match:
                timestamp, speaker_name, role_company, text = match.groups()
                speaker_name = speaker_name.strip()

                # Parse role and company from parentheses
                role = None
                company = None
                if role_company:
                    parts = [p.strip() for p in role_company.split(",")]
                    role = parts[0] if len(parts) > 0 else None
                    company = parts[1] if len(parts) > 1 else None

                segments.append(
                    {
                        "timestamp": timestamp,
                        "speaker": speaker_name,
                        "role": role,
                        "company": company,
                        "text": text.strip(),
                    }
                )

        return segments

    def _is_requirement_segment(self, segment: Dict) -> bool:
        """Check if segment contains a requirement."""
        text = segment["text"].lower()

        # Check for pain point indicators
        if any(indicator in text for indicator in self.PAIN_POINT_INDICATORS):
            return True

        # Check for feature request indicators
        if any(indicator in text for indicator in self.FEATURE_REQUEST_INDICATORS):
            return True

        # Check for integration keywords
        if any(keyword in text for keyword in self.INTEGRATION_KEYWORDS):
            return True

        # Check for business impact mentions
        if any(
            keyword in text
            for keyword in ["revenue", "deal", "customer", "sales", "contract"]
        ):
            return True

        return False

    def _extract_requirement_from_segment(
        self, segment: Dict, call_metadata: Optional[Dict]
    ) -> Optional[Requirement]:
        """Extract a Requirement from a segment."""
        self.requirement_counter += 1
        req_id = f"REQ-{self.requirement_counter:03d}"

        text = segment["text"]
        text_lower = text.lower()

        # Classify requirement type
        req_type = self._classify_requirement_type(text_lower)

        # Extract priority signals
        priority_signals = self._extract_priority_signals(text_lower, segment)

        # Extract entities
        entities = self._extract_entities(text)

        # Detect sentiment
        sentiment = self._detect_sentiment(text_lower)

        # Build source metadata
        source_metadata = SourceMetadata(
            call_id=call_metadata.get("call_id") if call_metadata else None,
            call_title=call_metadata.get("call_title") if call_metadata else None,
            call_date=call_metadata.get("call_date") if call_metadata else None,
            timestamp=segment.get("timestamp"),
        )

        # Build speaker info
        speaker = Speaker(
            name=segment["speaker"],
            role=segment.get("role"),
            company=segment.get("company"),
        )

        # Calculate confidence
        confidence = self._calculate_confidence(req_type, priority_signals, segment)

        # Build categories
        categories = self._build_categories(text_lower, req_type, entities)

        return Requirement(
            id=req_id,
            source_type="gong_call",
            requirement_text=text,
            requirement_type=req_type,
            source_metadata=source_metadata,
            speaker=speaker,
            categories=categories,
            priority_signals=priority_signals,
            entities=entities,
            sentiment=sentiment,
            confidence=confidence,
        )

    def _classify_requirement_type(self, text: str) -> RequirementType:
        """Classify the type of requirement."""
        # Integration keywords
        if any(keyword in text for keyword in self.INTEGRATION_KEYWORDS):
            return RequirementType.INTEGRATION

        # Pain point indicators
        if any(indicator in text for indicator in self.PAIN_POINT_INDICATORS):
            return RequirementType.PAIN_POINT

        # Feature request indicators
        if any(indicator in text for indicator in self.FEATURE_REQUEST_INDICATORS):
            return RequirementType.FEATURE_REQUEST

        # Technical constraint keywords
        if any(
            keyword in text
            for keyword in ["performance", "security", "compliance", "scale"]
        ):
            return RequirementType.TECHNICAL_CONSTRAINT

        # Business requirement keywords
        if any(keyword in text for keyword in ["revenue", "cost", "roi", "efficiency"]):
            return RequirementType.BUSINESS_REQUIREMENT

        # Default
        return RequirementType.FEATURE_REQUEST

    def _extract_priority_signals(
        self, text: str, segment: Dict
    ) -> List[PrioritySignal]:
        """Extract priority signals from text and metadata."""
        signals = []

        # Check urgency words
        for word, (urgency, confidence) in self.URGENCY_PATTERNS.items():
            if word in text:
                signals.append(
                    PrioritySignal(
                        type=PrioritySignalType.URGENCY_WORD,
                        value=word,
                        urgency=urgency,
                        confidence=confidence,
                    )
                )

        # Check timeline patterns
        for pattern, urgency in self.TIMELINE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                signals.append(
                    PrioritySignal(
                        type=PrioritySignalType.TIMELINE,
                        value=match.group(0),
                        urgency=urgency,
                        confidence=0.8,
                    )
                )

        # Check executive involvement
        role = segment.get("role", "").lower()
        if any(exec_role in role for exec_role in self.EXECUTIVE_ROLES):
            signals.append(
                PrioritySignal(
                    type=PrioritySignalType.EXECUTIVE,
                    value=f"{role} request",
                    urgency=Urgency.HIGH,
                    confidence=0.9,
                )
            )

        # Check business impact
        if any(
            keyword in text
            for keyword in ["revenue blocker", "deal breaker", "losing deals"]
        ):
            signals.append(
                PrioritySignal(
                    type=PrioritySignalType.BUSINESS_IMPACT,
                    value="business impact mentioned",
                    urgency=Urgency.CRITICAL,
                    confidence=0.9,
                )
            )

        return signals

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities (systems, timelines, etc.)."""
        entities = {}

        # Extract system mentions (capitalized words that look like product names)
        systems = re.findall(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b", text)
        if systems:
            entities["systems"] = list(set(systems))

        # Extract timeline mentions
        timeline_matches = re.findall(
            r"(\d+\s*(?:week|day|month|year)s?|Q[1-4]|this|next)\s+(?:week|month|quarter|year)",
            text,
            re.IGNORECASE,
        )
        if timeline_matches:
            entities["timeline"] = timeline_matches

        return entities

    def _detect_sentiment(self, text: str) -> str:
        """Detect sentiment of requirement (positive/negative/neutral)."""
        negative_words = {
            "problem",
            "issue",
            "frustrat",
            "broken",
            "slow",
            "difficult",
            "bad",
            "losing",
        }
        positive_words = {"great", "love", "excited", "perfect", "excellent", "happy"}

        negative_count = sum(1 for word in negative_words if word in text)
        positive_count = sum(1 for word in positive_words if word in text)

        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"

    def _calculate_confidence(
        self, req_type: RequirementType, priority_signals: List[PrioritySignal], segment: Dict
    ) -> float:
        """Calculate confidence score for requirement extraction."""
        confidence = 0.5  # Base confidence

        # Boost for clear requirement type
        if req_type in {
            RequirementType.INTEGRATION,
            RequirementType.FEATURE_REQUEST,
        }:
            confidence += 0.2

        # Boost for priority signals
        if priority_signals:
            confidence += min(0.2, len(priority_signals) * 0.05)

        # Boost for executive speaker
        role = segment.get("role", "").lower()
        if any(exec_role in role for exec_role in self.EXECUTIVE_ROLES):
            confidence += 0.1

        return min(1.0, confidence)

    def _build_categories(
        self, text: str, req_type: RequirementType, entities: Dict
    ) -> List[str]:
        """Build category tags for requirement."""
        categories = [req_type.value]

        # Add integration category if applicable
        if any(keyword in text for keyword in self.INTEGRATION_KEYWORDS):
            categories.append("integration")

        # Add system categories
        if "systems" in entities:
            for system in entities["systems"]:
                categories.append(system.lower())

        # Add timeline category
        if "timeline" in entities:
            categories.append("timeline_constraint")

        return list(set(categories))
