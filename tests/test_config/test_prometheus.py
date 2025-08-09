import pytest
from unittest.mock import patch, MagicMock
import time
from roary_visualizer.config.monitoring.prometheus import (
    initialize_metrics,
    track_request_count,
    track_request_latency,
    track_file_processing,
    update_memory_usage,
    update_cpu_usage,
    update_active_users,
    record_error,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    FILE_PROCESSING_TIME,
    MEMORY_USAGE,
    CPU_USAGE,
    ACTIVE_USERS,
    ERROR_COUNT
)

@patch('prometheus_client.start_http_server')
def test_initialize_metrics(mock_start_server):
    """Test metrics server initialization"""
    initialize_metrics(port=9090)
    mock_start_server.assert_called_once_with(9090)

def test_track_request_count():
    """Test request count tracking"""
    @track_request_count(endpoint="/test")
    def test_endpoint():
        return "test"
    
    # Get initial count
    initial_count = REQUEST_COUNT.labels(endpoint="/test")._value.get()
    
    # Call endpoint
    test_endpoint()
    
    # Check count increased
    assert REQUEST_COUNT.labels(endpoint="/test")._value.get() == initial_count + 1

def test_track_request_latency():
    """Test request latency tracking"""
    @track_request_latency(endpoint="/test")
    def slow_endpoint():
        time.sleep(0.1)
        return "test"
    
    # Call endpoint
    slow_endpoint()
    
    # Check latency was recorded
    assert REQUEST_LATENCY.labels(endpoint="/test")._sum.get() > 0

def test_track_file_processing():
    """Test file processing time tracking"""
    @track_file_processing(file_type="csv")
    def process_file():
        time.sleep(0.1)
        return "processed"
    
    # Call processing function
    process_file()
    
    # Check processing time was recorded
    assert FILE_PROCESSING_TIME.labels(file_type="csv")._sum.get() > 0

def test_update_memory_usage():
    """Test memory usage update"""
    update_memory_usage(1024.0)
    assert MEMORY_USAGE._value.get() == 1024.0

def test_update_cpu_usage():
    """Test CPU usage update"""
    update_cpu_usage(50.0)
    assert CPU_USAGE._value.get() == 50.0

def test_update_active_users():
    """Test active users update"""
    update_active_users(10)
    assert ACTIVE_USERS._value.get() == 10

def test_record_error():
    """Test error recording"""
    initial_count = ERROR_COUNT.labels(type="validation")._value.get()
    record_error("validation")
    assert ERROR_COUNT.labels(type="validation")._value.get() == initial_count + 1

def test_decorator_chaining():
    """Test multiple metric decorators can be chained"""
    @track_request_count(endpoint="/test")
    @track_request_latency(endpoint="/test")
    def test_endpoint():
        time.sleep(0.1)
        return "test"
    
    initial_count = REQUEST_COUNT.labels(endpoint="/test")._value.get()
    test_endpoint()
    
    assert REQUEST_COUNT.labels(endpoint="/test")._value.get() == initial_count + 1
    assert REQUEST_LATENCY.labels(endpoint="/test")._sum.get() > 0