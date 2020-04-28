import pandas as pd


class FloodData(object):

    _ratio_points_month_day = 0.5

    def __init__(self,
                 df_month,
                 df_day):

        self._df_month = df_month
        self._df_day = df_day
        self._create()

    def _create(self):
        self._prepare_month_day()
        self._save_test_from_day()
        self._conjoin_month_day()
        self._combine_month_day_test()
        self._calc_watercut()
        self._drop_zero_watercut()

    def _prepare_month_day(self):
        self._df_month = self._process(self._df_month, drop_cols=['well', 'formation'])
        self._df_day = self._process(self._df_day, drop_cols=['well', 'bhp'])

    def _save_test_from_day(self):
        day_count = len(self._df_day.index)
        day_number_test = 30
        day_number_train = day_count - day_number_test
        self._df_test = self._df_day.tail(day_number_test)
        self._df_day = self._df_day.head(day_number_train)

    def _conjoin_month_day(self):
        dates_month = self._df_month.index
        dates_day = self._df_day.index
        ratios = []
        for i in range(len(dates_day)):
            date_day = dates_day[i]
            number_points_month = len(dates_month[dates_month < date_day])
            number_points_day = len(dates_day[dates_day >= date_day])
            ratio = number_points_month / number_points_day
            ratios.append(ratio)
        ratio_points_month_day = min(ratios, key=lambda x: abs(x - self._ratio_points_month_day))
        i = ratios.index(ratio_points_month_day)
        number_points_month = len(dates_month[dates_month < dates_day[i]])
        number_points_day = len(dates_day[dates_day >= dates_day[i]])
        self._df_month = self._df_month.head(number_points_month)
        self._df_day = self._df_day.tail(number_points_day)

    def _combine_month_day_test(self):
        self.df = pd.concat(objs=[self._df_month, self._df_day, self._df_test],
                            axis='index',
                            keys=['month', 'day', 'test'],
                            names=['data_key', 'date'],
                            verify_integrity=True)

    def _calc_watercut(self):
        df = self.df
        df = df.cumsum(axis='index')
        df.columns = ['cum_prod_oil', 'cum_prod_liq']
        df['watercut'] = None
        for i in self.df.index:
            prod_oil = self.df.loc[i, 'prod_oil']
            prod_liq = self.df.loc[i, 'prod_liq']
            df.loc[i, 'watercut'] = (prod_liq - prod_oil) / prod_liq
        self.df = self.df.join(df)

    def _drop_zero_watercut(self):
        indexes_to_drop = self.df[self.df['watercut'] == 0].index
        self.df.drop(index=indexes_to_drop, inplace=True)

    @staticmethod
    def _process(df, drop_cols):
        df = df.drop(columns=drop_cols)
        df = df.dropna(axis='index', how='any')
        df = df.set_index(keys=['date', df.index], drop=True, verify_integrity=True)
        df = df.sum(axis='index', level='date')
        return df
