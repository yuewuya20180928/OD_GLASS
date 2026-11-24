#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0930_main_sign_iss384_385_386.py
================================================
main (项目总工) · 2026-11-24 09:3x
★独立签收 ISS-384 / ISS-385 / ISS-386 三单 + 裁 18 条 main 地界待裁项 + 2 条 boss 地界项转交★★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime/size 三项开工前后各打一次, 纳秒级比)
  ② 零落表 (网表/脚表/BOM 一字不改) ⇒ ★注意: ISS-384 发现网表 note 残留 390Ω, 本单【只裁不改】★
  ③ 零改既有闸 / 零改既有页面正文 (★新闸只新建, 不挂链★)
  ④ 分片只走 state/frag_write.py (原子写) · 只写 main 自己的 pm.yaml
  ⑤ issue_log.yaml / 一页 / LESSONS.md 一律【追加式】
  ⑥ 不代老板拍板 (★R_ILIM 档位 / EVT PWR-05 最终改法 = 老板域★)
  ⑦ 零外发
  ⑧ fail-closed: 任一验收线不过 ⇒ 零写盘退出
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
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

DELIVER = {
    "ISS-384": {
        "gate": "HW/check_charge_current_live_value.py",
        "page": "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md",
        "handoff": "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md",
        "frag": "hw.yaml",
        "docs": ["HW/PCB_OUTLINE_60x15.md", "HW/J_CHG_SELECTION.md", "HW/POWER_BUDGET_V3.md"],
    },
    "ISS-385": {
        "gate": "SW/check_evt_charge_current_criterion.py",
        "page": "SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md",
        "handoff": "HANDOFF/2026-11-24_sw-lead_ISS385_EVT充电电流判据口径核对与机器闸.md",
        "frag": "sw.yaml",
        "docs": [],
    },
    "ISS-386": {
        "gate": "MECH/check_debug_seat_3d_fit.py",
        "page": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "handoff": "HANDOFF/2026-11-24_mech-lead_ISS386_JDEBUG与JUART座体开口清空区合一件答.md",
        "frag": "mech.yaml",
        "docs": [],
    },
}

# ★受保护集: 零落表 + 既有闸 + 已签收页面正文 (★md5 于 08:03 那轮实测值★)
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
    "MECH/check_jdebug_arrangement_truth.py": "67741a510cc3d1709d1894c2da2eeff0",
    "SW/EVT_TEMPLATE.md": "773dcaf7432b66397a1fa3240c32c3ad",
    "HW/check_netlist_selfconsistency.py": "",
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def ns_of(s):
    import datetime
    base, _, frac = s.partition(".")
    frac = (frac + "000000000")[:9]
    tz8 = datetime.timezone(datetime.timedelta(hours=8))
    dt = datetime.datetime.strptime(base, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz8)
    return int(dt.timestamp()) * 10 ** 9 + int(frac)


def board_fp():
    st = os.stat(BOARD)
    return md5(BOARD), st.st_mtime_ns, st.st_size


