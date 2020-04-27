import numpy as np

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

        cum_prods_liq = self.report.df_flood_result.loc[slice('month', 'day')]['cum_prod_liq'].to_list()
        cum_prod_liq_start = max(cum_prods_liq)
        rates_liq = self.report.df_flood_result.loc['test']['prod_liq'].to_list()
        self.report.df_flood_result.loc['test']['cum_prod_liq'] = [cum_prod_liq_start + x for x in np.cumsum(rates_liq)]

    def _predict_rate_oil(self):
        cum_prods_oil = self.report.df_flood_result.loc[slice('month', 'day')]['cum_prod_oil'].to_list()
        cum_prods_liq = self.report.df_flood_result.loc[slice('month', 'day')]['cum_prod_liq'].to_list()
        watercuts = self.report.df_flood_result.loc[slice('month', 'day')]['watercut'].to_list()

        rate_liq = self.report.df_flood_result.loc['day']['prod_liq'].iloc[-1]
        rates_liq = [rate_liq] + self.report.df_flood_result.loc['test']['prod_liq'].to_list()

        self.flood_model = CoreyModel(cum_prods_oil, watercuts)
        cum_prod_oil_start = max(cum_prods_oil)
        cum_prod_liq_start = max(cum_prods_liq)
        result = self.flood_model.predict(cum_prod_oil_start, cum_prod_liq_start, rates_liq)

        # self.report.df_flood_result.loc[slice('month', 'day')]['watercut'] = self.flood_model.watercuts_model
        # self.report.df_flood_result.loc['test']['watercut'] = result['watercut']
        self.report.df_flood_result.loc['test']['prod_oil'] = result['rate_oil']
        self.report.df_flood_result.loc['test']['cum_prod_oil'] = [cum_prod_oil_start + x for x in np.cumsum(result['rate_oil'])]

        df = self.report.df_flood.loc['test']
        df_r = self.report.df_flood_result.loc['test']

        rates_oil_f = df['prod_oil'].to_list()
        rates_oil_m = df_r['prod_oil'].to_list()
        diffs_relative = []
        n = len(rates_oil_f)
        for i in range(n):
            rate_f = rates_oil_f[i]
            rate_m = rates_oil_m[i]
            diff = abs(rate_f - rate_m) / max(rate_f, rate_m)
            diffs_relative.append(diff)
        mape = sum(diffs_relative) / n

        self.diffs_relative_rate = diffs_relative
        self.mape = mape

        cp_oil_f = df['cum_prod_oil'].to_list()
        cp_oil_m = df_r['cum_prod_oil'].to_list()
        diffs_relative = []
        n = len(rates_oil_f)
        for i in range(n):
            cp_f = cp_oil_f[i]
            cp_m = cp_oil_m[i]
            diff = cp_m / cp_f
            diffs_relative.append(diff)

        self.diffs_relative_cp = diffs_relative
