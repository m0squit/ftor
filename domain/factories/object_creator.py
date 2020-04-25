from typing import List

from domain.aggregates.field import Field
from domain.aggregates.project import Project
from domain.aggregates.zone import Zone
from domain.entities.formation import Formation
from domain.entities.well import Well
from domain.factories.input_data import InputData
from domain.value_objects.fluid import Fluid
from domain.value_objects.report import Report


class ObjectCreator(object):

    _data: InputData
    _formations: List[Formation]
    _wells: List[Well]
    _zones: List[Zone]
    _fields: List[Field]
    _project: Project

    @classmethod
    def run(cls, data: InputData) -> Project:
        cls._data = data
        cls._create_formations()
        cls._create_wells()
        cls._create_zones()
        field = Field('kholmogorskoe', cls._formations, cls._wells)
        project = Project('project', cls._zones, [field])
        return project

    @classmethod
    def _create_formations(cls):
        formations = []
        for name, porosity in cls._data.formation_porosity_dict.items():
            formation = Formation(name, porosity, compressibility_total=5e-5)
            formations.append(formation)
        cls._formations = formations

    @classmethod
    def _create_wells(cls):
        wells = []
        for name, radius in cls._data.well_radius_dict.items():
            well = Well(name, radius)
            wells.append(well)
        cls._wells = wells

    @classmethod
    def _create_zones(cls):
        zones = []
        zone_dict = cls._data.zone_dict
        for well_name, well_dict in zone_dict.items():
            well = cls._find_well(name=well_name)

            for formation_name, formation_dict in well_dict.items():
                thickness = formation_dict['thickness']
                type_boundaries = formation_dict['type_boundaries']
                type_completion = formation_dict['type_completion']
                formation = cls._find_formation(name=formation_name)

                density = formation_dict['density']
                viscosity = formation_dict['viscosity']
                volume_factor = formation_dict['volume_factor']
                fluid = Fluid(density, viscosity, volume_factor)

                flood_data = formation_dict['flood_data']
                flux_data = formation_dict['flux_data']
                report = Report(data_rate=flux_data.df, data_production=flood_data.df)
                zone = Zone(thickness, type_boundaries, type_completion, formation, fluid, well, report)
                zones.append(zone)
        cls._zones = zones

    @classmethod
    def _find_well(cls, name):
        for well in cls._wells:
            if well.name == name:
                return well

    @classmethod
    def _find_formation(cls, name):
        for formation in cls._formations:
            if formation.name == name:
                return formation
