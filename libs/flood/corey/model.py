from typing import List, Dict

import numpy as np

from libs.flood._predictor import _Predictor
from libs.flood.corey.params import CoreyModelParams
from libs.numeric_tools.loss_function import LossFunction
from libs.numeric_tools.optimizer import Optimizer


class CoreyModel(object):
    """Corey flood model.

    Attributes:
        params: Setting parameters of model.
            They auto define base on input train data.
        cum_prods_oil: Train sequence of oil cumulative production values.
        watercuts_fact: Train sequence of watercut values.
            Each value must be correlated with value in "cum_prods_oil".
        watercuts_model: Model sequence of watercut values.
            Each value correlate with value in "cum_prods_oil".
    """
    def __init__(self,
                 cum_prods_oil: List[float],
                 watercuts: List[float],
                 weights: List[float] = None,
                 stoiip: float = None):

        self.cum_prods_oil = cum_prods_oil
        self.watercuts_fact = watercuts
        self.weights = weights
        self._create_model(stoiip)

    def calc_watercut(self, cum_prod_oil: float) -> float:
        recovery_factor = cum_prod_oil / (self.params.stoiip * 1e6)
        term_1 = (1 - recovery_factor) ** self.params.alpha
        term_2 = self.params.mobility_ratio * recovery_factor ** self.params.beta
        watercut = self.params.watercut_initial + 1 / (1 + term_1 / term_2)
        return watercut

    def predict(self,
                cum_prod_oil_start: float,
                cum_prod_liq_start: float,
                rates_liq: List[float]) -> Dict[str, List[float]]:
        """Predicts oil rate depending on liquid rate.

        Calculates watercut and oil rate values for each value of given liquid rate.

        Args:
            cum_prod_oil_start: Start value of oil cumulative production for prediction.
            cum_prod_liq_start: Start value of liquid cumulative production for prediction.
            rates_liq: Sequence of liquid rate values for oil rate definition in forecast.
        """
        cum_prods_liq = [cum_prod_liq_start + x for x in np.cumsum(rates_liq)]
        cum_prods_oil = _Predictor.run(cum_prod_oil_start, cum_prods_liq, self)
        watercuts = []
        rates_oil = []
        for i in range(len(cum_prods_oil)):
            cum_prod_oil = cum_prods_oil[i]
            watercut = self.calc_watercut(cum_prod_oil)
            rate_liq = rates_liq[i]
            rate_oil = rate_liq * (1 - watercut)
            watercuts.append(watercut)
            rates_oil.append(rate_oil)
        return {'watercut': watercuts, 'rate_oil': rates_oil}

    def _create_model(self, stoiip):
        self.params = CoreyModelParams()
        self._add_stoiip(stoiip)
        self._fit_params()

    def _add_stoiip(self, stoiip):
        self.params.stoiip = stoiip
        if stoiip is None:
            cum_prod_max = max(self.cum_prods_oil) / 1e6
            recovery_factor_min = 0.05
            stoiip_min = cum_prod_max
            stoiip_max = cum_prod_max * 1 / recovery_factor_min
            self.params.usable_params['stoiip'] = {'min': stoiip_min,
                                                   'max': stoiip_max}

    def _fit_params(self):
        params = Optimizer.calc_params(loss_function=self._loss_function,
                                       params=self.params,
                                       method_optimization='shgo')

    def _loss_function(self, params):
        self.watercuts_model = []
        self._set_params(params)
        for i in range(len(self.cum_prods_oil)):
            cum_prod = self.cum_prods_oil[i]
            watercut_model = self.calc_watercut(cum_prod)
            self.watercuts_model.append(watercut_model)
        self.error = LossFunction.run(self.watercuts_fact, self.watercuts_model, self.weights, mode='mae')
        return self.error

    def _set_params(self, params):
        self.params.set_values(params)
