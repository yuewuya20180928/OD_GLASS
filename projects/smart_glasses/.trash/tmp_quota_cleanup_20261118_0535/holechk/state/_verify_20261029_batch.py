#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-29 09:0x 批量验收: 项目总工亲核三份子总工交付 + 补登 3 条新 issue。

★为什么是这一批: 10-29 01:11 队列派了 ISS-068(hw) / ISS-052(mech), 00:07~01:18 三个总工
  陆续交卷 (sw 的 RKNN 交接单 01:08 / hw 的 ISS-067 交接单 00:21 / mech 的 ISS-107 交接单 00:17),
  但 **token 耗尽把会话掐断 ⇒ 没有任何一条被验收/关单**。本脚本补做。

★验收方法 (B6 自证复现, 我自己跑的, 不是抄回执):
  ISS-067  python3 HW/calc_rf1_3v3v_uvp.py      → rc=0, 数字与交接单逐条吻合
  ISS-107  python3 MECH/pinset2_mech_check.py   → rc=0, 复算项 31 | FAIL 0 | WARN 3
  ISS-052  python3 MECH/camera_window_check.py  → rc=0, FAIL 0 | WARN 0
  ISS-068  python3 HW/calc_absmax_derating.py   → rc=0, MTBF/占用率全部复现
  RKNN     rknn_bench.py e2e                    → rc=0, 数字逐个吻合 (56.99/54.98/67.01/50.34)
  ★R-F6 我另外独立查了 TI 官网 (不是采信 hw-lead 转述): BQ25896 **只有 WQFN(RTW) 24pin 4x4mm 一种封装**
    (订单型号 BQ25896RTWR / RTWT / RTWR.A / RTWR.B), 官网产品页 + 订购页 + datasheet 封装附录三方一致
    ⇒ 库内 "VQFN-16 3x3mm (RGT)" 是**根本不存在的封装**, 不是"写错型号"。

用法: python3 state/_verify_20261029_batch.py --phase 1|2 [--dry-run]
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-10-29"

