import numpy as np
from typing import List

from domain.aggregates.project import Project
from domain.aggregates.zone import Zone
from libs.flood.corey.model import CoreyModel
from libs.numeric_tools.loss_function import LossFunction
from libs.numeric_tools.weight_distributor import WeightDistributor


class Calculator(object):
    """Domain objects calculation manager.

    Class contains code for object data manipulation.
    All object calculation results it save in object.
    """
    _project: Project
    _forecast_days_number: int
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
    def run(cls, project: Project, forecast_days_number: int) -> Project:
        cls._project = project
        cls._forecast_days_number = forecast_days_number
        for zone in cls._project.zones:
            print(zone.well.name)
            cls._zone = zone
            cls._compute_zone()
        cls._calc_project()
        return project

    @classmethod
    def _compute_zone(cls):
        cls._prepare_before_prediction()
        cls._predict()

    @classmethod
    def _prepare_before_prediction(cls):
        df = cls._zone.report.df_flood.loc[:('test', None)]
        cls._cum_oil_hist = df['cum_prod_oil'].to_list()
        cls._cum_liq_hist = df['cum_prod_liq'].to_list()

        cls._cum_oil_max_hist = cls._zone.report.cum_prod_oil
        cls._cum_liq_max_hist = cls._zone.report.cum_prod_liq
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
        weights = WeightDistributor.run(cls._cum_oil_hist)
        # weights = None
        cls._zone.flood_model = CoreyModel(cls._cum_oil_hist, cls._watercuts_hist, weights)
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
        cls._zone.report.mae_test = LossFunction.run(watercuts_test, cls._watercuts_pred)

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

    @classmethod
    def _calc_project(cls):
        # cls._prepare()
        cls._calc()

    # @classmethod
    # def _prepare(cls):
    #     cls._project.df_result = cls._zone.report.df_result[['dev_rel_rate_oil', 'dev_abs_cum_oil']].copy()

    @classmethod
    def _calc(cls):
        days = [x for x in range(0, cls._forecast_days_number)]
        n = len(cls._project.wells)
        devs_rel_rate_oil = []
        devs_abs_cum_oil = []
        for i in days:
            dev_rel_rate_oil = 0
            dev_abs_cum_oil = 0
            for zone in cls._project.zones:
                df = zone.report.df_result
                dev_rel_rate_oil += df['dev_rel_rate_oil'].to_list()[i]
                dev_abs_cum_oil += df['dev_abs_cum_oil'].to_list()[i]
            devs_rel_rate_oil.append(dev_rel_rate_oil / n)
            devs_abs_cum_oil.append(dev_abs_cum_oil)
        cls._project.df_result['dev_rel_rate_oil'] = devs_rel_rate_oil
        cls._project.df_result['dev_abs_cum_oil'] = devs_abs_cum_oil
        cls._project.maes_train = [zone.report.mae_train for zone in cls._project.zones]
        cls._project.maes_test = [zone.report.mae_test for zone in cls._project.zones]
