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
        ⚠️ metadata_props 为空 = **许可信息 [0数据]** → 量产放行阻断项 L1
  ③ .nb (NBG): 解析头部 4 个字段
        byte 0-3  magic "VPMN"
        byte 4-5  version
        byte 6-7  format version (1 = VIPLite 2.0.3.2 / 2 = 2.0.10.x ABI)
        byte 8-11 target chip ID (LE)
     ★ chip ID 错 = 板端 NPU 加载后 SRAM size 报错 (A733 实测踩过)
  ④ 容量门禁: 板端 model_a/model_b 分区 = 15 MiB → 板端产物超了刷不进去
  ⑤ 重复资产: sha256 相同但 id 不同 → 名字骗人 (实测 yolov5s-sim_320_clean 与 _v2 完全同内容)

用法:
    python3 SW/tools/model_asset_check.py                # 全量检查
    python3 SW/tools/model_asset_check.py --json         # 机读输出
    python3 SW/tools/model_asset_check.py --id MOD-YOLOV5S-320-INT8   # 只查一条
    python3 SW/tools/model_asset_check.py --new /path/to/new.onnx      # 新模型入库: 打印台账行骨架

退出码: 0 = 台账与实物一致 (允许 WARN) | 1 = 有 FAIL | 2 = 用法/文件错
★ 语义: rc=0 **不等于可以量产**。量产放行看单独统计的 "放行阻断项 (L)" 计数 = 0
    L1 = 许可信息 [0数据] (未确认 license, 商用风险未清)
    L2 = 板端产物超 15 MiB 槽位 (刷不进)
    L3 = active 资产的 target chip ID 与目标 NPU 不符 (板端加载后报错)

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

# 板端 model_a / model_b 分区大小
# (SW/FLASH_AND_VERSION.md §4.1 推荐 C + SW/tools/s2_rescue_config.example.json)
MODEL_SLOT_BYTES = 15728640          # 15 MiB
MODEL_SLOT_MIB = 15

