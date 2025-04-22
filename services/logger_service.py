import logging
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger (required)
        level: Optional logging level to set for this logger
        
    Returns:
        A configured logger instance
    
    Raises:
        ValueError: If name is not provided
    """
    if not name:
        raise ValueError("Logger name must be provided")
    
    logger = logging.getLogger(name)
    
    if level is not None:
        logger.setLevel(level)
        
    return logger