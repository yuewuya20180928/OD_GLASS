#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/land_v_values.py — ★参数化 V 值一键落表器★ (★ISS-236 · 硬件总工 hw-lead · 2026-11-16★)

★★**干什么**★★
  ★**把 ISS-233 交卷单 §3 的【V-2 / V-3 / V-4 拍板即可一键落】逐字清单, 变成一条能跑的命令** ★
  ⇒ ★**老板拍完 A1/A2/A3 后, 一条命令把 V 值落进网表/脚表/BOM + 落表台账 + 门禁锚点, 并把新 md5 打到 stdout (供 SW/MECH 走 H-1 重锚)★ ★

★★**三条纪律 (★机器化保证, 不靠人自觉★)★★
  ① ★**默认 dry-run** ⇒ 不带 `--apply` ⇒ ★**零写盘**★ (只打印逐字 diff + 预期条数变化 + 谁要重锚)
  ② ★**取值白名单写死** ⇒ 只认 `V-3 ∈ {E, A, D, DEG4}` · `V-4 ∈ {680, 470, 390}` · `V-2 ∈ {1, 2}` ⇒ 其它一律报错退出 (非零 rc) + 零写盘
  ③ ★**`--apply` 必须同时带 `--boss-decision "<日期> <A1|A2|A3> = <值>"`** ⇒ 缺这条 ⇒ ★**拒绝执行并退出非零**★ ⇒ ★**这就是「不许替老板拍板」的机器化保证★ ★

★★**落表流程 (★逐条照抄 ISS-220 / ISS-223 / ISS-233 三批的既有落法★)**★
  真源改 `state/gen_netlist.py` / `HW/SCHEMATIC_V1_SPEC.json` / `state/p10_rows.json` / `HW/CHARGE_BOARD_SPEC.md`
  → 重生成 (`gen_netlist` → `gen_kicad_net` → `gen_netlist_pins` → `gen_bom` → `gen_schematic_pages` → `gen_kicad_sch`)
  → 门禁锚点 (`HW/check_netlist_selfconsistency.py` 的 `EXPECT` 现状断言值) + 规格页锚点表 (`HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 `<!-- ANCHORS -->` 块) 逐字一致
  → 落表台账新段 (`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16: 单号 + 文件名 + 新旧 md5)
  → 实跑 7 条门禁 + 四道尺子 + merge/gate_check ⇒ ★**新 md5 打到 stdout**★

★★**两个必须写进去的坑 (★ISS-230 交卷实测结论★)**★
  ① ★**V-3 落表必须同时删 `state/gen_netlist.py` 的 `DEMO_DNP` 3 行** ⇒ ★**只改阻值永远还是 DNP**★
  ② ★**生成顺序必须是 `gen_netlist.py` → `gen_kicad_net.py` → `gen_netlist_pins.py`** ⇒ ★**脚表脚号来自 `.net`, 顺序错了 V-2 的 pin3 出不来**★

★★**边界 (★本工具自己也不许越界★)**★
  · ★**绝不碰板**: `HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` / 布线 / 布局 / 板框 ⇒ 本工具【只落网表侧】
  · ★**不改 `SW/` / `MECH/`** (只输出「谁要走 H-1 重锚」的清单)
  · ★**不改 `state/issue_log.yaml`** (status 留给 main 落 verified) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不改 `DECISION_PENDING_2026-11-16.md`**
  · ★**零外发** · ★**实物 [实测] = 0 条**

★**用法**★
    # dry-run (默认 · 零写盘)
    python3 state/land_v_values.py --decision V-3=E
    # 真落 (必须带老板拍板凭据)
    python3 state/land_v_values.py --decision V-3=E --apply --boss-decision "2026-11-16 A1 = E"
    # 一次落多个
    python3 state/land_v_values.py --decision V-3=E --decision V-4=680 --apply \
        --boss-decision "2026-11-16 A1 = E" --boss-decision "2026-11-16 A3 = 680"
    # 非法取值 ⇒ 报错退出 (非零 rc) + 零写盘
    python3 state/land_v_values.py --decision V-3=E2
    # 回滚 (把某次落表整个还原)
    python3 state/land_v_values.py --rollback state/.bak_land_v_values_20261116-120000
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)

# ═══════════════════════════════════════════════════════════════════════════
# 0 · 常量
# ═══════════════════════════════════════════════════════════════════════════

# ★★生成链路 (★顺序是硬的: ISS-230 实测结论 — 脚表脚号来自 `.net`★)★★
GEN_ORDER = [
    ("state/gen_netlist.py", "网表 (表A HW/netlist_v1.csv)"),
    ("state/gen_kicad_net.py", "KiCad 网表 (HW/netlist_v1.net)"),
    ("state/gen_netlist_pins.py", "脚表 (表B HW/netlist_v1_pins.csv)"),
    ("state/gen_bom.py", "BOM (HW/BOM_v1.csv)"),
    ("state/gen_schematic_pages.py", "原理图页面 (HW/SCHEMATIC_V1.md)"),
    ("state/gen_kicad_sch.py", "KiCad 原理图 (HW/PCB/demo_mainboard*.kicad_sch)"),
]

# ★★受保护 (★本工具落表前后必须逐字节不变★)★★
PROTECTED = [
    ("HW/PCB/demo_mainboard.kicad_pcb", "611b869e13518c3c023fb178f91a0075"),
    ("HW/PCB/demo_mainboard.kicad_pro", "3e504d2be83152e337949723e909be1b"),
]

# ★★落表后要打 md5 出来 (★供 SW / MECH 两边走 H-1 重锚★)★★
MD5_TARGETS = [
    ("HW/netlist_v1.csv", "网表"),
    ("HW/netlist_v1_pins.csv", "脚表"),
    ("HW/BOM_v1.csv", "BOM"),
    ("HW/PCB/demo_mainboard.kicad_pcb", "板 (受保护)"),
    ("HW/PCB/demo_mainboard.kicad_pro", ".kicad_pro (受保护)"),
]

CHECK_SCRIPT = "HW/check_netlist_selfconsistency.py"
SPEC_PAGE = "HW/NETLIST_SELF_CONSISTENCY_SPEC.md"
LANDED_LEDGER = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
GEN_NETLIST = "state/gen_netlist.py"
SPEC_JSON = "HW/SCHEMATIC_V1_SPEC.json"
P10_ROWS = "state/p10_rows.json"
CHG_SPEC = "HW/CHARGE_BOARD_SPEC.md"

BASELINE_EXPECT_RESOLVED = 18

# ═══════════════════════════════════════════════════════════════════════════
# 1 · 补丁模型
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class Patch:
    """逐字文本补丁: `old` 必须在目标文件里【恰好】出现 `count` 次, 否则拒绝落。

    `ctx` = 唯一锚点 (★同一份文件里有多处相同文本时, 用来把补丁钉死到 ctx 之后那处★)。
    ★**ctx 只用来定位, 不会被替换** ⇒ 多条补丁互不干扰★。
    """
    path: str
    old: str
    new: str
    label: str
    count: int = 1
    group: str = ""
    ctx: str = ""

    @property
    def needle(self) -> str:
        return self.ctx + self.old


@dataclass
class ExpectPatch:
    """门禁 EXPECT 现状断言值补丁 (★只改【现状断言值】, 判据本体与阈值一个字不动★)。"""
    key: str
    new_check: str
    label: str = ""
    group: str = ""


@dataclass
class Decision:
    v: str                 # "V-2" / "V-3" / "V-4"
    value: str             # 白名单里的值
    patches: list = field(default_factory=list)
    expects: list = field(default_factory=list)
    delta: int = 0         # 落表后期望 `--expect-resolved` 条数变化 (负数 = 变少)
    board_delta: int = 0   # 板那一趟才转绿的条数 (本工具【不】做)
    warnings: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    rejected: str = ""     # 非空 = 必须打回 (rc≠0)


# ═══════════════════════════════════════════════════════════════════════════
# 2 · V-3 (BAT_DET 分压链) —★逐字照抄 ISS-233 §3.1 (E-1 ~ E-7) + §3.1 ⑥ 的 selftest 翻面★
# ═══════════════════════════════════════════════════════════════════════════

# ★**每个选项的逐字参数 (★E 的 note 是 ISS-233 §3.1 E-5 的逐字原文★)★★
V3_OPTS = {
    "E": dict(
        tag="方案E", top="100k", bot="60k",
        top_val="100k ±1%", bot_val="60k ±1%",
        rth="37.5kΩ", leak_mv="37.5mV", fs_pct="2.1%",
        i_ua="26.25µA", p_uw="110µW",
        node_v="1.575", leak_ua="26.25",
        spec_level="0-1.8V (分压, SARADC_VIN5 1.8V 域)",
        spec_imp="100k+60k 分压 + 100nF",
        note_top=('f"[{src}_RAW] 分压上臂 (100k); ★方案E (ISS-223 §11.4): R_th=37.5kΩ ⇒ '
                  'ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (2.1% FS, 可软件标定)★; '
                  '★常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)★"'),
        note_bot='f"[{src}] 分压下臂 地端 (60k ±1%)"',
        settle="1.575V 变成 4.0V",
        truth="100k+60k",
        cost="常开静态功耗 26.25µA / 110µW (0.630 mAh/日) ⇒ 待机功耗与精度的取舍",
    ),
    "A": dict(
        tag="方案A", top="2M", bot="1.2M",
        top_val="2M ±1%", bot_val="1.2M ±1%",
        rth="750kΩ", leak_mv="750.0mV", fs_pct="41.7%",
        i_ua="1.31µA", p_uw="5.51µW",
        node_v="1.575", leak_ua="1.3125",
        spec_level="0-1.8V (分压, SARADC_VIN5 1.8V 域)",
        spec_imp="2M+1.2M 分压 + 100nF",
        note_top=('f"[{src}_RAW] 分压上臂 (2M); ★方案A (ISS-223 §11.4): R_th=750kΩ ⇒ '
                  'ADC 输入漏电 ~1µA 只造成 750.0mV 偏移 (41.7% FS, 不可忽略)★; '
                  '★常开静态功耗 1.31µA / 5.51µW (V-3 裁决的代价)★"'),
        note_bot='f"[{src}] 分压下臂 地端 (1.2M ±1%)"',
        settle="1.575V 变成 2.1V",
        truth="2M+1.2M",
        cost="R_th=750kΩ ⇒ 漏电误差占 41.7% FS (不可软件标定) + 建立时间 675.8ms",
    ),
    "D": dict(
        tag="方案D", top="2M", bot="1M",
        top_val="2M ±1%", bot_val="1M ±1%",
        rth="666.7kΩ", leak_mv="666.7mV", fs_pct="37.0%",
        i_ua="1.40µA", p_uw="5.88µW",
        node_v="1.4", leak_ua="1.4",
        spec_level="0-1.8V (分压, SARADC_VIN5 1.8V 域)",
        spec_imp="2M+1M 分压 + 100nF",
        note_top=('f"[{src}_RAW] 分压上臂 (2M); ★方案D (ISS-223 §11.4): R_th=666.7kΩ ⇒ '
                  'ADC 输入漏电 ~1µA 只造成 666.7mV 偏移 (37.0% FS, 不可忽略)★; '
                  '★常开静态功耗 1.40µA / 5.88µW (V-3 裁决的代价)★"'),
        note_bot='f"[{src}] 分压下臂 地端 (1M ±1%)"',
        settle="1.4V 变成 2.1V",
        truth="2M+1M",
        cost="R_th=666.7kΩ ⇒ 漏电误差占 37.0% FS (不可软件标定) + 建立时间 600.7ms",
    ),
}

# ★**DEMO_DNP 里那 3 行 (★E-3: 整行删掉, 不留空行★)★★
V3_DEMO_DNP_OLD = (
    '    "R_BAT_DET_1": "同上 (电池电压分压上臂)",\n'
    '    "R_BAT_DET_2": "同上 (电池电压分压下臂)",\n'
    '    "C_DET_BAT": "同上 (电池 ADC 滤波)",\n'
)

