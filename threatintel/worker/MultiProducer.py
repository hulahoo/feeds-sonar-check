import json
from typing import List

from django.conf import settings
from kafka import KafkaProducer


def json_serializer(data):
    return json.dumps(data).encode('utf-8')


class MultiProducer:
    producer = KafkaProducer(bootstrap_servers=[f'{settings.KAFKA_IP}:9092'],
                             value_serializer=json_serializer)

    @classmethod
    def send_data(cls, data: dict):
        try:
            topic = settings.KAFKA_TOPIC
            cls.producer.send(topic, data)
        except Exception as e:
            print(e)

    @classmethod
    def send_list_of_data(cls, data_lst: List[dict]):
        for data in data_lst:
            cls.send_data(data)
        cls.flush()

    @classmethod
    def flush(cls, timeout=60 * 5):
        cls.producer.flush(timeout=timeout)
