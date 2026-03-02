from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.flashcard import FlashCard
from app.domain.repositories.flashcard_repository import FlashCardRepository
from app.infrastructure.database.models import FlashCardModel


class SQLAlchemyFlashCardRepository(FlashCardRepository):
    """SQLAlchemy implementation of FlashCardRepository"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: FlashCardModel) -> FlashCard:
        return FlashCard(
            id=model.id,
            word_front=model.word_front,
            word_back=model.word_back,
            example_sentences=model.example_sentences or [],
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, flashcard: FlashCard) -> FlashCard:
        db_flashcard = FlashCardModel(
            word_front=flashcard.word_front,
            word_back=flashcard.word_back,
            example_sentences=flashcard.example_sentences,
            created_by=flashcard.created_by
        )
        self.db.add(db_flashcard)
        self.db.commit()
        self.db.refresh(db_flashcard)
        return self._to_entity(db_flashcard)

    async def get_by_id(self, flashcard_id: int) -> Optional[FlashCard]:
        db_card = self.db.query(FlashCardModel).filter(FlashCardModel.id == flashcard_id).first()
        if db_card:
            return self._to_entity(db_card)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FlashCard]:
        db_cards = self.db.query(FlashCardModel).offset(skip).limit(limit).all()
        return [self._to_entity(card) for card in db_cards]

    async def update(self, flashcard_id: int, flashcard_data: dict) -> Optional[FlashCard]:
        db_card = self.db.query(FlashCardModel).filter(FlashCardModel.id == flashcard_id).first()
        if not db_card:
            return None

        for key, value in flashcard_data.items():
            if hasattr(db_card, key):
                setattr(db_card, key, value)

        db_card.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_card)
        return self._to_entity(db_card)

    async def delete(self, flashcard_id: int) -> bool:
        db_card = self.db.query(FlashCardModel).filter(FlashCardModel.id == flashcard_id).first()
        if not db_card:
            return False

        self.db.delete(db_card)
        self.db.commit()
        return True

    async def get_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FlashCard]:
        db_cards = (
            self.db.query(FlashCardModel)
            .filter(FlashCardModel.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(card) for card in db_cards]
