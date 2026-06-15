from typing import Optional, Dict, List
from core.field_snapshot import FieldSnapshot

class FlipPointDetector:
    def __init__(self, window_size: int = 30):
        self.history: List[FieldSnapshot] = []
        self.alert_threshold = 0.3
        self.acceleration_threshold = 0.05

    def feed(self, snap: FieldSnapshot) -> Optional[Dict]:
        self.history.append(snap)
        if len(self.history) < 5:
            return None
        recent = self.history[-5:]
        H_vals = [s.H for s in recent]
        A_vals = [s.A for s in recent]
        dH_dt = (H_vals[-1] - H_vals[0]) / max(0.001, len(recent))
        dA_dt = (A_vals[-1] - A_vals[0]) / max(0.001, len(recent))
        alerts = []
        if snap.H < self.alert_threshold:
            alerts.append("H_critical")
        if dA_dt > self.acceleration_threshold and snap.A > 0.4:
            alerts.append("A_accelerating")
        if dH_dt < -0.02 and dA_dt > 0.02:
            alerts.append("H_A_divergence")
        if alerts:
            return {
                "type": "flip_warning",
                "paths": alerts,
                "H": snap.H, "A": snap.A,
                "dH_dt": dH_dt, "dA_dt": dA_dt,
                "timestamp": snap.timestamp,
            }
        return None