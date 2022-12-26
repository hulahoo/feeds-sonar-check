from typing import Optional
from datetime import datetime
from sqlalchemy import and_

from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.apps.models.base import SyncPostgresDriver
from feeds_importing_worker.apps.models.models import Feed, FeedRawData, Indicator, Process, IndicatorFeedRelationship


class BaseProvider:
    def __init__(self):
        self.session = SyncPostgresDriver().session()


class FeedProvider(BaseProvider):
    def update(self, feed: Feed):
        self.session.add(self.session.merge(feed))
        self.session.commit()

    def get_all(self, is_active=True):
        query = self.session.query(Feed).filter(Feed.is_active == is_active)

        return query.all()

    def clear_old_data(self, feed: Feed, clear_before: datetime):
        query = self.session.query(FeedRawData).filter(
            FeedRawData.created_at < clear_before
        ).filter(
            FeedRawData.feed_id == feed.id
        )

        query.delete()


class FeedRawDataProvider(BaseProvider):
    def add(self, feed_raw_data: FeedRawData):
        self.session.add(feed_raw_data)

    def get_feed_data_content(self, feed: Feed):
        query = self.session.query(FeedRawData.content).filter(
            FeedRawData.feed_id == feed.id
        ).order_by(FeedRawData.chunk)
        return query.all()


class IndicatorProvider(BaseProvider):
    def add(self, indicator: Indicator):
        self.session.add(indicator)

    def get_by_value_type(self, value: str, type: str) -> Optional[Indicator]:
        query = self.session.query(Indicator).filter(Indicator.ioc_type == type).filter(
            Indicator.value == value)
        return query.one_or_none()

    def get_indicators_without_feeds(self) -> Optional[Indicator]:
        query = self.session.query(Indicator).join(IndicatorFeedRelationship,
                                                   IndicatorFeedRelationship.indicator_id == Indicator.id, isouter=True)
        return query.all()


class ProcessProvider(BaseProvider):
    def add(self, process: Process):
        self.session.add(process)
        self.session.commit()

    def update(self, process: Process):
        logger.info(f"Process to update: {process.id}")
        self.session.add(process)
        self.session.commit()
