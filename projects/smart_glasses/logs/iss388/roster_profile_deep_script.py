#!/usr/bin/env python3
"""ISS-388 · roster profiling: run each candidate SW gate --selftest at two TMPDIR depths."""
import os, subprocess, sys, time, json

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
CAND = [
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
    "SW/tools/check_sw_zero_copper_grade_consistency.py",
    "SW/tools/timing_check.py",
]

DEEP = os.path.join(ROOT, "tmp", "iss388_prof_deep")   # sandbox -> ROOT/tmp/iss388_prof_deep/xxx  (depth 3)
SHAL = os.path.join(ROOT, "tmp")                        # sandbox -> ROOT/tmp/xxx                 (depth 2)

for d in (DEEP, SHAL):
    os.makedirs(d, exist_ok=True)


def run(rel, tmpdir):
    env = dict(os.environ)
    env["TMPDIR"] = tmpdir
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, os.path.join(ROOT, rel), "--selftest"],
                           cwd=ROOT, capture_output=True, text=True, timeout=600, env=env)
        rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        rc, out = -99, "TIMEOUT"
    dt = time.time() - t0
    lines = [l for l in out.splitlines() if l.strip()]
    last = lines[-1].strip() if lines else ""
    return {"rc": rc, "t": round(dt, 1), "last": last, "out": out}


res = {}
for rel in CAND:
    a = run(rel, DEEP)
    b = run(rel, SHAL)
    same = (a["rc"] == b["rc"]) and (a["out"] == b["out"])
    res[rel] = {"deep": {k: a[k] for k in ("rc", "t", "last")},
                "shal": {k: b[k] for k in ("rc", "t", "last")},
                "identical": same,
                "deep_len": len(a["out"]), "shal_len": len(b["out"])}
    print(json.dumps(res[rel], ensure_ascii=False), flush=True)
    if not same:
        # find first differing line
        al = a["out"].splitlines()
        bl = b["out"].splitlines()
        for i in range(max(len(al), len(bl))):
            x = al[i] if i < len(al) else "<EOF>"
            y = bl[i] if i < len(bl) else "<EOF>"
            if x != y:
                print("   FIRST-DIFF line %d:\n     deep: %s\n     shal: %s" % (i + 1, x, y), flush=True)
                break

with open("/tmp/iss388_profile.json", "w") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("DONE", flush=True)
