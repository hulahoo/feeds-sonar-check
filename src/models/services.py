from src.models.models import Feed, Indicator, Source
from src.models.provider import FeedProvider, IndicatorProvider, SourceProvider


def create_feed(*, data_to_create_with: dict) -> Feed:
    return FeedProvider().create(data_to_create=data_to_create_with)


def save_feed(feed: Feed):
    return FeedProvider().save(feed=feed)


def get_feed(*, feed_name: str) -> Feed:
    return FeedProvider().read(feed_name=feed_name)


def delete_feed(*, feed_name: str):
    return FeedProvider().delete(feed_name=feed_name)


def get_source() -> list:
    return SourceProvider().read()


def get_source_by(fields: dict) -> Source:
    return SourceProvider().read_by_values(**fields)


def save_indicator(indicator: Indicator):
    return IndicatorProvider.save(indicator=indicator)


def add_feed_to_indicator(indicator, feed_data) -> Indicator:
    return IndicatorProvider().load_feed_relationship(
        indicator=indicator,
        data_to_create=feed_data
    )


def get_or_create(model, values: dict, defaults: dict = None):
    if isinstance(model, Indicator):
        provider = IndicatorProvider()
    else:
        return
    if defaults is not None:
        values = {**defaults, **values}
    instance = provider.read_by_values(**values)
    if instance:
        return instance
    else:
        instance = provider.create(**values)
        return instance
