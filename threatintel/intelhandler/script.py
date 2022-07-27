import csv
import json
from uuid import uuid4

from bs4 import BeautifulSoup
from flatdict import FlatterDict
from stix2elevator.options import initialize_options

from intelhandler.models import (
    Indicator,
)
from intelhandler.services import parse_misp_event, get_url, get_or_elevate, convert_txt_to_indicator

initialize_options(options={"spec_version": "2.1"})




def parse_custom_json(feed, raw_indicators=None, config: dict = {}):
    """
    Парсит переданный кастомный json с выбранными из фида полями и отдает список индикаторов.
    """
    feed.save()
    raw_json = json.loads(get_url(feed.link))
    indicators = []
    for key, value in FlatterDict(raw_json).items():
        # if key.rfind(feed.custom_field) != -1:
        indicator, created = Indicator.objects.get_or_create(value=value, defaults={
            "uuid": uuid4(),
            "supplier_name": feed.vendor,
            "supplier_confidence": feed.confidence,
            "weight": feed.confidence
        })
        indicator.feeds.add(feed)
        indicators.append(indicator)
    return indicators


def parse_stix(feed, raw_indicators=None, config: dict = {}):
    """
    Парсит переданный json в формате STIX и отдает список индикаторов.
    """
    bundle = get_or_elevate(feed)
    objects = bundle.get("objects")
    raw_indicators = []
    for object in objects:
        if object.get("type") == "indicator":
            raw_indicators.append(object)
    indicators = []
    feed.save()
    for raw_indicator in raw_indicators:
        indicator, created = Indicator.objects.get_or_create(value=raw_indicator.get("name"),
                                                             defaults={
                                                                 "uuid": uuid4(),
                                                                 "first_detected_date": raw_indicator.get("created"),
                                                                 "supplier_name": feed.vendor,
                                                                 "supplier_confidence": feed.confidence,
                                                                 "weight": feed.confidence
                                                             }
                                                             )

        indicator.feeds.add(feed)
        pattern = raw_indicator.get("pattern")
        if "ip" in pattern:
            indicator.ioc_context_ip = pattern
            indicator.type = "IP"
        elif "filesize" in pattern:
            indicator.ioc_context_file_size = pattern
        indicator.save()
        indicators.append(indicator)
    return indicators


def parse_free_text(feed, raw_indicators=None, config: dict = {}):
    """
    Парсит переданный текст и отдает список индикаторов.
    """
    raw_indicators = raw_indicators.split("\n")
    try:
        raw_indicators.remove("")
    except:
        pass
    raw_indicators = [
        ioc.replace("\r", "") for ioc in raw_indicators if not ioc.startswith("#")
    ]
    result = convert_txt_to_indicator(feed, raw_indicators)
    return result


def parse_misp(feed, raw_indicators=None, config: dict = {}) -> list:
    """
    Парсит переданный текст со списком url'ок и отдает список индикаторов.
    Применяется когда по ссылке находится список json файлов.
    """
    parsed_page = BeautifulSoup(get_url(feed.link), "html.parser")
    urls_for_parsing = []
    for link in list(parsed_page.find_all("a")):
        if ".json" in link.text:
            urls_for_parsing.append(f"{feed.link}{link.get('href')}")
    misp_events = parse_misp_event(urls_for_parsing, feed)
    return misp_events


def parse_csv(feed, raw_indicators=None, config: dict = {}) -> list:
    """
    Парсит переданный текст с параметрами для csv и отдает список индикаторов.
    """
    raw_indicators = [
        row for row in raw_indicators.split("\n") if not row.startswith("#")
    ]
    indicators = []
    feed.save()
    for row in csv.DictReader(
            raw_indicators,
            delimiter=config.get('delimiter', ","),
            fieldnames=config.get('fieldnames', ""),
            dialect=config.get('dialect', "excel"),
    ):
        indicator, created = Indicator.objects.get_or_create(value=row.get(feed.custom_field), defaults={
            "uuid": uuid4,
            "supplier_name": feed.vendor,
            "supplier_confidence": feed.confidence,
            "weight": feed.confidence
        })
        # indicator.save()
        indicator.feeds.add(feed)
    return indicators
