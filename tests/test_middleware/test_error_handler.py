import pytest
import time
from unittest.mock import MagicMock
import streamlit as st
from roary_visualizer.middleware.error_handler import (
    handle_errors,
    validate_input,
    validate_file_type,
    ValidationError,
    FileProcessingError
)
from roary_visualizer.middleware.performance import measure_performance, cache_data

def test_handle_errors_validation_error():
    """Test error handler with ValidationError"""
    @handle_errors
    def raise_validation_error():
        raise ValidationError("Invalid input")
    
    # Mock streamlit error function
    st.error = MagicMock()
    
    result = raise_validation_error()
    
    assert result is None
    st.error.assert_called_once()
    assert "Invalid input" in st.error.call_args[0][0]

def test_handle_errors_file_processing_error():
    """Test error handler with FileProcessingError"""
    @handle_errors
    def raise_file_error():
        raise FileProcessingError("File processing failed")
    
    st.error = MagicMock()
    
    result = raise_file_error()
    
    assert result is None
    st.error.assert_called_once()
    assert "File processing failed" in st.error.call_args[0][0]

def test_validate_input():
    """Test input validation"""
    # Test valid input
    try:
        validate_input(True, "This should not raise")
    except ValidationError:
        pytest.fail("validate_input raised ValidationError unexpectedly")
    
    # Test invalid input
    with pytest.raises(ValidationError) as exc_info:
        validate_input(False, "Test error message")
    assert str(exc_info.value) == "Test error message"

def test_validate_file_type():
    """Test file type validation"""
    allowed_extensions = {'txt', 'csv'}
    
    # Test valid file types
    try:
        validate_file_type("test.txt", allowed_extensions)
        validate_file_type("data.csv", allowed_extensions)
    except ValidationError:
        pytest.fail("validate_file_type raised ValidationError unexpectedly")
    
    # Test invalid file type
    with pytest.raises(ValidationError) as exc_info:
        validate_file_type("test.pdf", allowed_extensions)
    assert "Invalid file type" in str(exc_info.value)

def test_measure_performance():
    """Test performance monitoring decorator"""
    @measure_performance(threshold_ms=100)
    def slow_function():
        time.sleep(0.2)
        return "done"
    
    @measure_performance(threshold_ms=1000)
    def fast_function():
        return "done"
    
    # Test slow function (should log warning)
    result = slow_function()
    assert result == "done"
    
    # Test fast function (should log debug)
    result = fast_function()
    assert result == "done"

def test_cache_data():
    """Test data caching decorator"""
    call_count = 0
    
    @cache_data(ttl_seconds=1)
    def expensive_function(arg):
        nonlocal call_count
        call_count += 1
        return f"result_{arg}"
    
    # First call should execute the function
    result1 = expensive_function("test")
    assert result1 == "result_test"
    assert call_count == 1
    
    # Second call within TTL should use cached result
    result2 = expensive_function("test")
    assert result2 == "result_test"
    assert call_count == 1
    
    # Different argument should execute the function
    result3 = expensive_function("other")
    assert result3 == "result_other"
    assert call_count == 2
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Call after TTL should execute the function again
    result4 = expensive_function("test")
    assert result4 == "result_test"
    assert call_count == 3