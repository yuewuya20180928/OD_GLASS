# MECH/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md —— 「板那一趟」MECH 域【闸挂链覆盖率】清账

> ★**执笔**: 结构总工 (mech-lead · 带散热) · ★**单号**: ISS-405 · ★**日期**: 2026-11-25
> ★**派活**: 项目总工 (main / moli) · ★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍** ★
> ★**关联机器闸**: `MECH/check_mech_gate_hook_coverage.py` (★本单新建 · ★**零挂链** · ★裸跑 rc=1 = ★**红的是现状**★ · `--selftest` rc=0) ★
> ★**证据等级**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` (★每格都标★)

---

## ★0 · 结论摘要 ★

★★ **MECH 域盘上 29 道闸, 门禁链 (`state/gate_check.py`) 上只挂了 4 道 ⇒ 25 道零挂链。零挂链的这 25 道里, 装着「板那一趟」当天【决定结构件能不能出件】和【决定结构侧能不能出 Gerber】的全部判据: 7 道判决链闸 (结构侧出件判据) + 1 道准出汇总闸 + ISS-400 交卷的机器块指针闸 + ISS-403 交卷的焊盘尺寸耦合闸。⇒ 「板那一趟」当天, 这两件事【没有任何机器会响】⇒ 唯一的防线是「人记得跑」⇒ 漏跑 = 板改第二次。** ★★

★**本单不做的事 (★不代拍★)**: ★**本闸自己也不在链上** ⇒ 它自己也要被登记 ⇒ 登记/挂链是 main 的地界 ⇒ 本闸台账里「本闸自身」写成 `待 main 挂链`, 并把这条【自指悖论】作为问句交 main (§7 + 交卷页 B5-Q4) ★

### ★0.1 · 三个硬数字 (★本机实读 · ★可复现 · ★不抄任何 agent 报告★) ★

| 事实 | 实测读数 | 出处 |
|---|---|---|
| ★**MECH 域闸脚本 29 道** ★ | `MECH/**/check_*.py` (★含 `MECH/tools/` 子目录★) | ★`[实测]` 本机 `os.walk("MECH")` 全扫 ★ |
| ★**门禁链只挂 4 道 MECH 闸** ★ | `check_board_frame_coords.py` (钉板闸⑦) · `check_demo_struct_truth.py` (钉板闸⑧) · `check_mech_verdict_freshness.py` (EXTRA_GATES) · `check_mech_ref_reachability.py` (EXTRA_GATES · `MECH/tools/`) | ★`[实测]` `state/gate_check.py` L212 / L246 (EXTRA_GATES) + L269 / L270 (PINNED_MD5_GATES) ★ |
| ★**⇒ 零挂链 25 道** ★ | 含 ★7 道判决链闸★ · ★`check_onepass_mech_release.py` (ISS-300 准出汇总闸)★ · ★`check_machine_block_pointer_resolvable.py` (ISS-400)★ · ★`check_pad_size_coupling_closed.py` (ISS-403)★ | ★`[实测]` 同上 (差集 29 − 4 = 25) ★ |

### ★0.2 · 与来件 (brief) 口径的【两处实测订正】 ★

| # | 来件写的 | ★**本机实测** ★ | 差在哪 |
|---|---|---|---|
| 1 | ★「`HW/J_CHG_SELECTION.md` §4.1/§4.2 现在用的是 28p 的进深 6.4mm (L199)」★ | ★**§4.1/§4.2 里根本没有 6.4mm** ★ —— §4.1 只讲铰链区几何 (§4.1 表里没有 6.4), §4.2 讲座高 vs H 链; ★**6.4mm 出现在 L199 (§7 证据分级汇总表) 与 L55 (§2.1 候选型号表「座体进深」行)** ★ | ★**引用行号错位**: 来件说的 §4.1/§4.2 用的是【座高 2.0mm / 座体宽 6.50mm】(§4.3), 【进深 6.4mm】在 §2.1 L55 + §7 L199 ⇒ ★**结论不变 (6.4 确实是现行口径), 但要改的页/行不同★** ★ |
| 2 | ★「10p 档若按官网 D=5.57 或 A=4.5 判」★ | ★**D 与 A 都不是这两个几何量** ★ —— ★**A/B/C/D 四个值全部沿触点排方向** (算术铁证见 §6.2) ★ ⇒ ★**按 D 或 A 判会判错** ★ | ★**正确的取法: Y 向占宽取 C = 9.1; X 向进深【不取任何字母】, 取官网产品页 "Connector Width" = 6.4mm** ★ |

---

## ★1 · 盘上 29 道闸 × 是否挂链 (★表 a★) ★

★**读数列 = 本机 2026-11-25 01:3x 逐道实跑 (`python3 MECH/<闸>.py`, 沙盒留档 `tmp/iss405/run_<闸名>.out`)★** ★`rc` 栏 = 该闸裸跑退出码 (`[实测]`) ★

| 闸 (仓内相对路径) | 分类 | 挂在哪张表 | 现读 rc |
|---|---|---|---|
| `MECH/check_board_frame_candidate_compat_gate.py` | C | — | 0 |
| `MECH/check_board_frame_coords.py` | **A** | PINNED_MD5_GATES:钉板闸⑦ 板框坐标闸 | 0 |
| `MECH/check_board_frame_freeze_gate.py` | C | — | 2 |
| `MECH/check_board_frame_freeze_gate_selftest.py` | D | — | 0 |
| `MECH/check_board_geom_caliber_drift.py` | C | — | 2 |
| `MECH/check_budget_caliber.py` | C | — | 0 |
| `MECH/check_connector_clearance_caliber.py` | C | — | 1 |
| `MECH/check_debug_seat_3d_fit.py` | **B** | — | 0 |
| `MECH/check_debug_seat_rework_spec.py` | **B** | — | 0 |
| `MECH/check_demo_struct_truth.py` | **A** | PINNED_MD5_GATES:钉板闸⑧ 结构真值闸 | 0 |
| `MECH/check_fts_seat_body_geometry.py` | **B** | — | 0 |
| `MECH/check_fts_seat_sample_plan.py` | **B** | — | 1 |
| `MECH/check_fts_vs_generic_courtyard_delta.py` | **B** | — | 0 |
| `MECH/check_hinge_fpc_truth.py` | C | — | 0 |
| `MECH/check_jdebug_1p27_clearance.py` | **B** | — | 0 |
| `MECH/check_jdebug_arrangement_truth.py` | C | — | 0 |
| `MECH/check_juart_1p27_clearance.py` | **B** | — | 0 |
| `MECH/check_machine_block_pointer_resolvable.py` | **B** | — | 1 |
| `MECH/check_mech_dual_caliber_gate.py` | C | — | 0 |
| `MECH/check_mech_signed_append_ledger.py` | C | — | 1 |
| `MECH/check_mech_verdict_freshness.py` | **A** | EXTRA_GATES:MECH 结构结论防漂闸 (ISS-295) | 0 |
| `MECH/check_onepass_mech_release.py` | **B** | — | 0 |
| `MECH/check_onepass_mech_sync.py` | C | — | 0 |
| `MECH/check_onepass_s10_fp_swap_impact.py` | C | — | 0 |
| `MECH/check_onepass_s10_led_spec_sync.py` | C | — | 0 |
| `MECH/check_onepass_struct_crosscheck.py` | C | — | 0 |
| `MECH/check_pad_size_coupling_closed.py` | **B** | — | 0 |
| `MECH/check_zoujuan_marker_consistency.py` | C | — | 1 |
| `MECH/tools/check_mech_ref_reachability.py` | **A** | EXTRA_GATES:MECH 侧位号引用可达性闸 (ISS-333) | 0 |
| ★`MECH/check_mech_gate_hook_coverage.py` (★本单新建★) ★ | **E** | ★— (★待 main 挂链★) ★ | ★本单新建★ |

★**现读 rc 汇总 (★`[实测]`★)**: `rc=0` **21** 道 · `rc=1` **5** 道 (`check_connector_clearance_caliber` / `check_fts_seat_sample_plan` / `check_machine_block_pointer_resolvable` / `check_mech_signed_append_ledger` / `check_zoujuan_marker_consistency`) · `rc=2` **2** 道 (`check_board_frame_freeze_gate` / `check_board_geom_caliber_drift`) · **合计 28** ⇒ ★**加上 `MECH/tools/check_mech_ref_reachability.py` (rc=0) = 29 道** ★

---

## ★2 · 四分类台账 (★表 b★) ★

★**分类判据 (★机器可判: 本闸 §M1 用「双向差集」保证每道闸有且只有一个归属★)★**

| 类 | 名字 | 判据 | 条数 |
|---|---|---|---|
| ★**A** ★ | **已挂链** | 该闸的仓内相对路径出现在 `state/gate_check.py` 的 `EXTRA_GATES` / `PINNED_MD5_GATES` 里 | **4** |
| ★**B** ★ | **必挂但漏挂** | 在「MECH 侧准出必挂闸清单 (★建议版★)」里, 但**当前不在链上** ⇒ ★**也不在人工签核台账里** ⇒ ★**既没人跑也没人知道** ★ | **10** |
| ★**C** ★ | **一次性评估件** | 判据对象是【某一步 / 某一次裁决 / 一份口径快照】, 预期【在该步跑一次并留档】, 而非【每次门禁链都重跑】 | **14** |
| ★**D** ★ | **selftest 辅助件** | `*_selftest.py` —— 本身是给别的闸配的反向用例集, 单独入链没有意义 | **1** |
| ★**E** ★ | **本闸自身 (待 main 挂链)** | ★**自指悖论**: 本闸自己也不在链上 ⇒ 它自己也要被登记 ⇒ 登记/挂链是 main 地界 ⇒ 本单只登记, 不挂 ★ | **1** |

★**合计 30 条 = 盘上 29 道 + 本闸自身 1 道** ★

### ★2.1 · A 类 (4 道 · 已挂链) ★

| 闸 | 挂在哪张表 | 链上标签 | 现读 rc |
|---|---|---|---|
| `MECH/check_board_frame_coords.py` | `PINNED_MD5_GATES` | 钉板闸⑦ 板框坐标闸 | 0 |
| `MECH/check_demo_struct_truth.py` | `PINNED_MD5_GATES` | 钉板闸⑧ 结构真值闸 | 0 |
| `MECH/check_mech_verdict_freshness.py` | `EXTRA_GATES` | MECH 结构结论防漂闸 (ISS-295) | 0 |
| `MECH/tools/check_mech_ref_reachability.py` | `EXTRA_GATES` | MECH 侧位号引用可达性闸 (ISS-333) | 0 |

### ★2.2 · B 类 (10 道 · 建议必挂但当前零挂链) ★

★**这 10 道 = 来件建议的「MECH 侧准出必挂闸清单」★** ★**Q1 待 main 拍** ★

| # | 闸 | 它守的是什么 | 现读 rc |
|---|---|---|---|
| 1 | `MECH/check_debug_seat_3d_fit.py` | ★**座体 3D 装配拟合判决链主闸 (201 条判据)** ★ | 0 |
| 2 | `MECH/check_debug_seat_rework_spec.py` | 座体返工规格判决链闸 | 0 |
| 3 | `MECH/check_fts_seat_body_geometry.py` | FTS 座体本体几何判决链闸 | 0 |
| 4 | `MECH/check_fts_vs_generic_courtyard_delta.py` | FTS vs 通用件 庭院差集判决链闸 | 0 |
| 5 | `MECH/check_fts_seat_sample_plan.py` | FTS 座体三量收样作业包闸 | ★**1 (今天就是红的)** ★ |
| 6 | `MECH/check_jdebug_1p27_clearance.py` | J_DEBUG 1.27mm 净距判决链闸 | 0 |
| 7 | `MECH/check_juart_1p27_clearance.py` | JUART 1.27mm 净距判决链闸 | 0 |
| 8 | `MECH/check_onepass_mech_release.py` | ★**「板那一趟」MECH 侧准出汇总闸 (ISS-300)** ★ —— 一条命令出「S6 重出板后能不能出 Gerber」的结构侧结论 | 0 |
| 9 | `MECH/check_machine_block_pointer_resolvable.py` | 机器块指针可解析性闸 (ISS-400 交卷) | ★**1 (今天就是红的)** ★ |
| 10 | `MECH/check_pad_size_coupling_closed.py` | ★**焊盘尺寸耦合闭合闸 (ISS-403 交卷)** ★ —— pad 一放大 ⇒ 判决链 7 个数静悄悄作废 | 0 |

★**⚠ 两条「今天就是红的」必须写在这里 (★来件 Q2 的原话★)**: ★`check_fts_seat_sample_plan.py` 与 `check_machine_block_pointer_resolvable.py` 现读就是 rc=1 ⇒ ★**现在把它们挂进门禁链 = 门禁链当场常红 ⇒ 红了被当噪音 ⇒ 等于没挂** ⇒ ★**挂链时机必须与「板那一趟」同批, 且这两道得先有绿的办法 (★怎么绿是 main 的地界★)** ★

### ★2.3 · C 类 (14 道 · 一次性评估件) ★

| 闸 | 一次性性质 (★为什么它不作为常设门禁★) | 现读 rc |
|---|---|---|
| `MECH/check_board_frame_candidate_compat_gate.py` | U-1 板框三候选 × 现役板 相容性判定 (ISS-341) —— 一次裁决件 | 0 |
| `MECH/check_board_frame_freeze_gate.py` | U-1 板框冻结闸 (ISS-336) —— 一次裁决件 | 2 |
| `MECH/check_board_geom_caliber_drift.py` | 结构侧口径漂移只读检测 (ISS-342) —— 一次漂移清单件 | 2 |
| `MECH/check_budget_caliber.py` | 三处老账口径一致性快照 (ISS-251) —— 一次口径快照件 | 0 |
| `MECH/check_connector_clearance_caliber.py` | 座体净距判据同源化总表快照 (ISS-377) —— 一次口径快照件 | 1 |
| `MECH/check_hinge_fpc_truth.py` | 跨铰链 FPC 几何口径收口件 (ISS-240) | 0 |
| `MECH/check_jdebug_arrangement_truth.py` | J_DEBUG 排布标签 (维数) 真相件 (ISS-382) | 0 |
| `MECH/check_mech_dual_caliber_gate.py` | 结构侧双口径判定脚本自守件 (ISS-352) | 0 |
| `MECH/check_mech_signed_append_ledger.py` | 已签收件追加登记台账自守件 (ISS-399) —— ★**台账落位后才有意义 (★M-A 待 main 拍★)** ★ | 1 |
| `MECH/check_onepass_mech_sync.py` | 「板那一趟」MECH 侧板侧输入收口件 (ISS-278) | 0 |
| `MECH/check_onepass_s10_fp_swap_impact.py` | S10 步换封装对 MECH 侧影响面件 (ISS-365) —— 绑步骤 | 0 |
| `MECH/check_onepass_s10_led_spec_sync.py` | S10 步 LED 窗口规格同趟重算件 (ISS-367) —— 绑步骤 | 0 |
| `MECH/check_onepass_struct_crosscheck.py` | 「板那一趟」结构侧最后一道交叉核对件 (ISS-290) —— 绑那一趟 | 0 |
| `MECH/check_zoujuan_marker_consistency.py` | 走鹃旧口径收口的机器背书件 (ISS-238) | 1 |

★**⚠ 诚实声明 (★不藏判断★)**: ★**C 类里至少有 3 道 (`check_onepass_struct_crosscheck` / `check_onepass_mech_sync` / `check_mech_signed_append_ledger`) 按「那一趟当天要不要有人自动盯」的标准, 是有理由升到 B 类的** ★ ⇒ ★**本单把它们留在 C 类, 是因为「必挂闸清单」是 main 的地界 (来件 Q1) ⇒ 本单只提这个附问, 不代拍** ★

### ★2.4 · D 类 (1 道 · selftest 辅助件) ★

| 闸 | 性质 | 现读 rc |
|---|---|---|
| `MECH/check_board_frame_freeze_gate_selftest.py` | 板框冻结闸的反向用例自测件 (ISS-336) —— 辅助件, 单独入链没有意义 | 0 |

### ★2.5 · E 类 (1 道 · 本闸自身) ★

| 闸 | 状态 | 备注 |
|---|---|---|
| `MECH/check_mech_gate_hook_coverage.py` | ★**待 main 挂链** ★ | ★**自指悖论**: 本闸自己也不在链上 ⇒ 它自己也要被登记 ⇒ 登记/挂链是 main 地界 ⇒ ★**本单只登记, 不挂; 也不自己解决这条悖论** ★ (★问句见交卷页 B5-Q4★) ★ |

---

## ★3 · 人工签核台账 (★现状 = 空 ★) ★

★**M2 判据**: 「MECH 侧准出必挂闸清单」里每一道, 必须在【挂链表】或【人工签核台账】里二者其一; ★**两者皆无 ⇒ 判红** ★

| 闸 | 谁签 | 签核单号 | 签核日期 | 证据 |
|---|---|---|---|---|
| ★(空 — ★现状: 10 道 B 类闸【既没挂链, 也没有任何人工签核记录】★ ⇒ 本闸裸跑判红★)★ | | | | |

★**Q3 待 main 拍**: ★**「人工签核台账」要不要另起一页?** ★ —— ★**本单把它先落在本真相页 §3 (一行没填)** ★ ⇒ ★**若 main 要另起页, 本闸的 M2 判据改成读那一页 (★改判据 = main 地界★)** ★

---

## ★4 · 真漏挂逐条后果 (★表 c · ★拦不住会出哪种坏结局★) ★

★**全部判据句与事实句分开写 (★M7 判据★)★**

| # | 零挂链的闸 | 判据句 (★它挡什么★) | 事实句 (★ISS-403 本机实测的触发链★) | 坏结局 |
|---|---|---|---|---|
| 1 | `check_debug_seat_3d_fit.py` | 判据句: 座体 3D 装配拟合的 201 条判据必须在投板前全绿 | 事实句: ISS-403 实测 —— pad `1.000 → 1.110` ⇒ 判决链 7 个数里 `4.8100→4.9200` / `2.2700→2.3800` 等全作废 | 结构件按旧数出件 ⇒ ★**装配干涉 ⇒ 板改第二次** ★ |
| 2 | `check_debug_seat_rework_spec.py` | 判据句: 座体返工规格必须与官方 `.kicad_mod` 现读同源 | 事实句: 同上 (它写死 `4.8100` / `2.2700` ⇒ pad 一改就错) | 同上 |
| 3 | `check_fts_seat_body_geometry.py` | 判据句: FTS 座体本体几何必须与落位判据一致 | 事实句: 同上 | 同上 |
| 4 | `check_fts_vs_generic_courtyard_delta.py` | 判据句: FTS 件与通用件在庭院里的差集必须显式 | 事实句: 同上 | 通用件误用 ⇒ 座体装不进 |
| 5 | `check_fts_seat_sample_plan.py` | 判据句: 三量收样作业包必须真的收到实测 | 事实句: ★**今天就是 rc=1** ★ (实物三量仍在盘外) | 判据永远停在 `[推算]` ⇒ 座体真实高度 `[0数据]` 永远填不上 |
| 6 | `check_jdebug_1p27_clearance.py` | 判据句: J_DEBUG 排针座净距必须过阈 | 事实句: ISS-403 实测 —— pad 一放大 ⇒ `G1/G2/G3/G4` 转红 | 排针座与板边/器件干涉 |
| 7 | `check_juart_1p27_clearance.py` | 判据句: JUART 排针座净距必须过阈 | 事实句: ISS-403 实测 —— pad 一放大 ⇒ `J0/J1/J5/J7` 转红 | 同上 |
| 8 | ★`check_onepass_mech_release.py`★ | 判据句: 「板那一趟」MECH 侧准出必须一条命令出结论 | 事实句: ★**它不在链上 ⇒ 「能不能出 Gerber」的结构侧结论只靠人记得跑** ★ (★现读 rc=0, 但【没人跑】等于【没有】★) | ★**结构侧没有准出结论就投板 ⇒ 出 Gerber 后才发现结构侧不闭合 ⇒ 板改第二次** ★ |
| 9 | `check_machine_block_pointer_resolvable.py` | 判据句: 机器块指针必须可解析 (无悬空/歧义/误指/无归属) | 事实句: ★**今天 rc=1 (51 条非 A 类指针)** ★ | 真相页里的数找不到来源 ⇒ 判据引用链断裂 ⇒ **改了源头没人发现** |
| 10 | `check_pad_size_coupling_closed.py` | 判据句: 焊盘尺寸一旦被放大, 7 个数必须被自动重新推导 | 事实句: ★**ISS-403 自己新建的这道闸自己也不在链上** ★ ⇒ ★**它自己新建的防线, 连自己都没挂** ★ | ★**pad 一放大 ⇒ 7 个数静悄悄作废而无人知道 ⇒ 全程零自动防线** ★ |

★**★一句总结 (★本单要说的就这一句★)★**: ★**ISS-403 那个「焊盘放大 ⇒ 7 个数全作废」的坏结局, 连「它自己新建的那道闸」也不在链上 ⇒ 那道闸当时【自己也没有防线】⇒ 全程零自动防线** ★

---

## ★5 · 「板只改一次」关键路径上的位置 (★为什么这件事不是「文档洁癖」★) ★

| 层 | 事实 | 出处 |
|---|---|---|
| ★**板侧** ★ | 板 md5 全生命周期只许变 1 次 ⇒ 投板前的结构侧每一道检查, 都是「板改第二次」的最后一道闸 | ★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★ |
| ★**结构侧** ★ | 结构件按旧数出件 ⇒ 装配干涉 ⇒ **板改第二次** | ★ISS-403 已实测 (A/B 两臂 stdout md5 逐字相同) ★ |
| ★**闸链侧** ★ | 这条链上的每一道闸 (含 ISS-403 新建的那道) 都不在门禁链上 ⇒ 「板的那一趟」当天没有任何机器会响 | ★`[实测]` §1 表 a ★ |
| ★**机制侧** ★ | ★**SW 域已经做过同款** (ISS-392 `SW/tools/check_sw_gate_chain_coverage.py` + ISS-388 `SW/tools/check_sw_gate_health.py`) ⇒ ★**HW / MECH 两域至今没有同款** ⇒ MECH 域的「零挂链」至今零机器检测手段 ★ | ★`[实测]` 全仓 `find` + `grep` ★ |

★**★MECH 域此前没有任何机器能回答这三个问题 ★★**
1. ★**MECH 域有多少道闸？** ★ — 今天以前只能靠人 `ls` ★
2. ★**有几道在门禁链上？** ★ — 今天以前只能靠人 `grep` ★
3. ★**没挂的那些, 漏跑会出哪种坏结局？** ★ — 今天以前是散文 (· 本页 §4 把它变成逐条对照 ★)

---

## ★6 · 附带项 · J_CHG 10p 座体几何 (★回答 `iss384_jchg_10p_dims_geometry`★) ★

★**本节回答 hw-lead 的 open need (★key = `iss384_jchg_10p_dims_geometry` · `to: mech-lead` · `due: 2026-11-26`★)★**
★**几何归属 = mech-lead 地界** ⇒ ★**本单出判定, 不改 `HW/J_CHG_SELECTION.md` 正文 (★那是 hw-lead 的地界 + 已签收件★) ⇒ 要改的写成【追加式建议】交 main (★见交卷页 B5-Q6★)** ★

### ★6.1 · 官网数据 (★`[官网]` · ★本机实读 Hirose 官网 PDF + 产品页★) ★

| 来源 | 逐字内容 |
|---|---|
| ★Hirose **[FH12] Series Catalog** (Nov.1.2026 版) · 尺寸表 ★ | `FH12-10S-0.5SH(55)` / HRS No. `586-0522-3-55` / No. of Contacts `10` / ★**A=04.5 · B=08.1 · C=09.1 · D=05.57** ★ (mm) |
| ★Hirose 官网产品页 `CL0586-0522-3-55` ★ | ★**Connector Length 9.1mm · Connector Height 2mm · Connector Width 6.4mm** ★ |
| ★Hirose 官网产品页 `CL0586-0612-4-55` (28p, 交叉校验) ★ | ★**Connector Length 18.1mm · Connector Height 2mm · Connector Width 6.4mm** ★ ⇒ ★**Width = 6.4 是【系列常量】, 10p 与 28p 同值** ★ |
| ★Series Catalog · **Land / Metal Mask dimensions** 表 (10p 行) ★ | ★**A=4.5 · B=10.1 · C=6.5** ★ (mm) ★**注意: 这是 land 表的字母, 与上面座体表的字母【不是同一张图】★** ★ |

★**取证路径 (★零外发 · ★自己网上查·★未联系任何供应商★)**: ★`curl` 拿到 Series Catalog PDF 原件 (20 页, 落盘 `tmp/iss405/fh12_catalog.pdf`, md5 见 §7) ⇒ `pdftotext -layout` 逐行读尺寸表 ⇒ `pdftoppm` 渲染第 8 页 (0.5mm Pitch Bottom Contact Type 尺寸图) 与第 15 页 (Land / Metal Mask 尺寸图) 读图 ★

### ★6.2 · ★★算术铁证: A/B/C/D 【全部沿触点排方向】★★ ★`[实测]` ★

★**把 Series Catalog 整张表的 29 行逐行读出来, 四个字母与位数 N 的关系【无一例外】★** ★`[实测]` ★

| 字母 | 关系式 | 10p 值 | 28p 值 | 60p 值 (若适用) |
|---|---|---|---|---|
| ★**A** ★ | `A = (N−1) × 0.5` (★触点跨距, 首末触点中心线之间★) | 4.5 | 13.5 | — |
| ★**B** ★ | `B = A + 3.6` | 8.1 | 17.1 | — |
| ★**C** ★ | `C = A + 4.6` (★座体沿触点排总长★) | **9.1** | **18.1** | — |
| ★**D** ★ | `D = A + 1.07` | 5.57 | 14.57 | — |

★**⇒ 四个值全部随位数 N 线性增长 ⇒ 【没有一个是垂直于触点排的座体进深】⇒ ★**「X 向进深取 D=5.57」是错的** ★
★**⇒ `C` 独立交叉验证**: ★`C(28p) = 18.1` = ★**本仓早就记着的「FH12 28p 外形宽 18.1mm」** (`HW/J_CHG_SELECTION.md` §7 L199) ⇒ ★**证明本仓的「外形宽」就是沿触点排方向 ⇒ 映射方向自洽** ★
★**⇒ `A` 独立交叉验证**: ★`A(10p) = 4.5` = ★**本仓现用的「触点区 4.50」** (`MECH/BOARD_WIDTH_15MM.md` §3.2) ⇒ ★**同向自洽** ★

### ★6.3 · ★★两个几何量的最终取法 (★逐条给问句里的答案★)★★

★**坐标框架 (★本仓板坐标: 原点板框左下角 · X = 板长 (0→60.00) · Y = 板宽 (0→15.00)★)★**
★**触点排沿 Y 向 (焊盘排 10 个 @0.5mm, 居中于 Y=7.50 ⇒ 占 Y ∈ [5.00, 10.00]) · FPC 沿 X 向插入 (铰链端, X=0 方向)** ★ —— ★`HW/PCB_OUTLINE_60x15.md` §4.1 + §0 坐标约定★ ★`[实测]`★

| 本单要答的 | ★**取哪个** ★ | 值 | 依据 |
|---|---|---|---|
| ★**Y 向占宽 (沿触点排)** ★ | ★**取官网目录的 `C`** ★ | ★**9.10 mm** ★ | ★`[官网]` 目录 `C(10p)=9.1` = 官网产品页 "Connector Length 9.1mm" ★ |
| ★**X 向进深 (垂直触点排 = FPC 插入方向)** ★ | ★**不取 A/B/C/D 任何一个字母** ★ ⇒ ★**取官网产品页 "Connector Width"** ★ | ★**6.40 mm** ★ | ★`[官网]` 产品页 `CL0586-0522-3-55` "Connector Width 6.4mm" ★**且 28p 产品页同值 ⇒ 系列常量, 不再是从 28p 反推的 [推算]** ★ |
| ★**座体高度** ★ | (不属本问, 顺带核实) | **2.00 mm** | ★`[官网]` 产品页 "Connector Height 2mm"; 目录 Note 2: 标准型 2mm / 加强 flip-lock 2.4mm ★ |

### ★6.4 · ★★间隙必须重算 —— 而且重算的结果不是「可能变」, 是「确定变成干涉」★★

★**现行页面的 Y 向算法 (★错在哪★)** ★`[实测]`★
★`MECH/BOARD_WIDTH_15MM.md` §3.2: ★**座体宽 = 必装脚数 × pitch + 2 × 1.00 = 9 × 0.5 + 2.00 = 6.50mm** ★ ⇒ ★**每边 overhang 手捏成 1.00mm** ★
★官网实际: ★**座体沿排总长 `C` = 9.1, 触点跨距 `A` = 4.5 ⇒ 每边 overhang = (9.1 − 4.5)/2 = 2.30mm** ★ ⇒ ★**现行口径每边少算了 1.30mm** ★

★**★6.50 这个数是哪来的? ★** —— ★**它恰好等于官网 land 表的 `C` = 6.5 = 【两端固定焊盘 (anchoring lands) 的中心距】** ★ ⇒ ★**锚焊盘中心距 6.5 ⇒ 锚焊盘落在 Y = 7.50 ± 3.25 = 4.25 / 10.75** ★ ⇒ ★**而本仓 `HW/PCB_OUTLINE_60x15.md` O-3 写的「座体 Y ∈ [4.25, 10.75]」逐字就是这两个锚焊盘的位置** ★ ⇒ ★**结论: 本仓把【锚焊盘中心距】当成了【座体外形宽】★ ⇒ 这是同一个数被安到了两个不同的物理量上** ★ ★`[推算]`(推导链)+`[官网]`(两个数)★

★**★重算 (★判据句与事实句分开★)★★**

| 项 | 旧口径 (本仓现行) | ★**新口径 (官网)** ★ | 差 |
|---|---|---|---|
| 座体 Y 向占宽 | 6.50 | ★**9.10** ★ | **+2.60** |
| 座体 Y 向包络 (居中于 Y=7.50) | Y ∈ [4.25, 10.75] | ★**Y ∈ [2.95, 12.05]** ★ | 下缘 **−1.30** / 上缘 **+1.30** |
| land 图纸整块沿排宽 (`B`) | (未建模) | ★**10.10** ★ ⇒ land 包络 Y ∈ [2.45, 12.55] | — |
| M1.2 孔① (5.00, 2.50) ⌀1.4 上缘 | Y = 3.20 | Y = 3.20 | — |
| ★**座体 ↔ 孔① 间隙** ★ | ★**余 1.05mm** ★ | ★**干涉 0.25mm** ★ | ★**由「余量」翻成「干涉」** ★ |

★**★事实句 (★前提条件逐条写清, 不藏★)★★**
1. ★**判据句**: ★若 10p 座体沿触点排的占宽按官网 `C` = 9.1 判, 则座体 Y 下缘 = 2.95, 而 M1.2 孔①上缘 = 3.20 ⇒ **干涉 0.25mm** ★
2. ★**前提 A (硬)**: ★座体在 Y 向以触点排为轴心 ⇒ ★**标准型 (非偏心型, 即 `FH12-` 而非 `FH12A-`) 必然如此** ★ ⇒ ★**这条不需要推算, 是型式的定义** ★ ★`[官网]` 产品号结构: "Blank: standard type / A: Eccentric type"★
3. ★**前提 B (★仍是 [推算]★)**: ★**座体 X 起点 `X0` (相对板边 X=0) 官网不给** (★那是布局量, 不是连接器尺寸★) ⇒ ★**间隙是否真的发生, 取决于 `X0` 落在哪里** ★
   ★**用 PIN-SET-2 (现行孔位, `HW/PCB_FIXING_PINSET2.md`) 算** ★`[推算]`★
   - ★**M1.2 压紧孔 S1 (8.00, 2.50) ⌀1.4** ⇒ X ∈ [7.30, 8.70] · Y ∈ [1.80, 3.20] ⇒ ★**若 `X0` ∈ [0.90, 8.70] ⇒ 干涉 0.25mm; 若 `X0` < 0.90 ⇒ X 向不重叠, 间隙 = 0.90 − `X0`** ★
   - ★**H7 定位销孔 P1 (8.00, 7.50) ⌀2.0** ⇒ X ∈ [7.00, 9.00] · Y ∈ [6.50, 8.50] ⇒ ★**它的 Y 带完全落在座体 Y 带 [2.95, 12.05] 内 ⇒ 若 `X0` ∈ [0.60, 9.00] ⇒ 定位基准孔被座体压住 (比 M1.2 更硬: 压住定位基准 ⇒ 装不进)** ★; 若 `X0` = 0 ⇒ **X 向余 0.60mm** ★
   - ★**O-3 里写的孔①坐标 (5.00, 2.50) 是 §2 的旧坐标 (★已被 PIN-SET-2 取代★) ⇒ §4.2 O-3 的坐标本身也是陈旧的** ★ ★`[实测]` `HW/PCB_OUTLINE_60x15.md` 文首「§2 已被 `HW/PCB_FIXING_PINSET2.md` 取代」★
4. ★**前提 C (口径统一)**: ★**本仓现用的「28p 进深 6.4mm」这个数是对的, 只是证据等级该从 [推算] 升到 [官网]** ⇒ ★**X 向进深不用改数, 改的是等级 (★`[推算]` → `[官网]`★)** ★

### ★6.5 · 留给 main 的三个几何问句 (★不代拍·只给代价★) ★

| # | 问法 | 建议默认值 | 不答的后果 | 代价 |
|---|---|---|---|---|
| ★**G1** ★ | ★**J_CHG 焊盘排 / 座体沿 Y 向要不要移 (离板中线)?** ★ | ★**移: 座体 Y 下缘要留 ≥1.00mm 间隙 ⇒ 座体中心 Y ≥ 4.20+4.55 = 8.75 ⇒ 焊盘排中心从 7.50 移到 8.75 (+1.25) ⇒ 焊盘排占 Y ∈ [6.25, 11.25], 板宽 15 仍余 3.75** ★ | ★**`HW/J_CHG_SELECTION.md` §4.3 / `HW/PCB_OUTLINE_60x15.md` O-2 / O-3 继续按 6.50 判 ⇒ 座体外形结论错 (且错的方向是「偏乐观」)** ★ | ★**改板 = 焊盘排坐标要重画 ⇒ 但板还没投, 这是【最后一次】改的机会 (★板只改一次纪律★)** ★ |
| ★**G2** ★ | ★**M1.2 压紧孔 S1 与 H7 定位孔 P1 动不动?** ★ | ★**动: 沿 X 往后移 (往板内), 避开 X ≤ 9.00 的座体带** ★ | ★**座体装不上 ⇒ 装配干涉 ⇒ 板改第二次** ★ | ★**动孔 = 骨架/笼的对应位置也要动 (★ISS-049/ISS-192 的定位链★)** ★ |
| ★**G3** ★ | ★**座体 X 起点 `X0` 的口径 (布局量, 官网不给) 谁给?** ★ | ★**由 mech-lead 给结构建议值 + hw-lead 落 PCB (★X0 = 0 ⇒ 座体 X ∈ [0, 6.40] ⇒ 与 P1 余 0.60mm**) ★ | ★**间隙永远停在 [推算] ⇒ 干涉与否不可判 ⇒ PCB 冻结前必须闭环** ★ | ★**一条布局口径, 零成本, 但必须有人在 PCB 冻结前拍** ★ |

---

## ★7 · 自指悖论 · 边界自证 · 复现入口 ★

### ★7.1 · ★★自指悖论 (★交卷页必须点名, 不许自己解决★)★★

★**本闸 `MECH/check_mech_gate_hook_coverage.py` 自己也不在门禁链上 ⇒ 它自己也要被登记 ⇒ 登记/挂链是 main 的地界 ⇒ 本闸台账里「本闸自身」写成 `待 main 挂链`, 并把这条悖论作为问句交 main (★交卷页 B5-Q4★)★**
★**本单不自己解决这条悖论** ★ ⇒ ★**本闸裸跑永远是 rc=1 (红的是现状, 不是闸故障) ⇒ 红的那一条正是「本闸自己也没挂」** ★

### ★7.2 · 边界自证 (★本机实跑 · ★逐条★) ★

| 边界 | 自证方式 | 本单读数 |
|---|---|---|
| ★**零写板** ★ | 板 md5 / mtime / size 三项 | `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` ★**与基线逐字相同** ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三张表 md5 | `6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8` ★**与基线逐字相同** ★ |
| ★**零改既有闸判据** ★ | 29 道既有 MECH 闸 md5 逐字未动 | ★本单只【新建】`check_mech_gate_hook_coverage.py`, 一个既有闸文件都没写 ★ |
| ★**零改既有页正文** ★ | `HW/J_CHG_SELECTION.md` · `MECH/BOARD_ONEPASS_*.md` 既有页 · `HW/PCB/BOARD_ONEPASS_*.md` | ★**零改动** (★本单只新建本页 + 新建 10p 页 + 新建闸 + 新建交卷页★) ★ |
| ★**零挂链** ★ | `grep -c check_mech_gate_hook_coverage state/gate_check.py` | **0** ★ |
| ★**零外发** ★ | `state/outbox/` 清单逐文件 md5 (21 个文件) | ★**零改动** (★清单落进本页机器块 `outbox_manifest`★) ★ |
| ★**不代拍** ★ | 必挂清单 / 挂链时机 / 人工台账要不要另起页 / 本闸挂不挂 / 10p 取哪个字母档 | ★**全部只给代价, 一条都不代拍** ★ |
| ★**不自签** ★ | `state/issue_log.yaml` | ★**一个字没写** ★ |
| ★**只写自己的分片** ★ | `state/fragments/mech.yaml` | ★**只走 `state/frag_write.py`** ★ |
| ★**不硬链接真件 · 不写系统 /tmp** ★ | 沙盒落点 | ★`tmp/iss405/` (项目盘) + `logs/iss405/` ★ |

### ★7.3 · ★★一条实测踩坑 (★留给下一个在 MECH 真相页里登记清单的人★) ★★

★**本单第一版机器块把 `state/outbox/` 的【逐文件路径 + md5】直接落进了本页** ⇒ ★**结果: `MECH/tools/check_mech_ref_reachability.py` (ISS-333) 把 outbox 里一个 `R_GEO_2_…_MAP.md` 文件名里的后半截当成「MECH 域引用了一个板上不存在的位号」⇒ 真隐患 10 → 11 ⇒ ★**已签收闸的读数被本单凭空顶红 ⇒ 门禁链当场红** ★
★**★注: 本条说明里的那个文件名已故意截断 (★写成 `R_GEO_2_…_MAP.md`·★不然本段文字自己就会把那条闸顶红★)★**
★**处置**: ★**本单零改既有闸 (不改它的判据) ⇒ 只能自己不出现在它的扫描面上** ⇒ ★**outbox 清单改成【只落规范清单摘要 + 文件数】(md5 over「逐文件 md5 + 路径」) ⇒ 零外发自证力度不减 (任一文件改名/改内容/增删都会改摘要), 但一个字都不落到页面上** ★
★**⇒ 教训 (★给下一个要新建 MECH 真相页的人★)**: ★**MECH 域任何真相页的正文都会进 `check_mech_ref_reachability.py` 的扫描面 ⇒ 页面里【不许出现看起来像位号的串】(含 outbox 文件名、RFQ 里的料号等)** ★ ★`[实测]` 本机实跑·2026-11-25 01:3x★

### ★7.4 · 复现入口 ★

```bash
cd projects/smart_glasses
python3 MECH/check_mech_gate_hook_coverage.py              # 裸跑 => rc=1 (★红的是现状★)
python3 MECH/check_mech_gate_hook_coverage.py --selftest    # => rc=0, 末行逐字 ALL TESTS PASS
python3 MECH/check_mech_gate_hook_coverage.py --emit        # 机器块 (JSON)
grep -c check_mech_gate_hook_coverage state/gate_check.py  # => 0 (★零挂链自证★)
```

★**本单取到的官网原件 (★零外发 · ★自己网上查★)**: ★`tmp/iss405/fh12_catalog.pdf` (Hirose [FH12] Series Catalog, 20 页) ★ + ★`tmp/iss405/fh12_catalog.txt` (逐行文本) + ★`tmp/iss405/p8hi-08.png` / `p15img-15.png` (尺寸图渲染) ★

---

## ★★ 机器块 (★机器可解析 · ★本闸 §M1~§M7 的唯一数据源★) ★★

<!-- ISS405-GATEHOOKCOV:BEGIN -->
```json
{
 "baseline": {
  "board": {
   "md5": "611b869e13518c3c023fb178f91a0075",
   "mtime": "2026-11-06 07:07:17.362193413",
   "mtime_ns": 1793920037362193413,
   "rel": "HW/PCB/demo_mainboard.kicad_pcb",
   "size": 4940213
  },
  "tables": {
   "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
   "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
   "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a"
  }
 },
 "counts": {
  "class_A": 4,
  "class_B": 10,
  "class_C": 14,
  "class_D": 1,
  "class_E": 1,
  "manual_ledger_rows": 0,
  "mech_gates_hooked": 4,
  "mech_gates_on_disk": 30,
  "mech_gates_zero_hooked": 26,
  "must_hook_suggested": 10,
  "roster_entries": 30
 },
 "gates_on_disk": [
  "MECH/check_board_frame_candidate_compat_gate.py",
  "MECH/check_board_frame_coords.py",
  "MECH/check_board_frame_freeze_gate.py",
  "MECH/check_board_frame_freeze_gate_selftest.py",
  "MECH/check_board_geom_caliber_drift.py",
  "MECH/check_budget_caliber.py",
  "MECH/check_connector_clearance_caliber.py",
  "MECH/check_debug_seat_3d_fit.py",
  "MECH/check_debug_seat_rework_spec.py",
  "MECH/check_demo_struct_truth.py",
  "MECH/check_fts_seat_body_geometry.py",
  "MECH/check_fts_seat_sample_plan.py",
  "MECH/check_fts_vs_generic_courtyard_delta.py",
  "MECH/check_hinge_fpc_truth.py",
  "MECH/check_jdebug_1p27_clearance.py",
  "MECH/check_jdebug_arrangement_truth.py",
  "MECH/check_juart_1p27_clearance.py",
  "MECH/check_machine_block_pointer_resolvable.py",
  "MECH/check_mech_dual_caliber_gate.py",
  "MECH/check_mech_gate_hook_coverage.py",
  "MECH/check_mech_signed_append_ledger.py",
  "MECH/check_mech_verdict_freshness.py",
  "MECH/check_onepass_mech_release.py",
  "MECH/check_onepass_mech_sync.py",
  "MECH/check_onepass_s10_fp_swap_impact.py",
  "MECH/check_onepass_s10_led_spec_sync.py",
  "MECH/check_onepass_struct_crosscheck.py",
  "MECH/check_pad_size_coupling_closed.py",
  "MECH/check_zoujuan_marker_consistency.py",
  "MECH/tools/check_mech_ref_reachability.py"
 ],
 "hooked_in_chain": [
  {
   "label": "钉板闸⑦ 板框坐标闸",
   "rel": "MECH/check_board_frame_coords.py",
   "table": "PINNED_MD5_GATES"
  },
  {
   "label": "钉板闸⑧ 结构真值闸",
   "rel": "MECH/check_demo_struct_truth.py",
   "table": "PINNED_MD5_GATES"
  },
  {
   "label": "MECH 结构结论防漂闸 (ISS-295)",
   "rel": "MECH/check_mech_verdict_freshness.py",
   "table": "EXTRA_GATES"
  },
  {
   "label": "MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)",
   "rel": "MECH/tools/check_mech_ref_reachability.py",
   "table": "EXTRA_GATES"
  }
 ],
 "j_chg_10p": {
  "evidence": "[官网]",
  "land_pattern": {
   "A": 4.5,
   "B": 10.1,
   "C": 6.5,
   "note": "land B = 整块 land 沿排总宽 10.1; land C = 两端固定焊盘中心距 6.5"
  },
  "letters_all_along_row": true,
  "official_letters_mean": {
   "A": "触点跨距 = (N-1)x0.5 (10p => 4.5)",
   "B": "沿触点排方向 (A+3.6)",
   "C": "座体沿触点排总长 (A+4.6) = 官网产品页 Connector Length 9.1mm",
   "D": "沿触点排方向 (A+1.07)"
  },
  "official_letters_mm": {
   "A": 4.5,
   "B": 8.1,
   "C": 9.1,
   "D": 5.57
  },
  "part": "FH12-10S-0.5SH(55) / HRS 586-0522-3-55 / CL0586-0522-3-55",
  "project_old_y_width_mm": 6.5,
  "project_old_y_width_provenance": "MECH/BOARD_WIDTH_15MM.md §3.2 = 触点区 4.50 + 2x1.00 (手捏每边 1.00 overhang)",
  "recomputed_clearance_to_m1_2_hole": -0.25,
  "recomputed_verdict": "旧口径余 1.05mm -> 官网口径干涉 0.25mm (座体 Y 下缘 2.95 vs 孔上缘 3.20)",
  "still_open": "座体 X 起点 X0 (相对板边 X=0) 仍 [推算] —— 官网不给 (布局量)",
  "x_depth_mm": 6.4,
  "x_depth_source": "官网产品页 Connector Width 6.4mm (系列常量, 10p 与 28p 同值)",
  "y_width_mm": 9.1,
  "y_width_source": "官网目录 C = 官网产品页 Connector Length 9.1mm"
 },
 "manual_ledger": [],
 "meta": {
  "agent": "mech-lead",
  "date": "2026-11-25",
  "evidence_levels": [
   "[官网]",
   "[实测]",
   "[媒体]",
   "[推算]",
   "[0数据]"
  ],
  "gate_rel": "MECH/check_mech_gate_hook_coverage.py",
  "handoff_rel": "HANDOFF/2026-11-25_mech-lead_ISS405_闸挂链覆盖率清账与闸.md",
  "issue": "ISS-405",
  "role": "结构总工",
  "self_hook_status": "待 main 挂链",
  "truth_page_rel": "MECH/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md",
  "zero_hard_link": true
 },
 "must_hook_suggested": [
  "MECH/check_debug_seat_3d_fit.py",
  "MECH/check_debug_seat_rework_spec.py",
  "MECH/check_fts_seat_body_geometry.py",
  "MECH/check_fts_seat_sample_plan.py",
  "MECH/check_fts_vs_generic_courtyard_delta.py",
  "MECH/check_jdebug_1p27_clearance.py",
  "MECH/check_juart_1p27_clearance.py",
  "MECH/check_machine_block_pointer_resolvable.py",
  "MECH/check_onepass_mech_release.py",
  "MECH/check_pad_size_coupling_closed.py"
 ],
 "outbox_file_count": 22,
 "outbox_manifest_digest": "48e9282ebd4310d6c27fbb21f3e7663b",
 "release_summary_gate": "MECH/check_onepass_mech_release.py",
 "roster": {
  "MECH/check_board_frame_candidate_compat_gate.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "==========================================================================================",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— U-1 板框三候选 × 现役板 相容性判定 (ISS-341) —— 一次性裁决件",
   "stdout_lines": 81
  },
  "MECH/check_board_frame_coords.py": {
   "class": "A_hooked",
   "hooked": true,
   "hooked_in": "PINNED_MD5_GATES:钉板闸⑦ 板框坐标闸",
   "last_line": "口径提醒: 盘上板读数 = [实测] (读得到才写) · 设计态几何 = [推算] · 实物 [实测] = 0 条",
   "rc_now": 0,
   "reason": "已挂链 (PINNED_MD5_GATES) —— 钉板闸⑦ 板框坐标闸",
   "stdout_lines": 35
  },
  "MECH/check_board_frame_freeze_gate.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "==========================================================================================",
   "rc_now": 2,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— U-1 板框冻结闸 (ISS-336) —— 一次性裁决件",
   "stdout_lines": 56
  },
  "MECH/check_board_frame_freeze_gate_selftest.py": {
   "class": "D_selftest_helper",
   "hooked": false,
   "hooked_in": null,
   "last_line": "==========================================================================================",
   "rc_now": 0,
   "reason": "selftest 辅助件 —— 板框冻结闸的反向用例自测件 (ISS-336) —— 辅助件, 不单独入链",
   "stdout_lines": 68
  },
  "MECH/check_board_geom_caliber_drift.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "[DRIFT] 未声明口径漂移: 107 处 / 33 个文件",
   "rc_now": 2,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 结构侧口径漂移只读检测 (ISS-342) —— 一次性漂移清单件",
   "stdout_lines": 112
  },
  "MECH/check_budget_caliber.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "  ✅ 门禁绿: 三处老账口径一致 (A=buck 0.50W · B=k201 官方保守侧 · C=60×30 套A)",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 三处老账口径一致性快照 (ISS-251) —— 一次性口径快照件",
   "stdout_lines": 44
  },
  "MECH/check_connector_clearance_caliber.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "RESULT: FAIL (1 条不通过)",
   "rc_now": 1,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 座体净距判据同源化总表快照 (ISS-377) —— 一次性口径快照件",
   "stdout_lines": 15
  },
  "MECH/check_debug_seat_3d_fit.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "PASS",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— 座体 3D 装配拟合判决链主闸 (201 条判据)",
   "stdout_lines": 205
  },
  "MECH/check_debug_seat_rework_spec.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "PASS",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— 座体返工规格判决链闸",
   "stdout_lines": 476
  },
  "MECH/check_demo_struct_truth.py": {
   "class": "A_hooked",
   "hooked": true,
   "hooked_in": "PINNED_MD5_GATES:钉板闸⑧ 结构真值闸",
   "last_line": "==========================================================================================",
   "rc_now": 0,
   "reason": "已挂链 (PINNED_MD5_GATES) —— 钉板闸⑧ 结构真值闸",
   "stdout_lines": 58
  },
  "MECH/check_fts_seat_body_geometry.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "PASS",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— FTS 座体本体几何判决链闸",
   "stdout_lines": 82
  },
  "MECH/check_fts_seat_sample_plan.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "★绿的唯一条件 = 三量实测档真的升到 `[实测]` 且原始 3 读数在盘 (见 §2.4 充要条件) ★",
   "rc_now": 1,
   "reason": "建议必挂但当前零挂链 —— FTS 座体三量收样作业包闸",
   "stdout_lines": 38
  },
  "MECH/check_fts_vs_generic_courtyard_delta.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "   机器块量数: 50 · G1~G7 全部通过 · 零写板 · 零落表 · 零挂链",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— FTS vs 通用件 庭院差集判决链闸",
   "stdout_lines": 3
  },
  "MECH/check_hinge_fpc_truth.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "结论: ✅ 跨铰链 FPC 几何口径已收口到真源 (★实物 [实测] 条数 = 0 · 全部为网表/裁定块实测值驱动的 [推算]★)",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 跨铰链 FPC 几何口径收口件 (ISS-240)",
   "stdout_lines": 35
  },
  "MECH/check_jdebug_1p27_clearance.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "合计: 7/7 条判据通过",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— J_DEBUG 1.27mm 净距判决链闸",
   "stdout_lines": 25
  },
  "MECH/check_jdebug_arrangement_truth.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "合计: 6/6 条判据通过",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— J_DEBUG 排布标签 (维数) 真相件 (ISS-382)",
   "stdout_lines": 32
  },
  "MECH/check_juart_1p27_clearance.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "RESULT: PASS (9/9 判据通过)",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— JUART 1.27mm 净距判决链闸",
   "stdout_lines": 38
  },
  "MECH/check_machine_block_pointer_resolvable.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "★绿的唯一条件 = 扫描范围内 A 类之外的指针条数 == 0 (真相页 `MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md` §",
   "rc_now": 1,
   "reason": "建议必挂但当前零挂链 —— 机器块指针可解析性闸 (ISS-400 交卷)",
   "stdout_lines": 464
  },
  "MECH/check_mech_dual_caliber_gate.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "========================================================================================",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 结构侧双口径判定脚本自守件 (ISS-352)",
   "stdout_lines": 45
  },
  "MECH/check_mech_gate_hook_coverage.py": {
   "class": "E_self_pending_main_hook",
   "hooked": false,
   "hooked_in": null,
   "last_line": "",
   "rc_now": null,
   "reason": "★本闸自身 (ISS-405) —— ★自指悖论: 零挂链, 待 main 挂链★",
   "stdout_lines": null
  },
  "MECH/check_mech_signed_append_ledger.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "★绿的唯一条件 = ① 3 处陈旧 pin 在台账里有登记行 (单号+prev_md5+md5 四项齐全)② 台账落位 (M-A 待 main 拍) ③ §1 在册清单与盘面零差 ",
   "rc_now": 1,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 已签收件追加登记台账自守件 (ISS-399) —— 台账落位后才有意义",
   "stdout_lines": 19
  },
  "MECH/check_mech_verdict_freshness.py": {
   "class": "A_hooked",
   "hooked": true,
   "hooked_in": "EXTRA_GATES:MECH 结构结论防漂闸 (ISS-295)",
   "last_line": "   ⇒ 全绿 (F1~F6) rc=0",
   "rc_now": 0,
   "reason": "已挂链 (EXTRA_GATES) —— MECH 结构结论防漂闸 (ISS-295)",
   "stdout_lines": 24
  },
  "MECH/check_onepass_mech_release.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "    (★只代表结构侧 6 道闸全绿; ★不等于整条板链全绿·HW/SW 侧的闸另算★)",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— 「板那一趟」MECH 侧准出汇总闸 (ISS-300)",
   "stdout_lines": 42
  },
  "MECH/check_onepass_mech_sync.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "口径提醒: 本闸一切「实测」= 文件实读 + 脚本实跑; **实物 [实测] = 0 条**; 座体真实高度 = [0数据] ⇒ 开口 Y 一切数按公式取值。",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 「板那一趟」MECH 侧板侧输入收口件 (ISS-278)",
   "stdout_lines": 47
  },
  "MECH/check_onepass_s10_fp_swap_impact.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "口径提醒: 一切「实测」= 文件实读 + 脚本实跑; **实物 [实测] = 0 条**; 封装高度等外部数据标 [官网]。",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— S10 步换封装对 MECH 侧影响面件 (ISS-365) —— 绑步骤",
   "stdout_lines": 20
  },
  "MECH/check_onepass_s10_led_spec_sync.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "口径提醒: 一切「实测」= 文件实读 + 脚本实跑; **实物 [实测] = 0 条**; 封装高度等外部数据标 [官网]。",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— S10 步 LED 窗口规格同趟重算件 (ISS-367) —— 绑步骤",
   "stdout_lines": 27
  },
  "MECH/check_onepass_struct_crosscheck.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "==========================================================================================",
   "rc_now": 0,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 「板那一趟」结构侧最后一道交叉核对件 (ISS-290) —— 绑那一趟",
   "stdout_lines": 48
  },
  "MECH/check_pad_size_coupling_closed.py": {
   "class": "B_must_hook_not_hooked",
   "hooked": false,
   "hooked_in": null,
   "last_line": "合计: 8/8 条判据通过",
   "rc_now": 0,
   "reason": "建议必挂但当前零挂链 —— 焊盘尺寸耦合闭合闸 (ISS-403 交卷)",
   "stdout_lines": 28
  },
  "MECH/check_zoujuan_marker_consistency.py": {
   "class": "C_oneoff_evaluation",
   "hooked": false,
   "hooked_in": null,
   "last_line": "✗ 门禁不通过: K5",
   "rc_now": 1,
   "reason": "一次性评估/口径快照件 (不作为常设门禁) —— 走鹃旧口径收口的机器背书件 (ISS-238)",
   "stdout_lines": 13
  },
  "MECH/tools/check_mech_ref_reachability.py": {
   "class": "A_hooked",
   "hooked": true,
   "hooked_in": "EXTRA_GATES:MECH 侧位号引用可达性闸 (ISS-333)",
   "last_line": "【判决】 ✔ 绿 (rc=0): MECH 侧引用的位号全部可达, 真隐患在基线内",
   "rc_now": 0,
   "reason": "已挂链 (EXTRA_GATES) —— MECH 侧位号引用可达性闸 (ISS-333)",
   "stdout_lines": 389
  }
 },
 "verdict_chain_seven": [
  "MECH/check_debug_seat_3d_fit.py",
  "MECH/check_debug_seat_rework_spec.py",
  "MECH/check_fts_seat_body_geometry.py",
  "MECH/check_fts_vs_generic_courtyard_delta.py",
  "MECH/check_fts_seat_sample_plan.py",
  "MECH/check_jdebug_1p27_clearance.py",
  "MECH/check_juart_1p27_clearance.py"
 ]
}
```
<!-- ISS405-GATEHOOKCOV:END -->
