"""
Leaderboard service for calculating and retrieving leaderboard entries.

Leaderboard is based on number of solved (correct) answers.
Supports periods: last 7 days, last 30 days, all time.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from app.domain.entities.leaderboard import (
    LeaderboardPeriod,
    LeaderboardEntry,
    LeaderboardResponse,
    LeaderboardDummyCreate,
    XpLeaderboardEntry,
    XpLeaderboardResponse
)
from app.domain.repositories.leaderboard_repository import LeaderboardRepository
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class LeaderboardService:
    """Service for leaderboard operations"""

    def __init__(self, leaderboard_repository: LeaderboardRepository):
        self.leaderboard_repository = leaderboard_repository

    def _get_since_date(self, period: LeaderboardPeriod) -> Optional[datetime]:
        """Get start date for period"""
        now = datetime.utcnow()
        
        if period == LeaderboardPeriod.LAST_7_DAYS:
            return now - timedelta(days=7)
        elif period == LeaderboardPeriod.LAST_30_DAYS:
            return now - timedelta(days=30)
        elif period == LeaderboardPeriod.ALL_TIME:
            return None
        
        return None

    async def get_leaderboard(self, period: LeaderboardPeriod, current_user_id: Optional[int] = None) -> LeaderboardResponse:
        """Get leaderboard entries with current user rank"""
        since = self._get_since_date(period)
        
        # Get real user counts
        user_counts = await self.leaderboard_repository.get_user_correct_counts(period, since)
        
        # Get dummy entries
        dummy_entries = await self.leaderboard_repository.get_dummy_entries(period)
        
        # Combine and sort entries
        all_entries = []
        
        # Add real users
        for user in user_counts:
            all_entries.append({
                "display_name": user["display_name"],
                "solved_count": user["solved_count"],
                "total_xp": user.get("total_xp", 0),
                "user_id": user["user_id"],
                "is_dummy": False
            })
        
        # Add dummy users
        for dummy in dummy_entries:
            all_entries.append({
                "display_name": dummy["display_name"],
                "solved_count": dummy["solved_count"],
                "total_xp": dummy.get("total_xp", 0),
                "user_id": None,
                "is_dummy": True
            })
        
        # Sort by solved_count desc
        all_entries.sort(key=lambda x: x["solved_count"], reverse=True)
        
        # Assign ranks
        leaderboard_entries = []
        current_user_rank = None
        
        for index, entry in enumerate(all_entries, start=1):
            leaderboard_entries.append(LeaderboardEntry(
                rank=index,
                display_name=entry["display_name"],
                solved_count=entry["solved_count"],
                total_xp=entry["total_xp"],
                user_id=entry["user_id"],
                is_dummy=entry["is_dummy"]
            ))
            
            if current_user_id and entry["user_id"] == current_user_id:
                current_user_rank = index
        
        return LeaderboardResponse(
            period=period,
            entries=leaderboard_entries,
            current_user_rank=current_user_rank
        )

    async def add_dummy_entry(self, dummy_data: LeaderboardDummyCreate) -> dict:
        """Add a dummy leaderboard entry"""
        return await self.leaderboard_repository.create_dummy_entry(
            display_name=dummy_data.display_name,
            solved_count=dummy_data.solved_count,
            period=dummy_data.period
        )

    async def get_xp_leaderboard(self, current_user_id: Optional[int] = None) -> XpLeaderboardResponse:
        """Get XP leaderboard for public users"""
        users = await self.leaderboard_repository.get_public_user_xp()

        entries = []
        current_user_rank = None
        for index, user in enumerate(users, start=1):
            entries.append(XpLeaderboardEntry(
                rank=index,
                display_name=user["display_name"],
                total_xp=user["total_xp"],
                challenge_streak=user["challenge_streak"],
                user_id=user["user_id"]
            ))
            if current_user_id and user["user_id"] == current_user_id:
                current_user_rank = index

        return XpLeaderboardResponse(entries=entries, current_user_rank=current_user_rank)

    async def delete_dummy_entry(self, dummy_id: int) -> bool:
        """Delete a dummy leaderboard entry"""
        return await self.leaderboard_repository.delete_dummy_entry(dummy_id)
