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
        self._settings = settings
        self.maes_train = None
        self.maes_test = None

    def calc_metric(self):
        self._create_df_result()

        for i in self.df_result.index:
            dev_abs_rate_oil = 0
            dev_rel_rate_oil = 0
            dev_abs_cum_oil = 0
            dev_rel_cum_oil = 0
            for well in self.wells:
                df = well.report.df_test
                dev_abs_rate_oil += df['dev_abs_rate_oil'].to_list()[i - 1]
                dev_rel_rate_oil += df['dev_rel_rate_oil'].to_list()[i - 1]
                dev_abs_cum_oil += df['dev_abs_cum_oil'].to_list()[i - 1]
                dev_rel_cum_oil += df['dev_rel_cum_oil'].to_list()[i - 1]
            self.df_result.loc[i, 'dev_abs_rate_oil'] = dev_abs_rate_oil / self._num_well
            self.df_result.loc[i, 'dev_rel_rate_oil'] = dev_rel_rate_oil / self._num_well
            self.df_result.loc[i, 'dev_abs_cum_oil'] = dev_abs_cum_oil / self._num_well
            self.df_result.loc[i, 'dev_rel_cum_oil'] = dev_rel_cum_oil / self._num_well

        self.maes_train = [well.flood_model.mae_train for well in self.wells]
        self.maes_test = [well.flood_model.mae_test for well in self.wells]

    def _create_df_result(self):
        forecast_days_number = self._settings.forecast_days_number
        index = [i for i in range(1, forecast_days_number + 1)]
        columns = ['dev_abs_rate_oil', 'dev_rel_rate_oil', 'dev_abs_cum_oil', 'dev_rel_cum_oil']
        self.df_result = DataFrame(index=index, columns=columns)
