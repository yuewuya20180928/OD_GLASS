#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARS45 · RKNN 转换链实测 + RK3576 端到端 ≤60ms 判定 (sw-lead, 2026-10-29)
=================================================================================
为什么有这个脚本
----------------
老板 10-28 19:05 拍板: 酷芯微 ARS45 资料拿不到 ⇒ 切"资料充足"的备选芯片。
选型报告 (HW/SOC_BACKUP_TOP5.md) 结论 RK3576 是唯一"算力+资料"双达标候选,
但 **端到端 ≤60ms 在 RK3576 上没有任何厂商公开实测值** ⇒ 只能靠实测。

本脚本做两件事:
  ① RKNN 转换链: YOLOv5 INT8 → RKNN (target=rk3576) → 转换成败 / 产物大小 /
     仿真推理耗时 / COCO val2017 F1
  ② 把 ① 的 NPU 耗时代入 **口径 A (曝光→出光, 老板 10-25 拍板锁死)** 延迟模型,
     重算端到端, 回答 "RK3576 能否满足 ≤60ms"

★ 沿用 2026-10-28 已做过的同类方法 (不重写):
  cut_postprocessor.py / fix_static_shape.py / eval_od_accuracy.py (逐类 IoU 贪心匹配口径)

★ 证据分级 (硬规矩, 不许混):
  [实测]        = 本脚本在本机跑出来的
  [推算·仿真]   = RKNN PC 仿真器 (simulator) 跑出来的 —— ★ **不是板端 NPU 实测**
  [推算]        = 由上面两者推导
  [0数据]       = 拿不到

★★ **关于仿真器耗时的重大警告 (交卷必读)**:
   rknn-toolkit2 的 PC simulator 是 **用 x86 CPU 模拟 NPU 执行量化图**,
   它**不是 NPU 吞吐的代理**。本机实测: 同一模型 simulator 约 **440ms/帧**,
   而 RK3576 NPU 的公开第三方实测是 **十几 ms 量级** ⇒ **相差 ~30 倍**。
   ⇒ **绝对不许拿 simulator 的耗时当 "NPU 耗时" 填进延迟预算**。
   本脚本把它单独列为 `sim_latency_ms`，并在 e2e 计算里**默认不采用**,
   只在 `--use-sim-as-npu` 时才代入 (且强制标 [推算·仿真])。

用法
----
    # 全部跑一遍 (推荐, 一条命令复现全部数字)
    /home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py all

    # 单步
    ... rknn_bench.py probe      # 环境 / 模型 / 算子普查 / 板端在不在
    ... rknn_bench.py calib      # 生成校准集 (letterbox 640x640)
    ... rknn_bench.py convert    # ONNX -> RKNN INT8 (rk3576)
    ... rknn_bench.py sim        # 仿真推理: max_abs_diff + 耗时统计
    ... rknn_bench.py acc        # COCO val2017 F1 (同 10-28 口径)
    ... rknn_bench.py e2e        # 端到端重算 (口径 A)

    ... rknn_bench.py all --json # 机读输出

退出码: 0 = 本机可执行部分全过 | 1 = 有失败 | 2 = 用法错

★ 本脚本不联网、不外发、不写任何别人的目录; 产物默认写到 /tmp/rknn_bench。

★★ 步间依赖 (ISS-113, 2026-10-29 修)
------------------------------------
convert / sim / acc 三步都做 **INT8 量化**, rknn.build() 需要 calib 步生成的
`/tmp/rknn_bench/dataset.txt` (校准集清单)。旧代码这里是**裸 assert** ⇒ 干净机器
上直接跑 `acc` 会崩成 AssertionError (实测: RKNN 报 "Dataset file ... not found!")。
现在改成: **缺 dataset.txt 时自动先跑 calib** (--no-auto-calib 可关) ⇒
§7 里列的每条命令都能在干净机器上独立跑通; calib 本身跑不了时给**明确行动指引**,
不再抛裸 AssertionError。
★ `WORK=/tmp/rknn_bench` 在 /tmp ⇒ **会被系统清理** (重启/清缓存/tmpwatcher 都可能清)
  ⇒ 重跑 convert/sim/acc 时会**自动重新 calib** (多花 ~20s, 不影响结论数字)。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

# ----------------------------------------------------------------------------
# 0. ★ 环境自举: 必须在带 rknn-toolkit2 的 python 里跑
# ----------------------------------------------------------------------------
RKNN_PY = "/home/yuewuya/miniconda3/envs/rknn/bin/python"

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))

# ★★★ 已实测到的两个坑 (不修就跑不动) ——————————————————————————————
# 坑①: rknn-toolkit2 2.3.2 内部调用 onnx.mapping, 但 onnx/__init__.py 不自动
#       import 这个子模块 ⇒ "AttributeError: module 'onnx' has no attribute 'mapping'"
#       修法: import onnx.mapping  (一行)
# 坑②: simulator 不接受 load_rknn() 进来的模型
#       "RKNN model that loaded by 'load_rknn' not support inference on the simulator"
#       修法: 必须 load_onnx() + build() 在同一个 session 里, 再 init_runtime()
# ----------------------------------------------------------------------------


def _ensure_env() -> None:
    """如果当前解释器没有 rknn, 自动切到 rknn conda env 重跑一次。"""
    try:
        import rknn.api  # noqa: F401,PLC0415
        return
    except Exception:  # noqa: BLE001
        pass
    if os.path.exists(RKNN_PY) and os.path.realpath(RKNN_PY) != os.path.realpath(sys.executable):
        print(f"[env] 当前 python 无 rknn → 切到 {RKNN_PY} 重跑", file=sys.stderr)
        os.execv(RKNN_PY, [RKNN_PY, os.path.abspath(__file__), *sys.argv[1:]])
    print("❌ 本机找不到 rknn-toolkit2; 见报告 §2.1 安装说明")
    sys.exit(2)


_ensure_env()

import onnx  # noqa: E402
import onnx.mapping  # noqa: E402,F401  ★ 坑① 修复 (必须, 否则 load_onnx 报 AttributeError)
import numpy as np  # noqa: E402
from rknn.api import RKNN  # noqa: E402

# ----------------------------------------------------------------------------
# 1. 固定输入 (全部来自项目库, 不许在这里拍脑袋改)
# ----------------------------------------------------------------------------
# 主模型候选: SW/MODEL_ASSETS.md §1.2 台账 MOD-YOLOV5S-640-ARS45-SRC
#   —— 唯一实测可推理的 yolov5s ONNX (640), sha256[:16]=20368be665f6f59a
#   ⚠️ 许可 = AGPL-3.0 (SW/MODEL_LICENSE.md §1.2) ⇒ 商用阻断项 L4, 本单不解决
ONNX_MODEL = "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx"
ONNX_MODEL_SHA16 = "20368be665f6f59a"
CALIB_DIR = "/home/yuewuya/Public/radxa_yolo/calib_yolov5_100"   # 100 张 COCO val jpg
COCO_ROOT = "/work/object_detection/data/coco/raw"
VAL_DIR = os.path.join(COCO_ROOT, "val2017")
ANN = os.path.join(COCO_ROOT, "annotations", "instances_val2017.json")

TARGET_PLATFORM = "rk3576"
IMGSZ = 640
WORK = "/tmp/rknn_bench"

# 板端模型槽位上限 (SW/FLASH_AND_VERSION.md §4.1) —— RKNN 产物大小必须比这个
MODEL_SLOT_BYTES = 15_728_640

