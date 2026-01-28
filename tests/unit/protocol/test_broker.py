"""
Unit tests for ProtocolBrokerAgent.

Tests AC2: ProtocolBrokerAgent routes messages between agents
"""

import pytest
import time
from src.a_domain.protocol.broker import (
    ProtocolBrokerAgent,
    HandshakeManager,
    ContractStore,
    MessageRouter,
    Handshake,
    Contract
)
from src.a_domain.protocol.message import (
    ProtocolMessage,
    Agent,
    Security,
    ErrorCode
)


class TestHandshakeManager:
    """Test handshake management."""

    def test_create_handshake(self):
        """Test creating a handshake."""
        manager = HandshakeManager(timeout_seconds=5)

        handshake = manager.create_handshake(
            source_agent_id="agent-a",
            target_agent_id="agent-b",
            intent="test_intent"
        )

        assert handshake.source_agent_id == "agent-a"
        assert handshake.target_agent_id == "agent-b"
        assert handshake.intent == "test_intent"
        assert handshake.status == "pending"
        assert handshake.handshake_id is not None

    def test_get_handshake(self):
        """Test retrieving a handshake."""
        manager = HandshakeManager()
        handshake = manager.create_handshake("agent-a", "agent-b", "test")

        retrieved = manager.get_handshake(handshake.handshake_id)

        assert retrieved is not None
        assert retrieved.handshake_id == handshake.handshake_id

    def test_update_status(self):
        """Test updating handshake status."""
        manager = HandshakeManager()
        handshake = manager.create_handshake("agent-a", "agent-b", "test")

        result = manager.update_status(handshake.handshake_id, "accepted")

        assert result is True
        retrieved = manager.get_handshake(handshake.handshake_id)
        assert retrieved.status == "accepted"

    def test_handshake_expiration(self):
        """Test handshake expiration."""
        manager = HandshakeManager(timeout_seconds=1)
        handshake = manager.create_handshake("agent-a", "agent-b", "test")

        # Initially not expired
        assert not handshake.is_expired()

        # Wait for expiration
        time.sleep(1.5)

        # Now expired
        assert handshake.is_expired()

    def test_cleanup_expired(self):
        """Test cleanup of expired handshakes."""
        manager = HandshakeManager(timeout_seconds=1)

        # Create handshakes
        handshake1 = manager.create_handshake("agent-a", "agent-b", "test1")
        handshake2 = manager.create_handshake("agent-c", "agent-d", "test2")

        # Wait for expiration
        time.sleep(1.5)

        # Cleanup
        removed_count = manager.cleanup_expired()

        assert removed_count == 2
        assert manager.get_handshake(handshake1.handshake_id) is None
        assert manager.get_handshake(handshake2.handshake_id) is None


class TestContractStore:
    """Test contract storage."""

    def test_store_and_get_contract(self):
        """Test storing and retrieving a contract."""
        from datetime import datetime

        store = ContractStore()

        contract = Contract(
            contract_id="test-contract",
            participants=["agent-a", "agent-b"],
            input_schema={"field": "string"},
            output_schema={"result": "string"},
            security_policy={},
            created_at=datetime.utcnow(),
            status="active"
        )

        store.store_contract(contract)

        retrieved = store.get_contract("test-contract")

        assert retrieved is not None
        assert retrieved.contract_id == "test-contract"
        assert retrieved.participants == ["agent-a", "agent-b"]

    def test_terminate_contract(self):
        """Test terminating a contract."""
        from datetime import datetime

        store = ContractStore()

        contract = Contract(
            contract_id="test-contract",
            participants=["agent-a", "agent-b"],
            input_schema={},
            output_schema={},
            security_policy={},
            created_at=datetime.utcnow(),
            status="active"
        )

        store.store_contract(contract)

        result = store.terminate_contract("test-contract")

        assert result is True

        retrieved = store.get_contract("test-contract")
        assert retrieved.status == "terminated"


class TestMessageRouter:
    """Test message routing."""

    def test_register_agent(self):
        """Test registering an agent."""
        router = MessageRouter()

        def handler(message):
            pass

        router.register_agent("test-agent", handler)

        assert router.is_agent_registered("test-agent")

    def test_unregister_agent(self):
        """Test unregistering an agent."""
        router = MessageRouter()

        def handler(message):
            pass

        router.register_agent("test-agent", handler)
        router.unregister_agent("test-agent")

        assert not router.is_agent_registered("test-agent")

    def test_route_message(self):
        """Test routing a message."""
        router = MessageRouter()

        received_messages = []

        def handler(message):
            received_messages.append(message)

        router.register_agent("target-agent", handler)

        # Create message
        source = Agent(agent_id="source-agent", domain="test", version="1.0.0")
        target = Agent(agent_id="target-agent", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test",
            payload={},
            security=security
        )

        # Route message
        success = router.route_message(message)

        assert success is True
        assert len(received_messages) == 1
        assert received_messages[0].target_agent.agent_id == "target-agent"

    def test_route_message_agent_not_found(self):
        """Test routing to unregistered agent."""
        router = MessageRouter()

        source = Agent(agent_id="source-agent", domain="test", version="1.0.0")
        target = Agent(agent_id="unknown-agent", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test",
            payload={},
            security=security
        )

        success = router.route_message(message)

        assert success is False


