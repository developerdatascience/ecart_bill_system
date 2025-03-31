from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.auth import get_current_active_user
from app.core.database import DbDependency
from app.models.users import User
from app.models.orders import ProductCatalogue

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/billing", response_class=HTMLResponse, status_code=200)
async def get_bills(request: Request, user: str = Depends(get_current_active_user)):
    return templates.TemplateResponse("bills.html", {"request": request,
                                                     "user": {
                                                        "first_name": user.first_name,
                                                        "last_name": user.last_name,
                                                        "profile_picture": user.profile_picture,
                                                        "designation": user.designation,
                                                        "username": user.username,
                                                        "email": user.email}})


@router.post("/add_items", response_class=JSONResponse, status_code=200)
async def show_items(
        request: Request,
        db: DbDependency,
        item_description: str = Form(...),
        quantity: int = Form(...),
        discount: float = Form(...),
        total_price: float = Form(...)
        ):
    all_items = db.query(ProductCatalogue).filter(ProductCatalogue)
    return all_items