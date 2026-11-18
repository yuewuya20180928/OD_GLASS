#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/check_step1_parts_spec.py — ISS-237 「P2 屏口径收死」机器门禁

单号: ISS-237 (2026-11-16) · owner: hw-lead · verify_by: main

★为什么有这个门禁★
  HW/STEP1_PARTS_SPEC.md 的 §0/§3 一度写着 "display 座 = 40p/0.5mm + 背光 12V BOOST",
  而现行网表/脚表/板/BOM 全部落在 22p/0.5mm 且没有 BOOST 那一路
  ⇒ 照文档画板 = 投板前返工 (2-4 周 + ¥4-8K/批)。
  ⇒ 本门禁把「display 座口径」收成单一事实源: 文档口径 / 网表脚数 / 背光 BOOST 有无
    三者必须互相对得上, 且 §7 对账表必须逐行可判。

用法:
  python3 HW/check_step1_parts_spec.py            # 全过 => rc=0; 任一条不过 => rc=1 并点名
  python3 HW/check_step1_parts_spec.py --selftest # 反向用例 => 全抓到 rc=0
  python3 HW/check_step1_parts_spec.py --root DIR # 换根目录 (自测用沙盒副本)

★只读★: 本脚本一个字节都不改被检查的文件; --selftest 只在临时目录的副本上做突变。
★受保护 (本脚本只读, 绝不写)*: HW/netlist_v1.csv · HW/netlist_v1_pins.csv ·
HW/BOM_v1.csv · HW/PCB/demo_mainboard.kicad_pcb · HW/PCB/FPC_PIN_TABLES.md ·
HW/PCB/PI5_DSI_22P_PINOUT.md
"""

import argparse
import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------- 常量

REL_SPEC = "HW/STEP1_PARTS_SPEC.md"
REL_REG = "HW/PART_ALTERNATIVES_REGISTRY.md"
REL_NETLIST = "HW/netlist_v1.csv"
REL_PINS = "HW/netlist_v1_pins.csv"
REL_FPCT = "HW/PCB/FPC_PIN_TABLES.md"

# 判定词: 只许这四个 (C5 逐行校验)
JUDGE_WORDS = ("已落表", "待落表", "已作废", "待老板拍")
# 落表批次: 只许这三种 (C5 逐行校验)
BATCH_WORDS = ("V-2/V-3/V-4 同批", "板那一趟", "不落")

# 作废标记: 一行里出现它 ⇒ 该行的旧口径已作废 (C2/C4 用)
VOID_RE = re.compile(r"作废")
ISS_KEY = "ISS-237"

# 遗留针数 (现行主板侧 display 座 = 裁定针数, 屏侧 = 15p; 40/39/24/20 是 ISS-158 旧稿)
LEGACY_COUNTS = ("40", "39", "24", "20")

# display 上下文词: 只有带这些词的行才算「display 座口径声明」
# (否则 §4 的 SoM「40pin 排针」会被误判 —— 那是 SoM 侧, 跟屏座无关)
DISPLAY_CTX = ("屏", "display", "DSI", "FPC", "LCD", "座", "模组", "panel", "模块", "触摸")

# 任一 2 位数 + p/针/pin ⇒ "针数声明"
COUNT_RE = re.compile(r"(?<!\d)(\d{2})\s*(?:p\b|针|pin\b)")
# 遗留针数的声明 (大小写敏感: "40P0.5" 这种原厂排线规格不算口径声明)
LEGACY_RE = re.compile(r"(?<!\d)(?:40|39|24|20)\s*(?:p\b|针|pin\b)")
# 12V 背光 / BOOST 的声明 (只看「背光」语境, 免得把「USB/电池升压到 5V」误判成背光链)
BL_CTX = re.compile(r"背光|BOOST|BL_|背照")
BL_REQ = re.compile(r"12\s*V|BOOST|升压")
# 否定词: 说了"不做/没有/0 行"的不算"要求主板加这一路"
NEGATION_RE = re.compile(r"不做|没有|不存在|不落|不作|无独立|无\s*12|0\s*行|已删|作废|不加|不装|=\s*无|无背光|无 12|无独立背光")


# ---------------------------------------------------------------- 工具

def read_text(root, rel):
    p = Path(root) / rel
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def md5(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def split_md_row(line):
    """按 markdown 表格切列, 支持 \\| 转义."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells, cur, i = [], [], 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def section(text, start_re, end_re):
    """取从 start_re 到 end_re 之间的正文 (不含 end)."""
    m = re.search(start_re, text, re.M)
    if not m:
        return ""
    rest = text[m.start():]
    m2 = re.search(end_re, rest[len(m.group(0)):], re.M)
    return rest[: len(m.group(0)) + (m2.start() if m2 else len(rest))]


