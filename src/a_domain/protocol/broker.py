"""
Protocol Broker Agent

Implements the central message broker for agent-to-agent communication.
Based on System Architecture (ARCH-002).
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import uuid4
import threading
from queue import Queue

from .message import ProtocolMessage, Agent, ErrorResponse, ErrorCode
from .validator import MessageValidator, ContractValidator, ValidationResult


@dataclass
class Handshake:
    """Represents an active handshake between agents."""

    handshake_id: str
    source_agent_id: str
    target_agent_id: str
    intent: str
    status: str  # pending, accepted, rejected
    created_at: datetime
    expires_at: datetime

    def is_expired(self) -> bool:
        """Check if handshake has expired."""
        return datetime.utcnow() > self.expires_at


@dataclass
class Contract:
    """Represents a validated contract between agents."""

    contract_id: str
    participants: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    security_policy: Dict[str, Any]
    created_at: datetime
    status: str  # active, completed, terminated


@dataclass
class Collaboration:
    """Represents an active collaboration session."""

    collaboration_id: str
    contract_id: str
    participants: List[str]
    message_count: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)


class HandshakeManager:
    """Manages agent handshakes."""

    def __init__(self, timeout_seconds: int = 5):
        """
        Initialize handshake manager.

        Args:
            timeout_seconds: Handshake timeout in seconds
        """
        self.timeout_seconds = timeout_seconds
        self.handshakes: Dict[str, Handshake] = {}
        self._lock = threading.Lock()

    def create_handshake(
        self,
        source_agent_id: str,
        target_agent_id: str,
        intent: str
    ) -> Handshake:
        """
        Create a new handshake.

        Args:
            source_agent_id: Source agent ID
            target_agent_id: Target agent ID
            intent: Requested intent

        Returns:
            Created handshake
        """
        handshake_id = f"handshake-{uuid4()}"
        handshake = Handshake(
            handshake_id=handshake_id,
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            intent=intent,
            status="pending",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=self.timeout_seconds)
        )

        with self._lock:
            self.handshakes[handshake_id] = handshake

        return handshake

    def get_handshake(self, handshake_id: str) -> Optional[Handshake]:
        """Get handshake by ID."""
        with self._lock:
            return self.handshakes.get(handshake_id)

    def update_status(self, handshake_id: str, status: str) -> bool:
        """
        Update handshake status.

        Args:
            handshake_id: Handshake ID
            status: New status (accepted, rejected)

        Returns:
            True if updated, False if handshake not found
        """
        with self._lock:
            handshake = self.handshakes.get(handshake_id)
            if handshake:
                handshake.status = status
                return True
            return False

    def cleanup_expired(self) -> int:
        """
        Remove expired handshakes.

        Returns:
            Number of handshakes removed
        """
        with self._lock:
            expired = [
                hid for hid, h in self.handshakes.items()
                if h.is_expired()
            ]
            for hid in expired:
                del self.handshakes[hid]
            return len(expired)


class ContractStore:
    """Stores and manages contracts."""

    def __init__(self):
        self.contracts: Dict[str, Contract] = {}
        self._lock = threading.Lock()

    def store_contract(self, contract: Contract) -> None:
        """Store a contract."""
        with self._lock:
            self.contracts[contract.contract_id] = contract

    def get_contract(self, contract_id: str) -> Optional[Contract]:
        """Get contract by ID."""
        with self._lock:
            return self.contracts.get(contract_id)

    def terminate_contract(self, contract_id: str) -> bool:
        """
        Terminate a contract.

        Args:
            contract_id: Contract ID

        Returns:
            True if terminated, False if not found
        """
        with self._lock:
            contract = self.contracts.get(contract_id)
            if contract:
                contract.status = "terminated"
                return True
            return False


class MessageRouter:
    """Routes messages between agents."""

    def __init__(self):
        self.routes: Dict[str, Callable] = {}  # agent_id -> message handler
        self.message_queue = Queue()
        self._lock = threading.Lock()

    def register_agent(self, agent_id: str, handler: Callable) -> None:
        """
        Register an agent message handler.

        Args:
            agent_id: Agent ID
            handler: Callable that accepts ProtocolMessage
        """
        with self._lock:
            self.routes[agent_id] = handler

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        with self._lock:
            if agent_id in self.routes:
                del self.routes[agent_id]

    def route_message(self, message: ProtocolMessage) -> bool:
        """
        Route message to target agent.

        Args:
            message: Protocol message

        Returns:
            True if routed, False if target not found
        """
        target_id = message.target_agent.agent_id

        with self._lock:
            handler = self.routes.get(target_id)

        if handler:
            # In production, this would be async
            handler(message)
            return True
        else:
            return False

    def is_agent_registered(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        with self._lock:
            return agent_id in self.routes


class ProtocolBrokerAgent:
    """
    Central broker for agent-to-agent communication.

    Responsibilities:
    - Manage agent handshakes
    - Negotiate and validate contracts
    - Route messages between agents
    - Track active collaborations
    """

    def __init__(self, jwt_secret: Optional[str] = None):
        """
        Initialize protocol broker.

        Args:
            jwt_secret: Secret key for JWT validation (optional)
        """
        self.handshake_manager = HandshakeManager()
        self.contract_store = ContractStore()
        self.message_router = MessageRouter()
        self.message_validator = MessageValidator()
        self.contract_validator = ContractValidator()

        # Track active collaborations
        self.collaborations: Dict[str, Collaboration] = {}
        self._lock = threading.Lock()

    def initiate_handshake(
        self,
        source_agent_id: str,
        target_agent_id: str,
        intent: str
    ) -> ValidationResult:
        """
        Initiate handshake between two agents.

        Args:
            source_agent_id: Source agent ID
            target_agent_id: Target agent ID
            intent: Requested intent/capability

        Returns:
            ValidationResult with handshake ID if successful
        """
        # Verify target agent exists
        if not self.message_router.is_agent_registered(target_agent_id):
            return ValidationResult(
                valid=False,
                error_code=ErrorCode.CAPABILITY_NOT_FOUND,
                error_message=f"Target agent not registered: {target_agent_id}"
            )

        # Create handshake
        handshake = self.handshake_manager.create_handshake(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            intent=intent
        )

        return ValidationResult(
            valid=True,
            details={"handshake_id": handshake.handshake_id}
        )

    def accept_handshake(self, handshake_id: str) -> ValidationResult:
        """
        Accept a handshake and create contract.

        Args:
            handshake_id: Handshake ID

        Returns:
            ValidationResult with contract ID if successful
        """
        handshake = self.handshake_manager.get_handshake(handshake_id)

        if not handshake:
            return ValidationResult(
                valid=False,
                error_code=ErrorCode.TIMEOUT,
                error_message="Handshake not found or expired"
            )

        if handshake.is_expired():
            return ValidationResult(
                valid=False,
                error_code=ErrorCode.TIMEOUT,
                error_message="Handshake expired"
            )

        # Update handshake status
        self.handshake_manager.update_status(handshake_id, "accepted")

        # Create contract
        contract_id = f"contract-{uuid4()}"
        contract = Contract(
            contract_id=contract_id,
            participants=[handshake.source_agent_id, handshake.target_agent_id],
            input_schema={},  # TODO: Load from capability registry
            output_schema={},  # TODO: Load from capability registry
            security_policy={},
            created_at=datetime.utcnow(),
            status="active"
        )

        # Validate contract
        validation = self.contract_validator.validate_contract(contract.__dict__)
        if not validation.valid:
            return validation

        # Store contract
        self.contract_store.store_contract(contract)

        return ValidationResult(
            valid=True,
            details={"contract_id": contract_id}
        )

    def route_message(self, message: ProtocolMessage) -> ValidationResult:
        """
        Route a protocol message to target agent.

        Args:
            message: Protocol message

        Returns:
            ValidationResult indicating success or failure
        """
        # Validate message format
        validation = self.message_validator.validate(message.to_dict())
        if not validation.valid:
            return validation

        # Verify contract if contract_id present
        contract_id = message.contract_id
        if contract_id:
            contract = self.contract_store.get_contract(contract_id)
            if not contract:
                return ValidationResult(
                    valid=False,
                    error_code=ErrorCode.CONTRACT_VIOLATION,
                    error_message=f"Contract not found: {contract_id}"
                )

            if contract.status != "active":
                return ValidationResult(
                    valid=False,
                    error_code=ErrorCode.CONTRACT_VIOLATION,
                    error_message=f"Contract not active: {contract.status}"
                )

            # Update collaboration tracking
            self._update_collaboration(contract_id, message)

        # Route message
        success = self.message_router.route_message(message)

        if not success:
            return ValidationResult(
                valid=False,
                error_code=ErrorCode.CAPABILITY_NOT_FOUND,
                error_message=f"Target agent not registered: {message.target_agent.agent_id}"
            )

        return ValidationResult(valid=True)

    def terminate_collaboration(self, collaboration_id: str) -> ValidationResult:
        """
        Terminate an active collaboration.

        Args:
            collaboration_id: Collaboration ID

        Returns:
            ValidationResult indicating success
        """
        with self._lock:
            collaboration = self.collaborations.get(collaboration_id)
            if not collaboration:
                return ValidationResult(
                    valid=False,
                    error_code=ErrorCode.INTERNAL_ERROR,
                    error_message=f"Collaboration not found: {collaboration_id}"
                )

            # Terminate contract
            self.contract_store.terminate_contract(collaboration.contract_id)

            # Remove collaboration
            del self.collaborations[collaboration_id]

        return ValidationResult(valid=True)

    def register_agent(self, agent_id: str, handler: Callable) -> None:
        """
        Register an agent with the broker.

        Args:
            agent_id: Agent ID
            handler: Message handler function
        """
        self.message_router.register_agent(agent_id, handler)

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the broker.

        Args:
            agent_id: Agent ID
        """
        self.message_router.unregister_agent(agent_id)

    def get_collaboration_stats(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a collaboration.

        Args:
            collaboration_id: Collaboration ID

        Returns:
            Statistics dictionary or None if not found
        """
        with self._lock:
            collaboration = self.collaborations.get(collaboration_id)
            if not collaboration:
                return None

            duration = datetime.utcnow() - collaboration.started_at

            return {
                "collaboration_id": collaboration_id,
                "contract_id": collaboration.contract_id,
                "participants": collaboration.participants,
                "message_count": collaboration.message_count,
                "duration_seconds": duration.total_seconds(),
                "started_at": collaboration.started_at.isoformat(),
                "last_activity": collaboration.last_activity.isoformat()
            }

    def _update_collaboration(self, contract_id: str, message: ProtocolMessage) -> None:
        """Update collaboration tracking for a message."""
        with self._lock:
            # Find collaboration by contract_id
            collab = None
            for c in self.collaborations.values():
                if c.contract_id == contract_id:
                    collab = c
                    break

            # Create collaboration if it doesn't exist
            if not collab:
                collaboration_id = f"collab-{uuid4()}"
                contract = self.contract_store.get_contract(contract_id)
                if contract:
                    collab = Collaboration(
                        collaboration_id=collaboration_id,
                        contract_id=contract_id,
                        participants=contract.participants
                    )
                    self.collaborations[collaboration_id] = collab

            # Update stats
            if collab:
                collab.message_count += 1
                collab.last_activity = datetime.utcnow()
