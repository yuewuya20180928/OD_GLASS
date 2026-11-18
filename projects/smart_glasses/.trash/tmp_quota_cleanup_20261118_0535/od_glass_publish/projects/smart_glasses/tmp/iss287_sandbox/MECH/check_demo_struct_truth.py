#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_demo_struct_truth.py —— ISS-213 结构侧真值门禁 (demo 板当前成立的条目)
=================================================================================
★**它守的不是"54 项全绿", 是"demo 板当前成立的条目不许变红 + 那 6 条 PCB 类
不许被静默 + 板框真源/判据阈值不许被偷改 + ★真源不许被悄悄换掉★"** ★

★★ ISS-224 再基线 (2026-11-16, mech-lead) —— ★★从「钉死一组旧数」升级成「钉死真源 +
与落表台账对账」★★
  ① 背景: hw-lead 的 **ISS-220 落表 (2026-11-16 02:32)** 真改了网表/脚表 (md5
     `c78f9912…`→`13f59a43…` / `4814617e…`→`a600afae…`), 并把 `PIN-MISMATCH`
     (P9 页正文 21p vs 网表 22p) **真修好了** ⇒ 本闸的 3 组红灯 (G1 / G1b / G5b)
     是「**门禁读着旧数**」⇒ ★**门禁读旧数 = 假红/假绿** ⇒ 必须重锚。
  ② ★**但只改 md5 锚点 = 把门禁再废一次** ⇒ 所以新增 **C21**: ★**网表/脚表的 md5
     锚点 ↔ 落表台账 ↔ 盘上真源, 三方必须对得上** —— 锚点里的 md5 必须能在
     `HW/SCHEMATIC_LANDING_V1_LANDED.md` (ISS-220 落表记录) 或
     `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` 里查到【落表单号 + 文件名 + 新旧两个
     md5】, 否则红 ⇒ ★**"悄悄换真源"这条路被堵死** ★
  ③ 另加 **C22** (`PIN-MISMATCH` 独立复核: 自己从 P9 页正文 + 网表实读, 不看
     `hw_cross_review_check.py` 的判定) 与 **G8** (已修复的留痕必须在场: 删行 /
     删节 / 抹留痕都红) ⇒ ★**"悄悄抹掉一次真修复"这条路也被堵死** ★

★★ ISS-273 判决源改造 (2026-11-17, mech-lead) —— ★★把「判决源」从【域侧锚点副本】
  换成【落表台账的最新落表记录 (链头)】★★
  ① 背景: 网表/脚表的 md5 锚点 (域侧副本) 每次上游【合法】落表就当场过期 ⇒ 门禁红 ⇒
     人工开一条 dispatch 单 + 人工重锚 + 人工留痕 ⇒ ★**已跳 6 跳 (R-02~R-06)**★;
     ★**2026-11-17 05:0x 那一轮连派单前提都过期了 (ISS-253 的活早做完) ⇒ 纯浪费** ★
  ② ★**改后**: G5b / C21 直接读 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★只读★) 里该文件的
     【最新落表记录 = 链头】⇒ ★**合法落表不再红** (链头跟着盘上走) ★ ⇒ 域侧锚点副本
     `source_ledger.entries[]` ★**降级为历史留痕**★ (6 跳历史一条都不许删)
  ③ ★**判据语义一点没松** —— 「悄悄换真源」照样红: ★**盘上 md5 ≠ 台账链头 ⇒ 红** (R1) ·
     ★**台账里查不到该文件 ⇒ 红** (R3) · ★**落表单号缺失 / 与台账对不上 ⇒ 红** (R5) ·
     ★**板 / `.kicad_pro` md5 变 ⇒ 仍红且点名硬保护那一组** (R6)
  ④ ★**判「最新」靠【图】(改前 md5 → 改后 md5 的链) 不靠【行序】** ⇒ 台账行序被打乱也照样
     取最新那条 ⇒ ★**「取错记录造成假绿」这条路被堵死** (R4)
  ⑤ `--selftest` 反向用例 14 → ★**21**★ 条 (★老的 14 条一条没少、期望全不变★)

★**本闸的 16 条 FAIL 一条都不许消** —— 6 个 PCB 类 id 仍按老板 2026-11-11 10:07
  口径排队等原理图定稿 (排队是**正确状态**, 不是缺陷)。

