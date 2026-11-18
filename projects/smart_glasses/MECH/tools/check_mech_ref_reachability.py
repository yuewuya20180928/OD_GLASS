#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/tools/check_mech_ref_reachability.py — ISS-333 · MECH 侧位号引用可达性闸
===================================================================================================
★★**这道闸判的是什么东西** ★ (★ISS-326 设计稿 §0-①·本单把它变成能挂的闸★):

  ★**义务 (逐字)**★: ★MECH 域每份文档 / 每个判据脚本里引用的每个位号, 必须能在【板文件】或【网表】里找到★
    ⇒ ★找不到 ⇒ 判红★ ⇒ ★并逐条列出「哪个文件 / 哪一行 / 引用的是谁 / 板与网表里现在叫什么」★

★★★**★为什么必须有这道闸 (★ISS-326 实测·不是设计稿的自嗨★)** ★:
  ★**ISS-326 (verified) 实测: 「板只改一次」那一趟 (S1) 会给 186 个板位号改名 (加 `_1` 后缀)** ★
    ⇒ ★**MECH 域引用到的改名位号有 68 个** ★ ⇒ ★改完板, MECH 侧文档/判据脚本里的位号就【对不上板了】★ ★
    ⇒ ★**而 ISS-326 自己的沙盒实测出了「假绿」**: 判据脚本里的精确等值分支 `== "R_SEL_D0_N"` 失配后,
      ★**那条判据静悄悄不查了, 但脚本整体照样全绿** ⇒ ★缺陷对闸隐形★ ★
    ⇒ ★⇒ 这道闸就是 MECH 域的护栏: ★它必须能抓到「板改名了 / 脚本字面量没跟着改」★ ★

★★★**★R1 · 判据方向 (★不可改★)** ★ ★:
  ★**只问「你引用的位号现在存在吗」** ★ ⇒ ★**判据里不许写死「位号改名」这个具体方案** ★
    ⇒ ★**S1 走①还是走③, 这道闸都不用改** ★ ⇒ ★正向用例 MC-2 专门证明这一点★**

★★★**★R2 · 分类口径 (★零漂移的做法★)** ★:
  ★**只读 import `SW/tools/check_sw_ref_reachability.py`, 直接复用它的 `TOKEN_PREFIXES` / `read_board_refs` /
  `read_netlist_refs` / `read_net_names` / `classify`** ★ ⇒ ★MECH 版与 SW 版对同一盘面永远给同一个答案★ ★
  ★**MECH 侧只加三条 (C15 / C16 / C17), 不改 SW 那 14 条里的任何一条** ★ ★

  | 类 | 含义 | 判红? |
  |---|---|---|
  | `DESIGNATOR_OK` | ★**真位号** · 现在能在板/网表里找到★ | 否 |
  | `DESIGNATOR_DRIFT` | ★**真位号** · 建闸时在板上 · 现在找不到了 (★改名漂移★) | ★**是** ★ |
  | `DESIGNATOR_MISSING` | ★**真隐患** · 形状像位号 · 板/网表里从来没有过 | ★**是** (★计入基线★) |
  | `NET_NAME` | ★**电源轨名 / 逻辑信号名** ⇒ 它本来就不是位号 | 否 |
  | `DOC_INTERNAL` | ★**文档/代码自己的编号** (文档互引 / 锚点 / 环境变量键 / 物理符号 / 家族统称 / ★**代码常量名 (C15)**★ / ★**裸编号 (C16)**★ / ★**已登记的非位号 (C17)**★) | 否 |

★★★**★R3 · 建闸日基线 (★MECH 侧自己 fresh 测, 不许抄 SW 的 3★)** ★:
  ★**ISS-326 建闸日 (2026-11-18) 实测 = 16** ★ (60 原始 C14 → 剔 4 自污染 → 剔 40 py 变量名)
  ★**ISS-333 今天 (2026-11-18 晚) 复现 = 15** ★ (口径细化后的重算, 逐条差异见交卷页 §B2-2)
  ⇒ ★**本闸的基线上限 = 15 (★比 ISS-326 的 16 紧 1 条 ⇒ 符合「基线只许收紧不许放宽」★)** ★
  ⇒ ★**每一条都写明「为什么它本来就该对不上」** ★ (★照抄 SW 的 `BASELINE_TOKENS` 口径★)

★★★**★R4 · 反向用例 (★14 条, 含「假绿」那条★)** ★:
  ★`--selftest` ⇒ ★每条带「不是巧合」自证 (★同一棵沙盒树·破坏前必须 rc=0★)★ ★

★★★**★R5 · fail-closed (★三条 + 一条扩展★)** ★:
  ① 板文件读不到 ⇒ 判红 ② 网表读不到 / 没有 `ref` 列 ⇒ 判红
  ③ 扫描面拿不到 ⇒ 判红 ★**扩展条: `MECH/**/*.md` 与 `MECH/**/*.py` 【各自】非空, 且 token 总数 > 0** ★
  ④ ★**判据分支匹配不上 ⇒ 判红 (★不许「静悄悄不查了」★)** ★ ⇒ ★`RULE_PROBES` 分支自检, 每次跑都验一遍★ ★
  ⇒ ★**不许「没读到就当过」** ⇒ ★**失效方向是安全的: 红, 不是假绿** ★

★★★**★R6 · 边界 (★本闸自己也要守★)** ★:
  · ★**零写板** (只读板文件文本, 不 import pcbnew, 不跑 KiCad) ★
  · ★**零落表** (只读网表 CSV, 不写) ★
  · ★**零改既有闸** (★本文件是【新建】的一道闸, 不碰 `state/gate_check.py`★) ★
  · ★**零改既有 MECH 文档/脚本正文** (只读; 沙盒一律真拷贝, 绝不 hardlink/软链) ★
  · ★**扫描面排除闸自身** (`MECH/tools/check_mech_ref_reachability.py` ⇒ 闸不查自己, 免得自污染) ★

用法:
    python3 MECH/tools/check_mech_ref_reachability.py                        # 主模式: rc=0 = 引用全部可达
    python3 MECH/tools/check_mech_ref_reachability.py --dump-classification  # 打印全部分类
    python3 MECH/tools/check_mech_ref_reachability.py --selftest             # 反向用例 (14 条)
    python3 MECH/tools/check_mech_ref_reachability.py --root .               # 指定项目根
    python3 MECH/tools/check_mech_ref_reachability.py --freeze-registry --confirm-freeze   # ★重建冻结表★
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# ★**输入面 (★只读★)** ★
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
NETLIST_CSVS = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")
# ★**扫描面 (★递归·不许只扫顶层·ISS-326 实测 113 份 = 48 md + 65 py★)** ★
MECH_MD_GLOB = "MECH/**/*.md"
MECH_PY_GLOB = "MECH/**/*.py"
# ★**闸自身排除 (★免得这道闸把自己带红·ISS-326 自污染事故的同款根治★)** ★
SELF_GATE_REL = "MECH/tools/check_mech_ref_reachability.py"


