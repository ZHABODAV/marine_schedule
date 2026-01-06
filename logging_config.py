"""
Centralized logging configuration for Maritime Voyage Planner
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_dir: str = 'logs') -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Args:
        name: Logger name (typically __name__ of the module)
        log_dir: Directory to store log files
    
    Returns:
        Configured logger instance
    """
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to prevent duplicates
    logger.handlers.clear()
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # File handler (DEBUG and above) - rotating
    log_file = log_path / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Error file handler (ERROR and above only)
    error_log_file = log_path / f'errors_{datetime.now().strftime("%Y%m%d")}.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger
