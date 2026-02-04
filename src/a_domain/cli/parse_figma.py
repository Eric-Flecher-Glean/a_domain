#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "click>=8.0",
#   "pyyaml>=6.0",
# ]
# ///
"""
CLI tool for parsing Figma design files.

Usage:
    uv run src/a_domain/cli/parse_figma.py --help
    uv run src/a_domain/cli/parse_figma.py demo
"""

import sys
from pathlib import Path

import click

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from a_domain.requirements.figma_connector import FigmaConnector
from a_domain.requirements.figma_output import export_design_spec
from a_domain.requirements.figma_parser import DesignParserAgent


@click.group()
def cli():
    """Parse Figma design files and extract components."""
    pass


@cli.command()
@click.option(
    "--output-dir",
    default="output/figma",
    help="Directory for output files",
)
def demo(output_dir):
    """
    Run demo with example Figma file.

    This demonstrates the full Figma parsing workflow using
    the built-in example design file.
    """
    click.echo("🎨 Figma Design Parser - Demo Mode\n")

    # Initialize
    connector = FigmaConnector()
    parser = DesignParserAgent()

    # Fetch demo file
    click.echo("📁 Fetching demo Figma file...")
    files = connector.fetch_recent_files()

    if not files:
        click.echo("❌ No files found")
        return

    file = files[0]
    click.echo(f"   ✅ Loaded: {file['file_name']}\n")

    # Parse design
    click.echo("🔍 Parsing design components...")
    file_data = file["file_data"]
    file_metadata = {
        "file_id": file["file_id"],
        "file_name": file["file_name"],
    }

    spec = parser.parse_figma_file(file_data, file_metadata)
    click.echo(f"   ✅ Extracted {len(spec.components)} components\n")

    # Display summary
    click.echo("📊 Summary:")
    click.echo(f"   File: {spec.file_name}")
    click.echo(f"   Total Components: {len(spec.components)}")

    by_type = {}
    for comp in spec.components:
        comp_type = comp.component_type.value
        by_type[comp_type] = by_type.get(comp_type, 0) + 1

    for comp_type, count in sorted(by_type.items()):
        click.echo(f"   {comp_type}: {count}")

    # Show key components
    click.echo(f"\n🔑 Key Components:")
    for i, comp in enumerate(spec.components[:3], 1):
        click.echo(f"   {i}. {comp.name} ({comp.component_type.value})")
        if comp.properties.dimensions.width:
            click.echo(
                f"      Size: {comp.properties.dimensions.width} × {comp.properties.dimensions.height}"
            )
        if comp.user_story_hints:
            click.echo(f"      User story: {comp.user_story_hints[0]}")

    # Export
    click.echo(f"\n💾 Exporting to {output_dir}/...")
    output_path = Path(output_dir)
    export_design_spec(spec, output_path)

    click.echo(f"\n✅ Demo complete! Check {output_dir}/ for results")


@cli.command()
@click.argument("file_id")
@click.option(
    "--output-dir",
    default="output/figma",
    help="Directory for output files",
)
def parse(file_id, output_dir):
    """
    Parse a specific Figma file by ID.

    Example:
        parse abc123xyz
    """
    click.echo(f"🎨 Parsing Figma file: {file_id}\n")

    # Initialize
    connector = FigmaConnector()
    parser = DesignParserAgent()

    # Fetch file
    click.echo("📁 Fetching file from Figma...")
    file_data = connector.fetch_file(file_id)

    if not file_data:
        click.echo(f"❌ File not found: {file_id}")
        return

    click.echo(f"   ✅ File loaded\n")

    # Parse
    click.echo("🔍 Parsing components...")
    file_metadata = {"file_id": file_id, "file_name": f"Figma File {file_id}"}
    spec = parser.parse_figma_file(file_data, file_metadata)

    click.echo(f"✅ Extracted {len(spec.components)} components\n")

    # Export
    if spec.components:
        output_path = Path(output_dir)
        export_design_spec(spec, output_path)
        click.echo(f"💾 Results saved to {output_dir}/")
    else:
        click.echo("⚠️  No components found")


if __name__ == "__main__":
    cli()
