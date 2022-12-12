from loguru import logger

from src.models.base import SyncPostgresDriver, metadata
from src.models.models import Feed, FeedRawData


def create_migrations():
    logger.info("Start executing migrations...")
    metadata.create_all(SyncPostgresDriver().engine)
