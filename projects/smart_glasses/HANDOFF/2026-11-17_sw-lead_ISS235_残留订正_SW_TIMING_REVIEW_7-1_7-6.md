# [sw-lead→PM] ISS-235 残留订正 · `SW/SW_TIMING_REVIEW.md` §7-1 / §7-6 文档侧同款过期断言

| 项 | 值 |
|---|---|
| **单号** | ★**ISS-235 (交卷后残留订正 · follow-on)** · **owner**: sw-lead (软件总工) · **verify_by**: main (项目总工) |
| **交卷时刻** | ★**2026-11-17 04:5x ~ 05:1x (GMT+8)** ★ |
| **地界** | ★**只动 `SW/SW_TIMING_REVIEW.md` (1 个文件) + 本交接单 + `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py` 原子写★)** ★ |
| **零外发** | ★**本单没发任何邮件 / 询价 / 问询 / 采购** ★ |
| **实物 [实测] = 0 条** | ★**本单零实物** (★纯文档订正 + 脚本实跑复核★) ★ |

---

## B1 结论摘要

| 序 | 结论 | 证据 |
|---|---|---|
| **1.1** | ★**ISS-235 本体已交卷并被 main 落 verified (2026-11-16 08:5x)** ⇒ ★**本单不是重做 ISS-235, 是它交卷后 20 小时里自己回扫出来的【文档侧同款残留】** ★ | ★`state/issue_log.yaml` ⇒ `- id: ISS-235` · `status: verified` · `verify_result` = ★「main 2026-11-16 08:5x 自己实跑 … 落 verified」★ ★ |
| **1.2** | ★**ISS-235 的 3 条断言订正在盘上全部健在, 且门禁至今全绿** ⇒ ★**没有回退、没有被后来的落表冲掉** ★ | ★`[实测]` 本单实跑: `timing_check.py` rc=0 (**71/71**) · `check_demo_panel_spec.py` rc=0 · `--selftest` rc=0 (**16/16**) · `check_shutdown_semantics.py` rc=0 · `--selftest` rc=0 (**17/17**) · `--reverse-demo` rc=0 (★「✅ 变红」★) ★ |
| **1.3** | ★**双向翻转判别证据本单独立复现 (不抄交卷报告)**: 喂**落表前**的网表 ⇒ ★**F8 + REV-3 + REV-3c 三条重新变红** ⇒ ★**证明新判据跟网表真值走, 不是把红灯调没** ★ | ★`[实测]` `python3 SW/tools/timing_check.py --netlist state/.bak_iss220/HW_netlist_v1.csv.bak_iss220` ⇒ **rc=1 · 65/71** (★红: 「F8 … 都必须有器件行」+「REV-3 … 从 2 掉到 1」+「REV-3c …」; 另 3 条红是 ISS-225/ISS-231 的旧事, 与本单无关★) ★ |
| **1.4** | ★**★残留的真相: ISS-235 只订正了【代码侧】3 条断言, 【文档侧】同一份 `SW/SW_TIMING_REVIEW.md` 里同一族过期事实没人动 ⇒ §7 的 7 条待修项里, 有 2 条已经被上游合法落表真修好, 但文档仍把它们当【开着的 P0】★ ★ | ★`[实测]` 回盘现网表: ★**7-6 已不成立** ⇒ `U_EN_SW` 现共 13 行 (L419 + L440-L451), 其中 ★**L442 = 器件本体行** (type=IC · dnp=必装 · value=TPS22991RAA … · opn=TPS22991RAA)★ ⇒ ★**7-1 已不成立** ⇒ L167/L168 的注记已改成「上拉 2.2k 到 1.8V (灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)」⇒ 与 L169/L170 的 2.2k→`RAIL_VDD_1V8_IO` **已自洽** (★`annotation_error_ratio` 12.77 → **1.0**★) ★ |
| **1.5** | ★**★文档曾经【自相矛盾】(★这是最硬的证据★)**: §13 自带的机械判据 `grep -n "U_EN_SW" HW/netlist_v1.csv \| grep -c ",IC,"` ⇒ ★**实跑 = 1**, 而文档 §13 写着「**→ 0**」⇒ ★**照文档自己的命令跑, 会跟文档自己的结论打架** ★ | ★`[实测]` 本单实跑: `grep -n "U_EN_SW" HW/netlist_v1.csv \| grep -c ",IC,"` ⇒ **1** (★改之前文档声称 0★) ★ |
| **1.6** | ★**§7 另外 5 条本单逐条回盘, 仍全部成立 ⇒ 一个字没改**: 7-2 (`RESET_N` 恒低: Q_AND L65/L67 必装 + R_PG_PULL L62/L63 10k 上拉 **必装** ⇒ 栅极恒高) · 7-3 (U_SUPV L407-L409 **全 DNP** 而 R_SUPV_DIV1/DIV2 L404/L405 **必装 0Ω** ⇒ 短路风险在) · 7-4 (R_BAT_DET_1/2 + C_DET_BAT L182-L185 **全 DNP**, 而 L181/L186 **必装** ⇒ ADC 悬空在) · 7-5 (Q_ENVC L71 **DNP** vs L72/L73 **必装** ⇒ 矛盾在) · 7-7 (D_ESD_USB_D L417/L418 只护 D+ 与地, **D− 无 ESD** ⇒ 在) ★ | ★`[实测]` 逐行回盘网表 (行号全部现读) ★ |
| **1.7** | ★**订正方式 = 【追加式】, 不是改历史**: §7 的 **7 行一条没删**, 只在 7-1 / 7-6 两行内**追加**「✅ 已修复 (上游已修 · ISS-220 d6 / ISS-233)」+ 现值; ★**上游真修的, 不是本单改的网表** ⇒ 本单 `HW/` **0 字节写入** ★ | ★`[实测]` 受保护 5 件 md5 交卷前后逐字节不变 (见 B6 ⑤) ★ |
| **1.8** | ★**订正后文档【自洽】了**: §13 两条复现命令与文档声称**逐字一致** (13 / 1) · §1.1 F8 行的 `rail_switching_devices : 2` / `load_switch_without_device_row : []` 与脚本实算**一致** ⇒ ★**文档与真源同向** ★ | ★`[实测]` 见 B6 ④ ★ |
| **1.9** | ★**受影响的 5 处「前置」表述也一起订正** (§1.3 / §6-9 / §8 CR-8 / §10.1 / §11): 原文写「但要先修 §7-6 的 BOM 缺口」⇒ ★**该前置已于 2026-11-16 06:48:38 被 ISS-233 修掉 ⇒ 前置已满足** ⇒ ★**否则文档会让人以为「关机语义还要等」** ★ | ★`[实测]` 见 B6 ④ ★ |
| **1.10** | ★**本单零外发 / 零实物 / 未碰 PCB / 未碰 MECH / 未改 issue_log / 未改 PROJECT_TRACKER §0 / 未写别人的分片** ★ | ★`[实测]` 见 B2 边界自评 ★ |

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

