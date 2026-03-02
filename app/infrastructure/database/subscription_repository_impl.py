from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.subscription import Subscription, SubscriptionStatus
from app.domain.repositories.subscription_repository import SubscriptionRepository
from app.infrastructure.database.models import SubscriptionModel


class SQLAlchemySubscriptionRepository(SubscriptionRepository):
    """SQLAlchemy implementation of SubscriptionRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: SubscriptionModel) -> Subscription:
        """Convert database model to domain entity"""
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            plan=model.plan,
            status=model.status,
            start_date=model.start_date,
            end_date=model.end_date,
            auto_renew=model.auto_renew,
            payment_method=model.payment_method,
            transaction_id=model.transaction_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            cancelled_at=model.cancelled_at
        )
    
    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription"""
        db_subscription = SubscriptionModel(
            user_id=subscription.user_id,
            plan=subscription.plan,
            status=subscription.status,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            auto_renew=subscription.auto_renew,
            payment_method=subscription.payment_method,
            transaction_id=subscription.transaction_id
        )
        self.db.add(db_subscription)
        self.db.commit()
        self.db.refresh(db_subscription)
        return self._to_entity(db_subscription)
    
    async def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        db_sub = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_sub:
            return self._to_entity(db_sub)
        return None
    
    async def get_by_user_id(self, user_id: int) -> Optional[Subscription]:
        """Get subscription by user ID"""
        db_sub = self.db.query(SubscriptionModel).filter(SubscriptionModel.user_id == user_id).first()
        if db_sub:
            return self._to_entity(db_sub)
        return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Get all subscriptions with pagination"""
        db_subs = self.db.query(SubscriptionModel).offset(skip).limit(limit).all()
        return [self._to_entity(sub) for sub in db_subs]
    
    async def get_active_subscriptions(self) -> List[Subscription]:
        """Get all active subscriptions"""
        db_subs = self.db.query(SubscriptionModel).filter(
            SubscriptionModel.status == SubscriptionStatus.ACTIVE
        ).all()
        return [self._to_entity(sub) for sub in db_subs]
    
    async def update(self, subscription_id: int, subscription_data: dict) -> Optional[Subscription]:
        """Update subscription by ID"""
        db_sub = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if not db_sub:
            return None
        
        for key, value in subscription_data.items():
            if hasattr(db_sub, key):
                setattr(db_sub, key, value)
        
        db_sub.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_sub)
        return self._to_entity(db_sub)
    
    async def delete(self, subscription_id: int) -> bool:
        """Delete subscription by ID"""
        db_sub = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if not db_sub:
            return False
        
        self.db.delete(db_sub)
        self.db.commit()
        return True
    
    async def cancel_subscription(self, subscription_id: int) -> bool:
        """Cancel a subscription"""
        db_sub = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if not db_sub:
            return False
        
        db_sub.status = SubscriptionStatus.CANCELLED
        db_sub.auto_renew = False
        db_sub.cancelled_at = datetime.utcnow()
        db_sub.updated_at = datetime.utcnow()
        self.db.commit()
        return True
