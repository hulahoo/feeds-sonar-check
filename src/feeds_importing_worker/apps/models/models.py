from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text, Boolean, UniqueConstraint
)

from feeds_importing_worker.apps.models.abstract import IDBase, TimestampBase


class FeedRawData(IDBase, TimestampBase):
    __tablename__ = "feed_raw_data"

    feed_id = Column(Integer, ForeignKey("feed.id"))

    filename = Column(String(128))
    content = Column(BYTEA)
    chunk = Column(Integer)


class Feed(IDBase, TimestampBase):
    __tablename__ = "feed"

    title = Column(String(128))
    provider = Column(String(128))
    format = Column(String(8))
    url = Column(String(128))
    auth_type = Column(String(16))
    auth_api_token = Column(Text)
    auth_login = Column(String(32))
    auth_pass = Column(String(32))
    certificate = Column(Text)
    use_taxii = Column(Boolean)
    polling_frequency = Column(String(32))
    weight = Column(Integer)
    parsing_rules = Column(JSONB)
    is_active = Column(Boolean)
    updated_at = Column(DateTime)

    data = relationship(FeedRawData, order_by=FeedRawData.chunk)

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


class Indicator(IDBase, TimestampBase):
    __tablename__ = "indicator"

    ioc_type = Column(String(16))
    value = Column(String(256))
    context = Column(JSONB)
    is_sending_to_detections = Column(Boolean, default=True)
    is_false_positive = Column(Boolean, default=False)
    ioc_weight = Column(Integer)
    tags_weight = Column(Integer)
    is_archived = Column(Boolean, default=False)
    false_detected_counter = Column(Integer)
    positive_detected_counter = Column(Integer)
    total_detected_counter = Column(Integer)
    first_detected_at = Column(DateTime)
    last_detected_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)

    feeds = relationship(Feed, backref='indicators', secondary='indicator_feed_relationships')

    UniqueConstraint(value, ioc_type, name='indicator_unique_value_type')


class IndicatorFeedRelationships(IDBase, TimestampBase):
    __tablename__ = "indicator_feed_relationships"
    indicator_id = Column(Integer, ForeignKey("indicator.id"))
    feed_id = Column(Integer, ForeignKey("feed.id"))
    deleted_at = Column(DateTime)
