from fastapi import APIRouter, Depends, Cookie, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, result

from src.auth import security
from src.database import get_db
from src.auth.security import get_user_id_from_cookie
from src.models.teams import Team
from src.services import db_service
from src.schemas.teams_schema import TeamCreate



router = APIRouter(prefix='/teams', tags=["Teams"])


@router.post('/create')
async def create_team(
        team_data: TeamCreate,
        player_id = Depends(get_user_id_from_cookie),
        db: AsyncSession =  Depends(get_db),
):
    team = await db_service.create_new_team(db=db, team_data=team_data, player_id=player_id)
    return {'message': 'successful', 'team' : team}
@router.get('/my_team')
async def get_my_team(
        player_id: int = Depends(get_user_id_from_cookie),
        db: AsyncSession = Depends(get_db),
):
    team = await db_service.get_player_team(player_id, db)
    captain = await db_service.find_player_by_id(team.captain_id, db)
    return {
        "team_id": team.id,
        "team_name": team.name,
        "tag": team.tag,
        "captain": captain.username,
        "players": [
            {
                "player_id": player.id,
                "username": player.username,
                "game_role": player.game_role,
                "game_rank": player.game_rank
            } for player in team.players
        ]
    }

@router.post('/{team_id}/join')
async def join_team(team_id: int,
                    player_id: int = Depends(security.get_user_id_from_cookie),
                    db: AsyncSession = Depends(get_db)
                    ):
    team = await db_service.join_player_to_team(team_id, player_id, db)
    captain = await db_service.find_player_by_id(team.captain_id, db)
    return {
        "status": "success",
        "message": f"Вы успешно вступили в команду {team.name}",
        "team": {
            "id": team.id,
            "name": team.name,
            "tag": team.tag,
            "captain": captain.username
        }
    }

@router.post('/leave')
async def leave_team(
        player_id: int = Depends(get_user_id_from_cookie),
        db: AsyncSession = Depends(get_db)
):
    result = await db_service.leave_player_from_team(player_id, db)
    return result
@router.patch('/change_team_name/{new_name}')
async def change_team_name(
        new_name: str,
        player_id: int = Depends(get_user_id_from_cookie),
        db: AsyncSession = Depends(get_db)
):
    result = await db_service.change_team_name(player_id, new_name, db)
    return result
@router.post('/kick/{player_id_to_kick}')
async def kick_player(
        player_id_to_kick: int,
        player_id: int = Depends(get_user_id_from_cookie),
        db: AsyncSession = Depends(get_db),
):
    result = await db_service.kick_player(player_id_to_kick, player_id, db)
    return result