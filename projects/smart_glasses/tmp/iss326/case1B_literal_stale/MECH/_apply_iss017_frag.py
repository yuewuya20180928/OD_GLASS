#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-017 分片更新 (mech-lead, 2026-11-01) —— 走 state/frag_write.py 的原子写。

纪律: **不手改分片文件** —— 一律用 state/frag_write.py 的 update_fragment。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

NEEDS = [
    # ① 本地无法完成打印/量测 —— 要什么才能解 (waiting_on=boss)
    {"key": "iss017_local_print_measure_unblock",
     "to": "boss",
     "item": "ISS-017 实物实测 0 件的解锁条件 (本机物理上做不到, 证据 MECH/print/ENV_PROBE_20261101.md): "
              "打印机 192.168.1.68 与本机 192.168.2.4/24 跨网段不可达 (ping 无响应 + TCP 990/8883/6000/4000 全 closed); "
              "无切片器 (Bambu Studio/OrcaSlicer/Cura 均无); 无卡尺/千分尺/塞尺; 无 USB 串口 (电子卡尺也接不上); "
              "gateway 主机=本机 (无第二台可借道)。"
              "⇒ 请指定以下之一: ① 把打印执行方接入 192.168.1.0/24 或开子网互通 ② 委托代打印服务 ③ "
              "在能装 Bambu Studio 的桌面环境切片并由第三方打印。量测侧需: 数显卡尺(0.01mm) + 塞尺(0.02mm一档) + "
              "弹簧秤(0-25N) + 电子秤(0.01g), 或由打印方代测回填。"
              "已交付: Rev B 打印包可直接下片 (MECH/print/*_revb.stl, 自检 93/93 + 38/38 rc=0) + 89 项测量清单。"
              "执行方定下来后按 MEASURE_CHECKLIST.md 填表回填 measurements.yaml (M-PRINT kind 改成 实测) 即可解锁阶段门 G2。"
              "经项目总工转达",
     "waiting_on": "boss",
     "due": "2026-11-08",
     "since": "2026-11-01"},
    # ② 波导彩虹纹指标 (ISS-017 第二项, [0数据])
    {"key": "iss017_waveguide_rainbow_metric",
     "to": "jbd",
     "item": "ISS-017 第二项: 波导 **彩虹纹指标** 缺失 [0数据] —— JBD/波导厂未选型 ⇒ 无 2D 外形图 / 无耦入区 / 无容差角 / "
              "无彩虹纹指标。请给: ① 亮度均匀性指标 (目视彩虹纹可否接受/判定方法) ② 色差指标 (ΔE 或目视色偏判据) "
              "③ 应力敏感度 (装配应力是否引起彩虹纹, 对装配公差的要求) ④ AR 镀膜方案与耐久性 ⑤ 波导 2D 外形图 (卡镜框 3D 打印开工, "
              "采购周期 4-8 周)。"
              "结构侧能做什么/不能做什么: **能做** —— 控制装配应力 (沉槽/压垫/对称压紧) 以避免应力型彩虹纹; "
              "**不能做** —— 膜层本身的色差与亮度均匀性由波导厂镀膜决定, 结构改不了; "
              "⇒ 该指标缺失时, 结构侧只能给出'应力项可控'的结论, 给不出'彩虹纹合格'的结论。"
              "经项目总工走 JBD 销售 (我不外联)",
     "waiting_on": "jbd",
     "due": "2026-11-08",
     "since": "2026-11-01"},
    # ③ 板厚档位 → 检修口净空 (新发现的硬冲突)
    {"key": "iss017_pcb_thickness_vs_service_port_clearance",
     "to": "hw-lead",
     "item": "ISS-017 结构侧新发现 (需 hw-lead 定板厚档位后回算): "
              "**ISS-092 检修口净空 = 7.30 − (0.80 皮肤壁 + 0.50 隔热垫 + 0.30 空气隙 + PCB 板厚)**, "
              "⇒ 板厚 0.41 → 5.29 ✅ / 0.80 → 4.90 ✅ / 1.00 → 4.70 ✅ / **1.22 → 4.48 ❌ 差 0.02 破 ISS-085 的 4.50 硬要求**。"
              "ISS-122 (esc_layer_models_check.py) 两套模型对撞给出 9 层(1.22) vs 3 层(0.41), 4-6 层锁死下 0.80/1.00 —— "
              "**板厚档位未定 ⇒ 检修口净空就无法定**。请给: ① 最终板厚档位 (或 PCB 厂 DFM 报告) ② 若只能 1.22, "
              "结构侧的建议是把隔热垫+空气隙从 0.80 压到 0.60 (净空回到 4.68) —— 但这会削薄隔热链, 需 sw-lead 复核 43°C。"
              "另: **PIN-SET-2 孔位的 Y 坐标按板宽 15 定 (Y 0..15), 板宽 30 后 Y 全部作废** ⇒ 请一并重定 Y "
              "(X 坐标 8.00/52.00 不变, 板长 60 未变)。经项目总工转达",
     "waiting_on": "hw-lead",
     "due": "2026-11-15",
     "since": "2026-11-01"},
    # ④ 镜框截面口径 (板宽 30 的自由文本表述 vs 本域锁死链)
    {"key": "iss017_board_width_direction_clarify",
     "to": "main",
     "item": "ISS-017 口径待确认: PROJECT_TRACKER §(1.43) 那句 '镜腿截面从 15×7.3mm → 30×7.3mm' 是 **自由文本表述**, "
              "与本域三条锁死尺寸链 (镜脚内腔 H 7.30 × V 38.00 × L 130.00) 不对应 —— 7.3 是前后厚, 而 30 若指板宽则是 V 向尺寸。"
              "本单按 **板宽 = V 向** 计算 (与 BOARD_WIDTH_15MM.md §1.2 + HW/pcb60x30_check.py 的独立复算一致), "
              "结论: V 余量 17.00 → **2.00** (最坏 1.40), 板宽硬顶 31.40mm; H/L 链一字不动。"
              "请确认: 板宽 30mm 是否就是 **V 向** (镜脚垂直方向)? 若 boss 的本意是 '镜腿横截面宽 30mm', "
              "那是 **另一条链 (H 向)**, 7.3mm 前后厚根本放不下 ⇒ 请给口径, 我按你给的口径重算。",
     "due": "2026-11-08",
     "since": "2026-11-01"},
]