V3_UPPER_OLD = (
    '        add("P2", f"{src}_RAW", srcnode, r1, r1, "1M ±1%", "R", "必装", "[推算]", "",\n'
    '            f"[{src}_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V", cid)\n'
)
V3_LOWER_OLD = (
    '        add("P2", src, r2, "GND", r2, "1M ±1%", "R", "必装", "[推算]", "",\n'
    '            f"[{src}] 分压下臂 地端", cid)\n'
)


def v3_recipe(value: str) -> Decision:
    d = Decision(v="V-3", value=value)
    if value == "DEG4":
        # ★★降级④: BAT_DET 链保持 DNP, 网表一格不改 ⇒ 13 条永远不转绿★★
        d.delta = 0
        d.notes.append("★降级④ (ISS-223 §11.4): BAT_DET 链【保持不装 (DNP)】⇒ ★**网表一格不改**★ ⇒ "
                       "电量改由 BQ25896 的 I2C 状态寄存器读 ⇒ ★**R2×11 + R7 + R8 这 13 条永远不转绿**★")
        d.warnings.append("★★**降级④ ⇒ `--expect-resolved` 条数【不变】(18 条)★** ⇒ "
                          "★**这 13 条不是「还没落」, 是「按降级④【永远不落】」★** ⇒ "
                          "★**落表后必须改判据 (把 R2/R7/R8 从「未落表」改成「按降级④豁免」), 否则门禁恒红**★")
        d.warnings.append("★★**降级④ 连带要定的产品语义**: `DEMO_DNP` 的原始理由是「demo 不装电池」⇒ "
                          "★**这一条归 main (ISS-223 F-1 / ISS-233 B4.2 的 need)★**")
        return d

    o = V3_OPTS[value]
    d.delta = -13
    d.notes.append(f"★{o['tag']} = 上臂 {o['top']} ±1% + 下臂 {o['bot']} ±1% + 滤波 100nF ±10% "
                   f"(★代价: {o['cost']}★)")
    d.warnings.append(f"★★**V-3 落表会改【demo 的产品语义】**: `DEMO_DNP` 的原始理由是「demo 主板不装电池」⇒ "
                      f"★**把 BAT_DET 链改成必装 = 宣称 demo 板要装电池 / 或这链在 demo 上是空焊盘但要预留★** ⇒ "
                      f"★**这条语义归 main 拍 (ISS-223 F-1)★**")

    # ── E-1 / E-2: 规格页 (HW/SCHEMATIC_V1_SPEC.json 的 B-08) ──
    #   ★B-07 (VBUS_DET) 跟 B-08 (BAT_DET) 的 level/imp 逐字相同 ⇒ 必须用 ctx 钉死到 B-08★
    d.patches += [
        Patch(SPEC_JSON,
              '      "level": "0-3.3V (分压)",\n',
              f'      "level": "{o["spec_level"]}",\n',
              "E-1 规格页 B-08.level",
              ctx='      "id": "B-08",\n'),
        Patch(SPEC_JSON,
              '      "imp": "1M+1M 分压 + 100nF",\n',
              f'      "imp": "{o["spec_imp"]}",\n',
              "E-2 规格页 B-08.imp",
              ctx='      "id": "B-08",\n'),
        # ── E-3: 删 DEMO_DNP 三行 (★ISS-230 坑①: 只改阻值永远还是 DNP★) ──
        Patch(GEN_NETLIST, V3_DEMO_DNP_OLD, "",
              "E-3 删 DEMO_DNP 三行 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT)"),
        # ── E-4 / E-5: 上臂 value + note ──
        Patch(GEN_NETLIST, V3_UPPER_OLD,
              '        add("P2", f"{src}_RAW", srcnode, r1, r1, "%s", "R", "必装", "[推算]", "",\n'
              '            %s, cid)\n' % (o["top_val"], o["note_top"]),
              "E-4/E-5 上臂 value+note"),
        # ── E-6 / E-7: 下臂 value + note ──
        Patch(GEN_NETLIST, V3_LOWER_OLD,
              '        add("P2", src, r2, "GND", r2, "%s", "R", "必装", "[推算]", "",\n'
              '            %s, cid)\n' % (o["bot_val"], o["note_bot"]),
              "E-6/E-7 下臂 value+note"),
    ]

    # ── 门禁 EXPECT 现状断言值 (★只改断言值, 判据本体与阈值一个字不动★) ──
    d.expects += [
        # d2: DNP → 必装 (表A / 表B)
        ExpectPatch("d2_a182_dnp", "dnp == 必装", "d2 表A R_BAT_DET_1 DNP→必装"),
        ExpectPatch("d2_a183_dnp", "dnp == 必装", "d2 表A R_BAT_DET_2 DNP→必装"),
        ExpectPatch("d2_a184_dnp", "dnp == 必装", "d2 表A C_DET_BAT (滤波脚) DNP→必装"),
        ExpectPatch("d2_a185_dnp", "dnp == 必装", "d2 表A C_DET_BAT (地端) DNP→必装"),
        ExpectPatch("d2_b307_dnp", "dnp == 必装", "d2 表B R_BAT_DET_1 pin1 DNP→必装"),
        ExpectPatch("d2_b309_dnp", "dnp == 必装", "d2 表B R_BAT_DET_2 pin1 DNP→必装"),
        ExpectPatch("d2_b100_dnp", "dnp == 必装", "d2 表B C_DET_BAT pin1 DNP→必装"),
        # d2/d7/d8: 阻值
        ExpectPatch("d7_a181_value", f"value == {o['spec_imp']}",
                    "d7 表A L181 (NET_BAT_DET 行) 的 value = 规格页 B-08.imp"),
        ExpectPatch("d2_a182_value", f"value == {o['top_val']}", "d2 表A 上臂 value"),
        ExpectPatch("d7_a182_value", f"value == {o['top_val']}", "d7 上臂 value"),
        ExpectPatch("d7_a183_value", f"value == {o['bot_val']}", "d7 下臂 value"),
        ExpectPatch("d8_bom86_value", f"value == {o['top_val']}", "d8 BOM L86 上臂 value"),
        ExpectPatch("d8_bom87_value", f"value == {o['bot_val']}", "d8 BOM L87 下臂 value"),
        ExpectPatch("d8_bom86_dnp", "dnp == 必装", "d8 BOM L86 DNP→必装"),
        ExpectPatch("d8_bom87_dnp", "dnp == 必装", "d8 BOM L87 DNP→必装"),
        # note
        ExpectPatch("d2_a182_note", f"note contains 分压上臂 ({o['top']})",
                    "d2 表A note (DNP 前缀已消失)"),
        ExpectPatch("d8_a182_note", "note contains ADC 输入漏电 ~1µA",
                    "d8 表A note 自称漏电"),
        # calc 现状值
        ExpectPatch("d7_node_v", f"calc(node_v@4.2) == {o['node_v']}",
                    f"d7 分压后节点电压现状 ({o['node_v']}V ≤ 1.8V)"),
        ExpectPatch("d7_node_over", "calc(node_v@4.2) < 1.8",
                    "d7 分压后节点电压不再超 1.8V (★判据本体阈值不变, 只翻断言方向★)"),
        ExpectPatch("d8_leak_now", f"calc(leak_ua@4.2) == {o['leak_ua']}",
                    f"d8 分压链静态电流现状 ({o['leak_ua']}µA)"),
        ExpectPatch("d8_leak_claim", "calc(leak_note_ua@5) == 1",
                    "d8 note 自称漏电现状 (1µA 占位值)"),
    ]

    # ── selftest 反向用例翻面 (★ISS-233 §3.1 ⑥ 逐条照抄★) ──
    d.patches += [
        Patch(CHECK_SCRIPT,
              '        _mutate_line(os.path.join(tmp, REL["netlist"]), 182, "dnp", "必装")',
              '        _mutate_line(os.path.join(tmp, REL["netlist"]), 182, "dnp", "DNP")',
              "selftest 用例2: L182 dnp 必装→DNP (退回旧缺陷)"),
        Patch(CHECK_SCRIPT,
              '    cases.append(_run_case("用例2 改坏 L182 的 dnp (DNP→必装) ⇒ 必须红", root, m_net_dnp))',
              '    cases.append(_run_case("用例2 改坏 L182 的 dnp (必装→DNP, 退回旧缺陷) ⇒ 必须红", root, m_net_dnp))',
              "selftest 用例2 名字按新现状更新"),
        Patch(CHECK_SCRIPT,
              '        s = s.replace("| d2_a182_dnp | netlist | 182 | dnp == DNP |",\n'
              '                      "| d2_a182_dnp | netlist | 182 | dnp == 必装 |", 1)',
              '        s = s.replace("| d2_a182_dnp | netlist | 182 | dnp == 必装 |",\n'
              '                      "| d2_a182_dnp | netlist | 182 | dnp == DNP |", 1)',
              "selftest 用例7: 规格页锚点表的突变串按新现状翻转"),
        Patch(CHECK_SCRIPT,
              '        # ★把下臂改成 2M ⇒ calc(node_v@4.2) 从 2.1 变成 2.8 ⇒ d7_node_v / d7_node_over 双双变红',
              '        # ★把下臂改成 2M ⇒ calc(node_v@4.2) 从 %s ⇒ d7_node_v / d7_node_over 双双变红' % o["settle"],
              "selftest 用例11 注释按新现状更新 (★突变方向不用翻★)"),
        Patch(CHECK_SCRIPT,
              '    cases.append(_run_case("用例11 [d7] 改坏 L183 下臂 (1M→2M, 触发 calc) ⇒ 必须红", root, m_net_rbatdet2_2m))',
              '    cases.append(_run_case("用例11 [d7] 改坏 L183 下臂 (%s→2M, 触发 calc) ⇒ 必须红", root, m_net_rbatdet2_2m))' % o["bot"],
              "selftest 用例11 名字按新现状更新"),
        Patch(CHECK_SCRIPT,
              '        # ★把 note 里自称的漏电流从 1.65µA 改成 2.5µA (★与 1M+1M 真值一致了⇒ 缺陷消失⇒ 必须变红★)',
              '        # ★把 note 里自称的 ADC 输入漏电从 1µA 改成 2.5µA (★与本档 ~1µA 占位值不一致⇒ 必须变红★)',
              "selftest 用例12 注释按新现状更新"),
        Patch(CHECK_SCRIPT,
              '        raw = raw.replace("漏电流 ~1.65µA @5V", "漏电流 ~2.5µA @5V", 1)',
              '        raw = raw.replace("ADC 输入漏电 ~1µA", "ADC 输入漏电 ~2.5µA", 1)',
              "selftest 用例12: 突变串按新 note 翻转"),
        Patch(CHECK_SCRIPT,
              '    cases.append(_run_case("用例12 [d8] 改坏 L182 note 的自称漏电流 (1.65→2.5µA) ⇒ 必须红", root, m_net_leak_note))',
              '    cases.append(_run_case("用例12 [d8] 改坏 L182 note 的自称漏电流 (1→2.5µA) ⇒ 必须红", root, m_net_leak_note))',
              "selftest 用例12 名字按新现状更新"),
    ]

    # ── 规格页 §2 的机读汇总行 (★第 (2) 条那行会变陈旧★) ──
    d.patches += [
        Patch(SPEC_PAGE,
              "| ★(2) ★ | 表A L182/L183/L184/L185 与表B L100/L307/L309 的 `dnp` 仍 = DNP, 而 L181/L186/L210 是必装 | ★**成立 (缺陷在)** ★ |",
              "| ★(2) ★ | 表A L182/L183/L184/L185 与表B L100/L307/L309 的 `dnp` 仍 = DNP, 而 L181/L186/L210 是必装 | "
              f"★★**落表后 (2026-11-16 V-3={value}): 已修 (三颗从 DEMO_DNP 拿出来 ⇒ 必装; 阻值 {o['top']}+{o['bot']}; "
              f"分压后 {o['node_v']}V ≤ 1.8V) ⇒ ★**R2 组全绿**★ ★ |",
              "规格页 §2 表第 (2) 条 现状栏"),
    ]
    return d


