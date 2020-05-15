from typing import List


class WeightDistributor(object):

    @staticmethod
    def run(x: List[float]) -> List[float]:
        n = len(x)
        t = 30
        w = [1] * (n - t)
        for i in range(t):
            w.append(i * 1)
        return w
