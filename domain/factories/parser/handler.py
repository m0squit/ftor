from pandas import DataFrame


class Handler(object):

    _df: DataFrame

    @classmethod
    def run(cls, df: DataFrame) -> DataFrame:
        cls._df = df.copy()
        cls._process()
        cls._calc_watercut()
        return cls._df

    @classmethod
    def _process(cls):
        cls._df.drop(columns=['well'], inplace=True)
        cls._df.dropna(axis='index', how='any', inplace=True)
        cls._df.set_index(keys=['date', cls._df.index], drop=True, inplace=True, verify_integrity=True)
        cls._df = cls._df.sum(axis='index', level='date')

    @classmethod
    def _calc_watercut(cls):
        cls._df['watercut'] = None
        for i in cls._df.index:
            prod_oil = cls._df.loc[i, 'prod_oil']
            prod_liq = cls._df.loc[i, 'prod_liq']
            cls._df.loc[i, 'watercut'] = (prod_liq - prod_oil) / prod_liq
        cls._drop_zero_watercut()

    @classmethod
    def _drop_zero_watercut(cls):
        indexes_to_drop = cls._df[cls._df['watercut'] == 0].index
        cls._df.drop(index=indexes_to_drop, inplace=True)
