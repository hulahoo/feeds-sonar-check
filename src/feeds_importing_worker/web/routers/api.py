from flask import Flask
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

from feeds_importing_worker.config.log_conf import logger
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from feeds_importing_worker.apps.models.provider import FeedProvider, JobProvider
from feeds_importing_worker.apps.constants import SERVICE_NAME
from feeds_importing_worker.apps.enums import JobStatus
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.models import Job


app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

mimetype = 'application/json'


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


@app.route('/api/force-update', methods=["GET"])
def force_update():
    feed_service = FeedService()
    feed_provider = FeedProvider()
    job_provider = JobProvider()

    feeds = feed_provider.get_all()

    for feed in feeds:
        job_ = Job(
            service_name=SERVICE_NAME,
            title=f'{feed.provider} - {feed.title}',
            started_at=datetime.now(),
            status=JobStatus.IN_PROGRESS
        )

        job_provider.add(job_)

        feed_service.update_raw_data(feed)
        result = feed_service.parse(feed)

        job_.status = JobStatus.SUCCESS
        job_.result = result
        job_.finished_at = datetime.now()
        job_provider.update(job_)
