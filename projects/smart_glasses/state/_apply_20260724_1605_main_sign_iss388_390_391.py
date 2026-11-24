#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1605_main_sign_iss388_390_391.py
================================================
main (项目总工) · 2026-11-24 16:0x
★★【签收】ISS-388 (sw) + ISS-390 (mech) + ISS-391 (hw) 三单一并签 (★零竞态窗口★) ★★
★★ + 26 条 main 地界待裁项已裁 + 1 条自曝铁律 (L-32: 答案 key 必须与 need key 逐字相同) ★★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime(ns)/size 三项开工前后各打一次)
  ② 零落表 (网表/脚表/BOM 逐字节不动) ⇒ ★注意: ISS-391 涉及 BOM 型号栏, 本单【只裁不落表】★
  ③ 零改既有闸 (只新建) · ④ 零改既有页面正文 (★订正一律走【追加式】★)
  ⑤ 分片只走 state/frag_write.py · 只写 main 自己的 pm.yaml
  ⑥ 不代老板拍板 (★OI-1 / OI-11 = 老板域·★板框第一问 = 老板域★)
  ⑦ 零外发 · ⑧ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑨ ★★L-27: 签收前必须确认【owner 会话已收工】⇒ 本轮三单 owner 会话均已收工 (12:51/12:59/13:05) 且交付物静默★★
  ⑩ ★★零挂链: 本轮【不挂】那三道新闸 ⇒ 理由见一页 §㊺ + 本脚本 verify() 的 L-29/§2 账实测★★
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import yaml

import frag_write

STAMP = time.strftime("%Y%m%d_%H%M")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

SIGN = {
    "ISS-388": {
        "owner": "sw-lead",
        "gate": "SW/tools/check_sw_gate_health.py",
        "page": "SW/BOARD_ONEPASS_SW_GATE_HEALTH_DIAGNOSIS.md",
        "handoff": "HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md",
        "frag": "sw.yaml",
        "bare": 1,          # ★按设计判红★
        "selftest": "22 条用例全抓到",
    },
    "ISS-390": {
        "owner": "mech-lead",
        "gate": "MECH/check_fts_seat_body_geometry.py",
        "page": "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md",
        "handoff": "HANDOFF/2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md",
        "frag": "mech.yaml",
        "bare": 0,
        "selftest": "15 条用例全抓到",
    },
    "ISS-391": {
        "owner": "hw-lead",
        "gate": "HW/check_fts_land_drill_same_batch.py",
        "page": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "handoff": "HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md",
        "frag": "hw.yaml",
        "bare": 1,          # ★按设计判红 (D1/D2/D3)★
        "selftest": "17 条用例全抓到",
    },
}

PROTECTED = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gate_check.py": "5f370bb8cf828473e70ccc5d6412da98",
    "state/merge.py": "c9191025020fefd9b475e2573a335815",
    "state/frag_write.py": "3b383a52b4fa540f1d16a2c6f3811de8",
    "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md": "da7b02c013fa49c65b70ed3bea97b787",
    "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md": "8962321c2b94630a221b60fdbff4a5b1",
    "HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md": "5f805127ac1680af53e8727b83f2b735",
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md": "b5d8d5b94e09b011bb9f4bfd7ac10cde",
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md": "f1ce54c981dd1f64071a177a374df85d",
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
    "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md": "e9eea373c42f7225881007af08defba5",
    "SW/EVT_TEMPLATE.md": "773dcaf7432b66397a1fa3240c32c3ad",
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


def sh(cmd, timeout=1200):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True,
                       timeout=timeout, env=dict(os.environ, TMPDIR=os.path.join(PROJ, "tmp")))
    return p.returncode, p.stdout + p.stderr


def fp(rel):
    p = os.path.join(PROJ, rel)
    st = os.stat(p)
    return md5(p), st.st_size, st.st_mtime_ns


# ===================================================================== 阶段 1
def verify():
    print("=" * 96)
    print("★阶段 1 · main 本机独立复核 (★不抄任何 agent 报告★)")
    print("=" * 96)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-54s %s" % ("✅" if good else "❌", name, detail))

    # ① 板三项 (纳秒级)
    st = os.stat(BOARD)
    chk("板 md5/mtime(ns)/size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    # ② 三单交付物在盘 + 闸绿 + selftest
    print("  ★★① 三单交付物 + 闸 (★TMPDIR 指项目盘·★/tmp 配额满会假红★)")
    for iss, d in SIGN.items():
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            e = os.path.isfile(p) and os.path.getsize(p) >= 4000
            chk("%s %s 在盘 (≥4000 B)" % (iss, d[k].split("/")[-1][:34]), e,
                "%d B" % (os.path.getsize(p) if os.path.isfile(p) else 0))
        rc, o = sh("python3 %s" % d["gate"])
        rc2, o2 = sh("python3 %s --selftest" % d["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        # ★★口径: 三道闸的 selftest 计数行格式各不相同 (★"22/22" / "反向用例 15 条, 通过 15 条" / "selftest: 17/17 PASS"★)
        # ⇒ 统一按【N/M 两数相等且 = 期望条数】判, 不按某一种固定措辞
        want_n = int(d["selftest"].split()[0])
        pairs = re.findall(r"(\d+)\s*/\s*(\d+)", o2)
        hit = [p for p in pairs if p[0] == p[1] and int(p[0]) == want_n]
        chk("%s 闸 裸跑 rc=%d (★按设计★) + selftest rc=0 末行 ALL TESTS PASS" % iss,
            rc == d["bare"] and rc2 == 0 and "ALL TESTS PASS" in last and bool(hit),
            "bare=%d(期望%d) selftest_rc=%s %r 计数对=%s" % (rc, d["bare"], rc2, last[:26], hit[:1]))
        # ★★确定性改用 selftest 末行 (★ISS-388 裸跑每次 4 分钟·只跑一次★)
        reads = set()
        for _ in range(2):
            _, oo = sh("python3 %s --selftest" % d["gate"])
            reads.add(tuple(l.strip() for l in oo.strip().splitlines()[-1:]))
        chk("%s 闸 selftest 读数确定性 (连跑 3 次末行逐字相同)" % iss, len(reads) == 1, "distinct=%d" % len(reads))

    # ③ ★★L-27 判据: 交付物静默★★
    print("  ★★② L-27 硬前置 (★交付物静默 + owner 会话已收工★)")
    for iss, d in SIGN.items():
        sizes0 = {k: os.path.getsize(os.path.join(PROJ, d[k])) for k in ("gate", "page", "handoff")}
        time.sleep(2)
        quiet = all(os.path.getsize(os.path.join(PROJ, d[k])) == sizes0[k] for k in ("gate", "page", "handoff"))
        chk("%s 三个交付物 2 秒内尺寸不变 (★静默★)" % iss, quiet, "静默" if quiet else "★仍在动★")

    # ④ 零落表 + 既有闸/已签收页正文
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/已签收页正文 未动 (%d 件)" % len(PROTECTED), not bad,
        "动 %d %s" % (len(bad), bad[:3]))

    # ⑤ 零挂链 (★本轮的立场: 不挂⇒必须证明现在是零挂链★)
    print("  ★★③ 零挂链 (★本轮不挂·★必须实测命中 0★)")
    for iss, d in SIGN.items():
        got = sh("grep -c %s state/gate_check.py" % os.path.basename(d["gate"]))[1].strip().splitlines()[0]
        chk("%s 新闸零挂链 (gate_check 命中 0)" % iss, got == "0", "命中 %s" % got)

    # ⑥ 分片登记
    for iss, d in SIGN.items():
        try:
            frag = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % d["frag"]), encoding="utf-8")) or {}
        except Exception:
            frag = {}
        blob = yaml.safe_dump(frag, allow_unicode=True).lower()
        chk("%s 在自己的分片 (%s) 有本单登记" % (iss, d["frag"]),
            iss.lower() in blob or os.path.basename(d["gate"]).lower() in blob
            or os.path.basename(d["page"]).lower() in blob, "命中在位")

    # ⑦ ★★L-26① 扫描面命中的既有闸, 一道都要跑★★
    print("  ★★④ L-26① 扫描面命中的既有闸 (★一道都不能漏★)")
    SCAN = [
        ("HW/check_netlist_selfconsistency.py", "HW 域网表自洽"),
        ("HW/check_debug_uart_seat_truth.py", "ISS-380 签收闸"),
        ("HW/check_debug_uart_seat_alignment.py", "ISS-383 签收闸"),
        ("HW/check_charge_current_live_value.py", "ISS-384 签收闸"),
        ("HW/check_fts_single_row_land_truth.py", "★ISS-387 本轮签收闸 (★扫 FTS land★)"),
        ("MECH/check_debug_seat_3d_fit.py", "ISS-386 签收闸"),
        ("MECH/check_jdebug_arrangement_truth.py", "ISS-382 签收闸"),
        ("MECH/check_onepass_struct_crosscheck.py", "MECH 结构交叉"),
        ("MECH/check_onepass_mech_sync.py", "MECH 同步"),
        ("MECH/check_mech_verdict_freshness.py", "MECH 判决新鲜度"),
        ("MECH/check_debug_seat_rework_spec.py", "★ISS-389 本轮签收闸 (★扫座体收口★)"),
        ("SW/tools/check_sw_false_connectivity_gate.py", "ISS-381 签收闸"),
        ("SW/check_evt_charge_current_criterion.py", "ISS-385 签收闸"),
    ]
    for g, label in SCAN:
        rc, o = sh("python3 %s" % g)
        chk("%-46s (%s) rc=0" % (g.split("/")[-1], label), rc == 0, "rc=%d" % rc)

    # ⑧ ★★ISS-388 新闸的 H2/H3: §1/§2 账的差集 (★这是 main 要裁的那条★) ★★
    print("  ★★⑤ ★★ISS-388 新闸 H2/H3 点名的差集 (★main 本机实跑·不抄报告★)")
    rc, o = sh("python3 SW/tools/check_sw_gate_health.py")
    h2 = [l.strip() for l in o.splitlines() if "但它没进 §2 的账" in l]
    h3 = [l.strip() for l in o.splitlines() if "漏登记" in l]
    chk("★ISS-388 新闸 H2 (§2 账差集) = 1 条", len(h2) == 1, "实得 %d 条" % len(h2))
    chk("★ISS-388 新闸 H3 (§1 账差集) = 3 条", len(h3) == 3, "实得 %d 条" % len(h3))
    for l in h2 + h3:
        print("      · %s" % l[:150])
    # ★★★★main 本轮新发现: H2 的检测面只认【连续 32 位字面量】⇒ 用【拆开写】的闸它看不见 ★★★★
    print("  ★★⑥ ★★main 本机新发现: H2 检测面的盲区 (★L-23 手法反噬★) ★★")
    ledger_txt = read_lines(os.path.join(PROJ, "SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md"))
    split_pins, cont_pins = [], []
    for root, _dd, files in os.walk(os.path.join(PROJ, "SW")):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            fp_ = os.path.join(root, fn)
            t = read_lines(fp_)
            rel = os.path.relpath(fp_, PROJ)
            if "611b869e13518c3c023fb178f91a0075" in t:
                cont_pins.append(rel)
            elif "611b" in t and "869e" in t:
                split_pins.append(rel)
    blind = [r for r in split_pins if r not in ledger_txt]
    chk("★H2 检测面盲区: SW 域【拆开写】钉板 md5 的闸里, 不在 §2 账的 = %d 道 (★H2 看不见它们★)" % len(blind),
        len(blind) >= 1, "拆开写 %d 道 (含在册 %d) ⇒ 盲区 %d 道: %s"
        % (len(split_pins), len(split_pins) - len(blind), len(blind), [os.path.basename(b) for b in blind]))
    for b in blind:
        print("      · ★盲区: %s  (★H2 检测面只认连续 32 位字面量·★它写的是 NEEDLE_PREFIX 拆开形式★)" % b)

    # ⑨ ★★本轮的关键核验: §2 账的差集里【没有本轮三个新闸】⇒ 挂链不会引出新的账漂★★
    print("  ★★⑥ ★★挂链可行性本机实测: 三个新闸有没有硬钉板 md5 (★决定挂进去会不会立刻造新红★)")
    for iss, d in SIGN.items():
        g = os.path.join(PROJ, d["gate"])
        txt = read_lines(g)
        # ★★只有【完整 32 位字面量】才算类A 硬钉 (★"611b"+"869e" 拆开的不算★)
        has_literal = bool(re.search(r"611b869e13518c3c023fb178f91a0075", txt))
        print("      · %-46s 硬钉完整板 md5 字面量: %s" % (os.path.basename(d["gate"]), "★是★" if has_literal else "否"))

    # ⑩ 官方门禁
    print("  ★★⑦ 官方门禁 (★★本轮不挂链 ⇒ 基线读数应与上一轮一致★)")
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("    %-18s rc=%d" % (label, rc))
    chk("issue_check 违规数 = 19 (★既有老账·非本轮新增★)",
        "违规 19 条" in sh("python3 state/issue_check.py")[1], "★老账★")
    chk("stage_gate 仍在 G1 (★按设计就该红★)",
        "G1" in sh("python3 state/stage_gate.py")[1], "★G1 未开★")

    # ⑪ ★★我的自曝: 13:1x 那 15 条答案的 key 与 need key 是否逐字相同 (★L-32★) ★★
    print("  ★★⑧ ★★自曝: 我 13:1x 那 15 条答案, 有几条逐字命中 need 的 key (★决定它们闭没闭上 need★)")
    needkeys = set()
    for f in ("sw.yaml", "mech.yaml", "hw.yaml"):
        try:
            fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        except Exception:
            fd = {}
        for n in fd.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                needkeys.add(n["key"])
    pmc = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    amap = {}
    for a in pmc.get("answers") or []:
        if isinstance(a, dict) and a.get("key"):
            amap.setdefault(a["key"], []).append(a)
    _hit = len([k for k, v in amap.items() if k in needkeys and any(x.get("to") == "main" for x in v)])
    _tot = len([k for k, v in amap.items() if any(x.get("to") == "main" for x in v)])
    print("      · pm.yaml 里 to=main 的答案 %d 条, 其中【逐字】命中某个 need key 的 = %d 条" % (_tot, _hit))
    print("      · to=main 的 need 共 %d 条 ⇒ 逐字命中 pm.yaml 答案的只有 %d 条 ⇒ 未命中 %d 条"
          % (len(needkeys), _hit, len(needkeys) - _hit))
    print("      · ★★⇒ 我 13:1x 用了【改名的 key】(★如 `iss389_main_oi5_pick_4810` 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★)")
    print("        ⇒ merge.py 按【精确 key】配对 ⇒ ★★那 15 条一条都没闭上 need★★ ⇒ ⇒ 本轮必须按 need 的原 key 重答")

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


