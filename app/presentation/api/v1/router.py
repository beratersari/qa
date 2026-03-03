from fastapi import APIRouter
from app.presentation.api.endpoints import auth, users, subscriptions, flashcards, questions, question_sets, user_stats, leaderboard, challenge

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(subscriptions.router)
api_router.include_router(flashcards.router)
api_router.include_router(questions.router)
api_router.include_router(question_sets.router)
api_router.include_router(user_stats.router)
api_router.include_router(leaderboard.router)
api_router.include_router(challenge.router)
