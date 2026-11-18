# -*- coding: utf-8 -*-
"""ISS-313 · mech-lead · MECH 域 184(185) 条 needs 四分类处置 —— 数据源 (唯一真源)

★ 本文件是本单三件交卷物 (MECH/MECH_NEEDS_TRIAGE.md · HANDOFF/2026-11-18_mech-lead_ISS313_*.md
  · state/fragments/mech.yaml) 的**同源数据** ⇒ 改这里三处一起变, 不许各自重写。

★ 口径:
  - 关闭 = 从 needs_from 移出 + 依据行 (本文件 CLOSED[*].evidence) + 分片 needs_closed 台账
  - 保留 = 留在 needs_from + owner + 一句话问法 (本文件 KEPT[*])
  - 新答 = 写进 answers (本文件 CLOSED[*].answer)
  - 证据等级: [官网] / [实测] / [媒体] / [推算] / [0数据]
"""

# ============================================================================
# ① 类 · waiting_on = agent (35 条: 显式 agent 34 + waiting_on='hw-lead' 1 条格式错)
# ============================================================================
C1 = {
    # key: (action, reason, evidence, evidence_level, answer_value or None, answer_ref or None, board_trip)
    "iss085_battery_side": dict(
        action="close+answer",
        reason="本 need 的前提【电池位两边假设互斥】已被现网表消除 ⇒ 电池在镜脚已是事实, 无待裁项",
        evidence="[实测] HW/netlist_v1.csv L17「[BAT_CHG] 充电电流进镜脚侧电池保护 IC (BQ2970) —— 保护 IC 与电池同板 (镜脚)」+ L40「[V1.2 电池搬镜脚后]」+ L2「充电链整条在充电板」⇒ 电池在镜脚 / 充电板在镜框 的分工已落表",
        level="[实测]",
        answer="电池位已定: 电池在镜脚 (保护 IC 与电池同板), 充电板在镜框 (整条充电链在 CHG_BOARD)。[实测] HW/netlist_v1.csv L2/L17/L40。⇒ 跨铰链只过 BAT_CHG(充电电流)+GND+TS(高阻), SYS 不跨铰链 ⇒ 铰链区载流按 BAT_CHG 口径 (1.0-1.5A) 而非 SYS 口径 (0.55A)。本 need 的【互斥前提】消失, 按现网表执行。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-1 + HW/netlist_v1.csv L2/L17/L40",
        board="N"),

    "iss085_service_port_form": dict(
        action="close",
        reason="被同题的新版 need (iss092_service_port_face_decision, 2026-10-30) + 本域规格书全文取代 ⇒ 同一问题问两遍, 旧条留著只会重复催办",
        evidence="MECH/SERVICE_PORT_ISS092.md (2026-10-30, ISS-092 交卷) 已给完整规格 (开口 10.20×4.60 / 盖板 13.20×7.60×1.20 / 内腔 4.70 / SP-A·SP-B·SP-C 三案 / §11 七条接口请求) ⇒ 本条 (2026-10-27) 的全部问项被覆盖",
        level="[实测]",
        answer=None, ref=None, board="N"),

    "iss100_jchg_pitch_fix": dict(
        action="close+answer",
        reason="脚本口径早已改掉 ⇒ 那条 [FAIL] 假警报不复存在; 且本条引的『12mm 板宽』基线本身已作废",
        evidence="[实测] MECH/hinge_usb_check.py:67 \"j_chg_pitch_mm\": (0.50, \"J_CHG 定稿 0.5mm pitch (网表 V1.5 起; ISS-085 已定 0.5mm —— 原来这里写 1.27 是过期口径, 导致 [FAIL] 假警报)\")",
        level="[实测]",
        answer="已修: MECH/hinge_usb_check.py 的 j_chg_pitch_mm = 0.50 (脚本第 67 行自带作废说明) ⇒ 旧口径的 [FAIL]『J_CHG 座体 13.43mm > 板宽 12mm』是脚本过期造成的假警报, 现行板宽 30.00 / 座体 6.50 ⇒ 装得下。★另: 本条引的『12mm 板宽』基线已作废 (现行 60×30, MECH/BOARD_GEOM_30MM.md §1)。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-3 + MECH/hinge_usb_check.py:67",
        board="N"),

    "iss100_hw_pcb_outline_stale": dict(
        action="KEEP",
        reason="半边已闭合 (pcb_outline), 半边仍真冲突 (chg_input_limit 仍是 0.822 旧系数) ⇒ 不能整条关, 也不该整条留着",
        evidence="[实测] hw.yaml interface_claims.pcb_outline = 60x30mm (2026-11-01 已订正) ✔; chg_input_limit = 0.82-1.00A (仍是 390Ω 档 + 倒方向 0.822 系数) ✘ ⇒ 与 ISS-229/230 现行 680Ω 口径 (IIN 0.574A / ICHG 0.698A / 单 pin 0.349A) 不一致",
        level="[实测]", answer=None, ref=None, board="Y",
        owner="hw-lead (经项目总工)",
        why="分片取值属硬件总工地界, 我不许代改; 且这两个数会进板那一趟的 P10 充电链判据",
        oneline="hw-lead: 请把 interface_claims.chg_input_limit 从 0.82-1.00A (390Ω 档 + 0.822 倒向系数) 改成 680Ω 现行口径 (IIN 0.574A / ICHG 0.698A / 单 pin 0.349A), 出处 MECH/HINGE_POWER_CALC.md §0-A.1"),

    "iss099_hw_mounting_holes": dict(
        action="close+answer",
        reason="本条提的『2x M1.2 对角分布』固定孔方案已被 PIN-SET-2 套 A 取代 ⇒ 无待裁项",
        evidence="[实测] 现行套 A (MECH/BOARD_GEOM_30MM.md §3 + HW/pcb60x30_check.py:119-124 + mech.yaml interface_claims.pcb_mounting): P1(8.00,15.00)/P2(52.00,15.00) 定位销 ⌀2.0 (P1 全基准 + P2 只定 Y) + S1(8.00,10.00)/S2(52.00,20.00) 压紧 ⌀1.4",
        level="[实测]",
        answer="固定孔位已定 (PIN-SET-2 套 A): 2x 定位销 ⌀2.0 (P1 8.00/15.00 全基准 + P2 52.00/15.00 只定 Y) + 2x 压紧 ⌀1.4 (S1 8.00/10.00 + S2 52.00/20.00)。[实测] MECH/BOARD_GEOM_30MM.md §3 + HW/pcb60x30_check.py:119-124。★本条原提的 2xM1.2 对角分布 (5.0,2.50)/(55.0,12.50) 已作废 —— 15mm 板宽时代的方案, 且会压 SoC 逃线带。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-5 + MECH/BOARD_GEOM_30MM.md §3",
        board="Y"),

    "iss099_hw_jchg_qty": dict(
        action="close+answer",
        reason="备料口径已落表 ⇒ 无待裁项",
        evidence="[实测] HW/BOM_v1.csv:70 note「实物一对 (框侧座 + 脚侧座), 备料按 2 只」+ HW/netlist_v1.csv L38 note「J_CHG 实物是一对 (框侧座 + 脚侧座), 采购/备料别只算一只」",
        level="[实测]",
        answer="已落: J_CHG 实物是一对 (框侧充电板座 + 脚侧主 PCB 座), 备料按 2 只。[实测] HW/BOM_v1.csv:70 + HW/netlist_v1.csv L38 note (V1.9 结构侧回执)。★BOM 的 qty 列恒为 1 = 逻辑器件口径, 不是采购数。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-6 + HW/BOM_v1.csv:70",
        board="N"),

    "iss100_stale_cost_rows": dict(
        action="KEEP",
        reason="HW 文档正文 4 行旧代价仍在 (我不开 HW 地界)",
        evidence="[实测] HW/PCB_FORM_FACTOR_RECHECK.md L342 (板宽 15mm → 镜腿截面净高 37→40mm) / L377 (§3.1 15mm 板宽代价行) / L425 (M3 反问净高 37→40mm) 三行仍带作废口径 (开头更正声明只覆盖 ① 净高 37→40 一条)",
        level="[实测]", answer=None, ref=None, board="N",
        owner="hw-lead (经项目总工)",
        why="正文行属 HW 地界; 我只在 mech-lead 侧的结构结论是对的 (串行模型下净高 38mm 一毫米不用动)",
        oneline="hw-lead: 请删/改 HW/PCB_FORM_FACTOR_RECHECK.md 的 L342 / L377 / L425 三行 15mm 板宽旧代价 (L185 若仍在也一并清), 结构侧回执: 串行模型下镜腿根部净高 38mm 一毫米不用动, 打印件不改版"),

    "iss092_service_port_face_decision": dict(
        action="close+answer",
        reason="本域默认假设已生效 (SERVICE_PORT_ISS092.md §11 I-2 明写『不回就按这个做』) + 板那一趟已按外侧面给坐标 ⇒ 形态待裁项消解",
        evidence="[实测] MECH/SERVICE_PORT_ISS092.md §11 I-2「假设按【外侧面】+ 接受 +0.73 g」+ HW/PCB/BOARD_ONEPASS_WORKPACKET.md §1 C-OPEN-1 (调试口 罩 J_DEBUG) / C-OPEN-2 (检修口 罩 J_UART) 已按外侧面 SP-A 给出坐标 (帧 B160x100)",
        level="[实测]",
        answer="形态已定 = 镜脚外侧面 SP-A (H 法向朝外, 探针与焊盘同轴), 已按此落进板那一趟的开口认领句 (HW/PCB/BOARD_ONEPASS_WORKPACKET.md §1 C-OPEN-1/C-OPEN-2, 帧 B160x100); 重量代价 +0.364 g/侧 → 整机 +0.73 g 已按『接受』执行。[实测] MECH/SERVICE_PORT_ISS092.md §11 I-2 + §0 #1/#4。★剩余动作不是需求: +0.73 g 还没落进 MECH/MECH_BUDGET.md §3 重量表 ⇒ 登记为重量表一次订正。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-7 + MECH/SERVICE_PORT_ISS092.md §11 I-2",
        board="Y"),

    "iss092_probe_before_cover_decision": dict(
        action="close+answer",
        reason="本域默认假设已生效 (§11 I-3) 且规格书已按该假设出图 ⇒ 无待裁项",
        evidence="[实测] MECH/SERVICE_PORT_ISS092.md §11 I-3「假设按【装前压针】」+ §0 #6 (产线: J_DEBUG 改 2×5@1.27 Cortex-10 焊盘阵列 D-1 + 装前压针) + §0 #7 (零新增工位) + §4.2 C-6「默认无 (实心盖板)」",
        level="[实测]",
        answer="已定 = 采纳『装前压针』: 盖板最后装 ⇒ 最终盖板可以是实心 (默认无让位窗), 零新增工位, 防汗/防尘最好。[实测] MECH/SERVICE_PORT_ISS092.md §0 #6/#7 + §4.2 C-6 + §11 I-3。★若改为『装盖板压针』, 则须开让位窗 6.40×3.90 且接受防汗降级 —— 该分支不成立, 不采用。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-8 + MECH/SERVICE_PORT_ISS092.md §0 #6/#7",
        board="Y"),

    "iss092_ip_wording_decision": dict(
        action="close+answer",
        reason="本域默认假设已生效 (§11 I-4) + §0 #5 已把口径写死 ⇒ 无待裁项",
        evidence="[实测] MECH/SERVICE_PORT_ISS092.md §0 #5「IP: …【本项目现阶段不宣称 IP 等级】(FRAMEWORK_SCOPE H5-04 已把 IP 推迟到量产)」+ §6 三段措辞 + §11 I-4",
        level="[实测]",
        answer="措辞已定: 本项目现阶段【不宣称 IP 等级】; 规格书写『防汗; 量产件按 IPx4 设计 (待认证)』, 量产加 C-13 密封条 + C-14 迷宫搭边后才成立 IPx4 (防溅水), IPx5/x7 (浸水) 不可达。[实测] MECH/SERVICE_PORT_ISS092.md §0 #5 + §6 + §11 I-4 + FRAMEWORK_SCOPE H5-04。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-9 + MECH/SERVICE_PORT_ISS092.md §0 #5",
        board="N"),

    "iss092_print_pack_rev": dict(
        action="KEEP",
        reason="改版内容与批期都还没定",
        evidence="[实测] Rev B 打印包 (MECH/print/gen_print_pack_revb.py + temple_cage_revb.stl 等) 只含检具+试样; ISS-092 的通窗/螺钉凸台/磁铁沉槽/定位凸台/盖板件 五项尚未进包 (SERVICE_PORT_ISS092 §7.1 列的『镜脚外壁成形』清单); 第三档 Type-C 试样已单列 (ISS-218)",
        level="[实测]", answer=None, ref=None, board="N",
        owner="main (批期排程)",
        why="本域出不了『排进哪一批』的答案 —— ISS-027 批次表是项目总工的排期地界; 且批次排序要先看板那一趟",
        oneline="main: 请把 ISS-092 的打印包改版五件 (通窗 / 螺钉凸台 / 磁铁沉槽 / 定位凸台 / 盖板件) 排进 ISS-027 哪一批 (本域建议 B2 镜脚装配验证批), 并把第三档 Type-C 试样 (frame_typec_coupon_tier3_revb.stl) 同批"),

    "mech_dfm_battery_seat": dict(
        action="KEEP",
        reason="量产架构改动 = boss 级 (零件数 +2 / 成本), 不该由结构侧自决",
        evidence="[实测] MECH/MECH_BUDGET.md §5.5 + DFM_REVIEW: 镜脚下壳主腔深 38.00mm, 内外双面 1° 脱模 ⇒ 内腔横截面窄端少 1.327mm ⇒ 电芯段 H 链最坏余量 -0.577mm (几何做不出来); 皮纹面 0.5° 也只救到 0.087mm < 判据 0.40 ⇒ 公差/斜度都救不回来 ⇒ 唯一解 = CNC 金属嵌件 (Al6063-T6, 与 SoC 骨架共基准)",
        level="[推算]", answer=None, ref=None, board="N",
        owner="main → boss",
        why="架构/成本取舍是老板级; 改了会动整条镜腿壳体分型 (与 ISS-127 P1 耦合)",
        oneline="main→boss: 电池座与 PCB 座是否接受从『注塑件本体特征』改为 CNC 金属嵌件 (Al6063-T6, 与 SoC 骨架共基准)? 几何上不做不出来 (电芯段 H 链最坏 -0.577mm, 皮纹面 0.5° 也只救到 0.087mm), 代价 = 零件数 +2 (左右各 1) + 成本"),

    "mech_dfm_shell_geometry": dict(
        action="KEEP",
        reason="量产外形件建模排期 = 项目总工的排期地界",
        evidence="[实测] Rev B 打印包交付的是检具+试样 (fit_coupon_revb 150×132×22 / temple_cage_revb 60×122.4×27.8 / frame_typec_coupon_revb 33×3×7.2) ⇒ 不含镜框主体 / 镜腿上壳 / 镜脚下壳任何量产外形件 ⇒ 脱模斜度/分型面/缩痕/飞边/顶针目前 0 个数据点",
        level="[实测]", answer=None, ref=None, board="N",
        owner="main (排期) + 结构侧出模型",
        why="本域可做的是【建模】, 排期与开模次序要 main 定; 且与 ISS-127 P1 (H 向分型) 架构裁耦合",
        oneline="main: 请定量产外形件建模排期 (本域建议在 ISS-027 B3 镜框与光学批之前完成建模并跑 MECH/dfm_check.py 面级检查; 未完成不开模); 建模口径按 ISS-127 P1 (H 向分型 = 皮肤盖 + 内胆)"),

    "mech_rebase_netlist_hinge_mismatch": dict(
        action="KEEP",
        reason="N5 (J_CHG 不再跨铰链 / 充电链转 DNP) 至今没落 ⇒ 铰链区结构结论在 demo 阶段仍需成立",
        evidence="[实测] HW/netlist_v1.csv board 列实读 = MAIN_PCB 404 / CHG_BOARD 94 / HINGE 15 ⇒ CHG_BOARD 仍有 94 行未转 DNP; J_CHG 逐脚行 (L15-L23) 仍标 board=HINGE",
        level="[实测]", answer=None, ref=None, board="N",
        owner="main + hw-lead",
        why="网表是硬件总工的地界, 我只报; 结构侧影响 = 铰链区整套结论 (ISS-085/089/091) 是否转 deferred 到整机阶段",
        oneline="main+hw-lead: DEMO_BOARD_HW_DECISION §5-N5 (J_CHG 不再跨铰链 / 充电 IC 与电池位改 DNP) 至今未落 —— HW/netlist_v1.csv 仍 CHG_BOARD 94 行未转 DNP 且 J_CHG board=HINGE; 请给一句: demo 阶段是否保留 J_CHG 跨铰链? (结构侧按『保留 ⇒ 铰链区结论继续成立 / 取消 ⇒ 本域 ISS-085/089/091 转 deferred』执行)"),

    "mech_rebase_pcb_width_y_holes": dict(
        action="close",
        reason="被同批更晚的仲裁条 (iss192_pcb60x30_holes_set_b_to_set_a) 取代 ⇒ 同一件事问两遍",
        evidence="[实测] 套 A 已仲裁并落表 (MECH/BOARD_GEOM_30MM.md §3 + HW/pcb60x30_check.py:119-124 + mech.yaml interface_claims.pcb_mounting) ⇒ Y 坐标不再是待确认项",
        level="[实测]", answer=None, ref=None, board="Y"),

    "iss192_pcb60x30_holes_set_b_to_set_a": dict(
        action="close+answer",
        reason="hw-lead 已按套 A 改完 ⇒ 仲裁动作已闭环",
        evidence="[实测] HW/pcb60x30_check.py:119-124 HOLES = [P1 (8.00,15.00) ⌀2.0 全基准 / P2 (52.00,15.00) ⌀2.0 只定 Y / S1 (8.00,10.00) ⌀1.40 只压紧 / S2 (52.00,20.00) ⌀1.40 只压紧] = 套 A",
        level="[实测]",
        answer="已按套 A 落地: HW/pcb60x30_check.py 的 HOLES 表已是 P1(8.00,15.00)/P2(52.00,15.00)/S1(8.00,10.00)/S2(52.00,20.00)。[实测] HW/pcb60x30_check.py:119-124。★结构侧仲裁结论 = 套 A (Y 按中心线平移, S 孔 ±5.00 不变); 打印包 Rev B 本来就是套 A, 现在 hw 侧也一致 ⇒ 两边不再差 7.50mm。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-12 + HW/pcb60x30_check.py:119-124",
        board="Y"),

    "iss192_demo_board_zero_mounting_holes_keepout": dict(
        action="KEEP",
        reason="板域 + 现役板是 B160x100 台架板 ⇒ 结构侧给不了安装孔位置, 也不许代改板",
        evidence="[实测] HW/PCB/demo_mainboard.kicad_pcb 里 MountingHole footprint = 0 个; 全板只有 2 个 np_thru_hole 且都属 USB-C 座自身壳体柱; HW/PCB/demo_mainboard_params.json 的 misc.mounting_holes 声明 4 个 [[3,3],[57,3],[3,42],[57,42]] 是 60×45 时代遗留坐标, 其中两点贴在器件区 (J_SOM_P1 最近 6.8mm / J_SOM_P2 最近 10.7mm)",
        level="[实测]", answer=None, ref=None, board="Y",
        owner="hw-lead + main (板那一趟同批改)",
        why="板与网表都归硬件总工; 结构侧只能给『骨架要几个定位基准 + 孔心到板边余量』的接口要求",
        oneline="hw-lead: demo 板 (HW/PCB/demo_mainboard.kicad_pcb, 帧 B160x100) 零 MountingHole, 而 params 里的 4 个坐标是 60×45 时代遗留且两点压在器件区 —— 请在板那一趟同批补 4 个 ⌀2.2 固定孔 (孔心到板边 >=2.50mm, 避开 SoM 承载区) 并同步 params; 结构侧回执: 骨架按 2 定位销 (全基准 + 只定 Y) + 2 压紧孔 造"),

    "iss192_mech_scripts_dead_constants_disposition": dict(
        action="KEEP",
        reason="【文件长期并存还是退役 v2】是机制裁决, 不是事实核对 ⇒ 不能由结构侧自决",
        evidence="[实测] MECH/fit_check.py (M-FIT v2) 整套基线 (板宽 12 / 板长 50 / 4 层 0.80) 一起死, 文件头已写定性 + 运行期打作废横幅, 数字一个没动; 现行版是 MECH/fit_check_v3_30mm.py",
        level="[实测]", answer=None, ref=None, board="N",
        owner="main (机制裁决)",
        why="『历史可复现 > 文件干净』还是『退役 v2』是项目取舍; 本域倾向并存 + v2 打横幅",
        oneline="main: 请裁 MECH/fit_check.py (M-FIT v2, 基线板宽12/板长50/4层0.80 已全死) 与 MECH/fit_check_v3_30mm.py 长期并存还是退役 v2? 本域倾向并存 + v2 打作废横幅 (历史可复现 > 文件干净), 只改它一个数会造出 Frankenstein 半迁移口径"),

    "iss200_mech_doc_residual_old_pinmap": dict(
        action="close+answer",
        reason="4 处旧口径已逐处订正 ⇒ 授权问题已消解",
        evidence="[实测] MECH/USB_HINGE_STRUCTURE.md: L16 §0 C-3 (40p→16p/20p/26p 已标作废, 现行 25.30 整机 / 5.00 demo) + L18 §0 C-5 (SYS 不跨铰链, 老 0.55A 口径已作废) + L19 §0 C-6 (反插真实后果 = 1 断路 + 2 短接, 不是『BAT_CHG 短接 GND』) + L286 §5.1 J_CHG 行 (老 6 脚口径已作废) + L362 §5.3 C-4 (算式已按 10p 改写, 两格已按裁写齐)",
        level="[实测]",
        answer="4 处已订正 (ISS-200/ISS-206/ISS-237 三批): MECH/USB_HINGE_STRUCTURE.md 的 §0 C-3 / §0 C-5 / §0 C-6 / §5.1 表 J_CHG 行 / §5.3 C-4 现值 = 25.30 mm (整机) / 5.00 mm (demo), 现行 pin map 1×10p@0.5。[实测] 同文件 L16/L18/L19/L286/L362。★几何数字一个没被本轮改动。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-13 + MECH/USB_HINGE_STRUCTURE.md L16/L18/L19/L286/L362",
        board="N"),

    "iss200_hw_residual_old_pinmap": dict(
        action="KEEP",
        reason="HW 是别单地界, 我不许代改 ⇒ 且 4 处旧口径确实还在",
        evidence="[实测] HW/netlist_v1.csv L38 note 仍写『pin7=VBUS_DET』(现行 pin7=NC) + L20/L21 note 仍写『V1.8: pin10 已改作 TS 专用回流』(现行 pin10=HINGE_RSV, TS_RTN 在网表 0 次出现)",
        level="[实测]", answer=None, ref=None, board="N",
        owner="hw-lead (经项目总工)",
        why="逐脚 net 行是对的, 只有 note 列带旧口径 ⇒ 机器判定以逐脚 net 为准, 但人会读 note",
        oneline="hw-lead: 请订正 HW/netlist_v1.csv 的 note 列旧 J_CHG 口径 (L38『pin7=VBUS_DET』→pin7=NC; L20/L21『pin10 已改作 TS 专用回流』→pin10=HINGE_RSV), 逐脚 net 行一个不许动"),

    "iss200_mech_frag_mech_j_chg_pins_note": dict(
        action="close+answer",
        reason="同域自相矛盾的那一条已订正 ⇒ 无待裁项",
        evidence="[实测] mech.yaml interface_claims.mech_j_chg_pins.note 现写『本 note 现与同域另一条 claim j_chg_pin_map (ISS-200 已订正) 逐脚完全一致, 分片内不一致已消除』; value 仍是 10p@0.5mm",
        level="[实测]",
        answer="已订正: interface_claims.mech_j_chg_pins 的 note 现与 j_chg_pin_map 逐脚一致 (pin1/2=BAT_CHG, 3/4=GND, 5=CHG_STAT, 6=PWR_GOOD, 7=NC, 8=TS_BAT, 9/10=HINGE_RSV), value 10p@0.5mm 未动。[实测] mech.yaml interface_claims.mech_j_chg_pins.note。★合并器检不出同域不一致, 这一条只能人工收口 —— 已收。",
        ref="MECH/MECH_NEEDS_TRIAGE.md §2 ①-14 + state/fragments/mech.yaml interface_claims.mech_j_chg_pins",
        board="N"),
}

