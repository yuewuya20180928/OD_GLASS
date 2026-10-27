#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-037 交卷: 把 sw-lead 本轮的登记项原子写进 state/fragments/sw.yaml
—— 只用 frag_write.update_fragment (tmp + fsync + os.replace), 禁止 open(p,"w")
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from frag_write import update_fragment  # noqa: E402

AGENT = "sw-lead"

ARTIFACTS = [
    {
        "path": "SW/MODEL_ASSETS.md",
        "kind": "design",
        "version": "v1.0",
        "updated_at": "2026-10-27",
        "summary": (
            "模型资产登记与INT8量化管理 v1.0 (ISS-037): 10条资产台账(来源/sha256[:16]/大小/许可/输入输出shape/"
            "算子类型/NBG头4字段/状态机 candidate·active·reference·quarantined) + 机器复核工具 + INT8量化流程"
            "(路线A ACUITY/VIVANTE已跑通5步 P1..P5 / 路线B Art.Galaxy骨架B0..B9) + NBG头三件套铁律6条 + "
            "量化精度评估 L0~L4 五层金字塔 + Q-1~Q-10放行判据 + 模型变更回归 R-01~R-14 矩阵 + 变更记录模板。"
            "★[实测](2026-10-27): 60项判定 rc=0, 查出2个量产阻断项(L1许可[0数据]+L4 AGPL-3.0商用受限)"
            "+2条死资产(chip ID 0x10000020错)+3份同名yolov5s-sim sha256互不相同(两份逐字节相同, 输入320/320/640)。"
            "★ARS45板端模型0个/转换0次/板端实测0次; 端到端预算与锁死变量一字未改"
        ),
    },
    {
        "path": "SW/tools/model_asset_check.py",
        "kind": "tooling",
        "version": "v1.0",
        "updated_at": "2026-10-27",
        "summary": (
            "模型资产登记检查器: 逐条核对存在/大小/sha256[:16]/许可/opset/输入shape/NBG头(magic VPMN + format + "
            "chip ID 小端uint32)/板端15MiB槽位/重复sha256组; 产出量化放行阻断项 L1许可未知 L2超槽 L3chipID "
            "L4AGPL; --new 模式打印新模型台账行骨架; --json 机读供门禁。★[实测](10-27): 10条资产60项判定 rc=0, "
            "放行阻断项 L=2"
        ),
    },
]

CLAIMS = [
    {
        "key": "model_asset_id_scheme",
        "value": "MOD-<FAMILY>-<VER>-<RES>",
        "note": (
            "模型唯一 ID 规则 (例 MOD-YOLOV5S-320-INT8); 版本只认 sha256[:16], 不认文件名 —— 依据 [实测] 三份同名 "
            "yolov5s-sim sha256 互不相同且 clean/v2 两份逐字节相同 (输入 320/320/640)"
        ),
        "ref": "SW/MODEL_ASSETS.md#1.1",
    },
    {
        "key": "model_asset_slot_budget",
        "value": "15MiB",
        "note": (
            "板端 model_a/model_b 单槽上限 = 15,728,640 B; 来源 FLASH_AND_VERSION §4.1 + s2_rescue_config.example.json; "
            "只管板端产物, 不管 PC 侧 ONNX; 与 flash_capacity_floor=128MB-NOR-min 是同一条容量线的两半"
        ),
        "ref": "SW/MODEL_ASSETS.md#1.6",
    },
    {
        "key": "model_asset_registry_tool",
        "value": "SW/tools/model_asset_check.py",
        "note": "台账机器复核入口; rc=0 = 台账与实物一致 (不等于可量产, 量产看 L 计数)",
        "ref": "SW/MODEL_ASSETS.md#7",
    },
    {
        "key": "model_asset_release_gate",
        "value": "L=0",
        "note": (
            "量产放行判据: 放行阻断项计数必须 0 — L1 许可[0数据] / L2 超 15MiB 槽 / L3 chip ID 不符 / L4 AGPL 商用受限; "
            "当前 L=2 (L1 yolov5s-sim 许可未知 + L4 yolov8s AGPL-3.0)"
        ),
        "ref": "SW/MODEL_ASSETS.md#1.5",
    },
    {
        "key": "model_version_string_fmt",
        "value": "yolov5s-int8-ag2-<sha8>",
        "note": (
            "与 FLASH_AND_VERSION §2.5.1 一致, 不改; <sha8> = 板端模型文件 sha256 前 8 位; <ag2> = 板端格式版本, "
            "必填 (A7S NBG format version 坑); 换格式版本必须换版本串"
        ),
        "ref": "SW/MODEL_ASSETS.md#4.3",
    },
    {
        "key": "model_calib_min_images",
        "value": "100",
        "note": (
            "INT8 校准集最少张数 (A733 实测 6 张不够用); 现有 100 张 = COCO 通用集, 与眼镜场景分布不符, 需自建"
        ),
        "ref": "SW/MODEL_ASSETS.md#2.4",
    },
    {
        "key": "model_quant_scheme",
        "value": "pcq",
        "note": (
            "A733 侧真正 INT8 的量化方案名 (per-channel symmetric affine); Art.Galaxy 侧方案名 [0数据] "
            "(Q9 追加第 3 条); .quantize 量化参数表本身是资产, 换参数=换模型"
        ),
        "ref": "SW/MODEL_ASSETS.md#2.3",
    },
    {
        "key": "model_regression_gate",
        "value": "R-01..R-14",
        "note": (
            "模型变更后必跑的回归用例编号集合 (台账/许可/文件头/容量/加载/数值/量化器/总体精度/逐类精度/阈值/"
            "性能/端到端/版本串/刷写回滚), 全过才允许刷板; 与 BR-01..BR-12 不重叠 (一个测模型, 一个测刷写救砖)"
        ),
        "ref": "SW/MODEL_ASSETS.md#4.2",
    },
]

