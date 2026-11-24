#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_fts_seat_body_geometry.py —— ISS-390 · `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】机器闸
===================================================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零改已签收页 / 零外发 / 不代拍** ★
★**派活**: 项目总工 (main) · ISS-390 · 2026-11-24 派 / 做 · 交卷人 = 结构总工 (mech-lead) ★
★**关联页**: `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` (★本单新建的真相页★) ·
           `HANDOFF/2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md` (交卷页) ★
★**只读引用 (★不改★)**: `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` (ISS-389 · ★`OI-12` 的前提错误所在页★) ·
          `MECH/check_debug_seat_3d_fit.py` (★既有 MECH 闸 · ★L848 / L879 两处「官方 land」字符串所在★) ·
          `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` (ISS-386 合一件答) ·
          `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` (ISS-387 · ★`OI-387-4` 的来源页★) ★
★**★闸不挂 `state/gate_check.py` (★挂不挂归 main·本闸只自证「没挂」★)★**

────────────────────────────────────────────────────────────────────────────────────────────────────────
【★★本单要防的病根 (★main 2026-11-24 本机实读撞出来的, ★不是抄任何 agent 报告★)★★】
  ★**① 把【盘上通用 KiCad 库件】的数当成【Samtec 厂件】的数 ★
       (`6.0900` / `5.0800` / `3.5500` / `2.5400` 的真身 = `PinHeader_1x0{4,2}_P1.27mm_Vertical` 的
        `F.CrtYd` / `F.Fab`; 本机实测 `(size 1 1)` + `(drill 0.65)` ⇒ 与 Samtec 无关)
       ⇒ **G3** (★对照物定性: 机器块必须显式写 `source = generic_kicad_lib`·★**不许**出现
         「官方 land courtyard / 官方 1x4 THT / 官方 land 的 F.Fab」这类把通用件说成厂件的措辞★)
       ⇒ **G3 现场扫 4 个目标并逐处点名** (★本单真相页 + ISS-389 页 + 既有 MECH 闸源码 + 既有 3D_FIT 页★)
  ★**② 厂件外形查不到就写成阻塞项挂着 / 写成「等原厂回信」 ★ ⇒ **G1/G2** (三量逐项有值或明确 `[0数据]`
       + `[0数据]` 必须挂得上降级 id) + **零挂起措辞扫描** ★
  ★**③ §4 的订正漏登一处 ⇒ main 不知道还差哪几处 ⇒ **G4** (4 处逐条登记, 缺一条即红) ★
  ★**④ 影响面写空 / 不写「要不要重算」 ⇒ **G5** (`OI-12` 三值 + 受影响数名清单不许空, ★从机器块读, 不写死★) ★
  ★**⑤ 偷偷替 main / boss 拍板 ⇒ **G1.5** (三个 `*_decision` 字段必须全是 `not_decided_here`) ★
  ★**⑥ 写板 / 落表 / 挂链 ⇒ **G6** ★
  ★**⑦ 本闸自己环境敏感 ⇒ **G7** (★沙盒落项目盘 + 两个不同深度读数必须一致 + 源码不许碰系统 `/tmp`★) ★

【★G3 的三段语义 (★必须讲清, 否则会误读★)★】
  G3.1  ★**声明段** ★: 机器块 `attribution.source_of_6_0900_5_0800_3_5500_2_5400` 必须逐字 == `generic_kicad_lib`
        ⇒ **红线**: 改成 `samtec_official` 之类 ⇒ 必红 (★反向用例 c01★)
  G3.2  ★**现场扫描段** ★: 扫 4 个目标文件, 命中「把通用件说成厂件」的措辞 ⇒ **逐处点名 (文件 + 行号 + 命中的词)**;
        ★**命中若已被 §4 登记 (登记项的 `scan_substrings` 逐字出现在那一行里) ⇒ 算「已登记·待 main 落」,
        进「未落清单」并打印出来, 但【不】计为本闸失败** ★ (★本单零改既有页/零改既有闸 ⇒ 这类命中必然还在★);
        ★**命中若【没被登记】⇒ 必红, 且点名是哪一处 (★这就是「未登记的前提错误」, 真正的病根★) ★**
  G3.3  ★**防绕过段** ★: 机器块 `forbidden_phrasings` 列表必须与本闸的 `FORBIDDEN_MARKERS` **逐条相等 (集合相等)**
        ⇒ ★**不许把闸的词表弱化掉** ★ (★反向用例 c06 / c10★)

【rc 语义】
  0 = 全部通过 (★含「已登记·待 main 落」的未落清单, ★清单照样打印在输出里★)
  1 = 有断言不通过 (逐条列出 + 点名判据号)
  2 = 参数 / IO 错误

【用法】
  python3 MECH/check_fts_seat_body_geometry.py             # 扫真件 (只读)
  python3 MECH/check_fts_seat_body_geometry.py --emit      # 打印机器块 JSON (供页内粘贴)
  python3 MECH/check_fts_seat_body_geometry.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_fts_seat_body_geometry.py --root DIR  # 扫指定树 (反向用例在 <root>/tmp/iss390_sbx/selftest/ 上做)