def is_voided(line):
    return bool(VOID_RE.search(line))


def _heading_voided_map(lines):
    """逐行给出「有效作废状态」: 本行带作废标记, 或任一祖先标题带作废标记 (整节已作废).

    ★用标题栈 (而不是只看最近的标题) —— 否则 §3 (整节已作废) 下面的 §3.5 (标题本身没标)
    会把作废状态冲掉。
    """
    out = []
    stack = {}
    for ln in lines:
        m = re.match(r"^\s*(#{1,6})\s", ln)
        if m:
            lvl = len(m.group(1))
            for k in [k for k in stack if k >= lvl]:
                del stack[k]
            stack[lvl] = bool(VOID_RE.search(ln))
        out.append(is_voided(ln) or any(stack.values()))
    return out


# ---------------------------------------------------------------- 裁定块解析

RULING_KEYS = {
    "ISS": re.compile(r"ISS=(ISS-\d+)"),
    "RULING": re.compile(r"RULING=([A-Za-z])"),
    "SCREEN": re.compile(r"SCREEN=([^`]+)"),
    "PIN_COUNT": re.compile(r"PIN_COUNT=(\d+)"),
    "PITCH": re.compile(r"PITCH=([0-9.]+mm)"),
    "CONN": re.compile(r"CONN=([A-Za-z0-9\-./()]+)"),
    "BOOST": re.compile(r"BOOST=(有|无)"),
    "DATE": re.compile(r"DATE=(\d{4}-\d{2}-\d{2})"),
}


def parse_ruling(spec_text):
    """从 §0 裁定横幅里抽裁定块. 返回 (dict, errors)."""
    errors = []
    if spec_text is None:
        return {}, ["STEP1_PARTS_SPEC.md 不存在"]
    # 裁定块必须落在 §0 (第一段) 里
    sec0 = section(spec_text, r"^##\s*0\.", r"^##\s*1\.")
    block = ""
    for line in sec0.splitlines():
        if "裁定块" in line:
            block += line + "\n"
        elif block and re.search(r"PIN_COUNT=", line):
            block += line + "\n"
    if not block:
        return {}, ["§0 里找不到「裁定块」"]
    ruling = {}
    for key, rx in RULING_KEYS.items():
        hits = rx.findall(block)
        if not hits:
            errors.append("裁定块缺字段 %s" % key)
            continue
        if len(set(hits)) > 1:
            errors.append("裁定块字段 %s 出现多个值: %s" % (key, sorted(set(hits))))
        ruling[key] = hits[0].strip()
    return ruling, errors


# ---------------------------------------------------------------- 各条检查

