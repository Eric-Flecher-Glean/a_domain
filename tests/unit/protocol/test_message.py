"""
Unit tests for protocol message format.

Tests AC1: Protocol spec defines message format, authentication, error handling
"""

import pytest
import json
from src.a_domain.protocol.message import (
    ProtocolMessage,
    Agent,
    Security,
    ErrorResponse,
    ErrorCode
)
from src.a_domain.protocol.validator import MessageValidator


class TestProtocolMessage:
    """Test protocol message creation and serialization."""

    def test_message_creation(self):
        """Test creating a protocol message."""
        source = Agent(agent_id="test-agent", domain="a_domain", version="1.0.0")
        target = Agent(agent_id="target-agent", domain="test_domain", version="2.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test_intent",
            payload={"test": "data"},
            security=security
        )

        assert message.protocol_version == "1.0"
        assert message.source_agent.agent_id == "test-agent"
        assert message.target_agent.agent_id == "target-agent"
        assert message.message_type == "request"
        assert message.intent == "test_intent"

    def test_message_to_dict(self):
        """Test message serialization to dictionary."""
        source = Agent(agent_id="test-agent", domain="a_domain", version="1.0.0")
        target = Agent(agent_id="target-agent", domain="test_domain", version="2.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test_intent",
            payload={"test": "data"},
            security=security
        )

        message_dict = message.to_dict()

        assert "protocol_version" in message_dict
        assert "message_id" in message_dict
        assert "timestamp" in message_dict
        assert message_dict["source_agent"]["agent_id"] == "test-agent"
        assert message_dict["target_agent"]["agent_id"] == "target-agent"

    def test_message_to_json(self):
        """Test message serialization to JSON."""
        source = Agent(agent_id="test-agent", domain="a_domain", version="1.0.0")
        target = Agent(agent_id="target-agent", domain="test_domain", version="2.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test_intent",
            payload={"test": "data"},
            security=security
        )

        json_str = message.to_json()
        parsed = json.loads(json_str)

        assert parsed["protocol_version"] == "1.0"
        assert parsed["message_type"] == "request"

    def test_message_from_dict(self):
        """Test message deserialization from dictionary."""
        message_dict = {
            "protocol_version": "1.0",
            "message_id": "test-id",
            "timestamp": "2026-01-27T14:30:00Z",
            "source_agent": {
                "agent_id": "test-agent",
                "domain": "a_domain",
                "version": "1.0.0"
            },
            "target_agent": {
                "agent_id": "target-agent",
                "domain": "test_domain",
                "version": "2.0.0"
            },
            "message_type": "request",
            "intent": "test_intent",
            "payload": {"test": "data"},
            "security": {
                "auth_token": "test-token",
                "encryption": "none"
            }
        }

        message = ProtocolMessage.from_dict(message_dict)

        assert message.message_id == "test-id"
        assert message.source_agent.agent_id == "test-agent"
        assert message.target_agent.agent_id == "target-agent"

    def test_create_response(self):
        """Test creating response message."""
        source = Agent(agent_id="test-agent", domain="a_domain", version="1.0.0")
        target = Agent(agent_id="target-agent", domain="test_domain", version="2.0.0")
        security = Security(auth_token="test-token")

        request = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test_intent",
            payload={"test": "data"},
            security=security
        )

        response = request.create_response(payload={"result": "success"})

        # Source and target should be swapped
        assert response.source_agent.agent_id == "target-agent"
        assert response.target_agent.agent_id == "test-agent"
        assert response.message_type == "response"
        assert response.intent == "test_intent"

    def test_create_error_response(self):
        """Test creating error response message."""
        source = Agent(agent_id="test-agent", domain="a_domain", version="1.0.0")
        target = Agent(agent_id="target-agent", domain="test_domain", version="2.0.0")
        security = Security(auth_token="test-token")

        request = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test_intent",
            payload={"test": "data"},
            security=security
        )

        error = ErrorResponse(
            code=ErrorCode.SCHEMA_MISMATCH,
            message="Schema mismatch",
            details={"field": "test"}
        )

        error_response = request.create_error_response(error)

        assert error_response.message_type == "error"
        assert "error" in error_response.payload
        assert error_response.payload["error"]["code"] == ErrorCode.SCHEMA_MISMATCH


class TestMessageValidator:
    """Test message validation."""

    def test_valid_message(self):
        """Test validation of valid message."""
        validator = MessageValidator()

        message_dict = {
            "protocol_version": "1.0",
            "message_id": "test-id",
            "timestamp": "2026-01-27T14:30:00Z",
            "source_agent": {
                "agent_id": "test-agent",
                "domain": "a_domain",
                "version": "1.0.0"
            },
            "target_agent": {
                "agent_id": "target-agent",
                "domain": "test_domain",
                "version": "2.0.0"
            },
            "message_type": "request",
            "security": {
                "auth_token": "test-token",
                "encryption": "none"
            },
            "payload": {}
        }

        result = validator.validate(message_dict)
        assert result.valid is True

    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        validator = MessageValidator()

        message_dict = {
            "protocol_version": "1.0",
            # Missing message_id
            "timestamp": "2026-01-27T14:30:00Z",
            "source_agent": {
                "agent_id": "test-agent",
                "domain": "a_domain",
                "version": "1.0.0"
            },
            "target_agent": {
                "agent_id": "target-agent",
                "domain": "test_domain",
                "version": "2.0.0"
            },
            "message_type": "request",
            "security": {
                "auth_token": "test-token"
            }
        }

        result = validator.validate(message_dict)
        assert result.valid is False
        assert result.error_code == "MISSING_REQUIRED_FIELD"

    def test_invalid_message_type(self):
        """Test validation fails with invalid message type."""
        validator = MessageValidator()

        message_dict = {
            "protocol_version": "1.0",
            "message_id": "test-id",
            "timestamp": "2026-01-27T14:30:00Z",
            "source_agent": {
                "agent_id": "test-agent",
                "domain": "a_domain",
                "version": "1.0.0"
            },
            "target_agent": {
                "agent_id": "target-agent",
                "domain": "test_domain",
                "version": "2.0.0"
            },
            "message_type": "invalid_type",  # Invalid
            "security": {
                "auth_token": "test-token"
            }
        }

        result = validator.validate(message_dict)
        assert result.valid is False
        assert result.error_code == "INVALID_MESSAGE_TYPE"


class TestErrorResponse:
    """Test error response format."""

    def test_error_response_creation(self):
        """Test creating error response."""
        error = ErrorResponse(
            code=ErrorCode.AUTH_FAILED,
            message="Authentication failed",
            details={"reason": "expired token"},
            retry_after=300
        )

        error_dict = error.to_dict()

        assert error_dict["code"] == ErrorCode.AUTH_FAILED
        assert error_dict["message"] == "Authentication failed"
        assert error_dict["details"]["reason"] == "expired token"
        assert error_dict["retry_after"] == 300

    def test_all_error_codes_defined(self):
        """Test all standard error codes are defined."""
        assert hasattr(ErrorCode, "CAPABILITY_NOT_FOUND")
        assert hasattr(ErrorCode, "SCHEMA_MISMATCH")
        assert hasattr(ErrorCode, "AUTH_FAILED")
        assert hasattr(ErrorCode, "TIMEOUT")
        assert hasattr(ErrorCode, "INTERNAL_ERROR")
        assert hasattr(ErrorCode, "RATE_LIMIT_EXCEEDED")
        assert hasattr(ErrorCode, "CONTRACT_VIOLATION")
        assert hasattr(ErrorCode, "SECURITY_POLICY_VIOLATION")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
