"""
Service for managing daily challenges.

Daily challenges renew at 00:00 UTC+3.
Each challenge has 5 random questions.
Users earn 100 XP upon completion.
Streak system tracks consecutive daily completions.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from app.domain.entities.challenge import (
    DailyChallenge,
    UserChallengeProgress,
    DailyChallengeResponse,
    ChallengeProgressResponse,
    ChallengeSubmitAnswer,
    ChallengeAnswerResult,
)
from app.domain.entities.question import Question
from app.domain.repositories.challenge_repository import ChallengeRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)

# Constants
CHALLENGE_XP_REWARD = 100
QUESTIONS_PER_CHALLENGE = 5
UTC_PLUS_3_OFFSET = timedelta(hours=3)


class ChallengeService:
    """Service for daily challenge operations"""

    def __init__(
        self,
        challenge_repository: ChallengeRepository,
        question_repository: QuestionRepository,
        user_repository: UserRepository
    ):
        self.challenge_repository = challenge_repository
        self.question_repository = question_repository
        self.user_repository = user_repository

    def _get_challenge_date(self) -> datetime:
        """
        Get the current challenge date (00:00 UTC+3).
        Challenges reset at midnight UTC+3.
        """
        # Get current time in UTC+3
        now_utc = datetime.utcnow()
        now_utc_plus_3 = now_utc + UTC_PLUS_3_OFFSET
        
        # Get the date part (midnight UTC+3)
        challenge_date = now_utc_plus_3.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Convert back to UTC for storage
        return challenge_date - UTC_PLUS_3_OFFSET

    async def get_or_create_daily_challenge(self) -> DailyChallenge:
        """Get today's challenge or create if it doesn't exist"""
        challenge_date = self._get_challenge_date()
        
        # Try to get existing challenge
        challenge = await self.challenge_repository.get_challenge_by_date(challenge_date)
        
        if not challenge:
            # Create new challenge with random questions
            question_ids = await self.challenge_repository.get_random_question_ids(QUESTIONS_PER_CHALLENGE)
            
            if len(question_ids) < QUESTIONS_PER_CHALLENGE:
                logger.error(
                    "Not enough questions for daily challenge",
                    extra={"required": QUESTIONS_PER_CHALLENGE, "available": len(question_ids)}
                )
                raise ValueError("Not enough questions available for daily challenge")
            
            if len(question_ids) != QUESTIONS_PER_CHALLENGE:
                raise ValueError("Daily challenge must contain exactly 5 questions")
            
            challenge = DailyChallenge(
                challenge_date=challenge_date,
                question_ids=question_ids
            )
            challenge = await self.challenge_repository.create_challenge(challenge)
            
            logger.info(
                "Created new daily challenge",
                extra={"challenge_id": challenge.id, "question_count": len(question_ids)}
            )
        
        return challenge

    async def get_daily_challenge(self, user_id: int) -> DailyChallengeResponse:
        """Get today's challenge with user progress"""
        challenge = await self.get_or_create_daily_challenge()
        
        # Get user progress
        progress = await self.challenge_repository.get_user_progress(user_id, challenge.id)
        
        # Get question details
        questions = await self._get_question_details(challenge.question_ids)
        
        completed_questions = len(progress.completed_questions) if progress else 0
        
        return DailyChallengeResponse(
            challenge_id=challenge.id,
            challenge_date=challenge.challenge_date,
            questions=questions,
            total_questions=len(challenge.question_ids),
            completed_questions=completed_questions,
            is_completed=progress.is_completed if progress else False
        )

    async def submit_answer(
        self,
        user_id: int,
        answer_data: ChallengeSubmitAnswer
    ) -> Tuple[Optional[ChallengeAnswerResult], Optional[str]]:
        """Submit an answer for a challenge question"""
        # Get the challenge
        challenge = await self.challenge_repository.get_challenge_by_date(
            self._get_challenge_date()
        )
        
        if not challenge:
            return None, "No active challenge found"
        
        if challenge.id != answer_data.challenge_id:
            return None, "Invalid challenge ID"
        
        if answer_data.question_id not in challenge.question_ids:
            return None, "Question not part of this challenge"
        
        # Get the question
        question = await self.question_repository.get_by_id(answer_data.question_id)
        if not question:
            return None, "Question not found"
        
        # Check if answer is correct
        is_correct = answer_data.answer_index == question.answer_index
        
        # Get or create user progress
        progress = await self.challenge_repository.get_user_progress(user_id, challenge.id)
        
        if not progress:
            progress = UserChallengeProgress(
                user_id=user_id,
                challenge_id=challenge.id,
                completed_questions=[],
                is_completed=False,
                xp_awarded=False
            )
        
        # If already completed, don't process further
        if progress.is_completed:
            return ChallengeAnswerResult(
                question_id=answer_data.question_id,
                is_correct=is_correct,
                correct_answer_index=question.answer_index if not is_correct else None,
                correct_answer_text=question.choices[question.answer_index] if not is_correct else None,
                completed_questions=len(progress.completed_questions),
                total_questions=len(challenge.question_ids),
                challenge_completed=True,
                xp_earned=0
            ), None
        
        # Update progress if correct
        xp_earned = 0
        challenge_completed = False
        
        if is_correct and answer_data.question_id not in progress.completed_questions:
            progress.completed_questions.append(answer_data.question_id)
            
            # Check if challenge is complete
            if len(progress.completed_questions) >= len(challenge.question_ids):
                progress.is_completed = True
                progress.completed_at = datetime.utcnow()
                challenge_completed = True
                
                # Award XP if not already awarded
                if not progress.xp_awarded:
                    progress.xp_awarded = True
                    xp_earned = CHALLENGE_XP_REWARD
                    await self._award_challenge_xp(user_id)
        
        # Save progress
        await self.challenge_repository.upsert_user_progress(progress)
        
        logger.info(
            "Challenge answer submitted",
            extra={
                "user_id": user_id,
                "challenge_id": challenge.id,
                "question_id": answer_data.question_id,
                "is_correct": is_correct,
                "challenge_completed": challenge_completed
            }
        )
        
        return ChallengeAnswerResult(
            question_id=answer_data.question_id,
            is_correct=is_correct,
            correct_answer_index=question.answer_index if not is_correct else None,
            correct_answer_text=question.choices[question.answer_index] if not is_correct else None,
            completed_questions=len(progress.completed_questions),
            total_questions=len(challenge.question_ids),
            challenge_completed=challenge_completed,
            xp_earned=xp_earned
        ), None

    async def get_challenge_progress(self, user_id: int) -> ChallengeProgressResponse:
        """Get user's current challenge progress with streak info"""
        challenge = await self.get_or_create_daily_challenge()
        
        progress = await self.challenge_repository.get_user_progress(user_id, challenge.id)
        
        # Get user streak info
        user = await self.user_repository.get_by_id(user_id)
        
        return ChallengeProgressResponse(
            challenge_id=challenge.id,
            challenge_date=challenge.challenge_date,
            completed_questions=progress.completed_questions if progress else [],
            total_questions=len(challenge.question_ids),
            is_completed=progress.is_completed if progress else False,
            current_streak=user.challenge_streak if user else 0,
            longest_streak=user.longest_challenge_streak if user else 0
        )

    async def _get_question_details(self, question_ids: List[int]) -> List[dict]:
        """Get question details without answers"""
        questions = []
        for qid in question_ids:
            question = await self.question_repository.get_by_id(qid)
            if question:
                questions.append({
                    "id": question.id,
                    "prompt": question.prompt,
                    "choices": question.get_choices_with_letters(),
                    "difficulty_level": question.difficulty_level
                })
        return questions

    async def _award_challenge_xp(self, user_id: int) -> None:
        """Award XP and update streak for completing challenge"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return
        
        # Add XP
        new_xp = user.total_xp + CHALLENGE_XP_REWARD
        
        # Update streak
        new_streak = user.challenge_streak + 1
        new_longest = max(user.longest_challenge_streak, new_streak)
        
        await self.user_repository.update(user_id, {
            "total_xp": new_xp,
            "challenge_streak": new_streak,
            "longest_challenge_streak": new_longest
        })
        
        logger.info(
            "Challenge XP awarded",
            extra={
                "user_id": user_id,
                "xp_earned": CHALLENGE_XP_REWARD,
                "new_streak": new_streak
            }
        )

    async def check_and_reset_streak(self, user_id: int) -> None:
        """
        Check if user's streak should be reset.
        Called when user views challenge to check if they missed a day.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user or user.challenge_streak == 0:
            return
        
        # Get yesterday's challenge
        yesterday_date = self._get_challenge_date() - timedelta(days=1)
        yesterday_challenge = await self.challenge_repository.get_challenge_by_date(yesterday_date)
        
        if yesterday_challenge:
            progress = await self.challenge_repository.get_user_progress(user_id, yesterday_challenge.id)
            if not progress or not progress.is_completed:
                # User missed yesterday, reset streak
                await self.user_repository.update(user_id, {"challenge_streak": 0})
                logger.info(
                    "Challenge streak reset",
                    extra={"user_id": user_id, "previous_streak": user.challenge_streak}
                )
