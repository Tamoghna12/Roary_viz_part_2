import pytest
import time
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.roary_visualizer.config.performance.monitoring import (
    PerformanceStats,
    track_performance,
    get_performance_stats,
    initialize_performance_monitoring
)
from roary_visualizer.config.performance.monitoring import (
    PerformanceMonitor,
    PerformanceMetrics
)

@pytest.fixture
def performance_monitor():
    """Create PerformanceMonitor instance for testing"""
    return PerformanceMonitor()

def test_performance_metrics_creation():
    """Test PerformanceMetrics dataclass creation"""
    now = datetime.now()
    metrics = PerformanceMetrics(
        execution_time=1.5,
        memory_usage=100.0,
        cpu_usage=50.0,
        timestamp=now
    )
    
    assert metrics.execution_time == 1.5
    assert metrics.memory_usage == 100.0
    assert metrics.cpu_usage == 50.0
    assert metrics.timestamp == now

def test_monitor_decorator(performance_monitor):
    """Test monitor decorator functionality"""
    @performance_monitor.monitor()
    def test_function():
        time.sleep(0.1)
        return "test"
    
    # Execute monitored function
    result = test_function()
    
    assert result == "test"
    metrics = performance_monitor.get_metrics("test_function")
    assert len(metrics) == 1
    assert "test_function" in metrics
    assert metrics["test_function"].execution_time >= 0.1
    assert metrics["test_function"].memory_usage >= 0
    assert metrics["test_function"].cpu_usage >= 0

def test_monitor_with_name(performance_monitor):
    """Test monitor decorator with custom name"""
    @performance_monitor.monitor(name="custom_name")
    def test_function():
        return "test"
    
    test_function()
    
    metrics = performance_monitor.get_metrics("custom_name")
    assert len(metrics) == 1
    assert "custom_name" in metrics

def test_get_memory_usage(performance_monitor):
    """Test memory usage measurement"""
    memory_usage = performance_monitor.get_memory_usage()
    assert isinstance(memory_usage, float)
    assert memory_usage >= 0

def test_get_cpu_usage(performance_monitor):
    """Test CPU usage measurement"""
    cpu_usage = performance_monitor.get_cpu_usage()
    assert isinstance(cpu_usage, float)
    assert 0 <= cpu_usage <= 100

def test_get_metrics_filtering(performance_monitor):
    """Test metrics filtering by name"""
    @performance_monitor.monitor(name="test1")
    def function1():
        pass
    
    @performance_monitor.monitor(name="test2")
    def function2():
        pass
    
    function1()
    function2()
    
    # Get specific metrics
    metrics1 = performance_monitor.get_metrics("test1")
    assert len(metrics1) == 1
    assert "test1" in metrics1
    
    # Get all metrics
    all_metrics = performance_monitor.get_metrics()
    assert len(all_metrics) == 2
    assert "test1" in all_metrics
    assert "test2" in all_metrics

def test_reset_metrics(performance_monitor):
    """Test metrics reset functionality"""
    @performance_monitor.monitor()
    def test_function():
        pass
    
    test_function()
    assert len(performance_monitor.get_metrics()) == 1
    
    performance_monitor.reset_metrics()
    assert len(performance_monitor.get_metrics()) == 0

def test_check_resource_limits(performance_monitor):
    """Test resource limits checking"""
    limits = performance_monitor.check_resource_limits()
    
    assert isinstance(limits, dict)
    expected_keys = {
        'max_rss',
        'user_time',
        'system_time',
        'page_faults',
        'io_operations',
        'voluntary_context_switches',
        'involuntary_context_switches'
    }
    assert all(key in limits for key in expected_keys)
    assert all(isinstance(value, (int, float)) for value in limits.values())

def test_memory_usage_error_handling():
    """Test error handling in memory usage measurement"""
    monitor = PerformanceMonitor()
    with patch.object(monitor.process, 'memory_info', side_effect=Exception("Test error")):
        memory_usage = monitor.get_memory_usage()
        assert memory_usage == 0.0

def test_cpu_usage_error_handling():
    """Test error handling in CPU usage measurement"""
    monitor = PerformanceMonitor()
    with patch.object(monitor.process, 'cpu_percent', side_effect=Exception("Test error")):
        cpu_usage = monitor.get_cpu_usage()
        assert cpu_usage == 0.0

def test_resource_limits_error_handling():
    """Test error handling in resource limits checking"""
    monitor = PerformanceMonitor()
    with patch('resource.getrusage', side_effect=Exception("Test error")):
        limits = monitor.check_resource_limits()
        assert limits == {}

def test_performance_stats_initialization():
    stats = PerformanceStats()
    assert stats.memory_usage == 0.0
    assert stats.cpu_usage == 0.0
    assert stats.active_users == 0
    assert isinstance(stats.function_timings, dict)
    assert len(stats.function_timings) == 0

def test_performance_monitoring_start_stop():
    stats = PerformanceStats()
    stats.start_monitoring(interval=1.0)
    assert stats._monitor_thread is not None
    assert stats._monitor_thread.is_alive()
    
    # Let it run briefly
    time.sleep(2.0)
    
    # Check that metrics are being collected
    assert stats.memory_usage > 0
    assert stats.cpu_usage >= 0
    
    stats.stop_monitoring()
    assert not stats._monitor_thread.is_alive()

def test_record_timing():
    stats = PerformanceStats()
    stats.record_timing("test_function", 1.5)
    assert "test_function" in stats.function_timings
    assert stats.function_timings["test_function"] == 1.5

def test_update_active_users():
    stats = PerformanceStats()
    stats.update_active_users(10)
    assert stats.active_users == 10

def test_get_stats():
    stats = PerformanceStats()
    stats.memory_usage = 1024 * 1024  # 1MB
    stats.cpu_usage = 50.0
    stats.active_users = 5
    stats.record_timing("test_function", 1.5)
    
    current_stats = stats.get_stats()
    assert current_stats["memory_usage_mb"] == 1.0
    assert current_stats["cpu_usage_percent"] == 50.0
    assert current_stats["active_users"] == 5
    assert current_stats["function_timings"]["test_function"] == 1.5

@pytest.mark.asyncio
async def test_track_performance_decorator():
    @track_performance
    async def test_function():
        await asyncio.sleep(0.1)
        return "test"
    
    result = await test_function()
    assert result == "test"
    
    stats = get_performance_stats()
    assert "test_function" in stats["function_timings"]
    assert stats["function_timings"]["test_function"] > 0

def test_initialize_performance_monitoring():
    initialize_performance_monitoring(monitoring_interval=1.0)
    time.sleep(2.0)  # Let it collect some data
    
    stats = get_performance_stats()
    assert stats["memory_usage_mb"] > 0
    assert stats["cpu_usage_percent"] >= 0