"""Dataset Discovery Agent

Scans mock data repositories to discover, catalog, and register
dataset templates with inferred schemas and sample data.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import UUID

from ..domain.aggregates import DatasetRegistry
from ..domain.entities import DatasetTemplate
from ..domain.types import DatasetType, Industry
from .base_agent import BaseAgent


class SchemaInferenceEngine:
    """Infers JSON schemas from sample data."""

    @staticmethod
    def infer_field_type(value: Any) -> str:
        """Infer JSON Schema type from Python value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"

    @classmethod
    def infer_schema_from_records(cls, records: List[Dict]) -> Dict:
        """Infer JSON Schema from list of record dictionaries.

        Args:
            records: List of record dictionaries

        Returns:
            JSON Schema definition
        """
        if not records:
            return {"type": "object", "properties": {}}

        # Collect all fields across all records
        all_fields = set()
        for record in records:
            all_fields.update(record.keys())

        # Infer type for each field
        properties = {}
        required = []

        for field in all_fields:
            # Count occurrences and types
            field_types = set()
            non_null_count = 0

            for record in records:
                if field in record and record[field] is not None:
                    field_types.add(cls.infer_field_type(record[field]))
                    non_null_count += 1

            # Determine if required (present in >95% of records)
            if non_null_count / len(records) > 0.95:
                required.append(field)

            # Use most common type, or string if multiple
            if len(field_types) == 1:
                field_type = field_types.pop()
            else:
                field_type = "string"

            properties[field] = {"type": field_type}

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }


