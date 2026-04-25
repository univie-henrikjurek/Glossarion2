import logging
import sys
import os


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("glossarion2-dictionary")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


logger = setup_logging()