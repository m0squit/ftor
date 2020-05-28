from typing import Dict, List, Tuple

import scipy.optimize as optimize


class Optimizer(object):

    @classmethod
    def calc_params(cls, loss_function, params_min_max: List[Dict], method: str):
        bounds = []
        for param_set in params_min_max:
            param_min = param_set['min']
            param_max = param_set['max']
            bounds.append((param_min, param_max))
        params_min_max = cls._calc_target_function(loss_function, bounds, method)
        return params_min_max

    @staticmethod
    def _calc_target_function(loss_function, bounds: List[Tuple], method: str):
        solution = None
        if method == 'diff':
            solution = optimize.differential_evolution(loss_function,
                                                       bounds)

        if method == 'shgo':
            solution = optimize.shgo(loss_function,
                                     bounds)

        if method == 'dual':
            solution = optimize.dual_annealing(loss_function,
                                               bounds,
                                               initial_temp=1)
        return solution.x
