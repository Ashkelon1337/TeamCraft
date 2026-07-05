

from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import src.auth.security as security
from src.database import get_db
from src.models.players import GameRole
import src.services.db_service as db_service
from src.schemas.players_schema import PlayerResponse


router = APIRouter(prefix="/players", tags=["Players"])


@router.get('/profile', response_model=PlayerResponse)
async def get_profile(
        player_id: int = Depends(security.get_user_id_from_cookie),
        db: AsyncSession = Depends(get_db)

):
    player = await db_service.find_player_by_id(player_id, db)
    return player

@router.patch('/change_username')
async def change_username(
        new_username: str,
        player_id: int = Depends(security.get_user_id_from_cookie),
        db: AsyncSession = Depends(get_db)
):
    result = await db_service.change_username_player(player_id, new_username, db)
    return result

@router.patch('/change_gamerole/{new_gamerole}')
async def change_gamerole(
        new_gamerole: GameRole,
        player_id: int = Depends(security.get_user_id_from_cookie),
        db: AsyncSession = Depends(get_db)
):
    result = await db_service.change_gamerole(player_id, new_gamerole, db)
    return result