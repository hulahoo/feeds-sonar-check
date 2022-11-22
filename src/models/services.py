from src.models.models import Feed
from src.models.provider import FeedProvider


def create_feed(*, data_to_create_with: dict) -> Feed:
    return FeedProvider().create(data_to_create=data_to_create_with)


def delete_feed(*, feed_name: str):
    return FeedProvider().delete(feed_name=feed_name)
