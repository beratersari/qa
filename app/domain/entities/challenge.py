from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class DailyChallenge(BaseModel):
    """Daily challenge entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    challenge_date: datetime  # The date this challenge is for (00:00 UTC+3)
    question_ids: List[int] = Field(default_factory=list)  # 5 random questions
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserChallengeProgress(BaseModel):
    """Tracks user's progress on a daily challenge"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    user_id: int
    challenge_id: int
    completed_questions: List[int] = Field(default_factory=list)  # Question IDs answered correctly
    is_completed: bool = False
    xp_awarded: bool = False  # Whether 100 XP was given
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DailyChallengeResponse(BaseModel):
    """DTO for daily challenge response"""
    model_config = ConfigDict(from_attributes=True)
    
    challenge_id: int
    challenge_date: datetime
    questions: List[dict]  # Question details without answers
    total_questions: int
    completed_questions: int
    is_completed: bool


class ChallengeProgressResponse(BaseModel):
    """DTO for challenge progress response"""
    model_config = ConfigDict(from_attributes=True)
    
    challenge_id: int
    challenge_date: datetime
    completed_questions: List[int]
    total_questions: int
    is_completed: bool
    current_streak: int
    longest_streak: int


class ChallengeSubmitAnswer(BaseModel):
    """DTO for submitting challenge answer"""
    challenge_id: int
    question_id: int
    answer_index: int


class ChallengeAnswerResult(BaseModel):
    """DTO for challenge answer result"""
    model_config = ConfigDict(from_attributes=True)
    
    question_id: int
    is_correct: bool
    correct_answer_index: Optional[int] = None
    correct_answer_text: Optional[str] = None
    completed_questions: int
    total_questions: int
    challenge_completed: bool
    xp_earned: int
