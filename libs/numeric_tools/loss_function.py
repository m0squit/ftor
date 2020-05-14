from typing import List


class LossFunction(object):

    _n: int
    _x1: List[float]
    _x2: List[float]
    _w: List[float]

    @classmethod
    def run(cls, x1: List[float], x2: List[float], w: List[float] = None, mode: str = 'mae') -> float:
        cls._n = len(x1)
        cls._x1 = x1
        cls._x2 = x2
        cls._add_weights(w)
        if mode == 'mae':
            return cls._calc_mae()
        if mode == 'mse':
            return cls._calc_mse()

    @classmethod
    def _add_weights(cls, w):
        if w is None:
            cls._w = [1] * cls._n
        else:
            cls._w = w

    @classmethod
    def _calc_mae(cls) -> float:
        """Calculates Mean Absolute Error."""
        mae = 0
        for i in range(cls._n):
            mae += abs(cls._x1[i] - cls._x2[i]) * cls._w[i]
        mae /= cls._n
        return mae

    @classmethod
    def _calc_mse(cls) -> float:
        """Calculates Mean Square Error."""
        mse = 0
        for i in range(cls._n):
            mse += (cls._x1[i] - cls._x2[i]) ** 2 * cls._w[i]
        mse /= cls._n
        return mse