# ----------------------------------------------------------------------------
# 1b. ★★ 步间依赖自愈 (ISS-113, 2026-10-29, 项目总工登记 → sw-lead 修)
#
#     【根因】convert / sim / acc 三步都要做 INT8 量化, rknn.build(dataset=...)
#     需要 calib 步生成的 /tmp/rknn_bench/dataset.txt (校准集清单)。
#     旧代码在 _build_session_for_sim 里写的是**裸 assert** ⇒ 干净机器上直接跑
#     `acc` 会崩成 AssertionError, 拿不到任何精度数字 (项目总工 10-29 09:0x 亲跑撞到)。
#
#     【修法】(1) 缺 dataset.txt ⇒ **自动先跑 calib 步** (可用 --no-auto-calib 关)
#             (2) 原来的裸 assert 全部换成**带行动指引的显式报错**
#             (3) calib 源目录缺失 / dataset 引用的 png 被清掉 ⇒ 同样能自愈
#     ★ 不改任何结论数字, 只改依赖处理与报错路径。
# ----------------------------------------------------------------------------
DATASET_TXT = os.path.join(WORK, "dataset.txt")


class BenchError(RuntimeError):
    """可预期的、可给出行动指引的失败 (不是 bug) ⇒ main() 捕获后 rc=1 退出。"""


def _dataset_ok() -> bool:
    """dataset.txt 存在且**它引用的校准图片都还在**。

    /tmp 会被系统清理 ⇒ 可能出现 "dataset.txt 还在, 但引用的 png 没了" 的半残状态,
    那种状态一样要重做 calib (否则 rknn.build 会读到不存在的图)。
    """
    if not (os.path.isfile(DATASET_TXT) and os.path.getsize(DATASET_TXT) > 0):
        return False
    try:
        with open(DATASET_TXT, encoding="utf-8") as f:
            paths = [ln.strip() for ln in f if ln.strip()]
    except OSError:
        return False
    if not paths:
        return False
    return all(os.path.isfile(p) for p in paths)


def ensure_dataset(args, needer: str) -> dict:
    """保证量化校准集清单 dataset.txt 就位。缺 ⇒ 自动补跑 calib 步。

    返回 {"auto_calib": bool, "dataset_txt": str, "n_images": int, "note": str}
    """
    if _dataset_ok():
        try:
            with open(DATASET_TXT, encoding="utf-8") as f:
                n = sum(1 for ln in f if ln.strip())
        except OSError:
            n = 0
        return {"auto_calib": False, "dataset_txt": DATASET_TXT, "n_images": n,
                "note": "复用已有 dataset.txt"}

    if getattr(args, "no_auto_calib", False):
        raise BenchError(
            "缺少量化校准集清单: %s\n"
            "  依赖链: calib 步生成 dataset.txt → convert/sim/acc 三步的 INT8 量化 "
            "(rknn.build(dataset=...)) 需要它。\n"
            "  二选一:\n"
            "    1) 先跑 calib 步 (推荐, 之后 convert/sim/acc 都能独立跑):\n"
            "         cd %s && %s SW/tools/%s calib\n"
            "    2) 去掉 --no-auto-calib, 让本脚本自动补跑 calib。"
            % (DATASET_TXT, PROJ, sys.executable, os.path.basename(__file__)))

    # ★ 诊断信息走 stderr ⇒ --json 的 stdout 保持纯净可被机器解析
    print(f"[dep] ⚠ {DATASET_TXT} 不存在 (或引用的校准图已被 /tmp 清理) "
          f"⇒ 自动先跑 calib 步 (被 {needer} 步依赖)", file=sys.stderr)
    try:
        info = step_calib(args)
    except BenchError:
        raise
    except Exception as e:  # noqa: BLE001
        raise BenchError(
            "自动补跑 calib 步失败: %s: %s\n"
            "  → 请检查校准集源目录 %s 是否存在且含 jpg (当前 %d 张)。"
            % (type(e).__name__, e, CALIB_DIR,
               len(os.listdir(CALIB_DIR)) if os.path.isdir(CALIB_DIR) else 0))
    if not _dataset_ok():
        raise BenchError(
            "自动补跑 calib 步之后仍然没有可用的 %s\n"
            "  → 请检查 calib 步输出 (或手动跑: cd %s && %s SW/tools/%s calib)"
            % (DATASET_TXT, PROJ, sys.executable, os.path.basename(__file__)))
    return {"auto_calib": True, "dataset_txt": DATASET_TXT,
            "n_images": info.get("n_images", 0),
            "note": "★ 本次是自动补跑的 calib 步 (之前 dataset.txt 缺失)"}

# ----------------------------------------------------------------------------
# 2. 端到端延迟模型 —— 口径 A (曝光开始→光机出光), 老板 10-25 19:16 拍板锁死
#    来源: SW/SW_REQUIREMENTS.md §10.2 / SW/DISPLAY_MODE.md §1.3 / PROJECT_TRACKER §3.3
# ----------------------------------------------------------------------------
P60 = 16.67      # ms  sensor 帧周期 @60fps
E = 8.3          # ms  曝光积分
R = 8.3          # ms  读出
S3 = 8.0         # ms  ISP (含缩放)
S4 = 1.0         # ms  预处理 (letterbox + 布局转换 + 归一化)
S6 = 2.0         # ms  反量化 (A733 上占 SDK 总耗时 25% ⇒ 保守 2ms; RKNN 见报告说明)
S7 = 3.0         # ms  decode + NMS (CPU)
S8 = 1.0         # ms  画框
S9 = 3.0         # ms  显示 TX (DSI/DP→DSI 桥)
S10 = 5.0        # ms  光机逐帧延迟 ★ [0数据] (走鹃Ⅱ 未公开逐帧延迟; 目标值占位)

EXPOSURE_BLOCK = E + R + S3          # = 24.67ms  曝光→ISP输出 (口径 A 的物理块, 不可协商)
DISPLAY_TAIL = S8 + S9 + S10         # = 9ms    画框+TX+光机
T_OD_FIXED = S4 + S6 + S7            # = 6ms    T_od 里与 NPU 无关的部分

# ----------------------------------------------------------------------------
# 2b. 第三方公开实测锚点 (★ 本单无板 ⇒ 只能用外部实测当锚, 全部标 [公开实测·第三方])
#     来源: airockchip/rknn_model_zoo README 「Model performance benchmark(FPS)」表
#           (官方仓库; ★ 本机直连 raw.githubusercontent 超时未直读, 经搜索引擎快照读出 ⇒
#            见报告 §3.5 的证据分级说明)
#     口径: **整链路 FPS** (含 CPU 侧前后处理) ⇒ 可当作 **纯 NPU 耗时 S5 的上界**
#     一致性交叉验证: 同表 RK3588 yolov5s_relu = 66.1 FPS = 15.13ms,
#           与 PhotonVision 在 Orange Pi 5 (RK3588) 上实测的 YOLOv5
#           "Total Time" = 15034 ± 1734 µs (= 66.5 FPS) **吻合到 0.6%** ✔
# ----------------------------------------------------------------------------
THIRD_PARTY = [
    {"label": "RK3576 yolov5s (SiLU) 640 INT8 — model_zoo 57.5 FPS (保守, 同款结构)",
     "ms": 1000.0 / 57.5,
     "evidence": "[公开实测·第三方] airockchip/rknn_model_zoo 性能表 RK3576@single_core 57.5 FPS "
                 "⇒ 17.39 ms (整链路上界 ⇒ 纯 NPU ≤ 此值)"},
    {"label": "RK3576 yolov5s_relu 640 INT8 — model_zoo 65.0 FPS (乐观)",
     "ms": 1000.0 / 65.0,
     "evidence": "[公开实测·第三方] airockchip/rknn_model_zoo 性能表 RK3576@single_core 65.0 FPS "
                 "⇒ 15.38 ms (整链路上界; relu 变体, 比 SiLU 快)"},
    {"label": "RK3576 yolov5n 640 INT8 — model_zoo 112.7 FPS (降模型规模路线)",
     "ms": 1000.0 / 112.7,
     "evidence": "[公开实测·第三方] airockchip/rknn_model_zoo 性能表 RK3576@single_core 112.7 FPS "
                 "⇒ 8.87 ms (换模型 ⇒ 精度要另评)"},
]


