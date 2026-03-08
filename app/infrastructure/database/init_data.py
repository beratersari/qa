"""Initialize mock data for the application"""
from sqlalchemy.orm import Session
from app.infrastructure.database.models import (
    QuestionModel, QuestionSetModel, question_set_association
)
from app.domain.entities.question import QuestionSetType


def init_mock_data(db: Session) -> None:
    """Initialize mock question sets and questions if none exist"""

    # Check if we already have question sets
    existing_sets = db.query(QuestionSetModel).first()
    if existing_sets:
        return  # Data already initialized

    # Create normal question set
    normal_set = QuestionSetModel(
        name="Basic English Grammar",
        description="Essential grammar questions for beginners",
        set_type=QuestionSetType.NORMAL
    )
    db.add(normal_set)
    db.flush()  # Get the ID

    # Create premium question set
    premium_set = QuestionSetModel(
        name="Advanced Vocabulary",
        description="Challenging vocabulary questions for advanced learners",
        set_type=QuestionSetType.PREMIUM
    )
    db.add(premium_set)
    db.flush()

    # Create questions for normal set
    normal_questions = [
        QuestionModel(
            prompt="Which is the correct form of the verb 'to be' for 'I'?",
            choices=["is", "am", "are", "be"],
            answer_index=1,
            difficulty_level=1
        ),
        QuestionModel(
            prompt="What is the plural of 'child'?",
            choices=["childs", "children", "childes", "child"],
            answer_index=1,
            difficulty_level=2
        ),
        QuestionModel(
            prompt="Which word is a preposition?",
            choices=["run", "quickly", "under", "happy"],
            answer_index=2,
            difficulty_level=2
        ),
        QuestionModel(
            prompt="Choose the correct past tense: 'Yesterday I _____ to the store.'",
            choices=["go", "gone", "went", "going"],
            answer_index=2,
            difficulty_level=3
        ),
    ]

    # Create questions for premium set
    premium_questions = [
        QuestionModel(
            prompt="What does 'ephemeral' mean?",
            choices=["Lasting forever", "Short-lived", "Extremely large", "Very expensive"],
            answer_index=1,
            difficulty_level=7
        ),
        QuestionModel(
            prompt="Which word is most similar in meaning to 'ubiquitous'?",
            choices=["Rare", "Omnipresent", "Expensive", "Complicated"],
            answer_index=1,
            difficulty_level=8
        ),
        QuestionModel(
            prompt="What is the meaning of 'pragmatic'?",
            choices=["Idealistic", "Practical", "Emotional", "Theoretical"],
            answer_index=1,
            difficulty_level=6
        ),
        QuestionModel(
            prompt="Choose the word that best completes: 'The professor's lecture was so _____ that half the class fell asleep.'",
            choices=["scintillating", "soporific", "stimulating", "provocative"],
            answer_index=1,
            difficulty_level=9
        ),
    ]

    # Add all questions
    for q in normal_questions:
        db.add(q)
        db.flush()
        # Associate with normal set
        db.execute(
            question_set_association.insert().values(
                question_id=q.id,
                set_id=normal_set.id
            )
        )

    for q in premium_questions:
        db.add(q)
        db.flush()
        # Associate with premium set
        db.execute(
            question_set_association.insert().values(
                question_id=q.id,
                set_id=premium_set.id
            )
        )

    db.commit()
    print("Mock data initialized successfully!")
