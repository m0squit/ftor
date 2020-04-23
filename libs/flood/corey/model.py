import numpy as np

from libs.flood._predictor import _Predictor
from libs.flood.corey.params import CoreyModelParams
from libs.numeric_tools.optimizer import Optimizer


class CoreyModel(object):

    _recovery_factor_min = 1e-5

    def __init__(self,
                 cum_prods_oil,
                 watercuts,
                 stoiip=None):

        self.cum_prods_oil = cum_prods_oil
        self.watercuts = watercuts
        self.params = CoreyModelParams()
        self._create_model(stoiip)

    def calc_watercut(self, cum_prod_oil):
        recovery_factor = cum_prod_oil / self.params.stoiip
        term_1 = (1 - recovery_factor) ** self.params.alpha
        term_2 = self.params.mobility_ratio * recovery_factor ** self.params.beta
        watercut = self.params.watercut_initial + (1 - self.params.watercut_initial) / (1 + term_1 / term_2)
        return watercut

    def predict(self, cum_prod_oil_start, cum_prod_liq_start, rates_liq):
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
        self._add_stoiip(stoiip)
        params = Optimizer.calc_params(loss_function=self._loss_function,
                                       params=self.params,
                                       method_optimization='dif')
        self._set_params(params)

    def _add_stoiip(self, stoiip):
        self.params.stoiip = stoiip
        if stoiip is None:
            cum_prod_max = max(self.cum_prods_oil)
            stoiip_min = cum_prod_max
            stoiip_max = cum_prod_max * 1 / self._recovery_factor_min
            self.params.usable_params['stoiip'] = {'min': stoiip_min,
                                                   'max': stoiip_max,
                                                   'init': stoiip_min}

    def _set_params(self, params):
        self.params.set_values(params)

    def _loss_function(self, params):
        self._set_params(params)
        error_total = 0
        for i in range(len(self.cum_prods_oil)):
            cum_prod = self.cum_prods_oil[i]
            watercut_model = self.calc_watercut(cum_prod)
            watercut_fact = self.watercuts[i]
            error = abs(watercut_model - watercut_fact)
            error_total += error
        return error_total
