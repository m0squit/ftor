from abc import ABC, abstractmethod

from data.settings import Settings
from domain.aggregates.project import Project
from domain.factories.input_data import InputData
from domain.factories.project_creator import ProjectCreator


class _Repository(ABC):

    data: InputData

    @abstractmethod
    def _get_data(self):
        pass

    def create_project(self, settings: Settings) -> Project:
        project = ProjectCreator.run(self.data, settings)
        return project
