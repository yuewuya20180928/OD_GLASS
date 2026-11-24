# ★ISS-405 · mech-lead · MECH 域【闸挂链覆盖率】清账 + fail-closed 闸 ★＋ 附带一条已开的 open need (J_CHG 10p 座体几何) ★

★**单号**: ISS-405 · ★**派活**: 项目总工 (main / moli) · ★**执笔**: mech-lead (结构总工) · ★**日期**: 2026-11-25
★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
★**主线关系**: ★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属 ★**「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板)** ★

---

## ★0 · 一句话题面 ★

★★**MECH 域 29 道闸, 门禁链上只挂了 4 道 ⇒ 25 道零挂链 —— 其中包括 ISS-403 刚交卷的那道【焊盘尺寸耦合闸】、ISS-400 的【机器块指针闸】, 以及【7 道判决链闸】(结构侧出件判据) 与【准出汇总闸 `check_onepass_mech_release.py`】⇒ 「板那一趟」当天, 「MECH 侧能不能出 Gerber」和「结构件按旧数出件会不会装配干涉」这两件事, 【全都不在任何自动链上】⇒ 唯一的防线是「人记得跑」⇒ 漏跑 = 板改第二次 ★★**

---

## ★★一 · 题面 (★main 2026-11-25 01:1x 本机实读 + 实算, 不抄任何 agent 报告★) ★★

### ★1.1 · 本机实测三个数字 (★可复现★) ★

| 事实 | 实测读数 | 出处 |
|---|---|---|
| ★**MECH 域闸脚本 29 道** ★ | `glob('MECH/**/check_*.py')` (★**含 `MECH/tools/` 子目录★**) | 仓内实扫 |
| ★**门禁链只挂 4 道 MECH 闸** ★ | `check_board_frame_coords.py` (钉板闸⑦) · `check_demo_struct_truth.py` (钉板闸⑧) · `check_mech_verdict_freshness.py` (EXTRA_GATES) · `check_mech_ref_reachability.py` (EXTRA_GATES·`MECH/tools/`) | `state/gate_check.py` L211 `EXTRA_GATES` / L262 `PINNED_MD5_GATES` |
| ★**⇒ 零挂链 25 道** ★ | 含 ★**ISS-400 交卷的 `check_machine_block_pointer_resolvable.py`** ★ · ★**ISS-403 交卷的 `check_pad_size_coupling_closed.py`** ★ · ★**7 道判决链闸** ★ · ★**`check_onepass_mech_release.py` (ISS-300 的 MECH 侧准出汇总闸)** ★ | 同上 |

★**7 道判决链闸 (★ISS-403 交卷逐条点名过, 本单要自己重数一遍并逐字对上★)**:
`check_debug_seat_3d_fit.py` (★**201 条判据**★) · `check_debug_seat_rework_spec.py` · `check_fts_seat_body_geometry.py` · `check_fts_vs_generic_courtyard_delta.py` · `check_fts_seat_sample_plan.py` · `check_jdebug_1p27_clearance.py` · `check_juart_1p27_clearance.py`
★**⇒ 这 7 道全都不在链上 ⇒ ISS-403 那个「焊盘放大 ⇒ 7 个数全作废」的坏结局, 连「它自己新建的那道闸」也不在链上 ⇒ 全程零自动防线 ★**

### ★1.2 · 为什么这件事在「板只改一次」的关键路径上

★**「板只改一次」= 板 md5 全生命周期只许变 1 次** ⇒ ★**投板前的结构侧每一道检查, 都是「板改第二次」的最后一道闸** ★
★**具体链路 (★ISS-403 已实测的★)**:
`板那一趟把焊盘 1.000 → 1.110` ⇒ ★**MECH 判决链 7 个数全作废** (★`4.8100→4.9200` / `2.2700→2.3800` / `6.6100→6.7200` / `4.0700→4.1800` / `0.1350→0.0800` / `2.6950→2.6400` / `0.7700→0.7150`★) ⇒ 结构件按旧数出件 ⇒ 装配干涉 ⇒ **板改第二次**
⇒ ★**而这条链上的每一道闸 (含 ISS-403 新建的那道) 都不在门禁链上 ⇒ 「板的那一趟」当天没有任何机器会响** ★
★**另有一条更早的链**: ★`check_onepass_mech_release.py` (ISS-300 交卷, ★**「板那一趟」MECH 侧准出汇总闸: 一条命令出「S6 重出板后能不能出 Gerber」的结构侧结论**★) ⇒ ★**它也不在链上 ⇒ 「能不能出 Gerber」这条结论同样只靠人记得跑** ★

### ★1.3 · ★为什么至今没有机器闸盯这一格 ★

★**SW 域已经做过同款 (ISS-392 交卷 `SW/tools/check_sw_gate_chain_coverage.py` + ISS-388 交卷 `SW/tools/check_sw_gate_health.py`)** ⇒ ★**HW / MECH 两域至今没有同款** (★main 实扫: 仓里 coverage/health 类闸只有 SW 那两道 + `HW/check_onepass_preflight_coverage.py` + `HW/check_fp_truth_coverage_gap.py` + `SW/tools/iq_coverage_check.py`★)
⇒ ★**⇒ 也就是说: 【SW 域有「闸挂链覆盖率」这道闸, MECH 域没有】⇒ MECH 域的「零挂链」至今零机器检测手段★**