def check_c1_ruling_block(root, ruling):
    """C1: 裁定块存在 + 字段齐全 + 唯一 + 落在 §0 顶部."""
    errs = []
    for k in ("ISS", "RULING", "SCREEN", "PIN_COUNT", "PITCH", "CONN", "BOOST", "DATE"):
        if k not in ruling:
            errs.append("裁定块缺字段 %s" % k)
    if ruling.get("ISS") != ISS_KEY:
        errs.append("裁定块 ISS = %r, 应为 %r" % (ruling.get("ISS"), ISS_KEY))
    if ruling.get("RULING") not in ("A", "B"):
        errs.append("裁定块 RULING = %r, 应为 A 或 B" % ruling.get("RULING"))
    if ruling.get("BOOST") not in ("有", "无"):
        errs.append("裁定块 BOOST = %r, 应为 有/无" % ruling.get("BOOST"))
    if ruling.get("PIN_COUNT") and not ruling["PIN_COUNT"].isdigit():
        errs.append("裁定块 PIN_COUNT 不是数字: %r" % ruling["PIN_COUNT"])
    spec = read_text(root, REL_SPEC) or ""
    if spec:
        banner_pos = spec.find("P2 屏口径裁定")
        if banner_pos < 0:
            errs.append("§0 顶部找不到「P2 屏口径裁定」横幅")
        else:
            sec0 = section(spec, r"^##\s*0\.", r"^##\s*1\.")
            if "P2 屏口径裁定" not in sec0.split("\n")[2] if len(sec0.split("\n")) > 2 else True:
                pass
            # 横幅必须出现在 §0 的前 6 行内
            head = "\n".join(sec0.split("\n")[:6])
            if "P2 屏口径裁定" not in head:
                errs.append("裁定横幅不在 §0 顶部 (必须落在 §0 前 6 行内)")
    return errs


def _scope_lines(root):
    """C2/C4 的扫描范围: STEP1 全篇 + REGISTRY 的 §3 / §5.

    返回 (tag, line, effective_voided).
    """
    out = []
    spec = read_text(root, REL_SPEC)
    if spec:
        lines = spec.splitlines()
        flags = _heading_voided_map(lines)
        for i, (ln, v) in enumerate(zip(lines, flags), 1):
            out.append(("SPEC L%d" % i, ln, v))
    reg = read_text(root, REL_REG)
    if reg:
        for tag, body in (("REG §3", section(reg, r"^##\s*3\.", r"^##\s*4\.")),
                          ("REG §5", section(reg, r"^##\s*5\.", r"^##\s*6\."))):
            lines = body.splitlines()
            flags = _heading_voided_map(lines)
            for i, (ln, v) in enumerate(zip(lines, flags), 1):
                out.append(("%s +%d" % (tag, i), ln, v))
    return out


def check_c2_single_active_caliber(root, ruling):
    """C2: display 座的有效口径只有一种 —— 40p 与 22p 不许同时被标成现行/有效."""
    errs = []
    pin_count = ruling.get("PIN_COUNT")
    if not pin_count:
        return ["裁定块没有 PIN_COUNT, C2 无法判定"]

    allowed = {pin_count, "15", "31"}          # 现行: 主板座 = 裁定数, 屏侧 15p, camera 31p
    for tag, ln, void in _scope_lines(root):
        if not any(w in ln for w in DISPLAY_CTX):
            continue                              # 不是 display 座口径声明 (§4 的 SoM 排针等)
        legacy_hits = LEGACY_RE.findall(ln)
        if legacy_hits:
            if not void:
                errs.append("%s 提到遗留针数 %s 但没有「已作废」标记 ⇒ 两套口径仍并存: %s"
                            % (tag, "/".join(sorted(set(legacy_hits))), ln.strip()[:120]))
            continue
        if void:
            continue
        for cnt in COUNT_RE.findall(ln):
            if cnt not in allowed:
                errs.append("%s 的现行针数 %sp 不在裁定允许集 %s ⇒ 口径没收死: %s"
                            % (tag, cnt, sorted(allowed), ln.strip()[:120]))
    return errs


