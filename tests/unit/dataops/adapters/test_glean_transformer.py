"""Unit tests for GleanDataTransformer."""

import pytest
from datetime import datetime

from sdlc_framework.dataops.adapters.glean_data_transformer import GleanDataTransformer
from sdlc_framework.dataops.domain.types import DatasetType


class TestGleanDataTransformer:
    """Test suite for GleanDataTransformer."""

    @pytest.fixture
    def transformer(self):
        """Create a GleanDataTransformer instance."""
        return GleanDataTransformer()

    @pytest.fixture
    def sample_confluence_record(self):
        """Sample Confluence page record."""
        return {
            "page_id": "12345",
            "title": "Getting Started Guide",
            "body": "<h1>Welcome</h1><p>This is a test page.</p>",
            "space_key": "ENG",
            "author_email": "john@example.com",
            "last_modified": "2026-01-15T10:00:00Z",
            "created_at": "2026-01-01T08:00:00Z",
            "url": "https://confluence.example.com/pages/12345"
        }

    @pytest.fixture
    def sample_github_record(self):
        """Sample GitHub repository record."""
        return {
            "repo_id": "67890",
            "repo_name": "awesome-project",
            "full_name": "acme/awesome-project",
            "description": "An awesome project",
            "primary_language": "Python",
            "owner": "acme",
            "is_private": False,
            "stars": 150,
            "forks": 25,
            "open_issues": 5,
            "last_updated": "2026-01-20T15:30:00Z",
            "created_at": "2025-06-01T09:00:00Z",
            "url": "https://github.com/acme/awesome-project",
            "topics": ["python", "cli", "automation"]
        }

    @pytest.fixture
    def sample_slack_record(self):
        """Sample Slack message record."""
        return {
            "message_id": "1642512000.123456",
            "text": "Hello team! Great work on the release.",
            "channel_id": "C01234567",
            "channel_name": "engineering",
            "user_id": "U98765432",
            "user_email": "alice@example.com",
            "user_name": "Alice Smith",
            "timestamp": "2026-01-18T14:20:00Z",
            "thread_ts": None,
            "reactions": [{"emoji": "thumbsup", "count": 3}],
            "permalink": "https://slack.com/archives/C01234567/p1642512000123456"
        }

    @pytest.fixture
    def sample_jira_record(self):
        """Sample Jira issue record."""
        return {
            "issue_key": "PROJ-123",
            "summary": "Add user authentication feature",
            "description": "Implement OAuth2 authentication for the API",
            "issue_type": "Story",
            "status": "In Progress",
            "priority": "High",
            "assignee_email": "bob@example.com",
            "reporter_email": "charlie@example.com",
            "project_key": "PROJ",
            "project_name": "Main Project",
            "labels": ["security", "api"],
            "components": ["Backend", "Authentication"],
            "updated_at": "2026-01-22T11:45:00Z",
            "created_at": "2026-01-10T09:30:00Z",
            "url": "https://jira.example.com/browse/PROJ-123"
        }

    def test_transform_confluence_page(self, transformer, sample_confluence_record):
        """Test transforming Confluence page to Glean format."""
        result = transformer._transform_confluence_page(sample_confluence_record)

        assert result["objectType"] == "CONFLUENCE_PAGE"
        assert result["documentId"] == "12345"
        assert result["title"] == "Getting Started Guide"
        assert result["body"]["mimeType"] == "text/html"
        assert result["body"]["textContent"] == "<h1>Welcome</h1><p>This is a test page.</p>"
        assert result["container"] == "ENG"
        assert result["author"]["email"] == "john@example.com"
        assert result["updatedAt"] == "2026-01-15T10:00:00Z"
        assert result["createdAt"] == "2026-01-01T08:00:00Z"
        assert result["url"] == "https://confluence.example.com/pages/12345"

    def test_transform_confluence_page_minimal(self, transformer):
        """Test transforming Confluence page with minimal data."""
        minimal_record = {
            "id": "999",
            "content": "Some content"
        }

        result = transformer._transform_confluence_page(minimal_record)

        assert result["objectType"] == "CONFLUENCE_PAGE"
        assert result["documentId"] == "999"
        assert result["title"] == "Untitled Page"
        assert result["body"]["textContent"] == "Some content"
        assert result["container"] == "DEFAULT"

    def test_transform_github_repo(self, transformer, sample_github_record):
        """Test transforming GitHub repo to Glean format."""
        result = transformer._transform_github_repo(sample_github_record)

        assert result["objectType"] == "GITHUB_REPO"
        assert result["documentId"] == "67890"
        assert result["name"] == "awesome-project"
        assert result["fullName"] == "acme/awesome-project"
        assert result["description"] == "An awesome project"
        assert result["language"] == "Python"
        assert result["owner"]["login"] == "acme"
        assert result["isPrivate"] is False
        assert result["stars"] == 150
        assert result["forks"] == 25
        assert result["openIssues"] == 5
        assert result["topics"] == ["python", "cli", "automation"]

    def test_transform_github_repo_minimal(self, transformer):
        """Test transforming GitHub repo with minimal data."""
        minimal_record = {
            "id": "111",
            "name": "test-repo"
        }

        result = transformer._transform_github_repo(minimal_record)

        assert result["objectType"] == "GITHUB_REPO"
        assert result["documentId"] == "111"
        assert result["name"] == "test-repo"
        assert result["stars"] == 0
        assert result["forks"] == 0

    def test_transform_slack_message(self, transformer, sample_slack_record):
        """Test transforming Slack message to Glean format."""
        result = transformer._transform_slack_message(sample_slack_record)

        assert result["objectType"] == "SLACK_MESSAGE"
        assert result["documentId"] == "1642512000.123456"
        assert result["text"] == "Hello team! Great work on the release."
        assert result["channel"]["id"] == "C01234567"
        assert result["channel"]["name"] == "engineering"
        assert result["author"]["id"] == "U98765432"
        assert result["author"]["email"] == "alice@example.com"
        assert result["author"]["displayName"] == "Alice Smith"
        assert result["timestamp"] == "2026-01-18T14:20:00Z"
        assert result["reactions"] == [{"emoji": "thumbsup", "count": 3}]

    def test_transform_slack_message_minimal(self, transformer):
        """Test transforming Slack message with minimal data."""
        minimal_record = {
            "ts": "1234567890.123",
            "message": "Test message"
        }

        result = transformer._transform_slack_message(minimal_record)

        assert result["objectType"] == "SLACK_MESSAGE"
        assert result["documentId"] == "1234567890.123"
        assert result["text"] == "Test message"
        assert result["channel"]["name"] == "general"

    def test_transform_jira_issue(self, transformer, sample_jira_record):
        """Test transforming Jira issue to Glean format."""
        result = transformer._transform_jira_issue(sample_jira_record)

        assert result["objectType"] == "JIRA_ISSUE"
        assert result["documentId"] == "PROJ-123"
        assert result["key"] == "PROJ-123"
        assert result["summary"] == "Add user authentication feature"
        assert result["description"] == "Implement OAuth2 authentication for the API"
        assert result["issueType"] == "Story"
        assert result["status"] == "In Progress"
        assert result["priority"] == "High"
        assert result["assignee"]["email"] == "bob@example.com"
        assert result["reporter"]["email"] == "charlie@example.com"
        assert result["project"]["key"] == "PROJ"
        assert result["labels"] == ["security", "api"]
        assert result["components"] == ["Backend", "Authentication"]

    def test_transform_jira_issue_minimal(self, transformer):
        """Test transforming Jira issue with minimal data."""
        minimal_record = {
            "key": "TEST-1",
            "title": "Test issue"
        }

        result = transformer._transform_jira_issue(minimal_record)

        assert result["objectType"] == "JIRA_ISSUE"
        assert result["documentId"] == "TEST-1"
        assert result["key"] == "TEST-1"
        assert result["summary"] == "Test issue"

    def test_normalize_timestamp_iso_string(self, transformer):
        """Test normalizing ISO 8601 timestamp string."""
        timestamp = "2026-01-15T10:00:00Z"
        result = transformer._normalize_timestamp(timestamp)
        assert result == "2026-01-15T10:00:00Z"

    def test_normalize_timestamp_iso_string_no_z(self, transformer):
        """Test normalizing ISO string without Z suffix."""
        timestamp = "2026-01-15T10:00:00"
        result = transformer._normalize_timestamp(timestamp)
        assert result == "2026-01-15T10:00:00Z"

    def test_normalize_timestamp_datetime_object(self, transformer):
        """Test normalizing datetime object."""
        dt = datetime(2026, 1, 15, 10, 0, 0)
        result = transformer._normalize_timestamp(dt)
        assert result == "2026-01-15T10:00:00Z"

    def test_normalize_timestamp_unix_epoch(self, transformer):
        """Test normalizing Unix epoch timestamp."""
        timestamp = 1705315200  # 2024-01-15 10:00:00 UTC
        result = transformer._normalize_timestamp(timestamp)
        assert result.endswith("Z")
        assert "2024-01-15" in result

    def test_normalize_timestamp_none(self, transformer):
        """Test normalizing None timestamp returns current time."""
        result = transformer._normalize_timestamp(None)
        assert result.endswith("Z")
        assert "2026" in result  # Should be current year

    def test_transform_to_glean_format_confluence(self, transformer, sample_confluence_record):
        """Test transforming list of Confluence records."""
        records = [sample_confluence_record]
        result = transformer.transform_to_glean_format_sync(records, DatasetType.CONFLUENCE_PAGES)

        assert len(result) == 1
        assert result[0]["objectType"] == "CONFLUENCE_PAGE"
        assert result[0]["title"] == "Getting Started Guide"

    def test_transform_to_glean_format_github(self, transformer, sample_github_record):
        """Test transforming list of GitHub records."""
        records = [sample_github_record]
        result = transformer.transform_to_glean_format_sync(records, DatasetType.GITHUB_REPOS)

        assert len(result) == 1
        assert result[0]["objectType"] == "GITHUB_REPO"
        assert result[0]["name"] == "awesome-project"

    def test_transform_to_glean_format_unsupported_type(self, transformer):
        """Test transforming unsupported dataset type raises error."""
        records = [{"id": "1"}]

        with pytest.raises(ValueError, match="Unsupported dataset type"):
            transformer.transform_to_glean_format_sync(records, DatasetType.CUSTOM)

    def test_validate_transformed_data_valid_confluence(self, transformer, sample_confluence_record):
        """Test validation passes for valid Confluence data."""
        records = [sample_confluence_record]
        transformed = transformer.transform_to_glean_format_sync(records, DatasetType.CONFLUENCE_PAGES)

        is_valid, errors = transformer.validate_transformed_data(transformed, DatasetType.CONFLUENCE_PAGES)

        assert is_valid
        assert errors == []

    def test_validate_transformed_data_missing_object_type(self, transformer):
        """Test validation fails for missing objectType."""
        records = [{"documentId": "123", "title": "Test"}]

        is_valid, errors = transformer.validate_transformed_data(records, DatasetType.CONFLUENCE_PAGES)

        assert not is_valid
        assert len(errors) == 1
        assert "Missing 'objectType'" in errors[0]

    def test_validate_transformed_data_missing_document_id(self, transformer):
        """Test validation fails for missing documentId."""
        records = [{"objectType": "CONFLUENCE_PAGE", "title": "Test"}]

        is_valid, errors = transformer.validate_transformed_data(records, DatasetType.CONFLUENCE_PAGES)

        assert not is_valid
        assert "Missing 'documentId'" in errors[0]

    def test_validate_transformed_data_confluence_missing_title(self, transformer):
        """Test validation fails for Confluence page missing title."""
        records = [{
            "objectType": "CONFLUENCE_PAGE",
            "documentId": "123",
            "body": {"textContent": "Test"}
        }]

        is_valid, errors = transformer.validate_transformed_data(records, DatasetType.CONFLUENCE_PAGES)

        assert not is_valid
        assert "missing 'title'" in errors[0]

    def test_validate_transformed_data_slack_missing_text(self, transformer):
        """Test validation fails for Slack message missing text."""
        records = [{
            "objectType": "SLACK_MESSAGE",
            "documentId": "123",
            "channel": {"id": "C123"}
        }]

        is_valid, errors = transformer.validate_transformed_data(records, DatasetType.SLACK_MESSAGES)

        assert not is_valid
        assert "missing 'text'" in errors[0]

    @pytest.mark.asyncio
    async def test_async_transform_to_glean_format(self, transformer, sample_confluence_record):
        """Test async version of transform_to_glean_format."""
        records = [sample_confluence_record]
        result = await transformer.transform_to_glean_format(records, DatasetType.CONFLUENCE_PAGES)

        assert len(result) == 1
        assert result[0]["objectType"] == "CONFLUENCE_PAGE"
