"""Transformer for converting mock data to Glean-ingestible format.

This module provides transformations for different data source types
to match Glean's expected data formats.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List

from ..domain.types import DatasetType


class GleanDataTransformer:
    """Transforms mock data into Glean-ingestible format.

    Each data source type has specific format requirements:
    - Confluence: Page ID, title, body, space, author
    - GitHub: Repo name, description, language, stars, issues
    - Slack: Message ID, text, channel, author, timestamp
    - Jira: Issue key, summary, description, status, assignee
    """

    def __init__(self):
        """Initialize the transformer with type-specific handlers."""
        self._transformers: Dict[DatasetType, Callable] = {
            DatasetType.CONFLUENCE_PAGES: self._transform_confluence_page,
            DatasetType.GITHUB_REPOS: self._transform_github_repo,
            DatasetType.SLACK_MESSAGES: self._transform_slack_message,
            DatasetType.JIRA_ISSUES: self._transform_jira_issue,
        }

    async def transform_to_glean_format(
        self,
        records: List[Dict],
        dataset_type: DatasetType
    ) -> List[Dict]:
        """Transform records to Glean format.

        Args:
            records: List of raw record dictionaries.
            dataset_type: Type of dataset to transform.

        Returns:
            List of transformed records in Glean format.

        Raises:
            ValueError: If dataset_type is not supported.
        """
        transformer = self._get_transformer(dataset_type)
        return [transformer(record) for record in records]

    def transform_to_glean_format_sync(
        self,
        records: List[Dict],
        dataset_type: DatasetType
    ) -> List[Dict]:
        """Synchronous version of transform_to_glean_format.

        Args:
            records: List of raw record dictionaries.
            dataset_type: Type of dataset to transform.

        Returns:
            List of transformed records in Glean format.
        """
        transformer = self._get_transformer(dataset_type)
        return [transformer(record) for record in records]

    def _get_transformer(self, dataset_type: DatasetType) -> Callable:
        """Get the appropriate transformer for a dataset type.

        Args:
            dataset_type: Type of dataset.

        Returns:
            Transformer function for the dataset type.

        Raises:
            ValueError: If dataset_type is not supported.
        """
        if dataset_type not in self._transformers:
            raise ValueError(
                f"Unsupported dataset type: {dataset_type}. "
                f"Supported types: {list(self._transformers.keys())}"
            )

        return self._transformers[dataset_type]

    def _transform_confluence_page(self, record: Dict) -> Dict:
        """Transform a Confluence page record to Glean format.

        Args:
            record: Raw Confluence page data.

        Returns:
            Glean-formatted Confluence page.
        """
        return {
            "objectType": "CONFLUENCE_PAGE",
            "documentId": str(record.get("page_id", record.get("id", ""))),
            "title": record.get("title", "Untitled Page"),
            "body": {
                "mimeType": "text/html",
                "textContent": record.get("body", record.get("content", ""))
            },
            "container": record.get("space_key", record.get("space", "DEFAULT")),
            "author": {
                "email": record.get("author_email", record.get("author", "unknown@example.com"))
            },
            "updatedAt": self._normalize_timestamp(
                record.get("last_modified", record.get("updated_at"))
            ),
            "createdAt": self._normalize_timestamp(
                record.get("created_at", record.get("created"))
            ),
            "url": record.get("url", ""),
            "permissions": record.get("permissions", {}),
        }

    def _transform_github_repo(self, record: Dict) -> Dict:
        """Transform a GitHub repository record to Glean format.

        Args:
            record: Raw GitHub repo data.

        Returns:
            Glean-formatted GitHub repository.
        """
        return {
            "objectType": "GITHUB_REPO",
            "documentId": str(record.get("repo_id", record.get("id", ""))),
            "name": record.get("repo_name", record.get("name", "unnamed-repo")),
            "fullName": record.get("full_name", ""),
            "description": record.get("description", ""),
            "language": record.get("primary_language", record.get("language", "")),
            "owner": {
                "login": record.get("owner", record.get("owner_login", "unknown"))
            },
            "isPrivate": record.get("is_private", record.get("private", False)),
            "stars": record.get("stars", record.get("stargazers_count", 0)),
            "forks": record.get("forks", record.get("forks_count", 0)),
            "openIssues": record.get("open_issues", record.get("open_issues_count", 0)),
            "updatedAt": self._normalize_timestamp(
                record.get("last_updated", record.get("updated_at"))
            ),
            "createdAt": self._normalize_timestamp(
                record.get("created_at", record.get("created"))
            ),
            "url": record.get("url", record.get("html_url", "")),
            "topics": record.get("topics", []),
        }

    def _transform_slack_message(self, record: Dict) -> Dict:
        """Transform a Slack message record to Glean format.

        Args:
            record: Raw Slack message data.

        Returns:
            Glean-formatted Slack message.
        """
        return {
            "objectType": "SLACK_MESSAGE",
            "documentId": str(record.get("message_id", record.get("ts", ""))),
            "text": record.get("text", record.get("message", "")),
            "channel": {
                "id": record.get("channel_id", ""),
                "name": record.get("channel_name", record.get("channel", "general"))
            },
            "author": {
                "id": record.get("user_id", record.get("user", "")),
                "email": record.get("user_email", ""),
                "displayName": record.get("user_name", "Unknown User")
            },
            "timestamp": self._normalize_timestamp(
                record.get("timestamp", record.get("ts"))
            ),
            "threadTs": record.get("thread_ts"),
            "reactions": record.get("reactions", []),
            "attachments": record.get("attachments", []),
            "permalink": record.get("permalink", record.get("url", "")),
        }

    def _transform_jira_issue(self, record: Dict) -> Dict:
        """Transform a Jira issue record to Glean format.

        Args:
            record: Raw Jira issue data.

        Returns:
            Glean-formatted Jira issue.
        """
        return {
            "objectType": "JIRA_ISSUE",
            "documentId": record.get("issue_key", record.get("key", "")),
            "key": record.get("issue_key", record.get("key", "")),
            "summary": record.get("summary", record.get("title", "Untitled Issue")),
            "description": record.get("description", ""),
            "issueType": record.get("issue_type", record.get("type", "Task")),
            "status": record.get("status", "Open"),
            "priority": record.get("priority", "Medium"),
            "assignee": {
                "email": record.get("assignee_email", record.get("assignee", ""))
            },
            "reporter": {
                "email": record.get("reporter_email", record.get("reporter", ""))
            },
            "project": {
                "key": record.get("project_key", record.get("project", "")),
                "name": record.get("project_name", "")
            },
            "labels": record.get("labels", []),
            "components": record.get("components", []),
            "updatedAt": self._normalize_timestamp(
                record.get("updated_at", record.get("updated"))
            ),
            "createdAt": self._normalize_timestamp(
                record.get("created_at", record.get("created"))
            ),
            "url": record.get("url", ""),
        }

    def _normalize_timestamp(self, timestamp: Any) -> str:
        """Normalize timestamp to ISO 8601 format.

        Args:
            timestamp: Timestamp in various formats (ISO string, Unix epoch, datetime).

        Returns:
            ISO 8601 formatted timestamp string.
        """
        if timestamp is None:
            # Default to current time if not provided
            return datetime.utcnow().isoformat() + "Z"

        # If already a string, assume it's in correct format
        if isinstance(timestamp, str):
            # Ensure it has timezone indicator
            if not timestamp.endswith('Z') and '+' not in timestamp:
                return timestamp + "Z"
            return timestamp

        # If datetime object, convert to ISO format
        if isinstance(timestamp, datetime):
            return timestamp.isoformat() + "Z"

        # If Unix epoch (int or float), convert to datetime
        if isinstance(timestamp, (int, float)):
            dt = datetime.utcfromtimestamp(timestamp)
            return dt.isoformat() + "Z"

        # Fallback: return current time
        return datetime.utcnow().isoformat() + "Z"

    def validate_transformed_data(
        self,
        records: List[Dict],
        dataset_type: DatasetType
    ) -> tuple[bool, List[str]]:
        """Validate that transformed data meets Glean schema requirements.

        Args:
            records: List of transformed records.
            dataset_type: Type of dataset.

        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []

        for idx, record in enumerate(records):
            # Check objectType is present and matches expected value
            if "objectType" not in record:
                errors.append(f"Record {idx}: Missing 'objectType' field")
                continue

            # Check documentId is present
            if "documentId" not in record:
                errors.append(f"Record {idx}: Missing 'documentId' field")

            # Type-specific validations
            if dataset_type == DatasetType.CONFLUENCE_PAGES:
                if not record.get("title"):
                    errors.append(f"Record {idx}: Confluence page missing 'title'")
                if not record.get("body", {}).get("textContent"):
                    errors.append(f"Record {idx}: Confluence page missing body content")

            elif dataset_type == DatasetType.GITHUB_REPOS:
                if not record.get("name"):
                    errors.append(f"Record {idx}: GitHub repo missing 'name'")

            elif dataset_type == DatasetType.SLACK_MESSAGES:
                if not record.get("text"):
                    errors.append(f"Record {idx}: Slack message missing 'text'")
                if not record.get("channel"):
                    errors.append(f"Record {idx}: Slack message missing 'channel'")

            elif dataset_type == DatasetType.JIRA_ISSUES:
                if not record.get("key"):
                    errors.append(f"Record {idx}: Jira issue missing 'key'")
                if not record.get("summary"):
                    errors.append(f"Record {idx}: Jira issue missing 'summary'")

        return (len(errors) == 0, errors)
