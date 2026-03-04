from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.badge import Badge, UserBadge
from app.domain.repositories.badge_repository import BadgeRepository, UserBadgeRepository
from app.infrastructure.database.models import BadgeModel, UserBadgeModel


class SQLAlchemyBadgeRepository(BadgeRepository):
    """SQLAlchemy implementation for badges"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: BadgeModel) -> Badge:
        return Badge(
            id=model.id,
            name=model.name,
            description=model.description,
            icon_path=model.icon_path,
            conditions=model.conditions or [],
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, badge: Badge) -> Badge:
        db_badge = BadgeModel(
            name=badge.name,
            description=badge.description,
            icon_path=badge.icon_path,
            conditions=[condition.model_dump() for condition in badge.conditions] if badge.conditions else []
        )
        self.db.add(db_badge)
        self.db.commit()
        self.db.refresh(db_badge)
        return self._to_entity(db_badge)

    async def get_by_id(self, badge_id: int) -> Optional[Badge]:
        db_badge = self.db.query(BadgeModel).filter(BadgeModel.id == badge_id).first()
        if db_badge:
            return self._to_entity(db_badge)
        return None

    async def get_by_name(self, name: str) -> Optional[Badge]:
        db_badge = self.db.query(BadgeModel).filter(BadgeModel.name == name).first()
        if db_badge:
            return self._to_entity(db_badge)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Badge]:
        db_badges = self.db.query(BadgeModel).offset(skip).limit(limit).all()
        return [self._to_entity(badge) for badge in db_badges]

    async def update(self, badge_id: int, badge_data: dict) -> Optional[Badge]:
        db_badge = self.db.query(BadgeModel).filter(BadgeModel.id == badge_id).first()
        if not db_badge:
            return None
        for key, value in badge_data.items():
            if hasattr(db_badge, key):
                if key == "conditions" and value is not None:
                    value = [condition.model_dump() if hasattr(condition, "model_dump") else condition for condition in value]
                setattr(db_badge, key, value)
        db_badge.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_badge)
        return self._to_entity(db_badge)

    async def delete(self, badge_id: int) -> bool:
        db_badge = self.db.query(BadgeModel).filter(BadgeModel.id == badge_id).first()
        if not db_badge:
            return False
        self.db.delete(db_badge)
        self.db.commit()
        return True


class SQLAlchemyUserBadgeRepository(UserBadgeRepository):
    """SQLAlchemy implementation for user badge progress"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: UserBadgeModel) -> UserBadge:
        return UserBadge(
            id=model.id,
            user_id=model.user_id,
            badge_id=model.badge_id,
            current_progress=model.current_progress,
            is_completed=model.is_completed,
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, user_badge: UserBadge) -> UserBadge:
        db_user_badge = UserBadgeModel(
            user_id=user_badge.user_id,
            badge_id=user_badge.badge_id,
            current_progress=user_badge.current_progress,
            is_completed=user_badge.is_completed,
            completed_at=user_badge.completed_at
        )
        self.db.add(db_user_badge)
        self.db.commit()
        self.db.refresh(db_user_badge)
        return self._to_entity(db_user_badge)

    async def get_by_id(self, user_badge_id: int) -> Optional[UserBadge]:
        db_user_badge = self.db.query(UserBadgeModel).filter(UserBadgeModel.id == user_badge_id).first()
        if db_user_badge:
            return self._to_entity(db_user_badge)
        return None

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserBadge]:
        db_user_badges = (
            self.db.query(UserBadgeModel)
            .filter(UserBadgeModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(item) for item in db_user_badges]

    async def get_by_user_and_badge(self, user_id: int, badge_id: int) -> Optional[UserBadge]:
        db_user_badge = (
            self.db.query(UserBadgeModel)
            .filter(UserBadgeModel.user_id == user_id, UserBadgeModel.badge_id == badge_id)
            .first()
        )
        if db_user_badge:
            return self._to_entity(db_user_badge)
        return None

    async def update(self, user_badge_id: int, data: dict) -> Optional[UserBadge]:
        db_user_badge = self.db.query(UserBadgeModel).filter(UserBadgeModel.id == user_badge_id).first()
        if not db_user_badge:
            return None
        for key, value in data.items():
            if hasattr(db_user_badge, key):
                setattr(db_user_badge, key, value)
        db_user_badge.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user_badge)
        return self._to_entity(db_user_badge)

    async def delete(self, user_badge_id: int) -> bool:
        db_user_badge = self.db.query(UserBadgeModel).filter(UserBadgeModel.id == user_badge_id).first()
        if not db_user_badge:
            return False
        self.db.delete(db_user_badge)
        self.db.commit()
        return True
