import functools
import traceback
from typing import Any, Callable, TypeVar
import streamlit as st
from ..config.logging.config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class AppError(Exception):
    """Base application error class"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ValidationError(AppError):
    """Error raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class FileProcessingError(AppError):
    """Error raised when file processing fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for handling errors in Streamlit functions
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            st.error(f"⚠️ {str(e)}")
        except FileProcessingError as e:
            logger.error(f"File processing error: {str(e)}")
            st.error(f"❌ Error processing file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            st.error(
                "An unexpected error occurred. Please try again or contact support if the problem persists."
            )
            if st.session_state.get('debug_mode', False):
                st.exception(e)
        return None
    return wrapper

def validate_input(condition: bool, message: str) -> None:
    """Validate input condition or raise ValidationError
    
    Args:
        condition: Condition to validate
        message: Error message if validation fails
        
    Raises:
        ValidationError: If validation fails
    """
    if not condition:
        raise ValidationError(message)

def validate_file_type(filename: str, allowed_extensions: set[str]) -> None:
    """Validate file extension
    
    Args:
        filename: Name of file to validate
        allowed_extensions: Set of allowed file extensions
        
    Raises:
        ValidationError: If file extension is not allowed
    """
    ext = filename.lower().split('.')[-1]
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Invalid file type: {filename}. Allowed extensions: {', '.join(allowed_extensions)}"
        )