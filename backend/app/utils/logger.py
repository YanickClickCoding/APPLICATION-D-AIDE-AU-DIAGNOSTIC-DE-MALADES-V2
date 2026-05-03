"""
Logging configuration
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Configure le système de logging
    """
    # Format des logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Ajouter file handler si spécifié
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    # Configuration
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    # Logger pour SQLAlchemy (moins verbeux)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Logging configuré - Niveau: {log_level}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger avec le nom spécifié
    """
    return logging.getLogger(name)
