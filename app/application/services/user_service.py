from typing import List, Optional
from app.domain.entities.user import User, UserUpdate, UserRole
from app.domain.repositories.user_repository import UserRepository


class UserService:
    """Service for user management operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repository.get_by_id(user_id)
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return await self.user_repository.get_all(skip, limit)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        update_dict = user_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.user_repository.get_by_id(user_id)
        return await self.user_repository.update(user_id, update_dict)
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        return await self.user_repository.delete(user_id)
    
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        return await self.user_repository.update(user_id, {"is_active": False})
    
    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user account"""
        return await self.user_repository.update(user_id, {"is_active": True})
    
    async def change_user_role(self, user_id: int, role: UserRole) -> Optional[User]:
        """Change user role (Admin only)"""
        return await self.user_repository.update(user_id, {"role": role})
