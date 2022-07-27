import json
from uuid import uuid4

import requests
from stix2elevator import elevate

from intelhandler.models import Indicator


def get_url(url) -> str:
    """
    Опрашивает переданный url и возвращает всю страницу в строковом формате.
    """
    try:
        received_data = requests.get(url).text
    except:
        raise Exception("Возникла ошибка при получении данных")
    return received_data


def get_or_elevate(feed) -> dict:
    """
    Узнает версию stix и переводит во вторую версию.
    """
    text = get_url(feed.link)
    try:
        return json.loads(text)
    except:
        return elevate(text)


def parse_misp_event(urls_for_parsing, feed):
    """
    Парсит MISP евенты со страницы с url'ами.
    """
    indicators = []
    for url in urls_for_parsing:
        indicators.append(convert_misp_to_indicator(json.loads(get_url(url)), feed))
    return indicators


def convert_misp_to_indicator(feed, raw_indicators=None):
    """
    Из MISP события и входящих в него параметров и объектов -
    импортирует список индиктаторов
    """
    indicators = []
    attributes = raw_indicators.get("Event").get("Attribute")
    attribute_in_object = []
    if raw_indicators.get("Event").get("Object"):
        for object in raw_indicators.get("Event").get("Object"):
            attribute_in_object = object.get("Attribute")

    attributes_list = [*attributes, *attribute_in_object]
    try:
        for attribute in attributes_list:
            indicator, created = Indicator.objects.get_or_create(value=attribute.get('value'), defaults={
                "uuid": attribute.get("uuid"),
                "ioc_context_type": attribute.get("type"),
                "supplier_name": feed.vendor,
                "supplier_confidence": feed.confidence,
                "weight": feed.confidence
            })

            try:
                indicator.feeds.add(feed)
                indicators.append(indicator)
            except:
                pass
    except TypeError:
        pass
        return indicators


def convert_txt_to_indicator(feed, raw_indicators=None):
    if feed.format_of_feed == "TXT":
        complete_indicators = []
        feed.save()
        for raw_indicator in raw_indicators:
            indicator, created = Indicator.objects.get_or_create(value=raw_indicator,
                                                                 defaults={
                                                                     "uuid": uuid4(),
                                                                     "supplier_name": feed.vendor,
                                                                     "type": feed.type_of_feed,
                                                                     "weight": feed.confidence,
                                                                     "supplier_confidence": feed.confidence
                                                                 })
            # indicator = Indicator(
            #     type=feed.type_of_feed,
            #     value=raw_indicator,
            #     weight=feed.confidence,
            # )
            indicator.feeds.add(feed)
            complete_indicators.append(indicator)
        return complete_indicators
