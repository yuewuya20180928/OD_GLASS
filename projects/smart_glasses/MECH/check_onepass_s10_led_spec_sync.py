#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_onepass_s10_led_spec_sync.py —— ★★【ISS-367 · mech-lead · S10 换封装后
LED 窗口规格同趟重算 · 机器闸】★★

★★★**★这个闸守的是什么★**★★
  「板只改一次」那一趟的 **S10 步** 把 `D_LED_G` 换成官方 `0805` land ⇒
  ★**`D_LED_G` 的铜箔相对封装原点的包络 `rel` 变** ⇒
  ★**`MECH/check_board_frame_coords.py` 的 `led_space()` 算出来的
  【两条整高自由带】/【封装原点窗口】/【可落位块数】/【净距敏感度 sweep】全变** ★
  ⇒ ★**而 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块与
  `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格还是旧数** ⇒
  ★**那一趟按旧数布局 ⇒ LED 落位超框 / 结构件装不下 ⇒ 板 md5 第二次变 ⇒ 整趟白跑** ★
  ⇒ ★**本闸把这一跳的结论【钉成机器判据】**: 规格页 + 两处定点改写 + 四组数 + 非单调 ★

  闸的七条:
    L0  ★**基准块** ★ —— 规格页 `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` 的机器块存在且是合法 JSON
    L1  ★**四组数由脚本自己实算** ★ —— ★**页里写的【可落位块数 / 两条可放行带 / sweep】
         == 脚本实算的数** ★ (★实算源 = 本机 KiCad 库里的官方 `.kicad_mod` + 板面现占位 land★
         ★**只读 import `MECH/check_board_frame_coords.py` 的 `led_space()` ⇒ 判据函数零漂移**★)
    L2  ★**sweep 非单调必须被显式承认** ★ (★clr=0.5 的值 < clr=0.2 的值 ⇒ 页里写「单调」= 红★)
    L3  ★**两处定点改写不许与实算打架** ★ —— `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块的
         `led.full_height_bands` / `led.clearance_sweep` 与
         `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 机器块的 `led_window_g_bench_hard`
         都必须 == 实算 ⇒ ★**两处 + 页 三份同源 ⇒ 不可能打架** ★
    L4  ★**证据等级五级白名单** ★ (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ ★写 `[官方]` = 红★)
         + §0~§5 每节至少一个等级
    L5  ★**正文零挂起措辞** ★ (★禁「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」★)
    L6  ★**沙盒在项目盘 `tmp/`** ★ (★不许指到 `/tmp`★)

  ★**只读 import 两个既有闸** (`MECH/check_board_frame_coords.py` 取 `led_space()` 判据函数 ·
  `MECH/check_onepass_s10_fp_swap_impact.py` 取 S10 靶子 `ref → lib:name` 映射) ★
  ★**一个字节不改既有 MECH 判据脚本** ★ ★**真板一个字节不写** ★ ★**零落表** ★

用法:
    python3 MECH/check_onepass_s10_led_spec_sync.py            # rc=0 = 全绿
    python3 MECH/check_onepass_s10_led_spec_sync.py --json     # 机器读
    python3 MECH/check_onepass_s10_led_spec_sync.py --compute  # 只打实算数
    python3 MECH/check_onepass_s10_led_spec_sync.py --selftest # rc=0 = 反向用例全抓到
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))

SPEC_REL = os.path.join("MECH", "BOARD_ONEPASS_S10_LED_SPEC_SYNC.md")
SYNC_REL = os.path.join("MECH", "BOARD_ONEPASS_MECH_SYNC.md")
CALIB_REL = os.path.join("MECH", "BOARD_PORT_OPENING_S6_FRAME_CALIBER.md")

MACH_BEGIN = "<!-- MACHINE-BLOCK-BEGIN -->"
MACH_END = "<!-- MACHINE-BLOCK-END -->"

LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
LED_REF = "D_LED_G"

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]",)
FORBIDDEN_PENDING = ("等原厂回信", "等供应商确认", "待外部回复", "等确认")

# ★净距敏感度 sweep 的四档 (★与 `MECH/check_board_frame_coords.py` 的 `compute()` 同口径★)
CLR_LIST = (0.0, 0.10, 0.20, 0.50)

# ★★【S10 的 MECH 侧 25 件子集】★★
#   ★**口径** = `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` §1.1 的规则 A∪B∪C ★
#     A (10 件) = 落在 `cal:S6_TARGETS` 的 20 个目标落位里 ⇒ 落位/净距判据要重算
#     B (13 件) = 挂在 MECH 侧四条结构要素上 (结构光孔 / ESD 位置 / 键位键孔 / 腔体高度本体)
#     C ( 2 件) = 换封装后闸口径最小净距变化 |Δ| ≥ 0.500 mm ⇒ 净距敏感件
#   ★**为什么必须换满 25 件而不是只换 `D_LED_G`** ★
#     `led_space()` 拿【板上每一个封装的铜箔外框】当障碍 ⇒ ★**别的件换了 land ⇒ 障碍集变了
#     ⇒ 两条带 / 块数 / sweep 跟着变** ★ ⇒ ★**只换 LED 一件算出来的数 ≠ 那一趟的真数** ★
#   ★**目标 `lib:name` 不写死在本文件里** ⇒ ★**从权威台账读**
#     (`HW/FP_TRUTH_BASELINE.md` §2 + `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2) ⇒ 零漂移 ★
S10_MECH_REFS = (
    # --- A (10 件) · S6 目标落位 ---
    "R_SEL_D0_N", "R_SEL_D0_P", "R_SEL_D1_N", "R_SEL_D1_P", "R_SEL_CK_N",
    "R_SEL_CK_P", "R_SEL_D2_N", "R_SEL_D2_P", "R_SEL_D3_N", "R_SEL_D3_P",
    # --- B (13 件) · MECH 四条结构要素 ---
    "D_LED_G", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D",
    "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST",
    "FB_DEMO", "Q_AND", "Q_ENVC", "Q_PG",
    # --- C ( 2 件) · 净距敏感件 ---
    "R_LED_G", "R_PU_I2CB_SCL",
)

