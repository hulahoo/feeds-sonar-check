from typing import Optional, List
from datetime import datetime

from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.apps.models.base import SyncPostgresDriver
from feeds_importing_worker.apps.models.models import (
    Feed, FeedRawData, Indicator, Process, IndicatorFeedRelationship
)
from feeds_importing_worker.apps.enums import JobStatus
from feeds_importing_worker.apps.constants import SERVICE_NAME


class BaseProvider:
    def __init__(self):
        self.session = SyncPostgresDriver().session()


class FeedProvider(BaseProvider):
    def update(self, feed: Feed):
        with SyncPostgresDriver().session() as session:
            session.add(session.merge(feed))
            session.commit()

    def get_by_id(self, id_: int):
        with SyncPostgresDriver().session() as session:
            query = session.query(Feed).filter(Feed.id == id_)

            return query.one_or_none()

    def get_all(self, is_active=True):
        with SyncPostgresDriver().session() as session:
            query = session.query(Feed).filter(Feed.is_active == is_active)

            return query.all()

    def clear_old_data(self, feed: Feed, clear_before: datetime):
        with SyncPostgresDriver().session() as session:
            query = session.query(FeedRawData).filter(
                FeedRawData.created_at < clear_before
            ).filter(
                FeedRawData.feed_id == feed.id
            )
            query.delete()
            session.commit()


class FeedRawDataProvider(BaseProvider):
    def add(self, feed_raw_data: FeedRawData):
        with SyncPostgresDriver().session() as session:
            session.add(feed_raw_data)
            session.flush()
            session.commit()


class IndicatorProvider(BaseProvider):
    def add(self, indicator: Indicator):
        with SyncPostgresDriver().session() as session:
            session.add(indicator)

    def get_by_value_type(self, value: str, type: str) -> Optional[Indicator]:
        with SyncPostgresDriver().session() as session:
            query = session.query(Indicator).filter(Indicator.ioc_type == type).filter(
                Indicator.value == value)
            return query.one_or_none()

    def get_indicators_without_feeds(self) -> Optional[Indicator]:
        with SyncPostgresDriver().session() as session:
            query = session.query(Indicator).filter(
                ~Indicator.id.in_(session.query(IndicatorFeedRelationship.indicator_id).filter(
                    IndicatorFeedRelationship.deleted_at == None)))

            result = query.all()
            logger.debug(f'get_indicators_without_feeds - len result - {len(result)}')

            return result

    def get_id_set_for_feeds_current_indicators(self, feed: Feed):
        logger.debug(f"feed id - {feed.id}")
        with SyncPostgresDriver().session() as session:
            query = session.query(
                IndicatorFeedRelationship.indicator_id
            ).filter(
                IndicatorFeedRelationship.feed_id == feed.id
            ).filter(
                IndicatorFeedRelationship.deleted_at == None
            )

            return [str(item.indicator_id) for item in query.all()]

    def soft_delete_relations(self, indicators_id):
        logger.debug(f"Total count of relations for deleting - {len(indicators_id)}")
        now = datetime.now()
        with SyncPostgresDriver().session() as session:
            for indicator_id in indicators_id:
                feed_relation = session.query(IndicatorFeedRelationship).filter(
                    IndicatorFeedRelationship.indicator_id == indicator_id).first()
                feed_relation.deleted_at = now
            session.commit()


class ProcessProvider(BaseProvider):
    def add(self, process: Process):
        with SyncPostgresDriver().session() as session:
            current_process = session.query(Process).filter(
                Process.service_name == SERVICE_NAME
            ).filter(
                Process.name == process.name
            ).filter(
                Process.status.in_([JobStatus.IN_PROGRESS, JobStatus.PENDING])
            ).count()

            if not current_process:
                session.add(process)
                session.commit()

    def update(self, process: Process):
        with SyncPostgresDriver().session() as session:
            logger.info(f"Process to update: {process.id}")
            session.add(process)
            session.commit()

    def delete(self, status: str):
        with SyncPostgresDriver().session() as session:
            session.query(Process).filter(
                Process.service_name == SERVICE_NAME
            ).filter(
                Process.status == status
            ).delete()

            session.commit()

    def get_all_by_statuses(self, statuses: List[str]):
        with SyncPostgresDriver().session() as session:
            query = session.query(Process).filter(
                Process.service_name == SERVICE_NAME
            ).filter(
                Process.status.in_(statuses)
            )

            return query.all()
