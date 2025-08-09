import os
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    app_name: str = "roary_visualizer"
) -> Dict[str, Any]:
    """Configure application logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        app_name: Name of the application for log file naming
        
    Returns:
        Dict containing logger configuration
    """
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"{app_name}_{timestamp}.log"
    
    # Configure logging format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Configure file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10_485_760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure application logger
    app_logger = logging.getLogger(app_name)
    app_logger.setLevel(log_level)
    
    # Create performance logger with separate file
    perf_log_file = log_dir / f"{app_name}_performance_{timestamp}.log"
    perf_handler = logging.handlers.RotatingFileHandler(
        perf_log_file,
        maxBytes=10_485_760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    perf_handler.setFormatter(log_format)
    
    perf_logger = logging.getLogger(f"{app_name}.performance")
    perf_logger.setLevel(log_level)
    perf_logger.addHandler(perf_handler)
    
    return {
        "log_level": log_level,
        "log_dir": str(log_dir),
        "app_log_file": str(log_file),
        "perf_log_file": str(perf_log_file),
        "log_format": log_format
    }

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None):
    """Log an error with context information
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    logger.error(f"Error occurred: {error_info}", exc_info=True)

def configure_streamlit_logging():
    """Configure Streamlit-specific logging"""
    import streamlit as st
    
    class StreamlitHandler(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.ERROR:
                st.error(self.format(record))
            elif record.levelno >= logging.WARNING:
                st.warning(self.format(record))
            elif record.levelno >= logging.INFO:
                st.info(self.format(record))
            else:
                st.debug(self.format(record))
    
    streamlit_handler = StreamlitHandler()
    streamlit_handler.setFormatter(
        logging.Formatter("%(levelname)s - %(message)s")
    )
    
    st_logger = logging.getLogger("streamlit")
    st_logger.addHandler(streamlit_handler)
    st_logger.setLevel(logging.INFO)