#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0725_verify233_234_open235_236.py
★main (moli) 清账 + 开新单 · 2026-11-16 07:2x (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★本轮自己实跑, 不抄任何交卷报告★)** ★★
· ★**ISS-233 (hw-lead) 子会话** `agent:hw-lead:subagent:bef90f83` ★**status=done** ★ (交卷 07:01)
  ⇒ ★**main 本轮自己实跑 8 道闸** ⇒ 落 `verified` ⇒ **放掉 hw-lead 名额** ★
· ★**ISS-234 (sw-lead) 子会话** `agent:sw-lead:subagent:106168f5` ★**status=done** ★ (交卷 07:02)
  ⇒ ★**main 本轮自己实跑新门禁 + 旧门禁** ⇒ 落 `verified` ⇒ **放掉 sw-lead 名额** ★
· ★**ISS-229 (mech-lead) 子会话** `agent:mech-lead:subagent:61bfde5f` ★**status=running** ★
  ⇒ ★**不碰 (还在跑) ⇒ mech-lead 名额本轮空着** ★

★★**本轮新开 2 条 (★都是「原理图 / 网表 / 门禁 / 软件-接口」主线活, 一条都不碰 PCB 布线布局★)** ★★
· ★**ISS-235 (sw-lead)**: ★**ISS-233 落表把 SW 侧 3 条断言打成过期红** (timing_check F8 / REV-3 · demo_panel_spec REV-12)
  ⇒ ★**订正这 3 条 (不是放宽判据) + 每条补反向自证** ★
· ★**ISS-236 (hw-lead)**: ★**把 ISS-233 的【拍板即落清单】做成参数化一键落表器 (V-2/V-3/V-4) + 出【原理图定稿收口清单】** ★
  ⇒ ★**老板一拍板 = 一条命令落表, 不再起一个 2 小时 agent 周期** ★