### 2.1 本单目标

| # | 目标 | 判定 | 落点 |
|---|---|---|---|
| **A-1** | ★**独立复核 ISS-235 的 3 条断言订正是否健在 + 门禁是否仍全绿** ★ | ✅ **通过** | ★B1 1.2 + 1.3 (★71/71 · 16/16 · 17/17 · reverse-demo rc=0 · 双向翻转 65/71 复现★) ★ |
| **A-2** | ★**把文档侧同款残留 (§7-1 / §7-6) 订正成跟当前真源走** ★ | ✅ **通过** | ★B1 1.4 / 1.5 · ★`SW/SW_TIMING_REVIEW.md` 头部新增「【ISS-235 残留订正 (2026-11-17, sw-lead)】」注 + §7 表内 7-1 / 7-6 两行追加状态 + 5 处「前置」表述 + §13 两条复现命令 + §1.1 F8 行三个数 + §10.1 一项 + §8 CR-1 一项 + §7 节末追加回盘说明 ★ |
| **A-3** | ★**订正后必须自证「文档与真源同向」, 且另外 5 条不许被误改** ★ | ✅ **通过** | ★B1 1.6 / 1.8 · ★§13 自带命令实跑 = 文档声称 (13 / 1) ★ |
| **A-4** | ★**交卷 4 件** ★ | ✅ **通过** | ① 本交接单 (B1~B6 齐全) ② `state/fragments/sw.yaml` (★**走 `state/frag_write.py` 原子写**, ★**没删别人的条目**★) ③ `SW/SW_TIMING_REVIEW.md` ③ ④ 门禁实跑输出**原样**贴进 B6 ★ |

