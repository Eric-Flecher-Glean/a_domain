"""
Unit tests for CapabilityDiscoveryAgent.

Tests AC3: Agent registry supports registration and discovery
"""

import pytest
from src.a_domain.protocol.discovery import (
    CapabilityDiscoveryAgent,
    CapabilitySpec,
    CapabilityRegistry,
    CompatibilityMatrix,
    AgentMatch,
    CompatibilityResult
)


class TestCapabilitySpec:
    """Test capability specification."""

    def test_capability_creation(self):
        """Test creating a capability specification."""
        cap = CapabilitySpec(
            agent_id="test-agent",
            domain="test_domain",
            version="1.0.0",
            intents=["test_intent"],
            input_schema={"field": "string"},
            output_schema={"result": "string"}
        )

        assert cap.agent_id == "test-agent"
        assert cap.domain == "test_domain"
        assert "test_intent" in cap.intents

    def test_matches_intent(self):
        """Test intent matching."""
        cap = CapabilitySpec(
            agent_id="test-agent",
            domain="test",
            version="1.0.0",
            intents=["provision_dataset", "validate_data"],
            input_schema={},
            output_schema={}
        )

        assert cap.matches_intent("provision_dataset") is True
        assert cap.matches_intent("validate_data") is True
        assert cap.matches_intent("unknown_intent") is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        cap = CapabilitySpec(
            agent_id="test-agent",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={"in": "string"},
            output_schema={"out": "string"},
            requires=["capability_a"],
            provides=["capability_b"]
        )

        cap_dict = cap.to_dict()

        assert cap_dict["agent_id"] == "test-agent"
        assert cap_dict["intents"] == ["test"]
        assert cap_dict["requires"] == ["capability_a"]
        assert cap_dict["provides"] == ["capability_b"]


class TestCapabilityRegistry:
    """Test capability registry."""

    def test_register_capability(self):
        """Test registering a capability."""
        registry = CapabilityRegistry()

        cap = CapabilitySpec(
            agent_id="agent-1",
            domain="test",
            version="1.0.0",
            intents=["test_intent"],
            input_schema={},
            output_schema={}
        )

        registry.register(cap)

        retrieved = registry.get_capability("agent-1")
        assert retrieved is not None
        assert retrieved.agent_id == "agent-1"

    def test_unregister_capability(self):
        """Test unregistering a capability."""
        registry = CapabilityRegistry()

        cap = CapabilitySpec(
            agent_id="agent-1",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={},
            output_schema={}
        )

        registry.register(cap)
        result = registry.unregister("agent-1")

        assert result is True
        assert registry.get_capability("agent-1") is None

    def test_find_by_intent(self):
        """Test finding agents by intent."""
        registry = CapabilityRegistry()

        # Register multiple agents with same intent
        for i in range(3):
            cap = CapabilitySpec(
                agent_id=f"agent-{i}",
                domain="test",
                version="1.0.0",
                intents=["provision_dataset"],
                input_schema={},
                output_schema={}
            )
            registry.register(cap)

        # Find agents
        agent_ids = registry.find_by_intent("provision_dataset")

        assert len(agent_ids) == 3
        assert "agent-0" in agent_ids
        assert "agent-1" in agent_ids
        assert "agent-2" in agent_ids

    def test_find_by_domain(self):
        """Test finding agents by domain."""
        registry = CapabilityRegistry()

        # Register agents in different domains
        for domain in ["domain_a", "domain_b"]:
            for i in range(2):
                cap = CapabilitySpec(
                    agent_id=f"{domain}-agent-{i}",
                    domain=domain,
                    version="1.0.0",
                    intents=["test"],
                    input_schema={},
                    output_schema={}
                )
                registry.register(cap)

        # Find agents in domain_a
        agent_ids = registry.find_by_domain("domain_a")

        assert len(agent_ids) == 2
        assert "domain_a-agent-0" in agent_ids
        assert "domain_a-agent-1" in agent_ids

    def test_get_agent_count(self):
        """Test getting agent count."""
        registry = CapabilityRegistry()

        assert registry.get_agent_count() == 0

        # Register agents
        for i in range(5):
            cap = CapabilitySpec(
                agent_id=f"agent-{i}",
                domain="test",
                version="1.0.0",
                intents=["test"],
                input_schema={},
                output_schema={}
            )
            registry.register(cap)

        assert registry.get_agent_count() == 5


