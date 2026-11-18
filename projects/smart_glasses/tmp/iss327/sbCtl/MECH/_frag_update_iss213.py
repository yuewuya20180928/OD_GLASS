#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-213 分片原子写脚本 —— 结构侧 54 项交叉复核逐条定性表 + demo 板真缺陷收口

走 state/frag_write.py 的 update_fragment (tmp + fsync + os.replace), 全程零 open(p,"w").
纪律:
  * 只写自己 (mech-lead) 的分片
  * 只【新增】artifact / claim / need —— **一个别人的 key 都不删不改**
  * ★本单【不改值】: 分片 claim `mech_hinge_stack_fixed_mm` **实测已是 25.00**
    (ISS-209 已按 ISS-206 裁 2 的 16p/20p/4p/10p 收掉) ⇒ 本单只复核, 不重复写
    (若再写一次会造成同 key 两条 ⇒ 合并器会报重复)
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
        "path": "MECH/HW_CROSS_REVIEW_TRIAGE.md",
        "kind": "spec",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-213 交卷件: 结构侧 54 项交叉复核**逐条定性表** (项号/现状判定/关键数字/demo 相关性/"
            "MECH 地界/处置/恢复条件/证据等级, 54/54 一处不漏, 处置栏无一条留空或写'待定') + "
            "**17 条 FAIL 逐条去处表** (排队等原理图定稿 6 个 id / 7 行 + 登记 need 给 main 4 条 + "
            "出规格 6 条) + 6 个 PCB 类 id 的**排队表 + 恢复条件** + demo 板当前成立的 6 条真缺陷"
            "收口记录 (Type-C 开孔 / 印刷公差 / buck 功率守恒 / 端件温升口径 / 散热路径 / 腔体) + "
            "ISS-126 真实状态结论 (交 main 裁) + **机器可读锚点 yaml 块** (门禁按它复核, 改锚点=改判据⇒门禁红)。"
            "★关键数: 现口径 9.50×3.60 最坏单边 0.13/0.02、ISS-089 建议 10.00×4.20 最坏 0.38/0.32 "
            "(判据 0.60 ⇒ **两档现候选都判不合格, 打印包的'二选一'是假选择**) ⇒ 新出 **10.50×4.80** "
            "(FDM 直成型, 最坏 0.63/0.62) 与 **10.25×4.55** (金属·CNC ±0.05, 最坏 0.63/0.62); "
            "端件温升按 buck 口径 0.45–0.57W ⇒ ΔT 83K ⇒ 108°C, 60°C 判据 ⇒ P_max 0.21W ⇒ "
            "打印件 R=1944 K/W (0.5W 打进去 +972K 不可能) vs 铝 1.64 K/W (+0.82K) ⇒ **必须金属热路**; "
            "功率守恒 ICHG/IIN = η·Vbus/Vbat = 1.216 (3.70V) / 1.071 (4.20V), 规格书 0.822/0.933 是倒数 "
            "⇒ 390Ω 档单 pin 0.50–0.61A 超 0.5A 额定; 检修口内腔 7.30−2.60 = 4.70 ≥ cavity_req 4.50 "
            "(余 +0.20) ⇒ **ISS-126 的前提已被现口径超越**。★[实测]实物 = 0 条 (几何/热学全为 [推算])。"),
    },
    {
        "path": "MECH/check_demo_struct_truth.py",
        "kind": "check",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-213 机器门禁: **20 组检查** (rc=0 全过 / rc=2 有红, 失败点名哪一组)。★它守的是 "
            "**'demo 板当前成立的条目', 不是'54 项全绿'** ⇒ G1/G1b **不许把红灯调没** (断言 "
            "hw_cross_review_check.py 的 FAIL 名单仍是 17 条且逐条对齐, 谁改判据/阈值/把 FAIL 抹成 PASS "
            "⇒ 立刻红) · G2 demo 当前项**独立复算**全过 (内腔 4.70≥4.50 / 新开孔两档最坏单边 ≥0.60 / "
            "两档现候选判不合格 / buck 温升 108°C / P_max 0.21W / 金属 vs 打印件热阻 / 功率守恒 "
            "1.216·1.071 / demo PASS 12 项) · G3/G3b 6 个 PCB 类 id **已登记排队且恢复条件非空**, "
            "且**在 check 脚本里仍然是 FAIL** (不许修绿) · G4/G4b 板框四数 60.00/30.00/1.00/3.33g "
            "没被改 · G5/G5b 判据阈值 (cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00) 未松 "
            "+ 8 个受保护文件 md5 逐字节未变 · G6/G6b 定性表 54 项全覆盖 + 处置不留空 + 17 条 FAIL "
            "每条都在受控词表里 · G7 分片 claim mech_hinge_stack_fixed_mm = 25.00; "
            "★`--selftest` **8 个反向用例全被抓** (板宽/判据/开孔/耗散/FAIL 名单/排队表/板重/cavity_req "
            "任一改坏 ⇒ 必须变红)。★**本闸是否挂每日巡检交 main 裁 —— 本单没改 state/daily_check.py**。"),
    },
    {
        "path": "HANDOFF/2026-11-15_mech-lead_ISS213_结构54项定性表与demo真缺陷收口.md",
        "kind": "handoff",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-213 交接单 (B1~B6 齐全, 27 行): B1 结论 6 条 (54/54 定性 · 17/17 FAIL 有去处 · "
            "机器门禁 20/20 + selftest 8/8 · CHG-OPEN 真根因与第三档口径 · 端件温升/功率守恒/金属热路 · "
            "ISS-126 真实状态) + B2 逐条自评 + B3 证据分级 + B4 接口取值 5 条新 claim + B5 未决项 7 条 "
            "(交 main 的 6 条新 need / 打印包第三档 / MECH_BUDGET 文字 / u8 / ISS-126 裁 / 挂巡检 / "
            "不替老板拍) + B6 自证复现命令 (含 8 个 md5)。"),
    },
    {
        "path": "MECH/_frag_update_iss213.py",
        "kind": "script",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-213 分片原子写脚本 (走 state/frag_write.py 的 update_fragment): 新增 4 artifact / "
            "5 claim / 6 need; ★**不改任何已有 claim 的 value** (U-3 的 mech_hinge_stack_fixed_mm "
            "实测已是 25.00, ISS-209 已收 ⇒ 本单只复核不重复写); 禁 open(p,\"w\"); 只动自己分片。"),
    },
]

