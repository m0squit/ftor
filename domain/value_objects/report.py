import pandas as pd


class Report(object):

    def __init__(self,
                 df_flux: pd.DataFrame,
                 df_flood: pd.DataFrame):

        self.df_flux = df_flux
        self.df_flood = df_flood