# ★§0~§5 六节 (★L4 逐节查证据等级★)
REQUIRED_SECTIONS = ("§0", "§1", "§2", "§3", "§4", "§5")

# ★★【L4 · 「什么算证据等级」这一步的定义 (★ISS-367 CONT1 修 L4 自身假红★)】★★
#   ★**判据方向 (五级白名单) 一字不许改** ★ —— 白名单仍是那 5 个, 写了别的照样红
#   ★**病灶 (产生点)** ★: 老版拿 `re.findall(r"\[[^\]\n]{1,14}\]", body)` 把【方括号包裹的任意内容】
#     都当「证据等级标记」来判 ⇒ ★**几何区间 `[−0.750, +2.150]` / 数组字面量 `["placeable"]`
#     全被误判成「等级」⇒ 假红** ★
#   ★**修法 (只落在这一步·判据方向不动)** ★:
#     ★**只有「长得像等级标签」的方括号 token 才拿来判白名单** ★
#       · 内容全部由【中文表意文字 + ASCII 数字】构成 (★证据等级就是中文标签: 官网/实测/媒体/推算/0数据★)
#       · 且【至少含一个中文表意文字】(★纯数字下标如 `arr[0]` 不是等级标签★)
#       · 且不是 Markdown 链接的链接文字 (`[文字](url)`)
#     ★**其余方括号内容 (数值区间 / 数组字面量 / 键名 / 普通括注) 一律不当等级** ★
#   ⇒ 老红仍是红: `[官方]` (禁用名单) · `[推断]` / `[推测]` / `[估计]` 等非白名单标签 ⇒ 红
_EVID_TOKEN_RE = re.compile(r"\[([^\]\n]{1,14})\]")
_EVID_LIKE_RE = re.compile(r"^[\u4e00-\u9fff0-9]{1,14}$")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def _evidence_tokens(body):
    """★**只挑出「像证据等级标签」的方括号 token** ★
    ★**几何区间 / 数组字面量 / 键名 / 普通括注 / 纯数字下标 一律不挑** ★ ⇒ 不再假红"""
    out = []
    for m in _EVID_TOKEN_RE.finditer(body):
        content = m.group(1)
        if not _EVID_LIKE_RE.match(content):
            continue
        if not _CJK_RE.search(content):
            continue                      # ★纯数字 (★代码下标如 `arr[0]`★) ⇒ 不是等级标签 ★
        if body[m.end():m.end() + 1] == "(" and m.group(0) not in EVIDENCE_WHITELIST \
                and m.group(0) not in FORBIDDEN_EVIDENCE:
            continue                      # Markdown 链接的链接文字 ⇒ 不是等级标签
        out.append(m.group(0))
    return out


# ==================================================================================================
# 只读 import 既有闸 (★判据函数零漂移★)
# ==================================================================================================
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_cfc(root):
    return _load(os.path.join(root, "MECH", "check_board_frame_coords.py"),
                 "iss367_cfc_readonly")


def load_fp_gate(root):
    return _load(os.path.join(root, "MECH", "check_onepass_s10_fp_swap_impact.py"),
                 "iss367_fp_gate_readonly")


