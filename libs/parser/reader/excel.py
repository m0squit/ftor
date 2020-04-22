import pandas as pd

from libs.parser.reader._reader import _Reader


class ExcelReader(_Reader):

    @classmethod
    def _read(cls):
        cls._df = pd.read_excel(io=cls._path,
                                sheet_name=0,
                                header=None,
                                usecols=cls._usecols,
                                skiprows=cls._skiprows,
                                nrows=cls._nrows_max,
                                na_values=0)

    @classmethod
    def _process(cls):
        super()._process()
        cls._df.columns = ['date', 'well', 'prod_oil', 'prod_liq', 'formation']
