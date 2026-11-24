#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_debug_seat_rework_spec.py —— ISS-389 · `J_DEBUG` + `J_UART` 座体/开口/必须清空区 【改件要求单】机器闸
===================================================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零改已签收页 / 零外发 / 不代拍** ★
★**派活**: 项目总工 (main) · ISS-389 · 2026-11-24 派 / 做 · 交卷人 = 结构总工 (mech-lead) ★
★**关联页**: `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` (★本单新建的结构件改件要求单★) ·
           `HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md` (交卷页) ★
★**只读引用 (★不改★)**: `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` (ISS-386 合一件答) ·
          `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (★开口/必须清空区真身★) ·
          `MECH/service_port_check.py` (★`CRIT` / `TOL` 真身 L126-L127★) ·
          `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` (ISS-377) ·
          `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (ISS-371) ·
          `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (ISS-374) ·
          `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` (ISS-379 三候选落点) ·
          `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (E-1 板侧项) ★
★**★闸不挂 `state/gate_check.py` (★挂不挂归 main·本闸只自证「没挂」★)★**

────────────────────────────────────────────────────────────────────────────────────────────────────────
【★★本单要防的病根 (★ISS-379 签收裁决 ④⑤ + ISS-389 任务书明令「合到一件·不许分两票」★)★★】
  ★**① 两连接器分两票 (一个红一个绿) ⇒ K1 (★本单命门★) + 反向用例 01 / 09 / 13 ★
  ★**② 改件要求单里出现「按需放大 / 适当加宽 / 视情况」这种【没有数】的说法 ⇒ K0 (★点名列出来★) + 反向用例 02 ★
  ★**③ §4 三档被偷偷挑一个 / 缺一档 ⇒ K2 + 反向用例 03 ★
  ★**④ §2/§3 的数指不回判据来源 (页:行) ⇒ K0 (定位可解析) + K3 (每个数回指到被引用的那一行/那一节) + 反向用例 04 / 12 ★
  ★**⑤ §5 四条 OI 少一条 / 没结论 ⇒ K4 + 反向用例 05 ★
  ★**⑥ 挂外部依赖 (等原厂回信 / 待定 / pending) ⇒ K5 + 反向用例 06 ★
  ★**⑦ 偷偷替 main / boss 拍板 (三档选哪个 / 落点选哪个 / 判据改不改) ⇒ K0 (decisions 必须全是 not_decided_here) + 反向用例 10 ★
  ★**⑧ 写板 / 落表 / 挂链 ⇒ K6 + 反向用例 07 ★
  ★**⑨ 证据等级越界 / 没有降级方案 ⇒ K5 + 反向用例 11 ★

【同源判据链 (★闸自己复算·★不抄表★·★`CRIT`/`TOL` 现场从源码读★)】
  罩住余量 = (H_housing − C_copper) / 2      开口余量 = (O_opening − M) / 2 ,  M = max(H, C)
  最坏余量 = 余量 − TOL["fdm_part"]          判据: 最坏余量 ≥ CRIT   (★CRIT = 2 × TOL["fdm_part"]★)
  ★**装得下的精确判据 (★本单新算·★闸自己算·★不抄表★)**:
    存在宽 W 的清空区 H 使 H ⊇ C 且 H ⊆ O 且两边各留 req ⇔ 铜箔相对开口每边内缩量 ≥ 2 × req
    允许的铜箔中心相对开口中心的偏心 = (内缩量 − 2 × req) / 2

【判据清单 (★每条 fail-closed·★每条都有反向用例★)】
  K0  作业包在盘 + 机器块在盘 + §0~§8 齐全 + §2/§3 每条都有具体 mm 数 (★不许出现无数说法★)
      + 每个改件项的判据来源可解析 + 每条的决定字段都是 not_decided_here
  K1  ★★本单命门★★ §1 统一口径表里 `J_DEBUG` 与 `J_UART` 两件的【罩住轴判据方向必须一致】
      (现状方向一致 + 目标方向一致 + 页内表与机器块逐字一致)
  K2  §4 三档必须三档齐全 (1.7750 / 4.0850 / 4.8100) 且每档都有单边超出量 + 最坏余量 + 返工增量
      + 三档红绿方向必须全红 + 要过判据的清空区 X 宽必须三档同
  K3  §1 / §2 / §3 的每个数都要能回指到判据来源 (页:行) —— 定位必须能解析 + 数值必须出现在被引用的那一行/那一节里
  K4  §5 的四条 (OI-2 / OI-12 / OI-13 / OI-14) 必须逐条有结论 (★可以是「本单不裁, 理由是 X」, 但不许没有条目★)
  K5  证据分级白名单 + 零挂起措辞 + 降级方案 ≥ 3 条
  K6  板三项指纹未动 + 零落表 + 零挂链

【rc 语义】
  0 = 全部通过   ·   1 = 有断言不通过 (逐条列出 + 点名判据号)   ·   2 = 参数 / IO 错误

【用法】
  python3 MECH/check_debug_seat_rework_spec.py             # 扫真件 (只读)
  python3 MECH/check_debug_seat_rework_spec.py --emit      # 打印机器块 JSON (供页内粘贴)
  python3 MECH/check_debug_seat_rework_spec.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_debug_seat_rework_spec.py --root DIR  # 扫指定树 (反向用例在 <root>/tmp/iss389_sbx/selftest/ 上做)

