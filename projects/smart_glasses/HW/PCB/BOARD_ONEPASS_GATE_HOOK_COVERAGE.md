# BOARD_ONEPASS_GATE_HOOK_COVERAGE · 「板那一趟」板侧闸【挂链覆盖率】清账 (ISS-404)

> **单号** ISS-404 · **派活** 项目总工 (main / moli) · **执笔** 硬件总工 (hw-lead) · **日期** 2026-11-25
> **性质** 纯查证 + 纯分析 + 新建真相页 + 新建机器闸 ⇒ **零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`**
> **主线关系** 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属 **「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板)**

---

## §0 · 一句话题面与一句话结论

> ### ★★题面★★
> 「板那一趟」的**预检清单 / 作业包 / 提交顺序页**里点名的闸, 有 **13 道不在门禁链 `state/gate_check.py` 上** —— 其中就有投板前最命门的两道 `state/check_pcb_nets.py` (C1 缺失/多余焊盘) 与 `state/check_pcb_drc.py` (DRC + C6 生产文件齐)
> ⇒ 全仓唯一的 fail-closed 自动链【**不跑它们**】⇒ 它们只活在人工清单里 ⇒ **漏跑 = 没有任何机器会响** ⇒ 板投出去才发现 ⇒ 板改第二次

> ### ★★结论 (★本机实读 + 本机实算·不抄任何 agent 报告★)★★
> 1. 链上 **19 个挂载槽位 / 18 个唯一脚本**; 仓内闸 **105 → 107 道** (★本单新增本闸 1 道·另 +1 道是 mech-lead 的 ISS-405 并发交卷件·★); **零挂链 87 → 89 道**
> 2. 三份作业面文件合计点名 **19 道闸**, 其中 **6 道在链上 / 13 道不在链上** ⇒ **覆盖率 31.6%**
> 3. ★**13 道里今天就有 3 道是红的** (`check_pcb_nets.py` rc=1 · `check_netlist_contradiction_r3.py` rc=1 · `check_pcb_drc.py --strict` rc=1)★
> 4. ★**人工签核台账不存在** ⇒ G1 的「人工签核」那一路为空 ⇒ **「板那一趟」当天, 这 13 道闸漏跑 = 没有任何机器会响**★
> 5. 本单新建 **真相页 + 机器台账 + 机器闸**; 新闸裸跑 **rc=1** (★红的是现状, 不是闸故障★)、`--selftest` **rc=0 / 末行 ALL TESTS PASS / 1 正向 + 13 反向全抓到**

---

## §1 · 本机实测数字 (★可复现★)

| # | 事实 | 实测读数 | 出处 (★本机实读/实算★) |
|---|---|---|---|
| 1 | 门禁链规模 | ★**19 个挂载槽位 / 18 个唯一脚本**★ (EXTRA_GATES **8** + PINNED_MD5_GATES **10** + HW_PINOUT_GATE **1** = 19; `SW/tools/check_onepass_sw_sync.py` 被挂了两次 ⇒ 唯一脚本 18) | `state/gate_check.py` AST 实读 (`EXTRA_GATES` / `PINNED_MD5_GATES` / `HW_PINOUT_GATE`) |
| 2 | 仓内闸脚本总数 | ★**107 道** (HW 46 / MECH 30 / SW 31)★ ⇒ **零挂链 87 道** ⇒ ★**交卷时 107 道 / 零挂链 89 道**★ | `find HW MECH SW -name 'check_*.py'` (★**递归·含 `MECH/tools/` 与 `SW/tools/`·只扫顶层会漏 14 道**★) |
| 3 | 三页点名覆盖 | 预检清单 **12** 点名 / 作业包 **18** 点名 / 提交顺序页 **3** 点名 ⇒ 并集 **19** 道 ⇒ 在链 **6** / 不在链 **13** | `tmp/iss404/analyze.py` 现场解析 |
| 4 | 门禁链当前读数 | ★**rc=0 · Q1 18/18 · Q7 钉板 md5 闸链 10/10 道绿 · Q6 HW pinout 闸绿**★ | 裸跑 `python3 state/gate_check.py` |
| 5 | 人工签核台账 | ★**不存在** ⇒ G1 的「人工签核」那一路为空 | `ls HW/PCB/` + 全仓 `grep -rl 人工签核 --include='*.md'` (★只命中 2 份派活单本身★) |

### ★1.1 · 与派活单的三处精度修正 (★只改精度·不改结论★)★

| 派活单写的 | 本机实算 | 修正性质 |
|---|---|---|
| 「`EXTRA_GATES` 7 道 + `PINNED_MD5_GATES` 10 道 + HW pinout 闸 1 道 = **18**」 | `EXTRA_GATES` 实为 **8** 条 ⇒ 挂载槽位 **19** ⇒ 唯一脚本 **18** | ★**计数口径**: 18 是【唯一脚本数】, 19 是【挂载槽位数】★ (★`SW/tools/check_onepass_sw_sync.py` 同时在两张表里★) |
| 「仓内闸脚本共 **105** 道 ⇒ 零挂链 **87** 道」 | ★开单时的数对 (105 / 87)★ ⇒ ★**交卷时已是 107 / 89**★ | ★**时间口径**: 105 是【开单时的数】, 107 是【交卷时的数】(★差 2 道 = 本单新闸 1 + mech-lead 并发 ISS-405 闸 1★) |
| 「这两道今天的读数就是红的」 | ★`check_pcb_nets.py` **rc=1** ✓; ★`check_pcb_drc.py` **默认口径 rc=0 (绿)** ⇒ ★**只有 `--strict` 才是 rc=1**★ | ★★**这是本单最重要的一条修正**★ ⇒ 见 §2.3 的「挂链必须带 `--strict`」警告 |

---

## §2 · 表 (a): 三份作业面文件点名的 19 道闸 × 是否挂链 × 挂在哪张表

| # | 闸 (相对路径) | 点名页 | 是否挂链 | 挂在哪张表 | 今天的读数 |
|---|---|---|---|---|---|
| 1 | `HW/check_board_frame_caliber.py` | 预检清单 · 作业包 · 提交顺序页 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 2 | `HW/check_iss354_manufacturability.py` | 作业包 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 3 | `HW/check_iss354_mfg_closure.py` | 预检清单 · 作业包 · 提交顺序页 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 4 | `HW/check_netlist_contradiction_r3.py` | 预检清单 · 作业包 | ★★**未挂链**★★ | ★**无**★ | **rc=1 (红)** ★FINDINGS = 2 (F2 板级封装名空 186 · F3 DNP 零标记 40) |
| 5 | `HW/check_netlist_selfconsistency.py` | 预检清单 · 作业包 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 6 | `HW/check_onepass_commit_order.py` | 作业包 · 提交顺序页 | ★**已挂链**★ | PINNED_MD5_GATES | rc=0 (绿) |
| 7 | `HW/check_onepass_preflight_coverage.py` | 预检清单 · 作业包 · 提交顺序页 | ★**已挂链**★ | PINNED_MD5_GATES | rc=0 (绿) |
| 8 | `HW/check_onepass_s10_manifest.py` | 作业包 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) ★M2 清单 BOARD_MD5 == 盘上板 md5 · M4 FILE_COUNT 74 == 盘面 74 |
| 9 | `HW/check_part_selection_matrix.py` | 预检清单 · 作业包 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 10 | `HW/check_pcb_generator_defaults.py` | 作业包 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 11 | `HW/check_pin_function_labels.py` | 预检清单 · 作业包 | ★**已挂链**★ | PINNED_MD5_GATES | rc=0 (绿) ★挂链带 `--expect-known`★ |
| 12 | `HW/check_preflight_regen_idempotent.py` | 预检清单 · 作业包 | ★**已挂链**★ | PINNED_MD5_GATES | rc=0 (绿) |
| 13 | `HW/check_step1_parts_spec.py` | 预检清单 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 14 | `HW/check_workpack_state_values.py` | 预检清单 · 作业包 | ★**已挂链**★ | PINNED_MD5_GATES | rc=0 (绿) |
| 15 | `MECH/check_mech_verdict_freshness.py` | 作业包 | ★**已挂链**★ | EXTRA_GATES | rc=0 (绿) |
| 16 | `MECH/check_onepass_mech_sync.py` | 作业包 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 17 | `MECH/check_onepass_struct_crosscheck.py` | 作业包 | ★★**未挂链**★★ | ★**无**★ | rc=0 (绿) |
| 18 | `state/check_pcb_drc.py` | 预检清单 · 作业包 · 提交顺序页 | ★★**未挂链**★★ | ★**无**★ | rc=0 (默认口径) · ★`--strict` 下 **rc=1** (C4 unconnected items = 45) |
| 19 | `state/check_pcb_nets.py` | 预检清单 · 作业包 · 提交顺序页 | ★★**未挂链**★★ | ★**无**★ | **rc=1 (红)** ★C1: 缺失 0 · **多余 2** · 同号异网 3 |

★**合计: 点名 19 道 · 已挂链 6 道 · 未挂链 13 道 ⇒ 覆盖率 6/19 = 31.6%**★

### ★2.1 · 未挂链的 13 道 (★逐条·与派活单逐字对上★)★

```
HW/check_board_frame_caliber.py
HW/check_iss354_manufacturability.py
HW/check_iss354_mfg_closure.py
HW/check_netlist_contradiction_r3.py
HW/check_netlist_selfconsistency.py
HW/check_onepass_s10_manifest.py
HW/check_part_selection_matrix.py
HW/check_pcb_generator_defaults.py
HW/check_step1_parts_spec.py
MECH/check_onepass_mech_sync.py
MECH/check_onepass_struct_crosscheck.py
state/check_pcb_drc.py
state/check_pcb_nets.py
```

★**与派活单 §1.2 的 13 条名单逐字一致** (★顺序不同·成员相同★) ⇒ ★**派活单的这张名单本机可复现**★

### ★2.2 · 已挂链的 6 道 (★都挂在 `PINNED_MD5_GATES` / `EXTRA_GATES`★)★

- `HW/check_onepass_commit_order.py` ⇒ **PINNED_MD5_GATES** · 钉板闸③ 改板提交顺序闸
- `HW/check_onepass_preflight_coverage.py` ⇒ **PINNED_MD5_GATES** · 钉板闸④ 作业包覆盖度闸
- `HW/check_pin_function_labels.py` ⇒ **PINNED_MD5_GATES** · 钉板闸⑤ 脚表功能标签闸
- `HW/check_preflight_regen_idempotent.py` ⇒ **PINNED_MD5_GATES** · 钉板闸⑩ 板侧项全集重跑幂等闸
- `HW/check_workpack_state_values.py` ⇒ **PINNED_MD5_GATES** · 钉板闸⑥ 作业包现状值闸
- `MECH/check_mech_verdict_freshness.py` ⇒ **EXTRA_GATES** · MECH 结构结论防漂闸 (ISS-295)

### ★2.3 · ★★命门两道闸的本机实测读数 (★与派活单的差别在这一节★★)★★

**① `state/check_pcb_nets.py` ⇒ rc=1 (红)** ★[实测]★

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
     缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 · 非法 NC 0
     ★多: C_VBUS_GND pad1 = GND
     ★多: C_VBUS_GND pad2 = VBUS_5V_CHG
     ★错: Q_PG pad1 应为 PWR_GOOD, 实际 PWR_ON
     ★错: Q_PG pad3 应为 PWR_ON, 实际 PWR_GOOD
     ★错: D_ESD_USB_D pad1 应为 NET_USB_D_P_TYPEC, 实际 USB_D_P_SRC
❌ 不通过 —— 板子与网表**不等价** ⇒ 板子不能下单
```

