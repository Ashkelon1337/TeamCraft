

import src.auth.security as security
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Cookie, Response, HTTPException
from src.models.players import Player
from src.schemas.auth_schema import UserLogin, UserRegister
from src.services.db_service import find_user_by_username, register_player_in_db



async def set_cookie(token, response: Response):
    response.set_cookie(
        key='users_access_token',
        value=token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=1800,
    )

async def get_access_token(player_data: UserLogin, db: AsyncSession) -> str:
    user = await find_user_by_username(player_data.username, db)
    is_pass_correct = security.verify_password(
        plain_password=player_data.password,
        hashed_password=user.hashed_password
    )
    if not is_pass_correct:
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль")
    access_token = security.create_access_token(user.id)
    return access_token

