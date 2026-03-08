from typing import List, Optional
from app.domain.entities.flashcard import (
    FlashCard,
    FlashCardCreate,
    FlashCardUpdate,
    FlashCardSet,
    FlashCardSetCreate,
    FlashCardSetUpdate,
    FlashCardKnowledgeStatus
)
from app.domain.repositories.flashcard_repository import (
    FlashCardRepository,
    FlashCardSetRepository,
    FlashCardSessionRepository,
    FlashCardProgressRepository
)


class FlashCardService:
    """Service for flash card operations"""

    def __init__(
        self,
        flashcard_repository: FlashCardRepository,
        flashcard_set_repository: FlashCardSetRepository,
        flashcard_session_repository: FlashCardSessionRepository,
        flashcard_progress_repository: FlashCardProgressRepository
    ):
        self.flashcard_repository = flashcard_repository
        self.flashcard_set_repository = flashcard_set_repository
        self.flashcard_session_repository = flashcard_session_repository
        self.flashcard_progress_repository = flashcard_progress_repository

    async def create_flashcard(self, flashcard_data: FlashCardCreate, created_by: Optional[int]) -> FlashCard:
        flashcard = FlashCard(
            word_front=flashcard_data.word_front,
            word_back=flashcard_data.word_back,
            example_sentences=flashcard_data.example_sentences,
            created_by=created_by
        )
        return await self.flashcard_repository.create(flashcard)

    async def get_flashcard(self, flashcard_id: int) -> Optional[FlashCard]:
        return await self.flashcard_repository.get_by_id(flashcard_id)

    async def list_flashcards(self, skip: int = 0, limit: int = 100) -> List[FlashCard]:
        return await self.flashcard_repository.get_all(skip, limit)

    async def list_flashcards_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FlashCard]:
        return await self.flashcard_repository.get_by_creator(user_id, skip, limit)

    async def update_flashcard(self, flashcard_id: int, flashcard_data: FlashCardUpdate) -> Optional[FlashCard]:
        update_dict = flashcard_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.flashcard_repository.get_by_id(flashcard_id)
        return await self.flashcard_repository.update(flashcard_id, update_dict)

    async def delete_flashcard(self, flashcard_id: int) -> bool:
        return await self.flashcard_repository.delete(flashcard_id)


class FlashCardSetService:
    """Service for flash card set operations"""

    def __init__(
        self,
        flashcard_set_repository: FlashCardSetRepository,
        flashcard_session_repository: FlashCardSessionRepository,
        flashcard_progress_repository: FlashCardProgressRepository
    ):
        self.flashcard_set_repository = flashcard_set_repository
        self.flashcard_session_repository = flashcard_session_repository
        self.flashcard_progress_repository = flashcard_progress_repository

    async def create_set(self, set_data: FlashCardSetCreate, created_by: Optional[int]) -> FlashCardSet:
        flashcard_set = FlashCardSet(
            name=set_data.name,
            description=set_data.description,
            created_by=created_by
        )
        return await self.flashcard_set_repository.create(flashcard_set)

    async def get_set(self, set_id: int) -> Optional[FlashCardSet]:
        return await self.flashcard_set_repository.get_by_id(set_id)

    async def list_sets(self, skip: int = 0, limit: int = 100) -> List[FlashCardSet]:
        return await self.flashcard_set_repository.get_all(skip, limit)

    async def list_sets_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FlashCardSet]:
        return await self.flashcard_set_repository.get_by_creator(user_id, skip, limit)

    async def update_set(self, set_id: int, set_data: FlashCardSetUpdate) -> Optional[FlashCardSet]:
        update_dict = set_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.flashcard_set_repository.get_by_id(set_id)
        return await self.flashcard_set_repository.update(set_id, update_dict)

    async def delete_set(self, set_id: int) -> bool:
        return await self.flashcard_set_repository.delete(set_id)

    async def add_flashcard_to_set(self, set_id: int, flashcard_id: int) -> tuple[bool, bool]:
        return await self.flashcard_set_repository.add_flashcard_to_set(set_id, flashcard_id)

    async def remove_flashcard_from_set(self, set_id: int, flashcard_id: int) -> bool:
        return await self.flashcard_set_repository.remove_flashcard_from_set(set_id, flashcard_id)

    async def get_flashcards_in_set(self, set_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.flashcard_set_repository.get_flashcards_in_set(set_id, skip, limit)

    async def get_flashcard_count_in_set(self, set_id: int) -> int:
        return await self.flashcard_set_repository.get_flashcard_count_in_set(set_id)

    async def start_session(self, user_id: int, set_id: int) -> dict:
        return await self.flashcard_session_repository.create_session(user_id, set_id)

    async def update_progress(
        self,
        user_id: int,
        set_id: int,
        flashcard_id: int,
        status: FlashCardKnowledgeStatus
    ) -> dict:
        return await self.flashcard_progress_repository.upsert_progress(user_id, set_id, flashcard_id, status)

    async def get_progress(self, user_id: int, set_id: int) -> List[dict]:
        return await self.flashcard_progress_repository.get_progress_for_set(user_id, set_id)
