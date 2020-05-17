import pandas as pd
from pandas import DataFrame

from data.settings import Settings


class FloodData(object):

    _df_month: DataFrame
    _df_day: DataFrame
    _df_test: DataFrame
    _settings: Settings

    def __init__(self,
                 df_month,
                 df_day,
                 settings):

        self.df_month = df_month.copy()
        self.df_day = df_day.copy()
        self._settings = settings
        self._create()

    def _create(self):
        self._prepare_month_day()
        self._cut_test()
        self._create_df()
        self._convert_prod_to_cum_prod()

    def _prepare_month_day(self):
        self.df_month = self._process(self.df_month, drop_cols=['well', 'formation'])
        self.df_day = self._process(self.df_day, drop_cols=['well', 'bhp'])

    def _cut_test(self):
        total_days_number = len(self.df_day.index)
        forecast_days_number = self._settings.forecast_days_number
        self._df_test = self.df_day.tail(forecast_days_number)
        day_number_train = total_days_number - forecast_days_number
        self._df_day = self.df_day.head(day_number_train)
        last_train_day = self._df_day.index[-1]
        self._df_month = self.df_month.loc[:last_train_day]

    def _create_df(self):
        train_mode = self._settings.train_mode
        objs = []
        keys = []
        if train_mode == 'month':
            objs.append(self._df_month)
            keys.append('month')

        if train_mode == 'day':
            objs.append(self._df_day)
            keys.append('day')

        if train_mode == 'mix':
            self._combine_month_day()
            objs.extend([self._df_month, self._df_day])
            keys.extend(['month', 'day'])

        self._add_test(objs, keys)

    def _combine_month_day(self):
        dates_month = self._df_month.index
        dates_day = self._df_day.index
        ratios = []
        for i in range(len(dates_day)):
            date_day = dates_day[i]
            number_points_month = len(dates_month[dates_month < date_day])
            number_points_day = len(dates_day[dates_day >= date_day])
            ratio = number_points_month / number_points_day
            ratios.append(ratio)
        ratio_points_month_day = min(ratios, key=lambda x: abs(x - self._settings.ratio_points_month_day))
        i = ratios.index(ratio_points_month_day)
        number_points_month = len(dates_month[dates_month < dates_day[i]])
        number_points_day = len(dates_day[dates_day >= dates_day[i]])
        self._df_month = self._df_month.head(number_points_month)
        self._df_day = self._df_day.tail(number_points_day)

    def _add_test(self, objs, keys):
        objs.append(self._df_test)
        keys.append('test')
        self.df = pd.concat(objs=objs,
                            axis='index',
                            keys=keys,
                            names=['data_key', 'date'],
                            verify_integrity=True)

    def _convert_prod_to_cum_prod(self):
        df = self.df[['prod_oil', 'prod_liq']]
        df = df.cumsum(axis='index')
        df.columns = ['cum_prod_oil', 'cum_prod_liq']
        self.df = self.df.join(df)

    @classmethod
    def _process(cls, df, drop_cols):
        df.drop(columns=drop_cols, inplace=True)
        df.dropna(axis='index', how='any', inplace=True)
        df.set_index(keys=['date', df.index], drop=True, inplace=True, verify_integrity=True)
        df = df.sum(axis='index', level='date')
        df = cls._calc_watercut(df)
        df = cls._drop_zero_watercut(df)
        return df

    @staticmethod
    def _calc_watercut(df):
        df['watercut'] = None
        for i in df.index:
            prod_oil = df.loc[i, 'prod_oil']
            prod_liq = df.loc[i, 'prod_liq']
            df.loc[i, 'watercut'] = (prod_liq - prod_oil) / prod_liq
        return df

    @staticmethod
    def _drop_zero_watercut(df):
        indexes_to_drop = df[df['watercut'] == 0].index
        df.drop(index=indexes_to_drop, inplace=True)
        return df
