# ISS-284 · SW 侧 `hard_protected` 合法改板机制 (★P10 = 方案 ②★) — 交卷单

> ★**owner**: sw-lead (软件总工) · ★**派活人**: 项目总工 (main / moli) · ★**verify_by**: main
> ★**单号**: ISS-284 · ★**零外发** · ★**本单性质**: ★**内部活 · 门禁/台账机制侧** ★
> ★**落点**: `SW/SW_MD5_BASELINE_LEDGER.md` §1 (机制段 + 锚点字段) + §3 (追加留痕行) + `SW/tools/check_demo_panel_spec.py` 的 R6 判据
> ★**上游**: **ISS-279** (sw-lead 出设计 + 三方案) ⇒ ★**老板 2026-11-17 09:49 拍板「按照你的建议执行」⇒ P10 = 方案 ②** ★
> ★**交卷时刻**: 2026-11-17 10:3x (Asia/Shanghai) · ★**本单一个 md5 都没改** (★只改机制★)

---

## 0 一句话结论

★★**SW 侧现在有路了**: 板 / `.kicad_pro` 这两件硬保护件, ★**合法改板 = 一次由单号背书的显式动作** ★
⇒ ★**锚点写一条【四项捆在一起的原子记录】(单号 + 文件名 + 改前 md5 + 改后 md5) + 落表台账里有一行同四项 ⇒ R6 绿** ★
⇒ ★**「只改 md5 凑绿」这条路被彻底堵死** (★基线必须在台账里查得到 + 基线必须留在链尾★) ★
⇒ ★**判据方向一个字没变** (★盘上 ≠ 台账链头 ⇒ 红★) · ★**fail-closed 三条一条没动** (★链头不唯一 / 链断 / 链头无单号 ⇒ 红★) ★

---

## 0bis 交付物清单 (4 件 · 全部在盘)

| # | 交付物 | 落点 | md5 / 证据 |
|---|---|---|---|
| 1 | 交卷单 | `HANDOFF/2026-11-17_sw-lead_ISS284_hard_protected合法改板机制.md` | 本文件 |
| 2 | 台账机制段 + 留痕行 | `SW/SW_MD5_BASELINE_LEDGER.md` §1 (锚点 `reboard` 字段 + 机制十条) + §3 (R-12) | `c5484ec677ebd52ad4ff87ab520ec77b` |
| 3 | 闸改动 + 反向用例 | `SW/tools/check_demo_panel_spec.py` (`check_r6_hard_protected()` + 4 个 helper + REV-16~REV-21) | `4e8f9aeaf45f95e120421d29bdaa333c` |
| 4 | 分片 | `state/fragments/sw.yaml` (走 `state/frag_write.py --agent sw-lead` 原子写) | 4 artifact + 1 claim + 1 answer + 1 need |

★**原始日志目录**: `logs/iss284/` (8 份, 见 §B6) ★

---

## B1 机制设计 (★四条要求逐条对账★)

### B1-1 · 需求对账

| 任务书要求 (B1) | 本单怎么满足 | 机器证据 |
|---|---|---|
| ① **一个字段两个值** (不许两个可各自独立编辑的字段) · 四件捆在一起 · 台账里查得到 | 锚点 `hard_protected[].reboard` = ★**一个原子映射**★, 内含 `by` / `file` / `prev_md5` / `md5` 四项 (★四项缺一 ⇒ 整条记录无效 ⇒ 红★); 同一份四项必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的**同一行**里查到 | `check_r6_hard_protected()` 判据 ③-1; REV-16 / REV-17 |
| ② **R6 判据方向不许变** (盘上 ≠ 链头 ⇒ 红 · 合法改板只让链头前移) | 硬保护段与网表/脚表**同源**: 判决源 = 落表台账**链头**; 盘上 md5 ≠ 链头 ⇒ 红 | 判据 ③-2; REV-19; §B2 ③ |
| ③ **fail-closed 三条一条不许动** (链头不唯一 / 链断 / 链头无单号 ⇒ 红) | 三条逐条实现, ★**一条都没放宽★**; 外加「取不准一律判红」 | 判据 ③ (head/chain/head_iss) + REV-18 / REV-19 |
| ④ **不许动网表/脚表那条已跑通的链头逻辑 (ISS-275) ⇒ 改完读数逐字相同** | 网表/脚表分支**代码一字未动** (只把 `sw_ledger_state()` 加了一个可选参数 `recs`, 默认值 = 原路径 ⇒ 行为不变) | ★**`IDENTICAL: True`** (老/新两版脚本算出的链头/链/产出单号/记录表逐字相同★) ⇒ §B3 ⑥ |

