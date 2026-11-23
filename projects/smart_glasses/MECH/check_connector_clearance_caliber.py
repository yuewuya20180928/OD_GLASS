#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_connector_clearance_caliber.py —— 座体净距判据【同源化】总表 机器闸
===================================================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零改已签收页 / 零外发 / 不代老板拍板** ★
★**派活**: 项目总工 (main) · ISS-377 · 2026-11-24 派 / 做 · 交卷人 = 结构总工 (mech-lead) ★
★**续做**: cont1 (★上一趟 02:51 被 16 分钟墙掐死 ⇒ 只落了 `logs/iss377/board_connectors.json`★) ★
★**关联**: `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` (★本单新建的同源总表页★) ·
          `HANDOFF/2026-11-24_mech-lead_ISS377_座体净距判据同源化与座体型号自查.md` (交卷页) ★
★**只读引用 (★不改★)**: `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (★必须清空区与开口的真身★) ·
          `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (ISS-371 · 已签收) ·
          `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (ISS-374 · 已签收) ·
          `MECH/service_port_check.py` (★`CRIT` / `TOL` 真身 L126-L127★) ·
          `logs/iss377/board_connectors.json` (★板面实读·上一趟已落★) ★
★**★闸不挂 `state/gate_check.py` (★挂不挂归 main·本闸只自证「没挂」★)★**

────────────────────────────────────────────────────────────────────────────────────────────────────────
【★★本单要防的病根 (★ISS-374 亲手立的病·本闸继承★)★★】
  ★**① 拿一颗件的结论套另一颗** ⇒ K0 (逐格回读既有真相页) + K1 (口径来源逐轴) + 反向用例 1/2/4/11 ★
  ★**② 口径混用 (铜箔支配 vs 座体支配 各算各的)** ⇒ K1 + K2 (口径来源必须与实算分母一致) ★
  ★**③ 余量被当成标量 (只判一个轴)** ⇒ K3 (每行每轴都要判 + 必须存在 X 绿 Y 红的实例) ★

【同源判据链 (★闸自己复算·★不抄表★)】
  M = max(H_housing, C_copper)  (逐轴)      · 开口余量 = (O_opening − M) / 2
  罩住余量 = (H_housing − C_copper) / 2      · 最坏余量 = 余量 − TOL["fdm_part"]
  判据: 最坏余量 ≥ CRIT (★CRIT = 2 × TOL["fdm_part"]·真身 MECH/service_port_check.py L126-L127★)

【九条判据 (★每条 fail-closed·★每条都有反向用例★)】
  K0 §1 同源总表逐行逐格与既有真相页的数一致 (★自己从既有页重新读一遍·★不许抄表★)
  K1 每行 (每轴) 标「清空区口径来源」且不许留空 / 不许 TBD / 表内必须同时有 copper_driven 与 housing_driven
  K2 每行每轴每档的余量与判决自洽 (最坏 = 名义 − TOL; 判决 = 与 CRIT 比对的结果) + 红行与 unknown 行必须挂未决项号
  K3 余量必须按每边向量判 (X/Y 两向都要在) + 必须存在「X 绿 Y 红」的实例
  K4 §2 冲突清单每条必须同时有「后果句」与「判据句」且两句分开
  K5 证据等级五级白名单 + 正文零挂起措辞 + 查不到处必须有 ≥3 条降级方案
  K6 板面零写板自证 (md5 / mtime / size 三项 == 基线)
  K7 已签收件未被改动 (逐字节 md5 不变)
  K8 零挂链 ⇒ 自证 `grep -c check_connector_clearance_caliber state/gate_check.py` == 0

【rc 语义】
  0 = 全部通过   ·   1 = 有断言不通过 (逐条列出 + 点名判据号)   ·   2 = 参数 / IO 错误

【用法】
  python3 MECH/check_connector_clearance_caliber.py             # 扫真件 (只读)
  python3 MECH/check_connector_clearance_caliber.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_connector_clearance_caliber.py --root DIR  # 扫指定树 (反向用例在 tmp/iss377/selftest/ 上做)

【★沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss377/selftest/` (★不许写系统 `/tmp`★)
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

PAGE_REL = "MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md"
CALIBER_REL = "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md"
JDEBUG_REL = "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md"
JUART_REL = "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md"
CRIT_REL = "MECH/service_port_check.py"
GATE_JDEBUG_REL = "MECH/check_jdebug_1p27_clearance.py"
GATE_JUART_REL = "MECH/check_juart_1p27_clearance.py"
PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"
GATE_REL = "state/gate_check.py"
CONN_REL = "logs/iss377/board_connectors.json"

BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime": "2026-11-06 07:07:17.362193413",
    "mtime_ns": 1793920037362193413,
    "size": 4940213,
}

# ★已签收件的逐字节基线 (★ISS-371 / ISS-374 已由 main 签收 verified·★K7 专防「改已签收件」★)★
SIGNED_BASELINE = {
    JDEBUG_REL: "da7b02c013fa49c65b70ed3bea97b787",
    JUART_REL: "ffc099397dc573df207f265bff57dffb",
    GATE_JDEBUG_REL: "a9914b2c3e9f8f92f1fbb60d1d8bdd86",
    GATE_JUART_REL: "ea89e0dd3b2f77828b69f06bbe76969d",
    CALIBER_REL: "b254fa98c09bc7adb058e1d03eb13980",
}

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]", "[推断]", "[推测]", "[估计]", "[大概值]", "[大概]")
# ★挂起措辞白名单 (★本单零外发·★正文不许把缺口推给外部★)★
FORBIDDEN_PHRASES = ("等原厂回信", "等原厂回复", "等待原厂", "等原厂", "待外部确认",
                      "等外部回复", "等待外部回复", "回头再问原厂", "等原厂回覆")
