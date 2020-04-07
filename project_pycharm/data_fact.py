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
                 month_day_ratio):
        self.path_data = self._path_data / f'{name_field}' / f'{name_well}.xlsx'
        self.month_day_points_ratio = month_day_ratio
        self.df = None
        self.df_month = None
        self.df_day = None
        self.df_month_count = None
        self.df_day_count = None
        self._prepare_data()

    def _prepare_data(self):
        self._read_data()
        self._combine_month_day_dataframes()
        self._function()

    def _read_data(self):
        self.df_month = self._read_excel(sheet_name='month', usecols=[0, 20, 21], skiprows=2, indexes_drop=[0, 1])
        self.df_day = self._read_excel(sheet_name='day', usecols=[2, 8, 11], skiprows=2, indexes_drop=[None])
        self.df_month_count = len(self.df_month.index)
        self.df_day_count = len(self.df_day.index)

    def _read_excel(self, sheet_name, usecols, skiprows, indexes_drop):
        """Reads excel file and returns final data as dataframe.

        Args:
            usecols: A list of integers representing column numbers of excel table.
                First integer must be column number of time.
                Column numeration starts from zero.
            indexes_drop: A list of integers representing index numbers of excel table.
                Index numerations starts from zero.
        """
        io = self.path_data
        df = pd.read_excel(io=io,
                           sheet_name=sheet_name,
                           header=0,
                           usecols=usecols,
                           skiprows=skiprows,
                           nrows=self._nrows_max)

        # We prepare dataframe.
        df.drop(index=indexes_drop, inplace=True, errors='ignore')
        df.dropna(axis='index', how='any', inplace=True)
        df['Дата'] = df['Дата'].apply(func=self._convert_date_from_string)
        df.sort_values(by='Дата', axis='index', ascending=True, inplace=True, ignore_index=True)
        df.set_index(keys=['Дата', df.index], drop=True, inplace=True, verify_integrity=True)
        df = df.sum(axis='index', level='Дата')
        return df

    def _combine_month_day_dataframes(self):
        x_min = 0
        x_max = self.df_day_count
        solution = optimize.differential_evolution(func=self._target_function, bounds=[(x_min, x_max)]).x
        number_points_day = round(solution)
        number_points_month = round(number_points_day * self.month_day_points_ratio)
        index_end_month = number_points_month
        index_start_day = self.df_day_count - number_points_day
        df_month = self.df_month.iloc[:index_end_month]
        df_day = self.df_day.iloc[index_start_day:]

    def _target_function(self, number_points_day):
        number_points_day = round(number_points_day)
        row_month = round(number_points_day * self.month_day_points_ratio)
        row_day = self.df_day_count - number_points_day
        error = self.df_month['Дата'][row_month].month - self.df_day['Дата'][row_day].month
        return error
 
    def _function(self):
        pass
        # df['production_cumulative_oil'] = 0
        # df['watercut'] = 0
        # for i in df.index:
        #     production_oil = df['Добыча нефти (объем)'][i]
        #     production_liquid = df['Добыча жидкости'][i]
        #     df['production_cumulative_oil'][i] += production_oil
        #     df['watercut'][i] = (production_liquid - production_oil) / production_liquid

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
