#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_fts_land_drill_same_batch.py  ·  ISS-391 闸 D1~D7
「落 FTS 时排针钻孔 0.65 → 0.71」这条板侧改动, 有没有真的进到
「板只改一次」那一趟的【作业包 §0.2 ③】+【预检清单 B33_PIN_LAND_1P27】里。

用法:
    python3 HW/check_fts_land_drill_same_batch.py             # 正向跑
    python3 HW/check_fts_land_drill_same_batch.py --selftest  # 自测 (反向用例, 末行 ALL TESTS PASS)

★**本闸现在【必然红】(rc=1) —— 那是本单的发现, 不是本闸故障** ★
  ⇒ 红的那几条 (D1 / D2 / D3) 就是真相页 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md`
    §4 里「要 main 落什么」的登记项 ⇒ ★**main 落完 §4 #1/#2/#3 ⇒ 同一条命令即转绿**
    (★selftest 的「正向对照 (沙盒已补登记)」那一格就是转绿后的样子★)

★纪律:
  · fail-closed —— 任一条不满足 ⇒ 该条红 ⇒ 整体 rc=1
  · 每条闸至少一条反向用例 (--selftest 里把入参改坏 ⇒ 必须【只有】目标那条红)
  · ★零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 只读盘 + 只写自己的沙盒 tmp/iss391_sbx/
  · ★本闸【不许挂进 state/gate_check.py】(挂链是 main 的地界) ⇒ 只交脚本 + 路径 + 建议
  · ★本闸【不许写死任何一个数】—— 目标值/通用件值/基线全部从真相页机器块读 ⇒ 改页即红

★★D1 / D2 必须【现场解析真文件】 (★不是环境变量副本★) ★★
  ⇒ ★**这样「真实盘上的清单缺了」这件事才测得出来** ★
  ⇒ 前向跑 (无 --selftest) 时, 本闸读的是【项目盘上的真文件】(路径从本闸自己的位置推,
    不看任何环境变量) ⇒ ★**真实清单里没有改孔这一条 ⇒ 本闸当场红** ★
  ⇒ --selftest 只在【沙盒副本】上改; 跑完【必须复验真文件 md5 未变】(自测里带这一格)

闸定义 (口径照抄真相页 §2 / §3 / §4 / §5 / §6):
  D1  ★作业包 §0.2 ③ 的「③」那一项原文里必须查到「改孔」这一条板侧动作★
      (★现场解析作业包原文, 不接受外部传入的子项列表★)
      判据 = 【钻孔字样 (钻孔/孔径/drill)】+【目标值 0.71】+【pitch 那一腿的 1.27 仍在】
      ⇒ 只做其一时 / 只有 pitch 时 / 只有 drill 时, 都判红
  D2  ★预检清单 B33_PIN_LAND_1P27 的【描述列】里必须查到「改孔」这一条★
      (★JSON 项 + 表格行两处都要★ ⇒ 少一处 = 那一趟照样漏)
  D3  ★B33_PIN_LAND_1P27 的【验收手段】列里必须有一条【读钻孔直径】的验收命令★
      ⇒ 没有验收手段 = 改没改成没人知道 ⇒ 判红
  D4  ★两端数字必须自洽★: drill_target == drill_official 且 drill_target != drill_generic
      且 drill_generic == 本机库件实测值 (★现场解析 .kicad_mod★)
      ⇒ 另: 真相页机器块前置 (在盘 / 可解析 / 必需键齐全) + 官方 PDF 文字层复核
  D5  ★影响面★: 机器块必须列出【MECH 侧不受影响的数名清单】(从真相页读, 不许写死)
      ⇒ 空 ⇒ 判红 (★「结构件不必返工」这条结论没有落点 = 没算过★)
  D6  ★零扰动★: 板三项指纹 + 零落表 (网表/脚表/BOM) + 零挂链 + 已签收件 md5 同基线
      (★基线全部从真相页机器块读, 不写死★)
  D7  ★本闸自己环境无关★: 两个不同深度 (cwd) 下读数必须一致 ⇒ 路径必须从本闸自己推

★沙盒纪律 (★本机已踩过的坑★):
  沙盒一律落【项目盘】tmp/iss391_sbx/ (路径从本闸自己的 ROOT 推),
  不写系统 /tmp ⇒ 不依赖系统 /tmp 的深度 ⇒ D7 有意义。
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

# ---------------------------------------------------------------------------
# 路径 (★全部从本闸自己的位置推 ⇒ 与 cwd 无关★)
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SANDBOX = os.path.join(PROJ, "tmp", "iss391_sbx")

REAL_PATHS = {
    "page": os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md"),
    "workpacket": os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md"),
    "preflight": os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md"),
    "coverage_gate": os.path.join(PROJ, "HW", "check_onepass_preflight_coverage.py"),
    "iss387_gate": os.path.join(PROJ, "HW", "check_fts_single_row_land_truth.py"),
    "iss387_truth": os.path.join(PROJ, "HW", "PCB",
                                 "BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md"),
    "board": os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"),
    "netlist": os.path.join(PROJ, "HW", "netlist_v1.csv"),
    "pins": os.path.join(PROJ, "HW", "netlist_v1_pins.csv"),
    "bom": os.path.join(PROJ, "HW", "BOM_v1.csv"),
    "gate_check": os.path.join(PROJ, "state", "gate_check.py"),
    "lib_dir": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/"
               "Connector_PinHeader_1.27mm.pretty",
}

GATE_NAME = "check_fts_land_drill_same_batch"
ORDINALS = "①②③④⑤⑥⑦⑧⑨⑩"
ITEM_ID = "B33_PIN_LAND_1P27"
ORDINAL_OF_ITEM = "③"

LIB_FILES = {
    "J_DEBUG": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
    "J_UART": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
}

CN_TZ = datetime.timezone(datetime.timedelta(hours=8))


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def mtime_iso(path):
    return datetime.datetime.fromtimestamp(
        os.stat(path).st_mtime, CN_TZ).strftime("%Y-%m-%d %H:%M:%S.%f")


def num_eq(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def has_drill(text):
    """★文本里有没有「钻孔」这件事的字样 (中文 + 英文都要认)★"""
    if not text:
        return False
    if ("钻孔" in text) or ("孔径" in text):
        return True
    return bool(re.search(r"drill", text, re.I))


def sec_body(page, start_marker, end_marker=None):
    """从 start_marker 到下一个 '## ' (或 end_marker) 之间的正文。"""
    i = page.find(start_marker)
    if i < 0:
        return ""
    rest = page[i + len(start_marker):]
    j = rest.find("\n## ")
    k = rest.find(end_marker) if end_marker else -1
    ends = [x for x in (j, k) if x >= 0]
    return rest[:min(ends)] if ends else rest


# ---------------------------------------------------------------------------
# 现场解析: 作业包 §0.2 ③ 的子项 (★不许写死成一个常量数组★)
# ---------------------------------------------------------------------------
def parse_wp02_board_changes(wp_text):
    """★从作业包 §0.2 ③ 那一行【现场解析】出板侧改动清单的子项 ⇒ {序: 原文} ★"""
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
        parts = re.split(r"([%s])" % ORDINALS, cell)
        out, cur = {}, None
        for p in parts:
            if len(p) == 1 and p in ORDINALS:
                cur = p
                out[cur] = []
            elif cur is not None:
                out[cur].append(p)
        res = {k: "".join(v).strip() for k, v in out.items()}
        if res:
            return res
    return {}


# ---------------------------------------------------------------------------
# 现场解析: 预检清单的 JSON 项 + 表格行
# ---------------------------------------------------------------------------
def parse_preflight_json(text):
    """★预检清单页 §7 的 JSON 块 ⇒ items 列表★"""
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except Exception:  # noqa: BLE001
        return None
    items = data.get("items")
    return items if isinstance(items, list) else None


def parse_preflight_md_row(text, item_id):
    """★预检清单页 §2 表格里 item_id 那一行 ⇒ 7 个单元格★"""
    for line in text.split("\n"):
        s = line.strip()
        if not s.startswith("|"):
            continue
        if item_id not in s:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) >= 7:
            return cells
    return None


def _json_block_span(text):
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    return m


def replace_preflight_json(text, items):
    """★把 JSON 块替换成新的 items (★只用于自测造反向用例★)★"""
    m = _json_block_span(text)
    if not m:
        raise AssertionError("自测前提不成立: 预检清单页里没有 json 块")
    data = json.loads(m.group(1))
    data["items"] = items
    new = "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"
    return text[:m.start(1)] + new + text[m.end(1):]


# ---------------------------------------------------------------------------
# 现场解析: 通用库件的钻孔
# ---------------------------------------------------------------------------
def measure_lib_drill(lib_dir):
    """★现场解析两个 .kicad_mod 的 (drill X) ⇒ {ref: [值,...]} (★不许写死 0.65★)★"""
    out = {}
    for ref, fn in LIB_FILES.items():
        p = os.path.join(lib_dir, fn)
        if not os.path.exists(p):
            out[ref] = None
            continue
        vals = sorted(set(re.findall(r"\(drill\s+([0-9.]+)\)", read_text(p))))
        out[ref] = vals
    return out


# ---------------------------------------------------------------------------
# 机器块
# ---------------------------------------------------------------------------
REQUIRED_MB_KEYS = (
    "schema", "issue", "agent", "updated", "truth_doc",
    "board_write", "table_write", "existing_gate_change", "existing_page_change",
    "landing_part_decision", "same_batch_granularity_decision",
    "bom_landing_decision", "registration_owner_decision", "pad_diameter_decision",
    "drill_official", "drill_generic", "drill_target",
    "drill_sources", "board_current_land", "affected_refs",
    "drill_action", "same_batch_granularity", "same_batch_granularity_allowed_values",
    "registration_gaps", "mech_unaffected_numbers", "mech_unaffected_reason",
    "acceptance_commands", "zero_perturbation_baseline",
    "decisions_not_made_here", "open_items",
)


def parse_machine_block(page_text):
    """★从真相页里抽出 json 机器块 ⇒ (dict, err)★"""
    blocks = re.findall(r"```json\s*\n(.*?)\n```", page_text, re.S)
    if not blocks:
        return None, "真相页里找不到 ```json 机器块"
    for b in blocks:
        try:
            d = json.loads(b)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, dict) and str(d.get("schema", "")).startswith(
                "hw.fts.land_drill_change"):
            return d, ""
    return None, "真相页里找不到 schema = hw.fts.land_drill_change* 的机器块"


