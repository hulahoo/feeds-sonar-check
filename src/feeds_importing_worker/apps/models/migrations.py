"""Migrations functions"""
from sqlalchemy.engine.base import Engine
from sqlalchemy import inspect

from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.apps.models.base import SyncPostgresDriver, metadata
from feeds_importing_worker.apps.models.models import Indicators, IndicatorFeedRelationships, FeedsRawData


def create_migrations() -> None:
    """Create migrations for Database"""
    engine: Engine = SyncPostgresDriver().engine
    tables_list = [Indicators.__tablename__, IndicatorFeedRelationships.__tablename__, FeedsRawData.__tablename__]

    with SyncPostgresDriver().session() as db:
        db.execute("DROP TABLE IF EXISTS indicator CASCADE;")
        db.execute("DROP TABLE IF EXISTS feeds_raw_data CASCADE;")
        db.execute("DROP TABLE IF EXISTS feed_raw_data CASCADE;")
        db.execute("DROP TABLE IF EXISTS indicator_feed_relationships CASCADE;")
        db.flush()
        db.commit()
        logger.info("Table indicator dropped")

    if not inspect(engine).has_table("indicators"):
        Indicators.__table__.create(engine)
        tables_list.remove(Indicators.__tablename__)
        logger.info("Table Indicators created")

    if not inspect(engine).has_table("indicator_feed_relationships"):
        IndicatorFeedRelationships.__table__.create(SyncPostgresDriver().engine)
        tables_list.remove(IndicatorFeedRelationships.__tablename__)
        logger.info("Table Indicator_Feed_relationships created")

    if not inspect(engine).has_table("feeds_raw_data"):
        tables_list.remove(FeedsRawData.__tablename__)
        FeedsRawData.__table__.create(SyncPostgresDriver().engine)
        logger.info("Table FeedsRawData created")

    logger.info(f"Tables already exists: {tables_list}")
    logger.info("Migration applied successfully")