# ★含混结论词 (★ISS-371 口径纪律·继承★)★
FORBIDDEN_VERDICT_WORDS = ("合格", "OK")

CALIBER_SOURCES = ("copper_driven", "housing_driven", "unknown")
TOL = 1e-6


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


def near(a, b, tol=TOL) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def strip_md(s: str) -> str:
    return s.replace("*", "").replace("`", "")


def find_row(text: str, key: str, forbid=()) -> str:
    """按行标签在既有真相页里找那一行 (★带排除词·★避免匹配到「开口左下角可放行区间」★)"""
    for ln in text.splitlines():
        s = strip_md(ln)
        if key in s and not any(f in s for f in forbid):
            return s
    return ""


def parse_xy(s: str):
    """从 'X 142.063..143.838 x Y 55.330..57.870' 里抠出两个区间 ⇒ ((x0,x1),(y0,y1))"""
    s = strip_md(s)
    m = re.search(r"X\s*(-?\d+(?:\.\d+)?)\s*\.\.\s*(-?\d+(?:\.\d+)?)", s)
    if not m:
        return None
    x0, x1 = float(m.group(1)), float(m.group(2))
    m2 = re.search(r"Y\s*(-?\d+(?:\.\d+)?)\s*\.\.\s*(-?\d+(?:\.\d+)?)", s)
    if not m2:
        return None
    y0, y1 = float(m2.group(1)), float(m2.group(2))
    return (x0, x1), (y0, y1)


