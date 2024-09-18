from pydantic import BaseModel
from typing import Literal

class User(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    user_id: int

class Chat(BaseModel):
    name: str
    type: Literal['private', 'public']

class Message(BaseModel):
    user1_id: int
    user2_id: int
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
