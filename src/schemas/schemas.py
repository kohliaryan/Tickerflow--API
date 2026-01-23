from pydantic import BaseModel, EmailStr


class AuthRequestSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
