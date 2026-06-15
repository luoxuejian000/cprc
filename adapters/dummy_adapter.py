import time, numpy as np
from typing import List
from core.modality_evidence import ModalityEvidence

class DummyAdapter:
    @staticmethod
    def get_evidences() -> List[ModalityEvidence]:
        csi_existence = np.clip(0.5 + 0.3 * np.sin(time.time()), 0, 1)
        csi_motion = np.random.rand() * 0.2
        csi_stability = 0.92 + np.random.normal(0, 0.015)
        video_person = np.clip(csi_existence * (0.7 + 0.3 * np.random.rand()), 0, 1)
        video_flow = np.random.rand() * 0.15
        thermal_existence = np.clip(0.2 + np.random.rand() * 0.2, 0, 1)
        thermal_stability = 0.94
        return [
            ModalityEvidence("csi", {"existence": csi_existence, "motion_energy": csi_motion, "stability": csi_stability}),
            ModalityEvidence("video", {"person_score": video_person, "optical_flow": video_flow}),
            ModalityEvidence("thermal", {"existence": thermal_existence, "stability": thermal_stability}),
        ]