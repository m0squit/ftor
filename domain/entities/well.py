from domain.value_objects.report import Report
from libs.flood.corey.model import CoreyModel
from libs.numeric_tools.loss_function import LossFunction


class Well(object):

    def __init__(self,
                 name: str,
                 # radius: float,
                 # formation: Formation,
                 report: Report):

        self.name = name
        # self.radius = radius
        # self.formation = Formation
        self.report = report
        self._create_flood_model()

    def calc(self):
        self._predict_rate_liquid()
        self._predict_rate_oil()
        self._calc_metric()

    def _create_flood_model(self):
        report = self.report
        cum_prods_oil = report.df['cum_prod_oil'].to_list()
        watercuts = report.df['watercut'].to_list()
        self.flood_model = CoreyModel(cum_prods_oil, watercuts)

    def _predict_rate_liquid(self):
        # TODO: Write code about liquid prediction using flux lib.
        report = self.report
        report.df_result['prod_oil'] = report.df_test['prod_liq']
        report.df_result = report.calc_cum_prod(report.df_result, phase='liq')

    def _predict_rate_oil(self):
        report = self.report
        cum_prod_oil_start = report.cum_prod_oil
        cum_prod_liq_start = report.cum_prod_liq
        rates_liq = report.df_result['prod_liq']
        result = self.flood_model.predict(cum_prod_oil_start, cum_prod_liq_start, rates_liq)
        report.df_result['watercut'] = result['watercut']
        report.df_result['rate_oil'] = result['rate_oil']
        report.df_result = report.calc_cum_prod(report.df_result, phase='oil')

    def _calc_metric(self):
        if self.report.settings.prediction_mode == 'test':
            watercuts_fact = self.report.df_test['watercut']
            watercuts_model = self.report.df_result['watercut']
            self.flood_model.mae_test = LossFunction.run(watercuts_fact, watercuts_model)
            self.report.calc_metric()
