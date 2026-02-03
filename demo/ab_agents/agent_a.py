#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Agent A (Generator)

Generates content/prompts/tasks and sends them to Agent B for validation.
"""

from typing import Optional, Dict, Any, Callable
from uuid import uuid4
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.a_domain.protocol import ProtocolMessage, Agent, Security


class AgentA:
    """
    Agent A - Content Generator

    Responsibilities:
    - Generate prompts, tasks, or content
    - Send to Agent B for validation
    - Receive feedback and refine
    - Track generation history
    """

    def __init__(self, agent_id: str = "agent-a"):
        """Initialize Agent A."""
        self.agent_id = agent_id
        self.domain = "demo"
        self.version = "1.0.0"

        # Track message history
        self.sent_messages = []
        self.received_messages = []

        # Callback for broker communication
        self.message_handler: Optional[Callable] = None
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
        Handle incoming messages from Agent B.

        Args:
            message: Protocol message from Agent B
        """
        self.received_messages.append(message)

        payload = message.payload
        feedback_type = payload.get("feedback_type", "unknown")

        print(f"[Agent A] Received {feedback_type} from Agent B")
        print(f"[Agent A] Feedback: {payload.get('feedback', 'No feedback')}")

        if feedback_type == "validation_pass":
            print(f"[Agent A] ✓ Content approved!")
        elif feedback_type == "validation_fail":
            print(f"[Agent A] ✗ Content needs refinement")
            suggestions = payload.get("suggestions", [])
            if suggestions:
                print(f"[Agent A] Suggestions: {', '.join(suggestions)}")

    def generate_content(self, content_type: str = "prompt", iteration: int = 1) -> str:
        """
        Generate content to send for validation.

        Args:
            content_type: Type of content to generate
            iteration: Iteration number

        Returns:
            Generated content string
        """
        templates = {
            "prompt": f"Iteration {iteration}: Summarize the key points from this meeting transcript",
            "task": f"Iteration {iteration}: Implement user authentication with OAuth2",
            "content": f"Iteration {iteration}: Draft an email explaining the Q4 roadmap"
        }

        return templates.get(content_type, f"Generated content (iteration {iteration})")

    def send_for_validation(
        self,
        content: str,
        target_agent_id: str = "agent-b",
        contract_id: Optional[str] = None
    ) -> ProtocolMessage:
        """
        Generate and send content to Agent B for validation.

        Args:
            content: Content to validate
            target_agent_id: Target agent ID
            contract_id: Optional contract ID for collaboration

        Returns:
            The sent protocol message
        """
        # Create protocol message
        message = ProtocolMessage(
            source_agent=Agent(
                agent_id=self.agent_id,
                domain=self.domain,
                version=self.version
            ),
            target_agent=Agent(
                agent_id=target_agent_id,
                domain="demo",
                version="1.0.0"
            ),
            message_type="request",
            intent="validate_content",
            payload={
                "content": content,
                "content_type": "prompt",
                "requires_validation": True
            },
            security=Security(auth_token="demo-token")
        )

        # Track sent message
        self.sent_messages.append(message)

        # Send via broker
        if self.send_callback:
            print(f"[Agent A] → Agent B: Sending content for validation")
            print(f"[Agent A] Content: \"{content}\"")
            self.send_callback(message)
        else:
            print("[Agent A] ERROR: Not registered with broker")

        return message

    def get_agent_info(self) -> Agent:
        """Get agent info for protocol messages."""
        return Agent(
            agent_id=self.agent_id,
            domain=self.domain,
            version=self.version
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "agent_id": self.agent_id,
            "sent_messages": len(self.sent_messages),
            "received_messages": len(self.received_messages),
            "last_content": (
                self.sent_messages[-1].payload.get("content")
                if self.sent_messages else None
            )
        }


if __name__ == "__main__":
    # Simple test
    agent = AgentA()
    content = agent.generate_content("prompt", 1)
    print(f"Generated: {content}")
    print(f"Stats: {agent.get_stats()}")
