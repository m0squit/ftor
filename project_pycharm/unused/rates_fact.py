import pandas as pd


class RatesFact(object):

    def __init__(self,
                 file_excel_name):
        self._file_excel_name = file_excel_name
        self._read_excel_data()

    def _read_excel_data(self):
        io = f'{self._file_excel_name}.xlsx'
        data = pd.read_excel(io=io,
                             sheet_name='data',
                             header=0,
                             usecols=[1, 2, 4],
                             skiprows=1,
                             nrows=2168)
        data.drop(labels=0,
                  axis='index',
                  inplace=True)
        self.times = data['Elapsed time'].tolist()
        self.times_count = len(self.times)
        self.rates_oil = data['qo'].tolist()
        self.rates_liquid = data['ql'].tolist()
