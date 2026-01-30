"""Pydantic schemas for Dataset API."""

from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from ...domain.types import DatasetType, Stage, DatasetStatus, DataSource


class ConnectorInfo(BaseModel):
    """Connector information in dataset response."""
    connector_id: UUID
    name: str
    status: str
    endpoint_url: Optional[str] = None

    class Config:
        from_attributes = True


class TemplateInfo(BaseModel):
    """Template reference in dataset response."""
    template_id: UUID
    name: str

    class Config:
        from_attributes = True


class DatasetMetadataResponse(BaseModel):
    """Dataset metadata in response."""
    industry: Optional[str] = None
    use_case: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, str] = Field(default_factory=dict)


class QualityCheckResponse(BaseModel):
    """Quality check information."""
    check_id: UUID
    check_type: str
    status: str
    score: float
    executed_at: Optional[datetime] = None


class DatasetResponse(BaseModel):
    """Dataset response schema."""
    dataset_id: UUID
    name: str
    dataset_type: DatasetType
    stage: Stage
    client_id: UUID
    journey_id: UUID
    status: DatasetStatus
    created_at: datetime
    ready_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    data_source: DataSource
    record_count: int
    size_bytes: int
    quality_score: Optional[float] = None
    connector: Optional[ConnectorInfo] = None
    template: Optional[TemplateInfo] = None
    metadata: DatasetMetadataResponse = Field(default_factory=DatasetMetadataResponse)
    quality_checks: List[QualityCheckResponse] = Field(default_factory=list)
    links: Dict[str, str] = Field(alias="_links", default_factory=dict)

    class Config:
        from_attributes = True
        populate_by_name = True


class PaginationInfo(BaseModel):
    """Pagination metadata."""
    page: int
    per_page: int
    total_pages: int
    total_count: int


class DatasetListResponse(BaseModel):
    """List of datasets with pagination."""
    datasets: List[DatasetResponse]
    pagination: PaginationInfo
    links: Dict[str, str] = Field(alias="_links", default_factory=dict)

    class Config:
        populate_by_name = True
