"""
Output formatting for Figma design specifications.

Provides YAML/JSON serialization and formatting utilities for design specs
extracted from Figma files.
"""

from pathlib import Path
from typing import List, Optional

import yaml

from .figma_models import DesignComponent, DesignSpec


class FigmaOutputFormatter:
    """
    Formatter for Figma design specifications.

    Handles YAML/JSON serialization and file writing for extracted
    design components and technical specifications.
    """

    @staticmethod
    def to_yaml(spec: DesignSpec, include_metadata: bool = True) -> str:
        """
        Convert design spec to YAML format.

        Args:
            spec: DesignSpec object
            include_metadata: Include generation metadata (default: True)

        Returns:
            YAML string
        """
        output = {
            "design_spec": {
                "file_id": spec.file_id,
                "file_name": spec.file_name,
                "components": [comp.to_dict() for comp in spec.components],
                "design_tokens": {
                    "color_palette": spec.color_palette,
                    "typography_scale": spec.typography_scale,
                    "spacing_scale": spec.spacing_scale,
                },
                "user_flows": spec.user_flows,
            }
        }

        if include_metadata:
            output["metadata"] = {
                "total_components": len(spec.components),
                "component_types": list(
                    set(comp.component_type.value for comp in spec.components)
                ),
                "generated_at": spec.generated_at.isoformat(),
            }

        return yaml.dump(output, default_flow_style=False, sort_keys=False)

    @staticmethod
    def save_to_file(
        spec: DesignSpec,
        output_path: Path,
        include_metadata: bool = True,
    ) -> None:
        """
        Save design spec to YAML file.

        Args:
            spec: DesignSpec object
            output_path: Path to output file
            include_metadata: Include generation metadata
        """
        yaml_content = FigmaOutputFormatter.to_yaml(spec, include_metadata)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(yaml_content)

    @staticmethod
    def format_summary(spec: DesignSpec) -> str:
        """
        Generate human-readable summary of design spec.

        Args:
            spec: DesignSpec object

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append(f"🎨 Figma Design Specification")
        lines.append(f"{'=' * 60}")
        lines.append(f"File: {spec.file_name} ({spec.file_id})")
        lines.append(f"Total Components: {len(spec.components)}")
        lines.append("")

        # Group by type
        by_type = {}
        for comp in spec.components:
            comp_type = comp.component_type.value
            by_type.setdefault(comp_type, []).append(comp)

        lines.append("Components by Type:")
        for comp_type, comps in sorted(by_type.items()):
            lines.append(f"  {comp_type}: {len(comps)}")

        # Key components
        lines.append("")
        lines.append("Key Components:")
        lines.append("-" * 60)

        for i, comp in enumerate(spec.components[:5], 1):
            lines.append(f"\n{i}. {comp.name}")
            lines.append(f"   Type: {comp.component_type.value}")
            lines.append(f"   ID: {comp.id} (Node: {comp.figma_node_id})")

            if comp.properties.dimensions.width:
                lines.append(
                    f"   Size: {comp.properties.dimensions.width} × {comp.properties.dimensions.height}"
                )

            if comp.properties.colors.background:
                lines.append(f"   Background: {comp.properties.colors.background}")

            if comp.properties.variants:
                lines.append(f"   Variants: {', '.join(comp.properties.variants)}")

            if comp.annotations:
                lines.append(f"   Annotations: {len(comp.annotations)}")

        # Design tokens
        if spec.color_palette or spec.typography_scale or spec.spacing_scale:
            lines.append("")
            lines.append("Design Tokens:")
            lines.append("-" * 60)

            if spec.color_palette:
                lines.append(f"  Colors: {len(spec.color_palette)} defined")

            if spec.typography_scale:
                lines.append(f"  Typography: {len(spec.typography_scale)} scales")

            if spec.spacing_scale:
                lines.append(f"  Spacing: {len(spec.spacing_scale)} values")

        return "\n".join(lines)

    @staticmethod
    def format_technical_spec(spec: DesignSpec) -> str:
        """
        Format design spec as technical specification document.

        Args:
            spec: DesignSpec object

        Returns:
            Formatted technical specification (Markdown)
        """
        lines = []
        lines.append(f"# Technical Design Specification")
        lines.append(f"## {spec.file_name}")
        lines.append("")
        lines.append(f"**File ID**: `{spec.file_id}`")
        lines.append(f"**Generated**: {spec.generated_at.isoformat()}")
        lines.append(f"**Components**: {len(spec.components)}")
        lines.append("")

        # Components section
        lines.append("## Components")
        lines.append("")

        for comp in spec.components:
            lines.append(f"### {comp.name}")
            lines.append("")
            lines.append(f"- **Type**: {comp.component_type.value}")
            lines.append(f"- **ID**: {comp.id}")
            lines.append(f"- **Figma Node**: `{comp.figma_node_id}`")

            # Properties
            if comp.properties.dimensions.width:
                lines.append(
                    f"- **Dimensions**: {comp.properties.dimensions.width} × {comp.properties.dimensions.height}"
                )

            if comp.properties.colors.background:
                lines.append(
                    f"- **Background Color**: `{comp.properties.colors.background}`"
                )
                if comp.properties.colors.text:
                    lines.append(
                        f"- **Text Color**: `{comp.properties.colors.text}`"
                    )

            if comp.properties.typography.font:
                typo = comp.properties.typography
                lines.append(
                    f"- **Typography**: {typo.font} {typo.size} / weight {typo.weight}"
                )

            if comp.properties.variants:
                lines.append(f"- **Variants**: {', '.join(comp.properties.variants)}")

            # Annotations
            if comp.annotations:
                lines.append("")
                lines.append("**Design Notes**:")
                for ann in comp.annotations:
                    author_str = f" ({ann.author})" if ann.author else ""
                    lines.append(f"- {ann.text}{author_str}")

            # User story hints
            if comp.user_story_hints:
                lines.append("")
                lines.append("**User Story Hints**:")
                for hint in comp.user_story_hints:
                    lines.append(f"- {hint}")

            # Implementation notes
            if comp.implementation_notes:
                lines.append("")
                lines.append("**Implementation Notes**:")
                for note in comp.implementation_notes:
                    lines.append(f"- {note}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


def export_design_spec(
    spec: DesignSpec,
    output_dir: Path,
    formats: Optional[List[str]] = None,
) -> None:
    """
    Export design spec to multiple formats.

    Args:
        spec: DesignSpec to export
        output_dir: Directory for output files
        formats: List of format names (yaml, summary, technical)
    """
    if formats is None:
        formats = ["yaml", "summary", "technical"]

    output_dir.mkdir(parents=True, exist_ok=True)
    formatter = FigmaOutputFormatter()

    if "yaml" in formats:
        yaml_path = output_dir / "design-spec.yaml"
        formatter.save_to_file(spec, yaml_path)
        print(f"✅ Exported YAML: {yaml_path}")

    if "summary" in formats:
        summary_path = output_dir / "design-summary.txt"
        summary = formatter.format_summary(spec)
        summary_path.write_text(summary)
        print(f"✅ Exported summary: {summary_path}")

    if "technical" in formats:
        tech_path = output_dir / "technical-spec.md"
        tech_spec = formatter.format_technical_spec(spec)
        tech_path.write_text(tech_spec)
        print(f"✅ Exported technical spec: {tech_path}")
