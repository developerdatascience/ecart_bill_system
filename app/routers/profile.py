from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.auth import get_current_active_user
from app.core.database import DbDependency
from app.models.users import User
from pathlib import Path
import os
import shutil

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Ensure the directory for profile pictures exists
PROFILE_PIC_DIR = "static/images/"
os.makedirs(PROFILE_PIC_DIR, exist_ok=True)



@router.get("/profile", response_class=HTMLResponse, status_code=200)
async def get_profile(request: Request, user: str = Depends(get_current_active_user)):
    flash_success = request.cookies.get("flash_success")
    flash_error = request.cookies.get("flash_error")

    response= templates.TemplateResponse("profile.html", {
                                                    "request": request, 
                                                    "user": {
                                                        "first_name": user.first_name,
                                                        "last_name": user.last_name,
                                                        "profile_picture": user.profile_picture,
                                                        "designation": user.designation,
                                                        "username": user.username,
                                                        "email": user.email},
                                                    "flash_success": flash_success,
                                                    "flash_error": flash_error
                                                        })
    # Clear the cookies after displaying
    if flash_success:
        response.delete_cookie("flash_success")
    if flash_error:
        response.delete_cookie("flash_error")
    
    return response


@router.post("/update_profile", response_class=HTMLResponse, status_code=200)
async def update_profile(
    request: Request, 
    db: DbDependency,
    first_name: str = Form(...),
    last_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    designation: str = Form(...),
    profile_picture: UploadFile = File(None),
    current_user = Depends(get_current_active_user),
):
    try:
        # Store previous values for path calculation
        previous_email = current_user.email
        previous_username = current_user.username

        # Update user fields
        current_user.username = username
        current_user.email = email
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.designation = designation

        # Handle profile picture
        if profile_picture and profile_picture.filename:
            # New image upload
            directory = os.path.join(PROFILE_PIC_DIR, current_user.email)
            os.makedirs(directory, exist_ok=True)
            filename = f"{current_user.username}.jpg" 
            file_location = os.path.join(directory, filename)
            
            # Save new file
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(profile_picture.file, buffer)
            
            current_user.profile_picture = file_location
        else:
            # No new image - update path if username/email changed
            if previous_email != current_user.email or previous_username != current_user.username:
                old_path = current_user.profile_picture
                if old_path and os.path.exists(old_path):
                    new_directory = os.path.join(PROFILE_PIC_DIR, current_user.email)
                    os.makedirs(new_directory, exist_ok=True)
                    new_filename = f"{current_user.username}.jpg"
                    new_path = os.path.join(new_directory, new_filename)
                    
                    # Copy file to new location
                    shutil.copy(old_path, new_path)
                    current_user.profile_picture = new_path
                    
                    # Remove old directory if empty
                    try:
                        os.rmdir(os.path.dirname(old_path))
                    except OSError:
                        pass  # Directory not empty

        db.commit()
        db.refresh(current_user)
        response= RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie("flash_success", "Profile updated successfully!", max_age=5)
        return response

    except Exception as e:
        db.rollback()
        # Handle error appropriately
        # raise HTTPException(status_code=400, detail=str(e))
        response = RedirectResponse("/profile", status_code=303)
        response.set_cookie("flash_error", f"Failed to update profile: {str(e)}", max_age=5)
        return response