from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, status_code=200)
async def landingpage(request: Request):
    return templates.TemplateResponse("/landingpage.html", {"request": request})