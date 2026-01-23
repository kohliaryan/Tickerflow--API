from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.deps.auth import get_current_user
from src.models.users import User, Role
from src.schemas.schemas import AuthRequestSchema, TokenSchema
from src.utils.security import hash_password, create_access_token, verify_password

auth_router = APIRouter()

@auth_router.post("/signup", status_code=201)
async def signup(user_data: AuthRequestSchema, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(User).where(User.email==user_data.email))
    existing_user = result.scalars().one_or_none()

    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Account already exist with this email!")

    new_user = User(email=user_data.email, password=hash_password(user_data.password))
    role_user_result = await db.execute(select(Role).where(Role.name=="user"))
    user_role = role_user_result.scalars().one_or_none()

    if user_role is None:
        raise HTTPException(status_code=500, detail="some error on server!")

    new_user.roles.append(user_role)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"msg": "User created successfully!"}

@auth_router.post("/login", response_model=TokenSchema)
async def log_in(
    user_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == user_data.username)
    )
    user = result.scalars().one_or_none()

    if user is None or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
    }