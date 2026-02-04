#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pytest>=7.0",
#   "pyyaml>=6.0",
# ]
# ///
"""
Integration tests for Gong Transcript Extractor.

Tests the RequirementExtractorAgent with realistic Gong call transcripts.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from a_domain.requirements.extractor import RequirementExtractorAgent
from a_domain.requirements.gong_connector import GongConnector
from a_domain.requirements.models import RequirementType, Urgency


def test_extract_requirements():
    """
    Test AC1: Extracts requirements from Gong transcripts.

    This test verifies that the RequirementExtractorAgent can:
    1. Parse Gong transcript format
    2. Identify requirement segments
    3. Extract structured requirements
    4. Classify requirement types
    5. Detect priority signals
    """
    # Arrange
    agent = RequirementExtractorAgent()
    transcript = """[00:15:42] John Smith (CTO, Acme Corp): We need to integrate with Salesforce within 2 weeks
[00:16:05] Sales Rep (AE, Our Company): I understand the urgency. Can you tell me more about your current process?
[00:16:20] John Smith (CTO, Acme Corp): We're currently using a manual process and our sales team is losing deals because of delays
[00:16:45] Sales Rep (AE, Our Company): That sounds frustrating. What specific data do you need to sync?
[00:17:10] John Smith (CTO, Acme Corp): We need bi-directional sync of customer records, opportunities, and activity data
[00:17:35] Jane Doe (VP Product, Acme Corp): This is critical for us. We're evaluating three vendors and integration speed is our top criterion"""

    call_metadata = {
        "call_id": "test_abc123",
        "call_title": "Acme Corp - Technical Discovery",
        "call_date": "2026-02-03",
    }

    # Act
    requirements = agent.extract_from_transcript(transcript, call_metadata)

    # Assert
    assert len(requirements) > 0, "Should extract at least one requirement"

    # Check first requirement (integration request)
    req1 = requirements[0]
    assert req1.requirement_text == "We need to integrate with Salesforce within 2 weeks"
    assert req1.requirement_type == RequirementType.INTEGRATION
    assert req1.source_type == "gong_call"
    assert req1.source_metadata.call_id == "test_abc123"
    assert req1.source_metadata.timestamp == "00:15:42"

    # Check speaker info
    assert req1.speaker.name == "John Smith"
    assert req1.speaker.role == "CTO"
    assert req1.speaker.company == "Acme Corp"

    # Check priority signals
    assert len(req1.priority_signals) >= 2, "Should detect timeline and executive signals"

    # Check for timeline signal
    timeline_signals = [
        s for s in req1.priority_signals if s.type.value == "timeline"
    ]
    assert len(timeline_signals) > 0, "Should detect timeline signal"
    assert timeline_signals[0].urgency == Urgency.HIGH

    # Check for executive signal
    exec_signals = [
        s for s in req1.priority_signals if s.type.value == "executive"
    ]
    assert len(exec_signals) > 0, "Should detect executive speaker"

    # Check categories
    assert "integration" in req1.categories
    assert "Salesforce" in req1.categories or "salesforce" in req1.categories

    # Check entities
    assert "systems" in req1.entities
    assert "Salesforce" in req1.entities["systems"]

    # Check second requirement (pain point)
    req2 = next(
        (
            r
            for r in requirements
            if "manual process" in r.requirement_text or "losing deals" in r.requirement_text
        ),
        None,
    )
    assert req2 is not None, "Should extract pain point requirement"
    assert req2.requirement_type == RequirementType.PAIN_POINT
    assert req2.sentiment == "negative"

    # Check third requirement (critical business impact)
    req3 = next((r for r in requirements if "critical" in r.requirement_text), None)
    assert req3 is not None, "Should extract critical requirement"

    critical_signals = [
        s
        for s in req3.priority_signals
        if s.urgency in {Urgency.CRITICAL, Urgency.HIGH}
    ]
    assert len(critical_signals) > 0, "Should detect high urgency for critical requirement"

    print("✅ test_extract_requirements PASSED")
    print(f"   Extracted {len(requirements)} requirements")
    print(f"   Types: {set(r.requirement_type.value for r in requirements)}")
    print(f"   Speakers: {set(r.speaker.name for r in requirements if r.speaker)}")


def test_gong_connector_integration():
    """
    Test AC3: Integrates with Glean Gong connector.

    This test verifies that the GongConnector can fetch calls
    and the extractor can process them.
    """
    # Arrange
    connector = GongConnector()
    agent = RequirementExtractorAgent()

    # Act
    calls = connector.fetch_recent_calls(days=7)

    assert len(calls) > 0, "Connector should return calls"

    # Process first call
    call = calls[0]
    transcript = call.get("transcript", "")
    call_metadata = {
        "call_id": call["call_id"],
        "call_title": call["call_title"],
        "call_date": call["call_date"],
    }

    requirements = agent.extract_from_transcript(transcript, call_metadata)

    # Assert
    assert len(requirements) > 0, "Should extract requirements from connector output"
    assert requirements[0].source_type == "gong_call"
    assert requirements[0].source_metadata.call_id == call["call_id"]

    print("✅ test_gong_connector_integration PASSED")
    print(f"   Processed {len(calls)} calls")
    print(f"   Extracted {len(requirements)} requirements")


def test_nlp_pain_point_identification():
    """
    Test AC2: Identifies customer pain points and feature requests.

    This test verifies sophisticated NLP capabilities for detecting:
    - Pain points (problems, frustrations, inefficiencies)
    - Feature requests (wants, needs, desires)
    - Priority signals (urgency, business impact)
    """
    # Arrange
    agent = RequirementExtractorAgent()

    # Test various pain point patterns
    pain_point_transcript = """[00:10:00] Customer (CEO, BigCorp): This manual process is really frustrating our team
[00:10:30] Customer (CEO, BigCorp): We're wasting 10 hours per week on data entry
[00:11:00] Customer (CEO, BigCorp): The system is very slow and keeps crashing
[00:11:30] Customer (CEO, BigCorp): This is costing us deals - it's a revenue blocker"""

    # Act
    requirements = agent.extract_from_transcript(pain_point_transcript)

    # Assert
    pain_points = [r for r in requirements if r.requirement_type == RequirementType.PAIN_POINT]
    assert len(pain_points) >= 2, "Should identify multiple pain points"

    # Check for negative sentiment
    negative_reqs = [r for r in requirements if r.sentiment == "negative"]
    assert len(negative_reqs) > 0, "Should detect negative sentiment"

    # Check for business impact detection
    business_impact_reqs = [
        r for r in requirements
        if any(s.type.value == "business_impact" for s in r.priority_signals)
    ]
    assert len(business_impact_reqs) > 0, "Should detect business impact signals"

    print("✅ test_nlp_pain_point_identification PASSED")
    print(f"   Identified {len(pain_points)} pain points")
    print(f"   Detected {len(negative_reqs)} negative sentiments")
    print(f"   Found {len(business_impact_reqs)} business impact signals")


if __name__ == "__main__":
    print("🧪 Running Gong Extractor Integration Tests\n")

    try:
        test_extract_requirements()
        print()
        test_gong_connector_integration()
        print()
        test_nlp_pain_point_identification()
        print()
        print("✅ All tests PASSED")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
