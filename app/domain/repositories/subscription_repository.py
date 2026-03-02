from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.subscription import Subscription


class SubscriptionRepository(ABC):
    """Abstract repository for Subscription entity"""
    
    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription"""
        pass
    
    @abstractmethod
    async def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[Subscription]:
        """Get subscription by user ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Get all subscriptions with pagination"""
        pass
    
    @abstractmethod
    async def get_active_subscriptions(self) -> List[Subscription]:
        """Get all active subscriptions"""
        pass
    
    @abstractmethod
    async def update(self, subscription_id: int, subscription_data: dict) -> Optional[Subscription]:
        """Update subscription by ID"""
        pass
    
    @abstractmethod
    async def delete(self, subscription_id: int) -> bool:
        """Delete subscription by ID"""
        pass
    
    @abstractmethod
    async def cancel_subscription(self, subscription_id: int) -> bool:
        """Cancel a subscription"""
        pass
