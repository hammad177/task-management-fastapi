from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.controllers import TaskController
from app.services import TaskService
from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.common import ApiResponseBuilder
from app.core.dependencies import get_current_user
from app.models import User


router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def get_task_controller(db: AsyncSession = Depends(get_db)) -> TaskController:
    """Dependency injection for TaskController"""
    task_repository = TaskRepository(db)
    task_service = TaskService(task_repository)
    return TaskController(task_service)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
):
    """Create a new task"""
    result = await controller.create_task(task_data, current_user.id)
    return ApiResponseBuilder.created(
        message="Task created successfully",
        data=result
    )


@router.get("/")
async def get_all_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high|urgent)$", description="Filter by priority"),
    is_done: Optional[bool] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, min_length=1, description="Search by title or description"),
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
):
    """Get all tasks with optional filters"""
    result = await controller.get_all_tasks(
        current_user.id, skip, limit, priority, is_done, search
    )
    return ApiResponseBuilder.success(
        message="Tasks retrieved successfully",
        data=result
    )

@router.get("/{task_id}")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
):
    """Get a specific task by ID"""
    result = await controller.get_task(task_id, current_user.id)
    return ApiResponseBuilder.success(
        message="Task retrieved successfully",
        data=result
    )


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
):
    """Update a task"""
    result = await controller.update_task(task_id, current_user.id, task_data)
    return ApiResponseBuilder.success(
        message="Task updated successfully",
        data=result
    )


@router.patch("/{task_id}/toggle")
async def toggle_task_status(
    task_id: int,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
):
    """Toggle task completion status"""
    result = await controller.toggle_task_status(task_id, current_user.id)
    return ApiResponseBuilder.success(
        message="Task status toggled successfully",
        data=result
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    controller: TaskController = Depends(get_task_controller),
):
    """Delete a task"""
    await controller.delete_task(task_id, current_user.id)
    return ApiResponseBuilder.no_content(
        message="Task deleted successfully"
    )