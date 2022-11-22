from abc import ABC, abstractmethod


class AbstractProducer(ABC):
    """
    Абстрактный класс для базового описания продюсера
    """

    @abstractmethod
    def start_producer(self):
        raise NotImplementedError

    @abstractmethod
    def send_message(self):
        raise NotImplementedError

    @abstractmethod
    def start_process(self):
        raise NotImplementedError