# =================================================================================================
# §R2-0 · ★只读 import SW 侧那道闸 ⇒ 口径零漂移★ (★本文件一个字都不改它★)
# =================================================================================================
def _load_sw_gate(root: str):
    """★只读 import `SW/tools/check_sw_ref_reachability.py` ⇒ 复用它的口径函数★"""
    path = os.path.join(root, "SW", "tools", "check_sw_ref_reachability.py")
    if not os.path.isfile(path):
        raise SystemExit(f"[mech-gate] ★SW 侧那道闸读不到 (口径零漂移的前提没了): {path}")
    spec = importlib.util.spec_from_file_location("sw_ref_reachability_gate", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sw_ref_reachability_gate"] = mod
    spec.loader.exec_module(mod)
    return mod


sw = _load_sw_gate(DEFAULT_ROOT)

# ★**口径函数直接复用 (★不许抄一份改改★)** ★
TOKEN_PREFIXES = sw.TOKEN_PREFIXES
read_board_refs = sw.read_board_refs
read_netlist_refs = sw.read_netlist_refs
read_net_names = sw.read_net_names
InputError = sw.InputError

# ★**token 宇宙 (★声明式·不写死任何具体位号★)** ★
#   · 前 16 个 = ★SW 侧的 16 个前缀 (★照抄·口径零漂移★)★ ★
#   · ★C16 追加: 裸编号位号 (`Q1` / `Q2` / `X1`)★ —— ★但只收【live 或已登记】的, 否则 MECH 域的
#     `Q3/Q4/Q7/Q9/Q13` (老板的问题编号) 与 `X0/X11/X15/X19/X52` (坐标轴变量) 会变成 10 条假绿★
TOKEN_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")
BARE_NUMBER_RE = re.compile(r"\b(?:Q|X)\d+\b")

# ★**ISS-333 实测 (2026-11-18 本机实跑)**: MECH 域里 `Q\d+` / `X\d+` 共 13 个, 其中只有 3 个是真位号★ ★
#   ⇒ ★C16 只放这 3 个进扫描面★ ⇒ 其余 10 个 (Q3/Q4/Q7/Q9/Q13/X0/X11/X15/X19/X52) 归 C16「文档自己的编号」★
# ★**注意 `X1` 在 MECH 文档里【既是真位号也是坐标轴变量】⇒ 它是 live ⇒ 走 C1 ⇒ 不判红 (★已实测★)** ★

# =================================================================================================
# §R3 · 建闸日基线 (★MECH 侧自己 fresh 测·2026-11-18 本机实跑·不许抄 SW 的 3★)
# =================================================================================================
# ★**ISS-326 建闸日实测 = 16** ★ (60 原始 C14 → 剔 4 自污染 → 剔 40 py 变量名)
# ★**ISS-333 今天实测 = 10** ★ (口径细化后的重算 ⇒ ★比 16 紧 6 条 ⇒ 符合「只许收紧不许放宽」★)
# ★**逐条理由见交卷页 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` §B2-2** ★
BASELINE_COUNT = 10

# ★**建闸日冻结值 (★反放宽护栏: 本闸的 BASELINE_COUNT 不许超过它★)** ★
#   ★**为什么要有这条**: 「基线只许收紧不许放宽」是项目铁律 ⇒ ★光靠「不许改」是口头约定★
#   ⇒ ★机械化成一条【闸自己会判红】的检查: BASELINE_COUNT > 本常量 ⇒ 判红★ ★
BASELINE_COUNT_BUILDDAY = 10

# ★**逐条理由 (★为什么这一条「本来就该对不上」★)** ★
BASELINE_TOKENS = {
    "CONN_USB": (
        "★真隐患·已登记★: MECH 域 77 处引用 CONN_USB (FPC_FAB_NOTES / HINGE_FPC_GEOMETRY_TRUTH / HW_CROSS_REVIEW …) "
        "⇒ ★板上是 J_USB_C, 网表里只有 CONN_CAM / CONN_LIGHT ⇒ 「USB 连接器」这个对象在盘上已经换名/消失, "
        "MECH 侧的引用还留着 ⇒ 板那一趟若改这些位号, MECH 侧会一起漂移★"
    ),
    "C_VBUS_BULK": (
        "★真隐患·已登记★: MECH/STRUCT_REVIEW_ISS065.md §I-6 明写「`C_BULK`/`C_VBUS_BULK` 与 `C_VBUS_IN` 的位号在 netlist 里对不上 "
        "(脚本按 `C_VBUS_BULK` 算 1206, 但 netlist 里只有 `C_VBUS_IN`/`C_VBUS_OUT`/`C_SYS`)」⇒ ★判据脚本引用了一个盘上没有的位号★"
    ),
    "D_ESD_CHG": (
        "★真隐患·已登记★: MECH/cross_review_check.py:103 的 ESD 假设 dict 里写死 \"D_ESD_CHG\": 1.6 * 0.8 ⇒ "
        "★板上/网表里的 D_ESD_* 只有 D_ESD_CAM / D_ESD_DEMO / D_ESD_LIGHT / D_ESD_TC / D_ESD_USB_D ⇒ "
        "★判据脚本假设了一个不存在的 ESD 位号★ (★它只出现在 .py 里, ISS-326 的「py-only 粗口径」把它一起扫掉了 ⇒ 本闸口径把它捡回来★)"
    ),
    "J_CHG_A": (
        "★真隐患·已登记★: MECH/HW_CROSS_REVIEW.md §R-10「`J_CHG` 实物是一对, 网表只有一行」⇒ 处置写明「拆 `J_CHG_A`/`J_CHG_B` 两个 ref」⇒ "
        "★文档里已经写了这两个位号, 但它们还没落表 ⇒ 落表之前它们就是解析不到的★"
    ),
    "J_CHG_B": (
        "★真隐患·已登记★: 同 §R-10 ⇒ ★待与 `J_CHG_A` 同批落表 (★hw-lead owner★)"
    ),
    "J_CHG_PWR": (
        "★真隐患·已登记★: MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 的位号不符表里写明「主板侧改名 (如 `J_CHG_PWR`) 并同步 BOM/网表 (触落表, 须 main 批准)」⇒ "
        "★它是【拟用名】, 还没落表 ⇒ 现在解析不到是对的, 落表后才解析得到★"
    ),
    "J_JTAG": (
        "★真隐患·已登记★: MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md §位号不符表: 脚本用 `J_JTAG`, 盘上是 `J_DEBUG` ⇒ "
        "★位号名不符 ⇒ 按 params 生成的 land pattern 找不到器件 ⇒ hw-lead owner★"
    ),
    "J_USB": (
        "★真隐患·已登记★: 同表: 脚本用 `J_USB`, 盘上是 `J_USB_C` ⇒ ★位号名不符 ⇒ 同上★"
    ),
    "R_PU_STAT_L": (
        "★真隐患·已登记★: MECH/STRUCT_REVIEW_ISS065.md §R1「充电灯的驱动 `Q_CHG_LED` 栅极 = `U_CHG pin4` (本地 STAT, 开漏) + `R_PU_STAT_L` (本地上拉到 REGN 5V)」⇒ "
        "★MECH/iss065_check.py:374 的 T-3c 面积账也把它算进去了 ⇒ 板/网表里没有这个位号 ⇒ 真隐患★"
    ),
    "U_SOM_RK3572": (
        "★真隐患·已登记★: MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 的位号不符表明写「★**板上没有这个位号; 板上是 `J_SOM_P1..P4` "
        "(4 组 × 100 焊盘 = 400)★」⇒ ★位号 + 拓扑都不符 ⇒ hw-lead owner★"
    ),
}

# =================================================================================================
# §C17 · MECH_NON_DESIGNATOR_REGISTRY (★已登记的「不是位号引用」·与基线分开记账★)
# =================================================================================================
# ★**为什么要把它跟基线分开 (★这是本单对 ISS-326 设计稿的一处口径细化★)** ★:
#   ★**基线 = 「真隐患的容许上限」** ⇒ ★它该装的只有【真隐患】★ ★
#   ★**C17 = 「压根不是位号引用」** ⇒ ★装进去的每一条都有【盘上的书面证据】⇒ ★它们不该占真隐患的额度★ ★
#   ★**机械效果**: ISS-326 的 16 ⇒ 本闸的 10 ⇒ ★上限收紧 6 条, 而这 6 条不是「被人偷偷放宽掉的」★
#     ⇒ ★是【被更准的规则摘出去了】⇒ ★逐条理由见交卷页 §B2-2★ ★
MECH_NON_DESIGNATOR_REGISTRY = {
    # —— ISS-326 审计文档里的【故意写的假位号 / S1 新名示例】 ——
    "CONN_CAM_1": (
        "★非位号·已登记★: MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md §改名影响面里写的 S1 新名示例 (`CONN_CAM` → `CONN_CAM_1`) "
        "⇒ ★它是【文档在讲改名这件事时用的例子】, 不是一条位号引用★"
    ),
    "D_LED_G_1": (
        "★非位号·已登记★: 同文档里 S1 新名示例 (`D_LED_G` → `D_LED_G_1`) ⇒ ★同上★"
    ),
    "CONN_USB_ISSX": (
        "★非位号·已登记★: 同文档 §假绿分类表里的假位号 (★ISS-326 自己的反向测试夹具假位号★) ⇒ ★不是引用★"
    ),
    "TP_TEMP_ISSX": (
        "★非位号·已登记★: 同文档里的假位号 (ISS-326 反向测试夹具) ⇒ ★不是引用★"
    ),
    "TP_TEMP_ISSX2": (
        "★非位号·已登记★: 同文档里的假位号 (ISS-326 反向测试夹具) ⇒ ★不是引用★"
    ),
    "U_TEMP_1": (
        "★非位号·已登记★: 同文档里的假位号 (ISS-326 反向测试夹具) ⇒ ★不是引用★"
    ),
    # —— 物理量 / 代码常量 (★ISS-326 审计文档 §2-2 自己点名的 C15 例子★) ——
    "R_DCR": (
        "★非位号·已登记★: MECH/MECH_BUDGET.md §耗散口径 与 MECH/verify_budget.py 里的 `R_DCR` = 电感【铜损热阻 (mΩ)】⇒ "
        "★是物理量, 不是位号★ (★ISS-326 审计文档 §2-2 明写「判据脚本里大量用『形状像位号』的变量名 (`R_ILIM_VALUES` / `LED_REF` / `R_DCR` / `C_CASES`) ⇒ 它们不是位号」★)"
    ),
    "R_ILIM_VALUES": (
        "★非位号·已登记★: MECH/HINGE_POWER_CALC.md 引用的 `R_ILIM_VALUES` = 限流电阻候选档表【代码常量名】⇒ "
        "★ISS-326 审计文档 §2-2 点名的 C15 例子之一⇒ 不是位号★"
    ),
    "R_TIM": (
        "★非位号·已登记★: MECH/CENTER_CAVITY_REBALANCE_V2/V3.md 的 `R_TIM = 33.333 / A_m` = 导热垫【热阻 (K/W)】⇒ "
        "★是物理量公式, 不是位号★"
    ),
    # —— JSON 里的【场景 id】(★真位号在兄弟字段 `ref` 里★) ——
    "LED_G_WINDOW": (
        "★非位号·已登记★: MECH/BOARD_ONEPASS_MECH_SYNC.md 的 `led.id` = ★场景 id★ ⇒ 同对象的 `\"ref\": \"D_LED_G\"` 才是位号 ⇒ 不是位号引用★"
    ),
    "LED_G_HOLE_A": (
        "★非位号·已登记★: 同文件 `led.hypothesis_hole.id` = ★场景 id (有结构光孔)★ ⇒ 不是位号引用★"
    ),
    "LED_G_NOHOLE_B": (
        "★非位号·已登记★: 同文件 `led.hypothesis_nohole.id` = ★场景 id (无结构光孔)★ ⇒ 不是位号引用★"
    ),
}

# =================================================================================================
# §C2 · MECH_DESIGNATOR_REGISTRY (★建闸日冻结的「真位号」集合·78 条★)
# =================================================================================================
# ★**为什么要有这张表 (★与 SW 那道闸同款·不是多余的保险★)** ★:
#   ★**场景**: MECH 侧判据脚本里写死 `LED_REF = "D_LED_G"` ⇒ ★S1 改名之后板变成 `D_LED_G_1`★
#   ⇒ ★那行代码就会去查一个不存在的 key ⇒ ★脚本崩 / 判据静悄悄失配 (ISS-326 实测的假绿)★ ★
#   ⇒ ★**冻结表的作用**: 「这些 token 在建闸日【确确实实是位号】」⇒ ★改名之后它们必须仍然解析得到★
#   ⇒ ★**不是巧合, 是设计** ★
# ★**重建命令**: `python3 MECH/tools/check_mech_ref_reachability.py --freeze-registry --confirm-freeze` ★
# ★**★重建的触发条件 = 【盘面改过位号】, 不是【闸红了就重建】★ (★main 对 ISS-327 need #1 的拍板·写进本闸护栏★)** ★
MECH_DESIGNATOR_REGISTRY = (
    "BT_432243",
    "CONN_CAM",
    "CONN_LIGHT",
    "C_AC_CSI_D0_D3_P",
    "C_BAT",
    "C_BST",
    "C_KEY_CAM",
    "C_PMID",
    "C_REGN",
    "C_SYS",
    "C_VBUS_GND",
    "C_VBUS_IC",
    "C_VBUS_IN",
    "C_VBUS_OUT",
    "D_CHG_LED",
    "D_ESD_LIGHT",
    "D_ESD_TC",
    "D_LED_B",
    "D_LED_G",
    "D_LED_R",
    "FB_VBUS",
    "J_BOOT1",
    "J_CHG",
    "J_DEBUG",
    "J_SOM_P1",
    "J_SOM_P2",
    "J_SOM_P3",
    "J_SOM_P4",
    "J_TYPE_C",
    "J_UART",
    "J_USB_C",
    "L_CHG",
    "Q1",
    "Q2",
    "Q_CHG_LED",
    "R_CHG_LED",
    "R_ILIM",
    "R_LED_B",
    "R_LED_G",
    "R_LED_R",
    "R_NTC_BAT",
    "R_PU_I2CB_SCL",
    "R_PU_INT",
    "R_PU_SCL",
    "R_PU_SDA",
    "R_SEL_CK_N",
    "R_SEL_CK_P",
    "R_SEL_D0_N",
    "R_SEL_D0_P",
    "R_SEL_D1_N",
    "R_SEL_D1_P",
    "R_SEL_D2_N",
    "R_SEL_D2_P",
    "R_SEL_D3_N",
    "R_SEL_D3_P",
    "R_STAR_PGND",
    "R_TS_PULL",
    "R_VBUS_DET_D1",
    "SW_RST",
    "TP_BAT_CHG",
    "TP_DSI_CK_N",
    "TP_DSI_CK_P",
    "TP_DSI_D0_N",
    "TP_DSI_D0_P",
    "TP_DSI_D1_N",
    "TP_DSI_D1_P",
    "TP_DSI_D2_N",
    "TP_DSI_D2_P",
    "TP_DSI_D3_N",
    "TP_DSI_D3_P",
    "TP_LED_B",
    "TP_LED_G",
    "TP_LED_R",
    "TP_TS",
    "TP_VBUS",
    "U_CHG",
    "U_TEMP",
    "X1",
)
# ★共 78 条★ (★建闸日 2026-11-18 本机实跑: MECH 域引用到的 live 位号 ∪ 裸编号 live 位号 Q1/Q2/X1★)

# ★**盘面位号集合指纹 (★重建触发条件的判据★)** ★
#   ★**它变 = 盘面位号集合改过了** ⇒ ★这时候才允许 (且需要) 显式重建注册表★ ★
#   ★**它不变 = 盘面位号没动** ⇒ ★闸红只是【引用漂移】⇒ ★重建注册表【不是】闸红的理由★ ★
REGISTRY_BOARD_FINGERPRINT = "565b26cb335efa6bce1b567dbf2b598f75d1a5634721845dcea43670766e54a5"

# =================================================================================================
# §R5-④ · 判据分支自检 (★「判据分支匹配不上 ⇒ 判红」·不许静悄悄不查了★)
# =================================================================================================
# ★**这是 ISS-326 交卷页里反复强调的那一条**: 「判据分支匹配不上时必须【红】而不是【静悄悄不查了】」★
# ★**做法**: 每次跑闸, 都用一张【合成索引】把 C1..C17 每条分支各驱动一次, 核对分类结果★★
#   ⇒ ★任何一条分支的行为被改坏 / 被删掉 / 被改岔 ⇒ 闸立刻判红并点名是哪一条★ ★
# ★**为什么合成索引**: 分支覆盖要【确定性地】跑满, 不能靠盘上碰巧有什么 token★ ★
RULE_PROBES = (
    # (探针 token, 期望 class, 期望 rule, 该分支靠什么命中)
    ("R_PROBE_LIVE", "DESIGNATOR_OK", "C1", "live 解析 (板/网表里找得到)"),
    ("R_PROBE_DRIFT", "DESIGNATOR_DRIFT", "C2", "冻结注册表 (建闸日是位号·现在找不到)"),
    ("PWR_PROBE", "NET_NAME", "C3", "网名 (电源轨名/逻辑信号名)"),
    ("DOC_PROBE_REF", "DOC_INTERNAL", "C4", "文档互引 (盘上有同名文档)"),
    ("ANCHOR_PROBE_REF", "DOC_INTERNAL", "C5", "文档锚点 (# BEGIN/END)"),
    ("ENV_PROBE_REF", "DOC_INTERNAL", "C6", "环境变量键"),
    ("R_probe_lower", "DOC_INTERNAL", "C7", "物理符号 (后缀含小写)"),
    ("R_PROBE_TRUNC_", "DOC_INTERNAL", "C8", "前缀截断 (以 _ 结尾)"),
    ("R_PROBE_PIPE", "DOC_INTERNAL", "C9", "模式字面量 (每次出现都跟在 | 之后)"),
    ("L_PROBE_EYE", "DOC_INTERNAL", "C10", "物理量命名空间 (L_)"),
    ("PWR_PROBE_RAIL", "NET_NAME", "C11", "信号命名空间 (PWR_/VBUS_/…)"),
    ("R_PROBE_FAMILY", "DOC_INTERNAL", "C12", "家族统称 (≥2 个 live 位号的严格前缀)"),
    ("SW_PROBE_X", "DOC_INTERNAL", "C13", "软件侧命名空间 (SW_)"),
    ("R_PROBE_ABSENT", "DESIGNATOR_MISSING", "C14", "兜底 ⇒ 真隐患"),
    ("R_PROBE_CODEID", "DOC_INTERNAL", "C15", "★MECH 侧·判据脚本的代码常量/变量名★"),
    ("Q7", "DOC_INTERNAL", "C16", "★MECH 侧·裸编号 (Q\\d+/X\\d+)·非 live 非登记★"),
    ("R_PROBE_REGISTERED", "DOC_INTERNAL", "C17", "★MECH 侧·已登记的「不是位号引用」★"),
)

# ★**合成索引 (★让上面 17 条分支各自被确定地驱动一次★)** ★
def _probe_index() -> dict:
    live = {
        "R_PROBE_LIVE",
        "R_PROBE_FAMILY_A", "R_PROBE_FAMILY_B",   # ★给 C12 家族统称凑够 ≥2 个子位号★
        "R_SUPV_DIV1", "R_SUPV_DIV2",
    }
    return {
        "root": "<probe>",
        "board_refs": set(live),
        "netlist_refs": set(),
        "live_refs": set(live),
        "net_names": {"PWR_PROBE"},
        "doc_files": {"DOC_PROBE_REF"},
        "anchors": {"ANCHOR_PROBE_REF"},
        "env_keys": {"ENV_PROBE_REF"},
        "registry": {"R_PROBE_DRIFT"},
        "py_idents": {"R_PROBE_CODEID"},
        "non_designator_registry": {"R_PROBE_REGISTERED"},
        "occ": {},
    }


def run_rule_probes() -> list:
    """★跑一遍判据分支自检 ⇒ 返回 [(探针, 期望, 实际, 说明), ...] (空的 = 全过)★"""
    idx = _probe_index()
    occ_by_tok = {
        "R_PROBE_PIPE": [("<probe>", 1, '|R_PROBE_PIPE |')],
    }
    bad = []
    for tok, want_cls, want_rule, why in RULE_PROBES:
        occ = occ_by_tok.get(tok, [("<probe>", 1, f"{tok} ...")])
        got_cls, got_rule, _note = classify_mech(tok, idx, occ)
        if got_cls != want_cls or got_rule != want_rule:
            bad.append((tok, f"{want_cls}/{want_rule}", f"{got_cls}/{got_rule}", why))
    return bad


# =================================================================================================
# §IO · 只读收集 (★零写板 · 零落表★)
# =================================================================================================
def collect_mech_tokens(root: str):
    """★扫 MECH 递归面 (md + py) ⇒ (occ, n_md, n_py, py_idents)★"""
    md = sorted(glob.glob(os.path.join(root, MECH_MD_GLOB), recursive=True))
    py = [p for p in sorted(glob.glob(os.path.join(root, MECH_PY_GLOB), recursive=True))
          if os.path.relpath(p, root) != SELF_GATE_REL]
    if not md:
        raise InputError(f"★MECH 侧 md 扫描面拿不到 (glob `{MECH_MD_GLOB}` 空): {root}")
    if not py:
        raise InputError(f"★MECH 侧 py 扫描面拿不到 (glob `{MECH_PY_GLOB}` 空, 或全被闸自身排除规则滤掉): {root}")
    occ = {}
    for path in md + py:
        rel = os.path.relpath(path, root)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, 1):
                    for m in TOKEN_RE.finditer(line):
                        occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))
                    for m in BARE_NUMBER_RE.finditer(line):
                        occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))
        except OSError as exc:
            raise InputError(f"★MECH 侧文件读不了: {rel} ({exc})") from exc
    if not occ:
        raise InputError(f"★MECH 侧一个 token 都没抽到 (口径变了?): {root}")
    return occ, len(md), len(py), _python_identifiers(py)


