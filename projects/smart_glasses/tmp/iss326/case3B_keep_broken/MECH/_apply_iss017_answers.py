#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-017 收尾: 答复 hw-lead 的 ISS-121/ISS-118 需求 + 分片补充 (mech-lead, 2026-11-01)。

★ 为什么现在答复: hw-lead 2026-11-01 给了 **板宽 30 的 PIN-SET-2 新 Y 坐标**
  (iss118_pcb_holes_30mm_y: P1(8.00,15.00) / P2(52.00,15.00) / S1(8.00,10.00) / S2(52.00,20.00))
  ⇒ 我这条 needs (iss017_pcb_thickness_vs_service_port_clearance) 的 **Y 部分已被答复**,
  Rev B 打印包已按新坐标重生成并通过自检 ⇒ 答复闭环。

★ 走 state/frag_write.py 的原子写 (禁手改分片)。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

ANSWERS = [
    # ---- hw-lead iss118_pcb_holes_30mm_y: 孔位 Y 向重算 (板宽 15→30) ----
    {"key": "iss118_pcb_holes_30mm_y", "to": "hw-lead",
     "value": "已采纳并落到 Rev B 打印包: P1(8.00,15.00) / P2(52.00,15.00) / S1(8.00,10.00) / S2(52.00,20.00) —— "
              "结构侧已按此重生成 (MECH/print/temple_cage_revb.stl + fit_coupon_revb.stl), "
              "自检 93/93 尺寸判据 + 38/38 STL↔规格互验 rc=0。",
     "ref": "MECH/print/gen_print_pack_revb.py (P 表 pinset2_*_y) + MECH/print/verify_pack_revb.py"},
    # ---- hw-lead iss121_magnet_xy_define: 磁铁/定位凸台/螺钉在盖板下的确切 X/Y ----
    {"key": "iss121_magnet_xy_define", "to": "hw-lead",
     "value": "盖板 13.20(X)×7.60(Y)×1.20, 磁铁 2×N35 ⌀4.0×1.0 (ISS-092 C-8), 定位凸台 2×⌀1.60 间距 6.00 (C-11), "
              "自攻螺钉 1×M1.6 (C-3)。★**你指出的 '磁铁无处可放' 是对的, 我确认并已按几何重排**: "
              "⌀4.20 沉槽 + ≥2.10mm 壁 ⇒ 需 8.40mm, 而盖板 Y 向只有 7.60 ⇒ **Y 向放不下, 只能沿 X 排** ⇒ "
              "两槽中心 X=4.20 / 9.00 (端壁各 2.10), Y 居中 3.80。**但这样 Y 向壁只剩 1.70 < 2.10 ⇒ 仍有 0.40 不达标** ⇒ "
              "必须裁一个: ①盖板 Y 7.60→8.60 (盖板变宽 1.00, 重量 +0.02g) ②磁铁改 ⌀3.0 (壁达标但吸力降) "
              "③承认该处壁厚要求可降 (磁铁不承结构力, 只防丢 ⇒ 1.70 壁在 FDM PA-CF 上是否够, 需拉脱实测)。"
              "**我的假设: ③ + 待实测** (ISS-092 C-8 明确 '不承结构力')。Rev B 打印包已按 ①之外的几何 (X=4.20/9.00, Y=3.80) 出好, "
              "等你裁 Y 向壁怎么处理再改一行即可。",
     "ref": "MECH/print/gen_print_pack_revb.py (mag 位置) + MECH/SERVICE_PORT_ISS092.md C-8/C-11"},
    # ---- hw-lead iss121_mag_soc_gap_correction: 磁铁↔SoC 间距 68mm 的坐标系混算 ----
    {"key": "iss121_mag_soc_gap_correction", "to": "hw-lead",
     "value": "★**你算的对, 我确认是 ISS-092 的错, 已订正**: §4.3 那行 '磁铁在 L≈100.3, SoC 在 X 20..32 ⇒ 间距 ≥68mm' "
              "是把 **镜脚 L** 减 **板 X** (两套坐标系混算) ⇒ 68.30 无意义; 按同一条链 (磁铁 L100.30 vs SoC 逃线带末端 L72.30) "
              "实际 **28.00mm**。ISS-092 的 '68mm' 结论 **作废**。连带影响: §0 结论 10③ 与 §10 诚实边界第 3 条里的 "
              "'间距 ≥68mm 可达' 也要一并改成 28.00mm ⇒ **'对 SoC 大概率无影响' 这句话的依据强度要降** "
              "(28mm 是否够, 取决于 SoC 的磁敏感度, 而那仍是 [0数据])。"
              "**结构侧不改结论**: 磁铁位置由盖板/凸台决定 (ISS-092 C-8/C-11), 我会把它移到盖板 Y 向居中 3.80 —— "
              "这会让磁铁到 SoC 的实际间距变化, 落板后用你的脚本重算。",
     "ref": "MECH/SERVICE_PORT_ISS092.md §4.3 (待订正) + MECH/print/gen_print_pack_revb.py"},
    # ---- hw-lead iss121_skeleton_extent_confirm: 金属骨架是否贯通全板长 ----
    {"key": "iss121_skeleton_extent_confirm", "to": "hw-lead",
     "value": "**骨架不贯通全板长** —— 现行硬约束 `skeleton_extent` = '止于 PCB 段后缘'(已登记在 interface_claims), "
              "ISS-092 §8 第 4 行给的 L58.5..82.5 (板 X 18.00..42.00) 就是 **SoC 覆盖区**, 不是骨架全长; "
              "骨架在 **SoC 覆盖区之外本就不在 PCB 上方** (镜脚 V 净高 38.00, PCB 段只占板宽 30, "
              "SoC 逃线带外的板面没有骨架)。"
              "★**但板宽 30 之后这句要重核**: SoC 横向扩散通道从 2.00 → 3.50mm/边 (板宽 30 ⇒ SoC 边缘到板边 6.40mm/边), "
              "⇒ 骨架/石墨的 V 向覆盖要跟着加宽, 我在 fit_check_v3_30mm.py §4 已按 'V 覆盖 12.0 → 30.0 满宽' 算重量 (+1.215g/侧), "
              "**但覆盖边界 (X 起止) 我没有独立定过** —— 本单按 ISS-092 §8 的 L58.5..82.5 沿用 ⇒ 若你要别的起止, 给我数字我改。"
              "麦克风落位那条: 若骨架贯通全板 ⇒ 镜脚外侧面无 ≥40mm 合规落位 —— 与我的答复一致 (不贯通)。",
     "ref": "MECH/fit_check_v3_30mm.py §4 + MECH/SERVICE_PORT_ISS092.md §8 + 分片 skeleton_extent"},
    # ---- hw-lead iss121_mic_count_spec: 2× MEMS 外侧声孔间距 ≥40mm 做不到 ----
    {"key": "iss121_mic_count_spec", "to": "hw-lead",
     "value": "**接受你的建议: 每侧镜脚 1 颗 MEMS (L/R 一对)** —— 结构侧核算: 镜脚外侧面 ≥40mm 合规带确实只有板 X≤8.00 一处 "
              "(再往右到 X≥45 就离检修口通窗只剩 4.2mm, 且 §1.2 的通窗开口 X 49.21..59.41 也在那儿) ⇒ "
              "两孔间距 ≥40mm 在 **同一侧镜脚** 上做不到; 而 '镜框前框总宽 140mm' 的 L/R 跨距方案结构上零成本 "
              "(不占 PCB 面积、不加线、不改铰链区)。"
              "★**但我给一个你清单里没有的约束**: L/R 跨距 140mm 满足 '防声学串扰' 判据, 却不满足 "
              "'**单颗麦到同侧 PCB/SoC 的距离**' 这个电磁判据 —— 麦若装在镜框前框侧, 它离 **充电板/Type-C 座** "
              "(ISS-014 决策 5 已把充电板挪到镜框端件!) 就在同一块金属上 ⇒ **充电板的开关噪声与麦同处**, "
              "这比磁铁-麦间距更值得担心 (N35 静态场 vs 开关噪声)。⇒ 建议把麦放在充电板 **对侧** (即充电板在右端件 ⇒ 麦走左), "
              "并把 '麦 vs 充电板距离' 提为一条硬判据 (我的建议: ≥30mm, 需 sw-lead 复核 I2S/PDM 载流)。",
     "ref": "MECH/MECH_BUDGET.md §802 + MECH/SERVICE_PORT_ISS092.md §3.1"},
]

