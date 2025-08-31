"""
Logging configuration for the application
"""
import logging
from app.core.config import settings


def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


logger = setup_logging()