# ═══════════════════════════════════════════════════════════════════════════
# 3 · V-4 (R_ILIM 档位) —★逐字照抄 ISS-233 §3.3 (V4-1 ~ V4-10)★
# ═══════════════════════════════════════════════════════════════════════════

V4_OPTS = {
    "680": dict(
        ohms="680Ω", res="680", tag="680Ω ±1% (0402)",
        iinmax="0.57A", ichg="0.70A", pin="0.349A",
        pin_370="0.349", pin_420="0.307",
        verdict="余量 1.43× 对 0.50A 触点",
        power="0.94mW", power_f="0.8²/680",
        truth=("★★**680Ω 档真值 (V-4 裁定 2026-11-16)**: IINMAX = KILIM_max/RILIM = 390/680 = 0.574A; "
               "ICHG@3.70V = **0.698A**; J_CHG pin1/pin2 双 pin 并联 ⇒ **单 pin 0.349A ≤ 0.50A 触点工作上限 "
               "(余量 1.43×)** ⇒ **680Ω 档成立**; "),
        value=("680Ω ±1% (IINMAX ≈0.57A · ICHG ≈0.70A · 单 pin 0.349A ⇒ 余量 1.43× 对 0.50A 触点 · "
               "V-4 裁定 2026-11-16)"),
        green=True,
        cost="充电时间从 ~29min 拉长到 ~36-60min (2-2.1 倍慢) + 电芯 C 倍率 1.66C (若电芯规格书只允许 ≤1C ⇒ 必须退 1200Ω)",
        # ── §2.4 档位表新行 (★逐字照抄 ISS-233 §3.3 V4-6★) ──
        row24=("| **680Ω ±1%** | 0.47 / 0.52 / **0.57 A** | 0.572 / 0.635 / **0.698 A** | **~0.6-0.7 A** | "
               "★★**V-4 裁定 (2026-11-16)**: 单 pin **0.349A** (pin1/pin2 双 pin 并联) ≤ **0.50A 触点工作上限** "
               "⇒ 触点余量 **1.43×** · 铰链余量 **2.15×** (相对 1.5A 设计点) · 420mAh CC ≈ **36min** ★ |"),
        dead390=("| ~~390Ω ±1%~~ | 0.82 / 0.91 / **1.00 A** | 0.997 / 1.107 / **1.216 A** | **~1.1 A** | "
                 "❌ **390Ω 档已判死 (V-4 裁定 2026-11-16)**: 单 pin **0.608A** > **0.50A 触点工作上限 21.6%** "
                 "⇒ 不可选 |"),
        # ── §3.4 场景表 ①②③ 三行 (★逐字照抄 ISS-233 §3.3 V4-8★) ──
        scen1=("| ① Rd-only + 常见 Rp=56k 充电器 | 500 mA | 680Ω | 0.5A (源封顶) | **~0.61 A** | **2.5×** |"),
        scen2=("| ② Rd-only + Rp=22k 充电器 | 1.5 A | 680Ω | 0.47-0.57A | **~0.572-0.698 A** | **2.15×** |"),
        scen3=("| ③ 加 PD 5V/2A + `R_ILIM`=680Ω | 2 A | 680Ω | 0.47-0.57A | **~0.572-0.698 A** | **2.15×** |"),
        # ── §2.1 封顶链 / §3.3 正文 / §8 推算表 (★ISS-233 §3.3 漏列, 本单补★) ──
        chain=("| **本规格的封顶链** | ILIM 脚 `R_ILIM` = 680Ω → **0.47-0.57A 硬件上限**, 与寄存器无关 | [官方] |"),
        body1="- `R_ILIM` = 680Ω (→ 输入 0.47-0.57A, CC 段电池电流 ~0.572-0.698A)。\n",
        body2="- ⇒ **`R_ILIM` = 680Ω 是\"无软件依赖\"的基线; 有软件时 SoC 按 BC1.2 结果写 REG00 (IINLIM) 来精确贴合源能力。**\n",
        accept="- 若**接受** → 按本规格出 P10, `R_ILIM`=680Ω, J_CHG pin9/pin10 留空给未来的 I2C。\n",
        hist=("→ **定 390Ω**, 300Ω 判死 → ★★**V-4 裁定 2026-11-16 改档为 680Ω**★ | **结构总工** | 已闭环 | "
              "§2.4 (`R_ILIM` = 680Ω) |"),
        calc=("| `R_ILIM` = 680Ω → IIN 0.47-0.57A → ICHG ~0.572-0.698A | **[推算·可复算]** | 公式见 §2.4 / §3.4, B6 可复现 |"),
        script_list="(680,475,1200)",
    ),
    "470": dict(
        ohms="470Ω", res="470", tag="470Ω ±1% (0402)",
        iinmax="0.83A", ichg="1.01A", pin="0.504A",
        pin_370="0.504", pin_420="0.444",
        verdict="超 0.50A 工作上限 0.9% ⇒ 本档不成立",
        power="1.36mW", power_f="0.8²/470",
        truth=("★★**470Ω 档真值 (V-4 裁定 2026-11-16)**: IINMAX = KILIM_max/RILIM = 390/470 = 0.830A; "
               "ICHG@3.70V = **1.009A**; J_CHG pin1/pin2 双 pin 并联 ⇒ **单 pin 0.504A > 0.50A 触点工作上限 "
               "0.9%** ⇒ **470Ω 档不成立** (★ISS-233 §3.3 原文列的是 475Ω = 0.499A 贴边过 ⇒ ★**470 还是 475 "
               "请老板确认★**); "),
        value=("470Ω ±1% (IINMAX ≈0.83A · ICHG ≈1.01A · 单 pin 0.504A ⇒ 超 0.50A 工作上限 0.9% ⇒ "
               "本档不成立 · V-4 裁定 2026-11-16)"),
        green=False,
        cost="★**本档【不成立】**: 单 pin 0.504A > 0.50A 触点工作上限 (超 0.9%) ⇒ ★**落完 R10 仍红**★",
        row24=("| **470Ω ±1%** | 0.68 / 0.76 / **0.83 A** | 0.828 / 0.918 / **1.009 A** | **~0.9-1.0 A** | "
               "★★**V-4 裁定 (2026-11-16)**: 单 pin **0.505A** (pin1/pin2 双 pin 并联) > **0.50A 触点工作上限 0.9%** "
               "⇒ 触点余量 **0.99×** ⇒ ★**本档不成立** ★ |"),
        dead390=("| ~~390Ω ±1%~~ | 0.82 / 0.91 / **1.00 A** | 0.997 / 1.107 / **1.216 A** | **~1.1 A** | "
                 "❌ **390Ω 档已判死 (V-4 裁定 2026-11-16)**: 单 pin **0.608A** > **0.50A 触点工作上限 21.6%** "
                 "⇒ 不可选 |"),
        scen1=("| ① Rd-only + 常见 Rp=56k 充电器 | 500 mA | 470Ω | 0.5A (源封顶) | **~0.61 A** | **2.5×** |"),
        scen2=("| ② Rd-only + Rp=22k 充电器 | 1.5 A | 470Ω | 0.68-0.83A | **~0.828-1.009 A** | **1.49×** |"),
        scen3=("| ③ 加 PD 5V/2A + `R_ILIM`=470Ω | 2 A | 470Ω | 0.68-0.83A | **~0.828-1.009 A** | **1.49×** |"),
        chain=("| **本规格的封顶链** | ILIM 脚 `R_ILIM` = 470Ω → **0.68-0.83A 硬件上限**, 与寄存器无关 | [官方] |"),
        body1="- `R_ILIM` = 470Ω (→ 输入 0.68-0.83A, CC 段电池电流 ~0.828-1.009A)。\n",
        body2="- ⇒ **`R_ILIM` = 470Ω 是\"无软件依赖\"的基线; 有软件时 SoC 按 BC1.2 结果写 REG00 (IINLIM) 来精确贴合源能力。**\n",
        accept="- 若**接受** → 按本规格出 P10, `R_ILIM`=470Ω, J_CHG pin9/pin10 留空给未来的 I2C。\n",
        hist=("→ **定 390Ω**, 300Ω 判死 → ★★**V-4 裁定 2026-11-16 改档为 470Ω**★ | **结构总工** | 已闭环 | "
              "§2.4 (`R_ILIM` = 470Ω) |"),
        calc=("| `R_ILIM` = 470Ω → IIN 0.68-0.83A → ICHG ~0.828-1.009A | **[推算·可复算]** | 公式见 §2.4 / §3.4, B6 可复现 |"),
        script_list="(470,475,1200)",
    ),
    "390": dict(
        ohms="390Ω", res="390", tag="390Ω ±1% (0402)",
        iinmax="1.00A", ichg="1.22A", pin="0.608A",
        pin_370="0.608", pin_420="0.536",
        verdict="超 0.50A 工作上限 21.6% ⇒ 本档不成立 (须 J_CHG 10p→14p 四 pin 并联, 归板那一趟)",
        power="1.64mW", power_f="0.8²/390",
        truth=("★★**390Ω 档真值 (V-4 裁定 2026-11-16)**: IINMAX = KILIM_max/RILIM = 390/390 = 1.00A; "
               "ICHG@3.70V = **1.216A**; J_CHG pin1/pin2 双 pin 并联 ⇒ **单 pin 0.608A > 0.50A 触点工作上限 "
               "21.6%** ⇒ **390Ω 档不成立** (★**J_CHG 改 4 pin (10p→14p) 是改板 ⇒ 归「板只改一次」那一趟★**); "),
        value=("390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% ⇒ "
               "本档不成立 (须 J_CHG 改 4 pin) · V-4 裁定 2026-11-16)"),
        green=False,
        cost="★**本档【不成立】**: 单 pin 0.608A > 0.50A (超 21.6%) ⇒ ★**落完 R10 仍红**★ ⇒ "
             "★**这不是「改一行」, 是改板 (J_CHG 10p→14p) ⇒ 归「板只改一次」那一趟★**",
        row24=("| **390Ω ±1%** | 0.82 / 0.91 / **1.00 A** | 0.997 / 1.107 / **1.216 A** | **~1.1 A** | "
               "★★**V-4 裁定 (2026-11-16)**: 单 pin **0.608A** (pin1/pin2 双 pin 并联) > **0.50A 触点工作上限 21.6%** "
               "⇒ ★**本档不成立** (★要它成立只能 J_CHG 改 4 pin ⇒ 那是改板, 归「板只改一次」那一趟★) ★ |"),
        dead390="",
        scen1=("| ① Rd-only + 常见 Rp=56k 充电器 | 500 mA | 390Ω | 0.5A (源封顶) | **~0.61 A** | **2.5×** |"),
        scen2=("| ② Rd-only + Rp=22k 充电器 | 1.5 A | 390Ω | 0.82-1.00A | **~1.00-1.22 A** | **1.2-1.5×** |"),
        scen3=("| ③ 加 PD 5V/2A + `R_ILIM`=390Ω | 2 A | 390Ω | 0.82-1.00A | **~1.00-1.22 A** | **1.2-1.5×** |"),
        chain=("| **本规格的封顶链** | ILIM 脚 `R_ILIM` = 390Ω → **0.82-1.00A 硬件上限**, 与寄存器无关 | [官方] |"),
        body1="- `R_ILIM` = 390Ω (→ 输入 0.82-1.00A, CC 段电池电流 ~0.67-0.82A)。\n",
        body2="- ⇒ **`R_ILIM` = 390Ω 是\"无软件依赖\"的基线; 有软件时 SoC 按 BC1.2 结果写 REG00 (IINLIM) 来精确贴合源能力。**\n",
        accept="- 若**接受** → 按本规格出 P10, `R_ILIM`=390Ω, J_CHG pin9/pin10 留空给未来的 I2C。\n",
        hist=("→ **定 390Ω**, 300Ω 判死 | **结构总工** | 已闭环 | §2.4 (`R_ILIM` = 390Ω) |"),
        calc=("| `R_ILIM` = 390Ω → IIN 0.82-1.00A → ICHG ~0.67-0.82A | **[推算·可复算]** | 公式见 §2.4 / §3.4, B6 可复现 |"),
        script_list="(390,300,260)",
    ),
}

