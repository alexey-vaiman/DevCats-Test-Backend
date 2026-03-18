from app.core.config import settings
from app.core.security import create_access_token
from app.core.exceptions import UnauthorizedException
from app.schemas.auth import AdminLoginRequest, AdminLoginResponse

# Hardcoded for prototype purposes. In a real application, fetch from DB.
ADMIN_USERNAME_ENV = "admin"
ADMIN_PASSWORD_ENV = "admin123"

class AuthService:
    
    @staticmethod
    async def authenticate_admin(req: AdminLoginRequest) -> AdminLoginResponse:
        # Simplistic validation
        print(f"Authenticating: {req.username} / {req.password}")
        if req.username != ADMIN_USERNAME_ENV or req.password != ADMIN_PASSWORD_ENV:
            print(f"Auth failed: expected {ADMIN_USERNAME_ENV}/{ADMIN_PASSWORD_ENV}")
            raise UnauthorizedException("Incorrect username or password")
        
        access_token = create_access_token(subject=req.username)
        return AdminLoginResponse(access_token=access_token, token_type="bearer")

auth_service = AuthService()
