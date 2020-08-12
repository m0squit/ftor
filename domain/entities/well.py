from typing import List

from domain.value_objects.report import Report
from libs.flood.corey_model import CoreyModel
from libs.flood.numeric_tools.loss_function import LossFunction


class Well(object):

    def __init__(self,
                 name: str,
                 report: Report):

        self.name = name
        self.report = report
        self._create_flood_model()

    def calc(self, rates_liq_model: List[float]):
        self._predict_rate_oil(rates_liq_model)
        self._create_df_test_month()
        self._calc_metric()

    def _create_flood_model(self):
        cum_oil = self.report.df_train['cum_oil'].to_list()
        watercuts = self.report.df_train['watercut'].to_list()
        self.flood_model = CoreyModel(cum_oil, watercuts)

    def _predict_rate_oil(self, rates_liq_model: List[float]):
        cum_oil_start = self.report.df_train['cum_oil'].iloc[-1]
        cum_liq_start = self.report.df_train['cum_liq'].iloc[-1]
        result = self.flood_model.predict(cum_oil_start, cum_liq_start, rates_liq_model)
        self.report.df_test = self.report.df_test.assign(prod_liq_model=rates_liq_model)
        self.report.df_test = self.report.df_test.assign(prod_oil_model=result['rate_oil'])
        self.report.df_test = self.report.df_test.assign(watercut_model=result['watercut'])
        self._calc_cumulative_productions()

    def _calc_cumulative_productions(self):
        self.report.df_test['cum_liq'] = self.report.df_test['prod_liq'].cumsum()
        self.report.df_test['cum_oil'] = self.report.df_test['prod_oil'].cumsum()
        self.report.df_test['cum_liq_model'] = self.report.df_test['prod_liq_model'].cumsum()
        self.report.df_test['cum_oil_model'] = self.report.df_test['prod_oil_model'].cumsum()
        self.report.df_test['cum_oil_ksg'] = self.report.df_test['prod_oil_ksg'].cumsum()

    def _create_df_test_month(self):
        first_test_date = self.report.df_test.index[0]
        df_test_month = self.report.df_month.loc[first_test_date:]
        df_test_month = df_test_month.drop(columns='watercut')
        months = [date.month for date in df_test_month.index]
        prods_oil_ksg = []
        prods_oil_model = []
        prods_liq_model = []
        for month in months:
            df = self.report.df_test.filter(like=f'-0{month}-', axis='index')
            prod_oil_ksg = df['prod_oil_ksg'].sum()
            prod_oil_model = df['prod_oil_model'].sum()
            prod_liq_model = df['prod_liq_model'].sum()
            prods_oil_ksg.append(prod_oil_ksg)
            prods_oil_model.append(prod_oil_model)
            prods_liq_model.append(prod_liq_model)
        df_test_month = df_test_month.assign(prod_oil_ksg=prods_oil_ksg)
        df_test_month = df_test_month.assign(prod_oil_model=prods_oil_model)
        df_test_month = df_test_month.assign(prod_liq_model=prods_liq_model)
        self.report.df_test_month = df_test_month

    def _calc_metric(self):
        self._calc_metric_watercut()
        self._calc_metric_phase(phase='liq', source='model')
        self._calc_metric_phase(phase='oil', source='model')
        self._calc_metric_phase(phase='oil', source='ksg')

        self._calc_metric_prod_phase_for_df_test_month(phase='liq', source='model')
        self._calc_metric_prod_phase_for_df_test_month(phase='oil', source='model')
        self._calc_metric_prod_phase_for_df_test_month(phase='oil', source='ksg')

    def _calc_metric_watercut(self):
        watercuts_fact = self.report.df_test['watercut'].to_list()
        watercuts_model = self.report.df_test['watercut_model'].to_list()
        self.flood_model.mae_test = LossFunction.run(watercuts_fact, watercuts_model)

    def _calc_metric_phase(self, phase: str, source: str):
        self.report.df_test[f'dev_prod_{phase}_{source}'] = None
        self.report.df_test[f'dev_cum_{phase}_{source}'] = None
        for date in self.report.df_test.index:
            self._calc_metric_phase_param('prod', phase, source, date)
            self._calc_metric_phase_param('cum', phase, source, date)

    def _calc_metric_phase_param(self, param: str, phase: str, source: str, date):
        param_fact = self.report.df_test.loc[date, f'{param}_{phase}']
        param_source = self.report.df_test.loc[date, f'{param}_{phase}_{source}']
        relative_deviation = self._calc_relative_deviation(param_fact, param_source)
        self.report.df_test.loc[date, f'dev_{param}_{phase}_{source}'] = relative_deviation

    def _calc_metric_prod_phase_for_df_test_month(self, phase: str, source: str):
        self.report.df_test_month[f'dev_prod_{phase}_{source}'] = None
        for date in self.report.df_test_month.index:
            prod_fact = self.report.df_test_month.loc[date, f'prod_{phase}']
            prod_source = self.report.df_test_month.loc[date, f'prod_{phase}_{source}']
            relative_deviation = self._calc_relative_deviation(prod_fact, prod_source)
            self.report.df_test_month.loc[date, f'dev_prod_{phase}_{source}'] = relative_deviation

    @staticmethod
    def _calc_relative_deviation(value_1: float, value_2: float) -> float:
        term_1 = abs(value_1 - value_2)
        term_2 = max(value_1, value_2)
        relative_deviation = term_1 / term_2 * 100
        return relative_deviation
