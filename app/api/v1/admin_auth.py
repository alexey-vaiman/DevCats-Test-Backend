from fastapi import APIRouter, Body
from app.api.deps import SessionDep
from app.schemas.auth import AdminLoginRequest, AdminLoginResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["AdminAuth"])

@router.post("/login", response_model=AdminLoginResponse)
async def login(req: AdminLoginRequest = Body(...)):
    """Admin login (returns bearer token)"""
    print(f"Login request received for user: {req.username}")
    return await auth_service.authenticate_admin(req)
