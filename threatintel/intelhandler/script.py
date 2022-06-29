from uuid import uuid4
from intelhandler.models import (
    Feed,
    Indicator,
    Tag,
)
from datetime import datetime, date
from bs4 import BeautifulSoup
from flatdict import FlatterDict
import csv
import requests
import json


def convert_txt_to_indicator(raw_indicators, feed):
    if feed.format_of_feed == "TXT":
        complete_indicators = []
        for raw_indicator in raw_indicators:
            indicator = Indicator(
                type=feed.type_of_feed,
                value=raw_indicator,
                weight=feed.confidence,
            )
            indicator.save()
            indicator.feeds.add(feed)
            complete_indicators.append(indicator)
        return complete_indicators


def parse_custom_json(feed):
    """
    Парсит переданный кастомный json с выбранными из фида полями и отдает список индикаторов.
    """
    raw_json = json.loads(get_url(feed.link))
    indicators = []
    for key, value in FlatterDict(raw_json).items():
        if key.rfind(feed.custom_field) != -1:
            indicator = Indicator(
                uuid=uuid4(),
                value=value,
                supplier_name=feed.vendor,
                supplier_confidence=feed.confidence,
                weight=feed.confidence,
            )
            indicator.save()
            indicator.feeds.add(feed)
            indicators.append(indicator)
    return indicators


def get_url(url) -> str:
    """
    Опрашивает переданный url и возвращает всю страницу в строковом формате.
    """
    try:
        received_data = requests.get(url).text
    except:
        raise Exception("Возникла ошибка при получении данных")
    return received_data


def parse_stix(feed):
    """
    Парсит переданный json в формате STIX и отдает список индикаторов.
    """
    bundle = json.loads(get_url(feed.link))
    objects = bundle.get("objects")
    raw_indicators = []
    for object in objects:
        if object.get("type") == "indicator":
            raw_indicators.append(object)
    indicators = []
    for raw_indicator in raw_indicators:
        indicator = Indicator(
            uuid=uuid4(),
            value=raw_indicator.get("name"),
            first_detected_date=raw_indicator.get("created"),
            supplier_name=feed.vendor,
            supplier_confidence=feed.confidence,
            weight=feed.confidence,
        )
        indicator.save()
        indicator.feeds.add(feed)
        pattern = raw_indicator.get("pattern")
        if "ip" in pattern:
            indicator.ioc_context_ip = pattern
            indicator.type = "IP"
        elif "filesize" in pattern:
            indicator.ioc_context_file_size = pattern
        indicators.append(indicator)
    return indicators


def parse_free_text(raw_indicators, feed):
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
    result = convert_txt_to_indicator(raw_indicators, feed)
    return result


def convert_misp_to_indicator(raw_indicators, feed):
    """
    Из MISP события и входящих в него параметров и объектов -
    импортирует список индиктаторов
    """
    indicators = []
    attributes = raw_indicators.get("Event").get("Attribute")
    try:
        for attribute in attributes:
            indicator = Indicator(
                value=attribute.get("value"),
                uuid=attribute.get("uuid"),
                ioc_context_type=attribute.get("type"),
                supplier_name=feed.vendor,
                supplier_confidence=feed.confidence,
                weight=feed.confidence,
            )
            try:
                indicator.save()
                indicator.feeds.add(feed)
                indicators.append(indicator)
            except:
                pass
        if raw_indicators.get("Event").get("Object"):
            for object in raw_indicators.get("Event").get("Object"):
                attribute_in_object = object.get("Attribute")
                for attribute in attribute_in_object:
                    indicator = Indicator(
                        value=attribute.get("value"),
                        uuid=attribute.get("uuid"),
                        ioc_context_type=attribute.get("type"),
                        supplier_name=feed.vendor,
                        supplier_confidence=feed.confidence,
                        weight=feed.confidence,
                    )
                    try:
                        indicator.save()
                        indicator.feeds.add(feed)
                        indicators.append(indicator)
                    except:
                        pass
    except TypeError:
        pass
        return indicators


def parse_misp_event(urls_for_parsing, feed):
    """
    Парсит MISP евенты со страницы с url'ами.
    """
    indicators = []
    for url in urls_for_parsing:
        indicators.append(convert_misp_to_indicator(json.loads(get_url(url)), feed))
    return indicators


def parse_misp(feed) -> list:
    """
    Парсит переданный текст со списком url'ок и отдает список индикаторов.
    Применяется когда по ссылке находится список json файлов.
    """
    # При неправильном пути
    # if feed.link[-1] != "/":
    #     origin_link = feed.link + "/"
    parsed_page = BeautifulSoup(get_url(feed.link), "html.parser")
    urls_for_parsing = []
    for link in list(parsed_page.find_all("a")):
        if ".json" in link.text:
            urls_for_parsing.append(f"{feed.link}{link.get('href')}")
    misp_events = parse_misp_event(urls_for_parsing, feed)
    return misp_events


def parse_csv(feed) -> list:
    """
    Парсит переданный текст с параметрами для csv и отдает список индикаторов.
    """
    raw_indicators = [
        row for row in raw_indicators.split("\n") if not row.startswith("#")
    ]
    indicators = []
    for row in csv.DictReader(
        raw_indicators,
        delimiter=feed.field_names.separator,
        fieldnames=feed.field_names.split(","),
        dialect="excel",
    ):
        indicator = Indicator(
            uuid=uuid4(),
            value=row.get(feed.custom_field),
            supplier_name=feed.vendor,
            supplier_confidence=feed.confidence,
            weight=feed.confidence,
        )
        indicator.save()
        indicator.feeds.add(feed)
    return indicators
