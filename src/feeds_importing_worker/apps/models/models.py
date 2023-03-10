from datetime import datetime

from sqlalchemy import event, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, BYTEA, UUID
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, UniqueConstraint,
    BigInteger,  DECIMAL, text, ForeignKey
)

from feeds_importing_worker.apps.models.abstract import IDBase, TimestampBase


class FeedRawData(IDBase, TimestampBase):
    __tablename__ = "feeds_raw_data"

    feed_id = Column(BigInteger, ForeignKey('feeds.id'), nullable=True)  # NOSONAR

    filename = Column(String(128))
    content = Column(BYTEA)
    chunk = Column(Integer)


class Feed(IDBase, TimestampBase):
    __tablename__ = "feeds"

    title = Column(String(128))
    provider = Column(String(128))
    description = Column(String(255))
    format = Column(String(8))
    url = Column(String(128))
    auth_type = Column(String(16))
    auth_api_token = Column(String(255))
    auth_login = Column(String(32))
    auth_pass = Column(String(32))
    certificate = Column(BYTEA)
    is_use_taxii = Column(Boolean, default=False)
    polling_frequency = Column(String(32))
    weight = Column(DECIMAL())
    available_fields = Column(JSONB)
    parsing_rules = Column(JSONB)
    status = Column(String(32))
    is_active = Column(Boolean, default=True)
    is_truncating = Column(Boolean, default=True)
    max_records_count = Column(DECIMAL)
    updated_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(BigInteger)

    data = relationship(FeedRawData, order_by=FeedRawData.chunk, lazy='joined')

    @property
    def raw_content(self):
        pending = None

        for data in self.data:
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

    def __eq__(self, other):
        return self.id == other.id


class IndicatorFeedRelationship(IDBase, TimestampBase):
    __tablename__ = "indicator_feed_relationships"
    indicator_id = Column(UUID(as_uuid=True), ForeignKey('indicators.id'), nullable=True)
    feed_id = Column(BigInteger, ForeignKey('feeds.id'), nullable=True)
    deleted_at = Column(DateTime)


class Indicator(TimestampBase):
    __tablename__ = "indicators"

    id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    ioc_type = Column(String(32))
    value = Column(String(1024))
    context = Column(JSONB)
    is_sending_to_detections = Column(Boolean, default=True)
    is_false_positive = Column(Boolean, default=False)
    weight = Column(DECIMAL)
    feeds_weight = Column(DECIMAL)
    time_weight = Column(DECIMAL)
    tags_weight = Column(DECIMAL)
    is_archived = Column(Boolean, default=False)
    false_detected_counter = Column(BigInteger)
    positive_detected_counter = Column(BigInteger)
    total_detected_counter = Column(BigInteger)
    first_detected_at = Column(DateTime)
    last_detected_at = Column(DateTime)
    created_by = Column(BigInteger)
    updated_at = Column(DateTime, default=func.now())

    feeds = relationship(
        Feed,
        backref='indicators',
        secondary='indicator_feed_relationships',
        primaryjoin=(IndicatorFeedRelationship.indicator_id == id and not IndicatorFeedRelationship.deleted_at),
        lazy='joined'
    )

    UniqueConstraint(value, ioc_type, name='indicators_unique_value_type')


class IndicatorActivity(IDBase, TimestampBase):
    __tablename__ = "indicator_activities"

    indicator_id = Column(UUID(as_uuid=True))
    activity_type = Column(String(32))
    details = Column(JSONB)
    created_by = Column(BigInteger, nullable=True)


class Process(IDBase):
    __tablename__ = "processes"
    parent_id = Column(BigInteger, ForeignKey('processes.id'), nullable=True)
    service_name = Column(String(64))
    title = Column(String(128))
    name = Column(String(128))
    request = Column(JSONB)
    result = Column(JSONB)
    status = Column(String(32))
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    children = relationship('Process')


class AuditLog(IDBase, TimestampBase):
    __tablename__ = "audit_logs"
    service_name = Column(String(128))
    user_id = Column(BigInteger)
    event_type = Column(String(128))
    object_type = Column(String(128))
    object_name = Column(String(128))
    description = Column(String(256))
    prev_value = Column(JSONB)
    new_value = Column(JSONB)
    context = Column(JSONB)


class PlatformSetting(IDBase, TimestampBase):
    __tablename__ = "platform_settings"
    key = Column(String(128))
    value = Column(JSONB)
    updated_at = Column(DateTime)


@event.listens_for(Feed, 'before_update')
def receive_before_update(mapper, connection, target: Feed):
    target.updated_at = datetime.now()


@event.listens_for(Indicator, 'before_update')
def receive_before_update(mapper, connection, target: Indicator):
    target.updated_at = datetime.now()
