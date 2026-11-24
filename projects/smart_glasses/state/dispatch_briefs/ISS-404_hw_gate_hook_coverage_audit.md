# ★ISS-404 · hw-lead · 板那一趟【预检清单/作业包点名的闸 ⇒ 门禁链挂链覆盖率】双向清账 + fail-closed 闸 ★

★**单号**: ISS-404 · ★**派活**: 项目总工 (main / moli) · ★**执笔**: hw-lead (硬件总工) · ★**日期**: 2026-11-25
★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
★**主线关系**: ★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属 ★**「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板)** ★

---

## ★0 · 一句话题面 ★

★★**「板那一趟」的预检清单里点名的闸, 有一大半【不在门禁链 `state/gate_check.py` 上】—— 其中就有投板前最命门的两道 `check_pcb_drc.py` (DRC + C6 生产文件齐) 与 `check_pcb_nets.py` (C1 缺失/多余焊盘) ⇒ 全仓唯一的 fail-closed 自动链【不跑它们】, 它们只活在人工清单里 ⇒ 【漏跑 = 没有任何机器会响】⇒ 板投出去才发现 ⇒ 板改第二次 / 板投出去才发现 ★★**

---

## ★★一 · 题面 (★main 2026-11-25 01:1x 本机实读 + 本机实算, 不抄任何 agent 报告★) ★★

### ★1.1 · 三个本机实测数字 (★可复现★) ★

| 事实 | 实测读数 | 出处 (★本机实读★) |
|---|---|---|
| ★**门禁链只挂 18 道闸** ★ | `EXTRA_GATES` 7 道 + `PINNED_MD5_GATES` 10 道 + HW pinout 闸 1 道 = **18** | `state/gate_check.py` L211 `EXTRA_GATES` / L262 `PINNED_MD5_GATES` / 裸跑 `python3 state/gate_check.py` ⇒ 【Q7 钉板 md5 闸链】10/10 道绿 |
| ★**仓内闸脚本共 105 道** ★ | **HW 45 / MECH 29 / SW 31** ⇒ ★**零挂链 87 道** ★ | `glob('HW/**/check_*.py') + ('MECH/**/check_*.py') + ('SW/**/check_*.py')` (★**注意 `MECH/tools/` 与 `SW/tools/` 子目录也要扫, 只扫顶层会漏★**) |
| ★**SW 域已有同款覆盖率闸, HW / MECH 两域没有** ★ | 仓里 coverage/health 类闸只有 `SW/tools/check_sw_gate_chain_coverage.py` (ISS-392 交卷) · `SW/tools/check_sw_gate_health.py` (ISS-388 交卷) · `HW/check_onepass_preflight_coverage.py` (P1~P6) · `HW/check_fp_truth_coverage_gap.py` · `SW/tools/iq_coverage_check.py` | 仓内实扫 |

### ★1.2 · ★★【命门】: 板那一趟的三份作业面文件里点名的闸, 未挂链的那些 ★★

| 文件 | 点名闸数 | 已挂链 | ★**未挂链** ★ |
|---|---|---|---|
| `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★预检清单★) | 12 | 4 | ★**8** ★ |
| `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★作业包★) | 18 | 6 | ★**12** ★ |
| `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` (★提交顺序页★) | 3 | 2 | ★**1** ★ |

★**未挂链的逐条名单 (main 实测, 交卷页要重跑一遍并逐字对上)★**:
`check_board_frame_caliber.py` · `check_iss354_mfg_closure.py` · `check_iss354_manufacturability.py` · `check_netlist_contradiction_r3.py` · `check_netlist_selfconsistency.py` · `check_onepass_mech_sync.py` · `check_onepass_s10_manifest.py` · `check_onepass_struct_crosscheck.py` · `check_part_selection_matrix.py` · `check_pcb_drc.py` · `check_pcb_generator_defaults.py` · `check_pcb_nets.py` · `check_step1_parts_spec.py`

★**其中最要命的两道 (★投板前的命门闸★)**:
- ★**`state/check_pcb_nets.py`** ⇒ C1 缺失/多余焊盘一致性 ⇒ ★**今天就是红的** (★`C_VBUS_GND` pad1 = `GND` / pad2 = `VBUS_5V_CHG` ⇒ 焊盘级多余 2★ ⇒ 这正是 ISS-402 §3 那条掉板机理的同一件事★) ★
- ★**`state/check_pcb_drc.py`** ⇒ DRC + C6 生产文件齐 ⇒ ★**它同时是预检清单 B25 (unconnected 45→0) 与 B28 (留证链/盖章/发布闸) 的判据命令** ★
⇒ ★**这两道今天的读数就是红的, 而【全仓唯一的自动链不跑它们】⇒ 板那一趟当天, 只有「人记得翻清单」这一道防线 ★**