class TestProtocolBrokerAgent:
    """Test ProtocolBrokerAgent functionality."""

    def test_broker_initialization(self):
        """Test broker initialization."""
        broker = ProtocolBrokerAgent()

        assert broker.handshake_manager is not None
        assert broker.contract_store is not None
        assert broker.message_router is not None

    def test_initiate_handshake(self):
        """Test initiating a handshake."""
        broker = ProtocolBrokerAgent()

        # Register target agent
        def handler(message):
            pass

        broker.register_agent("agent-b", handler)

        # Initiate handshake
        result = broker.initiate_handshake(
            source_agent_id="agent-a",
            target_agent_id="agent-b",
            intent="test_intent"
        )

        assert result.valid is True
        assert "handshake_id" in result.details

    def test_initiate_handshake_target_not_found(self):
        """Test handshake with unregistered target."""
        broker = ProtocolBrokerAgent()

        result = broker.initiate_handshake(
            source_agent_id="agent-a",
            target_agent_id="unknown-agent",
            intent="test"
        )

        assert result.valid is False
        assert result.error_code == ErrorCode.CAPABILITY_NOT_FOUND

    def test_accept_handshake(self):
        """Test accepting a handshake."""
        broker = ProtocolBrokerAgent()

        # Register agent
        def handler(message):
            pass

        broker.register_agent("agent-b", handler)

        # Initiate and accept handshake
        handshake_result = broker.initiate_handshake("agent-a", "agent-b", "test")
        handshake_id = handshake_result.details["handshake_id"]

        accept_result = broker.accept_handshake(handshake_id)

        assert accept_result.valid is True
        assert "contract_id" in accept_result.details

    def test_route_message(self):
        """Test routing messages between agents."""
        broker = ProtocolBrokerAgent()

        received_messages = []

        def handler(message):
            received_messages.append(message)

        # Register agents
        broker.register_agent("agent-a", handler)
        broker.register_agent("agent-b", handler)

        # Create and route message
        source = Agent(agent_id="agent-a", domain="test", version="1.0.0")
        target = Agent(agent_id="agent-b", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test",
            payload={"data": "test"},
            security=security
        )

        result = broker.route_message(message)

        assert result.valid is True
        assert len(received_messages) == 1
        assert received_messages[0].payload["data"] == "test"

    def test_route_message_with_contract(self):
        """Test routing message with contract validation."""
        broker = ProtocolBrokerAgent()

        received_messages = []

        def handler(message):
            received_messages.append(message)

        # Register agents
        broker.register_agent("agent-a", handler)
        broker.register_agent("agent-b", handler)

        # Create handshake and contract
        handshake_result = broker.initiate_handshake("agent-a", "agent-b", "test")
        handshake_id = handshake_result.details["handshake_id"]

        accept_result = broker.accept_handshake(handshake_id)
        contract_id = accept_result.details["contract_id"]

        # Create message with contract_id
        source = Agent(agent_id="agent-a", domain="test", version="1.0.0")
        target = Agent(agent_id="agent-b", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test",
            payload={
                "data": "test",
                "contract_id": contract_id
            },
            security=security
        )

        result = broker.route_message(message)

        assert result.valid is True
        assert len(received_messages) == 1

    def test_collaboration_tracking(self):
        """Test collaboration tracking."""
        broker = ProtocolBrokerAgent()

        def handler(message):
            pass

        # Register agents
        broker.register_agent("agent-a", handler)
        broker.register_agent("agent-b", handler)

        # Create contract
        handshake_result = broker.initiate_handshake("agent-a", "agent-b", "test")
        handshake_id = handshake_result.details["handshake_id"]
        accept_result = broker.accept_handshake(handshake_id)
        contract_id = accept_result.details["contract_id"]

        # Send messages to create collaboration
        source = Agent(agent_id="agent-a", domain="test", version="1.0.0")
        target = Agent(agent_id="agent-b", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        for i in range(3):
            message = ProtocolMessage(
                source_agent=source,
                target_agent=target,
                message_type="request",
                intent="test",
                payload={"contract_id": contract_id},
                security=security
            )
            broker.route_message(message)

        # Check collaboration stats
        collaboration_id = list(broker.collaborations.keys())[0]
        stats = broker.get_collaboration_stats(collaboration_id)

        assert stats is not None
        assert stats["message_count"] == 3
        assert stats["contract_id"] == contract_id
        assert stats["participants"] == ["agent-a", "agent-b"]

    def test_terminate_collaboration(self):
        """Test terminating a collaboration."""
        broker = ProtocolBrokerAgent()

        def handler(message):
            pass

        # Register agents and create collaboration
        broker.register_agent("agent-a", handler)
        broker.register_agent("agent-b", handler)

        handshake_result = broker.initiate_handshake("agent-a", "agent-b", "test")
        handshake_id = handshake_result.details["handshake_id"]
        accept_result = broker.accept_handshake(handshake_id)
        contract_id = accept_result.details["contract_id"]

        # Send message to create collaboration
        source = Agent(agent_id="agent-a", domain="test", version="1.0.0")
        target = Agent(agent_id="agent-b", domain="test", version="1.0.0")
        security = Security(auth_token="test-token")

        message = ProtocolMessage(
            source_agent=source,
            target_agent=target,
            message_type="request",
            intent="test",
            payload={"contract_id": contract_id},
            security=security
        )
        broker.route_message(message)

        # Get collaboration ID
        collaboration_id = list(broker.collaborations.keys())[0]

        # Terminate
        result = broker.terminate_collaboration(collaboration_id)

        assert result.valid is True

        # Contract should be terminated
        contract = broker.contract_store.get_contract(contract_id)
        assert contract.status == "terminated"

        # Collaboration should be removed
        stats = broker.get_collaboration_stats(collaboration_id)
        assert stats is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
