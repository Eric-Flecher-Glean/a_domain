"""Unit tests for MockDataAdapter."""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from sdlc_framework.dataops.adapters.mock_data_adapter import (
    MockDataAdapter,
    MockDataAdapterError,
    TemplateNotFoundError,
    TemplateValidationError,
)
from sdlc_framework.dataops.domain.types import DataSource, Stage, Industry


class TestMockDataAdapter:
    """Test suite for MockDataAdapter."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary mock data repository."""
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            templates_path = repo_path / "mock_data" / "templates"
            templates_path.mkdir(parents=True)
            yield repo_path

    @pytest.fixture
    def adapter(self, temp_repo):
        """Create a MockDataAdapter instance."""
        return MockDataAdapter(temp_repo)

    @pytest.fixture
    def sample_template_data(self):
        """Create sample template data."""
        return {
            "metadata": {
                "industry": "fintech",
                "use_case": "developer_productivity",
                "data_type": "mock_template",
                "stage": "sandbox",
                "tags": ["demo", "testing"],
                "custom_fields": {
                    "version": "1.0",
                    "client": "acme-corp"
                }
            },
            "records": [
                {
                    "page_id": "12345",
                    "title": "Getting Started",
                    "body": "<h1>Welcome</h1><p>This is a test page.</p>",
                    "space_key": "ENG",
                    "author_email": "john@example.com",
                    "last_modified": "2026-01-15T10:00:00Z"
                },
                {
                    "page_id": "12346",
                    "title": "API Documentation",
                    "body": "<h1>API Reference</h1>",
                    "space_key": "ENG",
                    "author_email": "jane@example.com",
                    "last_modified": "2026-01-16T14:30:00Z"
                }
            ]
        }

    def create_template_file(self, repo_path, industry, use_case, dataset_type, data):
        """Helper to create a template file."""
        template_dir = repo_path / "mock_data" / "templates" / industry / use_case
        template_dir.mkdir(parents=True, exist_ok=True)

        template_file = template_dir / f"{dataset_type}.json"
        with open(template_file, 'w') as f:
            json.dump(data, f)

        return template_file

    def test_init_with_valid_path(self, temp_repo):
        """Test adapter initialization with valid repository path."""
        adapter = MockDataAdapter(temp_repo)
        assert adapter.repo_path == temp_repo
        assert adapter.templates_path == temp_repo / "mock_data" / "templates"

    def test_init_with_invalid_path(self):
        """Test adapter initialization with invalid path raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            MockDataAdapter(Path("/nonexistent/path"))

    def test_init_with_file_path(self, temp_repo):
        """Test adapter initialization with file instead of directory raises error."""
        file_path = temp_repo / "test_file.txt"
        file_path.touch()

        with pytest.raises(ValueError, match="not a directory"):
            MockDataAdapter(file_path)

    def test_load_template_data_success(self, adapter, temp_repo, sample_template_data):
        """Test successfully loading template data."""
        # Create template file
        self.create_template_file(
            temp_repo,
            "fintech",
            "developer_productivity",
            "confluence_pages",
            sample_template_data
        )

        # Load template
        data = adapter.load_template_data_sync(
            "fintech",
            "developer_productivity",
            "confluence_pages"
        )

        assert data == sample_template_data
        assert len(data["records"]) == 2

    def test_load_template_data_not_found(self, adapter):
        """Test loading non-existent template raises TemplateNotFoundError."""
        with pytest.raises(TemplateNotFoundError):
            adapter.load_template_data_sync(
                "healthcare",
                "patient_portal",
                "confluence_pages"
            )

    def test_load_template_data_invalid_json(self, adapter, temp_repo):
        """Test loading invalid JSON raises TemplateValidationError."""
        # Create invalid JSON file
        template_dir = temp_repo / "mock_data" / "templates" / "fintech" / "test"
        template_dir.mkdir(parents=True, exist_ok=True)

        template_file = template_dir / "confluence_pages.json"
        with open(template_file, 'w') as f:
            f.write("{ invalid json }")

        with pytest.raises(TemplateValidationError, match="Invalid JSON"):
            adapter.load_template_data_sync("fintech", "test", "confluence_pages")

    def test_validate_template_structure_missing_metadata(self, adapter, temp_repo):
        """Test validation fails for template missing metadata."""
        invalid_data = {
            "records": [{"id": "1"}]
        }

        self.create_template_file(
            temp_repo,
            "fintech",
            "test",
            "confluence_pages",
            invalid_data
        )

        with pytest.raises(TemplateValidationError, match="missing required keys"):
            adapter.load_template_data_sync("fintech", "test", "confluence_pages")

    def test_validate_template_structure_missing_records(self, adapter, temp_repo):
        """Test validation fails for template missing records."""
        invalid_data = {
            "metadata": {"industry": "fintech"}
        }

        self.create_template_file(
            temp_repo,
            "fintech",
            "test",
            "confluence_pages",
            invalid_data
        )

        with pytest.raises(TemplateValidationError, match="missing required keys"):
            adapter.load_template_data_sync("fintech", "test", "confluence_pages")

    def test_validate_template_structure_empty_records(self, adapter, temp_repo):
        """Test validation fails for template with empty records list."""
        invalid_data = {
            "metadata": {"industry": "fintech"},
            "records": []
        }

        self.create_template_file(
            temp_repo,
            "fintech",
            "test",
            "confluence_pages",
            invalid_data
        )

        with pytest.raises(TemplateValidationError, match="at least one record"):
            adapter.load_template_data_sync("fintech", "test", "confluence_pages")

    def test_extract_template_metadata(self, adapter, sample_template_data):
        """Test extracting metadata from template data."""
        metadata = adapter.extract_template_metadata_sync(sample_template_data)

        assert metadata.industry == Industry.FINTECH
        assert metadata.use_case == "developer_productivity"
        assert metadata.data_type == DataSource.MOCK_TEMPLATE
        assert metadata.stage == Stage.SANDBOX
        assert metadata.tags == ["demo", "testing"]
        assert metadata.custom_fields["version"] == "1.0"
        assert metadata.custom_fields["client"] == "acme-corp"

    def test_extract_template_metadata_minimal(self, adapter):
        """Test extracting metadata with minimal template data."""
        minimal_data = {
            "metadata": {},
            "records": [{"id": "1"}]
        }

        metadata = adapter.extract_template_metadata_sync(minimal_data)

        assert metadata.industry is None
        assert metadata.use_case is None
        assert metadata.data_type == DataSource.MOCK_TEMPLATE
        assert metadata.stage == Stage.SANDBOX
        assert metadata.tags == []
        assert metadata.custom_fields == {}

    def test_get_records(self, adapter, sample_template_data):
        """Test extracting records from template data."""
        records = adapter.get_records(sample_template_data)

        assert len(records) == 2
        assert records[0]["page_id"] == "12345"
        assert records[1]["page_id"] == "12346"

    def test_get_records_empty(self, adapter):
        """Test extracting records from data with no records."""
        data = {"metadata": {}}
        records = adapter.get_records(data)

        assert records == []

    def test_list_available_templates(self, adapter, temp_repo, sample_template_data):
        """Test listing available templates."""
        # Create multiple templates
        self.create_template_file(
            temp_repo,
            "fintech",
            "developer_productivity",
            "confluence_pages",
            sample_template_data
        )
        self.create_template_file(
            temp_repo,
            "fintech",
            "developer_productivity",
            "github_repos",
            sample_template_data
        )
        self.create_template_file(
            temp_repo,
            "healthcare",
            "patient_portal",
            "confluence_pages",
            sample_template_data
        )

        # List all templates
        templates = adapter.list_available_templates()
        assert len(templates) == 3

        # Filter by industry
        fintech_templates = adapter.list_available_templates(industry="fintech")
        assert len(fintech_templates) == 2
        assert all(t["industry"] == "fintech" for t in fintech_templates)

        # Filter by use case
        dev_prod_templates = adapter.list_available_templates(use_case="developer_productivity")
        assert len(dev_prod_templates) == 2
        assert all(t["use_case"] == "developer_productivity" for t in dev_prod_templates)

    def test_list_available_templates_empty(self, adapter):
        """Test listing templates when none exist."""
        templates = adapter.list_available_templates()
        assert templates == []

    @pytest.mark.asyncio
    async def test_async_load_template_data(self, adapter, temp_repo, sample_template_data):
        """Test async version of load_template_data."""
        self.create_template_file(
            temp_repo,
            "fintech",
            "developer_productivity",
            "confluence_pages",
            sample_template_data
        )

        data = await adapter.load_template_data(
            "fintech",
            "developer_productivity",
            "confluence_pages"
        )

        assert data == sample_template_data

    @pytest.mark.asyncio
    async def test_async_extract_template_metadata(self, adapter, sample_template_data):
        """Test async version of extract_template_metadata."""
        metadata = await adapter.extract_template_metadata(sample_template_data)

        assert metadata.industry == Industry.FINTECH
        assert metadata.use_case == "developer_productivity"
