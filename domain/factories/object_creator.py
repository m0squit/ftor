from domain.aggregates.field import Field
from domain.aggregates.project import Project
from domain.aggregates.zone import Zone
from domain.entities.formation import Formation
from domain.entities.well import Well
from domain.value_objects.fluid import Fluid
from domain.value_objects.report import Report
from domain.value_objects.reservoir import Reservoir


class ObjectCreator(object):

    _formations = []
    _wells = []
    _zones = []
    _fields = []
    _project = None

    @classmethod
    def run(cls, data):
        reservoir = Reservoir(thickness=10, porosity=0.2)
        fluid = Fluid(density=900, viscosity=1.5, volume_factor=1.1)

        formation_names = data['formations']
        for name in formation_names:
            formation = Formation(name, reservoir, fluid, compressibility_total=5e-5)
            cls._formations.append(formation)

        well_names = data['wells']
        for name in well_names:
            well = Well(name, radius=0.1)
            cls._wells.append(well)

        well_dict = data['data']
        for well_key, well_value in well_dict.items():
            well = cls._find_well(name=well_key)
            formation_dict = well_dict[well_key]
            for formation_key, formation_value in formation_dict.items():
                formation = cls._find_formation(name=formation_key)
                df_rate = formation_value['df_rate']
                df_production = formation_value['df_production']
                report = Report(data_rate=df_rate, data_production=df_production)
                zone = Zone(formation, well, report, type_completion=None, type_boundaries=None)
                cls._zones.append(zone)

        field = Field('kholmogorskoe', cls._formations, cls._wells)
        project = Project(name=None, fields=field)
        return project

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
