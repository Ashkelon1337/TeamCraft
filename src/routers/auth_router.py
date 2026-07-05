from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
import src.auth.security as security
from src.schemas.auth_schema import UserLogin, UserRegister
from src.services.db_service import register_player_in_db
from src.services.auth_service import get_access_token, set_cookie


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post('/register')
async def register(register_data: UserRegister, response: Response, db: AsyncSession = Depends(get_db)):
    new_player = await register_player_in_db(player_data=register_data, db=db)
    token = security.create_access_token(new_player.id)
    await set_cookie(token=token, response=response)
    return {'message': 'Успешная регистрация!'}

@router.post('/login')
async def login(login_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    token = await get_access_token(player_data=login_data, db=db,)
    await set_cookie(token=token, response=response,)
    return {'message': 'Успешный вход!'}