def extract_json_fence(text: str, marker_begin: str, marker_end: str):
    i = text.find(marker_begin)
    j = text.find(marker_end)
    if i < 0 or j < 0:
        return None
    seg = text[i:j]
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", seg, re.S)
    if not m:
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", seg, re.S)
        if not m:
            return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def extract_json_fence_named(text: str, fence_name: str):
    m = re.search(r"```" + re.escape(fence_name) + r"\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def read_crit(root: str):
    """★CRIT / TOL 真身 (只读·不许写死)★"""
    src = read_text(p(root, CRIT_REL))
    mt = re.search(r"TOL\s*=\s*\{[^}]*\}", src)
    if not mt:
        return None, None, "TOL 真身没找到"
    tol = eval(mt.group(0).split("=", 1)[1])
    mc = re.search(r"CRIT\s*=\s*2\s*\*\s*TOL\[\"fdm_part\"\]", src)
    if not mc:
        return None, None, "CRIT 真身 (L126-L127) 没找到"
    crit = 2 * tol["fdm_part"]
    return crit, tol, None


def source_of_axis(h, c):
    """★口径来源 (数值同源推导·★不许人挑★): H == C ⇒ 座体宽是拿铜箔宽冒充的 ⇒ copper_driven★"""
    if h is None or c is None:
        return "unknown"
    if abs(float(h) - float(c)) < 1e-9:
        return "copper_driven"
    if float(h) > float(c):
        return "housing_driven"
    return "copper_driven"


# ==================================================================================================
# 事实读取 (★只读·★自己重新读一遍·★不许抄表★)
# ==================================================================================================
class Facts(object):
    def __init__(self, root: str):
        self.root = root
        self.errors = []
        self.page = read_text(p(root, PAGE_REL))
        self.block = extract_json_fence(
            self.page, "<!-- MECH-CONNECTOR-CLEARANCE-CALIBER-JSON-BEGIN -->",
            "<!-- MECH-CONNECTOR-CLEARANCE-CALIBER-JSON-END -->")
        self.caliber = read_text(p(root, CALIBER_REL))
        self.jdebug = extract_json_fence(self.jdebug_text(), "<!-- MACHINE-BLOCK-BEGIN -->",
                                         "<!-- MACHINE-BLOCK-END -->")
        self.juart = extract_json_fence_named(self.juart_text(), "MECH-JUART-CLEARANCE-JSON")
        self.conn = json.loads(read_text(p(root, CONN_REL)))
        self.crit, self.tol, err = read_crit(root)
        if err:
            self.errors.append(err)

    def jdebug_text(self):
        return read_text(p(self.root, JDEBUG_REL))

    def juart_text(self):
        return read_text(p(self.root, JUART_REL))

    # ---- 真相页里的 H / O ----
    def housing_opening(self):
        out = {}
        for key, ref in (("J_DEBUG", "调试口"), ("J_UART", "检修口")):
            hrow = find_row(self.caliber, ref + " · 必须清空区", forbid=("可放行",))
            orow = find_row(self.caliber, ref + " · 开口", forbid=("可放行", "必须清空区"))
            hxy = parse_xy(hrow) if hrow else None
            oxy = parse_xy(orow) if orow else None
            if not hxy or not oxy:
                self.errors.append("真相页里找不到 %s 的必须清空区 / 开口行" % key)
                continue
            out[key] = {
                "housing": {"x": round(hxy[0][1] - hxy[0][0], 4), "y": round(hxy[1][1] - hxy[1][0], 4)},
                "housing_x": (hxy[0][1] - hxy[0][0]),
                "housing_y": (hxy[1][1] - hxy[1][0]),
                "opening": {"x": round(oxy[0][1] - oxy[0][0], 4), "y": round(oxy[1][1] - oxy[1][0], 4)},
                "opening_x": (oxy[0][1] - oxy[0][0]),
                "opening_y": (oxy[1][1] - oxy[1][0]),
                "src_h": hrow.strip()[:160], "src_o": orow.strip()[:160],
            }
        return out


# ==================================================================================================
# 判据 K0~K8
# ==================================================================================================
class Gate(object):
    def __init__(self, root: str):
        self.root = root
        self.f = Facts(root)
        self.results = []          # [(K编号, bool, 说明)]

    def chk(self, kid, ok, msg):
        self.results.append((kid, bool(ok), msg))
        return bool(ok)

    # ---------------- K0 ----------------
    def k0(self):
        f = self.f
        if f.block is None:
            return self.chk("K0", False, "页里找不到机器块 JSON (MECH-CONNECTOR-CLEARANCE-CALIBER-JSON)")
        rows = f.block.get("rows") or []
        tiers = f.block.get("tier_rows") or []
        if not rows:
            return self.chk("K0", False, "机器块 rows 为空")
        # (a) 行集合必须 == 板面连接器集合
        board_refs = set(f.conn.keys())
        page_refs = set(r.get("ref") for r in rows)
        if board_refs != page_refs:
            return self.chk("K0", False, "行集合与板面实读不一致: 板=%s 页=%s" %
                            (sorted(board_refs), sorted(page_refs)))
        ho = f.housing_opening()
        # (b) 逐行逐格对拍
        bad = []
        for r in rows:
            ref = r["ref"]
            c = f.conn.get(ref) or {}
            if not near(r["copper"]["x"], c.get("copper_x_width")) or \
               not near(r["copper"]["y"], c.get("copper_y_width")):
                bad.append("%s 铜箔包络与板面实读不一致" % ref)
            if ref in ho:
                h = ho[ref]
                if not near(r["housing"]["x"], h["housing_x"]) or \
                   not near(r["housing"]["y"], h["housing_y"]):
                    bad.append("%s 座体必须清空区与真相页不一致 (页=%s/%s 真身=%s/%s)" %
                               (ref, r["housing"]["x"], r["housing"]["y"],
                                h["housing_x"], h["housing_y"]))
                if not near(r["opening"]["x"], h["opening_x"]) or \
                   not near(r["opening"]["y"], h["opening_y"]):
                    bad.append("%s 开口与真相页不一致" % ref)
                # 口径来源必须与实算分母一致 (★防「口径混用」★) — 归 K2, 这里不重复算
        # (c) tier 档与已签收姊妹页对拍
        for t in tiers:
            ref = t["ref"]
            if ref == "J_DEBUG":
                if not f.jdebug:
                    bad.append("读不到 ISS-371 机器块")
                    continue
                tht = f.jdebug.get("land_tht") or {}
                smd = f.jdebug.get("land_smd") or {}
                if t["tier"] == "official_tht_1x04":
                    if not near(t["copper"]["x"], tht.get("copper_w_along_axis_mm")):
                        bad.append("J_DEBUG THT 铜箔 X 与 ISS-371 机器块不一致")
                    if not near(t["copper"]["y"], tht.get("copper_w_across_axis_mm")):
                        bad.append("J_DEBUG THT 铜箔 Y 与 ISS-371 机器块不一致")
                    oc = f.jdebug.get("calibers", {}).get("official_tht", {})
                    if not near(t["margin_open"]["x"], oc.get("clearance_x_left")):
                        bad.append("J_DEBUG THT 开口 X 余量与 ISS-371 (2.6950) 不一致")
                    if not near(t["worst_open"]["x"], oc.get("worst_clearance_x")):
                        bad.append("J_DEBUG THT 开口 X 最坏余量与 ISS-371 不一致")
                elif t["tier"] == "official_smd_1x04":
                    if not near(t["copper"]["x"], smd.get("copper_w_mm")):
                        bad.append("J_DEBUG SMD 铜箔 X 与 ISS-371 机器块不一致")
                    if not near(t["copper"]["y"], smd.get("copper_h_mm")):
                        bad.append("J_DEBUG SMD 铜箔 Y 与 ISS-371 机器块不一致")
                    c0 = smd.get("centered_rot0") or {}
                    if not near(t["margin_open"]["x"], c0.get("clearance_x_left")):
                        bad.append("J_DEBUG SMD 开口 X 余量与 ISS-371 (2.1000) 不一致")
                    if not near(t["margin_open"]["y"],
                                (c0.get("clearance_y_by_tier") or {}).get("0.90")):
                        bad.append("J_DEBUG SMD 开口 Y 余量与 ISS-371 (0.0700) 不一致")
                    if not near(t["worst_open"]["y"],
                                (c0.get("worst_clearance_y_by_tier") or {}).get("0.90")):
                        bad.append("J_DEBUG SMD 开口 Y 最坏余量与 ISS-371 (-0.2300) 不一致")
            elif ref == "J_UART":
                if not f.juart:
                    bad.append("读不到 ISS-374 JSON 块")
                    continue
                tiers_j = f.juart.get("tiers") or []
                pick = None
                for tj in tiers_j:
                    if t["tier"] == "official_tht_1x02" and tj.get("variant", "").startswith("PinHeader_1x02_P1.27mm_Vertical") \
                       and "SMD" not in tj.get("variant", ""):
                        pick = tj
                    if t["tier"] == "official_smd_1x02" and "SMD" in tj.get("variant", ""):
                        pick = tj
                if pick is None:
                    bad.append("ISS-374 机器块里找不到 %s 对应的档" % t["tier"])
                    continue
                if not near(t["copper"]["x"], pick.get("copper_x_width")):
                    bad.append("%s 铜箔 X 与 ISS-374 机器块不一致" % t["tier"])
                if not near(t["copper"]["y"], pick.get("copper_y_width")):
                    bad.append("%s 铜箔 Y 与 ISS-374 机器块不一致" % t["tier"])
                if not near(t["margin_cover"]["x"], pick.get("margin_nominal")):
                    bad.append("%s 罩住 X 余量与 ISS-374 不一致" % t["tier"])
                if not near(t["worst_cover"]["x"], pick.get("margin_worst")):
                    bad.append("%s 罩住 X 最坏余量与 ISS-374 不一致" % t["tier"])
                if "SMD" in t["tier"]:
                    ovf = pick.get("opening_y_overflow_per_side")
                    if ovf is not None and not near(-t["margin_open"]["y"], ovf):
                        bad.append("%s 开口 Y 余量与 ISS-374 的越界量不一致" % t["tier"])
        # (d) 正文表格与机器块必须一致 (每个位号的关键数都要在正文里出现)
        body = f.page
        for r in rows + tiers:
            ref = r["ref"]
            if ref not in body:
                bad.append("正文里找不到位号 %s" % ref)
                continue
            if r.get("housing") is None:
                continue
            for axis in ("x", "y"):
                for key in ("margin_open", "worst_open", "margin_cover", "worst_cover"):
                    v = (r.get(key) or {}).get(axis)
                    if v is None:
                        continue
                    s = ("%.4f" % v)
                    if s not in body:
                        bad.append("正文里找不到 %s 的 %s %s = %s (正文与机器块不一致)" % (ref, key, axis, s))
        return self.chk("K0", not bad, "; ".join(bad[:12]) if bad else "§1 表逐格与既有真相页一致")

    # ---------------- K1 ----------------
    def k1(self):
        f = self.f
        if f.block is None:
            return self.chk("K1", False, "机器块缺失")
        rows = (f.block.get("rows") or []) + (f.block.get("tier_rows") or [])
        bad = []
        srcs_seen = set()
        for r in rows:
            ref = r.get("ref")
            cs = r.get("caliber_source")
            if not cs:
                bad.append("%s 口径来源为空" % ref)
                continue
            if cs not in CALIBER_SOURCES:
                bad.append("%s 口径来源 %r 不在白名单 %s" % (ref, cs, list(CALIBER_SOURCES)))
                continue
            srcs_seen.add(cs)
            ax = r.get("caliber_source_axes") or {}
            for axis in ("x", "y"):
                v = ax.get(axis)
                if not v:
                    bad.append("%s %s 轴口径来源为空" % (ref, axis))
                elif v not in CALIBER_SOURCES:
                    bad.append("%s %s 轴口径来源 %r 不在白名单" % (ref, axis, v))
            # unknown 行必须挂未决项
            if cs == "unknown" and not (r.get("open_items") or []):
                bad.append("%s 口径来源 unknown 但没挂未决项号" % ref)
            # ★★「口径来源」必须逐行逐轴与实算分母一致 (★与 K2 重叠是故意的 fail-closed 冗余:
            #   ★K1 = 这一列本身可不可信; K2 = 余量与判决自不自洽; 两者都挂才拦得住「口径混用」★)★
            if r.get("housing"):
                for axis in ("x", "y"):
                    H = float(r["housing"][axis]); C = float(r["copper"][axis])
                    want = source_of_axis(H, C)
                    if ax.get(axis) != want:
                        bad.append("%s %s 轴口径来源 %r != 实算分母 %r (★不许拿一颗件的口径套另一颗★)" %
                                   (ref, axis, ax.get(axis), want))
        for need in ("copper_driven", "housing_driven"):
            if need not in srcs_seen:
                bad.append("表里没有 %s 的行 (★口径不许全表一套★)" % need)
        if "TBD" in f.page:
            bad.append("正文里出现 TBD")
        return self.chk("K1", not bad, "; ".join(bad[:12]) if bad else "口径来源逐行逐轴已标且非空")

    # ---------------- K2 ----------------
    def k2(self):
        f = self.f
        if f.block is None:
            return self.chk("K2", False, "机器块缺失")
        if f.crit is None:
            return self.chk("K2", False, "CRIT/TOL 真身读不到")
        if not near(f.crit, 2 * f.tol["fdm_part"]):
            return self.chk("K2", False, "CRIT 真身不等于 2 x TOL['fdm_part']")
        bad = []
        rows = (f.block.get("rows") or []) + (f.block.get("tier_rows") or [])
        for r in rows:
            ref = "%s/%s" % (r.get("ref"), r.get("tier"))
            # 口径来源必须与实算分母一致 (★防「口径混用」★)
            if r.get("housing"):
                for axis in ("x", "y"):
                    H = float(r["housing"][axis]); C = float(r["copper"][axis]); O = float(r["opening"][axis])
                    if r["caliber_source_axes"][axis] != source_of_axis(H, C):
                        bad.append("%s %s 轴口径来源与实算分母不一致" % (ref, axis))
                    # ★算术复算归 K2: 同源化清空区 + 两种余量 + 最坏余量★
                    M = max(H, C)
                    if not near(r["merged"][axis], round(M, 4)):
                        bad.append("%s %s 轴同源化清空区 M 复算不一致" % (ref, axis))
                    mo = (O - M) / 2.0
                    mc = (H - C) / 2.0
                    if r["margin_open"].get(axis) is not None and \
                       not near(r["margin_open"][axis], round(mo, 4)):
                        bad.append("%s %s 轴开口余量复算不一致" % (ref, axis))
                    if r["margin_cover"].get(axis) is not None and \
                       not near(r["margin_cover"][axis], round(mc, 4)):
                        bad.append("%s %s 轴罩住余量复算不一致" % (ref, axis))
                    if r["worst_open"].get(axis) is not None and \
                       not near(r["worst_open"][axis], round(mo - f.tol["fdm_part"], 4)):
                        bad.append("%s %s 轴开口最坏余量复算不一致" % (ref, axis))
                    if r["worst_cover"].get(axis) is not None and \
                       not near(r["worst_cover"][axis], round(mc - f.tol["fdm_part"], 4)):
                        bad.append("%s %s 轴罩住最坏余量复算不一致" % (ref, axis))
            for key in ("margin_open", "worst_open", "margin_cover", "worst_cover"):
                m = (r.get(key) or {})
                w = (r.get("worst_" + key.split("_", 1)[1]) or {}) if key.startswith("margin_") else {}
                if not m or not w:
                    continue
                for axis in ("x", "y"):
                    if m.get(axis) is None or w.get(axis) is None:
                        continue
                    if not near(w[axis], round(float(m[axis]) - f.tol["fdm_part"], 6)):
                        bad.append("%s %s %s 轴: 最坏余量 != 名义 − TOL" % (ref, key, axis))
            # 判决必须与 CRIT 比对结果一致
            for key, pkey in (("margin_open", "pass_open"), ("worst_open", "pass_worst_open"),
                              ("margin_cover", "pass_cover"), ("worst_cover", "pass_worst_cover")):
                m = (r.get(key) or {}); p = (r.get(pkey) or {})
                for axis in ("x", "y"):
                    if m.get(axis) is None or p.get(axis) is None:
                        continue
                    want = (float(m[axis]) >= f.crit)
                    if bool(p[axis]) != want:
                        bad.append("%s %s %s 轴判决与 CRIT 比对结果相反" % (ref, key, axis))
            # 红行必须挂未决项号 (★不许静默红★)
            reds = []
            taut = r.get("cover_tautology") or {}
            for axis in ("x", "y"):
                for key, pkey in (("worst_open", "pass_worst_open"), ("worst_cover", "pass_worst_cover")):
                    if key == "worst_cover" and taut.get(axis):
                        continue
                    p = (r.get(pkey) or {}).get(axis)
                    if p is False:
                        reds.append(axis)
            if reds and not (r.get("open_items") or []):
                bad.append("%s 是红行但没挂未决项号" % ref)
            # verdict 串必须与红绿一致
            v = r.get("verdict") or ""
            if reds and not v.startswith("红"):
                bad.append("%s 实际有红 (%s) 但 verdict 串不是以「红」开头" % (ref, ",".join(reds)))
            if not reds and v.startswith("红"):
                bad.append("%s verdict 串说红但没有红格" % ref)
        return self.chk("K2", not bad, "; ".join(bad[:12]) if bad else "余量与判决逐行逐轴自洽")

    # ---------------- K3 ----------------
    def k3(self):
        f = self.f
        if f.block is None:
            return self.chk("K3", False, "机器块缺失")
        bad = []
        rows = (f.block.get("rows") or []) + (f.block.get("tier_rows") or [])
        have_xy_split = False
        for r in rows:
            ref = "%s/%s" % (r.get("ref"), r.get("tier"))
            if not r.get("housing"):
                continue     # 未建模行 ⇒ 判据是「不许当绿用」(K1/K2 查), 这里不查轴
            for key in ("margin_open", "worst_open", "margin_cover", "worst_cover"):
                m = (r.get(key) or {})
                for axis in ("x", "y"):
                    if m.get(axis) is None:
                        bad.append("%s %s %s 轴余量缺失 (★余量必须按每边向量判★)" % (ref, key, axis))
            px = (r.get("pass_worst_open") or {}).get("x")
            py = (r.get("pass_worst_open") or {}).get("y")
            if px is True and py is False:
                have_xy_split = True
        if not have_xy_split:
            bad.append("表里没有「X 绿 Y 红」的实例 ⇒ 证明不了闸不是只判一个轴")
        return self.chk("K3", not bad, "; ".join(bad[:12]) if bad else "余量按 X/Y 两向向量判且有 X绿Y红 实例")

    # ---------------- K4 ----------------
    def k4(self):
        f = self.f
        if f.block is None:
            return self.chk("K4", False, "机器块缺失")
        bad = []
        conflicts = f.block.get("conflicts") or []
        if len(conflicts) < 2:
            bad.append("冲突清单少于 2 条")
        for c in conflicts:
            for k in ("judgement", "fact", "owner", "title"):
                if not (c.get(k) or "").strip():
                    bad.append("冲突 %s 缺字段 %s" % (c.get("id"), k))
        # 正文 §2 每条必须同时有「判据句」与「后果句」且分开
        body = f.page
        sec2 = ""
        i = body.find("## ★§2 冲突清单")
        j = body.find("## ★§3 座体真实型号自查")
        if i < 0 or j < 0:
            bad.append("正文里找不到 §2 冲突清单段")
        else:
            sec2 = body[i:j]
        blocks = re.split(r"###\s*★★(C\d+)", sec2)
        found = {}
        for k in range(1, len(blocks) - 1, 2):
            found[blocks[k]] = blocks[k + 1]
        if len(found) < 2:
            bad.append("正文 §2 的冲突条目少于 2 条")
        for cid, blk in found.items():
            if "判据句" not in blk:
                bad.append("§2 %s 缺「判据句」" % cid)
            if "后果句" not in blk:
                bad.append("§2 %s 缺「后果句」" % cid)
            if blk.find("判据句") == blk.find("后果句"):
                bad.append("§2 %s 判据句与后果句没分开" % cid)
        for c in conflicts:
            if c.get("id") not in found:
                bad.append("机器块里的冲突 %s 在正文 §2 找不到" % c.get("id"))
        return self.chk("K4", not bad, "; ".join(bad[:12]) if bad else "§2 每条冲突都有分开的判据句/后果句")

    # ---------------- K5 ----------------
    def k5(self):
        f = self.f
        if f.block is None:
            return self.chk("K5", False, "机器块缺失")
        bad = []
        body = f.page
        for e in EVIDENCE_WHITELIST:
            pass
        # 证据等级: 页里出现的所有 [xxx] 标签必须命中白名单
        for tag in set(re.findall(r"\[[^\[\]]{1,12}\]", body)):
            if tag in EVIDENCE_WHITELIST:
                continue
            if re.match(r"^\[[A-Za-z0-9_\- ]+\]$", tag):
                continue      # 形如 [实测] 之外的普通方括号 (如 [0数据] 已在白名单)
            if re.match(r"^\[[^\]]{1,12}\]$", tag) and not tag.startswith("[★"):
                # 中文标签 ⇒ 必须是五级白名单之一
                if re.search(r"[一-鿿]", tag) and tag not in EVIDENCE_WHITELIST:
                    bad.append("出现白名单外的证据等级标签 %s" % tag)
        for bad_tag in FORBIDDEN_EVIDENCE:
            if bad_tag in body:
                bad.append("出现禁用证据等级 %s" % bad_tag)
        for ph in FORBIDDEN_PHRASES:
            if ph in body:
                bad.append("正文出现挂起措辞 %s" % ph)
        for w in FORBIDDEN_VERDICT_WORDS:
            if w in body:
                bad.append("正文出现含混结论词 %s" % w)
        # 查不到处必须有降级方案 (★必须项★)
        dps = f.block.get("degrade_plans") or []
        if len(dps) < 3:
            bad.append("降级方案少于 3 条 (★必须项★)")
        dp_ids = set(d.get("id") for d in dps)
        for need in ("DP-1", "DP-2", "DP-3"):
            if need not in dp_ids:
                bad.append("缺任务书点名的降级候选 %s (★降级方案是必须项, 不是可选项★)" % need)
        for d in dps:
            for k in ("basis", "cost", "affects"):
                if not d.get(k):
                    bad.append("降级方案 %s 缺 %s" % (d.get("id"), k))
        if "降级方案" not in body:
            bad.append("正文里没有「降级方案」段")
        if "[0数据]" in body and not dps:
            bad.append("正文有 [0数据] 但机器块里没有降级方案")
        # 型号自查: 厂商料号列必须存在, 且 [0数据] 处必须挂降级方案
        pm = f.block.get("part_models") or {}
        if len(pm) < 6:
            bad.append("座体型号自查条目少于 6 条")
        for k, v in pm.items():
            if not v.get("value"):
                bad.append("型号条目 %s 缺板面 value" % k)
        return self.chk("K5", not bad, "; ".join(bad[:12]) if bad else "证据等级白名单 + 零挂起措辞 + 降级方案齐全")

    # ---------------- K6 ----------------
    def k6(self):
        path = p(self.root, PCB_REL)
        if not os.path.exists(path):
            return self.chk("K6", False, "板文件不存在")
        md5 = md5_of(path)
        st = os.stat(path)
        mtime_ns = st.st_mtime_ns
        size = st.st_size
        bad = []
        if md5 != BOARD_BASELINE["md5"]:
            bad.append("板 md5 %s != 基线 %s" % (md5, BOARD_BASELINE["md5"]))
        if size != BOARD_BASELINE["size"]:
            bad.append("板 size %d != 基线 %d" % (size, BOARD_BASELINE["size"]))
        if mtime_ns != BOARD_BASELINE["mtime_ns"]:
            import datetime
            got = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
            bad.append("板 mtime %s (ns=%d) != 基线 %s" % (got, mtime_ns, BOARD_BASELINE["mtime"]))
        return self.chk("K6", not bad, "; ".join(bad) if bad else "板 md5/mtime/size 三项 == 基线")

    # ---------------- K7 ----------------
    def k7(self):
        bad = []
        for rel, want in SIGNED_BASELINE.items():
            path = p(self.root, rel)
            if not os.path.exists(path):
                bad.append("%s 不存在" % rel)
                continue
            got = md5_of(path)
            if got != want:
                bad.append("%s md5 %s != 已签收基线 %s" % (rel, got, want))
        return self.chk("K7", not bad, "; ".join(bad) if bad else "已签收页/闸逐字节未变")

    # ---------------- K8 ----------------
    def k8(self):
        path = p(self.root, GATE_REL)
        if not os.path.exists(path):
            return self.chk("K8", False, "state/gate_check.py 不存在")
        txt = read_text(path)
        n = txt.count("check_connector_clearance_caliber")
        return self.chk("K8", n == 0, "gate_check.py 里出现 %d 次 check_connector_clearance_caliber (必须 0)" % n
                        if n else "零挂链 (grep -c == 0)")

    # ---------------- 汇总 ----------------
    def run(self):
        self.k0(); self.k1(); self.k2(); self.k3(); self.k4(); self.k5(); self.k6(); self.k7(); self.k8()
        if self.f.errors:
            for e in self.f.errors:
                self.results.append(("K0", False, "读取错误: %s" % e))
        return self.results


# ==================================================================================================
# 反向用例 (--selftest)
# ==================================================================================================
SANDBOX_FILES = [PAGE_REL, CALIBER_REL, JDEBUG_REL, JUART_REL, CRIT_REL,
                 GATE_JDEBUG_REL, GATE_JUART_REL, PCB_REL, GATE_REL, CONN_REL]


def make_sandbox(root: str, case: str):
    """建一份只含必要文件的影子树 (★落项目盘 tmp/iss377/selftest/<case>/★)"""
    sb = os.path.join(root, "tmp", "iss377", "selftest", case)
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    for rel in SANDBOX_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)     # ★copy2 保 mtime·★否则 K6 会在影子里假红★
    return sb


