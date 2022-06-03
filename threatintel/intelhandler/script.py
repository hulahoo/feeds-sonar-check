from .models import Feed, Indicator
from datetime import datetime
import requests


def create_indicator(raw_indicator, feed) -> Indicator:
    complete_indicator = Indicator(
        type=feed.type_of_feed,
        value=raw_indicator,
        weight=feed.confidence,
        updated_date=datetime.now(),
    )
    return complete_indicator


def parse_feed(feed) -> list:
    """
    Функция запрашивает данные с указанного url'а.
    Возвращает список индикаторов
    """
    if not isinstance(feed, Feed):
        raise Exception("Фид не был передан")
    try:
        raw_indicators = requests.get(feed.link).text.split("\n")
        try:
            raw_indicators.remove("")
        except:
            pass
        raw_indicators = [
            ioc.replace("\r", "") for ioc in raw_indicators if not ioc.startswith("#")
        ]
        result = [
            create_indicator(raw_indicator, feed) for raw_indicator in raw_indicators
        ]
    except:
        raise Exception("Возникла ошибка при получении или обработке данных")
    return result


# для проверки скрипта
# test_feed = Feed.objects.get()
# text = parse_feed(test_feed)
# print(text)
