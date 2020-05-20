from pathlib import Path
from typing import Dict

from pandas import DataFrame

from domain.factories.input_data import InputData
from domain.factories.parser.handler import Handler
from domain.factories.parser.reader.csv import CsvReader
from domain.factories.parser.reader.excel import ExcelReader


class Parser(object):

    _df_month: DataFrame
    _df_day: DataFrame
    _formations_porosities: Dict[str, float]
    _input_data: InputData

    @classmethod
    def run(cls, path: Path) -> InputData:
        cls._read(path)
        cls._create_input_data()
        return cls._input_data

    @classmethod
    def _read(cls, path: Path):
        cls._df_month = ExcelReader().run_specific(path / 'month.xlsx', usecols=[0, 1, 20, 21, 2], skiprows=5)
        cls._df_day = CsvReader().run_specific(path / 'day.csv', usecols=[1, 0, 4, 3, 2], skiprows=1)

    @classmethod
    def _create_input_data(cls):
        cls._parse_porosity()
        cls._create()

    @classmethod
    def _parse_porosity(cls):
        # TODO: Find all formations names in "month.xlsx".
        #  But maybe this file not contain info about it.
        #  Fetch porosity values for each formation from file "Печать...".
        #  Write formation name - porosity pairs to cls._formations_porosities.
        pass

    @classmethod
    def _create(cls):
        cls._input_data = InputData()
        names_wells = cls._df_month['well'].unique()
        names_wells = ['232']
        for name_well in names_wells:
            cls._cut_well(name_well)

    @classmethod
    def _cut_well(cls, name_well):
        data = {}

        # TODO: Fetch radius value for this well from file "Техрежим...".
        #  Write radius to data['radius'].

        df_month = cls._df_month[cls._df_month['well'] == name_well]
        df_month = Handler.run(df_month)

        # TODO: Define formations names for this well in df_month.
        #  But maybe this df not contain info about it.
        #  Write all formations names to data['formations_names'] as one string.
        #  Write average porosity for all well formations to data['porosity'].
        # df_month.drop(columns=['formation'], inplace=True)

        # TODO: Fetch average thickness, density, viscosity, volume_factor, type of completion values
        #  for well formations from file "Техрежим...".
        #  Write each parameter to data.

        density = 0.858
        df_day = cls._df_day[cls._df_day['well'] == name_well]
        df_day = cls._convert_prod_oil_units(df_day, density)
        df_day = Handler.run(df_day)

        data['df_month'] = df_month
        data['df_day'] = df_day

        # TODO: Where are get compressibility and type of boundaries ?
        #  Write it to data.

        cls._input_data.add_well(name_well, data)

    @staticmethod
    def _convert_prod_oil_units(df, density):
        df = df.assign(prod_oil=lambda x: x.prod_oil / density)
        return df
