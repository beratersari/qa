from typing import List, Optional
from app.domain.entities.flashcard import FlashCard, FlashCardCreate, FlashCardUpdate
from app.domain.repositories.flashcard_repository import FlashCardRepository


class FlashCardService:
    """Service for flash card operations"""

    def __init__(self, flashcard_repository: FlashCardRepository):
        self.flashcard_repository = flashcard_repository

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
