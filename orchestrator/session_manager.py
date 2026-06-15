import json, time
from typing import Optional, Dict
from core.field_snapshot import FieldSnapshot

class SessionManager:
    def __init__(self, log_path: str = "session_log.jsonl"):
        self.log_path = log_path
        self.session_id = int(time.time())

    def archive(self, snap: FieldSnapshot, meta: Optional[Dict] = None):
        record = {
            "session_id": self.session_id,
            "timestamp": snap.timestamp,
            "U": snap.U, "D": snap.D, "A": snap.A, "H": snap.H,
            "system_state": snap.system_state,
            "lambdas": snap.lambdas,
            "actions": [{"kind": a.kind, "reason": a.reason, "params": a.params} for a in snap.actions],
        }
        if meta:
            record["meta"] = meta
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")