class DatasetDiscoveryAgent(BaseAgent):
    """Agent that discovers and catalogs dataset templates.

    Capabilities:
    - Scans mock data template directories
    - Infers JSON schemas from sample records
    - Extracts metadata (industry, use_case) from file paths
    - Catalogs sample data for preview
    - Registers templates in DatasetRegistry
    """

    def __init__(self, registry: DatasetRegistry):
        super().__init__("DatasetDiscoveryAgent")
        self.registry = registry
        self.schema_engine = SchemaInferenceEngine()
        self.discovered_templates: List[DatasetTemplate] = []

    async def execute(
        self,
        source_path: Path,
        recursive: bool = True
    ) -> List[DatasetTemplate]:
        """Execute discovery scan on source path.

        Args:
            source_path: Root path to scan for templates
            recursive: Whether to scan subdirectories

        Returns:
            List of discovered and registered templates
        """
        execution = self.start_execution()
        self.log(f"Starting discovery scan: {source_path}")

        try:
            self.discovered_templates = []

            if not source_path.exists():
                self.log(f"Source path does not exist: {source_path}", "ERROR")
                return []

            # Scan for JSON template files
            pattern = "**/*.json" if recursive else "*.json"
            template_files = list(source_path.glob(pattern))

            self.log(f"Found {len(template_files)} potential template files")

            for template_file in template_files:
                try:
                    template = await self._process_template_file(template_file, source_path)
                    if template:
                        self.discovered_templates.append(template)
                        self.log(f"✅ Registered template: {template.name}")
                except Exception as e:
                    self.log(f"❌ Failed to process {template_file}: {e}", "ERROR")

            self.log(f"Discovery complete: {len(self.discovered_templates)} templates registered")
            return self.discovered_templates

        finally:
            self.end_execution()

    async def _process_template_file(
        self,
        file_path: Path,
        base_path: Path
    ) -> Optional[DatasetTemplate]:
        """Process a single template file.

        Args:
            file_path: Path to template JSON file
            base_path: Base path for relative path calculation

        Returns:
            Registered DatasetTemplate or None if invalid
        """
        self.log(f"Processing: {file_path.relative_to(base_path)}")

        # Load JSON data
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON in {file_path}: {e}", "ERROR")
            return None

        # Extract metadata from file path or JSON
        metadata = self._extract_metadata(file_path, base_path, data)

        # Infer schema from records
        records = self._extract_records(data)
        if not records:
            self.log(f"No records found in {file_path}", "WARN")
            return None

        schema = self.schema_engine.infer_schema_from_records(records)

        # Extract sample data (first 10 records)
        sample_data = records[:10]

        # Create template
        template = DatasetTemplate(
            name=metadata['name'],
            dataset_type=metadata['dataset_type'],
            industry=metadata.get('industry'),
            use_case=metadata.get('use_case'),
            description=metadata.get('description', ''),
            source_path=file_path,
            schema_definition=schema,
            default_record_count=len(records),
            metadata_template={
                'sample_data': sample_data,
                'source_file': str(file_path.relative_to(base_path))
            }
        )

        # Register in registry
        self.registry.register_template(template)

        return template

    def _extract_metadata(
        self,
        file_path: Path,
        base_path: Path,
        data: Dict
    ) -> Dict:
        """Extract metadata from file path and JSON content.

        Expected path structure:
        templates/{industry}/{use_case}/{dataset_type}.json

        Or metadata can be in JSON under "metadata" key.
        """
        metadata = {}

        # Try to extract from JSON first
        if isinstance(data, dict) and 'metadata' in data:
            json_meta = data['metadata']
            metadata['name'] = json_meta.get('name', file_path.stem)
            metadata['industry'] = self._parse_industry(json_meta.get('industry'))
            metadata['use_case'] = json_meta.get('use_case')
            metadata['dataset_type'] = self._parse_dataset_type(
                json_meta.get('dataset_type', json_meta.get('type', file_path.stem))
            )
            metadata['description'] = json_meta.get('description', '')
            return metadata

        # Extract from file path
        relative_path = file_path.relative_to(base_path)
        parts = relative_path.parts

        # Default values
        metadata['dataset_type'] = self._parse_dataset_type(file_path.stem)
        metadata['name'] = file_path.stem.replace('_', ' ').title()

        # Try to parse path structure: templates/industry/use_case/type.json
        if len(parts) >= 3:
            # parts[-3] = industry, parts[-2] = use_case, parts[-1] = filename
            metadata['industry'] = self._parse_industry(parts[-3])
            metadata['use_case'] = parts[-2].replace('_', ' ').replace('-', ' ')

        return metadata

    def _parse_industry(self, industry_str: Optional[str]) -> Optional[Industry]:
        """Parse industry string to Industry enum."""
        if not industry_str:
            return None

        industry_map = {
            'fintech': Industry.FINTECH,
            'finance': Industry.FINTECH,
            'healthcare': Industry.HEALTHCARE,
            'health': Industry.HEALTHCARE,
            'enterprise': Industry.ENTERPRISE,
            'manufacturing': Industry.MANUFACTURING,
            'retail': Industry.RETAIL
        }

        return industry_map.get(industry_str.lower())

    def _parse_dataset_type(self, type_str: str) -> DatasetType:
        """Parse dataset type string to DatasetType enum."""
        type_map = {
            'confluence': DatasetType.CONFLUENCE_PAGES,
            'confluence_pages': DatasetType.CONFLUENCE_PAGES,
            'github': DatasetType.GITHUB_REPOS,
            'github_repos': DatasetType.GITHUB_REPOS,
            'slack': DatasetType.SLACK_MESSAGES,
            'slack_messages': DatasetType.SLACK_MESSAGES,
            'jira': DatasetType.JIRA_ISSUES,
            'jira_issues': DatasetType.JIRA_ISSUES
        }

        return type_map.get(type_str.lower(), DatasetType.CUSTOM)

    def _extract_records(self, data: Any) -> List[Dict]:
        """Extract record list from JSON data.

        Supports multiple formats:
        - {"data": [records]}
        - {"records": [records]}
        - [records]
        - {"metadata": {...}, "data": [records]}
        """
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            # Try common keys
            for key in ['data', 'records', 'items']:
                if key in data and isinstance(data[key], list):
                    return data[key]

        return []

    def get_discovery_summary(self) -> Dict:
        """Get summary of last discovery run."""
        return {
            'total_templates': len(self.discovered_templates),
            'by_type': self._count_by_field('dataset_type'),
            'by_industry': self._count_by_field('industry'),
            'total_records': sum(t.default_record_count for t in self.discovered_templates)
        }

    def _count_by_field(self, field: str) -> Dict:
        """Count templates by field value."""
        counts = {}
        for template in self.discovered_templates:
            value = getattr(template, field)
            key = value.value if hasattr(value, 'value') else str(value) if value else 'None'
            counts[key] = counts.get(key, 0) + 1
        return counts
