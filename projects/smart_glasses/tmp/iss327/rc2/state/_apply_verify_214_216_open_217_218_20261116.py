#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main: 清僵尸 fixing (ISS-214 / ISS-216) + 新开两单 (ISS-217 → hw-lead, ISS-218 → mech-lead)
=========================================================================================
★**为什么这次要落账 (★2026-11-16 01:0x~01:2x 队列自动派活 job fb67af40 实测★)** ★
· ★**`advance.py --json` 的 A 段 (internal) = 0 条** ⇒ 不是没活, 是三个总工名额全被 `fixing` 占住 ★
· ★**实测两个会话已经结束** (★`sessions_list` + `subagents list` 双查★):
  - `agent:hw-lead:subagent:85841b8c` (7f8d0c5a) → **status=timeout** (★01:09:39 被超时掐掉, 掐在"final delivery checks"那一步★)
  - `agent:mech-lead:subagent:900f6943` (a628e635) → **status=done** (00:55 交卷, 全文在 transcript 里)
  - `agent:sw-lead:subagent:580cc849` (db9aa514) → **status=running** (★真在飞 ⇒ 本轮不碰 sw-lead★)
· ★**交付物都已落盘 (只看盘上实物, 不采信自述)**:
  - ISS-214: `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` (扩到 154 锚点 + §10~§14) · `HW/check_netlist_selfconsistency.py` (16/16 selftest)
    · `HANDOFF/2026-11-16_hw-lead_ISS214_网表一致性第2轮与3条待裁自查.md` (23,472 B, 01:04) · 分片 hw.yaml 01:07
  - ISS-216: `MECH/MECH_BUDGET.md` (§2.1/§2.3.1/§3 口径改 buck) · `MECH/verify_budget.py` (P_CHARGE 0.8→0.50 + §8 自检)
    · `HANDOFF/2026-11-16_mech-lead_ISS216_充电耗散口径统一.md` (13,184 B, 00:55) · 分片 mech.yaml 00:57
· ★**main 独立复核 (自己跑门禁 + 自己 md5) 全过** ⇒ 落 `verified` (★不是 closed★) ⇒ 放出两个名额 ★
· ★**两个名额 = 本 job 的活: 从各总工交卷里的 needs_from 开下一批单** ★ (★兄弟 job 交接口径: 开单是派活 job 的活★)

★★**两单全部【原理图主线内】(★老板 2026-11-11 10:07 口径: PCB 布线/布局类一律不派, 排队等原理图定稿★)** ★
★**两单都不许外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)
★**凡要查资料的 ⇒ 自己网上查 + 标证据等级 + 查不到必须写降级方案** (不得把外部依赖挂着当阻塞项)
★铁律: 干活的人不许自签 ⇒ verify_by=main (main 独立复核后落账)
★不碰: PROJECT_TRACKER.md §0 / 任何分片 / 任何真源文件 (板/网表/脚表/原理图/BOM) / outbox
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0115_verify214_216_open217_218"

# ==================================================================
# ① ISS-214 → hw-lead  (已 verified, 本段只写 verify_result)
# ==================================================================
VERIFY_214 = """pass · 2026-11-16 01:1x 项目总工独立复核 (★不采信自述, 只看盘上实物 + 自己跑门禁★)
★**① 交付物 3 件** [实测]: `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` (★扩到 154 条锚点 + §10 八条 8 栏 + §11 附带发现 8 条 + §13 未决 V-1~V-8★) · `HW/check_netlist_selfconsistency.py` (★新增 5 个文件源 + text contains/calc 判据 + R5~R11 翻面判据★) · `HANDOFF/2026-11-16_hw-lead_ISS214_网表一致性第2轮与3条待裁自查.md` (23,472 B, 01:04 落盘, B1~B6 齐全) · 分片 `state/fragments/hw.yaml` 01:07 原子写 (artifacts 78 / needs_from 89 / V-1~V-8 全登记)
★**② 机器门禁实跑 (main 自己跑的)** [实测]: `python3 HW/check_netlist_selfconsistency.py` → **rc=0** (★现状守卫 ⇒ 4+8 组缺陷★仍在★ ⇒ rc=0 是预期状态★) · `--selftest` → **16/16 通过** (★原 9 条一条没删 + 新增 7 条, 含 calc-only 用例★) · `--expect-resolved` → **rc=1** (★缺陷尚未落表 ⇒ 应当是红的★; 实跑列出 R10 390Ω 档单 pin 0.608A > 0.5A / R11 三处 board 列仍未落表★)
★**③ 受保护文件 md5 逐字节未变** [实测] (★main 自己 md5sum 实跑, 不是抄 agent 的自述★): 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**4 个受保护文件全部与开工前一致★**
★**④ 边界实测**: 00:40 以后 `HW/` 下被改动的只有 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 与 `HW/check_netlist_selfconsistency.py` (本单允许的两个); `HW/PCB/_frame_reference.kicad_pcb` / `STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` 的 mtime = 01:10:27 ⇒ ★**那是自动生成链在跑, 不是本单 agent 碰的★** ⇒ 未碰网表/脚表/BOM/板/.kicad_pro/SPEC.json/CHARGE_BOARD_SPEC/任何 `state/gen_*.py`
★**⑤ 未决**: 12 组缺陷须随整链重出第 1 步落表 ⇒ ★**已开 ISS-217 承接"落表作业包 v1"★**; V-1~V-6 六条待裁项 (V-1/V-3/V-4 纯工程取舍 ⇒ 作业包里给默认值供项目总工签字; V-2 选型 / V-5 堆叠账口径 / V-6 阈值 3.0mm ⇒ 分别归总工/结构/本单落定)
★**⑥ 会话状态说明 (★如实记, 不掩盖★)**: 子会话 `agent:hw-lead:subagent:85841b8c` (7f8d0c5a) **status=timeout** (★01:09:39 被跑批超时掐掉, 掐在"final delivery checks"那一步 ⇒ ★**它最后那句交卷总结没发出来★**) ⇒ ★**但交付物、门禁脚本、分片全部已落盘 (★上面 ①②③ 全是 main 自己实跑复核的, 不依赖那句总结★)** ⇒ ★**⇒ 照常落 verified, 并把"跑批超时"写进 note, 不当没发生★**"""

