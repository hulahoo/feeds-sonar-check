from intelhandler.models import (
    Feed,
    Indicator,
    MispEvent,
    MispObject,
    Attribute,
    OrganizationContact,
    Tag,
)
from datetime import datetime
from bs4 import BeautifulSoup
import csv
import requests
import json


def convert_to_indicator(raw_indicators, feed):
    """
    Из списка индикаторов и параметров фида создает список
    """
    print("Конвертирую фид в индикаторы")
    if feed.format_of_feed == "TXT":
        complete_indicators = []
        for raw_indicator in raw_indicators:
            indicator = Indicator(
                type=feed.type_of_feed,
                value=raw_indicator,
                weight=feed.confidence,
                updated_date=datetime.now(),
            )
            complete_indicators.append(indicator)
            indicator.save()
        return complete_indicators
    elif feed.format_of_feed == "JSON":
        event = raw_indicators.get("Event")
        misp_event = MispEvent(
            threat_level_id=event.get("threat_level_id"),
            timestamp=event.get("timestamp"),
            info=event.get("info"),
            publish_timestamp=event.get("publish_timestamp"),
            date=event.get("date"),
            published=event.get("published"),
            analysis=event.get("analysis"),
            uuid=event.get("uuid"),
        )
        # additional relations
        organization_contacts = OrganizationContact(
            name=event.get("Orgc").get("name"),
            uuid=event.get("Orgc").get("uuid"),
        )
        organization_contacts.save()
        misp_event.orgc = organization_contacts
        tags = []
        for tag in event.get("Tag"):
            tag = Tag(name=tag.get("name"), colour=tag.get("colour"))
            tag.save()
            tags.append(tag)
        misp_event.tag.add(tags)

        return misp_event


def get_url(url) -> str:
    """
    Опрашивает переданный url и возвращает всю страницу в строковом формате.
    """
    try:
        received_data = requests.get(url).text
    except:
        raise Exception("Возникла ошибка при получении данных")
    return received_data


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
    result = convert_to_indicator(raw_indicators, feed)
    return result


# In work
def parse_misp_event(urls_for_parsing, feed):
    """
    Парсит MISP евенты со страницы с url'ами.
    """
    indicators = []
    for url in urls_for_parsing:
        indicators.append = convert_to_indicator(json.loads(get_url(url)), feed)
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


def parse_csv(raw_indicators, feed, fieldnames) -> list:  # не доделано
    """
    Парсит переданный текст с параметрами для csv и отдает список индикаторов.
    """
    raw_indicators = raw_indicators.split("\n")
    for row in csv.DictReader(
        raw_indicators, fieldnames=["Firstseen", "DstIP", "DstPort"], dialect="excel"
    ):
        pass
    result = convert_to_indicator(raw_indicators, feed)
    pass


def parse_feed(feed):
    """
    Функция принимает фид который необходимо спарсить.
    Возвращает список индикаторов.
    """
    if not isinstance(feed, Feed):
        raise Exception("Фид не был передан")
    try:
        raw_data = get_url(feed.link)
    except:
        raise Exception("Возникла ошибка при получении данных")
    try:
        match feed.format_of_feed:
            case "TXT":
                print("This is TXT feed format")
                result = parse_free_text(raw_data, feed)
            case "XML":
                result = parse_xml(raw_data, feed)
            case "JSN":
                result = parse_misp(raw_data, feed)
            case "CSV":
                result = parse_csv(raw_data, feed)
    except:
        raise Exception("Возникла ошибка при обработке данных")
    return result