NEEDS_EXTRA = [
    {"key": "iss121_magnet_cover_y_wall_decision",
     "to": "main",
     "item": "ISS-092 盖板 **Y 向壁厚不达标** 待裁 (由 hw-lead iss121_magnet_xy_define U-1 引出, 我确认): "
             "磁铁 ⌀4.20 沉槽 + ≥2.10mm 壁 ⇒ 需 8.40mm, 盖板 Y 只有 7.60 ⇒ 沿 X 排后 **Y 向壁只剩 1.70 (缺 0.40)**。"
             "三个选项: ① 盖板 Y 7.60→8.60 (重量 +0.02g/侧) ② 磁铁改 ⌀3.0 (吸力降) "
             "③ 承认该处壁厚要求可降 (ISS-092 C-8 '磁铁不承结构力' ⇒ 1.70 壁在 PA-CF 上够不够需拉脱实测)。"
             "**我的假设: ③ (配合实测)**, Rev B 打印包已按 ① 之外的几何出好, 裁了我改一行即可。",
     "due": "2026-11-08", "since": "2026-11-01"},
    {"key": "iss092_magnet_soc_gap_correct",
     "to": "main",
     "item": "ISS-092 §4.3 '磁铁↔SoC 间距 ≥68mm' 是 **坐标系混算** (镜脚 L 减板 X) ⇒ 68.30 作废; "
             "按同一条链实际 **28.00mm** (磁铁 L100.30 vs SoC 逃线带末端 L72.30)。"
             "⇒ §0 结论 10③ 与 §10 诚实边界第 3 条的 '间距 ≥68mm 可达' 一并要订正, "
             "且 '对 SoC 大概率无影响' 的依据强度要降 (28mm 够不够取决于 SoC 磁敏感度 = [0数据])。"
             "**结构侧会把磁铁移到盖板 Y 居中 3.80, 落板后间距再变** ⇒ 请准许我按新位置更新 ISS-092 的这两处数字 "
             "(本单未改 ISS-092 正文 —— 它是已 verified 的文件, 改动需 PM 授权)。经项目总工",
     "due": "2026-11-08", "since": "2026-11-01"},
]