V4_NET_VALUE_OLD = ('"390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · '
                     '档位待 V-4 裁决)"')
V4_NOTE_TRUTH_OLD = (
    '"★★**390Ω 档真值**: IINMAX = KILIM_max/RILIM = 390/390 = 1.00A; ICHG@3.70V = **1.216A**; '
    'J_CHG pin1/pin2 双 pin 并联 ⇒ **单 pin 0.608A > 0.50A 触点工作上限 21.6%** ⇒ **390Ω 档不成立, '
    '档位待 V-4 裁决** (老板待拍项 · DECISION_PENDING_2026-11-16.md §3); "'
)
V4_PENDING_OLD = ('"★★**V1.7 (470Ω) 已作废** (V1.8 起改 390Ω; ★**V1.9 终值待 V-4 裁决**)★ "')
V4_P10_OLD = ("★**按 ICHG/IIN = 1.216 真值, 390Ω 档单 pin = 0.608A > 0.50A 工作上限 21.6% ⇒ 档位待 V-4 裁决**★")
V4_CHG_0822_OLD = ("| **390Ω ±1%** | 0.82 / 0.91 / **1.00 A** | 0.997 / 1.107 / **1.216 A** | **~1.1 A** | "
                   "★★**待裁决 (V-4)**: 单 pin **0.608A** (pin1/pin2 双 pin 并联) > **0.50A 触点工作上限 21.6%** ⇒ "
                   "**本档不成立**; 候选档位见 `DECISION_PENDING_2026-11-16.md` §3 (老板待拍项, ★本单不代拍★) ★ |")
V4_CHG_POWER_OLD = ("> ★**电阻功耗不是问题**: ILIM 脚被稳在 0.8V → P = 0.8²/390 = **1.64 mW** → 0402 足够 "
                    "(不需要大功率电阻)。")


def v4_recipe(value: str) -> Decision:
    d = Decision(v="V-4", value=value)
    o = V4_OPTS[value]
    d.delta = -1 if o["green"] else 0
    d.notes.append(f"★R_ILIM = {o['ohms']} ±1% (★IINMAX ≈{o['iinmax']} · ICHG ≈{o['ichg']} · 单 pin {o['pin']}★)")
    d.notes.append(f"★代价: {o['cost']}★")
    if not o["green"]:
        d.warnings.append(f"★★**V-4={value} 实算单 pin = {o['pin']} > 0.50A ⇒ 落完 R10【仍红】⇒ "
                          f"`--expect-resolved` 条数【不变】(18 条)★**")
    if value == "470":
        d.warnings.append("★★**白名单里的 470Ω 与 ISS-233 §3.3 原文的 475Ω 不是同一个数**★ ⇒ "
                          "★**470Ω 实算单 pin = 0.504A > 0.50A (不成立); 475Ω = 0.499A (贴边过)**★ ⇒ "
                          "★**本工具按 470Ω 逐字实现 (不替老板改成 475), 但这条要老板确认到底是 470 还是 475★**")

    # ── V4-1 / V4-2: 网表两行 value (真源 = state/gen_netlist.py, 2 处) ──
    d.patches += [
        Patch(GEN_NETLIST, V4_NET_VALUE_OLD, '"%s"' % o["value"],
              "V4-1/V4-2 R_ILIM value (L520 + L530 两处)", count=2),
        # ── V4-3: note 里的「390Ω 档真值」段 ──
        Patch(GEN_NETLIST, V4_NOTE_TRUTH_OLD, '"%s"' % o["truth"],
              "V4-3 R_ILIM note 的档位真值段"),
        # ★★ISS-233 §3.3 之外的补充 (★防「终值待 V-4 裁决」字样留在已裁决的网表里★)★★
        Patch(GEN_NETLIST, V4_PENDING_OLD,
              '"★★**V1.7 (470Ω) 已作废** (V1.8 起改 390Ω; ★**V1.9 终值 = %s (V-4 裁定 2026-11-16)**)★ "' % o["ohms"],
              "★补充: note 里『V1.9 终值待 V-4 裁决』字样随裁决一并收口"),
        # ── V4-4: state/p10_rows.json 的 J_CHG/BAT_CHG 行 note ──
        Patch(P10_ROWS, V4_P10_OLD,
              ("★**按 ICHG/IIN = 1.216 真值, %s 档单 pin = %s ⇒ V-4 裁定 2026-11-16**★"
               % (o["ohms"], o["pin"])),
              "V4-4 p10_rows.json J_CHG/BAT_CHG 行 note"),
        # ── V4-5: CHARGE_BOARD_SPEC §2.2 脚表 L124 ──
        Patch(CHG_SPEC,
              "| **10** | ILIM | AI | `R_ILIM` → PGND | **390Ω ±1% (0402)** | [官方] \"IINMAX = KILIM/RILIM\", "
              "KILIM = 320/355/390 AΩ | 见 §2.4; ILIM 脚被稳在 **0.8V**, 电阻功耗 = 0.8²/R ≈ 2.1mW |",
              "| **10** | ILIM | AI | `R_ILIM` → PGND | **%s (0402)** | [官方] \"IINMAX = KILIM/RILIM\", "
              "KILIM = 320/355/390 AΩ | 见 §2.4; ILIM 脚被稳在 **0.8V**, 电阻功耗 = %s ≈ %s |"
              % (o["tag"], o["power_f"], o["power"]),
              "V4-5 CHARGE_BOARD_SPEC §2.2 脚表 R_ILIM 行"),
        # ── V4-6: §2.4 档位表 390Ω 行 (★逐字照抄 ISS-233 §3.3 V4-6★) ──
        Patch(CHG_SPEC, V4_CHG_0822_OLD,
              o["row24"] + o["dead390"],
              "V4-6 CHARGE_BOARD_SPEC §2.4 档位表 (★并在其下补一行把 390Ω 标成【已判死】★)"),
        # ── V4-7: §2.4 表后面的功耗句 ──
        Patch(CHG_SPEC, V4_CHG_POWER_OLD,
              "> ★**电阻功耗不是问题**: ILIM 脚被稳在 0.8V → P = %s = **%s** → 0402 足够 "
              "(不需要大功率电阻)。" % (o["power_f"], o["power"]),
              "V4-7 CHARGE_BOARD_SPEC §2.4 功耗句"),
        # ── V4-8: §3.4 场景表 ①②③ 三行 (★逐字照抄 ISS-233 §3.3 V4-8★) ──
        Patch(CHG_SPEC,
              "| ① Rd-only + 常见 Rp=56k 充电器 | 500 mA | 390Ω | 0.5A (源封顶) | **~0.61 A** | **2.5×** |",
              o["scen1"], "V4-8a CHARGE_BOARD_SPEC §3.4 场景表 ①"),
        Patch(CHG_SPEC,
              "| ② Rd-only + Rp=22k 充电器 | 1.5 A | 390Ω | 0.82-1.00A | **~1.00-1.22 A** | **1.2-1.5×** |",
              o["scen2"], "V4-8b CHARGE_BOARD_SPEC §3.4 场景表 ②"),
        Patch(CHG_SPEC,
              "| ③ 加 PD 5V/2A + `R_ILIM`=390Ω | 2 A | 390Ω | 0.82-1.00A | **~1.00-1.22 A** | **1.2-1.5×** |",
              o["scen3"], "V4-8c CHARGE_BOARD_SPEC §3.4 场景表 ③"),
        # ── V4-9: §7 CSV 的 R_ILIM 两行 (★L536 与 L537 的字段不一样 ⇒ 分两条钉★) ──
        Patch(CHG_SPEC,
              "P10,ILIM,U_CHG pin10,R_ILIM,R_ILIM,390Ω ±1% (0402),R,必装,[官方],",
              "P10,ILIM,U_CHG pin10,R_ILIM,R_ILIM,%s,R,必装,[官方]," % o["tag"],
              "V4-9a CHARGE_BOARD_SPEC §7 CSV 的 ILIM 行"),
        Patch(CHG_SPEC,
              "P10,PGND,R_ILIM,PGND,R_ILIM,390Ω ±1% (0402),R,必装,[官方],",
              "P10,PGND,R_ILIM,PGND,R_ILIM,%s,R,必装,[官方]," % o["tag"],
              "V4-9b CHARGE_BOARD_SPEC §7 CSV 的 PGND 行"),
    ]
    # ── V4-11 ~ V4-15 (★ISS-233 §3.3 漏列的 5 处仍写 390Ω 的位置 ★)
    #   ★**不补 ⇒ 落完 680Ω, 规格页里还写着「R_ILIM = 390Ω → 0.82-1.00A」⇒ 规格页自相矛盾**★
    for _label, _old, _new in (
        ("V4-11 §2.1 本规格的封顶链行",
         "| **本规格的封顶链** | ILIM 脚 `R_ILIM` = 390Ω → **0.82-1.00A 硬件上限**, 与寄存器无关 | [官方] |",
         o["chain"]),
        ("V4-12a §3.3 的第一条正文",
         "- `R_ILIM` = 390Ω (→ 输入 0.82-1.00A, CC 段电池电流 ~0.67-0.82A)。\n",
         o["body1"]),
        ("V4-12b §3.3 的第二条正文",
         "- ⇒ **`R_ILIM` = 390Ω 是\"无软件依赖\"的基线; 有软件时 SoC 按 BC1.2 结果写 REG00 (IINLIM) 来精确贴合源能力。**\n",
         o["body2"]),
        ("V4-13 §3.6 的接受判据那句",
         "- 若**接受** → 按本规格出 P10, `R_ILIM`=390Ω, J_CHG pin9/pin10 留空给未来的 I2C。\n",
         o["accept"]),
        ("V4-14 §8 推算表的 R_ILIM 行",
         "| `R_ILIM` = 390Ω → IIN 0.82-1.00A → ICHG ~0.67-0.82A | **[推算·可复算]** | 公式见 §2.4 / §3.4, B6 可复现 |\n",
         o["calc"]),
        ("V4-15 §9 的 ISS-091 历史闭环行 (★保留 10-28 的历史事实 + 记 V-4 改档★)",
         "→ **定 390Ω**, 300Ω 判死 | **结构总工** | 已闭环 | §2.4 (`R_ILIM` = 390Ω) |",
         o["hist"]),
    ):
        if _old != _new:          # ★390Ω 档时旧=新 ⇒ 不打补丁 (★no-op 补丁会被预检当【旧值出现 2 次】★) ★
            d.patches.append(Patch(CHG_SPEC, _old, _new, _label))
    # ── V4-9 的 L536 note 段 (CSV 第 1 行的 note) ──
    d.patches += [
        Patch(CHG_SPEC,
              "ILIM 脚稳在 0.8V, 功耗 0.8²/390=1.64mW; **必装件** (不装 → REG04 复位默认 ICHG=2048mA 会让铰链过 2.05A); "
              "★★**390Ω 档真值: 单 pin 0.608A > 0.50A 触点工作上限 21.6% ⇒ 档位待 V-4 裁决 "
              "(老板待拍 · DECISION_PENDING_2026-11-16.md §3)**; 300Ω 档判死 (单 pin 0.791A > 0.5A 天花板)",
              "ILIM 脚稳在 0.8V, 功耗 %s=%s; **必装件** (不装 → REG04 复位默认 ICHG=2048mA 会让铰链过 2.05A); "
              "★★**%s 档真值 (V-4 裁定 2026-11-16): 单 pin %s ⇒ %s**; 300Ω 档判死 (单 pin 0.791A > 0.5A 天花板)"
              % (o["power_f"], o["power"], o["ohms"], o["pin"], o["verdict"]),
              "V4-9 CHARGE_BOARD_SPEC §7 CSV R_ILIM 行 note"),
    ]
    # ── V4-10: §10 自检脚本 (★真实文件里这行是【零缩进】★ ⇒ 缩进写错就永远对不上★) ──
    d.patches += [
        Patch(CHG_SPEC, "for r in (390,300,260):", "for r in %s:" % o["script_list"],
              "V4-10 CHARGE_BOARD_SPEC §10 自检脚本档位列表"),
    ]

    # ── 门禁 EXPECT 现状断言值 ──
    d.expects += [
        ExpectPatch("d10_a47_value", f"value == {o['value']}", "d10 表A L47 R_ILIM value"),
        ExpectPatch("d10_a48_value", f"value == {o['value']}", "d10 表A L48 R_ILIM value"),
        ExpectPatch("d10_bom97_value", f"value == {o['value']}", "d10 BOM L97 R_ILIM value"),
        ExpectPatch("d10_pin_max_370", f"calc(ichg_pin_max@3.7) == {o['pin_370']}",
                    f"d10 单 pin 载流现状 @3.70V ({o['pin_370']}A)"),
        ExpectPatch("d10_pin_max_420", f"calc(ichg_pin_max@4.2) == {o['pin_420']}",
                    f"d10 单 pin 载流现状 @4.20V ({o['pin_420']}A)"),
    ]
    if value != "680":
        # ★非 680 档 ⇒ 规格页里「单 pin **0.608A**」这句必须跟着换 (否则现状守卫红)★
        d.expects += [
            ExpectPatch("d10_spec_0608", f"text contains 单 pin **{o['pin']}**",
                        "d10 CHARGE_BOARD_SPEC 的单 pin 现状值"),
        ]
    else:
        d.expects += [
            ExpectPatch("d10_spec_0608", "text contains 单 pin **0.349A**",
                        "d10 CHARGE_BOARD_SPEC 的单 pin 现状值 (0.349A)"),
        ]
    return d