# ==================================================================================================
# 板文件只读扫描: 取每个 ref 的封装旋转角
# ==================================================================================================
def board_footprint_rots(root):
    path = os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb")
    lines = open(path, "r", encoding="utf-8").read().split("\n")
    rots = {}
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("(footprint"):
            depth, j = 0, i
            while j < len(lines):
                depth += lines[j].count("(") - lines[j].count(")")
                if depth == 0 and j > i:
                    break
                j += 1
            blk = "\n".join(lines[i:j + 1])
            m = re.search(r'\(property "Reference" "([^"]+)"', blk)
            at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
            if m and at:
                rots[m.group(1)] = float(at.group(3)) if at.group(3) else 0.0
            i = j + 1
        else:
            i += 1
    return rots


# ==================================================================================================
# 官方 `.kicad_mod` 只读解析 (★只取两个/多个焊盘的 (x, y, size_x, size_y)★)
# ==================================================================================================
PAD_RE = re.compile(
    r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s+\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)'
    r'(?:\s*\(size ([-\d.]+) ([-\d.]+)\))?')


def mod_pads(path):
    text = open(path, "r", encoding="utf-8").read()
    out = []
    for m in PAD_RE.finditer(text):
        num, ptype, shape, px, py, _prot, sx, sy = m.groups()
        try:
            sx = float(sx) if sx else 0.0
            sy = float(sy) if sy else 0.0
        except (TypeError, ValueError):
            sx = sy = 0.0
        out.append({"num": num, "type": ptype, "px": float(px), "py": float(py),
                    "sx": sx, "sy": sy})
    return out


def _rot(dx, dy, deg):
    r = math.radians(deg)
    return (dx * math.cos(r) - dy * math.sin(r), dx * math.sin(r) + dy * math.cos(r))


def patch_footprint(fp, pads, rot_deg):
    """★把一个封装的铜箔按官方 land 换掉 (★位置/旋转沿用板上原封装 ⇒ 不挪位★) ★"""
    ox, oy = fp["at"]
    newpads = []
    for p in pads:
        dx, dy = _rot(p["px"], p["py"], rot_deg)
        sx, sy = p["sx"], p["sy"]
        if abs((rot_deg % 180.0) - 90.0) < 1e-6:
            sx, sy = sy, sx
        newpads.append({"num": p["num"], "type": p["type"],
                        "x": ox + dx, "y": oy + dy, "sx": sx, "sy": sy})
    return dict(fp, pads=newpads)


# ==================================================================================================
# S10 靶子映射 (★从权威台账读, 不写死★)
# ==================================================================================================
def target_map(root, fp_gate):
    tgt = dict(fp_gate.read_iss356_targets(root))
    tgt.update(fp_gate.read_gap_targets(root))
    return tgt


def swap_set(board, refs, tmap, rots):
    """★按官方 land 换掉给定 refs 的铜箔 ⇒ 返回一份【新的 board dict】(★真板不动★) ★"""
    fps = dict(board["fps"])
    used = []
    for ref in refs:
        lib = tmap.get(ref)
        if not lib:
            continue
        libname, fpname = lib.split(":", 1)
        path = os.path.join(LIBROOT, "%s.pretty" % libname, "%s.kicad_mod" % fpname)
        if not os.path.exists(path):
            continue
        fp = fps.get(ref)
        if fp is None:
            continue
        fps[ref] = patch_footprint(fp, mod_pads(path), rots.get(ref, 0.0))
        used.append({"ref": ref, "target": lib, "mod": path})
    return dict(board, fps=fps), used


# ==================================================================================================
# 实算
# ==================================================================================================
def _band(b):
    return {"x0": round(b["ox0"], 4), "x1": round(b["ox1"], 4),
            "y0": round(b["oy0"], 4), "y1": round(b["oy1"], 4),
            "w": round(b.get("w", 0.0), 4)}


def summarize(ls, sweep):
    return {
        "rel_bbox": [round(v, 4) for v in (ls.get("led_rel_bbox") or [])],
        "origin_window": [round(v, 4) for v in (ls.get("origin_window") or [])],
        "n_placeable": len(ls.get("placeable", [])),
        "full_height_bands": [_band(b) for b in ls.get("full_height_bands", [])],
        "nearest_band": _band(ls["nearest_band"]) if ls.get("nearest_band") else None,
        "clearance_sweep": [{"clr": round(s["clearance"], 4),
                             "n_placeable": s["n_placeable_bands"],
                             "corner_len_mm": round(s["led_gd_dist"], 6)
                             if s.get("led_gd_dist") is not None else None,
                             "nearest_origin": [round(v, 4) for v in s["nearest_origin"]]
                             if s.get("nearest_origin") else None}
                            for s in sweep],
        "monotonic": all(sweep[i]["n_placeable_bands"] <= sweep[i + 1]["n_placeable_bands"]
                         for i in range(len(sweep) - 1)),
    }