def _python_identifiers(py_paths: list) -> set:
    """★把 MECH 判据脚本里的【Python 标识符 (NAME token)】收上来 ⇒ C15 用★"""
    names = set()
    for p in py_paths:
        try:
            with open(p, "rb") as fh:
                for tok in tokenize.tokenize(fh.readline):
                    if tok.type == tokenize.NAME:
                        names.add(tok.string)
        except Exception:                                   # noqa: BLE001 · 语法错误的文件不该让闸崩
            continue
    return names


def build_aux_index(root: str):
    """★辅助索引 (C4/C5/C6)★ ⇒ ★先复用 SW 那道闸的 (口径零漂移), 再补 MECH 递归面★"""
    doc_files, anchors, env_keys = sw.build_aux_index(root)
    doc_files, anchors, env_keys = set(doc_files), set(anchors), set(env_keys)
    md = sorted(glob.glob(os.path.join(root, MECH_MD_GLOB), recursive=True))
    py = [p for p in sorted(glob.glob(os.path.join(root, MECH_PY_GLOB), recursive=True))
          if os.path.relpath(p, root) != SELF_GATE_REL]
    for p in md:
        rel = os.path.relpath(p, root)
        doc_files.add(os.path.splitext(rel)[0])
        doc_files.add(os.path.splitext(os.path.basename(rel))[0])
        txt = open(p, "r", encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"#\s*(?:BEGIN|END)\s+([A-Za-z0-9_]+)", txt):
            anchors.add(m.group(1))
    env_pat = re.compile(r"os\.environ(?:\.get\(|\.setdefault\(|\.pop\(|\[)\s*[\"']([A-Za-z0-9_]+)[\"']")
    for p in py:
        txt = open(p, "r", encoding="utf-8", errors="replace").read()
        for m in env_pat.finditer(txt):
            env_keys.add(m.group(1))
    return doc_files, anchors, env_keys


