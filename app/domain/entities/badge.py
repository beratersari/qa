from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class BadgeProgressType(str, Enum):
    QUESTION_SETS_SOLVED = "question_sets_solved"
    FLASHCARDS_SOLVED = "flashcards_solved"
    QUESTIONS_SOLVED = "questions_solved"


class BadgeCondition(BaseModel):
    """Badge condition definition"""
    progress_type: BadgeProgressType
    progress_target: int = Field(..., ge=1)


class BadgeBase(BaseModel):
    """Shared badge fields"""
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    icon_path: Optional[str] = Field(None, max_length=500)
    conditions: List[BadgeCondition] = Field(..., min_length=1)

    @field_validator("conditions", mode="before")
    @classmethod
    def validate_conditions(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one condition must be provided")
        return v


class Badge(BaseModel):
    """Badge domain entity"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    icon_path: Optional[str] = Field(None, max_length=500)
    conditions: List[BadgeCondition] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BadgeCreate(BadgeBase):
    """DTO for creating a badge"""
    pass


class BadgeUpdate(BaseModel):
    """DTO for updating a badge"""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    icon_path: Optional[str] = Field(None, max_length=500)
    conditions: Optional[List[BadgeCondition]] = None


class BadgeResponse(BaseModel):
    """DTO for badge response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    icon_path: Optional[str]
    conditions: List[BadgeCondition]
    created_at: datetime
    updated_at: datetime


class UserBadge(BaseModel):
    """User badge progress entity"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    badge_id: int
    current_progress: int = 0
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserBadgeResponse(BaseModel):
    """DTO for user badge response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    badge: BadgeResponse
    current_progress: int
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
