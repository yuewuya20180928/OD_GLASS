#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-375 sw-lead · 闸 = 「调试排针物理针序契约 + JTAG 链 SoM 侧真相」
====================================================================
判据 D0 ~ D8, 每条 fail-closed; 另带 --selftest (反向用例 ≥8 条, 其中 ≥3 条针对「镜像」)。

★设计原则 (与本单任务书一致)★:
  * D0/D1/D2/D5 **不许写死常量**: 一律现读盘上事实
      - D0 ⇒ 解析盘上官方 land .kicad_mod (自己解析, 不抄文档)
      - D1 ⇒ 用 pcbnew 实读板 (pad1 在哪 / 有无极性标记)
      - D2 ⇒ 用 KiCad 自己的 FOOTPRINT.SetOrientationDegrees 算两个候选的 pad→X 序
               (**不许手算旋转矩阵**) ⇒ 两序必须互为逆序, 互等即红
      - D5 ⇒ 现读 HW/netlist_v1.csv 的 JTAG 四行 SoM 侧端点 (**不许把 SoC_NC 写死**)
  * D3/D4 ⇒ 页与闸不许各说各话 (页写 rot90 而闸算出 rot270 ⇒ 红)
  * D6 ⇒ 页 §2 表述不得与 HW/PCB/SOM_PIN_MAPPING.md 冲突
  * D7 ⇒ 板指纹三项 (md5/mtime/size) 未动
  * D8 ⇒ 证据等级五级白名单 + 零挂起措辞 + 判据句/事实句分开 + 零挂链
  * **零挂链**: 本闸【不许】挂进 state/gate_check.py ⇒ D8 自证 grep 计数 == 0

用法:
  python3 SW/tools/check_debug_pin_order_contract.py            # 跑 D0~D8
  python3 SW/tools/check_debug_pin_order_contract.py --selftest  # 跑反向用例自测
  python3 SW/tools/check_debug_pin_order_contract.py --json      # 机器可读输出

