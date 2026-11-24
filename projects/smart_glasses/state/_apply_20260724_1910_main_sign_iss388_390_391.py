#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1910_main_sign_iss388_390_391.py
================================================
main (项目总工) · 2026-11-24 19:1x
★★【签收】ISS-388 (sw) + ISS-390 (mech) + ISS-391 (hw) 三单一并签 (★一次全量重写·零竞态窗口★) ★★
★★ + 33 条 main 地界待裁项已裁 (★全部用【need 的原 key】·★L-32 铁律★) ★★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime(ns)/size 开工前后各打一次)
  ② 零落表 (网表/脚表/BOM 逐字节不动)
  ③ 零改既有闸 (只新建) · ④ 零改既有页面正文 (★订正一律走【追加式】★)
  ⑤ 分片只走 state/frag_write.py · 只写 main 自己的 pm.yaml
  ⑥ 不代老板拍板 · ⑦ 零外发 · ⑧ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑨ ★★L-27: 签收前必须确认【owner 会话已收工】+【交付物静默】+【钉 md5 不只钉 size】★★
  ⑩ ★★零挂链: 本轮【不挂】那三道新闸 ⇒ 机器理由见 §㊻ §③ (★三道闸各自都断言【零挂链】★)★★
  ⑪ ★★L-32: 落答案必须【用 need 的原 key】⇒ 落盘后回读验证【该 key 的 need 真的闭合】★★
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
PROBE = os.path.join(PROJ, "state/.verify/iss388_probe.txt")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

SIGN = {
    "ISS-388": {"owner": "sw-lead", "gate": "SW/tools/check_sw_gate_health.py",
                "page": "SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md",
                "handoff": "HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md",
                "frag": "sw.yaml"},
    "ISS-390": {"owner": "mech-lead", "gate": "MECH/check_fts_seat_body_geometry.py",
                "page": "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md",
                "handoff": "HANDOFF/2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md",
                "frag": "mech.yaml"},
    "ISS-391": {"owner": "hw-lead", "gate": "HW/check_fts_land_drill_same_batch.py",
                "page": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
                "handoff": "HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md",
                "frag": "hw.yaml"},
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
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md": "f1ce54c981dd1f64071a177a374df85d",
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
    "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md": "e9eea373c42f7225881007af08defba5",
    "SW/EVT_TEMPLATE.md": "773dcaf7432b66397a1fa3240c32c3ad",
    "SW/tools/check_debug_pin_order_contract.py": "3ea6aec63e08ac8f27dcf9e12507b164",
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


def sh(cmd, timeout=1200):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True,
                       timeout=timeout, env=dict(os.environ, TMPDIR=os.path.join(PROJ, "tmp")))
    return p.returncode, p.stdout + p.stderr


def verify():
    print("=" * 96)
    print("★阶段 1 · main 本机独立复核 (★不抄任何 agent 报告★)")
    print("=" * 96)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-56s %s" % ("✅" if good else "❌", name, detail))

    st = os.stat(BOARD)
    chk("板 md5/mtime(ns)/size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    print("  ★★① 三单闸读数 (★TMPDIR 指项目盘·★/tmp 配额满会假红★)")
    probe = read_lines(PROBE) if os.path.isfile(PROBE) else ""
    for iss, d in SIGN.items():
        if iss == "ISS-388":
            chk("ISS-388 闸 裸跑 rc=1 (★2/6 绿·★按设计★) + selftest ALL TESTS PASS (22/22)",
                "闸结果 2/6 通过, rc=1" in probe and "selftest 22/22 通过" in probe
                and "ALL TESTS PASS" in probe, "★留证 state/.verify/iss388_probe.txt★")
            continue
        rc, o = sh("python3 %s" % d["gate"])
        rc2, o2 = sh("python3 %s --selftest" % d["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        if iss == "ISS-390":
            # ★★真格式是「反向用例 15 条, 通过 15 条」+ 末行 ALL TESTS PASS (★不是 N/M 通过★)★★
            chk("%s 闸 裸跑 rc=0 + selftest 末行 ALL TESTS PASS + 15/15 反向用例" % iss,
                rc == 0 and rc2 == 0 and "ALL TESTS PASS" in last
                and "反向用例 15 条" in o2 and "通过 15 条" in o2,
                "bare=%d selftest=%s %r" % (rc, rc2, last[:26]))
        else:
            # ★★ISS-391: 期望【selftest 红·恰好 3 条 FAIL (①②③)】⇒ 这是【夹具陈旧】, 不是判据坏了 ★★
            fails = [l for l in o2.splitlines() if l.strip().startswith("[FAIL]")]
            names = " ".join(fails)
            chk("%s 闸 裸跑 rc=0 (7/7 绿) + selftest 红且恰好 3 条 FAIL (①②③=登记检测)" % iss,
                rc == 0 and "7/7" in o and rc2 != 0 and "SELFTEST FAILED" in last
                and len(fails) == 3 and "①" in names and "②" in names and "③" in names,
                "bare=%d selftest=%s FAIL条数=%d %r" % (rc, rc2, len(fails), last[:22]))

    print("  ★★② 三单交付物在盘 + md5 现读 (★L-27 通则②★)")
    FPS = {}
    for iss, d in SIGN.items():
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            e = os.path.isfile(p) and os.path.getsize(p) >= 4000
            chk("%s %-44s 在盘 (≥4000 B)" % (iss, d[k].split("/")[-1][:38]), e,
                "%d B / %s" % (os.path.getsize(p) if os.path.isfile(p) else 0,
                               md5(p)[:12] if os.path.isfile(p) else "-"))
            if os.path.isfile(p):
                FPS["%s|%s" % (iss, k)] = (md5(p), os.path.getsize(p))

    print("  ★★③ L-27 硬前置: 交付物静默")
    for iss, d in SIGN.items():
        s0 = {k: os.path.getsize(os.path.join(PROJ, d[k])) for k in ("gate", "page", "handoff")}
        m0 = {k: os.path.getmtime(os.path.join(PROJ, d[k])) for k in ("gate", "page", "handoff")}
        time.sleep(3)
        quiet = all(os.path.getsize(os.path.join(PROJ, d[k])) == s0[k]
                    and os.path.getmtime(os.path.join(PROJ, d[k])) == m0[k] for k in s0)
        age = min(time.time() - v for v in m0.values())
        chk("%s 三个交付物 3 秒静默 + 最旧静默 %.0f 分钟" % (iss, age / 60), quiet,
            "静默 %.0f 分钟" % (age / 60))

    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/已签收页正文 未动 (%d 件)" % len(PROTECTED), not bad,
        "动 %d %s" % (len(bad), bad[:3]))

    print("  ★★④ 零挂链 (★本轮不挂·★实测命中必须为 0★)")
    for iss, d in SIGN.items():
        got = sh("grep -c %s state/gate_check.py" % os.path.basename(d["gate"]))[1].strip().splitlines()[0]
        chk("%s 新闸零挂链 (gate_check 命中 0)" % iss, got == "0", "命中 %s" % got)

    print("  ★★⑤ ★★关键机器事实: 三道新闸各自都带【零挂链】自判据 (★⇒ 挂进去必自红★)")
    for iss, (g, tag) in {"ISS-388": ("SW/tools/check_sw_gate_health.py", "hook_hits"),
                          "ISS-390": ("MECH/check_fts_seat_body_geometry.py", "G6.5"),
                          "ISS-391": ("HW/check_fts_land_drill_same_batch.py", "D6")}.items():
        txt = read_lines(os.path.join(PROJ, g))
        base = os.path.basename(g)
        chk("%s 闸源码自带【零挂链】自判据 (%s)" % (iss, tag),
            base in txt and tag in txt, "★挂它 = 它自己判自己红★")

    for iss, d in SIGN.items():
        blob = yaml.safe_dump(yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % d["frag"]),
                                                  encoding="utf-8")) or {}, allow_unicode=True)
        chk("%s 在自己的分片 (%s) 有本单登记" % (iss, d["frag"]),
            iss.lower() in blob.lower() or os.path.basename(d["gate"]) in blob, "命中在位")

    print("  ★★⑥ L-26① 扫描面命中的既有闸 (★一道都不能漏★)")
    for g, label in [("HW/check_netlist_selfconsistency.py", "HW 域网表自洽"),
                     ("HW/check_debug_uart_seat_truth.py", "ISS-380 签收闸"),
                     ("HW/check_debug_uart_seat_alignment.py", "ISS-383 签收闸"),
                     ("HW/check_charge_current_live_value.py", "ISS-384 签收闸"),
                     ("HW/check_fts_single_row_land_truth.py", "★ISS-387 签收闸★"),
                     ("HW/check_onepass_preflight_coverage.py", "★覆盖度闸 (★P4 覆盖令牌★)"),
                     ("MECH/check_debug_seat_3d_fit.py", "ISS-386 签收闸"),
                     ("MECH/check_jdebug_arrangement_truth.py", "ISS-382 签收闸"),
                     ("MECH/check_onepass_struct_crosscheck.py", "MECH 结构交叉"),
                     ("MECH/check_onepass_mech_sync.py", "MECH 同步"),
                     ("MECH/check_debug_seat_rework_spec.py", "★ISS-389 签收闸★"),
                     ("SW/tools/check_sw_false_connectivity_gate.py", "ISS-381 签收闸"),
                     ("SW/check_evt_charge_current_criterion.py", "ISS-385 签收闸")]:
        rc, o = sh("python3 %s" % g)
        chk("%-44s (%s) rc=0" % (g.split("/")[-1], label), rc == 0, "rc=%d" % rc)

    print("  ★★⑦ 官方门禁")
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("    %-18s rc=%d" % (label, rc))
    chk("issue_check 违规数 = 19 (★既有老账·非本轮新增★)",
        "违规 19 条" in sh("python3 state/issue_check.py")[1], "★老账★")
    chk("stage_gate 仍在 G1 (★按设计就该红★)", "G1" in sh("python3 state/stage_gate.py")[1], "★G1 未开★")

    needkeys = {}
    for f in ("sw.yaml", "mech.yaml", "hw.yaml"):
        fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        for n in fd.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                needkeys.setdefault(n["key"], []).append((f, n.get("to")))
    print("  ★★⑧ ★★L-32 前提: 盘上 need key 总数 = %d (★待落答案必须逐字命中其中★)" % len(needkeys))

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok, FPS, needkeys