★**这就是 ISS-402 §3 那条掉板机理的同一件事** (C_VBUS_GND 焊盘级多余 2) ⇒ **今天就是红的, 且不在链上**★

**② `state/check_pcb_drc.py` ⇒ 默认口径 rc=0 (绿) / `--strict` rc=1 (红)** ★[实测]★

```
★ 默认口径 (裸跑):
  ✅ C3 DRC violations = 0 (要求 0)
  ✅ C4 unconnected items = 45  ← 骨架阶段允许未布线 (布线完成后用 --strict 归零)
  ✅ C6 生产文件齐 — Gerber 32 个
  ✅ 全过 —— 图纸可下单          ⇒ rc=0

★ --strict 口径:
  ❌ C4 unconnected items = 45 (--strict: 布线完成后必须为 0)
  ❌ 不通过 1 项: C4 45 项未连接   ⇒ rc=1
```

★★**这条是本单最重要的发现之一**★★: 
★**`check_pcb_drc.py` 裸跑是绿的** ⇒ ★**如果原样挂进链, 它会【永远绿】= 一道【假绿闸】= 比不挂更坏**★ ⇒ ★**挂它必须带 `--strict` 参数**★ (★`state/gate_check.py` 的 `run_external_gate` 已支持 per-gate 参数 `args`·★`HW/check_pin_function_labels.py` 就是同款先例★)