# ============================================================================
# ② 类 · waiting_on = boss (20 条) —— 不代拍 ⇒ 交 need key + 决策码 + 选项/代价/建议默认值/不拍后果
# ============================================================================
C2 = {
    "q4_battery_scope": dict(code="M-B0", state="已闭合", mine=False,
        options="★已闭合 (老板 10-25 19:16 拍板, 项目总工代录) ⇒ 留档备查, 不再重复问",
        decision="按需触发场景下 ≥1h (老板 10-25 19:16 拍板, 项目总工代录)",
        evidence="[官方] pm.yaml needs_from[q4_battery_scope].decision (decided_by=boss 2026-10-25 19:16) + decision_truth 全局 key 集合 ⇒ 已判 answered",
        note="本条已被老板拍过 ⇒ 不在本单决策页的待拍清单里, 留档备查"),
    "q16_aspect_ratio": dict(code="M-B0", state="已闭合", mine=False,
        options="★已闭合 (老板 10-25 19:16 拍板, 项目总工代录) ⇒ 留档备查, 不再重复问",
        decision="宽高比无所谓; 选型判据改为『≥1080p60 出图能力』(老板 10-25 19:16 拍板)",
        evidence="[官方] pm.yaml needs_from[q16_aspect_ratio].decision (decided_by=boss 2026-10-25 19:16) + decision_truth 全局 key 集合",
        note="原 A/B/C 三选一作废 ⇒ 镜框光学舱尺寸不再受宽高比约束 (但仍受眼盒 ≤62mm² 约束, 见 iss208_mech_waveguide_eyebox_le_62mm2_gate)"),

    "boss_local_print_measure": dict(code="M-B1", state="待拍",
        decision="指定打印与量测执行方 (三选一)",
        options="① 把打印执行方接入 192.168.1.0/24 或开子网互通 (零采购) | ② 委托代打印服务 (¥/件 + 排期) | ③ 在能装 Bambu Studio 的桌面环境切片 + 第三方打印",
        cost="① 零采购但依赖对方改网络; ② 一次性服务费 + 沟通成本, 拿到 STl 直接下片; ③ 需一台能装切片器的机器 + 第三方面",
        recommend="① (零采购; 本机实测 ping 无响应 + TCP 990/8883/6000/4000 全 closed, 见 MECH/print/ENV_PROBE_20261101.md)",
        consequence="不拍 ⇒ 实物实测 [实测] 永远 = 0 条 ⇒ G2 阶段门永久红; B1 的 34 项工艺数据 / B2 的 49 项实测全部拿不到; 且 T-05~T-08 材料试样 (UV 老化 2000h ≈ 83 天) 排期无法启动",
        evidence="[实测] MECH/print/ENV_PROBE_20261101.md: 打印机 192.168.1.68 与本机 192.168.2.4/24 跨网段不可达; 无切片器 (Bambu Studio/OrcaSlicer/Cura 均无); 无卡尺/千分尺/塞尺; 无 USB 串口",
        board="Y", owner="boss (经项目总工)"),

    "reva_cell_thickness_tol": dict(code="M-B2", state="待拍",
        decision="电芯厚度公差写进采购要求 ≤±0.10 (★并须把型号名改对)",
        options="① 收紧到 ≤±0.10 并把型号写对 (见 evidence 的型号错配) | ② 维持 ±0.15 (需把压垫工作间隙从 0.15 加到 0.20+, 吃掉 H 链余量) | ③ 改用丰江 432243 (4.30mm) 绕开厚度公差",
        cost="① 采购窗口可能变窄 (★但型号改对后才是真约束); ② H 链余量 -0.05~0.10, 判据 0.60 口径下余量归零风险; ③ 整机 +2.28g (MECH/CLEARANCE_FIX.md §解B 实测)",
        recommend="① + 型号改对 (本域建议)",
        consequence="不拍 ⇒ 采购单按 340mAh/4.60mm 下单, 而真型号厚 6.40mm ⇒ 到货装不进 7.30mm 镜腿 ⇒ 电芯段 H 链直接报废 (最坏 -1.10mm); 且 ±0.15 下最坏情况电芯顶到顶板 (硬干涉 0.25)",
        evidence="[官网] renata.com 锂聚合物电池页实读: ICP422339PR = 340mAh / 4.6mm / 23.5 / 40.5; ★ICP582035PR-01 = 340mAh / **6.4mm** / 20.5 / 37 ⇒ ★★本项目把『4.6×23.5×40.5』挂在 ICP582035PR-01 名下 (MECH/MECH_BUDGET.md L330/L332/L340 + MECH/BOARD_WIDTH_15MM.md:54) 是【型号-尺寸错配】, 正确型号是 ICP422339PR。★另 [实测] 公差未公开 (MECH/CLEARANCE_FIX.md §T-7 标 [0数据])",
        board="N", owner="boss (经项目总工) + main (采购条款落位)"),

    "mech_reltest_kit_site": dict(code="M-B3", state="待拍",
        decision="可靠性测试的场地与工装预算 (A 自购小件 / B 借用 / C 外委)",
        options="A 自购小件 ¥800-1500 (扭力计/拉力计/人工汗液试剂/酒精/色卡) | B 借用 (恒温箱/UVA-340 老化箱/振动台/FPC 动态弯折机) | C 外委 (X-ray 抽检 + 切片 ¥3000-8000 + MTF)",
        cost="A 最便宜但只能覆盖 T-01~T-08 的一部分; B 零采购但依赖外部排期; C 单价最高但一次买齐 12 类用例",
        recommend="A + C (A 覆盖贴肤/化学类, C 只外委 X-ray/切片/MTF 三项)",
        consequence="不拍 ⇒ 12 类用例全部停在方案阶段 (UV 单项就占 83 天设备窗口) ⇒ 1 台样机的唯一一次采集机会作废",
        evidence="[实测] state/measurements.yaml M-PRINT 实证: 本机无量具/无打印机/无恒温箱/无老化箱/无振动台/无 X-ray; 与 pm.yaml 的 test_equipment_budget 同一总账 (不重复申请金额)",
        board="N", owner="boss (经项目总工)"),

    "mech_reltest_usb_mon_kit": dict(code="M-B4", state="待拍",
        decision="ISS-085 T-13 监测设备清单 (与 M-B3 同一笔预算)",
        options="① USB 协议分析器 | ② 示波器 + 差分探头 | ③ 主机端自动批量传输脚本 | ④ 自制扭转保载夹具 | ⑤ FPC 动态弯折机 | ⑥ 阻抗仪",
        cost="① 单价最高但一键出报告; ② 通用件可复用; ③④⑤⑥ 单价低但要做工装",
        recommend="② + ③ (先把 USB 连续性判据立起来, 动态弯折另借)",
        consequence="不拍 ⇒ T-01/T-02/T-03 照做, 但 T-13 无数据 ⇒ 跨铰链 USB 链路连续性始终没有量产抽检口径",
        evidence="[推算] 挂测式, 不占额外样机; 人工手捏不住 0.5N·m 稳态 ⇒ 必须做夹具",
        board="N", owner="boss (经项目总工)"),

    "iss047_margin_criterion_decision": dict(code="M-B4b", state="已闭合 (main 已答)", mine=False,
        decision="俯角余量口径 = B' 有效余量 >=4deg (含边框遮挡 1.91deg => 俯角 <=25.89deg, h_max d=35 = 16.99mm) —— ★本条已被 main 用同一 key 答过 (merge 口径 answered) ⇒ 本单只留档, 不再重复问",
        options="—", cost="—", recommend="—",
        consequence="—",
        evidence="[实测] merge 口径: 该 key 有 to=mech-lead 的答复 (main 写) ⇒ 需求已闭合; ★但 DECISION_INDEX_2026-11-18.md 的待拍清单 #25 仍挂着这一条 ⇒ 建议 main 把它从清单里划掉, 免得重复催办",
        note="★与 M-B4 (mech_reltest_usb_mon_kit) 编号相邻但不是同一条, 故用 M-B4b"),
    "iss091_rilim_decision": dict(mine=True, code="M-B5", state="已闭合",
        decision="R_ILIM 档位 = 680Ω (V-4 已裁)",
        options="—",
        cost="—", recommend="—",
        consequence="—",
        evidence="[官方] DECISION_PENDING_2026-11-16.md §A2 行 A2 (V-4 建议 680Ω) + [实测] HW/netlist_v1.csv L47 已落 680Ω ±1% (IIN 0.574A / ICHG 0.698A / 单 pin 0.349A, 余量 1.43×); ★本条原文的『皮肤 47.1C→39.9C / 390Ω 42.1C / 充电 22→35min』按作废系数 0.822 算 ⇒ 已作废, 无有效数字",
        board="N", owner="—"),

    "iss091_worn_while_charging": dict(mine=True, code="M-B6", state="已闭合",
        decision="『边戴边充』不允许 (老板 10-28 已拍)",
        options="—", cost="—", recommend="—", consequence="—",
        evidence="[官方] 老板 10-28 拍板『边戴边充不允许』⇒ [实测] HW/netlist_v1.csv L47 note『V1.8/V1.9 产品语义仍有效 (老板 10-28 边戴边充不允许 ⇒ 充电时眼镜不在皮肤上 ⇒ 皮肤温度不再是充电时的硬约束)』",
        board="N", owner="—"),

    "iss100_board_length": dict(mine=True, code="M-B7", state="已闭合",
        decision="板长 = 60.00mm (10-28 项目总工裁)",
        options="—", cost="—", recommend="—", consequence="—",
        evidence="[官方] MECH/BOARD_GEOM_30MM.md §1「板长 X 60.00mm (X=0 = 铰链端) · 10-28 项目总工裁」+ §1 作废值行『12mm / 15mm / 板长 76 / 板长 50』",
        board="Y", owner="—"),

    "iss099_poka_yoke_decision": dict(mine=True, code="M-B8", state="已闭合 (按本域默认假设)",
        decision="机械防呆 = 结构硬约束 (外侧面防呆 + 定位键)",
        options="—", cost="—", recommend="—", consequence="—",
        evidence="[实测] MECH/USB_HINGE_STRUCTURE.md §5.3 C-3「4 个跨铰链连接器全部要求带机械定位键 / 非对称几何, 且 J_CHG 额外要求防反插」+ §0 C-6「必须加机械防呆 (P2S 打印件可零成本实现)」+ §3.2 第 6 条「FFC/BTB 座需带定位键型号; 且与 J_CHG 的防呆方案保持一致」; ★真实反插后果已按现行 10p map 更正 = 1 断路 (BAT_CHG 落预留脚) + 2 短接 (GND↔TS_BAT / CHG_STAT↔PWR_GOOD), 不是老口径的『BAT_CHG 短接 GND』",
        board="N", owner="—"),

    "iss099_rilim_300_dead": dict(mine=True, code="M-B9", state="已闭合",
        decision="R_ILIM 300Ω / 260Ω 已判死 (随 V-4 落表)",
        options="—", cost="—", recommend="—", consequence="—",
        evidence="[实测] HW/netlist_v1.csv L47 note「300Ω 档单 pin 0.791A / 260Ω 档单 pin 0.912A ⇒ 均判死」+ [官方] DECISION_PENDING_2026-11-16.md §A2 A2 建议值栏含『300Ω (建议正式判死: 0.534A > 0.5mm pitch FPC ZIF 额定天花板 0.5A)』; ★判死原因与本条一致, 且已落表",
        board="N", owner="—"),

    "proto_wear_criteria": dict(code="M-B10", state="待拍",
        decision="B4 佩戴体验三项可测项定义 (夹持力 / 配重分布 / 鼻梁压感)",
        options="① 老板给三个数 (夹持力 N / 配重分布 % / 鼻梁压感 mm 或 g) | ② 老板只给『合格区间』不点具体值 | ③ 授权结构侧按 ISO 12845/EN ISO 9241-6 提建议值由老板确认",
        cost="① 最省事但要老板花时间; ③ 本域出数有依据 (ISO 12845 夹持力分布 + 鼻梁区接触压强), 但仍需老板签字",
        recommend="③",
        consequence="不拍 ⇒ 这三项全标 [0数据] 且无判据, 而 1 台样机只有一次采集机会 (RELIABILITY_TEST_PLAN §B2.3/B3.3 样本量硬边界) ⇒ 漏测后续补不回来 ⇒ B4 佩戴体验这一整项作废",
        evidence="[实测] MECH/RELIABILITY_TEST_PLAN.md §B2.3/B3.3 样本量硬边界; [0数据] 三项判据当前均无值",
        board="N", owner="boss (经项目总工)"),

    "proto_b4_reliability_kit": dict(code="M-B11", state="待拍",
        decision="B4 当天的器具清单 (T-14 无损段 + T-13 挂测位)",
        options="① 沿用 M-B3/M-B4 的总预算, 只确认『本批次要哪几样』 | ② 单独批一笔 B4 零星器具",
        cost="① 零重复申请; ② 多一次审批",
        recommend="① (同源同账)",
        consequence="不拍 ⇒ B4 当天 T-14 (弯折区结构审查 + J_CHG 反插 20 次) 与 T-13 挂测位都缺器具 ⇒ 当天只能做目视, 无留证",
        evidence="[实测] T-14 反插只需 J_CHG 实物一对 (打印的 R11 防呆件 B2 出) + 计数; T-13 需协议分析器/示波器差分探头 + 自动传输脚本",
        board="N", owner="boss (经项目总工)"),

    "iss017_local_print_measure_unblock": dict(code="M-B12", state="待拍",
        decision="ISS-017 实物实测 0 件的解锁条件 (与 M-B1 同一笔, 合并拍)",
        options="① / ② / ③ 同 M-B1; 另加量测侧四件套 (数显卡尺 0.01mm + 塞尺 0.02mm 一档 + 弹簧秤 0-25N + 电子秤 0.01g) 或由打印方代测回填",
        cost="量测四件套 ≈ ¥300-600 (一次性, 可长期复用); 代测回填免费但每批一次往返",
        recommend="① + 自购量测四件套",
        consequence="不拍 ⇒ 同 M-B1: G2 永久红, B1/B2 实测拿不到; ★M-PRINT 是 B1 的唯一硬前置 ⇒ 它不解锁, B1→B2→G2 直接少 2 项",
        evidence="[实测] MECH/print/ENV_PROBE_20261101.md; 已交付可直接下片的 Rev B 打印包 (自检 93/93 + 38/38 rc=0) + 116 项测量清单 (总 116, MECH/print/MEASURE_CHECKLIST.md N1~N27 + 其余)",
        board="Y", owner="boss (经项目总工)"),

    "mech_mat_skin_coating_decision": dict(code="M-B13", state="待拍",
        decision="皮肤侧 PU 封闭涂层是否列为必须工序 + 整机是否做 ISO 10993 评价",
        options="① 列为必须工序 + 只对涂层件出 ISO 10993 声明 (暂不做整机评价) | ② 不列 (皮肤侧直接裸 PA6-CF) | ③ 整机做 ISO 10993 生物相容性评价",
        cost="① 增加 1 道工序 + 周期; ③ 排期后移 (1 台样机阶段做整机评价不现实)",
        recommend="① (与本域默认假设一致)",
        consequence="不拍 ⇒ 皮肤侧耐汗液/化妆品的责任无归属 ⇒ T-05~T-08 的 R6-1/R6-2 两组试样对比失去判据 ⇒ 贴肤面是否合格无结论",
        evidence="[官网] LOCTITE AA 3311 官网明确标注 ISO-10993 biocompatible (UV 胶侧生物相容有官网依据) ⇒ 可作为涂层/胶粘剂侧的合规依据; [推算] 整机贴肤消耗品属性 ⇒ 建议先做涂层件声明",
        board="N", owner="boss (经项目总工)"),

    "mech_mat_sweat_test_spec": dict(code="M-B14", state="待拍",
        decision="T-05~T-08 材料试样送检执行方 (7 组试样 + 老化箱/恒温槽排期)",
        options="① 送第三方检测机构 (贵, 报告权威) | ② 自建 (需老化箱/恒温槽, 本机没有) | ③ 混合: 第三方做 T-06/T-08 (UV 老化), 自建做 T-05/T-07",
        cost="T-08 UVA-340 2000h ≈ 83 天设备窗口 ⇒ 建议最先启动; 第三方单项 ¥ 数百~数千",
        recommend="③ + 立刻启动 T-08 排期",
        consequence="不拍 ⇒ 83 天的 UV 老化窗口错过, 全部顺延一个季度; 且 T-06 硬判据 (UV 后剪切 ≥90%) 没有被执行方",
        evidence="[实测] 试样清单: R6-1(PA6-CF 无涂层) / R6-2(PA6-CF+PU 涂层) / R6-3(VMQ-A50 硅胶垫 0.2mm) / R6-4(VHB5962 贴 PA-CF / 贴阳极铝) / R6-5(PC 窗口无 AF) / R6-6(镁合金转化涂层试片) / R5 三明治 ×3; 与 M-B3/M-B12 不重复 (本条只加材料试样与排期)",
        board="N", owner="boss (经项目总工)"),

    "mech_mat_nose_pad_criteria": dict(code="M-B15", state="待拍",
        decision="鼻托压力 / 镜腿压力分布 / 佩戴稳定 / 可佩戴时长 4 项判据",
        options="① 老板给 4 项可测判据 (压力 N / 分布 % / 稳定时长 h / 可佩戴 h) | ② 授权结构侧按 ISO 12845 + 现有 B4 方案提建议值",
        cost="① 老板花时间; ② 本域出数有依据但需老板签字",
        recommend="②",
        consequence="不拍 ⇒ ISS-038 的压力侧四项永远无判据 ⇒ 鼻托与镜腿的设计无从收敛 (材料侧交了 VMQ-A50 但压不出可用性结论)",
        evidence="[实测] ISS-038 已把压力侧划给 mech-lead, 但 ISS-024 本单只交材料 ⇒ 压力侧无判据; [0数据] 四项当前全无值",
        board="N", owner="boss (经项目总工)"),

    "mech_dfm_draft_texture": dict(code="M-B16", state="待拍",
        decision="镜腿皮肤侧是否接受皮纹面/喷砂面 (而非光面)",
        options="① 接受皮纹面 ⇒ 脱模斜度可放宽到 0.5° (深腔截面差 1.327→0.663mm) | ② 不接受 ⇒ 皮肤侧须 1.5° ⇒ 截面差 1.990mm",
        cost="① 外观取舍 + 模具成本略高; ② 几何余量被吃掉 0.663mm ⇒ 电芯段 H 链更紧",
        recommend="① (本域默认假设: 按皮纹面推进, 鼻梁区仍可光面)",
        consequence="不拍 ⇒ 脱模斜度只能按 1.5° 取 ⇒ 量产外壳几何做不出来 (与 mech_dfm_battery_seat 同一条链) ⇒ 开模前必须回来",
        evidence="[推算] 脱模斜度只吃垂直于拉出方向的截面: 1.327mm (1.0°) / 0.663mm (0.5°) / 1.990mm (1.5°); 判据要求 Δ≤0.35mm; 皮肤接触面清单见 ISS-024 §2.7",
        board="N", owner="boss (经项目总工)"),

    "iss209_mech_d_value_decision": dict(code="M-B17", state="待拍",
        decision="评估距离 d 取 15 / 18 / 20 (眼盒判据 V2 §3 ⑤-b)",
        options="d=15 ⇒ T=18.00mm, 可动余量仅 0.20mm (< 判据 0.60 ⇒ 装配不可行) | d=18 (同类公开值) ⇒ T=21.00mm, 余量 3.20mm (唯一装得下且有余量的折中) | d=20 ⇒ T=23.00mm, 余量 5.20mm 但镜框最厚 ×1.92 于 12mm 目标",
        cost="d=15 直接否掉当前腔体布局; d=20 镜框厚 23mm, 重量与外观代价大",
        recommend="d=18 (本域只给数, 不拍板)",
        consequence="不拍 ⇒ 镜框正中区腔体重排 (T = d+3.0) 与分光件规格 (C-6) 都定不下来 ⇒ 镜框占位件开不了工 ⇒ ISS-209/219/222 的下游全部挂起",
        evidence="[推算] MECH/CENTER_CAVITY_RECALC.md (T=18/21/23mm, 冲突量 3.20/6.20/8.20mm) + MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md §3 ⑤-b (结构侧不许放宽或收紧)",
        board="N", owner="boss (经项目总工)"),
}

