from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database import engine, Base, SessionLocal
from app.presentation.api.v1.router import api_router
from app.infrastructure.security import hash_password
from app.infrastructure.database.models import UserModel, FlashCardModel, QuestionModel, QuestionSetModel, UserQuestionStatsModel, LeaderboardDummyModel, DailyChallengeModel, UserChallengeProgressModel
from app.domain.entities.user import UserRole, SubscriptionType
from app.domain.entities.question import QuestionSetType
from app.infrastructure.logging import setup_logging, get_logger
from app.presentation.middleware import RequestLoggingMiddleware

settings = get_settings()

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    console_output=settings.LOG_CONSOLE,
    json_format=settings.LOG_JSON_FILE
)

# Get logger for this module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Application starting up")
    
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

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
            logger.info("Admin user created", extra={"user_id": admin_user.id})
        else:
            admin_user = existing_admin
            logger.debug("Admin user already exists")

        # Seed mock users if none exist
        if db.query(UserModel).count() < 10:
            mock_users = [
                UserModel(
                    email="user1@example.com",
                    username="user1",
                    hashed_password=hash_password("password123"),
                    full_name="Alex Johnson",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                    subscription_type=SubscriptionType.FREE,
                    total_xp=120,
                    challenge_streak=2,
                    longest_challenge_streak=5
                ),
                UserModel(
                    email="user2@example.com",
                    username="user2",
                    hashed_password=hash_password("password123"),
                    full_name="Jamie Lee",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=False,
                    subscription_type=SubscriptionType.FREE,
                    total_xp=220,
                    challenge_streak=3,
                    longest_challenge_streak=4
                ),
                UserModel(
                    email="user3@example.com",
                    username="user3",
                    hashed_password=hash_password("password123"),
                    full_name="Morgan Smith",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                    subscription_type=SubscriptionType.PREMIUM,
                    total_xp=410,
                    challenge_streak=1,
                    longest_challenge_streak=3
                ),
                UserModel(
                    email="user4@example.com",
                    username="user4",
                    hashed_password=hash_password("password123"),
                    full_name="Taylor Brown",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                    subscription_type=SubscriptionType.PREMIUM,
                    total_xp=90,
                    challenge_streak=0,
                    longest_challenge_streak=2
                ),
                UserModel(
                    email="user5@example.com",
                    username="user5",
                    hashed_password=hash_password("password123"),
                    full_name="Jordan Davis",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=False,
                    subscription_type=SubscriptionType.FREE,
                    total_xp=60,
                    challenge_streak=0,
                    longest_challenge_streak=1
                ),
                UserModel(
                    email="user6@example.com",
                    username="user6",
                    hashed_password=hash_password("password123"),
                    full_name="Casey Miller",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                    subscription_type=SubscriptionType.PREMIUM,
                    total_xp=300,
                    challenge_streak=4,
                    longest_challenge_streak=6
                ),
                UserModel(
                    email="user7@example.com",
                    username="user7",
                    hashed_password=hash_password("password123"),
                    full_name="Riley Wilson",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                    subscription_type=SubscriptionType.FREE,
                    total_xp=150,
                    challenge_streak=1,
                    longest_challenge_streak=3
                ),
                UserModel(
                    email="user8@example.com",
                    username="user8",
                    hashed_password=hash_password("password123"),
                    full_name="Avery Martinez",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                    subscription_type=SubscriptionType.FREE,
                    total_xp=80,
                    challenge_streak=2,
                    longest_challenge_streak=2
                ),
                UserModel(
                    email="user9@example.com",
                    username="user9",
                    hashed_password=hash_password("password123"),
                    full_name="Parker Lewis",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                    subscription_type=SubscriptionType.PREMIUM,
                    total_xp=500,
                    challenge_streak=5,
                    longest_challenge_streak=7
                )
            ]
            db.add_all(mock_users)
            db.commit()
            logger.info("Mock users seeded", extra={"count": len(mock_users)})

        users = db.query(UserModel).all()
        if len(users) < 10:
            fallback_user = UserModel(
                email="user10@example.com",
                username="user10",
                hashed_password=hash_password("password123"),
                full_name="Quinn Adams",
                role=UserRole.USER,
                is_active=True,
                is_verified=True,
                subscription_type=SubscriptionType.FREE,
                total_xp=110,
                challenge_streak=0,
                longest_challenge_streak=1
            )
            db.add(fallback_user)
            db.commit()
            logger.info("Fallback user seeded", extra={"user_id": fallback_user.id})

        # Seed mock questions if none exist
        if db.query(QuestionModel).count() == 0:
            mock_questions = [
                QuestionModel(
                    prompt="What is the capital of France?",
                    choices=["London", "Paris", "Berlin", "Madrid"],
                    answer_index=1,
                    difficulty_level=2,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="Which language is primarily spoken in Brazil?",
                    choices=["Spanish", "Portuguese", "French", "Italian"],
                    answer_index=1,
                    difficulty_level=3,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="What is the plural form of 'child'?",
                    choices=["childs", "children", "childes", "childrens"],
                    answer_index=1,
                    difficulty_level=1,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="Which planet is known as the Red Planet?",
                    choices=["Venus", "Mars", "Jupiter", "Saturn"],
                    answer_index=1,
                    difficulty_level=2,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="What is the largest ocean on Earth?",
                    choices=["Atlantic", "Indian", "Pacific", "Arctic"],
                    answer_index=2,
                    difficulty_level=3,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="Which element has the chemical symbol O?",
                    choices=["Gold", "Oxygen", "Osmium", "Silver"],
                    answer_index=1,
                    difficulty_level=1,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="Who wrote 'Romeo and Juliet'?",
                    choices=["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                    answer_index=1,
                    difficulty_level=4,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="Which country hosted the 2016 Summer Olympics?",
                    choices=["China", "Brazil", "UK", "Russia"],
                    answer_index=1,
                    difficulty_level=4,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="What is the square root of 64?",
                    choices=["6", "7", "8", "9"],
                    answer_index=2,
                    difficulty_level=2,
                    created_by=admin_user.id
                ),
                QuestionModel(
                    prompt="Which language has the most native speakers?",
                    choices=["English", "Spanish", "Mandarin", "Hindi"],
                    answer_index=2,
                    difficulty_level=5,
                    created_by=admin_user.id
                )
            ]
            db.add_all(mock_questions)
            db.commit()
            logger.info("Mock questions seeded", extra={"count": len(mock_questions)})

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
            review_set = QuestionSetModel(
                name="Daily Review",
                description="Questions for daily review practice",
                set_type=QuestionSetType.NORMAL,
                created_by=admin_user.id
            )
            db.add_all([normal_set, premium_set, review_set])
            db.commit()
            db.refresh(normal_set)
            db.refresh(premium_set)
            db.refresh(review_set)
            logger.info(
                "Question sets created",
                extra={"sets": ["General Knowledge", "Advanced Language", "Daily Review"]}
            )

            # Link questions to sets
            questions = db.query(QuestionModel).all()
            if questions:
                normal_set.questions.extend(questions[:4])
                premium_set.questions.extend(questions[4:8])
                review_set.questions.extend(questions[8:])
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
                ),
                FlashCardModel(
                    word_front="good morning",
                    word_back="buenos días",
                    example_sentences=["Good morning, everyone!", "Good morning, sir."],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="please",
                    word_back="por favor",
                    example_sentences=["Please close the door.", "Please wait a moment."],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="excuse me",
                    word_back="perdón",
                    example_sentences=["Excuse me, can you help?", "Excuse me for the interruption."],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="sorry",
                    word_back="lo siento",
                    example_sentences=["Sorry for the delay.", "I'm sorry about that."],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="how much",
                    word_back="cuánto",
                    example_sentences=["How much does it cost?", "How much time is left?"],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="where is",
                    word_back="dónde está",
                    example_sentences=["Where is the station?", "Where is my book?"],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="see you",
                    word_back="nos vemos",
                    example_sentences=["See you tomorrow.", "See you later!"],
                    created_by=admin_user.id
                ),
                FlashCardModel(
                    word_front="welcome",
                    word_back="bienvenido",
                    example_sentences=["Welcome to the team.", "Welcome home!"],
                    created_by=admin_user.id
                )
            ]
            db.add_all(mock_flashcards)
            db.commit()
            logger.info("Mock flashcards seeded", extra={"count": len(mock_flashcards)})

        # Seed mock leaderboard dummy entries if none exist
        if db.query(LeaderboardDummyModel).count() == 0:
            mock_dummies = [
                LeaderboardDummyModel(display_name="Ava", solved_count=24, period="last_7_days"),
                LeaderboardDummyModel(display_name="Liam", solved_count=20, period="last_7_days"),
                LeaderboardDummyModel(display_name="Noah", solved_count=18, period="last_7_days"),
                LeaderboardDummyModel(display_name="Emma", solved_count=30, period="last_30_days"),
                LeaderboardDummyModel(display_name="Olivia", solved_count=28, period="last_30_days"),
                LeaderboardDummyModel(display_name="Sophia", solved_count=25, period="last_30_days"),
                LeaderboardDummyModel(display_name="Mason", solved_count=40, period="all_time"),
                LeaderboardDummyModel(display_name="Isabella", solved_count=35, period="all_time"),
                LeaderboardDummyModel(display_name="Lucas", solved_count=33, period="all_time"),
                LeaderboardDummyModel(display_name="Mia", solved_count=31, period="all_time")
            ]
            db.add_all(mock_dummies)
            db.commit()
            logger.info("Mock leaderboard dummies seeded", extra={"count": len(mock_dummies)})

        # Seed mock user question stats if none exist
        if db.query(UserQuestionStatsModel).count() == 0:
            questions = db.query(QuestionModel).all()
            if questions:
                now = datetime.utcnow()
                mock_stats = []
                for index, question in enumerate(questions[:10]):
                    mock_stats.append(
                        UserQuestionStatsModel(
                            user_id=admin_user.id,
                            question_id=question.id,
                            total_attempts=3 + index,
                            correct_attempts=2 + (index % 2),
                            last_seen_at=now - timedelta(days=index),
                            last_result=index % 2 == 0,
                            next_review_at=now + timedelta(days=1 + index),
                            streak=index % 5
                        )
                    )
                db.add_all(mock_stats)
                db.commit()
                logger.info("Mock user question stats seeded", extra={"count": len(mock_stats)})

        # Seed mock daily challenges if none exist
        if db.query(DailyChallengeModel).count() == 0:
            questions = db.query(QuestionModel).all()
            if len(questions) >= 5:
                now = datetime.utcnow()
                mock_challenges = []
                for day_offset in range(10):
                    challenge_date = (now - timedelta(days=day_offset)).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    start = (day_offset * 5) % len(questions)
                    question_ids = [q.id for q in questions[start:start + 5]]
                    if len(question_ids) < 5:
                        question_ids = [q.id for q in questions[:5]]
                    mock_challenges.append(
                        DailyChallengeModel(
                            challenge_date=challenge_date,
                            question_ids=question_ids
                        )
                    )
                db.add_all(mock_challenges)
                db.commit()
                logger.info("Mock daily challenges seeded", extra={"count": len(mock_challenges)})

        # Seed mock challenge progress if none exist
        if db.query(UserChallengeProgressModel).count() == 0:
            challenges = db.query(DailyChallengeModel).limit(10).all()
            if challenges:
                now = datetime.utcnow()
                mock_progress = []
                for idx, challenge in enumerate(challenges):
                    completed_questions = challenge.question_ids[:3]
                    is_completed = idx % 2 == 0
                    if is_completed:
                        completed_questions = challenge.question_ids
                    mock_progress.append(
                        UserChallengeProgressModel(
                            user_id=admin_user.id,
                            challenge_id=challenge.id,
                            completed_questions=completed_questions,
                            is_completed=is_completed,
                            xp_awarded=is_completed,
                            completed_at=now - timedelta(days=idx) if is_completed else None
                        )
                    )
                db.add_all(mock_progress)
                db.commit()
                logger.info("Mock challenge progress seeded", extra={"count": len(mock_progress)})
    except Exception as e:
        logger.error("Error during startup", exc_info=True)
        raise
    finally:
        db.close()

    logger.info("Application startup complete")
    yield
    # Shutdown: Cleanup (if needed)
    logger.info("Application shutting down")


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

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

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
