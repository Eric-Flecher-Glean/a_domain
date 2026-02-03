#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
A/B Pattern Observability

Enhanced observability specifically for A/B agent collaboration patterns.
Integrates with existing Report Explorer infrastructure.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))


class ABPatternObserver:
    """
    Observability layer for A/B collaboration patterns.

    Captures pattern-specific events and generates timeline data
    compatible with the Report Explorer.
    """

    def __init__(self, session_id: Optional[str] = None, output_dir: str = "observability/reports-output"):
        """
        Initialize A/B pattern observer.

        Args:
            session_id: Unique session identifier
            output_dir: Directory for timeline output
        """
        self.session_id = session_id or f"ab-pattern-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        self.start_time = datetime.utcnow()
        self.events: List[Dict[str, Any]] = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Pattern-specific metrics
        self.metrics = {
            "total_iterations": 0,
            "total_messages": 0,
            "total_refinements": 0,
            "patterns_executed": set()
        }

    def observe(self, event: str, data: Dict[str, Any]) -> None:
        """
        Record an observability event.

        Args:
            event: Event name (e.g., 'workflow_started', 'iteration_complete')
            data: Event data
        """
        timestamp = datetime.utcnow()

        event_record = {
            "timestamp": timestamp.isoformat() + "Z",
            "event": event,
            "session_id": self.session_id,
            **data
        }

        self.events.append(event_record)

        # Update metrics
        self._update_metrics(event, data)

    def _update_metrics(self, event: str, data: Dict[str, Any]) -> None:
        """Update metrics based on event."""
        if event == "workflow_started":
            pattern = data.get("pattern")
            if pattern:
                self.metrics["patterns_executed"].add(pattern)

        elif event == "iteration_complete":
            self.metrics["total_iterations"] += 1

        elif event == "refinement_iteration":
            self.metrics["total_refinements"] += 1

        elif event in ["generate_complete", "validate_complete", "propose_complete", "critique_complete"]:
            self.metrics["total_messages"] += 1

    def generate_timeline_data(self) -> Dict[str, Any]:
        """
        Generate timeline data compatible with Report Explorer.

        Returns:
            Timeline data structure
        """
        end_time = datetime.utcnow()
        total_duration = (end_time - self.start_time).total_seconds() * 1000

        # Build timeline rows from events
        rows = []

        # Group events by workflow
        workflows = {}
        for event in self.events:
            workflow_id = event.get("workflow_id", "default")
            if workflow_id not in workflows:
                workflows[workflow_id] = []
            workflows[workflow_id].append(event)

        # Create rows for each workflow
        for workflow_id, workflow_events in workflows.items():
            # Add workflow start row
            start_event = next((e for e in workflow_events if e["event"] == "workflow_started"), None)
            if start_event:
                rows.append({
                    "id": f"workflow-{workflow_id}",
                    "name": f"🔄 {start_event.get('pattern', 'Pattern')} Workflow",
                    "type": "workflow",
                    "startTime": start_event["timestamp"],
                    "duration": 100,  # Placeholder
                    "status": "success",
                    "attributes": {
                        "pattern": start_event.get("pattern"),
                        "workflow_id": workflow_id
                    }
                })

            # Add iteration rows
            iteration_events = [e for e in workflow_events if e["event"] == "iteration_complete"]
            for i, event in enumerate(iteration_events, 1):
                rows.append({
                    "id": f"{workflow_id}-iteration-{i}",
                    "name": f"  Iteration {i}",
                    "type": "iteration",
                    "startTime": event["timestamp"],
                    "duration": event.get("duration_ms", 50),
                    "status": "success" if event.get("improvement", 0) >= 0 else "warning",
                    "attributes": {
                        "iteration": i,
                        "score": event.get("score", 0.0),
                        "improvement": event.get("improvement", 0.0)
                    }
                })

            # Add agent interaction rows
            agent_events = [
                e for e in workflow_events
                if e["event"] in ["generate_start", "validate_start", "propose_start", "critique_start", "refine_start"]
            ]
            for event in agent_events:
                action = event["event"].replace("_start", "")
                rows.append({
                    "id": f"{workflow_id}-{action}-{event['timestamp']}",
                    "name": f"    → {action.capitalize()}",
                    "type": "agent_action",
                    "startTime": event["timestamp"],
                    "duration": 25,
                    "status": "success",
                    "attributes": {
                        "action": action,
                        **{k: v for k, v in event.items() if k not in ["timestamp", "event", "session_id", "workflow_id", "pattern"]}
                    }
                })

        # Create timeline structure
        timeline_data = {
            "sessionId": self.session_id,
            "startTime": self.start_time.isoformat() + "Z",
            "endTime": end_time.isoformat() + "Z",
            "task": "A/B Pattern Execution",
            "totalDuration": total_duration,
            "status": "success",
            "rows": rows,
            "metadata": {
                "total_events": len(self.events),
                "total_iterations": self.metrics["total_iterations"],
                "total_refinements": self.metrics["total_refinements"],
                "patterns_executed": list(self.metrics["patterns_executed"]),
                "total_workflows": len(workflows)
            }
        }

        return timeline_data

    def save_timeline(self) -> str:
        """
        Save timeline data to JSON file.

        Returns:
            Path to saved file
        """
        timeline_data = self.generate_timeline_data()

        # Save as JSON
        json_path = self.output_dir / f"{self.session_id}-timeline.json"
        with open(json_path, 'w') as f:
            json.dump(timeline_data, f, indent=2)

        print(f"📊 Pattern timeline saved: {json_path}")
        return str(json_path)

    def generate_html_report(self) -> str:
        """
        Generate HTML report for pattern execution.

        Returns:
            Path to HTML file
        """
        timeline_data = self.generate_timeline_data()
        metadata = timeline_data["metadata"]

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Pattern Execution - {self.session_id}</title>
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
            border-left: 4px solid #4CAF50;
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
        .timeline-item.workflow {{
            border-left-color: #2196F3;
            background: #E3F2FD;
        }}
        .timeline-item.iteration {{
            border-left-color: #FF9800;
            background: #FFF3E0;
        }}
        .timeline-item.agent_action {{
            border-left-color: #9C27B0;
            background: #F3E5F5;
            margin-left: 20px;
        }}
        .timeline-item h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 16px;
        }}
        .attributes {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .attr-item {{
            padding: 8px;
            background: white;
            border-radius: 4px;
            font-size: 13px;
        }}
        .attr-label {{
            font-weight: 600;
            color: #666;
            font-size: 11px;
            text-transform: uppercase;
        }}
        .attr-value {{
            color: #333;
            margin-top: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 A/B Pattern Execution Report</h1>
        <div class="meta">
            <p><strong>Session:</strong> {timeline_data['sessionId']}</p>
            <p><strong>Started:</strong> {timeline_data['startTime']}</p>
            <p><strong>Duration:</strong> {timeline_data['totalDuration']:.0f}ms</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{metadata['total_workflows']}</div>
                <div class="stat-label">Workflows Executed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metadata['total_iterations']}</div>
                <div class="stat-label">Total Iterations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metadata['total_refinements']}</div>
                <div class="stat-label">Refinements</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(metadata['patterns_executed'])}</div>
                <div class="stat-label">Patterns Used</div>
            </div>
        </div>

        <h2>Patterns Executed</h2>
        <p>{', '.join(metadata['patterns_executed']) if metadata['patterns_executed'] else 'None'}</p>

        <h2>Timeline</h2>
        <div class="timeline">