# ============================================================================
# ③ 类 · vendor / jbd (16 条) —— 老板政策: 不再发信, 全靠自己查 ⇒ 自查 + 证据等级 + 降级方案 + 关闭
# ============================================================================
C3 = {
    "jbd_waveguide_2d": dict(
        answer="【自查结论 · 不再等外部回信】JBD 官网 (jb-display.com) 只公开 MicroLED 光引擎/投影器与开发套件参数: Hummingbird Mini Ⅱ 单色投影 0.15cc / 0.3g / 60mW; Hummingbird Ⅱ 全彩投影 0.2cc / 0.5g / 95mW; Hummingbird Ⅰ 全彩光引擎 6000 nits / 30° FOV; 第三代为【刻蚀】单层衍射光波导 (与雷鸟 X3 Pro 同款路线)。⇒ ★波导 2D 外形图 / 耦入区位置与容差角 / 是否自带定位基准 三项【公开渠道查不到】 [0数据]。【降级方案】① 镜框按【参数化占位 + 可换压框】设计: 卡槽按 3 档假想外形建模, 到货只换压框不改镜框主体 (ISS-134 V2 已定同一路径, 见 MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md); ② 眼盒面积 ≤62mm² 从结果改为【选型前置条件】 (MECH_BUDGET §1.7 X-1/X-6); ③ 彩虹纹验收改用代用量 (亮度均匀性 / 色差 ΔE / 彩虹抑制效率), 结构侧只承诺【装配应力可控】(沉槽/压垫/对称压紧), 不承诺彩虹纹合格 —— 膜层色差不由结构决定。",
        evidence="[官网] jb-display.com 产品页 + JBD 官网新闻 (第三代刻蚀光波导: 彩虹效应抑制效率 95% / ARTCs 校正后全局亮度均匀性 >80% / 色差 ΔE 0.02); [0数据] 波导 2D 外形图 / 耦入区容差角 / 安装基准 三项公开渠道查不到",
        level="[官网]/[0数据]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-1"),

    "jbd_dual_eye_module": dict(
        answer="【自查结论 · 前提已作废】走鹃Ⅱ 已于 2026-11-02 换型为视涯 0.49\" 1920×1080 SiOLED 面板 (老板『视崖屏幕已经不用了』, pm.yaml decision visionox_inquiry_release) ⇒ 本条问的『走鹃Ⅱ 一拖二双目模组或分光方案』的对象已不存在。【降级方案】结构按 ISS-209 重排口径留位: 正中区轴向厚度 T = d + 3.0 = 18/21/23mm (d=15/18/20, 待 M-B17 拍) + 眼盒 ≤62mm² 约束下的分光件新规格 (45° 平板 11×11×1.5 + 转向棱镜 ×2 9×9×5, 0.97cc) ⇒ 一拖二 vs 双光机之争被『参数化腔体 + 可换压框』吸收, 到货不改镜框主体。",
        evidence="[官方] pm.yaml needs_from[visionox_inquiry_release].decision (老板 2026-11-04 09:5x『视崖屏幕已经不用了』) + [推算] MECH/CENTER_CAVITY_RECALC.md",
        level="[官方]/[推算]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-2"),

    "jbd_optical_engine_dims": dict(
        answer="【自查结论 · 前提已作废 + 尺寸公开查不到】① 走鹃Ⅱ 已作废 (同 ③-2); ② 官网只给体积/重量/功耗/FOV (Hummingbird Ⅱ 全彩投影 0.2cc / 0.5g / 95mW / 30° FOV), **三维长×宽×高未公开** [0数据]。【降级方案】镜框光学腔体按 ISS-209/219 的参数化口径出 (T=18/21/23mm 三档 + 眼盒 ≤62mm²), 并给 MECH/print/optical_cage_TEMPLATE.stl 一个【可换压框】的卡槽模板 —— 不再等待光机外形到位。",
        evidence="[官网] jb-display.com 产品页 (Hummingbird Ⅱ = 0.2cc / 0.5g / 95mW / 30°); [0数据] 三维外形尺寸; [官方] 走鹃Ⅱ 已作废",
        level="[官网]/[0数据]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-3"),

    "vendor_ars45_thermal_pad": dict(
        answer="【自查结论 · 前提已作废】① 酷芯微 ARS45 已不在选型内 (老板 2026-10-29 00:49 令跳过酷芯微改选国内 TOP5; 现役主控 = RK3576); ② ARS45 底面散热焊盘 / 内置 boot storage 两项公开渠道查不到 [0数据]。【降级方案】散热路径按现役口径定死: SoC 背面散热焊盘 → 0.3mm 导热垫 → 铝/铜骨架 (纵向延伸兼 PCB 支撑) → 石墨面内扩展 → 对流, 路径不得有塑料隔断 (打印件 k=0.2 插进去热阻 +94K/W); boot storage 不占板宽 ⇒ 板宽不再受 boot storage 约束 (走板外 SPI-NOR/SD), 且『boot storage 是否内置』已由老板 2026-11-11 19:31 政策回答 (自己网上查, 不再外发)。",
        evidence="[官方] 老板 2026-10-29 00:49 (跳过酷芯微改选国内 TOP5) + 老板 2026-11-11 19:31『不再做任何邮件/供应商/原厂问询, 获取不到结果的自己网上查』; [0数据] ARS45 散热焊盘 / boot storage 公开渠道查不到; [实测] MECH/MECH_BUDGET.md §5.1 散热接触路径",
        level="[官方]/[0数据]/[实测]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-4"),

    "iss017_waveguide_rainbow_metric": dict(
        answer="【自查结论】彩虹纹四项 (亮度均匀性 / 色差 / 应力敏感度 / AR 镀膜耐久性) 在公开渠道只有【代用量】, 无可直接引用的供应商判据: JBD 官网第三代刻蚀光波导路线给出【彩虹效应抑制效率 95%】+ ARTCs 校正后【全局亮度均匀性 >80%】+【色差 ΔE 0.02】 [官网]; 波导未选型 ⇒ 具体某型号的膜层判据 [0数据]。【降级方案】① 验收改用代用量三件套 (亮度均匀性 / ΔE / 彩虹抑制效率), 数值门槛随波导选型一起定; ② 结构侧只承诺【应力项可控】(沉槽/压垫/对称压紧, 装配应力不引起应力型彩虹纹), **给不出『彩虹纹合格』的结论** —— 膜层色差与亮度均匀性由波导厂镀膜决定, 结构改不了; ③ 采购条款里写死『供方须提供 A_e (眼盒面积, 按 V2 §3 ⑥ 定义式) + 均匀性/色差指标』。",
        evidence="[官网] JBD 官网 (刻蚀光波导彩虹抑制 95% / ARTCs 均匀性 >80% / ΔE 0.02); [0数据] 具体型号膜层判据; [推算] 结构侧可控项 = 装配应力",
        level="[官网]/[0数据]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-5"),

    "mech_mat_waveguide_uv_cosmetic": dict(
        answer="【自查结论】波导/镀膜的 UV 透过率衰减 / 化妆品耐受 / 与硅胶垫相容性, 公开渠道查不到供应商分级数据 [0数据]。【降级方案】① 相容性改由【硅胶侧】承担: 波导按玻璃基 + 硅胶垫 VMQ-A50 (硅胶按有 ISO 10993 / FDA 21 CFR 177-2600 认证的牌号选, 证书未到手不得投产) ⇒ 波导本身不用背相容性; ② UV 判据 (透过率 Δ≤3%) 保留但标 [0数据], 改在【胶层与涂层】上实测 (T-06 UVA-340 2000h ⇒ 镜片/导光柱固定件); ③ 若波导带防刮涂层 ⇒ 该涂层必须同进 T-06/T-07/T-08 送检 (不接受『波导厂说没问题』)。",
        evidence="[0数据] 波导/镀膜 UV 与化妆品耐受分级, 公开渠道查不到; [官网] LOCTITE AA 3311 = ISO-10993 biocompatible (贴肤/胶粘剂侧生物相容有官网依据, 可作同类相容性论证的写法参照)",
        level="[0数据]/[官网]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-6"),

    "mech_dfm_waveguide_seat": dict(
        answer="【自查结论】波导 2D 外形 / 外形公差 / 能否承受压铸件收缩与热变形 / 安装面平面度 四项, 公开渠道查不到 [0数据] (未选型 ⇒ 无供应商数据)。【降级方案】卡槽按【CNC 卡座 + 3 点金属压条】出图 (DFM_REVIEW 1.1-12): ① 压条角度可调 ⇒ 换波导只换压条, 不动镜框主体; ② 平面度/平行度写成【设计态判据】(安装面 0.05mm / 平行度 ±0.3deg, 与 0.2mm 硅胶垫不变) 到货后按实测校正; ③ **不得**用『压铸本体直接卡波导』—— 未拿到外形公差前本体成型的卡槽必然超差。",
        evidence="[0数据] 四项几何数据公开渠道查不到; [推算] 设计态判据按 DFM_REVIEW 1.1-12",
        level="[0数据]/[推算]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-7"),

    "mech_reltest_cell_samples": dict(
        answer="【自查结论】① Renata 官网实读: ICP422339PR = 340mAh / 4.6mm / 23.5 / 40.5; ICP582035PR-01 = 340mAh / 6.4mm / 20.5 / 37 [官网]; 丰江官网实读: 432243 = 3.7V / ≥420mAh / 4.3×22.0×43.5mm / 脉冲 1~3A / 循环寿命 ≥500 [官网]; ② 膨胀曲线与内阻 公开渠道查不到 [0数据]。【降级方案】① 备件 2 只按【同批号 + 同生产月】采购 (循环/鼓包的离散靠批内一致性, 不靠规格书); ② 内阻按 0.10Ω (区间 0.08-0.15) [推算] —— 且 ISS-229 已证结论对该区间稳健 (680Ω 档 max 39.7~41.4°C 均 <43°C; 470Ω 档三档取值全破 ⇒ 470Ω 排除) ⇒ 内阻取值不改变任何结论, 该外部依赖可退休; ③ T-05 汗液浸泡判鼓包改用【实测判据】: 2 只 × 24h 浸泡后厚度/宽度复测, 单边变形 ≤0.20mm 且无渗漏 ⇒ 合格 (代替厂商膨胀曲线)。",
        evidence="[官网] renata.com 锂聚合物电池页 + battsysbattery.cn 软包聚合物电池页 (432243 行); [0数据] 膨胀曲线/内阻; [推算] MECH/HINGE_POWER_CALC.md §0-A.1 敏感性已证明结论稳健",
        level="[官网]/[0数据]/[推算]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-8"),

    "iss091_cell_ir": dict(
        answer="【自查结论】丰江官网只给尺寸/容量/循环/脉冲放电, **内阻未公布** [0数据]。【降级方案】按 0.10Ω (区间 0.08-0.15) [推算] 执行, 且该区间的敏感性已由 ISS-229 算完: 680Ω 档 max 皮肤侧 39.7°C (0.08Ω) ~ 41.4°C (0.15Ω) ⇒ 均 <43°C 红线, 结论稳健; 470Ω 档 max 44.7/45.8/48.3°C ⇒ **三档取值全破** ⇒ 470Ω 与内阻取值无关地被排除。⇒ 本条作为外部依赖可以退休, 不再挂等规格书。",
        evidence="[官网] battsysbattery.cn 432243 参数页 (无内阻项); [0数据] 内阻未公布; [推算] MECH/HINGE_POWER_CALC.md §0-A.1 + §N4 行 (ISS-229 重算的 30 行全网格)",
        level="[官网]/[0数据]/[推算]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-9"),

    "iss099_jchg_rfq": dict(
        answer="【自查结论 · 官网规格直接满足, 不需要询价】Hirose FH12-10S-0.5SH(55) 官网规格 [官网]: 单触点额定 **0.5A** / 10 位 / 0.50mm pitch / 可插 FPC 厚度 **0.30mm** / 额定电压 50V / 座高 2.00mm / ZIF flip-lock / 插拔 20 次 / 工作温度 -40~85°C / RoHS。⇒ ★RFQ 三问自己就有答案: ① 单触点 ≥0.5A ✔ (680Ω 档单 pin 0.349A ⇒ 余量 1.43×) ② 座体 6.50mm 宽 (脚本口径, 已入链) ③ 可插厚度 0.30mm > 固定段 2oz 成品 0.24-0.25mm ⇒ **不超上限** (原担心的 0.23mm 上限不成立于本型号)。【降级方案】若实测可插厚度不足 ⇒ 固定段改 1oz (压降回基准, 结论方向不变) 或固定段 2oz + 转角段单独加厚过渡。★询价函 state/outbox/j_chg_rfq.md 按老板 2026-11-12 02:02 不发, 只作留档。",
        evidence="[官网] FH12-10S-0.5SH(55) 官网/分销规格页 (Current Rating 0.5A · FFC/FCB Thickness 0.30mm · Height Above Board 2.00mm · 0.020\" pitch · 50V · 20 mating cycles); [官方] 老板 2026-11-12 02:02『不再发信, 全靠自己查资料』",
        level="[官网]/[官方]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-10"),

    "iss099_fpc_vendor_capability": dict(
        answer="【自查结论】① 分段铜厚 (固定段 2oz / 弯折段 1oz + 过渡斜坡 ≥1.0mm) = 公开 FPC 工艺通例, 无统一公开规格 [媒体/行业通例]; ② 0.5mm pitch 下 0.40mm 线宽 + 0.10mm 最小间隙 = 公开可达的常规能力 (0.5mm pitch 常规最小线宽/间隙 0.075-0.10mm) ⇒ 0.40/0.10 属常规边界 ✔ [媒体/行业通例]; ③ L2/L3 在 pin1-4 区做 keep-out 且 CAM 不自动修复 —— **这才是不可协商项**: 加工方普遍默认自动修复 ⇒ 必须写进加工图 CAM 备注 + 落料前看 CAM。【降级方案】① 做不到分段铜厚 ⇒ 固定段也用 1oz (压降回基准, 结论方向不变); ② 做不到 keep-out ⇒ 改 6 层 FPC (铰链区径向余量 1.00mm 会被挤掉, 需重算) ⇒ 因此把 keep-out 列为硬要求, 其余两项可降。",
        evidence="[媒体/行业通例] 0.5mm pitch FPC 常规最小线宽/间隙能力; [媒体/行业通例] 分段铜厚为常见工艺但无统一规格; [0数据] 具体 FPC 厂的书面确认 (不再外发)",
        level="[媒体]/[0数据]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-11"),

    "mech_mat_vendor_datasheet": dict(
        answer="【自查结论 · 三项里两项官网有、一项查不到】① 3M VHB 5962/5962P 官网 [官网]: 1.6mm 厚 (公差 ±10%) / 改良丙烯酸 / 超软丙烯酸泡棉 590 kg/m³ / 90° 剥离 39 N/cm / 动态重叠剪切 550 kPa / 最低应用温度 10°C / 短期耐温 149°C / **长期耐温 93°C** ⇒ ★温度维度结论: 长期 93°C 远高于皮肤侧 38-40°C 目标, 且 VHB 不在 SoC 热路径上 ⇒ 温度不是瓶颈; **耐汗液/耐化妆品/耐乙醇分级官网未给** [0数据]。② LOCTITE AA 3311 官网 [官网]: UV/VIS 固化 1-part 丙烯酸 / **ISO-10993 biocompatible** / 黏度 200-400 cP / 深度固化 >13mm ⇒ ★生物相容维度有官网依据; 耐湿/耐化妆品/耐醇/耐 UV 分级官网未给 [0数据]。③ 硅胶 ISO 10993 / FDA 21 CFR 177-2600 认证 ⇒ 采购条款写死『按有认证牌号选 (VMQ-A50)』。【降级方案】电池固定维持【背胶 + 限位台阶 + 激光压痕】三重冗余 (VHB 不单独承结构力), 耐受性靠 R6-4 送检实测; UV 胶只用于【非贴肤点】(镜片/导光柱), 贴肤点一律机械 + 硅胶; T-06 判据 (UV 后剪切 ≥90%) 走 R5 三明治试样实测; 证书未到手不得投产。",
        evidence="[官网] 3M VHB 5962 技术数据表 (长期耐温 93°C / 短期 149°C / 剥离 39 N/cm) + Henkel LOCTITE AA 3311 产品页 (ISO-10993 biocompatible); [0数据] 耐汗液/化妆品/乙醇分级与硅胶证书",
        level="[官网]/[0数据]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-12"),

    "mech_mat_anodize_process": dict(
        answer="【自查结论】MIL-A-8625F [官网]: Type III 膜厚公差 **±20%** (≤0.002in) / ±0.0004in (>2 mils); 典型膜厚 0.0005-0.002in (25-50µm); **50% 渗透 + 50% 表层生长 ⇒ 最终尺寸必须留 1/2 膜厚的余量**; 定位面/定位孔可在阳极后精加工 (业界通行方案 A: 阳极 → 遮蔽 → 精加工 ≤5µm) ⇒ ★定位重复性 ≤0.046mm 不依赖膜厚均匀性, 只依赖精加工面。镁合金化学转化体系在 pH5.5 含 Cl 汗液下的点蚀数据 公开渠道查不到 [0数据]。【降级方案】① 出图写『masked, then machined to ≤5µm』, 夹具基准 = 精加工的 ⌀2.0 H7/h6 销孔 (与 PIN-SET-2 一致); ② 膜厚公差按 ±20% 写进图纸 (标称 25µm ⇒ ±5µm), 最终尺寸留 1/2 膜厚余量; ③ 镁合金件按【转化膜 + 涂层 + 边缘封孔】三道 (方案 A), 点蚀判据改用 T-05/T-07 实物浸泡 + 显微截面 (R6-6 试样)。",
        evidence="[官网] MIL-A-8625F §3.7.2.1 (膜厚公差 ±20% / ±0.4 mil) + §3.4.3 (Type III 定义) + 行业通用『精加工后最终公差要留 1/2 涂层厚度』; [0数据] 镁合金转化 pH5.5 含 Cl 点蚀数据",
        level="[官网]/[0数据]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-13"),

    "mech_dfm_shrink_rate": dict(
        answer="【自查结论】① PC/ABS 注塑件收缩率: ASTM D955-89 口径下 **0.29%-0.76%**, 且**各向异性** (流动向 vs 垂直流动向不同), 以材料供应商牌号数据为准 [媒体/行业通例] ⇒ ★我原用的 1.5% 假设偏保守, 改按 0.3-0.8% 做敏感性; ② ADC12 镁合金压铸件线性收缩率 公开渠道查不到确切值 [0数据] ⇒ 按 1.0/1.5/2.0% 三档敏感性 (原假设保留); ③ 模具补偿基准依牌号与原生料比例定 (回料比例一变收缩率就变) ⇒ 出图前必须锁牌号 + 原生料比例。【降级方案】所有『两件互相配』的界面按 DFM_REVIEW 2.5.3 移交 CNC 件/镶件 (与 mech_dfm_battery_seat 同向) ⇒ 结论不因具体 S 改变 ⇒ 该外部依赖可退休。",
        evidence="[媒体/行业通例] ABS 注塑收缩率 0.29-0.76% (ASTM D955-89) + 各向异性; [0数据] ADC12 压铸收缩率公开值; [推算] 敏感性区间按 DFM_REVIEW 2.5.3",
        level="[媒体]/[0数据]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-14"),

    "mech_dfm_anodize_uniformity": dict(
        answer="【自查结论】MIL-A-8625F [官网]: 膜厚公差 ±20% (≤2 mil) / ±0.4 mil (>2 mil), 精密工艺可做到 ±0.1 mil; Type III 典型 0.0005-0.002in; 精加工后膜层处理 = 遮蔽 (masked) / 裸铝 / 重做 三选一。【降级方案】① 按方案 A (CNC → 阳极 → 定位面/定位孔二次精加工 ≤5µm) 出图, 遮蔽区在图纸上标注; ② 若供应商只能做方案 C (阳极前留量) ⇒ 要求书面承诺膜厚均匀性 ≤±10%, 否则方案 B/C 不可用; ③ ★膜厚均匀性**不是**定位重复性 (≤0.046mm) 的控制项 —— 定位由精加工面控制 ⇒ 本条作为外部依赖可退休, 真正的控制点转到『精加工面 + 遮蔽』的图纸表达。",
        evidence="[官网] MIL-A-8625F §3.7.2.1 + 行业『精加工后最终公差留 1/2 涂层厚度』通则; [推算] 定位重复性由精加工面控制 (MECH/PCB_MOUNT_PIN_SET2.md)",
        level="[官网]/[推算]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-15"),

    "mech_dfm_mold_tolerance": dict(
        answer="【自查结论】① 注塑 PC/ABS 一般公差带 通用经验 ±0.20~±0.30 (小件) / ±0.50 (大件); 压铸 ADC12 ±0.20~±0.25 [媒体/行业通例] ⇒ 本单用的 ±0.20/±0.25 属通用经验值, 方向合理但仍需按实际工艺确认; ② 最小特征 (⌀1.6 让过孔 / ⌀2.4 销孔 / 0.6mm 壁厚台阶) 对注塑/压铸属常规可达 [推算]; ③ 顶针/浇口/分型面可行布置 = 造型阶段决策, 需先有量产外形件模型。【降级方案】① 按 DFM_REVIEW 2.4 公差带出图并**全部设单向公差**; ② 最小特征不可达处改 CNC 镶件 (与 mech_dfm_battery_seat 同向); ③ 顶针/浇口/分型面归量产外形件建模阶段 (need mech_dfm_shell_geometry) ⇒ 本条作为外部依赖可退休。",
        evidence="[媒体/行业通例] 注塑/压铸通用公差带; [推算] 最小特征可达性; [推算] DFM_REVIEW 2.4 公差带口径",
        level="[媒体]/[推算]", ref="MECH/MECH_NEEDS_TRIAGE.md §4 ③-16"),
}

