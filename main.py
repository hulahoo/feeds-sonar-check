from dagster import job, repository, schedule

from src.apps.importer.import_handler import (PATTERN, end_worker, get_sources,
                                              op_source_downloads_worker)


@job
def main() -> None:
    """
    Главная функция для запуска определенных сервисов в зависимости
    от аргумента при вызвове модуля
    """
    partitions = get_sources().map(op_source_downloads_worker)
    end_worker(partitions.collect())


@schedule(
    cron_schedule="0 2 * * *",
    job=main,
    execution_timezone="Europe/Moscow",
)
def scheduler_time_worker(context):
    date = context.scheduled_execution_time.strftime(PATTERN)
    return {"ops": {"op_time_worker": {"config": {"date": date}}}}


@repository
def repos():
    return [scheduler_time_worker, main]
