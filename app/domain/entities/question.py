from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from enum import Enum


class QuestionSetType(str, Enum):
    NORMAL = "normal"
    PREMIUM = "premium"


def index_to_letter(index: int) -> str:
    """Convert index to letter (0->A, 1->B, etc.)"""
    return chr(65 + index)  # 65 is ASCII for 'A'


def letter_to_index(letter: str) -> int:
    """Convert letter to index (A->0, B->1, etc.)"""
    return ord(letter.upper()) - 65


class Question(BaseModel):
    """Question domain entity"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    prompt: str = Field(..., min_length=1, max_length=500)
    choices: List[str] = Field(default_factory=list)
    answer_index: int = Field(..., ge=0)
    difficulty_level: int = Field(1, ge=1, le=10)
    created_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v):
        if len(v) < 2:
            raise ValueError('At least 2 choices are required')
        if len(v) > 26:
            raise ValueError('Maximum 26 choices allowed (A-Z)')
        return v

    @model_validator(mode='after')
    def validate_answer_index(self):
        if self.answer_index >= len(self.choices):
            raise ValueError(f'Answer index {self.answer_index} is out of range. Must be less than {len(self.choices)}')
        return self

    def get_answer_letter(self) -> str:
        """Get answer as letter (A, B, C, etc.)"""
        return index_to_letter(self.answer_index)

    def get_choices_with_letters(self) -> List[dict]:
        """Get choices with their letter labels"""
        return [
            {"letter": index_to_letter(i), "text": choice}
            for i, choice in enumerate(self.choices)
        ]


class QuestionCreate(BaseModel):
    """DTO for creating a question"""
    prompt: str = Field(..., min_length=1, max_length=500)
    choices: List[str] = Field(default_factory=list)
    answer_index: int = Field(..., ge=0)
    difficulty_level: int = Field(1, ge=1, le=10)

    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v):
        if len(v) < 2:
            raise ValueError('At least 2 choices are required')
        if len(v) > 26:
            raise ValueError('Maximum 26 choices allowed (A-Z)')
        return v

    @model_validator(mode='after')
    def validate_answer_index(self):
        if self.answer_index >= len(self.choices):
            raise ValueError(f'Answer index {self.answer_index} is out of range. Must be less than {len(self.choices)}')
        return self


class QuestionUpdate(BaseModel):
    """DTO for updating a question"""
    prompt: Optional[str] = Field(None, min_length=1, max_length=500)
    choices: Optional[List[str]] = None
    answer_index: Optional[int] = Field(None, ge=0)
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)

    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v):
        if v is not None:
            if len(v) < 2:
                raise ValueError('At least 2 choices are required')
            if len(v) > 26:
                raise ValueError('Maximum 26 choices allowed (A-Z)')
        return v


class QuestionResponse(BaseModel):
    """DTO for question response without answer"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    prompt: str
    choices: List[dict]  # With letter labels
    difficulty_level: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime


class QuestionAnswerResponse(BaseModel):
    """DTO for question answer response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    answer_letter: str
    answer_text: str


class QuestionSet(BaseModel):
    """Question Set domain entity"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    set_type: QuestionSetType = QuestionSetType.NORMAL
    created_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QuestionSetCreate(BaseModel):
    """DTO for creating a question set"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    set_type: QuestionSetType = QuestionSetType.NORMAL


class QuestionSetUpdate(BaseModel):
    """DTO for updating a question set"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    set_type: Optional[QuestionSetType] = None


class QuestionSetResponse(BaseModel):
    """DTO for question set response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    set_type: QuestionSetType
    question_count: int = 0
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime


class QuestionSetAddQuestion(BaseModel):
    """DTO for adding a question to a set"""
    question_id: int


class QuestionInSetResponse(BaseModel):
    """DTO for question in a set response (without answer)"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    prompt: str
    choices: List[dict]
    difficulty_level: int
    set_id: int
    question_id: int
