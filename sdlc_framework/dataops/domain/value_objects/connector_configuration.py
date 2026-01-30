"""Connector Configuration value object."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class AuthenticationMethod(str, Enum):
    """Connector authentication methods."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    SERVICE_ACCOUNT = "service_account"


@dataclass(frozen=True)
class ConnectorConfiguration:
    """Immutable configuration for Glean data source connectors.

    Contains all settings needed to create and configure a connector
    for a specific dataset type.
    """

    connector_type: str
    endpoint: str
    authentication_method: AuthenticationMethod
    configuration_json: Dict
    rate_limits: Optional[Dict] = None
    sync_schedule: Optional[str] = None  # Cron expression

    def __post_init__(self):
        """Validate configuration on creation."""
        if not self.connector_type:
            raise ValueError("connector_type cannot be empty")

        if not self.endpoint:
            raise ValueError("endpoint cannot be empty")

        if not isinstance(self.configuration_json, dict):
            raise ValueError("configuration_json must be a dictionary")

        # Validate cron if provided
        if self.sync_schedule:
            # Basic validation - real implementation would use croniter
            if not isinstance(self.sync_schedule, str):
                raise ValueError("sync_schedule must be a cron expression string")

    @classmethod
    def for_confluence(
        cls,
        endpoint: str,
        api_key: str,
        sync_schedule: str = "0 */6 * * *"  # Every 6 hours
    ) -> "ConnectorConfiguration":
        """Create configuration for Confluence connector."""
        return cls(
            connector_type="confluence",
            endpoint=endpoint,
            authentication_method=AuthenticationMethod.API_KEY,
            configuration_json={
                "api_key": api_key,
                "spaces": ["*"],  # All spaces
                "include_attachments": True
            },
            rate_limits={"requests_per_minute": 100},
            sync_schedule=sync_schedule
        )

    @classmethod
    def for_github(
        cls,
        endpoint: str,
        token: str,
        sync_schedule: str = "0 */12 * * *"  # Every 12 hours
    ) -> "ConnectorConfiguration":
        """Create configuration for GitHub connector."""
        return cls(
            connector_type="github",
            endpoint=endpoint,
            authentication_method=AuthenticationMethod.OAUTH2,
            configuration_json={
                "access_token": token,
                "include_issues": True,
                "include_pull_requests": True,
                "include_wikis": False
            },
            rate_limits={"requests_per_hour": 5000},
            sync_schedule=sync_schedule
        )

    @classmethod
    def for_slack(
        cls,
        endpoint: str,
        bot_token: str,
        sync_schedule: str = "0 */1 * * *"  # Every hour
    ) -> "ConnectorConfiguration":
        """Create configuration for Slack connector."""
        return cls(
            connector_type="slack",
            endpoint=endpoint,
            authentication_method=AuthenticationMethod.OAUTH2,
            configuration_json={
                "bot_token": bot_token,
                "channels": ["*"],  # All public channels
                "include_private": False,
                "include_dm": False
            },
            rate_limits={"requests_per_minute": 50},
            sync_schedule=sync_schedule
        )
