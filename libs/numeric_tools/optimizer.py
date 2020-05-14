import scipy.optimize as optimize


class Optimizer(object):

    @classmethod
    def calc_params(cls, loss_function, params, method_optimization):
        bounds_type = []

        usable_params = params.usable_params
        for param_name, param_set in usable_params.items():
            param_min = param_set['min']
            param_max = param_set['max']
            bounds_type.append((param_min, param_max))

        params = cls._calc_target_function(loss_function=loss_function,
                                           bounds_type=bounds_type,
                                           method_optimization=method_optimization)
        return params

    @staticmethod
    def _calc_target_function(loss_function, bounds_type, method_optimization):
        solution = None
        if method_optimization == 'diff':
            solution = optimize.differential_evolution(loss_function,
                                                       bounds_type,
                                                       strategy='best2exp',
                                                       polish=True)

        if method_optimization == 'shgo':
            solution = optimize.shgo(loss_function,
                                     bounds_type)

        if method_optimization == 'dual':
            solution = optimize.dual_annealing(loss_function,
                                               bounds_type,
                                               no_local_search=False)
        return solution.x
