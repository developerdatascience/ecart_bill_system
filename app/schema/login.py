from pydantic import BaseModel
from typing import List


class SignIn(BaseModel):
    """schema for sign in"""
    username: str
    password: str


class SignUp(BaseModel):
    """schema for sign up"""
    username: str
    email: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str