---

## §3 · 表 (b): 仓内 107 道闸的分类台账

★**分类优先级 (★不许换★)**: `A_已挂链` > `B_必挂但漏挂` > `C_一次性沙盒件` > `D_selftest辅助件` > `E_域内常驻闸`★

| 分类 | 含义 | 条数 |
|---|---|---|
| `A_已挂链` | 在 `state/gate_check.py` 的挂链表上 (★fail-closed 语义·跑不起来即闸红★) | **18** |
| `B_必挂但漏挂` | ★**被三份作业面文件点名、但既不在挂链表、也不在人工签核台账**★ | **11** |
| `C_一次性沙盒件` | 文件名以 `_sbx` 结尾 (★一次性沙盒对比件·不常驻★) | **1** |
| `D_selftest辅助件` | 文件名含 `selftest` (★闸的反向用例辅助件·不是闸本体★) | **2** |
| `E_域内常驻闸` | 其余域内常驻闸 (★未被三页点名·属于各自域的专项判据★) | **74** |
| `本闸自身` | ★**ISS-404 本闸自己** (★零挂链·待 main 挂链·防自指漏洞★) | **1** |
| | **合计** | **107** |

★**★台账的成员集合必须是【活的快照】★**: 仓内闸数不是常数 —— ★**交卷期间别的代理会同时加闸**★ (★本单实测: mech-lead 的 `MECH/check_mech_gate_hook_coverage.py` 在 2026-11-25 01:39 落盘 ⇒ 仓内闸 105 → 107★) ⇒ ★**新闸的 G3 会因「台账成员集合 ≠ 仓内实扫集合」判红并逐条点名** ⇒ ★**这是设计内的 fail-closed (台账必须跟着仓走)·不是闸故障**★ ⇒ ★**刷新命令**: `python3 tmp/iss404/gen_ledger.py` → `gen_truth_page.py` → `gen_handoff.py`★

★**对派活单「四分类」口径的一处必要偏离 (★不放松·只补齐★)**★: 派活单给的四类 (`已挂链` / `必挂但漏挂` / `一次性沙盒件` / `selftest 辅助件`) **覆盖不了 107 道闸的全集** —— 本机实算有 **74 道**既不在链上、也不被三页点名、文件名既不是 `_sbx` 也不是 `selftest` ⇒ ★**若硬塞进四类, 就是把 74 道闸谎报成某一类**★ ⇒ ★**故增第 5 类 `E_域内常驻闸`**★ (★**G3 的「有且只有一个归属」仍然成立·且是可验证的穷尽划分**★)

