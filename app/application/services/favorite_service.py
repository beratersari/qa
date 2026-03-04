from typing import List, Optional
from app.domain.entities.favorite import (
    FavoriteList, FavoriteListCreate, FavoriteListUpdate,
    FavoriteItem, AddQuestionToFavorite, FavoriteListPrivacy
)
from app.domain.repositories.favorite_repository import FavoriteListRepository, FavoriteItemRepository


class FavoriteService:
    """Service for favorite list operations"""
    
    def __init__(self, favorite_list_repo: FavoriteListRepository, favorite_item_repo: FavoriteItemRepository):
        self.favorite_list_repo = favorite_list_repo
        self.favorite_item_repo = favorite_item_repo
    
    async def create_favorite_list(self, list_data: FavoriteListCreate, user_id: int) -> FavoriteList:
        """Create a new favorite list for a user"""
        shared_with_usernames = list_data.shared_with_usernames
        if list_data.privacy != FavoriteListPrivacy.SHARED:
            shared_with_usernames = []
        favorite_list = FavoriteList(
            name=list_data.name,
            description=list_data.description,
            user_id=user_id,
            is_default=False,
            privacy=list_data.privacy,
            shared_with_usernames=shared_with_usernames
        )
        return await self.favorite_list_repo.create(favorite_list)
    
    async def create_default_favorite_list(self, user_id: int) -> FavoriteList:
        """Create a default favorite list for a user"""
        favorite_list = FavoriteList(
            name="Favorites",
            description="My default favorites list",
            user_id=user_id,
            is_default=True,
            privacy=FavoriteListPrivacy.PRIVATE,
            shared_with_usernames=[]
        )
        return await self.favorite_list_repo.create(favorite_list)
    
    async def get_favorite_list(self, list_id: int) -> Optional[FavoriteList]:
        """Get a favorite list by ID"""
        return await self.favorite_list_repo.get_by_id(list_id)
    
    async def get_user_favorite_lists(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FavoriteList]:
        """Get all favorite lists for a user"""
        return await self.favorite_list_repo.get_by_user(user_id, skip, limit)
    
    async def get_default_favorite_list(self, user_id: int) -> Optional[FavoriteList]:
        """Get the default favorite list for a user"""
        return await self.favorite_list_repo.get_default_for_user(user_id)
    
    async def update_favorite_list(self, list_id: int, list_data: FavoriteListUpdate) -> Optional[FavoriteList]:
        """Update a favorite list"""
        update_dict = list_data.model_dump(exclude_unset=True)
        privacy = update_dict.get("privacy")
        if privacy is not None and hasattr(privacy, "value"):
            update_dict["privacy"] = privacy.value
        if "privacy" in update_dict and update_dict["privacy"] != FavoriteListPrivacy.SHARED.value:
            update_dict["shared_with_usernames"] = []
        if "privacy" in update_dict and update_dict["privacy"] == FavoriteListPrivacy.SHARED.value:
            if update_dict.get("shared_with_usernames") is None:
                update_dict["shared_with_usernames"] = []
        if not update_dict:
            return await self.favorite_list_repo.get_by_id(list_id)
        return await self.favorite_list_repo.update(list_id, update_dict)
    
    async def delete_favorite_list(self, list_id: int) -> bool:
        """Delete a favorite list (cannot delete default list)"""
        favorite_list = await self.favorite_list_repo.get_by_id(list_id)
        if not favorite_list:
            return False
        if favorite_list.is_default:
            return False  # Cannot delete default list
        return await self.favorite_list_repo.delete(list_id)
    
    async def get_question_count(self, list_id: int) -> int:
        """Get count of questions in a favorite list"""
        return await self.favorite_list_repo.get_question_count(list_id)

    async def get_flashcard_count(self, list_id: int) -> int:
        """Get count of flashcards in a favorite list"""
        return await self.favorite_list_repo.get_flashcard_count(list_id)
    
    async def add_question_to_list(self, list_id: int, question_id: int) -> tuple[bool, bool]:
        """Add a question to a favorite list. Returns (success, already_in_list)."""
        # Check if list exists
        favorite_list = await self.favorite_list_repo.get_by_id(list_id)
        if not favorite_list:
            return False, False
        
        # Check if question is already in list
        is_in_list = await self.favorite_item_repo.is_question_in_list(list_id, question_id)
        if is_in_list:
            return True, True
        
        # Add question to list
        await self.favorite_item_repo.add_question(list_id, question_id)
        return True, False

    async def add_flashcard_to_list(self, list_id: int, flashcard_id: int) -> tuple[bool, bool]:
        """Add a flashcard to a favorite list. Returns (success, already_in_list)."""
        # Check if list exists
        favorite_list = await self.favorite_list_repo.get_by_id(list_id)
        if not favorite_list:
            return False, False

        # Check if flashcard is already in list
        is_in_list = await self.favorite_item_repo.is_flashcard_in_list(list_id, flashcard_id)
        if is_in_list:
            return True, True

        # Add flashcard to list
        await self.favorite_item_repo.add_flashcard(list_id, flashcard_id)
        return True, False
    
    async def remove_question_from_list(self, list_id: int, question_id: int) -> bool:
        """Remove a question from a favorite list"""
        return await self.favorite_item_repo.remove_question(list_id, question_id)

    async def remove_flashcard_from_list(self, list_id: int, flashcard_id: int) -> bool:
        """Remove a flashcard from a favorite list"""
        return await self.favorite_item_repo.remove_flashcard(list_id, flashcard_id)
    
    async def get_questions_in_list(self, list_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all questions in a favorite list"""
        return await self.favorite_item_repo.get_questions_in_list(list_id, skip, limit)

    async def get_flashcards_in_list(self, list_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all flashcards in a favorite list"""
        return await self.favorite_item_repo.get_flashcards_in_list(list_id, skip, limit)
    
    async def is_question_in_any_user_list(self, user_id: int, question_id: int) -> bool:
        """Check if a question is in any of the user's favorite lists"""
        lists = await self.favorite_list_repo.get_by_user(user_id)
        for lst in lists:
            if await self.favorite_item_repo.is_question_in_list(lst.id, question_id):
                return True
        return False

    async def is_flashcard_in_any_user_list(self, user_id: int, flashcard_id: int) -> bool:
        """Check if a flashcard is in any of the user's favorite lists"""
        lists = await self.favorite_list_repo.get_by_user(user_id)
        for lst in lists:
            if await self.favorite_item_repo.is_flashcard_in_list(lst.id, flashcard_id):
                return True
        return False
