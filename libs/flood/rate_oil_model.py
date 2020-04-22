import scipy.integrate as integrate
import libs.flood.watercut_model_support as watercut_model


class RateOilModel(object):

    _params_initial = {'watercut_initial': 0.05,
                       'mobility_ratio': 1.66,
                       'parameter_alpha': 3.50,
                       'parameter_beta': 3.77}
    _method_optimization = 'differential_evolution'

    def __init__(self,
                 data,
                 mult_watercuts_train=1,
                 mult_indexes_train=1,
                 **optional):
        self.data = data
        self.mult_watercuts_train = mult_watercuts_train
        self.mult_indexes_train = mult_indexes_train
        self._params_initial =\
            optional['params_initial'] if 'params_initial' in optional else self._params_initial
        self._method_optimization =\
            optional['method_optimization'] if 'method_optimization' in optional else self._method_optimization

        self.rates_oil = []
        self.watercuts = []
        self.recovery_factors = []
        self.params_watercut = []
        self.index_start_train = None
        self.index_start_prediction = None
        self._calc_rates_oil()

    def _calc_rates_oil(self):
        self._get_settings_watercut_model()
        if self.mult_watercuts_train != 1:
            self._copy_before_train()
        self._calc_rates_oil_train()
        if self.mult_indexes_train != 1:
            self._calc_rates_oil_prediction()

    def _get_settings_watercut_model(self):
        watercut_model.WatercutModel.mult_watercuts_train = self.mult_watercuts_train
        watercut_model.WatercutModel.mult_indexes_train = self.mult_indexes_train
        settings_watercut_model = watercut_model.WatercutModel.get_settings(self.data,
                                                                            self._params_initial,
                                                                            self._method_optimization)
        self.index_start_train = settings_watercut_model['index_start_train']
        self.index_start_prediction = settings_watercut_model['index_start_prediction']
        self.params_watercut = settings_watercut_model['params']

    def _copy_before_train(self):
        recovery_factors = self.data.recovery_factors[:self.index_start_train]
        watercuts = self.data.watercuts[:self.index_start_train]
        rates_oil = self.data.rates_oil[:self.index_start_train]
        self.recovery_factors.extend(recovery_factors)
        self.watercuts.extend(watercuts)
        self.rates_oil.extend(rates_oil)

    def _calc_rates_oil_train(self):
        for i in range(self.index_start_train, self.index_start_prediction):
            recovery_factor = self.data.recovery_factors[i]
            watercut = watercut_model.WatercutModel.calc_watercut(recovery_factor, self.params_watercut)
            rate_liquid = self.data.rates_liquid[i]
            rate_oil = rate_liquid * (1 - watercut)
            self.recovery_factors.append(recovery_factor)
            self.watercuts.append(watercut)
            self.rates_oil.append(rate_oil)

    def _calc_rates_oil_prediction(self):
        cumulative_productions_liquid = self.data.cumulative_productions_liquid[self.index_start_prediction - 1:]
        recovery_factors = self._solve_ode(fun=self._calc_right_hand_side_ode,
                                           y0=[self.recovery_factors[-1]],
                                           t_span=(cumulative_productions_liquid[0], cumulative_productions_liquid[-1]),
                                           t_eval=cumulative_productions_liquid[1:])
        rates_liquid = self.data.rates_liquid[self.index_start_prediction:]
        for i in range(len(rates_liquid)):
            recovery_factors = list(recovery_factors)
            recovery_factor = recovery_factors[i]
            watercut = watercut_model.WatercutModel.calc_watercut(recovery_factor, self.params_watercut)
            rate_liquid = rates_liquid[i]
            rate_oil = rate_liquid * (1 - watercut)
            self.recovery_factors.append(recovery_factor)
            self.watercuts.append(watercut)
            self.rates_oil.append(rate_oil)

    def _calc_right_hand_side_ode(self, cumulative_production_liquid, recovery_factor):
        stoiip = self.data.stoiip
        term = (1 - watercut_model.WatercutModel.calc_watercut(recovery_factor, self.params_watercut)) * 1 / stoiip
        return term

    @staticmethod
    def _solve_ode(fun, t_span, y0, t_eval):
        solution = integrate.solve_ivp(fun=fun,
                                       t_span=t_span,
                                       y0=y0,
                                       method='RK45',
                                       t_eval=t_eval)
        return list(solution.y[0])
