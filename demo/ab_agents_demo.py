#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
A/B Agent Demo Runner

Demonstrates Agent A and Agent B collaborating via Protocol Broker.

Usage:
    python demo/ab_agents_demo.py --iterations=3
    python demo/ab_agents_demo.py --help
"""

import argparse
import sys
import os
import time
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.a_domain.protocol import ProtocolBrokerAgent, ProtocolMessage
from demo.ab_agents.agent_a import AgentA
from demo.ab_agents.agent_b import AgentB
from demo.ab_agents.observability import ABAgentObserver


class ABAgentDemo:
    """
    Orchestrates A/B agent collaboration demo.

    Shows:
    1. Agent registration with broker
    2. Message routing between agents
    3. Generate-validate-refine loop
    4. Real-time observability
    """

    def __init__(self):
        """Initialize demo environment."""
        # Create protocol broker
        self.broker = ProtocolBrokerAgent()

        # Create agents
        self.agent_a = AgentA()
        self.agent_b = AgentB()

        # Create observer for observability
        self.observer = ABAgentObserver()

        # Register agents with broker
        self._register_agents()

    def _register_agents(self) -> None:
        """Register both agents with the protocol broker."""
        # Register Agent A
        self.broker.register_agent(
            agent_id=self.agent_a.agent_id,
            handler=self.agent_a.handle_message
        )

        # Register Agent B
        self.broker.register_agent(
            agent_id=self.agent_b.agent_id,
            handler=self.agent_b.handle_message
        )

        # Give agents the send callback
        self.agent_a.register_with_broker(self._send_via_broker)
        self.agent_b.register_with_broker(self._send_via_broker)

        print("✓ Agents registered with broker")
        print(f"  • {self.agent_a.agent_id} (Generator)")
        print(f"  • {self.agent_b.agent_id} (Validator)")
        print()

    def _send_via_broker(self, message: ProtocolMessage) -> None:
        """
        Send message through protocol broker.

        Args:
            message: Protocol message to route
        """
        # Log message for observability
        agent_name = message.source_agent.agent_id
        self.observer.log_message(message, direction="sent", agent_name=agent_name)

        result = self.broker.route_message(message)
        if not result.valid:
            print(f"ERROR routing message: {result.error_message}")

    def run_interaction_cycle(self, iteration: int = 1) -> bool:
        """
        Run one generate-validate interaction cycle.

        Args:
            iteration: Iteration number

        Returns:
            True if validation passed, False otherwise
        """
        print(f"{'='*60}")
        print(f"Iteration {iteration}: Generate → Validate → Feedback")
        print(f"{'='*60}")

        # Track start time for cycle duration
        cycle_start = time.time()

        # Agent A generates content
        content = self.agent_a.generate_content("prompt", iteration)

        # Agent A sends to Agent B for validation
        self.agent_a.send_for_validation(content, target_agent_id=self.agent_b.agent_id)

        # Give time for message processing (in real system this would be async)
        time.sleep(0.1)

        # Check if validation passed
        passed = False
        if self.agent_a.received_messages:
            last_response = self.agent_a.received_messages[-1]
            passed = last_response.payload.get("valid", False)

        # Log interaction cycle
        cycle_duration = (time.time() - cycle_start) * 1000  # Convert to ms
        self.observer.log_interaction_cycle(iteration, passed, cycle_duration)

        return passed

    def run_demo(self, iterations: int = 3, delay: float = 1.0) -> None:
        """
        Run the full A/B agent demo.

        Args:
            iterations: Number of interaction cycles
            delay: Delay between iterations (seconds)
        """
        print(f"🚀 Starting A/B Agent Demo")
        print(f"   Running {iterations} interaction cycles")
        print()

        passed_count = 0

        for i in range(1, iterations + 1):
            passed = self.run_interaction_cycle(i)
            if passed:
                passed_count += 1

            if i < iterations:
                time.sleep(delay)
                print()

        # Summary
        print()
        print(f"{'='*60}")
        print(f"Demo Summary")
        print(f"{'='*60}")
        print(f"Total Cycles: {iterations}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {iterations - passed_count}")
        print()

        # Agent statistics
        print("Agent A Stats:")
        stats_a = self.agent_a.get_stats()
        for key, value in stats_a.items():
            print(f"  • {key}: {value}")
        print()

        print("Agent B Stats:")
        stats_b = self.agent_b.get_stats()
        for key, value in stats_b.items():
            print(f"  • {key}: {value}")
        print()

        print(f"✓ Demo completed successfully")
        print()

        # Generate observability reports
        print("📊 Generating observability reports...")
        self.observer.save_timeline()
        self.observer.generate_html_report()
        print()
        print("💡 Tip: Run 'make explorer' to view the timeline in Report Explorer")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="A/B Agent Demo - Protocol Broker Proof of Concept"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of interaction cycles to run (default: 3)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between iterations in seconds (default: 1.0)"
    )

    args = parser.parse_args()

    # Run demo
    demo = ABAgentDemo()
    demo.run_demo(iterations=args.iterations, delay=args.delay)


if __name__ == "__main__":
    main()
