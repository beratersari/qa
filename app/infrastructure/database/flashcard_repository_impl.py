from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.flashcard import FlashCard, FlashCardSet, FlashCardKnowledgeStatus
from app.domain.repositories.flashcard_repository import (
    FlashCardRepository,
    FlashCardSetRepository,
    FlashCardSessionRepository,
    FlashCardProgressRepository
)
from app.infrastructure.database.models import (
    FlashCardModel,
    FlashCardSetModel,
    FlashCardSetItemModel,
    FlashCardSessionModel,
    FlashCardProgressModel
)


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


class SQLAlchemyFlashCardSetRepository(FlashCardSetRepository):
    """SQLAlchemy implementation of FlashCardSetRepository"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: FlashCardSetModel) -> FlashCardSet:
        return FlashCardSet(
            id=model.id,
            name=model.name,
            description=model.description,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, flashcard_set: FlashCardSet) -> FlashCardSet:
        db_set = FlashCardSetModel(
            name=flashcard_set.name,
            description=flashcard_set.description,
            created_by=flashcard_set.created_by
        )
        self.db.add(db_set)
        self.db.commit()
        self.db.refresh(db_set)
        return self._to_entity(db_set)

    async def get_by_id(self, set_id: int) -> Optional[FlashCardSet]:
        db_set = self.db.query(FlashCardSetModel).filter(FlashCardSetModel.id == set_id).first()
        if db_set:
            return self._to_entity(db_set)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FlashCardSet]:
        db_sets = self.db.query(FlashCardSetModel).offset(skip).limit(limit).all()
        return [self._to_entity(s) for s in db_sets]

    async def get_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FlashCardSet]:
        db_sets = (
            self.db.query(FlashCardSetModel)
            .filter(FlashCardSetModel.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(s) for s in db_sets]

    async def update(self, set_id: int, set_data: dict) -> Optional[FlashCardSet]:
        db_set = self.db.query(FlashCardSetModel).filter(FlashCardSetModel.id == set_id).first()
        if not db_set:
            return None

        for key, value in set_data.items():
            if hasattr(db_set, key):
                setattr(db_set, key, value)

        db_set.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_set)
        return self._to_entity(db_set)

    async def delete(self, set_id: int) -> bool:
        db_set = self.db.query(FlashCardSetModel).filter(FlashCardSetModel.id == set_id).first()
        if not db_set:
            return False

        self.db.delete(db_set)
        self.db.commit()
        return True

    async def add_flashcard_to_set(self, set_id: int, flashcard_id: int) -> tuple[bool, bool]:
        db_set = self.db.query(FlashCardSetModel).filter(FlashCardSetModel.id == set_id).first()
        db_flashcard = self.db.query(FlashCardModel).filter(FlashCardModel.id == flashcard_id).first()

        if not db_set or not db_flashcard:
            return False, False

        existing_link = (
            self.db.query(FlashCardSetItemModel)
            .filter(
                FlashCardSetItemModel.set_id == set_id,
                FlashCardSetItemModel.flashcard_id == flashcard_id
            )
            .first()
        )
        if existing_link:
            return True, True

        link = FlashCardSetItemModel(set_id=set_id, flashcard_id=flashcard_id)
        self.db.add(link)
        self.db.commit()
        return True, False

    async def remove_flashcard_from_set(self, set_id: int, flashcard_id: int) -> bool:
        link = (
            self.db.query(FlashCardSetItemModel)
            .filter(
                FlashCardSetItemModel.set_id == set_id,
                FlashCardSetItemModel.flashcard_id == flashcard_id
            )
            .first()
        )
        if not link:
            return False

        self.db.delete(link)
        self.db.commit()
        return True

    async def get_flashcards_in_set(self, set_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        links = (
            self.db.query(FlashCardSetItemModel)
            .filter(FlashCardSetItemModel.set_id == set_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [
            {
                "id": link.flashcard.id,
                "word_front": link.flashcard.word_front,
                "word_back": link.flashcard.word_back,
                "example_sentences": link.flashcard.example_sentences or [],
                "set_id": link.set_id,
                "created_by": link.flashcard.created_by,
                "created_at": link.flashcard.created_at,
                "updated_at": link.flashcard.updated_at
            }
            for link in links
            if link.flashcard
        ]

    async def get_flashcard_count_in_set(self, set_id: int) -> int:
        return (
            self.db.query(FlashCardSetItemModel)
            .filter(FlashCardSetItemModel.set_id == set_id)
            .count()
        )


class SQLAlchemyFlashCardSessionRepository(FlashCardSessionRepository):
    """SQLAlchemy implementation of FlashCardSessionRepository"""

    def __init__(self, db: Session):
        self.db = db

    async def create_session(self, user_id: int, set_id: int) -> dict:
        session = FlashCardSessionModel(user_id=user_id, set_id=set_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return {
            "id": session.id,
            "user_id": session.user_id,
            "set_id": session.set_id,
            "started_at": session.started_at
        }


class SQLAlchemyFlashCardProgressRepository(FlashCardProgressRepository):
    """SQLAlchemy implementation of FlashCardProgressRepository"""

    def __init__(self, db: Session):
        self.db = db

    async def upsert_progress(self, user_id: int, set_id: int, flashcard_id: int, status: FlashCardKnowledgeStatus) -> dict:
        progress = (
            self.db.query(FlashCardProgressModel)
            .filter(
                FlashCardProgressModel.user_id == user_id,
                FlashCardProgressModel.set_id == set_id,
                FlashCardProgressModel.flashcard_id == flashcard_id
            )
            .first()
        )

        if progress:
            progress.status = status.value
            progress.updated_at = datetime.utcnow()
        else:
            progress = FlashCardProgressModel(
                user_id=user_id,
                set_id=set_id,
                flashcard_id=flashcard_id,
                status=status.value
            )
            self.db.add(progress)

        self.db.commit()
        self.db.refresh(progress)
        return {
            "id": progress.id,
            "user_id": progress.user_id,
            "set_id": progress.set_id,
            "flashcard_id": progress.flashcard_id,
            "status": progress.status,
            "updated_at": progress.updated_at
        }

    async def get_progress_for_set(self, user_id: int, set_id: int) -> List[dict]:
        progress_items = (
            self.db.query(FlashCardProgressModel)
            .filter(
                FlashCardProgressModel.user_id == user_id,
                FlashCardProgressModel.set_id == set_id
            )
            .all()
        )
        return [
            {
                "id": item.id,
                "user_id": item.user_id,
                "set_id": item.set_id,
                "flashcard_id": item.flashcard_id,
                "status": item.status,
                "updated_at": item.updated_at
            }
            for item in progress_items
        ]
