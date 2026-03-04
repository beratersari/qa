from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.badge_repository_impl import SQLAlchemyBadgeRepository, SQLAlchemyUserBadgeRepository
from app.application.services import BadgeService
from app.domain.entities.badge import BadgeCreate, BadgeUpdate, BadgeResponse, UserBadgeResponse
from app.domain.entities.user import User, UserRole
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/badges", tags=["Badges"])


def get_badge_service(db: Session = Depends(get_db)) -> BadgeService:
    badge_repo = SQLAlchemyBadgeRepository(db)
    user_badge_repo = SQLAlchemyUserBadgeRepository(db)
    return BadgeService(badge_repo, user_badge_repo)


def _build_user_badge_response(user_badge, badge) -> UserBadgeResponse:
    return UserBadgeResponse(
        id=user_badge.id,
        user_id=user_badge.user_id,
        badge=BadgeResponse(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            icon_path=badge.icon_path,
            conditions=badge.conditions,
            created_at=badge.created_at,
            updated_at=badge.updated_at
        ),
        current_progress=user_badge.current_progress,
        is_completed=user_badge.is_completed,
        completed_at=user_badge.completed_at,
        created_at=user_badge.created_at,
        updated_at=user_badge.updated_at
    )


@router.get("/", response_model=List[BadgeResponse])
async def list_badges(
    skip: int = 0,
    limit: int = 100,
    badge_service: BadgeService = Depends(get_badge_service),
    current_user: User = Depends(get_current_user)
):
    """List all badges"""
    badges = await badge_service.list_badges(skip, limit)
    return [
        BadgeResponse(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            icon_path=badge.icon_path,
            conditions=badge.conditions,
            created_at=badge.created_at,
            updated_at=badge.updated_at
        )
        for badge in badges
    ]


@router.post("/", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
async def create_badge(
    badge_data: BadgeCreate,
    badge_service: BadgeService = Depends(get_badge_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Create a badge"""
    badge = await badge_service.create_badge(badge_data)
    return BadgeResponse(
        id=badge.id,
        name=badge.name,
        description=badge.description,
        icon_path=badge.icon_path,
        conditions=badge.conditions,
        created_at=badge.created_at,
        updated_at=badge.updated_at
    )


@router.put("/{badge_id}", response_model=BadgeResponse)
async def update_badge(
    badge_id: int,
    badge_data: BadgeUpdate,
    badge_service: BadgeService = Depends(get_badge_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Update badge"""
    badge = await badge_service.update_badge(badge_id, badge_data)
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )
    return BadgeResponse(
        id=badge.id,
        name=badge.name,
        description=badge.description,
        icon_path=badge.icon_path,
        conditions=badge.conditions,
        created_at=badge.created_at,
        updated_at=badge.updated_at
    )


@router.delete("/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_badge(
    badge_id: int,
    badge_service: BadgeService = Depends(get_badge_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Delete badge"""
    success = await badge_service.delete_badge(badge_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )
    return None


@router.get("/me", response_model=List[UserBadgeResponse])
async def get_my_badges(
    skip: int = 0,
    limit: int = 100,
    badge_service: BadgeService = Depends(get_badge_service),
    current_user: User = Depends(get_current_user)
):
    """Get current user's badge progress"""
    user_badges = await badge_service.list_user_badges(current_user.id, skip, limit)
    if not user_badges:
        return []

    # Fetch badge details for each user badge
    results = []
    for user_badge in user_badges:
        badge = await badge_service.get_badge(user_badge.badge_id)
        if badge:
            results.append(_build_user_badge_response(user_badge, badge))
    return results


@router.get("/users/{user_id}", response_model=List[UserBadgeResponse])
async def get_user_badges(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    badge_service: BadgeService = Depends(get_badge_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Get badge progress for a user"""
    user_badges = await badge_service.list_user_badges(user_id, skip, limit)
    if not user_badges:
        return []

    results = []
    for user_badge in user_badges:
        badge = await badge_service.get_badge(user_badge.badge_id)
        if badge:
            results.append(_build_user_badge_response(user_badge, badge))
    return results
