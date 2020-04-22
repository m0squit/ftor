class FluxData(object):

    def __init__(self,
                 df):

        self.df = df

    def create(self):
        self._prepare()
        return self.df

    def _prepare(self):
        self.df.drop(columns=['well'], inplace=True)
        self.df.dropna(axis='index', how='any', inplace=True)
        self.df.drop_duplicates(subset='date', inplace=True)
        self.df.set_index(keys='date', inplace=True, verify_integrity=True)
