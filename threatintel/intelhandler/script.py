from .models import Feed, Indicator
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests


def create_indicator(raw_indicators, feed):
    """
    Из списка индикаторов и параметров фида создает список
    """
    complete_indicators = []
    for raw_indicator in raw_indicators:
        complete_indicators.append(
            Indicator(
                type=feed.type_of_feed,
                value=raw_indicator,
                weight=feed.confidence,
                updated_date=datetime.now(),
            )
        )
    return complete_indicators


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

    result = create_indicator(raw_indicators, feed)
    return result


def parse_misp(page_with_urls, feed) -> list:
    """
    Парсит переданный текст со списком url'ок и отдает список индикаторов.
    Применяется когда по ссылке находится список json файлов.
    """
    if feed.link[-1] != "/":
        origin_link = feed.link + "/"
    parsed_page = BeautifulSoup(page_with_urls, "html.parser")
    urls_for_parsing = []
    for link in list(parsed_page.find_all("a")):
        if ".json" in link.text:
            urls_for_parsing.append(f"{feed.link}{link.get('href')}")
    return urls_for_parsing


def parse_xml(raw_indicators, feed) -> list:
    """
    Парсит переданный текст с xml и отдает список индикаторов.
    """

    pass


def parse_csv(raw_indicators, feed) -> list:  # не доделано
    """
    Парсит переданный текст с параметрами для csv и отдает список индикаторов.
    """
    raw_indicators = raw_indicators.split("\n")
    try:
        raw_indicators.remove("")
    except:
        pass
    raw_indicators = [
        ioc.replace("\r", "") for ioc in raw_indicators if not ioc.startswith("#")
    ]

    result = create_indicator(raw_indicators, feed)
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