### B1-2 · 数据形状 (★锚点 §1 现状★)

```yaml
  hard_protected:                   # ★ 落表明令不许碰的 2 个 (板 / .kicad_pro) ⇒ 纯 md5 硬保护, 不走台账
    # ★★【ISS-284 · 2026-11-17 · sw-lead】★★ 合法改板机制 (★P10 = 方案 ②★):
    #   ★ `md5` = 【保护基线】(受保护那一刻的值) ⇒ ★永远不许改★
    #   ★ `reboard` = 【一条合法改板记录】= 单号 by + 文件名 file + 改前 md5 prev_md5 + 改后 md5 md5
    #     ★四件捆在【一个原子映射】里 ★
    #   ★ `reboard: null` = 还没发生过合法改板 ⇒ 纯 md5 硬保护 (★盘上 ≠ 基线 ⇒ 红★)
    - file: HW/PCB/demo_mainboard.kicad_pcb
      md5: 611b869e13518c3c023fb178f91a0075
      reboard: null
    - file: HW/PCB/demo_mainboard.kicad_pro
      md5: 3e504d2be83152e337949723e909be1b
      reboard: null
```

★**为什么 `md5` 字段保留而不是改写成新值** ★:
★**「保护基线」是 append-only 的事实 (受保护那一刻的值), 改它 = 改历史** ★ ⇒ ★**合法改板的新值只出现在 `reboard.md5` 里 (且必须与台账链头一致)** ★
⇒ ★**好处 (★实测★)**: ★**`SW/tools/check_onepass_sw_sync.py` 的 W6「台账 §1 锚点块两个 md5 未被手改」这条守卫不用改一个字就继续有效** ★ (★它正则是 `file:` 后面紧跟 `md5:` ⇒ 我把 `reboard:` 加在 `md5:` 后面 ⇒ 不破★)

### B1-3 · 闸怎么读 (★判据逐条★)

★**判决源**: 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★只读★) ⇒ ★**硬保护件第一次有了「链头」概念** ★

| 序 | 判据 | 红了说明 |
|---|---|---|
| ① | ★**保护基线自证**: 锚点里的基线 md5 必须在落表台账里与该文件**同行**查到 ★ | ★**锚点被单独改了 (只改 md5 不落表 = 悄悄换真源)** ★ |
| ② | ★**台账里没有变更行** ⇒ 不许有 `reboard` 记录; 且盘上 md5 必须 == 基线 ★ | ★**纯 md5 硬保护仍在** ★ |
| ③ | ★**台账里有变更行** ⇒ ★**链头唯一 / 链不断 / 链头有单号** 三条 fail-closed 一条不许动 ★ | ★**取不准 ⇒ 判红** ★ |
| ③-1 | ★**锚点必须带 `reboard` 原子记录, 四项缺一 ⇒ 红**; 且四项必须与台账链头**逐字**对上 (文件名 / 改后 md5 / 改前 md5 / 单号) ★ | ★**单号与 md5 不许各自独立编辑** ★ |
| ③-2 | ★**保护基线必须留在台账链的链尾** ★ | ★**基线被偷偷前移 (想「让盘上 == 基线」凑绿)** ★ |
| ③-3 | ★**盘上 md5 必须 == 台账链头** ★ | ★**真源被换了或台账没更新 (★判据方向没变★)** ★ |
| ④ | ★**同组受保护件成对覆盖**: 板 + `.kicad_pro` 必须被**同一单号**覆盖 ★ | ★**只改板不动 `.kicad_pro` (两件记录只来一条) ⇒ 红** ★ |

