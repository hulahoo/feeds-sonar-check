from dagster import job, op, schedule, repository, OpExecutionContext, ScheduleEvaluationContext, RunRequest, ScheduleDefinition

from src.services import FeedService
from src.models.provider import FeedProvider
from src.models.models import Feed


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