class TestCompatibilityMatrix:
    """Test compatibility matrix."""

    def test_set_and_get_compatibility(self):
        """Test storing and retrieving compatibility."""
        matrix = CompatibilityMatrix()

        result = CompatibilityResult(
            compatible=True,
            agent_a="agent-1",
            agent_b="agent-2",
            schema_version="1.0"
        )

        matrix.set_compatibility(result)

        retrieved = matrix.get_compatibility("agent-1", "agent-2")

        assert retrieved is not None
        assert retrieved.compatible is True

    def test_order_independent_key(self):
        """Test that agent order doesn't matter for cache key."""
        matrix = CompatibilityMatrix()

        result = CompatibilityResult(
            compatible=True,
            agent_a="agent-1",
            agent_b="agent-2",
            schema_version="1.0"
        )

        matrix.set_compatibility(result)

        # Retrieve with reversed order
        retrieved = matrix.get_compatibility("agent-2", "agent-1")

        assert retrieved is not None
        assert retrieved.compatible is True

    def test_clear(self):
        """Test clearing the matrix."""
        matrix = CompatibilityMatrix()

        result = CompatibilityResult(
            compatible=True,
            agent_a="agent-1",
            agent_b="agent-2",
            schema_version="1.0"
        )

        matrix.set_compatibility(result)
        matrix.clear()

        retrieved = matrix.get_compatibility("agent-1", "agent-2")
        assert retrieved is None


