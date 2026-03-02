from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, JSON, Table
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
