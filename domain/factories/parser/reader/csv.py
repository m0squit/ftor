import pandas as pd

from domain.factories.parser.reader._reader import _Reader


class CsvReader(_Reader):

    @classmethod
    def _read(cls):
        cls._df = pd.read_csv(filepath_or_buffer=cls._path,
                              sep=';',
                              header=None,
                              usecols=cls._usecols,
                              skiprows=cls._skiprows,
                              nrows=cls._nrows_max,
                              na_values=0,
                              parse_dates=[1],
                              dayfirst=True,
                              encoding='windows-1251')

    @classmethod
    def _process(cls):
        super()._process()
        cls._df.columns = ['date', 'well', 'prod_oil', 'prod_liq', 'bhp']
