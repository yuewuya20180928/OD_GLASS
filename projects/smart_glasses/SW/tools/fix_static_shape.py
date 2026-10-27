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
    # 2) shape inference: **fixed_input_shape = 真实输入 shape** → 从输入往前推
    #    (不传 fixed_input_shape 的话, 后处理里 90 个 NMS 的动态维度推不出来)
    try:
        m = shape_inference.infer_shapes(
            m, strict_mode=False, data_prop=True,
            fixed_input_shape={vi.name: dims})
    except Exception as e:  # noqa: BLE001
        print(f"[fix] ⚠️ shape_inference 部分失败 (不影响后续): {e}")
    # 3) 兜底: 只把**仍然**是动态且不在输出上的 dim_param 换成 1
    #    ⚠️ 输出维度绝不硬改成 1 —— 那样会得到"形状撒谎"的模型 (板端必错)
    n_fixed = 0
    out_names = {vo.name for vo in m.graph.output}
    for vi in list(m.graph.input) + list(m.graph.value_info):
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
