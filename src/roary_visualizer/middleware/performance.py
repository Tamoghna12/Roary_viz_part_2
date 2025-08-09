import time
import functools
from typing import Any, Callable, TypeVar
from ..config.logging.config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

def measure_performance(threshold_ms: float = 1000) -> Callable:
    """Decorator to measure and log function performance
    
    Args:
        threshold_ms: Performance threshold in milliseconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            if execution_time_ms > threshold_ms:
                logger.warning(
                    f"Performance warning: {func.__name__} took {execution_time_ms:.2f}ms "
                    f"(threshold: {threshold_ms}ms)"
                )
            else:
                logger.debug(
                    f"Performance metric: {func.__name__} took {execution_time_ms:.2f}ms"
                )
            
            return result
        return wrapper
    return decorator

def cache_data(ttl_seconds: int = 300) -> Callable:
    """Decorator to cache function results with TTL
    
    Args:
        ttl_seconds: Time to live for cached data in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time.time()
            
            # Check if result is cached and not expired
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            # Calculate new result and cache it
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            logger.debug(f"Cache miss for {func.__name__}, storing new result")
            
            return result
        return wrapper
    return decorator