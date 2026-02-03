"""Adapter for medtronic_mock_data repository.

This module provides integration with the medtronic_mock_data repository,
loading mock data templates and metadata for dataset provisioning.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.types import DatasetType, Industry, DataSource, Stage
from ..domain.value_objects.dataset_metadata import DatasetMetadata


class MockDataAdapterError(Exception):
    """Base exception for mock data adapter errors."""
    pass


class TemplateNotFoundError(MockDataAdapterError):
    """Raised when a template file cannot be found."""
    pass


class TemplateValidationError(MockDataAdapterError):
    """Raised when a template file fails validation."""
    pass


class MockDataAdapter:
    """Adapter for medtronic_mock_data repository.

    Responsibilities:
    - Locate template files by industry/use-case/type
    - Load JSON/CSV files
    - Parse metadata sections
    - Validate data integrity
    """

    def __init__(self, repo_path: Path):
        """Initialize the mock data adapter.

        Args:
            repo_path: Path to the medtronic_mock_data repository root.

        Raises:
            ValueError: If repo_path doesn't exist or isn't a directory.
        """
        if not isinstance(repo_path, Path):
            repo_path = Path(repo_path)

        if not repo_path.exists():
            raise ValueError(f"Mock data repository path does not exist: {repo_path}")

        if not repo_path.is_dir():
            raise ValueError(f"Mock data repository path is not a directory: {repo_path}")

        self.repo_path = repo_path
        self.templates_path = repo_path / "mock_data" / "templates"

        # Create templates directory if it doesn't exist (for testing)
        self.templates_path.mkdir(parents=True, exist_ok=True)

    async def load_template_data(
        self,
        industry: str,
        use_case: str,
        dataset_type: str
    ) -> Dict[str, Any]:
        """Load template data from the repository.

        Args:
            industry: Industry vertical (e.g., "fintech", "healthcare").
            use_case: Specific use case (e.g., "developer_productivity").
            dataset_type: Type of dataset (e.g., "confluence_pages").

        Returns:
            Dictionary containing template data and metadata.

        Raises:
            TemplateNotFoundError: If template file not found.
            TemplateValidationError: If template structure is invalid.
        """
        # Construct file path
        file_path = (
            self.templates_path /
            industry.lower() /
            use_case.lower() /
            f"{dataset_type}.json"
        )

        # Check if file exists
        if not file_path.exists():
            raise TemplateNotFoundError(
                f"Template not found: {file_path}\n"
                f"Looking for: industry={industry}, use_case={use_case}, type={dataset_type}"
            )

        # Load JSON file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise TemplateValidationError(
                f"Invalid JSON in template file {file_path}: {e}"
            )
        except Exception as e:
            raise MockDataAdapterError(
                f"Failed to read template file {file_path}: {e}"
            )

        # Validate structure
        self._validate_template_structure(data, file_path)

        return data

    def load_template_data_sync(
        self,
        industry: str,
        use_case: str,
        dataset_type: str
    ) -> Dict[str, Any]:
        """Synchronous version of load_template_data for non-async contexts.

        Args:
            industry: Industry vertical.
            use_case: Specific use case.
            dataset_type: Type of dataset.

        Returns:
            Dictionary containing template data and metadata.
        """
        # Construct file path
        file_path = (
            self.templates_path /
            industry.lower() /
            use_case.lower() /
            f"{dataset_type}.json"
        )

        # Check if file exists
        if not file_path.exists():
            raise TemplateNotFoundError(
                f"Template not found: {file_path}\n"
                f"Looking for: industry={industry}, use_case={use_case}, type={dataset_type}"
            )

        # Load JSON file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise TemplateValidationError(
                f"Invalid JSON in template file {file_path}: {e}"
            )
        except Exception as e:
            raise MockDataAdapterError(
                f"Failed to read template file {file_path}: {e}"
            )

        # Validate structure
        self._validate_template_structure(data, file_path)

        return data

    def _validate_template_structure(self, data: Dict[str, Any], file_path: Path) -> None:
        """Validate template data structure.

        Args:
            data: Template data to validate.
            file_path: Path to template file (for error messages).

        Raises:
            TemplateValidationError: If template structure is invalid.
        """
        # Check for required top-level keys
        required_keys = ["metadata", "records"]
        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            raise TemplateValidationError(
                f"Template {file_path} missing required keys: {missing_keys}"
            )

        # Validate metadata section
        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict):
            raise TemplateValidationError(
                f"Template {file_path} metadata must be a dictionary"
            )

        # Validate records section
        records = data.get("records", [])
        if not isinstance(records, list):
            raise TemplateValidationError(
                f"Template {file_path} records must be a list"
            )

        if len(records) == 0:
            raise TemplateValidationError(
                f"Template {file_path} must contain at least one record"
            )

    async def extract_template_metadata(
        self,
        template_data: Dict[str, Any]
    ) -> DatasetMetadata:
        """Extract metadata from template data.

        Args:
            template_data: Template data dictionary.

        Returns:
            DatasetMetadata object with extracted values.
        """
        # Parse metadata section from template
        meta = template_data.get("metadata", {})

        # Convert string values to enums
        industry_str = meta.get("industry")
        industry = Industry(industry_str.lower()) if industry_str else None

        data_type_str = meta.get("data_type", "mock_template")
        data_type = DataSource(data_type_str.lower()) if data_type_str else DataSource.MOCK_TEMPLATE

        stage_str = meta.get("stage", "sandbox")
        stage = Stage(stage_str.lower()) if stage_str else Stage.SANDBOX

        return DatasetMetadata(
            industry=industry,
            use_case=meta.get("use_case"),
            data_type=data_type,
            stage=stage,
            tags=meta.get("tags", []),
            custom_fields=meta.get("custom_fields", {})
        )

    def extract_template_metadata_sync(
        self,
        template_data: Dict[str, Any]
    ) -> DatasetMetadata:
        """Synchronous version of extract_template_metadata.

        Args:
            template_data: Template data dictionary.

        Returns:
            DatasetMetadata object with extracted values.
        """
        # Parse metadata section from template
        meta = template_data.get("metadata", {})

        # Convert string values to enums
        industry_str = meta.get("industry")
        industry = Industry(industry_str.lower()) if industry_str else None

        data_type_str = meta.get("data_type", "mock_template")
        data_type = DataSource(data_type_str.lower()) if data_type_str else DataSource.MOCK_TEMPLATE

        stage_str = meta.get("stage", "sandbox")
        stage = Stage(stage_str.lower()) if stage_str else Stage.SANDBOX

        return DatasetMetadata(
            industry=industry,
            use_case=meta.get("use_case"),
            data_type=data_type,
            stage=stage,
            tags=meta.get("tags", []),
            custom_fields=meta.get("custom_fields", {})
        )

    def get_records(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract records from template data.

        Args:
            template_data: Template data dictionary.

        Returns:
            List of record dictionaries.
        """
        return template_data.get("records", [])

    def list_available_templates(
        self,
        industry: Optional[str] = None,
        use_case: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """List available templates in the repository.

        Args:
            industry: Filter by industry (optional).
            use_case: Filter by use case (optional).

        Returns:
            List of dictionaries with template information.
        """
        templates = []

        # Start from industry level or templates root
        search_path = self.templates_path
        if industry:
            search_path = search_path / industry.lower()

        if not search_path.exists():
            return templates

        # Walk directory tree to find JSON files
        for json_file in search_path.rglob("*.json"):
            # Extract path components
            relative_path = json_file.relative_to(self.templates_path)
            parts = relative_path.parts

            if len(parts) >= 3:
                template_industry = parts[0]
                template_use_case = parts[1]
                template_type = json_file.stem

                # Apply filters
                if use_case and template_use_case.lower() != use_case.lower():
                    continue

                templates.append({
                    "industry": template_industry,
                    "use_case": template_use_case,
                    "dataset_type": template_type,
                    "path": str(json_file)
                })

        return templates
