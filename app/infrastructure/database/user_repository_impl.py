from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity"""
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=model.role,
            is_active=model.is_active,
            is_verified=model.is_verified,
            subscription_type=model.subscription_type,
            total_xp=model.total_xp,
            challenge_streak=model.challenge_streak,
            longest_challenge_streak=model.longest_challenge_streak,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        db_user = UserModel(
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            subscription_type=user.subscription_type,
            total_xp=user.total_xp
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return self._to_entity(db_user)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return self._to_entity(db_user)
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if db_user:
            return self._to_entity(db_user)
        return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        db_users = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_entity(user) for user in db_users]
    
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user by ID"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None
        
        for key, value in user_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    async def delete(self, user_id: int) -> bool:
        """Delete user by ID"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        
        db_user.last_login = datetime.utcnow()
        self.db.commit()
        return True
