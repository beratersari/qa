from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.infrastructure.database.subscription_repository_impl import SQLAlchemySubscriptionRepository
from app.application.services import SubscriptionService
from app.domain.entities.subscription import (
    SubscriptionCreate, SubscriptionResponse, SubscriptionPlan
)
from app.domain.entities.user import User, UserRole
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    subscription_repo = SQLAlchemySubscriptionRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    return SubscriptionService(subscription_repo, user_repo)


@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_admin)
):
    """Create a new subscription (Admin only)"""
    subscription = await subscription_service.create_subscription(subscription_data)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create subscription. User may not exist or already has an active subscription."
        )
    return subscription


@router.get("/my-subscription", response_model=SubscriptionResponse)
async def get_my_subscription(
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription"""
    subscription = await subscription_service.get_subscription_by_user_id(current_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    return subscription


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_user)
):
    """Get subscription by ID (Admin or subscription owner)"""
    subscription = await subscription_service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Only admin or subscription owner can view
    if current_user.role != UserRole.ADMIN and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this subscription"
        )
    
    return subscription


@router.get("/", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    skip: int = 0,
    limit: int = 100,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_admin)
):
    """List all subscriptions (Admin only)"""
    return await subscription_service.get_all_subscriptions(skip, limit)


@router.get("/status/active", response_model=List[SubscriptionResponse])
async def list_active_subscriptions(
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_admin)
):
    """List all active subscriptions (Admin only)"""
    return await subscription_service.get_active_subscriptions()


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: int,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_user)
):
    """Cancel a subscription (Admin or subscription owner)"""
    # Get subscription first to check ownership
    subscription = await subscription_service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Only admin or subscription owner can cancel
    if current_user.role != UserRole.ADMIN and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this subscription"
        )
    
    success = await subscription_service.cancel_subscription(subscription_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not cancel subscription"
        )
    
    # Return updated subscription
    updated = await subscription_service.get_subscription_by_id(subscription_id)
    return updated


@router.post("/{subscription_id}/renew", response_model=SubscriptionResponse)
async def renew_subscription(
    subscription_id: int,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_admin)
):
    """Renew a subscription (Admin only)"""
    subscription = await subscription_service.renew_subscription(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found or could not be renewed"
        )
    return subscription


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe_current_user(
    plan: SubscriptionPlan,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    current_user: User = Depends(get_current_user)
):
    """Subscribe current user to a plan"""
    subscription_data = SubscriptionCreate(
        user_id=current_user.id,
        plan=plan,
        auto_renew=True
    )
    
    subscription = await subscription_service.create_subscription(subscription_data)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create subscription. You may already have an active subscription."
        )
    return subscription
