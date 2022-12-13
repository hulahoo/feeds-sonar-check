from dagster import job, repository, ScheduleDefinition

from apps.services import FeedService
from apps.models.provider import FeedProvider
from apps.models.models import Feed


feed_service = FeedService()
feed_provider = FeedProvider()


def update_feed_raw_data(feed: Feed):
    @job(name=feed.provider)
    def fn():
        feed_service.update_raw_data(feed)
        feed_service.parse(feed)

    return fn


@repository
def feeds_repository():
    feeds = feed_provider.get_all()

    jobs = []

    for feed in feeds:
        jobs.append(
            ScheduleDefinition(job=update_feed_raw_data(feed), cron_schedule=feed.polling_frequency)
        )

    return jobs