CLAIMS = [
    {
        "key": "mech_typec_panel_opening_spec",
        "value": "10.50x4.80(FDM直成型)/10.25x4.55(金属·CNC)",
        "note": (
            "★ISS-213 (2026-11-15) 结构侧现行口径: 镜框端件 Type-C 面板开孔。★**根因**: 原口径只把"
            "**名义**间隙推到 0.47 (10.0×4.2 档), **没在最坏公差下验判据** ⇒ 现口径 9.50×3.60 的最坏单边 "
            "X 0.13 / Y 0.02, ISS-089 建议 10.00×4.20 的最坏 X 0.38 / Y 0.32 (判据 0.60) ⇒ **两档现候选 "
            "都判不合格, 打印包的'两档并行试样'是假二选一**。★**本单新出**: ①FDM 直成型 **10.50×4.80** "
            "(最坏 0.63/0.62 ✅, 端件面板最小外形 13.50×7.80 含承力壁 ≥1.50) ② 金属嵌件/CNC ±0.05 "
            "**10.25×4.55** (最坏 0.63/0.62 ✅, 外形 13.25×7.55); ★**该特征不得靠打印面成型** ⇒ 打印后"
            "扩孔 (±0.10) 或金属嵌件 (±0.05)。判据出处: 母座本体 8.94×3.26 [官方] + FDM ±0.30 + CRIT "
            "= 2×0.30 = 0.60。★下游未动: HW/CHARGE_BOARD_SPEC.md M-15 (名义+公差, 归 hw-lead) + "
            "MECH/print/gen_print_pack_revb.py 要加第三档试样 (交 main 排期)。[推算]"),
        "ref": "MECH/HW_CROSS_REVIEW_TRIAGE.md §5.1 + §1 anchors.typec_panel",
    },
    {
        "key": "mech_endpoint_surface_temp_caliber",
        "value": "buck: 83K/108C@0.50W; 60C判据⇒P_max=0.21W",
        "note": (
            "★ISS-213 端件外表面温升**现行口径 = buck** (P10 网表有 SW/L_CHG/C_BST/PMID ⇒ 开关型 "
            "buck, 耗散 = Pin−Pout+DCR = 0.45–0.57W), **不是** MECH_BUDGET §2.1 的 0.8W (那是线性"
            "稳压器公式 (5−4.2)×I ⇒ 对 buck 不适用, 本单判死该口径)。端件外表面 R_conv = 1/(10 W/m²K × "
            "0.030×0.020 m²) = 166.67 K/W ⇒ P=0.50W ⇒ ΔT **83K ⇒ 表面 108°C** (0.8W 口径 ⇒ 133K ⇒ "
            "158°C); ★**60°C 判据 ⇒ P_max = (60−25)/166.67 = 0.21W** ⇒ 现耗散超 **2.4–2.7×** ⇒ "
            "**必须金属热路** (打印件沿臂 70mm R = 1944 K/W ⇒ 0.5W 打进去 +972K 不可能; 铝6063 同几何 "
            "R = 1.64 K/W ⇒ +0.82K)。验收: B1 批端件表面 (充电板正上方) 充电 1A 稳态 30min 实测 ≤60°C; "
            "老板已拍'边戴边充不允许' ⇒ 43°C 皮肤红线不适用, 但端件表面仍要过 60°C (烫手)。[推算]"),
        "ref": "MECH/HW_CROSS_REVIEW_TRIAGE.md §5.3/§5.4",
    },
    {
        "key": "mech_mech_budget_linear_0p8w_dead",
        "value": "0.8W线性口径已作废(P10是buck)",
        "note": (
            "★ISS-213 判定: `MECH/MECH_BUDGET.md` §2.1 的『**0.8 W @ 1A** (IC 自身耗散 = (5−4.2)V × 1A)』"
            "是**线性充电 IC** 的公式, 而 P10 充电板是**开关型 buck** ⇒ 该口径对现行方案**不适用 (判死)**; "
            "现行耗散口径 = 0.45–0.57W (Pin−Pout+DCR), 端件温升口径见 claim "
            "`mech_endpoint_surface_temp_caliber`。★**本单未改 MECH_BUDGET 那一行** (它牵 "
            "`MECH/verify_budget.py` 的 P_CHARGE 常量 = 0.8 与 §2.3 皮肤热链) ⇒ 文字改动交 main 排期。"),
        "ref": "MECH/HW_CROSS_REVIEW_TRIAGE.md §5.3 + MECH/MECH_BUDGET.md §2.1",
    },
    {
        "key": "mech_iss126_current_status",
        "value": "内腔4.70>=4.50余0.20⇒前提已被现口径超越",
        "note": (
            "★ISS-213 复核 (2026-11-15): `state/issue_log.yaml` 的 **ISS-126** (open / owner=main / due "
            "2026-11-05) 至今仍按「板厚 0.41/0.80/1.00/1.22 四档都有可能, **只有 0.80 及以下才安全**, 1.22 档"
            "净空 4.48 破 4.50」在写, 并把解锁条件挂在「等 PCB 厂 DFM 报告 (ISS-122)」。★**但结构真源现行"
            "板厚就是 1.00mm (6 层)** (`MECH/BOARD_GEOM_30MM.md` §1 + `MECH/service_port_check.py` BASE "
            "`pcb_thk`=1.00, 注释「6 层现行; 4 层 0.80 已作废」) ⇒ 检修口盖板内腔 = 外表面 7.30 − PCB 元件面 "
            "2.60 = **4.70mm ≥ cavity_req 4.50 ✅ 余 0.20** (判据出处 = service_port_check.py 检查项 4.2, "
            "实跑 54/54 OK) ⇒ **ISS-126 的前提已被现口径超越**; 且它引的「6 层 ≈ 0.41mm」与现口径 (6 层 = "
            "1.00) 对不上。★**真实状态 = 可裁关闭** (或改写为「板厚若改到 1.22 档才需重开」)。"
            "★**issue_log 是 main 地界, 本单一字未动** ⇒ 交 main 裁; 同域 claim "
            "`sp_clearance_vs_pcb_thickness` 仍写「4.48-5.29mm / 待 ISS-122」, 一并交 main 裁。"
            "[实测] (实跑 service_port_check.py)"),
        "ref": "MECH/HW_CROSS_REVIEW_TRIAGE.md §5.5 + MECH/service_port_check.py BASE/§4.2",
    },
    {
        "key": "mech_hw_cross_review_triage_54",
        "value": "54项逐条定性/17条FAIL有去处/6个PCB类排队",
        "note": (
            "★ISS-213 交卷摘要: `MECH/hw_cross_review_check.py` 实测 **PASS 14 / FAIL 17 / 条件通过 8 / "
            "说明 15 (共 54 项) 而 rc=0** ⇒ 17 条「按现在的图纸/口径做出来会出问题」挂着, 一个红灯都不点; "
            "且 `state/daily_check.py` 里 grep 不到 hw_cross_review / service_port / hinge_usb / "
            "display_biosafety / cavity_recalc 任何一个 ⇒ **17 条在每日巡检里完全隐形** (同类问题第三次复发)。"
            "★**本单收口**: ① `MECH/HW_CROSS_REVIEW_TRIAGE.md` = 54 项逐条定性表 (处置栏 54/54 非空) + "
            "17 条 FAIL 逐条去处 (排队等原理图定稿 **6 个 id / 7 行** + 登记 need 给 main **4 条** + 出规格 "
            "**6 条**) + 机器可读锚点; ② `MECH/check_demo_struct_truth.py` = 机器门禁 **20 组** (G1/G1b "
            "**不许把红灯调没**: 断言 FAIL 名单仍是 17 条且逐条对齐; G3/G3b 6 个 PCB 类 id 已登记排队 "
            "**且在 check 脚本里仍然是 FAIL**) + `--selftest` **8/8** 反向用例; ③ 板框真源四数与判据阈值 "
            "一个没动。★**本闸挂不挂每日巡检交 main 裁 —— 本单没改 state/daily_check.py**。[实测]"),
        "ref": "MECH/HW_CROSS_REVIEW_TRIAGE.md + MECH/check_demo_struct_truth.py",
    },
]