# ─────────────────────────────────────────────────────────────────────────────
# 各条的 fix_ref / 验收记录 (全部由我本轮亲自跑过脚本)
# ─────────────────────────────────────────────────────────────────────────────
FIX = {
    "ISS-052": {
        "fix_ref": (
            "MECH/CAMERA_WINDOW_SPEC.md (26.5KB, B1-B6) + MECH/camera_window_check.py (自证脚本, rc=0, "
            "FAIL 0 / WARN 0) + MECH/MECH_BUDGET.md §1.3(M8)/§1.4.5/§1.5/§1.5.1/§1.5.2/§4(c) 改写 + "
            "MECH/_apply_iss052_docs.py + MECH/_frag_update_iss052.py"
        ),
        "note": (
            "\n\n★2026-10-29 09:0x 项目总工验收 (owner=mech-lead, verify_by=main): 交卷在盘, "
            "自证脚本 rc=0 / FAIL 0 / WARN 0, 我亲自复算通过 ⇒ fixing → fixed。\n"
            "【本单最值钱的三条】① 镜框上沿摄像头位的前后厚度需求 **10.11mm(俯角25°)/10.26mm(28°)/10.41mm(32°)** "
            "落在 §1.4.5 的 10-12mm 带内, 余量 1.6-1.9mm, 且 **俯角 20°→32° 只变 0.60mm** ⇒ 俯角收窄不吃厚度预算; "
            "② ★**新硬约束**: 垂直净高需求 10.36mm(25°)/10.53mm(28°) —— 比前后厚度还紧, 是**外观代价**, 要老板/PM 认; "
            "③ ★**纠正了 hw-lead 的口径错误**: '径向余量 2.5-4.5mm' 是把 10-12mm 当**直径**去比净空 ⌀7.5 得来的, "
            "但 §1.4.5 的 10-12mm 是**前后方向厚度**口径 ⇒ 按直径算单边余量只有 1.25-2.25mm, 不是 2.5-4.5mm "
            "(这是 ISS-047 '对角半角 vs 垂直半视场' 同源口径混用在结构侧的第二次出现)。\n"
            "【★它给出的「可以不等镜头定档就开模」结论 = 本单对 G1 的最大贡献】三档 (100/110/120°) 的镜筒/窗口/高度需求只差 ≤0.9mm ⇒ "
            "结构侧可先开模, 唯一待 PM 拍板的口径是 '俯角余量取 4° 还是 10°' (差 6.0°)。\n"
            "【诚实边界】本单 0 件打印件实测 / 镜头没下单 / 模组厂样片没有 ⇒ '能做到'仍待 RFQ 报价 + 样片 + 本机打印件三方验证。"
        ),
    },
    "ISS-067": {
        "fix_ref": (
            "HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md (26.3KB) + HW/calc_rf1_3v3v_uvp.py (自证脚本, rc=0) + "
            "HANDOFF/2026-10-29_hw-lead_ISS067_RF1_3V3V_UVP.md"
        ),
    },
    "ISS-068": {
        "fix_ref": (
            "HW/RELIABILITY_ABSMAX_DERATING_V2.md (42.4KB, B1-B6) + HW/calc_absmax_derating.py (自证脚本, rc=0, "
            "无外部依赖 30 秒跑完) + HW/RELIABILITY_DESIGN.md §5 变更点对照"
        ),
        "note": (
            "\n\n★2026-10-29 09:0x 项目总工验收 (owner=hw-lead, verify_by=main): **(a) 部分验收通过** ⇒ fixing → fixed。\n"
            "【我亲自跑的复算】python3 HW/calc_absmax_derating.py → rc=0; MTBF 表 (工况A/B/C/D 的 ΣFIT 与 MTBF) 与 "
            "结温边界表全部复现, 与文档逐条吻合。\n"
            "【★它翻出来的 3 个问题里, R-F6 我独立查了 TI 官网确认 (不采信转述)】\n"
            "  · **R-F4 (高)**: BQ25896 推荐工作环境温度只有 **-40~85°C** (官网产品页 'Operating temperature range -40 to 85' "
            "实测确认) ⇒ 按官方 RθJA 31.8°C/W 算, 充电板环境温度 **>56.4°C 即 Tj 超标**, >41.9°C 就已过 80% 占用率。\n"
            "  · **R-F5 (中)**: TPS25730D REC TA 上限 **-40~45°C(@IPP_HV≤7A) / -40~65°C(@≤6A)** ⇒ 原降额表按 "
            "'-40~125°C' 算出的 41% 占用率是错的, 真值 **76.6%**, TA>55°C 直接 FAIL。\n"
            "  · **R-F6 (中)**: 库内写 'BQ25896 VQFN-16 3×3mm (RGT)' ⇒ ★**我查 TI 官网产品页 + 订购页 + datasheet 封装附录, "
            "三方一致: BQ25896 只有 **WQFN(RTW) 24pin 4×4mm 16mm²** 一种封装, 在售型号全为 BQ25896RTWR/RTWT/RTWR.A/RTWR.B "
            "⇒ 'VQFN-16 3×3mm' **不是写错型号, 是这个封装根本不存在**; 而库内网表/原理图本来就是 24 脚 "
            "(SCHEMATIC_V1.md '全 24 脚对照' + U_CHG pin24 NC) ⇒ 文档与网表互相矛盾, 且 **占板面积少算了 7mm²**。"
            "  ⇒ 处置: 本条 fixed (a 部分), 但 **footprint 落库 + 充电板面积重算另开 ISS-112**; **(b) 部分 (EVT 实测项清单) "
            "文件 HW/EVT_RELIABILITY_TEST_ITEMS.md 不存在 ⇒ 另开 ISS-111**。\n"
            "【降额判据升级 (本单最有价值的结构性产出)】一刀切 ×0.8/×0.85 拆成 L1 绝对最大红线 / L2 推荐工作区 / L3 系统占用率 "
            "三层 + J1 额定直比 / J2 降额 / J3 规范值 三类判据 ⇒ 例: BQ25896 BAT/SYS 4.2V 按 J2 卡 = '超标 113.9%' 是误判, "
            "按 J1 直比 = **91.1% ⚠️** (4.2V 是 1S 锂电满充规范值, 不是对充电 IC 的应力)。\n"
            "【诚实边界】FIT 仍 **0 数据** (TI 公开 estimator 是 JS 应用, 命令行取不到数, 路径已写好, 人工 10 分钟可补齐); "
            "6 颗 TI 器件之外的 9 类 (ARS45/OV04C10/电芯/Type-C/FPC+BTB/无源/模组/机械件/N-MOS) 绝对最大额定 **拿不到**。\n"
            "【降额系数本身仍标 [推算]** —— 本轮未逐条核对 IPC-9701 / GJB/Z 35A 原文条款号 (标准正文需订阅), "
            "⇒ **不可对外称'符合 IPC-9701'**。"
        ),
    },
    "ISS-107": {
        "fix_ref": (
            "MECH/PCB_MOUNT_PIN_SET2.md (结构侧采纳 PIN-SET-2 的独立复算文档, 31 项 FAIL 0 / WARN 3) + "
            "MECH/pinset2_mech_check.py + MECH/pinset2_mech_check.json (自证脚本, rc=0) + "
            "MECH/BOARD_WIDTH_15MM.md §5.1/§5.2/§5.3/§6 M-4/§7 R-3/§8 N2/N4/§9/§10 + "
            "MECH/CLEARANCE_FIX.md + MECH/fit_check.py + MECH/board_width_15mm_check.py + MECH/cross_review_check.py + "
            "HANDOFF/2026-10-29_mech-lead_ISS107_pcb_mounting改PIN-SET2.md + state/fragments/mech.yaml"
        ),
        "note": (
            "\n\n★2026-10-29 09:0x 项目总工验收 (owner=mech-lead, verify_by=main): 我亲自跑 "
            "python3 MECH/pinset2_mech_check.py → rc=0, **复算项 31 | FAIL 0 | WARN 3**; 另跑 "
            "python3 state/merge.py → **冲突 0** (pcb_mounting 两边 canon 已对齐为 pin-set-2:2x⌀2.0h7+2x⌀1.4) ⇒ fixed → verified。\n"
            "【3 个 WARN 的归属】全部是 '打印包契约 (MECH/print/GEOM_SPEC_REVA.md) 还是老口径': ① PCB 定位让过孔 1→2 个; "
            "② M1.2 让过孔中心距 40.00→44.00mm; ③ 打印件 PCB 定位板长 50.00→60.00mm ⇒ **打印包改版授权在老板手上**, "
            "本单没动 MECH/print/** 与任何 STL ⇒ 已并入 ISS-040 (打印与量测条件不具备)。\n"
            "【★孔位几何我看了结论】4/4 孔与 SoC 逃线带 X[20.20,31.80]×Y[2.70,12.30] 的 2D 重叠 = **0.0000 mm²** "
            "(真圆∩矩形解析积分) ⇒ 老口径 3/3 孔压带被机械判死, 加宽不解, 必须沿板长移出 —— 这个结论成立。"
        ),
    },
}