# ==================================================================
# ② ISS-216 → mech-lead  (已 verified, 本段只写 verify_result)
# ==================================================================
VERIFY_216 = """pass · 2026-11-16 01:1x 项目总工独立复核 (★不采信自述, 只看盘上实物 + 自己跑门禁★)
★**① 交付物** [实测]: `MECH/MECH_BUDGET.md` (§2.1 峰值充电行 / §2.1 结构硬结论 / §2.3 结温行 / §2.3.1 / §3 / §6 全部改成 buck 口径) · `MECH/verify_budget.py` (`P_CHARGE` 0.8 → 0.50 + §8 口径自检 C1~C10) · `HANDOFF/2026-11-16_mech-lead_ISS216_充电耗散口径统一.md` (13,184 B, 00:55) · 分片 `state/fragments/mech.yaml` 00:57 原子写
★**② 机器门禁实跑 (main 自己跑的)** [实测]: `python3 MECH/verify_budget.py` → **rc=0** (★门禁绿: 数值对拍一致 + 充电耗散口径 = buck, 不是线性 0.8W★) · `--selftest` → **rc=0 · 反向用例 10/10 抓到了** (含反向5 漏 DCR 项 / 反向7 K_ILIM 全取 320 / 反向10 残留旧线性口径) · `python3 MECH/check_demo_struct_truth.py` → **rc=0** (20/20 组; ★6 个 PCB 类 id 仍是 FAIL = 正确状态, 排队等原理图定稿★)
★**③ 受保护文件 md5 逐字节未变** [实测] (★main 自己 md5sum 实跑★): 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · `MECH/hinge_usb_check.py` `3425bc141508de8a35f34c7cf7b803e8` · `MECH/service_port_check.py` `9b24bf985764880f0105aee677fba6a8` · `MECH/hw_cross_review_check.py` `e521387b87b0fcdf9f22d56f14199967` · `MECH/display_biosafety_v2_check.py` `29c77fc3fc823048b1d96c9500d28dd7` · `MECH/check_demo_struct_truth.py` `700c4e3638cb7779df297cc8b0607884` ⇒ ★**全部与开工前一致★**
★**④ 关键数值复核** [推算/官网]: buck 耗散三档 0.4600 / 0.5164 / 0.5740 W ⇒ 落在已定区间 0.45-0.57 W ✓; 端件 ΔT 83.3 K ⇒ 表面 108.3 °C ⇒ 60 °C 判据 ⇒ P_max 0.210 W ⇒ 现耗散 0.50 W 超 2.38× ⇒ 金属热路仍然必须 ✓ (★方向没变, 绝对值变了★); 功率守恒 ICHG/IIN = 1.216 / 1.071 (规格书 0.822/0.933 是倒数) ✓
★**⑤ 边界实测**: 00:40 以后 `MECH/` 下被改动的只有 `MECH/MECH_BUDGET.md` 与 `MECH/verify_budget.py` (本单允许的两个) + `MECH/_frag_update_iss216.py` (分片写入脚本) ⇒ 未碰 `HW/` 任何文件 / 3 个受保护 check 脚本 / `MECH/check_demo_struct_truth.py` / 打印包 / PCB 布线布局 / 判据阈值
★**⑥ 会话状态说明 (★如实记★)**: 子会话 `agent:mech-lead:subagent:900f6943` (a628e635) **status=done** (00:55 交卷, 交卷全文在 transcript 里, 四条命令输出齐全)
★**⑦ 未决**: 端件金属热路质量代价 (u8 未定) ⇒ ★**已开 ISS-218 承接 (只出参数化模板, 不预扣 §3 现有重量)★**; 打印包第三档试样 ⇒ 同 ISS-218; 390 Ω 档单 pin 超 0.5A ⇒ 仍归 hw-lead (ISS-217 的 V-4 确认单里处理); ISS-126 裁关闭 / 本闸是否挂每日巡检 ⇒ main 地界, 本 job 不代裁"""

