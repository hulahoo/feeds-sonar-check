from dagster import (
    job,
    op,
    repository,
    ScheduleDefinition,
    DefaultScheduleStatus,
    DagsterInstance
)
from datetime import datetime

from feeds_importing_worker.apps.models.models import Feed
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.provider import FeedProvider, ProcessProvider
from feeds_importing_worker.apps.enums import JobStatus

from feeds_importing_worker.config.log_conf import logger


feed_service = FeedService()
feed_provider = FeedProvider()
process_provider = ProcessProvider()


def update_feed(feed: Feed):
    @op(name=feed.provider + '_op')
    def op_fn():
        feed_service.update_raw_data(feed)
        feed_service.parse(feed)

    @job(name=feed.provider)
    def process_fn():
        op_fn()

    return process_fn


@job(name='check_jobs')
def check_jobs():
    if process_provider.get_all_by_statuses([JobStatus.IN_PROGRESS]):
        return

    pending_processes = process_provider.get_all_by_statuses([JobStatus.PENDING])

    for process in pending_processes:
        feed = feed_provider.get_by_id(process.request['feed-id'])

        if not feed:
            process.status = JobStatus.FAILED
            process_provider.update(process)

            continue

        process.started_at = datetime.now()
        process.status = JobStatus.IN_PROGRESS
        process_provider.update(process)

        try:
            update_feed(feed).execute_in_process(instance=DagsterInstance.get())
        except Exception as e:
            logger.warning(f'Unable to create job for feed {feed.id}: {e}')
            process.status = JobStatus.FAILED
            process_provider.update(process)
        else:
            process.finished_at = datetime.now()
            process.status = JobStatus.DONE
            process_provider.update(process)

        break


@repository
def feeds_repository():
    feeds = feed_provider.get_all()

    processes = []

    for feed in feeds:
        try:
            job = ScheduleDefinition(
                job=update_feed(feed),
                cron_schedule=feed.polling_frequency,
                default_status=DefaultScheduleStatus.STOPPED
            )
        except Exception as e:
            logger.warning(f'Unable to create job for feed {feed.id}: {e}')

        else:
            processes.append(job)

    processes.append(
        ScheduleDefinition(
            job=check_jobs,
            cron_schedule='* * * * *',
            default_status=DefaultScheduleStatus.RUNNING
        )
    )

    return processes