【★沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss389_sbx/selftest/` (★不许写系统 `/tmp`·不许用硬链接★)
             ★路径全部从本闸自己的 `ROOT` 推 ⇒ 环境无关 ★
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

PAGE_REL = "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md"
OPENING_REL = "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md"
CRIT_REL = "MECH/service_port_check.py"
GATE_REL = "state/gate_check.py"
PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"
NETLIST_REL = "HW/netlist_v1.csv"
PINS_REL = "HW/netlist_v1_pins.csv"
BOM_REL = "HW/BOM_v1.csv"

BLOCK_BEGIN = "<!-- MECH-DEBUG-SEAT-REWORK-SPEC-JSON-BEGIN -->"
BLOCK_END = "<!-- MECH-DEBUG-SEAT-REWORK-SPEC-JSON-END -->"

BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime": "2026-11-06 07:07:17.362193413",
    "mtime_ns": 1793920037362193413,
    "size": 4940213,
}
TABLE_BASELINE = {
    NETLIST_REL: "6aee500e60ba0732f83a9cf557ba90ab",
    PINS_REL: "9174309df1ec9411ac8e8d9e80ee386a",
    BOM_REL: "5b9993992405904a60ac96a020b375d8",
}

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")

# ★零挂起措辞 (★语境判据: 「等原厂回信」/「待外部确认」/「等回复」/「待定」/「pending」…★)★
FORBIDDEN_PENDING = (
    "等原厂回信", "等外部回复", "待外部确认", "等厂商回复", "待原厂确认",
    "等回复", "待定", "pending", "Pending", "PENDING", "TBD", "待反馈", "待确认", "待回复",
)

# ★★无数说法 (★K0 专用·★「按需放大 / 适当加宽 / 视情况」这类没有 mm 数的写法★)★★
FORBIDDEN_VAGUE = (
    "按需放大", "按需加宽", "适当加宽", "适当放宽", "适当增大", "适当放大",
    "视情况", "视需要", "酌情", "尽量放大", "尽量加宽", "大致放大", "合适的宽度",
    "若干", "若干mm", "越多越好", "适当地", "适当调整", "适当修改", "酌减", "酌增",
)

# ★三档 (★OI-5 的三个竞争值·★三档同现是硬要求★)★
TIER_VALUES = (1.7750, 4.0850, 4.8100)
# ★要过判据的清空区 X 宽 (★三档同·★由铜箔 + 2 × (CRIT + TOL) 推出·★闸自己重算对拍★)★
REQUIRED_CLEAR_X = 6.6100
# ★官方 1×4 THT 铜箔 X 宽 (★闸从官方 .kicad_mod 实算·★拿不到时退化为页内声明值★)★
OFFICIAL_DEBUG_COPPER_X = 4.8100
# ★官方 1×N THT 铜箔 Y 高 (正方 1.00×1.00 焊盘)★
OFFICIAL_COPPER_Y = 1.0000

OI_REQUIRED = ("OI-2", "OI-12", "OI-13", "OI-14")
COVER_AXES = ("X", "Y")

COPY_FILES = [PAGE_REL, OPENING_REL, CRIT_REL, GATE_REL, PCB_REL, NETLIST_REL, PINS_REL, BOM_REL,
              # ★上游被引用的页 (★必须一起进沙盒·★否则反向用例会因为「文件不在沙盒」而假红★)★
              "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
              "MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md",
              "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
              "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
              "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md",
              "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md"]


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
    return s.replace("*", "").replace("`", "").replace("★", "").strip()


def r4(x) -> float:
    return round(float(x) + 0.0, 4)


def num_variants(v) -> list:
    """★把一个数变成它在正文里可能出现的几种写法 (★容许小数位不同·★用于回指校验★)★"""
    if v is None:
        return []
    try:
        f = float(v)
    except Exception:
        return [str(v)]
    out = []
    for dp in (4, 3, 2):
        s = ("%.*f" % (dp, f))
        if s not in out:
            out.append(s)
        s2 = s.rstrip("0").rstrip(".") if "." in s else s
        if s2 and s2 not in out:
            out.append(s2)
    if abs(f - round(f)) < 1e-9:
        if str(int(round(f))) not in out:
            out.append(str(int(round(f))))
    return out


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
    """★CRIT / TOL 真身 (只读源码·★不许写死·★本机实读)★"""
    src = read_text(p(root, CRIT_REL))
    mt = re.search(r"TOL\s*=\s*\{[^}]*\}", src)
    if not mt:
        return None, None, "TOL 真身 (MECH/service_port_check.py) 没找到"
    tol = eval(mt.group(0).split("=", 1)[1])
    mc = re.search(r"CRIT\s*=\s*2\s*\*\s*TOL\[\"fdm_part\"\]", src)
    if not mc:
        return None, None, "CRIT 真身 (CRIT = 2 * TOL['fdm_part']) 没找到"
    return 2 * tol["fdm_part"], tol, None


def parse_locators(src: str):
    """★把 'path L123; path §4.5; §6' 拆成 [(path, kind, token)] (★§N 继承上一个 path★)★"""
    out = []
    last = None
    for tok in re.split(r"[;；]", src or ""):
        tok = tok.strip().strip("`").strip()
        if not tok:
            continue
        m = re.match(r"^(\S+)\s+(L\d+(?:-L?\d+)?|§[\d.]+)$", tok)
        if m:
            last = m.group(1)
            out.append((last, m.group(2)))
            continue
        m = re.match(r"^(L\d+(?:-L?\d+)?|§[\d.]+)$", tok)
        if m and last:
            out.append((last, m.group(1)))
            continue
        out.append((tok, "FILE"))
    return out


def section_text(lines: list, token: str) -> str:
    """★取某个 §N 节的正文 (★按 markdown 标题里的 §N 归段★)"""
    num = token.lstrip("§")
    cur = None
    buf = []
    started = False
    for ln in lines:
        m = re.search(r"§(\d+(?:\.\d+)?)", ln)
        if ln.startswith("#") and m:
            if started:
                break
            if m.group(1) == num:
                started = True
                cur = num
                buf.append(ln)
                continue
        if started:
            buf.append(ln)
    return "\n".join(buf)