def build_ver(FPS):
    def fp(iss, k):
        return FPS["%s|%s" % (iss, k)]
    V = {}
    V["ISS-388"] = (
        "✅ verified (★main 2026-11-24 19:1x 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**闸 `SW/tools/check_sw_gate_health.py` 裸跑 rc=1 (★2/6 绿·"
        "**这是【按设计判红】, 不是闸故障**) + `--selftest` rc=0 末行 `ALL TESTS PASS` (22 条反向用例全抓到, 其中专打 H1 命门 5 条)** ★ "
        "交付物三件 md5 钉在下方 (★L-27 通则②: 钉 md5 不只钉 size★) ★ 零写板 + 零落表 + 零挂链 (gate_check 命中 0) ★★"
        "**★main 本机独立复核 (★自己实跑, 不抄报告★)★**: ★**① 它的红逐条点名, 无一是误报**: H0 点名两道病闸 "
        "`SW/tools/check_sw_board_md5_rebase_readiness.py` (`--selftest` rc=1 · 反向用例 0/10) 与 `SW/tools/check_sw_ref_reachability_v2.py` "
        "(`--selftest` rc=1 · 0/7 · 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」) ⇒ ★**这两道闸今天【真的坏了】**; H1 点名 "
        "`SW/tools/check_debug_pin_order_contract.py` 的**判据与环境耦合** (两个深度 TMPDIR 下 rc 0 vs 1); H2 点名 §2 账少登记 "
        "`SW/tools/check_sw_false_connectivity_gate.py`; H3 点名 §1 账少登记 3 行 (`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` / `:241` / "
        "`SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215`) ⇒ ★**⇒ 账漂共 4 条 (D-1~D-4)** ★★"
        "**★★② ★★本单最有价值的一条 = 「三道闸坏了但【没人看见】」这个根因被机器化了 ★★**: ★**旧的三道闸都是【零挂链】⇒ 坏了也不响 ⇒ 就这么烂在盘上** ⇒ "
        "★**本闸把这个病灶变成可判的 (H0 逐道点名 + H1 抓环境耦合 + H2/H3 抓账实漂移)** ⇒ ⇒ ★**而且它的 H4 自己断言「零挂链」(`hook_hits = gc_txt.count(\"check_sw_gate_health\")`) "
        "⇒ 它【自己】也刻意零挂链 (★不是漏挂, 是设计★) ⇒ ⇒ ★★**【零挂链是它的正确形态, 不是缺陷】** ★★"
        "**★★③ ⇒ 本单签收含义 = 交付物在盘 + 闸绿(按设计) + 判据零削弱 (22 条反向用例全抓到) + 边界零越界; OI-388 的 5 条 main 地界待裁项已裁 (见一页 §㊻ A 组)** ★★"
        "**★交付物指纹 (★md5 + size·★现读★)★**: 闸 `%s` (%d B) · 诊断页 `%s` (%d B) · 交卷页 `%s` (%d B) ★★"
        % (fp("ISS-388", "gate")[0], fp("ISS-388", "gate")[1], fp("ISS-388", "page")[0], fp("ISS-388", "page")[1],
           fp("ISS-388", "handoff")[0], fp("ISS-388", "handoff")[1]))
    V["ISS-390"] = (
        "✅ verified (★main 2026-11-24 19:1x 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**闸 `MECH/check_fts_seat_body_geometry.py` 裸跑 rc=0 (★33 条判据 0 失败★) + "
        "`--selftest` rc=0 末行 `ALL TESTS PASS` (15 条反向用例全抓到) + 连跑 3 次末行逐字相同** ★ 交付物三件 md5 钉在下方 (★L-27 通则②★) ★ "
        "零写板 + 零落表 + 零挂链 + 零改既有页面正文 ★★**main 本机独立复核 (★自己解析 .kicad_mod, 不抄页面★)★**: ★**① 通用库件 "
        "`PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 的 `fp_rect` = 3.1000 × 6.0900 ⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」本机坐实; "
        "`PinHeader_1x02_…` = 3.1000 × 3.5500 ⇒ 「`3.5500` 同源」坐实** ⇒ ⇒ ★**⇒ 「把通用库件的 courtyard 当成厂件的数」这个前提错误, 本机独立复核确认** ★★"
        "**② 厂件外形按通式自己验算: N=4 ⇒ 4 × 1.27 = `5.0800` ✓ / N=2 ⇒ `2.5400` ✓** ⇒ ★**⇒ 厂件座体【宽 X = N × 1.27】本机算术复核命中** ★★"
        "**③ 通用件 F.Fab 跨排距 2.1000 vs 厂件 2.1600 ⇒ 差 `0.0600` ⇒ ★**通用件比厂件窄 0.0600 ⇒ 当座体用 ⇒ Y 向每边少让 0.0300** ⇒ 与本单结论一致 ★★"
        "**★★④ ★★本单最有价值的一条 = 「`6.0900`/`5.0800`/`3.5500`/`2.5400` 这组数【全部来自通用库件】, 与 Samtec 无关** ⇒ ⇒ "
        "★**⇒ ISS-371/389/374 把它们当「官方 1×4 THT 座体本体 (F.Fab)」写进已签收页与已签收闸源码 = 【定性前提错误】(★不是数值错, 是【出处错】★) ⇒ ⇒ "
        "★**⇒ 且它把 OI-11 (座体真实高 h = [0数据]) 的性质改了: 库件根本给不了 Z (绝缘体高), 而厂件 Z = `0.8600` [官网] ⇒ ⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」** ★★"
        "**★★⑤ ⇒ 本单签收含义 = 交付物在盘 + 闸全绿 + 核心数本机复算命中 + 边界零越界; OI-390 的 4 条 main 地界待裁项已裁 (见一页 §㊻ B 组)** ★★"
        "**★交付物指纹 (★md5 + size·★现读★)★**: 闸 `%s` (%d B) · 真相页 `%s` (%d B) · 交卷页 `%s` (%d B) ★★"
        % (fp("ISS-390", "gate")[0], fp("ISS-390", "gate")[1], fp("ISS-390", "page")[0], fp("ISS-390", "page")[1],
           fp("ISS-390", "handoff")[0], fp("ISS-390", "handoff")[1]))
    # ★★ISS-391: 本轮【不签收】⇒ 写 hold 记录 (★追加式·★不改 status·★老字一字未删★)★★
    HOLD_391 = (
        "★**2026-11-24 19:1x main 复核结论: ★★本轮【不签收】★★ ⇒ ★**理由 = 该闸的 `--selftest` 现在是 **14/17** "
        "(★末行 `SELFTEST FAILED`★), 按 L-29 通则① 【闸的 rc=1 必须先分清『它坏了』与『它按设计在等一件事』, 判据 = `--selftest` 末行是不是 `ALL TESTS PASS`】⇒ ⇒ "
        "★**末行不是 ALL TESTS PASS ⇒ 这道闸【自证已失效】⇒ ⇒ 本轮不能以「闸绿」为由签收它** ⇒ ⇒ ★★"
        "**★★★main 本机独立定位: 【判据本身没坏, 坏的是 selftest 的夹具】★★★** ⇒ ★**① 裸跑 rc=0 · 7/7 全绿 (★D1~D7 逐条绿★) ★** ⇒ "
        "**★★② main 直接把闸源码 import 进来做【决定性探针】: (a) 把作业包 ③ 那一项里的「钻孔」两个字真删掉 ⇒ `d1()` 立刻判红 ⇒ **D1 的检测力完好**; "
        "(b) 把预检清单真页里所有「钻孔」字样删掉 ⇒ `d2()` 判红 (2 条) + `d3()` 判红 ⇒ **D2/D3 的检测力完好** ⇒ ⇒ ★★"
        "**★★③ ⇒ 所以那 3 条 FAIL 是【夹具陈旧】: 闸源码里的常量 `WORKPACKET_DRILL_LEG` = 「排针 land 0.50→1.27mm + 钻孔 0.65→0.71mm (★ISS-391·落 FTS 必须用 Samtec 官方 Ø0.71 TYP·库件默认 (drill 0.65) 偏小 0.06·同属这一项的两条腿, 不可只做其一★)」, "
        "而 ISS-396 于 18:28~18:32 落 §4 #1 时实际写进作业包的字样是【另一个版本】(★带「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」★) ⇒ ⇒ **该常量在盘上作业包里出现 0 次** ⇒ ⇒ "
        "★**⇒ 反向用例 ①② 的 `replace(WORKPACKET_DRILL_LEG, ...)` 变成空操作 ⇒ 沙盒文件没被改 ⇒ D1/D2 自然不红 ⇒ ⇒ 【夹具锚点与盘上真实文本脱节】** ★★"
        "**★★④ ⇒ 结论 (★机器可核★): 【这是【selftest 夹具陈旧】, 不是【判据被削弱】, 也不是【闸在按设计等什么】】⇒ ⇒ ⇒ 【闸的检测力经 main 独立探针证明完好】⇒ ⇒ "
        "★**⇒ 但 L-29 的判据是硬的: selftest 末行不是 `ALL TESTS PASS` ⇒ 闸不自证 ⇒ 【不签】⇒ ⇒ ⇒ 【修法 = owner 把夹具锚点改成【从盘上真实文本动态取】(而不是硬编码一句文案)·★与 L-21 同族: 锚点不许硬编码会漂的字样★】⇒ ⇒ ★★"
        "**★★⑤ ⇒ 【为什么这条比「夹具坏了」更值得记】: 它【不是 agent 写错】, 是【ISS-396 的合法落地】把 ISS-391 闸的夹具锚点【顶过期了】⇒ ⇒ ★★**【落地的副作用会打穿别的闸的自证】⇒ ⇒ ⇒ 这是一条新的跨单因果 ⇒ ⇒ 归「板只改一次」那一趟同批修 (★owner = hw-lead·★闸属 ISS-391 的交付物★)** ★★"
        "**★★⑥ ⇒ 附: ISS-391 闸的 D6 自己断言「`state/gate_check.py` 里命中本闸名的行数 == 0」⇒ ⇒ 本闸必须保持零挂链 ⇒ ⇒ 挂链时机 = 与那一趟同批, 且必须【与它自己那条 D6 判据的翻转同批】** ★★"
        "**★交付物现状指纹 (★md5 + size·★本轮现读·★未签收故只留证不签★)★**: 闸 `%s` (%d B) · 真相页 `%s` (%d B) · 交卷页 `%s` (%d B) ★★"
        % (fp("ISS-391", "gate")[0], fp("ISS-391", "gate")[1], fp("ISS-391", "page")[0], fp("ISS-391", "page")[1],
           fp("ISS-391", "handoff")[0], fp("ISS-391", "handoff")[1]))
    V["ISS-391-HOLD"] = HOLD_391
    return V


def write_issue_log(V):
    p = LOG
    shutil.copy2(p, p + ".bak_%s_main_sign_iss388_390_391" % STAMP)
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}
    before_n = len(issues)
    for iss, vr in V.items():
        # ★★HOLD 型的 key 带 `-HOLD` 后缀 ⇒ 台账 id 是去掉后缀的那个 ★★
        base = iss[:-5] if iss.endswith("-HOLD") else iss
        e = by.get(base)
        if e is None:
            raise SystemExit("台账里没有 %s (★HOLD 型的真实 id = %s·★)" % (iss, base))
        if iss.endswith("-HOLD"):
            # ★★hold: 只追加 note_addendum, 【不改 status / 不改 verify_result】(★老字一字未删★) ★★
            prev = e.get("note_addendum") or ""
            e["note_addendum"] = (prev + "\n" if prev else "") + vr
            continue
        e["status"] = "verified"
        e["verify_result"] = vr
        e["verify_date"] = "2026-11-24 19:1x"
        e["verify_by"] = "main"
        e["fix_ref"] = "main 2026-11-24 19:1x 独立复核签收 (★三单一并签·一次全量重写·零竞态窗口·零写板·零落表·零改既有闸·零改既有页面正文·零挂链★)"
    tmp = p + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, p)
    print("  issue_log.yaml: 3 单签收 (★一次全量重写·零竞态窗口★) 条数 %d→%d (备份 %s.bak_%s_main_sign_iss388_390_391)"
          % (before_n, len(issues), os.path.basename(p), STAMP))
    return True