### ★1.3 · ★为什么至今没有机器闸盯这一格 ★

★**既有覆盖度闸 `HW/check_onepass_preflight_coverage.py` (★已挂在钉板闸④★) 的判据逐条读过★**:
`P1 清单可解析` · `P2 归属步合法 (S1~S13 每步至少被覆盖一次)` · ★**`P3 判据命令真存在: 每条 criterion 里引用的脚本文件在本机真实存在`** ★ · `P4 覆盖度 (25 个板侧标记每个都必须出现)` · `P5 现状一致` · `P6 受保护 5 件 md5`
⇒ ★**P3 查的是「脚本在不在」, 不是「它在不在 fail-closed 链上」⇒ 本缺口至今零机器闸覆盖★** ★
⇒ ★**反向也成立**: ★**挂链表里引用的脚本若哪天被删/改名, 链上那一条会直接变成「脚本跑不起来 ⇒ 算闸红」(fail-closed 语义成立)** ⇒ ★**所以本单要盯的是【反向】: 清单点名的闸【不在链上】这件事, 全仓没有任何一道闸会红★**

### ★1.4 · 坏结局 (★为什么值钱★)

★**「板只改一次」= 板 md5 全生命周期只许变 1 次** ⇒ ★**投板前的每一道检查, 都是「板改第二次」的最后一道闸** ★
⇒ 坏结局二选一: ① **人工漏跑** ⇒ 网表/板面不一致 (C1 多余焊盘) 或 DRC 不干净 ⇒ 投出去的板是错的 ⇒ **要么板改第二次 (2-4 周 + 一批板的钱), 要么流到用户手里** ② ★**闸红了没人知道** ⇒ 跟 ISS-388 的诊断一模一样 (★「闸自己坏了」这件事本身零检测手段★) ★

---

## ★★二 · 本单交付 (★5 件 · 全部零写板★) ★★

| # | 交付物 | 路径 | 验收口径 |
|---|---|---|---|
| ① | 真相页 | ★**新建** `HW/PCB/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md` ★ | §0~§7 + 机器块; ★**三张表**: (a) 清单/作业包/提交顺序页点名的闸 × 是否挂链 × 挂在哪张表 (`EXTRA_GATES` / `PINNED_MD5_GATES` / 无) (b) 仓内 105 道闸的四分类 (已挂链 / ★必挂但漏挂★ / 一次性沙盒件 (文件名以 `_sbx` 结尾的那类) / selftest 辅助件) (c) ★**真漏挂的逐条后果**: 哪一道坏结局靠它拦、拦不住会怎样 ★ |
| ② | 新闸 | ★**新建** `HW/check_onepass_gate_hook_coverage.py` ★ | ★**裸跑 rc=1** (★红的是现状, 不是闸故障★) · `--selftest` **rc=0** · 末行逐字 `ALL TESTS PASS` (★正向 ≥1 + 反向 ≥8★) · ★**零挂链** (★`grep -c check_onepass_gate_hook_coverage state/gate_check.py` = 0★) |
| ③ | 交卷页 | ★**新建** `HANDOFF/2026-11-25_hw-lead_ISS404_闸挂链覆盖率清账与闸.md` ★ | B1~B7 全填 (★标题用仓里规范口径, Q1 六块齐全★) |
| ④ | 自有分片收口 | `state/fragments/hw.yaml` | ★**只走 `state/frag_write.py`** ★ (★禁止 `open(p,"w")`★) · 写后四项自检: 条数 / 丢 key / 多的 key / 内容有变的条 (★老条目逐字比对★) |
| ⑤ | 留证 | `logs/iss404/` + 沙盒 `tmp/iss404/` | ★**不硬链接真件 · 不写系统 `/tmp`** ★ |

### ★2.1 · 新闸的判据骨架 (★main 给的方向, 具体实现你定, 但不许放松★) ★