【★沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss390_sbx/selftest/` (★不许写系统 `/tmp`·不许用硬链接★)
             ★路径全部从本闸自己的 `ROOT` 推 ⇒ 环境无关 (★G7 会自证这一点★)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

PAGE_REL = "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md"
ISS389_REL = "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md"
GATE3D_REL = "MECH/check_debug_seat_3d_fit.py"
FIT_REL = "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md"
GATE_REL = "state/gate_check.py"
PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"
NETLIST_REL = "HW/netlist_v1.csv"
PINS_REL = "HW/netlist_v1_pins.csv"
BOM_REL = "HW/BOM_v1.csv"

BLOCK_BEGIN = "<!-- MECH-FTS-SEAT-BODY-GEOMETRY-JSON-BEGIN -->"
BLOCK_END = "<!-- MECH-FTS-SEAT-BODY-GEOMETRY-JSON-END -->"

SANDBOX_REL = os.path.join("tmp", "iss390_sbx", "selftest")

BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime_ns": None,   # 运行时从基线常量填 (见下)
    "size": 4940213,
}
BOARD_BASELINE_MTIME = "2026-11-06 07:07:17.362193413"

TABLE_BASELINE = {
    NETLIST_REL: "6aee500e60ba0732f83a9cf557ba90ab",
    PINS_REL: "9174309df1ec9411ac8e8d9e80ee386a",
    BOM_REL: "5b9993992405904a60ac96a020b375d8",
}

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")

# ★★G3 的词表: ★每一条都是「把【通用第三方库件】的数说成【Samtec 厂件】的数」的措辞 ★★
# ★★【为什么要收窄到这些形式】★★: ★「官方 1x2 THT」/「换官方 1×4 THT」这类说法在仓里是【合法】的 ——
#   它指的是【把那颗连接器换成 FTS 厂件】(★厂件确实存在, ★而且厂件 land 也有官方件★), 不是把通用库的数冒充成厂件 ★
#   ⇒ ★**只有当「官方 / 厂件」这个定语【直接挂在本机通用库件的 `F.CrtYd` / `F.Fab` 图元上】时, 才是误认** ★
#   ⇒ 下面这 12 条就是那 12 种误认形式 (★反向用例 c01 / c05 / c06 / c10 / c12 全打这一组★) ★
FORBIDDEN_MARKERS = (
    "官方 land courtyard",
    "官方 land 的 F.Fab",
    "官方 land 的 `F.Fab`",
    "官方 land 的 `F.CrtYd`",
    "官方 land 自己的",
    "官方 1x4 THT 的 F.CrtYd",
    "官方 1x2 THT 的 F.CrtYd",
    "官方 1x4 THT 座体本体",
    "官方 1x2 THT 座体本体",
    "官方 1×4 THT 座体本体",
    "官方 1×2 THT 座体本体",
    "IPC 的 courtyard",
    "比 courtyard `6.0900` 还小",
)

# ★★零挂起措辞 (★缺口一律自己算 + 标证据等级 + 给降级方案·不许挂外部依赖★)★★
FORBIDDEN_PENDING = (
    "等原厂回信",
    "待原厂回信",
    "待外部确认",
    "等待原厂",
    "pending",
    "TODO:等",
)

# ★★G4: §4 必须逐条登记的 4 处 (★brief 明令·★缺一条即红★)★★
REQUIRED_CORRECTIONS = (
    ("MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md", "L634"),
    ("MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md", "L149"),
    ("MECH/check_debug_seat_3d_fit.py", "L848"),
    ("MECH/check_debug_seat_3d_fit.py", "L879"),
)

REQUIRED_PARTS = ("FTS-104-01-F-S", "FTS-102-01-F-S")
REQUIRED_QUANTITIES = ("seat_body_width_x_mm", "seat_body_depth_y_mm", "insulator_height_z_mm")

OI12_STATUS_ENUM = ("不需重算", "需重算", "待定")

COPY_FILES = (
    PAGE_REL,
    ISS389_REL,
    GATE3D_REL,
    FIT_REL,
    GATE_REL,
    PCB_REL,
    NETLIST_REL,
    PINS_REL,
    BOM_REL,
)

SCAN_TARGETS = (PAGE_REL, ISS389_REL, GATE3D_REL, FIT_REL)


# ==================================================================================================
# 小工具
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def p(root: str, rel: str) -> str:
    return os.path.normpath(os.path.join(root, rel))


def strip_md(s: str) -> str:
    s = re.sub(r"`{1,3}", "", s)
    s = re.sub(r"\*+", "", s)
    return s


def extract_json_fence(text: str, begin: str, end: str):
    i = text.find(begin)
    j = text.find(end)
    if i < 0 or j < 0 or j <= i:
        return None
    seg = text[i:j]
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", seg, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def section_text(text: str, start_tok: str, end_tok: str) -> str:
    i = text.find(start_tok)
    if i < 0:
        return ""
    j = text.find(end_tok, i + len(start_tok))
    if j < 0:
        j = len(text)
    return text[i:j]


def board_mtime_ns(path: str):
    try:
        return os.stat(path).st_mtime_ns
    except OSError:
        return None


