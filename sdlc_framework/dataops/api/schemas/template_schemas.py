"""Pydantic schemas for Template API."""

from typing import List, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from ...domain.types import DatasetType, Industry


class TemplateResponse(BaseModel):
    """Dataset template response schema."""
    template_id: UUID
    name: str
    dataset_type: DatasetType
    industry: Optional[Industry] = None
    use_case: Optional[str] = None
    description: str = ""
    schema_definition: Dict = Field(default_factory=dict)
    default_record_count: int
    estimated_size_mb: float
    sample_data: Optional[List[Dict]] = None
    links: Dict[str, str] = Field(alias="_links", default_factory=dict)

    class Config:
        from_attributes = True
        populate_by_name = True


class TemplateListResponse(BaseModel):
    """List of templates."""
    templates: List[TemplateResponse]
    total_count: int

    class Config:
        populate_by_name = True


class ClientMetadata(BaseModel):
    """Client metadata for template recommendations."""
    industry: str
    use_case: str
    company_size: Optional[str] = None


class TemplateRecommendationRequest(BaseModel):
    """Request for template recommendations."""
    client_metadata: ClientMetadata
    dataset_types: List[str]
    stage: str


class TemplateRecommendation(BaseModel):
    """Single template recommendation."""
    dataset_type: str
    recommended_template: TemplateResponse
    confidence_score: float = Field(ge=0.0, le=1.0)
    reason: str


class TemplateRecommendationsResponse(BaseModel):
    """Template recommendations response."""
    recommendations: List[TemplateRecommendation]
