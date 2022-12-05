from typing import List, Union

from loguru import logger

from src.apps.producer.base import BaseProducer


class MessageProducer(BaseProducer):

    __slots__ = ("message_to_send", "topic", "producer")

    def __init__(self, message_to_send: dict, topic: str):
        self.message_to_send = message_to_send
        self.topic = topic

    def start_producer(self) -> None:
        self.producer = self._start_producer()
        logger.info("Producer started!")

    def send_message(self, *, message_to_send: dict, topic: Union[List, str]):
        self._send_data(data=message_to_send, topic=topic,
                        producer=self.producer)
        logger.info("Message successfully sent!")

    def start_process(self):
        self.start_producer()
        self.send_message(
            message_to_send=self.message_to_send, topic=self.topic)


def producer_entrypoint(*, message_to_send: dict, topic: str):
    producer = MessageProducer(message_to_send=message_to_send, topic=topic)
    logger.info("Producer created...")
    producer.start_process()
