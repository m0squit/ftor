from typing import List

from data.settings import Settings
from domain.aggregates.project import Project
from domain.entities.formation import Formation
from domain.entities.well import Well
from domain.factories.input_data import InputData
from domain.value_objects.fluid import Fluid
from domain.value_objects.report import Report


class ProjectCreator(object):

    _settings: Settings
    _wells: List[Well]
    _project: Project

    @classmethod
    def run(cls, input_data: InputData, settings: Settings) -> Project:
        cls._settings = settings
        cls._create_wells(input_data)
        cls._create_project()
        return cls._project

    @classmethod
    def _create_wells(cls, input_data: InputData):
        cls._wells = []
        for name, data in input_data.wells.items():
            # radius = data['radius']
            #
            # fluid = Fluid(data['density'],
            #               data['viscosity'],
            #               data['volume_factor'])
            #
            # formation = Formation(data['formations_names'],
            #                       data['thickness'],
            #                       data['porosity'],
            #                       fluid,
            #                       data['compressibility'],
            #                       data['type_completion'],
            #                       data['type_boundaries'])

            report = Report(data['df_month'],
                            data['df_day'],
                            cls._settings)

            well = Well(name,
                        # radius,
                        # formation,
                        report)

            cls._wells.append(well)

    @classmethod
    def _create_project(cls):
        cls._project = Project(cls._wells, cls._settings)
