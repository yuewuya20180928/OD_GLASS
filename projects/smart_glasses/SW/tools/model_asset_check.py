#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型资产登记检查器 (Model Asset Registry Checker)
=====================================================================
ISS-037 (sw-lead, 2026-10-27): 模型资产与 INT8 量化管理缺失
  —— 权重是资产, 但散在 sw 需求里, 没有台账、没有许可栏、没有量化回归门禁。

本脚本把 SW/MODEL_ASSETS.md §1 的"资产台账"变成**可机械复核**的东西:
  ① 逐个资产核对: 存在 / 大小 / sha256 前缀 —— 防止"文件名改了内容没改"或"张冠李戴"
  ② ONNX: 读 metadata_props → 抽 license / version / opset / 输入输出 shape
        ⚠️ metadata_props 为空 **不等于** 许可未知 —— ISS-087 起, 许可由
        `SW/tools/license_probe.py` 溯源判定并登记进台账 (expected_license);
        台账里 expected_license 仍为空 = 许可真的没判定 → 量产放行阻断项 L1
  ③ .nb (NBG): 解析头部 4 个字段
        byte 0-3  magic "VPMN"
        byte 4-5  version
        byte 6-7  format version (1 = VIPLite 2.0.3.2 / 2 = 2.0.10.x ABI)
        byte 8-11 target chip ID (LE)
     ★ chip ID 错 = 板端 NPU 加载后 SRAM size 报错 (A733 实测踩过)
  ④ 容量门禁: 板端 model_a/model_b 分区 = 15 MiB → 板端产物超了刷不进去
  ⑤ 重复资产: sha256 相同但 id 不同 → 名字骗人 (实测 yolov5s-sim_320_clean 与 _v2 完全同内容)
  ⑥ C9 PC 侧 1 帧推理冒烟 (onnxruntime): **光看 shape 查不出坏模型** ——
        实测 `yolov5s-sim_320_clean.onnx` 输入改成 320 但图内 Reshape/anchor 常量
        仍是 640 尺度 → onnxruntime 直接 ShapeInferenceError 加载失败
        → 交付集里的模型若 C9 失败 = 阻断项 L5 (模型本身是坏的)

许可口径 (ISS-087, 2026-10-28)
---------------------------
  license_state:
    permissive    = 宽松许可 (Apache-2.0/MIT/BSD) → 商用无附加义务
    agpl-granted  = AGPL + **有** Enterprise 授权记录 (license_grant 非空) → 商用可行
    agpl-no-grant = AGPL + **无**授权记录 → 商用受阻 (阻断项 L4)
    unknown       = 许可未判定 → 阻断项 L1
  ★ "metadata_props 为空" 是**取数方式**的问题, "许可未判定" 才是**阻断项**。
    两者从 ISS-087 起分开记。

用法:
    python3 SW/tools/model_asset_check.py                # 全量检查
    python3 SW/tools/model_asset_check.py --no-smoke     # 跳过 C9 冒烟 (快)
    python3 SW/tools/model_asset_check.py --json         # 机读输出
    python3 SW/tools/model_asset_check.py --id MOD-YOLOV5S-320-INT8   # 只查一条
    python3 SW/tools/model_asset_check.py --new /path/to/new.onnx      # 新模型入库: 打印台账行骨架

退出码: 0 = 台账与实物一致 (允许 WARN) | 1 = 有 FAIL | 2 = 用法/文件错
★ 语义: rc=0 **不等于可以量产**。量产放行看单独统计的 "放行阻断项 (L)" 计数 = 0
    L1 = 许可未判定 (台账 expected_license 为空; 与 metadata 是否为空无关)
    L2 = 板端产物超 15 MiB 槽位 (刷不进)
    L3 = active 资产的 target chip ID 与目标 NPU 不符 (板端加载后报错)
    L4 = AGPL-3.0 且无 Enterprise 授权记录 (商用受阻)
    L5 = 交付集资产的 PC 侧推理冒烟失败 (模型本身是坏的)
  ★ L 只统计**交付集** (state = candidate / active); reference / quarantined /
    licensing-hold 不进交付集, 但会单独列出 —— 不许静默消失。

证据分级 (与 SW/MODEL_ASSETS.md 一致):
    [实测] = 本脚本跑出来的 | [官方] = 原厂书面/官网 | [推算] = 推导 | [0数据] = 拿不到
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SW_DIR = os.path.join(PROJ, "SW")

# ---- ISS-101: 量产放行门 (L=0) 的机械判据常量 ----
# "许可干净且可转换" = 下面 5 组条件**全部**满足 (详见 SW/MODEL_RELEASE_GATE.md §3)
#   G1 许可字段: license_state ∈ {permissive, agpl-granted} (见文件头)
#   G2 转换链产出物: 至少一条 npu_ready 产物 (静态 shape + 无高风险算子)
#   G3 实测精度: measured_acc 存在且 F1 ≥ ACC_MIN_F1 且样本 ≥ ACC_MIN_IMAGES
#   G4 PC 侧推理: C9 冒烟通过 (模型不是坏的)
#   G5 板端产物: .nb / Art.Galaxy 产物存在 + ≤15 MiB + chip ID 对
# NPU 编译器普遍不支持的算子 (ACUITY/VIPLite/Art.Galaxy 类):
#   NonMaxSuppression / TopK / Range / NonZero → 必须在裁图阶段移出
NPU_RISKY_OPS = {"NonMaxSuppression", "TopK", "Range", "NonZero"}
# 转换链产出物判据 (允许存在于图中但需登记说明的算子)
NPU_SUSPECT_OPS = {"Expand", "Resize", "Shape", "Cast", "Pad",
                    "Greater", "Less", "Equal", "GreaterOrEqual",
                    "Clip", "Min", "Max", "Not"}