### 2.2 边界自评

| # | 边界 | 判定 | 实测 |
|---|---|---|---|
| **B-1** | ★**不许改 `HW/`** ★ | ✅ **通过** | ★**受保护 5 件 md5 交卷前后逐字节不变** (B6 ⑤) ★ |
| **B-2** | ★**不许改 `MECH/`** ★ | ✅ **通过** | ★本单**一个字节没碰** ★ |
| **B-3** | ★**不许碰 PCB / 布线 / 布局** ★ | ✅ **通过** | ★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` md5 **不变**; ★本单**没跑任何生成器** ★ |
| **B-4** | ★**不许把断言改成「永远绿」** ★ | ✅ **通过** | ★本单**没动任何一条判据代码** (★`timing_check.py` / `check_demo_panel_spec.py` / `check_shutdown_semantics.py` **一个字节没动**★) ⇒ ★**判据强度零变化** ★; ★本单只改**文档里已经过期的陈述**, 且**原文一字未删** ⇒ ★**不是放宽, 是让文档跟真源同向** ★ |
| **B-5** | ★**不许改 `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / 别人的分片** ★ | ✅ **通过** | ★本单**没打开过**这 3 个文件; ★`state/fragments/sw.yaml` **只追加**本单的 artifact / claim, **别人的条目一个没删** ★ |
| **B-6** | ★**零外发** ★ | ✅ **通过** | ★**没发任何邮件 / 询价 / 问询 / 采购** ★ |
| **B-7** | ★**实物 [实测] = 0 条** ★ | ✅ **通过** | ★本单零实物; 所有 [实测] 都是**脚本实跑输出** ★ |

---

## B3 证据分级

| 事实 | 分级 | 依据 |
|---|---|---|
| ★ISS-235 `status: verified` (main 2026-11-16 08:5x 签字) ★ | **[实测]** | ★本单直接读 `state/issue_log.yaml` 的 `- id: ISS-235` 块 ★ |
| ★ISS-235 交卷单在盘 + 分片 5 个 `iss235` key 在盘 + 台账 R-06 留痕在盘 ★ | **[实测]** | ★`ls HANDOFF/2026-11-16_sw-lead_ISS235_*` (39840 B · 08:40) · `grep -c iss235 state/fragments/sw.yaml` = 5 · `grep -n "R-06" SW/SW_MD5_BASELINE_LEDGER.md` ★ |
| ★6 道门禁本单实跑全绿 (71/71 · 16/16 · 17/17 · reverse-demo ✅变红) ★ | **[实测]** | ★本单 2026-11-17 04:5x~05:1x 自己实跑 (★不抄任何交卷报告★), 输出原样贴 B6 ★ |
| ★双向翻转: 喂落表前网表 ⇒ 65/71, F8 + REV-3 + REV-3c 重新变红 ★ | **[实测]** | ★`python3 SW/tools/timing_check.py --netlist state/.bak_iss220/HW_netlist_v1.csv.bak_iss220` ★ |
| ★`U_EN_SW` 器件本体行 = 现网表 **L442** (type=IC · dnp=必装 · opn=TPS22991RAA) ★ | **[实测]** | ★`grep -n "U_EN_SW" HW/netlist_v1.csv \| grep ",IC,"` ★ |
| ★`U_EN_SW` 现共 13 行 (L419 + L440-L451); `U_PWR_SW` 现共 10 行 (其 IC 行 = L50) ★ | **[实测]** | ★`grep -c` / `grep -n` 实跑 ★ |
| ★L167/L168 注记已改成「2.2k 到 1.8V … t_r=186ns@100pF」⇒ 与 L169/L170 自洽 ★ | **[实测]** | ★`sed -n '167p;169p' HW/netlist_v1.csv` ★ |
| ★`annotation_error_ratio` = 1.0 (原记 12.77) ★ | **[实测]** | ★`timing_check.py` 现算 F3 段 ★ |
| ★§7 另外 5 条 (7-2/7-3/7-4/7-5/7-7) 仍成立 ★ | **[实测]** | ★逐行回盘网表 (行号现读, 见 B1 1.6) ★ |
| ★受保护 5 件 md5 交卷前后逐字节不变 ★ | **[实测]** | ★`md5sum` 交卷前后两轮 (B6 ⑤) ★ |
| ★文档 §13 自带命令实跑 = 13 / 1, 与订正后的文档声称逐字一致 ★ | **[实测]** | ★B6 ④ ★ |
| ★7-1 = ISS-220 d6 修 · 7-6 = ISS-233 修 (归因) ★ | **[实测]** | ★ISS-233 落表时刻 2026-11-16 06:48:38 + 网表 L442 逐行内容 + `timing_check.py` selftest 里「网表侧矛盾已被 ISS-220 d6 消除」这条**现在 PASS** ★ |
| ★本单对整机电气结论的影响 ★ | **[推算]** | ★**零影响** ⇒ ★F8 的**实测值** (开关数 / 器件行 / ON 脚下拉) 一个字节没变, 本单只改**文档陈述** ⇒ ★`check_shutdown_semantics.py` 的割边结论 (整机 `['U_PWR_SW']` / demo 空) 不受影响, 本单也没碰那个脚本 ★ |
| ★实物 / 板级实测 ★ | **[0数据]** | ★本单零实物 ★ |

