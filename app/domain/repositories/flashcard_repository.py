from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.flashcard import FlashCard, FlashCardSet, FlashCardKnowledgeStatus


class FlashCardRepository(ABC):
    """Abstract repository for FlashCard entity"""

    @abstractmethod
    async def create(self, flashcard: FlashCard) -> FlashCard:
        """Create a new flash card"""
        pass

    @abstractmethod
    async def get_by_id(self, flashcard_id: int) -> Optional[FlashCard]:
        """Get flash card by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FlashCard]:
        """Get all flash cards with pagination"""
        pass

    @abstractmethod
    async def update(self, flashcard_id: int, flashcard_data: dict) -> Optional[FlashCard]:
        """Update flash card by ID"""
        pass

    @abstractmethod
    async def delete(self, flashcard_id: int) -> bool:
        """Delete flash card by ID"""
        pass

    @abstractmethod
    async def get_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FlashCard]:
        """Get flash cards created by a user"""
        pass


class FlashCardSetRepository(ABC):
    """Abstract repository for FlashCardSet entity"""

    @abstractmethod
    async def create(self, flashcard_set: FlashCardSet) -> FlashCardSet:
        """Create a new flash card set"""
        pass

    @abstractmethod
    async def get_by_id(self, set_id: int) -> Optional[FlashCardSet]:
        """Get flash card set by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FlashCardSet]:
        """Get all flash card sets with pagination"""
        pass

    @abstractmethod
    async def get_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FlashCardSet]:
        """Get flash card sets created by a user"""
        pass

    @abstractmethod
    async def update(self, set_id: int, set_data: dict) -> Optional[FlashCardSet]:
        """Update flash card set by ID"""
        pass

    @abstractmethod
    async def delete(self, set_id: int) -> bool:
        """Delete flash card set by ID"""
        pass

    @abstractmethod
    async def add_flashcard_to_set(self, set_id: int, flashcard_id: int) -> tuple[bool, bool]:
        """Add a flash card to a set. Returns (success, already_in_set)."""
        pass

    @abstractmethod
    async def remove_flashcard_from_set(self, set_id: int, flashcard_id: int) -> bool:
        """Remove a flash card from a set"""
        pass

    @abstractmethod
    async def get_flashcards_in_set(self, set_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all flash cards in a set"""
        pass

    @abstractmethod
    async def get_flashcard_count_in_set(self, set_id: int) -> int:
        """Get count of flash cards in a set"""
        pass


class FlashCardSessionRepository(ABC):
    """Abstract repository for FlashCard sessions"""

    @abstractmethod
    async def create_session(self, user_id: int, set_id: int) -> dict:
        """Create a flash card session"""
        pass


class FlashCardProgressRepository(ABC):
    """Abstract repository for FlashCard progress"""

    @abstractmethod
    async def upsert_progress(self, user_id: int, set_id: int, flashcard_id: int, status: FlashCardKnowledgeStatus) -> dict:
        """Upsert flash card progress"""
        pass

    @abstractmethod
    async def get_progress_for_set(self, user_id: int, set_id: int) -> List[dict]:
        """Get flash card progress for set"""
        pass
