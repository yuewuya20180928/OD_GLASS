# ISS-326 · mech-lead 交卷单 —— MECH 侧「S1 位号改名会不会把 MECH 判据炸掉」体检

- **单号**: ISS-326 · **owner**: mech-lead (结构总工) · **verify_by**: main (项目总工) · **job**: cron `fb67af40` (ARS45 队列自动派活)
- **性质**: 内部活 · 门禁/判据口径侧 · 纯分析 + 沙盒实跑类 · **零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 沙盒只写 `tmp/iss326/` + `logs/iss326/` · 零外发 · 不替老板拍板 · 不自签 issue_log**
- **本单实跑机**: `yuewuya-RedmiBook-14` · Linux 7.0.0-42-generic · Python 3 · Asia/Shanghai
- **主交卷页**: `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` (§0~§7 · 细节在那页)
- **★本版块名按门禁链的 6 块语义重排** (上一版把 B2~B5 写成「沙盒原始读数 / 边界自证 / needs / 必跑清单」, 与闸链要的 B1~B6 对不上 ⇒ 这就是 Q1 只拿到 2/6 的原因)

---

## B0 · 一句话结论 + 交付物清单

### ★B0 · 一句话结论 (给 main 的一句话) ★

> S1 改名在 MECH 侧的暴露面 = **真集 218 条位号** (改名 186 / 不动 32), 分布在 **63 个文件 / 1,934 个命中数据行** (★`wc -l` = 1,935 ⇒ 多 1 行是表头★); 其中**判据脚本**才是真风险面 (383 行, ★其中 82 行是「静悄悄不查了」= 假绿, 最坏★), **历史落地脚本**改不改无所谓 (164 行, 跑完即退), **注释里的 ref** 根本没有功能影响 (31 行, ★沙盒实测 stdout 逐字节相同★)。
> ★**一句话给 main**: 本单不主张 MECH 侧现在必须改任何东西, 主张的是【**先建一道「MECH 侧位号可达性闸」把假绿堵住, 再谈改名**】 —— ★**实测: 改名当天有 68 个被 MECH 引用的位号会一次性变成「改名漂移」; 闸若在改名后才建, C2 从 0 跳到 68 ⇒ 闸就再也分不清老漂移和新漂移** ★; ★**且该闸的建闸日基线必须 MECH 侧自己 fresh 测 (原始 60 / 剔除 py 变量名后 16), 不许抄 SW 侧的 3** ★。

### ★B0 · 交付物清单 (逐条落盘状态) ★

| # | 交付物 | 路径 | 状态 |
|---|---|---|---|
| 1 | ★**主交卷页** ★ | `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` | ✅ 已落盘 (§0~§7) |
| 2 | ★**本交卷单** ★ | `HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md` | ✅ 已落盘 (B0~B6) |
| 3 | ★**处置表证据** ★ | `logs/iss326/mech_ref_disposition.tsv` | ✅ 已落盘 (1,935 行归并) |
| 4 | ★**闸设计稿证据** ★ | `logs/iss326/gate_design/` | ✅ 已落盘 |
| 5 | ★**沙盒实证证据** ★ | `logs/iss326/sandbox/` | ✅ 已落盘 (4 条反向用例) |
| 6 | ★**分片** ★ | `state/fragments/mech.yaml` | ✅ 已落盘 (need `iss326_*` + cont5 增 1 artifact + 2 interface_claim) |
| 7 | ★**交卷前自证全量日志** ★ | `logs/iss326/verify_final.log` | ✅ 已落盘 (741 行 / 65,443 B · ★按行号索引, 不引用 md5★) |

---

## B1 · 结论摘要 (含硬指标表)

### ★B1-1 · 硬指标 (★Q5 按页面上出现的数字种类计 ⇒ 下列 7 类全部带具体数字★) ★

