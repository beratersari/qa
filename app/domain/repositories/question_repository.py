from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.question import Question, QuestionSet


class QuestionRepository(ABC):
    """Abstract repository for Question entity"""

    @abstractmethod
    async def create(self, question: Question) -> Question:
        """Create a new question"""
        pass

    @abstractmethod
    async def get_by_id(self, question_id: int) -> Optional[Question]:
        """Get question by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get all questions with pagination"""
        pass

    @abstractmethod
    async def update(self, question_id: int, question_data: dict) -> Optional[Question]:
        """Update question by ID"""
        pass

    @abstractmethod
    async def delete(self, question_id: int) -> bool:
        """Delete question by ID"""
        pass

    @abstractmethod
    async def get_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get questions created by a user"""
        pass


class QuestionSetRepository(ABC):
    """Abstract repository for QuestionSet entity"""

    @abstractmethod
    async def create(self, question_set: QuestionSet) -> QuestionSet:
        """Create a new question set"""
        pass

    @abstractmethod
    async def get_by_id(self, set_id: int) -> Optional[QuestionSet]:
        """Get question set by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
        """Get all question sets with pagination"""
        pass

    @abstractmethod
    async def get_by_type(self, set_type: str, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
        """Get question sets by type (normal/premium)"""
        pass

    @abstractmethod
    async def update(self, set_id: int, set_data: dict) -> Optional[QuestionSet]:
        """Update question set by ID"""
        pass

    @abstractmethod
    async def delete(self, set_id: int) -> bool:
        """Delete question set by ID"""
        pass

    @abstractmethod
    async def add_question_to_set(self, set_id: int, question_id: int) -> tuple[bool, bool]:
        """Add a question to a set. Returns (success, already_in_set)."""
        pass

    @abstractmethod
    async def remove_question_from_set(self, set_id: int, question_id: int) -> bool:
        """Remove a question from a set"""
        pass

    @abstractmethod
    async def get_questions_in_set(self, set_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all questions in a set"""
        pass

    @abstractmethod
    async def get_question_count_in_set(self, set_id: int) -> int:
        """Get count of questions in a set"""
        pass
