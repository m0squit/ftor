import numpy as np
from typing import List

from domain.aggregates.project import Project
from domain.aggregates.zone import Zone
from libs.flood.corey.model import CoreyModel
from libs.numeric_tools.loss_functions import LossFunctions


class Calculator(object):
    """Domain objects calculation manager.

    Class contains code for object data manipulation.
    All object calculation results it save in object.
    """
    _forecast_period: int
    _zone: Zone
    _cum_oil_hist: List[float]
    _cum_liq_hist: List[float]
    _cum_oil_max_hist: float
    _cum_liq_max_hist: float
    _watercuts_hist: List[float]
    _rates_oil_pred: List[float]
    _rates_liq_pred: List[float]
    _watercuts_pred: List[float]
    _cum_liq_pred: List[float]

    @classmethod
    def run(cls, project: Project, forecast_period: int = 90) -> Project:
        cls._forecast_period = forecast_period
        for zone in project.zones:
            cls._zone = zone
            cls._compute_zone()
        return project

    @classmethod
    def _compute_zone(cls):
        cls._prepare_before_prediction()
        cls._predict()

    @classmethod
    def _prepare_before_prediction(cls):
        df = cls._zone.report.df_flood.loc[slice('month', 'day')]
        cls._cum_oil_hist = df['cum_prod_oil'].to_list()
        cls._cum_liq_hist = df['cum_prod_liq'].to_list()
        cls._cum_oil_max_hist = cls._cum_oil_hist[-1]
        cls._cum_liq_max_hist = cls._cum_liq_hist[-1]
        cls._watercuts_hist = df['watercut'].to_list()
        cls._zone.report.prepare()

    @classmethod
    def _predict(cls, mode='test'):
        """Predicts liquid and oil rate by specific zone on 1-365 days.

        Args:
            mode: Calculation mode for prediction. Available modes: 'final', 'test'.
                Final mode - prediction on unverifiable month.
                Test mode - prediction on last month from given data.
                Default - test.
        """
        # TODO: Use mode.
        cls._predict_rate_liquid()
        cls._predict_rate_oil()

    @classmethod
    def _predict_rate_liquid(cls):
        # TODO: Write code about liquid prediction using flux lib.
        cls._rates_liq_pred = cls._zone.report.df_flood.loc['test']['prod_liq'].to_list()
        cls._cum_liq_pred = [cls._cum_liq_max_hist + x for x in np.cumsum(cls._rates_liq_pred)]

    @classmethod
    def _predict_rate_oil(cls):
        cls._calc_rate_oil()
        cls._save_results()
        cls._calc_prediction_metric()

    @classmethod
    def _calc_rate_oil(cls):
        cls._zone.flood_model = CoreyModel(cls._cum_oil_hist, cls._watercuts_hist)
        result = cls._zone.flood_model.predict(cls._cum_oil_max_hist, cls._cum_liq_max_hist, cls._rates_liq_pred)
        cls._watercuts_pred = result['watercut']
        cls._rates_oil_pred = result['rate_oil']

    @classmethod
    def _save_results(cls):
        cls._zone.report.df_result['watercut_model'] = cls._watercuts_pred
        cls._zone.report.df_result['prod_oil_model'] = cls._rates_oil_pred
        cls._zone.report.df_result['cum_oil_model'] = [cls._cum_oil_max_hist +
                                                       x for x in np.cumsum(cls._rates_oil_pred)]
        watercuts_test = cls._zone.report.df_result['watercut'].to_list()
        cls._zone.report.mae_train = cls._zone.flood_model.error
        cls._zone.report.mae_test = LossFunctions.mae(watercuts_test, cls._watercuts_pred)

    @classmethod
    def _calc_prediction_metric(cls):
        df = cls._zone.report.df_result
        for i in df['prod_oil'].index:
            rate_oil_fact = df.loc[i, 'prod_oil']
            rate_oil_model = df.loc[i, 'prod_oil_model']
            df.loc[i, 'dev_rel_rate_oil'] = abs(rate_oil_fact - rate_oil_model) / max(rate_oil_fact, rate_oil_model)

            cum_prod_oil = df.loc[i, 'cum_prod_oil']
            cum_prod_oil_model = df.loc[i, 'cum_oil_model']
            df.loc[i, 'dev_abs_cum_oil'] = cum_prod_oil_model - cum_prod_oil
        cls._zone.report.df_result = df.copy()