★**【信任边界】 (★必须写清, 不许含糊★)**: ★**落表台账 = append-only 的信任边界** (★改台账 = 改历史 = 越权★) ⇒ ★**本闸保证的是【锚点自己不能说了算】**: 锚点里每一个 md5 都必须在台账里查得到 ★ ⇒ ★**「悄悄换台账」不在本闸能力范围内** (★与本表 §1 ISS-275 那条声明同口径★) ★

★**【歧义行的处理】**: ★**一行两件两值** (★一行里同时写了板与 `.kicad_pro` 的两个 md5★) ⇒ ★**不算变更行** ★ ⇒ ★**这是 fail-closed 方向** (★宁可当「没记过」也不当「记过」★) ⇒ ★**实测**: 落表台账 L114 那行 (★板与 `.kicad_pro` 两个 md5 同行★) **不**被误判成「板改过」★

### B1-4 · 落表台账那一行长什么样 (★给 main 的接口格式★)

★**格式契约 (与本表 §1 ⑧ 同一条)**: ★**一行 = 「单号 | 文件名 | 改前 md5 | 改后 md5」四项同行** ★

```
| ISS-XXX | `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `<新板 md5>` | ★**是 (合法改板·板只改一次)** ★ |
| ISS-XXX | `HW/PCB/demo_mainboard.kicad_pro`   | `3e504d2be83152e337949723e909be1b` | `<新 .kicad_pro md5>` | ★**否 (逐字节不变)** ★ |
```

★**★真落那一行留给「出板那一趟」的 main** ★ (★本单 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 一个字节没碰★ md5 `93c1328a9f1f257ac99781d308941979` · mtime 09:58:16 = 上游落表时刻, 早于本单开工 10:18★)
⇒ ★**SW 侧锚点 `hard_protected[].reboard` 要填同一单号的四项** ⇒ ★**填完 R6 即绿** ★

---

## B2 反向用例 (★六条 · 期望红组 vs 实际红组 · 原样 rc★)

★**跑法**: `python3 logs/iss284/run_cases_detail.py` (★在临时树上跑, 真盘一个字节不碰★) ⇒ 原样日志 `logs/iss284/reverse_cases_detail.log` ★
★**六条用例全部与期望一致: 6/6** ★

| # | 构造 | 期望红组 | ★**实际红组 (原样)** ★ | rc |
|---|---|---|---|---|
| ① | ★**只改了 `hard_protected` 里的板 md5, 单号字段没写 / 是空的** ★ | `R6 硬保护: 保护基线 md5 在落表台账里查不到 ⇒ 锚点被单独改了` | `R6 硬保护: HW/PCB/demo_mainboard.kicad_pcb 的保护基线 md5 391f56805c70 在落表台账 (HW/SCHEMATIC_LANDING_V1_LANDED.md) 里查不到 ⇒ 锚点被单独改了 (★只改 md5 不落表 = 悄悄换真源 = 红★)` | **1** |
| ② | ★**单号写了, 但台账里查不到那一行** ★ | `R6 硬保护: 锚点里有合法改板记录 (reboard) 但落表台账里查不到任何变更行` | `R6 硬保护: HW/PCB/demo_mainboard.kicad_pcb 锚点里有合法改板记录 (reboard) 但落表台账里查不到任何变更行 ⇒ 单号背书落不了地 = 红` ＋ `R6 硬保护: 受保护文件 md5 变了: HW/PCB/demo_mainboard.kicad_pcb (391f56805c70… ≠ 611b869e…)` | **1** |
| ③ | ★**台账里有两条合法改板记录指向同一个文件 (链头不唯一)** ★ | `R6 硬保护: 台账最新记录取不准 (链头不唯一)` | `R6 硬保护: HW/PCB/demo_mainboard.kicad_pcb 台账最新记录取不准 (链头不唯一 = ['391f56805c70', 'deadbeefdead'] (取不准 ⇒ 不许判绿)) ⇒ 取错记录可能假绿 ⇒ 判红` | **1** |
| ④ | ★**链断 (改前 md5 对不上台账记的上一次改后 md5)** ★ | `R6 硬保护: reboard 改前 md5 与台账链头那一行的改前不一致 (链断)` | `R6 硬保护: HW/PCB/demo_mainboard.kicad_pcb 的 reboard 改前 md5 611b869e1351 与台账链头那一行的改前 0123456789ab 不一致 (链断) ⇒ 判红` | **1** |
| ⑤ | ★**只改板不动 `.kicad_pro` (⇒ 两件的记录只来一条)** ★ | `R6 硬保护: .kicad_pro 没有被同一次合法改板覆盖 (记录只来一条)` | `R6 硬保护: HW/PCB/demo_mainboard.kicad_pro 没有被同一次合法改板 (ISS-9901) 覆盖 (记录只来一条 ⇒ 判红)` | **1** |
| ⑥ | ★**台账里四项齐全且与盘上现值一致 ⇒ 放行 (★正向用例★)** ★ | `{}` (★必须绿★) | ★**(空) — R6 全部失败项 0 条** ★ | **0** |

★**★六条全部在 `--selftest` 里跑 (★REV-16~REV-21★) ⇒ `SELFTEST 22/22 通过` (★原 16 条一条没删, 条数只增不减★)** ★

★**★「合法改板」长什么样 (★正向用例 REV-21 的实际形状★)**: ★**① 板文件改了 ⇒ 新 md5 `391f56805c70…`; ② 锚点 `reboard` = {by: ISS-9901, file: HW/PCB/demo_mainboard.kicad_pcb, prev_md5: 611b869e…, md5: 391f5680…}; ③ 落表台账里两行 (板一行变更 + `.kicad_pro` 一行「逐字节不变」, 同一单号) ⇒ R6 绿** ★

---

## B3 回归 (★本机实跑 · 原样 rc★)

| # | 命令 | ★期望★ | ★**实跑 rc** ★ | 判定 |
|---|---|---|---|---|
| ① | `python3 SW/tools/check_demo_panel_spec.py` | rc=0 (R1~R7 全过) | **rc=0** | ✅ |
| ② | `python3 SW/tools/check_demo_panel_spec.py --selftest` | rc=0 (★条数只许增不许减★) | **rc=0 · SELFTEST 22/22** (原 16 → 22) | ✅ |
| ③ | `python3 SW/tools/timing_check.py` | rc=0 (SELFTEST 71/71) | ★**rc=1 · 68/71** ★ | ⚠️ ★**与本单无关, A/B 实测证明 (见下)** ★ |
| ④ | `python3 HW/check_step1_parts_spec.py` | rc=0 | **rc=0 · 8/8 通过** | ✅ |
| ⑤ | `python3 HW/check_onepass_preflight_coverage.py` | rc=0 | ★**rc=1** ★ | ⚠️ ★**与本单无关 (上游落表造成, 见下)** ★ |
| ⑥ | `python3 state/merge.py && python3 state/gate_check.py` | rc=0 / rc=0 | **rc=0 / rc=0 (Q1 18/18)** | ✅ |
| ⑦ | ★**网表/脚表链头读数前后比对 (ISS-275 成果不许动)** ★ | 逐字相同 | ★**IDENTICAL: True** ★ | ✅ |
| ⑧ | `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` | ★五件逐字节不变★ | ★**板 `611b869e…` / `.kicad_pro` `3e504d2b…` 逐字节不变** ★ (★网表/脚表/BOM 是 09:58 上游落表改的, 早于本单开工 10:18★) | ✅ |

★**③ ⑤ 两条红的归因 (★不甩锅, 摆证据★)** ★:
★**根因 = 2026-11-17 09:58:15 hw-lead 的上游落表改了 `HW/netlist_v1.csv` / `_pins.csv` / `BOM_v1.csv`** (★mtime 09:58:15/09:58:15/09:58:15 ⇒ **早于本单开工 10:18**★)
⇒ ★**那些闸里登记的基线 (网表 `e06c1dd6…` / 脚表 `287e7861…` / BOM `94642d07…`) 是落表前的旧值 ⇒ 恒红** ★
⇒ ★**★A/B 实测 (★决定性证据★)**: 把本单改过的台账**换回改动前的版本** (★脚本自动反向生成, md5 `…` 与原文件逐字一致★) 再跑 `timing_check.py` ⇒ ★**仍是 68/71 · rc=1 · 同样那 3 条红** ★ (★日志 `logs/iss284/ab_timing_check_pre_ledger.log`★) ⇒ ★**证明这 3 条红不是本单弄坏的** ★
⇒ ★**且 `timing_check.py` 只读本单改过的两个文件里的一个 (台账), 只取 `source_ledger.entries[]` 段 —— 本单对那一段一个字没动** ★

★**⑦ 「读数逐字相同」的证明口径** ★: `logs/iss284/probe_netlist_reading.py` 用同一棵盘、同一份落表台账, 分别加载★**改前** (备份 `d8248eca21a2d0cead8a4da4fce3c24f`) 与★**改后** (`4e8f9aeaf45f95e120421d29bdaa333c`) 两版脚本, 各自算出网表/脚表的 ★**链头 / 链 / 产出单号表 / 全部落表记录**★ ⇒ ★**两份 JSON 逐字相同 ⇒ `IDENTICAL: True`** ★ (★网表链头 `2f17650cfbef` / 脚表链头 `6ea65fecdf95`, 两版一致★) ★

★**★本单的净效果**: ★**SW 侧 R1~R7 全绿 + 自证用例由 16 条增到 22 条且全过; 本单没引入任何新的红** ★

---

## B4 边界自查 (★逐条对账★)

| 边界 | 自查结果 (★本机实测★) |
|---|---|
| ★**零写板** ★ | ✅ 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pro` `3e504d2be83152e337949723e909be1b` **交卷前后逐字节不变** (★mtime 仍是 2026-11-06 07:07:17 / 2026-11-04 23:47:30★) |
| ★**零落表 (网表/脚表/BOM 一个字节不许动)** ★ | ✅ 本单**没写过** `HW/` 下任何文件 (★selftest 里改板是在**临时树**里做, 且★**先把硬链接换成真拷贝再改** ⇒ 真盘那一份 inode 一个字节不受影响★) |
| ★**落表台账零写入** ★ | ✅ `HW/SCHEMATIC_LANDING_V1_LANDED.md` md5 `93c1328a9f1f257ac99781d308941979` · mtime **09:58:16** (= 上游落表时刻, **早于本单开工**) |
| ★**不许改 `HW/` / `MECH/` 的文件与分片** ★ | ✅ 本单只写: `SW/tools/check_demo_panel_spec.py` · `SW/SW_MD5_BASELINE_LEDGER.md` · 本交卷单 · `logs/iss284/*` · `state/fragments/sw.yaml` (★走 `state/frag_write.py --agent sw-lead` 原子写★) |
| ★**不许动 ISS-275 那条已跑通的链头逻辑** ★ | ✅ ★**读数逐字相同 (`IDENTICAL: True`)** ★ (★网表/脚表分支代码一字未动★) |
| ★**不许放宽 fail-closed 三条** ★ | ✅ 链头不唯一 / 链断 / 链头无单号 三条逐条实现, ★**REV-18 / REV-19 两条用例当场证明它们还是红的** ★ |
| ★**零外发** ★ | ✅ 本单**未发任何邮件 / 询价 / 问询 / 采购** ⇒ ★**实物 [实测] = 0 条** (★板与屏不在本机★) ⇒ ★**凡是标 [实测] 的, 一律是「本机脚本 / 本机文件实读」★ ★ |
| ★**不替老板拍板** ★ | ✅ 老板 2026-11-17 09:49 已拍板 P10 = 方案 ② ⇒ 本单**只把那个拍板落成机制与闸**, ★**没有任何新拍板** ★ (★「板只改一次」那一趟的排期与那一行的真值 ⇒ 归 main★) |
| ★**不自签 issue_log** ★ | ✅ `state/issue_log.yaml` **本单零写入** (★status 留给 main 落 verified★) |
| ★**不许把整份大文件读进来 (只 grep 要改的那几行)** ★ | ✅ 本单只读了 `check_demo_panel_spec.py` 的相关段 (L130~L240 / L331~L440 / L441~L610 / L605~L960) 与台账的 §1/§3 段, ★**没有把整份 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (1296 行) 或板文件读进来** ★ |
| ★**分片写完 `grep` 校验自己的 key 在不在** ★ | ✅ `sw_hard_protected_legal_reboard_mechanism` / `sw_legal_reboard_landing_row_on_board_trip` / `ISS284_hard_protected合法改板机制` / `sw_hard_protected_reanchor_options` 四处 **grep 命中** ✓ |

