import scipy.optimize as optimize


class Optimizer(object):

    @classmethod
    def calc_params(cls, loss_function, params, method_optimization):
        bounds_type_1 = ([], [])
        bounds_type_2 = []
        params_initial = {}

        usable_params = params.usable_params
        for param_name, param_set in usable_params.items():
            param_min = param_set['min']
            param_max = param_set['max']
            param_init = param_set['init']

            bounds_type_1[0].append(param_min)
            bounds_type_1[1].append(param_max)
            bounds_type_2.append((param_min, param_max))
            params_initial[param_name] = param_init

        params = cls._calc_target_function(loss_function=loss_function,
                                           bounds_type_1=bounds_type_1,
                                           bounds_type_2=bounds_type_2,
                                           params_initial=params_initial,
                                           method_optimization=method_optimization)
        return params

    @staticmethod
    def _calc_target_function(loss_function, bounds_type_1, bounds_type_2, params_initial, method_optimization):
        solution = None
        if method_optimization == 'lsq':
            solution = optimize.least_squares(fun=loss_function,
                                              x0=params_initial,
                                              jac='3-point',
                                              bounds=bounds_type_1,
                                              method='trf',
                                              loss='linear',
                                              f_scale=1)

        if method_optimization == 'min':
            solution = optimize.minimize(fun=loss_function,
                                         x0=params_initial,
                                         method='L-BFGS-B',
                                         jac='2-point',
                                         bounds=bounds_type_2)

        if method_optimization == 'dif':
            solution = optimize.differential_evolution(loss_function,
                                                       bounds=bounds_type_2,
                                                       strategy='best2bin')

        if method_optimization == 'dua':
            solution = optimize.dual_annealing(func=loss_function,
                                               bounds=bounds_type_2,
                                               maxiter=1000,
                                               x0=params_initial)
        return solution.x