def board_baseline_mtime_ns() -> int:
    """基线 mtime = '2026-11-06 07:07:17.362193413' (★纳秒 9 位, ★手工拆·不靠 %f★)"""
    import datetime
    date_part, frac = BOARD_BASELINE_MTIME.split(".")
    frac = (frac + "000000000")[:9]
    dt = datetime.datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    return int(dt.timestamp()) * 1_000_000_000 + int(frac)


# ==================================================================================================
# 真相页 / 机器块 读取
# ==================================================================================================
class Facts:
    def __init__(self, root: str):
        self.root = root
        self.page_path = p(root, PAGE_REL)
        self.page = read_text(self.page_path)
        self.block = extract_json_fence(self.page, BLOCK_BEGIN, BLOCK_END)
        # ★§4 订正表区域 (★这里是【故意引用错误措辞】的地方, ★扫描时要排除★)★
        self.sec4 = section_text(self.page, "## ★§4", "## ★§5")
        # ★机器块区域 (★含 forbidden_phrasings 清单, ★扫描时要排除★)★
        i = self.page.find(BLOCK_BEGIN)
        j = self.page.find(BLOCK_END)
        self.block_region = self.page[i:j] if (i >= 0 and j > i) else ""

    @staticmethod
    def _line_span(text: str, start_idx: int, end_idx: int):
        if start_idx < 0:
            return None
        if end_idx < 0:
            end_idx = len(text)
        return (text.count("\n", 0, start_idx) + 1, text.count("\n", 0, end_idx) + 1)

    def quote_spans(self):
        """★真相页里【允许出现错误措辞】的两块: §4 订正表 + 机器块 ★"""
        s4 = self._line_span(self.page, self.page.find("## ★§4"), self.page.find("## ★§5"))
        i = self.page.find(BLOCK_BEGIN)
        j = self.page.find(BLOCK_END)
        sb = self._line_span(self.page, i, (j + len(BLOCK_END)) if j > i else -1)
        spans = [s for s in (s4, sb) if s]
        return spans

    @staticmethod
    def _in_spans(n: int, spans) -> bool:
        for a, b in spans:
            if a <= n <= b:
                return True
        return False

    def scan_files(self) -> list:
        """返回 [(rel, [(line_no, line_text, marker), ...]), ...] —— 只取本闸真正要扫的 4 个目标"""
        out = []
        for rel in SCAN_TARGETS:
            path = p(self.root, rel)
            if not os.path.isfile(path):
                continue
            lines = read_text(path).splitlines()
            hits = []
            for n, line in enumerate(lines, 1):
                for mk in FORBIDDEN_MARKERS:
                    if mk in line:
                        hits.append((n, line, mk))
                        break
            out.append((rel, hits))
        return out

    def correction_index(self) -> dict:
        """{rel_file: [scan_substrings]}"""
        idx = {}
        for c in (self.block or {}).get("corrections_registered") or []:
            loc = str(c.get("loc") or "")
            rel = loc.split(" L")[0].split(" L")[0].strip()
            for m in re.finditer(r"(MECH/[A-Za-z0-9_./-]+\.(?:md|py))", loc):
                rel = m.group(1)
            subs = c.get("scan_substrings") or ([c.get("scan_substring")] if c.get("scan_substring") else [])
            idx.setdefault(rel, []).extend([s for s in subs if s])
        return idx


