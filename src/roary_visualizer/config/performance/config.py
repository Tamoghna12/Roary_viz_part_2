import os
from dataclasses import dataclass
from typing import Dict, Any
from functools import lru_cache

@dataclass
class CacheConfig:
    """Cache configuration settings"""
    enable_cache: bool = True
    ttl_seconds: int = 300  # 5 minutes
    max_size: int = 128  # Maximum number of items in cache

@dataclass
class PerformanceConfig:
    """Performance configuration settings"""
    max_workers: int = 4
    chunk_size: int = 1000
    timeout_seconds: int = 30
    batch_size: int = 5000

@dataclass
class MemoryConfig:
    """Memory management configuration"""
    max_memory_mb: int = 1024  # 1GB
    gc_threshold: float = 0.8  # Trigger garbage collection at 80% usage
    enable_monitoring: bool = True

class PerformanceManager:
    """Manages application performance settings"""
    
    def __init__(self):
        """Initialize performance manager"""
        self.cache_config = self._load_cache_config()
        self.performance_config = self._load_performance_config()
        self.memory_config = self._load_memory_config()
    
    @staticmethod
    def _load_cache_config() -> CacheConfig:
        """Load cache configuration from environment"""
        return CacheConfig(
            enable_cache=os.getenv('ENABLE_CACHE', 'true').lower() == 'true',
            ttl_seconds=int(os.getenv('CACHE_TTL_SECONDS', '300')),
            max_size=int(os.getenv('CACHE_MAX_SIZE', '128'))
        )
    
    @staticmethod
    def _load_performance_config() -> PerformanceConfig:
        """Load performance configuration from environment"""
        return PerformanceConfig(
            max_workers=int(os.getenv('MAX_WORKERS', '4')),
            chunk_size=int(os.getenv('CHUNK_SIZE', '1000')),
            timeout_seconds=int(os.getenv('TIMEOUT_SECONDS', '30')),
            batch_size=int(os.getenv('BATCH_SIZE', '5000'))
        )
    
    @staticmethod
    def _load_memory_config() -> MemoryConfig:
        """Load memory configuration from environment"""
        return MemoryConfig(
            max_memory_mb=int(os.getenv('MAX_MEMORY_MB', '1024')),
            gc_threshold=float(os.getenv('GC_THRESHOLD', '0.8')),
            enable_monitoring=os.getenv('ENABLE_MEMORY_MONITORING', 'true').lower() == 'true'
        )
    
    @lru_cache(maxsize=1)
    def get_cache_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from arguments
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            str: Cache key
        """
        # Convert args and kwargs to a string representation
        args_str = ':'.join(str(arg) for arg in args)
        kwargs_str = ':'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{args_str}:{kwargs_str}"
    
    def should_cache(self, data_size: int) -> bool:
        """Check if data should be cached based on size
        
        Args:
            data_size: Size of data in bytes
            
        Returns:
            bool: True if data should be cached
        """
        if not self.cache_config.enable_cache:
            return False
        
        # Convert max_memory to bytes for comparison
        max_cache_size = self.memory_config.max_memory_mb * 1024 * 1024
        return data_size <= max_cache_size * self.memory_config.gc_threshold
    
    def get_batch_size(self, total_size: int) -> int:
        """Calculate optimal batch size based on data size
        
        Args:
            total_size: Total size of data to process
            
        Returns:
            int: Optimal batch size
        """
        if total_size <= self.performance_config.batch_size:
            return total_size
        
        # Calculate number of batches needed
        num_batches = (total_size + self.performance_config.batch_size - 1) // self.performance_config.batch_size
        return (total_size + num_batches - 1) // num_batches
    
    def get_worker_config(self) -> Dict[str, Any]:
        """Get worker configuration
        
        Returns:
            Dict[str, Any]: Worker configuration dictionary
        """
        return {
            'max_workers': self.performance_config.max_workers,
            'chunk_size': self.performance_config.chunk_size,
            'timeout': self.performance_config.timeout_seconds
        }

# Create global instance
performance_manager = PerformanceManager()