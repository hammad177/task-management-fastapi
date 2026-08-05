from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.common.response import ApiResponseBuilder


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI/Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return ApiResponseBuilder.bad_request(
        message="Validation error",
        errors=errors
    )


async def pydantic_validation_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return ApiResponseBuilder.bad_request(
        message="Validation error",
        errors=errors
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    return ApiResponseBuilder.conflict(
        message="Database integrity error",
        errors=["A resource with this information already exists"]
    )
    
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with formatted response"""
    # Map status codes to appropriate messages
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return ApiResponseBuilder.unauthorized(
            message="Authentication required",
            errors=[exc.detail] if exc.detail else ["Not authenticated"]
        )
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        return ApiResponseBuilder.forbidden(
            message="Permission denied",
            errors=[exc.detail] if exc.detail else ["You don't have permission"]
        )
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        return ApiResponseBuilder.not_found(
            message="Resource not found",
            errors=[exc.detail] if exc.detail else ["The requested resource was not found"]
        )
    elif exc.status_code == status.HTTP_409_CONFLICT:
        return ApiResponseBuilder.conflict(
            message="Conflict",
            errors=[exc.detail] if exc.detail else ["Resource already exists"]
        )
    else:
        # Generic HTTP exception
        return ApiResponseBuilder.error(
            message=exc.detail or "An error occurred",
            errors=[exc.detail] if exc.detail else ["An error occurred"],
            status_code=exc.status_code
        )

async def method_not_allowed_handler(request: Request, exc: Exception):
    """Handle Method Not Allowed errors with formatted response"""
    return ApiResponseBuilder.error(
        message="Method not allowed",
        errors=[f"The HTTP method '{request.method}' is not allowed for this endpoint"],
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )


async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    from app.common.settings import settings
    
    # Log the error here if needed
    print(f"Unhandled error: {exc}")
    
    return ApiResponseBuilder.server_error(
        message="An unexpected error occurred",
        errors=[str(exc)] if settings.DEBUG else ["Internal server error"]
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(status.HTTP_405_METHOD_NOT_ALLOWED, method_not_allowed_handler)
    app.add_exception_handler(Exception, global_exception_handler)