from typing import List, Optional
from app.domain.entities.badge import Badge, BadgeCreate, BadgeUpdate, UserBadge
from app.domain.repositories.badge_repository import BadgeRepository, UserBadgeRepository


class BadgeService:
    """Service for badge management"""

    def __init__(self, badge_repository: BadgeRepository, user_badge_repository: UserBadgeRepository):
        self.badge_repository = badge_repository
        self.user_badge_repository = user_badge_repository

    async def create_badge(self, badge_data: BadgeCreate) -> Badge:
        badge = Badge(
            name=badge_data.name,
            description=badge_data.description,
            icon_path=badge_data.icon_path,
            conditions=badge_data.conditions
        )
        return await self.badge_repository.create(badge)

    async def get_badge(self, badge_id: int) -> Optional[Badge]:
        return await self.badge_repository.get_by_id(badge_id)

    async def get_badge_by_name(self, name: str) -> Optional[Badge]:
        return await self.badge_repository.get_by_name(name)

    async def list_badges(self, skip: int = 0, limit: int = 100) -> List[Badge]:
        return await self.badge_repository.get_all(skip, limit)

    async def update_badge(self, badge_id: int, badge_data: BadgeUpdate) -> Optional[Badge]:
        update_dict = badge_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.badge_repository.get_by_id(badge_id)
        return await self.badge_repository.update(badge_id, update_dict)

    async def delete_badge(self, badge_id: int) -> bool:
        return await self.badge_repository.delete(badge_id)

    async def list_user_badges(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserBadge]:
        return await self.user_badge_repository.get_by_user(user_id, skip, limit)

    async def get_user_badge(self, user_badge_id: int) -> Optional[UserBadge]:
        return await self.user_badge_repository.get_by_id(user_badge_id)

    async def upsert_user_badge_progress(self, user_id: int, badge_id: int, current_progress: int, completed: bool) -> UserBadge:
        existing = await self.user_badge_repository.get_by_user_and_badge(user_id, badge_id)
        if existing:
            return await self.user_badge_repository.update(
                existing.id,
                {
                    "current_progress": current_progress,
                    "is_completed": completed,
                    "completed_at": existing.completed_at
                }
            )
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            current_progress=current_progress,
            is_completed=completed
        )
        return await self.user_badge_repository.create(user_badge)