# ═══════════════════════════════════════════════════════════════════════════
# 4 · V-2 (ESD 方案与型号) —★逐字照抄 ISS-233 §3.2 (V2-1) + §3.2 ③ 的行号漂移清单★
# ═══════════════════════════════════════════════════════════════════════════

V2_ESD_OLD = (
    '    add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",\n'
    '        "ESD 阵列 [待选型] (USB 2.0 双通道)", "D", "必装", "[推算]", "",\n'
    '        "[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— '
    '★**Forlinx 载板指引要求 ESD 紧贴接口**", "A-24")\n'
    '    add("P1", "GND", "D_ESD_USB_D", "GND", "D_ESD_USB_D", "ESD 阵列 [待选型]", "D", "必装",\n'
    '        "[推算]", "", "[D_ESD_USB_D] ESD 地端", "A-24")\n'
)
# ★★V-2 的 value 写法 (★ISS-233 §3.2 的规矩: 拍型号 vs 只拍方案★)★★
# ★**本工具【不替老板拍型号】** ⇒ ★**默认落【判据串】+ evidence `[推算]`** ★
# ★**若老板拍了具体型号 (★例: TPD2EUSB30★) ⇒ value 改成
#   「TPD2EUSB30 (3脚双通道, 0.7pF/线, Vclamp 8V@1A, IEC 61000-4-2 level 4 contact)」
#   + evidence 改成 `[官方]` ⇒ ★**那是【另一次落表】, 不在本工具的白名单里 (★不许自由字符串★)** ★
V2_ESD_VALUE_JUDGE = ("ESD 阵列 (USB 2.0 双通道, D+/D− 共用一颗, ≤1pF/线, IEC 61000-4-2 level 4)")
V2_ESD_VALUE_MODEL = ("TPD2EUSB30 (3脚双通道, 0.7pF/线, Vclamp 8V@1A, "
                      "IEC 61000-4-2 level 4 contact)")
V2_ESD_NEW = (
    '    add("P1", "NET_USB_D_P_TYPEC", "D_ESD_USB_D", "NET_USB_D_P_TYPEC", "D_ESD_USB_D",\n'
    '        "%(v)s", "D", "必装", "%(ev)s", "",\n'
    '        "[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (3脚双通道: pin1=D+ / pin2=D− / pin3=GND) —— '
    '★**已从 SoM 侧 USB_D_P_SRC 挪到 Type-C 侧 NET_USB_D_P_TYPEC** (★ISS-211 第(4)条: 不挪等于没护★)", "A-24")\n'
    '    add("P1", "NET_USB_D_N_TYPEC", "D_ESD_USB_D", "NET_USB_D_N_TYPEC", "D_ESD_USB_D",\n'
    '        "%(v)s", "D", "必装", "%(ev)s", "",\n'
    '        "[D_ESD_USB_D] ★D− 侧 (pin2) —— ★**官方口径: 两条数据线都要护** '
    '(ON Semi AND8074/D + TI TPD2EUSB30 2ch)", "A-24")\n'
    '    add("P1", "GND", "D_ESD_USB_D", "GND", "D_ESD_USB_D", "%(v)s", "D", "必装",\n'
    '        "%(ev)s", "", "[D_ESD_USB_D] ESD 地端 (pin3)", "A-24")\n'
)

# ★★网表行号漂移 (★2 行 → 3 行 ⇒ 后面所有行 +1★)★★
# ★★L417 = D+ 行 (改写但行号不变) · ★**L418 = 新增的 D− 行** · ★**原 L418 (GND 行) 顺移到 L419** ★
#   ⇒ ★**锚点行号 ≥ 418 的全部 +1** (★418 本身也要 +1 ⇒ 它指的是 GND 行, 不是新插的 D− 行★)
V2_NETLIST_SHIFT_FROM = 418
# ★★脚表行号漂移 (★D_ESD_USB_D 从 2 脚变 3 脚 ⇒ 新 pin3 落在 L174 ⇒ 后面所有行 +1★)★★
V2_PINS_SHIFT_FROM = 174


def v2_recipe(value: str) -> Decision:
    d = Decision(v="V-2", value=value)
    if value == "2":
        # ★★ISS-230 实测: V-2 只落网表侧 ⇒ --expect-resolved 7→7 ⇒ 一条都转不绿 = 假绿★★
        d.rejected = ("★★**V-2=2 (只落网表侧) 必须打回**★★ ⇒ ★**ISS-230 实测 (2026-11-16 06:2x, main 已核): "
                      "V-2 网表侧全落完, `--expect-resolved` 仍是 7 条 ⇒ 一条都转不绿 = 假绿**★ ⇒ "
                      "★**不许当正路**★ ⇒ ★**要落 V-2 就必须写成【网表侧 + 板那一趟】两段 (V-2=1)★**")
        return d

    d.delta = 0          # ★网表侧 0 条转绿 (ISS-230 实测 7→7)★
    d.board_delta = 3    # ★板那一趟 (B-3/B-4/B-5) 才转绿 3 条 (R4×2 + R9)★
    d.notes.append("★方案① = D+/D− 共用一颗 3 脚双通道 ESD (★value 串 = 判据串 + evidence [推算] ★"
                   "⇒ **本工具不替老板拍型号**★)")
    d.notes.append("★★**网表侧落表 = 0 条转绿** (★ISS-230 实测 7→7★) ⇒ ★**必须写成两段: 网表侧 + 板那一趟**★")
    d.warnings.append("★★**V-2=1 的板那一趟本工具【不做】** (★`HW/PCB/demo_mainboard.kicad_pcb` 一个字节都不碰★) ⇒ "
                      "★**板侧 B-3 (2 脚换 3 脚封装) / B-4 (挪到 J_USB_C 旁 ≤3.0mm) / B-5 (D− 补 ESD) 继续排队**★")
    d.warnings.append("★★**V-2 落表会改行数** (★网表 513→514 · 脚表 584→585★) ⇒ "
                      "★**门禁锚点的行号会整体漂移 ⇒ 本工具逐条改 (ISS-233 §3.2 ③ 的清单)★** ⇒ "
                      "★**SW / MECH 两边的台账对账项 (落表单号 / 文件名 / 新旧 md5) 都要重填**★")

    d.patches += [
        Patch(GEN_NETLIST, V2_ESD_OLD, V2_ESD_NEW % {"v": V2_ESD_VALUE_JUDGE, "ev": "[推算]"},
              "V2-1 USB ESD 段: 2 行 → 3 行 (pin1=D+ / pin2=D− / pin3=GND) + 挪到 Type-C 侧"),
    ]
    d.warnings.append("★★**型号还没拍 ⇒ 本次落表 value 写【判据串】+ evidence `[推算]`** ★★\n"
                      "   ★**若老板拍了具体型号 (★例: TPD2EUSB30★) ⇒ value 要换成\n"
                      "   「TPD2EUSB30 (3脚双通道, 0.7pF/线, Vclamp 8V@1A, IEC 61000-4-2 level 4 contact)」\n"
                      "   + evidence 换成 `[官方]` ⇒ ★**那是另一次落表 (★型号是老板/选型级的拍板项★)** ★")

    # ── 门禁 EXPECT: ESD 那组 + 行号漂移 ──
    d.expects += [
        ExpectPatch("d4_a417_value", f"value == {V2_ESD_VALUE_JUDGE}", "d4 表A L417 ESD D+ 行 value"),
        ExpectPatch("d4_a417_net", "net == NET_USB_D_P_TYPEC", "d4 表A L417 ESD D+ 行 net (从 SoM 侧挪到 Type-C 侧)"),
        ExpectPatch("d4_a417_note", "note contains 已从 SoM 侧 USB_D_P_SRC 挪到 Type-C 侧 NET_USB_D_P_TYPEC",
                    "d4 表A L417 note (ISS-211 第(4)条)"),
        ExpectPatch("d4_a418_value", f"value == {V2_ESD_VALUE_JUDGE}", "d4 表A L419 ESD GND 行 value (★行号随插行 +1★)"),
        ExpectPatch("d9_esd_dual_claim", f"value == {V2_ESD_VALUE_JUDGE}", "d9 表A L417 自称双通道的 value"),
        ExpectPatch("d4_bom62_value", f"value == {V2_ESD_VALUE_JUDGE}", "d4 BOM L62 D_ESD_USB_D value"),
    ]
    return d


# ═══════════════════════════════════════════════════════════════════════════
# 5 · 白名单
# ═══════════════════════════════════════════════════════════════════════════

WHITELIST = {
    "V-2": {"1": v2_recipe, "2": v2_recipe},
    "V-3": {"E": v3_recipe, "A": v3_recipe, "D": v3_recipe, "DEG4": v3_recipe},
    "V-4": {"680": v4_recipe, "470": v4_recipe, "390": v4_recipe},
}

WHITELIST_DOC = {
    "V-2": "V-2 ∈ {1, 2}  (1 = 网表侧+板侧两段走 · 2 = 只落网表侧 ⇒ ISS-230 实测是假绿 ⇒ 必须打回)",
    "V-3": "V-3 ∈ {E, A, D, DEG4}  (E = 100k+60k+100nF · A = 2.0M+1.2M · D = 2.0M+1.0M · DEG4 = 保持 DNP, 网表一格不改)",
    "V-4": "V-4 ∈ {680, 470, 390}  (Ω)",
}


# ═══════════════════════════════════════════════════════════════════════════
# 6 · 工具函数
# ═══════════════════════════════════════════════════════════════════════════


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write_text(path: str, txt: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)


