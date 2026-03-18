from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, error: str, message: str, status_code: int = 400, details: dict[str, Any] | None = None):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}

async def custom_exception_handler(request: Request, exc: CustomException):
    content = {
        "error": exc.error,
        "message": exc.message,
    }
    if exc.details:
        content["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=content)

class NotFoundException(CustomException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(error="not_found", message=message, status_code=404)

class UnauthorizedException(CustomException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(error="unauthorized", message=message, status_code=401)

class ValidationErrorException(CustomException):
    def __init__(self, message: str = "Validation error", details: dict[str, Any] | None = None):
        super().__init__(error="validation_error", message=message, status_code=400, details=details)