ACC_MIN_F1 = 0.30          # 实测精度地板 (IoU=0.5, score>=0.3)
ACC_MIN_IMAGES = 100       # 精度评测最少图数 (与校准集下限同量级)

# 板端 model_a / model_b 分区大小
# (SW/FLASH_AND_VERSION.md §4.1 推荐 C + SW/tools/s2_rescue_config.example.json)
MODEL_SLOT_BYTES = 15728640          # 15 MiB
MODEL_SLOT_MIB = 15

# 已登记资产台账 (唯一真源 = SW/MODEL_ASSETS.md §1.2; 本表必须与文档逐字段一致)
#   platform        : "candidate" (PC 侧源, 待转板端格式) | "A733-ref" (上一项目, 仅方法论参考)
#   state           : "candidate" (交付集: 待定版) | "active" (交付集: 在用)
#                   | "reference" (他项目参考) | "quarantined" (已判死: 坏模型 / chip ID 错)
#                   | "licensing-hold" (许可受限, 未采购前禁入交付物, 但随时可因采购而复活)
#   expected_license: 台账判定的许可串 (ISS-087 起: 由 license_probe.py 溯源判定, 不再等于
#                   metadata_props 原值); None = 仍未判定 → 判 L1 阻断项
#   license_state   : permissive | agpl-granted | agpl-no-grant | unknown  (见文件头)
#   license_grant   : Enterprise 授权记录号 (有值 → agpl-granted); None = 未采购
#   expected_chip   : 期望 NBG target chip ID (LE); None = 不适用
MANIFEST = [
    {
        "id": "MOD-YOLOV5S-320-INT8",
        "platform": "candidate",
        "state": "quarantined",
        "role": "★ 原'主 OD 模型候选' (320x320, 80 类) —— 【已判死】图内常量与输入尺寸不一致",
        "path": "/home/yuewuya/.openclaw/workspace/yolov5s-sim_320_clean.onnx",
        "fmt": "onnx",
        "size": 29337706,
        "sha256_16": "340978ec59391f69",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": 14,
        "expected_input": [1, 3, 320, 320],
        "expected_chip": None,
        "note": "★ 2026-10-28 C9 冒烟实测: onnxruntime 加载即失败 (Concat_527 "
                "ShapeInferenceError: Inferred=10 Declared=20) —— 只把输入改成 320, "
                "图内 Reshape/anchor 常量仍是 640 尺度 → **模型本身是坏的**; "
                "许可 = AGPL-3.0 (溯源见 SW/MODEL_LICENSE.md §1); 已隔离",
    },
    {
        "id": "MOD-YOLOV5S-320-INT8-DUP",
        "platform": "candidate",
        "state": "quarantined",
        "role": "★ 与 MOD-YOLOV5S-320-INT8 同内容不同名 (sha256 完全相同) → 台账去重后只留一条",
        "path": "/home/yuewuya/.openclaw/workspace/yolov5s-sim_320_v2.onnx",
        "fmt": "onnx",
        "size": 29337706,
        "sha256_16": "340978ec59391f69",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": 14,
        "expected_input": [1, 3, 320, 320],
        "expected_chip": None,
        "note": "文件名带 _v2 但内容与 clean 版逐字节相同 → 版本名不可信, 以 sha256 为准; "
                "已去重隔离 (同 clean 版, 同样是坏模型)",
    },
    {
        "id": "MOD-YOLOV5S-640-ARS45-SRC",
        "platform": "candidate",
        "state": "licensing-hold",
        "role": "★ 唯一实测可推理的 yolov5s ONNX (640x640) —— 走'采购'路线的转换链输入",
        "path": "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx",
        "fmt": "onnx",
        "size": 29337706,
        "sha256_16": "20368be665f6f59a",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": 14,
        "expected_input": [1, 3, 640, 640],
        "expected_chip": None,
        "note": "★ 2026-10-28 实测 onnxruntime @640 推理 OK (输出 [1,25200,85] + 3 路 "
                "80/40/20 网格特征图); 血缘: ultralytics/yolov5 v6.0 → onnxsim → "
                "onnx_extract 抽 3 路 head; 许可 AGPL-3.0 → 未采购前禁入交付物",
    },
    {
        "id": "MOD-YOLOV8S-COCO80-ONNX",
        "platform": "candidate",
        "state": "licensing-hold",
        "role": "COCO 80 类 yolov8s (备选主模型) —— AGPL-3.0, 未采购前禁入交付物",
        "path": "/work/object_detection/yolov8s_coco80/workspace/yolov8s.onnx",
        "fmt": "onnx",
        "size": 44842647,
        "sha256_16": "111da30a25b6c585",
        "expected_license": "AGPL-3.0 License (https://ultralytics.com/license)",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": 13,
        "expected_input": [1, 3, 640, 640],
        "expected_chip": None,
        "note": "★ AGPL-3.0 (metadata_props.license 原值) → 商用须向 Ultralytics 采购 "
                "Enterprise License; 2026-10-28 C9 冒烟实测 @640 推理 OK; "
                "44.8MB 源文件本身不刷板",
    },
    {
        "id": "MOD-SSDMBV2-FPNLITE-320-COCO90-TFODAPI",
        "platform": "candidate",
        "state": "candidate",
        "role": "★ 交付集里唯一许可干净的 80 类候选 (Apache-2.0) —— '不采购'路线的起点",
        "path": "/work/object_detection/pretrained/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8",
        "fmt": "savedmodel",
        "size": 9640645,
        "sha256_16": None,
        "expected_license": "Apache-2.0",
        "license_state": "permissive",
        "license_grant": None,
        "expected_opset": None,
        "expected_input": [1, 320, 320, 3],
        "expected_chip": None,
        "note": "TF OD API ssd_mobilenet_v2_fpnlite 320x320 (pipeline.config num_classes=90 "
                "→ COCO 90 含 10 padding, 可用 80 类); 许可 Apache-2.0 (tensorflow/models "
                "/research 子目录) → 商用无附加义务; ★ 但 NPU 可转换性 = [0数据] "
                "(TF SavedModel → ONNX → Art.Galaxy 三段都没跑过)",
    },
    {
        "id": "MOD-SSDMBV2-FPNLITE-320-FP32-FULL",
        "platform": "candidate",
        "state": "reference",
        "role": "★ ISS-101 实测产出: Apache-2.0 候选的 TF SavedModel → ONNX **全图** "
                "(含 NMS 后处理) —— **PC 侧 FP32 精度基准 / 裁图对照**, 不是上板产物",
        "path": str(SW_DIR / "artifacts" / "models" / "ssd_mbv2_fpnlite_320_fp32_full.onnx"),
        "fmt": "onnx",
        "size": 12259298,
        "sha256_16": "8709cc23432340f6",
        "expected_license": "Apache-2.0",
        "license_state": "permissive",
        "license_grant": None,
        "expected_opset": 13,
        "expected_input": [1, "unk__5514", "unk__5515", 3],
        "expected_chip": None,
        "npu_ready": False,
        "measured_acc": {"prec": 0.4521, "rec": 0.4184, "f1": 0.4346,
                         "iou": 0.5, "score_thr": 0.3, "images": 299,
                         "dataset": "COCO val2017 (前 299 张有标注)"},
        "note": "★ ISS-101 (2026-10-28) 实测产出: tf2onnx 1.16.1 + TF 2.20.0 "
                "--saved-model → ONNX **成功** (rc=0), opset 13, 3304 节点 / 33 算子; "
                "⚠️ 含 NonMaxSuppression(90)/TopK(2)/Range(2)/NonZero(1) → **不可上 NPU**; "
                "输入是动态 shape → NPU 编译器拒收; 故 state=reference (PC 侧基准)",
    },
    {
        "id": "MOD-SSDMBV2-FPNLITE-320-FP32-HEAD-NPU",
        "platform": "candidate",
        "state": "candidate",
        "role": "★ ISS-101 实测产出: Apache-2.0 候选的 **NPU 就绪 head 子图** "
                "(裁掉 NMS 后处理 + 固化静态 shape) —— 转换链第 1/2 段的板端输入",
        "path": str(SW_DIR / "artifacts" / "models" / "ssd_mbv2_fpnlite_320_fp32_head_npu.onnx"),
        "fmt": "onnx",
        "size": 10967518,
        "sha256_16": "6603df1e12391cfc",
        "expected_license": "Apache-2.0",
        "license_state": "permissive",
        "license_grant": None,
        "expected_opset": 13,
        "expected_input": [1, 320, 320, 3],
        "expected_chip": None,
        "npu_ready": True,
        "measured_acc": {"prec": 0.4521, "rec": 0.4184, "f1": 0.4346,
                         "iou": 0.5, "score_thr": 0.3, "images": 299,
                         "dataset": "COCO val2017 (前 299 张有标注)"},
        "note": "★ ISS-101 (2026-10-28) 实测产出: 由 SW/tools/cut_postprocessor.py "
                "从全图裁出 (保留 raw_detection_boxes/raw_detection_scores) + "
                "SW/tools/fix_static_shape.py 固化 shape → 299 节点 / 18 算子, "
                "**无 NMS 家族算子**; 与全图输出 max_abs_diff = 0.000e+00 (逐位相同); "
                "x86 CPU 实测 5.34 ms/帧 (vs 全图 35.08 ms) — 转换链第 1/2 段已通",
    },
    {
        "id": "MOD-YOLOV8S-COCO80-NB",
        "platform": "A733-ref",
        "state": "quarantined",
        "role": "COCO 80 类 yolov8s 的 NBG (A733 格式)",
        "path": "/work/object_detection/yolov8s_coco80/workspace/yolov8s_coco80.nb",
        "fmt": "nb",
        "size": 8450776,
        "sha256_16": "7fa016615610adaa",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": None,
        "expected_input": None,
        "expected_chip": 0x1000003B,
        "note": "★ 实测 chip ID = 0x10000020 (错) → A733 板端不可加载, 已隔离作废待重导",
    },
    {
        "id": "MOD-YOLOV8S-SCENEFT-NB",
        "platform": "A733-ref",
        "state": "reference",
        "role": "yolov8s 场景微调 NBG (★ 本地唯一 chip ID 正确的 yolov8s .nb)",
        "path": "/work/object_detection/yolov8s_scene_ft/deploy/yolov8s_scene_ft.nb",
        "fmt": "nb",
        "size": 12559680,
        "sha256_16": "6ac6975036524637",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": None,
        "expected_input": None,
        "expected_chip": 0x1000003B,
        "note": "chip 0x1000003B ✓ format 2 ✓; 板端实测可加载 (A733, 2026-08-17); 12.0MB ≤ 15MiB ✓",
    },
    {
        "id": "MOD-YOLOV8S-SCENEFT-V2-NB",
        "platform": "A733-ref",
        "state": "reference",
        "role": "yolov8s 场景微调 v2 NBG",
        "path": "/work/object_detection/yolov8s_scene_ft_v2/deploy/yolov8s_scene_ft_v2.nb",
        "fmt": "nb",
        "size": 7873008,
        "sha256_16": "e8a53286029272a4",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": None,
        "expected_input": None,
        "expected_chip": 0x1000003B,
        "note": "7.5MB, chip ✓; 本地最小可用 NBG",
    },
    {
        "id": "MOD-YOLOV5S-A733-NB-BASELINE",
        "platform": "A733-ref",
        "state": "quarantined",
        "role": "A733 板端 baseline .nb (acuity pipeline 产出)",
        "path": "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/wksp_nbg_unify/network_binary.nb",
        "fmt": "nb",
        "size": 6479672,
        "sha256_16": "e6827040cb29c60d",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": None,
        "expected_input": None,
        "expected_chip": 0x1000003B,
        "note": "★ 实测 chip ID = 0x10000020 (错, 来自 --optimize v3 flag) → 板端不可加载, 已隔离",
    },
    {
        "id": "MOD-YOLOV5S-320-QUANT-PARAM",
        "platform": "A733-ref",
        "state": "reference",
        "role": "INT8 量化参数表 (.quantize) —— 量化配置本身就是资产",
        "path": "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim_320.quantize",
        "fmt": "quantize",
        "size": 620518,
        "sha256_16": "c1d884d2f196fe45",
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": None,
        "expected_input": None,
        "expected_chip": None,
        "note": "per-tensor asymmetric_affine, i8; ★换量化参数=换模型, 必须跟 model= 版本串绑定",
    },
    {
        "id": "MOD-YOLOV5S-320-CALIB-DATASET",
        "platform": "A733-ref",
        "state": "reference",
        "role": "INT8 校准集 (100 张 COCO calib 图)",
        "path": "/home/yuewuya/Public/radxa_yolo/calib_yolov5_100",
        "fmt": "dir",
        "size": None,
        "sha256_16": None,
        "expected_license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "license_grant": None,
        "expected_opset": None,
        "expected_input": None,
        "expected_chip": None,
        "note": "目录型资产; 100 张 jpg (实测); 校准集 ≤6 张是 A733 踩过的坑",
    },
]


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_nbg_header(path: str) -> dict:
    with open(path, "rb") as f:
        b = f.read(16)
    if len(b) < 12:
        return {"magic": b[0:4].decode("ascii", "replace"), "truncated": True}
    return {
        "magic": b[0:4].decode("ascii", "replace"),
        "version": struct.unpack("<H", b[4:6])[0],
        "format": struct.unpack("<H", b[6:8])[0],
        "chip": struct.unpack("<I", b[8:12])[0],
        "truncated": False,
    }


