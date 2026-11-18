#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1440_verify_iss241_open_iss243_244.py
★main (moli) 2026-11-16 14:4x (cron 775d9893 ARS45 继续执行后继计划)★
★① ISS-241 (sw-lead) 独立复验 ⇒ 落 verified (清 sw-lead 名额)
★② 新开 ISS-243 (hw-lead · 落表前置 L1~L4) + ISS-244 (sw-lead · 缺口 G-1~G-10 自查补全 + OPN 回填清单)★

★★**为什么做这三件事 (★main 本轮自己实跑, 不抄任何交卷报告★)** ★★
· ★**`python3 state/advance.py --json` ⇒ internal = [] · approvals = [] · waiting = []** ⇒ rc=1
  ⇒ ★**根因 = sw-lead / hw-lead 两个名额都被【fixing】占着**:
    ★**sw-lead 名额 = ISS-241** (会话 `agent:sw-lead:subagent:89d4b23f` · session e6ffbd28 · status=**done** ·
      14:18 交卷 · ★**四件交付物已全部落盘** ⇒ **已交卷未签字**, 不是僵尸★)
    ★**hw-lead 名额 = ISS-242** (会话 `agent:hw-lead:subagent:2fcfe9b5` · session 5b030d1c · status=**running** ·
      ★**14:18 还在写分片 ⇒ 真在飞** ⇒ 本轮不派 hw-lead★)
· ★**⇒ 本轮: ① 清 ISS-241 (verified) ⇒ sw-lead 名额释放 ② 给 sw-lead 开 ISS-244 并立即派 ③ 给 hw-lead 开 ISS-243 (排队, 等 ISS-242 交卷)** ★

★★**ISS-241 复验 (★main 本轮自己实跑, 逐条不采信 agent 自述★)** ★★
· ★**`python3 HW/check_part_selection_matrix.py` ⇒ rc=0 (C0~C7 共 8 条全过)** ★
· ★**`--selftest` ⇒ rc=0 · 9/9 全抓到** (M1 删位号→C1/C7 红 · M2 候选清空→C2/C6 红 · M3 降级删空→C4 红 ·
  M4 越界位号→C7 红 · M5 非法证据等级→C5 红 · M6 删封装结论→C3 红 · M7 推荐项 why 清空→C4 红 ·
  M8 破坏 baseline JSON→C0 红 · M9 候选降到 1 个→C2 红 ⇒ **每条都带「变异生效 + 落盘回读复核同红」自证**) ★
· ★★**覆盖度 main 亲核 (★不是抄矩阵自报★)★**: ★**main 自己跑 `csv.DictReader` 读 `HW/BOM_v1.csv`**
  ⇒ ★**value 含「待选型」且 dnp=必装 的行 = 32 行 / 32 个位号** ⇒ ★**其中 9 个是 DNP (C_VBUS_IN/OUT/GND · D_ESD_LIGHT ·
  D_LED_B · Q1 · Q2 · SW_KEY_CAM · U_SUPV) ⇒ 剩下 23 个必装** ⇒ ★**矩阵 `expected_refs` = 22 个** ⇒ ★**差的那 1 个 = `U_PWR_SW`
  (★ISS-172 已单独出过矩阵 ⇒ 本单按黑名单排除, 不重复★) ⇒ ★**⇒ 覆盖度 22/22 完整, 零漏项** ★★
· ★**四件交付物 main 亲测在盘**: `HW/PART_SELECTION_MATRIX_2026-11-16.md` 153057 B (mtime 14:28) ·
  `HW/check_part_selection_matrix.py` 15723 B (mtime 14:28) · `HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md` 34734 B (mtime 14:31) ·
  `state/fragments/sw.yaml` (mtime 14:30 ⇒ ★**本单真写盘**: +3 artifact / +3 interface_claim / +2 answer · `needs_from` 一条没加★) ★
· ★**旁证**: `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (★【Q1】18/18★) · ★**5 个受保护 md5 逐字节未变**
  (板 611b869e… / .kicad_pro 3e504d2b… / 网表 34132f7e… / 脚表 b21b743a… / BOM c195a117…) ★
· ★**本单零落表**: ★**网表 L44/L45 (`C_REGN` = 「[待选型] 1µF」) 一字没改** ⇒ 等落表批次 ★
· ★**未替老板拍板**: ★**V-2 (ESD 方案二选一) / V-3 / V-4 / G-1 (Q_PG 源漏拓扑) 一条没代拍** ⇒ 已并进决策页 §A-补4 (W-1~W-6) ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml`** (ISS-241 的 status/verify_result/note + 追加两条新单) ★
· ★**不改任何交付物文件** · ★**不碰 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** ★
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM** · ★**零外发** · ★**未替老板拍板** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
IL_LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"

