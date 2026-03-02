from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.flashcard_repository_impl import SQLAlchemyFlashCardRepository
from app.application.services import FlashCardService
from app.domain.entities.flashcard import FlashCardCreate, FlashCardUpdate, FlashCardResponse
from app.domain.entities.user import User, UserRole
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/flashcards", tags=["Flash Cards"])


def get_flashcard_service(db: Session = Depends(get_db)) -> FlashCardService:
    flashcard_repo = SQLAlchemyFlashCardRepository(db)
    return FlashCardService(flashcard_repo)


@router.post("/", response_model=FlashCardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    flashcard_data: FlashCardCreate,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """Create a new flash card"""
    return await flashcard_service.create_flashcard(flashcard_data, current_user.id)


@router.get("/{flashcard_id}", response_model=FlashCardResponse)
async def get_flashcard(
    flashcard_id: int,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """Get a flash card by ID"""
    flashcard = await flashcard_service.get_flashcard(flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card not found"
        )
    return flashcard


@router.get("/", response_model=List[FlashCardResponse])
async def list_flashcards(
    skip: int = 0,
    limit: int = 100,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """List all flash cards"""
    return await flashcard_service.list_flashcards(skip, limit)


@router.get("/me/created", response_model=List[FlashCardResponse])
async def list_my_flashcards(
    skip: int = 0,
    limit: int = 100,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """List flash cards created by current user"""
    return await flashcard_service.list_flashcards_by_creator(current_user.id, skip, limit)


@router.put("/{flashcard_id}", response_model=FlashCardResponse)
async def update_flashcard(
    flashcard_id: int,
    flashcard_data: FlashCardUpdate,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """Update a flash card"""
    flashcard = await flashcard_service.get_flashcard(flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card not found"
        )

    # Allow admins or creators to update
    if flashcard.created_by and flashcard.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this flash card"
        )

    updated = await flashcard_service.update_flashcard(flashcard_id, flashcard_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update flash card"
        )
    return updated


@router.delete("/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard(
    flashcard_id: int,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a flash card"""
    flashcard = await flashcard_service.get_flashcard(flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card not found"
        )

    # Allow admins or creators to delete
    if flashcard.created_by and flashcard.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this flash card"
        )

    success = await flashcard_service.delete_flashcard(flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete flash card"
        )
    return None


@router.get("/admin/all", response_model=List[FlashCardResponse])
async def list_all_flashcards_admin(
    skip: int = 0,
    limit: int = 100,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_admin)
):
    """List all flash cards (Admin only)"""
    return await flashcard_service.list_flashcards(skip, limit)
