#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Propose-Critique-Refine Pattern

Iterative improvement loop where one agent proposes, another critiques,
and the first agent refines based on feedback.
"""

from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.a_domain.patterns.base import ABPattern, ABWorkflowContext
from src.a_domain.protocol import ProtocolBrokerAgent


@dataclass
class ProposeCritiqueRefineConfig:
    """Configuration for Propose-Critique-Refine pattern."""
    proposer_id: str = "agent-proposer"
    critic_id: str = "agent-critic"
    improvement_threshold: float = 0.1  # Minimum improvement per iteration
    convergence_threshold: float = 0.9  # Score to consider "good enough"
    max_iterations: int = 5


class ProposeCritiqueRefinePattern(ABPattern):
    """
    Propose-Critique-Refine Pattern

    Flow:
    1. Proposer creates initial proposal
    2. Critic evaluates and provides specific feedback
    3. Proposer refines proposal based on critique
    4. Repeat until convergence or max iterations
    5. Return best proposal

    Roles:
    - Proposer: Creates and refines proposals
    - Critic: Evaluates proposals and provides constructive feedback

    This pattern is ideal for:
    - Iterative design
    - Content improvement
    - Solution optimization
    """

    def __init__(
        self,
        broker: ProtocolBrokerAgent,
        observer: Optional[Callable] = None,
        config: Optional[ProposeCritiqueRefineConfig] = None
    ):
        """Initialize Propose-Critique-Refine pattern."""
        super().__init__(broker, observer)
        self.config = config or ProposeCritiqueRefineConfig()

    @property
    def pattern_name(self) -> str:
        return "Propose-Critique-Refine"

    @property
    def pattern_description(self) -> str:
        return "Iterative improvement through proposal, critique, and refinement cycles"

    @property
    def agent_roles(self) -> List[str]:
        return ["Proposer", "Critic"]

    def execute(
        self,
        input_data: Dict[str, Any],
        max_iterations: int = 5
    ) -> ABWorkflowContext:
        """
        Execute Propose-Critique-Refine workflow.

        Args:
            input_data: Must contain 'goal' or 'requirements'
            max_iterations: Maximum refinement iterations

        Returns:
            Workflow context with best proposal
        """
        # Initialize context
        self.context = ABWorkflowContext(
            input_data=input_data,
            max_iterations=max_iterations
        )

        self._observe("workflow_started", {
            "input_data": input_data,
            "config": {
                "proposer": self.config.proposer_id,
                "critic": self.config.critic_id,
                "convergence_threshold": self.config.convergence_threshold
            }
        })

        start_time = time.time()
        best_proposal = None
        best_score = 0.0
        previous_score = 0.0
        critique_history = []

        # Execution loop
        while self.context.should_continue():
            iteration_start = time.time()

            # Step 1: Propose (or refine)
            if self.context.current_iteration == 0:
                # Initial proposal
                proposal = self._propose(input_data, [])
            else:
                # Refinement based on critique
                proposal = self._refine(
                    input_data,
                    best_proposal,
                    critique_history
                )

            # Step 2: Critique
            critique = self._critique(proposal, input_data)

            # Extract score
            current_score = critique.get("score", 0.0)

            # Track best proposal
            if current_score > best_score:
                best_proposal = proposal
                best_score = current_score

            # Add to critique history
            critique_history.append(critique)

            # Record iteration
            iteration_data = {
                "proposal": proposal,
                "critique": critique,
                "score": current_score,
                "improvement": current_score - previous_score,
                "is_best": current_score == best_score,
                "duration_ms": (time.time() - iteration_start) * 1000
            }
            self.context.record_iteration(iteration_data)

            self._observe("iteration_complete", {
                "iteration": self.context.current_iteration,
                "score": current_score,
                "improvement": current_score - previous_score
            })

            # Check convergence
            if current_score >= self.config.convergence_threshold:
                self.context.is_complete = True
                self._observe("workflow_completed", {
                    "reason": "convergence",
                    "final_score": current_score,
                    "iterations": self.context.current_iteration
                })
                break

            # Check if improvement is stalling
            improvement = current_score - previous_score
            if improvement < self.config.improvement_threshold and self.context.current_iteration > 1:
                self.context.is_complete = True
                self._observe("workflow_completed", {
                    "reason": "diminishing_returns",
                    "final_score": best_score,
                    "iterations": self.context.current_iteration
                })
                break

            previous_score = current_score

        # Set final output
        self.context.final_output = {
            "proposal": best_proposal,
            "score": best_score,
            "iterations": self.context.current_iteration,
            "critique_history": critique_history
        }

        # Finalize
        self.context.total_duration_ms = (time.time() - start_time) * 1000

        return self.context

    def _propose(self, input_data: Dict[str, Any], critique_history: List[Dict]) -> str:
        """
        Create initial proposal.

        Args:
            input_data: Requirements and goals
            critique_history: Previous critiques (empty for initial)

        Returns:
            Proposal string
        """
        goal = input_data.get("goal", input_data.get("requirements", ""))

        self._observe("propose_start", {
            "goal": goal,
            "is_initial": True
        })

        # In real implementation, this calls Proposer agent
        proposal = f"Proposal for: {goal}"

        self._observe("propose_complete", {
            "proposal_length": len(proposal)
        })

        return proposal

    def _refine(
        self,
        input_data: Dict[str, Any],
        previous_proposal: str,
        critique_history: List[Dict]
    ) -> str:
        """
        Refine proposal based on critique.

        Args:
            input_data: Requirements and goals
            previous_proposal: Previous proposal to improve
            critique_history: All previous critiques

        Returns:
            Refined proposal string
        """
        latest_critique = critique_history[-1] if critique_history else {}

        self._observe("refine_start", {
            "previous_score": latest_critique.get("score", 0.0),
            "feedback_count": len(latest_critique.get("feedback", []))
        })

        # In real implementation, this calls Proposer agent with feedback
        feedback_items = latest_critique.get("feedback", [])
        refined = f"{previous_proposal} [Refined based on: {', '.join(feedback_items[:2])}]"

        self._observe("refine_complete", {
            "refined_length": len(refined)
        })

        return refined

    def _critique(self, proposal: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Critique the proposal.

        Args:
            proposal: Proposal to evaluate
            input_data: Requirements for comparison

        Returns:
            Critique with score and feedback
        """
        self._observe("critique_start", {
            "proposal_length": len(proposal)
        })

        # In real implementation, this calls Critic agent
        # Mock scoring based on proposal length/quality
        base_score = min(len(proposal) / 200.0, 0.9)

        # Check for refinement markers
        if "[Refined" in proposal:
            refinement_count = proposal.count("[Refined")
            base_score = min(base_score + (refinement_count * 0.15), 0.95)

        feedback = []
        if base_score < 0.5:
            feedback.append("Proposal needs more detail")
        elif base_score < 0.7:
            feedback.append("Good start, add specific examples")
        elif base_score < 0.9:
            feedback.append("Almost there, refine edge cases")

        critique = {
            "score": base_score,
            "feedback": feedback,
            "strengths": ["Clear structure"] if len(proposal) > 30 else [],
            "weaknesses": feedback
        }

        self._observe("critique_complete", {
            "score": base_score,
            "feedback_count": len(feedback)
        })

        return critique


if __name__ == "__main__":
    # Test Propose-Critique-Refine pattern
    print("Propose-Critique-Refine Pattern")
    print("=" * 60)

    # Create broker (mock for testing)
    broker = ProtocolBrokerAgent()

    # Create pattern
    pattern = ProposeCritiqueRefinePattern(broker)
    print(f"\nPattern: {pattern.pattern_name}")
    print(f"Description: {pattern.pattern_description}")
    print(f"Roles: {', '.join(pattern.agent_roles)}")

    # Execute workflow
    print("\nExecuting workflow...")
    context = pattern.execute(
        input_data={"goal": "Design a user-friendly API for data export"},
        max_iterations=5
    )

    print(f"\nResults:")
    print(f"  Completed: {context.is_complete}")
    print(f"  Iterations: {context.current_iteration}")
    print(f"  Duration: {context.total_duration_ms:.2f}ms")
    print(f"  Best score: {context.final_output['score']:.2f}")
    print(f"  Final proposal: {context.final_output['proposal'][:100]}...")
