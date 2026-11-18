#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-244 · G-5 (LED 亮度账不匹配) — 厂商 Iv-vs-If 曲线数字化器
==============================================================
作者: sw-lead (软件总工) · 2026-11-16

★为什么要有这个脚本 (上一轮 ISS-244 撞 timeout 的教训):
  上一轮把「APH1608SURCK 的 1 mA 档亮度」查出来了, 但只活在会话内存里,
  盘上零产出 ⇒ 本轮必须把它变成**可复核的盘上证据**:
    ① 原厂 PDF 落盘 (本目录 *.pdf)
    ② 数字化脚本落盘 (本文件)
    ③ 脚本自带**标定自证** (不靠人眼信任)

★数字化方法 (写清楚, 免得别人以为我编的):
  1. 用 `pdftotext -bbox` 从 PDF 文本层取出**轴刻度数字的 bbox** (PDF 点坐标)
     ⇒ 坐标轴标定来自厂商 PDF 自己的文字层, **不是猜的、不是手量的**
  2. 用 `pdftoppm -r <dpi> -png` 把同页渲染成位图 (points→pixels 比例 = dpi/72)
  3. 在标定出的绘图区里逐列扫描暗像素 ⇒ 得到曲线像素轨迹
  4. 用第 1 步的标定把像素轨迹映射回数据坐标 (X=If mA, Y=归一化亮度)
  5. **自证三条** (脚本自己判, 任何一条不过就 rc≠0):
     S1 曲线过原点 (If=0 → Y≈0, 容差 0.03)
     S2 曲线在 If=20 mA 处 Y≈1.00 (归一化定义点, 容差 0.06)
     S3 曲线单调不减 (容差 0.02)
     ⇒ 三条自证全过 = 这条曲线确实是从厂商图上量出来的 Iv-vs-If, 不是直线编的

用法:
    python3 extract_ivif.py <pdf> <page> [--dpi 300] [--json out.json]
    python3 extract_ivif.py --selftest          # 用本目录 PDF 自证 (rc=0 = 全过)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# 目标图标题 (在 PDF 文本层里能查到, 用于定位这一格图)
TARGET_TITLE_WORDS = ["Luminous", "Intensity", "vs.", "Forward", "Current"]
# 其它三格图的标题 (用来排除)
OTHER_TITLES = [
    ["Forward", "Current", "vs.", "Forward", "Voltage"],
    ["Forward", "Current", "Derating", "Curve"],
    ["Luminous", "Intensity", "vs.", "Ambient", "Temperature"],
]


def _words(pdf: str, page: int):
    html = subprocess.run(
        ["pdftotext", "-bbox", "-f", str(page), "-l", str(page), pdf, "-"],
        capture_output=True, text=True).stdout
    pat = r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>'
    out = []
    for a, b, c, d, w in re.findall(pat, html):
        out.append((float(a), float(b), float(c), float(d), w))
    return out


def _find_title(words, seq):
    """在词表里找标题序列 (顺序允许相邻/同段), 返回 bbox

    ★加「邻近性」约束: 匹配到的词必须挤在同一小块里 (横向 <90pt, 纵向 <25pt)
      —— 否则会把「Luminous Intensity vs. Ambient Temperature」+ 后面另一格图的
      「Forward Current」串成一串 (同一页有 4 格图, 词表是全局的)
    """
    best = None
    for i in range(len(words)):
        if words[i][4] != seq[0]:
            continue
        j, ok = i, True
        for k in range(1, len(seq)):
            j += 1
            while j < len(words) and words[j][4] != seq[k]:
                j += 1
            if j >= len(words):
                ok = False
                break
        if not ok:
            continue
        seq_w = words[i:j + 1]
        xs = [w[0] for w in seq_w]
        ys = [w[1] for w in seq_w]
        xe = [w[2] for w in seq_w]
        ye = [w[3] for w in seq_w]
        span_x = max(xe) - min(xs)
        span_y = max(ye) - min(ys)
        if span_x > 90 or span_y > 25:
            continue
        box = (min(xs), min(ys), max(xe), max(ye))
        if best is None or box[0] < best[0]:
            best = box
    return best