def onnx_meta(path: str) -> dict:
    try:
        import onnx  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        return {"_err": f"onnx 模块不可用: {e}"}
    m = onnx.load(path, load_external_data=False)
    md = {p.key: p.value for p in m.metadata_props}
    g = m.graph

    def shape(t):
        return [d.dim_value or d.dim_param for d in t.type.tensor_type.shape.dim]

    return {
        "producer": f"{m.producer_name} {m.producer_version}".strip(),
        "opset": max((o.version for o in m.opset_import if not o.domain), default=None),
        "meta": md,
        "license": md.get("license"),
        "version": md.get("version"),
        "inputs": {i.name: shape(i) for i in g.input},
        "outputs": {o.name: shape(o) for o in g.output},
        "n_nodes": len(g.node),
        "n_op_types": len(set(n.op_type for n in g.node)),
    }


SMOKE = True   # C9: PC 侧 1 帧推理冒烟 (--no-smoke 可关, 约省 10 s)


def smoke_test_onnx(path: str, inputs: dict) -> tuple:
    """C9: onnxruntime 建 session + 跑 1 帧随机输入。
       返回 (ok|None, msg); None = 环境不具备 (onnxruntime 不可用) → 不判 FAIL。
       ★ 动机: 实测 yolov5s-sim_320_clean.onnx 的输入改成 320 但图内常量仍是 640
         → onnxruntime 加载即报 ShapeInferenceError —— 光看 metadata/shape 查不出来。"""
    try:
        import numpy as np  # noqa: PLC0415
        import onnxruntime as ort  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        return None, f"⚠️ onnxruntime/numpy 不可用 ({e}) → 跳过 C9"
    try:
        so = ort.SessionOptions()
        so.log_severity_level = 3
        sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        name = sess.get_inputs()[0].name
        shape = [d if isinstance(d, int) and d > 0 else 1 for d in sess.get_inputs()[0].shape]
        x = np.zeros(shape, dtype=np.float32)
        outs = sess.run(None, {name: x})
        shapes = [list(o.shape) for o in outs]
        return True, f"PC 侧 1 帧推理 OK (onnxruntime) · 输出 {shapes}"
    except Exception as e:  # noqa: BLE001
        msg = str(e).split("\n")[0][:180]
        return False, f"★ PC 侧 1 帧推理失败 → 模型本身是坏的: {msg}"


