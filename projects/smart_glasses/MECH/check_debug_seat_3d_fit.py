#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_debug_seat_3d_fit.py —— ISS-386 · `J_DEBUG` + `J_UART` 座体/开口/必须清空区 【合一件答】机器闸
===================================================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零改已签收页 / 零外发 / 不代拍** ★
★**派活**: 项目总工 (main) · ISS-386 · 2026-11-24 派 / 做 · 交卷人 = 结构总工 (mech-lead) ★
★**关联页**: `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` (★本单新建的合一件答页★) ·
           `HANDOFF/2026-11-24_mech-lead_ISS386_JDEBUG与JUART座体开口清空区合一件答.md` (交卷页) ★
★**只读引用 (★不改★)**: `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (★开口/必须清空区真身★) ·
          `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` (★ISS-377 判据链·已签收★) ·
          `MECH/service_port_check.py` (★`CRIT` / `TOL` 真身 L126-L127★) ·
          `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` (★ISS-379 三候选落点·已签收·只读★) ★
★**★闸不挂 `state/gate_check.py` (★挂不挂归 main·本闸只自证「没挂」★)★**

────────────────────────────────────────────────────────────────────────────────────────────────────────
【★★本单要防的病根 (★ISS-379 签收裁决 ④⑤ 明确要求「合到一件答·别分两票」★)★★】
  ★**① 两连接器分两页各自绿** ⇒ K1 (两件必须同表 + 同字段 + 同判据) + 反向用例 07 ★
  ★**② `J_UART` 落点三选一被偷挑掉一个** ⇒ K2 (三候选必须齐全) + K10 (不许在本单落点) + 反向用例 01 / 09 ★
  ★**③ 帧依赖被悄悄写死** ⇒ K6 (帧 id 声明 + 坐标作废声明 + 帧无关结论必须存在) + 反向用例 02 / 10 ★
  ★**④ `CRIT`/`TOL` 被写死进页** ⇒ K5 (必须现场从 `MECH/service_port_check.py` 源码读 + 声明取法) + 反向用例 03 / 06 ★
  ★**⑤ 判决与实算相反 (把不过写成过)** ⇒ K4 (判决必须与按源码阈值重算的结果一致) + 反向用例 05 ★
  ★**⑥ 余量被抄表而不是实算** ⇒ K3 (每个数都由闸自己按公式重算 + 与页内机器块逐字相等) + 反向用例 04 ★
  ★**⑦ `J_DEBUG` 清空区 X 宽三值被偷偷挑一个** ⇒ K1b (三个竞争值必须齐全) + 反向用例 08 ★
  ★**⑧ 挂外部依赖 (等原厂回信)** ⇒ K8 (零挂链措辞 + 必须有降级方案) + 反向用例 12 ★

【同源判据链 (★闸自己复算·★不抄表★·★`CRIT`/`TOL` 现场从源码读★)】
  M = max(H_housing, C_copper) (逐轴)      · 开口余量 = (O_opening − M) / 2
  罩住余量 = (H_housing − C_copper) / 2      · 最坏余量 = 余量 − TOL["fdm_part"]
  判据: 最坏余量 ≥ CRIT   (★CRIT = 2 × TOL["fdm_part"]★)
  ★**实口径 (含绝对坐标, ★用于三个候选落点★)**: 罩住带符号余量 = min(C.x0−H.x0, H.x1−C.x1, C.y0−H.y0, H.y1−C.y1)
                                            开口带符号余量 = min((H∪C) 四边 vs O 四边) ★

【判据清单 (★每条 fail-closed·★每条都有反向用例★)】
  K0  机器块可解析 + 页内 §1/§2/§3 三节齐全 + 页内 §4 一致性结论存在
  K1  ★两连接器同表 (同一张 markdown 表里同时出现 J_DEBUG 与 J_UART, 行数/字段数一致)★
  K1b ★`J_DEBUG` 清空区 X 宽三个竞争值 (1.7750 / 4.0850 / 4.8100) 齐全★
  K2  ★`J_UART` 三个候选落点全部有判决 (少一个就红)★
  K3  每个余量 = 闸自己按公式实算, 与机器块逐字相等 (最坏 = 余量 − TOL)
  K4  判决与实算不相反 (不许把不过写成过)
  K5  `CRIT`/`TOL` 取法声明存在 + 闸从源码读到 + 页内声明值 == 源码值
  K6  帧 id 声明存在 + 「坐标随上位问题作废」声明存在 + 帧无关结论存在
  K7  证据等级齐全 (每行/每候选都带 [实测]/[推算]/[0数据] 之一)
  K8  零挂链 (无「等原厂回信 / 等外部回复 / 待外部确认」) + 降级方案 ≥ 3 条
  K9  板/网表/BOM 指纹 == 基线 (零写板 · 零落表)
  K10 ★本页不许替 main 落点 (`landing_point_decision` 必须是 not_decided_here)★

【rc 语义】
  0 = 全部通过   ·   1 = 有断言不通过 (逐条列出 + 点名判据号)   ·   2 = 参数 / IO 错误

【用法】
  python3 MECH/check_debug_seat_3d_fit.py             # 扫真件 (只读)
  python3 MECH/check_debug_seat_3d_fit.py --emit      # 打印机器块 JSON (供页内粘贴)
  python3 MECH/check_debug_seat_3d_fit.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_debug_seat_3d_fit.py --root DIR  # 扫指定树 (反向用例在 tmp/iss386_sbx/selftest/ 上做)

【★沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss386_sbx/selftest/` (★不许写系统 `/tmp`★·★不许用硬链接★)
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

PAGE_REL = "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md"
OPENING_REL = "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md"
CALIBER_REL = "MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md"
CRIT_REL = "MECH/service_port_check.py"
LAND_FIT_REL = "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md"
GATE_REL = "state/gate_check.py"
PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"
NETLIST_REL = "HW/netlist_v1.csv"
PINS_REL = "HW/netlist_v1_pins.csv"
BOM_REL = "HW/BOM_v1.csv"

BLOCK_BEGIN = "<!-- MECH-DEBUG-SEAT-3D-FIT-JSON-BEGIN -->"
BLOCK_END = "<!-- MECH-DEBUG-SEAT-3D-FIT-JSON-END -->"

BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime": "2026-11-06 07:07:17.362193413",
    "size": 4940213,
}
TABLE_BASELINE = {
    NETLIST_REL: "6aee500e60ba0732f83a9cf557ba90ab",
    PINS_REL: "9174309df1ec9411ac8e8d9e80ee386a",
    BOM_REL: "5b9993992405904a60ac96a020b375d8",
}

FRAME_ID = "B160x100"
KICAD_LIB = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty"
FOOTPRINT_FILE = {
    "J_DEBUG": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
    "J_UART": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
}

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_PENDING = ("等原厂回信", "等外部回复", "待外部确认", "等厂商回复", "待原厂确认")

# ★`J_DEBUG` 的三个竞争值 (★ISS-377 C3 登记的三个数·★本单只摆事实不裁决★)★
DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)


# ==================================================================================================
# 通用工具
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def p(root: str, rel: str) -> str:
    return os.path.join(root, rel)


def strip_md(s: str) -> str:
    return s.replace("*", "").replace("`", "")


def r4(x) -> float:
    return round(float(x) + 0.0, 4)


def parse_xy(s: str):
    """从 'X 142.063..143.838 × Y 55.330..57.870' 抠两个区间"""
    s = strip_md(s)
    m = re.search(r"X\s*(-?\d+(?:\.\d+)?)\s*\.\.\s*(-?\d+(?:\.\d+)?)", s)
    if not m:
        return None
    m2 = re.search(r"Y\s*(-?\d+(?:\.\d+)?)\s*\.\.\s*(-?\d+(?:\.\d+)?)", s)
    if not m2:
        return None
    return ((float(m.group(1)), float(m.group(2))), (float(m2.group(1)), float(m2.group(2))))