NEEDS = [
    {
        "key": "iss213_mech_cross_domain_to_main",
        "to": "main",
        "since": SINCE,
        "item": (
            "★ISS-213 跨域条目汇总 —— **本单只报增量, 不指派任何别的 agent, 请 main 派给对应总工**。①"
            "**PIN-MISMATCH / STK-P9 / TOPO-3**: HW 原理图 P9 页正文 pin 数 (21p vs 网表/同页器件表 22p) "
            "与堆叠账 (缺 4×2×0.50 走线边距 + 拓扑未定义) ⇒ 归 hw-lead (已有 need "
            "`iss089_p9_topology_and_stack`) —— ★结构侧建议: 拓扑定义按**拓扑 B (H 向径向嵌套)**, "
            "堆叠按触点区 27.00 / FPC 带宽 35.50 两个口径分列。②**NET-LED**: 充电灯 "
            "(D_CHG_LED/Q_CHG_LED/R_CHG_LED) 的网表 board 列标错 —— 网表 `['CHG_BOARD']` 但同页注记写"
            "「装在充电板 (镜框) 靠近 Type-C 座」, 且 `R_CHG_LED` 两端分别标 CHG_BOARD (net VBUS_5V_CHG) "
            "与 MAIN_PCB, 而 VBUS_5V_CHG 只存在于充电板 ⇒ **LED 链条物理上只能在镜框** ⇒ BOM 备料 / "
            "装配 / ISS-103 导光孔位置会跟着做错 ⇒ 归 hw-lead (已有 need "
            "`iss089_chg_led_board_column`)。③**THM-RATIO-3.70 / 4.20**: `HW/CHARGE_BOARD_SPEC.md` §3.4 的 "
            "ICHG/IIN 系数**方向反了** (写 0.822/0.933 = 倒数), 物理真值 = η·Vbus/Vbat = **1.216 / 1.071** ⇒ "
            "390Ω 档实际 ICHG 是表值 0.67–0.82A 的 ~1.48 倍 ⇒ **单 pin 0.50–0.61A 超 0.5A 触点额定** ⇒ "
            "390Ω 档判据要重算 ⇒ 需 hw-lead 用 BQ25896 datasheet 原文确认 (已有 need "
            "`iss089_ichg_ratio_datasheet`)。④**CHG-PRINT-TOL**: `CHARGE_BOARD_SPEC` M-15 的「面板开孔宽"
            "公差 ±0.1 (9.4~9.6)」的**名义 + 公差两处都不合格** ⇒ 归 hw-lead (已有 need "
            "`iss089_typec_opening_and_print_pack`) ⇒ 新口径见 need "
            "`iss213_mech_typec_third_candidate`。⑤**CHG-AREA**: 充电板 25×10 的器件 land 179mm² = 71% ⇒ "
            "余 71mm² **只够双面贴, 单面贴装不下** ⇒ 充电板 PCB 必须双面贴 ⇒ 归 hw-lead (新)。"
            "★全部为**增量**, 已有 need 的 key 我一个没动、没重复派活。"),
    },
    {
        "key": "iss213_mech_iss126_premise_superseded",
        "to": "main",
        "since": SINCE,
        "item": (
            "★ISS-213: `state/issue_log.yaml` 的 **ISS-126** (open / owner=main / due 2026-11-05) 的"
            "**前提已被现口径超越** ⇒ 请裁 (issue_log 是你的地界, **我一笔没动**)。现状: ISS-126 仍按"
            "「板厚 0.41/0.80/1.00/1.22 四档都有可能, **只有 0.80 及以下才安全**, 1.22 档净空 4.48 破 4.50」"
            "在写, 解锁条件挂在「等 PCB 厂 DFM 报告 (ISS-122)」。但**结构真源现行板厚 = 1.00mm (6 层)** "
            "(`MECH/BOARD_GEOM_30MM.md` §1 + `MECH/service_port_check.py` BASE `pcb_thk`=1.00, 注释"
            "「6 层现行; 4 层 0.80 已作废」) ⇒ 检修口盖板内腔 = 外表面 7.30 − PCB 元件面 2.60 = "
            "**4.70mm ≥ cavity_req 4.50 ✅ 余 0.20** (判据出处 = `service_port_check.py` 检查项 4.2, 实跑 "
            "**54/54 OK / FAIL 0**) ⇒ 「只有 0.80 及以下才安全」在现口径下**不成立** (1.00 档本来就过); "
            "且 ISS-126 引的「6 层 ≈ 0.41mm」与现口径 (6 层 = 1.00mm) **对不上**。⇒ **真实状态 = 可裁关闭**"
            "(或改写为「板厚若改到 1.22 档才需要重开」)。★顺带: 本域分片 claim "
            "`sp_clearance_vs_pcb_thickness` 的 value 仍写「4.48-5.29mm」且 note 挂「板厚档位待 hw-lead + "
            "PCB 厂 DFM (ISS-122)」⇒ **该 claim 也已被现口径超越**, 请一并裁 (claim 是我的地界, 本单"
            "**没动别的 key**, 等你裁了我再改)。★证据: [实测] (本机实跑 `service_port_check.py`)。"),
    },
    {
        "key": "iss213_mech_typec_third_candidate",
        "to": "main",
        "since": SINCE,
        "item": (
            "★ISS-213 增量 (挂在已有 need `iss089_typec_opening_and_print_pack` 之上, **不重复派活**): "
            "**打印包的「两档并行试样」是个假二选一** —— 两档现候选在最坏公差下**都判不合格**。①现口径 "
            "**9.50×3.60** (母座 8.94×3.26, FDM ±0.30, 判据 0.60) ⇒ 名义单边 X 0.28 / Y 0.17, "
            "**最坏 X 0.13 / Y 0.02** ❌; ②ISS-089 建议 **10.00×4.20** ⇒ 名义 X 0.53 / Y 0.47, "
            "**最坏 X 0.38 / Y 0.32** ❌ ⇒ ★**根因: `MECH/HW_CROSS_REVIEW.md` §3.2 的三条处置都只把名义"
            "间隙推到 0.47, 没在最坏公差下验判据**。⇒ **本单已出第三档 (结构侧现行口径)**: **FDM 直成型 "
            "10.50×4.80** (最坏 0.63/0.62 ✅, 端件面板最小外形 13.50×7.80 含承力壁 ≥1.50) 与 "
            "**金属嵌件/CNC ±0.05 10.25×4.55** (最坏 0.63/0.62 ✅, 外形 13.25×7.55); ★**该特征不得靠"
            "打印面成型** ⇒ 打印后扩孔 (±0.10) 或金属嵌件。★**下游两件要排期**: (a) "
            "`HW/CHARGE_BOARD_SPEC.md` M-15 的名义 + 公差两处改 (归 hw-lead) ⇒ (b) "
            "`MECH/print/gen_print_pack_revb.py` 加第三档试样 (`tc_open_w3/h3`) + 重生成 "
            "`frame_typec_coupon_revb.stl` + 更新 `MECH/print/MEASURE_CHECKLIST.md` M 段 —— ★(b) 是我的"
            "地界, 但它会动 Rev B 打印包基线 (自检 93/93 + 38/38) 与分片 claim `mprint_status` ⇒ **本单"
            "没改**, 请 main 排期后我来落。★顺带: 打印包现试样尺寸实测 33×3×7.2mm ⇒ 加第三档后面板外形"
            "会变长 (13.50+2×1.50 侧壁), B1 批试样清单要跟着改。[推算]"),
    },
    {
        "key": "iss213_mech_endpoint_thermal_path_metal",
        "to": "main",
        "since": SINCE,
        "item": (
            "★ISS-213: 端件 (镜框) 的**散热路径**必须有金属件 —— 这不是「最好有」, 是**唯一可行解**。算式: "
            "打印件 PA6-CF k=0.2 W/m·K, 沿臂长 70mm、截面 180mm² ⇒ **R = 0.070/(0.2×1.8e-4) ≈ 1944 K/W** "
            "⇒ 0.5W 打进去 **+972 K** (端件瞬间汽化); 铝 6063 (k=237) 同几何 ⇒ **R = 1.64 K/W** ⇒ "
            "**+0.82 K** ⇒ 差 **1185×**。⇒ **端件必须设金属导热路径 (铝屏蔽罩 → 金属骨架/桥)**; 端件外表面"
            "温升按 buck 口径 0.45–0.57W ⇒ ΔT 83K ⇒ **108°C** ⇒ 对 60°C 判据 ⇒ **P_max = 0.21W** ⇒ "
            "现值超 **2.4–2.7×** ⇒ 没有金属热路就必然超温。★验收办法 (B1 批加测项): 端件表面最热点 "
            "(充电板正上方) 充电 1A 稳态 30min 实测 **≤ 60°C**; 无金属热路的打印件版本直接判不合格。"
            "★**阻塞**: 镜框端件截面 **u8 未定义** ⇒ 端件形状/尺寸定不下来 (已有 need "
            "`iss089_frame_section_u8_block`) ⇒ ★**本单不替项目总工定端件截面**, 只把判据与验收办法摆出来。"
            "★老板已拍「边戴边充不允许」⇒ 充电时眼镜不戴 ⇒ 43°C 皮肤红线不适用, 但端件表面仍要过 60°C "
            "(烫手)。[推算]"),
    },
    {
        "key": "iss213_mech_pcb_class_6_queued",
        "to": "main",
        "since": SINCE,
        "item": (
            "★ISS-213: 结构侧 54 项交叉复核里 **6 个 PCB 类 id / 7 行 FAIL 按老板 2026-11-11 10:07 口径"
            "「PCB 布线/布局类一律不派, 排队等原理图定稿」** ⇒ 本单**只定性 + 写恢复条件, 一个没动, 判据"
            "阈值一个没松** ⇒ 它们在 `MECH/hw_cross_review_check.py` 里**仍然是 FAIL (正确状态)**。名单 + "
            "恢复条件: ①`STK-FANOUT` (行 13, 缺 5.50mm) —— 恢复条件: 原理图 P9 定稿给出 4 条 FPC 实际落点"
            "与拓扑 + 4 座沿 V 向排布方案定稿 ⇒ 复算 FPC 带宽合计 ≤ 板宽 30.00 − 0.60; ②`PCB-X-GAP` (行 18, "
            "缺 6.00mm) —— 4 座沿板长排布方案定稿 (含固定孔 X=5.00/15.00 一并重排) ⇒ 25.70 ≤ 可用 X + 0.60; "
            "③`MRG-54P` (行 20, 缺 4.50mm) —— 跨铰链连接器集合定稿; 若仍全合并 ⇒ 需 63p 座体 Y 向 ≤ "
            "30.00 − 0.60 或改接触排方向 (★pin 数 = 网表实读 **63p**, P9 的 54p 口径 ≠ 网表); "
            "④`MRG-X-4` (行 22, 缺 6.00mm) 同 ②; ⑤`MRG-X-3` (行 23 缺 0.50 / 行 24 缺 3.80, 两个实例) 同 ②; "
            "⑥`FRM-SUM` (行 28, 框侧合计 31.00 vs 端件可用 V 30–40 ⇒ −1.00~+9.00) —— 框侧落点与走线拓扑"
            "定稿 **且** u8 端件截面定义 ⇒ 框侧 V 向带宽合计 ≤ 端件可用 V 高 − 0.60。★**排队的账已经在位**: "
            "全文见 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §3/§4, 机器门禁 `MECH/check_demo_struct_truth.py` 的 "
            "**G3/G3b** 断言这 6 个 id 已登记排队、恢复条件非空、**且在 check 脚本里仍然是 FAIL** ⇒ 谁把它"
            "「修绿」或静默丢弃, 门禁立刻红。★请 main 排期 (原理图定稿后复活)。"),
    },
    {
        "key": "iss213_mech_mech_budget_charge_caliber_text",
        "to": "main",
        "since": SINCE,
        "item": (
            "★ISS-213: `MECH/MECH_BUDGET.md` §2.1 的充电耗散口径要改 (文字 + 连带 `MECH/verify_budget.py` 的 "
            "`P_CHARGE` 常量) —— ★**本单没改** (它牵 §2.3 皮肤热链与 §3 重量表, 不是我一个单能收的)。现状: "
            "§2.1 写「**0.8 W @ 1A** (IC 自身耗散 = (5−4.2)V × 1A)」= **线性充电 IC** 公式, 而 P10 充电板"
            "是**开关型 buck** (网表有 SW/L_CHG/C_BST/PMID) ⇒ 耗散应按 **Pin − Pout + DCR = 0.45–0.57W** ⇒ "
            "端件外表面温升 83K ⇒ **108°C** (0.8W 口径是 133K ⇒ 158°C) ⇒ 60°C 判据 ⇒ **P_max = 0.21W** ⇒ "
            "**必须金属热路** (见 need `iss213_mech_endpoint_thermal_path_metal`)。★结构侧现行口径已记在分片 "
            "claim `mech_endpoint_surface_temp_caliber` + `mech_mech_budget_linear_0p8w_dead` ⇒ 请 main "
            "排期改文档与脚本常量 (改完请回我一声, 我好把门禁锚点对齐)。★**判据阈值一个不许顺带松** "
            "(cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00)。[推算]"),
    },
]

