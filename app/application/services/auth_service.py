from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.domain.entities.user import User, UserCreate, UserRole, SubscriptionType
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.security import hash_password, verify_password, create_access_token, create_refresh_token


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register_user(self, user_data: UserCreate) -> Tuple[Optional[User], Optional[str]]:
        """Register a new user"""
        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            return None, "Email already registered"
        
        # Check if username already exists
        existing_username = await self.user_repository.get_by_username(user_data.username)
        if existing_username:
            return None, "Username already taken"
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user entity
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=UserRole.USER,
            subscription_type=SubscriptionType.FREE
        )
        
        # Save to database
        created_user = await self.user_repository.create(user)
        return created_user, None
    
    async def authenticate_user(self, username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """Authenticate a user with email or username and password"""
        # Try to find user by email first, then by username
        user = await self.user_repository.get_by_email(username)
        if not user:
            user = await self.user_repository.get_by_username(username)
        
        if not user:
            return None, "Invalid credentials"
        
        if not user.is_active:
            return None, "User account is deactivated"
        
        if not verify_password(password, user.hashed_password):
            return None, "Invalid credentials"
        
        # Update last login
        await self.user_repository.update_last_login(user.id)
        
        return user, None
    
    def create_tokens(self, user_id: int, email: str, role: str) -> dict:
        """Create access and refresh tokens"""
        token_data = {
            "sub": str(user_id),
            "email": email,
            "role": role
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
