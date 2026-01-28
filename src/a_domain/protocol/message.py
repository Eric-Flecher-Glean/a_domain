"""
Protocol Message Data Models

Defines the core message format for agent-to-agent communication.
Based on Protocol Specification v1.0 (TECH-001).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional, Literal
from uuid import uuid4
import json


@dataclass
class Agent:
    """Agent identifier with domain and version."""

    agent_id: str
    domain: str
    version: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "version": self.version
        }


@dataclass
class Security:
    """Security information for message authentication and encryption."""

    auth_token: str
    encryption: Literal["none", "aes256"] = "none"

    def to_dict(self) -> Dict[str, str]:
        return {
            "auth_token": self.auth_token,
            "encryption": self.encryption
        }


@dataclass
class ErrorResponse:
    """Error response format per protocol specification."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retry_after: int = 0
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "code": self.code,
            "message": self.message,
            "retry_after": self.retry_after
        }
        if self.details:
            result["details"] = self.details
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        return result


@dataclass
class ProtocolMessage:
    """
    Base protocol message format for agent-to-agent communication.

    Implements the A2ACP v1.0 JSON message schema defined in TECH-001.
    """

    source_agent: Agent
    target_agent: Agent
    message_type: Literal["request", "response", "event", "error"]
    payload: Dict[str, Any]
    security: Security
    protocol_version: str = "1.0"
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    intent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "protocol_version": self.protocol_version,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "source_agent": self.source_agent.to_dict(),
            "target_agent": self.target_agent.to_dict(),
            "message_type": self.message_type,
            "intent": self.intent,
            "payload": self.payload,
            "security": self.security.to_dict()
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProtocolMessage":
        """Create message from dictionary."""
        return cls(
            protocol_version=data.get("protocol_version", "1.0"),
            message_id=data.get("message_id", str(uuid4())),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            source_agent=Agent(**data["source_agent"]),
            target_agent=Agent(**data["target_agent"]),
            message_type=data["message_type"],
            intent=data.get("intent"),
            payload=data.get("payload", {}),
            security=Security(**data["security"])
        )

    @classmethod
    def from_json(cls, json_str: str) -> "ProtocolMessage":
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def create_response(
        self,
        payload: Dict[str, Any],
        message_type: Literal["response", "error"] = "response"
    ) -> "ProtocolMessage":
        """
        Create a response message to this message.

        Swaps source/target agents and creates new message with response payload.
        """
        return ProtocolMessage(
            source_agent=self.target_agent,  # Swap
            target_agent=self.source_agent,  # Swap
            message_type=message_type,
            intent=self.intent,
            payload=payload,
            security=self.security  # Keep same security context
        )

    def create_error_response(self, error: ErrorResponse) -> "ProtocolMessage":
        """Create an error response message."""
        return self.create_response(
            payload={"error": error.to_dict()},
            message_type="error"
        )

    @property
    def correlation_id(self) -> Optional[str]:
        """Get correlation ID from payload if present."""
        return self.payload.get("correlation_id")

    @property
    def contract_id(self) -> Optional[str]:
        """Get contract ID from payload if present."""
        return self.payload.get("contract_id")


# Error codes per protocol specification
class ErrorCode:
    """Standard error codes defined in TECH-001."""

    CAPABILITY_NOT_FOUND = "CAPABILITY_NOT_FOUND"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    AUTH_FAILED = "AUTH_FAILED"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    SECURITY_POLICY_VIOLATION = "SECURITY_POLICY_VIOLATION"
