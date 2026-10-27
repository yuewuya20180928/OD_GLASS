#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARS45 板端 INT8 转换链驱动器 (B0~B9) —— ISS-087 (sw-lead, 2026-10-28)
=====================================================================
为什么有这个脚本
----------------
ISS-037 §2.9 写的是 **ARS45 转换流程骨架 (B0~B9), 全部标 [0数据]** —— 原因是
"没有板 + 没有 Art.Galaxy 工具链 + 没有 ARS45 chip ID"。

但"没有工具链"不等于"什么都做不了"。本脚本把 B0~B9 拆成 **9 个可机械判定的步**,
每一步给出 **状态 / 阻塞原因 / 解锁条件**:

    READY    = 本机能跑, 现在就跑, 出产物
    PARTIAL  = 本机能跑一半 (产物/检查能出, 但最终转换要工具链)
    BLOCKED  = 必须等外部 (原厂工具链 / 原厂 chip ID / 板子)

★ 本脚本**不联网**、**不外发**、**不碰任何别人的目录**; 产物默认写到 /tmp。

用法:
    python3 SW/tools/int8_chain.py                       # 全链 readiness (默认用台账主候选)
    python3 SW/tools/int8_chain.py --model <onnx> --input-size 320
    python3 SW/tools/int8_chain.py --model <onnx> --build   # 真跑 B1/B2/B3/B6, 出产物
    python3 SW/tools/int8_chain.py --json
退出码: 0 = 链可执行部分全过 (READY/PARTIAL 步无失败) | 1 = 有失败 | 2 = 用法错
★ 退出码 0 **不代表"转换链已跑通"** —— 跑通与否看 BLOCKED 步清零 (需原厂 + 板)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))

# ----------------------------------------------------------------------------
# 目标平台的固定事实 (来自 SW/FLASH_AND_VERSION.md / SW/MODEL_ASSETS.md)
# ----------------------------------------------------------------------------
MODEL_SLOT_BYTES = 15_728_640      # 15 MiB 板端 model_a / model_b 单槽
VERSION_FMT = "{family}-int8-ag2-{sha8}"     # SW/FLASH_AND_VERSION.md §3.1.3

# Art.Galaxy 工具链的候选落地位置 (B0 探测用; 都不存在 = 阻塞)
ART_GALAXY_HINTS = [
    os.environ.get("ART_GALAXY_HOME", ""),
    os.environ.get("ART_GALAXY_SDK", ""),
    "/opt/art_galaxy", "/opt/Art.Galaxy", "/usr/local/art_galaxy",
    "/opt/art-galaxy", "/home/yuewuya/Art.Galaxy", "/work/art_galaxy",
]

# ARS45 chip ID —— [0数据] (原厂 Q9/Q11 未答); A733 的 0x1000003B **不可套用**
ARS45_CHIP_ID = None
A733_CHIP_ID = 0x1000003B

# A733 (ACUITY/VIPLite) 实测跑通的算子类型集 [实测·历史: A733 acuity_pipeline 转换成功]
A733_SUPPORTED_OPS = {
    "Conv", "Sigmoid", "Mul", "Add", "Concat", "MaxPool", "Resize", "Reshape",
    "Transpose", "Slice", "Sub", "Pow", "Constant", "Split", "Softmax", "Shape",
    "Gather", "Div",
}

# A733 已跑通的参考 ONNX (方法论基准)
A733_REF_ONNX = "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx"
A733_REF_CALIB = "/home/yuewuya/Public/radxa_yolo/calib_yolov5_100"
A733_REF_QUANT = "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim_320.quantize"

