from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UserQuestionStats(BaseModel):
    """Domain entity for tracking user performance on questions"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    question_id: int
    total_attempts: int = 0
    correct_attempts: int = 0
    last_seen_at: Optional[datetime] = None
    last_result: Optional[bool] = None
    next_review_at: Optional[datetime] = None
    streak: int = 0  # Current streak of correct answers
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage"""
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_attempts / self.total_attempts) * 100

    @property
    def mastery_level(self) -> str:
        """Determine mastery level based on streak and accuracy"""
        if self.streak >= 5 and self.accuracy >= 80:
            return "mastered"
        elif self.streak >= 3 and self.accuracy >= 60:
            return "proficient"
        elif self.total_attempts >= 3 and self.accuracy >= 40:
            return "learning"
        else:
            return "new"


class UserQuestionStatsCreate(BaseModel):
    """DTO for creating user question stats"""
    user_id: int
    question_id: int


class QuestionAnswerSubmit(BaseModel):
    """DTO for submitting a question answer"""
    question_id: int
    answer_index: int  # The index of the chosen answer


class QuestionAnswerResult(BaseModel):
    """DTO for answer result response"""
    model_config = ConfigDict(from_attributes=True)

    question_id: int
    is_correct: bool
    correct_answer_index: int
    correct_answer_text: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    streak: int
    mastery_level: str
    next_review_at: Optional[datetime]


class UserQuestionStatsResponse(BaseModel):
    """DTO for user question stats response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    total_attempts: int
    correct_attempts: int
    accuracy: float
    last_seen_at: Optional[datetime]
    last_result: Optional[bool]
    next_review_at: Optional[datetime]
    streak: int
    mastery_level: str


class UserStatsSummary(BaseModel):
    """DTO for overall user stats summary"""
    model_config = ConfigDict(from_attributes=True)

    total_questions_attempted: int
    total_correct: int
    overall_accuracy: float
    mastered_count: int
    proficient_count: int
    learning_count: int
    new_count: int
    current_streak: int  # Current session streak
    longest_streak: int


class QuestionsForReview(BaseModel):
    """DTO for questions due for review"""
    model_config = ConfigDict(from_attributes=True)

    questions: list  # List of QuestionResponse
    total_count: int
    due_now_count: int


class DailySolvedStats(BaseModel):
    """DTO for daily solved count"""
    date: date
    solved_count: int


class DailySolvedStatsResponse(BaseModel):
    """DTO for daily solved stats response"""
    period: str  # "last_7_days" or "last_30_days"
    daily_stats: List[DailySolvedStats]
    total_solved: int
    average_per_day: float


class QuestionAccuracy(BaseModel):
    """DTO for question with accuracy info"""
    question_id: int
    prompt: str
    total_attempts: int
    correct_attempts: int
    accuracy: float


class LowestAccuracyQuestionsResponse(BaseModel):
    """DTO for lowest accuracy questions response"""
    questions: List[QuestionAccuracy]
    count: int