STATUS_EXTRA = {
    "phase": "P3(ISS-017 已 fixed: Rev B 打印包 + 89 项清单 + 探测记录 + 板宽30 干涉重算全交; 实物实测仍 0 件挂 needs(boss); "
             "另答复 hw-lead 5 条 (ISS-121/ISS-118) 并回填 PIN-SET-2 板宽30 新 Y 坐标)",
    "progress_pct": 92,
}


def main():
    def mutate(d):
        d.setdefault("answers", [])
        ak = {a.get("key") for a in d["answers"]}
        for a in ANSWERS:
            if a["key"] not in ak:
                d["answers"].append(a)
        d.setdefault("needs_from", [])
        nk = {n.get("key") for n in d["needs_from"]}
        for n in NEEDS_EXTRA:
            if n["key"] not in nk:
                d["needs_from"].append(n)
        d["status"]["phase"] = STATUS_EXTRA["phase"]
        d["status"]["progress_pct"] = STATUS_EXTRA["progress_pct"]
        d["updated_at"] = "2026-11-01T22:25:00+08:00"

    update_fragment("mech-lead", mutate)
    print("✅ 分片已更新")
    print("   answers 新增:", [a["key"] for a in ANSWERS])
    print("   needs_from 新增:", [n["key"] for n in NEEDS_EXTRA])
    return 0


if __name__ == "__main__":
    sys.exit(main())
