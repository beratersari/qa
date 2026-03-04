from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.infrastructure.database.favorite_repository_impl import SQLAlchemyFavoriteListRepository, SQLAlchemyFavoriteItemRepository
from app.application.services import AuthService, FavoriteService
from app.domain.entities.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = SQLAlchemyUserRepository(db)
    return AuthService(user_repo)


def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    favorite_list_repo = SQLAlchemyFavoriteListRepository(db)
    favorite_item_repo = SQLAlchemyFavoriteItemRepository(db)
    return FavoriteService(favorite_list_repo, favorite_item_repo)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    """Register a new user"""
    user, error = await auth_service.register_user(user_data)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Create default favorite list for the new user
    await favorite_service.create_default_favorite_list(user.id)

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        subscription_type=user.subscription_type,
        total_xp=user.total_xp,
        level=user.level,
        challenge_streak=user.challenge_streak,
        longest_challenge_streak=user.longest_challenge_streak,
        profile_image_path=user.profile_image_path,
        bio=user.bio,
        contact_info=user.contact_info,
        profile_visibility=user.profile_visibility,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with email and password"""
    user, error = await auth_service.authenticate_user(form_data.username, form_data.password)
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = auth_service.create_tokens(user.id, user.email, user.role.value)
    return {
        **tokens,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value
        }
    }
