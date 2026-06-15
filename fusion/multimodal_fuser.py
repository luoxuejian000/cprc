import time
import numpy as np
from typing import List
from core.field_snapshot import FieldSnapshot
from core.modality_evidence import ModalityEvidence
from core.contradiction_edge import ContradictionEdge
from metrics.u_calculator import UCalculator
from metrics.d_calculator import DCalculator
from metrics.a_calculator import ACalculator
from metrics.h_calculator import HCalculator
from metrics.lambda_tuner import LambdaTuner

class MultimodalFuser:
    def __init__(self, window_size: int = 50):
        self.history: List[FieldSnapshot] = []
        self.lambda_tuner = LambdaTuner()
        self.tau = 1.0  # 当前温度

    def fuse(self, evidences: List[ModalityEvidence]) -> FieldSnapshot:
        now = time.time()
        for ev in evidences:
            ev.timestamp = ev.timestamp or now

        pres = {}
        mot = {}
        for ev in evidences:
            m = ev.modality
            rf = ev.raw_features
            if "existence" in rf:
                pres[m] = rf["existence"]
            elif "person_score" in rf:
                pres[m] = rf["person_score"]
            else:
                pres[m] = 0.5
            if "motion_energy" in rf:
                mot[m] = rf["motion_energy"]
            elif "optical_flow" in rf:
                mot[m] = rf["optical_flow"]
            else:
                mot[m] = 0.0

        U = UCalculator.calculate(pres)
        D = DCalculator.calculate(mot)

        contradictions = []
        names = list(pres.keys())
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                diff = abs(pres[names[i]] - pres[names[j]])
                if diff > 0.3:
                    contradictions.append(ContradictionEdge(
                        modality_a=names[i], modality_b=names[j],
                        conflict_type="presence",
                        strength=diff,
                        description=f"{names[i]}={pres[names[i]]:.2f} vs {names[j]}={pres[names[j]]:.2f}"
                    ))
        for ev in evidences:
            stab = ev.raw_features.get("stability", None)
            if stab is not None:
                internal_A = max(0.0, min(1.0, 1.0 - stab))
                if internal_A > 0.4:
                    contradictions.append(ContradictionEdge(
                        modality_a=ev.modality, modality_b=ev.modality,
                        conflict_type="internal",
                        strength=internal_A,
                        description=f"{ev.modality} internal: stability={stab:.2f}"
                    ))

        A = ACalculator.calculate(contradictions)

        # 历史化λ调谐：传入最近10个快照的H值
        H_series = [s.H for s in self.history[-10:]] if self.history else []
        lambdas = self.lambda_tuner.tune(H_series)
        H = HCalculator.calculate(U, D, A, lambdas)

        if H < 0.3:
            state = "DANGER"
        elif H < 0.5:
            state = "ALERT"
        else:
            state = "NORMAL"

        snap = FieldSnapshot(
            U=round(U,4), D=round(D,4), A=round(A,4), H=round(H,4),
            lambdas=lambdas,
            tau=self.tau,
            contradictions=contradictions,
            evidences=evidences,
            timestamp=now,
            system_state=state,
        )
        self.history.append(snap)
        if len(self.history) > 200:
            self.history.pop(0)
        return snap