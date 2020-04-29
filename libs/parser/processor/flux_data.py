import pandas as pd


class FluxData(object):

    def __init__(self,
                 df: pd.DataFrame):

        self.df = df.copy()
        self._create()

    def _create(self):
        self._prepare()

    def _prepare(self):
        self.df.drop(columns=['well'], inplace=True)
        self.df.dropna(axis='index', how='any', inplace=True)
        self.df.drop_duplicates(subset='date', inplace=True)
        self.df.set_index(keys='date', inplace=True, verify_integrity=True)