def check_c3_netlist_pins(root, ruling):
    """C3: 现行网表 CONN_LIGHT 的脚数 == 裁定后口径 (读脚表计数, 不许硬写)."""
    errs = []
    pin_count = ruling.get("PIN_COUNT")
    if not pin_count:
        return ["裁定块没有 PIN_COUNT, C3 无法判定"]
    want = int(pin_count)
    pins_txt = read_text(root, REL_PINS)
    if pins_txt is None:
        return ["%s 不存在" % REL_PINS]
    rows = list(csv.DictReader(pins_txt.splitlines()))
    cl = [r for r in rows if (r.get("ref") or "").strip() == "CONN_LIGHT"]
    got = len(cl)
    if got != want:
        errs.append("脚表 count(CONN_LIGHT) = %d, 裁定口径 = %d ⇒ 对不上" % (got, want))
    else:
        nums = sorted(int(m.group(1)) for r in cl
                      for m in [re.search(r"(\d+)", r.get("pin") or "")] if m)
        if nums != list(range(1, want + 1)):
            errs.append("CONN_LIGHT 脚号不是 1..%d 连续: %s" % (want, nums))
    # 座型必须与裁定的 CONN= 一致
    conn = ruling.get("CONN")
    net_txt = read_text(root, REL_NETLIST)
    if net_txt is None:
        errs.append("%s 不存在" % REL_NETLIST)
    elif conn:
        nrows = list(csv.reader(net_txt.splitlines()))
        hit = [r for r in nrows[1:] if len(r) > 4 and r[4].strip() == "CONN_LIGHT"]
        if not hit:
            errs.append("网表里没有 CONN_LIGHT 的器件行")
        else:
            blob = " ".join(",".join(r) for r in hit)
            if conn not in blob:
                errs.append("网表 CONN_LIGHT 行里找不到裁定的座型 %r" % conn)
    return errs


def check_c4_boost(root, ruling):
    """C4: 网表里 12V BOOST 那一路的存在/不存在, 必须与裁定一致; 文档侧也不许留现行要求."""
    errs = []
    boost = ruling.get("BOOST")
    if boost not in ("有", "无"):
        return ["裁定块 BOOST 缺值, C4 无法判定"]
    net_txt = read_text(root, REL_NETLIST)
    if net_txt is None:
        return ["%s 不存在" % REL_NETLIST]
    nrows = list(csv.reader(net_txt.splitlines()))
    hits = []
    for idx, r in enumerate(nrows[1:], 2):
        if len(r) < 6:
            continue
        # 只看机器字段 (net/node1/node2/ref/value), 不看 note (note 是说明文字)
        machine = " ".join(r[1:6])
        if re.search(r"(?<!\d)12\s*V|BOOST|BACKLIGHT|LED_(ANODE|CATHODE)|BL_(EN|PWM|A|K)", machine):
            hits.append("L%d: %s" % (idx, machine[:90]))
    if boost == "无" and hits:
        errs.append("裁定 BOOST=无, 但网表里有 %d 行 12V/BOOST 背光路: %s" % (len(hits), hits[:3]))
    if boost == "有" and not hits:
        errs.append("裁定 BOOST=有, 但网表里 12V/BOOST 背光路 0 行 ⇒ 裁定与网表对不上")
    # 文档侧: 不许留"主板要加一路 12V BOOST 背光"的现行要求
    for tag, ln, void in _scope_lines(root):
        if not BL_CTX.search(ln) or not BL_REQ.search(ln):
            continue
        if void or NEGATION_RE.search(ln):
            continue
        errs.append("%s 仍把 12V/BOOST 背光写成现行要求 (未标记作废/未否定): %s"
                    % (tag, ln.strip()[:120]))
    return errs


def _parse_table(text, section_start=r"^##\s*7\."):
    """取 §7 的第一张 markdown 表 ⇒ (header, rows)."""
    sec = section(text, section_start, r"^##\s*8\.")
    if not sec:
        return [], []
    header, rows = None, []
    for ln in sec.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            if header is not None:
                break
            continue
        cells = split_md_row(s)
        if header is None:
            header = cells
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return header or [], rows


