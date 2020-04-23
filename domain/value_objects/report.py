import pandas as pd


class Report(object):

    def __init__(self,
                 data_rate: pd.DataFrame,
                 data_production: pd.DataFrame):

        self.data_rate = data_rate
        self.data_production = data_production
