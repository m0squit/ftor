from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def __init__(self):
        self.data = None

    @abstractmethod
    def get_data(self):
        pass

    def create_project(self, data):
        # Calls factory to create all objects as project.
        pass
