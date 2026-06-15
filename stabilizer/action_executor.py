from typing import Any, Dict
from core.stabilizer_action import StabilizerAction

class ActionExecutor:
    def __init__(self, context: Dict[str, Any]):
        self.ctx = context

    def execute(self, action: StabilizerAction) -> None:
        if action.kind == "NO_OP":
            return
        if action.kind == "DAMP_LOCAL":
            new_tau = action.params.get("new_tau")
            if new_tau is not None:
                self.ctx.setdefault("llm_params", {})["temperature"] = new_tau
                # 同时更新融合器中的 tau
                fuser = self.ctx.get("fuser")
                if fuser:
                    fuser.tau = new_tau
        elif action.kind == "REFRESH_ANCHOR":
            if action.params.get("force_reinject_core_constraints"):
                pass  # 实际注入逻辑由外部实现
        elif action.kind == "REQUEST_CLARIFICATION":
            self.ctx["pending_clarification"] = action.params.get("choices", [])
        elif action.kind == "CHECKPOINT_SNAPSHOT":
            pass
        if "current_snapshot" in self.ctx:
            self.ctx["current_snapshot"].actions.append(action)