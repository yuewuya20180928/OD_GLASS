#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_sign_batch_20261124_2325.py
====================================
cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 23:2x
★main 本机独立复核: 台账里 9~10 条 `fixing` 但 agent 会话早已收工的挂账单 ⇒
  ★**它们把三个总工的槽位全占住 ⇒ advance.py 的 in_flight 规则 ⇒ internal 恒空 ⇒ 整条流水线停摆** ★
⇒ 本脚本 = 签收前的【机器依据采集器】(★只读·零写盘·不抄任何 agent 报告★)

逐单采集:
  ① 板三项指纹 (md5 / mtime_ns / size) ⇒ 零写板
  ② 落表三件 + 门禁三件 md5 ⇒ 零落表 + 零改既有闸
  ③ 新闸裸跑 rc + 末行
  ④ 新闸 --selftest rc + ALL TESTS PASS + 用例条数
  ⑤ 交卷页在盘 (B1~B6 段) + 真相页在盘
  ⑥ 零挂链 (state/gate_check.py 命中数 = 0)
  ⑦ 分片登记命中 (owner 自己的 fragments/*.yaml)
退出码: 0 = 采集完成 (不代表签收)
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TMP = os.path.join(PROJ, "tmp")
os.makedirs(TMP, exist_ok=True)
ENV = dict(os.environ, TMPDIR=TMP)

BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

PROTECTED = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gate_check.py": "5f370bb8cf828473e70ccc5d6412da98",
    "state/merge.py": "c9191025020fefd9b475e2573a335815",
    "state/frag_write.py": "3b383a52b4fa540f1d16a2c6f3811de8",
}

ISSUES = [
    {"id": "ISS-391", "owner": "hw-lead", "frag": "hw.yaml",
     "gate": "HW/check_fts_land_drill_same_batch.py",
     "page": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
     "handoff": "HANDOFF/2026-11-24_hw-lead_ISS391_cont1_闸判据加固与夹具真件现读.md"},
    {"id": "ISS-392", "owner": "sw-lead", "frag": "sw.yaml",
     "gate": "SW/tools/check_sw_gate_chain_coverage.py",
     "page": "SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md",
     "handoff": "HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md"},
    {"id": "ISS-393", "owner": "mech-lead", "frag": "mech.yaml",
     "gate": "MECH/check_fts_vs_generic_courtyard_delta.py",
     "page": "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
     "handoff": "HANDOFF/2026-11-24_mech-lead_ISS393_通用库件与厂件对照物差集与判决链重算.md"},
    {"id": "ISS-394", "owner": "hw-lead", "frag": "hw.yaml",
     "gate": "HW/check_seat_part_verdict_propagation.py",
     "page": "HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md",
     "handoff": "HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md"},
    {"id": "ISS-395", "owner": "hw-lead", "frag": "hw.yaml",
     "gate": "HW/check_gate10_concurrency_safety.py",
     "page": "HW/PCB/BOARD_ONEPASS_GATE10_CONCURRENCY_SAFETY.md",
     "handoff": "HANDOFF/2026-11-24_hw-lead_ISS395_钉板闸⑩并发假红机器化.md"},
    {"id": "ISS-396", "owner": "hw-lead", "frag": "hw.yaml",
     "gate": "HW/check_fts_land_drill_same_batch_sbx.py",
     "page": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
     "handoff": "HANDOFF/2026-11-24_hw-lead_ISS396_FTS改孔登记落盘.md"},
    {"id": "ISS-397", "owner": "mech-lead", "frag": "mech.yaml",
     "gate": "MECH/check_fts_seat_sample_plan.py",
     "page": "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
     "handoff": "HANDOFF/2026-11-24_mech-lead_ISS397_座体三量收样作业包.md"},
    {"id": "ISS-398", "owner": "sw-lead", "frag": "sw.yaml",
     "gate": "SW/tools/check_sw_ref_reachability_v2.py",
     "page": "SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md",
     "handoff": "HANDOFF/2026-11-24_sw-lead_ISS398_第三道病闸自测基线无关化.md"},
    {"id": "ISS-399", "owner": "mech-lead", "frag": "mech.yaml",
     "gate": "MECH/check_mech_signed_append_ledger.py",
     "page": "MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md",
     "handoff": "HANDOFF/2026-11-24_mech-lead_ISS399_MECH域已签收件追加台账设计与自守闸.md"},
    {"id": "ISS-400", "owner": "mech-lead", "frag": "mech.yaml",
     "gate": "MECH/check_machine_block_pointer_resolvable.py",
     "page": "MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md",
     "handoff": "HANDOFF/2026-11-24_mech-lead_ISS400_机器块指针可解析性清账.md"},
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def sh(cmd, timeout=900):
    try:
        r = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True,
                           timeout=timeout, env=ENV)
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return 99, "TIMEOUT"


def main():
    out = {}
    print("=" * 100)
    print("★main 本机独立复核采集器 · cron 775d9893 · 2026-11-24 23:2x")
    print("=" * 100)

    # ① 板三项
    st = os.stat(os.path.join(PROJ, BOARD))
    bmd5 = md5(os.path.join(PROJ, BOARD))
    board_ok = (bmd5 == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS and st.st_size == BOARD_SIZE)
    print("★① 板三项: md5=%s mtime_ns=%d size=%d ⇒ %s"
          % (bmd5, st.st_mtime_ns, st.st_size, "✅ 零写板" if board_ok else "❌ 变了"))

    # ② 受保护集
    bad = []
    for rel, want in PROTECTED.items():
        got = md5(os.path.join(PROJ, rel)) if os.path.isfile(os.path.join(PROJ, rel)) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    print("★② 受保护集 %d 件: %s" % (len(PROTECTED), "✅ 全同" if not bad else "❌ %s" % bad))

    for it in ISSUES:
        iid = it["id"]
        rec = {}
        print("\n" + "-" * 100)
        print("★ %s (%s)" % (iid, it["owner"]))
        # ⑤ 交付物在盘
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, it[k])
            ex = os.path.isfile(p)
            sz = os.path.getsize(p) if ex else 0
            rec[k + "_size"] = sz
            print("   %-8s %-62s %8d B %s" % (k, it[k][-62:], sz, "✅" if (ex and sz >= 4000) else "❌"))
        # 交卷页 B1~B6
        hp = os.path.join(PROJ, it["handoff"])
        if os.path.isfile(hp):
            ht = open(hp, encoding="utf-8").read()
            bs = [b for b in ("B1", "B2", "B3", "B4", "B5", "B6") if re.search(r"^#{1,4}\s*%s" % b, ht, re.M)]
            rec["blocks"] = bs
            print("   交卷页块: %s ⇒ %s" % (",".join(bs), "✅" if len(bs) >= 5 else "⚠"))
        # ③ 裸跑
        rc, o = sh("python3 %s" % it["gate"])
        lines = [l for l in o.strip().splitlines() if l.strip()]
        last = lines[-1] if lines else "(空)"
        rec["bare_rc"] = rc
        rec["bare_last"] = last[:160]
        print("   裸跑 rc=%-3d 末行: %s" % (rc, last[:110]))
        # ④ selftest
        rc2, o2 = sh("python3 %s --selftest" % it["gate"])
        lines2 = [l for l in o2.strip().splitlines() if l.strip()]
        last2 = lines2[-1] if lines2 else "(空)"
        rec["self_rc"] = rc2
        rec["self_last"] = last2[:160]
        rec["self_allpass"] = ("ALL TESTS PASS" in o2)
        m = re.search(r"(\d+)\s*/\s*(\d+)", o2)
        rec["self_ratio"] = m.group(0) if m else None
        print("   --selftest rc=%-3d ALL TESTS PASS=%s 比值=%s 末行: %s"
              % (rc2, rec["self_allpass"], rec["self_ratio"], last2[:90]))
        # ⑥ 零挂链
        hits = sh("grep -c %s state/gate_check.py" % os.path.basename(it["gate"]))[1].strip().splitlines()[0]
        rec["hook_hits"] = hits
        print("   零挂链 gate_check 命中: %s ⇒ %s" % (hits, "✅" if hits == "0" else "⚠ 已挂链"))
        # ⑦ 分片登记
        try:
            import yaml
            fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % it["frag"]), encoding="utf-8")) or {}
            blob = yaml.safe_dump(fd, allow_unicode=True)
            n = blob.lower().count(iid.lower())
            rec["frag_hits"] = n
            print("   分片 %s 命中 %s: %d ⇒ %s" % (it["frag"], iid, n, "✅" if n >= 1 else "❌"))
        except Exception as e:
            rec["frag_hits"] = -1
            print("   分片读取失败: %s" % e)
        out[iid] = rec

    with open(os.path.join(HERE, "_verify_sign_batch_20261124_2325.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\n" + "=" * 100)
    print("★采集完成 ⇒ 落盘 state/_verify_sign_batch_20261124_2325.json")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
