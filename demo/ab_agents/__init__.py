"""
A/B Agent Demo

Proof of concept showing Agent A (Generator) and Agent B (Validator)
collaborating via the Protocol Broker.
"""

from .agent_a import AgentA
from .agent_b import AgentB

__all__ = ["AgentA", "AgentB"]