★★**边界 (本轮共同)★★ ★★
★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ★
★**不许替老板拍板** ⇒ V-2 / V-3 / V-4 / 关机语义 全部只出选项 + 量化代价, 不代拍 ★
★**不许碰 PCB 布线 / 布局 / 板框** ⇒ 板侧 8 项 (B-1~B-8) 继续**排队**, 本 job 不派 ★
★**不改 PROJECT_TRACKER.md §0 锁死表** · ★**不写别人的分片** · ★**不发邮件 / 不联系供应商 / 不下采购单** ★
★**不调 message 工具** (微信通道 2026-11-11 10:17 已删) ★
"""
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

# =====================================================================
# ISS-233 / ISS-234 的 verify_result (★全是 main 本轮自己实跑的输出★)
# =====================================================================
V233 = (
    "★main 2026-11-16 07:2x 自己实跑 (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**A 类落表真的落地了**: ★**`--expect-resolved` 21 → 18 条** (★main 07:2x 实跑 `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, **18 条未落表**★) ⇒ ★**落表 3 条 = R3 的网表侧 (表A L442 / 脚表 L531 / BOM L208 各一行, 给 `U_EN_SW` 补器件本体行)★** ⇒ ★**其余 18 条逐条归因 (V-3 13 条 / V-2+板 3 条 / V-4 1 条 / 板侧 R3 1 条) 交卷单 §1 已逐条写死★**\n"
    "· ★**A 类判据成立 (★硬判据: 改了任一 V 值要不要回退? ⇒ 要回退 ⇒ 不许落★)**: ★**B 类 14 条 (V-3 13 + V-4 1) 一条没落 · C 类 4 条 (板侧 3 + R3 板封装 Value 1) 一条没落** ★ ⇒ ★**老板没拍的 V 值一个没落** ★\n"
    "· ★**门禁 8 道全绿 (main 07:2x 实跑)**: `HW/check_netlist_selfconsistency.py` rc=0 · `--selftest` rc=0 (**21/21 通过**, 含 ISS-230 新增用例19/20) · `state/check_netlist.py` rc=0 · `state/check_netlist_pins.py` rc=0 · `state/check_sch_erc.py` rc=0 (**ERC = 0**) · `state/check_sch_pinfull.py` rc=0 (**图上 584 脚 = 表里 584 脚 · K=0 · 218 器件/153 网**) · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (**Q1 18/18**) ★\n"
    "· ★**md5 (main 07:2x 实测)**: 网表 `3215020b…` → **`34132f7e40a241e1fae1476be0eafbd5`** · 脚表 `a600afae…` → **`b21b743a7702d30729f0d653c15392df`** · BOM `92b51580…` → **`c195a117ff17490d4d1e1a5b8f1995a7`** (★**只有 L208 一行: `U_EN_SW` procurement 由「待分类」变「已定型-IC」⇒ 这颗不再是伪物料★**) · 板 `611b869e…` ★**逐字节不变** · `.kicad_pro` `3e504d2b…` ★**逐字节不变** ★\n"
    "· ★**交付物在盘**: 交卷单 `HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md` (**52730 B**, mtime 07:01) · 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §15 (mtime 06:50) · 分片 `state/fragments/hw.yaml` (mtime 07:00) ★\n"
    "· ★**下游连锁已按设计生效**: ★**SW 侧 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点已由 ISS-234 走 H-1 重锚 (md5 `34132f7e…` / prev `3215020b…` / by ISS-233 + R-05 留痕) ⇒ `check_demo_panel_spec.py` rc=0 (R1~R7)★**\n"
    "· ⚠️ ★**但落表把 SW 侧 3 条断言打成过期红 (★不是「把红灯调没」, 是「断言写的是旧事实」★)**: ★**① `SW/tools/timing_check.py` F8 (L1463) 断言「`U_EN_SW` 在网表里没有器件行」⇒ 现在有器件行 (L442 type=IC) ⇒ 红** ★ · ★**② 同文件 REV-3 (L1484) 基线 `rail_switching_devices == 1` ⇒ 现在网表里负载开关 = 2 颗 ⇒ 红** ★ · ★**③ `SW/tools/check_demo_panel_spec.py` REV-12 (L502-506) 硬编码落表单号「ISS-220」⇒ 台账当前已是 ISS-233 ⇒ 这条反向用例改不到目标 ⇒ `--selftest` 15/16 (★「有断言 ≠ 断言有效」· ISS-227 同款教训★)★** ⇒ ★**已开 ISS-235 给 sw-lead 订正 (★本单不许代改 SW 地界★)** ★\n"
    "· ★**零外发** · ★**实物 [实测] = 0 条** · ★**没碰板 / 没碰布线布局 / 没改 SW MECH / 没改 PROJECT_TRACKER §0 / 没自签本条 (verify_by = main)★** ★"
)

V234 = (
    "★main 2026-11-16 07:2x 自己实跑 (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**新门禁实跑**: `python3 SW/tools/check_shutdown_semantics.py` ⇒ rc=0 (**R1~R7 全过** · 口径页/HW 文档/SW 镜像/网表 四方一致 · 开关候选 14 颗 · 整机割边 = ['U_PWR_SW'] · demo 割边 = 空) · `--selftest` ⇒ rc=0 (**17/17 全红**) ★\n"
    "· ★**旧门禁实跑**: `SW/tools/check_demo_panel_spec.py` ⇒ rc=0 (R1~R7) · `SW/tools/timing_check.py` ⇒ **rc=1 (68/70)** ⇒ ★**唯一 2 条红 = ISS-233 落表后过期的断言 (F8 器件行 / REV-3 基线 1→2) ⇒ 已开 ISS-235** ★ · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18) ★\n"
    "· ★**H-1 重锚已按设计走完**: `SW/SW_MD5_BASELINE_LEDGER.md` §1 `entries[]` 的 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 两条 = md5 `34132f7e…` / `b21b743a…` / prev `3215020b…` / `a600afae…` / **by ISS-233** + §1 `landing_records` 加 ISS-233 交接单位置 + §3 **R-05 留痕** ⇒ ★**R6 三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 绿** ★\n"
    "· ★**交卷自报「派单前提有误」, main 复核成立**: ★**main 逐行实读 `HW/netlist_v1.csv` ⇒ `U_PWR_SW` 本体行在 L50 (type=IC) + `U_EN_SW` 本体行在 L442 (type=IC) ⇒ 网表里负载开关 = 2 颗, 不是派单书说的 0 颗** ★ ⇒ ★**但交卷的方向性结论仍成立 (demo 板做不到真断电) ⇒ 真实原因换成 ①整机电池链全 DNP (`U_PWR_SW` 的 VIN 无源) ②demo 的 SoM 供电路径 `RAIL_DEMO_5V`→`J_SOM_P3` 7 根 VCC_DCIN 上零开关 ⇒ SoM 永远带电** ★\n"
    "· ★**交付物在盘**: `SW/SHUTDOWN_SEMANTICS_SPEC.md` (**41994 B**, 07:02 · 六格矩阵 + 2×2 方案表 + 给老板 5 条 + 机器可读基准块) · `SW/tools/check_shutdown_semantics.py` (**36101 B**, 06:57) · 交卷单 `HANDOFF/2026-11-16_sw-lead_ISS234_关机语义三口径方案与门禁.md` (**34272 B**, 07:02 · B1~B6) · 分片 `state/fragments/sw.yaml` (07:01) ★\n"
    "· ★**两处 HW 口径冲突 (交卷单 B5 U-B, 本单如实标出)**: ★**① 待机 0.15W 的温度 45.9-46.9°C vs `HW/POWER_SHUTDOWN_V3.md` §6 的 41.6-42.6°C (后者是 0.05W 口径) ② VBUS_DET 50µA 与文中 100k+100k 算式对不上 (5V/200k=25µA; 现行网表 1M+1M) ⇒ 已并进决策页, 不代裁** ★\n"
    "· ★**零外发** · ★**实物 [实测] = 0 条** · ★**没改 HW/ MECH/ · 没改 issue_log (verify_by = main)· 没碰 PCB** ★"
)

# =====================================================================
# 新开 ISS-235 (sw-lead)
# =====================================================================
TITLE_235 = ("★★[主线内·软件/接口侧·内部活] ★**ISS-233 落表把 SW 侧 3 条断言打成过期红** ⇒ 订正 "
             "`timing_check.py` F8 / REV-3 + `check_demo_panel_spec.py` REV-12 (★订正不是放宽★) + 每条补反向自证 ⇒ SW 门禁回全绿")

DESC_235 = (
    "★**main 2026-11-16 07:2x 自己实跑 (不是抄交卷报告)**:\n"
    "· ★**ISS-233 落表第 3 批 (2026-11-16 06:48:38) 改了网表 L442** (★给 `U_EN_SW` 补器件本体行: type NET→IC, value → `TPS22991RAA (…)` 器件身份描述★) + 脚表 L531 + BOM L208 ⇒ "
    "网表 md5 `3215020b…` → `34132f7e…` · 脚表 `a600afae…` → `b21b743a…` · BOM `92b51580…` → `c195a117…` · 板 `611b869e…` / `.kicad_pro` `3e504d2b…` ★**逐字节不变** ★\n"
    "· ★**⇒ `python3 SW/tools/timing_check.py` 现在 rc=1 (selftest 68/70)**, 2 条红:\n"
    "  ① ★**F8 实读 (L1463)**: 判据条件 `load_switch_without_device_row == [\"U_EN_SW\"]` (★断言「`U_EN_SW` 在网表里**没有器件行** ⇒ BOM/装配单会漏掉这颗开关」★) ⇒ ★**现在 `U_EN_SW` 有器件行 (网表 L442, type=IC) ⇒ 这条断言写的是旧事实 ⇒ 过期** ★\n"
    "  ② ★**REV-3 反向 (L1484)**: 基线 `rail_switching_devices == 1` (★删掉 `U_PWR_SW` 后必须掉到 0★) ⇒ ★**现在网表里负载开关 = 2 颗 (`U_PWR_SW` L50 + `U_EN_SW` L442) ⇒ 删掉 1 颗掉到 1, 不是 0 ⇒ 过期** ★\n"
    "· ★**⇒ `python3 SW/tools/check_demo_panel_spec.py` 主体 rc=0 (R1~R7) 但 `--selftest` 15/16**, 红的正是 ★**REV-12 (L502-506): 它把落表台账里的「ISS-220」改成「ISS-999」来验证 R6 会红, 但台账当前落表单号已经是 ISS-233 ⇒ 这条反向用例改不到目标 ⇒ 「有断言 ≠ 断言有效」(★ISS-227 同款教训★)** ★\n"
    "· ★**这 3 条红不是「红灯被调没」的反面, 是「断言写死了旧事实」⇒ 修法 = 把断言改成跟当前真源走 + 每条配一条真的能改到目标的反向用例** ★\n"
    "· ★**★这 3 条红的源头是本项目自己的合法落表 (ISS-233) ⇒ 修在 SW 侧脚本, 不许回头改网表 (那会把 ISS-233 的 A 类落表变成回退)★** ★"
)

BRIEF_235 = """★★**目标 (★内部活·软件/接口侧·不是 PCB 类·不是老板级拍板★)** ★★
★**把 ISS-233 落表后打红的 3 条 SW 侧过期断言订正成【跟当前真源走】的断言, 并给每一条补一条【真的改得到目标】的反向用例 ⇒ SW 门禁回全绿** ★★
⇒ ★**目标状态: `timing_check.py` rc=0 且 selftest 70/70 · `check_demo_panel_spec.py` rc=0 且 selftest 16/16 · `check_shutdown_semantics.py` rc=0 且 selftest 17/17 · `merge + gate_check` rc=0 · 受保护 md5 逐字节不变** ★★

