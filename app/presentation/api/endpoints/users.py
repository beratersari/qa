from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.application.services import UserService
from app.domain.entities.user import UserResponse, UserUpdate, UserRole
from app.domain.entities.user import User
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = SQLAlchemyUserRepository(db)
    return UserService(user_repo)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID (Admin or own profile)"""
    # Only admin can view other users' profiles
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
    return user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin)
):
    """List all users (Admin only)"""
    return await user_service.get_all_users(skip, limit)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
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
    return user


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
    return user


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
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
    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    role: UserRole,
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
    return user
