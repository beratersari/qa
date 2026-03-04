from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.infrastructure.database.badge_repository_impl import SQLAlchemyBadgeRepository, SQLAlchemyUserBadgeRepository
from app.application.services import UserService, BadgeService
from app.domain.entities.user import (
    UserResponse, UserUpdate, UserRole, UserProfileUpdate,
    PublicUserProfileResponse, ProfileVisibility
)
from app.domain.entities.user import User
from app.domain.entities.badge import BadgeResponse, UserBadgeResponse
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = SQLAlchemyUserRepository(db)
    return UserService(user_repo)


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


async def _get_user_badges(user_id: int, badge_service: BadgeService) -> List[UserBadgeResponse]:
    user_badges = await badge_service.list_user_badges(user_id)
    if not user_badges:
        return []
    results = []
    for user_badge in user_badges:
        badge = await badge_service.get_badge(user_badge.badge_id)
        if badge:
            results.append(_build_user_badge_response(user_badge, badge))
    return results


async def _user_to_response(user: User, badge_service: BadgeService) -> UserResponse:
    """Helper to convert User to UserResponse"""
    badges = await _get_user_badges(user.id, badge_service)
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        subscription_type=user.subscription_type,
        total_xp=user.total_xp,
        level=user.level,
        challenge_streak=user.challenge_streak,
        longest_challenge_streak=user.longest_challenge_streak,
        profile_image_path=user.profile_image_path,
        bio=user.bio,
        contact_info=user.contact_info,
        profile_visibility=user.profile_visibility,
        badges=badges,
        created_at=user.created_at,
        last_login=user.last_login
    )


async def _user_to_public_profile(user: User, badge_service: BadgeService) -> PublicUserProfileResponse:
    """Helper to convert User to PublicUserProfileResponse"""
    badges = await _get_user_badges(user.id, badge_service)
    return PublicUserProfileResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        profile_image_path=user.profile_image_path,
        bio=user.bio,
        subscription_type=user.subscription_type,
        badges=badges,
        level=user.level,
        challenge_streak=user.challenge_streak,
        longest_challenge_streak=user.longest_challenge_streak,
        created_at=user.created_at
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    badge_service: BadgeService = Depends(get_badge_service),
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return await _user_to_response(current_user, badge_service)


@router.put("/me/profile", response_model=UserResponse)
async def update_own_profile(
    profile_data: UserProfileUpdate,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    user = await user_service.update_user_profile(current_user.id, profile_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await _user_to_response(user, badge_service)


@router.get("/profile/{username}", response_model=PublicUserProfileResponse)
async def get_public_user_profile(
    username: str,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """Get a user's public profile by username. Only shows profile if visibility is public."""
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check profile visibility
    visibility = user.profile_visibility.value if hasattr(user.profile_visibility, "value") else user.profile_visibility
    is_owner = current_user.id == user.id
    is_admin = current_user.role == UserRole.ADMIN

    if visibility == "private" and not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private"
        )

    return await _user_to_public_profile(user, badge_service)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID (Admin or own profile)"""
    # Only admin can view other users' full profiles
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await _user_to_response(user, badge_service)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin)
):
    """List all users (Admin only)"""
    users = await user_service.get_all_users(skip, limit)
    return [await _user_to_response(user, badge_service) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """Update user information (Admin or own profile)"""
    # Only admin can update other users' profiles
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await _user_to_response(user, badge_service)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin)
):
    """Delete a user (Admin only)"""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin)
):
    """Deactivate a user account (Admin only)"""
    user = await user_service.deactivate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await _user_to_response(user, badge_service)


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin)
):
    """Activate a user account (Admin only)"""
    user = await user_service.activate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await _user_to_response(user, badge_service)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    role: UserRole,
    badge_service: BadgeService = Depends(get_badge_service),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin)
):
    """Change user role (Admin only)"""
    user = await user_service.change_user_role(user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await _user_to_response(user, badge_service)
