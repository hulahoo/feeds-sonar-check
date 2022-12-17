from typing import Optional
from datetime import datetime
from sqlalchemy import and_

from feeds_importing_worker.apps.models.base import SyncPostgresDriver
from feeds_importing_worker.apps.models.models import Feed, FeedsRawData, Indicators


class BaseProvider:
    def __init__(self):
        self.session = SyncPostgresDriver().session()


class FeedProvider(BaseProvider):
    def get_all(self, is_active=True):
        query = self.session.query(Feed).filter(Feed.is_active == is_active)

        return query.all()

    def clear_old_data(self, feed: Feed, clear_before: datetime):
        query = self.session.query(FeedsRawData).filter(
            FeedsRawData.created_at < clear_before
        ).filter(
            FeedsRawData.feed_id == feed.id
        )

        query.delete()


class FeedRawDataProvider(BaseProvider):
    def add(self, feed_raw_data: FeedsRawData):
        self.session.add(feed_raw_data)


class IndicatorProvider(BaseProvider):
    def add(self, indicator: Indicators):
        self.session.add(indicator)

    def get_by_value_type(self, value: str, type: str) -> Optional[Indicators]:
        query = self.session.query(Indicators).filter(
            and_(
                Indicators.value == value,
                Indicators.ioc_type == type
            )
        )

        return query.one_or_none()
