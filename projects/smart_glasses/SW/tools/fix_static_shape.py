#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-101 工具: 把 tf2onnx 产出的动态 shape ONNX 固化成静态 shape。

为什么需要: NPU 编译器 (ACUITY / Art.Galaxy) 要求**静态 shape** 输入,
tf2onnx 从 TF SavedModel 转出来的是 [1,'unk__5514','unk__5515',3] 动态 → 编译器直接拒收。
做法: 固定输入 → onnx shape inference → 把所有能推出来的 dim_param 换成 dim_value。

用法: python3 fix_static_shape.py in.onnx out.onnx 1 320 320 3
"""
import sys
import numpy as np
import onnx
from onnx import shape_inference


def main() -> int:
    src, dst = sys.argv[1], sys.argv[2]
    dims = [int(x) for x in sys.argv[3:]]
    m = onnx.load(src)
    # 1) 固定输入 shape
    vi = m.graph.input[0]
    for d, val in zip(vi.type.tensor_type.shape.dim, dims):
        d.ClearField("dim_param")
        d.dim_value = val
    # 2) shape inference (fixed_input_shape / strict_mode 关, 尽量多推)
    try:
        m = shape_inference.infer_shapes(
            m, strict_mode=False, data_prop=True)
    except Exception as e:  # noqa: BLE001
        print(f"[fix] ⚠️ shape_inference 部分失败 (不影响后续): {e}")
    # 3) 把所有能推出来的 dim_param 换成 dim_value
    #    (onnx shape_inference 会把已知维度写成 dim_value; 这里兜底再扫一遍)
    n_fixed = 0
    for vi in list(m.graph.input) + list(m.graph.output) + list(m.graph.value_info):
        shape = vi.type.tensor_type.shape
        if shape is None:
            continue
        for d in shape.dim:
            if d.HasField("dim_param") and d.dim_param.startswith("unk__"):
                d.ClearField("dim_param")
                d.dim_value = 1
                n_fixed += 1
    onnx.checker.check_model(m)
    onnx.save(m, dst)
    print(f"[fix] ✅ 写入 {dst} · 兜底固化 dim {n_fixed} 个")
    for vi in m.graph.input:
        print("[fix] input:", vi.name,
              [d.dim_value or d.dim_param for d in vi.type.tensor_type.shape.dim])
    for vo in m.graph.output:
        print("[fix] output:", vo.name,
              [d.dim_value or d.dim_param for d in vo.type.tensor_type.shape.dim])
    return 0


if __name__ == "__main__":
    sys.exit(main())
