"""
NLP patterns for requirements extraction.

This module provides comprehensive pattern matching and NLP utilities
for identifying pain points, feature requests, and priority signals in
Gong call transcripts.
"""

import re
from typing import Dict, List, Optional, Tuple

from .models import Urgency


class NLPPatterns:
    """
    Collection of NLP patterns for requirement extraction.

    Provides pattern matching, entity extraction, and sentiment analysis
    capabilities for analyzing Gong transcripts.
    """

    # Pain point patterns (problems, frustrations, inefficiencies)
    PAIN_POINT_PATTERNS = [
        # Explicit problems
        (r"(?:we have a |there'?s a )?(problem|issue) with", 0.9),
        (r"(?:is |are )(?:very )?(?:broken|buggy|slow)", 0.8),
        (r"doesn'?t work", 0.9),
        (r"not working", 0.9),
        (r"keeps (?:failing|crashing|breaking)", 0.8),
        # Frustrations
        (r"(?:very |really )?frustrat(?:ed|ing)", 0.9),
        (r"(?:so |very )?annoying", 0.7),
        (r"waste(?:s|ing) (?:time|hours|days)", 0.8),
        (r"takes? (?:too long|forever|hours)", 0.8),
        # Inefficiencies
        (r"manual(?:ly)? process", 0.7),
        (r"time-consuming", 0.8),
        (r"(?:have to|need to) do (?:it |this )?manual(?:ly)?", 0.7),
        (r"(?:can'?t|cannot) automate", 0.8),
        # Business impact
        (r"losing (?:deals|customers|revenue)", 0.95),
        (r"(?:deal|revenue) (?:blocker|killer)", 0.95),
        (r"costing us (?:money|time|deals)", 0.9),
    ]

    # Feature request patterns
    FEATURE_REQUEST_PATTERNS = [
        (r"(?:we )?(?:would |'d )?(?:really )?(?:like|love|want|need) to", 0.8),
        (r"(?:can|could) you (?:add|build|create|implement)", 0.9),
        (r"wish (?:we could|there was)", 0.7),
        (r"would be (?:great|awesome|helpful) (?:if|to)", 0.7),
        (r"(?:we'?re|we are) looking for (?:a way to|the ability to)", 0.8),
        (r"(?:is there|will there be) a (?:feature|capability|option) to", 0.8),
        (r"(?:we need|we require) (?:the ability to|a way to)", 0.9),
    ]

    # Integration request patterns
    INTEGRATION_PATTERNS = [
        (r"integrate with (\w+)", 0.9),
        (r"connect to (\w+)", 0.8),
        (r"(?:sync|synchronize) with (\w+)", 0.9),
        (r"(?:import|export) (?:from|to) (\w+)", 0.8),
        (r"(?:api|webhook) for (\w+)", 0.9),
        (r"(?:two-way|bidirectional|bi-directional) sync", 0.85),
    ]

    # Timeline/urgency patterns
    TIMELINE_URGENCY_PATTERNS = [
        (r"(?:as soon as possible|asap)", Urgency.CRITICAL, 0.95),
        (r"(?:immediately|right away|right now)", Urgency.CRITICAL, 0.95),
        (r"(?:by|before|within) (\d+) (?:day|week)s?", Urgency.HIGH, 0.9),
        (r"(?:this|next) (?:week|month)", Urgency.HIGH, 0.85),
        (r"by (?:end of |the end of )?(?:this |next )?(?:week|month|quarter)", Urgency.HIGH, 0.85),
        (r"Q[1-4]", Urgency.MEDIUM, 0.7),
        (r"(?:in the )?(?:near |immediate )?future", Urgency.LOW, 0.5),
    ]

    # Business impact indicators
    BUSINESS_IMPACT_PATTERNS = [
        (r"(?:revenue|deal|sales?) (?:blocker|killer)", 0.95),
        (r"losing (?:deals|customers|sales|revenue)", 0.95),
        (r"costing us \$?(\d+(?:,\d{3})*(?:\.\d{2})?)", 0.9),
        (r"(?:critical|essential|vital) (?:for|to) (?:our )?(?:business|success)", 0.85),
        (r"(?:make or break|deal breaker)", 0.95),
        (r"competitive (?:advantage|disadvantage)", 0.8),
    ]

    # Executive role patterns (for priority boosting)
    EXECUTIVE_ROLE_PATTERNS = [
        r"\bC[A-Z]{2}\b",  # CEO, CTO, CFO, etc.
        r"\b(?:Chief|VP|Vice President)\b",
        r"\b(?:President|Director)\b",
        r"\b(?:Head of|SVP)\b",
    ]

    # System/product name patterns
    SYSTEM_NAME_PATTERNS = [
        r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b",  # CamelCase (e.g., Salesforce)
        r"\b([A-Z]{2,})\b",  # Acronyms (e.g., CRM, API)
        r"\b([\w-]+\.(?:com|io|net))\b",  # URLs
    ]

    @classmethod
    def detect_pain_points(cls, text: str) -> List[Tuple[str, float]]:
        """
        Detect pain point mentions in text.

        Args:
            text: Text to analyze

        Returns:
            List of (matched_pattern, confidence) tuples
        """
        matches = []
        text_lower = text.lower()

        for pattern, confidence in cls.PAIN_POINT_PATTERNS:
            if re.search(pattern, text_lower):
                matches.append((pattern, confidence))

        return matches

    @classmethod
    def detect_feature_requests(cls, text: str) -> List[Tuple[str, float]]:
        """
        Detect feature request mentions in text.

        Args:
            text: Text to analyze

        Returns:
            List of (matched_pattern, confidence) tuples
        """
        matches = []
        text_lower = text.lower()

        for pattern, confidence in cls.FEATURE_REQUEST_PATTERNS:
            if re.search(pattern, text_lower):
                matches.append((pattern, confidence))

        return matches

    @classmethod
    def detect_integration_requests(cls, text: str) -> List[Tuple[str, str, float]]:
        """
        Detect integration request mentions in text.

        Args:
            text: Text to analyze

        Returns:
            List of (pattern, system_name, confidence) tuples
        """
        matches = []

        for pattern, confidence in cls.INTEGRATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                system = match.group(1) if match.groups() else "unknown"
                matches.append((pattern, system, confidence))

        return matches

    @classmethod
    def detect_timeline_urgency(cls, text: str) -> List[Tuple[str, Urgency, float]]:
        """
        Detect timeline/urgency mentions in text.

        Args:
            text: Text to analyze

        Returns:
            List of (matched_text, urgency_level, confidence) tuples
        """
        matches = []
        text_lower = text.lower()

        for pattern, urgency, confidence in cls.TIMELINE_URGENCY_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                matches.append((match.group(0), urgency, confidence))

        return matches

    @classmethod
    def detect_business_impact(cls, text: str) -> List[Tuple[str, float]]:
        """
        Detect business impact mentions in text.

        Args:
            text: Text to analyze

        Returns:
            List of (matched_pattern, confidence) tuples
        """
        matches = []
        text_lower = text.lower()

        for pattern, confidence in cls.BUSINESS_IMPACT_PATTERNS:
            if re.search(pattern, text_lower):
                matches.append((pattern, confidence))

        return matches

    @classmethod
    def extract_systems(cls, text: str) -> List[str]:
        """
        Extract system/product names from text.

        Args:
            text: Text to analyze

        Returns:
            List of system names
        """
        systems = []

        for pattern in cls.SYSTEM_NAME_PATTERNS:
            matches = re.findall(pattern, text)
            systems.extend(matches)

        # Deduplicate and filter
        return list(set(systems))

    @classmethod
    def is_executive_role(cls, role: str) -> bool:
        """
        Check if role is executive-level.

        Args:
            role: Role title

        Returns:
            True if executive role detected
        """
        if not role:
            return False

        for pattern in cls.EXECUTIVE_ROLE_PATTERNS:
            if re.search(pattern, role, re.IGNORECASE):
                return True

        return False

    @classmethod
    def calculate_requirement_confidence(
        cls,
        text: str,
        speaker_role: Optional[str] = None,
    ) -> float:
        """
        Calculate overall confidence score for a requirement.

        Args:
            text: Requirement text
            speaker_role: Speaker's role (optional)

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence

        # Boost for clear pain point
        pain_points = cls.detect_pain_points(text)
        if pain_points:
            avg_pain_confidence = sum(c for _, c in pain_points) / len(pain_points)
            confidence += avg_pain_confidence * 0.2

        # Boost for feature request
        feature_requests = cls.detect_feature_requests(text)
        if feature_requests:
            avg_feature_confidence = sum(c for _, c in feature_requests) / len(
                feature_requests
            )
            confidence += avg_feature_confidence * 0.15

        # Boost for business impact
        business_impacts = cls.detect_business_impact(text)
        if business_impacts:
            avg_impact_confidence = sum(c for _, c in business_impacts) / len(
                business_impacts
            )
            confidence += avg_impact_confidence * 0.2

        # Boost for executive speaker
        if speaker_role and cls.is_executive_role(speaker_role):
            confidence += 0.15

        return min(1.0, confidence)
