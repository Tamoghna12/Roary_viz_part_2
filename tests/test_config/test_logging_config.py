import os
import logging
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from roary_visualizer.config.logging.config import (
    setup_logging,
    get_logger,
    log_error,
    configure_streamlit_logging
)

@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_setup_logging(temp_log_dir):
    """Test logging setup configuration"""
    config = setup_logging(
        log_level="DEBUG",
        log_dir=temp_log_dir,
        app_name="test_app"
    )
    
    assert config["log_level"] == logging.DEBUG
    assert config["log_dir"] == temp_log_dir
    assert Path(config["app_log_file"]).exists()
    assert Path(config["perf_log_file"]).exists()

def test_get_logger():
    """Test logger retrieval"""
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"

def test_log_error():
    """Test error logging functionality"""
    logger = logging.getLogger("test_error_logger")
    logger.setLevel(logging.ERROR)
    
    mock_handler = MagicMock()
    logger.addHandler(mock_handler)
    
    test_error = ValueError("Test error")
    test_context = {"test_key": "test_value"}
    
    log_error(logger, test_error, test_context)
    
    assert mock_handler.handle.called
    args = mock_handler.handle.call_args[0][0]
    assert "ValueError" in args.getMessage()
    assert "Test error" in args.getMessage()
    assert "test_value" in args.getMessage()

def test_invalid_log_level():
    """Test handling of invalid log level"""
    config = setup_logging(log_level="INVALID")
    assert config["log_level"] == logging.INFO

@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_log_levels(temp_log_dir, log_level):
    """Test different logging levels"""
    config = setup_logging(
        log_level=log_level,
        log_dir=temp_log_dir
    )
    expected_level = getattr(logging, log_level)
    assert config["log_level"] == expected_level

def test_log_rotation(temp_log_dir):
    """Test log file rotation"""
    config = setup_logging(log_dir=temp_log_dir)
    logger = get_logger("test_rotation")
    
    # Write enough data to trigger rotation
    large_message = "x" * 1024 * 1024  # 1MB message
    for _ in range(11):  # Write > 10MB to trigger rotation
        logger.info(large_message)
    
    log_files = list(Path(temp_log_dir).glob("*.log*"))
    assert len(log_files) > 1  # Should have main log file plus at least one backup

@patch('streamlit.error')
@patch('streamlit.warning')
@patch('streamlit.info')
@patch('streamlit.debug')
def test_streamlit_logging(mock_debug, mock_info, mock_warning, mock_error):
    """Test Streamlit-specific logging configuration"""
    configure_streamlit_logging()
    logger = logging.getLogger("streamlit")
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    mock_debug.assert_not_called()  # Debug is not enabled by default
    mock_info.assert_called_with("INFO - Info message")
    mock_warning.assert_called_with("WARNING - Warning message")
    mock_error.assert_called_with("ERROR - Error message")