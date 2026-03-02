from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.question import Question, QuestionSet, QuestionSetType
from app.domain.repositories.question_repository import QuestionRepository, QuestionSetRepository
from app.infrastructure.database.models import QuestionModel, QuestionSetModel


class SQLAlchemyQuestionRepository(QuestionRepository):
    """SQLAlchemy implementation of QuestionRepository"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: QuestionModel) -> Question:
        return Question(
            id=model.id,
            prompt=model.prompt,
            choices=model.choices or [],
            answer_index=model.answer_index,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, question: Question) -> Question:
        db_question = QuestionModel(
            prompt=question.prompt,
            choices=question.choices,
            answer_index=question.answer_index,
            created_by=question.created_by
        )
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        return self._to_entity(db_question)

    async def get_by_id(self, question_id: int) -> Optional[Question]:
        db_question = self.db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if db_question:
            return self._to_entity(db_question)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Question]:
        db_questions = self.db.query(QuestionModel).offset(skip).limit(limit).all()
        return [self._to_entity(q) for q in db_questions]

    async def update(self, question_id: int, question_data: dict) -> Optional[Question]:
        db_question = self.db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not db_question:
            return None

        for key, value in question_data.items():
            if hasattr(db_question, key):
                setattr(db_question, key, value)

        db_question.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_question)
        return self._to_entity(db_question)

    async def delete(self, question_id: int) -> bool:
        db_question = self.db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not db_question:
            return False

        self.db.delete(db_question)
        self.db.commit()
        return True

    async def get_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        db_questions = (
            self.db.query(QuestionModel)
            .filter(QuestionModel.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(q) for q in db_questions]


class SQLAlchemyQuestionSetRepository(QuestionSetRepository):
    """SQLAlchemy implementation of QuestionSetRepository"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: QuestionSetModel) -> QuestionSet:
        return QuestionSet(
            id=model.id,
            name=model.name,
            description=model.description,
            set_type=model.set_type,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, question_set: QuestionSet) -> QuestionSet:
        db_set = QuestionSetModel(
            name=question_set.name,
            description=question_set.description,
            set_type=question_set.set_type,
            created_by=question_set.created_by
        )
        self.db.add(db_set)
        self.db.commit()
        self.db.refresh(db_set)
        return self._to_entity(db_set)

    async def get_by_id(self, set_id: int) -> Optional[QuestionSet]:
        db_set = self.db.query(QuestionSetModel).filter(QuestionSetModel.id == set_id).first()
        if db_set:
            return self._to_entity(db_set)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
        db_sets = self.db.query(QuestionSetModel).offset(skip).limit(limit).all()
        return [self._to_entity(s) for s in db_sets]

    async def get_by_type(self, set_type: str, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
        db_sets = (
            self.db.query(QuestionSetModel)
            .filter(QuestionSetModel.set_type == set_type)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(s) for s in db_sets]

    async def update(self, set_id: int, set_data: dict) -> Optional[QuestionSet]:
        db_set = self.db.query(QuestionSetModel).filter(QuestionSetModel.id == set_id).first()
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
        db_set = self.db.query(QuestionSetModel).filter(QuestionSetModel.id == set_id).first()
        if not db_set:
            return False

        self.db.delete(db_set)
        self.db.commit()
        return True

    async def add_question_to_set(self, set_id: int, question_id: int) -> tuple[bool, bool]:
        db_set = self.db.query(QuestionSetModel).filter(QuestionSetModel.id == set_id).first()
        db_question = self.db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        
        if not db_set or not db_question:
            return False, False
        
        # Check if already in set
        if db_question in db_set.questions:
            return True, True
        
        db_set.questions.append(db_question)
        self.db.commit()
        return True, False

    async def remove_question_from_set(self, set_id: int, question_id: int) -> bool:
        db_set = self.db.query(QuestionSetModel).filter(QuestionSetModel.id == set_id).first()
        db_question = self.db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        
        if not db_set or not db_question:
            return False
        
        if db_question not in db_set.questions:
            return False
        
        db_set.questions.remove(db_question)
        self.db.commit()
        return True

    async def get_questions_in_set(self, set_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        db_set = self.db.query(QuestionSetModel).filter(QuestionSetModel.id == set_id).first()
        if not db_set:
            return []
        
        questions = db_set.questions[skip:skip + limit]
        return [
            {
                "id": q.id,
                "prompt": q.prompt,
                "choices": [{"letter": chr(65 + i), "text": choice} for i, choice in enumerate(q.choices or [])],
                "set_id": set_id,
                "question_id": q.id
            }
            for q in questions
        ]

    async def get_question_count_in_set(self, set_id: int) -> int:
        db_set = self.db.query(QuestionSetModel).filter(QuestionSetModel.id == set_id).first()
        if not db_set:
            return 0
        return len(db_set.questions)