class TestCapabilityDiscoveryAgent:
    """Test CapabilityDiscoveryAgent functionality."""

    def test_agent_initialization(self):
        """Test discovery agent initialization."""
        discovery = CapabilityDiscoveryAgent()

        assert discovery.registry is not None
        assert discovery.compatibility_matrix is not None

    def test_register_capability(self):
        """Test registering an agent capability."""
        discovery = CapabilityDiscoveryAgent()

        discovery.register_capability(
            agent_id="dataset-provisioning-agent",
            domain="medtronic_poc",
            version="1.0.0",
            intents=["provision_test_dataset"],
            input_schema={"test_scenario_id": "string"},
            output_schema={"connection_string": "string"},
            provides=["dataset_provisioning"]
        )

        capability = discovery.registry.get_capability("dataset-provisioning-agent")

        assert capability is not None
        assert capability.agent_id == "dataset-provisioning-agent"
        assert "provision_test_dataset" in capability.intents

    def test_discover_by_intent(self):
        """Test discovering agents by intent."""
        discovery = CapabilityDiscoveryAgent()

        # Register agents with same intent
        discovery.register_capability(
            agent_id="agent-1",
            domain="domain_a",
            version="1.0.0",
            intents=["provision_dataset", "validate_data"],
            input_schema={},
            output_schema={}
        )

        discovery.register_capability(
            agent_id="agent-2",
            domain="domain_b",
            version="1.0.0",
            intents=["provision_dataset"],
            input_schema={},
            output_schema={}
        )

        # Discover agents
        matches = discovery.discover_by_intent("provision_dataset")

        assert len(matches) == 2
        agent_ids = [m.agent_id for m in matches]
        assert "agent-1" in agent_ids
        assert "agent-2" in agent_ids

    def test_discover_by_capability(self):
        """Test discovering agents by capability name."""
        discovery = CapabilityDiscoveryAgent()

        discovery.register_capability(
            agent_id="agent-1",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={},
            output_schema={},
            provides=["data_validation"]
        )

        discovery.register_capability(
            agent_id="agent-2",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={},
            output_schema={},
            provides=["data_provisioning"]
        )

        # Discover by capability
        matches = discovery.discover_by_capability("data_validation")

        assert len(matches) == 1
        assert matches[0].agent_id == "agent-1"

    def test_discover_by_domain(self):
        """Test discovering agents by domain."""
        discovery = CapabilityDiscoveryAgent()

        # Register agents in different domains
        for domain in ["medtronic_poc", "a_domain"]:
            discovery.register_capability(
                agent_id=f"{domain}-agent",
                domain=domain,
                version="1.0.0",
                intents=["test"],
                input_schema={},
                output_schema={}
            )

        # Discover agents in medtronic_poc
        matches = discovery.discover_by_domain("medtronic_poc")

        assert len(matches) == 1
        assert matches[0].agent_id == "medtronic_poc-agent"
        assert matches[0].domain == "medtronic_poc"

    def test_check_compatibility_compatible(self):
        """Test compatibility check for compatible agents."""
        discovery = CapabilityDiscoveryAgent()

        # Register compatible agents - agent-a's output matches agent-b's input
        discovery.register_capability(
            agent_id="agent-a",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={},  # No input needed
            output_schema={"result": "string", "status": "string"}
        )

        discovery.register_capability(
            agent_id="agent-b",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={"result": "string", "status": "string"},
            output_schema={}  # No output needed for this test
        )

        # Check compatibility - agent-a can provide what agent-b needs
        result = discovery.check_compatibility("agent-a", "agent-b")

        assert result.compatible is True
        assert len(result.issues) == 0

    def test_check_compatibility_incompatible(self):
        """Test compatibility check for incompatible agents."""
        discovery = CapabilityDiscoveryAgent()

        # Register incompatible agents
        discovery.register_capability(
            agent_id="agent-a",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={},
            output_schema={"field_a": "string"}
        )

        discovery.register_capability(
            agent_id="agent-b",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={"field_b": "string", "field_c": "number"},
            output_schema={}
        )

        # Check compatibility
        result = discovery.check_compatibility("agent-a", "agent-b")

        assert result.compatible is False
        assert len(result.issues) > 0

    def test_check_compatibility_caching(self):
        """Test that compatibility checks are cached."""
        discovery = CapabilityDiscoveryAgent()

        # Register agents
        discovery.register_capability(
            agent_id="agent-a",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={},
            output_schema={"result": "string"}
        )

        discovery.register_capability(
            agent_id="agent-b",
            domain="test",
            version="1.0.0",
            intents=["test"],
            input_schema={"result": "string"},
            output_schema={}
        )

        # First check
        result1 = discovery.check_compatibility("agent-a", "agent-b")

        # Second check (should use cache)
        result2 = discovery.check_compatibility("agent-a", "agent-b")

        # Should be same object from cache
        assert result1.last_validated == result2.last_validated

    def test_list_all_agents(self):
        """Test listing all registered agents."""
        discovery = CapabilityDiscoveryAgent()

        # Register multiple agents
        for i in range(3):
            discovery.register_capability(
                agent_id=f"agent-{i}",
                domain="test",
                version="1.0.0",
                intents=["test"],
                input_schema={},
                output_schema={}
            )

        # List all agents
        agents = discovery.list_all_agents()

        assert len(agents) == 3
        agent_ids = [a["agent_id"] for a in agents]
        assert "agent-0" in agent_ids
        assert "agent-1" in agent_ids
        assert "agent-2" in agent_ids

    def test_get_registry_stats(self):
        """Test getting registry statistics."""
        discovery = CapabilityDiscoveryAgent()

        # Register agents across different domains
        discovery.register_capability(
            agent_id="agent-1",
            domain="domain_a",
            version="1.0.0",
            intents=["intent_a", "intent_b"],
            input_schema={},
            output_schema={}
        )

        discovery.register_capability(
            agent_id="agent-2",
            domain="domain_a",
            version="1.0.0",
            intents=["intent_b", "intent_c"],
            input_schema={},
            output_schema={}
        )

        discovery.register_capability(
            agent_id="agent-3",
            domain="domain_b",
            version="1.0.0",
            intents=["intent_c"],
            input_schema={},
            output_schema={}
        )

        # Get stats
        stats = discovery.get_registry_stats()

        assert stats["total_agents"] == 3
        assert stats["domains"] == 2
        assert stats["unique_intents"] == 3
        assert "intent_a" in stats["intents"]
        assert "intent_b" in stats["intents"]
        assert "intent_c" in stats["intents"]
        assert stats["domain_distribution"]["domain_a"] == 2
        assert stats["domain_distribution"]["domain_b"] == 1

    def test_handles_10_plus_agents(self):
        """Test that discovery service handles 10+ registered agents (AC3)."""
        discovery = CapabilityDiscoveryAgent()

        # Register 15 agents
        for i in range(15):
            discovery.register_capability(
                agent_id=f"agent-{i}",
                domain=f"domain-{i % 3}",  # 3 domains
                version="1.0.0",
                intents=[f"intent-{i % 5}"],  # 5 intents
                input_schema={},
                output_schema={}
            )

        stats = discovery.get_registry_stats()

        assert stats["total_agents"] == 15
        assert stats["domains"] == 3
        assert stats["unique_intents"] == 5

        # Test discovery still works
        matches = discovery.discover_by_intent("intent-0")
        assert len(matches) == 3  # agents 0, 5, 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