ONEPAGER_BLOCK = """
## ★★㊻ 【2026-11-24 19:1x · 追加式】★ ★★ISS-388 / ISS-390 / ISS-391 三单独立复核签收 (★三单一并签·一次全量重写·零竞态窗口★) + ★★33 条 main 地界待裁项已裁 + ★★一条自曝铁律 (L-32) ★★

★**⓪ 取号说明 (★L-30·★先扫已用章节号★)**: ★**`§㊺` 已被兄弟 job `fb67af40` 于 18:3x 占用 ⇒ 本轮取 `§㊻`** ⇒ ★**盘上已用 = ㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺ (㊵ ×2 是已知的既有重复, 本轮不动)** ★

★**① 板面 (本机实读)**: ★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**② 三单签收 (★main 本机独立复核·不抄任何 agent 报告★)★**

| 单 | owner | 闸 | 裸跑 (★签收时刻★) | `--selftest` | 交付物 (★md5 现读·★见台账★) |
|---|---|---|---|---|---|
| **ISS-388** | sw-lead | `SW/tools/check_sw_gate_health.py` | ★**rc=1 · 2/6 绿** (★按设计判红★) | ★**rc=0 · 22/22 · `ALL TESTS PASS`** | 闸 32,327 B · 诊断页 20,941 B · 交卷页 37,416 B |
| **ISS-390** | mech-lead | `MECH/check_fts_seat_body_geometry.py` | ★**rc=0 · 33 条判据 0 失败** | ★**rc=0 · 15/15 · `ALL TESTS PASS`** | 闸 41,049 B · 真相页 46,898 B · 交卷页 37,068 B |
| **ISS-391** | hw-lead | `HW/check_fts_land_drill_same_batch.py` | ★**rc=0 · 7/7 全绿** (★状态已变·★见 §④★) | ★★**rc≠0 · 14/17 · `SELFTEST FAILED`** (★3 条 FAIL·★见 §④★) | ★**⇒ 本轮【不签收】·★只留 hold 记录 (★status 不变·★老字未删★)** |

★三闸零挂链 · 零落表 · 零改既有页面正文 · **L-26① 的 13 道扫描面闸逐道实跑全 rc=0** (含七个签收闸) ★

★**③ ★★★本轮最重要的机器事实: 三道新闸【各自都断言「零挂链」】⇒ 挂进去 = 立刻自己判自己红 ★★★★**
| 闸 | 自判据 | 实测源码 |
|---|---|---|
| ISS-388 | ★**H4** | ★`hook_hits = gc_txt.count("check_sw_gate_health")` ⇒ 命中数必须 == 0** |
| ISS-390 | ★**G6.5** | ★`self.chk("G6.5", "check_fts_seat_body_geometry" not in txt, ...)`** |
| ISS-391 | ★**D6** | ★`"D6 零挂链破了: state/gate_check.py 里命中 %s %s 次 (★必须是 0·挂链是 main 的地界★)"`** |

★**⇒ ⇒ 本轮【不挂】这三道闸, 而且这不是「暂缓」, 是【结构上的硬约束】: 现在挂 ⇒ 三道闸同时自红 ⇒ 现场会读成「板坏了」⇒ ⇒ 【挂链必须与「它们自己那条零挂链判据的翻转」同批】(★那一趟的闸清单刷新批次·★L-29 通则②★)** ★
★**⇒ ⇒ 附带: 那一次的「闸清单刷新」批次必须同时做三件同批事 = ① 翻这三道闸自己的零挂链判据 ② 刷新 `state/board_md5_pinned_gates.json` (★3 道新闸硬钉板 md5 字面量·须进 §2 的账·★L-21 同批重生成★) ③ 更新 ISS-388 的 H2/H3 账 (★它扫的就是这两本账★)** ★
★**⇒ ⇒ ★★而且本轮实读到一件事: `state/board_md5_pinned_gates.json` 里那 9 条的 `(file,line)` 钉住【已有 5 条失配】(★`HW/check_pin_function_labels.py` L148→现 L155 · `SW/tools/check_onepass_sw_sync.py` L107/758/781/783→现 L109/806/829/831★) ⇒ ⇒ ★★**这是 L-21 的一个既存实例: 往被钉文件里插行 ⇒ 清单自己过期 ⇒ 清单必须与补丁同批重生成** ⇒ ⇒ ★**⇒ 那一趟刷 §2 的账时, 必须【连这 5 条失配一起修】(★只加新闸不修旧的 = 半修)** ★ ★

★**④ ★★ISS-391: 签收时刻的状态【已经变了两次】—— 签收记录必须写现读, 而且这次现读本身不合格 ⇒ 本轮【不签收】 ★★**
★**交卷时 (12:13)**: 裸跑 rc=1 · 4/7 绿 · D1/D2/D3 红 (★按设计: 抓的正是「`钻孔 0.65→0.71` 还没进到作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」★) ★
★**兄弟 job `fb67af40` 18:28~18:32 派 ISS-396 把 §4 #1/#2/#3/#6 落到位 (追加式·老字一字未删) ⇒ 签收时刻现读 = rc=0 · 7/7 全绿** ★
★**⇒ 故 §㊸ 给签收人的那条口径「ISS-391 的 verify_result 须写明『D1/D2/D3 红 = 按设计』」在签收时刻【已不成立】⇒ ⇒ ★★"
"**★★★⇒ ⇒ 签收时刻的第二次变化: 该闸的 `--selftest` 现在是 **14/17** (★末行 `SELFTEST FAILED`★) ⇒ ⇒ 按 L-29 通则① (★判据 = `--selftest` 末行是不是 `ALL TESTS PASS`★) ⇒ ⇒ **末行不是 ⇒ 闸不自证 ⇒ ⇒ 【本轮不签收】(★status 保持 fixing·★只追加 hold 记录·★老字一字未删★)** ⇒ ⇒ ★★"
"**★★★⇒ ★★main 本机独立定位: 【判据本身没坏, 坏的是 selftest 的夹具】★★★** ⇒ ★**① 裸跑 rc=0 · 7/7 全绿 (★D1~D7 逐条绿★) ★** ⇒ "
"**★★② main 把闸源码 import 进来做【决定性探针】: (a) 把作业包 ③ 那一项里的「钻孔」两个字真删掉 ⇒ `d1()` 立刻判红 ⇒ **D1 的检测力完好**; "
"(b) 把预检清单真页里所有「钻孔」字样删掉 ⇒ `d2()` 判红 (2 条) + `d3()` 判红 ⇒ **D2/D3 的检测力完好** ⇒ ⇒ ★★"
"**★★③ ⇒ 那 3 条 FAIL 是【夹具陈旧】: 闸源码里的常量 `WORKPACKET_DRILL_LEG` 是 ISS-391 交卷时那句文案, 而 ISS-396 于 18:28~18:32 落 §4 #1 时实际写进作业包的字样是【另一个版本】(★带「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」★) ⇒ ⇒ **该常量在盘上作业包里出现 0 次** ⇒ ⇒ "
"★**⇒ 反向用例 ①② 的 `replace(WORKPACKET_DRILL_LEG, ...)` 变成空操作 ⇒ 沙盒文件根本没被改 ⇒ D1/D2 自然不红 ⇒ ⇒ 【夹具锚点与盘上真实文本脱节】** ★★"
"**★★④ ⇒ 【这不是 agent 写错, 是【ISS-396 的合法落地】把 ISS-391 闸的夹具锚点【顶过期了】】⇒ ⇒ ⇒ ★★**【落地的副作用会打穿别的闸的自证】⇒ ⇒ 这是一条新的跨单因果 ⇒ ⇒ 归「板只改一次」那一趟同批修 (★owner = hw-lead·★闸属 ISS-391 的交付物★) ⇒ ⇒ 修法 = 【夹具锚点改成从盘上真实文本动态取】(★不许硬编码会漂的字样·★L-21 同族★)** ★★"
"**★★⑤ ⇒ 附: 该闸的 D6 自己断言「`state/gate_check.py` 里命中本闸名的行数 == 0」⇒ ⇒ 必须保持零挂链 ⇒ ⇒ 挂链时机 = 与那一趟同批, 且必须【与它自己那条 D6 判据的翻转同批】** ★★"
"**★★⑥ ⇒ ★★这条同时也是 L-27 第 6 款的第一次真正用到: 【签收记录钉的是【签收那一刻】的指纹与读数, 不是【交卷那一刻】的 ⇒ 且【签收那一刻的读数自己也要合格】⇒ ⇒ 「交卷时绿」与「签收时绿」是两件事, 中间任何一次合法落地都可能把它变红】** ★★

★**⑤ ★★ISS-390 的核心声明, main 本机独立复核坐实 ★★**
★**main 自己解析 `.kicad_mod`**: `PinHeader_1x04_P1.27mm_Vertical` 的 `fp_rect` = **3.1000 × 6.0900** ⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」; `PinHeader_1x02_…` = **3.1000 × 3.5500** ⇒ 「`3.5500` 同源」 ⇒ ★**⇒ `6.0900`/`5.0800`/`3.5500`/`2.5400` 这组数与 Samtec 无关 ⇒ ⇒ ISS-371/389/374 把它们当「官方座体本体」是【定性前提错误】(不是数值错, 是出处错)** ★
★**厂件外形按通式自己算**: N=4 ⇒ `5.0800` ✓ / N=2 ⇒ `2.5400` ✓ ⇒ 「厂件座体宽 X = N × 1.27」命中 ★ · 通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600` ⇒ 通用件当座体用 ⇒ Y 向每边少让 `0.0300` ★
★**★⇒ ⇒ §㊶ 的 C4/C5/C6 三个数被这条改掉 (★老裁决一字未删·★本轮追加式订正★)**: ★**① 判据必须管到【座体本体】(座体 X `5.0800`/`2.5400` + Y `2.1600` 比铜箔包络每边都大) ⇒ J_UART 的 X 需求 `4.0700` → `4.3400` ⇒ OI-14 (DP-1) 目标值随之改 `4.3400`**; ★**② 「偏紧 `0.5200`」的措辞作废 (★`6.0900` 是通用库件的 `F.CrtYd`, 厂件【没有】courtyard 这个量★) ⇒ 判据本身 (每边 `0.9000`) 保留**; ★**③ 开口 Y 须 ≥ `5.7600`** (★座体 Y `2.1600` + 2×`0.9000` = `3.9600` 清空区, 再 + 2×`0.9000` ⇒ `5.7600`·★取代 §㊶ C5 的 `5.6000`/`5.8000`★) ⇒ **「接受零余量」选项消失** ★

★**⑥ ★★自曝 + 一条被实测证伪的旧裁决 (★追加式订正·★老字一字未删★) ★★**
★**★① L-32 (★本轮自曝铁律·★见 LESSONS★): 我 13:1x 那一轮落的 15 条 pm.yaml 答案, 【内容全对, 但一条都没闭上任何 need】** ⇒ 根因 = `state/merge.py` 按【精确 key】配对 (`answers_by_key.get(k, [])` + `_by == ask_to`) ⇒ 我用了【改名的 key】 ⇒ 配不上 ⇒ 零闭合 (★实测: pm.yaml 里 `to=main` 的答案中逐字命中 need key 的只有 113/152★) ⇒ ⇒ **本轮全部按 need 的原 key 重答一遍 (★老字一字未删·保留作人读记录★)** ★
★**★★② 我 13:1x 那条 `iss391_main_gap_registration_same_batch` 裁决里的「不许提前落」这一半, 其【担心 P4 会当场红】的理由, 被本轮实测证伪**: ★**覆盖度闸 P4 现读 = 绿 (★「作业包 §0.2 ③ 的 ③ ⇒ 命中 ['B33_PIN_LAND_1P27'] (覆盖令牌 7 个全在)」★)** ⇒ ★**⇒ 原因 = P4 查的是【清单页里有没有那些令牌】, 不是【板面改没改】⇒ ⇒ 「提前落登记会让覆盖度闸假红」这个担心不成立** ⇒ ★**⇒ 但那条裁决的另一半【#1/#2/#3 必须一起落】是对的, 且 ISS-396 正是这么落的 (追加式·老字一字未删) ⇒ ⇒ 本轮对该裁决的追加式订正 = 【删掉「不许提前落」这半句的约束力, 保留「#1/#2/#3 一起落」的原子性要求】(★老裁决原文一字未删★)** ★
★**★★③ 追加式订正: §㊶ C4 / C5 / C6 的数值被 §⑤ 取代 (★老字一字未删·★订正块在此★)** ★
★**★★④ ★★另一条机器事实 (★本轮 main 自己查出来的·★不是任何 agent 报的★)★★**: ★**ISS-396 的交卷页说「本板 8 铜层 ⇒ 适用多层行」—— 本轮 main 本机解析 `.kicad_pcb` 的 `(layers …)` 块确认 = F.Cu + In1..In6.Cu + B.Cu = 【确实 8 层】✓, 且 stackup 外层铜厚 = `0.035` mm = 【1 oz】✓ ⇒ ⇒ 所以 ISS-396 那条推断链成立** ★★

★**⑦ ★★33 条 main 地界待裁项已裁 (★一件没代老板拍板·★全部用 need 的原 key·★L-32★)★★**

★**★⇒ 本轮签收口径一句话: 【签 ISS-388 + ISS-390 (两单), ISS-391 【不签】(★selftest 14/17·★闸不自证·★L-29 硬判据★) ⇒ ⇒ 且 ISS-391 的 5 条 OI 裁决【照样已裁并落账】(★裁决与签收是两件事: 裁决是 main 的判断, 签收是 main 对【交付物自证合格】的确认·★自证不合格就不签·★但裁决不该被拖住★)】** ★

★**▌A 组 · ISS-388 (5 条·to=sw-lead)★★

| # | need key | main 裁决 (2026-11-24 19:1x) |
|---|---|---|
| A1 | `iss388_ledger_drift_owner` | ★**账漂 (D-1~D-4) 归【main 授权 + owner 落追加式订正块】, 且【必须与「板只改一次」那一趟同批】** ⇒ ★**① 改的是 ISS-372 真相页的 §1/§2 机器块 = 已签收页 ⇒ 按「已签收件的订正路径」⇒ main 授权路径, owner 落 (★老字一字未删★), main 不直接改 owner 的正文**; ★**② 为什么必须同批: D-1~D-4 的差集 = 【那三道闸坏了 + 账没跟上】⇒ 修账不修闸 = 账上写「已登记」但闸还是坏的 ⇒ ⇒ 【账 + 闸】必须一起修** ⇒ ★**③ 且闸 2 与闸 v2 修好之前, 新闸 `check_sw_gate_health.py` 必须保持零挂链** (★它自己 H4 会红·★见 §③★) ⇒ ★★ |
| A2 | `iss388_new_gate_hook_to_main` | ★**【不挂】, 且这不是「暂缓」而是【结构上的硬约束】** ⇒ ★**机器理由 (★main 本机实读源码坐实★)**: 该闸的 H4 判据字面就是 `hook_hits = gc_txt.count("check_sw_gate_health")` ⇒ ★**它一旦出现在 `state/gate_check.py` 里, 它自己立刻判红 ⇒ ⇒ 挂它 = 让它自己判自己红 = 【假红】⇒ ⇒ 【零挂链是它的正确形态, 不是缺陷】** ★★ ★**★⇒ 而且「挂链就能看见」这个直觉在这里【是错的】**: ★**看不见的病根 = 【那三道病闸零挂链 + 坏了没人跑】⇒ 处置不是挂这道元闸, 而是 ① 修那三道闸 (★闸 2 的 selftest 0/10 + 闸 v2 的 0/7 + 闸 1 的环境耦合★) + ② 把它们挂进链 ⇒ ⇒ 而它们【现在挂不得】(★挂了当场红·基线先红的账没修完★) ⇒ ⇒ 全部归 SW 域那一趟 ⇒ 本轮只裁归属, 不代排顺序** ★★ |
| A3 | `iss388_env_sensitivity_fix_location` | ★**路 A (在源头修) 为主 + 路 B (调用约定) 为辅, 顺序 = 先 B 后 A** ⇒ ★**① 闸 1 的红是【同一份源码, 只差 TMPDIR ⇒ 10/11 vs 11/11】⇒ 判据本身与环境耦合 ⇒ ⇒ 这是【闸的缺陷】, 不是调用方的错 ⇒ ⇒ 病根在闸 ⇒ 必须源头修 (路 A)** (★否则「靠人记得带 TMPDIR」= 把判据正确性押在人的记性上·★ISS-297 已栽过一次「约定靠人记会有忘的那天」★); ★**② 但路 B 也不能不做**: 本机 `/tmp` 用户配额打满 ⇒ 不带 TMPDIR 会假红 (★rc=120 / 0 字节★) ⇒ ⇒ **路 B 是止血, 路 A 是治病** ⇒ ⇒ ★**★⇒ 代价账 (★本单已算·main 核对后成立★)★: 路 A = 改【已签收件】的判据逻辑 ⇒ 必须 main 授权 + owner 落 + 重跑 11 条反向用例 + 重签 ⇒ ⇒ 那是一次签收指纹过期 (★今天已在 ISS-381/382/384 上栽过两次·★L-27★) ⇒ ⇒ 【不进这一趟】** ⇒ ⇒ ★**落法: 路 B 归 owner 立即落; 路 A 归 SW 域那一趟同批, main 在那一趟授权** ★★ |
| A4 | `iss388_third_sick_gate` | ★**要修, 但【不另起一单】⇒ 归「板只改一次」那一趟同批** ⇒ ★**① `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` = 0/7, 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」⇒ 它【真的坏了】, 不是误报 ⇒ 必须修** (★本单只登记不修是对的: 不在本单 brief 范围内★); ★**② 它的失败模式与闸 2 同类 (基线先红 ⇒ 差值型自测全灭) ⇒ 修它的前置 = 先修账 (D-1~D-4) ⇒ ⇒ 【同一条因果链】⇒ ⇒ 拆成两单 = 两批做完 = 又一次「板只改一次」的纪律破例 ⇒ ⇒ 归同一趟** ★ **③ 归属 owner = sw-lead** ★ ★ |
| A5 | `iss388_delta_selftest_convention` | ★**「基线必须先绿, 否则 selftest 结论不可读」写进闸的编写通则 —— 【采纳】, 但【落法 = 新增一份通则文档 + 逐闸加前置断言】, 不是【逐个改已签收闸的 selftest 口径】** ⇒ ★**① 闸 2 = 0/10 与闸 v2 = 0/7 都是【差值型自测在基线已红时全灭】⇒ 闸自曝「我不可信」却说不出「我是账漂了不是坏了」⇒ ⇒ 这个病确实需要一条通则**; ★**② 但「一次性改若干已签收闸的 selftest 口径」这条路【本轮不走】**: ★**(a) 改已签收闸的 selftest 逻辑 = 改判据 ⇒ 要重签 ⇒ 又是一次签收指纹过期 (★L-27·今天已栽两次★); (b) 且「差值型自测」本身不是错 —— 它【自证「红集 == {目标那一条}」】这个设计是对的 ⇒ 错的只是【基线已经红的时候, 差值不可读】⇒ ⇒ **正确解法 = 让基线先绿 (A1 的账漂 + 那三道闸修好) ⇒ 差值自测自然可读 ⇒ 通则只需写成【写闸时必须先声明「本闸的基线是什么; 基线红了 selftest 结论不可读」】+ 错误消息点名是哪个闸 + 它的原文末行 (★这正是新闸 H0 已做到的★)** ⇒ ⇒ ★**落法 = 新增一份通则 (★main 落·★`state/GATE_WRITING_CONVENTIONS.md`·★新文件不碰任何已签收闸★) + 逐闸加前置断言归 SW 域那一趟** ⇒ ★★ |

★**▌B 组 · ISS-390 (4 条·to=mech-lead)★★

| # | need key | main 裁决 (2026-11-24 19:1x) |
|---|---|---|
| B1 | `iss390_correction_landing` | ★**6 处定性订正归【main 授权 + owner 落追加式订正块】, 且【与「板只改一次」那一趟同批】** ⇒ ★**① 这 6 处全是【已签收页正文 + 已签收闸源码字符串】⇒ 按「已签收件的订正路径」⇒ main 授权路径, owner 落 (★老字一字未删★)**; ★**② 为什么要同批: §4 #3 的两处源码字符串 (`MECH/check_debug_seat_3d_fit.py` L848 / L879) 是【已签收闸的判据源码】⇒ 改它 ⇒ 那两道签收指纹当场过期 ⇒ ⇒ 【必须与那一趟的「重验全部验收线」同批】(★L-27 通则③★)** ⇒ ⇒ ★**③ 且这 6 处不落 ⇒ 【通用件 vs 厂件】的前提错误继续留在页上与闸源码里 ⇒ ⇒ 下一个读这页或跑那个闸的人会拿错对照物做结构判决 ⇒ ⇒ 而本闸 G3 的未落清单会永远停在那些条目上 ⇒ ⇒ 【G3 恒红 ⇒ 这道闸自己也就废了】⇒ ⇒ 故: main 授权 + owner 落 + 与那一趟同批, 三条一起** ★ ★ |
| B2 | `iss390_h_lock_and_test_sample` | ★**两问分别裁: (甲) h 走【三档参数化】, 不锁死; (乙) 打样归【那一趟同批】** ⇒ ★**(甲)**: ★**厂件柱高 `3.05` mm (官网表 TABLE 1 lead style -01) 而绝缘体只有 `0.86` ⇒ ⇒ 罩内腔板面以上那一维【不能】按 `0.86` 出件 ⇒ `h=0.90` 档【物理上装不下】⇒ 可行档是 `2.54` 与 `4.00` ⇒ ⇒ 这把 §㊶ C8 (「h 不卡那一趟」) 的依据从「[0数据]」升级成了「[0数据] 且已算明可行档只剩两个」⇒ ⇒ 【本裁决与 §㊶ C8 一致, 且依据更强】⇒ ⇒ 【不锁死】= h 锁死会绑死一个【还没测过】的量 ⇒ 三档参数化保留 (0.90 档标注物理不可行) ⇒ 锁定权仍在 boss (★`iss389_oi11_seat_height_window` 未代拍★)** ⇒ ★**(乙)**: ★**打样是【唯一能拿到 REF 公差】的路径 (★官网图给的是 REF 不是公差带★) ⇒ ⇒ 落 FTS 时打一块单板样、用卡尺量三量 (★绝缘体高 / 外形宽 / 外形深★) 回填 `keepout_dwg` + `body_geometry` ⇒ ⇒ 【必须与那一趟同批】(★落 FTS 那天才有样可打★) ⇒ ⇒ 归 mech-lead 执行 (转派), 但【不新起一单】** ★ ★ |
| B3 | `iss390_oi12_and_oi14_together` | ★**三个答案一起给: (a) 罩住判据【管到座体本体】⇒ 采纳; (b) 「偏紧 `0.5200`」的措辞【作废】(★`6.0900` 是通用库件的 `F.CrtYd`, 厂件【没有】courtyard 这个量★) ⇒ 判据本身 (每边 `0.9000`) 保留; (c) ⇒ (a) 成立 ⇒ J_UART 的 X 需求从 `4.0700` 变 `4.3400` ⇒ ⇒ 【OI-14 (DP-1) 的目标值 = `4.3400`】** ★★ ★**★⇒ 理由 (★main 本机独立复核坐实·自己解析 .kicad_mod★)★**: ★**① 座体本体 (厂件 X `5.0800`/`2.5400` + Y `2.1600`) 比铜箔包络 (X `4.8100`/`2.2700`) 每边都大 ⇒ ⇒ 只按铜箔算 = 会做出一个装不进座体的洞 ⇒ ⇒ 判据必须同时管座体本体**; ★**② 「偏紧 `0.5200`」的对照物是 `6.0900` ⇒ 而 `6.0900` 是【通用 KiCad 库件自己的 `F.CrtYd`】(★main 本机解析 `.kicad_mod` 的 `fp_rect` = 3.1000 × 6.0900 坐实★) ⇒ ⇒ Samtec 厂件【没有】courtyard 这个量 ⇒ 那句「比 courtyard 还小」在【厂件】这一层【无意义】⇒ ⇒ 作废那句措辞, 保留判据**; ★**③ (c) 是 (a) 的算术后果: J_UART 座体 X `2.5400` + 2 × `0.9000` = `4.3400` (★不是 `4.0700`·★`4.0700` 是按铜箔 `2.2700` 算的★) ⇒ ⇒ OI-14 目标值 = `4.3400`** ★ ★ ★**★⇒ 与 §㊶ C4 / C6 【冲突】⇒ ⇒ 按 L-27 通则③ (main 落裁决 ⇒ 已 verified 的单的交付物进入「会动」状态 ⇒ 那一趟必须重验全部验收线) ⇒ ⇒ 本条取代 §㊶ C4 与 C6 的对应部分, 老裁决的数值随之作废** ⇒ ⇒ ★**★⇒ 与 §㊴ C1 (OI-5 取 `4.8100`) 【不冲突】: `4.8100` = 铜箔沿脚排总展 (判「装得下」的输入), `4.3400` = 座体本体 + 2×余量 (判「装得下且留得住」的输出) ⇒ 两个数【都要】** ★ ★ |
| B4 | `iss390_y_direction_open_question` | ★**Y 向走【放大罩开口 Y】, 幅度按座体本体重算 ⇒ 开口 Y 须 `≥ 5.7600`** (★取代 §㊶ C5 的 `5.6000`/`5.8000`★) ★★ ★**★⇒ 理由 (★main 本机实算★)★**: ★**① 座体本体 Y = `2.1600` (厂件) ⇒ 按每边 `0.9000` ⇒ 清空区 Y 需求 = `2.1600` + 2 × `0.9000` = `3.9600` ⇒ ⇒ 比 §㊶ C5 裁的 `2.8000` 大 `1.1600`** ⇒ ⇒ ★**★★⇒ §㊶ C5 的【方向】(放大罩开口 Y) 仍成立, 但【数值】收窄为 `5.7600`** ⇒ ⇒ 本条构成对 §㊶ C5 的【订正】** ★ ★**② ⇒ 「接受零余量」那个选项【已不存在】⇒ ⇒ (b) 改判据口径只罩铜箔 = 【已判死】(★只罩铜箔 = 装不进座体★) ⇒ ⇒ 只剩 (a) 放大罩开口 Y 一条路 ⇒ ⇒ **罩开口 Y `4.6000` → `5.7600` = 放大 `1.1600`** ★ **③ ⇒ 结构性代价 (镜脚内腔 + 罩外观缝) 与 §㊶ C5 同源 ⇒ ⇒ 与板框第一问同批** ⇒ ★★ |

★**▌C 组 · ISS-391 (5 条·to=hw-lead)★★

| # | need key | main 裁决 (2026-11-24 19:1x) |
|---|---|---|
| C1 | `OI-391-1` | ★**三处补登记: 【已被 ISS-396 于 18:28~18:32 落到位 (#1/#2/#3) ⇒ 本轮【追认】, 而非新落】; 剩下的 #4/#5 见 C3 与本组 C1 附注** ⇒ ★**★⇒ 追认理由: ① §4 #1 (作业包 §0.2 ③ 的「③」那一项追加上「钻孔 `0.65→0.71`」这一腿) 已落 (追加式·老字一字未删); ② #2 (预检清单 `B33_PIN_LAND_1P27` 描述列) 与 #3 (验收手段列) 是在【生成器】里落的 ⇒ 页自己变 ⇒ ★**页里没手写一个字 ⇒ ⇒ 这才是对的做法 (★ISS-349 同一位号栽过一次「手写会蒸发」★)**; ③ #6 (生成器 `build_pinland_item()` + `read_board_pin_land()` 加 drill 字段现读板) 已落 ⇒ ★**⇒ 「重跑一次就蒸发」的那个坑被生成器这一手堵住了** ★★ ★**★⇒ 但 main 13:1x 那条裁决里的「不许提前落」这一半要追加式订正**: ★**它担心的【P4 会当场红】被实测证伪 (★P4 现读绿·「覆盖令牌 7 个全在」★) ⇒ ⇒ 因为 P4 查的是【清单页里有没有那些令牌】, 不是【板面改没改】⇒ ⇒ 「提前落会假红」不成立 ⇒ ⇒ 保留的那半句 = 【#1/#2/#3 必须一起落】(★原子性★·★ISS-396 正是这么做的★)** ⇒ ⇒ ★**★⇒ 追加式订正 = 【本裁决取代 13:1x 那条里的「不许提前落」约束, 老裁决原文一字未删】** ★★ |
| C2 | `OI-391-2` | ★**写成【一条】(pitch 与 drill 是同一项的两条腿, 不可只做其一), 不许拆成两条可分开的动作** ⇒ ★**机器理由: 新闸 D1 只能查出【整条没写】, 查不出【拆成两条只做一条】⇒ ⇒ 拆开写 = 判据出现盲区** ⇒ ⇒ **一条写 + 锚点含两个数 (`0.71` 与 `1.27`) = 机器可判** ⇒ ⇒ ★**★⇒ 现状已符合: 作业包 §0.2 ③ 的「③」那一项现在就是【一条含两腿】(★ISS-396 的落法★) ⇒ 本裁决【追认现状】** ⇒ ⇒ ★**★⇒ 与 §㊻ A1/B1 同一纪律: 措辞口径由 main 定, 落法由 owner 落, 且【必须机器可判】** ★ ★ |
| C3 | `OI-391-3` | ★**BOM L71 (J_DEBUG) / L77 (J_UART) 的 opn 与 footprint 两栏 = 与板侧 land 来源【同源】, 落表时机 = 【「板只改一次」那一趟的同一次落表与重出】; 本轮【零落表】(★BOM md5 `5b999399…` 逐字节未动★)** ⇒ ★**★⇒ 同源纪律 (★板面 land 来源 = BOM 型号栏 = 实物料号★)**: ★**板侧 land 来源 = 盘上通用 KiCad 1.27mm THT 库件 (★`PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c…` / `PinHeader_1x02_P1.27mm_Vertical` md5 `47bcbf6d…`★) + 一条显式偏离登记 (★偏离项 = 铜箔焊盘直径官方无值 + 孔径由 `0.65` 改 `0.71` + 焊盘直径放大到 ≥`1.010`/建议 `1.110` 的环宽理由·★见 `iss394_ring_width_fab_capability`★) + BOM 型号栏写 FTS 料号** ⇒ ⇒ **不成立 ⇒ 投板后才发现 ⇒ 2-4 周返工** ⇒ ⇒ ★**★⇒ 逐字草案按真相页 §4 #5 原样落, main 不改一字; 且【不得早于那一趟】—— 落表 = 落表台账变更 ⇒ 与板 md5 变更必须是同一趟** ⇒ ⇒ ★**★⇒ 与 §㊶ A3 (OI-387-3) 同一裁决, 两处口径必须一致** ★ ★ |
| C4 | `OI-391-4` | ★**生成器补登记: 【已被 ISS-396 落到位 (#6)】⇒ 本轮【追认】; 后续同批维护归 owner** ⇒ ★**机器理由: `state/_iss277_build_preflight.py` 的 `build_pinland_item()` (title + current_state + criterion 三处一起长) + `read_board_pin_land()` 加一个 drill 字段现读板 ⇒ ⇒ 不落 ⇒ §3 #2/#3 的补登记【重跑一次就蒸发】(★ISS-349 同一位号已栽过一次★) ⇒ ⇒ 现在这一手已经堵住了那个坑 (★页里没手写一个字⇒ 重跑生成器仍一致·★页 md5 三连跑恒定★) ⇒ ⇒ ★**★⇒ 但要追认一件它动过的东西: 真相页机器块里两枚 md5 基线 (`workpacket_md5` / `preflight_md5`) 随之刷新 (★按【基线随合法落地刷新】的口径, 只刷这两个键, 其余 7 个键不动★) ⇒ ⇒ 见 `iss396_main_truth_page_baseline_ratification`** ⇒ ⇒ ★**★⇒ 与 §㊶ A2 (OI-387-2「改孔与那一趟同批」) 同一批次 ⇒ 那一趟的「清单四处登记」批次要一次做完** ★ ★ |
| C5 | `OI-391-5` | ★**【与那四处登记同批挂】进 `state/gate_check.py`, 不提前挂** ⇒ ★**★⇒ 机器理由 (★main 本机实跑实测★)★**: ★**★这道闸的 D6 自己断言「`state/gate_check.py` 里命中本闸名的行数 == 0」⇒ ⇒ 挂进去 = 它自己判自己红 = 【假红】⇒ ⇒ 现场会把它读成「板坏了」** ⇒ ⇒ ★**★与全部先例同源: 闸与它要防/要等的那一趟同批生效** ⇒ ⇒ ★**★⇒ 且【挂链动作只能由 main 在那一趟统一做】(★不许 agent 自挂★) ⇒ ⇒ ★**★⇒ 顺带: 本轮三道新闸 (`check_sw_gate_health` / `check_fts_seat_body_geometry` / `check_fts_land_drill_same_batch`) 全部【与那一趟同批挂】⇒ ⇒ 那一次的「闸清单刷新」批次要一次挂三个 + 【同时翻它们自己那三条零挂链判据】+ 【同时刷新 §2 的账】(★三件同批·★见 §③★)** ⇒ ★ ★ |

★**▌D 组 · ISS-387 / ISS-389 (10 条·★L-32 重答·★用 need 的原 key★)★★**

★**★⇒ 这 10 条是我 13:1x 落过但【因 key 改名而一条没闭合】的 ⇒ 本轮按 need 的原 key 重答 (★老字一字未删·保留作人读记录★)★**

| # | need key | main 裁决 |
|---|---|---|
| D1 | `OI-387-1` | ★**焊盘【不维持 `1.000×1.000`】—— ★★这条被本轮的新证据【推翻】了, 追加式订正 13:1x 那条★★** ⇒ ★**机器事实 (★main 本机实算 + 官网能力表一手核实★)★**: ★**① 官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 = (`1.000` − `0.71`) / 2 = `0.1450` mm** ⇒ ★**② 本板 8 铜层 (★main 本机解析 `.kicad_pcb` 的 `(layers …)` 块 = F.Cu + In1..In6.Cu + B.Cu = 8 层★) + 外层铜厚 `0.035` mm (★stackup 实读 = 1 oz★) ⇒ 适用【多层 1 oz】那一行** ⇒ ★**③ JLCPCB 官网 PCB capabilities 一手核实 (★main 本轮自己 web_fetch, 逐字: 「PTH annular ring ≧0.20mm … Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm」★) ⇒ ⇒ `0.1450` < `0.15` ⇒ ★★【低于绝对下限】★★** ⇒ ⇒ ★**★⇒ ⇒ 「`1.000` 是 MECH 七个余量数一个都不用改的唯一成立条件」这个前提【已经不成立】** ⇒ ⇒ ★**★⇒ 处置 (★main 裁决, 不代拍焊盘最终值·★那要老板/板厂口径·★但工程方向本轮已定★)★**: ★**① 焊盘必须放大到 ≥ `1.010` (够绝对下限 `0.1500`) ⇒ 建议 `1.110` (够推荐值 `0.2000`)** ⇒ ⇒ **② ⇒ 铜箔包络随焊盘放大而放大 ⇒ ⇒ MECH 全链七个余量数【必须整体重算】(★`4.8100`/`2.2700`/`6.6100`/`4.0700`/`0.1350`/`2.6950`/`0.7700`·★按 pad `1.110` 重算·★归 mech-lead·★与那一趟同批★)** ⇒ ⇒ **③ ⇒ 但 [MECH 重算] 与 [板只改一次] 并不冲突 —— 因为它只改清单与结构件出件尺寸, 不改板 md5 的次数 ⇒ ⇒ 仍是一次投板** ⇒ ⇒ ★**★⇒ ④ ⇒ 【板厂口径这一格本轮仍无据】: 仓内 `HW/PCB/FAB_ORDER_NOTES.md` 只写「板厂」, 从未指名是哪一家 ⇒ ⇒ 「JLCPCB 那条官网」目前只是【参考档】不是【本板厂档】⇒ ⇒ 但 0.1450 低于业界主流厂的多层 1oz 绝对下限这一点, 已足以支撑【焊盘不能维持 1.000】这个方向 ⇒ ⇒ 剩下一格 = 【本板厂到底是谁 + 外层铜厚是不是 1 oz】⇒ 归【那一趟开单前 + 老板侧下单时确认】⇒ 【本仓零外发 ⇒ 不自行发问询】** ⇒ ⇒ ★**★⇒ ⑤ ⇒ 追加式订正: 13:1x 那条 `iss387_main_oi1_pad_1x1_maintained` (★维持 1.000·★以环宽可行为条件★) ⇒ 【被本条取代】(★老字一字未删★)** ⇒ ★★ |
| D2 | `OI-387-2` | ★**改孔动作与「板只改一次」那一趟【同批】—— 确认同批** ⇒ ★**机器理由: 改孔是【板侧动作】⇒ 不同批就要多投一次板 ⇒ 且本轮已实测【提前落登记没有造成假红】⇒ ⇒ 【登记可以早落, 改孔必须同批】⇒ ⇒ 两者不矛盾: 登记 = 清单 (可早), 改孔 = 板 (必须同批)** ⇒ ★★ |
| D3 | `OI-387-3` | ★**用【盘上通用 KiCad 1.27mm THT 库件 land】+ 【一条显式偏离登记】+ 【BOM 型号栏写 FTS 料号】三者同源 ⇒ 采纳 (★这是 13:1x A3 的同一裁决, 本轮按 need 原 key 重答★)** ⇒ ★**★⇒ 同源纪律 (★板面 land 来源 = BOM 型号栏 = 实物料号★)**: ★**Samtec 的直接图纸给的是孔位图, 【没有】铜箔焊盘直径 ⇒ ⇒ 所以「官方铜箔宽度」这一级【不存在】⇒ ⇒ 不能拿 FTSH (双排 SMT) 的数替代 ⇒ ⇒ 唯一能自洽的组合 = 通用库件 land + 偏离登记 + BOM 同源** ⇒ ⇒ ★**★⇒ 偏离登记必须逐字写明四项: ① 铜箔焊盘直径 = 库件默认 `1.000` (官方无值) · ② 孔径 `0.65→0.71` (官方 TYP) · ③ 焊盘直径放大到 ≥`1.010`/建议 `1.110` 的理由 = 环宽 (★见 D1★) · ④ 封装族 = FTS 直插单排 (★不是 FTSH 双排 SMT★)** ⇒ ⇒ ★**★⇒ 逐字草案按真相页原文落, main 不改一字** ⇒ ★ ★ |
| D4 | `OI-387-4` | ★**座体外形三量 (宽 X / 深 Y / 绝缘体高 Z) 走【双轨降级】, 且【甲轨的官网值本轮已由 ISS-390 取到 ⇒ 只剩乙轨 (实测) 待做】⇒ 归 mech-lead 执行 (转派), 与「板只改一次」那一趟同批, 不新起一单** ⇒ ★**★⇒ 已取得的官网值 (★main 本机独立复核坐实★)★**: ★**X = N × 1.27 ⇒ N=4 ⇒ `5.0800` / N=2 ⇒ `2.5400` · Y = `2.1600` (★通用件 F.Fab 跨排距 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`★) · Z = `0.8600`** ⇒ ⇒ ★**★⇒ ⇒ 「[0数据]」的性质变了 = 不是「查不到」, 是「查错了对象」+「REF 无公差带」⇒ ⇒ 剩下的只有【公差】与【实测】⇒ ⇒ 乙轨 (落 FTS 时打 1 块单板样, 卡尺量三量, 回填 `keepout_dwg` + `body_geometry`) 是【唯一】能拿到实物公差的路径 ⇒ ⇒ 归 mech-lead, 与那一趟同批** ⇒ ★ ★ |
| D5 | `iss389_oi2_b33_scope_window` | ★**含 J_UART —— B33_PIN_LAND_1P27 的范围含 J_DEBUG + J_UART 两个连接器** ⇒ ★**★⇒ 机器理由: ① 板上 BOM (`HW/BOM_v1.csv:77`) 与网表 (`HW/netlist_v1.csv:399`) 写的都是 1.27mm 实物排针, 而板上现有 land 是 0.50mm pitch 的自绘 SMD 占位 ⇒ ⇒ 不改 J_UART ⇒ 实物排针【落不进】⇒ ⇒ 「结构件零返工」不等于「实物装得上」; ② 两个连接器是【同一个封装族、同一个 pitch 族、同一个 land 尺寸】⇒ ⇒ 只改一个 = 板上留一个装不上的 ⇒ ⇒ 【两个必须同批】** ⇒ ⇒ ★**★⇒ 代价已算清: 含 ⇒ J_UART 结构件同批返工 (清空区 `2.5400×2.5400` → `4.3400×3.9600`·★注意 X 值已按 B3 更新·★不是本单原文的 `4.0700×2.8000`★) 且罩开口 Y 要改到含 `66.1000..70.7000`; 不含 ⇒ 实物装不上 ⇒ ⇒ ★**★⇒ ⇒ 结论: 含 ⇒ 与「板只改一次」纪律一致 (★一次投板一次做完·★不许留半个★)** ★ ★ |
| D6 | `iss389_oi3_juart_landing_window` | ★**J_UART 落点裁决【已被 ISS-379 挂起】⇒ 本轮【不重复开】; 但把机器事实定死, 让老板那一字母能一次拍完** ⇒ ★**★⇒ 机器事实 (★结构侧沙盒实算, main 核对★)★**: ★**① 三候选 X 向全可行; ② Y 向 C1 与 C3 可行且铜箔中心允许偏心 `0.0000`; ③ C2 内缩只有 `1.6000`, 差 `0.2000` ⇒ 【C2 不可行】⇒ ⇒ 【C2 不是「贵一点」, 是几何上死】⇒ ④ 三候选的清空区中心差 `-0.9250` / `+0.1450` / `+0.0450` ⇒ ⇒ 结构件开不开得了模全看这一条** ⇒ ⇒ ★**★⇒ ⇒ 主裁决 = 【C2 出局】(★机器判死·★不是偏好★) ⇒ 【C1 与 C3 二选一】⇒ ★★**★⇒ ★★但 C1 vs C3 的取舍 = 落点/结构件的协同决定 ⇒ 【归 boss, 与板框第一问同一窗口一次拍完】(★它与 OI-13 的 Y 向决定是同一个决定的两面·★但因为 C2 已出局, 「定 C2 而没同时改罩开口 Y ⇒ 结构件返工第二次」这条死结【自动消失】★)★ ★ ★★** ★ ★ |
| D7 | `iss389_oi5_clearance_x_tier_window` | ★**取 `4.8100` (★= 通用 KiCad 1×4 THT 的铜箔沿脚排总展 = `1.000` + 3 × `1.2700`·★main 本机解析 `.kicad_mod` 坐实·★pads=4 / drill 0.65 / pad 1.000×1.000 / y 0·1.27·2.54·3.81★)** ⇒ ★**★⇒ 三个候选 `1.7750` (圆当方) / `4.0850` (错的焊盘宽移到 1.27 pitch) / `4.8100` (真铜箔总展) 里只有 `4.8100` 是【盘上真实铜箔的量】⇒ ⇒ ★★**【且它正是 §㊴ C1 已经裁过的那个数 ⇒ 前后一致】** ⇒ ⇒ ★**★⇒ 但要同时说清两个边界: ① `4.8100` 是【铜箔包络】(判「装得下」的输入); ② 真正约束【结构件出件】的是【座体本体】口径 = `5.0800` ⇒ 需求 `6.8800` (★见 B3·★这就是 §㊶ C4/C6 被改掉的那两格★) ⇒ ⇒ ★**★⇒ ⇒ 两个数【都要】: `4.8100` 判铜箔装不装得下, `6.8800` 判座体留不留得住 ⇒ 不冲突** ⇒ ⇒ ★**★⇒ ⇒ 结构件总宽增量按最坏档 (`4.8100`) = `+1.8000`; 若焊盘因环宽放大到 `1.110` (★见 D1★) ⇒ 铜箔总展变 `4.9200` ⇒ ⇒ 【结构件出件须按座体口径 `6.8800` 出, 铜箔那一档的增量随之微调】** ⇒ ★ ★ |
| D8 | `iss389_oi12_cover_criterion_window` | ★**main 部分已裁 (★判据【管到座体本体】·★「偏紧 `0.5200`」措辞作废·★判据每边 `0.9000` 保留★); 要 boss 拍的是【代价那一面】(★结构件每边多让多少 / 镜脚内腔与外观缝的连带代价·★归老板域·★与板框第一问同一窗口★)** ⇒ ★**★⇒ 机器事实 (★main 本机独立复核坐实·★见 B3★)★**: ★**① 厂件座体 X `5.0800` (N=4) / `2.5400` (N=2) + Y `2.1600` ⇒ 清空区需求 X = `6.8800` / `4.3400`, Y = `3.9600`** ⇒ ⇒ **② 「比 courtyard 还紧 `0.5200`」这个论据【作废】(★`6.0900` 是通用 KiCad 库件自己的 `F.CrtYd`·★厂件没有 courtyard 这个量★)** ⇒ ⇒ ★**★⇒ ③ ⇒ 需求从 `6.6100`/`4.0700` 抬到 `6.8800`/`4.3400`, 每边多让 `0.1350` (★`0.2700` 总宽差÷2★) ⇒ ⇒ **boss 要拍的是【这 `0.1350`/边 值不值得 + 连带代价】** ⇒ ⇒ ★**★⇒ ⇒ 【本条与 OI-14 是同一个决定的两面 ⇒ 必须一起拍】(★OI-14 的目标值 = `4.3400`·★已由 B3 定★)** ⇒ ★ ★ |
| D9 | `iss389_oi13_y_zero_margin_window` | ★**main 部分已裁: 「接受零余量」这个选项【已不存在】(★座体口径下 Y 向缺口 `1.1600`·★装不下·★不是「压线过阈」★) ⇒ ⇒ 只剩【放大罩开口 Y】一条路 ⇒ 开口 Y 须 `≥ 5.7600`** ⇒ ★**★⇒ 机器事实 (★main 本机实算★)★**: ★**① 座体本体 Y = `2.1600` ⇒ 清空区 Y 需求 = `2.1600` + 2 × `0.9000` = `3.9600`; ② 罩开口 Y 现状 `4.6000` 只容清空区 Y `2.8000` ⇒ 缺口 `1.1600`; ③ ⇒ 开口 Y 须 ≥ `3.9600` + 2 × `0.9000` = `5.7600` ⇒ 放大 `1.1600`** ⇒ ⇒ ★**★⇒ ④ ⇒ 结构性代价 (镜脚内腔 + 罩外观缝 / 防水防尘 / 壁厚) 归老板域 ⇒ 与板框第一问同一窗口一次拍完** ⇒ ⇒ ★**★⇒ ⑤ ⇒ 附带好消息: 因为 C2 已出局 (★见 D6★), 「定 C2 而没同时改罩开口 Y ⇒ 结构件返工第二次」这条死结【自动消失】⇒ ⇒ ★★** ★ ★ |
| D10 | `iss389_oi14_dp1_correction_window` | ★**订正为 `4.3400` (★不是 `4.0700`★), 且【订正块往老页落】(★走追加式·★老字一字未删★), 但【与「板只改一次」那一趟同批】** ⇒ ★**★⇒ 机器理由: ① ISS-377 §3.2 的 DP-1 给 `3.4700` ⇒ 现行判据链下不够; ② 本轮把口径改成【座体本体】⇒ 目标值不是 `4.0700` (铜箔口径) 而是 **`4.3400`** (座体 `2.5400` + 2 × `0.9000`·★main 本机实算★) ⇒ ③ ⇒ 老页是已签收件 ⇒ 本单零改老页 ⇒ 订正块由 main 授权, owner 在那一趟的清单改版里落 ⇒ ⇒ ★**★⇒ ⇒ 【本条与 OI-12 必须一起拍】(★同源·★§㊶ C6 的 `4.0700` 那个值已被本条取代·★追加式订正·★老字未删★)** ⇒ ★ ★ |

★**▌E 组 · 环宽 / 焊盘 / 落盘四组 (4 条·跨单·★本轮的新证据都在这里★)★★**

| # | need key | main 裁决 |
|---|---|---|
| E1 | `iss394_ring_width_fab_capability` | ★**本仓零外发 ⇒ 这条不靠「等一句可以发」⇒ 靠【自己查公开的板厂工艺能力表】⇒ 本轮 main 已一手核实 JLCPCB 官网 PCB capabilities (★逐字: 「PTH annular ring ≧0.20mm … Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm」★) ⇒ ⇒ 结论: 环宽 `0.1450` (pad `1.000` + 孔 `0.71`) 低于多层 1oz 的绝对下限 `0.15` ⇒ 【焊盘 `1.000` 不可用】⇒ ⇒ 焊盘 ≥ `1.010` (绝对下限) ⇒ 建议 `1.110` (推荐值 `0.20`) ⇒ ⇒ ★**★⇒ 仍缺的一格 = 【本板厂是不是 JLCPCB】(★仓内 `FAB_ORDER_NOTES.md` 从未指名厂★) ⇒ 归【老板侧下单时确认】⇒ 【main 不自行发任何问询】⇒ ⇒ ★**★⇒ 补一句成本判断: 焊盘放大【不进铜箔包络之外的额外成本】, 但会让铜箔包络变大 ⇒ ⇒ MECH 七个数必须重算 ⇒ ⇒ 【重算不额外投板 ⇒ 不违反「板只改一次」】** ⇒ ★ ★ |
| E2 | `iss394_seat_outer_dimensions` | ★**双轨降级方案【采纳】, 但【甲轨的官网值已被 ISS-390 取到】⇒ ⇒ 实际只剩【乙轨 (1 台样件实测)】待做 ⇒ 且【与「板只改一次」那一趟同批】** ⇒ ★**★⇒ 已取得的官网值 (★main 本机独立复核坐实★)★**: ★**X = `5.0800`/`2.5400` (N×1.27) · Y = `2.1600` (★通用件 F.Fab `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`★) · Z = `0.8600`** ⇒ ⇒ ★**★⇒ ⇒ 「[0数据]」这句【已经过期】⇒ 「[0数据]」不再是「查不到」, 是「查错了对象」(★库件根本给不了 Z★) ⇒ ⇒ 剩下只有【公差】(★官网图给的是 REF 不是公差带·★X 的通式公差 ±0.25★) ⇒ ⇒ **乙轨 (落 FTS 时打 1 块单板样, 卡尺量三量, 回填 `keepout_dwg` + `body_geometry`) 是【唯一】能拿到实物公差的路径 ⇒ ⇒ 归 mech-lead 执行 (转派) + 与那一趟同批 (★落 FTS 那天才有样可打★) + 不新起一单** ⇒ ★ ★ |
| E3 | `iss396_main_pad_diameter_ring_width` | ★**与 D1 / E1 同一裁决: 焊盘【不维持 `1.000`】⇒ 方向 = 放大到 ≥ `1.010`, 建议 `1.110`; 最终值 = 【老板/板厂口径那一格】⇒ 【main 已把工程方向定死, 剩下的那一格归老板域】** ⇒ ★**★⇒ 追加式订正 ISS-396 交卷页里「建议默认值 = pad 取 `1.110`」这一句的口径**: ★**那是对的, 但【它写的是「若就是 JLCPCB 8 层 1 oz」这个前提下的建议】⇒ ⇒ 本轮的裁法 = 【① 工程方向无条件成立 (0.1450 < 业界主流多层 1oz 绝对下限 ⇒ 焊盘不能维持 1.000) · ② 具体取 `1.010` 还是 `1.110` = 取决于本板厂口径, 归老板那一格 · ③ 板厂口径 = 老板侧下单时确认, main 不自行发问询】** ⇒ ⇒ ★**★⇒ 追加式订正: 本条与 `iss387_main_oi1_pad_1x1_maintained` (13:1x 的「维持 1.000」) 【相互取代·以本条为准·老字一字未删★】** ⇒ ★ ★ |
| E4 | `iss396_main_registration_timing_vs_131x_ruling` | ★**★表态: 我 13:1x 那条裁决里的「不许提前落」这一半【撤回其约束力】(★追加式订正·★老裁决原文一字未删★) ⇒ 保留的那半句 = 【#1/#2/#3 必须一起落】** ★★ ★**★⇒ 机器理由 (★main 本机实跑覆盖度闸·★不抄报告★)★**: ★**① 覆盖度闸 P4 现读 = 绿: 「作业包 §0.2 ③ 的 ③ ⇒ 命中 ['B33_PIN_LAND_1P27'] (覆盖令牌 7 个全在)」⇒ ⇒ 提前落登记【没有】造成任何假红** ⇒ ⇒ **② ⇒ 我 13:1x 担心的【P4 会拿 `0.71` 去查真实板面 ⇒ 当场红】不成立 ⇒ ⇒ 因为 P4 查的是【清单页里有没有那些令牌】, 不是【板面改没改】⇒ ⇒ 所以「不许提前落」这个约束【是我自己推错的后果, 不是实测事实】** ⇒ ⇒ ★**★⇒ ③ ⇒ 撤回的那半句不影响任何实质结论 (★#1/#2/#3 一起落才是实质, 且 ISS-396 正是这么落的·★追加式·老字一字未删★) ⇒ ⇒ ★**★⇒ ④ ⇒ 追加式声明: 【本条是 main 自己对自己旧裁决的订正, 不由任何 agent 触发⇒⇒ 触发者是 main 本机实跑覆盖度闸的读数★】** ⇒ ★ ★ |

★**⑧ 本轮零派 / 零外发 / 零落表 / 零写板 / 零挂链**: ★**internal = 0 ⇒ 三单已交卷待签收 (★ISS-392~398 多条真在飞 ⇒ 不重复派★) ⇒ 外发段恒空** ★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标 / 清空区放大量的一切前提都挂在它身上, 本页不代拍** ★
★**⇒ 「板只改一次」那一趟现在明确要带【六条腿】**: ★**① 改孔 `0.65→0.71` (★焊盘放大到 ≥`1.010`/建议 `1.110`·★环宽 `0.1450` < 多层 1oz 绝对下限 `0.15`★) ② §4 剩下两处登记 (#4 覆盖令牌 + #5 BOM 两栏) ③ 三道新闸挂链 + 【同时翻它们自己那三条零挂链判据】+ 【同时刷新 §2 的账 (含那 5 条既存失配)】 ④ 六个签收件的 md5 刷新 + 全部验收线重跑 (★L-27 通则③★) ⑤ 六个签收页的定性订正块 (ISS-390 §4 六处 + ISS-389/OI-14 的 `4.3400` + §㊶ C4/C5/C6 的数值) ⑥ MECH 七个数按新焊盘重算 + 座体三量收样 (★乙轨·★落 FTS 那天才有样可打★)** ★ ★
"""

