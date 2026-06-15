import numpy as np
from typing import Dict

class DCalculator:
    @staticmethod
    def calculate(motion_scores: Dict[str, float]) -> float:
        if not motion_scores:
            return 0.0
        return float(np.mean(list(motion_scores.values())))