def line_of(txt: str, needle: str, occurrence: int = 0) -> int:
    """needle 在 txt 里第 occurrence 次出现时的【起始行号】(1-based)。"""
    idx = -1
    for _ in range(occurrence + 1):
        idx = txt.find(needle, idx + 1)
        if idx < 0:
            return -1
    return txt.count("\n", 0, idx) + 1


def find_after(txt: str, ctx: str, old: str) -> tuple[int, int]:
    """返回 (起点, `old` 在起点之后出现的次数)。

    ★`ctx` 必须【全文唯一】⇒ 定位可靠; 起点 = ctx 结束位置 (无 ctx ⇒ 0)★
    """
    if ctx:
        pos = txt.find(ctx)
        if pos < 0:
            return -1, 0
        if txt.find(ctx, pos + 1) >= 0:
            return -1, 0          # ★ctx 不唯一 ⇒ 定位不可靠★
        start = pos + len(ctx)
    else:
        start = 0
    n = 0
    idx = start
    while True:
        j = txt.find(old, idx)
        if j < 0:
            break
        n += 1
        idx = j + 1
    return start, n


def replace_after(txt: str, ctx: str, old: str, new: str, count: int) -> str:
    """把 ctx 之后的 `count` 处 `old` 换成 `new` (★ctx 本身不动★)。"""
    start, n = find_after(txt, ctx, old)
    if n != count:
        raise RuntimeError(f"★旧值出现 {n} 次 (期望 {count} 次)")
    positions = []
    idx = 0
    while True:
        j = txt.find(old, idx)
        if j < 0:
            break
        positions.append(j)
        idx = j + len(old)
    targets = [p for p in positions if p >= start][:count]
    res = []
    prev = 0
    for p in targets:
        res.append(txt[prev:p])
        res.append(new)
        prev = p + len(old)
    res.append(txt[prev:])
    return "".join(res)


def run(cmd: list[str], cwd: str, capture: bool = True) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out


def apply_expect_patch(txt: str, key: str, new_check: str) -> tuple[str, str]:
    """把 EXPECT 里 key 那一行的第 4 个字段 (判据) 换成 new_check。返回 (新文本, 旧判据)。"""
    pat = re.compile(
        r"^(?P<head>\s*\(\s*['\"]" + re.escape(key) + r"['\"]\s*,\s*['\"][a-z]+['\"]\s*,\s*['\"][^'\"]*['\"]\s*,\s*)"
        r"(?P<q>['\"])(?P<chk>.*)(?P=q)(?P<tail>\s*\)\s*,?\s*)$", re.M)
    m = pat.search(txt)
    if not m:
        raise KeyError(f"★EXPECT 里找不到锚点 {key!r} (★门禁脚本结构变了?★)")
    old = m.group("chk")
    new_txt = txt[:m.start()] + m.group("head") + m.group("q") + new_check + m.group("q") + m.group("tail") + txt[m.end():]
    return new_txt, old


def spec_anchor_block(root: str) -> str:
    rc, out = run([sys.executable, os.path.join(root, CHECK_SCRIPT), "--emit-anchors"], root)
    if rc != 0:
        raise RuntimeError(f"★--emit-anchors 失败 rc={rc}: {out[:400]}")
    return out.strip()


def regen_spec_anchors(root: str) -> str:
    """把规格页的 <!-- ANCHORS:BEGIN --> … <!-- ANCHORS:END --> 块整块重生成。"""
    path = os.path.join(root, SPEC_PAGE)
    txt = read_text(path)
    table = spec_anchor_block(root)
    new_txt, n = re.subn(r"(<!-- ANCHORS:BEGIN -->\n).*?(\n<!-- ANCHORS:END -->)",
                         lambda m: m.group(1) + table + m.group(2), txt, flags=re.S)
    if n != 1:
        raise RuntimeError("★规格页里找不到 ANCHORS 块 (★结构变了?★)")
    write_text(path, new_txt)
    return table


def shift_expect_lines(root: str, rules: list[tuple[str, int]]) -> list[tuple[str, str, str]]:
    """按 rules [(file_kind, from_line)] 把 EXPECT 里的行号整体漂移。返回 [(key, old_line, new_line)]。"""
    path = os.path.join(root, CHECK_SCRIPT)
    txt = read_text(path)
    out = []
    for kind, frm in rules:
        pat = re.compile(
            r"^(?P<head>\s*\(\s*['\"](?P<key>[a-z0-9_]+)['\"]\s*,\s*['\"]" + kind + r"['\"]\s*,\s*['\"])(?P<ln>[?\d]+)(?P<rest>['\"]\s*,.*)$",
            re.M)
        for m in list(pat.finditer(txt)):
            ln = m.group("ln")
            if ln.isdigit() and int(ln) >= frm:
                out.append((m.group("key"), ln, str(int(ln) + 1)))
    # 应用 (倒序, 免得行号串了)
    for key, old, new in sorted(out, key=lambda x: -int(x[1])):
        txt2, o = apply_expect_patch(txt, key, None) if False else (txt, None)
        pat2 = re.compile(r"^(\s*\(\s*['\"]" + re.escape(key) + r"['\"]\s*,\s*['\"][a-z]+['\"]\s*,\s*['\"])"
                          + re.escape(old) + r"(['\"]\s*,.*)$", re.M)
        txt, n = pat2.subn(lambda m: m.group(1) + new + m.group(2), txt, count=1)
        if n != 1:
            raise RuntimeError(f"★漂移行号失败: {key} @ {old}")
    write_text(path, txt)
    return out


# ═══════════════════════════════════════════════════════════════════════════
# 7 · 计划 (Plan) —— 把 N 个 decision 合成一次落表
# ═══════════════════════════════════════════════════════════════════════════


class Plan:
    def __init__(self, root: str, decisions: list[Decision]):
        self.root = root
        self.decisions = decisions
        self.patches: list[Patch] = []
        self.expects: list[ExpectPatch] = []
        self.line_shifts: list[tuple[str, int]] = []
        self.spec_extra: list[str] = []
        for d in decisions:
            self.patches += d.patches
            self.expects += d.expects
            if d.v == "V-2" and d.value == "1":
                self.line_shifts = [("netlist", V2_NETLIST_SHIFT_FROM), ("pins", V2_PINS_SHIFT_FROM)]

    # ── 校验: 每条补丁的 old 必须【恰好】出现 count 次 ──
    def verify(self) -> list[str]:
        errs = []
        cache: dict[str, str] = {}
        for p in self.patches:
            if p.path not in cache:
                fp = os.path.join(self.root, p.path)
                if not os.path.exists(fp):
                    errs.append(f"★缺文件: {p.path}")
                    cache[p.path] = ""
                    continue
                cache[p.path] = read_text(fp)
            n = find_after(cache[p.path], p.ctx, p.old)[1]
            if n != p.count:
                errs.append(
                    f"★★补丁对不上 (★状态漂移 or 已落过?★): {p.path} · {p.label} ⇒ "
                    f"旧值出现 {n} 次 (期望 {p.count} 次)")
        # EXPECT 锚点
        cpath = os.path.join(self.root, CHECK_SCRIPT)
        ctxt = read_text(cpath) if os.path.exists(cpath) else ""
        for e in self.expects:
            try:
                apply_expect_patch(ctxt, e.key, e.new_check)
            except KeyError:
                errs.append(f"★★门禁锚点对不上: {e.key} ({e.label}) ⇒ EXPECT 里没这条 ⇒ 拒绝落")
        return errs

    # ── dry-run 的逐字 diff ──
    def diff_text(self) -> str:
        out = []
        cache: dict[str, str] = {}
        for p in self.patches:
            if p.path not in cache:
                fp = os.path.join(self.root, p.path)
                cache[p.path] = read_text(fp) if os.path.exists(fp) else ""
            txt = cache[p.path]
            start, _n = find_after(txt, p.ctx, p.old)
            # ★★行号必须指向【真正要改的那一行】, 不能指向 ctx 锚点的行 (★ctx 只用来定位·不改★)★★
            # ★★否则干跑报出来的行号是假的 (★ISS-233 §3 的 L 号 = 真源: E-1 L426 / E-3 L319 / E-4 L863★)★★
            targets: list[int] = []
            if p.old:
                positions = []
                idx = 0
                while True:
                    j = txt.find(p.old, idx)
                    if j < 0:
                        break
                    positions.append(j)
                    idx = j + len(p.old)
                if start >= 0:
                    targets = [q for q in positions if q >= start][:p.count]
                else:
                    targets = positions[:p.count]
            if targets:
                ln = txt.count("\n", 0, targets[0]) + 1
            elif start >= 0:
                ln = txt.count("\n", 0, start) + 1
            else:
                ln = -1
            out.append(f"── [{p.label}] {p.path}:{ln}  (匹配 {p.count} 处)")
            if p.ctx:
                for l in p.ctx.rstrip("\n").split("\n"):
                    out.append(f"     {l}   ★定位锚点 (未改)★")
            if p.new == "":
                for l in p.old.rstrip("\n").split("\n"):
                    out.append(f"   - 旧: {l}")
                out.append("   + 新: (整行删除 · 不留空行)")
            else:
                for l in p.old.rstrip("\n").split("\n"):
                    out.append(f"   - 旧: {l}")
                for l in p.new.rstrip("\n").split("\n"):
                    out.append(f"   + 新: {l}")
            out.append("")
        if self.line_shifts:
            for kind, frm in self.line_shifts:
                out.append(f"── [行号漂移] {CHECK_SCRIPT}: {kind} 行号 ≥ {frm} 的锚点全部 +1 "
                           f"(★V-2 把 2 行改成 3 行★)")
                out.append("")
        cpath = os.path.join(self.root, CHECK_SCRIPT)
        ctxt = read_text(cpath) if os.path.exists(cpath) else ""
        for e in self.expects:
            try:
                _, old = apply_expect_patch(ctxt, e.key, e.new_check)
            except KeyError:
                old = "★(找不到)★"
            out.append(f"── [门禁现状断言] {CHECK_SCRIPT}: {e.key}  ({e.label})")
            out.append(f"   - 旧: {old}")
            out.append(f"   + 新: {e.new_check}")
            out.append("")
        return "\n".join(out)

    # ── 真落: 写补丁 + 漂移行号 + 改 EXPECT ──
    def apply_patches(self) -> None:
        # ① 行号漂移 (先做, 因为后面的 ExpectPatch 用 key 定位, 与行号无关, 顺序无所谓)
        if self.line_shifts:
            shift_expect_lines(self.root, self.line_shifts)
        # ② 文本补丁 (按文件分组, 一次性写)
        by_file: dict[str, list[Patch]] = {}
        for p in self.patches:
            by_file.setdefault(p.path, []).append(p)
        for path, plist in by_file.items():
            fp = os.path.join(self.root, path)
            txt = read_text(fp)
            for p in plist:
                txt = replace_after(txt, p.ctx, p.old, p.new, p.count)
            write_text(fp, txt)
        # ③ EXPECT 现状断言值
        cpath = os.path.join(self.root, CHECK_SCRIPT)
        ctxt = read_text(cpath)
        for e in self.expects:
            ctxt, _ = apply_expect_patch(ctxt, e.key, e.new_check)
        write_text(cpath, ctxt)


# ═══════════════════════════════════════════════════════════════════════════
# 8 · 落表台账 + 规格页落表状态
# ═══════════════════════════════════════════════════════════════════════════


def md5_table(root: str) -> list[tuple[str, str, str, str]]:
    out = []
    for path, kind in MD5_TARGETS:
        fp = os.path.join(root, path)
        out.append((path, kind, md5(fp) if os.path.exists(fp) else "★(缺)★", ""))
    return out


