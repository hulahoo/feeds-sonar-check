from flask import Flask, request
from flask_wtf.csrf import CSRFProtect
from requests.exceptions import RequestException

from feeds_importing_worker.config.log_conf import logger
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from feeds_importing_worker.apps.models.provider import FeedProvider, JobProvider
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.models import Feed, Job
from feeds_importing_worker.apps.enums import WorkerJobStatus


app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

mimetype = 'application/json'

feed_service = FeedService()
feed_provider = FeedProvider()
job_provider = JobProvider()


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
    feeds = feed_provider.get_all()

    for feed in feeds:
        job_provider.add(Job(
            feed_id=feed.id,
            status=WorkerJobStatus.PENDING
        ))

    result = []

    for job in job_provider.get_all():
        result.append(f'{job.status} - {job.feed.provider}: {job.feed.title}')

    return app.response_class(
        response='\n'.join(result),
        status=200,
        content_type=CONTENT_TYPE_LATEST
    )


@app.route('/api/preview', methods=["GET"])
def preview():
    PREVIEW_MAX_LINES = 50

    try:
        preview = feed_service.get_preview(Feed(
            url=request.args.get('url'),
            auth_type=request.args.get('auth_type', None),
            auth_login=request.args.get('auth_login', None),
            auth_pass=request.args.get('auth_pass', None),
        ))
    except RequestException as e:
        logger.warning(f'Unable to get feed preview: {e}')

        return app.response_class(
            response=f'Preview unavailable',
            status=200,
            content_type=CONTENT_TYPE_LATEST
        )
    else:
        result = []

        for _ in range(PREVIEW_MAX_LINES):
            try:
                result.append(next(preview))
            except StopIteration:
                break

    return app.response_class(
        response='\n'.join(result),
        status=200,
        mimetype='text/plain',
        content_type=CONTENT_TYPE_LATEST
    )
