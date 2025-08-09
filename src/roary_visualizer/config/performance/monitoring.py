import os
import time
import psutil
import logging
import threading
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
import resource
from ..monitoring.prometheus import (
    update_memory_usage,
    update_cpu_usage,
    update_active_users
)

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime

class PerformanceMonitor:
    """Monitors application performance metrics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.process = psutil.Process(os.getpid())
        self._metrics: Dict[str, PerformanceMetrics] = {}
    
    def monitor(self, name: str = None):
        """Decorator to monitor function performance
        
        Args:
            name: Optional name for the metrics
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                start_memory = self.get_memory_usage()
                
                result = func(*args, **kwargs)
                
                end_time = time.perf_counter()
                end_memory = self.get_memory_usage()
                
                metric_name = name or func.__name__
                self._metrics[metric_name] = PerformanceMetrics(
                    execution_time=end_time - start_time,
                    memory_usage=end_memory - start_memory,
                    cpu_usage=self.get_cpu_usage(),
                    timestamp=datetime.now()
                )
                
                self._log_metrics(metric_name)
                return result
            return wrapper
        return decorator
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB
        
        Returns:
            float: Memory usage in MB
        """
        try:
            return self.process.memory_info().rss / (1024 * 1024)
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {str(e)}")
            return 0.0
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage
        
        Returns:
            float: CPU usage percentage
        """
        try:
            return self.process.cpu_percent(interval=0.1)
        except Exception as e:
            logger.warning(f"Failed to get CPU usage: {str(e)}")
            return 0.0
    
    def get_metrics(self, name: str = None) -> Dict[str, PerformanceMetrics]:
        """Get collected metrics
        
        Args:
            name: Optional name to filter metrics
            
        Returns:
            Dict[str, PerformanceMetrics]: Collected metrics
        """
        if name:
            return {name: self._metrics[name]} if name in self._metrics else {}
        return self._metrics
    
    def _log_metrics(self, name: str) -> None:
        """Log performance metrics
        
        Args:
            name: Name of the metrics to log
        """
        metrics = self._metrics[name]
        logger.info(
            f"Performance metrics for {name}:\n"
            f"  Execution time: {metrics.execution_time:.3f}s\n"
            f"  Memory usage: {metrics.memory_usage:.2f}MB\n"
            f"  CPU usage: {metrics.cpu_usage:.1f}%"
        )
    
    def check_resource_limits(self) -> Dict[str, Any]:
        """Check system resource limits
        
        Returns:
            Dict[str, Any]: Resource limit information
        """
        try:
            rusage = resource.getrusage(resource.RUSAGE_SELF)
            return {
                'max_rss': rusage.ru_maxrss / 1024,  # Convert to MB
                'user_time': rusage.ru_utime,
                'system_time': rusage.ru_stime,
                'page_faults': rusage.ru_majflt,
                'io_operations': rusage.ru_inblock + rusage.ru_oublock,
                'voluntary_context_switches': rusage.ru_nvcsw,
                'involuntary_context_switches': rusage.ru_nivcsw
            }
        except Exception as e:
            logger.warning(f"Failed to get resource limits: {str(e)}")
            return {}
    
    def reset_metrics(self) -> None:
        """Reset collected metrics"""
        self._metrics.clear()

# Create global instance
performance_monitor = PerformanceMonitor()

class PerformanceStats:
    """Class to track performance statistics"""
    
    def __init__(self):
        self.function_timings: Dict[str, float] = {}
        self.memory_usage: float = 0.0
        self.cpu_usage: float = 0.0
        self.active_users: int = 0
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()

    def start_monitoring(self, interval: float = 5.0) -> None:
        """Start monitoring system resources
        
        Args:
            interval: Time between measurements in seconds
        """
        def monitor_resources():
            while not self._stop_monitoring.is_set():
                try:
                    process = psutil.Process()
                    
                    # Update memory usage (in bytes)
                    self.memory_usage = process.memory_info().rss
                    update_memory_usage(self.memory_usage)
                    
                    # Update CPU usage (percentage)
                    self.cpu_usage = process.cpu_percent(interval=1.0)
                    update_cpu_usage(self.cpu_usage)
                    
                    # Log current stats
                    logger.debug(
                        f"Performance stats - Memory: {self.memory_usage / 1024 / 1024:.2f}MB, "
                        f"CPU: {self.cpu_usage:.1f}%"
                    )
                    
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error monitoring resources: {str(e)}")
                    time.sleep(interval)
        
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(
            target=monitor_resources,
            daemon=True
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring system resources"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_monitoring.set()
            self._monitor_thread.join(timeout=5.0)

    def record_timing(self, function_name: str, execution_time: float) -> None:
        """Record function execution time
        
        Args:
            function_name: Name of the function
            execution_time: Time taken to execute in seconds
        """
        self.function_timings[function_name] = execution_time
        logger.debug(f"Function {function_name} took {execution_time:.3f} seconds")

    def update_active_users(self, count: int) -> None:
        """Update number of active users
        
        Args:
            count: Current number of active users
        """
        self.active_users = count
        update_active_users(count)
        logger.debug(f"Active users: {count}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics
        
        Returns:
            Dict containing current performance metrics
        """
        return {
            "memory_usage_mb": self.memory_usage / 1024 / 1024,
            "cpu_usage_percent": self.cpu_usage,
            "active_users": self.active_users,
            "function_timings": self.function_timings.copy()
        }

# Global performance stats instance
performance_stats = PerformanceStats()

def track_performance(func: Callable) -> Callable:
    """Decorator to track function performance
    
    Args:
        func: Function to track
    
    Returns:
        Wrapped function that tracks execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            performance_stats.record_timing(func.__name__, execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            performance_stats.record_timing(f"{func.__name__}_error", execution_time)
            logger.error(
                f"Error in {func.__name__}: {str(e)}. "
                f"Execution time: {execution_time:.3f}s"
            )
            raise
    return wrapper

def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics
    
    Returns:
        Dict containing current performance metrics
    """
    return performance_stats.get_stats()

def initialize_performance_monitoring(
    monitoring_interval: float = 5.0
) -> None:
    """Initialize performance monitoring
    
    Args:
        monitoring_interval: Time between measurements in seconds
    """
    performance_stats.start_monitoring(interval=monitoring_interval)
    logger.info("Performance monitoring initialized")