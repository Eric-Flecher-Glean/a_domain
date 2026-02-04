"""
Output formatting for extracted requirements.

Provides YAML serialization and formatting utilities for requirements
extracted from Gong transcripts and Figma designs.
"""

from pathlib import Path
from typing import List, Optional

import yaml

from .models import Requirement


class RequirementOutputFormatter:
    """
    Formatter for requirements output.

    Handles YAML serialization and file writing for extracted requirements.
    """

    @staticmethod
    def to_yaml(requirements: List[Requirement], include_metadata: bool = True) -> str:
        """
        Convert requirements to YAML format.

        Args:
            requirements: List of Requirement objects
            include_metadata: Include extraction metadata (default: True)

        Returns:
            YAML string
        """
        output = {
            "requirements": [req.to_dict() for req in requirements],
        }

        if include_metadata:
            output["metadata"] = {
                "total_requirements": len(requirements),
                "source_types": list(
                    set(req.source_type for req in requirements)
                ),
                "requirement_types": list(
                    set(req.requirement_type.value for req in requirements)
                ),
            }

        return yaml.dump(output, default_flow_style=False, sort_keys=False)

    @staticmethod
    def save_to_file(
        requirements: List[Requirement],
        output_path: Path,
        include_metadata: bool = True,
    ) -> None:
        """
        Save requirements to YAML file.

        Args:
            requirements: List of Requirement objects
            output_path: Path to output file
            include_metadata: Include extraction metadata
        """
        yaml_content = RequirementOutputFormatter.to_yaml(
            requirements, include_metadata
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(yaml_content)

    @staticmethod
    def format_summary(requirements: List[Requirement]) -> str:
        """
        Generate human-readable summary of requirements.

        Args:
            requirements: List of Requirement objects

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append(f"📋 Requirements Summary")
        lines.append(f"{'=' * 60}")
        lines.append(f"Total Requirements: {len(requirements)}")
        lines.append("")

        # Group by type
        by_type = {}
        for req in requirements:
            req_type = req.requirement_type.value
            by_type.setdefault(req_type, []).append(req)

        for req_type, reqs in sorted(by_type.items()):
            lines.append(f"{req_type.replace('_', ' ').title()}: {len(reqs)}")

        # High priority requirements
        high_priority = [
            req
            for req in requirements
            if any(
                signal.urgency.value in {"high", "critical"}
                for signal in req.priority_signals
            )
        ]

        if high_priority:
            lines.append("")
            lines.append(f"⚠️  High Priority: {len(high_priority)} requirements")

        # Executive requirements
        exec_requirements = [
            req
            for req in requirements
            if req.speaker
            and req.speaker.role
            and any(
                role in req.speaker.role.lower()
                for role in ["ceo", "cto", "cfo", "vp", "president"]
            )
        ]

        if exec_requirements:
            lines.append(
                f"👔 Executive Requests: {len(exec_requirements)} requirements"
            )

        lines.append("")
        lines.append("Top Requirements:")
        lines.append("-" * 60)

        # Show top 5 by confidence
        sorted_reqs = sorted(requirements, key=lambda r: r.confidence, reverse=True)[:5]

        for i, req in enumerate(sorted_reqs, 1):
            lines.append(f"\n{i}. {req.requirement_text[:80]}...")
            lines.append(f"   Type: {req.requirement_type.value}")
            lines.append(f"   Confidence: {req.confidence:.2f}")
            if req.speaker:
                speaker_info = req.speaker.name
                if req.speaker.role:
                    speaker_info += f" ({req.speaker.role})"
                lines.append(f"   Speaker: {speaker_info}")
            if req.priority_signals:
                urgency = max(
                    (signal.urgency.value for signal in req.priority_signals),
                    default="medium",
                )
                lines.append(f"   Urgency: {urgency}")

        return "\n".join(lines)

    @staticmethod
    def format_for_review(requirements: List[Requirement]) -> str:
        """
        Format requirements for human review.

        Args:
            requirements: List of Requirement objects

        Returns:
            Formatted review output
        """
        lines = []
        lines.append("# Requirements for Review")
        lines.append("")
        lines.append(f"**Total**: {len(requirements)} requirements extracted")
        lines.append("")

        for i, req in enumerate(requirements, 1):
            lines.append(f"## {i}. {req.requirement_text}")
            lines.append("")
            lines.append(f"- **Type**: {req.requirement_type.value}")
            lines.append(f"- **Confidence**: {req.confidence:.2f}")
            lines.append(
                f"- **Source**: {req.source_metadata.call_title or 'Unknown'}"
            )

            if req.speaker:
                speaker_line = f"- **Speaker**: {req.speaker.name}"
                if req.speaker.role:
                    speaker_line += f" ({req.speaker.role})"
                if req.speaker.company:
                    speaker_line += f" @ {req.speaker.company}"
                lines.append(speaker_line)

            if req.priority_signals:
                lines.append("- **Priority Signals**:")
                for signal in req.priority_signals:
                    lines.append(
                        f"  - {signal.type.value}: {signal.value} (urgency: {signal.urgency.value})"
                    )

            if req.categories:
                lines.append(f"- **Categories**: {', '.join(req.categories)}")

            if req.entities:
                lines.append("- **Entities**:")
                for entity_type, values in req.entities.items():
                    lines.append(f"  - {entity_type}: {', '.join(values)}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


def export_requirements(
    requirements: List[Requirement],
    output_dir: Path,
    formats: Optional[List[str]] = None,
) -> None:
    """
    Export requirements to multiple formats.

    Args:
        requirements: List of requirements to export
        output_dir: Directory for output files
        formats: List of format names (yaml, summary, review)
    """
    if formats is None:
        formats = ["yaml", "summary", "review"]

    output_dir.mkdir(parents=True, exist_ok=True)
    formatter = RequirementOutputFormatter()

    if "yaml" in formats:
        yaml_path = output_dir / "requirements.yaml"
        formatter.save_to_file(requirements, yaml_path)
        print(f"✅ Exported YAML: {yaml_path}")

    if "summary" in formats:
        summary_path = output_dir / "requirements-summary.txt"
        summary = formatter.format_summary(requirements)
        summary_path.write_text(summary)
        print(f"✅ Exported summary: {summary_path}")

    if "review" in formats:
        review_path = output_dir / "requirements-review.md"
        review = formatter.format_for_review(requirements)
        review_path.write_text(review)
        print(f"✅ Exported review: {review_path}")
