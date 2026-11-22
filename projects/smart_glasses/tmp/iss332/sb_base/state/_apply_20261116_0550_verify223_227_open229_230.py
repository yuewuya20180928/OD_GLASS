#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0550_verify223_227_open229_230.py
★main (moli) 手动清账 + 开新单 · 2026-11-16 05:50 (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★队列止血 + 落表主线推进, 不是例行公事★)** ★★
· ★**ISS-223 (hw-lead) 子会话** `agent:hw-lead:subagent:684f3e4b` ★**status=done · endedAt 05:27:24**★
  ⇒ 4 件交付物全部落盘 ⇒ ★main 本轮自己实跑门禁 + 自己 md5 + 自己查分片 ⇒ 落 `verified` ⇒ **放掉 hw-lead 名额** ★
· ★**ISS-227 (mech-lead) 子会话** `agent:mech-lead:subagent:5997cb10` ★**status=done · endedAt 05:27:55**★
  ⇒ 交付物 4/4 在盘 + 门禁 22/22 + selftest 24/24 ⇒ 落 `verified` ⇒ **放掉 mech-lead 名额** ★
  ⇒ ★**但 `MECH/check_demo_struct_truth.py` 现在 rc=2 (G5b + C21 红)** ⇒ ★**根因 = ISS-223 05:18 重生成网表 (md5 `13f59a43…`→`3215020b…`) ⇒ 锚点过期** ★
  ⇒ ★**不是 ISS-227 的锅** (mech-lead 已用「还原网表 ⇒ 门禁立刻回 23/23」自证) ⇒ 归本单 ISS-229 的附带项 ★
· ★**ISS-228 (sw-lead) 子会话** `agent:sw-lead:subagent:4930b32a` ★**status=running (05:26 起)★** ⇒ **不碰** ★

★★**ISS-229 新开 (mech-lead 名额)** ★★
★**充电时皮肤侧温度重算 (★42.14°C 这个数是按【错的方向】算出来的 ⇒ 现在是【无有效数字】★)** ★★
· ★**实测依据 (main 2026-11-16 05:4x 实算, 不是抄交卷报告★)**:
  `MECH/hinge_power_calc.py` L33 `ICHG_FACTOR = 0.822` ⇒ ★**ISS-220 第 1 批已把方向改正 (ICHG/IIN = η·Vbus/Vbat) ⇒ 正确系数 = 1.216 @3.7V / 1.071 @4.2V** ★
  ⇒ ★**`MECH/hinge_power_calc.json` 的 `rilim_table` / `copper_vs_rilim` 全表都建立在 0.822 上 ⇒ 「390Ω 档 皮肤侧 42.14°C < 43°C 红线 ✅」这个结论【方向反了】★ ★
  ⇒ ★**main 独立推算 (按同一 k_eff 50.13 K/W + 同一 R_path 口径线性外推, [推算])**:
    390Ω 档 max: ICHG 0.822→1.216 A ⇒ P_hinge 74.9→163.8 mW / P_cell 67.6→147.9 mW ⇒ ΔT 7.14→**15.6°C** ⇒ 皮肤侧 42.14→**~50.6°C** ⇒ ★**43°C 红线【不再满足】** ★
    470Ω 档 max: ICHG 0.682→1.009 A ⇒ 皮肤侧 39.9→**~45.8°C** ⇒ ★**也不满足** ★
    680Ω 档 max: ICHG 0.471→0.697 A ⇒ 皮肤侧 37.3→**~40.1°C** ⇒ ★**满足** ★
    ⇒ ★**⇒ V-4 (R_ILIM 档位) 的建议区间要重算: 390Ω/470Ω 两档在【修正系数】下都不满足 43°C ⇒ 680Ω / 1.2kΩ 才是活档** ★
  ⇒ ★**这直接改写老板待拍板页 §9 的 V-4 建议默认值** ⇒ ★**必须先有 mech-lead 的脚本实跑数, 再改决策页** ★
· ★**附带项: MECH 闸 G5b + C21 重锚 (★走 ISS-224 建立的 H-1 流程★)** ⇒ 落表方已写台账 (`HW/SCHEMATIC_LANDING_V1_LANDED.md` §13 有 ISS-223 + 新旧 md5) ⇒ ★**本单只更新 MECH 侧锚点 + 留痕, 不许改判据语义** ★

★★**ISS-230 新开 (hw-lead 名额)** ★★
★**把「原理图落表 第 3 批」从【等老板拍板】变成【拍完就落】+ 修两处文档病** ★★
· ★**依据 (main 本轮实测)**: `--expect-resolved` 还剩 **21 条未落表**, 其中 ★**13 条 = R2/R7/R8 = V-3 (BAT_DET 分压链)**★ (ISS-223 已把 V-3 做成可判: 推荐 E = 100k+60k+100nF) · ★**R4/R9 = V-2 (ESD 选型)**★ · ★**R10 = V-4 (R_ILIM 档位)**★ · ★**R3 = 板只改一次那一趟**★ ⇒ ⇒ ★**⇒ 现在缺的不是一个「等答案」, 而是「答案一到就能一键落」的逐字改法** ★
· ★**§7 充电板清单的两处实测病**: ① ★**CSV 块本身不合法** (main 实测: 表头 13 列, ★**idx 23 (`U_CHG` 那行) 解析成 16 列** ★ ⇒ note 里逗号未加引号 ⇒ board 列被解析成 `" 0.8mm max height"`) ★ ② ★**§7 ↔ 网表双向差集 (main 自己重算, 与交卷报告数字一致)**: §7 唯一位号 **41** / 网表 CHG_BOARD 唯一位号 **40** / 交集 **25** ⇒ ★**§7 有而网表没有 = 16 个** · ★**网表有而 §7 没有 = 15 个** ★
· ★**F-3 遗留**: 「A 组 20 条必须 `z_diff` 非空 且 `imp` 为空」这条加强型独立断言还没加 (main 实测现状: 20 条迁移行全部仍在判据覆盖内且值全对 ⇒ ★**加断言不会红, 现在就能加**★)