# 已登记资产台账 (唯一真源 = SW/MODEL_ASSETS.md §1.2; 本表必须与文档逐字段一致)
#   platform        : "candidate" (PC 侧源, 待转板端格式) | "A733-ref" (上一项目, 仅方法论参考)
#   state           : "candidate" | "reference" (A733 板端产物/工具产物, 作方法论与回归基准)
#                   | "quarantined" (已判死: chip ID 错, 不进任何流程)
#   expected_license: 期望 license 串; None = 登记为"未知" → 判 L1 阻断项
#   expected_chip   : 期望 NBG target chip ID (LE); None = 不适用
MANIFEST = [
    {
        "id": "MOD-YOLOV5S-320-INT8",
        "platform": "candidate",
        "state": "candidate",
        "role": "主 OD 模型候选 (PC 侧源, 320x320, 80 类)",
        "path": "/home/yuewuya/.openclaw/workspace/yolov5s-sim_320_clean.onnx",
        "fmt": "onnx",
        "size": 29337706,
        "sha256_16": "340978ec59391f69",
        "expected_license": None,          # [0数据] onnx 无 metadata_props
        "expected_opset": 14,
        "expected_input": [1, 3, 320, 320],
        "expected_chip": None,
        "note": "initializer 29,307,008 B / 245 节点 / 12 算子类型; 无 metadata_props → 许可未知",
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
        "expected_license": None,
        "expected_opset": 14,
        "expected_input": [1, 3, 320, 320],
        "expected_chip": None,
        "note": "文件名带 _v2 但内容与 clean 版逐字节相同 → 版本名不可信, 以 sha256 为准; 已去重隔离",
    },
    {
        "id": "MOD-YOLOV8S-COCO80-ONNX",
        "platform": "candidate",
        "state": "candidate",
        "role": "COCO 80 类 yolov8s (备选主模型)",
        "path": "/work/object_detection/yolov8s_coco80/workspace/yolov8s.onnx",
        "fmt": "onnx",
        "size": 44842647,
        "sha256_16": "111da30a25b6c585",
        "expected_license": "AGPL-3.0 License (https://ultralytics.com/license)",
        "expected_opset": 13,
        "expected_input": [1, 3, 640, 640],
        "expected_chip": None,
        "note": "★ AGPL-3.0 → 商用需向 Ultralytics 采购商业许可; 44.8MB 源文件本身不刷板",
    },
    {
        "id": "MOD-YOLOV5S-320-INT8-ACUITY",
        "platform": "A733-ref",
        "state": "reference",
        "role": "A733 ACUITY 导入产物 (.onnx 副本, 量化链输入)",
        "path": "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx",
        "fmt": "onnx",
        "size": 29337706,
        "sha256_16": "20368be665f6f59a",
        "expected_license": None,
        "expected_opset": None,
        "expected_input": [1, 3, 640, 640],
        "expected_chip": None,
        "note": "★ 与上面两条同名 (yolov5s-sim) 不同内容不同输入尺寸 (320 vs 640) → 名字不带尺寸 = 资产失控, 必须靠 sha 区分",
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
        "expected_license": None,
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
        "expected_license": None,
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
        "expected_license": None,
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
        "expected_license": None,
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
        "expected_license": None,
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
        "expected_license": None,
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
            if a.get("expected_license"):
                add("C5", lic == a["expected_license"], f"license = {lic!r}")
            else:
                add("C5", None, "★ metadata_props 无 license 字段 → 许可 [0数据] (量产放行阻断项 L1)")
            if a.get("expected_opset") is not None:
                add("C6", m.get("opset") == a["expected_opset"], f"opset = {m.get('opset')}")
            if a.get("expected_input"):
                got = list(m["inputs"].values())[0] if m["inputs"] else None
                add("C7", got == a["expected_input"], f"输入 shape = {got}")

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
    """量产放行阻断项 (只算 candidate/active; reference/quarantined 不进 ARS45 流程)
       L1 许可 [0数据] | L2 超 15MiB 槽位 | L3 chip ID 不符 | L4 许可商用受限 (AGPL)"""
    out = []
    for r in results:
        if r["state"] not in ("candidate", "active"):
            continue
        for code, ok, msg in r["checks"]:
            if code == "C5" and ok is None and "license" in msg:
                out.append(("L1 许可[0数据]", r["id"], msg))
            if code == "C5" and ok is True and "AGPL" in msg:
                out.append(("L4 许可商用受限(AGPL)", r["id"],
                            msg + "  → 商用须向 Ultralytics 采购商业许可"))
            if code == "C4" and ok is False:
                out.append(("L2 超 15MiB 槽位", r["id"], msg))
            if code == "C7" and ok is False:
                out.append(("L3 chip ID 不符", r["id"], msg))
    return out


def print_human(results: list, dups: list) -> None:
    print("=" * 100)
    print("模型资产登记检查器 (ISS-037) — SW/MODEL_ASSETS.md §1 台账机器复核")
    print("=" * 100)
    for r in results:
        print(f"\n▶ {r['id']}  [{r['fmt']} | {r['platform']} | {r['state']}]")
        print(f"  {r['path']}")
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
    print(f"量产放行阻断项 (L): {len(blockers)} 条 "
          f"{'→ ✅ 可进量产评审' if not blockers else '→ ❌ 不许进量产评审 (见 §1.5)'}")
    for tag, aid, msg in blockers:
        print(f"    - {tag}  [{aid}]  {msg}")
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
    print('        "expected_license": <从 metadata_props 取, 取不到填 null = [0数据]>,')
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
            print(f"license = {m.get('license')!r}  ← null = [0数据], 必须人工向来源方确认")
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--id", default=None, help="只检查某一条资产 id")
    ap.add_argument("--new", default=None, help="新模型入库: 打印台账行骨架")
    args = ap.parse_args()

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