★**B 类只有 11 道而不是 13 道的原因**: 真漏挂 13 道里, `state/check_pcb_nets.py` 与 `state/check_pcb_drc.py` 住在 `state/` 目录 ⇒ **不在 `HW/` `MECH/` `SW/` 这 107 道的扫描面内** ⇒ ★**它们在「真漏挂名单」里, 但不在「仓内 107 道」的分类台账里**★

<details><summary><b>★全量清单 (★107 道逐条★)★</b></summary>

**A_已挂链 (18)**

- `HW/check_bq25896_pinout.py` — HW_PINOUT_GATE
- `HW/check_fsin_rootcause.py` — PINNED_MD5_GATES
- `HW/check_g1a7_selection_landed.py` — PINNED_MD5_GATES
- `HW/check_onepass_commit_order.py` — PINNED_MD5_GATES
- `HW/check_onepass_preflight_coverage.py` — PINNED_MD5_GATES
- `HW/check_pin_function_labels.py` — PINNED_MD5_GATES
- `HW/check_preflight_regen_idempotent.py` — PINNED_MD5_GATES
- `HW/check_workpack_state_values.py` — PINNED_MD5_GATES
- `MECH/check_board_frame_coords.py` — PINNED_MD5_GATES
- `MECH/check_demo_struct_truth.py` — PINNED_MD5_GATES
- `MECH/check_mech_verdict_freshness.py` — EXTRA_GATES
- `MECH/tools/check_mech_ref_reachability.py` — EXTRA_GATES
- `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` — EXTRA_GATES
- `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` — EXTRA_GATES
- `SW/tools/check_demo_panel_spec_r6_selftest.py` — EXTRA_GATES
- `SW/tools/check_landing_trace_obligation.py` — EXTRA_GATES
- `SW/tools/check_onepass_sw_sync.py` — EXTRA_GATES / PINNED_MD5_GATES
- `SW/tools/check_sw_ref_reachability.py` — EXTRA_GATES

**B_必挂但漏挂 (11)**

- `HW/check_board_frame_caliber.py`
- `HW/check_iss354_manufacturability.py`
- `HW/check_iss354_mfg_closure.py`
- `HW/check_netlist_contradiction_r3.py`
- `HW/check_netlist_selfconsistency.py`
- `HW/check_onepass_s10_manifest.py`
- `HW/check_part_selection_matrix.py`
- `HW/check_pcb_generator_defaults.py`
- `HW/check_step1_parts_spec.py`
- `MECH/check_onepass_mech_sync.py`
- `MECH/check_onepass_struct_crosscheck.py`

**C_一次性沙盒件 (1)**

- `HW/check_fts_land_drill_same_batch_sbx.py`

**D_selftest辅助件 (2)**

- `MECH/check_board_frame_freeze_gate_selftest.py`
- `SW/tools/check_sw_ref_reachability_v2_selftest.py`

**本闸自身 (1)**

- `HW/check_onepass_gate_hook_coverage.py`

**E_域内常驻闸 (74)**

```
HW/check_board_comparable_gate.py                           HW/check_board_netlist_divergence_gate.py                   HW/check_charge_current_live_value.py
HW/check_chg_spec7_vs_netlist.py                            HW/check_debug_uart_seat_alignment.py                       HW/check_debug_uart_seat_truth.py
HW/check_fp_libid_truth.py                                  HW/check_fp_truth_baseline.py                               HW/check_fp_truth_coverage_gap.py
HW/check_fp_truth_land_swap.py                              HW/check_fts_land_drill_same_batch.py                       HW/check_fts_single_row_land_truth.py
HW/check_gate10_concurrency_safety.py                       HW/check_generator_value_drift_closed.py                    HW/check_hw_external_dep_closed.py
HW/check_iss243_cregn.py                                    HW/check_iss247_f1_landed.py                                HW/check_jdebug_land_fit.py
HW/check_juart_land_fit.py                                  HW/check_land_row_anchors.py                                HW/check_netlist_gnd_rows.py
HW/check_onepass_s10_swap_set_truth.py                      HW/check_part_selection_gaps.py                             HW/check_part_selection_landed_crosscheck.py
HW/check_s8_target_list.py                                  HW/check_seat_part_verdict_propagation.py                   HW/check_tp_int_gap.py
MECH/check_board_frame_candidate_compat_gate.py             MECH/check_board_frame_freeze_gate.py                       MECH/check_board_geom_caliber_drift.py
MECH/check_budget_caliber.py                                MECH/check_connector_clearance_caliber.py                   MECH/check_debug_seat_3d_fit.py
MECH/check_debug_seat_rework_spec.py                        MECH/check_fts_seat_body_geometry.py                        MECH/check_fts_seat_sample_plan.py
MECH/check_fts_vs_generic_courtyard_delta.py                MECH/check_hinge_fpc_truth.py                               MECH/check_jdebug_1p27_clearance.py
MECH/check_jdebug_arrangement_truth.py                      MECH/check_juart_1p27_clearance.py                          MECH/check_machine_block_pointer_resolvable.py
MECH/check_mech_dual_caliber_gate.py                        MECH/check_mech_gate_hook_coverage.py                       MECH/check_mech_signed_append_ledger.py
MECH/check_onepass_mech_release.py                          MECH/check_onepass_s10_fp_swap_impact.py                    MECH/check_onepass_s10_led_spec_sync.py
MECH/check_pad_size_coupling_closed.py                      MECH/check_zoujuan_marker_consistency.py                    SW/check_evt_charge_current_criterion.py
SW/tools/check_brightness_biosafety.py                      SW/tools/check_debug_header_fw_impact.py                    SW/tools/check_debug_pin_order_contract.py
SW/tools/check_demo_panel_spec.py                           SW/tools/check_fp_truth_read.py                             SW/tools/check_iss250_rknn_target_gate.py
SW/tools/check_iss355_convert_route.py                      SW/tools/check_load_switch_selection.py                     SW/tools/check_onepass_legb_sw_impact.py
SW/tools/check_onepass_sw_release.py                        SW/tools/check_rk3572_target_caliber.py                     SW/tools/check_rk3572_vccio_domain.py
SW/tools/check_rknn_target_compat.py                        SW/tools/check_shutdown_semantics.py                        SW/tools/check_sw09_patch_dryrun.py
SW/tools/check_sw_board_md5_rebase_readiness.py             SW/tools/check_sw_false_connectivity_gate.py                SW/tools/check_sw_fp_truth_impact.py
SW/tools/check_sw_gate_chain_coverage.py                    SW/tools/check_sw_gate_health.py                            SW/tools/check_sw_ref_reachability_v2.py
SW/tools/check_sw_zero_copper_grade_consistency.py          SW/tools/check_timing_review_adc_sync.py
```

