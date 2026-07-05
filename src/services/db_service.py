from sqlalchemy import select, or_, delete
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.teams_schema import TeamCreate
from src.schemas.auth_schema import UserRegister
from sqlalchemy.orm import selectinload, defer
import src.auth.security as security
from src.models.teams import Team
from src.models.players import Player, GameRole

async def is_exists_player_name(username: str, db: AsyncSession) -> None:
    player = await db.scalar(select(Player).where(Player.username == username))
    if player:
        raise HTTPException(status_code=409, detail=f'Игрок "{player.username}" уже существует')

async def is_player_captain(player_id: int, db: AsyncSession):
    player = await find_player_by_id(player_id, db)
    if not await is_player_in_team(player): raise HTTPException(status_code=409, detail='Вы не состоите в команде')
    return True if player.team.captain_id == player.id else False

async def register_player_in_db(player_data: UserRegister, db: AsyncSession) -> Player:
    is_existing_player = await db.scalar(select(Player).where(Player.username == player_data.username))
    if is_existing_player:
        raise HTTPException(status_code=409)
    hashed_password = security.hash_password(player_data.password)
    new_player = Player(username=player_data.username, email=player_data.email, hashed_password=hashed_password)
    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)
    return new_player

async def find_user_by_username(username: str, db: AsyncSession) -> Player:
    user = await db.scalar(select(Player).where(Player.username == username))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

async def find_player_by_id(player_id: int, db: AsyncSession) -> Player:
    player = await db.scalar(
        select(Player)
        .where(Player.id == player_id)
        .options(selectinload(Player.team).selectinload(Team.players))
    )

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Player not found'
        )
    return player

async def is_player_in_team(player: Player) -> bool:
    return True if player.team_id else False

async def create_new_team(team_data: TeamCreate, db: AsyncSession, player_id: int) -> Team:
    player = await find_player_by_id(player_id, db)
    possible_team = (
        (await db.scalars(select(Team)
        .where(or_(Team.name == team_data.name, Team.tag == team_data.tag)))).
        first()
    )
    if possible_team:
        raise HTTPException(
            status_code=400,
            detail="Команда с таким названием или тегом уже существует"
        )
    if await is_player_in_team(player):
        raise HTTPException(status_code=409, detail='сначала покиньте свою команду')
    new_team = Team(
        **team_data.model_dump(), captain_id=player_id
    )
    new_team.players.append(player)
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    return new_team

async def get_player_team(player_id: int, db: AsyncSession) -> Team:
    player = await db.scalar(
        select(Player)
        .where(Player.id == player_id)
        .options(selectinload(Player.team).selectinload(Team.players))
    )
    if not player:
        raise HTTPException(status_code=404, detail="Игрок не найден")

    if not await is_player_in_team(player):
        raise HTTPException(status_code=409, detail='Вы не состоите в команде')

    return player.team

async def get_team_by_id(team_id: int, db: AsyncSession) -> Team:
    team = await db.scalar(select(Team).where(Team.id == team_id).options(selectinload(Team.players)))
    if not team:
        raise HTTPException(status_code=404, detail="Такой команды не сущетсвует")
    return team

async def join_player_to_team(team_id: int, player_id: int, db: AsyncSession) -> Team:
    player = await find_player_by_id(player_id, db)
    if await is_player_in_team(player):
        raise HTTPException(status_code=409, detail='Сначала покиньте свою команду')
    team = await get_team_by_id(team_id, db)
    team.players.append(player)
    await db.commit()
    await db.refresh(team)
    return team

async def leave_player_from_team(player_id: int, db: AsyncSession) -> dict:
    player = await find_player_by_id(player_id, db)
    if not player.team_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в команде")
    team_name = player.team.name
    if player.team.captain_id == player_id:
        raise HTTPException(
            status_code=400,
            detail="Капитан не может просто так покинуть команду. Передайте права или удалите её."
        )
    player.team_id = None
    player.team = None
    await db.commit()
    return {'detail': f'Вы успешно вышли из {team_name}'}
async def change_username_player(player_id: int, new_username: str, db: AsyncSession) -> dict:
    await is_exists_player_name(new_username, db)
    player = await find_player_by_id(player_id, db)
    player.username = new_username
    await db.commit()
    await db.refresh(player)
    return {'message': 'successful', 'new_name': player.username}
async def change_team_name(player_id: int, new_name: str, db: AsyncSession) -> dict:
    if not await is_player_captain(player_id, db): raise HTTPException(status_code=403, detail='Вы не являетесь капитаном команды')
    if await db.scalar(select(Team).where(Team.name == new_name)):
        raise HTTPException(status_code=400, detail='Команда с таким названием уже существует')
    team = await get_player_team(player_id, db)
    team.name = new_name
    await db.commit()
    await db.refresh(team)
    return {'message': 'successful', 'new_name': team.name}

async def change_gamerole(player_id: int, new_gamerole: GameRole, db: AsyncSession) -> dict:
    player = await find_player_by_id(player_id, db)
    if player.game_role == new_gamerole:
        raise HTTPException(status_code=400, detail='Вы уже имеете эту роль')
    if player.team_id:
        team_players = player.team.players
        for p in team_players:
            if p.game_role == new_gamerole:
                raise HTTPException(status_code=400, detail='В вашей команде уже есть игрок с этой ролью')
    player.game_role = new_gamerole
    await db.commit()
    await db.refresh(player)
    return {'message': 'successful', 'new_role': player.game_role}
async def kick_player(
        player_id_to_kick: int,
        player_id: int,
        db: AsyncSession,
) -> dict:
    if player_id == player_id_to_kick:
        raise HTTPException(status_code=400, detail='Вы не можете кикнуть себя')
    player_to_kick = await find_player_by_id(player_id_to_kick, db)
    player = await find_player_by_id(player_id, db)

    if player_to_kick.team_id != player.team_id:
        raise HTTPException(status_code=400, detail="Игрок не находится в вашей команде")
    if not await is_player_captain(player_id, db):
        raise HTTPException(status_code=400, detail='Вы не являетесь капитаном команды')
    player_to_kick.team = None
    player_to_kick.team_id = None
    await db.commit()
    return {'message': 'successful'}