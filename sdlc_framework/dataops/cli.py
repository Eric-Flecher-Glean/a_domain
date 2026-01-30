"""CLI tool for DataOps operations."""

import asyncio
import sys
from pathlib import Path

from .agents import DatasetDiscoveryAgent
from .domain.aggregates import DatasetRegistry


async def run_discovery(source_path: str):
    """Run dataset discovery scan."""
    print("=" * 70)
    print("DataOps Discovery Agent")
    print("=" * 70)

    source = Path(source_path)
    if not source.exists():
        print(f"❌ Error: Path does not exist: {source}")
        return 1

    # Create registry
    registry = DatasetRegistry()

    # Create and run discovery agent
    agent = DatasetDiscoveryAgent(registry)
    templates = await agent.execute(source, recursive=True)

    # Print summary
    print("\n" + "=" * 70)
    print("DISCOVERY SUMMARY")
    print("=" * 70)

    summary = agent.get_discovery_summary()
    print(f"\n✅ Total templates discovered: {summary['total_templates']}")
    print(f"📊 Total records across templates: {summary['total_records']}")

    if summary['by_type']:
        print("\n📋 Templates by type:")
        for type_name, count in summary['by_type'].items():
            print(f"  - {type_name}: {count}")

    if summary['by_industry']:
        print("\n🏢 Templates by industry:")
        for industry, count in summary['by_industry'].items():
            print(f"  - {industry}: {count}")

    print("\n" + "=" * 70)
    print("REGISTERED TEMPLATES")
    print("=" * 70)

    for template in templates:
        print(f"\n📄 {template.name}")
        print(f"   Type: {template.dataset_type.value}")
        if template.industry:
            print(f"   Industry: {template.industry.value}")
        if template.use_case:
            print(f"   Use Case: {template.use_case}")
        print(f"   Records: {template.default_record_count}")
        print(f"   Schema fields: {len(template.schema_definition.get('properties', {}))}")
        print(f"   Source: {template.source_path}")

    print("\n" + "=" * 70)
    return 0


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m sdlc_framework.dataops.cli <source_path>")
        print("\nExample:")
        print("  python -m sdlc_framework.dataops.cli /path/to/medtronic_mock_data/templates")
        return 1

    source_path = sys.argv[1]
    return asyncio.run(run_discovery(source_path))


if __name__ == "__main__":
    sys.exit(main())