CLAIMS = [
    {"key": "pcb_outline", "value": "60x30mm",
     "note": "★板宽 15 → **30mm** (老板 10-29 19:16 拍板, §0 台账 11-01 20:5x 订正) + 板长 60 (ISS-100); "
             "60x30=1800mm² ⇒ RK3576 装得下 (余 122.3mm², ISS-118); 板宽是 **V 向** 尺寸 ⇒ 镜脚 V 余量 17.00 → 2.00 (最坏 1.40), "
             "板宽硬顶 31.40mm; PCB 板重 1.332 → 2.664g (4层)",
     "ref": "HW/PCB_OUTLINE_60x15.md + HW/CHIP_SELECTION_DECISION.md §0 + MECH/fit_check_v3_30mm.py"},
    {"key": "pcb_board_width", "value": "30mm",
     "note": "老板 10-29 19:16 拍板 (§(1.43) '板宽可以放到 30mm 以内' + 量产先例背书); "
             "★结构侧代价 = **V 链从 17.00 掉到 2.00mm (最坏 1.40)**, 板宽硬顶 31.40mm; H/L 链不动; "
             "电池空间/续航不变 (串行排布, 板宽只吃 PCB 段的 V)",
     "ref": "MECH/fit_check_v3_30mm.py §1"},
    {"key": "mfit_scope", "value": "镜脚侧通过(V链临界)/镜框侧未验",
     "note": "M-FIT v3 (板宽 30 基线): 镜脚侧 V 余量 2.00 (最坏 1.40) ✅过判据 0.60 但比板宽15少15.00; "
             "H 控制段 (电芯段) 6.35 余 0.95/最坏 0.65 不动; L 余 14.50 不动; "
             "★板厚 1.22 档 ⇒ 检修口净空 4.48 破 4.50 硬要求 (待板厚档位); 镜框侧缺 u1/u4/u8b/u5 ⇒ 未验",
     "ref": "MECH/fit_check_v3_30mm.py"},
    {"key": "mprint_status", "value": "0件已打/RevB包就绪",
     "note": "M-PRINT 实物实测 = 0 数据 (本机跨网段不可达打印机 + 无切片器 + 无量具, 证据 ENV_PROBE_20261101.md); "
             "已交付 Rev B 可直接下片打印包 + 89 项测量清单 + 自检 93/93 + 38/38; "
             "kind 保持 推算 (未冒充实测), 升级路径 = needs_from iss017_local_print_measure_unblock",
     "ref": "MECH/print/README.md"},
    {"key": "sp_clearance_vs_pcb_thickness", "value": "4.48-5.29mm",
     "note": "ISS-092 检修口净空 = 7.30-(0.80皮肤壁+0.50隔热垫+0.30空气隙+板厚) ⇒ 板厚 0.41/0.80/1.00/1.22 → "
             "5.29/4.90/4.70/**4.48**; ISS-085 硬要求 ≥4.50 ⇒ **板厚 1.22 档差 0.02 不通过**; "
             "板厚档位待 hw-lead + PCB 厂 DFM (ISS-122)",
     "ref": "MECH/fit_check_v3_30mm.py §2 + MECH/SERVICE_PORT_ISS092.md C-5"},
    {"key": "print_pack_rev", "value": "B",
     "note": "打印包 Rev B (2026-11-01): 板宽 30/板长 60/RK3576/PIN-SET-2/ISS-092 检修口/Type-C 移镜框端件; "
             "Rev A (板宽 12 口径) 已过期不可再打; 自检 93/93 尺寸判据 + 38/38 STL↔规格逐点互验 (rc=0); "
             "测量清单 89 项有效待测",
     "ref": "MECH/print/README.md"},
    {"key": "temple_v_margin", "value": "2.00mm",
     "note": "板宽 30 + 走线槽 6 = 36.00 vs 镜脚净高 38.00 ⇒ 余量 2.00 (最坏 1.40); 板宽硬顶 31.40mm; "
             "板宽 15 时为 17.00 ⇒ 掉了 15.00",
     "ref": "MECH/fit_check_v3_30mm.py"},
]

