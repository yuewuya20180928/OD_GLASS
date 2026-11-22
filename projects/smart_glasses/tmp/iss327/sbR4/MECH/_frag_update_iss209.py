#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-209 分片原子写脚本 —— 正中区腔体重排 + U-3 订正

走 state/frag_write.py 的 update_fragment (tmp + fsync + os.replace), 全程零 open(p,"w").
纪律:
  * 只写自己 (mech-lead) 的分片
  * 只【新增】artifact / claim / need  —— 一个别人的 key 都不删不改
  * 唯一一次【改值】= U-3: mech_hinge_stack_fixed_mm 24.00 → 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
    ★按 key 定位后替换, **不用** CLI --add-claim (它是追加语义 ⇒ 会造成同 key 两条)
  * issue 状态 / owner 是 main 的活, 本脚本不碰 state/issue_log.yaml
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "state"))

from frag_write import update_fragment  # noqa: E402

AGENT = "mech-lead"
SINCE = "2026-11-15"

ARTIFACTS = [
    {
        "path": "MECH/CENTER_CAVITY_RECALC.md",
        "kind": "recalc",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": ("ISS-209 交卷件: 镜框正中区光学腔体按眼盒硬约束 (A_e<=62mm2 + d=15-20mm) 重排 —— "
                    "参数化余量预算表 9 行 (3 d × 3 A_e, 每个数由 cavity_recalc_check.py 算出并被门禁逐格回读比对) + "
                    "出瞳面 ±3mm 装配公差带单独成行 (占 6.0mm 行程, 9 行里占 27-33%) + 冲突量化 5 条 (只报不改) + "
                    "降级方案 6 条 + 出路候选 4 条 (不替老板拍板) + 边界。★T = d + 3.0 = 18/21/23mm (d=15/18/20), "
                    "全部超 10-12mm 目标上沿 +6/+9/+11mm; 与旧数 11.8mm 的冲突量 3.2/6.2/8.2mm (与 1.7.1 C-1 逐字一致); "
                    "A_e 在 <=62mm2 合法区内对轴向预算影响 = 0.00mm (面板口径 9.125mm 顶死)。★[实测]实物 = 0 条。"),
    },
    {
        "path": "MECH/cavity_recalc_check.py",
        "kind": "check",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": ("ISS-209 机器门禁: 12 项检查 (X-1/X-2 在位 / 参数表 9 行逐格一致 / C-1 冲突量 3.2 与 8.2 一致 / "
                    "判据文件 md5 未变 / ±3mm 带单独成行 / 重量重核一致 / 鼻梁热路径一致 / 4 个受保护脚本 md5 未变 / "
                    "分片 claim 25.00 / 判据阈值未松 / 分光件冲突量一致 / 边界声明齐全), rc=0 全过, 失败点名是哪一条; "
                    "带 --selftest (9 个反向用例: 改坏参数表 / 删 62 / 改坏冲突量 / 篡改判据文件 / 删一行表 / "
                    "改坏重量数 / 篡改分片 claim / 篡改受保护脚本 / 改掉 ±3 带) 全被抓; --emit-rows 原样重生成三张表。"),
    },
    {
        "path": "HANDOFF/2026-11-15_mech-lead_ISS209_正中区腔体重排.md",
        "kind": "handoff",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": ("ISS-209 交卷单 (B1 结论 / B2 验收自评 / B3 证据分级 / B4 接口取值 / B5 未决与卡点 / B6 自证命令), "
                    "B1~B6 六块齐全。"),
    },
    {
        "path": "MECH/_frag_update_iss209.py",
        "kind": "script",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": ("ISS-209 分片原子写脚本 (走 state/frag_write.py 的 update_fragment): U-3 订正 "
                    "mech_hinge_stack_fixed_mm 24.00→25.00 (按 key 定位后替换, 不用 CLI --add-claim 的追加语义) + "
                    "新增 3 artifact / 2 claim / 6 need; 禁 open(p,\"w\"); 只动自己分片的一个 key + 追加。"),
    },
]

