from datetime import datetime

from src.models.base import SyncPostgresDriver
from src.models.models import Feed, FeedRawData


class BaseProvider:
    def __init__(self):
        self.session = SyncPostgresDriver().session()


class FeedProvider(BaseProvider):
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
