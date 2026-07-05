import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Cookie, HTTPException
from src.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pass_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_pass_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
def create_access_token(user_id: int) -> str:
    payload = {
        'sub': str(user_id),
        'exp': datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    }
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

async def get_user_id_from_cookie(users_access_token: str | None = Cookie(None)):
    if not users_access_token:
        raise HTTPException(status_code=401)
    try:
        payload = jwt.decode(jwt=users_access_token, key=SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(status_code=401)
        return int(user_id)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401)