★★**为什么是现在 (★main 2026-11-16 07:2x 自己实跑, 不是抄交卷报告★)** ★★
· ★**ISS-233 (hw-lead) 落表第 3 批 (2026-11-16 06:48:38) 改了网表 L442** (给 `U_EN_SW` 补器件本体行: type NET→IC) + 脚表 L531 + BOM L208 ⇒ ★**网表 md5 `3215020b…` → `34132f7e…` · 脚表 `a600afae…` → `b21b743a…` · BOM `92b51580…` → `c195a117…`; 板 `611b869e…` / `.kicad_pro` `3e504d2b…` 逐字节不变** ★
· ★**main 实跑 `python3 SW/tools/timing_check.py` ⇒ rc=1 (selftest 68/70)** ★ (★这 2 条红就是 ISS-233 交卷单 B5 U-D 里点名要 main 授权的那 2 条★)
· ★**main 实跑 `python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=0 (R1~R7)** ★ · ★**`--selftest` ⇒ 15/16** ★ (★红的是 REV-12★)
· ★**main 实跑 `python3 SW/tools/check_shutdown_semantics.py` ⇒ rc=0 (R1~R7)** ★ · ★**`--selftest` ⇒ 17/17** ★
· ★**★这 3 条红的性质 = 【断言写死了旧事实】(★不是判据错, 是真源变了断言没跟★) ⇒ 修法 = 订正断言 + 补反向自证; ★**不许回头改网表** (那等于把 ISS-233 的 A 类落表回退掉)★** ★

★★**你要做的 (★三件事, 一件都不能少★)** ★★
① ★**订正 3 条过期断言 (★订正, 不是放宽★)**
  · ★**F8 (L1463)**: 现在的判据是「`load_switch_without_device_row == [\"U_EN_SW\"]`」⇒ ★**翻成正向断言: `U_PWR_SW` 与 `U_EN_SW` 都必须有器件行 (★`load_switch_without_device_row == []` 且两个 ref 都在 `load_switch_refs` 里★) ⇒ 语义 = 「BOM/装配单不许漏掉任何一颗负载开关」** ★ ⇒ ★**同时把对应的反向用例改成: 把 `U_EN_SW` 的器件本体行删掉 (★在 /tmp 临时树上删★) ⇒ 必须红** ★
  · ★**REV-3 (L1484)**: 基线 `rail_switching_devices` ★**1 → 2** (★网表里现在就是 2 颗★) ⇒ 删掉 `U_PWR_SW` 后必须掉到 ★**1** (★不是 0★) ⇒ ★**REV-3b (两个都删 ⇒ 0) 保持不变** ★
  · ★**REV-12 (`check_demo_panel_spec.py` L502-506)**: ★**不许硬编码「ISS-220」** ⇒ ★**改成按台账里【当前的落表单号】动态定位** (★从 §1 锚点块 / 落表台账里读出来再改坏★) ⇒ ★**改坏 ⇒ R6 必须红** ★
② ★**每一条都要【反向自证】(★必做, 且必须自证「真的改到了目标」★)**
  · ★**在 /tmp 临时树上做 (★不许碰真盘★)**: 改坏 ⇒ 必须红; 改回 ⇒ 必须回绿 ★
  · ★**★判别标准: 「红」必须是【目标那条判据】红, 不是别的条红 (★ISS-227 的教训: 有断言 ≠ 断言有效★)** ★
  · ★**每条新判据至少配 1 条反向用例; ★**反向用例必须自带「我确实改到了目标」的断言 (★例如 REV-12 改完后先断言台账里 ISS-233 已变成 ISS-999★)** ★
③ ★**交卷 4 件**
  · ★**新建 `HANDOFF/2026-11-16_sw-lead_ISS235_SW侧3条过期断言订正.md`** (★B1~B6 六块齐全★) ★
  · ★**分片 `state/fragments/sw.yaml`** ⇒ ★**必须走 `python3 state/frag_write.py` 原子写 (★不许 `open(p,\"w\")`★)** ⇒ ★**不许删别人的条目** ★
  · ★**交卷前最后一步: 把所有门禁实跑输出原样贴进交接单 (★不许只写「全绿」三个字★)** ★

★★**边界 (★越界即无效★)** ★★
· ★**不许改 `HW/` (★网表 / 脚表 / BOM / 落表台账 一个字节都不许碰★)** ⇒ ★**交卷时必须实测这 5 个 md5 逐字节不变: 网表 `34132f7e40a241e1fae1476be0eafbd5` · 脚表 `b21b743a7702d30729f0d653c15392df` · BOM `c195a117ff17490d4d1e1a5b8f1995a7` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`** ★
· ★**不许改 `MECH/`** · ★**不许碰 PCB / 布线 / 布局** ★
· ★**不许把断言改成「永远绿」** (★比如加 `or True` / 把判据条件放宽成「非空即过」/ 把 `--skip-md5` 设成默认跳过★) ⇒ ★**判据强度不许比现在弱** ★
· ★**不许改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不许改 `PROJECT_TRACKER.md` §0** · ★**不许写别人的分片** · ★**零外发** · ★**实物 [实测] = 0 条** ★

★★**验收命令 (★交卷时逐条实跑并贴输出★)** ★★
```
python3 SW/tools/timing_check.py                  # ★rc=0 且 selftest 70/70★
python3 SW/tools/check_demo_panel_spec.py          # ★rc=0 (R1~R7)★
python3 SW/tools/check_demo_panel_spec.py --selftest # ★rc=0 且 16/16★
python3 SW/tools/check_shutdown_semantics.py       # ★rc=0 (R1~R7)★
python3 SW/tools/check_shutdown_semantics.py --selftest # ★rc=0 且 17/17★
python3 state/merge.py && python3 state/gate_check.py # ★rc=0 (Q1 18/18)★
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```
★**★反向自证清单 (★每条都要有「改坏 ⇒ 红 ⇒ 改回 ⇒ 绿」的完整记录★)★**
1. ★**F8**: 把 `U_EN_SW` 的器件本体行删掉 ⇒ 必须红 (「有负载开关没器件行」) ★
2. ★**REV-3**: 删掉 `U_PWR_SW` ⇒ 开关数必须掉到 1 (★不是 0★); 再删 `U_EN_SW` ⇒ 必须掉到 0 ★
3. ★**REV-12**: 把落表台账里【当前的】落表单号改坏 ⇒ R6 必须红; 改回 ⇒ 必须绿 ★
"""

# =====================================================================
# 新开 ISS-236 (hw-lead)
# =====================================================================
TITLE_236 = ("★★[主线内·原理图/网表侧·内部活] ★**把 ISS-233 的【拍板即落清单】做成参数化【一键落表器】(V-2 / V-3 / V-4)** "
             "⇒ ★**老板拍板 = 一条命令落表 (默认 dry-run·不落任何值)** ★ + 出【原理图定稿收口清单】(★还差什么才能定稿★)")

DESC_236 = (
    "★**main 2026-11-16 07:2x 自己实跑 (不是抄交卷报告)**:\n"
    "· ★**`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, 18 条未落表** (★ISS-233 落 A 类 3 条后由 21 条降到 18 条★) ⇒ ★**构成: V-3 13 条 (R2×11 + R7 + R8) · V-2+板 3 条 (R4×2 + R9) · V-4 1 条 (R10) · 板侧 R3 1 条 (板封装 Value)** ★\n"
    "· ★**这 18 条现在全部卡在「老板拍 V 值」或「板那一趟」⇒ 板那一趟按老板 11-11 10:07 口径排队 ⇒ ⇒ 真正能解开的只有 V-2 / V-3 / V-4 三个值** ★\n"
    "· ★**ISS-233 交卷单 §3 已给出【老板回一个字母就能落】的逐字清单 (文件 + 行号 + 旧值 + 新值)★ ⇒ ★**但落表仍要起一个 2 小时的 agent 周期, 而周期里最容易出的事就是「手改改错一行 / 忘了改门禁锚点 / 忘了登台账」** ★\n"
    "· ★**⇒ 本单把它做成【参数化落表器】: 默认 dry-run 只打印逐字 diff; 必须带 `--apply` + `--boss-decision` 才允许落; 落完自动跑门禁并把新 md5 打到 stdout (供 SW/MECH 走 H-1 重锚)** ★\n"
    "· ★**另附一件**: ★**【原理图定稿收口清单】** ⇒ 老板一眼能看到「还差什么才能定稿」(18 条 + 板侧 8 项 + 3 个 V 值, 每条写解锁动作与责任方) ★"
)

