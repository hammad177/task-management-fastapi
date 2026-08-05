from typing import Optional, List
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.core.security import create_access_token


class UserService:
    """Service layer for user business logic"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user with validation"""
        # Check if username exists
        if await self.user_repository.exists_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        
        # Check if email exists
        if await self.user_repository.exists_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        
        # Hash password and create user
        hashed_password = self._hash_password(user_data.password)
        user = await self.user_repository.create(user_data, hashed_password)
        
        return UserResponse.model_validate(user)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user"""
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        return UserResponse.model_validate(user)
    
    async def get_user(self, user_id: int) -> UserResponse:
        """Get a single user by ID"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_validate(user)
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get a user by username"""
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        return UserResponse.model_validate(user)
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination"""
        users = await self.user_repository.get_all(skip, limit)
        return [UserResponse.model_validate(user) for user in users]
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update a user"""
        
        if "password" in user_data.model_dump(exclude_unset=True):
            # Hash the new password before updating
            user_data.password = self._hash_password(user_data.password)
        
        user = await self.user_repository.update(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_validate(user)
    
    async def delete_user(self, user_id: int) -> None:
        """Delete a user"""
        deleted = await self.user_repository.delete(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Change user password"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not self._verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        hashed_password = self._hash_password(new_password)
        updated = await self.user_repository.update_password(user_id, hashed_password)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
    
    async def login(self, username: str, password: str) -> dict:
        """Login user and return token"""
        user = await self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email
        }
        access_token = create_access_token(token_data)
        
        return {
            "user": user,
            "access_token": access_token
        }