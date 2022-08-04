import random

import requests
from dagster import op, schedule, job, repository, Field, DynamicOutput, DynamicOut

from worker.utils import django_init

PATTERN = "%Y-%m-%d"


@op(config_schema={'data_lst': Field(list, default_value=[])})
def op_time_worker(context):
    django_init()
    # actualization()
    # from worker.MultiProducer import MultiProducer
    #
    # data_lst = context.op_config['data_lst']
    # if data_lst is None:
    #     data_lst = []
    # print(data_lst)
    # logger = get_dagster_logger()
    # logger.info(str(data_lst))
    # MultiProducer.send_list_of_data(data_lst)


def actualization():
    from intelhandler.models import Indicator
    from django.utils import timezone

    Indicator.objects.filter(ttl__date=timezone.datetime.today()).delete()


def download(path: str, limit) -> list:
    text = requests.get(path).text
    return text


@op(out=DynamicOut())
def get_sources():
    django_init()

    from intelhandler.models import Source

    for index, obj in enumerate(list(Source.objects.all())):
        yield DynamicOutput(value=(index, obj.id), mapping_key=f'{index}'.replace('.', '_'))


@op
def op_source_downloads_worker(context, data):
    print(data)

    django_init()

    print('django init')

    from intelhandler.models import Source
    from intelhandler.models import Feed
    from worker.services import choose_type

    index, obj = data
    obj: Source = Source.objects.get(id=obj)

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
