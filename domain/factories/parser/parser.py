from pathlib import Path

from pandas import DataFrame

from domain.factories.input_data import InputData
from domain.factories.parser.handler import Handler
from domain.factories.parser.reader.csv import CsvReader
from domain.factories.parser.reader.excel import ExcelReader


class Parser(object):

    _df_month: DataFrame
    _df_day: DataFrame
    _input_data: InputData

    @classmethod
    def run(cls, path: Path) -> InputData:
        cls._read(path)
        cls._create_input_data()
        return cls._input_data

    @classmethod
    def _read(cls, path: Path):
        cls._df_month = ExcelReader().run_specific(path / 'month.xlsx', usecols=[0, 1, 20, 21], skiprows=5)
        cls._df_day = CsvReader().run_specific(path / 'day_new.csv', usecols=[1, 0, 35, 32], skiprows=1)

    @classmethod
    def _create_input_data(cls):
        cls._input_data = InputData()
        names_wells = cls._df_month['well'].unique()
        # TODO: Delete 33-35 rows. It is only for tested otdelnoe field case.
        names_wells = [name_well.replace('Г', '') for name_well in names_wells]
        names_wells.remove('7')
        # names_wells = ['1']
        for name_well in names_wells:
            cls._cut_well(name_well)

    @classmethod
    def _cut_well(cls, name_well):
        data = {}
        df_month = cls._df_month[cls._df_month['well'] == f'{name_well}Г']
        df_month = Handler.run(df_month, df_type='month')

        df_day = cls._df_day[cls._df_day['well'] == name_well]
        # TODO: Change density value for specific oil field. 0.858 for Kholmogorskoe, 0.849 for Otdelnoe.
        density = 0.849
        df_day = cls._convert_prod_oil_units(df_day, density)
        df_day = Handler.run(df_day, df_type='day')

        data['df_month'] = df_month
        data['df_day'] = df_day

        cls._input_data.add_well(name_well, data)

    @staticmethod
    def _convert_prod_oil_units(df, density):
        df = df.assign(prod_oil=lambda x: x.prod_oil / density)
        return df
