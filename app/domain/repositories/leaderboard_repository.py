from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.entities.leaderboard import LeaderboardPeriod


class LeaderboardRepository(ABC):
    """Abstract repository for leaderboard data"""

    @abstractmethod
    async def get_user_correct_counts(
        self,
        period: LeaderboardPeriod,
        since: Optional[datetime] = None
    ) -> List[dict]:
        """Get user correct answer counts for period"""
        pass

    @abstractmethod
    async def get_public_user_xp(self) -> List[dict]:
        """Get public users ordered by total XP"""
        pass

    @abstractmethod
    async def get_dummy_entries(self, period: LeaderboardPeriod) -> List[dict]:
        """Get dummy leaderboard entries for period"""
        pass

    @abstractmethod
    async def create_dummy_entry(self, display_name: str, solved_count: int, period: LeaderboardPeriod) -> dict:
        """Create a dummy leaderboard entry"""
        pass

    @abstractmethod
    async def delete_dummy_entry(self, dummy_id: int) -> bool:
        """Delete a dummy leaderboard entry"""
        pass

    @abstractmethod
    async def get_user_rank(self, user_id: int, period: LeaderboardPeriod, since: Optional[datetime] = None) -> Optional[int]:
        """Get rank for a specific user"""
        pass
