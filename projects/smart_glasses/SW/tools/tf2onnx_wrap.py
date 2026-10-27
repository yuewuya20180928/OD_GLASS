#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-101: tf2onnx 转换包装器 —— numpy 2.x 兼容垫片。
tf2onnx 1.16.1 的 tfonnx.py 用 np.cast (NumPy 2.0 已删除) → AttributeError。
这里在 import tf2onnx 之前补回 np.cast 别名, 不改 tf2onnx 源码。
"""
import sys
import numpy as np

if not hasattr(np, "cast"):
    np.cast = lambda arr, dtype: np.asarray(arr, dtype=dtype)  # noqa: E731

from tf2onnx.convert import main  # noqa: E402

sys.argv[0] = "tf2onnx.convert"
if __name__ == "__main__":
    main()