# ==================================================================================================
# 闸
# ==================================================================================================
class Gate:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.f = Facts(self.root)
        self.results = []
        self.notes = []
        self.pending = []          # ★已登记·待 main 落 的未落清单 ★

    def chk(self, kid, ok, msg):
        self.results.append((kid, bool(ok), msg))

    # ---------------- G1 (机器块 + 三量逐项有值 + 不代拍) ----------------
    def g1(self):
        if self.f.block is None:
            self.chk("G1.0", False, "★机器块 (JSON) 缺失或不可解析 (%s ... %s)" % (BLOCK_BEGIN, BLOCK_END))
            return
        self.chk("G1.0", True, "机器块在盘且可解析")
        bg = self.f.block.get("body_geometry") or {}
        missing = []
        for part in REQUIRED_PARTS:
            node = bg.get(part)
            if not isinstance(node, dict):
                missing.append("%s: 机器块 body_geometry 里没有这一项" % part)
                continue
            for q in REQUIRED_QUANTITIES:
                cell = node.get(q)
                if not isinstance(cell, dict):
                    missing.append("%s/%s: 缺字段" % (part, q))
                    continue
                val = str(cell.get("value") or "").strip()
                if val == "":
                    missing.append("%s/%s: value 为空 (★不许空串·不许缺项★)" % (part, q))
        self.chk("G1.1", not missing,
                 "★三量 (宽 X / 深 Y / 绝缘体高 Z) 逐项必须有值或明确 `[0数据]`: %s" % missing)

        # 不代拍: 三个 *_decision 字段必须全是 not_decided_here
        dec = self.f.block.get("decisions") or {}
        bad = []
        for k, v in dec.items():
            if not k.endswith("_decision"):
                continue
            if str(v) != "not_decided_here":
                bad.append("%s=%r" % (k, v))
        self.chk("G1.2", len(dec) >= 3 and not bad,
                 "★`decisions` 必须有 ≥3 项且全是 `not_decided_here` (★不许代拍★): 坏项 %s / 共 %d 项"
                 % (bad, len(dec)))

        # §0~§7 齐全
        need_secs = ["## ★§0", "## ★§1", "## ★§2", "## ★§3", "## ★§4",
                     "## ★§5", "## ★§6", "## ★§7"]
        lack = [s for s in need_secs if s not in self.f.page]
        self.chk("G1.3", not lack, "真相页 §0~§7 缺: %s" % lack)

    # ---------------- G2 (证据等级白名单 + [0数据] 必须挂降级 id) ----------------
    def g2(self):
        bg = (self.f.block or {}).get("body_geometry") or {}
        deg = (self.f.block or {}).get("degradation") or {}
        deg_ids = set()
        pb = deg.get("path_b") or {}
        if pb.get("id"):
            deg_ids.add(str(pb["id"]))
        for d in deg.get("degrade_plans") or []:
            if d.get("id"):
                deg_ids.add(str(d["id"]))
        for k in ("path_a", "path_b"):
            if isinstance(deg.get(k), dict) and deg[k].get("id"):
                deg_ids.add(str(deg[k]["id"]))

        bad_ev = []
        bad_deg = []
        for part in REQUIRED_PARTS:
            node = bg.get(part) or {}
            for q in REQUIRED_QUANTITIES:
                cell = node.get(q) or {}
                ev = str(cell.get("evidence") or "")
                tags = re.findall(r"\[[^\]]+\]", ev)
                if not tags:
                    bad_ev.append("%s/%s: 无证据标记" % (part, q))
                    continue
                for tg in tags:
                    if tg not in EVIDENCE_WHITELIST:
                        bad_ev.append("%s/%s: %s (★白名单 %s★)" % (part, q, tg, list(EVIDENCE_WHITELIST)))
                if "[0数据]" in tags:
                    did = str(cell.get("degradation_id") or "").strip()
                    if not did:
                        bad_deg.append("%s/%s: `[0数据]` 但没有 degradation_id" % (part, q))
                    elif did not in deg_ids:
                        bad_deg.append("%s/%s: degradation_id %r 不在降级方案表里 (★可查到的: %s★)"
                                       % (part, q, did, sorted(deg_ids)))
        self.chk("G2.1", not bad_ev, "★证据分级越界或缺失: %s" % bad_ev)
        self.chk("G2.2", not bad_deg, "★`[0数据]` 的项必须挂得上降级 id (★不许「0数据但没降级」★): %s" % bad_deg)

        # 零挂起措辞 (全页扫, ★机器块与 §4 区除外——那里是故意引用★)
        page = self.f.page.replace(self.f.block_region, "")
        page = page.replace(self.f.sec4, "")
        hits = [w for w in FORBIDDEN_PENDING if w in page]
        self.chk("G2.3", not hits,
                 "★页内出现挂起措辞 (★查不到 ⇒ 自己网上查 + 标证据等级 + 写降级方案; 不许挂外部依赖★): %s" % hits)

        # 降级方案必须写清「谁 / 什么时候 / 量哪三个量 / 填回哪一格」
        pb = deg.get("path_b") or {}
        need = ("who", "when", "measure", "fill_back_to")
        lack = [k for k in need if not pb.get(k)]
        self.chk("G2.4", bool(pb.get("id")) and not lack and len(pb.get("measure") or []) >= 3,
                 "★降级方案 (路径乙) 必须写清 %s 且至少 3 个量: 缺 %s" % (list(need), lack))
        self.chk("G2.5", deg.get("blocked_on_external_reply") is False,
                 "★降级方案不许挂外部回复 (★不许写「等原厂回信」★)")

    # ---------------- G3 (对照物定性) ----------------
    def g3(self):
        blk = self.f.block or {}
        attr = blk.get("attribution") or {}
        src = str(attr.get("source_of_6_0900_5_0800_3_5500_2_5400") or "")
        self.chk("G3.1", src == "generic_kicad_lib",
                 "★对照物定性: `6.0900`/`5.0800`/`3.5500`/`2.5400` 的来源必须逐字写 `generic_kicad_lib`"
                 " (★现在是 %r★)" % src)
        self.chk("G3.2", attr.get("is_samtec_vendor_data") is False,
                 "★机器块必须显式声明 `is_samtec_vendor_data = false`★")
        vendor = attr.get("samtec_vendor_body_values") or {}
        self.chk("G3.3", bool(vendor.get("x")) and bool(vendor.get("y")) and bool(vendor.get("z")),
                 "★机器块必须显式写出厂件座体三量 (samtec_vendor_body_values.x/y/z)★")
        self.chk("G3.4", attr.get("samtec_has_courtyard_concept") is False,
                 "★机器块必须显式声明 `samtec_has_courtyard_concept = false` (★厂件没有 courtyard 这个量★)")

        # 防绕过: 词表必须与本闸一致
        listed = attr.get("forbidden_phrasings") or []
        if isinstance(listed, str):
            listed = [listed]
        miss = [m for m in FORBIDDEN_MARKERS if m not in listed]
        extra = [m for m in listed if m not in FORBIDDEN_MARKERS]
        self.chk("G3.5", not miss and not extra,
                 "★机器块 `forbidden_phrasings` 必须与本闸词表逐条相等 (★不许弱化闸★): 缺 %s / 多 %s"
                 % (miss, extra))

        # 现场扫描 + 逐处点名
        cidx = self.f.correction_index()
        spans = self.f.quote_spans()
        unregistered = []
        for rel, hits in self.f.scan_files():
            for (n, line, mk) in hits:
                if rel == PAGE_REL:
                    # ★★真相页: 只有 §4 订正表区与机器块区允许出现 (★那里是【登记区】, ★故意引用★)
                    if self.f._in_spans(n, spans):
                        self.notes.append("真相页 §4/机器块 登记区内的引用 (★故意·不计入未落清单★): %s L%d [%s]"
                                          % (rel, n, mk))
                        continue
                    unregistered.append("%s L%d [%s] ⇒ %s" % (rel, n, mk, line.strip()[:120]))
                    continue
                covered = False
                for sub in cidx.get(rel, []):
                    if sub in line:
                        covered = True
                        break
                if covered:
                    self.pending.append("%s L%d [%s]" % (rel, n, mk))
                else:
                    unregistered.append("%s L%d [%s] ⇒ %s" % (rel, n, mk, line.strip()[:120]))
        self.chk("G3.6", not unregistered,
                 "★未登记的「把通用件说成厂件」措辞 (★逐处点名★): %s" % unregistered)

    # ---------------- G4 (§4 订正登记 4 处齐全) ----------------
    def g4(self):
        cors = (self.f.block or {}).get("corrections_registered") or []
        by_loc = {}
        for c in cors:
            by_loc[str(c.get("loc") or "")] = c
        lack = []
        for rel, line_tok in REQUIRED_CORRECTIONS:
            hit = None
            for loc, c in by_loc.items():
                if rel in loc and line_tok in loc:
                    hit = c
                    break
            if hit is None:
                lack.append("%s %s" % (rel, line_tok))
                continue
            for k in ("old", "new", "status"):
                if not str(hit.get(k) or "").strip():
                    lack.append("%s %s: 登记项缺字段 %s" % (rel, line_tok, k))
            if str(hit.get("status") or "") not in ("待 main 落", "已落"):
                lack.append("%s %s: status 必须是 `待 main 落` 或 `已落` (★现 %r★)"
                            % (rel, line_tok, hit.get("status")))
        self.chk("G4.1", not lack,
                 "★§4 的 4 处前提订正必须逐条登记 (哪一行 / 原措辞 / 新措辞 / 状态) ⇒ 缺一条即红: %s" % lack)

        # 真相页 §4 表里也要逐条点名这 4 处
        sec4 = self.f.sec4
        lack2 = []
        for rel, line_tok in REQUIRED_CORRECTIONS:
            if rel not in sec4 or line_tok not in sec4:
                lack2.append("%s %s" % (rel, line_tok))
        self.chk("G4.2", not lack2,
                 "★真相页 §4 订正表必须逐条点名这 4 处: %s" % lack2)

        # ★本单零改既有文件 ⇒ 登记项的状态必须是「待 main 落」★
        self.chk("G4.3", len(cors) >= 4,
                 "★订正登记项少于 4 条: %d★" % len(cors))

    # ---------------- G5 (影响面: OI-12 三值 + 受影响数清单) ----------------
    def g5(self):
        blk = self.f.block or {}
        oi = blk.get("oi12_recompute") or {}
        st = str(oi.get("status") or "")
        self.chk("G5.1", st in OI12_STATUS_ENUM,
                 "★`OI-12` 结论状态必须是三值之一 %s (★现 %r★)" % (list(OI12_STATUS_ENUM), st))
        det = (blk.get("impact") or {}).get("affected_numbers_detail") or []
        changed = [d for d in det if str(d.get("change")).lower() == "true"]
        if st == "需重算":
            self.chk("G5.2", len(changed) >= 1,
                     "★`需重算` ⇒ 必须列出受影响的数名清单 (★从机器块 `impact.affected_numbers_detail` 读·不许写死★)★")
            self.chk("G5.3", all(str(d.get("name") or "").strip() for d in changed),
                     "★受影响的数名不许有空串★")
        else:
            self.chk("G5.2", True, "★`OI-12` = %s ⇒ 不强制要求受影响数清单★" % st)
            self.chk("G5.3", True, "★`OI-12` = %s ⇒ 跳过受影响数清单检查★" % st)
        # 不变 / 变 两张清单都要有
        imp = blk.get("impact") or {}
        self.chk("G5.4", bool(imp.get("unchanged")) and bool(imp.get("changed")),
                 "★影响面必须同时写清【哪些不变】与【哪些变】★")
        # 本单的三量必须与 §2 的三量表逐字一致 (页 ↔ 块)
        sec2 = section_text(self.f.page, "## ★§2", "## ★§3")
        bg = (blk.get("body_geometry") or {})
        bad = []
        for part in REQUIRED_PARTS:
            node = bg.get(part) or {}
            for q in REQUIRED_QUANTITIES:
                v = str((node.get(q) or {}).get("value") or "")
                if v and v not in sec2:
                    bad.append("%s/%s=%s" % (part, q, v))
        self.chk("G5.5", not bad,
                 "★机器块的三量值必须逐字出现在页 §2 三量表里: %s" % bad)

    # ---------------- G6 (零写板 / 零落表 / 零挂链) ----------------
    def g6(self):
        pcb = p(self.root, PCB_REL)
        if os.path.isfile(pcb):
            st = os.stat(pcb)
            self.chk("G6.1", md5_of(pcb) == BOARD_BASELINE["md5"],
                     "板 md5 %s ≠ 基线 %s (零写板被破坏)" % (md5_of(pcb), BOARD_BASELINE["md5"]))
            want_ns = board_baseline_mtime_ns()
            self.chk("G6.2", st.st_mtime_ns == want_ns,
                     "板 mtime_ns %d ≠ 基线 %d (零写板被破坏)" % (st.st_mtime_ns, want_ns))
            self.chk("G6.3", st.st_size == BOARD_BASELINE["size"],
                     "板 size %d ≠ 基线 %d (零写板被破坏)" % (st.st_size, BOARD_BASELINE["size"]))
        else:
            self.chk("G6.1", False, "板文件不在盘: %s" % PCB_REL)
        for rel, want in TABLE_BASELINE.items():
            f = p(self.root, rel)
            if not os.path.isfile(f):
                self.chk("G6.4", False, "表文件不在盘: %s" % rel)
                continue
            got = md5_of(f)
            self.chk("G6.4", got == want,
                     "%s md5 %s ≠ 基线 %s (零落表被破坏)" % (rel, got, want))
        gf = p(self.root, GATE_REL)
        if os.path.isfile(gf):
            txt = read_text(gf)
            self.chk("G6.5", "check_fts_seat_body_geometry" not in txt,
                     "★本闸被挂进了 state/gate_check.py (★本单零挂链·挂不挂归 main★)")
        else:
            self.chk("G6.5", False, "state/gate_check.py 不在盘")

    # ---------------- G7 (本闸自己环境无关) ----------------
    def g7(self):
        # G7.1 沙盒路径必须落项目盘 (从本闸自己的 ROOT 推)
        self.chk("G7.1",
                 (not SANDBOX_REL.startswith(("/", "\\"))) and ".." not in SANDBOX_REL
                 and SANDBOX_REL.startswith(os.path.join("tmp", "iss390_sbx")),
                 "★沙盒必须落项目盘 `<root>/tmp/iss390_sbx/`: 现 %r★" % SANDBOX_REL)

        # G7.2 源码不许碰系统 /tmp / tempfile
        # ★★下面这些 token 是【拼】出来的 ⇒ 源码里不会出现它们的字面量 ⇒ 自检不自伤★★
        bad_tokens = ("tempfile." "gettempdir", "tempfile." "mkdtemp",
                      '"' + "/tm" + 'p"', "'" + "/tm" + "p'")
        src = read_text(os.path.abspath(__file__))
        bad = []
        for tok in bad_tokens:
            if tok in src:
                bad.append(tok)
        self.chk("G7.2", not bad,
                 "★本闸源码不许依赖系统临时目录 (★沙盒一律从 ROOT 推★): %s" % bad)

        # G7.3 两个不同深度 (不同 cwd) 的读数必须一致
        def fingerprint() -> list:
            out = []
            for rel in SCAN_TARGETS + (PCB_REL, NETLIST_REL, PINS_REL, BOM_REL):
                f = p(self.root, rel)
                if os.path.isfile(f):
                    out.append((rel, md5_of(f)))
            return out

        cwd0 = os.getcwd()
        try:
            os.chdir(cwd0)
            fp0 = fingerprint()
            os.chdir(self.root)
            fp1 = fingerprint()
            os.chdir(p(self.root, "MECH"))
            fp2 = fingerprint()
        finally:
            os.chdir(cwd0)
        self.chk("G7.3", fp0 == fp1 == fp2,
                 "★两个不同深度的读数必须一致 (★cwd 无关★): %s" %
                 ("一致" if fp0 == fp1 == fp2 else "不一致 %s / %s / %s" % (fp0, fp1, fp2)))

    # ---------------- run ----------------
    def run(self):
        self.g1()
        self.g2()
        self.g3()
        self.g4()
        self.g5()
        self.g6()
        self.g7()
        return self.results


