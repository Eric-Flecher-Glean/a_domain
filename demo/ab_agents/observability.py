#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Observability hooks for A/B Agent Demo

Logs agent messages to JSON for visualization in Report Explorer.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.a_domain.protocol import ProtocolMessage


class ABAgentObserver:
    """
    Observability layer for A/B agent collaboration.

    Tracks all messages and generates timeline data for visualization.
    """

    def __init__(self, session_id: Optional[str] = None):
        """Initialize observer."""
        self.session_id = session_id or f"ab-demo-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        self.start_time = datetime.utcnow()
        self.messages: List[Dict[str, Any]] = []

        # Output path for timeline data
        self.output_dir = Path("observability/reports-output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log_message(
        self,
        message: ProtocolMessage,
        direction: str = "sent",  # sent or received
        agent_name: str = "unknown"
    ) -> None:
        """
        Log a protocol message for observability.

        Args:
            message: Protocol message
            direction: Message direction (sent/received)
            agent_name: Name of the agent logging the message
        """
        timestamp = datetime.utcnow()

        message_data = {
            "timestamp": timestamp.isoformat() + "Z",
            "direction": direction,
            "agent_name": agent_name,
            "message_id": message.message_id,
            "source_agent": message.source_agent.agent_id,
            "target_agent": message.target_agent.agent_id,
            "message_type": message.message_type,
            "intent": message.intent,
            "payload_summary": self._summarize_payload(message.payload)
        }

        self.messages.append(message_data)

    def _summarize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the payload for visualization."""
        summary = {}

        # Extract key fields
        if "content" in payload:
            content = payload["content"]
            summary["content_preview"] = content[:50] + "..." if len(content) > 50 else content

        if "feedback_type" in payload:
            summary["feedback_type"] = payload["feedback_type"]

        if "valid" in payload:
            summary["valid"] = payload["valid"]

        if "quality_score" in payload:
            summary["quality_score"] = payload["quality_score"]

        return summary

    def log_interaction_cycle(self, iteration: int, passed: bool, duration_ms: float) -> None:
        """
        Log a complete interaction cycle.

        Args:
            iteration: Iteration number
            passed: Whether validation passed
            duration_ms: Duration in milliseconds
        """
        cycle_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "interaction_cycle",
            "iteration": iteration,
            "passed": passed,
            "duration_ms": duration_ms
        }

        self.messages.append(cycle_data)

    def generate_timeline_json(self) -> Dict[str, Any]:
        """
        Generate timeline data compatible with Report Explorer.

        Returns:
            Timeline data dictionary
        """
        end_time = datetime.utcnow()
        total_duration = (end_time - self.start_time).total_seconds() * 1000

        # Build timeline rows
        rows = []

        for i, msg_data in enumerate(self.messages):
            if msg_data.get("type") == "interaction_cycle":
                # Interaction cycle summary row
                row = {
                    "id": f"cycle-{msg_data['iteration']}",
                    "name": f"Interaction Cycle {msg_data['iteration']}",
                    "type": "stage",
                    "startTime": msg_data["timestamp"],
                    "duration": msg_data["duration_ms"],
                    "status": "success" if msg_data["passed"] else "warning",
                    "attributes": {
                        "iteration": msg_data["iteration"],
                        "validation_result": "PASS" if msg_data["passed"] else "FAIL"
                    }
                }
                rows.append(row)
            else:
                # Message row
                direction_icon = "→" if msg_data["direction"] == "sent" else "←"
                row = {
                    "id": msg_data["message_id"],
                    "name": f"{msg_data['agent_name']} {direction_icon} {msg_data['target_agent' if msg_data['direction'] == 'sent' else 'source_agent']}",
                    "type": "message",
                    "startTime": msg_data["timestamp"],
                    "duration": 50,  # Arbitrary small duration for visualization
                    "status": "success",
                    "attributes": {
                        "message_type": msg_data["message_type"],
                        "intent": msg_data["intent"],
                        "payload": msg_data["payload_summary"]
                    }
                }
                rows.append(row)

        timeline_data = {
            "sessionId": self.session_id,
            "startTime": self.start_time.isoformat() + "Z",
            "endTime": end_time.isoformat() + "Z",
            "task": "A/B Agent Collaboration Demo",
            "totalDuration": total_duration,
            "status": "success",
            "rows": rows,
            "metadata": {
                "total_messages": len([m for m in self.messages if "message_id" in m]),
                "total_cycles": len([m for m in self.messages if m.get("type") == "interaction_cycle"])
            }
        }

        return timeline_data

    def save_timeline(self) -> str:
        """
        Save timeline data to JSON file.

        Returns:
            Path to saved file
        """
        timeline_data = self.generate_timeline_json()

        # Save as JSON
        json_path = self.output_dir / f"{self.session_id}-timeline.json"
        with open(json_path, 'w') as f:
            json.dump(timeline_data, f, indent=2)

        print(f"\n📊 Timeline data saved: {json_path}")
        return str(json_path)

    def generate_html_report(self) -> str:
        """
        Generate simple HTML report for visualization.

        Returns:
            Path to HTML file
        """
        timeline_data = self.generate_timeline_json()

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Agent Demo - {self.session_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-top: 0;
        }}
        .meta {{
            color: #666;
            margin-bottom: 30px;
        }}
        .timeline {{
            margin-top: 20px;
        }}
        .timeline-item {{
            padding: 15px;
            margin-bottom: 10px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }}
        .timeline-item.warning {{
            border-left-color: #FF9800;
        }}
        .timeline-item h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 16px;
        }}
        .attributes {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .attr-item {{
            padding: 8px;
            background: white;
            border-radius: 4px;
            font-size: 14px;
        }}
        .attr-label {{
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .attr-value {{
            color: #333;
            margin-top: 4px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            margin-top: 8px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 A/B Agent Collaboration Demo</h1>
        <div class="meta">
            <p><strong>Session:</strong> {timeline_data['sessionId']}</p>
            <p><strong>Started:</strong> {timeline_data['startTime']}</p>
            <p><strong>Duration:</strong> {timeline_data['totalDuration']:.0f}ms</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{timeline_data['metadata']['total_cycles']}</div>
                <div class="stat-label">Interaction Cycles</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{timeline_data['metadata']['total_messages']}</div>
                <div class="stat-label">Messages Exchanged</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{timeline_data['totalDuration']:.0f}ms</div>
                <div class="stat-label">Total Duration</div>
            </div>
        </div>

        <h2>Timeline</h2>
        <div class="timeline">
"""

        for row in timeline_data['rows']:
            status_class = row['status']
            html_content += f"""
            <div class="timeline-item {status_class}">
                <h3>{row['name']}</h3>
                <div class="attributes">
                    <div class="attr-item">
                        <div class="attr-label">Type</div>
                        <div class="attr-value">{row['type']}</div>
                    </div>
                    <div class="attr-item">
                        <div class="attr-label">Duration</div>
                        <div class="attr-value">{row['duration']:.0f}ms</div>
                    </div>
"""
            for key, value in row.get('attributes', {}).items():
                html_content += f"""
                    <div class="attr-item">
                        <div class="attr-label">{key}</div>
                        <div class="attr-value">{value}</div>
                    </div>
"""
            html_content += """
                </div>
            </div>
"""

        html_content += """
        </div>
    </div>

    <script>
        const TIMELINE_DATA = """ + json.dumps(timeline_data) + """;
        console.log('Timeline data:', TIMELINE_DATA);
    </script>
</body>
</html>
"""

        # Save HTML
        html_path = self.output_dir / f"{self.session_id}-timeline.html"
        with open(html_path, 'w') as f:
            f.write(html_content)

        print(f"📄 HTML report saved: {html_path}")
        print(f"🌐 View at: http://localhost:3000/reports/{self.session_id}-timeline.html")

        return str(html_path)


if __name__ == "__main__":
    # Simple test
    observer = ABAgentObserver()
    print(f"Observer initialized: {observer.session_id}")
    observer.save_timeline()
    observer.generate_html_report()
