from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SubscriptionType(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


class User(BaseModel):
    """User domain entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
    subscription_type: SubscriptionType = SubscriptionType.FREE
    total_xp: int = 0
    challenge_streak: int = 0
    longest_challenge_streak: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    @property
    def level(self) -> int:
        """Calculate level based on total XP (0-99 -> level 1, 100-199 -> level 2, etc.)"""
        return (self.total_xp // 100) + 1


class UserCreate(BaseModel):
    """DTO for creating a user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    """DTO for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """DTO for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    subscription_type: SubscriptionType
    total_xp: int
    level: int
    challenge_streak: int
    longest_challenge_streak: int
    created_at: datetime
    last_login: Optional[datetime]
