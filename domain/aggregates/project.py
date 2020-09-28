from typing import List
from pandas import DataFrame

from data.settings import Settings
from domain.entities.well import Well


class Project(object):

    def __init__(self, settings: Settings, wells: List[Well]):
        self.wells = wells
        self.settings = settings
        self._num_well = len(wells)

    def calc_metric(self):
        self._create_df_result()
        self._calc_metric_phase(phase='liq', source='model')
        self._calc_metric_phase(phase='oil', source='model')
        self._calc_metric_phase(phase='oil', source='ksg')

        self._create_df_result_month()
        self._calc_metric_month_phase(phase='liq', source='model')
        self._calc_metric_month_phase(phase='oil', source='model')
        self._calc_metric_month_phase(phase='oil', source='ksg')

    def _create_df_result(self):
        dates = self.wells[0].report.df_test.index
        columns = ['dev_prod_liq_model', 'dev_cum_liq_model',
                   'dev_prod_oil_model', 'dev_cum_oil_model',
                   'dev_prod_oil_ksg', 'dev_cum_oil_ksg',
                   'dev_sum_prod_oil_model,'
                   'dev_sum_prod_oil_ksg']
        self.df_result = DataFrame(index=dates, columns=columns)

    def _create_df_result_month(self):
        dates = self.wells[0].report.df_test_month.index
        columns = ['dev_prod_liq_model',
                   'dev_prod_oil_model',
                   'dev_prod_oil_ksg']
        self.df_result_month = DataFrame(index=dates, columns=columns)

    def _calc_metric_phase(self, phase: str, source: str):
        for date in self.df_result.index:
            sum_prod = 0
            sum_prod_source = 0
            dev_rate = 0
            dev_cum = 0
            for well in self.wells:
                df = well.report.df_test
                dev_rate += df.loc[date, f'dev_prod_{phase}_{source}']
                dev_cum += df.loc[date, f'dev_cum_{phase}_{source}']

                df = well.report.df_test
                sum_prod += df.loc[date, f'prod_{phase}']
                sum_prod_source += df.loc[date, f'prod_{phase}_{source}']

            self.df_result.loc[date, f'dev_prod_{phase}_{source}'] = dev_rate / self._num_well
            self.df_result.loc[date, f'dev_cum_{phase}_{source}'] = dev_cum / self._num_well

            relative_deviation = self._calc_relative_deviation(sum_prod, sum_prod_source)
            self.df_result.loc[date, f'dev_sum_prod_{phase}_{source}'] = relative_deviation

    def _calc_metric_month_phase(self, phase: str, source: str):
        for date in self.df_result_month.index:
            dev_prod = 0
            for well in self.wells:
                df = well.report.df_test_month
                dev_prod += df.loc[date, f'dev_prod_{phase}_{source}']
            self.df_result_month.loc[date, f'dev_prod_{phase}_{source}'] = dev_prod / self._num_well

    @staticmethod
    def _calc_relative_deviation(value_1: float, value_2: float) -> float:
        term_1 = abs(value_1 - value_2)
        term_2 = max(value_1, value_2)
        relative_deviation = term_1 / term_2 * 100
        return relative_deviation
