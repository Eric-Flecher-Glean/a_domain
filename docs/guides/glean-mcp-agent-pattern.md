# Glean MCP Agent Implementation Pattern

**Pattern Type**: Glean MCP Agent
**Purpose**: Access existing Glean agents via Model Context Protocol
**Repository Reference**: ADR-006 in `docs/architecture/ddd-specification.md`

---

## Overview

The Glean MCP Agent pattern allows you to leverage existing, battle-tested Glean agents deployed across 222 customers with 200+ agents each. These agents are accessed via the `mcp__glean__chat` tool from the Model Context Protocol.

### When to Use This Pattern

✅ **Use Glean MCP Agent when:**
- Capability already exists in Glean platform (Sales, Support, SDLC agents)
- Need multi-source data integration with enterprise systems (Salesforce, Gong, GitHub, etc.)
- Require Glean's agentic looping feature for complex analysis
- Need bi-directional system integration (read from one, write to another)
- Want zero implementation cost (agent already deployed)

❌ **Don't use when:**
- Custom domain-specific logic needed (use XML Prompt Agent instead)
- Rapid prototyping required without Glean setup
- Agent workflow requires custom multi-step orchestration
- Building SDLC meta-agents

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Your Application                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Python/TypeScript Code                            │  │
│  │                                                    │  │
│  │  mcp__glean__chat(                                │  │
│  │    message="Extract pain points from Q1 calls",  │  │
│  │    context={"industry": "healthcare"}            │  │
│  │  )                                                │  │
│  └──────────────────┬────────────────────────────────┘  │
└─────────────────────┼────────────────────────────────────┘
                      │ MCP Protocol
                      ↓
┌─────────────────────────────────────────────────────────┐
│  Glean MCP Server                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Routes to appropriate Glean Agent                 │  │
│  │ - Extract Common Pain Points                      │  │
│  │ - Deal Strategy                                   │  │
│  │ - Customer Sentiment Scorer                       │  │
│  │ - etc.                                            │  │
│  └──────────────────┬────────────────────────────────┘  │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│  Glean Platform                                          │
│  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌───────────┐  │
│  │ Gong     │  │ HubSpot │  │ Teams  │  │Salesforce │  │
│  └──────────┘  └─────────┘  └────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### 1. Import MCP Tool

```python
# Available when running in Claude Code environment
# or with Glean MCP server configured

from mcp.tools import mcp__glean__chat
```

### 2. Construct Message and Context

```python
# Basic invocation
message = "Extract customer pain points from sales calls in Q1 2026"

# Optional context to narrow scope
context = {
    "industry": "healthcare",
    "customer_segment": "enterprise",
    "timeframe": "Q1 2026"
}
```

### 3. Invoke Agent

```python
response = mcp__glean__chat(
    message=message,
    context=[f"{key}: {value}" for key, value in context.items()]
)
```

### 4. Parse Response

```python
# Response structure (example)
result = {
    "pain_points": [
        {
            "description": "Manual data entry taking 10+ hours/week",
            "frequency": "high",
            "impact": "productivity loss",
            "source": "Gong call #12345",
            "customer": "Memorial Hospital"
        },
        {
            "description": "Integration with legacy EMR systems",
            "frequency": "medium",
            "impact": "technical debt",
            "source": "HubSpot ticket #67890",
            "customer": "Regional Health Network"
        }
    ],
    "summary": "6 pain points identified across 15 calls",
    "recommendations": [
        "Prioritize automation for data entry",
        "Investigate EMR integration solutions"
    ]
}
```

---

## Complete Example

See `examples/glean_mcp_agent_example.py` for a runnable demonstration.

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Example: Glean MCP Agent - Customer Pain Point Extractor

