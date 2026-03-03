"""
Service for managing user question statistics with spaced repetition algorithm.

Spaced Repetition Logic:
- After correct answer: extend review interval based on streak
  - 1 correct: +1 day
  - 2 correct: +3 days
  - 3 correct: +7 days
  - 4 correct: +14 days
  - 5+ correct: +30 days
- After incorrect answer: reset streak and shorten interval
  - Reset to +1 day (or immediate if streak was already 0)
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from app.domain.entities.user_question_stats import (
    UserQuestionStats,
    QuestionAnswerSubmit,
    QuestionAnswerResult,
    UserQuestionStatsResponse,
    UserStatsSummary,
)
from app.domain.entities.question import Question
from app.domain.repositories.user_question_stats_repository import UserQuestionStatsRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


# Spaced repetition intervals (in days) based on streak
REVIEW_INTERVALS = {
    0: 1,    # First attempt or after reset
    1: 1,    # 1 correct in a row
    2: 3,    # 2 correct in a row
    3: 7,    # 3 correct in a row
    4: 14,   # 4 correct in a row
    5: 30,   # 5+ correct in a row (mastered)
}


class UserQuestionStatsService:
    """Service for managing user question statistics with spaced repetition"""

    def __init__(
        self,
        stats_repository: UserQuestionStatsRepository,
        question_repository: QuestionRepository,
        user_repository: UserRepository
    ):
        self.stats_repository = stats_repository
        self.question_repository = question_repository
        self.user_repository = user_repository

    def _calculate_next_review(self, streak: int, is_correct: bool) -> datetime:
        """
        Calculate the next review time based on spaced repetition.
        
        Args:
            streak: Current streak of correct answers
            is_correct: Whether the last answer was correct
        
        Returns:
            Datetime for next review
        """
        if is_correct:
            # Extend interval based on new streak
            days = REVIEW_INTERVALS.get(min(streak, 5), 30)
        else:
            # Reset to short interval after incorrect
            days = REVIEW_INTERVALS[0]
        
        return datetime.utcnow() + timedelta(days=days)

    async def submit_answer(
        self,
        user_id: int,
        answer_data: QuestionAnswerSubmit
    ) -> Tuple[Optional[QuestionAnswerResult], Optional[str]]:
        """
        Submit an answer for a question and update stats.
        
        Args:
            user_id: ID of the user submitting the answer
            answer_data: Contains question_id and answer_index
        
        Returns:
            Tuple of (result, error_message)
        """
        # Get the question
        question = await self.question_repository.get_by_id(answer_data.question_id)
        if not question:
            logger.warning(
                f"Answer submission failed: question not found",
                extra={"user_id": user_id, "question_id": answer_data.question_id}
            )
            return None, "Question not found"

        # Check if answer is correct
        is_correct = answer_data.answer_index == question.answer_index

        # Get existing stats or create new
        existing_stats = await self.stats_repository.get_by_user_and_question(
            user_id, answer_data.question_id
        )

        now = datetime.utcnow()

        if existing_stats:
            # Update existing stats
            new_total = existing_stats.total_attempts + 1
            new_correct = existing_stats.correct_attempts + (1 if is_correct else 0)
            
            # Update streak
            if is_correct:
                new_streak = existing_stats.streak + 1
            else:
                new_streak = 0
            
            # Calculate next review
            next_review = self._calculate_next_review(new_streak, is_correct)

            updated_stats = UserQuestionStats(
                id=existing_stats.id,
                user_id=user_id,
                question_id=answer_data.question_id,
                total_attempts=new_total,
                correct_attempts=new_correct,
                last_seen_at=now,
                last_result=is_correct,
                next_review_at=next_review,
                streak=new_streak,
                created_at=existing_stats.created_at,
                updated_at=now
            )
        else:
            # Create new stats
            new_streak = 1 if is_correct else 0
            next_review = self._calculate_next_review(new_streak, is_correct)

            updated_stats = UserQuestionStats(
                user_id=user_id,
                question_id=answer_data.question_id,
                total_attempts=1,
                correct_attempts=1 if is_correct else 0,
                last_seen_at=now,
                last_result=is_correct,
                next_review_at=next_review,
                streak=new_streak
            )

        # Save to database
        saved_stats = await self.stats_repository.upsert(updated_stats)

        # Award XP for first-time correct solve
        if is_correct:
            previously_solved = existing_stats.correct_attempts > 0 if existing_stats else False
            if not previously_solved:
                xp_earned = question.difficulty_level * 2
                await self._add_user_xp(user_id, xp_earned)

        logger.info(
            f"Answer submitted",
            extra={
                "user_id": user_id,
                "question_id": answer_data.question_id,
                "is_correct": is_correct,
                "streak": saved_stats.streak
            }
        )

        # Calculate accuracy
        accuracy = saved_stats.accuracy

        # Build result
        result = QuestionAnswerResult(
            question_id=answer_data.question_id,
            is_correct=is_correct,
            correct_answer_index=question.answer_index,
            correct_answer_text=question.choices[question.answer_index],
            total_attempts=saved_stats.total_attempts,
            correct_attempts=saved_stats.correct_attempts,
            accuracy=accuracy,
            streak=saved_stats.streak,
            mastery_level=saved_stats.mastery_level,
            next_review_at=saved_stats.next_review_at
        )

        return result, None

    async def get_user_stats(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserQuestionStatsResponse]:
        """Get all question stats for a user"""
        stats = await self.stats_repository.get_by_user(user_id, skip, limit)
        return [
            UserQuestionStatsResponse(
                id=s.id,
                question_id=s.question_id,
                total_attempts=s.total_attempts,
                correct_attempts=s.correct_attempts,
                accuracy=s.accuracy,
                last_seen_at=s.last_seen_at,
                last_result=s.last_result,
                next_review_at=s.next_review_at,
                streak=s.streak,
                mastery_level=s.mastery_level
            )
            for s in stats
        ]

    async def _add_user_xp(self, user_id: int, xp_earned: int) -> None:
        """Add XP to user and update total"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(
                "User not found when adding XP",
                extra={"user_id": user_id, "xp_earned": xp_earned}
            )
            return
        
        new_total_xp = user.total_xp + xp_earned
        await self.user_repository.update(user_id, {"total_xp": new_total_xp})
        
        logger.info(
            "XP awarded",
            extra={"user_id": user_id, "xp_earned": xp_earned, "total_xp": new_total_xp}
        )

    async def get_question_stats(self, user_id: int, question_id: int) -> Optional[UserQuestionStatsResponse]:
        """Get stats for a specific question"""
        stats = await self.stats_repository.get_by_user_and_question(user_id, question_id)
        if not stats:
            return None
        
        return UserQuestionStatsResponse(
            id=stats.id,
            question_id=stats.question_id,
            total_attempts=stats.total_attempts,
            correct_attempts=stats.correct_attempts,
            accuracy=stats.accuracy,
            last_seen_at=stats.last_seen_at,
            last_result=stats.last_result,
            next_review_at=stats.next_review_at,
            streak=stats.streak,
            mastery_level=stats.mastery_level
        )

    async def get_questions_for_review(self, user_id: int, limit: int = 10) -> List[dict]:
        """
        Get questions that are due for review.
        
        Returns questions where next_review_at <= now or never seen.
        """
        question_ids = await self.stats_repository.get_questions_for_review(user_id, limit)
        
        if not question_ids:
            return []
        
        # Get question details
        questions = []
        for qid in question_ids:
            question = await self.question_repository.get_by_id(qid)
            if question:
                questions.append({
                    "id": question.id,
                    "prompt": question.prompt,
                    "choices": question.get_choices_with_letters(),
                })
        
        logger.debug(
            f"Retrieved questions for review",
            extra={"user_id": user_id, "count": len(questions)}
        )
        
        return questions

    async def get_user_stats_summary(self, user_id: int) -> UserStatsSummary:
        """Get overall statistics summary for a user"""
        summary = await self.stats_repository.get_user_stats_summary(user_id)
        
        return UserStatsSummary(
            total_questions_attempted=summary["total_questions_attempted"],
            total_correct=summary["total_correct"],
            overall_accuracy=summary["overall_accuracy"],
            mastered_count=summary["mastered_count"],
            proficient_count=summary["proficient_count"],
            learning_count=summary["learning_count"],
            new_count=summary["new_count"],
            current_streak=summary["current_streak"],
            longest_streak=summary["longest_streak"]
        )

    async def reset_question_stats(self, user_id: int, question_id: int) -> bool:
        """Reset stats for a specific question (start over)"""
        stats = await self.stats_repository.get_by_user_and_question(user_id, question_id)
        if not stats:
            return False
        
        reset_stats = UserQuestionStats(
            id=stats.id,
            user_id=user_id,
            question_id=question_id,
            total_attempts=0,
            correct_attempts=0,
            last_seen_at=None,
            last_result=None,
            next_review_at=None,
            streak=0
        )
        
        await self.stats_repository.upsert(reset_stats)
        
        logger.info(
            f"Reset question stats",
            extra={"user_id": user_id, "question_id": question_id}
        )
        
        return True