CLAIMS = [
    {
        "key": "mech_center_cavity_rebudget",
        "value": "d=15/18/20 => T=18/21/23mm(含±3带)",
        "note": ("★ISS-209 (2026-11-15) 正中区腔体重排 (按 X-1 眼盒<=62mm2 + X-2 评估距离 d=15-20mm): "
                 "正中区轴向厚度需求 T = d + 3.0 (含出瞳面 ±3mm 可调带) = 18.00/21.00/23.00mm (d=15/18/20); "
                 "与旧数 11.8mm 的冲突量 = d - 11.8 = 3.20/6.20/8.20mm (与 MECH_BUDGET 1.7.1 C-1 逐字一致); "
                 "vs 现行目标 10-12mm 全档超差 +6.0/+9.0/+11.0mm; 扣器件区 11.8 与带 6.0 后的可动余量 = 0.20/3.20/5.20mm "
                 "(d=15 档 < 判据 0.60 ⇒ 装配不可行)。★口径: 耦合光学出射面→波导出瞳面净空 (器件区嵌套其中), "
                 "加厚方向朝耳侧 ⇒ 眼距 d 不受影响。★A_e 在 <=62mm2 合法区内对轴向预算影响 = 0.00mm (面板有效面积 65.40mm2, "
                 "等效直径 9.125mm 顶死) ⇒ 老板拍波导眼盒时厚度不用让步。★[推算] 出处 MECH/CENTER_CAVITY_RECALC.md §1 + "
                 "MECH_BUDGET.md 1.7 X-1/X-2 + V2 C-4/C-5; 门禁 python3 MECH/cavity_recalc_check.py (rc=0)。"),
        "ref": "MECH/CENTER_CAVITY_RECALC.md §1 + MECH/MECH_BUDGET.md §1.7 X-1/X-2",
    },
    {
        "key": "mech_center_cavity_splitter_resize",
        "value": "A_e=62 => 分光件 0.97cc / W4 3.68-7.36g",
        "note": ("★ISS-209 新冲突 (只报不改): 分光件要承的光束口径必须 >= 眼盒等效直径 D_e (25/40/62 mm2 => "
                 "5.642/7.136/8.885mm), 而 §1.3 M6 的 14×10×6 / 0.79cc / W4 3-6g 是按走鹃Ⅱ 2.9mm 光束定的 (器件已作废) "
                 "⇒ 按 A_e=62 重算: 45° 平板所需对角 12.57mm (§1.2 宽松式) / 15.39mm (严格矩形包含口径, 比 10×10 平板的 "
                 "14.14mm 差 1.25mm), 转向棱镜 8×8 装不下 8.885mm 光束 (需 >=9×9×5) ⇒ 分光组件 0.97cc (+0.18cc) / "
                 "W4 3.68-7.36g (+0.68~+1.36g) / 腔体占位要放大。★只报不改 + 登记 need "
                 "(iss209_mech_splitter_resize_for_eyebox62)。[推算]"),
        "ref": "MECH/CENTER_CAVITY_RECALC.md §2.4 + MECH/MECH_BUDGET.md §1.3 M6",
    },
]

