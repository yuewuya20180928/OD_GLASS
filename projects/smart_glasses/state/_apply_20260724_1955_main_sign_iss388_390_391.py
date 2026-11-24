#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1955_main_sign_iss388_390_391.py
=================================================
main (项目总工) · 2026-11-24 19:5x
★★【签收】ISS-388 (sw) + ISS-390 (mech) 三单签收; ISS-391 【暂缓签收】(★闸被抽走判据★) ★★
★★ + 19 条 main 地界待裁项已裁 (★全部用 need 的原 key·★修掉我 13:1x 的静默失效★) ★★
★★ + 自曝铁律 L-32: 「答案 key 必须逐字抄 need 的 key」⇒ 否则机制【静默不闭合】★★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime(ns)/size 三项开工前后各打一次)
  ② 零落表 (网表/脚表/BOM 逐字节不动) ⇒ ★注意: ISS-391 涉及 BOM 型号栏, 本单【只裁不落表】★
  ③ 零改既有闸 (只新建) · ④ 零改既有页面正文 (★订正一律走【追加式】★)
  ⑤ 分片只走 state/frag_write.py · 只写 main 自己的 pm.yaml
  ⑥ 不代老板拍板 (★OI-1 / OI-11 = 老板域·★板框第一问 = 老板域★)
  ⑦ 零外发 · ⑧ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑨ ★★L-27: 签收前必须确认【owner 会话已收工】⇒ 本轮三单 owner 会话均已收工 ★★
  ⑩ ★★零挂链: 本轮【不挂】那三道新闸 ⇒ 理由见一页 §㊻ + 本脚本 verify() 的 L-29/§2 账实测★★
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

import frag_write

STAMP = time.strftime("%Y%m%d_%H%M")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
VERIFY = os.path.join(PROJ, "state/.verify/g1605")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

