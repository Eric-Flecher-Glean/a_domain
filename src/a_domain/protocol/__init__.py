"""
Agent-to-Agent Communication Protocol (A2ACP) v1.0

This module implements the standardized protocol for agent collaboration
across all domains in the a_domain platform.
"""

from .message import ProtocolMessage, Agent, Security, ErrorResponse
from .broker import ProtocolBrokerAgent
from .validator import MessageValidator, ContractValidator
from .discovery import CapabilityDiscoveryAgent, CapabilitySpec, AgentMatch

__version__ = "1.0.0"

__all__ = [
    "ProtocolMessage",
    "Agent",
    "Security",
    "ErrorResponse",
    "ProtocolBrokerAgent",
    "MessageValidator",
    "ContractValidator",
    "CapabilityDiscoveryAgent",
    "CapabilitySpec",
    "AgentMatch",
]
