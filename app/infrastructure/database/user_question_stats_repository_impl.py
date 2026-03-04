from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.domain.entities.user_question_stats import UserQuestionStats
from app.domain.repositories.user_question_stats_repository import UserQuestionStatsRepository
from app.infrastructure.database.models import UserQuestionStatsModel, QuestionModel, SolvedQuestionModel
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemyUserQuestionStatsRepository(UserQuestionStatsRepository):
    """SQLAlchemy implementation of UserQuestionStatsRepository"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: UserQuestionStatsModel) -> UserQuestionStats:
        return UserQuestionStats(
            id=model.id,
            user_id=model.user_id,
            question_id=model.question_id,
            total_attempts=model.total_attempts,
            correct_attempts=model.correct_attempts,
            last_seen_at=model.last_seen_at,
            last_result=model.last_result,
            next_review_at=model.next_review_at,
            streak=model.streak,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, stats: UserQuestionStats) -> UserQuestionStats:
        db_stats = UserQuestionStatsModel(
            user_id=stats.user_id,
            question_id=stats.question_id,
            total_attempts=stats.total_attempts,
            correct_attempts=stats.correct_attempts,
            last_seen_at=stats.last_seen_at,
            last_result=stats.last_result,
            next_review_at=stats.next_review_at,
            streak=stats.streak
        )
        self.db.add(db_stats)
        self.db.commit()
        self.db.refresh(db_stats)
        
        logger.debug(
            f"Created user question stats",
            extra={"user_id": stats.user_id, "question_id": stats.question_id}
        )
        
        return self._to_entity(db_stats)

    async def get_by_id(self, stats_id: int) -> Optional[UserQuestionStats]:
        db_stats = self.db.query(UserQuestionStatsModel).filter(
            UserQuestionStatsModel.id == stats_id
        ).first()
        if db_stats:
            return self._to_entity(db_stats)
        return None

    async def get_by_user_and_question(self, user_id: int, question_id: int) -> Optional[UserQuestionStats]:
        db_stats = self.db.query(UserQuestionStatsModel).filter(
            and_(
                UserQuestionStatsModel.user_id == user_id,
                UserQuestionStatsModel.question_id == question_id
            )
        ).first()
        if db_stats:
            return self._to_entity(db_stats)
        return None

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserQuestionStats]:
        db_stats = self.db.query(UserQuestionStatsModel).filter(
            UserQuestionStatsModel.user_id == user_id
        ).order_by(UserQuestionStatsModel.updated_at.desc()).offset(skip).limit(limit).all()
        return [self._to_entity(s) for s in db_stats]

    async def update(self, stats_id: int, stats_data: dict) -> Optional[UserQuestionStats]:
        db_stats = self.db.query(UserQuestionStatsModel).filter(
            UserQuestionStatsModel.id == stats_id
        ).first()
        if not db_stats:
            return None

        for key, value in stats_data.items():
            if hasattr(db_stats, key):
                setattr(db_stats, key, value)

        db_stats.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_stats)
        return self._to_entity(db_stats)

    async def upsert(self, stats: UserQuestionStats) -> UserQuestionStats:
        """Create or update stats for user and question"""
        existing = await self.get_by_user_and_question(stats.user_id, stats.question_id)
        
        if existing:
            update_data = {
                "total_attempts": stats.total_attempts,
                "correct_attempts": stats.correct_attempts,
                "last_seen_at": stats.last_seen_at,
                "last_result": stats.last_result,
                "next_review_at": stats.next_review_at,
                "streak": stats.streak,
            }
            return await self.update(existing.id, update_data)
        else:
            return await self.create(stats)

    async def get_questions_for_review(self, user_id: int, limit: int = 10) -> List[int]:
        """Get question IDs due for review or answered incorrectly"""
        now = datetime.utcnow()
        
        # Get questions where next_review_at is due, never seen, or last answer incorrect
        db_stats = self.db.query(UserQuestionStatsModel.question_id).filter(
            and_(
                UserQuestionStatsModel.user_id == user_id,
                or_(
                    UserQuestionStatsModel.next_review_at <= now,
                    UserQuestionStatsModel.next_review_at.is_(None),
                    UserQuestionStatsModel.last_result.is_(False)
                )
            )
        ).order_by(
            UserQuestionStatsModel.last_result.asc().nulls_first(),
            UserQuestionStatsModel.next_review_at.asc().nulls_first()
        ).limit(limit).all()
        
        return [s[0] for s in db_stats]

    async def get_user_stats_summary(self, user_id: int) -> dict:
        """Get summary statistics for a user"""
        # Get all stats for the user
        stats = self.db.query(UserQuestionStatsModel).filter(
            UserQuestionStatsModel.user_id == user_id
        ).all()
        
        total_questions = len(stats)
        total_attempts = sum(s.total_attempts for s in stats)
        total_correct = sum(s.correct_attempts for s in stats)
        
        # Count by mastery level
        mastered = 0
        proficient = 0
        learning = 0
        new = 0
        
        for s in stats:
            accuracy = (s.correct_attempts / s.total_attempts * 100) if s.total_attempts > 0 else 0
            
            if s.streak >= 5 and accuracy >= 80:
                mastered += 1
            elif s.streak >= 3 and accuracy >= 60:
                proficient += 1
            elif s.total_attempts >= 3 and accuracy >= 40:
                learning += 1
            else:
                new += 1
        
        # Get longest streak
        longest_streak = max((s.streak for s in stats), default=0)
        
        return {
            "total_questions_attempted": total_questions,
            "total_correct": total_correct,
            "overall_accuracy": (total_correct / total_attempts * 100) if total_attempts > 0 else 0,
            "mastered_count": mastered,
            "proficient_count": proficient,
            "learning_count": learning,
            "new_count": new,
            "current_streak": 0,  # Would need session tracking
            "longest_streak": longest_streak
        }

    async def get_by_user_and_questions(self, user_id: int, question_ids: List[int]) -> List[UserQuestionStats]:
        """Get stats for multiple questions for a user"""
        db_stats = self.db.query(UserQuestionStatsModel).filter(
            and_(
                UserQuestionStatsModel.user_id == user_id,
                UserQuestionStatsModel.question_id.in_(question_ids)
            )
        ).all()
        return [self._to_entity(s) for s in db_stats]

    async def get_daily_solved_counts(self, user_id: int, start_date: date, end_date: date) -> List[dict]:
        """Get daily solved counts for a user within a date range"""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Query to get count of all correct submissions per day from SolvedQuestionModel
        results = (
            self.db.query(
                func.date(SolvedQuestionModel.solved_at).label('day'),
                func.count(SolvedQuestionModel.id).label('solved_count')
            )
            .filter(
                and_(
                    SolvedQuestionModel.user_id == user_id,
                    SolvedQuestionModel.solved_at >= start_datetime,
                    SolvedQuestionModel.solved_at <= end_datetime
                )
            )
            .group_by(func.date(SolvedQuestionModel.solved_at))
            .all()
        )

        # Create a dict of existing counts
        counts_dict = {}
        for r in results:
            if r.day is None:
                continue
            if isinstance(r.day, date):
                day_key = r.day
            elif isinstance(r.day, str):
                day_key = datetime.fromisoformat(r.day).date()
            else:
                day_key = r.day.date()
            counts_dict[day_key] = r.solved_count

        # Fill in all dates in the range with 0 if no data
        daily_stats = []
        current_date = start_date
        while current_date <= end_date:
            daily_stats.append({
                'date': current_date,
                'solved_count': counts_dict.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        return daily_stats

    async def get_lowest_accuracy_questions(self, user_id: int, limit: int = 10) -> List[dict]:
        """Get questions with lowest accuracy for a user"""
        # Join with questions table to get prompt
        results = (
            self.db.query(
                UserQuestionStatsModel.question_id,
                QuestionModel.prompt,
                UserQuestionStatsModel.total_attempts,
                UserQuestionStatsModel.correct_attempts
            )
            .join(QuestionModel, UserQuestionStatsModel.question_id == QuestionModel.id)
            .filter(
                and_(
                    UserQuestionStatsModel.user_id == user_id,
                    UserQuestionStatsModel.total_attempts > 0
                )
            )
            .all()
        )

        # Calculate accuracy and sort
        questions_with_accuracy = []
        for r in results:
            accuracy = (r.correct_attempts / r.total_attempts * 100) if r.total_attempts > 0 else 0.0
            questions_with_accuracy.append({
                'question_id': r.question_id,
                'prompt': r.prompt,
                'total_attempts': r.total_attempts,
                'correct_attempts': r.correct_attempts,
                'accuracy': round(accuracy, 2)
            })

        # Sort by accuracy ascending and return top n
        questions_with_accuracy.sort(key=lambda x: x['accuracy'])
        return questions_with_accuracy[:limit]

    async def record_solved_question(self, user_id: int, question_id: int) -> None:
        """Record a correct question submission"""
        db_solved = SolvedQuestionModel(
            user_id=user_id,
            question_id=question_id,
            solved_at=datetime.utcnow()
        )
        self.db.add(db_solved)
        self.db.commit()