# =================================================================================================
# §CLASSIFY · 分类 (★SW 的 14 条一字不改, MECH 侧只加 C15/C16/C17 三条★)
# =================================================================================================
def classify_mech(token: str, idx: dict, occ: list):
    """★返回 (class, rule_id, 说明)★ ⇒ ★先走 SW 那道闸的 14 条, 再走 MECH 侧三条★"""
    cls, rule, note = sw.classify(token, idx, occ)
    if cls != "DESIGNATOR_MISSING":
        return cls, rule, note
    # ★C16 · 裸编号 (Q\d+ / X\d+) —— MECH 域用它表示【老板的问题编号】或【坐标轴变量】⇒ 不是位号★
    #   ★**注意**: live 的裸编号 (Q1/Q2/X1) 在 C1 就已经命中了 ⇒ 走不到这里 ⇒ 不判红★
    if BARE_NUMBER_RE.fullmatch(token) and token not in idx["live_refs"] and token not in idx["registry"]:
        return ("DOC_INTERNAL", "C16",
                "★裸编号 (`Q\\d+`/`X\\d+`)·既不 live 也不在注册表 ⇒ MECH 域用它表示【文档自己的编号】或【坐标轴变量】⇒ 不是位号★")
    # ★C15 · 判据脚本的代码常量/变量名命名空间★
    if token in idx.get("py_idents", ()):
        return ("DOC_INTERNAL", "C15",
                "★判据脚本里的【代码常量/变量名】(Python 标识符)⇒ 不是位号★")
    # ★C17 · 已登记的「不是位号引用」★
    if token in idx.get("non_designator_registry", ()):
        return ("DOC_INTERNAL", "C17", "★已登记的「不是位号引用」⇒ 不计入真隐患★")
    return cls, rule, note


