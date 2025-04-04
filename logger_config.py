import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging():
    """Set up logging configuration for the application."""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Get current date for log file naming
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = f'logs/app_{current_date}.log'
    
    # Create logger
    logger = logging.getLogger('fred_dashboard')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatters and add to handlers
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info("Logging initialized")
    return logger
