#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_generator_value_drift_closed.py —— ★「板那一趟」生成器重跑 Value 漂移 + `C_VBUS_GND` 掉板 闭合闸★

★**零挂链**: ★本闸【故意不挂进 `state/gate_check.py`】(★挂不挂链 = main 的地界★) ⇒
   ★`grep -c check_generator_value_drift_closed state/gate_check.py` 必须 = 0★

★**性质**: ★**fail-closed** ★ ⇒ ★**真相页缺一条登记 / 值对不上 / 等级越界 / 机理缺项 /
   路线缺项 / 出现代拍措辞 / 外发·挂链·写板 ⇒ 一律红 (rc=1)★

★**判据**:
  ★D1 (fail-closed 命门)★: 板面 Value ≠ 网表侧 Value 的**每一条**都必须在本单真相页 §2 台账里登记
        (位号 + 双方逐字值 + 处置口径) ⇒ ★**少登记一条 ⇒ 红** ⇒ ★**不许任何豁免 / 白名单 / 已知例外**★
  ★D2★: 台账里登记的值必须与**现读值逐字相同** ⇒ 台账过期 ⇒ 红
  ★D3★: 台账每行必须带证据等级, 且等级只能用五级白名单 ⇒ 越界 (例如 `[官方]`) ⇒ 红
  ★D4★: `C_VBUS_GND` 的机理结论必须在页上 (三处存在性 + 掉板机理) ⇒ 缺 ⇒ 红
  ★D5★: 三条路线 (甲/乙/丙) 的代价账必须齐 ⇒ 缺一条 ⇒ 红
  ★D6★: 零代拍 —— 页里不许出现替 main / 老板拍板的措辞 ⇒ 出现 ⇒ 红
  ★D7★: 零外发 + 零挂链 + 零写板自证 ⇒ 任一不满足 ⇒ 红

★**用法**:
  python3 HW/check_generator_value_drift_closed.py              # 主模式 (rc=0 全绿 / rc=1 有红项)
  python3 HW/check_generator_value_drift_closed.py --selftest    # 自测 (rc=0, 末行逐字 ALL TESTS PASS)

★**纪律**: ★判据只能加严不许放松· 自测夹具不许写死要测的数· 沙盒不许硬链接到真件 (★L-24★)·
  ★不许往系统 `/tmp` 写 (★沙盒落项目盘 `tmp/iss402/`★)★
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

BOARD = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
BOM = os.path.join(PROJ, "HW", "BOM_v1.csv")
GATE_CHECK = os.path.join(PROJ, "state", "gate_check.py")
TRUTH_PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_GENERATOR_VALUE_DRIFT.md")
SANDBOX = os.path.join(PROJ, "tmp", "iss402", "selftest")

GATE_NAME = "check_generator_value_drift_closed"
BOARD_FILTER = "MAIN_PCB"
PSEUDO = ("RAIL_", "NET_")

# ★D3 白名单: 只有这五级 (★与 brief §2.1 一致★)
EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")

# ★D6: 替 main / 老板拍板的措辞 (★白名单只放中性词★)
D6_FORBIDDEN = (
    "已决定", "就按路线", "老板已拍", "main 已拍", "已拍板", "拍板为", "本单决定",
    "最终选定", "决定采用路线", "裁定为", "予以采纳", "批准采用", "定案",
)
D6_NEUTRAL_OK = ("not_decided_here", "待 main 拍", "不代拍", "本单不代拍", "谁拍", "留给 main")

# ★D4: `C_VBUS_GND` 机理结论必须在页上出现的关键词
#   (★三处存在性 = 网表 / 板面 / BOM 三处都要点到 + 掉板机理★)
D4_KEYS = ("C_VBUS_GND", "CHG_BOARD", "BOARD_FILTER", "MAIN_PCB",
           "掉板", "多余", "网表", "板面", "BOM")
D4_BLOCK_KEYS = ("in_netlist", "netlist_board_col", "on_board", "drop_reason", "evidence_level")

# ★D5: 三条路线
D5_ROUTES = ("A", "B", "C")
D5_ROUTE_WORDS = ("路线甲", "路线乙", "路线丙")

