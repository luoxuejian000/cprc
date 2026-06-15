#!/usr/bin/env python3
import sys, time, datetime
sys.path.insert(0, ".")

from adapters.dummy_adapter import DummyAdapter
from orchestrator.orchestrator import Orchestrator
from orchestrator.session_manager import SessionManager

def main():
    context = {"llm_params": {"temperature": 1.0, "top_p": 1.0}, "logger": print}
    orch = Orchestrator(context)
    session_mgr = SessionManager("demo_log.jsonl")

    print("=" * 60)
    print("  晶脉·谐振中枢 (CPRC) v1.1 — 升级版场域健康引擎")
    print("  + 温度动力学自调谐")
    print("  + 历史自我模态")
    print("  + 决策上下文审计")
    print("=" * 60)
    print("(Ctrl+C 停止)\n")

    try:
        for i, snap in enumerate(orch.run_loop(DummyAdapter.get_evidences, interval=0.3)):
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            flag = "OK" if snap.system_state == "NORMAL" else ("!!" if snap.system_state == "ALERT" else "XX")
            print(f"[{ts}] #{i:03d}  U={snap.U:.3f} D={snap.D:.3f} A={snap.A:.3f} H={snap.H:.3f}  tau={snap.tau:.2f}  {flag}  {snap.system_state}")
            if snap.actions and snap.actions[-1].kind != "NO_OP":
                act = snap.actions[-1]
                print(f"      [ACT] {act.kind}: {act.reason}")
            trends = orch.trend_analyzer.compute(orch.fuser.history)
            session_mgr.archive(snap, meta={"trends": trends, "lambdas": snap.lambdas})
            if i >= 200:
                break
    except KeyboardInterrupt:
        print("\n[CPRC] 停止。")

if __name__ == "__main__":
    main()