# ==================================================================
# ③ 新开 ISS-217 → hw-lead
# ==================================================================
BRIEF_217 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**ISS-211 (4 条) + ISS-214 (8 条) 共 12 组"网表/规格自相矛盾"★, 从"两轮规格页"汇成 ★**一份【整链重出 第 1 步 · 原理图侧落表作业包 v1】★** ⇒ 逐组给出 ★**(真修法在哪个真源 · 改成什么 · 改完跑哪条命令 · 翻面判据是哪条 · 证据等级)★** ⇒ ★**并把机器门禁扩到"作业包漏一条就红"★** ⇒ ★**本单不许改网表 / 脚表 / BOM / 板 / .kicad_pro / 任何生成器 / SPEC.json / CHARGE_BOARD_SPEC**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 01:0x~01:2x 实测, 不是推测★)** ★★
· ★**ISS-211 (11-15 23:5x 交卷, 已 verified) 与 ISS-214 (11-16 01:0x 交卷, 本轮刚落 verified) 两轮规格页都在, 但规格页只说"这条错在哪、真修法在哪", 没说"落表那趟具体改哪一行、改成什么"★** ⇒ ★**而落表那趟是【整链重出 第 1 步】(`state/RECHAIN_STEP1_LANDING_SPEC.md`: C/E 两项已定可落 · D 项等评审) ⇒ 板只改一次 ⇒ 这一趟必须一次落干净, 不许分批试错★** ⇒ ★**⇒ 缺的就是这份"作业包": 谁改、改哪行、改成什么、跑哪条命令、怎么算翻面★**
· ★**这正是【原理图主线】的真瓶颈**: 老板 2026-11-11 10:07 定的口径是"先解决原理图绘制的问题" ⇒ 原理图侧的网表/规格自相矛盾就是原理图侧的问题 ⇒ ★**本单是原理图主线的收口件, 不是 PCB 类, 可以派★**
· ★**同时它也是下一趟落表的唯一输入**: 落表那趟由项目总工执行, 作业包就是它的 SOP ⇒ ★**没有作业包, 落表那趟就会把规格页当成"参考"而不是"逐条照做"★**

★★**★① 输入件 (★都已 verified, 不许重复定性, 不许推翻, 直接用★)** ★★
· ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** ★= ISS-211 v1 (4 条 · §1) + ISS-214 v2 (8 条 · §10 · 每条 8 栏齐) + §11 附带发现 8 条 + §13 未决 V-1~V-8 + §14 边界自查 (★机读锚点表 = 唯一真源在 `HW/check_netlist_selfconsistency.py` 的 `EXPECT` 里, 154 条★)
· ★**`HW/check_netlist_selfconsistency.py`** ★= 现状守卫 154 锚点 · `--selftest` 16/16 · `--expect-resolved` 翻面口径 R1~R11
· ★**`HANDOFF/2026-11-16_hw-lead_ISS214_网表一致性第2轮与3条待裁自查.md`** ★= 上一轮的交卷报告 (B1~B6)
· ★**`state/RECHAIN_STEP1_LANDING_SPEC.md`** ★= 落表那趟的既有作业包 (C 项复位 P0 / E 项 NC 拆分 / D 项去耦待评审) ⇒ ★**你这份要和它对齐, 不许另起一套编号★**

