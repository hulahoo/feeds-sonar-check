"""Main file for running the service"""

import subprocess
from threading import Thread

from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.apps.models.migrations import create_migrations
from feeds_importing_worker.web.routers.api import execute as flask_app


def start_worker():
    subprocess.run(["dagit", "-f", "feeds_importing_worker/worker.py"], check=True)



def execute() -> None:
    """Run the service.

    1. Create migrations;
    2. Run Flask thread;
    3. Run Worker thread.
    """
    create_migrations()
    logger.info("Start Flask...")
    # remove later
    # worker_thread: Thread = Thread(target=start_worker)
    flask_thread: Thread = Thread(target=flask_app)

    flask_thread.start()
    # worker_thread.start()