判据来源 (全部只读, 一个字不改):
  · `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 的 `MECH_ANCHORS` yaml 块 (本单写死的口径)
  · `MECH/BOARD_GEOM_30MM.md` §1 (板框真源四数)
  · `MECH/service_port_check.py` / `MECH/hw_cross_review_check.py` (判据阈值, **只 import 读常量**)
  · `HW/netlist_v1.csv` (网表实读) · `HW/SCHEMATIC_V1.md` P9 页 (页正文实读)

用法:
    python3 MECH/check_demo_struct_truth.py               # rc=0 全过 / rc=2 有红
    python3 MECH/check_demo_struct_truth.py --selftest     # 反向用例: 改坏任一锚点必须变红
    python3 MECH/check_demo_struct_truth.py --json         # 机器可读输出

★**边界**: 本脚本 **只读** 任何文件; 不改 `MECH/hw_cross_review_check.py` /
  `MECH/service_port_check.py` / `MECH/hinge_usb_check.py` /
  `MECH/display_biosafety_v2_check.py` 的判据语义, 不改板框真源,
  不改判据阈值, 不碰 `HW/`, 不碰 `state/daily_check.py` (是否挂巡检由 main 裁)。
"""
from __future__ import annotations

import argparse
import copy
import csv
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TRIAGE = os.path.join(HERE, "HW_CROSS_REVIEW_TRIAGE.md")
BOARD_GEOM = os.path.join(HERE, "BOARD_GEOM_30MM.md")

# ★ 受保护文件 md5 (交卷前逐字节不变; 值来自任务书 + cavity_recalc_check.py 的 MD5_EXPECTED)
# ★★【ISS-224】网表 / 脚表**不在这里写死** —— 它们的 md5 真源是 §1 锚点的
#   `source_ledger.entries` (可与落表台账对账) ⇒ 这里只留 6 个"硬保护"文件。
MD5_EXPECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "MECH/hinge_usb_check.py": "3425bc141508de8a35f34c7cf7b803e8",
    # ★★【ISS-264 · H-1 重基线 · 2026-11-17】★★ service_port_check.py 的 md5 由
    #   `9b24bf985764880f0105aee677fba6a8` → `db58ff6a2afc28b8bf517e3c57c56bc1`
    #   (原因: ISS-264 迁了夹具基准常量 p2_y 7.50→15.00 / s2_y 12.50→20.00 到 30mm 板套 A 口径,
    #    并加了 7.4b/7.5b 口径钉死 + 8.1b 开口 Y 现值 + --selftest 反向用例 ⇒ 受保护脚本必须重基线)
    #   留痕: MECH/HW_CROSS_REVIEW_TRIAGE.md §3.1 **R-07** 行 (跳数/谁改的/单号/新旧 md5/复现命令)
    #   ★**判据逻辑 / 阈值 (CRIT 0.60 / cavity_req 4.50 / cav_v 38.00 / duct_v 6.00) 一个字节没动** ★
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
    "MECH/hw_cross_review_check.py": "e521387b87b0fcdf9f22d56f14199967",
    "MECH/display_biosafety_v2_check.py": "29c77fc3fc823048b1d96c9500d28dd7",
}

# ★★【ISS-224】"不许悄悄换真源"机制管的两个真源 (网表/脚表) —— 锚点必须覆盖这两个
LEDGER_REQUIRED = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv")

# ★ 6 个 PCB 类 id (排队等原理图定稿 —— 判定语义不许改, 只登记排队)
PCB_CLASS_IDS = ("STK-FANOUT", "PCB-X-GAP", "MRG-54P", "MRG-X-4", "MRG-X-3", "FRM-SUM")

# ★ 基准判定汇总 (★【ISS-224 再基线】PASS 14→15 / FAIL 17→16: 少的那条 = PIN-MISMATCH,
#   它被 ISS-220 真修好了 ⇒ 见 HW_CROSS_REVIEW_TRIAGE.md §2 第 05 行 + §3.1)
BASE_SUMMARY = dict(pass_=15, fail=16, cond=8, info=15, total=54)

# ★ demo 板当前成立且必须 PASS 的项 (从 triage §2 判定表里摘出来的 PASS 项)
DEMO_PASS_IDS = ("STK-cav_v_-触点", "STK-cav_v_-FP", "RAD-fpc_t", "RAD-fpc_t_2oz", "PCB-Y",
                 "MRG-14P", "TOPO-2", "C1 铰链区 V 向", "C2 铰链区 H 向",
                 "C3 镜脚电芯段 V 向", "C4 主 PCB 段 H 向", "C5 镜脚 L 向")

# ★★【ISS-224】P9 页旧口径标记 (出现 = 有人把 P9 页回退成 ISS-220 之前的样子)
P9_STALE_MARKERS = ("1×21p@0.5mm", "18p@0.5mm", "4 组跨铰链", "(10+4+18+21)×0.5")
# ★★【ISS-224】P9 页新口径标记 (必须出现 = d6 真的落了)
P9_NEW_MARKERS = ("1×22p@0.5mm", "31p@0.3mm", "1 组跨铰链")


# ====================================================================== 工具
def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: str, name: str):
    """只 import 读常量 (两个 check 脚本都是 `if __name__ == '__main__'` 保护的, 安全)。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_anchors(doc_text: str) -> dict:
    m = re.search(r"# BEGIN MECH_ANCHORS(.*?)# END MECH_ANCHORS", doc_text, re.S)
    if not m:
        raise SystemExit("[gate] 定性表里找不到 MECH_ANCHORS 块")
    import yaml
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict) or "anchors" not in data:
        raise SystemExit("[gate] MECH_ANCHORS 块格式不对")
    return data["anchors"]


def load_sources(root: str) -> dict:
    """从**只读**真源里独立读出判据/几何事实 (不读定性表的锚点)。"""
    sp = load_module(os.path.join(root, "MECH", "service_port_check.py"), "_sp_ref")
    hx = load_module(os.path.join(root, "MECH", "hw_cross_review_check.py"), "_hx_ref")
    bg = read_text(os.path.join(root, "MECH", "BOARD_GEOM_30MM.md"))
    sec1 = re.search(r"##\s*1\.\s*板框(.*?)(?=\n##\s)", bg, re.S)
    sec1 = sec1.group(1) if sec1 else ""
    facts = {
        "sp": dict(sp.BASE),
        "sp_crit": sp.CRIT,
        "sp_tol": dict(sp.TOL),
        "hx": dict(hx.BASE),
        "geom_sec1": sec1,
    }
    return facts


def normalize_item(item: str) -> str:
    """定性表里为了区分同名的两个实例加了后缀/括注, 归一化回脚本的原始项号。"""
    it = item.strip("`").strip()
    it = re.sub(r"\s*\(\d+\.\d+\)\s*$", "", it)     # STK-cav_v_-触点 (38.00) -> STK-cav_v_-触点
    if it.endswith("b"):                            # MRG-X-3b (深度上界 7.5 档) -> MRG-X-3
        it = it[:-1]
    return it


