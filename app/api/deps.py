from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/admin/auth/login")

async def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedException("Invalid token credentials")
        return username
    except JWTError:
        raise UnauthorizedException("Invalid token credentials")

from typing import Annotated

# alias for dependency injection
AdminDep = Annotated[str, Depends(get_current_admin)]
SessionDep = Annotated[AsyncSession, Depends(get_db)]