def check_c5_reconciliation_table(root, ruling):
    """C5: §7 对账表齐全 + 每行判定非空 + 判定词只有那四个 + 证据具体 + 批次合法."""
    errs = []
    spec = read_text(root, REL_SPEC)
    if spec is None:
        return ["%s 不存在" % REL_SPEC]
    if not re.search(r"^##\s*7\.", spec, re.M):
        return ["STEP1_PARTS_SPEC.md 里没有 §7 对账表"]
    sec7 = section(spec, r"^##\s*7\.", r"^##\s*8\.")
    if "不止 M1~M11" not in sec7:
        errs.append("§7 表头未写清「本表是 §5 全部落成约束的对账, 不止 M1~M11」")
    header, rows = _parse_table(spec)
    if not header:
        return errs + ["§7 里解析不到对账表"]
    # 表头
    for need in ("条目号", "判定", "证据", "落表批次"):
        if not any(need in h for h in header):
            errs.append("§7 表头缺列「%s」" % need)
    try:
        i_id = next(i for i, h in enumerate(header) if "条目号" in h)
        i_jd = next(i for i, h in enumerate(header) if "判定" in h)
        i_ev = next(i for i, h in enumerate(header) if "证据" in h)
        i_bt = next(i for i, h in enumerate(header) if "落表批次" in h)
    except StopIteration:
        return errs + ["§7 表头列定位失败"]
    if not rows:
        return errs + ["§7 对账表 0 行数据"]

    seen_ids, non_m_rows = [], 0
    for r in rows:
        if len(r) <= max(i_id, i_jd, i_ev, i_bt):
            errs.append("§7 行列数不足: %s" % (r[:1],))
            continue
        item = r[i_id].strip()
        item_norm = item.replace("*", "").replace("`", "").strip()
        judge = r[i_jd].strip()
        ev = r[i_ev].strip()
        batch = r[i_bt].strip()
        if not item:
            errs.append("§7 有一行条目号为空")
            continue
        seen_ids.append(item_norm)
        if not re.match(r"^M\d+$", item_norm):
            non_m_rows += 1
        # 判定非空 + 只许四个词
        if not judge:
            errs.append("§7 条目 %s 的判定为空" % item)
        else:
            head = re.split(r"[\s(（]", judge)[0]
            if head not in JUDGE_WORDS:
                errs.append("§7 条目 %s 的判定「%s」不是允许的四个词之一 %s"
                            % (item, judge[:40], list(JUDGE_WORDS)))
        # 证据必须具体
        if not ev:
            errs.append("§7 条目 %s 的证据为空" % item)
        elif not re.search(r"L\d{1,4}|count\(", ev):
            if re.match(r"^(M\d+|§5)", item_norm):
                errs.append("§7 条目 %s 的证据没有具体行号/计数: %s" % (item, ev[:80]))
            elif not re.search(r"§\d", ev):
                errs.append("§7 条目 %s 的证据不够具体: %s" % (item, ev[:80]))
        # 批次
        if not batch:
            errs.append("§7 条目 %s 的落表批次为空" % item)
        elif not any(b in batch for b in BATCH_WORDS):
            errs.append("§7 条目 %s 的落表批次「%s」不在 %s" % (item, batch[:40], list(BATCH_WORDS)))
    # M1~M11 必须齐全
    for n in range(1, 12):
        key = "M%d" % n
        hit = [s for s in seen_ids if s == key]
        if not hit:
            errs.append("§7 对账表缺 %s 行" % key)
        elif len(hit) > 1:
            errs.append("§7 对账表 %s 出现 %d 次 (须一条一行)" % (key, len(hit)))
    if non_m_rows < 1:
        errs.append("§7 对账表没有 §5 里未编进 M1~M11 的其它落成约束行")
    return errs


def check_c6_fpctables(root, ruling):
    """C6: HW/PCB/FPC_PIN_TABLES.md 的 display 口径 == 裁定口径."""
    errs = []
    pin_count = ruling.get("PIN_COUNT")
    if not pin_count:
        return ["裁定块没有 PIN_COUNT, C6 无法判定"]
    txt = read_text(root, REL_FPCT)
    if txt is None:
        return ["%s 不存在" % REL_FPCT]
    m = re.search(r"^##\s*display:.*$", txt, re.M)
    if not m:
        return errs + ["FPC_PIN_TABLES.md 里找不到 ## display: 段"]
    head = m.group(0)
    side = re.search(r"板侧\s*(\d+)\s*p", head)
    if not side:
        errs.append("FPC_PIN_TABLES.md 的 display 段没写「板侧 Np」")
    elif side.group(1) != pin_count:
        errs.append("FPC_PIN_TABLES.md display 板侧 = %sp, 裁定口径 = %sp ⇒ 对不上"
                    % (side.group(1), pin_count))
    screen = (ruling.get("SCREEN") or "").split(" (")[0].strip()
    if screen and screen not in head:
        errs.append("FPC_PIN_TABLES.md 的 display 段不是裁定的屏「%s」" % screen)
    if VOID_RE.search(txt) is None:
        errs.append("FPC_PIN_TABLES.md 里没有 40p 表的「已作废」标记")
    return errs


