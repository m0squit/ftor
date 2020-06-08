from typing import List


class WeightDistributor(object):

    @staticmethod
    def run(x: List[float]) -> List[float]:
        n = len(x)
        w = [1] * n
        w[0] = 1000
        return w
