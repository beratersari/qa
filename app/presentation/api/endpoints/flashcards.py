from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.flashcard_repository_impl import (
    SQLAlchemyFlashCardRepository,
    SQLAlchemyFlashCardSetRepository,
    SQLAlchemyFlashCardSessionRepository,
    SQLAlchemyFlashCardProgressRepository
)
from app.application.services import FlashCardService, FlashCardSetService
from app.domain.entities.flashcard import (
    FlashCardCreate,
    FlashCardUpdate,
    FlashCardResponse,
    FlashCardSetCreate,
    FlashCardSetUpdate,
    FlashCardSetResponse,
    FlashCardSetAddFlashcard,
    FlashCardInSetResponse,
    FlashCardSessionResponse,
    FlashCardProgressUpdate,
    FlashCardProgressResponse
)
from app.domain.entities.user import User, UserRole
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/flashcards", tags=["Flash Cards"])


def get_flashcard_service(db: Session = Depends(get_db)) -> FlashCardService:
    flashcard_repo = SQLAlchemyFlashCardRepository(db)
    flashcard_set_repo = SQLAlchemyFlashCardSetRepository(db)
    flashcard_session_repo = SQLAlchemyFlashCardSessionRepository(db)
    flashcard_progress_repo = SQLAlchemyFlashCardProgressRepository(db)
    return FlashCardService(
        flashcard_repo,
        flashcard_set_repo,
        flashcard_session_repo,
        flashcard_progress_repo
    )


def get_flashcard_set_service(db: Session = Depends(get_db)) -> FlashCardSetService:
    flashcard_set_repo = SQLAlchemyFlashCardSetRepository(db)
    flashcard_session_repo = SQLAlchemyFlashCardSessionRepository(db)
    flashcard_progress_repo = SQLAlchemyFlashCardProgressRepository(db)
    return FlashCardSetService(
        flashcard_set_repo,
        flashcard_session_repo,
        flashcard_progress_repo
    )


# ==================== FLASHCARD SET ROUTES ====================
# NOTE: All /sets routes MUST be defined BEFORE any /{flashcard_id} routes
# to avoid "sets" being parsed as a flashcard_id parameter


