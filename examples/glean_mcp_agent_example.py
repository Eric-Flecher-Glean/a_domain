#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Example: Glean MCP Agent - Customer Pain Point Extractor

Demonstrates the Glean MCP Agent implementation pattern:
1. Invoke existing Glean agent via mcp__glean__chat tool
2. Pass context parameters to narrow scope
3. Parse structured results
4. Integrate into requirements backlog

Pattern: Glean MCP Agent
Reference: ADR-006 (docs/architecture/ddd-specification.md)
Story: P1-EXAMPLE-001
"""

import json
from typing import Dict, List, Any


def extract_pain_points_via_glean(
    industry: str,
    timeframe: str,
    customer_segment: str = "enterprise"
) -> Dict[str, Any]:
    """
    Extract customer pain points using Glean's "Extract Common Pain Points" agent.

    This demonstrates how to:
    - Construct message for Glean agent
    - Pass context parameters to narrow scope
    - Handle response structure

    The Glean agent integrates data from multiple sources:
    - Gong (call transcripts)
    - HubSpot (customer records)
    - Teams (chat logs)
    - Salesforce (opportunities)
    - Zoom (meeting transcripts)

    Args:
        industry: Industry vertical (e.g., "healthcare", "finance", "retail")
        timeframe: Time period (e.g., "Q1 2026", "last 30 days")
        customer_segment: Customer segment (e.g., "enterprise", "smb")

    Returns:
        Dictionary containing:
        - pain_points: List of extracted pain points with metadata
        - summary: High-level summary
        - recommendations: Actionable next steps
    """

    # Step 1: Construct message
    # The message should be clear and specific about what you want
    message = f"Extract customer pain points from sales calls in {timeframe}"

    # Step 2: Add context to narrow scope
    # Context is passed as a list of strings in "key: value" format
    context = [
        f"industry: {industry}",
        f"timeframe: {timeframe}",
        f"customer_segment: {customer_segment}",
        "focus: technical challenges and integration issues",
        "include_frequency_analysis: true",
        "include_impact_assessment: true"
    ]

    print(f"🔍 Invoking Glean MCP Agent: 'Extract Common Pain Points'")
    print(f"   Message: {message}")
    print(f"   Context Parameters:")
    for ctx in context:
        print(f"     • {ctx}")
    print()

    # Step 3: Invoke Glean agent via MCP
    # In real implementation with Glean MCP configured:
    #
    # from mcp.tools import mcp__glean__chat
    # response = mcp__glean__chat(
    #     message=message,
    #     context=context
    # )

    # For this demo, we simulate the response
    # Real Glean agent would return similar structured data
    response = {
        "agent_name": "Extract Common Pain Points",
        "agent_version": "2.1.0",
        "data_sources_used": ["Gong", "HubSpot", "Teams", "Salesforce", "Zoom"],
        "analysis_date": "2026-02-03",
        "pain_points": [
            {
                "id": "PP-001",
                "description": "Manual data entry taking 10+ hours/week per user",
                "frequency": "high",
                "frequency_score": 0.85,
                "impact": "productivity",
                "impact_score": 0.90,
                "sentiment": "frustrated",
                "source": "Gong call #12345",
                "source_url": "https://glean.com/gong/calls/12345",
                "customer": "Memorial Hospital",
                "customer_segment": "enterprise",
                "mentioned_by": ["CTO", "Operations Manager", "Lead Nurse"],
                "first_mentioned": "2026-01-15",
                "last_mentioned": "2026-01-28",
                "mention_count": 8
            },
            {
                "id": "PP-002",
                "description": "Integration with legacy EMR systems causing data sync delays",
                "frequency": "medium",
                "frequency_score": 0.65,
                "impact": "technical debt",
                "impact_score": 0.75,
                "sentiment": "concerned",
                "source": "HubSpot ticket #67890",
                "source_url": "https://glean.com/hubspot/tickets/67890",
                "customer": "Regional Health Network",
                "customer_segment": "enterprise",
                "mentioned_by": ["IT Director", "VP Engineering"],
                "first_mentioned": "2026-01-20",
                "last_mentioned": "2026-01-30",
                "mention_count": 5
            },
            {
                "id": "PP-003",
                "description": "Real-time sync delays (5-10 min) causing data inconsistency",
                "frequency": "high",
                "frequency_score": 0.80,
                "impact": "data quality",
                "impact_score": 0.85,
                "sentiment": "critical",
                "source": "Teams chat with CTO",
                "source_url": "https://glean.com/teams/chats/abc123",
                "customer": "City General Hospital",
                "customer_segment": "enterprise",
                "mentioned_by": ["CTO", "Data Architect"],
                "first_mentioned": "2026-01-22",
                "last_mentioned": "2026-02-01",
                "mention_count": 6
            },
            {
                "id": "PP-004",
                "description": "Mobile app crashes when offline, losing entered data",
                "frequency": "medium",
                "frequency_score": 0.60,
                "impact": "user experience",
                "impact_score": 0.70,
                "sentiment": "annoyed",
                "source": "Salesforce opportunity notes",
                "source_url": "https://glean.com/salesforce/opportunities/xyz789",
                "customer": "Community Clinic Group",
                "customer_segment": "smb",
                "mentioned_by": ["Practice Manager", "Head Physician"],
                "first_mentioned": "2026-01-18",
                "last_mentioned": "2026-01-25",
                "mention_count": 4
            },
            {
                "id": "PP-005",
                "description": "Lack of HIPAA-compliant audit logging for compliance",
                "frequency": "low",
                "frequency_score": 0.30,
                "impact": "compliance risk",
                "impact_score": 0.95,
                "sentiment": "concerned",
                "source": "Zoom meeting transcript",
                "source_url": "https://glean.com/zoom/meetings/def456",
                "customer": "State Medical Board",
                "customer_segment": "enterprise",
                "mentioned_by": ["Compliance Officer", "Legal Counsel"],
                "first_mentioned": "2026-01-29",
                "last_mentioned": "2026-01-29",
                "mention_count": 2
            },
            {
                "id": "PP-006",
                "description": "No bulk import capability for migrating historical records",
                "frequency": "medium",
                "frequency_score": 0.55,
                "impact": "migration blocker",
                "impact_score": 0.80,
                "sentiment": "frustrated",
                "source": "Gong call #23456",
                "source_url": "https://glean.com/gong/calls/23456",
                "customer": "University Hospital System",
                "customer_segment": "enterprise",
                "mentioned_by": ["CIO", "Database Administrator"],
                "first_mentioned": "2026-01-12",
                "last_mentioned": "2026-01-27",
                "mention_count": 7
            }
        ],
        "summary": {
            "total_pain_points": 6,
            "total_mentions": 32,
            "unique_customers": 6,
            "unique_sources": 5,
            "average_frequency_score": 0.63,
            "average_impact_score": 0.83,
            "sentiment_breakdown": {
                "critical": 1,
                "frustrated": 2,
                "concerned": 2,
                "annoyed": 1
            }
        },
        "recommendations": [
            {
                "priority": "P0",
                "action": "Prioritize automation for data entry (PP-001)",
                "rationale": "Highest combined frequency and impact score (0.85 × 0.90 = 0.765)",
                "estimated_effort": "8 weeks",
                "expected_impact": "Save 10+ hours/week per user (40+ hours/week org-wide)"
            },
            {
                "priority": "P0",
                "action": "Implement real-time sync monitoring and alerting (PP-003)",
                "rationale": "Critical sentiment, high impact on data quality",
                "estimated_effort": "4 weeks",
                "expected_impact": "Prevent data inconsistency issues"
            },
            {
                "priority": "P1",
                "action": "Add HIPAA-compliant audit logging (PP-005)",
                "rationale": "Low frequency but very high impact (compliance risk)",
                "estimated_effort": "6 weeks",
                "expected_impact": "Unblock State Medical Board deal"
            },
            {
                "priority": "P1",
                "action": "Investigate EMR integration solutions (PP-002)",
                "rationale": "Technical debt accumulating, affects multiple customers",
                "estimated_effort": "12 weeks",
                "expected_impact": "Enable faster onboarding for healthcare customers"
            },
            {
                "priority": "P2",
                "action": "Add offline mode with local data caching (PP-004)",
                "rationale": "Medium priority but affects SMB segment",
                "estimated_effort": "8 weeks",
                "expected_impact": "Improve mobile user experience"
            },
            {
                "priority": "P2",
                "action": "Build bulk import tool for historical records (PP-006)",
                "rationale": "Unblocking migration for enterprise customers",
                "estimated_effort": "4 weeks",
                "expected_impact": "Reduce migration timeline from months to weeks"
            }
        ],
        "metadata": {
            "agentic_looping_iterations": 3,
            "confidence_score": 0.88,
            "processing_time_seconds": 12.5,
            "tokens_used": 15420
        }
    }

    return response


def format_output(result: Dict[str, Any]) -> None:
    """
    Format and display Glean agent results in human-readable format.

    Args:
        result: Response from Glean MCP agent
    """

    print("=" * 70)
    print("📊 GLEAN MCP AGENT RESULTS")
    print("=" * 70)
    print()

    # Agent info
    print(f"🤖 Agent: {result['agent_name']} (v{result['agent_version']})")
    print(f"📅 Analysis Date: {result['analysis_date']}")
    print(f"📁 Data Sources: {', '.join(result['data_sources_used'])}")
    print()

    # Summary
    summary = result['summary']
    print("📈 SUMMARY")
    print("-" * 70)
    print(f"Total Pain Points: {summary['total_pain_points']}")
    print(f"Total Mentions: {summary['total_mentions']}")
    print(f"Unique Customers: {summary['unique_customers']}")
    print(f"Avg Frequency Score: {summary['average_frequency_score']:.2f}")
    print(f"Avg Impact Score: {summary['average_impact_score']:.2f}")
    print()

    # Sentiment breakdown
    print("😐 Sentiment Breakdown:")
    for sentiment, count in summary['sentiment_breakdown'].items():
        print(f"   {sentiment.capitalize()}: {count}")
    print()

    # Pain points
    print("🔴 PAIN POINTS IDENTIFIED")
    print("-" * 70)
    for i, pain_point in enumerate(result['pain_points'], 1):
        print(f"\n{i}. {pain_point['description']} (ID: {pain_point['id']})")
        print(f"   Customer: {pain_point['customer']} ({pain_point['customer_segment']})")
        print(f"   Frequency: {pain_point['frequency']} (score: {pain_point['frequency_score']:.2f})")
        print(f"   Impact: {pain_point['impact']} (score: {pain_point['impact_score']:.2f})")
        print(f"   Sentiment: {pain_point['sentiment']}")
        print(f"   Mentions: {pain_point['mention_count']} times by {', '.join(pain_point['mentioned_by'])}")
        print(f"   First mentioned: {pain_point['first_mentioned']}")
        print(f"   Source: {pain_point['source']}")
        print(f"   URL: {pain_point['source_url']}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 70)
    for rec in result['recommendations']:
        print(f"\n{rec['priority']}: {rec['action']}")
        print(f"   Rationale: {rec['rationale']}")
        print(f"   Effort: {rec['estimated_effort']}")
        print(f"   Impact: {rec['expected_impact']}")

    # Metadata
    print("\n📊 METADATA")
    print("-" * 70)
    metadata = result['metadata']
    print(f"Agentic Looping Iterations: {metadata['agentic_looping_iterations']}")
    print(f"Confidence Score: {metadata['confidence_score']:.2f}")
    print(f"Processing Time: {metadata['processing_time_seconds']}s")
    print(f"Tokens Used: {metadata['tokens_used']:,}")

    print("\n" + "=" * 70)


def integrate_into_backlog(pain_points: List[Dict[str, Any]]) -> None:
    """
    Demonstrate how to integrate Glean agent results into requirements backlog.

    Args:
        pain_points: List of pain points from Glean agent
    """

    print("\n🔗 BACKLOG INTEGRATION")
    print("-" * 70)
    print("Converting pain points to backlog stories...\n")

    for pain_point in pain_points[:3]:  # Show first 3 as examples
        story_id = f"P0-PAIN-{pain_point['id']}"
        priority = "P0" if pain_point['impact_score'] > 0.80 else "P1"

        print(f"Story: {story_id}")
        print(f"  Title: {pain_point['description']}")
        print(f"  Priority: {priority} (impact: {pain_point['impact_score']:.2f})")
        print(f"  Type: Bug" if pain_point['impact'] in ['compliance risk', 'data quality'] else "  Type: Feature")
        print(f"  Source: {pain_point['source']}")
        print(f"  Mentioned by: {len(pain_point['mentioned_by'])} stakeholders")
        print(f"  Customer: {pain_point['customer']}")
        print()

    print(f"... and {len(pain_points) - 3} more pain points")
    print("\n✅ Pain points ready to add to IMPLEMENTATION_BACKLOG.yaml")


def main():
    """
    Main demonstration of Glean MCP Agent pattern.
    """

    print("🎯 GLEAN MCP AGENT EXAMPLE")
    print("   Pattern: Glean MCP Agent")
    print("   Agent: Extract Common Pain Points")
    print("   Story: P1-EXAMPLE-001\n")

    # Step 1: Extract pain points via Glean MCP
    result = extract_pain_points_via_glean(
        industry="healthcare",
        timeframe="Q1 2026",
        customer_segment="enterprise"
    )

    # Step 2: Format and display results
    format_output(result)

    # Step 3: Show integration into backlog
    integrate_into_backlog(result['pain_points'])

    print("\n" + "=" * 70)
    print("✅ EXAMPLE COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Glean MCP agents provide zero-cost access to battle-tested capabilities")
    print("  2. Context parameters narrow scope and improve relevance")
    print("  3. Structured responses enable automated backlog integration")
    print("  4. Multi-source data aggregation (Gong, HubSpot, Teams, Salesforce, Zoom)")
    print("  5. Agentic looping delivers higher quality analysis")
    print("\nNext Steps:")
    print("  • Review docs/guides/glean-mcp-agent-pattern.md")
    print("  • Identify which Glean agents apply to your use case")
    print("  • Register agent capability in Domain Registry")
    print()


if __name__ == "__main__":
    main()
