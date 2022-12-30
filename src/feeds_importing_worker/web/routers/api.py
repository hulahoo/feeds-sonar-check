from flask import Flask
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

from feeds_importing_worker.config.log_conf import logger
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from feeds_importing_worker.apps.models.provider import FeedProvider, ProcessProvider
from feeds_importing_worker.apps.constants import SERVICE_NAME
from feeds_importing_worker.apps.enums import JobStatus
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.models import Process


app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

mimetype = 'application/json'

feed_service = FeedService()
feed_provider = FeedProvider()
process_provider = ProcessProvider()


def execute():
    """
    Main function to start Flask application
    """
    app.run(host='0.0.0.0', port='8080')


@app.route('/health/readiness', methods=["GET"])
def readiness():
    """
    Текущее состояние готовности сервиса
    """
    logger.info("Readiness checking started")
    return app.response_class(
        response={"status": "UP"},
        status=200,
        mimetype=mimetype
    )


@app.route('/health/liveness', methods=["GET"])
def liveness():
    """
    Возвращает информацию о работоспособности сервиса
    """
    logger.info("Liveness checking started")
    return app.response_class(
        response={"status": "UP"},
        status=200,
        mimetype=mimetype
    )


@app.route('/metrics', methods=["GET"])
def metrics():
    """
    Возвращает метрики сервиса
    """
    return app.response_class(
        response=generate_latest(),
        status=200,
        mimetype='text/plain',
        content_type=CONTENT_TYPE_LATEST
    )


@app.route('/api', methods=["GET"])
def api_routes():
    return {
        "openapi:": "3.0.0",
        "info": {
            "title": "Воркер импорта фидов",
            "version": "0.0.1",
        },
        "paths": {}
        }


def _update_feeds(parent_process: Process):
    feeds = feed_provider.get_all()

    for feed in feeds:
        process = Process(
            service_name=SERVICE_NAME,
            title=f'{feed.provider} - {feed.title}',
            started_at=datetime.now(),
            status=JobStatus.IN_PROGRESS,
            parent_id=parent_process.id
        )

        process_provider.add(process)

        feed_service.update_raw_data(feed)
        result = feed_service.parse(feed)

        process.status = JobStatus.SUCCESS
        process.result = result
        process.finished_at = datetime.now()
        process_provider.update(process)


def _remove_old_relatioins(parent_process: Process):
    process = Process(
        service_name=SERVICE_NAME,
        title='remove old relations',
        started_at=datetime.now(),
        status=JobStatus.IN_PROGRESS,
        parent_id=parent_process.id
    )

    process_provider.add(process)

    feed_service.soft_delete_indicators_without_feeds()

    process.status = JobStatus.SUCCESS
    process.finished_at = datetime.now()
    process_provider.update(process)


@app.route('/api/force-update', methods=["GET"])
def force_update():
    process = Process(
        service_name=SERVICE_NAME,
        title='feeds parsing',
        started_at=datetime.now(),
        status=JobStatus.IN_PROGRESS
    )

    process_provider.add(process)

    _update_feeds(process)
    _remove_old_relatioins(process)

    process.status = JobStatus.SUCCESS
    process.finished_at = datetime.now()
    process_provider.update(process)

    return app.response_class(
        response={"status": "FINISHED"},
        status=200,
        mimetype=mimetype
    )