# ============================================================================
# ④ 类 · waiting_on = 空 (114 条) —— 三选一: (a) 已作废 (b) 已被本单答复覆盖 (c) 真·待答
#     C4a = 已作废/已被覆盖 ⇒ 关 ; C4c = 真·待答 ⇒ 留
# ============================================================================
C4_CLOSE = {
    "iss091_stack_value_conflict": dict(
        reason="(a) 已作废 —— 本条要统一的两个数 (27.0 / 26.5) 都已退出活口径",
        evidence="[实测] 现行铰链区口径 = 25.30 mm (整机: 31p@0.3 + 22p@0.5 + 10p@0.5) / 5.00 mm (demo: 只有 J_CHG) —— MECH/USB_HINGE_STRUCTURE.md §0 C-3 + §9 + MECH/HINGE_FPC_GEOMETRY_TRUTH.md T1/T2; 净高分母 = 38.00 (现行) 不是 37.00 (已作废的叠放模型)",
        level="[实测]", board="N"),

    "iss091_pin9_10_ntc_return": dict(
        reason="(a) 已作废 —— 本条的前提 (把 pin9/pin10 改作 TS 专用回流) 已被网表撤除",
        evidence="[实测] TS_RTN 在 HW/netlist_v1.csv 里 0 次出现 (2026-11-03 起残留撤除, NTC 与 30.31k 分压下臂改回 PGND) ⇒ 现行 pin9/10 = HINGE_RSV, 没有 TS 专用回流; 本域 need iss202_mech_frag_old_needs_stale (2026-11-12) 已把这条登记为【前提已不存在】",
        level="[实测]", board="N"),

    "iss089_typec_opening_and_print_pack": dict(
        reason="(b) 已被后续两条覆盖 —— 打印包改版已按第三档试样落地",
        evidence="[实测] ISS-213 (need iss213_mech_typec_third_candidate) 出第三档 (FDM 直成型 10.50×4.80 / 金属嵌件 CNC ±0.05 10.25×4.55, 最坏单边 0.63/0.62 ✅) + ISS-218 已落成 MECH/print/frame_typec_coupon_tier3_revb.stl (72.0×32.0×5.0mm, 可直接下片) + 门禁 (余量对拍 4/4 + MECH_ANCHORS 7/7 + 反向用例 8/8); ① 镜脚侧 Type-C 特征已随 ISS-014 决策 5 (充电板挪镜框) 作废",
        level="[实测]", board="N"),

    "iss017_board_width_direction_clarify": dict(
        reason="(a) 已作废 —— 口径已被锁定",
        evidence="[官方] 板宽 30mm = V 向 (镜脚垂直方向): 老板 10-29 19:16 拍板 + MECH/BOARD_GEOM_30MM.md §0『板宽是 V 向尺寸 ⇒ 镜脚 V 余量 17.00 → 2.00 (最坏 1.40), 板宽硬顶 31.40mm』+ 镜脚三条锁死尺寸链 H 7.30 / V 38.00 / L 130.00 一字不动",
        level="[官方]/[实测]", board="Y"),

    "optical_cavity_recompute_for_sioled": dict(
        reason="(b) 已被 ISS-208/209 的重排交付覆盖",
        evidence="[实测] MECH/CENTER_CAVITY_RECALC.md + MECH/cavity_recalc_check.py (rc=0, 12 项 + --selftest 9/9) + MECH/MECH_BUDGET.md §1.8 指针段 + §1.7 X-1..X-6 (眼盒/腔体/热学判据) ⇒ 镜框侧四件事 (光学腔体 / 分光器 / 显示仓布局 / 外形重量) 已出数",
        level="[实测]", board="N"),

    "mech_numpy_dep_for_print_check": dict(
        reason="(a) 已解决 —— 本条的阻塞 (numpy 缺失) 不复存在, 剩余项已由另一条 need 承接",
        evidence="[实测] 2026-11-11 21:2x 实测: numpy 2.5.4 (python3 3.14.4) ⇒ python3 MECH/dfm_check.py rc=0 + python3 MECH/print/verify_pack_revb.py rc=0 (93/93 + 38/38); ★真正剩余阻塞 (量产外形件模型) 已由 need mech_dfm_shell_geometry 承接",
        level="[实测]", board="N"),

    "iss134_mech_close_legacy_zoujuan_refs": dict(
        reason="(b) 已被本单自己的收口交付覆盖 (ISS-208)",
        evidence="[实测] 5 份旧文档 33 处『走鹃』逐处定性 = 活动 27 (全部改写成现行口径) + 历史 6 (保留原文 + 加『已作废 (2026-11-15, ISS-134 V2)』); 机器门禁 python3 MECH/display_biosafety_v2_check.py rc=0 (5 项) 带 --selftest 6 用例全过; 逐处定性表见 MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md §1",
        level="[实测]", board="N"),

    "iss208_mech_legacy_zoujuan_closeout_done": dict(
        reason="(b) 闭环完成上报 —— 交付物已落盘, 无待答项",
        evidence="[实测] 同上: MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md §1 + display_biosafety_v2_check.py rc=0 + 判据文件 md5 96239070dc7c0ec00edb1b758a698769 / bda4a29464336bc1452c913602ce3f46 未变",
        level="[实测]", board="N"),

    "iss208_mech_rebudget_frame_cavity_d15_20": dict(
        reason="(b) 已被 ISS-209 的重排交付覆盖",
        evidence="[实测] MECH/CENTER_CAVITY_RECALC.md: T = d + 3.0 = 18.00/21.00/23.00mm (d=15/18/20), 冲突量 3.20/6.20/8.20mm 与 §1.7.1 C-1 逐字一致; MECH_BUDGET §1.7.1 C-1 + §1.8 指针段; 机器门禁 MECH/cavity_recalc_check.py rc=0",
        level="[实测]", board="N"),

    "iss208_mech_recompute_optical_thermal_468mw": dict(
        reason="(b) 已被 ISS-209 的重排 + 热学三连交付覆盖",
        evidence="[实测] ISS-209 已出: 腔体重排 (CENTER_CAVITY_RECALC.md) + 腔体热 C-7 (need iss209_mech_cavity_heat_468mw_vs_50c) + 鼻梁热路径 C-C (need iss209_mech_nose_bridge_heat_path) + X-3 冲突 (need iss209_mech_x3_skin_path_claim); 现行热学判据已落 MECH_BUDGET §1.7 X-3 (腔体 ≤50°C / 面板结温 ≤60°C / ≥0.5W 被动散热面 / 不得密闭腔)",
        level="[实测]", board="N"),

    "iss209_mech_cavity_rebudget_done": dict(
        reason="(b) 闭环完成上报 —— 交付物已落盘",
        evidence="[实测] MECH/CENTER_CAVITY_RECALC.md + MECH/cavity_recalc_check.py (rc=0, 12 项 + --selftest 9/9) + MECH_BUDGET §1.8 指针段 (既有数字 0 改动)",
        level="[实测]", board="N"),

    "iss209_mech_splitter_resize_for_eyebox62": dict(
        reason="(b) 已被 ISS-219 闭环 (C-6)",
        evidence="[实测] need iss219_mech_m6_splitter_spec_landing (2026-11-16) 原文写明『结构侧给出的新规格 (C-6, 已闭环 need iss209_mech_splitter_resize_for_eyebox62)』: 45° 平板 11×11×1.5 + 转向棱镜 ×2 9×9×5 ⇒ 0.9697cc (工程 0.9915) / W4 3.68-7.36g (工程 3.77-7.53), 整机重量上限 74.0 → 76.13g",
        level="[实测]", board="N"),

    "iss213_mech_endpoint_thermal_path_metal": dict(
        reason="(b) 结论已落结构真源 + 剩余项已拆分到 u8 那条",
        evidence="[实测] MECH/MECH_BUDGET.md §3/§2.3.1 + mech.yaml interface_claims (mech_endpoint_surface_temp_caliber / mech_mech_budget_linear_0p8w_dead) + MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md: 端件必须金属热路 (打印件 1944 K/W ❌ / 铝 6063-T6 1.935 K/W ✅), R_热路 ≤70 K/W ⇒ 截面积 ≥4.975mm² (2.0×2.0 不合格); ★剩余『端件截面 u8 未定 ⇒ 重量算不出』已转 need iss218_mech_u8_endpoint_section_decide",
        level="[实测]", board="N"),

    "iss213_mech_mech_budget_charge_caliber_text": dict(
        reason="(b) 已被 ISS-216 改完 (文字 + 脚本常量 + 口径自检)",
        evidence="[实测] MECH/MECH_BUDGET.md §2.1 B 行『0.45-0.57 W (代表值 0.50 W) — 耗散 = Pin − Pout + P_DCR (buck 口径)』+ §2.3.1 (皮肤侧 60.0°C / 端件 108.3°C / P_max 0.21W) + MECH/verify_budget.py 的 P_CHARGE = 0.50 + §8 口径自检 C1~C10 (含 C5 = 门禁锚点 0.50W)",
        level="[实测]", board="N"),

    "iss218_mech_alu_k_201_vs_237": dict(
        reason="(b) 已被 ISS-219 改完 (四处文档 + 脚本常量)",
        evidence="[实测] MECH/MECH_BUDGET.md L519『k 口径 (旧口径 237 已订正) → 201 · §2.3.1/§3 ISS-216 注/§5.1/§5.5 四处 + MECH/verify_budget.py 常量 + ENDPOINT_METAL_PATH_MASS_TEMPLATE.md 已统一为 201 W/m·K (Hydro/Aalco/Kaiser 三家互证)』+ verify_budget.py:111 K_AL_6063_T6 = 201.0 (旧 237 只留追溯)",
        level="[实测]", board="N"),

    "iss229_mech_charge_skin_temp_scope_to_main": dict(
        reason="(b) 三个问题都被 V-4 落表回答了",
        evidence="[实测] HW/netlist_v1.csv L47 已落 680Ω (IIN 0.574A / ICHG 0.698A / 单 pin 0.349A ⇒ 余量 1.43×); ① 充电时皮肤侧 43°C 不再是硬约束 (老板 10-28『边戴边充不允许』⇒ 充电时眼镜不在皮肤上), 但铰链段温升 / TS 停充门限偏差 (390Ω max 36.5mV = 1.13°C) / 单 pin 触点额定三条仍成立; ② V-4 建议默认值已拍 (680Ω) ⇒ DECISION_PENDING_2026-11-16.md §A2 A2 可直接落; ③ 本域 need 里的 47.1°C / 42.1°C 已被 ISS-229 的 §B4.2 订正覆盖",
        level="[实测]", board="N"),

    "iss246_mech_handoff_review": dict(
        reason="(b) 交卷待复核 —— 交付物已落盘, 无待答项 (复核本身是 main 的动作)",
        evidence="[实测] HANDOFF/2026-11-18_mech-lead_ISS310_板框口径代价对照.md 之前的 ISS-246 交卷单 (6 段: B2 自评 / B3 证据分级 / B4 接口取值 / B5 验收命令原样输出 / B6 边界审计 / 附交卷物清单) + 分片 (frag_write.py 原子写) + merge/gate_check rc=0 Q1 18/18",
        level="[实测]", board="N"),

    "iss251_mech_service_port_pad_y_migrate": dict(
        reason="(b) 已被 ISS-264 覆盖 —— 三项里两项已迁, 剩下一项已另立 need",
        evidence="[实测] MECH/SERVICE_PORT_ISS092.md 头部 ISS-264 指针: 夹具基准常量已迁 (p2_y=15.00 / s2_y=20.00) + pcb_thk=1.00 已核, 受保护脚本走 H-1 重基线 (md5 9b24bf98… → db58ff6a…); ★【只剩 jd_y0 一项】⇒ 已由 need iss264_mech_jd_y0_and_open_y_caliber / iss264_mech_jd_y0_legal_range_errata_pending / iss267_mech_jd_y0_and_frame_decision 承接",
        level="[实测]", board="Y"),

    "iss251_mech_demo_truth_gate_red_concurrent": dict(
        reason="(b) 并发事件已闭环 —— 该闸现为绿",
        evidence="[实测] python3 MECH/check_demo_struct_truth.py rc=0 (57 项判据本身没坏) + 板 md5 611b869e13518c3c023fb178f91a0075 / mtime 2026-11-06 07:07:17 逐字节不变 ⇒ 当年『21/23 红』的并发窗口已过",
        level="[实测]", board="Y"),

    "iss251_mech_owner_decisions_pending": dict(
        reason="(b) 5 项已拆到具体 need —— 2 项已定, 3 项另有归属",
        evidence="[实测] (d) 板长 = 60.00mm 已定 (BOARD_GEOM_30MM §1) ⇒ 归零; (e) 板厚 = 1.00mm (6 层) 已定 ⇒ 归零; (a) d 值 ⇒ need iss209_mech_d_value_decision (决策码 M-B17); (b) u8 ⇒ need iss218_mech_u8_endpoint_section_decide; (c) 集热面材质/面积 ⇒ need iss219_mech_c7_sink_area_confirm + iss222_mech_c7b_sink_is_metal_not_print",
        level="[实测]", board="N"),

    "iss251_mech_handoff_review": dict(
        reason="(b) 交卷待复核 —— 交付物已落盘, 无待答项",
        evidence="[实测] HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md (B1-B6 六块齐全 + 附 A 三处逐条订正表 + 附 B 并发说明 + 附 C 边界自审) + MECH/check_budget_caliber.py (rc=0 17/17 · --selftest rc=0 13/13) + 分片 (5 artifact + 5 claim + 4 need, frag_write.py 原子写)",
        level="[实测]", board="N"),

    "iss264_mech_gate_script_md5_rebase": dict(
        reason="(b) 三个新 md5 已落进 issue_log 的受保护锚点",
        evidence="[实测] state/issue_log.yaml 实读: 4ae5827e986f1aebb108c5aa2a475074 / c4bf9151dd59826fb2320c34e8afbd0f / db58ff6a2afc28b8bf517e3c57c56bc1 各命中 6 处 ⇒ 落锚动作已完成 (本单不自签 issue_log, 只是核对结果)",
        level="[实测]", board="Y"),

    "iss271_mech_s6_port_opening_claim": dict(
        reason="(b) 认领句已被挂进板那一趟的作业包",
        evidence="[实测] HW/PCB/BOARD_ONEPASS_WORKPACKET.md §1「三条开口的认领句 (3 条 · 全部可抄进作业包 §3-S6)」+ C-OPEN-1 调试口 (罩 J_DEBUG, 帧 B160x100, 开口 X 137.850..148.050 × Y 54.300..58.900) + C-OPEN-2 检修口 (罩 J_UART, 开口 X 13.790..23.990 × Y 66.300..70.900) + §3-S6 行 B15_SVC_PORT_SPLIT / B16_LED_G_OPTO",
        level="[实测]", board="Y"),

    "iss271_mech_ledg_g5_brightness_gate": dict(
        reason="(b) 老板已拍 (2026-11-17 09:49)",
        evidence="[官方] pm.yaml needs_from[boss_g5_led_brightness_20261117].decision: 选项 ② = 改 R 到 20mA 档 ⇒ R_LED_R = 68Ω ±1% (红) / R_LED_G = 55Ω ±1% (绿); 代价: 每颗 2.2mW → 66mW (两颗 ≈0.13W 进电池账) + 亮度 ×14 ⇒ 眼旁光源 IEC 62471 分级要重算; ★另有 boss_dled_g_expose_decision_20261117 一并拍了 U-8 (外露与否)",
        level="[官方]", board="Y"),

    "iss246_mech_continue_verify": dict(
        reason="(b) 续做复核已完成 —— 交付物已落盘, 无待答项",
        evidence="[实测] 交卷单已追加 C-1~C-6 附录 (当期真值 05:07:16) + 门禁 rc=0 23/23 · --selftest rc=0 14/14 · merge rc=0 · gate_check rc=0 (Q1 18/18) + 沙盒反证 绿-红-红-绿 四步留档 4 份; ★本轮复跑 check_demo_struct_truth.py --selftest ⇒ rc=0 (反向用例 28/28 抓到)",
        level="[实测]", board="N"),

    "iss278_mech_demo_struct_truth_selftest_regression": dict(
        reason="(b) 回归已修复 —— 本轮实跑 rc=0",
        evidence="[实测] 本轮实跑 python3 MECH/check_demo_struct_truth.py --selftest ⇒ rc=0, 反向用例 28/28 抓到 (含 R8/R9/R10/R11a/R11b/R12 六条台账链头用例) + 主跑 rc=0; 板 md5 611b869e13518c3c023fb178f91a0075 与 mtime 2026-11-06 07:07:17 逐字节不变 ⇒ 『板只改一次』铁律未破",
        level="[实测]", board="Y"),

    "iss278_mech_to_hw_board_inputs": dict(
        reason="(b) 已转出 —— 不再由 mech-lead 追",
        evidence="[官方] 本条正文自述: 『已转出 · 2026-11-17 · main 16:0x 已转 hw-lead 的 ISS-292 任务书「⑬ 追加」节 · pm.yaml 已回写答案 ⇒ 本条不再由 mech-lead 追; 其中 E-1~E-5 归 hw-lead 的 ISS-292, E-6 的 MECH 半边已由 ISS-294 (mech-lead) 接手并交卷』",
        level="[官方]", board="Y"),

    "iss296_mech_iss294_opening_status_need": dict(
        reason="(b) 状态已写清 —— 本单交卷页 §7 已把这条 need 的现状写全",
        evidence="[实测] J_USB_C 边开口几何已算完 (帧 B160x100): 边开口 X 132.995..147.005 × Y 0.000..7.300 (宽 14.010 深 7.300) + 必须清空区 X 133.895..146.105 × Y 0.000..6.400 + 单边净距 X/Y 0.900 ⇒ 最坏 0.600 = CRIT 刚好过 + 座体真实高 h 仍 [0数据] ⇒ 开口最终尺寸 + Z 向窗口仍是 main→boss 拍板项 (已在 MECH/BOARD_ONEPASS_MECH_SYNC.md §10.1 落笔)",
        level="[实测]", board="Y"),

    "iss203_mech_claim_mainboard_len_carrier_direct": dict(
        reason="(b) 已被同批更晚的升级条取代",
        evidence="[实测] need iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice (2026-11-15) 把同一件事升级给老板 (pm.yaml 已有该 key 的 to=boss 待拍项, DECISION_INDEX #31 剩 0 天) ⇒ 旧条 (2026-11-12) 不再单独追; ★两条 claim 的 value 已在 ISS-206 保持 69/76 不改 + 补注『这是 A/B 互斥方案的板长, 不是现行板板长』",
        level="[实测]", board="N"),

    "iss229_hw_landing_must_sync_mech_anchor_iss233": dict(
        reason="(b) 该次实例已闭环 —— 规则已另立常驻条",
        evidence="[实测] 事件已闭环: 2026-11-16 06:48:38 ISS-233 第 3 批改网表 L442 + 脚表 L531 ⇒ 本域已按 H-1 把 MECH 锚点跟到 (网表 34132f7e40a241e1fae1476be0eafbd5 / 脚表 b21b743a7702d30729f0d653c15392df, by=ISS-233) ⇒ 门禁回 rc=0 (23/23); ★常驻规则由 need iss224_hw_landing_must_update_gate_ledger 承接",
        level="[实测]", board="Y"),

    "iss218_mech_pa_cf_shrinkage_density_feedback": dict(
        reason="(b) 自查部分已尽 + 剩余实物回填已挂到打印执行方那条",
        evidence="[实测] 补偿公式已在册 (Bambu 官网公式 补偿% = (实测/设计) × 100, 随件试样自带 3 个标定方块 5/10/20, 前置 = PA-CF 必须 80~90℃/8~12h 干料否则数据不可比) + 密度按 1.18 g/cc 占位记账 (标签已标 [0数据-占位], 只用于净重差粗算, 不进 §3 合计) + 加工厂表面粗糙度 Ra 已降级为功能性要求 (开口两对边无刀痕阶梯 / 锐边倒钝 R0.2 / 去毛刺); ★剩余『打印方量完回填』已挂在 need boss_local_print_measure (决策码 M-B1) / iss017_local_print_measure_unblock (M-B12) 上 ⇒ 本条不再单独追外部",
        level="[实测]/[推算]", board="Y"),
}