★**★并发声明 (★诚实标出, 不是我干的★)** ★:
★**2026-11-17 09:58:15 hw-lead 落了一批网表/脚表/BOM ⇒ 网表 md5 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…` (★不是本单改的★) ⇒ §B3 ③⑤ 那两条闸的红由它引起, 与本单无关 (★A/B 实测证明★)** ★
★**另: 本单开工期间 (10:18~10:4x) `state/` / `HW/check_fsin_rootcause.py` / `HW/PCB/{STACKUP,LAYOUT_RULES}.md` / `docs/` 等有别的会话在写 —— ★本单没碰这些★** ★

---

## B5 未决 / 给 main (★不替老板拍板★)

### B5-1 ★给 main 的 need (已写进分片): 出板那一趟要落的那一行 ★
★**key = `sw_legal_reboard_landing_row_on_board_trip`** ⇒ ★**出板那一趟请在 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里写两行** (★格式: 单号 | 文件名 | 改前 md5 | 改后 md5 四项同行★):
① 板那一行 = 「出板单号 | `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | <新板 md5>」
② `.kicad_pro` 那一行 = 「出板单号 | `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | <新 .kicad_pro md5>」
(★若 `.kicad_pro` 真的逐字节没变, ★**改前=改后也要写一行「否 (逐字节不变)」**★ ⇒ ★**两件必须成对, 只来一条 = 红**★)
★**同时 SW 侧锚点 `hard_protected[].reboard` 要填同一单号的四项** ⇒ ★**填完 R6 即绿** ★

### B5-2 ★本单没解决的 (★归别人, 不留成外部依赖★) ★
| 项 | 现状 | 归谁 |
|---|---|---|
| ★**落表台账里板那一行的真值** ★ | ★**本单零落表** ⇒ 那两行**还没落** (★闸现在是绿的, 因为还没改板★) ★ | ★**main (出板那一趟)** ★ |
| ★**`timing_check.py` 的两条网表锚点断言仍按 ISS-225 口径 (只认「落表前/落表后」两个状态)** ★ | ★**09:58 那批落表后恒红 (68/71)** ⇒ ★**不是本单弄坏的 (A/B 已证)** ★ ⇒ ★**修法 = 把它们也换成【台账链头】口径 (与 ISS-275 同构)** ★ | ★**main 派单 (★sw-lead 建议下轮做·本单不改·理由: 改了会动 `timing_check.py` 的判据口径, 不在本单任务书落点内★)** ★ |
| ★**`HW/check_onepass_preflight_coverage.py` 的 P5/P6** ★ | ★**P6 的三条基线 (网表/脚表/BOM) 是 08:01 记的旧值 ⇒ 09:58 落表后恒红** ★ | ★**hw-lead / main (★重记基线★)** ★ |
| ★**「悄悄换台账」** ★ | ★**不在本闸能力范围内** (★落表台账 = append-only 的信任边界★) ⇒ ★**本闸保证的是「锚点自己不能说了算」** ★ | ★**制度层 (★main 立口径★)** ★ |

### B5-3 ★给老板的一句话 (★不代拍★) ★
★**机制侧已经闭环 (★合法改板有路且有闸★) ⇒ 剩下唯一需要人拍的是: 「出板那一趟」什么时候走、那一行由谁落** ★ ⇒ ★**本单不催、不代排 (★排期归 main★)** ★

---

## B6 复现命令 (★全部本机可跑★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 主闸
python3 SW/tools/check_demo_panel_spec.py            # rc=0 (R1~R7 全过)
python3 SW/tools/check_demo_panel_spec.py --selftest  # rc=0 (SELFTEST 22/22)

# ② 六条反向/正向用例的【原样 rc + 期望红组 vs 实际红组】
python3 logs/iss284/run_cases_detail.py               # rc=0 (六条用例: 6/6 与期望一致)
cat logs/iss284/reverse_cases_detail.log

# ③ ★「网表/脚表链头读数前后逐字相同」的证明 (ISS-275 成果不许动)
python3 logs/iss284/probe_netlist_reading.py \
        logs/iss284/check_demo_panel_spec.pre_iss284.py SW/tools/check_demo_panel_spec.py . \
        | grep IDENTICAL                          # ⇒ IDENTICAL: True
cat logs/iss284/netlist_reading_before_after.log

# ④ 其它闸
python3 SW/tools/timing_check.py                     # rc=1 68/71 (★09:58 上游落表造成, 见 B3★)
python3 HW/check_step1_parts_spec.py                 # rc=0 (8/8)
python3 HW/check_onepass_preflight_coverage.py       # rc=1 (★上游落表造成, 见 B3★)
python3 state/merge.py && python3 state/gate_check.py  # rc=0 / rc=0 (Q1 18/18)

# ⑤ 受保护 5 件 + 落表台账 (★板/.kicad_pro 逐字节不变★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/SCHEMATIC_LANDING_V1_LANDED.md
```