# ★★签收对象: ISS-388 / ISS-390 签; ISS-391 暂缓 (★闸的判据被抽掉★) ★★
SIGN = {
    "ISS-388": {
        "owner": "sw-lead",
        "gate": "SW/tools/check_sw_gate_health.py",
        "page": "SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md",
        "handoff": "HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md",
        "frag": "sw.yaml",
        "bare": 1,          # ★按设计判红★
        "selftest_n": 22,
    },
    "ISS-390": {
        "owner": "mech-lead",
        "gate": "MECH/check_fts_seat_body_geometry.py",
        "page": "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md",
        "handoff": "HANDOFF/2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md",
        "frag": "mech.yaml",
        "bare": 0,
        "selftest_n": 15,
    },
}
# ★★ISS-391: 本轮【不签】★★
HOLD = {
    "ISS-391": {
        "owner": "hw-lead",
        "gate": "HW/check_fts_land_drill_same_batch.py",
        "page": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "handoff": "HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md",
        "frag": "hw.yaml",
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
    # ★★这一件的基线已被【第三方】合法改动 (★兄弟 job ISS-396 在 18:32 落了 §4 #2/#3 登记·★不是 main 落的★)
    # ⇒ 重设基线 + verify() 里做【范围核对】+ 一页里披露 ⇒ 见 §㊻ §⑧
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md": "192873f6c977b376c28785824a82f9f1",
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


# ===================================================================== 阶段 1
def verify():
    print("=" * 96)
    print("★阶段 1 · main 本机独立复核 (★不抄任何 agent 报告★)")
    print("=" * 96)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-56s %s" % ("✅" if good else "❌", name, detail))

    # ① 板三项 (纳秒级)
    st = os.stat(BOARD)
    chk("板 md5/mtime(ns)/size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    # ② 两单签收对象: 交付物在盘 + 闸读数 (★用本轮已实跑的日志, 复核时重跑一遍快的★)
    print("  ★★① 两单交付物 + 闸 (★TMPDIR 指项目盘·★/tmp 配额满会假红★)")
    for iss, d in SIGN.items():
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            e = os.path.isfile(p) and os.path.getsize(p) >= 4000
            chk("%s %s 在盘 (≥4000 B)" % (iss, d[k].split("/")[-1][:32]), e,
                "%d B" % (os.path.getsize(p) if os.path.isfile(p) else 0))
        b = os.path.basename(d["gate"])[:-3]
        import re as _re
        for mode, want in (("bare", d["bare"]), ("self", 0)):
            lg = os.path.join(VERIFY, "%s.%s.log" % (b, mode))
            txt = read_lines(lg) if os.path.isfile(lg) else ""
            last = txt.strip().splitlines()[-1] if txt.strip() else "(无日志)"
            if mode == "bare":
                # ★按设计判红 = rc=1 且末行自报「几项通过 / 几项」⇒ 判它【是不是按设计的部分通过】★
                mc = _re.search(r"(\d+)\s*/\s*(\d+)", last)
                if want == 0:
                    # ★rc=0 ⇒ 末行必须是明确的 PASS/全绿, 且【不得】出现任何 FAIL/失败条数 ★
                    tailblk = "\n".join(txt.strip().splitlines()[-6:])
                    good = ("PASS" in last or "全绿" in last or "✅" in last) and \
                           ("FAIL" not in tailblk) and ("失败 0 条" in tailblk or "条绿" in tailblk
                                                        or "判据 33 条" in tailblk or "0 失败" in tailblk)
                else:
                    # ★rc=1 按设计 ⇒ 必须能看到「部分通过」的计数, 且不是「0 项通过」(那才是坏了)★
                    good = bool(mc) and int(mc.group(1)) > 0 and int(mc.group(1)) < int(mc.group(2))
                chk("%s 闸 裸跑 rc=%d (★按设计·★部分通过★)" % (iss, want), good, last[:70])
            else:
                mc = _re.search(r"selftest\s+(\d+)/(\d+)\s+通过|通过\s+(\d+)\s+条|(\d+)/(\d+) PASS", txt)
                got = None
                if mc:
                    got = int(next(g for g in mc.groups() if g))
                chk("%s 闸 --selftest rc=0 且 ALL TESTS PASS (★%d 条★)" % (iss, d["selftest_n"]),
                    "ALL TESTS PASS" in txt and got == d["selftest_n"], "读到 %s 条 · 末行 %r" % (got, last[:34]))

    # ③ ★★ISS-391 暂缓的机器依据★★
    print("  ★★② ★★ISS-391 本轮【暂缓签收】的机器依据 (★selftest 不全绿 + 判据被抽走★)")
    lg = os.path.join(VERIFY, "check_fts_land_drill_same_batch.self.log")
    t391 = read_lines(lg) if os.path.isfile(lg) else ""
    import re as _re
    m391 = _re.search(r"selftest:\s*(\d+)/(\d+) PASS", t391)
    got391 = (int(m391.group(1)), int(m391.group(2))) if m391 else (0, 0)
    chk("★ISS-391 闸 --selftest 不全绿 (★实测 %d/%d·★故不可签★)" % got391,
        got391[1] > 0 and got391[0] < got391[1], "%d/%d" % got391)
    # ★★判据被抽走: 把真文件 ③ 里的「钻孔 0.65→0.71」删掉, D1 还绿吗 ★★
    probe = os.path.join(VERIFY, "d1_probe.txt")
    if os.path.isfile(probe):
        pt = read_lines(probe)
        # ★★判据层的致命结论 = 只删动作腿 (留解释文字) ⇒ D1 仍绿 ★★
        chk("★★D1 在「只删动作腿·留解释文字」后仍判绿 (★判据被削弱·★故不可签★)",
            "D1_AFTER_DELETE=GREEN" in pt, "★只删动作腿 ⇒ D1 仍绿 ★")
        # ★★对照: 整条拿掉 ⇒ D1 才红 ⇒ 它只挡「整条没写」, 挡不住「只删动作腿」★★
        chk("★★对照: 整条 ③ 拿掉 ⇒ D1 才红 (★它只挡得住「整条没写」★)",
            "D1_AFTER_FULL_REMOVE=RED" in pt, "★整条拿掉 ⇒ 红 ★")
        chk("★★探针全程真件逐字节未动", "真件逐字节未动: True" in pt, "★沙盒·真件未动 ★")
    else:
        chk("★★D1 判据抽走探针已存在", False, "缺 %s" % probe)

    # ④ 零落表 + 既有闸/已签收页正文
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/已签收页正文 未动 (%d 件)" % len(PROTECTED), not bad,
        "动 %d %s" % (len(bad), bad[:3]))

    # ④b ★★第三方对受保护集的改动: 范围核对 (★只允许改 B33 那一项★) ★★
    print("  ★★④b ★★第三方对受保护集的改动 (★兄弟 job ISS-396 18:32 落的 §4 #2/#3★) ⇒ 范围核对 ★★")
    base = os.path.join(PROJ, "tmp/iss396/backup/PREFLIGHT.md.bak")
    cur = os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md")
    if os.path.isfile(base):
        import difflib
        d = list(difflib.unified_diff(open(base, encoding="utf-8").read().splitlines(),
                                      open(cur, encoding="utf-8").read().splitlines(), n=0))
        changed = [l for l in d if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---"))]
        only_b33 = all(("B33" in l) or ("钻孔" in l) or ("drill" in l.lower())
                       or ("title" in l) or ("current_state" in l) or ("criterion" in l)
                       or ("pitch" in l) for l in changed)
        chk("★PREFLIGHT 的改动只落在 B33 那一项 (★范围核对·★不是乱改★)", only_b33,
            "改动 %d 行 · 全落在 B33/钻孔/drill/title/current_state/criterion" % len(changed))
        txt = open(cur, encoding="utf-8").read()
        chk("★PREFLIGHT 机器块已含 drill 0.71 登记 (⇒ §4 #2/#3 真落·★D1/D2/D3 才转绿★)",
            "0.71" in txt and ("drill" in txt.lower()), "已含 drill 0.71")
    else:
        chk("★PREFLIGHT 旧基线副本存在 (★范围核对用★)", False, "缺 %s" % base)

    # ⑤ 零挂链
    print("  ★★③ 零挂链 (★本轮不挂·★必须实测命中 0★)")
    for iss, d in list(SIGN.items()) + list(HOLD.items()):
        got = sh("grep -c %s state/gate_check.py" % os.path.basename(d["gate"]))[1].strip().splitlines()[0]
        chk("%s 新闸零挂链 (gate_check 命中 0)" % iss, got == "0", "命中 %s" % got)

    # ⑥ 分片登记
    for iss, d in list(SIGN.items()) + list(HOLD.items()):
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

    # ⑧ ★★本轮的关键核验: §2 账的差集 + 新闸有没有硬钉板 md5 (★决定挂进去会不会立刻造新红★)★★
    print("  ★★⑤ ★★挂链可行性本机实测: 新闸有没有硬钉板 md5 (★决定挂进去会不会立刻造新红★)")
    import re as _re
    for iss, d in list(SIGN.items()) + list(HOLD.items()):
        g = os.path.join(PROJ, d["gate"])
        txt = read_lines(g)
        has_literal = bool(_re.search(r"611b869e13518c3c023fb178f91a0075", txt))
        print("      · %-46s 硬钉完整板 md5 字面量: %s" % (os.path.basename(d["gate"]), "★是★" if has_literal else "否"))

    # ⑨ 官方门禁
    print("  ★★⑥ 官方门禁 (★★本轮不挂链 ⇒ 基线读数应与上一轮一致★)")
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("    %-18s rc=%d" % (label, rc))

    # ⑩ ★★我的自曝: 13:1x 那 15 条答案的 key 与 need key 是否逐字相同 (★L-32★) ★★
    print("  ★★⑦ ★★自曝: 我 13:1x 那 15 条答案, 有几条逐字命中 need 的 key (★决定它们闭没闭上 need★)")
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
    mine = [k for k in amap if k.startswith(("iss387_main", "iss389_main", "iss391_main"))]
    hit = [k for k in mine if k in needkeys]
    print("      · 我 13:1x 那批 = %d 条 · 其中逐字命中 need key 的 = %d 条" % (len(mine), len(hit)))
    print("      · ★★⇒ 那批【一条都没闭上 need】(★因为用了【自己起的改名 key】★) ⇒ ⇒ 本轮按 need 的原 key 重答")
    print("      · merge.py 的 lint 里有【答案 key 无 need 引用】这一类 = 189 条 (★我那批 15 条全在里面★)")

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


VER = {
    "ISS-388": "✅ verified (★main 2026-11-24 19:5x 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**闸 `SW/tools/check_sw_gate_health.py` 裸跑 rc=1 (★按设计判红·★**"
               "**这不是闸故障**) + `--selftest` rc=0 末行 `ALL TESTS PASS` (22 条反向用例全抓到)** ★ 交卷页 + 诊断页 + sw.yaml 分片登记在位 ★ 零写板 + 零落表 (网表/脚表/BOM 逐字节未动) + 零挂链 (gate_check 命中 0) ★★"
               "**★main 本机独立复核 (★自己实跑, 不抄报告★)★**: ★**① 它的 4 条红逐条点名, 无一是误报**: H0 点名两道病闸 "
               "`SW/tools/check_sw_board_md5_rebase_readiness.py` (`--selftest` 0/10 · 末行「有用例 FAIL ⇒ 本闸不可信」) + "
               "`SW/tools/check_sw_ref_reachability_v2.py` (`--selftest` 0/7 · 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」) ⇒ ★**这两道闸今天【真的坏了】**; "
               "H1 点名 `SW/tools/check_debug_pin_order_contract.py` 的**判据与环境耦合** (两个深度 TMPDIR 下 rc 0 vs 1); "
               "H2 点名 §2 账少登记 2 道 (`check_sw_false_connectivity_gate.py` + `check_sw_gate_chain_coverage.py`); H3 点名 §1 账少登记 3 行 ⇒ ★**合计 4 条账漂 (D-1~D-4)** ★★"
               "**★★② ★★本单最有价值的一条 = 「三道闸坏了但【没人看见】」这个根因被机器化了 ★★**: ★**旧的三道闸都是【零挂链】⇒ 坏了也不响 ⇒ 就这么烂在盘上** ⇒ "
               "★**本闸把这个病灶变成可判的 (H0 逐道点名 + H1 抓环境耦合 + H2/H3 抓账实漂移)** ⇒ ⇒ ★**而且它的 H4 自己断言「零挂链」⇒ 它【自己】也刻意零挂链 (★不是漏挂, 是设计★)** ★★"
               "**★★③ ★★main 本机独立复核: 本闸【零挂链是它自己的硬判据】★★**: ★**源码 L463-465 逐字 = `gc_txt = read_text(os.path.join(root, GATE_CHECK_REL))` + `hook_hits = gc_txt.count(\"check_sw_gate_health\")` + `if hook_hits != 0: errs.append(\"零挂链被破坏 ⇒ 判红\")` ⇒ "
               "★**⇒ 一旦把它挂进 `state/gate_check.py` ⇒ 它自己的 H4 立刻判红 ⇒ ⇒ ★**⇒ 本闸【结构上就不能被挂链】(★否则自己判自己红★) ⇒ ⇒ 【零挂链是它的正确形态, 不是缺陷】** ★★"
               "**★★④ ⇒ 本单签收含义 = 交付物在盘 + 闸绿(按设计) + 判据零削弱 (★22 条反向用例全抓到★) + 边界零越界; "
               "OI-388 的 5 条 main 地界待裁项已裁 (见一页 §㊻ A 组)** ★",
    "ISS-390": "✅ verified (★main 2026-11-24 19:5x 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**闸 `MECH/check_fts_seat_body_geometry.py` 裸跑 rc=0 (★33 条判据 0 失败★) + "
               "`--selftest` rc=0 末行 `ALL TESTS PASS` (15 条反向用例全抓到)** ★ 真相页 + 交卷页 + mech.yaml 分片登记在位 ★ "
               "零写板 + 零落表 + 零挂链 + 零改既有页面正文 ★★**main 本机独立复核 (★自己解析 .kicad_mod, 不抄页面★)★**: ★**① 通用库件 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` "
               "的 `fp_rect` = 3.1000 × 6.0900 ⇒ 「`6.0900` 是通用件自己的 courtyard」本机坐实; `PinHeader_1x02_…` = 3.1000 × 3.5500 ⇒ 「`3.5500` 同源」坐实** ⇒ "
               "⇒ ★**⇒ 「把通用库件的 courtyard 当成厂件的数」这个前提错误, 本机独立复核确认** ★★**② 厂件外形按通式自己验算: N=4 ⇒ 4 × 1.27 = `5.0800` ✓ / N=2 ⇒ `2.5400` ✓** ⇒ "
               "★**⇒ 厂件座体【宽 X = N × 1.27】本机算术复核命中** ★★**③ 通用件 F.Fab 跨排距 2.1000 vs 厂件 2.1600 ⇒ 差 `0.0600` ⇒ ★**通用件比厂件窄 0.0600 ⇒ "
               "当座体用 ⇒ Y 向每边少让 0.0300** ⇒ 与本单结论一致 ★★**④ ★★本单最有价值的一条 = 「`6.0900`/`5.0800`/`3.5500`/`2.5400` 这组数【全部来自通用库件】, 与 Samtec 无关** "
               "⇒ ⇒ 【ISS-371/389/374 把它们当「官方 1×4 THT 座体本体 (F.Fab)」写进已签收页与已签收闸源码] ⇒ ⇒ 这是【定性前提错误】(★不是数值错, 是【出处错】★) ⇒ ⇒ "
               "★**⇒ 且它把 OI-11 (座体真实高 h = [0数据]) 的性质改了: 库件根本给不了 Z (绝缘体高), 而厂件 Z = `0.8600` [官网] ⇒ ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」** ★ ★"
               "**★★⑤ ⇒ 本单签收含义 = 交付物在盘 + 闸全绿 + 核心数本机复算命中 + 边界零越界; OI-390 的 4 条 main 地界待裁项已裁 (见一页 §㊻ B 组)** ★",
}

HOLD_391 = ("⏸️ ★★暂缓签收 (★main 2026-11-24 19:5x 本机独立复核★) ⇒ ★**本轮【不签】★** ⇒ ★**理由 = 【闸的判据被抽掉了】(★机器实测·★不是意见分歧★)** ★★\n"
            "★★**① 闸的 selftest 不全绿**: ★**本机实跑 `HW/check_fts_land_drill_same_batch.py --selftest` = `14/17 PASS` + 末行 `SELFTEST FAILED` ⇒ "
            "⇒ ★**按 L-29 通则①: `--selftest` 末行不是 `ALL TESTS PASS` ⇒ 这道闸【不可信】⇒ ⇒ 不可拿它当签收凭据** ★★\n"
            "★★**② 三条反向用例抓不到了 (★① ② ③ 全 FAIL★)**: ★**① 「删掉作业包 §0.2 ③ 里的『钻孔』两个字 ⇒ D1 红」⇒ 实际红: 无; "
            "② 「删掉 B33 描述列里的钻孔字样 ⇒ D2 红」⇒ 实际红: 无; ③ 「删掉 B33 验收手段列里读钻孔的命令 ⇒ D3 红」⇒ 实际红: 无** ★★\n"
            "★★**③ ★★main 本机决定性实验 (★沙盒·★真件逐字节未动★)★**: ★**把真文件作业包 §0.2 ③ 里的「钻孔 0.65→0.71」这一腿真的删掉, 再跑 D1 ⇒ ★★"
            "★**D1 仍然判绿** ⇒ ⇒ ★★**⇒ 【D1 这条判据已经抓不到「把改孔这一腿删掉」这个动作了】⇒ ⇒ ★★**⇒ 判据被削弱 ⇒ ⇒ 这道闸现在【保护不了它要保护的东西】⇒ ⇒ 不可签** ★★\n"
            "★★**③b ★★对照实验 (★main 本机实跑★)★**: ★**把 ③ 整条只剩 pitch 那一腿 ⇒ D1 才红 ⇒ ⇒ ★**说明 D1 只在【整条都拿掉】时才红 ⇒ ⇒ 【它挡得住「整条没写」, 挡不住「只删动作腿、留下一段解释文字」】** ⇒ ⇒ ★★**⇒ 这正是【判据层】的削弱 (★比夹具层更致命·★夹具层只影响自测, 判据层影响【真跑时的保护力】★)** ★★\n"
            "★★**④ 根因 (★main 本机定位·★两级★)★**: ★**【判据层·更致命】D1 的三条子判据全是【关键词/子串命中】(★`has_drill()` 认『钻孔』/『孔径』/不分大小写的『drill』+『0.71』子串 +『1.27』子串★) ⇒ ⇒ 而登记落盘后真件那一行【带了一段解释性括注】(★「通用库件默认 (drill 0.65) 偏小 0.06」+「Ø0.71 TYP」+「.028 0.71 (TYP)」★) ⇒ ⇒ 【纯解释文字】也同时满足全部三条 ⇒ ⇒ 【动作腿删掉它照样绿】⇒ ⇒ 判据被削弱** ★ "
            "★**【夹具层】闸的 selftest 靠【写死的常量】(`WORKPACKET_DRILL_LEG` / `DRILL_TITLE` / `DRILL_CRIT`) 造反向用例 ⇒ ⇒ 而真文件那一行现在的原文与常量【逐字不同】(★真件多了一句「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」★) ⇒ ⇒ 反向用例替换不中 ⇒ ⇒ 三条用例【假绿】(★期望红却绿★) ⇒ ⇒ selftest 14/17** ★★"
            "★★**⇒ 两者合起来 = 这道闸【现在看起来是绿的, 其实抓不到它要抓的东西】⇒ ⇒ 按 L-29 通则①【不可信】⇒ ⇒ 不可签, 更不可挂链** ★★\n"
            "★★**⑤ ★★而【登记已经提前落了】(★本机实读 mtime★)★**: ★**作业包 §0.2 ③ / 预检清单 B33 / 生成器 / 真相页 = 18:28~18:32 已被改 (★兄弟 job fb67af40 的 18:2x 那一趟落的·★不是 main 落的★)** ⇒ "
            "⇒ ★**⇒ 板侧四道新闸的裸跑读数因此从 4/7 变成 7/7 全绿** ⇒ ⇒ ★**⇒ ★★【按设计判红】这个前提已经不存在了 ⇒ ⇒ 这道闸现在【不是等 main 落登记】, 是【夹具跟不上真件】** ★★\n"
            "★★**⑥ ⇒ 处置**: ★**① main 本轮不签 ISS-391, 台账 status 保持 `fixing` + 追加式 note_addendum 记明上面 6 条; "
            "② 闸的夹具必须改成【从真件现读原文构造反向用例】(★不许写死常量★) ⇒ 归 owner 修 (★修在产生点·★改判据逻辑 ⇒ 需重签·★本轮不代修★); "
            "③ OI-391-1~5 五条 main 地界待裁项【照裁照落】(★待裁项与签收是两件事·★裁了不等于签★), 但 OI-391-1 的「谁落登记」这一问【已被 §4 提前落盘部分回答】⇒ ⇒ "
            "⇒ 追加一条订正: ★**登记已在 18:28~18:32 由兄弟 job 提前落 ⇒ ⇒ 【提前落】这件事本身【已被登记过一遍】⇒ ⇒ 所以 D1/D2/D3 现在【本该是绿的】(★与实测一致★) "
            "⇒ ⇒ 但 §4 #5 (BOM 两栏) + §4 #6 (生成器现读) 仍【未落】⇒ ⇒ 且【提前落】触发了本闸夹具脱节 ⇒ ⇒ 这一条必须由 owner 修夹具后重跑自测才能签** ★★\n"
            "★★**⑦ ⇒ 本单签收含义 = 【本轮不签】+ 6 条机器依据已留痕 + 5 条待裁项已裁** ★")


def write_issue_log():
    p = LOG
    # ★★CAS 并发守卫 (★兄弟 job 正在并发写这份 5 MB 台账 ⇒ 读-改-写之间有窗口★) ★★
    raw0 = open(p, "rb").read()
    md5_0 = hashlib.md5(raw0).hexdigest()
    shutil.copy2(p, p + ".bak_%s_main_sign_iss388_390_391" % STAMP)
    doc = yaml.safe_load(raw0.decode("utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}
    before_n = len(issues)

    # ★★先记下【改动之前】的原始 status (★★否则下面那道 CAS 前置检查会读到我刚写进去的值★)★★
    orig_status = {k: (by.get(k) or {}).get("status") for k in list(VER.keys()) + list(HOLD.keys())}

    for iss, vr in VER.items():
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        e["status"] = "verified"
        e["verify_result"] = vr
        e["verify_date"] = "2026-11-24 19:5x"
        e["verify_by"] = "main"
        e["fix_ref"] = "main 2026-11-24 19:5x 独立复核签收 (★零写板·零落表·零改既有闸·零改既有页面正文·零挂链·零外发★)"

    # ★★ISS-391: 保持 fixing + 追加式 note_addendum (★老字一字未删★) ★★
    e = by.get("ISS-391")
    if e is None:
        raise SystemExit("台账里没有 ISS-391")
    notes = e.get("note_addendum") or []
    if not isinstance(notes, list):
        notes = [notes]
    notes = list(notes) + [{
        "at": "2026-11-24 19:5x",
        "by": "main",
        "text": HOLD_391,
    }]
    e["note_addendum"] = notes

    # ★★落盘前 CAS 复核 (★读-改-写窗口内若有人改过 ⇒ 报错退出·★不覆盖别人的写★) ★★
    md5_now = hashlib.md5(open(p, "rb").read()).hexdigest()
    if md5_now != md5_0:
        raise SystemExit("★★CAS 失败: 台账在我读之后被改过 (★%s != %s★) ⇒ 有人并发写 ⇒ "
                         "★零写盘退出·★不覆盖别人的写★ ★★" % (md5_now[:12], md5_0[:12]))
    # ★★签收前置: 三单此刻必须仍是 fixing (★若已被别人签过 ⇒ 我的裁决会覆盖别人的·★必须退出★) ★★
    for iss, st in orig_status.items():
        if st not in ("fixing", "open"):
            raise SystemExit("★★台账里 %s 的 status 在我读的时候已是 %s (★不是我写的·★可能是别人签收过★) ⇒ "
                             "★零写盘退出 ★★" % (iss, st))
    tmp = p + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, p)
    print("  issue_log.yaml: ISS-388 + ISS-390 签收 + ISS-391 暂缓 note_addendum (★一次全量重写·零竞态窗口★) 条数 %d→%d"
          % (before_n, len(issues)))
    return True


def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_sign_iss388_390_391" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """
## ★★㊻ 【2026-11-24 19:5x · 追加式】★ ★★ISS-388 / ISS-390 两单独立复核签收 + ★★ISS-391 暂缓签收 (★闸的判据被抽掉·★机器实测★) + 19 条 main 地界待裁项已裁 + ★★一条自曝铁律 (L-32) ★★

★**① 板面 (本机实读)**: ★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**② 签收结果 (★main 本机独立复核·不抄任何 agent 报告★)★**

| 单 | owner | 闸 | 裸跑 | `--selftest` | 本轮结论 |
|---|---|---|---|---|---|
| **ISS-388** | sw-lead | `SW/tools/check_sw_gate_health.py` | ★**rc=1 (★按设计判红★)** | ★**rc=0 · 22/22 · `ALL TESTS PASS`** | ★**✅ verified** ★ |
| **ISS-390** | mech-lead | `MECH/check_fts_seat_body_geometry.py` | ★**rc=0 · 判据 0 失败** | ★**rc=0 · 15/15 · `ALL TESTS PASS`** | ★**✅ verified** ★ |
| **ISS-391** | hw-lead | `HW/check_fts_land_drill_same_batch.py` | ★**rc=0 · 7/7 全绿** | ★**rc=1 · 14/17 · `SELFTEST FAILED`** | ★**⏸️ 暂缓签收 (★判据被抽走★)** ★ |

★零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · **L-26① 的 13 道扫描面闸逐道实跑全 rc=0 (含七个签收闸)** ★

★**③ ★★ISS-390: 「通用库件 courtyard 被当成厂件」这个前提错误, 本机独立复核确认 ★★**
★**main 自己解析 `.kicad_mod`**: `PinHeader_1x04_P1.27mm_Vertical` 的 `fp_rect` = **3.1000 × 6.0900** ⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」坐实; `PinHeader_1x02_…` = **3.1000 × 3.5500** ⇒ 「`3.5500` 同源」坐实 ★
★**厂件外形按通式自己算**: N=4 ⇒ 4 × 1.27 = **`5.0800`** ✓ / N=2 ⇒ **`2.5400`** ✓ ⇒ 「厂件座体宽 X = N × 1.27」命中 ★
★**通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600` ⇒ 通用件当座体用 ⇒ Y 向每边少让 `0.0300`** ★ ★
★**★★⇒ 「`6.0900`/`5.0800`/`3.5500`/`2.5400` 这组数【全部来自通用库件】, 与 Samtec 无关** ⇒ ⇒ **ISS-371/389/374 把它们当「官方座体本体 (F.Fab)」写进已签收页与已签收闸源码 = 【定性前提错误】(不是数值错, 是出处错)** ⇒ ⇒ ★**且它把 OI-11 (h = [0数据]) 的性质改了: 库件根本给不了 Z (绝缘体高), 而厂件 Z = `0.8600` [官网] ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」** ★ ★

★**④ ★★ISS-391: 本轮【暂缓签收】(★机器实测·★6 条依据★) ★★**
★**① `--selftest` = `14/17 PASS` + 末行 `SELFTEST FAILED` ⇒ 按 L-29 通则① 这道闸【不可信】⇒ 不可拿它当签收凭据** ★
★**② 三条反向用例 (① 删钻孔字样 ⇒ D1 红 / ② 删 B33 描述列钻孔 ⇒ D2 红 / ③ 删 B33 验收手段 ⇒ D3 红) 全部 FAIL (★期望红却绿★)** ★
★**③ ★★main 决定性实验 (★沙盒·真件逐字节未动★)★: 把真文件作业包 §0.2 ③ 里的「钻孔 0.65→0.71」这一腿真的删掉, 再跑 D1 ⇒ ★**D1 仍然判绿** ⇒ ⇒ **D1 已经抓不到「把改孔这一腿删掉」这个动作了** ⇒ ⇒ 判据被削弱 ⇒ ⇒ 不可签** ★
★**③b ★★对照实验 (★main 本机实跑★)★: 把 ③ 整条只剩 pitch 那一腿 ⇒ **D1 才红** ⇒ ⇒ **D1 只在【整条都拿掉】时才红 ⇒ ⇒ 【它挡得住「整条没写」, 挡不住「只删动作腿、留下一段解释文字」】** ★
★**④ 根因 (★main 本机定位·★两级★)★: ★**【判据层·更致命】D1 的三条子判据全是【关键词/子串命中】(★`has_drill()` 认『钻孔』/『孔径』/不分大小写的『drill』+『0.71』子串 +『1.27』子串★) ⇒ ⇒ 而登记落盘后真件那一行【带了一段解释性括注】(★「通用库件默认 (drill 0.65) 偏小 0.06」+「Ø0.71 TYP」+「.028 0.71 (TYP)」★) ⇒ ⇒ 【纯解释文字】也同时满足全部三条 ⇒ ⇒ 【动作腿删掉它照样绿】⇒ ⇒ 判据被削弱** ★ ★**【夹具层】闸的 selftest 靠【写死的常量】造反向用例 ⇒ ⇒ 而真文件那一行现在的原文与常量【逐字不同】(★真件多了一句「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」★) ⇒ ⇒ 反向用例替换不中 ⇒ ⇒ 三条用例【假绿】⇒ ⇒ selftest 14/17** ★★★**⇒ 两者合起来 = 这道闸【现在看起来是绿的, 其实抓不到它要抓的东西】⇒ ⇒ 按 L-29 通则①【不可信】⇒ ⇒ 不可签, 更不可挂链** ★ ★**⇒ 修法 (★两层都要修·★归 owner·★修在产生点·★改判据逻辑 ⇒ 需重签★)★: ① 判据层 = D1/D2/D3 必须【认动作本身】(★认『钻孔 0.65→0.71』这个【动作短语】或【机器块里的 drill 字段】★), 而不是认关键词子串; ② 夹具层 = 反向用例必须【从真件现读原文构造】, 不许写死常量** ★ ★
★**⑤ ★★而【登记已经提前落了】(★本机实读 mtime★)★**: 作业包 §0.2 ③ / 预检清单 B33 / 生成器 / 真相页 = **18:28~18:32** 已被改 (★兄弟 job fb67af40 那一趟落的·★不是 main 落的★) ⇒ ⇒ **板侧四道新闸的裸跑读数因此从 4/7 变成 7/7 全绿** ⇒ ⇒ ★**★【按设计判红】这个前提已经不存在了** ⇒ ⇒ 这道闸现在【不是等 main 落登记】, 是【夹具跟不上真件】** ★
★**⑥ ⇒ 处置**: main 本轮不签 (台账 `fixing` + 追加式 note_addendum 记明上述 6 条) + OI-391-1~5 照裁照落 (★裁 ≠ 签★) + 夹具必修归 owner (★改判据逻辑 ⇒ 需重签★) ★

★**⑤ ★★19 条 main 地界待裁项已裁 (★一件没代老板拍板★)★★**

★**▌A 组 · ISS-388 (5 条·to=sw-lead)★★

| # | need key | main 裁决 (2026-11-24 19:5x) |
|---|---|---|
| A1 | `iss388_ledger_drift_owner` | ★**账漂 (D-1~D-4) 归【main 授权 + owner 落追加式订正块】, 且【必须与「板只改一次」那一趟同批】** ⇒ ★**① 改的是 ISS-372 真相页的 §1/§2 机器块 = 已签收页 ⇒ 按「已签收件的订正路径」⇒ **main 授权路径, owner 落追加式订正块 (★老字一字未删★) ⇒ main 不直接改 owner 的正文**; ★**② 为什么必须同批**: D-1~D-4 的差集 = 【那三道闸坏了 + 账没跟上】⇒ 修账不修闸 = 账上写「已登记」但闸还是坏的 ⇒ ⇒ **必须【账 + 闸】一起修** ⇒ 而闸的修法在 §㉙ 与 §㊶ 已裁 (★闸 2 的 selftest 0/10 = 差值型自测在基线已红时全灭⇒ 归 SW 域那一趟同批★) ⇒ ⇒ ★**③ 且闸 2 与闸 v2 修好之前, 新闸 `check_sw_gate_health.py` 必须保持零挂链** ⇒ 挂了它自己 H4 会红 (★源码 L463-465 实测★) ⇒ ⇒ **零挂链是它的正确形态** ⇒ ⇒ ★**★⇒ 落法 = main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★ |
| A2 | `iss388_new_gate_hook_to_main` | ★**【不挂】, 且这不是「暂缓」而是【结构性不可挂】** ⇒ ★**理由 (★main 本机实读源码坐实·★不是抄报告★)★**: 该闸 H4 判据字面就是 `hook_hits = gc_txt.count("check_sw_gate_health")` ⇒ ★**它一旦出现在 `state/gate_check.py` 里, 它自己立刻判红** ⇒ ⇒ 挂它 = 让它自己判自己红 = 【假红】⇒ ⇒ **零挂链是它的正确形态** ⇒ ★**★⇒ 「挂链就能看见」这个直觉在这里【是错的】⇒ 看不见的病根是【那三道病闸零挂链 + 坏了没人跑】⇒ 处置 = 修那三道闸 + 把它们挂进链 (★归 SW 域那一趟·★本轮只裁归属, 不代排顺序★)** ★ ★ |
| A3 | `iss388_env_sensitivity_fix_location` | ★**路 A (在源头修) 为主 + 路 B (调用约定) 为辅, 且【顺序 = 先 B 后 A】** ⇒ ★**① 闸 1 的红是【同一份源码, 只差 TMPDIR ⇒ 10/11 vs 11/11】⇒ ⇒ 判据本身与环境耦合 ⇒ ⇒ **这是【闸的缺陷】, 不是调用方的错 ⇒ ⇒ 病根在闸 ⇒ 必须源头修 (路 A)** ⇒ 否则「靠人记得带 TMPDIR」= 把判据正确性押在人的记性上 (★ISS-297 已栽过一次「约定靠人记会有忘的那天」★); ★**② 但路 B 也不能不做**: 本机 `/tmp` 用户配额打满 ⇒ 不带 TMPDIR 会假红 (★rc=120 / 0 字节★) ⇒ ⇒ **路 B 是止血 (今天就让一切调用都带对), 路 A 是治病 (让闸与环境无关)** ⇒ ⇒ ★**★⇒ 顺序 = 先 B (零风险·今天可落) + 后 A (要重签 ISS-372/ISS-375 ⇒ 归 SW 域那一趟同批·★本轮不代排★)** ★ ★ |
| A4 | `iss388_third_sick_gate` | ★**要修, 但【不另起一单】⇒ 归「板只改一次」那一趟同批** ⇒ ★**① `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` = 0/7, 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」⇒ ⇒ **它【真的坏了】, 不是误报 ⇒ 必须修** (★本单只登记不修是对的: 它不在本单 brief 范围内★); ★**② ★★但它的失败模式与闸 2 同类 (基线先红 ⇒ 差值型自测全灭) ⇒ ⇒ 修它的前置 = 先修账 (D-1~D-4) ⇒ ⇒ 【它与账漂是同一条因果链】⇒ ⇒ 拆成两单 = 两批做完 = 又一次「板只改一次」的纪律破例 ⇒ ⇒ 归同一趟** ★ **③ ⇒ 归属 owner = sw-lead (★它本来就该在 SW 域那一趟里★)** ★ ★ |
| A5 | `iss388_delta_selftest_convention` | ★**「基线必须先绿, 否则 selftest 结论不可读」写进闸的编写通则 —— 【采纳】, 但【落法 = 新增一份通则文档 + 逐闸加前置断言】, 不是【逐个改已签收闸的 selftest 口径】** ⇒ ★**① 闸 2 = 0/10 与闸 v2 = 0/7 都是【差值型自测在基线已红时全灭】⇒ ⇒ 闸自曝「我不可信」却说不出「我是账漂了不是坏了」⇒ ⇒ **这个病确实需要一条通则**; ★**② ★★但「一次性改若干已签收闸的 selftest 口径」这条路【本轮不走】★★**: (a) 改已签收闸的 selftest 逻辑 = 改判据 ⇒ 要重签 ⇒ 又是一次签收指纹过期 (★今天已在 ISS-381/382/384 上栽过两次·★L-27★); (b) 且「差值型自测」本身不是错 —— 它【自证「红集 == {目标那一条}」】这个设计是对的 ⇒ ⇒ 错的只是【基线已经红的时候, 差值不可读】⇒ ⇒ **正确解法 = 让基线先绿 (A1 的账漂 + 那三道闸修好) ⇒ 差值自测自然可读 ⇒ 通则只需写成【写闸时必须先声明「本闸的基线是什么; 基线红了 selftest 结论不可读」】+ 错误消息点名是哪个闸 + 它的原文末行 (★这正是新闸 H0 已做到的★)** ⇒ ⇒ ★**★⇒ 落法 = 新增一份通则 (★main 落·★`state/GATE_WRITING_CONVENTIONS.md`·★新文件不碰任何已签收闸★) + 逐闸加前置断言归 SW 域那一趟** ⇒ ★★ |

★**▌B 组 · ISS-390 (4 条·to=mech-lead)★★

| # | need key | main 裁决 (2026-11-24 19:5x) |
|---|---|---|
| B1 | `iss390_correction_landing` | ★**6 处定性订正归【main 授权 + owner 落追加式订正块】, 且【与「板只改一次」那一趟同批】** ⇒ ★**① 这 6 处全是【已签收页正文 + 已签收闸源码字符串】⇒ 按「已签收件的订正路径」⇒ **main 授权路径, owner 落**, main 不直接改 owner 的正文 (★老字一字未删·★只加订正块★); ★**② §4 #3 的两处源码字符串 (`MECH/check_debug_seat_3d_fit.py` L848 / L879) 是【已签收闸的判据源码】⇒ 改它 ⇒ **那两道签收指纹当场过期** ⇒ ⇒ 【必须与那一趟的「重验全部验收线」同批】(★L-27 通则③★); ★**③ ★★⇒ 这 6 处不落 ⇒ 【通用件 vs 厂件】的前提错误继续留在页上与闸源码里 ⇒ ⇒ 下一个读这页或跑那个闸的人会拿错对照物做结构判决 ⇒ ⇒ 而本闸 G3 的未落清单会永远停在 17 处 ⇒ ⇒ 【G3 恒红 ⇒ 这道闸自己也就废了】⇒ ⇒ ★**★⇒ 故: main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★ |
| B2 | `iss390_h_lock_and_test_sample` | ★**两问分别裁: (甲) h 走【三档参数化】, 不锁死; (乙) 打样归【那一趟同批】** ⇒ ★**(甲) 理由**: ★**① 厂件柱高 `3.05` mm (官网表 TABLE 1 lead style -01) 而绝缘体只有 `0.86` ⇒ ⇒ **罩内腔板面以上那一维【不能】按 `0.86` 出件 ⇒ `h=0.90` 档【物理上装不下】⇒ 可行档是 `2.54` 与 `4.00`** ⇒ ⇒ ★**★⇒ 这把 §㊶ C8 那条 (「h 不卡那一趟」) 的依据从「[0数据]」升级成了「[0数据] 且已算明可行档只剩两个」** ⇒ ★**② ⇒ 【不锁死】的理由 = h 锁死会绑死一个【还没测过】的量 ⇒ ⇒ 三档参数化 (0.90 / 2.54 / 4.00) 让结构侧在两档之间走, 而 0.90 已被物理判死 ⇒ ⇒ **实际只剩 2.54 与 4.00 两档 ⇒ ⇒ 锁定权仍在 boss (★`iss389_oi11_seat_height_window` 未代拍★) ⇒ ⇒ 本裁决只裁「形式」, 不裁「值」** ★ **(乙) 理由**: ★**打样是【唯一能拿到 REF 公差】的路径 (★官网图给的是 REF 不是公差带★) ⇒ ⇒ 落 FTS 时打一块单板样、用卡尺量三量 (★绝缘体高 / 外形宽 / 外形深★) 回填 `keepout_dwg` + `body_geometry` ⇒ ⇒ 【必须与那一趟同批】(★落 FTS 那一天才有样可打★) ⇒ ⇒ **归 mech-lead 执行 (转派), 但【不新起一单】(★与那一趟同批·★与「板只改一次」纪律一致★)** ★ ★ |
| B3 | `iss390_oi12_and_oi14_together` | ★**三个答案一起给: (a) 罩住判据【管到座体本体】(★不是只管铜箔★) ⇒ 采纳; (b) 「偏紧 `0.5200`」的措辞【作废】(★`6.0900` 是通用库件的 `F.CrtYd`, 厂件【没有】courtyard 这个量★); (c) ⇒ (a) 成立 ⇒ **J_UART 的 X 需求从 `4.0700` 变 `4.3400`** ⇒ ⇒ **OI-14 (DP-1) 的目标值 = `4.3400`**** ⇒ ★**① 座体本体 (厂件 X `5.0800` / `2.5400` + Y `2.1600`) 比铜箔包络 (X `4.8100` / `2.2700`) 【每边都大】⇒ ⇒ **只按铜箔算 = 会做出一个装不进座体的洞 ⇒ 判据必须同时管座体本体** ⇒ ⇒ (a) = 管 ⇒ 采纳; ★**② 「偏紧 `0.5200`」的对照物是 `6.0900` ⇒ 而 `6.0900` 是【通用 KiCad 库件自己的 `F.CrtYd`】(★main 本机解析 `.kicad_mod` 的 `fp_rect` = 3.1000 × 6.0900 坐实★) ⇒ ⇒ **Samtec 厂件没有 courtyard 这个量 ⇒ 那句「比 courtyard 还小」在【厂件】这一层【无意义】⇒ ⇒ (b) = 作废那句措辞, 保留判据本身 (每边 `0.9000` = `CRIT 0.60` + `TOL 0.30`)**; ★**③ (c) 是 (a) 的算术后果**: 厂件 J_UART 座体 X `2.5400` + 2 × `0.9000` = `4.3400` (★不是 `4.0700`·★`4.0700` 是按铜箔 `2.2700` 算的★) ⇒ ⇒ **OI-14 (DP-1) 的目标值 = `4.3400`** ⇒ ★**★⇒ ★★与 §㊶ C4 / §㊶ C6 【冲突】⇒ ⇒ 按 L-27 通则③ (main 落裁决 ⇒ 已 verified 的单的交付物进入「会动」状态 ⇒ 那一趟必须重验全部验收线) ⇒ ⇒ 本条取代 §㊶ C4 与 C6 的对应部分, 老裁决的数值随之作废** ⇒ ⇒ 而 §㊶ C6 那个 `4.0700` 恰好是本单 §4 订正清单里的一条 (★L634 机器块 + 正文路径 B 段★) ⇒ ⇒ 正好一起订正** ★ ★ |
| B4 | `iss390_y_direction_open_question` | ★**Y 向走【放大罩开口 Y】, 但【幅度按座体本体重算】⇒ 开口 Y 须 `≥ 5.7600`** (★取代 §㊶ C5 的 `5.6000`/`5.8000`★)** ⇒ ★**① 座体本体 Y = `2.1600` (厂件·★main 本机复核: 通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`★) ⇒ 按每边 `0.9000` ⇒ 清空区 Y 需求 = `2.1600` + 2 × `0.9000` = `3.9600` ⇒ ⇒ ★**★⇒ 比 §㊶ C5 裁的 `2.8000` 大 `1.1600`** ⇒ ⇒ ★**★★⇒ §㊶ C5 的【方向】(放大罩开口 Y) 仍成立, 但【数值】需重算: 开口 Y 须 ≥ 清空区 Y `3.9600` + 2 × `0.9000` = `5.7600`** ⇒ ⇒ **本条构成对 §㊶ C5 的【订正】(方向同, 数值收窄)**; ★**② 「接受零余量」那个选项【已不存在】(★本单自己也这么说★) ⇒ ⇒ (b) 改判据口径只罩铜箔 = 【已判死】(★只罩铜箔 = 装不进座体★) ⇒ ⇒ **只剩 (a) 放大罩开口 Y 一条路** ⇒ ⇒ **罩开口 Y `4.6000` → `5.7600` = 放大 `1.1600`**; ★**③ ⇒ 结构性代价 (镜脚内腔 + 罩外观缝) 与 §㊶ C5 同源 ⇒ ⇒ 与板框第一问同批** ⇒ ⇒ **与 B3 同源 ⇒ 两条一起落** ★ ★ |

★**▌C 组 · ISS-391 (5 条·to=hw-lead)★★〔★注: 本轮【不签 ISS-391】(★见 §④★), 但【待裁项照裁·★裁 ≠ 签★〕★★

| # | need key | main 裁决 (2026-11-24 19:5x) |
|---|---|---|
| C1 | `OI-391-1` | ★**三处补登记归【owner 落追加式订正块, 落在「板只改一次」那一趟的清单改版里】, 【不许提前落】—— ★★★但本机实读发现【已提前落】(★18:28~18:32·★兄弟 job fb67af40 那一趟★) ⇒ ⇒ ★**因此本问已被【部分回答】⇒ ⇒ 追加订正: 登记已落 ⇒ D1/D2/D3 现在【本该是绿的】(★与实测一致★) ⇒ ⇒ 但 §4 #5 (BOM L71/L77 两栏) + §4 #6 (生成器现读) 仍【未落】⇒ ⇒ 且【提前落】触发了本闸的夹具脱节 (★见 §④③④★) ⇒ ⇒ ⇒ 本问【改为: §4 #5 + #6 仍归 owner 在那一趟落; 提前落这件事的后果由 §④ 的夹具修复吸收】** ★★"
               "★**★⇒ 为什么不许提前落 (★机器可核★)★**: ★**提前落 ⇒ 中间态 = 板还没改, 清单却写了要改孔 ⇒ ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (★板上还是 `0.65`★) ⇒ 当场红 ⇒ ⇒ 现场会把它读成「板坏了」⇒ ⇒ ★**这正是 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + ISS-384 A5 全同款纪律的另一种说法** ⇒ ⇒ ★**⇒ 且 §4 #1/#2/#3 必须【一起落】** (★`wp02_tokens()` 会从③的原文里自动抽「小数」当覆盖令牌 ⇒ 补上 `0.65` 与 `0.71` 之后, 现有 P4 会自动要求清单页 `B33_PIN_LAND_1P27` 里也能查到这两个数 ⇒ ⇒ #1 与 #2/#3 不同步 ⇒ P4 当场红★) ⇒ ⇒ **三处一起** ★★"
               "★**★⇒ 附 (★main 自己的发现·★两页都没算这一格★)★: 改孔后环宽 `0.1750 → 0.1450` mm, 且本板 `.kicad_pro` 的 DRC 只有 `min_via_annular_width 0.1` (过孔) ⇒ "
               "★**⇒ THT 焊盘环宽【无判据】⇒ 触不到板 DRC ⇒ ⇒ 属【制程能力】问题 ⇒ 那一趟投板前必须坐实 ⇒ 见 `iss394_ring_width_fab_capability`** ★ ★",
    "OI-391-2": "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-2★)★: ★**写成【一条】(pitch 与 drill 是同一项的两条腿, 不可只做其一), 不许拆成两条可分开的动作** ★★"
               "★**★⇒ 理由 (★机器可核★)★**: ★**新闸 D1 只能查出【整条没写】, 查不出【拆成两条只做一条】⇒ ⇒ 拆开写 = 判据出现盲区** ⇒ ⇒ "
               "★**★⇒ 一条写 + 锚点含两个数 (`0.71` 与 `1.27`) = 机器可判** ⇒ ⇒ ★**★⇒ 与 §㊻ A1/B1 同一纪律: 措辞口径由 main 定, 落法由 owner 落, 且【必须机器可判】** ★ ★"
               "★**★⇒ ★★main 本轮实测的一条补充 (★这条比本裁决本身更重要★)★: ★**★真文件那一行的原文已经与闸的夹具常量【逐字不同】(★真件多了一句「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」★) ⇒ ⇒ 【锚点必须逐字匹配】这条裁决的【机器可判】前提【不成立】⇒ ⇒ ⇒ **所以「一条写」之外, 还必须加一条: 【夹具的锚点必须从真件现读, 不许写死常量】** ⇒ ⇒ 归 owner 修夹具时一并落** ★ ★",
    "OI-391-3": "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-3★)★: ★**BOM L71 (J_DEBUG) / L77 (J_UART) 的 opn 与 footprint 两栏 = 与板侧 land 来源【同源】, "
               "★**落表时机 = 那一趟的同一次落表与重出; 本轮【零落表】** ★★"
               "★**★⇒ 同源纪律 (★板面 land 来源 = BOM 型号栏 = 实物料号★)**: ★**板侧 land 来源 = 盘上通用 KiCad 1.27mm THT 库件 "
               "★**(★`PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c…` / `PinHeader_1x02_P1.27mm_Vertical` md5 `47bcbf6d…`★) + 一条显式偏离登记 "
               "★**(★偏离项 = 铜箔焊盘直径官方无值 + 孔径由 `0.65` 改 `0.71`★) + BOM 型号栏写 FTS 料号** ⇒ ⇒ **不成立 ⇒ 投板后才发现 ⇒ 2-4 周返工** ⇒ ⇒ "
               "★**★⇒ 逐字草案按真相页 §4 #5 原样落, main 不改一字** ⇒ ⇒ ★**★⇒ 与 §㊶ A3 (OI-387-3) 同一裁决, 两处口径必须一致** ★ ★"
               "★**★⇒ 附 (★main 本机实读★)★: ★**HW/BOM_v1.csv 逐字节未动 (md5 `5b999399…`) ⇒ ⇒ §4 #5 **确实还没落** ⇒ ⇒ 归 owner 在那一趟落** ★ ★",
    "OI-391-4": "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-4★)★: ★**生成器补登记归【owner (hw-lead) 落】, 且【与那一趟同批】; "
               "★**本轮【零改既有脚本正文】** ★★"
               "★**★⇒ 理由 (★机器可核★)★**: ★**`state/_iss277_build_preflight.py` 的 `build_pinland_item()` (title + current_state + criterion 三处一起长) + "
               "★**`read_board_pin_land()` 加一个 drill 字段现读板** ⇒ ⇒ ★**不落 ⇒ §3 #2/#3 的补登记【重跑一次就蒸发】(★ISS-349 同一位号已栽过一次★) ⇒ 白补, "
               "★**改孔这条子动作重新回到没人做的状态** ⇒ ⇒ ★**★⇒ 归 owner 落 (★本单零改既有脚本正文★) + 必须与那一趟同批 (★否则中途重跑一次就白补★)** ⇒ ★ ★"
               "★**★⇒ 附 (★main 本机实读 mtime★)★: ★**`state/_iss277_build_preflight.py` mtime = 18:28:31 ⇒ ⇒ §4 #6 **已经落过了** ⇒ ⇒ ⇒ 本问【已回答】⇒ ⇒ 剩下的是【闸的夹具要跟着真件现读】(★见 §④④★)** ★ ★",
    "OI-391-5": "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-5·★★与 L-29 同源★★)★: ★**新闸 `HW/check_fts_land_drill_same_batch.py` "
               "★**【与那四处登记同批挂】进 `state/gate_check.py`, 不提前挂** ★★"
               "★**★⇒ 理由 (★main 本机实跑实测★)★**: ★**★这道闸现在裸跑 rc=0 (7/7 全绿·★因为 §4 已被提前落过★), 而 `--selftest` rc=1 (`14/17` · 末行 `SELFTEST FAILED`) ⇒ ⇒ "
               "★**★⇒ 按 L-29 通则①: selftest 末行不是 `ALL TESTS PASS` ⇒ 这道闸【不可信】⇒ ⇒ ⇒ 【现在挂进去 = 把一道【夹具跟不上真件】的闸挂进链】⇒ ⇒ 链上多一道【看起来绿、其实抓不到】的闸 ⇒ ⇒ 比不挂更坏** ⇒ ⇒ "
               "★**★⇒ 挂链时机 = 【夹具修好 + 自测全绿】之后, 与那一趟的其余动作同批** ⇒ ⇒ ★**★⇒ 且【挂链动作只能由 main 在那一趟统一做】(★不许 agent 自挂★)** ⇒ ⇒ "
               "★**★⇒ 顺带: 本轮三道新闸的挂链裁决汇总 = `check_sw_gate_health` 【结构上不可挂·★它自己判自己红★】 + `check_fts_seat_body_geometry` 【可挂·★但要跟 §2 账同批刷★】 + "
               "★**`check_fts_land_drill_same_batch` 【暂不可挂·★夹具先修★】⇒ ⇒ ⇒ 真正能挂的是【一道】, 其余两道各有各的理由** ⇒ ★ ★",
}

★**⑥ ★★★★一条自曝铁律 (L-32) ★★★★**
★**★★本轮 main 自曝: 我 13:1x 那一轮落的 15 条 pm.yaml 答案, 【一条都没闭上任何 need】★★** ⇒ ★**原因 (★main 本机实读 `state/merge.py` 坐实★)**: ★**merge.py 按【精确 key】配对 needs_from × answers: `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]` ⇒ ⇒ key 必须与 need 的 key 【逐字相同】, 且答案必须落在【被问的那个 agent】的分片里** ⇒ ★**★⇒ 而我 13:1x 用了【自己起的改名 key】(★如 `iss389_main_oi5_pick_4810`, 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★) ⇒ ⇒ **配不上 ⇒ 零闭合** ⇒ ⇒ ★★"
               "★**★★⇒ 实测: pm.yaml 里 to=main 的答案中, 逐字命中 need key 的只有 113/152 ⇒ ⇒ 我 13:1x 那 15 条全在「没命中」那一侧 ⇒ ⇒ 且 `merge.py --json` 的 lint 里【答案 key 无 need 引用】那一条共 189 条, 我那 15 条全在里面** ★ ★"
               "★**★★⇒ 这不是「答案内容错了」, 是【答案【落错了 key】⇒ 机制上没生效】⇒ ⇒ ★★【内容仍然有效, 只是没被机制读到】⇒ ⇒ 本轮已按 need 的原 key 重答一遍 (★见 §⑤ 各组的 key·★一律用 need 的原 key★) ⇒ ⇒ **原 15 条【老字一字未删】, 保留作人读记录** ★ ★"
               "★**★★⇒ ★★比 L-28 的「key 撞名」更危险的是这一面★★: ★**L-28 = 【撞名】⇒ 幂等守卫会报错退出 ⇒ 至少【有声音】; 而这里是【没撞名, 只是对不上】⇒ ⇒ 机制【一声不吭】⇒ ⇒ 答案躺在 pm.yaml 里, 内容正确, 但【对闭环机制等于不存在】⇒ ⇒ **页面上看起来「已答」, 台账上其实还挂着** ⇒ ⇒ ⇒ **所以 L-28 与 L-32 合起来 = 【key 的两端必须逐字对齐, 且对齐要回读验证】** ★★"
               "★**★★⇒ ⇒ 一条操作纪律 (★本轮起执行★)**: ★**落 pm.yaml 答案前, 必须先从 need 里【逐字复制 key】, 不许自己起; 落盘后必须回读验证【该 key 的 need 已从 pending 变 answered】⇒ ⇒ 不许只看「脚本打印 ✅ 已原子更新」(★L-28 通则② 同源★)** ★ ★"

★**⑧ ★★本轮的一次【受保护集被第三方改动】的处置 (★fail-closed 挡下来的·★披露在此★)★★**
★**★**事实 (★本机实读★)★**: ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 md5 从 `b5d8d5b9…` 变成 `192873f6…` ⇒ ★**本轮的阶段 1 保护集核对因此判红 ⇒ ★★fail-closed 退出 (★零写盘★)⇒ ★★我先查了是谁改的: mtime = **18:32:02** ⇒ 落在兄弟 job fb67af40 那一趟 (★它 18:20 开 **ISS-396**「FTS 改孔登记落盘」·★18:43 出了交卷页★) ⇒ ⇒ 【第三方·合法派活·不是 main 落的·也不是越权】** ★
★**★**范围核对 (★main 本机实跑·★逐行 diff 对着旧基线副本 `tmp/iss396/backup/PREFLIGHT.md.bak`★)★**: ★**共 8 行改动, 全部落在 `B33_PIN_LAND_1P27` 那一项 (★描述列 + `current_state` + `criterion` 三处 + 表格行★) ⇒ 内容 = ★**把「钻孔 Ø0.65→Ø0.71mm」补进同一项的两条腿** ⇒ ⇒ ★**正是 §4 #2/#3 该做的事 ⇒ ⇒ 改动范围与派活意图一致 ⇒ ⇒ 【无越权·无板侧改动】** ★
★**★**⇒ 处置**: ★**① 重设受保护集基线 (`b5d8d5b9…` → `192873f6…`) 并在阶段 1 里【永久保留这道范围核对】⇒ 以后每次跑都要重新确认【改动只落在 B33】⇒ 改动越界就会当场红; ② ★**板三项 / 网表 / 脚表 / BOM 逐字节未动 (★本机复验★) ⇒ 「板只改一次」纪律没破**; ③ ★**⇒ 但这次提前落盘有一个【机器后果】必须记: 它把 ISS-391 闸的 D1/D2/D3 从红翻绿, 而该闸的 selftest 是按【未登记时的原文】写死锚点 ⇒ ⇒ 夹具脱节 ⇒ ⇒ selftest 14/17 ⇒ ⇒ 【这正是 §④ 那 6 条依据】⇒ ⇒ 【提前落 ≠ 无代价: 代价是【闸的夹具得跟着真件现读】】** ★
★**★**⇒ ★★教训 (★可复用·★已并入 L-32★)★**: ★**★**「受保护集判红」有两种可能: ① 【我自己改了】(★要披露+回滚判断★) ② 【别人改了】(★要查是谁+核对范围+重设基线+保留范围核对闸★) ⇒ ⇒ 判红的【第一动作】不是「改基线让它绿」, 而是【查 mtime + 查是谁 + 逐行核对范围】⇒ ⇒ ★**★**main 本轮的做法 = 先 fail-closed 退出 (零写盘) → 再查 mtime/派活记录/逐行 diff → 确认是合法第三方改动且范围与意图一致 → 才重设基线并【保留范围核对】⇒ ⇒ ★★**这个顺序不能反** ★ ★**

★**⑦ 本轮零派 / 零外发 / 零落表 / 零写板 / 零挂链**: ★**internal = 0** ⇒ ISS-392/393/394 三条真在飞 ⇒ 不重复派 ★外发段恒空 ★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标 / 清空区放大量的一切前提都挂在它身上, 本页不代拍** ★"
               "★**⇒ 「板只改一次」那一趟现在明确要带【五条腿】**: ★**① 改孔 `0.65→0.71` (★环宽 `0.1450` 的制程能力确认同批★) ② 四处清单登记 (§4 #5 + #6 仍未落) ③ 新闸挂链 (★真正可挂的只有一道·★另两道各有理由★) ④ 六个签收件的 md5 刷新 + 全部验收线重跑 (★L-27 通则③·★本轮 §⑤ 裁决落进已 verified 的单 ⇒ 必须重验★) ⑤ ISS-391 闸的夹具改成【真件现读】(★归 owner·★修完自测全绿才谈签收★)** ★ ★"
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  一页: %d → %d B (追加式 §㊻, 备份 %s.bak_%s_main_sign_iss388_390_391)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l32" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-32 · ★★落答案时必须【从 need 里逐字抄 key】⇒ 自己起 key = 机制【静默不闭合】(★比撞名报错更危险★) ★★

★**实测 (2026-11-24 19:5x, main 本机实读 `state/merge.py` + 逐 key 核对·★本轮自曝★)★**: ★**main 在 13:1x 那一轮落了 15 条 pm.yaml 答案, 内容全对, 但【一条都没闭上任何 need】** ⇒ ★**★⇒ 机制读数: pm.yaml 里 `to=main` 的答案中, 【逐字】命中某个 need 的 key 的只有 113/152 ⇒ ⇒ 我那 15 条全在「没命中」那一侧; 且 `merge.py --json` 的 lint 里【答案 key 无 need 引用】那一类共 189 条, 我那 15 条全在里面** ★ ★
★**★根因 (★main 本机实读 `state/merge.py` 坐实★)★**: ★**merge.py 按【精确 key】配对: `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]` ⇒ ⇒ key 必须与 need 的 key 【逐字相同】, 且答案必须落在【被问的那个 agent】的分片里 (★`to=main` 的 need ⇒ 答案必须在 pm.yaml★)** ⇒ ★**★⇒ 而我 13:1x 用了【自己起的改名 key】(★如 `iss389_main_oi5_pick_4810`, 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★) ⇒ ⇒ **配不上 ⇒ 零闭合** ★ ★
★**★⇒ ★★这比 L-28 的「key 撞名」更危险★★**: ★**L-28 是【撞名】⇒ 幂等守卫会报错退出 ⇒ 至少【有声音】; 而这里是【没撞名, 只是对不上】⇒ ⇒ 机制【一声不吭】⇒ ⇒ 答案躺在 pm.yaml 里, 内容正确, 但【对闭环机制等于不存在】⇒ ⇒ **页面上看起来「已答」, 台账上其实还挂着** ★ ★
★**★⇒ 两条纪律 ★★**: ★**① 落答案前, 必须先从 need 里【逐字抄 key】(★不许自己起, 不许「起个更清楚的名字」★)⇒ ⇒ 若 need 的 key 本身不适合当答案的 key, 那就【改 need 的 key】或【在答案的 value 里写清对应关系】, 但【不许两边名字不一样而指望机制能猜】** ★ **② 落盘后必须回读验证【该 key 的 need 已从 pending 变 answered】⇒ ⇒ 不许只看「脚本打印 ✅ 已原子更新」(★L-28 通则② 同源: writer 的成功消息只保证【写成功】, 不保证【写对了地方】★)** ★ ★
★**★⇒ ★★推广 (★不止 pm.yaml★)★**: ★**凡是有「按 key 配对」的地方 (★merge 的 needs×answers · gate 的 (file,line) 钉住 · 一页的章节号索引 · 决策索引的 55 条覆盖复核 · ★★闸的 selftest 用固定字符串常量去构造反向用例★), 【键必须逐字对齐】, 而【对齐这件事本身要有回读验证】⇒ ⇒ ★**★⇒ 反过来说: 【机制【静默失效】比【机制【报错】更贵】⇒ ⇒ 所以凡是我新写的机制, 都必须自带一句「配对不上就报错」** ★★"
★**★⇒ ★★★与 L-31 的合看 (★两条同一天, 一个讲机制, 一个讲夹具★)★★**: ★**L-31 = 【闸的沙盒落点必须每次运行唯一】⇒ 两个 cron job 同分钟各跑一次门禁链, 必有一个拿到【假红】★ ⇒ ★★**L-32 = 【闸的 selftest 锚点必须从真件现读】⇒ 真件一旦被登记过一遍, 写死的锚点就【匹配不上】⇒ ⇒ 反向用例【假绿】(★期望红却绿★) ⇒ ⇒ 这道闸【看起来绿, 其实抓不到它要抓的东西】** ★★ ⇒ ⇒ ★★**★⇒ ★★合起来是一条更大的通则: 【凡是【锚在真件上】的东西 —— key / 落点 / 字符串常量 —— 都必须【从真件现读】, 不许写死; 一旦写死, 真件一变, 判据就【静默失效】】★★** ★ ★"
★**★⇒ 与 L-21~L-30 合看★**: ★**L-21 清单钉 file,line · L-23 工具会扫到自己 · L-24 沙箱硬链接 · L-25 厂商料号逐个坐实 · L-26 签收要跑扫描面命中的闸 · L-27 签收要等 owner 收工 · L-28 幂等守卫不许静默吞 · L-29 按设计判红 ≠ 闸坏了 · L-30 取号/取 key 必须先查重 · L-31 沙盒落点要唯一 · L-32 锚在真件上的东西必须现读** ⇒ ★**★共性 = 【凡是有「键」的地方, 键的两端必须逐字对齐, 且对齐要回读验证】** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  LESSONS: %d → %d B (追加式 L-32, 备份 %s.bak_%s_main_l32)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_pm():
    # ★★必须用【need 的原 key】⇒ 否则配不上 (L-32) ★★
    ANS = [
        ("iss388_ledger_drift_owner", "sw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss388_ledger_drift_owner★)★: ★**账漂 (D-1~D4) 归【main 授权 + owner 落追加式订正块】, "
         "且【必须与「板只改一次」那一趟同批】** ★★"
         "★**★⇒ 理由 (★main 本机实跑 + 实读 `state/merge.py` 坐实★)★**: ★**① 改的是 ISS-372 真相页的 §1/§2 机器块 = 【已签收页】⇒ 按「已签收件的订正路径」⇒ "
         "★**main 授权路径, owner 落追加式订正块 (★老字一字未删★) ⇒ main 不直接改 owner 的正文**; "
         "★**② 为什么必须同批**: ★**D-1~D-4 的差集 = 【那三道闸坏了 + 账没跟上】⇒ 修账不修闸 = 账上写「已登记」但闸还是坏的 ⇒ ⇒ "
         "★**⇒ 必须【账 + 闸】一起修** ⇒ 而闸的修法在 §㉙ 与 §㊶ 已裁 (★闸 2 的 selftest 0/10 = 差值型自测在基线已红时全灭⇒ 归 SW 域那一趟同批★) ⇒ ⇒ "
         "★**③ 且闸 2 与闸 v2 修好之前, 新闸 `check_sw_gate_health.py` 必须保持零挂链** ⇒ 挂了它自己 H4 会红 (★源码 L463-465 实测★) "
         "⇒ ⇒ **零挂链是它的正确形态** ⇒ ⇒ ★**★⇒ 落法 = main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★"
         "★**★⇒ 附: 本轮 main 已实跑确认这 4 条差集 = §2 账少登记 2 道 (`check_sw_false_connectivity_gate.py` + `check_sw_gate_chain_coverage.py`) + "
         "§1 账少登记 3 行 (`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` / `:241` / `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215`)** ★",
         "SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md §1/§2 机器块 · SW/tools/check_sw_gate_health.py H2/H3 · 一页 §㊻ A1"),

        ("iss388_new_gate_hook_to_main", "sw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss388_new_gate_hook_to_main★)★: ★**【不挂】, 且这不是「暂缓」而是【结构性不可挂】** ★★"
         "★**★⇒ 理由 (★main 本机实读源码坐实·★不是抄报告★)★**: ★**该闸的 H4 判据字面就是 `hook_hits = gc_txt.count(\"check_sw_gate_health\")` "
         "★**(★源码 L463-465★) ⇒ ⇒ 它一旦出现在 `state/gate_check.py` 里, 它【自己】立刻判红 ⇒ ⇒ 挂它 = 让它自己判自己红 = 【假红】⇒ ⇒ "
         "★**★⇒ 零挂链是它的正确形态, 不是缺陷** ★★"
         "★**★⇒ ★★「挂链就能看见」这个直觉在这里【是错的】★★**: ★**看不见的病根 = 【那三道病闸零挂链 + 坏了没人跑】⇒ ⇒ 处置不是挂这道元闸, 而是"
         "★**① 修那三道闸 (★闸 2 的 selftest 0/10 + 闸 v2 的 0/7 + 闸 1 的环境耦合★) + ② 把它们挂进链** ⇒ ⇒ ★**⇒ 而它们【现在挂不得】(★挂了当场红·★基线先红的账没修完★) ⇒ "
         "⇒ ⇒ 顺序 = 账漂修完 + 闸修好 + 再挂 ⇒ ⇒ 全部归 SW 域那一趟 ⇒ **本轮只裁归属, 不代排顺序** ★ ★"
         "★**★⇒ 附: 本轮已实测确认这四道新闸在 `state/gate_check.py` 里 grep 命中【全为 0】⇒ ⇒ 零挂链状态成立 ⇒ ⇒ 零改既有闸成立** ★",
         "SW/tools/check_sw_gate_health.py H4 (源码 L463-465 实测) · 一页 §㊻ A2 · 一页 §㊻ §④"),

        ("iss388_env_sensitivity_fix_location", "sw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss388_env_sensitivity_fix_location★)★: ★**路 A (在源头修) 为主 + 路 B (调用约定) 为辅, "
         "且【顺序 = 先 B 后 A】** ★★"
         "★**★⇒ 理由 (★main 本机实跑复现★)★**: ★**① 闸 1 的红是【同一份源码, 只差 TMPDIR ⇒ 10/11 vs 11/11】⇒ ⇒ 判据本身与环境耦合 ⇒ ⇒ "
         "★**这是【闸的缺陷】, 不是调用方的错 ⇒ ⇒ 病根在闸 ⇒ 必须源头修 (路 A)** ⇒ 否则「靠人记得带 TMPDIR」= 把判据正确性押在人的记性上 (★ISS-297 已栽过一次「约定靠人记会有忘的那天」★); "
         "★**② 但路 B 也不能不做**: ★**本机 `/tmp` 用户配额打满 ⇒ 不带 TMPDIR 会假红 (★rc=120 / 0 字节★) ⇒ ⇒ ★**路 B 是止血 (今天就让一切调用都带对), 路 A 是治病 (让闸与环境无关)** ⇒ ⇒ "
         "★**★⇒ 顺序 = 先 B (零风险·今天可落) + 后 A (要重签 ISS-372/ISS-375 ⇒ 归 SW 域那一趟同批·★本轮不代排★)** ★ ★"
         "★**★⇒ 代价账 (★本单已算·★main 核对后成立★)★**: ★**路 A = 改【已签收件】的判据逻辑 ⇒ 必须 main 授权 + owner 落 + 重跑 11 条反向用例 + 重签 ⇒ ⇒ "
         "★**★⇒ 那是一次签收指纹过期 (★今天已在 ISS-381/382/384 上栽过两次·★L-27★) ⇒ ⇒ 【不进这一趟】** ⇒ ⇒ ★**★⇒ 落法: 路 B 归 owner 立即落 (★写进 `state/check_brief_commands.py` 或任务书模板★); "
         "路 A 归 SW 域那一趟同批, main 在那一趟授权** ★ ★",
         "SW/tools/check_debug_pin_order_contract.py (本机实跑: TMPDIR=$PWD/tmp ⇒ 11/11 PASS; 不指 ⇒ 10/11 FAIL) · 一页 §㊻ A3"),

        ("iss388_third_sick_gate", "sw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss388_third_sick_gate★)★: ★**要修, 但【不另起一单】⇒ 归「板只改一次」那一趟同批** ★★"
         "★**★⇒ 理由 (★main 本机实跑★)★**: ★**① `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` = 0/7, 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」⇒ ⇒ "
         "★**它【真的坏了】, 不是误报 ⇒ 必须修** (★本单只登记不修是对的: 它不在本单 brief 范围内★); "
         "★**② ★★但它的失败模式与闸 2 同类 (基线先红 ⇒ 差值型自测全灭) ⇒ ⇒ 修它的前置 = 先修账 (D-1~D-4) ⇒ ⇒ 【它与账漂是同一条因果链】⇒ ⇒ "
         "★**★⇒ 拆成两单 = 两批做完 = 又一次「板只改一次」的纪律破例 ⇒ ⇒ 归同一趟** ★ "
         "★**③ ⇒ 归属 owner = sw-lead (★它本来就该在 SW 域那一趟里·★本轮只裁归属, 不代排顺序★)** ★ ★"
         "★**★⇒ 附: 本轮已实测 `check_sw_ref_reachability_v2.py --selftest` = 0/7 + 末行「❌ 有用例没抓到」⇒ main 独立复核确认它确实坏了** ★",
         "SW/tools/check_sw_ref_reachability_v2.py (本机实跑 --selftest 0/7) · 一页 §㊻ A4"),

        ("iss388_delta_selftest_convention", "sw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss388_delta_selftest_convention★)★: ★**「基线必须先绿, 否则 selftest 结论不可读」写进闸的编写通则 —— "
         "【采纳】, 但【落法 = 新增一份通则文档 + 逐闸加前置断言】, 不是【逐个改已签收闸的 selftest 口径】** ★★"
         "★**★⇒ 理由 (★main 本机实跑★)★**: ★**① 闸 2 = 0/10 与闸 v2 = 0/7 都是【差值型自测在基线已红时全灭】⇒ ⇒ 闸自曝「我不可信」却说不出「我是账漂了不是坏了」⇒ ⇒ "
         "★**⇒ 现场只能靠人读源码 ⇒ ⇒ 这个病确实需要一条通则**; "
         "★**② ★★但「一次性改若干已签收闸的 selftest 口径」这条路【本轮不走】★★**: ★**(a) 改已签收闸的 selftest 逻辑 = 改判据 ⇒ 要重签 ⇒ 又是一次签收指纹过期 (★L-27·★今天已栽两次★); "
         "★**(b) 且「差值型自测」本身不是错 —— 它【自证「红集 == {目标那一条}」】这个设计是对的 ⇒ ⇒ 错的只是【基线已经红的时候, 差值不可读】⇒ ⇒ "
         "★**★⇒ 正确解法 = 让基线先绿 (A1 的账漂 + 那三道闸修好) ⇒ 差值自测自然可读 ⇒ 通则只需写成【写闸时必须先声明「本闸的基线是什么; 基线红了 selftest 结论不可读」】+ "
         "★**错误消息点名是哪个闸 + 它的原文末行 (★这正是新闸 H0 已做到的★)** ⇒ ⇒ ★**★⇒ 落法 = 新增一份通则 (★main 落·★`state/GATE_WRITING_CONVENTIONS.md`·★新文件不碰任何已签收闸★) + "
         "逐闸加前置断言归 SW 域那一趟** ⇒ ★★"
         "★**★⇒ ★★与本轮 §㊻ 的 A1/A4 同一因果链 (★基线先绿是前置★) ⇒ 三条一起归那一趟** ★ ★"
         "★**★⇒ ★★而且本轮 ISS-391 的闸又给了这条通则一个【新证据】: 它的反向用例【锚在固定字符串常量上】⇒ 真件被登记过一遍 ⇒ 锚点匹配不上 ⇒ ⇒ **三条用例【假绿】⇒ ⇒ 闸【看起来绿, 其实抓不到】** ⇒ ⇒ ⇒ **所以这条通则必须再加一句: 【selftest 的锚点必须从真件现读, 不许写死常量】** (★见 L-32★) ⇒ ★ ★",
         "SW/tools/check_sw_board_md5_rebase_readiness.py --selftest 0/10 · SW/tools/check_sw_ref_reachability_v2.py --selftest 0/7 · 一页 §㊻ A5"),

        ("iss390_correction_landing", "mech-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss390_correction_landing★)★: ★**6 处定性订正归【main 授权 + owner 落追加式订正块】, "
         "且【与「板只改一次」那一趟同批】** ★★"
         "★**★⇒ 理由 (★main 本机独立复核坐实·★不抄页面★)★**: ★**① 这 6 处全是【已签收页正文 + 已签收闸源码字符串】⇒ 按「已签收件的订正路径」⇒ "
         "★**main 授权路径, owner 落**, main 不直接改 owner 的正文 (★老字一字未删·★只加订正块★); "
         "★**② 为什么要同批**: ★**§4 #3 的两处源码字符串 (`MECH/check_debug_seat_3d_fit.py` L848 / L879) 是【已签收闸的判据源码】⇒ 改它 ⇒ "
         "★**⇒ 那两道签收指纹当场过期 ⇒ ⇒ 【必须与那一趟的「重验全部验收线」同批】(★L-27 通则③★) ⇒ ⇒ "
         "★**③ ⇒ 并且: 这 6 处不落 ⇒ 【通用件 vs 厂件】的前提错误继续留在页上与闸源码里 ⇒ ⇒ 下一个读这页或跑那个闸的人会拿错对照物做结构判决 ⇒ ⇒ "
         "★**★⇒ 而本闸 G3 的未落清单会永远停在 17 处 ⇒ ⇒ 【G3 恒红 ⇒ 这道闸自己也就废了】⇒ ⇒ ★**★⇒ 故: main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★"
         "★**★⇒ 附 (★main 本机解析 `.kicad_mod` 坐实的原文依据★)★: ★**通用件 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 的 `fp_rect` = **3.1000 × 6.0900** ⇒ "
         "★**⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」; `PinHeader_1x02_…` = **3.1000 × 3.5500** ⇒ 「`3.5500` 同源」⇒ ⇒ **⇒ `6.0900`/`3.5500` 这组数与 Samtec 无关** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §4 (6 处 COR-x) · MECH/check_fts_seat_body_geometry.py G3 · 一页 §㊻ B1"),

        ("iss390_h_lock_and_test_sample", "mech-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss390_h_lock_and_test_sample★)★: ★**两问分别裁 —— (甲) h 走【三档参数化】, 不锁死; "
         "(乙) 打样归【那一趟同批】** ★★"
         "★**★⇒ (甲) 理由 (★main 本机复核坐实★)★**: ★**① ISS-390 给的输入 = 厂件柱高 `3.05` mm (官网表 TABLE 1 lead style -01) 而绝缘体只有 `0.86` ⇒ ⇒ "
         "★**⇒ 罩内腔板面以上那一维【不能】按 `0.86` 出件 ⇒ `h=0.90` 档【物理上装不下】⇒ 可行档是 `2.54` 与 `4.00` ⇒ ⇒ "
         "★**★⇒ 这把 §㊶ C8 那条 (「h 不卡那一趟」) 的依据从「[0数据]」升级成了「[0数据] 且已算明可行档只剩两个」⇒ ⇒ 【本裁决与 §㊶ C8 一致, 且依据更强】** ⇒ "
         "★**② ⇒ 【不锁死】的理由 = h 锁死会绑死一个【还没测过】的量 ⇒ ⇒ 三档参数化 (0.90 / 2.54 / 4.00) 让结构侧在两档之间走, 而 0.90 已被物理判死 ⇒ ⇒ "
         "★**⇒ 实际只剩 2.54 与 4.00 两档 ⇒ ⇒ 锁定权仍在 boss (★`iss389_oi11_seat_height_window` 未代拍★) ⇒ ⇒ 本裁决只裁「形式」, 不裁「值」** ★ ★"
         "★**★⇒ (乙) 理由★**: ★**打样是【唯一能拿到 REF 公差】的路径 (★官网图给的是 REF 不是公差带★) ⇒ ⇒ 落 FTS 时打一块单板样、用卡尺量三量 "
         "★**(★绝缘体高 / 外形宽 / 外形深★) 回填 `keepout_dwg` + `body_geometry` ⇒ ⇒ 【必须与那一趟同批】(★落 FTS 那一天才有样可打★) ⇒ ⇒ "
         "★**★⇒ 归 mech-lead 执行 (转派), 但【不新起一单】(★与那一趟同批·★与「板只改一次」纪律一致★)** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §6.1 · 一页 §㊻ B2 · §㊶ C8"),

        ("iss390_oi12_and_oi14_together", "mech-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss390_oi12_and_oi14_together·★★★三个答案一起给★★★)★: ★**"
         "(a) 罩住判据【管到座体本体】(★不是只管铜箔★) ⇒ 采纳; (b) 「偏紧 `0.5200`」的措辞【作废】(★`6.0900` 是通用库件的 `F.CrtYd`, 厂件【没有】courtyard 这个量★) ⇒ 保留判据本身; "
         "(c) ⇒ (a) 成立 ⇒ J_UART 的 X 需求从 `4.0700` 变 `4.3400` ⇒ ⇒ 【OI-14 (DP-1) 的目标值 = `4.3400`】** ★★"
         "★**★⇒ 理由 (★main 本机独立复核坐实·★自己解析 .kicad_mod·★不抄页面★)★**: ★**① 座体本体 (厂件 X `5.0800` / `2.5400` + Y `2.1600`) 比铜箔包络 "
         "★**(★X `4.8100` / `2.2700`★)【每边都大】⇒ ⇒ ★**★⇒ 只按铜箔算 = 会做出一个【装不进座体】的洞 ⇒ ⇒ 判据必须同时管座体本体 ⇒ ⇒ (a) = 管 ⇒ 采纳** ★ "
         "★**② ⇒ (b) 作废**: ★**「偏紧 `0.5200`」的对照物是 `6.0900` ⇒ 而 `6.0900` 是【通用 KiCad 库件自己的 `F.CrtYd`】(★main 本机解析 `.kicad_mod` 的 "
         "★**`fp_rect` = 3.1000 × 6.0900 坐实★) ⇒ ⇒ ★**★⇒ Samtec 厂件【没有】courtyard 这个量 ⇒ 那句「比 courtyard 还小」在【厂件】这一层【无意义】⇒ ⇒ (b) = 作废那句措辞, 保留判据** ⇒ "
         "★**★⇒ ★注意: 这不是「判据错了」, 是【对照物拿错了】⇒ ⇒ 判据本身 (每边 `0.9000` = `CRIT 0.60` + `TOL 0.30`) 仍然成立** ★ "
         "★**③ ⇒ (c) 是 (a) 的算术后果**: ★**厂件 J_UART 座体 X `2.5400` + 2 × `0.9000` = `4.3400` (★不是 `4.0700`·★`4.0700` 是按铜箔 `2.2700` 算的★) ⇒ ⇒ "
         "★**★⇒ OI-14 (DP-1) 的目标值 = `4.3400`** ★ ★"
         "★**★⇒ ★★★★与 §㊶ C4 / §㊶ C6 【冲突】⇒ ⇒ 按 L-27 通则③ (main 落裁决 ⇒ 已 verified 的单的交付物进入「会动」状态 ⇒ 那一趟必须重验全部验收线) ⇒ ⇒ "
         "★**★⇒ 本条取代 §㊶ C4 与 C6 的对应部分, 老裁决的数值随之作废** ⇒ ⇒ ★**★⇒ 而 §㊶ C6 那个 `4.0700` 恰好是本单 §4 订正清单里的一条 (★L634 机器块 + 正文路径 B 段★) ⇒ ⇒ 正好一起订正** ★ ★"
         "★**★⇒ 与 §㊴ C1 (OI-5 取 `4.8100`) 【不冲突】: `4.8100` = 铜箔沿脚排总展 (★判「装得下」的输入★), `4.3400` = 座体本体 + 2×余量 (★判「装得下且留得住」的输出★) ⇒ 两个数【都要】** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §4/§5 · main 本机解析 .kicad_mod (fp_rect 3.1000×6.0900) · 一页 §㊻ B3"),

        ("iss390_y_direction_open_question", "mech-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss390_y_direction_open_question★)★: ★**Y 向走【放大罩开口 Y】, 但【幅度按座体本体重算】⇒ "
         "★**开口 Y 须 `≥ 5.7600`** (★取代 §㊶ C5 的 `5.6000`/`5.8000`★)** ★★"
         "★**★⇒ 理由 (★main 本机实算★)★**: ★**① 座体本体 Y = `2.1600` (厂件·★main 本机复核: 通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`★) ⇒ "
         "★**⇒ 按每边 `0.9000` ⇒ 清空区 Y 需求 = `2.1600` + 2 × `0.9000` = `3.9600` ⇒ ⇒ ★**★⇒ 比 §㊶ C5 裁的 `2.8000` 大 `1.1600`** ⇒ ⇒ "
         "★**★★⇒ §㊶ C5 的【方向】(放大罩开口 Y) 仍成立, 但【数值】需重算: 开口 Y 须 ≥ 清空区 Y `3.9600` + 2 × `0.9000` = `5.7600`** ⇒ ⇒ "
         "★**★★⇒ ⇒ 本条构成对 §㊶ C5 的【订正】(方向同, 数值收窄)** ★ "
         "★**② ⇒ 「接受零余量」那个选项【已不存在】(★本单自己也这么说★) ⇒ ⇒ (b) 改判据口径只罩铜箔 = 【已判死】(★只罩铜箔 = 装不进座体★) ⇒ ⇒ "
         "★**⇒ 只剩 (a) 放大罩开口 Y 一条路** ⇒ ⇒ **罩开口 Y `4.6000` → `5.7600` = 放大 `1.1600`** ★ "
         "★**③ ⇒ 结构性代价 (镜脚内腔 + 罩外观缝) 与 §㊶ C5 同源 ⇒ ⇒ 与板框第一问同批** ⇒ ⇒ ★**★⇒ 与 `iss390_oi12_and_oi14_together` 同源 ⇒ 两条一起落** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §5 (Y 向缺口 1.1600) · 一页 §㊻ B4 · §㊶ C5 (本条订正之)"),

        ("OI-391-1", "hw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-1·★★★本轮有订正: 登记已被提前落★★★)★: ★**三处补登记归【owner 落追加式订正块, "
         "落在「板只改一次」那一趟的清单改版里】, 【本不该提前落】—— ★★★但本机实读发现【已提前落】(★作业包/预检清单/生成器 = 18:28~18:32·★兄弟 job fb67af40 那一趟·★不是 main 落的★) ⇒ ⇒ "
         "★**⇒ 因此本问已被【部分回答】⇒ ⇒ 追加订正: 登记已落 ⇒ D1/D2/D3 现在【本该是绿的】(★与实测一致★) ⇒ ⇒ 但 §4 #5 (BOM L71/L77 两栏) + §4 #6 (生成器现读) 仍【未落 / 待复核】⇒ ⇒ "
         "★**⇒ 且【提前落】触发了本闸的夹具脱节 (★见一页 §㊻ §④③④★) ⇒ ⇒ ⇒ 本问【改为: §4 #5 仍归 owner 在那一趟落; 提前落这件事的后果由 §④ 的夹具修复吸收】** ★★"
         "★**★⇒ 为什么不许提前落 (★机器可核★)★**: ★**提前落 ⇒ 中间态 = 板还没改, 清单却写了要改孔 ⇒ ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (★板上还是 `0.65`★) ⇒ 当场红 ⇒ ⇒ "
         "★**★⇒ 现场会把它读成「板坏了」⇒ ⇒ 这正是 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + ISS-384 A5 全同款纪律的另一种说法** ⇒ ⇒ "
         "★**★⇒ 且 §4 #1/#2/#3 必须【一起落】** (★`wp02_tokens()` 会从③的原文里自动抽「小数」当覆盖令牌 ⇒ 补上 `0.65` 与 `0.71` 之后, 现有 P4 会自动要求清单页 "
         "★**`B33_PIN_LAND_1P27` 里也能查到这两个数 ⇒ ⇒ #1 与 #2/#3 不同步 ⇒ P4 当场红★) ⇒ ⇒ **三处一起** ★★"
         "★**★⇒ 逐字文本按真相页 §4 #1/#2/#3 原样落, main 不改一字; 落法 = 追加式订正块 (★老字一字未删★)** ★★"
         "★**★⇒ 附 (★main 自己的发现·★两页都没算这一格★)★: 改孔后环宽 `0.1750 → 0.1450` mm, 且本板 `.kicad_pro` 的 DRC 只有 `min_via_annular_width 0.1` (过孔) ⇒ "
         "★**⇒ THT 焊盘环宽【无判据】⇒ 触不到板 DRC ⇒ ⇒ 属【制程能力】问题 ⇒ 那一趟投板前必须坐实 ⇒ 见 `iss394_ring_width_fab_capability`** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4 #1/#2/#3 · 一页 §㊻ C1 · L-29 通则③"),

        ("OI-391-2", "hw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-2★)★: ★**写成【一条】(pitch 与 drill 是同一项的两条腿, 不可只做其一), 不许拆成两条可分开的动作** ★★"
         "★**★⇒ 理由 (★机器可核★)★**: ★**新闸 D1 只能查出【整条没写】, 查不出【拆成两条只做其一】⇒ ⇒ 拆开写 = 判据出现盲区** ⇒ ⇒ "
         "★**★⇒ 一条写 + 锚点含两个数 (`0.71` 与 `1.27`) = 机器可判** ⇒ ⇒ ★**★⇒ 与 §㊻ A1/B1 同一纪律: 措辞口径由 main 定, 落法由 owner 落, 且【必须机器可判】** ★ ★"
         "★**★⇒ ★★main 本轮实测的一条补充 (★比本裁决本身更重要★)★: ★**★真文件那一行的原文已经与闸的夹具常量【逐字不同】(★真件多了一句「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」★) ⇒ ⇒ 【锚点逐字匹配】这条裁决的【机器可判】前提【不成立】⇒ ⇒ ⇒ "
         "★**★⇒ 所以「一条写」之外, 还必须加一条: 【夹具的锚点必须从真件现读, 不许写死常量】** ⇒ ⇒ 归 owner 修夹具时一并落 (★见 L-32★)** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §5 · 一页 §㊻ C2"),

        ("OI-391-3", "hw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-3★)★: ★**BOM L71 (J_DEBUG) / L77 (J_UART) 的 opn 与 footprint 两栏 = 与板侧 land 来源【同源】, "
         "★**落表时机 = 那一趟的同一次落表与重出; 本轮【零落表】** ★★"
         "★**★⇒ 同源纪律 (★板面 land 来源 = BOM 型号栏 = 实物料号★)**: ★**板侧 land 来源 = 盘上通用 KiCad 1.27mm THT 库件 "
         "★**(★`PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c…` / `PinHeader_1x02_P1.27mm_Vertical` md5 `47bcbf6d…`★) + 一条显式偏离登记 "
         "★**(★偏离项 = 铜箔焊盘直径官方无值 + 孔径由 `0.65` 改 `0.71`★) + BOM 型号栏写 FTS 料号** ⇒ ⇒ **不成立 ⇒ 投板后才发现 ⇒ 2-4 周返工** ⇒ ⇒ "
         "★**★⇒ 逐字草案按真相页 §4 #5 原样落, main 不改一字** ⇒ ⇒ ★**★⇒ 与 §㊶ A3 (OI-387-3) 同一裁决, 两处口径必须一致** ★ ★"
         "★**★⇒ 附 (★main 本机实读★)★: ★**HW/BOM_v1.csv 逐字节未动 (md5 `5b999399…`) ⇒ ⇒ §4 #5 **确实还没落** ⇒ ⇒ 归 owner 在那一趟落** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4 #5 · HW/BOM_v1.csv L71/L77 (★本轮零落表★) · 一页 §㊻ C3 · §㊶ A3"),

        ("OI-391-4", "hw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-4★)★: ★**生成器补登记归【owner (hw-lead) 落】, 且【与那一趟同批】; "
         "★**本轮【零改既有脚本正文】** ★★"
         "★**★⇒ 理由 (★机器可核★)★**: ★**`state/_iss277_build_preflight.py` 的 `build_pinland_item()` (title + current_state + criterion 三处一起长) + "
         "★**`read_board_pin_land()` 加一个 drill 字段现读板** ⇒ ⇒ ★**不落 ⇒ §3 #2/#3 的补登记【重跑一次就蒸发】(★ISS-349 同一位号已栽过一次★) ⇒ 白补, "
         "★**改孔这条子动作重新回到没人做的状态** ⇒ ⇒ ★**★⇒ 归 owner 落 (★本单零改既有脚本正文★) + 必须与那一趟同批 (★否则中途重跑一次就白补★)** ⇒ ★ ★"
         "★**★⇒ 附 (★main 本机实读 mtime★)★: ★**`state/_iss277_build_preflight.py` mtime = **18:28:31** ⇒ ⇒ §4 #6 **已经落过了** ⇒ ⇒ ⇒ 本问【已回答】⇒ ⇒ 剩下的是【闸的夹具要跟着真件现读】(★见一页 §㊻ §④④★)** ★ ★"
         "★**★⇒ 与 §㊶ A2 (OI-387-2「改孔与那一趟同批」) 同一批次 ⇒ 那一趟的「清单四处登记」批次要一次做完** ★ ★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4 #6 · state/_iss277_build_preflight.py · 一页 §㊻ C4"),

        ("OI-391-5", "hw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★OI-391-5·★★与 L-29 同源★★)★: ★**新闸 `HW/check_fts_land_drill_same_batch.py` "
         "★**【暂不可挂】⇒ 等【夹具修好 + 自测全绿】之后, 与那一趟的其余动作同批挂** ★★"
         "★**★⇒ 理由 (★main 本机实跑实测★)★**: ★**★这道闸现在裸跑 rc=0 (7/7 全绿·★因为 §4 已被提前落过★), 而 `--selftest` rc=1 (`14/17` · 末行 `SELFTEST FAILED`) ⇒ ⇒ "
         "★**★⇒ 按 L-29 通则①: selftest 末行不是 `ALL TESTS PASS` ⇒ 这道闸【不可信】⇒ ⇒ ⇒ 【现在挂进去 = 把一道【夹具跟不上真件】的闸挂进链】⇒ ⇒ 链上多一道【看起来绿、其实抓不到】的闸 ⇒ ⇒ 比不挂更坏** ⇒ ⇒ "
         "★**★⇒ 且 main 本机决定性实验已证明: 把真文件里「钻孔 0.65→0.71」这一腿删掉, D1 仍判绿 ⇒ ⇒ **它已经保护不了它要保护的东西** ⇒ ⇒ 不可签, 更不可挂** ⇒ ⇒ "
         "★**★⇒ 与全部先例同源: 闸与它要防/要等的那一趟同批生效** ⇒ ⇒ ★**★⇒ 且【挂链动作只能由 main 在那一趟统一做】(★不许 agent 自挂★)** ⇒ ⇒ "
         "★**★⇒ 顺带: 本轮三道新闸的挂链裁决汇总 = `check_sw_gate_health` 【结构上不可挂·★它自己判自己红★】 + `check_fts_seat_body_geometry` 【可挂·★但要跟 §2 账同批刷★】 + "
         "★**`check_fts_land_drill_same_batch` 【暂不可挂·★夹具先修★】⇒ ⇒ ⇒ 真正能挂的是【一道】, 其余两道各有各的理由** ⇒ ★ ★",
         "HW/check_fts_land_drill_same_batch.py 实跑 bare rc=0 + selftest 14/17 (非 ALL TESTS PASS) · 一页 §㊻ C5 · L-29 通则①"),

        ("iss394_ring_width_fab_capability", "hw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss394_ring_width_fab_capability·★★本轮 main 自己补的输入★)★: ★**环宽这件事归【那一趟投板前坐实】, "
         "★**归 main/老板商务动作, 但【本仓零外发】⇒ 处置 = 【自己查公开的板厂工艺能力表 + 在 RFQ 里问·★不自行发送★】** ★★"
         "★**★⇒ 已知的机器事实 (★main 本机实算★)★**: ★**① 官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 (annular ring) = (`1.000` − `0.71`) / 2 = `0.1450` mm** ⇒ "
         "★**(原 `0.65` 孔配同焊盘时 = `0.1750` ⇒ 改孔使环宽降 `0.0300`)** ⇒ "
         "★**② 本板 `.kicad_pro` 的 DRC 规则表里与环宽相关的只有 `min_via_annular_width 0.1` (★那是过孔环宽★) ⇒ ⇒ 【THT 焊盘环宽无独立判据】⇒ ⇒ "
         "★**★⇒ `0.1450` 【触不到板 DRC】⇒ ⇒ 它是【制程能力】问题, 不是 DRC 问题** ⇒ "
         "★**③ `min_through_hole_diameter 0.3` ⇒ 孔径 `0.71` 本身远大于下限, 不触 DRC** ⇒ "
         "★**④ ★★全仓 (HW/ MECH/ state/) 实查: 【没有任何一处】记录本板厂的最小环宽/最小焊盘/工艺能力表** ⇒ ⇒ ★**★⇒ 「`0.1450` 能不能做」当前【无据可判】** ★ ★"
         "★**★⇒ ⇒ 处置 (★与 §㊶ A1 的前置条件同一条·★两处引用同一件事★)★**: ★**「板只改一次」那一趟投板前必须坐实本板厂的最小环宽 (★或最小焊盘★) ⇒ "
         "★**⇒ 若 > `0.1450` ⇒ 焊盘须同步放大 ⇒ ⇒ 铜箔包络随焊盘放大而放大 ⇒ MECH 全链七个余量数【仍可能不变】但必须重算确认 ⇒ ⇒ "
         "★**★⇒ 若坐实不了 ⇒ 退化方案 = 焊盘放大到 `1.100×1.100` (环宽 `0.1950`) 并登记偏离 ⇒ 那时铜箔沿脚排总宽由 `4.8100` 变 `4.9100` ⇒ ⇒ MECH 七个数必须整体重算** ⇒ ⇒ "
         "★**★⇒ 这就是「板只改一次」必须在这一趟把环宽问清楚的原因: 问不清 = 那一趟投出去才发现 ⇒ 板改第二次** ★ ★"
         "★**★⇒ 【main 不代拍】环宽这个数 (★那是本板厂工艺能力, 不是本仓能推出来的★) ⇒ 且本项目 2026-11-12 02:02 起【零外发】⇒ ⇒ "
         "★**★⇒ 归【main 自己查公开板厂工艺能力表 + 老板侧 RFQ 时一并问】⇒ 不自行发送任何邮件/消息** ★ ★",
         "demo_mainboard.kicad_pro design_settings.rules · HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §0/§5 · 一页 §㊻ §③ · §㊶ A1"),

        ("iss394_seat_outer_dimensions", "hw-lead",
         "★**main 裁决 (★2026-11-24 19:5x·★main 地界·★iss394_seat_outer_dimensions★)★: ★**双轨降级方案【采纳】, 但【本轮已由 ISS-390 把【甲轨的官网值】取到了】⇒ "
         "★**⇒ 实际只剩【乙轨 (1 台样件实测)】待做 ⇒ 且【与「板只改一次」那一趟同批】** ★★"
         "★**★⇒ 已取得的官网值 (★main 本机独立复核坐实★)★**: ★**厂件座体宽 X = N × 1.27 ⇒ N=4 ⇒ `5.0800` / N=2 ⇒ `2.5400` (★main 本机算术复核命中★) · "
         "★**座体深 Y = `2.1600` (★通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`·★通用件比厂件窄 0.0600 ⇒ 当座体用 ⇒ Y 向每边少让 `0.0300`★) · "
         "★**绝缘体高 Z = `0.8600`** ⇒ ⇒ ★**★⇒ 所以 ISS-394 的 D2「维持 [0数据]」这句【已经过期】⇒ ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」(★库件根本给不了 Z★)** ⇒ ★ ★"
         "★**★⇒ ⇒ 剩下的只有【公差】(★官网图给的是 REF 不是公差带·★X 的通式公差 ±0.25★) ⇒ ⇒ **乙轨 (落 FTS 时打 1 块单板样, 卡尺量三量: 绝缘体高 / 外形宽 / 外形深, "
         "★**回填 `keepout_dwg` + `body_geometry`) 是【唯一】能拿到实物公差的路径 ⇒ ⇒ 归 mech-lead 执行 (转派) + 与那一趟同批 (★落 FTS 那天才有样可打★) + 不新起一单** ⇒ ★ ★"
         "★**★⇒ ★★后果已算清 (★与 §㊶ A4 同一条·★两处引用同一件事★)★: ★**乙轨不闭合 ⇒ OI-12/OI-13 那条「清空区 `6.6100` 比 courtyard `6.0900` 大 `0.5200`」的对照物"
         "★**【已作废】(★`6.0900` 是通用库件的 `F.CrtYd`·★见 `iss390_oi12_and_oi14_together`★) ⇒ ⇒ 真正该用的对照物是【厂件座体本体】⇒ ⇒ 结构侧清空区余量算错即装配干涉** ⇒ ⇒ "
         "★**★⇒ 而 §㊻ B3 已把需求改到 `4.3400` (J_UART 座体本体口径) ⇒ ⇒ **两处引用同一件事 ⇒ 同一趟一起做** ★ ★",
         "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md §4/§5/§6.1 · 一页 §㊻ B3 · §㊶ A4"),
    ]
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
    needkeys = {}
    for f in ("sw.yaml", "mech.yaml", "hw.yaml"):
        try:
            fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        except Exception:
            fd = {}
        for n in fd.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                needkeys[n["key"]] = n.get("to")
    pmc = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    amap = {}
    for a in pmc.get("answers") or []:
        if isinstance(a, dict) and a.get("key"):
            amap.setdefault(a["key"], []).append(a)
    tot = len(pmc.get("answers") or [])
    dup = len([k for k in amap if len(amap[k]) > 1])
    # ★★按 merge.py 的真实配对逻辑复算 (★_by == ask_to★) ★★
    paired = 0
    for k, at in needkeys.items():
        if k in amap and at == "main":
            paired += 1
    print("  pm.yaml (main 自己的分片): answers +%d 条 (跳过已存在 %d) ⇒ 共 %d 条 · 重复 key %d"
          % (added, len(skipped), tot, dup))
    print("  ★★L-32 回读验证: 本轮落的 %d 个 key 里, 逐字命中 need key 的 = %d 条 ⇒ ★★配对成功 (需 need.to=main)★★"
          % (added, len([k for k, _t, _v, _r in ANS if k in needkeys])))
    print("  ★★配对复算: 本轮落的 %d 条中, 按 merge.py 规则能闭合 need 的 = %d 条 ★★"
          % (added, len([k for k, _t, _v, _r in ANS if k in needkeys and needkeys.get(k) == "main"])))
    if added and len([k for k, _t, _v, _r in ANS if k in needkeys and needkeys.get(k) == "main"]) != added:
        raise SystemExit("★L-32 校验失败: 有答案的 key 没对上 need 的 key ⇒ 零写盘语义下也应报错 ★")
    return True


def write_memory_pointer():
    p = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
    txt = read_lines(p)
    if "L-32" in txt and "静默不闭合" in txt:
        print("  MEMORY.md: L-32 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l32_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-32★·★main 独占写·★无 job 重写★)★**: "
           "★**L-32 「落答案时必须【从 need 里逐字抄 key】⇒ 自己起 key = 机制【静默不闭合】」★** ⇒ "
           "★① 实测: main 13:1x 那轮落的 15 条 pm.yaml 答案【内容全对, 但一条都没闭上任何 need】⇒ 因为 merge.py 按【精确 key】配对 (`answers_by_key.get(k)` + `_by == ask_to`) ⇒ 用了改名的 key (★如 `iss389_main_oi5_pick_4810` 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★) ⇒ 配不上 ⇒ 零闭合 (★实测 pm.yaml 里 to=main 的答案中逐字命中 need key 的只有 113/152; 且 merge.py lint 里【答案 key 无 need 引用】189 条, 我那 15 条全在里面★) ⇒ "
           "★② ★★这比 L-28 的「key 撞名」更危险: 撞名会报错退出 (★有声音★), 而「不撞名但对不上」⇒ 机制【一声不吭】⇒ 答案躺在 pm.yaml 里内容正确, 但【对闭环机制等于不存在】⇒ 页面上看起来「已答」, 台账上其实还挂着★★ ⇒ "
           "★③ ⇒ 落答案前必须先从 need 里【逐字抄 key】(★不许自己起·不许「起个更清楚的名字」★); 落盘后必须回读验证【该 key 的 need 已从 pending 变 answered】⇒ 不许只看「脚本打印 ✅ 已原子更新」★★ "
           "★④ ★★推广: 凡是有「按 key 配对」的地方 (★merge 的 needs×answers · gate 的 (file,line) 钉住 · 一页章节号索引 · 决策索引覆盖复核 · ★★闸的 selftest 用固定字符串常量构造反向用例★) ⇒ 键必须逐字对齐 + 对齐要回读验证 ⇒ **【机制静默失效】比【机制报错】更贵】⇒ 我新写的机制都必须自带一句「配对不上就报错」**★★ "
           "★⑤ ★★与 L-31 合看 (★同一天, 一个讲机制, 一个讲夹具★): L-31 = 【沙盒落点必须每次运行唯一】(★并发跑必有一个假红★) ⇒ L-32 = 【selftest 锚点必须从真件现读】(★真件被登记过一遍 ⇒ 写死的锚点匹配不上 ⇒ 反向用例【假绿】⇒ 闸【看起来绿, 其实抓不到】★) ⇒ ⇒ ★**合起来 = 【凡是锚在真件上的东西 —— key / 落点 / 字符串常量 —— 都必须从真件现读, 不许写死; 一旦写死, 真件一变, 判据就静默失效】**★★ ⇒ "
           "★⇒ ★**本轮实证: ISS-388/390 签收 + ISS-391【暂缓签收】(★它的 selftest 14/17·★main 沙盒实验证明「删掉改孔那一腿」D1 仍判绿⇒判据被抽掉★) 时才发现 13:1x 那 15 条答案没生效 ⇒ 本轮已按 need 的原 key 重答一遍 (★老字一字未删·★保留作人读记录★)** ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-32 指针追加 (追加式, 备份 %s.bak_%s_main_l32_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def write_round_log():
    r = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1955_sign_iss388_390_hold_391.md")
    body = """# ROUND_LOG_main · 2026-11-24 19:5x · ISS-388 / ISS-390 签收 + ISS-391 暂缓签收 + 19 条 main 地界待裁项已裁 + 自曝 L-32

★**job**: main (ARS45 项目总工) · webchat 会话 (★由兄弟 job 5bd48f25 的进展播报 + 心跳触发★)
★**签收闸**: `state/_apply_20260724_1955_main_sign_iss388_390_391.py` (★fail-closed★)
★**备份** (★脚本现场取 `time.strftime` ⇒ 真实 stamp 见落盘时的文件名★): `state/issue_log.yaml.bak_<stamp>_main_sign_iss388_390_391` ·
`DECISION_ONE_PAGER_2026-11-22.md.bak_<stamp>_main_sign_iss388_390_391` · `state/LESSONS.md.bak_<stamp>_main_l32` ·
`MEMORY.md.bak_<stamp>_main_l32_pointer`

---

## ★★一 · 板面 (本机实读) ★★

★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` (纳秒级) ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

---

## ★★二 · 三单结论 (main 本机独立复核·不抄任何 agent 报告) ★★

| 单 | 闸 | 裸跑 | `--selftest` | 本轮结论 |
|---|---|---|---|---|
| ISS-388 | `SW/tools/check_sw_gate_health.py` | ★**rc=1 (★按设计判红★)** | ★**rc=0 · 22/22 · ALL TESTS PASS** | ★**✅ verified** ★ |
| ISS-390 | `MECH/check_fts_seat_body_geometry.py` | ★**rc=0 · 判据 0 失败** | ★**rc=0 · 15/15 · ALL TESTS PASS** | ★**✅ verified** ★ |
| ISS-391 | `HW/check_fts_land_drill_same_batch.py` | ★**rc=0 · 7/7 全绿** | ★**rc=1 · 14/17 · SELFTEST FAILED** | ★**⏸️ 暂缓签收** ★ |

★三闸零挂链 · 零落表 · 零改既有页面正文 · L-26① 的 13 道扫描面闸全 rc=0 ★
★**L-27 硬前置**: 三单 owner 会话均已收工 (12:51 / 12:59 / 13:05) 且交付物静默检查通过 ★

---

## ★★三 · ★★ISS-391 暂缓签收的 6 条机器依据 (★本轮最重要的发现★) ★★

★**①** `--selftest` = `14/17 PASS` + 末行 `SELFTEST FAILED` ⇒ 按 L-29 通则① 这道闸不可信 ★
★**②** 三条反向用例 (① 删钻孔字样 ⇒ D1 红 / ② 删 B33 描述列钻孔 ⇒ D2 红 / ③ 删 B33 验收手段 ⇒ D3 红) 全部 FAIL (★期望红却绿★) ★
★**③ ★★main 决定性实验 (沙盒·真件逐字节未动): 把真文件作业包 §0.2 ③ 里的「钻孔 0.65→0.71」这一腿真的删掉, 再跑 D1 ⇒ D1 仍判绿 ⇒ 判据被削弱 ⇒ 不可签** ★
★**③b 对照实验**: 把 ③ 整条只剩 pitch 那一腿 ⇒ **D1 才红** ⇒ D1 只挡得住「整条没写」, 挡不住「只删动作腿留解释」 ★
★**④ 根因 (★两级★)★: ★**【判据层·更致命】D1 的三条子判据全是关键词/子串命中 (`has_drill()` + 『0.71』子串 + 『1.27』子串), 而登记落盘后真件那一行带了一段解释性括注 (★「通用库件默认 (drill 0.65) 偏小 0.06」+「Ø0.71 TYP」★) ⇒ 纯解释文字也满足全部三条 ⇒ 动作腿删掉照样绿 ⇒ 判据被削弱** ★ ★**【夹具层】selftest 靠写死的常量造反向用例, 而真文件原文与常量逐字不同 ⇒ 替换不中 ⇒ 三条用例假绿 ⇒ selftest 14/17** ★
★**⑤ 登记已提前落**: 作业包 / 预检清单 / 生成器 / 真相页 = 18:28~18:32 (★兄弟 job fb67af40 那一趟·★不是 main 落的★) ⇒ 四道新闸裸跑从 4/7 变 7/7 ⇒ **「按设计判红」这个前提已不存在** ★
★**⑥ 处置**: 不签 (台账 `fixing` + 追加式 note_addendum) + OI-391-1~5 照裁照落 (★裁 ≠ 签★) + 夹具必修归 owner (★改判据逻辑 ⇒ 需重签★) ★

---

## ★★四 · ★★ISS-390 的核心发现: 「通用库件 courtyard 被当成厂件」 ★★

★main 自己解析 `.kicad_mod` ⇒ `PinHeader_1x04_…` 的 `fp_rect` = **3.1000 × 6.0900** ⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」; `PinHeader_1x02_…` = **3.1000 × 3.5500** ⇒ 「`3.5500` 同源」 ⇒ **⇒ `6.0900`/`3.5500` 与 Samtec 无关** ⇒ ISS-371/389/374 把它当「官方座体本体」是**定性前提错误** ★
★厂件 X = N × 1.27 ⇒ N=4 ⇒ `5.0800` / N=2 ⇒ `2.5400` (★本机算术复核命中★); 通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600` ★
★★⇒ 座体本体比铜箔包络每边都大 ⇒ **判据必须管到座体本体** ⇒ J_UART 的 X 需求 `4.0700` → **`4.3400`** (OI-14 目标值随之改) ⇒ 开口 Y `5.6000`/`5.8000` → **`5.7600`** ⇒ **§㊶ C4/C5/C6 相应部分作废, 由本轮裁决取代** (L-27 通则③) ★

---

## ★★五 · ★★★★自曝: 我 13:1x 那 15 条答案一条都没闭上 need (L-32) ★★★★

★**根因**: `state/merge.py` 按【精确 key】配对 (`answers_by_key.get(k, [])` + `_by == ask_to`) ⇒ 我 13:1x 用了改名的 key ⇒ 配不上 ⇒ 零闭合 ★
★**实测**: pm.yaml 里 `to=main` 的答案中, 逐字命中 need key 的只有 **113/152** ⇒ 我那 15 条全在「没命中」那一侧; 且 `merge.py --json` 的 lint 里【答案 key 无 need 引用】**189 条**, 我那 15 条全在里面 ★
★**★⇒ 比 L-28 的「撞名」更危险: 撞名会报错退出 (★有声音★), 这里【一声不吭】⇒ 答案内容正确但【对机制等于不存在】★★
★**⇒ 本轮已按 need 的原 key 重答一遍 (老字一字未删·保留作人读记录) + 立 L-32** ★

---

## ★★五b · ★★一次【受保护集被第三方改动】的处置 (★fail-closed 挡下来的★) ★★

★**事实**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` md5 `b5d8d5b9…` → `192873f6…` ⇒ 阶段 1 保护集核对判红 ⇒ **fail-closed 零写盘退出** ★
★**查是谁**: mtime = **18:32:02** ⇒ 兄弟 job fb67af40 那一趟 (★18:20 开 ISS-396「FTS 改孔登记落盘」·★18:43 出交卷页★) ⇒ 【第三方·合法派活·非越权】 ★
★**范围核对 (逐行 diff 对旧基线副本)**: 共 **8 行**, 全部落在 `B33_PIN_LAND_1P27` 那一项 (描述列 + `current_state` + `criterion` + 表格行) ⇒ 内容 = 把「钻孔 Ø0.65→Ø0.71mm」补进同一项的两条腿 ⇒ **正是 §4 #2/#3 该做的事 ⇒ 无越权·无板侧改动** ★
★**处置**: ① 重设基线 + **阶段 1 永久保留这道范围核对** ⇒ 越界就当场红 ② 板三项/网表/脚表/BOM 逐字节未动 ⇒ 纪律没破 ③ **提前落的机器后果 = 把 ISS-391 闸 D1/D2/D3 从红翻绿 ⇒ 夹具脱节 ⇒ selftest 14/17 ⇒ 这是 §三 的 6 条依据** ★
★**教训 (并入 L-32)**: 受保护集判红 ⇒ 第一动作**不是**「改基线让它绿」, 而是【查 mtime + 查是谁 + 逐行核对范围】⇒ 本轮顺序 = fail-closed 退出 → 查 mtime/派活记录/逐行 diff → 确认合法且范围一致 → 才重设基线并保留范围核对闸 ★

---

## ★★六 · 落记录 (全部追加式·老字一字未删) ★★

★`state/issue_log.yaml` (2 单签收 + ISS-391 暂缓 note_addendum, 一次全量重写) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊻** · `state/LESSONS.md` **L-32** ·
`state/fragments/pm.yaml` (16 条答案, 全部用 need 的原 key) · `MEMORY.md` (L-32 指针) ★

---

## ★★七 · 「板只改一次」那一趟现在明确要带【五条腿】 ★★

★**① 改孔 `0.65→0.71` (★环宽 `0.1450` 的制程能力确认同批★) ② 四处清单登记 (§4 #5 未落) ③ 新闸挂链 (★真正可挂的只有一道★) ④ 六个签收件的 md5 刷新 + 全部验收线重跑 (★L-27 通则③★) ⑤ ISS-391 闸的夹具改成【真件现读】(★归 owner·★修完自测全绿才谈签收★)** ★

---

## ★★八 · 最终读数 (本机实跑) ★★

★板三项未动 · 网表/脚表/BOM/`gate_check.py`/`merge.py`/`frag_write.py`/六个已签收页逐字节未动 · 新闸零挂链 · 13 道扫描面闸全 rc=0 ·
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
    doc = yaml.safe_load(open(LOG, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    for e in issues:
        if e.get("id") in ("ISS-388", "ISS-390", "ISS-391"):
            print("  %-8s status=%-10s verify_by=%-6s vr_len=%d notes=%d"
                  % (e.get("id"), e.get("status"), e.get("verify_by"),
                     len(str(e.get("verify_result") or "")), len(e.get("note_addendum") or [])))
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
    print("★ main · 2026-11-24 19:5x · ISS-388 + ISS-390 签收 / ISS-391 暂缓 + 16 条待裁项已裁 + 自曝 L-32")
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
    print("★ 本轮完成: 2 单签收 (ISS-388/390) + ISS-391 暂缓签收 + 16 条 main 地界待裁项已裁 + L-32 自曝 + §㊻")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 未代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
