from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.question_repository_impl import SQLAlchemyQuestionSetRepository
from app.application.services import QuestionSetService
from app.domain.entities.question import (
    QuestionSetCreate,
    QuestionSetUpdate,
    QuestionSetResponse,
    QuestionSetAddQuestion,
    QuestionInSetResponse,
    QuestionSetType
)
from app.domain.entities.user import User
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/question-sets", tags=["Question Sets"])


def get_question_set_service(db: Session = Depends(get_db)) -> QuestionSetService:
    question_set_repo = SQLAlchemyQuestionSetRepository(db)
    return QuestionSetService(question_set_repo)


@router.post("/", response_model=QuestionSetResponse, status_code=status.HTTP_201_CREATED)
async def create_question_set(
    set_data: QuestionSetCreate,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_admin)
):
    """Create a new question set (Admin only)"""
    question_set = await question_set_service.create_set(set_data, current_user.id)
    question_count = await question_set_service.get_question_count_in_set(question_set.id)
    return QuestionSetResponse(
        id=question_set.id,
        name=question_set.name,
        description=question_set.description,
        set_type=question_set.set_type,
        question_count=question_count,
        created_by=question_set.created_by,
        created_at=question_set.created_at,
        updated_at=question_set.updated_at
    )


@router.get("/{set_id}", response_model=QuestionSetResponse)
async def get_question_set(
    set_id: int,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_user)
):
    """Get a question set by ID"""
    question_set = await question_set_service.get_set(set_id)
    if not question_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question set not found"
        )
    question_count = await question_set_service.get_question_count_in_set(set_id)
    return QuestionSetResponse(
        id=question_set.id,
        name=question_set.name,
        description=question_set.description,
        set_type=question_set.set_type,
        question_count=question_count,
        created_by=question_set.created_by,
        created_at=question_set.created_at,
        updated_at=question_set.updated_at
    )


@router.get("/", response_model=List[QuestionSetResponse])
async def list_question_sets(
    skip: int = 0,
    limit: int = 100,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_user)
):
    """List all question sets"""
    sets = await question_set_service.list_sets(skip, limit)
    result = []
    for s in sets:
        question_count = await question_set_service.get_question_count_in_set(s.id)
        result.append(QuestionSetResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            set_type=s.set_type,
            question_count=question_count,
            created_by=s.created_by,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
    return result


@router.get("/type/{set_type}", response_model=List[QuestionSetResponse])
async def list_question_sets_by_type(
    set_type: QuestionSetType,
    skip: int = 0,
    limit: int = 100,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_user)
):
    """List question sets by type (normal/premium)"""
    sets = await question_set_service.list_sets_by_type(set_type, skip, limit)
    result = []
    for s in sets:
        question_count = await question_set_service.get_question_count_in_set(s.id)
        result.append(QuestionSetResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            set_type=s.set_type,
            question_count=question_count,
            created_by=s.created_by,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
    return result


@router.put("/{set_id}", response_model=QuestionSetResponse)
async def update_question_set(
    set_id: int,
    set_data: QuestionSetUpdate,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_admin)
):
    """Update a question set (Admin only)"""
    updated = await question_set_service.update_set(set_id, set_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question set not found"
        )
    question_count = await question_set_service.get_question_count_in_set(set_id)
    return QuestionSetResponse(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        set_type=updated.set_type,
        question_count=question_count,
        created_by=updated.created_by,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_set(
    set_id: int,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_admin)
):
    """Delete a question set (Admin only)"""
    success = await question_set_service.delete_set(set_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question set not found"
        )
    return None


@router.post("/{set_id}/questions", status_code=status.HTTP_201_CREATED)
async def add_question_to_set(
    set_id: int,
    data: QuestionSetAddQuestion,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_admin)
):
    """Add a question to a set (Admin only)"""
    success, already_in_set = await question_set_service.add_question_to_set(set_id, data.question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question set or question not found"
        )
    if already_in_set:
        return {"message": "Question is already in this set"}
    return {"message": "Question added to set successfully"}


@router.delete("/{set_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_question_from_set(
    set_id: int,
    question_id: int,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_admin)
):
    """Remove a question from a set (Admin only)"""
    success = await question_set_service.remove_question_from_set(set_id, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in set"
        )
    return None


@router.get("/{set_id}/questions", response_model=List[QuestionInSetResponse])
async def get_questions_in_set(
    set_id: int,
    skip: int = 0,
    limit: int = 100,
    question_set_service: QuestionSetService = Depends(get_question_set_service),
    current_user: User = Depends(get_current_user)
):
    """Get all questions in a set (without answers)"""
    questions = await question_set_service.get_questions_in_set(set_id, skip, limit)
    return [QuestionInSetResponse(**q) for q in questions]
