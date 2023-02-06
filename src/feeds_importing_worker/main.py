"""Main file for running the service"""

import subprocess
import os
import shutil

from threading import Thread

from feeds_importing_worker.config.config import settings
from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.web.routers.api import execute as flask_app
from feeds_importing_worker.apps.models.provider import ProcessProvider
from feeds_importing_worker.apps.enums import JobStatus


path = os.path.dirname(os.path.abspath(__file__))
os.environ['DAGSTER_HOME'] = settings.app.dagster_home


def init_dagster_config():
    if os.path.exists(settings.app.dagster_home):
        shutil.rmtree(settings.app.dagster_home)

    os.makedirs(settings.app.dagster_home)

    shutil.copy(settings.app.config_path, settings.app.dagster_home)

    ProcessProvider().delete(status=JobStatus.IN_PROGRESS)


def start_dagit():
    subprocess.run(['dagit', '-f', f'{path}/worker.py'], check=True)


def start_dagster():
    subprocess.run(['dagster-daemon', 'run', '-f', f'{path}/worker.py'], check=True)


def execute() -> None:
    """
    Run the service.

    1. Create migrations;
    2. Run Flask thread;
    3. Run Worker thread.
    """
    init_dagster_config()

    worker_thread: Thread = Thread(target=start_dagit)
    flask_thread: Thread = Thread(target=flask_app)
    daemon_thread: Thread = Thread(target=start_dagster)

    logger.info("Start Flask...")
    flask_thread.start()

    logger.info("Start Dagster...")
    daemon_thread.start()

    if settings.app.dagit_enabled:
        logger.info("Start Dagit...")
        worker_thread.start()
