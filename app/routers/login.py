"""
Creating a user signup and signup routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.models.login import Signup, Signin


Base.metadata.create_all(bind=engine)

router = APIRouter()




