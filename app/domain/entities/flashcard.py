from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class FlashCard(BaseModel):
    """Flash card domain entity"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    word_front: str = Field(..., min_length=1, max_length=200)
    word_back: str = Field(..., min_length=1, max_length=200)
    example_sentences: List[str] = Field(default_factory=list)
    created_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FlashCardCreate(BaseModel):
    """DTO for creating a flash card"""
    word_front: str = Field(..., min_length=1, max_length=200)
    word_back: str = Field(..., min_length=1, max_length=200)
    example_sentences: List[str] = Field(default_factory=list)


class FlashCardUpdate(BaseModel):
    """DTO for updating a flash card"""
    word_front: Optional[str] = Field(None, min_length=1, max_length=200)
    word_back: Optional[str] = Field(None, min_length=1, max_length=200)
    example_sentences: Optional[List[str]] = None


class FlashCardResponse(BaseModel):
    """DTO for flash card response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    word_front: str
    word_back: str
    example_sentences: List[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
