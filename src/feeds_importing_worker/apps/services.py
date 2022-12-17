import requests
from requests.auth import HTTPBasicAuth

from datetime import datetime
from feeds_importing_worker.config.log_conf import logger

from feeds_importing_worker.apps.importer import get_parser
from feeds_importing_worker.apps.constants import CHUNK_SIZE
from feeds_importing_worker.apps.models.models import Feed, FeedsRawData
from feeds_importing_worker.apps.models.provider import FeedProvider, FeedRawDataProvider, IndicatorProvider


class FeedService:
    def __init__(self):
        self.indicator_provider = IndicatorProvider()
        self.feed_raw_data_provider = FeedRawDataProvider()

    def _download_raw_data(self, feed: Feed):
        auth = None

        # TODO: implement token auth
        if feed.auth_type == 'basic':
            auth = HTTPBasicAuth(feed.auth_login, feed.auth_pass)

        with requests.get(feed.url, auth=auth, stream=True) as r:
            r.raise_for_status()

            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                yield chunk

    def update_raw_data(self, feed: Feed):
        logger.info(f'Start download feed {feed.provider} - {feed.title}...')

        feed_provider = FeedProvider()
        now = datetime.now()
        chunk_num = 1

        for chunk in self._download_raw_data(feed):
            feed_raw_data = FeedsRawData(
                feed_id=feed.id,
                filename=feed.title,
                content=chunk,
                chunk=chunk_num,
                created_at=now
            )

            chunk_num += 1

            self.feed_raw_data_provider.add(feed_raw_data)

        try:
            self.feed_raw_data_provider.session.commit()
        except Exception as e:
            self.feed_raw_data_provider.session.rollback()
            raise e
        else:
            feed_provider.clear_old_data(feed, now)
            feed_provider.session.commit()
        finally:
            feed_provider.session.close()

    def parse(self, feed: Feed):
        logger.info(f'Start parsing feed {feed.provider} - {feed.title}...')

        parser = get_parser(feed.format)
        new_indicators = parser.get_indicators(feed.raw_content)

        for new_indicator in new_indicators:
            indicator = self.indicator_provider.get_by_value_type(new_indicator.value, new_indicator.ioc_type)

            if indicator:
                if feed not in indicator.feeds:
                    indicator.feeds.append(self.indicator_provider.session.merge(feed))
            else:
                indicator = new_indicator
                indicator.feeds = [self.indicator_provider.session.merge(feed)]

            self.indicator_provider.add(indicator)
            self.indicator_provider.session.flush()

        try:
            self.indicator_provider.session.commit()
        except Exception as e:
            self.indicator_provider.session.rollback()
            raise e
        finally:
            self.indicator_provider.session.close()
