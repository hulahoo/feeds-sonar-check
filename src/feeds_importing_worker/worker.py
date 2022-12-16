import subprocess

from dagster import job, repository, ScheduleDefinition, op

from feeds_importing_worker.apps.models.models import Feed
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.provider import FeedProvider


feed_service = FeedService()
feed_provider = FeedProvider()


def update_feed(feed: Feed):
    @op(name=feed.provider + '_op')
    def op_fn():
        feed_service.update_raw_data(feed)
        feed_service.parse(feed)

    @job(name=feed.provider)
    def job_fn():
        op_fn()

    return job_fn


@repository
def feeds_repository():
    feeds = feed_provider.get_all()

    jobs = []

    for feed in feeds:
        jobs.append(
            ScheduleDefinition(
                job=update_feed(feed),
                cron_schedule=feed.polling_frequency,
            )
        )

    return jobs


def start_worker():
    subprocess.run(["dagit", "-f", "src/feeds_importing_worker/worker.py"])
