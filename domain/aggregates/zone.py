from domain.entities.formation import Formation
from domain.entities.well import Well
from domain.value_objects.fluid import Fluid
from domain.value_objects.report import Report
from libs.flood.corey.model import CoreyModel


class Zone(object):

    def __init__(self,
                 thickness: float,
                 type_boundaries: str,
                 type_completion: str,
                 formation: Formation,
                 fluid: Fluid,
                 well: Well,
                 report: Report):

        self.thickness = thickness
        self.type_boundaries = type_boundaries
        self.type_completion = type_completion
        self.formation = formation
        self.fluid = fluid
        self.well = well
        self.report = report
        self._add_self()

    def _add_self(self):
        self.formation.zones.append(self)
        self.well.zones.append(self)

    def predict_rate_oil(self):
        data_production = self.report.data_production
        cum_prods_oil = data_production['cum_prod_oil']
        watercuts = data_production['watercut']
        self.flood_model = CoreyModel(cum_prods_oil, watercuts)
