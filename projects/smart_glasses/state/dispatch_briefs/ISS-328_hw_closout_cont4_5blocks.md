# 任务书 · ISS-328 cont4 (hw-lead) —— 【只填 5 块 + 写分片】· 纯写型 · 零写板

> **单号**: ISS-328 cont4 · **owner**: hw-lead (硬件总工) · **verify_by**: main · **派活 job**: cron `775d9893` (ARS45 继续执行后继计划) · **日期**: 2026-11-18 23:3x (Asia/Shanghai)
> **性质**: ★**PCB 线 · 纯收卷/填实类** ★ · ★**零写板 · 零落表 · 零改闸 · 零改生成器代码 · 零改网表/脚表/BOM/原理图真源 · 零改别人的分片** ★ · ★**零外发** ★ · 不替老板拍板 · 不自签 `state/issue_log.yaml`

---

## ★★① 派活顺序铁律 (★违反这条就是白跑一轮★)★★

★**第 1 步 = write (★填 5 块·先写文件★) → 第 2 步 = write 分片 (★`state/fragments/hw.yaml`·走 `state/frag_write.py`★) → 第 3 步 = 才跑必跑项 (★`state/gate_check.py` 只许跑一次·加 `timeout`·★不许跑 `--json` 版★)★**

★**为什么写死这条**: ★**上一趟 (cont3 · 21:5x→22:17) 的死因 = 12 分钟全烧在【跑必跑项】上 ⇒ 交卷页一个字节没写** ★ (★同型死法已在兄弟 job 21:5x 记录: 「顺序死法」★)
★**⇒ 所以: 交付物优先, 门禁最后跑一次, 跑不完就在 B5 写「未跑」+ 原因, 不许反复重跑★**

---

## ★★② 本单要干的活 (★一共就 5 个占位符 + 1 次分片写★)★★

★**交付页已经做完了, 一个字都不许改**: `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` (58,493 B @22:13:42 · ★占位符 0★) ★

★**只剩交卷页** `HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md` (8,156 B @22:13:52) ★**5 处 `<!-- B* -->` 占位符**:

| 行 | 占位符 | 块标题 (★标题已在盘上, 只许在占位符位置填正文, 不许改标题★) | 填什么 |
|---|---|---|---|
| ★**72** ★ | `<!-- B2_ACCEPTANCE -->` | `## B2 验收标准自评 (★逐条 通过 / 不通过 / 未验★)` | ★**逐条**列验收项 + 判决 (通过 / 不通过 / 未验) ★ |
| ★**78** ★ | `<!-- B3_EVIDENCE -->` | `## B3 证据分级` | ★**每条结论打证据标签** (`[实测]` / `[推算]` / `[0数据]` / `[官网]`) + 证据文件路径 ★ |
| ★**84** ★ | `<!-- B4_INTERFACE -->` | `## B4 接口取值声明 (★别人要照抄的东西逐字给★)` | ★**逐字给**: 读数表里的候选/官方两列数字 · 退铜名单 2 条 · 逐网孤岛 7 条 · 段内翻转分母 47 与 20/47 · 段数 3,986 vs 18,092 ★ |
| ★**90** ★ | `<!-- B5_OPEN -->` | `## B5 未决项与卡点 (★需要谁回答什么★)` | ★**需要 main / 老板各拍什么的清单** (★本单【不代拍】★) ★ |
| ★**96** ★ | `<!-- B6_REPRO -->` | `## B6 自证复现命令 (★原样贴输出★)` | ★**4 条只读自证命令 + 原样输出** (★见 §④★) ★ |

★**★分片**: `state/fragments/hw.yaml` 里 ISS-328 的 status 段 (★当前 L11~L13 还写着「右上臂后台起链中 … 六条读数待收」⇒ 已过期, 要改成【最终判决 REJECT】口径★) + 已有 3 条 need (`iss328_ru_arm_gate_verdict` / `iss328_p1_partpos_20_must_keep` / `iss328_ru_arm_vs_ctl_arm_diff`) 的 **value 改成最终读数** (★不许新造重复 key★) · ★**写法必须走 `python3 state/frag_write.py --agent hw-lead` (原子写)·禁 `open(p,"w")`★**

