from abc import ABC, abstractmethod

from data.settings import Settings
from domain.factories.object_creator import ObjectCreator


class _Repository(ABC):

    @abstractmethod
    def __init__(self,
                 settings: Settings):

        self.settings = settings
        self.data = None

    @abstractmethod
    def _get_data(self):
        pass

    def create_project(self):
        project = ObjectCreator.run(self.data)
        return project