BRIEF_236 = """★★**目标 (★内部活·原理图/网表侧·不是 PCB 布线布局类·★不许替老板拍板★)** ★★
★**把 ISS-233 交卷单 §3 的【V-2 / V-3 / V-4 拍板即可一键落】逐字清单, 做成一个【参数化落表器】+ 一份【原理图定稿收口清单】** ★★
⇒ ★**目标状态: 老板拍完 A1/A2/A3 后, 一条命令把 V 值落进网表/脚表/BOM + 落表台账 + 门禁锚点, 并把新 md5 打到 stdout (供 SW/MECH 走 H-1 重锚); ★**而在你交卷这一刻, 盘上一个 V 值都不许被落** ★★

★★**为什么是现在 (★main 2026-11-16 07:2x 自己实跑, 不是抄交卷报告★)** ★★
· ★**main 实跑 `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, ★**18 条未落表**★ (★ISS-233 落 A 类 3 条后由 21 条降下来的★) ★
· ★**构成 (★ISS-233 交卷单 §1 逐条归因, main 复核过条数★)**: ★**V-3 13 条 (R2×11 + R7 + R8) · V-2+板 3 条 (R4×2 + R9) · V-4 1 条 (R10) · 板侧 R3 1 条 (板封装 Value)** ★
· ★**⇒ 18 条里, 板那一趟能解的只有 4 条 (★按老板 11-11 10:07 口径「PCB 布线/布局类不派, 排队等原理图定稿」⇒ 本 job 不派★); ★**真正只等老板一句话的是 V-2 / V-3 / V-4 三个值** ★**
· ★**ISS-233 交卷单 §3 已有逐字清单 (★文件 + 行号 + 旧值 + 新值 + 影响面 + 谁要重锚★) ⇒ ★**本单不是重新做一遍清单, 是把那份清单【变成能跑的东西】** ★
· ★**★落表是本项目最容易出事的一步 (★历史上出过「改了网表忘了改门禁锚点」「改了行号忘了改 SPEC 锚点」「忘了删 `DEMO_DNP` 白名单」★) ⇒ ★**本单的价值 = 把这一步变成一条有自检、有留痕、有回滚的命令** ★

★★**你要做的 (★两件交付物, 少一件即无效★)** ★★
① ★**参数化一键落表器 (★建议 `state/land_v_values.py`★)** ★
  · ★**取值白名单写死 (★不许自由字符串★)**: ★**V-3 ∈ {E, A, D, DEG4}** (★E = 100k+60k+100nF ★· A = 2.0M+1.2M · D = 2.0M+1.0M · DEG4 = 降级④「BAT_DET 链保持 DNP, 网表一格不改」★) · ★**V-4 ∈ {680, 470, 390}** (★Ω★) · ★**V-2 ∈ {1, 2}** (★1 = 网表侧+板侧两段走 · 2 = 只落网表侧 (★ISS-230 实测是假绿 ⇒ 必须打回, 不许当正路★)★) ★
  · ★**默认 dry-run (★不带 `--apply` ⇒ 零写盘★)**: 打印 ★**逐字 diff (文件 + 行号 + 旧值 + 新值) + 预期 `--expect-resolved` 条数变化 + 要连带改的台账/锚点清单 + 会要谁走 H-1 重锚** ★
  · ★**带 `--apply` 才允许落, 且必须同时带 `--boss-decision "<日期> <A1|A2|A3> = <值>"` ⇒ 缺这条 ⇒ ★**拒绝执行并退出非零** (★这就是「不许替老板拍板」的机器化保证★) ★
  · ★**落表必须复用 ISS-220 / ISS-223 / ISS-233 的既有流程 (★逐条照抄那三批的落法★)**: ★**网表 + 脚表 + BOM + `HW/SCHEMATIC_LANDING_V1_LANDED.md` 新段 (单号 + 文件名 + 新旧 md5) + `HW/check_netlist_selfconsistency.py` 的 EXPECT 与 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 锚点表逐字一致** ★
  · ★**★两个必须写进去的坑 (★ISS-230 交卷实测结论★)**: ★**① V-3 落表必须同时删 `state/gen_netlist.py` 的 `DEMO_DNP` 3 行 (★只改阻值永远还是 DNP★) ② 生成顺序必须是 `gen_netlist.py` → `gen_kicad_net.py` → `gen_netlist_pins.py` (★脚表脚号来自 `.net`, 顺序错了 V-2 的 pin3 出不来★)** ★
  · ★**落完必须实跑并输出**: ★**`--expect-resolved` (条数应 ↓) · `check_netlist_selfconsistency.py` rc=0 · `--selftest` 21/21 · 四道尺子 (`check_netlist.py` / `check_netlist_pins.py` / `check_sch_erc.py` / `check_sch_pinfull.py`) 全 rc=0 · `state/merge.py && state/gate_check.py` rc=0 + ★**把网表/脚表/BOM 的新 md5 打到 stdout** (供 sw-lead / mech-lead 走 H-1 重锚)★** ★
② ★**【原理图定稿收口清单】(★建议 `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md`★)** ★
  · ★**一张表, 逐条列**: ★**18 条未落表 (逐条: 条目 id + 阻塞原因 + 解锁动作 + 责任方 [boss / 板那一趟 / hw-lead] + 落表后期望 `--expect-resolved` 条数) + 板侧 B-1~B-8 (★只列, 标明「排队等原理图定稿」★) + 三个 V 值 (V-2 / V-3 / V-4) 的取值选项与代价 (★照抄 ISS-233 §3, 不改一个字★)** ★
  · ★**结尾必须有一行【还差什么才能定稿】的总数 (★例如: 老板 3 个值 → 板那一趟 8 项 → 定稿★)** ★

★★**★必须做的反向自证 (★缺一条即无效★)★** ★★
① ★**dry-run 跑一遍 ⇒ 盘上 5 个 md5 逐字节不变** (★网表 `34132f7e40a241e1fae1476be0eafbd5` · 脚表 `b21b743a7702d30729f0d653c15392df` · BOM `c195a117ff17490d4d1e1a5b8f1995a7` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`★) ⇒ ★**证明「默认不落」** ★
② ★**非法取值 (例如 `--decision V-3=E2`) 必须报错退出 (非零 rc) 且零写盘** ⇒ ★**证明「白名单守得住」** ★
③ ★**★在 /tmp 副本上真落一次 V-3=E ⇒ `--expect-resolved` 条数真的少 13 条 ⇒ 然后把 /tmp 副本还原 ⇒ ★**真盘一个 V 值都不许被落** ★** ⇒ ★**这条是本单的核心自证: 证明「这套流程真能一键落」, 又证明「本单没落」** ★
④ ★**★每条反向自证都要贴实跑输出, 不许只写结论** ★

★★**边界 (★越界即无效★)** ★★
· ★**★不许落任何 V 值 (V-2 / V-3 / V-4 老板都没拍) ⇒ 脚本默认 dry-run, `--apply` 必须带 `--boss-decision`★** ★
· ★**不许碰板** (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` / 布线 / 布局 / 板框 一律不碰★) ⇒ ★**板侧 B-1~B-8 继续排队** ★
· ★**不改 `SW/`** · ★**不改 `MECH/`** (★except 登记 need★) ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不改 `DECISION_PENDING_2026-11-16.md`** (★决策页由 main 统一更新★) ★
· ★**不许写别人的分片** · ★**零外发** · ★**实物 [实测] = 0 条** ★

★★**验收命令 (★交卷时逐条实跑并贴输出★)** ★★
```
python3 HW/check_netlist_selfconsistency.py            # rc=0
python3 HW/check_netlist_selfconsistency.py --selftest # rc=0 · 21/21
python3 HW/check_netlist_selfconsistency.py --expect-resolved # rc=1 · 18 条 (★不变★)
python3 state/check_netlist.py && python3 state/check_netlist_pins.py # rc=0
python3 state/check_sch_erc.py && python3 state/check_sch_pinfull.py  # rc=0 (ERC=0 · 584=584)
python3 state/merge.py && python3 state/gate_check.py   # rc=0 (Q1 18/18)
python3 state/land_v_values.py --decision V-3=E         # ★dry-run: 只打印 diff, 零写盘★
python3 state/land_v_values.py --decision V-3=E2        # ★必须报错退出★
```
"""


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    by_id = {i.get("id"): i for i in log["issues"]}

    # ---------------- ISS-233 → verified ----------------
    i233 = by_id["ISS-233"]
    assert i233.get("status") == "fixing", i233.get("status")
    i233["status"] = "verified"
    i233["verify_by"] = "main"
    i233["verify_date"] = TODAY
    i233["verify_result"] = V233
    i233["fix_ref"] = "HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md"
    i233["note"] = (i233.get("note") or "") + (
        "\n2026-11-16 07:2x ★**main 实跑 8 道闸 (含 `--expect-resolved` 21→18) ⇒ 落 verified** ★ "
        "⇒ ★**副作用如实记: 落表把 SW 侧 3 条断言打成过期红 (timing_check F8/REV-3 + demo_panel_spec REV-12) ⇒ 已开 ISS-235 给 sw-lead 订正 (★不是回退落表★)** ★"
    )

    # ---------------- ISS-234 → verified ----------------
    i234 = by_id["ISS-234"]
    assert i234.get("status") == "fixing", i234.get("status")
    i234["status"] = "verified"
    i234["verify_by"] = "main"
    i234["verify_date"] = TODAY
    i234["verify_result"] = V234
    i234["fix_ref"] = "HANDOFF/2026-11-16_sw-lead_ISS234_关机语义三口径方案与门禁.md"
    i234["note"] = (i234.get("note") or "") + (
        "\n2026-11-16 07:2x ★**main 实跑新门禁 rc=0 + selftest 17/17 + 旧门禁 + H-1 重锚三方对账 ⇒ 落 verified** ★ "
        "⇒ ★**派单前提「负载开关 0 颗」经 main 逐行复核为 2 颗 (U_PWR_SW L50 + U_EN_SW L442) ⇒ 结论方向仍成立, 原因已换 (电池链全 DNP + demo SoM 供电路径零开关)★** ★ "
        "⇒ ★**交卷时刻唯一红 (timing_check 2 条过期断言) 已开 ISS-235★** ★"
    )

    # ---------------- 新开 ISS-235 (sw-lead) ----------------
    assert "ISS-235" not in by_id
    log["issues"].append({
        "id": "ISS-235",
        "title": TITLE_235,
        "severity": "high",
        "source_blocker": "SW-TIM-B2",
        "desc": DESC_235,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "2026-11-16 07:2x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实跑** "
            "(`timing_check.py` rc=1 68/70 · `check_demo_panel_spec.py --selftest` 15/16 · 逐行读网表 L50/L442 · 5 个 md5 实测) ★\n"
            "★**sw-lead 名额的上一条 ISS-234 本轮 07:2x 落 verified (main 实跑: 新门禁 rc=0 + selftest 17/17 + H-1 重锚三方对账绿) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
            "★**这 3 条红是【断言写死了旧事实】(★ISS-233 合法落表造成的锚点过期★) ⇒ 修在 SW 侧脚本, 不许回头改网表 (那等于把 ISS-233 的 A 类落表回退掉)** ★\n"
            "★**边界**: 不许改 `HW/` (网表/脚表/BOM 5 个 md5 必须逐字节不变) · 不许碰 PCB · 不许把断言放宽成永远绿 · 不许自签 issue_log ★"
        ),
        "task_brief": BRIEF_235,
        "dispatched_at": TODAY,
    })

    # ---------------- 新开 ISS-236 (hw-lead) ----------------
    assert "ISS-236" not in by_id
    log["issues"].append({
        "id": "ISS-236",
        "title": TITLE_236,
        "severity": "high",
        "source_blocker": None,
        "desc": DESC_236,
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "2026-11-16 07:2x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实跑** "
            "(`--expect-resolved` rc=1 = 18 条 · ISS-233 交卷单 §3 逐字清单已在盘) ★\n"
            "★**hw-lead 名额的上一条 ISS-233 本轮 07:2x 落 verified (main 实跑 8 道闸全绿) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
            "★**★核心红线: 老板没拍 V-2/V-3/V-4 ⇒ 本单一个 V 值都不许落 ⇒ 落表器默认 dry-run 且 `--apply` 必须带 `--boss-decision`★** ★\n"
            "★**边界**: 不许碰板 (B-1~B-8 继续排队) · 不许改 SW/MECH · 不许自签 issue_log ★"
        ),
        "task_brief": BRIEF_236,
        "dispatched_at": TODAY,
    })

    shutil.copy2(LOG, LOG + ".bak_20261116_0725_verify233_234_open235_236")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-233 → verified · ISS-234 → verified · 新开 ISS-235 (sw-lead) / ISS-236 (hw-lead)")


if __name__ == "__main__":
    main()
