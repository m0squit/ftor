import pathlib
import pandas as pd


class DataMonthFact(object):

    _directory_data = pathlib.Path.cwd().parent / 'data' / 'fact'
    _nrows_max = 1e5

    def __init__(self,
                 name_well):
        self.name_well = name_well
        
        self.dates = []
        self.watercuts = []
        self.cumulative_productions_oil = []
        self._productions_oil = []
        self._productions_liquid = []

    def _read_data(self):
        io = self._directory_data / f'{self.name_well}_month.xlsx'
        data = pd.read_excel(io=io,
                             sheet_name='data',
                             header=0,
                             usecols=[0, 20, 21],
                             skiprows=2,
                             nrows=self._nrows_max)

        data.drop(labels=[0, 1], axis='index', inplace=True)
        data.dropna(axis='index', how='any', inplace=True)
        data.sort_values(by='Дата',
                         axis='columns',
                         ascending=True,
                         inplace=True,
                         ignore_index=True)

        self.dates = data['Дата']
        self._productions_oil = data['Добыча нефти (объем)']
        self._productions_liquid = data['Добыча жидкости']

data_month_fact = DataMonthFact()
