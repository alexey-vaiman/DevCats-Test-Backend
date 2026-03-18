from typing import Optional
from pydantic import BaseModel, Field

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = Field(..., examples=["bearer"])
