from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.controllers import UserController
from app.services import UserService
from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate, UserLogin, ChangePassword
from app.common import ApiResponseBuilder
from app.core import get_current_user
from app.models import User


router = APIRouter(prefix="/api/users", tags=["Users"])


def get_user_controller(db: AsyncSession = Depends(get_db)) -> UserController:
    """Dependency injection for UserController"""
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    return UserController(user_service)


# ============================================
# Public Routes (No Authentication Required)
# ============================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    controller: UserController = Depends(get_user_controller),
):
    """Register a new user"""
    result = await controller.register(user_data)
    return ApiResponseBuilder.created(
        message="User registered successfully",
        data=result
    )


@router.post("/login")
async def login(
    login_data: UserLogin,
    controller: UserController = Depends(get_user_controller),
):
    """Login user and get access token"""
    result = await controller.login(login_data.username, login_data.password)
    return ApiResponseBuilder.success(
        message="Login successful",
        data={
            "user": result["user"],
            "access_token": result["access_token"],
            "token_type": "bearer"
        }
    )


# ============================================
# Protected Routes (Authentication Required)
# ============================================

@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """Get current user profile"""
    result = await controller.get_current_user(current_user.id)
    return ApiResponseBuilder.success(
        message="User profile retrieved successfully",
        data=result
    )

@router.get("/me/tasks")
async def get_current_user_with_tasks(
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """Get current user profile with all their tasks"""
    result = await controller.get_user_with_tasks(current_user.id)
    return ApiResponseBuilder.success(
        message="User profile with tasks retrieved successfully",
        data=result
    )

@router.get("/")
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_user),
):
    """Get all users (admin only)"""
    # TODO: Add admin check
    result = await controller.get_all_users(skip, limit)
    return ApiResponseBuilder.success(
        message="Users retrieved successfully",
        data=result
    )


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_user),
):
    """Get a specific user by ID"""
    result = await controller.get_user(user_id)
    return ApiResponseBuilder.success(
        message="User retrieved successfully",
        data=result
    )


@router.put("/me")
async def update_user(
    user_data: UserUpdate,
    controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_user),
):
    """Update a user (self only)"""
    result = await controller.update_user(current_user.id, user_data)
    return ApiResponseBuilder.success(
        message="User updated successfully",
        data=result
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_user),
):
    """Delete a user (self only)"""
    # TODO: Check if user is deleting themselves or is admin
    await controller.delete_user(current_user.id)
    return ApiResponseBuilder.no_content(
        message="User deleted successfully"
    )


@router.patch("/me/password")
async def change_password(
    password_data: ChangePassword,
    controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_user),
):
    """Change current user's password"""
    await controller.change_password(
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    return ApiResponseBuilder.success(
        message="Password changed successfully"
    )