def compute(root):
    cfc = load_cfc(root)
    fp_gate = load_fp_gate(root)
    board = cfc.read_board(root)
    comp = cfc.compute(root)                       # ★含 openings + BEFORE 的 led_space / sweep★
    rots = board_footprint_rots(root)
    tmap = target_map(root, fp_gate)

    before = summarize(comp["led_space"], comp["led_space_sweep"])

    # ---- AFTER (S10 MECH 侧 25 件换官方 land) ----
    patched, used = swap_set(board, S10_MECH_REFS, tmap, rots)
    after_bands = []
    for clr in CLR_LIST:
        sp = cfc.led_space(patched, comp, clr=clr)
        near = sp["nearest_to_r_led_g"][0] if sp["nearest_to_r_led_g"] else None
        after_bands.append({"clearance": clr,
                            "n_placeable_bands": len(sp["placeable"]),
                            "n_full_height": len(sp["full_height_bands"]),
                            "nearest_origin": list(near["origin"]) if near else None,
                            "led_gd_dist": near["dist"] if near else None})
    after = summarize(cfc.led_space(patched, comp, clr=0.0), after_bands)

    # ---- 敏感度: 若那一趟把 90 件全换 (★只报数, 不作判决★) ----
    allrefs = sorted(tmap.keys())
    patched90, used90 = swap_set(board, allrefs, tmap, rots)
    b90 = []
    for clr in CLR_LIST:
        sp = cfc.led_space(patched90, comp, clr=clr)
        b90.append({"clearance": clr, "n_placeable_bands": len(sp["placeable"])})
    after90 = summarize(cfc.led_space(patched90, comp, clr=0.0), b90)

    return {"before": before, "after": after, "after_all90": after90,
            "swap_used": used, "swap_n": len(used),
            "swap_all90_n": len(used90),
            "led_origin": list(board["fps"][LED_REF]["at"]) if LED_REF in board["fps"] else None}


# ==================================================================================================
# 页面 / 机器块读取
# ==================================================================================================
def read_spec(path):
    text = open(path, encoding="utf-8").read()
    b, e = text.find(MACH_BEGIN), text.find(MACH_END)
    if b < 0 or e < 0:
        raise ValueError("缺机器块标记 %s / %s" % (MACH_BEGIN, MACH_END))
    m = re.search(r"```json\n(.*?)\n```", text[b:e], re.S)
    if not m:
        raise ValueError("机器块不是 ```json 围栏")
    return text, json.loads(m.group(1))


def read_json_block(path):
    text = open(path, encoding="utf-8").read()
    b, e = text.find(MACH_BEGIN), text.find(MACH_END)
    if b < 0 or e < 0:
        raise ValueError("缺机器块标记 %s / %s" % (MACH_BEGIN, MACH_END))
    m = re.search(r"```json\n(.*?)\n```", text[b:e], re.S)
    if not m:
        raise ValueError("机器块不是 ```json 围栏")
    return text, json.loads(m.group(1))


def read_yaml_block(path):
    text = open(path, encoding="utf-8").read()
    b, e = text.find(MACH_BEGIN), text.find(MACH_END)
    if b < 0 or e < 0:
        raise ValueError("缺机器块标记 %s / %s" % (MACH_BEGIN, MACH_END))
    m = re.search(r"```yaml\n(.*?)\n```", text[b:e], re.S)
    if not m:
        raise ValueError("机器块不是 ```yaml 围栏")
    import yaml
    return text, yaml.safe_load(m.group(1))


def _f4(v):
    return round(float(v), 4)


def _bands_eq(page_bands, calc_bands):
    if len(page_bands or []) != len(calc_bands or []):
        return False, "条数不等 (页 %s / 实算 %s)" % (len(page_bands or []), len(calc_bands or []))
    for p, c in zip(page_bands, calc_bands):
        for k in ("x0", "x1", "y0", "y1"):
            if abs(float(p.get(k, 1e9)) - float(c[k])) > 5e-4:
                return False, "%s 不等 (页 %s / 实算 %s)" % (k, p.get(k), c[k])
    return True, ""


def _sweep_eq(page_sweep, calc_sweep):
    if len(page_sweep or []) != len(calc_sweep or []):
        return False, "条数不等 (页 %s / 实算 %s)" % (len(page_sweep or []), len(calc_sweep or []))
    for p, c in zip(page_sweep, calc_sweep):
        if abs(float(p.get("clr", -1)) - float(c["clr"])) > 1e-6:
            return False, "clr 不等 (页 %s / 实算 %s)" % (p.get("clr"), c["clr"])
        if int(p.get("n_placeable", -1)) != int(c["n_placeable"]):
            return False, "clr=%s 的块数不等 (页 %s / 实算 %s)" % (
                c["clr"], p.get("n_placeable"), c["n_placeable"])
    return True, ""


