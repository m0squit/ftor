import pathlib
import pandas as pd
import datetime
import calendar
import math
import scipy.optimize as optimize


class DataFact(object):

    _path_data = pathlib.Path.cwd().parent / 'data' / 'fact'
    _nrows_max = 1e5

    def __init__(self,
                 name_field,
                 name_well,
                 ratio_points_month_day):
        self.path_data = self._path_data / f'{name_field}' / f'{name_well}.xlsx'
        self.ratio_points_month_day = ratio_points_month_day
        self.df = None
        self.df_month = None
        self.df_day = None
        self.df_month_count = None
        self.df_day_count = None
        self._prepare_data()

    def _prepare_data(self):
        self._read_data()
        self._combine_month_day_dataframes()
        self._calc_watercut()

    def _read_data(self):
        self.df_month = self._read_excel(sheet_name='month', usecols=[0, 20, 21], skiprows=3, indexes_drop=[0, 1])
        self.df_day = self._read_excel(sheet_name='day', usecols=[2, 11, 8], skiprows=3, indexes_drop=[None])
        self.df_month_count = len(self.df_month.index)
        self.df_day_count = len(self.df_day.index)

    def _read_excel(self, sheet_name, usecols, skiprows, indexes_drop):
        """Reads excel file and returns final data as dataframe.

        Args:
            usecols: A list of integers representing column numbers of excel table.
                First integer must be column number of time.
                Second - column number of oil production.
                Third - column number of liquid production.
                Column numeration starts from zero.
            indexes_drop: A list of integers representing index numbers of excel table.
                Index numerations starts from zero.
        """
        io = self.path_data
        df = pd.read_excel(io=io,
                           sheet_name=sheet_name,
                           header=None,
                           usecols=usecols,
                           skiprows=skiprows,
                           nrows=self._nrows_max,
                           na_values=0)
        # We prepare dataframe.
        df = df[usecols]
        df.columns = ['date', 'production_oil', 'production_liquid']
        df.drop(index=indexes_drop, inplace=True, errors='ignore')
        df.dropna(axis='index', how='any', inplace=True)
        df['date'] = df['date'].apply(func=self._convert_date_from_string)
        df.sort_values(by='date', axis='index', ascending=True, inplace=True, ignore_index=True)
        df.set_index(keys=['date', df.index], drop=True, inplace=True, verify_integrity=True)
        df = df.sum(axis='index', level='date')
        return df

    def _combine_month_day_dataframes(self):
        dates_month = self.df_month.index
        dates_day = self.df_day.index
        ratios = []
        for i in range(len(dates_day)):
            date_day = dates_day[i]
            number_points_month = len(dates_month[dates_month < date_day])
            number_points_day = len(dates_day[dates_day >= date_day])
            ratio = number_points_month / number_points_day
            ratios.append(ratio)
        ratio_points_month_day = min(ratios, key=lambda x: abs(x - self.ratio_points_month_day))
        i = ratios.index(ratio_points_month_day)
        number_points_month = len(dates_month[dates_month < dates_day[i]])
        number_points_day = len(dates_day[dates_day >= dates_day[i]])
        df_month = self.df_month.head(number_points_month)
        df_day = self.df_day.tail(number_points_day)
        self.df = pd.concat(objs=[df_month, df_day],
                            axis='index',
                            keys=['month', 'day'],
                            names=['level_date', 'date'],
                            verify_integrity=True)

    def _calc_watercut(self):
        df = self.df.drop(columns='production_liquid')
        df = df.cumsum(axis='index')
        df['watercut'] = 0
        for i in self.df.index:
            production_oil = self.df['production_oil'][i]
            production_liquid = self.df['production_liquid'][i]
            df.loc[i, 'watercut'] = (production_liquid - production_oil) / production_liquid
        self.df = df
        print(self.df)

    @staticmethod
    def _convert_date_from_string(x):
        if type(x) is not str:
            return x
        format_date = '%m.%Y'
        date = datetime.datetime.strptime(x, format_date)
        day_last = calendar.monthrange(date.year, date.month)[1]  # A last day of the date month.
        date = date.replace(day=day_last)
        return date


DataFact('kholmogorskoe', '2276_116', 0.3)