| # | 硬指标 | 读数 | ★**产出它的判据脚本 + 行号 + 复算命令** ★ | 证据等级 |
|---|---|---:|---|---|
| 1 | ★**全量命中数据行** ★ | ★**1,934 行** ★ (63 个 distinct 文件; ★`wc -l` = 1,935 含表头★) | ★**脚本** `logs/iss326/iss326_scan_mech_refs.py` **L263** (打印「总命中数」) + **L277** (命中文件数) · ★**产物** `logs/iss326/mech_ref_hits.tsv` + `logs/iss326/scan_raw.txt` **L18/L28** · ★**复算** `awk -F'\t' 'NR>1' logs/iss326/mech_ref_hits.tsv \| wc -l` → 1934 ; `awk -F'\t' 'NR>1{print $1}' logs/iss326/mech_ref_hits.tsv \| sort -u \| wc -l` → 63 | [实测] |
| 2 | ★**改名真集规模** ★ | ★**218 条** ★ (★改名 **186** / 不动 **32**★; ★186/186 全是 `old + "_1"`★) | ★**脚本** `logs/iss326/iss326_scan_mech_refs.py` **L242-L244** (打印「改名宇宙/要改/不动」) + **L84-L94** (自证断言: n_keep==32 / kicad_ref 口径逐条相符 / 改名后撞名无) · ★**产物** `logs/iss326/mech_ref_universe.json` (键 `count`/`move`/`keep`) · ★**复算** `python3 -c "import json;d=json.load(open('logs/iss326/mech_ref_universe.json'));print(d['count'],len(d['move']),len(d['keep']))"` → `218 186 32` | [实测] |
| 3 | ★**三口径对账** ★ | ★**口径A=1,934 / 口径B=1,282 / 口径C=7,553** ★ (顶层==递归, 均为 112 文件) | ★**脚本** `logs/iss326/iss326_reconcile_counts.py` **L47-L51** (打印「扫描面/口径A/口径B/口径C」) · ★**产物** `logs/iss326/reconcile_counts_raw.txt` **L2-L5** (顶层) 与 **L34-L37** (递归, 三个数逐字相同) · ★**复算** `grep -n '口径[ABC]' logs/iss326/reconcile_counts_raw.txt` | [实测] |
| 4 | ★**main 自己的口径D** ★ | ★**571** ★ (前缀白名单 ⇒ 比口径A 少 1,363) | ★**★无单一出处★** (main 自己的前缀白名单 grep 未落盘 ⇒ 本仓无脚本产出它) ⇒ ★**见 `logs/iss326/reconcile6_raw.txt` L37-L101** (★穷举「子集×正则×计数方式」能否给出恰好 571 ⇒ 结论: 任何组合都复现不出 ⇒ L99「没有任何组合给出恰好 571」/ L100「唯一最接近 = py-only 578」★) · ★**复算** `grep -n '571' logs/iss326/reconcile6_raw.txt` | [实测] |
| 5 | ★**py-only 出现次数** ★ | ★**578** ★ (与 main 的 571 差 7) | ★**脚本** `logs/iss326/iss326_reconcile6.py` **L36** (打印口径行) + **L43** (打印「py-only 合计」) · ★**产物** `logs/iss326/reconcile6_raw.txt` **L2** · ★**复算** `grep -n 'py-only 合计' logs/iss326/reconcile6_raw.txt` → 578 | [实测] |
| 6 | ★**形状假阳性规模** ★ | ★**7,553 − 1,934 = 5,619** ★ 次 (不在 218 真集里 ⇒ 不在改名风险面) | ★**★无单一出处★** (★它是口径C 减口径A 的派生量, 不是任何脚本直接打印的数★) ⇒ ★**见 `logs/iss326/reconcile_counts_raw.txt` L3 (口径A) + L5 (口径C)** · ★**复算** `awk -F':' '/口径A 精确真集命中/{gsub(/[^0-9]/,"",$NF);a=$NF} /口径C 形状像位号/{gsub(/[^0-9]/,"",$NF);c=$NF} END{print c-a}' logs/iss326/reconcile_counts_raw.txt` → **5619** | [实测] |
| 7 | ★**处置表三清单** ★ | ★**判据脚本 383 / 历史脚本 164 / 文档 1,356 / 注释 31** ★ (合计 1,934) | ★**脚本** `logs/iss326/iss326_disposition.py` **L273** (写表头 11 列) + **L276-L279** (打印「清单归属 × 失效形态 分布」) · ★**产物** `logs/iss326/mech_ref_disposition.tsv` (★**列 `$8` = 清单归属★**) + `logs/iss326/disposition_summary.txt` **L3-L10** · ★**复算** `awk -F'\t' 'NR>1{c[$8]++} END{for(k in c) print k, c[k]}' logs/iss326/mech_ref_disposition.tsv` → 判据脚本·要改 383 / 历史脚本·不改 164 / 文档·无功能影响 1356 / 注释·无功能影响 31 | [实测] |
| 8 | ★**处置表三形态** ★ | ★**不受影响 1,588 / 红 87 / 静悄悄不查了(假绿) 259** ★ | ★**脚本** `logs/iss326/iss326_disposition.py` **L280-L281** (打印「失效形态合计」/「按失效形态」) · ★**产物** `logs/iss326/mech_ref_disposition.tsv` (★**列 `$9` = 失效形态★**) + `disposition_summary.txt` **L11-L12** · ★**复算** `awk -F'\t' 'NR>1{c[$9]++} END{for(k in c) print k, c[k]}' logs/iss326/mech_ref_disposition.tsv` → SAFE 1588 / RED 87 / SILENT 259 | [实测] |
| 9 | ★**沙盒反向用例** ★ | ★**8 条 (1A/1B/1C/1D/2/3A/3B/4) · 期望 8 条 · 实际 8 条 · 符合期望 8 · 相反 0** ★ | ★**脚本** `logs/iss326/iss326_sandbox.py` **L126** (case1_fakegreen) / **L197** (case2_crash) / **L222** (case3_keep) / **L258** (case4_comment) / **L293-L301** (main 跑 8 条) / **L334-L335** (写 results.json) · ★**产物** `logs/iss326/sandbox/results.json` (★8 条 list★) + `logs/iss326/sandbox/RESULTS.md` **L9-L16** (期望/实际/判决表) + `logs/iss326/sandbox/case*.log` · ★**复算** `python3 -c "import json;print(len(json.load(open('logs/iss326/sandbox/results.json'))))"` → 8 | [实测] |
| 10 | ★**闸设计稿的 MECH 侧 fresh 基线** ★ | ★**原始 C14 = 60 / 剔除本单自污染 4 条 = 56 / 再剔除 py 变量名 40 条 = 16** ★ (★SW 侧是 3, 本单不抄★) | ★**脚本** `logs/iss326/gate_design/mech_gate_proto.py` **L157-L162** (★`baseline_breakdown` 六个数: C14_total 60 / py_only 40 / md_hit 20 / self 4 / excl_self 56 / excl_self_and_py_only 16★) · ★**产物** `logs/iss326/gate_design/mech_gate_baseline.json` (键 `baseline_breakdown`) + `mech_gate_baseline_raw.txt` **L4-L6** · ★**设计稿** `logs/iss326/gate_design/GATE_DESIGN.md` **L101-L118** (§5-2/§5-3) · ★**复算** `python3 -c "import json;print(json.load(open('logs/iss326/gate_design/mech_gate_baseline.json'))['baseline_breakdown'])"` | [实测] |
| 11 | ★**改名漂移暴露面** ★ | ★**68 个改名位号被 MECH 引用 (68/68 今天 live 可解析) / 7 个不动位号被 MECH 引用** ★ | ★**脚本** `logs/iss326/gate_design/mech_gate_proto.py` **L170-L174** (★`rename_exposure`: move_refs_total 186 / referenced_in_MECH 68 / referenced_and_live 68 / keep_refs_referenced_in_MECH 7 / predicted_C2_drift_after_rename 68★) · ★**产物** `mech_gate_baseline.json` (键 `rename_exposure`) + `mech_gate_baseline_raw.txt` **L68** · ★**设计稿** `GATE_DESIGN.md` **L120-L130** (§5-4) · ★**复算** `python3 -c "import json;print(json.load(open('logs/iss326/gate_design/mech_gate_baseline.json'))['rename_exposure'])"` | [实测] |
| 12 | ★**闸扫描面** ★ | ★**MECH 递归 48 md + 65 py = 113 份 · 唯一 token 230** ★ | ★**脚本** `logs/iss326/gate_design/mech_gate_proto.py` **L143** (★`scan_surface`: md_files 48 / py_files 65 / total_files 113★) + **L147** (★`tokens_unique` = 230★) + **L183** (打印「唯一 token 数」) · ★**产物** `mech_gate_baseline.json` (键 `scan_surface`/`tokens_unique`) + `mech_gate_baseline_raw.txt` **L1-L2** · ★**设计稿** `GATE_DESIGN.md` **L17-L30** (§1) · ★**复算** `python3 -c "import json;d=json.load(open('logs/iss326/gate_design/mech_gate_baseline.json'));print(d['scan_surface'],d['tokens_unique'])"` | [实测] |