NEEDS = [
    {
        "key": "model_toolchain_q9_addendum",
        "to": "vendor",
        "item": (
            "Q9 追加 10 条 (模型转换专项, 经 main 转达, 我不单独对外): ①Art.Galaxy 支持的输入格式与 opset 范围 "
            "②yolov5s 12 类算子 (Conv/Sigmoid/Mul/Concat/Slice/Resize/Pow/Sub/MaxPool/Reshape/Transpose/Add) 覆盖情况 "
            "③支持的量化方案 + 输出能否直通量化整数而不强制 FP32 (A733 上反量化占 SDK 总 25~29%) ④校准集最少张数与推荐分布 "
            "⑤板端模型文件头布局 + ARS45 的 chip ID 是多少 (错则板端加载后报 SRAM size 错) "
            "⑥Art.Galaxy 是否与 VeriSilicon ACUITY/VIPLite 同源 (假设 H1, 决定 A733 的 p1/p2 脚本能否复用) "
            "⑦官方是否提供预编译的 yolov5 板端模型及其许可与类别映射是否正确 (A733 官方 .nb 实测类别映射错→422 false positive) "
            "⑧转换产物体积上限 (板端槽位 15MiB) ⑨冷启动加载耗时 ⑩工具链运行平台与是否需要授权/NDA "
            "-> 卡 SW/MODEL_ASSETS.md §2.9 转换骨架 B0~B9 全部九步"
        ),
        "since": "2026-10-27",
        "waiting_on": "vendor",
        "due": "2026-10-29",
    },
    {
        "key": "model_license_yolov5sim",
        "to": "vendor",
        "item": (
            "模型许可确认 (经 main 转达, 量产阻断项 L1): yolov5s-sim 系列 ONNX 的来源与上游许可是什么 "
            "(3 份 onnx 的 metadata_props 全空, 本机也查不到 LICENSE 文件) -> 不确认则不许进量产评审; "
            "同时请确认原厂 model zoo 是否提供带明确许可的预编译板端模型 (可绕开第三方权重许可风险)"
        ),
        "since": "2026-10-27",
        "waiting_on": "vendor",
        "due": "2026-10-29",
    },
    {
        "key": "model_license_agpl_ultralytics",
        "to": "main",
        "item": (
            "yolov8s 的 AGPL-3.0 商业许可采购决策 (走 main 转老板, 阻断项 L4): yolov8s.onnx 的 metadata 许可实测为 "
            "AGPL-3.0 -> 商用眼镜产品需向 Ultralytics 采购 Enterprise License, 否则有开源义务; 费用与周期必须进 "
            "BOM/采购计划, 不能等量产前 -> 若最终选 yolov5s 系则此条作废"
        ),
        "since": "2026-10-27",
        "waiting_on": "boss",
        "due": "2026-10-29",
    },
    {
        "key": "model_od_input_size",
        "to": "main",
        "item": (
            "ARS45 OD 输入尺寸裁决 (走 main): 决定 ONNX 静态化 shape + 转换产物体积 + 端到端预算 "
            "(我给的约束: 端到端 <60ms, 纯 NPU 跨 16.67ms 会让框龄 age 从 2 跳 3 直接 +16.67ms; 板端 model 槽位 15MiB) "
            "-> 我的默认假设是 640x480 (与锁定的 ISP 缩放链一致), 若裁决不同我按新值重算并重出静态 shape"
        ),
        "since": "2026-10-27",
        "due": "2026-10-29",
    },
]

