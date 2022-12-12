from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text, Boolean
)

from src.models.abstract import IDBase, TimestampBase


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
    polling_frequency = Column(Boolean)
    weight = Column(Integer)
    parsing_rules = Column(JSONB)
    is_active = Column(Boolean)
    updated_at = Column(DateTime)


class FeedRawData(IDBase, TimestampBase):
    __tablename__ = "feed_raw_data"

    feed_id = Column(Integer, ForeignKey("feed.id"))

    filename = Column(String(128))
    content = Column(Text)
    chunk = Column(Integer)
