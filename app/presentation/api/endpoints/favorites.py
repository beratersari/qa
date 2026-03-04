from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.favorite_repository_impl import SQLAlchemyFavoriteListRepository, SQLAlchemyFavoriteItemRepository
from app.infrastructure.database.question_repository_impl import SQLAlchemyQuestionRepository
from app.infrastructure.database.flashcard_repository_impl import SQLAlchemyFlashCardRepository
from app.application.services import FavoriteService
from app.domain.entities.favorite import (
    FavoriteListCreate,
    FavoriteListUpdate,
    FavoriteListResponse,
    AddQuestionToFavorite,
    AddFlashcardToFavorite,
    FavoriteQuestionResponse,
    FavoriteFlashcardResponse
)
from app.domain.entities.user import User, UserRole
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/favorites", tags=["Favorites"])


def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    favorite_list_repo = SQLAlchemyFavoriteListRepository(db)
    favorite_item_repo = SQLAlchemyFavoriteItemRepository(db)
    return FavoriteService(favorite_list_repo, favorite_item_repo)


def get_question_service(db: Session = Depends(get_db)):
    from app.application.services import QuestionService
    question_repo = SQLAlchemyQuestionRepository(db)
    return QuestionService(question_repo)


def get_flashcard_service(db: Session = Depends(get_db)):
    from app.application.services import FlashCardService
    flashcard_repo = SQLAlchemyFlashCardRepository(db)
    return FlashCardService(flashcard_repo)


def can_view_favorite_list(current_user: User, favorite_list) -> bool:
    if current_user.role == UserRole.ADMIN or favorite_list.user_id == current_user.id:
        return True
    privacy = favorite_list.privacy.value if hasattr(favorite_list.privacy, "value") else favorite_list.privacy
    if privacy == "public":
        return True
    if privacy == "shared" and current_user.username in (favorite_list.shared_with_usernames or []):
        return True
    return False


