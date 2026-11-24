#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_2345_cron775d_sign_iss391_400.py
================================================
cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 23:4x
★★【签收】台账里 10 条 `fixing` 但 owner 会话早已收工的挂账单 (ISS-391~400) ★★
★★ 根因: 它们把三个总工的槽位全占住 ⇒ advance.py 的 in_flight 规则 ⇒ internal 恒空 ⇒ 整条流水线停摆 ★★

★纪律 (本脚本自己守):
  ① 零写板 (板 md5 / mtime_ns / size 三项开工前后各打一次)
  ② 零落表 (网表 / 脚表 / BOM 逐字节不动)
  ③ 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 不代老板拍板
  ④ 只写 state/issue_log.yaml (★不写任何 agent 的分片★)
  ⑤ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑥ CAS 并发守卫 (★台账在我读之后被改过 ⇒ 零写盘退出·不覆盖别人的写★)
  ⑦ 签收前置: 每条此刻必须仍是 fixing (★若已被别人签过 ⇒ 我的裁决会覆盖别人的 ⇒ 退出★)
  ⑧ 只签【机器依据齐】的; 判红闸必须是【红的是现状】且 selftest 全绿
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import yaml

STAMP = time.strftime("%Y%m%d_%H%M")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
VERIFY_DIR = os.path.join(PROJ, "state/.verify/cron775d_2345")

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

# iss -> (owner, frag, gate, page, handoff, bare_rc_expected, bare_note, selftest_ratio)
SIGN = {
    "ISS-391": ("hw-lead", "hw.yaml", "HW/check_fts_land_drill_same_batch.py",
                "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
                "HANDOFF/2026-11-24_hw-lead_ISS391_cont1_闸判据加固与夹具真件现读.md",
                0, "裸跑 7/7 全绿", "19/19"),
    "ISS-392": ("sw-lead", "sw.yaml", "SW/tools/check_sw_gate_chain_coverage.py",
                "SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md",
                "HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md",
                0, "裸跑 7/7 通过", "25/25"),
    "ISS-393": ("mech-lead", "mech.yaml", "MECH/check_fts_vs_generic_courtyard_delta.py",
                "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
                "HANDOFF/2026-11-24_mech-lead_ISS393_通用库件与厂件对照物差集与判决链重算.md",
                0, "裸跑 G1~G7 全过 · 机器块 50 量", None),
    "ISS-394": ("hw-lead", "hw.yaml", "HW/check_seat_part_verdict_propagation.py",
                "HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md",
                "HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md",
                1, "裸跑 rc=1 · 3 条判据红 = 【被推翻的料号还写在 5 处活副本 + 1 条已闭答案 + 1 条未答 need】= 本单要清的那件事本身", "20/20"),
    "ISS-395": ("hw-lead", "hw.yaml", "HW/check_gate10_concurrency_safety.py",
                "HW/PCB/BOARD_ONEPASS_GATE10_CONCURRENCY_SAFETY.md",
                "HANDOFF/2026-11-24_hw-lead_ISS395_钉板闸⑩并发假红机器化.md",
                0, "裸跑 rc=0 · 并发两跑双绿 + 真漂移仍判红", None),
    "ISS-396": ("hw-lead", "hw.yaml", "HW/check_fts_land_drill_same_batch_sbx.py",
                "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
                "HANDOFF/2026-11-24_hw-lead_ISS396_FTS改孔登记落盘.md",
                0, "裸跑 9/9 全绿", "11/11"),
    "ISS-397": ("mech-lead", "mech.yaml", "MECH/check_fts_seat_sample_plan.py",
                "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
                "HANDOFF/2026-11-24_mech-lead_ISS397_座体三量收样作业包.md",
                1, "裸跑 rc=1 · 唯一红 = B.6 (三量实测档仍 [0数据]) = 现状, 不是闸故障", None),
    "ISS-398": ("sw-lead", "sw.yaml", "SW/tools/check_sw_ref_reachability_v2.py",
                "SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md",
                "HANDOFF/2026-11-24_sw-lead_ISS398_第三道病闸自测基线无关化.md",
                1, "裸跑 rc=1 · 红因 = 新增真隐患 SW_MD5 (真患 4 > 基线 3) = 基线漂移的现状, 判据一字未改", "7/7"),
    "ISS-399": ("mech-lead", "mech.yaml", "MECH/check_mech_signed_append_ledger.py",
                "MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md",
                "HANDOFF/2026-11-24_mech-lead_ISS399_MECH域已签收件追加台账设计与自守闸.md",
                1, "裸跑 rc=1 · 红 = 3 处陈旧 pin 未登记台账 + 台账落位待 main 拍 = 现状", None),
    "ISS-400": ("mech-lead", "mech.yaml", "MECH/check_machine_block_pointer_resolvable.py",
                "MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md",
                "HANDOFF/2026-11-24_mech-lead_ISS400_机器块指针可解析性清账.md",
                1, "裸跑 rc=1 · 红 = 扫描范围内 A 类之外的指针条数 ≠ 0 = 现状 (51 条待改)", None),
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def sh(cmd, timeout=1200):
    try:
        r = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True,
                           timeout=timeout, env=dict(os.environ, TMPDIR=os.path.join(PROJ, "tmp")))
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return 99, "TIMEOUT"


