import pathlib
import pandas as pd
import scipy.integrate as integrate


class DataArtificial(object):

    _nrows_max = 1e5

    def __init__(self,
                 name_file_excel):
        self.name_file_excel = name_file_excel

        self.times = []
        self.times_count = None
        self.rates_oil = []
        self.rates_water = []
        self.rates_liquid = []
        self.watercuts = []
        self.stoiip = None
        self.cumulative_productions_oil = []
        self.cumulative_productions_liquid = []
        self.recovery_factors = []
        self._read_data()
        self._prepare_data()

    @staticmethod
    def _convert_rate_units(rates):
        return list(map(lambda x: x / 24, rates))

    def _read_data(self):
        io = pathlib.Path.cwd().parent / 'data' / 'artificial' / f'{self.name_file_excel}.xlsx'
        data = pd.read_excel(io=io,
                             sheet_name='data',
                             header=0,
                             usecols=[1, 2, 3],
                             skiprows=1,
                             nrows=self._nrows_max)
        data.drop(labels=0, axis='index', inplace=True)
        data.dropna(axis='index', how='all', inplace=True)

        self.times = data['Elapsed time'].tolist()
        self.times_count = len(self.times)
        self.rates_oil = data['qo'].tolist()
        self.rates_water = data['qw'].tolist()
        self.stoiip = pd.read_excel(io=io,
                                    sheet_name='data',
                                    header=None,
                                    usecols=[3],
                                    nrows=1)[3][0]

    def _prepare_data(self):
        for i in range(self.times_count):
            # Расчет дебита жидкости и обводненности
            rate_oil = self.rates_oil[i]
            rate_water = self.rates_water[i]
            rate_liquid = rate_oil + rate_water
            watercut = rate_water / rate_liquid
            self.rates_liquid.append(rate_liquid)
            self.watercuts.append(watercut)
            # Расчет накопленной добычи нефти и жидкости
            times = self.times[:i + 1]
            rates_oil = self._convert_rate_units(self.rates_oil[:i + 1])
            rates_liquid = self._convert_rate_units(self.rates_liquid[:i + 1])
            # Добавление начальных значений на момент времени t=0
            times.insert(0, 0)
            rates_oil.insert(0, 0)
            rates_liquid.insert(0, 0)
            cumulative_production_oil = integrate.simps(rates_oil, times, even='first')
            cumulative_production_liquid = integrate.simps(rates_liquid, times, even='first')
            self.cumulative_productions_oil.append(cumulative_production_oil)
            self.cumulative_productions_liquid.append(cumulative_production_liquid)
            # Расчет КИН
            recovery_factor = cumulative_production_oil / self.stoiip
            self.recovery_factors.append(recovery_factor)
