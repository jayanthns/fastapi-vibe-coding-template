"""
User management API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.repository import UserRepository
from src.apps.users.schemas import (
    UserCreate,
    UserLogin,
    UserPasswordChange,
    UserProfile,
    UserResponse,
    UserUpdate,
)
from src.apps.users.service import UserService
from src.core.auth import get_current_active_user, get_current_superuser
from src.core.logging import get_logger
from src.core.pagination import PageParams, PaginatedResponse
from src.core.schemas import APIResponse
from src.db.session import get_db

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get user service instance."""
    repository = UserRepository(db)
    return UserService(repository)


@router.post("/register", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    user_create: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """Register a new user."""
    logger = get_logger(request)
    logger.info(f"User registration attempt for email: {user_create.email}")

    try:
        user, access_token = await service.create_user(user_create)

        logger.info(f"User registered successfully: {user.id}")

        return APIResponse.create_with_trace_id(
            data={
                "user": user.model_dump(),
                "access_token": access_token,
                "token_type": "bearer",
            },
            message="User registered successfully",
            status_code=201,
            trace_id=getattr(request.state, "trace_id", None),
        )

    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=APIResponse[dict])
async def login_user(
    request: Request,
    user_login: UserLogin,
    service: UserService = Depends(get_user_service),
):
    """Authenticate user and return access token."""
    logger = get_logger(request)
    logger.info(f"Login attempt for email: {user_login.email}")

    try:
        user, access_token = await service.authenticate_user(user_login)

        logger.info(f"User logged in successfully: {user.id}")

        return APIResponse.create_with_trace_id(
            data={
                "user": user.model_dump(),
                "access_token": access_token,
                "token_type": "bearer",
            },
            message="Login successful",
            trace_id=getattr(request.state, "trace_id", None),
        )

    except ValueError as e:
        logger.warning(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=APIResponse[UserProfile])
async def get_current_user_profile(
    request: Request,
    current_user: dict = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
):
    """Get current user's profile."""
    logger = get_logger(request)
    logger.info(f"Profile request for user: {current_user['id']}")

    user = await service.get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Profile retrieved for user: {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="Profile retrieved successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.patch("/me", response_model=APIResponse[UserProfile])
async def update_current_user_profile(
    request: Request,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
):
    """Update current user's profile."""
    logger = get_logger(request)
    logger.info(f"Profile update request for user: {current_user['id']}")

    user = await service.update_user(current_user["id"], user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Profile updated for user: {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="Profile updated successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.post("/me/change-password", response_model=APIResponse[dict])
async def change_password(
    request: Request,
    password_change: UserPasswordChange,
    current_user: dict = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
):
    """Change current user's password."""
    logger = get_logger(request)
    logger.info(f"Password change request for user: {current_user['id']}")

    try:
        success = await service.change_password(current_user["id"], password_change)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Password changed for user: {current_user['id']}")

        return APIResponse.create_with_trace_id(
            data={"message": "Password changed successfully"},
            message="Password changed successfully",
            trace_id=getattr(request.state, "trace_id", None),
        )

    except ValueError as e:
        logger.warning(f"Password change failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Admin endpoints
@router.get("/", response_model=APIResponse[PaginatedResponse[UserResponse]])
async def list_users(
    request: Request,
    params: PageParams = Depends(),
    search: str | None = Query(None, description="Search term for users"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_superuser),
    service: UserService = Depends(get_user_service),
):
    """List all users (admin only)."""
    logger = get_logger(request)
    logger.info(f"User list request by admin: {current_user['id']}")

    users, total = await service.get_users(
        skip=params.skip, limit=params.limit, search=search, is_active=is_active
    )

    paginated_response = PaginatedResponse.create(
        items=users,
        total=total,
        params=params,
    )

    logger.info(f"Returned {len(users)} users out of {total}")

    return APIResponse.create_with_trace_id(
        data=paginated_response,
        message=f"Retrieved {len(users)} users",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.get("/{user_id}", response_model=APIResponse[UserProfile])
async def get_user_by_id(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_superuser),
    service: UserService = Depends(get_user_service),
):
    """Get user by ID (admin only)."""
    logger = get_logger(request)
    logger.info(f"User details request for {user_id} by admin: {current_user['id']}")

    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User details retrieved for {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="User details retrieved successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.patch("/{user_id}", response_model=APIResponse[UserProfile])
async def update_user_by_id(
    request: Request,
    user_id: UUID,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_superuser),
    service: UserService = Depends(get_user_service),
):
    """Update user by ID (admin only)."""
    logger = get_logger(request)
    logger.info(f"User update request for {user_id} by admin: {current_user['id']}")

    user = await service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User updated: {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="User updated successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.post("/{user_id}/verify", response_model=APIResponse[UserProfile])
async def verify_user(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_superuser),
    service: UserService = Depends(get_user_service),
):
    """Verify a user account (admin only)."""
    logger = get_logger(request)
    logger.info(f"User verification request for {user_id} by admin: {current_user['id']}")

    user = await service.verify_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User verified: {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="User verified successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.post("/{user_id}/deactivate", response_model=APIResponse[UserProfile])
async def deactivate_user(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_superuser),
    service: UserService = Depends(get_user_service),
):
    """Deactivate a user account (admin only)."""
    logger = get_logger(request)
    logger.info(f"User deactivation request for {user_id} by admin: {current_user['id']}")

    user = await service.deactivate_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User deactivated: {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="User deactivated successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.post("/{user_id}/activate", response_model=APIResponse[UserProfile])
async def activate_user(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_superuser),
    service: UserService = Depends(get_user_service),
):
    """Activate a user account (admin only)."""
    logger = get_logger(request)
    logger.info(f"User activation request for {user_id} by admin: {current_user['id']}")

    user = await service.activate_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User activated: {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="User activated successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )


@router.post("/{user_id}/make-superuser", response_model=APIResponse[UserProfile])
async def make_superuser(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_superuser),
    service: UserService = Depends(get_user_service),
):
    """Make a user a superuser (admin only)."""
    logger = get_logger(request)
    logger.info(f"Make superuser request for {user_id} by admin: {current_user['id']}")

    user = await service.make_superuser(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User made superuser: {user.id}")

    return APIResponse.create_with_trace_id(
        data=user.model_dump(),
        message="User promoted to superuser successfully",
        trace_id=getattr(request.state, "trace_id", None),
    )
