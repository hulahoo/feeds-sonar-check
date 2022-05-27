from tkinter import E
import requests


def get_data_from_url(url) -> list:
    """
    Функция запрашивает данные с указанного url'а.
    """
    try:
        result = requests.get(url).text
    except:
        raise Exception("Возникла ошибка при получении данных")
    
    return result


text = get_data_from_url("https://openphish.com/feed.txt").split("\n")
text.remove("")
print(text)