★★**边界 (两单共同)★★ ★★
★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到写降级方案 ★
★**不许替老板拍板** ⇒ ★**V-2 / V-3 / V-4 / 集热面材质 / u8 / d 值 / 板长 全部只出选项 + 量化代价 + 建议默认值, 不代拍** ★
★**不许碰 PCB 布线 / 布局 / 板框** ⇒ 板侧 8 项 (B-1~B-8) 继续**排队**, 本 job 不派 ★
★**板 / 网表 / 脚表 / `.kicad_pro` md5 交卷前后必须逐字节不变** ★
"""
import os
import shutil
import datetime as dt
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

BRIEF_229 = """★★**目标 (★内部活·结构/热路侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把「充电时皮肤侧温度」这个数【重算一遍】—— 因为它现在是【按错的方向算出来的 ⇒ 无有效数字】** ★★ ⇒ ★**这直接改写老板待拍板页 §9 的 V-4 (R_ILIM 档位) 建议默认值** ★★

★★**为什么是现在 (★main 2026-11-16 05:4x 实算 + 实跑, 不是推测, 也不是抄交卷报告★)** ★★
· ★**根因 (main 实读代码)**: `MECH/hinge_power_calc.py` L33 ★**`ICHG_FACTOR = 0.822`** ★
  ⇒ ★**而 ISS-220 (hw-lead) 第 1 批落表已把充电电流换算方向改正** (★`HW/CHARGE_BOARD_SPEC.md` §2.4 的口径 = ★**`ICHG/IIN = η·Vbus/Vbat`**) ★
  ⇒ ★**正确系数 = 1.216 @ Vbat 3.7V / 1.071 @ 4.2V** ★ ⇒ ★**0.822 是【倒数方向】的旧值 ⇒ 所有建立在它上面的温度数全部偏乐观** ★
· ★**受影响的产物 (main 实查)**: `MECH/hinge_power_calc.json` 的 ★**`rilim_table`** (每档 × min/typ/max 三行) ★ + ★**`copper_vs_rilim`** (每档 × 2 种铜厚 = 8 行) ★ ⇒ ★**全表都要重算** ★
· ★**main 独立推算 (★口径: `IINMAX = KILIM_max / R_ILIM` (KILIM_max = 390 AΩ) → `ICHG = IINMAX × 系数`; `dV = ICHG × R_path` (R_path 由旧表反解: 390Ω/1oz = 91.06mV / 0.822A = 110.8 mΩ) → `P_hinge = ICHG × dV`; `P_cell = ICHG² × 0.10Ω`; `ΔT_hinge = P_hinge × k_eff 50.13 K/W`; `ΔT_cell = P_cell × k_eff`; `T_skin = 35 + ΔT`· 标 [推算]★)**:
  | 档 | ICHG (旧→新) | P_hinge | P_cell | ΔT | 皮肤侧 | 43°C |
  |---|---|---|---|---|---|---|
  | 390Ω max | 0.822→**1.216** A | 74.9→163.8 mW | 67.6→147.9 mW | 7.14→**15.6°C** | 42.14→**~50.6°C** | ★**❌ 不再满足** ★ |
  | 470Ω max | 0.682→**1.009** A | 51.5→112.8 mW | 46.2→101.8 mW | 4.92→**10.8°C** | 39.92→**~45.8°C** | ★**❌ 不再满足** ★ |
  | 680Ω max | 0.471→**0.697** A | 24.6→53.9 mW | 22.2→48.6 mW | 2.35→**5.14°C** | 37.35→**~40.1°C** | ★**✅ 满足** ★ |
  ⇒ ★**⇒ 现在文档里「390Ω 档 42.14°C, 只剩 0.86°C 余量」这句【是错的】⇒ V-4 的活档变成 680Ω / 1.2kΩ** ★
· ★**main 独立复核过什么 (★不是抄交卷报告★)**: `MECH/hinge_power_calc.py` L33 / `MECH/HINGE_POWER_CALC.md` L74 · L158 · L171 · L182 · L209~L210 · L354 · `MECH/hinge_power_calc.json` 的 `rilim_table` + `copper_vs_rilim` 全表逐行 · `HW/PCB_OUTLINE_60x15.md` L149 / L190 (★那两行也带着同一个错数·但 ★**那是 HW 地界, 本单只报不改**★) ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**重算脚本改对方向 + 重出表** ★ ⇒ ★**把 `MECH/hinge_power_calc.py` 的 `ICHG_FACTOR` 从 0.822 改成【按 Vbat 分档的正确系数】** (★3.7V ⇒ 1.216 · 4.2V ⇒ 1.071 ⇒ ★**取最坏 (Vbat 最低) 的 1.216, 并在输出里把两个值都列出来**★) ⇒ ★**重跑 `python3 MECH/hinge_power_calc.py` (★★必须在项目库根目录跑 ★★· 该脚本用相对路径写 `MECH/hinge_power_calc.json`· L323) 重出 `MECH/hinge_power_calc.json`** ⇒ ★**`rilim_table` (每档 × min/typ/max) 与 `copper_vs_rilim` (每档 × 2 种铜厚) 两张表全部重算** ★
    ⇒ ★**`rilim_table` 里要重判的是 `T_skin` / `T_skin_opt`; `copper_vs_rilim` 里要重判的是 `T_skin` + `pass_43`** ★ (★main 本轮实测过这两张表的字段名, 别写错字段★) ★
  ⇒ ★**口径纪律**: ★**① 只改【系数】和【由它派生的数】, 不许动 `k_eff` 50.13 / R_path / 环境基准 / `R_cell` 0.10 / 铜厚档 / KILIM 320/355/390 任何一个** ★
  ⇒ ★**② 每档要同时给 min/typ/max 三行 + 两种铜厚 (1oz / 2oz)**, ★**不许只给一行** ★
  ⇒ ★**③ 表里每一行都要标证据等级**: `ICHG` = [推算] (系数来源 = `HW/CHARGE_BOARD_SPEC.md` §2.4 改正后的口径) · `ΔV / P / 皮肤温度` = [推算] · ★**板端 [实测] = 0 条** ★
② ★**改正 `MECH/HINGE_POWER_CALC.md`** ★ ⇒ ★**把 L74 / L158 / L171 / L182 / L209~L210 / L354 这几处「0.822 / 42.1°C / 47.1°C / 39.9°C / 37.3°C」全部按新表改掉** ⇒ ★**并在文件头加一段【口径订正留痕】: 「旧表建立在倒方向的 0.822 上 ⇒ 全部温度数偏乐观 ⇒ 已作废」** ★
  ⇒ ★**旧数不许直接删掉而不留痕** ⇒ ★**要写成「旧值 (作废) → 新值」对照** ★
③ ★**把结论整理成给 main 的【V-4 建议默认值更新包】(★不是代拍★)** ★ ⇒ ★**写成一份交接单里的表: 每个档 (300/390/470/680/1.2kΩ) × (min/typ/max) × (1oz/2oz) 的新皮肤侧温度 + `pass_43` 判定 + 充电时间 + 单 pin 载流 vs 0.5A 触点额定** ★
  ⇒ ★**并在表头写清「本单不代拍 V-4; 建议默认值由项目总工/老板拍」** ⇒ ★**不许自己写「建议选 X」** ★
  ⇒ ★**另附一条: 「充电时皮肤侧是否仍是硬约束」的现状说明 (★老板 10-28 已拍「边戴边充不允许」⇒ 充电时眼镜不在皮肤上 ⇒ 这条约束的【产品语义】与【数】要分开说★)** ⇒ ★**只作说明, 不改老板已拍的口径** ★
④ ★**交接单 + 分片 + 附带项 (MECH 闸 G5b + C21 重锚)** ★ ⇒ ★**交接单** `HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md` (★B1~B6 六块齐全★) + ★**分片** `state/fragments/mech.yaml` (★必须走 `python3 state/frag_write.py` 原子写★) ★
  ⇒ ★**附带项 (MECH 闸重锚, ★走 ISS-224 建立的 H-1 流程★)**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS.source_ledger.entries` 里 ★**`HW/netlist_v1.csv` 那一条** ★ ⇒ ★**`md5` 改成盘上实测值 (交卷那一刻实测, 交卷报告写清) · `prev_md5` 改成 `13f59a43dbd35dc6cb16e897c8c891ab` · `by` 改成 `ISS-223` · `landed_at` 写落表时刻** ★
    ⇒ ★**并加【留痕】: §3.1「已修复 (留痕)」节加一行 (谁改的 / 哪个单号 / 新旧 md5 / 复现命令)** ★
    ⇒ ★**门禁必须从 rc=2 (21/23) 回到 rc=0 (23/23)**, 且 ★**`--selftest` 的反向用例一条都不许被删** ★
    ⇒ ★**C21 要真在跑**: 锚点里登记的 md5 / prev_md5 / 落表单号 / 文件名 ★**四项都必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 或 `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` 里查到** ★
      (★main 本轮实测: LANDED 里 `ISS-223` × 3 · `HW/netlist_v1.csv` × 5 · `13f59a43` × 3 · `3215020b` × 1 ⇒ ★**台账侧四项齐全, 只差 MECH 侧锚点没跟上**★) ★
    ⇒ ★**脚表那条 (`HW/netlist_v1_pins.csv`) 本轮 md5 没变 (`a600afae…`) ⇒ 不许乱动它** ★

★★**边界 (★违反一条即本单无效★)** ★★
· ★**不许改** `HW/` 下任何文件 (★网表 / 脚表 / 板 / `.kicad_pro` / 原理图 / BOM 一个字节不许动★) ⇒ ★**`HW/PCB_OUTLINE_60x15.md` L149 / L190 那两行的订正只【报】给 main, 本单不改 (HW 地界)** ★
· ★**不许改** `SW/` 下任何文件 ★
· ★**不许改** `state/issue_log.yaml` (★status 留给 main 落 verified★) / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` (★决策页是 main 的地界★) / `state/outbox/` / 别人的分片 ★
· ★**不许碰** PCB 布线 / 布局 / 板框 ⇒ ★**板侧 8 项 (B-1~B-8) 继续排队, 不归本单** ★
· ★**不许把 [推算] 写成 [官网]/[实测]** ⇒ ★**板与屏不在本机 ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」★ ★
· ★**板端 [实测] = 0 条** ★
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到必须写降级方案** ★ ⇒ ★**不许写「等原厂回信」** ★
· ★**不许自签 issue_log** ★
· ★**不许替老板拍板** (★V-4 / 集热面材质 / u8 / d 值 一律只给数 + 选项 + 代价★) ★

★★**交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★)** ★★
```
python3 MECH/hinge_power_calc.py                                  # rc=0 (★系数已改正 + 两张表重出★)
python3 MECH/verify_budget.py                                     # rc=0 (★门禁绿★)
python3 MECH/cavity_recalc_check.py                               # rc=0 (★22/22★)
python3 MECH/cavity_recalc_check.py --selftest                    # rc=0 (★24/24★)
python3 MECH/check_demo_struct_truth.py                           # rc=0 (★23/23★ · ★G5b + C21 必须转绿★)
python3 MECH/check_demo_struct_truth.py --selftest                # rc=0 (★反向用例一条不许少★)
python3 state/merge.py && python3 state/gate_check.py             # rc=0 且 【Q1 交付齐备率】 18/18
```
★**受保护 md5 (交卷前后必须逐字节不变)**: ★**板 `611b869e13518c3c023fb178f91a0075` · 网表 `3215020b6d4120e1b7728227effdc6d3` (★交卷那一刻实测, 若变了就写清是谁变的★) · 脚表 `a600afae493f5a7a6c55f46ad35ac89c` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · `MECH/hinge_usb_check.py` `3425bc14…` · `MECH/service_port_check.py` `9b24bf98…` · `MECH/hw_cross_review_check.py` `e521387b…` · `MECH/display_biosafety_v2_check.py` `29c77fc3…`** ★
★**交卷前最后一件事**: ★**把你算出来的每档温度 vs 43°C 红线的判定表, 和 main 本轮独立推算的那四个数 (390/470/680 档 max) 逐条对拍 ⇒ 对得上就写「与 main 独立推算一致」, 对不上就写「不一致, 我的数是 X, 差异原因 Y」★ ⇒ ★**不许为了对上而改口径** ★
"""

BRIEF_230 = """★★**目标 (★内部活·原理图/网表侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把「原理图落表 第 3 批」从【等老板拍板】变成【拍完就落】+ 修两处文档病 + 加一条加强型断言** ★★

★★**为什么是现在 (★main 2026-11-16 05:4x 实跑, 不是推测★)** ★★
· ★**落表只剩 21 条 (`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, 21 条未落表)** ★
  ⇒ ★**13 条 = R2/R7/R8 = V-3 (BAT_DET 分压链)**★ (★ISS-223 已把它做成【可拍】: 推荐 E = 上臂 100k±1% + 下臂 60k±1% + 滤波 100nF±10%, 唯一代价 26.25µA / 110µW 常开★) ★
  ⇒ ★**4 条 = R4/R9 = V-2 (ESD 方案与型号)**★ · ★**1 条 = R10 = V-4 (R_ILIM 档位)**★ · ★**R3 = 板只改一次那一趟** ★
  ⇒ ★**⇒ 现在缺的不是「等答案」, 而是【答案一到就能一键落】的逐字改法** ⇒ ★**这单就是把那份逐字改法做出来** ★
· ★**§7 充电板清单的两处实测病 (main 自己重算的, 不是抄交卷报告)**:
  ① ★**§7 的 CSV 块本身不是合法 CSV** ⇒ ★**表头 13 列, 但 idx 23 (`U_CHG` 那行) 解析成 16 列** ★ ⇒ ★**note 里的逗号没加引号 ⇒ board 列被解析成 `" 0.8mm max height"`** ★
  ② ★**§7 ↔ 网表双向差集**: §7 唯一位号 **41** / 网表 `board=CHG_BOARD` 唯一位号 **40** / 交集 **25** ⇒ ★**§7 有而网表没有 = 16 个** · ★**网表有而 §7 没有 = 15 个** ★
· ★**F-3 遗留的加强型断言**: ★**「A 组 20 条必须 `z_diff` 非空 且 `imp` 为空」** ★ ⇒ ★**main 本轮实测: 20 条迁移行全部仍在判据覆盖内且值全对 ⇒ 现在加这条断言【不会红】, 不用等第 3 批** ★
· ★**另有一处过期结论要作废标记**: `HW/PCB_OUTLINE_60x15.md` L149 / L190 带着「390Ω 档 皮肤侧 42.14°C (< 43°C 红线 ✅)」★ ⇒ ★**这个数是按错方向的 0.822 算的 (mech-lead 的 ISS-229 正在重算) ⇒ 本单只【标作废 + 指向 `MECH/HINGE_POWER_CALC.md`】, 不写新数 (新数归 mech-lead)** ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**第 3 批落表作业包 v2:【每个待裁项的每个选项 ⇒ 逐字改法】** ★ ⇒ ★**对 V-2 / V-3 / V-4 各写出「选哪个 ⇒ 改哪个文件的哪一行 ⇒ 改成什么字面值 ⇒ 重跑哪些生成器 ⇒ 哪几条判据会转绿 ⇒ 门禁会怎么变」的完整映射** ★
  ⇒ ★**每个选项都要有: ① 改法 (文件 + 行 + 旧值 + 新值, 逐字) ② 影响面 (哪几条 R# 判据 / 哪些网表行 / 脚表 / BOM 行) ③ 板侧连带项 (★只列, 不许改板★) ④ 量化代价 (BOM 成本 / 载流 / 面积 / 功耗) ⑤ 若老板选了别的选项 ⇒ 本单映射不用重做** ★
  ⇒ ★**V-3 必须覆盖【方案 E】+ ISS-223 §11.4 列的 4 条降级 (①按需使能上臂 ②用途降级为低电量粗判 ③三个数到手回填 ④改读 BQ25896 遥测)** ⇒ **每条都要写出「落到网表哪一行/哪个字段」** ★
  ⇒ ★**不许替老板拍板** ⇒ ★**每个选项后面只准写「建议默认值 + 依据 + 代价」, 不准写「已决定」** ★
② ★**修 §7 的 CSV 合法性 + 把 §7 ↔ 网表的双向差集【清单化】** ★
  ⇒ ★**① 把 §7 那个 CSV 块修成【合法 CSV】** (★main 实测: 只需把 `U_CHG` 那行 note 里的逗号正确加引号 ⇒ 全块 81 行 × 13 列齐★) ⇒ ★**并写一个一次性脚本把 §7 块解析 + 逐行对拍网表, 把 16/15 差集打成一张表** ★
  ⇒ ★**② 差集表要逐条给「该 §7 补 / 该网表补 / 该改名 / 该归板 / 该留白」的处置建议** ⇒ ★**但【不许改网表】(★网表真源是 `state/p10_rows.json`; ★**F-5 已订正: §7 与网表是两个版本, 对账的错在 §7★ ⇒ 本单只修 §7 侧, 改网表归【充电板整页】那一趟★)** ★
  ⇒ ★**③ 明确写清「本单【没有】做双向对账」的原因** (★现状两个版本, 起点不成立★) ⇒ ★**不许为了做对账去改网表** ★
③ ★**加加强型断言 (F-3 遗留)** ★ ⇒ ★**在 `state/check_netlist.py` 或 `HW/check_netlist_selfconsistency.py` 加一条独立断言: 「A 组 20 条 NET 行必须 `z_diff` 非空 且 `imp` 为空」** ⇒ ★**并配一条反向用例 (把某条 A 组的 `z_diff` 清空 ⇒ 必须红)** ⇒ ★**加完 `--selftest` 必须一条都不少** ★
  ⇒ ★**main 本轮实测基线**: `state/check_netlist.py` 判据 5 现在覆盖 ★**37 条 A 组 NET 行, 其中实际被比对 22 条 (want 非空), 15 条因 `imp`/`z_diff` 双空而跳过** ★ ⇒ ★**⇒ 那 15 条 (全是 `conn_id=A-24` 的 USB 连接器行) 本来就不该有阻抗值 ⇒ 加强断言必须【只针对迁移过的那 20 条】, 不许把 A-24 那 15 条也拖进来 (那会把 15 条真红)** ★ ★
    (★这 15 条是 `A-24` = `J_TYPE_C` 的 16p 母座行: `GND` / `USB_CC1` / `USB_CC2` / `CARRIER_BOARD_EN` / `RAIL_DEMO_5V` / `RAIL_BOARD_5V` 等功能串 ⇒ 本来就没有阻抗值★) ★
④ ★**交接单 + 分片 + 作废标记** ★ ⇒ ★**交接单** `HANDOFF/2026-11-16_hw-lead_ISS230_第3批作业包v2与加强断言.md` (★B1~B6 六块齐全★) + ★**分片** `state/fragments/hw.yaml` (★必须走 `python3 state/frag_write.py` 原子写★) ★
  ⇒ ★**`HW/PCB_OUTLINE_60x15.md` L149 / L190: 只把那个 42.14°C 结论标成【作废 (口径 0.822 方向反了) + 指向 `MECH/HINGE_POWER_CALC.md`】, 不许写新温度数** ★

★★**边界 (★违反一条即本单无效★)** ★★
· ★**不许改** `MECH/` 下任何文件 (★mech-lead 的 ISS-229 正在改 `MECH/HINGE_POWER_CALC.md` + `MECH/hinge_power_calc.*` ⇒ **不许抢**★) / `SW/` 下任何文件 ★
· ★**不许改** `state/issue_log.yaml` (★status 留给 main 落 verified★) / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` (★决策页是 main 的地界★) / `state/outbox/` / 别人的分片 ★
· ★**不许碰** PCB 布线 / 布局 / 板框 ⇒ ★**板侧 8 项 (B-1~B-8) 继续排队, 不归本单** ★
· ★**不许在本单落表任何 V-2 / V-3 / V-4 的值** (★那是老板拍完之后的活★) ⇒ ★**网表 / 脚表 / BOM / 板一个字节不许动** ★
· ★**不许把 [推算] 写成 [官网]/[实测]** ⇒ ★**板端 [实测] = 0 条** ★
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到必须写降级方案** ★ ⇒ ★**不许写「等原厂回信」** ★
· ★**不许自签 issue_log** ★
· ★**不许替老板拍板** (★V-2 / V-3 / V-4 / 板长 / 充电板去留 全部只出选项 + 量化代价 + 建议默认值★) ★

★★**交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★)** ★★
```
python3 HW/check_netlist_selfconsistency.py                    # rc=0 (★现状守卫★)
python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (★反向用例一条不许少★)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★预期: 还有 21 条未落表★)
python3 state/check_netlist.py                                  # rc=0 (★加完加强断言仍绿★)
python3 state/check_netlist_pins.py                             # rc=0
python3 state/check_sch_erc.py                                  # rc=0 (★ERC 违规数 = 0★)
python3 state/check_sch_pinfull.py                              # rc=0
python3 state/merge.py && python3 state/gate_check.py           # rc=0 且 【Q1 交付齐备率】 18/18
```
★**受保护 md5 (交卷前后必须逐字节不变)**: ★**板 `611b869e13518c3c023fb178f91a0075` · 网表 `3215020b6d4120e1b7728227effdc6d3` · 脚表 `a600afae493f5a7a6c55f46ad35ac89c` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`** ★
★**已知会红、且不归你管的那盏 (★提前说清, 免得你误修★)** ★★
· ★**`MECH/check_demo_struct_truth.py` 现在 rc=2 (G5b + C21 红)** ⇒ ★**根因 = ISS-223 05:18 重生成网表 ⇒ MECH 锚点过期** ★ ⇒ ★**mech-lead 的 ISS-229 正在重锚 ⇒ **不许自己去改 `MECH/`** ★
· ★**`SW/tools/check_demo_panel_spec.py` 的 R6 现在红** ⇒ ★**同一个根因 (SW 台账锚点过期)** ★ ⇒ ★**sw-lead 名额被 ISS-228 占着 ⇒ 本轮没人做 ⇒ **不许自己去改 `SW/`** ★
★**交卷前最后一件事**: ★**把你写的【每个选项的逐字改法】自己走一遍「照着改能不能改出那一行」的自查 ⇒ 交卷时把自查结果贴出来** ★
"""


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {i.get("id"): i for i in issues}

    # ---------- 1. ISS-223 → verified (main 本轮自己实跑验收) ----------
    i223 = by_id["ISS-223"]
    assert i223.get("status") == "fixing", i223.get("status")
    i223["status"] = "verified"
    i223["verify_by"] = "main"
    i223["verify_date"] = TODAY
    i223["verify_result"] = (
        "★main 2026-11-16 05:4x~05:5x 自测验收 (★本轮自己实跑, 不抄交卷报告★)★\n"
        "· 交付物 4/4 在盘: ①HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md (28544 B, 05:27, B1~B6 六块齐全) "
        "②HW/SCHEMATIC_LANDING_V1_LANDED.md §10~§14 (78644 B, 05:29) ③HW/SCHEMATIC_LANDING_WORKPACKET_V1.md §9 修订记录 F-1~F-5 (177530 B, 05:22) "
        "④state/calc_v3_batdet.py (11767 B, 05:25) + state/calc_v3_batdet_output.txt ★\n"
        "· 门禁 (main 自己跑的): `HW/check_netlist_selfconsistency.py` rc=0 (现状守卫 + 作业包 28 条 8 栏齐 + 三方对齐全过) ; "
        "★`--selftest` rc=0 (19/19 反向用例全抓到) ★ ; ★`--expect-resolved` rc=1 (★预期: 还有 21 条未落表, 其中 13 条卡 V-3 / 4 条卡 V-2 / 1 条卡 V-4 / R3 卡板只改一次★) ★ ; "
        "`state/check_netlist.py` rc=0 ; `state/check_netlist_pins.py` rc=0 ; `state/check_sch_erc.py` rc=0 (ERC=0) ; `state/check_sch_pinfull.py` rc=0 (584 脚=584 脚 K=0) ; "
        "`state/merge.py` rc=0 ; `state/gate_check.py` rc=0 (Q1 18/18) ★\n"
        "· ★**main 独立复算 (★不抄交卷报告★)**: ★**A 组字段迁移实测 = 20 条 `conn_id` 的 `imp` 空 + `z_diff` 非空, 且 `imp` 非空+`z_diff` 非空 = 0 条 (⇒ 迁移没搬一半) ; "
        "这 20 条【全部仍在 `state/check_netlist.py` 判据 5 的被比对集合里】(⇒ F-3 担心的「覆盖 20 行→0 行 静默失效」【没有发生】) ; "
        "逐条值对拍 = 0 条不符 (⇒ 迁移后值全对)** ★ ⇒ ★**判据 5 现状输出「A 组阻抗逐条对照规格 (37 条 net)」= A 组 NET 行总数, 其中实际比对 22 条 / 跳过 15 条 (全是 A-24 的 USB 母座功能行, 本来就没阻抗值) ★ ★\n"
        "· ★**受保护 md5 交卷前后逐字节不变 (main 实测)**: 板 `611b869e13518c3c023fb178f91a0075` ✓ · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ✓ · "
        "脚表 `a600afae493f5a7a6c55f46ad35ac89c` (与交卷前一致, 脚表不含 NET 行 value ⇒ 不变是对的) ✓ · BOM `92b51580867deca9f8b04af88d925d96` ✓ ; "
        "★**网表按落表计划变了: `13f59a43dbd35dc6cb16e897c8c891ab` → `3215020b6d4120e1b7728227effdc6d3` (只 L291/L292 两行, 即 USB 串阻 22Ω±1% + 差分阻抗 90Ω±15% 搬进 z_diff, main 实读 L291/L292 逐字确认)** ★\n"
        "· ★**分片真落盘 (main 实查)**: `state/fragments/hw.yaml` (mtime 05:28) ⇒ ★**ISS-220 补落的 3 条声明在 L2867 `iss220_chgboard_white_list_scope` / L2872 `iss220_i2ca_pullup_domain_1v8` / L2877 `iss220_ichg_ratio_true_value`** ★ ⇒ ★**交付物① 真在盘 (ISS-217 的老账「交卷自述通过、盘上实为 0 条」这次没复发)** ★\n"
        "· ★**V-3 可判化真落盘 (main 实查)**: LANDED §11 (11.1 官方参数 / 11.2 误差算式 / 11.3 三档实测 / 11.4 可拍依据+推荐值+4 条降级) + `state/calc_v3_batdet.py` ⇒ "
        "★**⇒ V-3 从「拍不了」变成「可拍」, 推荐 E = 100k+60k+100nF, 唯一代价 26.25µA/110µW** ⇒ ★**这 13 条 R2/R7/R8 现在等的是老板一个「是/否」, 不是技术障碍** ★\n"
        "· ★**不在本单账上的红 (★按设计, 是「锚点过期」不是「红灯被调没」★)**: `MECH/check_demo_struct_truth.py` rc=2 (G5b + C21) + `SW/tools/check_demo_panel_spec.py` rc=1 (R6) ⇒ "
        "★**根因 = ISS-223 05:18 重生成网表 (md5 13f59a43→3215020b) ⇒ MECH/SW 两侧台账锚点还钉着旧值** ★ ⇒ ★**由 ISS-229 (mech-lead 重锚 MECH 侧) + 后续 sw-lead 名额空出后重锚 SW 侧 收口** ★\n"
        "· ★**板侧 8 项 (B-1~B-8) 继续排队**: B-1 (C_VBUS_GND 封装归属) / B-3+B-4 (ESD 换 3 脚 + 挪到 ≤3.0mm ⇒ 布线必须重跑) / B-5 (D− 补 ESD) / B-8 (若 V-3 拍 E ⇒ R_BAT_DET 阻值要改) ⇒ ★**归「板只改一次」那一趟, 本 job 按老板 10-11 10:07 口径【不派 PCB 类】** ★"
    )
    i223["note"] = (i223.get("note") or "") + (
        "\n2026-11-16 05:50 (cron 775d9893 继续执行后继计划) ★main 独立实测验收 ⇒ 落 verified★ "
        "⇒ ★放掉 hw-lead 名额 ⇒ 同轮新开 ISS-230 派出★"
    )

    # ---------- 2. ISS-227 → verified (main 本轮自己实跑验收) ----------
    i227 = by_id["ISS-227"]
    assert i227.get("status") == "fixing", i227.get("status")
    i227["status"] = "verified"
    i227["verify_by"] = "main"
    i227["verify_date"] = TODAY
    i227["verify_result"] = (
        "★main 2026-11-16 05:4x~05:5x 自测验收 (★本轮自己实跑, 不抄交卷报告★)★\n"
        "· 交付物 4/4 在盘: ①MECH/CENTER_CAVITY_REBALANCE_V3.md §2.5 (43996 B, 05:24, C7B×4 + U8×5 + R7B×3 = 12 行关键表, main 实测 C7B- 命中 13 处) "
        "②MECH/cavity_recalc_check.py (105976 B, 05:23) ③HANDOFF/2026-11-16_mech-lead_ISS227_C7b集热面口径修正.md (26853 B, 05:27, B1~B6 六块齐全) "
        "④state/fragments/mech.yaml (mtime 05:27, ★回掉 need `iss222_mech_c7b_sink_is_metal_not_print`★) ★\n"
        "· 门禁 (main 自己跑的): `MECH/cavity_recalc_check.py` rc=0 (★22/22★, 含新增 C21 集热面口径 + C22 整节存在性) ; "
        "★`--selftest` rc=0 (★24/24★ ⇒ ★**F-5 报的「反向19 删整节不被抓」已闭环**: 现在反向19 真删掉 §2.5 ⇒ 抓到 C21+C22 双红) ★ ; "
        "`MECH/verify_budget.py` rc=0 (充电耗散口径 = buck) ; `state/merge.py` rc=0 ; `state/gate_check.py` rc=0 (Q1 18/18) ★\n"
        "· ★**受保护 md5 交卷前后逐字节不变 (main 实测)**: `MECH/hinge_usb_check.py` `3425bc14…` ✓ · `MECH/service_port_check.py` `9b24bf98…` ✓ · "
        "`MECH/hw_cross_review_check.py` `e521387b…` ✓ · `MECH/display_biosafety_v2_check.py` `29c77fc3…` ✓ · 板 `611b869e…` ✓ · `.kicad_pro` `3e504d2b…` ✓ · 脚表 `a600afae…` ✓\n"
        "· ★**唯一红项 = `MECH/check_demo_struct_truth.py` rc=2 (21/23 组过, G5b + C21 红) ⇒ ★**根因不在本单**★: main 实读两红的内容都是同一条 ⇒ "
        "★**`HW/netlist_v1.csv: 3215020b… != 13f59a43…` (盘上真源 vs 锚点登记) ⇒ = ISS-223 05:18 重生成网表后的【锚点过期】** ★ ⇒ "
        "★**⇒ 这是设计里的红 (C21 机制就是为「真源被换了」而设), 不是「红灯被调没」** ★ ⇒ mech-lead 自己已用「把网表还原成锚点值 ⇒ 门禁立刻回 23/23」自证与本单改动无关 ★ ⇒ "
        "★**本轮由 ISS-229 (mech-lead) 走 ISS-224 的 H-1 流程重锚 MECH 侧收口** ★\n"
        "· ★**本单不代拍的三条 (★正确, 全部老板级★)**: ①集热面最终材质 (铝 6063-T6 / 镁 / 打印件+独立热路 ⇒ 代价 +9.72g vs +11.34~22.68g) ②u8 端件截面 (框截面未定义 ⇒ [0数据]) ③d 取 15/18/20 ⇒ ★**只给量化代价, 不代拍** ★\n"
        "· ★**重要副产物 (main 本轮独立实算才发现的)**: ★**ISS-227 之外, `MECH/hinge_power_calc.py` L33 的 `ICHG_FACTOR = 0.822` 是【倒方向】的旧系数 ⇒ 充电时皮肤侧温度全表偏乐观 ⇒ "
        "「390Ω 档 42.14°C < 43°C 红线」这个结论【无有效数字】⇒ 已开 ISS-229 (mech-lead) 重算** ★"
    )
    i227["note"] = (i227.get("note") or "") + (
        "\n2026-11-16 05:50 (cron 775d9893 继续执行后继计划) ★main 独立实测验收 ⇒ 落 verified★ "
        "⇒ ★放掉 mech-lead 名额 ⇒ 同轮新开 ISS-229 派出★"
    )

    # ---------- 3. 新开 ISS-229 (mech-lead) ----------
    assert "ISS-229" not in by_id, "ISS-229 已存在"
    issues.append({
        "id": "ISS-229",
        "title": "★★[主线内·结构/热路侧·内部活] 充电时皮肤侧温度【按改正后的系数】重算 (★0.822 是倒方向的旧值 ⇒ 「390Ω 档 42.14°C」无有效数字★ ⇒ 直接改写 V-4 建议默认值★) + 附带 MECH 闸 G5b/C21 重锚 (ISS-223 落表后锚点过期)",
        "severity": "high",
        "source_blocker": "ISS-223",
        "desc": "★**main 2026-11-16 05:4x 实读 + 实算 (不是抄交卷报告)**:\n"
                "· `MECH/hinge_power_calc.py` L33 `ICHG_FACTOR = 0.822` ⇒ ★**ISS-220 第 1 批已把充电电流换算方向改正 (ICHG/IIN = η·Vbus/Vbat) ⇒ 正确系数 1.216 @3.7V / 1.071 @4.2V** ★\n"
                "· ⇒ `MECH/hinge_power_calc.json` 的 `rilim_table` + `copper_vs_rilim` 全表建立在 0.822 上 ⇒ ★**「390Ω 档 皮肤侧 42.14°C (< 43°C 红线), 只剩 0.86°C 余量」这个结论【方向反了】** ★\n"
                "· main 独立推算 (口径: IINMAX = KILIM_max/R_ILIM (390 AΩ) → ICHG = IINMAX×系数; dV = ICHG×R_path (R_path 由旧表反解 110.8 mΩ); P_hinge = ICHG×dV; P_cell = ICHG²×0.10Ω; ΔT = P×k_eff 50.13; T_skin = 35+ΔT · [推算]): 390Ω max ⇒ 皮肤侧 42.14→**~50.6°C (❌)** ; 470Ω max ⇒ 39.9→**~45.8°C (❌)** ; 680Ω max ⇒ 37.3→**~40.1°C (✅)** ⇒ ★**V-4 的活档变成 680Ω / 1.2kΩ** ★\n"
                "· ★**附带项: MECH 闸 G5b + C21 红** ⇒ 根因 = ISS-223 05:18 重生成网表 (md5 13f59a43→3215020b) ⇒ ★**落表台账四项已齐 (main 实测 LANDED 里 ISS-223×3 / HW/netlist_v1.csv×5 / 13f59a43×3 / 3215020b×1) ⇒ 只差 MECH 侧锚点跟上** ⇒ 走 ISS-224 的 H-1 流程重锚 + 留痕 ★\n"
                "· ★**本单 = 内部活 · 零外发 · 不许替老板拍 V-4** ★",
        "owner": "mech-lead",
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
        "note": "2026-11-16 05:50 (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实读 `MECH/hinge_power_calc.py` L33 + 自己实算四档温度 + 自己实查落表台账四项齐全** ★\n"
                "★**mech-lead 名额的上一条 ISS-227 本轮 05:50 落 verified (main 实测: cavity 22/22 + selftest 24/24 + verify_budget rc=0 + 交接单 B1~B6 + 分片真落盘) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改 `HW/` 任何文件 (含 `HW/PCB_OUTLINE_60x15.md` L149/L190 那两行只报不改) · 不改 `SW/` · 不碰 PCB 布线布局 · 不写别人分片 · 不发信 · 不自签 issue_log · 不代拍 V-4 ★",
        "task_brief": BRIEF_229,
        "dispatched_at": None,
    })

    # ---------- 4. 新开 ISS-230 (hw-lead) ----------
    assert "ISS-230" not in by_id, "ISS-230 已存在"
    issues.append({
        "id": "ISS-230",
        "title": "★★[主线内·原理图/网表侧·内部活] 落表第 3 批【逐字改法映射 v2】(★把 21 条未落表从「等老板拍板」变成「拍完就落」★: V-3 13 条 + V-2 4 条 + V-4 1 条) + 修 §7 充电板清单的非法 CSV + 加 F-3 加强型断言 + 标作废一处过期温度结论",
        "severity": "high",
        "source_blocker": "ISS-223",
        "desc": "★**main 2026-11-16 05:4x 实跑 (不是抄交卷报告)**:\n"
                "· `HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, ★**21 条未落表** ★ ⇒ 13 条 = R2/R7/R8 (V-3 BAT_DET, ISS-223 已做成可拍, 推荐 E=100k+60k+100nF) · 4 条 = R4/R9 (V-2 ESD 选型) · 1 条 = R10 (V-4) · R3 = 板只改一次那一趟\n"
                "· ★**⇒ 现在缺的不是「等答案」, 而是【答案一到就能一键落】的逐字改法** ⇒ 本单就是做那份映射 ★\n"
                "· ★**§7 充电板清单两处实测病**: ① ★**CSV 块不是合法 CSV** (表头 13 列, idx 23 `U_CHG` 行解析成 16 列 ⇒ note 逗号未加引号 ⇒ board 列被解析成 `\" 0.8mm max height\"`) ★ ② ★**§7 ↔ 网表双向差集**: §7 唯一位号 41 / 网表 CHG_BOARD 唯一位号 40 / 交集 25 ⇒ §7-only **16** 个 · 网表-only **15** 个 ★\n"
                "· ★**F-3 遗留**: 「A 组 20 条必须 z_diff 非空 且 imp 为空」的加强型独立断言未加 ⇒ ★**main 实测 20 条迁移行全在覆盖内且值全对 ⇒ 现在加不会红** ★\n"
                "· ★**另有一处过期结论**: `HW/PCB_OUTLINE_60x15.md` L149/L190 的「42.14°C < 43°C 红线 ✅」用的是倒方向系数 ⇒ 本单只标作废, 新数归 ISS-229 (mech-lead) ★\n"
                "· ★**本单 = 内部活 · 零外发 · 不许落表任何 V 值 · 不许碰板** ★",
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
        "note": "2026-11-16 05:50 (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实跑 `--expect-resolved` (21 条) + 自己重算 §7↔网表差集 (16/15/25) + 自己实测 A 组 20 条迁移行覆盖** ★\n"
                "★**hw-lead 名额的上一条 ISS-223 本轮 05:50 落 verified (main 实测: 现状守卫 rc=0 + selftest 19/19 + 交付物 4/4 + 分片 3 条真落盘 + 受保护 md5 逐字节不变) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改 `MECH/` (mech-lead 的 ISS-229 在改) · 不改 `SW/` · 不碰 PCB 布线布局 · 不落表任何 V 值 · 不写别人分片 · 不发信 · 不自签 issue_log · 不代拍 V-2/V-3/V-4 ★",
        "task_brief": BRIEF_230,
        "dispatched_at": None,
    })

    # ---------- 写回 ----------
    shutil.copy2(LOG, LOG + ".bak_20261116_0550_verify223_227_open229_230")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-223 → verified / ISS-227 → verified / ISS-229 新开 (owner=mech-lead) / ISS-230 新开 (owner=hw-lead)")
    print("issues total:", len(log["issues"]))


if __name__ == "__main__":
    main()
