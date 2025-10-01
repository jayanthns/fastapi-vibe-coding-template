"""
API router for sensitive field configuration management.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_db
from app.repositories.sensitive_field import SensitiveFieldRepository
from app.schemas.sensitive_field import (
    SensitiveFieldCreate,
    SensitiveFieldList,
    SensitiveFieldResponse,
    SensitiveFieldUpdate,
)
from app.services.sensitive_field import SensitiveFieldService
from app.utils.security import secure_response

router = APIRouter()


def get_sensitive_field_service(
    db: AsyncSession = Depends(get_db),
) -> SensitiveFieldService:
    """Get sensitive field service instance."""
    repository = SensitiveFieldRepository(db)
    return SensitiveFieldService(repository)


@router.post("/", response_model=dict, status_code=201)
async def create_sensitive_field(
    request: Request,
    sensitive_field: SensitiveFieldCreate,
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """Create a new sensitive field pattern."""
    logger = get_logger(request)
    logger.info(f"Creating sensitive field pattern: {sensitive_field.field_name}")

    result = await service.create_sensitive_field(sensitive_field)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=secure_response(result))

    logger.info(f"Sensitive field pattern created successfully: {result['data'].id}")
    return secure_response(result)


@router.get("/", response_model=dict)
async def list_sensitive_fields(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(
        None, description="Search term for field name or description"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """List sensitive field patterns with pagination and filtering."""
    logger = get_logger(request)
    logger.info(
        f"Listing sensitive fields: skip={skip}, limit={limit}, search={search}, is_active={is_active}"
    )

    result = await service.get_all_sensitive_fields(skip, limit, search, is_active)
    return secure_response(result)


@router.get("/active", response_model=dict)
async def get_active_sensitive_fields(
    request: Request,
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """Get all active sensitive field patterns for masking logic."""
    logger = get_logger(request)
    logger.info("Getting active sensitive field patterns")

    result = await service.get_active_sensitive_fields()
    return secure_response(
        {
            "success": True,
            "message": "Active sensitive field patterns retrieved successfully",
            "data": result,
        }
    )


@router.get("/{sensitive_field_id}", response_model=dict)
async def get_sensitive_field(
    request: Request,
    sensitive_field_id: UUID,
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """Get a sensitive field pattern by ID."""
    logger = get_logger(request)
    logger.info(f"Getting sensitive field pattern: {sensitive_field_id}")

    result = await service.get_sensitive_field(sensitive_field_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=secure_response(result))

    return secure_response(result)


@router.put("/{sensitive_field_id}", response_model=dict)
async def update_sensitive_field(
    request: Request,
    sensitive_field_id: UUID,
    sensitive_field: SensitiveFieldUpdate,
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """Update a sensitive field pattern."""
    logger = get_logger(request)
    logger.info(f"Updating sensitive field pattern: {sensitive_field_id}")

    result = await service.update_sensitive_field(sensitive_field_id, sensitive_field)

    if not result["success"]:
        status_code = 400 if "already exists" in result["message"] else 404
        raise HTTPException(status_code=status_code, detail=secure_response(result))

    logger.info(f"Sensitive field pattern updated successfully: {sensitive_field_id}")
    return secure_response(result)


@router.delete("/{sensitive_field_id}", response_model=dict)
async def delete_sensitive_field(
    request: Request,
    sensitive_field_id: UUID,
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """Delete a sensitive field pattern."""
    logger = get_logger(request)
    logger.info(f"Deleting sensitive field pattern: {sensitive_field_id}")

    result = await service.delete_sensitive_field(sensitive_field_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=secure_response(result))

    logger.info(f"Sensitive field pattern deleted successfully: {sensitive_field_id}")
    return secure_response(result)


@router.patch("/{sensitive_field_id}/deactivate", response_model=dict)
async def deactivate_sensitive_field(
    request: Request,
    sensitive_field_id: UUID,
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """Deactivate a sensitive field pattern (soft delete)."""
    logger = get_logger(request)
    logger.info(f"Deactivating sensitive field pattern: {sensitive_field_id}")

    result = await service.deactivate_sensitive_field(sensitive_field_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=secure_response(result))

    logger.info(
        f"Sensitive field pattern deactivated successfully: {sensitive_field_id}"
    )
    return secure_response(result)


@router.patch("/{sensitive_field_id}/activate", response_model=dict)
async def activate_sensitive_field(
    request: Request,
    sensitive_field_id: UUID,
    service: SensitiveFieldService = Depends(get_sensitive_field_service),
):
    """Activate a sensitive field pattern."""
    logger = get_logger(request)
    logger.info(f"Activating sensitive field pattern: {sensitive_field_id}")

    result = await service.activate_sensitive_field(sensitive_field_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=secure_response(result))

    logger.info(f"Sensitive field pattern activated successfully: {sensitive_field_id}")
    return secure_response(result)
