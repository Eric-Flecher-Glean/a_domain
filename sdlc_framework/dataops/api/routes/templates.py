"""Template API routes."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.types import DatasetType, Industry
from ...infrastructure.persistence.repositories import TemplateRepository
from ..dependencies import get_db, require_scope
from ..schemas.template_schemas import (
    TemplateResponse,
    TemplateListResponse,
    TemplateRecommendationRequest,
    TemplateRecommendationsResponse,
    TemplateRecommendation
)


router = APIRouter(prefix="/v1/dataops", tags=["templates"])


def template_to_response(template, base_url: str = "/v1/dataops") -> TemplateResponse:
    """Convert domain template to API response."""
    sample_data = template.metadata_template.get('sample_data', [])

    return TemplateResponse(
        template_id=template.template_id,
        name=template.name,
        dataset_type=template.dataset_type,
        industry=template.industry,
        use_case=template.use_case,
        description=template.description,
        schema_definition=template.schema_definition,
        default_record_count=template.default_record_count,
        estimated_size_mb=template.estimated_size_mb,
        sample_data=sample_data if sample_data else None,
        _links={
            "self": f"{base_url}/templates/{template.template_id}",
            "datasets": f"{base_url}/datasets?template_id={template.template_id}"
        }
    )


@router.get(
    "/templates",
    response_model=TemplateListResponse,
    dependencies=[Depends(require_scope("dataops:templates:read"))]
)
async def list_templates(
    industry: Optional[str] = None,
    use_case: Optional[str] = None,
    dataset_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List dataset templates with optional filtering.

    Query Parameters:
    - industry: Filter by industry (fintech, healthcare, enterprise, etc.)
    - use_case: Filter by use case
    - dataset_type: Filter by dataset type
    """
    repo = TemplateRepository(db)

    # Parse enum values
    industry_enum = None
    if industry:
        try:
            industry_enum = Industry(industry.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid industry: {industry}"
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

    # Query templates
    templates = await repo.find_by_criteria(
        industry=industry_enum,
        use_case=use_case,
        dataset_type=dataset_type_enum
    )

    # Convert to response
    template_responses = [template_to_response(t) for t in templates]

    return TemplateListResponse(
        templates=template_responses,
        total_count=len(template_responses)
    )


@router.get(
    "/templates/{template_id}",
    response_model=TemplateResponse,
    dependencies=[Depends(require_scope("dataops:templates:read"))]
)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get template by ID."""
    repo = TemplateRepository(db)
    template = await repo.get_by_id(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )

    return template_to_response(template)


@router.post(
    "/templates/recommend",
    response_model=TemplateRecommendationsResponse,
    dependencies=[Depends(require_scope("dataops:templates:read"))]
)
async def recommend_templates(
    request: TemplateRecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered template recommendations based on client metadata.

    Matches client industry/use_case to appropriate templates
    and returns ranked recommendations with confidence scores.
    """
    repo = TemplateRepository(db)

    # Parse industry
    try:
        industry = Industry(request.client_metadata.industry.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid industry: {request.client_metadata.industry}"
        )

    # Find matching templates by industry and use case
    all_templates = await repo.find_by_criteria(
        industry=industry,
        use_case=request.client_metadata.use_case
    )

    # Build recommendations for each requested dataset type
    recommendations = []

    for dataset_type_str in request.dataset_types:
        # Parse dataset type
        try:
            dataset_type = DatasetType(dataset_type_str.lower())
        except ValueError:
            continue

        # Find best match for this type
        matching_templates = [
            t for t in all_templates
            if t.dataset_type == dataset_type
        ]

        if matching_templates:
            # Use first match (in production, this would be ML-based ranking)
            best_match = matching_templates[0]

            # Calculate confidence score (simplified)
            confidence = 0.95 if (
                best_match.industry == industry and
                best_match.use_case == request.client_metadata.use_case
            ) else 0.70

            reason = "Exact match on industry and use_case" if confidence > 0.9 else "Partial match"

            recommendations.append(
                TemplateRecommendation(
                    dataset_type=dataset_type_str,
                    recommended_template=template_to_response(best_match),
                    confidence_score=confidence,
                    reason=reason
                )
            )

    return TemplateRecommendationsResponse(recommendations=recommendations)
