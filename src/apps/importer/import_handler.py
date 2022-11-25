import random

import requests
from dagster import DynamicOut, DynamicOutput, job, op, repository, schedule

from src.apps.importer.services import choose_type
from src.models.models import Feed
from src.models.services import get_source, get_source_by

PATTERN = "%Y-%m-%d"


def download(path: str, limit) -> list:
    text = requests.get(path).text
    return text


@op(out=DynamicOut())
def get_sources():
    sources = get_source()
    for index, obj in enumerate(sources):
        yield DynamicOutput(value=(index, obj.id), mapping_key=f'{index}'.replace('.', '_'))


@op
def op_source_downloads_worker(context, data):

    _, obj = data
    fields = {'id': obj}
    obj = get_source_by(fields=fields)

    feed_raw = {"feed": {
        "link": obj.path,
        "confidence": random.randint(0, 1000000),
        "source_id": obj.id,
        "format_of_feed": obj.format,
        "name": obj.name
    },

        "raw_indicators": obj.raw_indicators,
        "config": {
            "limit": obj.max_rows,
            "is_instead_full": obj.is_instead_full
    }
    }
    feed = Feed(**feed_raw["feed"])

    method = choose_type(obj.format.lower())
    config = feed_raw.get('config', {})
    result = method(feed, feed_raw['raw_indicators'], config)

    return len(result)


@op
def end_worker(context, data):
    return len(data)


@job
def job_time_worker():
    # op_time_worker()

    partitions = get_sources().map(op_source_downloads_worker)
    end_worker(partitions.collect())


@schedule(
    cron_schedule="0 2 * * *",
    job=job_time_worker,
    execution_timezone="Europe/Moscow",
)
def scheduler_time_worker(context):
    date = context.scheduled_execution_time.strftime(PATTERN)
    return {"ops": {"op_time_worker": {"config": {"date": date}}}}


@repository
def repos():
    return [scheduler_time_worker, job_time_worker]
