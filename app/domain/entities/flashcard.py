from datetime import datetime
from typing import Optional, List
from enum import Enum
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


class FlashCardSet(BaseModel):
    """Flash card set domain entity"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    created_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FlashCardSetCreate(BaseModel):
    """DTO for creating a flash card set"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class FlashCardSetUpdate(BaseModel):
    """DTO for updating a flash card set"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class FlashCardSetResponse(BaseModel):
    """DTO for flash card set response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    flashcard_count: int = 0
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime


class FlashCardInSetResponse(BaseModel):
    """DTO for flash card in set response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    word_front: str
    word_back: str
    example_sentences: List[str]
    set_id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime


class FlashCardSetAddFlashcard(BaseModel):
    """DTO for adding a flash card to a set"""
    flashcard_id: int


class FlashCardKnowledgeStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"


class FlashCardSession(BaseModel):
    """Flash card set session entity"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    set_id: int
    started_at: datetime = Field(default_factory=datetime.utcnow)


class FlashCardSessionResponse(BaseModel):
    """DTO for flash card session response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    set_id: int
    started_at: datetime


class FlashCardSessionCreate(BaseModel):
    """DTO for creating a flash card session"""
    set_id: int


class FlashCardProgressUpdate(BaseModel):
    """DTO for updating flash card progress"""
    flashcard_id: int
    status: FlashCardKnowledgeStatus


class FlashCardProgressResponse(BaseModel):
    """DTO for flash card progress response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    set_id: int
    flashcard_id: int
    status: FlashCardKnowledgeStatus
    updated_at: datetime
