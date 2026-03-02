from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database import engine, Base, SessionLocal
from app.presentation.api.v1.router import api_router
from app.infrastructure.security import hash_password
from app.infrastructure.database.models import UserModel, FlashCardModel, QuestionModel, QuestionSetModel
from app.domain.entities.user import UserRole, SubscriptionType
from app.domain.entities.question import QuestionSetType

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)

    # Seed dev admin user and mock data
    db = SessionLocal()
    try:
        existing_admin = db.query(UserModel).filter(UserModel.email == "admin@example.com").first()
        if not existing_admin:
            admin_user = UserModel(
                email="admin@example.com",
                username="admin",
                hashed_password=hash_password("admin123"),
                full_name="Development Admin",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                subscription_type=SubscriptionType.PREMIUM
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        else:
            admin_user = existing_admin

        # Seed mock questions if none exist
        if db.query(QuestionModel).count() == 0:
            mock_questions = [
                QuestionModel(
                    prompt="What is the capital of France?",
                    choices=["London", "Paris", "Berlin", "Madrid"],
                    answer_index=1,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="Which language is primarily spoken in Brazil?",
                    choices=["Spanish", "Portuguese", "French", "Italian"],
                    answer_index=1,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="What is the plural form of 'child'?",
                    choices=["childs", "children", "childes", "childrens"],
                    answer_index=1,
                    created_by=admin_user.id
                )
            ]
            db.add_all(mock_questions)
            db.commit()

        # Seed mock question sets if none exist
        if db.query(QuestionSetModel).count() == 0:
            normal_set = QuestionSetModel(
                name="General Knowledge",
                description="General questions for all users",
                set_type=QuestionSetType.NORMAL,
                created_by=admin_user.id
            )
            premium_set = QuestionSetModel(
                name="Advanced Language",
                description="Advanced language questions for premium users",
                set_type=QuestionSetType.PREMIUM,
                created_by=admin_user.id
            )
            db.add_all([normal_set, premium_set])
            db.commit()
            db.refresh(normal_set)
            db.refresh(premium_set)

            # Link questions to sets
            questions = db.query(QuestionModel).all()
            if questions:
                normal_set.questions.extend(questions[:2])
                premium_set.questions.extend(questions[2:])
                db.commit()

        # Seed mock flashcards if none exist
        if db.query(FlashCardModel).count() == 0:
            mock_flashcards = [
                FlashCardModel(
                    word_front="hello",
                    word_back="hola",
                    example_sentences=["Hello, how are you?", "Hello there!"],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="thank you",
                    word_back="gracias",
                    example_sentences=["Thank you for your help.", "Thank you so much!"],
                    created_by=admin_user.id
                )
            ]
            db.add_all(mock_flashcards)
            db.commit()
    finally:
        db.close()

    yield
    # Shutdown: Cleanup (if needed)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Language Learning App API
    
    ## Features
    
    * **Authentication**: JWT-based authentication with access and refresh tokens
    * **Users**: User management with role-based access control (User/Admin)
    * **Subscriptions**: Premium subscription management with monthly/yearly plans
    
    ## Authentication
    
    Most endpoints require authentication. Use the `/api/v1/auth/login` endpoint to obtain a JWT token,
    then include it in the Authorization header as `Bearer <token>`.
    
    ## User Roles
    
    * **User**: Regular users can manage their own profile and subscriptions
    * **Admin**: Administrators can manage all users and subscriptions
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Language Learning App API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
