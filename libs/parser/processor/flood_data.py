import pandas as pd


class FloodData(object):

    _ratio_points_month_day = 0.5

    def __init__(self,
                 df_month,
                 df_day):

        self.df_month = df_month
        self.df_day = df_day
        self.df = None
        self.delimiter_month_day = None

    def create(self):
        self._prepare()
        self._combine_month_day()
        return self.df

    def _prepare(self):
        self.df_month = self._process(self.df_month, drop_cols=['well', 'formation'])
        self.df_day = self._process(self.df_day, drop_cols=['well', 'bhp'])

    def _combine_month_day(self):
        dates_month = self.df_month.index
        dates_day = self.df_day.index
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
        self.delimiter_month_day = number_points_month

        df_month = self.df_month.head(number_points_month)
        df_day = self.df_day.tail(number_points_day)
        self.df = pd.concat(objs=[df_month, df_day],
                            axis='index',
                            keys=['month', 'day'],
                            names=['level_date', 'date'],
                            verify_integrity=True)

    def _calc_watercut(self):
        df = self.df.drop(columns='prod_liq')
        df = df.cumsum(axis='index')
        df.columns = ['cum_prod_oil', 'cum_prod_liq']
        df['watercut'] = None
        for i in self.df.index:
            prod_oil = self.df['prod_oil'][i]
            prod_liq = self.df['prod_liq'][i]
            df.loc[i, 'watercut'] = (prod_liq - prod_oil) / prod_liq
        self.df = self.df.join(df)

    @staticmethod
    def _process(df, drop_cols):
        df.drop(columns=drop_cols, inplace=True)
        df.dropna(axis='index', how='any', inplace=True)
        df.set_index(keys=['date', df.index], drop=True, inplace=True, verify_integrity=True)
        df = df.sum(axis='index', level='date')
        return df
