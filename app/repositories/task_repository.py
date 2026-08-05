from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    """Repository for task database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, task_data: TaskCreate, user_id: int) -> Task:
        """Create a new task for a user"""
        task = Task(
            title=task_data.title,
            description=task_data.description,
            is_done=task_data.is_done,
            priority=task_data.priority,
            owner_id=user_id
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get task by ID - only if it belongs to the user"""
        result = await self.db.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.owner_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for a user with pagination"""
        result = await self.db.execute(
            select(Task)
            .where(Task.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Task.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_priority(self, user_id: int, priority: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by priority for a user"""
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.owner_id == user_id,
                    Task.priority == priority
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Task.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_status(self, user_id: int, is_done: bool, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by completion status for a user"""
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.owner_id == user_id,
                    Task.is_done == is_done
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Task.created_at.desc())
        )
        return result.scalars().all()
    
    async def search(self, user_id: int, query: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Search tasks by title or description for a user"""
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.owner_id == user_id,
                    or_(
                        Task.title.ilike(f"%{query}%"),
                        Task.description.ilike(f"%{query}%")
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Task.created_at.desc())
        )
        return result.scalars().all()
    
    async def update(self, task_id: int, user_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update task by ID - only if it belongs to the user"""
        # Get task first (with ownership check)
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return None
        
        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def delete(self, task_id: int, user_id: int) -> bool:
        """Delete task by ID - only if it belongs to the user"""
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return False
        
        await self.db.delete(task)
        await self.db.commit()
        return True
    
    async def count_by_user(self, user_id: int) -> int:
        """Count total tasks for a user"""
        result = await self.db.execute(
            select(Task).where(Task.owner_id == user_id)
        )
        return len(result.scalars().all())