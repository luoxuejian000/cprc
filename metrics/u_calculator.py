import numpy as np
from typing import Dict

class UCalculator:
    @staticmethod
    def calculate(presence_scores: Dict[str, float]) -> float:
        if len(presence_scores) >= 2:
            vals = list(presence_scores.values())
            return max(0.0, min(1.0, 1.0 - float(np.std(vals))))
        elif len(presence_scores) == 1:
            return list(presence_scores.values())[0]
        else:
            return 0.5