NEEDS = [
    {
        "key": "iss209_mech_cavity_rebudget_done",
        "to": "main",
        "item": ("★ISS-209 重排完成 (闭环 ISS-208 登记的 need iss208_mech_rebudget_frame_cavity_d15_20): "
                 "正中区轴向厚度需求 T = d + 3.0 (含出瞳面 ±3mm 带) = 18.00/21.00/23.00mm (d=15/18/20); "
                 "与 §1.4.5 旧数 11.8mm 的冲突量 = 3.20/6.20/8.20mm (与 §1.7.1 C-1 逐字一致); "
                 "vs 现行目标 10-12mm 全档超差 +6.0/+9.0/+11.0mm ⇒ 镜框最厚处从 12mm 变 18-23mm (×1.50-1.92); "
                 "可动余量 (扣器件区 11.8 + 带 6.0) = 0.20/3.20/5.20mm ⇒ d=15 档装配不可行 (判据 0.60)。"
                 "★眼盒维度: A_e 在 <=62mm2 合法区内对轴向预算影响 = 0.00mm (面板等效直径 9.125mm 顶死) ⇒ "
                 "老板拍波导眼盒时厚度不用让步。★交卷件 MECH/CENTER_CAVITY_RECALC.md + 机器门禁 "
                 "MECH/cavity_recalc_check.py (rc=0, 12 项 + --selftest 9/9)。★未改 MECH_BUDGET 任何既有数字 "
                 "(只新增 §1.8 指针段)。"),
        "since": SINCE,
    },
    {
        "key": "iss209_mech_splitter_resize_for_eyebox62",
        "to": "main",
        "item": ("★ISS-209 新冲突 C-6 (只报不改, 请裁): X-1 的眼盒 <=62mm2 ⇒ 分光件要承的光束口径从 2.9mm 变 8.885mm "
                 "⇒ §1.3 M6 的 14×10×6mm / 0.79cc / W4 3-6g 全部偏小: 按光束重算 = 平板对角需求 12.57mm (§1.2 宽松式) / "
                 "15.39mm (严格矩形包含口径, 比 10×10 的 14.14mm 差 1.25mm) + 转向棱镜需 >=9×9×5 (现 8×8 装不下) "
                 "⇒ 分光组件 0.97cc (+0.18cc) / W4 3.68-7.36g (+0.68~+1.36g) / 正中区腔体占位要放大。"
                 "★连带: 整机重量上限 74.0g → 76.13g (d=20 档 + 分光件)。★只报不改, 几何数字变更请裁。"),
        "since": SINCE,
    },
    {
        "key": "iss209_mech_cavity_heat_468mw_vs_50c",
        "to": "main",
        "item": ("★ISS-209 新冲突 C-7 (只报不改): 面板 468mW (V2 §3 ③-d) 放正中区 ⇒ 按 ISS-065 §2.3 模型, "
                 "腔体节点 81.20/77.43/75.24°C (d=15/18/20) vs X-3 的腔体红线 50°C ⇒ 超 31.20/27.43/25.24°C; "
                 "保 50°C 所需被动散热面 ≈ 4668.9mm² (u8 未定值 1000mm² 的 4.67 倍) ⇒ 加厚只贡献 297.6-537.6mm² "
                 "(6.4%-11.5%) ⇒ ★腔体散热不能靠加厚, 必须金属热路导到铰链侧/端件 (X-3: >=0.5W 被动散热面 + 不得密闭腔)。"
                 "★归 ISS-208 的 468mW 重算单 (iss208_mech_recompute_optical_thermal_468mw), 本单不拍板。"),
        "since": SINCE,
    },
    {
        "key": "iss209_mech_nose_bridge_heat_path",
        "to": "main",
        "item": ("★ISS-209 C-C (量化, 只报): 若 PCB/SoC 要挪到镜框正中 —— 鼻梁区热路径 = 12.0mm "
                 "(节点→鼻梁接触面, ISS-065 §2.3 L_bridge; ★加厚方向朝耳侧 ⇒ 这条路径长度不变), R_bridge = 400K/W; "
                 "SoC 0.55W + 面板 0.468W = 1.018W 进镜框 ⇒ 鼻梁接触面 54.33/52.75/51.83°C (d=15/18/20) "
                 "⇒ 对 43°C 红线余量 -11.33/-9.75/-8.83°C; 加鼻梁侧热断 (R_bridge=1000) 仍 43.74/43.03/42.61°C ⇒ "
                 "加厚救不了; 保 43°C 所需 R_bridge = 454.8/409.9/383.9 K/W (仅面板) / 1101.2/1003.6/946.9 K/W (含 SoC)。"
                 "⇒ 结构侧论据: PCB 不进镜框正中 (与 ISS-065 §2.4 同向)。"),
        "since": SINCE,
    },
    {
        "key": "iss209_mech_x3_skin_path_claim",
        "to": "main",
        "item": ("★ISS-209 与 X-3 口径的冲突 (只报不改, 建议裁): X-3 写「光学件在镜框, 不进皮肤热路径」, "
                 "但按 468mW 面板算, 仅面板就让鼻梁接触面到 43.89/43.16/42.74°C (d=15/18/20) ⇒ d=15/18 档已破 "
                 "43°C 红线 0.89/0.16°C ⇒ 这句话在现行功耗下不成立 (除非配鼻梁侧热断 >=454.8 K/W)。"
                 "★X-3 在 MECH_BUDGET §1.7, 本单未改该行一个字 ⇒ 请裁: 加限定语还是补热断要求。"),
        "since": SINCE,
    },
    {
        "key": "iss209_mech_d_value_decision",
        "to": "boss",
        "item": ("★ISS-209 需老板/判据侧拍的一维: 评估距离 d 取 15 / 18 / 20 的取舍 (我给数, 不拍板) —— "
                 "d=15: T=18.00mm, 可动余量仅 0.20mm (< 判据 0.60 ⇒ 装配不可行, 出瞳面 ±3mm 带无处放); "
                 "d=18 (同类公开值): T=21.00mm, 可动余量 3.20mm (唯一「装得下且有余量」的折中); "
                 "d=20: T=23.00mm, 可动余量 5.20mm 但镜框最厚 23mm (×1.92 于 12mm 目标)。"
                 "★d 是 V2 判据 (§3 ⑤-b), 结构侧不许放宽或收紧 ⇒ 经项目总工转老板。"),
        "waiting_on": "boss",
        "since": SINCE,
    },
]


