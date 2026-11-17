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
    # ★落表器自测 (★11 条反向用例 · 全在临时副本里做 · 真盘零写入★)
    python3 state/land_v_values.py --selftest
    # ★V-2 的两轴 (★架构 A3/W-1 + 型号 选型级★) ⇒ 不给就按真源现状走
    python3 state/land_v_values.py --decision V-2=1 --v2-arch 2 --v2-model "TPD2EUSB30 (...)"
    # 回滚 (把某次落表整个还原)
    python3 state/land_v_values.py --rollback state/.bak_land_v_values_20261116-120000

★★**ISS-260 (2026-11-16) 的 V-2 重写 (★hw-lead★)**★★
  ★**V-2 的配方改成【读当前真源】**: 定位靠【位号 + 网名】(★`add(..., "D_ESD_USB_D", ...)`★),
  ★**不再靠 value 串匹配** ⇒ ★**ISS-257 把真源换成真型号之后, 本工具不会再漂** ★
  ★**两轴彻底分开**:
    · ★**架构轴** (2脚单通道 / 3脚双通道 / 2脚双向) ⇒ ★**归 A3 / W-1 裁** ⇒
      ★**本工具【不】替老板选架构** ⇒ 默认按【真源现状】走; 换架构必须显式
      `--v2-arch` + `--v2-model` + `--v2-evidence` (★`--boss-decision` 也必须同时覆盖两轴★) ★
    · ★**型号轴** (真 OPN) ⇒ ★**本工具一个字都不许改** ⇒ 真源现值原样保住;
      ★**现值是占位/判据串 ⇒ 拒绝落** (★型号归选型级 / 老板★) ⇒
      ★**绝不许把 ISS-257 已落的真型号降级成一句判据串** ★
  ★**落表动作 = 只挪网 (USB_D_P_SRC → NET_USB_D_P_TYPEC)** ⇒ ★**行数不变 ⇒ 门禁锚点行号不漂移** ★
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
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
# ★★ISS-283 · B1: 落表授权通道要用的两个文件 (★身份列从 registry 取·值从网表行取★)★★
NETLIST_CSV = "HW/netlist_v1.csv"
REGISTRY_JSON = "HW/land_row_anchors_registry.json"
# ★★ISS-283 · B1: 行号锚点守卫 (★落表前先让它把台账的 `id_str` 补齐·不然合法落表走不通★)★★
ANCHOR_GUARD = "HW/check_land_row_anchors.py"

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
    errors: list = field(default_factory=list)     # ★非空 = 落表前校验不过 (rc=3 · 零写盘)★
    v2_readout: list = field(default_factory=list)  # ★V-2 的真源读数 (★架构 / 型号两轴★)★
    v2_arch: str = ""       # ★本次落表实际用的架构档 (★1/2/3★)★
    v2_model: str = ""      # ★本次落表实际用的型号串★
    v2_src_arch: str = ""    # ★真源现状的架构档★
    v2_src_model: str = ""   # ★真源现状的型号串★
    line_shift_extra: list = field(default_factory=list)  # ★额外的行号漂移 (★只有架构 ② 用得到★)★
    auth_changes: list = field(default_factory=list)  # ★ISS-283 · B1: 身份变更授权记录 (★落表台账里要登记★)★


# ═════════════════════════════════════════════════════════════════════════════
# 1-B · 「已落过」判定 (★ISS-283 · ⑩: V-3 / V-4 也要有·不然重复落会崩★)
# ═════════════════════════════════════════════════════════════════════════════
def _already_landed_evidence(root: str, patches: list) -> list[str]:
    """★「已落过」的机器证据 (★旧串 0 次 + 新串在场 ⇒ 这一格已经落过了·不是漂移★) ★

    ★**为什么要有它 (★今天的病灶★)**: 落表器自测的用例 12 硬套 V-3/V-4 的补丁,
      而这两个值【已经落过表了】⇒ 真盘里旧值出现 0 次 ⇒ `replace_after` 抛 RuntimeError ⇒ **崩** ★
    ⇒ ★**「合法落表」与「重复落表」是两件事, 不许混** ⇒ 这一格落过了 ⇒ 明确说【已落过】+ 拒绝重复落 ★
    """
    out: list[str] = []
    cache: dict[str, str] = {}
    for p in patches:
        fp = os.path.join(root, p.path)
        if not os.path.exists(fp):
            continue
        if p.path not in cache:
            cache[p.path] = read_text(fp)
        txt = cache[p.path]
        _s, n_old = find_after(txt, p.ctx, p.old)
        if n_old != 0:
            continue                      # ★旧串还在 ⇒ 没落过 (★真漂移由 verify() 报★)
        if not p.new:
            continue                      # ★删除型补丁 ⇒ 单凭「旧串没了」不足为证 ★
        _s2, n_new = find_after(txt, p.ctx, p.new)
        if n_new >= 1:
            out.append(f"{p.path} · {p.label} (★旧串 0 次 + 新串在场 {n_new} 次★)")
    return out


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


def v3_recipe(value: str, root: str = "", arch_req: str = "", model_req: str = "",
              ev_req: str = "") -> Decision:
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
    # ── ★ISS-283 · ⑩: 「已落过」判定 (★V-3 也要有·不然重复落 ⇒ 旧串 0 次 ⇒ 崩★) ──
    if root:
        _ev = _already_landed_evidence(root, d.patches)
        if _ev:
            d.errors.append(
                "★★【已落过】V-3=%s 这一格【已经落过表了】⇒ 拒绝重复落 (★零写盘★)★\n"
                "   ★**证据 (★旧串 0 次 + 新串在场 ⇒ 是「落过了」不是「漂移了」★)**:\n%s"
                % (value, "\n".join("     · " + e for e in _ev[:6])))
            return d

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


def v4_recipe(value: str, root: str = "", arch_req: str = "", model_req: str = "",
              ev_req: str = "") -> Decision:
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
    # ── ★ISS-283 · ⑩: 「已落过」判定 (★V-4 也要有·不然重复落 ⇒ 旧串 0 次 ⇒ 崩★) ──
    if root:
        _ev = _already_landed_evidence(root, d.patches)
        if _ev:
            d.errors.append(
                "★★【已落过】V-4=%s 这一格【已经落过表了】⇒ 拒绝重复落 (★零写盘★)★\n"
                "   ★**证据 (★旧串 0 次 + 新串在场 ⇒ 是「落过了」不是「漂移了」★)**:\n%s"
                % (value, "\n".join("     · " + e for e in _ev[:6])))
            return d

    return d


# ═══════════════════════════════════════════════════════════════════════════
# 4 · V-2 (ESD 落表) —★ISS-260 重写 (2026-11-16 · hw-lead)★
#
# ★★**为什么重写 (★实测, 不是推测★)**★★
#   ISS-236 的 V-2 配方把【改前原串】硬编码在工具里 (`V2_ESD_OLD`)。ISS-257 (21:22 已 verified)
#   把 `state/gen_netlist.py` 的 D_ESD_USB_D 那两行换成了【真型号】(TPD1E05U06DPYR · evidence [官方])
#   ⇒ ★**旧串在真源里出现 0 次** ⇒ `--decision V-2=1` 当场 rc=3 (★零写盘★) ⇒
#   ★**决策页 §A 承诺的「A1+A2+A3 一并拍 ⇒ 一条命令 ⇒ 15 条一次落」在 V-2 这一格当场失效** ★
#
# ★★**这一版的两轴分离 (★本版的核心★)**★★
#   ★**架构轴 (2脚单通道 / 3脚双通道 / 2脚双向)**: ★**归 A3 / W-1 裁** ⇒
#     ★**落表器【只】认【真源现状】(默认 = 现状架构) ⇒ 绝不替老板选架构** ★
#     ★**换架构必须显式 `--v2-arch=<arch>` + `--v2-model=<型号>` + `--v2-evidence=<等级>`** ★
#   ★**型号轴 (真 OPN)**: ★**本工具一个字都不许改** ⇒
#     ★**现状是占位/判据串 ⇒ 拒绝落 (★型号未落 ⇒ 归选型级 / 老板★)** ★
#     ★**绝不许把 ISS-257 已落的真型号降级成一句判据串** ★
#
# ★★**落表动作 (★与架构无关的那部分★)**★★
#   ★**把 D_ESD_USB_D 的信号行从 SoM 侧挪到 Type-C 侧** (★ISS-211 第(4)条: 不挪等于没护★)
#   ★**行数【不变】⇒ 门禁锚点的行号【不漂移】⇒ ISS-236 那套 +1 漂移机制整个不需要了** ★
# ═══════════════════════════════════════════════════════════════════════════

V2_REF = "D_ESD_USB_D"

# ★★SoM 侧网名 → Type-C 侧网名 (★挪网对照表★)★★
V2_NET_MOVE = {
    "USB_D_P_SRC": "NET_USB_D_P_TYPEC",
    "USB_D_N_SRC": "NET_USB_D_N_TYPEC",
}

# ★★架构档 (★只有这三个是老板 A3 / W-1 桌上的选项★)★★
V2_ARCHS = {
    "1": dict(
        shape="single2",
        title="① 2 脚单通道",
        desc="★一颗 2 脚件只护一条线 (D+ / 地) ★⇒ ★**D− 侧仍裸奔 (ISS-241 Q-A 明写的代价: USB 只护 D+)★** ★",
        cost="★**占位【焊盘数】不变 (2) ⇒ footprint 不换封装** ★ ⇒ ★**但占位间距 2.30mm ≠ DPY 0.65mm ⇒ 仍要按厂商 land 重画 (ISS-241 矩阵 §3.1 ③) ⇒ + 挪位置 (47.99mm → ≤3.0mm) + 板焊盘 net 同步改 (B-9)** ★",
    ),
    "2": dict(
        shape="dual3",
        title="② 3 脚双通道",
        desc="★一颗 3 脚件覆盖 D+ / D− / 地 (pin1=D+ / pin2=D− / pin3=GND) ★⇒ ★**D− 侧一起护上** ★",
        cost="★★**占位只有 2 焊盘 ⇒ 3 脚件物理落不下 ⇒ 必须先改 footprint (板那一趟 B-3) ⇒ 板 md5 要变**★★",
    ),
    "3": dict(
        shape="bidir2",
        title="③ 2 脚双向件",
        desc="★`PESD5V0S1BA` (SOD-323) pin1=K1 / pin2=K2 对称 ⇒ ★**天然免疫 pad 序接反** ★",
        cost="★★**SOD-323 官方 land 间距 ≠ 占位 2.30mm ⇒ 要重画 land ⇒ 仍是板那一趟**★★",
    ),
}

# ★★架构名 → 形态 (★从真源读出来的那一档★)★★
V2_SHAPE2ARCH = {"single2": "1", "dual3": "2", "bidir2": "3"}

# ★★网表行号漂移 (★只有架构 ② (2 行 → 3 行) 才用得上★)★★
# ★★L417 = D+ 行 (改写但行号不变) · ★**L418 = 新增的 D− 行** · ★**原 L418 (GND 行) 顺移到 L419** ★
V2_NETLIST_SHIFT_FROM = 418
# ★★脚表行号漂移 (★D_ESD_USB_D 从 2 脚变 3 脚 ⇒ 新 pin3 落在 L174 ⇒ 后面所有行 +1★)★★
V2_PINS_SHIFT_FROM = 174

# ★★型号像不像真 OPN (★第一个 token 必须含数字 ⇒ 「ESD 阵列 [待选型] …」这种占位串会被挡下★)★★
V2_OPN_RE = re.compile(r"^[A-Z][A-Z0-9\-]*[0-9][A-Z0-9\-]*\b")
# ★★占位/判据串的禁用词 (★真型号串里一个字都不该有★)★★
V2_PLACEHOLDER_MARKS = ("待选型", "阵列 [待", "ESD 阵列", "待裁", "TODO")


