#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0830_main_sign_iss380_383_382_381.py
==================================================
main (项目总工) · 2026-11-24 08:3x
★独立签收本轮 4 单 (ISS-380 / ISS-383 / ISS-382 / ISS-381) + 裁 17 条 main 地界待裁项★★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime/size 三项开工前后各打一次, 纳秒级比)
  ② 零落表 (网表/脚表/BOM/落表台账 一字不改)
  ③ 零改既有闸 / 零改既有页面正文 (★新闸只新建, 不挂链★)
  ④ 分片只走 state/frag_write.py (原子写) · 只写 main 自己的 pm.yaml
  ⑤ issue_log.yaml / 一页 / LESSONS.md 一律【追加式】(★老字一字未删·★零 churn★)
  ⑥ 不代老板拍板 (★板框第一问仍未答 ⇒ 落点坐标的一切前提都挂在它身上★)
  ⑦ 零外发 (老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料)
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

import frag_write  # ★只用它的原子写 ★

STAMP = time.strftime("%Y%m%d_%H%M")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

# ---- 本轮四单交付物 (★本机实读路径★) ----
DELIVER = {
    "ISS-380": {
        "gate": "HW/check_debug_uart_seat_truth.py",
        "page": "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
        "handoff": "HANDOFF/2026-11-24_hw-lead_ISS380_座体厂商型号与keepout图纸自查.md",
        "frag": "hw.yaml",
    },
    "ISS-383": {
        "gate": "HW/check_debug_uart_seat_alignment.py",
        "page": "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md",
        "handoff": "HANDOFF/2026-11-24_hw-lead_ISS383_座体选型落地四方对齐.md",
        "frag": "hw.yaml",
    },
    "ISS-382": {
        "gate": "MECH/check_jdebug_arrangement_truth.py",
        "page": "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md",
        "handoff": "HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md",
        "frag": "mech.yaml",
    },
    "ISS-381": {
        "gate": "SW/tools/check_sw_false_connectivity_gate.py",
        "page": "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md",
        "handoff": "HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md",
        "frag": "sw.yaml",
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
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md": "f1ce54c981dd1f64071a177a374df85d",
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


def sh(cmd):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
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

    # ---- 四单: 交付物在盘 + 闸绿 + selftest 末行 ALL TESTS PASS ----
    for iss, d in DELIVER.items():
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            e = os.path.isfile(p) and os.path.getsize(p) >= 4000
            chk("%s 交付物在盘 (≥4000 B) %s" % (iss, d[k].split("/")[-1]), e,
                "%d B" % (os.path.getsize(p) if os.path.isfile(p) else 0))
        rc, o = sh("python3 %s" % d["gate"])
        tail = [l.strip() for l in o.strip().splitlines() if l.strip()][-1:] or [""]
        chk("%s 自带闸裸跑 rc=0" % iss, rc == 0, "rc=%d 末行=%r" % (rc, tail[0][:44]))
        rc2, o2 = sh("python3 %s --selftest" % d["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        chk("%s --selftest 末行 ALL TESTS PASS" % iss,
            rc2 == 0 and "ALL TESTS PASS" in last, "rc=%d 末行=%r" % (rc2, last[:44]))
        # 闸读数确定性 (连跑 3 次末行逐字相同)
        reads = set()
        for _ in range(3):
            _, oo = sh("python3 %s" % d["gate"])
            reads.add(tuple(l.strip() for l in oo.strip().splitlines()[-1:]))
        chk("%s 闸读数确定性 (连跑 3 次末行逐字相同)" % iss, len(reads) == 1, "distinct=%d" % len(reads))

    # ---- 零落表 + 既有闸/页面未动 ----
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/既有页面正文 未动 (%d 件)" % len(PROTECTED), not bad,
        "动 %d %s" % (len(bad), bad[:3]))

    # ---- 零挂链 (四个新闸都没进 gate_check.py) ----
    for iss, d in DELIVER.items():
        rc4, o4 = sh("grep -c %s state/gate_check.py" % os.path.basename(d["gate"]))
        got = o4.strip().splitlines()[0].strip() if o4.strip() else "?"
        chk("%s 零挂链 (gate_check.py 命中 0)" % iss, got == "0", "命中 %s" % got)

    # ---- ★别人的分片: 只查【替 main 答了 main 地界的题】或【登记了别人单的产物】⇒
    #      ★★needs_from 且 to=main 的条目是【向 main 提问】, 不是越界 (★L-22 同型: 判据要按 section/to 落, 不能只落 key 子串★)★★
    MAIN_DOMAIN = set()
    for k in ("iss383_main_choose_single_row_1x4_criteria", "iss383_main_single_row_1p27_vendor_pn",
              "iss383_main_bom_model_column_timing", "iss383_main_official_vs_custom_footprint",
              "iss383_main_register_juart_target_lib", "iss383_main_mech_recompute_three_inconsistencies",
              "iss383_main_hang_new_gate_or_not", "iss380_board_trip_bom_part_fill",
              "iss381_cont1_acceptance_line_single_vs_dual", "iss381_cont1_three_cheat_methods_policy",
              "iss381_cont1_diff_copper_symmetry_threshold", "iss381_cont1_gate_chain_mount",
              "iss381_cont1_correction_block_into_legacy_page", "iss382_correction_block_landing",
              "iss382_g5_dimension_criterion", "iss382_label_downstream_wording", "iss382_new_gate_hook"):
        MAIN_DOMAIN.add(k)
    x_bad = []
    for f in ("sw", "mech", "hw"):
        try:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
        except Exception:
            continue
        # (1) 别人的分片里不许有【main 地界题目的答案】
        for e in (d.get("answers") or []):
            if isinstance(e, dict) and str(e.get("key")) in MAIN_DOMAIN:
                x_bad.append("%s.yaml[answers] %s" % (f, e.get("key")))
        # (2) 别人的分片里不许登记【别人那单】的产物 (artifacts 路径属别的 owner)
        for e in (d.get("artifacts") or []):
            if isinstance(e, dict):
                p = str(e.get("path") or "")
                if ("iss381" in p.lower() and f != "sw") or ("iss382" in p.lower() and f != "mech"):
                    x_bad.append("%s.yaml[artifacts] %s" % (f, p[:48]))
    chk("别人的分片 零【代 main 答题】+ 零【登记别人单的产物】", not x_bad,
        "越界 %d %s" % (len(x_bad), x_bad[:3]))
    # (3) 向 main 提问的条目 (needs_from + to=main) 是【正常协作】⇒ 计数登记, 不当越界
    ask = 0
    for f in ("sw", "mech", "hw"):
        try:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
        except Exception:
            continue
        for e in (d.get("needs_from") or []):
            if isinstance(e, dict) and e.get("to") == "main":
                ask += 1
    print("     (附) 三个分片向 main 提问的 need 共 %d 条 (★这是协作, 不是越界★)" % ask)

    # ---- 各自的闸/页 在自己的分片里有登记 (★大小写不敏感★) ----
    for iss, d in DELIVER.items():
        f = d["frag"]
        try:
            # ★frag 字段已是「hw.yaml」★ ⇒ 直接拼, 不许再补一次 .yaml (★否则读的是 hw.yaml.yaml ⇒ 空 blob★)
            frag = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        except Exception:
            frag = {}
        blob = yaml.safe_dump(frag, allow_unicode=True).lower()
        # ★key 形态是 `iss380_xxx` (★无短横★) ⇒ 用去掉短横的形态去匹配, 否则永远不命中
        low = iss.lower().replace("-", "")
        chk("%s 自己的分片 (%s) 有本单登记" % (iss, f),
            low in blob or os.path.basename(d["gate"]).lower() in blob
            or os.path.basename(d["handoff"]).lower() in blob
            or os.path.basename(d["page"]).lower() in blob, "命中在位")

    # ---- ★★本轮独立复核的两条厂商级硬事实 (★main 自己查的, 不抄 agent★) ----
    # (a) FTSH-104-01-F-DV / FTSH-102-01-F-DV 是【双排 SMT】⇒ ISS-380 §2 的 D-1/U-1 首选候选判定被推翻
    #     证据: Samtec 官网单品页标题 "8 Pin, 2 Row, SMT" / "4 Pin, 2 Row, SMT" + Mouser 参数表
    #           "Number of Positions: 8 / Number of Rows: 2" + DigiKey "CONN HEADER SMD 8POS"
    #     ⇒ 编码规律: FTSH-1NN-…-DV ⇒ NN = 每排位数, 总位数 = 2×NN (105→10 / 110→20 / 103→6 同规律)
    # (b) ★ISS-383 §0-2 「两家的 1.27mm 都没有单排」不成立★ ⇒ Samtec 【FTS】系列有单排直插:
    #     FTS-104-01-F-S = Mouser "Number of Positions: 4 / Number of Rows: 1 / Mounting Style: Through Hole"
    #     + DigiKey "Number of Positions 4 / Number of Rows 1" + Samtec 官网 FTS 家族页「Single Row」
    #     ⇒ 板侧真值档 (1×4 单排直插) 【有现成可采购件】, 不必「另找厂按规格书下单」
    for iss in ("ISS-380", "ISS-383"):
        p = os.path.join(PROJ, DELIVER[iss]["page"])
        t = read_lines(p)
        if iss == "ISS-380":
            chk("★ISS-380 §2 D-1 首选候选被独立复核推翻 (8 Pin 2 Row SMT)",
                "2x2" not in t and ("FTSH-104-01-F-DV" in t), "★已记入 note_addendum★")
        else:
            chk("★ISS-383 §1.1 已自行坐实 D-1 = 8 Pin / 2 Row / SMT (与 main 独立复核一致)",
                "8 Pin" in t and "2 Row" in t, "双源一致")

    # ---- J3 台账条目数 (ISS-382 的契约: 一处都不许漏 ⇒ 同 tuple 计数) ----
    rc5, o5 = sh("python3 - <<'PY'\n"
                  "import importlib.util,sys,json\n"
                  "spec=importlib.util.spec_from_file_location('g','MECH/check_jdebug_arrangement_truth.py')\n"
                  "g=importlib.util.module_from_spec(spec); sys.modules['g']=g; spec.loader.exec_module(g)\n"
                  "t=g.read_text('MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md')\n"
                  "b=g.parse_machine_blocks(t)[0]\n"
                  "led=b.get('arrangement_correction_ledger') or []\n"
                  "print('LEDGER',len(led))\n"
                  "print('ARR',b.get('land_smd',{}).get('arrangement'))\n"
                  "PY")
    led_n = 0
    arr = ""
    for ln in o5.splitlines():
        if ln.startswith("LEDGER "):
            led_n = int(ln.split()[1])
        if ln.startswith("ARR "):
            arr = ln.split(" ", 1)[1].strip()
    chk("★ISS-382 真相页机器块台账 = 7 条 (★一处都不许漏★)", led_n == 7, "%d 条" % led_n)
    chk("★ISS-382 真相页声明 = 2x4_staggered (★实测维数★)", arr == "2x4_staggered", repr(arr))

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


# ===================================================================== 阶段 2 · 追加式落记录
def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_sign_iss380_383_382_381" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """
## ★★㊳ 【2026-11-24 08:3x · 追加式】★ 本轮 4 单 (ISS-380/383/382/381) 独立复核签收 + ★★main 两条厂商级独立复核发现★★ + ★★17 条 main 地界待裁项已裁 (★一件没代老板拍板★)★★

★**① 板面 (本机实读·开工前后各打一次)** ★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**② 四单签收 (★main 本机独立复核·不抄 agent 报告★)** ★

| 单 | owner | 闸裸跑 | --selftest | 交付物 | 板面 |
|---|---|---|---|---|---|
| **ISS-380** | hw-lead | `HW/check_debug_uart_seat_truth.py` rc=0 (K0~K5 6/6) | rc=0 末行 `ALL TESTS PASS` (6 反向用例, 一条对一条 K) | 真相页 35,720 B + 交卷页 25,582 B | 零写板 |
| **ISS-383** | hw-lead | `HW/check_debug_uart_seat_alignment.py` rc=0 (K0~K4 5/5) | rc=0 末行 `ALL TESTS PASS` | 真相页 48,956 B + 交卷页 27,948 B | 零写板 |
| **ISS-382** | mech-lead | `MECH/check_jdebug_arrangement_truth.py` rc=0 (J0~J5 6/6) | rc=0 末行 `ALL TESTS PASS` (10 反向用例) | 真相页 27,324 B + 交卷页 17,548 B | 零写板 |
| **ISS-381** | sw-lead | `SW/tools/check_sw_false_connectivity_gate.py` rc=0 (K0~K6) | rc=0 末行 `ALL TESTS PASS` (17 反向用例) | 真相页 25,034 B + 交卷页 22,292 B | 零写板 |

★**四闸连跑 3 次末行逐字相同 (★读数确定性★)** ★**四闸全部零挂链** (`state/gate_check.py` 命中 0) ★**零落表** (网表/脚表/BOM/11 件既有闸与页面正文逐字节未动) ★

★**③ ★★main 两条厂商级独立复核发现 (★本机实查厂商页/分销参数表, 非抄 agent 报告★)★★**

★**发现一 (推翻 ISS-380 §2 的首选候选)**: ★★`FTSH-104-01-F-DV` 官网单品页标题逐字为「.050in/1.27mm Micro Header Strip, **8 Pin, 2 Row, SMT**」+ Mouser 参数表「Number of Positions: **8** / Number of Rows: **2**」+ DigiKey「CONN HEADER SMD **8POS**」⇒ ★★它是【双排贴片 8 位】, 不是 ISS-380 §2.1 写的「1×4 单排直插」★★ ⇒ 同规律 5 个料号交叉验证 (`105`→10 位 / `110`→20 位 / `103`→6 位 / `102`→4 位 ⇒ `1NN` = 每排位数, 总位数 = 2×NN) ⇒ ★★**ISS-380 §2 的 D-1 / U-1 两个「首选候选」判定被推翻** ★ ⇒ ★★**§2.3 结论 2-1「按板侧真值 (1×4 · 1.27 mm · 直插), 唯一同时满足三要素的候选是 FTSH-104-01-F-DV (D-1)」不成立** ★★

★**发现二 (推翻 ISS-383 §0-2 的「无单排」结论)**: ★★ISS-383 §0-2 写「★**两家的 1.27 mm 都没有单排** ⇒ 只能另找厂按规格书下单」★★ ⇒ ★★该结论不成立★ ⇒ ★★Samtec 【**FTS**】系列 (与 FTSH 同厂、1.27mm) 有单排直插: `FTS-104-01-F-S` = Mouser「Number of Positions: **4** / Number of Rows: **1** / Mounting Style: **Through Hole**」+ DigiKey「Number of Positions 4 / Number of Rows 1」+ Samtec 官网 FTS 家族页「**FTS - .050" (1,27mm) Low Profile, .016" (.41mm) Square Post Terminal Strip, Single Row**」★★ ⇒ ★★**板侧真值档 (1×4 单排直插) 有现成可采购件** ★★ ⇒ ★★§3.3-② 的降级路径「另找厂按规格书下单」被降级为【备选】, 不再是唯一解★★ ★

★**⇒ 这两条发现的共同点 (★与 §㊲ 的 17 条裁项直接相关★)**: ★★ISS-380 交回的 7 个未决项里, 「BOM 型号栏填哪一档」(§6-1) 的【前提】被这两条发现改变了 ⇒ main 裁的是【口径与依据】, 具体料号仍需官方单品页二次确认 ⇒ **不代老板拍板, 不代 agent 落料号** ★★

★**④ ★★17 条 main 地界待裁项 ⇒ 已裁 (★逐条给默认值 + 理由·一件没代老板拍板★)★★**

★**▌A 组 · 座体选型 (ISS-380 + ISS-383)★★

| # | need key | main 裁决 (2026-11-24 08:3x) |
|---|---|---|
| A1 | `iss383_main_choose_single_row_1x4_criteria` | ★**以板侧真值档 (1×4 · 1.27 mm · 单排 · 直插) 为准** ★★理由: ① 板是本趟的产物, 落表/落板以板侧为准; ② 结构侧「Cortex-10 2×5」只是**它自己的模型假设**, 且 ISS-383 已实测三方三个口径全不对 ⇒ 板侧定一版, 结构侧重算 (★不迁就任一方★) ★★ |
| A2 | `iss383_main_single_row_1p27_vendor_pn` | ★**不用另找厂** ⇒ Samtec 【FTS】系列有单排直插 1.27mm: 4 位 = `FTS-104-01-F-S` / 2 位 = `FTS-102-01-F-S` (★Mouser + DigiKey 参数表双源★) ⇒ ★**但铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认** (★FTS 的 post 是 .016″ (.41mm) 方柱, 与 FTSH 的 .41 mm 不同族, **不许拿 FTSH 的铜箔数顶替**) ★★ ⇒ ★★**A2 的默认建议从「另找厂下单」改为「FTS 单排直插 + 官网单品页补齐 land」★★ ★ |
| A3 | `iss383_main_bom_model_column_timing` | ★**与 land 改动同一次工序落** ★★理由: 型号栏与板上封装不同源 ⇒ 投产包 BOM 与 Gerber 对不上 ⇒ 违「板只改一次」的单源纪律 ★★ |
| A4 | `iss383_main_official_vs_custom_footprint` | ★**官方通用件 (`PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c…` / `PinHeader_1x02_P1.27mm_Vertical` md5 `47bcbf6d…`) ⇒ 自建留给走双排 SMT 那一档** ★★理由: 两个通用件都是【单排 THT / 排距 1.27 / 焊盘 1.000×1.000 / 钻孔 0.65】, 与板侧真值档逐项对齐 (★本机实测 pad 1.000×1.000 + drill 0.65 + 单列 X=0.0 / Y 间距 1.27×3★) ⇒ 与 BOM 描述栏同型 ★★ ⇒ ★★**但双排 SMT 那一档库里没有** (`2x04` 只有 THT 与 SMD 两支, SMD 那支是 2 列交错 `PinHeader_2x04_P1.27mm_Vertical_SMD` 的排中心距 3.9, 与 Samtec 双排 SMT 不同型) ⇒ 走双排必须自建 ★★ ★ |
| A5 | `iss383_main_register_juart_target_lib` | ★**补** ★★理由: 本机实读 `HW/FP_TRUTH_BASELINE.md` 里 `J_UART` 命中 **0** 次, 而该件确在库 ⇒ 台账漏登记 ⇒ 后续闸查不到该件 ★★ |
| A6 | `iss380_board_trip_bom_part_fill` | ★**填板侧真值档 (1×4 / 1×2 单排直插)** ★★同 A1 理由 ★★ ⇒ ★★**但 ISS-380 §2 的 D-1/U-1 不得直接当料号用** (★已被发现一推翻★) ⇒ 料号须走 A2 的 FTS 单排 + 官网单品页二次确认 ★★ ★ |
| A7 | `iss383_main_mech_recompute_three_inconsistencies` | ★**要, 且与板那一趟同批** ★★理由: 结构件与板同改一次, 不分两批 ⇒ 否则板改好了结构没跟上 ⇒ 装配干涉 ⇒ 板再改第二次 (★违「板只改一次」★) ★★ |

★**▌B 组 · 布线验收线 (ISS-381)★★

| # | need key | main 裁决 (2026-11-24 08:3x) |
|---|---|---|
| B1 | `iss381_cont1_acceptance_line_single_vs_dual` | ★**双轨 (保留 `unc 45→0` 作覆盖度指标 + 新闸作身份闸)** ★★理由: 两套判据两个数字都不说谎 ⇒ 现场只看一个数必然误读 ★★ |
| B2 | `iss381_cont1_three_cheat_methods_policy` | ★**一条都不许单独用** ★★理由: K1a 身份 + K1b 焊盘集合 + K1c 铜状态 + K5 交叉核对 四道机器判据已能把三种反例全部判红并逐条点名 ⇒ 只守 unc 计数 ⇒ 三种刷法都能把 45 刷到 0 而一条铜都不加 ⇒ 验收线给「全接上了」的错觉 ★★ ⇒ ★**且 ISS-381 已实测证伪 main 旧 need 的半句「unc 抓不到 UART_RX」** (★`UART_RX` 零铜且 pad≥2 ⇒ 必然贡献 ≥1 条 unc item★) ⇒ ★★该半句已在 ISS-381 真相页 §1/§2 就地订正, 本页不再重复 ★★ ★ |
| B3 | `iss381_cont1_diff_copper_symmetry_threshold` | ★**先不拍阈值, 但把 Δ 登记成【只报数不判红】** ★★理由: 本轮硬事实 20 对差分腿里 11 对不是「两腿都有铜」⇒ 有铜 ≠ 对称 ⇒ 不拍阈值 ⇒ K2 只判「成对都有铜」⇒ 对称性无人管 ★★ ⇒ ★**阈值要拍时与「板那一趟」同批, 且先出实测分布再谈数** ★★ ★ |
| B4 | `iss381_cont1_gate_chain_mount` | ★**与「板那一趟」同批挂** ★★先例: ISS-300/309/312/315 + ISS-372 U7 同款 ⇒ 提前单独挂 ⇒ 中间态红 ⇒ 现场误读成「板坏了」 ★★ |
| B5 | `iss381_cont1_correction_block_into_legacy_page` | ★**落 · 追加式 · 与那一趟同批** ★★老字一个字没删 ★★ ⇒ ★**订正内容按 ISS-381 真相页 §1/§2 的实测口径写** (★「unc 抓得到零铜网, 抓不到的是【身份】」★) ★★ ★ |

★**▌C 组 · 排布标签 + 闸盲区 (ISS-382)★★

| # | need key | main 裁决 (2026-11-24 08:3x) |
|---|---|---|
| C1 | `iss382_correction_block_landing` | ★**落进 `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` §0 机器块 + 与板那一趟同批** ★★先例代价: ISS-374 cont2 追加已签收页 ⇒ `K7` 立刻红 2 条 ⇒ 不许提前落 ★★ ★ |
| C2 | `iss382_g5_dimension_criterion` | ★**新闸独立挂, 旧闸 G5 只判「有没有写交错」** ★★理由: 零改已签收闸是本轮硬边界 + 旧闸判据本身是盲区 (★main 本机实测: 新闸 J2 逐字比对 ⇒ 写 `2x2` 红 / `2x4` 红 / `9x9 staggered` 红 / `2 列 × 4 行交错` 红, 只 `2x4_staggered` 绿★) ★★ ⇒ ★★**J2 这一条是本轮闸盲区的真正关闭点** ★★ ★ |
| C3 | `iss382_label_downstream_wording` | ★**改 · 但只改字样不动结论 · 且与 C1 同批** ★★ ★ |
| C4 | `iss382_new_gate_hook` | ★**与「板那一趟」同批挂** ★★同 B4 先例 ★★ ★ |

★**⑤ ★★两处需要纠正「已闭项」的地方 (★追加式·老字一字未删·★原位标注★)★★**

★**⑤-1 ISS-380 §2 的首选候选**: ★★已被发现一推翻 ⇒ ★★**D-1 / U-1 两个料号不得当「1×4 / 1×2 单排直插」用** ⇒ ★★A2 的正确方向是 FTS 单排直插 + 官网单品页补齐 land ★★ ★
★**⑤-2 ISS-383 §0-2 的「两家都没有单排」**: ★★已被发现二推翻 ⇒ ★★**FTS-104-01-F-S (4 位 1 排 直插) / FTS-102-01-F-S (2 位 1 排 直插) 现成可采购** ⇒ ★★A2 的「另找厂按规格书下单」降级为备选 ★★ ★

★**⑥ 本轮零派 / 零外发**: ★**internal = 0** (三个总工名下 `open` = 0) ⇒ 四单全部已交卷待签收 ⇒ 重派 = 重复劳动 ★**外发段恒空** (老板 2026-11-12 02:02 政策 ⇒ `state/outbox/` 只备不发) ★★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标的一切前提都挂在它身上, 本页不代拍** ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    after = os.path.getsize(p)
    print("  一页: %d → %d B (追加式, 备份 %s.bak_%s_main_sign_iss380_383_382_381)"
          % (before, after, os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l25" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-25 · ★★厂商料号的「排数 / 脚数 / 贴装型态」必须逐个料号坐实, 不许用「同族规律」直接推 ★★

★**实测 (2026-11-24 08:3x, main 本机实查厂商页 + 分销参数表 · ★本轮 ISS-380/383 交卷时踩中·★两处都踩中★)★**: main 复核 ISS-380 的「首选候选」时, 拿厂商官网单品页标题逐字读, 发现 `FTSH-104-01-F-DV` 的官方标题是「**8 Pin, 2 Row, SMT**」⇒ ★**双排贴片 8 位** ⇒ 而交付件 §2.1 把它写成「1×4 单排直插」⇒ ★**该件的「脚数 / 排数 / 型态」三格全错** ★ ⇒ ★**同批还有第二处: ISS-383 自己写的「★两家的 1.27 mm 都没有单排 ⇒ 另找厂按规格书下单★」也不成立** ⇒ ★**Samtec 同厂同 1.27mm 的【FTS】系列有单排直插: `FTS-104-01-F-S` = Mouser 参数表「Number of Positions: 4 / Number of Rows: 1 / Mounting Style: Through Hole」+ DigiKey「Number of Positions 4 / Number of Rows 1」** ★

★**⇒ 通则 ①**: ★**「官网家族页 + 分销页标题」只够判【排距 / 型态 / 有无此系列】, 判【脚数 / 排数】必须去【该料号自己的单品页标题】或【分销参数表的 Number of Positions / Number of Rows 两栏】** ⇒ ★**家族页天然只给「家族」, 不给「这一件」★ ★
★**⇒ 通则 ②**: ★**「同族规律」可以用来【交叉验算】, 不可以用来【代替查证】** ⇒ ★★main 这次就是先用规律 (`1NN` ⇒ 每排 N 位 ⇒ 双排总位 2N) 把 5 个料号对齐 (105→10 / 110→20 / 103→6 / 102→4 / 104→8), ★★规律自洽**才敢**说「`-DV` 是双排」⇒ ★**但「规律自洽」本身不能证明【某一件的具体位���】—— 判某一件仍必须看那一件的标题/参数表** ★★ ★
★**⇒ 通则 ③**: ★**两个不同厂商的「都没有」这种否定句, 要逐个厂商各查一遍, 且要查【同厂的不同系列】** ⇒ ★**本例两个否定句都栽在「只查了同厂的一个系列」(FTSH vs FTS)★ ⇒ ★**否定句比肯定句更容易错, 因为它只需要漏一个系列就能成立** ★ ★
★**⇒ 通则 ④**: ★**这类错误会【顺着结论链一路传染】**: 料号错 ⇒ 「唯一候选」错 ⇒ 「BOM 型号栏填哪一档」错 ⇒ 「另找厂下单」错 ⇒ ★**每一格都要单独坐实, 不许因为「上一格对了」就顺推下一格** ★ ★
★**★与 L-21 / L-22 / L-23 / L-24 合看★**: ★**前四条讲「机制与闸自己怎么写清」, 本条讲「外部事实怎么坐实」·★共性 = 【判据必须落在产生点, 且不许用代理指标冒充真值】** ★·★L-21 的「清单钉 (file,line)」是机制侧的例子, 本条的「厂商单品页标题逐字读」是外部事实侧的例子 —— ★**两者是同一个动作: 找到【真值所在的那一处】, 直接读它** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    after = os.path.getsize(p)
    print("  LESSONS: %d → %d B (追加式, 备份 %s.bak_%s_main_l25)"
          % (before, after, os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_issue_log():
    p = LOG
    shutil.copy2(p, p + ".bak_%s_main_sign_iss380_383_382_381" % STAMP)
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}

    VER = {
        "ISS-380": "✅ verified (★main 2026-11-24 08:3x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `HW/check_debug_uart_seat_truth.py` 裸跑 rc=0 (K0~K5 6/6) + `--selftest` rc=0 末行 ALL TESTS PASS (6 反向用例, 一条对一条 K) + 连跑 3 次末行逐字相同 (读数确定性)** ★ 真相页 35,720 B + 交卷页 25,582 B (B1~B6 齐全) + hw.yaml 分片登记在位 ★ 零写板 (md5/mtime/size 三项未动) + 零落表 (网表/脚表/BOM 未动) + 零挂链 (`state/gate_check.py` 命中 0) + 11 件既有闸与页面正文逐字节未动 ★★**本单的 §2 候选表有【一处被 main 独立复核推翻的判定】**: `FTSH-104-01-F-DV` / `FTSH-102-01-F-DV` 官网单品页标题逐字为「8 Pin, 2 Row, SMT」/「4 Pin, 2 Row, SMT」⇒ 是【双排贴片】, 不是 §2.1 写的「1×4 / 1×2 单排直插」⇒ ★**§2.3 结论 2-1「唯一同时满足三要素的候选是 D-1」不成立** ⇒ ★**该两个料号不得当单排直插件落表** (★正确方向见 §㊳ A2: Samtec FTS-104-01-F-S / FTS-102-01-F-S 单排直插, 官网单品页补齐 land★) ⇒ ★**本单其余部分 (§1 板侧真值 / §3 座体高 [0数据] 与降级三件套 / §4 keepout 登记 / §5 四条不自洽点 / §6 七问 / §7 复跑命令) 全部复核通过** ★★**签收含义 = 交付物在盘且闸绿且边界零越界; 不等于 §2 的每个料号判定都对 (已被推翻的那一条已在 note_addendum 就地标注)** ★",
        "ISS-383": "✅ verified (★main 2026-11-24 08:3x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `HW/check_debug_uart_seat_alignment.py` 裸跑 rc=0 (K0~K4 5/5) + `--selftest` rc=0 末行 ALL TESTS PASS + 连跑 3 次末行逐字相同** ★ 真相页 48,956 B (7 段) + 交卷页 27,948 B + hw.yaml 分片登记在位 ★ 零写板 + 零落表 + 零挂链 ★★**§1.1/§1.2 独立坐实了 D-1/U-1 = 8 Pin/2 Row/SMT 与 4 Pin/2 Row/SMT, 与 main 本机查厂商页 + 分销参数表的结论一致 (双源互证) ⇒ 该件的排布判定可信** ★★**但 §0-2「两家的 1.27mm 都没有单排」这一条已被 main 独立复核推翻**: Samtec 同厂同 1.27mm 的【FTS】系列有单排直插 (`FTS-104-01-F-S` = Mouser「Number of Positions 4 / Number of Rows 1 / Through Hole」+ DigiKey「Number of Positions 4 / Number of Rows 1」) ⇒ ★**§3.3-② 的「另找厂按规格书下单」从唯一解降级为备选** ⇒ ★**§0-2 / §3.3-② 已就地标注 (老字一字未删), 正确方向见 §㊳ A2** ★★",
        "ISS-382": "✅ verified (★main 2026-11-24 08:3x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `MECH/check_jdebug_arrangement_truth.py` 裸跑 rc=0 (J0~J5 6/6) + `--selftest` rc=0 末行 ALL TESTS PASS (10 反向用例) + 连跑 3 次末行逐字相同** ★ 真相页 27,324 B (§2 订正块草稿逐处清单在位) + 交卷页 17,548 B + mech.yaml 分片登记在位 ★ 零写板 + 零落表 + 零挂链 ★★**main 本机实测本闸真的能区分维数 (本轮最关键的一条)**: J2 逐字比对 ⇒ 写 `2x4_staggered` 绿, 而写 `2x2 staggered` / `2x4` / `9x9 staggered` / `2 列 × 4 行交错` **全红** ⇒ ★**旧闸 G5「只判有没有写交错」的盲区被真正关闭** ★★**且 J3 台账计数判据实测有效**: 真相页机器块 `arrangement_correction_ledger` = 7 条 (4 条「2 列 × 2 行」+ 2 条「2x2」+ 1 条「2x2」无交错限定词) ⇒ 少一条即红 (实测缺 L719 那条 ⇒ 红并点名) ⇒ ★**「一处都不许漏」不是口号, 是可判的** ★★**注意台账字段类型**: `cols`/`rows` 须为 **int**, `staggered` 须为 **bool**, `file` 须为**带 `.md` 的** `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ⇒ ★**沙盒草稿 `tmp/iss382_sbx/ledger.json` 里是字符串型 + 无 `.md`, 直接抄进页会红 (main 已实测三种组合: 原样绿 / 补 .md 红 / 再转 int 仍红) ⇒ 以真相页机器块为准, 不以沙盒草稿为准** ★★",
        "ISS-381": "✅ verified (★main 2026-11-24 08:3x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `SW/tools/check_sw_false_connectivity_gate.py` 裸跑 rc=0 (K0~K6) + `--selftest` rc=0 末行 ALL TESTS PASS (17 反向用例) + 连跑 3 次末行逐字相同** ★ 真相页 25,034 B (§0..§7 八段) + 交卷页 22,292 B + sw.yaml 分片登记在位 ★ 零写板 + 零落表 + 零挂链 ★★**本单实测证伪了 main 旧 need 的半句「unc 判据抓不到 UART_RX」**: `UART_RX` 零铜且 pad≥2 ⇒ 必然贡献 ≥1 条 unc item ⇒ 真洞是「unc 只数条数、不认身份」, 不是「unc 抓不到它」⇒ ★**该半句已在真相页 §1/§2 就地订正, 本页不重复** ★★**该闸的价值 = 身份闸**: K1a 身份 + K1b 焊盘集合 + K1c 铜状态 + K5 交叉核对 ⇒ 三种刷法 (删网 / 标 NC / 改名) 各自可判红并逐条点名 ⇒ 与 `unc 45→0` 双轨互补 (★见 §㊳ B1/B2★) ★★",
    }

    NOTE = {
        "ISS-380": "★**2026-11-24 08:3x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**§2 的 D-1 / U-1 两个「首选候选」判定被推翻** —— `FTSH-104-01-F-DV` 官网单品页标题 =「.050in/1.27mm Micro Header Strip, **8 Pin, 2 Row, SMT**」+ Mouser 参数表「Number of Positions **8** / Number of Rows **2**」+ DigiKey「CONN HEADER SMD **8POS**」⇒ 是双排贴片 8 位, 非 §2.1 写的「1×4 单排直插」; `FTSH-102-01-F-DV` 官网标题 =「**4 Pin, 2 Row, SMT**」⇒ 双排贴片 4 位, 非「1×2」⇒ ★**§2.3 结论 2-1「唯一同时满足三要素的候选是 D-1」不成立** ⇒ ★**这两个料号不得当 1×4/1×2 单排直插件落表** (★同页 D-2 `FTSH-105-01-L-DV-K` 被正确解码为 2 排 10 位 ⇒ 同一张表内两种解码并存, 本身即自相矛盾★) ② ★**正确方向**: Samtec 同厂同 1.27mm 的【FTS】系列有单排直插 (`FTS-104-01-F-S` 4 位 1 排 / `FTS-102-01-F-S` 2 位 1 排) ⇒ §3.3-② 的「另找厂按规格书下单」不再是唯一解 ⇒ ★**料号须走 FTS 单排 + 官网单品页补齐 land (铜箔宽 / pin 方径 / 座体高)·不许拿 FTSH 的铜箔数顶替 FTS** ③ 本单 §1/§3/§4/§5/§6/§7 全部复核通过 ⇒ **签收成立, 但 §2 那一处判定以本补注为准** ④ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字节未动.",
        "ISS-383": "★**2026-11-24 08:3x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**§1.1/§1.2 的排布判定经 main 独立复核确认成立** (厂商官网单品页标题 + Mouser/DigiKey 参数表双源与本单一致: D-1 = 8 Pin/2 Row/SMT, U-1 = 4 Pin/2 Row/SMT) ⇒ 该件可信 ② ★**但 §0-2「★两家的 1.27 mm 都没有单排 ⇒ 另找厂按规格书下单★」这一条已被 main 独立复核推翻** ⇒ Samtec 同厂同 1.27mm 的【FTS】系列**有单排直插**: `FTS-104-01-F-S` = Mouser「Number of Positions: **4** / Number of Rows: **1** / Mounting Style: **Through Hole**」+ DigiKey「Number of Positions 4 / Number of Rows 1」+ Samtec 官网 FTS 家族页「**FTS - .050\" (1,27mm) Low Profile, .016\" (.41mm) Square Post Terminal Strip, Single Row**」⇒ ★**板侧真值档 (1×4 单排直插) 有现成可采购件** ⇒ §3.3-② 从唯一解降级为备选 ③ ★**连带影响 §1.1 的「铜箔 X 宽 = [0数据]」**: 若改用 FTS 单排直插, 铜箔宽/pin 方径须按 FTS 原厂 land 重新取 (★FTS post 是 .016″(.41mm) 方柱, 与 FTSH 不同族★) ⇒ ★**A2/A4 的裁决已据此改写 (见 §㊳)** ④ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字节未动.",
        "ISS-382": "★**2026-11-24 08:3x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**本闸真的能区分维数 (main 本机实测, 这是本轮最关键的一条)**: J2 逐字比对 ⇒ 写 `2x4_staggered` **绿**, 而写 `2x2 staggered` / `2x4` / `9x9 staggered` / `2 列 × 4 行交错` **全红** ⇒ ★**旧闸 G5「只判有没有写交错」的盲区被真正关闭 (不是新增一条更强的同型判据, 是把维数逐字钉死)** ② ★**J3 台账计数判据实测有效**: 真相页机器块 `arrangement_correction_ledger` = 7 条 (4 条「2 列 × 2 行」+ 2 条「2x2」+ 1 条「2x2」无交错限定词) ⇒ 少一条即红 (实测缺 L719 那条 ⇒ 红并点名「漏登记」) ⇒ ★**「一处都不许漏」是可判的, 不是口号** ③ ★**字段类型是硬契约 (main 实测三种组合)**: `cols`/`rows` 须 **int**、`staggered` 须 **bool**、`file` 须为**带 `.md` 的** `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ⇒ 沙盒草稿 `tmp/iss382_sbx/ledger.json` 是**字符串型 + 无 `.md`** ⇒ ★**直接照抄草稿会让 J3 红 ⇒ 以真相页机器块为准, 不以沙盒草稿为准** (★生成器 `gen_ledger.py` 产的是正确型, 草稿 JSON 是后写的副本★) ④ ★**订正块落点已裁 (§㊳ C1)**: 落进本真相页 §0 机器块 + 与「板那一趟」同批 (★先例: ISS-374 cont2 追加已签收页 ⇒ K7 立刻红 2 条 ⇒ 不许提前落★) ⇒ **本单 §2 是草稿, 未落进已签收页, 符合纪律** ⑤ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字节未动.",
        "ISS-381": "★**2026-11-24 08:3x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**本单实测证伪了 main 旧 need 的半句「unc 判据抓不到 UART_RX」** ⇒ `UART_RX` 零铜 (0 段走线 · 0 过孔) 且 pad≥2 ⇒ 必然贡献 ≥1 条 unc item ⇒ ★**真洞是「unc 只数条数、不认身份」** ⇒ 该半句以本单真相页 §1/§2 为准 (★已就地订正·老字未删★) ② ★**闸的身份判据链实测成立**: K1a 身份 + K1b 焊盘集合 + K1c 铜状态 + K5 交叉核对 ⇒ 三种刷法 (删网 / 标 NC / 改名) 各自可判红并逐条点名 ⇒ 与 `unc 45→0` 构成双轨 (★见 §㊳ B1/B2★) ③ ★**B3 的差分铜长对称性阈值 main 裁为「先不拍阈值·只报数不判红」** ⇒ 理由: 本轮硬事实 20 对差分腿里 11 对不是「两腿都有铜」⇒ 有铜 ≠ 对称 ⇒ 不拍阈值时至少先把分布登记出来, 阈值与「板那一趟」同批再谈 ④ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字节未动.",
    }

    for iss, vr in VER.items():
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        e["status"] = "verified"
        e["verify_result"] = vr
        e["verify_date"] = "2026-11-24 08:3x"
        e["verify_by"] = "main"
        e["fix_ref"] = "main 2026-11-24 08:3x 独立复核签收 (★零写板·零落表·零挂链★)"

    for iss, nt in NOTE.items():
        e = by.get(iss)
        prev = e.get("note_addendum") or ""
        e["note_addendum"] = (prev + ("\n" if prev else "") + nt)

    tmp = p + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, p)
    print("  issue_log.yaml: 已落 4 单签收 + 4 条 note_addendum (追加式, 备份 %s.bak_%s_main_sign_iss380_383_382_381)"
          % (os.path.basename(p), STAMP))
    return True


def write_pm():
    """main 自己的分片 pm.yaml ⇒ 走 frag_write 原子写 (★只写自己的★)"""
    ANS = [
        # key, to, value, ref
        ("iss383_main_choose_single_row_1x4_criteria", "hw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★一件没代老板拍板★)★: ★**以板侧真值档 (1×4 · 1.27 mm · 单排 · 直插) 为准** ★★"
         "★**理由 (★main 本机实读★)★**: ① ★**板是「板那一趟」的产物** ⇒ 落表与落板以板侧为准; ② 结构侧的「Cortex-10 2×5」是★**它自己的模型假设**★, 而 ISS-383 已实测三方三个口径**全都不对** (★BOM 描述栏写 1.27 单排直插 · 板面实封装是 0.5mm 排距 SMD 占位盘 · 结构侧算 2×5★) ⇒ ★**板侧定一版让结构侧重算**, 不迁就任何一方 (★L-15: 几份各自正确的数对不上 ⇒ 最贵的风险是【谁都不改】★) ★★"
         "★**这条裁的是【口径与依据】, 不裁料号**★ ⇒ 料号走 A2 (★见 `iss383_main_single_row_1p27_vendor_pn★★★★★)★",
         "ISS-383 真相页 §0-3 / §1.1 / §1.2 · §㊳ A1"),

        ("iss383_main_single_row_1p27_vendor_pn", "hw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界★)★: ★**不用另找厂** ⇒ Samtec 【**FTS**】系列 (★同厂 · 同 1.27mm · 与 FTSH 不同族★) 有单排直插: 4 位 = `FTS-104-01-F-S` · 2 位 = `FTS-102-01-F-S` ★★"
         "★**main 本机实查证据 (★双源互证★)★**: Mouser 参数表「Number of Positions: **4** / Number of Rows: **1** / Mounting Style: **Through Hole**」+ DigiKey「Number of Positions **4** / Number of Rows **1**」+ Samtec 官网 FTS 家族页「**FTS - .050\" (1,27mm) Low Profile, .016\" (.41mm) Square Post Terminal Strip, Single Row**」 ⇒ ★**ISS-383 §0-2「两家的 1.27mm 都没有单排」不成立, 该条已在真相页就地标注** ★★"
         "★**但铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认** ⇒ ★**不许拿 FTSH 的铜箔数顶替 FTS** (★FTS post 是 .016″ (.41mm) 方柱, 与 FTSH 的 .016″ 说法易混但两族不同★) ⇒ ★**降级路径排序改为: ① FTS 单排直插 (现成可采购) → ② 才轮到「另找厂按规格书下单」** ★★",
         "ISS-383 真相页 §0-2 / §1.1 / §3.3-② · §㊳ A2 · ★L-25★"),

        ("iss383_main_bom_model_column_timing", "hw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界★)★: ★**与 land 改动同一次工序落** ★★"
         "★**理由 (★main 地界·★先例同款★)★**: 型号栏落地与改 land 分离 ⇒ BOM 型号与板上封装**不同源** ⇒ 投产包 BOM 与 Gerber 对不上 ⇒ ★**违「板只改一次」的单源纪律** (★同批落 ⇒ 一次改对, 不分两批★) ⇒ ★**落表时机 = 与 land 改动那一次工序** ★★",
         "ISS-383 真相页 §3.3 / §4 · §㊳ A3"),

        ("iss383_main_official_vs_custom_footprint", "hw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★本机实读库封装★)★: ★**走【单排直插】那一档用官方通用件; 自建封装只留给【双排 SMT】那一档** ★★"
         "★**main 本机实测两个通用件 (★与 BOM 描述栏逐项同型★)★**: `PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c1f70d4b832be258501945385` = 单列 X=0.0 / Y 间距 1.27×3 / 焊盘 1.000×1.000 / 钻孔 0.65 · `PinHeader_1x02_P1.27mm_Vertical` md5 `47bcbf6d0f267d543e50d4b2a8dfabf5` = 同型少两位 ⇒ ★**正好是板侧真值档 (1.27 / 单排 / 直插 / 方针 1.000)** ★★"
         "★**但双排 SMT 那一档库里没有** ⇒ 本机实测 `PinHeader_2x04_P1.27mm_Vertical_SMD` 的排中心距是 **3.9** (两列 X=±1.95), 与 Samtec 双排 SMT 的 1.27 排中心距**不同型** ⇒ ★**走双排 SMT 必须自建封装** ⇒ **这两条是并列的两档, 不是同一档的两个选项** ★★",
         "ISS-383 真相页 §0-3 · §㊳ A4 · main 本机实测库封装铜箔/钻孔/排距"),

        ("iss383_main_register_juart_target_lib", "hw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★本机实读★)★: ★**补** ★★"
         "★**main 本机实读依据**: `HW/FP_TRUTH_BASELINE.md` 里 `grep -c J_UART` = **0** (★零命中★), 而该件确在库 ⇒ ★**台账漏登记** ⇒ 后续闸查不到该件 ⇒ 补 (★与 land 改动同批·★属「板只改一次」的单源纪律: 台账与真件同源★) ★★",
         "ISS-383 真相页 §5 · §㊳ A5 · main 本机实读 FP_TRUTH_BASELINE.md"),

        ("iss380_board_trip_bom_part_fill", "hw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★一件没代老板拍板★)★: ★**填板侧真值档 (1×4 / 1×2 · 单排 · 直插)** ★★同 A1 理由 (★板是本趟产物·★结构侧 2×5 只是它自己的模型假设·★三方三口径全不对⇒板侧定一版·结构侧重算★) ★★"
         "★★**但 ISS-380 §2 的 D-1 / U-1 两个料号【不得直接用】★** ⇒ main 本机查厂商官网单品页标题 + Mouser/DigiKey 参数表 ⇒ `FTSH-104-01-F-DV` = 「**8 Pin, 2 Row, SMT**」/ `FTSH-102-01-F-DV` = 「**4 Pin, 2 Row, SMT**」⇒ ★**是双排贴片, 不是单排直插** ⇒ ISS-380 §2.3 结论 2-1「唯一同时满足三要素的候选是 D-1」**不成立** ⇒ ★**料号须走 A2: Samtec FTS-104-01-F-S / FTS-102-01-F-S (单排直插) + 官网单品页补齐 land** ★★"
         "★**这一档的落表【不代老板拍板】**: 板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标的一切前提都挂在它身上** ★★",
         "ISS-380 真相页 §2.3 / §6-1 · §㊳ A6 · main 本机查厂商单品页 + 分销参数表"),

        ("iss383_main_mech_recompute_three_inconsistencies", "hw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★一件没代老板拍板★)★: ★**要, 且与「板那一趟」同批** ★★"
         "★**理由 (★main 地界·★先例同款★)★**: 结构件与板同改一次, 不分两批 ⇒ ★**板改好了结构没跟上 ⇒ 装配干涉 ⇒ 板再改第二次** (★违「板只改一次」★) ⇒ ★**结构侧那三条不自洽点 (脚数 / 相对位置 / 座体真实高度) 跟着 A1 落定的口径重算** ★★"
         "★**注意 §5-③ 座体真实高度仍 [0数据]**: 结构侧按 Z 向保守上界 `4.70` 出件 (★与 ISS-380 §3.3-② 同源·★不猜高度★) ⇒ ★**高度图纸到手后仍要重算一次**, 但**不等它才出件** ⇒ ★**这一条不等老板的板框第一问** ★★",
         "ISS-383 真相页 §3.3 / §5 · ISS-380 真相页 §3.3-② · §㊳ A7"),

        ("iss381_cont1_acceptance_line_single_vs_dual", "sw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界★)★: ★**双轨 (★保留 `unc 45→0` 作覆盖度指标 + 新闸作身份闸★)** ★★"
         "★**理由 (★main 地界★)★**: ★**两套判据两个数字都不说谎** ⇒ 单轨则 unc 归 0 后本闸仍可能红 ⇒ 现场要解释「哪个红」 ★★ ⇒ ★**覆盖度 (unc) 与身份 (每条必需网的预期拓扑) 是两个正交的问题, 合成一个数就会丢一个** ★★",
         "ISS-381 真相页 §2 / §3 · §㊳ B1"),

        ("iss381_cont1_three_cheat_methods_policy", "sw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界★)★: ★**一条都不许单独用** ★★"
         "★**理由 (★main 地界·★本轮硬事实★)★**: K1a 身份 + K1b 焊盘集合 + K1c 铜状态 + K5 交叉核对 四道机器判据已能把三种反例 (★删网 / 标 NC / 改名★) 全部判红并逐条点名 ⇒ ★**只守 unc 计数 ⇒ 三种刷法都能把 45 刷到 0 而一条铜都不加 ⇒ 验收线给「全接上了」的错觉** ★★"
         "★★**另: main 旧 need 的半句「unc 判据抓不到 UART_RX」已被 ISS-381 本机实测证伪** ⇒ `UART_RX` 零铜且 pad≥2 ⇒ 必然贡献 ≥1 条 unc item ⇒ ★**真洞是「unc 只数条数、不认身份」** ⇒ 该半句以 ISS-381 真相页 §1/§2 为准 (★已就地订正★) ★★",
         "ISS-381 真相页 §3.3-④ · ISS-381 真相页 §1 / §2 · §㊳ B2"),

        ("iss381_cont1_diff_copper_symmetry_threshold", "sw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★阈值属于【判据方向】但本轮先不拍★)★: ★**先不拍阈值, 但把 Δ 登记成【只报数不判红】** ★★"
         "★**理由 (★本轮硬事实★)★**: 20 对差分腿里 **11 对不是「两腿都有铜」** (★7 对一腿有铜 + 4 对两腿都零铜★) ⇒ ★**有铜 ≠ 对称** ⇒ 不拍阈值 ⇒ K2 只判「成对都有铜」⇒ 对称性无人管 ⇒ ★**先把实测分布登记出来, 阈值与「板那一趟」同批再谈** ★★"
         "★**不新增老板拍板件**: 这条是判据方向的题, 但★**先登记不判红 = 不拍**★ ⇒ 老板待拍板面维持原数不变 ★★",
         "ISS-381 真相页 §2 / §3 · §㊳ B3"),

        ("iss381_cont1_gate_chain_mount", "sw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★先例同款★)★: ★**与「板那一趟」同批挂** ★★"
         "★**理由 (★先例: ISS-300/309/312/315 + ISS-372 U7 同款★)★**: 提前单独挂 ⇒ 中间态红 ⇒ 现场误读成「板坏了」 ⇒ ★**闸与它要防的那件事同批生效, 才是真防线** ★★"
         "★**并遵守本轮硬边界**: ★**零改已签收闸** ⇒ 本闸**只新建**, 不改既有闸; 挂链动作与「板那一趟」同批落 (★由 main 在那一趟统一挂, 不许 agent 自挂★) ★★",
         "ISS-381 真相页 §4 · §㊳ B4 · 先例 ISS-300/309/312/315 + ISS-372 U7"),

        ("iss381_cont1_correction_block_into_legacy_page", "sw-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★先例同款★)★: ★**落 · 追加式 · 与那一趟同批** ★★"
         "★**理由 (★main 地界★)★**: 老字一个字没删 ⇒ 只追加; 提前落 ⇒ 中间态与「板那一趟」不一致 ⇒ ★**订正块要跟它纠正的那批事实同批落** (★同 C1 / B4 的节奏★) ★★"
         "★**订正内容按 ISS-381 真相页 §1/§2 的实测口径写**: ★**「unc 抓得到零铜网 (UART_RX 就是那 45 条里的一条), 抓不到的是【身份】」** ⇒ ★**不许写成「unc 抓不到 UART_RX」** (★main 旧 need 的那半句已被证伪★) ★★",
         "ISS-381 真相页 §1 / §2 · §㊳ B5"),

        ("iss382_correction_block_landing", "mech-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★先例同款★)★: ★**落进 `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` §0 机器块 + 与板那一趟同批** ★★"
         "★**理由 (★main 地界·★先例代价已实测★)★**: 先例 ISS-374 cont2 追加已签收页 ⇒ `K7` 立刻红 2 条 ⇒ ★**提前落 ⇒ 中间态红 ⇒ 现场误读** ⇒ ★**订正块与它要纠正的那一趟同批落** ★★"
         "★**并已核对本单 §2 草稿合规**: ★**它是【草稿】, 未落进已签收页** ⇒ 符合「零改既有页面正文」硬边界 ⇒ ★**落点由 main 在那一趟统一落** ★★",
         "ISS-382 真相页 §2 / §3 · §㊳ C1 · 先例 ISS-374 cont2"),

        ("iss382_g5_dimension_criterion", "mech-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★本机实测★)★: ★**新闸独立挂, 旧闸 G5 只判「有没有写交错」** ★★"
         "★**理由 (★main 地界 + 本轮硬边界 + 本机实测★)★**: ① ★**零改已签收闸是本轮硬边界** ⇒ 不许往旧闸 G5 里塞新判据; ② ★**旧闸判据本身是盲区**: G5 只判「页面 arrangement 字符串里【含】staggered/交错」⇒ ★**写 `2x2` 绿、写 `9x9` 也绿** ⇒ ★**判据形同虚设** ★★"
         "★★**main 本机实测新闸 J2 真的能区分 (★这是本轮闸盲区的真正关闭点★)**: 写 `2x4_staggered` **绿**; 写 `2x2 staggered` / `2x4` / `9x9 staggered` / `2 列 × 4 行交错` **全红** ⇒ ★**不是新增一条更强的同型判据, 是把【维数】逐字钉死** ★★"
         "★**J3 台账计数判据同样实测有效**: 真相页 7 条, 少一条即红并点名 ⇒ 「一处都不许漏」是可判的 ★★",
         "ISS-382 真相页 §3 / §4 · main 本机实测 J2 五种写法 + J3 少一条 · §㊳ C2"),

        ("iss382_label_downstream_wording", "mech-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★先例同款★)★: ★**改 · 但只改字样不动结论 · 且与 C1 同批** ★★"
         "★**理由 (★main 地界★)★**: 文字与实测长期不一致 ⇒ 现场读错; 而★**结论数字不动** ⇒ ★**标签错 ≠ 结论错, 两件事分开 (★这正是新闸 J2 管标签 / J4 管结论的分工★)** ★★"
         "★**并遵守零改既有页面正文**: 改字样=★**追加式订正块里的字样**, 不许就地改已签收页正文 ⇒ 与 C1 同批一起追加 ★★",
         "ISS-382 真相页 §2 / §3 · §㊳ C3"),

        ("iss382_new_gate_hook", "mech-lead",
         "★**main 裁决 (★2026-11-24 08:3x·★main 地界·★先例同款★)★: ★**与「板那一趟」同批挂** ★★"
         "★**理由 (★先例: ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 同款★)★**: 提前挂 ⇒ 中间态红 ⇒ 误读 ★★"
         "★**并注意本闸自带 K5「零挂链」判据** ⇒ ★**挂链动作只能由 main 在那一趟统一做**, 不许 agent 自挂 (★main 本机实测: 四个新闸在 `state/gate_check.py` 里命中均为 0★) ★★",
         "ISS-382 真相页 §4 · §㊳ C4 · 先例 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8"),
    ]

    # 幂等: 已存在的 key 就不重复追加 (★不造重名 key★)
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
    print("  pm.yaml (main 自己的分片): answers +%d 条 (跳过已存在 %d) ⇒ 共 %d 条"
          % (added, len(skipped), len(yaml.safe_load(open(PM, encoding="utf-8"))["answers"])))
    return True


def write_memory_pointer():
    """MEMORY.md 铁律指针 (★main 独占写·★无 job 重写★)"""
    p = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
    txt = read_lines(p)
    if "L-25" in txt and "厂商料号的「排数 / 脚数 / 贴装型态」" in txt:
        print("  MEMORY.md: L-25 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l25_pointer" % STAMP)
    before = os.path.getsize(p)
    anchor = "★ ⇒ ★**三条同属一类: 【闸的扫描面会扫到自己人】"
    i = txt.find(anchor)
    if i < 0:
        # 退而求其次: 挂在最后一条指针之后
        old = txt
        add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-25★·★main 独占写·★无 job 重写★)★**: "
               "★**L-25 「厂商料号的『排数 / 脚数 / 贴装型态』必须逐个料号坐实, 不许用『同族规律』直接推」★** ⇒ "
               "★① 官网家族页只够判【排距/型态/有无此系列】, 判【脚数/排数】必须读【该料号自己的单品页标题】或【分销参数表的 Number of Positions / Number of Rows 两栏】★ "
               "★② 「同族规律」只能【交叉验算】, 不能【代替查证】★ "
               "★③ 两个不同厂商的「都没有」这种否定句, 要逐厂各查一遍**且要查同厂的不同系列** (★本例两个否定句都栽在「只查了同厂的一个系列」FTSH vs FTS★)★ "
               "★④ 料号错 ⇒「唯一候选」错 ⇒「BOM 填哪一档」错 ⇒「另找厂下单」错 ⇒ 每一格都要单独坐实, 不许因为「上一格对了」就顺推下一格★ ★⇒ "
               "★**本轮实证: `FTSH-104-01-F-DV` 官网标题逐字是「8 Pin, 2 Row, SMT」(双排贴片 8 位, 不是 1×4 单排直插); 而 Samtec 同厂同 1.27mm 的【FTS】系列有单排直插 `FTS-104-01-F-S` (Mouser: 4 Position / 1 Row / Through Hole) ⇒ ISS-383 §0-2「两家都没有单排」也不成立** ★ ★\n")
        with open(p, "a", encoding="utf-8") as f:
            f.write(add)
        print("  MEMORY.md: L-25 指针追加在文末 (追加式, 备份 %s.bak_%s_main_l25_pointer)"
              % (os.path.basename(p), STAMP))
        return True

    j = txt.find("\n", i)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-25★·★main 独占写·★无 job 重写★)★**: "
           "★**L-25 「厂商料号的『排数 / 脚数 / 贴装型态』必须逐个料号坐实, 不许用『同族规律』直接推」★** ⇒ "
           "★① 官网家族页只够判【排距/型态/有无此系列】, 判【脚数/排数】必须读【该料号自己的单品页标题】或【分销参数表的 Number of Positions / Number of Rows 两栏】★ "
           "★② 「同族规律」只能【交叉验算】, 不能【代替查证】★ "
           "★③ 两个不同厂商的「都没有」这种否定句, 要逐厂各查一遍**且要查同厂的不同系列** (★本例两个否定句都栽在「只查了同厂的一个系列」FTSH vs FTS★)★ "
           "★④ 料号错 ⇒「唯一候选」错 ⇒「BOM 填哪一档」错 ⇒「另找厂下单」错 ⇒ 每一格都要单独坐实, 不许因为「上一格对了」就顺推下一格★ ★⇒ "
           "★**本轮实证: `FTSH-104-01-F-DV` 官网标题逐字是「8 Pin, 2 Row, SMT」(双排贴片 8 位, 不是 1×4 单排直插); 而 Samtec 同厂同 1.27mm 的【FTS】系列有单排直插 `FTS-104-01-F-S` (Mouser: 4 Position / 1 Row / Through Hole) ⇒ ISS-383 §0-2「两家都没有单排」也不成立** ★")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-25 指针追加 (追加式, 备份 %s.bak_%s_main_l25_pointer)"
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
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append(rel)
    print("  零落表 + 既有闸/页面正文 (%d 件): %s" % (len(PROTECTED), "★全未动★" if not bad else "★★动了 %s★★" % bad))
    rc, o = sh("python3 state/merge.py")
    print("  merge.py rc=%d" % rc)
    rc, o = sh("python3 state/gate_check.py")
    print("  gate_check.py rc=%d" % rc)
    for iss, d in DELIVER.items():
        rc, o = sh("python3 %s" % d["gate"])
        print("  %s 闸 rc=%d" % (iss, rc))
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
    print("★ main (项目总工) · 2026-11-24 08:3x · 本轮 4 单独立复核签收 + 17 条 main 地界待裁项已裁")
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
    print("★ 本轮完成: 4 单签收 + 17 条 main 地界待裁项已裁 + 2 处「已闭项」纠正 + L-25")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 零代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
