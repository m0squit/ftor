import pandas as pd
import datetime
import calendar
import math
import scipy.optimize as optimize


io = '2276_116.xlsx'
nrows_max = 1e5


def convert_date_from_string(x):
    if type(x) is not str:
        return x
    format_date = '%m.%Y'
    date = datetime.datetime.strptime(x, format_date)
    day_last = calendar.monthrange(date.year, date.month)[1]  # A last day of the date month.
    date = date.replace(day=day_last)
    return date


def read_excel(sheet_name, usecols, skiprows, indexes_drop):
    """Reads excel file and returns final data as dataframe.

    Args:
        usecols: A list of integers representing column numbers of excel table.
            First integer must be column number of time.
            Column numeration starts from zero.
        indexes_drop: A list of integers representing index numbers of excel table.
            Index numerations starts from zero.
    """
    df = pd.read_excel(io=io,
                       sheet_name=sheet_name,
                       header=0,
                       usecols=usecols,
                       skiprows=skiprows,
                       nrows=nrows_max)

    # We prepare dataframe.
    df.drop(index=indexes_drop, inplace=True, errors='ignore')
    df.dropna(axis='index', how='any', inplace=True)
    df['Дата'] = df['Дата'].apply(func=convert_date_from_string)
    df.sort_values(by='Дата', axis='index', ascending=True, inplace=True, ignore_index=True)
    df.set_index(keys=['Дата', df.index], drop=True, inplace=True, verify_integrity=True)
    df = df.sum(axis='index', level='Дата')
    return df


def combine_dataframes(df_month, df_day):
    month_day_ratio = 0.3  # A ratio of points number from month and day dataframes.
    df_day_count = len(df_day.index)

    def target_function(y):
        row_month = round(y * month_day_ratio)
        row_day = round(df_day_count - y)
        q = df_month['Дата'][row_month].month is df_day['Дата'][row_day].month
        if q is True:
            return 0
        return 1e3

    min = 2
    max = df_day_count - 2
    y = round(optimize.differential_evolution(func=target_function, bounds=(min, max)).x)
    return y


def read_data():
    df_month = read_excel(sheet_name='month', usecols=[0, 20, 21], skiprows=2, indexes_drop=[0, 1])
    df_day = read_excel(sheet_name='day', usecols=[2, 8, 11], skiprows=2, indexes_drop=[None])
    df = combine_dataframes(df_month, df_day)

    # df['production_cumulative_oil'] = 0
    # df['watercut'] = 0
    # for i in df.index:
    #     production_oil = df['Добыча нефти (объем)'][i]
    #     production_liquid = df['Добыча жидкости'][i]
    #     df['production_cumulative_oil'][i] += production_oil
    #     df['watercut'][i] = (production_liquid - production_oil) / production_liquid

    return df


print(read_data())
