from typing import List, Optional
from fastapi import HTTPException, status

from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate, TaskResponse


class TaskService:
    """Service layer for task business logic"""
    
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskResponse:
        """Create a new task for a user"""
        
        task = await self.task_repository.create(task_data, user_id)
        return TaskResponse.model_validate(task)
    
    async def get_task(self, task_id: int, user_id: int) -> TaskResponse:
        """Get a single task by ID - only if it belongs to the user"""
        task = await self.task_repository.get_by_id(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return TaskResponse.model_validate(task)
    
    async def get_all_tasks(
        self, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100,
        priority: Optional[str] = None,
        is_done: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[TaskResponse]:
        """Get all tasks for a user with optional filters"""
        # Apply filters
        if search:
            tasks = await self.task_repository.search(user_id, search, skip, limit)
        elif priority:
            tasks = await self.task_repository.get_by_priority(user_id, priority, skip, limit)
        elif is_done is not None:
            tasks = await self.task_repository.get_by_status(user_id, is_done, skip, limit)
        else:
            tasks = await self.task_repository.get_all(user_id, skip, limit)
        
        return [TaskResponse.model_validate(task) for task in tasks]
    
    async def update_task(self, task_id: int, user_id: int, task_data: TaskUpdate) -> TaskResponse:
        """Update a task - only if it belongs to the user"""
        task = await self.task_repository.update(task_id, user_id, task_data)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return TaskResponse.model_validate(task)
    
    async def delete_task(self, task_id: int, user_id: int) -> None:
        """Delete a task - only if it belongs to the user"""
        deleted = await self.task_repository.delete(task_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    
    async def toggle_task_status(self, task_id: int, user_id: int) -> TaskResponse:
        """Toggle task completion status - only if it belongs to the user"""
        task = await self.task_repository.get_by_id(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Toggle is_done
        update_data = TaskUpdate(is_done=not task.is_done)
        updated_task = await self.task_repository.update(task_id, user_id, update_data)
        return TaskResponse.model_validate(updated_task)