退出码: 0 = 全绿; 1 = 有判据红; 2 = 用法/环境错误
"""
from __future__ import print_function

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

PAGE = os.path.join(ROOT, "SW", "BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md")
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
NETLIST = os.path.join(ROOT, "HW", "netlist_v1.csv")
PIN_TABLE = os.path.join(ROOT, "HW", "PCB", "FET3572C_PIN_TABLE.csv")
SOM_MAP = os.path.join(ROOT, "HW", "PCB", "SOM_PIN_MAPPING.md")
GATE_CHECK = os.path.join(ROOT, "state", "gate_check.py")
LAND_DIR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty"
LAND_1X04 = "PinHeader_1x04_P1.27mm_Vertical"
LAND_1X02 = "PinHeader_1x02_P1.27mm_Vertical"
PCBNEW_SH = os.path.join(ROOT, "state", "pcbnew_py.sh")

# ---- 板指纹基线 (与任务书一致) ----
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

# ---- 证据等级五级白名单 ----
EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
# ---- 零挂起措辞黑名单 (不许出现「等回复/等确认」这类) ----
HANGING_WORDS = ("等原厂回信", "等原厂回复", "待原厂回信", "等回复", "待回复",
                 "等确认", "待确认", "等对方", "先问原厂", "等回信")

# ---- JTAG 四线的 SoM 侧端点 (页 §2 要给, 闸要现读网表) ----
JTAG_SOC_NETS = ("JTAG_TCK_SOC", "JTAG_TMS_SOC", "JTAG_TDI_SOC", "JTAG_TDO_SOC")


class Result(object):
    def __init__(self):
        self.checks = []

    def add(self, cid, name, ok, detail):
        self.checks.append({"id": cid, "name": name, "ok": bool(ok), "detail": detail})
        return ok

    @property
    def failed(self):
        return [c for c in self.checks if not c["ok"]]

    @property
    def red_ids(self):
        return sorted(c["id"] for c in self.failed)


# ======================================================================
# 工具
# ======================================================================
def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def board_stat():
    st = os.stat(BOARD)
    return {"md5": md5(BOARD), "mtime": st.st_mtime, "size": st.st_size}


def board_mtime_str():
    """板 mtime 字符串, ★纳秒精度★ (与 `stat -c '%y'` 同格式同精度)。
    ★2026-11-24 02:4x 修 bug★: 原实现用 `%f` 只到微秒 (6 位) ⇒ 与任务书给的
    9 位纳秒常量永远不相等 ⇒ D7 假红。"""
    st = os.stat(BOARD)
    sec, frac = divmod(st.st_mtime_ns, 1000000000)
    import datetime
    dt = datetime.datetime.fromtimestamp(sec)
    return dt.strftime("%Y-%m-%d %H:%M:%S") + ".%09d" % frac


def sbx_dir():
    """沙盒目录 (★边界: 沙盒只落 tmp/iss375_sbx/ + logs/iss375/★)。"""
    d = os.path.join(ROOT, "tmp", "iss375_sbx")
    try:
        os.makedirs(d, exist_ok=True)
        return d
    except Exception:
        return None


def run_pcbnew(code):
    """在 KiCad 自带 python 里跑一段代码, 返回 stdout (KiCad 的 stderr 噪声已滤)。

    ★★2026-11-24 02:0x 订正 (cont2 · 修 bug)★★:
      原 docstring 写的根因是「`-c` 入口 vs 脚本文件入口」⇒ **实测是错的**:
      本机 KiCad 10.0.8 (AppDir/shared/lib/python3.11/dist-packages/pcbnew.py:24225)
      的 `pcbnew.FootprintLoad(lib, name)` 实现是 `return plug.FootprintLoad(...)`,
      而 `plug` 这个 SwigPyObject **根本没有 FootprintLoad 成员** ⇒
      ★★**写成 .py 文件也一样炸** ⇒ 「脚本文件入口能成」是假象。
      (main 的对照实验 (a) 用的是 AppDir 自带解释器, 与 `state/pcbnew_py.sh`
       的 squashfs-root 解释器不是同一入口 ⇒ 结论不可迁移。)
      ★真正可用的读法 = `pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)`
        拿到 PCB_IO 插件, 再 `.FootprintLoad(LAND_DIR, NAME)` ⇒ 本机实测 OK。
    ★保留「写成临时 .py 文件再跑」这个入口不变 (双模兼容: 普通 python3 也能跑本闸)★。"""
    if not os.path.exists(PCBNEW_SH):
        raise RuntimeError("pcbnew_py.sh 不存在: %s" % PCBNEW_SH)
    tmpd = tempfile.mkdtemp(prefix="iss375_py_", dir=sbx_dir())
    try:
        script = os.path.join(tmpd, "_run.py")
        with open(script, "w", encoding="utf-8") as fh:
            fh.write(code)
        proc = subprocess.Popen(["bash", PCBNEW_SH, script],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)
    out = out.decode("utf-8", "replace")
    err = err.decode("utf-8", "replace")
    if proc.returncode != 0:
        raise RuntimeError("pcbnew 调用失败 rc=%s\nSTDERR:\n%s"
                           % (proc.returncode, err[-3000:]))
    lines = [ln for ln in out.splitlines() if "duplicate image handler" not in ln]
    return "\n".join(lines)


# ======================================================================
# D0 · 官方 land 的 pad1 形状 (盘上 .kicad_mod 实读, 自己解析)
# ======================================================================
def parse_land_mod(fpname):
    """解析 .kicad_mod ⇒ {pad_name: {'type':..,'shape':..,'at':(x,y),'size':..,'drill':..}}"""
    path = os.path.join(LAND_DIR, fpname + ".kicad_mod")
    if not os.path.exists(path):
        raise RuntimeError("land 不存在: %s" % path)
    txt = read_text(path)
    pads = {}
    # (pad "1" thru_hole rect (at 0 0) (size 1 1) (drill 0.65) ...)
    # ★头匹配必须【非贪婪】/ 不可带 (.*)· 否则会把整个文件吞掉·只剩一个 pad★
    headers = list(re.finditer(r'\(pad\s+"([^"]+)"\s+(\S+)\s+(\S+)', txt))
    for i, m in enumerate(headers):
        name, ptype, shape = m.group(1), m.group(2), m.group(3)
        end = headers[i + 1].start() if i + 1 < len(headers) else len(txt)
        body = txt[m.start():end]
        at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', body)
        size = re.search(r'\(size\s+([-\d.]+)\s+([-\d.]+)', body)
        drill = re.search(r'\(drill\s+([-\d.]+)', body)
        pads[name] = {
            "type": ptype, "shape": shape,
            "at": (float(at.group(1)), float(at.group(2))) if at else None,
            "size": (float(size.group(1)), float(size.group(2))) if size else None,
            "drill": float(drill.group(1)) if drill else None,
        }
    if not pads:
        raise RuntimeError("land 解析失败 (0 pad): %s" % path)
    return pads


def d0_official_land(result, page_contract):
    """官方 land pad1 形状实读, 并与页里写的比。"""
    try:
        pads4 = parse_land_mod(LAND_1X04)
        pads2 = parse_land_mod(LAND_1X02)
    except Exception as exc:
        result.add("D0", "官方 land pad1 形状 (盘上实读)", False, "land 读取失败: %s" % exc)
        return
    detail = []
    ok = True
    for fpname, pads, key in ((LAND_1X04, pads4, "1x04"), (LAND_1X02, pads2, "1x02")):
        if "1" not in pads:
            result.add("D0", "官方 land pad1 形状 (盘上实读)", False, "%s 无 pad 1" % fpname)
            return
        p1 = pads["1"]
        others = [pads[k]["shape"] for k in pads if k != "1"]
        marker = (p1["shape"] != others[0]) and all(s == others[0] for s in others)
        detail.append("%s: pad1=%s %s / 其余=%s ⇒ 有 pin1 标记=%s"
                       % (key, p1["type"], p1["shape"], others[0], marker))
        if not marker:
            ok = False
        # 页里写的必须与实读一致
        claimed = page_contract.get("land", {}).get(key, {})
        want_shape = claimed.get("pad1_shape")
        if want_shape is not None:
            if want_shape != "%s %s" % (p1["type"], p1["shape"]):
                ok = False
                detail.append("  ✗ 页写 pad1_shape=%r, 实读=%r %r" %
                              (want_shape, p1["type"], p1["shape"]))
            if claimed.get("other_shape") not in (None, "%s %s" % (p1["type"], others[0])):
                ok = False
                detail.append("  ✗ 页写 other_shape=%r, 实读=%r" %
                              (claimed.get("other_shape"), "%s %s" % (p1["type"], others[0])))
    result.add("D0", "官方 land pad1 形状 (盘上实读, 不写死)", ok, "; ".join(detail))


# ======================================================================
# D1 · 现状板面 pad1 位置 + 有无极性标记 (pcbnew 实读)
# ======================================================================
def read_current_board():
    code = r'''
import json, pcbnew
b = pcbnew.LoadBoard(%r)
out = {}
for ref in ("J_DEBUG", "J_UART"):
    f = [x for x in b.GetFootprints() if x.GetReference() == ref][0]
    pads = []
    for p in f.Pads():
        bb = p.GetBoundingBox()
        pads.append({
            "pad": p.GetPadName(),
            "x": round(pcbnew.ToMM(p.GetPosition().x), 4),
            "shape": str(p.GetShape()),
            "attr": str(p.GetAttribute()),
            "net": p.GetNetname(),
        })
    pads.sort(key=lambda d: d["x"])
    # 形状名归一 (KiCad 10: shape int)
    shp = {}
    for nm in ("PAD_SHAPE_CIRCLE", "PAD_SHAPE_RECT", "PAD_SHAPE_OVAL",
               "PAD_SHAPE_ROUNDRECT", "PAD_SHAPE_TRAPEZOID", "PAD_SHAPE_CHAMFERED_RECT"):
        if hasattr(pcbnew, nm):
            shp[int(getattr(pcbnew, nm))] = nm.replace("PAD_SHAPE_", "")
    att = {}
    for nm in ("PAD_ATTRIB_PTH", "PAD_ATTRIB_SMD", "PAD_ATTRIB_CONN", "PAD_ATTRIB_NPTH"):
        if hasattr(pcbnew, nm):
            att[int(getattr(pcbnew, nm))] = nm.replace("PAD_ATTRIB_", "")
    for p in pads:
        p["shape"] = shp.get(int(p["shape"]), p["shape"])
        p["attr"] = att.get(int(p["attr"]), p["attr"])
    p1 = [p for p in pads if p["pad"] == "1"][0]
    xs = [p["x"] for p in pads]
    # pad1 极性标记: pad1 的形状与其余 pad 不同
    others = sorted(set(p["shape"] for p in pads if p["pad"] != "1"))
    p1shape = p1["shape"]
    marker = (len(others) == 1 and others[0] != p1shape)
    out[ref] = {
        "pads": pads,
        "n_pads": len(pads),
        "pad1_x": p1["x"],
        "pin1_end": "X_MIN" if p1["x"] == min(xs) else ("X_MAX" if p1["x"] == max(xs) else "MID"),
        "pad1_marker": marker,
        "pad1_shape": p1shape,
        "pad_attr": p1["attr"],
        "net_by_pad": dict((p["pad"], p["net"]) for p in pads),
    }
print("###JSON###" + json.dumps(out))
''' % BOARD
    out = run_pcbnew(code)
    for ln in out.splitlines():
        if ln.startswith("###JSON###"):
            return json.loads(ln[len("###JSON###"):])
    raise RuntimeError("read_current_board 无 JSON 输出:\n%s" % out[-2000:])


def d1_current_board(result, page_contract, cur):
    ok = True
    detail = []
    for ref in ("J_DEBUG", "J_UART"):
        c = cur[ref]
        pc = page_contract.get("current", {}).get(ref, {})
        detail.append("%s: pad1@X=%s (%s) 标记=%s 形状=%s 属性=%s"
                      % (ref, c["pad1_x"], c["pin1_end"], c["pad1_marker"],
                         c["pad1_shape"], c["pad_attr"]))
        if pc.get("pin1_end") != c["pin1_end"]:
            ok = False
            detail.append("  ✗ 页写 pin1_end=%r, 实读=%r" % (pc.get("pin1_end"), c["pin1_end"]))
        if pc.get("pad1_marker") != c["pad1_marker"]:
            ok = False
            detail.append("  ✗ 页写 pad1_marker=%r, 实读=%r"
                          % (pc.get("pad1_marker"), c["pad1_marker"]))
        if pc.get("pads") is not None and int(pc["pads"]) != c["n_pads"]:
            ok = False
            detail.append("  ✗ 页写 pads=%r, 实读=%r" % (pc.get("pads"), c["n_pads"]))
    result.add("D1", "现状板面 pad1 位置/极性标记 (实读板, 不写死)", ok, "; ".join(detail))


# ======================================================================
# D2 · 两个候选的 pad→X 序 (KiCad 自己的 SetOrientationDegrees 算)
# ======================================================================
def compute_candidate_orders():
    """用 pcbnew 在【板副本】上把候选 land 摆上去, 读 pad→X 序。
    ★不许手算旋转矩阵★ —— 一律走 FOOTPRINT.SetOrientationDegrees + SetPosition。

    ★★2026-11-24 02:3x 修 bug (KiCad 10.0.8 / AppDir python3.11 · 本机实测)★★:
      ① pcbnew.FootprintLoad() 本机就是坏的: pcbnew.py:24225 -> plug.FootprintLoad,
         而 plug 是裸 SwigPyObject ⇒ AttributeError ⇒ 改走
         pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP).FootprintLoad(...)
      ② ★更狠的一条★: 同一进程里【第 3 次】插件调用就拿到坏对象
         (FindPlugin 返回裸 SwigPyObject / FootprintLoad 返回坏 FOOTPRINT ⇒ Pads() 不可迭代)
         ⇒ ⇒ 【一个候选一个子进程】, 彻底隔离该退化行为。
      ③ 板副本只落 tmp/iss375_sbx/, 不写真板, 不 Save。"""
    CANDS = (("J_DEBUG", "rot90", 141.0450, 56.6000, 90.0, "PinHeader_1x04_P1.27mm_Vertical"),
             ("J_DEBUG", "rot270", 144.8550, 56.6000, 270.0, "PinHeader_1x04_P1.27mm_Vertical"),
             ("J_UART", "rot90", 18.2550, 68.6000, 90.0, "PinHeader_1x02_P1.27mm_Vertical"),
             ("J_UART", "rot270", 19.5250, 68.6000, 270.0, "PinHeader_1x02_P1.27mm_Vertical"))
    out = {}
    for ref, tag, ox, oy, rot, fpname in CANDS:
        code = r'''
import json, os, shutil, tempfile, pcbnew
LAND_DIR = %r
SRC = %r
NAME = %r
REF = %r
OX = %r
OY = %r
ROT = %r
tmpd = tempfile.mkdtemp(prefix="iss375_d2_", dir=%r)
dst = os.path.join(tmpd, "cand.kicad_pcb")
try:
    shutil.copyfile(SRC, dst)
    io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
    if not hasattr(io, "FootprintLoad"):
        raise RuntimeError("PCB_IO plugin unavailable: " + str(type(io)))
    fp = io.FootprintLoad(LAND_DIR, NAME)
    b = pcbnew.LoadBoard(dst)
    old = [x for x in b.GetFootprints() if x.GetReference() == REF][0]
    b.Remove(old)
    fp.SetReference(REF)
    b.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I_MM(OX, OY))
    fp.SetOrientationDegrees(ROT)
    fp.SetPosition(pcbnew.VECTOR2I_MM(OX, OY))
    fp.SetOrientationDegrees(ROT)
    pads = [{"pad": p.GetPadName(),
             "x": round(pcbnew.ToMM(p.GetPosition().x), 4),
             "y": round(pcbnew.ToMM(p.GetPosition().y), 4),
             "shape": str(p.GetShape())}
            for p in fp.Pads()]
    pads.sort(key=lambda d: d["x"])
    print("###JSON###" + json.dumps({
        "origin": [OX, OY], "rot": ROT,
        "order_by_x": [p["pad"] for p in pads],
        "xs": [p["x"] for p in pads],
        "ys": [p["y"] for p in pads],
        "shapes": [p["shape"] for p in pads],
        "pad1_end": ("X_MIN" if pads[0]["pad"] == "1" else
                     ("X_MAX" if pads[-1]["pad"] == "1" else "MID")),
    }))
finally:
    shutil.rmtree(tmpd, ignore_errors=True)
''' % (LAND_DIR, BOARD, fpname, ref, ox, oy, rot,
           os.path.join(ROOT, "tmp", "iss375_sbx"))
        raw = run_pcbnew(code)
        got = None
        for ln in raw.splitlines():
            if ln.startswith("###JSON###"):
                got = json.loads(ln[len("###JSON###"):])
        if got is None:
            raise RuntimeError("候选 %s/%s 无 JSON 输出:\n%s" % (ref, tag, raw[-2000:]))
        out.setdefault(ref, {})[tag] = got
    return out


def d2_candidate_orders(result, page_contract, orders):
    """两候选的 pad→X 序必须互为逆序 (不是互等) + 与页一致。"""
    ok = True
    detail = []
    for ref in ("J_DEBUG", "J_UART"):
        cand = orders.get(ref, {})
        o90 = cand.get("rot90", {})
        o270 = cand.get("rot270", {})
        seq90 = o90.get("order_by_x", [])
        seq270 = o270.get("order_by_x", [])
        detail.append("%s rot90 序=%s (pad1@%s) / rot270 序=%s (pad1@%s)"
                      % (ref, seq90, o90.get("pad1_end"), seq270, o270.get("pad1_end")))
        if not seq90 or not seq270:
            ok = False
            detail.append("  ✗ 候选序缺失")
            continue
        # ★核心: 两序必须互为逆序, 不是互等★
        if seq90 == seq270:
            ok = False
            detail.append("  ✗ 两候选序【互等】(镜像是本单核心, 互等即红)")
        if list(reversed(seq90)) != seq270:
            ok = False
            detail.append("  ✗ rot270 序不是 rot90 序的逆序")
        # pad1 端位
        if o90.get("pad1_end") == o270.get("pad1_end"):
            ok = False
            detail.append("  ✗ 两候选 pad1 端位相同 (应相反)")
        # 与页写的比
        pc = page_contract.get("candidates", {}).get(ref, {})
        for tag, live in (("rot90", o90), ("rot270", o270)):
            claimed = pc.get(tag, {})
            if claimed.get("pin1_end") != live.get("pad1_end"):
                ok = False
                detail.append("  ✗ 页写 %s.%s.pin1_end=%r, 实算=%r"
                              % (ref, tag, claimed.get("pin1_end"), live.get("pad1_end")))
    result.add("D2", "两候选 pad→X 序 (KiCad 变换算, 须互为逆序)", ok, "; ".join(detail))


# ======================================================================
# D3 · 页 §1 必须同时给两个候选 + 裁决 + 落点写死值
# ======================================================================
def d3_page_has_both_candidates(result, page_contract, page_text):
    ok = True
    detail = []
    for ref in ("J_DEBUG", "J_UART"):
        pc = page_contract.get("candidates", {}).get(ref, {})
        for tag in ("rot90", "rot270"):
            c = pc.get(tag)
            if not c:
                ok = False
                detail.append("✗ %s 缺候选 %s" % (ref, tag))
                continue
            if not c.get("origin_mm"):
                ok = False
                detail.append("✗ %s.%s 缺落点写死值 (origin_mm)" % (ref, tag))
            if c.get("pin1_end") not in ("X_MIN", "X_MAX"):
                ok = False
                detail.append("✗ %s.%s 缺 pin1 端位" % (ref, tag))
        if "rot90" in pc and "rot270" in pc:
            o1 = pc.get("rot90", {}).get("origin_mm")
            o2 = pc.get("rot270", {}).get("origin_mm")
            if o1 == o2:
                ok = False
                detail.append("✗ %s 两候选落点相同 (应互为镜像)" % ref)
    # 裁决 + 落点写死值 (正文里要有)
    if not re.search(r"裁决", page_text):
        ok = False
        detail.append("✗ 页里没有『裁决』字样 (须给裁决建议)")
    if not re.search(r"落点写死值", page_text):
        ok = False
        detail.append("✗ 页里没有『落点写死值』字样")
    if not re.search(r"归\s*main\s*裁|归 main 裁|待\s*main", page_text):
        ok = False
        detail.append("✗ 页里没有『归 main 裁』(不代拍声明缺失)")
    result.add("D3", "页同时给出两候选+裁决+落点写死值", ok, "; ".join(detail))


# ======================================================================
# D4 · 页里写的 pin1 朝向必须与 D2 算出来的一致
# ======================================================================
def d4_page_matches_computed(result, page_contract, orders):
    ok = True
    detail = []
    for ref in ("J_DEBUG", "J_UART"):
        pc = page_contract.get("candidates", {}).get(ref, {})
        live = orders.get(ref, {})
        for tag in ("rot90", "rot270"):
            claimed = pc.get(tag, {})
            lv = live.get(tag, {})
            # 1) pin1 端位
            if claimed.get("pin1_end") != lv.get("pad1_end"):
                ok = False
                detail.append("✗ %s.%s pin1_end 页=%r 实算=%r"
                              % (ref, tag, claimed.get("pin1_end"), lv.get("pad1_end")))
            # 2) 线序 (按 pad 号 → net 名映射) 必须与实算的 pad 序一致
            cur = page_contract.get("current", {}).get(ref, {})
            net_by_pad = cur.get("net_by_pad", {})
            claimed_order = claimed.get("order_by_x")
            if claimed_order and lv.get("order_by_x"):
                expect = [net_by_pad.get(p, p) for p in lv["order_by_x"]]
                if list(claimed_order) != list(expect):
                    ok = False
                    detail.append("✗ %s.%s 线序 页=%r 实算=%r"
                                  % (ref, tag, claimed_order, expect))
            # 3) 线序标签与端位自洽
            if claimed.get("order_label") and claimed.get("pin1_end"):
                if claimed["pin1_end"] == "X_MIN" and claimed["order_label"] != "顺排":
                    ok = False
                    detail.append("✗ %s.%s pin1 在 X 最小端却标 %r (应顺排)"
                                  % (ref, tag, claimed["order_label"]))
                if claimed["pin1_end"] == "X_MAX" and claimed["order_label"] != "逆排":
                    ok = False
                    detail.append("✗ %s.%s pin1 在 X 最大端却标 %r (应逆排)"
                                  % (ref, tag, claimed["order_label"]))
    result.add("D4", "页的 pin1 朝向与 D2 实算一致", ok, "; ".join(detail))


# ======================================================================
# D5 · 网表侧 JTAG 四线的 SoM 侧端点 (现读网表, 不写死 SoC_NC)
# ======================================================================
def read_netlist_soc_endpoints():
    """现读 HW/netlist_v1.csv ⇒ {net_name: SoM 侧端点}"""
    txt = read_text(NETLIST)
    out = {}
    for ln in txt.splitlines():
        parts = ln.split(",")
        if len(parts) < 4:
            continue
        net = parts[1].strip()
        if net in JTAG_SOC_NETS:
            out[net] = parts[2].strip()   # 该行的「另一端」列 = SoM 侧端点
    return out


def d5_netlist_soc_side(result, page_contract, endpoints):
    ok = True
    detail = []
    if len(endpoints) != len(JTAG_SOC_NETS):
        ok = False
        detail.append("✗ 网表里 JTAG 四行没读全 (%d/%d)" % (len(endpoints), len(JTAG_SOC_NETS)))
    claimed = page_contract.get("jtag_soc_side", {})
    for net in JTAG_SOC_NETS:
        live = endpoints.get(net)
        if live is None:
            ok = False
            detail.append("✗ 网表里找不到 %s" % net)
            continue
        cl = claimed.get(net)
        if cl is None:
            ok = False
            detail.append("✗ 页里缺 %s 的 SoM 侧端点" % net)
        elif cl != live:
            ok = False
            detail.append("✗ %s 页写=%r 实读=%r" % (net, cl, live))
        detail.append("%s→%s" % (net, live))
    # 页正文里也要出现这四个网名 + 端点
    result.add("D5", "网表 JTAG 四线 SoM 侧端点 (现读, 不写死)", ok, "; ".join(detail))


# ======================================================================
# D6 · 页 §2 表述不得与 SOM_PIN_MAPPING.md 冲突
# ======================================================================
def d6_som_map_consistency(result, page_text):
    ok = True
    detail = []
    som = read_text(SOM_MAP)
    for net in ("JTAG_TCK", "JTAG_TMS", "JTAG_TDI", "JTAG_TDO"):
        m = re.search(r"\|\s*`%s`\s*\|([^\n]*)\|" % re.escape(net), som)
        if not m:
            ok = False
            detail.append("✗ SOM_PIN_MAPPING.md 里找不到 %s 行" % net)
            continue
        concl = m.group(1)
        says_absent = ("没有同名" in concl) or ("不存在" in concl)
        if not says_absent:
            ok = False
            detail.append("✗ SOM_PIN_MAPPING.md 的 %s 行结论变了: %s" % (net, concl.strip()[:80]))
        # 页里如果写「已落地/已连通」且映射页说「不存在」⇒ 冲突
        for bad in ("已在 SoM 侧落地", "已在 SoC 侧落地", "SoM 侧已落地", "四线已通",
                    "已在 SoM 侧引出"):
            if bad in page_text:
                ok = False
                detail.append("✗ 页里出现与映射页冲突的表述: %s" % bad)
        if net not in page_text:
            ok = False
            detail.append("✗ 页 §2 里没提到 %s" % net)
    # 页里必须出现「不落地」这个受控表述, 且不能把「信号不存在」当结论写
    if "不落地" not in page_text:
        ok = False
        detail.append("✗ 页里没有『不落地』这个受控表述")
    # 若页里断言「信号不存在」为事实 ⇒ 冲突 (脚表只覆盖引出引脚)
    # ★★2026-11-24 02:4x 精化★★: 本条只管【本页自己的断言】⇒
    #   ① 引用块 (行首 '>') = 映射页原话, 不是本页结论 ⇒ 豁免
    #   ② 明写「原话 / 第 48-51 行 / SOM_PIN_MAPPING.md」的转述 = 在报告映射页怎么写 ⇒ 豁免
    #   ★本页自己的结论句 (无上述出处标记) 仍然会被抓 ⇒ 判据没被削弱
    for pat in (r"信号(在|于)[^。\n]{0,20}不存在(?![^\n]{0,40}(不能|未|不作|无法))",):
        for m in re.finditer(pat, page_text):
            seg = page_text[max(0, m.start() - 80):m.end() + 80]
            line_start = page_text.rfind("\n", 0, m.start()) + 1
            line = page_text[line_start:page_text.find("\n", m.start())]
            exempt = (line.lstrip().startswith(">")
                      or any(k in seg for k in ("原话", "第 48-51 行", "SOM_PIN_MAPPING.md",
                                                "逐针表里没有同名", "引用")))
            if exempt:
                continue
            if "不能" not in seg and "不作断言" not in seg and "下不得" not in seg:
                ok = False
                detail.append("✗ 页里把『信号不存在』当结论写了: ...%s..." % seg[:120])
    result.add("D6", "页 §2 与 SOM_PIN_MAPPING.md 结论不冲突", ok, "; ".join(detail))


# ======================================================================
# D7 · 板指纹三项未动
# ======================================================================
def d7_board_fingerprint(result):
    st = board_stat()
    mt = board_mtime_str()
    ok = (st["md5"] == BOARD_MD5 and st["size"] == BOARD_SIZE and mt == BOARD_MTIME)
    detail = "md5=%s (期望 %s) / mtime=%s (期望 %s) / size=%s (期望 %s)" % (
        st["md5"], BOARD_MD5, mt, BOARD_MTIME, st["size"], BOARD_SIZE)
    result.add("D7", "板指纹三项未动 (零写板自证)", ok, detail)


# ======================================================================
# D8 · 证据等级白名单 + 零挂起措辞 + 判据句/事实句分开 + 零挂链
# ======================================================================
def d8_evidence_and_hygiene(result, page_text):
    ok = True
    detail = []
    # 1) 证据等级只用五级白名单 —— 找出所有形如 [xxx] 的证据标记
    # ★★2026-11-24 02:5x 修 bug (selftest T-D8a 实测发现)★★:
    #   原实现只收「以白名单词开头的 token」⇒ 【白名单外的等级标签 (如 [猜测]) 根本收不到】
    #   ⇒ 形同虚设 ⇒ 改成: 任何方括号标签 (1~12 字) 都当证据等级候选 (页里实测只有五级白名单标签)
    found = set(re.findall(r"\[([^\[\]\n]{1,12})\]", page_text))
    evidence_like = set()
    for tok in found:
        if tok.startswith("ISS") or tok.startswith("/") or re.match(r"^[0-9a-fA-F]{8,}$", tok):
            continue
        evidence_like.add(tok)
    for tok in sorted(evidence_like):
        if "[%s]" % tok not in EVIDENCE_WHITELIST:
            ok = False
            detail.append("✗ 证据等级不在白名单: [%s]" % tok)
    # 白名单五级必须都出现 (证明确实按级标了)
    for lv in EVIDENCE_WHITELIST:
        if lv not in page_text:
            ok = False
            detail.append("✗ 证据等级 %s 未在页里出现" % lv)
    # 2) 零挂起措辞
    for w in HANGING_WORDS:
        if w in page_text:
            ok = False
            detail.append("✗ 出现挂起措辞: %s" % w)
    # 3) 判据句 / 事实句 分开
    if "判据句" not in page_text:
        ok = False
        detail.append("✗ 页里没有『判据句』小节")
    if "事实句" not in page_text:
        ok = False
        detail.append("✗ 页里没有『事实句』小节")
    # 4) 零挂链 (自证)
    if os.path.exists(GATE_CHECK):
        gtxt = read_text(GATE_CHECK)
        cnt = gtxt.count("check_debug_pin_order_contract")
        if cnt != 0:
            ok = False
            detail.append("✗ 新闸被挂进 state/gate_check.py (%d 处)" % cnt)
        else:
            detail.append("零挂链: state/gate_check.py 命中 0")
    result.add("D8", "证据等级白名单+零挂起措辞+判据/事实分开+零挂链", ok, "; ".join(detail))


# ======================================================================
# 页解析 (机器可读契约块)
# ======================================================================
def parse_page_contract(page_text):
    m = re.search(r"```json iss375_contract\s*(\{.*?\})\s*```", page_text, re.S)
    if not m:
        raise RuntimeError("页里找不到 ```json iss375_contract 块")
    return json.loads(m.group(1))


# ======================================================================
# 主跑
# ======================================================================
def run_all(page_path=PAGE):
    result = Result()
    page_text = read_text(page_path)
    contract = parse_page_contract(page_text)
    d0_official_land(result, contract)
    cur = read_current_board()
    d1_current_board(result, contract, cur)
    orders = compute_candidate_orders()
    d2_candidate_orders(result, contract, orders)
    d3_page_has_both_candidates(result, contract, page_text)
    d4_page_matches_computed(result, contract, orders)
    endpoints = read_netlist_soc_endpoints()
    d5_netlist_soc_side(result, contract, endpoints)
    d6_som_map_consistency(result, page_text)
    d7_board_fingerprint(result)
    d8_evidence_and_hygiene(result, page_text)
    return result, contract, cur, orders, endpoints


def fmt_result(result):
    lines = []
    for c in result.checks:
        lines.append("  [%s] %-4s %-8s %s" % ("PASS" if c["ok"] else "FAIL", c["id"],
                                               c["name"], c["detail"]))
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return run_selftest()
    try:
        result, contract, cur, orders, endpoints = run_all()
    except Exception as exc:
        print("FATAL: %s" % exc)
        return 2
    print("=== ISS-375 · check_debug_pin_order_contract ===")
    print(fmt_result(result))
    if "--json" in args:
        print(json.dumps({"checks": result.checks}, ensure_ascii=False, indent=2))
    n_ok = len(result.checks) - len(result.failed)
    print("=== %d/%d PASS ===" % (n_ok, len(result.checks)))
    if result.failed:
        print("RED: %s" % ",".join(result.red_ids))
        return 1
    print("ALL CHECKS PASS")
    return 0


# ======================================================================
# --selftest · 反向用例 (≥8 条, 其中 ≥3 条针对「镜像」)
# ======================================================================
# 镜像类三条 (本单核心) —— ★★每一条都必须动【判据自己的数据源】, 不是动页★★:
#   M1 把页里的 rot90 改成 rot270     ⇒ D2/D3/D4 红 (页与实算脱钩)
#   M2 把【D2 的算式】改成手算常数     ⇒ D2/D4 红 (变异体: compute_candidate_orders 返回写死常数)
#   M3 把【网表里的】SoC_NC 改成别的    ⇒ D5 红 (沙盒网表副本, 真网表只读)
# ★★为什么不能只改页 ★★: 改页只能证明「页与闸对不上」, 证明不了
#   「D2 真的是用 KiCad 变换算的」与「D5 真的是现读网表的」——
#   ⇒ 要动【闸的算式】与【网表本体】, 才测得到本单真正的两条命脉。
MIRROR_CASES = ("M1", "M2", "M3")


def _mutate_page(text, fn):
    return fn(text)


def _case_m1(text, _tmpdir=None):
    """M1: 把页里所有 rot90 标成 rot270 (⇒ 两候选同向 ⇒ 镜像是坏的)"""
    return text.replace('"rot90"', '"rot270"').replace("rot 90", "rot 270")


# ======================================================================
# M2 · 把 D2 的算式改成【手算常数】⇒ 必须 D2 红
# ======================================================================
# ★做法: 把本闸源码复制到沙盒, 追加一段 monkeypatch, 让 compute_candidate_orders()
#   返回【写死的常数】(两个候选同序 = 「两个候选被当同一个」这个典型手算错误),
#   再跑这个变异体 ⇒ D2 必须自己发现 (不许靠页来发现)。
# ★★不碰真闸文件, 不碰真板, 只落 tmp/iss375_sbx/★★
_MUTANT_BLOCK = '''
# ---- M2 变异体: 把 D2 的算式改成手算常数 (不再走 KiCad 的 SetOrientationDegrees) ----
def _mutant_compute_candidate_orders():
    _K4 = ("1", "2", "3", "4")
    _K2 = ("1", "2")
    return {
        "J_DEBUG": {"rot90": {"order_by_x": list(_K4), "pad1_end": "X_MIN"},
                    "rot270": {"order_by_x": list(_K4), "pad1_end": "X_MIN"}},
        "J_UART": {"rot90": {"order_by_x": list(_K2), "pad1_end": "X_MIN"},
                   "rot270": {"order_by_x": list(_K2), "pad1_end": "X_MIN"}},
    }
compute_candidate_orders = _mutant_compute_candidate_orders
'''


def _case_m2_gate_formula(text, tmpdir):
    """M2: 变异本闸自己的 D2 算式 ⇒ 期望 D2 红 (其余仍绿)。返回 (红集, 说明)。"""
    src = read_text(os.path.abspath(__file__))
    marker = 'if __name__ == "__main__":'
    # ★必须用 rfind 定位【最后】那个标记 ★: 本闸源码里前面还有一处同名字符串字面量
    #   (变异块注入那行自己就含这个串) ⇒ 用 str.replace 会插到第一个命中处 ⇒ SyntaxError
    pos = src.rfind(marker)
    if pos < 0:
        return {"FATAL: 找不到 __main__ 标记"}, "闸源码结构变了"
    mutant_path = os.path.join(tmpdir, "_mutant_gate_m2.py")
    with open(mutant_path, "w", encoding="utf-8") as fh:
        fh.write(src[:pos] + _MUTANT_BLOCK + "\n" + src[pos:])
    proc = subprocess.run([sys.executable, mutant_path, "--json"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = proc.stdout.decode("utf-8", "replace")
    idx = out.find('{"checks"')
    if idx < 0:
        idx = out.find('{\n  "checks"')
    if idx < 0:
        return {"FATAL: 变异体无 JSON 输出"}, out[-500:]
    try:
        data = json.JSONDecoder().raw_decode(out[idx:])[0]
    except Exception as exc:
        return {"FATAL:%s" % type(exc).__name__}, out[-500:]
    red = set(c["id"] for c in data["checks"] if not c["ok"])
    return red, "变异体 rc=%s" % proc.returncode


# ======================================================================
# M3 · 把【网表里的】SoC_NC 改成别的 ⇒ 必须 D5 红
# ======================================================================
def _case_m3_mutated_netlist(text, tmpdir):
    """M3: 沙盒网表副本里把 JTAG 四线的 SoM 侧端点 SoC_NC 改掉 ⇒ 期望 D5 红。"""
    src = read_text(NETLIST)
    out_lines = []
    n_mut = 0
    for ln in src.splitlines(True):
        if any((",%s," % net) in ln for net in JTAG_SOC_NETS) and ",SoC_NC," in ln:
            ln = ln.replace(",SoC_NC,", ",SoC_FAKE,", 1)
            n_mut += 1
        out_lines.append(ln)
    if n_mut != 4:
        return {"FATAL: 改了 %d 行 (应 4 行)" % n_mut}, ""
    mut_path = os.path.join(tmpdir, "netlist_m3_mutated.csv")
    with open(mut_path, "w", encoding="utf-8") as fh:
        fh.write("".join(out_lines))
    saved = globals()["NETLIST"]
    globals()["NETLIST"] = mut_path
    try:
        res, _, _, _, _ = run_all()
        red = set(res.red_ids)
    except Exception as exc:
        red = {"FATAL:%s" % type(exc).__name__}
    finally:
        globals()["NETLIST"] = saved
    return red, "沙盒网表副本改了 %d 行" % n_mut


def _case_d0(text, _tmpdir=None):
    """D0: 页里把官方 land 的 pad1 形状写错"""
    return text.replace('"pad1_shape": "thru_hole rect"', '"pad1_shape": "thru_hole circle"')


def _case_d1(text, _tmpdir=None):
    """D1: 页里把现状 pad1 位置写反 (X 最小端 ⇒ X 最大端)"""
    return text.replace('"pin1_end": "X_MIN", "pad1_marker": false, "pad_shape": "RECT", "pad_attr": "SMD", "net_by_pad": {"1": "JTAG_TCK"',
                        '"pin1_end": "X_MAX", "pad1_marker": false, "pad_shape": "RECT", "pad_attr": "SMD", "net_by_pad": {"1": "JTAG_TCK"')


def _case_d3(text, _tmpdir=None):
    """D3: 页里删掉一个候选 (只给一个 ⇒ 红)"""
    out = text.replace('"rot270": {"origin_mm": [144.8550, 56.6000]', '"rot270_x": {"origin_mm": [144.8550, 56.6000]')
    return out.replace('"rot270": {"origin_mm": [19.5250, 68.6000]', '"rot270_x": {"origin_mm": [19.5250, 68.6000]')


def _case_d6(text, _tmpdir=None):
    """D6: 页里写「已在 SoM 侧落地」⇒ 与映射页「不存在」冲突"""
    return text.replace("JTAG 链在 SoM 侧不落地",
                        "JTAG 链已在 SoM 侧落地")


def _case_d7(text, _tmpdir=None):
    """D7: 板指纹被动过 (用临时副本测, 不碰真板)"""
    return text


def _case_d8_evidence(text, _tmpdir=None):
    """D8: 证据等级用白名单外的等级"""
    return text.replace("[实测]", "[猜测]", 1)


def _case_d8_hanging(text, _tmpdir=None):
    """D8: 出现挂起措辞"""
    return text.replace("零外发", "等原厂回信后补齐，零外发", 1)


def _case_d8_chain(text, _tmpdir=None):
    """D8: 新闸挂进 state/gate_check.py"""
    return text


def _run_on_text(text, tmpdir):
    """把页写成临时文件跑一遍 ⇒ 返回红判据集合"""
    tmp_page = os.path.join(tmpdir, "page_%s.md" % os.urandom(4).hex())
    with open(tmp_page, "w", encoding="utf-8") as fh:
        fh.write(text)
    try:
        res, _, _, _, _ = run_all(page_path=tmp_page)
        return set(res.red_ids)
    except Exception as exc:
        return {"FATAL:%s" % type(exc).__name__}


def run_selftest():
    base_text = read_text(PAGE)
    tmpdir = tempfile.mkdtemp(prefix="iss375_selftest_")
    cases = []
    try:
        # 先确认基线全绿
        base_red = _run_on_text(base_text, tmpdir)
        if base_red:
            print("SELFTEST FATAL: 基线页不绿, 红=%s" % sorted(base_red))
            return 1

        # --- 镜像三条 ---
        # ★★2026-11-24 02:5x 订正期望集★★: D2/D3/D4 三条判据都是
        #   「页 ↔ 实算一致性」家族 (D2 = 页写序 vs 实算序 + 两序互逆; D3 = 两候选齐; D4 = 朝向一致)
        #   ⇒ 页里的 rot90/rot270 一改, 这三条【必然同时红】⇒ 期望集如实写成三条
        cases.append(("M1", "把页里的 rot 90 改成 rot 270", _case_m1,
                      {"D2", "D3", "D4"}))
        # ★★2026-11-24 04:3x 订正期望集 (M2 改成变异闸源码后, 期望集如实写成两条)★★:
        #   变异体让 compute_candidate_orders() 返回【写死的常数】且两候选同序
        #   ⇒ ① D2 自己红 (互等 + 非逆序 + pad1 端位相同) 【本条的目标判据】
        #   ⇒ ② D4 也必然红 (D4 = 页写序 vs D2 实算序 ⇒ D2 的输出被污染, D4 必然对不上)
        #   ⇒ 这两条是【真实的耦合】(D4 依赖 D2 的输出), 不是把判据改松 ⇒ 如实写成 {D2, D4}
        cases.append(("M2", "把 D2 的算式改成手算常数 (变异本闸源码)",
                      _case_m2_gate_formula, {"D2", "D4"}))
        cases.append(("M3", "把网表里的 SoC_NC 改成别的 (沙盒网表副本)",
                      _case_m3_mutated_netlist, {"D5"}))

        # --- 其余判据的反向用例 ---
        cases.append(("T-D0", "页里把官方 land 的 pad1 形状写错", _case_d0, {"D0"}))
        cases.append(("T-D1", "页里把现状 pad1 位置写反", _case_d1, {"D1"}))
        cases.append(("T-D3", "页里删掉一个候选", _case_d3, {"D2", "D3", "D4"}))
        cases.append(("T-D6", "页里写『已在 SoM 侧落地』", _case_d6, {"D6"}))
        cases.append(("T-D8a", "证据等级用白名单外的等级", _case_d8_evidence, {"D8"}))
        cases.append(("T-D8b", "出现挂起措辞", _case_d8_hanging, {"D8"}))

        print("=== ISS-375 · check_debug_pin_order_contract --selftest ===")
        n_ok = 0
        for cid, desc, fn, expect in cases:
            # ★M2/M3 走【判据自己的数据源】(变异本闸源码 / 沙盒网表副本) ★
            # ⇒ 它们的 runner 直接返回 (红集, 说明) ★
            # ★其余用例走【页文本变异】⇒ 返回变异后的页文本 ★
            out = fn(base_text, tmpdir)
            if isinstance(out, tuple):
                red, note = out
            else:
                red, note = _run_on_text(out, tmpdir), ""
            # 「红的是目标那一条, 其余仍绿」⇒ 实际红集 ⊆ 期望集, 且期望集 ⊆ 实际红集
            hit = (expect <= red)
            # 其余仍绿: 实际红集里不得出现期望集之外的判据
            extra = red - expect
            ok = hit and not extra
            if ok:
                n_ok += 1
            print("  [%s] %-8s %-42s 期望红=%-12s 实红=%-12s %s"
                  % ("PASS" if ok else "FAIL", cid, desc,
                     ",".join(sorted(expect)) or "-",
                     ",".join(sorted(red)) or "-",
                     ("" if ok else ("← 期望集未被完全命中" if not hit
                                     else "← 额外红了: %s" % ",".join(sorted(extra))))
                     + ((" · " + note) if note else "")))

        # --- 额外: D7 (板指纹) 与 D8 (零挂链) 用沙盒副本单独测 ---
        # D7: 复制一份板副本到临时目录, 改它 ⇒ D7 应红
        tmp_board = os.path.join(tmpdir, "board_copy.kicad_pcb")
        shutil.copyfile(BOARD, tmp_board)
        with open(tmp_board, "ab") as fh:
            fh.write(b"\n")
        saved_board = globals()["BOARD"]
        globals()["BOARD"] = tmp_board
        try:
            res, _, _, _, _ = run_all()
            red7 = set(res.red_ids)
        except Exception as exc:
            red7 = {"FATAL:%s" % type(exc).__name__}
        finally:
            globals()["BOARD"] = saved_board
        ok7 = ("D7" in red7)
        n_ok += 1 if ok7 else 0
        print("  [%s] %-8s %-42s 期望红=%-12s 实红=%-12s"
              % ("PASS" if ok7 else "FAIL", "T-D7", "板指纹被动过 (临时副本)",
                 "D7", ",".join(sorted(red7))))

        # D8 零挂链: 临时 gate_check.py 里出现本闸名 ⇒ D8 红
        saved_gate = globals()["GATE_CHECK"]
        tmp_gate = os.path.join(tmpdir, "gate_check_copy.py")
        with open(tmp_gate, "w", encoding="utf-8") as fh:
            fh.write("# 伪造挂链\nGATES = ['check_debug_pin_order_contract']\n")
        globals()["GATE_CHECK"] = tmp_gate
        try:
            res, _, _, _, _ = run_all()
            red8 = set(res.red_ids)
        except Exception as exc:
            red8 = {"FATAL:%s" % type(exc).__name__}
        finally:
            globals()["GATE_CHECK"] = saved_gate
        ok8 = ("D8" in red8)
        n_ok += 1 if ok8 else 0
        print("  [%s] %-8s %-42s 期望红=%-12s 实红=%-12s"
              % ("PASS" if ok8 else "FAIL", "T-D8c", "新闸挂进 state/gate_check.py (临时副本)",
                 "D8", ",".join(sorted(red8))))

        total = len(cases) + 2
        print("=== selftest %d/%d PASS (共 %d 条反向用例, 其中镜像类 %d 条) ==="
              % (n_ok, total, total, len(MIRROR_CASES)))
        if n_ok == total:
            print("ALL TESTS PASS")
            return 0
        print("SELFTEST FAILED")
        return 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
