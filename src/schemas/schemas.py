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
    total_tickets: int = Field(..., gt=0)
    event_date: datetime

class EventResponseSchema(BaseModel):
    id: int
    title: str
    total_tickets: int
    available_tickets: int
    event_date: datetime

class EventUpdateSchema(BaseModel):
    title: str
    event_date: datetime
