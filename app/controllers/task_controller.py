from typing import List, Optional

from app.services import TaskService
from app.schemas import TaskCreate, TaskUpdate, TaskResponse


class TaskController:
    """Controller for task HTTP operations"""
    
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
    
    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskResponse:
        """Create a new task"""
        return await self.task_service.create_task(task_data, user_id)
    
    async def get_task(self, task_id: int, user_id: int) -> TaskResponse:
        """Get a task by ID"""
        return await self.task_service.get_task(task_id, user_id)
    
    async def get_all_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        priority: Optional[str] = None,
        is_done: Optional[bool] = None,
        search: Optional[bool] = None
    ) -> List[TaskResponse]:
        """Get all tasks with filters"""
        return await self.task_service.get_all_tasks(user_id, skip, limit, priority, is_done, search)
    
    async def update_task(self, task_id: int, user_id: int, task_data: TaskUpdate) -> TaskResponse:
        """Update a task"""
        return await self.task_service.update_task(task_id, user_id, task_data)
    
    async def delete_task(self, task_id: int, user_id: int) -> None:
        """Delete a task"""
        return await self.task_service.delete_task(task_id, user_id)
    
    async def toggle_task_status(self, task_id: int, user_id: int) -> TaskResponse:
        """Toggle task completion status"""
        return await self.task_service.toggle_task_status(task_id, user_id)