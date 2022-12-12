import requests

from datetime import datetime

from src.models.provider import FeedProvider, FeedRawDataProvider
from src.models.models import Feed, FeedRawData
from src.constants import CHUNK_SIZE


class FeedService:
    def download_raw_data(self, url: str):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()

            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                yield chunk

    def update_raw_data(self):
        feed_raw_data_provider = FeedRawDataProvider()
        feed_provider = FeedProvider()

        now = datetime.now()

        for feed in feed_provider.get_all():
            chunk_num = 1

            for chunk in self.download_raw_data(feed.url):
                feed_raw_data = FeedRawData(
                    feed_id=feed.id,
                    filename=feed.title,
                    content=chunk,
                    chunk=chunk_num,
                    created_at=now
                )

                chunk_num += 1

                feed_raw_data_provider.add(feed_raw_data)

            try:
                feed_raw_data_provider.commit()
            except Exception as e:
                feed_raw_data_provider.rollback()
                raise e
            else:
                feed_provider.clear_old_data(feed, now)
                feed_provider.commit()
