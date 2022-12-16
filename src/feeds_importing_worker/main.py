"""Main file for running the service"""

from threading import Thread

from feeds_importing_worker.web.routers.api import execute as flask_app
from feeds_importing_worker.worker import start_worker


def execute() -> None:
    """Run the service.

    1. Create migrations;
    2. Run Flask thread;
    3. Run Worker thread.

    """

    flask_thread: Thread = Thread(target=flask_app)
    # TODO раскомментить воркер
    # worker_thread: Thread = Thread(target=start_worker)

    flask_thread.start()
    # worker_thread.start()
