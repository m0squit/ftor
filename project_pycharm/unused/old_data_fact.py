import pandas as pd
import scipy.integrate as integrate


class DataFact(object):
    """Класс описывает фактические данные.

    Attributes:
        times (list(float)): Временной ряд, hr.
        points_count (float): Длина временного ряда.
        rates_oil (list(float)): Дебит нефти на каждый момент времени, m3/day.
        rates_water (list(float)): Дебит воды на каждый момент времени, m3/day.
        rates_liquid (list(float)): Дебит жидкости на каждый момент времени, m3/day.
        watercuts (list(float)): Обводненность продукции скважины на каждый момент времени, fr.
        cumulative_productions_oil (list(float)): Накопленная добыча нефти на каждый момент времени, m3.
        cumulative_productions_liquid (list(float)): Накопленная добыча жидкости на каждый момент времени, m3.
        recovery_factors (list(float)): КИН на каждый момент времени, fr.
        stoiip (float): Объем начальных извлекаемых запасов нефти, m3.
        file_name (str): Название файла с фактическими данными.

    """

    times = []
    points_count = None
    rates_oil = []
    rates_water = []
    rates_liquid = []
    watercuts = []
    cumulative_productions_oil = []
    cumulative_productions_liquid = []
    stoiip = None
    recovery_factors = []

    def __init__(self,
                 file_name):
        self.file_name = file_name

    @classmethod
    def convert_rate_units(cls, rates):
        return map(lambda x: x / 24, rates)

    def calc_data(self):
        self._read_data()
        self._prepare_data()

    def _read_data(self):
        io = f'{self.file_name}.xlsx'
        data = pd.read_excel(io=io,
                             sheet_name='data',
                             header=0,
                             usecols=[1, 2, 4, 6, 7],
                             skiprows=1,
                             nrows=2168)
        data.drop(labels=0,
                  axis='index',
                  inplace=True)
        self.times = data['Elapsed time'].tolist()
        self.points_count = len(self.times)
        self.rates_oil = data['qo'].tolist()
        self.rates_water = data['qw'].tolist()
        self.stoiip = pd.read_excel(io=io,
                                    sheet_name='data',
                                    header=None,
                                    usecols=[3],
                                    nrows=1)[3][0]

    def _prepare_data(self):
        for i in range(self.points_count):

            # Расчет дебита жидкости и обводненности
            rate_oil = self.rates_oil[i]
            rate_water = self.rates_water[i]
            rate_liquid = rate_oil + rate_water
            watercut = rate_water / rate_liquid
            self.rates_liquid.append(rate_liquid)
            self.watercuts.append(watercut)

            # Расчет накопленной добычи нефти и накопленной добычи жидкости
            times = self.times[:i + 1]
            rates_oil = self.rates_oil[:i + 1]
            rates_oil = self.convert_rate_units(rates_oil)
            rates_liquid = self.rates_liquid
            rates_liquid = self.convert_rate_units(rates_liquid)
            cumulative_production_oil = integrate.simps(rates_oil, times)
            cumulative_production_liquid = integrate.simps(rates_liquid, times)
            self.cumulative_productions_oil.append(cumulative_production_oil)
            self.cumulative_productions_liquid.append(cumulative_production_liquid)

            # Расчет КИН
            stoiip = self.stoiip
            recovery_factor = cumulative_production_oil / stoiip
            self.recovery_factors.append(recovery_factor)