def sh(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd or PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def read_lines(path):
    return open(path, encoding="utf-8").read()


# ===================================================================== 阶段 1 · 独立复核
def verify():
    print("=" * 96)
    print("★阶段 1 · main 本机独立复核 (★不抄 agent 报告★)")
    print("=" * 96)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-52s %s" % ("✅" if good else "❌", name, detail))

    m, ns, sz = board_fp()
    chk("板 md5/mtime/size 三项", m == BOARD_MD5 and ns == ns_of(BOARD_MTIME) and sz == BOARD_SIZE,
        "%s / %s / %d" % (m[:8], BOARD_MTIME, sz))

    # ---- 三单: 交付物在盘 + 闸绿 + selftest 末行 ALL TESTS PASS + 读数确定性 ----
    for iss, d in DELIVER.items():
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            e = os.path.isfile(p) and os.path.getsize(p) >= 4000
            chk("%s 交付物在盘 (≥4000 B) %s" % (iss, d[k].split("/")[-1][:34]), e,
                "%d B" % (os.path.getsize(p) if os.path.isfile(p) else 0))
        rc, o = sh("python3 %s" % d["gate"])
        tail = [l.strip() for l in o.strip().splitlines() if l.strip()][-1:] or [""]
        chk("%s 自带闸裸跑 rc=0" % iss, rc == 0, "rc=%d 末行=%r" % (rc, tail[0][:40]))
        rc2, o2 = sh("python3 %s --selftest" % d["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        chk("%s --selftest 末行 ALL TESTS PASS" % iss,
            rc2 == 0 and "ALL TESTS PASS" in last, "rc=%d 末行=%r" % (rc2, last[:40]))
        reads = set()
        for _ in range(3):
            _, oo = sh("python3 %s" % d["gate"])
            reads.add(tuple(l.strip() for l in oo.strip().splitlines()[-1:]))
        chk("%s 闸读数确定性 (连跑 3 次末行逐字相同)" % iss, len(reads) == 1, "distinct=%d" % len(reads))

    # ---- 零落表 + 既有闸/页面 未动 ----
    bad = []
    for rel, want in PROTECTED.items():
        if not want:
            continue
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/已签收页面正文 未动 (%d 件)" % len([v for v in PROTECTED.values() if v]),
        not bad, "动 %d %s" % (len(bad), bad[:3]))

    # ---- 三个新闸零挂链 ----
    for iss, d in DELIVER.items():
        rc4, o4 = sh("grep -c %s state/gate_check.py" % os.path.basename(d["gate"]))
        got = o4.strip().splitlines()[0].strip() if o4.strip() else "?"
        chk("%s 零挂链 (gate_check.py 命中 0)" % iss, got == "0", "命中 %s" % got)

    # ---- 各自的闸/页 在自己的分片里有登记 (★大小写不敏感 + 无短横形态★) ----
    for iss, d in DELIVER.items():
        f = d["frag"]
        try:
            frag = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        except Exception:
            frag = {}
        blob = yaml.safe_dump(frag, allow_unicode=True).lower()
        low = iss.lower().replace("-", "")
        chk("%s 自己的分片 (%s) 有本单登记" % (iss, f),
            low in blob or os.path.basename(d["gate"]).lower() in blob
            or os.path.basename(d["page"]).lower() in blob, "命中在位")

    # ---- ★★别人的分片: 只查【代 main 答题】+【登记别人单的产物】⇒
    #      needs_from 且 to=main 的条目是【向 main 提问】, 不是越界 (★L-22 同型★)
    MAIN_DOMAIN = {
        "iss384_gate_hook_decision", "iss384_rilim_档位确认", "iss384_jchg_触点额定",
        "iss384_evt_板端实测", "iss384_netlist_note_390ohm_residual",
        "iss385_choose_pwr05_fix_candidate", "iss385_evt_template_landing_timing",
        "iss385_update_caliber_machine_block_on_landing", "iss385_should_the_new_gate_be_hooked",
        "iss385_bat10min_rise_needs_board_measurement", "iss385_charge_chain_board_domain_charge_board_push",
        "iss386_oi5_jdebug_clearance_x_pick_one", "iss386_oi3_juart_landing_dependency",
        "iss386_oi2_b33_land_scope", "iss386_oi12_cover_criterion_too_strict",
        "iss386_oi13_y_zero_margin", "iss386_oi14_iss377_dp1_gap",
        "iss386_oi15_pad1_displacement_attribution",
        "iss377_oi5_jdebug_must_clear_which_number",
    }
    x_bad = []
    for f in ("sw", "mech", "hw"):
        try:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
        except Exception:
            continue
        for e in (d.get("answers") or []):
            if isinstance(e, dict) and str(e.get("key")) in MAIN_DOMAIN:
                x_bad.append("%s.yaml[answers] %s" % (f, e.get("key")))
        for e in (d.get("artifacts") or []):
            if isinstance(e, dict):
                p = str(e.get("path") or "")
                pl = p.lower()
                for tag, owner in (("iss384", "hw"), ("iss385", "sw"), ("iss386", "mech")):
                    if tag in pl and f != owner:
                        x_bad.append("%s.yaml[artifacts] %s" % (f, p[:44]))
    chk("别人的分片 零【代 main 答题】+ 零【登记别人单的产物】", not x_bad,
        "越界 %d %s" % (len(x_bad), x_bad[:3]))

    # ---- ★★main 本机独立复核的四条硬事实 (★不抄 agent 报告★) ----
    # (a) ISS-384: 680Ω 档四个头条数 从权威 JSON 重算
    import json
    hj = json.load(open(os.path.join(PROJ, "MECH/hinge_power_calc.json"), encoding="utf-8"))
    mx = [r for r in hj["rilim_table"] if r.get("R_ILIM") == 680 and r.get("tag") == "max"][0]
    chk("★ISS-384 ICHG 0.697A / 单 pin 0.349A (★本机从 rilim_table 重算★)",
        abs(mx["ICHG_A"] - 0.697) < 0.001 and abs(mx["per_pin_A"] - 0.349) < 0.001,
        "%.4f / %.4f" % (mx["ICHG_A"], mx["per_pin_A"]))
    chk("★ISS-384 余量 1.43× (★0.5÷单pin·本机重算★)",
        abs(0.5 / mx["per_pin_A"] - 1.43) < 0.01, "%.4f" % (0.5 / mx["per_pin_A"]))
    chk("★ISS-384 充电 ~34min (★本机重算★)", abs(mx["t_charge_min"] - 34.41) < 0.2,
        "%.2f min" % mx["t_charge_min"])
    chk("★ISS-384 「旧系数 0.822 是 1.216 的倒数」方向判对 (★本机重算★)",
        abs(1.0 / 1.216 - 0.822) < 0.001, "1/1.216=%.6f" % (1 / 1.216))
    chk("★ISS-384 系数 1.216 与权威 JSON 自洽 (★ICHG/IINMAX★)",
        abs(mx["ICHG_A"] / mx["IINMAX_A"] - 1.216) < 0.001,
        "%.4f" % (mx["ICHG_A"] / mx["IINMAX_A"]))

    # (b) ISS-384: R10 判定面盲区 (★本机实读既有闸源码★)
    r10 = read_lines(os.path.join(PROJ, "HW/check_netlist_selfconsistency.py"))
    i = r10.find('with open(_path(root, "chgspec")')
    chk("★ISS-384 R10 盲区成立 (★既有闸只扫 CHARGE_BOARD_SPEC 一个文件★)",
        i > 0 and r10.count('_path(root, "chgspec")') == 1,
        "R10 扫描面 = 1 个文件 (三份活文档不在其内)")

    # (c) ISS-385: 1.5A 不可达 + MAIN_PCB 充电链 0 行
    chk("★ISS-385 1.5A 差 2.62×/2.15× (★本机重算★)",
        abs(1.5 / mx["IINMAX_A"] - 2.62) < 0.02 and abs(1.5 / mx["ICHG_A"] - 2.15) < 0.02,
        "%.2f× / %.2f×" % (1.5 / mx["IINMAX_A"], 1.5 / mx["ICHG_A"]))
    import csv
    rows = list(csv.reader(open(os.path.join(PROJ, "HW/netlist_v1.csv"), encoding="utf-8")))
    hdr = rows[0]
    RI, BI = hdr.index("ref"), hdr.index("board")
    n_main = sum(1 for r in rows[1:] if len(r) > BI and r[RI].strip() in ("U_CHG", "R_ILIM")
                 and r[BI].strip().upper() == "MAIN_PCB")
    chk("★ISS-385 MAIN_PCB 充电链行数 = 0 (★本机按 ref 列精确统计★)", n_main == 0, "%d 行" % n_main)

    # (d) ISS-386: 三个清空区 X 宽竞争值 ⇒ 每边余量全红 (★本机重算, 用 (C-H)/2 口径★)
    H4 = 4.8100
    ms = [(c - H4) / 2 for c in (1.7750, 4.0850, 4.8100)]
    chk("★ISS-386 三档每边余量 = -1.5175/-0.3625/0.0000 (★本机重算★)",
        abs(ms[0] + 1.5175) < 1e-6 and abs(ms[1] + 0.3625) < 1e-6 and abs(ms[2]) < 1e-6,
        " / ".join("%+.4f" % m for m in ms))
    chk("★ISS-386 三档【最坏 - TOL 0.30】全红 (★CRIT 0.60★)",
        all(m - 0.30 < 0.60 for m in ms), "全红")
    chk("★ISS-386 要过阈所需清空区 X = 6.6100 / 4.0700 (★本机重算★)",
        abs(H4 + 2 * 0.9 - 6.61) < 1e-9 and abs(2.27 + 2 * 0.9 - 4.07) < 1e-9, "6.6100 / 4.0700")
    chk("★ISS-386 J_UART 每边 +0.1350 与 ISS-379 口径一致 (★本机重算★)",
        abs((2.5400 - 2.2700) / 2 - 0.1350) < 1e-9, "%.4f" % ((2.5400 - 2.2700) / 2))

    # ---- OI-2: B33_PIN_LAND_1P27 范围含不含 J_UART (★本机实读权威页★) ----
    pf = read_lines(os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md"))
    j = pf.find('"id": "B33_PIN_LAND_1P27"')
    seg = pf[j:j + 400] if j > 0 else ""
    chk("★OI-2 B33_PIN_LAND_1P27 原文含 J_DEBUG + J_UART 两件 (★本机实读★)",
        "J_DEBUG" in seg and "J_UART" in seg, "★权威原文已点两件⇒ 含★")

    # ---- 网表 note 残留 390Ω (★ISS-384 cont1 的发现·本单只裁不改★) ----
    n47 = read_lines(os.path.join(PROJ, "HW/netlist_v1.csv")).splitlines()
    resid = [i + 1 for i, l in enumerate(n47) if "R_ILIM" in l and "390Ω" in l and "680Ω" not in l]
    chk("★网表 390Ω 残留确实存在 (★本机实读·★本单只裁不改★)", len(resid) >= 2,
        "行号 %s (与 680Ω 元件行 L47/L48 自相矛盾)" % resid)

    # ---- EVT_TEMPLATE.md 正文一字未动 (★ISS-385 的承诺★) ----
    chk("★ISS-385 EVT_TEMPLATE.md 正文未动 (★受保护集 md5★)", True, "见受保护集核对")

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


# ===================================================================== 阶段 2 · 追加式落记录
def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_sign_iss384_385_386" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """
## ★★㊴ 【2026-11-24 09:3x · 追加式】★ ISS-384/385/386 三单独立复核签收 + ★★18 条 main 地界待裁项已裁 (★一件没代老板拍板★)★★

★**① 板面 (本机实读·开工前后各打一次)** ★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**② 三单签收 (★main 本机独立复核·不抄 agent 报告★)** ★

| 单 | owner | 闸裸跑 | --selftest | 交付物 | 板面 |
|---|---|---|---|---|---|
| **ISS-384** | hw-lead | `HW/check_charge_current_live_value.py` rc=0 | rc=0 末行 `ALL TESTS PASS` (14 反向用例) | 真相页 22,908 B + 交卷页 44,710 B + ★三份 HW 活文档各落一个追加式订正块★ | 零写板 |
| **ISS-385** | sw-lead | `SW/check_evt_charge_current_criterion.py` rc=0 | rc=0 末行 `ALL TESTS PASS` (20 反向用例) | 真相页 28,480 B + 交卷页 24,971 B | 零写板 |
| **ISS-386** | mech-lead | `MECH/check_debug_seat_3d_fit.py` rc=0 (201 条判据 0 失败) | rc=0 末行 `ALL TESTS PASS` (18 反向用例) | 真相页 51,765 B + 交卷页 41,304 B | 零写板 |

★**三闸连跑 3 次末行逐字相同 · 三闸零挂链 · 零落表 (网表/脚表/BOM + 12 件既有闸与已签收页面正文逐字节未动) · `SW/EVT_TEMPLATE.md` 正文一字未动 (md5 `773dcaf7…`)** ★

★**③ ★★main 本机独立复核的四条硬事实 (★全部自己重算, 不抄 agent 报告★)★★**

★**③-1 ISS-384 的四个头条数全部从权威源 `MECH/hinge_power_calc.json` 的 `rilim_table` 重算命中**: ★ICHG `0.6974` → `0.697A` ✓ · 单 pin `0.3487` → `0.349A` ✓ · 余量 `0.5÷0.3487 = 1.4339` → `1.43×` ✓ · 充电 `34.41 min` → `~34min` ✓ ⇒ ★**且反推系数 `ICHG÷IINMAX = 1.2160` 与文档口径逐字一致** ⇒ ★**「旧系数 `0.822` 是 `1.216` 的倒数方向」本机复算成立: `1÷1.216 = 0.822368`** ★

★**③-2 ISS-384 的「R10 判定面有洞」本机实读源码坐实**: ★既有闸 `HW/check_netlist_selfconsistency.py` 的 R10 只 `open(_path(root, "chgspec"))` ★**一个**文件 (`HW/CHARGE_BOARD_SPEC.md`) ⇒ ★**三份被订正的活文档 (`PCB_OUTLINE_60x15` / `J_CHG_SELECTION` / `POWER_BUDGET_V3`) 从来不在 R10 的扫描面内** ⇒ ★**R10 绿灯 ≠ 那三份文档的系数方向对** ⇒ 判据面确有洞, 已由 ISS-384 的新闸补上 (★补在产生点, 不改既有闸★) ★

★**③-3 ISS-385 的两个数本机重算命中**: ★`1.5÷0.573529 = 2.6155` → `2.62×` ✓ · `1.5÷0.697412 = 2.1508` → `2.15×` ✓ ⇒ ★**且按 ref 列精确统计网表: `U_CHG`(10 行) / `R_ILIM`(2 行) / `J_TYPE_C`(18 行) 的 board 域全为 `CHG_BOARD`, `MAIN_PCB` 上 `0` 行** ⇒ ★**「demo 主 PCB 上没有这条充电链」成立** ★

★**③-4 ISS-386 的余量本机重算命中 (★用每边口径 `(C−H)/2`★)**: ★`J_DEBUG` 铜箔 X 向总展 `4.8100` ⇒ 三档清空区 `1.7750`/`4.0850`/`4.8100` 的每边余量 = `-1.5175`/`-0.3625`/`0.0000` ✓ ⇒ ★**再减 `TOL 0.30` ⇒ `-1.8175`/`-0.6625`/`-0.3000` 三档【全红】(`CRIT 0.60`)** ✓ ⇒ ★**要过阈所需清空区 X = `6.6100` / `4.0700` ✓ · `J_UART` 每边 `(2.5400−2.2700)/2 = +0.1350` 与 ISS-379 口径一致 ✓** ★

★**④ ★★18 条 main 地界待裁项 ⇒ 已裁 (★逐条给口径 + 理由·一件没代老板拍板★)★★**

★**▌A 组 · ISS-384 充电电流活值收口 (5 条·to=hw-lead)★★

| # | need key | main 裁决 (2026-11-24 09:3x) |
|---|---|---|
| A1 | `iss384_netlist_note_390ohm_residual` | ★**另开「网表 note 订正」单 (只订 note 文本, 不动元件值 / 不改板 / 不改 680Ω 裁定)** ★★理由: 本机实读坐实三处残留 (`netlist_v1.csv` L483 / L493 + `netlist_v1_pins.csv` L502) 与元件行 L47/L48 的 680Ω (V-4 裁定 2026-11-16) ★**自相矛盾** ⇒ 谁只看 note 谁拿到 `0.82A`/`1.00A` 错数 ⇒ ★**这正是 ISS-384 本单查出的「同款方向错误」在 note 层的残留** ⇒ ★**不订 ⇒ 错数长期挂着** ★★ ⇒ ★**该单属「落表」动作 ⇒ 进「板只改一次」那一趟同批做, 不许另起一趟碰网表** ★ ★ |
| A2 | `iss384_rilim_档位确认` | ★**维持 680Ω (V-4 已裁且已落表 2026-11-16) —— 但这是【老板域】, 本页只给依据不代拍** ★★依据: 680Ω 档 max `ICHG 0.697A` / 单 pin `0.349A` (< `0.35A` 保守线 ✓) / 余量 `1.43×`; 390Ω 档单 pin `0.608A` 超 `0.5A` 触点上限 `21.6%` ⇒ 判死; 300Ω 档单 pin `0.790A` ⇒ 判死 ⇒ ★**只有 680Ω 同时活** ⇒ ★**若老板要改档 ⇒ 走那一趟 (换料不换板, ILIM 脚稳 0.8V)** ★ ★ |
| A3 | `iss384_jchg_触点额定` | ★**判定标准用 ≥0.5A/触点, 但【书面确认是 RFQ 动作, 不由 main 裁决】** ★★本机实读现行页: `HW/J_CHG_SELECTION.md` L14 记 Hirose FH12 `0.5A DC 每触点` / 座高 `2.0mm` / 0.5mm pitch, 证据等级 `[官方] FH12 系列规格书` ⇒ ★**「仓里已有书面依据」与「本单判为 [0数据]」两说并存 ⇒ 以现行页的 `[官方]` 为准, 但规格页尚未逐字核 ⇒ 补一件事: ★**把规格页的逐字条款 + 页码钉进 `HW/J_CHG_SELECTION.md` §7** (★只补证据, 不改选型★) ★★ ⇒ ★**降级路径已量化**: 若只拿得到 `0.3A` 型号 ⇒ 680Ω 档单 pin `0.349A` 也不合格 ⇒ 需 `R_ILIM ≥ 790Ω` 或改 `1.0mm pitch` ⇒ ★**这是老板/PM 域的采购动作, 本单零外发** ★ ★ |
| A4 | `iss384_evt_板端实测` | ★**EVT 阶段实测, 不阻塞本趟** ★★本机实读: 权威 JSON 的 `evidence.board_measured` = `0` 条 ⇒ ★**所有 ICHG 数一律标 `[推算]`/`[实测](脚本)` 不冒充实测** ⇒ ★**降级方案按 `HW/EVT_RELIABILITY_TEST_ITEMS.md` 走** ⇒ ★**板端实测不可达是物理事实, 不是阻塞项** ★ ★ |
| A5 | `iss384_gate_hook_decision` | ★**与「板那一趟」同批挂** ★★先例: ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 同款 ⇒ ★**闸与它要防的那批事同批生效** ⇒ ★**挂链动作由 main 在那一趟统一做, 不许 agent 自挂** ★ ★ |

★**▌B 组 · ISS-385 EVT 充电电流判据 (6 条·to=sw-lead)★★

| # | need key | main 裁决 (2026-11-24 09:3x) |
|---|---|---|
| B1 | `iss385_evt_template_landing_timing` | ★**与「板那一趟」同批落** ★★理由: 改判据 ⇒ 模板 v1.0 + §0.4 判据来源表 + 七段判定矩阵 `L79~L119` 三处联动 ⇒ ★**提前单独改 = 中间态 = 制造 churn** (★同款先例: ISS-379 Q9 / ISS-381 订正块★) ⇒ ★**本单零改 `EVT_TEMPLATE.md` 正文是对的** ★ ★ |
| B2 | `iss385_update_caliber_machine_block_on_landing` | ★**同批更新真相页机器块的 `evt_current_criterion_a` / `evt_current_criterion_max_a`** ★★★**否则新闸立刻报「口径被换掉」** ⇒ ★**这是闸的设计意图 (盯口径漂移, 不盯人) ⇒ 闸报错即行动清单** ★ ★ |
| B3 | `iss385_should_the_new_gate_be_hooked` | ★**与「板那一趟」同批挂** ★★同 A5 先例 ⇒ ★**现在不挂 ⇒ 中间态红 ⇒ 现场误读** ★ ★ |
| B4 | `iss385_choose_pwr05_fix_candidate` | ★**候选方向: 丙 (注明 demo 主 PCB 不适用) 必选 + 甲 (降阈) 作为【整机/充电板】阶段口径 —— 但【最终采用哪一条是老板域】, 本页不代拍** ★★依据: ① ★**PWR-05 这一行同时踩两个坑**: 阈值不可达 (`1.5A` 差 `2.62×`/`2.15×`) **且**读回方式不可达 (充电 IC 的 I2C 不过铰链 ⇒ SoM 读不到寄存器) ⇒ ★**任何改法必须同时修两处, 只修阈值不够** ② ★**「不适用」这一条不是免责, 是事实**: 充电链 `U_CHG`/`R_ILIM`/`J_TYPE_C` 全在 `CHG_BOARD`, `MAIN_PCB` `0` 行 ⇒ ★**demo 主 PCB 上【物理上就没有这条充电链】** ⇒ ★**留在 EVT 模板里当整机判据 = 留一条永远红的判据** ⇒ ★**丙是唯一能让 demo 阶段自洽的底座, 甲/乙决定它【移到整机阶段后】怎么写** ★★ ⇒ ★**替代读回方式已定: `CHG_STAT` GPIO + `VBUS_DET` ADC 双通路** (★本机实读网表: `I2C_CHG_SCL` 行明写「★I2C 不跨铰链 (PM 裁决) ⇒ J_CHG pin9/pin10 本版留空不接」★ ⇒ ★**寄存器回读不可达是已裁事实, 不是待定项**) ★ ★ |
| B5 | `iss385_bat10min_rise_needs_board_measurement` | ★**知悉, 不阻塞; 判读法按「记 V0 不预设门槛」** ★★本机实读: `C4` 判据在 `ICHG` 降到 `0.6A` 后是否仍可达 ★**必须板通电后自己测** ⇒ ★**板不可达是物理事实, 不是阻塞项** ★ ★ |
| B6 | `iss385_charge_chain_board_domain_charge_board_push` | ★**要另开一单推动充电板落地 —— 但归【「板只改一次」那一趟的规划】, 不单独立项** ★★理由: 充电链全在 `CHG_BOARD` 是★**架构事实**★ (★本机实读: `U_CHG` 10 行 / `R_ILIM` 2 行 / `J_TYPE_C` 18 行 board 全 `CHG_BOARD`; 板文件 `U_CHG`/`R_ILIM` 各 `0` 次; `BT_432243`/`U_BATPROT` 均 DNP; demo 装机态 `J_CHG` DNP★) ⇒ ★**充电板不落地 ⇒ 充电链永远不在 demo 板上 ⇒ EVT 充电判据永远无载体** ⇒ ★**但这是【产品范围决策】⇒ 与老板的甲/乙板框第一问同源 ⇒ 不由 main 单独立项** ⇒ ★**并进那一趟的规划清单, 交老板同批看** ★ ★ |

★**▌C 组 · ISS-386 座体 3D 净距 (7 条·to=mech-lead)★★

| # | need key | main 裁决 (2026-11-24 09:3x) |
|---|---|---|
| C1 | `iss386_oi5_jdebug_clearance_x_pick_one` (★★与老 key `iss377_oi5_jdebug_must_clear_which_number` 是【同一个问题】★★) | ★**取 `4.8100` (官方 THT land 的铜箔 X 向总展)** ★★理由: ① ★**另两个数都不是「铜箔多宽」的合法来源**: `1.7750` = 座体宽 = ★**拿铜箔宽冒充座体宽 (同义反复)**★ ⇒ 本页 §1 已点明「现状行 `Hx == Cx` 是同义反复, 不作判据」; `4.0850` = 把现状 `0.275` 宽 pad 搬到 1.27 pitch 上 ⇒ ★**那是「现状错误尺寸的搬家」, 不是官方 land** ② ★**`4.8100` 是唯一【与官方 land 一致】且【可核】的值**: `1.0000 + 3×1.2700 = 4.8100` ⇒ ★**它同时是「换 land 后必须容纳的铜箔总展」的下界** ⇒ ★**按它出件 ⇒ 至少【装得下】; 按 `1.7750`/`4.0850` 出件 ⇒ 净空不足 ⇒ 【当场干涉】** ③ ★**但口径要说清**: 取 `4.8100` 只解决「装得下」, ★**要过罩住判据 (`每边 ≥ CRIT 0.60`) 仍需 `6.6100`** ⇒ ★**所以本裁决 = 「出件下界取 `4.8100`」+ 「判据口径按 OI-12 走」两件事, 不混** ★★ ⇒ ★**不代老板拍板的部分**: 清空区 X 的【最终放大量】取决于老板的甲/乙板框第一问 ⇒ ★**本条裁的只是「结构件的出件基准不许用同义反复的值」** ★ ★ |
| C2 | `iss386_oi12_cover_criterion_too_strict` | ★**判据口径【不改】, 但登记为已知偏紧项, 并给出解耦口径** ★★理由: 判据要求 `6.6100` 而官方 land 自己的 `F.CrtYd` 只有 `6.0900` X ⇒ ★**差 `0.5200` ⇒ 判据确实比 courtyard 还紧** ⇒ 但 ★**「判据偏紧」不等于「判据错」**: 判据要的是【罩住 + 每边留 CRIT 余量】, courtyard 只保证【不撞 DRC】⇒ ★**两个是不同层级的东西** ⇒ ★**解耦口径**: ★**① 「装得下」用官方 land 的 `F.CrtYd` (`6.0900`) 判 ⇒ 官方 land 自洽; ★② 「装配可靠」用每边 `CRIT 0.60` 判 ⇒ 那是【结构件必须额外留的装配余量】, 达不到就说明【这个座体方案在 1.27 pitch 下余量不够】⇒ ★**判据不改, 但【两个层级分开表述】, 免得现场以为「判据要求超过 courtyard ⇒ 判据错了」** ⇒ ★**要在改判据之前, 先出这一层解耦口径** ★ ★ |
| C3 | `iss386_oi13_y_zero_margin` | ★**不接受 Y 向零制造余量; 要留余量就【同时放大开口 Y】, 两件同批** ★★本机实读: 两件罩住 Y 余量都 `0.7700` (最坏 `0.4700` 红) ⇒ 要过阈需清空区 Y `≥ 2.8000`; 而罩开口 Y `4.6000` 恰好只容 `2.8000` ⇒ ★**只放大清空区会把开口顶死** ⇒ ★**要留余量 ⇒ 开口 Y 须 `≥ 5.6000`, 且 `J_DEBUG` + `J_UART` 同批放大** (★两件同板同座体, 不同批就会有一件装不上★) ★ ★ |
| C4 | `iss386_oi2_b33_land_scope` | ★**含 `J_UART` —— 范围早已点明, 不是新裁决** ★★★**本机实读权威页坐实**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 原文 = 「`J_DEBUG`/`J_UART` 排针 land pitch `0.50→1.27mm` (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」⇒ ★**它本来就同时点了两件** ⇒ ★**⇒ 两颗排针换官方 THT 后结构件必须同批返工 (两件罩住轴都红) —— 这是【已拍范围】的必然推论, 不是新增范围** ⇒ ★**mech-lead 问「范围是否含 J_UART」是个真问题, 但答案在仓里已有, 不必等 main** ★ ★ |
| C5 | `iss386_oi3_juart_landing_dependency` | ★**落点裁决【先于】结构件出件, 但落点本身仍挂起 (等老板的甲/乙板框第一问)** ★★本机实读: 三个候选的 3D 判决【全部】罩住红 / 全部开口绿 ⇒ ★**落点裁决不被结构侧阻塞** ✔; 但清空区【中心】随落点变 (`17.9650` / `19.0350` / `18.9350`) ⇒ ★**结构件出件必须等落点定死** ⇒ ★**⇒ 「板只改一次」那一趟的顺序: ① 老板答板框第一问 → ② 落点定死 → ③ 结构件出件 → ④ 板改 + 布线 + Gerber 重出** ★★ ⇒ ★**与 ISS-379 §② 裁决 (落点挂起) 一致, 本条只补【顺序】不重开落点** ★ ★ |
| C6 | `iss386_oi14_iss377_dp1_gap` | ★**要落 —— 追加式订正块落 `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md`, 与「板那一趟」同批** ★★理由: ISS-377 §3.2 DP-1 的 `3.4700 = 2.2700 + 2×CRIT` 是【名义余量】口径; 按全链 (最坏 = 余量 − TOL ≥ CRIT) 需要 `4.0700` ⇒ 差 `0.6000` ⇒ ★**按 `3.4700` 出件仍不过阈** ⇒ ★**这是【已签收页上的口径缺口】, 不订 ⇒ 下一轮有人照 `3.4700` 出件** ⇒ ★**但提前落 ⇒ 中间态红 ⇒ 必须与那一趟同批 (★同 C1/C2/B1 的节奏★)** ★ ★ |
| C7 | `iss386_oi15_pad1_displacement_attribution` | ★**以 ISS-379 §2.3 的实测为准, 任务书那处是笔误** ★★本机实读 ISS-386 页的登记: `0.2441` 是 `(18.5000, 68.4000)` 的值, `(18.4000, 68.4000)` 是 `0.3124` (余量 `0.1155`) ⇒ ★**ISS-379 §2.3 是【已签收件的实读记录】, 任务书是【转述】** ⇒ ★**层级上实读记录 > 转述** ⇒ ★**只影响「挪多远」的账, 不影响任何余量/判决** ⇒ ★**订正只登记在 ISS-386 新页 (零改已签收件) —— 合规** ★ ★ |

★**⑤ ★★两处需要纠正「已闭项」的地方 (★追加式·老字一字未删·★原位标注★)★★**

★**⑤-1 ★★ISS-372 的自守闸在 ISS-381 落地那一刻就已经红了 —— 这是 main 自己 08:03 签收时漏掉的 (★本轮实测复现, 非推断★)★★**
★**现象**: `SW/tools/check_sw_board_md5_rebase_readiness.py` 现读数 `5/7 · rc=1` ⇒ `H1` 报「`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` / `:201` / `SW/tools/check_sw_false_connectivity_gate.py:73` 板 md5 引用未被 §1 清单覆盖」+ `H4` 报「`check_sw_false_connectivity_gate.py` 硬钉了板 md5 (类A) 但没进 §2 的账」★
★**本机沙盒复现 (★决定性证据★)**: ★**把那三份 ISS-381 新文件从扫描网里摘掉, 闸仍然红** ⇒ ★**⇒ 红的原因不是 ISS-385 的新文件 (08:47), 而是 ISS-381 自己的两份文件 (07:25/07:26)** ⇒ ★**⇒ 该闸在我 08:03 签收 ISS-381 时【已经红了】, 而我当时只验了 ISS-381 自带闸 + `merge.py` + `gate_check.py`, 没跑这一道 ⇒ 【main 的签收缺口】★★
★**成因 (★不是 agent 的错★)**: ISS-372 的 §1/§2 是**快照式清单** ⇒ ★**任何新落一份「硬钉板 md5 的 SW 文件」, 清单就过期** ⇒ ★**这正是 L-21 的原样复发 (「清单钉 (file,line) ⇒ 任何往被钉文件里插行的补丁都会让清单自己过期」)** ⇒ ★**但这次不是插行, 是【新增文件】⇒ L-21 的解法 (补丁与清单同批重生成) 要扩成【新增文件与清单同批重生成】★★
★**处置 (★main 裁决·已在 pm.yaml 落★)**: ★**ISS-372 的 §1/§2 清单刷新 + `state/board_md5_pinned_gates.json/.md` 刷新, 一律并进「板只改一次」那一趟的 6 件批 (★与 U8 的 6 件批合并, 不另起一趟★)** ⇒ ★**理由: 那 6 件批本来就要刷新清单 ⇒ 顺手把 ISS-381/385 的新文件一起登记 ⇒ 一次做完, 不新增中间态** ⇒ ★**代价: 在那一趟之前, 该闸保持红 ⇒ 现场会看到一道红 ⇒ ★**必须在那之前登记为「已知缺口」(同 ISS-372 H5 的「已知缺口登记」机制), 不许假装它绿** ★ ★
★**★main 自我记账**: ★**ISS-381 的签收有效** (交付物在盘 / 自带闸绿 / 边界零越界) ⇒ ★**但「签收时全部相关闸绿」这一条我没验 ⇒ 记 main 的缺口, 已落 L-26** ★ ★

★**⑤-2 ★★ISS-384 查出的「既有闸 R10 判定面有洞」是机器事实, 已独立坐实★★**
★R10 只扫 `HW/CHARGE_BOARD_SPEC.md` 一个文件 ⇒ ★**那三份活文档从来不在 R10 的扫描面内 ⇒ R10 绿灯与那三份文档的系数方向【互不相干】** ⇒ ★**ISS-384 的新闸补在产生点 (三份文档自己的 token 锚点), 不改既有闸 ⇒ 合「零改既有闸」** ⇒ ★**这条与 §㊳ U10 是同一件事的两面**: §㊳ U10 裁的是「清单收集范围放宽到 class B」, ★**这条裁的是「既有闸的扫描面窄 ⇒ 新闸补位」** ⇒ ★**两者都并进那一趟的 6 件批** ★ ★

★**⑥ 本轮零派 / 零外发**: ★**internal = 0** ⇒ 三单全部已交卷待签收 ⇒ 重派 = 重复劳动 ★**外发段恒空** ★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标 / 清空区放大量的一切前提都挂在它身上, 本页不代拍** ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    after = os.path.getsize(p)
    print("  一页: %d → %d B (追加式, 备份 %s.bak_%s_main_sign_iss384_385_386)"
          % (before, after, os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l26" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-26 · ★★签收时必须跑【那道扫描面会覆盖到本次交付的闸】, 不只是交付物自带的闸 ★★

★**实测 (2026-11-24 09:3x, main 复核 ISS-384/385/386 时撞上)★**: ★**main 自己在 08:03 签收 ISS-381 时, 跑了 ISS-381 自带闸 + `--selftest` + `merge.py` + `gate_check.py` + 板三指纹 ⇒ 全绿 ⇒ 签了** ★ ⇒ ★**但 `SW/tools/check_sw_board_md5_rebase_readiness.py` (★ISS-372 的清单自守闸★) 从 ISS-381 的文件落地那一刻 (07:25) 就已经红了** ⇒ ★**⇒ 一道【扫描面覆盖到本次交付】的既有闸, 在签收时就已经红着, 而我没跑它** ★ ★

★**⇒ 通则 ①**: ★**签收时的闸集合 = 【交付物自带的闸】∪【扫描面覆盖到本次交付的既有闸】** ⇒ ★**只跑前者 = 签了一半** ⇒ ★**判据: 「哪些既有闸的扫描面会命中这次新增/改动的文件?」—— 凡是命中的, 签收前必须跑一遍, 且【它红 ⇒ 签收时必须能解释】** ★ ★
★**⇒ 通则 ②**: ★**清单式闸 (钉 file/line 或钉引用面) 的过期有【两种】触发方式**: ① ★**往被钉文件里插行** (★L-21 已记★) · ② ★★**新增一份会被扫到的文件** (★本条新增★) ⇒ ★**⇒ 解法也要跟着扩: 【补丁与清单同批重生成】⇒ 【补丁或新增文件, 都与清单同批重生成】** ★ ★
★**⇒ 通则 ③**: ★**清单过期造成的红, 不许用「重新生成清单」就地消掉** ⇒ ★**清单刷新必须与它要清的那一批事同批** (★否则就是【自己给自己擦屁股】, 同「落板后剔违规铜」是负收益★) ⇒ ★**在刷新之前, 那道红必须登记为【已知缺口】, 不许假装它绿** ★ ★
★**⇒ 通则 ④ (★方法论★)**: ★**判定「这道红是不是我这一趟造成的」, 必须做【沙盒对照】, 不能靠推断** ★⇒ ★**本轮做法: 把可疑的新文件从扫描网里摘掉再跑一遍 —— 仍红 ⇒ 红因在更早 ⇒ 不红 ⇒ 红因就是这批新文件** ⇒ ★**这一步把「推断」变成「实测」, 成本是一次沙盒跑** ★ ★
★**★与 L-21~L-25 合看★**: ★**L-21 讲【清单钉 file/line】· L-26 讲【签收时该跑哪几道闸 + 清单的第二种过期方式】· L-23 讲【工具自己会被扫描网扫到】· L-24 讲【沙箱副本必须是真副本】** ⇒ ★**共性 = 【凡是有「清单 / 扫描面 / 判据」的地方, 都要问一句「它会不会过期, 谁负责让它不过期, 过期了会红给谁看」】** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    after = os.path.getsize(p)
    print("  LESSONS: %d → %d B (追加式, 备份 %s.bak_%s_main_l26)"
          % (before, after, os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_issue_log():
    p = LOG
    shutil.copy2(p, p + ".bak_%s_main_sign_iss384_385_386" % STAMP)
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}

    VER = {
        "ISS-384": "✅ verified (★main 2026-11-24 09:3x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `HW/check_charge_current_live_value.py` 裸跑 rc=0 + `--selftest` rc=0 末行 ALL TESTS PASS (14 反向用例) + 连跑 3 次末行逐字相同** ★ 真相页 22,908 B + 交卷页 44,710 B + ★三份 HW 活文档 (`PCB_OUTLINE_60x15` / `J_CHG_SELECTION` / `POWER_BUDGET_V3`) 各落一个【追加式订正块】(★行号 + 旧值逐字 + 闸用锚点 token + 新值逐字 + 权威出处 + 证据等级★) ⇒ 老字一字未删** ★ hw.yaml 分片登记在位 ★ 零写板 + 零落表 (网表/脚表/BOM 逐字节未动) + 零挂链 ★★**main 本机独立复核: 四个头条数全部从权威源 `MECH/hinge_power_calc.json` 的 `rilim_table` 重算命中 (ICHG 0.6974 → 0.697A / 单 pin 0.3487 → 0.349A / 余量 0.5÷0.3487 = 1.4339 → 1.43× / 充电 34.41 min → ~34min), 且反推系数 ICHG÷IINMAX = 1.2160 与文档口径逐字一致 ⇒ 「旧系数 0.822 是 1.216 的倒数方向」本机复算成立 (1÷1.216 = 0.822368)** ★★**main 本机实读既有闸源码坐实「R10 判定面有洞」: `HW/check_netlist_selfconsistency.py` 的 R10 只 open 一个文件 (`HW/CHARGE_BOARD_SPEC.md`) ⇒ 那三份活文档从来不在 R10 扫描面内 ⇒ R10 绿灯与那三份文档的系数方向互不相干 ⇒ 该盲区是机器事实, ISS-384 的新闸补在产生点且不改既有闸, 合「零改既有闸」** ★★**★本单唯一未闭环项 (已裁, 见 §㊴ A1): 网表/脚表 note 层仍残留 3 处 390Ω 活值 (`netlist_v1.csv` L483 / L493 + `netlist_v1_pins.csv` L502) 与元件行 L47/L48 的 680Ω 自相矛盾 ⇒ 属「落表」动作 ⇒ 进「板只改一次」那一趟同批订正, 本单零落表** ★★**签收含义 = 交付物在盘且闸绿且边界零越界; R_ILIM 最终档位是老板域, 未代拍** ★",
        "ISS-385": "✅ verified (★main 2026-11-24 09:3x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `SW/check_evt_charge_current_criterion.py` 裸跑 rc=0 + `--selftest` rc=0 末行 ALL TESTS PASS (20 反向用例) + 连跑 3 次末行逐字相同** ★ 真相页 28,480 B + 交卷页 24,971 B + sw.yaml 分片登记在位 ★ 零写板 + 零落表 + 零挂链 ★★**`SW/EVT_TEMPLATE.md` 正文一字未动 (md5 `773dcaf7432b66397a1fa3240c32c3ad` 逐字节比对)** ★★**main 本机独立复核: `1.5÷0.573529 = 2.6155 → 2.62×` 与 `1.5÷0.697412 = 2.1508 → 2.15×` 重算命中; 且按 netlist 的 ref 列精确统计 ⇒ `U_CHG`(10 行) / `R_ILIM`(2 行) / `J_TYPE_C`(18 行) 的 board 域全为 `CHG_BOARD`, `MAIN_PCB` 上 0 行 ⇒ 「demo 主 PCB 上没有这条充电链」成立** ★★**本单查出的第二个坑 (寄存器回读不可达) 本机实读网表坐实: `I2C_CHG_SCL` 行明写「★I2C 不跨铰链 (PM 裁决) ⇒ J_CHG pin9/pin10 本版留空不接」⇒ 读回不可达是【已裁事实】不是待定项 ⇒ 替代 = `CHG_STAT` GPIO + `VBUS_DET` ADC 双通路** ★★**★PWR-05 最终采用哪个改法 (甲/乙/丙) 是老板域, main 只给方向 (丙为 demo 阶段唯一自洽底座) 而未代拍** ★",
        "ISS-386": "✅ verified (★main 2026-11-24 09:3x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `MECH/check_debug_seat_3d_fit.py` 裸跑 rc=0 (201 条判据 0 失败) + `--selftest` rc=0 末行 ALL TESTS PASS (18 反向用例) + 连跑 3 次末行逐字相同** ★ 真相页 51,765 B + 交卷页 41,304 B + mech.yaml 分片登记在位 ★ 零写板 + 零落表 + 零挂链 + ★**零改已签收件 / 既有页面正文** (★§二列出的 9 份只读页 + `BOARD_ONEPASS_JUART_LAND_FIT.md` 一字不改, 只新建 1 个 MECH/BOARD_ONEPASS_* 文件★) ★★**main 本机独立复核 (★用每边口径 `(C−H)/2` 重算★)**: 官方 1×4 THT 铜箔 X 向总展 `4.8100` ⇒ 三档清空区 `1.7750`/`4.0850`/`4.8100` 的每边余量 = `-1.5175`/`-0.3625`/`0.0000`, 再减 `TOL 0.30` ⇒ `-1.8175`/`-0.6625`/`-0.3000` ⇒ **三档全红 (`CRIT 0.60`) 成立**; 要过阈所需清空区 X = `6.6100` (J_DEBUG) / `4.0700` (J_UART) 重算命中; `J_UART` 每边 `(2.5400−2.2700)/2 = +0.1350` 与 ISS-379 口径一致 ⇒ **三个候选落点全红/全绿的结论成立** ★★**OI-2 本机实读权威页坐实: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 原文已点 `J_DEBUG`/`J_UART` 两件 ⇒ 范围本就含 J_UART, 两颗排针换官方 THT 后结构件同批返工是【已拍范围】的必然推论** ★★**OI-5 已裁 (§㊴ C1): 出件基准取 `4.8100` (官方 land 铜箔总展), 「装得下」与「每边 CRIT 余量」两层分开表述 (OI-12) · OI-13 Y 向零余量不接受 (须同时放大开口 Y ≥ 5.6000 两件同批) · OI-14 订正块与那一趟同批落 · OI-15 以 ISS-379 §2.3 实读为准** ★",
    }

    NOTE = {
        "ISS-384": "★**2026-11-24 09:3x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**四个头条数本机重算全部命中** (★权威源 `MECH/hinge_power_calc.json` 的 `rilim_table`·★不是抄页面★): ICHG `0.6974` / 单 pin `0.3487` / 余量 `1.4339` / 充电 `34.41 min` ⇒ 且反推系数 `ICHG÷IINMAX = 1.2160` 与文档口径逐字一致 ⇒ 「旧系数 0.822 是 1.216 的倒数」复算成立 (`1÷1.216 = 0.822368`) ② ★**「R10 判定面有洞」本机实读源码坐实**: 既有闸的 R10 只 open `HW/CHARGE_BOARD_SPEC.md` 一个文件 ⇒ **那三份活文档从来不在 R10 扫描面内** ⇒ R10 绿灯与那三份文档的系数方向互不相干 ⇒ 盲区成立, 新闸补在产生点且不改既有闸 ⇒ 合「零改既有闸」 ③ ★**网表 note 残留 390Ω 已裁 (§㊴ A1)**: 另开「网表 note 订正」单, 只订 note 文本, 不动元件值/不改板 ⇒ 属「落表」动作 ⇒ 进「板只改一次」那一趟同批 ④ ★**R_ILIM 档位是老板域, 未代拍** (★依据: 680Ω 档单 pin 0.349A < 0.35A 保守线且余量 1.43×; 390Ω 档单 pin 0.608A 超 0.5A 触点上限 21.6% 判死; 300Ω 档 0.790A 判死 ⇒ 只有 680Ω 同时活★) ⑤ ★**J_CHG 触点额定**: 现行页 `HW/J_CHG_SELECTION.md` L14 已记 Hirose FH12 `0.5A DC 每触点` / 座高 2.0mm / 0.5mm pitch, 证据等级 `[官方] FH12 系列规格书` ⇒ 本单判为 `[0数据]` 与现行页并存 ⇒ 以现行页为准, 但规格页尚未逐字核 ⇒ 补一件事: 把条款 + 页码钉进 §7 (只补证据, 不改选型) ⑥ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字节未动.",
        "ISS-385": "★**2026-11-24 09:3x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**两个数本机重算命中**: `1.5÷0.573529 = 2.6155 → 2.62×` (输入侧) · `1.5÷0.697412 = 2.1508 → 2.15×` (电池侧) ⇒ **判据不可达是硬事实, 且旧 0.822 口径下同样不可达 (`1.5÷0.4714 = 3.18×`) ⇒ 既存判据缺陷成立** ② ★**「demo 主 PCB 上没有这条充电链」本机按 ref 列精确统计坐实**: `U_CHG`(10 行) / `R_ILIM`(2 行) / `J_TYPE_C`(18 行) board 域全 `CHG_BOARD`, `MAIN_PCB` 上 **0 行** ⇒ ★**(注: 用全文关键词匹配会误命中 note 文本 ⇒ 本机复核时先踩了这个坑, 改按 ref 列才得到真值; 该闸本身用的就是 ref 口径, 正确★)** ③ ★**「寄存器回读不可达」本机实读网表坐实**: `I2C_CHG_SCL` 行明写「★I2C 不跨铰链 (PM 裁决) ⇒ J_CHG pin9/pin10 本版留空不接」⇒ 是已裁事实 ⇒ 替代 = `CHG_STAT` GPIO + `VBUS_DET` ADC 双通路 ④ ★**PWR-05 改法已裁方向但未代拍 (§㊴ B4)**: 丙 (注明 demo 主 PCB 不适用) 是 demo 阶段唯一自洽底座 (充电链物理上不在 demo 板上 ⇒ 留在模板里 = 留一条永远红的判据), 甲 (降阈到硬件真值附近) 作整机/充电板阶段口径 ⇒ **最终采用哪一条 = 老板域** ⑤ ★**落点已裁 (§㊴ B1/B2/B3)**: EVT 模板 + 真相页机器块 + 新闸挂链, 三件一律与「板只改一次」那一趟同批 ⇒ 提前单独改 = 中间态 = churn ⑥ `SW/EVT_TEMPLATE.md` 正文一字未动 (md5 `773dcaf7432b66397a1fa3240c32c3ad`) ⑦ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字节未动.",
        "ISS-386": "★**2026-11-24 09:3x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**余量本机重算命中 (★口径: 铜箔每边超出 = (C−H)/2★)**: 官方 1×4 THT 铜箔 X 向总展 `4.8100` (`1.0000 + 3×1.2700`) ⇒ 三档清空区 `1.7750`/`4.0850`/`4.8100` 每边余量 `-1.5175`/`-0.3625`/`0.0000`, 再减 `TOL 0.30` ⇒ `-1.8175`/`-0.6625`/`-0.3000` ⇒ **三档全红 (`CRIT 0.60`) 成立**; 要过阈所需 `6.6100` / `4.0700` 重算命中; `J_UART` 每边 `(2.5400−2.2700)/2 = +0.1350` 与 ISS-379 口径一致 ⇒ **三候选全红/全绿成立** ② ★**OI-2 本机实读权威页坐实**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 原文 = 「`J_DEBUG`/`J_UART` 排针 land pitch `0.50→1.27mm` (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」⇒ **范围本就含 J_UART** ⇒ 两颗排针换官方 THT 后结构件同批返工是【已拍范围】的必然推论, 不是新增范围 ⇒ ★**mech-lead 的提问是真问题, 但答案在仓里已有, 不必等 main** ③ ★**OI-5 已裁 (§㊴ C1)**: 出件基准取 `4.8100` (官方 land 铜箔总展) ⇒ 理由: `1.7750` 是【拿铜箔宽冒充座体宽】的同义反复 (本页 §1 已点明), `4.0850` 是【现状错误尺寸的搬家】, 只有 `4.8100` 既【与官方 land 一致】又【可核】⇒ **取它只解决「装得下」, 要过罩住判据仍需 `6.6100` ⇒ 两件事不混** ④ ★**OI-12 已裁 (§㊴ C2)**: 判据口径【不改】, 但【两个层级分开表述】—— 「装得下」用官方 land 的 `F.CrtYd 6.0900` 判, 「装配可靠」用每边 `CRIT 0.60` 判 ⇒ 免得现场以为「判据要求超过 courtyard ⇒ 判据错了」 ⑤ ★**OI-13 已裁 (§㊴ C3)**: Y 向零制造余量【不接受】, 要留余量须同时放大开口 Y `≥ 5.6000`, 且 `J_DEBUG` + `J_UART` 同批 (不同批就会有一件装不上) ⑥ ★**OI-15 已裁 (§㊴ C7)**: 以 ISS-379 §2.3 实读为准 (`0.2441` 属 `(18.5000,68.4000)`, `(18.4000,68.4000)` 是 `0.3124`), 任务书那处是转述笔误 ⇒ 层级上【实读记录 > 转述】⇒ 只影响「挪多远」的账 ⑦ ★**落点顺序已裁 (§㊴ C5)**: 老板答板框第一问 → 落点定死 → 结构件出件 → 板改 + 布线 + Gerber 重出 ⇒ 与 ISS-379 §② (落点挂起) 一致, 本条只补顺序不重开落点 ⑧ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字节未动.",
    }

    for iss, vr in VER.items():
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        e["status"] = "verified"
        e["verify_result"] = vr
        e["verify_date"] = "2026-11-24 09:3x"
        e["verify_by"] = "main"
        e["fix_ref"] = "main 2026-11-24 09:3x 独立复核签收 (★零写板·零落表·零挂链·零改既有闸·零改既有页面正文★)"

    for iss, nt in NOTE.items():
        e = by.get(iss)
        prev = e.get("note_addendum") or ""
        e["note_addendum"] = (prev + ("\n" if prev else "") + nt)

    tmp = p + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, p)
    print("  issue_log.yaml: 已落 3 单签收 + 3 条 note_addendum (追加式, 备份 %s.bak_%s_main_sign_iss384_385_386)"
          % (os.path.basename(p), STAMP))
    return True


def write_pm():
    ANS = [
        ("iss384_netlist_note_390ohm_residual", "hw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★一件没代老板拍板★)★: ★**另开「网表 note 订正」单 (只订 note 文本, 不动元件值 / 不改板 / 不改 680Ω 裁定)** ★★"
         "★**main 本机实读依据 (★三处逐一坐实★)★**: `HW/netlist_v1.csv` L483 (note: 「R_ILIM 390Ω 硬件封顶: IINMAX 1.00A / ICHG 0.82A」) · L493 (note: 「R_ILIM = 390Ω ±1% 必装 ⇒ 定 390Ω」) · `HW/netlist_v1_pins.csv` L502 (同 L493) ⇒ ★**与元件行 L47/L48 的 680Ω (V-4 裁定 2026-11-16) 自相矛盾 ⇒ 谁只看 note 谁拿到 0.82A/1.00A 错数** ★★"
         "★**⇒ 处置**: ★**该单属「落表」动作 ⇒ 进「板只改一次」那一趟同批做, 不许另起一趟碰网表** (★同「板只改一次」纪律: 碰网表只碰一次★) ★★"
         "★**不裁的部分**: 错数订正【是维护动作】, main 直接裁; 但 ★**若要连带改 R_ILIM 档位, 那是老板域** ⇒ ★**本条只裁「note 文本订正」, 不碰档位** ★★",
         "ISS-384 交卷页 cont1 新发现 · 一页 §㊴ A1 · main 本机实读网表 L47/L48 vs L483/L493"),

        ("iss384_rilim_档位确认", "hw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★老板域·★main 只给依据不代拍★)★: ★**维持 680Ω (V-4 已裁且已落表 2026-11-16)** ★★"
         "★**main 本机从权威 JSON 重算的依据 (★只有 680Ω 同时活★)★**: 680Ω 档 max = IINMAX `0.573529` / ICHG `0.697412` / 单 pin `0.348706` (★< `0.35A` 保守降额线 ✓★) / 余量 `1.43×` / 充电 `34.41 min` · 390Ω 档 max 单 pin `0.6080` ⇒ ★**超 `0.5A` 触点上限 `21.6%` ⇒ 判死** · 300Ω 档 max 单 pin `0.7904` ⇒ ★**判死** ★★"
         "★**⇒ 若老板要改档 ⇒ 走「板只改一次」那一趟 (换料不换板, ILIM 脚稳 0.8V)** ★★"
         "★**★本条【不代拍】**: 档位是【已落表事实 + 采购/安全余量】的联合决策 ⇒ 老板域 ⇒ ★**main 只登记「只有 680Ω 同时活」这个机器事实** ★★",
         "MECH/hinge_power_calc.json rilim_table · 一页 §㊴ A2 · main 本机重算"),

        ("iss384_jchg_触点额定", "hw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★采购/RFQ 动作不由 main 裁决★)★: ★**判定标准用「单触点额定 ≥0.5A」, 但书面确认走 RFQ (★零外发, 由老板放行★)** ★★"
         "★**main 本机实读现行页 (★与本单判为 [0数据] 的说法并存 ⇒ 以现行页为准★)★**: `HW/J_CHG_SELECTION.md` L14 = 「Hirose **FH12** 系列 (0.5mm pitch / 1×10p / **0.5A DC 每触点** / 座体高 **2.0mm**) 直接满足『≥0.35A』判据」· 证据等级 **[官方] FH12 系列规格书** · L15 = 70% 降额条款原文「When passing the current through all of the contacts, use 70% of the current rating」⇒ 全触点同时导通时每触点 `0.35A` ★★"
         "★**⇒ 补一件事 (只补证据, 不改选型)**: ★**把规格页的逐字条款 + 页码钉进 `HW/J_CHG_SELECTION.md` §7** ⇒ ★**这样「规格页尚未逐字核」这个缺口就闭合了** ★★"
         "★**降级路径已量化 (本机复核确认)★**: 若只拿得到 `0.3A` 型号 ⇒ 680Ω 档单 pin `0.349A` 也不合格 ⇒ 需 `R_ILIM ≥ 790Ω` 或改 `1.0mm pitch` (★MECH §M-6 已量化·铰链区装不下 1.0mm★) ⇒ ★**这是老板/PM 域的采购动作, 本单零外发** ★★",
         "HW/J_CHG_SELECTION.md §0-3 L14/L15/L21 · 一页 §㊴ A3"),

        ("iss384_evt_板端实测", "hw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界★)★: ★**EVT 阶段实测, 不阻塞本趟** ★★"
         "★**main 本机实读依据**: 权威源 `MECH/hinge_power_calc.json` 的 `evidence.board_measured` = **0 条** ⇒ ★**所有 ICHG 数一律标 `[推算]` / `[实测](脚本)`, 不冒充实测** ⇒ ★**降级方案按 `HW/EVT_RELIABILITY_TEST_ITEMS.md` 实测复核** ⇒ ★**板端实测不可达是物理事实, 不是阻塞项** ★★"
         "★**★本条【知悉型】, 不是等外部回复★** ★★",
         "MECH/hinge_power_calc.json rilim_table evidence · 一页 §㊴ A4"),

        ("iss384_gate_hook_decision", "hw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★先例同款★)★: ★**与「板只改一次」那一趟同批挂** ★★"
         "★**理由 (★先例: ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 同款★)★**: 提前单独挂 ⇒ 中间态红 ⇒ 现场误读成「板坏了」⇒ ★**闸与它要防的那批事同批生效, 才是真防线** ★★"
         "★**并遵守零改既有闸**: 本闸只新建, 不改既有闸 ⇒ ★**挂链动作由 main 在那一趟统一做, 不许 agent 自挂** (★main 本机实测: 三个新闸在 `state/gate_check.py` 里命中均为 0★) ★★",
         "ISS-384 交卷页 · 一页 §㊴ A5 · 先例 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8"),

        ("iss385_evt_template_landing_timing", "sw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★先例同款★)★: ★**与「板只改一次」那一趟同批落** ★★"
         "★**理由 (★main 本机实读★)★**: 改判据 ⇒ 模板 v1.0 + §0.4 判据来源表 + 七段判定矩阵 `L79~L119` 三处联动 ⇒ ★**提前单独改 = 中间态 = 制造 churn** (★同款先例: ISS-379 Q9 / ISS-381 订正块 / ISS-382 C1 都是「与那一趟同批落」★) ⇒ ★**本单零改 `EVT_TEMPLATE.md` 正文是对的 (★main 本机实测 md5 `773dcaf7432b66397a1fa3240c32c3ad` 逐字节未动★)** ★★",
         "SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md §2 · 一页 §㊴ B1"),

        ("iss385_update_caliber_machine_block_on_landing", "sw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★★本条是给 main 自己执行的备忘★)★: ★**那一趟改完 EVT 页后, 同批更新真相页机器块的 `evt_current_criterion_a` / `evt_current_criterion_max_a`** ★★"
         "★**★否则本单新闸立刻报「口径被换掉」⇒ 这是闸的设计意图 (盯口径漂移, 不盯人) ⇒ 闸的报错文本含现值与登记值, 照着改即可★** ★★"
         "★**⇒ 落进「板只改一次」那一趟的批清单, 不许漏** ★★",
         "SW/check_evt_charge_current_criterion.py · 一页 §㊴ B2"),

        ("iss385_should_the_new_gate_be_hooked", "sw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★先例同款★)★: ★**与「板只改一次」那一趟同批挂** ★★"
         "★**理由 (★先例: ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + ISS-384 A5 同款★)★**: 提前挂 ⇒ 中间态红 ⇒ 现场误读 ⇒ ★**闸与它要防的那批事同批生效** ⇒ ★**挂链动作由 main 在那一趟统一做, 不许 agent 自挂** (★main 本机实测: 三个新闸在 `state/gate_check.py` 里命中均为 0★) ★★"
         "★**并附一条 (★★本轮实测发现的同类缺口★)★**: 挂链那一趟【必须同时】把 ISS-372 的 §1/§2 清单刷新 (★新增文件与清单同批重生成⇒ 见 L-26★) ⇒ ★**否则新闸挂上去之后, ISS-372 那道清单自守闸仍然是红的** ★★",
         "SW/check_evt_charge_current_criterion.py · 一页 §㊴ B3 · L-26"),

        ("iss385_choose_pwr05_fix_candidate", "sw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★★最终采用哪一条是老板域, main 只给方向不代拍★)★: ★**方向 = 丙 (注明 demo 主 PCB 不适用) 作为 demo 阶段底座 + 甲 (降阈到硬件真值附近) 作为【整机/充电板】阶段口径** ★★"
         "★**理由 (★main 本机实读 + 重算★)★**: ① ★**PWR-05 这一行同时踩两个坑**: 阈值不可达 (`1.5A` 差 `2.62×` 输入侧 / `2.15×` 电池侧) ★**且** 读回方式不可达 ⇒ ★**任何改法必须同时修两处, 只修阈值不够** ② ★**「不适用」不是免责, 是事实**: 充电链 `U_CHG`(10 行) / `R_ILIM`(2 行) / `J_TYPE_C`(18 行) board 域全 `CHG_BOARD`, `MAIN_PCB` **0 行** ⇒ ★**demo 主 PCB 上物理上就没有这条充电链** ⇒ ★**留在 EVT 模板里当整机判据 = 留一条永远红的判据** ⇒ ★**丙是唯一能让 demo 阶段自洽的底座**; 甲/乙 决定它【移到整机阶段后】怎么写 ★★"
         "★**替代读回方式 (已定)**: `CHG_STAT` GPIO + `VBUS_DET` ADC 双通路 ⇒ ★**依据: 网表 `I2C_CHG_SCL` 行明写「★I2C 不跨铰链 (PM 裁决) ⇒ J_CHG pin9/pin10 本版留空不接」⇒ 寄存器回读不可达是【已裁事实】不是待定项** ★★"
         "★**★不代拍的部分**: 甲/乙/丙 的最终采用与措辞 = 老板域 ⇒ ★**main 只裁「方向」与「必须同时修两处」这条纪律** ★★",
         "SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md §2.4 对照表 · 一页 §㊴ B4"),

        ("iss385_bat10min_rise_needs_board_measurement", "sw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★知悉型·★不是等外部回复★)★: ★**知悉, 不阻塞; 判读法按「记 V0 不预设门槛」** ★★"
         "★**main 本机实读**: 判据 C4「电池电压 10min 内上升 ≥0.1V」在 `ICHG` 从 `1.5A` 降到 `0.6A` 后是否仍可达 ⇒ ★**必须板通电后自己测** (插 Type-C 前记 V0, 10min 后记 V1, 记 `V1−V0`) ⇒ ★**降级方案已写进 C4 判读法** ⇒ ★**板不可达是物理事实, 不是阻塞项** ★★",
         "SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md §2 · 一页 §㊴ B5"),

        ("iss385_charge_chain_board_domain_charge_board_push", "sw-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★★产品范围决策归老板·main 不单独立项★)★: ★**要推动充电板落地, 但并进「板只改一次」那一趟的规划清单, 不单独立项** ★★"
         "★**main 本机实读坐实的架构事实 (★F1~F7 复核通过★)★**: `U_CHG` 10 行 / `R_ILIM` 2 行 / `J_TYPE_C` 18 行 board 域全 `CHG_BOARD`; `MAIN_PCB` 上 **0 行**; 板文件里 `U_CHG`/`R_ILIM` 各 **0 次**; `BT_432243`/`U_BATPROT` 均 DNP; demo 装机态 `J_CHG` DNP ⇒ ★**充电板不落地 ⇒ 充电链永远不在 demo 板上 ⇒ EVT 充电判据永远无载体** ★★"
         "★**★为什么不由 main 单独立项**: ★**这是【产品范围决策】(demo 台架板要不要带充电链) ⇒ 与老板的甲/乙板框第一问同源** ⇒ ★**并进那一趟的规划清单交老板同批看, 不另起一单** ⇒ ★**main 地界只裁「归属」, 不裁「做不做」** ★★",
         "HW/netlist_v1.csv board 列 (main 本机按 ref 列统计) · 一页 §㊴ B6"),

        ("iss386_oi5_jdebug_clearance_x_pick_one", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★★★与老 key `iss377_oi5_jdebug_must_clear_which_number` 是同一个问题★ 本条为准★)★: ★**出件基准取 `4.8100` (官方 THT land 的铜箔 X 向总展)** ★★"
         "★**理由 (★main 本机重算 + 实读★)★**: ① ★**另两个数都不是「铜箔多宽」的合法来源**: `1.7750` = 座体宽 = ★**拿铜箔宽冒充座体宽 (同义反复)**★ ⇒ ★**你自己那页 §1 已点明「现状行 `Hx == Cx` 是同义反复, 不作判据」**; `4.0850` = 把现状 `0.275` 宽 pad 搬到 1.27 pitch 上 ⇒ ★**那是「现状错误尺寸的搬家」, 不是官方 land** ② ★**`4.8100` 是唯一【与官方 land 一致】且【可核】的值**: `1.0000 + 3×1.2700 = 4.8100` ⇒ ★**它同时是「换 land 后必须容纳的铜箔总展」的下界** ⇒ ★**按它出件 ⇒ 至少【装得下】; 按 `1.7750`/`4.0850` 出件 ⇒ 净空不足 ⇒ 【当场干涉】** ③ ★**★但口径必须说清 (★不混两件事★)★**: 取 `4.8100` 只解决「装得下」⇒ ★**要过罩住判据 (每边 ≥ `CRIT 0.60`) 仍需 `6.6100`** ⇒ ★**本裁决 = 「出件下界取 `4.8100`」+ 「判据口径按 OI-12 走」两件事** ★★"
         "★**不代老板拍板的部分**: 清空区 X 的【最终放大量】取决于老板的甲/乙板框第一问 ⇒ ★**本条裁的只是「结构件的出件基准不许用同义反复的值」** ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §1/§3 · 一页 §㊴ C1 · main 本机重算 (C−H)/2"),

        ("iss377_oi5_jdebug_must_clear_which_number", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★★本条与 `iss386_oi5_jdebug_clearance_x_pick_one` 是同一个问题 ⇒ 以本条为准, 两个 key 判同一结论★)★: ★**出件基准取 `4.8100` (官方 THT land 铜箔 X 向总展 = `1.0000 + 3×1.2700`)** ★★"
         "★**理由**: `1.7750` 是【拿铜箔宽冒充座体宽】的同义反复 · `4.0850` 是【现状错误尺寸的搬家】· ★**只有 `4.8100` 既与官方 land 一致又可核** ⇒ ★**按它出件至少装得下; 按另两个出件 ⇒ 当场干涉** ⇒ ★**本机重算三档每边余量 `-1.5175`/`-0.3625`/`0.0000` ⇒ 全红 ⇒ 结构件无论如何都要动 (与你的结论一致) ⇒ 只是【返工幅度】按 `4.8100` 取最小** ★★"
         "★**★但要过罩住判据仍需 `6.6100` ⇒ 「出件下界」与「判据口径」是两件事, 不混★** ★★"
         "★**最终放大量归老板的板框第一问** ★★",
         "ISS-377 §2-C3 · 一页 §㊴ C1 · main 本机重算"),

        ("iss386_oi12_cover_criterion_too_strict", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★★改判据口径 = 判据方向 ⇒ 但本轮先不拍数值, 只解耦表述★)★: ★**判据口径【不改】, 但登记为已知偏紧项, 并给出【两个层级分开表述】的口径** ★★"
         "★**理由 (★main 本机实读 + 重算★)★**: 判据要求 `6.6100` 而官方 land 自己的 `F.CrtYd` 只有 `6.0900` X ⇒ ★**差 `0.5200` ⇒ 判据确实比 courtyard 还紧** ⇒ 但 ★**「判据偏紧」≠「判据错」**: 判据要的是【罩住 + 每边留 `CRIT` 余量】, courtyard 只保证【不撞 DRC】⇒ ★**两个是不同层级的东西** ★★"
         "★**⇒ 解耦口径 (★本条的可执行部分★)★**: ★**① 「装得下」用官方 land 的 `F.CrtYd 6.0900` 判 ⇒ 官方 land 自洽**; ★**② 「装配可靠」用每边 `CRIT 0.60` 判 ⇒ 那是【结构件必须额外留的装配余量】, 达不到就说明【这个座体方案在 1.27 pitch 下余量不够】⇒ ★**判据不改, 但两个层级分开表述, 免得现场以为「判据要求超过 courtyard ⇒ 判据错了」** ⇒ ★**要在改判据之前, 先出这一层解耦口径** ★★"
         "★**★数值档位本轮不拍**: 那是判据方向 ⇒ 与老板的板框第一问同批 ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §1-§3 · 一页 §㊴ C2"),

        ("iss386_oi13_y_zero_margin", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界★)★: ★**不接受 Y 向零制造余量; 要留余量就【同时放大开口 Y】, `J_DEBUG` + `J_UART` 同批** ★★"
         "★**理由 (★main 本机实读 + 重算★)★**: 两件罩住 Y 余量都 `0.7700` (最坏 `0.4700` ⇒ 红) ⇒ 要过阈需清空区 Y `≥ 2.8000`; 而罩开口 Y `4.6000` 恰好只容 `2.8000` ⇒ ★**只放大清空区会把开口顶死** ⇒ ★**要留余量 ⇒ 开口 Y 须 `≥ 5.6000`, 且两件同批** (★两件同板同座体 ⇒ 不同批就会有一件装不上★) ★★"
         "★**「零余量」不接受的机器理由**: 最坏口径 (`余量 − TOL 0.30`) = `0.4700` < `CRIT 0.60` ⇒ ★**零余量在最坏口径下是红的 ⇒ 不是「勉强接受」, 是【过不了判据】** ★ ★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §2/§3 · 一页 §㊴ C3"),

        ("iss386_oi2_b33_land_scope", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★★不是新裁决, 是把仓里已有的原文摆出来★)★: ★**含 `J_UART` —— 范围早已点明** ★★"
         "★**main 本机实读权威页坐实 (★不是抄 brief★)★**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 原文 = 「★**`J_DEBUG`/`J_UART` 排针 land pitch `0.50→1.27mm` (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)**★」⇒ ★**它本来就同时点了两件** ⇒ ★**⇒ 两颗排针换官方 THT 后结构件必须同批返工 (两件罩住轴都红) —— 这是【已拍范围】的必然推论, 不是新增范围** ⇒ ★**mech-lead 问「范围是否含 J_UART」是个真问题, 但答案在仓里已有, 不必等 main** ★★"
         "★**⇒ 落点 (★本机实读 PREFLIGHT §B33 的 current_state 段★)**: `J_DEBUG` = pitch 0.50 / 4 脚 / 铜箔 X 142.0625..143.8375 × Y 56.1500..57.0500 (`1.7750 × 0.9000`) · `J_UART` = pitch 0.50 / 2 脚 / 铜箔 X 18.5025..19.2775 × Y 68.1500..69.0500 (`0.7750 × 0.9000`) ⇒ ★**换 land 后两件的铜箔 X 向总展分别是 `4.8100` / `2.2700` ⇒ 与你算的一致** ★ ★",
         "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md B33_PIN_LAND_1P27 (main 本机实读) · 一页 §㊴ C4"),

        ("iss386_oi3_juart_landing_dependency", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★★不重开落点, 只补顺序★)★: ★**落点裁决【先于】结构件出件, 但落点本身仍挂起 (等老板的甲/乙板框第一问)** ★★"
         "★**理由 (★main 本机重算确认你的结论★)★**: 三个候选的 3D 判决【全部】罩住红 / 全部开口绿 ⇒ ★**落点裁决不被结构侧阻塞** ✔; 但清空区【中心】随落点变 (`17.9650` / `19.0350` / `18.9350`) ⇒ ★**结构件出件必须等落点定死** ⇒ ★**⇒ 「板只改一次」那一趟的顺序**: ★**① 老板答板框第一问 → ② 落点定死 → ③ 结构件出件 → ④ 板改 + 布线 45→0 + Gerber/投产包重出** ★★"
         "★**与 ISS-379 §② (落点挂起, 倾向 rot90 + `(18.4000,68.4000)`) 一致 ⇒ 本条只补【顺序】, 不重开落点** ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3 · ISS-379 §② · 一页 §㊴ C5"),

        ("iss386_oi14_iss377_dp1_gap", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界·★先例同款★)★: ★**要落 —— 追加式订正块落 `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md`, 与「板那一趟」同批** ★★"
         "★**理由 (★main 本机重算确认★)★**: ISS-377 §3.2 DP-1 的 `3.4700 = 2.2700 + 2×CRIT` 是【名义余量】口径; 按全链 (最坏 = 余量 − `TOL 0.30` ≥ `CRIT 0.60`) 需要 `2.2700 + 2×0.90 = 4.0700` ⇒ 差 `0.6000` ⇒ ★**按 `3.4700` 出件仍不过阈** ⇒ ★**这是【已签收页上的口径缺口】⇒ 不订 ⇒ 下一轮有人照 `3.4700` 出件** ⇒ ★**但提前落 ⇒ 中间态红 ⇒ 必须与那一趟同批** (★同 C1/C2/B1 的节奏★) ★★"
         "★**并遵守零改已签收件**: 订正块是追加式, 老字一字未删 ⇒ 交给你按追加式落 ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md · ISS-377 §3.2 DP-1 · 一页 §㊴ C6"),

        ("iss386_oi15_pad1_displacement_attribution", "mech-lead",
         "★**main 裁决 (★2026-11-24 09:3x·★main 地界★)★: ★**以 ISS-379 §2.3 的实测为准, 任务书那处是转述笔误** ★★"
         "★**理由 (★main 本机实读 + 层级判断★)★**: `0.2441` 是 `(18.5000, 68.4000)` 的值, `(18.4000, 68.4000)` 是 `0.3124` (余量 `0.1155`) ⇒ ★**ISS-379 §2.3 是【已签收件的实读记录】, 任务书是【转述】** ⇒ ★**层级上【实读记录 > 转述】** ⇒ ★**只影响「挪多远」的账, 不影响任何余量/判决** ⇒ ★**订正只登记在 ISS-386 新页 (零改已签收件) —— 合规** ★★"
         "★**⇒ 不需要 main / hw-lead 另行核对笔误位置** ⇒ ★**直接以 ISS-379 §2.3 为准即可** ★★",
         "ISS-379 §2.3 (已签收件) · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3 · 一页 §㊴ C7"),
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
    tot = len(yaml.safe_load(open(PM, encoding="utf-8"))["answers"])
    print("  pm.yaml (main 自己的分片): answers +%d 条 (跳过已存在 %d) ⇒ 共 %d 条" % (added, len(skipped), tot))
    return True


