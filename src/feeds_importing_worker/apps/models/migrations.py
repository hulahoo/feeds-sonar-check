"""Migrations functions"""

from feeds_importing_worker.apps.models.base import (
    SyncPostgresDriver,
    metadata,
)
from feeds_importing_worker.config.log_conf import logger


def create_migrations() -> None:
    """Create migrations for Database"""

    logger.info("Start executing migrations...")
    metadata.create_all(SyncPostgresDriver().engine)
    logger.info("Migrations applied successfully")
