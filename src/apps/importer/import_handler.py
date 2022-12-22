import random

import requests
from dagster import DynamicOut, DynamicOutput, op, get_dagster_logger

from src.apps.importer.services import choose_type
from src.models.models import Feed
from src.models.services import get_source, get_source_by

PATTERN = "%Y-%m-%d"


def download(path: str) -> list:
    text = requests.get(path).text
    return text


@op(out=DynamicOut())
def get_sources():
    sources = get_source()
    for index, obj in enumerate(sources):
        yield DynamicOutput(value=(index, obj.id), mapping_key=f'{index}'.replace('.', '_'))


@op
def op_source_downloads_worker(context, data):

    _, obj = data
    fields = {'id': obj}
    obj = get_source_by(fields=fields)

    feed_raw = {"feed": {
        "link": obj.path,
        "confidence": random.randint(0, 1000000),
        "source_id": obj.id,
        "format_of_feed": obj.format,
        "name": obj.name
    },
        "raw_indicators": obj.raw_indicators,
        "config": {
            "limit": obj.max_rows,
            "is_instead_full": obj.is_instead_full
    }
    }

    feed = Feed(**feed_raw["feed"])

    method = choose_type(obj.format.lower())
    config = feed_raw.get('config', {})
    result = method(feed, feed_raw['raw_indicators'], config)

    return len(result)


@op
def end_worker(data):
    return len(data)
