"""Migrations functions"""
from sqlalchemy.engine.base import Engine
from sqlalchemy import inspect
from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.apps.models.base import SyncPostgresDriver
from feeds_importing_worker.apps.models.models import Indicators, IndicatorFeedRelationships, FeedRawData


def create_migrations() -> None:
    """Create migrations for Database"""
    engine: Engine = SyncPostgresDriver().engine
    tables_list = [Indicators.__tablename__, IndicatorFeedRelationships.__tablename__, FeedRawData.__tablename__]

    # remove after
    with SyncPostgresDriver().session() as db:
        db.execute("DROP TABLE IF EXISTS indicators CASCADE;")
        db.flush()
        db.commit()
        logger.info("Table indicators dropped")

    if not inspect(engine).has_table("indicators"):
        Indicators.__table__.create(engine)
        tables_list.remove(Indicators.__tablename__)
        logger.info("Table Indicators created")

    if not inspect(engine).has_table("indicator_feed_relationships") and inspect(engine).has_table("feeds"):
        IndicatorFeedRelationships.__table__.create(SyncPostgresDriver().engine)
        tables_list.remove(IndicatorFeedRelationships.__tablename__)
        logger.info("Table Indicator_Feed_relationships created")

    if not inspect(engine).has_table("feeds_raw_data") and inspect(engine).has_table("feeds"):
        tables_list.remove(FeedRawData.__tablename__)
        FeedRawData.__table__.create(SyncPostgresDriver().engine)
        logger.info("Table FeedRawData created")

    logger.info(f"List of unapplied tables: {tables_list}. Waiting for other services for applying migrations")
    logger.info("Migration applied successfully")
