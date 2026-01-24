from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Role
from src.utils.security import hash_password

admin = {"email": "admin@test.com", "password": "admin"}
users: list[dict] = [
    {"email": "harpreet.singh@test.com", "password": "password"},
    {"email": "gurleen.kaur@test.com", "password": "password"},
    {"email": "amanpreet.singh@test.com", "password": "password"},
    {"email": "navjot.kaur@test.com", "password": "password"},
    {"email": "simran.kaur@test.com", "password": "password"},
    {"email": "jaspreet.singh@test.com", "password": "password"},
    {"email": "manpreet.singh@test.com", "password": "password"},
    {"email": "kiran.kaur@test.com", "password": "password"},
    {"email": "sandeep.singh@test.com", "password": "password"},
    {"email": "harleen.kaur@test.com", "password": "password"},
    {"email": "amritpal.singh@test.com", "password": "password"},
    {"email": "baljit.singh@test.com", "password": "password"},
    {"email": "parmeet.kaur@test.com", "password": "password"},
    {"email": "ranjit.singh@test.com", "password": "password"},
    {"email": "sukhpreet.kaur@test.com", "password": "password"},
    {"email": "deepak.singh@test.com", "password": "password"},
    {"email": "mandeep.kaur@test.com", "password": "password"},
    {"email": "arshdeep.singh@test.com", "password": "password"},
    {"email": "navdeep.kaur@test.com", "password": "password"},
    {"email": "karan.singh@test.com", "password": "password"},
]

async def seed_users(db: AsyncSession):
    result = await db.execute(select(User))
    existing_user = result.scalars().first()

    if existing_user is not None:
        return

    result = await db.execute(select(Role).where(Role.name=="user"))
    user_role = result.scalars().one_or_none()

    if user_role is None:
        user_role = Role(name="user")
        db.add(user_role)

    for user in users:
        u = User(email=user["email"], password= hash_password(user["password"]))
        u.roles.append(user_role)
        db.add(u)

    result = await db.execute(select(Role).where(Role.name=="admin"))
    admin_role = result.scalars().one_or_none()

    if admin_role is None:
        admin_role = Role(name="admin")
        db.add(admin_role)

    a = User(email=admin["email"], password=hash_password(admin["password"]))
    a.roles.append(admin_role)
    db.add(a)

    await db.commit()
