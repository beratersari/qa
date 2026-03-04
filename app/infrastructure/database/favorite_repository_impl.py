from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.favorite import FavoriteList, FavoriteItem
from app.domain.repositories.favorite_repository import FavoriteListRepository, FavoriteItemRepository
from app.infrastructure.database.models import (
    FavoriteListModel,
    FavoriteQuestionModel,
    FavoriteFlashcardModel,
    QuestionModel,
    FlashCardModel
)


class SQLAlchemyFavoriteListRepository(FavoriteListRepository):
    """SQLAlchemy implementation of FavoriteListRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: FavoriteListModel) -> FavoriteList:
        """Convert database model to domain entity"""
        return FavoriteList(
            id=model.id,
            name=model.name,
            description=model.description,
            user_id=model.user_id,
            is_default=model.is_default,
            privacy=model.privacy,
            shared_with_usernames=model.shared_with_usernames or [],
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    async def create(self, favorite_list: FavoriteList) -> FavoriteList:
        """Create a new favorite list"""
        db_list = FavoriteListModel(
            name=favorite_list.name,
            description=favorite_list.description,
            user_id=favorite_list.user_id,
            is_default=favorite_list.is_default,
            privacy=favorite_list.privacy.value if hasattr(favorite_list.privacy, "value") else favorite_list.privacy,
            shared_with_usernames=favorite_list.shared_with_usernames
        )
        self.db.add(db_list)
        self.db.commit()
        self.db.refresh(db_list)
        return self._to_entity(db_list)
    
    async def get_by_id(self, list_id: int) -> Optional[FavoriteList]:
        """Get favorite list by ID"""
        db_list = self.db.query(FavoriteListModel).filter(FavoriteListModel.id == list_id).first()
        if db_list:
            return self._to_entity(db_list)
        return None
    
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FavoriteList]:
        """Get all favorite lists for a user"""
        db_lists = (
            self.db.query(FavoriteListModel)
            .filter(FavoriteListModel.user_id == user_id)
            .order_by(FavoriteListModel.is_default.desc(), FavoriteListModel.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(lst) for lst in db_lists]
    
    async def get_default_for_user(self, user_id: int) -> Optional[FavoriteList]:
        """Get the default favorite list for a user"""
        db_list = (
            self.db.query(FavoriteListModel)
            .filter(FavoriteListModel.user_id == user_id, FavoriteListModel.is_default == True)
            .first()
        )
        if db_list:
            return self._to_entity(db_list)
        return None
    
    async def update(self, list_id: int, list_data: dict) -> Optional[FavoriteList]:
        """Update favorite list by ID"""
        db_list = self.db.query(FavoriteListModel).filter(FavoriteListModel.id == list_id).first()
        if not db_list:
            return None
        
        for key, value in list_data.items():
            if hasattr(db_list, key):
                setattr(db_list, key, value)
        
        db_list.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_list)
        return self._to_entity(db_list)
    
    async def delete(self, list_id: int) -> bool:
        """Delete favorite list by ID"""
        db_list = self.db.query(FavoriteListModel).filter(FavoriteListModel.id == list_id).first()
        if not db_list:
            return False
        
        self.db.delete(db_list)
        self.db.commit()
        return True
    
    async def get_question_count(self, list_id: int) -> int:
        """Get count of questions in a favorite list"""
        return self.db.query(FavoriteQuestionModel).filter(FavoriteQuestionModel.favorite_list_id == list_id).count()

    async def get_flashcard_count(self, list_id: int) -> int:
        """Get count of flashcards in a favorite list"""
        return self.db.query(FavoriteFlashcardModel).filter(FavoriteFlashcardModel.favorite_list_id == list_id).count()


class SQLAlchemyFavoriteItemRepository(FavoriteItemRepository):
    """SQLAlchemy implementation of FavoriteItemRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: FavoriteQuestionModel) -> FavoriteItem:
        """Convert database model to domain entity"""
        return FavoriteItem(
            id=model.id,
            favorite_list_id=model.favorite_list_id,
            question_id=model.question_id,
            added_at=model.added_at
        )
    
    async def add_question(self, favorite_list_id: int, question_id: int) -> FavoriteItem:
        """Add a question to a favorite list"""
        db_item = FavoriteQuestionModel(
            favorite_list_id=favorite_list_id,
            question_id=question_id
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return self._to_entity(db_item)

    async def add_flashcard(self, favorite_list_id: int, flashcard_id: int) -> FavoriteItem:
        """Add a flashcard to a favorite list"""
        db_item = FavoriteFlashcardModel(
            favorite_list_id=favorite_list_id,
            flashcard_id=flashcard_id
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return FavoriteItem(
            id=db_item.id,
            favorite_list_id=db_item.favorite_list_id,
            flashcard_id=flashcard_id,
            added_at=db_item.added_at
        )
    
    async def remove_question(self, favorite_list_id: int, question_id: int) -> bool:
        """Remove a question from a favorite list"""
        db_item = (
            self.db.query(FavoriteQuestionModel)
            .filter(
                FavoriteQuestionModel.favorite_list_id == favorite_list_id,
                FavoriteQuestionModel.question_id == question_id
            )
            .first()
        )
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True

    async def remove_flashcard(self, favorite_list_id: int, flashcard_id: int) -> bool:
        """Remove a flashcard from a favorite list"""
        db_item = (
            self.db.query(FavoriteFlashcardModel)
            .filter(
                FavoriteFlashcardModel.favorite_list_id == favorite_list_id,
                FavoriteFlashcardModel.flashcard_id == flashcard_id
            )
            .first()
        )
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True
    
    async def is_question_in_list(self, favorite_list_id: int, question_id: int) -> bool:
        """Check if a question is in a favorite list"""
        return (
            self.db.query(FavoriteQuestionModel)
            .filter(
                FavoriteQuestionModel.favorite_list_id == favorite_list_id,
                FavoriteQuestionModel.question_id == question_id
            )
            .first()
            is not None
        )

    async def is_flashcard_in_list(self, favorite_list_id: int, flashcard_id: int) -> bool:
        """Check if a flashcard is in a favorite list"""
        return (
            self.db.query(FavoriteFlashcardModel)
            .filter(
                FavoriteFlashcardModel.favorite_list_id == favorite_list_id,
                FavoriteFlashcardModel.flashcard_id == flashcard_id
            )
            .first()
            is not None
        )
    
    async def get_questions_in_list(self, favorite_list_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all questions in a favorite list with question details"""
        items = (
            self.db.query(FavoriteQuestionModel, QuestionModel)
            .join(QuestionModel, FavoriteQuestionModel.question_id == QuestionModel.id)
            .filter(FavoriteQuestionModel.favorite_list_id == favorite_list_id)
            .order_by(FavoriteQuestionModel.added_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for item, question in items:
            result.append({
                "id": item.id,
                "favorite_list_id": item.favorite_list_id,
                "question_id": question.id,
                "prompt": question.prompt,
                "choices": [{"letter": chr(65 + i), "text": choice} for i, choice in enumerate(question.choices or [])],
                "difficulty_level": question.difficulty_level,
                "added_at": item.added_at
            })
        return result

    async def get_flashcards_in_list(self, favorite_list_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all flashcards in a favorite list with flashcard details"""
        items = (
            self.db.query(FavoriteFlashcardModel, FlashCardModel)
            .join(FlashCardModel, FavoriteFlashcardModel.flashcard_id == FlashCardModel.id)
            .filter(FavoriteFlashcardModel.favorite_list_id == favorite_list_id)
            .order_by(FavoriteFlashcardModel.added_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for item, flashcard in items:
            result.append({
                "id": item.id,
                "favorite_list_id": item.favorite_list_id,
                "flashcard_id": flashcard.id,
                "word_front": flashcard.word_front,
                "word_back": flashcard.word_back,
                "example_sentences": flashcard.example_sentences or [],
                "added_at": item.added_at
            })
        return result
    
    async def get_by_id(self, item_id: int) -> Optional[FavoriteItem]:
        """Get favorite item by ID"""
        db_item = self.db.query(FavoriteQuestionModel).filter(FavoriteQuestionModel.id == item_id).first()
        if db_item:
            return self._to_entity(db_item)
        return None