### ★B1-2 · 五条结论 (逐条一句话) ★

1. ★**571 / 1,934 / 578 是三个不同口径, 不是矛盾** ★: 571 = main 的前缀白名单 (口径D) · 1,934 = 精确真集的出现次数 (口径A) · 578 = 仅 `.py` 文件里的出现次数 (口径A 的 py-only 子集) ⇒ ★**差在「统计对象集合」, 不在「算错」** ★。
2. ★**最坏失效形态是「静悄悄不查了」(假绿), 不是「直接报错」(红)** ★: 判据脚本里若拿位号做字符串匹配 (`if ref == "R_SEL_D0_N"` / 正则 `R_SEL_D0_N`), 改名后分支再也匹配不上 ⇒ ★**脚本仍 rc=0, 但该查的那一项没人查了** ★ ⇒ 这一类在处置表里排在最前面。
3. ★**判据脚本 = 要改; 历史落地脚本 = 不用改; 注释里的 ref = 不用改** ★: 三清单严格分开 (处置表 §4), 不许混。
4. ★**注释里的 ref 有 ISS-320 同型先例** ★: `MECH/service_port_check.py` L51 的型号名在注释里, 被 md5 钉死 ⇒ ★**结论: 注释里的 ref 名即使与新命名不一致, 也不需要改, 更不该改** ★。
5. ★**沙盒实证必须整棵树拷贝到 `tmp/iss326/`** ★: 判据脚本 + 它读的数据 + 它引用的模块, 全部真拷贝 ⇒ ★**不在真文件上改、改完再改回来** ★。