---

## ★★③ 数字只能来自机器读数 (★名单制铁律: 不许自己再数一遍★)★★

★**唯一读数来源** (★★照抄, 不许重算, 不许改写数字★★):

- ★`logs/iss328/33_recalc_gate_rc.txt` (★3,391 B @22:13★) ⇒ ★**名单制闸 rc 复算** ★
  - 复算 ① 右上臂链终板 vs 官方板: ★**RC_FINAL_OFFICIAL=1** ★
  - 复算 ② clrfix 终板 vs 官方板: ★**RC_CLRFIX_OFFICIAL=1** ★
  - 候选板 `tmp/iss328/chain_iss328_s8ru/final_chain.kicad_pcb` / `tmp/iss328/_clrfix_iss328_s8ru_final.kicad_pcb` · 基线板 `HW/PCB/demo_mainboard.kicad_pcb`
  - ★**退铜名单 (官方板有铜⇒候选零铜): 2 条 ⇒ `CSI_MCLK_SRC` · `USB_CC1`** ★ (★只有这 2 条, 一条都不许多写★)
  - ★**差分对死腿: 0** ★ · ★**逐网孤岛变多: 7 条 ⇒ `BOOT_N` · `CSI_D0_CK_N` · `CSI_MCLK` · `CSI_MCLK_SRC` · `KEY_VOL_P` · `LED_B` · `USB_CC1`** ★
  - ★**救回零铜的网: 13** (★参考项★)
  - 指标两列 (候选 vs 官方板): ★DRC 12/0 · unc 29/45 · 零铜 13/24 · 差分单边零铜 7/11 · 差分Δ超差 2/3 · 走线段 3,986/18,092 · 过孔 593/433 · parity True/False ★
- ★`logs/iss328/34_cont3_readonly_recalc.txt` (★10,429 B @22:13★) ⇒ ★**段内 P/N 顺序翻转逐对读数 (分母 47)** ★
- ★`logs/iss328/08_rightupper_arm.log` (★14,492 B @21:37★) ⇒ ★**臂 vs 基线臂同链终板那一组读数** (★L64~L199★)
- ★`logs/iss328/06_tp_noop_placement_diff.txt` ⇒ ★**TP 钉 vs 不钉 = 落位差异 16 行 (8 个 ref 挪位)** ★
- ★`logs/iss328/04_official_chain_fp_pos_diff.txt` ⇒ ★**官方链补丁链不动落位 (diff = 0)** ★

★**★铁律★**: ★**「unc 45 → 29」不许写成「变好了」** ★ (★段数 3,986 vs 官方终板 18,092 ⇒ 路由器代码已漂移 ⇒ 【同工艺才可比】⇒ 两个数不可直接比★) · ★**B5 里必须写清这条★**

---

## ★★④ B6 自证复现命令 (★只跑这 4 条·只读·每条加 `timeout`★)★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
grep -c '<!-- ' 'HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md'
grep -c iss328 state/fragments/hw.yaml
```

★**★自匹配陷阱 (★必读★)★**: ★**B6 里写的 grep 命令如果原样含 `<!-- ` 这三个字符, 它自己会把这一行也数进去 ⇒ 占位符计数永远不为 0 ⇒ 验收失败★**
★**⇒ B6 里那条 grep 必须写成【打断 PAT 的形式】★**, 例如:

```bash
grep -cE "<!--[ ]" 'HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md'
```

★**★同样的坑在 B0~B5 里也要避开: 正文里出现 `<!-- B2_ACCEPTANCE -->` 这种字面量 ⇒ 会自匹配 ⇒ 用「★`<!--` + `B2_ACCEPTANCE` + `-->` 三段拼写★」或直接写「B2 占位符」★**

★**板的自证期望值 (★抄上去就行·不许改·不许重跑链去凑★)**:
- md5 = `611b869e13518c3c023fb178f91a0075` ★**逐字节不许变** ★
- mtime = `2026-11-06 07:07:17.362193413` ★**逐字节不许变** ★

---

## ★★⑤ 必跑项 (★只许跑一次·加 timeout·★不许跑 `--json` 版·不许反复重跑★)★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
timeout 300 python3 state/gate_check.py; echo "GATE_RC=$?"
```