def find_row(text: str, key: str, forbid=()) -> str:
    for ln in text.splitlines():
        s = strip_md(ln)
        if key in s and not any(f in s for f in forbid):
            return s
    return ""


def extract_json_fence(text: str, begin: str, end: str):
    i = text.find(begin)
    j = text.find(end)
    if i < 0 or j < 0:
        return None
    seg = text[i:j]
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", seg, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def read_crit(root: str):
    """★CRIT / TOL 真身 (只读源码·★不许写死·★不许 import·★本机实读)★"""
    src = read_text(p(root, CRIT_REL))
    mt = re.search(r"TOL\s*=\s*\{[^}]*\}", src)
    if not mt:
        return None, None, "TOL 真身 (MECH/service_port_check.py) 没找到"
    tol = eval(mt.group(0).split("=", 1)[1])
    mc = re.search(r"CRIT\s*=\s*2\s*\*\s*TOL\[\"fdm_part\"\]", src)
    if not mc:
        return None, None, "CRIT 真身 (CRIT = 2 * TOL['fdm_part']) 没找到"
    return 2 * tol["fdm_part"], tol, None


def parse_footprint_copper(path: str):
    """★从官方 .kicad_mod 解析 pad → rot90 (沿板 X 排) 的铜箔包络 (X 宽, Y 宽)★"""
    if not os.path.isfile(path):
        return None
    src = read_text(path)
    pads = []
    for m in re.finditer(r"\(pad\s+\"([^\"]+)\"[^\n]*?\n", src):
        blk = src[m.start():m.start() + 400]
        if "thru_hole" not in blk and "smd" not in blk:
            continue
        at = re.search(r"\(at\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\)", blk)
        sz = re.search(r"\(size\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\)", blk)
        if not at or not sz:
            continue
        pads.append((float(at.group(1)), float(at.group(2)),
                     float(sz.group(1)), float(sz.group(2))))
    if not pads:
        return None
    ys = [q[1] for q in pads]
    xs = [q[0] for q in pads]
    max_w = max(q[2] for q in pads)
    max_h = max(q[3] for q in pads)
    # 针排沿封装局部 Y ⇒ 摆成板上 X 向直排 = rot 90
    span_local_y = max(ys) - min(ys)
    return {
        "pads": len(pads),
        "copper_x": r4(span_local_y + max_w),
        "copper_y": r4(max_h),
        "span_local_y": r4(span_local_y),
    }


# ==================================================================================================
# 事实读取
# ==================================================================================================
class Facts(object):
    def __init__(self, root: str):
        self.root = root
        self.errors = []
        self.page = read_text(p(root, PAGE_REL))
        self.block = extract_json_fence(self.page, BLOCK_BEGIN, BLOCK_END)
        self.opening_text = read_text(p(root, OPENING_REL))
        self.caliber_text = read_text(p(root, CALIBER_REL))
        self.land_fit_text = read_text(p(root, LAND_FIT_REL))
        self.crit, self.tol, err = read_crit(root)
        if err:
            self.errors.append(err)

    def housing_opening(self):
        """★从既有真相页 (只读) 重新读一遍 H / O —— 不许抄自己页里的数★"""
        out = {}
        for key, ref in (("J_DEBUG", "调试口"), ("J_UART", "检修口")):
            hrow = find_row(self.opening_text, ref + " · 必须清空区", forbid=("可放行",))
            orow = find_row(self.opening_text, ref + " · 开口", forbid=("可放行", "必须清空区"))
            hxy, oxy = parse_xy(hrow), parse_xy(orow)
            if not hxy or not oxy:
                self.errors.append("既有真相页里找不到 %s 的必须清空区 / 开口行" % key)
                continue
            out[key] = {
                "housing": {"x0": hxy[0][0], "x1": hxy[0][1], "y0": hxy[1][0], "y1": hxy[1][1]},
                "housing_w": {"x": r4(hxy[0][1] - hxy[0][0]), "y": r4(hxy[1][1] - hxy[1][0])},
                "opening": {"x0": oxy[0][0], "x1": oxy[0][1], "y0": oxy[1][0], "y1": oxy[1][1]},
                "opening_w": {"x": r4(oxy[0][1] - oxy[0][0]), "y": r4(oxy[1][1] - oxy[1][0])},
                "src_h": strip_md(hrow).strip()[:200],
                "src_o": strip_md(orow).strip()[:200],
            }
        return out


# ==================================================================================================
# 判据计算 (★闸自己算·★不抄表★)
# ==================================================================================================
def compute_row(row, crit, tol_fdm):
    """按 ISS-377 §0.1 判据链重算一行 ⇒ 返回【扁平】结果 (margin_open.x / margin_open.y ...)"""
    c = row["copper"]
    h = row["housing_w"]
    o = row["opening_w"]
    out = {"M": {}, "margin_open": {}, "worst_open": {}, "pass_open": {},
           "margin_cover": {}, "worst_cover": {}, "pass_cover": {}, "cover_tautology": {}}
    for ax in ("x", "y"):
        M = max(h[ax], c[ax])
        m_open = r4((o[ax] - M) / 2.0)
        m_cov = r4((h[ax] - c[ax]) / 2.0)
        w_open = r4(m_open - tol_fdm)
        w_cov = r4(m_cov - tol_fdm)
        out["M"][ax] = r4(M)
        out["margin_open"][ax] = m_open
        out["worst_open"][ax] = w_open
        out["pass_open"][ax] = bool(w_open >= crit - 1e-9)
        out["margin_cover"][ax] = m_cov
        out["worst_cover"][ax] = w_cov
        out["pass_cover"][ax] = bool(w_cov >= crit - 1e-9)
        out["cover_tautology"][ax] = bool(abs(h[ax] - c[ax]) < 1e-9)
    out["verdict_cover"] = ("红" if not (out["pass_cover"]["x"] and out["pass_cover"]["y"])
                            else "绿")
    out["verdict_open"] = ("红" if not (out["pass_open"]["x"] and out["pass_open"]["y"])
                           else "绿")
    return out


def signed_gaps(c, h):
    """★实口径: 铜箔 bbox 相对清空区四边的带符号余量 (负 = 伸出)★"""
    return {
        "x0": r4(c["x0"] - h["x0"]),
        "x1": r4(h["x1"] - c["x1"]),
        "y0": r4(c["y0"] - h["y0"]),
        "y1": r4(h["y1"] - c["y1"]),
    }


def union_rect(a, b):
    return {
        "x0": min(a["x0"], b["x0"]), "x1": max(a["x1"], b["x1"]),
        "y0": min(a["y0"], b["y0"]), "y1": max(a["y1"], b["y1"]),
    }


def open_gaps(inner, o):
    return {
        "x0": r4(inner["x0"] - o["x0"]),
        "x1": r4(o["x1"] - inner["x1"]),
        "y0": r4(inner["y0"] - o["y0"]),
        "y1": r4(o["y1"] - inner["y1"]),
    }


def compute_candidate(cand, ho, crit, tol_fdm):
    """★逐候选落点: 罩住实口径 + 开口实口径★"""
    c = cand["copper_bbox"]
    h = ho["housing"]
    o = ho["opening"]
    sg = signed_gaps(c, h)
    cover_signed = r4(min(sg.values()))
    cover_worst = r4(cover_signed - tol_fdm)
    uni = union_rect(h, c)
    og = open_gaps(uni, o)
    open_signed = r4(min(og.values()))
    open_worst = r4(open_signed - tol_fdm)
    return {
        "cover_signed": cover_signed,
        "cover_worst": cover_worst,
        "cover_pass": bool(cover_worst >= crit - 1e-9),
        "cover_gaps": sg,
        "open_signed": open_signed,
        "open_worst": open_worst,
        "open_pass": bool(open_worst >= crit - 1e-9),
        "open_gaps": og,
        "union_bbox": {"x0": uni["x0"], "x1": uni["x1"], "y0": uni["y0"], "y1": uni["y1"]},
    }