★**★原始日志 8 份 (`logs/iss284/`)**: `gates_demo_panel.log` · `gates_timing_check.log` · `gates_step1.log` · `gates_onepass_preflight.log` · `gates_onepass_sw_sync.log` · `gates_merge.log` · `gates_gate_check.log` · `netlist_reading_before_after.log` · `ab_timing_check_pre_ledger.log` · `reverse_cases_detail.log` (+ 3 个工具脚本) ★
★**★老版脚本快照也落盘了** (`logs/iss284/check_demo_panel_spec.pre_iss284.py`, md5 `d8248eca21a2d0cead8a4da4fce3c24f`) ⇒ ★**§B3 ⑦ 的「读数逐字相同」证明随时可复跑, 不依赖 /tmp★** ★

---

## B7 交卷物 md5 指纹 (★交卷时刻★)

```
4e8f9aeaf45f95e120421d29bdaa333c  SW/tools/check_demo_panel_spec.py     (改前 d8248eca21a2d0cead8a4da4fce3c24f)
c5484ec677ebd52ad4ff87ab520ec77b  SW/SW_MD5_BASELINE_LEDGER.md         (改前 82ed57873d217b76e013e4181bbe41e7)
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb       (★未动★)
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro      (★未动★)
93c1328a9f1f257ac99781d308941979  HW/SCHEMATIC_LANDING_V1_LANDED.md    (★未动★)
```

★**★一句话给 main**: ★**SW 侧 R6 现在认「合法改板」了 —— 但★**它只认由单号背书、台账查得到、且基线不许动的合法改板**★; 出板那一趟请按 §B5-1 的两行格式落表台账, SW 侧即刻绿。** ★**零写板 · 零落表 · 不替老板拍板 · issue_log 未自签** ★
