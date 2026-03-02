from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.application.services import AuthService
from app.domain.entities.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = SQLAlchemyUserRepository(db)
    return AuthService(user_repo)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    user, error = await auth_service.register_user(user_data)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return user


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
