# ISS-223 续做任务书 (hw-lead)

★**上一会话 `agent:hw-lead:subagent:359d0e98` status=timeout @04:20:44 ⇒ 半成品, 本单续做** ★
★**同一个单、同一个 agent ⇒ 不占第二个名额** ★

★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: ★**(A)** 把 ISS-220 漏掉的 3 条分片声明补落盘; ★**(B)** 落表第 2 批 = V-1 已裁的那批 (d5 + 补差A 值迁移); ★**(C)** 修作业包 F-1~F-5; ★**(D)** 把 V-3 变可拍 (官方参数自查) ★ ⇒ 出 ★**(1) 落表记录 · (2) 真源改动 + 重生成网表/脚表 · (3) 门禁未落表条数前后对比 · (4) 交接单 + 分片** ★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 04:1x 实测, 不是推测★)** ★★
· ★**ISS-220 已把 6 组落进盘 (未落表条数 50 → 29)**, 但 ★**交付物 ④ 分片实测 0 条** (`hw.yaml` mtime 01:59:34 早于派活 · `iss220` 命中 0) ⇒ 3 条口径声明下游看不见 ★
· ★**V-1 已裁 = 22Ω** (依据全 [实测]: 板 `R_SER_USB_D_P/N = 22Ω±1%` + 网表器件行 L431/L432 `22Ω±1%` + 门禁 EXPECT「NET 行 value 含 22Ω」) ⇒ ★**d5 那 8 条红现在能落** ★
· ★**ISS-220 查出的 F-1~F-5 是作业包自身的病** ⇒ 不修, 第 3 批还会撞同样的坑 ★
· ★**V-3 卡在 SoM ADC 参数缺失** ⇒ 现在不是「不值得拍」, 是「拍不了」⇒ 本单去把它变成可拍 ★

