from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.domain.entities.challenge import DailyChallenge, UserChallengeProgress
from app.domain.repositories.challenge_repository import ChallengeRepository
from app.infrastructure.database.models import DailyChallengeModel, UserChallengeProgressModel, QuestionModel
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemyChallengeRepository(ChallengeRepository):
    """SQLAlchemy implementation of ChallengeRepository"""

    def __init__(self, db: Session):
        self.db = db

    def _challenge_to_entity(self, model: DailyChallengeModel) -> DailyChallenge:
        return DailyChallenge(
            id=model.id,
            challenge_date=model.challenge_date,
            question_ids=model.question_ids or [],
            created_at=model.created_at
        )

    def _progress_to_entity(self, model: UserChallengeProgressModel) -> UserChallengeProgress:
        return UserChallengeProgress(
            id=model.id,
            user_id=model.user_id,
            challenge_id=model.challenge_id,
            completed_questions=model.completed_questions or [],
            is_completed=model.is_completed,
            xp_awarded=model.xp_awarded,
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def get_challenge_by_date(self, challenge_date: datetime) -> Optional[DailyChallenge]:
        """Get challenge by date"""
        model = self.db.query(DailyChallengeModel).filter(
            DailyChallengeModel.challenge_date == challenge_date
        ).first()
        if model:
            return self._challenge_to_entity(model)
        return None

    async def create_challenge(self, challenge: DailyChallenge) -> DailyChallenge:
        """Create a new daily challenge"""
        model = DailyChallengeModel(
            challenge_date=challenge.challenge_date,
            question_ids=challenge.question_ids
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        logger.info(
            "Created daily challenge",
            extra={"challenge_id": model.id, "challenge_date": str(challenge.challenge_date)}
        )

        return self._challenge_to_entity(model)

    async def get_user_progress(self, user_id: int, challenge_id: int) -> Optional[UserChallengeProgress]:
        """Get user's progress for a specific challenge"""
        model = self.db.query(UserChallengeProgressModel).filter(
            UserChallengeProgressModel.user_id == user_id,
            UserChallengeProgressModel.challenge_id == challenge_id
        ).first()
        if model:
            return self._progress_to_entity(model)
        return None

    async def create_user_progress(self, progress: UserChallengeProgress) -> UserChallengeProgress:
        """Create user progress record"""
        model = UserChallengeProgressModel(
            user_id=progress.user_id,
            challenge_id=progress.challenge_id,
            completed_questions=progress.completed_questions,
            is_completed=progress.is_completed,
            xp_awarded=progress.xp_awarded,
            completed_at=progress.completed_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._progress_to_entity(model)

    async def update_user_progress(self, progress_id: int, progress_data: dict) -> Optional[UserChallengeProgress]:
        """Update user progress"""
        model = self.db.query(UserChallengeProgressModel).filter(
            UserChallengeProgressModel.id == progress_id
        ).first()
        if not model:
            return None

        for key, value in progress_data.items():
            if hasattr(model, key):
                setattr(model, key, value)

        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        return self._progress_to_entity(model)

    async def upsert_user_progress(self, progress: UserChallengeProgress) -> UserChallengeProgress:
        """Create or update user progress"""
        existing = await self.get_user_progress(progress.user_id, progress.challenge_id)
        
        if existing:
            update_data = {
                "completed_questions": progress.completed_questions,
                "is_completed": progress.is_completed,
                "xp_awarded": progress.xp_awarded,
                "completed_at": progress.completed_at,
            }
            return await self.update_user_progress(existing.id, update_data)
        else:
            return await self.create_user_progress(progress)

    async def get_user_challenge_history(self, user_id: int, limit: int = 30) -> List[UserChallengeProgress]:
        """Get user's challenge history"""
        models = self.db.query(UserChallengeProgressModel).filter(
            UserChallengeProgressModel.user_id == user_id
        ).order_by(UserChallengeProgressModel.created_at.desc()).limit(limit).all()
        return [self._progress_to_entity(m) for m in models]

    async def get_random_question_ids(self, count: int = 5) -> List[int]:
        """Get random question IDs for challenge"""
        # Use SQLAlchemy's random function to get random questions
        models = self.db.query(QuestionModel.id).order_by(func.random()).limit(count).all()
        return [m[0] for m in models]