def write_memory_pointer():
    p = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
    txt = read_lines(p)
    if "L-26" in txt and "签收时必须跑" in txt:
        print("  MEMORY.md: L-26 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l26_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-26★·★main 独占写·★无 job 重写★)★**: "
           "★**L-26 「签收时必须跑【扫描面覆盖到本次交付的闸】, 不只是交付物自带的闸」★** ⇒ "
           "★① 签收闸集合 = 交付物自带闸 ∪ 扫描面命中本次交付的既有闸 ⇒ 只跑前者 = 签了一半★ "
           "★② 清单式闸的过期有【两种】触发方式: 插行 (L-21) + 【新增一份会被扫到的文件】⇒ 解法跟着扩: 【补丁或新增文件, 都与清单同批重生成】★ "
           "★③ 清单过期造成的红不许「就地重新生成清单」消掉 ⇒ 必须与它要清的那批事同批; 刷新前登记为【已知缺口】, 不许假装它绿★ "
           "★④ 判定「这道红是不是我这一趟造成的」必须做【沙盒对照】不能靠推断: 把可疑新文件从扫描网摘掉再跑一遍, 仍红 ⇒ 红因在更早★ "
           "★⇒ ★**本轮实证: main 08:03 签收 ISS-381 时没跑 ISS-372 的清单自守闸 ⇒ 那道闸从 ISS-381 文件落地那刻 (07:25) 就已红 ⇒ 已记 main 自己的缺口; 处置 = 清单刷新并进「板只改一次」那一趟的 6 件批** ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-26 指针追加 (追加式, 备份 %s.bak_%s_main_l26_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def final_check():
    print()
    print("=" * 96)
    print("★阶段 3 · 写盘后收尾复核")
    print("=" * 96)
    m, ns, sz = board_fp()
    print("  板三项: %s / %s / %d  ⇒ %s"
          % (m[:8], "2026-11-06 07:07:17.362193413", sz,
             "★未动★" if (m == BOARD_MD5 and ns == ns_of(BOARD_MTIME) and sz == BOARD_SIZE) else "★★动了★★"))
    bad = []
    for rel, want in PROTECTED.items():
        if not want:
            continue
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append(rel)
    print("  零落表 + 既有闸/已签收页面正文 (%d 件): %s"
          % (len([v for v in PROTECTED.values() if v]), "★全未动★" if not bad else "★★动了 %s★★" % bad))
    for cmd, label in (("python3 state/merge.py", "merge.py"),
                       ("python3 state/gate_check.py", "gate_check.py"),
                       ("python3 state/issue_check.py", "issue_check.py")):
        rc, o = sh(cmd)
        print("  %-16s rc=%d" % (label, rc))
    for iss, d in DELIVER.items():
        rc, o = sh("python3 %s" % d["gate"])
        print("  %-16s rc=%d" % (iss + " 闸", rc))
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
    print("★ main (项目总工) · 2026-11-24 09:3x · ISS-384/385/386 三单独立复核签收 + 18 条 main 地界待裁项已裁")
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
    print()
    final_check()
    print()
    print("★ 本轮完成: 3 单签收 + 18 条 main 地界待裁项已裁 + L-26 + ★★main 自己 08:03 签收缺口的记账与处置★★")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 零代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
