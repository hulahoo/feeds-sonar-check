from dagster import job, repository, ScheduleDefinition, op, DefaultScheduleStatus
from datetime import datetime

from feeds_importing_worker.apps.models.models import Feed, Process
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.provider import FeedProvider, ProcessProvider
from feeds_importing_worker.apps.constants import SERVICE_NAME
from feeds_importing_worker.apps.enums import JobStatus


feed_service = FeedService()
feed_provider = FeedProvider()
process_provider = ProcessProvider()


def update_feed(feed: Feed):
    @op(name=feed.provider + '_op')
    def op_fn():
        process_ = Process(
            service_name=SERVICE_NAME,
            title=f'{feed.provider} - {feed.title}',
            started_at=datetime.now(),
            status=JobStatus.IN_PROGRESS
        )

        process_provider.add(process_)

        feed_service.update_raw_data(feed)
        result = feed_service.parse(feed)
        feed_service.soft_delete_indicators_without_feeds()
        process_.status = JobStatus.SUCCESS
        process_.result = result
        process_.finished_at = datetime.now()
        process_provider.update(process_)

    @job(name=feed.provider)
    def process_fn():
        op_fn()

    return process_fn


@repository
def feeds_repository():
    feeds = feed_provider.get_all()

    processes = []

    for feed in feeds:
        processes.append(
            ScheduleDefinition(
                job=update_feed(feed),
                cron_schedule=feed.polling_frequency,
                default_status=DefaultScheduleStatus.RUNNING
            )
        )

    return processes