★★**★② 你要出的作业包本体 (★每组 8 栏, 缺一栏门禁就红★)** ★★
★**栏位 (一字不许少)**: ① 项号 (d1..d11 + 附带 #1..#8, 与规格页条号一一对应) ② 现状逐字 + 行号 [实测] ③ 缺陷一句话 ④ ★**真修法在哪个真源 (精确到: 哪个文件的哪一行 / 哪个 JSON key / 哪个生成器参数)★** ⑤ ★**改法 (逐字值: 改哪个文件哪一行, 改成什么字面值)★** ⑥ 改完跑哪条命令 ⑦ 翻面判据 (门禁哪条 R#) ⑧ 证据等级 [官网]/[实测]/[媒体]/[推算]/[0数据] ★
★**★3. 三项补差 (★都是规格页 §11 附带发现里【还没被规格覆盖】的那几条, 本轮必须补齐★)** ★
· ★**补差 A · `imp` 一个字段混着用 (规格页 §11 附带发现 #1)★** ⇒ ★**NET 行的"阻抗"与器件行的"阻值"在 DSI 组是两个不同的物理量 (NET 行 100Ω = MIPI 差分阻抗 / 器件行 0Ω = 直通位), 在 USB 组却被塞进同一个字段★** ⇒ 你要出 **字段拆分方案** (串阻值字段 vs 差分阻抗字段各叫什么 · 哪些连接该填哪个 · 对 `state/gen_netlist.py` 里 conn_row() 的改动面有多大) + **迁移清单** (哪几行要改) + 改完后 `python3 state/check_netlist.py` 与 `python3 state/check_netlist_pins.py` 应该是什么结果 ⇒ ★**只出方案, 不许改生成器★**
· ★**补差 B · ESD 位置判据 5mm vs 3.0mm 口径收口 (规格页 §11 附带发现 #3 / 未决 V-6)★** ⇒ ★**ISS-211 §5.2 写 ≤5mm, 而 `state/gen_schematic_pages.py` 的 P9 页自引的 ISS-085 结构总工回执写 ≤3.0mm ⇒ 按 3.0mm 判 (项目自己的规矩, 更严)★** ⇒ 你要把 **门禁 R9 的翻面阈值从 5.0 改成 3.0** (★只改翻面判据, 现状断言不动★) ⇒ ★**并且在 `--selftest` 里加一条反向用例证明阈值真被读到 3.0 而不是 5.0 (★自己把 3.0 改回 5.0 必须变红★)★**
· ★**补差 C · 充电链 π 滤波拓扑 + `J_CHG` 位号双义 (规格页 §11 附带发现 #4 / #6 · 未决 V-7 / V-8)★** ⇒ ★**`C_VBUS_OUT` (100µF) 在网表里是【串联】在 BQ25896 的 DC 输入路径上 (稳态充不了电), 而 `HW/CHARGE_BOARD_SPEC.md` §7 的 `C_VBUS_BULK` 是【对地】100µF, 且 §7.1 计数对账表的"现行网表引用 80 行"已过期★** ⇒ 你要出 **π 滤波真值拓扑规格** (哪只位号对地 / 哪只串联 / 各自容量判据) + **`J_CHG` 位号消歧方案** (网表=铰链 FPC 1×10p@0.5mm board=HINGE vs 板文件=SoM BTB 100pin, 两个物理件 ⇒ 命名规则建议 + 对 ISS-199/ISS-202 的影响) ⇒ ★**充电板不进 demo 板 ⇒ 本单只出规格, 不碰网表也不碰板★**

★★**★4. 待裁项确认单 (★不许代拍, 只出"一句话可勾选"的确认单★)** ★★
· ★**V-1 (USB 串阻取 22Ω 外部串阻 还是 0Ω 靠 SoM PHY 内部匹配) / V-3 (BAT_DET 分压比 方案 A 2.0M+1.2M 还是 降级档 D) / V-4 (R_ILIM 档位: 解① 475~510Ω 还是 解② 390Ω + J_CHG 4 pin 并联)★** ⇒ ★**这三条是【纯工程取舍, 有量化代价】⇒ 你给: 默认值 + 备选 + 代价 (含对 60ms/充电时间/单 pin 载流/皮肤温度的影响) + 落表后影响哪几行 ⇒ 供项目总工签字★★
· ★**V-2 (ESD 方案二选一 + 型号) = 选型 ⇒ 仍属老板级** ★⇒ 你只给"官网参数满足的候选 + 判据串 + 查不到的降级方案", 不许代拍
· ★**V-5 (堆叠账唯一口径) = 归 mech-lead + 项目总工** ★⇒ 你只写清 P9 页要改成【引用哪个数】, ★**不许自带第二个堆叠数★**
· ★**V-6 (阈值 3.0mm) = 本单补差 B 已落定** ★⇒ 写进作业包即可

★★**★5. 机器门禁扩项 (★hw-lead 地界, 只读脚本, 不写任何项目文件★)** ★★
· ★**扩 `HW/check_netlist_selfconsistency.py`: 加"作业包完整性"自检** ⇒ ★**作业包里必须逐组出现 (项号 · 真修法文件 · 改法 · 命令 · 翻面判据 id) ⇒ 缺任何一组 ⇒ 红★** ⇒ ★**`--selftest` 加反向用例 (★删掉一组必须变红★)★** ⇒ ★**并做三方对齐: 作业包项号 ↔ 规格页 §10 条号 ↔ 门禁 R# 必须对得上 (对不上 ⇒ 红)★**

★★**★6. 交付物 (★就这四件, 不许多写, 不许改别人的地界★)** ★★
· ★**新建** `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` ★= 作业包本体 (★12 组 + 附带 8 条 + 3 项补差 + 6 条待裁确认单★)
· 扩 `HW/check_netlist_selfconsistency.py` ★= 作业包完整性 + 三方对齐 + R9 阈值 3.0mm + 新增反向用例
· ★**新建** `HANDOFF/2026-11-16_hw-lead_ISS217_落表作业包v1.md` ★= B1~B6 齐全
· `state/fragments/hw.yaml` ★= ★**走 `python3 state/frag_write.py` 原子写** (★禁止 `open(p,"w")`★): +artifacts +1 claim (`schematic_landing_workpacket_v1`) +1 need (★6 条待裁确认单 to main★)

★★**★7. 验收命令 (★交卷前自己实跑, 原样贴进交卷★)** ★★
```
python3 HW/check_netlist_selfconsistency.py              # rc=0 (现状守卫; ★缺陷仍在是预期★)
python3 HW/check_netlist_selfconsistency.py --selftest    # rc=0 (★原 16 条一条不许删 + 新增用例全过★)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★缺陷尚未落表 ⇒ 应当是红的★)
python3 state/check_netlist.py                           # rc=0
python3 state/check_netlist_pins.py                      # rc=0
python3 state/merge.py                                   # rc=0
python3 state/gate_check.py                              # rc=0, 【Q1】18/18
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```
★**受保护 md5 期望值 (★必须逐字节一致★)**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**以你开工前自己跑出来的 md5 为准, 并把开工前/交卷后两个值都贴出来★**

★★**★8. 边界 (★违反一条即交卷无效★)** ★★
· ★**不许改**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard.kicad_pro` · `HW/SCHEMATIC_V1_SPEC.json` · `HW/CHARGE_BOARD_SPEC.md` · `HW/EMC_PRECHECK.md` · 任何 `state/gen_*.py` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · `MECH/` 与 `SW/` 任何文件 · 任何别的总工的分片
· ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★)
· ★**零外发**: 不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**凡要查资料 ⇒ 自己在官网/官方 datasheet 上查 + 标证据等级 + 查不到写降级方案 ⇒ 没有"批一句可以发"这个选项★**
· ★**不许替老板拍**: 整机屏路线 / 波导归属 / FOV / 板长方案取舍 / 充电板是否留 / 端件截面 u8
· ★**本单实物 [实测] = 0 条** (板与屏不在本机) ⇒ 标 [实测] 的一律是"本机脚本/本机文件实读", 不是"实物测过"
· ★**不许自己改 issue_log 状态** (★verify_by=main, 干活的人不许自签★)"""

# ==================================================================
# ④ 新开 ISS-218 → mech-lead
# ==================================================================
BRIEF_218 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**打印包那个"两档并行试样"的假二选一落成【第三档试样】(10.50×4.80 FDM 直成型 + 10.25×4.55 金属·CNC)★** ⇒ 出 ★**加工规格 + 加工余量 + 逐项测量清单条目 + 生成器/门禁落项 (只增不改, 既有基线必须仍全绿)★** ⇒ ★**外加: 端件金属热路的 u8 参数化重量账模板 (只出模板, 不预扣 §3 现有重量)★** ⇒ ★**本单不许改 HW/ 下任何文件 / 不许碰 PCB 布线布局**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 01:0x~01:2x 实测, 不是推测★)** ★★
· ★**ISS-213 (11-15 23:5x 交卷, 已 verified) 已判死"两档并行试样"是个假二选一**: ★**现两档候选 9.50×3.60 最坏 0.13/0.02 · 10.00×4.20 最坏 0.38/0.32, 判据 0.60 ⇒ 两档都不合格★** ⇒ ★**ISS-213 自己出了第三档 10.50×4.80 (FDM 直成型, 最坏 0.63/0.62) 与 10.25×4.55 (金属·CNC), 但【还没落成"可下片的试样 + 门禁"】★** ⇒ ★**⇒ 本单把第三档补成实物级交付**
· ★**ISS-216 (11-16 00:55 交卷, 本轮刚落 verified) 把充电耗散口径换成 buck 之后, 端件外表面从 158 °C 落到 108.3 °C, 但仍超 60 °C 判据 ⇒ 金属热路这条结构义务一条没减 ⇒ 而端件金属件的重量要落进 §3 的哪一行取决于端件截面 u8, u8 未定 ⇒ ★**本单只出"u8 参数化重量账模板", 让 u8 一拍下来就能直接代入, 不预扣、不猜数★**

★★**★① 现状 (★main 实测, 你要自己复核一遍★)** ★★
· ★**`MECH/print/gen_print_pack_revb.py`** 的参数表里: `tc_open_w`/`tc_open_h` = 9.50/3.60 (现口径) 与 `tc_open_w2`/`tc_open_h2` = 10.00/4.20 (ISS-089 并行试样, 待授权) ⇒ ★**第三档要作为【新增参数】接进去, 不许改这两个既有参数的含义★**
· ★**`MECH/print/verify_pack_revb.py`** = 解析几何精确求尺寸 + STL 逐点互验两段式自检 ⇒ ★**main 实跑现状: 尺寸判据 93/93 + STL 逐点互验 38/38 (fit_coupon 15/15 · temple_cage 18/18 · frame_typec 5/5)★** ⇒ ★**★这三组数字是本单的基线: 改完必须【仍然全绿】, 且新条目数要写清 (★不许为了加第三档把既有基线改小★)★**
· ★**`MECH/print/README.md`** = Rev B 台账 (Rev A 已作废的原因都在里面) · ★**`MECH/print/GEOM_SPEC_REVA.md`** = 几何规格 · ★**`MECH/print/MEASURE_CHECKLIST.md`** = 逐项测量清单 · ★**`MECH/print/ENV_PROBE_20261101.md`** = ★**本机物理上不能打印也不能量测的证据 (打印机跨网段不可达 / 无切片器 / 无量具)★**

★★**★② 你要出的东西 (★四件, 不许多写, 不许改别人的地界★)** ★★
· ★**新建** `MECH/print/PRINT_COUPON_TIER3_SPEC.md` ★= 第三档试样规格: ★**(a) 两档各自"为什么合格"的最坏余量算式 (对判据 0.60) (b) 加工余量** (FDM: 收缩率 / 孔径补偿 / 层纹方向; 金属 CNC: 公差带 + 表面处理) ★**(c) 逐项测量清单条目 (按 `MECH/print/MEASURE_CHECKLIST.md` 的既有格式接进去) (d) 本机不可打印不可量测的降级说明 (引 `MECH/print/ENV_PROBE_20261101.md`)★** ⇒ ★**加工余量取值要标证据等级: 查得到就写 [官网] + 出处, 查不到写 [0数据] + 降级方案 (★不许写成"经验值"糊过去★)★
· 扩 `MECH/print/gen_print_pack_revb.py` 与 `MECH/print/verify_pack_revb.py` ★= 把第三档做成【参数化第三档】: 生成器出件 + 自检里加"第三档两档余量 ≥ 判据 0.60"的对拍 ⇒ ★**★并且给自检加一个自检模式 (★`--selftest`★) 带反向用例: 把第三档尺寸改回 9.50×3.60 必须变红★** ⇒ ★**既有 93/93 + 38/38 必须仍全绿, 判据 0.60 一个不许松, 既有阈值一个不许动★**
· ★**新建** `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` ★= 端件金属热路的 u8 参数化重量账模板: ★**(a) 硬指标 R_热路 ≤ 70 K/W; 铝 6063 同几何 1.641 K/W ✅ / 打印件 PA6-CF 1944 K/W ❌ (b) 端件截面 u8 取 3~5 个值 ⇒ 金属件质量区间 (c) 代入 `MECH/MECH_BUDGET.md` §3 的 W6/W9 的方法 (d) ★**§3 现有重量数字一个不许改、不许预扣 (u8 未定) 的字样写死在这份模板里★★**
· ★**新建** `HANDOFF/2026-11-16_mech-lead_ISS218_打印包第三档与热路重量模板.md` ★= B1~B6 齐全 + `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py` 原子写, ★禁止 `open(p,"w")`★): +artifacts +1 claim (`print_coupon_tier3_spec` / `endpoint_metal_path_mass_template`) + needs

★★**★3. 验收命令 (★交卷前自己实跑, 原样贴进交卷★)** ★★
```
python3 MECH/print/verify_pack_revb.py            # rc=0 (★既有 93/93 + 38/38 仍全绿 + 第三档新增条目全绿★)
python3 MECH/print/verify_pack_revb.py --selftest  # rc=0 (★反向用例全被抓; ★若现有脚本还没有这个模式 ⇒ 你给它加上并说明★)
python3 MECH/print/verify_pack.py                  # rc=0 (★Rev A 46/46 不得变红★)
python3 MECH/verify_budget.py                     # rc=0 (★上一轮的 buck 口径不许被本单改回去★)
python3 MECH/check_demo_struct_truth.py           # rc=0
python3 state/merge.py                            # rc=0
python3 state/gate_check.py                       # rc=0, 【Q1】18/18
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```
★**受保护 md5 期望值 (★必须逐字节一致★)**: 网表 `c78f991283cc82d56c8e3dd31657c785` / 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**以你开工前自己跑出来的 md5 为准, 开工前/交卷后两个值都贴出来★**

★★**★4. 边界 (★违反一条即交卷无效★)** ★★
· ★**不许改**: `HW/` 下任何文件 (含网表 / 脚表 / 板 / .kicad_pro) · `MECH/MECH_BUDGET.md` 的 §3 现有重量数字 · `MECH/check_demo_struct_truth.py` · 3 个受保护 check 脚本 (`MECH/hinge_usb_check.py` / `MECH/service_port_check.py` / `MECH/hw_cross_review_check.py` / `MECH/display_biosafety_v2_check.py`) · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · 任何别的总工的分片
· ★**不许碰 PCB 布线 / 布局 / 板框** · ★**判据阈值 0.60 一个不许松** · ★**打印包既有基线 93/93 + 38/38 必须仍全绿**
· ★**零外发**: 不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ ★**查资料自己上官网 + 标证据等级 + 查不到写降级方案★
· ★**不许替老板拍**: 整机屏路线 / 波导归属 / FOV / 板长方案取舍 / 充电板是否留 / 端件截面 u8
· ★**本单实物 [实测] = 0 条** (本机物理上不能打印也不能量测) ⇒ 交付物是"可直接下片的 STL + 逐项测量清单", 不是"已打印"
· ★**不许自己改 issue_log 状态** (★verify_by=main, 干活的人不许自签★)"""

NEW = [
    {
        "id": "ISS-217",
        "title": "★★[主线内·原理图/网表侧·内部活] 12 组网表/规格自相矛盾 (ISS-211 四条 + ISS-214 八条) ⇒ 汇成【整链重出 第 1 步 · 原理图侧落表作业包 v1】+ 3 项补差 (imp 字段拆分 / ESD 阈值 5→3.0mm / π 滤波拓扑 + J_CHG 位号双义) + 门禁扩到\"作业包漏一条就红\" (不改网表·不改板)",
        "severity": "high",
        "source_blocker": "ISS-214",
        "desc": "★**ISS-211 (4 条) 与 ISS-214 (8 条) 两轮规格页都已 verified, 但规格页只说\"错在哪、真修法在哪\", 没说\"落表那趟具体改哪一行、改成什么、跑哪条命令、怎么算翻面\"★** ⇒ ★**落表那趟 = 整链重出 第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md` · C/E 两项已定可落 · D 项等评审) ⇒ 板只改一次 ⇒ 这一趟必须一次落干净, 不许分批试错★** ⇒ ★**缺的就是这份作业包 (= 落表那趟的 SOP)** ★ ★**这正是【原理图主线】的真瓶颈 (老板 2026-11-11 10:07: 先解决原理图绘制的问题) ⇒ 本单是原理图侧收口件, 不是 PCB 类★** ★ ★**附加 3 项补差**: ★**A · `imp` 一个字段混着用 (NET 行差分阻抗 vs 器件行阻值) ⇒ 字段拆分方案 + 迁移清单; B · ESD 位置判据 5mm vs 3.0mm ⇒ 门禁 R9 翻面阈值对齐 3.0mm + 反向用例; C · `C_VBUS_OUT` 串联在 BQ25896 DC 输入路径 (稳态充不了电) + `J_CHG` 位号双义 ⇒ π 滤波真值拓扑 + 消歧方案 (充电板不进 demo 板 ⇒ 只出规格)★** ★ ★**待裁项**: V-1/V-3/V-4 纯工程取舍 ⇒ 作业包给默认值供项目总工签字; V-2 选型仍属老板级; V-5 堆叠账归结构; V-6 本单落定 ★ ★**本单不改网表/脚表/BOM/板/.kicad_pro/生成器/SPEC.json/CHARGE_BOARD_SPEC, 受保护 md5 一个字节不许变; 零外发★**",
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-16",
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 01:2x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-214 交卷里的未决 V-1~V-8 + 规格页 §4 落表时机总表 + §5.2 翻面条件★** ⇒ ★**hw-lead 名额的上一条 ISS-214 已于本轮 01:1x 落 verified ⇒ 名额空出来 ⇒ 本单是第 3 轮★** ★ ★**本单 = 落表那趟的唯一输入 (SOP) ⇒ 不落作业包, 落表那趟就会把规格页当参考而不是逐条照做★**",
        "task_brief": BRIEF_217,
    },
    {
        "id": "ISS-218",
        "title": "★★[主线内·结构侧·内部活] 打印包第三档试样落地 (10.50×4.80 FDM 直成型 + 10.25×4.55 金属·CNC · 两档并行试样已被判死) ⇒ 加工规格 + 加工余量 + 测量清单 + 生成器/自检落项 (既有 93/93 + 38/38 必须仍全绿) + 端件金属热路 u8 参数化重量账模板 (不预扣 §3)",
        "severity": "high",
        "source_blocker": "ISS-213",
        "desc": "★**ISS-213 已判死\"两档并行试样\"是个假二选一** (★现两档 9.50×3.60 最坏 0.13/0.02 · 10.00×4.20 最坏 0.38/0.32, 判据 0.60 ⇒ 两档都不合格★) ⇒ ★**ISS-213 自己出了第三档 10.50×4.80 (FDM 直成型) 与 10.25×4.55 (金属·CNC), 但还没落成\"可下片的试样 + 门禁\"★** ⇒ 本单补成实物级交付 (★加工规格 + 加工余量 + 逐项测量清单条目 + 生成器参数化第三档 + 自检反向用例★) ★ ★**外加 ISS-216 留下的账**: ★**buck 口径把端件外表面从 158 °C 拉到 108.3 °C, 但仍超 60 °C 判据 ⇒ 金属热路这条结构义务一条没减; 而端件金属件的重量落进 §3 哪一行取决于端件截面 u8, u8 未定 ⇒ 本单只出 u8 参数化重量账模板, 不预扣、不猜数★** ★ ★**本单不改 HW/ 下任何文件 / 不碰 PCB 布线布局 / 判据 0.60 不许松 / 打印包既有基线 93/93 + 38/38 必须仍全绿 / 零外发★**",
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-16",
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 01:2x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-213 交卷里的 need `iss213_mech_typec_third_candidate` (打印包两档并行试样是假二选一 → 第三档) + ISS-216 交卷里的 need `iss216_mech_endpoint_metal_path_mass_after_u8` (端件金属热路质量账待 u8)★** ⇒ ★**mech-lead 名额的上一条 ISS-216 已于本轮 01:1x 落 verified ⇒ 名额空出来 ⇒ 本单是第 3 轮★** ★ ★**本单 = 结构侧唯一可推进的活 (6 个 PCB 类 FAIL 仍在排队等原理图定稿, 按老板 2026-11-11 10:07 口径不派)★**",
        "task_brief": BRIEF_218,
    },
]


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    import fcntl
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            raw = f.read()
        log = yaml.safe_load(raw)

        rt = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("❌ yaml 往返不一致 ⇒ 拒绝落盘")
            return 2
        print("✅ yaml 往返逐字节一致 (自证通过)")

        issues = log.get("issues") or []
        by_id = {i.get("id"): i for i in issues}

        # ---- ① 清僵尸 fixing: ISS-214 / ISS-216 → verified ----
        for iid, vr, fx in (("ISS-214", VERIFY_214, "HANDOFF/2026-11-16_hw-lead_ISS214_网表一致性第2轮与3条待裁自查.md"),
                            ("ISS-216", VERIFY_216, "HANDOFF/2026-11-16_mech-lead_ISS216_充电耗散口径统一.md")):
            it = by_id.get(iid)
            if it is None:
                print("❌ %s 不存在 ⇒ 中止" % iid)
                return 2
            if it.get("status") != "fixing":
                print("⚠ %s status=%s (不是 fixing) ⇒ 跳过落账" % (iid, it.get("status")))
                continue
            it["status"] = "verified"
            it["fixed_at"] = "2026-11-16"
            it["verify_date"] = "2026-11-16 01:1x"
            it["verify_result"] = vr
            it["fix_ref"] = fx
            it["note"] = (it.get("note") or "") + (
                "\n★**2026-11-16 01:1x 队列自动派活 job (fb67af40) 落 `verified` (★清僵尸 fixing·第 17 次复发★)**:\n"
                "★**实测**: 子会话已结束 (hw-lead 85841b8c = timeout 01:09:39 / mech-lead 900f6943 = done 00:55) ⇒ "
                "交付物已落盘 ⇒ ★**但 brief 不许子 agent 改 issue_log ⇒ status 停在 `fixing` ⇒ `advance.py` 的 in_flight 规则 ⇒ 名额被占住 ⇒ A 段 0 条 ⇒ 队列断线★**\n"
                "★**main 独立复核 (只看盘上实物 + 自己跑门禁 + 自己 md5) 通过 ⇒ 落 `verified` (★不是 closed★) ⇒ 放出名额★**\n"
                "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 板/网表/脚表/原理图/BOM 一个字节未动 ★\n"
            )
            print(" - %s fixing → verified (main 独立复核通过)" % iid)

        # ---- ② 新开两单 ----
        for n in NEW:
            iid = n["id"]
            assert iid not in by_id, "%s 已存在 ⇒ 中止" % iid
            assert n["owner"] in ("hw-lead", "sw-lead", "mech-lead"), "%s owner 非法" % iid
            assert n["verify_by"] == "main", "%s verify_by 必须 main" % iid
            assert n["severity"] in ("blocker", "high", "medium", "low"), "%s severity 非法" % iid
            issues.append(n)
            print(" - 新开 %s → %s (%s)" % (iid, n["owner"], n["title"][:48]))

        log["issues"] = issues
        shutil.copy2(LOG, BAK)
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("备份:", BAK)
        print("issues 总数:", len(issues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
