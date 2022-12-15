import threading

from feeds_importing_worker.config.log_conf import logger
from feeds_importing_worker.web.routers.api import app as flask_app
from feeds_importing_worker.apps.models.migrations import create_migrations
from feeds_importing_worker.worker import start_worker


def execute():
    create_migrations()
    logger.info("Migrations applied successfully")

    flask_thread = threading.Thread(target=flask_app)
    worker_thread = threading.Thread(target=start_worker)
    flask_thread.start()
    worker_thread.start()
