from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.flashcard import FlashCard


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
