import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name="SecurePresence", log_file="app.log", level=logging.INFO):
    """
    Sets up a thread-safe logger with console and file output.
    Uses RotatingFileHandler to manage log size.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding handlers multiple times
    if logger.hasHandlers():
        return logger

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    try:
        # Ensure log directory exists, saving right alongside the main script or in a logs dir
        # For this setup we will just put it in the current working directory for simplicity
        # or properly in a 'logs' folder if we had one. Let's assume cwd is root or use a relative path.
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

    return logger

# Singleton instance to be used across the app
logger = setup_logger()
