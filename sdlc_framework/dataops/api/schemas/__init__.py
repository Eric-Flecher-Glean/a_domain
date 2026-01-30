"""Pydantic schemas for API request/response."""

from .dataset_schemas import (
    DatasetResponse,
    DatasetListResponse,
    ConnectorInfo
)
from .template_schemas import (
    TemplateResponse,
    TemplateListResponse,
    TemplateRecommendationRequest,
    TemplateRecommendationsResponse
)

__all__ = [
    "DatasetResponse",
    "DatasetListResponse",
    "ConnectorInfo",
    "TemplateResponse",
    "TemplateListResponse",
    "TemplateRecommendationRequest",
    "TemplateRecommendationsResponse"
]