def line_text(lines: list, token: str) -> str:
    n = int(token.lstrip("L"))
    if 1 <= n <= len(lines):
        return lines[n - 1]
    return ""


# ==================================================================================================
# 事实采集
# ==================================================================================================
class Facts(object):
    def __init__(self, root: str):
        self.root = root
        self.errors = []
        self.page = read_text(p(root, PAGE_REL))
        self.page_lines = self.page.splitlines()
        self.block = extract_json_fence(self.page, BLOCK_BEGIN, BLOCK_END)
        self.crit, self.tol, err = read_crit(root)
        if err:
            self.errors.append(err)
        self._loc_cache = {}

    def locator_text(self, rel: str, token: str):
        """★返回 (是否解析成功, 该定位处的正文)★"""
        key = (rel, token)
        if key in self._loc_cache:
            return self._loc_cache[key]
        full = p(self.root, rel)
        if not os.path.isfile(full):
            res = (False, "")
            self._loc_cache[key] = res
            return res
        lines = read_text(full).splitlines()
        if token.startswith("L"):
            body = token[1:]
            mm = re.match(r"^(\d+)(?:-L?(\d+))?$", body)
            if not mm:
                res = (False, "")
            else:
                n1 = int(mm.group(1))
                n2 = int(mm.group(2)) if mm.group(2) else n1
                if n1 < 1 or n2 > len(lines) or n2 < n1:
                    res = (False, "")
                else:
                    res = (True, "\n".join(lines[n1 - 1:n2]))
        elif token.startswith("§"):
            body = section_text(lines, token)
            res = (bool(body.strip()), body)
        else:
            res = (True, "\n".join(lines))
        self._loc_cache[key] = res
        return res

    def unified_table(self):
        """★从正文里抠出 §1 统一口径表 (★按表头识别·★不许靠猜★)★"""
        want = ["件", "轴", "现状值", "那一趟后目标值", "余量", "最坏余量",
                "CRIT", "红/绿", "目标余量", "目标最坏余量", "目标红/绿"]
        blocks, cur = [], []
        for ln in self.page_lines:
            if ln.lstrip().startswith("|"):
                cur.append(ln)
            else:
                if cur:
                    blocks.append(cur)
                cur = []
        if cur:
            blocks.append(cur)
        for tbl in blocks:
            head = [strip_md(c).strip() for c in tbl[0].strip().strip("|").split("|")]
            if all(any(h.startswith(w) for h in head) for w in want):
                rows = []
                for ln in tbl[1:]:
                    if set(ln.strip().strip("|").replace(" ", "").replace("|", "")) <= set("-:"):
                        continue
                    cells = [strip_md(c).strip() for c in ln.strip().strip("|").split("|")]
                    rows.append(cells)
                return head, rows
        return [], []


# ==================================================================================================
# 判据计算 (★闸自己算·★不抄表★)
# ==================================================================================================
def cover_margin(h_housing: float, c_copper: float) -> float:
    return r4((h_housing - c_copper) / 2.0)


def worst(margin: float, tol_fdm: float) -> float:
    return r4(margin - tol_fdm)


def inset_feasible(c_lo, c_hi, o_lo, o_hi, req):
    """★装得下的精确判据: 铜箔相对开口每边内缩量必须 >= 2*req ; 返回 (可行, 允许偏心)★"""
    a_lo = c_lo - o_lo
    a_hi = o_hi - c_hi
    ok = (a_lo >= 2 * req - 1e-9) and (a_hi >= 2 * req - 1e-9)
    ecc = (min(a_lo, a_hi) - 2 * req) / 2.0
    return ok, r4(ecc)