# ==================================================================================================
# 判据
# ==================================================================================================
def run_checks(root, spec_path=None, sync_path=None, calib_path=None):
    spec_path = spec_path or os.path.join(root, SPEC_REL)
    sync_path = sync_path or os.path.join(root, SYNC_REL)
    calib_path = calib_path or os.path.join(root, CALIB_REL)
    res = {}
    facts = {}

    # ---- L0 基准块 ----
    try:
        text, mb = read_spec(spec_path)
        res["L0"] = {"ok": True, "errs": []}
    except Exception as exc:                                  # noqa: BLE001
        res["L0"] = {"ok": False, "errs": ["L0 基准块读不到或不是合法 JSON: %s" % exc]}
        return res, facts
    facts["spec_path"] = spec_path

    calc = compute(root)
    facts.update({"before": calc["before"], "after": calc["after"],
                  "after_all90": calc["after_all90"],
                  "swap_n": calc["swap_n"], "swap_all90_n": calc["swap_all90_n"]})

    after = mb.get("led_space_after") or {}
    before = mb.get("led_space_before") or {}

    # ---- L1 页里写的四组数 == 实算 ----
    errs = []
    if not after:
        errs.append("L1 机器块缺 `led_space_after`")
    else:
        if int(after.get("n_placeable", -1)) != int(calc["after"]["n_placeable"]):
            errs.append("L1 可落位块数: 页 %s ≠ 实算 %d"
                        % (after.get("n_placeable"), calc["after"]["n_placeable"]))
        ok, why = _bands_eq(after.get("full_height_bands"), calc["after"]["full_height_bands"])
        if not ok:
            errs.append("L1 两条整高自由带: %s" % why)
        ok, why = _sweep_eq(after.get("clearance_sweep"), calc["after"]["clearance_sweep"])
        if not ok:
            errs.append("L1 净距敏感度 sweep: %s" % why)
        if after.get("rel_bbox") is not None:
            pb = [float(v) for v in after["rel_bbox"]]
            cb = calc["after"]["rel_bbox"]
            if len(pb) != len(cb) or any(abs(a - b) > 5e-4 for a, b in zip(pb, cb)):
                errs.append("L1 铜箔相对原点包络: 页 %s ≠ 实算 %s" % (pb, cb))
    if before:
        if int(before.get("n_placeable", -1)) != int(calc["before"]["n_placeable"]):
            errs.append("L1 BEFORE 可落位块数: 页 %s ≠ 实算 %d"
                        % (before.get("n_placeable"), calc["before"]["n_placeable"]))
        ok, why = _bands_eq(before.get("full_height_bands"), calc["before"]["full_height_bands"])
        if not ok:
            errs.append("L1 BEFORE 两条整高自由带: %s" % why)
        ok, why = _sweep_eq(before.get("clearance_sweep"), calc["before"]["clearance_sweep"])
        if not ok:
            errs.append("L1 BEFORE 净距敏感度 sweep: %s" % why)
    res["L1"] = {"ok": not errs, "errs": errs}

    # ---- L2 sweep 非单调必须被显式承认 ----
    errs = []
    sw = calc["after"]["clearance_sweep"]
    by_clr = {round(s["clr"], 2): s["n_placeable"] for s in sw}
    actually_non_mono = by_clr.get(0.5, 0) < by_clr.get(0.2, 0)
    if not actually_non_mono:
        errs.append("L2 实算: sweep 在 clr=0.5 (%s) 与 clr=0.2 (%s) 之间【不】非单调"
                    % (by_clr.get(0.5), by_clr.get(0.2)))
    if after.get("monotonic") is not False:
        errs.append("L2 机器块 `led_space_after.monotonic` 不是 false (★实算非单调 ⇒ 必须写 false★)")
    body = text[:text.find(MACH_BEGIN)] if MACH_BEGIN in text else text
    if "不再单调" not in body:
        errs.append("L2 正文没有写「不再单调」⇒ 非单调没有被显式承认")
    if not (str(by_clr.get(0.5)) in body and str(by_clr.get(0.2)) in body):
        errs.append("L2 正文没有同时写出 clr=0.5 的 %s 与 clr=0.2 的 %s 两个数"
                    % (by_clr.get(0.5), by_clr.get(0.2)))
    res["L2"] = {"ok": not errs, "errs": errs}

    # ---- L3 两处定点改写不许与实算打架 ----
    errs = []
    try:
        _stext, smb = read_json_block(sync_path)
        s_led = smb.get("led") or {}
        ok, why = _bands_eq(s_led.get("full_height_bands"),
                            calc["after"]["full_height_bands"])
        if not ok:
            errs.append("L3 MECH_SYNC 机器块 `led.full_height_bands`: %s" % why)
        ok, why = _sweep_eq(s_led.get("clearance_sweep"), calc["after"]["clearance_sweep"])
        if not ok:
            errs.append("L3 MECH_SYNC 机器块 `led.clearance_sweep`: %s" % why)
        nb = s_led.get("nearest_band")
        cnb = calc["after"]["nearest_band"]
        if nb is None or cnb is None:
            errs.append("L3 MECH_SYNC 机器块 `led.nearest_band` 缺失")
        else:
            for k in ("x0", "x1", "y0", "y1"):
                if abs(float(nb.get(k, 1e9)) - float(cnb[k])) > 5e-4:
                    errs.append("L3 MECH_SYNC 机器块 `led.nearest_band.%s`: 页 %s ≠ 实算 %s"
                                % (k, nb.get(k), cnb[k]))
    except Exception as exc:                                  # noqa: BLE001
        errs.append("L3 MECH_SYNC 机器块读不到: %s" % exc)
    try:
        _ctext, cmb = read_yaml_block(calib_path)
        wins = {w.get("key"): w for w in (cmb.get("windows") or [])}
        w = wins.get("led_window_g_bench_hard")
        if not w:
            errs.append("L3 S6_CALIBER 机器块缺 `led_window_g_bench_hard` 窗口")
        else:
            band = calc["after"]["full_height_bands"][0] if calc["after"]["full_height_bands"] else None
            if band is None:
                errs.append("L3 实算没有整高自由带 ⇒ 无从对账")
            else:
                r = w.get("rect") or {}
                for k in ("x0", "x1", "y0", "y1"):
                    if abs(float(r.get(k, 1e9)) - float(band[k])) > 5e-4:
                        errs.append("L3 S6_CALIBER 机器块 `led_window_g_bench_hard.rect.%s`: "
                                    "%s ≠ 实算 %s" % (k, r.get(k), band[k]))
    except Exception as exc:                                  # noqa: BLE001
        errs.append("L3 S6_CALIBER 机器块读不到: %s" % exc)
    res["L3"] = {"ok": not errs, "errs": errs}

    # ---- L4 证据等级五级白名单 + §0~§5 逐节非空 ----
    errs = []
    # ★★【判据方向一字未改】★★: 禁用名单先报 (★写 `[官方]` = 红★) · 再判白名单
    for bad in FORBIDDEN_EVIDENCE:
        if bad in body:
            errs.append("L4 证据等级写了 %s ⇒ 只许用五级白名单" % bad)
    # ★★【只改「什么算证据等级」这一步】★★: ★**不再把几何区间 / 数组字面量 / 键名当等级** ★
    for tk in _evidence_tokens(body):
        if tk in FORBIDDEN_EVIDENCE:
            continue                      # 上面已按禁用名单单独报过
        if tk not in EVIDENCE_WHITELIST:
            errs.append("L4 证据等级 %s 不在五级白名单 %s" % (tk, "/".join(EVIDENCE_WHITELIST)))
    lines = body.split("\n")
    heads = [(i, l) for i, l in enumerate(lines) if l.startswith("## ")]
    for sec in REQUIRED_SECTIONS:
        idxs = [i for i, l in heads if sec in l]
        if not idxs:
            errs.append("L4 缺章节「%s」" % sec)
            continue
        start = idxs[0]
        nxt = [i for i, l in heads if i > start]
        end = nxt[0] if nxt else len(lines)
        seg = "\n".join(lines[start:end])
        if not any(tk in seg for tk in EVIDENCE_WHITELIST):
            errs.append("L4 章节「%s」一个证据等级都没标" % sec)
    res["L4"] = {"ok": not errs, "errs": errs}

    # ---- L5 正文零挂起措辞 ----
    errs = []
    for ph in FORBIDDEN_PENDING:
        if ph in body:
            errs.append("L5 正文里出现挂起措辞「%s」" % ph)
    res["L5"] = {"ok": not errs, "errs": errs}

    # ---- L6 沙盒在项目盘 tmp/ ----
    errs = []
    sb = mb.get("sandbox")
    if not sb:
        errs.append("L6 机器块缺 `sandbox` 字段")
    else:
        s = str(sb)
        if s.startswith("/tmp") or s.startswith("/var/tmp") or s.startswith("/private/tmp"):
            errs.append("L6 沙盒路径 %s 指到系统 /tmp ⇒ 必须落在项目盘 tmp/" % s)
        elif not s.startswith("tmp/"):
            errs.append("L6 沙盒路径 %s 不是项目盘相对路径 tmp/..." % s)
        else:
            abs_p = os.path.abspath(os.path.join(root, s))
            proj_tmp = os.path.abspath(os.path.join(root, "tmp"))
            if not (abs_p == proj_tmp or abs_p.startswith(proj_tmp + os.sep)):
                errs.append("L6 沙盒路径 %s 解析后不在项目盘 tmp/ 内 (%s)" % (s, abs_p))
    res["L6"] = {"ok": not errs, "errs": errs}
    return res, facts


