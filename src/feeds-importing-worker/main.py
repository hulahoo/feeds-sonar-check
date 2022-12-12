from dagster import job, repository, ScheduleDefinition

from apps.services import FeedService
from apps.models.provider import FeedProvider
from apps.models.models import Feed


def update_feed_raw_data(feed: Feed):
    @job(name=feed.provider)
    def fn():
        FeedService().update_raw_data(feed)

    return fn


@repository
def feeds_repository():
    feeds = FeedProvider().get_all()

    jobs = []

    for feed in feeds:
        jobs.append(
            ScheduleDefinition(job=update_feed_raw_data(feed), cron_schedule=feed.polling_frequency)
        )

    return jobs