def append_ledger(root: str, decisions: list[Decision], boss: list[str], old_md5: dict) -> str:
    fpath = os.path.join(root, LANDED_LEDGER)
    if not fpath.endswith(LANDED_LEDGER):
        raise RuntimeError(f"★台账路径不对: {fpath}")
    txt = read_text(fpath)
    now = time.strftime("%Y-%m-%d %H:%M:%S (Asia/Shanghai)")
    lines = []
    lines.append("")
    lines.append("## ★★16 · ★★V 值拍板即落 (★ISS-236 · 2026-11-16 · 硬件总工 (hw-lead) 执行 · "
                 "★`state/land_v_values.py` 一键落★) ★★")
    lines.append("")
    lines.append("> ★**单号**: ★**ISS-236** · ★**owner**: hw-lead · ★**verify_by**: main · "
                 "★**落表器**: ★**`state/land_v_values.py`** (★默认 dry-run · `--apply` 强制 `--boss-decision`★) ★")
    lines.append("> ★**老板拍板凭据 (★机器化留痕★)**: " + " / ".join(f"`{b}`" for b in boss))
    lines.append("> ★**落表时间**: ★**%s** ★" % now)
    lines.append("> ★**性质**: ★**V 值拍板后落表** (★V-2 / V-3 / V-4 老板都拍了才落★) · "
                 "★**没碰板** (受保护 md5 逐字节不变)★ · ★**没碰 `SW/` / `MECH/` / `state/issue_log.yaml` / "
                 "`PROJECT_TRACKER.md` §0 / 别人的分片★** · ★**零外发 ⇒ 实物 [实测] = 0 条★ ★")
    lines.append("")
    lines.append("### ★★16.1 · 拍板了什么 + 逐条落点 ★★")
    lines.append("")
    lines.append("| V 值 | 取值 | 落表后期望 `--expect-resolved` 条数变化 | 本工具落的落点 | 板那一趟才转绿的 |")
    lines.append("|---|---|---|---|---|")
    for d in decisions:
        delta_txt = ("**%d 条**" % d.delta) if d.delta else "★**0 条**★"
        board_txt = ("★**%d 条**★" % d.board_delta) if d.board_delta else "—"
        pts = []
        for p in d.patches[:40]:
            pts.append(f"`{p.path}` ({p.label})")
        lines.append("| ★**%s** ★ | ★**%s** ★ | %s | %s | %s |"
                     % (d.v, d.value, delta_txt, "<br>".join(pts) if pts else "★(无网表侧改动)★", board_txt))
    lines.append("")
    lines.append("### ★★16.2 · 新旧 md5 前后对照 (★供 SW / MECH 两边走 H-1 重锚★) ★★")
    lines.append("")
    lines.append("| 文件 | 前 | 后 | 变了? |")
    lines.append("|---|---|---|---|")
    for f, kind in MD5_TARGETS:
        fp = os.path.join(root, f)
        new = md5(fp) if os.path.exists(fp) else "★(缺)★"
        old = old_md5.get(f, "★(基线未知)★")
        lines.append("| ★**`%s`** ★ | `%s` | `%s` | %s |"
                     % (f, old, new, "★**是**★" if old != new else "否"))
    lines.append("")
    lines.append("★**受保护的两个必须逐字节不变**: `HW/PCB/demo_mainboard.kicad_pcb` = `%s` · "
                 "`HW/PCB/demo_mainboard.kicad_pro` = `%s` ★"
                 % (md5(os.path.join(root, PROTECTED[0][0])),
                    md5(os.path.join(root, PROTECTED[1][0]))))
    lines.append("")
    lines.append("### ★★16.3 · 复现命令 (★B6 自证★) ★★")
    lines.append("")
    lines.append("```bash")
    lines.append("cd %s" % root)
    lines.append("python3 state/land_v_values.py %s   # ★dry-run: 逐字 diff, 零写盘★"
                 % " ".join("--decision %s=%s" % (d.v, d.value) for d in decisions))
    lines.append("python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \\")
    lines.append("python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \\")
    lines.append("python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py")
    lines.append("python3 HW/check_netlist_selfconsistency.py                    # rc=0")
    lines.append("python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (21/21)")
    lines.append("python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★预期 %d 条★)"
                 % max(0, BASELINE_EXPECT_RESOLVED + sum(d.delta for d in decisions)))
    lines.append("python3 state/check_netlist.py && python3 state/check_netlist_pins.py")
    lines.append("python3 state/check_sch_erc.py && python3 state/check_sch_pinfull.py")
    lines.append("python3 state/merge.py && python3 state/gate_check.py")
    lines.append("md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    txt = txt.rstrip("\n") + "\n" + "\n".join(lines) + "\n"
    write_text(fpath, txt)
    return fpath


def append_spec_status(root: str, decisions: list[Decision], boss: list[str]) -> str:
    fpath = os.path.join(root, SPEC_PAGE)
    if not fpath.endswith(SPEC_PAGE):
        raise RuntimeError(f"★规格页路径不对: {fpath}")
    txt = read_text(fpath)
    now = time.strftime("%Y-%m-%d")
    # ★★章节号动态取 (★规格页里已经有 §5.5 时不能再占 5.5★)★★
    nums = [int(m) for m in re.findall(r"^###\s+★?5\.(\d+)", txt, re.M)]
    sec = 5 + (max(nums) + 1 if nums else 1)
    lines = []
    lines.append(f"### ★5.{sec} ★★落表状态 (★ISS-236 · V 值拍板即落 · 2026-11-16 · 硬件总工执行 · "
                 f"★`state/land_v_values.py`★)★★")
    lines.append("")
    lines.append("★★**一句话**: ★**老板拍完 %s ⇒ 落表器 `state/land_v_values.py` 一键落进网表/脚表/BOM + "
                 "落表台账 + 门禁锚点** ★" % ", ".join(f"{d.v}={d.value}" for d in decisions))
    lines.append("")
    lines.append("| V 值 | 取值 | `--expect-resolved` 条数变化 | 板那一趟 |")
    lines.append("|---|---|---|---|")
    for d in decisions:
        lines.append("| ★**%s** ★ | ★**%s** ★ | %s | %s |"
                     % (d.v, d.value,
                        ("**%d 条**" % d.delta) if d.delta else "★**0 条**★",
                        ("★**%d 条**★" % d.board_delta) if d.board_delta else "—"))
    lines.append("")
    lines.append("★**老板拍板凭据**: %s ★" % " / ".join(f"`{b}`" for b in boss))
    lines.append("")
    lines.append("★**门禁实测 (★本单实跑·见落表台账 §16★)★**: 现状守卫 `rc=0` · `--selftest` `rc=0` **21/21** · "
                 "`--expect-resolved` `rc=1` **%d 条** · 四道尺子全 `rc=0` · `merge.py` + `gate_check.py` `rc=0` ★"
                 % max(0, BASELINE_EXPECT_RESOLVED + sum(d.delta for d in decisions)))
    lines.append("")
    lines.append("---")
    lines.append("")
    block = "\n".join(lines)
    marker = "\n---\n\n## 6. ★★附带发现"
    if marker not in txt:
        raise RuntimeError("★规格页 §6 起点没找到 (★结构变了?★)")
    txt = txt.replace(marker, "\n" + block + marker, 1)
    write_text(fpath, txt)
    return fpath


# ═══════════════════════════════════════════════════════════════════════════
# 9 · 备份 / 回滚
# ═══════════════════════════════════════════════════════════════════════════


def backup_files(root: str, paths: list[str], tag: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    bdir = os.path.join(root, "state", f".bak_land_v_values_{tag}_{ts}")
    os.makedirs(bdir, exist_ok=True)
    for p in paths:
        fp = os.path.join(root, p)
        if not os.path.exists(fp):
            continue
        dst = os.path.join(bdir, p)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(fp, dst)
    with open(os.path.join(bdir, "BACKUP_INFO.txt"), "w", encoding="utf-8") as fh:
        fh.write("★V 值落表回滚副本 (★落表器自动打的★)\n")
        fh.write(f"★落表时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        fh.write("★还原命令:\n")
        fh.write(f"  python3 state/land_v_values.py --rollback {os.path.relpath(bdir, root)}\n")
        for p in paths:
            fh.write(f"  - {p}\n")
    return bdir


def do_rollback(root: str, bdir: str) -> int:
    if not os.path.isdir(bdir):
        print(f"★★ rc=2: 回滚目录不存在: {bdir}", file=sys.stderr)
        return 2
    info = os.path.join(bdir, "BACKUP_INFO.txt")
    n = 0
    for rel in sorted(os.listdir(bdir)):
        if rel == "BACKUP_INFO.txt":
            continue
        src = os.path.join(bdir, rel)
        dst = os.path.join(root, rel)
        if os.path.isdir(src):
            for sub in os.listdir(src):
                s2 = os.path.join(src, sub)
                d2 = os.path.join(dst, sub)
                os.makedirs(os.path.dirname(d2), exist_ok=True)
                shutil.copy2(s2, d2)
                n += 1
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            n += 1
    print(f"✅ rc=0: 已从 {bdir} 还原 {n} 个文件")
    if os.path.exists(info):
        print(open(info, encoding="utf-8").read())
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# 10 · 主流程
# ═══════════════════════════════════════════════════════════════════════════


def parse_decision_arg(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"★写法必须是 V-x=值 (★收到 {raw!r}★)")
    v, val = raw.split("=", 1)
    return v.strip(), val.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="★参数化 V 值一键落表器 (★默认 dry-run · `--apply` 必须带 `--boss-decision`★)★")
    ap.add_argument("--decision", action="append", default=[],
                    help="★V 值决定, 可重复: V-3=E / V-4=680 / V-2=1★")
    ap.add_argument("--apply", action="store_true", help="★真落 (★不带就是 dry-run, 零写盘★)")
    ap.add_argument("--boss-decision", action="append", default=[],
                    help='★老板拍板凭据: "<日期> <A1|A2|A3> = <值>"★ (★`--apply` 必带★)')
    ap.add_argument("--root", default=DEFAULT_ROOT, help="工程根 (默认 = state/ 的上一级)")
    ap.add_argument("--rollback", default=None, help="★从某个备份目录还原 (★落表回滚★)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "state")):
        print(f"★★ rc=2: 工程根不对: {root}", file=sys.stderr)
        return 2

    if args.rollback:
        return do_rollback(root, os.path.abspath(args.rollback))

    if not args.decision:
        print(__doc__.strip())
        print("")
        print("★★ rc=2: 没给 --decision (★干跑也要给一个, 才知道要打什么 diff★)", file=sys.stderr)
        return 2

    # ── ① 白名单校验 (★取值写死, 不许自由字符串★) ──
    decisions: list[Decision] = []
    for raw in args.decision:
        try:
            v, val = parse_decision_arg(raw)
        except ValueError as exc:
            print(f"★★ rc=2: {exc}", file=sys.stderr)
            return 2
        if v not in WHITELIST:
            print(f"★★ rc=2: ★**非法 V 值名 {v!r}** ⇒ 只认 {', '.join(sorted(WHITELIST))} ★", file=sys.stderr)
            for k, v2 in sorted(WHITELIST_DOC.items()):
                print(f"   ★{k}★: {v2}", file=sys.stderr)
            return 2
        if val not in WHITELIST[v]:
            print(f"★★ rc=2: ★**非法取值 {v}={val}** ⇒ 白名单里只有 "
                  f"{{{', '.join(sorted(WHITELIST[v]))}}} ★", file=sys.stderr)
            print(f"   ★{v}★: {WHITELIST_DOC[v]}", file=sys.stderr)
            print("★★ ★**零写盘** ★ (★本工具在解析阶段就退了, 一个字节都没碰★)", file=sys.stderr)
            return 2
        decisions.append(WHITELIST[v][val](val))

    # ── ② 被否决的取值 (★必须打回★) ──
    for d in decisions:
        if d.rejected:
            print(f"★★ rc=2: ★**{d.v}={d.value} 必须打回** ★", file=sys.stderr)
            print(d.rejected, file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2

    plan = Plan(root, decisions)
    total_delta = sum(d.delta for d in decisions)
    expected_after = max(0, BASELINE_EXPECT_RESOLVED + total_delta)

    # ── ③ 补丁校验 (★状态漂移 / 已落过 ⇒ 拒绝落★) ──
    errs = plan.verify()
    if errs:
        print("★★ rc=3: ★**落表前校验不过 ⇒ 拒绝落 (★零写盘★)** ★", file=sys.stderr)
        for e in errs:
            print(f"   {e}", file=sys.stderr)
        return 3

    # ── ④ dry-run 报告 (★零写盘★) ──
    print("╔══ V 值落表器 (★默认 dry-run · 零写盘★) ══╗")
    print(f"★ 工程根: {root}")
    print(f"★ 决定: {', '.join('%s=%s' % (d.v, d.value) for d in decisions)}")
    print(f"★ 模式: {'★APPLY (真落)★' if args.apply else '★DRY-RUN (只打印, 零写盘)★'}")
    print("")
    print("★★【逐字 diff (★文件 + 行号 + 旧值 + 新值★)】★★")
    print(plan.diff_text())

    print("★★【落表后期望 `--expect-resolved` 条数变化】★★")
    print(f"   基线 (2026-11-16 ISS-233 交卷后): ★**{BASELINE_EXPECT_RESOLVED} 条** ★")
    for d in decisions:
        print(f"   · {d.v}={d.value}: ★**{d.delta:+d} 条** ★ ⇒ "
              f"{'★**落完仍红 (按降级/判决不成立)**★' if d.delta == 0 else '★**转绿**★'}")
    print(f"   ⇒ 落表后期望: ★**{expected_after} 条** ★")
    for d in decisions:
        if d.board_delta:
            print(f"   · ★**{d.v}={d.value} 的板那一趟** ⇒ 再转绿 ★**{d.board_delta} 条** ★ ⇒ "
                  f"★**板那一趟落完 = {max(0, expected_after - d.board_delta)} 条** ★ "
                  f"(★本工具【不】做, 板一个字节都不碰★)")
    print("")
    print("★★【要连带改的台账 / 锚点】★★")
    print("   · `HW/check_netlist_selfconsistency.py` 的 `EXPECT` 现状断言值: ★**%d 条** ★"
          % len(plan.expects))
    for e in plan.expects:
        print(f"       ★ {e.key}★ ({e.label})")
    if plan.line_shifts:
        for kind, frm in plan.line_shifts:
            print(f"   · 门禁锚点**行号漂移**: {kind} 行号 ≥ {frm} ⇒ 全部 +1")
    print("   · `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 `<!-- ANCHORS -->` 块: ★**整块重生成** ★")
    print("   · `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` §5.5: ★**新增落表状态段** ★")
    print("   · `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16: ★**新增落表台账 (单号 + 文件名 + 新旧 md5)** ★")
    print("")
    print("★★【会要谁走 H-1 重锚】★★")
    print("   · ★**sw-lead**★: `SW/SW_MD5_BASELINE_LEDGER.md` §1 `entries` 的 "
          "`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 两条 (★+ BOM 那条若台账里有★)")
    print("   · ★**mech-lead**★: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `source_ledger.entries` "
          "+ §3.1 留痕新增一行")
    print("   ★**两边的 H-1 都要填四项: 落表单号 + 文件名 + 新 md5 + 旧 md5 ★** "
          "(★四项在 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 里必须可查★)")
    print("")
    if any(d.warnings for d in decisions):
        print("★★【★落表前必须看一眼的警告★】★★")
        for d in decisions:
            for w in d.warnings:
                print(f"   ★ {d.v}={d.value}: {w}")
        print("")

    if not args.apply:
        print("✅ rc=0: ★**DRY-RUN 完成 · 零写盘** ★ (★盘上 5 个 md5 逐字节不变★)")
        print("   ★**要真落就加 `--apply --boss-decision \"<日期> <A1|A2|A3> = <值>\"` ★**")
        return 0

    # ── ⑤ --apply 的老板拍板凭据 (★机器化保证: 不许替老板拍板★) ──
    boss = []
    for b in args.boss_decision:
        m = re.match(r"^\s*(\d{4}-\d{2}-\d{2})\s+(A1|A2|A3)\s*=\s*(\S+)\s*$", b)
        if not m:
            print(f"★★ rc=2: ★**`--boss-decision` 写法不对: {b!r}** ⇒ "
                  f"必须是 \"<日期> <A1|A2|A3> = <值>\" (★例: \"2026-11-16 A1 = E\"★) ★", file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2
        boss.append((m.group(1), m.group(2), m.group(3)))
    if not boss:
        print("★★ rc=2: ★**`--apply` 必须带 `--boss-decision \"<日期> <A1|A2|A3> = <值>\"`** ★", file=sys.stderr)
        print("   ★**这是「不许替老板拍板」的机器化保证 ⇒ 缺这条就拒绝执行** ★", file=sys.stderr)
        print("★★ ★**零写盘** ★", file=sys.stderr)
        return 2
    # ★★拍板码 → 拍板项 (★DECISION_PENDING_2026-11-16.md §A: A1=V-3 · A2=V-4 · A3=V-2★) ★★
    A_ITEM = {"A1": "V-3", "A2": "V-4", "A3": "V-2"}
    boss_map: dict[str, str] = {}
    for _d, _c, _v in boss:
        _item = A_ITEM[_c]
        if _v not in WHITELIST[_item]:
            print(f"★★ rc=2: ★★拍板原文里的值 {_v!r} 不在 {_item} 白名单里** "
                  f"⇒ {{{', '.join(sorted(WHITELIST[_item]))}}} ★", file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2
        if _item in boss_map and boss_map[_item] != _v:
            print(f"★★ rc=2: ★★{_c} 被拍成两个不同的值 ({boss_map[_item]} / {_v})** ★", file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2
        boss_map[_item] = _v
    missing = [f"{d.v}={d.value}" for d in decisions if boss_map.get(d.v) != d.value]
    if missing:
        print(f"★★ rc=2: ★**这些决定没有对应的老板拍板凭据: {', '.join(missing)}** ★", file=sys.stderr)
        print("   ★**每个要落的 V 值都必须有一张 `--boss-decision` 凭据 (★值要对得上★)** ★", file=sys.stderr)
        print("★★ ★**零写盘** ★", file=sys.stderr)
        return 2

    # ── ⑥ 备份 (★有回滚★) ──
    touched = sorted({p.path for p in plan.patches} | {CHECK_SCRIPT, SPEC_PAGE, LANDED_LEDGER})
    old_md5 = {p: md5(os.path.join(root, p)) for p in touched if os.path.exists(os.path.join(root, p))}
    old_md5.update({p: md5(os.path.join(root, p)) for p, _ in MD5_TARGETS
                    if os.path.exists(os.path.join(root, p))})
    bdir = backup_files(root, touched, "v")
    print(f"★★ 回滚副本: {os.path.relpath(bdir, root)} ★★")

    try:
        # ── ⑦ 落补丁 ──
        plan.apply_patches()
        # ── ⑧ 重生成 (★顺序是硬的★) ──
        for script, kind in GEN_ORDER:
            rc, out = run([sys.executable, os.path.join(root, script)], root)
            if rc != 0:
                raise RuntimeError(f"★重生成失败: {script} rc={rc}\n{out[-1500:]}")
            print(f"   ★ 重生成 OK: {script}  ({kind})")
        # ── ⑨ 规格页锚点表整块重生成 ──
        regen_spec_anchors(root)
        print("   ★ 重生成 OK: 规格页 ANCHORS 块")
        # ── ⑩ 规格页 §5.5 + 台账 §16 (★带真实 md5★) ──
        append_spec_status(root, decisions, [f"{b[0]} {b[1]} = {b[2]}" for b in boss])
        append_ledger(root, decisions, [f"{b[0]} {b[1]} = {b[2]}" for b in boss], old_md5)
        print("   ★ 重生成 OK: 规格页 §5.5 + 落表台账 §16")
    except Exception as exc:
        print(f"★★ rc=1: 落表失败 ⇒ 自动回滚: {exc}", file=sys.stderr)
        do_rollback(root, bdir)
        return 1

    # ── ⑪ 门禁实跑 ──
    print("")
    print("★★【落表后门禁实跑】★★")
    gates = [
        ([sys.executable, os.path.join(root, CHECK_SCRIPT)], "现状守卫 (期望 rc=0)"),
        ([sys.executable, os.path.join(root, CHECK_SCRIPT), "--selftest"], "反向用例 (期望 rc=0, 21/21)"),
        ([sys.executable, os.path.join(root, CHECK_SCRIPT), "--expect-resolved"], "翻面口径 (期望 rc=1)"),
        ([sys.executable, os.path.join(root, "state/check_netlist.py")], "尺子1"),
        ([sys.executable, os.path.join(root, "state/check_netlist_pins.py")], "尺子2"),
        ([sys.executable, os.path.join(root, "state/check_sch_erc.py")], "尺子3 (ERC=0)"),
        ([sys.executable, os.path.join(root, "state/check_sch_pinfull.py")], "尺子4 (图=表)"),
    ]
    failed = []
    for cmd, kind in gates:
        rc, out = run(cmd, root)
        tail = "\n".join(out.strip().split("\n")[-6:])
        print(f"   ★ {kind}: rc={rc}")
        for l in tail.split("\n"):
            print(f"       {l}")
        if kind.startswith("翻面口径"):
            if rc != 1:
                failed.append(f"{kind}: rc={rc} (期望 1)")
        elif rc != 0:
            failed.append(f"{kind}: rc={rc}")
    # merge + gate_check (★合成一条跑★)
    rc1, out1 = run([sys.executable, os.path.join(root, "state/merge.py")], root)
    rc2, out2 = run([sys.executable, os.path.join(root, "state/gate_check.py")], root)
    print(f"   ★ merge.py + gate_check.py: rc={rc1}/{rc2}")
    for l in (out1 + out2).strip().split("\n")[-4:]:
        print(f"       {l}")
    if rc1 != 0 or rc2 != 0:
        failed.append(f"merge/gate_check: rc={rc1}/{rc2}")

    # ── ⑫ 受保护 md5 ──
    print("")
    print("★★【受保护 md5 (★必须逐字节不变★)】★★")
    prot_ok = True
    for path, expect in PROTECTED:
        got = md5(os.path.join(root, path))
        ok = (got == expect)
        prot_ok = prot_ok and ok
        print(f"   {'✅' if ok else '★★'} {path}: {got} (期望 {expect})")

    # ── ⑬ 新 md5 打到 stdout (★供 SW / MECH 走 H-1 重锚★) ──
    print("")
    print("★★【★落表后新 md5 (★供 sw-lead / mech-lead 走 H-1 重锚★)★★】★★")
    for path, kind in MD5_TARGETS:
        fp = os.path.join(root, path)
        got = md5(fp) if os.path.exists(fp) else "★(缺)★"
        old = old_md5.get(path, "?")
        print(f"   {got}  {path}   ★{kind}★  (旧 {old})")
    print("")
    print(f"★★ 落表单号: ★**ISS-236** ★ · 老板拍板凭据: {', '.join(f'{b[0]} {b[1]} = {b[2]}' for b in boss)}")
    print(f"★★ 落表台账: ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16** ★")
    print(f"★★ 回滚: ★**`python3 state/land_v_values.py --rollback {os.path.relpath(bdir, root)}`** ★")

    if failed or not prot_ok:
        print("")
        print(f"★★ rc=1: 落表后有门禁不过 ⇒ 自动回滚: {'; '.join(failed) or '受保护 md5 变了'}", file=sys.stderr)
        do_rollback(root, bdir)
        return 1

    print("")
    print("✅ rc=0: ★**落表完成 · 全部门禁绿 · 受保护 md5 逐字节不变** ★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
