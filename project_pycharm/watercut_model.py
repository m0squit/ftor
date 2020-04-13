import math
import project_pycharm.watercut_model_optimizer as model_optimizer


class WatercutModel(object):

    mult_watercuts_train = None
    mult_indexes_train = None
    _data = None
    _index_start_train = None
    _index_start_prediction = None

    @classmethod
    def get_settings(cls, data, params_initial, method_optimization):
        cls._data = data
        cls._calc_bounds_train()
        params = model_optimizer.WatercutsModelOptimizer.calc_params(cls._target_function,
                                                                     params_initial,
                                                                     method_optimization)
        settings = {'index_start_train': cls._index_start_train,
                    'index_start_prediction': cls._index_start_prediction,
                    'params': params}
        return settings

    @classmethod
    def _calc_bounds_train(cls):
        watercuts = cls._data.watercuts
        watercut_initial = watercuts[0]
        watercut_critical = watercut_initial * cls.mult_watercuts_train
        # for watercut in watercuts:
        #     if watercut > watercut_critical:
        indexes_count = cls._data.times_count
        index_start_train = 0  # watercuts.index(watercut)
        range_train = (indexes_count - index_start_train) * cls.mult_indexes_train
        range_train = math.ceil(range_train)
        index_start_prediction = index_start_train + range_train
        cls._index_start_train = index_start_train
        cls._index_start_prediction = index_start_prediction
        # break

    @classmethod
    def _target_function(cls, params):
        error_total = 0
        for i in range(cls._index_start_train, cls._index_start_prediction):
            watercut_fact = cls._data.watercuts[i]
            recovery_factor = cls._data.recovery_factors[i]
            watercut_model = cls.calc_watercut(recovery_factor, params)
            error = abs(watercut_fact - watercut_model)
            error_total += error
        return error_total

    @staticmethod
    def calc_watercut(recovery_factor, params):
        watercut_initial = params[0]
        mobility_ratio = params[1]
        parameter_alpha = params[2]
        parameter_beta = params[3]
        term_1 = (1 - recovery_factor) ** parameter_alpha
        term_2 = mobility_ratio * recovery_factor ** parameter_beta
        watercut = watercut_initial + (1 - watercut_initial) / (1 + term_1 / term_2)
        return watercut