@router.post("/sets", response_model=FlashCardSetResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard_set(
    set_data: FlashCardSetCreate,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Create a new flash card set"""
    flashcard_set = await flashcard_set_service.create_set(set_data, current_user.id)
    flashcard_count = await flashcard_set_service.get_flashcard_count_in_set(flashcard_set.id)
    return FlashCardSetResponse(
        id=flashcard_set.id,
        name=flashcard_set.name,
        description=flashcard_set.description,
        flashcard_count=flashcard_count,
        created_by=flashcard_set.created_by,
        created_at=flashcard_set.created_at,
        updated_at=flashcard_set.updated_at
    )


@router.get("/sets/{set_id}", response_model=FlashCardSetResponse)
async def get_flashcard_set(
    set_id: int,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Get a flash card set by ID"""
    flashcard_set = await flashcard_set_service.get_set(set_id)
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set not found"
        )
    flashcard_count = await flashcard_set_service.get_flashcard_count_in_set(set_id)
    return FlashCardSetResponse(
        id=flashcard_set.id,
        name=flashcard_set.name,
        description=flashcard_set.description,
        flashcard_count=flashcard_count,
        created_by=flashcard_set.created_by,
        created_at=flashcard_set.created_at,
        updated_at=flashcard_set.updated_at
    )


@router.get("/sets", response_model=List[FlashCardSetResponse])
async def list_flashcard_sets(
    skip: int = 0,
    limit: int = 100,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """List all flash card sets"""
    sets = await flashcard_set_service.list_sets(skip, limit)
    result = []
    for s in sets:
        flashcard_count = await flashcard_set_service.get_flashcard_count_in_set(s.id)
        result.append(FlashCardSetResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            flashcard_count=flashcard_count,
            created_by=s.created_by,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
    return result


@router.get("/sets/me/created", response_model=List[FlashCardSetResponse])
async def list_my_flashcard_sets(
    skip: int = 0,
    limit: int = 100,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """List flash card sets created by current user"""
    sets = await flashcard_set_service.list_sets_by_creator(current_user.id, skip, limit)
    result = []
    for s in sets:
        flashcard_count = await flashcard_set_service.get_flashcard_count_in_set(s.id)
        result.append(FlashCardSetResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            flashcard_count=flashcard_count,
            created_by=s.created_by,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
    return result


@router.put("/sets/{set_id}", response_model=FlashCardSetResponse)
async def update_flashcard_set(
    set_id: int,
    set_data: FlashCardSetUpdate,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Update a flash card set"""
    flashcard_set = await flashcard_set_service.get_set(set_id)
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set not found"
        )
    if flashcard_set.created_by and flashcard_set.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this flash card set"
        )
    updated = await flashcard_set_service.update_set(set_id, set_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update flash card set"
        )
    flashcard_count = await flashcard_set_service.get_flashcard_count_in_set(set_id)
    return FlashCardSetResponse(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        flashcard_count=flashcard_count,
        created_by=updated.created_by,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard_set(
    set_id: int,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a flash card set"""
    flashcard_set = await flashcard_set_service.get_set(set_id)
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set not found"
        )
    if flashcard_set.created_by and flashcard_set.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this flash card set"
        )
    success = await flashcard_set_service.delete_set(set_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete flash card set"
        )
    return None


@router.post("/sets/{set_id}/flashcards", status_code=status.HTTP_201_CREATED)
async def add_flashcard_to_set(
    set_id: int,
    data: FlashCardSetAddFlashcard,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Add a flash card to a set"""
    flashcard = await flashcard_service.get_flashcard(data.flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card not found"
        )
    flashcard_set = await flashcard_set_service.get_set(set_id)
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set not found"
        )
    if flashcard_set.created_by and flashcard_set.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this flash card set"
        )
    success, already_in_set = await flashcard_set_service.add_flashcard_to_set(set_id, data.flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set or flash card not found"
        )
    if already_in_set:
        return {"message": "Flash card is already in this set"}
    return {"message": "Flash card added to set successfully"}


@router.delete("/sets/{set_id}/flashcards/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_flashcard_from_set(
    set_id: int,
    flashcard_id: int,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Remove a flash card from a set"""
    flashcard_set = await flashcard_set_service.get_set(set_id)
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set not found"
        )
    if flashcard_set.created_by and flashcard_set.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this flash card set"
        )
    success = await flashcard_set_service.remove_flashcard_from_set(set_id, flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card not found in set"
        )
    return None


@router.delete("/sets/{set_id}/flashcards/{flashcard_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard_from_set(
    set_id: int,
    flashcard_id: int,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a flash card owned by the current user"""
    flashcard_set = await flashcard_set_service.get_set(set_id)
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set not found"
        )
    flashcard = await flashcard_service.get_flashcard(flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card not found"
        )
    if flashcard.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this flash card"
        )
    await flashcard_set_service.remove_flashcard_from_set(set_id, flashcard_id)
    success = await flashcard_service.delete_flashcard(flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete flash card"
        )
    return None


@router.get("/sets/{set_id}/flashcards", response_model=List[FlashCardInSetResponse])
async def get_flashcards_in_set(
    set_id: int,
    skip: int = 0,
    limit: int = 100,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Get all flash cards in a set"""
    flashcards = await flashcard_set_service.get_flashcards_in_set(set_id, skip, limit)
    return [FlashCardInSetResponse(**card) for card in flashcards]


@router.post("/sets/{set_id}/sessions", response_model=FlashCardSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_flashcard_session(
    set_id: int,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Start a flash card session for a set"""
    flashcard_set = await flashcard_set_service.get_set(set_id)
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flash card set not found"
        )
    session = await flashcard_set_service.start_session(current_user.id, set_id)
    return FlashCardSessionResponse(**session)


@router.post("/sets/{set_id}/progress", response_model=FlashCardProgressResponse, status_code=status.HTTP_201_CREATED)
async def update_flashcard_progress(
    set_id: int,
    data: FlashCardProgressUpdate,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Update flash card knowledge status for a set"""
    progress = await flashcard_set_service.update_progress(
        current_user.id,
        set_id,
        data.flashcard_id,
        data.status
    )
    return FlashCardProgressResponse(**progress)


@router.get("/sets/{set_id}/progress", response_model=List[FlashCardProgressResponse])
async def get_flashcard_progress(
    set_id: int,
    flashcard_set_service: FlashCardSetService = Depends(get_flashcard_set_service),
    current_user: User = Depends(get_current_user)
):
    """Get flash card progress for a set"""
    progress = await flashcard_set_service.get_progress(current_user.id, set_id)
    return [FlashCardProgressResponse(**item) for item in progress]


# ==================== INDIVIDUAL FLASHCARD ROUTES ====================
# These routes with dynamic parameters must come AFTER all /sets routes


@router.post("/", response_model=FlashCardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    flashcard_data: FlashCardCreate,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """Create a new flash card"""
    return await flashcard_service.create_flashcard(flashcard_data, current_user.id)


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


@router.get("/admin/all", response_model=List[FlashCardResponse])
async def list_all_flashcards_admin(
    skip: int = 0,
    limit: int = 100,
    flashcard_service: FlashCardService = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_admin)
):
    """List all flash cards (Admin only)"""
    return await flashcard_service.list_flashcards(skip, limit)


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
