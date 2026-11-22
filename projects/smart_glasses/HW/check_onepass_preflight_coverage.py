#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-277 · 「板只改一次」板侧漏项【覆盖度闸】 —— 清单页 + 作业包 + 交卷单三处一致性的机器判据
=================================================================================================
派活: state/dispatch_briefs/ISS-277_hw_onepass_preflight_coverage.md (项目总工 2026-11-17 07:3x)

★**本闸守的是「清单全不全 / 清不新鲜」, 不是板** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★

六条判据:
  P1 清单可解析  : JSON 块能解析 + 每条固定 9 个字段齐全 (★缺一个即红★) + 字段非空
  P2 归属步合法  : `step` ∈ S1~S13 + ★S1~S13 每步至少被覆盖一次★ (★不许有步没人管★)
  P3 判据命令真存在: 每条 `criterion` 里引用的脚本文件在本机真实存在 (★不许把不存在的命令写进清单★)
  P4 覆盖度      : ★本闸核心★ —— 25 个板侧标记每个都必须在清单里出现 (★漏一条即红★)
                    + 反向: 每条 `source_iss` 必须落在来源单全集里 (★不许有来源不明的项★)
  P5 现状一致    : ★标 [实测] 的现状值必须与盘面实测一致★ (★改了盘面没改清单 = 清单过期 = 当场红★)
  P6 受保护 5 件 : 板 / .kicad_pro / 网表 / 脚表 / BOM 的 md5 逐字节不变

★**★P4 是本单的核心判据**: ★**「只在交卷单里、没进清单」的漏项才会被抓住** ⇒ ★**漏做一项 = 板 md5 变第二次** ★
★**★P5 是防「清单变成第二份过期文档」的关键**: 盘面一变, 清单不跟 = 当场红 ★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 HW/check_onepass_preflight_coverage.py            # 主模式
  python3 HW/check_onepass_preflight_coverage.py --selftest  # 反向用例 (≥6 条, 每条自证改到了目标)
  ★自检用 env 覆盖★: PREFLIGHT_CHECKLIST / PREFLIGHT_PCB / PREFLIGHT_PRO /
                     PREFLIGHT_NETLIST / PREFLIGHT_PINS / PREFLIGHT_BOM
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
# ★★ISS-283 · ⑩-b: 落表台账的 md5 注册表 (★网表/脚表/BOM 的基线走「落表台账为准」★) ★★
sys.path.insert(0, HERE)
import landing_md5
# ★★ISS-297 · 2026-11-17 20:3x (hw-lead): HW 侧「合法改板」通道 (★共用判决库·不许自己再写一份★)
import board_reboard                                          # noqa: E402

CHECKLIST = os.environ.get("PREFLIGHT_CHECKLIST") or os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")

def protected_map():
    """★受保护 5 件 (★每次调用都重读 env ⇒ --selftest 能在运行中换路径 ★)

    ★★ISS-283 · ⑩-b (★2026-11-17 12:4x 实测★): 网表 / 脚表 / BOM 三件的基线 【不再写死】★★
      ⇒ 改成 ★**「落表台账为准」**★ (★`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 的最新登记★)
      ⇒ ★★**理由: 只把基线数字改成新值 = 下次落表又红一遍 ⇒ 判据的【取值来源】必须变·不是【取值】变★★**
      ⇒ ★**台账里查不到 / 链头不唯一 / 链断 / 四项不齐 ⇒ 一律红** (★fail-closed·见 `HW/landing_md5.py`★) ★
    ★**板 / `.kicad_pro` 两件的基线照旧写死** (★它们不归落表链管 ⇒ 那两条一条不许动★) ★
    ⇒ 返回值第 2 项 = 写死的基线 (None = 走落表台账) · 第 3 项 = 该件的相对路径 (查台账要用★)
    """
    return {
        "板": (os.environ.get("PREFLIGHT_PCB") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"),
               "611b869e13518c3c023fb178f91a0075",
               "HW/PCB/demo_mainboard.kicad_pcb"),
        ".kicad_pro": (os.environ.get("PREFLIGHT_PRO") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pro"),
                       "3e504d2be83152e337949723e909be1b",
                       "HW/PCB/demo_mainboard.kicad_pro"),
        "网表": (os.environ.get("PREFLIGHT_NETLIST") or os.path.join(PROJ, "HW", "netlist_v1.csv"),
                 # ★★ISS-283 · ⑩-b: 不写死 ⇒ 走「落表台账为准」 (★出处 = 落表台账 §16.2★) ★★
                 None,
                 "HW/netlist_v1.csv"),
        "脚表": (os.environ.get("PREFLIGHT_PINS") or os.path.join(PROJ, "HW", "netlist_v1_pins.csv"),
                 # ★★ISS-283 · ⑩-b: 不写死 ⇒ 走「落表台账为准」 ★★
                 None,
                 "HW/netlist_v1_pins.csv"),
        "BOM": (os.environ.get("PREFLIGHT_BOM") or os.path.join(PROJ, "HW", "BOM_v1.csv"),
                # ★★ISS-283 · ⑩-b: 不写死 ⇒ 走「落表台账为准」 ★★
                None,
                "HW/BOM_v1.csv"),
    }

FIELDS = ("id", "source_iss", "title", "current_state", "action",
          "criterion", "step", "blocked_by", "evidence")

STEPS = ["S%d" % i for i in range(1, 14)]

