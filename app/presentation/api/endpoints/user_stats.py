from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.user_question_stats_repository_impl import SQLAlchemyUserQuestionStatsRepository
from app.infrastructure.database.question_repository_impl import SQLAlchemyQuestionRepository
from app.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.application.services.user_question_stats_service import UserQuestionStatsService
from app.domain.entities.user_question_stats import (
    QuestionAnswerSubmit,
    QuestionAnswerResult,
    UserQuestionStatsResponse,
    UserStatsSummary,
    DailySolvedStatsResponse,
    LowestAccuracyQuestionsResponse,
)
from app.domain.entities.user import User
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/stats", tags=["User Question Stats"])


def get_stats_service(db: Session = Depends(get_db)) -> UserQuestionStatsService:
    stats_repo = SQLAlchemyUserQuestionStatsRepository(db)
    question_repo = SQLAlchemyQuestionRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    return UserQuestionStatsService(stats_repo, question_repo, user_repo)


@router.post("/submit", response_model=QuestionAnswerResult, status_code=status.HTTP_200_OK)
async def submit_answer(
    answer_data: QuestionAnswerSubmit,
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """
    Submit an answer for a question.
    
    This will:
    - Check if the answer is correct
    - Update user's stats for this question
    - Apply spaced repetition algorithm for next review
    - Return detailed result with streak and mastery level
    """
    result, error = await stats_service.submit_answer(current_user.id, answer_data)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    
    return result


@router.get("/", response_model=List[UserQuestionStatsResponse])
async def get_my_stats(
    skip: int = 0,
    limit: int = 100,
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """Get all question statistics for the current user"""
    return await stats_service.get_user_stats(current_user.id, skip, limit)


@router.get("/users/{user_id}", response_model=List[UserQuestionStatsResponse])
async def get_user_stats_by_admin(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_admin)
):
    """Get question statistics for a specific user (Admin only)"""
    return await stats_service.get_user_stats(user_id, skip, limit)


@router.get("/summary", response_model=UserStatsSummary)
async def get_my_stats_summary(
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """Get overall statistics summary for the current user"""
    return await stats_service.get_user_stats_summary(current_user.id)


@router.get("/review", response_model=List[dict])
async def get_questions_for_review(
    limit: int = 10,
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get questions that are due for review.

    Returns questions where:
    - next_review_at <= now (due for review)
    - OR never seen before (no stats exist)
    """
    questions = await stats_service.get_questions_for_review(current_user.id, limit)
    return questions


@router.get("/daily-solved", response_model=DailySolvedStatsResponse)
async def get_daily_solved_stats(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back (1-30)"),
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily solved question counts for the last N days.

    Use this endpoint to populate a line chart showing solved questions over time.
    Common values for `days`: 7 (last week) or 30 (last month).

    Returns:
    - period: The time period string
    - daily_stats: List of {date, solved_count} for each day
    - total_solved: Total questions solved in the period
    - average_per_day: Average solved per day
    """
    return await stats_service.get_daily_solved_stats(current_user.id, days)


@router.get("/lowest-accuracy", response_model=LowestAccuracyQuestionsResponse)
async def get_lowest_accuracy_questions(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of questions to return"),
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get questions with the lowest accuracy for the current user.

    This is useful for identifying questions that need more practice.

    Returns:
    - questions: List of questions with accuracy info, sorted by accuracy ascending
    - count: Number of questions returned
    """
    return await stats_service.get_lowest_accuracy_questions(current_user.id, limit)


@router.get("/{question_id}", response_model=UserQuestionStatsResponse)
async def get_question_stats(
    question_id: int,
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific question"""
    stats = await stats_service.get_question_stats(current_user.id, question_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stats found for this question"
        )
    return stats


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reset_question_stats(
    question_id: int,
    stats_service: UserQuestionStatsService = Depends(get_stats_service),
    current_user: User = Depends(get_current_user)
):
    """Reset statistics for a specific question (start over)"""
    success = await stats_service.reset_question_stats(current_user.id, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stats found for this question"
        )
    return None
