#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-101 工具: OD 模型实测精度评测 (自写逐类 IoU 贪心匹配)。

为什么不用 pycocotools 的 COCOeval:
  ★ 本机 pycocotools 的 evaluate() 要求 COCO json 格式的 detection 结果,
    而 TF OD API 的输出 (detection_boxes/detection_scores/detection_classes)
    需要自己转成 [image_id, category_id, bbox, score] 再喂进去 —— 可以做,
    但本单先要的是**一个能当场复现的绝对基线**, 自写匹配器更直白。
  ⚠️ **口径声明**: 本脚本输出的是 P/R/F1 (逐类 IoU 匹配后全类汇总),
    **不是官方 mAP**, 不可与论文里的 mAP@0.5 直接比较。
    只用于**同一口径下的门限自比** (量产放行门 G3 的 F1 ≥ 0.30)。

★★★ 坐标约定 (本单踩过的坑, 必读):
  TF OD API 的 `detection_boxes` 是**归一化**的 [ymin, xmin, ymax, xmax],
  且坐标系是**原图**尺寸, 不是 resize 后的尺寸!
  → 必须乘 **原图宽高** 还原, 乘 resize 尺寸会得到完全错误的分数
     (实测: 乘 320 → P=0.0176; 乘原图宽高 → P=0.4521)。

用法:
  python3 eval_od_accuracy.py --model <path.onnx> [--images 300] [--score-thr 0.3] [--iou 0.5]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict

COCO_ROOT = "/work/object_detection/data/coco/raw"
VAL_DIR = os.path.join(COCO_ROOT, "val2017")
ANN = os.path.join(COCO_ROOT, "annotations", "instances_val2017.json")


def iou_xyxy(b1, b2) -> float:
    ix = max(0.0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
    iy = max(0.0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
    inter = ix * iy
    ua = ((b1[2] - b1[0]) * (b1[3] - b1[1])
          + (b2[2] - b2[0]) * (b2[3] - b2[1]) - inter)
    return inter / ua if ua > 0 else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--images", type=int, default=300, help="取 val2017 前 N 张")
    ap.add_argument("--score-thr", type=float, default=0.3)
    ap.add_argument("--iou", type=float, default=0.5)
    ap.add_argument("--per-class", action="store_true")
    args = ap.parse_args()

    try:
        import numpy as np
        import onnxruntime as ort
        from PIL import Image
    except Exception as e:  # noqa: BLE001
        print(f"❌ 依赖缺失: {e}")
        return 2

    if not os.path.exists(ANN):
        print(f"❌ COCO 标注不在: {ANN}")
        return 2

    so = ort.SessionOptions()
    so.log_severity_level = 3
    sess = ort.InferenceSession(args.model, so, providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    nm = inp.name
    dt = {"tensor(uint8)": np.uint8, "tensor(float)": np.float32}.get(inp.type, np.float32)
    want = 320
    try:
        want = int(inp.shape[1]) if isinstance(inp.shape[1], int) else 320
    except Exception:  # noqa: BLE001
        pass

    ann = json.load(open(ANN, encoding="utf-8"))
    cats = {c["id"]: c["name"] for c in ann["categories"]}
    gt = defaultdict(list)
    for a in ann["annotations"]:
        x, y, w, h = a["bbox"]
        gt[a["image_id"]].append((a["category_id"], x, y, w, h))

    files = sorted(os.listdir(VAL_DIR))[: args.images]
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    n_img = 0
    t0 = time.time()
    for fnm in files:
        iid = int(fnm.split(".")[0])
        g = gt.get(iid)
        if not g:
            continue
        n_img += 1
        im = Image.open(os.path.join(VAL_DIR, fnm)).convert("RGB")
        W, H = im.size
        arr = np.array(im.resize((want, want)))
        if dt is np.uint8:
            arr = arr.astype(np.uint8)
        else:
            arr = arr.astype(dt)
        out = sess.run(["detection_boxes", "detection_scores",
                        "detection_classes", "num_detections"], {nm: arr[None]})
        b, sc, cl, n = out
        n = int(n[0])
        used = set()
        for i in range(n):
            if sc[0][i] < args.score_thr:
                break
            y1, x1, y2, x2 = b[0][i]
            # ★★★ 归一化 → 原图坐标 (乘原图宽高, 不是 resize 尺寸)
            cb = (x1 * W, y1 * H, x2 * W, y2 * H)
            c = int(cl[0][i]) - 1
            best, bi = -1.0, -1
            for j, (gc, gx, gy, gw, gh) in enumerate(g):
                if gc - 1 != c or j in used:
                    continue
                v = iou_xyxy(cb, (gx, gy, gx + gw, gy + gh))
                if v > best:
                    best, bi = v, j
            if best >= args.iou:
                used.add(bi)
                tp[c] += 1
            else:
                fp[c] += 1
        for j, (gc, *_rest) in enumerate(g):
            if j not in used:
                fn[gc - 1] += 1

    A = sum(tp.values())
    B = sum(fp.values())
    C = sum(fn.values())
    P = A / max(1, A + B)
    R = A / max(1, A + C)
    F1 = 2 * A / max(1, 2 * A + B + C)
    print(f"模型      : {args.model}")
    print(f"输入 dtype: {inp.type}  shape: {inp.shape}")
    print(f"评测图数  : {n_img} 张 (val2017 前 {args.images} 张中有标注的), "
          f"耗时 {time.time() - t0:.1f}s")
    print(f"口径      : 逐类 IoU={args.iou} 贪心匹配, score≥{args.score_thr} "
          f"(★ 非官方 mAP)")
    print(f"TP={A} FP={B} FN={C}")
    print(f"Precision={P:.4f}  Recall={R:.4f}  F1={F1:.4f}")
    if args.per_class:
        print("  类别            TP    FP    FN     P      R")
        for c in sorted(set(list(tp) + list(fp) + list(fn))):
            pp = tp[c] / max(1, tp[c] + fp[c])
            rr = tp[c] / max(1, tp[c] + fn[c])
            print(f"  {cats.get(c + 1, c + 1):14s} {tp[c]:4d} {fp[c]:5d} "
                  f"{fn[c]:5d}  {pp:.3f}  {rr:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