# ★P4 的覆盖度标记 (★从 6 份来源交卷单反查出来的板侧项标记 ★)
MARKERS = ["D_ESD_CAM", "Q_AND", "Q_PG", "D_ESD_TC", "U_LDO_S28", "J_CHG",
           "D_CHG_LED", "D_LED_G", "D_LED_R", "SW_BOOT", "SW_KEY_PWR",
           "SW_KEY_VM", "SW_KEY_VP", "SW_RST", "R_SEL_D3_P", "J_DEBUG",
           "J_UART", "R_SUPV_DIV", "U_SUPV", "TPS7A20", "Q_ENVC",
           "D_ESD_USB_D", "C_REGN", "C_VBUS_GND", "U_EN_SW", "R_BAT_DET_1"]

# ★来源单全集 (★每条 source_iss 必须落在里面 ★)
# ★★ISS-283 · cont2: 增 ISS-283 (★本单落表带来的板侧同步项 §③ 三条的来源单★
#   ⇒ ★★只【增来源】不【放宽判据】: 来源不明 (不在这个全集里) 照样判红★★)
# ★★ISS-343 · 2026-11-23 01:0x (hw-lead): 增 ISS-290 (★E-1/E-2 两条板侧取舍的来源单★
#   ⇒ ★**只加成员·一个都不减** ★★ ★**且不放宽任何判据** ★★
SOURCES = {"ISS-239", "ISS-241", "ISS-244", "ISS-247", "ISS-266",
           "ISS-269", "ISS-271", "ISS-274", "ISS-276", "ISS-283",
           "ISS-290"}

# ★P5 现状探针 (★item_id → (命令, 抽取正则, 必须在该条 current_state 里出现的串 ★)
PROBES = {
    "B02_C_VBUS_GND": (
        ["bash", "state/pcbnew_py.sh", "state/check_pcb_nets.py"],
        r"(多余 \d+)"),
    "B17_DNP_43": (
        ["python3", "HW/check_netlist_contradiction_r3.py"],
        r"(零标记 \d+ 颗)"),
    "B25_UNCONNECTED": (
        ["python3", "state/check_pcb_drc.py"],
        r"(unconnected items = \d+)"),
    "B03_ULDO_S28_PAD3": (
        ["python3", "HW/check_pin_function_labels.py"],
        r"(\d+ 条缺陷)"),
    "B20_LAND_8ROWS": (
        ["python3", "-c",
         "import csv;rs=csv.DictReader(open('HW/netlist_v1_pins.csv'));"
         "refs={r['ref'] for r in rs};t={'D_CHG_LED','D_LED_G','D_LED_R','SW_BOOT',"
         "'SW_KEY_PWR','SW_KEY_VM','SW_KEY_VP','SW_RST'};"
         "print('落表残项 %d 行'%len(t&refs))"],
        r"(落表残项 \d+ 行)"),
}

_CACHE = {}


def sh(cmd, timeout=900):
    key = " ".join(cmd)
    if key in _CACHE:
        return _CACHE[key]
    try:
        r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        out = (r.stdout or b"").decode("utf-8", "replace")
        rc = r.returncode
    except Exception as e:                                   # pragma: no cover
        out, rc = "EXC: %s" % e, -1
    _CACHE[key] = (rc, out)
    return rc, out


def md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def load_items(checklist_path):
    """★从清单页里抽 JSON 块 ⇒ (items, 全文) ★"""
    txt = read_text(checklist_path)
    m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    if not m:
        return None, txt
    try:
        data = json.loads(m.group(1))
    except Exception:
        return None, txt
    items = data.get("items")
    return (items if isinstance(items, list) else None), txt