def check_c7_m_set(root, ruling):
    """C7: §5 的 M 编号集合 == §7 覆盖的 M 编号集合."""
    errs = []
    spec = read_text(root, REL_SPEC)
    if spec is None:
        return ["%s 不存在" % REL_SPEC]
    sec5 = section(spec, r"^##\s*5\.", r"^##\s*6\.")
    m5 = set(re.findall(r"\*\*(M\d+)\*\*", sec5))
    if not m5:
        errs.append("§5 里解析不到 M1~M11 编号")
    header, rows = _parse_table(spec)
    m7 = set()
    try:
        i_id = next(i for i, h in enumerate(header) if "条目号" in h)
        for r in rows:
            if len(r) > i_id:
                m7 |= set(re.findall(r"\b(M\d+)\b", r[i_id]))
    except StopIteration:
        pass
    if m5 and m5 != m7:
        errs.append("§5 与 §7 的 M 编号集合不一致: §5-only=%s §7-only=%s"
                    % (sorted(m5 - m7), sorted(m7 - m5)))
    return errs


def check_c8_s1(root, ruling):
    """C8: §6 S1 必须存在, 且带 ISS-237 的确认语."""
    errs = []
    spec = read_text(root, REL_SPEC)
    if spec is None:
        return ["%s 不存在" % REL_SPEC]
    hit = [ln for ln in spec.splitlines() if ln.strip().startswith("| **S1** |")]
    if not hit:
        return ["§6 里找不到 S1 行 (被删了?)"]
    ln = hit[0]
    if ISS_KEY not in ln:
        errs.append("§6 S1 没有 ISS-237 确认语")
    if "确认为准" not in ln and "确认" not in ln:
        errs.append("§6 S1 没有「确认为准」语")
    return errs


CHECKS = [
    ("C1", "裁定块存在且字段齐全", check_c1_ruling_block),
    ("C2", "display 座只有一套有效口径 (40p/22p 不许并存)", check_c2_single_active_caliber),
    ("C3", "网表 CONN_LIGHT 脚数 == 裁定口径", check_c3_netlist_pins),
    ("C4", "12V/BOOST 背光路与裁定一致", check_c4_boost),
    ("C5", "§7 对账表齐全且每行可判", check_c5_reconciliation_table),
    ("C6", "FPC_PIN_TABLES.md 的 display 口径 == 裁定口径", check_c6_fpctables),
    ("C7", "§5 与 §7 的 M 编号集合一致", check_c7_m_set),
    ("C8", "§6 S1 存在且经 ISS-237 确认", check_c8_s1),
]


def run_checks(root, verbose=True):
    spec = read_text(root, REL_SPEC)
    ruling, rerr = parse_ruling(spec)
    results = []
    if rerr:
        results.append(("C1", False, rerr))
        # 裁定块都读不出来, 后面几条没法判 —— 直接返回
        if verbose:
            for cid, ok, errs in results:
                print("[FAIL] %s  %s" % (cid, "; ".join(errs)))
            print("[SKIP] 裁定块解析失败, C2~C8 无法判定")
        return results
    for cid, desc, fn in CHECKS:
        try:
            errs = fn(root, ruling)
        except Exception as e:                      # noqa: BLE001
            errs = ["检查器内部异常: %r" % (e,)]
        results.append((cid, not errs, errs))
        if verbose:
            if errs:
                for e in errs:
                    print("[FAIL] %s  %s" % (cid, e))
                print("       └ %s" % desc)
            else:
                print("[PASS] %s  %s" % (cid, desc))
    return results


