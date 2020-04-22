from libs.parser.processor.flood_data import FloodData
from libs.parser.processor.flux_data import FluxData
from libs.parser.reader.csv import CsvReader
from libs.parser.reader.excel import ExcelReader


class Calculator(object):

    _df_month = None
    _df_day = None

    _df_m_w = None
    _df_d_w = None

    _df_m_w_f = None
    _df_d_w_f = None

    _formations = None
    _wells = None
    _data = None

    @classmethod
    def run(cls, path):
        cls._read(path)
        cls._create()
        cls._fill_data()
        return {'formations': cls._formations,
                'wells': cls._wells,
                'data': cls._data}

    @classmethod
    def _read(cls, path):
        path_month = path / 'month.xlsx'
        path_day = path / 'day.csv'
        cls._df_month = ExcelReader().run_specific(path_month, usecols=[0, 1, 21, 22, 2], skiprows=5)
        cls._df_day = CsvReader().run_specific(path_day, usecols=[1, 0, 3, 4, 2], skiprows=1)

    @classmethod
    def _create(cls):
        cls._formations = cls._df_month['formation'].unique()
        cls._wells = cls._df_month['well'].unique()
        cls._data = dict.fromkeys(cls._wells)

    @classmethod
    def _fill_data(cls):
        for well in cls._wells:
            cls._cut_well(well)
            formations = cls._df_m_w['formation'].unique()
            cls._data[well] = dict.fromkeys(formations)

            for formation in formations:
                cls._cut_formation(formation)
                cls._data[well][formation] = dict.fromkeys(['flood_data', 'flux_data'])
                df_month = cls._df_m_w_f
                df_day = cls._df_d_w_f
                flood_data = FloodData(df_month, df_day)
                flux_data = FluxData(df_day)
                cls._data[well][formation]['flood_data'] = flood_data
                cls._data[well][formation]['flux_data'] = flux_data

    @classmethod
    def _cut_well(cls, well):
        cls._df_m_w = cls._df_month[cls._df_month['well'] == well]
        cls._df_d_w = cls._df_day[cls._df_day['well'] == well]

    @classmethod
    def _cut_formation(cls, formation):
        cls._df_m_w_f = cls._df_m_w[cls._df_m_w['formation'] == formation]
        cls._df_d_w_f = cls._df_d_w
