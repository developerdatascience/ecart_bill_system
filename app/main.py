from fastapi import FastAPI
from .routers import orders, login, landingpage, profile, analytics, bills, upload_catalogue
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# CONFIGURE CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(landingpage.router, tags=["landingpage"])
app.include_router(orders.router, tags=["orders"])
app.include_router(login.router, tags=["Authentications"])
app.include_router(profile.router, tags=["profile"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(bills.router, tags=["bills"])
app.include_router(upload_catalogue.router, tags=["Upload Product Catalogue"])