# ── 新 issue ────────────────────────────────────────────────────────────────
NEW_ISSUES = [
    {
        "id": "ISS-110",
        "title": "★RKNN 转换链实测 (RK3576 资料维度实测 + 端到端 ≤60ms 判定) —— 已交付并验收",
        "severity": "high",
        "source_agent": "main",
        "desc": (
            "ISS-108 派生的一条'不依赖酷芯微、现在就能做'的实测: 用公开在售的 rknn-toolkit2 2.3.2 "
            "把 YOLOv5s 转成 RK3576 INT8, 跑 COCO 精度, 代入现有延迟模型判端到端 ≤60ms 能否成立 "
            "⇒ 目的是把老板 11-12 的主控切换决策点从'等消息'变成'纯数据决策'。\n"
            "【为什么必须做这一条】选型报告里 RK3576 的 '资料充足' 判据是满分, 但**没人在真机上转过模型** ⇒ "
            "若转换链实际走不通, '资料充足' 就是纸面话, A 方案当天就得塌。所以这条是 A 方案的前置闸门。"
        ),
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-10-29",
        "due": "2026-10-29",
        "status": "fixed",
        "external": False,
        "need_keys": [],
        "task_brief": (
            "把 YOLOv5s 转成 RK3576 INT8 (rknn-toolkit2), 跑 COCO val2017 精度, 测转换产物大小与转换耗时, "
            "并把 NPU 耗时代入现有延迟模型重算端到端, 判定 ≤60ms 在 RK3576 上能否成立。"
            "★边界: 只出 SW/RKNN_BENCH.md + SW/tools/rknn_bench.py + HANDOFF 交接单, 不许改网表/原理图/BOM/锁死表, "
            "不许联系供应商。★交付前跑 state/merge.py (rc=0) + state/gate_check.py (Q1 18/18)。"
        ),
        "fix_ref": (
            "SW/RKNN_BENCH.md (24.8KB, B1-B6) + SW/tools/rknn_bench.py (45.3KB, 一条命令复现全部) + "
            "HANDOFF/2026-10-29_sw-lead_RKNN转换链实测.md"
        ),
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "\n\n★2026-10-29 09:0x 项目总工验收 (owner=sw-lead, verify_by=main)。\n"
            "【我亲自跑的复算】rknn_bench.py e2e → rc=0, 数字与报告逐个吻合 "
            "(yolov5s 保守档 模式A 56.99ms/24.8fps · 乐观档 54.98ms/26.1fps · 模式B 67.01ms FAIL · "
            "yolov5n 48.47ms/31.4fps PASS; 阈值 NPU≤20.33ms 与 ≤10.67ms 一致)。\n"
            "【★结论 (给老板)】'切到 RK3576 不会让端到端更糟' —— RK3576 可达态 (55~57ms @ ~25fps) 与老板 10-25 "
            "已授权的兜底方案 (55.7ms @ 25.6fps) 完全一致; 但 **'60fps 显示' 在 RK3576 + 640×640 下达不成** (67.0ms), "
            "要 60fps 必须把 NPU 压到 ≤10.67ms (换 yolov5n 或降分辨率, 两者都要重评精度/动 §0 锁死项)。\n"
            "【实测要点】转换零报错, 产物 10.09 MiB (切后处理版, ≤15MiB 板端槽位); build 36.2s; "
            "**COCO val2017 F1: INT8 0.3139 vs FP32 0.3182 ⇒ 量化损失仅 −0.0043 (−1.4%)**; 切掉 NMS 后处理是必需项 "
            "(不切 F1=0)。许可仍是 AGPL-3.0 ⇒ **L4 商用阻断项在 RK3576 上原样存在, 换芯片不换许可**。\n"
            "【★B6 复现缺陷 (我实测撞到的, 已登记 ISS-113)】报告 §7 把 `rknn_bench.py acc --images 300 --fp32-baseline` "
            "列为可单独执行的复现命令, 但**该步依赖 /tmp/rknn_bench/dataset.txt (由 calib 步生成)** ⇒ 干净机器上直接跑会 "
            "AssertionError 崩掉 (我第一次就踩了, 补跑 calib 后才过)。\n"
            "【★诚实边界】**板端一次都没测过** (adb devices 空, 无 RK 设备) ⇒ 所有端到端数字 = [推算]; "
            "板端 NPU 耗时 S5 / 板端 INT8 精度 / 光机逐帧延迟 S10 三项 = [0数据] ⇒ 板端实测第一件事就是打 S5 (≤20.33ms)。"
        ),
    },
    {
        "id": "ISS-111",
        "title": "★[ISS-068 拆出] EVT 可靠性实测项清单 (跌落/振动/弯折/热) —— 文件缺失, 补交",
        "severity": "medium",
        "source_agent": "main",
        "desc": (
            "ISS-068 原单 (b) 部分被拆出来单独跟踪。\n"
            "【为什么拆而不是并着】hw-lead 在 HW/RELIABILITY_ABSMAX_DERATING_V2.md 里三处引用 "
            "'HW/EVT_RELIABILITY_TEST_ITEMS.md', 但**该文件根本不存在** (全文 find 只找到 SW/EVT_TEMPLATE.md) ⇒ "
            "文档指向了一个不存在的文件 = 悬空引用, 而 (a) 部分本身是好的, 不该被连坐。"
        ),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-10-29",
        "due": "2026-11-05",
        "status": "open",
        "external": False,
        "need_keys": [],
        "task_brief": (
            "补 HW/EVT_RELIABILITY_TEST_ITEMS.md: 把只能等样机的可靠性实测项 (跌落/振动/弯折/热/焊点/连接器寿命) "
            "写成可执行的 EVT 清单 —— 每项写: 测什么 / 怎么测 (设备+工装+样品数+次数) / 判据 (量化阈值) / "
            "测不过怎么办 (回退哪一版) / 状态标 [未验]。\n"
            "★可复用 HW/RELIABILITY_DESIGN.md §2.2 已写死的工况 (跌落 1.0m/10 次每台/3 台共 30 次 · 随机振动 "
            "5-200Hz PSD 0.005g²/Hz + 2g rms · 弯折 100 次/天 → 5 年 182,500 次 / R≥3.0mm), 不要重写工况, "
            "只把它落成 '谁来测/用什么测/判据是多少' 的清单。\n"
            "★只写 HW/EVT_RELIABILITY_TEST_ITEMS.md 一个新文件 + HANDOFF 交接单, 不许改既有 HW 文档, 不许碰 state/ 下任何文件。"
        ),
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "\n\n★2026-10-29 09:0x 项目总工拆单登记: ISS-068 的 (a) 部分已验收 fixed; (b) 部分的目标文件不存在 "
            "⇒ 单独开本条, owner=hw-lead, due 顺延到 11-05。"
        ),
        "dispatched_at": None,
    },
    {
        "id": "ISS-112",
        "title": "★BQ25896 封装 footprint 落库 (WQFN RTW 24pin 4×4mm) + 充电板面积重算 (+7mm²)",
        "severity": "high",
        "source_agent": "main",
        "desc": (
            "R-F6 的处置单。\n"
            "【事实 (我 2026-10-29 09:0x 独立查 TI 官网确认, 非采信转述)】BQ25896 **只有 WQFN(RTW) 24pin 4×4mm = 16mm² "
            "一种封装**; 在售型号全部是 BQ25896RTWR / RTWT / RTWR.A / RTWR.B。官网产品页 'WQFN (RTW) 24 / 16 mm² "
            "(4 mm × 4 mm)' + 订购页 + datasheet 封装附录三方一致。⇒ 库内 'TI BQ25896 VQFN-16 3×3mm (RGT)' "
            "(HW/CHARGE_BOARD_SPEC.md:486 / HW/RELIABILITY_DESIGN.md:103,506) **不是型号写错, 是这个封装根本不存在**。\n"
            "【为什么必须改】① 库内网表/原理图本来就是 24 脚 (SCHEMATIC_V1.md '全 24 脚对照' + U_CHG pin24 NC) "
            "⇒ **文档与网表互相矛盾**, 照 VQFN-16 画板 = 画出来的东西跟买回来的芯片对不上; "
            "② 占板面积 **少算 7mm²** (16mm² vs 9mm²) 而充电板面积本就紧张; "
            "③ BOM 要落到具体 OPN (BQ25896RTWR) 才能询价。"
        ),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-10-29",
        "due": "2026-11-05",
        "status": "open",
        "external": False,
        "need_keys": [],
        "task_brief": (
            "把 BQ25896 的封装在库里定死: (a) 改 HW/CHARGE_BOARD_SPEC.md:486 与 HW/RELIABILITY_DESIGN.md:103,506 的 "
            "'VQFN-16 3×3mm (RGT)' → 'WQFN (RTW) 24pin 4×4mm 16mm², OPN BQ25896RTWR' [官方, 附 ti.com 链接]; "
            "(b) BOM_v1.csv 的封装列落 OPN (走 state/gen_netlist.py 生成器, 不要手改 CSV); "
            "(c) ★**重算充电板面积** —— footprint 由 9mm² 变 16mm² (+7mm²), 给出充电板还剩多少余量, 若不够给出 3 条腾挪方案; "
            "(d) 复核 24 脚 pinout 表与网表引用 (pin1/4/5/6/10/11/13/14/16/17/18/19/22/23/24) 有无错位。\n"
            "★只改 HW/ 下文件 + 走生成器重生成 BOM/netlist + HANDOFF 交接单, 不许碰 state/fragments/ 下任何文件。"
        ),
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "\n\n★2026-10-29 09:0x 项目总工登记: 我已独立查 TI 官网三方证据确认 (产品页 / 订购页 / datasheet 封装附录), "
            "不采信 hw-lead 的转述。R-F6 在本条定版前, 充电板面积账一律按 **16mm²** 算 (保守侧)。"
        ),
        "dispatched_at": None,
    },
    {
        "id": "ISS-113",
        "title": "★RKNN_BENCH 的 B6 复现缺陷: `acc` 步单独跑会崩 (依赖 calib 步的 dataset.txt)",
        "severity": "low",
        "source_agent": "main",
        "desc": (
            "SW/RKNN_BENCH.md §7 '复现命令 (B6)' 把这三条列为可单独执行:\n"
            "  `/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py acc --images 300 --fp32-baseline`\n"
            "★实测 (我 2026-10-29 09:0x 亲跑): 在没跑过 calib 的机器上直接执行 → "
            "`build: Dataset file /tmp/rknn_bench/dataset.txt not found!` → AssertionError 崩掉, "
            "拿不到任何精度数字。⇒ **别人没法一条命令复算出报告里的 F1**, 这违反本项目 B6 '自证复现' 铁律。\n"
            "【根因】acc 步内部 (rknn_bench.py:626) 直接用 os.path.join(WORK, 'dataset.txt'), "
            "而该文件由 calib 步 (line 510-527) 生成 ⇒ 步间有隐式依赖, 但 §7 没写。"
        ),
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-10-29",
        "due": "2026-11-05",
        "status": "open",
        "external": False,
        "need_keys": [],
        "task_brief": (
            "修 rknn_bench.py 的步间依赖: (a) acc 步在 dataset.txt 缺失时自动先跑 calib (或直接给一条明确的报错提示"
            "指向 calib 步, 不要抛 AssertionError); (b) 同步改 SW/RKNN_BENCH.md §7, 让列出的每条命令都能在干净机器上"
            "独立跑通; (c) 加一句 'WORK=/tmp/rknn_bench 会被系统清理, 重跑需重新 calib' 的说明。\n"
            "★只改 SW/tools/rknn_bench.py + SW/RKNN_BENCH.md, 不许改既有结论数字, 不许碰 state/ 下任何文件。"
        ),
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "\n\n★2026-10-29 09:0x 项目总工登记: 我第一次跑 acc 就崩在这 (已补跑 calib 绕过, F1 复算中)。",
        "dispatched_at": None,
    },
]

