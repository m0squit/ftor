import pandas as pd


class Report(object):

    def __init__(self,
                 df_flux: pd.DataFrame,
                 df_flood: pd.DataFrame):

        self.df_flux = df_flux
        self.df_flood = df_flood
        self.df_result = pd.DataFrame()
        self.mae_train = 0
        self.mae_test = 0

    def prepare(self):
        self.df_result = self.df_flood.loc['test'].copy()
        columns = ['prod_oil_model',
                   'prod_liq_model',
                   'watercut_model',
                   'cum_oil_model',
                   'cum_liq_model',
                   'dev_rel_rate_oil',
                   'dev_abs_cum_oil']
        self.df_result.reindex(columns)
