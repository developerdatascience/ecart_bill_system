"""
Creating a user signup and signup routes
"""

from datetime import  timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status, Query
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import engine, get_db, Base
from app.models.users import User, UserLoginLog
from app.schema.users import SignUp, LoginRequest, Token, UserOut
from app.core.database import get_db, DbDependency
from app.core.auth import get_hashed_password, create_access_token, authenticate_user, get_current_user, get_current_active_user
from app.core.config import settings


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


@router.get("/signin", response_class=HTMLResponse, status_code=200)
async def getsiginpage(request: Request):
    return templates.TemplateResponse("sigin.html", {"request": request})



@router.get("/application", response_class=HTMLResponse, status_code=200)
async def application(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("base.html", {"request": request, 
                                                    "user": {
                                                        "username": user.username,
                                                        "email": user.email}
                                                    })


@router.get("/login", response_class=HTMLResponse, status_code=200)
async def login_page(
    request: Request,
    error: str = None,
    success: str = None
):
    """Render login page with error/success messages"""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": error,
            "success": success
        }
    )

@router.post("/login_dashboard", response_class=HTMLResponse, status_code=200)
async def login_user(
    db: DbDependency,
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission"""
    #Authenticate user
    user = authenticate_user(db, email, password)

    if not user:
        return RedirectResponse(
            url="/login?error=Invalid+email+or+password",
            status_code = status.HTTP_303_SEE_OTHER
        )
    
    if not user.is_active:
        return RedirectResponse(
            url="/login?error=Account+is+disabled",
            status_code = status.HTTP_303_SEE_OTHER
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data = {"sub": user.email},
        expires_delta = access_token_expires
    )

    response = RedirectResponse(url="/application", status_code = status.HTTP_303_SEE_OTHER)

    login_log= UserLoginLog(user_id=user.id)
    db.add(login_log)
    db.commit()
    db.refresh(login_log)

    # Set HTTP-only cookie with token

    response.set_cookie(
        key="access_token",
        value= access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure = True,
        samesite="Lax"
    )

    return response

    

@router.post("/logout", response_class=HTMLResponse, status_code=200)
async def logout_user(
     db: DbDependency,
    user: User = Depends(get_current_active_user)
):
    """
    Handle user logout by:
    1. Recording logout time in UserLoginLog
    2. Clearing authentication cookie
    3. Redirecting to login page
    """
    # Find the most recent login entry withour login time
    login_log = db.query(UserLoginLog).filter(
        UserLoginLog.user_id == user.id,
        UserLoginLog.logout_time.is_(None)
    ).order_by(UserLoginLog.login_time.desc()).first()

    if login_log:
        login_log.logout_time = datetime.now()
        db.add(login_log)
        db.commit()

    response = RedirectResponse(
        url="/login",
        status_code = status.HTTP_303_SEE_OTHER
    )

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="Lax"
        )

    return response
