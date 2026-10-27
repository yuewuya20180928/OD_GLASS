#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-101 工具: 把 OD 模型的 **NMS 后处理段从图里剪掉**, 只留 NPU 能跑的子图。

为什么必须剪 (ISS-101 实测, 不是猜的):
  TF OD API SSD-MobileNetV2-FPNLite 的 SavedModel → ONNX 后, **2465/3304 节点 (74.7%)**
  是 Postprocessor 段, 里面含 NonMaxSuppression(90) / TopK(2) / Range(2) / NonZero(1) /
  Pad(5) / Resize(1) / Greater(8) / Less(90) / Not(98) ...
  这类算子 **NPU 编译器 (ACUITY / VIPLite / Art.Galaxy) 一律不支持或支持极差**。
  → 转换器要么直接报错, 要么 fallback 到 CPU 跑 (→ NPU 加速归零)。

剪裁点: 保留 **raw_detection_boxes** (编码框) + **raw_detection_scores** (类别分),
  把 decode + NMS 移到板端 CPU —— 这与 Rockchip awnpu model zoo 的 YOLOX 做法完全同构
  (`onnx.utils.extract_model(..., ['798','824','850'])` = 只留 3 路 head, 后处理外置),
  也与 A733 上 yolov5 的 "3 路 head + CPU decode" 路线同构。

用法:
  python3 cut_postprocessor.py in.onnx out.onnx \
      --keep raw_detection_boxes raw_detection_scores [--input-name input_tensor]
"""
from __future__ import annotations

import argparse
import collections
import os
import sys

import onnx


def op_histogram(model: onnx.ModelProto) -> dict:
    return dict(collections.Counter(n.op_type for n in model.graph.node))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--keep", nargs="+", required=True,
                    help="要保留的输出名 (图输出 tensor 名)")
    ap.add_argument("--input-name", default=None,
                    help="裁剪后保留的输入名 (默认全部输入)")
    args = ap.parse_args()

    m = onnx.load(args.src)
    before = op_histogram(m)

    # 找到每个要保留的输出在图里的**真正生产者** (可能经 Identity 转发)
    prod = {}
    for n in m.graph.node:
        for o in n.output:
            prod[o] = n

    keep_nodes: list = []
    keep_tensors: set = set()
    queue: list = []
    for name in args.keep:
        vo = next((v for v in m.graph.output if v.name == name), None)
        if vo is None:
            print(f"❌ 图输出里没有 {name!r}; 可选: "
                  f"{[v.name for v in m.graph.output]}")
            return 2
        queue.append(name)

    # 反向可达性分析: 从保留输出回溯到输入
    seen_nodes: set = set()
    while queue:
        tname = queue.pop()
        if tname in keep_tensors:
            continue
        keep_tensors.add(tname)
        n = prod.get(tname)
        if n is None:
            continue
        if id(n) in seen_nodes:
            continue
        seen_nodes.add(id(n))
        keep_nodes.append(n)
        queue.extend(n.input)

    # 重建图: 只保留可达节点; 只保留指定输出; 删掉不可达 initializer
    g = m.graph
    old_nodes = list(g.node)
    g.ClearField("node")
    for n in old_nodes:
        if id(n) in seen_nodes:
            g.node.append(n)

    old_outputs = list(g.output)
    g.ClearField("output")
    for vo in old_outputs:
        if vo.name in args.keep:
            g.output.append(vo)

    used = set(keep_tensors)
    for n in g.node:
        used.update(n.input)
    old_inits = list(g.initializer)
    g.ClearField("initializer")
    dropped = 0
    for init in old_inits:
        if init.name in used:
            g.initializer.append(init)
        else:
            dropped += 1
    # 保留 value_info 里仍被引用的部分 (剪干净, 免得 checker 报 dangling)
    old_vi = list(g.value_info)
    g.ClearField("value_info")
    for vi in old_vi:
        if vi.name in used:
            g.value_info.append(vi)

    onnx.checker.check_model(m)
    onnx.save(m, args.dst)

    after = op_histogram(m)
    print(f"[cut] ✅ {args.dst}  ({os.path.getsize(args.dst)} B)")
    print(f"[cut] 节点 {len(before)} → {len(after)} 个算子实例 "
          f"({len(before)} → {len(after)} 类算子)")
    print(f"[cut] 丢弃 initializer {dropped} 个")
    print(f"[cut] 输出: {[v.name for v in g.output]}")
    risky = {"NonMaxSuppression", "TopK", "Range", "NonZero", "Expand",
             "Pad", "Resize", "Greater", "Less", "Equal", "GreaterOrEqual",
             "Clip", "Min", "Max", "Not", "Shape", "Cast"}
    left = {k: v for k, v in after.items() if k in risky}
    print(f"[cut] 剩余高风险算子: {left if left else '无'}")
    print("[cut] 剩余算子表:",
          dict(sorted(after.items(), key=lambda kv: -kv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
