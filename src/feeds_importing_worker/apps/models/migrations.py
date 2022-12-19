"""Migrations functions"""
from sqlalchemy.engine.base import Engine
from sqlalchemy import inspect

from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.apps.models.base import SyncPostgresDriver
from feeds_importing_worker.apps.models.models import Indicator, IndicatorFeedRelationship, FeedRawData


def create_migrations() -> None:
    """Create migrations for Database"""
    engine: Engine = SyncPostgresDriver().engine
    tables_list = [Indicator.__tablename__, IndicatorFeedRelationship.__tablename__, FeedRawData.__tablename__]

    if not inspect(engine).has_table("indicators"):
        Indicator.__table__.create(engine)
        tables_list.remove(Indicator.__tablename__)
        logger.info("Table Indicators created")

    if not inspect(engine).has_table("indicator_feed_relationships"):
        IndicatorFeedRelationship.__table__.create(SyncPostgresDriver().engine)
        tables_list.remove(IndicatorFeedRelationship.__tablename__)
        logger.info("Table Indicator_Feed_relationships created")

    if not inspect(engine).has_table("feeds_raw_data"):
        tables_list.remove(FeedRawData.__tablename__)
        FeedRawData.__table__.create(SyncPostgresDriver().engine)
        logger.info("Table FeedsRawData created")

    logger.info(f"Tables already exists: {tables_list}")
    logger.info("Migration applied successfully")