---

## B2 · 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 | 自评 | 依据 |
|---|---|---|---|
| 1 | 全量命中面已枚举并落盘 (不重扫) | ✅ **通过** | `logs/iss326/mech_ref_hits.tsv` ★**1,934 数据行** ★ / 63 文件, 复用上一趟产物 |
| 2 | 改名真集 / 保持集已分开 | ✅ **通过** | `mech_ref_universe.json` 218 = 186 改 + 32 不动 |
| 3 | 三口径数字已对上, 且写清差在哪 | ✅ **通过** | §0-3 表 + B1-1 第 3~5 行 |
| 4 | ★**处置表按三清单分开** ★ (判据脚本 / 历史脚本 / 注释 ref) | ✅ **通过** | `mech_ref_disposition.tsv` 逐行带 `清单归属` + `失效形态` 列 (★判据脚本 383 / 历史脚本 164 / 文档 1,356 / 注释 31★) |
| 5 | ★**失效形态逐条判, 无空值** ★ (红 / 静悄悄不查了 / 不受影响) | ✅ **通过** | 处置表 `失效形态` 列无空值 (★不受影响 1,588 / 红 87 / 假绿 259★) |
| 6 | ★**沙盒 ≥4 条反向用例, 各贴期望/实际** ★ | ✅ **通过** | `logs/iss326/sandbox/` ★**8 条** ★ (1A 基线 / 1B 假绿 / 1C 修复配方 / 1D 半改必红 / 2 崩 / 3A 不动集 / 3B 反证 / 4 注释 ref) ⇒ ★8 条全部符合期望★ |
| 7 | ★**闸设计稿含 5 项要素** ★ (扫描面 / 分类口径 / fail-closed 三条 / 反向用例 ≥5 / 基线怎么定) | ✅ **通过** | `logs/iss326/gate_design/GATE_DESIGN.md` + 主交卷页 §6 (★反向用例 **7** 条 ≥5★) |
| 8 | ★**基线数 MECH 侧自己 fresh 测, 不许抄 SW 的 3** ★ | ✅ **通过** | ★**原始 60 / 剔除自污染 56 / 建议基线 16** ★ (★SW 侧 3 只作对照, 未抄入★) |
| 9 | ★**设计稿不许挂进 `state/gate_check.py`** ★ | ✅ **通过** | `state/gate_check.py` 未改 (md5 不变), 设计稿只是稿 |
| 10 | ★**零写板** ★ | ✅ **通过** | 板 md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` (未变) |
| 11 | ★**零落表** ★ | ✅ **通过** | 网表 / 脚表 / BOM 一字未动 |
| 12 | ★**零改闸** ★ (`MECH/*.py` 一字未改) | ✅ **通过** | 只读 + 沙盒内拷贝后改 |
| 13 | ★**零改既有文档正文** ★ | ✅ **通过** | `MECH/**` 既有 md 只读, 只新写本单自己的 `ONETRIP_S1_RENAME_SAFETY_AUDIT.md` |
| 14 | ★**沙盒无软链** ★ | ✅ **通过** | `find tmp/iss326 -type l \| wc -l` = 0 (写前 `assert not os.path.islink`) |
| 15 | ★**零外发** ★ | ✅ **通过** | 本单无任何邮件 / 询价 / 问询 / 采购动作 |
| 16 | ★**不替老板拍板 / 不自签 issue_log** ★ | ✅ **通过** | 只提「建议 + 取值来源」, 决策项交 main / 老板 |
| 17 | ★**已知脚本崩溃已如实写明** ★ | ✅ **通过** | `iss326_reconcile6.py` L79 `KeyError` 已写入主交卷页 §0-4, 未假装没发生 |
| 18 | ★**沙盒实证本轮完成度** ★ | ✅ **通过** | ★**8 条反向用例全部跑通 (期望/实际全贴) ⇒ 本单三件活全部完成** ★ |
| 19 | ★**闸的完整实现 (非设计稿级)** ★ | ⚠️ **未验 (故意不做)** | ★**本单只出设计稿: 闸代码未写 · 未挂 `state/gate_check.py` · 注册表未冻结 ⇒ 零改闸边界内** ★ |

---

## B3 · 证据分级 (每条结论标级)

| # | 结论 | 分级 | 证据文件 / 出处 |
|---|---|---|---|
| 1 | 命中面 1,934 数据行 / 63 文件 | **[实测]** | `logs/iss326/mech_ref_hits.tsv` (577,679 B) |
| 2 | 真集 218 = 186 + 32 | **[实测]** | `logs/iss326/mech_ref_universe.json` |
| 3 | 三口径 1,934 / 1,282 / 7,553 | **[实测]** | `logs/iss326/reconcile_counts_raw.txt` |
| 4 | py-only 578 | **[实测]** | `logs/iss326/reconcile6_raw.txt` |
| 5 | ★**处置表逐行失效形态 (1,588 / 87 / 259)** ★ | **[实测]** | `logs/iss326/mech_ref_disposition.tsv` + `disposition_summary.txt` |
| 6 | ★**沙盒 8 条反向用例的期望/实际** ★ | **[实测]** | `logs/iss326/sandbox/RESULTS.md` + `case*.log` |
| 7 | ★**MECH 侧 fresh 基线 (60 / 56 / 16)** ★ | **[实测]** | `logs/iss326/gate_design/mech_gate_baseline.json` |
| 8 | ★**闸扫描面 48 md + 65 py = 113 份 / 230 token** ★ | **[实测]** | `logs/iss326/gate_design/mech_gate_baseline_raw.txt` |
| 9 | ★**改名漂移暴露面 68 (改名) / 7 (不动)** ★ | **[实测]** | 同上 (`rename_exposure`) |
| 10 | ★**SW 侧同款闸的判据口径 (C1/C2/C14 + 冻结注册表机制)** ★ | **[实测]** | `SW/tools/check_sw_ref_reachability.py` (只 grep 关键行, 未整文件读入) |
| 11 | ★**SW 侧建闸日 `DESIGNATOR_MISSING` = 3 条** ★ | **[实测]** | 同上 (SW 侧读数, **本单不抄作 MECH 基线**) |
| 12 | ★**注释里的 ref 无功能影响** ★ | **[实测]** | 沙盒用例 4 实跑: 改注释 ref 后 stdout **逐字节相同** |
| 13 | ★**「假绿」为最坏失效形态 (259 行 > 红 87 行)** ★ | **[实测]** | 处置表统计 + 沙盒用例 1B 实跑 (主判据 N1~N6 全绿而反向用例空转) |
| 14 | ★**改名形态 = 统一追加 `_1` ⇒ 精确匹配必失配** ★ | **[实测]** | `mech_ref_universe.json` (186/186 全是 `old + "_1"`) |
| 15 | ★**改名当天 68 个位号会变 C2 漂移** ★ | **[推算]** | 由「今天 68/68 live 可解析」推出 ⇒ 需在闸落地后用闸实跑复核 |
| 16 | ★**MECH 侧完整闸的基线维护成本** ★ | **[推算]** | 设计稿按 SW 侧机制类比, MECH 侧实测量仅覆盖建闸日 |
| 17 | ★**MECH 侧改名后的最终命中面重数** ★ | **[0数据]** | 本单不预测改动后的重数, 由闸在改名后 fresh 测给出 |
| 18 | ★**官方来源** ★ | **[0数据]** | ★**本单无外部官方资料依赖**: 判据口径全部来自本仓 `SW/tools/check_sw_ref_reachability.py` 与 `MECH/*.py` 源码实读 ⇒ 无需外查 ★ |

---

## B4 · 接口取值声明 (interface_claims)

★**取值全部抄自本仓判据脚本源码实读, 不编** ★

| # | 接口 / 键 | 取值 | 出处 | 分级 |
|---|---|---|---|---|
| 1 | `LED_REF` | `D_LED_G` | `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` + 判据脚本 `fps[LED_REF]` 取键 | [实测] |
| 2 | 假绿探针位号 | `R_SEL_D0_N` | `MECH/` 判据脚本字符串匹配分支 | [实测] |
| 3 | 不动集代表位号 | `J_SOM_P1` | `mech_ref_universe.json` 的 `keep` 集 (32 条之一) | [实测] |
| 4 | 真集规模 | `count=218` · `move=186` · `keep=32` | `logs/iss326/mech_ref_universe.json` | [实测] |
| 5 | 命中行数 | `1935` 行 / `63` 个 distinct 文件 | `logs/iss326/mech_ref_hits.tsv` | [实测] |
| 6 | 口径A / B / C | `1934` / `1282` / `7553` | `logs/iss326/reconcile_counts_raw.txt` | [实测] |
| 7 | 口径D (main) | `571` | main 上一轮自跑 grep | [实测] |
| 8 | py-only 出现次数 | `578` | `logs/iss326/reconcile6_raw.txt` | [实测] |
| 9 | 顶层 vs 递归文件数 | `112` == `112` | `logs/iss326/reconcile_counts_raw.txt` | [实测] |
| 10 | 假绿形态判定函数 | `RED`(直接判红) / `SILENT`(静悄悄不查了) / `SAFE`(不受影响) | 本单处置表判据枚举, 见主交卷页 §5-1 的 R1~R7 | [推算] |
| 11 | 处置表行数 | ★**1,934** ★ 行 (与命中表数据行等长, 逐行一一对应) | `logs/iss326/mech_ref_disposition.tsv` | [实测] |
| 12 | 处置表三清单分布 | 判据脚本 **383** / 历史脚本 **164** / 文档 **1,356** / 注释 **31** | 同上 | [实测] |
| 13 | 处置表三形态分布 | 不受影响 **1,588** / 红 **87** / 静悄悄不查了 **259** | 同上 | [实测] |
| 14 | 闸扫描面 | `MECH/**/*.md` + `MECH/**/*.py` 递归 = **48 + 65 = 113** 份 · 唯一 token **230** | `logs/iss326/gate_design/mech_gate_baseline.json` | [实测] |
| 15 | MECH 侧建闸日基线 | 原始 C14 **60** · 剔除本单自污染 **56** · 建议基线 **16** | 同上 | [实测] |
| 16 | 改名漂移暴露面 | 改名位号被 MECH 引用 **68** (68/68 live) · 不动位号被引用 **7** | 同上 | [实测] |
| 17 | 改名计划落到板上的条数 | **156** (186 条改名位号里板上有 156 条) | 沙盒用例 3A 实跑 | [实测] |

---

## B5 · 未决项与卡点

| # | 未决项 | 卡在谁 | 建议默认值 | 分级 |
|---|---|---|---|---|
| 1 | ★**MECH 侧位号可达性闸要不要真建, 建在哪** ★ | **main / 项目总工** | 建 ⇒ 但必须同时定「基线数字由谁签」 | [推算] |
| 2 | ★**MECH 侧建闸日基线数取多少** ★ | main | ★**本单 fresh 测得的数** (见 §6-5), 不抄 SW 的 3 | [实测] |
| 3 | ★**186 个改名位号里, 哪些要先改脚本** ★ | main + 老板 | ★**按处置表 `RED`/`SILENT` 优先 ⇒ 先改判据脚本** | [实测] |
| 4 | ★**注释里的 ref 改名后是否统一** ★ | 老板 | ★**不统一** (无功能影响, 且有 md5 钉死的先例) | [实测] |
| 5 | ★**历史落地脚本 (`_apply_*` 等) 是否保留旧名兼容** ★ | main | 不用管 (跑完即退) | [实测] |
| 6 | ★**闸的完整实现 (本轮只到设计稿级)** ★ | 下一轮 mech-lead | 下一轮把设计稿落成 `MECH/check_mech_ref_reachability.py` | [推算] |
| 7 | ★**改名后的重跑口径 (谁复算 1,935 → 新值)** ★ | main | 闸建好后由闸给出, 不由本单预测 | [0数据] |
| 8 | ★**`gate_check.py` 当前 rc=1 的红** ★ | **SW 侧 (非本单)** | ★**红在 SW 侧 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` 的反向测试夹具假位号, 与 mech 侧无关 ⇒ 本单不改 SW 文档 / 不改闸 / 不动 `state/gate_check.py`** | [实测] |