def mutate(d: dict) -> None:
    # ---- 1) U-3: 按 key 定位后替换 (不许用 CLI --add-claim 的追加语义) ----
    fixed = 0
    for c in d.get("interface_claims", []):
        if c.get("key") == "mech_hinge_stack_fixed_mm":
            c["value"] = "25.00"
            c["note"] = (
                "收敛版 (16p/20p/4p/**10p** @0.5mm) 堆叠, 余 12.00 | "
                "★ISS-209 (2026-11-15) 按 ISS-206 裁 2 订正: 原值 24.00 + note 的 8p 口径 "
                "(16p/20p/4p/8p, 余 13.00) 与 MECH/USB_HINGE_STRUCTURE.md §9 不一致 (文档已写 25.00), "
                "本单按 U-3 把它改成 25.00 + 10p 口径; ★2026-11-06 标注保留: 仅供追溯, 现行板无跨铰链。"
            )
            fixed += 1
    if fixed != 1:
        raise SystemExit(f"[iss209_frag] U-3 定位失败: 找到 {fixed} 条 mech_hinge_stack_fixed_mm")

    # ---- 2) 只新增 artifact / claim / need ----
    arts = d.setdefault("artifacts", [])
    have_art = {a.get("path") for a in arts}
    for a in ARTIFACTS:
        if a["path"] not in have_art:
            arts.append(a)
    claims = d.setdefault("interface_claims", [])
    have_key = {c.get("key") for c in claims}
    for c in CLAIMS:
        if c["key"] not in have_key:
            claims.append(c)
    needs = d.setdefault("needs_from", [])
    have_need = {n.get("key") for n in needs}
    for n in NEEDS:
        if n["key"] not in have_need:
            needs.append(n)


def main() -> int:
    update_fragment(AGENT, mutate)
    print("[iss209_frag] ✅ mech.yaml 已原子写 (U-3 订正 24.00→25.00 + 3 artifact + 2 claim + 6 need)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
