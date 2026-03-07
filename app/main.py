from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database import engine, Base, SessionLocal
from app.presentation.api.v1.router import api_router
from app.infrastructure.security import hash_password
from app.infrastructure.database.models import UserModel, FlashCardModel, QuestionModel, QuestionSetModel, UserQuestionStatsModel, LeaderboardDummyModel, DailyChallengeModel, UserChallengeProgressModel, FavoriteListModel, FavoriteQuestionModel, FavoriteFlashcardModel, BadgeModel, UserBadgeModel, SolvedQuestionModel
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
                longest_challenge_streak=1,
                profile_image_path="/static/images/default_avatar.png",
                bio="New user exploring the platform",
                contact_info="user10@example.com",
                profile_visibility="public"
            )
            db.add(fallback_user)
            db.commit()
            logger.info("Fallback user seeded", extra={"user_id": fallback_user.id})

        # Add profile data to existing users if they don't have it
        all_users = db.query(UserModel).all()
        for idx, user in enumerate(all_users):
            if user.bio is None:
                bios = [
                    "Learning enthusiast and quiz lover",
                    "Language learner aiming for fluency",
                    "Casual learner enjoying the journey",
                    "Dedicated student of knowledge",
                    "Trivia master in training",
                    "Words are my passion",
                    "Exploring new horizons daily",
                    "Knowledge seeker and achiever",
                    "Making learning fun every day",
                    "Always curious, always learning"
                ]
                profile_images = [
                    "/static/images/avatar1.png",
                    "/static/images/avatar2.png",
                    "/static/images/avatar3.png",
                    "/static/images/avatar4.png",
                    "/static/images/avatar5.png",
                    None,
                    "/static/images/avatar7.png",
                    "/static/images/avatar8.png",
                    None,
                    "/static/images/avatar10.png"
                ]
                visibilities = ["public", "private", "public", "private", "public", "private", "public", "private", "public", "private"]
                user.bio = bios[idx % len(bios)]
                user.profile_image_path = profile_images[idx % len(profile_images)]
                user.contact_info = f"Contact {user.username} at their profile"
                user.profile_visibility = visibilities[idx % len(visibilities)]
        db.commit()
        logger.info("User profiles enriched with mock data")

        # Create default favorite lists for users who don't have one
        all_users = db.query(UserModel).all()
        for user in all_users:
            existing_default = (
                db.query(FavoriteListModel)
                .filter(FavoriteListModel.user_id == user.id, FavoriteListModel.is_default == True)
                .first()
            )
            if not existing_default:
                default_list = FavoriteListModel(
                    name="Favorites",
                    description="My default favorites list",
                    user_id=user.id,
                    is_default=True,
                    privacy="private",
                    shared_with_usernames=[]
                )
                db.add(default_list)
        db.commit()
        logger.info("Default favorite lists ensured for all users")

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

        # Seed mock favorite lists and items if none exist
        if db.query(FavoriteListModel).count() > 0 and db.query(FavoriteQuestionModel).count() == 0 and db.query(FavoriteFlashcardModel).count() == 0:
            users = db.query(UserModel).all()
            questions = db.query(QuestionModel).all()
            flashcards = db.query(FlashCardModel).all()
            if users and questions and flashcards:
                # Create some public and shared lists
                public_list = FavoriteListModel(
                    name="Exam Essentials",
                    description="Key questions and flashcards for exam prep",
                    user_id=users[0].id,
                    is_default=False,
                    privacy="public",
                    shared_with_usernames=[]
                )
                shared_list = FavoriteListModel(
                    name="Shared Practice",
                    description="Shared practice set",
                    user_id=users[1].id,
                    is_default=False,
                    privacy="shared",
                    shared_with_usernames=[users[2].username, users[3].username]
                )
                db.add_all([public_list, shared_list])
                db.commit()
                db.refresh(public_list)
                db.refresh(shared_list)

                # Add questions to lists
                for question in questions[:3]:
                    db.add(FavoriteQuestionModel(favorite_list_id=public_list.id, question_id=question.id))
                for question in questions[3:6]:
                    db.add(FavoriteQuestionModel(favorite_list_id=shared_list.id, question_id=question.id))

                # Add flashcards to lists
                for flashcard in flashcards[:3]:
                    db.add(FavoriteFlashcardModel(favorite_list_id=public_list.id, flashcard_id=flashcard.id))
                for flashcard in flashcards[3:6]:
                    db.add(FavoriteFlashcardModel(favorite_list_id=shared_list.id, flashcard_id=flashcard.id))

                db.commit()
                logger.info("Mock favorite lists and items seeded")

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

        # Seed mock badges if none exist
        if db.query(BadgeModel).count() == 0:
            mock_badges = [
                BadgeModel(
                    name="Question Set Explorer",
                    description="Solve 10 question sets",
                    icon_path="/static/badges/question_sets_10.png",
                    conditions=[
                        {"progress_type": "question_sets_solved", "progress_target": 10}
                    ]
                ),
                BadgeModel(
                    name="Flashcard Sprinter",
                    description="Solve 100 flashcards",
                    icon_path="/static/badges/flashcards_100.png",
                    conditions=[
                        {"progress_type": "flashcards_solved", "progress_target": 100}
                    ]
                ),
                BadgeModel(
                    name="Question Master",
                    description="Solve 250 questions",
                    icon_path="/static/badges/questions_250.png",
                    conditions=[
                        {"progress_type": "questions_solved", "progress_target": 250}
                    ]
                ),
                BadgeModel(
                    name="Well-Rounded Learner",
                    description="Solve 3 question sets and 50 flashcards",
                    icon_path="/static/badges/well_rounded.png",
                    conditions=[
                        {"progress_type": "question_sets_solved", "progress_target": 3},
                        {"progress_type": "flashcards_solved", "progress_target": 50}
                    ]
                )
            ]
            db.add_all(mock_badges)
            db.commit()
            logger.info("Mock badges seeded", extra={"count": len(mock_badges)})

        # Seed mock user badge progress if none exist
        if db.query(UserBadgeModel).count() == 0:
            users = db.query(UserModel).all()
            badges = db.query(BadgeModel).all()
            if users and badges:
                progress_samples = [3, 25, 80, 120, 200]
                for index, user in enumerate(users[:5]):
                    for badge in badges:
                        current_progress = progress_samples[index % len(progress_samples)]
                        target = max(condition.get("progress_target", 0) for condition in badge.conditions) if badge.conditions else 0
                        is_completed = current_progress >= target
                        completed_at = datetime.utcnow() if is_completed else None
                        db.add(
                            UserBadgeModel(
                                user_id=user.id,
                                badge_id=badge.id,
                                current_progress=current_progress,
                                is_completed=is_completed,
                                completed_at=completed_at
                            )
                        )
                db.commit()
                logger.info("Mock user badge progress seeded")

        # Seed mock user question stats if none exist
        if db.query(UserQuestionStatsModel).count() == 0:
            questions = db.query(QuestionModel).all()
            users = db.query(UserModel).all()
            if questions and users:
                now = datetime.utcnow()
                mock_stats = []
                solved_entries = []
                # Create stats for multiple users with varied data
                for user in users[:5]:
                    for index, question in enumerate(questions[:10]):
                        # Vary the data based on user and question
                        total_attempts = 3 + (index % 5) + (user.id % 3)
                        correct_attempts = max(1, total_attempts - (index % 4))
                        day_offset = (index + user.id) % 30
                        solved_at = now - timedelta(days=day_offset)
                        mock_stats.append(
                            UserQuestionStatsModel(
                                user_id=user.id,
                                question_id=question.id,
                                total_attempts=total_attempts,
                                correct_attempts=correct_attempts,
                                last_seen_at=solved_at,
                                last_result=index % 3 == 0,
                                next_review_at=now + timedelta(days=1 + index),
                                streak=index % 5
                            )
                        )
                        # Seed solved questions for each correct attempt
                        for _ in range(correct_attempts):
                            solved_entries.append(
                                SolvedQuestionModel(
                                    user_id=user.id,
                                    question_id=question.id,
                                    solved_at=solved_at
                                )
                            )
                db.add_all(mock_stats)
                db.add_all(solved_entries)
                db.commit()
                logger.info("Mock user question stats seeded", extra={"count": len(mock_stats)})
                logger.info("Mock solved questions seeded", extra={"count": len(solved_entries)})

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
    allow_origins=settings.CORS_ORIGINS,
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