# ==================================================================================================
# 判据 K0~K10
# ==================================================================================================
class Gate(object):
    def __init__(self, root: str):
        self.root = root
        self.f = Facts(root)
        self.results = []
        self.notes = []

    def chk(self, kid, ok, msg):
        self.results.append((kid, bool(ok), msg))
        return bool(ok)

    # ---------------- K0 ----------------
    def k0(self):
        if not self.chk("K0.1", self.f.block is not None, "机器块 (JSON) 缺失或不可解析"):
            return
        for sec in ("§1", "§2", "§3", "§4", "§5", "§6"):
            self.chk("K0.2", sec in self.f.page, "页内缺节: %s" % sec)
        for key in ("rows", "j_debug_clearance_x_candidates", "j_uart_candidates",
                    "criterion", "frame_id", "landing_point_decision"):
            self.chk("K0.3", key in self.f.block, "机器块缺字段: %s" % key)

    # ---------------- K1 (同表) ----------------
    def k1(self):
        page = self.f.page
        # 找 markdown 表: 连续以 '|' 开头的行
        blocks, cur = [], []
        for ln in page.splitlines():
            if ln.lstrip().startswith("|"):
                cur.append(ln)
            else:
                if cur:
                    blocks.append(cur)
                cur = []
        if cur:
            blocks.append(cur)
        hit = [b for b in blocks if "J_DEBUG" in "\n".join(b) and "J_UART" in "\n".join(b)]
        self.chk("K1.1", len(hit) >= 1,
                 "★两连接器必须同表: 没找到同时含 J_DEBUG 与 J_UART 的同一张 markdown 表 (共 %d 张表)" % len(blocks))
        if not hit:
            return
        tbl = hit[0]
        ncol = len([c for c in tbl[0].strip().strip("|").split("|")])
        data = [ln for ln in tbl[1:]
                if not set(ln.strip().strip("|").replace(" ", "").replace("|", "")) <= set("-:")]
        refs = []
        for ln in data:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            refs.append((strip_md(cells[0]), strip_md(cells[1]) if len(cells) > 1 else ""))
            self.chk("K1.2", len(cells) == ncol,
                     "同源表行字段数不一致: 行 %r 有 %d 格, 表头 %d 格" % (cells[0], len(cells), ncol))
        want = {("J_DEBUG", "status_quo"), ("J_DEBUG", "official_tht"),
                ("J_UART", "status_quo"), ("J_UART", "official_tht")}
        got = set(refs)
        self.chk("K1.3", want <= got,
                 "同源表缺行: 缺 %s (实有 %s)" % (sorted(want - got), sorted(got)))
        self.chk("K1.4", len(data) == len(want),
                 "同源表行数 %d ≠ 期望 %d (两连接器 × 两档)" % (len(data), len(want)))
        # K1.5 页内 markdown 行的关键数必须与机器块逐字相等 (同源)
        blk_rows = {(r.get("ref"), r.get("tier")): r for r in (self.f.block.get("rows") or [])}
        for ln in data:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            key = (strip_md(cells[0]), strip_md(cells[1]))
            br = blk_rows.get(key)
            if not br:
                continue
            need = []
            for fld in ("margin_open", "margin_cover", "worst_open", "worst_cover"):
                for ax in ("x", "y"):
                    need.append("%0.4f" % float(br[fld][ax]))
            missing = [v for v in need if v not in strip_md(ln)]
            self.chk("K1.5", not missing,
                     "同源表行 %s 的余量数与机器块不一致: 缺 %s" % (key, missing))
        # 同判据: 页内必须出现 CRIT/TOL 取法声明, 且与源码一致
        self.k5()

    # ---------------- K1b (三个竞争值齐全) ----------------
    def k1b(self):
        cands = self.f.block.get("j_debug_clearance_x_candidates") or []
        vals = tuple(sorted(r4(c.get("value")) for c in cands))
        self.chk("K1b.1", vals == tuple(sorted(DEBUG_CLEAR_X)),
                 "★`J_DEBUG` 清空区 X 宽三个竞争值必须齐全: 实有 %s, 期望 %s"
                 % (list(vals), list(DEBUG_CLEAR_X)))
        for c in cands:
            self.chk("K1b.2", "cost" in c and c.get("cost"),
                     "清空区候选值 %s 缺代价说明 (cost)" % c.get("value"))
        for v in DEBUG_CLEAR_X:
            self.chk("K1b.3", ("%0.4f" % v) in strip_md(self.f.page),
                     "页内正文找不到清空区竞争值 %0.4f (三个竞争值必须在正文里一起摆)" % v)

    # ---------------- K2 (三候选齐全) ----------------
    def k2(self):
        cands = self.f.block.get("j_uart_candidates") or []
        self.chk("K2.1", len(cands) == 3,
                 "★`J_UART` 三个候选落点必须全部有判决: 实有 %d 个 (期望 3)" % len(cands))
        expect_pts = [("270", 18.6, 68.6), ("90", 18.4, 68.4), ("90", 18.3, 68.6)]
        for c in cands:
            key = (str(c.get("rot")), r4(c.get("pad1_x")), r4(c.get("pad1_y")))
            self.chk("K2.2", key in expect_pts,
                     "候选落点不在 ISS-379 已签收的三个里: %s (期望 %s)" % (key, expect_pts))
            self.chk("K2.3", c.get("verdict") is not None,
                     "候选落点 %s 缺判决 (verdict)" % (key,))
            self.chk("K2.4", c.get("copper_bbox") is not None,
                     "候选落点 %s 缺 copper_bbox" % (key,))

    # ---------------- K3 (实算 = 机器块) ----------------
    def k3(self):
        crit, tol = self.f.crit, self.f.tol
        if crit is None:
            self.chk("K3.0", False, "CRIT/TOL 读不到 (源码被改坏?)")
            return
        tol_fdm = tol["fdm_part"]
        ho = self.f.housing_opening()
        for row in self.f.block.get("rows") or []:
            key = (row.get("ref"), row.get("tier"))
            res = compute_row(row, crit, tol_fdm)
            for ax in ("x", "y"):
                for fld in ("margin_open", "worst_open", "margin_cover", "worst_cover"):
                    want = res[fld][ax]
                    got = row.get(fld, {}).get(ax)
                    self.chk("K3.1", got is not None and abs(float(got) - want) <= 1e-9,
                             "%s %s 轴 %s: 页内 %s ≠ 闸实算 %s" % (key[0], key[1], ax, got, want))
                for fld, src in (("pass_open", "pass_open"), ("pass_cover", "pass_cover")):
                    got = row.get(fld, {}).get(ax)
                    want = res[src][ax]
                    self.chk("K3.2", bool(got) == bool(want),
                             "%s %s 轴 %s 判决: 页内 %s ≠ 实算 %s" % (key[0], key[1], ax, got, want))
            # H / O 必须与既有真相页一致 (独立源)
            if key[0] in ho:
                for fld in ("housing", "opening"):
                    a = row.get(fld) or {}
                    b = ho[key[0]][fld]
                    same = all(abs(float(a.get(ax, 1e9)) - float(b[ax])) <= 1e-6 for ax in ("x0", "x1", "y0", "y1"))
                    self.chk("K3.3", same,
                             "%s 的 %s 与既有真相页 MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 不一致" % (key[0], fld))
        # 三个候选逐个实算
        for c in self.f.block.get("j_uart_candidates") or []:
            if c.get("ref") not in ho or not c.get("copper_bbox"):
                continue
            res = compute_candidate(c, ho[c["ref"]], crit, tol_fdm)
            for fld in ("cover_signed", "cover_worst", "open_signed", "open_worst"):
                want = res[fld]
                got = c.get(fld)
                self.chk("K3.4", got is not None and abs(float(got) - want) <= 1e-9,
                         "候选 %s %s: 页内 %s ≠ 闸实算 %s" % (c.get("name"), fld, got, want))
            self.chk("K3.5", bool(c.get("cover_pass")) == bool(res["cover_pass"]),
                     "候选 %s 罩住判决: 页内 %s ≠ 实算 %s" % (c.get("name"), c.get("cover_pass"), res["cover_pass"]))
            self.chk("K3.6", bool(c.get("open_pass")) == bool(res["open_pass"]),
                     "候选 %s 开口判决: 页内 %s ≠ 实算 %s" % (c.get("name"), c.get("open_pass"), res["open_pass"]))
        # 三个清空区竞争值逐个实算
        for c in self.f.block.get("j_debug_clearance_x_candidates") or []:
            want_cover = r4((float(c["value"]) - 4.81) / 2.0)
            want_worst = r4(want_cover - tol_fdm)
            got_cover = c.get("margin_cover_x")
            got_worst = c.get("worst_cover_x")
            self.chk("K3.7", got_cover is not None and abs(float(got_cover) - want_cover) <= 1e-9,
                     "清空区候选 %s 罩住余量: 页内 %s ≠ 实算 %s" % (c.get("value"), got_cover, want_cover))
            self.chk("K3.8", got_worst is not None and abs(float(got_worst) - want_worst) <= 1e-9,
                     "清空区候选 %s 最坏余量: 页内 %s ≠ 实算 %s" % (c.get("value"), got_worst, want_worst))

    # ---------------- K4 (判决不许反) ----------------
    def k4(self):
        crit = self.f.crit
        if crit is None:
            return
        for row in self.f.block.get("rows") or []:
            key = "%s %s" % (row.get("ref"), row.get("tier"))
            verdict = str(row.get("verdict") or "")
            self.chk("K4.0", ("罩住" in verdict) and ("开口" in verdict),
                     "%s 判决串必须同时写清「罩住」与「开口」两段: %r" % (key, verdict))
            if "罩住红" in verdict:
                bad = [ax for ax in ("x", "y") if row.get("pass_cover", {}).get(ax) is True]
                self.chk("K4.1", not bad,
                         "%s 罩住段写了「红」, 但 %s 实算为过 ⇒ 判决与实算相反" % (key, bad))
            if "罩住绿" in verdict:
                bad = [ax for ax in ("x", "y") if row.get("pass_cover", {}).get(ax) is False]
                self.chk("K4.2", not bad,
                         "%s 罩住段写了「绿」, 但 %s 实算为不过 ⇒ 判决与实算相反" % (key, bad))
            if "开口红" in verdict:
                bad = [ax for ax in ("x", "y") if row.get("pass_open", {}).get(ax) is True]
                self.chk("K4.3", not bad,
                         "%s 开口段写了「红」, 但 %s 实算为过 ⇒ 判决与实算相反" % (key, bad))
            if "开口绿" in verdict:
                bad = [ax for ax in ("x", "y") if row.get("pass_open", {}).get(ax) is False]
                self.chk("K4.4", not bad,
                         "%s 开口段写了「绿」, 但 %s 实算为不过 ⇒ 判决与实算相反" % (key, bad))
        for c in self.f.block.get("j_uart_candidates") or []:
            self.chk("K4.5", c.get("cover_pass") is not None and c.get("open_pass") is not None,
                     "候选 %s 缺判决布尔量" % c.get("name"))
            self.chk("K4.6", ("罩住" in str(c.get("verdict"))) and ("开口" in str(c.get("verdict"))),
                     "候选 %s 判决串必须同时写清「罩住」与「开口」两段" % c.get("name"))
            if "罩住红" in str(c.get("verdict")):
                self.chk("K4.7", c.get("cover_pass") is False,
                         "候选 %s 罩住段写了「红」但布尔量为 %s" % (c.get("name"), c.get("cover_pass")))
            if "开口绿" in str(c.get("verdict")):
                self.chk("K4.8", c.get("open_pass") is True,
                         "候选 %s 开口段写了「绿」但布尔量为 %s" % (c.get("name"), c.get("open_pass")))

    # ---------------- K5 (CRIT/TOL 取法) ----------------
    def k5(self):
        crit, tol = self.f.crit, self.f.tol
        if crit is None:
            self.chk("K5.1", False, "CRIT/TOL 读不到")
            return
        tol_fdm = tol["fdm_part"]
        crit_decl = (self.f.block.get("criterion") or {}).get("crit_source", "")
        self.chk("K5.1", "service_port_check.py" in crit_decl,
                 "机器块缺 CRIT/TOL 取法声明 (必须指向 MECH/service_port_check.py 源码): %r" % crit_decl)
        self.chk("K5.2", "TOL" in crit_decl and "fdm_part" in crit_decl,
                 "CRIT/TOL 取法声明必须写明 TOL['fdm_part']: %r" % crit_decl)
        decl_crit = (self.f.block.get("criterion") or {}).get("crit_value")
        self.chk("K5.3", decl_crit is not None and abs(float(decl_crit) - crit) <= 1e-9,
                 "页内声明的 CRIT %s ≠ 源码实读 %s (阈值改了必须跟着改声明)" % (decl_crit, crit))
        decl_tol = (self.f.block.get("criterion") or {}).get("tol_fdm_part")
        self.chk("K5.4", decl_tol is not None and abs(float(decl_tol) - tol_fdm) <= 1e-9,
                 "页内声明的 TOL['fdm_part'] %s ≠ 源码实读 %s" % (decl_tol, tol_fdm))
        # 页内正文必须出现源码路径
        self.chk("K5.5", "MECH/service_port_check.py" in self.f.page,
                 "页内正文未引用 CRIT/TOL 真身路径 MECH/service_port_check.py")

    # ---------------- K6 (帧依赖) ----------------
    def k6(self):
        page = self.f.page
        fid = self.f.block.get("frame_id")
        self.chk("K6.1", fid == FRAME_ID,
                 "★机器块 frame_id %r ≠ %r (帧 id 写错/被改)" % (fid, FRAME_ID))
        self.chk("K6.2", FRAME_ID in page, "页内正文未写明帧 id %s" % FRAME_ID)
        self.chk("K6.3", ("作废" in page) or ("失效" in page),
                 "页内缺『若上位问题落乙 ⇒ 三个候选坐标全部作废』的声明")
        fi = self.f.block.get("frame_independent") or {}
        self.chk("K6.4", bool(fi.get("statements")),
                 "机器块缺帧无关结论 (frame_independent.statements)")
        for st in fi.get("statements") or []:
            self.chk("K6.5", bool(st.get("text")) and bool(st.get("basis")),
                     "帧无关结论缺 text/basis: %r" % st)

    # ---------------- K7 (证据等级) ----------------
    def k7(self):
        blk = self.f.block or {}
        used = set(blk.get("evidence_levels_used") or [])
        self.chk("K7.1", used and all(u in EVIDENCE_WHITELIST for u in used),
                 "证据等级白名单越界: %s" % sorted(used))
        for row in blk.get("rows") or []:
            ev = row.get("evidence") or ""
            self.chk("K7.2", any(e in ev for e in EVIDENCE_WHITELIST),
                     "%s %s 行缺证据等级" % (row.get("ref"), row.get("tier")))
        for c in blk.get("j_uart_candidates") or []:
            ev = c.get("evidence") or ""
            self.chk("K7.3", any(e in ev for e in EVIDENCE_WHITELIST),
                     "候选 %s 缺证据等级" % c.get("name"))
        for c in blk.get("j_debug_clearance_x_candidates") or []:
            ev = c.get("evidence") or ""
            self.chk("K7.4", any(e in ev for e in EVIDENCE_WHITELIST),
                     "清空区候选 %s 缺证据等级" % c.get("value"))

    # ---------------- K8 (零挂链 + 降级方案) ----------------
    def k8(self):
        page = self.f.page
        for w in FORBIDDEN_PENDING:
            self.chk("K8.1", w not in page, "页内出现挂起措辞: %r (禁止把外部依赖挂着当阻塞项)" % w)
        dp = self.f.block.get("degrade_plans") or []
        self.chk("K8.2", len(dp) >= 3, "降级方案少于 3 条 (查不到处必须给降级方案): %d" % len(dp))
        for d in dp:
            self.chk("K8.3", d.get("cost") and d.get("basis"),
                     "降级方案 %s 缺 basis/cost" % d.get("id"))
        for w in ("发邮件", "询价", "采购询问", "等待原厂"):
            self.chk("K8.4", w not in page, "页内出现外发措辞: %r (本单零外发)" % w)

    # ---------------- K9 (零写板 / 零落表) ----------------
    def k9(self):
        pcb = p(self.root, PCB_REL)
        if os.path.isfile(pcb):
            self.chk("K9.1", md5_of(pcb) == BOARD_BASELINE["md5"],
                     "板 md5 %s ≠ 基线 %s (零写板被破坏)" % (md5_of(pcb), BOARD_BASELINE["md5"]))
            self.chk("K9.2", os.path.getsize(pcb) == BOARD_BASELINE["size"],
                     "板 size %d ≠ 基线 %d" % (os.path.getsize(pcb), BOARD_BASELINE["size"]))
        else:
            self.notes.append("K9.1/K9.2 跳过 (沙盒无板文件)")
        for rel, want in TABLE_BASELINE.items():
            f = p(self.root, rel)
            if os.path.isfile(f):
                self.chk("K9.3", md5_of(f) == want,
                         "%s md5 %s ≠ 基线 %s (零落表被破坏)" % (rel, md5_of(f), want))
            else:
                self.notes.append("K9.3 跳过 (沙盒无 %s)" % rel)

    # ---------------- K10 (不许替 main 落点) ----------------
    def k10(self):
        d = self.f.block.get("landing_point_decision")
        self.chk("K10.1", d == "not_decided_here",
                 "★本页不许替 main 落点: landing_point_decision = %r (必须是 not_decided_here)" % d)
        for c in self.f.block.get("j_uart_candidates") or []:
            self.chk("K10.2", not c.get("chosen"),
                     "候选 %s 被标成 chosen (落点裁决权在 main·已被 ISS-379 挂起)" % c.get("name"))
        oi = self.f.block.get("open_items") or {}
        self.chk("K10.3", any("OI" in str(k) for k in oi.keys()),
                 "机器块缺未决项登记 (open_items)")
        txt = self.f.page
        self.chk("K10.4", "OI-5" in txt,
                 "页内未登记 OI-5 (`J_DEBUG` 清空区 X 宽以哪个数为准 ⇒ to=main)")

    # ---------------- 零挂链 (自证) ----------------
    def kchain(self):
        g = p(self.root, GATE_REL)
        if not os.path.isfile(g):
            self.notes.append("KCHAIN 跳过 (沙盒无 state/gate_check.py)")
            return
        txt = read_text(g)
        self.chk("KCHAIN", "check_debug_seat_3d_fit" not in txt,
                 "★本闸被挂进了 state/gate_check.py (本单零挂链·挂不挂归 main)")

    def run(self):
        for f in (self.k0, self.k1, self.k1b, self.k2, self.k3, self.k4, self.k5,
                  self.k6, self.k7, self.k8, self.k9, self.k10, self.kchain):
            try:
                f()
            except Exception as exc:  # fail-closed
                self.chk(f.__name__.upper(), False, "判据执行异常 (fail-closed): %r" % exc)
        return self.results


