from typing import List


class WeightDistributor(object):

    @staticmethod
    def run(x: List[float]) -> List[float]:
        n = len(x)
        t = 30
        w = [1] * (n - t)
        w[0] = 10
        for i in range(1, t + 1):
            w.append(i)
        return w