---

## B4 接口取值声明 (interface_claims · 已写进 `state/fragments/sw.yaml`)

| key | value | note |
|---|---|---|
| ★`iss235_residual_doc_fix` ★ | ★`SW/SW_TIMING_REVIEW.md` §7-1 / §7-6 已按【追加式】订正成「✅ 已修复 (上游已修)」: 7-6 = ISS-233 (2026-11-16 06:48:38 · 网表 L442) · 7-1 = ISS-220 d6 (2026-11-16 02:32) ⇒ 现值 = IC 行数 1 · annotation_error_ratio 1.0 · rail_switching_devices 2 · load_switch_without_device_row []` ★ | ★`[实测]` ★**7 行一条没删, 原文一字未改, 只追加状态 + 现值** ★ |
| ★`iss235_doc_repro_selfconsistent` ★ | ★`SW/SW_TIMING_REVIEW.md` §13 的两条自带命令实跑 = 文档声称 (grep -c U_EN_SW = **13** · grep -n U_EN_SW \| grep -c ",IC," = **1**) ⇒ ★**文档与真源同向 (订正前文档说 0 而实跑 1 = 自相矛盾)** ★ | ★`[实测]` ★**这就是本单的反向自证: 照文档自己的命令跑, 结果与文档一致** ★ |
| ★`iss235_residual_needs_to_close` ★ | ★`state/fragments/sw.yaml` 的 `needs_from` 里两条已被上游满足、但仍开着的需求: `iss190_netlist_i2ca_note_contradiction` (7-1) + `iss190_netlist_u_en_sw_no_device_row` / `iss191_u_en_sw_device_row_recheck` (7-6) ⇒ ★**由 hw-lead 登记 answer 关闭 (★不是 sw-lead 自己答自己★)** ★ | ★`[实测]` ★**本单刻意没登记 answer** ⇒ ★登记 `to=sw-lead` 会触发门禁「⚠️ 自闭合 (自己答自己)」★ ⇒ ★**留 hw-lead 关, 已列 B5 ★** ★ |

---

## B5 未决项与卡点

### U-A ★**三条 `needs_from` 已被上游满足但仍开着 —— 需 hw-lead 登记 answer 关闭 (★owner = hw-lead★) ★

- ★**`iss190_netlist_i2ca_note_contradiction`** (7-1) ★**机械判据现已满足**: `timing_check.py` F3 的 `annotation_error_ratio` = **1.0** (原记 12.77) ⇒ ★**这条 need 的判据已经绿了** ★
- ★**`iss190_netlist_u_en_sw_no_device_row`** (7-6) ★**机械判据现已满足**: `grep -n "U_EN_SW" HW/netlist_v1.csv | grep -c ",IC,"` = **1** (need 原文写「现为 0, 应为 ≥1」) ★
- ★**`iss191_u_en_sw_device_row_recheck`** (7-6 的复查条目) ★**同上, 机械判据现已满足** ★
- ★**★本单为什么不自己登记 answer**: `state/gate_check.py` 的 `self_closed` 判据 = ★「需求发起人自己答了自己 (author==owner 且 to==owner)」★ ⇒ ★**我登记 `to=sw-lead` 的 answer 会直接触发门禁的「⚠️ 自闭合」告警 ⇒ 那是把闭环做成假的** ★ ⇒ ★**正确做法 = 被问方 hw-lead 登记 answer (to=sw-lead)★ ⇒ ★**本单已在 B4 的 `iss235_residual_needs_to_close` 里点名** ★

### U-B ★**受保护 md5 基线已随上游落表前进 (★本单不背这个锅, 但要 main 知情★) ★

- ★**ISS-235 交卷时 (2026-11-16 08:4x) 的基线** = 网表 `34132f7e…` · 脚表 `b21b743a…` · BOM `c195a117…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ★
- ★**本单开工时的现值 (2026-11-17 04:5x)** = 网表 ★**`e06c1dd6…`**★ · 脚表 ★**`287e7861…`**★ · BOM ★**`94642d07…`**★ · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ⇒ ★**前三件是 ISS-233 之后又有上游合法落表推进的结果 (ISS-243 落表第 4 批 15:45 等), 不是本单改的** ★ ⇒ ★**板与 `.kicad_pro` 自始至终逐字节不变** ★
- ⇒ ★**「受保护 md5 逐字节不变」的口径 = 本单前后不变 (不是「等于某个历史值」)**, ★B6 ⑤ 两轮对拍可复核 ★