# ---------------------------------------------------------------- ISS-241 复验
VERIFY_241 = (
    "★main (moli) 2026-11-16 14:4x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**会话**: `agent:sw-lead:subagent:89d4b23f` (session e6ffbd28) 13:47:09 起 · 14:18 止 · runtime 2679s · ★**status=done** ★ ⇒ **真交卷** ★\n"
    "· ★**main 自己实跑 2 道闸**: `python3 HW/check_part_selection_matrix.py` ⇒ **rc=0** (「PASS — 选型证据矩阵门禁全过 (8/8)」★) · "
    "`--selftest` ⇒ **rc=0 · 9/9** (★每条都自证「变异生效 / 变异前绿 / 变异后红」+ 落盘回读复核同红★)\n"
    "· ★★**覆盖度 main 亲核 (★不是抄矩阵自报★)★**: ★**main 自己跑 `csv.DictReader` 读 `HW/BOM_v1.csv`** ⇒ "
    "★**value 含「待选型」的行 = 32 行 / 32 个位号** ⇒ ★**其中 9 个是 DNP** (C_VBUS_IN / C_VBUS_OUT / C_VBUS_GND / D_ESD_LIGHT / "
    "D_LED_B / Q1 / Q2 / SW_KEY_CAM / U_SUPV) ⇒ ★**剩下 23 个必装** ⇒ ★**矩阵 `expected_refs` = 22 个** ⇒ "
    "★**差的 1 个 = `U_PWR_SW` (ISS-172 已单独出过矩阵 ⇒ 本单按黑名单排除·不重复)** ⇒ ★**⇒ 覆盖 22/22 完整, 零漏项** ★★\n"
    "· ★**四件交付物 main 亲测在盘**: `HW/PART_SELECTION_MATRIX_2026-11-16.md` 153057 B (mtime 14:28) · "
    "`HW/check_part_selection_matrix.py` 15723 B (mtime 14:28) · "
    "`HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md` 34734 B (mtime 14:31) · "
    "`state/fragments/sw.yaml` (mtime 14:30 ⇒ ★**本单真写盘**: +3 artifact / +3 interface_claim / +2 answer · `needs_from` 一条没加★)\n"
    "· ★**旁证**: `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (★【Q1】18/18★) · ★**5 个受保护 md5 逐字节未变** "
    "(板 611b869e… / .kicad_pro 3e504d2b… / 网表 34132f7e… / 脚表 b21b743a… / BOM c195a117…)\n"
    "· ★**本单零落表**: ★**网表 L44/L45 (`C_REGN` = 「[待选型] 1µF」) 一字没改** (★TI BQ25896 手册 pin22 要求 4.7µF(10V) ⇒ 归落表批次★)\n"
    "· ★**未替老板拍板**: ★**V-2 (ESD 方案二选一) / V-3 / V-4 / G-1 (Q_PG 源漏拓扑) 一条没代拍** ⇒ ★**已并进决策页 "
    "`DECISION_PENDING_2026-11-16.md` §A-补4 (W-1~W-6)★"
)

NOTE_241 = (
    "\n\n★2026-11-16 14:4x (cron 775d9893 继续执行后继计划) ★**main 独立复验 ⇒ 落 verified · 清 sw-lead 名额** ★\n"
    "· ★**依据 (★main 本轮自己实跑, 不采信 agent 自述★)**: 选型矩阵门禁 rc=0 **8/8** · `--selftest` rc=0 **9/9** · "
    "★**覆盖度 main 亲核 = 22/22 (BOM 待选型∩必装 23 件 − U_PWR_SW〔ISS-172 已办〕= 22)** · 四件交付物在盘 · merge rc=0 · gate_check Q1 18/18 · ★**5 个受保护 md5 逐字节未变** ★\n"
    "· ★**为什么必须清 (★不是形式主义★)**: status=fixing ⇒ advance.py 的 in_flight 判据挡住 sw-lead ⇒ "
    "★**sw-lead 唯一写会话名额被『已交卷但没签字』占着** ⇒ A 段开不出来 ★\n"
    "· ★**清账后 sw-lead 名额释放** ⇒ ★**本轮已开 ISS-244 (sw-lead) 并派出 (见 dispatch_log)** ★\n"
    "· ★**3 条硬发现一条没代拍, 已并进决策页 §A-补4 (W-1~W-6)**: ESD 4 件只能落单通道 2 脚件 / 占位 pad 序 ≠ 库引脚序 / `C_REGN` 1µF vs 官方 4.7µF ★\n"
    "· ★**边界**: 只改本条 status/verify_result/verify_by/verify_date/note · 零外发 · 零落表 · 零 PCB 触碰 · 没碰任何分片 / 真源文件 / outbox ★"
)

# ---------------------------------------------------------------- ISS-243 新开
TITLE_243 = (
    "★★[主线内·原理图/网表侧·内部活] ★★ISS-241 交卷的 4 条落表前置 (L1~L4) 收口: "
    "① **L1/G-6 `C_REGN` = 1µF → 4.7µF(10V) 官方值订正** (★TI BQ25896 pin22 原文要求 4.7µF ⇒ 网表 L44/L45 + 脚表 + BOM 三处★) · "
    "② **L2/G-2 三件 MOS 的占位 pad↔pin 映射表** (★实测 `Q_AND`=D/S/G · `Q_ENVC`=G/S/D · `Q_PG`=S/D/G ⇒ SOT-23 库序 G/S/D ⇒ 必重画 land★) · "
    "③ **L3 `D_ESD_CAM` pad1=GND 与另两件反序 ⇒ 单向 ESD 件会接错** · "
    "④ **L4/G-8 充电板侧 6 件器件 footprint 全「待定」** (★`D_ESD_TC`/`FB_VBUS`/`D_TVS_VBUS`/`Q_CHG_LED`/`D_CHG_LED`/`C_REGN`★) "
    "⇒ **L1 直接落表 (官方值, 无需拍板) + L2/L3/L4 出逐字改法映射 (只报不改板)**"
)

