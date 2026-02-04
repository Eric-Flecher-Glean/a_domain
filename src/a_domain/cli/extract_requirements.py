#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "click>=8.0",
#   "pyyaml>=6.0",
# ]
# ///
"""
CLI tool for extracting requirements from Gong transcripts.

Usage:
    uv run src/a_domain/cli/extract_requirements.py --help
    uv run src/a_domain/cli/extract_requirements.py demo
    uv run src/a_domain/cli/extract_requirements.py --recent-days=7
"""

import sys
from pathlib import Path

import click

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from a_domain.requirements.extractor import RequirementExtractorAgent
from a_domain.requirements.gong_connector import GongConnector
from a_domain.requirements.output import export_requirements


@click.group()
def cli():
    """Extract requirements from Gong call transcripts."""
    pass


@cli.command()
@click.option(
    "--output-dir",
    default="output/requirements",
    help="Directory for output files",
)
def demo(output_dir):
    """
    Run demo with example transcript.

    This demonstrates the full requirements extraction workflow using
    the built-in example transcript.
    """
    click.echo("🔍 Gong Requirements Extractor - Demo Mode\n")

    # Initialize
    connector = GongConnector()
    agent = RequirementExtractorAgent()

    # Fetch demo call
    click.echo("📞 Fetching demo Gong call...")
    calls = connector.fetch_recent_calls()

    if not calls:
        click.echo("❌ No calls found")
        return

    call = calls[0]
    click.echo(f"   ✅ Loaded: {call['call_title']}\n")

    # Extract requirements
    click.echo("🤖 Extracting requirements...")
    transcript = call["transcript"]
    call_metadata = {
        "call_id": call["call_id"],
        "call_title": call["call_title"],
        "call_date": call["call_date"],
    }

    requirements = agent.extract_from_transcript(transcript, call_metadata)
    click.echo(f"   ✅ Extracted {len(requirements)} requirements\n")

    # Display summary
    click.echo("📊 Summary:")
    click.echo(f"   Total: {len(requirements)}")

    by_type = {}
    for req in requirements:
        req_type = req.requirement_type.value
        by_type[req_type] = by_type.get(req_type, 0) + 1

    for req_type, count in sorted(by_type.items()):
        click.echo(f"   {req_type}: {count}")

    # High priority
    high_priority = [
        req
        for req in requirements
        if any(
            signal.urgency.value in {"high", "critical"}
            for signal in req.priority_signals
        )
    ]
    click.echo(f"   High Priority: {len(high_priority)}")

    # Export
    click.echo(f"\n💾 Exporting to {output_dir}/...")
    output_path = Path(output_dir)
    export_requirements(requirements, output_path)

    click.echo(f"\n✅ Demo complete! Check {output_dir}/ for results")


@cli.command()
@click.option(
    "--days",
    default=7,
    help="Number of days to look back",
)
@click.option(
    "--output-dir",
    default="output/requirements",
    help="Directory for output files",
)
def extract(days, output_dir):
    """
    Extract requirements from recent Gong calls.

    This command fetches Gong calls from the past N days and
    extracts requirements from their transcripts.
    """
    click.echo(f"🔍 Extracting requirements from past {days} days\n")

    # Initialize
    connector = GongConnector()
    agent = RequirementExtractorAgent()

    # Fetch calls
    click.echo("📞 Fetching Gong calls from Glean...")
    calls = connector.fetch_recent_calls(days=days)

    if not calls:
        click.echo("❌ No calls found")
        return

    click.echo(f"   ✅ Found {len(calls)} calls\n")

    # Extract from each call
    all_requirements = []

    for i, call in enumerate(calls, 1):
        click.echo(f"[{i}/{len(calls)}] Processing: {call['call_title']}")

        transcript = call.get("transcript", "")
        if not transcript:
            click.echo("   ⚠️  No transcript available")
            continue

        call_metadata = {
            "call_id": call["call_id"],
            "call_title": call["call_title"],
            "call_date": call["call_date"],
        }

        requirements = agent.extract_from_transcript(transcript, call_metadata)
        all_requirements.extend(requirements)
        click.echo(f"   ✅ Extracted {len(requirements)} requirements")

    # Summary
    click.echo(f"\n📊 Total Requirements: {len(all_requirements)}\n")

    # Export
    if all_requirements:
        click.echo(f"💾 Exporting to {output_dir}/...")
        output_path = Path(output_dir)
        export_requirements(all_requirements, output_path)
        click.echo(f"\n✅ Extraction complete! Check {output_dir}/ for results")
    else:
        click.echo("❌ No requirements extracted")


@cli.command()
@click.argument("transcript_file", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    default="output/requirements",
    help="Directory for output files",
)
def from_file(transcript_file, output_dir):
    """
    Extract requirements from a transcript file.

    The file should contain a Gong-formatted transcript with
    speaker labels and timestamps.
    """
    click.echo(f"🔍 Extracting from file: {transcript_file}\n")

    # Read transcript
    transcript = Path(transcript_file).read_text()

    # Initialize and extract
    agent = RequirementExtractorAgent()
    requirements = agent.extract_from_transcript(transcript)

    click.echo(f"✅ Extracted {len(requirements)} requirements\n")

    # Export
    if requirements:
        output_path = Path(output_dir)
        export_requirements(requirements, output_path)
        click.echo(f"💾 Results saved to {output_dir}/")
    else:
        click.echo("❌ No requirements found")


if __name__ == "__main__":
    cli()
