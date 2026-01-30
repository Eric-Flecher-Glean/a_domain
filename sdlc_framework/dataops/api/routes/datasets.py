"""Dataset API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.types import DatasetType, Stage, DatasetStatus
from ...infrastructure.persistence.repositories import DatasetRepository
from ..dependencies import get_db, require_scope
from ..schemas.dataset_schemas import (
    DatasetResponse,
    DatasetListResponse,
    PaginationInfo,
    ConnectorInfo,
    TemplateInfo,
    DatasetMetadataResponse,
    QualityCheckResponse
)


router = APIRouter(prefix="/v1/dataops", tags=["datasets"])


def dataset_to_response(dataset, base_url: str = "/v1/dataops") -> DatasetResponse:
    """Convert domain dataset to API response."""
    # Build connector info
    connector = None
    if dataset.connector_id:
        connector = ConnectorInfo(
            connector_id=dataset.connector_id,
            name=dataset.name,
            status="healthy",  # TODO: Get actual connector status
            endpoint_url=None
        )

    # Build template info
    template = None
    if dataset.template_id:
        template = TemplateInfo(
            template_id=dataset.template_id,
            name="Template"  # TODO: Load template name
        )

    # Build metadata
    metadata = DatasetMetadataResponse()
    if dataset.metadata:
        metadata = DatasetMetadataResponse(
            industry=dataset.metadata.industry.value if dataset.metadata.industry else None,
            use_case=dataset.metadata.use_case,
            tags=dataset.metadata.tags,
            custom_fields=dataset.metadata.custom_fields
        )

    # Build quality checks
    quality_checks = [
        QualityCheckResponse(
            check_id=check.check_id,
            check_type=check.check_type.value,
            status=check.status.value,
            score=check.score,
            executed_at=check.executed_at
        )
        for check in dataset.quality_checks
    ]

    return DatasetResponse(
        dataset_id=dataset.dataset_id,
        name=dataset.name,
        dataset_type=dataset.dataset_type,
        stage=dataset.stage,
        client_id=dataset.client_id,
        journey_id=dataset.journey_id,
        status=dataset.status,
        created_at=dataset.created_at,
        ready_at=dataset.ready_at,
        archived_at=dataset.archived_at,
        data_source=dataset.data_source,
        record_count=dataset.record_count,
        size_bytes=dataset.size_bytes,
        quality_score=dataset.quality_score.overall_score if dataset.quality_score else None,
        connector=connector,
        template=template,
        metadata=metadata,
        quality_checks=quality_checks,
        _links={
            "self": f"{base_url}/datasets/{dataset.dataset_id}",
            "quality": f"{base_url}/datasets/{dataset.dataset_id}/quality",
            "usage": f"{base_url}/datasets/{dataset.dataset_id}/usage"
        }
    )


@router.get(
    "/datasets",
    response_model=DatasetListResponse,
    dependencies=[Depends(require_scope("dataops:datasets:read"))]
)
async def list_datasets(
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    journey_id: Optional[UUID] = Query(None, description="Filter by journey ID"),
    stage: Optional[str] = Query(None, description="Filter by stage (sandbox, pilot, production)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    dataset_type: Optional[str] = Query(None, description="Filter by dataset type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """List datasets with filtering and pagination.

    Query Parameters:
    - client_id: Filter by client UUID
    - journey_id: Filter by journey UUID
    - stage: Filter by stage (sandbox, pilot, production)
    - status: Filter by status (provisioning, ready, etc.)
    - dataset_type: Filter by type (confluence_pages, github_repos, etc.)
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    """
    repo = DatasetRepository(db)

    # Parse enums
    stage_enum = None
    if stage:
        try:
            stage_enum = Stage(stage.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage: {stage}"
            )

    status_enum = None
    if status:
        try:
            status_enum = DatasetStatus(status.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    dataset_type_enum = None
    if dataset_type:
        try:
            dataset_type_enum = DatasetType(dataset_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid dataset_type: {dataset_type}"
            )

    # Query datasets
    if journey_id:
        datasets = await repo.find_by_journey(journey_id)
        # Apply additional filters in memory (could optimize with DB query)
        if status_enum:
            datasets = [d for d in datasets if d.status == status_enum]
        if dataset_type_enum:
            datasets = [d for d in datasets if d.dataset_type == dataset_type_enum]
    elif client_id and stage_enum:
        datasets = await repo.find_by_client_and_stage(
            client_id, stage_enum, dataset_type_enum, status_enum
        )
    else:
        # List all (with limits)
        datasets = await repo.list_all(limit=per_page, offset=(page - 1) * per_page)

    # Apply pagination (simplified - in production, use SQL OFFSET/LIMIT)
    total_count = len(datasets)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_datasets = datasets[start_idx:end_idx]

    # Convert to response
    dataset_responses = [dataset_to_response(d) for d in paginated_datasets]

    # Build pagination info
    total_pages = (total_count + per_page - 1) // per_page
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_count=total_count
    )

    return DatasetListResponse(
        datasets=dataset_responses,
        pagination=pagination,
        _links={
            "self": f"/v1/dataops/datasets?page={page}",
            "first": "/v1/dataops/datasets?page=1",
            "last": f"/v1/dataops/datasets?page={total_pages}"
        }
    )


@router.get(
    "/datasets/{dataset_id}",
    response_model=DatasetResponse,
    dependencies=[Depends(require_scope("dataops:datasets:read"))]
)
async def get_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get dataset by ID."""
    repo = DatasetRepository(db)
    dataset = await repo.get_by_id(dataset_id)

    if not dataset:
        # Try to load from domain repository
        dataset_model = await repo.get_by_id(dataset_id)
        if dataset_model:
            dataset = repo._to_domain(dataset_model)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found"
        )

    return dataset_to_response(dataset)
