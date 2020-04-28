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
        self._mark_current_state()

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

    def _add_self(self):
        self.formation.zones.append(self)
        self.well.zones.append(self)

    def _mark_current_state(self):
        df = self.report.df_flood
        df_train = df.loc[slice('month', 'day')]
        self._cum_prods_oil = df_train['cum_prod_oil'].to_list()
        self._cum_prods_liq = df_train['cum_prod_liq'].to_list()
        self._cum_prod_oil_cur = self._cum_prods_oil[-1]
        self._cum_prod_liq_cur = self._cum_prods_liq[-1]
        self.watercuts = df_train['watercut'].to_list()

    def _predict_rate_liquid(self):
        # TODO: Write code about liquid prediction using flux lib.
        self._rates_liq = self.report.df_flood.loc['test']['prod_liq'].to_list()
        pass

    def _predict_rate_oil(self):
        df = self.report.df_flood.copy()
        df['watercut_model'] = None
        df['prod_oil_model'] = df['prod_oil']
        df['cum_prod_oil_model'] = df['cum_prod_oil']

        self.flood_model = CoreyModel(self._cum_prods_oil, self.watercuts)
        result = self.flood_model.predict(self._cum_prod_oil_cur, self._cum_prod_liq_cur, self._rates_liq)
        watercut_model = self.flood_model.watercuts_model + result['watercut']
        df['watercut_model'] = watercut_model
        df.loc['test']['prod_oil_model'] = result['rate_oil']
        df.loc['test']['cum_prod_oil_model'] = [self._cum_prod_oil_cur + x for x in np.cumsum(result['rate_oil'])]

        df = self._calc_prediction_metric(df)
        self.report.df_flood = df.copy()

    @staticmethod
    def _calc_prediction_metric(df):
        df['diff_rel_prod_oil'] = None
        df['diff_prod_oil'] = None
        df['diff_cum_prod_oil'] = None
        df_test = df.loc['test']
        for i in df_test['prod_oil'].index:
            prod_oil = df_test.loc[i, 'prod_oil']
            prod_oil_model = df_test.loc[i, 'prod_oil_model']
            df_test.loc[i, 'diff_rel_prod_oil'] = abs(prod_oil - prod_oil_model) / max(prod_oil, prod_oil_model)

            df_test.loc[i, 'diff_prod_oil'] = abs(prod_oil - prod_oil_model)

            cum_prod_oil = df_test.loc[i, 'cum_prod_oil']
            cum_prod_oil_model = df_test.loc[i, 'cum_prod_oil_model']
            df_test.loc[i, 'diff_cum_prod_oil'] = cum_prod_oil_model - cum_prod_oil
        return df
