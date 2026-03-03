from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.challenge_repository_impl import SQLAlchemyChallengeRepository
from app.infrastructure.database.question_repository_impl import SQLAlchemyQuestionRepository
from app.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.application.services.challenge_service import ChallengeService
from app.domain.entities.challenge import (
    DailyChallengeResponse,
    ChallengeProgressResponse,
    ChallengeSubmitAnswer,
    ChallengeAnswerResult,
)
from app.domain.entities.user import User
from app.presentation.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/challenge", tags=["Daily Challenge"])


def get_challenge_service(db: Session = Depends(get_db)) -> ChallengeService:
    challenge_repo = SQLAlchemyChallengeRepository(db)
    question_repo = SQLAlchemyQuestionRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    return ChallengeService(challenge_repo, question_repo, user_repo)


@router.get("/daily", response_model=DailyChallengeResponse)
async def get_daily_challenge(
    challenge_service: ChallengeService = Depends(get_challenge_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's daily challenge.
    
    Returns 5 random questions for the daily challenge.
    Tracks user progress and completion status.
    """
    # Check and reset streak if needed
    await challenge_service.check_and_reset_streak(current_user.id)
    
    return await challenge_service.get_daily_challenge(current_user.id)


@router.post("/submit", response_model=ChallengeAnswerResult)
async def submit_challenge_answer(
    answer_data: ChallengeSubmitAnswer,
    challenge_service: ChallengeService = Depends(get_challenge_service),
    current_user: User = Depends(get_current_user)
):
    """
    Submit an answer for a challenge question.
    
    - Only correct answers count towards completion
    - 100 XP awarded upon completing all 5 questions
    - Streak increases with each daily completion
    """
    result, error = await challenge_service.submit_answer(current_user.id, answer_data)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return result


@router.get("/progress", response_model=ChallengeProgressResponse)
async def get_challenge_progress(
    challenge_service: ChallengeService = Depends(get_challenge_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get current challenge progress with streak information.
    
    Shows:
    - Completed questions
    - Current streak (consecutive days)
    - Longest streak ever
    """
    return await challenge_service.get_challenge_progress(current_user.id)
