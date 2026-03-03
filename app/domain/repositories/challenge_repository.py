from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.entities.challenge import DailyChallenge, UserChallengeProgress


class ChallengeRepository(ABC):
    """Abstract repository for challenge data"""

    @abstractmethod
    async def get_challenge_by_date(self, challenge_date: datetime) -> Optional[DailyChallenge]:
        """Get challenge by date"""
        pass

    @abstractmethod
    async def create_challenge(self, challenge: DailyChallenge) -> DailyChallenge:
        """Create a new daily challenge"""
        pass

    @abstractmethod
    async def get_user_progress(self, user_id: int, challenge_id: int) -> Optional[UserChallengeProgress]:
        """Get user's progress for a specific challenge"""
        pass

    @abstractmethod
    async def create_user_progress(self, progress: UserChallengeProgress) -> UserChallengeProgress:
        """Create user progress record"""
        pass

    @abstractmethod
    async def update_user_progress(self, progress_id: int, progress_data: dict) -> Optional[UserChallengeProgress]:
        """Update user progress"""
        pass

    @abstractmethod
    async def upsert_user_progress(self, progress: UserChallengeProgress) -> UserChallengeProgress:
        """Create or update user progress"""
        pass

    @abstractmethod
    async def get_user_challenge_history(self, user_id: int, limit: int = 30) -> List[UserChallengeProgress]:
        """Get user's challenge history"""
        pass

    @abstractmethod
    async def get_random_question_ids(self, count: int = 5) -> List[int]:
        """Get random question IDs for challenge"""
        pass
