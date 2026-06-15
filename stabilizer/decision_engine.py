import numpy as np
from typing import List, Optional
from core.field_snapshot import FieldSnapshot, StabilizerAction

def decide_stabilization(
    snap: FieldSnapshot,
    dH_dt: float,
    dA_dt: float,
    recent_H: List[float],
    last_action_kind: Optional[str] = None,
) -> StabilizerAction:
    H, A, U, tau = snap.H, snap.A, snap.U, snap.tau
    num_contradictions = len(snap.contradictions)

    # 1) 明显失谐：H跌破安全线
    if H < 0.28:
        return StabilizerAction(
            kind="CHECKPOINT_SNAPSHOT",
            reason=f"H={H:.3f} critically low; anchor then damp",
            params={"keep_last_n_turns": 3, "freeze_core_anchors": True},
        )

    # 2) 矛盾饱和/翻转前兆
    if A > 0.55 and dA_dt > 0.08:
        if num_contradictions >= 2:
            return StabilizerAction(
                kind="REQUEST_CLARIFICATION",
                reason=f"A={A:.3f} rising; cross-modal conflict; ask user",
                params={"choices": ["确认目标", "确认环境扰动", "继续自动但降置信"]},
            )
        else:
            # 内部漂移 -> 用温度动力学调节
            new_tau = _compute_resonance_tau(tau, recent_H)
            return StabilizerAction(
                kind="DAMP_LOCAL",
                reason=f"A={A:.3f} rising w/o cross-modal; tau adjusted via resonance",
                params={"new_tau": new_tau},
            )

    # 3) 锚点衰减
    if U < 0.35 and H < 0.45:
        return StabilizerAction(
            kind="REFRESH_ANCHOR",
            reason=f"U={U:.3f} low; refresh core anchors",
            params={"force_reinject_core_constraints": True},
        )

    # 4) 探索过头
    if tau > 1.2 and A > 0.2:
        new_tau = _compute_resonance_tau(tau, recent_H)
        return StabilizerAction(
            kind="DAMP_LOCAL",
            reason=f"tau={tau:.2f} high while A>0; tau adjusted",
            params={"new_tau": new_tau},
        )

    return StabilizerAction(kind="NO_OP", reason="within resonant band")

def _compute_resonance_tau(tau_prev: float, recent_H: List[float]) -> float:
    if len(recent_H) < 3:
        return tau_prev
    dH_dt = recent_H[-1] - recent_H[-2]
    d2H_dt2 = dH_dt - (recent_H[-2] - recent_H[-3])
    alpha, beta, gamma = 0.1, 0.05, 0.01
    d_ln_tau = -alpha * dH_dt / (tau_prev**2 + 1e-8) + beta * d2H_dt2 / (tau_prev + 1e-8) - gamma
    new_tau = tau_prev * np.exp(d_ln_tau)
    return max(0.1, min(2.0, new_tau))