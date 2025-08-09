import pytest
import os
from unittest.mock import patch
from roary_visualizer.config.performance.config import (
    PerformanceManager,
    CacheConfig,
    PerformanceConfig,
    MemoryConfig
)

@pytest.fixture
def performance_manager():
    """Create PerformanceManager instance for testing"""
    return PerformanceManager()

def test_cache_config_defaults():
    """Test cache configuration default values"""
    config = CacheConfig()
    assert config.enable_cache is True
    assert config.ttl_seconds == 300
    assert config.max_size == 128

def test_performance_config_defaults():
    """Test performance configuration default values"""
    config = PerformanceConfig()
    assert config.max_workers == 4
    assert config.chunk_size == 1000
    assert config.timeout_seconds == 30
    assert config.batch_size == 5000

def test_memory_config_defaults():
    """Test memory configuration default values"""
    config = MemoryConfig()
    assert config.max_memory_mb == 1024
    assert config.gc_threshold == 0.8
    assert config.enable_monitoring is True

def test_load_cache_config_from_env():
    """Test loading cache configuration from environment variables"""
    with patch.dict(os.environ, {
        'ENABLE_CACHE': 'false',
        'CACHE_TTL_SECONDS': '600',
        'CACHE_MAX_SIZE': '256'
    }):
        manager = PerformanceManager()
        config = manager.cache_config
        
        assert config.enable_cache is False
        assert config.ttl_seconds == 600
        assert config.max_size == 256

def test_load_performance_config_from_env():
    """Test loading performance configuration from environment variables"""
    with patch.dict(os.environ, {
        'MAX_WORKERS': '8',
        'CHUNK_SIZE': '2000',
        'TIMEOUT_SECONDS': '60',
        'BATCH_SIZE': '10000'
    }):
        manager = PerformanceManager()
        config = manager.performance_config
        
        assert config.max_workers == 8
        assert config.chunk_size == 2000
        assert config.timeout_seconds == 60
        assert config.batch_size == 10000

def test_load_memory_config_from_env():
    """Test loading memory configuration from environment variables"""
    with patch.dict(os.environ, {
        'MAX_MEMORY_MB': '2048',
        'GC_THRESHOLD': '0.9',
        'ENABLE_MEMORY_MONITORING': 'false'
    }):
        manager = PerformanceManager()
        config = manager.memory_config
        
        assert config.max_memory_mb == 2048
        assert config.gc_threshold == 0.9
        assert config.enable_monitoring is False

def test_get_cache_key(performance_manager):
    """Test cache key generation"""
    # Test with different argument combinations
    key1 = performance_manager.get_cache_key("arg1", "arg2", kwarg1="val1")
    key2 = performance_manager.get_cache_key("arg1", "arg2", kwarg1="val1")
    key3 = performance_manager.get_cache_key("arg1", "arg2", kwarg1="val2")
    
    # Same arguments should produce same key
    assert key1 == key2
    # Different arguments should produce different keys
    assert key1 != key3

def test_should_cache(performance_manager):
    """Test cache decision logic"""
    # Test with small data size (should cache)
    small_size = 1024 * 1024  # 1MB
    assert performance_manager.should_cache(small_size) is True
    
    # Test with large data size (should not cache)
    large_size = 2 * 1024 * 1024 * 1024  # 2GB
    assert performance_manager.should_cache(large_size) is False
    
    # Test with cache disabled
    with patch.dict(os.environ, {'ENABLE_CACHE': 'false'}):
        manager = PerformanceManager()
        assert manager.should_cache(small_size) is False

def test_get_batch_size(performance_manager):
    """Test batch size calculation"""
    # Test with small data size
    small_size = 1000
    assert performance_manager.get_batch_size(small_size) == small_size
    
    # Test with large data size
    large_size = 20000
    batch_size = performance_manager.get_batch_size(large_size)
    assert batch_size <= large_size
    assert batch_size > 0

def test_get_worker_config(performance_manager):
    """Test worker configuration"""
    config = performance_manager.get_worker_config()
    
    assert isinstance(config, dict)
    assert 'max_workers' in config
    assert 'chunk_size' in config
    assert 'timeout' in config
    assert config['max_workers'] == performance_manager.performance_config.max_workers
    assert config['chunk_size'] == performance_manager.performance_config.chunk_size
    assert config['timeout'] == performance_manager.performance_config.timeout_seconds