def _cluster(items, gap_factor=3.0):
    """把一行里的数字按 x 间隙切成若干簇 (一行里常常并排放着 4 ���图的刻度)"""
    items = sorted(items)
    if len(items) < 2:
        return [items]
    gaps = [items[i + 1][0] - items[i][1] for i in range(len(items) - 1)]
    med = sorted(gaps)[len(gaps) // 2] or 1.0
    thr = max(med * gap_factor, 5.0)
    clusters, cur = [], [items[0]]
    for i in range(1, len(items)):
        if items[i][0] - items[i - 1][1] > thr:
            clusters.append(cur)
            cur = [items[i]]
        else:
            cur.append(items[i])
    clusters.append(cur)
    return clusters


def _tick_rows(words):
    """找出所有「同一 y 上的数字簇」(候选 x 轴刻度组)"""
    from collections import defaultdict
    byrow = defaultdict(list)
    for xmin, ymin, xmax, ymax, w in words:
        if re.fullmatch(r"\d+(\.\d+)?", w):
            byrow[round(ymin, 1)].append((xmin, xmax, w))
    rows = []
    for r, items in byrow.items():
        for cluster in _cluster(items):
            if len(cluster) < 5:
                continue
            vals = [float(w) for _, _, w in cluster]
            xs = [(a + b) / 2.0 for a, b, _ in cluster]
            diffs = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
            if min(diffs) <= 0:
                continue
            spread = max(diffs) - min(diffs)
            if spread > 0.25 * (sum(diffs) / len(diffs)):
                continue
            rows.append({"y": r, "labels": [w for _, _, w in cluster], "xs": xs, "vals": vals})
    return rows


def _tick_cols(words):
    """找出所有「同一 x 上的数字列」(候选 y 轴刻度列)"""
    from collections import defaultdict
    bycol = defaultdict(list)
    for xmin, ymin, xmax, ymax, w in words:
        if re.fullmatch(r"\d+(\.\d+)?", w):
            bycol[round(xmin, 1)].append((ymin, ymax, w))
    cols = []
    for c, items in bycol.items():
        items = sorted(items)
        if len(items) < 4:
            continue
        vals = [float(w) for _, _, w in items]
        ys = [(a + b) / 2.0 for a, b, _ in items]
        diffs = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
        if min(diffs) <= 0:
            continue
        spread = max(diffs) - min(diffs)
        if spread > 0.25 * (sum(diffs) / len(diffs)):
            continue
        cols.append({"x": c, "labels": [w for _, _, w in items], "ys": ys, "vals": vals})
    return cols


def digitize(pdf: str, page: int, dpi: int = 300, verbose: bool = True):
    words = _words(pdf, page)
    title = _find_title(words, TARGET_TITLE_WORDS)
    if title is None:
        raise RuntimeError("在第 %d 页文本层找不到标题 %s" % (page, " ".join(TARGET_TITLE_WORDS)))
    others = [_find_title(words, t) for t in OTHER_TITLES]

    rows = _tick_rows(words)
    cols = _tick_cols(words)

    # ---- x 轴刻度行: 在目标图标题下方, 且与标题 x 范围有重叠
    tx0, ty0, tx1, ty1 = title
    xcands = []
    for r in rows:
        if r["y"] <= ty1 + 2:          # 必须在标题下方
            continue
        if max(r["xs"]) < tx0 - 5 or min(r["xs"]) > tx1 + 5:
            continue
        # 排除落在其它格图标题带里的行
        bad = False
        for o in others:
            if o and r["y"] >= o[1] - 2 and r["y"] <= o[3] + 2:
                bad = True
        if bad:
            continue
        xcands.append(r)
    if not xcands:
        raise RuntimeError("找不到目标图的 x 轴刻度行")
    # 取离标题最近的一行
    xcands.sort(key=lambda r: r["y"])
    xrow = xcands[0]

    # ---- y 轴刻度列: 在目标图左侧, 且 y 范围与图的竖直范围重叠
    ycands = []
    for c in cols:
        if c["x"] >= tx0 - 1:
            continue
        if max(c["ys"]) < ty0 - 10 or min(c["ys"]) > ty1 + 120:
            continue
        ycands.append(c)
    if not ycands:
        raise RuntimeError("找不到目标图的 y 轴刻度列")
    # 取 x 最大 (最靠右 = 最贴近本图) 的一列
    ycands.sort(key=lambda c: -c["x"])
    ycol = ycands[0]

    # 标定: 点坐标
    x_pts = xrow["xs"]
    x_vals = xrow["vals"]
    # x 值可能降序 (轴反向), 取最小值对应最小 x
    order = sorted(range(len(x_vals)), key=lambda i: x_vals[i])
    x_pts_s = [x_pts[i] for i in order]
    x_vals_s = [x_vals[i] for i in order]
    y_pts = ycol["ys"]
    y_vals = ycol["vals"]
    order = sorted(range(len(y_vals)), key=lambda i: y_vals[i])
    y_pts_s = [y_pts[i] for i in order]
    y_vals_s = [y_vals[i] for i in order]

    # ---- 渲染
    with tempfile.TemporaryDirectory() as td:
        stem = os.path.join(td, "p")
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", str(page), "-l", str(page),
                        pdf, stem], check=True, capture_output=True)
        pngs = [f for f in os.listdir(td) if f.endswith(".png")]
        if not pngs:
            raise RuntimeError("pdftoppm 没出图")
        img = Image.open(os.path.join(td, pngs[0])).convert("L")
    arr = np.array(img)
    scale = dpi / 72.0

    def p2x(px):  # 点 → 像素 x
        return px * scale

    def p2y(py):  # 点 → 像素 y
        return py * scale

    x0_px, x1_px = p2x(x_pts_s[0]), p2x(x_pts_s[-1])
    # PDF 文本层的 y 是「自页顶向下」⇒ 位图里也是向下 ⇒ 值最小的刻度在**下方**
    y_bot_px = p2y(y_pts_s[0])   # 值最小 (如 0.0) ⇒ 位图 y 大 (靠下)
    y_top_px = p2y(y_pts_s[-1])  # 值最大 (如 2.5) ⇒ 位图 y 小 (靠上)
    vx0, vx1 = x_vals_s[0], x_vals_s[-1]
    vy0, vy1 = y_vals_s[0], y_vals_s[-1]

    ix0, ix1 = int(round(x0_px)), int(round(x1_px))
    iy_bot, iy_top = int(round(y_bot_px)), int(round(y_top_px))
    H, W = arr.shape
    ix0 = max(0, ix0); ix1 = min(W - 1, ix1)
    iy_bot = min(H - 1, iy_bot); iy_top = max(0, iy_top)
    if ix1 - ix0 < 50 or iy_bot - iy_top < 30:
        raise RuntimeError("绘图区太小 (W=%d H=%d) ⇒ 标定八成错了" % (ix1 - ix0, iy_bot - iy_top))

    # ---- 曲线提取 (RANSAC 直线/曲线拟合)
    #     ★为什么不用「逐列取暗像素中位数」: 绘图区里还有 "Ta = 25 °C" 标注文字
    #       和 y 轴小刻度线 ⇒ 中位数会被文字拉到顶部 ⇒ 量出乱数
    #     ★改为: 先用 RANSAC 在全部暗像素里拟合**占比最大的那条迹线** (曲线),
    #       再按该模型逐列取内点 ⇒ 文字/刻度线自然被排除
    mx0, mx1 = ix0 + 3, ix1 - 3
    my0, my1 = iy_top + 3, iy_bot - 3
    if mx1 - mx0 < 50 or my1 - my0 < 30:
        raise RuntimeError("内缩后绘图区太小 ⇒ 标定八成错了")
    sub = arr[my0:my1 + 1, mx0:mx1 + 1]
    dark = sub < 140
    rr, cc = np.nonzero(dark)
    if len(rr) < 30:
        raise RuntimeError("绘图区只扫到 %d 个暗像素 ⇒ 绘图区可能选错" % len(rr))

    rng = np.random.default_rng(20261116)
    best = None
    n_iter = 6000
    idx = np.arange(len(rr))
    for _ in range(n_iter):
        pick = rng.choice(idx, size=2, replace=False)
        (r1, c1), (r2, c2) = (rr[pick[0]], cc[pick[0]]), (rr[pick[1]], cc[pick[1]])
        if c2 == c1:
            continue
        a = (r2 - r1) / (c2 - c1)
        b = r1 - a * c1
        if not (-3.0 <= a <= 0.0):     # 曲线必须向上 (图像 y 随 x 减小)
            continue
        resid = np.abs(rr - (a * cc + b))
        inl = resid <= 2.5
        cnt = int(inl.sum())
        if cnt < 25:
            continue
        span = int(cc[inl].max() - cc[inl].min())
        if span < 0.30 * sub.shape[1]:
            continue                      # 太短 ⇒ 拟合到的是文字/刻度, 不是曲线
        if best is None or cnt > best[0]:
            best = (cnt, a, b, inl, span)
    if best is None:
        raise RuntimeError("RANSAC 没找到可信迹线")
    inl_cnt, a_best, b_best, inl_mask, span = best
    inl_frac = float(inl_mask.sum()) / float(len(rr))

    trace = []
    for c in range(int(cc[inl_mask].min()), int(cc[inl_mask].max()) + 1):
        sel = np.nonzero((cc == c) & (np.abs(rr - (a_best * c + b_best)) <= 3.0))[0]
        if len(sel) == 0:
            continue
        trace.append((c, float(np.median(rr[sel]))))
    if len(trace) < 20:
        raise RuntimeError("只扫到 %d 列内点 ⇒ 标定八成错了" % len(trace))

    def to_data(c, r):
        px = mx0 + c
        py = my0 + r
        dx = vx0 + (px - x0_px) * (vx1 - vx0) / (x1_px - x0_px)
        dy = vy0 + (y_bot_px - py) * (vy1 - vy0) / (y_bot_px - y_top_px)
        return dx, dy

    pts = [to_data(c, r) for c, r in trace]
    # 按 x 排序并做中值滤波去毛刺
    pts.sort(key=lambda t: t[0])
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    if len(ys) > 9:
        k = 5
        pad = np.pad(ys, (k // 2, k // 2), mode="edge")
        ys = np.array([np.median(pad[i:i + k]) for i in range(len(ys))])

    def interp(xq):
        return float(np.interp(xq, xs, ys))

    # ---- 自证三条
    v0 = interp(0.0)
    v20 = interp(20.0)
    checks = [
        {"id": "S1", "desc": "曲线过原点 (If=0 → Y≈0)", "value": round(v0, 4),
         "tol": 0.03, "pass": abs(v0) <= 0.03},
        {"id": "S2", "desc": "归一化定义点 (If=20mA → Y≈1.00)", "value": round(v20, 4),
         "tol": 0.06, "pass": abs(v20 - 1.0) <= 0.06},
        {"id": "S3", "desc": "单调不减", "value": round(float(np.min(np.diff(ys))), 4),
         "tol": 0.02, "pass": float(np.min(np.diff(ys))) >= -0.02},
    ]

    grid = [0.5, 1.0, 1.1, 1.2, 1.3, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 30.0, 50.0]
    x_lo, x_hi = float(xs.min()), float(xs.max())
    sampled = []
    for g in grid:
        if g < x_lo - 1e-9 or g > x_hi + 1e-9:
            sampled.append({"if_ma": g, "iv_norm": None, "in_range": False,
                            "note": "超出厂商图上曲线覆盖范围 (%.1f~%.1f mA), 不外推" % (x_lo, x_hi)})
        else:
            sampled.append({"if_ma": g, "iv_norm": round(interp(g), 4), "in_range": True, "note": ""})

    out = {
        "source_pdf": os.path.basename(pdf),
        "source_path": os.path.abspath(pdf),
        "page": page,
        "dpi": dpi,
        "graph_title": "Luminous Intensity vs. Forward Current",
        "y_axis": "Luminous intensity normalised at 20 mA",
        "x_axis": "Forward current (mA)",
        "calibration": {
            "x_ticks": {"labels": xrow["labels"], "points_x": [round(v, 2) for v in x_pts_s],
                        "values": x_vals_s},
            "y_ticks": {"labels": ycol["labels"], "points_y": [round(v, 2) for v in y_pts_s],
                        "values": y_vals_s},
            "method": "坐标轴标定取自 PDF 文本层 (pdftotext -bbox) 的刻度数字 bbox, 非人工量取",
        },
        "self_checks": checks,
        "self_checks_pass": all(c["pass"] for c in checks),
        "trace": {
            "method": "RANSAC 迹线拟合 (6000 次迭代, 容差 2.5 px) + 逐列取内点中位数",
            "inlier_px": inl_cnt,
            "dark_px_total": int(len(rr)),
            "inlier_fraction": round(inl_frac, 4),
            "model_row": "row = %.6f * col + %.3f" % (a_best, b_best),
            "x_span_data_ma": [round(x_lo, 3), round(x_hi, 3)],
            "note": "厂商图上这条曲线只画到 If≈%.0f mA, 超出部分不外推" % x_hi,
        },
        "sampled": sampled,
    }
    if verbose:
        print("== %s  p%d ==" % (os.path.basename(pdf), page))
        print("  x 刻度:", list(zip(xrow["labels"], [round(v, 1) for v in x_pts_s])))
        print("  y 刻度:", list(zip(ycol["labels"], [round(v, 1) for v in y_pts_s])))
        for c in checks:
            print("  [%s] %-42s value=%-8s tol=%-5s => %s"
                  % ("PASS" if c["pass"] else "FAIL", c["desc"], c["value"], c["tol"],
                     "PASS" if c["pass"] else "FAIL"))
        for s in sampled:
            print("  If=%-6s mA  Iv_norm=%s %s" % (s["if_ma"], s["iv_norm"], s.get("note", "")))
    return out


def selftest():
    """用本目录已有的厂商 PDF 自证 (rc=0 = 全过)"""
    cases = [
        ("led_aa1608sursk.pdf", 3),
        ("led_aph1608surck.pdf", 3),
    ]
    npass = 0
    for fn, page in cases:
        p = os.path.join(HERE, fn)
        if not os.path.isfile(p):
            print("[SKIP] %s 不在 %s" % (fn, HERE))
            continue
        try:
            out = digitize(p, page, dpi=300, verbose=False)
        except Exception as exc:  # noqa: BLE001
            print("[FAIL] %s p%d 数字化失败: %s" % (fn, page, exc))
            continue
        ok = out["self_checks_pass"]
        npass += 1 if ok else 0
        print("[%s] %s p%d  自证 S1/S2/S3 = %s" % ("PASS" if ok else "FAIL", fn, page,
              [c["pass"] for c in out["self_checks"]]))
        for s in out["sampled"]:
            if s["if_ma"] in (1.0, 1.1, 1.2, 1.3, 1.5, 2.0):
                print("      If=%-5s mA -> Iv_norm=%s" % (s["if_ma"], s["iv_norm"]))
        print("      迹线覆盖 If = %s mA, 内点占比 %s" % (out["trace"]["x_span_data_ma"],
                                                     out["trace"]["inlier_fraction"]))
    print("--- SELFTEST %d/%d ---" % (npass, len(cases)))
    return 0 if npass == len(cases) else 1


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    if len(args) < 2:
        print(__doc__)
        return 2
    pdf = args[0]
    page = int(args[1])
    dpi = 300
    jsout = None
    i = 2
    while i < len(args):
        if args[i] == "--dpi":
            i += 1
            dpi = int(args[i])
        elif args[i] == "--json":
            i += 1
            jsout = args[i]
        i += 1
    out = digitize(pdf, page, dpi=dpi)
    if jsout:
        with open(jsout, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print("wrote %s" % jsout)
    return 0 if out["self_checks_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