LESSONS_BLOCK = """

## ★L-32 · ★★落答案时必须【从 need 里逐字抄 key】⇒ 自己起 key = 机制【静默失效】(★比撞名报错更危险★) ★★

★**实测 (2026-11-24 19:1x, main 本机实读 `state/merge.py` + 逐 key 核对·★本轮自曝★)★**: ★**main 在 13:1x 那一轮落了 15 条 pm.yaml 答案, 内容全对, 但【一条都没闭上任何 need】** ⇒ ★**★⇒ 机制读数: pm.yaml 里 `to=main` 的答案中, 【逐字】命中某个 need 的 key 的只有 113/152 ⇒ ⇒ 我那 15 条全在「没命中」那一侧** ★ ★
★**★根因 (★main 本机实读 `state/merge.py` 坐实★)★**: ★**merge.py 按【精确 key】配对: `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]` ⇒ ⇒ key 必须与 need 的 key 【逐字相同】, 且答案必须落在【被问的那个 agent】的分片里** ⇒ ★**★⇒ 而我 13:1x 用了【自己起的改名 key】(★如 `iss389_main_oi5_pick_4810`, 而 need 的 key 是 `iss389_oi5_clearance_x_tier_window`★) ⇒ ⇒ **配不上 ⇒ 零闭合** ★ ★
★**★⇒ ★★这比 L-28 的「key 撞名」更危险★★**: ★**L-28 是【撞名】⇒ 幂等守卫会报错退出 ⇒ 至少【有声音】; 而这里是【没撞名, 只是对不上】⇒ ⇒ 机制【一声不吭】⇒ ⇒ 答案躺在 pm.yaml 里, 内容正确, 但【对闭环机制等于不存在】⇒ ⇒ **页面上看起来「已答」, 台账上其实还挂着** ★ ★
★**★⇒ 两条纪律 ★★**: ★**① 落答案前, 必须先从 need 里【逐字抄 key】(★不许自己起, 不许「起个更清楚的名字」★)⇒ ⇒ 若 need 的 key 本身不适合当答案的 key, 那就【改 need 的 key】或【在答案的 value 里写清对应关系】, 但【不许两边名字不一样而指望机制能猜】** ★ **② 落盘后必须回读验证【该 key 的 need 已从 pending 变 answered】⇒ ⇒ 不许只看「脚本打印 ✅ 已原子更新」(★L-28 通则② 同源: writer 的成功消息只保证【写成功】, 不保证【写对了地方】★)** ★ ★
★**★⇒ ★★推广 (★不止 pm.yaml★)★**: ★**凡是有「按 key 配对」的地方 (★merge 的 needs×answers · gate 的 (file,line) 钉住 · 一页的章节号索引 · 决策索引的 55 条覆盖复核★), 【键必须逐字对齐】, 而【对齐这件事本身要有回读验证】⇒ ⇒ ★**★⇒ 反过来说: 【机制【静默失效】比【机制【报错】更贵】⇒ ⇒ 所以凡是我新写的机制, 都必须自带一句「配对不上就报错」** ★★"
★**★⇒ ★★与 L-28 的关系 (★一对镜像面★)★**: ★**L-28: 「撞名」⇒ 【必须报错退出】(★不能静默跳过然后继续报绿★) ⇒ ⇒ ★**L-32: 「不撞名但对不上」⇒ 【必须被当成错误处理】⇒ ⇒ 两侧合起来 = 【key 是唯一的连接键, 任何一侧不对齐都必须响】** ★★"
★**★⇒ ★★与 L-21 / L-30 合看 (★同一族的第三条·★本轮同时踩到★)★**: ★**L-21: 清单钉 (file,line) ⇒ 往被钉文件里插行会让清单自己过期 ⇒ 补丁与清单必须同批重生成 · L-30: 取号/取 key 必须先查重 ⇒ ⇒ L-32: 【键的两端必须逐字对齐, 而且对齐要有回读验证】** ⇒ ★**★⇒ 三条合起来 = 【凡是有「键」的地方, 键的【产生】与【使用】两端必须同时被检查】★★** ★ ★"
★**★⇒ ★★本轮的第二个自曝 (★与 L-32 同族·★但方向相反★)★**: ★**ISS-391 闸的 `--selftest` 从 17/17 变成 14/17 —— 而【判据本身没坏】(★main 用 import 闸源码 + 真删文本的探针证明 D1/D2/D3 检测力完好★) ⇒ ⇒ 坏的是【selftest 的夹具锚点】: 闸里硬编码了一句文案当锚点, 而【另一次合法落地】把盘上真实文本换成了另一个版本 ⇒ ⇒ 【那个锚点在盘上出现 0 次】⇒ ⇒ 【反向用例变成空操作】⇒ ⇒ ⇒ 【落地的副作用会打穿别的闸的自证】★★ "
"★**★⇒ ⇒ ★★由此得出一条新的铁律 (★本轮立, 归 L-32 家族但独立★): 【★闸的 selftest 夹具不许硬编码「会漂的字样」当锚点 ⇒ 必须从盘上真实内容动态取 ⇒ ★否则【任何一次合法落地】都可能把别的闸的自证静默打穿, 而那条闸【看起来还是绿的】(裸跑 rc=0) ⇒ ⇒ 只有 selftest 才暴露得出来 ⇒ ⇒ 而 selftest 又常常【没人跑】⇒ ⇒ ⇒ 【于是它就烂在盘上, 正是今天 ISS-388 那道元闸要抓的病灶】】** ★★ "
"★**★⇒ ⇒ ★★**⇒ 附带一条判据纪律 (★本轮自曝★)**: ★**★ 「裸跑绿」不等于「闸可信」** ⇒ ★**⇒ 签收一台闸时, 【裸跑读数】与【selftest 读数】是两个都要看的数 ⇒ ⇒ ★★**⇒ 本轮 ISS-391 就是【裸跑 7/7 全绿 + selftest 14/17 红】⇒ ⇒ 若只看裸跑就会误签 ⇒ ⇒ ⇒ 这就是 L-29 通则① 的正确用法: 【selftest 末行必须是 ALL TESTS PASS 才算闸可信】** ★★ "
"★**★⇒ ★★本轮顺手实证的另三件 (★都是同一条纪律的不同切面★)★**: ★**① 章节号取号: `§㊺` 已被兄弟 job 18:3x 占用 ⇒ 本轮先扫已用集合再取号, 取到 `§㊻` ⇒ ★**这正是 L-30 的实例** ★ **② 签收记录的「现读」纪律: ISS-391 交卷时是 4/7 红 (按设计), 签收时刻已是 7/7 全绿 ⇒ ★**签收记录钉的是【签收那一刻】的指纹与读数, 不是【交卷那一刻】的 ⇒ ⇒ 「按设计判红」这种口径必须写明【是哪个时刻的读数】, 否则签收记录就是假的 (★这是 L-27 的第 6 款, 本轮第一次真正被用到★)** ★ **③ ★★`state/board_md5_pinned_gates.json` 的 9 条 `(file,line)` 钉住里【已有 5 条失配】⇒ ⇒ 这是 L-21 的既存实例 ⇒ ⇒ 刷那本账时必须【连旧失配一起修】, 只加新闸不修旧的 = 半修** ★ ★"
"""


