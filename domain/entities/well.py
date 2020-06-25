import datetime

from typing import List

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

    def calc(self, rates_liq: List[float]):
        self._predict_rate_oil(rates_liq)
        self._create_df_test_month()
        self._calc_metric()

    def _create_flood_model(self):
        cum_prods_oil = self.report.df_train['cum_prod_oil'].to_list()
        watercuts = self.report.df_train['watercut'].to_list()
        self.flood_model = CoreyModel(cum_prods_oil, watercuts)

    def _predict_rate_oil(self, rates_liq_model: List[float]):
        cum_prod_oil_start = self.report.df_train['cum_prod_oil'].iloc[-1]
        cum_prod_liq_start = self.report.df_train['cum_prod_liq'].iloc[-1]
        self.report.df_test = self.report.df_test.assign(prod_liq_model=rates_liq_model)

        self.report.df_test['cum_liq'] = self.report.df_test['prod_liq'].cumsum()
        self.report.df_test['cum_liq_model'] = self.report.df_test['prod_liq_model'].cumsum()

        result = self.flood_model.predict(cum_prod_oil_start, cum_prod_liq_start, rates_liq_model)
        self.report.df_test = self.report.df_test.assign(watercut_model=result['watercut'])
        self.report.df_test = self.report.df_test.assign(prod_oil_model=result['rate_oil'])

        self.report.df_test['cum_oil'] = self.report.df_test['prod_oil'].cumsum()
        self.report.df_test['cum_oil_model'] = self.report.df_test['prod_oil_model'].cumsum()

    def _create_df_test_month(self):
        first_test_date = self.report.df_test.index[0]
        df_test_month = self.report.df_month.loc[first_test_date:]
        df_test_month = df_test_month.drop(columns='watercut')
        months = [date.month for date in df_test_month.index]
        prods_oil_model = []
        prods_liq_model = []
        for month in months:
            df = self.report.df_test.filter(like=f'-0{month}-', axis='index')
            prod_oil_model = df['prod_oil_model'].sum()
            prod_liq_model = df['prod_liq_model'].sum()
            prods_oil_model.append(prod_oil_model)
            prods_liq_model.append(prod_liq_model)
        df_test_month = df_test_month.assign(prod_oil_model=prods_oil_model)
        df_test_month = df_test_month.assign(prods_liq_model=prods_liq_model)
        self.report.df_test_month = df_test_month

    def _calc_metric(self):
        self._calc_metric_watercut()
        self._calc_metric_prod_phase(phase='liq')
        self._calc_metric_prod_phase(phase='oil')

    def _calc_metric_watercut(self):
        watercuts_fact = self.report.df_test['watercut'].to_list()
        watercuts_model = self.report.df_test['watercut_model'].to_list()
        self.flood_model.mae_test = LossFunction.run(watercuts_fact, watercuts_model)

    def _calc_metric_prod_phase(self, phase: str):
        self.report.df_test[f'dev_abs_rate_{phase}'] = None
        self.report.df_test[f'dev_abs_cum_{phase}'] = None

        self.report.df_test[f'dev_rel_rate_{phase}'] = None
        self.report.df_test[f'dev_rel_cum_{phase}'] = None

        for i in self.report.df_test.index:
            prod_fact = self.report.df_test.loc[i, f'prod_{phase}']
            prod_model = self.report.df_test.loc[i, f'prod_{phase}_model']
            term_1 = abs(prod_fact - prod_model)
            term_2 = max(prod_fact, prod_model)
            self.report.df_test.loc[i, f'dev_abs_rate_{phase}'] = term_1
            self.report.df_test.loc[i, f'dev_rel_rate_{phase}'] = term_1 / term_2 * 100

            cum_fact = self.report.df_test.loc[i, f'cum_{phase}']
            cum_model = self.report.df_test.loc[i, f'cum_{phase}_model']
            term_1 = abs(cum_fact - cum_model)
            term_2 = max(cum_fact, cum_model)
            self.report.df_test.loc[i, f'dev_abs_cum_{phase}'] = term_1
            self.report.df_test.loc[i, f'dev_rel_cum_{phase}'] = term_1 / term_2 * 100
