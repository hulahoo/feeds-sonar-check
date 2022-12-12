from src.models.migrations import create_migrations

from src.services import FeedService

# create_migrations()

FeedService().update_raw_data()