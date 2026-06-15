import numpy as np
from typing import List
from core.contradiction_edge import ContradictionEdge

class ACalculator:
    @staticmethod
    def calculate(contradictions: List[ContradictionEdge]) -> float:
        if not contradictions:
            return 0.0
        return float(np.mean([c.strength for c in contradictions]))