# =================================================================================================
# §ANALYZE · 主判定
# =================================================================================================
def analyze_mech(root: str) -> dict:
    """★跑一遍 ⇒ 返回结构化结果 (★主模式与 --selftest 共用同一份逻辑★)★"""
    root = os.path.abspath(root)
    board_refs = read_board_refs(os.path.join(root, BOARD_REL))            # ★F1 fail-closed★
    netlist_refs = read_netlist_refs({"root": root})                       # ★F2 fail-closed★
    net_names = read_net_names(root)
    occ, n_md, n_py, py_idents = collect_mech_tokens(root)                # ★F3 fail-closed★
    doc_files, anchors, env_keys = build_aux_index(root)

    live_refs = board_refs | netlist_refs
    idx = {
        "root": root,
        "board_refs": board_refs,
        "netlist_refs": netlist_refs,
        "live_refs": live_refs,
        "net_names": net_names,
        "doc_files": doc_files,
        "anchors": anchors,
        "env_keys": env_keys,
        "registry": set(MECH_DESIGNATOR_REGISTRY),
        "py_idents": py_idents,
        "non_designator_registry": set(MECH_NON_DESIGNATOR_REGISTRY),
        "occ": occ,
    }

    rows = []
    for tok in sorted(occ):
        cls, rule, note = classify_mech(tok, idx, occ[tok])
        rows.append({"token": tok, "cls": cls, "rule": rule, "note": note, "occ": occ[tok]})

    drift = [r for r in rows if r["cls"] == "DESIGNATOR_DRIFT"]
    missing = [r for r in rows if r["cls"] == "DESIGNATOR_MISSING"]

    missing_total = len(missing)
    new_missing = [r for r in missing if r["token"] not in BASELINE_TOKENS]
    baseline_ok = (missing_total <= BASELINE_COUNT) and (not new_missing)
    resolved_baseline = sorted(t for t in BASELINE_TOKENS if t not in {r["token"] for r in missing})

    # ★**基线自洽检查 (★不许放宽★)** ★
    baseline_integrity = []
    if BASELINE_COUNT != len(BASELINE_TOKENS):
        baseline_integrity.append(
            f"BASELINE_COUNT={BASELINE_COUNT} 但 BASELINE_TOKENS 只有 {len(BASELINE_TOKENS)} 条 (★必须相等★)")
    if BASELINE_COUNT > BASELINE_COUNT_BUILDDAY:
        baseline_integrity.append(
            f"BASELINE_COUNT={BASELINE_COUNT} > 建闸日冻结值 {BASELINE_COUNT_BUILDDAY} "
            f"(★基线只许收紧不许放宽★)")
    for t in BASELINE_TOKENS:
        if t in live_refs:
            baseline_integrity.append(f"基线里的 {t} 现在【解析得到】⇒ 它不是真隐患 ⇒ 必须从基线里删掉 (★收紧★)")

    # ★**盘面位号集合指纹 (★重建注册表的唯一合法触发条件★)** ★
    cur_fp = hashlib.sha256(("\n".join(sorted(live_refs))).encode()).hexdigest()
    reg_tokens = set(MECH_DESIGNATOR_REGISTRY)
    added = sorted(live_refs - reg_tokens)
    removed = sorted(reg_tokens - live_refs)

    return {
        "root": root,
        "live_refs": live_refs,
        "md_scanned": n_md,
        "py_scanned": n_py,
        "rows": rows,
        "drift": drift,
        "missing": missing,
        "new_missing": new_missing,
        "missing_total": missing_total,
        "baseline_count": BASELINE_COUNT,
        "baseline_ok": baseline_ok,
        "baseline_integrity": baseline_integrity,
        "resolved_baseline": resolved_baseline,
        "board_refs_n": len(board_refs),
        "netlist_refs_n": len(netlist_refs),
        "net_names_n": len(net_names),
        "tokens_n": len(rows),
        "docs_n": len({rel for r in rows for rel, _ln, _l in r["occ"]}),
        "fingerprint": cur_fp,
        "fingerprint_match": (cur_fp == REGISTRY_BOARD_FINGERPRINT),
        "registry_added": added,
        "registry_removed": removed,
        "probe_failures": run_rule_probes(),
    }


# =================================================================================================
# §REPORT · 输出 (★[FAIL] 行是给门禁链 `run_external_gate()` 抽原因用的★)
# =================================================================================================
def suggest_names(token: str, live: set, limit: int = 6):
    """★「板与网表里现在叫什么」⇒ ★直接复用 SW 那道闸的 (口径零漂移)★"""
    return sw.suggest_names(token, live, limit)


