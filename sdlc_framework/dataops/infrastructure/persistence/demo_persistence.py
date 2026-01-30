"""Demo script to test persistence layer.

Note: Requires PostgreSQL running with database 'dataops' created.
Run: createdb dataops
"""

import asyncio
from uuid import uuid4
from pathlib import Path

from ...domain.entities import DatasetTemplate
from ...domain.types import DatasetType, Industry
from .database import init_db, get_db_session
from .repositories import TemplateRepository


async def demo():
    """Demonstrate persistence layer functionality."""
    print("=" * 70)
    print("DataOps Persistence Layer Demo")
    print("=" * 70)

    # Initialize database (create tables)
    print("\n1. Initializing database...")
    await init_db()
    print("✅ Database initialized")

    # Create a template
    print("\n2. Creating template...")
    template = DatasetTemplate(
        template_id=uuid4(),
        name="Demo FinTech Confluence Template",
        dataset_type=DatasetType.CONFLUENCE_PAGES,
        industry=Industry.FINTECH,
        use_case="developer_productivity",
        description="Demo template for testing",
        source_path=Path("demo/template.json"),
        schema_definition={
            "type": "object",
            "properties": {
                "page_id": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["page_id", "title"]
        },
        default_record_count=100,
        metadata_template={"sample": "data"}
    )
    print(f"✅ Created template: {template.name}")

    # Save to database
    print("\n3. Saving to database...")
    async with get_db_session() as session:
        repo = TemplateRepository(session)
        saved_template = await repo.save_template(template)
        print(f"✅ Saved template with ID: {saved_template.template_id}")

    # Retrieve from database
    print("\n4. Retrieving from database...")
    async with get_db_session() as session:
        repo = TemplateRepository(session)
        retrieved = await repo.get_by_id(template.template_id)

        if retrieved:
            print(f"✅ Retrieved template: {retrieved.name}")
            print(f"   Type: {retrieved.dataset_type.value}")
            print(f"   Industry: {retrieved.industry.value if retrieved.industry else 'N/A'}")
            print(f"   Records: {retrieved.default_record_count}")
        else:
            print("❌ Template not found")

    # Search by criteria
    print("\n5. Searching by industry...")
    async with get_db_session() as session:
        repo = TemplateRepository(session)
        fintech_templates = await repo.find_by_criteria(industry=Industry.FINTECH)
        print(f"✅ Found {len(fintech_templates)} FinTech template(s)")

    # List all
    print("\n6. Listing all templates...")
    async with get_db_session() as session:
        repo = TemplateRepository(session)
        all_templates = await repo.list_all()
        print(f"✅ Total templates in database: {len(all_templates)}")
        for tmpl in all_templates:
            print(f"   - {tmpl.name} ({tmpl.dataset_type.value})")

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo())
