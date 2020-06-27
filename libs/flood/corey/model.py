from typing import List, Dict

import numpy as np
import scipy.optimize as optimize

from libs.flood._predictor import _Predictor
from libs.flood.corey.params import CoreyModelParams
from libs.numeric_tools.loss_function import LossFunction
from libs.numeric_tools.optimizer import Optimizer
from libs.numeric_tools.weight_distributor import WeightDistributor


class CoreyModel(object):
    """Corey flood model.

    Attributes:
        params: Setting parameters of model.
            They auto define base on input train data.
        cums_oil: Train sequence of oil cumulative production values.
        watercuts_fact: Train sequence of watercut values.
            Each value must be correlated with value in "cum_prods_oil".
        watercuts_model: Model sequence of watercut values.
            Each value correlate with value in "cum_prods_oil".
    """
    def __init__(self,
                 cums_oil: List[float],
                 watercuts: List[float]):

        self.cums_oil = cums_oil
        self.watercuts_fact = watercuts
        self._create_model()

    def calc_watercut(self, cum_oil: float) -> float:
        recovery_factor = cum_oil / (self.params.stoiip * 1e6)
        term_1 = (1 - recovery_factor) ** self.params.alpha
        term_2 = self.params.mobility_ratio * recovery_factor ** self.params.beta
        watercut = self.params.watercut_initial + 1 / (1 + term_1 / term_2)
        return watercut

    def predict(self,
                cum_oil_start: float,
                cum_liq_start: float,
                rates_liq: List[float]) -> Dict[str, List[float]]:
        """Predicts oil rate depending on liquid rate.

        Calculates watercut and oil rate values for each value of given liquid rate.

        Args:
            cum_oil_start: Start value of oil cumulative production for prediction.
            cum_liq_start: Start value of liquid cumulative production for prediction.
            rates_liq: Sequence of liquid rate values for oil rate definition in forecast.
        """
        cums_liq = [cum_liq_start + x for x in np.cumsum(rates_liq)]
        cums_oil = _Predictor.run(cum_oil_start, cums_liq, self)
        watercuts = []
        rates_oil = []
        for i in range(len(cums_oil)):
            cum_oil = cums_oil[i]
            watercut = self.calc_watercut(cum_oil)
            rate_liq = rates_liq[i]
            rate_oil = rate_liq * (1 - watercut)
            watercuts.append(watercut)
            rates_oil.append(rate_oil)
        return {'watercut': watercuts, 'rate_oil': rates_oil}

    def _create_model(self):
        self.params = CoreyModelParams()
        self._set_model_preferences()
        self._add_stoiip_boundaries()
        self._fit_params()

    def _set_model_preferences(self):
        self.recovery_factor_min = 0.05
        self.recovery_factor_max = 0.9
        self.weights = WeightDistributor.run(self.cums_oil)

    def _add_stoiip_boundaries(self):
        cum_max = max(self.cums_oil) / 1e6
        stoiip_min = cum_max * 1 / self.recovery_factor_max
        stoiip_max = cum_max * 1 / self.recovery_factor_min
        self.params.usable_params['stoiip'] = {'min': stoiip_min, 'max': stoiip_max}

    def _fit_params(self):
        self._minimize_trend()
        self._minimize_last_value()
        self._calc_watercut_model()

    def _minimize_trend(self):
        params_min_max = list(self.params.usable_params.values())
        params = Optimizer.calc_params(self._loss_function_trend, params_min_max, method='diff')

    def _minimize_last_value(self):
        initial_guess = self.params.watercut_initial
        watercut_initial = optimize.minimize(self._loss_function_last_value, initial_guess)

    def _calc_watercut_model(self):
        self.watercuts_model = []
        for cum_prod_oil in self.cums_oil:
            watercut_model = self.calc_watercut(cum_prod_oil)
            self.watercuts_model.append(watercut_model)
        self.mae_train = LossFunction.run(self.watercuts_fact, self.watercuts_model, self.weights, mode='mae')

    def _loss_function_trend(self, params: List[float]) -> float:
        self.params.set_values(params)
        self._calc_watercut_model()
        return self.mae_train

    def _loss_function_last_value(self, watercut_initial: float) -> float:
        self.params.watercut_initial = watercut_initial[0]
        cum_prod_oil = self.cums_oil[-1]
        watercut_fact = self.watercuts_fact[-1]
        watercut_model = self.calc_watercut(cum_prod_oil)
        error = abs(watercut_fact - watercut_model)
        return error
