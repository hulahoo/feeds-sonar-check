from typing import Optional
from datetime import datetime

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
        feed_raw_data = query.all()

        pending = None

        for data in feed_raw_data:
            content = data.content.decode('utf-8')

            if pending is not None:
                content = pending + content

            lines = content.split('\n')

            if lines and lines[-1] and content and lines[-1][-1] == content[-1]:
                pending = lines.pop()
            else:
                pending = None

            yield from lines

        if pending is not None:
            yield pending


class IndicatorProvider(BaseProvider):
    def add(self, indicator: Indicator):
        self.session.add(indicator)

    def get_by_value_type(self, value: str, type: str) -> Optional[Indicator]:
        query = self.session.query(Indicator).filter(Indicator.ioc_type == type).filter(
            Indicator.value == value)
        return query.one_or_none()

    def get_indicators_without_feeds(self) -> Optional[Indicator]:
        query = self.session.query(Indicator).filter(
            ~Indicator.id.in_(self.session.query(IndicatorFeedRelationship.indicator_id)))

        result = query.all()
        logger.debug(f'get_indicators_without_feeds - len result - {len(result)}')

        return result

    def get_id_set_for_feeds_current_indicators(self, feed: Feed):
        query = self.session.query(IndicatorFeedRelationship.indicator_id).filter(
            IndicatorFeedRelationship.feed_id == feed.id)
        return [str(item.indicator_id) for item in query.all()]

    def delete_relations(self, indicators_id):
        logger.debug(f"Total count of relations for deleting - {len(indicators_id)}")
        for indicator_id in indicators_id:
            self.session.query(IndicatorFeedRelationship).filter(
                IndicatorFeedRelationship.indicator_id == indicator_id).delete()
        self.session.commit()


class ProcessProvider(BaseProvider):
    def add(self, process: Process):
        self.session.add(process)
        self.session.commit()

    def update(self, process: Process):
        logger.info(f"Process to update: {process.id}")
        self.session.add(process)
        self.session.commit()