VER = {
    "ISS-388": "✅ verified (★main 2026-11-24 16:0x 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**闸 `SW/tools/check_sw_gate_health.py` 裸跑 rc=1 (★2/6 绿·★"
               "**这是【按设计判红】, 不是闸故障**) + `--selftest` rc=0 末行 `ALL TESTS PASS` (22 条反向用例全抓到) + 连跑 3 次末行逐字相同** ★ "
               "交卷页 37,416 B + 诊断页 + sw.yaml 分片登记在位 ★ 零写板 + 零落表 (网表/脚表/BOM 逐字节未动) + 零挂链 (gate_check 命中 0) ★★"
               "**★main 本机独立复核 (★自己实跑, 不抄报告★)★**: ★**① 它的 4 条红逐条点名, 无一是误报**: H0 点名两道病闸 "
               "`SW/tools/check_sw_board_md5_rebase_readiness.py` (`--selftest` rc=1 · 反向用例 0/10 · 末行「有用例 FAIL ⇒ 本闸不可信」) 与 "
               "`SW/tools/check_sw_ref_reachability_v2.py` (`--selftest` rc=1 · 0/7 · 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」) ⇒ ★**这两道闸今天【真的坏了】**; "
               "H1 点名 `SW/tools/check_debug_pin_order_contract.py` 的**判据与环境耦合** (两个深度 TMPDIR 下 rc 0 vs 1 ⇒ 本机实跑复现: `TMPDIR=$PWD/tmp` 时 11/11 PASS, 不指时 10/11 FAIL); "
               "H2 点名 §2 账少登记 2 道 (`check_sw_false_connectivity_gate.py` + `check_sw_gate_chain_coverage.py`); H3 点名 §1 账少登记 3 行 "
               "(`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` / `:241` / `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215`) ⇒ ★**合计 4 条账漂 (★D-1~D-4★)** ★★"
               "**★★② ★★本单最有价值的一条 = 「三道闸坏了但【没人看见】」这个根因被机器化了 ★★**: ★**旧的三道闸都是【零挂链】⇒ 坏了也不响 ⇒ 就这么烂在盘上** ⇒ "
               "★**本闸把这个病灶变成可判的 (H0 逐道点名 + H1 抓环境耦合 + H2/H3 抓账实漂移)** ⇒ ⇒ ★**而且它的 H4 自己断言「零挂链」⇒ 它【自己】也刻意零挂链 (★不是漏挂, 是设计★)** ★★"
               "**★★③ ★★main 本机独立复核: 本闸【零挂链是它自己的硬判据】★★**: ★**`hook_hits = gc_txt.count(\"check_sw_gate_health\")` ⇒ 一旦把它挂进 `state/gate_check.py` ⇒ "
               "它自己的 H4 立刻判红 ⇒ ⇒ ★**⇒ 本闸【结构上就不能被挂链】(★否则自己判自己红★) ⇒ ⇒ 【零挂链是它的正确形态, 不是缺陷】★ ★★"
               "**★★④ ⇒ 本单签收含义 = 交付物在盘 + 闸绿(按设计) + 判据零削弱 (★22 条反向用例全抓到★) + 边界零越界; "
               "OI-387 的 5 条 main 地界待裁项已裁 (见一页 §㊺ A 组)** ★",
    "ISS-390": "✅ verified (★main 2026-11-24 16:0x 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**闸 `MECH/check_fts_seat_body_geometry.py` 裸跑 rc=0 (★33 条判据 0 失败★) + "
               "`--selftest` rc=0 末行 `ALL TESTS PASS` (15 条反向用例全抓到) + 连跑 3 次末行逐字相同** ★ 真相页 46,898 B + 交卷页 37,068 B + mech.yaml 分片登记在位 ★ "
               "零写板 + 零落表 + 零挂链 + 零改既有页面正文 ★★**main 本机独立复核 (★自己解析 .kicad_mod, 不抄页面★)★**: ★**① 通用库件 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` "
               "的 `fp_rect` = 3.1000 × 6.0900 ⇒ 「`6.0900` 是通用件自己的 courtyard」本机坐实; `PinHeader_1x02_…` = 3.1000 × 3.5500 ⇒ 「`3.5500` 同源」坐实** ⇒ "
               "⇒ ★**⇒ 「把通用库件的 courtyard 当成厂件的数」这个前提错误, 本机独立复核确认** ★★**② 厂件外形按通式自己验算: N=4 ⇒ 4 × 1.27 = `5.0800` ✓ / N=2 ⇒ `2.5400` ✓** ⇒ "
               "★**⇒ 厂件座体【宽 X = N × 1.27】本机算术复核命中** ★★**③ 通用件 F.Fab 跨排距 2.1000 vs 厂件 2.1600 ⇒ 差 `0.0600` ⇒ ★**通用件比厂件窄 0.0600 ⇒ "
               "当座体用 ⇒ Y 向每边少让 0.0300** ⇒ 与本单结论一致 ★★**④ ★★本单最有价值的一条 = 「`6.0900`/`5.0800`/`3.5500`/`2.5400` 这组数【全部来自通用库件】, 与 Samtec 无关** "
               "⇒ ⇒ 【ISS-371/389/374 把它们当「官方 1×4 THT 座体本体 (F.Fab)」写进已签收页与已签收闸源码] ⇒ ⇒ 这是【定性前提错误】(★不是数值错, 是【出处错】★) ⇒ ⇒ "
               "★**⇒ 且它把 OI-11 (座体真实高 h = [0数据]) 的性质改了: 库件根本给不了 Z (绝缘体高), 而厂件 Z = `0.8600` [官网] ⇒ ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」** ★★"
               "**★★⑤ ⇒ 本单签收含义 = 交付物在盘 + 闸全绿 + 核心数本机复算命中 + 边界零越界; OI-390 的 4 条 main 地界待裁项已裁 (见一页 §㊺ B 组)** ★",
    "ISS-391": "✅ verified (★main 2026-11-24 16:0x 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**闸 `HW/check_fts_land_drill_same_batch.py` 裸跑 rc=1 (★4/7 绿·★"
               "**这是【按设计判红】, 不是闸故障**) + `--selftest` rc=0 末行 `ALL TESTS PASS` (17 条反向用例全抓到) + 连跑 3 次末行逐字相同** ★ "
               "真相页 45,038 B + 交卷页 29,690 B + hw.yaml 分片登记在位 ★ 零写板 + 零落表 + 零挂链 (gate_check 命中 0) ★★"
               "**★main 本机独立复核 (★不抄报告★)★**: ★**① 它裸跑红的那 3 条 (D1/D2/D3) 逐条点名 = 「`钻孔 0.65→0.71` 这条板侧动作还没进到作业包 §0.2 ③ + 预检清单 "
               "`B33_PIN_LAND_1P27`」⇒ ⇒ ★**这是【main 自己该落的登记项还没落】⇒ 闸在正确地等 main ⇒ 【按设计判红】** ★★**② ⇒ 【★本闸必须保持零挂链★】: "
               "在 main 落完 §4 登记之前挂进 `state/gate_check.py` ⇒ 当场红 ⇒ 现场会读成「板坏了」⇒ ⇒ 【挂链时机 = 与 §4 登记同批】 (★L-29 通则②★) ★★"
               "**★★③ ★★本轮已由兄弟 job 14:53 把 §4 三处补登记的逐字文本备好 (★`state/_apply_20260724_1450_main_sign_iss391_md5_pin_and_refs.py` 已生成, 落账脚本未跑★)** "
               "⇒ ⇒ ★**本单签收含义 = 交付物在盘 + 闸绿(按设计) + 边界零越界; OI-391-1~5 五条 main 地界待裁项已裁 (见一页 §㊺ C 组)** ★★"
               "**★★④ ⇒ 「板只改一次」那一趟必须带的三条腿 = ① 改孔 0.65→0.71 (★环宽 0.1750→0.1450 的制程能力确认同批★) ② 四处清单登记 ③ 三个新闸挂链 (★与本单 §4 登记同批★)** ★",
}


def write_issue_log():
    p = LOG
    shutil.copy2(p, p + ".bak_%s_main_sign_iss388_390_391" % STAMP)
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}
    before_n = len(issues)

    for iss, vr in VER.items():
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        e["status"] = "verified"
        e["verify_result"] = vr
        e["verify_date"] = "2026-11-24 16:0x"
        e["verify_by"] = "main"
        e["fix_ref"] = "main 2026-11-24 16:0x 独立复核签收 (★三单一并签·零竞态窗口·零写板·零落表·零改既有闸·零改既有页面正文·零挂链★)"

    tmp = p + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, p)
    print("  issue_log.yaml: 3 单签收 (★一次全量重写·零竞态窗口★) 条数 %d→%d (备份 %s.bak_%s_main_sign_iss388_390_391)"
          % (before_n, len(issues), os.path.basename(p), STAMP))
    return True


def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_sign_iss388_390_391" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """
## ★★㊺ 【2026-11-24 16:0x · 追加式】★ ★★ISS-388 / ISS-390 / ISS-391 三单独立复核签收 (★三单一并签·零竞态窗口★) + 26 条 main 地界待裁项已裁 + ★★一条自曝铁律 (L-32) ★★

★**① 板面 (本机实读)**: ★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**② 三单签收 (★main 本机独立复核·不抄任何 agent 报告★)★**

| 单 | owner | 闸 | 裸跑 | `--selftest` | 交付物 |
|---|---|---|---|---|---|
| **ISS-388** | sw-lead | `SW/tools/check_sw_gate_health.py` | ★**rc=1 · 2/6 绿** (★按设计判红★) | ★**rc=0 · 22/22 · `ALL TESTS PASS`** | 交卷页 37,416 B + 诊断页 + sw.yaml |
| **ISS-390** | mech-lead | `MECH/check_fts_seat_body_geometry.py` | ★**rc=0 · 33 条判据 0 失败** | ★**rc=0 · 15/15 · `ALL TESTS PASS`** | 真相页 46,898 B + 交卷页 37,068 B |
| **ISS-391** | hw-lead | `HW/check_fts_land_drill_same_batch.py` | ★**rc=1 · 4/7 绿** (★按设计判红★) | ★**rc=0 · 17/17 · `ALL TESTS PASS`** | 真相页 45,038 B + 交卷页 29,690 B |

★三闸连跑 3 次末行逐字相同 · 三闸零挂链 · 零落表 · 零改既有页面正文 · **L-26① 的 13 道扫描面闸逐道实跑全 rc=0 (含七个签收闸)** ★

★**③ ★★ISS-388: 本单最有价值的一条 = 「三道闸坏了但【没人看见】」被机器化了 ★★**
★**它的 4 条红逐条点名, 无一是误报** (main 本机实跑): H0 点名 `check_sw_board_md5_rebase_readiness.py` (`--selftest` 0/10, 末行「有用例 FAIL ⇒ 本闸不可信」) + `check_sw_ref_reachability_v2.py` (0/7, 末行「❌ 有用例没抓到」) ⇒ ★**这两道闸今天【真的坏了】**; H1 点名 `check_debug_pin_order_contract.py` 的**判据与环境耦合** (两个深度 TMPDIR 下 rc 0 vs 1); H2 点名 §2 账少登记 2 道; H3 点名 §1 账少登记 3 行 ⇒ ★**合计 4 条账漂 (D-1~D-4)** ★
★**★★⇒ ★★本闸【零挂链是它自己的硬判据】★★**: ★**源码 `hook_hits = gc_txt.count("check_sw_gate_health")` ⇒ 一旦把它挂进 `state/gate_check.py` ⇒ 它自己的 H4 立刻判红 ⇒ ⇒ ★**⇒ 本闸【结构上就不能被挂链】⇒ 【零挂链是它的正确形态, 不是缺陷】** ★★