def mutate_page(sb, fn):
    path = os.path.join(sb, PAGE_REL)
    txt = open(path, encoding="utf-8").read()
    txt2 = fn(txt)
    assert txt2 != txt, "反向用例的变异没有生效"
    open(path, "w", encoding="utf-8").write(txt2)


def block_mutate(sb, fn):
    """变异机器块 JSON (★重新序列化回页★)"""
    path = os.path.join(sb, PAGE_REL)
    txt = open(path, encoding="utf-8").read()
    i = txt.find("<!-- MECH-CONNECTOR-CLEARANCE-CALIBER-JSON-BEGIN -->")
    j = txt.find("<!-- MECH-CONNECTOR-CLEARANCE-CALIBER-JSON-END -->")
    seg = txt[i:j]
    m = re.search(r"```json\s*(\{.*\})\s*```", seg, re.S)
    data = json.loads(m.group(1))
    fn(data)
    new_seg = seg[:m.start()] + "```json\n" + json.dumps(data, ensure_ascii=False, indent=1) + "\n```" + seg[m.end():]
    open(path, "w", encoding="utf-8").write(txt[:i] + new_seg + txt[j:])


def find_row_obj(data, ref, tier=None):
    for r in (data.get("rows") or []) + (data.get("tier_rows") or []):
        if r.get("ref") == ref and (tier is None or r.get("tier") == tier):
            return r
    return None


