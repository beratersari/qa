from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, date
from app.domain.entities.user_question_stats import UserQuestionStats


class UserQuestionStatsRepository(ABC):
    """Abstract repository for UserQuestionStats entity"""

    @abstractmethod
    async def create(self, stats: UserQuestionStats) -> UserQuestionStats:
        """Create new user question stats"""
        pass

    @abstractmethod
    async def get_by_id(self, stats_id: int) -> Optional[UserQuestionStats]:
        """Get stats by ID"""
        pass

    @abstractmethod
    async def get_by_user_and_question(self, user_id: int, question_id: int) -> Optional[UserQuestionStats]:
        """Get stats for a specific user and question"""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserQuestionStats]:
        """Get all stats for a user"""
        pass

    @abstractmethod
    async def update(self, stats_id: int, stats_data: dict) -> Optional[UserQuestionStats]:
        """Update stats by ID"""
        pass

    @abstractmethod
    async def upsert(self, stats: UserQuestionStats) -> UserQuestionStats:
        """Create or update stats for user and question"""
        pass

    @abstractmethod
    async def get_questions_for_review(self, user_id: int, limit: int = 10) -> List[int]:
        """Get question IDs due for review (next_review_at <= now or never seen)"""
        pass

    @abstractmethod
    async def get_user_stats_summary(self, user_id: int) -> dict:
        """Get summary statistics for a user"""
        pass

    @abstractmethod
    async def get_by_user_and_questions(self, user_id: int, question_ids: List[int]) -> List[UserQuestionStats]:
        """Get stats for multiple questions for a user"""
        pass

    @abstractmethod
    async def get_daily_solved_counts(self, user_id: int, start_date: date, end_date: date) -> List[dict]:
        """Get daily solved counts for a user within a date range"""
        pass

    @abstractmethod
    async def get_lowest_accuracy_questions(self, user_id: int, limit: int = 10) -> List[dict]:
        """Get questions with lowest accuracy for a user"""
        pass

    @abstractmethod
    async def record_solved_question(self, user_id: int, question_id: int) -> None:
        """Record a correct question submission"""
        pass
