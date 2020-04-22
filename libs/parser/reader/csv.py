import pandas as pd

from libs.parser.reader._reader import _Reader


class CsvReader(_Reader):

    @classmethod
    def _read(cls):
        cls._df = pd.read_csv(filepath_or_buffer=cls._path,
                              header=None,
                              usecols=cls._usecols,
                              skiprows=cls._skiprows,
                              nrows=cls._nrows_max,
                              na_values=0)

    @classmethod
    def _process(cls):
        super()._process()
        cls._df.columns = ['date', 'well', 'prod_oil', 'prod_liq', 'bhp']
