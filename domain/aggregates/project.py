from typing import List
from pandas import DataFrame

from data.settings import Settings
from domain.entities.well import Well


class Project(object):

    def __init__(self,
                 wells: List[Well],
                 settings: Settings):

        self.wells = wells
        self._num_well = len(wells)
        self.settings = settings
        self.maes_train = None
        self.maes_test = None

    def calc_metric(self):
        self._create_df_result()
        self._calc_metric_phase(phase='liq', calc='model')
        self._calc_metric_phase(phase='oil', calc='model')
        self._calc_metric_phase(phase='oil', calc='ksg')
        self.maes_train = [well.flood_model.mae_train for well in self.wells]
        self.maes_test = [well.flood_model.mae_test for well in self.wells]

    def _create_df_result(self):
        forecast_days_number = self.settings.forecast_days_number
        index = [i for i in range(1, forecast_days_number + 1)]
        columns = ['dev_rel_rate_liq_model', 'dev_rel_cum_liq_model',
                   'dev_rel_rate_oil_model', 'dev_rel_cum_oil_model',
                   'dev_rel_rate_oil_ksg', 'dev_rel_cum_oil_ksg']
        self.df_result = DataFrame(index=index, columns=columns)

    def _calc_metric_phase(self, phase: str, calc: str):
        for i in self.df_result.index:
            dev_rel_rate = 0
            dev_rel_cum = 0
            for well in self.wells:
                df = well.report.df_test
                dev_rel_rate += df[f'dev_rel_rate_{phase}_{calc}'].to_list()[i - 1]
                dev_rel_cum += df[f'dev_rel_cum_{phase}_{calc}'].to_list()[i - 1]
            self.df_result.loc[i, f'dev_rel_rate_{phase}_{calc}'] = dev_rel_rate / self._num_well
            self.df_result.loc[i, f'dev_rel_cum_{phase}_{calc}'] = dev_rel_cum / self._num_well
