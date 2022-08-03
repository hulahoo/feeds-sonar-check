import json
import random
from typing import List

from kafka import KafkaProducer

from intelhandler.constants import STIX
from worker.utils import django_init

django_init()
from django.conf import settings
from intelhandler.script import parse_stix, parse_misp, parse_free_text, parse_csv
from intelhandler.models import Feed, Indicator, Source
from intelhandler.serializers import IndicatorWithFeedsSerializer


if __name__ == '__main__':
    django_init()
    print(Feed.get_model_fields())


    # Source.objects.all().delete()
    # Source.objects.create(name="test_source",
    #                       provider_name='provider',
    #                       path='https://raw.githubusercontent.com/davidonzo/Threat-Intel/4cbb51faf707a11da4258ed402f585ac5c330f3b/stix2/34d0015a5622c3a14174e7a8bb5cc51d.json',
    #                       format=STIX
    #                       )

    # d=Indicator.get_models_fields_with_lookup_expr()
    # a=Indicator.objects.prefetch_related('feeds')
    # a = Indicator.objects.filter().prefetch_related('feeds')
    # ser = IndicatorWithFeedsSerializer(a,many=True)
    # d = (ser.data)



    def stix():
        req = {"feed": {
            "link": 'https://raw.githubusercontent.com/davidonzo/Threat-Intel/master/stix2/04485fad82d561bffe7e83dd47d81d7f.json',
            "confidence": 1242432,
            "name": f"name{random.randint(0, 12031)}"

        },
            "type": "stix",
            "raw_indicators": {"name": f"unique_name_{random.randint(0, 1000)}"}
        }
        feed = Feed(**req['feed'])

        result = parse_stix(feed, req['raw_indicators'])



    # free text https://www.misp-project.org/feeds/
    def misp():
        req = {"feed": {
            "link": "http://www.botvrij.eu/data/feed-osint/0319b483-5973-4932-91ea-5a44c2975b24.json",
            "confidence": 121242432,
            "name": f"name{random.randint(0, 12031)}"

        },
            "type": "misp",
            "raw_indicators": {"name": f"unique_name_{random.randint(0, 1000)}"}
        }

        feed = Feed(**req['feed'])
        parse_misp(feed, req['raw_indicators'])


    def free_text():
        req = {"feed": {
            "link": "https://cybercrime-tracker.net/all.php",
            "confidence": 121243228432,
            "format_of_feed": "TXT",
            "name": f"name{random.randint(0, 12031)}"
        },
            "type": "free_text",
            "raw_indicators": f"nawqdme1{random.randint(0, 10200)}\nnqame2{random.randint(0, 12000)}\nnamqe3{random.randint(0, 12000)}"
        }

        feed = Feed(**req['feed'])
        parse_free_text(feed, req['raw_indicators'])


    def csv():
        req = {"feed": {
            "link": "https://home.nuug.no/~peter/pop3gropers.txt",
            "confidence": 12112324228432,
            "name": f"name{random.randint(0, 12031)}"

        },
            "type": "free_text",
            "raw_indicators": f"nawqdme1{random.randint(0, 10200)}\nnqame2{random.randint(0, 12000)}\nnamqe3{random.randint(0, 12000)}"

        }

        feed = Feed(**req['feed'])
        parse_csv(feed, req['raw_indicators'])


    # stix()
    # misp()
    # free_text()
    # csv()
