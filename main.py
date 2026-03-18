from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import CustomException, custom_exception_handler
from app.api.v1 import (
    public as public_router,
    admin_auth as admin_auth_router,
    admin_products as admin_products_router,
    admin_sellers as admin_sellers_router,
    admin_offers as admin_offers_router,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Exception handlers
app.add_exception_handler(CustomException, custom_exception_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, modify in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(public_router.router, prefix="/v1/public")
app.include_router(admin_auth_router.router, prefix="/v1/admin")
app.include_router(admin_products_router.router, prefix="/v1/admin")
app.include_router(admin_sellers_router.router, prefix="/v1/admin")
app.include_router(admin_offers_router.products_offers_router, prefix="/v1/admin")
app.include_router(admin_offers_router.offers_router, prefix="/v1/admin")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

