from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.favorite import FavoriteList, FavoriteItem


class FavoriteListRepository(ABC):
    """Abstract repository for FavoriteList entity"""
    
    @abstractmethod
    async def create(self, favorite_list: FavoriteList) -> FavoriteList:
        """Create a new favorite list"""
        pass
    
    @abstractmethod
    async def get_by_id(self, list_id: int) -> Optional[FavoriteList]:
        """Get favorite list by ID"""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FavoriteList]:
        """Get all favorite lists for a user"""
        pass
    
    @abstractmethod
    async def get_default_for_user(self, user_id: int) -> Optional[FavoriteList]:
        """Get the default favorite list for a user"""
        pass
    
    @abstractmethod
    async def update(self, list_id: int, list_data: dict) -> Optional[FavoriteList]:
        """Update favorite list by ID"""
        pass
    
    @abstractmethod
    async def delete(self, list_id: int) -> bool:
        """Delete favorite list by ID"""
        pass
    
    @abstractmethod
    async def get_question_count(self, list_id: int) -> int:
        """Get count of questions in a favorite list"""
        pass

    @abstractmethod
    async def get_flashcard_count(self, list_id: int) -> int:
        """Get count of flashcards in a favorite list"""
        pass


class FavoriteItemRepository(ABC):
    """Abstract repository for FavoriteItem entity"""
    
    @abstractmethod
    async def add_question(self, favorite_list_id: int, question_id: int) -> FavoriteItem:
        """Add a question to a favorite list"""
        pass

    @abstractmethod
    async def add_flashcard(self, favorite_list_id: int, flashcard_id: int) -> FavoriteItem:
        """Add a flashcard to a favorite list"""
        pass
    
    @abstractmethod
    async def remove_question(self, favorite_list_id: int, question_id: int) -> bool:
        """Remove a question from a favorite list"""
        pass

    @abstractmethod
    async def remove_flashcard(self, favorite_list_id: int, flashcard_id: int) -> bool:
        """Remove a flashcard from a favorite list"""
        pass
    
    @abstractmethod
    async def is_question_in_list(self, favorite_list_id: int, question_id: int) -> bool:
        """Check if a question is in a favorite list"""
        pass

    @abstractmethod
    async def is_flashcard_in_list(self, favorite_list_id: int, flashcard_id: int) -> bool:
        """Check if a flashcard is in a favorite list"""
        pass
    
    @abstractmethod
    async def get_questions_in_list(self, favorite_list_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all questions in a favorite list with question details"""
        pass

    @abstractmethod
    async def get_flashcards_in_list(self, favorite_list_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all flashcards in a favorite list with flashcard details"""
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[FavoriteItem]:
        """Get favorite item by ID"""
        pass
