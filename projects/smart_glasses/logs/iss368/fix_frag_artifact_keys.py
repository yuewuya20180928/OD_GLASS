#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-368 · sw-lead · 给本单那 4 条 artifact 补上【iss368 前缀的 key】.

★**只走 state/frag_write.py** ★ (★--set-json + --set-field★ ⇒ 仍是那个原子写脚本★)
★**不许碰别人的条目** ★: 除本单那 4 条 (按 path 精确识别) 外 · 其余 265 条逐字节原样带过去
★**写前写后各记一次 md5** ★
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import yaml

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FRAG = os.path.join(PROJ, "state", "fragments", "sw.yaml")
OUTJSON = os.path.join(PROJ, "logs", "iss368", "frag_artifacts_set.json")

KEYS = {
    "SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md": "iss368_sw09_landing_patch_page",
    "SW/tools/apply_sw09_three_place_patch.py": "iss368_sw09_apply_three_place_patch",
    "SW/tools/check_sw09_patch_dryrun.py": "iss368_sw09_patch_dryrun_gate",
    "HANDOFF/2026-11-23_sw-lead_ISS368_SW09三处同批落地补丁.md": "iss368_sw09_handoff_page",
}


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    md5_before = md5_of(FRAG)
    print("写前 md5 = %s" % md5_before)
    d = yaml.safe_load(open(FRAG, encoding="utf-8"))
    arts = d["artifacts"]
    n_other = len(arts)
    others_before = [a for a in arts if a.get("path") not in KEYS]
    new = []
    hit = 0
    for a in arts:
        a = dict(a)
        p = a.get("path")
        if p in KEYS:
            hit += 1
            a["key"] = KEYS[p]
            s = a.get("summary", "")
            if "iss368_" not in s:
                a["summary"] = "%s · 键 iss368_%s" % (s, KEYS[p][len("iss368_"):])
        new.append(a)
    missing = [p for p in KEYS if p not in [a.get("path") for a in arts]]
    print("artifacts 原 %d 条 · 命中本单 %d 条 · 别人的 %d 条 (原样带过去) · 缺 %d 条"
          % (n_other, hit, len(others_before), len(missing)))
    if missing:
        print("★缺条目★ %s" % missing)
        return 1
    with open(OUTJSON, "w", encoding="utf-8", newline="") as f:
        json.dump(new, f, ensure_ascii=False, indent=1)

    # ★写前再核一次 md5 (★期间被别人改过 ⇒ 停下·不静默覆盖★) ★
    md5_again = md5_of(FRAG)
    if md5_again != md5_before:
        print("★已停止: 读完之后 sw.yaml 又被改过 (md5 %s ⇒ %s) ⇒ 不写★" % (md5_before, md5_again))
        return 1

    r = subprocess.run([sys.executable, os.path.join(PROJ, "state", "frag_write.py"),
                        "--agent", "sw-lead", "--set-json", OUTJSON, "--set-field", "artifacts"],
                       capture_output=True, text=True, cwd=PROJ)
    print("frag_write rc = %d · %s" % (r.returncode, (r.stdout or "").strip()))
    if r.returncode != 0:
        print("★stderr★ %s" % (r.stderr or "")[:500])
        return 1

    md5_after = md5_of(FRAG)
    print("写后 md5 = %s" % md5_after)
    d2 = yaml.safe_load(open(FRAG, encoding="utf-8"))
    a2 = d2["artifacts"]
    others_after = [a for a in a2 if a.get("path") not in KEYS]
    same = others_before == others_after
    print("artifacts 写后 %d 条 · 别人的 %d 条逐条相同 = %s" % (len(a2), len(others_after), same))
    print("带 iss368 key 的 artifact = %d"
          % len([a for a in a2 if str(a.get("key", "")).startswith("iss368")]))
    ok = same and len(a2) == n_other and len(others_after) == len(others_before)
    print("★结论: %s★" % ("通过" if ok else "不通过"))
    with open(os.path.join(PROJ, "logs", "iss368", "frag_artifacts_set.md5"), "w",
              encoding="utf-8", newline="") as f:
        f.write("frag_write --set-json 前 md5 = %s\nfrag_write --set-json 后 md5 = %s\n"
                "artifacts 条数 前 %d 后 %d\n别人的条目逐条相同 = %s\n"
                % (md5_before, md5_after, n_other, len(a2), same))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