@router.post("/lists", response_model=FavoriteListResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite_list(
    list_data: FavoriteListCreate,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Create a new favorite list"""
    favorite_list = await favorite_service.create_favorite_list(list_data, current_user.id)
    question_count = await favorite_service.get_question_count(favorite_list.id)
    flashcard_count = await favorite_service.get_flashcard_count(favorite_list.id)
    return FavoriteListResponse(
        id=favorite_list.id,
        name=favorite_list.name,
        description=favorite_list.description,
        user_id=favorite_list.user_id,
        is_default=favorite_list.is_default,
        privacy=favorite_list.privacy,
        shared_with_usernames=favorite_list.shared_with_usernames,
        question_count=question_count,
        flashcard_count=flashcard_count,
        created_at=favorite_list.created_at,
        updated_at=favorite_list.updated_at
    )


@router.get("/lists", response_model=List[FavoriteListResponse])
async def get_my_favorite_lists(
    skip: int = 0,
    limit: int = 100,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Get all favorite lists for the current user"""
    lists = await favorite_service.get_user_favorite_lists(current_user.id, skip, limit)
    result = []
    for lst in lists:
        question_count = await favorite_service.get_question_count(lst.id)
        flashcard_count = await favorite_service.get_flashcard_count(lst.id)
        result.append(FavoriteListResponse(
            id=lst.id,
            name=lst.name,
            description=lst.description,
            user_id=lst.user_id,
            is_default=lst.is_default,
            privacy=lst.privacy,
            shared_with_usernames=lst.shared_with_usernames,
            question_count=question_count,
            flashcard_count=flashcard_count,
            created_at=lst.created_at,
            updated_at=lst.updated_at
        ))
    return result


@router.get("/lists/default", response_model=FavoriteListResponse)
async def get_default_favorite_list(
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Get the default favorite list for the current user"""
    favorite_list = await favorite_service.get_default_favorite_list(current_user.id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Default favorite list not found"
        )
    question_count = await favorite_service.get_question_count(favorite_list.id)
    flashcard_count = await favorite_service.get_flashcard_count(favorite_list.id)
    return FavoriteListResponse(
        id=favorite_list.id,
        name=favorite_list.name,
        description=favorite_list.description,
        user_id=favorite_list.user_id,
        is_default=favorite_list.is_default,
        privacy=favorite_list.privacy,
        shared_with_usernames=favorite_list.shared_with_usernames,
        question_count=question_count,
        flashcard_count=flashcard_count,
        created_at=favorite_list.created_at,
        updated_at=favorite_list.updated_at
    )


@router.get("/lists/{list_id}", response_model=FavoriteListResponse)
async def get_favorite_list(
    list_id: int,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Get a specific favorite list by ID"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    if not can_view_favorite_list(current_user, favorite_list):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this favorite list"
        )
    
    question_count = await favorite_service.get_question_count(list_id)
    flashcard_count = await favorite_service.get_flashcard_count(list_id)
    return FavoriteListResponse(
        id=favorite_list.id,
        name=favorite_list.name,
        description=favorite_list.description,
        user_id=favorite_list.user_id,
        is_default=favorite_list.is_default,
        privacy=favorite_list.privacy,
        shared_with_usernames=favorite_list.shared_with_usernames,
        question_count=question_count,
        flashcard_count=flashcard_count,
        created_at=favorite_list.created_at,
        updated_at=favorite_list.updated_at
    )


@router.put("/lists/{list_id}", response_model=FavoriteListResponse)
async def update_favorite_list(
    list_id: int,
    list_data: FavoriteListUpdate,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Update a favorite list (owner or admin only)"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    # Check ownership (admin can edit any list)
    if current_user.role != UserRole.ADMIN and favorite_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this favorite list"
        )
    
    updated_list = await favorite_service.update_favorite_list(list_id, list_data)
    question_count = await favorite_service.get_question_count(list_id)
    flashcard_count = await favorite_service.get_flashcard_count(list_id)
    return FavoriteListResponse(
        id=updated_list.id,
        name=updated_list.name,
        description=updated_list.description,
        user_id=updated_list.user_id,
        is_default=updated_list.is_default,
        privacy=updated_list.privacy,
        shared_with_usernames=updated_list.shared_with_usernames,
        question_count=question_count,
        flashcard_count=flashcard_count,
        created_at=updated_list.created_at,
        updated_at=updated_list.updated_at
    )


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite_list(
    list_id: int,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a favorite list (owner or admin only, cannot delete default list)"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    # Check ownership (admin can delete any list)
    if current_user.role != UserRole.ADMIN and favorite_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this favorite list"
        )
    
    # Cannot delete default list
    if favorite_list.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the default favorite list"
        )
    
    success = await favorite_service.delete_favorite_list(list_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete favorite list"
        )
    return None


@router.post("/lists/{list_id}/questions", status_code=status.HTTP_201_CREATED)
async def add_question_to_favorite_list(
    list_id: int,
    data: AddQuestionToFavorite,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    question_service = Depends(get_question_service),
    current_user: User = Depends(get_current_user)
):
    """Add a question to a favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    # Check ownership (admin can add to any list)
    if current_user.role != UserRole.ADMIN and favorite_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this favorite list"
        )
    
    # Check if question exists
    question = await question_service.get_question(data.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    success, already_in_list = await favorite_service.add_question_to_list(list_id, data.question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add question to favorite list"
        )
    
    if already_in_list:
        return {"message": "Question is already in this favorite list"}
    return {"message": "Question added to favorite list successfully"}


@router.post("/lists/{list_id}/flashcards", status_code=status.HTTP_201_CREATED)
async def add_flashcard_to_favorite_list(
    list_id: int,
    data: AddFlashcardToFavorite,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    flashcard_service = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_user)
):
    """Add a flashcard to a favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )

    # Check ownership (admin can add to any list)
    if current_user.role != UserRole.ADMIN and favorite_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this favorite list"
        )

    # Check if flashcard exists
    flashcard = await flashcard_service.get_flashcard(data.flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )

    success, already_in_list = await favorite_service.add_flashcard_to_list(list_id, data.flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add flashcard to favorite list"
        )

    if already_in_list:
        return {"message": "Flashcard is already in this favorite list"}
    return {"message": "Flashcard added to favorite list successfully"}


@router.delete("/lists/{list_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_question_from_favorite_list(
    list_id: int,
    question_id: int,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Remove a question from a favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    # Check ownership (admin can remove from any list)
    if current_user.role != UserRole.ADMIN and favorite_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this favorite list"
        )
    
    success = await favorite_service.remove_question_from_list(list_id, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this favorite list"
        )
    return None


@router.delete("/lists/{list_id}/flashcards/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_flashcard_from_favorite_list(
    list_id: int,
    flashcard_id: int,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Remove a flashcard from a favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )

    # Check ownership (admin can remove from any list)
    if current_user.role != UserRole.ADMIN and favorite_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this favorite list"
        )

    success = await favorite_service.remove_flashcard_from_list(list_id, flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found in this favorite list"
        )
    return None


@router.get("/lists/{list_id}/questions", response_model=List[FavoriteQuestionResponse])
async def get_questions_in_favorite_list(
    list_id: int,
    skip: int = 0,
    limit: int = 100,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Get all questions in a favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    if not can_view_favorite_list(current_user, favorite_list):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this favorite list"
        )
    
    questions = await favorite_service.get_questions_in_list(list_id, skip, limit)
    return [FavoriteQuestionResponse(**q) for q in questions]


@router.get("/lists/{list_id}/flashcards", response_model=List[FavoriteFlashcardResponse])
async def get_flashcards_in_favorite_list(
    list_id: int,
    skip: int = 0,
    limit: int = 100,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_user)
):
    """Get all flashcards in a favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )

    if not can_view_favorite_list(current_user, favorite_list):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this favorite list"
        )

    flashcards = await favorite_service.get_flashcards_in_list(list_id, skip, limit)
    return [FavoriteFlashcardResponse(**f) for f in flashcards]


