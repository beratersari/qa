from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.user import User


class UserRepository(ABC):
    """Abstract repository for User entity"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        pass
    
    @abstractmethod
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user by ID"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user by ID"""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        pass