</details>

---

## §4 · 表 (c): 13 道真漏挂的逐条后果 (★拦什么 / 拦不住会怎样★)

| # | 闸 | 拦什么 (判据) | 拦不住会怎样 (坏结局) | 今天的读数 | 证据 |
|---|---|---|---|---|---|
| 1 | `state/check_pcb_nets.py` | C1 焊盘级等价 (ref,焊盘号)→网络 | 板面多一个焊盘 / 脚位对调 ⇒ 网表与板不等价 ⇒ 投出去的板是错的 (要么板改第二次 2-4 周 + 一批板的钱, 要么流到用户手里) | **rc=1 (红)** ★C1: 缺失 0 · **多余 2** · 同号异网 3 | `[实测]` |
| | | | ★ISS-402 §3 掉板机理的同一件事 (C_VBUS_GND 多余 2) ⇒ 今天就红, 且不在链上★ | | |
| 2 | `state/check_pcb_drc.py` | C3 DRC violations = 0 + C4 unconnected = 0 (--strict) + C6 生产文件齐 (Gerber 32 个) | DRC 不干净 / 未布线 45 项 / 生产文件不齐 ⇒ 投板 = 板改第二次或废板 | rc=0 (默认口径) · ★`--strict` 下 **rc=1** (C4 unconnected items = 45) | `[实测]` |
| | | | ★★它是预检清单 B25 (unconnected 45→0) 与 B28 (留证链/盖章/发布闸) 的判据命令★ | | |
| 3 | `HW/check_netlist_selfconsistency.py` | 网表自身一致性 4 处 + 7 组缺陷的「现状守卫」 | 网表内部自相矛盾复发 ⇒ 板面照抄 ⇒ 板改第二次 | rc=0 (绿) | `[实测]` |
| | | | ★★它是【现状守卫】不是【找错】⇒ 落表改动若不更新规格 ⇒ 守卫变红 ⇒ 挂上去才有意义★★ | | |
| 4 | `HW/check_part_selection_matrix.py` | BOM 待选型件 OPN 选型证据矩阵 | 带着没有证据的 OPN 投板 ⇒ 买回来的料不是图纸上那颗 ⇒ 板是废的 (不是改板, 是退料) | rc=0 (绿) | `[实测]` |
| | | | ★★它判的是【买回来的对不对】, 与 DRC/网表是正交的一条防线★ | | |
| 5 | `HW/check_netlist_contradiction_r3.py` | 网表 / 板 第 3 轮自相矛盾机器门禁 (F2 / F3) | DNP 位号在板文件里零标记 ⇒ 贴片坐标把它当必装 ⇒ 白贴 40 颗料 ⇒ 成本 + 工艺缺陷 | **rc=1 (红)** ★FINDINGS = 2 (F2 板级封装名空 186 · F3 DNP 零标记 40) | `[实测]` |
| | | | ★★它今天就是红的 ⇒ 挂链时机要考虑 (与 C1 修复同批?)★★ | | |
| 6 | `HW/check_board_frame_caliber.py` | 板框 / 坐标系口径机器闸 (C1~C6) | 三套基线搅乱 ⇒ 落位撞 SoM 座 / 重复计算坐标 ⇒ 板改第二次 | rc=0 (绿) | `[实测]` |
| | | | ★★三页都点它 ⇒ 它是覆盖面最广的一道漏挂闸★★ | | |
| 7 | `HW/check_onepass_s10_manifest.py` | S10 投产包 md5 清单 (MANIFEST.md5) | 投产包不是这一版板出的 (旧包/混包) ⇒ 投出去的板与图面不一致 ⇒ 板改第二次 | rc=0 (绿) ★M2 清单 BOARD_MD5 == 盘上板 md5 · M4 FILE_COUNT 74 == 盘面 74 | `[实测]` |
| | | | ★★chain_gate.py (S11) 判不了这一条 (它只判 mtime 新旧) ⇒ 本闸不可替代★★ | | |
| 8 | `MECH/check_onepass_mech_sync.py` | M1 帧标签 · M2 两条开口各自不压 SoM 座 · M3 座体高度参数式自洽 · M4 判据命令真存在 | 检修口/调试口被当成一个开口 ⇒ 照抄合并的错值 ⇒ 板改第二次 (★ISS-267/271 的病根★) | rc=0 (绿) | `[实测]` |
| | | | ★★它是 ISS-267/271 病根的直接闸 ⇒ 漏挂 = 病根复发窗口一直开着★★ | | |
| 9 | `MECH/check_onepass_struct_crosscheck.py` | N2/N3/N4 (S6 的 20 个目标落位 × MECH 保留区) · N5 (座体类器件三方对照) · 贴角 keep-out 口径 | hw-lead 的闸不查结构保留区 + MECH 的闸不碰 S6 目标落位 ⇒ 两边各自绿 ⇒ 合起来撞 ⇒ S6 一跑就撞 ⇒ 板 md5 变第二次 | rc=0 (绿) | `[实测]` |
| | | | ★★它是唯一补【两边各自绿、合起来撞】这段缝的闸★★ | | |
| 10 | `HW/check_pcb_generator_defaults.py` | 板生成器默认值闸 (层数默认 8 = 盘上铜层数 等三条) | 生成器默认值漂了 ⇒ 重跑生成器 ⇒ 板 md5 变第二次 | rc=0 (绿) | `[实测]` |
| | | | ★★它守的是【生成器】不是【板】★★ | | |
| 11 | `HW/check_step1_parts_spec.py` | ISS-237 「P2 屏口径收死」⇒ display 座口径单一事实源 | 照旧文档画板 ⇒ 投板前返工 (★闸注释里自报的代价: 2-4 周 + ¥4-8K/批★) | rc=0 (绿) | `[实测]` |
| | | | ★★它判的是「照哪份文档画」★★ | | |
| 12 | `HW/check_iss354_mfg_closure.py` | ISS-354 可制造性收口只读判定 (C1~C4) | 收口没落到文档 ⇒ 那一趟照着没有的清单开工 ⇒ 漏项 ⇒ 板改第二次 | rc=0 (绿) | `[实测]` |
| 13 | `HW/check_iss354_manufacturability.py` | ISS-354 5 件在盘 (A-1 5 个 ref 改项清单 · A-2 4 类不自洽 · A-3 SoM pin1 排向降级方案) | 交卷件被误删 / 改坏 ⇒ 那一趟的输入没了 ⇒ 停工或照猜的画 | rc=0 (绿) | `[实测]` |

