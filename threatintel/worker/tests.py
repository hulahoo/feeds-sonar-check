import json
import random
from typing import List

from kafka import KafkaProducer

from worker.utils import django_init

django_init()
from django.conf import settings
from intelhandler.script import parse_stix
from intelhandler.models import Feed

if __name__ == '__main__':
    req = {"feed": {
        "link": 'https://raw.githubusercontent.com/davidonzo/Threat-Intel/master/stix2/01e05d0c2d5ee8b49a6a06ff623af7e1.json',
        "confidence":1242432

    },
        "type": "stix",
        "raw_indicators": {"name":f"unique_name_{random.randint(0,1000)}"}
    }
    feed = Feed(**req['feed'])

    parse_stix(feed,req['raw_indicators'])
