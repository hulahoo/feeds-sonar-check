import requests

from datetime import datetime

from apps.models.provider import FeedProvider, FeedRawDataProvider
from apps.models.models import Feed, FeedRawData
from apps.constants import CHUNK_SIZE


class FeedService:
    def _download_raw_data(self, url: str):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()

            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                yield chunk

    def update_raw_data(self, feed: Feed):
        feed_raw_data_provider = FeedRawDataProvider()
        feed_provider = FeedProvider()
        now = datetime.now()
        chunk_num = 1

        for chunk in self._download_raw_data(feed.url):
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
            feed_raw_data_provider.session.commit()
        except Exception as e:
            feed_raw_data_provider.session.rollback()
            raise e
        else:
            feed_provider.clear_old_data(feed, now)
            feed_provider.session.commit()
        finally:
            feed_provider.session.close()
