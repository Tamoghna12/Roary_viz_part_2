from prometheus_client import Counter, Histogram, Gauge, start_http_server
from functools import wraps
import time
from typing import Callable, Any

# Define metrics
REQUEST_COUNT = Counter(
    'app_request_count',
    'Number of requests received',
    ['endpoint']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

MEMORY_USAGE = Gauge(
    'app_memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'app_cpu_usage_percent',
    'CPU usage percentage'
)

FILE_PROCESSING_TIME = Histogram(
    'app_file_processing_seconds',
    'Time spent processing files',
    ['file_type']
)

ACTIVE_USERS = Gauge(
    'app_active_users',
    'Number of active users'
)

ERROR_COUNT = Counter(
    'app_error_count',
    'Number of errors occurred',
    ['type']
)

def initialize_metrics(port: int = 9090) -> None:
    """Initialize Prometheus metrics server
    
    Args:
        port: Port number for the metrics server
    """
    start_http_server(port)

def track_request_count(endpoint: str) -> Callable:
    """Decorator to track request count for endpoints
    
    Args:
        endpoint: Name of the endpoint
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            REQUEST_COUNT.labels(endpoint=endpoint).inc()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def track_request_latency(endpoint: str) -> Callable:
    """Decorator to track request latency
    
    Args:
        endpoint: Name of the endpoint
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(
                time.time() - start_time
            )
            return result
        return wrapper
    return decorator

def track_file_processing(file_type: str) -> Callable:
    """Decorator to track file processing time
    
    Args:
        file_type: Type of file being processed
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            FILE_PROCESSING_TIME.labels(file_type=file_type).observe(
                time.time() - start_time
            )
            return result
        return wrapper
    return decorator

def update_memory_usage(usage_bytes: float) -> None:
    """Update memory usage metric
    
    Args:
        usage_bytes: Current memory usage in bytes
    """
    MEMORY_USAGE.set(usage_bytes)

def update_cpu_usage(usage_percent: float) -> None:
    """Update CPU usage metric
    
    Args:
        usage_percent: Current CPU usage percentage
    """
    CPU_USAGE.set(usage_percent)

def update_active_users(count: int) -> None:
    """Update active users metric
    
    Args:
        count: Current number of active users
    """
    ACTIVE_USERS.set(count)

def record_error(error_type: str) -> None:
    """Record an error occurrence
    
    Args:
        error_type: Type of error that occurred
    """
    ERROR_COUNT.labels(type=error_type).inc()