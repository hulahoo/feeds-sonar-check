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


# def convert_csv_to_indicator(raw_indicators, feed):
#     fields = feed.field_names.split(",")
#     pass


def convert_txt_to_indicator(raw_indicators, feed):
    if feed.format_of_feed == "TXT":
        complete_indicators = []
        for raw_indicator in raw_indicators:
            indicator = Indicator(
                type=feed.type_of_feed,
                value=raw_indicator,
                weight=feed.confidence,
                feeds=feed,
                updated_date=datetime.now(),
            )
            complete_indicators.append(indicator)
            indicator.save()
        return complete_indicators


def convert_misp_to_indicator(raw_indicators, feed):
    """
    Из MISP события и входящих в него параметров и объектов -
    импортирует список индиктаторов
    """
    if feed.format_of_feed == "JSON":
        indicators = []
        attributes = raw_indicators.get("Event").get("Attribute")
        for attribute in attributes:
            indicator = Indicator(
                value=attribute.get("value"),
                uuid=attribute.get("uuid"),
                ioc_context_type=attribute.get("type"),
                weight=feed.confidence,
                updated_date=datetime.now(),
            )
            indicators.append(indicator)
        if raw_indicators.get("Event").get("Object"):
            for object in raw_indicators.get("Event").get("Object"):
                attribute_in_object = object.get("Attribute")
                indicator = Indicator(
                    value=attribute_in_object.get("value"),
                    uuid=attribute_in_object.get("uuid"),
                    ioc_context_type=attribute_in_object.get("type"),
                    weight=feed.confidence,
                    updated_date=datetime.now(),
                )
                indicators.append(indicator)
        return indicators


def parse_custom_json(raw_json, feed):
    """
    Парсит переданный кастомный json с выбранными из фида полями и отдает список индикаторов.
    """
    indicators = []
    for item in FlatterDict(raw_json).keys():
        if item[0].rfind(feed.custom_field) != -1:
            indicator = Indicator(
                value=item[1],
                supplier_name=feed.vendor,
                weight=feed.confidence,
                updated_date=datetime.now(),
                feeds=feed,
            )
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


def parse_stix(data_from_url, feed):
    """
    Парсит переданный json в формате STIX и отдает список индикаторов.
    """
    bundle = json.loads(data_from_url)
    objects = bundle.get("objects")
    raw_indicators = []
    for object in objects:
        if object.get("type") == "indicator":
            raw_indicators.append(object)
    indicators = []
    for raw_indicator in raw_indicators:
        indicator = Indicator(
            # uuid=uuid.uuid5(), # TODO: Fix uuid creating with params
            value=raw_indicator.get("name"),
            first_detected_date=raw_indicator.get("created"),
            updated_date=raw_indicator.get("modified"),
            feeds=feed,
        )
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


def parse_misp_event(urls_for_parsing, feed):
    """
    Парсит MISP евенты со страницы с url'ами.
    """
    indicators = []
    for url in urls_for_parsing:
        indicators.append = convert_misp_to_indicator(json.loads(get_url(url)), feed)
        pass
    return indicators


def parse_misp(page_with_urls, feed) -> list:
    """
    Парсит переданный текст со списком url'ок и отдает список индикаторов.
    Применяется когда по ссылке находится список json файлов.
    """
    # При неправильном пути
    # if feed.link[-1] != "/":
    #     origin_link = feed.link + "/"
    parsed_page = BeautifulSoup(page_with_urls, "html.parser")
    urls_for_parsing = []
    for link in list(parsed_page.find_all("a")):
        if ".json" in link.text:
            urls_for_parsing.append(f"{feed.link}{link.get('href')}")
    misp_events = parse_misp_event(urls_for_parsing, feed)

    return misp_events


def parse_xml(raw_indicators, feed) -> list:
    """
    Парсит переданный текст с xml и отдает список индикаторов.
    """

    pass


# TODO
# def parse_csv(raw_indicators, feed, fieldnames) -> list:  # не доделано
#     """
#     Парсит переданный текст с параметрами для csv и отдает список индикаторов.
#     """
#     raw_indicators = [
#         row for row in raw_indicators.split("\n") if not row.startswith("#")
#     ]
#     for row in csv.DictReader(
#         raw_indicators,
#         fieldnames=feed.field_names.split(","),
#         dialect="excel",
#     ):
#         print(row)

#     result = convert_csv_to_indicator(raw_indicators, feed)
#     pass