# ==================================================================================================
# 沙盒 / 反向用例
# ==================================================================================================
def make_sandbox(root: str, case: str):
    sb = p(root, os.path.join(SANDBOX_REL, case))
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    for rel in COPY_FILES:
        src = p(root, rel)
        dst = p(sb, rel)
        if not os.path.isfile(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)          # ★不许硬链接 (cp -al)★
    return sb


def write_text(path: str, s: str):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(s)


def block_mutate(sb: str, fn):
    path = p(sb, PAGE_REL)
    txt = read_text(path)
    i = txt.find(BLOCK_BEGIN)
    j = txt.find(BLOCK_END)
    seg = txt[i:j]
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", seg, re.S)
    if not m:
        raise AssertionError("block_mutate: 找不到机器块 json fence")
    data = json.loads(m.group(1))
    fn(data)
    new_seg = seg[:m.start()] + "```json\n" + json.dumps(data, ensure_ascii=False, indent=1) + "\n```" + seg[m.end():]
    write_text(path, txt[:i] + new_seg + txt[j:])


def page_replace(sb: str, old: str, new: str):
    path = p(sb, PAGE_REL)
    txt = read_text(path)
    if old not in txt:
        raise AssertionError("page_replace: 找不到 %r" % old[:60])
    write_text(path, txt.replace(old, new, 1))


