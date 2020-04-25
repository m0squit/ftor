class FluxData(object):

    def __init__(self,
                 df):

        self.df = df
        self._create()

    def _create(self):
        self._prepare()
        return self.df

    def _prepare(self):
        self.df = self.df.drop(columns=['well'])
        self.df = self.df.dropna(axis='index', how='any')
        self.df = self.df.drop_duplicates(subset='date')
        self.df = self.df.set_index(keys='date', verify_integrity=True)