def parse_triage_rows(doc_text: str) -> list:
    """切出 §2 定性表, 逐行解出 (序号, 项号, 判定, 处置, 备注)。"""
    m = re.search(r"##\s*2\s*★\s*54 项逐条定性表(.*?)\n---\n\n##\s*3", doc_text, re.S)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        if not line.startswith("| **"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        num = cells[0].replace("*", "")
        item = cells[1].strip("`")
        verdict = cells[2]
        disp = cells[6].replace("*", "")
        note = cells[8] if len(cells) > 8 else ""
        rows.append(dict(num=num, item=item, base=normalize_item(item),
                         verdict=verdict, disp=disp, note=note))
    return rows


def parse_queue_rows(doc_text: str) -> dict:
    """切出 §4 排队表, 解出 {id: 恢复条件}。"""
    m = re.search(r"##\s*4\s*6 个 PCB 类 id 的排队表(.*?)\n---", doc_text, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        item = cells[0].strip("`")
        resume = cells[-1]
        out.setdefault(item, "")
        out[item] = out[item] + " " + resume
    return out


def parse_fixed_section(doc_text: str):
    """★【ISS-224】切出 §3.1「已修复 (留痕)」节 —— 一次真修复不许从账上消失。"""
    m = re.search(r"^##\s*3\.1[^\n]*已修复[^\n]*$", doc_text, re.M)
    if not m:
        return None
    nxt = re.search(r"^\s*---\s*$", doc_text[m.end():], re.M)
    body = doc_text[m.end(): m.end() + (nxt.start() if nxt else len(doc_text))]
    ids = []
    for line in body.splitlines():
        if line.startswith("| **"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                ids.append(cells[1].strip("`"))
    return {"ids": ids, "text": body}


def run_cross_review(root: str) -> dict:
    """实跑 hw_cross_review_check.py --json (只读, 不改它)。"""
    p = subprocess.run([sys.executable, os.path.join(root, "MECH", "hw_cross_review_check.py"),
                        "--json"], capture_output=True, text=True, cwd=root, timeout=300)
    txt = p.stdout
    i = txt.find('{\n  "results"')
    if i < 0:
        raise SystemExit("[gate] hw_cross_review_check.py --json 没吐 JSON:\n" + txt[-2000:])
    d = json.loads(txt[i:])
    return d


# ====================================================== 真源实读 (C22 用)
def netlist_pin_counts(path: str) -> dict:
    """从网表实读: 每个连接器实际占用的 pin 数 (mandatory + DNP)。"""
    rows = list(csv.reader(open(path, encoding="utf-8")))
    hdr = rows[0]
    i1, i2 = hdr.index("node1"), hdr.index("node2")
    u: dict[str, set] = {}
    for r in rows[1:]:
        if not r or len(r) < len(hdr):
            continue
        for cell in (r[i1], r[i2]):
            m = re.match(r"^(\w+)\s+pin(\d+)$", cell.strip())
            if not m:
                continue
            u.setdefault(m.group(1), set()).add(int(m.group(2)))
    return {k: len(v) for k, v in u.items()}


def extract_page(text: str, page: str) -> str:
    """切出 `## P9 ...` 这一页的正文。"""
    m = re.search(r"^##\s*" + page + r"[^\n]*$", text, re.M)
    if not m:
        return ""
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    return text[m.start(): m.end() + (nxt.start() if nxt else len(text))]


def declared_pins(p9_text: str) -> dict:
    """从 P9 页正文抽连接器的 pin 数声明 (划掉的连接器不算声明)。"""
    t = re.sub(r"~~.*?~~", "", p9_text, flags=re.S)
    out = {}
    for conn in ("J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"):
        vals = set()
        for m in re.finditer(re.escape(conn) + r"[^。\n]{0,40}?(\d+)\s*(?:×\s*(\d+)\s*)?p(?![A-Za-z0-9])", t):
            vals.add(int(m.group(2) or m.group(1)))
        out[conn] = sorted(vals)
    return out


def load_pin_truth(root: str) -> dict:
    """★【ISS-224】独立读出 (P9 页声明 vs 网表实际) —— 不看 hw_cross_review_check.py 的判定。"""
    net = netlist_pin_counts(os.path.join(root, "HW", "netlist_v1.csv"))
    sch = read_text(os.path.join(root, "HW", "SCHEMATIC_V1.md"))
    p9 = extract_page(sch, "P9")
    return {"net": net, "decl": declared_pins(p9), "p9": p9}


def load_ledger_records(root: str, anchors: dict) -> list:
    """把锚点里登记的落表台账位置逐个读出来 (支持 `*` 通配)。"""
    sl = anchors.get("source_ledger") or {}
    specs = sl.get("landing_records") or []
    recs = []
    for spec in specs:
        if not spec:
            continue
        p = os.path.join(root, spec)
        if os.path.isfile(p):
            recs.append((spec, read_text(p)))
            continue
        d = os.path.dirname(spec) or "."
        b = os.path.basename(spec)
        for hit in sorted(glob.glob(os.path.join(root, d, b))):
            recs.append((os.path.relpath(hit, root), read_text(hit)))
    return recs


def md5_seen(text: str, value: str) -> bool:
    """台账里是不是出现了这个 md5 (全文或 12 位前缀 —— 落表记录用的是前缀)。"""
    if not value:
        return False
    return value in text or value[:12] in text


# ====================================================================== 落表台账判决源 (ISS-273)
#  ★★【ISS-273 · 2026-11-17】★★ 判决源从【域侧锚点副本】换成【落表台账的最新记录 (链头)】:
#   · 台账 = HW/SCHEMATIC_LANDING_V1_LANDED.md (★只读: 台账本身一个字都不许改★)
#   · 记录 = 台账里该文件的【改前 md5 → 改后 md5】表格行 (行内第一个 md5 = 前驱, 最后一个 = 改后)
#   · 链头 = 「不是任何记录的改前 md5」的那个改后 md5 ⇒ ★**判最新靠图 (前驱→改后), 不靠行序**
#     ⇒ 台账行序被打乱也不影响判定 ⇒ 「取错记录造成假绿」这条路被堵死
LEDGER_CANON = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
LEDGER_MD_RE = re.compile(r"\b[0-9a-f]{32}\b|\b[0-9a-f]{12}\b")


def ledger_records(text: str, rel: str) -> list:
    """从落表台账文本里抽出 rel 的落表记录 ⇒ [{'prev','new','iss','sec','row'}] (★行序无关★)。"""
    out = []
    ctx_iss = None          # ★最近的带单号标题 ⇒ 批次单号 (行里没写单号时继承它)
    title = "(文首)"
    base = os.path.basename(rel)
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            title = s
            hit = re.findall(r"ISS-\d+", s)
            if hit:
                ctx_iss = hit[0]
            continue
        if not s.startswith("|"):
            continue
        if rel not in s and base not in s:
            continue
        tk = LEDGER_MD_RE.findall(s)
        if len(tk) < 2:
            continue            # ★只有一个 md5 ⇒ 不是「改前→改后」记录行
        row_iss = re.findall(r"ISS-\d+", s)
        out.append({"prev": tk[0][:12], "new": tk[-1][:12],
                    "iss": row_iss[0] if row_iss else ctx_iss,
                    "sec": title, "row": s[:140]})
    return out


def ledger_state(rel: str, text: str) -> dict:
    """算该受管真源在台账里的链头 / 链 / 产出单号表 (★取不准就返回 head=None ⇒ 判红★)。"""
    recs = ledger_records(text, rel)
    new_keys = {r["new"] for r in recs}
    prev_keys = {r["prev"] for r in recs}
    heads = sorted(new_keys - prev_keys)
    producer = {}
    for r in recs:
        producer.setdefault(r["new"], set())
        if r["iss"]:
            producer[r["new"]].add(r["iss"])
    why = ""
    head = None
    if not recs:
        why = "台账里一条记录都没有"
    elif not heads:
        why = "没有链头 (每条记录都是别人的前驱 ⇒ 台账不成链)"
    elif len(heads) > 1:
        why = f"链头不唯一 = {heads} (取不准 ⇒ 不许判绿)"
    else:
        head = heads[0]
    chain = []
    if head:
        by_new = {}
        for r in recs:
            by_new.setdefault(r["new"], []).append(r)
        cur, seen = head, {head}
        chain = [head]
        while True:
            rs = by_new.get(cur) or []
            if not rs:
                break                       # 链尾 (起源值, 没有产出记录)
            prevs = {r["prev"] for r in rs if r["prev"] != r["new"]}
            if len(prevs) != 1:
                why = why or f"链上 {cur} 的前驱不唯一 = {sorted(prevs)}"
                chain = []
                break
            p = prevs.pop()
            if p in seen:
                why = why or f"链成环 ({p})"
                chain = []
                break
            cur = p
            seen.add(cur)
            chain.append(cur)
    return {"records": recs, "head": head, "chain": chain,
            "producer": producer, "why": why,
            "head_iss": sorted(producer.get(head, set())) if head else [],
            "known": new_keys | prev_keys}


def ledger_canonical_text(root: str, anchors: dict, overrides: dict = None) -> tuple:
    """取判决源台账文本 (默认 HW/SCHEMATIC_LANDING_V1_LANDED.md, ★只读★) + 它的 spec 名。"""
    ov = overrides or {}
    sl = anchors.get("source_ledger") or {}
    specs = list(sl.get("landing_records") or [])
    spec = LEDGER_CANON
    if not (os.path.isfile(os.path.join(root, spec)) or spec in ov):
        for s in specs:
            if os.path.isfile(os.path.join(root, s)) or s in ov:
                spec = s
                break
    if spec in ov:
        return str(ov[spec]), spec
    p = os.path.join(root, spec)
    if os.path.isfile(p):
        return read_text(p), spec
    return "", spec


def synth_ledger(recs_by_file: dict, tag: str = "合成") -> str:
    """把抽出来的落表记录重排成一份【合成台账】(★反向用例专用: 专测「行序打乱仍取最新」★)。"""
    lines = [f"# {tag}落表台账 (★仅供反向用例★)", ""]
    for rel, recs in recs_by_file.items():
        for i, r in enumerate(recs):
            lines.append(f"| {tag} {i} | `{rel}` | `{r['prev']}` | `{r['new']}` | "
                         f"{r['iss'] or '★无单号★'} | 说明 |")
    return "\n".join(lines) + "\n"


# ====================================================================== 检查组
def run_checks(root: str, anchors: dict, facts: dict, xrev: dict,
               doc: str = None, pin_truth: dict = None,
               ledger_texts: dict = None, md5_override: dict = None) -> list:
    """返回 [(组号, 组名, ok, 明细)]。anchors/doc/pin_truth 可被 --selftest 篡改 ⇒ 反向用例。"""
    out = []
    A = anchors
    sp, hx = facts["sp"], facts["hx"]
    if doc is None:
        doc = read_text(os.path.join(root, "MECH", "HW_CROSS_REVIEW_TRIAGE.md"))
    if pin_truth is None:
        pin_truth = load_pin_truth(root)

    def g(code, name, ok, detail):
        out.append((code, name, bool(ok), detail))

    # ---------------- G1 不许把红灯调没 ----------------
    s = xrev["summary"]
    n_total = len(xrev["results"])
    g("G1", "不许把红灯调没 (FAIL 名单仍是 16 条)",
      s["pass"] == BASE_SUMMARY["pass_"] and s["fail"] == BASE_SUMMARY["fail"]
      and s["cond"] == BASE_SUMMARY["cond"] and s["info"] == BASE_SUMMARY["info"]
      and n_total == BASE_SUMMARY["total"],
      f"实测汇总 PASS {s['pass']} / FAIL {s['fail']} / 条件通过 {s['cond']} / "
      f"说明 {s['info']} (共 {n_total})")

    fail_ids = [r["id"] for r in xrev["results"] if r["verdict"] == "FAIL"]
    exp_fail = list(A.get("fail_expect", []))
    from collections import Counter
    same = Counter(fail_ids) == Counter(exp_fail)
    g("G1b", "FAIL 名单逐条对齐 (一条不许少/一条不许多)", same,
      f"实测 {len(fail_ids)} 条 vs 锚点 {len(exp_fail)} 条; 差集 "
      f"实测多={sorted((Counter(fail_ids)-Counter(exp_fail)).elements())} "
      f"锚点多={sorted((Counter(exp_fail)-Counter(fail_ids)).elements())}")

    # ---------------- G2 demo 板当前成立的条目全过 ----------------
    # G2-1 盖板内腔 (ISS-126 现口径)
    cavity = sp["h_outer_out"] - sp["h_pcb_face"]
    g("G2.1", "检修口盖板内腔 ≥ cavity_req (ISS-126 现口径)",
      cavity >= sp["cavity_req"] and abs(cavity - A["service_port"]["cavity_now"]) < 1e-9,
      f"内腔 = {sp['h_outer_out']} − {sp['h_pcb_face']} = {cavity:.2f}mm "
      f"vs 硬要求 {sp['cavity_req']:.2f} (余 {cavity - sp['cavity_req']:+.2f}); "
      f"锚点写 {A['service_port']['cavity_now']}")

    # G2-2 Type-C 开孔: 新口径两档在最坏公差下过判据, 两档现候选判不合格
    tc = A["typec_panel"]
    crit = A["thresholds"]["crit"]

    def worst_gap(op, body, tol):
        return (op - tol - body) / 2.0

    new_x = worst_gap(tc["new_opening_x"], tc["body_x"], tc["fdm_tol"])
    new_y = worst_gap(tc["new_opening_y"], tc["body_y"], tc["fdm_tol"])
    mt_x = worst_gap(tc["metal_opening_x"], tc["body_x"], 0.05)
    mt_y = worst_gap(tc["metal_opening_y"], tc["body_y"], 0.05)
    g("G2.2", "Type-C 新开孔口径最坏单边间隙 ≥ 判据 (FDM 直成型档)",
      new_x >= crit and new_y >= crit,
      f"{tc['new_opening_x']}×{tc['new_opening_y']} ⇒ 最坏 X {new_x:.2f} / Y {new_y:.2f} "
      f"vs 判据 {crit:.2f}")
    g("G2.3", "Type-C 金属/CNC 档最坏单边间隙 ≥ 判据 (±0.05)",
      mt_x >= crit and mt_y >= crit,
      f"{tc['metal_opening_x']}×{tc['metal_opening_y']} ⇒ 最坏 X {mt_x:.2f} / Y {mt_y:.2f} "
      f"vs 判据 {crit:.2f}")
    rej_bad = []
    for r in tc["rejected"]:
        gx = worst_gap(r["x"], tc["body_x"], tc["fdm_tol"])
        gy = worst_gap(r["y"], tc["body_y"], tc["fdm_tol"])
        rej_bad.append((r["name"], gx, gy))
    g("G2.4", "两档现候选 (打印包现试样) 判不合格 —— 证明'二选一'是假选择",
      all(gx < crit or gy < crit for _n, gx, gy in rej_bad),
      "; ".join(f"{n}: 最坏 X {gx:.2f} / Y {gy:.2f}" for n, gx, gy in rej_bad))

    # G2-5 端件温升口径 (buck) + P_max + 金属热路
    th = A["thermal"]
    dt = th["p_buck_w"] * th["r_conv_k_per_w"]
    surf = th["ambient_c"] + dt
    p_max = (th["surface_limit_c"] - th["ambient_c"]) / th["r_conv_k_per_w"]
    g("G2.5", "端件温升按 buck 口径 (Pin−Pout+DCR), 不用 MECH_BUDGET 的 0.8W 线性口径",
      abs(dt - 83.33) < 1.0 and abs(surf - 108.33) < 1.0,
      f"P={th['p_buck_w']:.2f}W × R={th['r_conv_k_per_w']:.2f} K/W ⇒ ΔT {dt:.1f}K ⇒ 表面 {surf:.1f}°C "
      f"(线性口径 {th['p_mech_linear_w']:.2f}W ⇒ ΔT {th['p_mech_linear_w']*th['r_conv_k_per_w']:.0f}K ⇒ "
      f"{th['ambient_c']+th['p_mech_linear_w']*th['r_conv_k_per_w']:.0f}°C)")
    g("G2.6", "60°C 判据 ⇒ 端件表面能吃下的最大耗散 P_max (现值必须超它 ⇒ 强制金属热路)",
      abs(p_max - th["p_max_w"]) < 0.01 and th["p_buck_w"] > p_max,
      f"P_max = ({th['surface_limit_c']:.0f}−{th['ambient_c']:.0f})/{th['r_conv_k_per_w']:.2f} "
      f"= {p_max:.3f}W; 现耗散 {th['p_buck_w']:.2f}W ⇒ 超 {th['p_buck_w']/p_max:.2f}× ⇒ 必须金属热路")
    g("G2.7", "散热路径必须是金属 (打印件 R 远大于铝)",
      th["r_print_k_per_w"] > 100 * th["r_alu_k_per_w"],
      f"打印件 {th['r_print_k_per_w']:.0f} K/W vs 铝 {th['r_alu_k_per_w']:.3f} K/W "
      f"(差 {th['r_print_k_per_w']/th['r_alu_k_per_w']:.0f}×) ⇒ 0.5W 打进去 "
      f"+{th['p_buck_w']*th['r_print_k_per_w']:.0f}K (打印件) vs "
      f"+{th['p_buck_w']*th['r_alu_k_per_w']:.2f}K (铝)")

    # G2-8 buck 功率守恒
    pw = A["power"]
    r37 = pw["eta"] * pw["v_bus"] / 3.70
    r42 = pw["eta"] * pw["v_bus"] / 4.20
    g("G2.8", "buck 功率守恒 ICHG/IIN = η·Vbus/Vbat (规格书的 0.822/0.933 是倒数)",
      abs(r37 - pw["ratio_370"]) < 5e-4 and abs(r42 - pw["ratio_420"]) < 5e-4,
      f"3.70V ⇒ {r37:.3f} (锚点 {pw['ratio_370']}) · 4.20V ⇒ {r42:.3f} (锚点 {pw['ratio_420']}); "
      f"规格书倒数 = {3.70/pw['v_bus']/pw['eta']:.3f} / {4.20/pw['v_bus']/pw['eta']:.3f}")

    # G2-9 demo 当前必须 PASS 的项
    by_id = {}
    for r in xrev["results"]:
        by_id.setdefault(r["id"], []).append(r["verdict"])
    bad_pass = [i for i in DEMO_PASS_IDS if not any(v == "PASS" for v in by_id.get(i, []))]
    g("G2.9", "demo 当前成立的 PASS 项 (公差链 C1~C5 / 径向 / 堆叠余量 / 合并 14P / 拓扑 B) 全过",
      not bad_pass, f"共 {len(DEMO_PASS_IDS)} 项, 不再 PASS 的 = {bad_pass or '无'}")

    # ---------------- G3 6 条 PCB 类已登记排队 (不许静默) ----------------
    q = parse_queue_rows(doc)
    missing = [i for i in PCB_CLASS_IDS if not q.get(i, "").strip()]
    in_anchor = [i for i in PCB_CLASS_IDS if i not in A.get("pcb_class_queued", [])]
    g("G3", "6 个 PCB 类 id 已登记排队且恢复条件非空 (不许静默丢弃)",
      not missing and not in_anchor,
      f"排队表缺恢复条件的 = {missing or '无'}; 锚点 pcb_class_queued 缺的 = {in_anchor or '无'}")
    # 排队的这 6 个 id 必须**仍然是 FAIL** (不许被"修绿")
    still_fail = [i for i in PCB_CLASS_IDS if "FAIL" not in by_id.get(i, [])]
    g("G3b", "排队的 PCB 类 id 在 hw_cross_review_check.py 里仍然是 FAIL (不许修绿)",
      not still_fail, f"不再是 FAIL 的 = {still_fail or '无'}")

    # ---------------- G4 板框真源四数不变 ----------------
    sec1 = facts["geom_sec1"]
    bg = A["board_geom"]
    four = [("板长 X", bg["board_len_x"], "60.00mm", "板长 X"),
            ("板宽 Y", bg["board_width_y"], "30.00mm", "板宽 Y"),
            ("板厚", bg["board_thickness"], "1.00mm", "板厚"),
            ("板重", bg["board_mass_g"], "3.33g", "板重")]
    miss4 = [n for n, v, tok, _lbl in four if tok not in sec1]
    mism4 = [f"{n}: 锚点 {v} vs 文档要求 {tok}" for n, v, tok, _lbl in four
             if abs(float(v) - float(tok.replace("mm", "").replace("g", ""))) > 1e-9]
    g("G4", "MECH/BOARD_GEOM_30MM.md §1 四数 (60.00/30.00/1.00/3.33g) 一个没被改",
      not miss4 and not mism4,
      f"§1 缺失项 = {miss4 or '无'}; 锚点与文档不一致 = {mism4 or '无'}")
    # 板框四数还要与 hw_cross_review_check.py / service_port_check.py 的口径一致
    g("G4b", "板框四数与两个 check 脚本的现行口径一致 (pcb_len/pcb_w/pcb_thk)",
      abs(hx["pcb_len"] - bg["board_len_x"]) < 1e-9
      and abs(hx["pcb_w"] - bg["board_width_y"]) < 1e-9
      and abs(sp["pcb_thk"] - bg["board_thickness"]) < 1e-9,
      f"脚本 pcb_len={hx['pcb_len']} / pcb_w={hx['pcb_w']} / pcb_thk={sp['pcb_thk']} "
      f"vs 锚点 {bg['board_len_x']}/{bg['board_width_y']}/{bg['board_thickness']}")

    # ---------------- G5 判据阈值一个没松 ----------------
    th_anchor = A["thresholds"]
    g("G5", "判据阈值未松: cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00",
      abs(sp["cavity_req"] - th_anchor["cavity_req"]) < 1e-9
      and abs(sp["cav_v"] - th_anchor["cav_v"]) < 1e-9
      and abs(sp["duct_v"] - th_anchor["duct_v"]) < 1e-9
      and abs(facts["sp_crit"] - th_anchor["crit"]) < 1e-9
      and abs(hx["judge"] - th_anchor["crit"]) < 1e-9
      and abs(hx["cav_v_now"] - th_anchor["cav_v"]) < 1e-9,
      f"service_port: cavity_req={sp['cavity_req']} cav_v={sp['cav_v']} duct_v={sp['duct_v']} "
      f"CRIT={facts['sp_crit']:.2f}; hw_cross_review: judge={hx['judge']} cav_v_now={hx['cav_v_now']}")

    # ---------------- G5b 受保护文件 md5 逐字节未变 ----------------
    # ★★【ISS-273 · 2026-11-17 · 判决源改造】★★
    #   ★【旧】网表/脚表 = 锚点 source_ledger (域侧副本) 里登记的 md5 ⇒ 上游每落一次表就红一次 (已跳 6 跳)
    #   ★【新】网表/脚表 = ★**落表台账 (HW/SCHEMATIC_LANDING_V1_LANDED.md) 的最新记录 (链头)**★
    #        ⇒ 合法落表不再红 (链头跟着盘上走) · 悄悄换真源照样红 (盘上 ≠ 链头)
    #   ★域侧锚点副本【降级】为「历史留痕」: 它的 md5 必须是台账链里的历史值 + 它的落表单号必须对得上
    #        ⇒ 锚点编造 (md5 不在链里 / 单号对不上) 仍红, 但【停在历史值】不再红 (R2 = 本单要达成的行为)
    #   ★6 个硬保护文件 (板/.kicad_pro + 4 个 check 脚本) 仍读脚本自己的 MD5_EXPECTED 字典 (一个字没动)
    ledger = A.get("source_ledger") or {}
    entries = list(ledger.get("entries") or [])
    ent_by_file = {str(e.get("file")): e for e in entries}

    def fmd5(rel):
        if md5_override and rel in md5_override:
            return str(md5_override[rel])
        return md5(os.path.join(root, rel))

    led_text, led_spec = ledger_canonical_text(root, A, ledger_texts)
    badmd5 = []
    for rel, want in MD5_EXPECTED.items():
        got = fmd5(rel)
        if got != want:
            badmd5.append(f"{rel}: {got} != {want}")
    led_state = {}
    for rel in LEDGER_REQUIRED:
        st = ledger_state(rel, led_text)
        led_state[rel] = st
        got = fmd5(rel)
        if not led_text:
            badmd5.append(f"{rel}: 落表台账读不到 ({led_spec})")
        elif not st["records"]:
            badmd5.append(f"{rel}: 落表台账里查不到任何记录 (台账查不到)")
        elif not st["head"]:
            badmd5.append(f"{rel}: 台账链头取不准 ({st['why']})")
        elif got[:12] != st["head"]:
            badmd5.append(f"{rel}: 盘上 md5 {got[:12]}… != 台账最新记录 {st['head']}… (真源被换了?)")
        # 域侧锚点副本: 历史留痕, 但不许胡说
        e = ent_by_file.get(rel)
        if not e:
            badmd5.append(f"{rel}: 锚点 source_ledger.entries 没登记 (历史留痕缺失)")
        else:
            am = str(e.get("md5") or "")[:12]
            aby = str(e.get("by") or "")
            if not am or am not in st["known"]:
                badmd5.append(f"{rel}: 锚点副本 md5 {am or '(空)'}… 台账链里查不到 (锚点胡说?)")
            elif aby not in st["producer"].get(am, set()):
                badmd5.append(f"{rel}: 锚点副本落表单号 {aby or '(空)'} 与台账对不上 "
                              f"(台账产出该 md5 的单号 = {sorted(st['producer'].get(am, []))})")
    g("G5b", "受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)",
      not badmd5,
      "; ".join(badmd5) if badmd5 else
      f"{len(MD5_EXPECTED)} 个硬保护文件 全部一致 + {len(LEDGER_REQUIRED)} 个台账管理真源 "
      f"= 台账最新记录 (链头: "
      + ", ".join(f"{r}={led_state[r]['head']}" for r in LEDGER_REQUIRED)
      + ") + 域侧锚点副本 = 历史留痕 (允许停在历史值)")

    # ---------------- C21 真源变更台账对账 (不许悄悄换真源) ----------------
    #  ★★【ISS-273】★★ 判决源 = 落表台账最新记录 (链头); 域侧锚点副本 = 历史留痕
    #   ① 台账里必须查得到该受管真源的落表记录 (查不到 ⇒ 红)
    #   ② 记录必须能算出【唯一链头】(取不准 ⇒ 红 ⇒ 不许假绿)
    #   ③ 链头必须带落表单号 (字段缺失 ⇒ 红)
    #   ④ 链必须连得起来 (断了 / 有记录不在链上 ⇒ 红)
    #   ⑤ 盘上真源 md5 必须 == 链头 (被换了 ⇒ 红)
    #   ⑥ 域侧锚点副本必须登记受管真源, 且它的 md5 / 落表单号必须在台账里对得上 (历史留痕不许胡说)
    problems = []
    for rel in LEDGER_REQUIRED:
        st = led_state.get(rel) or {}
        recs = st.get("records") or []
        head = st.get("head")
        if not recs:
            problems.append(f"{rel}: 落表台账 ({led_spec}) 里查不到任何记录 ⇒ 台账没记这次落表?")
            continue
        if not head:
            problems.append(f"{rel}: 台账最新记录取不准 ({st.get('why')}) ⇒ 取错记录可能假绿 ⇒ 判红")
            continue
        if not st.get("head_iss"):
            problems.append(f"{rel}: 台账最新记录 ({head}) 缺落表单号 (字段缺失)")
        if not st.get("chain"):
            problems.append(f"{rel}: 落表链断了 / 不唯一 ({st.get('why')})")
        else:
            orphan = sorted({r["new"] for r in recs} - set(st["chain"]))
            if orphan:
                problems.append(f"{rel}: 台账里有记录不在链上 = {orphan}")
        got = fmd5(rel)
        if got[:12] != head:
            problems.append(f"{rel}: 盘上 md5 {got[:12]} != 台账最新 {head} (真源被换了或台账没更新)")
        e = ent_by_file.get(rel)
        if not e:
            problems.append(f"锚点 source_ledger.entries 缺受管真源 = {rel}")
            continue
        am = str(e.get("md5") or "")[:12]
        aby = str(e.get("by") or "")
        if not am or am not in st["known"]:
            problems.append(f"{rel}: 锚点副本 md5 {am or '(空)'} 台账链里查不到 (锚点胡说?)")
        elif aby not in st["producer"].get(am, set()):
            problems.append(f"{rel}: 锚点副本落表单号 {aby or '(空)'} 与台账对不上 "
                            f"(台账记 {sorted(st['producer'].get(am, []))})")
    g("C21", "真源变更台账对账 (盘上真源 ↔ 落表台账最新记录 (链头) ↔ 域侧锚点历史副本)",
      not problems,
      "; ".join(problems) if problems else
      "台账最新记录 (链头) = "
      + ", ".join(f"{r} {led_state[r]['head']} (by {led_state[r]['head_iss']})" for r in LEDGER_REQUIRED)
      + "; 锚点副本 = 历史留痕 (允许停在历史值, 但不许与台账对不上)")

    # ---------------- C22 PIN-MISMATCH 独立复核 ----------------
    #  ★★【ISS-224 新增】★★ 不看 hw_cross_review_check.py 的判定, 自己实读 P9 页 + 网表
    prob22 = []
    net = pin_truth["net"]
    decl = pin_truth["decl"]
    p9 = pin_truth["p9"]
    pt = A.get("pin_truth") or {}
    for conn in ("J_CHG", "CONN_LIGHT", "CONN_CAM"):
        if conn not in pt:
            prob22.append(f"锚点 pin_truth 缺 {conn}")
    for conn, want in pt.items():
        got = net.get(conn)
        if got != want:
            prob22.append(f"网表实读 {conn} = {got}p ≠ 锚点 {want}p")
    for conn in ("J_CHG", "CONN_LIGHT", "CONN_CAM"):
        d = decl.get(conn) or []
        if not d:
            prob22.append(f"P9 页正文抽不到 {conn} 的 pin 声明")
        elif net.get(conn) not in d:
            prob22.append(f"P9 页声明 {conn}={d} ≠ 网表实读 {net.get(conn)}p")
    stale = [k for k in P9_STALE_MARKERS if k in p9]
    if stale:
        prob22.append(f"P9 页正文仍有旧口径 = {stale}")
    missing_new = [k for k in P9_NEW_MARKERS if k not in p9]
    if missing_new:
        prob22.append(f"P9 页正文缺新口径 = {missing_new}")
    g("C22", "PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)",
      not prob22,
      "; ".join(prob22) if prob22 else
      f"网表实读 CONN_LIGHT {net.get('CONN_LIGHT')}p / CONN_CAM {net.get('CONN_CAM')}p / "
      f"J_CHG {net.get('J_CHG')}p; P9 声明 CONN_LIGHT {decl.get('CONN_LIGHT')} / "
      f"CONN_CAM {decl.get('CONN_CAM')} / J_CHG {decl.get('J_CHG')}; 旧口径 0 处 / 新口径 3 处")

    # ---------------- G6 定性表 54/54 + 处置不留空 ----------------
    rows = parse_triage_rows(doc)
    items = [r["base"] for r in rows]
    src_ids = [r["id"] for r in xrev["results"]]
    from collections import Counter as _C
    miss_items = sorted((_C(src_ids) - _C(items)).elements())
    extra_items = sorted((_C(items) - _C(src_ids)).elements())
    empty_disp = [r["item"] for r in rows if not r["disp"].strip() or "待定" in r["disp"]]
    g("G6", "定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'",
      len(rows) == BASE_SUMMARY["total"] and not miss_items and not extra_items and not empty_disp,
      f"表内 {len(rows)} 行 / 应 {BASE_SUMMARY['total']}; 缺项号 = {miss_items or '无'}; "
      f"多余项号 = {extra_items or '无'}; 处置留空或待定 = {empty_disp or '无'}")
    # 16 条 FAIL 每条都有明确去处
    fail_rows = [r for r in rows if "FAIL" in r["verdict"]]
    ok_disp = ("维持现状", "出规格", "修掉", "登记 need 给 main", "排队等原理图定稿")
    no_dest = [r["item"] for r in fail_rows if r["disp"].strip() not in ok_disp]
    g("G6b", "16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)",
      len(fail_rows) == BASE_SUMMARY["fail"] and not no_dest,
      f"FAIL 行 {len(fail_rows)} 条; 去处不在受控词表里的 = {no_dest or '无'}")

    # ---------------- G7 分片账 (ISS-206 U-3) ----------------
    import yaml
    frag = os.path.join(root, "state", "fragments", "mech.yaml")
    fixed = None
    if os.path.exists(frag):
        d = yaml.safe_load(read_text(frag)) or {}
        for c in (d.get("interface_claims") or []):
            if c.get("key") == "mech_hinge_stack_fixed_mm":
                fixed = str(c.get("value"))
    g("G7", "分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)",
      fixed == "25.00", f"实测 value = {fixed}")

    # ---------------- G8 已修复的留痕必须在场 ----------------
    #  ★★【ISS-224 新增】★★ 一次真修复不许从账上消失 (删行 / 删节 / 抹留痕 ⇒ 红)
    prob8 = []
    pm_rows = [r for r in rows if r["base"] == "PIN-MISMATCH"]
    if not pm_rows:
        prob8.append("§2 定性表里找不到 PIN-MISMATCH 那一行 (行被删 = 抹掉一次真修复)")
    else:
        r0 = pm_rows[0]
        if "FAIL" in r0["verdict"]:
            prob8.append(f"PIN-MISMATCH 判定 = {r0['verdict']} (ISS-220 落表后应为 PASS)")
        elif "PASS" not in r0["verdict"]:
            prob8.append(f"PIN-MISMATCH 判定 = {r0['verdict']} (应为 ✅ PASS)")
        if "ISS-220" not in r0["note"]:
            prob8.append("PIN-MISMATCH 行的备注里没有 ISS-220 留痕")
        if "落表" not in r0["note"]:
            prob8.append("PIN-MISMATCH 行的备注里没有「落表」留痕")
    fixed_sec = parse_fixed_section(doc)
    if fixed_sec is None:
        prob8.append("§3.1「已修复 (留痕)」节不见了 (删节 = 抹掉一次真修复)")
    else:
        if "PIN-MISMATCH" not in fixed_sec["ids"]:
            prob8.append("§3.1「已修复」节里没有 PIN-MISMATCH")
        if "ISS-220" not in fixed_sec["text"]:
            prob8.append("§3.1「已修复」节里没有落表单号 ISS-220")
    g("G8", "已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)",
      not prob8,
      "; ".join(prob8) if prob8 else
      f"§2 行在位 (判定 = {pm_rows[0]['verdict'] if pm_rows else '—'}, 备注带 ISS-220/落表) + "
      f"§3.1 已修复节在位 (列着 {fixed_sec['ids'] if fixed_sec else '—'})")

    return out


# ====================================================================== selftest
def selftest(root: str, anchors: dict, facts: dict, xrev: dict,
             doc: str, pin_truth: dict) -> int:
    base = run_checks(root, anchors, facts, xrev, doc=doc, pin_truth=pin_truth)
    base_bad = [c for c in base if not c[2]]
    cases = []

    def add(name, expect, a=None, d=None, p=None, lt=None, mo=None):
        cases.append((name,
                      a if a is not None else copy.deepcopy(anchors),
                      d if d is not None else doc,
                      p if p is not None else pin_truth,
                      lt, mo, expect))

    # ---- 原 ISS-213 的 8 条反向用例 ----
    def m1(a): a["board_geom"].__setitem__("board_width_y", 15.00)
    add("反向1: 板宽锚点 30.00 → 15.00 (旧板宽)", "G4", a=mut(copy.deepcopy(anchors), m1))
    def m2(a): a["thresholds"].__setitem__("crit", 0.30)
    add("反向2: 判据 CRIT 0.60 → 0.30 (松判据)", "G5", a=mut(copy.deepcopy(anchors), m2))
    def m3(a): a["typec_panel"].__setitem__("new_opening_x", 9.50)
    add("反向3: 新开孔 10.50 → 9.50 (退回到不合格的现口径)", "G2.2",
        a=mut(copy.deepcopy(anchors), m3))
    def m4(a): a["thermal"].__setitem__("p_buck_w", 0.15)
    add("反向4: buck 耗散 0.50 → 0.15 (假装不需要金属热路)", "G2.6",
        a=mut(copy.deepcopy(anchors), m4))
    def m5(a): a.__setitem__("fail_expect", [x for x in a["fail_expect"] if x != "NET-LED"])
    add("反向5: FAIL 名单里删掉 NET-LED (把红灯调没)", "G1b",
        a=mut(copy.deepcopy(anchors), m5))
    def m6(a): a.__setitem__("pcb_class_queued",
                             [x for x in a["pcb_class_queued"] if x != "FRM-SUM"])
    add("反向6: 排队表里删掉 FRM-SUM (静默丢弃排队条目)", "G3",
        a=mut(copy.deepcopy(anchors), m6))
    def m7(a): a["board_geom"].__setitem__("board_mass_g", 3.30)
    add("反向7: 板重 3.33 → 3.30 (板框真源被偷改)", "G4",
        a=mut(copy.deepcopy(anchors), m7))
    def m8(a): a["thresholds"].__setitem__("cavity_req", 5.00)
    add("反向8: cavity_req 4.50 → 5.00 (松硬要求)", "G5",
        a=mut(copy.deepcopy(anchors), m8))

    # ---- ISS-224 新增: 真源不许被悄悄换 / 真修复不许被悄悄抹 ----
    # ⑨ P9 页正文回退成 21p (⇒ PIN-MISMATCH 改回 FAIL)
    def m9(p):
        p["p9"] = (p["p9"].replace("1×22p@0.5mm", "1×21p@0.5mm")
                       .replace("31p@0.3mm", "18p@0.5mm")
                       .replace("1 组跨铰链", "4 组跨铰链通道"))
        p["decl"] = declared_pins(p["p9"])
    add("反向9: P9 页正文回退成 21p (PIN-MISMATCH 改回 FAIL)", "C22",
        p=mut_pin(copy.deepcopy(pin_truth), m9))
    # ⑩ 网表 CONN_LIGHT 改回 21p
    def m10(p): p["net"]["CONN_LIGHT"] = 21
    add("反向10: 网表 CONN_LIGHT 改回 21p (网表被回退)", "C22",
        p=mut_pin(copy.deepcopy(pin_truth), m10))
    # ⑪ 网表 md5 锚点改回旧值
    def m11(a): a["source_ledger"]["entries"][0].__setitem__("md5", "c78f991283cc82d56c8e3dd31657c785")
    add("反向11: 网表 md5 锚点改回旧值 c78f9912… (锚点回滚)", "G5b",
        a=mut(copy.deepcopy(anchors), m11))
    # ⑫ md5 锚点改成台账里不存在的哈希
    def m12(a): a["source_ledger"]["entries"][0].__setitem__("md5", "deadbeefdeadbeefdeadbeefdeadbeef")
    add("反向12: 网表 md5 锚点改成台账里查不到的哈希", "C21",
        a=mut(copy.deepcopy(anchors), m12))
    # ⑬ 落表单号改坏
    def m13(a): a["source_ledger"]["entries"][0].__setitem__("by", "ISS-999")
    add("反向13: 落表单号改坏 (ISS-220 → ISS-999)", "C21",
        a=mut(copy.deepcopy(anchors), m13))
    # ⑭ 删掉「已修复」留痕 (§2 行的备注 + §3.1 整节)
    def m14(d):
        d = d.replace("★**已由 ISS-220 落表修复 (2026-11-16 02:32)** ★", "")
        d = re.sub(r"^##\s*3\.1[^\n]*已修复[^\n]*$.*?(?=^##\s*4\s)", "", d, flags=re.S | re.M)
        return d
    add("反向14: 删掉「已修复」留痕 (行 05 备注 + §3.1 整节)", "G8",
        d=m14(doc))

    # ---- ISS-273 新增: 判决源 = 落表台账最新记录 (链头) · 域侧锚点副本降级为历史留痕 ----
    base_led = read_text(os.path.join(root, LEDGER_CANON))
    recs_net = ledger_records(base_led, "HW/netlist_v1.csv")
    recs_pins = ledger_records(base_led, "HW/netlist_v1_pins.csv")
    net_head = ledger_state("HW/netlist_v1.csv", base_led)["head"]
    head_rec = next((r for r in recs_net if r["new"] == net_head), None)

    def drop_rel(text, rel):
        """把台账里该文件的全部落表记录行删掉 (⇒ 台账查不到这个文件)。"""
        b = os.path.basename(rel)
        out = []
        for ln in text.splitlines():
            t = ln.strip()
            if t.startswith("|") and (rel in t or b in t) and len(LEDGER_MD_RE.findall(t)) >= 2:
                continue
            out.append(ln)
        return "\n".join(out) + "\n"

    def break_head_ticket(text, rel, ticket="ISS-999"):
        """把台账最新记录那一行的落表单号改坏 (⇒ 单号与台账/锚点对不上)。"""
        head = ledger_state(rel, text)["head"]
        out, hit = [], 0
        for ln in text.splitlines():
            if head and head[:12] in ln and ln.strip().startswith("|") and "ISS-" in ln:
                ln = re.sub(r"ISS-\d+", ticket, ln, count=1)
                hit += 1
            out.append(ln)
        assert hit, "没找到台账最新记录那一行"
        return "\n".join(out) + "\n"

    # R1 —— 盘上网表被偷偷改 (md5 变, 台账没更新) ⇒ 必须红
    add("R1: 盘上网表被偷偷改 (md5 变, 台账没更新)", "C21",
        mo={"HW/netlist_v1.csv": "0badc0de0badc0de0badc0de0badc0de"})
    # R2 —— 盘上 md5 == 台账最新, 但域侧锚点副本停在历史值 (旧值在台账链里) ⇒ 必须绿 (本单要达成的行为)
    def m_r2(a):
        e = a["source_ledger"]["entries"][0]
        e["md5"] = "16ac89f77c25a3f61834cc7ebcd78a7f"
        e["by"] = "ISS-249"
    add("R2: 盘上 md5 == 台账最新, 域侧锚点副本停在历史值 ⇒ 必须绿", None,
        a=mut(copy.deepcopy(anchors), m_r2))
    # R3 —— 台账里查不到该文件的任何记录 ⇒ 必须红
    add("R3: 台账里查不到网表的任何落表记录", "C21",
        lt={LEDGER_CANON: drop_rel(base_led, "HW/netlist_v1.csv")})
    # R4 —— 台账里同一条链的多跳记录顺序打乱 ⇒ 仍取最新那条 ⇒ 必须绿 (不许假红也不许假绿)
    synth4 = synth_ledger({"HW/netlist_v1.csv": list(reversed(recs_net)),
                            "HW/netlist_v1_pins.csv": list(reversed(recs_pins))})
    add("R4: 台账里同一条链的记录顺序打乱 ⇒ 仍取最新 ⇒ 必须绿", None,
        lt={LEDGER_CANON: synth4})
    # R5a —— 台账最新记录的落表单号被改坏 (与台账/锚点对不上) ⇒ 必须红
    add("R5a: 台账最新记录的落表单号被改坏 (与台账对不上)", "C21",
        lt={LEDGER_CANON: break_head_ticket(base_led, "HW/netlist_v1.csv")})
    # R5b —— 台账最新记录的落表单号字段缺失 ⇒ 必须红
    synth5 = synth_ledger({"HW/netlist_v1.csv": [dict(head_rec or {}, iss=None)],
                            "HW/netlist_v1_pins.csv": recs_pins})
    add("R5b: 台账最新记录的落表单号字段缺失", "C21",
        lt={LEDGER_CANON: synth5})
    # R6 —— 板 / .kicad_pro md5 变 (硬保护) ⇒ 仍红, 且点名硬保护那一组 (G5b), 不是 C21
    add("R6: 板 md5 变 (硬保护) ⇒ 红, 且 C21 不红", ("G5b", ("C21",)),
        mo={"HW/PCB/demo_mainboard.kicad_pcb": "11111111111111111111111111111111"})

    print("=" * 100)
    print("ISS-213/224 机器门禁 —— 反向用例 (改坏任一锚点必须变红)")
    print("=" * 100)
    if base_bad:
        print(f"❌ 基线就不绿: {[c[0] for c in base_bad]} ⇒ 门禁本身有问题, 自测不成立")
        return 2
    print(f"  ✅ 基线全绿 ({len(base)}/{len(base)} 组检查)")
    ok = 0
    for name, a, d, p, lt, mo, expect in cases:
        res = run_checks(root, a, facts, xrev, doc=d, pin_truth=p,
                         ledger_texts=lt, md5_override=mo)
        red = [c[0] for c in res if not c[2]]
        if expect is None:
            hit, exp_txt = (not red), "绿 (不许红)"
        elif isinstance(expect, tuple):
            must, forbid = expect
            hit = (must in red) and all(x not in red for x in forbid)
            exp_txt = f"{must} 红 / {list(forbid)} 不红"
        else:
            hit, exp_txt = (expect in red), f"{expect} 红"
        flag = "✅" if hit else "❌"
        if hit:
            ok += 1
        print(f"  {flag} {name:<48} 期望 {exp_txt:<24} 实际红组 {red or '无'}")
    print("-" * 100)
    print(f"反向用例: {ok}/{len(cases)} 抓到了")
    return 0 if ok == len(cases) else 2


def mut(d: dict, fn) -> dict:
    fn(d)
    return d


def mut_pin(d: dict, fn) -> dict:
    fn(d)
    return d


# ====================================================================== main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="反向用例: 改坏任一锚点必须变红")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc = read_text(TRIAGE)
    anchors = load_anchors(doc)
    facts = load_sources(PROJ)
    xrev = run_cross_review(PROJ)
    pin_truth = load_pin_truth(PROJ)

    if args.selftest:
        return selftest(PROJ, anchors, facts, xrev, doc, pin_truth)

    res = run_checks(PROJ, anchors, facts, xrev, doc=doc, pin_truth=pin_truth)
    print("=" * 100)
    print("ISS-213/224 结构侧真值门禁 (demo 板当前成立的条目 + 板框/阈值/红灯保护 + 真源台账对账)")
    print("=" * 100)
    print(f"定性表: MECH/HW_CROSS_REVIEW_TRIAGE.md  |  源: MECH/service_port_check.py + "
          f"MECH/hw_cross_review_check.py + MECH/BOARD_GEOM_30MM.md + "
          f"HW/netlist_v1.csv + HW/SCHEMATIC_V1.md")
    print("-" * 100)
    for code, name, ok, detail in res:
        print(f"  [{'OK ' if ok else 'FAIL'}] {code:<5} {name}")
        print(f"         {detail}")
    npass = sum(1 for r in res if r[2])
    print("-" * 100)
    print(f"【结论】{npass}/{len(res)} 组检查通过 | FAIL {len(res)-npass} 组")
    print("口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。")
    print("          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。")
    print("          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。")
    print("          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。")
    print("=" * 100)
    if args.json:
        print(json.dumps({"checks": [{"code": c, "name": n, "ok": o, "detail": d}
                                      for c, n, o, d in res],
                          "summary": {"pass": npass, "total": len(res)}},
                         ensure_ascii=False, indent=2))
    return 0 if npass == len(res) else 2


if __name__ == "__main__":
    sys.exit(main())