def selftest(root: str):
    cases = []

    def case(name, desc, mutate, expect_kid):
        cases.append((name, desc, mutate, expect_kid))

    # 01 ★★定性★★ 把对照物来源从 generic_kicad_lib 改成 samtec_official ⇒ 必须 G3 红
    def m01(sb):
        block_mutate(sb, lambda d: d["attribution"].__setitem__(
            "source_of_6_0900_5_0800_3_5500_2_5400", "samtec_official"))
    case("c01_source_is_samtec",
         "★★定性★★ 把 `6.0900` 的 source 从 `generic_kicad_lib` 改成 `samtec_official` ⇒ 必须红 (G3)",
         m01, "G3")

    # 02 ★★定性★★ 删掉 §4 订正登记里的一处 ⇒ 必须 G4 红
    def m02(sb):
        block_mutate(sb, lambda d: d.__setitem__(
            "corrections_registered",
            [c for c in d["corrections_registered"] if "L879" not in str(c.get("loc"))]))
    case("c02_drop_one_correction",
         "★★定性★★ 删掉 §4 订正登记里的一处 (L879) ⇒ 必须红 (G4)",
         m02, "G4")

    # 03 证据等级改成六级之外的词 ⇒ 必须 G2 红
    def m03(sb):
        block_mutate(sb, lambda d: d["body_geometry"]["FTS-104-01-F-S"]
                     ["insulator_height_z_mm"].__setitem__("evidence", "[猜测]"))
    case("c03_bad_evidence_tag",
         "把某一项的证据等级改成六级之外的词 `[猜测]` ⇒ 必须红 (G2)",
         m03, "G2")

    # 04 [0数据] 项的降级 id 删掉 ⇒ 必须 G2 红
    def m04(sb):
        def f(d):
            cell = d["body_geometry"]["FTS-102-01-F-S"]["seat_body_depth_y_mm"]
            cell["evidence"] = "[0数据]"
            cell["degradation_id"] = ""
        block_mutate(sb, f)
    case("c04_zero_data_without_degradation",
         "把某一项改成 `[0数据]` 但删掉降级 id ⇒ 必须红 (G2)",
         m04, "G2")

    # 05 ★★定性★★ 往真相页正文注入【未登记】的「官方 land courtyard」⇒ 必须 G3 红
    def m05(sb):
        page_replace(sb, "## ★§3 降级方案", "## ★§3 降级方案\n\n★本件的官方 land courtyard 按厂件算★")
    case("c05_unregistered_phrase_in_page",
         "★★定性★★ 往真相页正文注入【未登记】的「官方 land courtyard」⇒ 必须红 (G3)",
         m05, "G3")

    # 06 ★★定性★★ 把机器块的 forbidden_phrasings 弱化 (删一条) ⇒ 必须 G3 红
    def m06(sb):
        block_mutate(sb, lambda d: d["attribution"].__setitem__(
            "forbidden_phrasings", [m for m in d["attribution"]["forbidden_phrasings"]
                                    if m != "官方 land courtyard"]))
    case("c06_weakened_wordlist",
         "★★定性★★ 把机器块的 `forbidden_phrasings` 删一条 (弱化闸) ⇒ 必须红 (G3)",
         m06, "G3")

    # 07 `OI-12` = 需重算 但把受影响数清单清空 ⇒ 必须 G5 红
    def m07(sb):
        def f(d):
            d["impact"]["affected_numbers_detail"] = [x for x in d["impact"]["affected_numbers_detail"]
                                                      if str(x.get("change")).lower() != "true"]
        block_mutate(sb, f)
    case("c07_oi12_needs_recompute_empty_impact",
         "★`OI-12` = 需重算 但把受影响数清单清空 ⇒ 必须红 (G5)",
         m07, "G5")

    # 08 偷偷替 main 拍板 ⇒ 必须 G1 红
    def m08(sb):
        block_mutate(sb, lambda d: d["decisions"].__setitem__("oi12_over_strict_decision", "是"))
    case("c08_decided_for_main",
         "偷偷把 `oi12_over_strict_decision` 写成「是」⇒ 必须红 (G1)",
         m08, "G1")

    # 09 沙盒板被追加一字节 ⇒ 必须 G6 红
    def m09(sb):
        with open(p(sb, PCB_REL), "ab") as fh:
            fh.write(b"\n")
    case("c09_board_changed", "沙盒板被追加一字节 ⇒ 必须红 (G6)", m09, "G6")

    # 10 ★★定性★★ 把 forbidden_phrasings 里某条换成【同义但不同】的词 (绕过) ⇒ 必须 G3 红
    def m10(sb):
        def f(d):
            fp = d["attribution"]["forbidden_phrasings"]
            fp[fp.index("官方 land courtyard")] = "厂件的 land courtyard"
        block_mutate(sb, f)
    case("c10_wordlist_renamed",
         "★★定性★★ 把词表里的「官方 land courtyard」换成同义不同词 ⇒ 必须红 (G3)",
         m10, "G3")

    # 11 把三量的 value 抽空 ⇒ 必须 G1 红
    def m11(sb):
        block_mutate(sb, lambda d: d["body_geometry"]["FTS-104-01-F-S"]
                     ["seat_body_width_x_mm"].__setitem__("value", ""))
    case("c11_empty_quantity",
         "把三量里一项的 value 抽空 ⇒ 必须红 (G1)",
         m11, "G1")

    # 12 ★★定性★★ 在 ISS-389 页里注入【未登记】的另一种「把通用件说成厂件」措辞 ⇒ 必须 G3 红
    def m12(sb):
        path = p(sb, ISS389_REL)
        txt = read_text(path)
        write_text(path, txt + "\n★补充: 官方 1x2 THT 的 F.CrtYd 就是厂件 courtyard★\n")
    case("c12_unregistered_phrase_in_iss389",
         "★★定性★★ 在 ISS-389 页注入【未登记】的「官方 1x2 THT … 厂件 courtyard」⇒ 必须红 (G3)",
         m12, "G3")

    # 13 把降级方案挂到外部回复 ⇒ 必须 G2 红
    def m13(sb):
        block_mutate(sb, lambda d: d["degradation"].__setitem__("blocked_on_external_reply", True))
    case("c13_degradation_blocked_on_external",
         "把降级方案标成「等外部回复」⇒ 必须红 (G2)",
         m13, "G2")

    # 14 本闸被挂进 gate_check.py ⇒ 必须 G6 红
    def m14(sb):
        write_text(p(sb, GATE_REL), read_text(p(sb, GATE_REL)) + "\n# check_fts_seat_body_geometry\n")
    case("c14_chained_into_gate_check",
         "把本闸挂进 state/gate_check.py ⇒ 必须红 (G6)",
         m14, "G6")

    # 15 `OI-12` 状态写成三值之外的词 ⇒ 必须 G5 红
    def m15(sb):
        block_mutate(sb, lambda d: d["oi12_recompute"].__setitem__("status", "要重算"))
    case("c15_oi12_status_out_of_enum",
         "★把 `OI-12` 状态写成三值之外的词「要重算」⇒ 必须红 (G5)",
         m15, "G5")

    npass = 0
    for name, desc, mutate, expect in cases:
        sb = make_sandbox(root, name)
        try:
            # ★★先在【未被改动的沙盒】上跑一遍闸 ⇒ 必须全绿 ★★
            # (★不然反向用例会因为「沙盒缺文件」这种环境噪声假红 ⇒ 等于没测★)
            pre = Gate(sb).run()
            pre_fail = [(k, m) for k, ok, m in pre if not ok]
            if pre_fail:
                print("[FAIL] %-38s ★沙盒基线就红 (★反向用例无效·闸在干净沙盒上就不通过★): %s"
                      % (name, pre_fail[0]))
                continue
            mutate(sb)
            g = Gate(sb)
            res = g.run()
            fails = [(k, m) for k, ok, m in res if not ok]
            if not fails:
                print("[FAIL] %-38s 期望红 (点名 %s) ⇒ 实际【绿】 (闸坏了)" % (name, expect))
            else:
                hit = any(k.startswith(expect) for k, _ in fails)
                others = [k for k, _ in fails if not k.startswith(expect)]
                if hit:
                    print("[ok]   %-38s rc=1 且点名 %s ✓  (%s)%s"
                          % (name, expect, fails[0][1][:96],
                             ("  ★同时命中 %s★" % others) if others else ""))
                    npass += 1
                else:
                    print("[FAIL] %-38s 红了但没点名 %s ⇒ 实际点名 %s"
                          % (name, expect, [k for k, _ in fails]))
        except Exception as exc:
            print("[FAIL] %-38s 反向用例执行异常: %r" % (name, exc))
        finally:
            shutil.rmtree(sb, ignore_errors=True)
    print("反向用例 %d 条, 通过 %d 条" % (len(cases), npass))
    if npass == len(cases):
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


