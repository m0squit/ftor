import datetime
from numpy import cumsum
from pandas import DataFrame, concat

from data.settings import Settings


class Report(object):

    def __init__(self,
                 df_train,
                 df_fact,

                 df_month: DataFrame,
                 df_day: DataFrame,
                 settings: Settings):

        self.df_month_original = df_month
        self.df_day_original = df_day
        self.settings = settings
        self._df_month = df_month
        self._df_day = df_day
        self._create()

    def calc_metric(self):
        df_test = self.df_test
        df_result = self.df_result
        for i in df_test.index:
            ro_fact = df_test.loc[i, 'prod_oil']
            ro_model = df_result.loc[i, 'prod_oil']
            co_fact = df_test.loc[i, 'cum_prod_oil']
            co_model = df_result.loc[i, 'cum_prod_oil']
            df_result.loc[i, 'dev_rel_rate_oil'] = abs(ro_fact - ro_model) / max(ro_fact, ro_model)
            df_result.loc[i, 'dev_abs_cum_oil'] = co_model - co_fact

    def _create(self):
        if self.settings.prediction_mode == 'test':
            self._cut_test()
        self._calc_current_cum_prod()
        self._create_df()
        self._create_df_result()

    def _cut_test(self):
        forecast_days_number = self.settings.forecast_days_number
        self.df_test = self._df_day.tail(forecast_days_number)
        self.df_test = self._calc_cum_prods(self.df_test)

        first_test_date = self.df_test.index[0]
        self._df_month = self._df_month.loc[:first_test_date]

        total_days_number = len(self._df_day.index)
        days_number_train = total_days_number - forecast_days_number
        self._df_day = self._df_day.head(days_number_train)

    def _calc_current_cum_prod(self):
        df_month = self._df_month
        df_day = self._df_day
        last_month_date = df_month.index[-1]
        last_day_date = df_day.index[-1]
        prods_oil = df_month['prod_oil'].to_list() + df_day['prod_oil'][last_month_date:last_day_date].to_list()[1:]
        prods_liq = df_month['prod_liq'].to_list() + df_day['prod_liq'][last_month_date:last_day_date].to_list()[1:]
        self.cum_prod_oil = sum(prods_oil)
        self.cum_prod_liq = sum(prods_liq)

    def _create_df(self):
        train_mode = self.settings.train_mode
        if train_mode == 'month':
            self.df = self._df_month
        if train_mode == 'day':
            self.df = self._df_day
        if train_mode == 'mix':
            self._create_mix_month_day()
        self.df = self._calc_cum_prods(self.df)

    def _create_mix_month_day(self):
        dates_month = self._df_month.index
        dates_day = self._df_day.index
        ratios = []
        for i in range(len(dates_day)):
            date_day = dates_day[i]
            number_points_month = len(dates_month[dates_month < date_day])
            number_points_day = len(dates_day[dates_day >= date_day])
            ratio = number_points_month / number_points_day
            ratios.append(ratio)
        ratio_points_month_day = min(ratios, key=lambda x: abs(x - self.settings.ratio_points_month_day))
        i = ratios.index(ratio_points_month_day)
        number_points_month = len(dates_month[dates_month < dates_day[i]])
        number_points_day = len(dates_day[dates_day >= dates_day[i]])
        df_month = self._df_month.head(number_points_month)
        df_day = self._df_day.tail(number_points_day)
        self.df = concat(objs=[df_month, df_day],
                         axis='index',
                         verify_integrity=True)

    def _create_df_result(self):
        last_date = self.df.index[-1]
        forecast_days_number = self.settings.forecast_days_number
        if self.settings.prediction_mode == 'test':
            index = self.df_test.index
        else:
            index = [last_date + datetime.timedelta(days=x) for x in range(1, forecast_days_number + 1)]
        columns = self.df.columns
        self.df_result = DataFrame(index=index, columns=columns)

    @classmethod
    def _calc_cum_prods(cls, df: DataFrame) -> DataFrame:
        df = cls.calc_cum_prod(df, 'oil')
        df = cls.calc_cum_prod(df, 'liq')
        return df

    @staticmethod
    def calc_cum_prod(df: DataFrame, phase: str) -> DataFrame:
        df = df.copy()
        df[f'cum_prod_{phase}'] = cumsum(df[f'prod_{phase}'].to_list())
        return df
