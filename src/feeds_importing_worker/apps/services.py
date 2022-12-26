import requests
from requests.auth import HTTPBasicAuth

from datetime import datetime
from feeds_importing_worker.config.log_conf import logger

from feeds_importing_worker.apps.importer import get_parser
from feeds_importing_worker.apps.constants import CHUNK_SIZE
from feeds_importing_worker.apps.enums import FeedStatus
from feeds_importing_worker.apps.models.models import Feed, FeedRawData
from feeds_importing_worker.apps.models.provider import FeedProvider, FeedRawDataProvider, IndicatorProvider


class FeedService:
    def __init__(self):
        self.indicator_provider = IndicatorProvider()
        self.feed_raw_data_provider = FeedRawDataProvider()
        self.feed_provider = FeedProvider()

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

        now = datetime.now()
        chunk_num = 1

        for chunk in self._download_raw_data(feed):
            feed_raw_data = FeedRawData(
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
            # TODO: add log
            self.feed_raw_data_provider.session.rollback()
            raise e
        else:
            self.feed_provider.clear_old_data(feed, now)
            self.feed_provider.session.commit()
        finally:
            self.feed_provider.session.close()

    def parse(self, feed: Feed):
        logger.info(f'Start parsing feed {feed.provider} - {feed.title}...')

        feed.status = FeedStatus.LOADING
        logger.debug('Start to update feed provider')
        self.feed_provider.update(feed)
        logger.debug('Feed provider updated')

        parser = get_parser(feed.format)
        # TODO: log broken data
        logger.debug('Start to get indicators')
        data = self.feed_raw_data_provider.get_feed_data_content(feed)
        new_indicators = parser.get_indicators(feed.raw_content, feed.parsing_rules)

        result = {
            'feed': f'{feed.provider} - {feed.title}',
            'indicators-processed': 0
        }
        logger.debug(f"result = {result}")
        count = 0
        for new_indicator in new_indicators:
            count +=1
            if count % 20 == 0:
                logger.debug(f'count - {count}')
                logger.debug(f'Indicator info: value -{new_indicator.value}, ioc_type - {new_indicator.ioc_type}')
            indicator = self.indicator_provider.get_by_value_type(new_indicator.value, new_indicator.ioc_type)

            # TODO: delete relationship
            if indicator:
                if feed not in indicator.feeds:
                    logger.debug(f'Append feed to indicator')
                    indicator.feeds.append(self.indicator_provider.session.merge(feed))
            else:
                # logger.debug(f'Create new indicator')
                indicator = new_indicator
                indicator.feeds = [self.indicator_provider.session.merge(feed)]

            self.indicator_provider.add(indicator)
            self.indicator_provider.session.flush()

            result['indicators-processed'] += 1

            if (
                feed.is_truncating
                and feed.max_records_count
                and result['indicators-processed'] >= feed.max_records_count
            ):
                logger.debug('Proceeding indicators broken')
                break
            #TODO добавить коммит на каждые 5000 записей
        try:
            self.indicator_provider.session.commit()
        except Exception as e:
            self.indicator_provider.session.rollback()
            logger.debug('Error occurred during commit data')
            feed.status = FeedStatus.FAILED
            self.feed_provider.update(feed)

            raise e
        finally:
            self.indicator_provider.session.close()
            logger.debug('All fine')
            feed.status = FeedStatus.NORMAL
            self.feed_provider.update(feed)

        return result

    def delete_indicators(self, feed: Feed):
        logger.info(f'Start soft deleting indicators for feed {feed.provider} - {feed.title}...')
        indicators = self.indicator_provider.get_indicators_without_feeds()
        logger.debug('Indicators without feeds fetched')

        now = datetime.now()

        result = {
            'feed': f'{feed.provider} - {feed.title}',
            'indicators-processed': 0
        }

        if indicators:
            logger.debug('There are indicators to be deleted')
            for indicator in indicators:
                result['indicators-processed'] += 1
                indicator.updated_at = now
                self.indicator_provider.add(indicator)
                self.indicator_provider.session.flush()

            try:
                self.indicator_provider.session.commit()
            except Exception as e:
                self.indicator_provider.session.rollback()
                logger.debug('Error occurred during commit data')
                feed.status = FeedStatus.FAILED
                raise e
            finally:
                self.indicator_provider.session.close()
                logger.debug('All fine')

        return result
