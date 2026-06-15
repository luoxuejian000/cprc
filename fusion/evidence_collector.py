from typing import List, Callable
from core.modality_evidence import ModalityEvidence

class EvidenceCollector:
    def __init__(self):
        self.sources: List[Callable[[], ModalityEvidence]] = []

    def register(self, source: Callable[[], ModalityEvidence]):
        self.sources.append(source)

    def collect_all(self) -> List[ModalityEvidence]:
        return [source() for source in self.sources]