# ---------------------------------------------------------------- 自测 (反向用例)

def _sandbox(root):
    """把被检查的文件拷到临时目录 (自测只动副本, 绝不动真文件)."""
    tmp = Path(tempfile.mkdtemp(prefix="iss237_selftest_"))
    for rel in (REL_SPEC, REL_REG, REL_NETLIST, REL_PINS, REL_FPCT):
        src = Path(root) / rel
        dst = tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return tmp


def _mutate(path, old, new, must_change=True):
    """把文件里的 old 换成 new; 必须真的改了 (否则用例是假用例)."""
    txt = Path(path).read_text(encoding="utf-8")
    if old not in txt:
        raise AssertionError("突变目标不存在: %r (文件 %s)" % (old[:80], path))
    Path(path).write_text(txt.replace(old, new, 1), encoding="utf-8")
    after = Path(path).read_text(encoding="utf-8")
    if must_change and after == txt:
        raise AssertionError("突变没改到东西 (假用例): %r" % old[:80])
    if must_change and old in after:
        raise AssertionError("突变后旧串还在 (假用例): %r" % old[:80])


def _find_line(path, prefix):
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if ln.strip().startswith(prefix):
            return ln
    raise AssertionError("找不到以 %r 开头的行 (文件 %s)" % (prefix, path))


def _drop_line(path, prefix):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    out = [ln for ln in lines if not ln.strip().startswith(prefix)]
    if len(out) == len(lines):
        raise AssertionError("没删到任何行 (假用例): %r" % prefix)
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")