# ---------------------------------------------------------------------------
# 入参采集
# ---------------------------------------------------------------------------
def count_chain_hits(gate_check_path):
    """state/gate_check.py 里命中本闸名的行数 (零挂链 = 0)。"""
    if not os.path.exists(gate_check_path):
        return -1
    n = 0
    with open(gate_check_path, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if GATE_NAME in ln:
                n += 1
    return n


def collect(paths=None, facts=None):
    """★把闸要用的全部入参收成 dict (★自测时逐项替换即可制造反向用例★)★"""
    p = dict(REAL_PATHS)
    if paths:
        p.update(paths)
    ctx = {"paths": p}
    ctx["page_text"] = read_text(p["page"]) if os.path.exists(p["page"]) else ""
    ctx["page_exists"] = bool(ctx["page_text"].strip())
    ctx["wp_text"] = read_text(p["workpacket"]) if os.path.exists(p["workpacket"]) else ""
    ctx["pf_text"] = read_text(p["preflight"]) if os.path.exists(p["preflight"]) else ""
    if facts is None:
        facts = {}
        for key, path in (("board", "board"), ("netlist", "netlist"),
                          ("pins", "pins"), ("bom", "bom"),
                          ("coverage_gate", "coverage_gate"),
                          ("iss387_gate", "iss387_gate"),
                          ("iss387_truth", "iss387_truth"),
                          ("workpacket", "workpacket"), ("preflight", "preflight")):
            fp = p[path]
            facts["%s_md5" % key] = md5_of(fp) if os.path.exists(fp) else None
        facts["board_size"] = os.path.getsize(p["board"]) if os.path.exists(p["board"]) else None
        facts["board_mtime"] = mtime_iso(p["board"]) if os.path.exists(p["board"]) else None
        facts["chain_hits"] = count_chain_hits(p["gate_check"])
        facts["lib_drill"] = measure_lib_drill(p["lib_dir"])
    ctx["facts"] = facts
    mb, err = parse_machine_block(ctx["page_text"])
    ctx["mb"] = mb
    ctx["mb_error"] = err
    return ctx


# =========================================================================
# D1  作业包 §0.2 ③ 的「③」那一项原文里必须有「改孔」这一条
# =========================================================================
def d1(ctx):
    fails = []
    if not ctx["wp_text"]:
        return ["D1 读不到作业包 (★%s★) ⇒ fail-closed (★不许「查不到就算过」★)"
                % ctx["paths"]["workpacket"]]
    parsed = parse_wp02_board_changes(ctx["wp_text"])
    if not parsed:
        return ["D1 作业包 §0.2 ③ 那一行解析不出来 ⇒ fail-closed"]
    if ORDINAL_OF_ITEM not in parsed:
        return ["D1 作业包 §0.2 ③ 那一行里【没有 %s 这一项】⇒ 解析到的子项 = %s ⇒ fail-closed"
                % (ORDINAL_OF_ITEM, sorted(parsed))]
    text = parsed[ORDINAL_OF_ITEM]
    if not has_drill(text):
        fails.append("D1 作业包 §0.2 ③ 的 %s 那一项原文里【查不到「钻孔」这件事】⇒ "
                     "「落 FTS 要改孔 0.65→0.71」这条板侧动作【不在那一趟的清单上】⇒ "
                     "不在清单 = 没人做 = 板投出去才发现排针插不进 ⇒ 【板改两次】 "
                     "★实测原文: %s★" % (ORDINAL_OF_ITEM, text[:120]))
    if "0.71" not in text:
        fails.append("D1 作业包 §0.2 ③ 的 %s 那一项原文里【查不到目标孔径 0.71】⇒ "
                     "★只写了字样没写目标值, 那一趟的人照样不知道要改成多少★" % ORDINAL_OF_ITEM)
    if "1.27" not in text:
        fails.append("D1 作业包 §0.2 ③ 的 %s 那一项原文里【查不到 pitch 那一腿的 1.27】⇒ "
                     "★说明有人把 pitch 那一腿删掉/覆盖了 ⇒ 两条腿少了一条★" % ORDINAL_OF_ITEM)
    return fails


# =========================================================================
# D2  预检清单 B33_PIN_LAND_1P27 的【描述列】里必须有「改孔」这一条
# =========================================================================
def d2(ctx):
    fails = []
    if not ctx["pf_text"]:
        return ["D2 读不到预检清单 (★%s★) ⇒ fail-closed" % ctx["paths"]["preflight"]]
    items = parse_preflight_json(ctx["pf_text"])
    if items is None:
        fails.append("D2 预检清单页的 json 块解析不出来 ⇒ fail-closed")
        item = None
    else:
        item = next((it for it in items if str(it.get("id")) == ITEM_ID), None)
        if item is None:
            fails.append("D2 预检清单页的 json 块里【没有 item %s】⇒ fail-closed" % ITEM_ID)
    if item is not None:
        desc = " ".join(str(item.get(k, "")) for k in ("title", "current_state", "action"))
        if not has_drill(desc):
            fails.append("D2 预检清单 %s 的【描述列】(json 项) 里【查不到「钻孔」这件事】⇒ "
                         "★清单页是那一趟的验收凭据, 它不写钻孔 ⇒ 改没改都没人查★" % ITEM_ID)
        elif "0.71" not in desc:
            fails.append("D2 预检清单 %s 的【描述列】(json 项) 里【查不到目标孔径 0.71】" % ITEM_ID)
    row = parse_preflight_md_row(ctx["pf_text"], ITEM_ID)
    if row is None:
        fails.append("D2 预检清单页的【表格行】里【找不到 %s 那一行】⇒ fail-closed" % ITEM_ID)
    else:
        desc = "%s %s" % (row[2], row[5])
        if not has_drill(desc):
            fails.append("D2 预检清单 %s 的【描述列】(表格行) 里【查不到「钻孔」这件事】⇒ "
                         "★表格是给人看的那一份, 它不写钻孔 ⇒ 人照着做也会漏★" % ITEM_ID)
        elif "0.71" not in desc:
            fails.append("D2 预检清单 %s 的【描述列】(表格行) 里【查不到目标孔径 0.71】" % ITEM_ID)
    return fails


# =========================================================================
# D3  B33_PIN_LAND_1P27 的【验收手段】列里必须有一条读钻孔直径的命令
# =========================================================================
def d3(ctx):
    fails = []
    if not ctx["pf_text"]:
        return ["D3 读不到预检清单 (★%s★) ⇒ fail-closed" % ctx["paths"]["preflight"]]
    items = parse_preflight_json(ctx["pf_text"])
    item = None
    if items is not None:
        item = next((it for it in items if str(it.get("id")) == ITEM_ID), None)
    if item is None:
        fails.append("D3 预检清单页里【拿不到 item %s 的验收手段列】⇒ fail-closed" % ITEM_ID)
    else:
        crit = str(item.get("criterion", ""))
        if not (has_drill(crit) and "0.71" in crit):
            fails.append("D3 预检清单 %s 的【验收手段列】(json 项) 里【没有一条读钻孔直径的验收命令】⇒ "
                         "★没有验收手段 = 改没改成没人知道★" % ITEM_ID)
        elif not ("pcbnew_py.sh" in crit or "GetDrillSize" in crit):
            fails.append("D3 预检清单 %s 的【验收手段列】里的钻孔命令【不是读板钻孔的命令】⇒ "
                         "★必须是读板 (pcbnew_py.sh / GetDrillSize)★" % ITEM_ID)
    row = parse_preflight_md_row(ctx["pf_text"], ITEM_ID)
    if row is None:
        fails.append("D3 预检清单页的【表格行】里【找不到 %s 那一行】⇒ fail-closed" % ITEM_ID)
    else:
        crit = row[6]
        if not (has_drill(crit) and "0.71" in crit):
            fails.append("D3 预检清单 %s 的【验收手段列】(表格行) 里【没有一条读钻孔直径的验收命令】"
                         % ITEM_ID)
    return fails


# =========================================================================
# D4  两端数字必须自洽 (★真相页自己写错目标值也要红★)
# =========================================================================
def d4(ctx):
    fails = []
    mb = ctx["mb"]
    if not mb:
        return ["D4 真相页的机器块拿不到 (%s) ⇒ fail-closed" % (ctx["mb_error"] or "解析失败")]
    miss = [k for k in REQUIRED_MB_KEYS if k not in mb]
    if miss:
        fails.append("D4 真相页机器块缺必需键: %s ⇒ fail-closed" % miss)
        return fails
    off = mb.get("drill_official")
    gen = mb.get("drill_generic")
    tgt = mb.get("drill_target")
    if not num_eq(tgt, off):
        fails.append("D4 机器块 drill_target (%s) != drill_official (%s) ⇒ "
                     "★真相页自己写错了目标值★" % (tgt, off))
    if num_eq(tgt, gen):
        fails.append("D4 机器块 drill_target (%s) == drill_generic (%s) ⇒ "
                     "★目标值等于通用库件值 ⇒ 改孔这个动作等于没发生★" % (tgt, gen))
    lib = ctx["facts"].get("lib_drill") or {}
    vals = set()
    for ref, v in lib.items():
        if v is None:
            fails.append("D4 读不到本机库件 %s 的 .kicad_mod ⇒ fail-closed (★不许「查不到就算过」★)"
                         % ref)
            continue
        if len(v) != 1:
            fails.append("D4 本机库件 %s 的钻孔不唯一 = %s ⇒ fail-closed" % (ref, v))
            continue
        vals.add(v[0])
    if vals:
        if len(vals) != 1:
            fails.append("D4 本机两个库件的钻孔不一致 = %s ⇒ fail-closed" % sorted(vals))
        else:
            measured = list(vals)[0]
            if not num_eq(gen, measured):
                fails.append("D4 机器块 drill_generic (%s) != 本机库件实测值 (%s) ⇒ "
                             "★真相页把第三方库件的值写错了 (或库件被人动过)★" % (gen, measured))
    # 官方那条: PDF 文字层复核 (在盘才查, 查得到就必须对得上)
    src = (mb.get("drill_sources") or {}).get("official") or {}
    pdf = src.get("local_path")
    if pdf:
        ap = os.path.join(PROJ, pdf)
        if os.path.exists(ap):
            txt = ""
            try:
                r = subprocess.run(["pdftotext", "-layout", ap, "-"],
                                   capture_output=True, text=True, timeout=60)
                txt = r.stdout or ""
            except Exception:  # noqa: BLE001
                txt = ""
            if txt.strip():
                if "0.71" not in txt:
                    fails.append("D4 官方 PDF 文字层里【查不到 0.71】⇒ ★官方那条的出处对不上★")
                if ".028" not in txt:
                    fails.append("D4 官方 PDF 文字层里【查不到 .028】⇒ ★官方那条的原文逐字对不上★")
    # *_decision 字段不许代拍
    for k in ("landing_part_decision", "same_batch_granularity_decision",
              "bom_landing_decision", "registration_owner_decision",
              "pad_diameter_decision"):
        if str(mb.get(k)) != "not_decided_here":
            fails.append("D4 机器块 %s = %s ⇒ ★本单不代拍, 必须是 not_decided_here★"
                         % (k, mb.get(k)))
    if mb.get("board_write") != "none" or mb.get("table_write") != "none":
        fails.append("D4 机器块 board_write / table_write 必须都是 none (★本单零写板零落表★)")
    return fails


# =========================================================================
# D5  影响面: MECH 侧不受影响的数名清单
# =========================================================================
def d5(ctx):
    fails = []
    mb = ctx["mb"]
    if not mb:
        return ["D5 真相页的机器块拿不到 ⇒ fail-closed"]
    nums = mb.get("mech_unaffected_numbers")
    if not isinstance(nums, list) or not nums:
        fails.append("D5 机器块里【没有列出 MECH 侧不受影响的数名清单】⇒ "
                     "★「结构件不必因这一趟再返工」这条结论没有落点 = 没算过★")
        return fails
    if any((not isinstance(x, str)) or not x.strip() for x in nums):
        fails.append("D5 机器块 mech_unaffected_numbers 里有空项/非字符串项 ⇒ fail-closed")
        return fails
    if not any(re.search(r"\d", x) for x in nums):
        fails.append("D5 机器块 mech_unaffected_numbers 里【一个数都没有】⇒ fail-closed")
    reason = str(mb.get("mech_unaffected_reason", ""))
    if not reason.strip():
        fails.append("D5 机器块 mech_unaffected_reason 为空 ⇒ fail-closed")
    # §6 正文与机器块不许漂移
    body = sec_body(ctx["page_text"], "## §6")
    if not body.strip():
        fails.append("D5 真相页里【找不到 §6 (MECH 影响面) 节】⇒ fail-closed")
    else:
        hit = False
        for x in nums:
            token = x.split(":")[-1] if ":" in x else x
            if token and token in body:
                hit = True
                break
        if not hit:
            fails.append("D5 真相页 §6 正文里【一个机器块登记的数都查不到】⇒ "
                         "★正文与机器块漂移了 (机器块写了, 人看不到)★")
    return fails


# =========================================================================
# D6  零扰动
# =========================================================================
def d6(ctx):
    fails = []
    mb = ctx["mb"]
    if not mb:
        return ["D6 真相页的机器块拿不到 ⇒ fail-closed"]
    base = mb.get("zero_perturbation_baseline") or {}
    f = ctx["facts"]
    checks = (
        ("板 md5", "board_md5", "board_md5"),
        ("网表 md5", "netlist_md5", "netlist_md5"),
        ("脚表 md5", "pins_md5", "pins_md5"),
        ("BOM md5", "bom_md5", "bom_md5"),
        ("覆盖度闸 md5", "coverage_gate_md5", "coverage_gate_md5"),
        ("ISS-387 闸 md5", "iss387_gate_md5", "iss387_gate_md5"),
        ("ISS-387 真相页 md5", "iss387_truth_md5", "iss387_truth_md5"),
    )
    for label, bkey, fkey in checks:
        exp = base.get(bkey)
        got = f.get(fkey)
        if exp is None:
            fails.append("D6 机器块 zero_perturbation_baseline 里没有 %s 的基线 ⇒ fail-closed" % bkey)
        elif got != exp:
            fails.append("D6 %s 与基线不同: 基线 %s / 实测 %s ⇒ ★本单零扰动破★" % (label, exp, got))
    # ★已签收【页面正文】: 只在【真路径】下比 md5 (★沙盒副本本来就是用来改坏的, 不参与这一项★)
    for label, bkey, pkey in (("作业包 md5", "workpacket_md5", "workpacket"),
                              ("预检清单 md5", "preflight_md5", "preflight")):
        if os.path.abspath(ctx["paths"][pkey]) != os.path.abspath(REAL_PATHS[pkey]):
            continue
        exp = base.get(bkey)
        got = ctx["facts"].get("%s_md5" % pkey)
        if exp is None:
            fails.append("D6 机器块 zero_perturbation_baseline 里没有 %s 的基线 ⇒ fail-closed" % bkey)
        elif got != exp:
            fails.append("D6 %s 与基线不同: 基线 %s / 实测 %s ⇒ ★本单零改既有页面正文破★"
                         % (label, exp, got))
    if base.get("board_size") is not None and f.get("board_size") != base.get("board_size"):
        fails.append("D6 板 size 与基线不同: 基线 %s / 实测 %s" % (base.get("board_size"), f.get("board_size")))
    exp_mt = str(base.get("board_mtime", ""))[:19]
    if exp_mt and not str(f.get("board_mtime", ""))[:19] == exp_mt:
        fails.append("D6 板 mtime 与基线不同: 基线 %s / 实测 %s" % (exp_mt, f.get("board_mtime")))
    ch = f.get("chain_hits")
    if ch != 0:
        fails.append("D6 零挂链破了: state/gate_check.py 里命中 %s %s 次 (★必须是 0·挂链是 main 的地界★)"
                     % (GATE_NAME, ch))
    return fails


# =========================================================================
# D7  本闸自己环境无关 (★沙盒落项目盘 · 两个不同深度读数必须一致★)
# =========================================================================
def facts_digest(paths, cwd):
    """★在指定 cwd 下重新采集一遍事实 ⇒ 摘要串 (★用于证明「与 cwd 无关」★)★"""
    old = os.getcwd()
    try:
        os.chdir(cwd)
        c = collect(paths)
        blob = json.dumps({
            "facts": {k: v for k, v in c["facts"].items() if k != "lib_drill"},
            "lib": c["facts"].get("lib_drill"),
            "page_len": len(c["page_text"]),
            "mb": hashlib.md5(json.dumps(c["mb"], ensure_ascii=False,
                                          sort_keys=True).encode("utf-8")).hexdigest()
            if c["mb"] else None,
        }, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(blob.encode("utf-8")).hexdigest()
    finally:
        os.chdir(old)


def d7(ctx):
    fails = []
    cwd_a = PROJ
    cwd_b = os.path.join(PROJ, "HW", "PCB")
    if not os.path.isdir(cwd_b):
        cwd_b = os.path.expanduser("~")
    d1_ = facts_digest(ctx["paths"], cwd_a)
    d2_ = facts_digest(ctx["paths"], cwd_b)
    if d1_ != d2_:
        fails.append("D7 两个不同深度 (cwd=%s vs cwd=%s) 的读数不一致 ⇒ "
                     "★本闸的路径解析有 cwd 依赖 ⇒ 在别的目录下跑会读错文件★"
                     % (cwd_a, cwd_b))
    # 沙盒必须落项目盘
    if not os.path.abspath(SANDBOX).startswith(os.path.abspath(PROJ) + os.sep):
        fails.append("D7 沙盒路径 %s 不在项目盘内 ⇒ ★不许落系统 /tmp★" % SANDBOX)
    return fails


CHECKS = (
    ("D1", d1, "作业包 §0.2 ③ 的「③」那一项原文里有「改孔」这一条"),
    ("D2", d2, "预检清单 B33_PIN_LAND_1P27 的描述列里有「改孔」这一条"),
    ("D3", d3, "B33_PIN_LAND_1P27 的验收手段列里有读钻孔直径的命令"),
    ("D4", d4, "两端数字自洽 (target == official != generic == 本机库件实测)"),
    ("D5", d5, "MECH 侧不受影响的数名清单在位"),
    ("D6", d6, "零写板 / 零落表 / 零挂链 / 已签收件 md5 同基线"),
    ("D7", d7, "本闸自己与 cwd 无关 (两个深度读数一致)"),
)


def run_all(ctx):
    return [(code, desc, fn(ctx)) for code, fn, desc in CHECKS]


def report(results, title):
    print("── %s" % title)
    nfail = 0
    for code, desc, fails in results:
        if fails:
            nfail += 1
            print("  [%s] ✘ RED  %s" % (code, desc))
            for f in fails:
                print("        · %s" % f)
        else:
            print("  [%s] ✔ GREEN  %s" % (code, desc))
    print("── %s: %d/%d 条绿" % (title, len(results) - nfail, len(results)))
    return nfail


# =========================================================================
# 沙盒构造 (★只在沙盒副本上改, 真文件一个字节不许动★)
# =========================================================================
DRILL_TITLE = ("`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm + 钻孔 Ø0.65→Ø0.71mm "
               "(★ISS-391·落 FTS 官方 Ø0.71 TYP·库件默认 0.65·不可只做 pitch★)")
DRILL_STATE = ("★**ISS-391 追加 [实测]**: 落 FTS 官方 Ø0.71 TYP, 库件默认 (drill 0.65) 偏小 0.06; "
               "与 pitch 同属 ③, 不可只做其一")
DRILL_CRIT = ("; `bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard("
              "'HW/PCB/demo_mainboard.kicad_pcb');print('; '.join('%s drill = %.2f'%"
              "(f.GetReference(), pcbnew.ToMM(p.GetDrillSize().x)) for f in b.GetFootprints() "
              "if f.GetReference() in ('J_DEBUG','J_UART') for p in f.Pads()))\"` "
              "⇒ 期望读数: J_DEBUG drill = 0.71 / J_UART drill = 0.71")


WORKPACKET_DRILL_LEG = ("排针 land 0.50→1.27mm + 钻孔 0.65→0.71mm "
                        "(★ISS-391·落 FTS 必须用 Samtec 官方 Ø0.71 TYP·"
                        "库件默认 (drill 0.65) 偏小 0.06·"
                        "同属这一项的两条腿, 不可只做其一★)")


def make_fixed_workpacket(text):
    """★把作业包 §0.2 ③ 的「③」那一项补上「钻孔 0.65→0.71」这一腿 (★沙盒用★)★"""
    old = "排针 land 0.50→1.27mm"
    if old not in text:
        raise AssertionError("自测前提不成立: 作业包里找不到 %r" % old)
    return text.replace(old, WORKPACKET_DRILL_LEG, 1)


def set_wp_ordinal(text, ordinal, new_text):
    """★把作业包 §0.2 ③ 那一行里【某个序号的整条子项】换成 new_text (★沙盒用★)★"""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "板侧改动清单" not in line or "①" not in line:
            continue
        cell = None
        for c in line.split("|"):
            if "①" in c:
                cell = c
                break
        if cell is None:
            continue
        parts = re.split(r"([%s])" % ORDINALS, cell)
        out, cur, done = [], None, False
        for p in parts:
            if len(p) == 1 and p in ORDINALS:
                cur = p
                done = False
                out.append(p)
            elif cur == ordinal and not done:
                out.append(new_text)
                done = True
            else:
                out.append(p)
        newcell = "".join(out)
        newlines = []
        for c in line.split("|"):
            newlines.append(newcell if c == cell else c)
        lines[i] = "|".join(newlines)
        return "\n".join(lines)
    raise AssertionError("自测前提不成立: 作业包里找不到「板侧改动清单」那一行")


def make_fixed_preflight(text, add_desc=True, add_crit=True):
    """★把 B33 的描述列 + 验收手段列补上改孔 (★沙盒用★)★"""
    items = parse_preflight_json(text)
    if items is None:
        raise AssertionError("自测前提不成立: 预检清单 json 块解析不出来")
    for it in items:
        if str(it.get("id")) != ITEM_ID:
            continue
        if add_desc:
            it["title"] = DRILL_TITLE
            it["current_state"] = str(it.get("current_state", "")) + " " + DRILL_STATE
        if add_crit:
            it["criterion"] = str(it.get("criterion", "")) + DRILL_CRIT
    out = replace_preflight_json(text, items)
    # 表格行同步
    lines = out.split("\n")
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s.startswith("|") or ITEM_ID not in s:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 7:
            continue
        if add_desc:
            cells[2] = DRILL_TITLE
            cells[5] = cells[5] + " " + DRILL_STATE
        if add_crit:
            cells[6] = cells[6] + DRILL_CRIT
        lines[i] = "| " + " | ".join(cells) + " |"
        break
    return "\n".join(lines)


def _mutate_mb(mb_text, old, new):
    if old not in mb_text:
        raise AssertionError("自测前提不成立: 机器块里找不到 %r" % old)
    return mb_text.replace(old, new, 1)


def _rebuild_page(page_text, mb_text):
    blocks = list(re.finditer(r"```json\s*\n(.*?)\n```", page_text, re.S))
    if not blocks:
        raise AssertionError("自测前提不成立: 页面里没有 json 块")
    last = blocks[-1]
    return page_text[:last.start(1)] + mb_text + page_text[last.end(1):]


# =========================================================================
# 自测
# =========================================================================
def selftest():
    os.makedirs(SANDBOX, exist_ok=True)
    real_md5_before = {k: md5_of(REAL_PATHS[k]) for k in
                       ("page", "workpacket", "preflight", "board", "netlist",
                        "pins", "bom", "coverage_gate", "iss387_gate", "iss387_truth")}

    # ---- 沙盒: 已补登记的作业包 / 预检清单 / 真相页 / 库件 -----------------
    sb = {
        "workpacket": os.path.join(SANDBOX, "BOARD_ONEPASS_WORKPACKET.md"),
        "preflight": os.path.join(SANDBOX, "BOARD_ONEPASS_PREFLIGHT.md"),
        "page": os.path.join(SANDBOX, "BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md"),
        "lib_dir": os.path.join(SANDBOX, "lib"),
    }
    os.makedirs(sb["lib_dir"], exist_ok=True)
    wp_fixed = make_fixed_workpacket(read_text(REAL_PATHS["workpacket"]))
    with open(sb["workpacket"], "w", encoding="utf-8") as fh:
        fh.write(wp_fixed)
    pf_fixed = make_fixed_preflight(read_text(REAL_PATHS["preflight"]))
    with open(sb["preflight"], "w", encoding="utf-8") as fh:
        fh.write(pf_fixed)
    page_text = read_text(REAL_PATHS["page"])
    with open(sb["page"], "w", encoding="utf-8") as fh:
        fh.write(page_text)
    for ref, fn in LIB_FILES.items():
        shutil.copyfile(os.path.join(REAL_PATHS["lib_dir"], fn),
                        os.path.join(sb["lib_dir"], fn))
    # 沙盒的其余路径仍指向真文件 (只读) —— 覆盖度闸/ISS-387 闸/板/三表
    sb.update({
        "coverage_gate": REAL_PATHS["coverage_gate"],
        "iss387_gate": REAL_PATHS["iss387_gate"],
        "iss387_truth": REAL_PATHS["iss387_truth"],
        "board": REAL_PATHS["board"],
        "netlist": REAL_PATHS["netlist"],
        "pins": REAL_PATHS["pins"],
        "bom": REAL_PATHS["bom"],
        "gate_check": REAL_PATHS["gate_check"],
    })
    base_mb, err = parse_machine_block(page_text)
    if err:
        print("SELFTEST ABORT: %s" % err)
        return 1
    base_mb_text = json.dumps(base_mb, ensure_ascii=False, indent=1)

    cases = []   # (用例名, 期望红的那条, paths_override 或 None, facts_override 或 None)

    # --- 正向对照: 沙盒已补登记 ⇒ 全绿 --------------------------------
    cases.append(("正向对照 (沙盒已按 §4 补登记 ⇒ D1~D7 全绿)", None, None, None))

    # --- 反向用例 ①: 作业包 ③ 里的「钻孔」两个字删掉 ⇒ D1 红 -----------
    wp03 = parse_wp02_board_changes(wp_fixed).get(ORDINAL_OF_ITEM, "")
    wp_no = set_wp_ordinal(wp_fixed, ORDINAL_OF_ITEM,
                           wp03.replace(WORKPACKET_DRILL_LEG, "排针 land 0.50→1.27mm"))
    p = dict(sb)
    p["workpacket"] = os.path.join(SANDBOX, "case01_workpacket.md")
    with open(p["workpacket"], "w", encoding="utf-8") as fh:
        fh.write(wp_no)
    cases.append(("① 删掉作业包 §0.2 ③ 里的「钻孔」两个字 ⇒ D1 红", ["D1"], p, None))

    # --- 反向用例 ②: B33 描述列里的钻孔字样删掉 ⇒ D2 红 ----------------
    pf_no = make_fixed_preflight(read_text(REAL_PATHS["preflight"]), add_desc=False,
                                 add_crit=True)
    p = dict(sb)
    p["preflight"] = os.path.join(SANDBOX, "case02_preflight.md")
    with open(p["preflight"], "w", encoding="utf-8") as fh:
        fh.write(pf_no)
    cases.append(("② 删掉 B33_PIN_LAND_1P27 描述列里的钻孔字样 ⇒ D2 红", "D2", p, None))

    # --- 反向用例 ③: B33 验收手段列里那条读钻孔的命令删掉 ⇒ D3 红 ----
    pf_no2 = make_fixed_preflight(read_text(REAL_PATHS["preflight"]), add_desc=True,
                                  add_crit=False)
    p = dict(sb)
    p["preflight"] = os.path.join(SANDBOX, "case03_preflight.md")
    with open(p["preflight"], "w", encoding="utf-8") as fh:
        fh.write(pf_no2)
    cases.append(("③ 删掉 B33_PIN_LAND_1P27 验收手段列里读钻孔的命令 ⇒ D3 红",
                  "D3", p, None))

    # --- 反向用例 ④: 机器块 drill_target 改成 0.65 ⇒ D4 红 -------------
    t = _mutate_mb(base_mb_text, '"drill_target": "0.71"', '"drill_target": "0.65"')
    p = dict(sb)
    p["page"] = os.path.join(SANDBOX, "case04_page.md")
    with open(p["page"], "w", encoding="utf-8") as fh:
        fh.write(_rebuild_page(page_text, t))
    cases.append(("④ 机器块 drill_target 改成 0.65 (= 通用件值) ⇒ D4 红", "D4", p, None))

    # --- 反向用例 ⑤: 机器块 mech_unaffected_numbers 清空 ⇒ D5 红 -------
    mb5 = json.loads(base_mb_text)
    mb5["mech_unaffected_numbers"] = []
    p = dict(sb)
    p["page"] = os.path.join(SANDBOX, "case05_page.md")
    with open(p["page"], "w", encoding="utf-8") as fh:
        fh.write(_rebuild_page(page_text, json.dumps(mb5, ensure_ascii=False, indent=1)))
    cases.append(("⑤ 机器块 mech_unaffected_numbers 清空 ⇒ D5 红", "D5", p, None))

    # --- 反向用例 ⑥: 板 md5 被动过 ⇒ D6 红 -----------------------------
    bad = dict(collect(sb)["facts"])
    bad["board_md5"] = "00000000000000000000000000000000"
    cases.append(("⑥ 板 md5 被动过 ⇒ D6 红", "D6", None, bad))

    # --- 反向用例 ⑦: 挂链命中数 = 1 ⇒ D6 红 ----------------------------
    bad = dict(collect(sb)["facts"])
    bad["chain_hits"] = 1
    cases.append(("⑦ 零挂链被破 (chain hits = 1) ⇒ D6 红", "D6", None, bad))

    # --- 反向用例 ⑧: 机器块 drill_generic 改成 0.71 ⇒ D4 红 ------------
    t = _mutate_mb(base_mb_text, '"drill_generic": "0.65"', '"drill_generic": "0.71"')
    p = dict(sb)
    p["page"] = os.path.join(SANDBOX, "case08_page.md")
    with open(p["page"], "w", encoding="utf-8") as fh:
        fh.write(_rebuild_page(page_text, t))
    cases.append(("⑧ 机器块 drill_generic 改成 0.71 (≠ 本机库件实测 0.65) ⇒ D4 红",
                  "D4", p, None))

    # --- 反向用例 ⑨: 机器块 drill_target 改成 0.70 ⇒ D4 红 -------------
    t = _mutate_mb(base_mb_text, '"drill_target": "0.71"', '"drill_target": "0.70"')
    p = dict(sb)
    p["page"] = os.path.join(SANDBOX, "case09_page.md")
    with open(p["page"], "w", encoding="utf-8") as fh:
        fh.write(_rebuild_page(page_text, t))
    cases.append(("⑨ 机器块 drill_target 改成 0.70 (既非 official 也非 generic) ⇒ D4 红",
                  "D4", p, None))

    # --- 反向用例 ⑩: 作业包 ③ 的 pitch 那一腿被覆盖掉 ⇒ D1 红 ---------
    wp_leg = set_wp_ordinal(
        wp_fixed, ORDINAL_OF_ITEM,
        "`J_DEBUG`/`J_UART` 排针 land 改 + 钻孔 0.65→0.71mm (★ISS-391★)")
    p = dict(sb)
    p["workpacket"] = os.path.join(SANDBOX, "case10_workpacket.md")
    with open(p["workpacket"], "w", encoding="utf-8") as fh:
        fh.write(wp_leg)
    cases.append(("⑩ 作业包 ③ 的 pitch 那一腿的 1.27 被覆盖掉 ⇒ D1 红", ["D1"], p, None))

    # --- 反向用例 ⑪: 作业包 §0.2 ③ 那一整行删掉 ⇒ D1 红 (fail-closed) --
    lines = [ln for ln in wp_fixed.split("\n") if "板侧改动清单" not in ln]
    p = dict(sb)
    p["workpacket"] = os.path.join(SANDBOX, "case11_workpacket.md")
    with open(p["workpacket"], "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    cases.append(("⑪ 作业包 §0.2 ③ 那一整行删掉 ⇒ D1 红 (fail-closed)",
                  ["D1"], p, None))

    # --- 反向用例 ⑫: 库件钻孔被动过 (沙盒副本 0.60) ⇒ D4 红 ------------
    lib_bad = os.path.join(SANDBOX, "lib_bad")
    os.makedirs(lib_bad, exist_ok=True)
    for ref, fn in LIB_FILES.items():
        txt = read_text(os.path.join(REAL_PATHS["lib_dir"], fn))
        with open(os.path.join(lib_bad, fn), "w", encoding="utf-8") as fh:
            fh.write(txt.replace("(drill 0.65)", "(drill 0.60)"))
    p = dict(sb)
    p["lib_dir"] = lib_bad
    cases.append(("⑫ 本机库件钻孔被动过 (0.65→0.60) ⇒ D4 红", "D4", p, None))

    # --- 反向用例 ⑬: 路径改成 cwd 依赖 ⇒ D7 红 -------------------------
    p = dict(sb)
    p["page"] = "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md"
    cases.append(("⑬ 路径解析改成 cwd 依赖 (相对路径) ⇒ D7 红", ["D7"], p, None))

    # --- 反向用例 ⑮: 预检清单页读不到 ⇒ D2 + D3 同时 fail-closed --------
    p = dict(sb)
    p["preflight"] = os.path.join(SANDBOX, "case15_preflight_MISSING.md")
    cases.append(("⑮ 预检清单页读不到 ⇒ D2 + D3 同时 fail-closed", ["D2", "D3"], p, None))

    # --- 反向用例 ⑭: 机器块 *_decision 被代拍 ⇒ D4 红 ------------------
    t = _mutate_mb(base_mb_text, '"landing_part_decision": "not_decided_here"',
                   '"landing_part_decision": "decided_fts"')
    p = dict(sb)
    p["page"] = os.path.join(SANDBOX, "case14_page.md")
    with open(p["page"], "w", encoding="utf-8") as fh:
        fh.write(_rebuild_page(page_text, t))
    cases.append(("⑭ 机器块 landing_part_decision 被代拍 ⇒ D4 红", "D4", p, None))

    npass = 0
    ntotal = len(cases)
    for name, want_red, paths, facts in cases:
        pp = paths if paths is not None else sb
        ctx = collect(pp, facts=facts)
        results = run_all(ctx)
        reds = [code for code, _d, f in results if f]
        if want_red is None:
            ok = not reds
            detail = "期望全绿 · 实际红: %s" % (reds or "无")
        else:
            want = [want_red] if isinstance(want_red, str) else list(want_red)
            ok = (sorted(reds) == sorted(want))
            detail = "期望【只有】%s 红 · 实际红: %s" % ("+".join(want), reds or "无")
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
        print("        %s" % detail)
        if ok:
            npass += 1

    # ---- 真文件 md5 复验 (★跑完自测必须复验真文件 md5 未变★) -----------
    changed = [k for k, v in real_md5_before.items()
               if md5_of(REAL_PATHS[k]) != v]
    if changed:
        npass_ok = False
        print("  [FAIL] 自测后真文件 md5 变了: %s ⇒ ★自测不许碰真文件★" % changed)
    else:
        npass_ok = True
        print("  [PASS] 自测后真文件 md5 全部未变 (板/网表/脚表/BOM/作业包/预检清单/"
              "覆盖度闸/ISS-387 闸/ISS-387 真相页)")
    if npass_ok:
        npass += 1
    ntotal += 1
    print("── selftest: %d/%d PASS" % (npass, ntotal))
    if npass == ntotal:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


# =========================================================================
# main
# =========================================================================
def main():
    ap = argparse.ArgumentParser(
        description="ISS-391 闸: 排针改孔 0.65→0.71 有没有进到「板只改一次」那一趟的清单里")
    ap.add_argument("--selftest", action="store_true", help="跑自测 (反向用例)")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    print("★ ISS-391 闸 D1~D7 · 「落 FTS 排针改孔 0.65→0.71」有没有进到"
          "「板只改一次」那一趟的作业包 §0.2 ③ + 预检清单 B33_PIN_LAND_1P27 里")
    print("★ 本闸【现场解析真文件】(路径从本闸自己推, 不看环境变量) ⇒ "
          "真实清单里缺这一条 ⇒ 本闸当场红")
    print("★ 红 ⇒ 那就是 §4 要 main 落的登记项 (不是本闸故障); "
          "main 落完 §4 #1/#2/#3 ⇒ 同一条命令即转绿")
    ctx = collect()
    results = run_all(ctx)
    nfail = report(results, "ISS-391 排针改孔同批完整性闸")
    if nfail:
        print("❌ 有 %d 条判据红 (★D1/D2/D3 = 「改孔」这条板侧动作还没进清单 ⇒ "
              "详见 HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4★)" % nfail)
        return 1
    print("✅ 全绿 (★改孔这一条已经进了作业包 §0.2 ③ + 预检清单 B33_PIN_LAND_1P27★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
