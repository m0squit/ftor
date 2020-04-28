import pandas as pd


class Report(object):

    def __init__(self,
                 df_flux: pd.DataFrame,
                 df_flood: pd.DataFrame):

        self.df_flux = df_flux
        self.df_flood = df_flood
        self.mae_train: float = 0.0
        self.mae_test: float = 0.0

    def prepare(self, mode):
        pass
