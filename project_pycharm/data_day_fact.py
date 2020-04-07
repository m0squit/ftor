import pathlib
import pandas as pd


class DataDayFact(object):

    def __init__(self,
                 name_well):
        self.name_well = name_well
        self.dates = []
        self.watercuts = {'telemetry': [], 'lab': [], 'volume': []}

    def _read_data_day(self):
        io = self._directory_data / f'{self.name_field_well}_day.xlsx'
        data = pd.read_excel(io=io,
                             sheet_name='data',
                             header=0,
                             usecols=[2, 12, 13, 14],
                             skiprows=1,
                             nrows=self._nrows_max)

        data.drop(labels=0, axis='index', inplace=True)
        data.dropna(axis='index', how='all', inplace=True)
        self.dates_day = data['date']
        self.watercuts_day['telemetry'] = data['wc_telemetry']
        self.watercuts_day['lab'] = data['wc_lab']
        self.watercuts_day['volume'] = data['wc_volume']
