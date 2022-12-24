"""Main file for running the service"""

import subprocess
import os
from threading import Thread

from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.web.routers.api import execute as flask_app


def start_worker():
    path = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(['dagit', '-f', f'{path}/worker.py'], check=True)


def execute() -> None:
    """
    Run the service.

    1. Create migrations;
    2. Run Flask thread;
    3. Run Worker thread.
    """
    worker_thread: Thread = Thread(target=start_worker)
    flask_thread: Thread = Thread(target=flask_app)

    logger.info("Start Flask...")
    flask_thread.start()

    logger.info("Start Dagit...")
    worker_thread.start()