DESC_243 = (
    "★main 2026-11-16 14:3x~14:4x 自己实跑 + 逐行实读出来的 (★不是抄任何交卷报告★) ★\n"
    "★**① L1 (G-6) —— `C_REGN` 值与原厂手册冲突 (★官方硬要求, 无需老板拍板★)**: ★**main 实读网表 L44/L45 = 「[待选型] 1µF」** ★\n"
    "  ⇒ ★**TI BQ25896 (SLUSC76C) pin22 REGN 原文: 「Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND」** "
    "(★sw-lead 已下载原厂 PDF 本地 pdftotext 实读; 你必须自己再核一遍, 不许照抄★) ⇒ ★**差 4.7 倍** ⇒ 落表批次必须改 BOM value ★\n"
    "★**② L2 (G-2) —— 占位 pad 序号 ≠ 库封装引脚序 (★实测数据, 你必须自己重读板文件复核★)**: ★**`Q_AND` pad1=RESET_N(D)/pad2=GND(S)/pad3=PG_AND(G) = D/S/G** ★\n"
    "  · ★**`Q_ENVC` pad1=PG_AND(G)/pad2=GND(S)/pad3=EN_VCORE(D) = G/S/D (唯一天然对上)** ★\n"
    "  · ★**`Q_PG` pad1=PWR_ON(S)/pad2=BAT_SW(D)/pad3=PWR_GOOD(G) = S/D/G** ★\n"
    "  ⇒ ★**SOT-23 库引脚序统一 G/S/D ⇒ `Q_AND`/`Q_PG` 必须人工改映射 (接反 ⇒ Vgs 极性反 ⇒ 开机路径不通)** ★\n"
    "★**③ L3 —— `D_ESD_CAM` pad 序与另两件相反**: ★**pad1=GND / pad2=CSI_D0_CK_P**; 而 `D_ESD_DEMO`/`D_ESD_USB_D` 是 pad1=信号 / pad2=GND ★\n"
    "  ⇒ ★**单向器件 (TI TPD1E05U06: pin1=I/O · pin2=GND) 按 pad 序号机械接 ⇒ I/O 接到 GND 位 ⇒ 直接不工作** ⇒ 对调 or 改双向件 (归 W-1) ★\n"
    "★**④ L4 (G-8) —— 充电板 6 件器件封装是「待定」** ⇒ ★**板文件里查无这些位号 ⇒ 无法给几何兼容结论 ⇒ 充电板要画图必须先定封装** ★\n"
    "★**⑤ 本单要做的四件事**: ★**① L1 落表 (`C_REGN` 4.7µF, 网表+脚表+BOM 三处, 逐字改法 + 落表台账登记) ② L2 出三件 MOS 的 pad↔pin 映射表 (板那一趟照表改) ③ L3 出 `D_ESD_CAM` 的改法映射 ④ L4 出充电板 6 件 footprint 候选清单** ★"
)

BRIEF_243 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**ISS-241 交卷时点名交回硬件侧的 4 条落表前置 (L1~L4) 收口**★ ⇒ ★**L1 直接落表 (官方值, 无需拍板) + L2/L3/L4 出逐字改法映射 (只报不改板) + 落表台账登记 + 一道独立机器门禁**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 14:3x~14:4x 自己实跑, 不是推测★)** ★★
· ★**main 实读网表 L44/L45**: `C_REGN` value = 「**[待选型] 1µF**」 ⇒ 与原厂手册冲突 (见下 L1) ★
· ★**main 实跑 `python3 HW/check_part_selection_matrix.py` ⇒ rc=0 (8/8)** (★ISS-241 的矩阵门禁, 证明 22 件覆盖完整★)
· ★**main 实算覆盖度**: BOM 里 value 含「待选型」且必装 = 23 件 ⇒ 减 `U_PWR_SW` (ISS-172 已办) = 22 件 ⇒ ★**矩阵 22/22 全覆盖** ★
· ★**main 实读矩阵 §4 缺口登记**: G-1/G-2/G-6/G-8 四条明确写着「归 hw-lead / 落表批次」 ★

★★**① L1 (G-6): `C_REGN` 官方值订正 —— ★【本单唯一允许改真源的一项】★** ★★
· ★**依据 (你必须自己核, 不许照抄)**: ★**TI BQ25896 (SLUSC76C) pin22 REGN 原文要求 4.7 µF (10 V rating) 陶瓷电容, 且要贴近 IC 放置** ★
  ⇒ ★**取法**: ★**自己下载原厂 PDF (ti.com 的 BQ25896 datasheet) ⇒ `pdftotext` 实读 pin22 段落 ⇒ 把原文抄进交卷单** ★
  (★**抓取纪律**: 用 `web_search`/`web_fetch` + 带 `--max-time` 的 curl; ★**不许 curl 挂死** ⇒ 本机上一轮 curl 卡死过, 必须加 `--max-time`★) ★
· ★**改什么 (★三处, 一处不许漏★)**:
  ① `HW/netlist_v1.csv` L44/L45 (★**两条行**: `P1,REGN,C_REGN,U_CHG pin22,C_REGN,...` 与 `P1,GND,C_REGN,GND,C_REGN,...`★) ⇒ value 栏 `[待选型] 1µF` → `4.7µF ±10% (10V)` (★**耐压必须写进去, 手册明确要 10 V rating★) ★
  ② `HW/netlist_v1_pins.csv` 里 `C_REGN` 的对应行 (★**自己 grep 定位, 行号会漂移 ⇒ 以 ref+net 为锚, 不要写死行号★) ★
  ③ `HW/BOM_v1.csv` 里 `C_REGN` 行的 value 栏 ⇒ 同值 + ★**opn 栏如果还是空的, 填官方可采购型号 (例: GRM188R71H475KA73D /  Murata GRM188 系列 4.7µF 10V X7R 0603★ —— ★**具体型号自己查官方在售, 标 [官网] 出处, 不许瞎写**★) ★
  ⇒ ★**「充电板贴 U_CHG pin22」的放置要求**: ★**同时把这句话写进 `HW/CHARGE_BOARD_SPEC.md` (§REGN 那节或你判断合适的位置, ★**只加一节, 不许删改别人写的内容★)★**
