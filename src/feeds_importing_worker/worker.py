from dagster import (
    job,
    op,
    repository,
    ScheduleDefinition,
    DefaultScheduleStatus,
)
from datetime import datetime

from feeds_importing_worker.apps.models.models import Feed, Process
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.provider import FeedProvider, ProcessProvider, JobProvider
from feeds_importing_worker.apps.constants import SERVICE_NAME
from feeds_importing_worker.apps.enums import JobStatus, WorkerJobStatus


feed_service = FeedService()
feed_provider = FeedProvider()
process_provider = ProcessProvider()
job_provider = JobProvider()


def update_feed(feed: Feed):
    @op(name=feed.provider + '_op')
    def op_fn():
        process = Process(
            service_name=SERVICE_NAME,
            title=f'{feed.provider} - {feed.title}',
            started_at=datetime.now(),
            status=JobStatus.IN_PROGRESS
        )

        process_provider.add(process)

        feed_service.update_raw_data(feed)
        result = feed_service.parse(feed)
        feed_service.soft_delete_indicators_without_feeds()
        process.status = JobStatus.SUCCESS
        process.result = result
        process.finished_at = datetime.now()
        process_provider.update(process)

    @job(name=feed.provider)
    def process_fn():
        op_fn()

    return process_fn


@job(name='check_jobs')
def check_jobs():
    job_provider.delete(status=WorkerJobStatus.FINISHED)

    if job_provider.get_all(status=WorkerJobStatus.RUNNING):
        return

    jobs = job_provider.get_all(status=WorkerJobStatus.PENDING)

    for job in jobs:
        job.status = WorkerJobStatus.RUNNING
        job_provider.update(job)

        update_feed(job.feed).execute_in_process()

        job.status = WorkerJobStatus.FINISHED
        job_provider.update(job)

        break


@repository
def feeds_repository():
    feeds = feed_provider.get_all()

    processes = []

    for feed in feeds:
        processes.append(
            ScheduleDefinition(
                job=update_feed(feed),
                cron_schedule=feed.polling_frequency,
                default_status=DefaultScheduleStatus.STOPPED
            )
        )

    processes.append(
        ScheduleDefinition(
            job=check_jobs,
            cron_schedule='* * * * *',
            default_status=DefaultScheduleStatus.RUNNING
        )
    )

    return processes
