import scipy.optimize as optimize


class WatercutsModelOptimizer(object):

    params_bounds = {'watercut_initial': {'min': 0, 'max': 1},
                     'mobility_ratio': {'min': 0.01, 'max': 5},
                     'parameter_alpha': {'min': 0.5, 'max': 20},
                     'parameter_beta': {'min': 0.1, 'max': 20}}

    @classmethod
    def calc_params(cls, target_function, params_initial, method_optimization):
        watercut_initial_min = cls.params_bounds['watercut_initial']['min']
        watercut_initial_max = cls.params_bounds['watercut_initial']['max']
        mobility_ratio_min = cls.params_bounds['mobility_ratio']['min']
        mobility_ratio_max = cls.params_bounds['mobility_ratio']['max']
        parameter_alpha_min = cls.params_bounds['parameter_alpha']['min']
        parameter_alpha_max = cls.params_bounds['parameter_alpha']['max']
        parameter_beta_min = cls.params_bounds['parameter_beta']['min']
        parameter_beta_max = cls.params_bounds['parameter_beta']['max']
        bounds_type_1 = ([watercut_initial_min, mobility_ratio_min, parameter_alpha_min, parameter_beta_min],
                         [watercut_initial_max, mobility_ratio_max, parameter_alpha_max, parameter_beta_max])
        bounds_type_2 = [(watercut_initial_min, watercut_initial_max),
                         (mobility_ratio_min, mobility_ratio_max),
                         (parameter_alpha_min, parameter_alpha_max),
                         (parameter_beta_min, parameter_beta_max)]
        params = cls._calc_target_function(target_function=target_function,
                                           bounds_type_1=bounds_type_1,
                                           bounds_type_2=bounds_type_2,
                                           params_initial=params_initial,
                                           method_optimization=method_optimization)
        return params

    @staticmethod
    def _calc_target_function(target_function, bounds_type_1, bounds_type_2, params_initial, method_optimization):
        solution = None
        if method_optimization == 'least_squares':
            solution = optimize.least_squares(fun=target_function,
                                              x0=params_initial,
                                              jac='3-point',
                                              bounds=bounds_type_1,
                                              method='trf',
                                              loss='linear',
                                              f_scale=1)
        if method_optimization == 'minimize':
            solution = optimize.minimize(fun=target_function,
                                         x0=params_initial,
                                         method='L-BFGS-B',
                                         jac='2-point',
                                         bounds=bounds_type_2)
        if method_optimization == 'differential_evolution':
            solution = optimize.differential_evolution(target_function,
                                                       bounds=bounds_type_2,
                                                       strategy='best2bin')
        if method_optimization == 'dual_annealing':
            solution = optimize.dual_annealing(func=target_function,
                                               bounds=bounds_type_2,
                                               maxiter=1000,
                                               x0=params_initial)
        return solution.x
