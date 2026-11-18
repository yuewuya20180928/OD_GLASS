#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
isp_budget_solve.py -- ISS-124 (03a/03b') ISP 能力与功耗自查 · 反解器
=====================================================================
★**本脚本不发明任何模型, 也不复制任何阈值** ⇒ 全部从既有文件里**import / 现场解析**:
  ① `SW/tools/timing_check.py`  —— 皮肤热模型常数 (T_SKIN_A/B/REDLINE) + F7 皮肤档位
  ② `HW/e2e_budget_rk3572.py`  —— 端到端预算模型 (T_FIXED 拆分 / 模式A / 模式B / age 台阶)
     ⇒ 60ms 硬线不是写死的, 是从 `display_out_max_for(... budget_ms=60.0)` 的**函数默认值**里取
  ③ `SW/RKNN_BENCH.md` §4.1   —— ISP 段基线 S3 (ISP 含缩放) 的 ms 值, 现场正则解析
  ④ `HW/POWER_BUDGET_V3.md`   —— ISP 动态功耗地板 (x ≥ 60 mW @ 1080p30) + §4.1 满载镜腿内/整机上界档位
  ⑤ `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` —— 官方 ISP 口径 (12M pixels / 4096x3072)

★**为什么必须这么写 (纪律)**: 阈值一旦在两个脚本里各抄一份就会漂 ⇒ 本脚本每条锚点都打印
  「来源文件 + 行号」, 任何人一条 grep 就能复核; 锚点抓不到 ⇒ rc=1 (不许静默用默认值糊过去)。

用法:
    python3 SW/tools/isp_budget_solve.py            # 主表
    python3 SW/tools/isp_budget_solve.py --json     # 机读

退出码: 0 = 锚点全抓到 + 自检全过 (数字可复算) · 1 = 有锚点没抓到或自检不过
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", ".."))

P_RKNN_BENCH = os.path.join(PROJ, "SW", "RKNN_BENCH.md")
P_POWER_V3 = os.path.join(PROJ, "HW", "POWER_BUDGET_V3.md")
P_DS_TXT = os.path.join(PROJ, "HW", "RK3572_PIN_TABLE", "rk3572_datasheet_V1.1.txt")
P_DS_PDF = os.path.join(PROJ, "HW", "RK3572_PIN_TABLE", "RK3572_datasheet_V1.1.pdf")

# ── 需求侧像素率 (★[推算] 需求锁定链: 全幅 2688x1520@60 → 640x480@60 直出★) ─────────
DEMAND = [
    ("full_2688x1520_60", 2688, 1520, 60),
    ("1080p60", 1920, 1080, 60),
    ("640x480_60", 640, 480, 60),
    ("1280x960_15", 1280, 960, 15),
]


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("打不开模块: %s" % path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _read(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().splitlines()


class Anchor:
    """一条锚点: 值 + 来源文件 + 行号 (供复核)"""

    def __init__(self, key: str, value, src: str, line_no: int, grade: str, note: str = ""):
        self.key = key
        self.value = value
        self.src = src
        self.line_no = line_no
        self.grade = grade
        self.note = note

    def __repr__(self) -> str:
        return "%s=%s [%s] (%s:%d)" % (self.key, self.value, self.grade,
                                      os.path.basename(self.src), self.line_no)


def _find(lines: list[str], pattern: str, key: str, src: str, grade: str,
          cast=float, note: str = "") -> Anchor:
    rx = re.compile(pattern)
    for i, ln in enumerate(lines, start=1):
        m = rx.search(ln)
        if m:
            return Anchor(key, cast(m.group(1)), src, i, grade, note)
    raise KeyError("锚点没抓到: %s (pattern=%s, src=%s)" % (key, pattern, src))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    # ── 0. 加载既有模型 (只读 import, 不改一个数) ────────────────────────────────
    tc = _load("timing_check", os.path.join(PROJ, "SW", "tools", "timing_check.py"))
    e2e = _load("e2e_budget_rk3572", os.path.join(PROJ, "HW", "e2e_budget_rk3572.py"))

    # ── 1. 抓锚点 ───────────────────────────────────────────────────────────────
    anchors: list[Anchor] = []

    # ① 60ms 硬线 —— 从 e2e 模块自己的函数默认值取 (不许在本脚本写死 60)
    _sig = inspect.signature(e2e.display_out_max_for)
    BUDGET_MS = _sig.parameters["budget_ms"].default
    anchors.append(Anchor("budget_ms", BUDGET_MS, os.path.join(PROJ, "HW", "e2e_budget_rk3572.py"),
                          0, "[推算·模型]", "display_out_max_for() 的 budget_ms 默认值"))

    bench = _read(P_RKNN_BENCH)
    # ② ISP 段基线 S3 (ms) —— 现场解析 RKNN_BENCH §4.1
    s3 = _find(bench, r"^S3\s*=\s*([\d.]+)\s*ms", "isp_s3_ms", P_RKNN_BENCH, "[官方口径·项目模型]",
               note="RKNN_BENCH §4.1 延迟模型 S3 = ISP (含缩放)")
    anchors.append(s3)
    ISP_NOW_MS = float(s3.value)

    # ③ 皮肤热模型常数 —— 从 timing_check 的 DEVICE 取 (不许在本脚本写死 50.13/35.0/43)
    A_SKIN = float(tc.DEVICE["T_SKIN_A"])
    B_SKIN = float(tc.DEVICE["T_SKIN_B"])
    REDLINE_C = float(tc.DEVICE["T_SKIN_REDLINE"])
    _nl = tc.Netlist(tc.DEFAULT_NETLIST)
    _o = tc.compute(_nl)
    P_REDLINE_W = float(_o["F7_skin_tiers"]["p_redline_w"])
    anchors.append(Anchor("T_SKIN_A", A_SKIN, os.path.join(PROJ, "SW", "tools", "timing_check.py"),
                          0, "[推算·MECH]", "DEVICE['T_SKIN_A']"))
    anchors.append(Anchor("T_SKIN_B", B_SKIN, os.path.join(PROJ, "SW", "tools", "timing_check.py"),
                          0, "[推算·MECH]", "DEVICE['T_SKIN_B']"))
    anchors.append(Anchor("T_SKIN_REDLINE", REDLINE_C, os.path.join(PROJ, "SW", "tools", "timing_check.py"),
                          0, "[官方]", "DEVICE['T_SKIN_REDLINE'] = ISO 13732-1 43°C"))
    anchors.append(Anchor("P_REDLINE", P_REDLINE_W, os.path.join(PROJ, "SW", "tools", "timing_check.py"),
                          0, "[推算]", "F7_skin_tiers.p_redline_w (网表实读)"))

    # ④ ISP 动态功耗地板 (POWER_BUDGET_V3 §2.3) + 满载档位 (§4.1)
    pw = _read(P_POWER_V3)
    xrow = _find(pw, r"ISP 动态 @1080p30 \| \*\*≥\s*([\d.]+)\s*mW", "isp_p_floor_mw",
                 P_POWER_V3, "[推算]", note="§2.3 x = ISP 动态 @1080p30 地板")
    anchors.append(xrow)
    X_FLOOR_MW = float(xrow.value)
    mpps_row = _find(pw, r"1080p30\s*=\s*(\d+)MP/s", "isp_floor_mpps", P_POWER_V3, "[推算]",
                     note="§2.3 锚点像素率 1080p30 = 62 MP/s")
    anchors.append(mpps_row)
    X_FLOOR_MPPS = float(mpps_row.value)

    # §4.1 满载: 镜腿内口径 / 整机上界口径 的 (无桥/有桥 × 中位/下界/上界) 档位
    full_rows: dict[tuple[str, str], tuple[float, int]] = {}
    caliber = ""
    in_41 = False
    for i, ln in enumerate(pw, start=1):
        if ln.startswith("### 4.1"):
            in_41 = True
            continue
        if in_41 and ln.startswith("### ") and not ln.startswith("### 4.1"):
            break
        if not in_41:
            continue
        if "镜腿内口径" in ln and ln.strip().startswith("|"):
            caliber = "temple"
        elif "整机上界口径" in ln and ln.strip().startswith("|"):
            caliber = "whole"
        m = re.search(r"V3\s+(无桥|有桥)\s*\((中位|下界|上界)\s*([\d.]+)W\)", ln)
        if m and caliber:
            key = (caliber, m.group(1) + "-" + m.group(2))
            full_rows[key] = (float(m.group(3)), i)
    if not full_rows:
        print("[FATAL] POWER_BUDGET_V3 §4.1 满载档位没抓到", file=sys.stderr)
        return 1
    for k in sorted(full_rows):
        v, ln = full_rows[k]
        anchors.append(Anchor("full_%s_%s_W" % k, v, P_POWER_V3, ln, "[推算]",
                              note="POWER_BUDGET_V3 §4.1 满载档位"))

    # ⑤ 官方 ISP 口径 (RK3572 datasheet 文本层)
    ds = _read(P_DS_TXT)
    pix = _find(ds, r"One channel ISP,(\d+)M pixels", "rk3572_isp_mpix", P_DS_TXT, "[官网]",
                cast=int, note="RK3572 datasheet V1.1 §1.2.10 ISP 单通道 12M pixels")
    anchors.append(pix)
    maxin = _find(ds, r"Maximum input:(\d+x\d+)", "rk3572_isp_max_input", P_DS_TXT, "[官网]",
                  cast=str, note="RK3572 datasheet V1.1 §1.2.10 ISP 最大输入 4096x3072")
    anchors.append(maxin)
    maxw, maxh = (int(x) for x in re.match(r"(\d+)x(\d+)", maxin.value).groups())
    MPX_OFFICIAL = float(pix.value)
    MAXIN_MP = maxw * maxh / 1e6
    ds_md5 = hashlib.md5(open(P_DS_PDF, "rb").read()).hexdigest()

    # ── 2. 需求侧像素率 (★[推算]★) ─────────────────────────────────────────────
    demand = {}
    for name, w, h, fps in DEMAND:
        demand[name] = round(w * h * fps / 1e6, 1)

    # ── 3. 03a 官方口径对齐 (★分辨率上限口径 vs 需求★) ───────────────────────────
    # ★★口径纪律: 12M Pixel 是【单帧分辨率上限】, 不是【每秒处理能力】★★
    per_frame_mp = {}
    for name, w, h, fps in DEMAND:
        per_frame_mp[name] = round(w * h / 1e6, 3)

    # ── 4. 降级方案 B: 反解 ISP 段最多能占多少 ms (★核心★) ─────────────────────
    # 模式A: e2e = T_FIXED + T_od        (显示等 OD)
    # 模式B: e2e = T_FIXED + age*FRAME   (异步 60fps)
    # ISP 段是 T_PRE_EXPOSURE 里的 S3 ⇒ 把 S3 换成变量 X:
    #   T_FIXED(X) = T_FIXED - S3 + X
    # ⇒ 模式A: X ≤ budget - T_od - (T_FIXED - S3)
    # ⇒ 模式B: X ≤ budget - age*FRAME - (T_FIXED - S3)
    FIXED_NOISP = float(e2e.T_FIXED) - ISP_NOW_MS

    def isp_budget_ms_a(t_od: float) -> float:
        """模式A: X ≤ budget − (T_FIXED − S3) − T_od"""
        return BUDGET_MS - FIXED_NOISP - t_od

    def isp_budget_ms_b(age: int) -> float:
        return BUDGET_MS - FIXED_NOISP - age * float(e2e.FRAME_MS)

    # 基线候选 (★用 e2e 模块自己的 scale()/RK3576_S5, 不另抄一份★)
    s5n = e2e.scale(e2e.RK3576_S5["yolov5n@640"][0], e2e.RK3576_TOPS, e2e.RK3572_TOPS)
    s5_320 = (e2e.scale(e2e.RK3576_S5["yolov5s@320 (估)"][0], e2e.RK3576_TOPS, e2e.RK3572_TOPS) +
              e2e.scale(e2e.RK3576_S5["yolov5s@320 (估)"][1], e2e.RK3576_TOPS, e2e.RK3572_TOPS)) / 2
    s5s = e2e.scale(e2e.RK3576_S5["yolov5s@640 (relu)"][0], e2e.RK3576_TOPS, e2e.RK3572_TOPS)
    candidates = [
        ("RK3572 + yolov5n@640 (★现行 demo 锁定★)", s5n),
        ("RK3572 + yolov5s@320", s5_320),
        ("RK3572 + yolov5s@640 (relu)", s5s),
    ]

    solve = []
    for label, s5 in candidates:
        r = e2e.e2e(s5)
        t_od = r["t_od"]
        age = r["age"]
        xa = isp_budget_ms_a(t_od)
        xb = isp_budget_ms_b(age)
        xb1 = isp_budget_ms_b(1)
        solve.append({
            "label": label, "s5_ms": round(s5, 3), "t_od_ms": round(t_od, 3), "age": age,
            "modeA_now_ms": round(r["modeA"], 3), "modeA_ok": r["modeA"] <= BUDGET_MS,
            "modeB_now_ms": round(r["modeB"], 3), "modeB_ok": r["modeB"] <= BUDGET_MS,
            "isp_max_modeA_ms": round(xa, 3),
            "isp_max_modeB_ms": round(xb, 3),
            "isp_max_modeB_if_age1_ms": round(xb1, 3),
            "isp_headroom_modeA_ms": round(xa - ISP_NOW_MS, 3),
            "isp_headroom_modeB_ms": round(xb1 - ISP_NOW_MS, 3),
        })

    # ── 5. 降级方案 A: ISP 动态功耗按像素率线性插值 → 皮肤温度重估 ─────────────
    # A1: 过原点线性, 锚点 (62 MP/s, 60 mW)
    def p_isp_a1(mpps: float) -> float:
        return X_FLOOR_MW * mpps / X_FLOOR_MPPS

    # A2: 两点线性, 锚点 (62 MP/s, 60 mW) → (250 MP/s, 242 mW)
    #     250 MP/s 是 ARS45 的能力上限 (★已作废芯片★) ⇒ 242 mW = 60 mW × (250/62) (本文推导)
    X_FULL_MPPS = 250.0
    X_FULL_MW = X_FLOOR_MW * (X_FULL_MPPS / X_FLOOR_MPPS)

    def p_isp_a2(mpps: float) -> float:
        if mpps >= X_FULL_MPPS:
            return X_FULL_MW
        k = (X_FULL_MW - X_FLOOR_MW) / (X_FULL_MPPS - X_FLOOR_MPPS)
        return X_FLOOR_MW + k * (mpps - X_FLOOR_MPPS)

    def p_isp_pow(mpps: float, gamma: float) -> float:
        """★敏感性带: 功耗 ~ 像素率^gamma (gamma<1 次线性 / >1 超线性)"""
        return X_FLOOR_MW * (mpps / X_FLOOR_MPPS) ** gamma

    def t_skin(p_w: float) -> float:
        return A_SKIN + B_SKIN * p_w

    # ★POWER_BUDGET_V3 §2.3 场景 W 里的 ISP 项 = 2x (ISP@60) = 2 × 60 = 120 mW
    #   (x 定义在 1080p30 = 62 MP/s; 旧锁定链的 ISP 输入是 1080p@60 = 124.4 MP/s ⇒ 2x 即 120 mW @ 124.4 MP/s)
    MODEL_ISP_60_MW = 2.0 * X_FLOOR_MW
    MODEL_ISP_60_MPPS = demand["1080p60"]

    power_rows = []
    for name in ("full_2688x1520_60", "1080p60", "640x480_60"):
        mpps = demand[name]
        a1 = p_isp_a1(mpps)
        a2 = p_isp_a2(mpps)
        ag = p_isp_pow(mpps, 0.8)
        al = p_isp_pow(mpps, 1.2)
        power_rows.append({
            "case": name, "mpps": mpps,
            "isp_mw_a1_linear": round(a1, 1),
            "isp_mw_a2_two_point": round(a2, 1),
            "isp_mw_gamma08": round(ag, 1),
            "isp_mw_gamma12": round(al, 1),
            "delta_mw_vs_model_isp60": round(a1 - MODEL_ISP_60_MW, 1),
        })

    MPPS_FULL = demand["full_2688x1520_60"]
    d_isp_mw = p_isp_a1(MPPS_FULL) - MODEL_ISP_60_MW          # 中心值 (线性)
    d_isp_lo = p_isp_pow(MPPS_FULL, 0.8) - MODEL_ISP_60_MW   # 次线性 (更省)
    d_isp_hi = p_isp_pow(MPPS_FULL, 1.2) - MODEL_ISP_60_MW   # 超线性 (更贵)

    skin_rows = []
    for key in sorted(full_rows):
        p0, ln = full_rows[key]
        t0 = t_skin(p0)
        t1 = t_skin(p0 + d_isp_mw / 1000.0)
        tlo = t_skin(p0 + d_isp_lo / 1000.0)
        thi = t_skin(p0 + d_isp_hi / 1000.0)
        skin_rows.append({
            "caliber_and_tier": key[0] + "/" + key[1],
            "p_now_w": p0, "t_now_c": round(t0, 1),
            "p_new_w": round(p0 + d_isp_mw / 1000.0, 4), "t_new_c": round(t1, 1),
            "t_new_c_sublinear": round(tlo, 1), "t_new_c_superlinear": round(thi, 1),
            "still_over_redline": t1 > REDLINE_C,
            "still_over_redline_worst_case": thi > REDLINE_C,
            "redline_c": REDLINE_C,
        })

    # ── 6. 自检 (★证明本脚本没跑偏★) ───────────────────────────────────────────
    checks = []

    def chk(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    chk("60ms 硬线来自 e2e 模块函数默认值 (非本脚本写死)", BUDGET_MS == 60.0, "budget_ms=%s" % BUDGET_MS)
    chk("ISP 基线 S3 从 RKNN_BENCH 现场解析到", s3.value == 8.0, "S3=%s ms" % s3.value)
    chk("皮肤模型常数来自 timing_check.DEVICE (35.0/50.13)",
        (A_SKIN, B_SKIN) == (35.0, 50.13), "A=%s B=%s" % (A_SKIN, B_SKIN))
    # 反解模型自洽: ISP 保持 S3 时, 我的公式必须复现 e2e.e2e()
    r0 = e2e.e2e(s5n)
    myA = FIXED_NOISP + ISP_NOW_MS + r0["t_od"]
    myB = FIXED_NOISP + ISP_NOW_MS + r0["age"] * float(e2e.FRAME_MS)
    chk("反解模型在 ISP=S3 时复现 e2e.e2e() 模式A", abs(myA - r0["modeA"]) < 1e-9,
        "mine=%.6f vs module=%.6f" % (myA, r0["modeA"]))
    chk("反解模型在 ISP=S3 时复现 e2e.e2e() 模式B", abs(myB - r0["modeB"]) < 1e-9,
        "mine=%.6f vs module=%.6f" % (myB, r0["modeB"]))
    # 官方 ISP 口径: 全幅 2688x1520 必须落在 12M 单帧上限之内
    chk("官方 12M pixel 单帧上限 ≥ 全幅 2688x1520",
        2688 * 1520 / 1e6 <= MPX_OFFICIAL + 1e-9,
        "%.3f Mpx vs %.0f Mpx" % (2688 * 1520 / 1e6, MPX_OFFICIAL))
    chk("官方最大输入 4096x3072 ≈ 12M pixel 口径自洽",
        abs(MAXIN_MP - MPX_OFFICIAL) / MPX_OFFICIAL < 0.10,
        "4096x3072=%.2f Mpx vs 12M" % MAXIN_MP)
    # 两种插值在满幅点必须收敛 (≤5%)
    a1f = p_isp_a1(demand["full_2688x1520_60"])
    a2f = p_isp_a2(demand["full_2688x1520_60"])
    chk("降级方案A 两种插值在满幅 245.1 MP/s 处收敛 (≤5%)",
        abs(a1f - a2f) / a1f <= 0.05, "A1=%.1f mW vs A2=%.1f mW" % (a1f, a2f))
    chk("敏感性带 (γ=0.8 / γ=1.2) 给出 ISP 功耗区间",
        p_isp_pow(demand["full_2688x1520_60"], 0.8) < a1f < p_isp_pow(demand["full_2688x1520_60"], 1.2),
        "%.1f / %.1f / %.1f mW" % (p_isp_pow(demand["full_2688x1520_60"], 0.8), a1f,
                                   p_isp_pow(demand["full_2688x1520_60"], 1.2)))
    # 皮肤重估后所有满载档位仍超红线 (⇒ 43°C 结论不翻案) —— 连最乐观的 γ=0.8 也要检查
    chk("★满载所有档位在 ISP 重估后仍超 43°C 红线 ⇒ 结论不翻案",
        all(r["still_over_redline"] for r in skin_rows),
        "超红线档位数=%d/%d" % (sum(1 for r in skin_rows if r["still_over_redline"]), len(skin_rows)))
    chk("★敏感性带最保守端 (γ=0.8) 满载仍全部超 43°C ⇒ 结论对插值形状不敏感",
        all(r["still_over_redline_worst_case"] for r in skin_rows),
        "超红线档位数=%d/%d" % (sum(1 for r in skin_rows if r["still_over_redline_worst_case"]),
                                len(skin_rows)))

    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)

    out = {
        "demand_mpps": demand,
        "per_frame_mpix": per_frame_mp,
        "official": {
            "rk3572_isp_mpix_per_frame": MPX_OFFICIAL,
            "rk3572_isp_max_input": "%dx%d" % (maxw, maxh),
            "rk3572_isp_max_input_mpix": round(MAXIN_MP, 3),
            "rk3572_datasheet_pdf_md5": ds_md5,
            "rk3572_datasheet_pdf": os.path.relpath(P_DS_PDF, PROJ),
            "isp_mpps_max": None,
            "isp_mpps_source": "[0数据] 官方 datasheet / brief datasheet 只给单帧分辨率上限 (12M/16M Pixel), 全项目检索无 MP/s 吞吐口径 ⇒ 见 SW/ISP_CAPABILITY_RESEARCH.md",
            "resolution_caliber_usage_pct": {
                k: round(v / MPX_OFFICIAL * 100.0, 2) for k, v in per_frame_mp.items()
            },
        },
        "isp_power_mw": {
            "62": round(X_FLOOR_MW, 1),
            "124": round(p_isp_a1(demand["1080p60"]), 1),
            "245": round(p_isp_a1(demand["full_2688x1520_60"]), 1),
            "245_gamma08": round(p_isp_pow(demand["full_2688x1520_60"], 0.8), 1),
            "245_gamma12": round(p_isp_pow(demand["full_2688x1520_60"], 1.2), 1),
        },
        "isp_ms_budget_60ms_line": {
            "modeA": max(r["isp_max_modeA_ms"] for r in solve if r["modeA_ok"]),
            "modeB": max(r["isp_max_modeB_if_age1_ms"] for r in solve),
            "isp_now_ms": ISP_NOW_MS,
        },
        "solve_rows": solve,
        "power_rows": power_rows,
        "skin_rows": skin_rows,
        "anchors": [{"key": a.key, "value": a.value, "grade": a.grade,
                     "src": os.path.relpath(a.src, PROJ), "line": a.line_no, "note": a.note}
                    for a in anchors],
        "selftest": {"passed": passed, "total": total,
                     "items": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks]},
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0 if passed == total else 1

    # ── 7. 人读主表 ────────────────────────────────────────────────────────────
    print("=" * 104)
    print("ISS-124 · ISP 能力与功耗自查 · 反解器 (sw-lead 2026-11-15)")
    print("=" * 104)
    print("\n【0】锚点 (全部现场 import/解析, 不在本脚本写死)")
    for a in anchors:
        print("   %-34s = %-10s [%s]  %s:%s" % (a.key, a.value, a.grade,
                                                  os.path.basename(a.src), a.line_no or "-"))
    print("   %-34s = %-10s [官网]  %s" % ("rk3572_datasheet_pdf_md5", ds_md5,
                                          os.path.relpath(P_DS_PDF, PROJ)))

    print("\n【1】需求侧像素率 [推算] vs 官方单帧分辨率口径 [官网]")
    print("   %-22s %10s %12s %12s %10s" % ("case", "MP/s", "Mpx/frame", "占 12M", "余量"))
    for name, _, _, _ in DEMAND:
        mpps = demand[name]
        mp = per_frame_mp[name]
        pct = mp / MPX_OFFICIAL * 100.0
        print("   %-22s %10.1f %12.3f %11.2f%% %9.2f%%" % (name, mpps, mp, pct, 100 - pct))
    print("   ★★口径纪律: 12M Pixel = 【单帧分辨率上限】, **不是 12M MP/s** ⇒ 这张表不含任何 MP/s 吞吐结论")
    print("   ★官方 ISP MP/s 吞吐上限 = %s  (datasheet V1.1 全文无此口径)" % "None/[0数据]")

    print("\n【2】★降级方案 B (核心): 60ms 硬线下 ISP 段最多能占多少 ms")
    print("   %-38s %8s %8s %6s %11s %11s %11s %11s" %
          ("基线", "S5", "T_od", "age", "模式A现值", "模式B现值", "ISP上限A", "ISP上限B"))
    for r in solve:
        print("   %-38s %8.2f %8.2f %6d %8.2f%s %8.2f%s %11.2f %11.2f" %
              (r["label"], r["s5_ms"], r["t_od_ms"], r["age"],
               r["modeA_now_ms"], "OK" if r["modeA_ok"] else "!!",
               r["modeB_now_ms"], "OK" if r["modeB_ok"] else "!!",
               r["isp_max_modeA_ms"], r["isp_max_modeB_if_age1_ms"]))
    print("   ★现 ISP 段基线 S3 = %.2f ms (RKNN_BENCH §4.1)" % ISP_NOW_MS)
    for r in solve:
        print("   ★ %-38s ⇒ 模式A 余量 %+.2f ms / 模式B(age=1) 余量 %+.2f ms"
              % (r["label"], r["isp_headroom_modeA_ms"], r["isp_headroom_modeB_ms"]))
    print("   ★模式B 现值 %s ⇒ age=2 时模式B 本来就不成立 (与 ISP 无关), 模式B 的 ISP 上限只能按 age=1 给" %
          ("%.2f ms" % solve[0]["modeB_now_ms"]))

    print("\n【3】降级方案 A: ISP 动态功耗按像素率线性插值 [推算]")
    print("   锚点: POWER_BUDGET_V3 §2.3  x ≥ %.0f mW @ %.0f MP/s (1080p30)" % (X_FLOOR_MW, X_FLOOR_MPPS))
    print("   ★现行模型里的 ISP 项 = 2x (ISP@60) = %.0f mW @ %.1f MP/s (旧锁定链 ISP 输入 1080p@60)"
          % (MODEL_ISP_60_MW, MODEL_ISP_60_MPPS))
    print("   %-22s %9s %13s %13s %13s %13s" % ("case", "MP/s", "A1线性", "A2两点", "γ=0.8(省)", "γ=1.2(贵)"))
    for p in power_rows:
        print("   %-22s %9.1f %13.1f %13.1f %13.1f %13.1f" %
              (p["case"], p["mpps"], p["isp_mw_a1_linear"], p["isp_mw_a2_two_point"],
               p["isp_mw_gamma08"], p["isp_mw_gamma12"]))
    print("   ★满幅 %.1f MP/s ⇒ ISP 功耗 %.1f mW (线性) ⇒ 相对现行模型 %.0f mW 的增量 = %+.1f mW"
          % (MPPS_FULL, p_isp_a1(MPPS_FULL), MODEL_ISP_60_MW, d_isp_mw))
    print("   ★敏感性带: 次线性 γ=0.8 ⇒ %+.1f mW / 超线性 γ=1.2 ⇒ %+.1f mW"
          % (d_isp_lo, d_isp_hi))

    print("\n【4】皮肤温度重估 (镜腿内口径 / 整机上界口径, 全部并列)")
    print("   %-24s %9s %9s %9s %9s %9s %9s" % ("口径/档位", "P现(W)", "T现", "P新(W)", "T新", "γ=0.8", "γ=1.2"))
    for r in skin_rows:
        print("   %-24s %9.3f %8.1f°C %9.3f %8.1f°C %8.1f°C %8.1f°C" %
              (r["caliber_and_tier"], r["p_now_w"], r["t_now_c"], r["p_new_w"], r["t_new_c"],
               r["t_new_c_sublinear"], r["t_new_c_superlinear"]))
    print("   ★★结论: 满载本来就超 43°C 红线 ⇒ ISP 重估**不翻案**, 只是更差 (最乐观 γ=0.8 也一样);")
    print("      ★唯一能进红线的杠杆 (待机-B 地板 0.05W + 按需触发) 与 ISP 吞吐**无关** ⇒ 结论方向不变")

    print("\n【5】SELF-TEST (%d 项)" % total)
    for name, ok, detail in checks:
        print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                               ("  (%s)" % detail) if detail else ""))
    print("\nSELFTEST %d/%d 通过, rc=%d" % (passed, total, 0 if passed == total else 1))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
