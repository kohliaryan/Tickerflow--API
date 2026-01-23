from datetime import datetime, timezone, timedelta
import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.openapi.models import OAuth2
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.models.users import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/aith/login")

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) ->str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    # Standard 401 Error to return if anything goes wrong
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # A. Decode Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # B. Extract Data (we stored user_id in 'sub' or 'user_id'?)
        # Let's assume you used: data={"sub": str(user.id)}
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except jwt.PyJWTError:  # Catches expired or fake tokens
        raise credentials_exception

    # C. Get User from DB
    # Note: We use int(user_id) because 'sub' is a string in JWT
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user