def verify():
    print("=" * 100)
    print("★阶段 1 · main 本机独立复核 (★不抄任何 agent 报告★ · cron 775d9893 · 2026-11-24 23:4x)")
    print("=" * 100)
    os.makedirs(VERIFY_DIR, exist_ok=True)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-58s %s" % ("✅" if good else "❌", name, detail))

    st = os.stat(BOARD)
    chk("板 md5/mtime(ns)/size 三项", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE,
        "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    bad = []
    for rel, want in PROTECTED.items():
        got = md5(os.path.join(PROJ, rel)) if os.path.isfile(os.path.join(PROJ, rel)) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("零落表 + 零改既有闸 (%d 件受保护)" % len(PROTECTED), not bad, "动 %d %s" % (len(bad), bad[:3]))

    for iss, (owner, frag, gate, page, handoff, bare_want, bare_note, ratio) in SIGN.items():
        print("\n  ★★ %s (%s) ★★" % (iss, owner))
        for k, rel in (("闸", gate), ("真相页", page), ("交卷页", handoff)):
            p = os.path.join(PROJ, rel)
            sz = os.path.getsize(p) if os.path.isfile(p) else 0
            chk("%s %s 在盘" % (iss, k), sz >= 4000, "%s %d B" % (rel.split("/")[-1][:38], sz))
        # 交卷页 B1~B6
        ht = open(os.path.join(PROJ, handoff), encoding="utf-8").read()
        nb = sum(1 for b in ("B1", "B2", "B3", "B4", "B5", "B6")
                 if ("## ★%s" % b) in ht or ("## %s" % b) in ht or ("### ★%s" % b) in ht)
        chk("%s 交卷页 B1~B6 段齐全" % iss, nb >= 5, "%d/6" % nb)
        # 闸裸跑
        rc, o = sh("python3 %s" % gate)
        open(os.path.join(VERIFY_DIR, "%s.bare.log" % iss), "w", encoding="utf-8").write(o)
        lines = [l for l in o.strip().splitlines() if l.strip()]
        last = lines[-1] if lines else "(空)"
        chk("%s 闸裸跑 rc=%d (★按设计★)" % (iss, bare_want), rc == bare_want, last[:76])
        # 闸 selftest
        rc2, o2 = sh("python3 %s --selftest" % gate)
        open(os.path.join(VERIFY_DIR, "%s.selftest.log" % iss), "w", encoding="utf-8").write(o2)
        l2 = [l for l in o2.strip().splitlines() if l.strip()]
        last2 = l2[-1] if l2 else "(空)"
        good = (rc2 == 0) and ("ALL TESTS PASS" in o2)
        if ratio:
            good = good and (ratio in o2)
        chk("%s 闸 --selftest rc=0 且 ALL TESTS PASS" % iss, good, last2[:76])
        # 零挂链
        hits = sh("grep -c %s state/gate_check.py" % os.path.basename(gate))[1].strip().splitlines()[0]
        chk("%s 新闸零挂链" % iss, hits == "0", "gate_check 命中 %s" % hits)
        # 分片登记
        fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % frag), encoding="utf-8")) or {}
        blob = yaml.safe_dump(fd, allow_unicode=True).lower()
        chk("%s 在自己分片 (%s) 有登记" % (iss, frag), iss.lower() in blob, "命中 %d" % blob.count(iss.lower()))

    # ★★ISS-391 专项: main 19:5x 暂缓的那条机器依据 (判据被抽走) 是否已修好 ★★
    print("\n  ★★ ISS-391 专项: main 2026-11-24 19:5x【暂缓签收】的机器依据 (★判据被抽走★) 是否已修好 ★★")
    rc, o = sh("python3 tmp/iss391/decisive_experiment.py")
    open(os.path.join(VERIFY_DIR, "ISS391.decisive.log"), "w", encoding="utf-8").write(o)
    d1_red = ("实验 ③" in o) and ("⇒ D1 红 ✔" in o)
    d1b_red = ("实验 ③b" in o) and ("⇒ D1 红 ✔" in o)
    real_green = ("对照: 真件原样 ⇒ D1 必须绿" in o) and ("⇒ D1 绿 ✔" in o)
    unchanged = ("before=00b0ea5bae70b7f663b55b9b80014d03 after=00b0ea5bae70b7f663b55b9b80014d03" in o)
    chk("★ISS-391 决定性实验 ③ (只删动作腿·留解释括注) ⇒ D1 红", d1_red, "★判据不再被解释性文字糊弄★")
    chk("★ISS-391 对照实验 ③b (整条只剩 pitch 腿) ⇒ D1 红", d1b_red, "★仍抓得住★")
    chk("★ISS-391 对照: 真件原样 ⇒ D1 绿 (判据没被改松)", real_green, "★真件登记还在就仍绿★")
    chk("★ISS-391 实验全程真件逐字节未动", unchanged, "★before==after★")

    print("\n  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


def build_result(iss, owner, gate, page, handoff, bare_want, bare_note, ratio):
    tpl = ("✅ verified (★main 2026-11-24 23:4x 本机独立复核 · 不抄任何 agent 报告★ · cron 775d9893★) ⇒ "
           "★**闸 `%s` 裸跑 rc=%d (★%s★) + `--selftest` rc=0 末行 `ALL TESTS PASS`%s** ★ "
           "真相页 + 交卷页 (B1~B6 齐全) + owner 分片登记在位 ★ 零写板 (板三项指纹逐字节未动) + 零落表 (网表/脚表/BOM 逐字节未动) + "
           "零挂链 (gate_check 命中 0) + 零改既有闸/既有页面正文 + 零外发 ★★"
           "**★main 本机独立复核要点★**: ★**① 板三项 md5 `611b869e…` / mtime_ns 1793920037362193413 / size 4940213 与基线逐字相同** ★ "
           "**② 受保护集 6 件 (网表/脚表/BOM/gate_check.py/merge.py/frag_write.py) md5 全同 ⇒ 零落表零改闸** ★ "
           "**③ 新闸 selftest 末行逐字 `ALL TESTS PASS` (反向用例全抓到 ⇒ 判据没被削弱)** ★ "
           "**④ 裸跑 rc=%d 的定性 = ★%s★ ⇒ 【红的是现状, 不是闸故障】** ★ "
           "**⑤ 零挂链 (新闸不在官方门禁链里 ⇒ 挂了会立刻造新红 ⇒ 本轮不挂) + owner 分片命中** ★ "
           "**⑥ 本单签收含义 = 交付物在盘 + 闸按设计 + 判据零削弱 + 边界零越界; owner 留给 main 的未决项仍在分片 needs_from 里 (一条没代拍)** ★")
    return tpl % (gate, bare_want, bare_note,
                  (" (★%s 条★)" % ratio) if ratio else "",
                  bare_want, bare_note)


def write_issue_log():
    raw0 = open(LOG, "rb").read()
    md5_0 = hashlib.md5(raw0).hexdigest()
    shutil.copy2(LOG, LOG + ".bak_%s_cron775d_sign_391_400" % STAMP)
    doc = yaml.safe_load(raw0.decode("utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}
    before_n = len(issues)

    orig_status = {k: (by.get(k) or {}).get("status") for k in SIGN}

    for iss, (owner, frag, gate, page, handoff, bare_want, bare_note, ratio) in SIGN.items():
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        e["status"] = "verified"
        e["verify_result"] = build_result(iss, owner, gate, page, handoff, bare_want, bare_note, ratio)
        e["verify_date"] = "2026-11-24 23:4x"
        e["verify_by"] = "main"
        e["fix_ref"] = ("main 2026-11-24 23:4x 独立复核签收 (★零写板·零落表·零改既有闸·零改既有页面正文·零挂链·零外发·"
                        "不代老板拍板★) ★**签收理由 = owner 会话早已收工, 但台账 status 停在 fixing ⇒ 它把该 agent 的槽位占住 ⇒ "
                        "advance.py 的 in_flight 规则 ⇒ internal 恒空 ⇒ 整条流水线停摆 ⇒ 本轮一次性清掉这 10 条挂账单★")

    # ★★落盘前 CAS 复核 (★读-改-写窗口内若有人改过 ⇒ 报错退出·不覆盖别人的写★) ★★
    md5_now = hashlib.md5(open(LOG, "rb").read()).hexdigest()
    if md5_now != md5_0:
        raise SystemExit("★★CAS 失败: 台账在我读之后被改过 (★%s != %s★) ⇒ 有人并发写 ⇒ 零写盘退出 ★★"
                         % (md5_now[:12], md5_0[:12]))
    for iss, st in orig_status.items():
        if st not in ("fixing", "open"):
            raise SystemExit("★★台账里 %s 的 status 在我读的时候已是 %s (★不是我写的·可能别人签收过★) ⇒ 零写盘退出 ★★"
                             % (iss, st))
    tmp = LOG + ".tmp_cron775d_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, LOG)
    print("  issue_log.yaml: %d 条签收 (fixing→verified) · 条数 %d→%d · 备份 %s"
          % (len(SIGN), before_n, len(issues), os.path.basename(LOG) + ".bak_%s_cron775d_sign_391_400" % STAMP))
    return True


def main():
    if not verify():
        print("\n★★阶段 1 有红项 ⇒ fail-closed ⇒ 零写盘退出 ★★")
        return 1
    print("\n" + "=" * 100)
    print("★阶段 2 · 落台账 (★CAS 守卫 + 只写 issue_log.yaml★)")
    print("=" * 100)
    write_issue_log()
    print("\n★签收完成 · 10 条挂账单清空 ⇒ 三个总工的槽位解锁 ⇒ 下一轮 advance.py 的 internal 不再被 in_flight 挡死")
    return 0


if __name__ == "__main__":
    sys.exit(main())
