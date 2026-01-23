from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import String, DateTime, func, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base

user_roles=Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True)
)


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[EmailStr] = mapped_column(String, unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

class Role(Base):

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
