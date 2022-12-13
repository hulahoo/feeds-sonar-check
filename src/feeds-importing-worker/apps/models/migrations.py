from loguru import logger

from apps.models.base import SyncPostgresDriver, metadata
from apps.models.models import Indicator, IndicatorFeedRelationships


def create_migrations():
    logger.info("Start executing migrations...")
    metadata.create_all(SyncPostgresDriver().engine)
