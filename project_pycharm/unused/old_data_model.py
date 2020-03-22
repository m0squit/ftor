import scipy.optimize as optimize


class DataModel(object):
    """Класс описывает модельные данные.

    Attributes:
        params_watercut (list(float)): Параметры модели обводненности.
        recovery_factors (list(float)): КИН на каждый момент времени, fr.
        watercuts (list(float)): Обводненность продукции скважины на каждый момент времени, fr.
        rates_oil (list(float)): Дебит нефти на каждый момент времени, sm3/day.
        deviations_rate_oil (list(float)): Отклонение дебита нефти модельного от фактического на каждый момент времени, fr.
        _recovery_factor (float): КИН на текущий временной шаг, fr.
        _rate_liquid (float): Дебит жидкости на текущий временной шаг, sm3/day.
        _rate_oil (float): Дебит нефти на текущий временной шаг, sm3/day.
        _mult_error (float): Множитель ошибки последнего значения обводненности на train выборке.
        _method_optimization (str): Метод оптимизации целевых функций.
        data_fact (DataFact): Фактические данные.
        bounds_params_watercut (dict(str:float)): Min, max значения параметров модели обводненности для оптимизации.
        bounds_rate_oil (dict(str:float)): Min, max значения дебита нефти для оптимизации.
        initial_params_watercut (dict(str:float)): Начальные значения параметров модели обводненности для оптимизации.
        initial_rate_oil (float): Начальные значения дебита нефти обводненности для оптимизации.

        point_train_start (float): Индекс элемента временного ряда для начала train выборки.
        point_train_end (float): Индекс элемента временного ряда для конца train выборки.
        _mult_points_train (float): Множитель длины временного ряда для получения train выборки.
        _mult_watercuts_train (float): Множитель значения обводненности для получения point_train_start.

    """

    rates_oil = []
    watercuts = []
    recovery_factors = []
    deviations_rate_oil = []
    params_watercut = []
    _bounds_params_watercut = {'watercut_initial': {'min': 0, 'max': 1},
                               'mobility_ratio': {'min': 0.01, 'max': 5},
                               'parameter_alpha': {'min': 0.5, 'max': 20},
                               'parameter_beta': {'min': 0.1, 'max': 20}}
    _initial_params_watercut = {'watercut_initial': 0.05,
                                'mobility_ratio': 1.66,
                                'parameter_alpha': 3.50,
                                'parameter_beta': 3.77}
    _recovery_factor = None
    _rate_liquid = None
    _rate_oil = None
    _bounds_rate_oil = {'min': 0, 'max': None}
    _initial_rate_oil = None
    _mult_error = 1e3

    point_train_start = None
    point_train_end = None
    _mult_watercuts_train = 1.1
    _mult_points_train = 0.8

    # Для оптимизации целевых функций доступны следующие методы:
    # 'least_squares',
    # 'minimize',
    # 'differential_evolution',
    # 'dual_annealing'
    _method_optimization = 'differential_evolution'

    def __init__(self,
                 data_fact):
        self.data_fact = data_fact

    @classmethod
    def _calc_watercut(cls, recovery_factor, params_watercut):
        watercut_initial = params_watercut[0]
        mobility_ratio = params_watercut[1]
        parameter_alpha = params_watercut[2]
        parameter_beta = params_watercut[3]
        term_1 = (1 - recovery_factor) ** parameter_alpha
        term_2 = mobility_ratio * recovery_factor ** parameter_beta
        watercut = watercut_initial + (1 - watercut_initial) / (1 + term_1 / term_2)
        return watercut

    @classmethod
    def _calc_solution_target_function(cls, target_function, method, x0, bounds_type_1, bounds_type_2):
        solution = None
        if method == 'least_squares':
            solution = optimize.least_squares(fun=target_function,
                                              x0=x0,
                                              jac='3-point',
                                              bounds=bounds_type_1,
                                              method='trf',
                                              loss='linear',
                                              f_scale=1)
        if method == 'minimize':
            solution = optimize.minimize(fun=target_function,
                                         x0=x0,
                                         method='L-BFGS-B',
                                         jac='2-point',
                                         bounds=bounds_type_2)
        if method == 'differential_evolution':
            solution = optimize.differential_evolution(target_function,
                                                       bounds=bounds_type_2,
                                                       strategy='best2bin')
        if method == 'dual_annealing':
            solution = optimize.dual_annealing(func=target_function,
                                               bounds=bounds_type_2,
                                               maxiter=1000,
                                               x0=x0)
        return solution.x

    def calc_data(self):
        self._cut_data_train()
        self._calc_model(self._target_function_watercut, self._method_optimization)
        self._calc_data_train()
        self._calc_data_prediction()

    def _calc_model(self, target_function, method):
        if target_function == self._target_function_watercut:
            x0 = list(self._initial_params_watercut.values())
            watercut_initial_min = self._bounds_params_watercut['watercut_initial']['min']
            watercut_initial_max = self._bounds_params_watercut['watercut_initial']['max']
            mobility_ratio_min = self._bounds_params_watercut['mobility_ratio']['min']
            mobility_ratio_max = self._bounds_params_watercut['mobility_ratio']['max']
            parameter_alpha_min = self._bounds_params_watercut['parameter_alpha']['min']
            parameter_alpha_max = self._bounds_params_watercut['parameter_alpha']['max']
            parameter_beta_min = self._bounds_params_watercut['parameter_beta']['min']
            parameter_beta_max = self._bounds_params_watercut['parameter_beta']['max']
            bounds_type_1 = ([watercut_initial_min, mobility_ratio_min, parameter_alpha_min, parameter_beta_min],
                             [watercut_initial_max, mobility_ratio_max, parameter_alpha_max, parameter_beta_max])
            bounds_type_2 = [(watercut_initial_min, watercut_initial_max),
                             (mobility_ratio_min, mobility_ratio_max),
                             (parameter_alpha_min, parameter_alpha_max),
                             (parameter_beta_min, parameter_beta_max)]
            self.params_watercut = self._calc_solution_target_function(target_function=target_function,
                                                                       method=method,
                                                                       x0=x0,
                                                                       bounds_type_1=bounds_type_1,
                                                                       bounds_type_2=bounds_type_2)
        if target_function == self._target_function_rate_oil:
            x0 = self._initial_rate_oil
            rate_oil_min = self._bounds_rate_oil['min']
            rate_oil_max = self._bounds_rate_oil['max']
            bounds_type_1 = (rate_oil_min, rate_oil_max)
            bounds_type_2 = [bounds_type_1]
            self._rate_oil = self._calc_solution_target_function(target_function=target_function,
                                                                 method=method,
                                                                 x0=x0,
                                                                 bounds_type_1=bounds_type_1,
                                                                 bounds_type_2=bounds_type_2)

    def _cut_data_train(self):
        data_fact = self.data_fact
        recovery_factors = data_fact.recovery_factors
        watercuts = data_fact.watercuts
        mult_watercuts_train = self._mult_watercuts_train
        mult_points_train = self._mult_points_train
        watercut_fact_0 = watercuts[0]
        watercut_critical = watercut_fact_0 * mult_watercuts_train
        for watercut_fact in watercuts:

            if watercut_fact > watercut_critical:
                point_train_start = watercuts.index(watercut_fact)
                recovery_factor_train_start = recovery_factors[point_train_start]
                recovery_factor_max = max(recovery_factors)
                range_recovery_factors = recovery_factor_max - recovery_factor_train_start
                recovery_factor_train_end = recovery_factor_train_start + range_recovery_factors * mult_points_train
                recovery_factor_train_end = min(recovery_factors, key=lambda x: abs(x - recovery_factor_train_end))
                point_train_end = recovery_factors.index(recovery_factor_train_end)
                self.point_train_start = point_train_start
                self.point_train_end = point_train_end
                break

    def _calc_data_train(self):
        params_watercut = self.params_watercut

        data_fact = self.data_fact
        point_train_start = data_fact.point_train_start
        point_train_end = data_fact.point_train_end

        rates_oil_fact = data_fact.rates_oil
        rates_liquid = data_fact.rates_liquid
        recovery_factors = data_fact.recovery_factors

        self.rates_oil = data_fact.rates_oil[:point_train_start]
        self.recovery_factors = data_fact.recovery_factors[:point_train_end + 1]

        for i in range(point_train_start, point_train_end + 1):

            rate_liquid = rates_liquid[i]
            recovery_factor = self.recovery_factors[i]
            watercut = self._calc_watercut(recovery_factor, params_watercut)
            rate_oil_model = rate_liquid * (1 - watercut)
            rate_oil_fact = rates_oil_fact[i]
            deviation_rate_oil = abs(rate_oil_model - rate_oil_fact) / rate_oil_fact
            self._initial_rate_oil = rate_oil_model
            self.watercuts.append(watercut)
            self._rate_oil = rate_oil_model
            self.rates_oil.append(rate_oil_model)
            self.deviations_rate_oil.append(deviation_rate_oil)

    def _calc_data_prediction(self):
        params_watercut = self.params_watercut
        data_fact = self.data_fact
        rates_liquid = data_fact.rates_liquid
        rates_oil_fact = data_fact.rates_oil
        point_train_end = data_fact.point_train_end
        point_pred_start = point_train_end + 1
        points_count = data_fact.points_count
        stoiip = data_fact.stoiip
        recovery_factors = self.recovery_factors
        self._recovery_factor = recovery_factors[-1]
        for i in range(point_pred_start, points_count + 1):

            rate_liquid = rates_liquid[i]
            self._rate_liquid = rate_liquid
            self._calc_model(self._target_function_rate_oil, self._method_optimization)
            rate_oil_model = self._rate_oil
            rate_oil_fact = rates_oil_fact[i]
            deviation_rate_oil = abs(rate_oil_model - rate_oil_fact) / rate_oil_fact
            recovery_factor = self._recovery_factor + rate_oil_model / stoiip
            watercut = self._calc_watercut(recovery_factor, params_watercut)
            self._recovery_factor = recovery_factor
            self.recovery_factors.append(recovery_factor)
            self.watercuts.append(watercut)
            self.rates_oil.append(rate_oil_model)
            self.deviations_rate_oil.append(deviation_rate_oil)

    def _target_function_watercut(self, params):
        data_fact = self.data_fact
        recovery_factors = data_fact.recovery_factors
        watercuts_fact = data_fact.watercuts
        point_train_start = data_fact.point_train_start
        point_train_end = data_fact.point_train_end
        mult_error = self._mult_error
        error_total = 0
        mult = 1
        for i in range(point_train_start, point_train_end + 1):
            recovery_factor = recovery_factors[i]
            watercut_model = self._calc_watercut(recovery_factor, params)
            watercut_fact = watercuts_fact[i]
            if i == point_train_end:
                mult = mult_error
            error = abs(watercut_model - watercut_fact) * mult
            error_total += error
        return error_total

    def _target_function_rate_oil(self, rate_oil):
        recovery_factor = self._recovery_factor
        params_watercut = self.params_watercut
        rate_liquid = self._rate_liquid
        stoiip = self.data_fact.stoiip
        rate_oil_left = rate_oil
        recovery_factor += rate_oil / stoiip
        watercut = self._calc_watercut(recovery_factor, params_watercut)
        rate_oil_right = rate_liquid * (1 - watercut)
        error = abs(rate_oil_left - rate_oil_right)
        return error
