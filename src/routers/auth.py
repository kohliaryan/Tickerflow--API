from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
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
async def login(user_data: AuthRequestSchema, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(User).where(User.email==user_data.email))
    user = result.scalars().one_or_none()
    if user is None:
        raise HTTPException(status_code=400, detail="No user with this email found!")

    is_valid = verify_password(user_data.password, user.password)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid password")

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