def e2e_mode_a(t_od: float) -> float:
    """模式 A: 显示等 OD (age=0)。

    口径 A 端到端 = (曝光+读出+ISP) + T_od + (画框+TX+光机)
                  = 24.67 + T_od + 9
    (来源 SW/SW_REQUIREMENTS.md §10.2 / SW/DISPLAY_MODE.md §1.3)
    """
    return EXPOSURE_BLOCK + t_od + DISPLAY_TAIL


def e2e_mode_b(t_od: float, period: float = P60) -> tuple:
    """模式 B: 异步 (显示不等 OD)。age = ceil(T_od / period) —— 台阶函数。

    口径 A 端到端 = age*P + P + S3 + (画框+TX+光机) = (age+1)*16.67 + 17
    ★ 推导见 SW/SW_REQUIREMENTS.md §10.2 的时序图 (显示帧 M 的合成时刻 = 16.67M + 16.67 + S3)
    """
    age = int(np.ceil(t_od / period - 1e-9))
    age = max(age, 1)
    return age * period + period + S3 + DISPLAY_TAIL, age


def sha16(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()[:16]


# ----------------------------------------------------------------------------
# 3. YOLOv5 前后处理 (从 /home/yuewuya/Public/radxa_yolo/code/eval_tta_yolov5s_onnx.py
#    搬过来的成熟实现 —— A733 上已验证过, 不重写)
# ----------------------------------------------------------------------------
def letterbox(img: np.ndarray, new_size: int):
    h0, w0 = img.shape[:2]
    scale = min(new_size / h0, new_size / w0)
    new_h, new_w = int(h0 * scale), int(w0 * scale)
    import cv2  # noqa: PLC0415
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    pad_x = (new_size - new_w) // 2
    pad_y = (new_size - new_h) // 2
    canvas = np.zeros((new_size, new_size, 3), dtype=np.uint8)
    canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = img_resized
    return canvas, scale, pad_x, pad_y


def preprocess(img: np.ndarray, imgsz: int, div255: bool = True):
    """返回 (NCHW float32, scale, pad_x, pad_y)

    ★★★ 本单实测到的坑 (必读) ★★★
    本模型的输入是 **RGB, 值域 [0,1] (即 uint8/255)**, 不是 0-255!
    [实测] 证据: 用 0-255 喂进去 ⇒ COCO 图 139 的 top-100 检测 **maxIoU = 0.000** (全错);
                改成 RGB/255 ⇒ **maxIoU = 0.956, 85/100 个检测 IoU≥0.5** (对上了 GT 的 tv)。
    ⚠️ `/home/yuewuya/Public/radxa_yolo/code/eval_tta_yolov5s_onnx.py` 里写的
       "yolov5s-sim.onnx 期望 input 0-255" 是**错的** ⇒ 不许直接复用那个脚本。
    ⚠️ 同理 A733 板端 `yolov5_pre_process_bgr.cpp` 传的是 uint8 0-255 —— 那是给
       **A733 的 int8 量化模型**用的 (量化吸收了 scale), 与 FP32 ONNX 不是一回事。
    """
    canvas, scale, pad_x, pad_y = letterbox(img, imgsz)
    rgb = canvas[..., ::-1]
    blob = np.ascontiguousarray(rgb.transpose(2, 0, 1)).astype(np.float32)
    if div255:
        blob = blob / 255.0
    return np.expand_dims(blob, 0), scale, pad_x, pad_y


def unletterbox_boxes(boxes_xyxy, scale, pad_x, pad_y, orig_h, orig_w):
    b = boxes_xyxy.copy()
    b[:, [0, 2]] -= pad_x
    b[:, [1, 3]] -= pad_y
    b[:, [0, 2]] /= scale
    b[:, [1, 3]] /= scale
    b[:, [0, 2]] = np.clip(b[:, [0, 2]], 0, orig_w)
    b[:, [1, 3]] = np.clip(b[:, [1, 3]], 0, orig_h)
    return b


def xywh2xyxy(x: np.ndarray) -> np.ndarray:
    y = x.copy()
    y[:, 0] = x[:, 0] - x[:, 2] / 2
    y[:, 1] = x[:, 1] - x[:, 3] / 2
    y[:, 2] = x[:, 0] + x[:, 2] / 2
    y[:, 3] = x[:, 1] + x[:, 3] / 2
    return y


def nms(boxes: np.ndarray, scores: np.ndarray, iou_thr: float):
    if len(boxes) == 0:
        return []
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(int(i))
        if order.size == 1:
            break
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w * h
        iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-9)
        order = order[1:][iou < iou_thr]
    return keep


ANCHORS = {
    8:  np.array([[10, 13], [16, 30], [33, 23]]),
    16: np.array([[30, 61], [62, 45], [59, 119]]),
    32: np.array([[116, 90], [156, 198], [373, 326]]),
}


def decode_output_tensor(out, conf_thr, iou_thr, max_det,
                          scale, pad_x, pad_y, orig_h, orig_w):
    """从 **`output` 张量** (1, 25200, 85) 解码 → (boxes 原图 xyxy, scores, classes)

    ★★★ 本单实测到的坑 (必读) ★★★
      yolov5s-sim.onnx 的 3 路 head 输出 '350'/'498'/'646' 是 **pre-sigmoid 的原始 conv 输出**
      ⇒ 不能按 "head 已是 0-1 的 obj/cls + 像素 xywh" 来解 (10-28 那套假设是错的)。
      `output` 张量才是解码后的结果。但 ★ **INT8 量化会把 `output` 张量废掉**
      (像素坐标与 0-1 概率混在一个 int8 张量里 ⇒ 步长 5.57) ⇒ **板端必须用 head 自己解码**。
      ⇒ 用 `decode_raw_heads()` (见下)。
    """
    out = out[0]                                   # (25200, 85)
    obj = out[:, 4]
    cls = out[:, 5:85]
    score = obj * cls.max(1)
    mask = score > conf_thr
    if not mask.any():
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    xywh = out[mask, 0:4]
    scores = score[mask]
    classes = cls[mask].argmax(1).astype(int)
    boxes = unletterbox_boxes(xywh2xyxy(xywh), scale, pad_x, pad_y, orig_h, orig_w)
    fb, fs, fc = [], [], []
    for c in np.unique(classes):
        idx = np.where(classes == c)[0]
        keep = nms(boxes[idx], scores[idx], iou_thr)
        for k in idx[keep][:max_det]:
            fb.append(boxes[k])
            fs.append(scores[k])
            fc.append(c)
    if not fb:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    return np.array(fb), np.array(fs), np.array(fc, dtype=int)


