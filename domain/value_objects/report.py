import datetime
from numpy import cumsum
from pandas import DataFrame, concat


class Report(object):

    def __init__(self,
                 df_train,
                 df_test):

        self.df_train = df_train
        self.df_test = df_test