# ==============================================================================
# 六条判据
# ==============================================================================
def check_P1(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 清单页里找不到可解析的 JSON 块 (或 items 不是数组)"]
    for it in items:
        if not isinstance(it, dict):
            bad.append("item 不是 dict: %r" % (it,))
            ok = False
            continue
        miss = [f for f in FIELDS if f not in it]
        empty = [f for f in FIELDS if f in it and not str(it[f]).strip()]
        if miss or empty:
            ok = False
            bad.append("id=%s 缺字段=%s 空字段=%s" % (it.get("id", "?"), miss, empty))
    return ok, ["     条目 %d 条 · 9 字段齐全且非空: %s" % (len(items), "✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_P2(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    dist = {s: 0 for s in STEPS}
    for it in items:
        st = str(it.get("step", "")).strip()
        if st not in STEPS:
            ok = False
            bad.append("id=%s 的 step=%r 不在 S1~S13" % (it.get("id"), st))
        else:
            dist[st] += 1
    empty = [s for s in STEPS if dist[s] == 0]
    if empty:
        ok = False
        bad.append("这些步没人管 (零覆盖): %s" % empty)
    return ok, ["     步覆盖: %s" % " ".join("%s=%d" % (s, dist[s]) for s in STEPS)] + \
        ["     ❌ %s" % b for b in bad]


def check_P3(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    for it in items:
        crit = str(it.get("criterion", ""))
        m = re.search(r"(python3|bash|md5sum)\s+([^\s⇒;]+)", crit)
        if not m:
            ok = False
            bad.append("id=%s 的 criterion 里认不出命令: %r" % (it.get("id"), crit[:60]))
            continue
        for tok in re.findall(r"[\w./\-]+\.(?:py|sh)", crit):
            p = tok if os.path.isabs(tok) else os.path.join(PROJ, tok)
            if not os.path.exists(p):
                ok = False
                bad.append("id=%s 的 criterion 引用了不存在的文件: %s" % (it.get("id"), tok))
    return ok, ["     每条 criterion 的脚本文件都在盘上: %s" % ("✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


# ==============================================================================
# ★★ISS-343 · 2026-11-23 01:0x (hw-lead): P4 加严 —— 「作业包 §0.2 ③ 的板侧改动清单,
#   每一条都必须在清单页有对应 item」 ★★
# ==============================================================================
#   ★**病根**: 原 P4 只查「位号在不在清单里」+「来源单在不在全集里」⇒ ★**一条【不带新位号】的板改**
#     (★同一个 `J_DEBUG`/`J_UART` 的 land pitch 从 0.50 改成 1.27★) ⇒ **天生查不出** ⇒ ★**P4 绿 = 假绿** ★
#     (★真样本 = ISS-343 本单: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 32 条 item 里根本没有这一项★) ★
#   ★**方向纪律: 只许【加严】不许【放宽】** ★ ⇒ ① P1/P2/P3/P5/P6 一字未动 ② 26 个 MARKERS 一个没删
#     ③ SOURCES 只加成员 (ISS-290) ④ 本判据是【在 P4 里多加一块】, 不是换掉 P4 ★
#
#   ★**不许把 7 项写死成一个常量数组糊弄过去** (★那样下次作业包改了闸不会红★) ⇒
#     ★**7 项的【原文】从作业包现场解析** (★见 parse_wp02_board_changes★) ★
#     ★**覆盖判定 = 「绑定的清单 item 必须【真实存在】」+「绑定的 item 里必须能查到该子项的【覆盖令牌】」** ★
#       ⇒ ★**作业包改了 (加子项/改子项/删子项/把零板改项改成板改) ⇒ 本判据当场红** ★
WORKPACKET = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md")

# ★作业包 §0.2 ③ 的子项 → 清单页 item id 的对照 (★ordinal → (item ids, 额外覆盖令牌)★)
#   ★**这不是「把 7 项写死」**: 7 项的【原文 + 覆盖令牌】从作业包现场解析 (★见下★),
#     本表只回答「哪条子项该由清单页哪个 item 覆盖」⇒ ★**作业包一改就红** ★
WP02_BINDING = {
    "①": (["B11_Q_PG_LAND"], []),
    "②": (["B07_ESD_USB_D_3PIN", "B08_ESD_USB_D_NEAR"], []),
    "③": (["B33_PIN_LAND_1P27"], []),
    "④": (["B01_REF_SUFFIX"], ["_1", "位号"]),
    "⑤": (["B02_C_VBUS_GND"], []),
    "⑥": (["B07_ESD_USB_D_3PIN", "B08_ESD_USB_D_NEAR", "B09_ESD_USB_D_MINUS"], []),
}

# ★零板改项 (★【不进】板侧项全集★): 排除理由必须写清 (★出处 = pm.yaml 同一 key★)
WP02_ZERO_BOARD_CHANGE = {
    "⑦": "★E-2 = 零板改 (★pm.yaml key main_e1_e2_board_side_rulings_20261117 · decision 原文: E-2 = 零板改, 清死参数, 圆角不并进那一趟★) ⇒ ★它【不碰板 md5】⇒ 【不进】板侧项全集★",
}

WP02_ORDINALS = "①②③④⑤⑥⑦⑧⑨⑩"


def workpacket_path():
    """★作业包路径 (★每次调用都重读 env ⇒ --selftest 能在运行中换路径 ★)"""
    return os.environ.get("PREFLIGHT_WORKPACKET") or WORKPACKET


def parse_wp02_board_changes(wp_text):
    """★从作业包 §0.2 ③ 那一行【现场解析】出板侧改动清单的子项 ⇒ [(ordinal, 原文)] ★

    ★**只认「板侧改动清单」那一行里的 ①②③… 标记** ⇒ ★**作业包改了就解析出不一样的东西 ⇒ 闸会红** ★
    ★**绝不接受外部传入的子项列表** (★那才是「写死」★) ★
    """
    for line in wp_text.split("\n"):
        if "板侧改动清单" not in line or "①" not in line:
            continue
        cell = None
        for c in line.split("|"):
            if "①" in c:
                cell = c
                break
        if cell is None:
            continue
        parts = re.split(r"([%s])" % WP02_ORDINALS, cell)
        out, cur = [], None
        for p in parts:
            if len(p) == 1 and p in WP02_ORDINALS:
                cur = [p, []]
                out.append(cur)
            elif cur is not None:
                cur[1].append(p)
        res = [(k, "".join(v).strip()) for k, v in out]
        if res:
            return res
    return []


def wp02_tokens(text):
    """★从作业包子项原文里【自动】抽出「覆盖令牌」★ (★不许手工抄进代码★) ★

      · 设计符: `Q_PG` / `D_ESD_USB_D` / `C_VBUS_GND` 这类下划线名 + `R4` / `R9` 这类规则号 ★
      · 小数: `1.27` / `0.50` / `3.0` / `47.99` 这类目标值 (★整数不抽: `156→157` 是件数·不是覆盖口径★) ★
    """
    toks = set(re.findall(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+", text))
    toks |= set(re.findall(r"\b[A-Z]{1,3}\d{1,3}\b", text))
    toks |= set(re.findall(r"\d+\.\d+", text))
    return toks


def check_P4_workpack_coverage(items):
    """★P4 加严块 (★ISS-343★): 作业包 §0.2 ③ 的每一条板侧改动都必须有对应 item ★"""
    ok, bad, good = True, [], []
    by_id = {str(it.get("id")): it for it in (items or [])}
    wp_path = workpacket_path()
    if not os.path.exists(wp_path):
        return False, ["     ❌ 找不到作业包 %s ⇒ 新判据 fail-closed (★不许「查不到就算过」★)" % wp_path]
    parsed = parse_wp02_board_changes(read_text(wp_path))
    if not parsed:
        return False, ["     ❌ 作业包 %s 的「板侧改动清单」那一行解析不出来 ⇒ 新判据 fail-closed" % wp_path]
    expect = set(WP02_BINDING) | set(WP02_ZERO_BOARD_CHANGE)
    got = set(o for o, _ in parsed)
    if got != expect:
        ok = False
        bad.append("❌ 作业包 §0.2 ③ 解析出的子项集合 = %s, 而判据绑定表认识的是 %s ⇒ "
                   "★作业包改了 / 绑定表过期 (fail-closed)★" % (sorted(got), sorted(expect)))
    for o, text in parsed:
        if "零板改" in text:
            if o not in WP02_ZERO_BOARD_CHANGE:
                ok = False
                bad.append("❌ 作业包 §0.2 ③ 的 %s 写了「零板改」但判据没登记它的排除理由 ⇒ 漏判" % o)
            else:
                good.append("     ✔ 作业包 §0.2 ③ 的 %s = 零板改项 ⇒ 不进板侧项全集 (%s)"
                            % (o, WP02_ZERO_BOARD_CHANGE[o][:48]))
            continue
        if o not in WP02_BINDING:
            ok = False
            bad.append("❌ 作业包 §0.2 ③ 的 %s = 「%s」是板改项但判据绑定表里没有它 ⇒ 漏判 (fail-closed)"
                       % (o, text[:36]))
            continue
        ids, extra = WP02_BINDING[o]
        missing = [i for i in ids if i not in by_id]
        if missing:
            ok = False
            bad.append("❌ 作业包 §0.2 ③ 的 %s = 「%s」缺对应 item: %s ⇒ ★那一趟会漏做这一项 (★删清单页里的这条就红★)"
                       % (o, text[:36], missing))
            continue
        blob = " ".join(json.dumps(by_id[i], ensure_ascii=False) for i in ids)
        toks = sorted(wp02_tokens(text) | set(extra))
        miss = [t for t in toks if t not in blob]
        if miss:
            ok = False
            bad.append("❌ 作业包 §0.2 ③ 的 %s = 「%s」绑定的 item %s 里找不到覆盖令牌 %s ⇒ 覆盖对不上"
                       % (o, text[:36], ids, miss))
            continue
        good.append("     ✔ 作业包 §0.2 ③ 的 %s ⇒ 命中 %s (覆盖令牌 %d 个全在)"
                    % (o, ids, len(toks)))
    return ok, good + bad


def check_P4(items, txt):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    blob = json.dumps(items, ensure_ascii=False)
    for mk in MARKERS:
        if mk not in blob:
            ok = False
            bad.append("★板侧标记 %s 在清单里找不到 ⇒ 漏项 (★它只存在于来源交卷单里 ★)" % mk)
    for it in items:
        s = str(it.get("source_iss", "")).strip()
        if s not in SOURCES:
            ok = False
            bad.append("id=%s 的 source_iss=%r 不在来源单全集里 ⇒ 来源不明" % (it.get("id"), s))
    # ★★ISS-343 · 加严块 (★只加·不减·不改前面任何一条的判据方向★★)
    ok2, lines2 = check_P4_workpack_coverage(items)
    ok = ok and ok2
    return ok, ["     覆盖度: %d 个标记全部在清单里: %s" % (len(MARKERS), "✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad] + lines2


def check_P5(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    by_id = {str(it.get("id")): it for it in items}
    for item_id, (cmd, rx) in PROBES.items():
        it = by_id.get(item_id)
        if it is None:
            ok = False
            bad.append("清单里没有探针绑定的条目 %s" % item_id)
            continue
        rc, out = sh(cmd)
        m = re.search(rx, out)
        if not m:
            ok = False
            bad.append("%s 的探针没抽到值 (rc=%d): %s" % (item_id, rc, rx))
            continue
        val = m.group(1)
        state = str(it.get("current_state", ""))
        if val not in state:
            ok = False
            bad.append("%s: 盘面实测 = %r, 但清单 current_state 里没有这个值 ⇒ 清单过期"
                       % (item_id, val))
    return ok, ["     %d 个现状探针: 清单里的现状值 == 盘面实测: %s"
                % (len(PROBES), "✔" if ok else "❌")] + ["     ❌ %s" % b for b in bad]


def check_P6():
    ok, bad, good = True, [], []
    pmap = protected_map()
    # ★★ISS-297 · 2026-11-17 20:3x (hw-lead): 板 / `.kicad_pro` 两件改走【落表台账链头 + 合法改板通道】★★
    #   ★判据方向一字未变 (★盘上 ≠ 判决源 ⇒ 红★); ★变的只是【判决源】: 写死常量 → 落表台账链头 ★
    #   ★`reboard: null` (还没发生过合法改板) ⇒ ★仍按纯 md5 硬保护判 (盘上 ≠ 基线 ⇒ 红)★ ★
    #   ★fail-closed 三条一条不许动 (★链头不唯一 / 链断 / 链头无单号 ⇒ 仍红★) ★
    for name, rel in (("板", board_reboard.PCB_REL), (".kicad_pro", board_reboard.PRO_REL)):
        path, base = pmap[name][0], pmap[name][1]
        if not os.path.exists(path):
            ok = False
            bad.append("%s 不存在: %s" % (name, path))
            continue
        res = board_reboard.check_file(PROJ, rel, path, base, md5fn=md5)
        if res["ok"]:
            good.append("     ✔ %s" % res["msg"])
        else:
            ok = False
            for e in res["errs"]:
                bad.append("%s: %s" % (name, e))
    for name, (path, base, rel) in pmap.items():
        if name in ("板", ".kicad_pro"):
            continue
        if not os.path.exists(path):
            ok = False
            bad.append("%s 不存在: %s" % (name, path))
            continue
        cur = md5(path)
        if base is None:
            # ★★ISS-283 · ⑩-b: 网表/脚表/BOM 走「落表台账为准」的口径 (★不是把基线数字改成新值★) ★
            g, msg = landing_md5.check_registered(PROJ, rel, path, md5)
            if g:
                good.append("     ✔ %s" % msg)
            else:
                ok = False
                bad.append("%s: %s" % (name, msg))
            continue
        if cur != base:
            ok = False
            bad.append("%s md5 %s ≠ 基线 %s" % (name, cur, base))
        else:
            good.append("     ✔ %s md5 未变 (%s) (★基线写死·不归落表链管★)" % (name, cur))
    return ok, ["     受保护 5 件 md5 逐字节不变: %s" % ("✔" if ok else "❌")] + good + \
        ["     ❌ %s" % b for b in bad]


CHECKS = {
    "P1": lambda items, txt: check_P1(items),
    "P2": lambda items, txt: check_P2(items),
    "P3": lambda items, txt: check_P3(items),
    "P4": lambda items, txt: check_P4(items, txt),
    "P5": lambda items, txt: check_P5(items),
    "P6": lambda items, txt: check_P6(),
}


def evaluate(checklist_path, only=None):
    items, txt = load_items(checklist_path)
    lines, ok = [], True
    for cid, fn in CHECKS.items():
        if only and cid != only:
            continue
        r_ok, r_lines = fn(items, txt)
        lines.append("  %s  %s" % ("OK " if r_ok else "FAIL", cid))
        lines.extend(r_lines)
        ok = ok and r_ok
    return ok, lines


# ==============================================================================
# --selftest
# ==============================================================================
def write_variant(src_path, dst_path, mutate):
    """★把清单页的 JSON 块换掉, 写一份副本 (★用来做反向用例 ★)"""
    txt = read_text(src_path)
    m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    data = json.loads(m.group(1))
    mutate(data)
    new_block = "```json\n%s\n```" % json.dumps(data, ensure_ascii=False, indent=2)
    txt2 = txt[:m.start()] + new_block + txt[m.end():]
    open(dst_path, "w", encoding="utf-8").write(txt2)
    return dst_path


def run_selftest(checklist_path):
    tmpd = tempfile.mkdtemp(prefix="iss277_selftest_")
    cases = []
    try:
        # ① 清单里删掉一条 (含标记 D_ESD_CAM) ⇒ P4 红
        p = os.path.join(tmpd, "v1.md")
        write_variant(checklist_path, p, lambda d: d["items"].remove(
            next(i for i in d["items"] if i["id"] == "B13_ESD_CAM_PAD")))
        ok, _ = evaluate(p, only="P4")
        cases.append(("① 删掉含 D_ESD_CAM 的那一条 ⇒ P4 红", ok is False))

        # ② 改一条现状值 ⇒ P5 红
        p = os.path.join(tmpd, "v2.md")
        def mut2(d):
            it = next(i for i in d["items"] if i["id"] == "B25_UNCONNECTED")
            it["current_state"] = it["current_state"].replace("unconnected items = 45",
                                                             "unconnected items = 40")
        write_variant(checklist_path, p, mut2)
        ok, _ = evaluate(p, only="P5")
        cases.append(("② 把 unconnected 现状值改成 40 ⇒ P5 红", ok is False))

        # ③ 抽掉一个字段 ⇒ P1 红
        p = os.path.join(tmpd, "v3.md")
        def mut3(d):
            it = next(i for i in d["items"] if i["id"] == "B01_REF_SUFFIX")
            it.pop("step")
        write_variant(checklist_path, p, mut3)
        ok, _ = evaluate(p, only="P1")
        cases.append(("③ 抽掉一条的 step 字段 ⇒ P1 红", ok is False))

        # ④ 归属步改成 S99 ⇒ P2 红
        p = os.path.join(tmpd, "v4.md")
        def mut4(d):
            next(i for i in d["items"] if i["id"] == "B02_C_VBUS_GND")["step"] = "S99"
        write_variant(checklist_path, p, mut4)
        ok, _ = evaluate(p, only="P2")
        cases.append(("④ 把归属步改成 S99 ⇒ P2 红", ok is False))

        # ⑤ 判据命令写成不存在的 ⇒ P3 红
        p = os.path.join(tmpd, "v5.md")
        def mut5(d):
            next(i for i in d["items"] if i["id"] == "B01_REF_SUFFIX")["criterion"] = \
                "python3 HW/check_this_does_not_exist_zzz.py ⇒ rc=0"
        write_variant(checklist_path, p, mut5)
        ok, _ = evaluate(p, only="P3")
        cases.append(("⑤ 判据命令指向不存在的脚本 ⇒ P3 红", ok is False))

        # ⑥ 改受保护 5 件之一 (板) ⇒ P6 红
        pcb_src = protected_map()["板"][0]
        pcb_bad = os.path.join(tmpd, "board_bad.kicad_pcb")
        t = read_text(pcb_src)
        open(pcb_bad, "w", encoding="utf-8").write(t + "\n; ★selftest 注入的一行 ★\n")
        old = os.environ.get("PREFLIGHT_PCB")
        os.environ["PREFLIGHT_PCB"] = pcb_bad
        ok, _ = evaluate(checklist_path, only="P6")
        if old is None:
            os.environ.pop("PREFLIGHT_PCB", None)
        else:
            os.environ["PREFLIGHT_PCB"] = old
        cases.append(("⑥ 板文件被改一个字节 ⇒ P6 红", ok is False))

        # ⑥b ★★ISS-283 · ⑩-b: 网表被改一个字节 ⇒ P6 红 (★新口径: 台账登记 vs 盘上·不是 vs 写死基线★) ★
        net_src = protected_map()["网表"][0]
        net_bad = os.path.join(tmpd, "netlist_bad.csv")
        t = read_text(net_src)
        open(net_bad, "w", encoding="utf-8").write(t + "\n; ★selftest 注入的一行 ★\n")
        old = os.environ.get("PREFLIGHT_NETLIST")
        os.environ["PREFLIGHT_NETLIST"] = net_bad
        ok, _ = evaluate(checklist_path, only="P6")
        if old is None:
            os.environ.pop("PREFLIGHT_NETLIST", None)
        else:
            os.environ["PREFLIGHT_NETLIST"] = old
        cases.append(("⑥b 网表被改一个字节 ⇒ P6 红 (★台账登记 ≠ 盘上★)", ok is False))

        # ⑥c ★★ISS-283 · ⑩-b: 落表台账里【查不到该文件的登记】⇒ P6 红 (★fail-closed·不许猜★) ★
        #   ★★cont2 修: 旧写法的过滤条件是 `A not in l or B not in l` ⇒ 【逻辑取反】⇒
        #      台账里没有任何一行同时含 A 和 B ⇒ 【一行都没删掉】⇒ 台账原样 ⇒ P6 仍绿 ⇒ 用例假失败★
        #      ⇒ 现在改成【真的把网表的登记行删掉】(★台账里所有链都删 ⇒ 「查不到」无歧义★) ★
        led_src = os.path.join(PROJ, "HW", "SCHEMATIC_LANDING_V1_LANDED.md")
        led_bad = os.path.join(tmpd, "ledger_bad.md")
        lt = read_text(led_src)
        lt_lines = lt.split("\n")
        lt2_lines = [l for l in lt_lines if "`HW/netlist_v1.csv`**" not in l]
        n_removed = len(lt_lines) - len(lt2_lines)
        if n_removed < 1:
            print("  ⚠ ⑥c ★★突变没咬到台账里网表的登记行 ⇒ 用例自身没写完★")
        open(led_bad, "w", encoding="utf-8").write("\n".join(lt2_lines))
        oldl = os.environ.get("LANDING_LEDGER")
        os.environ["LANDING_LEDGER"] = led_bad
        ok, _ = evaluate(checklist_path, only="P6")
        if oldl is None:
            os.environ.pop("LANDING_LEDGER", None)
        else:
            os.environ["LANDING_LEDGER"] = oldl
        cases.append(("⑥c 落表台账里【所有链】都查不到网表的登记 ⇒ P6 红 (★fail-closed★)", ok is False,
                      "★自证改动★: 台账删掉 %d 行网表登记 (md5 %s → %s)"
                      % (n_removed, md5(led_src)[:8], md5(led_bad)[:8])))

        # ⑥d (★cont2 增★): 落表台账里【最新一条链】的 BOM 登记【新 md5 缺了】⇒ 四项不齐 ⇒ P6 红
        #   ★★反向用例只许增不许减★ ⇒ 这条把 C6 那边的「四项不齐」也搬到 P6 侧测一遍 ★
        led_bad2 = os.path.join(tmpd, "ledger_bad2.md")
        ll = read_text(led_src).split("\n")
        heads = [i for i, l in enumerate(ll) if l.startswith("## ")]
        n_fixed = 0
        if heads:
            s0 = heads[-1]
            secs = [i for i in range(s0, len(ll))
                    if ll[i].startswith("### ") and "16.2" in ll[i] and "新旧 md5" in ll[i]]
            if secs:
                s = secs[-1]
                for i in range(s + 1, len(ll)):
                    if ll[i].startswith("### ") or ll[i].startswith("## "):
                        break
                    if ll[i].startswith("|") and "`HW/BOM_v1.csv`" in ll[i]:
                        parts = ll[i].split("|")
                        if len(parts) >= 4:
                            parts[3] = " `★(缺)★` "
                            ll[i] = "|".join(parts)
                            n_fixed += 1
                        break
        open(led_bad2, "w", encoding="utf-8").write("\n".join(ll))
        oldl = os.environ.get("LANDING_LEDGER")
        os.environ["LANDING_LEDGER"] = led_bad2
        ok, _ = evaluate(checklist_path, only="P6")
        if oldl is None:
            os.environ.pop("LANDING_LEDGER", None)
        else:
            os.environ["LANDING_LEDGER"] = oldl
        cases.append(("⑥d 落表台账【最新一条链】里 BOM 的【新 md5】缺了 ⇒ P6 红 (★四项不齐★)", ok is False,
                      "★自证改动★: 台账改 %d 行 BOM 登记 (md5 %s → %s)"
                      % (n_fixed, md5(led_src)[:8], md5(led_bad2)[:8])))

        # ⑦ 把 source_iss 改成来源不明的 ⇒ P4 红 (反向: 不许有来源不明的项)
        p = os.path.join(tmpd, "v7.md")
        def mut7(d):
            next(i for i in d["items"] if i["id"] == "B05_U_EN_SW_VALUE")["source_iss"] = "ISS-999"
        write_variant(checklist_path, p, mut7)
        ok, _ = evaluate(p, only="P4")
        cases.append(("⑦ source_iss 改成来源不明 (ISS-999) ⇒ P4 红", ok is False))

        # ★★ISS-343 · ⑧ 删掉新加的那条 (排针 land 1.27) ⇒ P4 红且【点名 ③ 排针 land 缺对应 item】★★
        #   ★这一条 = 本单的病根样本: 一条【不带新位号】的板改 (同一个 J_DEBUG/J_UART 的 land pitch 改)
        #     ⇒ 老 P4 的 26 个标记判它【抓不到】(J_DEBUG/J_UART 这两个标记在 B15 里也有) ⇒ 只能靠新判据抓 ★
        p = os.path.join(tmpd, "v8.md")
        write_variant(checklist_path, p, lambda d: d["items"].remove(
            next(i for i in d["items"] if i["id"] == "B33_PIN_LAND_1P27")))
        ok, lines = evaluate(p, only="P4")
        named = [l for l in lines if "缺对应 item" in l and "③" in l]
        cases.append(("⑧ 删掉新加的 B33_PIN_LAND_1P27 ⇒ P4 红且点名「③ 排针 land 缺对应 item」",
                      ok is False and len(named) >= 1,
                      "★自证改动★: 副本清单页 md5 %s → %s (★真件零动★) · 判红行: %s"
                      % (md5(checklist_path)[:8], md5(p)[:8],
                         named[0].strip() if named else "★没抓到点名行★")))

        # ★★ISS-343 · ⑨ 把 SOURCES 里的 ISS-290 去掉 ⇒ P4 红 (★证明「来源单那一路」也没白加★) ★★
        #   ★沙盒纪律: ★真件闸脚本一个字节都不许动★ ⇒ 改的是【副本】(★副本里还把 HERE/PROJ 指向真盘★) ★
        gate_copy = os.path.join(tmpd, "gate_without_iss290.py")
        gsrc = read_text(os.path.join(PROJ, "HW", "check_onepass_preflight_coverage.py"))
        # ★只删 SOURCES 集合末尾那一个成员 (★不许误伤本文件里别的 ISS-290 字样★)
        pat290 = re.compile(r'\n[ \t]*"ISS-290"([ \t]*\})')
        n_iss290 = len(pat290.findall(gsrc))
        gsrc2 = pat290.sub(r'\1', gsrc, count=1)
        gsrc2 = gsrc2.replace("HERE = os.path.dirname(os.path.abspath(__file__))",
                              "HERE = %r" % os.path.join(PROJ, "HW"))
        gsrc2 = gsrc2.replace("PROJ = os.path.dirname(HERE)", "PROJ = %r" % PROJ)
        open(gate_copy, "w", encoding="utf-8").write(gsrc2)
        rr = subprocess.run([sys.executable, gate_copy, "--checklist", checklist_path],
                            cwd=PROJ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
        gout = (rr.stdout or b"").decode("utf-8", "replace")
        src_line = next((l.strip() for l in gout.split("\n") if "来源不明" in l), "")
        cases.append(("⑨ 把 SOURCES 里的 ISS-290 去掉 ⇒ P4 红 (★证明来源单那一路没白加★)",
                      (rr.returncode != 0) and ("FAIL  P4" in gout) and ("来源不明" in gout) and n_iss290 == 1,
                      "★自证改动★: 副本闸脚本里从 SOURCES 集合删掉 %d 处成员 (★真件零动★) · rc=%d · %s"
                      % (n_iss290, rr.returncode, src_line or "★没抓到来源不明行★")))

        # ★★ISS-343 · ⑩ 作业包 §0.2 ③ 的子项被改 (副本) ⇒ P4 红 (★证明 7 项是【现场解析】不是写死★) ★★
        wp_bad = os.path.join(tmpd, "wp_drift.md")
        wt = read_text(workpacket_path())
        wt2 = wt.replace("`J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm",
                          "`J_DEBUG`/`J_UART` 排针 land 0.50→2.54mm")
        n_drift = 0 if wt2 == wt else 1
        open(wp_bad, "w", encoding="utf-8").write(wt2)
        oldwp = os.environ.get("PREFLIGHT_WORKPACKET")
        os.environ["PREFLIGHT_WORKPACKET"] = wp_bad
        ok, lines = evaluate(checklist_path, only="P4")
        drift_line = next((l.strip() for l in lines if "找不到覆盖令牌" in l), "")
        if oldwp is None:
            os.environ.pop("PREFLIGHT_WORKPACKET", None)
        else:
            os.environ["PREFLIGHT_WORKPACKET"] = oldwp
        cases.append(("⑩ 作业包 §0.2 ③ 的「排针 land 1.27」被改成 2.54 (副本) ⇒ P4 红 (★证明 7 项是现场解析★)",
                      ok is False and n_drift == 1,
                      "★自证改动★: 作业包副本 md5 %s → %s (★真件零动★) · %s"
                      % (md5(workpacket_path())[:8], md5(wp_bad)[:8],
                         drift_line or "★没抓到覆盖令牌行★")))

        # ★基线: 真盘必须全绿 (否则上面那些红没意义)
        ok0, _ = evaluate(checklist_path)
        cases.append(("★基线: 真盘 P1~P6 全绿", ok0 is True))

        # ── ★★ISS-297 · ⑯ 「合法改板」通道的反向用例 (★沙盒跑·真盘零写·判决源 = 落表台账链头★) ──
        #   ★机制: `HW/board_reboard.py` 的 CASES (★照 ISS-284 已跑通的口径·不许自创★) ★
        #   ★每条都【真跑本闸】(★受保护 5 件指向沙盒副本★) ⇒ 判据变红/变绿都必须是本闸自己的结论 ★
        ch_cases = []

        def ch_prepare(sb):
            """★把本闸要读的东西铺进沙盒 (★板/`.kicad_pro`/锚点/落表台账 board_reboard 已拷★) ★"""
            for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
                src = os.path.join(PROJ, rel)
                d = os.path.join(sb, rel)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(src, d)

        def ch_judge(sb):
            old = {k: os.environ.get(k) for k in
                   ("PREFLIGHT_PCB", "PREFLIGHT_PRO", "PREFLIGHT_NETLIST",
                    "PREFLIGHT_PINS", "PREFLIGHT_BOM")}
            try:
                os.environ["PREFLIGHT_PCB"] = os.path.join(sb, board_reboard.PCB_REL)
                os.environ["PREFLIGHT_PRO"] = os.path.join(sb, board_reboard.PRO_REL)
                os.environ["PREFLIGHT_NETLIST"] = os.path.join(sb, "HW/netlist_v1.csv")
                os.environ["PREFLIGHT_PINS"] = os.path.join(sb, "HW/netlist_v1_pins.csv")
                os.environ["PREFLIGHT_BOM"] = os.path.join(sb, "HW/BOM_v1.csv")
                ok, lines = evaluate(checklist_path)
                return ok, "★本闸 P1~P6 绿? %s★ · %s" % ("是" if ok else "否", " | ".join(lines))
            finally:
                for k, v in old.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v

        for _name, _exp, _got, _note in board_reboard.run_cases(
                PROJ, os.path.join(tmpd, "iss297_channel"), ch_judge, prepare=ch_prepare):
            ch_cases.append(("★ISS-297★ " + _name, _exp == _got, _note))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("=" * 78)
    print("  ISS-277 · 反向用例 (★每条都自证「真的改到了目标」 ★)")
    print("=" * 78)
    bad = 0
    for item in cases:
        name, caught = item[0], item[1]
        proof = item[2] if len(item) > 2 else None
        mark = "✔" if caught else "✘"
        if not caught:
            bad += 1
        print("  %s  %s" % (mark, name))
        if proof:
            print("       %s" % proof)
    print("-" * 78)
    print("  反向用例 %d/%d 通过" % (len(cases) - bad, len(cases)))
    if bad:
        print("  ❌ 有反向用例没抓到 ⇒ 闸不是判据 (或用例本身写错了)")
        return 1
    print("  ✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没 ★)")

    # ★★ISS-297 · ⑯ 「合法改板」通道反向用例 (★10 条·判决源 = 落表台账链头 + 四项原子映射★) ★★
    print("=" * 78)
    print("  ★★ISS-297 · ⑯ 「合法改板」通道反向用例 (%d 条·判决源 = 落表台账链头 + 四项原子映射★)" % len(ch_cases))
    print("=" * 78)
    bad_ch = 0
    for name, passed, info in ch_cases:
        if not passed:
            bad_ch += 1
        print("  %s %s" % ("✔" if passed else "✘", name))
        print("       %s" % info)
    print("-" * 78)
    print("  ⇒ 通道用例: %d/%d 通过 · 合计 %d/%d"
          % (len(ch_cases) - bad_ch, len(ch_cases),
             (len(cases) - bad) + (len(ch_cases) - bad_ch), len(cases) + len(ch_cases)))
    if bad_ch:
        print("  ❌ 有通道反向用例没抓到 ⇒ 通道判据是摆设 ⇒ 闸不算数")
        return 1
    print("  ✅ 通道反向用例全抓到 ⇒ 「合法改板」当天不会再集体假红, 且没背书照样红★")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--checklist", default=CHECKLIST)
    args = ap.parse_args()

    if not os.path.exists(args.checklist):
        print("❌ 用法错: 找不到清单页 %s" % args.checklist)
        return 2

    if args.selftest:
        return run_selftest(args.checklist)

    print("=" * 78)
    print("  ISS-277 · 板侧漏项覆盖度闸 (★P1 清单 / P2 归属步 / P3 判据真命令 / P4 覆盖度 / P5 现状 / P6 受保护 ★)")
    print("=" * 78)
    ok, lines = evaluate(args.checklist)
    for l in lines:
        print(l)
    print("-" * 78)
    if ok:
        print("  ✅ rc=0: ★★板侧项全集与作业包对齐, 现状值与盘面一致 ★★")
        return 0
    print("  ❌ rc=1: ★★有板侧项漏在清单外, 或清单现状已过期 ⇒ 那一趟会漏做 ★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