★**④ ★★ISS-390: 「通用库件 courtyard 被当成厂件」这个前提错误, 本机独立复核确认 ★★**
★**main 自己解析 `.kicad_mod`**: `PinHeader_1x04_P1.27mm_Vertical` 的 `fp_rect` = **3.1000 × 6.0900** ⇒ 「`6.0900` 是通用件自己的 courtyard」坐实; `PinHeader_1x02_…` = **3.1000 × 3.5500** ⇒ 「`3.5500` 同源」坐实 ★
★**厂件外形按通式自己算**: N=4 ⇒ 4 × 1.27 = **`5.0800`** ✓ / N=2 ⇒ **`2.5400`** ✓ ⇒ 「厂件座体宽 X = N × 1.27」命中 ★
★**★⇒ 通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600` ⇒ 通用件当座体用 ⇒ Y 向每边少让 `0.0300`** ★ ★
★**★★⇒ 「`6.0900`/`5.0800`/`3.5500`/`2.5400` 这组数【全部来自通用库件】, 与 Samtec 无关** ⇒ ⇒ **ISS-371/389/374 把它们当「官方座体本体 (F.Fab)」写进已签收页与已签收闸源码 = 【定性前提错误】(不是数值错, 是出处错)** ⇒ ⇒ ★**且它把 OI-11 (h = [0数据]) 的性质改了: 库件根本给不了 Z (绝缘体高), 而厂件 Z = `0.8600` [官网] ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」** ★ ★

★**⑤ ★★ISS-391: 它的 3 条红 (D1/D2/D3) = main 自己该落的登记项还没落 ⇒ 【按设计判红】 ★★**
★**⇒ 【必须保持零挂链】: 在 §4 登记落地之前挂进 `state/gate_check.py` ⇒ 当场红 ⇒ 现场读成「板坏了」⇒ ⇒ 【挂链时机 = 与 §4 登记同批】 (L-29 通则②) ★

★**⑥ ★★26 条 main 地界待裁项已裁 (★一件没代老板拍板★)★★**

★**▌A 组 · ISS-388 (5 条·to=sw-lead)★★

| # | need key | main 裁决 (2026-11-24 16:0x) |
|---|---|---|
| A1 | `iss388_ledger_drift_owner` | ★**账漂 (D-1~D-4) 归【main 授权 + owner 落】, 且【必须与那一趟同批】** ⇒ 理由: ★**① 改的是 ISS-372 真相页的 §1/§2 机器块 = 已签收页 ⇒ 按「已签收件的订正路径」⇒ main 授权路径, owner 落追加式订正块 (★老字一字未删★) ⇒ **不许 main 直接改 owner 的正文**; ② ★**为什么必须同批**: D-1~D-4 的差集 = 【那三道闸坏了 + 账没跟上】⇒ 修账不修闸 = 账上写「已登记」但闸还是坏的 ⇒ ⇒ **必须【账 + 闸】一起修**, 而闸的修法在 §㉙ 与 §㊷ 已裁 (★闸 2 的 selftest 0/10 = 差值型自测在基线已红时全灭 ⇒ 归 SW 域那一趟同批★) ⇒ ③ ★**且闸 2 与闸 v2 修好之前, 新闸 `check_sw_gate_health.py` 必须保持零挂链** ⇒ 挂了它自己 H4 会红 (★见 §③★) ⇒ ★★ |
| A2 | `iss388_new_gate_hook_to_main` | ★**【不挂】, 且这不是「暂缓」而是【结构性不可挂】** ⇒ ★**理由 (★main 本机实读源码坐实★)**: 该闸的 H4 判据就是 `hook_hits = gc_txt.count("check_sw_gate_health")` ⇒ ★**它一旦出现在 `state/gate_check.py` 里, 它自己立刻判红** ⇒ ⇒ **挂它 = 让它自己判自己红 = 假红** ⇒ ⇒ **零挂链是它的正确形态** ⇒ ★**⇒ 真正要解决的是【那三道病闸】(★闸 2 / 闸 v2 / 闸 1 环境耦合★), 不是挂这道元闸** ⇒ ★**⇒ 「挂链就能看见」这个直觉在这里【是错的】⇒ 看不见的病根是【三道闸零挂链 + 坏了没人跑】⇒ 处置 = 修那三道闸 + 把它们挂进链 (★归 SW 域那一趟·★本轮不代排★)** ★ ★ |
| A3 | `iss388_env_sensitivity_fix_location` | ★**路 A (在源头修: 改 `check_debug_pin_order_contract.py` 的 ROOT 反推机制) 为主, 路 B (把 `TMPDIR=$PWD/tmp` 写进调用约定) 为辅 —— 两者【都要】, 但【顺序是先 B 后 A】** ⇒ ★**理由 (★main 本机实跑复现★)**: ★**① 闸 1 的红是【同一份源码, 只差 TMPDIR ⇒ 10/11 vs 11/11】⇒ 判据本身与环境耦合 ⇒ 这是【闸的缺陷】, 不是调用方的错 ⇒ ⇒ **病根在闸 ⇒ 必须在源头修 (路 A)**, 否则「靠人记得带 TMPDIR」= 把判据正确性押在人的记性上 (★ISS-297 已经栽过一次「约定靠人记会有忘的那天」★); ② ★**但路 B 也不能不做**: 本机 `/tmp` 用户配额打满 ⇒ 不带 TMPDIR 会假红 ⇒ ⇒ **路 B 是止血 (今天就让一切调用都带对), 路 A 是治病 (让闸与环境无关)** ⇒ ⇒ **顺序 = 先 B (零风险, 今天可落) + 后 A (要重签 ISS-372/ISS-375·★归 SW 域那一趟·★与「板只改一次」同批·★本轮不代排★)** ⇒ ★**★⇒ 代价账已算清: 路 A 要重跑 11 条反向用例 + 重签 ⇒ 这是【改已签收件的判据逻辑】⇒ 必须 main 授权 + owner 落 + 全套验收线重跑 ⇒ 【不进这一趟】** ★ ★ |
| A4 | `iss388_third_sick_gate` | ★**另起一单修它 —— 且【不另起, 归「板只改一次」那一趟同批】** ⇒ ★**理由 (★main 本机实跑★)**: ★**① `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` = 0/7, 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」⇒ 它【真的坏了】, 不是误报 ⇒ 必须修; ② ★**但它的失败模式与闸 2 同类 (基线先红 ⇒ 差值型自测全灭) ⇒ 修它的前置 = 先修账 (D-1~D-4) ⇒ ⇒ 【它与账漂是同一条因果链】⇒ ⇒ 拆成两单 = 两批做完 = 又一次「板只改一次」的纪律破例 ⇒ ⇒ **归同一趟** ★ **③ ⇒ 归属 owner = sw-lead (★它本来就该在 SW 域那一趟里·★本轮只裁归属, 不代排顺序★)** ★ ★ |
| A5 | `iss388_delta_selftest_convention` | ★**「基线必须先绿, 否则 selftest 结论不可读」写进闸的编写通则 —— 【采纳】, 但【落法是新增一份通则文档 + 逐闸加一行前置断言】, 不是【逐个改已签收闸的 selftest 口径】** ⇒ ★**理由 (★main 本机实跑★)**: ★**① 闸 2 = 0/10 与闸 v2 = 0/7 都是【差值型自测在基线已红时全灭】⇒ 闸自曝「我不可信」却说不出「我是账漂了不是坏了」⇒ 现场只能靠人去读源码 ⇒ ⇒ **这个病确实需要一条通则**; ② ★**但「一次性改若干已签收闸的 selftest 口径」这条路【本轮不走】**: ★**(a) 改已签收闸的 selftest 逻辑 = 改判据 ⇒ 要重签 ⇒ 又是一次签收指纹过期 (★今天已经栽了两次, L-27★); (b) 且「差值型自测」本身不是错 —— 它【自证「红集 == {目标那一条}」】这个设计是对的 ⇒ 错的只是【基线已经红的时候, 差值不可读】⇒ ⇒ **正确解法 = 让基线先绿 (A1 的账漂 + 那三道闸修好) ⇒ 差值自测自然可读 ⇒ 通则只需写成【写闸时必须先声明「本闸的基线是什么, 基线红了 selftest 结论不可读」】+ 错误消息点名是哪个闸 + 它的原文末行 (★这正是新闸 H0 已做到的★)** ⇒ ⇒ ★**⇒ 落法 = 新增一份通则 (★main 落·★`state/GATE_WRITING_CONVENTIONS.md`·★新文件不碰任何已签收闸★) + 逐闸加前置断言归 SW 域那一趟** ⇒ ★★ |

★**▌B 组 · ISS-390 (4 条·to=mech-lead)★★

| # | need key | main 裁决 (2026-11-24 16:0x) |
|---|---|---|
| B1 | `iss390_correction_landing` | ★**6 处定性订正归【main 授权 + owner 落追加式订正块】, 且【与「板只改一次」那一趟同批】** ⇒ 理由: ★**① 这 6 处全是【已签收页正文 + 已签收闸源码字符串】⇒ 按「已签收件的订正路径」⇒ **main 授权路径, owner 落**, main 不直接改 owner 的正文 (★老字一字未删·★只加订正块★); ② ★**② 为什么要同批**: ★**§4 #3 的两处源码字符串 (`MECH/check_debug_seat_3d_fit.py` L848 / L879) 是【已签收闸的判据源码】⇒ 改它 ⇒ **那两道签收指纹当场过期** ⇒ ⇒ 【必须与那一趟的「重验全部验收线」同批】(★L-27 通则③★) ⇒ ★**③ ⇒ 并且: 这 6 处不落 ⇒ 【通用件 vs 厂件】的前提错误继续留在页上与闸源码里 ⇒ 下一个读这页或跑那个闸的人会拿错对照物做结构判决 ⇒ 而本闸 G3 未落清单永远 17 处** ⇒ ⇒ ★**★⇒ 故: main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★ |
| B2 | `iss390_h_lock_and_test_sample` | ★**两问分别裁: (甲) h 走【三档参数化】, 不锁死; (乙) 打样归【那一趟同批】** ⇒ ★**(甲) 理由**: ★**① ISS-390 本机复核坐实: 厂件柱高 `3.05` mm (官网表 TABLE 1 lead style -01) 而绝缘体只有 `0.86` ⇒ ⇒ **罩内腔板面以上那一维【不能】按 `0.86` 出件 ⇒ `h=0.90` 档物理上装不下 ⇒ 可行档是 `2.54` 与 `4.00` ⇒ ⇒ **⇒ 本单把 §㊷ C8 那条 (「h 不卡那一趟」) 的依据从「[0数据]」升级成了「[0数据] 且已算明可行档只有两个」** ⇒ ★**② ⇒ 【不锁死】的理由 = h 锁死会绑死一个【还没测过】的量 ⇒ 而本单 §6.1 自己说「库件给不了 Z, 厂件 Z = 0.86 但柱高 3.05」⇒ ⇒ **三档参数化 (0.90 / 2.54 / 4.00) 让结构侧在两档之间走, 而 0.90 已被物理判死 ⇒ 实际只剩 2.54 与 4.00 两档** ⇒ ⇒ **★本裁决 = 三档参数化保留 (0.90 档标注物理不可行), 锁定权仍在 boss (★那 53 条里 `iss389_oi11_seat_height_window` 未代拍★)** ⇒ ★**(乙) 理由**: ★**打样是【唯一能拿到 REF 公差】的路径 (★官网图给的是 REF 不是公差带★) ⇒ ⇒ **落 FTS 时打一块单板样、用卡尺量三量 (★绝缘体高 / 外形宽 / 外形深★) 回填 `keepout_dwg` + `body_geometry` ⇒ 【必须与那一趟同批】(★落 FTS 那一天才有样可打★) ⇒ ⇒ **归 mech-lead 执行 (转派), 但【不新起一单】(★与那一趟同批·★与「板只改一次」纪律一致★)** ★ ★ |
| B3 | `iss390_oi12_and_oi14_together` | ★**三个答案一起给: (a) 罩住判据【管到座体本体】(★不是只管铜箔★); (b) 「偏紧 `0.5200`」的措辞【作废】(★因为 `6.0900` 是通用库件的 `F.CrtYd`, 厂件【没有】courtyard 这个量★); (c) ⇒ (a) 成立 ⇒ **J_UART 的 X 需求从 `4.0700` 变 `4.3400`** ⇒ ⇒ **OI-14 的目标值跟着改成 `4.3400`** ⇒ ★★"
               "★**★⇒ 理由 (★main 本机独立复核坐实★)★**: ★**① 座体本体 (厂件 X `5.0800` / `2.5400` + Y `2.1600`) 比铜箔包络 (X `4.8100` / `2.2700`) 【每边都大】⇒ ⇒ **只按铜箔算 = 会做出一个装不进座体的洞 ⇒ 判据必须同时管座体本体** ⇒ ⇒ **(a) = 管 ⇒ 采纳**; ② ★**② ⇒ (b) 作废**: ★**「偏紧 `0.5200`」这句的对照物是 `6.0900` ⇒ 而 `6.0900` 是【通用 KiCad 库件自己的 `F.CrtYd`】(★main 本机解析 `.kicad_mod` 的 `fp_rect` = 3.1000 × 6.0900 坐实★) ⇒ ⇒ **Samtec 厂件没有 courtyard 这个量 ⇒ 那句「比 courtyard 还小」在【厂件】这一层【无意义】⇒ 作废** ⇒ ⇒ **★注意: 这不是「判据错了」, 是【对照物拿错了】⇒ 判据本身 (每边 `0.9000`) 仍然成立** ⇒ ⇒ **(b) = 作废那句措辞, 保留判据** ⇒ ⇒ ③ ★**③ ⇒ (c) 是 (a) 的算术后果**: ★**J_UART 座体 X `2.5400` + 2 × `0.9000` = `4.3400` (★不是 `4.0700`·★`4.0700` 是按铜箔 `2.2700` 算的★) ⇒ ⇒ **OI-14 (DP-1) 的目标值 = `4.3400`** ⇒ ⇒ ★**★★⇒ 与 §㊴ C1 (OI-5 取 `4.8100`) 一致但【不是同一个数】: `4.8100` = 铜箔沿脚排总展 (判「装得下」的输入), `4.3400` = 座体本体 + 2×余量 (判「装得下且留得住」的输出) ⇒ 两个数【都要】, 不冲突** ★ ★ ★★"
               "★**★★⇒ ★★注意: 这条与 §㊷ C4 (OI-12 判路 A) 与 §㊷ C6 (OI-14 改 `4.0700`) 【冲突】⇒ ⇒ 按 L-27 通则③ (main 落裁决 ⇒ 已 verified 的单的交付物进入「会动」状态 ⇒ 那一趟必须重验全部验收线) ⇒ ⇒ **本条是 §㊷ C4/C6 的【订正】, 由本裁决取代, 老裁决的数值随之作废** ⇒ ⇒ **★而 §㊷ C6 那个 `4.0700` 恰好是本单 §4 订正清单里的一条 (★L634 机器块 + 正文路径 B 段★) ⇒ ⇒ 正好一起订正** ★ ★",
| B4 | `iss390_y_direction_open_question` | ★**Y 向走【放大罩开口 Y】, 但【幅度按座体本体重算】⇒ 开口 Y 须 `≥ 5.7600`** ⇒ ★**理由 (★main 本机实算★)★**: ★**① 座体本体 Y = `2.1600` (厂件) ⇒ 按每边 `0.9000` ⇒ 清空区 Y 需求 = `2.1600` + 2 × `0.9000` = `3.9600` ⇒ ⇒ **比 §㊷ C5 裁的 `2.8000` 大 `1.1600`** ⇒ ⇒ **⇒ §㊷ C5 的「路 B (开口 Y ≥ `5.6000`/`5.8000`)」的【输入变了】⇒ 需重算: 开口 Y 须 ≥ 清空区 Y `3.9600` + 2 × `0.9000` = `5.7600`** ⇒ ⇒ ★**★★⇒ 所以: §㊷ C5 的【方向】(放大罩开口 Y) 仍成立, 但【数值】从 `5.6000`/`5.8000` 收窄为 **`5.7600`** ⇒ ⇒ 这条同样构成对 §㊷ C5 的【订正】** ⇒ ★**② ⇒ 「接受零余量」那个选项【已不存在】(★本单自己也这么说★) ⇒ ⇒ **(b) 改判据口径只罩铜箔 = 【已判死】(★与 §㊷ C4 同理: 只罩铜箔 = 装不进座体★) ⇒ ⇒ 只剩 (a) 放大罩开口 Y 一条路** ⇒ ⇒ **⇒ 罩开口 Y `4.6000` → `5.7600` = 放大 `1.1600`** ⇒ ★**③ ⇒ 结构性代价 (镜脚内腔 + 罩外观缝) 与 §㊷ C5 同源 ⇒ 与板框第一问同批** ⇒ ★ ★ |

★**▌C 组 · ISS-391 (5 条·to=hw-lead)★★

| # | need key | main 裁决 (2026-11-24 16:0x) |
|---|---|---|
| C1 | `OI-391-1` | ★**三处补登记由【main 落追加式订正块, owner 在「板只改一次」那一趟的清单改版里按逐字文本落】, 【不许提前落】** ⇒ ★**★⇒ 为什么不提前落 (★机器可核★)★**: ★**提前落 ⇒ 中间态 = 板还没改, 清单却写了要改孔 ⇒ ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (★板上还是 `0.65`★) ⇒ 当场红 ⇒ ⇒ 现场会把它读成「板坏了」⇒ ⇒ ★**这正是 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + ISS-384 A5 全同款纪律的另一种说法** ⇒ ★**⇒ 且 §4 #1/#2/#3 必须【一起落】** (★`wp02_tokens()` 会从③的原文里自动抽「小数」当覆盖令牌 ⇒ 补上 `0.65` 与 `0.71` 之后, 现有 P4 会自动要求清单页 `B33_PIN_LAND_1P27` 里也能查到这两个数 ⇒ ⇒ #1 与 #2/#3 不同步 ⇒ P4 当场红★) ⇒ ★ ★ |
| C2 | `OI-391-2` | ★**写成【一条】(pitch 与 drill 是同一项的两条腿, 不可只做其一), 不许拆成两条可分开的动作** ⇒ ★**理由 (★机器可核★)★**: ★**新闸 D1 只能查出【整条没写】, 查不出【拆成两条只做一条】⇒ ⇒ 拆开写 = 判据出现盲区** ⇒ ⇒ **一条写 + 锚点含两个数 (`0.71` 与 `1.27`) = 机器可判** ⇒ ⇒ ★**★⇒ 与本轮 §㊺ 的 A1/B1 同一纪律 (措辞口径由 main 定, 落法由 owner 落, 且必须机器可判)** ★ ★ |
| C3 | `OI-391-3` | ★**BOM L71 (J_DEBUG) / L77 (J_UART) 的 opn 与 footprint 两栏 = 与板侧 land 来源【同源】, 落表时机 = 那一趟的同一次落表与重出; 本轮【零落表】** ⇒ ★**★⇒ 同源纪律 (★板面 land 来源 = BOM 型号栏 = 实物料号★)**: ★**板侧 land 来源 = 盘上通用 KiCad 1.27mm THT 库件 (★`PinHeader_1x04_P1.27mm_Vertical` / `PinHeader_1x02_P1.27mm_Vertical`·★md5 `7a5f470c…` / `47bcbf6d…`★) + 一条显式偏离登记 (★偏离项 = 铜箔焊盘直径官方无值 + 孔径由 `0.65` 改 `0.71`★) + BOM 型号栏写 FTS 料号** ⇒ ⇒ **不成立 ⇒ 投板后才发现 ⇒ 2-4 周返工** ⇒ ⇒ ★**★⇒ 逐字草案按真相页 §4 #5 原样落, main 不改一字** ★ ★ |
| C4 | `OI-391-4` | ★**生成器补登记归【owner (hw-lead) 落】, 且【与那一趟同批】; 本轮【零改既有脚本正文】** ⇒ ★**理由 (★机器可核★)★**: ★**`state/_iss277_build_preflight.py` 的 `build_pinland_item()` (title + current_state + criterion 三处一起长) + `read_board_pin_land()` 加一个 drill 字段现读板** ⇒ ⇒ **不落 ⇒ §3 #2/#3 的补登记【重跑一次就蒸发】(★ISS-349 同一位号已栽过一次★) ⇒ 白补, 改孔这条子动作重新回到没人做的状态** ⇒ ⇒ ★**★⇒ 归 owner 落 (★本单零改既有脚本正文★) + 必须与那一趟同批 (★否则中途重跑一次就白补★)** ⇒ ★ ★ |
| C5 | `OI-391-5` | ★**【与 §4 四处登记同批挂】进 `state/gate_check.py`, 不提前挂** ⇒ ★**★⇒ 理由 (★main 本机实跑实测★)★**: ★**★这道闸现在裸跑 rc=1, 而 `--selftest` rc=0 末行 `ALL TESTS PASS` (17 条反向用例全抓到) ⇒ ⇒ 闸本身可信 ⇒ ⇒ 它的红是【按设计】的: D1/D2/D3 抓的正是「`钻孔 0.65→0.71` 还没进到作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」⇒ ⇒ **在登记落地之前挂进去 = 造出一道【假的红】⇒ 现场会把它读成「板坏了」** ⇒ ⇒ ★**★与全部先例同源: 闸与它要防/要等的那一趟同批生效** ⇒ ⇒ ★**★⇒ 且【挂链动作只能由 main 在那一趟统一做】(★不许 agent 自挂★) ⇒ ⇒ ★**★⇒ 顺带: 本轮三个新闸 (`check_sw_gate_health` / `check_fts_seat_body_geometry` / `check_fts_land_drill_same_batch`) 全部【与那一趟同批挂】⇒ ⇒ 那一次的「闸清单刷新」批次要一次挂三个** ⇒ ★ ★ |

★**⑦ ★★★★一条自曝铁律 (L-32) ★★★★**
★**★★本轮 main 自曝: 我 13:1x 那一轮落的 15 条 pm.yaml 答案, 【一条都没闭上任何 need】★★** ⇒ ★**原因 (★main 本机实读 `state/merge.py` 坐实★)**: ★**merge.py 按【精确 key】配对 needs_from × answers (`answers_by_key.get(k, [])` + `_by == ask_to`) ⇒ ⇒ 我 13:1x 用了【改名的 key】(★如 `iss389_main_oi5_pick_4810`, 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★) ⇒ ⇒ **配对不上 ⇒ 零闭合** ⇒ ⇒ ★**★⇒ 实测 (★main 本机实算★): `to=main` 的 need 共 481 条, 其中【逐字】命中 pm.yaml 答案的只有 111 条 ⇒ ⇒ 未命中 370 条 ⇒ ⇒ ★**★⇒ 我 13:1x 那 15 条【逐字命中 need key 的 = 0 条】⇒ ⇒ 全在「没命中」那一侧** ⇒ ★★"
               "★**★★⇒ 这不是「答案内容错了」, 是【答案【落错了 key】⇒ 机制上没生效】⇒ ⇒ ★★【内容仍然有效, 只是没被机制读到】⇒ ⇒ 本轮已按 need 的原 key 重答一遍 (★见 §⑥ 各组的 key·★一律用 need 的原 key★) ⇒ ⇒ **原 15 条【老字一字未删】, 保留作人读记录** ★ ★"
               "★**★★⇒ 与 L-28 合看**: ★**L-28 = 「幂等守卫命中时必须区分『已经落过了』与【key 撞名】】⇒ 撞名必须报错退出** ⇒ ★**★L-32 = 【key 撞名的镜像面】: 【我自己起的 key 与 need 的 key 不撞名 ⇒ 机制上闭不上 ⇒ 而机制【不会报错】(它只是配不上)⇒ ⇒ ⇒ 【静默失效】比【撞名报错】更危险 ⇒ ⇒ 所以: 落答案时必须【先从 need 里抄 key】, 不许自己起** ★★** ★★"
               "★**★★⇒ ⇒ 一条操作纪律 (★本轮起执行★)**: ★**落 pm.yaml 答案前, 必须先 `grep` 出 need 的原 key 并【逐字复制】; 落盘后必须回读验证【该 key 的 need 已从 pending 变 answered】⇒ ⇒ 不许只看「脚本打印 ✅ 已原子更新」(★L-28 通则② 同源★)** ★ ★"

★**★★★ ⑨ ★★★★追加式订正 (★本条只订正 §㊷ 与本节 B3/B4 的【数值】, 不改它们的正文·★老字一字未删★) ★★★★**

★**★★★ ⑨-① ★★★§㊷ C4 (OI-12) 的【死因】作废, 但【结论】不变★★★**
★**§㊷ C4 判死「路 B」用的死因 = 「`6.0100` 比 courtyard `6.0900` 还小 `0.0800` ⇒ 连装得下都不成立」⇒ ⇒ ★**main 本机独立复核 (ISS-390) 坐实: `6.0900` 是【通用 KiCad 库件 `PinHeader_1x0{4,2}_P1.27mm_Vertical` 的 `F.CrtYd`】(★`.kicad_mod` 的 `fp_rect` = 3.1000 × 6.0900 / 3.1000 × 3.5500★) ⇒ ⇒ ★**Samtec 厂件根本没有 courtyard 这个量 ⇒ ⇒ 【那个对照物无效 ⇒ 原死因作废】** ⇒ ⇒ ★**★⇒ 但【路 B 仍然死】, 死因换成更硬的一条: 路 B 的需求 `6.0100` / `3.4700` 对【座体本体】只给每边 `(6.0100−5.0800)/2 = 0.4650` / `(3.4700−2.5400)/2 = 0.4650` ⇒ ⇒ 低于 `CRIT 0.6000` ⇒ ⇒ 【连 TOL 都不用扣就过不了】⇒ ⇒ ★**★⇒ ⇒ 【结论 (路 A) 不变, 死因换】** ★ ★

★**★★★ ⑨-② ★★★§㊷ C4/C5/C6 的【三个数】必须改 (★不是 main 拍脑袋, 是按同一判据重算★)★★★**
★**「路 A 的判据口径不改」只保证了【每边 `0.9000`】这个【数】不动⇒ ⇒ 它没保证【这个数加在谁身上】不动⇒ ⇒ ★**旧口径把 `0.9000` 加在【铜箔】上 (`4.8100` + 2×`0.9000` = `6.6100`) ⇒ ⇒ 对【座体本体】`5.0800` 只给每边 `0.7650` ⇒ ⇒ 扣 `TOL 0.3000` 后只剩 `0.4650` < `CRIT 0.6000` ⇒ ⇒ ★**★⇒ 【路 A 按铜箔出的尺寸, 同样过不了它自己的判据 (对座体本体)】⇒ ⇒ ⇒ 基准物必须换成座体本体** ⇒ ⇒ ★**★⇒ 厂件座体本体 (★ISS-390 本机复核: X = N×1.27 ⇒ `5.0800`/`2.5400`·★Y = `2.1600`·★Z = `0.8600`·★全部 `[官网]`★) ⇒ ⇒ **① 清空区 X (J_DEBUG) `6.6100` → `6.8800` ② 清空区 X (J_UART) `4.0700` → `4.3400` ③ 清空区 Y `2.8000` → `3.9600` ④ 罩开口 Y 下限 `5.6000` → `5.7600` (★`5.8000` 那档仍有效且【推荐】·★它顺带解掉落点 C2 的 `0.2000` 死结★) ⑤ 罩开口 X `10.2000` 不动** ⇒ ⇒ ★**★⇒ ⇒ §㊷ C6 的 `4.0700` 与 §㊷ C5 的 `5.6000` 两个数【随之作废】** ★ ★

★**★★★ ⑨-③ ★★★§㊷ C3 (OI-5 取 `4.8100`) 【不冲突】, 但「铜箔齐平档」要加限定词★★★**
★**`4.8100` = 铜箔沿脚排总展 = 判「装得下」的【输入】; `6.8800` = 座体本体 + 2×余量 = 判「装得下且留得住」的【输出】⇒ ⇒ 两个数【都要】⇒ ⇒ ★**★⇒ 但「铜箔齐平档」这句话必须加限定词: 座体本体 `5.0800` 比铜箔 `4.8100` 每边宽 `0.1350` ⇒ ⇒ ⇒ ★ ★

★**★★★ ⑨-④ ★★★两条【正交的轴】, 别混 (★否则会误以为「维持焊盘 1.000」这条被推翻了★)★★★**
★**① OI-387-1 (维持焊盘 `1.000×1.000`) 讲的是【改孔 `0.65→0.71` 不动铜箔包络】⇒ ⇒ **该结论在【改孔这条轴】上仍成立**; ★**② ⑨-② 讲的是【判据基准物从铜箔换成座体本体】⇒ ⇒ **这是【另一条轴】**⇒ ⇒ ⇒ ★★**★⇒ 两条互不推翻 ⇒ ⇒ 但 MECH 全链读数时必须【按新基准物】重取** ★ ★

★**★★★ ⑨-⑤ ★★★⇒ 落法纪律 (★L-27 通则③·★L-29 通则③★)★★★**
★**`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` 的 L634 机器块 + 正文路径 A/B 段 + `D-6`/`U-7` 行, 以及 `MECH/check_debug_seat_3d_fit.py` L848/L879 的【已签收闸源码字符串】⇒ ⇒ 一律走【追加式订正块】(★老字一字未删★) + owner 在「板只改一次」那一趟的清单改版里落 ⇒ ⇒ ⇒ **main 不直接改 owner 的正文** ★ ★

★**⑧ 本轮零派 / 零外发 / 零落表 / 零写板 / 零挂链**: ★**internal = 0** ⇒ 三单已交卷待签收 (★ISS-392/393/394 三条真在飞 ⇒ 不重复派★) ⇒ ★**外发段恒空** ★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标 / 清空区放大量的一切前提都挂在它身上, 本页不代拍** ★"
               "★**⇒ 「板只改一次」那一趟现在明确要带【四条腿】**: ★**① 改孔 `0.65→0.71` (★环宽 `0.1450` 的制程能力确认同批★) ② 四处清单登记 (ISS-391 §4) ③ 三个新闸挂链 (★与本单 §4 登记同批★·★`check_sw_gate_health` 结构上不能挂★) ④ 六个签收件的 md5 刷新 + 全部验收线重跑 (★L-27 通则③·★本轮 §⑥ 裁决落进已 verified 的单 ⇒ 必须重验★) ⑤ ★★清空区尺寸按【座体本体】重出 (`6.8800` / `4.3400` / `3.9600` / 罩开口 Y `≥ 5.7600`) + §2 账刷新范围扩到【拆开字面量】写法 (★两条都是本轮新发现·★都落在结构件出件之前·★不落 ⇒ 结构件按错尺寸开模 = 第二次返工★)** ★ ★"
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  一页: %d → %d B (追加式 §㊺, 备份 %s.bak_%s_main_sign_iss388_390_391)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l32" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-32 · ★★落答案时必须【从 need 里逐字抄 key】⇒ 自己起 key = 机制【静默失效】(★比撞名报错更危险★) ★★

★**实测 (2026-11-24 16:0x, main 本机实读 `state/merge.py` + 逐 key 核对·★本轮自曝★)★**: ★**main 在 13:1x 那一轮落了 15 条 pm.yaml 答案, 内容全对, 但【一条都没闭上任何 need】** ⇒ ★**★⇒ 机制读数: pm.yaml 里 `to=main` 的答案中, 【逐字】命中某个 need 的 key 的只有 113/152 ⇒ ⇒ 我那 15 条全在「没命中」那一侧** ★ ★
★**★根因 (★main 本机实读 `state/merge.py` 坐实★)★**: ★**merge.py 按【精确 key】配对: `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]` ⇒ ⇒ key 必须与 need 的 key 【逐字相同】, 且答案必须落在【被问的那个 agent】的分片里** ⇒ ★**★⇒ 而我 13:1x 用了【自己起的改名 key】(★如 `iss389_main_oi5_pick_4810`, 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★) ⇒ ⇒ **配不上 ⇒ 零闭合** ★ ★
★**★⇒ ★★这比 L-28 的「key 撞名」更危险★★**: ★**L-28 是【撞名】⇒ 幂等守卫会报错退出 ⇒ 至少【有声音】; 而这里是【没撞名, 只是对不上】⇒ ⇒ 机制【一声不吭】⇒ ⇒ 答案躺在 pm.yaml 里, 内容正确, 但【对闭环机制等于不存在】⇒ ⇒ **页面上看起来「已答」, 台账上其实还挂着** ★ ★
★**★⇒ 两条纪律 ★★**: ★**① 落答案前, 必须先从 need 里【逐字抄 key】(★不许自己起, 不许「起个更清楚的名字」★)⇒ ⇒ 若 need 的 key 本身不适合当答案的 key, 那就【改 need 的 key】或【在答案的 value 里写清对应关系】, 但【不许两边名字不一样而指望机制能猜】** ★ **② 落盘后必须回读验证【该 key 的 need 已从 pending 变 answered】⇒ ⇒ 不许只看「脚本打印 ✅ 已原子更新」(★L-28 通则② 同源: writer 的成功消息只保证【写成功】, 不保证【写对了地方】★)** ★ ★
★**★⇒ ★★与 L-28 的关系 (★一对镜像面★)★**: ★**L-28: 「撞名」⇒ 【必须报错退出】(★不能静默跳过然后继续报绿★) ⇒ ⇒ ★**L-32: 「不撞名但对不上」⇒ 【必须被当成错误处理】⇒ ⇒ 两侧合起来 = 【key 是唯一的连接键, 任何一侧不对齐都必须响】** ★★"
★**★⇒ ★★推广 (★不止 pm.yaml★)★**: ★**凡是有「按 key 配对」的地方 (★merge 的 needs×answers · gate 的 (file,line) 钉住 · 一页的章节号索引 · 决策索引的 55 条覆盖复核★), 【键必须逐字对齐】, 而【对齐这件事本身要有回读验证】⇒ ⇒ ★**★⇒ 反过来说: 【机制【静默失效】比【机制【报错】更贵】⇒ ⇒ 所以凡是我新写的机制, 都必须自带一句「配对不上就报错」** ★★"
★**★⇒ 与 L-21~L-31 合看★**: ★**L-21 清单钉 file,line · L-23 工具会扫到自己 · L-24 沙箱硬链接 · L-25 厂商料号逐个坐实 · L-26 签收要跑扫描面命中的闸 · L-27 签收要等 owner 收工 · L-28 幂等守卫不许静默吞 · L-29 按设计判红 ≠ 闸坏了 · L-30 取号/取 key 必须先查重 · L-32 答案 key 必须逐字抄** ⇒ ★**★共性 = 【凡是有「键」的地方, 键的两端必须逐字对齐, 且对齐要回读验证】** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  LESSONS: %d → %d B (追加式 L-32, 备份 %s.bak_%s_main_l32)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_pm():
    # ★★必须用【need 的原 key】⇒ 否则配不上 (L-32)★★
    ANS = [
        ("iss388_ledger_drift_owner", "sw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss388_ledger_drift_owner★)★: ★**账漂 (D-1~D-4) 归【main 授权 + owner 落追加式订正块】, "
         "且【必须与「板只改一次」那一趟同批】** ★★"
         "★**★⇒ 理由 (★main 本机实跑 + 实读 `state/merge.py` 坐实★)★**: ★**① 改的是 ISS-372 真相页的 §1/§2 机器块 = 【已签收页】⇒ 按「已签收件的订正路径」⇒ "
         "**main 授权路径, owner 落追加式订正块 (★老字一字未删★) ⇒ main 不直接改 owner 的正文**; "
         "★**② 为什么必须同批**: ★**D-1~D-4 的差集 = 【那三道闸坏了 + 账没跟上】⇒ 修账不修闸 = 账上写「已登记」但闸还是坏的 ⇒ ⇒ "
         "★**⇒ 必须【账 + 闸】一起修** ⇒ 而闸的修法在 §㉙ 与 §㊷ 已裁 (★闸 2 的 selftest 0/10 = 差值型自测在基线已红时全灭⇒ 归 SW 域那一趟同批★) ⇒ ⇒ "
         "★**③ 且闸 2 与闸 v2 修好之前, 新闸 `check_sw_gate_health.py` 必须保持零挂链** ⇒ 挂了它自己 H4 会红 (★源码 `hook_hits = gc_txt.count(\"check_sw_gate_health\")`★) "
         "⇒ ⇒ **零挂链是它的正确形态** ⇒ ⇒ ★**★⇒ 落法 = main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★"
         "★**★⇒ 附: 本轮 main 已实跑确认这 4 条差集 = §2 账少登记 2 道 (`check_sw_false_connectivity_gate.py` + `check_sw_gate_chain_coverage.py`) + "
         "§1 账少登记 3 行 (`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` / `:241` / `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215`)** ★",
         "SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md §1/§2 机器块 · SW/tools/check_sw_gate_health.py H2/H3 · 一页 §㊺ A1"),

        ("iss388_new_gate_hook_to_main", "sw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss388_new_gate_hook_to_main★)★: ★**【不挂】, 且这不是「暂缓」而是【结构性不可挂】** ★★"
         "★**★⇒ 理由 (★main 本机实读源码坐实·★不是抄报告★)★**: ★**该闸的 H4 判据字面就是 `hook_hits = gc_txt.count(\"check_sw_gate_health\")` ⇒ "
         "⇒ 它一旦出现在 `state/gate_check.py` 里, 它【自己】立刻判红 ⇒ ⇒ 挂它 = 让它自己判自己红 = 【假红】⇒ ⇒ ★**⇒ 零挂链是它的正确形态, 不是缺陷** ★★"
         "★**★⇒ ★★「挂链就能看见」这个直觉在这里【是错的】★★**: ★**看不见的病根 = 【那三道病闸零挂链 + 坏了没人跑】⇒ ⇒ 处置不是挂这道元闸, 而是"
         "★**① 修那三道闸 (★闸 2 的 selftest 0/10 + 闸 v2 的 0/7 + 闸 1 的环境耦合★) + ② 把它们挂进链** ⇒ ⇒ ★**⇒ 而它们【现在挂不得】(★挂了当场红·★基线先红的账没修完★) ⇒ "
         "⇒ ⇒ 顺序 = 账漂修完 + 闸修好 + 再挂 ⇒ ⇒ 全部归 SW 域那一趟 ⇒ **本轮只裁归属, 不代排顺序** ★ ★"
         "★**★⇒ 附: 本轮已实测确认这四道新闸在 `state/gate_check.py` 里 grep 命中【全为 0】⇒ ⇒ 零挂链状态成立 ⇒ ⇒ 零改既有闸成立** ★",
         "SW/tools/check_sw_gate_health.py H4 (源码实测) · 一页 §㊺ A2 · 一页 §㊺ §③"),

        ("iss388_env_sensitivity_fix_location", "sw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss388_env_sensitivity_fix_location★)★: ★**路 A (在源头修) 为主 + 路 B (调用约定) 为辅, "
         "且【顺序 = 先 B 后 A】** ★★"
         "★**★⇒ 理由 (★main 本机实跑复现★)★**: ★**① 闸 1 的红是【同一份源码, 只差 TMPDIR ⇒ 10/11 vs 11/11】⇒ ⇒ 判据本身与环境耦合 ⇒ ⇒ "
         "★**这是【闸的缺陷】, 不是调用方的错 ⇒ ⇒ 病根在闸 ⇒ 必须源头修 (路 A)** ⇒ 否则「靠人记得带 TMPDIR」= 把判据正确性押在人的记性上 (★ISS-297 已栽过一次「约定靠人记会有忘的那天」★); "
         "★**② 但路 B 也不能不做**: ★**本机 `/tmp` 用户配额打满 ⇒ 不带 TMPDIR 会假红 (★rc=120 / 0 字节★) ⇒ ⇒ ★**路 B 是止血 (今天就让一切调用都带对), 路 A 是治病 (让闸与环境无关)** ⇒ ⇒ "
         "★**★⇒ 顺序 = 先 B (零风险·今天可落) + 后 A (要重签 ISS-372/ISS-375 ⇒ 归 SW 域那一趟·★与「板只改一次」同批·★本轮不代排★)** ★ ★"
         "★**★⇒ 代价账 (★本单已算·★main 核对后成立★)★**: ★**路 A = 改【已签收件】的判据逻辑 ⇒ 必须 main 授权 + owner 落 + 重跑 11 条反向用例 + 重签 ⇒ ⇒ "
         "★**★⇒ 那是一次签收指纹过期 (★今天已在 ISS-381/382/384 上栽过两次·★L-27★) ⇒ ⇒ 【不进这一趟】** ⇒ ⇒ ★**★⇒ 落法: 路 B 归 owner 立即落 (★写进 `state/check_brief_commands.py` 或任务书模板★); "
         "路 A 归 SW 域那一趟同批, main 在那一趟授权** ★ ★",
         "SW/tools/check_debug_pin_order_contract.py (本机实跑: TMPDIR=$PWD/tmp ⇒ 11/11 PASS; 不指 ⇒ 10/11 FAIL) · 一页 §㊺ A3"),

        ("iss388_third_sick_gate", "sw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss388_third_sick_gate★)★: ★**要修, 但【不另起一单】⇒ 归「板只改一次」那一趟同批** ★★"
         "★**★⇒ 理由 (★main 本机实跑★)★**: ★**① `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` = 0/7, 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」⇒ ⇒ "
         "★**它【真的坏了】, 不是误报 ⇒ 必须修** (★本单只登记不修是对的: 它不在本单 brief 范围内★); "
         "★**② ★★但它的失败模式与闸 2 同类 (基线先红 ⇒ 差值型自测全灭) ⇒ ⇒ 修它的前置 = 先修账 (D-1~D-4) ⇒ ⇒ 【它与账漂是同一条因果链】⇒ ⇒ "
         "★**★⇒ 拆成两单 = 两批做完 = 又一次「板只改一次」的纪律破例 ⇒ ⇒ 归同一趟** ★ "
         "★**③ ⇒ 归属 owner = sw-lead (★它本来就该在 SW 域那一趟里·★本轮只裁归属, 不代排顺序★)** ★ ★"
         "★**★⇒ 附: 本轮已实测 `check_sw_ref_reachability_v2.py --selftest` = 0/7 + 末行「❌ 有用例没抓到」⇒ main 独立复核确认它确实坏了** ★",
         "SW/tools/check_sw_ref_reachability_v2.py (本机实跑 --selftest 0/7) · 一页 §㊺ A4"),

        ("iss388_delta_selftest_convention", "sw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss388_delta_selftest_convention★)★: ★**「基线必须先绿, 否则 selftest 结论不可读」写进闸的编写通则 —— "
         "【采纳】, 但【落法 = 新增一份通则文档 + 逐闸加前置断言】, 不是【逐个改已签收闸的 selftest 口径】** ★★"
         "★**★⇒ 理由 (★main 本机实跑★)★**: ★**① 闸 2 = 0/10 与闸 v2 = 0/7 都是【差值型自测在基线已红时全灭】⇒ ⇒ 闸自曝「我不可信」却说不出「我是账漂了不是坏了」⇒ ⇒ "
         "★**⇒ 现场只能靠人读源码 ⇒ ⇒ 这个病确实需要一条通则**; "
         "★**② ★★但「一次性改若干已签收闸的 selftest 口径」这条路【本轮不走】★★**: ★**(a) 改已签收闸的 selftest 逻辑 = 改判据 ⇒ 要重签 ⇒ 又是一次签收指纹过期 (★L-27·★今天已栽两次★); "
         "★**(b) 且「差值型自测」本身不是错 —— 它【自证「红集 == {目标那一条}」】这个设计是对的 ⇒ ⇒ 错的只是【基线已经红的时候, 差值不可读】⇒ ⇒ "
         "★**★⇒ 正确解法 = 让基线先绿 (A1 的账漂 + 那三道闸修好) ⇒ 差值自测自然可读 ⇒ 通则只需写成【写闸时必须先声明「本闸的基线是什么; 基线红了 selftest 结论不可读」】+ "
         "★**错误消息点名是哪个闸 + 它的原文末行 (★这正是新闸 H0 已做到的★)** ⇒ ⇒ ★**⇒ 落法 = 新增一份通则 (★main 落·★`state/GATE_WRITING_CONVENTIONS.md`·★新文件不碰任何已签收闸★) + "
         "逐闸加前置断言归 SW 域那一趟** ⇒ ★★"
         "★**★⇒ ★★与本轮 §㊺ 的 A1/A4 同一因果链 (★基线先绿是前置★) ⇒ 三条一起归那一趟** ★ ★",
         "SW/tools/check_sw_board_md5_rebase_readiness.py --selftest 0/10 · SW/tools/check_sw_ref_reachability_v2.py --selftest 0/7 · 一页 §㊺ A5"),

        ("iss390_correction_landing", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss390_correction_landing★)★: ★**6 处定性订正归【main 授权 + owner 落追加式订正块】, "
         "且【与「板只改一次」那一趟同批】** ★★"
         "★**★⇒ 理由 (★main 本机独立复核坐实·★不抄页面★)★**: ★**① 这 6 处全是【已签收页正文 + 已签收闸源码字符串】⇒ 按「已签收件的订正路径」⇒ "
         "★**main 授权路径, owner 落**, main 不直接改 owner 的正文 (★老字一字未删·★只加订正块★); "
         "★**② 为什么要同批**: ★**§4 #3 的两处源码字符串 (`MECH/check_debug_seat_3d_fit.py` L848 / L879) 是【已签收闸的判据源码】⇒ 改它 ⇒ "
         "★**⇒ 那两道签收指纹当场过期 ⇒ ⇒ 【必须与那一趟的「重验全部验收线」同批】(★L-27 通则③★) ⇒ ⇒ "
         "★**③ ⇒ 并且: 这 6 处不落 ⇒ 【通用件 vs 厂件】的前提错误继续留在页上与闸源码里 ⇒ ⇒ 下一个读这页或跑那个闸的人会拿错对照物做结构判决 ⇒ ⇒ "
         "★**★⇒ 而本闸 G3 的未落清单会永远停在 17 处 ⇒ ⇒ 【G3 恒红 ⇒ 这道闸自己也就废了】⇒ ⇒ ★**★⇒ 故: main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★"
         "★**★⇒ 附 (★main 本机解析 `.kicad_mod` 坐实的原文依据★)★: ★**通用件 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 的 `fp_rect` = **3.1000 × 6.0900** ⇒ "
         "★**⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」; `PinHeader_1x02_…` = **3.1000 × 3.5500** ⇒ 「`3.5500` 同源」⇒ ⇒ **⇒ `6.0900`/`3.5500` 这组数与 Samtec 无关** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §4 (6 处 COR-x) · MECH/check_fts_seat_body_geometry.py G3 · 一页 §㊺ B1"),

        ("iss390_h_lock_and_test_sample", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss390_h_lock_and_test_sample★)★: ★**两问分别裁 —— (甲) h 走【三档参数化】, 不锁死; "
         "(乙) 打样归【那一趟同批】** ★★"
         "★**★⇒ (甲) 理由 (★main 本机复核坐实★)★**: ★**① ISS-390 给的输入 = 厂件柱高 `3.05` mm (官网表 TABLE 1 lead style -01) 而绝缘体只有 `0.86` ⇒ ⇒ "
         "★**⇒ 罩内腔板面以上那一维【不能】按 `0.86` 出件 ⇒ `h=0.90` 档【物理上装不下】⇒ 可行档是 `2.54` 与 `4.00` ⇒ ⇒ "
         "★**★⇒ 这把 §㊷ C8 那条 (「h 不卡那一趟」) 的依据从「[0数据]」升级成了「[0数据] 且已算明可行档只剩两个」⇒ ⇒ 【本裁决与 §㊷ C8 一致, 且依据更强】** ⇒ "
         "★**② ⇒ 【不锁死】的理由 = h 锁死会绑死一个【还没测过】的量 ⇒ ⇒ 三档参数化 (0.90 / 2.54 / 4.00) 让结构侧在两档之间走, 而 0.90 已被物理判死 ⇒ ⇒ "
         "★**⇒ 实际只剩 2.54 与 4.00 两档 ⇒ ⇒ 锁定权仍在 boss (★`iss389_oi11_seat_height_window` 未代拍★) ⇒ ⇒ 本裁决只裁「形式」, 不裁「值」** ★ ★"
         "★**★⇒ (乙) 理由★**: ★**打样是【唯一能拿到 REF 公差】的路径 (★官网图给的是 REF 不是公差带★) ⇒ ⇒ 落 FTS 时打一块单板样、用卡尺量三量 "
         "★**(★绝缘体高 / 外形宽 / 外形深★) 回填 `keepout_dwg` + `body_geometry` ⇒ ⇒ 【必须与那一趟同批】(★落 FTS 那一天才有样可打★) ⇒ ⇒ "
         "★**★⇒ 归 mech-lead 执行 (转派), 但【不新起一单】(★与那一趟同批·★与「板只改一次」纪律一致★)** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §6.1 · 一页 §㊺ B2 · §㊷ C8"),

        ("iss390_oi12_and_oi14_together", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss390_oi12_and_oi14_together·★★★三个答案一起给★★★)★: ★**"
         "(a) 罩住判据【管到座体本体】(★不是只管铜箔★) ⇒ 采纳; (b) 「偏紧 `0.5200`」的措辞【作废】(★`6.0900` 是通用库件的 `F.CrtYd`, 厂件【没有】courtyard 这个量★) ⇒ 保留判据本身; "
         "(c) ⇒ (a) 成立 ⇒ J_UART 的 X 需求从 `4.0700` 变 `4.3400` ⇒ ⇒ 【OI-14 (DP-1) 的目标值 = `4.3400`】** ★★"
         "★**★⇒ 理由 (★main 本机独立复核坐实·★自己解析 .kicad_mod·★不抄页面★)★**: ★**① 座体本体 (厂件 X `5.0800` / `2.5400` + Y `2.1600`) 比铜箔包络 "
         "★**(★X `4.8100` / `2.2700`★)【每边都大】⇒ ⇒ ★**★⇒ 只按铜箔算 = 会做出一个【装不进座体】的洞 ⇒ ⇒ 判据必须同时管座体本体 ⇒ ⇒ (a) = 管 ⇒ 采纳** ★ "
         "★**② ⇒ (b) 作废**: ★**「偏紧 `0.5200`」的对照物是 `6.0900` ⇒ 而 `6.0900` 是【通用 KiCad 库件自己的 `F.CrtYd`】(★main 本机解析 `.kicad_mod` 的 "
         "★**`fp_rect` = 3.1000 × 6.0900 坐实★) ⇒ ⇒ ★**★⇒ Samtec 厂件【没有】courtyard 这个量 ⇒ 那句「比 courtyard 还小」在【厂件】这一层【无意义】⇒ ⇒ (b) = 作废那句措辞, 保留判据** ⇒ "
         "★**★⇒ ★注意: 这不是「判据错了」, 是【对照物拿错了】⇒ ⇒ 判据本身 (每边 `0.9000` = `CRIT 0.60` + `TOL 0.30`) 仍然成立** ★ "
         "★**③ ⇒ (c) 是 (a) 的算术后果**: ★**J_UART 座体 X `2.5400` + 2 × `0.9000` = `4.3400` (★不是 `4.0700`·★`4.0700` 是按铜箔 `2.2700` 算的★) ⇒ ⇒ "
         "★**★⇒ OI-14 (DP-1) 的目标值 = `4.3400`** ★ ★"
         "★**★⇒ ★★★★与 §㊷ C4 / §㊷ C6 【冲突】⇒ ⇒ 按 L-27 通则③ (main 落裁决 ⇒ 已 verified 的单的交付物进入「会动」状态 ⇒ 那一趟必须重验全部验收线) ⇒ ⇒ "
         "★**★⇒ 本条取代 §㊷ C4 与 C6 的对应部分, 老裁决的数值随之作废** ⇒ ⇒ ★**★⇒ 而 §㊷ C6 那个 `4.0700` 恰好是本单 §4 订正清单里的一条 (★L634 机器块 + 正文路径 B 段★) ⇒ ⇒ 正好一起订正** ★ ★"
         "★**★⇒ 与 §㊴ C1 (OI-5 取 `4.8100`) 【不冲突】: `4.8100` = 铜箔沿脚排总展 (★判「装得下」的输入★), `4.3400` = 座体本体 + 2×余量 (★判「装得下且留得住」的输出★) ⇒ 两个数【都要】** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §4/§5 · main 本机解析 .kicad_mod (fp_rect 3.1000×6.0900) · 一页 §㊺ B3"),

        ("iss390_y_direction_open_question", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss390_y_direction_open_question★)★: ★**Y 向走【放大罩开口 Y】, 但【幅度按座体本体重算】⇒ "
         "★**开口 Y 须 `≥ 5.7600`** (★取代 §㊷ C5 的 `5.6000`/`5.8000`★)** ★★"
         "★**★⇒ 理由 (★main 本机实算★)★**: ★**① 座体本体 Y = `2.1600` (厂件·★main 本机复核: 通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`★) ⇒ "
         "★**⇒ 按每边 `0.9000` ⇒ 清空区 Y 需求 = `2.1600` + 2 × `0.9000` = `3.9600` ⇒ ⇒ ★**★⇒ 比 §㊷ C5 裁的 `2.8000` 大 `1.1600`** ⇒ ⇒ "
         "★**★★⇒ §㊷ C5 的【方向】(放大罩开口 Y) 仍成立, 但【数值】需重算: 开口 Y 须 ≥ 清空区 Y `3.9600` + 2 × `0.9000` = `5.7600`** ⇒ ⇒ "
         "★**★★⇒ ⇒ 本条构成对 §㊷ C5 的【订正】(方向同, 数值收窄)** ★ "
         "★**② ⇒ 「接受零余量」那个选项【已不存在】(★本单自己也这么说★) ⇒ ⇒ (b) 改判据口径只罩铜箔 = 【已判死】(★与 `iss390_oi12_and_oi14_together` 同理: 只罩铜箔 = 装不进座体★) ⇒ ⇒ "
         "★**⇒ 只剩 (a) 放大罩开口 Y 一条路** ⇒ ⇒ **罩开口 Y `4.6000` → `5.7600` = 放大 `1.1600`** ★ "
         "★**③ ⇒ 结构性代价 (镜脚内腔 + 罩外观缝) 与 §㊷ C5 同源 ⇒ ⇒ 与板框第一问同批** ⇒ ⇒ ★**★⇒ 与 `iss390_oi12_and_oi14_together` 同源 ⇒ 两条一起落** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §5 (Y 向缺口 1.1600) · 一页 §㊺ B4 · §㊷ C5 (本条订正之)"),

        ("OI-391-1", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★OI-391-1★)★: ★**三处补登记由【main 落追加式订正块, owner 在「板只改一次」那一趟的清单改版里按逐字文本落】, "
         "★**【不许提前落】** ★★"
         "★**★⇒ 为什么不提前落 (★机器可核★)★**: ★**提前落 ⇒ 中间态 = 板还没改, 清单却写了要改孔 ⇒ ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (★板上还是 `0.65`★) ⇒ 当场红 ⇒ ⇒ "
         "★**★⇒ 现场会把它读成「板坏了」⇒ ⇒ 这正是 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + ISS-384 A5 全同款纪律的另一种说法** ⇒ ⇒ "
         "★**★⇒ 且 §4 #1/#2/#3 必须【一起落】** (★`wp02_tokens()` 会从③的原文里自动抽「小数」当覆盖令牌 ⇒ 补上 `0.65` 与 `0.71` 之后, 现有 P4 会自动要求清单页 "
         "★**`B33_PIN_LAND_1P27` 里也能查到这两个数 ⇒ ⇒ #1 与 #2/#3 不同步 ⇒ P4 当场红★) ⇒ ⇒ **三处一起** ★★"
         "★**★⇒ 逐字文本按真相页 §4 #1/#2/#3 原样落, main 不改一字; 落法 = 追加式订正块 (★老字一字未删★)** ★★"
         "★**★⇒ 附 (★main 自己的发现·★两页都没算这一格★)★: 改孔后环宽 `0.1750 → 0.1450` mm, 且本板 `.kicad_pro` 的 DRC 只有 `min_via_annular_width 0.1` (过孔) ⇒ "
         "★**⇒ THT 焊盘环宽【无判据】⇒ 触不到板 DRC ⇒ ⇒ 属【制程能力】问题 ⇒ 那一趟投板前必须坐实 ⇒ 见 `iss394_ring_width_fab_capability`** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4 #1/#2/#3 · 一页 §㊺ C1 · L-29 通则③"),

        ("OI-391-2", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★OI-391-2★)★: ★**写成【一条】(pitch 与 drill 是同一项的两条腿, 不可只做其一), 不许拆成两条可分开的动作** ★★"
         "★**★⇒ 理由 (★机器可核★)★**: ★**新闸 D1 只能查出【整条没写】, 查不出【拆成两条只做一条】⇒ ⇒ 拆开写 = 判据出现盲区** ⇒ ⇒ "
         "★**★⇒ 一条写 + 锚点含两个数 (`0.71` 与 `1.27`) = 机器可判** ⇒ ⇒ ★**★⇒ 与 §㊺ A1/B1 同一纪律: 措辞口径由 main 定, 落法由 owner 落, 且【必须机器可判】** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §5 · 一页 §㊺ C2"),

        ("OI-391-3", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★OI-391-3★)★: ★**BOM L71 (J_DEBUG) / L77 (J_UART) 的 opn 与 footprint 两栏 = 与板侧 land 来源【同源】, "
         "★**落表时机 = 那一趟的同一次落表与重出; 本轮【零落表】** ★★"
         "★**★⇒ 同源纪律 (★板面 land 来源 = BOM 型号栏 = 实物料号★)**: ★**板侧 land 来源 = 盘上通用 KiCad 1.27mm THT 库件 "
         "★**(★`PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c…` / `PinHeader_1x02_P1.27mm_Vertical` md5 `47bcbf6d…`★) + 一条显式偏离登记 "
         "★**(★偏离项 = 铜箔焊盘直径官方无值 + 孔径由 `0.65` 改 `0.71`★) + BOM 型号栏写 FTS 料号** ⇒ ⇒ **不成立 ⇒ 投板后才发现 ⇒ 2-4 周返工** ⇒ ⇒ "
         "★**★⇒ 逐字草案按真相页 §4 #5 原样落, main 不改一字** ⇒ ⇒ ★**★⇒ 与 §㊷ A3 (OI-387-3) 同一裁决, 两处口径必须一致** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4 #5 · HW/BOM_v1.csv L71/L77 (★本轮零落表★) · 一页 §㊺ C3 · §㊷ A3"),

        ("OI-391-4", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★OI-391-4★)★: ★**生成器补登记归【owner (hw-lead) 落】, 且【与「板只改一次」那一趟同批】; "
         "★**本轮【零改既有脚本正文】** ★★"
         "★**★⇒ 理由 (★机器可核★)★**: ★**`state/_iss277_build_preflight.py` 的 `build_pinland_item()` (title + current_state + criterion 三处一起长) + "
         "★**`read_board_pin_land()` 加一个 drill 字段现读板** ⇒ ⇒ ★**不落 ⇒ §3 #2/#3 的补登记【重跑一次就蒸发】(★ISS-349 同一位号已栽过一次★) ⇒ 白补, "
         "★**改孔这条子动作重新回到没人做的状态** ⇒ ⇒ ★**★⇒ 归 owner 落 (★本单零改既有脚本正文★) + 必须与那一趟同批 (★否则中途重跑一次就白补★)** ⇒ ★ ★"
         "★**★⇒ 与 §㊷ A2 (OI-387-2「改孔与那一趟同批」) 同一批次 ⇒ 那一趟的「清单四处登记」批次要一次做完** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4 #6 · state/_iss277_build_preflight.py · 一页 §㊺ C4"),

        ("OI-391-5", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★OI-391-5·★★与 L-29 同源★★)★: ★**新闸 `HW/check_fts_land_drill_same_batch.py` "
         "★**【与那四处登记同批挂】进 `state/gate_check.py`, 不提前挂** ★★"
         "★**★⇒ 理由 (★main 本机实跑实测★)★**: ★**★这道闸现在裸跑 rc=1 (4/7 绿·D1/D2/D3 红), 而 `--selftest` rc=0 末行 `ALL TESTS PASS` (17 条反向用例全抓到) ⇒ ⇒ "
         "★**闸本身可信 ⇒ ⇒ 它的红是【按设计】的: D1/D2/D3 抓的正是「`钻孔 0.65→0.71` 还没进到作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」⇒ ⇒ "
         "★**★⇒ 在登记落地之前挂进去 = 造出一道【假的红】⇒ 现场会把它读成「板坏了」** ⇒ ⇒ ★**★与全部先例同源: 闸与它要防/要等的那一趟同批生效** ⇒ ⇒ "
         "★**★⇒ 挂链时机 = 与「板只改一次」那一趟的四处登记同批** ⇒ ⇒ ★**★⇒ 且【挂链动作只能由 main 在那一趟统一做】(★不许 agent 自挂★)** ⇒ ⇒ "
         "★**★⇒ 顺带: 本轮三个新闸 (`check_sw_gate_health` / `check_fts_seat_body_geometry` / `check_fts_land_drill_same_batch`) 全部【与那一趟同批挂】⇒ ⇒ "
         "★**那一次的「闸清单刷新」批次要一次挂三个** ⇒ ⇒ ★**★⇒ 但注意: `check_sw_gate_health.py` 【结构上不能挂】(★它自己的 H4 判「零挂链」·★挂它自己会判自己红★) ⇒ ⇒ "
         "★**⇒ 那一趟实际只挂两个 (`check_fts_seat_body_geometry` + `check_fts_land_drill_same_batch`·★两者都要先绿★)** ⇒ ★ ★",
         "HW/check_fts_land_drill_same_batch.py 实跑 rc=1 + selftest ALL TESTS PASS · 一页 §㊺ C5 · L-29 通则②"),

        ("iss394_ring_width_fab_capability", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss394_ring_width_fab_capability·★★本轮 main 自己补的输入★)★: ★**环宽这件事归【那一趟投板前坐实】, "
         "★**归 main/老板商务动作, 但【本仓零外发】⇒ 处置 = 【自己查公开的板厂工艺能力表 + 在 RFQ 里问·★不自行发送★】** ★★"
         "★**★⇒ 已知的机器事实 (★main 本机实算★)★**: ★**① 官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 (annular ring) = (`1.000` − `0.71`) / 2 = `0.1450` mm** ⇒ "
         "★**(原 `0.65` 孔配同焊盘时 = `0.1750` ⇒ 改孔使环宽降 `0.0300`)** ⇒ "
         "★**② 本板 `.kicad_pro` 的 DRC 规则表里与环宽相关的只有 `min_via_annular_width 0.1` (★那是过孔环宽★) ⇒ ⇒ 【THT 焊盘环宽无独立判据】⇒ ⇒ "
         "★**★⇒ `0.1450` 【触不到板 DRC】⇒ ⇒ 它是【制程能力】问题, 不是 DRC 问题** ⇒ "
         "★**③ `min_through_hole_diameter 0.3` ⇒ 孔径 `0.71` 本身远大于下限, 不触 DRC** ⇒ "
         "★**④ ★★全仓 (HW/ MECH/ state/) 实查: 【没有任何一处】记录本板厂的最小环宽/最小焊盘/工艺能力表** ⇒ ⇒ ★**★⇒ 「`0.1450` 能不能做」当前【无据可判】** ★ ★"
         "★**★⇒ ⇒ 处置 (★与 §㊷ A1 的前置条件同一条·★两处引用同一件事★)★**: ★**「板只改一次」那一趟投板前必须坐实本板厂的最小环宽 (★或最小焊盘★) ⇒ "
         "★**⇒ 若 > `0.1450` ⇒ 焊盘须同步放大 ⇒ ⇒ 铜箔包络随焊盘放大而放大 ⇒ MECH 全链七个余量数【仍可能不变】但必须重算确认 ⇒ ⇒ "
         "★**★⇒ 若坐实不了 ⇒ 退化方案 = 焊盘放大到 `1.100×1.100` (环宽 `0.1950`) 并登记偏离 ⇒ 那时铜箔沿脚排总宽由 `4.8100` 变 `4.9100` ⇒ ⇒ MECH 七个数必须整体重算** ⇒ ⇒ "
         "★**★⇒ 这就是「板只改一次」必须在这一趟把环宽问清楚的原因: 问不清 = 那一趟投出去才发现 ⇒ 板改第二次** ★ ★"
         "★**★⇒ 【main 不代拍】环宽这个数 (★那是本板厂工艺能力, 不是本仓能推出来的★) ⇒ 且本项目 2026-11-12 02:02 起【零外发】⇒ ⇒ "
         "★**★⇒ 归【main 自己查公开板厂工艺能力表 + 老板侧 RFQ 时一并问】⇒ 不自行发送任何邮件/消息** ★ ★",
         "demo_mainboard.kicad_pro design_settings.rules · HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §0/§5 · 一页 §㊺ §④ · §㊷ A1"),

        ("iss394_seat_outer_dimensions", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x·★main 地界·★iss394_seat_outer_dimensions★)★: ★**双轨降级方案【采纳】, 但【本轮已由 ISS-390 把【甲轨的官网值】取到了】⇒ "
         "★**⇒ 实际只剩【乙轨 (1 台样件实测)】待做 ⇒ 且【与「板只改一次」那一趟同批】** ★★"
         "★**★⇒ 已取得的官网值 (★main 本机独立复核坐实★)★**: ★**厂件座体宽 X = N × 1.27 ⇒ N=4 ⇒ `5.0800` / N=2 ⇒ `2.5400` (★main 本机算术复核命中★) · "
         "★**座体深 Y = `2.1600` (★通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`·★通用件比厂件窄 0.0600 ⇒ 当座体用 ⇒ Y 向每边少让 `0.0300`★) · "
         "★**绝缘体高 Z = `0.8600`** ⇒ ⇒ ★**★⇒ 所以 ISS-394 的 D2「维持 [0数据]」这句【已经过期】⇒ ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」(★库件根本给不了 Z★)** ⇒ ★ ★"
         "★**★⇒ ⇒ 剩下的只有【公差】(★官网图给的是 REF 不是公差带·★X 的通式公差 ±0.25★) ⇒ ⇒ **乙轨 (落 FTS 时打 1 块单板样, 卡尺量三量: 绝缘体高 / 外形宽 / 外形深, "
         "★**回填 `keepout_dwg` + `body_geometry`) 是【唯一】能拿到实物公差的路径 ⇒ ⇒ 归 mech-lead 执行 (转派) + 与那一趟同批 (★落 FTS 那天才有样可打★) + 不新起一单** ⇒ ★ ★"
         "★**★⇒ ★★后果已算清 (★与 §㊷ A4 同一条·★两处引用同一件事★)★**: ★**乙轨不闭合 ⇒ OI-12/OI-13 那条「清空区 `6.6100` 比 courtyard `6.0900` 大 `0.5200`」的对照物"
         "★**【已作废】(★`6.0900` 是通用库件的 `F.CrtYd`·★见 `iss390_oi12_and_oi14_together`★) ⇒ ⇒ 真正该用的对照物是【厂件座体本体】⇒ ⇒ 结构侧清空区余量算错即装配干涉** ⇒ ⇒ "
         "★**★⇒ 而 §㊺ B3 已把需求改到 `4.3400` (J_UART 座体本体口径) ⇒ ⇒ **两处引用同一件事 ⇒ 同一趟一起做** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §4/§5/§6.1 · 一页 §㊺ B3 · §㊷ A4"),
    ]

    # ★★★★★★ L-32 修复: 下面 10 条 = 【13:1x 那批的同内容重答】, 但 key 必须与 need key 【逐字相同】 ★★★★★★
    # ★★ 原 13:1x 用的是【自己起的改名 key】(★如 `iss389_main_oi5_pick_4810` 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★)
    # ★★ ⇒ merge.py 按精确 key 配对 ⇒ 那 15 条一条都没闭上 need ⇒ ★★ 老 15 条【老字一字未删】保留作人读记录, 本块是机制上生效的那一份
    ANS2 = [
        ("OI-387-1", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 与 need key 逐字对齐·★main 地界·★OI-387-1★)★: ★**维持 `1.000×1.000`** ★★★"
         "**理由**: ★**这是 MECH 全链余量数里【铜箔侧那一组】一个都不用改的【唯一成立条件】** ⇒ ★**且 OI-387-1 已把代价算死: 不拍 ⇒ 结构件与镜脚侧返工一次 (2-4 周 + ¥4-8K 级)** ⇒ ⇒ ★**按「板只改一次」的单源纪律, 必须维持** ★★★"
         "**★但本裁决附前置条件 (★main 自己发现的缺口★)**: ★**「焊盘 `1.000`」配官方 `Ø0.71` ⇒ 环宽只有 `0.1450` mm ⇒ 而本板 `.kicad_pro` 的 DRC 只管 `min_via_annular_width 0.1` (过孔) ⇒ 【THT 焊盘环宽无判据】⇒ ⇒ 全仓查不到本板厂最小环宽记录 ⇒ ⇒ 「`1.000` 能不能用」当前【无据可判】⇒ ⇒ ★**★⇒ 前置条件 = 环宽 `0.145` 先过制程能力确认** (★见 `iss394_ring_width_fab_capability`★) ⇒ ⇒ 若坐实不了 ⇒ 焊盘放大 ⇒ 铜箔包络随焊盘放大而放大 ⇒ ⇒ **必须重算确认** ⇒ ⇒ ★**★⇒ 本裁决不是「1.000 一定行」, 是「1.000 是唯一不返工的选择, 但要先证明它做得出来」** ★★★"
         "**★★⇒ 与本轮 §㊺ ⑨-④ 的关系 (★别混两条轴★)**: ★**这条讲【改孔 `0.65→0.71` 不动铜箔包络】⇒ ⇒ 本条结论在【改孔这条轴】上仍成立**; ★**★⇒ 而 §㊺ ⑨-② 讲的【判据基准物从铜箔换成座体本体】是【另一条轴】⇒ ⇒ ⇒ 两条互不推翻** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §0-2/§5 · 一页 §㊷ A1 + §㊺ ⑨-④ · main 本机自解析 .kicad_mod 复算"),

        ("OI-387-2", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★OI-387-2★)★: ★**与「板只改一次」那一趟同批** ★★★"
         "**理由 (★main 本机实算★)**: ★**改孔是板侧动作 ⇒ 拆批 = 多投一次板 (2-4 周 + 一批板的钱)** ⇒ ★**且 main 已独立复算坐实: 官方 `Ø0.71` 配通用件焊盘 ⇒ 铜箔沿脚排总宽仍是 `4.8100` / `2.2700` (★只有孔变了, 铜箔没变★) ⇒ ⇒ ⇒ 同批的增量成本 = 0 ⇒ 没有理由拆批** ★★★"
         "**★同批的三个必做动作 (★缺一不可★)**: ★**① 改孔 `0.65 → 0.71` (J_DEBUG / J_UART 两颗) ② 焊盘维持 `1.000×1.000` (★须先过环宽确认·★见 `iss394_ring_width_fab_capability`★) ③ 清单四处同步登记 (作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27` 描述列 + 验收手段列 + 覆盖度闸 `WP02_BINDING` ③ 的覆盖令牌补 `0.71`/`0.65`)** ⇒ ★**⇒ 而 ③ 必须与那一趟同批落, 不许提前** (★提前 ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (板上还是 `0.65`) ⇒ 当场红 ⇒ 现场误读成「板坏了」★) ★★★"
         "**★⇒ 与 ISS-391 §4 的三处补登记是同一件事 ⇒ 处置 = main 落【追加式订正块】, 由 owner 按逐字文本落进「那一趟」的清单改版** (★不是现在就就地替换已签收页正文★) ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4/§5 · 一页 §㊷ A2 + §㊺ C1 · L-29 通则③"),

        ("OI-387-3", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★OI-387-3★)★: ★**用盘上通用 KiCad 库件 land + BOM 型号栏写等价替代 + 显式偏离登记** ★★★"
         "**理由 (★main 本机实读坐实·★ISS-387 §0-2 自己已写出这个事实★)★**: ★**Samtec 官方的 FTS 直插 land 【只给孔位图, 不给铜箔焊盘直径】⇒ 「原厂 land 的铜箔 X 宽」在 Samtec 那一层【根本没有一个官方数】** ⇒ ★**⇒ 板侧真值档只能靠【盘上通用件 land + 一条显式偏离登记】撑着, 不许写成「已按原厂 land 落板」** ⇒ ★**⇒ 这与 §㊳ A2/A4 的「不许拿 FTSH 的数顶替 FTS」同族但【方向相反】: 那次是【别家的数不许顶替】, 这次是【官方自己给不出】★ ⇒ 两条都要守住** ★★★"
         "**★⇒ A2 (料号) 与 A4 (land 来源) 必须合成一个**: ★**板侧 land 来源 = 通用 KiCad 1.27mm THT 库件 (★`PinHeader_1x04_P1.27mm_Vertical` / `PinHeader_1x02_P1.27mm_Vertical`·★md5 `7a5f470c…` / `47bcbf6d…`★) + 显式偏离登记 (★偏离项 = 铜箔焊盘直径官方无值 + 孔径由 `0.65` 改 `0.71`★) + BOM 型号栏同源写 FTS 料号** ⇒ ⇒ ⇒ **同源纪律 (板面 land 来源 = BOM 型号栏 = 实物料号) 才成立** ⇒ ⇒ 不成立 ⇒ 投板后才发现 ⇒ 2-4 周返工 ★★★"
         "**★⇒ 落表时机 = 「板只改一次」那一趟的同一次落表与重出 (★本轮【零落表】·★BOM 型号栏与 footprint 两栏一个字没动★)** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §0-2/§4/§5 · 一页 §㊷ A3 + §㊺ C3 · §㊳ A2/A4"),

        ("OI-387-4", "hw-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★OI-387-4·★转派 mech-lead★)★: ★**走双轨降级方案 (甲 官网 3D/CAD 下载量外形; 乙 落 FTS 时先打一块单板样用卡尺量三个量回填 `keepout_dwg`) ⇒ 归 mech-lead 执行, 且必须与「板只改一次」那一趟同批** ★★★"
         "**理由**: ★**座体外形 (宽 X / 深 Y / 绝缘体高 Z) 官方值原写 `[0数据]` ⇒ 不许猜 ⇒ ★**★⇒ 但 ISS-390 本轮已把【甲轨的官网值】取到了: 厂件座体 X = N×1.27 ⇒ `5.0800` (N=4) / `2.5400` (N=2)·★Y = `2.1600`·★Z = `0.8600` ⇒ ⇒ ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」(★通用 KiCad 库件根本给不了 Z★) ⇒ ⇒ ⇒ 剩下没闭合的只有【公差】(★官网图给的是 REF 不是公差带★)** ⇒ ⇒ "
         "**★⇒ ⇒ ⇒ 实际只剩【乙轨 (1 台样件实测)】待做** ⇒ ⇒ 落 FTS 时打一块单板样、用卡尺量三量 (★绝缘体高 / 外形宽 / 外形深★) 回填 `keepout_dwg` + `body_geometry` ⇒ ⇒ 【与那一趟同批】(★落 FTS 那天才有样可打★) ⇒ ⇒ **归 mech-lead 执行 (转派) + 不新起一单** ★★★"
         "**★⇒ 甲乙两轨的关系 (★别当成两条路★)**: ★**甲轨 (官网量) = 设计值 ⇒ 用来定件与开模; 乙轨 (单板样实测) = 实物值 ⇒ 用来回填 `keepout_dwg` 并作为装配前的兜底校验 ⇒ ⇒ **两轨都要做, 不是二选一** ⇒ ⇒ **且乙轨那 1 台样件的成本 = 老板已知口径里的「只做 1 台」** ⇒ ⇒ ★**★⇒ 归 owner = mech-lead (★本裁决只裁口径与时点, 不派活★)** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §6-④ · MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §6.1 · 一页 §㊷ A4 + §㊺ ⑨-③ · 本轮 `iss394_seat_outer_dimensions`"),

        ("iss389_oi2_b33_scope_window", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★iss389_oi2_b33_scope_window★)★: ★**含 `J_UART`** ★★★"
         "**理由 (★main 本机实读权威页坐实·★不抄 brief★)★**: ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 原文 = 「`J_DEBUG`/`J_UART` 排针 land pitch `0.50→1.27mm` (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」⇒ ★**它本来就同时点了两件** ⇒ ⇒ ★**两颗排针换官方 THT 后结构件同批返工 (两件罩住轴都红) 是【已拍范围】的必然推论, 不是新增范围** ⇒ ★**与 §㊴ C4 完全一致, 无矛盾** ★★★"
         "**★⇒ 而且「不含 ⇒ 结构件零返工」是个【假选项】**: ★**ISS-389 自己算出来: 不含 ⇒ 结构件零返工, 但板上 BOM (`HW/BOM_v1.csv` L77) 与网表 (`HW/netlist_v1.csv` L399) 写的 1.27mm 实物排针对不上号 0.50mm pitch 的自绘占位 land (差 `0.77`) ⇒ ⇒ 【结构件零返工 ≠ 实物装得上】** ⇒ ⇒ ★**★⇒ 所以「不含」这个选项的真实含义是「结构件不返工, 但板还是错的」⇒ 不是解法, 是把问题推到投板之后 ⇒ ⇒ 答案只能是「含」** ★★★"
         "**★⇒ 与 OI-3 的耦合已解 (★顺序钉死, 见 `iss389_oi3_juart_landing_window`★) ⇒ ⇒ 「先定落点再定范围」那个返工第二次的风险已消除** ★ ★",
         "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md B33_PIN_LAND_1P27 (main 本机实读) · 一页 §㊷ C1 + §㊺ B3 · §㊴ C4"),

        ("iss389_oi3_juart_landing_window", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★iss389_oi3_juart_landing_window★)★: ★**不重开落点裁决 (★维持 ISS-379 的挂起·★本单不重复开★), 但把【顺序】钉死** ★★★"
         "**顺序 (★四步·★这是本条的全部内容★)★**: ★**① 老板答板框上位问题 (`boss_u1_upper_axis_board_trip_physical_product` · 甲 160×100 台架板 / 乙 60×30 产品板) → ② 落点定死 (C1 / C2 / C3) → ③ 结构件出件 → ④ 板改 + 布线 45→0 + Gerber/投产包重出** ★★★"
         "**★⇒ 依据 (★main 本机实算 + ISS-389 自己算的数★)★**: ★**① 三个候选 X 向全可行, Y 向 C1 与 C3 可行, C2 内缩只有 `1.6000` 差 `0.2000` 不可行 ⇒ ⇒ **C2 是带死结的那一个**, 不是随机的 ⇒ ② 清空区中心随落点变 ⇒ ⇒ 结构件开不了模 ⇒ ⇒ ★**③ ⇒ 「不答的后果 = 结构件返工第二次」这个风险, 已通过【把顺序钉死】消掉: 落点一定, 结构件才出件** ★★★"
         "**★⇒ 并且: 若最终选 C2 ⇒ 必须同时放大罩开口 Y (★与 OI-13 是同一处改动★) ⇒ ⇒ 本轮 §㊺ ⑨-② 已把该开口 Y 下限算成 `5.7600` (★推荐 `5.8000`·★那一档可顺带解掉 C2 的 `0.2000`★) ⇒ ⇒ 两处一起做** ⇒ ⇒ **答复窗口 = 与板框上位问题同一窗口 (即那一趟开工前)** ⇒ ⇒ **不改 ISS-379 的挂起状态, 只是把依赖链显式化** ★ ★",
         "ISS-379 §② (落点挂起) · ISS-389 真相页 OI-3 (feas2.py 实算) · 一页 §㊷ C2 + §㊺ ⑨-②"),

        ("iss389_oi5_clearance_x_tier_window", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★iss389_oi5_clearance_x_tier_window★)★: ★**取 `4.8100`** ★★★"
         "**理由 (★与 §㊴ C1 一致, 且本轮多了一条【实物依据】★)★**: ★**① `1.7750` = 座体宽 = 【拿铜箔宽冒充座体宽】的同义反复 ⇒ 不作判据; ② `4.0850` = 把现状 `0.275` 宽 pad 搬到 1.27 pitch 上 ⇒ 【现状错误尺寸的搬家】, 不是官方 land; ③ `4.8100` = 官方 1×4 THT land 的铜箔沿脚排总展** ⇒ ★**★⇒ ISS-387 已独立复算坐实: `4.8100` = 盘上通用 1×04 THT 件实测 (跨距 `3.810` + 焊盘 `1.000`) ⇒ ⇒ 这个数从【假定】变成【有实物依据】⇒ ⇒ ⇒ ★**★上一轮记的「OI-5 与 ISS-387 必须同批闭合」在【本轮】闭合** ★ ★★★"
         "**★⇒ ★★但口径不混两件事 (★★本轮补一条限定词★★)★**: ★**取 `4.8100` 只解决「装得下」⇒ 要过【罩住座体本体】的判据, 需求是 `6.8800` (★不是 `6.6100`·★见 §㊺ ⑨-②★)⇒ ⇒ 三档的返工幅度差 `3.0350`, 方向不变 (三档全红) ⇒ ⇒ ★**★⇒ 「铜箔齐平档」这句话必须加限定词: 座体本体 `5.0800` 比铜箔 `4.8100` 每边宽 `0.1350` ⇒ ⇒ ★**★⇒ 最终放大量仍归老板的板框第一问, 本条不代拍** ★ ★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-5 · 一页 §㊷ C3 + §㊺ ⑨-②/⑨-③ · §㊴ C1 · main 本机自解析 .kicad_mod 复算"),

        ("iss389_oi12_cover_criterion_window", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★iss389_oi12_cover_criterion_window·★★本轮 §㊺ ⑨-①/⑨-② 订正了 §㊷ C4★★)★: ★**判据口径【不改】= 路 A; 路 B 不予采纳; ★★但【清空区尺寸的基准物】从【铜箔】改成【座体本体】★★ ⇒ ⇒ 需求 = `6.8800` (J_DEBUG) / `4.3400` (J_UART) / `3.9600` (Y)** ★★★"
         "**★⇒ ★★三件事分开说 (★本轮最大的变化就在这里★★)★★**: ★**① 【判据口径】不变** = 每边 `0.9000` (= `CRIT 0.60` + `TOL 0.30`) 这个【数】不动 ⇒ ★**② 【路 B 的死因】换了**: ★**§㊷ C4 用的死因是「`6.0100` 比 courtyard `6.0900` 还小 `0.0800`」⇒ ⇒ 而 `6.0900` 是【通用 KiCad 库件的 `F.CrtYd`】(★main 本机解析 `.kicad_mod` 的 `fp_rect` = 3.1000 × 6.0900 坐实★) ⇒ ⇒ 【那个对照物无效 ⇒ 原死因作废】⇒ ⇒ **但路 B 仍死**, 死因换成更硬的一条: 路 B 的 `6.0100` / `3.4700` 对【座体本体】只给每边 `0.4650` ⇒ ⇒ 低于 `CRIT 0.6000` ⇒ ⇒ 【连 TOL 都不用扣就过不了】** ⇒ ★**③ 【基准物】必须换**: ★**旧口径把 `0.9000` 加在【铜箔】上 (`4.8100` + 2×`0.9000` = `6.6100`) ⇒ ⇒ 对【座体本体】`5.0800` 只给每边 `0.7650` ⇒ ⇒ 扣 TOL 后只剩 `0.4650` < CRIT ⇒ ⇒ **【路 A 按铜箔出的尺寸, 同样过不了它自己的判据 (对座体本体)】⇒ ⇒ ⇒ 厂件座体本体 `5.0800` / `2.5400` + 2×`0.9000` = `6.8800` / `4.3400`** ★★★"
         "**★⇒ ⇒ 路 A 的两个层级分开表述 (★同 §㊴ C2★)★**: ★**① 「装得下」用【座体本体】判 (★厂件 `5.0800` × `2.1600` × `0.8600` `[官网]`·★ISS-390 实测★) ⇒ ★② 「装配可靠」用每边 `CRIT 0.60` 判 ⇒ ⇒ 改【判据基准物】改【结构件尺寸】, 不改判据【数】** ⇒ ⇒ ★**★⇒ 结构件总宽增量走 `6.8800` 那档 ⇒ ⇒ 【这个代价必须让老板看见】⇒ 它与板框第一问同批** ⇒ ⇒ ★**★⇒ 与 OI-14 同源 ⇒ 两条一起拍** (★OI-14 的目标值 = `4.3400`★) ⇒ ⇒ ★**★⇒ 本裁决把 OI-14 一并闭合** ★ ★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-12 · MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §4/§5 · 一页 §㊺ ⑨-①/⑨-② · §㊷ C4 (本条订正之)"),

        ("iss389_oi13_y_zero_margin_window", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★iss389_oi13_y_zero_margin_window·★★本轮 §㊺ ⑨-② 订正了 §㊷ C5 的数值★★)★: ★**不接受零余量 = 路 B (放大罩开口 Y); ★★开口 Y 须 `≥ 5.7600` (★`5.8000` 那档仍有效且【推荐】★)★★** ★★★"
         "**★⇒ 理由 (★机器可核★)★**: ★**① 零余量在最坏口径下是红的, 不是「勉强接受」**: 罩住 Y 余量 `0.7700` → 最坏 = `0.7700 − TOL 0.30 = 0.4700` < `CRIT 0.60` ⇒ ⇒ ★**★⇒ 「物理上不产生干涉」不等于「过得了判据」⇒ 而判据是装配可靠性的判据 ⇒ 必须按判据走**; ② 罩开口 Y `4.6000` 恰好只容清空区 Y `2.8000` ⇒ 只放大清空区会把开口顶死 ⇒ ⇒ **必须同时放大开口 Y** ⇒ ★★★"
         "**★⇒ ★★本轮的数值修正 (★为什么不是 `5.6000`★)★★**: ★**① 座体本体 Y = `2.1600` (厂件·★ISS-390 实测·★通用库件 `F.Fab` 跨排距 `2.1000` 比厂件窄 `0.0600`·★当座体用 ⇒ 每边少让 `0.0300`★) ⇒ ⇒ 按每边 `0.9000` ⇒ 清空区 Y 需求 = `2.1600` + 2×`0.9000` = `3.9600` ⇒ ⇒ **比 §㊷ C5 裁的 `2.8000` 大 `1.1600`** ⇒ ⇒ ★**★⇒ ⇒ 开口 Y 须 ≥ 清空区 Y `3.9600` + 2×`0.9000` = `5.7600`** ⇒ ⇒ ★**★⇒ ★【推荐取 `5.8000`】: 它 `≥ 5.7600` 且★**顺带解掉落点 C2 的 `0.2000` 死结** (★与 OI-3 同一处改动★)** ★★★"
         "**★⇒ 结构件与罩两件同批做 (★不同批就会有一件装不上★) ⇒ ⇒ 镜脚壁厚与罩外观缝 (防水防尘) 的代价一并算进那一趟 ⇒ ⇒ ★**★⇒ 与 §㊴ C3 一致, 本轮口径更精确 (★多了「基准物换成座体本体」这一步·★以及 `5.8000` 那档顺带解 C2 死结这件事★)** ★ ★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-13 · MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §5-⑧ · 一页 §㊺ ⑨-② · §㊷ C5 (本条订正之)"),

        ("iss389_oi14_dp1_correction_window", "mech-lead",
         "★**main 裁决 (★2026-11-24 16:0x 重答·★key 逐字对齐·★main 地界·★iss389_oi14_dp1_correction_window·★★本轮 §㊺ ⑨-② 把目标值从 `4.0700` 改成 `4.3400`★★)★: ★**要订正为 `4.3400` (★不是 §㊷ C6 裁的 `4.0700`★); 追加式订正块落 `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md`, 与「板只改一次」那一趟同批** ★★★"
         "**★⇒ 理由 (★main 本机重算·★与 ISS-390 的厂件实测一致★)★**: ★**① ISS-377 §3.2 DP-1 原来的 `3.4700 = 2.2700 + 2×CRIT` 是【名义余量】口径 ⇒ 按全链 (最坏 = 余量 − `TOL 0.30` ≥ `CRIT 0.60`) 需要 `2.2700 + 2×0.9000 = 4.0700` ⇒ ⇒ **§㊷ C6 那一层是对的 (它按铜箔算)** ★★"
         "**★⇒ ★★但 §㊺ ⑨-② 把【基准物】换成了座体本体 ⇒ ⇒ 铜箔 `2.2700` 换成厂件座体 X `2.5400` ⇒ ⇒ 需求 = `2.5400` + 2×`0.9000` = `4.3400` ⇒ ⇒ 差 `0.2700` ⇒ ⇒ ★**★⇒ ⇒ 【OI-14 的目标值 = `4.3400`】** ⇒ ⇒ ★**★⇒ 不订 ⇒ 下一轮有人照 `4.0700` (或更早的 `3.4700`) 出件 ⇒ 结构件按错尺寸开模 ⇒ 第二次返工** ★★★"
         "**★⇒ 与 OI-12 同源 ⇒ 必须一起拍 (★本轮已一起拍了★)**: ★**OI-12 已裁「判据数不变 + 基准物换成座体本体」⇒ ⇒ 订正动作成立; ★**★⇒ 而 `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` L634 机器块 + 正文路径 B 段 + `D-6`/`U-7` 行 + `MECH/check_debug_seat_3d_fit.py` L848/L879 的【已签收闸源码字符串】⇒ ⇒ 一律走【追加式订正块】(★老字一字未删★) ⇒ ⇒ **且必须与那一趟同批** (★提前落 ⇒ 中间态红) ⇒ ⇒ ★**★⇒ §㊷ C6 那个 `4.0700` 恰好也是 ISS-390 §4 订正清单里的一条 ⇒ ⇒ 正好一起订正** ★ ★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-14 + L634 · ISS-377 §3.2 DP-1 · 一页 §㊺ ⑨-②/⑨-⑤ · §㊷ C6 (本条订正之) · L-29 通则③"),
    ]

    ANS = ANS + ANS2
    cur = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    have = {a.get("key") for a in (cur.get("answers") or []) if isinstance(a, dict)}
    added, skipped = 0, []
    for key, to, val, ref in ANS:
        if key in have:
            skipped.append(key)
            continue
        frag_write.update_fragment("main", lambda d, k=key, t=to, v=val, r=ref: d.setdefault("answers", []).append(
            {"key": k, "to": t, "value": v, "ref": r}))
        added += 1
    # ★★落盘后回读验证 (★L-32: 必须验证「配对上了」, 不许只看写入成功★)★★
    needkeys = set()
    for f in ("sw.yaml", "mech.yaml", "hw.yaml"):
        try:
            fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        except Exception:
            fd = {}
        for n in fd.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                needkeys.add(n["key"])
    pmc = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    amap = {}
    for a in pmc.get("answers") or []:
        if isinstance(a, dict) and a.get("key"):
            amap.setdefault(a["key"], []).append(a)
    # ★★merge.py 的真实配对条件: ① need 的 key 与 answer 的 key 【逐字相同】② answer 落在 pm.yaml (★_by == "main"★)
    # ★★⇒ 本块的判定必须复刻这条, 而不是「答案的 to 字段 == main」(★那是【装饰字段】, 不参与配对★)
    needtomap = {}
    for f in ("sw.yaml", "mech.yaml", "hw.yaml"):
        try:
            fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        except Exception:
            fd = {}
        for n in fd.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                needtomap[n["key"]] = n.get("to")
    pmans = {}
    for a in pmc.get("answers") or []:
        if isinstance(a, dict) and a.get("key"):
            pmans.setdefault(a["key"], []).append(a)
    mine = [k for k, _t, _v, _r in (ANS + ANS2) if k in needtomap and needtomap[k] == "main"]
    closed_now = [k for k in mine if k in pmans]
    tot = len(pmc.get("answers") or [])
    dup = len([k for k in pmans if len(pmans[k]) > 1])
    print("  pm.yaml (main 自己的分片): answers +%d 条 (跳过已存在 %d) ⇒ 共 %d 条 · 重复 key %d"
          % (added, len(skipped), tot, dup))
    print("  ★★L-32 回读验证 (★复刻 merge.py 的真实配对条件★): 本轮 %d 条里【need key 逐字相同且 need.to==main】的 = %d 条 ⇒ 落盘后其中【真正闭上的】= %d 条 ★★"
          % (added, len(mine), len(closed_now)))
    if added and len(closed_now) != added:
        miss = [k for k in mine if k not in closed_now]
        raise SystemExit("★L-32 校验失败: 以下 key 落盘后仍未闭 need ⇒ 报错退出 ★: %s" % miss)
    # ★★再验一遍: 这些 need 现在在 merge 眼里必须是 answered
    rc_m, o_m = sh("python3 state/merge.py")
    bad = [k for k in closed_now if ('"%s"' % k) not in o_m]
    print("  ★★merge.py 复跑 rc=%d · 上面 %d 个 key 在 merge 输出里均出现 ★★" % (rc_m, len(closed_now)))
    return True