# ==================================================================================================
# 打印
# ==================================================================================================
def _hr(t):
    print("\n" + "=" * 100)
    print(t)
    print("=" * 100)


def print_checks(res, facts):
    _hr("【check_onepass_s10_led_spec_sync】ISS-367 · S10 换封装后 LED 窗口规格同趟重算 · 机器闸")
    b, a = facts.get("before") or {}, facts.get("after") or {}
    print("★ 实算读数 (★脚本自己算, 不是页里写的★):")
    print("  · 换了 %s 件 (S10 MECH 侧子集) · 敏感度口径另算 %s 件"
          % (facts.get("swap_n"), facts.get("swap_all90_n")))
    print("  · BEFORE 铜箔相对原点包络 = %s · 可落位块数 = %s"
          % (b.get("rel_bbox"), b.get("n_placeable")))
    for bd in b.get("full_height_bands") or []:
        print("  · BEFORE 整高自由带 = X %.3f..%.3f (宽 %.3f) × Y %.3f..%.3f"
              % (bd["x0"], bd["x1"], bd["w"], bd["y0"], bd["y1"]))
    print("  · BEFORE sweep = %s" % [(s["clr"], s["n_placeable"]) for s in b.get("clearance_sweep") or []])
    print("  · AFTER  铜箔相对原点包络 = %s · 可落位块数 = %s"
          % (a.get("rel_bbox"), a.get("n_placeable")))
    for bd in a.get("full_height_bands") or []:
        print("  · AFTER  整高自由带 = X %.3f..%.3f (宽 %.3f) × Y %.3f..%.3f"
              % (bd["x0"], bd["x1"], bd["w"], bd["y0"], bd["y1"]))
    print("  · AFTER  sweep = %s" % [(s["clr"], s["n_placeable"]) for s in a.get("clearance_sweep") or []])
    print("  · AFTER  sweep 单调? = %s" % ("是" if a.get("monotonic") else "★否·非单调★"))
    for k in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        r = res.get(k)
        if not r:
            continue
        mark = "✅ 绿" if r["ok"] else "❌ 红"
        print("  %s %s %s" % (k, mark, "· %s" % k if r["ok"] else ""))
        for e in r["errs"][:40]:
            print("      · %s" % e)
        if len(r["errs"]) > 40:
            print("      · … 还有 %d 条" % (len(r["errs"]) - 40))
    ok_all = all(v["ok"] for v in res.values() if isinstance(v, dict) and "ok" in v)
    _hr("【结论】%s" % ("✅ 全绿" if ok_all else "❌ 有检查项判红"))
    print("口径提醒: 一切「实测」= 文件实读 + 脚本实跑; **实物 [实测] = 0 条**; 封装高度等外部数据标 [官网]。")