Demonstrates how to:
1. Invoke existing Glean agent via mcp__glean__chat
2. Pass context parameters
3. Parse and integrate results
"""

def extract_pain_points_via_glean(industry, timeframe):
    """
    Extract customer pain points using Glean's "Extract Common Pain Points" agent.

    This agent integrates data from:
    - Gong (call transcripts)
    - HubSpot (customer records)
    - Teams (chat logs)
    - Salesforce (opportunities)
    - Zoom (meeting transcripts)
    """

    # Construct message
    message = f"Extract customer pain points from sales calls in {timeframe}"

    # Add context
    context = [
        f"industry: {industry}",
        f"timeframe: {timeframe}",
        "focus: technical challenges and integration issues"
    ]

    print(f"🔍 Invoking Glean MCP Agent...")
    print(f"   Message: {message}")
    print(f"   Context: {context}")
    print()

    # In real implementation, this would call mcp__glean__chat
    # For demo purposes, we return mock data

    # response = mcp__glean__chat(message=message, context=context)

    # Mock response for demonstration
    response = {
        "pain_points": [
            {
                "description": "Manual data entry taking 10+ hours/week",
                "frequency": "high",
                "impact": "productivity",
                "source": "Gong call #12345",
                "customer": "Memorial Hospital"
            },
            {
                "description": "Integration with legacy EMR systems",
                "frequency": "medium",
                "impact": "technical debt",
                "source": "HubSpot ticket #67890",
                "customer": "Regional Health Network"
            },
            {
                "description": "Real-time sync delays causing data inconsistency",
                "frequency": "high",
                "impact": "data quality",
                "source": "Teams chat with CTO",
                "customer": "City General Hospital"
            }
        ],
        "summary": "3 pain points identified across 8 calls",
        "recommendations": [
            "Prioritize automation for data entry",
            "Investigate EMR integration solutions",
            "Implement real-time sync monitoring"
        ]
    }

    return response


def main():
    print("🎯 Glean MCP Agent Example: Customer Pain Point Extractor\\n")
    print("=" * 60)
    print()

    # Extract pain points
    result = extract_pain_points_via_glean(
        industry="healthcare",
        timeframe="Q1 2026"
    )

    # Display results
    print("✅ Pain points extracted successfully!\\n")
    print(f"📊 Summary: {result['summary']}\\n")

    print("🔴 Pain Points Identified:")
    for i, pain_point in enumerate(result['pain_points'], 1):
        print(f"\\n{i}. {pain_point['description']}")
        print(f"   Frequency: {pain_point['frequency']}")
        print(f"   Impact: {pain_point['impact']}")
        print(f"   Source: {pain_point['source']}")
        print(f"   Customer: {pain_point['customer']}")

    print(f"\\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"   • {rec}")

    print("\\n" + "=" * 60)
    print("✅ Example complete! Glean MCP agent successfully invoked.")


if __name__ == "__main__":
    main()
```

---

## Benefits

### Zero Implementation Cost
- Agent already deployed across 222 customers
- Battle-tested with high usage (550K+ runs/week at T-Mobile)
- No development effort required

### Multi-Source Integration
- Automatically aggregates data from 5+ sources:
  - Gong (call transcripts)
  - HubSpot (CRM data)
  - Teams (chat logs)
  - Salesforce (opportunities)
  - Zoom (meeting transcripts)

### Agentic Looping
- Glean agent uses agentic looping for complex analysis
- Iterative refinement for higher quality results
- Handles ambiguous queries intelligently

### Enterprise Security
- Leverages Glean's security model
- Permission enforcement at data source level
- No custom security implementation needed

---

## Limitations

### Customization Constraints
- Cannot modify agent logic or prompts
- Limited to Glean's agent configuration options
- Cannot add custom data sources easily

### Dependency on Glean Platform
- Requires Glean deployment and configuration
- Performance dependent on Glean infrastructure
- API rate limits may apply

### Limited to Existing Agents
- Only 50+ pre-built agents available
- If capability doesn't exist, need XML Prompt Agent instead
- Cannot prototype new agent types quickly

---

## Comparison with XML Prompt Agent

| Aspect | Glean MCP Agent | XML Prompt Agent |
|--------|----------------|------------------|
| **Development Time** | 0 (already exists) | Minutes to hours |
| **Customization** | Limited | Full control |
| **Data Sources** | Pre-configured | Manual integration |
| **Security** | Built-in | Manual implementation |
| **Iteration Speed** | Slow (Glean release cycle) | Fast (edit XML) |
| **Agentic Looping** | Built-in | Manual orchestration |
| **Cost** | Zero (existing investment) | Development time |

---

## Related Documentation

- **ADR-006**: Dual-Mode Agent Implementation Strategy (`docs/architecture/ddd-specification.md`)
- **Glean Agent Library**: `docs/research/glean-agent-usage-categorization.md`
- **XML Prompt Pattern**: `docs/guides/xml-prompt-agent-pattern.md`
- **Example Code**: `examples/glean_mcp_agent_example.py`

---

## Next Steps

1. ✅ Review this guide
2. ✅ Run the example: `uv run examples/glean_mcp_agent_example.py`
3. 🔄 Identify which Glean agents apply to your use case
4. 🔄 Implement integration following this pattern
5. 🔄 Register agent capability in Domain Registry

---

**Last Updated**: 2026-02-03
**Pattern Version**: 1.0.0
**Related Stories**: P1-EXAMPLE-001, P1-EXAMPLE-002
