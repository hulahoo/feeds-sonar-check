from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.apps.models.base import SyncPostgresDriver, metadata


def create_migrations():
    logger.info("Start executing migrations...")
    metadata.create_all(SyncPostgresDriver().engine)
