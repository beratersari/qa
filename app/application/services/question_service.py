from typing import List, Optional
from app.domain.entities.question import (
    Question, QuestionCreate, QuestionUpdate,
    QuestionSet, QuestionSetCreate, QuestionSetUpdate, QuestionSetType
)
from app.domain.repositories.question_repository import QuestionRepository, QuestionSetRepository


class QuestionService:
    """Service for question operations"""

    def __init__(self, question_repository: QuestionRepository):
        self.question_repository = question_repository

    async def create_question(self, question_data: QuestionCreate, created_by: Optional[int]) -> Question:
        question = Question(
            prompt=question_data.prompt,
            choices=question_data.choices,
            answer_index=question_data.answer_index,
            difficulty_level=question_data.difficulty_level,
            created_by=created_by
        )
        return await self.question_repository.create(question)

    async def get_question(self, question_id: int) -> Optional[Question]:
        return await self.question_repository.get_by_id(question_id)

    async def list_questions(self, skip: int = 0, limit: int = 100) -> List[Question]:
        return await self.question_repository.get_all(skip, limit)

    async def list_questions_by_creator(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        return await self.question_repository.get_by_creator(user_id, skip, limit)

    async def update_question(self, question_id: int, question_data: QuestionUpdate) -> Optional[Question]:
        update_dict = question_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.question_repository.get_by_id(question_id)
        return await self.question_repository.update(question_id, update_dict)

    async def delete_question(self, question_id: int) -> bool:
        return await self.question_repository.delete(question_id)


class QuestionSetService:
    """Service for question set operations"""

    def __init__(self, question_set_repository: QuestionSetRepository):
        self.question_set_repository = question_set_repository

    async def create_set(self, set_data: QuestionSetCreate, created_by: Optional[int]) -> QuestionSet:
        question_set = QuestionSet(
            name=set_data.name,
            description=set_data.description,
            set_type=set_data.set_type,
            created_by=created_by
        )
        return await self.question_set_repository.create(question_set)

    async def get_set(self, set_id: int) -> Optional[QuestionSet]:
        return await self.question_set_repository.get_by_id(set_id)

    async def list_sets(self, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
        return await self.question_set_repository.get_all(skip, limit)

    async def list_sets_by_type(self, set_type: QuestionSetType, skip: int = 0, limit: int = 100) -> List[QuestionSet]:
        return await self.question_set_repository.get_by_type(set_type.value, skip, limit)

    async def update_set(self, set_id: int, set_data: QuestionSetUpdate) -> Optional[QuestionSet]:
        update_dict = set_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.question_set_repository.get_by_id(set_id)
        return await self.question_set_repository.update(set_id, update_dict)

    async def delete_set(self, set_id: int) -> bool:
        return await self.question_set_repository.delete(set_id)

    async def add_question_to_set(self, set_id: int, question_id: int) -> tuple[bool, bool]:
        return await self.question_set_repository.add_question_to_set(set_id, question_id)

    async def remove_question_from_set(self, set_id: int, question_id: int) -> bool:
        return await self.question_set_repository.remove_question_from_set(set_id, question_id)

    async def get_questions_in_set(self, set_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.question_set_repository.get_questions_in_set(set_id, skip, limit)

    async def get_question_count_in_set(self, set_id: int) -> int:
        return await self.question_set_repository.get_question_count_in_set(set_id)