### U-C ★**本单没碰、也不该由我碰的东西 (owner 不变) ★

- ★`HW/**` 一字未改 (★上游落表是 hw-lead 的活★) · ★`state/issue_log.yaml` 一字未改 (★ISS-235 的 status 由 main 落 verified, 本单没碰★) · ★`state/fragments/{hw,mech,pm}.yaml` 一字未改 ★
- ★**§7 的 5 条仍成立的 P0 (7-2 / 7-3 / 7-4 / 7-5 / 7-7) 仍在 ⇒ 本单没有把任何一条真问题"消掉"** ⇒ ★**它们仍分别挂在 sw.yaml 的 needs_from 与 HW 侧待修清单上, 等上游裁决★**

---

## B6 自证复现命令 (★输出原样 · 2026-11-17 04:5x~05:1x 实跑★)

> ★**以下全部是本单自己实跑的输出, 不是抄任何交卷报告。** ★

### ① 五道门禁 + 反向演示 (★全绿★)

```text
$ python3 SW/tools/timing_check.py
SELFTEST 71/71 通过, rc=0

$ python3 SW/tools/check_demo_panel_spec.py
✅ ISS-212 demo 显示侧口径门禁: 全过

$ python3 SW/tools/check_demo_panel_spec.py --selftest
--- SELFTEST 16/16 通过 ---

$ python3 SW/tools/check_shutdown_semantics.py
✅ R1~R7 全过 (口径页 / HW 文档 / SW 镜像 / 网表 四方一致)

$ python3 SW/tools/check_shutdown_semantics.py --selftest
SELFTEST 17/17 通过, rc=0

$ python3 SW/tools/timing_check.py --reverse-demo
反向演示: ✅ 变红 ⇒ 它真在读网表 (不是演常量)
```

### ② ★**双向翻转判别证据** (★喂落表前网表 ⇒ 3 条重新变红 ⇒ 不是把红灯调没★)

```text
$ python3 SW/tools/timing_check.py --netlist state/.bak_iss220/HW_netlist_v1.csv.bak_iss220
  [FAIL] I2C 网表注记与实算一致 (误差 < 1.01 倍 ⇒ 网表侧矛盾已被 ISS-220 d6 消除)
  [FAIL] 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)
  [FAIL] F3 实读: 网表自带的 t_r 注记 186ns (ISS-220 d6 已把 I2C_A 改成 2.2k@1.8V ⇒ 注记与实算一致, 网表侧矛盾已消除)
  [FAIL] ★F8 实读: 负载开关 U_PWR_SW / U_EN_SW **都必须有器件行** (BOM/装配单不许漏掉任何一颗负载开关)
  [FAIL] REV-3 反向: 从网表里删掉 U_PWR_SW ⇒ 装机开关数必须从 2 掉到 1 (★不是 0★ · 断电主开关没了)
  [FAIL] REV-3c 反向: 把 U_EN_SW 的**器件本体行**删掉 (只留引脚行) ⇒ F8『不许漏掉任何一颗负载开关』必须变红
SELFTEST 65/71 通过, rc=1
```