| 判据 | 要求 |
|---|---|
| ★**G1 清单↔挂链 双向闭环** ★ | ★**清单/作业包/提交顺序页点名的每一道闸, 必须在【挂链表】或【人工签核台账】里二者其一; 两者皆无 ⇒ 判红** ★ (★fail-closed: 闸脚本缺失 / 跑不起来 ⇒ 一律算红★) |
| ★**G2 挂链表引用的脚本真实存在** ★ | 挂链表里每一条的脚本路径必须在本机存在 ⇒ 不存在 ⇒ 判红 (★防「幽灵闸」★) |
| ★**G3 分类台账自洽** ★ | 仓内每道闸必须在四分类里有且只有一个归属; ★**新闸脚本自己也要在台账里登记** ★ (★防「自指漏洞」★) |
| ★**G4 板三证不动** ★ | 板 / 网表 / 脚表 / BOM md5 与基线逐字相同 (★基线 md5 = `611b869e13518c3c023fb178f91a0075`★) |
| ★**G5 零挂链 + 零外发自证** ★ | `grep -c` 本闸名在 `state/gate_check.py` = 0; ★`state/outbox/` 未动 ★ |
| ★**G6 证据分级** ★ | 每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` |
| ★**G7 零写板自证** ★ | 板 md5 / mtime / size 三项与基线逐字相同 |

★**★自指悖论 (★必须在交卷页点名, 并且不许自己解决★)★**: ★**新闸 G1 要求「清单点名的闸都要在链上或台账里」—— 而本闸自己也不在链上 ⇒ 逻辑上它也该被登记进台账, 而登记它的动作在 main 地界 (挂链) ⇒ ★本闸的台账里「本闸自身」这一行请写成 `待 main 挂链`, 并把这条悖论作为问句交 main, 不许自己拍板★ ★**

### ★2.2 · 必跑命令 (★交卷页 B6 要贴原样输出 + rc★) ★

```
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-404_hw_gate_hook_coverage_audit.md   # rc=0
python3 HW/check_onepass_gate_hook_coverage.py                       # rc=1 (红的是现状)
python3 HW/check_onepass_gate_hook_coverage.py --selftest             # rc=0, 末行 ALL TESTS PASS
python3 HW/check_onepass_preflight_coverage.py                        # 既有闸不许被本单弄红 (★原样读数★)
python3 state/merge.py                                               # rc=0
python3 state/gate_check.py                                          # rc=0, Q1 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv   # 与基线逐字相同
```

---

## ★★三 · 边界 (★违反任一条 ⇒ 本单交卷无效★) ★★

| ★边界★ | ★怎么自证★ |
|---|---|
| ★**零写板** ★ | 板 md5 / mtime / size 三项与基线逐字相同 |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三张表 md5 与基线逐字相同 |
| ★**零改既有闸判据** ★ | `HW/check_onepass_preflight_coverage.py` 等既有闸 md5 逐字未动 |
| ★**零改既有页正文** ★ | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `BOARD_ONEPASS_WORKPACKET.md` / `BOARD_ONEPASS_COMMIT_ORDER.md` md5 逐字未动 (★只读 + 只引用★) |
| ★**零挂链** ★ | `grep -c check_onepass_gate_hook_coverage state/gate_check.py` = **0** (★挂链是 main 的机制地界★) |
| ★**零外发** ★ | ★**不许发任何邮件/询价/问询/采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ `state/outbox/` 零改动 ★ |
| ★**不代拍** ★ | 「哪些闸必挂 / 挂链顺序 / 人工签核台账要不要另起页 / 本闸挂不挂链」★**一律只给代价, 不代拍** ★ |
| ★**不自签** ★ | ★`state/issue_log.yaml` 一个字不许写 (★由 main 签收★) ★ |
| ★**只写自己的分片** ★ | 只写 `state/fragments/hw.yaml` (★走 `frag_write.py`★) |

---

## ★★四 · 留给 main 的问句 (★一条都不代拍 · 每条带问法 / 建议默认值 / 不答后果 / 代价★) ★★

1. **Q1** 真漏挂清单要挂哪几道? (★建议: 清单点名的 8 道里, `check_pcb_nets.py` / `check_pcb_drc.py` / `check_netlist_selfconsistency.py` / `check_part_selection_matrix.py` 四道优先 —— 它们分别是网表一致性 / DRC / 网表自洽 / 选型矩阵★) ⇒ 不答 ⇒ 人工清单仍是唯一防线
2. **Q2** 挂链顺序? (★建议: 先挂「今天就是红的」那两道? ★—— 注意: `check_pcb_nets.py` 今天 C1 红 ⇒ 挂上去门禁链当场红 ⇒ 挂链时机要不要与「板那一趟」的 C1 修复同批★) ⇒ 不答 ⇒ 挂了链 = 门禁链常红 = 红了被当噪音
3. **Q3** 「人工签核台账」要不要另起页? (★建议: 起一页, 逐条写明「谁在哪一步跑了它 / 读数是多少」★) ⇒ 不答 ⇒ 未挂链的闸 = 没人跑也没人知道
4. **Q4** ★**本闸自己挂不挂链? (自指悖论)** ★ ⇒ 不答 ⇒ 本闸永远零挂链 = 又一个「没人跑」的闸 (★同 ISS-388 病★)
5. **Q5** 仓内 105 道闸的分类台账要不要进 `state/fragments/hw.yaml` 的 `interface_claims`? ⇒ 不答 ⇒ 下一个总工又得自己数一遍