### ★4.1 · 为什么这 13 道值得为它建一台机器闸★

- **「板只改一次」= 板 md5 全生命周期只许变 1 次** ⇒ ★**投板前的每一道检查, 都是「板改第二次」的最后一道闸**★
- 坏结局二选一: ① **人工漏跑** ⇒ 网表/板面不一致 (C1 多余焊盘) 或 DRC 不干净 ⇒ 投出去的板是错的 ⇒ ★**要么板改第二次 (2-4 周 + 一批板的钱), 要么流到用户手里**★ ② ★**闸红了没人知道** ⇒ 与 ISS-388 的诊断一模一样 (★「闸自己坏了」这件事本身零检测手段★)
- ★**既有覆盖度闸盯不到这一格**: `HW/check_onepass_preflight_coverage.py` (★已挂在钉板闸④★) 的 P3 查的是「**脚本在不在盘上**」, ★**不是「它在不在 fail-closed 链上」**★ ⇒ ★**本缺口至今零机器闸覆盖**★
- ★**反向也成立**: 挂链表里引用的脚本若哪天被删/改名, 链上那一条会直接变成「脚本跑不起来 ⇒ 算闸红」⇒ ★**fail-closed 语义本身是成立的**★ ⇒ ★**所以本单要盯的正好是【反向】: 清单点名的闸【不在链上】这件事, 全仓没有任何一道闸会红**★

---

## §5 · 新闸 `HW/check_onepass_gate_hook_coverage.py` (G1~G7)

| 判据 | 要求 | 实现要点 |
|---|---|---|
| **G1 清单↔挂链 双向闭环** | 页面点名的每一道闸, 必须在【挂链表】或【人工签核台账】里二者其一; 两者皆无 ⇒ 判红 | ★**fail-closed**: 闸脚本缺失 / 语法跑不起来 / 页面点名了找不到的脚本 ⇒ 一律算红 |
| **G2 挂链表引用的脚本真实存在** | 挂链表每一条的脚本必须在本机存在 ⇒ 不存在即红 (防幽灵闸) | ★用 **AST** 读 `state/gate_check.py` (★不执行·不 import·不因 main 改链而过期★) |
| **G3 分类台账自洽** | 每道闸在台账里有且只有一个归属; **本闸自己也要登记** | ★台账成员集合必须与仓内实扫**逐字相等**; ★声明「已挂链」但链上没有 ⇒ 幽灵闸红★ |
| **G4 板三证不动** | 板 / 网表 / 脚表 / BOM md5 与基线逐字相同 | ★板 = 写死基线 `611b869e…`; ★网表/脚表/BOM = 走「**落表台账为准**」(★ISS-283 的口径·不写死数字★) |
| **G5 零挂链 + 零外发自证** | 本闸名在 `state/gate_check.py` 里的行数须与台账登记的挂链状态一致; `state/outbox/` 未动 | ★**挂链状态可翻转** ⇒ 见 §5.1 的自指悖论机制★ |
| **G6 证据分级** | 每条结论标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 写清「拦什么/拦不住会怎样」 | ★台账里 14 条结论逐条校验★ |
| **G7 零写板自证** | 板 md5 / mtime / size 三项与基线逐字相同 | ★台账 `board_baseline` 三项快照★ |

