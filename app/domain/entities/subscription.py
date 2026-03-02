from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class SubscriptionPlan(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Subscription(BaseModel):
    """Subscription domain entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    user_id: int
    plan: SubscriptionPlan
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime
    auto_renew: bool = True
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None


class SubscriptionCreate(BaseModel):
    """DTO for creating a subscription"""
    user_id: int
    plan: SubscriptionPlan
    auto_renew: bool = True
    payment_method: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    """DTO for updating a subscription"""
    status: Optional[SubscriptionStatus] = None
    auto_renew: Optional[bool] = None
    end_date: Optional[datetime] = None


class SubscriptionResponse(BaseModel):
    """DTO for subscription response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    plan: SubscriptionPlan
    status: SubscriptionStatus
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    created_at: datetime
    cancelled_at: Optional[datetime]
