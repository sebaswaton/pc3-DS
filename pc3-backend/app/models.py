from pydantic import BaseModel, Field
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: str
    dni: str = Field(pattern=r'^\d{8}$')
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateInitiativeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    author_id: str


class SignRequest(BaseModel):
    user_id: str


class CommentRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    author_id: str
    parent_id: Optional[str] = None
