from dagster import (
    job,
    op,
    sensor,
    repository,
    ScheduleDefinition,
    DefaultScheduleStatus,
    RunRequest,
    DefaultSensorStatus,
)
from datetime import datetime

from feeds_importing_worker.apps.models.models import Feed, Process
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.provider import FeedProvider, ProcessProvider
from feeds_importing_worker.apps.enums import JobStatus

from feeds_importing_worker.config.log_conf import logger


feed_service = FeedService()
feed_provider = FeedProvider()
process_provider = ProcessProvider()


def update_feed(feed: Feed):
    @op(name=f'{feed.id}_{feed.provider}_op')
    def op_fn():
        try:
            feed_service.update_raw_data(feed)
            feed_service.parse(feed)
        except Exception as e:
            logger.warning(f'Unable to process feed: {feed.id} {feed.provider} - {feed.title}\n{e}')

    @job(name=f'{feed.id}_{feed.provider}')
    def process_fn():
        op_fn()

    return process_fn


@op(config_schema={'feed_id': int, 'process_id': int})
def op_fn(context):
    process = process_provider.get_by_id(context.op_config['process_id'])

    process.started_at = datetime.now()
    process.status = JobStatus.IN_PROGRESS
    process_provider.update(process)

    feed: Feed = feed_provider.get_by_id(context.op_config['feed_id'])

    feed_service.update_raw_data(feed)
    feed_service.parse(feed)

    process.finished_at = datetime.now()
    process.status = JobStatus.DONE
    process_provider.update(process)


@job
def process_fn():
    op_fn()


@sensor(job=process_fn, default_status=DefaultSensorStatus.RUNNING, minimum_interval_seconds=60)
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

        process_provider.session.close()
        feed_provider.session.close()

        yield RunRequest(
            run_key=f'FEED: {feed.id} {datetime.now()}',
            run_config={
                'ops': {'op_fn': {'config': {'feed_id': feed.id, 'process_id': process.id}}}
            },
        )

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

    processes.append(check_jobs)

    return processes
