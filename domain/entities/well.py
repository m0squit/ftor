from domain.value_objects.report import Report
from libs.flood.corey.model import CoreyModel
from libs.numeric_tools.loss_function import LossFunction


class Well(object):

    def __init__(self,
                 name: str,
                 report: Report):

        self.name = name
        self.report = report
        self._create_flood_model()

    def calc(self):
        self._predict_rate_oil()
        self._calc_metric()

    def _create_flood_model(self):
        cum_prods_oil = self.report.df_train['cum_prod_oil'].to_list()
        watercuts = self.report.df_train['watercut'].to_list()
        self.flood_model = CoreyModel(cum_prods_oil, watercuts)

    def _predict_rate_oil(self):
        cum_prod_oil_start = self.report.df_train['cum_prod_oil'].iloc[-1]
        cum_prod_liq_start = self.report.df_train['cum_prod_liq'].iloc[-1]
        rates_liq = self.report.df_test['prod_liq'].to_list()
        result = self.flood_model.predict(cum_prod_oil_start, cum_prod_liq_start, rates_liq)
        self.report.df_test = self.report.df_test.assign(watercut_model=result['watercut'])
        self.report.df_test = self.report.df_test.assign(prod_oil_model=result['rate_oil'])

    def _calc_metric(self):
        self._calc_metric_watercut()
        self._calc_metric_prod()

    def _calc_metric_watercut(self):
        watercuts_fact = self.report.df_test['watercut']
        watercuts_model = self.report.df_test['watercut_model']
        self.flood_model.mae_test = LossFunction.run(watercuts_fact, watercuts_model)

    def _calc_metric_prod(self):
        self.report.df_test['dev_rel_rate_oil'] = None
        self.report.df_test['dev_abs_cum_oil'] = None
        for i in self.report.df_test.index:
            prod_oil_fact = self.report.df_test.loc[i, 'prod_oil']
            prod_oil_model = self.report.df_test.loc[i, 'prod_oil_model']
            term_1 = abs(prod_oil_fact - prod_oil_model)
            term_2 = max(prod_oil_fact, prod_oil_model)
            self.report.df_test.loc[i, 'dev_rel_rate_oil'] = term_1 / term_2
            self.report.df_test.loc[i, 'dev_abs_cum_oil'] = prod_oil_fact - prod_oil_model

        self.report.df_test['dev_abs_cum_oil'] = self.report.df_test['dev_abs_cum_oil'].cumsum()