def format_report(res: dict, verbose: bool = True) -> str:
    out = []
    L = out.append
    L("=" * 78)
    L("ISS-333 · MECH 侧位号引用可达性闸 · check_mech_ref_reachability.py")
    L("=" * 78)
    L(f"项目根        : {res['root']}")
    L(f"板位号        : {res['board_refs_n']} 个 (★板文件文本解析, 未 import pcbnew★)")
    L(f"网表位号      : {res['netlist_refs_n']} 个 (★三张 CSV 的 ref 列★)")
    L(f"网名索引      : {res['net_names_n']} 个")
    L(f"扫描面        : {res['md_scanned']} 份 `MECH/**/*.md` (递归) + {res['py_scanned']} 份 `MECH/**/*.py` (递归)")
    L(f"                (★闸自身已排除: {SELF_GATE_REL}★)")
    L(f"抽出 token    : {res['tokens_n']} 个唯一标识符")
    L("")
    counts = {}
    for r in res["rows"]:
        counts[r["cls"]] = counts.get(r["cls"], 0) + 1
    L("【分类统计】 (★SW 的 14 条 + MECH 侧的 C15/C16/C17★)")
    for cls in ("DESIGNATOR_OK", "DESIGNATOR_DRIFT", "DESIGNATOR_MISSING", "NET_NAME", "DOC_INTERNAL"):
        L(f"   {cls:22s} {counts.get(cls, 0):4d}")
    L("")
    L(f"【R3 建闸日基线】 `DESIGNATOR_MISSING` 实测 = {res['missing_total']} 条 · 允许上限 = {res['baseline_count']} 条")
    L(f"   ⇒ {'✔ 在基线内' if res['baseline_ok'] else '✘ 超基线 (见下方 FAIL 行)'}")
    if res["resolved_baseline"]:
        L(f"   ★提示: 基线里的 {', '.join(res['resolved_baseline'])} 现在已经解析得到了 ⇒ "
          f"★建议把 BASELINE_COUNT 收到 {res['missing_total']} 并从 BASELINE_TOKENS 里删掉 (★收紧, 不是放宽★)★")
    L("")
    if res["drift"]:
        L("【★真位号·改名漂移 (C2)★】 —— ★这就是「板只改一次那一趟」要抓的东西★")
        for r in res["drift"]:
            rel, ln, _line = r["occ"][0]
            L(f"   ★{r['token']}★  ({rel}:{ln})  ← 引用的位号现在解析不到")
            for s in suggest_names(r["token"], res["live_refs"]):
                L(f"        板/网表里现在叫: {s}")
            L(f"        判红理由: {r['note']}")
        L("")
    if res["missing"]:
        L("【★真隐患 (C14)·现在就对不上的位号引用★】")
        for r in res["missing"]:
            rel, ln, _line = r["occ"][0]
            tag = "★基线内·已登记★" if r["token"] in BASELINE_TOKENS else "★★超基线★★"
            L(f"   {tag} {r['token']}  ({rel}:{ln})  出现 {len(r['occ'])} 次")
            L(f"        理由: {BASELINE_TOKENS.get(r['token'], '★不在建闸日基线里 ⇒ 这是新增的真隐患★')}")
        L("")
    # ★**判据分支自检结果 (★R5-④★)** ★
    if res["probe_failures"]:
        L("【★R5-④ 判据分支自检 (★判据分支匹配不上 ⇒ 必须判红★)★】")
        for tok, want, got, why in res["probe_failures"]:
            L(f"   ★✘ 分支失配★ {tok}: 期望 {want} · 实际 {got}  ({why})")
        L("")
    else:
        L(f"【★R5-④ 判据分支自检★】 {len(RULE_PROBES)}/{len(RULE_PROBES)} 条分支全部命中 (★判据没被改岔★)")
        L("")
    # ★**基线自洽检查 (★不许放宽★)** ★
    if res["baseline_integrity"]:
        L("【★基线自洽检查 (★只许收紧不许放宽★)★】")
        for s in res["baseline_integrity"]:
            L(f"   ★✘ {s}")
        L("")
    # ★**盘面指纹 (★重建注册表的唯一合法触发条件★)** ★
    if not res["fingerprint_match"]:
        L("【★盘面位号集合已变 (★重建注册表的合法触发条件=【盘面改过位号】·★不是【闸红了就重建】★)★】")
        L(f"   建闸日指纹 : {REGISTRY_BOARD_FINGERPRINT}")
        L(f"   当前指纹   : {res['fingerprint']}")
        if res["registry_added"]:
            L(f"   新增 live 位号 ({len(res['registry_added'])}): {', '.join(res['registry_added'][:12])}"
              f"{' …' if len(res['registry_added']) > 12 else ''}")
        if res["registry_removed"]:
            L(f"   消失的注册表位号 ({len(res['registry_removed'])}): {', '.join(res['registry_removed'][:12])}"
              f"{' …' if len(res['registry_removed']) > 12 else ''}")
        L("   ★⇒ 需要人工判: 这些变更是【合法改名】还是【盘面改过位号】⇒ 只有前者才需要显式重建注册表★")
        L("   ★⇒ 重建命令: `--freeze-registry --confirm-freeze` (★双确认·不许在 CI 里跑★)")
        L("")
    # ★**FAIL 行 (★门禁链 `run_external_gate()` 靠 stdout 的 [FAIL] 行抽原因★)** ★
    for r in res["drift"]:
        rel, ln, _line = r["occ"][0]
        cands = ", ".join(suggest_names(r["token"], res["live_refs"])) or "(无近似名)"
        L(f"[FAIL] 位号引用解析不到 (改名漂移): {r['token']} @ {rel}:{ln} ⇒ 板与网表里现在叫: {cands}")
    for r in res["new_missing"]:
        rel, ln, _line = r["occ"][0]
        cands = ", ".join(suggest_names(r["token"], res["live_refs"])) or "(无近似名)"
        L(f"[FAIL] 位号引用解析不到 (新增真隐患·超基线): {r['token']} @ {rel}:{ln} ⇒ 板与网表里现在叫: {cands}")
    if res["missing_total"] > res["baseline_count"]:
        L(f"[FAIL] 真隐患条数 {res['missing_total']} > 基线上限 {res['baseline_count']} (★基线只许收紧不许放宽★)")
    for s in res["baseline_integrity"]:
        L(f"[FAIL] 基线自洽检查不过: {s}")
    for tok, want, got, why in res["probe_failures"]:
        L(f"[FAIL] 判据分支失配 (★判据分支匹配不上 ⇒ 判红·不许静悄悄不查了★): {tok} 期望 {want} 实际 {got} ({why})")
    if not res["baseline_ok"] and not res["drift"] and not res["new_missing"]:
        L(f"[FAIL] 真隐患条数 {res['missing_total']} 超基线上限 {res['baseline_count']}")
    if verbose:
        L("")
        L("【R2 分类全表】 (★`--dump-classification` 同源★)")
        for r in res["rows"]:
            L(f"   {r['cls']:20s} {r['rule']:4s} {r['token']:44s} {r['note']}")
    L("")
    ok = (res["baseline_ok"] and not res["drift"]
          and not res["baseline_integrity"] and not res["probe_failures"])
    L(f"【判决】 {'✔ 绿 (rc=0): MECH 侧引用的位号全部可达, 真隐患在基线内' if ok else '✘ 红 (rc≠0)'}")
    return "\n".join(out)


