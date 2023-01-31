"""Main file for running the service"""

import subprocess
import os
from threading import Thread

from feeds_importing_worker.config.config import settings
from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.web.routers.api import execute as flask_app
from feeds_importing_worker.apps.models.base import metadata


os.environ['DAGSTER_HOME'] = settings.app.dagster_home
path = os.path.dirname(os.path.abspath(__file__))

metadata.drop_all(tables=[metadata.tables['_jobs']])
metadata.create_all(tables=[metadata.tables['_jobs']])


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
