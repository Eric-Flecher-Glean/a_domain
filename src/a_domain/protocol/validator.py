"""
Message and Contract Validation

Implements validation logic for protocol messages and contracts
per Protocol Specification v1.0 (TECH-001).
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
# import jwt  # TODO: Install PyJWT for JWT validation
import json


@dataclass
class ValidationResult:
    """Result of message or contract validation."""

    valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class MessageValidator:
    """
    Validates protocol messages against specification.

    Checks:
    - Message schema compliance
    - Required fields present
    - Field type correctness
    - Message size limits
    """

    MAX_MESSAGE_SIZE_BYTES = 1_000_000  # 1 MB
    MAX_PAYLOAD_SIZE_BYTES = 900_000    # 900 KB

    def __init__(self):
        self.required_fields = [
            "protocol_version",
            "message_id",
            "timestamp",
            "source_agent",
            "target_agent",
            "message_type",
            "security"
        ]

    def validate(self, message_dict: Dict[str, Any]) -> ValidationResult:
        """
        Validate a protocol message dictionary.

        Args:
            message_dict: Message as dictionary

        Returns:
            ValidationResult with validation status
        """
        # Check message size
        message_json = json.dumps(message_dict)
        if len(message_json.encode('utf-8')) > self.MAX_MESSAGE_SIZE_BYTES:
            return ValidationResult(
                valid=False,
                error_code="MESSAGE_TOO_LARGE",
                error_message=f"Message size exceeds {self.MAX_MESSAGE_SIZE_BYTES} bytes"
            )

        # Check required fields
        for field in self.required_fields:
            if field not in message_dict:
                return ValidationResult(
                    valid=False,
                    error_code="MISSING_REQUIRED_FIELD",
                    error_message=f"Required field missing: {field}"
                )

        # Validate protocol version
        if not self._validate_protocol_version(message_dict.get("protocol_version")):
            return ValidationResult(
                valid=False,
                error_code="INVALID_PROTOCOL_VERSION",
                error_message=f"Invalid protocol version: {message_dict.get('protocol_version')}"
            )

        # Validate message type
        valid_types = ["request", "response", "event", "error"]
        if message_dict.get("message_type") not in valid_types:
            return ValidationResult(
                valid=False,
                error_code="INVALID_MESSAGE_TYPE",
                error_message=f"Message type must be one of: {valid_types}"
            )

        # Validate agent structures
        for agent_field in ["source_agent", "target_agent"]:
            if not self._validate_agent(message_dict.get(agent_field)):
                return ValidationResult(
                    valid=False,
                    error_code="INVALID_AGENT_STRUCTURE",
                    error_message=f"Invalid {agent_field} structure"
                )

        # Validate security structure
        if not self._validate_security(message_dict.get("security")):
            return ValidationResult(
                valid=False,
                error_code="INVALID_SECURITY_STRUCTURE",
                error_message="Invalid security structure"
            )

        # Validate payload size
        payload_json = json.dumps(message_dict.get("payload", {}))
        if len(payload_json.encode('utf-8')) > self.MAX_PAYLOAD_SIZE_BYTES:
            return ValidationResult(
                valid=False,
                error_code="PAYLOAD_TOO_LARGE",
                error_message=f"Payload size exceeds {self.MAX_PAYLOAD_SIZE_BYTES} bytes"
            )

        return ValidationResult(valid=True)

    def _validate_protocol_version(self, version: Any) -> bool:
        """Check protocol version format (e.g., '1.0')."""
        if not isinstance(version, str):
            return False
        parts = version.split(".")
        return len(parts) == 2 and all(p.isdigit() for p in parts)

    def _validate_agent(self, agent: Any) -> bool:
        """Validate agent structure."""
        if not isinstance(agent, dict):
            return False
        required = ["agent_id", "domain", "version"]
        return all(field in agent for field in required)

    def _validate_security(self, security: Any) -> bool:
        """Validate security structure."""
        if not isinstance(security, dict):
            return False
        if "auth_token" not in security:
            return False
        if "encryption" in security:
            if security["encryption"] not in ["none", "aes256"]:
                return False
        return True


class JWTValidator:
    """
    Validates JWT authentication tokens.

    Implements token validation per Protocol Specification v1.0.
    """

    def __init__(self, secret_key: str, issuer: str = "a_domain-auth-service"):
        """
        Initialize JWT validator.

        Args:
            secret_key: Secret key for token verification
            issuer: Expected token issuer
        """
        self.secret_key = secret_key
        self.issuer = issuer

    def validate_token(
        self,
        token: str,
        target_agent_id: str,
        required_capabilities: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate JWT token for agent-to-agent communication.

        Checks:
        - Signature verification
        - Expiration
        - Audience match
        - Required capabilities

        Args:
            token: JWT token string
            target_agent_id: Expected target agent ID (audience)
            required_capabilities: Capabilities required for this operation

        Returns:
            ValidationResult with validation status
        """
        # TODO: Implement JWT validation when PyJWT is installed
        # For now, return placeholder validation
        return ValidationResult(
            valid=False,
            error_code="NOT_IMPLEMENTED",
            error_message="JWT validation not yet implemented (requires PyJWT)"
        )


class ContractValidator:
    """
    Validates inter-agent contracts before execution.

    Implements contract validation logic per technical design (DES-001).
    """

    def validate_contract(self, contract: Dict[str, Any]) -> ValidationResult:
        """
        Validate contract structure and content.

        Args:
            contract: Contract dictionary

        Returns:
            ValidationResult with validation status
        """
        # Check required fields
        required = ["contract_id", "participants", "input_schema", "output_schema"]
        for field in required:
            if field not in contract:
                return ValidationResult(
                    valid=False,
                    error_code="INVALID_CONTRACT",
                    error_message=f"Required field missing: {field}"
                )

        # Validate participants (must be list of at least 2 agent IDs)
        participants = contract.get("participants", [])
        if not isinstance(participants, list) or len(participants) < 2:
            return ValidationResult(
                valid=False,
                error_code="INVALID_CONTRACT",
                error_message="Contract must have at least 2 participants"
            )

        # Validate schemas are dictionaries
        for schema_field in ["input_schema", "output_schema"]:
            if not isinstance(contract.get(schema_field), dict):
                return ValidationResult(
                    valid=False,
                    error_code="INVALID_CONTRACT",
                    error_message=f"Invalid {schema_field}: must be a dictionary"
                )

        return ValidationResult(valid=True)

    def check_schema_compatibility(
        self,
        provided_schema: Dict[str, Any],
        expected_schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Check if provided schema is compatible with expected schema.

        Args:
            provided_schema: Schema provided by source agent
            expected_schema: Schema expected by target agent

        Returns:
            ValidationResult with compatibility status
        """
        # Simple key-based compatibility check
        # In production, this would use JSON Schema validation
        provided_keys = set(provided_schema.keys())
        expected_keys = set(expected_schema.keys())

        missing_keys = expected_keys - provided_keys
        if missing_keys:
            return ValidationResult(
                valid=False,
                error_code="SCHEMA_MISMATCH",
                error_message="Provided schema missing required fields",
                details={"missing_fields": list(missing_keys)}
            )

        return ValidationResult(valid=True)
