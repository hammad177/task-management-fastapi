from typing import List, Optional
from fastapi import HTTPException, status

from app.services import UserService
from app.schemas import UserCreate, UserUpdate, UserResponse


class UserController:
    """Controller for user HTTP operations"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def register(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        return await self.user_service.create_user(user_data)
    
    async def login(self, username: str, password: str) -> dict:
        """Login user"""
        return await self.user_service.login(username, password)
    
    async def get_user(self, user_id: int) -> UserResponse:
        """Get a user by ID"""
        return await self.user_service.get_user(user_id)
    
    async def get_current_user(self, user_id: int) -> UserResponse:
        """Get current user profile"""
        return await self.user_service.get_user(user_id)
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination"""
        return await self.user_service.get_all_users(skip, limit)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update a user"""
        return await self.user_service.update_user(user_id, user_data)
    
    async def delete_user(self, user_id: int) -> None:
        """Delete a user"""
        return await self.user_service.delete_user(user_id)
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Change user password"""
        return await self.user_service.change_password(user_id, current_password, new_password)