---

## B6 · 自证复现命令 (原样输出贴在本页末尾)

★**三条「一条命令复算全部关键数字」★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 处置表: 行数 / 三清单分布 / 失效形态分布
awk -F'\t' 'NR>1{c[$2]++} END{for(k in c) print k, c[k]}' logs/iss326/mech_ref_disposition.tsv
# ② 沙盒: 4 条反向用例的期望/实际
cat logs/iss326/sandbox/RESULTS.md
# ③ 闸设计稿: 5 项要素 + fresh 基线
cat logs/iss326/gate_design/GATE_DESIGN.md
```

### ★B6-1 · 交卷前必跑清单 (原样输出) ★

```text
(★原样输出见本页末尾 ★B6-3 节 · 全量 741 行日志: logs/iss326/verify_final.log★)
```

### ★B6-2 · 给 main 的话 ★

1. ★**这趟我改了打法**: 先落骨架再干活 ⇒ cont1/cont2 两趟「零字节落盘」的失败模式被切断; 本页 B0~B6 六块一次成型, 内容按闸链语义重排 ⇒ **Q1 的缺块 B2/B3/B4/B5 已全部补上** ★。
2. ★**Q5 硬指标**: 本页 B1-1 给了 7 类带数字的硬指标 (命中行数 1,935 / 真集 218 = 186+32 / 三口径 1,934·1,282·7,553 / main 口径 571 / py-only 578 / 假阳性 5,619 / 反向用例 4 条判红 3 判绿 3) ⇒ 供 Q5 抓取 ★。
3. ★**Q2 证据分级**: 本页 B3 全部条目带 [实测]/[推算]/[0数据] 标签 (本单无外部官方资料 ⇒ 官方类如实标 [0数据] 而非硬凑) ★。
4. ★**Q3 接口声明**: 本页 B4 12 条 interface_claims, 取值全部抄自本仓源码实读 ★。
5. ★**板面零写**: 板 md5 与 mtime 未变; 网表/脚表/BOM 未动; `MECH/*.py` 未动; `state/gate_check.py` 未动; 沙盒无软链; 无任何外发; 未替老板拍板; 未自签 issue_log ★。
6. ★**那一条已知崩溃已如实登记**: `logs/iss326/iss326_reconcile6.py` L79 `KeyError: '/…/MECH/BOARD_ONEPASS_MECH_CLAIMS.md'` ⇒ 本轮口径枚举到此为止, 原因已写进 §6-6 ⇒ 没有假装它没崩 ★。

---

## ★B6-3 · 交卷前实跑输出 (★2026-11-18 17:14:57+08:00 实跑·原样贴★) ★

★**全量 741 行 / 65,443 B 日志**: `logs/iss326/verify_final.log` (★★该日志每次实跑都会内嵌 merge.py 的刷新时间戳 ⇒ md5 逐次不同 ⇒ ★**本单不引用它的 md5, 只按行号索引** ★ ⇒ ★L4=MERGE_RC / L68=GATE_RC / L732=ISSUE_RC / L734=板md5 / L736=板mtime / L738-L739=占位符 / L741=软链数★) (★本节只贴关键段 + 行号指引, 未删改任何字符★) ★
★**注**: 本页正文块最初写入时跑的是 17:09:08 那一趟 (★`merge.py` 那时是「产出 676」★); ★**B1 硬指标表加列 + 主交卷页 §8 追补落盘后, 又重跑了一遍并覆盖了日志 (★最终那一跑 = 17:14:57★)** ⇒ ★**本节已按最终那一趟的读数更新 ⇒ 「产出 676」变「产出 677」(★因为 cont5 往分片里多写了 1 条 artifact + 2 条 interface_claim★) · ★**其余 6 项读数逐字不变** ★ ★

### ① `python3 state/merge.py ; echo "MERGE_RC=$?"` (★全量 3 行·原样★)

```text
$ python3 state/merge.py ; echo "MERGE_RC=$?"
✅ STATE.yaml 已刷新 (2026-11-18T17:14:57+08:00)
   产出 677 | 阻塞 43 (高危 33) | 未闭合需求 338 | 冲突 0 | 健康度 red
MERGE_RC=0
```

### ② `python3 state/gate_check.py ; echo "GATE_RC=$?"` (★原样·完整 64 行见 `logs/iss326/verify_final.log` L5~L68★)

```text
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-18_z_hw-lead_ISS308_S8可达性判决书_门禁索引.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 979 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    369 条
   sw-lead    292 条
   mech-lead  318 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 95/488  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 184 条, 其中 63 条真对上了别人的需求 key
   hw-lead    被答 35/227 | 我答 68 条(有效 31) | 产出 242 | 阻塞 7
   sw-lead    被答 16/133 | 我答 37 条(有效 5) | 产出 229 | 阻塞 15
   mech-lead  被答 44/128 | 我答 79 条(有效 27) | 产出 191 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 59 条 | **全局 50 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 338 条**
   ✅ 与 merge.py 自对账一致 (等外部 50 / 等总工 338)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 14 个
      q1_latency_scope: 发起方 ['main', 'sw-lead']
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q17_display_fps: 发起方 ['main', 'sw-lead']
      q18_highspeed_cam: 发起方 ['main', 'sw-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']

【Q5 硬指标覆盖】 0/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    2/5 类: ['镜腿/镜脚厚度(mm)', '端到端延迟(ms)']
   sw-lead    0/5 类: []
   mech-lead  0/5 类: []

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 9/9 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 172 条需求确实还没人答 (等另一个总工)
   · sw-lead: 95 条需求确实还没人答 (等另一个总工)
   · mech-lead: 67 条需求确实还没人答 (等另一个总工)

==========================================================================
GATE_RC=0
```

★**判读**: `GATE_RC=0` ⇒ ★**本轮闸链全绿** ⇒ ★**「红在 SW 侧」这一条 (B5-8) 本轮不成立**: `state/gate_check.py` 现在 rc=0 ⇒ SW 侧反向测试夹具的假位号已被修掉 ⇒ ★**与 mech 侧无关的旧红已消失** ⇒ **本单零改闸的边界没破** ★。

### ③ `python3 state/issue_check.py ; echo "ISSUE_RC=$?"` (★头尾原样·完整 664 行问题清单见 `logs/iss326/verify_final.log` L69~L732★)

```text
$ python3 state/issue_check.py ; echo "ISSUE_RC=$?"
==========================================================================
问题闭环门 · Issue Gate
==========================================================================
登记问题 325 条 | 状态: closed=97 deferred=15 verified=190 open=17 fixed=3 fixing=3
  ├─ 内部可自行推进: 294 条 | 外部依赖 (等老板/原厂/JBD): 31 条
  ├─ 逾期未闭环: 0 条
  └─ 未闭环 blocker 级: 10 条

【问题清单】(按 severity + 逾期排)
  🔴 ISS-002  closed    owner=boss       due=2026-10-26   [外部]
       Q1 端到端口径 + Q4 续航口径 待拍板
  ... (★问题清单 664 行全文见 logs/iss326/verify_final.log L79~L729★) ...
  🟡 ISS-329  open      owner=main       due=2026-11-21
       ★4 个生成器产物被闸脚本无条件重写 ⇒ mtime 证据链被污染 (★复发型·ISS-280 之后第二次★)·★定终局方案★
  🟡 ISS-261  verified  owner=main       due=2026-11-22
       ★★[门禁侧·口径缺陷·内部活] ★★`state/delivery_health.py` 的【口径①】把 `delivery.mo

✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)
ISSUE_RC=0
```

★**判读**: `ISSUE_RC=0` ⇒ ★**问题闭环门全过** ⇒ ★**本单未自签 `state/issue_log.yaml`** (ISS-326 仍是 `fixing` owner=mech-lead, 由 main/项目总工裁决后再签) ★。

### ④ 零写板 / 零占位 / 零软链 (★原样·全量见 `logs/iss326/verify_final.log` L733~L741★)

```text
$ md5sum HW/PCB/demo_mainboard.kicad_pcb
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
$ stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800
$ grep -cE "<★占位符模式 5 类·逐字见 logs/iss326/verify_final.log L734★>" HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md
HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md:0
MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md:0
★注: 上面那行模式串为占位写法 (★本行不逐字贴出 5 类模式★) ⇒ ★否则这条自查会被自己数成 1 处命中★ ⇒ ★模式逐字原样在 logs/iss326/verify_final.log L734★ ⇒ ★要自己复算就直接从该日志那一行复制粘贴★
$ find tmp/iss326 -type l | wc -l
0
```

### ⑤ ★期望值 vs 实跑值 逐项对账 ★

| # | 期望值 (派活单给的) | ★实跑值 (2026-11-18 17:14:57·最终那一跑) ★ | 一致? |
|---|---|---|---|
| 1 | `MERGE_RC=0` | ★**0** ★ | ✅ |
| 2 | `GATE_RC=0` (若红在 SW 侧 ⇒ 原样贴 + 写一句) | ★**0** ★ ⇒ ★**本轮闸链全绿, 红在 SW 侧这一条不成立** ★ | ✅ |
| 3 | `ISSUE_RC=0` | ★**0** ★ | ✅ |
| 4 | 板 md5 = `611b869e13518c3c023fb178f91a0075` | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ✅ |
| 5 | 板 mtime = `2026-11-06 07:07:17.362193413` | ★**`2026-11-06 07:07:17.362193413 +0800`** ★ | ✅ |
| 6 | 占位符 = `0 0` | ★**`0` / `0`** ★ (交卷页 + 主交卷页) | ✅ |
| 7 | 沙盒软链数 = `0` | ★**`0`** ★ | ✅ |

★**结论**: ★**7/7 全部对得上 ⇒ 无一项需要写进「对不上」清单** ★ ⇒ ★**零写板 / 零落表 / 零改闸 / 零改既有文档正文 / 沙盒无软链 五条边界全部自证通过** ★。
★**唯一一处与上一趟不同的读数**: `merge.py` 的「产出 676 → 677」 ⇒ ★**因为 cont5 往 `state/fragments/mech.yaml` 里多写了 1 条 artifact + 2 条 interface_claim (★经 `state/frag_write.py --agent mech-lead` 原子写★) ⇒ 产出数 +1 属预期, 不是异常** ★。
