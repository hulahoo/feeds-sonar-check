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
from feeds_importing_worker.apps.models.provider import FeedProvider, ProcessProvider, Process, PlatformSettingProvider
from feeds_importing_worker.apps.enums import JobStatus

from feeds_importing_worker.config.log_conf import logger


feed_service = FeedService()
feed_provider = FeedProvider()
process_provider = ProcessProvider()
platform_setting_provider = PlatformSettingProvider()


def update_feed(feed: Feed):
    @op(name=f'{feed.id}_{feed.provider}_op')
    def op_fn():
        feed_service.update_raw_data(feed.id)
        feed_service.parse(feed.id)

    @job(name=f'{feed.id}_{feed.provider}')
    def process_fn():
        op_fn()

    return process_fn


@op
def add_jobs():
    platform_setting = platform_setting_provider.get()
    logger.info(f"Platform settings: {platform_setting}")

    minutes_from_last_check = (datetime.now() - datetime.fromisoformat(platform_setting.value['last_check'])).total_seconds() // 60

    if minutes_from_last_check < int(platform_setting.value['delay']):
        # add new feeds to update queue
        feeds = feed_provider.get_new(datetime.fromisoformat(platform_setting.value['last_check']))

        if feeds:
            logger.info('Add new feeds to schedule')

            platform_setting.value['last_check'] = datetime.now().isoformat()
            platform_setting_provider.update(platform_setting)
        else:
            logger.info(
                f'Skip jobs. Waiting {int(platform_setting.value["delay"]) - minutes_from_last_check} min'
            )

    else:
        # add all feeds to update queue
        logger.info(f'Add all feeds to schedule after {platform_setting.value["delay"]} min')

        feeds = feed_provider.get_all()

        platform_setting.value['last_check'] = datetime.now().isoformat()
        platform_setting_provider.update(platform_setting)

    for feed in feeds:
        process_provider.add(Process(
            status=JobStatus.PENDING,
            name=f'import {feed.provider}: {feed.title}',
            request={
                'feed-id': feed.id,
            }
        ))


@job(name='check_jobs')
def check_jobs():
    add_jobs()

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
