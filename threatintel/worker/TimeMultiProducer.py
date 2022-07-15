from typing import List

from dagster import op, schedule, job, repository, Field, get_dagster_logger
from dagster.config import config_schema

from worker.utils import django_init

PATTERN = "%Y-%m-%d"


@op(config_schema={'data_lst': Field(list, default_value=[])})
def op_time_producer(context):
    django_init()
    from worker.MultiProducer import MultiProducer

    data_lst = context.op_config['data_lst']
    if data_lst is None:
        data_lst = []
    print(data_lst)
    logger = get_dagster_logger()
    logger.info(str(data_lst))
    MultiProducer.send_list_of_data(data_lst)


@job
def job_time_producer():
    op_time_producer()


@schedule(
    cron_schedule="0 2 * * *",
    job=job_time_producer,
    execution_timezone="Europe/Moscow",
)
def scheduler_time_producer(context):
    date = context.scheduled_execution_time.strftime(PATTERN)
    return {"ops": {"op_time_producer": {"config": {"date": date}}}}


@repository
def repos():
    return [scheduler_time_producer, job_time_producer]