# =================================================================================================
# §SELFTEST · 反向用例 (★14 条·含「假绿」与「判据分支失配」两条最要紧的★)
# =================================================================================================
def _copy_input_surface(src_root: str, dst_root: str) -> None:
    """★把闸要读的那一面拷进沙盒 (★真拷贝·绝不 hardlink·绝不软链★)★"""
    os.makedirs(dst_root, exist_ok=True)
    rels = [BOARD_REL] + list(NETLIST_CSVS)
    for rel in rels:
        s = os.path.join(src_root, rel)
        d = os.path.join(dst_root, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
    # ★MECH 递归面 (md + py) — 闸自身不拷 (★自排除·闸不查自己★)★
    for pat in (MECH_MD_GLOB, MECH_PY_GLOB):
        for p in sorted(glob.glob(os.path.join(src_root, pat), recursive=True)):
            rel = os.path.relpath(p, src_root)
            if rel == SELF_GATE_REL:
                continue
            d = os.path.join(dst_root, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(p, d)
    for d in sw.AUX_MD_DIRS:
        for p in sorted(glob.glob(os.path.join(src_root, d, "*.md"))):
            t = os.path.join(dst_root, os.path.relpath(p, src_root))
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(p, t)
    for p in sorted(glob.glob(os.path.join(src_root, "*.md"))):
        t = os.path.join(dst_root, os.path.basename(p))
        shutil.copy2(p, t)
    for d in sw.AUX_PY_DIRS:
        for p in sorted(glob.glob(os.path.join(src_root, d, "*.py"))):
            t = os.path.join(dst_root, os.path.relpath(p, src_root))
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(p, t)


def _write_text(path: str, text: str) -> None:
    """★写文件前必查软链 (★sw-lead 11-18 14:39 软链写穿过真件的事故★)★"""
    if os.path.islink(path):
        raise RuntimeError(f"★拒绝写软链: {path}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _rewrite_ref(path: str, old: str, new: str) -> int:
    """★把一张网表 CSV 的 `ref` 列里的某个位号改名/删除 (★沙盒专用★)★"""
    import csv as _csv
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        rdr = _csv.DictReader(fh)
        fields = list(rdr.fieldnames or [])
        rows = list(rdr)
    n = 0
    for row in rows:
        if (row.get("ref") or "").strip() == old:
            row["ref"] = new
            n += 1
    _write_text(path, "")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        wr = _csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for row in rows:
            wr.writerow(row)
    return n


def _rename_in_board(sandbox: str, old: str, new: str) -> int:
    """★沙盒里把板上的某个位号改名 (★真拷贝·真盘一个字节都不写★)★"""
    p = os.path.join(sandbox, BOARD_REL)
    txt = open(p, "r", encoding="utf-8", errors="replace").read()
    n = 0
    for pat in ('(property "Reference" "%s"', '(fp_text reference "%s"'):
        needle = pat % old
        if needle in txt:
            n += txt.count(needle)
            txt = txt.replace(needle, pat % new)
    _write_text(p, txt)
    return n


def _rename_everywhere(sandbox: str, old: str, new: str) -> int:
    """★沙盒里把一个位号在【板 + 3 张网表】里同步改名 (★模拟 S1 改名★)★"""
    n = _rename_in_board(sandbox, old, new)
    for rel in NETLIST_CSVS:
        n += _rewrite_ref(os.path.join(sandbox, rel), old, new)
    return n


def _replace_in_mech(sandbox: str, pattern: str, repl: str, only_suffix: str = "") -> int:
    """★沙盒里按正则改 MECH 递归面里的位号串 (★默认只改 .md / 或只改 .py★)★"""
    n = 0
    for pat in (MECH_MD_GLOB, MECH_PY_GLOB):
        for p in sorted(glob.glob(os.path.join(sandbox, pat), recursive=True)):
            rel = os.path.relpath(p, sandbox)
            if rel == SELF_GATE_REL:
                continue
            if only_suffix and not rel.endswith(only_suffix):
                continue
            txt = open(p, "r", encoding="utf-8", errors="replace").read()
            new_txt, k = re.subn(pattern, repl, txt)
            if k:
                _write_text(p, new_txt)
                n += k
    return n


def _gate_rc(root: str):
    """★在沙盒根上跑一遍闸的主判定 ⇒ (rc, 明细) (★0=绿·1=红·2=输入读不到⇒fail-closed 判红★)★"""
    try:
        res = analyze_mech(root)
    except InputError as exc:
        return 2, [f"fail-closed: {exc}"]
    detail = []
    for r in res["drift"]:
        detail.append(f"改名漂移:{r['token']}")
    for r in res["new_missing"]:
        detail.append(f"新增真隐患:{r['token']}")
    if res["missing_total"] > res["baseline_count"]:
        detail.append(f"真隐患 {res['missing_total']} > 基线 {res['baseline_count']}")
    for s in res["baseline_integrity"]:
        detail.append(f"基线自洽:{s}")
    for tok, want, got, _why in res["probe_failures"]:
        detail.append(f"判据分支失配:{tok}")
    ok = (res["baseline_ok"] and not res["drift"]
          and not res["baseline_integrity"] and not res["probe_failures"])
    return (0 if ok else 1), detail


def run_selftest(root: str, tmpdir: str = "") -> int:
    root = os.path.abspath(root)
    base = tmpdir or os.path.join(root, "tmp", "iss333_gates")
    os.makedirs(base, exist_ok=True)
    work = tempfile.mkdtemp(prefix="iss333_refreach_", dir=base)

    cases = []

    def case(name, expect, desc):
        cases.append((name, expect, desc))

    # ★★ISS-326 沙盒的 7 条 (case1B/1C/1D/2/3A/3B/4) 逐条映射到【这道闸】★★
    case("MC-1", "red", "★case1B 假绿★ 判据脚本里 `== \"R_SEL_D0_N\"` 失配 (世界已改名, 脚本没改) ⇒ 【必须红】")
    case("MC-2", "green", "★case1C 对照/修复配方★ 板改名 + MECH 同步改 ⇒ 【必须绿】(★证明判据没写死「改名方案」★)")
    case("MC-3", "red", "★case1D 反证★ 只改 MECH 文档里的位号 (板不改) ⇒ 【必须红】(★改名漂移★)")
    case("MC-4", "red", "★case2 崩★ 板上 D_LED_G 改名 (MECH 不动) ⇒ 【必须红】")
    case("MC-5", "red", "★case3A 不动集★ 只改改名集位号, 不动集 J_SOM_P1 一律不动 ⇒ 【必须红】且 【J_SOM_P1 不得出现在红项里】")
    case("MC-6", "red", "★case3B 反证★ 连不动集里的 J_SOM_P1 也改 ⇒ 【必须红】且 【必须点名 J_SOM_P1】")
    case("MC-7", "green", "★case4 注释里的 ref★ 改判据脚本【注释/文档串】里的位号名 ⇒ 【必须绿】")
    # ★★ISS-326 设计稿 §4 的其余几条 + fail-closed 三条 + 基线护栏 + 判据分支守卫★★
    case("MC-8", "red", "★G1 假位号新增★ MECH 文档里写一个盘上没有的位号 ⇒ 【必须红】")
    case("MC-9", "red", "★F3 扫描面半残★ MECH/**/*.py 全删 ⇒ 【必须红】(★fail-closed★)")
    case("MC-10", "red", "★F1 板读不到★ 板文件删掉 ⇒ 【必须红】(★fail-closed★)")
    case("MC-11", "red", "★F2 网表读不到★ 网表 CSV 删掉 ⇒ 【必须红】(★fail-closed★)")
    case("MC-12", "red", "★G7 基线不许被放宽★ BASELINE_COUNT 被改大 ⇒ 【必须红】")
    case("MC-13", "green", "★正向对照★ 原样不动 ⇒ 【必须绿】(★不许把闸修成永远红★)")
    case("MC-14", "red", "★★判据分支匹配不上 ⇒ 必须红★ (★不许静悄悄不查了★) ⇒ 故意改坏一条分支探针")

    results = []
    for name, expect, desc in cases:
        sandbox = os.path.join(work, name)
        _copy_input_surface(root, sandbox)
        rc_before, det_before = _gate_rc(sandbox)
        extra = ""
        if name == "MC-1":
            n = _replace_in_mech(sandbox, r'"R_SEL_D0_N"', '"R_SEL_D0_N_1"', only_suffix=".py")
            extra = f"· 判据脚本字面量替换 {n} 处 (板不动)"
        elif name == "MC-2":
            n = _rename_everywhere(sandbox, "R_SEL_D0_N", "R_SEL_D0_N_1")
            m = _replace_in_mech(sandbox, r"\bR_SEL_D0_N\b", "R_SEL_D0_N_1")
            extra = f"· 板+网表改名 {n} 处 · MECH 同步改 {m} 处"
        elif name == "MC-3":
            n = _replace_in_mech(sandbox, r"\bR_SEL_D0_N\b", "R_SEL_D0_N_X", only_suffix=".md")
            extra = f"· 只改 MECH 文档 {n} 处 (板不动)"
        elif name == "MC-4":
            n = _rename_everywhere(sandbox, "D_LED_G", "D_LED_G_1")
            extra = f"· 板+网表把 D_LED_G 改名 {n} 处 (MECH 不动)"
        elif name == "MC-5":
            br = read_board_refs(os.path.join(sandbox, BOARD_REL))
            move = sorted(r for r in br if r.startswith("R_SEL_"))
            for r in move:
                _rename_everywhere(sandbox, r, r + "_1")
            extra = f"· 只改改名集 {len(move)} 个 (J_SOM_P1 不动)"
        elif name == "MC-6":
            br = read_board_refs(os.path.join(sandbox, BOARD_REL))
            move = sorted(r for r in br if r.startswith("R_SEL_"))
            for r in move:
                _rename_everywhere(sandbox, r, r + "_1")
            _rename_everywhere(sandbox, "J_SOM_P1", "J_SOM_P1_X")
            extra = f"· 改名集 {len(move)} 个 + 连 J_SOM_P1 也改"
        elif name == "MC-7":
            p = os.path.join(sandbox, "MECH", "check_board_frame_coords.py")
            txt = open(p, "r", encoding="utf-8", errors="replace").read()
            n = txt.count("J_SOM_P1")
            _write_text(p, txt.replace("J_SOM_P1", "ZZ_COMMENT_PROBE_1"))
            extra = f"· 改注释/文档串里的位号名 {n} 处"
        elif name == "MC-8":
            p = os.path.join(sandbox, "MECH", "README.md")
            txt = open(p, "r", encoding="utf-8", errors="replace").read()
            _write_text(p, txt + "\n<!-- ISS333 MC-8 -->\nprobe part: `R_ZZ_ISS333_FAKE_999` 假装位号\n")
            extra = "· MECH/README.md 里写一个盘上没有的位号"
        elif name == "MC-9":
            for p in sorted(glob.glob(os.path.join(sandbox, MECH_PY_GLOB), recursive=True)):
                os.remove(p)
            extra = "· 删掉 MECH/**/*.py 全部"
        elif name == "MC-10":
            os.remove(os.path.join(sandbox, BOARD_REL))
            extra = "· 删掉板文件"
        elif name == "MC-11":
            os.remove(os.path.join(sandbox, "HW", "netlist_v1.csv"))
            extra = "· 删掉 HW/netlist_v1.csv"
        elif name == "MC-12":
            global BASELINE_COUNT
            _saved = BASELINE_COUNT
            BASELINE_COUNT = _saved + 1
            globals()["BASELINE_COUNT"] = BASELINE_COUNT
            extra = f"· BASELINE_COUNT { _saved } → {BASELINE_COUNT}"
        elif name == "MC-13":
            extra = "· 不做任何改动 (正向对照)"
        elif name == "MC-14":
            _saved_probes = globals()["RULE_PROBES"]
            globals()["RULE_PROBES"] = tuple(
                (t, ("DESIGNATOR_MISSING" if i == 0 else c), r, w)
                for i, (t, c, r, w) in enumerate(_saved_probes))
            extra = "· 故意把【C1 这一条】分支探针的期望类改成 DESIGNATOR_MISSING (★只改一条·其余 16 条仍须全对★)"

        rc_after, det_after = _gate_rc(sandbox)

        # —— MC-5 / MC-6 的附加断言 ——
        note = ""
        if name == "MC-5":
            named = any("J_SOM_P1" in d for d in det_after)
            if named:
                ok = False
                note = "★J_SOM_P1 被误伤了 (不该动的不动集被点名)★"
            else:
                ok = (rc_after != 0) and (rc_before == 0)
                note = "★不动集 J_SOM_P1 未被误伤 (红项里没有它)★"
        elif name == "MC-6":
            named = any("J_SOM_P1" in d for d in det_after)
            ok = (rc_after != 0) and (rc_before == 0) and named
            note = "★J_SOM_P1 已被点名 (证明它确实在不动集里·该改就会红)★" if named else "★J_SOM_P1 没被点名★"
        else:
            ok = (rc_after != 0 and rc_before == 0) if expect == "red" else (rc_after == 0 and rc_before == 0)

        if name == "MC-12":
            globals()["BASELINE_COUNT"] = _saved
        if name == "MC-14":
            globals()["RULE_PROBES"] = _saved_probes

        results.append((name, expect, desc, rc_before, rc_after, ok, det_before, det_after, extra, note))
        shutil.rmtree(sandbox, ignore_errors=True)
    shutil.rmtree(work, ignore_errors=True)

    print("=" * 78)
    print("ISS-333 · MECH 侧位号引用可达性闸 · 反向用例 (★R4★)")
    print("=" * 78)
    print(f"沙盒根: {base}   (★真拷贝·绝不 hardlink·真盘一个字节都不写★)")
    print("-" * 78)
    passed = 0
    for name, expect, desc, rc_b, rc_a, ok, det_b, det_a, extra, note in results:
        mark = "✅" if ok else "❌"
        print(f"  {mark} {name} 期望={expect:5s} 破坏前 rc={rc_b}  破坏后 rc={rc_a}  {desc}")
        if extra:
            print(f"      ★做法★ {extra}")
        if note:
            print(f"      ★附加断言★ {note}")
        if expect == "red":
            print(f"      ★不是巧合自证★: 同一棵沙盒树·破坏前 rc={rc_b} (红项: {', '.join(det_b) if det_b else '无'}) "
                  f"⇒ 破坏后 rc={rc_a} (红项: {', '.join(det_a) if det_a else '无'}) ⇒ 这条红【只可能】来自被改坏的那一处")
        else:
            print(f"      ★不是巧合自证★: 同一棵沙盒树·破坏前 rc={rc_b} ⇒ 破坏后 rc={rc_a} "
                  f"(红项: {', '.join(det_a) if det_a else '无'}) ⇒ ★判据没被「改坏的那一处」弄红★")
        if ok:
            passed += 1
        else:
            print(f"      ★用例没过★ 破坏前 rc={rc_b} (★必须 0 ⇒ 才叫「不是巧合」★) 破坏后 rc={rc_a}")
    print("-" * 78)
    print(f"反向用例: {passed}/{len(results)} 通过")
    if passed == len(results):
        print("✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没 ★)")
        return 0
    print("❌ 有用例没抓到 ⇒ 判据可能没被真读")
    return 1


# =================================================================================================
# §FREEZE · 重建冻结表 (★★双确认★·★重建不是闸红的理由★)
# =================================================================================================
def freeze_registry(root: str) -> int:
    """★重建 MECH_DESIGNATOR_REGISTRY + 盘面指纹 (★建闸日跑一次·之后只读★)★"""
    root = os.path.abspath(root)
    try:
        board_refs = read_board_refs(os.path.join(root, BOARD_REL))
        netlist_refs = read_netlist_refs({"root": root})
        occ, _nmd, _npy, _ids = collect_mech_tokens(root)
    except InputError as exc:
        print(f"[FAIL] {exc}")
        return 2
    live = board_refs | netlist_refs
    keep = sorted(t for t in occ if t in live)
    fp = hashlib.sha256(("\n".join(sorted(live))).encode()).hexdigest()
    print("MECH_DESIGNATOR_REGISTRY = (")
    for tok in keep:
        print(f'    "{tok}",')
    print(")")
    print(f"# ★共 {len(keep)} 条★  (★由 `--freeze-registry` 生成·建闸日 2026-11-18 实测★)")
    print(f'REGISTRY_BOARD_FINGERPRINT = "{fp}"')
    print("# ★盘面 live 位号集合 sha256★")
    return 0


# =================================================================================================
# §MAIN
# =================================================================================================
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT, help="项目根 (默认: 脚本上两级)")
    ap.add_argument("--selftest", action="store_true", help="反向用例 (14 条)")
    ap.add_argument("--dump-classification", action="store_true",
                    help="★R2: 打印全部分类 (一条命令复现分类规则★)")
    ap.add_argument("--freeze-registry", action="store_true", help="★重建 MECH_DESIGNATOR_REGISTRY 冻结表★")
    ap.add_argument("--confirm-freeze", action="store_true",
                    help="★与 --freeze-registry 一起用 (★双确认·★重建的触发条件 = 【盘面改过位号】, "
                         "★不是【闸红了就重建】★)★")
    ap.add_argument("--tmpdir", default="", help="沙盒临时树根目录")
    ap.add_argument("--brief", action="store_true", help="不打印分类全表")
    args = ap.parse_args(argv)

    if args.freeze_registry:
        if not args.confirm_freeze:
            print("[FAIL] ★重建冻结表需要显式双确认: --freeze-registry --confirm-freeze★")
            print("★重建的触发条件 = 【盘面改过位号】⇒ ★不是【闸红了就重建】★")
            print("★只许在【盘面位号集合确实改过】、且【人工判过漂移名单】之后才重建★")
            return 2
        print("★★重建冻结表★★ ⇒ ★请确认: 盘面位号集合确实改过, 且你已逐条看过漂移名单★")
        return freeze_registry(args.root)

    if args.selftest:
        return run_selftest(args.root, args.tmpdir)

    try:
        res = analyze_mech(args.root)
    except InputError as exc:
        print(f"[FAIL] fail-closed: {exc}")
        print("★输入读不到 ⇒ 判红 (★不许「没读到就当过」★)")
        return 2
    print(format_report(res, verbose=not args.brief))
    ok = (res["baseline_ok"] and not res["drift"]
          and not res["baseline_integrity"] and not res["probe_failures"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
