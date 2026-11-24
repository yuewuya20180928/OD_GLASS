#!/usr/bin/env python3
"""ISS-388 · precise roster mapping: one selftest run per gate, named."""
import os, subprocess, sys, time, json

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
ROSTER = [
    "SW/tools/check_debug_pin_order_contract.py",
    "SW/tools/check_sw_board_md5_rebase_readiness.py",
    "SW/tools/check_sw_false_connectivity_gate.py",
    "SW/check_evt_charge_current_criterion.py",
    "SW/tools/check_debug_header_fw_impact.py",
    "SW/tools/check_onepass_sw_sync.py",
    "SW/tools/check_onepass_legb_sw_impact.py",
    "SW/tools/check_fp_truth_read.py",
    "SW/tools/check_sw_fp_truth_impact.py",
    "SW/tools/check_landing_trace_obligation.py",
    "SW/tools/check_sw_ref_reachability.py",
    "SW/tools/check_sw_ref_reachability_v2.py",
    "SW/tools/check_demo_panel_spec.py",
]
SHAL = os.path.join(ROOT, "tmp")
os.makedirs(SHAL, exist_ok=True)
env = dict(os.environ)
env["TMPDIR"] = SHAL
for rel in ROSTER:
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, os.path.join(ROOT, rel), "--selftest"],
                           cwd=ROOT, capture_output=True, text=True, timeout=600, env=env)
        rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        rc, out = -99, "TIMEOUT"
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    last = lines[-1] if lines else ""
    verdict = [l for l in lines if l.startswith("[PASS]") or l.startswith("[FAIL]")]
    vfail = [l.split()[1] for l in verdict if l.startswith("[FAIL]")]
    print(json.dumps({"gate": rel, "rc": rc, "t": round(time.time() - t0, 1),
                      "last": last[:90], "n_verdict": len(verdict),
                      "failed_cases": vfail[:14]}, ensure_ascii=False), flush=True)
print("DONE", flush=True)
