from typing import List


class LossFunctions(object):

    @staticmethod
    def mse(x_fact: List[float], x_model: List[float]) -> float:
        """Calculates Mean Square Error."""
        mse = 0
        n = len(x_fact)
        for i in range(n):
            mse += (x_fact[i] - x_model[i]) ** 2
        mse /= n
        return mse

    @staticmethod
    def mae(x_fact: List[float], x_model: List[float]) -> float:
        """Calculates Mean Absolute Error."""
        mae = 0
        n = len(x_fact)
        for i in range(n):
            mae += abs(x_fact[i] - x_model[i])
        mae /= n
        return mae
