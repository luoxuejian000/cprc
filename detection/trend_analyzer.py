from typing import List
from core.field_snapshot import FieldSnapshot

class TrendAnalyzer:
    @staticmethod
    def compute(snapshots: List[FieldSnapshot]) -> dict:
        if len(snapshots) < 2:
            return {"dH_dt": 0.0, "dA_dt": 0.0}
        prev = snapshots[-2]
        curr = snapshots[-1]
        dt = curr.timestamp - prev.timestamp
        if dt <= 0.001:
            return {"dH_dt": 0.0, "dA_dt": 0.0}
        return {
            "dH_dt": (curr.H - prev.H) / dt,
            "dA_dt": (curr.A - prev.A) / dt,
        }