"""

        for row in timeline_data['rows']:
            row_class = row['type']
            html_content += f"""
            <div class="timeline-item {row_class}">
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

        print(f"📄 Pattern HTML report saved: {html_path}")
        print(f"🌐 View at: http://localhost:3000/reports/{self.session_id}-timeline.html")

        return str(html_path)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "metrics": {
                **self.metrics,
                "patterns_executed": list(self.metrics["patterns_executed"])
            },
            "duration_ms": (datetime.utcnow() - self.start_time).total_seconds() * 1000
        }


if __name__ == "__main__":
    # Test observability
    print("A/B Pattern Observability")
    print("=" * 60)

    observer = ABPatternObserver()
    print(f"\nSession ID: {observer.session_id}")

    # Simulate pattern execution
    observer.observe("workflow_started", {
        "pattern": "Generate-Validate",
        "workflow_id": "test-workflow-1"
    })

    observer.observe("iteration_complete", {
        "workflow_id": "test-workflow-1",
        "iteration": 1,
        "score": 0.85,
        "improvement": 0.0,
        "duration_ms": 150
    })

    observer.observe("workflow_completed", {
        "workflow_id": "test-workflow-1",
        "reason": "convergence",
        "final_score": 0.92
    })

    # Generate reports
    print("\nGenerating reports...")
    observer.save_timeline()
    observer.generate_html_report()

    # Show summary
    print("\nSummary:")
    summary = observer.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
