#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_sw_ref_reachability.py — ISS-318 · SW 侧位号引用可达性闸
=================================================================================================
★★**这道闸判的是什么东西** ★ (★ISS-318 任务书 §1 第一件★):

  ★**义务 (逐字)**★: ★SW 侧每份文档里引用的每个位号, 必须能在【板文件】或【网表】里找到★
    ⇒ ★找不到 ⇒ 判红★ ⇒ ★并逐条列出「哪个文件 / 哪一行 / 引用的是谁 / 板与网表里现在叫什么」★

★★**为什么这道闸现在必须存在 (★ISS-318 §0-①·本机实读★)** ★:
  ★**ISS-314 (verified) 实测: 板那一趟的 S1 会给 156 个板位号加 `_1` 后缀** ★
  ⇒ ★**改完板, SW 侧文档里引用的位号就【对不上板了】** ★
  ⇒ ★**但 SW 侧当时 9 道闸全绿 (main 08:1x 实跑全绿)** ⇒ ★「全绿」不等于「改完板之后还对」★ ★
  ⇒ ⇒ ★这道闸就是那条「板只改一次那一趟」的 **SW 侧护栏** ★

★★★**★判据方向 (★不可改★)★** ★:
  ★**只问「你引用的位号现在存在吗」** ★ ⇒ ★**判据里不许写死「位号改名」这个具体方案** ★
  ⇒ ★**S1 走①还是走③, 这道闸都不用改** ★ ⇒ ★**正向用例 RC-6 专门证明这一点★**

★★★**★R2 · 分类规则 (★「不许把所有 R_/C_ 开头的东西都当位号」★)** ★:
  ★**每个 token 先分类, 再决定它该不该被查** ⇒ 分类规则全部写在本文件里 (★下面 §CLASSIFY★)
  ⇒ ★**一条命令复现全部分类**: `python3 SW/tools/check_sw_ref_reachability.py --dump-classification` ★

  | 类 | 含义 | 判红? |
  |---|---|---|
  | `DESIGNATOR_OK` | ★**真位号** · 现在能在板/网表里找到★ | 否 |
  | `DESIGNATOR_DRIFT` | ★**真位号** · 建闸时在板上 · 现在找不到了 (★改名漂移★) | ★**是** ★ |
  | `DESIGNATOR_MISSING` | ★**真隐患** · 形状像位号 · 板/网表里从来没有过 | ★**是** (★计入基线★) |
  | `NET_NAME` | ★**电源轨名 / 逻辑信号名** ⇒ 它本来就不是位号 | 否 |
  | `DOC_INTERNAL` | ★**文档自己的编号** (文档互引 / 锚点 / 环境变量键 / 物理符号 / 家族统称 / 模式字面量) | 否 |

  ★**规则按顺序命中, 第一条命中即停** ⇒ ★**顺序 = 优先级** ★

★★★**★R3 · 现状基线 (★实测, 不许估★)** ★:
  ★**建闸日 (2026-11-18) 本机实跑基线**: ★**`DESIGNATOR_MISSING` = 3 条** ★
    (`TP_INT` / `TP_TEMP` / `CONN_USB` —— ★逐条理由见 `BASELINE_TOKENS`★)
  ⇒ ★**这个数 = 闸的允许上限** ⇒ ★**不许为了让闸绿而放宽上限** ★
  ⇒ ★**收紧方向**: 每修好一条就把 `BASELINE_TOKENS` 里的它删掉 + 把 `BASELINE_COUNT` 减 1★

★★★**★R5 · fail-closed (★三条★)** ★:
  ★① 板文件读不到 ⇒ 判红 ② 网表读不到 ⇒ 判红 ③ 文档列表拿不到 (扫不到任何 `SW/*.md`) ⇒ 判红 ★
  ⇒ ★**不许「没读到就当过」** ⇒ ★**失效方向是安全的: 红, 不是假绿** ★

★★★**★边界 (★ISS-318 任务书 §1 第一件 硬约束★)** ★:
  · ★**零写板** (只读板文件文本, 不 import pcbnew, 不跑 KiCad) ★
  · ★**零落表** (只读网表 CSV, 不写) ★
  · ★**零改既有闸** (★本文件是【新建】的一道闸, 不碰 `state/gate_check.py`★) ★
  · ★**零改既有 SW 文档正文** (只读) ★

用法:
    python3 SW/tools/check_sw_ref_reachability.py                        # 主模式: rc=0 = 引用全部可达
    python3 SW/tools/check_sw_ref_reachability.py --dump-classification  # ★R2 一条命令复现全部分类★
    python3 SW/tools/check_sw_ref_reachability.py --selftest             # 反向用例 (≥5 条 + 不是巧合自证)
    python3 SW/tools/check_sw_ref_reachability.py --root .               # 指定项目根
    python3 SW/tools/check_sw_ref_reachability.py --freeze-registry      # ★重建 DESIGNATOR_REGISTRY 冻结表★
