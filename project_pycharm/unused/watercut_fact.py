import pandas as pd


class WatercutFact(object):

    def __init__(self,
                 file_excel_name):
        self._file_excel_name = file_excel_name
        self._read_excel_data()
        self._prepare_data()

    def _read_excel_data(self):
        io = f'{self._file_excel_name}.xlsx'
        data = pd.read_excel(io=io,
                             sheet_name='data',
                             header=0,
                             usecols=[6, 7, 8],
                             skiprows=1,
                             nrows=2168)
        data.drop(labels=0,
                  axis='index',
                  inplace=True)
        self.times = data['Elapsed time'].tolist()
        self.times_count = len(self.times)
        self._productions_oil = data['prod_o'].tolist()
        self._productions_liquid = data['prod_l'].tolist()

    def _prepare_data(self):
        cumulative_productions_oil = []
        watercuts = []
        for i in range(self.times_count):
            cumulative_production_oil = sum(self._productions_oil[:i + 1])
            production_water = self._productions_liquid[i] - self._productions_oil[i]
            watercut = production_water / self._productions_liquid[i]
            cumulative_productions_oil.append(cumulative_production_oil)
            watercuts.append(watercut)
        self.cumulative_productions_oil = cumulative_productions_oil
        self.watercuts = watercuts