· ★**落表纪律 (★必读★)**:
  · ★**落表前先备份** (★沿用本仓惯例: `state/.bak_iss243/` 放改前副本★) ★
  · ★**落表后必须把这一行登记进落表台账** (★`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` §9 修订记录 / §落表台账 四项 (单号/文件/行/说明) · ★**沿用 ISS-223/ISS-233 的台账写法, 自己读那份文件照抄格式★) ★
  · ★**落表后必须跑这 4 道闸并把原样输出贴进交卷单**: ★**`python3 state/check_netlist.py` · `python3 state/check_netlist_pins.py` · `python3 state/check_sch_erc.py` · `python3 state/check_sch_pinfull.py` · ★**外加 `python3 state/merge.py && python3 state/gate_check.py` (★【Q1】18/18★) ⇒ 全部 rc=0** ★
  · ★**`HW/check_netlist_selfconsistency.py --expect-resolved` 的条数不许变多** (★落表前后的数字必须记在交卷单里★) ★
· ★**绝对不许**: ★**动 ISS-242 已经落的那几行** (★`C_VBUS_OUT`/`C_VBUS_GND` 两颗 2 脚电容各落进 3 个网 ⇒ ISS-242 在改 ⇒ ★**你动手前必须先读盘看 ISS-242 落了什么, 不许照抄本任务书里的行号★) · ★**改板 / 改布线 / 改布局 / 改板框** · ★**改脚表里别的器件** ★

★★**② L2 (G-2): 三件 MOS 的 pad↔pin 映射表 (★只出表, 不许改板★)** ★★
· ★**自己读板文件实测** (★不许照抄本任务书给的数, 你必须自己从 `HW/PCB/demo_mainboard.kicad_pcb` 里读出 pad 号 / net / 尺寸★) ★
· ★**交一张表, 每件 MOS 一行**: ★**位号 · pad1(net/引脚功能) · pad2 · pad3 · 占位 pad 序(如 D/S/G) · SOT-23 库引脚序(G/S/D) · 是否一致 · 重画 land 时必须接到哪个引脚** ★
· ★**表里必须写清**: ★**`Q_AND`/`Q_PG` 与库序不一致 ⇒ 重画 land 时必须人工改映射 (接反 ⇒ Vgs 极性反 ⇒ 开机路径不通); `Q_ENVC` 天然对上** ★
· ★**另加一列**: ★**「如果落板批次想免重画 land ⇒ 需要选引脚序 = 占位 pad 序的器件 ⇒ 在售是否存在」** (★自己查官方在售目录; ★查不到就写 [0数据] + 降级方案=必须重画★) ★
· ★**充电板 `Q_CHG_LED` 也查一遍** (★它在充电板上 ⇒ 板文件里查无此位号 ⇒ 写「充电板侧, 板文件无占位 ⇒ 待 L4 定封装后核」★) ★
· ★**交付形态**: ★**新建 `HW/MOS_PAD_PIN_MAPPING.md` (或并进你判断合适的现有收口件, ★新建一个文件更清楚★) ★**

★★**③ L3: `D_ESD_CAM` 的 pad 序反了 (★只出改法映射, 不许改板★)** ★★
· ★**自己实读**: ★**`D_ESD_CAM` pad1=GND / pad2=CSI_D0_CK_P; `D_ESD_DEMO`/`D_ESD_USB_D` pad1=信号 / pad2=GND** ★
· ★**出改法映射**: ★**方案甲 = 落表时把两件的单向件换成双向件 (PESD5V0S1BA 等) ⇒ pad 序天然免疫** · ★**方案乙 = 保留单向件 (TPD1E05U06) ⇒ 落板批次必须对调 land 的 pad1/pad2** ★ ⇒ ★**两条都写代价, 一条不许代拍** ★
· ★**依据**: ★**TI TPD1E05U06 是单向件 (pin1=I/O · pin2=GND) ⇒ 按 pad 序号机械接 ⇒ I/O 接到 GND 位 ⇒ 器件不工作** ★ (★自己核手册★) ★

★★**④ L4 (G-8): 充电板 6 件器件的 footprint 候选清单 (★只出清单, 不许画板★)** ★★
· ★**6 件**: `D_ESD_TC` / `FB_VBUS` / `D_TVS_VBUS` / `Q_CHG_LED` / `D_CHG_LED` / `C_REGN` ⇒ ★**这 6 件在 BOM 里 footprint 栏是「待定」, 板文件里查无此位号** ★
· ★**每件给**: ★**候选封装 (≥2, 官方在售) · 焊盘数 · 本体尺寸 · 与占位/充电板面积约束的关系 · 出处链接 + 证据等级 · 降级方案** ★
  (★**充电板面积约束**: ★自己从 `HW/CHARGE_BOARD_SPEC.md` / `MECH_BUDGET` 里读出现在认的充电板尺寸, ★读不到就写 [0数据]★) ★
· ★**`C_REGN` 的 footprint 与 L1 同批落 (4.7µF 0603/0805 通用) ⇒ 交叉引用即可, 不重复论证** ★
· ★**`Q_CHG_LED` 是 N-MOS ⇒ 库里 SOT-23 是 G/S/D ⇒ 充电板上是新画 ⇒ 不存在 pad 序问题, 但要写清** ★

