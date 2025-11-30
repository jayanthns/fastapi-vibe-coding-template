"""
FastAPI router for Animal API endpoints.
"""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.core.pagination import PageParams, PaginatedResponse
from src.core.schemas import APIResponse
from src.db.session import get_db_with_trace_id
from src.middleware.trace import get_trace_id
from src.apps.animals.repository import AnimalRepository
from src.apps.animals.schemas import Animal, AnimalCreate, AnimalUpdate
from src.apps.animals.service import AnimalService

router = APIRouter()


def get_animal_service(
    db: AsyncSession = Depends(get_db_with_trace_id),
) -> AnimalService:
    """Get animal service instance."""
    repository = AnimalRepository(db)
    return AnimalService(repository)


@router.post(
    "/",
    response_model=APIResponse[Animal],
    status_code=status.HTTP_201_CREATED,
)
async def create_animal(
    request: Request,
    payload: AnimalCreate,
    service: AnimalService = Depends(get_animal_service),
):
    """Create a new animal."""
    logger = get_logger(request)
    logger.info(f"Creating new animal: {payload.name} ({payload.species})")

    animal = await service.create_animal(payload)

    logger.info(f"Successfully created animal with ID: {animal.id}")
    return APIResponse.create_with_trace_id(
        data=animal,
        message="Animal created successfully",
        status_code=201,
        trace_id=get_trace_id(request),
    )


@router.get("/", response_model=APIResponse[PaginatedResponse[Animal]])
async def list_animals(
    request: Request,
    params: PageParams = Depends(),
    service: AnimalService = Depends(get_animal_service),
):
    """Retrieve all animals with pagination."""
    logger = get_logger(request)
    logger.info(f"Listing animals - skip: {params.skip}, limit: {params.limit}")

    animals, total = await service.list_animals(params.skip, params.limit)

    paginated_response = PaginatedResponse.create(
        items=animals,
        total=total,
        params=params,
    )

    logger.info(f"Retrieved {len(animals)} animals out of {total}")
    return APIResponse.create_with_trace_id(
        data=paginated_response,
        message=f"Retrieved {len(animals)} animals",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get("/{animal_id}", response_model=APIResponse[Animal])
async def get_animal(
    request: Request,
    animal_id: UUID,
    service: AnimalService = Depends(get_animal_service),
):
    """Retrieve a single animal by ID."""
    logger = get_logger(request)
    logger.info(f"Retrieving animal with ID: {animal_id}")

    animal = await service.get_animal(animal_id)
    if not animal:
        logger.warning(f"Animal not found with ID: {animal_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal not found",
        )

    logger.info(f"Animal retrieved successfully: {animal.name}")
    return APIResponse.create_with_trace_id(
        data=animal,
        message="Animal retrieved successfully",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.put("/{animal_id}", response_model=APIResponse[Animal])
async def update_animal(
    request: Request,
    animal_id: UUID,
    payload: AnimalUpdate,
    service: AnimalService = Depends(get_animal_service),
):
    """Update an animal."""
    logger = get_logger(request)
    logger.info(f"Updating animal with ID: {animal_id}")

    animal = await service.update_animal(animal_id, payload)
    if not animal:
        logger.warning(f"Animal not found for update with ID: {animal_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal not found",
        )

    logger.info(f"Animal updated successfully: {animal.name}")
    return APIResponse.create_with_trace_id(
        data=animal,
        message="Animal updated successfully",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    request: Request,
    animal_id: UUID,
    service: AnimalService = Depends(get_animal_service),
):
    """Delete an animal."""
    logger = get_logger(request)
    logger.info(f"Attempting to delete animal with ID: {animal_id}")

    success = await service.delete_animal(animal_id)
    if not success:
        logger.warning(f"Animal not found for deletion: {animal_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal not found",
        )

    logger.info(f"Successfully deleted animal with ID: {animal_id}")
    return None


@router.get("/logger-demo/", response_model=APIResponse[Dict[str, Any]])
async def logger_demo(request: Request):
    """Demo endpoint to showcase the logger functionality."""
    logger = get_logger(request)

    logger.debug("This is a debug message - usually not shown in production")
    logger.info("This is an info message - normal operation flow")
    logger.warning("This is a warning message - something unusual but not critical")

    # Demonstrate operation logging
    try:
        result = 42 / 1
        logger.info(f"Operation completed successfully: {result}")
    except Exception as e:
        logger.exception(f"This would log an exception: {str(e)}")

    return APIResponse.create_with_trace_id(
        data={
            "message": "Logger helper demo completed successfully!",
            "request_info": {
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("user-agent", ""),
            },
        },
        message="Logger demo completed",
        status_code=200,
        trace_id=get_trace_id(request),
    )