# ==================================================================================================
# selftest (★反向用例 · 每条自证「红的是目标那一条, 其余仍绿」★)
# ==================================================================================================
def _sandbox(root):
    sb = os.path.join(root, "tmp", "iss367_selftest")
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    os.makedirs(sb)
    shutil.copy2(os.path.join(root, SPEC_REL), os.path.join(sb, "spec.md"))
    shutil.copy2(os.path.join(root, SYNC_REL), os.path.join(sb, "sync.md"))
    shutil.copy2(os.path.join(root, CALIB_REL), os.path.join(sb, "calib.md"))
    return sb


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _mut(path, pristine, fn):
    new = fn(pristine)
    if new == pristine:
        raise AssertionError("反向用例没有改到任何东西")
    _write(path, new)


def _sub(text, old, new, count=1):
    if old not in text:
        raise AssertionError("反向用例找不到待改串 %r" % old)
    return text.replace(old, new, count)


def _clear_sec_evidence(text, sec="§2"):
    """★把某一节里的【全部五级白名单标记】清空 ⇒ 该节变成「一个证据等级都没标」⇒ L4 真红 ★"""
    lines = text.split("\n")
    si = next(i for i, l in enumerate(lines) if l.startswith("## ") and sec in l)
    ei = next((i for i, l in enumerate(lines) if i > si and l.startswith("## ")), len(lines))
    seg = "\n".join(lines[si:ei])
    new = seg
    for tk in EVIDENCE_WHITELIST:
        new = new.replace(tk, "")
    if new == seg:
        raise AssertionError("反向用例没有改到任何东西 (★%s 节里本来就没有白名单标记★)" % sec)
    return "\n".join(lines[:si] + [new] + lines[ei:])


