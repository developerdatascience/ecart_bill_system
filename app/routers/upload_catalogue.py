import pandas as pd
from fastapi import APIRouter, Depends, Form, status, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models.orders import ProductCatalogue
from app.models.users import User
from fastapi.templating import Jinja2Templates
from app.core.database import DbDependency
from app.core.auth import get_current_active_user



router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/settings", response_class=HTMLResponse, status_code=200)
async def get_product_catalogue(request: Request, user: str = Depends(get_current_active_user)):
    flash_success = request.cookies.get("flash_success")
    flash_error = request.cookies.get("flash_error")
    response= templates.TemplateResponse("product_catalogue.html", {"request": request,
                                                                 "user": {
                                                                     "first_name": user.first_name,
                                                                    "last_name": user.last_name,
                                                                    "profile_picture": user.profile_picture,
                                                                    "designation": user.designation,
                                                                    "username": user.username,
                                                                    "email": user.email},
                                                                "flash_success": flash_success,
                                                                "flash_error": flash_error})
    
    # Clear the cookies after displaying
    if flash_success:
        response.delete_cookie("flash_success")
    if flash_error:
        response.delete_cookie("flash_error")
    return response


@router.post("/upload_catalogue", response_class=HTMLResponse, status_code=200)
async def upload_catalogue(request: Request, db: DbDependency, file: UploadFile = File(...)):
    """Upload Product Catalogue"""
    try:
        if file.filename.endswith(".csv"):
            df: pd.DataFrame = pd.read_csv(file.file)
        elif file.filename.endswith([".xlsx", ".xlx"]):
            df: pd.DataFrame = pd.read_excel(file.file, engine="openpyxl")
        else:
            raise HTTPException(status_code=415, detail = "Unsupported file format. Only CSV, XLSX and XLS files are supported")

        required_columns = {"product_name", "brand", "mrp", "pack_size", "category", "discount","barcode"}
        df.columns = df.columns.str.lower()
        if not required_columns.issubset(set(df.columns)):
            raise HTTPException(status_code=400, detail="Missing required columns")

        # Convert DataFrame to list of dictionaries
        products = df.to_dict(orient="records")
        db.bulk_insert_mappings(ProductCatalogue, products)
        db.commit()
        response = RedirectResponse("/settings", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie("flash_success", "Catalogue updated successfully!", max_age=5)
        return response
    except Exception as e:
        db.rollback()
        response = RedirectResponse("/settings", status_code=303)
        response.set_cookie("flash_error", f"Failed to upload catalogue: {str(e)}", max_age=5)
        return response