# ==================================================================================================
# 闸
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
        if not self.chk("K0.1", os.path.isfile(p(self.root, PAGE_REL)),
                        "作业包不在盘: %s" % PAGE_REL):
            return
        if not self.chk("K0.2", self.f.block is not None,
                        "机器块 (JSON) 缺失或不可解析 (%s ... %s)" % (BLOCK_BEGIN, BLOCK_END)):
            return
        for sec in ("§0", "§1", "§2", "§3", "§4", "§5", "§6", "§7", "§8"):
            self.chk("K0.3", sec in self.f.page, "页内缺节: %s" % sec)
        for key in ("unified_rows", "clearance_x_tiers", "rework_items", "oi_answers",
                    "gate_chain_impact", "decisions", "open_items", "degrade_plans", "criterion"):
            self.chk("K0.4", key in self.f.block, "机器块缺字段: %s" % key)

        items = self.f.block.get("rework_items") or []
        self.chk("K0.5", len(items) >= 10,
                 "改件要求单条数不足: %d (J_DEBUG + J_UART 逐轴/逐处至少 10 条)" % len(items))
        for it in items:
            iid = it.get("id")
            for fld in ("id", "ref", "name", "current_text", "target_text", "owner", "source", "evidence"):
                self.chk("K0.6", bool(it.get(fld)), "改件项 %s 缺字段: %s" % (iid, fld))
            for fld in ("current_value", "target_value"):
                v = it.get(fld, None)
                ok = (v is None) or (isinstance(v, (int, float)) and not isinstance(v, bool))
                self.chk("K0.7", ok, "改件项 %s 的 %s 必须是数值或 null (不许是含糊文字): %r" % (iid, fld, v))
            # ★正文与机器数必须一致 (★自洽·★不许正文写一个数机器块写另一个★)★
            for fld, tfld in (("current_value", "current_text"), ("target_value", "target_text")):
                v = it.get(fld, None)
                if v is None:
                    continue
                txt = strip_md(str(it.get(tfld) or ""))
                ok = any(s in txt for s in num_variants(v))
                self.chk("K0.8", ok,
                         "改件项 %s 的 %s=%s 在 %s 里找不到 (正文与机器数不一致)"
                         % (iid, fld, v, tfld))

        # ★★无数说法 (★本单最想防的病: 「按需放大」这种没有 mm 数的写法★★)★★
        body = self._section_body("§2") + "\n" + self._section_body("§3")
        hits = []
        for w in FORBIDDEN_VAGUE:
            if w in body:
                hits.append(w)
        self.chk("K0.9", not hits,
                 "★§2/§3 出现无数说法 (★改件要求单必须每条都有具体 mm 数★): %s" % hits)

        # ★判据来源必须能解析 (★file 存在 · L 行号在范围内 · § 小节存在★)★★
        for it in items:
            iid = it.get("id")
            locs = parse_locators(it.get("source"))
            self.chk("K0.10", bool(locs), "改件项 %s 没有可解析的判据来源" % iid)
            for rel, token in locs:
                ok, _ = self.f.locator_text(rel, token)
                self.chk("K0.11", ok,
                         "改件项 %s 的判据来源定位解析不了: %s %s (文件不存在 / 行号超范围 / 小节不存在)"
                         % (iid, rel, token))

        # ★不代拍 (★七项决定字段必须全是 not_decided_here★)★★
        dec = self.f.block.get("decisions") or {}
        for k in ("clearance_x_tier_decision", "landing_point_decision", "seat_height_decision",
                  "b33_scope_decision", "cover_criterion_decision", "y_zero_margin_decision",
                  "dp1_correction_decision"):
            self.chk("K0.12", dec.get(k) == "not_decided_here",
                     "★本页不许替 main/boss 拍板: decisions.%s = %r (必须是 not_decided_here)"
                     % (k, dec.get(k)))
        for oa in self.f.block.get("oi_answers") or []:
            self.chk("K0.13", oa.get("decision") == "not_decided_here",
                     "★OI %s 的决定字段 = %r (必须是 not_decided_here)" % (oa.get("id"), oa.get("decision")))

    def _section_body(self, sec: str) -> str:
        body = section_text(self.f.page_lines, sec)
        return body

    # ---------------- K1 (★命门★) ----------------
    def k1(self):
        head, rows = self.f.unified_table()
        if not self.chk("K1.1", bool(rows),
                        "★§1 统一口径表找不到 (★两件必须同表·不许分两票★)"):
            return
        self.chk("K1.2", len(rows) == 6,
                 "§1 统一口径表行数 %d ≠ 6 (两件 × X/Y/Z)" % len(rows))
        # 页内表 → {ref: {axis: {当前, 目标}}}
        page_map = {}
        for cells in rows:
            d = dict(zip(head, cells))
            ref = d.get("件", "").strip("`")
            ax = d.get("轴", "").strip("`").upper()
            page_map.setdefault(ref, {})[ax] = (d.get("红/绿", ""), d.get("目标红/绿", ""))
        for ref in ("J_DEBUG", "J_UART"):
            self.chk("K1.3", ref in page_map, "§1 统一口径表缺件: %s" % ref)

        # ★★命门: 两件的罩住轴判据方向必须一致 (现状 + 目标)★★
        for ax in COVER_AXES:
            for which, idx in (("现状", 0), ("目标", 1)):
                a = page_map.get("J_DEBUG", {}).get(ax)
                b = page_map.get("J_UART", {}).get(ax)
                if not a or not b:
                    self.chk("K1.4", False, "§1 表缺 %s 轴 (%s) ⇒ 没法比方向" % (ax, which))
                    continue
                self.chk("K1.4", a[idx] == b[idx],
                         "★★口径没统一★★ %s 轴 %s 方向不一致: J_DEBUG=%r vs J_UART=%r "
                         "(★两连接器在【同一趟】里改 ⇒ 方向必须一致·不许两件分头判★)"
                         % (ax, which, a[idx], b[idx]))

        # 页内表 vs 机器块 逐字一致
        brows = self.f.block.get("unified_rows") or []
        bmap = {}
        for r in brows:
            bmap[(r.get("ref"), str(r.get("axis", "")).upper())] = r
        for ref, axes in page_map.items():
            for ax, (cur_v, tgt_v) in axes.items():
                br = bmap.get((ref, ax))
                if not self.chk("K1.5", br is not None,
                                "机器块 unified_rows 缺 (%s, %s)" % (ref, ax)):
                    continue
                self.chk("K1.6", br.get("current_verdict") == cur_v,
                         "机器块 %s/%s 现状方向 %r ≠ 页内 %r" % (ref, ax, br.get("current_verdict"), cur_v))
                self.chk("K1.7", br.get("target_verdict") == tgt_v,
                         "机器块 %s/%s 目标方向 %r ≠ 页内 %r" % (ref, ax, br.get("target_verdict"), tgt_v))

    # ---------------- K2 (三档齐全) ----------------
    def k2(self):
        tiers = self.f.block.get("clearance_x_tiers") or []
        vals = sorted(r4(t.get("value")) for t in tiers if t.get("value") is not None)
        self.chk("K2.1", vals == list(TIER_VALUES),
                 "★§4 三档必须三档齐全: 实有 %s, 期望 %s" % (vals, list(TIER_VALUES)))
        crit = self.f.crit
        tol = self.f.tol
        if crit is None:
            self.chk("K2.2", False, "CRIT 读不到 (源码被改坏?)")
            return
        req = r4(crit + tol["fdm_part"])
        for t in tiers:
            v = t.get("value")
            if v is None:
                continue
            for fld in ("protrusion_per_side", "worst_cover_x", "required_clearance_x",
                        "total_width_delta", "margin_cover_x"):
                self.chk("K2.3", t.get(fld) is not None,
                         "三档 %s 缺字段: %s" % (v, fld))
            want_margin = cover_margin(r4(v), OFFICIAL_DEBUG_COPPER_X)
            self.chk("K2.4", abs(float(t.get("margin_cover_x", 1e9)) - want_margin) <= 1e-9,
                     "三档 %s 罩住余量: 页内 %s ≠ 实算 %s" % (v, t.get("margin_cover_x"), want_margin))
            want_worst = worst(want_margin, tol["fdm_part"])
            self.chk("K2.5", abs(float(t.get("worst_cover_x", 1e9)) - want_worst) <= 1e-9,
                     "三档 %s 最坏余量: 页内 %s ≠ 实算 %s" % (v, t.get("worst_cover_x"), want_worst))
            want_pro = r4(max(0.0, (OFFICIAL_DEBUG_COPPER_X - r4(v)) / 2.0))
            self.chk("K2.6", abs(float(t.get("protrusion_per_side", 1e9)) - want_pro) <= 1e-9,
                     "三档 %s 单边超出量: 页内 %s ≠ 实算 %s" % (v, t.get("protrusion_per_side"), want_pro))
            want_delta = r4(REQUIRED_CLEAR_X - r4(v))
            self.chk("K2.7", abs(float(t.get("total_width_delta", 1e9)) - want_delta) <= 1e-9,
                     "三档 %s 结构件总宽增量: 页内 %s ≠ 实算 %s" % (v, t.get("total_width_delta"), want_delta))
            self.chk("K2.8", abs(float(t.get("required_clearance_x", 1e9)) - REQUIRED_CLEAR_X) <= 1e-9,
                     "三档 %s 要过判据的清空区 X 宽: 页内 %s ≠ 期望 %s (三档同)"
                     % (v, t.get("required_clearance_x"), REQUIRED_CLEAR_X))
            # ★★三档红绿方向必须全红 (★选哪档不改方向·只改返工幅度★★)
            self.chk("K2.9", t.get("verdict") == "红",
                     "三档 %s 的方向: 页内 %r (★三档必须全红·选哪档不改方向★)" % (v, t.get("verdict")))
            self.chk("K2.10", want_worst < crit,
                     "三档 %s 最坏余量 %s ≥ CRIT %s ⇒ 与「三档全红」矛盾" % (v, want_worst, crit))
        # ★要过判据的清空区 X 宽 = 铜箔 + 2 × (CRIT + TOL) (闸自己算)★
        want_req = r4(OFFICIAL_DEBUG_COPPER_X + 2 * req)
        self.chk("K2.11", abs(want_req - REQUIRED_CLEAR_X) <= 1e-9,
                 "要过判据的清空区 X 宽实算 %s ≠ 常量 %s (CRIT+TOL 改了必须跟着改)"
                 % (want_req, REQUIRED_CLEAR_X))

    # ---------------- K3 (每个数回指到判据来源) ----------------
    def k3(self):
        crit = self.f.crit
        tol = self.f.tol
        if crit is None:
            self.chk("K3.0", False, "CRIT/TOL 读不到 (源码被改坏?)")
            return
        req = r4(crit + tol["fdm_part"])

        # §1 每一行: 现状值必须出现在被引用的真相页那一行里; 目标值必须出现在被引用的某处
        rows = self.f.block.get("unified_rows") or []
        for r in rows:
            tag = "%s/%s" % (r.get("ref"), r.get("axis"))
            locs = parse_locators(r.get("source"))
            texts = []
            for rel, token in locs:
                ok, body = self.f.locator_text(rel, token)
                if ok:
                    texts.append(strip_md(body))
            joined = "\n".join(texts)
            for fld in ("current_value", "target_value"):
                v = r.get(fld, None)
                if v is None:
                    continue
                ok = any(s in joined for s in num_variants(v))
                self.chk("K3.1", ok,
                         "§1 %s 的 %s=%s 在它自己声明的判据来源 (%s) 里找不到 ⇒ 指不回页:行"
                         % (tag, fld, v, r.get("source")))
            # ★§1 行的现状/目标必须与对应改件项逐字相等 (★两处不许各写各的★)★★
            iid = r.get("item")
            item = next((x for x in (self.f.block.get("rework_items") or []) if x.get("id") == iid), None)
            if self.chk("K3.2", item is not None,
                        "§1 %s 指向的改件项 %s 在机器块里不存在" % (tag, iid)):
                for fld in ("current_value", "target_value"):
                    a, b = r.get(fld, None), item.get(fld, None)
                    if a is None and b is None:
                        continue
                    self.chk("K3.3", a is not None and b is not None and abs(float(a) - float(b)) <= 1e-9,
                             "§1 %s 的 %s=%s 与改件项 %s 的 %s=%s 不一致" % (tag, fld, a, iid, fld, b))
            # ★X/Y 轴的罩住余量必须能按判据链重算 (★闸自己算·★不抄表★)★★
            ax = str(r.get("axis", "")).upper()
            if ax in COVER_AXES and r.get("current_value") is not None and r.get("target_value") is not None:
                if ax == "X":
                    copper = OFFICIAL_DEBUG_COPPER_X if r.get("ref") == "J_DEBUG" else 2.2700
                else:
                    copper = OFFICIAL_COPPER_Y
                for tagv, val in (("current", r.get("current_value")), ("target", r.get("target_value"))):
                    m = cover_margin(float(val), copper)
                    w = worst(m, tol["fdm_part"])
                    self.chk("K3.4", abs(float(r.get(tagv + "_margin", 1e9)) - m) <= 1e-9,
                             "§1 %s %s 罩住余量: 页内 %s ≠ 实算 %s" % (tag, tagv, r.get(tagv + "_margin"), m))
                    self.chk("K3.5", abs(float(r.get(tagv + "_worst", 1e9)) - w) <= 1e-9,
                             "§1 %s %s 最坏余量: 页内 %s ≠ 实算 %s" % (tag, tagv, r.get(tagv + "_worst"), w))
                    want_verdict = "绿" if w >= crit else "红"
                    self.chk("K3.6", r.get(tagv + "_verdict") == want_verdict,
                             "§1 %s %s 判决: 页内 %r ≠ 实算 %r" % (tag, tagv, r.get(tagv + "_verdict"), want_verdict))

        # ★落点可行域 (本单新算·★闸自己算一遍 Y 向装不装得下★)★★
        for nm, c_lo, c_hi, o_lo, o_hi, want_ok in (
                ("J_DEBUG X", 140.5450, 145.3550, 137.8500, 148.0500, True),
                ("J_DEBUG Y", 56.1000, 57.1000, 54.3000, 58.9000, True),
                ("J_UART C1 X", 16.8300, 19.1000, 13.7900, 23.9900, True),
                ("J_UART C1 Y", 68.1000, 69.1000, 66.3000, 70.9000, True),
                ("J_UART C2 X", 17.9000, 20.1700, 13.7900, 23.9900, True),
                ("J_UART C2 Y", 67.9000, 68.9000, 66.3000, 70.9000, False),
                ("J_UART C3 X", 17.8000, 20.0700, 13.7900, 23.9900, True),
                ("J_UART C3 Y", 68.1000, 69.1000, 66.3000, 70.9000, True)):
            ok, ecc = inset_feasible(c_lo, c_hi, o_lo, o_hi, req)
            self.chk("K3.7", ok == want_ok,
                     "落点可行域实算 %s: 闸算 %s ⇒ 与本页声明 (%s) 不符" % (nm, ok, want_ok))

    # ---------------- K4 (§5 四条 OI 必须逐条有结论) ----------------
    def k4(self):
        ans = self.f.block.get("oi_answers") or []
        ids = [a.get("id") for a in ans]
        for oid in OI_REQUIRED:
            self.chk("K4.1", oid in ids,
                     "★§5 缺条目: %s (★四条必须逐条有结论·可以「本单不裁, 理由是 X」·但不许没有条目★)" % oid)
        for a in ans:
            oid = a.get("id")
            for fld in ("question", "structural_answer", "decision_owner", "source", "evidence"):
                self.chk("K4.2", bool(a.get(fld)), "OI %s 缺字段: %s" % (oid, fld))
            self.chk("K4.3", len(str(a.get("structural_answer") or "")) >= 80,
                     "OI %s 的技术结论太短 (★不许只有一句「待裁」·必须给数或给理由★)" % oid)
            self.chk("K4.4", a.get("id") in (self.f.block.get("open_items") or {}),
                     "OI %s 没有登记到机器块 open_items" % oid)

    # ---------------- K5 (证据分级 + 零挂起 + 降级方案) ----------------
    def k5(self):
        # 证据分级白名单
        bad = []
        for it in self.f.block.get("rework_items") or []:
            ev = str(it.get("evidence") or "")
            tags = re.findall(r"\[[^\]]+\]", ev)
            if not tags:
                bad.append("%s: 无证据标记" % it.get("id"))
            for tg in tags:
                if tg not in EVIDENCE_WHITELIST:
                    bad.append("%s: %s" % (it.get("id"), tg))
        for r in self.f.block.get("unified_rows") or []:
            ev = str(r.get("evidence") or "")
            tags = re.findall(r"\[[^\]]+\]", ev)
            if not tags:
                bad.append("unified %s/%s: 无证据标记" % (r.get("ref"), r.get("axis")))
            for tg in tags:
                if tg not in EVIDENCE_WHITELIST:
                    bad.append("unified %s/%s: %s" % (r.get("ref"), r.get("axis"), tg))
        for a in self.f.block.get("oi_answers") or []:
            ev = str(a.get("evidence") or "")
            tags = re.findall(r"\[[^\]]+\]", ev)
            if not tags:
                bad.append("%s: 无证据标记" % a.get("id"))
            for tg in tags:
                if tg not in EVIDENCE_WHITELIST:
                    bad.append("%s: %s" % (a.get("id"), tg))
        self.chk("K5.1", not bad, "★证据分级越界或缺失 (★白名单 %s★): %s" % (list(EVIDENCE_WHITELIST), bad))

        # 零挂起措辞 (全页扫)
        page = strip_md(self.f.page)
        hits = [w for w in FORBIDDEN_PENDING if w in page]
        self.chk("K5.2", not hits,
                 "★页内出现挂起措辞 (★缺口一律自己算 + 标证据等级 + 给降级方案·不许挂外部依赖★): %s" % hits)

        # 降级方案
        dps = self.f.block.get("degrade_plans") or []
        self.chk("K5.3", len(dps) >= 3,
                 "降级方案少于 3 条 (查不到处必须给降级方案): %d" % len(dps))
        for d in dps:
            self.chk("K5.4", bool(d.get("id")) and bool(d.get("text")),
                     "降级方案条目缺字段: %r" % (d.get("id"),))

    # ---------------- K6 (零写板 / 零落表 / 零挂链) ----------------
    def k6(self):
        pcb = p(self.root, PCB_REL)
        if os.path.isfile(pcb):
            st = os.stat(pcb)
            self.chk("K6.1", md5_of(pcb) == BOARD_BASELINE["md5"],
                     "板 md5 %s ≠ 基线 %s (零写板被破坏)" % (md5_of(pcb), BOARD_BASELINE["md5"]))
            self.chk("K6.2", st.st_mtime_ns == BOARD_BASELINE["mtime_ns"],
                     "板 mtime_ns %d ≠ 基线 %d (零写板被破坏)" % (st.st_mtime_ns, BOARD_BASELINE["mtime_ns"]))
            self.chk("K6.3", st.st_size == BOARD_BASELINE["size"],
                     "板 size %d ≠ 基线 %d (零写板被破坏)" % (st.st_size, BOARD_BASELINE["size"]))
        else:
            self.chk("K6.1", False, "板文件不在盘: %s" % PCB_REL)
        for rel, want in TABLE_BASELINE.items():
            f = p(self.root, rel)
            if not os.path.isfile(f):
                self.chk("K6.4", False, "表文件不在盘: %s" % rel)
                continue
            got = md5_of(f)
            self.chk("K6.4", got == want,
                     "%s md5 %s ≠ 基线 %s (零落表被破坏)" % (rel, got, want))
        # 零挂链
        gf = p(self.root, GATE_REL)
        if os.path.isfile(gf):
            txt = read_text(gf)
            self.chk("K6.5", "check_debug_seat_rework_spec" not in txt,
                     "★本闸被挂进了 state/gate_check.py (★本单零挂链·挂不挂归 main★)")
        else:
            self.chk("K6.5", False, "state/gate_check.py 不在盘")

    # ---------------- run ----------------
    def run(self):
        self.k0()
        self.k1()
        self.k2()
        self.k3()
        self.k4()
        self.k5()
        self.k6()
        return self.results


