#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Generate-Validate Pattern

One agent generates content, another validates it.
This is the pattern demonstrated in P0-AB-001.
"""

from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.a_domain.patterns.base import ABPattern, ABWorkflowContext
from src.a_domain.protocol import ProtocolBrokerAgent, ProtocolMessage, Agent, Security


@dataclass
class GenerateValidateConfig:
    """Configuration for Generate-Validate pattern."""
    generator_id: str = "agent-generator"
    validator_id: str = "agent-validator"
    quality_threshold: float = 0.8
    max_refinement_iterations: int = 3
    auto_refine: bool = True


class GenerateValidatePattern(ABPattern):
    """
    Generate-Validate Pattern

    Flow:
    1. Generator creates content
    2. Validator evaluates content
    3. If validation fails and auto_refine enabled, repeat with feedback
    4. Otherwise, return final result

    Roles:
    - Generator: Creates content based on requirements
    - Validator: Validates content against quality criteria
    """

    def __init__(
        self,
        broker: ProtocolBrokerAgent,
        observer: Optional[Callable] = None,
        config: Optional[GenerateValidateConfig] = None
    ):
        """Initialize Generate-Validate pattern."""
        super().__init__(broker, observer)
        self.config = config or GenerateValidateConfig()

    @property
    def pattern_name(self) -> str:
        return "Generate-Validate"

    @property
    def pattern_description(self) -> str:
        return "One agent generates content, another validates it with optional refinement"

    @property
    def agent_roles(self) -> List[str]:
        return ["Generator", "Validator"]

    def execute(
        self,
        input_data: Dict[str, Any],
        max_iterations: int = 3
    ) -> ABWorkflowContext:
        """
        Execute Generate-Validate workflow.

        Args:
            input_data: Must contain 'task' or 'requirements'
            max_iterations: Maximum refinement iterations

        Returns:
            Workflow context with validated content
        """
        # Initialize context
        self.context = ABWorkflowContext(
            input_data=input_data,
            max_iterations=max_iterations
        )

        self._observe("workflow_started", {
            "input_data": input_data,
            "config": {
                "generator": self.config.generator_id,
                "validator": self.config.validator_id,
                "threshold": self.config.quality_threshold
            }
        })

        start_time = time.time()

        # Execution loop
        while self.context.should_continue():
            iteration_start = time.time()

            # Step 1: Generate content
            generated_content = self._generate(input_data)

            # Step 2: Validate content
            validation_result = self._validate(generated_content)

            # Record iteration
            iteration_data = {
                "generated_content": generated_content,
                "validation_result": validation_result,
                "quality_score": validation_result.get("quality_score", 0.0),
                "valid": validation_result.get("valid", False),
                "duration_ms": (time.time() - iteration_start) * 1000
            }
            self.context.record_iteration(iteration_data)

            # Check if validation passed
            if validation_result.get("valid", False):
                self.context.is_complete = True
                self.context.final_output = {
                    "content": generated_content,
                    "validation": validation_result,
                    "iterations_needed": self.context.current_iteration
                }
                self._observe("workflow_completed", {
                    "iterations": self.context.current_iteration,
                    "success": True
                })
                break

            # Check if we should refine
            if not self.config.auto_refine:
                self.context.is_complete = True
                self.context.final_output = {
                    "content": generated_content,
                    "validation": validation_result,
                    "status": "validation_failed"
                }
                self._observe("workflow_completed", {
                    "iterations": self.context.current_iteration,
                    "success": False,
                    "reason": "validation_failed_no_refinement"
                })
                break

            # Prepare feedback for next iteration
            if self.context.should_continue():
                input_data["feedback"] = validation_result.get("suggestions", [])
                input_data["previous_attempt"] = generated_content
                self._observe("refinement_iteration", {
                    "iteration": self.context.current_iteration,
                    "feedback": validation_result.get("suggestions", [])
                })

        # Finalize
        self.context.total_duration_ms = (time.time() - start_time) * 1000

        return self.context

    def _generate(self, input_data: Dict[str, Any]) -> str:
        """
        Generate content using Generator agent.

        Args:
            input_data: Task requirements and optional feedback

        Returns:
            Generated content string
        """
        task = input_data.get("task", "")
        feedback = input_data.get("feedback", [])
        previous = input_data.get("previous_attempt", None)

        # Build generation prompt
        if previous and feedback:
            content = f"Refined iteration: {task}\nPrevious: {previous}\nFeedback: {', '.join(feedback)}"
        else:
            content = f"Generate: {task}"

        self._observe("generate_start", {
            "task": task,
            "has_feedback": bool(feedback)
        })

        # In a real implementation, this would call the Generator agent
        # For now, we return a mock response
        generated = content

        self._observe("generate_complete", {
            "content_length": len(generated)
        })

        return generated

    def _validate(self, content: str) -> Dict[str, Any]:
        """
        Validate content using Validator agent.

        Args:
            content: Content to validate

        Returns:
            Validation result with quality score and feedback
        """
        self._observe("validate_start", {
            "content_length": len(content)
        })

        # In a real implementation, this would call the Validator agent
        # For now, we return a mock validation
        quality_score = 0.9 if len(content) > 20 else 0.5
        valid = quality_score >= self.config.quality_threshold

        result = {
            "valid": valid,
            "quality_score": quality_score,
            "issues": [] if valid else ["Content too short"],
            "suggestions": [] if valid else ["Add more detail to the generated content"]
        }

        self._observe("validate_complete", {
            "valid": valid,
            "quality_score": quality_score
        })

        return result


if __name__ == "__main__":
    # Test Generate-Validate pattern
    print("Generate-Validate Pattern")
    print("=" * 60)

    # Create broker (mock for testing)
    broker = ProtocolBrokerAgent()

    # Create pattern
    pattern = GenerateValidatePattern(broker)
    print(f"\nPattern: {pattern.pattern_name}")
    print(f"Description: {pattern.pattern_description}")
    print(f"Roles: {', '.join(pattern.agent_roles)}")

    # Execute workflow
    print("\nExecuting workflow...")
    context = pattern.execute(
        input_data={"task": "Summarize the meeting transcript"},
        max_iterations=3
    )

    print(f"\nResults:")
    print(f"  Completed: {context.is_complete}")
    print(f"  Iterations: {context.current_iteration}")
    print(f"  Duration: {context.total_duration_ms:.2f}ms")
    print(f"  Final output: {context.final_output}")