★★**交付物 (6 件, 少一件即无效) ★★
① ★**补落 ISS-220 的 3 条分片声明** ★ ⇒ keys `iss220_chgboard_white_list_scope` / `iss220_i2ca_pullup_domain_1v8` / `iss220_ichg_ratio_true_value` ⇒ ★**必须走 `python3 state/frag_write.py --agent hw-lead` (原子写)★** ⇒ 交卷贴 `state/fragments/hw.yaml` 的 mtime 前/后 + 3 个 key 的命中行 (★不许手改 YAML★) ★
② ★**落表第 2 批 (V-1 = 22Ω)** ★ ⇒ 只许改: `HW/SCHEMATIC_V1_SPEC.json` (B-21/B-22 的 `imp` ⇒ `22Ω ±1%`) + `state/gen_netlist.py` (若取值优先级还要微调) + ★**补差A 的值迁移: A 组 20 条 `imp` 清空 · 差分阻抗搬进 `z_diff` (100Ω±10%) · B-21/B-22 的 `z_diff` = 90Ω±15%**★ ⇒ 改完 `python3 state/gen_netlist.py` 重生成网表/脚表 ⇒ ★**不许手工编辑生成产物 (CSV)★** ★
③ ★**门禁前后对比** ★ ⇒ `python3 HW/check_netlist_selfconsistency.py --expect-resolved` 的「未落表条数」★**落表前 = 29 ⇒ 落表后 = N (贴两次输出)★** ⇒ ★**不许靠删条目 / 改判据 / 改 EXPECT 锚点达成 ⇒ EXPECT 锚点组 d1..d11 一个不许减, R1~R11 判据代码一个字不许改** ★
④ ★**修作业包 F-1~F-5 五处** ★ ⇒ 逐条给出改法并改 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` (★作业包是 hw-lead 自己的产物, 本单可改★): F-1 d2 的真源是 `DEMO_DNP` 白名单 (不是 `add()` 的 dnp 参数) · F-2 d10 的 J_CHG 行真源是 `state/p10_rows.json` (作业包把文件归属写错了) · F-3 补差A 清空 A 组 `imp` 须与 `state/check_netlist.py` 判据 5 同趟改 (否则判据覆盖 20 行 → 0 行) · F-4 d10 的方向修正连带作废「皮肤侧 42.14°C / 不能再抬电流」这条结论 (它是按 0.822 算的) · F-5 #5 的白名单↔§7 双向对账在现状下不可能过 (§7 与网表是两个版本: 16 个位号网表里没有, 15 个 CHG_BOARD 位号不在 §7 里) ⇒ ★**每条都要写明「改了什么 + 为什么现在能改 / 还差什么」** ★
⑤ ★**V-3 可判化** ★ ⇒ 自己查 ★**RK3572 官方 datasheet**★ 里 SARADC_VIN5 (1.8V 域) 的 **输入漏电流 / 满量程 / 输入电容** ⇒ 出 V-3 (2.0M+1.2M vs 2.0M+1.0M) 的 ★**误差算式 + 可拍依据 + 推荐值 + 降级方案**★ ⇒ ★**不许代拍 (拍板权在 main/老板)★** ⇒ 查不到就写 [0数据] + 降级 ★
⑥ ★**板侧同步清单更新** (★只更新状态, 不许动板★) ⇒ B-1~B-6 六项逐条标: 因本批落表而变化的 / 仍等 V-2 与「板只改一次」那一趟的 ⇒ ★**交接单 (★新建★) `HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/hw.yaml` (★走 `state/frag_write.py` 原子写★)** ★

★★**边界 (★违反一条即本单无效★) ★★
· ★**不许改** `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` / ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★) ★
· ★**不许代拍** V-2 (ESD 方案与型号 = 老板级选型) / V-3 (本单只出依据) / V-4 (R_ILIM 档位 = 老板待拍, 已在 `DECISION_PENDING_2026-11-16.md` §3) / V-5 (结构侧堆叠口径) ⇒ ★**V-1 已由 main 裁 = 22Ω, 可直接落** ★
· ★**不许改判据阈值 / EXPECT 锚点** (★不许为了让门禁变绿而放松★) ★
· ★**不许改** `MECH/` 下任何文件 / `SW/` 下任何文件 / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 ★
· ★**开工前先给每个要改的真源文件留 `.bak_iss223` 副本** ⇒ 交卷贴每个真源文件的 md5 前/后对照 ★
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到必须写降级方案** ★
· ★**本单实物 [实测] = 0 条** (板不在本机) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」 ★
· ★**不许自签 issue_log** (★status 留给 main 落 verified★) ★

★★**交卷前必须实跑并把输出原样贴进回复 ★★
```
python3 HW/check_netlist_selfconsistency.py                    # rc=0 (现状守卫 + 作业包完整性 + 三方对齐)
python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (反向用例全抓到, 19/19 或更多)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # ★rc=1 是预期 (还有 BLOCKED 条目) ⇒ 必须贴 29 → N 的前后对比
python3 state/check_netlist.py                                  # rc=0 (全过)
python3 state/check_netlist_pins.py                             # rc=0 (每个针脚归属唯一)
python3 state/check_sch_erc.py                                  # rc=0 (ERC 违规数 = 0)
python3 state/check_sch_pinfull.py                              # rc=0 (图上脚数 = 表里脚数)
python3 state/merge.py && python3 state/gate_check.py           # rc=0 且 【Q1 交付齐备率】 18/18
```
★**落表若导致上面某条门禁变红 ⇒ 不许放松门禁, 也不许回退已落表的条目来凑绿 ⇒ 交卷报红并说明原因 (★main 复核)**★


==============================================================================

★★**续做登记 (main 2026-11-16 04:36 实测)** ★★

* ★

★★★ ★**2026-11-16 04:36 续做登记 (main 实测, 非推测) — 本单会话 `agent:hw-lead:subagent:359d0e98` status=timeout @04:20:44 ⇒ 半成品, 树处于「源与产物脱节」状态** ★★★
★**已落 (main 04:36 查 mtime 实测)**: `HW/SCHEMATIC_V1_SPEC.json` (04:15:47 ⇒ B-21/B-22 `imp` 已改 `22Ω ±1%`) · `state/gen_netlist.py` (04:21:43 ⇒ `conn_row()` 已支持 `imp`/`z_diff` 取值优先级 + 同趟 note 栏输出) · `state/check_netlist.py` (04:24:51 ⇒ 比对源改成 `imp or z_diff`, 与生成器同源) ★
★**未落 (main 04:36 查 mtime 实测)**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` mtime **仍 02:32:07** ⇒ ★**网表/脚表根本没重生成** (⇒ 源已改、产物没重生成 ⇒ md5 仍是旧值 `13f59a43…`/`a600afae…`) ★ · `state/fragments/hw.yaml` mtime **仍 01:59:34** + `iss220` 命中 **0** ⇒ ★**3 条声明没补落** ★ · `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` mtime **仍 02:35** ⇒ ★**F-1~F-5 没修** ★ · `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` **不存在** ⇒ 交接单没写 · V-3 (RK3572 SARADC_VIN5 官方参数自查) **没做** ★
★**main 04:36 实跑的门禁现状 (交给续做的人收)**: `HW/check_netlist_selfconsistency.py` → ★**rc=1, 2 条红**★
  · ★[d5_spec_b21_imp] 判据 'spec.connections[id=B-21].imp == 90Ω ±10% (与 MIPI 不同模板!)' 不成立 (实际 '22Ω ±1%')
  · ★[d5_spec_b22_imp] 判据 'spec.connections[id=B-22].imp == 90Ω ±10%' 不成立 (实际 '22Ω ±1%')
  · ⇒ ★**根因 = 规格页 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` L376/L378 那两个判据单元格还写着 V-1 裁前的旧值** ★
  · ⇒ ★**★预警 (main 提前算出来的)**: ★**重生成网表后 `d5_a291_value` / `d5_a292_value` (L366/L368, 网表 291/292 行 value == 90Ω ±10%) 也会变红** ⇒ ★**必须同趟把规格页这 4 个判据单元格 (90Ω ±10% ⇒ 22Ω ±1%) 一起改** ★ ⇒ ★**否则落表会把红从 2 条变成 4 条** ★ ⇒ ★**这不是「改判据凑绿」, 是「d5 的判据本体要跟着落表走」** ★
  · ★**其余门禁当前全绿 (main 04:36 实跑)**: `state/check_netlist.py` rc=0 · `state/check_netlist_pins.py` rc=0 · `SW/tools/demo_timing_check.py` rc=0 · `MECH/check_demo_struct_truth.py` rc=0 (23/23) · `SW/tools/check_demo_panel_spec.py` rc=0 (R1~R7, ISS-225 已把它升级成三方对账) ★
★**落表后必须同趟做的三件事 (顺序不许搞反, 缺一件就出事)**: ① 重生成网表/脚表 ⇒ md5 变 ② ★**落表记录 (`HW/SCHEMATIC_LANDING_V1_LANDED.md` + 本单交接单) 里必须能查到【落表单号 + 文件名 + 新 md5 + 旧 md5】四项** (⇒ MECH 闸 C21 / SW 闸 R6 的三方对账靠这个, 缺一项 = 门禁假红) ③ ★**把「MECH 闸要改哪条锚点」在交接单里点名写出 (本单不许改 `MECH/`, 锚点由 mech-lead 下一轮重锚)** ★ ⇒ ★**落表后 MECH 闸 G5b+C21 与 SW 闸 R6 会按设计变红 (锚点过期), 那不是故障, 是机制在工作** ★
★**状态 = 保持 `fixing`, 续做 (同一个 agent 续同一个单, 不占第二个名额)** ★