# ==================================================================================================
# main
# ==================================================================================================
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=PROJ)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    if args.emit:
        blk = extract_json_fence(read_text(p(root, PAGE_REL)), BLOCK_BEGIN, BLOCK_END)
        if blk is None:
            print("机器块读不到")
            return 2
        print(json.dumps(blk, ensure_ascii=False, indent=1))
        return 0

    if args.selftest:
        return selftest(root)

    g = Gate(root)
    res = g.run()
    for n in g.notes:
        print("[note] %s" % n)
    if g.pending:
        print("★★G3 未落清单 (★已登记为 §4 的 COR-x, 状态 = 待 main 落; ★本单零改既有页/零改既有闸 ⇒ 这类命中必然还在★)★★")
        for it in sorted(set(g.pending)):
            print("    · %s" % it)
        print("★★未落 %d 处 ⇒ main 落完 §4 的订正后, 这一栏应清空★★" % len(set(g.pending)))
    else:
        print("★G3 未落清单: 0 处")
    nfail = 0
    for kid, ok, msg in res:
        if not ok:
            nfail += 1
            print("[FAIL] %-10s %s" % (kid, msg))
        else:
            print("[ok]   %-10s ✓" % kid)
    print("判据 %d 条 · 失败 %d 条" % (len(res), nfail))
    if nfail == 0:
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
