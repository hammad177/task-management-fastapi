from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    description: str = Field(..., description="Task description", min_length=1, max_length=500)
    is_done: bool = Field(False, description="Completion status")
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$", description="Task priority")


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    is_done: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")


class TaskResponse(TaskBase):
    """Schema for task response (includes database fields)"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)