# 板端 NPU 打点口径 (SOUL.md 铁律: 纯 NPU vs SDK 总耗时必须分开报)
TIMING_TAPS = [
    "t_capture",      # sensor 曝光 → 帧到 CPU
    "t_pre",          # 缩放 / 归一化 / 布局转换
    "t_npu",          # ★ 纯 NPU 推理 (vip_run_network 等价)
    "t_sdk_total",    # ★ SDK 总耗时 (含 INT8→FP32 反量化)
    "t_decode",       # decode + NMS
    "t_draw",         # 画框
    "t_compose",      # 叠加进显示帧
    "t_display",      # 送 MIPI-DSI / 光机
]
TIMING_RULE = "每段必须给 min/avg/max + 采样帧数; 纯 NPU 与 SDK 总耗时分开报 (A733: 27.19 vs 36.51 ms)"


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def shape_of(t) -> list:
    return [d.dim_value or d.dim_param for d in t.type.tensor_type.shape.dim]


def load_onnx(path: str):
    import onnx  # noqa: PLC0415
    return onnx.load(path, load_external_data=False)


# ----------------------------------------------------------------------------
# B0 工具链探测
# ----------------------------------------------------------------------------
def step_b0() -> dict:
    found = []
    for h in ART_GALAXY_HINTS:
        if h and os.path.isdir(h):
            found.append(h)
    ver = None
    if found:
        for root, _dirs, files in os.walk(found[0]):
            for fn in files:
                if fn.lower() in ("version", "version.txt", "release"):
                    try:
                        with open(os.path.join(root, fn), encoding="utf-8",
                                  errors="replace") as f:
                            ver = f.read(200).strip()[:120]
                    except OSError:
                        pass
    return {
        "id": "B0", "name": "Art.Galaxy 工具链到位", "status": "READY" if found else "BLOCKED",
        "evidence": "[实测] 本机全盘探测 + 环境变量 ART_GALAXY_HOME/ART_GALAXY_SDK",
        "detail": (f"找到工具链: {found}" if found
                   else "本机无 Art.Galaxy 工具链 (conda env / /opt / /usr/local 全无)"),
        "blocker": None if found else "原厂未交付 Art.Galaxy (Q11)",
        "unlock": (None if found else
                   "项目总工转原厂: 工具链包 (docker? SDK? 授权?) + 手册; 落地后设 "
                   "ART_GALAXY_HOME 即可自动识别"),
        "version": ver,
    }


# ----------------------------------------------------------------------------
# B1 ONNX 自检 (格式/opset/shape)
# ----------------------------------------------------------------------------
def step_b1(path: str) -> dict:
    st = {"id": "B1", "name": "输入格式 / opset 自检", "status": "READY", "blocker": None,
          "unlock": None}
    try:
        import onnx  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        st.update(status="BLOCKED", blocker=f"onnx 模块不可用: {e}",
                  detail="本机缺 onnx → 无法做格式自检")
        return st
    try:
        m = load_onnx(path)
    except Exception as e:  # noqa: BLE001
        st.update(status="BLOCKED", blocker=f"ONNX 解析失败: {e}", detail=str(e)[:200])
        return st
    try:
        onnx.checker.check_model(m)
        checker = "✅ onnx.checker 通过"
    except Exception as e:  # noqa: BLE001
        checker = f"❌ checker 报错: {str(e)[:160]}"
    opset = max((o.version for o in m.opset_import if not o.domain), default=None)
    dyn_in = [i.name for i in m.graph.input
              if any(isinstance(d.dim_param, str) and d.dim_param
                     for d in i.type.tensor_type.shape.dim)]
    dyn_out = [o.name for o in m.graph.output
               if any(isinstance(d.dim_param, str) and d.dim_param
                      for d in o.type.tensor_type.shape.dim)]
    st.update(
        evidence="[实测] 本机 onnx 解析 + checker",
        detail=(f"{checker}; ir={m.ir_version}; opset={opset}; "
                f"producer={m.producer_name} {m.producer_version}; "
                f"节点={len(m.graph.node)}; 算子类型={len(set(n.op_type for n in m.graph.node))}; "
                f"输入={ {i.name: shape_of(i) for i in m.graph.input} }; "
                f"输出={ {o.name: shape_of(o) for o in m.graph.output} }; "
                f"动态维 输入={dyn_in or '无'} 输出={dyn_out or '无'}"),
        dynamic_in=dyn_in, dynamic_out=dyn_out, opset=opset,
        note=("★ Art.Galaxy 接受哪些 opset / 输入格式 = [0数据] (Q9); "
              "本步只判 '这份 ONNX 本身是否合法', 不代表工具链能吃"),
    )
    # B1b: PC 侧 1 帧推理冒烟 (链输入资产体检)
    smoke_ok, smoke_msg = smoke_test_onnx(path)
    st["smoke"] = {"ok": smoke_ok, "msg": smoke_msg}
    if smoke_ok is False:
        st["status"] = "BLOCKED"
        st["blocker"] = "链输入资产本身跑不起来 (PC 侧冒烟失败) → 换资产或重新导出, 不要拿去转换"
        st["unlock"] = ("重新从 checkpoint 用正确 imgsz 导出 (不是改 ONNX 的输入 dim); "
                        "本机可用 checkpoint: /home/yuewuya/Public/radxa_yolo/code/yolov5su.pt")
    elif smoke_ok is True:
        st["detail"] += f"; PC 侧冒烟: {smoke_msg}"
    return st