STATUS = {
    "phase": "P2(ISS-017 闭环: Rev B 打印包 + 89 项清单 + 探测记录 + 板宽30 干涉重算全部交付; 实物实测仍 0 件, 挂 needs_from(boss))",
    "progress_pct": 90,
    "health": "yellow",
    "summary": (
        "ISS-017 (打印件实测 0 件 + 彩虹纹指标缺失) 走任务书允许的 '本环境无法实际打印/量测' 分支交付, 4 项全交: "
        "① **Rev B 打印包可直接下片** (MECH/print/*_revb.stl) —— Rev A 已过期 (板宽 12mm 口径), "
        "Rev B 按 **板宽 30 / 板长 60 / RK3576 / PIN-SET-2 / ISS-092 检修口** 重做, Type-C 面板移到镜框端件; "
        "自检 **93/93 尺寸判据 + 38/38 STL↔规格逐点互验 (rc=0)** —— "
        "★方法论改进: 放弃 '在 STL 上量尺寸' (绕向不一致/共面内部面/射线内起点/坐标混用 4 个坑), "
        "改成 '解析模型精确求尺寸 + STL 逐点互验' 两段式; "
        "② **逐项测量清单 89 项有效待测** (新增板宽30 的 PCB 样板/PIN-SET-2/板厚三档/V余量梳、ISS-092 检修口壁7+盖板9、ISS-065 5 项); "
        "③ **环境探测记录** (ENV_PROBE_20261101.md, 本人实测) —— 打印机跨网段不可达/无切片器/无量具/无 USB 串口, "
        "并**更正 10-25 旧记录 '无外网' 的错误** (pip 实测可通); "
        "④ **needs_from**: boss (打印+量测执行方, due 11-08) + jbd (波导彩虹纹指标, due 11-08) + hw-lead (板厚档位/PIN-SET-2 的 Y) + main (板宽方向口径)。"
        "★**新发现 (板宽 30 的连带)**: ① **V 链是唯一被板宽打穿的链** —— V 余量 17.00 → **2.00** (最坏 1.40), 板宽硬顶 31.40mm; "
        "② **板厚 1.22 (ISS-122 模型A) ⇒ ISS-092 检修口净空 4.48 < 4.50 硬要求** (0.41/0.80/1.00 → 5.29/4.90/4.70 ✅); "
        "③ 电池空间/续航 **不变** (串行排布, 板宽只吃 PCB 段的 V); ④ 重量 PCB +1.33~1.67g + 骨架 +1.22g/侧 ⇒ 整机 +3.76~4.10g ⇒ 52.7-78.1g。"
        "**诚实边界**: 实物 M-PRINT = 0 件 0 数据 (kind 保持推算, 未冒充实测); 镜框侧光机/波导干涉 **无法判定**; "
        "彩虹纹指标 [0数据] (JBD 未选型)。未联系任何供应商/原厂, 未改 HW/ SW/ PROJECT_TRACKER.md DECISIONS.md。"
    ),
}


def main():
    def mutate(d):
        d.setdefault("needs_from", [])
        keys = {n.get("key") for n in d["needs_from"]}
        for n in NEEDS:
            if n["key"] not in keys:
                d["needs_from"].append(n)
        d.setdefault("interface_claims", [])
        ck = {c.get("key") for c in d["interface_claims"]}
        for c in CLAIMS:
            d["interface_claims"] = [x for x in d["interface_claims"] if x.get("key") != c["key"]]
            d["interface_claims"].append(c)
        d["status"] = dict(STATUS)
        d["updated_at"] = "2026-11-01T21:40:00+08:00"
        d["updated_by"] = "mech-lead"

    update_fragment("mech-lead", mutate)
    print("✅ 分片已更新 (走 state/frag_write.py 原子写)")
    print("   needs_from 新增/覆盖:", [n["key"] for n in NEEDS])
    print("   interface_claims 更新:", [c["key"] for c in CLAIMS])
    return 0


if __name__ == "__main__":
    sys.exit(main())
