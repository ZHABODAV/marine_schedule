import logging
import traceback
from typing import Dict, Any, Optional
from flask import jsonify

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base class for application errors."""
    def __init__(self, message: str, status_code: int = 500, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv

class ValidationError(AppError):
    """Raised when input validation fails."""
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, payload=payload)

class NotFoundError(AppError):
    """Raised when a resource is not found."""
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, payload=payload)

class UnauthorizedError(AppError):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication required", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, payload=payload)

class ForbiddenError(AppError):
    """Raised when permission is denied."""
    def __init__(self, message: str = "Insufficient permissions", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, payload=payload)

def handle_app_error(error: AppError):
    """Handle custom application errors."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def handle_generic_error(error: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(error)}\n{traceback.format_exc()}")
    response = jsonify({
        'error': 'Internal Server Error',
        'message': str(error) if hasattr(error, 'message') else str(error)
    })
    response.status_code = 500
    return response

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    app.register_error_handler(AppError, handle_app_error)
    app.register_error_handler(ValidationError, handle_app_error)
    app.register_error_handler(NotFoundError, handle_app_error)
    app.register_error_handler(UnauthorizedError, handle_app_error)
    app.register_error_handler(ForbiddenError, handle_app_error)
    app.register_error_handler(Exception, handle_generic_error)
