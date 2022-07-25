import json
from typing import List

from kafka import KafkaProducer

from worker.utils import django_init

django_init()
from django.conf import settings


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


# if __name__ == '__main__':
    # def stix():
    # req = {"feed": {
    #     "url": 'https://raw.githubusercontent.com/davidonzo/Threat-Intel/master/stix2/01e05d0c2d5ee8b49a6a06ff623af7e1.json',
    #
    # },
    #     "type": "stix",
    #     "raw_indicators": []
    # }
    #
    # print(settings.KAFKA_TOPIC, settings.KAFKA_IP)
    # MultiProducer.send_data({"WQE": 'QWW'})
    # MultiProducer.flush()