★★**⑤ 交卷单 + ⑥ 分片 + ⑦ 门禁** ★★
· ★**交卷单** `HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md` ⇒ ★**B1~B6 六块齐全** (B1 目标与范围 / B2 事实与数据 (每条带出处) / B3 改法映射 / B4 验收命令实跑输出 / B5 边界自证 / B6 留给 main 的待裁) ★
· ★**分片** `state/fragments/hw.yaml` ⇒ ★**走 `python3 state/frag_write.py` 原子写** ⇒ ★**只许加自己的 claim/need/artifact, 不许改别人的 key, 不许手改 yaml** ★
· ★**独立机器门禁** (★新建, 不许挂 md5, 判据不许放松★) ⇒ 至少 5 条断言:
  ① `C_REGN` 在网表/脚表/BOM 三处的 value 必须是 4.7µF 级且**带 10V 耐压标注** (★不许只写「4.7µF」——手册要 10 V rating★)
  ② `C_REGN` 的 opn 栏不许为空 (★空 = 采购单出不来★)
  ③ 落表台账里必须登记本单 (单号 + 三处改动) ⇒ 缺 = 红 (★防止「改了盘没留痕」★)
  ④ `HW/MOS_PAD_PIN_MAPPING.md` 必须存在且三件 MOS 都在表里 ⇒ 缺 = 红
  ⑤ 映射表里每件 MOS 必须同时写出「占位 pad 序」与「SOT-23 库引脚序」两个串 ⇒ 缺 = 红 (★防止表只抄一半★)
  · ★**`--selftest` 反向用例 ≥ 5 条, 每条必须自证「真的改到了目标」** (★例: 把 C_REGN 的 10V 标注删掉 ⇒ 期望红 C1; 把台账登记删掉 ⇒ 期望红 C3; 把映射表里 Q_PG 那行删掉 ⇒ 期望红 C4/C5★) ⇒ ★**不许出现「改了没生效」的假用例** ★

★★**验收命令 (全部必须 rc=0, 原样输出贴进交卷单)★★ ★★
★**`python3 HW/check_part_selection_matrix.py` (ISS-241 的门禁, 不许被本单改红) · `--selftest` · `python3 state/check_netlist.py` · `python3 state/check_netlist_pins.py` · `python3 state/check_sch_erc.py` · `python3 state/check_sch_pinfull.py` · `python3 HW/check_netlist_selfconsistency.py --expect-resolved` (★条数不许变多★) · `python3 state/merge.py && python3 state/gate_check.py` (★【Q1】18/18★) · ★**你自己新建的门禁 + `--selftest`** ★

★★**边界 (★逐条自证★)★★ ★★
★**零外发** (★老板 2026-11-12 02:02: 不再发信 / 不联系供应商 / 全靠自己查资料 ⇒ 你查资料只用 web_search / web_fetch / 带 --max-time 的 curl★) ·
★**不改 PROJECT_TRACKER.md §0** · ★**不写别的 agent 的分片** · ★**不碰 PCB 布线 / 布局 / 板框** (★板那一趟按老板 2026-11-11 10:07 排队★) ·
★**不改 `state/land_v_values.py`** (★那是 ISS-236 的一键落表器, 改它要 main 排期★) ·
★**不替老板拍板**: ★**V-2 (ESD 方案二选一) / V-3 / V-4 / G-1 (Q_PG 源漏拓扑) / W-1~W-6 一条不许代拍** ⇒ 只出选项 + 代价 ⇒ 交 main 排期 ·
★**实物 [实测] = 0 条** (本机无板) · ★**`state/issue_log.yaml` 不许自己改** (verify 留给 main) ★

