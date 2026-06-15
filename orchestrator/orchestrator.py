import time
import numpy as np
from typing import List, Callable
from core.field_snapshot import FieldSnapshot, ModalityEvidence
from fusion.multimodal_fuser import MultimodalFuser
from fusion.evidence_collector import EvidenceCollector
from detection.flip_point_detector import FlipPointDetector
from detection.trend_analyzer import TrendAnalyzer
from stabilizer.decision_engine import decide_stabilization
from stabilizer.action_executor import ActionExecutor

class Orchestrator:
    def __init__(self, context: dict):
        self.fuser = MultimodalFuser()
        self.detector = FlipPointDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.executor = ActionExecutor(context)
        self.context = context
        self.context["fuser"] = self.fuser  # 供执行器访问 tau
        self.running = False

        # 历史自我模态：作为一个证据源
        def history_self_source() -> ModalityEvidence:
            if len(self.fuser.history) >= 10:
                recent_U = np.mean([s.U for s in self.fuser.history[-10:]])
                recent_H = np.mean([s.H for s in self.fuser.history[-10:]])
                trend = (self.fuser.history[-1].H - self.fuser.history[-10].H) / 10.0
                # 将历史趋势映射为存在分和稳定性
                existence = recent_U * (1.0 + 0.2 * trend)  # 趋势好则存在感增强
                stability = 1.0 - abs(trend) * 5.0  # 波动大则稳定性低
                return ModalityEvidence(
                    "history_self",
                    {"existence": max(0, min(1, existence)),
                     "stability": max(0, min(1, stability))}
                )
            else:
                return ModalityEvidence("history_self", {"existence": 0.5, "stability": 0.5})

        self.history_source = history_self_source

    def step(self, raw_evidences: List[ModalityEvidence]) -> FieldSnapshot:
        # 收集证据：外部证据 + 历史自我
        all_evidences = raw_evidences + [self.history_source()]

        snap = self.fuser.fuse(all_evidences)
        self.context["current_snapshot"] = snap

        warning = self.detector.feed(snap)
        if warning:
            logger = self.context.get("logger")
            if logger:
                msg = f"Flip warning: {warning}"
                if hasattr(logger, 'warning'):
                    logger.warning(msg)
                else:
                    logger(msg)

        trends = self.trend_analyzer.compute(self.fuser.history)
        recent_H = [s.H for s in self.fuser.history[-10:]]
        action = decide_stabilization(snap, trends["dH_dt"], trends["dA_dt"], recent_H)
        self.executor.execute(action)

        return snap

    def run_loop(self, sensor_func: Callable[[], List[ModalityEvidence]], interval: float = 0.5):
        self.running = True
        while self.running:
            raw_evidences = sensor_func()
            snap = self.step(raw_evidences)
            yield snap
            time.sleep(interval)

    def stop(self):
        self.running = False