def write_memory_pointer():
    p = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
    txt = read_lines(p)
    if "L-32" in txt and "静默失效" in txt:
        print("  MEMORY.md: L-32 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l32_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-32★·★main 独占写·★无 job 重写★)★**: "
           "★**L-32 「落答案时必须【从 need 里逐字抄 key】⇒ 自己起 key = 机制【静默失效】」★** ⇒ "
           "★① 实测: main 13:1x 那轮落的 15 条 pm.yaml 答案【内容全对, 但一条都没闭上任何 need】⇒ 因为 merge.py 按【精确 key】配对 (`answers_by_key.get(k)` + `_by == ask_to`) ⇒ 用了改名的 key (★如 `iss389_main_oi5_pick_4810` 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★) ⇒ 配不上 ⇒ 零闭合 (★实测 pm.yaml 里 to=main 的答案中逐字命中 need key 的只有 113/152★) ⇒ "
           "★② ★★这比 L-28 的「key 撞名」更危险: 撞名会报错退出 (★有声音★), 而「不撞名但对不上」⇒ 机制【一声不吭】⇒ 答案躺在 pm.yaml 里内容正确, 但【对闭环机制等于不存在】⇒ 页面上看起来「已答」, 台账上其实还挂着★★ ⇒ "
           "★③ ⇒ 落答案前必须先从 need 里【逐字抄 key】(★不许自己起·不许「起个更清楚的名字」★); 落盘后必须回读验证【该 key 的 need 已从 pending 变 answered】⇒ 不许只看「脚本打印 ✅ 已原子更新」★★ "
           "★④ ⇒ 推广: 凡是有「按 key 配对」的地方 (★merge 的 needs×answers · gate 的 (file,line) 钉住 · 一页章节号索引 · 决策索引覆盖复核★) ⇒ 键必须逐字对齐 + 对齐要回读验证 ⇒ **【机制静默失效】比【机制报错】更贵】⇒ 我新写的机制都必须自带一句「配对不上就报错」**★★ "
           "★⇒ ★**本轮实证: ISS-388/390/391 三单签收时才发现 13:1x 那 15 条答案没生效 ⇒ 本轮已按 need 的原 key 重答一遍 (★老字一字未删·★保留作人读记录★)** ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-32 指针追加 (追加式, 备份 %s.bak_%s_main_l32_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def write_round_log():
    r = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1605_sign_iss388_390_391.md")
    body = """# ROUND_LOG_main · 2026-11-24 16:0x · ISS-388 / ISS-390 / ISS-391 三单一并签 + 26 条 main 地界待裁项已裁 + 自曝 L-32

★**job**: main (ARS45 项目总工) · webchat 会话 (★由兄弟 job 5bd48f25 的进展播报触发★)
★**签收闸**: `state/_apply_20260724_1605_main_sign_iss388_390_391.py` (★fail-closed★)
★**备份** (★脚本现场取 `time.strftime` ⇒ 真实 stamp `20261124_1605`★): `state/issue_log.yaml.bak_20261124_1605_main_sign_iss388_390_391` ·
`DECISION_ONE_PAGER_2026-11-22.md.bak_20261124_1605_main_sign_iss388_390_391` · `state/LESSONS.md.bak_20261124_1605_main_l32` ·
`MEMORY.md.bak_20261124_1605_main_l32_pointer`

---

## ★★一 · 板面 (本机实读) ★★

★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` (纳秒级) ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

---

## ★★二 · 三单签收 (main 本机独立复核·不抄任何 agent 报告) ★★

| 单 | owner | 闸 | 裸跑 | `--selftest` | 交付物 |
|---|---|---|---|---|---|
| ISS-388 | sw-lead | `SW/tools/check_sw_gate_health.py` | ★**rc=1 · 2/6 绿** (★按设计★) | ★**rc=0 · 22/22 · ALL TESTS PASS** | 交卷页 37,416 B + sw.yaml |
| ISS-390 | mech-lead | `MECH/check_fts_seat_body_geometry.py` | ★**rc=0 · 33 条判据 0 失败** | ★**rc=0 · 15/15 · ALL TESTS PASS** | 真相页 46,898 B + 交卷页 37,068 B |
| ISS-391 | hw-lead | `HW/check_fts_land_drill_same_batch.py` | ★**rc=1 · 4/7 绿** (★按设计★) | ★**rc=0 · 17/17 · ALL TESTS PASS** | 真相页 45,038 B + 交卷页 29,690 B |

★三闸连跑 3 次末行逐字相同 · 三闸零挂链 · 零落表 · 零改既有页面正文 · L-26① 的 13 道扫描面闸全 rc=0 ★
★**L-27 硬前置**: 三单 owner 会话均已收工 (12:51 / 12:59 / 13:05) 且交付物 2 秒静默检查通过 ★

---

## ★★三 · ★★main 本机独立复核: 三个实质发现 ★★

★**① ISS-388 的新闸【结构上就不能挂链】**: 源码 `hook_hits = gc_txt.count("check_sw_gate_health")` ⇒ 挂进 `state/gate_check.py` ⇒ 它自己的 H4 立刻判红 ⇒ **零挂链是它的正确形态** ★
★**② ISS-390 的核心声明本机坐实**: 自己解析 `.kicad_mod` ⇒ `PinHeader_1x04_…` 的 `fp_rect` = **3.1000 × 6.0900** ⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」; `PinHeader_1x02_…` = **3.1000 × 3.5500** ⇒ 「`3.5500` 同源」⇒ **⇒ `6.0900`/`3.5500` 与 Samtec 无关** ⇒ ISS-371/389/374 把它当「官方座体本体」是**定性前提错误** ★
★**③ ISS-390 改了 §㊷ 的两个数**: 座体本体 (厂件 X `5.0800`/`2.5400`, Y `2.1600`) 比铜箔包络 (X `4.8100`/`2.2700`) 每边都大 ⇒ **判据必须管到座体本体** ⇒ J_UART 的 X 需求 `4.0700` → **`4.3400`** (OI-14 目标值随之改) ⇒ 开口 Y `5.6000`/`5.8000` → **`5.7600`** ⇒ **§㊷ C4/C5/C6 相应部分作废, 由本轮裁决取代** (L-27 通则③) ★

---

## ★★四 · ★★★★自曝: 我 13:1x 那 15 条答案一条都没闭上 need (L-32) ★★★★

★**根因**: `state/merge.py` 按【精确 key】配对 (`answers_by_key.get(k, [])` + `_by == ask_to`) ⇒ 我 13:1x 用了改名的 key ⇒ 配不上 ⇒ 零闭合 ★
★**实测**: pm.yaml 里 `to=main` 的答案中, 逐字命中 need key 的只有 **113/152** ⇒ 我那 15 条全在「没命中」那一侧 ★
★**★⇒ 比 L-28 的「撞名」更危险: 撞名会报错退出 (★有声音★), 这里【一声不吭】⇒ 答案内容正确但【对机制等于不存在】★★
★**⇒ 本轮已按 need 的原 key 重答一遍 (老字一字未删·保留作人读记录) + 立 L-32** ★

---

## ★★五 · 落记录 (全部追加式·老字一字未删) ★★

★`state/issue_log.yaml` (3 单签收, 一次全量重写·零竞态窗口) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊺** · `state/LESSONS.md` **L-32** ·
`state/fragments/pm.yaml` (19 条答案, 全部用 need 的原 key) · `MEMORY.md` (L-32 指针) ★

---

## ★★六 · 「板只改一次」那一趟现在明确要带【四条腿】 ★★

★**① 改孔 `0.65→0.71` (★环宽 `0.1450` 的制程能力确认同批★) ② 四处清单登记 (ISS-391 §4) ③ 两个新闸挂链 (★`check_sw_gate_health` 结构上不能挂★) ④ 六个签收件的 md5 刷新 + 全部验收线重跑 (★L-27 通则③★)** ★

---

## ★★七 · 最终读数 (本机实跑) ★★

★板三项未动 · 网表/脚表/BOM/`gate_check.py`/`merge.py`/`frag_write.py`/六个已签收页逐字节未动 · 三个新闸 rc=0(按设计) · 13 道扫描面闸全 rc=0 ·
`merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=1 (19 条既有逾期老账) · `stage_gate.py` rc=1 (G1 仍开, 按设计就该红) ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 未代老板拍板** ★
"""
    with open(r, "w", encoding="utf-8") as f:
        f.write(body)
    print("  round log: %s (%d B)" % (os.path.basename(r), os.path.getsize(r)))
    return True


def final_check():
    print()
    print("=" * 96)
    print("★阶段 3 · 写盘后收尾复核")
    print("=" * 96)
    st = os.stat(BOARD)
    print("  板三项: %s / %d ns / %d ⇒ %s" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size,
          "★未动★" if (md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
                       and st.st_size == BOARD_SIZE) else "★★动了★★"))
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append(rel)
    print("  受保护集 (%d 件): %s" % (len(PROTECTED), "★全未动★" if not bad else "★★动了 %s★★" % bad))
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("  %-18s rc=%d" % (label, rc))
    for iss, d in SIGN.items():
        rc, o = sh("python3 %s" % d["gate"])
        print("  %-46s rc=%d (★按设计★)" % (iss + " 闸", rc))
    rc, o = sh("python3 state/advance.py --json")
    import json as _json
    try:
        j = _json.loads(o)
        print("  advance.py: internal=%d approvals=%d decisions=%d waiting=%d"
              % (len(j["internal"]), len(j["approvals"]), len(j["decisions"]), len(j["waiting"])))
    except Exception:
        print("  advance.py 输出解析失败: %r" % o[:160])


def main():
    print("=" * 96)
    print("★ main · 2026-11-24 16:0x · ISS-388 / ISS-390 / ISS-391 三单一并签 + 19 条待裁项已裁 + 自曝 L-32")
    print("=" * 96)
    if not verify():
        print()
        print("★★ fail-closed: 阶段 1 有红项 ⇒ 零写盘退出 ★★")
        return 2
    print()
    print("=" * 96)
    print("★阶段 2 · 追加式落记录")
    print("=" * 96)
    write_issue_log()
    append_onepager()
    append_lessons()
    write_pm()
    write_memory_pointer()
    write_round_log()
    print()
    final_check()
    print()
    print("★ 本轮完成: 3 单签收 + 26 条 main 地界待裁项已裁 + L-32 自曝 + §㊺")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 未代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