★**跑法**: 裸跑 **rc=1** (★红的是现状 = 13 道闸没挂链, 不是闸故障★) · `--selftest` **rc=0** · ★末行逐字 `ALL TESTS PASS`★ · ★**1 条正向 + 13 条反向全抓到**★

### ★5.1 · ★★自指悖论 (★本闸不自拍·交 main 拍★)★★

> G1 要求「页面点名的闸都要在链上或台账里」—— 而 **本闸自己也不在链上** ⇒ 逻辑上它也该被登记进台账, 而登记它的动作在 main 地界 (挂链) ⇒ ★**本闸的台账里「本闸自身」这一行写成 `待 main 挂链`**, 并把这条悖论作为问句交 main, **不许自己拍板**★

★**本闸给出的机制 (★不是拍板·是把悖论变成一个可执行的开关★)**: ★

| 台账 `self.hook_status` | 本闸 G5 的期望 | main 要做的动作 |
|---|---|---|
| `待 main 挂链` (★当前值★) | `grep` 本闸名 ⇒ **必须 0 行** | 什么都不做 (★现状即绿★) |
| `已挂链` | `grep` 本闸名 ⇒ **必须 ≥1 行** | ★① 把台账这一行改成 `已挂链` ② 把本闸加进 `state/gate_check.py` 的任一张挂链表★ |

★⇒ ★**main 挂本闸时, 闸脚本一个字节都不用改**★ —— 只要翻台账里那一个字段, G5 就自动从「期望 0 行」翻成「期望 ≥1 行」★
★⇒ ★**同时, 台账里漏掉这一步 ⇒ G5 会红并点名**「台账登记「待 main 挂链」但 `gate_check.py` 里已有 N 行提到本闸」⇒ ★**没有静默漂移**★

### ★5.2 · 挂链的「两处写」代价 (★实测·必须让 main 知道★)★

★**main 挂上任何一道闸之后, 除了改 `state/gate_check.py`, 还要同步改台账的 `must_hook_missing` 名单 (删掉那一条)**★ ⇒ 否则 G3 会红并点名 「台账有 · 盘面派生无 (已挂链或已不被页面点名·请同步台账)」★

★**为什么这样设计**: 若让台账静默漂移, 台账就永远过期 ⇒ 「台账自洽」四个字就是空话 ⇒ ★**宁可让 main 多写一行 JSON, 也不要一个永远过期的台账**★

★**分类本身是【规则派生】的** (A>B>C>D>E) ⇒ ★**main 挂链不会让 `classification` 过期**★ ⇒ ★**只有 `must_hook_missing` 这一份【名单】需要同步**★ ⇒ ★**挂链的增量成本 = 1 行 JSON**★

---

## §6 · 坏结局与代价 (★为什么这件事值钱★)

| 坏结局 | 机理 | 代价 |
|---|---|---|
| **① 板改第二次** | 13 道闸漏跑 ⇒ 投出去的板是错的 ⇒ 返工重投 | ★2-4 周 + 一批板的钱 (★`HW/check_step1_parts_spec.py` 的闸注释里自报: 2-4 周 + ¥4-8K/批★) |
| **② 流到用户手里** | 同上, 但没人返工 | ★**不可逆**★ |
| **③ 闸红了没人知道** | 与 ISS-388 的诊断一模一样: 「闸自己坏了」这件事本身零检测手段 | ★**同一种病复发**★ ⇒ ★**这正是本单要建的闸要盯的那一格**★ |
| **④ 挂链时机踩坑** | ★`check_pcb_nets.py` 今天 C1 红 ⇒ 挂上去门禁链当场红 ⇒ 红了被当噪音 ⇒ **比不挂更坏**★ | ★**挂链必须与「板那一趟」的 C1 修复同批**★ |
| **⑤ 假绿** | ★`check_pcb_drc.py` 裸跑 rc=0 ⇒ 挂上去永远绿 ⇒ **一道假绿闸比不挂更坏**★ | ★**必须带 `--strict`**★ |

---

## §7 · 证据分级 + 机器块

| 结论 | 等级 | 依据 |
|---|---|---|
| 链上 19 槽位 / 18 唯一脚本 | `[实测]` | AST 实读 `state/gate_check.py` |
| 仓内 105→107 道闸 | `[实测]` | `find` 实扫 (递归) |
| 三页点名 19 道 / 未挂 13 道 | `[实测]` | 现场解析三页 + AST 实读链 |
| 13 道闸今天的读数 | `[实测]` | 本机实跑 (留证 `logs/iss404/unhooked_gates_readings.txt`) |
| `check_pcb_drc.py` 默认绿 / `--strict` 红 | `[实测]` | 本机实跑两种口径 |
| 人工签核台账不存在 | `[实测]` | 全仓实扫 |
| 板 md5 `611b869e13518c3c023fb178f91a0075` | `[实测]` | `md5sum` |
| 网表/脚表/BOM 基线 | `[实测]` | ★落表台账 §16.2 (ISS-302 链) 实查★ |
| 「板改第二次 = 2-4 周 + 一批板的钱」 | `[推算]` | ★闸注释自报的代价·非本单实测★ |
| 各闸「拦什么」的语义描述 | `[推算]` | ★读各闸 docstring 自述·非逐条重跑取证★ |
| 本闸 14 条反向用例全抓到 | `[实测]` | `--selftest` 本机实跑 |