# Admin endpoints for managing any user's favorites
@router.get("/admin/users/{user_id}/lists", response_model=List[FavoriteListResponse])
async def admin_get_user_favorite_lists(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Get all favorite lists for a specific user"""
    lists = await favorite_service.get_user_favorite_lists(user_id, skip, limit)
    result = []
    for lst in lists:
        question_count = await favorite_service.get_question_count(lst.id)
        flashcard_count = await favorite_service.get_flashcard_count(lst.id)
        result.append(FavoriteListResponse(
            id=lst.id,
            name=lst.name,
            description=lst.description,
            user_id=lst.user_id,
            is_default=lst.is_default,
            privacy=lst.privacy,
            shared_with_usernames=lst.shared_with_usernames,
            question_count=question_count,
            flashcard_count=flashcard_count,
            created_at=lst.created_at,
            updated_at=lst.updated_at
        ))
    return result


@router.post("/admin/lists/{list_id}/questions", status_code=status.HTTP_201_CREATED)
async def admin_add_question_to_favorite_list(
    list_id: int,
    data: AddQuestionToFavorite,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    question_service = Depends(get_question_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Add a question to any user's favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    # Check if question exists
    question = await question_service.get_question(data.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    success, already_in_list = await favorite_service.add_question_to_list(list_id, data.question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add question to favorite list"
        )
    
    if already_in_list:
        return {"message": "Question is already in this favorite list"}
    return {"message": "Question added to favorite list successfully"}


@router.post("/admin/lists/{list_id}/flashcards", status_code=status.HTTP_201_CREATED)
async def admin_add_flashcard_to_favorite_list(
    list_id: int,
    data: AddFlashcardToFavorite,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    flashcard_service = Depends(get_flashcard_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Add a flashcard to any user's favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )

    # Check if flashcard exists
    flashcard = await flashcard_service.get_flashcard(data.flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )

    success, already_in_list = await favorite_service.add_flashcard_to_list(list_id, data.flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add flashcard to favorite list"
        )

    if already_in_list:
        return {"message": "Flashcard is already in this favorite list"}
    return {"message": "Flashcard added to favorite list successfully"}


@router.put("/admin/lists/{list_id}", response_model=FavoriteListResponse)
async def admin_update_favorite_list(
    list_id: int,
    list_data: FavoriteListUpdate,
    favorite_service: FavoriteService = Depends(get_favorite_service),
    current_user: User = Depends(get_current_admin)
):
    """Admin: Update any user's favorite list"""
    favorite_list = await favorite_service.get_favorite_list(list_id)
    if not favorite_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite list not found"
        )
    
    updated_list = await favorite_service.update_favorite_list(list_id, list_data)
    question_count = await favorite_service.get_question_count(list_id)
    flashcard_count = await favorite_service.get_flashcard_count(list_id)
    return FavoriteListResponse(
        id=updated_list.id,
        name=updated_list.name,
        description=updated_list.description,
        user_id=updated_list.user_id,
        is_default=updated_list.is_default,
        privacy=updated_list.privacy,
        shared_with_usernames=updated_list.shared_with_usernames,
        question_count=question_count,
        flashcard_count=flashcard_count,
        created_at=updated_list.created_at,
        updated_at=updated_list.updated_at
    )
