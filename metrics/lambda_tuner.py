import numpy as np
from typing import List

class LambdaTuner:
    def __init__(self, lr: float = 0.08):
        self.lambdas = {"U": 0.34, "D": 0.33, "A": 0.33}
        self.lr = lr

    def tune(self, H_series: List[float]) -> dict:
        if not H_series:
            return self.lambdas
        recent_H = H_series[-1]
        if len(H_series) >= 3:
            trend = (H_series[-1] - H_series[-3]) / 2.0  # 简化趋势
        else:
            trend = 0.0
        # H低或下降趋势 -> 提高U权重求稳；H高 -> 提高D权重求发展
        tgt_U = 0.50 - 0.15 * recent_H - 0.05 * trend
        tgt_D = 0.25 + 0.20 * recent_H + 0.05 * trend
        tgt_A = 1.0 - tgt_U - tgt_D
        self.lambdas["U"] += self.lr * (tgt_U - self.lambdas["U"])
        self.lambdas["D"] += self.lr * (tgt_D - self.lambdas["D"])
        self.lambdas["A"] += self.lr * (tgt_A - self.lambdas["A"])
        total = sum(self.lambdas.values())
        for k in self.lambdas:
            self.lambdas[k] /= total
        return dict(self.lambdas)