### ★1.4 · ★★附带一条【已开着的 open need】(★due 2026-11-26 · 明天到期★) ★★

★**need key = `iss384_jchg_10p_dims_geometry`** (★登记在 `state/fragments/hw.yaml` 的 `needs_from` 里 · `to: mech-lead` · `status: open` · `due: 2026-11-26`★)
★**它要你回的是 (★逐字★)**:
> ★**ISS-384 §7 补钉时查到的官网 10p 尺寸** (★Hirose [FH12] Series Catalog Nov.1.2026 尺寸表★): `FH12-10S-0.5SH()` / HRS No. 586-0522-3 / 10 contacts / ★**A=4.5 / B=8.1 / C=9.1 / D=5.57 (mm)** ★[官网] ★
> ★**`HW/J_CHG_SELECTION.md` §4.1/§4.2 现在用的是 28p 的进深 6.4mm (L199)** ⇒ ★**10p 档若按官网 D=5.57 或 A=4.5 判, 「与 M1.2 孔① 间隙 1.05mm」与「座体 X 向进深未核 [推算]」两条结论可能变** ★
> ★**几何归属 = mech-lead 地界, hw-lead 只登记数据不判定 ⇒ 请回: 10p 的 X 向进深 / Y 向占宽各取哪个字母, 以及间隙是否要重算** ★
> ★**证据等级 [官网] (Hirose 官网产品页 + 系列目录); 零外发** ★

★**本单怎么用它 (★不许顺手改网表/落表, 只许算 + 落页 + 回答★)★**: ★**只做几何判定与结论回写 (落成一份 MECH 侧页 + 在 `state/fragments/mech.yaml` 登记一条 `answer`)** ⇒ ★**不许改 `HW/J_CHG_SELECTION.md` 正文 (★那是 hw-lead 的地界 + 已签收件★) ⇒ 要改的话写成【追加式建议】交 main★ ★

---

## ★★二 · 本单交付 (★5 件主项 + 1 件附带项 · 全部零写板★) ★★

| # | 交付物 | 路径 | 验收口径 |
|---|---|---|---|
| ① | 真相页 | ★**新建** `MECH/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md` ★ | §0~§7 + 机器块; ★**三张表**: (a) MECH 域 29 道闸 × 是否挂链 × 挂在哪张表 (b) 四分类台账 (已挂链 / ★必挂但漏挂★ / 一次性沙盒件 / selftest 辅助件) (c) ★**真漏挂逐条后果**: 拦不住会出哪种坏结局 ★ |
| ② | 新闸 | ★**新建** `MECH/check_mech_gate_hook_coverage.py` ★ | ★**裸跑 rc=1** (★红的是现状, 不是闸故障★) · `--selftest` **rc=0** · 末行逐字 `ALL TESTS PASS` (★正向 ≥1 + 反向 ≥8★) · ★**零挂链** ★ |
| ③ | 交卷页 | ★**新建** `HANDOFF/2026-11-25_mech-lead_ISS405_闸挂链覆盖率清账与闸.md` ★ | B1~B7 全填 (★标题用仓里规范口径, Q1 六块齐全★) |
| ④ | 自有分片收口 | `state/fragments/mech.yaml` | ★**只走 `state/frag_write.py`** ★ · 写后四项自检 (条数 / 丢 key / 多的 key / 内容有变的条) · ★**`needs_from` 全 `to: main`** ★ |
| ⑤ | 留证 | `logs/iss405/` + 沙盒 `tmp/iss405/` | ★**不硬链接真件 · 不写系统 `/tmp`** ★ |
| ⑥ | ★**附带项** ★ | ★**新建** `MECH/BOARD_ONEPASS_J_CHG_10P_GEOMETRY.md` (或并进真相页 §6) ★ | ★**回答 `iss384_jchg_10p_dims_geometry`**: X 向进深 / Y 向占宽各取官网哪个字母 + 间隙是否要重算 + 证据等级 ★ |

### ★2.1 · 新闸的判据骨架 (★main 给方向, 实现你定, 但不许放松★) ★

| 判据 | 要求 |
|---|---|
| ★**M1 分类台账自洽** ★ | MECH 域每道闸必须在四分类里有且只有一个归属; ★**新闸脚本自身也要登记** ★ (防自指漏洞) |
| ★**M2 必挂闸清单闭环** ★ | ★**「MECH 侧准出必挂闸清单」里每一道, 必须在【挂链表】或【人工签核台账】里二者其一; 两者皆无 ⇒ 判红** ★ (★fail-closed: 脚本缺失 / 跑不起来 ⇒ 一律算红★) |
| ★**M3 挂链表引用的脚本真实存在** ★ | 不存在 ⇒ 判红 (防幽灵闸) |
| ★**M4 7 道判决链闸 + 准出汇总闸的归属必须显式登记** ★ | ★**不许「未分类」蒙过去** ★ |
| ★**M5 板三证不动** ★ | 板 / 网表 / 脚表 / BOM md5 与基线逐字相同 (★基线 md5 = `611b869e13518c3c023fb178f91a0075`★) |
| ★**M6 零挂链 + 零外发自证** ★ | `grep -c` 本闸名在 `state/gate_check.py` = 0; `state/outbox/` 未动 |
| ★**M7 证据分级 + 10p 几何的回答带等级** ★ | `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` |