def run_case(root, case, mutate, expect):
    sb = make_sandbox(root, case)
    mutate(sb)
    g = Gate(sb)
    res = g.run()
    reds = sorted(set(kid for kid, ok, _ in res if not ok))
    ok = (reds == sorted(expect))
    detail = []
    for kid, good, msg in res:
        if not good:
            detail.append("%s: %s" % (kid, msg[:160]))
    return ok, reds, detail


def selftest(root):
    cases = []

    # ① ★把 J_UART 的口径来源从 housing_driven 改成 copper_driven ⇒ K1/K2 必红★
    def m1(sb):
        def f(data):
            r = find_row_obj(data, "J_UART", "status_quo")
            r["caliber_source"] = "copper_driven"
            r["caliber_source_axes"]["x"] = "copper_driven"
            r["caliber_source_axes"]["y"] = "copper_driven"
        block_mutate(sb, f)
    cases.append(("M1 J_UART 口径来源 housing_driven -> copper_driven (★拿一颗件的口径套另一颗★)",
                  m1, {"K1", "K2"}))

    # ② ★把 J_UART 的座体必须清空区 X 宽抄成 J_DEBUG 的 4.8100 ⇒ K0/K2 必红★
    def m2(sb):
        def f(data):
            r = find_row_obj(data, "J_UART", "status_quo")
            r["housing"]["x"] = 4.81
        block_mutate(sb, f)
    cases.append(("M2 J_UART 座体必须清空区 X 宽 2.5400 -> 4.8100 (★抄 J_DEBUG 的数★)",
                  m2, {"K0", "K2"}))

    # ③ ★把 J_UART 换 SMD 变体那档的 Y 向余量删掉 ⇒ K3 必红★
    def m3(sb):
        def f(data):
            r = find_row_obj(data, "J_UART", "official_smd_1x02")
            r["margin_open"]["y"] = None
            r["worst_open"]["y"] = None
            r["pass_open"]["y"] = None
            r["pass_worst_open"]["y"] = None
        block_mutate(sb, f)
    cases.append(("M3 J_UART SMD 档 Y 向余量删掉 (★只留 X 向★)", m3, {"K3"}))

    # ④ ★把 J_DEBUG 的口径来源改成 housing_driven (★与实算分母相反★) ⇒ K2 必红★
    def m4(sb):
        def f(data):
            r = find_row_obj(data, "J_DEBUG", "status_quo")
            r["caliber_source"] = "housing_driven"
            r["caliber_source_axes"]["x"] = "housing_driven"
        block_mutate(sb, f)
    cases.append(("M4 J_DEBUG 口径来源 copper_driven -> housing_driven (★口径混用★)", m4, {"K1", "K2"}))

    # ⑤ 板被写 ⇒ K6 必红
    def m5(sb):
        path = os.path.join(sb, PCB_REL)
        with open(path, "r+b") as fh:
            fh.seek(0)
            fh.write(b"\x00")
    cases.append(("M5 板文件被改一个字节 ⇒ 零写板自证红", m5, {"K6"}))

    # ⑥ 已签收闸被改 ⇒ K7 必红
    def m6(sb):
        path = os.path.join(sb, GATE_JDEBUG_REL)
        with open(path, "ab") as fh:
            fh.write(b"\n# ISS-377 selftest mutation\n")
    cases.append(("M6 已签收闸 check_jdebug_1p27_clearance.py 被追加一行 ⇒ K7 红", m6, {"K7"}))

    # ⑦ 挂链 ⇒ K8 必红
    def m7(sb):
        path = os.path.join(sb, GATE_REL)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n# ISS-377 selftest: MECH/check_connector_clearance_caliber.py\n")
    cases.append(("M7 把新闸挂进 state/gate_check.py ⇒ K8 红", m7, {"K8"}))

    # ⑧ §2 某条冲突缺「后果句」 ⇒ K4 必红
    def m8(sb):
        def f(txt):
            return txt.replace("★**★后果句 (事实层)**: ★**`J_UART` 换官方 SMD 变体",
                               "★**★后果X (事实层)**: ★**`J_UART` 换官方 SMD 变体", 1)
        mutate_page(sb, f)
    cases.append(("M8 §2 的 C2 删掉「后果句」标记 ⇒ K4 红", m8, {"K4"}))

    # ⑨ 证据等级越界 ⇒ K5 必红
    def m9(sb):
        def f(data):
            r = find_row_obj(data, "J_DEBUG", "status_quo")
            r["evidence"] = "[推断]+[推算]"
        block_mutate(sb, f)
    cases.append(("M9 证据等级 [实测] -> [推断] (白名单外) ⇒ K5 红", m9, {"K5"}))

    # ⑩ 降级方案少于 3 条 ⇒ K5 必红
    def m10(sb):
        def f(data):
            data["degrade_plans"] = [d for d in (data.get("degrade_plans") or []) if d.get("id") != "DP-3"]
        block_mutate(sb, f)
    cases.append(("M10 删掉一条降级方案 (DP-3) ⇒ K5 红", m10, {"K5"}))

    # ⑪ 表里删掉一颗连接器 ⇒ K0 必红 (★不许少列一颗件★)
    def m11(sb):
        def f(data):
            data["rows"] = [r for r in (data.get("rows") or []) if r.get("ref") != "J_USB_C"]
        block_mutate(sb, f)
    cases.append(("M11 同源表删掉 J_USB_C 一行 ⇒ K0 红", m11, {"K0"}))

    # ⑫ 最坏余量被改 (不自洽) ⇒ K2 必红
    def m12(sb):
        def f(data):
            r = find_row_obj(data, "J_DEBUG", "status_quo")
            r["worst_open"]["x"] = 3.9135
        block_mutate(sb, f)
        def g(txt):
            return txt.replace("3.9125", "3.9135")
        mutate_page(sb, g)
    cases.append(("M12 J_DEBUG 现状开口 X 最坏余量被改成不自洽的数 ⇒ K2 红", m12, {"K2"}))

    # ⑬ 正文挂起措辞 ⇒ K5 必红
    def m13(sb):
        def f(txt):
            return txt.replace("### ★§3.2 降级方案", "### ★§3.2 降级方案 (★等原厂回信后再定★)", 1)
        mutate_page(sb, f)
    cases.append(("M13 正文出现挂起措辞 ⇒ K5 红", m13, {"K5"}))

    print("=== SELFTEST: %d 条反向用例 ===" % len(cases))
    failed = 0
    for name, mut, expect in cases:
        ok, reds, detail = run_case(root, name.split(" ")[0], mut, expect)
        status = "PASS" if ok else "FAIL"
        print("[%s] %s" % (status, name))
        print("        期望红集=%s 实得红集=%s" % (sorted(expect), reds))
        if not ok:
            failed += 1
            for d in detail:
                print("        ! %s" % d)
    print("selftest: %d/%d 通过" % (len(cases) - failed, len(cases)))
    if failed:
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS")
    return 0


# ==================================================================================================
def main():
    ap = argparse.ArgumentParser(description="ISS-377 座体净距判据同源化 机器闸 (只读)")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例 (末行 ALL TESTS PASS)")
    ap.add_argument("--root", default=PROJ, help="项目根 (★反向用例在影子树上跑★)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest(root)
    g = Gate(root)
    res = g.run()
    print("=== ISS-377 · MECH/check_connector_clearance_caliber.py ===")
    print("页: %s" % os.path.relpath(p(root, PAGE_REL), root))
    print("CRIT=%.4f (真身 %s L126-L127) TOL[fdm_part]=%.4f" %
          (g.f.crit if g.f.crit else -1, CRIT_REL, g.f.tol["fdm_part"] if g.f.tol else -1))
    print("-" * 78)
    for kid, ok, msg in res:
        print("%-4s %-6s %s" % (kid, "PASS" if ok else "FAIL", msg))
    print("-" * 78)
    nfail = sum(1 for _, ok, _ in res if not ok)
    if nfail:
        print("RESULT: FAIL (%d 条不通过)" % nfail)
        return 1
    print("RESULT: PASS (9/9 判据通过)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
