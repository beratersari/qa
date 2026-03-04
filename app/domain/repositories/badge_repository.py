from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.badge import Badge, UserBadge


class BadgeRepository(ABC):
    """Abstract repository for badges"""

    @abstractmethod
    async def create(self, badge: Badge) -> Badge:
        """Create a badge"""
        pass

    @abstractmethod
    async def get_by_id(self, badge_id: int) -> Optional[Badge]:
        """Get badge by ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Badge]:
        """Get badge by name"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Badge]:
        """List badges"""
        pass

    @abstractmethod
    async def update(self, badge_id: int, badge_data: dict) -> Optional[Badge]:
        """Update badge"""
        pass

    @abstractmethod
    async def delete(self, badge_id: int) -> bool:
        """Delete badge"""
        pass


class UserBadgeRepository(ABC):
    """Abstract repository for user badge progress"""

    @abstractmethod
    async def create(self, user_badge: UserBadge) -> UserBadge:
        """Create user badge progress"""
        pass

    @abstractmethod
    async def get_by_id(self, user_badge_id: int) -> Optional[UserBadge]:
        """Get user badge progress by ID"""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserBadge]:
        """Get badges for a user"""
        pass

    @abstractmethod
    async def get_by_user_and_badge(self, user_id: int, badge_id: int) -> Optional[UserBadge]:
        """Get user badge progress for a badge"""
        pass

    @abstractmethod
    async def update(self, user_badge_id: int, data: dict) -> Optional[UserBadge]:
        """Update user badge progress"""
        pass

    @abstractmethod
    async def delete(self, user_badge_id: int) -> bool:
        """Delete user badge progress"""
        pass
