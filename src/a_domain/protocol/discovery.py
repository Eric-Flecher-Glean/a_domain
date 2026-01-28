"""
Capability Discovery Agent

Implements agent capability registration and discovery.
Based on System Architecture (ARCH-002) and Technical Design (DES-001).
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
import threading
import re


@dataclass
class CapabilitySpec:
    """
    Agent capability specification.

    Defines what an agent can do and how to interact with it.
    """

    agent_id: str
    domain: str
    version: str
    intents: List[str]  # e.g., ["provision_test_dataset", "validate_data"]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    requires: List[str] = field(default_factory=list)  # Required capabilities from other agents
    provides: List[str] = field(default_factory=list)  # Capabilities this agent offers
    description: str = ""
    registered_at: datetime = field(default_factory=datetime.utcnow)

    def matches_intent(self, intent: str) -> bool:
        """Check if this capability matches the given intent."""
        return intent in self.intents

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "version": self.version,
            "intents": self.intents,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "requires": self.requires,
            "provides": self.provides,
            "description": self.description,
            "registered_at": self.registered_at.isoformat()
        }


@dataclass
class AgentMatch:
    """Represents a matched agent from discovery query."""

    agent_id: str
    domain: str
    version: str
    capability: CapabilitySpec
    match_score: float = 1.0  # 0.0 to 1.0, higher is better match

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "version": self.version,
            "match_score": self.match_score,
            "capability": self.capability.to_dict()
        }


@dataclass
class CompatibilityResult:
    """Result of compatibility check between two agents."""

    compatible: bool
    agent_a: str
    agent_b: str
    schema_version: str
    issues: List[str] = field(default_factory=list)
    last_validated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "compatible": self.compatible,
            "agent_a": self.agent_a,
            "agent_b": self.agent_b,
            "schema_version": self.schema_version,
            "issues": self.issues,
            "last_validated": self.last_validated.isoformat()
        }


class CapabilityRegistry:
    """
    Registry for agent capabilities.

    Thread-safe storage and retrieval of capability specifications.
    """

    def __init__(self):
        self.capabilities: Dict[str, CapabilitySpec] = {}  # agent_id -> capability
        self.intent_index: Dict[str, Set[str]] = {}  # intent -> set of agent_ids
        self.domain_index: Dict[str, Set[str]] = {}  # domain -> set of agent_ids
        self._lock = threading.Lock()

    def register(self, capability: CapabilitySpec) -> None:
        """
        Register an agent's capability.

        Args:
            capability: Capability specification
        """
        with self._lock:
            agent_id = capability.agent_id

            # Store capability
            self.capabilities[agent_id] = capability

            # Index by intents
            for intent in capability.intents:
                if intent not in self.intent_index:
                    self.intent_index[intent] = set()
                self.intent_index[intent].add(agent_id)

            # Index by domain
            if capability.domain not in self.domain_index:
                self.domain_index[capability.domain] = set()
            self.domain_index[capability.domain].add(agent_id)

    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent's capability.

        Args:
            agent_id: Agent ID

        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if agent_id not in self.capabilities:
                return False

            capability = self.capabilities[agent_id]

            # Remove from intent index
            for intent in capability.intents:
                if intent in self.intent_index:
                    self.intent_index[intent].discard(agent_id)
                    if not self.intent_index[intent]:
                        del self.intent_index[intent]

            # Remove from domain index
            if capability.domain in self.domain_index:
                self.domain_index[capability.domain].discard(agent_id)
                if not self.domain_index[capability.domain]:
                    del self.domain_index[capability.domain]

            # Remove capability
            del self.capabilities[agent_id]

            return True

    def get_capability(self, agent_id: str) -> Optional[CapabilitySpec]:
        """
        Get capability specification for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Capability specification or None if not found
        """
        with self._lock:
            return self.capabilities.get(agent_id)

    def get_all_capabilities(self) -> List[CapabilitySpec]:
        """Get all registered capabilities."""
        with self._lock:
            return list(self.capabilities.values())

    def find_by_intent(self, intent: str) -> List[str]:
        """
        Find agents that support a specific intent.

        Args:
            intent: Intent to search for

        Returns:
            List of agent IDs
        """
        with self._lock:
            return list(self.intent_index.get(intent, set()))

    def find_by_domain(self, domain: str) -> List[str]:
        """
        Find agents in a specific domain.

        Args:
            domain: Domain to search for

        Returns:
            List of agent IDs
        """
        with self._lock:
            return list(self.domain_index.get(domain, set()))

    def get_agent_count(self) -> int:
        """Get total number of registered agents."""
        with self._lock:
            return len(self.capabilities)


class CompatibilityMatrix:
    """
    Tracks compatibility between agent pairs.

    Caches compatibility checks to avoid redundant validation.
    """

    def __init__(self):
        self.matrix: Dict[str, CompatibilityResult] = {}  # key: "agent_a:agent_b"
        self._lock = threading.Lock()

    def _get_key(self, agent_a: str, agent_b: str) -> str:
        """Generate cache key for agent pair (order-independent)."""
        return f"{min(agent_a, agent_b)}:{max(agent_a, agent_b)}"

    def set_compatibility(self, result: CompatibilityResult) -> None:
        """
        Store compatibility result.

        Args:
            result: Compatibility result
        """
        key = self._get_key(result.agent_a, result.agent_b)
        with self._lock:
            self.matrix[key] = result

    def get_compatibility(self, agent_a: str, agent_b: str) -> Optional[CompatibilityResult]:
        """
        Get cached compatibility result.

        Args:
            agent_a: First agent ID
            agent_b: Second agent ID

        Returns:
            Compatibility result or None if not cached
        """
        key = self._get_key(agent_a, agent_b)
        with self._lock:
            return self.matrix.get(key)

    def clear(self) -> None:
        """Clear all cached compatibility results."""
        with self._lock:
            self.matrix.clear()


class CapabilityDiscoveryAgent:
    """
    Agent capability discovery service.

    Responsibilities:
    - Maintain registry of agent capabilities
    - Support intent-based queries
    - Manage capability versioning
    - Track compatibility matrix
    """

    def __init__(self):
        self.registry = CapabilityRegistry()
        self.compatibility_matrix = CompatibilityMatrix()

    def register_capability(
        self,
        agent_id: str,
        domain: str,
        version: str,
        intents: List[str],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        requires: Optional[List[str]] = None,
        provides: Optional[List[str]] = None,
        description: str = ""
    ) -> None:
        """
        Register an agent's capability.

        Args:
            agent_id: Unique agent identifier
            domain: Agent's domain
            version: Agent version (semantic versioning)
            intents: List of intents this agent supports
            input_schema: Expected input schema
            output_schema: Returned output schema
            requires: Required capabilities from other agents
            provides: Capabilities this agent offers
            description: Human-readable description
        """
        capability = CapabilitySpec(
            agent_id=agent_id,
            domain=domain,
            version=version,
            intents=intents,
            input_schema=input_schema,
            output_schema=output_schema,
            requires=requires or [],
            provides=provides or [],
            description=description
        )

        self.registry.register(capability)

    def unregister_capability(self, agent_id: str) -> bool:
        """
        Unregister an agent's capability.

        Args:
            agent_id: Agent ID

        Returns:
            True if unregistered, False if not found
        """
        return self.registry.unregister(agent_id)

    def discover_by_intent(self, intent: str) -> List[AgentMatch]:
        """
        Discover agents by intent.

        Args:
            intent: Intent to search for (e.g., "provision_test_dataset")

        Returns:
            List of matching agents
        """
        agent_ids = self.registry.find_by_intent(intent)

        matches = []
        for agent_id in agent_ids:
            capability = self.registry.get_capability(agent_id)
            if capability:
                match = AgentMatch(
                    agent_id=agent_id,
                    domain=capability.domain,
                    version=capability.version,
                    capability=capability,
                    match_score=1.0  # Exact intent match
                )
                matches.append(match)

        return matches

    def discover_by_capability(self, capability_name: str) -> List[AgentMatch]:
        """
        Discover agents by capability name.

        Args:
            capability_name: Capability to search for

        Returns:
            List of matching agents
        """
        all_capabilities = self.registry.get_all_capabilities()

        matches = []
        for capability in all_capabilities:
            if capability_name in capability.provides:
                match = AgentMatch(
                    agent_id=capability.agent_id,
                    domain=capability.domain,
                    version=capability.version,
                    capability=capability,
                    match_score=1.0
                )
                matches.append(match)

        return matches

    def discover_by_domain(self, domain: str) -> List[AgentMatch]:
        """
        Discover all agents in a domain.

        Args:
            domain: Domain to search for

        Returns:
            List of matching agents
        """
        agent_ids = self.registry.find_by_domain(domain)

        matches = []
        for agent_id in agent_ids:
            capability = self.registry.get_capability(agent_id)
            if capability:
                match = AgentMatch(
                    agent_id=agent_id,
                    domain=capability.domain,
                    version=capability.version,
                    capability=capability,
                    match_score=1.0
                )
                matches.append(match)

        return matches

    def check_compatibility(
        self,
        agent_a: str,
        agent_b: str,
        force_recheck: bool = False
    ) -> CompatibilityResult:
        """
        Check compatibility between two agents.

        Args:
            agent_a: First agent ID
            agent_b: Second agent ID
            force_recheck: Force recheck even if cached

        Returns:
            Compatibility result
        """
        # Check cache first
        if not force_recheck:
            cached = self.compatibility_matrix.get_compatibility(agent_a, agent_b)
            if cached:
                return cached

        # Get capabilities
        cap_a = self.registry.get_capability(agent_a)
        cap_b = self.registry.get_capability(agent_b)

        if not cap_a or not cap_b:
            result = CompatibilityResult(
                compatible=False,
                agent_a=agent_a,
                agent_b=agent_b,
                schema_version="1.0",
                issues=["One or both agents not registered"]
            )
            return result

        # Check schema compatibility
        issues = []

        # Check if output of A matches input of B
        a_output_keys = set(cap_a.output_schema.keys())
        b_input_keys = set(cap_b.input_schema.keys())

        missing_from_a = b_input_keys - a_output_keys
        if missing_from_a:
            issues.append(f"Agent A missing required output fields: {missing_from_a}")

        # Check if output of B matches input of A (bidirectional)
        b_output_keys = set(cap_b.output_schema.keys())
        a_input_keys = set(cap_a.input_schema.keys())

        missing_from_b = a_input_keys - b_output_keys
        if missing_from_b:
            issues.append(f"Agent B missing required output fields: {missing_from_b}")

        compatible = len(issues) == 0

        result = CompatibilityResult(
            compatible=compatible,
            agent_a=agent_a,
            agent_b=agent_b,
            schema_version="1.0",
            issues=issues
        )

        # Cache result
        self.compatibility_matrix.set_compatibility(result)

        return result

    def get_capability_schema(self, agent_id: str, version: str) -> Optional[CapabilitySpec]:
        """
        Get capability schema for a specific agent version.

        Args:
            agent_id: Agent ID
            version: Version to retrieve

        Returns:
            Capability specification or None if not found
        """
        capability = self.registry.get_capability(agent_id)

        if capability and capability.version == version:
            return capability

        return None

    def list_all_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.

        Returns:
            List of agent summaries
        """
        capabilities = self.registry.get_all_capabilities()

        return [
            {
                "agent_id": cap.agent_id,
                "domain": cap.domain,
                "version": cap.version,
                "intents": cap.intents,
                "registered_at": cap.registered_at.isoformat()
            }
            for cap in capabilities
        ]

    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Statistics dictionary
        """
        capabilities = self.registry.get_all_capabilities()

        # Count by domain
        domain_counts = {}
        for cap in capabilities:
            domain_counts[cap.domain] = domain_counts.get(cap.domain, 0) + 1

        # Count unique intents
        all_intents = set()
        for cap in capabilities:
            all_intents.update(cap.intents)

        return {
            "total_agents": self.registry.get_agent_count(),
            "domains": len(domain_counts),
            "domain_distribution": domain_counts,
            "unique_intents": len(all_intents),
            "intents": sorted(list(all_intents))
        }
