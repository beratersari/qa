from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class LeaderboardPeriod(str, Enum):
    """Time period for leaderboard"""
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    ALL_TIME = "all_time"


class LeaderboardDummyCreate(BaseModel):
    """DTO for creating a dummy leaderboard entry"""
    display_name: str = Field(..., min_length=2, max_length=100)
    solved_count: int = Field(..., ge=0)
    period: LeaderboardPeriod


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    model_config = ConfigDict(from_attributes=True)

    rank: int
    display_name: str
    solved_count: int
    total_xp: int
    user_id: Optional[int] = None
    is_dummy: bool = False


class LeaderboardResponse(BaseModel):
    """Leaderboard response with entries and current user rank"""
    model_config = ConfigDict(from_attributes=True)

    period: LeaderboardPeriod
    entries: List[LeaderboardEntry]
    current_user_rank: Optional[int] = None


class XpLeaderboardEntry(BaseModel):
    """XP leaderboard entry"""
    model_config = ConfigDict(from_attributes=True)

    rank: int
    display_name: str
    total_xp: int
    challenge_streak: int
    user_id: Optional[int] = None


class XpLeaderboardResponse(BaseModel):
    """XP leaderboard response"""
    model_config = ConfigDict(from_attributes=True)

    entries: List[XpLeaderboardEntry]
    current_user_rank: Optional[int] = None