BLOCKERS = [
    {
        "id": "SW-MODEL-B1",
        "desc": (
            "模型许可未清 + ARS45 板端模型 0 个 -> 量产评审前必须有 (a) 许可确认 (放行阻断项 L1 许可[0数据] 与 "
            "L4 AGPL-3.0 商用受限, 当前 L=2) 与 (b) 一条跑通 SW/MODEL_ASSETS.md §2.9 B0~B9 的转换链 "
            "(无板 + 无 Art.Galaxy 工具链 + 无 ARS45 chip ID -> 转换 0 次、板端实测 0 次)"
        ),
        "severity": "high",
        "needs_from": ["vendor", "main", "boss"],
        "waiting_since": "2026-10-27",
    },
]

STATUS = {
    "phase": "P2(方案设计)",
    "progress_pct": 46,
    "health": "red",
    "summary": (
        "10-27 ISS-037 交卷: SW/MODEL_ASSETS.md v1.0 (模型资产台账 10 条 + INT8 量化流程 + 量化精度评估 L0~L4 + "
        "模型变更回归 R-01~R-14) + SW/tools/model_asset_check.py (机器复核, 60 项判定 rc=0)。"
        "★[实测]查出: 3 份同名 yolov5s-sim sha256 互不相同 (clean/v2 逐字节相同, 输入 320/320/640) → 立 "
        "唯一 ID + 版本只认 sha256 两条硬规则; 2 条 .nb 的 NBG chip ID = 0x10000020 (错, A733 真值 0x1000003B) → 隔离作废; "
        "许可栏 yolov5s-sim 系 [0数据] + yolov8s 实测 AGPL-3.0 → 放行阻断项 L=2。"
        "★ARS45 板端模型 0 个 / 转换 0 次 / 板端实测 0 次; 端到端预算与锁死变量一字未改。"
        "健康度仍 red: 主因是原厂 3 个决定性 0 数据 (工具链/chip ID/板端耗时) + 无板"
    ),
}


def mutate(d):
    arts = d.setdefault("artifacts", [])
    paths = {a.get("path") for a in arts}
    for a in ARTIFACTS:
        if a["path"] not in paths:
            arts.append(a)
    claims = d.setdefault("interface_claims", [])
    keys = {c.get("key") for c in claims}
    for c in CLAIMS:
        if c["key"] not in keys:
            claims.append(c)
    needs = d.setdefault("needs_from", [])
    nkeys = {n.get("key") for n in needs}
    for n in NEEDS:
        if n["key"] not in nkeys:
            needs.append(n)
    blocks = d.setdefault("blockers", [])
    bids = {b.get("id") for b in blocks}
    for b in BLOCKERS:
        if b["id"] not in bids:
            blocks.append(b)
    d["status"] = STATUS
    d["updated_at"] = "2026-10-27"
    d["updated_by"] = "sw-lead"


if __name__ == "__main__":
    update_fragment(AGENT, mutate)
    print("[frag_write] ✅ sw.yaml 已原子更新 (artifacts +2 / interface_claims +8 / needs_from +4 / blockers +1 / status)")