# ==================================================================================================
# 机器块生成 (--emit)
# ==================================================================================================
def build_block():
    """★按只读真源重算, 生成机器块 (★闸自己算·★不抄表★)★"""
    crit, tol, err = read_crit(PROJ)
    if err:
        raise SystemExit(err)
    tol_fdm = tol["fdm_part"]
    ho = Facts(PROJ).housing_opening()

    rows = []
    # ---- 现状档 ----
    status = {
        "J_DEBUG": {"copper": {"x": 1.775, "y": 0.9},
                    "land": "SMD 4 pad, pitch 0.50, 0.275x0.900 自绘占位 (lib_id 空)",
                    "src": "logs/iss377/board_connectors.json J_DEBUG; MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L183/L184"},
        "J_UART": {"copper": {"x": 0.775, "y": 0.9},
                   "land": "SMD 2 pad, pitch 0.50, 0.275x0.900 自绘占位 (lib_id 空)",
                   "src": "logs/iss377/board_connectors.json J_UART; MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L196/L197"},
    }
    official = {
        "J_DEBUG": {"copper": {"x": 4.81, "y": 1.0},
                    "land": "Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical (THT)",
                    "src": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §0.1 + §1.1 (ISS-371 已签收)"},
        "J_UART": {"copper": {"x": 2.27, "y": 1.0},
                   "land": "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical (THT)",
                   "src": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md §1.2 (ISS-374 已签收)"},
    }
    for tier, table in (("status_quo", status), ("official_tht", official)):
        for ref in ("J_DEBUG", "J_UART"):
            t = table[ref]
            row = {
                "ref": ref,
                "tier": tier,
                "land": t["land"],
                "copper": t["copper"],
                "housing": ho[ref]["housing"],
                "opening": ho[ref]["opening"],
                "housing_w": ho[ref]["housing_w"],
                "opening_w": ho[ref]["opening_w"],
                "evidence": "[实测](输入) + [推算](余量)",
                "source_refs": [t["src"]],
                "open_items": [],
            }
            row.update(compute_row(row, crit, tol_fdm))
            row["caliber_source_axes"] = {
                "x": "copper_driven" if abs(row["housing_w"]["x"] - row["copper"]["x"]) < 1e-9
                     else ("housing_driven" if row["housing_w"]["x"] > row["copper"]["x"] else "copper_driven"),
                "y": "copper_driven" if abs(row["housing_w"]["y"] - row["copper"]["y"]) < 1e-9
                     else ("housing_driven" if row["housing_w"]["y"] > row["copper"]["y"] else "copper_driven"),
            }
            if ref == "J_DEBUG" and tier == "official_tht":
                row["open_items"] = ["OI-5", "OI-7"]
            if ref == "J_UART":
                row["open_items"] = ["OI-1", "OI-5b"] if tier == "official_tht" else ["OI-1"]
            cover_txt = "红" if not (row["pass_cover"]["x"] and row["pass_cover"]["y"]) else "绿"
            open_txt = "红" if not (row["pass_open"]["x"] and row["pass_open"]["y"]) else "绿"
            row["verdict"] = "罩住%s / 开口%s" % (cover_txt, open_txt)
            row["verdict_detail"] = {
                "cover_failed_axes": [ax.upper() for ax in ("x", "y") if not row["pass_cover"][ax]],
                "open_failed_axes": [ax.upper() for ax in ("x", "y") if not row["pass_open"][ax]],
                "cover_tautology_axes": [ax.upper() for ax in ("x", "y") if row["cover_tautology"][ax]],
            }
            row["notes"] = ("罩住X 为同义反复 (Hx == Cx ⇒ 座体宽是拿铜箔宽冒充的) ⇒ 不作判据; "
                            "换官方 land 后该轴立刻变成真判据" if row["cover_tautology"]["x"] else "")
            rows.append(row)

    # ---- `J_DEBUG` 清空区 X 宽三个竞争值 ----
    clear_src = {
        1.7750: "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (真相页·座体宽 = 板读铜箔宽)",
        4.0850: "MECH/BOARD_ONEPASS_MECH_SYNC.md L561 / MECH/BOARD_ONEPASS_MECH_CLAIMS.md L50 / "
                "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md L175 (现页四处·3.81 + 0.275)",
        4.8100: "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §0.1 (官方 THT 真 land·3.81 + 1.00)",
    }
    clear_costs = {
        1.7750: "结构件按此数出件 ⇒ 换官方 THT 后铜箔每边超出清空区 1.5175 ⇒ 几何上当场干涉 ⇒ "
                "清空区 X 至少要放到 4.8100 (+3.0350 总宽); 若还要过罩住判据 ⇒ 需 6.6100 (+4.8350)",
        4.0850: "结构件按此数出件 ⇒ 换官方 THT 后铜箔每边超出清空区 0.3625 ⇒ 仍干涉 ⇒ "
                "清空区 X 至少要放到 4.8100 (+0.7250 总宽); 若还要过罩住判据 ⇒ 需 6.6100 (+2.5250)",
        4.8100: "结构件按此数出件 ⇒ 换官方 THT 后铜箔与清空区齐平 (每边超出 0.0000) ⇒ 几何上不干涉, "
                "但罩住余量 0.0000 ⇒ 最坏 -0.3000 < CRIT ⇒ 判据上仍红 ⇒ 过判据仍需 6.6100 (+1.8000)",
    }
    clear_rows = []
    for v in DEBUG_CLEAR_X:
        mc = r4((v - 4.81) / 2.0)
        mw = r4(mc - tol_fdm)
        clear_rows.append({
            "value": v,
            "source": clear_src[v],
            "margin_cover_x": mc,
            "worst_cover_x": mw,
            "protrusion_per_side": r4(max(0.0, (4.81 - v) / 2.0)),
            "verdict": "红" if mw < crit - 1e-9 else "绿",
            "cost": clear_costs[v],
            "evidence": "[实测](取值出处) + [推算](余量)",
            "open_items": ["OI-5"],
        })

    # ---- `J_UART` 三个候选落点 (ISS-379 §2.3 已签收·只读引用)★ ----
    cand_defs = [
        ("C1", 270, 18.6, 68.6, 0.04, 0.2750,
         "rot 270 · pad1 (18.6000, 68.6000) · 板侧余量 0.2750 · pad1 位移 0.0400"),
        ("C2", 90, 18.4, 68.4, 0.3124, 0.1155,
         "rot 90 · pad1 (18.4000, 68.4000) · 板侧余量 0.1155 · pad1 位移 0.3124"),
        ("C3", 90, 18.3, 68.6, 0.34, 0.0447,
         "rot 90 · pad1 (18.3000, 68.6000) · 板侧余量 0.0447 · pad1 位移 0.3400"),
    ]
    # 官方 1x02 THT rot90 / rot270 的局部铜箔包络 (ISS-379 §9 CU 块)
    cu_local = {90: {"x0": -0.5, "x1": 1.77, "y0": -0.5, "y1": 0.5},
                270: {"x0": -1.77, "x1": 0.5, "y0": -0.5, "y1": 0.5}}
    cands = []
    for name, rot, px, py, disp, board_margin, desc in cand_defs:
        loc = cu_local[rot]
        bbox = {"x0": r4(px + loc["x0"]), "x1": r4(px + loc["x1"]),
                "y0": r4(py + loc["y0"]), "y1": r4(py + loc["y1"])}
        c = {"name": name, "ref": "J_UART", "rot": rot,
             "pad1_x": px, "pad1_y": py,
             "pad1_displacement": disp,
             "board_side_margin": board_margin,
             "description": desc,
             "copper_bbox": bbox,
             "evidence": "[实测](板侧落点·ISS-379) + [推算](3D 余量)",
             "source_refs": ["HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3 (ISS-379 已签收·只读)"],
             "chosen": False,
             "open_items": ["OI-3"]}
        c.update(compute_candidate(c, ho["J_UART"], crit, tol_fdm))
        c["verdict"] = ("罩住%s / 开口%s" % ("红" if not c["cover_pass"] else "绿",
                                            "红" if not c["open_pass"] else "绿"))
        cands.append(c)

    # ---- 帧无关结论 ----
    req = r4(crit + tol_fdm)
    fw = {
        "required_margin_per_side": req,
        "statements": [
            {"id": "FW-1",
             "text": "`J_UART` 换官方 1x2 THT 后罩住判据【与落点无关、与帧无关】: 铜箔 X 宽 2.2700 vs "
                     "座体必须清空区 X 宽 2.5400 ⇒ 每边余量 (2.5400-2.2700)/2 = 0.1350 ⇒ 最坏 -0.1650 < CRIT ⇒ "
                     "不过阈; 要过阈必须把清空区 X 宽放到 >= 2.2700 + 2 x (CRIT + TOL) = 4.0700 ⇒ "
                     "【无论 main 选哪个候选落点, 宽度要求都是 4.0700, 只是清空区的中心随落点移动】",
             "basis": "宽度比与坐标无关 (ISS-379 §2.3 三候选的 copper 宽逐字相同 = 2.2700)"},
            {"id": "FW-2",
             "text": "`J_UART` 三个候选的罩住余量【在实口径下互不相同但【判决相同】】: C1 每边伸出 0.7900 / "
                     "C2 每边伸出 0.0100 / C3 四边全在区内但最窄边只有 0.0900 ⇒ 三者最坏余量 "
                     "-1.0900 / -0.3100 / -0.2100 ⇒ 全部 < CRIT ⇒ 三候选【全部】不过阈 ⇒ 落点裁决不被结构侧阻塞",
             "basis": "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3 三候选 copper bbox + 罩开口/清空区真身"},
            {"id": "FW-3",
             "text": "`J_UART` 罩开口侧【三候选全部过阈】: 只要 (H ∪ C) 落在 O 内缩 (CRIT+TOL) = 0.9000 之后的窗口里 ⇒ "
                     "开口过阈; 本帧该窗口 = X 14.6900..23.0900 × Y 67.2000..70.0000 ⇒ 三个候选的 copper bbox 全部落在窗口内 "
                     "⇒ 三个候选的开口余量【逐字相同】= 1.0300 (最坏 0.7300) ⇒ 全部 >= CRIT ⇒ "
                     "★开口侧是 Y 向卡住 (H_y 2.5400 本身就只剩 1.0300/边) 而不是落点卡住★",
             "basis": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md §3.5 开口 X 13.790..23.990 × Y 66.300..70.900"},
            {"id": "FW-4",
             "text": "`J_DEBUG` 的判决【与三个竞争值的选择无关】: 按 1.7750 / 4.0850 / 4.8100 出件 ⇒ 罩住 X 最坏余量 "
                     "-1.8175 / -0.6625 / -0.3000 ⇒ 三者【全部红】⇒ OI-5 选哪个只改【返工幅度】"
                     "(每边超出 1.5175 / 0.3625 / 0.0000) 不改【红绿方向】⇒ 这一趟 `J_DEBUG` 的结构件无论如何都要动",
             "basis": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 + MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §0.1"},
            {"id": "FW-5",
             "text": "两个连接器的【红绿方向相同】(换官方 THT 后两件的罩住轴都红) ⇒ 上一轮 ISS-374/ISS-377 的"
                     "「一红一绿」是【口径差】造成的表象 (`J_DEBUG` 的 Hx 是铜箔支配 ⇒ 罩住 X 恒等于 0 同义反复); "
                     "口径统一后两件同向 ⇒ 【不互相矛盾】⇒ 那一趟必须【同批改两件】的结构件",
             "basis": "MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md §0.1 判据链 + 本页 §1 同源主表"},
        ],
        "frame_caveat": "三个候选落点的绝对坐标挂在帧 B160x100 上 ⇒ 若上位问题 (板框) 落乙, 三个坐标【全部作废】; "
                        "但 FW-1~FW-5 全部是【宽度/余量/相对位置】结论 ⇒ 与帧无关 ⇒ 坐标作废不影响判决",
    }

    consistency = {
        "same_table": True,
        "same_criterion": "两件同一张同源主表 · 同一套判据链 (ISS-377 §0.1) · 同一份 CRIT/TOL (源码实读)",
        "contradictions": [],
        "couplings": [
            "① `J_DEBUG` 换官方 THT 后罩住 X 在三个竞争值下【全红】⇒ 无论 OI-5 怎么裁, `J_DEBUG` 结构件都要返工 ⇒ "
            "不存在「只改 `J_UART` 结构件」这种省事方案",
            "② `J_UART` 的罩住宽度要求 (4.0700) 与落点无关, 但【清空区中心】随落点变 (C1 17.9650 / C2 19.0350 / C3 18.9350) ⇒ "
            "结构件出件必须等落点定死 ⇒ 「板只改一次」那一趟里落点裁决必须【先于】结构件出件",
            "③ Y 向两件同源同值: 罩住 Y 余量 0.7700 (最坏 0.4700) 要过阈需 H_y >= 1.0000 + 2 x 0.9000 = 2.8000, "
            "而罩开口 Y 4.6000 只容得下 H_y <= 4.6000 - 2 x 0.9000 = 2.8000 ⇒ 【Y 向恰好卡死, 零制造余量】⇒ "
            "要留制造余量必须放大开口 Y (不得只放大清空区)",
        ],
    }

    degrade = [
        {"id": "DP-1",
         "title": "按最坏值设计: `J_DEBUG` 清空区 X 宽取 4.8100 与 6.6100 的【最大值】",
         "basis": "官方 THT 真 land 铜箔 X 4.8100 + 2 x (CRIT + TOL) 1.8000 = 6.6100; "
                  "而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200",
         "cost": "结构件清空区 X 宽 +4.8350 (按 1.7750 出件) ⇒ 结构件出件前必须先定 OI-5, 否则返工两次",
         "affects": ["J_DEBUG"], "evidence": "[推算]"},
        {"id": "DP-2",
         "title": "按最坏值设计: `J_UART` 清空区 X 宽放到 4.0700 (中心随落点定)",
         "basis": "官方 1x2 THT 铜箔 X 2.2700 + 2 x (CRIT + TOL) 1.8000 = 4.0700; "
                  "★注: ISS-377 §3.2 DP-1 给的 3.4700 = 2.2700 + 2 x CRIT 是【名义余量】口径; "
                  "按全链 (最坏 = 余量 - TOL >= CRIT) 需要 4.0700 ⇒ 差 0.6000 ⇒ 本页只登记, 不回头改老页★",
         "cost": "清空区 X 宽 +1.5300 (按 2.5400 出件) + 中心随落点移动 ⇒ 必须与板那一趟同批",
         "affects": ["J_UART"], "evidence": "[推算]"},
        {"id": "DP-3",
         "title": "选官网参数直接满足的替代型号: `J_UART` 换铜箔 X 宽 <= 0.7400 的排针 (清空区一个数都不改)",
         "basis": "要让清空区 X 2.5400 保持不动并过罩住判据 ⇒ 铜箔 X 宽 <= 2.5400 - 2 x (CRIT + TOL) 1.8000 = 0.7400; "
                  "★官方 1x2 SMD 变体铜箔 X 1.9200 不满足 ⇒ 只能另选更窄的排针 / 改成别的出线方式★",
         "cost": "选型与 pad 序要另开一单 (板侧 + 硬件侧) ; `B33` 要把 `J_UART` 排除在换 land 名单外",
         "affects": ["J_UART"], "evidence": "[推算]"},
        {"id": "DP-4",
         "title": "改设计路径绕开: Y 向零余量 ⇒ 开口 Y 一并放大 (不改只放大清空区)",
         "basis": "开口 Y 4.6000 只容 H_y <= 2.8000 ⇒ 恰好卡死 ⇒ 要留制造余量须开口 Y >= 2.8000 + 2 x (CRIT + TOL)",
         "cost": "罩开口 Y 规格重做 (4.6000 ⇒ 至少 5.6000) ⇒ 结构件开口与清空区同批改",
         "affects": ["J_DEBUG", "J_UART"], "evidence": "[推算]"},
    ]

    open_items = {
        "OI-5": "`J_DEBUG` 的「必须清空区 X 宽」以哪个数为准 (1.7750 / 4.0850 / 4.8100) ⇒ to=main "
                "★本单不代答★ (三个值的代价已摆在 §3; 判决方向三者全红 ⇒ 裁哪个只改返工幅度)",
        "OI-3": "`J_UART` 落点三选一 (rot 270 / rot 90 / rot 90) ⇒ to=main (★已被 ISS-379 裁决挂起, 本单不重开★) "
                "★三个候选的 3D 判定本单已全部给出且全部同向, 不被结构侧阻塞★",
        "OI-11": "`J_DEBUG` 座体真实高 h = [0数据] ⇒ 按 Z 向保守上界 4.70 参数化 (与 ISS-380 §3.3-② 同源) ⇒ "
                 "★X 向判决与 h 无关★",
        "OI-12": "罩住判据 (座体必须清空区 vs 铜箔 每边 >= CRIT + TOL) 对 THT 排针是否过严 ⇒ to=main + boss "
                 "(★事实: 官方 1x4 THT 的 F.CrtYd 只有 6.0900 X, 而判据要求清空区 6.6100 ⇒ 比 courtyard 还大 0.5200★)",
        "OI-13": "Y 向零余量 (开口 Y 4.6000 只容 H_y 2.8000) 是否接受 ⇒ to=main + boss",
    }

    blk = {
        "schema": "mech.debug.seat.3d.fit.v1",
        "issue": "ISS-386",
        "agent": "mech-lead",
        "updated": "2026-11-24",
        "frame_id": FRAME_ID,
        "criterion": {
            "formula": "M = max(H_housing, C_copper) per axis; margin_open = (O_opening - M)/2; "
                       "margin_cover = (H_housing - C_copper)/2; worst = margin - TOL['fdm_part']; "
                       "pass iff worst >= CRIT",
            "crit_source": "MECH/service_port_check.py L126-L127 (CRIT = 2 * TOL['fdm_part'])",
            "crit_value": crit,
            "tol_fdm_part": tol_fdm,
            "required_margin_per_side": req,
            "position_form": "实口径: cover_signed = min(C.x0-H.x0, H.x1-C.x1, C.y0-H.y0, H.y1-C.y1); "
                             "open_signed = min over ((H ∪ C) 四边 vs O 四边)",
            "axes": ["x", "y"],
        },
        "rows": rows,
        "j_debug_clearance_x_candidates": clear_rows,
        "j_uart_candidates": cands,
        "frame_independent": fw,
        "consistency": consistency,
        "degrade_plans": degrade,
        "open_items": open_items,
        "landing_point_decision": "not_decided_here",
        "evidence_levels_used": ["[实测]", "[推算]", "[0数据]"],
        "board_baseline": BOARD_BASELINE,
        "gate": "MECH/check_debug_seat_3d_fit.py",
        "gate_chained": False,
    }
    return blk


# ==================================================================================================
# 反向用例 (--selftest)
# ==================================================================================================
COPY_FILES = [PAGE_REL, OPENING_REL, CALIBER_REL, CRIT_REL, LAND_FIT_REL, GATE_REL,
              PCB_REL, NETLIST_REL, PINS_REL, BOM_REL]


def make_sandbox(root: str, case: str):
    sb = p(root, os.path.join("tmp", "iss386_sbx", "selftest", case))
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


def block_mutate(sb: str, fn):
    path = p(sb, PAGE_REL)
    txt = read_text(path)
    i = txt.find(BLOCK_BEGIN)
    j = txt.find(BLOCK_END)
    seg = txt[i:j]
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", seg, re.S)
    data = json.loads(m.group(1))
    fn(data)
    new_seg = seg[:m.start()] + "```json\n" + json.dumps(data, ensure_ascii=False, indent=1) + "\n```" + seg[m.end():]
    write_text(path, txt[:i] + new_seg + txt[j:])


def write_text(path: str, s: str):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(s)


def selftest(root: str):
    cases = []

    def case(name, desc, mutate, expect_kid):
        cases.append((name, desc, mutate, expect_kid))

    # 01 删掉一个 J_UART 候选 ⇒ 必须红 (K2)
    case("c01_drop_candidate",
         "把 `J_UART` 三个候选删成两个 ⇒ 必须红 (K2)",
         lambda sb: block_mutate(sb, lambda d: d.__setitem__("j_uart_candidates", d["j_uart_candidates"][:2])),
         "K2")

    # 02 帧 id 改成别的 ⇒ 必须红 (K6)
    case("c02_frame_id",
         "把帧 id 改成 F30A ⇒ 必须红 (K6)",
         lambda sb: block_mutate(sb, lambda d: d.__setitem__("frame_id", "F30A")),
         "K6")

    # 03 源码 TOL 改掉 ⇒ 闸读数必须跟着变 ⇒ 红 (K3/K5)
    def m03(sb):
        f = p(sb, CRIT_REL)
        t = read_text(f).replace('TOL = {"fdm_part": 0.30, "fdm_feat": 0.25}',
                                  'TOL = {"fdm_part": 0.40, "fdm_feat": 0.25}')
        write_text(f, t)
    case("c03_tol_changed", "把源码 TOL['fdm_part'] 0.30→0.40 ⇒ 闸读数跟着变 ⇒ 红 (K3/K5)", m03, "K3")

    # 04 改错一个余量 ⇒ 必须红 (K3)
    case("c04_wrong_margin",
         "把 `J_UART` 换 THT 的罩住余量 0.1350 抄成 0.5350 ⇒ 必须红 (K3)",
         lambda sb: block_mutate(sb, lambda d: d["rows"][3].__setitem__("margin_cover", {"x": 0.535, "y": 0.77})),
         "K3")

    # 05 判决与实算相反 ⇒ 必须红 (K4)
    case("c05_flip_verdict",
         "把 `J_UART` 换 THT 的罩住判决从红改成过 ⇒ 必须红 (K4)",
         lambda sb: block_mutate(sb, lambda d: d["rows"][3].__setitem__("pass_cover", {"x": True, "y": False})),
         "K4")

    # 06 CRIT 写死 / 抽掉取法声明 ⇒ 必须红 (K5)
    case("c06_crit_hardcoded",
         "把机器块里的 CRIT/TOL 取法声明抽掉 (写死数值) ⇒ 必须红 (K5)",
         lambda sb: block_mutate(sb, lambda d: d["criterion"].__setitem__("crit_source", "0.60 (写死)")),
         "K5")

    # 07 两连接器拆成两张表 ⇒ 必须红 (K1)
    def m07(sb):
        f = p(sb, PAGE_REL)
        txt = read_text(f)
        i = txt.find("| `J_UART`")
        j = txt.find("\n", i)
        row = txt[i:j]
        txt = txt[:i] + txt[j + 1:]
        txt += "\n\n| 位号 | 档位 | 假表 |\n|---|---|---|\n" + row + "\n"
        write_text(f, txt)
    case("c07_split_tables", "把 `J_UART` 的行拆到另一张表 ⇒ 必须红 (K1)", m07, "K1")

    # 08 `J_DEBUG` 三个竞争值删一个 ⇒ 必须红 (K1b)
    case("c08_drop_clear_x",
         "把 `J_DEBUG` 清空区 X 宽三个竞争值删成两个 ⇒ 必须红 (K1b)",
         lambda sb: block_mutate(sb, lambda d: d.__setitem__(
             "j_debug_clearance_x_candidates", d["j_debug_clearance_x_candidates"][:2])),
         "K1b")

    # 09 偷偷落点 ⇒ 必须红 (K10)
    case("c09_pick_landing",
         "在本页偷偷挑一个落点 (chosen=true) ⇒ 必须红 (K10)",
         lambda sb: block_mutate(sb, lambda d: (d["j_uart_candidates"][0].__setitem__("chosen", True),
                                                 d.__setitem__("landing_point_decision", "rot270"))),
         "K10")

    # 10 抽掉「坐标作废」声明 ⇒ 必须红 (K6)
    def m10(sb):
        f = p(sb, PAGE_REL)
        t = read_text(f)
        t = t.replace("作废", "XX")
        write_text(f, t)
        block_mutate(sb, lambda d: d["frame_independent"].__setitem__("frame_caveat", "无"))
    case("c10_drop_void_stmt", "抽掉『坐标随上位问题作废』声明 ⇒ 必须红 (K6)", m10, "K6")

    # 11 抽掉证据等级 ⇒ 必须红 (K7)
    case("c11_drop_evidence", "把一行证据等级抽掉 ⇒ 必须红 (K7)",
         lambda sb: block_mutate(sb, lambda d: d["rows"][0].__setitem__("evidence", "")),
         "K7")

    # 12 注入挂起措辞 ⇒ 必须红 (K8)
    def m12(sb):
        f = p(sb, PAGE_REL)
        t = read_text(f).replace("## ★§4", "等原厂回信\n\n## ★§4")
        write_text(f, t)
    case("c12_pending_wording", "注入『等原厂回信』挂起措辞 ⇒ 必须红 (K8)", m12, "K8")

    # 13 板文件被改 (沙盒副本) ⇒ 必须红 (K9)
    def m13(sb):
        f = p(sb, PCB_REL)
        with open(f, "a", encoding="utf-8") as fh:
            fh.write("\n(footprint \"x\" (at 0 0))\n")
    case("c13_board_changed", "沙盒板文件被追加一个字节 ⇒ 必须红 (K9)", m13, "K9")

    # 14 降级方案删到 2 条 ⇒ 必须红 (K8)
    case("c14_drop_degrade", "把降级方案删到 2 条 ⇒ 必须红 (K8)",
         lambda sb: block_mutate(sb, lambda d: d.__setitem__("degrade_plans", d["degrade_plans"][:2])),
         "K8")

    # 15 网表被改 (沙盒副本) ⇒ 必须红 (K9)
    def m15(sb):
        with open(p(sb, NETLIST_REL), "a", encoding="utf-8") as fh:
            fh.write("X,X,X,X\n")
    case("c15_netlist_changed", "沙盒网表被追加 ⇒ 必须红 (K9)", m15, "K9")

    # 16 闸被挂进 gate_check.py ⇒ 必须红 (KCHAIN)
    def m16(sb):
        f = p(sb, GATE_REL)
        with open(f, "a", encoding="utf-8") as fh:
            fh.write("\n# check_debug_seat_3d_fit\n")
    case("c16_chained", "把本闸挂进 state/gate_check.py ⇒ 必须红 (KCHAIN)", m16, "KCHAIN")

    # 17 抽掉 OI-5 ⇒ 必须红 (K10)
    def m17(sb):
        f = p(sb, PAGE_REL)
        t = read_text(f).replace("OI-5", "OI-XX")
        write_text(f, t)
    case("c17_drop_oi5", "把 OI-5 改成 OI-XX ⇒ 必须红 (K10)", m17, "K10")

    # 18 帧无关结论抽掉 ⇒ 必须红 (K6)
    case("c18_drop_frame_indep", "抽掉帧无关结论 statements ⇒ 必须红 (K6)",
         lambda sb: block_mutate(sb, lambda d: d["frame_independent"].__setitem__("statements", [])),
         "K6")

    npass = 0
    for name, desc, mutate, expect in cases:
        sb = make_sandbox(root, name)
        try:
            mutate(sb)
            g = Gate(sb)
            res = g.run()
            fails = [(k, m) for k, ok, m in res if not ok]
            if not fails:
                print("[FAIL] %-22s 期望红 (点名 %s) ⇒ 实际【绿】 (闸坏了)" % (name, expect))
            else:
                hit = any(k.startswith(expect) for k, _ in fails)
                if hit:
                    print("[ok]   %-22s rc=1 且点名 %s ✓  (%s)" % (name, expect, fails[0][1][:110]))
                    npass += 1
                else:
                    print("[FAIL] %-22s 红了但没点名 %s ⇒ 实际点名 %s" % (name, expect, [k for k, _ in fails]))
        except Exception as exc:
            print("[FAIL] %-22s 反向用例执行异常: %r" % (name, exc))
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
        blk = build_block()
        print(json.dumps(blk, ensure_ascii=False, indent=1))
        return 0

    if args.selftest:
        return selftest(root)

    g = Gate(root)
    res = g.run()
    for n in g.notes:
        print("[note] %s" % n)
    crit, tol, _ = read_crit(root)
    print("★CRIT/TOL 现场从 MECH/service_port_check.py 源码读: CRIT = %s · TOL['fdm_part'] = %s" % (crit, tol["fdm_part"]))
    print("★要求每边余量 >= CRIT + TOL = %s" % round(crit + tol["fdm_part"], 4))
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