# ★D7: 闸不许碰的东西
#   ★★刻意【拆成拼接】★★ ⇒ ★★本文件自身的源码里不会留下这两个字面量★★
#   ⇒ ★★否则 D7 会被闸自己的源码判红 (★自指陷阱★)★★
D7_BANNED_TOKENS = ("state/" + "out" + "box", "out" + "box/")


# ============================================================ 板面读数 (方法乙·自写扫描器)
class Sym(str):
    __slots__ = ()


def _tokenize(text):
    i, n, out = 0, len(text), []
    while i < n:
        c = text[i]
        if c in "()":
            out.append(c)
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n:
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                    continue
                if text[j] == '"':
                    break
                buf.append(text[j])
                j += 1
            out.append(("str", "".join(buf)))
            i = j + 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < n and (not text[j].isspace()) and text[j] not in '()"':
                j += 1
            out.append(Sym(text[i:j]))
            i = j
    return out


def _parse(tokens, pos=0):
    tok = tokens[pos]
    if tok == "(":
        lst, pos = [], pos + 1
        while pos < len(tokens) and tokens[pos] != ")":
            node, pos = _parse(tokens, pos)
            lst.append(node)
        return ("list", lst), pos + 1
    if tok == ")":
        raise ValueError("unexpected )")
    if isinstance(tok, tuple):
        return tok, pos + 1
    return ("sym", str(tok)), pos + 1


def _kids(node):
    return node[1] if node[0] == "list" else []


def _head(node):
    k = _kids(node)
    if k and k[0][0] == "sym":
        return k[0][1]
    return ""


def _val(node):
    if node[0] in ("str", "sym"):
        return node[1]
    return ""


def _find_all(node, name):
    out = []
    for k in _kids(node):
        if k[0] == "list":
            if _head(k) == name:
                out.append(k)
            out.extend(_find_all(k, name))
    return out


def _prop(node, pname):
    for p in _find_all(node, "property"):
        k = _kids(p)
        if len(k) >= 2 and _val(k[1]) == pname:
            return _val(k[2]) if len(k) >= 3 else ""
    return None


def read_board_values(path):
    """★读板: {ref: Value}★ (★只读, 不写★)"""
    with open(path, "rb") as f:
        text = f.read().decode("utf-8", errors="replace")
    root, _ = _parse(_tokenize(text), 0)
    out = {}
    for fp in _find_all(root, "footprint"):
        ref = _prop(fp, "Reference")
        if ref:
            out[ref] = _prop(fp, "Value")
    return out


def file_fp(path):
    with open(path, "rb") as f:
        b = f.read()
    st = os.stat(path)
    return {"md5": hashlib.md5(b).hexdigest(), "size": st.st_size, "mtime": st.st_mtime}


