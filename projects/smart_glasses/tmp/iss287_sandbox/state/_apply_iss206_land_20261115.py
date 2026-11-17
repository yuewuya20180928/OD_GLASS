#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-206 落账脚本 (mech-lead) —— 只写 state/fragments/mech.yaml, 走 state/frag_write.py 原子写。

纪律:
  · 只写自己分片 (mech-lead)
  · 只碰: 裁 6 那两条 claim (只改 note, 不改 value) + 本单相关的 need/artifact + status
  · 不删别人的 key
"""
import os
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(PROJ, "state"))
from frag_write import update_fragment  # noqa: E402

NOTE_CARRIER = (
    "载板化后主板长12mm宽6层双面贴面积模型"
    " | ★ISS-206 (2026-11-15) 复核后【value 维持 69mm 不改】+ 补注来源: 本值是 "
    "MECH/SOC_CARRIER_EVAL.md 的 B 档 (BTB 载板化) **互斥方案** 的板长, 不是现行板板长 ——"
    " 同文件 §3/§5/§7 (A 直接焊 76 / B 载板 69, 且 A 超镜脚 1.3mm / B 余 5.2mm) 明确把两者当"
    " **两套互斥方案** 建模 (ISS-084 结论行亦写『拍板权留给项目总工』) ⇒ 按 ISS-206 裁 6 的闸:"
    " ★**这属方案取舍 (老板级), 不是数值订正 ⇒ 只报不改 + 登记 need 给 main** (need key="
    "iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice)。"
    "★现行 demo 板板长 = 60.00mm / 板宽 30.00 / 板厚 1.00 (6 层) (MECH/BOARD_GEOM_30MM.md §1),"
    " 另见同分片 claim pcb_length_proposed=60mm。"
)

NOTE_DIRECT = (
    "直接焊时主板长_与hw-lead_ISS-078一致76x12=912mm2"
    " | ★ISS-206 (2026-11-15) 复核后【value 维持 76mm 不改】+ 补注来源: 本值是 "
    "MECH/SOC_CARRIER_EVAL.md 的 A 档 (SoC 直接焊) **互斥方案** 的板长, 不是现行板板长 ——"
    " 同文件 §3/§5/§7 (A 直接焊 76 / B 载板 69) 明确把两者当 **两套互斥方案** 建模"
    " ⇒ 按 ISS-206 裁 6 的闸: ★**这属方案取舍 (老板级), 不是数值订正 ⇒ 只报不改 + 登记 need 给 main**。"
    "★本值同时是 BOARD_GEOM_30MM.md §1/§7 列的【作废值】之一 (板长 76) —— 但那说的是"
    " **现行 demo 板**; 本 claim 讲的是 **A 档方案** 的板长 ⇒ 两者不是同一个数, 不能互相覆盖。"
)

NEEDS = [
    {
        "key": "iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice",
        "to": "main",
        "item": (
            "★ISS-206 裁 6 的闸命中 ⇒ 本分片 interface_claims 的 mainboard_len_carrier=69mm 与 "
            "mainboard_len_direct=76mm **只报不改** (value 一字未动, 只补了 note 注明来源)。"
            "★**判据 (我自己复算的, 不猜)**: ①claim 语义 —— 两条 note 分别写『载板化后主板长』/"
            "『直接焊时主板长』; ②同域真源 MECH/SOC_CARRIER_EVAL.md §3 (A 直接焊 电池40.5+主板76+余15=131mm "
            "超1.3mm / B 载板 40.5+69+15=125mm 余5.2mm) + §5 表 (A 910mm2 / B 832mm2) + §7 结论"
            "『载板化把主板长度 76→69mm』⇒ **明确是 A/B 两套互斥方案**, 不是同一块板的两个口径; "
            "③ISS-084 结论行写明『拍板权留给项目总工』。"
            "⇒ **按 brief 的闸: 数值订正 = 方案取舍 = 老板级 ⇒ 只报不改 + 报你裁**。"
            "★**我的建议 (供裁, 不替你拍)**: ①若 A/B 方案已因 11-02『demo 一块板』作废 ⇒ "
            "这两条应整体标作废 (不是改成 60.00); ②若还要保留作对照 ⇒ value 保持 69/76 但 note 必须写明"
            "『A/B 方案板长, 非现行板板长』(本单已按此补注)。★**请明确一句: 这两条 claim 算『现行板长』"
            "还是『历史方案对照』?** —— 合并器只报两家都声明同 key 的冲突, 单边过期值它检不出来 "
            "(ISS-107 同型教训)。"
        ),
        "since": "2026-11-15",
    },
    {
        "key": "iss206_mech_hw_cross_review_escape_band_rk3572",
        "to": "main",
        "item": (
            "★ISS-206 裁 8 只报不改 (一字未动): MECH/hw_cross_review_check.py 的 soc_escape_x="
            "(20.20, 31.80) / hole_x=(5.00, 15.00, 55.00) 仍是 **旧 SoC (RK3576)** 的逃线带与固定孔位。"
            "★**理由 (两条, 都是既有裁决, 不是我的偏好)**: ①老板 10-29 10:07 口径『PCB 布线/布局类一律排队"
            "等原理图定稿』⇒ 逃线带 = 布局类; ②主控已从 RK3576 换成 RK3572 ⇒ 逃线带本身要重算 ⇒ "
            "属整链重出的一步, 换主控后单改这三个数只会造出【假绿/假红】。"
            "★**本单实测**: 该脚本 rc=0, 汇总 PASS 14 / FAIL 17 / 条件通过 8 / 说明 15 (共 54 项), "
            "★**分布未因本单变红** (本单一字没碰它) —— 其中 FAIL 里含『7.7 焊盘阵列与 SoC 逃线带间距 "
            "≥5.0mm (实测 18.70mm)』这类仍依赖旧逃线带位置的项, **整链重出时必须一起重算**。"
            "★**请裁**: 逃线带重算挂到哪一单 (整链重出计划 / 原理图定稿后单独一单)?"
        ),
        "since": "2026-11-15",
    },
    {
        "key": "iss206_mech_frag_claim_hinge_stack_24_vs_doc_25",
        "to": "main",
        "item": (
            "★ISS-206 边界内发现, **本单只报不改**: MECH/USB_HINGE_STRUCTURE.md 的 §9 claim 镜像行已按"
            "裁 2 改成 mech_hinge_stack_fixed_mm = 25.00 (16p/20p/4p/**10p** @0.5) 堆叠 余 12.00, "
            "但**本分片 state/fragments/mech.yaml 的同名 claim 仍是 value=24.00 + note 『收敛版 "
            "(16p/20p/4p/8p @0.5mm) 堆叠, 余 13.00』** ⇒ ★**文档与分片现在差 1.0 mm + 差一整套 8p 口径**。"
            "★**为什么我不动**: 本单边界明确『只许新增/改写本分片里 **裁 6 那两条 claim** 与 本单相关的 "
            "need/artifact 条目』⇒ 这条 claim 不在可写清单里 ⇒ 报你裁。"
            "★**建议**: 改成 value=25.00 + note 换 10p 口径 (与文档 §9 一致); 该 claim 已标"
            "『2026-11-06 标注: 仅供追溯, 现行板无跨铰链』⇒ 影响面 = 追溯口径, 不是活基线。"
            "★**顺带**: mech_hinge_stack_declared_mm=49.62 同样带旧 8p/40p 口径, 也在文档 §9 镜像范围内。"
        ),
        "since": "2026-11-15",
    },
    {
        "key": "iss206_mech_close_iss202_203_needs_via_main_answers",
        "to": "main",
        "item": (
            "★ISS-206 已按你的裁决把 ISS-202 / ISS-203 登记的 8 条 need 全部执行完毕 (裁 1~5 + 裁 7 已改完并"
            "实测通过, 裁 6/裁 8 按闸只报不改并各登记 1 条 need)。但 **state/fragments/pm.yaml 里没有这 8 条"
            "key 的 answer** ⇒ merge.py 的闭单口径 (需求 (owner,key,to) 被闭合 ⟺ 存在 key 相同且 **作者 = to**"
            " 的答复) 认不到 ⇒ ★**Q4 需求闭环率上这 8 条仍算『等 main 回音』**。"
            "★**要你做**: 在 pm.yaml 落这 8 条 key 的 answer (作者必须是 main)。"
            "★**8 条 key**: iss202_mech_doc_residual_jchg_old_6pin / iss202_mech_script_recommended_pins_"
            "jchg_8 / iss202_mech_other_docs_jchg_old_pinmap / iss202_mech_c4_stack_arith_pending / "
            "iss203_mech_service_port_doc_15mm_margin / iss203_mech_claim_mainboard_len_carrier_direct / "
            "iss203_mech_service_port_pinset2_baseline_15mm / iss203_mech_service_port_pcb_thk_4layer。"
            "★另: iss203_mech_hw_cross_review_old_escape_and_holes 那条 = 本单的裁 8, 已由 "
            "iss206_mech_hw_cross_review_escape_band_rk3572 细化。"
        ),
        "since": "2026-11-15",
    },
]

ARTIFACTS = [
    ("MECH/hinge_usb_check.py",
     "ISS-206 裁 1: RECOMMENDED_PINS[J_CHG] 8 -> 10 (对齐网表真源 1x10p@0.5mm); 注释里的老 6 脚期拆脚说法"
     "(SYSx2 载流 / VBUS_DET / BAT_DET 跨铰链) 一并改掉, 并逐脚写清 10p map (pin1/2=BAT_CHG, pin3/4=GND, "
     "pin5=CHG_STAT, pin6=PWR_GOOD, pin7=NC, pin8=TS_BAT, pin9/10=HINGE_RSV)。★改前/改后两套跑法已贴: "
     "8p => 收敛版 24.0mm 且 FAIL 1 (正文 25.0 与脚本 24.0 不一致); 10p => 收敛版 25.0mm 且 FAIL 0。★FAIL->PASS "
     "的根因 = pin 数本身 (8->10 = +2 脚 x 0.5 = +1.0mm), 不是判据放宽。"),
    ("MECH/USB_HINGE_STRUCTURE.md",
     "ISS-206 裁 2: 11 处旧口径 + 5.2 F-3 全部按 10p 真源改 (脚数 / pin map / 跨铰链归属 / 防呆措辞 / "
     "反插风险描述); 3.2b 声明版行 + 收敛版行 + 7 占位行 + 9 claim 注 + 5.3 C-4 算式行 五处统一 "
     "(声明版 31.50 / 收敛版 25.00 / 触点区 21.00 / 堆叠 25.00); C-4 按裁决写两套算式并加注记"
     "(脚本 16+20+4+10=50脚@0.5=25.0mm 堆叠; 行内 8+20+4+10=42脚@0.5=21.0mm 触点区 + 4x1.0mm 间隙 = 25.0mm "
     "堆叠; 两套 connectors 组成不同, 最终都落 25.0mm, 差的只是触点区那一格)。"),
    ("MECH/FPC_FAB_NOTES.md",
     "ISS-206 裁 3: N-6 (pin10 不再走 TS 专用回流, 现 HINGE_RSV; 跨铰链 TS 只剩 pin8 一根) + I-5 "
     "(反插 = BAT_CHG 落 HINGE_RSV 断路 + GND<->TS_BAT 短 + CHG_STAT<->PWR_GOOD 短; 防呆仍必需但理由已换)。"
     "只改 pin map / 跨铰链归属 / 防呆措辞, 未动任何几何数字。"),
    ("MECH/RELIABILITY_TEST_PLAN.md",
     "ISS-206 裁 3: R10 (J_CHG 1x10p@0.5 + BAT_CHG 双脚并联, SYS 不跨铰链) + T-14 失效模式 + T-14 判据"
     "(★判据本身改了: 反插位型下 BAT_CHG 对 HINGE_RSV 为断路不得导通; GND<->TS_BAT 与 CHG_STAT<->PWR_GOOD "
     "各自成短, 必须由防呆阻断) + 失败定义 + K-11 (10p) + K-12 (脚数已落定 10p, 8p 口径作废)。"),
    ("MECH/STRUCT_REVIEW_ISS065.md",
     "ISS-206 裁 3: R3 —— 跨铰链方向已无 VBUS_DET 分压信号 (2026-11-04 起 VBUS_DET 改主板本地分压, "
     "J_CHG pin7=NC), 想恢复关机插电时充电灯亮只能另跨一根 VBUS 电源线占 pin9/pin10 预留脚之一; "
     "只改 pin map / 跨铰链归属 / 防呆措辞, 未动几何数字。"),
    ("MECH/SERVICE_PORT_ISS092.md",
     "ISS-206 裁 4: 正文 15mm 口径 -> 现行 60x30 口径 (V PCB 段 需求 21.00 -> 36.00, 余 +17.00 -> +2.00, "
     "最坏 +1.40, 单边口径 +1.70; 1.6.2 三条余量 0.95/17.00/14.50 -> 0.95/2.00/14.50); 数字全部取自 "
     "python3 MECH/service_port_check.py 的输出, 零手算。"),
    ("MECH/service_port_check.py",
     "ISS-206 裁 5 + 裁 7: pcb_thk 0.80 (4 层) -> 1.00 (6 层现行, BOARD_GEOM_30MM.md 1) => H 链需求 "
     "4.20 -> 4.40, 余 +3.10 -> +2.90 (仍 > 判据 0.60); ★裁 7 夹具基准 p2_y=7.50 / s2_y=12.50 / "
     "jd_y0=9.50 **数字一字未动**, 只加了一行注记标明这套基准已作废 (现行基准见 BOARD_GEOM_30MM.md 1) + "
     "只换数字会让 7.4 式符号反过来造假红 + 真正迁移留整链重出。实测 rc=0, 54/54 一致, FAIL 0。"),
    ("HANDOFF/2026-11-15_mech-lead_ISS206_J_CHG旧口径一次性收口.md",
     "ISS-206 交接单 (B1 结论 / B2 验收自评 / B3 证据分级 / B4 接口取值 / B5 未决与卡点 U-1~U-6 / "
     "B6 复现命令 + 裁 1 改前改后两套跑法 + 每个数字变化属于哪一类 + grep 残留逐行归类 + 边界自检)。"),
]


def mutate(d):
    # ---- 裁 6: 只改这两条 claim 的 note (value 不动) ----
    hit = 0
    for c in d.get("interface_claims", []):
        if c.get("key") == "mainboard_len_carrier":
            c["note"] = NOTE_CARRIER
            c["ref"] = "MECH/SOC_CARRIER_EVAL.md 3/5/7 (A/B 互斥方案) + MECH/BOARD_GEOM_30MM.md 1"
            hit += 1
        elif c.get("key") == "mainboard_len_direct":
            c["note"] = NOTE_DIRECT
            c["ref"] = "MECH/SOC_CARRIER_EVAL.md 3/5/7 (A/B 互斥方案) + MECH/BOARD_GEOM_30MM.md 1/7"
            hit += 1
    assert hit == 2, f"裁 6 两条 claim 没找全 (hit={hit})"

    # ---- need: 去重后追加 ----
    have = {n.get("key") for n in d.get("needs_from", [])}
    for n in NEEDS:
        if n["key"] not in have:
            d.setdefault("needs_from", []).append(n)

    # ---- artifact: 去重后追加 ----
    havep = {a.get("path") for a in d.get("artifacts", [])}
    for path, summary in ARTIFACTS:
        if path not in havep:
            d.setdefault("artifacts", []).append({
                "path": path, "kind": "note", "version": "1.0",
                "updated_at": "2026-11-15", "summary": summary,
            })

    # ---- status ----
    d["updated_at"] = "2026-11-15"
    d["updated_by"] = "mech-lead"
    st = d.setdefault("status", {})
    st["phase"] = "P3"
    st["progress_pct"] = 97
    st["health"] = "yellow"
    st["summary"] = (
        "2026-11-15 ISS-206 (结构侧 J_CHG 旧口径一次性收口): ★**结构侧已无第 3 套 pin map** —— "
        "脚本活口径 RECOMMENDED_PINS[J_CHG]=10 (改前/改后两套跑法已贴: 8p=>收敛版 24.0mm + FAIL 1, "
        "10p=>25.0mm + FAIL 0; 根因=pin 数本身 8->10 = +2x0.5 = +1.0mm, 不是判据放宽); "
        "11 处文档旧口径 + 5.2 F-3 + 3 份文档 (FPC N-6/I-5, RELIABILITY R10/T-14/K-11/K-12, ISS065 R3) "
        "全部按 1x10p@0.5mm 逐脚真源改齐; ★**T-14 判据本身已改** (反插 = BAT_CHG 落 HINGE_RSV 断路 + "
        "GND<->TS_BAT 短 + CHG_STAT<->PWR_GOOD 短, 防呆仍必需但理由换了); 检修口文档 15mm -> 60x30 "
        "(V PCB 段 36.00/余+2.00/最坏+1.40); 板厚 0.80 -> 1.00 (H PCB 4.40/余+2.90)。"
        "★**裁 6/裁 8 按闸只报不改**: 裁 6 两条板长 claim (69/76) 判为 **A/B 互斥方案板长** (非同一块板两口径) "
        "=> 方案取舍属老板级, value 一字未动, 只补 note 注来源 + 登记 need; 裁 8 逃线带/孔位一字未动 "
        "(RK3576->RK3572 + 整链重出)。★**新登记 4 条 need 给 main**: 裁 6 方案取舍 / 裁 8 逃线带重算挂哪单 / "
        "分片 claim mech_hinge_stack_fixed_mm 仍 24.00 (文档已 25.00, 边界不许我改) / ISS-202+203 八条 need "
        "请 main 在 pm.yaml 落 answer (否则 Q4 认不到闭单)。★**边界自检**: HW/** 一字未动 "
        "(网表 md5 c78f991283cc82d56c8e3dd31657c785 / 板 611b869e13518c3c023fb178f91a0075 均未变); "
        "没碰 issue_log / PROJECT_TRACKER 0 / 别人的分片 / MECH/print / BOARD_GEOM_30MM; 零外发; "
        "判据阈值一个没松; 没碰 PCB 布线布局。★**证据边界**: 实物 [实测] 仍 0 条 (0 件打印 / 0 台样机) "
        "=> 全部数是 [推算]/[实测-脚本]; J_DEBUG 阵列在 30mm 板上的 Y 仍 [0数据] (迁移随整链重出)。"
    )


if __name__ == "__main__":
    update_fragment("mech-lead", mutate)
    print("✅ mech.yaml 已原子更新 (ISS-206 落账)")
