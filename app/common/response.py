from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from fastapi import status
from fastapi.responses import JSONResponse

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    status_code: int = Field(..., description="HTTP status code")
    data: Optional[T] = Field(None, description="Response data (if any)")
    errors: Optional[List[str]] = Field(None, description="Error details (if any)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Task created successfully",
                "status_code": 201,
                "data": {"id": 1, "title": "Learn FastAPI"},
                "errors": None
            }
        }


class ApiResponseBuilder:
    """Builder class for creating standardized API responses"""
    
    @staticmethod
    def success(
        message: str = "Success",
        data: Any = None,
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """Create a success response"""
        response = ApiResponse(
            success=True,
            message=message,
            status_code=status_code,
            data=data,
            errors=None
        )
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump(mode="json")
        )
    
    @staticmethod
    def error(
        message: str = "Error occurred",
        errors: Optional[List[str]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> JSONResponse:
        """Create an error response"""
        response = ApiResponse(
            success=False,
            message=message,
            status_code=status_code,
            data=None,
            errors=errors
        )
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump(mode="json")
        )
    
    @staticmethod
    def created(
        message: str = "Resource created successfully",
        data: Any = None
    ) -> JSONResponse:
        """Create a 201 Created response"""
        return ApiResponseBuilder.success(
            message=message,
            data=data,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def no_content(
        message: str = "Resource deleted successfully"
    ) -> JSONResponse:
        """Create a 204 No Content response"""
        response = ApiResponse(
            success=True,
            message=message,
            status_code=status.HTTP_204_NO_CONTENT,
            data=None,
            errors=None
        )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=response.model_dump(mode="json")
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        errors: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a 404 Not Found response"""
        return ApiResponseBuilder.error(
            message=message,
            errors=errors or ["The requested resource was not found"],
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def bad_request(
        message: str = "Bad request",
        errors: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a 400 Bad Request response"""
        return ApiResponseBuilder.error(
            message=message,
            errors=errors or ["Invalid request parameters"],
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Unauthorized",
        errors: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a 401 Unauthorized response"""
        return ApiResponseBuilder.error(
            message=message,
            errors=errors or ["Authentication required"],
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(
        message: str = "Forbidden",
        errors: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a 403 Forbidden response"""
        return ApiResponseBuilder.error(
            message=message,
            errors=errors or ["You don't have permission to access this resource"],
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def conflict(
        message: str = "Conflict",
        errors: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a 409 Conflict response"""
        return ApiResponseBuilder.error(
            message=message,
            errors=errors or ["Resource already exists or conflict detected"],
            status_code=status.HTTP_409_CONFLICT
        )
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        errors: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a 500 Internal Server Error response"""
        return ApiResponseBuilder.error(
            message=message,
            errors=errors or ["An unexpected error occurred"],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Convenience functions for direct use
def success_response(
    message: str = "Success",
    data: Any = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Quick success response"""
    return ApiResponseBuilder.success(message, data, status_code)


def error_response(
    message: str = "Error occurred",
    errors: Optional[List[str]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """Quick error response"""
    return ApiResponseBuilder.error(message, errors, status_code)