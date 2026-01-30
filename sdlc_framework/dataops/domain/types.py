"""Domain type definitions and enums for DataOps."""

from enum import Enum


class DatasetType(str, Enum):
    """Types of datasets that can be managed."""
    CONFLUENCE_PAGES = "confluence_pages"
    GITHUB_REPOS = "github_repos"
    SLACK_MESSAGES = "slack_messages"
    JIRA_ISSUES = "jira_issues"
    CUSTOM = "custom"


class Stage(str, Enum):
    """Client journey stages."""
    SANDBOX = "sandbox"
    PILOT = "pilot"
    PRODUCTION = "production"


class DatasetStatus(str, Enum):
    """Dataset lifecycle states."""
    PROVISIONING = "provisioning"
    VALIDATING = "validating"
    READY = "ready"
    FAILED = "failed"
    TEARDOWN = "teardown"
    ARCHIVED = "archived"


class DataSource(str, Enum):
    """Source of dataset data."""
    MOCK_TEMPLATE = "mock_template"
    SANITIZED_PRODUCTION = "sanitized_production"
    CUSTOM = "custom"


class CheckType(str, Enum):
    """Types of quality checks."""
    SCHEMA_VALIDATION = "schema_validation"
    DATA_COMPLETENESS = "data_completeness"
    CONNECTOR_HEALTH = "connector_health"
    SAMPLE_QUERY_SUCCESS = "sample_query_success"


class CheckStatus(str, Enum):
    """Quality check execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"


class Industry(str, Enum):
    """Industry verticals for template categorization."""
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    ENTERPRISE = "enterprise"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