★**★自指悖论 (★交卷页必须点名, 不许自己解决★)★**: ★**新闸自己也不在链上 ⇒ 它自己也要被登记 ⇒ 登记/挂链是 main 地界 ⇒ 本闸台账里「本闸自身」写成 `待 main 挂链`, 并把这条悖论作为问句交 main★ ★**

### ★2.2 · 必跑命令 (★交卷页 B6 要贴原样输出 + rc★) ★

```
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-405_mech_gate_hook_coverage_and_jchg10p.md   # rc=0
python3 MECH/check_mech_gate_hook_coverage.py                 # rc=1 (红的是现状)
python3 MECH/check_mech_gate_hook_coverage.py --selftest       # rc=0, 末行 ALL TESTS PASS
python3 MECH/check_onepass_mech_release.py                     # 既有闸不许被本单弄红 (★原样读数★)
python3 MECH/check_pad_size_coupling_closed.py                 # ISS-403 交卷件: 原样读数 (★rc=0★)
python3 MECH/check_machine_block_pointer_resolvable.py         # ISS-400 交卷件: 原样读数 (★rc=1 红的是现状★)
python3 state/merge.py                                         # rc=0
python3 state/gate_check.py                                    # rc=0, Q1 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv   # 与基线逐字相同
```

---

## ★★三 · 边界 (★违反任一条 ⇒ 本单交卷无效★) ★★

| ★边界★ | ★怎么自证★ |
|---|---|
| ★**零写板** ★ | 板 md5 / mtime / size 三项与基线逐字相同 |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三张表 md5 与基线逐字相同 (★10p 几何那条也不许落表★) |
| ★**零改既有闸判据** ★ | 11+ 道既有 MECH 闸 md5 逐字未动 (★含 ISS-399/400/403 三趟交卷的闸★) |
| ★**零改既有页正文** ★ | `HW/J_CHG_SELECTION.md` (★hw-lead 地界★) · `MECH/BOARD_ONEPASS_*.md` 既有页 · `HW/PCB/BOARD_ONEPASS_*.md` 全部 md5 逐字未动 |
| ★**零挂链** ★ | `grep -c check_mech_gate_hook_coverage state/gate_check.py` = **0** |
| ★**零外发** ★ | ★**不许发任何邮件/询价/问询/采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ `state/outbox/` 零改动; ★**10p 尺寸只用官网/系列目录, 零外发** ★ |
| ★**不代拍** ★ | 「哪些闸必挂 / 挂链顺序 / 人工签核台账要不要另起页 / 本闸挂不挂链 / 10p 取哪个字母档」★**一律只给代价, 不代拍** ★ |
| ★**不自签** ★ | ★`state/issue_log.yaml` 一个字不许写 ★ |
| ★**只写自己的分片** ★ | 只写 `state/fragments/mech.yaml` (★走 `frag_write.py`★) |

---

## ★★四 · 留给 main 的问句 (★一条都不代拍 · 每条带问法 / 建议默认值 / 不答后果 / 代价★) ★★

1. **Q1** MECH 域「必挂闸清单」取哪几道? (★建议: 7 道判决链闸 + `check_onepass_mech_release.py` + ISS-400/403 两道新闸 = 10 道★) ⇒ 不答 ⇒ 结构侧护栏继续零自动防线
2. **Q2** 挂链时机? (★建议: 与「板那一趟」同批, 别今天挂 —— `check_fts_seat_sample_plan.py` 等今天就是红的, 挂了链 = 门禁链常红 = 红了被当噪音★) ⇒ 不答 ⇒ 挂链时机随人 ⇒ 红了被当噪音
3. **Q3** 「人工签核台账」要不要另起页? ⇒ 不答 ⇒ 未挂链的闸 = 没人跑也没人知道
4. **Q4** ★**本闸自己挂不挂链? (自指悖论)** ★ ⇒ 不答 ⇒ 本闸永远零挂链 = 又一个「没人跑」的闸
5. **Q5** ★**J_CHG 10p 几何**: X 向进深取官网哪个字母 / Y 向占宽取哪个 / 间隙要不要重算? ⇒ 不答 ⇒ `HW/J_CHG_SELECTION.md` §4.1/§4.2 继续按 28p 的 6.4mm 判 ⇒ 座体外形结论可能错 (★`[推算]` 级悬着★)
6. **Q6** 10p 的结论要不要落进 `HW/J_CHG_SELECTION.md` (追加式) —— ★那是 hw-lead 的地界, 本单只出建议, 由 main 指派★ ⇒ 不答 ⇒ 结论停在 MECH 侧页, 落表批次没人认领