# ----------------------------------------------------------------------------
# 3b. ★★★ raw head 解码 (板端真正要用的路径) —— [实测] 与 ONNX `output` 逐元素吻合
# ----------------------------------------------------------------------------
# 公式 (对 yolov5s-sim.onnx 的 3 路 head 350/498/646):
#     s0..s3 = sigmoid(raw[..., 0:4])          ← ★ 4 个 bbox 通道 **全部** 先过 sigmoid
#     cx = (s0*2 - 0.5 + gx) * stride
#     cy = (s1*2 - 0.5 + gy) * stride
#     w  = (s2*2)**2 * anchor_w
#     h  = (s3*2)**2 * anchor_h
#     obj = sigmoid(raw[...,4]);  cls = sigmoid(raw[...,5:85])
# [实测] 验证: 与 ONNX `output` 张量逐元素对比 ⇒ cx/cy max_abs_diff = 6.0e-05, w/h = 0
# [实测] grid/anchor 来自 ONNX initializer (按 shape 匹配, 不硬编码):
#        grid  (1,3,G,G,2) = [gx, gy]     anchor (1,3,G,G,2) = [anchor_w, anchor_h]
def load_grid_anchor(model_path: str):
    """从 ONNX initializer 里提取 3 个 stride 的 grid / anchor (按 shape 匹配, 不硬编码)"""
    from onnx import numpy_helper  # noqa: PLC0415
    m = onnx.load(model_path, load_external_data=False)
    init = {i.name: numpy_helper.to_array(i) for i in m.graph.initializer}
    out = {}
    for stride, g in ((8, 80), (16, 40), (32, 20)):
        cand = [(k, v) for k, v in init.items() if tuple(v.shape) == (1, 3, g, g, 2)]
        grid = None
        anch = None
        for k, v in cand:
            flat = v.reshape(-1)
            if float(flat[0]) == 0.0 and float(flat[1]) == 0.0:
                grid = v
            else:
                anch = v
        if grid is None or anch is None:
            raise RuntimeError(f"找不到 stride {stride} 的 grid/anchor initializer")
        out[stride] = {"grid": grid[0], "anchor": anch[0]}
    return out


def decode_raw_heads(h80, h40, h20, ga, conf_thr, iou_thr, max_det,
                     scale, pad_x, pad_y, orig_h, orig_w):
    """3 路 raw head (pre-sigmoid) → (boxes 原图 xyxy, scores, classes)"""
    all_b, all_s, all_c = [], [], []
    for stride, head in ((8, h80), (16, h40), (32, h20)):
        if head is None:
            continue
        head = head[0]                                  # (3, G, G, 85)
        grid = ga[stride]["grid"]                       # (3,G,G,2) = [gx, gy]
        anch = ga[stride]["anchor"]                     # (3,G,G,2) = [aw, ah]
        for a in range(head.shape[0]):
            r = head[a]
            s = 1.0 / (1.0 + np.exp(-r[..., 0:4]))
            cx = (s[..., 0] * 2 - 0.5 + grid[a, ..., 0]) * stride
            cy = (s[..., 1] * 2 - 0.5 + grid[a, ..., 1]) * stride
            bw = (s[..., 2] * 2) ** 2 * anch[a, ..., 0]
            bh = (s[..., 3] * 2) ** 2 * anch[a, ..., 1]
            obj = 1.0 / (1.0 + np.exp(-r[..., 4]))
            cls = 1.0 / (1.0 + np.exp(-r[..., 5:]))       # (G, G, 80)
            score = obj * cls.max(-1)                    # ★ 轴: 类别维是最后一维 ⇒ 用 -1
            mask = score > conf_thr
            if not mask.any():
                continue
            xywh = np.stack([cx, cy, bw, bh], -1)[mask]
            all_b.append(xywh2xyxy(xywh))
            all_s.append(score[mask])
            all_c.append(cls[mask].argmax(1))
    if not all_b:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    boxes = unletterbox_boxes(np.concatenate(all_b), scale, pad_x, pad_y, orig_h, orig_w)
    scores = np.concatenate(all_s)
    classes = np.concatenate(all_c).astype(int)
    fb, fs, fc = [], [], []
    for c in np.unique(classes):
        idx = np.where(classes == c)[0]
        keep = nms(boxes[idx], scores[idx], iou_thr)
        for k in idx[keep][:max_det]:
            fb.append(boxes[k])
            fs.append(scores[k])
            fc.append(c)
    if not fb:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    return np.array(fb), np.array(fs), np.array(fc, dtype=int)