def _py_str(s: str) -> str:
    """去掉 Python 字符串字面量的外层引号。"""
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _split_call_args(body: str, base: int) -> tuple[list[str], list[tuple[int, int]]]:
    """把 `add(...)` 的实参切开。返回 (实参列表, 每个实参的 [起, 止) 偏移) ★偏移是绝对偏移★。"""
    args: list[str] = []
    spans: list[tuple[int, int]] = []
    seg_start = 0
    depth = 0
    quote = None
    i = 0
    n = len(body)
    while i < n:
        ch = body[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            i += 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            seg = body[seg_start:i]
            lead = len(seg) - len(seg.lstrip())
            core = seg.strip()
            args.append(core)
            spans.append((base + seg_start + lead, base + seg_start + lead + len(core)))
            seg_start = i + 1
            i += 1
            continue
        i += 1
    seg = body[seg_start:]
    lead = len(seg) - len(seg.lstrip())
    core = seg.strip()
    if core:
        args.append(core)
        spans.append((base + seg_start + lead, base + seg_start + lead + len(core)))
    return args, spans


def scan_add_calls(txt: str) -> list[dict]:
    """扫出 `state/gen_netlist.py` 里所有 `add(...)` 调用 (★只认行首的 add(★)★)。"""
    calls: list[dict] = []
    for m in re.finditer(r"(?m)^[ \t]*add\(", txt):
        open_i = txt.index("(", m.start())
        depth = 0
        j = open_i
        quote = None
        while j < len(txt):
            ch = txt[j]
            if quote:
                if ch == "\\":
                    j += 2
                    continue
                if ch == quote:
                    quote = None
                j += 1
                continue
            if ch in "\"'":
                quote = ch
                j += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            continue
        body = txt[open_i + 1:j]
        args, spans = _split_call_args(body, open_i + 1)
        calls.append({
            "off": m.start(), "end": j + 1, "raw": txt[m.start():j + 1],
            "args": args, "spans": spans,
            "line": txt.count("\n", 0, m.start()) + 1,
        })
    return calls


def v2_read_source(root: str) -> dict:
    """★从【当前真源】现读 D_ESD_USB_D 的现状 (★不靠任何硬编码的旧串★)★。"""
    ro = {"errors": [], "warnings": [], "rows": [], "arch": "", "model": "", "evidence": "",
          "opn": "", "opn_line": 0, "block": ""}
    path = os.path.join(root, GEN_NETLIST)
    if not os.path.exists(path):
        ro["errors"].append(f"★★缺文件: {GEN_NETLIST} ⇒ 拒绝落 ★")
        return ro
    txt = read_text(path)
    rows = []
    for c in scan_add_calls(txt):
        if len(c["args"]) < 12:
            continue
        if _py_str(c["args"][4]) != V2_REF:
            continue
        rows.append({
            "line": c["line"], "off": c["off"], "end": c["end"], "raw": c["raw"],
            "spans": c["spans"],
            "page": _py_str(c["args"][0]), "net": _py_str(c["args"][1]),
            "node1": _py_str(c["args"][2]), "node2": _py_str(c["args"][3]),
            "ref": _py_str(c["args"][4]), "value": _py_str(c["args"][5]),
            "typ": _py_str(c["args"][6]), "dnp": _py_str(c["args"][7]),
            "ev": _py_str(c["args"][8]), "tbd": _py_str(c["args"][9]),
            "note": _py_str(c["args"][10]), "cid": _py_str(c["args"][11]),
        })
    ro["rows"] = rows
    if not rows:
        ro["errors"].append(
            f"★★【状态漂移】{GEN_NETLIST} 里找不到 `{V2_REF}` 的 add(...) 行 ⇒ "
            f"★**期望: 至少 1 行 `add(..., \"{V2_REF}\", ...)`** ⇒ ★**实际: 0 行** ⇒ 拒绝落 ★")
        return ro

    # ── 架构判定 (★按行数 + GND 行数★) ──
    gnd_rows = [r for r in rows if r["net"] == "GND"]
    sig_rows = [r for r in rows if r["net"] != "GND"]
    if len(rows) == 2 and len(gnd_rows) == 1 and len(sig_rows) == 1:
        ro["arch"] = "single2"
    elif len(rows) == 3 and len(gnd_rows) == 1 and len(sig_rows) == 2:
        ro["arch"] = "dual3"
    else:
        ro["arch"] = "unknown"
        ro["errors"].append(
            f"★★【状态漂移】{V2_REF} 在 {GEN_NETLIST} 里的行数 / 网名不是已知形态 ⇒ "
            f"★**期望: 2 行 (1 信号 + 1 GND) 或 3 行 (2 信号 + 1 GND)** ⇒ "
            f"★**实际: {len(rows)} 行 (GND {len(gnd_rows)} 行 / 信号 {len(sig_rows)} 行) "
            f"⇒ 行号 {[r['line'] for r in rows]}** ⇒ 拒绝落 ★")

    # ── 行必须【连续】(★中间夹了别的行 ⇒ 拼不出一个可替换的块 ⇒ 拒绝落★) ──
    base = rows[0]["off"]
    for a, b in zip(rows, rows[1:]):
        gap = txt[a["end"]:b["off"]]
        if gap.strip():
            ro["errors"].append(
                f"★★【状态漂移】{V2_REF} 的 L{a['line']} 与 L{b['line']} 之间夹了别的内容 ⇒ "
                f"★**⇒ 拼不出一个可替换的整块 ⇒ 拒绝落** ★")
    ro["block"] = txt[base:rows[-1]["end"]]
    for r in rows:
        r["rel_spans"] = [(s - base, e - base) for (s, e) in r["spans"]]

    # ── 型号 / evidence (★几行的 value 必须一致★) ──
    vals = {r["value"] for r in rows}
    if len(vals) != 1:
        ro["errors"].append(
            f"★★【状态漂移】{V2_REF} 的 {len(rows)} 行 value 不一致 ⇒ "
            f"★**期望: 同一颗器件的同一串 value** ⇒ ★**实际: {sorted(vals)}** ⇒ 拒绝落 ★")
    ro["model"] = rows[0]["value"]
    ro["evidence"] = rows[0]["ev"]

    # ── 型号轴: 现在是占位/判据串 ⇒ 拒绝落 (★不许把占位串原样留着当「落了」★) ──
    if any(m in ro["model"] for m in V2_PLACEHOLDER_MARKS) or not V2_OPN_RE.match(ro["model"]):
        ro["errors"].append(
            f"★★【型号轴未落】{GEN_NETLIST} 里 {V2_REF} 的 value 还是【占位 / 判据串】★★\n"
            f"   ★**期望**: 一条真 OPN (★第一个 token 必须含数字, 例 `TPD1E05U06DPYR ...`★)\n"
            f"   ★**实际**: {ro['model']!r}\n"
            f"   ★**⇒ 型号归【选型级 / 老板】(ISS-241 矩阵 · ISS-257 已落的那条就是本工具要保住的那条)★**\n"
            f"   ★**⇒ 本工具【不】写判据串, 也不替你选型号 ⇒ 拒绝落 (★零写盘★)**★")

    # ── BOM 侧的 OPN (PARTS 字典) 必须与网表 value 指的是同一颗器件 ──
    m = re.search(r'"' + re.escape(V2_REF) + r'"\s*:\s*\{[^\n]*?"opn"\s*:\s*"([^"]*)"', txt)
    if m:
        ro["opn"] = m.group(1)
        ro["opn_line"] = txt.count("\n", 0, m.start()) + 1
        a_tok = ro["model"].split(" ")[0]
        b_tok = ro["opn"].split(" ")[0]
        if a_tok != b_tok:
            ro["errors"].append(
                f"★★【状态漂移】{V2_REF} 的网表 value 与 PARTS 字典的 OPN 不是同一颗器件 ⇒ "
                f"★**期望: 两边第一个 token 相同** ⇒ ★**实际: 网表 {a_tok!r} / PARTS {b_tok!r}** ⇒ 拒绝落 ★")
    else:
        ro["warnings"].append(f"★★**PARTS 字典里没找到 {V2_REF} 的 opn ⇒ 型号一致性这一条本轮没校到** ★")
    return ro


def _splice(txt: str, spans: list[tuple[int, int]], news: list[str]) -> str:
    """按 (起, 止) 偏移替换 txt 里的若干段 (★倒序替换, 免得偏移串了★)。"""
    out = txt
    for (s, e), nt in sorted(zip(spans, news), key=lambda x: -x[0][0]):
        out = out[:s] + nt + out[e:]
    return out


def v2_netlist_line(root: str, ref: str, net: str) -> int | None:
    """在 `HW/netlist_v1.csv` 里找 (ref, net) 那一行的行号 (1-based, 含表头)。"""
    path = os.path.join(root, "HW/netlist_v1.csv")
    if not os.path.exists(path):
        return None
    hits = []
    with open(path, encoding="utf-8", newline="") as fh:
        for i, line in enumerate(fh, start=1):
            cells = next(csv.reader([line.rstrip("\n")]), [])
            if len(cells) > 4 and cells[4].strip() == ref and cells[1].strip() == net:
                hits.append(i)
    if len(hits) != 1:
        return None
    return hits[0]


def v2_dual3_block(model: str, evidence: str) -> str:
    """★架构 ② 的目标块: 3 行 (D+ / D− / GND) (★value = 老板拍的型号, 不是判据串★)★。"""
    return (
        '    add("P1", "NET_USB_D_P_TYPEC", "D_ESD_USB_D", "NET_USB_D_P_TYPEC", "D_ESD_USB_D",\n'
        '        "%s", "D", "必装", "%s", "",\n'
        '        "[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (3脚双通道: pin1=D+ / pin2=D− / pin3=GND) —— '
        '★**已从 SoM 侧 USB_D_P_SRC 挪到 Type-C 侧 NET_USB_D_P_TYPEC** (★ISS-211 第(4)条: 不挪等于没护★) —— '
        '★**Forlinx 载板指引要求 ESD 紧贴接口**", "A-24")\n'
        '    add("P1", "NET_USB_D_N_TYPEC", "D_ESD_USB_D", "NET_USB_D_N_TYPEC", "D_ESD_USB_D",\n'
        '        "%s", "D", "必装", "%s", "",\n'
        '        "[D_ESD_USB_D] ★D− 侧 (pin2) —— ★**官方口径: 两条数据线都要护** '
        '(ON Semi AND8074/D + TI TPD2EUSB30 2ch) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**", "A-24")\n'
        '    add("P1", "GND", "D_ESD_USB_D", "GND", "D_ESD_USB_D", "%s", "D", "必装",\n'
        '        "%s", "", "[D_ESD_USB_D] ESD 地端 (pin3)", "A-24")\n'
    ) % (model, evidence, model, evidence, model, evidence)


def v2_auth_records(root: str, csv_line: int, old_net: str, new_net: str) -> list[dict]:
    """★V-2 的【身份变更授权记录】 (★身份列从 registry 取·值从网表行取★)

    ★**为什么要机器生成 (★不许手抄★)**: 行号锚点守卫的【合法落表】通道判的是
      「落表台账里能查到 (落表单号 + 文件名 + 旧身份 + 新身份)」⇒ ★手抄必然抄错★
      ⇒ ★守卫判红 ⇒ 落表器自回滚 ⇒ 合法落表做不成** ★
    ★**身份列不许硬编码**: 从 `HW/land_row_anchors_registry.json` 的 `d4_a417_net` 条目取
      (★那是守卫自己的口径★ ⇒ 两边一致★) ⇒ 取不到 / 身份列里没有 `net` ⇒ 返回空
      ⇒ ★**空 ⇒ 落表器拒绝落 (★fail-closed★)** ★
    """
    cols = ["ref", "net"]
    reg_p = os.path.join(root, REGISTRY_JSON)
    if os.path.exists(reg_p):
        try:
            with open(reg_p, encoding="utf-8") as fh:
                reg = json.load(fh)
            a = (reg.get("anchors") or {}).get("d4_a417_net") or {}
            if a.get("idcols"):
                cols = [str(c) for c in a["idcols"]]
        except Exception:
            pass
    if "net" not in cols:
        return []
    row = None
    try:
        with open(os.path.join(root, NETLIST_CSV), encoding="utf-8") as fh:
            for i, r in enumerate(csv.DictReader(fh), start=2):
                if i == csv_line:
                    row = r
                    break
    except Exception:
        return []
    if row is None:
        return []
    old_vals = [(row.get(c, "") or "").strip() for c in cols]
    new_vals = list(old_vals)
    ni = cols.index("net")
    old_vals[ni] = old_net
    new_vals[ni] = new_net
    return [{"file": NETLIST_CSV, "table": "netlist", "line": csv_line,
             "old": old_vals, "new": new_vals}]


def v2_recipe(value: str, root: str = "", arch_req: str = "", model_req: str = "",
              ev_req: str = "") -> Decision:
    d = Decision(v="V-2", value=value)
    if value == "2":
        # ★★ISS-230 实测: V-2 只落网表侧 ⇒ --expect-resolved 7→7 ⇒ 一条都转不绿 = 假绿★★
        d.rejected = ("★★**V-2=2 (只落网表侧) 必须打回**★★ ⇒ ★**ISS-230 实测 (2026-11-16 06:2x, main 已核): "
                      "V-2 网表侧全落完, `--expect-resolved` 仍是 7 条 ⇒ 一条都转不绿 = 假绿**★ ⇒ "
                      "★**不许当正路**★ ⇒ ★**要落 V-2 就必须写成【网表侧 + 板那一趟】两段 (V-2=1)★**")
        return d

    d.delta = 0          # ★网表侧 0 条转绿 (ISS-230 实测 7→7)★
    d.board_delta = 3    # ★板那一趟 (B-3/B-4/B-5) 才转绿 3 条 (R4×2 + R9)★

    ro = v2_read_source(root)
    d.errors += ro["errors"]
    d.v2_readout.append(f"★**真源现状 (★现读 `{GEN_NETLIST}`, 不靠硬编码旧串★)**: "
                         f"架构 = ★**{ro['arch'] or '★(读不出来)★'}** ★ · "
                         f"型号 = ★**{ro['model'] or '★(读不出来)★'}** ★ · "
                         f"evidence = ★**{ro['evidence'] or '★(读不出来)★'}** ★")
    if ro["opn"]:
        d.v2_readout.append(f"★**BOM 侧 OPN (PARTS 字典 L{ro['opn_line']})**: `{ro['opn']}` ★")
    if ro["errors"]:
        d.notes.append("★★**真源读不出来 / 读出来不自洽 ⇒ 本次【拒绝落】(★零写盘★) ⇒ 修法见交卷单 §B2** ★")
        return d

    cur_arch = ro["arch"]
    cur_shape = V2_ARCHS.get(V2_SHAPE2ARCH.get(cur_arch, ""), None)
    want_arch = arch_req or V2_SHAPE2ARCH.get(cur_arch, "")
    d.v2_src_arch = V2_SHAPE2ARCH.get(cur_arch, "")
    d.v2_src_model = ro["model"]

    # ── 架构轴: 老板没拍 ⇒ 落表器【只】认真源现状 (★不替老板选架构★) ──
    if not arch_req:
        d.notes.append(
            f"★★**架构轴 (A3 / W-1) 未拍 ⇒ 本次落表按【真源现状】"
            f"{cur_shape['title'] if cur_shape else cur_arch} 走** ★\n"
            f"   ★**落表器【不】替你选架构** ★ ⇒ ★**换架构必须显式 `--v2-arch=<1|2|3>` + `--v2-model=<型号>`** ★")
    elif arch_req not in V2_ARCHS:
        d.errors.append(f"★★`--v2-arch` 取值 {arch_req!r} 不认识 ⇒ 只认 {sorted(V2_ARCHS)} ★")
        return d
    else:
        d.notes.append(
            f"★★**架构轴 (A3 / W-1) = {V2_ARCHS[arch_req]['title']}** (★老板显式指定★) ★\n"
            f"   {V2_ARCHS[arch_req]['desc']}\n"
            f"   代价: {V2_ARCHS[arch_req]['cost']}")

    # ── 型号轴: 真源是真型号 ⇒ 原样保住; 要改 ⇒ 必须显式给型号 + 证据等级 ──
    model = ro["model"]
    evidence = ro["evidence"]
    d.v2_arch = want_arch
    d.v2_model = model
    if model_req:
        model = model_req
        evidence = ev_req or evidence
        d.notes.append(
            f"★★**型号轴 = 老板显式指定**: `{model}` (★evidence `{evidence}`★) ★\n"
            f"   ★**本工具【不】写判据串** ⇒ 型号必须由老板 / 选型给出来 ★")
        if not ev_req:
            d.warnings.append("★★**`--v2-model` 给了但 `--v2-evidence` 没给 ⇒ 沿用真源现状的 evidence "
                              f"(`{evidence}`) ⇒ ★**证据等级必须由落表人自己负责** ★")
    else:
        d.notes.append(
            f"★★**型号轴: 真源现值原样保住 (★一个字都不改★) ⇒ `{model}` + evidence `{evidence}`** ★\n"
            f"   ★**⇒ 本次落表【不会】把真型号降级成一句判据串 (★ISS-257 的成果不会被 undo★)** ★")

    rows = ro["rows"]
    sig_rows = [r for r in rows if r["net"] != "GND"]
    src_shape = cur_arch
    want_shape = V2_ARCHS[want_arch]["shape"]

    # ── 已落过? (★挪网已经做过了 ⇒ 明确区分于「状态漂移」★) ──
    already = [r for r in sig_rows if r["net"] in V2_NET_MOVE.values()]
    if already and want_shape == src_shape:
        d.errors.append(
            "★★【已落过】D_ESD_USB_D 的信号行已经在 Type-C 侧了 ⇒ "
            f"★**期望: 还在 SoM 侧 ({' / '.join(sorted(V2_NET_MOVE))})** ⇒ "
            f"★**实际: L{already[0]['line']} net = {already[0]['net']}** ⇒ "
            f"★**不要重复落 (★零写盘★)**★")
        return d

    if want_shape == src_shape:
        # ═══ 同架构 ⇒ 只做【挪网】(★行数不变 ⇒ 行号不漂移★) ═══
        target_net = None
        sig = None
        for r in sig_rows:
            if r["net"] in V2_NET_MOVE:
                target_net = V2_NET_MOVE[r["net"]]
                sig = r
                break
        if target_net is None:
            d.errors.append(
                f"★★【状态漂移】D_ESD_USB_D 的信号行网名不在挪网对照表里 ⇒ "
                f"★**期望: {sorted(V2_NET_MOVE)} 之一** ⇒ ★**实际: {[r['net'] for r in sig_rows]}** ⇒ 拒绝落 ★")
            return d
        old_block = ro["block"]
        edits = []
        if sig["net"] != target_net:
            edits.append((sig["rel_spans"][1], '"%s"' % target_net))
            if sig["node2"] == sig["net"]:
                edits.append((sig["rel_spans"][3], '"%s"' % target_net))
        if model_req:
            for r in rows:
                edits.append((r["rel_spans"][5], '"%s"' % model))
        new_block = _splice(old_block, [x[0] for x in edits], [x[1] for x in edits]) if edits else old_block
        d.patches.append(Patch(
            GEN_NETLIST, old_block, new_block,
            f"V2-1 D_ESD_USB_D 挪到 Type-C 侧 (★架构 {cur_arch} ⇒ 行数不变, 只动网名★)"))

        # ── 门禁 EXPECT: 只有「网名」这一条现状值要改 (★value / evidence 一个字不动★) ──
        csv_line = v2_netlist_line(root, V2_REF, sig["net"])
        if csv_line is None:
            d.errors.append(
                f"★★【状态漂移】在 `HW/netlist_v1.csv` 里找不到 ref={V2_REF} 且 net={sig['net']} 的行 ⇒ "
                f"★**⇒ 门禁锚点行号算不出来 ⇒ 拒绝落**★")
            return d
        d.expects.append(ExpectPatch(
            "d4_a417_net", f"net == {target_net}",
            f"d4 表A L{csv_line} ESD 信号行 net (★从 SoM 侧挪到 Type-C 侧★)"))
        # ── ★ISS-283 · B1: 身份变更授权记录 (★守卫的【合法落表】通道靠它★) ──
        d.auth_changes += v2_auth_records(root, csv_line, sig["net"], target_net)
        if not d.auth_changes:
            d.errors.append(
                "★★★【落表授权】V-2 的身份变更授权记录生成不出来 "
                "(★registry 的身份列里没有 `net`·或网表里找不到那一行★) ⇒ "
                "★**不许硬落** (★守卫查不到授权 ⇒ 一定判红·落表器会自回滚★) ⇒ 拒绝落 (★零写盘★)★★")
            return d
        d.v2_readout.append(
            f"★**落表动作**: 只动 1 行的 net (真源 L{sig['line']} → `{target_net}`) ⇒ "
            f"★**行数不变 ⇒ 门禁锚点行号不漂移** ★")
        d.v2_readout.append(
            f"★**身份变更授权 (★ISS-283 B1·行号锚点守卫的合法通道★)**: "
            f"旧身份 `{d.auth_changes[0]['old']}` → 新身份 `{d.auth_changes[0]['new']}` "
            f"(★网表 L{csv_line}·授权记录会写进落表台账★)")

    elif want_shape == "dual3" and src_shape == "single2":
        # ═══ ① → ②: 2 行变 3 行 (★D− 行新插 ⇒ 网表行号 ≥418 全部 +1★) ═══
        if not model_req:
            d.errors.append(
                "★★【型号轴必须同时拍】架构换成 ② (3脚双通道) ⇒ ★**必须同时给 `--v2-model <真 OPN>`** ★\n"
                "   ★**理由: 换架构必然改 value ⇒ 本工具【不许】写判据串代替型号 (★那会把 ISS-257 的成果 undo 掉★)** ★\n"
                "   ★**⇒ 型号归【选型级 / 老板】(A3 / W-1 一起拍) ⇒ 拒绝落 (★零写盘★)**★")
            return d
        d.patches.append(Patch(
            GEN_NETLIST, ro["block"], v2_dual3_block(model, evidence),
            "V2-1 D_ESD_USB_D: 2 行 → 3 行 (pin1=D+ / pin2=D− / pin3=GND) + 挪到 Type-C 侧"))
        d.line_shift_extra = [("netlist", V2_NETLIST_SHIFT_FROM), ("pins", V2_PINS_SHIFT_FROM)]
        d.expects += [
            ExpectPatch("d4_a417_value", f"value == {model}", "d4 表A L417 ESD D+ 行 value (★落成老板拍的型号★)"),
            ExpectPatch("d4_a417_net", "net == NET_USB_D_P_TYPEC", "d4 表A L417 ESD D+ 行 net (从 SoM 侧挪到 Type-C 侧)"),
            ExpectPatch("d4_a418_value", f"value == {model}", "d4 表A L419 ESD GND 行 value (★行号随插行 +1★)"),
            ExpectPatch("d9_esd_dual_claim", f"value == {model}", "d9 表A L417 自称双通道的 value"),
            ExpectPatch("d4_bom62_value", f"value == {model}", "d4 BOM L62 D_ESD_USB_D value"),
        ]
        d.v2_readout.append("★**落表动作**: 2 行 → 3 行 (★新增 D− 行★) ⇒ ★**门禁锚点行号 ≥418 全部 +1** ★")
    else:
        d.errors.append(
            f"★★【架构切换不支持】真源现状 = ★**{cur_arch}** ★ ⇒ 目标 = ★**{want_shape}** ★\n"
            f"   ★**⇒ 换架构 = 改 footprint = 板那一趟 (★本工具【只】落网表侧, 板一个字节都不碰★) ⇒ 拒绝落** ★")
        return d

    # ── 板那一趟的清单 (★本工具【不做】★) ──
    d.warnings.append("★★**V-2=1 的板那一趟本工具【不做】** (★`HW/PCB/demo_mainboard.kicad_pcb` 一个字节都不碰★) ⇒ "
                      "★**板侧 B-3 (换封装 / 改占位焊盘) / B-4 (挪到 J_USB_C 旁 ≤3.0mm) / B-5 (D− 补 ESD) 继续排队**★")
    d.warnings.append("★★**网名挪了 ⇒ 板上的 footprint 焊盘网名也必须同趟改** (★`D_ESD_USB_D` pad1: "
                      "`USB_D_P_SRC` → `NET_USB_D_P_TYPEC`★) ⇒ ★**板那一趟漏改 ⇒ 网表与板对不上** ★")
    d.notes.append("★★**网表侧落表 = 0 条转绿** (★ISS-230 实测 7→7★) ⇒ ★**必须写成两段: 网表侧 + 板那一趟**★")
    d.notes.append("★★**两个未决 (★本工具【不】代拍, 只把两件事分开列出来★)**★★\n"
                   "   ① ★**架构轴 (A3 / W-1)**: ① 2脚单通道 / ② 3脚双通道 / ③ 2脚双向件 —— "
                   "★**物理约束: 占位只有 2 焊盘 ⇒ ② 落不下 (ISS-241 硬发现①) ⇒ ② 必须先改 footprint (板那一趟)** ★\n"
                   "   ② ★**型号轴 (选型级)**: 现状 `TPD1E05U06DPYR` = ISS-241 矩阵 ③ 的推荐项 (★evidence [官网]★) —— "
                   "★**换架构 ⇒ 必须同时换型号 ⇒ 两轴必须一起拍** ★")
    return d


# ═══════════════════════════════════════════════════════════════════════════
# 4-B · V-5 (W-4 / G-1: `Q_PG` 写法 A) + V-6 (G-5 / W-6: LED 亮度档)
#
# ★★**为什么这两个也走落表器 (★而不是人手改 CSV·★2026-11-17 12:1x 实测★)** ★★:
#   ① ★**落表 = 机器留痕** ⇒ 备份/回滚/台账 §16 新旧 md5/老板凭据/门禁实跑 全部自动 ★
#   ② ★**人手改 CSV 会被下次生成覆盖** ⇒ 改的必须是【真源 `state/gen_netlist.py`】★★
#   ③ ★**两条都改了【实体身份 / 器件阻值】** ⇒ 必须过【行号锚点守卫】与【落表后门禁】★ ★
#
# ★**老板凭据 (★机器转录·不代拍★)** ★:
#   · V-5 / W-4 / G-1 = `boss_w4_q_pg_topology_20261117` (★pm.yaml ★2026-11-17 09:49★) ★
#   · V-6 / G-5 / W-6 = `boss_g5_led_brightness_20261117` (★pm.yaml ★2026-11-17 09:49★) ★
# ═══════════════════════════════════════════════════════════════════════════

V5_BLOCK_OLD = '''    add("P1", "PWR_ON", "Q_PG", "U_PWR_SW ON", "Q_PG",
        "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)", "SW",
        "必装", "[官方]", "",
        "[PWR_ON] ★★**V1.9 P0 修正 (2026-10-28)**: Q_PG 由 N-MOS 改 **P-MOS 高边开关** —— "
        "原 N-MOS 低边接法是**错的**: 栅极接 PG(LOW=电源良好) · 源极接 GND · 漏极接 ON ⇒ "
        "PG 低时 MOS 关 ⇒ ON 只剩 10k 下拉 = 低 = **开关关** ⇒ ①插电反而开不了机 ②SoC 拉高 PWR_CTRL 会被 Q_PG 拉到 GND 拉不高 ⇒ **开机路径彻底不通**。"
        "★**正解 (零新增 pin · 零新增轨)**: 源极接 ON · **漏极接 BAT_SW (电池轨, 关机后仍带电)** · 栅极接 PG ⇒ "
        "PG 低(良好)→Vgs≈-4.2V→P-MOS 导通→ON=BAT_SW=高=**开机**; PG 高(无输入)→Vgs=+3.3V→P-MOS 关→ON 落下拉=低=**关** (关机态仍能充电)。"
        "★选型硬判据: 低漏 P-MOS · Vgs(th) 明确 · 栅极最大耐压 ±20V · 关断漏电 nA 级",
        "C-02")
    add("P1", "BAT_SW", "Q_PG", "NET_BAT_SW", "Q_PG",
        "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)", "SW",
        "必装", "[官方]", "",
        "[PWR_ON] ★V1.9: Q_PG **漏极**接 **BAT_SW (电池轨 3.0-4.2V)** —— ★**不能用 3.3V 轨**: 库内 3.3V 全挂在 SYS 下 "
        "(U_LDO_IO33 输入 = RAIL_SYS), 关机断电后即灭 ⇒ 漏极无电位 ⇒ 插电开不了机。BAT_SW 在关机态仍带电 ✔",
        "C-02")
    add("P1", "PWR_GOOD", "Q_PG", "J_CHG pin6", "Q_PG",
        "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)", "SW",
        "必装", "[官方]", "",
        "[PWR_GOOD] Q_PG **栅极** = 充电板 PG (经 J_CHG pin6 跨铰链, 框侧开漏信号; 主板侧 R_PU_PG 10k 上拉 3.3V)。"
        "★V1.9: PG 低(电源良好) → 栅极≈0 → P-MOS 导通 → ON 拉高 = 开机", "C-06")
'''

V5_BLOCK_NEW = '''    add("P1", "PWR_GOOD", "Q_PG", "J_CHG pin6", "Q_PG",
        "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)", "SW",
        "必装", "[官方]", "",
        "[PWR_GOOD] ★★**ISS-283 · G-1 裁决 (2026-11-17 09:49 老板拍板「写法 A」)★**: DMP3098L 厂商引脚序 ★**1=G / 2=S / 3=D**★ ⇒ ★**pad1 = 栅极 G = PWR_GOOD (充电板 PG)★** · ★**pad2 = 源极 S = BAT_SW**★ · ★**pad3 = 漏极 D = PWR_ON (负载侧)**★ ⇒ ★**写法 A**★ (★**原落表把 pad1↔pad3 写反 ⇒ G/D 对调 ⇒ 写法 B ⇒ PG 高低都关 ⇒ 开机路径彻底不通**★; ★**ISS-244 实跑**: PG 低 ⇒ VGS≈−4.2V ⇒ 导通 ⇒ ON=BAT_SW=高=开机; PG 高 ⇒ VGS≈−0.9V ⇒ 关断 ⇒ ON 落下拉=低=关★) ★**板上 `Q_PG` land 仍按旧接法画 (pad1→PWR_ON / pad3→PWR_GOOD) ⇒ 板那一趟必须重画这 3 根线 (ISS-283 板侧清单 §③-2)★**", "C-06")
    add("P1", "BAT_SW", "Q_PG", "NET_BAT_SW", "Q_PG",
        "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)", "SW",
        "必装", "[官方]", "",
        "[PWR_ON] ★V1.9: Q_PG **源极 (pad2 = S)** 接 **BAT_SW (电池轨 3.0-4.2V)** —— ★**不能用 3.3V 轨**: 库内 3.3V 全挂在 SYS 下 "
        "(U_LDO_IO33 输入 = RAIL_SYS), 关机断电后即灭 ⇒ 源极无电位 ⇒ 插电开不了机。BAT_SW 在关机态仍带电 ✔ ★**ISS-283 · G-1 写法 A: pad2 = S = BAT_SW (★这一格本来就是对的·这次不动★)**★",
        "C-02")
    add("P1", "PWR_ON", "Q_PG", "U_PWR_SW ON", "Q_PG",
        "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)", "SW",
        "必装", "[官方]", "",
        "[PWR_ON] ★★**V1.9 P0 修正 (2026-10-28)**: Q_PG 由 N-MOS 改 **P-MOS 高边开关** —— "
        "原 N-MOS 低边接法是**错的**: 栅极接 PG(LOW=电源良好) · 源极接 GND · 漏极接 ON ⇒ "
        "PG 低时 MOS 关 ⇒ ON 只剩 10k 下拉 = 低 = **开关关** ⇒ ①插电反而开不了机 ②SoC 拉高 PWR_CTRL 会被 Q_PG 拉到 GND 拉不高 ⇒ **开机路径彻底不通**。"
        "★**正解 (零新增 pin · 零新增轨)**: ★**ISS-283 · G-1 写法 A (2026-11-17 09:49 老板拍板)★** ★**栅极 (pad1, G) 接 PG** · "
        "★**源极 (pad2, S) 接 BAT_SW (电池轨, 关机后仍带电)** · ★**漏极 (pad3, D) 接 ON** ⇒ "
        "PG 低(良好)→Vgs≈-4.2V→P-MOS 导通→ON=BAT_SW=高=**开机**; PG 高(无输入)→Vgs≈-0.9V→P-MOS 关→ON 落下拉=低=**关** (关机态仍能充电)。"
        "★选型硬判据: 低漏 P-MOS · Vgs(th) 明确 · 栅极最大耐压 ±20V · 关断漏电 nA 级",
        "C-02")
'''

V6_BLOCK_OLD = '''        add("P7", f"LED_{col}_D", f"R_LED_{col}", f"D_LED_{col}", f"R_LED_{col}", "1k ±1%",
            "R", dnp, "[推算]", "",
            f"[LED_{col}_D] LED_{col} 串阻 (3.3V 驱动; 实际值随 LED Vf 与目标亮度定)")
'''

V6_BLOCK_NEW = '''        add("P7", f"LED_{col}_D", f"R_LED_{col}", f"D_LED_{col}", f"R_LED_{col}", "68Ω ±1%" if col == "R" else ("55Ω ±1%" if col == "G" else "1k ±1%"),
            "R", dnp, "[推算]", "",
            f"[LED_{col}_D] LED_{col} 串阻 = {('68Ω ±1%' if col == 'R' else ('55Ω ±1%' if col == 'G' else '1k ±1%'))} (★**ISS-283 · G-5 裁决 (2026-11-17 09:49 老板拍「选项 ② = 改 R 到 20 mA 档」)★**; ★**红 68Ω / 绿 55Ω = ISS-244 [官网] 级实测折算的 20 mA 档真值 (★150Ω 只有 ~5 mA·达不到 20 mA 档★)★**) ⇒ 单颗 ~20 mA · 功耗 2.2 mW→66 mW (★两颗 ≈ 0.13 W 进电池账★) · ★**亮度 ×14 ⇒ IEC 62471 分级要重算 (★ISS-283 登记 need·不代拍★)**★)" if col in ("R", "G") else f"[LED_{col}_D] LED_{col} 串阻 (3.3V 驱动; 实际值随 LED Vf 与目标亮度定)")
'''


def netlist_auth_records(root: str, specs: list[tuple[str, str, str]]) -> list[dict]:
    '''★网表身份变更授权记录 (★通用版·身份列 = [ref, net]★) ★

    ★**为什么要有它 (★ISS-283 · B1·V-5 落表改的是 pad↔net 的对调★)**:
      落表改 net ⇒ 那一行的实体身份 (ref+net) 变了 ⇒ 行号锚点守卫会判红
      ⇒ 必须在台账里登记【旧身份 → 新身份】⇒ 守卫查到授权记录才放行 ★
    ★**旧行号按 (ref, old_net) 现读真源** ⇒ 不许手抄行号 ★
    '''
    out: list[dict] = []
    cols = ["ref", "net"]
    try:
        with open(os.path.join(root, NETLIST_CSV), encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except Exception:
        return out
    for ref_want, old_net, new_net in specs:
        line = None
        row = None
        for i, r in enumerate(rows, start=2):
            if ((r.get("ref") or "").strip() == ref_want
                    and (r.get("net") or "").strip() == old_net):
                line, row = i, r
                break
        if line is None or row is None:
            continue
        old_vals = [(row.get(c, "") or "").strip() for c in cols]
        new_vals = list(old_vals)
        ni = cols.index("net")
        old_vals[ni] = old_net
        new_vals[ni] = new_net
        out.append({"file": NETLIST_CSV, "table": "netlist", "line": line,
                    "old": old_vals, "new": new_vals})
    return out


def _q_pg_pad_nets(root: str) -> list[str]:
    '''★读盘: `Q_PG` 的三条 `add()` 在网表里落成哪三个网 (★行序 = pad 序★)'''
    out: list[str] = []
    try:
        with open(os.path.join(root, NETLIST_CSV), encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if (r.get("ref") or "").strip() == "Q_PG":
                    out.append((r.get("net") or "").strip())
    except Exception:
        return out
    return out


def v5_recipe(value: str, root: str = "", arch_req: str = "", model_req: str = "",
              ev_req: str = "") -> Decision:
    '''★V-5 (W-4 / G-1): `Q_PG` 写法 A = S=BAT_SW / D=ON / G=PG ★'''
    d = Decision(v="V-5", value=value)
    if value != "A":
        d.rejected = ("★★**V-5=B (写法 B) 必须打回**★★ ⇒ ★**写法 B = note 首句直译 (源极接 ON · "
                      "漏极接 BAT_SW · 栅极接 PG) ⇒ PG 低时 VGS=0V 不导通 · PG 高时 VGS=+3.3V 反向偏置 ⇒ "
                      "【PG 高低都关 ⇒ 开机路径彻底不通】**★ (★ISS-244 实跑★) ⇒ ★**老板 2026-11-17 09:49 "
                      "拍的是写法 A** (★pm.yaml `boss_w4_q_pg_topology_20261117`★) ⇒ 其它取值一律打回★")
        return d
    d.delta = 0          # ★网表侧 0 条转绿 (★pad 序要对 ⇒ 板那一趟重画 land 才转绿★)★
    d.board_delta = 0
    d.v2_readout.append(
        "★★**落表动作 (W-4 / G-1 写法 A)**: `state/gen_netlist.py` 里 `Q_PG` 的三条 `add()` "
        "★**整块重排 (★pad1↔pad3 的网互换★) + 三行 note 改写成写法A**★ ⇒ "
        "★**pad1 = PWR_GOOD (G) · pad2 = BAT_SW (S) · pad3 = PWR_ON (D)**★")
    d.v2_readout.append(
        "★★**老板凭据**: 2026-11-17 09:49「按照你的建议执行」⇒ pm.yaml "
        "`boss_w4_q_pg_topology_20261117` (★已录★) ⇒ ★**落表器只机器转录·不代拍**★")
    if root:
        _cur = _q_pg_pad_nets(root)
        if _cur == ["PWR_GOOD", "BAT_SW", "PWR_ON"]:
            d.errors.append("★★【已落过】`Q_PG` 的 pad 序已经是写法 A "
                            "(PWR_GOOD / BAT_SW / PWR_ON) ⇒ ★**拒绝重复落 (★零写盘★)**★")
            return d
        if _cur != ["PWR_ON", "BAT_SW", "PWR_GOOD"]:
            d.errors.append("★★【状态漂移】`Q_PG` 的 pad 序不是预期的那两档之一 ⇒ "
                            f"★**期望: ['PWR_ON','BAT_SW','PWR_GOOD'] (旧) 或 "
                            f"['PWR_GOOD','BAT_SW','PWR_ON'] (写法A·已落过)★** ⇒ "
                            f"★**实际: {_cur}**★ ⇒ 拒绝落 (★零写盘★)")
            return d
    d.patches.append(Patch(GEN_NETLIST, V5_BLOCK_OLD, V5_BLOCK_NEW,
                            "V5-1 `Q_PG` 写法 A (★pad1↔pad3 网互换 + 三行 note 改写★)"))
    d.auth_changes += netlist_auth_records(root, [("Q_PG", "PWR_ON", "PWR_GOOD"),
                                                   ("Q_PG", "PWR_GOOD", "PWR_ON")])
    if root and not d.auth_changes:
        d.errors.append("★★★【落表授权】V-5 的身份变更授权记录生成不出来 ⇒ "
                        "★**不许硬落** (★守卫查不到授权 ⇒ 一定判红·落表器会自回滚★) ⇒ 拒绝落 (★零写盘★)★★")
        return d
    d.v2_readout.append(
        "★**身份变更授权 (★ISS-283 B1 通道★)**: "
        + "; ".join(f"L{a['line']} {a['old']} → {a['new']}" for a in d.auth_changes))
    d.warnings.append("★★**V-5 的板那一趟本工具【不做】** (★板一个字节都不碰★) ⇒ "
                      "★**板上的 `Q_PG` land 仍按旧接法画 (pad1→PWR_ON / pad3→PWR_GOOD) ⇒ "
                      "板那一趟必须重画 `Q_PG` 的 3 根线**★")
    d.warnings.append("★★**连带 (★如实登记·不瞒★)**: 板那一趟要么重画 land, 要么改选 D-S-G 序器件 "
                      "(★那也是换封装 ⇒ 同样是板那一趟★) ⇒ ★**板只改一次那一趟的 S 步清单必须带上它**★")
    return d


def v6_recipe(value: str, root: str = "", arch_req: str = "", model_req: str = "",
              ev_req: str = "") -> Decision:
    '''★V-6 (G-5 / W-6): LED 亮度档 = `R_LED_R` 68Ω · `R_LED_G` 55Ω (★20 mA 档★) ★'''
    d = Decision(v="V-6", value=value)
    if value != "20mA":
        d.rejected = ("★★**V-6=150R 必须打回**★★ ⇒ ★**150Ω 只有 ~5 mA (ISS-244 [官网] 级实测折算)★** ⇒ "
                      "★**达不到老板批的「20 mA 档」**★ ⇒ ★**20 mA 档的真值 = 红 68Ω / 绿 55Ω**★ "
                      "(★老板 2026-11-17 09:49 拍的是「选项 ② = 改 R 到 20 mA 档」·pm.yaml "
                      "`boss_g5_led_brightness_20261117`★) ⇒ 其它取值一律打回★")
        return d
    d.delta = 0
    d.board_delta = 0
    d.v2_readout.append(
        "★★**落表动作 (G-5 亮度档)**: `R_LED_R` = ★**68Ω ±1%**★ (红) · "
        "`R_LED_G` = ★**55Ω ±1%**★ (绿) ⇒ ★**蓝 (`R_LED_B`, DNP) 不在老板拍板范围 ⇒ 保持 1k ±1%**★")
    d.v2_readout.append(
        "★★**老板凭据**: 2026-11-17 09:49「按照你的建议执行」⇒ pm.yaml "
        "`boss_g5_led_brightness_20261117` (★已录★) ⇒ ★**落表器只机器转录·不代拍**★")
    if root:
        try:
            with open(os.path.join(root, NETLIST_CSV), encoding="utf-8") as fh:
                _v = {}
                for r in csv.DictReader(fh):
                    _rf = (r.get("ref") or "").strip()
                    if _rf in ("R_LED_R", "R_LED_G"):
                        _v[_rf] = (r.get("value") or "").strip()
        except Exception:
            _v = {}
        if _v.get("R_LED_R") == "68Ω ±1%" and _v.get("R_LED_G") == "55Ω ±1%":
            d.errors.append("★★【已落过】`R_LED_R` / `R_LED_G` 的阻值已经是 68Ω / 55Ω ⇒ "
                            "★**拒绝重复落 (★零写盘★)**★")
            return d
    d.patches.append(Patch(GEN_NETLIST, V6_BLOCK_OLD, V6_BLOCK_NEW,
                            "V6-1 LED 串阻改 20 mA 档 (★红 68Ω / 绿 55Ω★)"))
    # ★★SPEC.json 的 `imp` 三个值一样 ("1k 串阻 → LED → GND") ⇒ ★**ctx 只定位·old 必须自带区分★
    #   (★不然 find_after 会把 ctx 之后的 3 处全数出来 ⇒ 判「歧义」⇒ 拒绝落·这是对的 fail-closed★)★★
    d.patches.append(Patch(SPEC_JSON,
                            '"signal": "LED_R",\n      "dir": "SoC→LED",\n      "level": "3.3V",\n      "imp": "1k 串阻 → LED → GND",',
                            '"signal": "LED_R",\n      "dir": "SoC→LED",\n      "level": "3.3V",\n      "imp": "68Ω 串阻 → LED → GND",',
                            "V6-2a SPEC.json B-12 (LED_R) 的 imp"))
    d.patches.append(Patch(SPEC_JSON,
                            '"signal": "LED_G",\n      "dir": "SoC→LED",\n      "level": "3.3V",\n      "imp": "1k 串阻 → LED → GND",',
                            '"signal": "LED_G",\n      "dir": "SoC→LED",\n      "level": "3.3V",\n      "imp": "55Ω 串阻 → LED → GND",',
                            "V6-2b SPEC.json B-13 (LED_G) 的 imp"))
    d.warnings.append("★★**连带 (★如实登记·不瞒★)**: 每颗功耗 2.2 mW → 66 mW (★两颗 ≈ 0.13 W 进电池账★) · "
                      "★**亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级要重算 ⇒ 登记 need 给 main (★本工具不代拍★)**★")
    d.warnings.append("★★**这两个阻值进 BOM ⇒ 板那一趟要重出 BOM + 投产包** (★但 footprint 不变 ⇒ "
                      "不构成额外板改★)")
    return d


# ═══════════════════════════════════════════════════════════════════════════
# 5 · 白名单
# ═══════════════════════════════════════════════════════════════════════════

WHITELIST = {
    "V-2": {"1": v2_recipe, "2": v2_recipe},
    "V-3": {"E": v3_recipe, "A": v3_recipe, "D": v3_recipe, "DEG4": v3_recipe},
    "V-4": {"680": v4_recipe, "470": v4_recipe, "390": v4_recipe},
    # ★★ISS-283 · B2/B3: W-4 (G-1 写法A) / G-5 (20mA 亮度档) 也走落表器 (★机器留痕·不许人手改 CSV★)★★
    # ★★白名单里【写死老板拍的那一档】+ ★**把老板没拍的备选也列进来但一律打回**★★
    #   (★V-2 的 "2" 就是这个先例: 进白名单但配方打回 ⇒ 「打回」这条路径才可被机器验★)★★
    "V-5": {"A": v5_recipe, "B": v5_recipe},
    "V-6": {"20mA": v6_recipe, "150R": v6_recipe},
}

WHITELIST_DOC = {
    "V-2": "V-2 ∈ {1, 2}  (1 = 网表侧+板侧两段走 · 2 = 只落网表侧 ⇒ ISS-230 实测是假绿 ⇒ 必须打回)",
    "V-3": "V-3 ∈ {E, A, D, DEG4}  (E = 100k+60k+100nF · A = 2.0M+1.2M · D = 2.0M+1.0M · DEG4 = 保持 DNP, 网表一格不改)",
    "V-4": "V-4 ∈ {680, 470, 390}  (Ω)",
    "V-5": "V-5 ∈ {A, B}  (★W-4 / G-1 · `Q_PG` 写法 A = S=BAT_SW / D=ON / G=PG = 【唯一可落的那档】★ · ★**B 必须打回**: 写法 B ⇒ PG 高低都关 ⇒ 开机路径彻底不通 (ISS-244 实跑)★)",
    "V-6": "V-6 ∈ {20mA, 150R}  (★G-5 / W-6 · `R_LED_R`=68Ω · `R_LED_G`=55Ω (★红/绿 20 mA 档 = 唯一可落的那档★) · ★**150R 必须打回**: 150Ω 只有 ~5 mA ⇒ 达不到老板批的 20 mA 档 (ISS-244 [官网] 级折算)★)",
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
        self.errors: list[str] = []
        self.readout: list[str] = []
        for d in decisions:
            self.patches += d.patches
            self.expects += d.expects
            self.errors += d.errors
            self.readout += d.v2_readout
            # ★★行号漂移: ★**只有架构 ② (2 行 → 3 行) 才需要**★ ⇒ ★**架构 ① (只挪网) 行数不变 ⇒ 不漂移** ★
            self.line_shifts += d.line_shift_extra

    # ── 校验: 每条补丁的 old 必须【恰好】出现 count 次 ──
    def verify(self) -> list[str]:
        errs = list(self.errors)
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
                if n == 0:
                    errs.append(
                        f"★★【状态漂移 or 已落过】★★ 补丁对不上: {p.path} · {p.label} ⇒ "
                        f"★**旧串在真源里出现 0 次 (期望 {p.count} 次)** ⇒ "
                        f"★**⇒ 要么真源那一段被改过了 (漂移), 要么这一格已经落过了 (旧串已被换掉) ⇒ "
                        f"本工具【分不清这两者】⇒ 拒绝落 (★零写盘★) ⇒ 请对一眼真源那一段**★")
                else:
                    errs.append(
                        f"★★【重复 / 歧义】★★ 补丁对不上: {p.path} · {p.label} ⇒ "
                        f"★**旧串在真源里出现 {n} 次 (期望 {p.count} 次)** ⇒ "
                        f"★**⇒ 真源里有多个一样的块 ⇒ 定位不可靠 ⇒ 拒绝落 (★零写盘★)** ★")
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


def append_ledger(root: str, decisions: list[Decision], boss: list[str], old_md5: dict,
                  issue: str = "ISS-236") -> str:
    fpath = os.path.join(root, LANDED_LEDGER)
    if not fpath.endswith(LANDED_LEDGER):
        raise RuntimeError(f"★台账路径不对: {fpath}")
    txt = read_text(fpath)
    now = time.strftime("%Y-%m-%d %H:%M:%S (Asia/Shanghai)")
    lines = []
    lines.append("")
    lines.append("## ★★16 · ★★V 值拍板即落 (★%s · 2026-11-16 · 硬件总工 (hw-lead) 执行 · "
                 "★`state/land_v_values.py` 一键落★) ★★" % issue)
    lines.append("")
    lines.append("> ★**单号**: ★**%s** · ★**owner**: hw-lead · ★**verify_by**: main · "
                 "★**落表器**: ★**`state/land_v_values.py`** (★默认 dry-run · `--apply` 强制 `--boss-decision`★) ★" % issue)
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
    lines.append("### ★★16.3 · 身份变更授权台账 (★ISS-283 · B1 · 行号锚点守卫的【合法落表】通道★) ★★")
    lines.append("")
    lines.append("> ★**这是「合法落表改 net 名」的唯一授权证据** ⇒ ★**守卫查不到下面这些记录 ⇒ 一律判红** ★")
    lines.append("> ★**判据 (★四项齐全才成立★)**: 落表单号 + 文件名 + 表 + 行号 + 旧身份 + 新身份 ★")
    lines.append("> ★**旧身份 / 新身份 = JSON 数组 (★身份列的值·按守卫 registry 的口径★)** ★")
    lines.append("")
    _auths = [(d, a) for d in decisions for a in (d.auth_changes or [])]
    if _auths:
        lines.append("<!-- LANDING_AUTH:BEGIN -->")
        lines.append("| 单号 | 文件 | 表 | 行号 | 旧身份 | 新身份 | 日期 | 凭据 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for _d, _a in _auths:
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                issue, _a["file"], _a["table"], _a["line"],
                json.dumps(_a["old"], ensure_ascii=False),
                json.dumps(_a["new"], ensure_ascii=False),
                now[:10], " / ".join(boss) if boss else "★(无凭据)★"))
        lines.append("<!-- LANDING_AUTH:END -->")
        lines.append("")
    else:
        lines.append("★**本批没有身份变更** (★⇒ 不需要授权记录★) ★")
        lines.append("")
    lines.append("### ★★16.4 · 复现命令 (★B6 自证★) ★★")
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
    lines.append("# ★★ISS-283 · ⑪: 落表后【全闸扫描】 (★一次性跑完所有闸 + 列出红的 + 查有没有人认领★) ★★")
    lines.append("python3 state/land_v_values.py --selftest    # ★落表器自测 (★条数只许增不许减★) ★")
    for _g, _k in ALL_GATES:
        if _g.startswith("state/land_v_values.py --selftest"):
            continue
        lines.append("python3 %s" % _g)
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


def regen_all(root: str) -> list[tuple[str, int, str]]:
    """★按 GEN_ORDER 重跑一遍生成链 (★回滚后必须做!★)

    ★★**为什么必须有这一步 (★2026-11-17 复验实测到的坑★)**★★
      · ★**备份里只有【真源 + 门禁 + 规格页 + 台账】(★派生产物是从真源生成的, 不备份★)** ⇒
        只还原真源 ⇒ ★**网表 / 脚表 / BOM / 原理图页面 停在【落表后】的版本** ⇒
        ★**真源与产物不一致 (半回滚) ⇒ 现状守卫 18 条 EXPECT 全红 (rc=1)★**
      · ⇒ ★**回滚 = 还原真源 + 重生成派生产物 (★顺序还是硬的: netlist → kicad_net → pins★)**★

    ★**返回 [(脚本, rc, 错误尾部)] (★rc≠0 不抛异常, 由调用方决定当不当 fatal★)**
    """
    out: list[tuple[str, int, str]] = []
    for script, _kind in GEN_ORDER:
        sp = os.path.join(root, script)
        if not os.path.exists(sp):
            out.append((script, -1, "★缺文件 (★沙盒最小副本里可能没带★)"))
            continue
        rc, so = run([sys.executable, sp], root)
        out.append((script, rc, so.strip()[-1200:] if rc != 0 else ""))
    return out


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

    # ── ★★回滚必须把【派生产物】一起回滚 (★2026-11-17 复验实测到的坑★)★★
    #   只还原真源 ⇒ 网表/脚表/BOM/原理图 停在【落表后】⇒ 真源与产物不一致 (半回滚) ⇒
    #   现状守卫 18 条 EXPECT 全红 (rc=1) ⇒ ⇒ 回滚后必须按 GEN_ORDER 重生成一遍
    print("★★ 回滚后重生成派生产物 (★不然 = 半回滚: 真源回去了, 产物没回去★)★★")
    regen_failed = []
    for script, rc, err in regen_all(root):
        if rc == 0:
            print(f"   ★ 重生成 OK: {script}")
        elif rc == -1:
            print(f"   ★ 跳过: {script} ({err})")
        else:
            regen_failed.append(f"{script}(rc={rc})")
            print(f"   ★★ 重生成失败: {script} rc={rc}", file=sys.stderr)
            if err:
                for l in err.strip().split("\n")[-6:]:
                    print(f"        {l}", file=sys.stderr)

    # ── 回滚后自检: 现状守卫必须回绿 (★rc=0 = 真源与产物重新一致★) ──
    gpath = os.path.join(root, CHECK_SCRIPT)
    if os.path.exists(gpath):
        grc, gout = run([sys.executable, gpath], root)
        print(f"★ 回滚后现状守卫: rc={grc} (★期望 0 = 真源与产物重新一致★)")
        for l in gout.strip().split("\n")[-3:]:
            print(f"     {l}")
        if grc != 0:
            regen_failed.append(f"现状守卫 rc={grc}")
    if os.path.exists(info):
        print(open(info, encoding="utf-8").read())
    if regen_failed:
        print(f"★★ rc=1: 回滚后派生产物重生成/自检有问题: {'; '.join(regen_failed)} ★★",
              file=sys.stderr)
        return 1
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
# 10 · 落表后【全闸扫描】 (★ISS-283 · ⑪ 的机制化要求★)
# ═══════════════════════════════════════════════════════════════════════════
# ★★**为什么要有这一步 (★main 2026-11-17 11:2x 实跑抓出来的病灶·一字未改★)** ★★:
#   ★**落表成功 ≠ 全链绿** ⇒ 落表完必须扫一遍【所有以真源 md5 / 现状值为基线的闸与自测】★★
#   ★**今天的实例**: 落表前全绿 · 落表后 3 道红 · 其中 2 道【落表前谁都没料到】
#     (★HW 板框口径 C6 / MECH 坐标归一 C4★) ⇒ ★**若不是 main 手工全扫, 这两道会一直红到下一轮★★
#   ⇒ ★**手工扫 = 一定会漏** ⇒ 必须机器化 + 必须【列出红的】+ 必须【查有没有人认领】★★
#
# ★**口径 (★三条硬规矩★)** ★:
#   ① ★**只读** ⇒ 只跑闸, 不碰任何闸的判据 / 阈值 / 台账 ★
#   ② ★**不许 fatal** ⇒ 别的单的闸红 (★SW/MECH 侧在飞的单★) 不该回滚本单已完成的落表 ⇒
#      ⇒ 本扫描【只报不判死】, 但必须【大声报】 ★
#   ③ ★**认领从 `state/issue_log.yaml` 查** ⇒ 红了要能说出【谁认领】⇒ 没认领的才需要 main 派单 ★

ALL_GATES = [
    ("HW/check_land_row_anchors.py", "行号锚点守卫"),
    ("HW/check_land_row_anchors.py --selftest", "行号锚点守卫 · 反向用例"),
    ("HW/check_netlist_selfconsistency.py", "现状守卫 (表A↔表B↔BOM↔图)"),
    ("HW/check_netlist_selfconsistency.py --selftest", "现状守卫 · 反向用例"),
    ("HW/check_netlist_contradiction_r3.py", "网表矛盾 R3"),
    ("HW/check_part_selection_landed_crosscheck.py", "选型落表交叉核对 (pad 序)"),
    ("HW/check_onepass_preflight_coverage.py", "一遍过 · 预检覆盖度"),
    ("HW/check_onepass_preflight_coverage.py --selftest", "一遍过 · 预检覆盖度 · 反向用例"),
    ("HW/check_onepass_commit_order.py", "一遍过 · 提交顺序"),
    ("HW/check_onepass_commit_order.py --selftest", "一遍过 · 提交顺序 · 反向用例"),
    ("HW/check_board_frame_caliber.py", "板框口径 (C6 走落表台账)"),
    ("HW/check_board_frame_caliber.py --selftest", "板框口径 · 反向用例"),
    ("state/check_netlist.py", "尺子1 · 网表"),
    ("state/check_netlist_pins.py", "尺子2 · 脚表"),
    ("state/check_sch_erc.py", "尺子3 · ERC"),
    ("state/check_sch_pinfull.py", "尺子4 · 图=表"),
    ("state/land_v_values.py --selftest", "落表器自测"),
    ("state/merge.py", "分片合并"),
    ("state/gate_check.py", "总闸"),
    ("state/issue_check.py", "issue 一致性"),
    ("state/check_chain_content_anchor.py", "链内容锚点"),
    ("state/chain_gate.py", "链闸"),
    ("MECH/check_board_frame_coords.py", "MECH · 板框坐标归一 (★归 ISS-286·不是本单的活★)"),
    ("SW/tools/timing_check.py", "SW · 时序 (★归 ISS-285·不是本单的活★)"),
]


def gate_owners(root: str, cmd: str) -> list[str]:
    """★查这道闸红了【有没有人认领】 (★从 `state/issue_log.yaml` 查·不猜★)"""
    p = os.path.join(root, "state", "issue_log.yaml")
    if not os.path.exists(p):
        return []
    try:
        import yaml
        with open(p, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception:
        return []
    script = cmd.split()[0]
    key = os.path.basename(script)
    hits: list[str] = []
    for it in (data.get("issues") or []):
        if not isinstance(it, dict):
            continue
        st = str(it.get("status") or "").lower()
        if st in ("closed", "done", "verified", "resolved"):
            continue
        blob = " ".join(str(it.get(k) or "") for k in
                        ("title", "desc", "note", "task_brief", "fix_ref"))
        if key not in blob and script not in blob:
            continue
        hits.append("%s (owner=%s · reporter=%s · status=%s)"
                    % (it.get("id"), it.get("owner"), it.get("reporter"), st))
    return hits


def scan_all_gates(root: str, timeout: int = 300) -> tuple[int, list[str]]:
    """★落表后【全闸扫描】 ⇒ (红的闸数, 报告文本) ★

    ★**只读·只报·不判死** ⇒ 别的单的闸红不回滚本单已完成的落表 (★口径见上★) ★
    """
    out_lines: list[str] = []
    reds: list[tuple[str, str, int]] = []
    for cmd, kind in ALL_GATES:
        argv = [sys.executable] + cmd.split()
        try:
            pr = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                                timeout=timeout)
            rc = pr.returncode
            tail = (pr.stdout or "").strip().split("\n")[-3:]
        except subprocess.TimeoutExpired:
            rc, tail = -1, ["★超时 (★%ds 没跑完★)" % timeout]
        except Exception as exc:
            rc, tail = -1, ["★跑不起来: %s" % exc]
        mark = "✅" if rc == 0 else ("★红★" if rc != 1 else "★预期红★")
        out_lines.append("   %s %-58s rc=%-3s (%s)" % (mark, cmd, rc, kind))
        if rc != 0:
            reds.append((cmd, kind, rc))
            for t in tail:
                if t.strip():
                    out_lines.append("        · %s" % t.strip())
            owners = gate_owners(root, cmd)
            out_lines.append("        ⇒ 认领: %s"
                             % (" / ".join(owners) if owners
                                else "★**无人在认领 ⇒ 需要 main 派单★**"))
    head = [
        "",
        "★★【★落表后全闸扫描 (★ISS-283 · ⑪·一次性跑完所有闸 + 列出红的 + 查有没有人认领★)】★★",
    ]
    tail = [
        "★★【全闸扫描结论】★★: 共 %d 道 · 红 %d 道" % (len(ALL_GATES), len(reds)),
    ]
    if reds:
        tail.append("★★**红的闸 (★不判死·但必须被看见★)**:")
        for cmd, kind, rc in reds:
            tail.append("   ★ %s  rc=%s  (%s)" % (cmd, rc, kind))
        tail.append("★**本扫描【只报不判死】** ⇒ 别的单的闸红 (★SW/MECH 侧在飞的单★) 不回滚本单已完成的落表 ★")
    else:
        tail.append("✅ 全闸皆绿")
    return len(reds), head + out_lines + tail


# ═══════════════════════════════════════════════════════════════════════════
# 9 · 落表器自测 (★--selftest★) —— ★★全在临时副本里做, 真盘零写入★★
# ═══════════════════════════════════════════════════════════════════════════

# ★★自测要搬进临时副本的文件 (★够干跑用就行, 不搬全工程★)★★
SELFTEST_FILES = [
    "state/gen_netlist.py",
    "HW/check_netlist_selfconsistency.py",
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
    # ★V-3 / V-4 的配方也要碰这几个 (★不然用例7 会被「缺文件」误杀★)★
    "HW/SCHEMATIC_V1_SPEC.json",
    "HW/CHARGE_BOARD_SPEC.md",
    "HW/NETLIST_SELF_CONSISTENCY_SPEC.md",
    "HW/SCHEMATIC_LANDING_V1_LANDED.md",
    # ★V-4 的配方要读 p10_rows.json (★不然用例7 会被「缺文件」误杀★)★
    "state/p10_rows.json",
    # ★★2026-11-17 复验新增: 回滚往返回用例要真跑一遍生成链 (★不然用例12 没法验「半回滚」★)★★
    "state/gen_kicad_net.py",
    "state/gen_netlist_pins.py",
    "state/gen_bom.py",
    "state/gen_schematic_pages.py",
    "HW/PCB/pinout_footprint.json",
    "HW/PCB/som_pin_assign.json",
    "HW/BOM_pseudo_refs_v1.csv",
    # ★★用例12 的【回滚后现状守卫】要读这几个 (★门禁 REL 里那几项根因层文件★)★★
    "HW/EMC_PRECHECK.md",
    "HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt",
    "HW/PCB/FET3572C_PIN_TABLE.csv",
    "HW/SCHEMATIC_LANDING_WORKPACKET_V1.md",
]

# ★★ISS-257 之前 (★占位串那一版★) 的 D_ESD_USB_D 两行 (★本轮实测的坏案例·必须当回归用例★)★★
SELFTEST_V2_OLD_BLOCK = (
    '    add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",\n'
    '        "ESD 阵列 [待选型] (USB 2.0 双通道)", "D", "必装", "[推算]", "",\n'
    '        "[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— '
    '★**Forlinx 载板指引要求 ESD 紧贴接口**", "A-24")\n'
    '    add("P1", "GND", "D_ESD_USB_D", "GND", "D_ESD_USB_D", "ESD 阵列 [待选型]", "D", "必装",\n'
    '        "[推算]", "", "[D_ESD_USB_D] ESD 地端", "A-24")\n'
)


def _sbx_copy(root: str, tag: str) -> str:
    """把自测要用的文件复制进一个临时目录 (★真盘只读★)。"""
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="land_v_selftest_%s_" % tag)
    for rel in SELFTEST_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(src):
            raise RuntimeError("★自测要用的文件不存在: %s" % rel)
        shutil.copy2(src, dst)
    return tmp


def _sbx_run(tmp: str, args: list[str]) -> tuple[int, str]:
    """在临时副本里跑一次落表器 (★子进程, 走真实命令行路径★)。"""
    cmd = [sys.executable, os.path.join(HERE, "land_v_values.py"), "--root", tmp] + args
    p = subprocess.run(cmd, capture_output=True, text=True,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _sbx_md5s(tmp: str) -> dict:
    out = {}
    for rel in ("HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro",
                "HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        fp = os.path.join(tmp, rel)
        out[rel] = md5(fp) if os.path.exists(fp) else "★(缺)★"
    return out


def _sbx_replace_block(tmp: str, new_block: str) -> None:
    """把临时副本里的 D_ESD_USB_D 那一段整块换掉 (★只动真源那一处★)。"""
    path = os.path.join(tmp, GEN_NETLIST)
    txt = read_text(path)
    ro = v2_read_source(tmp)
    if not ro["rows"]:
        raise RuntimeError("★自测: 真源里找不到 D_ESD_USB_D")
    old = ro["block"]
    if new_block is None:
        new_block = ""
    if old not in txt:
        raise RuntimeError("★自测: 真源里找不到那一块原文")
    txt = txt.replace(old, new_block, 1)
    write_text(path, txt)


def _sbx_unland(tmp: str, patches: list) -> None:
    """★把沙盒里的源码【退回落表前】 (★替换型: new → old★ · 删除型: 把删掉的块放回去★)

    ★★**为什么要它 (★ISS-283 · ⑩ 的直接后果★)** ★:
      V-2 / V-3 / V-4 都【已经落过表了】⇒
        · 「配方还认得当前真源吗」这个用例 ⇒ 必须在【退回落表前】的副本里跑 ★
        · 「回滚往返回」⇒ 也必须在【退回落表前】的副本里跑 (★不然根本没有东西可落·一落就崩★) ★
      ⇒ ★**不许把用例删掉** ⇒ ★**把副本退回落表前·让用例照样测得到** ★
    """
    cache: dict[str, str] = {}

    def load(p):
        if p.path not in cache:
            fp = os.path.join(tmp, p.path)
            cache[p.path] = read_text(fp) if os.path.exists(fp) else ""
        return cache[p.path]

    for p in patches:
        txt = load(p)
        if not txt:
            continue
        if p.new:
            _s, n = find_after(txt, p.ctx, p.new)
            if n == p.count:
                txt = replace_after(txt, p.ctx, p.new, p.old, p.count)
                cache[p.path] = txt
        else:
            if p.old in txt:
                continue
            m = re.search(r"^DEMO_DNP = \{\n", txt, re.M)
            if m:
                txt = txt[:m.end()] + p.old + txt[m.end():]
                cache[p.path] = txt
    for path, txt in cache.items():
        write_text(os.path.join(tmp, path), txt)


def _sbx_csv_set(tmp: str, rel: str, line: int, col: str, val: str) -> None:
    """★沙盒里改某个物理行的某一列 (★按 CSV 解析后重写·不做字符串硬替换★)"""
    fp = os.path.join(tmp, rel)
    lines = read_text(fp).split("\n")
    head = next(csv.reader([lines[0]]))
    vals = next(csv.reader([lines[line - 1]]))
    vals[head.index(col)] = val
    lines[line - 1] = ",".join('"' + v.replace('"', '""') + '"' if ("," in v or '"' in v) else v
                               for v in vals)
    write_text(fp, "\n".join(lines))


def _sbx_unland_v2(tmp: str) -> None:
    """★把沙盒里的 V-2 真源【退回落表前】 (★网名还在 SoM 侧那一版·落地后这一格变成【已落过】★)"""
    path = os.path.join(tmp, GEN_NETLIST)
    txt = read_text(path)
    new = 'add("P1", "NET_USB_D_P_TYPEC", "D_ESD_USB_D", "NET_USB_D_P_TYPEC", "D_ESD_USB_D",'
    old = 'add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",'
    if new in txt:
        txt = txt.replace(new, old, 1)
        write_text(path, txt)
    # ★网表 CSV 也要退回 (★v2_netlist_line 按 (ref, net) 找行·不然找不到行 ⇒ 配方判【状态漂移】★) ★
    fp = os.path.join(tmp, NETLIST_CSV)
    if not os.path.exists(fp):
        return
    lines = read_text(fp).split("\n")
    head = next(csv.reader([lines[0]]))
    for i in range(1, len(lines)):
        if not lines[i].strip():
            continue
        vals = next(csv.reader([lines[i]]))
        d = dict(zip(head, vals))
        if d.get("ref") == "D_ESD_USB_D" and d.get("net") == "NET_USB_D_P_TYPEC":
            vals[head.index("net")] = "USB_D_P_SRC"
            if "node2" in head and vals[head.index("node2")] == "NET_USB_D_P_TYPEC":
                vals[head.index("node2")] = "USB_D_P_SRC"
            lines[i] = ",".join('"' + v.replace('"', '""') + '"' if ("," in v or '"' in v) else v
                                for v in vals)
            write_text(fp, "\n".join(lines))
            return


def _sbx_unland_v5(tmp: str) -> None:
    """★把沙盒里的 V-5 真源【退回落表前】 (★Q_PG 三条 add() 换回旧顺序 + 网表 CSV 换回旧 pad 序★)"""
    path = os.path.join(tmp, GEN_NETLIST)
    txt = read_text(path)
    if V5_BLOCK_NEW in txt:
        txt = txt.replace(V5_BLOCK_NEW, V5_BLOCK_OLD, 1)
        write_text(path, txt)
    fp = os.path.join(tmp, NETLIST_CSV)
    if not os.path.exists(fp):
        return
    lines = read_text(fp).split("\n")
    head = next(csv.reader([lines[0]]))
    old_order = ["PWR_ON", "BAT_SW", "PWR_GOOD"]
    hits = []
    for i in range(1, len(lines)):
        if not lines[i].strip():
            continue
        vals = next(csv.reader([lines[i]]))
        d = dict(zip(head, vals))
        if d.get("ref") == "Q_PG":
            hits.append((i, vals))
    if len(hits) != 3:
        return
    for (i, vals), want_net in zip(hits, old_order):
        ni = head.index("net")
        vals[ni] = want_net
        if "node2" in head:
            n2 = head.index("node2")
            if vals[n2] == "J_CHG pin6":
                vals[n2] = "U_PWR_SW ON"
            elif vals[n2] == "U_PWR_SW pin2":
                vals[n2] = "U_PWR_SW ON"
            elif vals[n2] == "NET_BAT_SW":
                pass
        lines[i] = ",".join('"' + v.replace('"', '""') + '"' if ("," in v or '"' in v) else v
                            for v in vals)
    write_text(fp, "\n".join(lines))


def run_selftest(root: str) -> int:
    """★落表器自测 (★≥6 条反向用例★) ⇒ ★rc=0 = 全过★。"""
    import shutil
    import tempfile

    print("╔══ 落表器自测 (★--selftest★ · ★全在临时副本里做 · 真盘零写入★) ══╗")
    print(f"★ 工程根: {root}")
    print("")

    real_before = {rel: md5(os.path.join(root, rel)) for rel in SELFTEST_FILES
                   if os.path.exists(os.path.join(root, rel))}
    protected_before = {rel: md5(os.path.join(root, rel)) for rel in
                        ("HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro",
                         "HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")}

    cases = []
    tmps = []
    n_checks = [0]

    def new_case(name: str) -> tuple[str, str]:
        tmp = _sbx_copy(root, "c%d" % len(cases))
        tmps.append(tmp)
        cases.append((name, tmp))
        return tmp, tmp

    def check(name: str, ok: bool, detail: str = "") -> bool:
        mark = "✅" if ok else "★★"
        print(f"   {mark} {name}")
        if detail:
            for l in detail.strip().split("\n")[:12]:
                print(f"        {l}")
        n_checks[0] += 1
        return ok

    all_ok = True
    # ★★ISS-283 · B2: 用例 6 / 用例 8 会在沙盒里【故意】把 V-2 退回落表前 ⇒
    #   ⇒ 用例 10 (★每个用例跑完 5 个受保护 md5 逐字节不变★) 的比对基准要跟着改成
    #   ★**沙盒自己在【故意改动之后】的快照** ⇒ ★**否则 = 把【故意的改动】当成【自测写盘】★
    #   (★★这正是 2026-11-17 12:3x 实测撞到的: A3 落表后 V-2 真源已改 ⇒ 旧基准判红·假的★)★★
    sbx_base: dict = {}

    # ── 用例 1: ★本轮实测的坏案例 (★ISS-257 之前的占位串★) ⇒ V-2 路径必须立刻红 ──
    tmp, _ = new_case("regress_placeholder")
    _sbx_replace_block(tmp, SELFTEST_V2_OLD_BLOCK)
    rc, out = _sbx_run(tmp, ["--decision", "V-2=1"])
    all_ok &= check(
        "用例1 ★【回归·本轮实测坏案例】真源退回 ISS-257 之前的占位串 ⇒ V-2 必须红 (rc≠0) ★",
        rc != 0 and "型号轴未落" in out,
        f"rc={rc}\n{out.strip()[-700:]}")

    # ── 用例 2: ★已落过 ⇒ 必须红, 且文案必须说清【已落过】(不许与【状态漂移】混在一起)★ ──
    tmp, _ = new_case("already_landed")
    ro = v2_read_source(tmp)
    txt = read_text(os.path.join(tmp, GEN_NETLIST))
    txt = txt.replace('add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",',
                      'add("P1", "NET_USB_D_P_TYPEC", "D_ESD_USB_D", "NET_USB_D_P_TYPEC", "D_ESD_USB_D",', 1)
    write_text(os.path.join(tmp, GEN_NETLIST), txt)
    rc, out = _sbx_run(tmp, ["--decision", "V-2=1"])
    all_ok &= check(
        "用例2 ★【已落过】信号行已在 Type-C 侧 ⇒ 必须红 (rc≠0) 且文案写【已落过】★",
        rc != 0 and "已落过" in out,
        f"rc={rc}\n{out.strip()[-700:]}")

    # ── 用例 3: ★状态漂移 (★删掉 GND 那一行★) ⇒ 必须红且文案写【状态漂移】★ ──
    tmp, _ = new_case("drift")
    ro = v2_read_source(tmp)
    gnd = [r for r in ro["rows"] if r["net"] == "GND"][0]
    path = os.path.join(tmp, GEN_NETLIST)
    txt = read_text(path)
    txt = txt.replace(gnd["raw"] + "\n", "", 1)
    write_text(path, txt)
    rc, out = _sbx_run(tmp, ["--decision", "V-2=1"])
    all_ok &= check(
        "用例3 ★【状态漂移】真源少了一行 ⇒ 必须红 (rc≠0) 且文案写【状态漂移】★",
        rc != 0 and "状态漂移" in out,
        f"rc={rc}\n{out.strip()[-700:]}")

    # ── 用例 4: V-2=2 必须打回 ──
    tmp, _ = new_case("v2_2")
    rc, out = _sbx_run(tmp, ["--decision", "V-2=2"])
    all_ok &= check(
        "用例4 ★ V-2=2 (只落网表侧 = 假绿) 必须打回 (rc≠0) ★",
        rc != 0 and "必须打回" in out,
        f"rc={rc}\n{out.strip()[-400:]}")

    # ── 用例 5: 非法取值必须打回 ──
    tmp, _ = new_case("bad_value")
    rc, out = _sbx_run(tmp, ["--decision", "V-2=E2"])
    all_ok &= check(
        "用例5 ★ 非法取值 V-2=E2 必须打回 (rc≠0) ★",
        rc != 0 and "非法取值" in out,
        f"rc={rc}\n{out.strip()[-400:]}")

    # ── 用例 6: --apply 不带 --boss-decision 必须拒绝 ──
    #   ★★ISS-283 · B2: V-2 【已经落过表了】⇒ 要在【退回落表前】的副本里跑
    #   (★不然配方直接判【已落过】⇒ 压根走不到 boss-decision 那道闸·用例就失去意义·假的★) ★★
    tmp, _ = new_case("apply_no_boss")
    _sbx_unland_v2(tmp)
    sbx_base["apply_no_boss"] = _sbx_md5s(tmp)
    rc, out = _sbx_run(tmp, ["--decision", "V-2=1", "--apply"])
    all_ok &= check(
        "用例6 ★ `--apply` 不带 `--boss-decision` 必须拒绝 (rc≠0) ★",
        rc != 0 and "boss-decision" in out,
        f"rc={rc}\n{out.strip()[-400:]}")

    # ── 用例 7: ★V-3 / V-4 的锚点必须仍然是【当前真源】 (★从「碰巧成立」变成【被断言住】★) ──
    #   ★★ISS-283 · ⑩: V-3 / V-4 【已经落过表了】⇒ 这个用例要在【退回落表前】的副本里跑 ★★
    tmp, _ = new_case("v3_v4_anchor")
    _sbx_unland(tmp, WHITELIST["V-3"]["E"]("E", tmp).patches)
    _sbx_unland(tmp, WHITELIST["V-4"]["680"]("680", tmp).patches)
    rc3, out3 = _sbx_run(tmp, ["--decision", "V-3=E"])
    rc4, out4 = _sbx_run(tmp, ["--decision", "V-4=680"])
    all_ok &= check(
        "用例7 ★ V-3=E 与 V-4=680 的锚点必须仍然是【当前真源】 (各 rc=0) ★",
        rc3 == 0 and rc4 == 0,
        f"V-3=E rc={rc3} / V-4=680 rc={rc4}\n{out3.strip()[-200:]}\n{out4.strip()[-200:]}")

    # ── 用例 7b: ★★【已落过】(★V-3 / V-4 都落过了 ⇒ 必须【红】+ 文案写【已落过】·不许崩★)★★ ──
    tmp, _ = new_case("v3_v4_already_landed")
    rc7b, out7b = _sbx_run(tmp, ["--decision", "V-3=E"])
    rc7c, out7c = _sbx_run(tmp, ["--decision", "V-4=680"])
    all_ok &= check(
        "用例7b ★★【已落过】V-3=E / V-4=680 在已落过的真源上 ⇒ 必须红 (rc≠0) 且文案写【已落过】★",
        rc7b != 0 and rc7c != 0 and "已落过" in out7b and "已落过" in out7c,
        f"V-3=E rc={rc7b}\n{out7b.strip()[-400:]}\nV-4=680 rc={rc7c}\n{out7c.strip()[-400:]}")

    # ── 用例 8: ★绝不许把真型号降级成判据串 (★ISS-257 的成果不许被 undo★) ──
    #   ★★ISS-283 · ⑩: V-2 【已经落过表了】⇒ 要在【退回落表前】的副本里跑 (★不然配方直接判【已落过】★) ★★
    tmp, _ = new_case("no_downgrade")
    _sbx_unland_v2(tmp)
    sbx_base["no_downgrade"] = _sbx_md5s(tmp)
    rc, out = _sbx_run(tmp, ["--decision", "V-2=1"])
    new_lines = [l for l in out.split("\n") if l.strip().startswith("+ 新:")]
    # ★★降级判定 (★要精确: 旧 note 里本来就写着「ESD 阵列」, 那个不算降级★)★★
    downgrade = [l for l in new_lines
                 if ("ESD 阵列 (USB 2.0 双通道" in l) or ("[待选型]" in l)
                 or ('"[推算]"' in l)]
    keeps_model = any("TPD1E05U06DPYR" in l for l in new_lines)
    all_ok &= check(
        "用例8 ★ V-2 的 diff 新值行里【不许】出现判据串 / [推算] / [待选型] (★不许把真型号降级★) ★",
        rc == 0 and keeps_model and not downgrade,
        f"rc={rc}\n" + "\n".join(new_lines[:12]) + ("\n★降级行: %s" % downgrade if downgrade else ""))

    # ── 用例 9: ★换架构必须同时给型号 (★不许自己写判据串★) ──
    tmp, _ = new_case("arch_switch_needs_model")
    rc, out = _sbx_run(tmp, ["--decision", "V-2=1", "--v2-arch", "2"])
    all_ok &= check(
        "用例9 ★ `--v2-arch=2` 不给 `--v2-model` ⇒ 必须红 (★不许自己挑架构 / 自己写判据串★) ★",
        rc != 0 and "型号轴必须同时拍" in out,
        f"rc={rc}\n{out.strip()[-700:]}")

    # ── 用例 9b: ★V-5 / V-6 的白名单必须写死 (★只认老板拍的那一档★) ──
    tmp, _ = new_case("v5_v6_whitelist")
    rc5a, out5a = _sbx_run(tmp, ["--decision", "V-5=B"])
    rc6a, out6a = _sbx_run(tmp, ["--decision", "V-6=150R"])
    all_ok &= check(
        "用例9b ★ V-5=B / V-6=150R 必须打回 (★白名单写死·只认老板拍的那一档★) ★",
        rc5a != 0 and rc6a != 0 and "打回" in out5a and "打回" in out6a,
        f"V-5=B rc={rc5a}\n{out5a.strip()[-300:]}\nV-6=150R rc={rc6a}\n{out6a.strip()[-300:]}")

    # ── 用例 9c: ★V-5 / V-6 【已落过】⇒ 必须红 (★不许重复落·不许崩★) ──
    tmp, _ = new_case("v5_v6_already_landed")
    rc5b, out5b = _sbx_run(tmp, ["--decision", "V-5=A"])
    rc6b, out6b = _sbx_run(tmp, ["--decision", "V-6=20mA"])
    all_ok &= check(
        "用例9c ★★【已落过】V-5=A / V-6=20mA 在已落过的真源上 ⇒ 必须红 (rc≠0) 且文案写【已落过】★",
        rc5b != 0 and rc6b != 0 and "已落过" in out5b and "已落过" in out6b,
        f"V-5=A rc={rc5b}\n{out5b.strip()[-300:]}\nV-6=20mA rc={rc6b}\n{out6b.strip()[-300:]}")

    # ── 用例 9d: ★V-5 的落表动作必须是【写法A 的 pad 序】 (★在退回落表前的副本里跑★) ──
    tmp, _ = new_case("v5_landing_shape")
    _sbx_unland_v5(tmp)
    sbx_base["v5_landing_shape"] = _sbx_md5s(tmp)
    rc5c, out5c = _sbx_run(tmp, ["--decision", "V-5=A"])
    _newl = [l for l in out5c.split("\n") if l.strip().startswith("+ 新:")]
    all_ok &= check(
        "用例9d ★ V-5 的 diff 必须含【pad1=PWR_GOOD / pad2=BAT_SW / pad3=PWR_ON】三行 ★",
        rc5c == 0
        and any('"PWR_GOOD", "Q_PG", "J_CHG pin6"' in l for l in _newl)
        and any('"BAT_SW", "Q_PG", "NET_BAT_SW"' in l for l in _newl)
        and any('"PWR_ON", "Q_PG", "U_PWR_SW ON"' in l for l in _newl),
        f"rc={rc5c}\n" + "\n".join(_newl[:8]))

    # ── 用例 10: ★每个用例跑完, 5 个受保护 md5 必须逐字节不变 (★自测自己也不许写盘★) ──
    md5_ok = True
    detail = []
    for name, t in cases:
        now = _sbx_md5s(t)
        base = sbx_base.get(name) or protected_before
        for rel, h in now.items():
            if h != base.get(rel):
                md5_ok = False
                detail.append(f"{name}: {rel} 变了 ⇒ {h} (期望 {base.get(rel)})")
    all_ok &= check(
        "用例10 ★ 每个用例跑完, 5 个受保护 md5 必须逐字节不变 (★自测自己也不许写盘★) ★",
        md5_ok, "\n".join(detail))

    # ── 用例 11: ★真盘的 5 个受保护 md5 自测前后必须逐字节不变 ──
    real_ok = True
    detail2 = []
    for rel, h in protected_before.items():
        now = md5(os.path.join(root, rel))
        if now != h:
            real_ok = False
            detail2.append(f"{rel}: {now} (期望 {h})")
    for rel, h in real_before.items():
        now = md5(os.path.join(root, rel))
        if now != h:
            real_ok = False
            detail2.append(f"{rel}: {now} (期望 {h})")
    all_ok &= check(
        "用例11 ★ 真盘的 5 个受保护 md5 (+ 真源) 自测前后必须逐字节不变 ★",
        real_ok, "\n".join(detail2))

    # ── 用例 12: ★★【已落过】状态 ⇒ 必须判红 (★不许硬套补丁·不许崩★)★★ ──
    #   ★★2026-11-17 ISS-283 · ⑩ 实测的坑: V-3 / V-4 已经落过表 ⇒ 旧值出现 0 次
    #      ⇒ 老版用例 12 硬套补丁 ⇒ `RuntimeError: 旧值出现 0 次` ⇒ **崩** ★
    #   ⇒ ★**修法**: 配方先判【已落过】(⇒ 拒绝重复落 + 文案写【已落过】) ⇒ 用例 12 改成对【已落过】判红 ★
    tmp, _ = new_case("v3_already_landed")
    d12 = WHITELIST["V-3"]["E"]("E", tmp, "", "", "")
    plan12 = Plan(tmp, [d12])
    errs12 = plan12.verify()
    txt12 = " ".join(errs12)
    crash12 = None
    if not errs12:                 # ★**没落过才允许真的去套补丁** (★落了 ⇒ 不许硬套·不许崩★) ★
        try:
            plan12.apply_patches()
        except Exception as exc:
            crash12 = str(exc)
    all_ok &= check(
        "用例12 ★★【已落过】V-3=E 在已落过的真源上 ⇒ 必须判红 (文案写【已落过】) 且【不许崩】 ★",
        bool(errs12) and ("已落过" in txt12) and crash12 is None,
        f"verify 报错 {len(errs12)} 条:\n" + "\n".join(errs12[:6])
        + (f"\n★崩了: {crash12}" if crash12 else "\n★没崩 (★判红靠的是 verify 的错误·不是 RuntimeError★)"))

    # ── 用例 13: ★★【回滚往返回】(★与 V 值无关·合成补丁·不依赖任何一格「还没落」★)★★ ──
    #   ★★2026-11-17 复验实测到的坑: 老版 `--rollback` 只还原真源, 派生产物(网表/脚表/BOM)停在落表后
    #   ⇒ **半回滚** ⇒ 现状守卫 18 条 EXPECT 全红 (rc=1) ⇒ ⇒ 回滚后必须重生成派生产物
    #   ★★ISS-283 · ⑩: V-3/V-4/V-2 都已落过 ⇒ 「拿真配方跑一遍」的版本测不到了 ⇒ 改成【合成补丁】★★
    tmp, _ = new_case("rollback_roundtrip")
    rt_artifacts = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")
    pre = {rel: md5(os.path.join(tmp, rel)) for rel in rt_artifacts}
    gp = os.path.join(tmp, GEN_NETLIST)
    gtxt = read_text(gp)
    needle = '"[SYS] 开关引脚端去耦 (紧贴 VOUT, 承 SoC 上电冲击; 另一端接地)"'
    if needle not in gtxt:
        needle = '"[SYS] 开关引脚端去耦'
    idx = gtxt.find(needle)
    if idx < 0:
        all_ok &= check("用例13 ★【回滚往返回】★", False, "★沙盒里找不到用来合成补丁的 note 串★")
    else:
        bdir13 = backup_files(tmp, [GEN_NETLIST], "rt")     # ★**先备份** (★回滚要回到这一版★)★
        gtxt2 = gtxt[:idx] + '"★ISS283-ROLLBACK-TEST★' + gtxt[idx + 1:]
        write_text(gp, gtxt2)
        regen13 = regen_all(tmp)
        post = {rel: md5(os.path.join(tmp, rel)) for rel in rt_artifacts}
        landed_changed = any(post[rel] != pre[rel] for rel in rt_artifacts)
        rb_rc = do_rollback(tmp, bdir13)
        back = {rel: md5(os.path.join(tmp, rel)) for rel in rt_artifacts}
        roundtrip_ok = all(back[rel] == pre[rel] for rel in rt_artifacts)
        grc13, _gout = run([sys.executable, os.path.join(tmp, CHECK_SCRIPT)], tmp)
        all_ok &= check(
            "用例13 ★【回滚往返回】(★合成补丁·与 V 值无关★)落表⇒产物变⇒回滚⇒产物逐字节回到落表前 且 现状守卫回绿 (rc=0) ★",
            landed_changed and roundtrip_ok and rb_rc == 0 and grc13 == 0,
            f"落表后产物变了: {landed_changed}\n回滚后逐字节回去: {roundtrip_ok} "
            f"(pre={pre} / back={back})\n回滚 rc={rb_rc} · 现状守卫 rc={grc13}\n"
            f"重生成: {[(s, r) for s, r, _ in regen13]}")

    # ── 清理临时副本 ──
    for t in tmps:
        shutil.rmtree(t, ignore_errors=True)

    print("")
    print("★★【自测用例汇总】★★")
    for i, (name, _t) in enumerate(cases, start=1):
        print(f"   {i}. {name}")
    n = len(cases)
    print(f"   {n + 1}. ★每个用例跑完 5 个受保护 md5 逐字节不变★")
    print(f"   {n + 2}. ★真盘 5 个受保护 md5 自测前后不变★")
    print("")
    if all_ok:
        print(f"✅ rc=0: ★**落表器自测全过 ({n_checks[0]} 条) · 真盘零写入** ★")
        return 0
    print("★★ rc=1: ★**落表器自测有红的** ★", file=sys.stderr)
    return 1
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
    ap.add_argument("--selftest", action="store_true",
                    help="★落表器自测 (★≥11 条反向用例·全在临时副本里做·真盘零写入★)")
    ap.add_argument("--v2-arch", default="",
                    help="★V-2 的【架构轴】(★A3 / W-1 裁★): 1=2脚单通道 · 2=3脚双通道 · 3=2脚双向件 "
                         "★**不给 = 按真源现状走 (★落表器不替你选架构★)**")
    ap.add_argument("--v2-model", default="",
                    help="★V-2 的【型号轴】(★选型级·老板拍★): 真 OPN 串 (★不给 = 真源现值原样保住★)")
    ap.add_argument("--v2-evidence", default="",
                    help="★配合 `--v2-model` 用的 evidence 等级 (★[官网] / [实测] / [推算]★)")
    ap.add_argument("--issue", default="ISS-236",
                    help="★落表单号 (★写进落表台账的 §16 抬头 + 身份变更授权记录·默认 = 落表器自己的单号★)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "state")):
        print(f"★★ rc=2: 工程根不对: {root}", file=sys.stderr)
        return 2

    if args.rollback:
        return do_rollback(root, os.path.abspath(args.rollback))

    if args.selftest:
        return run_selftest(root)

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
        decisions.append(WHITELIST[v][val](val, root, args.v2_arch, args.v2_model, args.v2_evidence))

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
    if plan.readout:
        print("★★【★V-2 两轴读数 (★架构 / 型号 分开列·不混成一句★)】★★")
        for l in plan.readout:
            print(f"   {l}")
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
        m = re.match(r"^\s*(\d{4}-\d{2}-\d{2})\s+(A1|A2|A3|A4|A5)\s*=\s*(\S+)\s*$", b)
        if not m:
            print(f"★★ rc=2: ★**`--boss-decision` 写法不对: {b!r}** ⇒ "
                  f"必须是 \"<日期> <A1|A2|A3|A4|A5> = <值>\" (★例: \"2026-11-16 A1 = E\"·"
                  f"\"2026-11-17 A4 = A\"·\"2026-11-17 A5 = 20mA\"★) ★", file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2
        boss.append((m.group(1), m.group(2), m.group(3)))
    if not boss:
        print("★★ rc=2: ★**`--apply` 必须带 `--boss-decision \"<日期> <A1|A2|A3> = <值>\"`** ★", file=sys.stderr)
        print("   ★**这是「不许替老板拍板」的机器化保证 ⇒ 缺这条就拒绝执行** ★", file=sys.stderr)
        print("★★ ★**零写盘** ★", file=sys.stderr)
        return 2
    # ★★拍板码 → 拍板项 (★DECISION_PENDING_2026-11-16.md §A: A1=V-3 · A2=V-4 · A3=V-2★) ★★
    # ★★ISS-283 · B2/B3: A4 = V-5 (W-4 / G-1 写法A) · A5 = V-6 (G-5 / W-6 20mA 亮度档) ★★
    A_ITEM = {"A1": "V-3", "A2": "V-4", "A3": "V-2", "A4": "V-5", "A5": "V-6"}
    # ★★A3 (V-2) 的凭据可以带【覆盖】(★架构 / 型号两轴★)★★
    A3_EXTRA = re.compile(r"^1(?:/arch=(?P<arch>[123]))?(?:/model=(?P<model>.+))?$")
    boss_map: dict[str, str] = {}
    boss_cover: dict[str, tuple[str, str]] = {}
    for _d, _c, _v in boss:
        _item = A_ITEM[_c]
        if _item == "V-2":
            m3 = A3_EXTRA.match(_v)
            if not m3:
                print(f"★★ rc=2: ★★A3 的取值 {_v!r} 写法不对** ⇒ "
                      f"★只认 `1` (★两段走 · 架构 / 型号按真源现状★) 或 "
                      f"`1/arch=<1|2|3>/model=<真 OPN>` (★显式覆盖两轴★)★", file=sys.stderr)
                print("★★ ★**零写盘** ★", file=sys.stderr)
                return 2
            boss_cover["V-2"] = (m3.group("arch") or "", m3.group("model") or "")
            _v = "1"
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

    # ── ⑤b V-2 的两轴覆盖 (★要求 `--boss-decision` 同时覆盖架构 + 型号★) ──
    v2d = next((d for d in decisions if d.v == "V-2"), None)
    if v2d is not None:
        _arch, _model = boss_cover.get("V-2", ("", ""))
        _changed = (v2d.v2_arch != v2d.v2_src_arch) or (v2d.v2_model != v2d.v2_src_model)
        if _changed and not (_arch and _model):
            print(f"★★ rc=2: ★★本次 V-2 落表要动【架构 / 型号】两轴** ⇒ "
                  f"★**`--boss-decision` 必须同时覆盖两轴** (★不许只写 `A3 = 1`★) ⇒ ", file=sys.stderr)
            print(f"   ★**写法**: \"<日期> A3 = 1/arch={v2d.v2_arch}/model={v2d.v2_model}\" ★",
                  file=sys.stderr)
            print(f"   ★**本次实际落表**: 架构 ★**{v2d.v2_arch}** ★ · 型号 ★**{v2d.v2_model}** ★",
                  file=sys.stderr)
            print(f"   ★**真源现状**: 架构 ★**{v2d.v2_src_arch or '★(读不出来)★'}** ★ · "
                  f"型号 ★**{v2d.v2_src_model or '★(读不出来)★'}** ★", file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2
        if _arch and _arch != v2d.v2_arch:
            print(f"★★ rc=2: ★★凭据里写的架构 {_arch!r} 与本次落表实际用的 "
                  f"{v2d.v2_arch!r} 对不上** ⇒ ★**凭据必须与命令行 `--v2-arch` 一致** ★", file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2
        if _model and _model != v2d.v2_model:
            print(f"★★ rc=2: ★★凭据里写的型号与本次落表实际用的对不上** ⇒ "
                  f"★**凭据必须与命令行 `--v2-model` 一致** ★", file=sys.stderr)
            print("★★ ★**零写盘** ★", file=sys.stderr)
            return 2

    # ── ⑥ 备份 (★有回滚★) ──
    touched = sorted({p.path for p in plan.patches} | {CHECK_SCRIPT, SPEC_PAGE, LANDED_LEDGER,
                                                       ANCHOR_GUARD, REGISTRY_JSON})
    old_md5 = {p: md5(os.path.join(root, p)) for p in touched if os.path.exists(os.path.join(root, p))}
    old_md5.update({p: md5(os.path.join(root, p)) for p, _ in MD5_TARGETS
                    if os.path.exists(os.path.join(root, p))})
    bdir = backup_files(root, touched, "v")
    print(f"★★ 回滚副本: {os.path.relpath(bdir, root)} ★★")

    try:
        # ── ★★ISS-283 · B1: 落表前先让行号锚点守卫把台账的 `id_str` 补齐 (★机器写★) ──
        #   ★★**为什么必须先补 (★2026-11-17 12:12 实测·不是推测★★)**:
        #     守卫判「实体身份变了 (ref+net)」时, 要拿【旧身份】去落表台账的授权记录里比对
        #     ⇒ 【旧身份】的来源 = registry 的 `id_str` (★落表改完之后按行号回查必然查不到★)
        #     ⇒ ★**不补 ⇒ 合法落表必判红 (NOOLD) ⇒ 落表器自回滚 ⇒ 合法落表这条路走不通★★
        #   ★**这一段是【机制】不是【一次性补丁】** ⇒ 以后每次落表都自动走一遍 ⇒ 不会再踩同一个坑 ★★
        _mg = [sys.executable, os.path.join(root, ANCHOR_GUARD), "--migrate-id-str"]
        rc_mg, out_mg = run(_mg, root)
        for l in out_mg.strip().split("\n")[-4:]:
            if l.strip():
                print(f"   ★ {l}")
        if rc_mg != 0:
            raise RuntimeError(f"★行号锚点守卫的台账 `id_str` 补齐失败: rc={rc_mg}\n{out_mg[-1500:]}")
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
        append_ledger(root, decisions, [f"{b[0]} {b[1]} = {b[2]}" for b in boss], old_md5,
                      issue=args.issue)
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
        # ★★ISS-262 (2026-11-17 · hw-lead): 行号锚点守卫 (★纯漂移 ⇒ 机器重锚 + 打印新行号★)
        #   ⇒ ★**落表后【行号整体位移】不再是无声无息** ★ ⇒ ★**锚点行号由机器改, 不许人手改** ★
        ([sys.executable, os.path.join(root, "HW/check_land_row_anchors.py"), "--reanchor"],
         "★行号锚点守卫 (ISS-262 · 纯漂移自动重锚·期望 rc=0)★"),
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

    # ── ★★ISS-283 · ⑪: 落表后【全闸扫描】 (★一次性跑完所有闸 + 列出红的 + 查有没有人认领★) ──
    #   ★**为什么不能省 (★main 2026-11-17 11:2x 实跑抓出来的病灶★)**:
    #     落表前全绿 · 落表后 3 道红 · 其中 2 道【落表前谁都没料到】⇒ 手工扫一定会漏 ⇒ 必须机制化 ★
    #   ★**口径: 只报不判死** ⇒ 别的单的闸红 (★SW/MECH 侧在飞的单★) 不回滚本单已完成的落表 ★
    n_red, scan_txt = scan_all_gates(root)
    for l in scan_txt:
        print(l)
    print(f"   ★ 全闸扫描: 红 {n_red} 道 (★只报不判死·不回滚★)")

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
    print(f"★★ 落表单号: ★**{args.issue}** ★ · 老板拍板凭据: {', '.join(f'{b[0]} {b[1]} = {b[2]}' for b in boss)}")
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
