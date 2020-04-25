from typing import List

from domain.factories.input_data import InputData
from libs.parser.processor.flood_data import FloodData
from libs.parser.processor.flux_data import FluxData
from libs.parser.reader.csv import CsvReader
from libs.parser.reader.excel import ExcelReader


class Parser(object):

    _df_month = None
    _df_day = None

    _df_m_w = None
    _df_d_w = None

    _df_m_w_f = None
    _df_d_w_f = None

    _data = InputData()
    _names_formation: List[str]
    _names_well: List[str]

    @classmethod
    def run(cls, path):
        cls._read(path)
        cls._create()
        return cls._data

    @classmethod
    def _read(cls, path):
        path_month = path / 'month.xlsx'
        path_day = path / 'day.csv'
        cls._df_month = ExcelReader().run_specific(path_month, usecols=[0, 1, 20, 21, 2], skiprows=5)
        cls._df_day = CsvReader().run_specific(path_day, usecols=[1, 0, 4, 3, 2], skiprows=1)

    @classmethod
    def _create(cls):
        cls._create_formations()
        cls._create_wells()
        cls._create_zones()

    @classmethod
    def _create_formations(cls):
        cls._names_formation = cls._df_month['formation'].unique()
        formation_porosity_dict = dict.fromkeys(cls._names_formation)
        # TODO: Fetch porosity values for each formation from file "Печать..." and set in dict below.
        for name_formation in cls._names_formation:
            # TODO: Change loop body.
            if name_formation == 'БС10':
                porosity = 0.2
            else:
                porosity = 0.17
            formation_porosity_dict[name_formation] = porosity
        cls._data.formation_porosity_dict = formation_porosity_dict

    @classmethod
    def _create_wells(cls):
        cls._names_well = cls._df_month['well'].unique()
        well_radius_dict = dict.fromkeys(cls._names_well)
        # TODO: Fetch radius values for each well from file "Техрежим..." and set in dict below.
        for name_well in cls._names_well:
            # TODO: Change loop body.
            radius = 0.1
            well_radius_dict[name_well] = radius
        cls._data.well_radius_dict = well_radius_dict

    @classmethod
    def _create_zones(cls):
        # TODO: Delete temp code row 72 (it is created here to avoid run all wells).
        cls._names_well = ['232']
        zone_dict = dict.fromkeys(cls._names_well)
        # TODO: Fetch density, viscosity, volume_factor, thickness, type of completion values
        #  for each well from file "Техрежим..." and set in dict below.
        #  Where is get type of boundaries ?
        for name_well in cls._names_well:
            cls._cut_well(name_well)
            names_formation_well = cls._df_m_w['formation'].unique()
            zone_dict[name_well] = dict.fromkeys(names_formation_well)

            for name_formation in names_formation_well:
                cls._cut_formation(name_formation)
                zone_dict[name_well][name_formation] = dict.fromkeys(['flood_data', 'flux_data'])
                df_month = cls._df_m_w_f
                df_day = cls._df_d_w_f
                flood_data = FloodData(df_month, df_day)
                flux_data = FluxData(df_day)
                zone_dict[name_well][name_formation]['flood_data'] = flood_data
                zone_dict[name_well][name_formation]['flux_data'] = flux_data
                # TODO: Change code below.
                if name_formation == 'БС10':
                    density = 0.864
                else:
                    density = 0.858
                zone_dict[name_well][name_formation]['density'] = density
                zone_dict[name_well][name_formation]['viscosity'] = 1.5
                zone_dict[name_well][name_formation]['volume_factor'] = 1.1
                zone_dict[name_well][name_formation]['thickness'] = 10
                zone_dict[name_well][name_formation]['type_boundaries'] = 'type'
                zone_dict[name_well][name_formation]['type_completion'] = 'type'
        cls._data.zone_dict = zone_dict

    @classmethod
    def _cut_well(cls, name_well):
        cls._df_m_w = cls._df_month[cls._df_month['well'] == name_well]
        cls._df_d_w = cls._df_day[cls._df_day['well'] == name_well]

    @classmethod
    def _cut_formation(cls, name_formation):
        cls._df_m_w_f = cls._df_m_w[cls._df_m_w['formation'] == name_formation]
        cls._df_d_w_f = cls._df_d_w