STATUS = {
    "phase": "P3",
    "progress_pct": 98,
    "health": "yellow",
    "summary": (
        "2026-11-15 ISS-213 (结构侧 54 项交叉复核逐条定性 + demo 板真缺陷收口): ★**结构侧 54 项表逐条定性完成, "
        "一处不漏** (`MECH/HW_CROSS_REVIEW_TRIAGE.md`: 项号/现状判定/关键数字/demo 相关性/MECH 地界/处置/恢复"
        "条件/证据等级 8 列 × 54 行, 处置栏 54/54 非空, 没有一条写「待定」)。★**17 条 FAIL 每条都有明确去处**: "
        "排队等原理图定稿 6 个 id / 7 行 (STK-FANOUT/PCB-X-GAP/MRG-54P/MRG-X-4/MRG-X-3×2/FRM-SUM, 逐条写了恢复"
        "条件, 判据阈值一个没松 ⇒ 它们**仍然是 FAIL**, 这是正确状态) + 登记 need 给 main 4 条 (P9 页 pin 数与"
        "堆叠账 / NET-LED 网表 board 列 / CHARGE_BOARD_SPEC §3.4 的 ICHG/IIN 方向 / M-15 印刷公差) + 出规格 6 条 "
        "(MECH 地界内本单收掉)。★**新机器门禁 `MECH/check_demo_struct_truth.py`** (20 组检查 rc=0, `--selftest` "
        "8/8 反向用例全被抓): 它守的是「demo 板当前成立的条目」而不是「54 项全绿」⇒ **G1/G1b 不许把红灯调没** "
        "(断言 FAIL 名单仍是 17 条且逐条对齐) · G2 demo 当前项独立复算全过 · G3/G3b 6 条 PCB 类已登记排队"
        "且没被静默 · G4 板框四数 60.00/30.00/1.00/3.33g 没被改 · G5 判据阈值 (cavity_req 4.50/CRIT 0.60/"
        "cav_v 38.00/duct_v 6.00) 未松 + 8 个受保护文件 md5 未变 · G6 定性表 54/54 + 处置不留空 · G7 分片 25.00。"
        "★**demo 板真缺陷收掉 6 条**: ①CHG-OPEN —— 真根因是「判据只在名义值上验」⇒ 打印包两档现候选 (9.50×3.60 "
        "最坏 0.13/0.02、10.00×4.20 最坏 0.38/0.32, 判据 0.60) **都判不合格, 二选一是假的** ⇒ 新出 10.50×4.80 "
        "(FDM 直成型, 最坏 0.63/0.62) 与 10.25×4.55 (金属·CNC ±0.05) ②CHG-PRINT-TOL —— 该特征不得靠打印面 ⇒ "
        "扩孔 ±0.10 或金属嵌件 ±0.05 ③THM-RATIO 3.70/4.20 —— ICHG/IIN = η·Vbus/Vbat = 1.216/1.071 (规格书 "
        "0.822/0.933 是倒数) ⇒ 390Ω 档单 pin 0.50–0.61A 超 0.5A 额定 ④THM-SURF —— 口径钉死为 buck "
        "(0.45–0.57W) ⇒ 108°C, 60°C 判据 ⇒ P_max 0.21W ⇒ 超 2.4× ⑤THM-PATH —— 打印件 R=1944 K/W (0.5W "
        "打进去 +972K 不可能) vs 铝 1.64 K/W (+0.82K) ⇒ **端件必须金属热路** ⑥腔体 —— 检修口内腔 4.70 ≥ "
        "cavity_req 4.50 (余 +0.20) ⇒ **ISS-126 的前提已被现口径超越, 可裁关闭** (issue_log 是 main 地界, "
        "一笔没动)。★**边界**: 未改 HW/ 任何文件 · 网表/脚表/板/.kicad_pro · state/gen_*.py · "
        "state/daily_check.py · state/issue_log.yaml (含 ISS-126) · PROJECT_TRACKER.md §0 · state/outbox/ · "
        "别人的分片 · BOARD_GEOM_30MM §1 四数 · 判据阈值 · 3 个受保护 check 脚本; ★没碰 PCB 布线/布局/板框; "
        "★本闸挂不挂每日巡检交 main 裁; ★零外发; ★本单 [实测] 实物 = 0 条。"
    ),
}


