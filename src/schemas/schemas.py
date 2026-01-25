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
    total_tickets: int
    price_in_rupee: int
    venue: str
    event_date: datetime

class EventResponseSchema(BaseModel):
    id: int
    title: str
    total_tickets: int
    available_tickets: int
    price_in_rupee: int
    venue: str
    event_date: datetime

class EventUpdateSchema(BaseModel):
    title: str
    price_in_rupee: int
    venue: str
    event_date: datetime
