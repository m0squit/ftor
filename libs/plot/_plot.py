from abc import ABC, abstractmethod


class _Plot(ABC):

    @classmethod
    @abstractmethod
    def create(cls, ):
        pass
