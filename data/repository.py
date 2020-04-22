from abc import ABC, abstractmethod

from domain.factories.object_creator import ObjectCreator


class Repository(ABC):

    @abstractmethod
    def __init__(self):
        self.data = None

    @abstractmethod
    def _get_data(self):
        pass

    def create_project(self):
        project = ObjectCreator.run(self.data)
        return project