★★**★注 (★main 2026-11-16 14:4x 追加★)★★**: ★**本单与 ISS-242 同属 hw-lead ⇒ 按铁律「一个 agent 同时只允许一个写会话」⇒ ISS-242 交卷签字前不许开跑** ★
★**⇒ 你拿到这张单时, 第一件事 = 先读盘 (`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 的当前内容 + md5) ⇒ ★**以盘上真源为准, 不要照抄本任务书里的行号/值** ★** ⇒ 再动手** ★
"""

# ---------------------------------------------------------------- ISS-244 新开
TITLE_244 = (
    "★★[主线内·硬件选型/官方口径侧·内部活] ★★ISS-241 缺口登记 G-1~G-10 的**自查补全** "
    "(★老板 2026-11-12 02:02 政策: 不再发信 · 全靠自己查资料★ ⇒ 每条要么补上证据, 要么写清降级方案, 不许挂「等回复」★) "
    "+ ★**21 件 OPN 回填清单** (每件: 落表时要改哪几行 · 需不需要改 footprint · 谁拍) "
    "⇒ ★**G-5 LED 1mA 工作点亮度 / G-3·G-4 差分单边 ESD / G-10 分压阻值 / G-1 Q_PG 源漏拓扑 四条最需要自查★**"
)

DESC_244 = (
    "★main 2026-11-16 14:3x~14:4x 自己实跑 + 逐行实读出来的 (★不是抄任何交卷报告★) ★\n"
    "★**① 任务来源**: ★**ISS-241 (sw-lead, 14:18 交卷, main 已复验落 verified) 的 §4 缺口登记 G-1~G-10** ⇒ ★**每条都写着「归谁」: "
    "G-1 ⇒ main/PM (Q_PG 源漏拓扑) · G-2 ⇒ hw-lead (板那一趟) · G-3/G-4 ⇒ PM (V-2 ESD 方案) · G-5 ⇒ PM/结构+落表批次 · G-6 ⇒ main (落表批次, ★**已另开 ISS-243★) · "
    "G-7 ⇒ hw-lead (板那一趟) · G-8 ⇒ main (充电板那一趟, ★**已并进 ISS-243 的 L4★) · G-9 ⇒ main (确认口径, ★**main 本轮已核: 22/22 完整★) · G-10 ⇒ 等原厂数据** ★\n"
    "★**② 病灶**: ★**10 条缺口里有 6 条其实【自己就能查资料补掉】, 现在却挂成「等回复/等拍板」⇒ 按老板 11-12 02:02 政策这不对** ★\n"
    "  · ★**G-5 (LED 亮度账)**: ★**`R_LED_G`/`R_LED_R` = 1 kΩ · 3.3 V ⇒ ≈1.1~1.3 mA, 而候选 LED 全是 20 mA 标称 ⇒ 1 mA 工作点亮度 [0数据]** ★\n"
    "    ⇒ ★**可自查的**: ★**查厂商是否给 Iv-vs-If 曲线 / 低电流档数据 (Kingbright KP-2012SGC · APT1608SURCK · AA1608SURSK) ⇒ 能查到就把 [0数据] 升成 [官网]; 查不到就写降级 (改串阻 ⇒ 属改网表 ⇒ 归落表批次)★** ★\n"
    "  · ★**G-3 / G-4 (差分单边 ESD)**: ★**CSI 只有 CK_P 单边有 ESD 位 · USB 只有 D+ 单边有 ESD 位** ★\n"
    "    ⇒ ★**可自查的**: ★**查 ESD 选型的行业依据 (USB 2.0 差分对单边保护的业界做法 / 厂商 app note) ⇒ 给 V-2 老板拍板提供依据** ★\n"
    "  · ★**G-10 (`R_SUPV_DIV1/2` 最终阻值)**: ★**归 U_SUPV (TPS3808G01 类) 的电压窗口** ⇒ ★**可自查的: 查原厂手册的窗口阈值 ⇒ 把「等原厂」变成「按官方窗口给候选值 + 标注窗口假设」** ★\n"
    "  · ★**G-1 (Q_PG 源漏拓扑)**: ★**可自查的: 查 P 沟道高边开关的标准拓扑 (源极=高电位侧) + 网表 note 原文逐字 ⇒ 把矛盾写成可判的两版原理图描述, 交 main/PM 拍** ★\n"
    "★**③ 本单要做的两件事**: ★**① G-1~G-10 逐条自查补全 (每条: 状态 / 证据等级 / 出处 / 降级方案 / 还差什么) ② 21 件 OPN 回填清单 (只出清单, 不落表)** ★"
)

BRIEF_244 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**ISS-241 登记的 10 条缺口 (G-1~G-10) 逐条自查补全**★ (★老板 2026-11-12 02:02 政策: **不再发信 · 全靠自己查资料** ⇒ 每条要么补上证据, 要么写清降级方案, 不许挂「等回复」★) + ★**出 21 件的 OPN 回填清单 (只出清单, 不落表)**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 14:3x~14:4x 自己实跑, 不是推测★)** ★★
· ★**ISS-241 已交卷 (14:18) 且 main 已复验落 verified** ⇒ ★**矩阵与 10 条缺口登记都在盘上**: `HW/PART_SELECTION_MATRIX_2026-11-16.md` §4 (★153057 B★) ★
· ★**main 实跑 `python3 HW/check_part_selection_matrix.py` ⇒ rc=0 (8/8)** · `--selftest` ⇒ rc=0 (9/9) ★
· ★**main 亲核覆盖度**: ★**BOM 待选型∩必装 = 23 件 ⇒ 减 `U_PWR_SW` (ISS-172 已办) = 22 件 ⇒ 矩阵 22/22 全覆盖, 零漏项** ★
· ★**main 实读 §4 缺口表**: ★**10 条里有 6 条标着「归 main / PM」或「等原厂」⇒ ★**按老板 11-12 02:02 政策, 「等回复」类的一律要自己查资料**★ ★

★★**① G-1~G-10 逐条自查补全 (★新建收口件★)** ★★
· ★**新建** `HW/PART_SELECTION_GAPS_CLOSEOUT.md` ⇒ ★**一张表, 每条缺口一行, 列 = 缺口 / 归谁 / ★**本轮自查结果**★ / 证据等级 / 出处(链接+页/章节) / 降级方案 / 还差什么 / 状态(已闭合/需老板拍/需落表/需等原厂)★ ★
· ★**每条都必须真查, 不许把原文抄一遍交差**: ★**抓取纪律 = `web_search` / `web_fetch` + 带 `--max-time` 的 curl** (★**本机上一轮 curl 挂死过 ⇒ 必须加 `--max-time`, 不许裸 curl★) ⇒ ★**厂商 PDF 可下载后用 `pdftotext` 实读** ★
· ★**四条重点缺口 (★这是本单的核心★)**:
  · ★**G-5 (LED 亮度账不匹配)**: ★**现状 = `R_LED_G`/`R_LED_R` 1 kΩ + 3.3 V ⇒ 实际 ≈1.1~1.3 mA, 而候选 LED (Kingbright KP-2012SGC / APT1608SURCK / AA1608SURSK) 全是 20 mA 标称 ⇒ 1 mA 工作点亮度 [0数据]** ★
    ⇒ ★**要做的**: ★**查厂商手册有没有 Iv-vs-If 曲线或低电流档 (≤2 mA) 的实测点 ⇒ 能查到 ⇒ 把 [0数据] 升成 [官网] + 给出 1 mA 档的推算亮度; 查不到 ⇒ 写清降级方案 (★**改串阻 = 改网表 ⇒ 归落表批次, 本单只出建议值 + 代价, 不落表★) ⇒ 并把「LED 实际亮度」登记为需老板拍的一项 (因为亮度直接关系到光生物安全白场辐亮度)** ★
  · ★**G-3 / G-4 (高速差分对与 USB 只有单边 ESD 位)**: ★**`D_ESD_CAM` 只保护 CK_P · `D_ESD_USB_D` 只保护 D+ ⇒ `CSI_D0_CK_N` / `D0~D3` 各 lane / `USB_D_N_SRC` 在网表上都没有 ESD 占位** ★
    ⇒ ★**要做的**: ★**查业界依据 (USB 2.0 差分对单边 ESD 保护的通行做法 / 半导体厂商 app note / ESD 器件选型手册) ⇒ 给「V-2 (ESD 方案二选一)」这条老板待拍项补上可引用的依据 + 代价 (单边 vs 双边 = 焊盘数 / 面积 / 结电容对上升沿的影响) ⇒ 只出依据 + 代价, 不代拍** ★
  · ★**G-1 (`Q_PG` 源漏拓扑与网表 note 相反)**: ★**网表 note 写「源极接 ON · 漏极接 BAT_SW」, 而 P 沟道高边开关应是 源极=高电位侧 (BAT_SW) / 漏极=负载侧 (ON) ⇒ 直译则 Vgs 极性定义反 (PG 低时 Vgs≈+3.3V 而非 −4.2V ⇒ 开机路径不通)** ★
    ⇒ ★**要做的**: ★**查原厂 P 沟道 MOSFET 手册的源漏定义 + 典型高边接法图 ⇒ 把两条可能的原理图写法各画成文字描述 (含 Vgs 符号方向) ⇒ 交 main/PM 拍; ★**本单不许改网表 note** ★
  · ★**G-10 (`R_SUPV_DIV1/2` 最终阻值)**: ★**现状 = 只给了 0 Ω 跳线件的 OPN, 给不出最终分压阻值 (TBD-02 原厂电压窗口未到)** ★
    ⇒ ★**要做的**: ★**查 U_SUPV 候选 (TPS3808G01 类) 官方手册的检测窗口阈值 ⇒ 按官方窗口反推分压比 ⇒ 给候选阻值 + 误差带 + 标注「窗口假设」⇒ 仍属需落表, 只出依据** ★
· ★**其余六条 (G-2 / G-6 / G-7 / G-8 / G-9)**: ★**G-6 已另开 ISS-243 (落表) · G-2/G-7 归板那一趟 · G-8 已并进 ISS-243 的 L4 · G-9 已由 main 核完 (22/22)** ⇒ ★**你这张表里要把这四条写成「已转单 / 已闭合 + 出处」, 不许重复论证** ★
· ★**不许做的事**: ★**改网表 / 脚表 / BOM 一个字** · ★**改板 / 布线 / 布局** · ★**改 ISS-241 的矩阵正文** (★只许在收口页引用它★) ★

★★**② 21 件 OPN 回填清单 (★只出清单, 不落表★)** ★★
· ★**新建** (或并进上面那份收口件) ⇒ ★**一行一件, 列 = 位号 / 矩阵里的推荐项(型号) / 证据等级 / ★**落表时要改哪几处** (★网表行号或 ref+net 锚点 / 脚表行 / BOM 行★) / ★**需不需要改 footprint** (★G-7: 绝大多数件的占位 land 与厂商 land 不重合 ⇒ 要改 land ⇒ 归板那一趟★) / **谁拍** / 状态★ ★
· ★**落表时的行号不许写死**: ★**写 ref+net 这样的稳定锚点, 并注明「行号会随落表漂移」** ★
· ★**交 main 排落表批次** (★**main 会把它并进 `state/land_v_values.py` 或另起一个落表器 — 那是 main 的活, 你不许改那个脚本★) ★

★★**③ 交卷单 + ④ 分片 + ⑤ 机器门禁** ★★
· ★**交卷单** `HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md` ⇒ ★**B1~B6 六块齐全** (B1 目标与范围 / B2 事实与数据 (每条带出处) / B3 十条缺口的逐条自查结果 / B4 OPN 回填清单 / B5 验收命令实跑输出 / B6 边界自证 + 留给 main 的待拍项) ★
· ★**分片** `state/fragments/sw.yaml` ⇒ ★**走 `python3 state/frag_write.py` 原子写** ⇒ ★**只许加自己的 claim/need/artifact, 不许改别人的 key, 不许手改 yaml** ★
· ★**独立机器门禁** (★新建, 不许挂 md5★) ⇒ 至少 6 条断言:
  ① ★**G-1~G-10 十条必须全部在收口页出现, 一条不许漏** (★缺一条 = 红★)
  ② ★**每条必须带状态 + 证据等级 + 出处 + 降级方案四栏** (★任一栏空 = 红★)
  ③ ★**证据等级只能是白名单 `[官网]/[实测]/[媒体]/[推算]/[0数据]`** (★写「[官方]」= 红, ★ISS-241 的 M5 反向用例就是这么打的★)
  ④ ★**不许出现「等回复 / 等原厂回信 / 待供应商确认」这类挂起措辞** (★老板 11-12 02:02 政策 ⇒ 出现 = 红; 确实查不到的必须写成「[0数据] + 降级方案」★)
  ⑤ ★**OPN 回填清单必须 22 件全在** (★以 BOM 待选型∩必装 − U_PWR_SW 为准; ★你必须自己跑 csv 统计, 不要抄数字★)
  ⑥ ★**清单每行必须带「落表锚点」字段且不许为空** (★防止落表时找不到改哪儿★)
  · ★**`--selftest` 反向用例 ≥ 5 条, 每条必须自证「真的改到了目标」** (★例: 删掉一条缺口 ⇒ 期望红 C1/C2; 把证据等级写成「[官方]」⇒ 期望红 C3; 写一句「等原厂回信」⇒ 期望红 C4; 清单里删一件 ⇒ 期望红 C5★) ⇒ ★**不许出现「改了没生效」的假用例** ★

★★**验收命令 (全部必须 rc=0, 原样输出贴进交卷单)★★ ★★
★**`python3 HW/check_part_selection_matrix.py` (ISS-241 的门禁, 不许被本单改红) · `--selftest` · `python3 state/merge.py && python3 state/gate_check.py` (★【Q1】18/18★) · ★**你自己新建的门禁 + `--selftest`** ★

★★**边界 (★逐条自证★)★★ ★★
★**零外发** (★老板 2026-11-12 02:02: 不再发信 / 不联系供应商 / 不下单 ⇒ 你查资料只用 web_search / web_fetch / 带 --max-time 的 curl★) ·
★**不改 PROJECT_TRACKER.md §0** · ★**不写别的 agent 的分片** · ★**不碰 PCB 布线 / 布局 / 板框** ·
★**不改网表 / 脚表 / BOM 一个字** (★本单只出清单 + 依据, 落表归 main 排期★) ·
★**不改 ISS-241 的矩阵正文与门禁脚本** ·
★**不替老板拍板**: ★**V-2 / V-3 / V-4 / G-1 (Q_PG 源漏拓扑) / LED 亮度档 一条不许代拍** ⇒ 只出依据 + 代价 ⇒ 交 main ★
★**实物 [实测] = 0 条** (本机无板) · ★**`state/issue_log.yaml` 不许自己改** (verify 留给 main) ★
"""


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(IL, IL + ".bak_20261116_1440_verify241_open243_244")

    lf = open(IL_LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        issues = il.get("issues") or []

        # --- ① ISS-241 落 verified
        hit = 0
        for it in issues:
            if it.get("id") == "ISS-241":
                it["status"] = "verified"
                it["verify_by"] = "main"
                it["verify_date"] = TODAY
                it["verify_result"] = VERIFY_241
                it["note"] = (it.get("note") or "") + NOTE_241
                hit += 1
        if hit != 1:
            raise SystemExit("★ISS-241 命中数异常 (%s) ⇒ 中止" % hit)

        # --- ② 新开 ISS-243 / ISS-244
        existing = {it.get("id") for it in issues}
        for iid in ("ISS-243", "ISS-244"):
            if iid in existing:
                raise SystemExit("★%s 已存在 ⇒ 中止 (不重复开)" % iid)

        issues.append({
            "id": "ISS-243",
            "title": TITLE_243,
            "severity": "high",
            "source_blocker": "ISS-241",
            "source_agent": "main",
            "desc": DESC_243,
            "owner": "hw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": (
                "★2026-11-16 14:4x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = ISS-241 (sw-lead, 14:18 交卷) 交卷时点名交回硬件侧的 4 条落表前置** "
                "(★L1/G-6 `C_REGN` 1µF vs TI 官方 4.7µF(10V) ⇒ ★**官方硬要求, 无需老板拍板, 可直接落**★ · "
                "L2/G-2 三件 MOS 占位 pad 序 ≠ 库引脚序 ⇒ 出映射表 · L3 `D_ESD_CAM` pad 反序 ⇒ 出改法 · L4/G-8 充电板 6 件 footprint 待定 ⇒ 出清单★) "
                "⇒ ★**排队不派 (hw-lead 名额被 ISS-242 占着, 会话 status=running · 14:18 还在写分片 ⇒ 真在飞)** ⇒ 等 ISS-242 交卷签字后由 advance.py 自动可派 ★"
            ),
            "dispatched_at": None,
            "task_brief": BRIEF_243,
        })

        issues.append({
            "id": "ISS-244",
            "title": TITLE_244,
            "severity": "high",
            "source_blocker": "ISS-241",
            "source_agent": "main",
            "desc": DESC_244,
            "owner": "sw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": (
                "★2026-11-16 14:4x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = ISS-241 §4 的 10 条缺口登记 + 老板 2026-11-12 02:02 政策「不再发信, 全靠自己查资料」** "
                "(★10 条里 6 条标着「归 main/PM」或「等原厂」⇒ 按政策必须自己查资料补掉, 不许挂「等回复」★ · "
                "重点 = G-5 LED 1mA 工作点亮度 [0数据] · G-3/G-4 差分单边 ESD · G-10 分压阻值 · G-1 Q_PG 源漏拓扑★) "
                "⇒ ★**本轮可派 (sw-lead 名额因 ISS-241 落 verified 已释放)** ⇒ 已派 (见 dispatch_log) ★"
            ),
            "dispatched_at": None,
            "task_brief": BRIEF_244,
        })

        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()

    print("   - ISS-241 → verified (main 亲核签字: 门禁 8/8 + selftest 9/9 + 覆盖度亲核 22/22)")
    print("   - ISS-243 新开 (hw-lead · 落表前置 L1~L4 · 排队等 ISS-242)")
    print("   - ISS-244 新开 (sw-lead · 缺口 G-1~G-10 自查补全 + OPN 回填清单)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
