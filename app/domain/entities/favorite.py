from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class FavoriteListPrivacy(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    SHARED = "shared"


class FavoriteList(BaseModel):
    """FavoriteList domain entity"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    user_id: int
    is_default: bool = False
    privacy: FavoriteListPrivacy = FavoriteListPrivacy.PRIVATE
    shared_with_usernames: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FavoriteListCreate(BaseModel):
    """DTO for creating a favorite list"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    privacy: FavoriteListPrivacy = FavoriteListPrivacy.PRIVATE
    shared_with_usernames: List[str] = Field(default_factory=list)


class FavoriteListUpdate(BaseModel):
    """DTO for updating a favorite list"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    privacy: Optional[FavoriteListPrivacy] = None
    shared_with_usernames: Optional[List[str]] = None


class FavoriteListResponse(BaseModel):
    """DTO for favorite list response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    user_id: int
    is_default: bool
    privacy: FavoriteListPrivacy
    shared_with_usernames: List[str]
    question_count: int = 0
    flashcard_count: int = 0
    created_at: datetime
    updated_at: datetime


class FavoriteItem(BaseModel):
    """FavoriteItem domain entity - represents a question in a favorite list"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    favorite_list_id: int
    question_id: Optional[int] = None
    flashcard_id: Optional[int] = None
    added_at: datetime = Field(default_factory=datetime.utcnow)


class AddQuestionToFavorite(BaseModel):
    """DTO for adding a question to a favorite list"""
    question_id: int


class AddFlashcardToFavorite(BaseModel):
    """DTO for adding a flashcard to a favorite list"""
    flashcard_id: int


class FavoriteQuestionResponse(BaseModel):
    """DTO for favorite question response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    favorite_list_id: int
    question_id: int
    prompt: str
    choices: List[dict]  # With letter labels
    difficulty_level: int
    added_at: datetime


class FavoriteFlashcardResponse(BaseModel):
    """DTO for favorite flashcard response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    favorite_list_id: int
    flashcard_id: int
    word_front: str
    word_back: str
    example_sentences: List[str]
    added_at: datetime
