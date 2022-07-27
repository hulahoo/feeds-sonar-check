import random

from django.test import TestCase

from intelhandler.models import Feed
from intelhandler.script import parse_stix, parse_csv, parse_misp, parse_free_text, parse_custom_json


def randoms():
    return random.randint(0, 1000000)


class ServicesTestCase(TestCase):
    def setUp(self):
        self.feed_template = {"feed": {
            "link": '',
            "confidence": randoms(),
            "name": f"name{randoms()}"

        },
            "raw_indicators": {"name": f"unique_name_{randoms()}"}
        }

    @staticmethod
    def create_feed(feed, link):
        feed['feed']['link'] = link
        obj = Feed(**feed['feed'])
        return obj, feed['raw_indicators']

    def test_stix(self):
        link = 'https://raw.githubusercontent.com/davidonzo/Threat-Intel/4cbb51faf707a11da4258ed402f585ac5c330f3b/stix2/34d0015a5622c3a14174e7a8bb5cc51d.json'

        params = ServicesTestCase.create_feed(self.feed_template, link)
        result = parse_stix(*params)
        self.assertEqual(type(result).__name__, 'list')

    def test_misp(self):
        link = "http://www.botvrij.eu/data/feed-osint/0319b483-5973-4932-91ea-5a44c2975b24.json"
        params = ServicesTestCase.create_feed(self.feed_template, link)

        result = parse_misp(*params)
        self.assertEqual(type(result).__name__, 'list')

    def test_free_text(self):
        link = 'https://cybercrime-tracker.net/all.php'

        feed = self.feed_template
        feed['format_of_feed'] = 'TXT'
        feed['raw_indicators'] = f'test_name{randoms()}'

        params = ServicesTestCase.create_feed(feed, link)
        result = parse_free_text(*params)
        self.assertEqual(type(result).__name__, 'list')

    def test_csv(self):
        link = 'https://home.nuug.no/~peter/pop3gropers.txt'

        feed = self.feed_template
        feed['raw_indicators'] = f'test_name{randoms()}'

        params = ServicesTestCase.create_feed(self.feed_template, link)
        result = parse_csv(*params)
        self.assertEqual(type(result).__name__, 'list')

    def test_custom_json(self):
        link = "https://raw.githubusercontent.com/Lookingglass/opentpx/master/examples/tpx/valid/tpx2-2-example-collections-nc.json"

        params = ServicesTestCase.create_feed(self.feed_template, link)
        result = parse_custom_json(*params)
        self.assertEqual(type(result).__name__, 'list')