def main() -> int:
    def mutate(d: dict) -> None:
        d.setdefault("artifacts", [])
        have_a = {a.get("path") for a in d["artifacts"]}
        for a in ARTIFACTS:
            if a["path"] not in have_a:
                d["artifacts"].append(a)
        d.setdefault("interface_claims", [])
        have_c = {c.get("key") for c in d["interface_claims"]}
        for c in CLAIMS:
            if c["key"] not in have_c:
                d["interface_claims"].append(c)
        d.setdefault("needs_from", [])
        have_n = {n.get("key") for n in d["needs_from"]}
        for n in NEEDS:
            if n["key"] not in have_n:
                d["needs_from"].append({"key": n["key"], "to": n["to"],
                                        "item": n["item"], "since": n["since"]})
        st = d.setdefault("status", {})
        st.update(STATUS)

    d = update_fragment(AGENT, mutate)
    print(f"[frag_update_iss213] ✅ {AGENT} 分片已原子更新 "
          f"(artifact {len(d.get('artifacts') or [])} / claim {len(d.get('interface_claims') or [])} / "
          f"need {len(d.get('needs_from') or [])}) → 再跑 python3 state/merge.py")
    print("[frag_update_iss213] ★U-3 复核: mech_hinge_stack_fixed_mm = "
          f"{[c.get('value') for c in d.get('interface_claims') or [] if c.get('key') == 'mech_hinge_stack_fixed_mm']}"
          " (已是 25.00 ⇒ 本单未重复写)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