"""
from __future__ import annotations

import argparse
import csv
import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile

# =================================================================================================
# §CONFIG · 全部配置集中在这里 (★一条命令能复算★)
# =================================================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# ★**输入面 (★只读★)** ★
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
NETLIST_CSVS = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")
DOC_GLOB = "SW/*.md"
# ★**辅助索引面 (★给 C4/C5/C6 三条「文档自己的编号」规则用★)· 一层深★ ★
AUX_MD_DIRS = ("SW", "HW", "MECH", "state", "REF", "REQ", "PRINT", "config", "docs", "deploy")
AUX_PY_DIRS = ("SW/tools", "state", "HW")

# ★**token 宇宙 (★声明式·不写死任何具体位号★)** ★
#   · 前 12 个 = ★ISS-318 任务书 §0-① 的细口径 (main 08:1x 实跑口径)★ ★
#   · 后 4 个 = ★本单实测补齐★ (板上真有该前缀的位号, 且 SW 文档里引用得到)★ ★
#     - FB_  : 铁氧体 (本项目板上 1 个: FB_DEMO) · SW 文档引用 1 次 · 解析得到★ ★
#     - BT_  : 电芯 (BT_432243) · SW 文档引用 9 次 · 全部解析得到★ ★
#     - CONN_: 连接器 (CONN_CAM / CONN_LIGHT) · SW 文档引用 20 次 ★
#       ⇒ ★顺带抓到 CONN_USB (★已从网表消失的历史件·SW 文档里还留着引用★)★ ★
#     - CHG_ : 充电板侧 (CHG_GND_STAR 位号 / CHG_BOARD 板列 / CHG_STAT 网名) ★
#   · ★扩展口径时【只许加不许减】★ ⇒ ★减前缀 = 缩小覆盖面 = 判据变软 ★ ★
TOKEN_PREFIXES = (
    "R_", "C_", "U_", "J_", "D_", "L_", "Q_", "TP_", "LED_", "SW_", "VBUS_", "PWR_",
    "FB_", "BT_", "CONN_", "CHG_",
)

# ★**「电源轨名 / 逻辑信号名」命名空间 (★C11 规则用★)** ★
#   · 判据只问「这个 token 在板/网表里找不到」⇒ 网名本来就找不到 ⇒ 必须先把网名摘出去
#   · ★本项目板上位号前缀与本集合【无交集】 (★R_/C_/U_/J_/D_/L_/Q_/TP_/SW_/FB_/BT_/LED_★)★ ★
SIGNAL_PREFIXES = frozenset({
    "PWR_", "VBUS_", "NET_", "RAIL_", "BAT_", "SARADC_", "USB_", "DSI_", "CSI_",
    "SYS_", "CHG_", "GPIO_", "PG_", "RESET_", "INT_",
})

# ★**「物理量符号」命名空间 (★C10 规则用★)** ★
#   · 本项目板上【没有】`L_` 开头的位号 (铁氧体一律 `FB_`) ⇒ SW 文档里的 `L_B` / `L_eye` 是光学物理量
#   · ★若将来板上出现 `L_` 位号 ⇒ 必须把 `L_` 从这里移走 (并在同一个改动里更新本文件)★ ★
PHYSICS_PREFIXES = frozenset({"L_"})

# ★**「软件侧命名空间」前缀 (★C12 规则用★)** ★
#   · `SW_` 开头在本项目里 = SW 侧文档 / 锚点 / 环境变量键 / 条目编号 (`SW07_TP_INT` 这种)★
#   · ★例外: 板上真有 `SW_` 位号 (SW_BOOT / SW_KEY_PWR / SW_KEY_VM / SW_KEY_VP / SW_RST)★
#     ⇒ ★它们走 C1 (live 解析) 或 C2 (冻结注册表) 优先命中 ⇒ 不会被这条规则误伤★ ★
SOFTWARE_NS_PREFIX = "SW_"

# ★**板文件里位号的两种文本形态 (★KiCad 5/6/7 = fp_text·KiCad 8/9/10 = property★)** ★
BOARD_REF_PATTERNS = (
    re.compile(r'\(property\s+"Reference"\s+"([^"]+)"'),
    re.compile(r'\(fp_text\s+reference\s+"([^"]+)"'),
)

# ★**网表里「网名」的列 (★网名索引·三个来源都读★)** ★
NET_COLUMNS = ("net", "node1", "node2", "board")

# =================================================================================================
# §R3 · 现状基线 (★实测·2026-11-18 本机实跑·不许估★)
# =================================================================================================
# ★**允许上限 = 建闸日实测的 `DESIGNATOR_MISSING` 条数** ★
BASELINE_COUNT = 3

# ★**逐条理由 (★为什么这三条「本来就该对不上」/「真隐患」★)** ★
BASELINE_TOKENS = {
    "TP_INT": (
        "★真隐患·但已登记★: SW/BOARD_ONEPASS_SW_SYNC.md §SW06 明写「TP_INT (触控中断) 在网表和板上都不存在 "
        "⇒ SW 侧不许按『有触控中断』写代码」⇒ ★它是一个【被文档自己点名的空洞】★ "
        "⇒ 板那一趟若决定接触控, 必须同批落表 + 落位 + 布线, 否则 SW 侧引用永远是空的★"
    ),
    "TP_TEMP": (
        "★真隐患·未登记★: SW/SW_TIMING_REVIEW.md §CR-7 (EVT 上电段) 要求「TP_TEMP 热电偶对照标定」 "
        "⇒ ★板上 42 个 TP_* 里没有 TP_TEMP (只有 TP_USB_D_N / TP_KEY_PWR / TP_RESET 等)★ "
        "⇒ ★EVT 测温校准步骤依赖一个不存在的测试点 ⇒ 这就是本闸今天就抓得到的真隐患★"
    ),
    "CONN_USB": (
        "★真隐患·已登记★: SW/SW_TIMING_REVIEW.md L60/L272 明写「CONN_USB 已不在网表 ⇒ 对象消失 ⇒ 推翻」 "
        "⇒ ★它是【历史件】的遗留引用·文档自己已经知道它没了·但引用还留在文档里★"
    ),
}

# =================================================================================================
# §C2 · DESIGNATOR_REGISTRY (★建闸日冻结的「真位号」集合★)
# =================================================================================================
# ★**为什么要有这张表 (★不是多余的保险, 是必需的★)** ★:
#   ★**场景**: 板上有个位号 `TP_PG`, 同时板上还有 `TP_PG_VCORE` / `TP_PG_VIO` ★
#     ⇒ 若「家族统称」规则只看「是不是别的位号的前缀」, 那么 S1 改名之后 (板变成 `TP_PG_1` 等)
#     ⇒ ★`TP_PG` 会被误判成「家族统称」而溜过去 ⇒ 改名漂移就漏了★ ★
#   ⇒ ★**冻结表的作用**: 「这些 token 在建闸日【确确实实是位号】」 ⇒ ★改名之后它们必须仍然解析得到★
#     ⇒ ★不是巧合, 是设计★ ★
#   ⇒ ★**重建命令**: `python3 SW/tools/check_sw_ref_reachability.py --freeze-registry` ★
DESIGNATOR_REGISTRY = (
    "BT_432243",
    "CONN_CAM_1",
    "CONN_LIGHT_1",
    "C_DET_BAT_1",
    "C_DET_VBUS_D_1",
    "C_REGN_1",
    "C_RST_1",
    "C_SW_IN_1",
    "C_SW_OUT_1",
    "C_VBUS_DEMO_1",
    "C_VBUS_GND_1",
    "C_VBUS_OUT_1",
    "D_CHG_LED_1",
    "D_ESD_DEMO_1",
    "D_ESD_USB_D_1",
    "D_LED_B_1",
    "D_LED_G_1",
    "D_LED_R_1",
    "FB_DEMO_1",
    "J_CHG_1",
    "J_SOM_P1",
    "J_SOM_P2",
    "J_SOM_P3",
    "J_TYPE_C_1",
    "J_USB_C_1",
    "Q_AND_1",
    "Q_CHG_LED_1",
    "Q_ENVC_1",
    "Q_PG_1",
    "R_BAT_DET_1",
    "R_BAT_DET_2",
    "R_CC1",
    "R_CC2",
    "R_CE_1",
    "R_CHG_LED_1",
    "R_EN_VCORE_1",
    "R_ILIM_1",
    "R_PD_ON_1",
    "R_PG_PULL_1",
    "R_PU_BOOT_N_1",
    "R_PU_CHG_STAT_1",
    "R_PU_I2CA_SCL_1",
    "R_PU_I2CB_SCL_1",
    "R_PU_PG_1",
    "R_PU_RESET_N_1",
    "R_SER_RESET_N_1",
    "R_SER_USB_D_N_1",
    "R_SER_USB_D_P_1",
    "R_SUPV_DIV1",
    "R_SUPV_DIV2",
    "R_VBUS_DET_D1",
    "R_VBUS_DET_D2",
    "SW_BOOT_1",
    "SW_KEY_PWR_1",
    "SW_KEY_VM_1",
    "SW_KEY_VP_1",
    "SW_RST_1",
    "TP_BOOT_1",
    "TP_KEY_PWR_1",
    "TP_PG_VCORE_1",
    "TP_PG_VIO_1",
    "TP_RESET_1",
    "TP_USB_D_N_1",
    "U_BATPROT_1",
    "U_CHG_1",
    "U_DCDC_VCORE_1",
    "U_DCDC_VIO_1",
    "U_EN_SW_1",
    "U_LDO_IO18",
    "U_LDO_IO33",
    "U_LDO_L18",
    "U_LDO_L33",
    "U_LDO_S12",
    "U_LDO_S18B_1",
    "U_LDO_S28",
    "U_PWR_SW_1",
    "U_SUPV_1",
    "U_TEMP_1",
)
# ★共 78 条★  (★由 `--freeze-registry` 生成·建闸日 2026-11-18 实测★)

# =================================================================================================
# §CLASSIFY · R2 分类规则 (★按顺序命中, 第一条命中即停★)
# =================================================================================================
CLASS_RULES = {
    "C1": "★live 解析: token 现在能在【板文件】或【网表】里找到 ⇒ 真位号·存在★",
    "C2": "★冻结注册表: token 在建闸日是位号, 现在找不到了 ⇒ 真位号·【改名漂移】★",
    "C3": "★网名: token 是【电源轨名 / 逻辑信号名】 ⇒ 它本来就不是位号★",
    "C4": "★文档互引: 盘上存在 `<目录>/<token>.md` ⇒ 文档自己的编号★",
    "C5": "★文档锚点: 盘上某 .md 里有 `# BEGIN/END <token>` ⇒ 文档自己的编号★",
    "C6": "★环境变量键: 盘上某 .py 把它当环境变量键用 ⇒ 文档自己的编号★",
    "C7": "★物理符号: token 的后缀段里含【小写字母】 ⇒ 物理量 (R_on / R_th / L_eye)★",
    "C8": "★前缀截断: token 以 `_` 结尾 ⇒ 文本被截断 (R_BAT_DET_)★",
    "C9": "★模式字面量: token 的【每一次】出现都紧跟在 `|` 之后 ⇒ 判据正文里的 grep pattern★",
    "C10": "★物理量命名空间: token 的前缀 ∈ PHYSICS_PREFIXES (L_) ⇒ 光学物理量★",
    "C11": "★信号命名空间: token 的前缀 ∈ SIGNAL_PREFIXES ⇒ 电源轨名 / 逻辑信号名★",
    "C12": "★家族统称: token 是 ≥2 个 live 位号的严格前缀 ⇒ 文档对一组件的统称 (R_SUPV_DIV)★",
    "C13": "★软件侧命名空间: token 以 `SW_` 开头 ⇒ 文档 / 锚点 / 环境变量键 / 条目编号★",
    "C14": "★兜底: 形状像位号, 板/网表里从来没有过 ⇒ 【真隐患】★",
}

FAIL_CLASSES = ("DESIGNATOR_DRIFT", "DESIGNATOR_MISSING")


# =================================================================================================
# §IO · 只读收集 (★零写板 · 零落表★)
# =================================================================================================
class InputError(Exception):
    """★fail-closed: 输入读不到 ⇒ 抛这个 ⇒ 判红 (★不许静默跳过★)"""


def _read_text(path: str) -> str:
    if not os.path.isfile(path):
        raise InputError(f"★输入文件不存在: {path}")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as exc:
        raise InputError(f"★输入文件读不了: {path} ({exc})") from exc


def read_board_refs(board_path: str) -> set:
    """★从板文件【文本】里抽位号 (★不许 import pcbnew ⇒ 不需要 root★)★"""
    txt = _read_text(board_path)
    refs = set()
    for pat in BOARD_REF_PATTERNS:
        for m in pat.finditer(txt):
            ref = m.group(1).strip()
            if ref:
                refs.add(ref)
    if not refs:
        raise InputError(f"★板文件里一个位号都没抽到 (板文件格式变了?): {board_path}")
    return refs


def read_netlist_refs(net_names: set) -> set:
    """★从三张网表 CSV 的 `ref` 列抽位号★"""
    refs = set()
    for rel in NETLIST_CSVS:
        path = os.path.join(net_names["root"], rel)
        if not os.path.isfile(path):
            raise InputError(f"★网表真源不存在: {rel}")
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            rdr = csv.DictReader(fh)
            if rdr.fieldnames is None or "ref" not in rdr.fieldnames:
                raise InputError(f"★网表 CSV 没有 `ref` 列: {rel}")
            for row in rdr:
                val = (row.get("ref") or "").strip()
                if val:
                    refs.add(val)
    return refs


def read_net_names(root: str) -> set:
    """★网名索引 (★电源轨名 / 逻辑信号名 ⇒ C3 规则用★)★"""
    names = set()
    for rel in NETLIST_CSVS:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            raise InputError(f"★网表真源不存在: {rel}")
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            rdr = csv.DictReader(fh)
            for row in rdr:
                for col in NET_COLUMNS:
                    val = (row.get(col) or "").strip()
                    if val:
                        names.add(val)
    # ★板文件里的网名 (KiCad 10 文本形态: (net "NAME")★)
    board_path = os.path.join(root, BOARD_REL)
    if os.path.isfile(board_path):
        txt = _read_text(board_path)
        for m in re.finditer(r'\(net\s+"([^"]+)"', txt):
            names.add(m.group(1).strip())
    return names


def collect_doc_tokens(root: str):
    """★扫 SW 侧文档 ⇒ token → [(相对路径, 行号, 行文本)]★"""
    import glob
    files = sorted(glob.glob(os.path.join(root, DOC_GLOB)))
    if not files:
        raise InputError(f"★SW 侧文档列表拿不到 (glob `{DOC_GLOB}` 空): {root}")
    pat = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")
    occ = {}
    n_docs = len(files)
    for path in files:
        rel = os.path.relpath(path, root)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, 1):
                    for m in pat.finditer(line):
                        tok = m.group(0)
                        occ.setdefault(tok, []).append((rel, lineno, line.rstrip("\n")))
        except OSError as exc:
            raise InputError(f"★SW 侧文档读不了: {rel} ({exc})") from exc
    if not occ:
        raise InputError(f"★SW 侧文档里一个 token 都没抽到 (口径变了?): {root}")
    return occ, n_docs


def build_aux_index(root: str):
    """★辅助索引: 文档互引 (C4) / 文档锚点 (C5) / 环境变量键 (C6)★"""
    import glob
    md_paths = []
    for d in AUX_MD_DIRS:
        md_paths += sorted(glob.glob(os.path.join(root, d, "*.md")))
    md_paths += sorted(glob.glob(os.path.join(root, "*.md")))
    py_paths = []
    for d in AUX_PY_DIRS:
        py_paths += sorted(glob.glob(os.path.join(root, d, "*.py")))

    doc_files = set()
    anchors = set()
    for p in md_paths:
        rel = os.path.relpath(p, root)
        noext = os.path.splitext(rel)[0]
        doc_files.add(noext)                       # ★相对路径去扩展名 (HW/R_GEO_...md ⇒ HW/R_GEO_...)★ ★
        doc_files.add(os.path.splitext(os.path.basename(rel))[0])   # ★纯文件名去扩展名 (⇒ R_GEO_...)★ ★
        try:
            txt = open(p, "r", encoding="utf-8", errors="replace").read()
        except OSError as exc:
            raise InputError(f"★辅助索引读不了: {rel} ({exc})") from exc
        for m in re.finditer(r"#\s*(?:BEGIN|END)\s+([A-Za-z0-9_]+)", txt):
            anchors.add(m.group(1))

    env_keys = set()
    env_pat = re.compile(r"os\.environ(?:\.get\(|\.setdefault\(|\.pop\(|\[)\s*[\"']([A-Za-z0-9_]+)[\"']")
    for p in py_paths:
        rel = os.path.relpath(p, root)
        try:
            txt = open(p, "r", encoding="utf-8", errors="replace").read()
        except OSError as exc:
            raise InputError(f"★辅助索引读不了: {rel} ({exc})") from exc
        for m in env_pat.finditer(txt):
            env_keys.add(m.group(1))
    return doc_files, anchors, env_keys


# =================================================================================================
# §CLASSIFY · 分类 (★R2★)
# =================================================================================================
def classify(token: str, idx: dict, occ: list):
    """★返回 (class, rule_id, 说明)★"""
    live = idx["live_refs"]
    nets = idx["net_names"]

    # C1 · live 解析
    if token in live:
        where = []
        if token in idx["board_refs"]:
            where.append("板文件")
        if token in idx["netlist_refs"]:
            where.append("网表")
        return ("DESIGNATOR_OK", "C1", f"现在在【{'+'.join(where)}】里能找到")

    # C2 · 冻结注册表 ⇒ 改名漂移
    if token in idx["registry"]:
        return ("DESIGNATOR_DRIFT", "C2",
                "★建闸日它在板/网表里是真位号, 现在找不到了 ⇒ 【改名漂移】★")

    # C3 · 网名
    if token in nets:
        return ("NET_NAME", "C3", "它是【电源轨名 / 逻辑信号名】, 本来就不是位号")

    # C4 · 文档互引
    if token in idx["doc_files"]:
        return ("DOC_INTERNAL", "C4", "盘上有一份同名文档 ⇒ 文档自己的编号 (文档互引)")

    # C5 · 文档锚点
    if token in idx["anchors"]:
        return ("DOC_INTERNAL", "C5", "盘上某 .md 里有 `# BEGIN/END <token>` ⇒ 文档锚点")

    # C6 · 环境变量键
    if token in idx["env_keys"]:
        return ("DOC_INTERNAL", "C6", "盘上某 .py 把它当环境变量键用 ⇒ 判据/夹具的键名")

    # C7 · 物理符号 (后缀含小写字母)
    if re.search(r"[a-z]", token):
        return ("DOC_INTERNAL", "C7", "后缀含小写字母 ⇒ 物理量符号 (不是位号)")

    # C8 · 前缀截断
    if token.endswith("_"):
        return ("DOC_INTERNAL", "C8", "以 `_` 结尾 ⇒ 文本被截断的前缀")

    # C9 · 模式字面量 (每次出现都紧跟在 `|` 之后)
    if occ and all(_preceded_by_pipe(line, token) for _rel, _ln, line in occ):
        return ("DOC_INTERNAL", "C9", "每次出现都紧跟在 `|` 之后 ⇒ 判据正文里的 grep pattern")

    # C10 · 物理量命名空间
    prefix = token.split("_", 1)[0] + "_"
    if prefix in PHYSICS_PREFIXES:
        return ("DOC_INTERNAL", "C10", f"前缀 `{prefix}` ∈ 物理量命名空间 (本项目板上无该前缀位号)")

    # C11 · 信号命名空间
    if prefix in SIGNAL_PREFIXES:
        return ("NET_NAME", "C11", f"前缀 `{prefix}` ∈ 电源轨名/逻辑信号名命名空间")

    # C12 · 家族统称 (≥2 个 live 位号的严格前缀)
    kids = [r for r in live if r != token and r.startswith(token)]
    if len(kids) >= 2:
        return ("DOC_INTERNAL", "C12",
                f"是 ≥2 个 live 位号的严格前缀 ({', '.join(sorted(kids)[:4])}) ⇒ 文档对一组件的统称")

    # C13 · 软件侧命名空间
    if token.startswith(SOFTWARE_NS_PREFIX):
        return ("DOC_INTERNAL", "C13", "`SW_` 开头 ⇒ SW 侧文档 / 锚点 / 环境变量键 / 条目编号")

    # C14 · 兜底 ⇒ 真隐患
    return ("DESIGNATOR_MISSING", "C14", "形状像位号, 但板/网表里从来没有过 ⇒ 【真隐患】")


def _preceded_by_pipe(line: str, token: str) -> bool:
    idx = line.find(token)
    while idx != -1:
        if idx > 0 and line[idx - 1] == "|":
            return True
        idx = line.find(token, idx + 1)
    return False


# =================================================================================================
# §ANALYZE · 主判定
# =================================================================================================
def analyze(root: str):
    """★跑一遍 ⇒ 返回结构化结果 (★主模式与 --selftest 共用同一份逻辑★)★"""
    root = os.path.abspath(root)
    board_path = os.path.join(root, BOARD_REL)
    board_refs = read_board_refs(board_path)
    netlist_refs = read_netlist_refs({"root": root})
    net_names = read_net_names(root)
    occ, n_docs = collect_doc_tokens(root)
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
        "registry": set(DESIGNATOR_REGISTRY),
        "occ": occ,
    }

    rows = []
    for tok in sorted(occ):
        cls, rule, note = classify(tok, idx, occ[tok])
        rows.append({"token": tok, "cls": cls, "rule": rule, "note": note, "occ": occ[tok]})

    drift = [r for r in rows if r["cls"] == "DESIGNATOR_DRIFT"]
    missing = [r for r in rows if r["cls"] == "DESIGNATOR_MISSING"]

    # ★**基线判定 (★R3: 上限不许放宽★)** ★
    new_missing = [r for r in missing if r["token"] not in BASELINE_TOKENS]
    missing_total = len(missing)
    baseline_ok = (missing_total <= BASELINE_COUNT) and (not new_missing)
    resolved_baseline = sorted(t for t in BASELINE_TOKENS if t not in {r["token"] for r in missing})

    return {
        "root": root,
        "live_refs": live_refs,
        "docs_scanned": n_docs,
        "rows": rows,
        "drift": drift,
        "missing": missing,
        "new_missing": new_missing,
        "missing_total": missing_total,
        "baseline_count": BASELINE_COUNT,
        "baseline_ok": baseline_ok,
        "resolved_baseline": resolved_baseline,
        "board_refs_n": len(board_refs),
        "netlist_refs_n": len(netlist_refs),
        "net_names_n": len(net_names),
        "tokens_n": len(rows),
        "docs_n": len({rel for r in rows for rel, _ln, _l in r["occ"]}),
    }


def suggest_names(token: str, live: set, limit: int = 6):
    """★「板与网表里现在叫什么」· 给出最接近的候选 (★difflib·stdlib★)★"""
    pool = sorted(live)
    cand = set()
    for r in pool:
        if r.startswith(token) or token.startswith(r):
            cand.add(r)
    for r in difflib.get_close_matches(token, pool, n=limit, cutoff=0.75):
        cand.add(r)
    return sorted(cand)[:limit]


def format_report(res: dict, verbose: bool = True) -> str:
    out = []
    live = res["rows"]
    L = out.append
    L("=" * 74)
    L("ISS-318 · SW 侧位号引用可达性闸 · check_sw_ref_reachability.py")
    L("=" * 74)
    L(f"项目根        : {res['root']}")
    L(f"板位号        : {res['board_refs_n']} 个 (★板文件文本解析, 未 import pcbnew★)")
    L(f"网表位号      : {res['netlist_refs_n']} 个 (★三张 CSV 的 ref 列★)")
    L(f"网名索引      : {res['net_names_n']} 个")
    L(f"扫描文档      : {res.get('docs_scanned', res['docs_n'])} 份 `SW/*.md` (★其中 {res['docs_n']} 份含至少一个 token★)")
    L(f"抽出 token    : {res['tokens_n']} 个唯一标识符")
    L("")
    counts = {}
    for r in live:
        counts[r["cls"]] = counts.get(r["cls"], 0) + 1
    L("【分类统计】 (★R2★)")
    for cls in ("DESIGNATOR_OK", "DESIGNATOR_DRIFT", "DESIGNATOR_MISSING", "NET_NAME", "DOC_INTERNAL"):
        L(f"   {cls:22s} {counts.get(cls, 0):4d}")
    L("")
    L(f"【R3 现状基线】 `DESIGNATOR_MISSING` 实测 = {res['missing_total']} 条 · 允许上限 = {res['baseline_count']} 条")
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
            for s in suggest_names(r["token"], res["_live"]):
                L(f"        板/网表里现在叫: {s}")
            for rel2, ln2, _l2 in r["occ"][1:4]:
                L(f"        另外还出现在: {rel2}:{ln2}")
            L(f"        判红理由: {r['note']}")
        L("")
    if res["missing"]:
        L("【★真隐患 (C14)·现在就对不上的位号引用★】")
        for r in res["missing"]:
            rel, ln, _line = r["occ"][0]
            tag = "★基线内·已登记★" if r["token"] in BASELINE_TOKENS else "★★超基线★★"
            L(f"   {tag} {r['token']}  ({rel}:{ln})  出现 {len(r['occ'])} 次")
            L(f"        理由: {BASELINE_TOKENS.get(r['token'], '★不在建闸日基线里 ⇒ 这是新增的真隐患★')}")
            for s in suggest_names(r["token"], res["_live"]):
                L(f"        板/网表里现在叫: {s}")
        L("")
    # ★**FAIL 行 (★挂进门禁链后 `run_external_gate()` 靠 stdout 的 [FAIL] 行抽原因★)** ★
    for r in res["drift"]:
        rel, ln, _line = r["occ"][0]
        cands = ", ".join(suggest_names(r["token"], res["_live"])) or "(无近似名)"
        L(f"[FAIL] 位号引用解析不到 (改名漂移): {r['token']} @ {rel}:{ln} "
          f"⇒ 板与网表里现在叫: {cands}")
    for r in res["new_missing"]:
        rel, ln, _line = r["occ"][0]
        cands = ", ".join(suggest_names(r["token"], res["_live"])) or "(无近似名)"
        L(f"[FAIL] 位号引用解析不到 (新增真隐患·超基线): {r['token']} @ {rel}:{ln} "
          f"⇒ 板与网表里现在叫: {cands}")
    if res["missing_total"] > res["baseline_count"]:
        L(f"[FAIL] 真隐患条数 {res['missing_total']} > 基线上限 {res['baseline_count']} "
          f"(★基线只许收紧不许放宽★)")
    if not res["baseline_ok"] and not res["drift"] and not res["new_missing"]:
        L(f"[FAIL] 真隐患条数 {res['missing_total']} 超基线上限 {res['baseline_count']}")
    if verbose:
        L("")
        L("【R2 分类全表】 (★`--dump-classification` 同源★)")
        for r in res["rows"]:
            L(f"   {r['cls']:20s} {r['rule']:4s} {r['token']:44s} {r['note']}")
    L("")
    ok = res["baseline_ok"] and not res["drift"]
    L(f"【判决】 {'✔ 绿 (rc=0): SW 侧引用的位号全部可达, 真隐患在基线内' if ok else '✘ 红 (rc≠0)'}")
    return "\n".join(out)


# =================================================================================================
# §SELFTEST · 反向用例 (★R4: ≥3 条 + 每条带「不是巧合」自证★)
# =================================================================================================
def _copy_input_surface(src_root: str, dst_root: str):
    """★把闸要读的那一面拷进沙盒 (★真拷贝, 绝不 hardlink★)★"""
    import glob
    os.makedirs(dst_root, exist_ok=True)
    rels = [BOARD_REL] + list(NETLIST_CSVS)
    for rel in rels:
        s = os.path.join(src_root, rel)
        d = os.path.join(dst_root, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
    for pat in (DOC_GLOB,):
        for p in sorted(glob.glob(os.path.join(src_root, pat))):
            d = os.path.join(dst_root, os.path.relpath(p, src_root))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(p, d)
    for d in AUX_MD_DIRS:
        for p in sorted(glob.glob(os.path.join(src_root, d, "*.md"))):
            t = os.path.join(dst_root, os.path.relpath(p, src_root))
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(p, t)
    for d in AUX_PY_DIRS:
        for p in sorted(glob.glob(os.path.join(src_root, d, "*.py"))):
            t = os.path.join(dst_root, os.path.relpath(p, src_root))
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(p, t)


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
    with open(path, "w", encoding="utf-8", newline="") as fh:
        wr = _csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for row in rows:
            wr.writerow(row)
    return n


def _gate_rc(root: str):
    """★在沙盒根上跑一遍闸的主判定 ⇒ (rc, 明细) (★0=绿·1=红·2=输入读不到⇒fail-closed 判红★)★"""
    try:
        res = analyze(root)
    except InputError as exc:
        return 2, [f"fail-closed: {exc}"]
    detail = []
    for r in res["drift"]:
        detail.append(f"改名漂移:{r['token']}")
    for r in res["new_missing"]:
        detail.append(f"新增真隐患:{r['token']}")
    if res["missing_total"] > res["baseline_count"]:
        detail.append(f"真隐患 {res['missing_total']} > 基线 {res['baseline_count']}")
    return (0 if (res["baseline_ok"] and not res["drift"]) else 1), detail


def run_selftest(root: str, tmpdir: str = "") -> int:
    root = os.path.abspath(root)
    base = tmpdir or os.path.join(root, "tmp", "iss318_tmp")
    os.makedirs(base, exist_ok=True)
    work = tempfile.mkdtemp(prefix="iss318_refreach_", dir=base)

    cases = []          # (用例名, 期望, 破坏动作, 说明)

    def case(name, expect, desc):
        cases.append((name, expect, desc))

    case("RC-1", "red", "★SW 文档里写一个板上从来没有的位号 ⇒ 必须红★")
    case("RC-2", "red", "★板文件里把一个 SW 文档引用的位号删掉 (★模拟 S1 改名★) ⇒ 必须红★")
    case("RC-3", "red", "★网表里把一个 SW 文档引用的位号删掉 ⇒ 必须红★")
    case("RC-4", "red", "★板文件读不到 ⇒ 必须红 (fail-closed★)")
    case("RC-5", "red", "★网表读不到 ⇒ 必须红 (fail-closed★)")
    case("RC-6", "green", "★板改名 + SW 文档同步改成新名 ⇒ 必须绿 (★证明判据没写死「改名方案」★)")
    case("RC-7", "green", "★原样不动 ⇒ 必须绿 (★正向对照·不许把闸修成永远红★)")

    results = []
    for name, expect, desc in cases:
        sandbox = os.path.join(work, name)
        _copy_input_surface(root, sandbox)
        # —— 「不是巧合」自证: 同一棵沙盒树, 破坏之前必须判绿 ——
        rc_before, det_before = _gate_rc(sandbox)
        # —— 破坏 ——
        if name == "RC-1":
            p = os.path.join(sandbox, "SW", "SW_TIMING_REVIEW.md")
            with open(p, "a", encoding="utf-8") as fh:
                fh.write("\n<!-- ISS318 RC-1 -->\nprobe part: `R_ZZ_ISS318_FAKE_999` 假装位号\n")
        elif name == "RC-2":
            # ★模拟 S1 改名: 板 + 三张网表【同步】改名 ⇒ 旧名在盘上彻底消失 ★
            p = os.path.join(sandbox, BOARD_REL)
            txt = open(p, "r", encoding="utf-8", errors="replace").read()
            txt = txt.replace('(property "Reference" "C_DET_BAT"', '(property "Reference" "C_DET_BAT_1"', 1)
            open(p, "w", encoding="utf-8").write(txt)
            for rel in NETLIST_CSVS:
                _rewrite_ref(os.path.join(sandbox, rel), "C_DET_BAT", "C_DET_BAT_1")
        elif name == "RC-3":
            # ★网表三张【全部】抹掉一个 SW 文档引用的位号 (★R_ILIM 是【只在网表里】的件·不在板上·所以只抹网表就能真的抹掉它★)★
            for rel in NETLIST_CSVS:
                _rewrite_ref(os.path.join(sandbox, rel), "R_ILIM", "")
        elif name == "RC-4":
            os.remove(os.path.join(sandbox, BOARD_REL))
        elif name == "RC-5":
            os.remove(os.path.join(sandbox, "HW", "netlist_v1.csv"))
        elif name == "RC-6":
            # ★板改名 + 网表同步改名 + 文档同步改 ⇒ 必须绿 (★判据只问「存在吗」★)★
            p = os.path.join(sandbox, BOARD_REL)
            txt = open(p, "r", encoding="utf-8", errors="replace").read()
            txt = txt.replace('(property "Reference" "C_DET_BAT"', '(property "Reference" "C_DET_BAT_1"', 1)
            open(p, "w", encoding="utf-8").write(txt)
            for rel in NETLIST_CSVS:
                _rewrite_ref(os.path.join(sandbox, rel), "C_DET_BAT", "C_DET_BAT_1")
            # ★★2026-11-18 16:1x (sw-lead · ISS-318 cont1 收尾) · 【夹具补全·不是放宽判据】★★
            #   ★**病灶 (实测)**: 旧夹具只把 `C_DET_BAT` 改成新名写在【两份硬编码文档】里
            #     (`SW/SW_TIMING_REVIEW.md` + `SW/ADC_CALIBER_TABLE.md`)
            #     ⇒ ★**IS-323 (2026-11-18 14:39 / 16:17) 又新增了两份含 `C_DET_BAT` 的文档**
            #       (`SW/ONETRIP_SW_RENAME_SAFETY.md` + `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md`)
            #       ⇒ 那两份文档仍引用旧名 ⇒ 板/网表里已无此位号 ⇒ 闸【正确地】判「改名漂移:C_DET_BAT」红
            #       ⇒ ★⇒ RC-6 假红 (6/7)★
            #   ★**为什么这是【夹具缺陷】不是【判据缺陷】**: RC-6 要测的是「板改名 + **文档同步**改新名 ⇒ 必须绿」
            #     ⇒ ★**「文档同步」的定义就是【所有引用该位号的文档都改了】** ⇒ 夹具只改两份 = 没实现被测场景★
            #     ⇒ ★**修法 = 把夹具改成【按 token 驱动·扫全部文档】** ⇒ 判据 (R1~R5 的判红口径) 一个字没动★
            #     ⇒ ★**这正是项目铁律「修夹具 ≠ 放宽判据」的正面用法: 修在夹具, 不碰判据★**
            #   ★**零写板**: 这一段全部在沙盒副本里做 (真拷贝·绝不 hardlink) ⇒ 真盘一个字节都不写★
            import glob as _glob
            _old, _new = "C_DET_BAT", "C_DET_BAT_1"
            for d in sorted(_glob.glob(os.path.join(sandbox, DOC_GLOB))):
                txt = open(d, "r", encoding="utf-8", errors="replace").read()
                if _old not in txt:
                    continue
                open(d, "w", encoding="utf-8").write(txt.replace(_old, _new))

        # —— 破坏之后 ——
        rc_after, det_after = _gate_rc(sandbox)
        if expect == "red":
            ok = (rc_after != 0) and (rc_before == 0)
        else:
            ok = (rc_after == 0) and (rc_before == 0)
        results.append((name, expect, desc, rc_before, rc_after, ok, det_before, det_after))
        shutil.rmtree(sandbox, ignore_errors=True)
    shutil.rmtree(work, ignore_errors=True)

    print("=" * 74)
    print("ISS-318 · SW 侧位号引用可达性闸 · 反向用例 (★R4★)")
    print("=" * 74)
    print(f"沙盒根: {base}   (★真拷贝·绝不 hardlink·真盘一个字节都不写★)")
    print("-" * 74)
    passed = 0
    for name, expect, desc, rc_before, rc_after, ok, det_before, det_after in results:
        mark = "✅" if ok else "❌"
        print(f"  {mark} {name} 期望={expect:5s} 破坏前 rc={rc_before}  破坏后 rc={rc_after}  {desc}")
        if expect == "red":
            print(f"      ★不是巧合自证★: 同一棵沙盒树·破坏前 rc={rc_before} "
                  f"(红项: {', '.join(det_before) if det_before else '无'}) ⇒ 破坏后 rc={rc_after} "
                  f"(红项: {', '.join(det_after) if det_after else '无'}) "
                  f"⇒ 这条红【只可能】来自被改坏的那一处")
        else:
            print(f"      ★不是巧合自证★: 同一棵沙盒树·破坏前 rc={rc_before} ⇒ 破坏后 rc={rc_after} "
                  f"(红项: {', '.join(det_after) if det_after else '无'}) "
                  f"⇒ ★判据没被「改坏的那一处」弄红 (★正向对照: 闸没被修成永远红★)")
        if ok:
            passed += 1
        else:
            print(f"      ★用例没过★ 破坏前 rc={rc_before} (★必须 0 ⇒ 才叫「不是巧合」★) 破坏后 rc={rc_after}")
    print("-" * 74)
    print(f"反向用例: {passed}/{len(results)} 通过")
    if passed == len(results):
        print("✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没 ★)")
        return 0
    print("❌ 有用例没抓到 ⇒ 判据可能没被真读")
    return 1


# =================================================================================================
# §FREEZE · 重建 DESIGNATOR_REGISTRY (★一条命令★)
# =================================================================================================
def freeze_registry(root: str) -> int:
    root = os.path.abspath(root)
    try:
        board_refs = read_board_refs(os.path.join(root, BOARD_REL))
        netlist_refs = read_netlist_refs({"root": root})
        net_names = read_net_names(root)
        occ, _n_docs = collect_doc_tokens(root)
        doc_files, anchors, env_keys = build_aux_index(root)
    except InputError as exc:
        print(f"[FAIL] {exc}")
        return 2
    live = board_refs | netlist_refs
    idx = {
        "root": root, "board_refs": board_refs, "netlist_refs": netlist_refs,
        "live_refs": live, "net_names": net_names, "doc_files": doc_files,
        "anchors": anchors, "env_keys": env_keys, "registry": set(),
    }
    keep = []
    for tok in sorted(occ):
        cls, _rule, _note = classify(tok, idx, occ[tok])
        if cls == "DESIGNATOR_OK":
            keep.append(tok)
    print("DESIGNATOR_REGISTRY = (")
    for tok in keep:
        print(f'    "{tok}",')
    print(")")
    print(f"# ★共 {len(keep)} 条★  (★由 `--freeze-registry` 生成·建闸日 2026-11-18 实测★)")
    return 0


# =================================================================================================
# §MAIN
# =================================================================================================
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT, help="项目根 (默认: 脚本上两级)")
    ap.add_argument("--selftest", action="store_true", help="反向用例")
    ap.add_argument("--dump-classification", action="store_true",
                    help="★R2: 打印全部分类 (一条命令复现分类规则★)")
    ap.add_argument("--freeze-registry", action="store_true", help="重建 DESIGNATOR_REGISTRY")
    ap.add_argument("--tmpdir", default="", help="沙盒临时树根目录")
    ap.add_argument("--brief", action="store_true", help="不打印分类全表")
    args = ap.parse_args(argv)

    if args.freeze_registry:
        return freeze_registry(args.root)
    if args.selftest:
        return run_selftest(args.root, args.tmpdir)

    try:
        res = analyze(args.root)
    except InputError as exc:
        print(f"[FAIL] fail-closed: {exc}")
        print("★输入读不到 ⇒ 判红 (★不许「没读到就当过」★)")
        return 2
    res["_live"] = res["live_refs"]
    print(format_report(res, verbose=not args.brief))
    ok = res["baseline_ok"] and not res["drift"]
    return 0 if ok else 1


def _live_refs(root: str) -> set:
    try:
        return read_board_refs(os.path.join(root, BOARD_REL)) | read_netlist_refs({"root": root})
    except InputError:
        return set()


if __name__ == "__main__":
    sys.exit(main())
