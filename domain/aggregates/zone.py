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

    def predict(self, mode='test'):
        """Predicts liquid and oil rate on 1 month.

        Args:
            mode: Calculation mode for prediction. Available modes: 'final', 'test'.
                Final mode - prediction on unverifiable month.
                Test mode - prediction on last month from given data.
                Default - test.
        """
        self.report.prepare(mode)
        self._predict_rate_liquid()
        self._predict_rate_oil()

    def _predict_rate_liquid(self):
        # TODO: Write code about liquid prediction using flux lib.
        pass

    def _predict_rate_oil(self):
        df_flood = self.report.df_flood.loc[slice('month', 'day')]

        cum_prods_oil = df_flood['cum_prod_oil'].to_list()
        cum_prods_liq = df_flood['cum_prod_liq'].to_list()
        watercuts = df_flood['watercut'].to_list()
        cum_prod_oil_start = max(cum_prods_oil)
        cum_prod_liq_start = max(cum_prods_liq)

        df_flood_result = self.report.df_flood.loc['test']
        rates_liq = df_flood_result['prod_liq'].to_list()
        rates_liq.insert(0, 0)
        self.flood_model = CoreyModel(cum_prods_oil, watercuts, 12627651260.49573)
        result = self.flood_model.predict(cum_prod_oil_start, cum_prod_liq_start, rates_liq)

        df_flood_result['prod_oil'] = result['rate_oil']
        df_flood_result['watercut'] = result['watercut']
        df_flood_result['cum_prod_oil'] = [cum_prod_oil_start + x for x in result['rate_oil']]
        self.report.df_flood_result = df_flood_result
