from datetime import datetime, timedelta
from typing import List, Optional
from app.domain.entities.subscription import Subscription, SubscriptionCreate, SubscriptionStatus, SubscriptionPlan
from app.domain.entities.user import SubscriptionType
from app.domain.repositories.subscription_repository import SubscriptionRepository
from app.domain.repositories.user_repository import UserRepository


class SubscriptionService:
    """Service for subscription management operations"""
    
    def __init__(self, subscription_repository: SubscriptionRepository, user_repository: UserRepository):
        self.subscription_repository = subscription_repository
        self.user_repository = user_repository
    
    def _calculate_end_date(self, plan: SubscriptionPlan) -> datetime:
        """Calculate subscription end date based on plan"""
        if plan == SubscriptionPlan.MONTHLY:
            return datetime.utcnow() + timedelta(days=30)
        elif plan == SubscriptionPlan.YEARLY:
            return datetime.utcnow() + timedelta(days=365)
        return datetime.utcnow() + timedelta(days=30)
    
    async def create_subscription(self, subscription_data: SubscriptionCreate) -> Optional[Subscription]:
        """Create a new subscription for a user"""
        # Check if user exists
        user = await self.user_repository.get_by_id(subscription_data.user_id)
        if not user:
            return None
        
        # Check if user already has a subscription
        existing_sub = await self.subscription_repository.get_by_user_id(subscription_data.user_id)
        
        # Calculate end date
        end_date = self._calculate_end_date(subscription_data.plan)
        
        if existing_sub:
            # Update existing subscription instead of inserting a new one
            updated_sub = await self.subscription_repository.update(
                existing_sub.id,
                {
                    "plan": subscription_data.plan,
                    "status": SubscriptionStatus.ACTIVE,
                    "start_date": datetime.utcnow(),
                    "end_date": end_date,
                    "auto_renew": subscription_data.auto_renew,
                    "payment_method": subscription_data.payment_method,
                    "cancelled_at": None
                }
            )
            created_sub = updated_sub
        else:
            # Create subscription entity
            subscription = Subscription(
                user_id=subscription_data.user_id,
                plan=subscription_data.plan,
                status=SubscriptionStatus.ACTIVE,
                end_date=end_date,
                auto_renew=subscription_data.auto_renew,
                payment_method=subscription_data.payment_method
            )
            
            # Save subscription
            created_sub = await self.subscription_repository.create(subscription)
        
        # Update user's subscription type to premium
        await self.user_repository.update(
            subscription_data.user_id, 
            {"subscription_type": SubscriptionType.PREMIUM}
        )
        
        return created_sub
    
    async def get_subscription_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        return await self.subscription_repository.get_by_id(subscription_id)
    
    async def get_subscription_by_user_id(self, user_id: int) -> Optional[Subscription]:
        """Get subscription by user ID"""
        return await self.subscription_repository.get_by_user_id(user_id)
    
    async def get_all_subscriptions(self, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Get all subscriptions with pagination"""
        return await self.subscription_repository.get_all(skip, limit)
    
    async def get_active_subscriptions(self) -> List[Subscription]:
        """Get all active subscriptions"""
        return await self.subscription_repository.get_active_subscriptions()
    
    async def cancel_subscription(self, subscription_id: int) -> bool:
        """Cancel a subscription"""
        subscription = await self.subscription_repository.get_by_id(subscription_id)
        if not subscription:
            return False
        
        # Cancel subscription
        result = await self.subscription_repository.cancel_subscription(subscription_id)
        
        if result:
            # Update user's subscription type back to free
            await self.user_repository.update(
                subscription.user_id,
                {"subscription_type": SubscriptionType.FREE}
            )
        
        return result
    
    async def renew_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """Renew a subscription"""
        subscription = await self.subscription_repository.get_by_id(subscription_id)
        if not subscription:
            return None
        
        # Calculate new end date
        new_end_date = self._calculate_end_date(subscription.plan)
        
        # Update subscription
        updated_sub = await self.subscription_repository.update(
            subscription_id,
            {
                "status": SubscriptionStatus.ACTIVE,
                "end_date": new_end_date,
                "cancelled_at": None
            }
        )
        
        if updated_sub:
            # Update user's subscription type to premium
            await self.user_repository.update(
                subscription.user_id,
                {"subscription_type": SubscriptionType.PREMIUM}
            )
        
        return updated_sub
