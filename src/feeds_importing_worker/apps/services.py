import requests

from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from datetime import datetime

from feeds_importing_worker.config.log_conf import logger

from feeds_importing_worker.apps.importer import get_parser, IParser
from feeds_importing_worker.apps.constants import CHUNK_SIZE
from feeds_importing_worker.apps.enums import FeedStatus
from feeds_importing_worker.apps.models.models import Feed, FeedRawData, AuditLog
from feeds_importing_worker.apps.models.provider import FeedProvider, IndicatorProvider, IndicatorActivityProvider, AuditLogProvider


class FeedService:
    def __init__(self):
        self.indicator_provider = IndicatorProvider()
        self.feed_provider = FeedProvider()
        self.indicator_activity_provider = IndicatorActivityProvider()
        self.audit_log_provider = AuditLogProvider()

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

    def update_raw_data(self, feed_id: int):
        feed = self.feed_provider.get_by_id(feed_id)

        logger.info(f'Start download feed {feed.id} {feed.provider} - {feed.title}...')

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

                feed.data.append(feed_raw_data)
        except RequestException as e:
            logger.error(f'Failed to update feed data: {e}')
            return

        try:
            self.feed_provider.update(feed)
        except Exception as e:
            logger.error(f'Error occurred during commit data \n {e}')
        else:
            self.feed_provider.clear_old_data(feed, now)

    def parse(self, feed_id: int):
        feed = self.feed_provider.get_by_id(feed_id)

        logger.info(f'Start parsing feed {feed.provider} - {feed.title}...')
        feed.status = FeedStatus.LOADING

        logger.debug('Start to update feed provider')
        self.feed_provider.update(feed)
        logger.debug('Feed provider updated')

        parser: IParser = get_parser(feed.format)

        logger.debug('Start to get indicators')

        new_indicators = parser.get_indicators(feed.raw_content, feed.parsing_rules)

        old_indicators_id_list = self.indicator_provider.get_id_set_for_feeds_current_indicators(feed)

        if old_indicators_id_list:
            logger.debug(f'Len if old ind list - {len(old_indicators_id_list)}')
            logger.debug(f'first elem - {old_indicators_id_list[0]}')

        indicators_processed = 0

        try:
            for count, new_indicator in enumerate(new_indicators):
                self.process_indicator(count, new_indicator, feed, old_indicators_id_list)

                indicators_processed += 1

                if count % 100 == 0:
                    logger.info("Max batch size reached. Commiting indicators")
                    self.indicator_provider.commit()
                    self.audit_log_provider.commit()

                if (
                    feed.is_truncating
                    and feed.max_records_count
                    and indicators_processed >= feed.max_records_count
                ):
                    logger.debug(f'Feed is truncated to {feed.max_records_count}')
                    break

            self.indicator_provider.commit()
            self.audit_log_provider.commit()

        except Exception as e:
            logger.error(f'Unable to parse content for feed {feed.id} \n {e}')
            feed.status = FeedStatus.FAILED
            self.feed_provider.update(feed)

            return

        try:
            if old_indicators_id_list:
                logger.info("Soft deleting old indicators")
                self.indicator_provider.soft_delete_relations(old_indicators_id_list)

        except Exception as e:
            logger.error(f'Error occurred during commit data \n {e}')
            feed.status = FeedStatus.FAILED
        else:
            logger.debug('All fine')
            feed.status = FeedStatus.NORMAL
        finally:
            self.feed_provider.update(feed)

    def process_indicator(self, count, new_indicator, feed, old_indicators_id_list):
        if count % 200 == 0:
            logger.debug(f'count - {count}')
            logger.debug(f'Indicator info: value -{new_indicator.value}, ioc_type - {new_indicator.ioc_type}')

        indicator = self.indicator_provider.get_by_value_type(new_indicator.value, new_indicator.ioc_type)

        if indicator:
            logger.info(
                f"Retrieved existed indicator: {indicator.id} with value: {new_indicator.value} and type: {new_indicator.ioc_type}"
            )

            if feed not in indicator.feeds:
                logger.debug(f'Append feed to indicator')
                indicator.feeds.append(feed)
                indicator.is_archived = False
                self.indicator_activity_provider.create(
                    {
                        "indicator_id": indicator.id,
                        "activity_type": "Added new feeds",
                        "created_by": None,
                        "details": {"feeds": feed}
                    }
                )
            if indicator.id in old_indicators_id_list:
                logger.info("Retrieved indicator found in old indicator list. Remove it from old ind. list")
                old_indicators_id_list.remove(indicator.id)
        else:
            logger.info("Creating new indicator")
            indicator = new_indicator

            indicator.feeds = [feed]
            indicator.feeds_weight = feed.weight
            indicator.weight = feed.weight
            self.indicator_activity_provider.create(
                {
                    "indicator_id": indicator.id,
                    "activity_type": "Added feeds",
                    "created_by": None,
                    "details": {"feed": feed}
                }
            )

        self.indicator_provider.add(indicator)

        self.audit_log_provider.add(AuditLog(
            event_type='add',
            object_type='indicator',
            object_name=indicator.value,
        ))

    def soft_delete_indicators_without_feeds(self):
        logger.info(f'Start soft deleting for indicators without feeds')
        indicators = self.indicator_provider.get_indicators_without_feeds()
        logger.debug('Indicators without feeds fetched')

        result = {
            'indicators-processed': 0
        }

        if indicators:
            logger.debug('There are few indicators feeds relations to be deleted')

            for count, indicator in enumerate(indicators):
                result['indicators-processed'] += 1
                indicator.is_archived = True
                self.indicator_provider.add(indicator)
            try:
                self.indicator_provider.commit()
            except Exception as e:
                logger.error(f'Error occurred during commit data \n {e}')

        logger.debug(f'Result: {result}')
        return result