★**期望**: ★`GATE_RC=0` · ★`【Q1 交付齐备率】 18/18` (★hw-lead 6/6·本单那页 B0~B6 齐了才算齐★) · ★`【Q7 钉板 md5 闸链】 9/9 道绿`★
★**★若 rc≠0: 【不许重跑·不许改闸·不许改别人的页】⇒ 把 rc 与原始输出抄进 B5「未决项」★**

---

## ★★⑥ 绝对禁止 (★违反任一条 = 本单作废★)★★

★**★不许重跑链 / 不许重新生成任何板产物★** ⇒ ★**禁用**: `state/gen_pcb_netlist_board.py` · `state/replay_patch_chain.sh` · `state/clrfix_iter.sh` · `state/gen_pcb_routing.py` · `tmp/iss328/run_ru_arm.sh` · ★**任何 `state/compare_arm_official.py` / `state/compare_arm_baseline.sh` 的重跑 (★读数直接抄 `logs/iss328/` 里已有的★)★**
★**零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` md5/mtime 逐字节不许变★) · ★**零落表** (★网表 / 脚表 / BOM / 原理图源一个字节都不许改★) · ★**零改闸** (★`state/gate_check.py` / `merge.py` / `issue_check.py` / `compare_arm_official.py` / `cmp_pcb_geom.py` 不许改★) · ★**零改生成器代码** · ★**零改既有文档正文** (★含 ISS-325 的 `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` 与本单交付页★) · ★**零改别人的分片** (`state/fragments/sw.yaml` / `mech.yaml` / `pm.yaml`) · ★**零改 `state/issue_log.yaml`** · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ 没有「批一句可以发」这个选项★) · ★**不替老板拍板** (★要拍的写进 B5, 交 main★) · ★**不自称 verified** (★`issue_log` 的 status 由 main 签★)

---

## ★★⑦ 交卷验收 (★main 23:3x 实跑逐条核★)★★

| # | 判据 | 期望 |
|---|---|---|
| 1 | ★`grep -c '<!-- '` 交卷页★ | ★**0** (★用 §④ 的打断 PAT 写法自检★)★ |
| 2 | ★`grep -cE "🔄\|待填\|PLACEHOLDER\|施工中"` 交卷页★ | ★**0** ★ |
| 3 | ★`grep -cE "__[A-Z_]+__"` 交卷页★ | ★**0** ★ |
| 4 | ★`grep -c iss328 state/fragments/hw.yaml`★ | ★**≥ 1** (★现在 7·本单只会改值, 不会变少★)★ |
| 5 | ★`hw.yaml` 的 ISS-328 status 段★ | ★**不再写「后台起链中 / 读数待收」** ★ (★改成最终判决 REJECT 口径★)★ |
| 6 | ★板 md5 / mtime★ | ★`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` ★**逐字节未变** ★ |
| 7 | ★`state/gate_check.py` (★只跑一次★)★ | ★rc=0 (★否则写进 B5·不许重跑★)★ |
| 8 | ★B0~B6 六块齐全 + 交卷页里不含任何占位符★ | ★是 ★ |

★**★交卷时在最后一条消息里回这三行 (★main 直接抄进汇报★)★**:
```
GATE_RC=<你跑出来的数>
PLACEHOLDER_COUNT=<交卷页 grep 结果>
FRAG_ISS328_HITS=<hw.yaml grep 结果>
```

---

## ★★⑧ 本单的边界声明 (★交卷页 B5 里必须原样带上★)★★

★**这是「板只改一次」纪律下的【纯分析/作业包类】活**: ★**本单一个字节都没动板, 没动网表真源, 没动闸** ★ ⇒ ★**板那一趟 (S1~S13) 的开工条件仍未满足** ★ (★老板 2026-11-17 00:43 口径: 真动板那一趟必须一次做完★) ★
★**本单只是把右上臂这条【已证伪的处方】的读数【如实落纸 + 登记】, 供 main 拿去写「板那一趟」作业包的不做清单** ★