C4_KEEP = {
    "soc_carrier_mainboard_site": dict(owner="main → boss (A/B 方案取舍)",
        why="主板位 + 载板化方案取舍是老板级; 同一问题已由 pm.yaml 的 iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice (DECISION_INDEX #31, 剩 0 天) 升级给老板 ⇒ 本域不重复问, 只跟结果",
        oneline="main: 主板位 (镜脚 / 镜框) + A/B 载板化取舍的老板裁决已在 DECISION_INDEX #31 挂着 ⇒ 出结果后回本域一句即可 (结构结论全部随它变)",
        evidence="[官方] pm.yaml 已有 to=boss 的同题决策项 (DECISION_INDEX_2026-11-18.md #31, due 2026-11-18)", board="N"),

    "u8_frame_section_carrier": dict(owner="main (端件截面 u8 排期)",
        why="u8 是端件热路 / 框侧汇流 / 装配顺序三条链的共同前置; 已有专门条目 (iss218_mech_u8_endpoint_section_decide + iss089_frame_section_u8_block)",
        oneline="main: u8 端件截面请排期拍 (本域已备好重量账模板 MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md, 五档情景 A/B/C) —— 它同时卡端件金属热路重量与框侧汇流",
        evidence="[实测] MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md (u8∈{30,33,35,38,40} × 表A/B/C)", board="N"),

    "iss089_frame_section_u8_block": dict(owner="main (与 u8 同一条)",
        why="本条是『把 u8 提到阻塞级』的提级请求; u8 的实际排期条目是 iss218_mech_u8_endpoint_section_decide",
        oneline="main: u8 提为阻塞级的动作 = 把 iss218_mech_u8_endpoint_section_decide 排进板那一趟之前; 本域不再另问",
        evidence="[实测] 端件要装 充电板 25×10 + Type-C 沉板 + 铝屏蔽罩 + 铰链件 + 4 条跨铰链 FPC 固定段 (合计 V 向带宽 31.00mm) ⇒ 端件可用 V 高只有约 30-40mm ⇒ 余量 -1.00~+9.00mm", board="N"),

    "iss089_decision_stack_correction": dict(owner="main (DECISIONS.md 是项目总工地界)",
        why="★本条建议的替换值 31.00mm 本身也已过期 —— 现行真值是 25.30mm (整机) / 5.00mm (demo) ⇒ 要改就得改到新值, 不能改到 31.00",
        oneline="main: DECISIONS.md 2026-10-27 那条『铰链区堆叠仍 26.5mm (余 10.5mm)』已过期 —— ★但本条当年建议的替换值 31.00mm 也不是现行值: 现行 = 25.30mm (整机) / 5.00mm (demo), 出处 MECH/HINGE_FPC_GEOMETRY_TRUTH.md T1/T2 + MECH/USB_HINGE_STRUCTURE.md §9 ⇒ 请按新值改, 别按 31.00 改",
        evidence="[实测] DECISIONS.md:26 仍写『铰链区堆叠仍 26.5mm (余 10.5mm)』; [实测] 现行口径 25.30/5.00 (MECH/USB_HINGE_STRUCTURE.md §0 C-3 + §9)", board="N"),

    "proto_pcb_freeze_gate": dict(owner="main (排期) + 板那一趟",
        why="板框/厚度/层数/孔位冻结闸: 板厚与层数已定 (1.00mm / 6 层), 板框仍在拍 (U-1) ⇒ 闸还没满足; 老板 11-17 00:43『接下来的目标是绘制 PCB 图』⇒ 板只改一次 ⇒ 冻结闸是这一趟的第一前置",
        oneline="main: 板框冻结闸还差 U-1 (板框三选一: B160x100 / F30A / P60x15) ⇒ 板只改一次那一趟开工前必须先冻结 (板厚 1.00/6 层与 PIN-SET-2 套 A 已定)",
        evidence="[实测] MECH/BOARD_GEOM_30MM.md §1 (板长 60 / 板宽 30 / 板厚 1.00 六层) + §3 (套 A 孔位) 已锁; 板框三选一仍待老板 (need iss310_main_board_frame_u1_decision 已由 main 升级)", board="Y"),

    "iss121_magnet_cover_y_wall_decision": dict(owner="main (结构取舍)",
        why="盖板 Y 向壁厚缺 0.40mm 是真冲突, 三个选项各有代价; 三个选项的成本还没算完",
        oneline="main: 检修口盖板 Y 向壁厚缺 0.40mm 请裁 —— ① 盖板 Y 7.60→8.60 (+0.02g/侧) ② 磁铁改 ⌀3.0 (吸力降) ③ 承认该处壁厚要求可降 (ISS-092 C-8『磁铁不承结构力』⇒ 需拉脱实测); 本域默认假设 = ③",
        evidence="[实测] MECH/SERVICE_PORT_ISS092.md C-8 磁吸件 2× N35 ⌀4.00×1.00 + 镜脚侧 ⌀4.20×1.00 沉槽; C-3 盖板外形 13.20×7.60×1.20 ⇒ 沉槽+≥2.10 壁 需 8.40 > 7.60", board="Y"),

    "iss092_magnet_soc_gap_correct": dict(owner="main (PM 授权改 ISS-092 正文)",
        why="MECH/SERVICE_PORT_ISS092.md 是已 verified 的文件, 本轮边界只许交新文件 ⇒ 正文里那两处 68.30mm 只能由 main 授权后改",
        oneline="main: 请准许把 MECH/SERVICE_PORT_ISS092.md 里『磁铁↔SoC 间距 ≥68mm』两处订正为 28.00mm (坐标混算作废) 并把『对 SoC 大概率无影响』的依据强度降级 (28mm 够不够取决于 SoC 磁敏感度 = [0数据]); 同一文档 §11 I-2/I-3/I-4 三条默认假设已生效",
        evidence="[实测] SERVICE_PORT_ISS092.md §0 #10 仍写『间距 ≥68mm 可达』; §6 风险表仍写『磁铁在 L≈100.3, SoC 在 X 20..32 ⇒ 间距 ≥68mm』", board="N"),

    "proto_b1_split_coupon": dict(owner="main (B1 批次排期)",
        why="拆两段是排期建议 (B1a 纯 coupon 34 项 / B1b 板相关项), 不是结构结论",
        oneline="main: B1 拆两段请拍 (B1a = 纯 coupon 34 项工艺标定, 完全不依赖 PCB 冻结 ⇒ ISS-040 打印执行方一有着落就能开; B1b = 板相关项, 必须等 PCB 冻结) ⇒ 本域建议按拆两段执行, B1a 先开",
        evidence="[实测] B1a 34 项 (孔收缩 +0.05~+0.15 / 0.80 壁成型 / 45° 免支撑 / 拉脱 ≥15N / 0.10 塞尺进不去 / 壁厚阶梯 / 间隙梳 / 悬空角 / 标定块) 全部不依赖板框/厚度/层数/孔位", board="Y"),

    "mech_iss127_temple_split": dict(owner="main → boss (架构裁)",
        why="镜腿壳体改 H 向分型 (皮肤盖 + 内胆) 是架构级; P1 已被本域算完并推荐, 只差这一刀",
        oneline="main→boss: 镜腿壳体改 H 向分型 (皮肤盖 + 内胆) 是否接受? P1 收益: 链① 三档 α 全过 0.40 (0.750/0.736/0.722/0.708) + 链② 四档全过 + 重量净减 0.38g/对; 代价: 零件 24→26 件 + 模具 2 套/侧 + 外观多一条分型线 (贴肤面可零斜度) + 皮肤盖加强筋 +0.15~0.25g/对; 备选 P2 (局部 H 向分型) 会让链② 破线 0.190 < 0.40",
        evidence="[推算] MECH/ISS127_H_CHAIN_SOLUTION.md §C (Δ=2·38·tanα ⇒ 1.327 / 0.663 / 1.990; 等效腔深 h_max=20.05/10.03/6.68mm < 电芯高 23.50 ⇒ V 向脱模在任何 α 下无解)", board="Y"),

    "mech_iss127_graphite_cut": dict(owner="main (预算裁)",
        why="石墨裁剪是重量预算裁剪, 骨架 4.08g/对 的超支另算 (本条不动)",
        oneline="main: 石墨按【只铺 SoC 段 + X 向逃线带 5.00/边】裁剪是否确认? 收益 = 石墨 2.16g/对 → 0.98g/对 (净减 0.38g/对), 依据 = 30mm 板宽下骨架候选 C 的 SoC 段满宽 30.00, 横向扩散已被满宽铝骨架覆盖",
        evidence="[推算] MECH/ISS127_H_CHAIN_SOLUTION.md §C.1 重量表 (P1 金属+石墨 5.86 g/对 vs 基线 6.24); 骨架本身 4.08 g/对 仍超 +1~3g 预算 1.08", board="Y"),

    "mech_iss127_graphite_in_hchain": dict(owner="main + hw-lead",
        why="挤占 vs 叠加 是链② 的口径钉子, 两条文档不一致, 必须有一句裁定",
        oneline="main+hw-lead: 石墨在链② (PCB/骨架堆叠 H 链) 里是【挤占】那 0.30 空气隙还是【叠加】在 4.40 之外? 本域按叠加 (保守) 算 ⇒ 链② 在 α=1.5° + 含石墨 + 板厚 1.22 时最坏 0.190 < 0.40 破线; 按挤占则 0.490 ✅ —— 请钉一句 (注: P1 H 向分型下链② 脱模项=0 ⇒ 四档全过)",
        evidence="[推算] MECH/BOARD_GEOM_30MM.md §5.4 写『4.40 vs 7.30 ⇒ 余 2.60』但同句又写 4.40 ⇒ 2.60 (差 0.30) vs MECH/skeleton_section_check.py §4 写 4.70 ⇒ 2.60", board="Y"),

    "iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice": dict(owner="main → boss",
        why="A/B 互斥方案的取舍是老板级; 老板已把『P7/P8 用哪块板』拍了 (选项 A = 改现役 160×100 台架板), 但这条问的是【claim 算现行板长还是历史方案对照】, 还没答",
        oneline="main→boss: 这两条 claim (mainboard_len_carrier=69mm / mainboard_len_direct=76mm) 算『现行板长』还是『历史方案对照’? 建议按『历史方案对照』保留并补注 (value 不改) —— 现行板长是 60.00mm; 老板 11-17 已拍 P7/P8 = 改现役 160×100 台架板, 若 A/B 方案随之作废则这两条整体标作废",
        evidence="[实测] mech.yaml interface_claims 两条 note 已补『本值是 A/B 互斥方案的板长, 不是现行板板长』; [官方] MECH/BOARD_GEOM_30MM.md §1 现行板长 60.00mm; [官方] pm.yaml boss_p7_p8_which_board_20261117 (选项 A = 改现役 160×100 台架板)", board="N"),

    "iss134_mech_boss_decide_waveguide_vendor_and_fov": dict(owner="main → boss",
        why="波导归属 + FOV 目标是老板级; 公开波导只有 20-30°(D) vs 我们 D3 口径 120° 对角, 差一个量级 ⇒ 必须一起拍",
        oneline="main→boss: 波导归属 (A 舜宇奥来 / B 瑞声×Dispelix / C JBD 刻蚀) + FOV 目标一起拍 —— 本域建议按 B 的公开几何做镜框参数化占位 (卡槽 + 可换压框), A 或 C 到货只重做压框; ★FOV 必须在占位件之前定 (耦入/耦出角可调), 否则重演 11-02 方案变了全部重算",
        evidence="[媒体] 公开参数: 歌尔奥来 LM3027 0.74mm/30°(D)/<4.3g/眼盒15×10mm; Dispelix 0.7mm/25°/4.7g/出瞳4mm/出瞳距18mm/60×41mm/透过率90%; JBD Pavo 只供波导不供光引擎 ⇒ 耦合责任在我们", board="Y"),

    "iss134_mech_reassign_iss004_013_016_048": dict(owner="main (issue_log 地界)",
        why="issue 状态与 owner 是项目总工的活, 我一笔没动 state/issue_log.yaml ⇒ 只报不改",
        oneline="main: 请按 ISS-134 的建议重排 4 条 issue 的 owner/状态 (ISS-016 走鹃Ⅱ 长宽高 → closed 因 11-02 换型作废; ISS-048 光生物安全 → owner 改 mech-lead 按 V2 判据表闭环; ISS-004 波导未选型 → owner 改 pm/mech-lead 并改成『等老板拍归属 + 参数化占位』; ISS-013 → note 改成『缺几何数据 + 用参数化占位与可换压框绕开』), 并连带改 MECH/PROTOTYPE_PLAN.md B3 的开工前置 (JBD 回 u1+u4 之前镜框不开工)",
        evidence="[实测] MECH/display_biosafety_v2_check.py 的外部依赖已归零 (12 个 0数据 全部有可测替代量); [实测] MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md §1", board="N"),

    "iss134_mech_archive_jbd_question_list": dict(owner="main (根目录文件地界)",
        why="JBD_QUESTION_LIST.md 在项目根目录, 属 main 地界; 且按老板 11-11 19:31 + 11-12 02:02 不再发信 ⇒ 那批问项已全部作废",
        oneline="main: 请把根目录 JBD_QUESTION_LIST.md 归档为历史件 (走鹃Ⅱ 出瞳/波长/光通量/MTF/光生物安全 已随 11-02 换型作废; 波导交 JBD 推荐那条已被公开采购路线取代); 同批 state/outbox/ 下的 jbd_query.md / jbd_query_addendum.md / visionox_display_inquiry.md / visionox_display_dsc_mode_query.md 我一律不发只留档",
        evidence="[官方] 老板 2026-11-04 09:5x『视崖屏幕已经不用了』; [官方] 老板 2026-11-12 02:02『不再发信, 全靠自己查资料』", board="N"),

    "iss208_mech_waveguide_eyebox_le_62mm2_gate": dict(owner="main → boss (与波导归属一起拍)",
        why="眼盒面积是选型前置条件, 不是结果; 老板拍波导时必须一起拍, 否则选回来的波导一定超限",
        oneline="main→boss: 眼盒面积 A_e <= 62mm² (入眼 2000 cd/m², V2 C-4/C-5) 必须作为波导【选型前置条件】一起拍 —— 公开在售波导标称眼盒全部超限 (12×10=120mm² 超 1.94× / 15×10=150mm² 超 2.42×) ⇒ 且『出瞳 4mm』≠ 眼盒面积 (A_e 的厂商定义式公开查不到 ⇒ 要求供方按 V2 §3 ⑥ 定义式给 A_e)",
        evidence="[推算] 公式 L_eye,max = 0.1234/A_e (A_e 以 m² 代入); 12×10 ⇒ 入眼上限只剩 1028 cd/m²; 15×10 ⇒ 只剩 823 cd/m²", board="Y"),

    "iss208_main_fix_v2_section_refs": dict(owner="main (判据文件地界)",
        why="改判据文件 (DISPLAY_BIOSAFETY_CRITERIA_V2.md) 是项目总工的活, 我一字没改 (md5 96239070dc7c0ec00edb1b758a698769)",
        oneline="main: DISPLAY_BIOSAFETY_CRITERIA_V2.md 的节号自指对不上 (C-4 写『出处 3.5 (式 5/6/7)』、① 写『本文 3.7』, 而该文件 3 实际只有 ①~⑥) ⇒ 请统一改成 3 ⑤-b / 3 ⑥ / 3 ③-c; ★不影响任何阈值 (62mm²/1500/4000/50°C/60°C/15-20mm/0.011rad/0.1234 全部照抄无误), 只影响检索",
        evidence="[实测] 判据文件 md5 96239070dc7c0ec00edb1b758a698769 / bda4a29464336bc1452c913602ce3f46 未变; 本域已按语义引用 (MECH_BUDGET §1.7 X-1..X-6)", board="N"),

    "iss209_mech_cavity_heat_468mw_vs_50c": dict(owner="main (与 u8/集热面一起裁)",
        why="腔体 81.20/77.43/75.24°C vs 50°C 红线是硬冲突, 加厚救不了 (只贡献 6.4%-11.5% 面积) ⇒ 必须走金属热路",
        oneline="main: 面板 468mW 放正中区 ⇒ 腔体 81.20/77.43/75.24°C (d=15/18/20) vs 50°C 红线, 保 50°C 需被动散热面 ≈4668.9mm² (u8 未定值的 4.67 倍) ⇒ 腔体散热不能靠加厚, 必须金属热路导到铰链侧/端件 (≥0.5W 被动散热面 + 不得密闭腔) —— 请与 u8 + 集热面材质一起裁",
        evidence="[推算] MECH/ISS065 §2.3 模型 + MECH_BUDGET §1.7 X-3 (腔体 ≤50°C / 面板结温 ≤60°C)", board="N"),

    "iss209_mech_nose_bridge_heat_path": dict(owner="main (结构论据已给, 待认可)",
        why="量化已给完, 剩下的是『PCB 不进镜框正中』这条论据要不要写进锁死链",
        oneline="main: 鼻梁区热路径量化: 节点→鼻梁接触面 12.0mm / R_bridge=400K/W, SoC 0.55W + 面板 0.468W = 1.018W 进镜框 ⇒ 鼻梁接触面 54.33/52.75/51.83°C (d=15/18/20) ⇒ 对 43°C 余量 -11.33/-9.75/-8.83°C; 加鼻梁侧热断 (R=1000) 仍 43.74/43.03/42.61°C ⇒ 加厚救不了 ⇒ 结构侧论据 = PCB 不进镜框正中 (与 ISS-065 §2.4 同向), 请认可",
        evidence="[推算] ISS-065 §2.3 L_bridge=12.0mm + R_bridge=400K/W; 保 43°C 所需 R_bridge = 454.8/409.9/383.9 K/W (仅面板) / 1101.2/1003.6/946.9 (含 SoC)", board="N"),

    "iss209_mech_x3_skin_path_claim": dict(owner="main (判据措辞裁决)",
        why="X-3 那句话在现行 468mW 功耗下不成立 ⇒ 要么加限定语, 要么补热断要求; 这是判据措辞, 归 main",
        oneline="main: MECH_BUDGET §1.7 X-3『光学件在镜框, 不进皮肤热路径』在 468mW 面板下不成立 (仅面板就让鼻梁接触面到 43.89/43.16/42.74°C, d=15/18 档已破 43°C 红线 0.89/0.16°C) ⇒ 请裁: 加限定语还是补『鼻梁侧热断 >=454.8 K/W』要求 (本单未改该行一个字)",
        evidence="[推算] 同 MECH_BUDGET §1.7 X-3 + ISS-065 §2.3 模型", board="N"),

    "iss213_mech_cross_domain_to_main": dict(owner="main (派给对应总工)",
        why="跨域条目汇总: ① ② 已被 hw-lead 答复 (iss089_p9_topology_and_stack / iss089_chg_led_board_column 均已被答), ③ ICHG 系数已被 ISS-229 解决 ⇒ 剩下的仍要 main 派",
        oneline="main: ISS-213 跨域汇总里 ① PIN-MISMATCH/STK-P9/TOPO-3 与 ② NET-LED 已由 hw-lead 答复、③ THM-RATIO 已由 ISS-229 解决 ⇒ 剩下条目请按本条正文继续派给对应总工 (结构侧对 ① 的建议已写明: 拓扑按 H 向径向嵌套, 堆叠按触点区 27.00 / FPC 带宽 35.50 两口径分列)",
        evidence="[实测] need iss089_p9_topology_and_stack / iss089_chg_led_board_column 已被 hw-lead 答 (merge answered); ③ 见 HW/netlist_v1.csv L47 (ICHG/IIN = 1.216 方向修正已落表)", board="Y"),

    "iss213_mech_iss126_premise_superseded": dict(owner="main (issue_log 地界)",
        why="ISS-126 的 open 状态与解锁条件是 main 的活; 本域只给『前提已超越』的证据",
        oneline="main: ISS-126 的前提已被现口径超越 —— 现行板厚 = 1.00mm (6 层) (MECH/BOARD_GEOM_30MM §1 + service_port_check.py BASE pcb_thk=1.00, 注释『6 层现行; 4 层 0.80 已作废』) ⇒ 检修口盖板内腔 = 7.30 − 2.60 = 4.70mm >= cavity_req 4.50 ✅ 余 0.20 (实跑 54/54 OK / FAIL 0) ⇒ 『只有 0.80 及以下才安全』不成立 ⇒ 请裁关闭 (或改写为『板厚若改到 1.22 档才需重开』)",
        evidence="[实测] MECH/service_port_check.py 实跑 rc=0; [实测] 板厚 1.00 = 6 层 (MECH/BOARD_GEOM_30MM.md §1)", board="Y"),

    "iss213_mech_typec_third_candidate": dict(owner="main → boss (开口尺寸)",
        why="第三档几何已出且试样已落, 但『产品件走 FDM 直成型还是金属嵌件』是产品决策",
        oneline="main→boss: Type-C 开口第三档已出 (FDM 直成型 10.50×4.80 / 金属嵌件 CNC ±0.05 10.25×4.55, 最坏单边 0.63/0.62 ✅, 端件面板最小外形 13.50×7.80 含承力壁 ≥1.50) ⇒ 该特征不得靠打印面成型 ⇒ 请拍: 产品件走 FDM 直成型还是金属嵌件 (两档都合格, 是工艺路线决策) + 开口圆角 R; ★下游两件要排期: HW/CHARGE_BOARD_SPEC.md M-15 的名义+公差 (hw-lead) + 打印包加第三档试样",
        evidence="[推算] 原两档 (9.50×3.60 / 10.00×4.20) 在最坏公差下都判不合格 (X 0.13/0.38, Y 0.02/0.32) ⇒ 根因是 MECH/HW_CROSS_REVIEW.md §3.2 只把名义间隙推到 0.47, 没在最坏公差下验判据", board="Y"),

    "iss213_mech_pcb_class_6_queued": dict(owner="main (随整链重出)",
        why="6 个 PCB 类 id / 7 行 FAIL 按老板 11-11 10:07『PCB 布线/布局类一律不派, 排队等原理图定稿』⇒ 保持 FAIL 是正确状态; 只差『挂到哪一单』",
        oneline="main: 6 个 PCB 类 id (STK-FANOUT / PCB-X-GAP / MRG-54P / MRG-X-4 / MRG-X-3 ×2 / FRM-SUM) 的重算挂到哪一单? 恢复条件已逐条写在 MECH/hw_cross_review_check.py 的说明里 (原理图 P9 定稿给 4 条 FPC 实际落点与拓扑 ⇒ 复算 FPC 带宽合计 ≤ 板宽 30.00 − 0.60) ⇒ 建议随整链重出; ★本单一字没碰它, 分布未变 (PASS 14 / FAIL 17 / 条件通过 8 / 说明 15)",
        evidence="[实测] MECH/hw_cross_review_check.py 实跑 rc=0, 汇总 PASS 14 / FAIL 17 / 条件通过 8 / 说明 15 (共 54 项)", board="Y"),

    "iss216_mech_endpoint_metal_path_mass_after_u8": dict(owner="main (与 u8 同批)",
        why="金属热路的重量代价必须等 u8; 本域已把硬指标落定 (R_热路 ≤70 K/W ⇒ A ≥4.975mm²)",
        oneline="main: 端件金属热路的重量代价等 u8 落定后回算 —— 本域先落硬指标: R_热路 ≤70 K/W (60°C 端件判据下 0.50W ⇒ ΔT ≤35K); 铝 6063-T6 同几何 1.935 K/W ✅ / 打印件 1944 K/W ❌ ⇒ 热路必须是铝/铜件; ★§3 逐件 0 改动, 不预扣不猜数 ⇒ 请把 u8 排期与打印包第三档试样一起排",
        evidence="[实测] MECH/MECH_BUDGET.md §3 (R_热路 ≤70 K/W ⇒ 2.0×2.0 铝条不合格 R=87.1 K/W) + MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md", board="N"),

    "iss218_mech_tier3_coupon_print_and_measure": dict(owner="main (打印/切片/量测执行方)",
        why="试样已落成, 只差实物; 执行方归 boss 侧那条",
        oneline="main: Type-C 第三档试样已落成 (frame_typec_coupon_tier3_revb.stl, 72.0×32.0×5.0mm, 可直接下片) + 门禁 (余量对拍 4/4 + MECH_ANCHORS 7/7 + 反向用例 8/8) ⇒ 现在只差实物: 打印 + 切片 + 量测三项执行方 (本机跨网段不可达/无切片器/无量具) ⇒ 回填口径 = MECH/print/MEASURE_CHECKLIST.md N1~N27 (总 116 项) 填 state/measurements.yaml 的 M-PRINT (kind 必须写 实测) + MECH_BUDGET §5.4 的 FDM 孔径收缩/公差行; ★放行闸 = N23~N26 (装母座后单边塞尺 ≥0.60)",
        evidence="[实测] 门禁 4/4 + 7/7 + 8/8; 金属件图纸必须写: 开口 10.25±0.05 / 4.55±0.05 (逐项指定, 不许吃 2768-m 一般公差) + 开口尺寸按氧化后计 + 锐边倒钝 R0.2 去毛刺", board="Y"),

    "iss218_mech_u8_endpoint_section_decide": dict(owner="main (u8 拍板)",
        why="u8 是端件热路/框侧汇流/装配顺序三条链的共同前置; 本域已备好重量账模板",
        oneline="main: 端件截面 u8 请排期拍 (本域已把重量账模板备好: u8∈{30,33,35,38,40} × 表A 整条端件金属化 11.3~22.7g (比 W9 本身还重 ⇒ 不可接受) / 表B 半高 5.7~11.3g / 表C 局部热桥 0.95~5.67g (推荐 3.0×3.0=1.70g)); ★新算出一条硬下限: R_热路 ≤70K/W ⇒ A ≥4.98mm² ⇒ 2.0×2.0 铝条也不合格 (R=87.1 K/W)",
        evidence="[实测] MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md §2.5 五步走 + MECH/MECH_BUDGET.md §3 (W6/W9 现值 0 改动)", board="N"),

    "iss238_mech_marker_policy_decision": dict(owner="main (判据口径)",
        why="判据本体的放宽要走 H-1 重基线, 顺序不许倒; 本域推荐 P3 (判据本体零改动)",
        oneline="main: 作废标注的判据口径三选一 —— P1 regex (已作废 + 日期或 ISS 号) / P2 四选一 (漏检风险最高, 不推荐) / P3 维持单串 + 新增形态同步进清单 (★本域推荐★ ⇒ 判据本体零改动, 不用走 H-1); ★底线不许破: 放宽的只是『什么算作废标注』, 裸走鹃命中必须仍然是红; 另: 要不要把 python3 MECH/check_zoujuan_marker_consistency.py 挂进 state/daily_check.py? (实测 grep -n display_biosafety state/daily_check.py ⇒ 0 命中 ⇒ 巡检仍看不见)",
        evidence="[实测] 提案全文 + 10 条反向用例设计见 MECH/DISPLAY_BIOSAFETY_CRITERIA_V2_MARKER_POLICY_PROPOSAL.md", board="N"),

    "iss240_mech_hinge_fpc_truth_decisions": dict(owner="main (三处拍板)",
        why="跨铰链 FPC 几何收口三处要 main 拍; 改判据要 H-1 重基线, 本单不许碰",
        oneline="main: 跨铰链 FPC 三处请拍 —— (a) 旧 claim mech_hinge_stack_fixed_mm=25.00 与 G7/C9 字面判据怎么处置? 三档 (a) 改成 demo 口径 J_CHG 单链 (高度 5.00/径向 3.35) 丢留痕 / (b) 保留 25.00 但标明=整机阶段旧架构口径 demo 不适用 / (c) 拆 claim key (本域倾向 c); (b) hinge_usb_check.py 的 CROSS_LINKS 4 条 (CONN_USB 网表 0 命中) 与 ffc_pitch_mm 一律 0.5mm 怎么改? 建议按 board 栏取 (board==HINGE 才算跨铰链); (c) claim mech_hinge_links_count=0(demo) 与 mech_hinge_radial_mm=4.40 / mech_hinge_stack_declared_mm=49.62 三个旧 key 是否按 demo 口径清理",
        evidence="[实测] 现行口径 25.30 mm (整机) / 5.00 mm (demo) —— MECH/HINGE_FPC_GEOMETRY_TRUTH.md T1/T2; ★改判据 = 受保护脚本 H-1 重基线, 本单不许碰", board="N"),

    "iss222_mech_c7b_sink_is_metal_not_print": dict(owner="main (与 u8/集热面一起裁)",
        why="C-7b 改变了 C-7 的解法 (打印件顶面不能当集热面) ⇒ 集热面材质必须一起裁",
        oneline="main: C-7b 已算出: 打印件 PA-CF 沿上沿方向热阻 3610 K/W ⇒ 顶面有效热导 R=398.9 K/W (比同面积直接对流差 8.4 倍) ⇒ 实算腔体 53.60°C ❌ (超 50°C 红线 3.60°C) ⇒ ★铝制集热背板 120×30×1.0 不是可选降级, 是 P3 成立的必要条件 (装上 47.77°C @0.468W / 48.65 @0.50W ✅, P_max 0.5496W, +9.72g = 2.70 mg/mm²); 端件整条金属化 11.34-22.68g 换 600-800mm² = 14.18-37.80 mg/mm² (贵 5.3-14.0 倍且面积仍差 3-7 倍) ⇒ 不可接受 ⇒ 请裁集热面做成什么材质",
        evidence="[推算] MECH/MECH_BUDGET.md §3 C-7b 行 (P3 打印件方案实算 53.60°C ❌ vs 装铝背板 47.77°C ✅)", board="N"),

    "iss219_mech_c8_ts_axis_caliber": dict(owner="main (三选一)",
        why="分光件轴向口径不自洽, 三档全废 ⇒ 要么改口径, 要么给构型, 要么走并排化",
        oneline="main: §1.4.5 的 t_s=6.0mm 与平板几何在旧口径下就已不自洽 (45° 平板必须覆盖整个光束直径 ⇒ 竖向投影 >= 光束直径) ⇒ 修正后器件区 15.8/16.8 ⇒ 可动余量 -3.8/-0.8/+1.2 (旧) 与 -4.8/-1.8/+0.2 (新) ⇒ 三档全废 (d=20 余 0.2 < 判据 0.60) ⇒ 三条出路请裁: (a) t_s 改按平板竖向投影重算 ⇒ ISS-209 候选 1 器件区并排化 从推荐升级为必须 (b) 给分光件竖向压缩构型 (c) 走并排化 (耦合光学与分光件转向 90° 并排)",
        evidence="[推算] MECH/MECH_BUDGET.md §1.4.5 + §1.3 M6 + ISS-209 §4 候选 1", board="N"),

    "iss219_mech_c7_sink_area_confirm": dict(owner="main (镜框上沿可外露面积)",
        why="集热面面积能不能做到 3600mm² 是 C-7 的唯一前置",
        oneline="main: 镜框上沿可外露集热面能不能做到 120×30 = 3600mm² (波导压框/摄像头/装饰件会遮)? 做不到 ⇒ 降级: (a) 铝制集热背板 120×30×1.0 顶上沿外侧把面积做出来 (+9.72g) (b) 扩到镜框顶面 + 铰链上盖两处并联 (+800-1200mm²) (c) 面板功耗降到 ≤0.415W (P3 的 P_max=0.604W ⇒ 468mW 只余 +29%) (d) 改整机形态",
        evidence="[推算] d=15 档集热面需求 ≈2628mm² (P3) / ≈4175mm² (P1), 现状端件只有 600-800mm²; P3 达标时腔体 45.95-46.63°C @0.468W / 46.70-47.43°C @0.50W; u8 只占集热面 14.3-18.2% ⇒ u8 未定不阻塞本条", board="N"),

    "iss219_mech_m6_splitter_spec_landing": dict(owner="main (§1.3 M6 落地)",
        why="§1.3 M6 现行值是按走鹃Ⅱ 2.9mm 光束定的, 与眼盒 ≤62mm² 不自洽 ⇒ 换不换要拍",
        oneline="main: 请裁 §1.3 M6 的落地 —— 现行 14×10×6 / 0.79cc / W4 3-6g 按走鹃Ⅱ 2.9mm 光束定, 与 X-1 的 62mm² 眼盒不自洽; 结构侧新规格 (C-6, 已闭环 iss209_mech_splitter_resize_for_eyebox62) = 45° 平板 11×11×1.5 + 转向棱镜 ×2 9×9×5 ⇒ 0.9697cc (工程 0.9915) / W4 3.68-7.36g (工程 3.77-7.53), 腔体占位要放大; 连带整机重量上限 74.0 → 76.13g",
        evidence="[推算] MECH/MECH_BUDGET.md §1.3 M6 一行本单未改; [实测] 整数件重量表现值 0 改动", board="N"),

    "iss224_hw_landing_must_update_gate_ledger": dict(owner="hw-lead (常驻规则)",
        why="常驻规则: 每次落表要同步 MECH 侧锚点, 否则 MECH 闸假红",
        oneline="hw-lead: 每次改 HW/netlist_v1.csv 或 HW/netlist_v1_pins.csv 都必须同步 MECH 侧锚点 (MECH/HW_CROSS_REVIEW_TRIAGE.md §1 source_ledger.entries 的 md5/prev_md5/by/landed_at 四个字段), 且落表记录里必须能查到【落表单号 + 文件名 + 新 md5 + 旧 md5】四项 ⇒ 门禁 C21 逐项对账; ★只改锚点不落表 = 悄悄换真源, 只落表不改锚点 = 门禁假红",
        evidence="[实测] MECH/check_demo_struct_truth.py 的 C21 逐项对账 + ISS-233/ISS-249/ISS-277 三次并发落表的实测记录", board="Y"),

    "iss229_mech_hw_pcb_outline_old_charge_numbers": dict(owner="hw-lead (经项目总工)",
        why="HW 文档三处仍带 0.822 旧系数; 我不许代改 HW 地界",
        oneline="hw-lead: 请把 HW/PCB_OUTLINE_60x15.md 的三处旧系数数改掉 —— ①§3.4 表 ICHG/单 pin/余量: 390Ω 0.82A→1.216A / 0.411A→0.608A / ✅→❌超 0.5A 21.6%; 470Ω 0.68A→1.009A / 0.341A→0.505A / ✅→❌超 1.0%; 680Ω 0.47A→0.697A / 0.236A→0.349A / ✅余量 1.43×; 300Ω 0.534A→0.790A ②L149 充电时间 ~29.20min→~19.7min (典型 32.08→21.7min) ③§4.2 O-4 TS 参考地抬高 14-32mV=0.44-0.99°C → 390Ω max 36.5mV=1.13°C (留 1°C 裕量只在 680Ω/1.2kΩ 成立)",
        evidence="[实测] 该文 L149 (充电时间仍取旧 rilim_table) + L234 (脚本块里 ichg = tuple(v*0.822 for v in iin) 仍是倒向系数) + L276 (表行) 三处; 新数出处 MECH/HINGE_POWER_CALC.md §0-A.1 + MECH/hinge_power_calc.json", board="Y"),

    "iss229_mech_sw_evt_pwr05_charge_current_criterion": dict(owner="sw-lead",
        why="SW 的 PWR-05 判据量的是哪个电流, 只有 sw-lead 能定",
        oneline="sw-lead: 请复核 SW/EVT_TEMPLATE.md PWR-05『充电电流 ≥1.5A @5V/2A 适配器』量的是输入电流 IIN 还是电池侧电流 ICHG —— 改正系数 1.216 下 max 档电池侧 = 390Ω 1.216A / 680Ω 0.697A / 1.2kΩ 0.395A (连现行 V-4 候选 680Ω 也只有 0.697A ⇒ 1.5A 达不到); 若量的是 IIN, 390Ω max 1.00A / 680Ω 0.574A ⇒ 同样达不到; ★该不兼容在旧 0.822 系数下就已存在 (390Ω max = 0.822A) ⇒ 属既存判据, 不是 ISS-229 造成的",
        evidence="[实测] MECH/HINGE_POWER_CALC.md §0-A.1 + MECH/hinge_power_calc.json; 复现: python3 MECH/hinge_power_calc.py (rc=0)", board="Y"),

    # ---- 板那一趟相关 (检修口净空 / 开口坐标 / 帧 id / 落表台账 / 挂链口径) ----
    "iss222_mech_print_pack_optical_cage_md5": dict(owner="main (PROJECT_TRACKER 是项目总工地界)",
        why="打印包禁改项因走鹃Ⅱ 作废而解冻, STL 已重生, 但台账登记值还没更新",
        oneline="main: 请把 PROJECT_TRACKER.md 里 optical_cage_TEMPLATE.stl 的登记 md5 从 6f23c2e2f52e81060e5c0bbecb4cc881 更新成 537dc6afb4246cce30aa6853de7cebd1 (ISS-222 已按新规格重生: 分光件座 14×6×10 → 7.78×8.84×11.0; 其余 6 个 STL 逐字节未变)",
        evidence="[实测] PROJECT_TRACKER.md L1286 / L1386 仍写旧 md5 6f23c2e2f52e81060e5c0bbecb4cc881", board="Y"),

    "iss264_mech_jd_y0_and_open_y_caliber": dict(owner="main + hw-lead",
        why="jd_y0 (J_DEBUG 焊盘阵列 Y 起点) 是所有检修口 Y 向数的总开关, 未定则开口 Y / P-5 最近距离全部悬着",
        oneline="main+hw-lead: 请给 30mm 板上 J_DEBUG 阵列真实起点 jd_y0 (合法区间 [1.665, 11.730], 现状 9.50) ⇒ 定了它, 开口 Y (现 7.835..12.435) 与 P-5 最近距离 (P2 3.23mm / S2 8.53mm) 一次算清; ★候选 A 9.50 / C 10.00~11.00 (B 不可用), 且须与落表 1x4 vs 脚本 2x5 的脚数一起定 (差 0.635mm)",
        evidence="[实测] MECH/service_port_check.py 检查项 8.1b 脚本实算开口 Y = 7.835..12.435 + 检查项 7.4/7.5 (3.23 / 8.53); 文档旧值 8.67..13.27 已标作废 (对应 jd_y0=10.97)", board="Y"),

    "iss264_mech_jd_y0_legal_range_errata_pending": dict(owner="main",
        why="两件要 main 拍/改: 决策页 A 段的 jd_y0 区间订正 + 检查项 2.5 的 Y 上限是否按 30mm 板口径放宽",
        oneline="main: 请拍两件 —— ① 决策页 A 段把『jd_y0 合法区间』改成订正后的 [1.665, 11.730] mm, 并把『按相对位置迁 ⇒ 孔与焊盘阵列重叠 12.37mm』改写成『检查项 2.5 判红 (焊盘上沿 25.77 > 13.00, 余量 -12.77mm)』(P-5 3.23/8.53 与开口 Y 7.835..12.435 不变) ② 检查项 2.5 的 Y 上限 13.00 要不要按 30mm 板口径订正为 28.00 (订正 ⇒ 区间上界 11.73→26.73, 候选表整张重算, jd_y0=24.50 几何上变可行但治具/探针对位前提要重谈; 不订正 ⇒ 维持最保守窄带, 候选只有 A 9.50 / C 10.00~11.00)",
        evidence="[实测] 区间订正依据 ISS-267 U6 + check_demo_struct_truth.py 检查项 2.5 实算 (上界 11.73 不是 12.13 / 下界 1.665 不是 3.57)", board="Y"),

    "iss267_mech_jd_y0_and_frame_decision": dict(owner="main (板框三选一) → boss",
        why="板框三套并存 + jd_y0 两拍合并; 板框 = 老板拍, main 汇总",
        oneline="main: 板框口径三选一请汇总后交老板 (① B160x100 台架板 160×100 ② F30A 产品板 60×30 套A ③ P60x15 60×15) —— 结构侧已给 36 档机器可行域表 (MECH/board_frame_feasibility.py) + 两条路线代价 (MECH/BOARD_FRAME_DECISION_INPUT.md §C): ① 36 档全红 (V链-68.00 / L链-85.50, 与板厚无关) 且板本身 47.36g = 整机质量预算 65~97% ⇒ 不得宣称可投产; ② 板厚 0.80/1.00 两档全绿 (开口可一次带完) 但 S6 20 落位 + 三条开口 + 座体 6 组 + 9 道钉板闸 + MECH 6 闸 + 帧表 + 叠层阻抗 + 骨架截面 都要重算重锚且 P7 布通未验证 ⇒ 建议先拍框再拍板厚再拍层数最后 P7",
        evidence="[实测] MECH/BOARD_FRAME_DECISION_INPUT.md §C + MECH/board_frame_feasibility.py 36 档实算; ★老板 11-17 已拍 P7/P8 = 改现役 160×100 台架板 (帧 B160x100) ⇒ 需与本条的口径统一", board="Y"),

    "iss267_mech_debug_part_model": dict(owner="hw-lead",
        why="J_DEBUG 脚数与座体高度是结构开口尺寸的输入, 落表与结构模型不一致",
        oneline="hw-lead: 请定 J_DEBUG 的脚数与座体真实高度 —— 落表是 1×4 (HW/BOM_v1.csv:71 + HW/netlist_v1_pins.csv:202-205) 而 MECH/service_port_check.py 按 2×5 (10 脚 Cortex-10) 算 ⇒ 必须清空区 X 宽 7.62 与开口 X 10.20 要重算; 另 J_UART 相对位置: 盘上板 J_DEBUG@(144.30,58.00) 与 J_UART@(20.74,70.00) 相距 123.6mm 而结构模型让它们紧邻 ⇒ 开口 X 49.21..59.41 在盘上板不成立; 座体真实高 2.54 是假设 ⇒ 开口 Y 宽 4.60 / 单边 1.03 全部依赖它 ⇒ [0数据]",
        evidence="[实测] 板读 J_DEBUG@(144.30,58.00) / J_UART@(20.74,70.00); BOM 1×4 vs 结构 2×5", board="Y"),

    "iss271_mech_s6_ledg_window": dict(owner="hw-lead (板那一趟坐标空间)",
        why="板侧落位坐标已算好, 等 hw-lead 在板那一趟用; 但脚数与 J_UART 相对位置还没定",
        oneline="hw-lead: 板侧坐标空间可直接用 —— (1) 检修口/调试口: Y 向 jd_y0 ∈ [1.665, 11.730] (现状 9.50), X 向 jd_x0 ∈ [48.290, 51.090] (2×5) 或 [48.925, 51.725] (落表 1×4), 开口 X 可放行区间 [47.00, 60.00], 必须清空区 X 50.50..58.12 × Y jd_y0±1.27, 开口 10.20×4.60, 单边间隙 X 1.29 / Y 1.03; ★脚数与 jd_x0 必须一起定 (差 0.635mm) (2) D_LED_G 落位窗口 (60×30 套A 板坐标): 可放行矩形 18 块, 全高可用 X 带 3 条 (X 3.00..6.40 / X 9.60..14.20 / ★X 33.00..47.71 宽 14.71 = 首选窗口★) × Y 1.60..28.40",
        evidence="[实测] 本域实算 (MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md §7b + MECH/BOARD_ONEPASS_MECH_SYNC.md §3)", board="Y"),

    "iss276_mech_s6_claim_frame_align": dict(owner="hw-lead",
        why="帧 id 与坐标基准必须两边一致, 不一致就停手",
        oneline="hw-lead: 请与 HW/PCB/BOARD_FRAME_CALIBER.md (ISS-274 同批产出) 的帧声明对齐后再收进 §3-S6 —— 三条具体: ①调试口开口 = X 137.850..148.050 × Y 54.300..58.900 (帧 B160x100), 左下角可放行 X0 ∈ [137.850, 142.063] · Y0 ∈ [54.300, 55.330] ②UART 检修口开口 = X 13.790..23.990 × Y 66.300..70.900, 左下角可放行 X0 ∈ [13.790, 17.620] · Y0 ∈ [66.300, 67.330] ③★S6 必须拆成两条: J_DEBUG (144.30,58.00) 与 J_UART (20.74,70.00) ΔX = 123.56mm ⇒ 一个开口罩不住两个 ⇒『必须清空区 7.62×2.54』是 60×30 套A 的并排模型, 在本帧不成立, 不得抄★",
        evidence="[实测] MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md §1 + 板读 J_DEBUG/J_UART 坐标", board="Y"),

    "iss296_mech_m3_nine_gates_green_need": dict(owner="main (写进板那一趟作业包)",
        why="9 道钉板 md5 闸要收工当天同一次全绿, 这句话必须写进作业包",
        oneline="main: 请把『9 道钉板 md5 闸 ①~⑨ 收工当天必须同一次全绿』写进板那一趟的作业包 —— 机器清单 state/board_md5_pinned_gates.json 实测 9/9 全是『已有 reboard 通道』(HW 6 道由 ISS-297 建好, 本单已把 M3 表那 6 个单元格由『待建』订正为『已建 (ISS-297)』并留痕); ★第 5 道 HW/check_pin_function_labels.py 主模式仍 rc=1 (18 条 ISS-257 起的既有缺陷, 属别单范畴) ⇒ 那一道的前置债在 hw-lead 那边",
        evidence="[实测] state/board_md5_pinned_gates.json (mtime 2026-11-17 20:49) 9/9 有通道", board="Y"),

    "iss296_mech_m2_6_frame_id_need": dict(owner="main → boss (U-274-6)",
        why="帧 id 统一 = 老板级 (U-274-6), 且是后期坐标漂移的根",
        oneline="main→boss: 帧 id 统一请拍 (U-274-6) —— 盘上并存 B160x100 (MECH 闸现役帧) / 160x100-bench (HW 侧) / 60x30-setA / F30A 四套写法 ⇒ 权威表是 HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES = B160x100 / F30A / P60x15 (现役 = B160x100), MECH/check_onepass_mech_sync.py 的 FRAMES_ALLOWED 亦为同三个 id ⇒ 本单一律按权威表三个 id 书写; 另请裁: 是否在 MECH 两页 (BOARD_PORT_OPENING_S6_FRAME_CALIBER.md / BOARD_ONEPASS_MECH_CLAIMS.md) 加一行 id 对照注记, 免得两处各写一套",
        evidence="[实测] HW/PCB/BOARD_FRAME_CALIBER.md §2 + MECH/check_onepass_mech_sync.py FRAMES_ALLOWED", board="Y"),

    "iss296_mech_m1_ledger_row_need": dict(owner="main (出板那一趟落表用)",
        why="落表台账那一行的接口格式是出板那一趟的输入, 台账本体不许 MECH 侧写",
        oneline="main: 出板那一趟落表请按这个格式写 —— 每受管文件一行 = 单号 | 文件名 | 改前 md5 | 改后 md5 四项同行; 板与 .kicad_pro 必须成对两行同一个单号 (只写一行 ⇒ 判红); .kicad_pro 真没变时也要写『否 (逐字节不变)』那一行; 一行不许同时写两件两值 (歧义行 ⇒ MECH 侧当它不算变更行 ⇒ 判红); 单号必须出现在行内或该行所属小节标题里; ★板的前值 = 611b869e13518c3c023fb178f91a0075, .kicad_pro 的前值 = 3e504d2be83152e337949723e909be1b (逐字节不变)",
        evidence="[实测] MECH/check_demo_struct_truth.py 的 C21 逐项对账 (12 条反向用例)", board="Y"),

    "iss300_release_gate_hook_into_gate_chain": dict(owner="main (挂闸是项目总工的活)",
        why="挂闸动作在 main 地界 (state/gate_check.py 一个字不许本单改)",
        oneline="main: 请把 MECH/check_onepass_mech_release.py 挂进 state/gate_check.py 的 EXTRA_GATES —— 事实: 该闸 rc=0 实跑通过, fail-closed 语义与现有 run_external_gate 同款, 不写任何文件, 不碰板; 代价: gate_check 每次跑多一道外闸, 该闸内部再跑 6 道 ⇒ 门禁链单次耗时增加约 6 闸的量 (本机实测 6 闸合计 <60s)",
        evidence="[实测] state/gate_check.py:211-214 EXTRA_GATES 现只有 2 条 (MECH/check_mech_verdict_freshness.py + SW/tools/check_onepass_sw_sync.py) ⇒ 该闸尚未挂上; 本单未改 gate_check.py 一个字", board="Y"),

    "iss300_release_gate_hook_staging_vs_legal_reboard": dict(owner="main (口径裁决)",
        why="挂链后板那一趟当天必然从绿转红 —— 这个口径必须先裁, 否则会误读成板改坏了",
        oneline="main: 请裁挂链口径 —— 6 道里有 2 道是钉板 md5 闸 (check_board_frame_coords 的 C4 + check_onepass_mech_sync 的 M5) ⇒ 板只改一次那一趟板 md5 会合法变 ⇒ 那 2 道当天必然从绿转红 ⇒ 只有走合法改板通道 (ISS-296 已建好) 才回绿; 代价: 挂链后当天 gate_check 会红 ⇒ 若不分阶段, 会被误读成板改坏 → 去改板凑绿 → 板 md5 变第二次 → 整趟白跑 ⇒ 本域已把这句话写死在汇总闸的失败输出里 (板 md5 当天变更是合法的, 绝不许改板凑绿)",
        evidence="[实测] 板 md5 611b869e13518c3c023fb178f91a0075 / mtime 2026-11-06 07:07:17 逐字节不变 (本轮实测)", board="Y"),

    "iss296_mech_cont3b_reboard_day_selftest_must_run": dict(owner="main (写进收工验收清单)",
        why="板那一趟落表当天, MECH 两道闸的主跑与 --selftest 必须同一次一起绿 —— ⑱/⑲ 两条反向用例已把 main 的真实落表形状 (两张表) 钉进闸的自检, 只跑主模式抓不到假红",
        oneline="main: 请把『板那一趟落表后 MECH 两道闸的【主跑 + --selftest】必须同一次一起绿』写进收工验收清单 —— ⑱/⑲ 两条用例已把真实落表形状 (两张表) 钉进闸的自检 ⇒ 落表当天若只跑主模式, 两张表形状的假红不会被抓到",
        evidence="[实测] 本轮实跑 python3 MECH/check_demo_struct_truth.py --selftest ⇒ rc=0 (反向用例 28/28 抓到) + 主跑 rc=0; ★板 md5 611b869e13518c3c023fb178f91a0075 / mtime 2026-11-06 07:07:17 逐字节不变",
        board="Y"),

    "iss303_mech_n6_depends_on_cfc_ledger_api": dict(owner="main (代码级耦合登记 · 常驻约束)",
        why="★这是永久约束不是一次性事项: N6 只读调用板框坐标闸的 5 个名字, 改名 = 本域闸 fail-closed 恒红",
        oneline="main: 代码级耦合登记 (常驻): MECH/check_onepass_struct_crosscheck.py 的 N6 只读调用 MECH/check_board_frame_coords.py 的 5 个名字 (ledger_state / ledger_cover_rows / m12 / PROTECTED / LEDGER_CANON) ⇒ 这 5 个名字不许改 (改名 = 我的闸 fail-closed 恒红); 若要改口径请走同源改法 (ISS-296 同源探针 logs/iss296/probe_ledger_reading_same_source.py 继续跑); ★代价: 板帧坐标闸与结构交叉核对闸共用一套台账解析器 ⇒ 好处口径零漂移, 边界同域 MECH/ 内 ⇒ 不碰 HW/ 与 SW/",
        evidence="[实测] MECH/check_onepass_struct_crosscheck.py N6 的 5 个只读名 + MECH/check_board_frame_coords.py 对应定义",
        board="Y"),

    "iss303_mech_n6_membership_vs_equality_caliber": dict(owner="main (口径二选一)",
        why="两道闸口径不同源 (一道成员判定, 一道等值判定), 是取舍不是事实",
        oneline="main: 请裁 N6 与 C4 的口径 —— N6 现在是【成员判定】(盘上 md5 ∈ 硬基线 ∪ 台账登记过的 md5) 而 MECH/check_board_frame_coords.py 的 C4 仍是【等值判定】(盘上 md5 必须 == 台账链头) ⇒ 若台账里出现链上历史值 (或盘上被回滚到硬基线) 则 C4 会红而 N6 会绿; 代价: 两道闸口径不同源 (一道兜底合法落表跳, 一道严格等值) ⇒ 建议保持现状 (严格等值仍由 C4 承担) 或把 N6 也改成等值 (更严但盘上回滚场景会红); 本单按任务书 B1.2 的字面口径实现 (成员判定)",
        evidence="[实测] MECH/check_onepass_struct_crosscheck.py N6 + MECH/check_board_frame_coords.py C4 实读", board="Y"),
}
