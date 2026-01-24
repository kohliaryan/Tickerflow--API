from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AuthRequestSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class EventRequestSchema(BaseModel):
    title: str
    total_ticket: int = Field(..., gt=0)
    event_date: datetime