def check_one(a: dict) -> dict:
    """返回一条检查结果: {id, checks:[(code, ok|None, msg)], ...}"""
    res = {"id": a["id"], "platform": a["platform"], "state": a["state"],
           "fmt": a["fmt"], "path": a["path"], "checks": []}

    def add(code, ok, msg):
        # ok: True=通过 / False=不通过 / None=告警 (信息性或 [0数据], 不判 FAIL)
        res["checks"].append((code, None if ok is None else bool(ok), msg))

    p = a["path"]

    if a["fmt"] == "dir":
        if not os.path.isdir(p):
            add("C1", False, "目录不存在")
            return res
        n = len([f for f in os.listdir(p) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
        add("C1", True, f"目录存在, 图像 {n} 张")
        add("C4", n >= 100, f"校准集 {n} 张 (要求 ≥100 张; A733 实测踩坑: 6 张不够)")
        return res

    if a["fmt"] == "savedmodel":
        # TF SavedModel 目录型资产 (Apache-2.0 路线用)
        if not os.path.isdir(p):
            add("C1", False, "目录不存在")
            return res
        pb = os.path.join(p, "saved_model", "saved_model.pb")
        add("C1", os.path.exists(pb),
            f"目录存在, saved_model.pb {'存在' if os.path.exists(pb) else '缺失'}")
        if os.path.exists(pb):
            sz_pb = os.path.getsize(pb)
            if a.get("size") is not None:
                add("C2", sz_pb == a["size"],
                    f"saved_model.pb 大小 {sz_pb} B (台账 {a['size']} B)")
            if a.get("sha256_16"):
                got = sha256_of(pb)[:16]
                add("C3", got == a["sha256_16"], f"sha256[:16] {got} (台账 {a['sha256_16']})")
        add("C4", None, "PC 侧源 (SavedModel, 不直接刷板; 15 MiB 门禁管转换后的板端产物)")
        lic = a.get("expected_license")
        if lic:
            add("C5", True,
                f"许可 = {lic!r} (台账判定; SavedModel 无 metadata → 溯源见 SW/MODEL_LICENSE.md)")
        else:
            add("C5", None, "★ 许可未判定 → 量产放行阻断项 L1")
        return res

    if not os.path.exists(p):
        add("C1", False, "文件不存在")
        return res
    add("C1", True, f"文件存在 ({os.path.getsize(p)} B)")

    sz = os.path.getsize(p)
    if a.get("size") is not None:
        add("C2", sz == a["size"], f"大小 {sz} B (台账 {a['size']} B)")
    else:
        add("C2", True, f"大小 {sz} B (台账未登记)")

    if a.get("sha256_16"):
        got = sha256_of(p)[:16]
        add("C3", got == a["sha256_16"], f"sha256[:16] {got} (台账 {a['sha256_16']})")

    # C4 容量门禁: **只管板端产物** (.nb)。ONNX 是 PC 侧源文件, 不直接刷板,
    #    它的大小由转换后的 .nb 决定 → 只报信息 (WARN), 不判 FAIL。
    if a["fmt"] == "nb":
        add("C4", sz <= MODEL_SLOT_BYTES,
            f"板端产物容量 {sz/1048576:.1f} MiB vs 槽位 {MODEL_SLOT_MIB} MiB")
    elif a["fmt"] == "onnx":
        add("C4", None,
            f"PC 侧源文件 {sz/1048576:.1f} MiB (不直接刷板; 15 MiB 门禁管转换后的 .nb)")

    if a["fmt"] == "onnx":
        m = onnx_meta(p)
        if "_err" in m:
            add("C5", None, f"onnx 解析跳过: {m['_err']}")
        else:
            lic = m.get("license")
            exp = a.get("expected_license")
            if exp:
                if lic:
                    # metadata 自带许可 → 必须与台账判定一致 (防台账与实物脱节)
                    add("C5", lic == exp, f"license = {lic!r} (台账 {exp!r})")
                else:
                    # metadata 空 ≠ 许可未知: 台账已用 license_probe.py 溯源判定
                    add("C5", True,
                        f"metadata_props 无 license → 台账判定许可 = {exp!r} "
                        f"(溯源: SW/tools/license_probe.py; 证据链见 SW/MODEL_LICENSE.md)")
            else:
                add("C5", None, "★ 许可未判定 (台账 expected_license 为空) → 量产放行阻断项 L1")
            if a.get("expected_opset") is not None:
                add("C6", m.get("opset") == a["expected_opset"], f"opset = {m.get('opset')}")
            if a.get("expected_input"):
                got = list(m["inputs"].values())[0] if m["inputs"] else None
                add("C7", got == a["expected_input"], f"输入 shape = {got}")
        # C9 PC 侧 1 帧推理冒烟 (ISS-087 新增): 光看 shape 查不出坏模型
        if SMOKE and a["fmt"] == "onnx":
            ok, msg = smoke_test_onnx(p, m.get("inputs") if "_err" not in m else {})
            if ok is None:
                add("C9", None, msg)
            elif a["state"] in ("candidate", "active"):
                # 交付集里失败 = 真阻断项 (L5)
                add("C9", ok, msg)
            else:
                # 已隔离/禁入交付物: 失败正是隔离理由 → 只报信息, 不判 FAIL
                add("C9", None, f"[{a['state']}] {msg}")

        # ---- ISS-101: C10~C13 NPU 就绪度 (量产放行门 G2 的机械判据) ----
        if a["fmt"] == "onnx" and "_err" not in m:
            ops = {n.op_type for n in onnx.load(p, load_external_data=False).graph.node}
            risky = sorted(ops & NPU_RISKY_OPS)
            add("C10", not risky,
                f"NPU 高风险算子 (NMS/TopK/Range/NonZero): "
                f"{risky if risky else '无'}"
                + ("" if risky else " → 可上 NPU 编译")
                + f" | 全图算子 {len(ops)} 种")
            # C11 动态 shape: NPU 编译器要求静态输入
            dimv = list(m["inputs"].values())[0] if m["inputs"] else []
            dyn = [d for d in dimv if isinstance(d, str)]
            add("C11", not dyn,
                f"输入 shape = {dimv} "
                + ("→ 动态维度, NPU 编译器拒收 (须固化)"
                   if dyn else "→ 静态 shape ✓"))
            # C12 台账登记的 npu_ready 标记与实测是否一致
            declared = a.get("npu_ready")
            if declared is None:
                add("C12", None, "台账未登记 npu_ready 标记 (非交付集资产, 不阻断)")
            else:
                add("C12", bool(declared) == (not risky and not dyn),
                    f"台账 npu_ready = {bool(declared)} | 实测: 高风险算子 "
                    f"{len(risky)} 种, 动态维度 {len(dyn)} 个")
            # C13 实测精度 (G3)
            acc = a.get("measured_acc")
            if not acc:
                add("C13", None,
                    "★ 台账未登记实测精度 (measured_acc) → 量产放行阻断项 L7")
            else:
                ok_acc = (acc.get("f1", 0) >= ACC_MIN_F1
                          and acc.get("images", 0) >= ACC_MIN_IMAGES)
                add("C13", ok_acc,
                    f"实测精度: P={acc.get('prec')} R={acc.get('rec')} "
                    f"F1={acc.get('f1')} @IoU={acc.get('iou')} "
                    f"({acc.get('images')} 张, {acc.get('dataset')}) "
                    f"门限 F1≥{ACC_MIN_F1} / ≥{ACC_MIN_IMAGES} 张")

    if a["fmt"] == "nb":
        h = read_nbg_header(p)
        add("C5", h.get("magic") == "VPMN", f"magic = {h.get('magic')!r} (期望 'VPMN')")
        add("C6", h.get("format") in (1, 2), f"NBG format version = {h.get('format')}")
        chip = h.get("chip")
        if a.get("expected_chip") is not None:
            ok = chip == a["expected_chip"]
            if ok:
                add("C7", True, f"target chip ID = 0x{chip:08X} (期望 0x{a['expected_chip']:08X})")
            elif a["state"] == "quarantined":
                add("C7", None,
                    f"target chip ID = 0x{chip:08X} ≠ 0x{a['expected_chip']:08X} "
                    f"→ 已隔离 (state=quarantined): 板端加载后报 SRAM size 错, 不可用")
            else:
                add("C7", False,
                    f"target chip ID = 0x{chip:08X} (期望 0x{a['expected_chip']:08X})"
                    f"  ★ chip ID 错 → 板端加载后报 SRAM size 错")
        else:
            add("C7", True, f"target chip ID = 0x{chip:08X}")

    return res


def duplicate_scan() -> list:
    """同 sha256 不同 id → 名字骗人"""
    by_hash = {}
    for a in MANIFEST:
        if a["fmt"] == "dir" or not a.get("sha256_16"):
            continue
        by_hash.setdefault(a["sha256_16"], []).append(a["id"])
    return [(h, ids) for h, ids in by_hash.items() if len(ids) > 1]


def count_release_blockers(results: list) -> list:
    """量产放行阻断项 —— **只算交付集 (state = candidate / active)**。
       reference / quarantined / licensing-hold 不进交付集, 但会在输出里单列,
       不许静默消失 (ISS-087)。

       L1 许可未判定 (台账 expected_license 为空)
       L2 板端产物超 15 MiB 槽位
       L3 chip ID 与目标 NPU 不符
       L4 许可为 AGPL-3.0 且无 Enterprise 授权记录 → 商用受阻
       L5 交付集资产的 PC 侧推理冒烟失败 (模型本身是坏的)
       --- ISS-101 新增 ---
       L6 交付集资产含 NPU 不支持算子 (NMS/TopK/Range/NonZero) 或动态 shape
          → NPU 编译器拒收, 模型上不了板
       L7 交付集资产无实测精度 (measured_acc 未登记 / 低于门限)
       L8 交付集无任何 NPU 就绪产物 (转换链第 1/2 段没跑通)
    """
    out = []
    by_id = {a["id"]: a for a in MANIFEST}
    for r in results:
        if r["state"] not in ("candidate", "active"):
            continue
        a = by_id.get(r["id"], {})
        lic_state = a.get("license_state", "unknown")
        for code, ok, msg in r["checks"]:
            if code == "C5" and ok is None and "许可未判定" in msg:
                out.append(("L1 许可未判定", r["id"], msg))
            if code == "C4" and ok is False:
                out.append(("L2 超 15MiB 槽位", r["id"], msg))
            if code == "C7" and ok is False:
                out.append(("L3 chip ID 不符", r["id"], msg))
            if code == "C9" and ok is False:
                out.append(("L5 PC 侧推理冒烟失败", r["id"], msg))
            if code == "C10" and ok is False:
                out.append(("L6 含 NPU 不支持算子", r["id"], msg))
            if code == "C11" and ok is False:
                out.append(("L6 动态 shape", r["id"], msg))
            if code == "C13" and (ok is False or ok is None):
                out.append(("L7 无实测精度", r["id"], msg))
        if lic_state == "agpl-no-grant":
            out.append(("L4 许可商用受限(AGPL)", r["id"],
                        f"许可 = {a.get('expected_license')!r} 且无 Enterprise 授权记录 "
                        f"→ 商用受阻: 须向 Ultralytics 采购 Enterprise License, "
                        f"或改用许可干净的模型栈 (SW/MODEL_LICENSE.md §3)"))
    # L8: 交付集里至少要有 1 条 npu_ready 产物 (转换链第 1/2 段跑通)
    ship = [r for r in results if r["state"] in ("candidate", "active")]
    if ship and not any(by_id.get(r["id"], {}).get("npu_ready") for r in ship):
        out.append(("L8 交付集无 NPU 就绪产物", "(全体)",
                    "交付集里没有任何 npu_ready=True 的资产 → "
                    "TF/ONNX → NPU 转换链第 1/2 段未跑通 → 不许进量产评审"))
    return out


def print_human(results: list, dups: list) -> None:
    print("=" * 100)
    print("模型资产登记检查器 (ISS-037/ISS-087) — SW/MODEL_ASSETS.md §1 台账机器复核")
    print("=" * 100)
    by_id = {a["id"]: a for a in MANIFEST}
    ship = [r for r in results if r["state"] in ("candidate", "active")]
    hold = [r for r in results if r["state"] == "licensing-hold"]
    quar = [r for r in results if r["state"] == "quarantined"]
    ref = [r for r in results if r["state"] == "reference"]
    for r in results:
        a = by_id.get(r["id"], {})
        print(f"\n▶ {r['id']}  [{r['fmt']} | {r['platform']} | {r['state']}]")
        print(f"  {r['path']}")
        print(f"  许可: {a.get('expected_license')!r} · license_state="
              f"{a.get('license_state')} · license_grant={a.get('license_grant')!r}")
        for code, ok, msg in r["checks"]:
            mark = "✅" if ok is True else ("❌" if ok is False else "⚠️ ")
            print(f"    {mark} {code}  {msg}")
    if dups:
        print("\n▶ C8 重复资产 (sha256 相同但 id 不同 → 文件名里的版本号不可信)")
        for h, ids in dups:
            print(f"    ⚠️  C8  sha256[:16]={h} → {', '.join(ids)}")
    n_fail = sum(1 for r in results for c, ok, _ in r["checks"] if ok is False)
    n_warn = sum(1 for r in results for c, ok, _ in r["checks"] if ok is None)
    blockers = count_release_blockers(results)
    print("\n" + "-" * 100)
    print(f"汇总: 资产 {len(results)} 条 · FAIL {n_fail} · WARN {n_warn} · 重复组 {len(dups)}")
    print(f"交付集 (candidate/active): {len(ship)} 条 | licensing-hold: {len(hold)} 条 | "
          f"quarantined: {len(quar)} 条 | reference: {len(ref)} 条")
    print(f"量产放行阻断项 (L): {len(blockers)} 条 "
          f"{'→ ✅ 放行阻断项已清零 (★不等于有可用模型: 量产可用模型清单见 SW/MODEL_RELEASE_GATE.md)' if not blockers else '→ ❌ 不许进量产评审 (见 §1.5)'}")
    if not blockers:
        print("   ★ 交付集里的模型是否**真的能上板**是另一件事 (NPU 可转换性 = 板端产物 + 板端实测): "
              "交付集现在只有 1 条 Apache-2.0 候选, 其 NPU 可转换性 = [0数据] → 量产可用模型清单 = 空 (ISS-101)")
    for tag, aid, msg in blockers:
        print(f"    - {tag}  [{aid}]  {msg}")
    if hold:
        print("\n▶ licensing-hold (许可受限, 未采购前**禁入交付物**; 采购后可复活)")
        for r in hold:
            a = by_id.get(r["id"], {})
            print(f"    - {r['id']}: 许可 {a.get('expected_license')!r} "
                  f"→ 须向 Ultralytics 采购 Enterprise License, 或改用 Apache-2.0 栈")
    if quar:
        print("\n▶ quarantined (已判死, 不进任何流程)")
        for r in quar:
            why = [f"{c}: {m[:110]}" for c, ok, m in r["checks"]
                   if ok is False or (ok is None and ("失败" in m or "不存在" in m))]
            print(f"    - {r['id']}: " + ("; ".join(why) if why else "(登记为已隔离)"))
    print(f"退出码 rc = {1 if n_fail else 0}")
    print("-" * 100)


def cmd_new(path: str) -> int:
    """新模型入库: 打印台账行骨架 + 头部信息"""
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}")
        return 2
    sz = os.path.getsize(path)
    sha = sha256_of(path)
    print("--- 台账行骨架 (贴进 SW/MODEL_ASSETS.md §1.2) ---")
    print("    {")
    print('        "id": "MOD-<NAME>-<VER>",')
    print('        "platform": "candidate",')
    print('        "state": "candidate",')
    print('        "role": "<角色>",')
    print(f'        "path": "{os.path.abspath(path)}",')
    print(f'        "size": {sz},')
    print(f'        "sha256_16": "{sha[:16]}",')
    print('        "expected_license": <metadata_props 取; 取不到就用 '
          'SW/tools/license_probe.py 溯源判定>,')
    print('        "license_state": "permissive|agpl-granted|agpl-no-grant|unknown",')
    print('        "license_grant": <Enterprise 授权记录号; 无则 null>,')
    print('        "expected_opset": <null>,')
    print('        "expected_input": <null>,')
    print('        "expected_chip": <null>,')
    print('        "note": "...",')
    print("    },")
    print("--- 头部信息 ---")
    if path.endswith((".nb", ".nbg")):
        print(f"size = {sz} B ({sz/1048576:.2f} MiB) · 板端槽位门禁 15 MiB: "
              f"{'PASS' if sz <= MODEL_SLOT_BYTES else 'FAIL (超槽位, 刷不进去)'}")
    else:
        print(f"size = {sz} B ({sz/1048576:.2f} MiB) · PC 侧源文件, 不受 15 MiB 板端槽位门禁 "
              f"(门禁管转换后的 .nb)")
    print(f"sha256 = {sha}")
    if path.endswith(".onnx"):
        m = onnx_meta(path)
        if "_err" not in m:
            print(f"producer = {m['producer']} · opset = {m['opset']} · "
                  f"nodes = {m['n_nodes']} · 算子类型 = {m['n_op_types']}")
            print(f"license = {m.get('license')!r}  ← null = metadata 没写, "
                  f"不代表许可未知: 用 SW/tools/license_probe.py 溯源判定")
            print(f"inputs  = {m['inputs']}")
            print(f"outputs = {m['outputs']}")
    if path.endswith((".nb", ".nbg")):
        h = read_nbg_header(path)
        print(f"NBG header: magic={h['magic']!r} version=0x{h['version']:04X} "
              f"format={h['format']} chip=0x{h['chip']:08X}")
        print("  ★ chip ID 必须等于目标 NPU 的真实 chip ID (A733 = 0x1000003B); "
              "ARS45 的 chip ID 未知 → [0数据]")
    return 0


def main() -> int:
    global SMOKE
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--id", default=None, help="只检查某一条资产 id")
    ap.add_argument("--new", default=None, help="新模型入库: 打印台账行骨架")
    ap.add_argument("--no-smoke", action="store_true", help="跳过 C9 PC 侧推理冒烟 (更快)")
    args = ap.parse_args()

    if args.no_smoke:
        SMOKE = False

    if args.new:
        return cmd_new(args.new)

    assets = MANIFEST
    if args.id:
        assets = [a for a in MANIFEST if a["id"] == args.id]
        if not assets:
            print(f"❌ 未知 id: {args.id}")
            return 2

    results = [check_one(a) for a in assets]
    dups = duplicate_scan()

    if args.json:
        print(json.dumps({
            "model_slot_mib": MODEL_SLOT_MIB,
            "ship_set": [r["id"] for r in results if r["state"] in ("candidate", "active")],
            "licensing_hold": [r["id"] for r in results if r["state"] == "licensing-hold"],
            "assets": results,
            "duplicates": dups,
            "release_blockers": count_release_blockers(results),
        }, ensure_ascii=False, indent=2, default=str))
    else:
        print_human(results, dups)

    n_fail = sum(1 for r in results for c, ok, _ in r["checks"] if ok is False)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