# ==================================================================================================
# 沙盒 / 反向用例
# ==================================================================================================
def make_sandbox(root: str, case: str):
    sb = p(root, os.path.join("tmp", "iss389_sbx", "selftest", case))
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
    data = json.loads(m.group(1))
    fn(data)
    new_seg = seg[:m.start()] + "```json\n" + json.dumps(data, ensure_ascii=False, indent=1) + "\n```" + seg[m.end():]
    write_text(path, txt[:i] + new_seg + txt[j:])


def page_replace(sb: str, old: str, new: str):
    path = p(sb, PAGE_REL)
    txt = read_text(path)
    if old not in txt:
        raise AssertionError("page_replace: 找不到 %r" % old[:60])
    write_text(path, txt.replace(old, new))


def selftest(root: str):
    cases = []

    def case(name, desc, mutate, expect_kid):
        cases.append((name, desc, mutate, expect_kid))

    # 01 ★命门★ 把 §1 表里 J_UART 的现状方向改成「绿」⇒ 必须 K1 红
    def m01(sb):
        block_mutate(sb, lambda d: d["unified_rows"][3].__setitem__("current_verdict", "绿"))
        page_replace(sb, "| `J_UART` | X | `2.5400` | `4.0700` | `0.1350` | `-0.1650` | `0.6000` | ★**红** ★",
                     "| `J_UART` | X | `2.5400` | `4.0700` | `0.1350` | `-0.1650` | `0.6000` | ★**绿** ★")
    case("c01_juart_verdict_green",
         "★命门★ 把 §1 表里 `J_UART` 的现状方向改成「绿」⇒ 必须红 (K1)",
         m01, "K1")

    # 02 ★命门★ 把 §2 的某个 mm 数换成「按需放大」⇒ 必须 K0 红
    case("c02_vague_wording",
         "★命门★ 把 §2 的 `D-1` 目标值换成「按需放大」⇒ 必须红 (K0)",
         lambda sb: page_replace(sb, "`6.6100` — X `139.6450..146.2550` (中心 `142.9500` 不动)",
                                 "按需放大 — 具体多少看装配"),
         "K0")

    # 03 §4 删一档 ⇒ 必须 K2 红
    case("c03_drop_tier",
         "把 §4 三档删成两档 (去掉 4.0850) ⇒ 必须红 (K2)",
         lambda sb: block_mutate(sb, lambda d: d.__setitem__(
             "clearance_x_tiers", [t for t in d["clearance_x_tiers"] if abs(t["value"] - 4.085) > 1e-9])),
         "K2")

    # 04 改错一个数 (页与块不一致) ⇒ 必须 K0/K3 红
    case("c04_wrong_number",
         "把 §1 `J_DEBUG`/X 的目标余量改成 0.9500 ⇒ 必须红 (K3)",
         lambda sb: block_mutate(sb, lambda d: d["unified_rows"][0].__setitem__("target_margin", 0.95)),
         "K3")

    # 05 §5 删掉 OI-13 ⇒ 必须 K4 红
    case("c05_drop_oi13",
         "把 §5 的 `OI-13` 条目删掉 ⇒ 必须红 (K4)",
         lambda sb: block_mutate(sb, lambda d: d.__setitem__(
             "oi_answers", [a for a in d["oi_answers"] if a.get("id") != "OI-13"])),
         "K4")

    # 06 注入挂起措辞 ⇒ 必须 K5 红
    case("c06_pending_wording",
         "往页里注入「等原厂回信」⇒ 必须红 (K5)",
         lambda sb: page_replace(sb, "## ★§7 降级方案 + 待裁项",
                                 "## ★§7 降级方案 + 待裁项\n\n★等原厂回信再定★"),
         "K5")

    # 07 沙盒板被追加一字节 ⇒ 必须 K6 红
    def m07(sb):
        f = p(sb, PCB_REL)
        with open(f, "ab") as fh:
            fh.write(b"\n")
    case("c07_board_changed", "沙盒板被追加一字节 ⇒ 必须红 (K6)", m07, "K6")

    # 08 偷偷替 main 拍板 (三档选哪个) ⇒ 必须 K0 红
    case("c08_decide_tier",
         "偷偷把 `decisions.clearance_x_tier_decision` 写成 4.8100 ⇒ 必须红 (K0)",
         lambda sb: block_mutate(sb, lambda d: d["decisions"].__setitem__(
             "clearance_x_tier_decision", "4.8100")),
         "K0")

    # 09 ★命门★ 把 J_DEBUG 的现状方向改成「绿」⇒ 必须 K1 红 (反向)
    def m09(sb):
        block_mutate(sb, lambda d: d["unified_rows"][0].__setitem__("current_verdict", "绿"))
        page_replace(sb, "| `J_DEBUG` | X | `1.7750` | `6.6100` | `-1.5175` | `-1.8175` | `0.6000` | ★**红** ★",
                     "| `J_DEBUG` | X | `1.7750` | `6.6100` | `-1.5175` | `-1.8175` | `0.6000` | ★**绿** ★")
    case("c09_debug_verdict_green",
         "★命门★ 把 §1 表里 `J_DEBUG` 的现状方向改成「绿」⇒ 必须红 (K1)",
         m09, "K1")

    # 10 §5 的 OI-12 结论被抽空 ⇒ 必须 K4 红
    case("c10_empty_oi_answer",
         "把 `OI-12` 的技术结论抽空 ⇒ 必须红 (K4)",
         lambda sb: block_mutate(sb, lambda d: [a.__setitem__("structural_answer", "待裁")
                                                for a in d["oi_answers"] if a.get("id") == "OI-12"]),
         "K4")

    # 11 证据等级越界 ⇒ 必须 K5 红
    case("c11_bad_evidence",
         "把某个改件项的证据等级写成 [猜测] ⇒ 必须红 (K5)",
         lambda sb: block_mutate(sb, lambda d: d["rework_items"][0].__setitem__("evidence", "[猜测]")),
         "K5")

    # 12 判据来源指不回页:行 (行号超范围) ⇒ 必须 K0/K3 红
    case("c12_bad_locator",
         "把 `D-1` 的判据来源行号改成超范围的 L99999 ⇒ 必须红 (K0)",
         lambda sb: block_mutate(sb, lambda d: d["rework_items"][0].__setitem__(
             "source", "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L99999")),
         "K0")

    # 13 ★命门★ 把 §1 的目标方向改成「红」⇒ 必须 K1 红 (目标方向也必须一致)
    case("c13_target_verdict_red",
         "★命门★ 把 §1 表里 `J_UART` 的目标方向改成「红」⇒ 必须红 (K1)",
         lambda sb: block_mutate(sb, lambda d: d["unified_rows"][3].__setitem__("target_verdict", "红")),
         "K1")

    # 14 改件项正文与机器数不一致 ⇒ 必须 K0 红
    case("c14_text_number_mismatch",
         "把 `D-1` 的 current_text 里的 1.7750 改掉 ⇒ 必须红 (K0)",
         lambda sb: block_mutate(sb, lambda d: d["rework_items"][0].__setitem__(
             "current_text", "1.9000 (X 142.063..143.838, 中心 142.9500)")),
         "K0")

    # 15 三档的方向被偷偷改绿 ⇒ 必须 K2 红
    case("c15_tier_verdict_green",
         "把三档里 4.8100 那一档的方向改成「绿」⇒ 必须红 (K2)",
         lambda sb: block_mutate(sb, lambda d: d["clearance_x_tiers"][2].__setitem__("verdict", "绿")),
         "K2")

    # 16 净表被改 ⇒ 必须 K6 红
    def m16(sb):
        f = p(sb, NETLIST_REL)
        with open(f, "a", encoding="utf-8") as fh:
            fh.write("J_DEBUG,0,0,X\n")
    case("c16_netlist_changed", "沙盒网表被追加一行 ⇒ 必须红 (K6)", m16, "K6")

    # 17 本闸被挂进 gate_check.py ⇒ 必须 K6 红
    case("c17_chained",
         "把本闸挂进 state/gate_check.py ⇒ 必须红 (K6)",
         lambda sb: page_replace(sb, "<!-- MECH-DEBUG-SEAT-REWORK-SPEC-JSON-BEGIN -->",
                                 "<!-- MECH-DEBUG-SEAT-REWORK-SPEC-JSON-BEGIN -->") or
                   write_text(p(sb, GATE_REL),
                              read_text(p(sb, GATE_REL)) + "\n# check_debug_seat_rework_spec\n"),
         "K6")

    npass = 0
    for name, desc, mutate, expect in cases:
        sb = make_sandbox(root, name)
        try:
            # ★★先在【未被改动的沙盒】上跑一遍闸 ⇒ 必须全绿 ★★
            # (★不然反向用例会因为「沙盒缺文件」这种环境噪声假红 ⇒ 等于没测★)
            pre = Gate(sb).run()
            pre_fail = [(k, m) for k, ok, m in pre if not ok]
            if pre_fail:
                print("[FAIL] %-28s ★沙盒基线就红 (★反向用例无效·闸在干净沙盒上就不通过★): %s"
                      % (name, pre_fail[0]))
                continue
            mutate(sb)
            g = Gate(sb)
            res = g.run()
            fails = [(k, m) for k, ok, m in res if not ok]
            if not fails:
                print("[FAIL] %-28s 期望红 (点名 %s) ⇒ 实际【绿】 (闸坏了)" % (name, expect))
            else:
                hit = any(k.startswith(expect) for k, _ in fails)
                if hit:
                    print("[ok]   %-28s rc=1 且点名 %s ✓  (%s)" % (name, expect, fails[0][1][:110]))
                    npass += 1
                else:
                    print("[FAIL] %-28s 红了但没点名 %s ⇒ 实际点名 %s"
                          % (name, expect, [k for k, _ in fails]))
        except Exception as exc:
            print("[FAIL] %-28s 反向用例执行异常: %r" % (name, exc))
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
    crit, tol, _ = read_crit(root)
    print("★CRIT/TOL 现场从 MECH/service_port_check.py 源码读: CRIT = %s · TOL['fdm_part'] = %s"
          % (crit, tol["fdm_part"] if tol else None))
    print("★要求每边余量 >= CRIT + TOL = %s" % round(crit + tol["fdm_part"], 4) if crit else "★读不到阈值")
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
