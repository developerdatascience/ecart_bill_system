from pydantic import BaseModel
from typing import List


class LoginRequest(BaseModel):
    """schema for sign in"""
    email: str
    password: str


class SignUp(BaseModel):
    """schema for sign up"""
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class TokenResponse(BaseModel):
    """JWT toke response"""
    access_token: str
    token_type: str
    user_id: int
    email: str
    username: str