# ----------------------------------------------------------------------------
# 4. 评测口径 —— 与 SW/tools/eval_od_accuracy.py 严格同口径 (逐类 IoU 贪心匹配)
# ----------------------------------------------------------------------------
def iou_xyxy(b1, b2) -> float:
    ix = max(0.0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
    iy = max(0.0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
    inter = ix * iy
    ua = ((b1[2] - b1[0]) * (b1[3] - b1[1])
          + (b2[2] - b2[0]) * (b2[3] - b2[1]) - inter)
    return inter / ua if ua > 0 else 0.0


def score_predictions(pred_by_img: dict, n_img: int, iou_thr: float) -> dict:
    """pred_by_img[iid] = (boxes xyxy 原图坐标, scores, classes)  →  P/R/F1"""
    ann = json.load(open(ANN, encoding="utf-8"))
    gt = collections.defaultdict(list)
    for a in ann["annotations"]:
        x, y, w, h = a["bbox"]
        gt[a["image_id"]].append((a["category_id"], x, y, w, h))
    tp = collections.defaultdict(int)
    fp = collections.defaultdict(int)
    fn = collections.defaultdict(int)
    for iid, (boxes, scores, classes) in pred_by_img.items():
        g = gt.get(iid, [])
        used = set()
        for k in range(len(scores)):
            c = int(classes[k])
            best, bi = -1.0, -1
            for j, (gc, gx, gy, gw, gh) in enumerate(g):
                if gc - 1 != c or j in used:
                    continue
                v = iou_xyxy(boxes[k], (gx, gy, gx + gw, gy + gh))
                if v > best:
                    best, bi = v, j
            if best >= iou_thr:
                used.add(bi)
                tp[c] += 1
            else:
                fp[c] += 1
        for j, (gc, *_r) in enumerate(g):
            if j not in used:
                fn[gc - 1] += 1
    A = sum(tp.values())
    B = sum(fp.values())
    C = sum(fn.values())
    P = A / max(1, A + B)
    R = A / max(1, A + C)
    F1 = 2 * A / max(1, 2 * A + B + C)
    return {"tp": A, "fp": B, "fn": C, "precision": P, "recall": R, "f1": F1,
            "n_images": n_img, "iou_thr": iou_thr}


# ----------------------------------------------------------------------------
# 5. 各步骤
# ----------------------------------------------------------------------------
def step_probe(args) -> dict:
    """环境 / 板端在不在 / 模型台账核对 / 算子普查"""
    import subprocess as sp  # noqa: PLC0415
    st = {}
    st["rknn_toolkit2_version"] = _rknn_version()
    st["python"] = sys.version.split()[0]
    st["onnx_version"] = onnx.__version__
    st["numpy_version"] = np.__version__
    # 板端探测: 有没有 RK 设备 / adb 设备
    devs = []
    try:
        r = sp.run(["adb", "devices"], capture_output=True, text=True, timeout=15)
        devs = [ln for ln in r.stdout.splitlines()[1:] if ln.strip()]
    except Exception:  # noqa: BLE001
        pass
    st["adb_devices"] = devs
    st["rk3576_board_present"] = bool(devs)
    st["board_measured"] = False
    st["board_note"] = ("本机无 RK3576 板 ⇒ **板端 NPU 耗时未实测**; "
                         "本单只出 PC 侧转换 + 仿真 + 精度")
    # 模型台账核对
    m = onnx.load(ONNX_MODEL, load_external_data=False)

    def sh(v):
        return [d.dim_value or d.dim_param for d in v.type.tensor_type.shape.dim]
    st["model_path"] = ONNX_MODEL
    st["model_sha16"] = sha16(ONNX_MODEL)
    st["model_sha16_matches_ledger"] = (st["model_sha16"] == ONNX_MODEL_SHA16)
    st["model_inputs"] = [(i.name, sh(i)) for i in m.graph.input]
    st["model_outputs"] = [(o.name, sh(o)) for o in m.graph.output]
    st["model_nodes"] = len(m.graph.node)
    census = collections.Counter(n.op_type for n in m.graph.node)
    st["op_census"] = dict(sorted(census.items(), key=lambda kv: -kv[1]))
    # RKNN 支持清单 (toolkit2 2.3.2 内置的 supported_op.md 不在包里 ⇒ 用官方文档口径)
    st["npu_risky_ops_present"] = {
        op: census.get(op, 0) for op in
        ("NonMaxSuppression", "TopK", "Range", "NonZero", "Einsum", "Gather")
        if census.get(op, 0) > 0
    }
    st["npu_risky_ops_note"] = (
        "本模型 (yolov5 RT 抽取版) 已不含 NMS/TopK/Range ⇒ **不需要 cut_postprocessor.py**; "
        "cut 脚本在 RKNN 侧仍然保留给 '带内嵌 NMS 的导出模型' 用")
    st["license"] = "AGPL-3.0 (SW/MODEL_LICENSE.md §1.2) ⇒ 商用阻断项 L4, 本单不解决"
    return st


def _rknn_version() -> str:
    try:
        p = os.path.join(os.path.dirname(onnx.__file__), "..", "rknn", "VERSION")
        return open(p, encoding="utf-8").read().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def step_calib(args) -> dict:
    """生成 letterbox 640x640 的校准集 + dataset.txt"""
    import cv2  # noqa: PLC0415
    if not os.path.isdir(CALIB_DIR):
        raise BenchError(
            "校准集源目录不存在: %s\n"
            "  → calib 步需要 100 张 COCO val jpg 作量化校准集; 请先备齐该目录。"
            % CALIB_DIR)
    outdir = os.path.join(WORK, "calib")
    os.makedirs(outdir, exist_ok=True)
    files = sorted(f for f in os.listdir(CALIB_DIR) if f.lower().endswith(".jpg"))
    if not files:
        raise BenchError(
            "校准集源目录里没有 jpg: %s\n"
            "  → calib 步无从生成 dataset.txt ⇒ convert/sim/acc 三步都会失败。"
            % CALIB_DIR)
    lines = []
    for fn in files:
        img = cv2.imread(os.path.join(CALIB_DIR, fn))   # BGR
        if img is None:
            continue
        canvas, _s, _px, _py = letterbox(img, IMGSZ)    # BGR canvas
        dst = os.path.join(outdir, os.path.splitext(fn)[0] + ".png")
        # cv2.imwrite 期望 BGR ⇒ 直接写 BGR canvas; imread 回来还是 BGR
        cv2.imwrite(dst, canvas)
        lines.append(dst)
    if not lines:
        raise BenchError(
            "校准集源目录里的 jpg 全部读不出来 (损坏?): %s" % CALIB_DIR)
    ds = os.path.join(WORK, "dataset.txt")
    with open(ds, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return {"calib_dir": outdir, "dataset_txt": ds, "n_images": len(lines),
            "source": CALIB_DIR, "letterbox": f"{IMGSZ}x{IMGSZ} 黑边(0) 同推理口径"}


def _new_rknn(cfg_std=255):
    r = RKNN(verbose=False)
    kw = {}
    if cfg_std and cfg_std != 1:
        kw = dict(mean_values=[[0, 0, 0]], std_values=[[cfg_std] * 3])
    r.config(target_platform=TARGET_PLATFORM,
             quantized_dtype="w8a8",
             quantized_algorithm="normal",
             quantized_method="channel",
             optimization_level=3, **kw)
    return r


def step_cut(args) -> dict:
    """★ 用 SW/tools/cut_postprocessor.py 把后处理从图里剪掉 (只留 3 路 raw head)

    ★★ 为什么必须切 (本单实测的核心发现, 见报告 §3.2.4 坑 3):
       未切版本的第 0 个输出 `output` (1,25200,85) 把**像素尺度坐标**(范围 -6.8..706.9)
       与 **0~1 的概率**混在**同一个 int8 张量**里 ⇒ 量化步长 = 706.9/127 ≈ 5.57
       ⇒ 概率被量化成 0 / ±5.57 ⇒ **INT8 模型一个检测都出不来** (实测 F1 = 0)。
       切掉之后只剩 3 路 raw head (值域约 -41..+11 ⇒ int8 步长 0.16) ⇒ 精度可保。
    """
    src = ONNX_MODEL
    dst = os.path.join(WORK, "yolov5s_heads.onnx")
    os.makedirs(WORK, exist_ok=True)
    r = subprocess.run([sys.executable,
                        os.path.join(HERE, "cut_postprocessor.py"), src, dst,
                        "--keep", "350", "498", "646"],
                       capture_output=True, text=True)
    return {
        "ok": r.returncode == 0,
        "src": src, "dst": dst,
        "tool": "SW/tools/cut_postprocessor.py (复用 10-28 那套)",
        "stdout": r.stdout[-1500:],
        "stderr": r.stderr[-800:],
        "sha16": sha16(dst) if os.path.exists(dst) else None,
        "bytes": os.path.getsize(dst) if os.path.exists(dst) else None,
    }


def step_convert(args) -> dict:
    """ONNX -> RKNN INT8 (rk3576)。默认转 **切完 head 的版本** (板端真正能用的那个)"""
    os.makedirs(WORK, exist_ok=True)
    # ★ ISS-113: INT8 量化需要 calib 步生成的 dataset.txt ⇒ 缺则自动补跑 calib
    dep = ensure_dataset(args, "convert")
    src = ONNX_MODEL
    tag = "full"
    if not args.no_cut:
        cut = step_cut(args)
        if cut.get("ok"):
            src = cut["dst"]
            tag = "heads"
    t0 = time.time()
    r = _new_rknn(cfg_std=args.cfg_std)
    rc_load = r.load_onnx(src)
    if rc_load != 0:
        return {"ok": False, "stage": "load_onnx", "rc": rc_load, "dep": dep}
    t_load = time.time() - t0
    t0 = time.time()
    rc_build = r.build(do_quantization=True, dataset=DATASET_TXT)
    t_build = time.time() - t0
    if rc_build != 0:
        return {"ok": False, "stage": "build", "rc": rc_build,
                "load_s": t_load, "build_s": t_build, "dep": dep,
                "error": "rknn.build(INT8) 失败 rc=%s; 校准集清单=%s"
                         % (rc_build, DATASET_TXT)}
    out = os.path.join(WORK, f"yolov5s_rk3576_int8_{tag}.rknn")
    r.export_rknn(out)
    r.release()
    sz = os.path.getsize(out)
    return {
        "ok": True,
        "variant": tag,
        "onnx_used": src,
        "artifact": out,
        "artifact_bytes": sz,
        "artifact_mib": round(sz / 1048576, 2),
        "slot_budget_bytes": MODEL_SLOT_BYTES,
        "fits_15MiB_slot": sz <= MODEL_SLOT_BYTES,
        "load_s": round(t_load, 2),
        "build_s": round(t_build, 2),
        "cfg_std": args.cfg_std,
        "dep": dep,
        "quant": {"dtype": "w8a8", "algorithm": "normal", "method": "channel",
                  "target_platform": TARGET_PLATFORM},
        "evidence": "[实测] 本机 rknn-toolkit2 2.3.2 转换",
    }


def _build_session_for_sim(args, needer: str = "sim"):
    """★ 坑②: simulator 必须 load_onnx+build 同 session

    ★★ ISS-113: 这里原来写的是**裸 assert** ⇒ 干净机器上 dataset.txt 缺失时
       直接崩成 AssertionError (项目总工 10-29 09:0x 亲跑撞到)。现在:
         (1) 先 ensure_dataset() ⇒ 缺 dataset.txt 自动补跑 calib 步
         (2) 裸 assert 全部换成带行动指引的 BenchError
    """
    src = ONNX_MODEL
    if not args.no_cut:
        dst = os.path.join(WORK, "yolov5s_heads.onnx")
        if not os.path.exists(dst):
            step_cut(args)
        if os.path.exists(dst):
            src = dst
    # ★ ISS-113: 量化校准集清单 (缺 → 自动补跑 calib 步)
    ensure_dataset(args, needer)
    r = _new_rknn(cfg_std=args.cfg_std)
    rc_load = r.load_onnx(src)
    if rc_load != 0:
        raise BenchError("rknn.load_onnx 失败 rc=%s (src=%s)" % (rc_load, src))
    rc_build = r.build(do_quantization=True, dataset=DATASET_TXT)
    if rc_build != 0:
        raise BenchError(
            "rknn.build(INT8 量化) 失败 rc=%s\n"
            "  → 校准集清单 = %s; 量化标定量 = %d 张; 源目录 = %s"
            % (rc_build, DATASET_TXT, _count_dataset(), CALIB_DIR))
    rc_init = r.init_runtime()   # target=None ⇒ simulator
    if rc_init != 0:
        raise BenchError("rknn.init_runtime 失败 rc=%s" % rc_init)
    return r


def _count_dataset() -> int:
    try:
        with open(DATASET_TXT, encoding="utf-8") as f:
            return sum(1 for ln in f if ln.strip())
    except OSError:
        return 0


def _predict(rknn_obj, blob, args, ga, cut: bool):
    """跑一次推理 → (boxes, scores, classes); cut=True 用 raw head 解码"""
    outs = rknn_obj.inference(inputs=[blob], data_format="nchw")
    if cut:
        # 切版只有 3 路 head: outs = [350, 498, 646]
        h80, h40, h20 = outs[0], outs[1], outs[2]
        return decode_raw_heads(h80, h40, h20, ga, args.score_thr, args.nms_iou,
                                args.max_det, 1.0, 0, 0, 1, 1)   # 先在 640 坐标系里解
    else:
        return decode_output_tensor(outs[0], args.score_thr, args.nms_iou,
                                    args.max_det, 1.0, 0, 0, 1, 1)


def _heads_by_shape(outs):
    """★ RKNN 工具链会**重排输出顺序** (实测: 切版模型 outs[0] 是 40×40 的 498, 不是 80×80 的 350)
    ⇒ 必须**按 spatial 尺寸**认头, 不能按下标。返回 (h80, h40, h20)"""
    by_g = {}
    for o in outs:
        a = np.asarray(o)
        if a.ndim != 5:
            continue
        g = a.shape[2]
        by_g[g] = a
    return by_g.get(80), by_g.get(40), by_g.get(20)


def step_sim(args) -> dict:
    """仿真推理: max_abs_diff (vs ONNX FP32) + 耗时统计"""
    import cv2  # noqa: PLC0415
    import onnxruntime as ort  # noqa: PLC0415
    if not os.path.isdir(VAL_DIR):
        raise BenchError("COCO val2017 目录不存在: %s (sim/acc 步需要它)" % VAL_DIR)
    files = sorted(os.listdir(VAL_DIR))[:5]
    blobs, names = [], []
    for fn in files:
        img = cv2.imread(os.path.join(VAL_DIR, fn))
        blob, _s, _px, _py = preprocess(img, IMGSZ, div255=(args.input_scale == "unit"))
        blob_ref, _s, _px, _py = preprocess(img, IMGSZ, div255=True)   # ONNX 参考永远 /255
        blobs.append((blob, blob_ref))
        names.append(fn)
    so = ort.SessionOptions()
    so.log_severity_level = 3
    sess = ort.InferenceSession(ONNX_MODEL, so, providers=["CPUExecutionProvider"])
    iname = sess.get_inputs()[0].name
    r = _build_session_for_sim(args, needer="sim")
    cut = not args.no_cut
    diffs = []
    for blob, blob_ref in blobs:
        a = sess.run(None, {iname: blob_ref})      # ONNX FP32 参考: 永远喂 /255
        b = r.inference(inputs=[blob], data_format="nchw")
        for i, (x, y) in enumerate(zip(a, b)):
            if x.shape == y.shape:
                diffs.append({"out": i, "max_abs_diff": float(np.max(np.abs(
                    x.astype(np.float64) - y.astype(np.float64))))})
    blob = blobs[0][0]
    r.inference(inputs=[blob], data_format="nchw")
    ts = []
    n = args.sim_iters
    for _ in range(n):
        t0 = time.perf_counter()
        r.inference(inputs=[blob], data_format="nchw")
        ts.append((time.perf_counter() - t0) * 1000)
    ts = np.array(ts)
    r.release()
    return {
        "variant": "heads(cut)" if cut else "full",
        "n_images_compared": len(blobs),
        "max_abs_diff_vs_onnx_fp32": diffs,
        "sim_latency_ms": {
            "min": round(float(ts.min()), 2), "avg": round(float(ts.mean()), 2),
            "max": round(float(ts.max()), 2), "p50": round(float(np.median(ts)), 2),
            "n": int(len(ts)),
        },
        "evidence": "[推算·仿真] ★★ **simulator 是 x86 CPU 模拟 NPU, 不是 NPU 吞吐代理** "
                    "(实测 ~380ms vs 公开第三方板端十几 ms ⇒ 差 ~20~30×) ⇒ "
                    "**该值不许填进延迟预算**",
    }


def step_acc(args) -> dict:
    """COCO val2017 F1 —— 与 10-28 (eval_od_accuracy.py) 同口径"""
    import cv2  # noqa: PLC0415
    if not os.path.isdir(VAL_DIR):
        raise BenchError("COCO val2017 目录不存在: %s (acc 步需要它)" % VAL_DIR)
    if not os.path.isfile(ANN):
        raise BenchError("COCO 标注文件不存在: %s (acc 步需要它)" % ANN)
    ga = load_grid_anchor(ONNX_MODEL)
    r = _build_session_for_sim(args, needer="acc")
    cut = not args.no_cut
    files = sorted(os.listdir(VAL_DIR))[:args.images]
    preds = {}
    t0 = time.time()
    for fn in files:
        iid = int(fn.split(".")[0])
        img = cv2.imread(os.path.join(VAL_DIR, fn))
        if img is None:
            continue
        H, W = img.shape[:2]
        blob, scale, px, py = preprocess(img, IMGSZ, div255=(args.input_scale == "unit"))
        outs = r.inference(inputs=[blob], data_format="nchw")
        if cut:
            h80, h40, h20 = _heads_by_shape(outs)
            b, s, c = decode_raw_heads(h80, h40, h20, ga, args.score_thr,
                                       args.nms_iou, args.max_det, scale, px, py, H, W)
        else:
            b, s, c = decode_output_tensor(outs[0], args.score_thr, args.nms_iou,
                                           args.max_det, scale, px, py, H, W)
        if len(s):
            preds[iid] = (b, s, c)
    r.release()
    res = score_predictions(preds, len(preds), args.eval_iou)
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["images_requested"] = args.images
    res["score_thr"] = args.score_thr
    res["nms_iou"] = args.nms_iou
    res["variant"] = "heads(cut, CPU 解码)" if cut else "full(output 张量)"
    res["input_scale"] = args.input_scale
    res["cfg_std"] = args.cfg_std
    res["caliber"] = ("逐类 IoU 贪心匹配 (同 SW/tools/eval_od_accuracy.py) —— "
                      "**不是官方 mAP**, 只可同口径自比")
    res["evidence"] = "[实测] RKNN INT8 模型 (PC simulator) 在 COCO val2017 上的 F1"
    # FP32 参考 (onnxruntime, 同一个 ONNX + 同一套解码) —— 量化 INT8 精度损失的基线
    if args.fp32_baseline:
        res["fp32_baseline"] = _fp32_baseline(args, ga, cut)
        res["int8_vs_fp32"] = {
            "f1_delta": round(res["f1"] - res["fp32_baseline"]["f1"], 4),
            "recall_delta": round(res["recall"] - res["fp32_baseline"]["recall"], 4),
            "precision_delta": round(res["precision"] - res["fp32_baseline"]["precision"], 4),
        }
    return res


def _fp32_baseline(args, ga, cut) -> dict:
    """onnxruntime FP32 参考 (同一套 decode + 同一套匹配) —— INT8 量化损失的基线"""
    import cv2  # noqa: PLC0415
    import onnxruntime as ort  # noqa: PLC0415
    so = ort.SessionOptions()
    so.log_severity_level = 3
    src = ONNX_MODEL
    if cut:
        dst = os.path.join(WORK, "yolov5s_heads.onnx")
        if not os.path.exists(dst):
            step_cut(args)
        src = dst
    sess = ort.InferenceSession(src, so, providers=["CPUExecutionProvider"])
    iname = sess.get_inputs()[0].name
    files = sorted(os.listdir(VAL_DIR))[:args.images]
    preds = {}
    t0 = time.time()
    for fn in files:
        iid = int(fn.split(".")[0])
        img = cv2.imread(os.path.join(VAL_DIR, fn))
        if img is None:
            continue
        H, W = img.shape[:2]
        blob, scale, px, py = preprocess(img, IMGSZ, div255=True)   # ONNX FP32: 真实输入域
        out = sess.run(None, {iname: blob})
        if cut:
            h80, h40, h20 = _heads_by_shape(out)
            b, s, c = decode_raw_heads(h80, h40, h20, ga, args.score_thr,
                                       args.nms_iou, args.max_det, scale, px, py, H, W)
        else:
            b, s, c = decode_output_tensor(out[0], args.score_thr, args.nms_iou,
                                           args.max_det, scale, px, py, H, W)
        if len(s):
            preds[iid] = (b, s, c)
    r = score_predictions(preds, len(preds), args.eval_iou)
    r["elapsed_s"] = round(time.time() - t0, 1)
    r["variant"] = res_variant = ("heads(cut, CPU 解码)" if cut else "full(output 张量)")
    r["evidence"] = "[实测] ONNX FP32 (onnxruntime CPU) 同口径参考"
    return r


def step_e2e(args) -> dict:
    """端到端重算 (口径 A)"""
    npu_candidates = []
    # 板端实测 (无板 ⇒ 空)
    npu_candidates.append({"label": "板端实测 (RK3576 NPU, 我们自己的板)", "ms": None,
                           "evidence": "[0数据] 本单无 RK3576 板"})
    # 第三方公开实测 (model_zoo 官方性能表: 整链路 FPS, ⇒ 纯 NPU 的上界)
    for c in THIRD_PARTY:
        if args.thirdparty_ms:
            continue
        npu_candidates.append(c)
    # 命令行传入的第三方实测 (可覆盖)
    if args.thirdparty_ms:
        npu_candidates.append({"label": f"第三方公开实测 ({args.thirdparty_ms} ms)",
                               "ms": float(args.thirdparty_ms),
                               "evidence": "[公开实测·第三方] " + (args.thirdparty_src or "外部")})
    # 仿真 (只在显式要求时带)
    if args.use_sim_as_npu and args.sim_ms:
        npu_candidates.append({"label": f"仿真器 ({args.sim_ms} ms)",
                               "ms": float(args.sim_ms),
                               "evidence": "[推算·仿真] ★★ 不代表板端 NPU, 仅作下界参考"})
    rows = []
    for cand in npu_candidates:
        if cand["ms"] is None:
            rows.append({**cand, "T_od": None, "modeA_e2e": None,
                         "modeB_e2e": None, "age": None,
                         "modeA_verdict": "unknown", "modeB_verdict": "unknown"})
            continue
        t_od = cand["ms"] + T_OD_FIXED
        a_e2e = e2e_mode_a(t_od)
        b_e2e, age = e2e_mode_b(t_od)
        rows.append({
            **cand, "T_od": round(t_od, 2),
            "modeA_e2e": round(a_e2e, 2),
            "modeA_fps": round(1000.0 / (S3 + t_od + DISPLAY_TAIL), 1),
            "modeA_verdict": "pass" if a_e2e <= 60 else "fail",
            "modeB_e2e": round(b_e2e, 2), "age": age,
            "modeB_verdict": "pass" if b_e2e <= 60 else "fail",
        })
    # 台阶表
    ladder = []
    for npu in (2, 6, 10, 10.67, 12, 16.67, 20.33, 24, 26.33, 30, 33.33, 40):
        t_od = npu + T_OD_FIXED
        a = e2e_mode_a(t_od)
        b, age = e2e_mode_b(t_od)
        ladder.append({"npu_ms": npu, "T_od": round(t_od, 2), "age": age,
                       "modeA_e2e": round(a, 2), "modeA": "pass" if a <= 60 else "fail",
                       "modeB_e2e": round(b, 2), "modeB": "pass" if b <= 60 else "fail"})
    return {
        "caliber": "口径 A = 曝光开始 → 光机出光 (老板 10-25 19:16 锁死, 本单不改)",
        "constants": {"P60": P60, "exposure_block": EXPOSURE_BLOCK,
                      "S4": S4, "S6": S6, "S7": S7, "T_od_fixed": T_OD_FIXED,
                      "display_tail": DISPLAY_TAIL, "S10_optic": S10,
                      "S10_evidence": "[0数据] 光机逐帧延迟未公开, 按目标值 5ms 占位"},
        "modeA_formula": "e2e = 24.67 + T_od + 9",
        "modeB_formula": "e2e = (age+1)*16.67 + 17,  age = ceil(T_od/16.67)  ← 台阶函数",
        "thresholds": {
            "modeA_pass_needs_npu_le": round(60 - EXPOSURE_BLOCK - DISPLAY_TAIL - T_OD_FIXED, 2),
            "modeB_age1_pass_needs_npu_le": round(P60 - T_OD_FIXED, 2),
        },
        "candidates": rows,
        "ladder": ladder,
    }


# ----------------------------------------------------------------------------
# 6. main
# ----------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="RKNN 转换链实测 + RK3576 端到端判定")
    ap.add_argument("step", choices=["probe", "calib", "convert", "sim", "acc", "e2e", "all"])
    ap.add_argument("--images", type=int, default=300, help="COCO val2017 取前 N 张")
    ap.add_argument("--score-thr", type=float, default=0.3)
    ap.add_argument("--nms-iou", type=float, default=0.45)
    ap.add_argument("--eval-iou", type=float, default=0.5)
    ap.add_argument("--max-det", type=int, default=100)
    ap.add_argument("--sim-iters", type=int, default=20)
    ap.add_argument("--fp32-baseline", action="store_true",
                    help="同时跑 ONNX FP32 (onnxruntime) 参考, 量化 INT8 精度损失")
    ap.add_argument("--no-cut", action="store_true",
                    help="不切后处理 (用完整 ONNX, 输出 `output` 张量) —— 用于演示坑 3")
    ap.add_argument("--cfg-std", type=int, default=255,
                    help="rknn.config 的 std_values (0=不设, 255=img/255)")
    ap.add_argument("--input-scale", choices=["raw", "unit"], default="raw",
                    help="喂给 RKNN runtime 的输入域: raw=图像域 0-255 (★默认, 模型内建 std=255 会自己除) / unit=已经 /255 (调试用)")
    ap.add_argument("--thirdparty-ms", type=float, default=None,
                    help="第三方公开实测的 RK3576 NPU 耗时 (ms), 用于 e2e 代入")
    ap.add_argument("--thirdparty-src", default=None)
    ap.add_argument("--use-sim-as-npu", action="store_true",
                    help="★ 仅调试用: 把仿真耗时当 NPU 耗时代入 e2e (会标 [推算·仿真])")
    ap.add_argument("--sim-ms", type=float, default=None)
    ap.add_argument("--no-auto-calib", action="store_true",
                    help="★ 缺 dataset.txt 时**不自动补跑** calib 步 (默认会自动补跑); "
                         "关掉后缺依赖会给出指向 calib 步的明确报错 (不再抛 AssertionError)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    out = {}
    t_start = time.time()
    if args.step == "all":
        # ★ 一条命令复现全部数字: 精度步默认带上 FP32 基线 (量化损失)
        args.fp32_baseline = True
    # ★ ISS-113: 步间依赖失败 (缺校准集/数据目录) 走**明确报错**, 不抛裸 AssertionError
    try:
        if args.step in ("probe", "all"):
            out["probe"] = step_probe(args)
        if args.step in ("calib", "all"):
            out["calib"] = step_calib(args)
        if args.step in ("convert", "all"):
            out["convert"] = step_convert(args)
        if args.step in ("sim", "all"):
            out["sim"] = step_sim(args)
        if args.step in ("acc", "all"):
            out["acc"] = step_acc(args)
        if args.step in ("e2e", "all"):
            out["e2e"] = step_e2e(args)
    except BenchError as e:
        print("=" * 96)
        print("❌ 前置条件不满足 (不是脚本 bug) —— 解决办法在上面:")
        print("=" * 96)
        print(str(e))
        print("=" * 96)
        return 1
    out["_elapsed_s"] = round(time.time() - t_start, 1)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0

    print("=" * 96)
    print("RKNN 转换链实测 + RK3576 端到端判定 (sw-lead 2026-10-29)")
    print("=" * 96)
    if "probe" in out:
        p = out["probe"]
        print("\n[probe] rknn-toolkit2 =", p["rknn_toolkit2_version"],
              "| python", p["python"], "| onnx", p["onnx_version"], "| numpy", p["numpy_version"])
        print("[probe] RK3576 板端在不在 :", p["rk3576_board_present"], "| adb devices:", p["adb_devices"])
        print("[probe] 模型:", p["model_path"], "sha16 =", p["model_sha16"],
              "(台账一致:", p["model_sha16_matches_ledger"], ")")
        print("[probe] 输入:", p["model_inputs"])
        print("[probe] 输出:", p["model_outputs"])
        print("[probe] 节点数:", p["model_nodes"], "| 算子表:", p["op_census"])
        print("[probe] NPU 高风险算子:", p["npu_risky_ops_present"] or "无")
    if "calib" in out:
        c = out["calib"]
        print(f"\n[calib] {c['n_images']} 张 → {c['calib_dir']} ({c['letterbox']})")
        print(f"[calib] dataset.txt = {c['dataset_txt']}")
    if "convert" in out:
        c = out["convert"]
        if c.get("ok"):
            print(f"\n[convert] ✅ 成功  {c['artifact']}")
            if c.get("dep"):
                print(f"[convert] 校准集: {c['dep']['note']} "
                      f"({c['dep']['n_images']} 张, {c['dep']['dataset_txt']})")
            print(f"[convert] 产物 {c['artifact_bytes']} B = {c['artifact_mib']} MiB "
                  f"| 15MiB 槽位够不够: {c['fits_15MiB_slot']}")
            print(f"[convert] load {c['load_s']}s / build(INT8) {c['build_s']}s")
            print(f"[convert] 量化: {c['quant']}")
        else:
            print(f"\n[convert] ❌ 失败 @ {c.get('stage')} rc={c.get('rc')}")
    if "sim" in out:
        s = out["sim"]
        print("\n[sim] max_abs_diff vs ONNX FP32:", s["max_abs_diff_vs_onnx_fp32"])
        print("[sim] 仿真耗时 ms:", s["sim_latency_ms"])
        print("[sim] ⚠️", s["evidence"])
    if "acc" in out:
        a = out["acc"]
        print(f"\n[acc] COCO val2017 {a['n_images']} 张 | TP={a['tp']} FP={a['fp']} FN={a['fn']}")
        print(f"[acc] Precision={a['precision']:.4f} Recall={a['recall']:.4f} F1={a['f1']:.4f}")
        print("[acc] 口径:", a["caliber"])
        if "fp32_baseline" in a:
            b = a["fp32_baseline"]
            print(f"[acc] FP32 参考 (onnxruntime): P={b['precision']:.4f} R={b['recall']:.4f} "
                  f"F1={b['f1']:.4f} | INT8 相对 FP32: {a['int8_vs_fp32']}")
    if "e2e" in out:
        e = out["e2e"]
        print(f"\n[e2e] {e['caliber']}")
        print(f"[e2e] 模式A: {e['modeA_formula']} | 模式B: {e['modeB_formula']}")
        print(f"[e2e] 阈值: 模式A 达标需 NPU ≤ {e['thresholds']['modeA_pass_needs_npu_le']} ms; "
              f"模式B age=1 需 NPU ≤ {e['thresholds']['modeB_age1_pass_needs_npu_le']} ms")
        for r in e["candidates"]:
            if r["ms"] is None:
                print(f"[e2e] · {r['label']}: NPU=— (板端实测未做) ⇒ 端到端 unknown")
                continue
            print(f"[e2e] · {r['label']}: NPU={r['ms']:.2f} T_od={r['T_od']} "
                  f"模式A={r['modeA_e2e']}ms ({r['modeA_verdict']}, 显示 {r.get('modeA_fps')}fps) "
                  f"模式B={r['modeB_e2e']}ms age={r['age']} ({r['modeB_verdict']})")
        print("[e2e] 台阶表 (NPU ms → 端到端 ms):")
        for r in e["ladder"]:
            print(f"        NPU={r['npu_ms']:>6} T_od={r['T_od']:>6} age={r['age']} "
                  f"| 模式A {r['modeA_e2e']:>6} {r['modeA']:4s} "
                  f"| 模式B {r['modeB_e2e']:>6} {r['modeB']}")
    print("=" * 96)
    print(f"总耗时 {out['_elapsed_s']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
