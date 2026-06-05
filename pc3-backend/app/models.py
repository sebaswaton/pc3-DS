from pydantic import BaseModel, Field
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: str


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