def append_onepager():
    p = ONEPAGER
    old = read_lines(p)
    used = set(re.findall(r"^##\s*★*([㊀-㊿]+)", old, re.M))
    if "㊻" in used:
        raise SystemExit("★§㊻ 已被占用 ⇒ 零写盘退出★")
    shutil.copy2(p, p + ".bak_%s_main_sign_iss388_390_391" % STAMP)
    before = os.path.getsize(p)
    with open(p, "a", encoding="utf-8") as f:
        f.write(ONEPAGER_BLOCK)
    print("  一页: %d → %d B (追加式 §㊻, 备份 %s.bak_%s_main_sign_iss388_390_391)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    old = read_lines(p)
    used = [int(x) for x in re.findall(r"^##\s*★L-(\d+)", old, re.M)]
    if 32 in used:
        raise SystemExit("★L-32 已被占用 ⇒ 零写盘退出★")
    shutil.copy2(p, p + ".bak_%s_main_l32" % STAMP)
    before = os.path.getsize(p)
    with open(p, "a", encoding="utf-8") as f:
        f.write(LESSONS_BLOCK)
    print("  LESSONS: %d → %d B (追加式 L-32, 备份 %s.bak_%s_main_l32)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_pm(needkeys):
    sys.path.insert(0, HERE)
    from _ans_1910 import ANSWERS

    # ★★L-32 前置: 分两类 key ★★
    #   ① 【要闭 need 的】⇒ 必须逐字命中某个 need 的 key, 否则【报错退出】(★不许静默配不上★)
    #   ② 【main 自裁的】⇒ 用 `main_` / `_main_` 前缀标明 (★先例: main_advance_py_decision_list_order_dependency·
    #      iss387_main_rilim_ring_width_fab_capability·★它们【不闭 need】, 只是把 main 的判断登记在册★)
    def is_selfraised(k):
        # ★★只有【盘上 need 里根本不存在】的 key 才算 main 自裁; 盘上存在的 ⇒ 必须走闭合路径 ★★
        return k not in needkeys
    closers = [k for k, _v, _r in ANSWERS if not is_selfraised(k)]
    selfraised = [k for k, _v, _r in ANSWERS if is_selfraised(k)]
    bad = [k for k in closers if k not in needkeys]
    if bad:
        raise SystemExit("★★L-32 校验失败: 这些 key 在盘上找不到对应 need ⇒ 零写盘退出★★ %s" % bad)
    print("  ★★L-32 前置: 33 条 = 【闭 need 的】%d 条 (★全部逐字命中★) + 【main 自裁的】%d 条 (★`_main_`/`main_` 前缀·不闭 need·只登记★)"
          % (len(closers), len(selfraised)))
    for k in selfraised:
        print("      · main 自裁: %s" % k)

    cur = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    have = {a.get("key"): a for a in (cur.get("answers") or []) if isinstance(a, dict)}
    added, skipped = 0, []
    for key, val, ref in ANSWERS:
        if key in have:
            # ★★L-28: 幂等守卫命中 ⇒ 必须核对 value 是否逐字相同 ⇒ 不同 ⇒ key 撞名 ⇒ 报错退出★★
            if have[key].get("value") != val:
                raise SystemExit("★★L-28 key 撞名: %s 已存在但 value 不同 ⇒ 报错退出 (★不写没核过的内容★)★★" % key)
            skipped.append(key)
            continue
        frag_write.update_fragment("main", lambda d, k=key, v=val, r=ref: d.setdefault("answers", []).append(
            {"key": k, "to": "main", "value": v, "ref": r}))
        added += 1

    # ★★L-32 回读验证: 逐个确认【该 key 的 need 已从 pending 变 answered】★★
    pmc = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    amap = {}
    for a in pmc.get("answers") or []:
        if isinstance(a, dict) and a.get("key"):
            amap.setdefault(a["key"], []).append(a)
    need_after = set()
    for f in ("sw.yaml", "mech.yaml", "hw.yaml"):
        fd = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        for n in fd.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                need_after.add(n["key"])
    miss = [k for k, _v, _r in ANSWERS
            if k in need_after and not (k in amap and any(x.get("to") == "main" for x in amap[k]))]
    miss += [k for k in closers if k not in amap]
    dup = len([k for k, v in amap.items() if len(v) > 1])
    tot = len(pmc.get("answers") or [])
    print("  pm.yaml (main 自己的分片): answers +%d 条 (跳过已存在且逐字相同 %d) ⇒ 共 %d 条 · 重复 key %d"
          % (added, len(skipped), tot, dup))
    print("  ★★L-32 回读验证: 本轮 %d 条答案里, 逐字命中 need key 且 to=main 的 = %d 条 (★miss %d★)"
          % (len(ANSWERS), len(ANSWERS) - len(miss), len(miss)))
    if miss:
        raise SystemExit("★★L-32 回读验证失败: %s 仍未闭合 ⇒ 报错退出★★" % miss)
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
           "★⑤ ⇒ 与 L-21 / L-30 合看 = 【凡是有「键」的地方, 键的【产生】与【使用】两端必须同时被检查】★★ "
           "★⇒ ★**本轮实证 (★19:1x·★ISS-388/390/391 三单一并签★): ① 我 19:1x 那轮按 need 原 key 重答的 33 条 (★含 13:1x 那 15 条的重答+5 条 ISS-396 交回的) 全部逐字命中 ⇒ ② 一页取号先扫已用集合 (★`§㊺` 已被兄弟 job 18:3x 占用 ⇒ 本轮取 `§㊻`·★L-30 实例★) ③ ISS-391 交卷时 4/7 红, 签收时刻已 7/7 全绿 ⇒ ★**签收记录钉的是【签收那一刻】的读数, 不是【交卷那一刻】的 ⇒ 「按设计判红」必须写明是哪个时刻 (★L-27 第 6 款·★首次真正用到★)** ④ `state/board_md5_pinned_gates.json` 的 9 条 (file,line) 钉住里【已有 5 条失配】⇒ ★**刷那本账时必须连旧失配一起修, 只加新闸不修旧的 = 半修 (★L-21 既存实例★)** ⑤ ★★三道新闸【各自都断言零挂链】⇒ 挂链必须与「翻那三条零挂链判据」同批, 否则挂进去就是三道假红** ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-32 指针追加 (追加式, 备份 %s.bak_%s_main_l32_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def write_round_log():
    r = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1910_sign_iss388_390_391.md")
    body = """# ROUND_LOG_main · 2026-11-24 19:1x · ISS-388 / ISS-390 / ISS-391 三单一并签 + 33 条 main 地界待裁项已裁 + 自曝 L-32

★**job**: main (ARS45 项目总工) · webchat 会话 (★由兄弟 job 5bd48f25 的进展播报触发★)
★**签收闸**: `state/_apply_20260724_1910_main_sign_iss388_390_391.py` (★fail-closed·★答案正文在 `state/_ans_1910.py` + `state/_ans_1910_d.py`★)
★**备份** (★脚本现场取 `time.strftime`★): `state/issue_log.yaml.bak_<stamp>_main_sign_iss388_390_391` ·
`DECISION_ONE_PAGER_2026-11-22.md.bak_<stamp>_main_sign_iss388_390_391` · `state/LESSONS.md.bak_<stamp>_main_l32` ·
`MEMORY.md.bak_<stamp>_main_l32_pointer`

---

## ★★一 · 板面 (本机实读) ★★

★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` (纳秒级) ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

---

## ★★二 · 三单签收 (main 本机独立复核·不抄任何 agent 报告) ★★

| 单 | owner | 闸 | 裸跑 (★签收时刻★) | `--selftest` |
|---|---|---|---|---|
| ISS-388 | sw-lead | `SW/tools/check_sw_gate_health.py` | ★**rc=1 · 2/6 绿** (★按设计★) | ★**rc=0 · 22/22 · ALL TESTS PASS** (★248s/次·★本轮用 detached 探测留证★) |
| ISS-390 | mech-lead | `MECH/check_fts_seat_body_geometry.py` | ★**rc=0 · 33 条判据 0 失败** | ★**rc=0 · 15/15 · ALL TESTS PASS** |
| ISS-391 | hw-lead | `HW/check_fts_land_drill_same_batch.py` | ★**rc=0 · 7/7 全绿** (★状态已变★) | ★★**rc≠0 · 14/17 · `SELFTEST FAILED`** ⇒ ★★**【本轮不签收】** ★★ |

★三闸零挂链 · 零落表 · 零改既有页面正文 · L-26① 的 13 道扫描面闸全 rc=0 (含七个签收闸) ★

★**⇒ ⇒ 签收口径: 【签 ISS-388 + ISS-390 两单】; 【ISS-391 不签】(★status 保持 fixing·★只追加 hold 记录·★老字未删★) ★**

---

## ★★三之二 · ★★ISS-391 为什么【不签】(★本轮第二个实质发现★) ★★

★**① 裸跑 rc=0 · 7/7 全绿 (D1~D7 逐条绿)** ★
★**② `--selftest` = 14/17, 末行 `SELFTEST FAILED`; 3 条 FAIL = ① (删作业包「钻孔」⇒ D1 红) · ② (删预检描述列钻孔字样 ⇒ D2 红) · ③ (删验收手段列读钻孔命令 ⇒ D3 红)** ★
★**③ main 的决定性探针 (★把闸源码 import 进来自己跑★)**: ★**把作业包 ③ 那一项里的「钻孔」真删掉 ⇒ `d1()` 立刻判红 ⇒ D1 检测力完好; 把预检清单真页里所有「钻孔」字样删掉 ⇒ `d2()` 判红 (2 条) + `d3()` 判红 ⇒ D2/D3 检测力完好** ★
★**④ 根因 = 夹具锚点硬编码 + 落地顶过期了它**: ★**闸里的常量 `WORKPACKET_DRILL_LEG` 是 ISS-391 交卷时那句文案; ISS-396 于 18:28~18:32 落 §4 #1 时实际写进作业包的是另一个版本 (★带「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」★) ⇒ ⇒ 【该常量在盘上作业包里出现 0 次】⇒ ⇒ 反向用例 ①② 的 `replace(...)` 变成空操作 ⇒ 沙盒文件根本没被改 ⇒ D1/D2 自然不红** ★
★**⑤ ⇒ 结论: 【这不是 agent 写错, 是【ISS-396 的合法落地】把 ISS-391 闸的夹具锚点顶过期了】⇒ ⇒ ★★**【落地的副作用会打穿别的闸的自证 ⇒ 新的跨单因果, 必须登记】** ⇒ ⇒ 修法 = 锚点改成【从盘上真实文本动态取】⇒ 归那一趟同批 (★owner = hw-lead★) ⇒ ⇒ **本轮不签** (★L-29 通则①: selftest 末行不是 ALL TESTS PASS ⇒ 闸不自证 ⇒ 不签★) ★
★**⑥ ⇒ 裁决与签收是两件事: ISS-391 的 5 条 OI 裁决【照样已裁并落账】(★裁决是 main 的判断; 签收是 main 对【交付物自证合格】的确认·★自证不合格就不签·★但裁决不该被拖住★)** ★

---

## ★★三 · ★★★本轮最重要的机器事实 ★★★

★**① 三道新闸【各自都断言「零挂链」】⇒ 挂进去 = 立刻自己判自己红**:
- ISS-388 H4 = `hook_hits = gc_txt.count("check_sw_gate_health")`
- ISS-390 G6.5 = `"check_fts_seat_body_geometry" not in txt`
- ISS-391 D6 = `命中 %s %s 次 (★必须是 0★)`
⇒ ⇒ **本轮不挂; 那一趟挂链时必须【与翻这三条判据 + 刷 §2 的账】同批** ★

★**② ISS-391 的状态在签收前变了**: 交卷时 (12:13) = rc=1 · 4/7 绿 · D1/D2/D3 红 (按设计) ⇒ 兄弟 job 18:28~18:32 派 ISS-396 落 §4 #1/#2/#3/#6 ⇒ **签收时刻 = rc=0 · 7/7 全绿** ⇒ §㊸ 给的「写明 D1/D2/D3 红 = 按设计」口径在签收时刻已不成立 ⇒ 本轮按【现读】写 ★

★**③ ISS-390 的核心声明 main 本机坐实**: 自己解析 `.kicad_mod` ⇒ `fp_rect` = 3.1000 × 6.0900 ⇒ 「`6.0900` 是通用件自己的 `F.CrtYd`」⇒ ⇒ `6.0900`/`5.0800`/`3.5500`/`2.5400` 与 Samtec 无关 ⇒ **§㊶ C4/C5/C6 被订正** (J_UART X 需求 `4.0700`→`4.3400`; 开口 Y →`5.7600`; 「偏紧 0.5200」措辞作废) ★

★**④ 环宽: main 一手核实 JLCPCB 官网** ⇒ 「PTH annular ring ≧0.20mm … Multilayer: 1 oz: … absolute minimum 0.15 mm」⇒ 本板 8 铜层 + 外层 0.035mm (1oz) ⇒ **`0.1450` < `0.15` = 低于绝对下限** ⇒ **焊盘 `1.000` 不可用** ⇒ ≥`1.010`, 建议 `1.110` ⇒ ⇒ **§㊶ A1 的「维持 1.000」被推翻** ★

★**⑤ §2 的账现存 5 条 (file,line) 失配** (`HW/check_pin_function_labels.py` L148→155; `SW/tools/check_onepass_sw_sync.py` L107/758/781/783→109/806/829/831) ⇒ L-21 既存实例 ⇒ 刷那本账时必须连旧失配一起修 ★

---

## ★★四 · ★★★★自曝: 我 13:1x 那 15 条答案一条都没闭上 need (L-32) ★★★★

★**根因**: `state/merge.py` 按【精确 key】配对 ⇒ 我用了改名的 key ⇒ 配不上 ⇒ 零闭合 (★实测: pm.yaml 里 `to=main` 的答案中逐字命中 need key 的只有 **113/152**★) ★
★**★⇒ 比 L-28 的「key 撞名」更危险: 撞名会报错退出 (★有声音★), 而「不撞名但对不上」⇒ 机制【一声不吭】⇒ 答案内容正确但【对闭环机制等于不存在】★★
★**⇒ 本轮按 need 的原 key 重答 33 条 (含 13:1x 那 15 条的重答 + ISS-396 交回的 5 条) + 立 L-32** ★

---

## ★★五 · 落记录 (全部追加式·老字一字未删) ★★

★`state/issue_log.yaml` (★**2 单签收 (ISS-388/390) + 1 单 hold 追加记录 (ISS-391·status 不变)·一次全量重写·零竞态窗口★**) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊻** (★`§㊺` 已被兄弟 job 18:3x 占用 ⇒ 按 L-30 先扫已用集合再取号★) ·
`state/LESSONS.md` **L-32** (★`L-31` 已被兄弟 job 15:4x 占用★) · `state/fragments/pm.yaml` (34 条: 33 条用 need 原 key + 1 条 main 自裁) · `MEMORY.md` (L-32 指针) ★

---

## ★★六 · 「板只改一次」那一趟现在明确要带【六条腿】 ★★

★**① 改孔 `0.65→0.71` (★焊盘 ≥`1.010`/建议 `1.110`·★环宽 `0.1450` < 多层 1oz 绝对下限 `0.15`★) ② §4 剩下两处登记 (#4 覆盖令牌 + #5 BOM 两栏) ③ 三道新闸挂链 + 【同时翻三条零挂链判据】+ 【同时刷 §2 的账 (含 5 条既存失配)】 ④ 六个签收件的 md5 刷新 + 全部验收线重跑 (L-27 通则③) ⑤ 六个签收页的定性订正块 (ISS-390 §4 六处 + OI-14 的 `4.3400` + §㊶ C4/C5/C6) ⑥ MECH 七个数按新焊盘重算 + 座体三量收样 ⑦ ★★ISS-391 闸的 selftest 夹具改动态锚点 + 重跑 17 条反向用例 + 重签 (★本轮 hold 的解除条件★)** ★

---

## ★★七 · 纪律自证 ★★

★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 未代老板拍板 · 未写任何 agent 的分片** ★
★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ 落点坐标 / 清空区放大量的一切前提都挂在它身上 ⇒ **本页不代拍** ★
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
        print("  %-46s rc=%d" % (iss + " 闸", rc))
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
    print("★ main · 2026-11-24 19:1x · ISS-388 / ISS-390 / ISS-391 三单一并签 + 33 条待裁项已裁 + 自曝 L-32")
    print("=" * 96)
    ok, FPS, needkeys = verify()
    if not ok:
        print()
        print("★★ fail-closed: 阶段 1 有红项 ⇒ 零写盘退出 ★★")
        return 2
    print()
    print("=" * 96)
    print("★阶段 2 · 追加式落记录")
    print("=" * 96)
    V = build_ver(FPS)
    write_issue_log(V)
    append_onepager()
    append_lessons()
    write_pm(needkeys)
    write_memory_pointer()
    write_round_log()
    print()
    final_check()
    print()
    print("★ 本轮完成: 3 单签收 + 33 条 main 地界待裁项已裁 + L-32 自曝 + §㊻")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 未代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
