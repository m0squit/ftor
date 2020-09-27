from pathlib import Path
from typing import List

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
        cls._df_day = CsvReader().run_specific(path / 'day.csv', usecols=[1, 0, 35, 32], skiprows=1)

    @classmethod
    def _define_well_names(cls) -> List:
        # TODO: Delete some rows. In this form it is work only for Otdelnoe field case.
        cls._df_month['well'] = cls._df_month['well'].apply(lambda x: x.replace('Г', ''))
        well_names = cls._df_month['well'].unique().tolist()
        well_names.remove('7')
        well_names = ['1']
        return well_names

    @classmethod
    def _create_input_data(cls):
        cls._input_data = InputData()
        well_names = cls._define_well_names()
        for well_name in well_names:
            cls._cut_well(well_name)

    @classmethod
    def _cut_well(cls, well_name: str):
        # TODO: Change density value for specific oil field. 0.858 for Kholmogorskoe, 0.849 for Otdelnoe.
        density = 0.849

        df_month = cls._df_month[cls._df_month['well'] == f'{well_name}']
        df_day = cls._df_day[cls._df_day['well'] == well_name]
        df_day = cls._convert_prod_oil_units(df_day, density)
        df_month = Handler.run(df_month, df_type='month')
        df_day = Handler.run(df_day, df_type='day')
        well_data = {'df_month': df_month, 'df_day': df_day}
        cls._input_data.add_well(well_name, well_data)

    @staticmethod
    def _convert_prod_oil_units(df, density):
        df = df.assign(prod_oil=lambda x: x.prod_oil / density)
        return df