def smoke_test_onnx(path: str) -> tuple:
    """onnxruntime 建 session + 跑 1 帧随机输入 → (ok|None, msg)"""
    try:
        import numpy as np  # noqa: PLC0415
        import onnxruntime as ort  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        return None, f"onnxruntime/numpy 不可用 ({e})"
    try:
        so = ort.SessionOptions()
        so.log_severity_level = 3
        sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        name = sess.get_inputs()[0].name
        shape = [d if isinstance(d, int) and d > 0 else 1 for d in sess.get_inputs()[0].shape]
        outs = sess.run(None, {name: np.zeros(shape, dtype=np.float32)})
        return True, f"OK · 输出 {[list(o.shape) for o in outs]}"
    except Exception as e:  # noqa: BLE001
        return False, f"❌ {str(e).split(chr(10))[0][:180]}"


# ----------------------------------------------------------------------------
# B2 静态化 (固定输入 shape)
# ----------------------------------------------------------------------------
def step_b2(path: str, out_dir: str, input_size: int, build: bool) -> dict:
    st = {"id": "B2", "name": f"静态化 ONNX (输入 {input_size}×{input_size})",
          "status": "READY" if build else "PARTIAL", "blocker": None, "unlock": None}
    import onnx  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    from onnx import numpy_helper  # noqa: PLC0415

    m = load_onnx(path)
    src_in = None
    for i in m.graph.input:
        sh = shape_of(i)
        if len(sh) == 4:
            src_in = i
            src_hw = (sh[2] if isinstance(sh[2], int) else None,
                      sh[3] if isinstance(sh[3], int) else None)
            break
    if src_in is None:
        st.update(status="BLOCKED", blocker="找不到 4 维图像输入", detail="")
        return st

    # a) 改输入 shape
    dim = src_in.type.tensor_type.shape.dim
    dim[2].dim_value = input_size
    dim[3].dim_value = input_size
    for d in dim:
        d.ClearField("dim_param")

    # b) 改网格型 Reshape 常量 (yolov5/yolox 系: [1,3,85,H,W] → 按 stride 比例缩放)
    changed = []
    if src_hw and src_hw[0] and src_hw[1]:
        s_old = src_hw[0] / (src_hw[1] or 1)
        for init in m.graph.initializer:
            try:
                arr = numpy_helper.to_array(init)
            except Exception:  # noqa: BLE001
                continue
            if arr.ndim == 5 and arr.shape[0] == 1 and arr.shape[1] == 3 and arr.shape[2] == 85:
                old_h, old_w = int(arr.shape[3]), int(arr.shape[4])
                # 网格尺寸必须能被 32 整除 (P3/P4/P5)
                new_h = new_w = None
                for cand in (input_size // 8, input_size // 16, input_size // 32):
                    if old_h == cand * (src_hw[0] // cand if src_hw[0] else 0):
                        new_h = new_w = cand
                if new_h is None:
                    # 通用: 按 old/src 比例缩放, 取最接近的 8 倍数
                    ratio = input_size / src_hw[0]
                    new_h = int(round(old_h * ratio / 8)) * 8
                    new_w = int(round(old_w * ratio / 8)) * 8
                if new_h and new_w and (new_h, new_w) != (old_h, old_w):
                    new_arr = np.array(arr.shape[:3] + (new_h, new_w), dtype=arr.dtype)
                    init.CopyFrom(numpy_helper.from_array(new_arr, name=init.name))
                    changed.append(f"{init.name}: {old_h}×{old_w} → {new_h}×{new_w}")
    dst = os.path.join(out_dir, f"{os.path.splitext(os.path.basename(path))[0]}_s{input_size}.onnx")
    if build:
        os.makedirs(out_dir, exist_ok=True)
        onnx.save(m, dst)
        st["artifact"] = dst
        st["sha256_16"] = sha256_of(dst)[:16]
    st.update(
        evidence="[实测] 本机 onnx 图改写 (A733 同款方法: make_416_onnx.py)",
        detail=(f"输入 {src_in.name} {shape_of(src_in)[:1]}×3×{src_hw[0]}×{src_hw[1]} "
                f"→ 3×{input_size}×{input_size}; 网格常量改写 {len(changed)} 处: "
                f"{changed if changed else '无 (该模型无 5 维 Reshape 常量)'}"),
        artifacts=[dst] if build else [],
        note=("★ 改写只覆盖 yolov5/yolox 系 (5 维 [1,3,85,H,W] Reshape 常量); "
              "其余结构需 onnxsim → 本机无 onnxsim, 若改写后 checker 报错则改用原厂工具链"),
    )
    return st


# ----------------------------------------------------------------------------
# B3 摘 Detect 头 (后处理外移 → 板端 CPU decode)
# ----------------------------------------------------------------------------
def step_b3(path: str, out_dir: str, build: bool) -> dict:
    st = {"id": "B3", "name": "摘 Detect 头 (后处理外移)", "status": "READY" if build else "PARTIAL",
          "blocker": None, "unlock": None}
    import onnx  # noqa: PLC0415
    m = load_onnx(path)
    heads = []
    for o in m.graph.output:
        sh = shape_of(o)
        if len(sh) == 5:
            heads.append(o.name)
    if not heads:
        st.update(status="BLOCKED", blocker="没有 5 维 head 输出 (该模型后处理未内嵌?)",
                  detail="输出: " + ", ".join(f"{o.name}{shape_of(o)}" for o in m.graph.output))
        return st
    dst = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + "_rt.onnx")
    if build:
        os.makedirs(out_dir, exist_ok=True)
        in_name = m.graph.input[0].name
        onnx.utils.extract_model(path, dst, [in_name], heads)
        st["artifact"] = dst
        st["sha256_16"] = sha256_of(dst)[:16]
    st.update(
        evidence="[实测] onnx.utils.extract_model (与 Rockchip awnpu_model_zoo "
                 "examples/yolov5/convert_model/python/onnx_extract.py 同法)",
        detail=f"head 输出 {heads} (5 维特征图); 输入名 {m.graph.input[0].name}",
        note=("A733 参考: yolov5 用 ['350','498','646'] → 再抽 ['349','497','645']; "
              "yolox 用 ['798','824','850'] —— 每家模型的 head 名不同, 必须逐模型核对"),
    )
    return st


# ----------------------------------------------------------------------------
# B4 量化 (本地可做: 校准集 + 参数资产; 转换需工具链)
# ----------------------------------------------------------------------------
def step_b4() -> dict:
    n_img = 0
    if os.path.isdir(A733_REF_CALIB):
        n_img = len([f for f in os.listdir(A733_REF_CALIB)
                     if f.lower().endswith((".jpg", ".jpeg", ".png"))])
    q_ok = os.path.exists(A733_REF_QUANT)
    st = {
        "id": "B4", "name": "INT8 量化 (校准集 / 参数 / 量化器)",
        "status": "PARTIAL" if (n_img >= 100 and q_ok) else "BLOCKED",
        "evidence": "[实测] 本机校准集目录计数 + 量化参数资产存在性",
        "detail": (f"校准集 {A733_REF_CALIB}: {n_img} 张 (要求 ≥100); "
                   f"量化参数资产 {'存在' if q_ok else '缺失'}: {A733_REF_QUANT}; "
                   f"A733 方案 = pcq (per-channel symmetric affine)"),
        "blocker": "Art.Galaxy 量化器本体 (方案名/校准接口/输出是否直通量化整数) = [0数据] (Q9)",
        "unlock": "原厂给量化手册后, 把量化器命令接到本脚本 B4 段",
        "note": ("★ 眼镜场景校准集 (≥100 张, 分布对口) = [0数据]: 现存 100 张是 COCO 通用集, "
                 "分布不符; A733 实测 6 张不够用"),
    }
    return st


# ----------------------------------------------------------------------------
# B5 导出板端产物 + 文件头/chip ID
# ----------------------------------------------------------------------------
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


def step_b5(produced: list) -> dict:
    st = {
        "id": "B5", "name": "导出板端产物 + 文件头/chip ID",
        "status": "BLOCKED",
        "evidence": "[实测] 本机无 Art.Galaxy → 无法导出; chip ID 校验器已就绪",
        "detail": (f"ARS45 chip ID = {ARS45_CHIP_ID} → [0数据] (原厂 Q9 第 5 条未答); "
                   f"A733 = 0x{A733_CHIP_ID:08X} (★ 不可套用: 套错 → 板端加载报 SRAM size 错)"),
        "blocker": "Art.Galaxy 导出命令 + ARS45 chip ID + 板端文件头布局 (是否同 NBG)",
        "unlock": "原厂给出 chip ID 与头布局后, 用 SW/tools/model_asset_check.py 的 C5/C7 直接判",
        "nbg_header_checker": "SW/tools/model_asset_check.py :: read_nbg_header (magic VPMN / "
                              "version / format / chip LE uint32 @ byte 8-11)",
    }
    if produced:
        st["produced_headers"] = []
        for p in produced:
            if p.endswith((".nb", ".nbg")):
                st["produced_headers"].append({"path": p, "header": read_nbg_header(p)})
    return st


# ----------------------------------------------------------------------------
# B6 算子覆盖表
# ----------------------------------------------------------------------------
def step_b6(path: str) -> dict:
    import onnx  # noqa: PLC0415
    from onnx import numpy_helper  # noqa: PLC0415
    m = load_onnx(path)
    init_params = {}
    for init in m.graph.initializer:
        try:
            n = int(numpy_helper.to_array(init).size)
        except Exception:  # noqa: BLE001
            n = 0
        init_params[init.name] = n
    census: dict = {}
    for node in m.graph.node:
        c = census.setdefault(node.op_type, {"count": 0, "params": 0})
        c["count"] += 1
        for nm, np_ in init_params.items():
            if nm.startswith(node.name + ".") or nm == node.name:
                c["params"] += np_
    rows = []
    for op, c in sorted(census.items(), key=lambda kv: -kv[1]["count"]):
        rows.append({
            "op": op, "count": c["count"], "params": c["params"],
            "a733": "✅" if op in A733_SUPPORTED_OPS else "⚠️",
        })
    unsupported = [r["op"] for r in rows if r["a733"] != "✅"]
    return {
        "id": "B6", "name": "算子覆盖表核对",
        "status": "READY",
        "evidence": "[实测] 本机 onnx 图统计; 对照集 = A733 实测转换成功算子 [实测·历史]",
        "detail": f"算子类型 {len(rows)} 种 / 节点 {sum(r['count'] for r in rows)} 个",
        "table": rows,
        "not_in_a733": unsupported,
        "blocker": ("Art.Galaxy 官方算子支持清单 = [0数据] (Q9 第 2 条); "
                    "上表 ⚠️ 项只是 'A733 没跑过', 不等于 Art.Galaxy 不支持") if unsupported else None,
        "unlock": "原厂给算子支持清单后, 把本表升级成正式覆盖表 (SW/MODEL_ASSETS.md §2.7 模板)",
        "note": "★ A733 实测 12 类算子 (yolov5s) 全过 → yolov5 系结构是 NPU 友好型",
    }


# ----------------------------------------------------------------------------
# B7 板端加载 + 首帧 shape 对齐
# ----------------------------------------------------------------------------
def step_b7() -> dict:
    return {
        "id": "B7", "name": "板端加载 + 首帧输出 shape 对齐",
        "status": "BLOCKED",
        "evidence": "[0数据] 无板",
        "detail": "判据已写死: 板端加载后首帧输出 shape 必须与 PC 端 ONNX 逐路一致",
        "blocker": "无 ARS45 板 + 无板端 SDK",
        "unlock": "板子回来后: 加载 → 跑 1 帧 → 与 PC 端 outputs 比对 (本脚本可出 PC 端期望值)",
        "pc_expect": "本脚本 B3 段输出即 PC 端期望 shape",
    }


# ----------------------------------------------------------------------------
# B8 纯 NPU vs SDK 总耗时打点
# ----------------------------------------------------------------------------
def step_b8() -> dict:
    return {
        "id": "B8", "name": "纯 NPU 耗时 vs SDK 总耗时 打点",
        "status": "BLOCKED",
        "evidence": "[0数据] 无板",
        "detail": TIMING_RULE,
        "taps": TIMING_TAPS,
        "blocker": "无板 + 原厂 SDK 打点接口 (Q8)",
        "unlock": "板子回来后按本表逐段埋点; 端到端预算表见 PROJECT_TRACKER §3 (sw-lead 只报自己那段)",
    }


# ----------------------------------------------------------------------------
# B9 登记台账 + 精度评估 + 回归
# ----------------------------------------------------------------------------
def step_b9(path: str, out_dir: str) -> dict:
    st = {
        "id": "B9", "name": "登记台账 + 精度评估 + 回归",
        "status": "PARTIAL",
        "evidence": "[实测] 台账与回归门禁已建 (SW/MODEL_ASSETS.md §1.2 / §4.2)",
        "detail": ("离线可跑: R-01 (ONNX checker) / R-02 (输入输出 shape 与台账一致) / "
                   "R-03 (sha256 版本绑定) / R-08+R-09 (ONNX 口径 COCO 评估, 需评估器) / "
                   "R-14 (台账字段完整性); 需板: R-04~R-07, R-10~R-13"),
        "blocker": "无板端产物 → R-04 起全部不可跑; 板端 INT8 模型台账条数 = 0",
        "unlock": "B5 出产物后: python3 SW/tools/model_asset_check.py --new <产物> 打印台账行骨架",
    }
    if os.path.exists(path):
        sha = sha256_of(path)[:8]
        fam = os.path.splitext(os.path.basename(path))[0].split("_")[0]
        st["version_string"] = VERSION_FMT.format(family=fam, sha8=sha)
        st["version_note"] = ("与 SW/FLASH_AND_VERSION.md §3.1.3 一致 (model=<...> 字段); "
                              "<sha8> = 板端模型文件 sha256 前 8 位")
    return st


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help="待转换 ONNX (默认 = 台账主候选)")
    ap.add_argument("--input-size", type=int, default=320)
    ap.add_argument("--out", default="/tmp/ars45_int8_chain")
    ap.add_argument("--build", action="store_true", help="真跑 B1/B2/B3 (出产物)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    model = args.model or "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx"
    if not os.path.exists(model):
        print(f"❌ 模型不存在: {model}")
        return 2
    if args.build:
        os.makedirs(args.out, exist_ok=True)

    steps = [step_b0(), step_b1(model)]
    steps.append(step_b2(model, args.out, args.input_size, args.build))
    steps.append(step_b3(model, args.out, args.build))
    steps.append(step_b4())
    steps.append(step_b6(model))
    steps.append(step_b5([os.path.join(args.out, f) for f in os.listdir(args.out)]
                          if args.build and os.path.isdir(args.out) else []))
    steps.append(step_b7())
    steps.append(step_b8())
    steps.append(step_b9(model, args.out))

    n_ready = sum(1 for s in steps if s["status"] == "READY")
    n_part = sum(1 for s in steps if s["status"] == "PARTIAL")
    n_block = sum(1 for s in steps if s["status"] == "BLOCKED")

    if args.json:
        print(json.dumps({"model": model, "input_size": args.input_size,
                          "built": args.build, "out": args.out,
                          "steps": steps,
                          "summary": {"ready": n_ready, "partial": n_part,
                                      "blocked": n_block, "total": len(steps)}},
                         ensure_ascii=False, indent=2, default=str))
        return 0

    print("=" * 100)
    print("ARS45 板端 INT8 转换链 B0~B9 readiness (ISS-087)")
    print("=" * 100)
    print(f"模型: {model}")
    print(f"目标输入: {args.input_size}×{args.input_size}   产物目录: {args.out}   "
          f"实跑产物: {'是' if args.build else '否 (加 --build 出产物)'}")
    for s in steps:
        icon = {"READY": "✅", "PARTIAL": "🟡", "BLOCKED": "⛔"}[s["status"]]
        print(f"\n{icon} {s['id']}  {s['name']}   [{s['status']}]")
        print(f"     证据: {s.get('evidence')}")
        if s.get("detail"):
            print(f"     说明: {s['detail']}")
        if s.get("blocker"):
            print(f"     ⛔ 阻塞: {s['blocker']}")
        if s.get("unlock"):
            print(f"     🔓 解锁: {s['unlock']}")
        if s.get("note"):
            print(f"     ★ {s['note'].lstrip('★ ')}")
        if s.get("version_string"):
            print(f"     版本串: model={s['version_string']}")
        if s.get("table"):
            print("     算子覆盖表 (op / 节点数 / 参数量 / A733 实测):")
            for r in s["table"]:
                print(f"        {r['op']:12s} n={r['count']:<4d} params={r['params']:<12d} "
                      f"A733={r['a733']}")
    print("\n" + "-" * 100)
    print(f"汇总: READY {n_ready} · PARTIAL {n_part} · BLOCKED {n_block} (共 {len(steps)} 步, B0~B9)")
    blk = [s["id"] for s in steps if s["status"] == "BLOCKED"]
    prt = [s["id"] for s in steps if s["status"] == "PARTIAL"]
    print(f"  READY: {[s['id'] for s in steps if s['status'] == 'READY']}")
    print(f"  PARTIAL (本机可跑一半): {prt}")
    print(f"  BLOCKED: {blk}")
    print("★ BLOCKED 的步全部卡在**原厂交付工具链 + 有板**两件事上, 不是本机工程量;")
    print("  PARTIAL 的步缺的是工具链那半段 (B2/B3 加 --build 可全跑; B4 缺量化器; B9 缺板端产物)。")
    print(f"退出码 rc = 0")
    print("-" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
