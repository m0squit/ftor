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

    def predict(self, time_period: int = 1):
        """Predicts liquid and oil rate for a given time period.

        Args:
            time_period: Month number for prediction. Default 1.
        """
        self._predict_rate_liquid()
        self._predict_rate_oil()

    def _predict_rate_liquid(self):
        df_flux = self.report.df_flux

    def _predict_rate_oil(self):
        df_flood = self.report.df_flood
        cum_prods_oil = df_flood['cum_prod_oil'].to_list()
        cum_prods_liq = df_flood['cum_prod_liq'].to_list()
        watercuts = df_flood['watercut'].to_list()
        cum_prod_oil_start = max(cum_prods_oil)
        cum_prod_liq_start = max(cum_prods_liq)
        self.flood_model = CoreyModel(cum_prods_oil, watercuts)