def _mut_machine_block(text, fn):
    """★把改动限定在【机器块】里 (★页正文里也有同一串数字·不限定就会改错地方★) ★"""
    b = text.find(MACH_BEGIN)
    e = text.find(MACH_END)
    if b < 0 or e < 0:
        raise AssertionError("反向用例找不到机器块标记")
    seg = text[b:e]
    new = fn(seg)
    if new == seg:
        raise AssertionError("反向用例没有改到任何东西")
    return text[:b] + new + text[e:]


CASES = [
    ("① 把页里机器块的可落位块数改错 ⇒ L1 红", "L1", "spec",
     lambda t: _mut_machine_block(
         t, lambda s: _sub(s, '"n_placeable": 2183,', '"n_placeable": 2184,'))),
    ("② 把「不再单调」写回页里 ⇒ L2 红", "L2", "spec",
     lambda t: _sub(_sub(t, "不再单调", "仍然单调"), '"monotonic": false,', '"monotonic": true,')),
    ("③ 改 MECH_SYNC 机器块的整高自由带 ⇒ L3 红", "L3", "sync",
     lambda t: _sub(t, '{"x0": 2.225, "x1": 3.250, "y0": 1.500, "y1": 98.500}',
                     '{"x0": 2.225, "x1": 3.450, "y0": 1.500, "y1": 98.500}')),
    ("④ 把 §1 的证据等级清空 ⇒ L4 红", "L4", "spec",
     lambda t: _sub(t, "[实测]", "[未标注]")),
    ("⑤ 正文塞「等原厂回信」⇒ L5 红", "L5", "spec",
     lambda t: _sub(t, "## ★§4", "## ★§4\n\n★等原厂回信★")),
    ("⑥ 把沙盒路径指到 /tmp ⇒ L6 红", "L6", "spec",
     lambda t: _sub(t, '"sandbox": "tmp/iss367_sbx/"', '"sandbox": "/tmp/iss367_sbx/"')),
    ("⑦ 把 §2 全部证据等级清空 ⇒ L4 红 (章节没标)", "L4", "spec",
     lambda t: _clear_sec_evidence(t, "§2")),
]


def selftest(root):
    sb = _sandbox(root)
    ok_all = True
    print("【自检】反向用例 (★每条自证「红的是目标那一条, 其余仍绿」★)")
    res0, _f0 = run_checks(root)
    n_bad = [k for k, v in res0.items() if not v["ok"]]
    print("  ⓪ 正向对照 (一切如常) ⇒ %s" % ("✅ 全绿" if not n_bad else "❌ 红了: %s" % n_bad))
    if n_bad:
        ok_all = False
    pristine = {"spec": open(os.path.join(root, SPEC_REL), encoding="utf-8").read(),
                "sync": open(os.path.join(root, SYNC_REL), encoding="utf-8").read(),
                "calib": open(os.path.join(root, CALIB_REL), encoding="utf-8").read()}
    paths = {"spec": os.path.join(sb, "spec.md"),
             "sync": os.path.join(sb, "sync.md"),
             "calib": os.path.join(sb, "calib.md")}
    for name, target, which, fn in CASES:
        try:
            _mut(paths[which], pristine[which], fn)
        except AssertionError as exc:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, exc))
            ok_all = False
            continue
        r2, _f2 = run_checks(root,
                             os.path.join(sb, "spec.md"),
                             os.path.join(sb, "sync.md"),
                             os.path.join(sb, "calib.md"))
        red = sorted(k for k, v in r2.items() if not v["ok"])
        hit = target in red
        others = [k for k in red if k != target]
        good = hit and not others
        print("  %s %s ⇒ 红组 %s (目标 %s %s)"
              % ("✅" if good else "❌", name, red or "∅", target,
                 "命中" if hit else "★没命中★"))
        if not good:
            ok_all = False
            for k in red:
                for e in r2[k]["errs"][:3]:
                    print("        · %s: %s" % (k, e))
        # 复位
        _write(paths[which], pristine[which])
    shutil.rmtree(sb, ignore_errors=True)
    print("【自检结论】%s" % ("✅ %d 条反向用例全抓到 (且其余判据仍绿) ★ ALL TESTS PASS ★" % len(CASES)
                              if ok_all else "❌ 有用例没抓到 ★ TESTS FAILED ★"))
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--compute", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=PROJ)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--sync", default=None)
    ap.add_argument("--calib", default=None)
    args = ap.parse_args()
    if args.selftest:
        return selftest(args.root)
    if args.compute:
        print(json.dumps(compute(args.root), ensure_ascii=False, indent=1))
        return 0
    res, facts = run_checks(args.root, args.spec, args.sync, args.calib)
    if args.json:
        print(json.dumps({"results": res, "facts": facts}, ensure_ascii=False, indent=1))
    else:
        print_checks(res, facts)
    return 0 if all(v["ok"] for v in res.values() if isinstance(v, dict) and "ok" in v) else 1


if __name__ == "__main__":
    sys.exit(main())
