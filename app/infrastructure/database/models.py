from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, JSON, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.database.base import Base
from app.domain.entities.user import UserRole, SubscriptionType
from app.domain.entities.subscription import SubscriptionStatus, SubscriptionPlan
from app.domain.entities.question import QuestionSetType


# Association table for many-to-many relationship between Question and QuestionSet
question_set_association = Table(
    'question_set_questions',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('set_id', Integer, ForeignKey('question_sets.id'), primary_key=True)
)


class UserModel(Base):
    """SQLAlchemy model for User"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    subscription_type = Column(SQLEnum(SubscriptionType), default=SubscriptionType.FREE)
    total_xp = Column(Integer, default=0, nullable=False)
    challenge_streak = Column(Integer, default=0, nullable=False)  # Current daily challenge streak
    longest_challenge_streak = Column(Integer, default=0, nullable=False)  # Best streak ever
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationship
    subscription = relationship("SubscriptionModel", back_populates="user", uselist=False)
    flashcards = relationship("FlashCardModel", back_populates="creator")


class SubscriptionModel(Base):
    """SQLAlchemy model for Subscription"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    plan = Column(SQLEnum(SubscriptionPlan), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("UserModel", back_populates="subscription")


class FlashCardModel(Base):
    """SQLAlchemy model for FlashCard"""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    word_front = Column(String(200), nullable=False)
    word_back = Column(String(200), nullable=False)
    example_sentences = Column(JSON, default=list)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("UserModel", back_populates="flashcards")


class QuestionModel(Base):
    """SQLAlchemy model for Question"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String(500), nullable=False)
    choices = Column(JSON, default=list)
    answer_index = Column(Integer, nullable=False)
    difficulty_level = Column(Integer, default=1, nullable=False)  # 1-10 difficulty
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("UserModel")
    sets = relationship("QuestionSetModel", secondary=question_set_association, back_populates="questions")


class QuestionSetModel(Base):
    """SQLAlchemy model for QuestionSet"""
    __tablename__ = "question_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    set_type = Column(SQLEnum(QuestionSetType), default=QuestionSetType.NORMAL, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("UserModel")
    questions = relationship("QuestionModel", secondary=question_set_association, back_populates="sets")


class UserQuestionStatsModel(Base):
    """SQLAlchemy model for UserQuestionStats - tracks user performance on questions"""
    __tablename__ = "user_question_stats"
    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='uq_user_question'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    last_seen_at = Column(DateTime, nullable=True)
    last_result = Column(Boolean, nullable=True)
    next_review_at = Column(DateTime, nullable=True, index=True)
    streak = Column(Integer, default=0, nullable=False)  # Current streak of correct answers
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel")
    question = relationship("QuestionModel")


class LeaderboardDummyModel(Base):
    """SQLAlchemy model for dummy leaderboard entries"""
    __tablename__ = "leaderboard_dummies"
    
    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String(100), nullable=False)
    solved_count = Column(Integer, default=0, nullable=False)
    period = Column(String(20), nullable=False)  # last_7_days, last_30_days, all_time
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyChallengeModel(Base):
    """SQLAlchemy model for daily challenges"""
    __tablename__ = "daily_challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    challenge_date = Column(DateTime, nullable=False, unique=True, index=True)  # 00:00 UTC+3
    question_ids = Column(JSON, default=list)  # List of 5 question IDs
    created_at = Column(DateTime, default=datetime.utcnow)


class UserChallengeProgressModel(Base):
    """SQLAlchemy model for user challenge progress"""
    __tablename__ = "user_challenge_progress"
    __table_args__ = (
        UniqueConstraint('user_id', 'challenge_id', name='uq_user_challenge'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("daily_challenges.id"), nullable=False, index=True)
    completed_questions = Column(JSON, default=list)  # List of answered question IDs
    is_completed = Column(Boolean, default=False)
    xp_awarded = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel")
    challenge = relationship("DailyChallengeModel")