★**零数据声明**: ★**本单没有任何一条结论来自外部网站 / 媒体 / 供应商资料**★ ⇒ ★**全部证据等级为 `[实测]` 或 `[推算]`; `[官网]` `[媒体]` `[0数据]` 三档本单为 0 条**★ (★符合老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信·全靠自己查资料」★)

### ★7.1 · 机器块 (★可复现★)★

```json
{
 "issue": "ISS-404",
 "owner": "hw-lead",
 "date": "2026-11-25",
 "chain": {
  "slots": 19,
  "unique_scripts": 18,
  "tables": {
   "EXTRA_GATES": 8,
   "PINNED_MD5_GATES": 10,
   "HW_PINOUT_GATE": 1
  }
 },
 "repo_gates": {
  "at_issue_open": 105,
  "after_iss404": 107,
  "per_domain": {
   "HW": 46,
   "MECH": 30,
   "SW": 31
  },
  "unhooked_at_issue_open": 87,
  "unhooked_after_iss404": 89,
  "hw": 46,
  "mech": 30,
  "sw": 31
 },
 "pages_named": {
  "total": 19,
  "hooked": 6,
  "not_hooked": 13,
  "coverage_pct": 31.6
 },
 "not_hooked": [
  "HW/check_board_frame_caliber.py",
  "HW/check_iss354_manufacturability.py",
  "HW/check_iss354_mfg_closure.py",
  "HW/check_netlist_contradiction_r3.py",
  "HW/check_netlist_selfconsistency.py",
  "HW/check_onepass_s10_manifest.py",
  "HW/check_part_selection_matrix.py",
  "HW/check_pcb_generator_defaults.py",
  "HW/check_step1_parts_spec.py",
  "MECH/check_onepass_mech_sync.py",
  "MECH/check_onepass_struct_crosscheck.py",
  "state/check_pcb_drc.py",
  "state/check_pcb_nets.py"
 ],
 "readings_today": {
  "HW/check_board_frame_caliber.py": "rc=0 (绿)",
  "HW/check_iss354_manufacturability.py": "rc=0 (绿)",
  "HW/check_iss354_mfg_closure.py": "rc=0 (绿)",
  "HW/check_netlist_contradiction_r3.py": "**rc=1 (红)** ★FINDINGS = 2 (F2 板级封装名空 186 · F3 DNP 零标记 40)",
  "HW/check_netlist_selfconsistency.py": "rc=0 (绿)",
  "HW/check_onepass_s10_manifest.py": "rc=0 (绿) ★M2 清单 BOARD_MD5 == 盘上板 md5 · M4 FILE_COUNT 74 == 盘面 74",
  "HW/check_part_selection_matrix.py": "rc=0 (绿)",
  "HW/check_pcb_generator_defaults.py": "rc=0 (绿)",
  "HW/check_step1_parts_spec.py": "rc=0 (绿)",
  "MECH/check_onepass_mech_sync.py": "rc=0 (绿)",
  "MECH/check_onepass_struct_crosscheck.py": "rc=0 (绿)",
  "state/check_pcb_drc.py": "rc=0 (默认口径) · ★`--strict` 下 **rc=1** (C4 unconnected items = 45)",
  "state/check_pcb_nets.py": "**rc=1 (红)** ★C1: 缺失 0 · **多余 2** · 同号异网 3"
 },
 "manual_signoff_ledger": "★不存在★",
 "new_gate": "HW/check_onepass_gate_hook_coverage.py",
 "new_gate_bare_rc": 1,
 "new_gate_selftest_rc": 0,
 "new_gate_selftest_last_line": "ALL TESTS PASS",
 "new_gate_hooked": "★零挂链·待 main 挂链·自指悖论交 main 拍★",
 "ledger": "HW/PCB/BOARD_ONEPASS_GATE_HOOK_LEDGER.json",
 "board_md5": "611b869e13518c3c023fb178f91a0075"
}
```

### ★7.2 · 复现命令 (★全部本机实跑·rc 如实★)★

```bash
# 台账重生成 (★一次性·真件只写台账一个★)
python3 tmp/iss404/gen_ledger.py

# 新闸裸跑 (★rc=1 · 红的是现状★)
python3 HW/check_onepass_gate_hook_coverage.py

# 新闸反向用例 (★rc=0 · 末行 ALL TESTS PASS★)
python3 HW/check_onepass_gate_hook_coverage.py --selftest

# 既有闸不许被本单弄红
python3 HW/check_onepass_preflight_coverage.py

# 门禁链不许被本单弄红 (★rc=0 · Q1 18/18 · Q7 10/10★)
python3 state/merge.py && python3 state/gate_check.py

# 零挂链自证 (★必须 0★)
grep -c check_onepass_gate_hook_coverage state/gate_check.py

# 板三证自证
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