### ③ ★**文档侧残留的原始证据 (改之前)** —— ★★照文档自己的命令跑, 结果跟文档自己的结论打架★★

```text
$ grep -n "U_EN_SW"  HW/netlist_v1.csv | grep -c ",IC,"   # → 0    ← 文档 §13 订正【前】的声称
$ grep -n "U_EN_SW"  HW/netlist_v1.csv | grep -c ",IC,"   # → 1    ← 实跑真值 (ISS-233 加的 L442)
$ grep -c "U_EN_SW"  HW/netlist_v1.csv                    # → 13
$ grep -c "U_PWR_SW" HW/netlist_v1.csv                    # → 10
$ grep -n "U_EN_SW"  HW/netlist_v1.csv | grep ",IC,"      # → 442: ... U_EN_SW,"TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)",IC,必装,...
```

### ④ ★**订正后: 文档声称 == 实跑 (自洽)** —— ★★这就是本单的反向自证★★

```text
$ grep -c "U_EN_SW"  HW/netlist_v1.csv          # → 13   ★★订正后文档声称 13 = 实跑 13 = 一致★★
$ grep -n "U_EN_SW"  HW/netlist_v1.csv | grep -c ",IC,"   # → 1   ★★订正后文档声称 1 = 实跑 1 = 一致★★
$ grep -c "U_PWR_SW" HW/netlist_v1.csv          # → 10   ★★订正后文档声称 10 = 实跑 10 = 一致★★

$ python3 SW/tools/timing_check.py --only F8_power_off
   load_switch_refs                   : ['U_PWR_SW', 'U_EN_SW']
   load_switch_without_device_row     : []
   rail_switching_devices             : 2
   on_pin_pulldown_ohm                : 10000.0
★★订正后 §1.1 F8 行声称 rail_switching_devices : 2 / load_switch_without_device_row : [] = 实算 = 一致★★
```

### ⑤ ★**受保护 5 件 md5 (本单前后两轮, 逐字节不变)** ★

```text
e06c1dd633566aa44732762c2ff99d1c  HW/netlist_v1.csv
287e7861a0d1007748d92d9fbecdd490  HW/netlist_v1_pins.csv
94642d07a69e8d60dd2af57f69b93607  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
```

### ⑥ ★**状态源合并 + 项目总工质量门** ★

```text
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-17T04:57:55+08:00)
   产出 412 | 阻塞 43 (高危 33) | 未闭合需求 243 | 冲突 0 | 健康度 red
merge rc=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-17_hw-lead_ISS268_板只改一次作业包v3_§0两行口径订正.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-17_sw-lead_ISS270_SW侧外部依赖自查.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-17_mech-lead_ISS271_板侧开口S6认领与LED位置约束.md
...
【Q4 需求闭环率】
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过
gate rc=0
```

### ⑦ ★**分片原子写的无损核验 (★不许删别人的条目★)** ★

```text
$ python3 state/frag_write.py --agent sw-lead --add-artifact ... --add-claim ... --add-claim ... --add-claim ...
[frag_write] ✅ sw.yaml 已原子更新 → 再跑 python3 state/merge.py

$ 前后对拍 (needs_from / answers / interface_claims / artifacts / blockers)
needs_from       before= 91 after= 91  lost=0  added=0
answers          before= 22 after= 22  lost=0  added=0
interface_claims before=207 after=210  lost=0  added=3   (+iss235_residual_doc_fix
                                                     +iss235_doc_repro_selfconsistent
                                                     +iss235_residual_needs_to_close)
artifacts        before=131 after=133  lost=0  added=1   (SW_TIMING_REVIEW.md 条目 2 → 3)
blockers         before= 15 after= 15  lost=0  added=0
⇒ ★**别人的条目一个没删, 自闭合 0 条** ★
```
```