def _run_in_sandbox(tmp):
    """在沙盒里跑一遍, 返回 (rc, stdout)."""
    script = Path(__file__).resolve()
    proc = subprocess.run([sys.executable, str(script), "--root", str(tmp)],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _mutate_p2_row_to_legacy(tmp):
    """把 §0 的 P2 行换回 ISS-237 之前的旧稿 (40p/0.5mm, 无作废标记).

    ★自证: 换完之后该行必须【不含】任何「作废」字样、且【含】40p —— 否则就是一条假用例。
    """
    path = tmp / REL_SPEC
    legacy = ("| **P2 屏模组** | ★**Radxa Display 8 HD** (800×1280) | "
              "★**40p / 0.5mm** FPC, **逐针针位表已拿到** (§3.1) · **4-lane DSI** · "
              "驱动 IC 走内核白名单 | ★**针位表 = 全 40 针原文** ✔ |")
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    hit = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("| **P2 屏模组** |") and "40p" in ln:
            lines[i] = legacy
            hit += 1
    if hit != 1:
        raise AssertionError("没定位到唯一的 §0 P2 行 (命中 %d 次)" % hit)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    # 自证: 突变确实把「旧稿口径」写成了现行
    now = [ln for ln in Path(path).read_text(encoding="utf-8").splitlines()
           if ln.strip().startswith("| **P2 屏模组** |")][0]
    if "作废" in now:
        raise AssertionError("突变后 P2 行仍带作废标记 ⇒ 这条用例抓不到真问题 (假用例)")
    if "40p" not in now:
        raise AssertionError("突变后 P2 行没有 40p ⇒ 突变无效 (假用例)")


CASES = [
    ("T1 改坏 §0 针数 (裁定块 PIN_COUNT 22→40)", "C3",
     lambda tmp: _mutate(tmp / REL_SPEC, "PIN_COUNT=22", "PIN_COUNT=40")),
    ("T2 §0 P2 行换回旧稿 (40p/0.5mm, 无作废标记)", "C2",
     _mutate_p2_row_to_legacy),
    ("T3 删掉 §6 的 S1 行", "C8",
     lambda tmp: _drop_line(tmp / REL_SPEC, "| **S1** |")),
    ("T4 改网表脚数 (脚表去掉一个 CONN_LIGHT 行)", "C3",
     lambda tmp: _drop_line(tmp / REL_PINS, "CONN_LIGHT.pin22")),
    ("T5 删一条对账判定 (M6 判定清空)", "C5",
     lambda tmp: _mutate(tmp / REL_SPEC,
                         "| **M6** | 屏背光单独一路 12V BOOST + 限流 (LED typ 12.8V / max 14V / 200mA typ) | 已作废 (依据 ISS-237:",
                         "| **M6** | 屏背光单独一路 12V BOOST + 限流 (LED typ 12.8V / max 14V / 200mA typ) |  |")),
    ("T6 把 M6 判定改成非法词 (基本已落)", "C5",
     lambda tmp: _mutate(tmp / REL_SPEC,
                         "| **M6** | 屏背光单独一路 12V BOOST + 限流 (LED typ 12.8V / max 14V / 200mA typ) | 已作废 (依据 ISS-237:",
                         "| **M6** | 屏背光单独一路 12V BOOST + 限流 (LED typ 12.8V / max 14V / 200mA typ) | 基本已落 |")),
    ("T7 删掉 §7 的 M7 行 (对账表缺一条)", "C5",
     lambda tmp: _drop_line(tmp / REL_SPEC, "| **M7** |")),
    ("T8 registry §3 把 40p 的作废标记去掉", "C2",
     lambda tmp: _mutate(tmp / REL_REG,
                         "★★**Radxa Display 8 HD / 10 FHD** (MIPI-DSI 一体屏模组) ★**P2 定案 ★已作废 (依据 ISS-237 2026-11-16)★**",
                         "★★**Radxa Display 8 HD / 10 FHD** (MIPI-DSI 一体屏模组) ★**P2 定案**")),
]


def run_selftest(root, verbose=True):
    ok = True
    # 先跑基线: 基线必须全过, 否则反向用例没意义
    base = run_checks(root, verbose=False)
    if not all(r[1] for r in base):
        ok = False
        print("[FAIL] selftest 基线就没过, 反向用例无意义:")
        for cid, _, errs in base:
            for e in errs:
                print("       %s: %s" % (cid, e))
        return ok, 0
    if verbose:
        print("[PASS] selftest 基线 (真盘) 全过")
    passed = 0
    for name, expect_cid, mut in CASES:
        tmp = _sandbox(root)
        try:
            mut(tmp)
            rc, out = _run_in_sandbox(tmp)
            caught = rc != 0 and expect_cid in out
            if caught:
                passed += 1
                if verbose:
                    print("[PASS] %s ⇒ rc=%d, 点名 %s" % (name, rc, expect_cid))
            else:
                ok = False
                if verbose:
                    print("[FAIL] %s ⇒ rc=%d (期望 rc=1 且点名 %s)" % (name, rc, expect_cid))
                    for ln in out.splitlines()[:12]:
                        print("       | %s" % ln)
        except AssertionError as e:
            ok = False
            if verbose:
                print("[FAIL] %s ⇒ 突变本身无效: %s" % (name, e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if verbose:
        print("---- selftest: %d/%d 用例抓到了 ----" % (passed, len(CASES)))
        if passed < 5:
            print("[FAIL] selftest 用例少于 5 个 (要求 >=5/5)")
            ok = False
    return ok, passed


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="ISS-237 P2 屏口径门禁")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
                    help="项目根目录 (默认 = 本脚本上两级)")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例")
    args = ap.parse_args()
    root = Path(args.root)

    if not (root / REL_SPEC).exists():
        print("[FAIL] 找不到 %s (root=%s)" % (REL_SPEC, root))
        return 1

    if args.selftest:
        ok, passed = run_selftest(root)
        print("SELFTEST %d/%d => %s" % (passed, len(CASES), "OK" if ok else "RED"))
        return 0 if ok else 1

    results = run_checks(root)
    npass = sum(1 for _, o, _ in results if o)
    print("---- %d/%d 通过 ⇒ rc=%d ----" % (npass, len(results), 0 if npass == len(results) else 1))
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
