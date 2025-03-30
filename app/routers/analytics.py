from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.auth import get_current_active_user
from app.core.database import DbDependency
from app.models.users import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")



@router.get("/analytics", response_class=HTMLResponse, status_code=200)
async def get_profile(request: Request, user: str = Depends(get_current_active_user)):
    return templates.TemplateResponse("analytics.html", {"request": request, 
                                                    "user": {
                                                        "username": user.username,
                                                        "email": user.email}
                                                    })
