import calendar
import datetime

import pandas as pd
import scipy.integrate as integrate


class Reader(object):

    _path = None
    _nrows_max = None
    _ratio_points_month_day = None
    _data = None

    @classmethod
    def run(cls, path, nrows_max=1e5, ratio_points_month_day=0.5):
        cls._path = path
        cls._nrows_max = nrows_max
        cls._ratio_points_month_day = ratio_points_month_day

        df_m = cls._read_month()
        df_d = cls._read_day()

        wells = df_m['well'].unique()
        cls._data = dict.fromkeys(wells)
        for well in wells:
            df_m_w = df_m[df_m['well'] == well]
            df_d_w = df_d[df_d['well'] == well]

            formations = df_m_w['formation'].unique()
            cls._data[well] = dict.fromkeys(formations)
            for formation in formations:
                df_m_w_f = df_m_w[df_m_w['formation'] == formation]
                df_m_w_f = cls._prepare_df_month(df_m_w_f)

                df_d_w_f = df_d_w

                cls._data[well][formations] = dict.fromkeys(['df_rate', 'df_production'])
                cls._create_df_rate(well, formation, df_d_w_f)
                cls._create_df_production(well, formation, df_m_w_f, df_d_w_f)

    @classmethod
    def _read_month(cls):
        path = cls._path / 'month.xlsx'
        df = cls._read(path=path, usecols=[0, 1, 21, 22, 2], skiprows=5)
        df.columns = ['date', 'well', 'prod_oil', 'prod_liq', 'formation']
        return df

    @classmethod
    def _read_day(cls):
        path = cls._path / 'day.csv'
        df = cls._read(path=path, usecols=[1, 0, 3, 4, 2], skiprows=1)
        df.columns = ['date', 'well', 'prod_oil', 'prod_liq', 'bhp']
        return df

    @classmethod
    def _read(cls, path, usecols, skiprows):
        """Reads excel file and returns final data as dataframe.

        Args:
            usecols: A list of integers representing column numbers of excel table.
                First integer must be column number of time.
                Second - column number of well name.
                Third - column number of oil production.
                Fourth - column number of liquid production.
                Fifth - column number of formation name / bhp.
                Column numeration starts from zero.
        """
        df = pd.read_table(filepath_or_buffer=path,
                           sheet_name=0,
                           header=None,
                           usecols=usecols,
                           engine='python',
                           skiprows=skiprows,
                           nrows=cls._nrows_max,
                           na_values=0)

        # We prepare dataframe.
        df = df[usecols]
        df.rename(columns={0: 'date'}, inplace=True)
        df['date'] = df['date'].apply(func=cls._convert_date_from_string)
        df.sort_values(by='date', axis='index', ascending=True, inplace=True, ignore_index=True)
        return df

    @classmethod
    def _create_df_rate(cls, well, formation, df):
        df.drop(columns=['well'], inplace=True)
        df.dropna(axis='index', how='any', inplace=True)
        df = cls._prepare_df_day(df)
        cls._data[well][formation]['df_rate'] = df

    @classmethod
    def _create_df_production(cls, well, formation, df_m, df_d):
        df = cls._combine_df_m_df_d(df_m, df_d)
        cls._data[well][formation]['df_production'] = df

    @classmethod
    def _combine_df_m_df_d(cls, df_m, df_d):
        ratios = []
        for i in range(len(df_d)):
            df_d = df_d[i]
            number_points_month = len(df_m[df_m < df_d])
            number_points_day = len(df_d[df_d >= df_d])
            ratio = number_points_month / number_points_day
            ratios.append(ratio)

        ratio_points_month_day = min(ratios, key=lambda x: abs(x - cls._ratio_points_month_day))
        i = ratios.index(ratio_points_month_day)
        number_points_month = len(df_m[df_m < df_d[i]])
        number_points_day = len(df_d[df_d >= df_d[i]])

        df_m = df_m.head(number_points_month)
        df_m = cls._calc_watercut_df_m(df_m)
        cumprod_oil = df_m['prod_oil'][-1]
        df_d = df_d.tail(number_points_day)
        df_d = cls._calc_watercut_df_d(df_d, cumprod_oil)
        df = pd.concat(objs=[df_m, df_d],
                       axis='index',
                       keys=['month', 'day'],
                       names=['level_date', 'date'],
                       verify_integrity=True)
        return df

    @staticmethod
    def _convert_date_from_string(x):
        if type(x) is not str:
            return x
        format_date = '%m.%Y'
        date = datetime.datetime.strptime(x, format_date)
        day_last = calendar.monthrange(date.year, date.month)[1]  # A last day of the date month.
        date = date.replace(day=day_last)
        return date

    @staticmethod
    def _prepare_df_month(df):
        df.drop(columns=['well', 'formation'], inplace=True)
        df.dropna(axis='index', how='any', inplace=True)
        df.set_index(keys=['date', df.index], drop=True, inplace=True, verify_integrity=True)
        df = df.sum(axis='index', level='date')
        return df

    @staticmethod
    def _prepare_df_day(df):
        df.drop_duplicates(subset='date', inplace=True)
        df.set_index(keys='date', inplace=True, verify_integrity=True)
        return df

    @staticmethod
    def _calc_watercut_df_m(df):
        df_w = df.drop(columns='prod_liq')
        df_w = df_w.cumsum(axis='index')
        df_w['wc'] = None
        for i in df.index:
            prod_oil = df['prod_oil'][i]
            prod_liq = df['prod_liq'][i]
            df_w.loc[i, 'wc'] = (prod_liq - prod_oil) / prod_liq
        return df_w

    @staticmethod
    def _calc_watercut_df_d(df, cumprod_oil):
        prods = df['prod_oil'].to_list()
        prods.insert(0, 0)
        for i in range(1, len(prods)):
            prods = prods[:i + 1]
            cumprod = integrate.simps(prods, range(i + 1), even='first')
            df['prod_oil'][i] = cumprod
        df['prod_oil'] = df['prod_oil'].apply(lambda x: x + cumprod_oil)
        return df
