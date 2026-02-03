#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Agent B (Validator)

Receives content from Agent A, validates it, and provides feedback.
"""

from typing import Optional, Dict, Any, Callable, List
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.a_domain.protocol import ProtocolMessage, Agent, Security


class AgentB:
    """
    Agent B - Content Validator

    Responsibilities:
    - Receive content from Agent A
    - Validate against quality criteria
    - Provide structured feedback
    - Track validation history
    """

    def __init__(self, agent_id: str = "agent-b"):
        """Initialize Agent B."""
        self.agent_id = agent_id
        self.domain = "demo"
        self.version = "1.0.0"

        # Track message history
        self.received_messages = []
        self.sent_messages = []

        # Validation criteria
        self.min_content_length = 10
        self.required_keywords = ["summarize", "implement", "draft", "analyze"]

        # Callback for broker communication
        self.send_callback: Optional[Callable] = None

    def register_with_broker(self, send_callback: Callable) -> None:
        """
        Register with the protocol broker.

        Args:
            send_callback: Function to send messages through broker
        """
        self.send_callback = send_callback

    def handle_message(self, message: ProtocolMessage) -> None:
        """
        Handle incoming messages from Agent A.

        Args:
            message: Protocol message from Agent A
        """
        self.received_messages.append(message)

        intent = message.intent
        payload = message.payload

        print(f"\n[Agent B] ← Agent A: Received validation request")
        print(f"[Agent B] Intent: {intent}")

        if intent == "validate_content":
            content = payload.get("content", "")
            print(f"[Agent B] Content: \"{content}\"")

            # Validate content
            validation_result = self.validate_content(content)

            # Send response
            self.send_validation_response(message, validation_result)

    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Validate content against quality criteria.

        Args:
            content: Content to validate

        Returns:
            Validation result dictionary
        """
        issues = []
        suggestions = []
        valid = True

        # Check length
        if len(content) < self.min_content_length:
            valid = False
            issues.append("Content too short")
            suggestions.append(f"Expand to at least {self.min_content_length} characters")

        # Check for action keywords
        content_lower = content.lower()
        has_keyword = any(kw in content_lower for kw in self.required_keywords)

        if not has_keyword:
            valid = False
            issues.append("Missing action keyword")
            suggestions.append(f"Include one of: {', '.join(self.required_keywords)}")

        # Check for iteration marker
        if "iteration" in content_lower:
            # Good - shows iterative refinement
            pass

        return {
            "valid": valid,
            "issues": issues,
            "suggestions": suggestions,
            "quality_score": self._calculate_score(content, valid)
        }

    def _calculate_score(self, content: str, valid: bool) -> float:
        """Calculate quality score 0.0 to 1.0."""
        if not valid:
            return 0.6  # Failing but fixable

        # Base score
        score = 0.8

        # Bonus for length
        if len(content) > 50:
            score += 0.1

        # Bonus for specific terms
        if "iteration" in content.lower():
            score += 0.1

        return min(score, 1.0)

    def send_validation_response(
        self,
        request_message: ProtocolMessage,
        validation_result: Dict[str, Any]
    ) -> None:
        """
        Send validation feedback to Agent A.

        Args:
            request_message: Original request message
            validation_result: Validation result
        """
        valid = validation_result["valid"]
        feedback_type = "validation_pass" if valid else "validation_fail"

        # Build feedback message
        feedback = []
        if valid:
            feedback.append(f"✓ Content validated successfully")
            feedback.append(f"Quality score: {validation_result['quality_score']:.2f}")
        else:
            feedback.append(f"✗ Validation failed")
            for issue in validation_result["issues"]:
                feedback.append(f"  - {issue}")

        # Create response message
        response = request_message.create_response(
            payload={
                "feedback_type": feedback_type,
                "valid": valid,
                "quality_score": validation_result["quality_score"],
                "issues": validation_result["issues"],
                "suggestions": validation_result["suggestions"],
                "feedback": "\n".join(feedback)
            },
            message_type="response"
        )

        # Track sent message
        self.sent_messages.append(response)

        # Send via broker
        if self.send_callback:
            print(f"[Agent B] → Agent A: Sending {feedback_type}")
            if valid:
                print(f"[Agent B] ✓ PASS (score: {validation_result['quality_score']:.2f})")
            else:
                print(f"[Agent B] ✗ FAIL")
                for suggestion in validation_result["suggestions"]:
                    print(f"[Agent B]   → {suggestion}")
            self.send_callback(response)
        else:
            print("[Agent B] ERROR: Not registered with broker")

    def get_agent_info(self) -> Agent:
        """Get agent info for protocol messages."""
        return Agent(
            agent_id=self.agent_id,
            domain=self.domain,
            version=self.version
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        validations = len(self.received_messages)
        passed = sum(
            1 for msg in self.sent_messages
            if msg.payload.get("valid", False)
        )

        return {
            "agent_id": self.agent_id,
            "validations_performed": validations,
            "passed": passed,
            "failed": validations - passed,
            "pass_rate": (passed / validations * 100) if validations > 0 else 0
        }


if __name__ == "__main__":
    # Simple test
    agent = AgentB()
    test_content = "Iteration 1: Summarize the key points"
    result = agent.validate_content(test_content)
    print(f"Validation result: {result}")
    print(f"Stats: {agent.get_stats()}")