# ============================================================ 网表 / BOM / 生成器口径
def pick_board_values(rows):
    """★本体行优先 + 逐字截断 40 (★口径 = state/gen_pcb_netlist_board.py::pick_board_values★)"""
    value_of, value_body = {}, {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if not ref:
            continue
        v = (r.get("value") or "").strip()
        if not v:
            continue
        if ref not in value_of:
            value_of[ref] = v[:40]
        typ = (r.get("type") or "").strip()
        if typ not in ("NET", "") and ref not in value_body:
            value_body[ref] = v[:40]
    for ref, v in value_body.items():
        value_of[ref] = v
    return value_of


USBIF_RE = re.compile(r"^(?:[AB](?:1|4|5|6|7|8|9|12)|shield)$")


def _is_pad_name(tail):
    """★同生成器 state/gen_pcb_netlist_board.py:225-237 的口径★"""
    if not tail:
        return False
    if re.fullmatch(r"pin\d+(\+pin\d+)*", tail):
        return True
    if USBIF_RE.match(tail):
        return True
    return False


def _split_node(node):
    node = (node or "").strip()
    if not node:
        return None, None
    m = re.match(r"^([A-Za-z_0-9]+)\s+(.*)$", node)
    if not m:
        return node, None
    return m.group(1), m.group(2).strip()


def special_values():
    """★特殊路径封装自带写死 Value (★源码实读, 不手抄★)"""
    out = {}
    src = open(os.path.join(PROJ, "state", "som_btb_footprint.py"), encoding="utf-8").read()
    if "Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm (SOM {conn})" not in src:
        raise RuntimeError("som_btb_footprint.py 口径变了 ⇒ 闸需同步")
    for conn in ("P1", "P2", "P3", "P4"):
        out["J_SOM_%s" % conn] = ("Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm (SOM %s) "
                                  "★pin1 所在排待实测确认" % conn)
    src = open(os.path.join(PROJ, "state", "display_fpc_footprint.py"), encoding="utf-8").read()
    if 'value="HIROSE FH12-22S-0.5SH(55) 22p 0.5mm"' not in src:
        raise RuntimeError("display_fpc_footprint.py 口径变了 ⇒ 闸需同步")
    out["CONN_LIGHT"] = "HIROSE FH12-22S-0.5SH(55) 22p 0.5mm"
    src = open(os.path.join(PROJ, "state", "usb_c_footprint.py"), encoding="utf-8").read()
    if '"GCT USB4105-16P USB-C 电源口 (自绘, 原厂图纸 Rev B3)"' not in src:
        raise RuntimeError("usb_c_footprint.py 口径变了 ⇒ 闸需同步")
    out["J_USB_C"] = "GCT USB4105-16P USB-C 电源口 (自绘, 原厂图纸 Rev B3)"
    src = open(os.path.join(PROJ, "state", "tmp117_footprint.py"), encoding="utf-8").read()
    if 'value="TI TMP117 (WSON-6 DRV0006B, 2x2mm)"' not in src:
        raise RuntimeError("tmp117_footprint.py 口径变了 ⇒ 闸需同步")
    out["U_TEMP"] = "TI TMP117 (WSON-6 DRV0006B, 2x2mm)"
    return out


def collect_live():
    """★现读盘面 + 网表 + BOM ⇒ 生成【实测台账】★"""
    board = read_board_values(BOARD)
    rows = list(csv.DictReader(open(NETLIST, encoding="utf-8-sig")))
    main_rows = [r for r in rows if (r.get("board") or BOARD_FILTER).strip() == BOARD_FILTER]
    gen_of = pick_board_values(main_rows)
    special = special_values()

    main_refs = {(r.get("ref") or "").strip() for r in main_rows}
    main_refs.discard("")
    real = {x for x in main_refs if not x.startswith(PSEUDO)}
    node_universe = set()
    for r in main_rows:
        for k in ("node1", "node2"):
            comp, tail = _split_node(r.get(k))
            if not comp or comp in real or comp.startswith(PSEUDO):
                continue
            if _is_pad_name(tail):
                node_universe.add(comp)

    def gen_would_be(ref):
        if ref in special:
            return special[ref], "special"
        if ref in gen_of:
            return gen_of[ref], "netlist_body"
        if ref in node_universe:
            return ("SoM BTB %s (100pin, 部分已分配)" % ref.split("_")[-1], "som_placeholder")
        return None, "not_placed"

    bom_rows = list(csv.DictReader(open(BOM, encoding="utf-8-sig")))
    bom_of = {r["ref"].strip(): (r.get("value") or "") for r in bom_rows}

    drift, drops = {}, {}
    for ref, bval in board.items():
        gval, placement = gen_would_be(ref)
        if placement == "not_placed":
            drops[ref] = {"board_value": bval, "bom_value": bom_of.get(ref),
                          "netlist_rows": [i + 1 for i, r in enumerate(rows)
                                           if (r.get("ref") or "").strip() == ref],
                          "netlist_board_cols": sorted({(r.get("board") or "") for r in rows
                                                        if (r.get("ref") or "").strip() == ref})}
        elif bval != gval:
            drift[ref] = {"board_value": bval, "netlist_value": gval,
                          "bom_value": bom_of.get(ref), "placement": placement}

    return {
        "board": board,
        "drift": drift,
        "drops": drops,
        "bom": bom_of,
        "netlist_rows_total": len(rows),
        "netlist_rows_main": len(main_rows),
        "fp_before": file_fp(BOARD),
        "netlist_md5": file_fp(NETLIST)["md5"],
        "bom_md5": file_fp(BOM)["md5"],
    }


# ============================================================ 真相页解析
def read_page(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_page(page_text):
    """★⇒ {table_rows: {ref: {...}}, block: {...}, sections: {...}}★"""
    out = {"table_rows": {}, "block": {}, "sections": {}, "table_order": []}
    if not page_text:
        return out
    # §2 表 (★从 §2 到 §3 之间★)
    i = page_text.find("## §2")
    j = page_text.find("## §3", i + 1) if i >= 0 else -1
    sec2 = page_text[i:j] if (i >= 0 and j > i) else ""
    for line in sec2.splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            continue
        ref = cells[1].strip("`")
        out["table_rows"][ref] = {
            "ref": ref,
            "board_value": cells[2].strip("`"),
            "netlist_value": cells[3].strip("`"),
            "bom_value": cells[4].strip("`"),
            "diff_type": cells[5],
            "affects_electrical": cells[6],
            "landing_owner": cells[7],
            "evidence_level": cells[8],
        }
        out["table_order"].append(ref)
    # §6 机器块 (yaml fenced)
    m = re.search(r"```yaml\s*\n(.*?)\n```", page_text, re.S)
    if m:
        try:
            import yaml
            out["block"] = yaml.safe_load(m.group(1)) or {}
        except Exception as e:  # pragma: no cover
            out["block_error"] = str(e)
    # §3 段落文本
    k = page_text.find("## §3")
    l = page_text.find("## §4", k + 1) if k >= 0 else -1
    out["sections"]["3"] = page_text[k:l] if (k >= 0 and l > k) else ""
    out["sections"]["4"] = page_text[l:page_text.find("## §5", l)] if l > 0 else ""
    return out


# ============================================================ 判据
def evaluate(page_text, live, opts=None):
    """★⇒ (fails: dict D-code → 说明, oks: dict)★"""
    opts = opts or {}
    fails = {}
    page = parse_page(page_text)
    block = page["block"].get("generator_value_drift") or {}
    if page.get("block_error"):
        fails["D1"] = "机器块 YAML 解析失败: %s" % page["block_error"]
    if not page_text:
        for code in ("D1", "D2", "D3", "D4", "D5", "D6"):
            fails[code] = "真相页不存在 ⇒ fail-closed"

    live_drift = live["drift"]
    live_drops = live["drops"]

    # ---- D1: 覆盖 (★每条实测差异都必须登记 + 行数相等 + 有处置口径★)
    d1 = []
    for ref, d in sorted(live_drift.items()):
        t = page["table_rows"].get(ref)
        if t is None:
            d1.append("未登记: %s (板面=%r / 网表侧=%r)" % (ref, d["board_value"], d["netlist_value"]))
            continue
        if t["board_value"] != d["board_value"] or t["netlist_value"] != d["netlist_value"]:
            continue      # ★值对不上归 D2★
        if not t["landing_owner"].strip():
            d1.append("登记了但缺处置口径 (落表归属): %s" % ref)
        if not t["diff_type"].strip():
            d1.append("登记了但缺差异类型: %s" % ref)
    extra = sorted(set(page["table_rows"]) - set(live_drift))
    if extra:
        d1.append("台账里多出【实测无差异】的位号: %s" % ", ".join(extra))
    rc = block.get("row_count")
    if rc is None:
        d1.append("机器块缺 row_count")
    elif int(rc) != len(live_drift):
        d1.append("机器块 row_count=%s ≠ 实测差异条数=%d" % (rc, len(live_drift)))
    brows = block.get("rows") or []
    if len(brows) != len(live_drift):
        d1.append("机器块 rows 行数=%d ≠ 实测差异条数=%d" % (len(brows), len(live_drift)))
    if d1:
        fails["D1"] = "; ".join(d1)

    # ---- D2: 登记值 == 现读值 (★台账过期即红★)
    d2 = []
    for ref, t in page["table_rows"].items():
        d = live_drift.get(ref)
        if d is None:
            continue
        if t["board_value"] != d["board_value"]:
            d2.append("%s 板面值: 台账=%r ≠ 现读=%r" % (ref, t["board_value"], d["board_value"]))
        if t["netlist_value"] != d["netlist_value"]:
            d2.append("%s 网表侧值: 台账=%r ≠ 现读=%r" % (ref, t["netlist_value"], d["netlist_value"]))
    for br in brows:
        ref = br.get("ref")
        d = live_drift.get(ref)
        if d is None:
            continue
        if br.get("board_value") != d["board_value"]:
            d2.append("%s 机器块板面值: %r ≠ 现读=%r" % (ref, br.get("board_value"), d["board_value"]))
        if br.get("netlist_value") != d["netlist_value"]:
            d2.append("%s 机器块网表侧值: %r ≠ 现读=%r" % (ref, br.get("netlist_value"), d["netlist_value"]))
    if block.get("board_md5") and block["board_md5"] != live["fp_before"]["md5"]:
        d2.append("机器块 board_md5=%s ≠ 现读=%s" % (block["board_md5"], live["fp_before"]["md5"]))
    if block.get("netlist_md5") and block["netlist_md5"] != live["netlist_md5"]:
        d2.append("机器块 netlist_md5 ≠ 现读")
    if block.get("bom_md5") and block["bom_md5"] != live["bom_md5"]:
        d2.append("机器块 bom_md5 ≠ 现读")
    if d2:
        fails["D2"] = "; ".join(d2)

    # ---- D3: 证据等级白名单 (★每行都要带★)
    d3 = []
    for ref, t in page["table_rows"].items():
        if t["evidence_level"] not in EVIDENCE_WHITELIST:
            d3.append("%s 台账证据等级=%r 不在白名单 %s" % (ref, t["evidence_level"], list(EVIDENCE_WHITELIST)))
    for br in brows:
        lv = br.get("evidence_level")
        if lv not in EVIDENCE_WHITELIST:
            d3.append("%s 机器块证据等级=%r 不在白名单 %s" % (br.get("ref"), lv, list(EVIDENCE_WHITELIST)))
    if d3:
        fails["D3"] = "; ".join(d3)

    # ---- D4: `C_VBUS_GND` 机理 (★三处存在性 + 掉板机理 + 与现读一致★)
    d4 = []
    sec3 = page["sections"].get("3", "")
    for k in D4_KEYS:
        if k not in sec3:
            d4.append("§3 缺关键词 %r" % k)
    cvb = block.get("cvbus_gnd") or {}
    for k in D4_BLOCK_KEYS:
        if k not in cvb:
            d4.append("机器块 cvbus_gnd 缺字段 %r" % k)
    if cvb:
        if bool(cvb.get("in_netlist")) is not True:
            d4.append("机器块 cvbus_gnd.in_netlist 与现读不符 (现读: 在网表里)")
        if cvb.get("netlist_board_col") != "CHG_BOARD":
            d4.append("机器块 cvbus_gnd.netlist_board_col=%r ≠ 现读 CHG_BOARD"
                      % cvb.get("netlist_board_col"))
        if bool(cvb.get("on_board")) is not True:
            d4.append("机器块 cvbus_gnd.on_board 与现读不符 (现读: 板上有实物封装)")
        if cvb.get("evidence_level") not in EVIDENCE_WHITELIST:
            d4.append("机器块 cvbus_gnd.evidence_level 越界")
    if "C_VBUS_GND" not in live_drops:
        d4.append("现读: 板上【没有】C_VBUS_GND ⇒ 本页的掉板结论已过期")
    if d4:
        fails["D4"] = "; ".join(d4)

    # ---- D5: 三条路线代价账齐 (★甲/乙/丙 + 代价 + 谁拍★)
    d5 = []
    routes = block.get("routes") or {}
    for k in D5_ROUTES:
        if k not in routes or not str(routes.get(k) or "").strip():
            d5.append("机器块 routes 缺 %s" % k)
        else:
            txt = str(routes[k])
            if "代价" not in txt:
                d5.append("routes.%s 缺『代价』" % k)
            if "谁拍" not in txt:
                d5.append("routes.%s 缺『谁拍』" % k)
    sec4 = page["sections"].get("4", "")
    for w in D5_ROUTE_WORDS:
        if w not in sec4:
            d5.append("§4 缺 %s" % w)
    if d5:
        fails["D5"] = "; ".join(d5)

    # ---- D6: 零代拍 (★页里不许出现替 main / 老板拍板的措辞★)
    d6 = []
    if page_text:
        for bad in D6_FORBIDDEN:
            if bad in page_text:
                d6.append("出现代拍措辞 %r" % bad)
    if d6:
        fails["D6"] = "; ".join(d6)

    # ---- D7: 零外发 + 零挂链 + 零写板自证
    d7 = []
    self_src = opts.get("self_source")
    if self_src is None:
        try:
            with open(os.path.abspath(__file__), encoding="utf-8") as f:
                self_src = f.read()
        except Exception:
            self_src = ""
    for tok in D7_BANNED_TOKENS:
        if tok in self_src:
            d7.append("闸自身源码引用了禁止路径 %r" % tok)
    gc = opts.get("gate_check_text")
    if gc is None:
        try:
            with open(GATE_CHECK, encoding="utf-8") as f:
                gc = f.read()
        except Exception:
            gc = ""
    if GATE_NAME in gc:
        d7.append("state/gate_check.py 里出现了本闸名 ⇒ 已挂链 (★本闸要求零挂链★)")
    fp_after = opts.get("fp_after") or file_fp(BOARD)
    if live["fp_before"]["md5"] != fp_after["md5"]:
        d7.append("板 md5 运行前后不一致: %s → %s" % (live["fp_before"]["md5"], fp_after["md5"]))
    if live["fp_before"]["mtime"] != fp_after["mtime"]:
        d7.append("板 mtime 运行前后不一致")
    if live["fp_before"]["size"] != fp_after["size"]:
        d7.append("板 size 运行前后不一致")
    if d7:
        fails["D7"] = "; ".join(d7)

    return fails, page


# ============================================================ 自测
def _mutate_drop_row(page_text, ref):
    """★把某一条从 §2 表与机器块里同时删掉 (⇒ D1 红)★"""
    lines = page_text.splitlines()
    out = []
    skip = False
    for ln in lines:
        m = re.match(r"^\|\s*\d+\s*\|", ln)
        if m:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[1].strip("`") == ref:
                skip = True
                continue
        if skip:
            if ln.strip().startswith("-") or ln.strip() == "":
                pass
            skip = False
        out.append(ln)
    txt = "\n".join(out)
    # 机器块: 删掉该 ref 的 8 行
    blocks = re.findall(r"```yaml\s*\n(.*?)\n```", txt, re.S)
    if blocks:
        ylines = blocks[0].splitlines()
        res, i = [], 0
        while i < len(ylines):
            ln = ylines[i]
            if ln.strip().startswith("- ref:") and ('"%s"' % ref) in ln:
                i += 1
                while i < len(ylines) and ylines[i].startswith("      "):
                    i += 1
                continue
            res.append(ln)
            i += 1
        newblk = "\n".join(res)
        newblk = re.sub(r"(?m)^  row_count: \d+$", "  row_count: %d" % len(
            [l for l in res if l.strip().startswith("- ref:")]), newblk)
        txt = txt.replace(blocks[0], newblk)
    return txt


def _mutate_block_value(page_text, ref, field, newval):
    """★改机器块某行的某个值 (⇒ D2 红)★"""
    m = re.search(r"```yaml\s*\n(.*?)\n```", page_text, re.S)
    if not m:
        return page_text
    y = m.group(1)
    pat = re.compile(r"(- ref: \"%s\"\n(?:      .*\n)*?      %s: )\"(?:[^\"]*)\"" % (re.escape(ref), field))
    if not pat.search(y):
        return page_text
    y2 = pat.sub(lambda mm: mm.group(1) + '"%s"' % newval, y, count=1)
    return page_text[:m.start(1)] + y2 + page_text[m.end(1):]


def _mutate_evidence(page_text, ref, newval):
    """★改台账某行的证据等级 (⇒ D3 红)★"""
    lines = page_text.splitlines()
    for i, ln in enumerate(lines):
        if re.match(r"^\|\s*\d+\s*\|", ln):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 9 and cells[1].strip("`") == ref:
                cells[8] = newval
                lines[i] = "| " + " | ".join(cells) + " |"
                break
    return "\n".join(lines)


def _mutate_drop_cvbus(page_text):
    m = re.search(r"```yaml\s*\n(.*?)\n```", page_text, re.S)
    if not m:
        return page_text
    y = m.group(1)
    lines = y.splitlines()
    res, i = [], 0
    while i < len(lines):
        if lines[i].strip() == "cvbus_gnd:":
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                i += 1
            continue
        res.append(lines[i])
        i += 1
    y2 = "\n".join(res)
    return page_text[:m.start(1)] + y2 + page_text[m.end(1):]


def _mutate_drop_route(page_text, key):
    m = re.search(r"```yaml\s*\n(.*?)\n```", page_text, re.S)
    if not m:
        return page_text
    y = m.group(1)
    lines = y.splitlines()
    res = []
    for ln in lines:
        if ln.strip().startswith("%s:" % key) and ln.startswith("    "):
            continue
        res.append(ln)
    y2 = "\n".join(res)
    return page_text[:m.start(1)] + y2 + page_text[m.end(1):]


def _mutate_forbid(page_text, phrase):
    return page_text + "\n\n★自测注入: %s★\n" % phrase


def run_selftest(live, page_text):
    """★自测: 正向 ≥1 + 反向 ≥6, 每条反向用例自证「红的是目标那一条、其余仍绿」★"""
    os.makedirs(SANDBOX, exist_ok=True)
    cases = []          # (名字, kind, 期望红集合, 实际红集合, 说明)
    base_fails, _ = evaluate(page_text, live)
    cases.append(("正向·当前真相页全绿", "pos", set(), set(base_fails),
                  "基线: D1~D7 全绿 (页齐 + 机器块齐 + 无代拍 + 零挂链)"))

    drift_refs = sorted(live["drift"])
    if not drift_refs:
        print("FATAL: 实测无差异行 ⇒ 自测无夹具")
        return 2
    pick = drift_refs[0]
    pick2 = drift_refs[-1]

    # 反向 1 · D1 (少登记一条)
    p1 = _mutate_drop_row(page_text, pick)
    f1, _ = evaluate(p1, live)
    cases.append(("反向1·D1·少登记一条 (%s)" % pick, "rev", {"D1"}, set(f1),
                  "台账漏登一条 ⇒ 必须只红 D1"))

    # 反向 2 · D2 (登记值被抄旧)
    p2 = _mutate_block_value(page_text, pick2, "board_value", "★台账过期★")
    f2, _ = evaluate(p2, live)
    cases.append(("反向2·D2·台账值过期 (%s)" % pick2, "rev", {"D2"}, set(f2),
                  "登记值 ≠ 现读值 ⇒ 必须只红 D2"))

    # 反向 3 · D3 (证据等级越界)
    p3 = _mutate_evidence(page_text, pick, "[官方]")
    f3, _ = evaluate(p3, live)
    cases.append(("反向3·D3·证据等级越界 (%s)" % pick, "rev", {"D3"}, set(f3),
                  "[官方] 不在五级白名单 ⇒ 必须只红 D3"))

    # 反向 4 · D4 (机理块缺)
    p4 = _mutate_drop_cvbus(page_text)
    f4, _ = evaluate(p4, live)
    cases.append(("反向4·D4·cvbus_gnd 机理块缺", "rev", {"D4"}, set(f4),
                  "机器块缺 cvbus_gnd ⇒ 必须只红 D4"))

    # 反向 5 · D5 (路线缺一条)
    p5 = _mutate_drop_route(page_text, "B")
    f5, _ = evaluate(p5, live)
    cases.append(("反向5·D5·路线乙缺", "rev", {"D5"}, set(f5),
                  "routes 少一条 ⇒ 必须只红 D5"))

    # 反向 6 · D6 (出现代拍措辞)
    p6 = _mutate_forbid(page_text, "已决定")
    f6, _ = evaluate(p6, live)
    cases.append(("反向6·D6·出现代拍措辞", "rev", {"D6"}, set(f6),
                  "『已决定』⇒ 必须只红 D6"))

    # 反向 7 · D7 (已挂链) —— ★用沙盒副本, 不许碰真 state/gate_check.py★
    gc_copy = os.path.join(SANDBOX, "gate_check_linked_copy.py")
    shutil.copy2(GATE_CHECK, gc_copy)          # ★copy2, 不是硬链接 (★L-24★)
    with open(gc_copy, "a", encoding="utf-8") as f:
        f.write("\n# ★自测注入: %s★\n" % GATE_NAME)
    with open(gc_copy, encoding="utf-8") as f:
        gc_text = f.read()
    f7, _ = evaluate(page_text, live, {"gate_check_text": gc_text})
    cases.append(("反向7·D7·已挂链 (沙盒副本)", "rev", {"D7"}, set(f7),
                  "沙盒副本里出现本闸名 ⇒ 必须只红 D7"))

    # 反向 8 · D7 (板被写过)
    fp_bad = dict(live["fp_before"])
    fp_bad["md5"] = "0" * 32
    f8, _ = evaluate(page_text, live, {"fp_after": fp_bad})
    cases.append(("反向8·D7·板指纹前后不一致", "rev", {"D7"}, set(f8),
                  "板 md5 前后不一致 ⇒ 必须只红 D7"))

    # 反向 9 · D1 (整页没了) —— ★fail-closed 命门★
    f9, _ = evaluate("", live)
    cases.append(("反向9·D1~D6·真相页缺失 (fail-closed)", "rev",
                  {"D1", "D2", "D3", "D4", "D5", "D6"}, set(f9),
                  "真相页不在 ⇒ D1~D6 必红 (D7 仍绿)"))

    # ---- 判定 ----
    ok = True
    print("=" * 74)
    print("★--selftest: 正向 ≥1 + 反向 ≥6 (★每条反向用例自证「红的是目标那一条、其余仍绿」★)")
    print("=" * 74)
    for name, kind, want, got, note in cases:
        if kind == "pos":
            good = (got == set())
            print("%s %-46s 期望红=∅  实际红=%s" % ("✔" if good else "✘", name, sorted(got) or "∅"))
        else:
            good = (got == want)
            extra = got - want
            missing = want - got
            print("%s %-46s 期望红=%s  实际红=%s%s" % (
                "✔" if good else "✘", name, sorted(want), sorted(got),
                "" if good else ("  ★多红=%s 少红=%s★" % (sorted(extra), sorted(missing)))))
            if extra:
                ok = False
        if not good:
            ok = False
        print("      └─ %s" % note)
    print("-" * 74)
    n_pos = sum(1 for c in cases if c[1] == "pos")
    n_rev = sum(1 for c in cases if c[1] == "rev")
    print("用例: 正向 %d 条 + 反向 %d 条 (合计 %d)" % (n_pos, n_rev, len(cases)))
    if n_pos < 1 or n_rev < 6:
        print("✘ 用例数不达标 (要求 正向≥1 反向≥6)")
        ok = False
    if not ok:
        print("✘ SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS")
    return 0


# ============================================================ main
def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--truth-page", default=TRUTH_PAGE)
    args = ap.parse_args()

    live = collect_live()
    page_text = read_page(args.truth_page)

    if args.selftest:
        rc = run_selftest(live, page_text)
        return rc

    fails, _ = evaluate(page_text, live)
    print("=" * 74)
    print("check_generator_value_drift_closed · ISS-402 · 「板那一趟」生成器重跑 Value 漂移 + C_VBUS_GND 掉板")
    print("=" * 74)
    print("真相页      : %s (%s)" % (args.truth_page, "存在" if page_text else "★缺失★"))
    print("实测差异条数: %d   实测掉板件数: %d   板面封装数: %d"
          % (len(live["drift"]), len(live["drops"]), len(live["board"])))
    print("板三项指纹  : md5=%s size=%d mtime=%d"
          % (live["fp_before"]["md5"], live["fp_before"]["size"], live["fp_before"]["mtime"]))
    print("-" * 74)
    order = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")
    names = {
        "D1": "fail-closed 命门: 每条实测差异都必须登记 (不许豁免)",
        "D2": "台账登记值 == 现读值 (不许抄旧值)",
        "D3": "证据等级白名单 (五级)",
        "D4": "C_VBUS_GND 机理 (三处存在性 + 掉板机理)",
        "D5": "三条路线 (甲/乙/丙) 代价账齐",
        "D6": "零代拍",
        "D7": "零外发 + 零挂链 + 零写板自证",
    }
    for code in order:
        if code in fails:
            print("❌ %s  %s" % (code, names[code]))
            for part in fails[code].split("; "):
                print("      · %s" % part)
        else:
            print("✅ %s  %s" % (code, names[code]))
    print("-" * 74)
    if fails:
        print("❌ rc=1: 有 %d 条判据红 (★fail-closed★)" % len(fails))
        return 1
    print("✅ rc=0: D1~D7 全绿 (★26 处已逐条登记 · 机理在页 · 三条路线齐 · 零代拍·零挂链·零写板★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
