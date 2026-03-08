from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from app.domain.entities.leaderboard import LeaderboardPeriod
from app.domain.repositories.leaderboard_repository import LeaderboardRepository
from app.infrastructure.database.models import UserQuestionStatsModel, UserModel, LeaderboardDummyModel
from app.domain.entities.user import ProfileVisibility
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemyLeaderboardRepository(LeaderboardRepository):
    """SQLAlchemy implementation of LeaderboardRepository"""

    def __init__(self, db: Session):
        self.db = db

    async def get_user_correct_counts(
        self,
        period: LeaderboardPeriod,
        since: Optional[datetime] = None
    ) -> List[dict]:
        """Get user correct answer counts for period"""
        query = self.db.query(
            UserQuestionStatsModel.user_id,
            UserModel.username,
            func.count(UserQuestionStatsModel.question_id).label("solved_count")
        ).join(UserModel, UserQuestionStatsModel.user_id == UserModel.id)

        if since:
            query = query.filter(UserQuestionStatsModel.last_seen_at >= since)

        # Only count questions that have been solved at least once
        query = query.filter(UserQuestionStatsModel.correct_attempts > 0)

        results = (
            query.group_by(UserQuestionStatsModel.user_id, UserModel.username)
            .order_by(desc("solved_count"))
            .all()
        )

        return [
            {
                "user_id": row.user_id,
                "display_name": row.username,
                "solved_count": int(row.solved_count or 0),
            }
            for row in results
        ]

    async def get_dummy_entries(self, period: LeaderboardPeriod) -> List[dict]:
        """Get dummy leaderboard entries for period"""
        results = (
            self.db.query(LeaderboardDummyModel)
            .filter(LeaderboardDummyModel.period == period.value)
            .order_by(LeaderboardDummyModel.solved_count.desc())
            .all()
        )

        return [
            {
                "id": row.id,
                "display_name": row.display_name,
                "solved_count": row.solved_count,
                "period": row.period,
            }
            for row in results
        ]

    async def get_public_user_xp(self) -> List[dict]:
        """Get public users ordered by total XP"""
        results = (
            self.db.query(
                UserModel.id,
                UserModel.username,
                UserModel.total_xp,
                UserModel.challenge_streak
            )
            .filter(UserModel.profile_visibility == ProfileVisibility.PUBLIC)
            .order_by(UserModel.total_xp.desc())
            .all()
        )

        return [
            {
                "user_id": row.id,
                "display_name": row.username,
                "total_xp": row.total_xp,
                "challenge_streak": row.challenge_streak,
            }
            for row in results
        ]

    async def create_dummy_entry(self, display_name: str, solved_count: int, period: LeaderboardPeriod) -> dict:
        """Create a dummy leaderboard entry"""
        dummy = LeaderboardDummyModel(
            display_name=display_name,
            solved_count=solved_count,
            period=period.value
        )
        self.db.add(dummy)
        self.db.commit()
        self.db.refresh(dummy)

        logger.info(
            "Created dummy leaderboard entry",
            extra={"display_name": display_name, "solved_count": solved_count, "period": period.value}
        )

        return {
            "id": dummy.id,
            "display_name": dummy.display_name,
            "solved_count": dummy.solved_count,
            "period": dummy.period,
        }

    async def delete_dummy_entry(self, dummy_id: int) -> bool:
        """Delete a dummy leaderboard entry"""
        dummy = self.db.query(LeaderboardDummyModel).filter(LeaderboardDummyModel.id == dummy_id).first()
        if not dummy:
            return False

        self.db.delete(dummy)
        self.db.commit()
        
        logger.info("Deleted dummy leaderboard entry", extra={"dummy_id": dummy_id})
        return True

    async def get_user_rank(self, user_id: int, period: LeaderboardPeriod, since: Optional[datetime] = None) -> Optional[int]:
        """Get rank for a specific user"""
        user_counts = await self.get_user_correct_counts(period, since)
        
        rank = 1
        for entry in user_counts:
            if entry["user_id"] == user_id:
                return rank
            rank += 1
        
        return None
