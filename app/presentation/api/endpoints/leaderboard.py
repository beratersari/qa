from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.database.leaderboard_repository_impl import SQLAlchemyLeaderboardRepository
from app.application.services.leaderboard_service import LeaderboardService
from app.domain.entities.leaderboard import LeaderboardPeriod, LeaderboardDummyCreate, LeaderboardResponse, XpLeaderboardResponse
from app.domain.entities.user import User
from app.presentation.middleware.auth_middleware import get_current_user, get_current_admin

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


def get_leaderboard_service(db: Session = Depends(get_db)) -> LeaderboardService:
    repo = SQLAlchemyLeaderboardRepository(db)
    return LeaderboardService(repo)


@router.get("/xp", response_model=XpLeaderboardResponse)
async def get_xp_leaderboard(
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service),
    current_user: User = Depends(get_current_user)
):
    """Get XP leaderboard for public users"""
    return await leaderboard_service.get_xp_leaderboard(current_user.id)


@router.get("/{period}", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: LeaderboardPeriod,
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service),
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard for specified period with current user rank"""
    return await leaderboard_service.get_leaderboard(period, current_user.id)


@router.post("/dummy", status_code=status.HTTP_201_CREATED)
async def create_dummy_entry(
    dummy_data: LeaderboardDummyCreate,
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service),
    current_user: User = Depends(get_current_admin)
):
    """Create a dummy leaderboard entry (Admin only)"""
    return await leaderboard_service.add_dummy_entry(dummy_data)


@router.delete("/dummy/{dummy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dummy_entry(
    dummy_id: int,
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service),
    current_user: User = Depends(get_current_admin)
):
    """Delete a dummy leaderboard entry (Admin only)"""
    success = await leaderboard_service.delete_dummy_entry(dummy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dummy entry not found"
        )
    return None