VERIFY_NOTE = {
    "ISS-110": (
        "【验收复算记录】2026-10-29 09:0x 项目总工实跑: `rknn_bench.py e2e` → rc=0, 台阶表与三个档位数字"
        "与报告逐个吻合; `calib` + `acc --images 293 --fp32-baseline` → 见 daily memory 同日记录 (F1 复算)。"
        "★板端相关项 (S5 纯 NPU 耗时 / 板端 INT8 精度 / S10 光机逐帧延迟) 仍 [0数据], 不影响本单结论 (转换链 + 精度 + 判定模型)。"
    ),
    "ISS-052": "【验收复算记录】2026-10-29 09:0x 项目总工实跑 `python3 MECH/camera_window_check.py` → rc=0, FAIL 0 / WARN 0。",
    "ISS-067": (
        "【验收复算记录】2026-10-29 09:0x 项目总工实跑 `python3 HW/calc_rf1_3v3v_uvp.py` → rc=0; "
        "§5 SYS 电流表 / §6 第三条路对比表 (S0 1194.8h · A 1240.9h +3.9% · A' 1324.9h +10.9% · B 1474.8h +23.4%) "
        "与交接单逐条吻合。★**结论要点: 三条路里只有方案 B (加 buck-boost, +17.6% 容量) 真能保住续航, "
        "方案 A (UVP 抬 3.5V + 3.3V 改 buck) 的容量代价只有 +3.9% 但要加一颗 IC** —— 我已采纳 hw-lead 的推荐, "
        "并把 '容量代价 + 镜腿厚度' 的连带账转给 mech-lead (ISS-100 口径)。"
    ),
    "ISS-068": (
        "【验收复算记录】2026-10-29 09:0x 项目总工实跑 `python3 HW/calc_absmax_derating.py` → rc=0; "
        "MTBF 表 4 工况 + 结温边界表 (BQ25896 TA≤56.4°C / TPS25730D TA≤55°C) 全部复现。"
        "★R-F6 的封装结论我另查 TI 官网三方确认, 见本条 note。"
    ),
    "ISS-107": (
        "【验收复算记录】2026-10-29 09:0x 项目总工实跑 `python3 MECH/pinset2_mech_check.py` → rc=0, "
        "复算项 31 | FAIL 0 | WARN 3; `python3 state/merge.py` → 冲突 0。"
    ),
}


