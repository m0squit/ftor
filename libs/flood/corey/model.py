from libs.flood.corey.params import CoreyModelParams
from libs.numeric_tools.optimizer import Optimizer


class CoreyModel(object):

    _recovery_factor_min = 1e-5

    def __init__(self,
                 cum_prods,
                 watercuts,
                 stoiip=None):

        self.cum_prods = cum_prods
        self.watercuts = watercuts
        self.params = CoreyModelParams()
        self._add_stoiip(stoiip)
        self._create_model()

    def calc(self):
        pass

    def _add_stoiip(self, stoiip):
        self.params.stoiip = stoiip
        if stoiip is None:
            cum_prod_max = max(self.cum_prods)
            stoiip_min = cum_prod_max
            stoiip_max = cum_prod_max * 1 / self._recovery_factor_min
            self.params.usable_params['stoiip'] = {'min': stoiip_min, 'max': stoiip_max, 'init': stoiip_min}

    def _create_model(self):
        params = Optimizer().calc_params(loss_function=self._loss_function,
                                         params=self.params,
                                         method_optimization='diff')

    def _loss_function(self, params):
        error_total = 0
        for i in range(len(self.cum_prods)):
            cum_prod = self.cum_prods[i]
            self.params.set_values(params)
            watercut_model = self._calc_watercut(cum_prod)
            watercut_fact = self.watercuts[i]
            error = abs(watercut_model - watercut_fact)
            error_total += error
        return error_total

    def _calc_watercut(self, cum_prod):
        p = self.params
        recovery_factor = cum_prod / p.stoiip
        term_1 = (1 - recovery_factor) ** p.alpha
        term_2 = p.mobility_ratio * recovery_factor ** p.beta
        watercut = p.watercut_initial + (1 - p.watercut_initial) / (1 + term_1 / term_2)
        return watercut
