"""
Glean Gong Connector - Fetches Gong call transcripts via Glean MCP.

This module provides integration with Glean's MCP server to fetch
Gong sales call transcripts and meeting data.
"""

from typing import Dict, List, Optional


class GongConnector:
    """
    Connector to fetch Gong call transcripts via Glean MCP.

    This connector abstracts the Glean MCP meeting_lookup tool to fetch
    Gong call transcripts and metadata for requirements extraction.
    """

    def __init__(self, mcp_client=None):
        """
        Initialize GongConnector.

        Args:
            mcp_client: Optional MCP client instance (for testing/mocking)
        """
        self.mcp_client = mcp_client

    def fetch_recent_calls(
        self, days: int = 7, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Fetch recent Gong calls from Glean.

        Args:
            days: Number of days to look back (default: 7)
            filters: Optional additional filters

        Returns:
            List of call metadata dicts with transcripts
        """
        # In production, this would call:
        # mcp__glean__meeting_lookup(query="type:gong updated:past_week")
        #
        # For now, return placeholder structure that matches expected format
        return [
            {
                "call_id": "gong_abc123",
                "call_title": "Example Discovery Call",
                "call_date": "2026-02-03",
                "transcript": self._get_example_transcript(),
                "participants": [
                    {"name": "John Smith", "role": "CTO", "company": "Acme Corp"},
                    {"name": "Sales Rep", "role": "AE", "company": "Our Company"},
                ],
            }
        ]

    def fetch_call_by_id(self, call_id: str) -> Optional[Dict]:
        """
        Fetch a specific Gong call by ID.

        Args:
            call_id: Gong call ID

        Returns:
            Call metadata dict with transcript, or None if not found
        """
        # In production:
        # mcp__glean__read_document(urls=[f"gong://calls/{call_id}"])
        return None

    def _get_example_transcript(self) -> str:
        """
        Get example transcript for testing.

        This is a placeholder for development/testing. In production,
        transcripts come from Glean MCP.
        """
        return """[00:15:42] John Smith (CTO, Acme Corp): We need to integrate with Salesforce within 2 weeks
[00:16:05] Sales Rep (AE, Our Company): I understand the urgency. Can you tell me more about your current process?
[00:16:20] John Smith (CTO, Acme Corp): We're currently using a manual process and our sales team is losing deals because of delays
[00:16:45] Sales Rep (AE, Our Company): That sounds frustrating. What specific data do you need to sync?
[00:17:10] John Smith (CTO, Acme Corp): We need bi-directional sync of customer records, opportunities, and activity data
[00:17:35] Jane Doe (VP Product, Acme Corp): This is critical for us. We're evaluating three vendors and integration speed is our top criterion"""

    def search_calls_by_topic(
        self, topic: str, limit: int = 10
    ) -> List[Dict]:
        """
        Search Gong calls by topic/keyword.

        Args:
            topic: Search query (e.g., "integration", "salesforce")
            limit: Maximum number of results

        Returns:
            List of matching calls
        """
        # In production:
        # mcp__glean__meeting_lookup(query=f"type:gong {topic}")
        return []

    def get_calls_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[Dict]:
        """
        Get Gong calls within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of calls in date range
        """
        # In production:
        # mcp__glean__meeting_lookup(
        #     query=f"type:gong after:{start_date} before:{end_date}"
        # )
        return []