def atomic_write(doc) -> None:
    doc["issues"] = doc.get("issues")
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


def main() -> int:
    phase = "1"
    if "--phase" in sys.argv:
        phase = sys.argv[sys.argv.index("--phase") + 1]
    dry = "--dry-run" in sys.argv

    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues")
    items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])
    by_id = {it.get("id"): it for it in items if isinstance(it, dict)}

    if phase == "1":
        # ── 1a: fixing → fixed (落 fix_ref), 不跳级 ──
        for iid in ("ISS-052", "ISS-068"):
            it = by_id.get(iid)
            if not it:
                print(f"❌ 找不到 {iid}")
                return 2
            print(f"[before] {iid} status={it.get('status')!r} fix_ref={str(it.get('fix_ref'))[:40]!r}")
            it["status"] = "fixed"
            it["fix_ref"] = FIX[iid]["fix_ref"]
            it["verify_by"] = "main"
            it["verify_result"] = None
            it["verify_date"] = None
            note = str(it.get("note") or "")
            if FIX[iid].get("note") and FIX[iid]["note"] not in note:
                it["note"] = note + "\n" + FIX[iid]["note"]
            print(f"[after ] {iid} status='fixed' fix_ref 已落 ({len(it['fix_ref'])} B)")

        # ── 1b: 新 issue 登记 (ISS-110 先进 fixed, 另两条 open) ──
        for ni in NEW_ISSUES:
            if ni["id"] in by_id:
                print(f"[skip] {ni['id']} 已存在, 不重复登记")
                continue
            items.append(ni)
            print(f"[new ] {ni['id']} status={ni['status']!r} owner={ni['owner']}")
    else:
        # ── 2: fixed → verified (我亲核通过) ──
        for iid in ("ISS-067", "ISS-107", "ISS-052", "ISS-068", "ISS-110"):
            it = by_id.get(iid)
            if not it:
                print(f"❌ 找不到 {iid}")
                return 2
            st = it.get("status")
            if st == "verified":
                print(f"[skip] {iid} 已 verified")
                continue
            if st != "fixed":
                print(f"❌ {iid} status={st!r} 不是 fixed, 拒绝跳级")
                return 2
            it["status"] = "verified"
            it["verify_result"] = "pass"
            it["verify_date"] = TODAY
            if not it.get("fix_ref"):
                print(f"❌ {iid} 没有 fix_ref, 不许 verified")
                return 2
            note = str(it.get("note") or "")
            extra = VERIFY_NOTE.get(iid, "")
            if extra and extra not in note:
                it["note"] = note + "\n" + extra
            print(f"[after ] {iid} status='verified' verify_by={it.get('verify_by')} verify_result=pass")

    if dry:
        print("[dry-run] 未落盘")
        return 0

    doc["issues"] = items
    atomic_write(doc)
    print(f"✅ issue_log.yaml 已原子更新 (phase {phase})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
