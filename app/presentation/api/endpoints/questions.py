from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.question_repository_impl import SQLAlchemyQuestionRepository
from app.application.services import QuestionService
from app.domain.entities.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionAnswerResponse
)
from app.domain.entities.user import User
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/questions", tags=["Questions"])


def get_question_service(db: Session = Depends(get_db)) -> QuestionService:
    question_repo = SQLAlchemyQuestionRepository(db)
    return QuestionService(question_repo)


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    question_service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_admin)
):
    """Create a new question (Admin only)"""
    question = await question_service.create_question(question_data, current_user.id)
    return QuestionResponse(
        id=question.id,
        prompt=question.prompt,
        choices=question.get_choices_with_letters(),
        difficulty_level=question.difficulty_level,
        created_by=question.created_by,
        created_at=question.created_at,
        updated_at=question.updated_at
    )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    question_service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_user)
):
    """Get a question by ID (without answer)"""
    question = await question_service.get_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return QuestionResponse(
        id=question.id,
        prompt=question.prompt,
        choices=question.get_choices_with_letters(),
        difficulty_level=question.difficulty_level,
        created_by=question.created_by,
        created_at=question.created_at,
        updated_at=question.updated_at
    )


@router.get("/", response_model=List[QuestionResponse])
async def list_questions(
    skip: int = 0,
    limit: int = 100,
    question_service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_user)
):
    """List all questions (without answers)"""
    questions = await question_service.list_questions(skip, limit)
    return [
        QuestionResponse(
            id=q.id,
            prompt=q.prompt,
            choices=q.get_choices_with_letters(),
            difficulty_level=q.difficulty_level,
            created_by=q.created_by,
            created_at=q.created_at,
            updated_at=q.updated_at
        )
        for q in questions
    ]


@router.get("/{question_id}/answer", response_model=QuestionAnswerResponse)
async def get_question_answer(
    question_id: int,
    question_service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_user)
):
    """Get question answer"""
    question = await question_service.get_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return QuestionAnswerResponse(
        id=question.id,
        answer_letter=question.get_answer_letter(),
        answer_text=question.choices[question.answer_index]
    )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    question_service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_admin)
):
    """Update a question (Admin only)"""
    updated = await question_service.update_question(question_id, question_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return QuestionResponse(
        id=updated.id,
        prompt=updated.prompt,
        choices=updated.get_choices_with_letters(),
        created_by=updated.created_by,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    question_service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_admin)
):
    """Delete a question (Admin only)"""
    success = await question_service.delete_question(question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return None


@router.get("/me/created", response_model=List[QuestionResponse])
async def list_my_questions(
    skip: int = 0,
    limit: int = 100,
    question_service: QuestionService = Depends(get_question_service),
    current_user: User = Depends(get_current_admin)
):
    """List questions created by current user (Admin only)"""
    questions = await question_service.list_questions_by_creator(current_user.id, skip, limit)
    return [
        QuestionResponse(
            id=q.id,
            prompt=q.prompt,
            choices=q.get_choices_with_letters(),
            difficulty_level=q.difficulty_level,
            created_by=q.created_by,
            created_at=q.created_at,
            updated_at=q.updated_at
        )
        for q in questions
    ]
