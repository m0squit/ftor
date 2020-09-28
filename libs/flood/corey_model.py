import numpy as np

from scipy.integrate import solve_ivp
from scipy.optimize import differential_evolution, minimize_scalar
from sklearn.metrics import mean_absolute_error
from typing import Callable, List, Dict

from libs.flood.corey_model_params import CoreyModelParams
from libs.flood.loss_function import LossFunction


def _calc_cums_oil(watercut: Callable[[float], float], Qo0: float, Ql: np.ndarray) -> np.ndarray:
    """Calulates oil cumulative productions by liquid.

    Solves initial value problem: dQo / dQl = 1 - watercut(Qo) and Qo(Ql) = Qo0.
    """
    solution = solve_ivp(fun=lambda cum_liq, cum_oil: 1 - watercut(cum_oil),
                         y0=[Qo0],
                         t_span=(Ql[0], Ql[-1]),
                         t_eval=Ql,
                         method='RK45')
    
    Qo = list(solution.y[0])
    return Qo


class CoreyModel(object):
    """Corey flood model.

    Based on modified Brooks-Corey for relative permabilities: https://petrowiki.org/Relative_permeability_models.

    Attributes:
        params: Setting parameters of model. They auto define base on input train data.
        cums_oil: Train sequence of oil cumulative production values.
        watercuts_fact: Train sequence of watercut values. Each value must be correlated with value in "cum_oil".
        watercuts_model: Model sequence of watercut values. Each value correlate with value in "cum_oil".
    """

    params_bounds = {'watercut_initial': {'min': -0.5, 'max': 1},
                     'mobility_ratio': {'min': 0.0025, 'max': 50},
                     'n_o': {'min': 1, 'max': 6},
                     'n_w': {'min': 1, 'max': 6},
                     'recovery_factor': {'min': 0.05, 'max': 0.9}}

    def __init__(self, cums_oil: np.ndarray, watercuts: np.ndarray):
        self.cums_oil = cums_oil
        self.watercuts_fact = watercuts

        self.watercuts_model: np.ndarray
        self.mae_train: float

        self.watercut_initial: float
        self.mobility_ratio: float
        self.n_o: float
        self.n_w: float
        self.recovery_factor: float

        self._create_model()

    def set_params_values(self, params: List[float]):
        self.watercut_initial = params[0]
        self.mobility_ratio = params[1]
        self.n_o = params[2]
        self.n_w = params[3]
        self.recovery_factor = params[4]

    def calc_watercut(self, cum_oil: float or np.ndarray) -> float:
        term_1 = (1 - self.recovery_factor) ** self.n_o
        term_2 = self.mobility_ratio * self.recovery_factor ** self.n_w
        watercut = self.watercut_initial + 1 / (1 + term_1 / term_2)
        return watercut

    def predict(self, cum_oil_start: float, cum_liq_start: float, rates_liq: np.ndarray) -> Dict[str, np.ndarray]:
        """Predicts oil rate depending on liquid rate.

        Calculates watercut and oil rate values for each value of given liquid rate.

        Args:
            cum_oil_start: Start value of oil cumulative production for prediction.
            cum_liq_start: Start value of liquid cumulative production for prediction.
            rates_liq: Sequence of liquid rate values for oil rate definition in forecast.
        """
        cums_liq = np.cumsum(rates_liq) + cum_liq_start
        cums_oil = _calc_cums_oil(self.calc_watercut, cum_oil_start, cums_liq)
        watercuts = self.calc_watercut(cums_oil)
        rates_oil = rates_liq * (1 - watercuts)
        return {'watercut': watercuts, 'rate_oil': rates_oil}

    def _create_model(self):
        self._fit()
        self._calc_watercut_model()

    def _fit(self):
        bounds = list(tuple(min_max.values()) for min_max in self.params_bounds.values())
        # Fit by trend
        self.set_params_values(differential_evolution(self._loss_function_trend, bounds).x)
        # Fit by last value
        self.watercut_initial = minimize_scalar(self._loss_function_last_value, bounds=bounds[0], method='Bounded')

    def _calc_watercut_model(self):
        self.watercuts_model = self.calc_watercut(self.cums_oil)
        self.mae_train = mean_absolute_error(self.watercuts_fact, self.watercuts_model)

    def _loss_function_trend(self, params: List[float]) -> float:
        self.set_params_values(params)
        self._calc_watercut_model()
        return self.mae_train

    def _loss_function_last_value(self, watercut_initial: float) -> float:
        self.watercut_initial = watercut_initial
        cum_oil = self.cums_oil[-1]
        watercut_fact = self.watercuts_fact[-1]
        watercut_model = self.calc_watercut(cum_oil)
        error = abs(watercut_fact - watercut_model)
        return error
