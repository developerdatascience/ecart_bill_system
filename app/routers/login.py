"""
Creating a user signup and signup routes
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status, Query
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import engine, get_db, Base
from app.models.users import User, UserLoginLog
from app.schema.users import SignUp, SignIn, Token, UserOut
from app.core.database import get_db, DbDependency
from app.core.auth import get_hashed_password, create_access_token


Base.metadata.create_all(bind=engine)

router = APIRouter()
templates = Jinja2Templates(directory="templates")



@router.get("/signup", response_class=HTMLResponse, status_code=200)
async def signup(
    request: Request,
    success: bool = Query(default=False)
    ):
    return templates.TemplateResponse(
        "signup.html", 
        {
            "request": request,
            "success": success,
            "error": request.query_params.get("error")
        }
        )


@router.post("/register", response_class=HTMLResponse, status_code=200)
async def register(
    request: Request,
    db:DbDependency,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
    ):
    """An API for user registration"""
    db_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
        ).first()
    if db_user:
        error_msg = ""
        if db_user.email == email:
            error_msg += "Email already registered"
        if db_user.username == username:
            error_msg += "Username already taken"
        return RedirectResponse(
            url=f"/signup?error={error_msg.strip().replace(' ', '+')}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    hashed_password = get_hashed_password(password)
    try:
        new_user = User(
        username = username,
        email = email,
        hashed_password = hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return RedirectResponse(url="/signup?success=true", status_code=status.HTTP_303_SEE_OTHER)
    except IntegrityError as e:
        db.rollback()
        raise RedirectResponse(url=f"/signup?error=Username+or+email+already+exists", 
                               status_code = status.HTTP_303_SEE_OTHER)
    except Exception as e:
        db.rollback()
        raise RedirectResponse(url=f"/signup?error={str(e).replace(' ', '+')}", 
                               status_code = status.HTTP_303_SEE_OTHER)
