from typing import List


class LossFunctions(object):

    @classmethod
    def mse(cls, x_fact: List[float], x_model: List[float]) -> float:
        """Calculates Mean Square Error."""
        mse = 0
        n = len(x_fact)
        weights = cls._create_weights(x_fact)
        for i in range(n):
            mse += (x_fact[i] - x_model[i]) ** 2 * weights[i]
        mse /= n
        return mse

    @classmethod
    def mae(cls, x_fact: List[float], x_model: List[float]) -> float:
        """Calculates Mean Absolute Error."""
        mae = 0
        n = len(x_fact)
        weights = cls._create_weights(x_fact)
        for i in range(n):
            mae += abs(x_fact[i] - x_model[i]) * weights[i]
        mae /= n
        return mae

    @staticmethod
    def _create_weights(x):
        n = len(x)
        t = 30
        weights = [1] * (n - t)
        for i in range(30):
            weights.append(i * 1)
        return weights
