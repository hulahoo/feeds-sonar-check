import os
import json

from datetime import datetime

from flask import Flask, request
from flask_wtf.csrf import CSRFProtect
from requests.exceptions import RequestException

from feeds_importing_worker.config.log_conf import logger
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from feeds_importing_worker.apps.models.provider import FeedProvider, ProcessProvider, PlatformSettingProvider
from feeds_importing_worker.apps.services import FeedService
from feeds_importing_worker.apps.models.models import Feed, Process
from feeds_importing_worker.config.config import settings
from feeds_importing_worker.apps.enums import JobStatus
from feeds_importing_worker.apps.constants import SERVICE_NAME


app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = True
app.config['WTF_CSRF_ENABLED'] = settings.app.csrf_enabled

csrf = CSRFProtect()
csrf.init_app(app)

mimetype = 'application/json'

feed_service = FeedService()
feed_provider = FeedProvider()
process_provider = ProcessProvider()
platform_setting_provider = PlatformSettingProvider()


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
        process_provider.add(Process(
            service_name=SERVICE_NAME,
            status=JobStatus.PENDING,
            name=f'import {feed.provider}: {feed.title}',
            request={
                'feed-id': feed.id,
            }
        ))

    return app.response_class(
        response={"status": "Started"},
        status=200,
        content_type=mimetype
    )

@app.route('/api/force-update/statistics', methods=["GET"])
def force_update_statistics():
    result = []

    for process in process_provider.get_all_by_statuses([JobStatus.PENDING, JobStatus.IN_PROGRESS]):
        result.append({
            "process_status": process.status,
            "process_name": process.name,
            "feed-id": process.request
        })

    return app.response_class(
        response=json.dumps(result),
        status=200,
        content_type=mimetype
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


@app.route('/api/current-frequency', methods=["POST"])
def post_current_frequency():
    data = request.get_json()

    logger.info(f"Incoming data to update: {data}")

    delay = int(data['delay'])

    platform_setting = platform_setting_provider.get()

    platform_setting.value['delay'] = delay
    platform_setting.value['last_check'] = datetime.now().isoformat()

    platform_setting_provider.update(platform_setting)

    return app.response_class(
        response=json.dumps({'delay': platform_setting.value['delay']}),
        status=200,
        content_type=mimetype
    )


@app.route('/api/current-frequency', methods=["GET"])
def get_current_frequency():
    platform_setting = platform_setting_provider.get()

    return app.response_class(
        response=json.dumps({'delay': platform_setting.value['delay']}),
        status=200,
        content_type=mimetype
    )
