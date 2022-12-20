from dagster import job, repository, ScheduleDefinition, op
from datetime import datetime

from feeds_importing_worker.apps.models.models import Feed, Job
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.provider import FeedProvider, JobProvider
from feeds_importing_worker.apps.constants import SERVICE_NAME


feed_service = FeedService()
feed_provider = FeedProvider()
job_provider = JobProvider()


def update_feed(feed: Feed):
    @op(name=feed.provider + '_op')
    def op_fn():
        job_ = Job(
            service_name=SERVICE_NAME,
            title=f'{feed.provider} - {feed.title}',
            started_at=datetime.now()
        )

        job_provider.add(job_)

        feed_service.update_raw_data(feed)
        feed_service.parse(feed)

        # TODO: job add status and result
        job_.finished_at = datetime.now()
        job_provider.update(job_)

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
