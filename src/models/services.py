from src.models.models import Feed
from src.models.provider import FeedProvider, SourceProvider, IndicatorProvider


def create_feed(*, data_to_create_with: dict) -> Feed:
    return FeedProvider().create(data_to_create=data_to_create_with)


def delete_feed(*, feed_name: str):
    return FeedProvider().delete(feed_name=feed_name)


def get_source() -> list:
    return SourceProvider().read()


def get_or_create(provider: IndicatorProvider, **kwargs):
    instance = provider.read_by_value(**kwargs)
    if instance:
        return instance
    else:
        instance = provider.create(**kwargs)
        return instance
