"""
Creating a user signup and signup routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import engine, get_db, Base
from app.models.users import User, UserLoginLog
from app.schema.users import SignUp, SignIn, Token, UserOut
from app.core.database import get_db, DbDependency
from app.core.auth import get_hashed_password, create_access_token


Base.metadata.create_all(bind=engine)

router = APIRouter()



@router.post("/signup", response_model=UserOut)
async def signup(user: SignUp, db:DbDependency):
    """An API for user registration"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_hashed_password(user.password)
    try:
        new_user = User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
