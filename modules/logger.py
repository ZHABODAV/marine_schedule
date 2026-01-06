import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from .config import config

def setup_logger(name: str, log_dir: str = 'logs') -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Args:
        name: Logger name (typically __name__ of the module)
        log_dir: Directory to store log files
    
    Returns:
        Configured logger instance
    """
    # Get config settings
    log_level_str = config.get('logging.level', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    log_to_console = config.get('logging.console', True)
    log_filename = config.get('logging.file', 'app.log')
    
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all, handlers filter
    
    # Remove existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_format = logging.Formatter(
            '[%(levelname)s] %(name)s: %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    # File handler (DEBUG and above) - rotating
    # Use configured filename prefix or default
    base_name = Path(log_filename).stem
    log_file = log_path / f'{base_name}_{datetime.now().strftime("%Y%m%d")}.log'
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Error file handler (ERROR and above only)
    error_log_file = log_path / f'errors_{datetime.now().strftime("%Y%m%d")}.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    logger.addHandler(error_handler)
    
    return logger
