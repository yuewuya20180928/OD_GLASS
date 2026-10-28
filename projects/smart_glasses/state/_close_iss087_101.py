#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""关单脚本: ISS-087 + ISS-101 (sw-lead 已交卷, 项目总工验收) —— 2026-10-28 08:2x
原子写 issue_log.yaml (tmp + os.replace), 禁止 open(p,"w") 覆盖。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

issues = doc.get("issues")
if isinstance(issues, dict):
    items = list(issues.values())
else:
    items = issues

TODAY = "2026-10-28"
CLOSES = {
    "ISS-087": {
        "fix_ref": "SW/MODEL_LICENSE.md + SW/ARS45_INT8_CHAIN.md + HANDOFF/2026-10-28_sw-lead_ISS087_模型许可与INT8转换链.md",
        "note": (
            "★2026-10-28 08:2x 项目总工验收关单。sw-lead 交卷 (00:47) 后 issue_log 一直挂在 fixing 没落 fix_ref ⇒ 现补。\n"
            "【交付】① 模型许可: yolov5s-sim 系 3 份 ONNX 许可 = **AGPL-3.0** (7 环物证可复现: Rockchip zoo README → sha256 逐字节相同 → "
            "ONNX initializer 命名 → pickle 命名空间 → 本机 ultralytics 8.4.80 AGPL-3.0 → GitHub API spdx_id=AGPL-3.0; "
            "脚本 python3 SW/tools/license_probe.py)。AGPL 商用路径: 官网明写 embedded deployments / 任何商用产品 / 自训练微调模型均需 Enterprise License; "
            "官方无公开价 [0数据]; 立项预算 10^4~10^5 USD (一次性 US$5k-50k + 年费 US$2k-20k/型号) / 周期 4-12 周 [推算]。\n"
            "不采购 = 商用受阻 (唯一合规路径是固件连同训练脚本/配置/权重整体以 AGPL-3.0 开源 §6, 与闭源量产直接冲突) ⇒ 台账 2 条 AGPL 资产置 licensing-hold 禁入交付物。\n"
            "② INT8 转换链: 10 步 READY 2 / PARTIAL 4 / BLOCKED 4 (--build 真跑出 _s640.onnx + _rt.onnx)。4 个 BLOCKED = B0 工具链 / B5 导出+chip ID / "
            "B7 板端加载 / B8 打点 —— 全卡在『原厂交付 Art.Galaxy + 有板』, 不是本机工程量。**板端 INT8 模型仍 0 个 / 转换 0 次 / 板端实测 0 次** (不粉饰)。\n"
            "【★顺手查出的真缺陷】台账原主模型候选 yolov5s-sim_320_clean.onnx **PC 侧推理就失败** (Concat_527 ShapeInferenceError: Inferred=10 Declared=20 —— "
            "只改输入 dim、图内常量仍是 640 尺度), 416 变体同病; 唯一实测可推理的是 640 那份 ⇒ 新增 C9 = PC 侧 1 帧推理冒烟门禁 (交付集内失败 = 阻断项 L5), 坏模型已隔离。\n"
            "【自证复现】python3 SW/tools/model_asset_check.py → rc=0 (资产 11 条 · FAIL 0 · WARN 11 · 重复组 1; 交付集 candidate/active 1 条 · "
            "licensing-hold 2 条 · quarantined 4 条 · reference 4 条; 量产放行阻断项 L=0)。python3 SW/tools/license_probe.py rc=0。python3 SW/tools/int8_chain.py rc=0。"
        ),
    },
    "ISS-101": {
        "fix_ref": "SW/MODEL_RELEASE_GATE.md + HANDOFF/2026-10-28_sw-lead_ISS101_量产放行门判定.md",
        "note": (
            "★2026-10-28 08:2x 项目总工验收关单。sw-lead 交卷 (01:01) 后 issue_log 一直挂在 open 没落 fix_ref ⇒ 现补。\n"
            "【核心突破: [0数据] → [实测]】唯一许可干净候选 (Apache-2.0) 的 NPU 可转换性: 本机已有 tf2 conda 环境 (TF 2.20.0) ⇒ 装 tf2onnx 1.16.1 后\n"
            "  第 1 段 (TF SavedModel → ONNX) 实测 rc=0: 12,259,298 B / opset 13 / 3304 节点 / 33 算子。\n"
            "  ★查出两个 NPU 致命问题并解掉: ① **74.7% 的图 (2465/3304 节点) 是 NMS 后处理** (含 NonMaxSuppression(90)/TopK(2)/Range(2)/NonZero(1), "
            "NPU 编译器一律拒收) ② **输入是动态 shape** [1,'unk__5514','unk__5515',3] (编译器直接拒) ⇒ 自写 cut_postprocessor.py + fix_static_shape.py → "
            "**299 节点 / 18 算子 / 静态 [1,320,320,3]**, 与全图输出 **max_abs_diff = 0.000e+00 (逐位相同)**。做法与本机 awnpu_model_zoo/examples/yolox 原厂配方同构 (extract_model 只留 head)。\n"
            "  第一组真实精度: 299 张 COCO val2017 → **P=0.4521 R=0.4184 F1=0.4346** (person R=0.532)。\n"
            "【第 3 段缺件】M1~M10 逐条列出 (M3/M4/M9/M10 为新增, 建议并入 Q9) + 4 条『拿到工具链前的可行性判断依据』 (不是猜通不通, 而是把不确定性从 74.7% 的图缩到 3 个节点); "
            "并发现一条现在就能做的下一步: 用本机 ACUITY 工具链试跑第 3 段 (已记为 R-U6 请求拍板, ⚠️ ACUITY ≠ Art.Galaxy, 不得当 ARS45 实测)。\n"
            "【AGPL 商用路径】5 个 Apache-2.0 候选逐条给许可/先例/代价。签字人 = boss (走项目总工, sw-lead 不拍板)。建议路径 1 (采购 Enterprise) 与路径 2 (换 Apache-2.0 栈) 并行准备 (等待期不产生工程进展)。\n"
            "【判据写死】L=0 判据写进复核器 (C10~C13 + L6/L7/L8, 五组判据 G1~G5) 并做了**反例验证** (注入缺陷后复核器立刻变红 ⇒ 判据不是摆设)。\n"
            "【★它自查出的真 bug】复核器自己的 C9 冒烟硬编码 float32, 而本模型输入是 uint8 ⇒ 会把好模型判成坏模型 (实测 FAIL=1 / L=1) ⇒ **这个 bug 会让"
            "『Apache-2.0 路线不可用』这个错误结论凭空成立** ⇒ 已修。\n"
            "【诚实缺口】健康度仍 red: 板端 INT8 产物仍是 0 个 (卡第 3 段: 等原厂工具链 + chip ID + 板子, 且采购待老板拍板)。**『量产可用模型清单』从空集变成 1 条待第 3 段落地的候选** —— "
            "G5 (板端产物 + 板端实测) 尚未满足, L=0 只覆盖 G1~G4。\n"
            "【自证复现】python3 SW/tools/model_asset_check.py rc=0 (资产 13 条 · FAIL 0 · WARN 33 · 重复组 1; **★交付集里 NPU 就绪且有实测精度的产物: 2 条**; 量产放行阻断项 L=0)。"
        ),
    },
}

changed = []
for it in items:
    iid = it.get("id")
    if iid not in CLOSES:
        continue
    c = CLOSES[iid]
    it["fix_ref"] = c["fix_ref"]
    it["status"] = "verified"
    it["verify_by"] = "main"          # ★验证分离: owner=sw-lead ≠ verify_by=main
    it["verify_result"] = "pass"
    it["verify_date"] = TODAY
    it["note"] = (it.get("note") or "") + "\n" + c["note"]
    changed.append(iid)

if not changed:
    print("❌ 没找到要关的单")
    sys.exit(1)

doc["issues"] = items
text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
fd, tmp = tempfile.mkstemp(prefix="issue_log.yaml.", suffix=".tmp", dir=HERE)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise

print(f"✅ 已关单: {changed} (status=verified, verify_by=main, verify_result=pass)")
