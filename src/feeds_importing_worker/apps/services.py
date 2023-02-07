import requests

from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from datetime import datetime

from feeds_importing_worker.config.log_conf import logger

from feeds_importing_worker.apps.importer import get_parser, IParser
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

        if feed.auth_type == 'basic':
            auth = HTTPBasicAuth(feed.auth_login, feed.auth_pass)
        if feed.auth_type == 'token':
            raise NotImplementedError('Not implemented auth type - token')

        with requests.get(feed.url, auth=auth, stream=True) as r:
            r.raise_for_status()

            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                yield chunk

    def get_preview(self, feed: Feed):
        for chunk in self._download_raw_data(feed):
            feed.data.append(FeedRawData(content=chunk, chunk=1))

            return feed.raw_content

    def update_raw_data(self, feed: Feed):
        logger.info(f'Start download feed {feed.provider} - {feed.title}...')

        now = datetime.now()
        chunk_num = 1

        try:
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
        except RequestException as e:
            logger.error(f'Failed to update feed data: {e}')
            return

        try:
            self.feed_raw_data_provider.session.commit()
        except Exception as e:
            logger.debug('Error occurred during in process commit data')
            self.feed_raw_data_provider.session.rollback()
            raise e
        else:
            self.feed_provider.clear_old_data(feed, now)
            self.feed_provider.session.commit()
        finally:
            self.feed_provider.session.close()
            self.feed_raw_data_provider.session.close()

    def parse(self, feed: Feed):
        logger.info(f'Start parsing feed {feed.provider} - {feed.title}...')
        feed.status = FeedStatus.LOADING

        logger.debug('Start to update feed provider')
        self.feed_provider.update(feed)
        logger.debug('Feed provider updated')

        now = datetime.now()
        parser: IParser = get_parser(feed.format)

        logger.debug('Start to get indicators')

        new_indicators = parser.get_indicators(feed.raw_content, feed.parsing_rules)

        old_indicators_id_list = self.indicator_provider.get_id_set_for_feeds_current_indicators(feed)
        len_old = 0
        logger.info(f"Old indicators: {old_indicators_id_list}")

        if old_indicators_id_list:
            len_old = len(old_indicators_id_list)
            logger.debug(f'Len if old ind list - {len(old_indicators_id_list)}')
            logger.debug(f'first elem - {old_indicators_id_list[0]}')

        result = {
            'feed': f'{feed.provider} - {feed.title}',
            'indicators-processed': 0
        }

        logger.debug(f"result = {result}")

        try:
            for count, new_indicator in enumerate(new_indicators):
                logger.info(f"Count: {count} for indicator: {new_indicator}")
                self.process_indicator(count, new_indicator, feed, now, old_indicators_id_list, result)

                if (
                        feed.is_truncating
                        and feed.max_records_count
                        and result['indicators-processed'] >= feed.max_records_count
                ):
                    logger.debug(f'Feed is truncated to {feed.max_records_count}')
                    break
        except Exception as e:
            logger.warning(f'Unable to parse content for feed {feed.id} \n {e}')
            result['status'] = FeedStatus.FAILED
            return result

        try:
            if old_indicators_id_list:
                logger.info("Soft deleting old indicators")
                self.indicator_provider.soft_delete_relations(old_indicators_id_list)

            self.indicator_provider.session.commit()
        except Exception as e:
            logger.debug('Error occurred during commit data')
            self.indicator_provider.session.rollback()
            feed.status = FeedStatus.FAILED

            raise e
        else:
            logger.debug('All fine')
            feed.status = FeedStatus.NORMAL
        finally:
            logger.info("Closing session")
            self.indicator_provider.session.close()

            self.feed_provider.update(feed)
            self.feed_provider.session.close()

        logger.debug(f"result = {result}")
        logger.debug(f"Len of old_indicators_id_list - {len_old}, new len after work- {len(old_indicators_id_list)}")

        return result

    def process_indicator(self, count, new_indicator, feed, now, old_indicators_id_list, result):
        if count % 200 == 0:
            logger.debug(f'count - {count}')
            logger.debug(f'Indicator info: value -{new_indicator.value}, ioc_type - {new_indicator.ioc_type}')
        indicator = self.indicator_provider.get_by_value_type(new_indicator.value, new_indicator.ioc_type)
        logger.info(f"Retrieved existed indicator: {indicator} with value: {new_indicator.value} and type: {new_indicator.ioc_type}")

        if indicator:
            if feed not in indicator.feeds:
                logger.debug(f'Append feed to indicator')
                indicator.feeds.append(self.indicator_provider.session.merge(feed))
                indicator.is_archived = False
                indicator.updated_at = now
            if indicator.id in old_indicators_id_list:
                logger.info("Retrieved indicator found in old indicator list. Remove it from old ind. list")
                old_indicators_id_list.remove(indicator.id)
        else:
            logger.info("Creating new indicator")
            indicator = new_indicator
            indicator.updated_at = now

            indicator.feeds = [self.indicator_provider.session.merge(feed)]

        self.indicator_provider.add(indicator)
        self.indicator_provider.session.flush()

        result['indicators-processed'] += 1

        if count % 400 == 0:
            try:
                logger.info("Max batch size reached. Commiting indicators")
                self.indicator_provider.session.commit()
            except Exception as e:
                self.indicator_provider.session.rollback()

                logger.debug(f'Error occurred during in process commit data \n {e}')

                feed.status = FeedStatus.FAILED
                self.feed_provider.update(feed)
            finally:
                self.feed_provider.session.close()
                self.indicator_provider.session.close()

    def soft_delete_indicators_without_feeds(self):
        logger.info(f'Start soft deleting for indicators without feeds')
        indicators = self.indicator_provider.get_indicators_without_feeds()
        logger.debug('Indicators without feeds fetched')

        now = datetime.now()

        result = {
            'indicators-processed': 0
        }

        if indicators:
            logger.debug('There are few indicators feeds relations to be deleted')

            for count, indicator in enumerate(indicators):
                result['indicators-processed'] += 1
                indicator.is_archived = True
                indicator.updated_at = now
                self.indicator_provider.add(indicator)
                self.indicator_provider.session.flush()

            try:
                self.indicator_provider.session.commit()
            except Exception as e:
                self.indicator_provider.session.rollback()
                logger.debug(f'Error occurred during commit data \n {e}')
            finally:
                self.indicator_provider.session.close()
                logger.debug('All fine')

        logger.debug(f'Result: {result}')
        return result
