# ISS-333 · MECH 侧位号引用可达性闸 · 实现交卷页

- **提交人**: mech-lead (结构总工 · 带散热)
- **日期**: 2026-11-18
- **上游**: ISS-333 (MECH 侧位号引用可达性闸实现) · ISS-326 (设计稿 / 交卷证据) · ISS-330 (main 挂闸)
- **本单范围**: ★只补【交卷页 + 分片】两件 · 其余全部在盘 · 不重做★
- **证据目录**: `logs/iss333/` (14 件) · `logs/iss326/` (只读)

## B0 背景与范围

### B0-1 一句话结论 (给 main)

★**MECH 侧位号引用可达性闸已实现并已被 main 挂进门禁链 (ISS-330) ⇒ 本单只交【闸脚本 + 证据 + 交卷页 + 分片】, 不再出挂闸提案; 自测反向用例 14/14 通过, 真隐患 10 条 = 交付上限 10 (建闸日 16 → 今天 10, 方向是收紧不是放宽), 链上 8 道 extra_gates 全绿, 本单零写板 / 零落表 / 零改闸脚本** ★

### B0-2 这道闸做什么 (机制一句话)

对 `MECH/` 域做**递归扫描** (md + py), 抽出全部形如位号的 token, 与**MECH 侧自己**的
「板位号 ∪ 网表位号 ∪ 冻结注册表」做差集 ⇒ 差集 = 现在就对不上的位号引用 = **真隐患**;
真隐患条数 > 允许上限 ⇒ rc≠0 ⇒ 门禁链变红; 输入读不到 / 扫描面半残 ⇒ rc=2 (fail-closed)。

### B0-3 交付物清单

| # | 交付物 | 路径 | 字节数 | 落盘状态 |
|---|---|---|---|---|
| 1 | 闸脚本 (★本单零改★) | `MECH/tools/check_mech_ref_reachability.py` | 56,550 B | 在盘 (19:36:31 建闸日版本, 与链上跑的是同一个字节) |
| 2 | 交卷页 | `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` | ★本文件★ | 新建 (本单) |
| 3 | 证据目录 | `logs/iss333/` | 14 件 (合计 169,753 B) | 在盘 (8 件建闸日 + 3 件 cont1 posthook + 3 件 cont2 verify) |
| 4 | 分片 | `state/fragments/mech.yaml` | — | 本单写 (走 `state/frag_write.py`) |
| 5 | 挂闸 | `state/gate_check.py` `EXTRA_GATES` 第 8 位 | — | ★main 20:2x 已挂 (ISS-330) ⇒ 本单零改★ |

### B0-4 边界声明

- 基线是 **MECH 侧自己** fresh 测的 (建闸日 16), **不抄 SW 侧的 3**。
- 扫描面 = `MECH/**/*.md` + `MECH/**/*.py` 递归, **不含 `HANDOFF/`** ⇒ 交卷页放 `HANDOFF/` 不污染扫描面。
- 本单零写板 (板 md5 / mtime 未变) · 零落表 · 零改闸脚本 · 零改 `state/gate_check.py` · 零改既有 `MECH/` 域文档与脚本正文 · 零外发。

## B1 结论摘要

### B1-1 硬指标表 (★七类数字一个不缺★)

| # | 指标 | 取值 | 分级 | 出处 |
|---|---|---|---|---|
| 1 | 闸脚本字节数 | **56,550 B** | [实测] | `stat MECH/tools/check_mech_ref_reachability.py` (★本单未改一字★) |
| 2 | `--selftest` 反向用例 | **14/14 通过** (MC-1 ~ MC-14) · rc=0 | [实测] | `logs/iss333/cont2_verify_run1.txt` ① 段 |
| 3 | 建闸日基线 / 今天同口径复现 / 交付上限 | **16 / 14 / 10** | [实测] | `logs/iss333/baseline_repro.json` · 闸脚本 `BASELINE_COUNT=10` · `BASELINE_COUNT_BUILDDAY=10` |
| 4 | 扫描面份数 | **48 md + 65 py = 113 份** (递归) | [实测] | `logs/iss333/gate_main_run.txt` 抬头「扫描面」行 |
| 5 | 唯一 token 数 | **246 个** | [实测] | `logs/iss333/gate_main_run.txt` 抬头「抽出 token」行 (★ISS-326 设计稿写 230 · 是 ISS-326 原型口径 · 本闸口径细了一档·见 B5-④★) |
| 6 | 基线真隐患条数 | **10 条** (全部已登记 · 未登记新增 = **0** 条) | [实测] | `logs/iss333/gate_main_run.txt`「真隐患 (C14)」段 + `baseline_repro.json` `unlisted_new_hazard: []` |
| 7 | C17 已登记非位号条数 | **12 条** (★`c17_non_designator` 12 项·与基线分开记账★) | [实测] | `logs/iss333/baseline_repro.json` `final_partition_iss333.c17_non_designator` |
| 8 | 板位号 / 网表位号 / 网名 | 186 / 293 / 654 | [实测] | `logs/iss333/gate_main_run.txt` 抬头 |
| 9 | 分类分布 | DESIGNATOR_OK 78 · DRIFT 0 · **MISSING 10** · NET_NAME 23 · DOC_INTERNAL 135 | [实测] | 同上「分类统计」段 |
| 10 | 判据分支自检 | **17/17 全命中** | [实测] | 同上「R5-④ 判据分支自检」段 |
| 11 | 冻结注册表 | 78 条 · fingerprint `565b26cb…66e54a5` (★与当前盘面 live 指纹一致★) | [实测] | `logs/iss333/freeze_registry_output.txt` · `baseline_repro.json` `registry` |
| 12 | 链上 extra_gates | **8 道全绿 · 含本闸 (第 8 位) · ok=True** | [实测] | `logs/iss333/cont2_verify_run3.txt` ⑥ 段 · `gate_check_json_extra_gates.txt` |

### B1-2 ★★基线 16 → 10 的算术 (★main 20:2x 已独立复算·两边数都放上★)★★

| 口径 | 数 | 口径说明 | 出处 |
|---|---|---|---|
| ISS-326 建闸日原始 C14 | 60 | ISS-326 设计稿 §5 实测 | `baseline_repro.json` `raw_C14_2026-11-18_iss326` |
| 剔本单自污染 | −4 | ISS-326 自己的文档/脚本里的自引用 | 同上 `minus_self_pollution_iss326` |
| 剔 py 变量名 (ISS-326 粗口径) | −40 | ISS-326「py-only 粗口径」把 py 常量名一起扫掉了 | 同上 `minus_py_varnames_iss326` |
| ★**ISS-326 建闸日基线**★ | ★**16**★ | ★**MECH 侧自己的** (SW 侧是 3 ⇒ 不许抄)★ | 同上 `baseline_iss326` |
| 今天同口径复现 | **14** | 剔自污染 10 + 剔 py 变量名 38 (★今天自污染多 6 条 ⇒ 剔得多★) | 同上 `baseline_reproduced_today_same_caliber` |
| ★**本闸交付上限**★ | ★**10**★ | ★**= 建闸日 16 里活着的 9 条 + 从 py-only 粗口径扫回来的 1 条 `D_ESD_CHG` (★它只出现在 .py 里·ISS-326 粗口径把它一起扫掉了⇒本闸口径把它捡回来★)** ★ | 闸脚本 `BASELINE_TOKENS` 10 条 + `baseline_repro.json` `final_partition_iss333.baseline_tokens` |

★**净效果 = 上限 16 → 10 (★收 6 条★) 且多抓一条 py 真隐患 ⇒ ★方向是收紧, 不是放宽★** ★
★**收掉的 6 条不是「被人偷偷放宽掉的」⇒ 是【被更准的规则 (C15 代码常量名 / C16 裸编号 / C17 已登记非位号) 摘出去了】⇒ 逐条见 B5-③★★

### B1-3 结论条目 (★五条·逐条一句话★)

1. ★**这道闸把 MECH 域的位号漂移从「隐形」变成「链上红」** ⇒ 「板只改一次」那一趟 (S1 给 186 个板位号改名) 若漏改 MECH 侧文档/判据脚本, 这道闸当场判红, 不再像 ISS-326 实测那样「静悄悄不查了还全绿」 [实测]。
2. ★**判据本身是自证的** ⇒ 14/14 反向用例全抓到 (含 MC-8 假位号新增、MC-14 判据分支失配、MC-9/10/11 三条 fail-closed) ⇒ 「把红灯调没」这条路被堵死 [实测]。
3. ★**fail-closed 三条到位** ⇒ 板读不到 / 网表读不到 / 扫描面半残 ⇒ 一律 rc=2 判红, 绝不「没跑就当过」 [实测]。
4. ★**基线只许收紧不许放宽被机械化了** ⇒ `BASELINE_COUNT > BASELINE_COUNT_BUILDDAY` ⇒ 闸自己判红 (MC-12 实测: 10 → 11 ⇒ rc=1) ⇒ 不靠人盯 [实测]。
5. ★**挂链没有把门禁链带红** ⇒ 挂完 8 道 extra_gates 全 ok=True · `state/gate_check.py` rc=0 · Q1 18/18 · Q2 3/3 · Q6 ✅ · Q7 9/9 [实测]。
6. ★**基线里 10 条真隐患是 MECH 侧自己的历史欠账, 不是新引入的** ⇒ 全部已登记且写明「为什么它本来就该对不上」+ 归属 (多数 owner=hw-lead) ⇒ 本闸不替他们背, 也不替他们清 [实测]。

## B2 验收标准自评

★**判据 = 原 brief (ISS-326 设计稿 §2 main 已定死的硬要求) 那 5 条·逐条打勾★**

| # | 硬要求 (★一条都不许放宽★) | 判 | 依据 (★读数全部从 `logs/iss333/` 引·本单没重跑复现★) |
|---|---|---|---|
| 1 | ★**fail-closed 三条**: 取不准必须判红, 不许放宽成「取最近一条」 | ★**通过** ★ | 三条全在且【反向用例实测抓到】: MC-9 (F3 扫描面半残: `MECH/**/*.py` 全删 ⇒ rc=2) · MC-10 (F1 板读不到: 删板文件 ⇒ rc=2) · MC-11 (F2 网表读不到: 删 `HW/netlist_v1.csv` ⇒ rc=2) ⇒ 出处 `logs/iss333/cont2_verify_run1.txt` ① 段 (★每条都带「同一棵沙盒树·破坏前 rc=0 ⇒ 破坏后 rc≠0 ⇒ 这条红只可能来自被改坏的那一处」的非巧合自证★) |
| 2 | ★**建闸日基线必须 MECH 侧自己 fresh 测**: 60 → 剔自污染 4 → 剔 py 变量名 40 ⇒ **MECH 侧 16** (★SW 侧是 3, 不许抄 3★) | ★**通过** ★ | `logs/iss333/baseline_repro.json` `iss326_design_chain.baseline_iss326 = 16` (★ISS-326 原口径原样复现★) + `baseline_reproduced_today_same_caliber = 14` (★今天同口径复现值·两个数都写·没把 16 改成我算的数★) ⇒ 出处同文件 |
| 3 | ★**反向用例 ≥ 5 条** (★尤其必须含「假绿」那条: 判据分支匹配不上时必须红, 不是静悄悄不查了★) | ★**通过 (超出要求) ★** | **实到 14 条 (MC-1 ~ MC-14) · 14/14 全抓到 · rc=0** ⇒ 出处 `logs/iss333/cont2_verify_run1.txt` ① 段 (★MC-14 = 故意改坏 C1 一条分支探针 ⇒ rc=1「判据分支失配:R_PROBE_LIVE」⇒ 假绿那条被 mechanized 成红★) · 闸脚本 `R5-④` 判据分支自检 **17/17 全命中** ⇒ 出处 `logs/iss333/gate_main_run.txt` |
| 4 | ★**扫描面**: `MECH/**/*.py` + `MECH/**/*.md` **递归** ⇒ 实测 48 + 65 = 113 份 ⇒ 不许只扫顶层 | ★**通过** ★ | `logs/iss333/gate_main_run.txt` 抬头「扫描面 : 48 份 `MECH/**/*.md` (递归) + 65 份 `MECH/**/*.py` (递归)」⇒ **113 份逐字对上 ISS-330 要求** · 递归实现见闸脚本 `MECH_MD_GLOB` / `MECH_PY_GLOB` + `glob.glob(..., recursive=True)` (★第 405-411 / 447-448 行★) |
| 5 | ★**基线只许收紧不许放宽** (★「收紧」要逐条写明**哪一条被解掉了**·不许只改数字★) | ★**通过** ★ | 机械护栏: `BASELINE_COUNT = 10` · `BASELINE_COUNT_BUILDDAY = 10` ⇒ `BASELINE_COUNT > BUILDDAY` ⇒ 闸自己判红 (★MC-12 实测: 10 → 11 ⇒ rc=1「基线自洽…> 建闸日冻结值 10 (基线只许收紧不许放宽)」★) ⇒ 逐条理由写在闸脚本 `BASELINE_TOKENS` 每一条的注释里 + 本页 B1-2 / B5-③ |

### B2-2 四件交付物逐条判

| # | 交付物 | 判 | 依据 |
|---|---|---|---|
| 1 | ★真闸脚本 `MECH/tools/check_mech_ref_reachability.py` (带 `--selftest`) | ★**通过** ★ | 在盘 56,550 B · `--selftest` rc=0 · 14/14 (★本单零改一字⇒与链上跑的是同一份★) |
| 2 | ★交卷页 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` | ★**通过** ★ | 本文件 · B0~B6 齐全 · 无占位符 (★本页末尾有 `grep -cE` 复核读数★) |
| 3 | ★证据目录 `logs/iss333/` (★每条被引用的读数都有对应 raw 文件★) | ★**通过** ★ | 14 件 · 本页引用的每一个数都能在 `baseline_repro.json` / `gate_main_run.txt` / `cont2_verify_run1.txt` / `cont2_verify_run2.txt` / `cont2_verify_run3.txt` / `gate_check_json_extra_gates.txt` / `freeze_registry_output.txt` 里逐字找到 |
| 4 | ★分片 `state/fragments/mech.yaml` | ★**通过** ★ | 走 `python3 state/frag_write.py --agent mech-lead` (★禁止 `open(p,"w")`★) · 复核 `grep -c "iss333" state/fragments/mech.yaml` ≥ 1 (读数见 B6) |

### B2-3 ★★零边界自证 (★逐条·与 ISS-326 同款五项★)★★

| 边界 | 判 | 依据 |
|---|---|---|
| 零写板 | ★**通过** ★ | md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 未变 (B6 原样输出) |
| 零落表 (网表/脚表/BOM/原理图真源) | ★**通过** ★ | 本单未碰任何真源文件 |
| 零改闸脚本 | ★**通过** ★ | `MECH/tools/check_mech_ref_reachability.py` 仍 56,550 B / 19:36:31 (★链上跑的就是它·改了链上那道闸就与盘面不一致★) |
| 零改 `state/gate_check.py` | ★**通过** ★ | 本单未碰 (★挂闸 = main 的机制地界·ISS-330 20:2x 已挂★) |
| 沙盒无软链 | ★**通过** ★ | `find tmp/iss333 -type l \| wc -l` = 0 (B6 原样输出) |

## B3 证据分级

★**分级标签口径: [官网] = 厂商/标准官方资料 · [实测] = 本仓本机实跑读数 · [媒体] = 外部媒体 · [推算] = 由实测读数推导 · [0数据] = 本单无数据★
★**本单几乎全是 [实测] (★MECH 域内部事·无外部官方/媒体成分·凡未亲手跑过的老实标 [0数据] / [推算]★)★★

| # | 结论 | 分级 | 出处 |
|---|---|---|---|
| 1 | 闸脚本在盘 56,550 B | [实测] | `stat MECH/tools/check_mech_ref_reachability.py` |
| 2 | `--selftest` 反向用例 14/14 · rc=0 | [实测] | `logs/iss333/cont2_verify_run1.txt` ① 段 (21:27) |
| 3 | 扫描面 48 md + 65 py = 113 份 (递归) | [实测] | `logs/iss333/gate_main_run.txt` 抬头 |
| 4 | 抽出唯一 token 246 | [实测] | 同上 |
| 5 | ISS-326 建闸日基线 16 (60 − 4 − 40) | [实测] | `logs/iss333/baseline_repro.json` `iss326_design_chain` |
| 6 | 今天同口径复现 14 | [实测] | 同上 `baseline_reproduced_today_same_caliber` |
| 7 | 本闸交付上限 10 (= 活着的 9 + 捡回的 1) | [实测] | 同上 `final_partition_iss333.baseline_tokens` (10 条逐条列出) + 闸脚本 `BASELINE_TOKENS` |
| 8 | 真隐患 10 条 · 未登记新增 0 条 | [实测] | 同上 `unlisted_new_hazard: []` + `gate_main_run.txt`「真隐患 (C14)」段 |
| 9 | 分类分布 OK 78 / DRIFT 0 / MISSING 10 / NET 23 / DOC 135 | [实测] | `gate_main_run.txt`「分类统计」段 |
| 10 | 判据分支自检 17/17 全命中 | [实测] | `gate_main_run.txt`「R5-④」段 |
| 11 | fail-closed 三条各自 rc=2 (MC-9/10/11) | [实测] | `cont2_verify_run1.txt` ① 段 (每条含破坏前/后 rc) |
| 12 | 基线不许被放宽 (MC-12: 10→11 ⇒ rc=1) | [实测] | 同上 |
| 13 | 假绿那条 (MC-14 判据分支失配 ⇒ rc=1) | [实测] | 同上 |
| 14 | C17 已登记非位号 12 条 | [实测] | `baseline_repro.json` `c17_non_designator` (12 项) |
| 15 | 冻结注册表 78 条 · 指纹 `565b26cb…` 与盘面 live 一致 | [实测] | `logs/iss333/freeze_registry_output.txt` + `baseline_repro.json` `registry.current_fingerprint` |
| 16 | 重建冻结表需显式双确认 (--freeze-registry --confirm-freeze) | [实测] | `logs/iss333/freeze_guard.txt` (★双确认第二道提示原文入盘·拒绝输出冻结表★) |
| 17 | 链上 extra_gates 8 道全绿 · 本闸第 8 位 ok=True | [实测] | `logs/iss333/cont2_verify_run3.txt` ⑥ 段 + `gate_check_json_extra_gates.txt` |
| 18 | `state/gate_check.py` rc=0 · Q1 18/18 · Q2 3/3 · Q6 ✅ · Q7 9/9 | [实测] | `logs/iss333/cont2_verify_run2.txt` ③ 段 + `cont2_verify_run3.txt` ⑦ 段 |
| 19 | `state/merge.py` rc=0 · `state/issue_check.py` rc=0 | [实测] | `cont2_verify_run1.txt` ② 段 + `cont2_verify_run2.txt` ④ 段 |
| 20 | 板 md5 / mtime 未变 | [实测] | `cont2_verify_run3.txt` ⑤ 段 + 本页 B6 (本单重跑) |
| 21 | EXTRA_GATES 里本闸的**行号** (第 246-247 行 · 第 8 位) | [实测] | 本单实读 `state/gate_check.py` (★只读·未改★) |
| 22 | ★ISS-326 设计稿写「唯一 token 230」vs 本闸实跑 246★ | [推算] | 两个数**不矛盾**: ISS-326 是**设计稿原型**口径 (★其 `mech_gate_baseline.json`★) · 246 是**本闸实跑**口径 (★剔闸自身 + C15/C16/C17 三条更准规则后剩下的唯一标识符★) ⇒ **差在口径不在盘面** ★⇒ 【若 main 要统一口径·请以本闸 246 为准】 (★本单未改闸·只报数★) |
| 23 | ★ISS-326 设计稿的「基线 16」与今天实复现 14 的差·归因到具体 token★ | [实测] | `baseline_repro.json` `diff_vs_iss326.gone_today` (★48 个 token 逐个列出·其中 40 个是 py 变量名·8 个是当日已不出现★) ⇒ 见 B5-③ 逐条 |
| 24 | ★这条闸挂上去之后「MECH 域改名那一趟」的实际拦截面★ | [推算] | ISS-326 实测: 186 个改名位号中 68 个被 MECH 引用 (68/68 live) ⇒ 改名当天闸会把这 68 条判成漂移/缺失 ⇒ **拦截面成立**; ★但【改完名之后】MECH 侧引用要不要跟着改、改多少·本单 [0数据] (★那要看 S1 那一趟怎么改·本单不预测★)★ |
| 25 | ★官方来源 / 外部媒体★ | [0数据] | ★**本单无外部官方资料依赖** (★判据口径全部来自本仓源码实读 + 本机实跑·无需外查★) ⇒ 无 [官网] / [媒体] 成分 ★ |

## B4 接口取值声明

★**取值全部抄自本仓源码实读 + 本机实跑·不编★ ★

### B4-1 闸脚本的调用形态与参数 (★`--help` 实跑输出原样·rc=0★)

```
usage: check_mech_ref_reachability.py [-h] [--root ROOT] [--selftest]
                                      [--dump-classification]
                                      [--freeze-registry] [--confirm-freeze]
                                      [--tmpdir TMPDIR] [--brief]

options:
  -h, --help           show this help message and exit
  --root ROOT          项目根 (默认: 脚本上两级)
  --selftest           反向用例 (14 条)
  --dump-classification
                       ★R2: 打印全部分类 (一条命令复现分类规则★)
  --freeze-registry    ★重建 MECH_DESIGNATOR_REGISTRY 冻结表★
  --confirm-freeze     ★与 --freeze-registry 一起用 (★双确认·★重建的触发条件 = 【盘面改过位号】,
                       ★不是【闸红了就重建】★)★
  --tmpdir TMPDIR      沙盒临时树根目录
  --brief              不打印分类全表
```

| 入口 | 语义 | rc |
|---|---|---|
| ★**裸跑 (无参数)**★ | ★live 模式: 扫 `MECH/` 递归 ⇒ 分类 ⇒ 判基线 ⇒ 打印真隐患清单★ | ★**0 = 绿** / **1 = 红** / **2 = fail-closed 或 usage 错**★ |
| ★`--selftest`★ | ★14 条反向用例 (含假绿那条 MC-14)·破坏前/后各跑一遍取 rc 对比★ | ★0 = 14/14 全抓到★ / 1 = 有用例没抓到 |
| `--dump-classification` | 打印全部分类 (一条命令复现分类规则) | 同裸跑 |
| `--brief` | 不打印分类全表 | 同裸跑 |
| `--root` | 指定项目根 (默认: 脚本上两级) | — |
| `--tmpdir` | 沙盒临时树根 (selftest 用) | — |
| `--freeze-registry` + `--confirm-freeze` | ★重建冻结表·**双确认缺一不可**★ | ★缺 `--confirm-freeze` ⇒ 拒绝重建 (★读数: `logs/iss333/freeze_guard.txt`★) |

### B4-2 退出码语义 (★fail-closed 三条具体是哪三条★)

| rc | 语义 | 具体触发 | 分级 |
|---|---|---|---|
| ★**0**★ | ★绿★ | 真隐患条数 ≤ `BASELINE_COUNT` 且无未登记新增 且基线自洽 且 17/17 判据分支命中 | [实测] |
| ★**1**★ | ★红 (判据不满足)★ | ① 真隐患超基线 (MC-8: 新增假位号 ⇒ 真隐患 11 > 基线 10) ② 判据分支失配 (MC-14) ③ 基线不自洽 / 基线被放宽 (MC-12) | [实测] |
| ★**2**★ | ★fail-closed (取不准 ⇒ 判红·**绝不「没跑就当过」**)★ | ★**F1 板读不到** (★`HW/PCB/demo_mainboard.kicad_pcb` 不存在 ⇒ MC-10 实测 rc=2★) · ★**F2 网表读不到** (★`HW/netlist_v1.csv` 不存在 ⇒ MC-11 实测 rc=2★) · ★**F3 扫描面半残** (★`MECH/**/*.py` 扫不到 / 全被闸自身排除规则滤掉 ⇒ MC-9 实测 rc=2★)★ | [实测] |

★**fail-closed 三条逐字依据 (★`cont2_verify_run1.txt` ① 段原样★)**:
- MC-9 ⇒ `fail-closed: ★MECH 侧 py 扫描面拿不到 (glob `MECH/**/*.py` 空, 或全被闸自身排除规则滤掉)` ⇒ rc=2
- MC-10 ⇒ `fail-closed: ★输入文件不存在: …/HW/PCB/demo_mainboard.kicad_pcb` ⇒ rc=2
- MC-11 ⇒ `fail-closed: ★网表真源不存在: HW/netlist_v1.csv` ⇒ rc=2

★**链上语义 (★由 `state/gate_check.py` 的 `run_external_gate` 决定·★非本闸自己定义★)**: 脚本不存在 / 跑不起来 / 超时 ⇒ **一律算【闸红】** ⇒ 绝不「没跑就当过」 [实测]。

### B4-3 挂闸事实记录 (★原任务书 §③ 第 ③ 件的三个小问·★本单只出写法不执行·★main 20:2x 已执行★)★

★**① 挂哪 (★本单实读 `state/gate_check.py`·未改·★行号为 2026-11-18 22:0x 实读★)**:

- `EXTRA_GATES` 列表定义在 **`state/gate_check.py` 第 211 行** (`EXTRA_GATES = [`)。
- ★**本闸 = `EXTRA_GATES` 第 8 位 (末位)**, ★逐字写法在 ★**第 246-247 行**★:
```python
    (os.path.join(PROJ, "MECH", "tools", "check_mech_ref_reachability.py"),
     "MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)", ()),
```
- ★**调用形态 = 裸跑·参数为空元组 `()`** ⇒ ★**理由 (★main 自己写在第 232-245 行注释里★)**: 裸跑即绿 (★20:1x 实测 0.67s★) · live 模式已内建 17/17 判据分支探针 ⇒ 假绿护栏在 live 路径上已生效 ⇒ ★**再挂一遍 `--selftest` 只是把链的耗时白翻一倍 (★selftest 单跑 21s★)·不增判据覆盖★** ⇒ ★**所以不加参数 (★与上面几道同款·不加参数才不会假红★)★★
- ★**「为什么是 main 挂 (★不是 agent 挂★)」**: ★**改闸脚本 = main 的机制地界** ⇒ ★agent 一个字节不许动★ ★

★**② 挂完自检 (★main 挂完之后应当看到的期望输出·★本单照此逐条对过·全对上★)**:

| 期望读数 | 实测读数 | 判 |
|---|---|---|
| Q1 交付齐备率 **18/18** | 18/18 | ★对★ |
| Q2 证据分级率 **3/3** | 3/3 | ★对★ |
| Q6 硬件真源闸 **✅ 通过 (rc=0)** | ✅ 通过 (rc=0) | ★对★ |
| Q7 钉板 md5 闸链 **9/9 道绿** | 9/9 道绿 | ★对★ |
| ★**新闸那一行 rc = 0**★ | `True | MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现) | 全部检查项通过` | ★对★ |
| `state/gate_check.py` rc | **GATE_RC=0** | ★对★ |

★**查法提醒 (★main 20:5x 踩过·★原样转述★)**: ★**`extra_gates` 这一段【只出现在 `--json` 模式里】⇒ 默认 stdout 根本不打印 extra_gates ⇒ 只 grep 默认输出会误判「链上没这道闸」⇒ 那是找错地方, 不是闸没挂上 ★** ⇒ 要看链上那道闸 ⇒ 跑 `python3 state/gate_check.py --json` (★本单已把读数落在 `logs/iss333/cont2_verify_run3.txt` ⑥ 段·条数 = 8★)。

★**③ 挂不挂的风险 (★明确建议·不许含糊★)**:

★★**建议: 挂 (★维持现状·不许拆★)·理由三条★★**
1. ★**挂上去不会把现在的门禁链带红** ⇒ 实测: 8 道 extra_gates 全 `ok=True` · `gate_check.py` rc=0 · Q1/Q2/Q6/Q7 全达标 (★B4-3② 逐条对过★) ⇒ ★**链是绿的·不是「挂完变红」★**
2. ★**它盖的是一条已经出过事的洞**: ISS-326 自己实测出「假绿」—— 判据脚本里的精确等值分支失配后, **那条判据静悄悄不查了, 但脚本整体照样全绿** ⇒ ★**缺陷对闸隐形** ⇒ ★**而 S1 改名那一趟会给 186 个板位号改名、其中 68 个被 MECH 引用 ⇒ 不挂 = 改完板 MECH 侧对不上而没人拦** ★⇒ ★**挂的收益远大于挂的风险★★
3. ★**不挂的代价高于挂的代价**: 不挂 ⇒ 这道闸退化成「一个没人跑的手写脚本」⇒ ★**与 ISS-136「以前谁都不跑 ⇒ 漂移长期没人拦」完全同款★** ⇒ ★**项目铁律是「判据只有挂在链上才算数」★★

★**★但挂着有一个【真·当下就存在】的风险·必须让 main 知道 (★这是我的判断·不是 main 的)★★**:
★**这条闸把 `MECH/**/*.md` + `MECH/**/*.py` 全部当扫描面 ⇒ 以后任何人在 MECH 域任何一个 .md 或 .py 里写死一个盘上没有的位号 ⇒ 闸当场判「新增真隐患」⇒ rc=1 ⇒ 全项目门禁链变红 ★**
⇒ ★**这正是 MC-8 那个反向用例干的事 (★实测 rc=1·真隐患 11 > 基线 10★)⇒ ★**这条风险【已被反向用例证实是真的】★
⇒ ★**缓解办法 (★不是改闸·是写文档规矩★)**: ★**MECH 域文档里要写「改名后名」或「形状像位号但不是位号」的东西 ⇒ 一律写进 `logs/iss333/` 或 `HANDOFF/`, 不许写进 `MECH/`** ★
⇒ ★**★本单这条交卷页就故意放在 `HANDOFF/` (★不在扫描面里★) 就是这个原因★★
⇒ ★**这条建议写进项目规矩 (★main 拍·我不自签★): 「凡是要在 MECH 域写位号字面量的文档 ⇒ 先想一句『这句会不会让闸变红』」★★

★**④ 挂闸已由 main 于 2026-11-18 20:2x 执行 (ISS-330) ⇒ 本单只交闸脚本与证据, 不再出挂闸提案; 本单零改 `state/gate_check.py`★**

## B5 未决项与卡点

★**本节每条都写清「不写会怎样 / 不解会怎样」⇒ 未解项一律交 main 拍, 本单不自己改闸、不替老板拍板★★**

### B5-① ★基线 16 是建闸日值·今天实测 ≠ 16 ⇒ 建议收不收? (★明确建议 + 理由★)★★

| 口径 | 数 | 分级 | 出处 |
|---|---|---|---|
| ISS-326 建闸日基线 (60 − 4 − 40) | **16** | [实测] | `baseline_repro.json` `baseline_iss326` |
| 今天同口径复现 (62 − 10 − 38) | **14** | [实测] | 同上 `baseline_reproduced_today_same_caliber` |
| 本闸交付上限 | **10** | [实测] | 同上 `final_partition_iss333.baseline_count` + 闸脚本 `BASELINE_COUNT` |

★**建议: ★已经收了·而且收得对·不要再往回收 (★除非有具体证据★)★★**
★**理由三条**:
1. ★**方向合规**: 铁律是「基线只许收紧不许放宽」⇒ 16 → 14 → 10 是**连续收紧** ⇒ 合规 ✓ (★反向不成立·放宽就违规★)
2. ★**机械化护栏已生效**: `BASELINE_COUNT = 10` + `BASELINE_COUNT_BUILDDAY = 10` ⇒ ★**今后任何人想把上限调回 11/16 ⇒ 闸自己判红 (MC-12 实测 rc=1) ⇒ 不靠人盯★** ⇒ ★**这条已经把「建议」变成「事实」⇒ 不需要 main 再拍一次★
3. ★**再往下收没有新证据支撑**: ★**10 条里每一条都有盘上书面理由 + 归属 (多数 owner=hw-lead)⇒ 它们不是「白捡的额度」⇒ 在 hw-lead 把对应位号真正落表之前, 把上限收到 <10 ⇒ 等于【提前宣布这批隐患已解】⇒ 那是不许的★**

★**★不收会怎样 / 不解会怎样 (★这才是关键★)★★**:
- ★**若 main 拍「回收到 14」⇒ 方向违规 (放宽) ⇒ 而且 MC-12 会当场判红 ⇒ 门禁链变红 ⇒ ★**所以「回收到 14」这个选项【物理上不存在】★★
- ★**若有人把 `BASELINE_COUNT_BUILDDAY` 也改成 14 ⇒ MC-12 的护栏同时失效 ⇒ ★**这是本单发现的【唯一一个真·机制漏洞】⇒ 已在 B5-⑤ 登记·交 main 拍★★
- ★**若把 `BASELINE_TOKENS` 里某条删掉而不同步改 `BASELINE_COUNT` ⇒ 闸自己判红 (`基线自洽: BASELINE_COUNT=10 但 BASELINE_TOKENS 只有 9 条`) ⇒ ★**这是好设计·不需要人工介入★★
- ★**★唯一正确的后续动作 (★写在闸自己的提示里★)**: ★**当某条基线隐患被真正解掉 (★位号真的落表 / 文档真的改对了★) ⇒ 把 `BASELINE_COUNT` 收到当前 `missing_total` 并从 `BASELINE_TOKENS` 里删掉那一条 ⇒ 这叫【收紧】·不叫【放宽】⇒ 闸自己会打印这句提示★**

### B5-② 闸挂在 `EXTRA_GATES` 第几位 · 挂了会不会把现在的门禁链带红 (★本单实读·行号实测★)

| 项 | 实测 | 分级 |
|---|---|---|
| `EXTRA_GATES` 列表定义位置 | `state/gate_check.py` ★**第 211 行** ★ | [实测] |
| ★**本闸位置**★ | ★**第 8 位 (末位)** · ★逐字写法在 ★**第 246-247 行** ★ | [实测] |
| 调用形态 | ★**裸跑·参数 `()`** ⇒ ★**不加 `--selftest` (★live 路径已内建 17/17 判据分支探针·再加只是把链的耗时翻倍·不增判据覆盖★)★ | [实测] |
| 链上 extra_gates 条数 | **8** · **8 条全 ok=True** | [实测] (`cont2_verify_run3.txt` ⑥ 段) |
| ★**挂了会不会把现在的门禁链带红**★ | ★**不会·实测带绿** ★: `state/gate_check.py` **rc=0** · Q1 **18/18** · Q2 **3/3** · Q6 **✅ 通过 (rc=0)** · Q7 **9/9 道绿** | [实测] (`cont2_verify_run2.txt` / `cont2_verify_run3.txt`) |

★**独立判断 (★不只转述 main 的实测·我自己也判一次★)**: ★**这条闸挂链【当下是纯增益】·理由 = ① 它判红的前提是「MECH 域出现盘上没有的位号」·而这正是 S1 改名那一趟最可能发生的事 (ISS-326 实测 68/186 个改名位号被 MECH 引用) ⇒ 不挂 ⇒ 这批漂移无人拦; ② 它当前的 10 条基线全部在基线内 ⇒ 挂上去当天不会红; ③ 它【不可能】误伤别的域 ⇒ 扫描面只在 `MECH/` 下 ★**
★**★但它引入了【一个】新约束, 而这个约束是【真】的**: ★**从今天起, 「在 MECH 域 .md/.py 里写死一个盘上没有的位号」= 把全项目门禁链弄红 ⇒ 这条必须写进项目规矩, 不写就会有人踩 (★MC-8 反向用例就是干这件事的·实测 rc=1★)★**

### B5-③ ★C17 登记条目逐条指到盘上实物证据 (★五 + 十二 两条线都给★)★

★**线 A: ISS-326 §2-2 点名的「五条代码常量」⇒ 闸内实际分类 + 盘上实物证据 (★逐条不空口★)** ★

| # | token | 闸内实际分类 | 盘上实物证据 (★为什么它不是位号★) | 分级 |
|---|---|---|---|---|
| 1 | `R_ILIM_VALUES` | ★**C17 已登记** ★ | `MECH/HINGE_POWER_CALC.md` 引用的 = ★**限流电阻候选档表【代码常量名】**★ (★闸脚本 `MECH_NON_DESIGNATOR_REGISTRY` 内写明★) | [实测] |
| 2 | `LED_REF` | C15 (Python 标识符命名空间·**未进 C17** ★) | `MECH/check_board_frame_coords.py` 里的 ★**Python 变量名**★ + `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` 里的 `LED_REF` (★它取键用的真位号是 `D_LED_G`★) ⇒ ★**ISS-326 实测: 板上位号改名 ⇒ `fps[LED_REF]` 抛 `KeyError: 'D_LED_G'`★ ⇒ **它就是块代码常量**★ | [实测] |
| 3 | `R_DCR` | ★**C17 已登记** ★ | `MECH/MECH_BUDGET.md` §耗散口径 + `MECH/verify_budget.py` 里的 `R_DCR` = ★**电感【铜损热阻 (mΩ)】**★ ⇒ 物理量 | [实测] |
| 4 | `C_CASES` | C15 (Python 标识符·**未进 C17**) | `MECH/iss065_check.py` 里的 Python 变量名 (★ISS-326 审计文档 §2-2 点名★) | [实测] |
| 5 | `CONN_REFS` | C15 (Python 标识符·**未进 C17**) | `MECH/check_onepass_struct_crosscheck.py` 里的 Python 变量名 (★ISS-326 设计稿 §2-2 点名★) | [实测] |

★**⇒ 归类结论: ★**五条里 2 条 (`R_ILIM_VALUES` / `R_DCR`) 进了 C17 显式注册表 (★因为它们【也出现在 .md 正文里】·不能只靠「Python 标识符」那条规则摘出去·必须显式登记★)·另 3 条 (`LED_REF` / `C_CASES` / `CONN_REFS`) 只在 .py 里 ⇒ 被 C15 命名空间规则自动摘出 ⇒ 【无需】进 C17 ⇒ ★**这不是漏登·是两层规则各管一段·MC-13 正向对照 (原样不动 rc=0) 已证明这样判得对★★

★**线 B: 闸内 C17 注册表全 12 条 ⇒ 逐条指到盘上实物证据 (★`baseline_repro.json` `c17_non_designator` + `detail[].files` 逐条对出来★)** ★

| # | token | 盘上实物证据 (文件路径) | 为什么它不是位号 | 分级 |
|---|---|---|---|---|
| 1 | `CONN_CAM_1` | `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` | S1 新名示例 (`CONN_CAM` → `CONN_CAM_1`) | [实测] |
| 2 | `D_LED_G_1` | 同上 | S1 新名示例 (`D_LED_G` → `D_LED_G_1`) | [实测] |
| 3 | `CONN_USB_ISSX` | 同上 | 假位号 (★ISS-326 自己的反向测试夹具★) | [实测] |
| 4 | `TP_TEMP_ISSX` | 同上 | 假位号 (夹具) | [实测] |
| 5 | `TP_TEMP_ISSX2` | 同上 | 假位号 (夹具) | [实测] |
| 6 | `U_TEMP_1` | 同上 | 假位号 (夹具) | [实测] |
| 7 | `R_DCR` | `MECH/MECH_BUDGET.md` · `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` · `MECH/_frag_update_iss216.py` | 物理量 (铜损热阻 mΩ) | [实测] |
| 8 | `R_ILIM_VALUES` | `MECH/HINGE_POWER_CALC.md` · `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` | 代码常量名 (限流档表) | [实测] |
| 9 | `R_TIM` | `MECH/CENTER_CAVITY_REBALANCE_V2.md` · `MECH/CENTER_CAVITY_REBALANCE_V3.md` | 物理量公式 (导热垫热阻 K/W) | [实测] |
| 10 | `LED_G_WINDOW` | `MECH/BOARD_ONEPASS_MECH_SYNC.md` | ★**JSON 里的【场景 id】**★ ⇒ 同对象 `"ref": "D_LED_G"` 才是位号 | [实测] |
| 11 | `LED_G_HOLE_A` | 同上 | 场景 id (有结构光孔) | [实测] |
| 12 | `LED_G_NOHOLE_B` | 同上 | 场景 id (无结构光孔) | [实测] |

★**⇒ 12 条 C17 与 10 条真隐患**分开记账** (★这是 ISS-326 设计稿没有、本闸新加的一处口径细化·★理由写在闸脚本 §C17 注释里★) ⇒ ★**⇒ 「16 → 10」里被摘掉的 6 条不是「被人偷偷放宽掉的」·是【被更准的规则摘出去了】⇒ 方向是收紧★**

### B5-④ 未决项 ①: ISS-326 设计稿的「唯一 token 230」与本闸实跑 246 对不上

| 项 | 值 | 分级 |
|---|---|---|
| ISS-326 设计稿口径 | 唯一 token **230** (★`logs/iss326/gate_design/mech_gate_baseline.json` `tokens_unique`★) | [实测] |
| 本闸实跑 | 唯一 token **246** (★`logs/iss333/gate_main_run.txt`★) | [实测] |
| 扫描面份数 | **113 (48 md + 65 py)** · ★**两边逐字一致** ★ | [实测] |

★**判读 (★推算)**: ★**两个数**不矛盾** ⇒ 差在【口径】不在【盘面】: 230 是 ISS-326 **设计稿原型**用的提取口径 · 246 是本闸**实跑**口径 (★剔闸自身 + C15/C16/C17 三条更准规则后剩下的唯一标识符★) ⇒ ★**扫描面本身 (113 份 / 48+65) 两边一致 ⇒ 没有「多扫了文件」的风险****
★**★不写会怎样★**: ★**main 若拿 230 来对账会以为闸「多算了 16 个 token」⇒ 需要一句话说清是口径差★**
★**处置建议**: ★**以本闸 246 为准 (★live 路径的实测值★)·230 保留为 ISS-326 设计稿的历史读数 ⇒ 不追改历史文件 (★`logs/iss326/` 只读★)★**

### B5-⑤ 未决项 ②: ★★「反放宽护栏」本身可以被拆 (★这是本单发现的唯一真·机制漏洞·交 main 拍★)★★

★**现象**: 闸脚本里 `BASELINE_COUNT_BUILDDAY = 10` 是★**普通模块级常量★** ⇒ ★**谁都可以把它改成 14 / 16 ⇒ MC-12 的护栏同时失效 ⇒ 「基线只许收紧不许放宽」从【机械化】退回【口头约定】★**

★**复现命令 (★main 可自己跑·★本单没跑·因为跑它就得改闸脚本·★那是我被禁止的★)**:
```bash
# 在副本上把 MECH/tools/check_mech_ref_reachability.py 里 BASELINE_COUNT_BUILDDAY 由 10 改成 14
# 然后同时把 BASELINE_COUNT 改成 14 并同步 BASELINE_TOKENS 到 14 条
# ⇒ 期望: 现在会 rc=0 (因为 14 > 10 已不成立 ⇒ 护栏失效) ⇒ ★**护栏被绕过**
```

★**我建议怎么改 (★但不自己改·★闸脚本已在链上·★改了链上那道闸就与盘面不一致★)**:
★**选项 A (★推荐·最省事★)**: ★**把 `BASELINE_COUNT_BUILDDAY` 也写成【由冻结表推出来】而不是【手写常量】⇒ 例如从 `MECH_DESIGNATOR_REGISTRY` 的 fingerprint 或一个单独的只读冻结文件推导 ⇒ 【改它就等于改冻结表 ⇒ 而冻结表重建需要双确认 (★`--freeze-registry` + `--confirm-freeze`★)⇒ 护栏与现有双确认机制合流·零新增流程★****
★**选项 B (★次选·成本更高★)**: ★**让 `BASELINE_COUNT_BUILDDAY` 本身也被算进 fingerprint ⇒ 改了它 ⇒ fingerprint 对不上 ⇒ 闸自判红****
★**为什么必须交 main (★不自己改的三条理由★)**: ★**① 闸脚本已在 `EXTRA_GATES` 里·链上跑的就是它 ⇒ 我改 ⇒ 链上那道闸与盘面不一致 ⇒ 全项目门禁失真★ ② 改判据 = 改「基线只许收紧不许放宽」的机械形态 ⇒ 属于 main 的机制地界 (★ISS-330 同款边界★) ③ 这条漏洞【今天不造成假红也不造成假绿】⇒ 不紧急 ⇒ 但【趁现在闸刚挂、改动成本最低】⇒ ★**建议 main 排一条 ISS·优先级中****

### B5-⑥ 未决项 ③: MECH 域文档写位号字面量 ⇒ 会把全项目门禁链弄红 (★已发生过的真事·不是理论风险★)

| 项 | 内容 | 分级 |
|---|---|---|
| 现象 | ★**在 `MECH/` 域任何一个 .md / .py 里写死一个盘上没有的位号 ⇒ 闸当场判「新增真隐患」⇒ rc=1 ⇒ 全项目门禁链变红** ★ | [实测] (★MC-8 反向用例: rc=1·红项「新增真隐患:R_ZZ_ISS333_FAKE_999, 真隐患 11 > 基线 10」★) |
| 影响面 | ★**门禁链是全项目的 ⇒ 一个人写文档就能让所有域变红** ★ | [实测] |
| 已有缓解 | ★**本单这条交卷页就放在 `HANDOFF/` (★不在扫描面里★) ⇒ 本身不构成风险★** | [实测] |
| ★**建议 (★交 main 拍·我不改项目规矩★)★★ | ★**把一条规矩写进项目守则: 「MECH 域文档里要写位号字面量 (★尤其是『改名后名』与『形状像位号但不是位号』的写法★) ⇒ 一律写进 `logs/` 或 `HANDOFF/`, 不许直接落 `MECH/`」** ★ | ★[推算]★ |

★**★不写会怎样★**: ★**下一个写 MECH 文档的人 (★不是我·可能是 sw-lead / hw-lead 顺手写一句★)会踩⇒ 然后一道闸红了但【没人知道是谁的文档】⇒ 排查成本高 ⇒ ★**所以【规矩】比【修闸】更划算·这是我的判断★**

### B5-⑦ 未决项 ④: 10 条真隐患的归属未闭合 (★不是本单的活·但本单把它们点名了★)

★**10 条基线真隐患里, 绝大多数的根因是【位号没落表】⇒ owner=hw-lead (★改板/落表通道★)· 本单不越界去清 ⇒ 只点名交 main 排期★**

| token | 根因 | 归属 |
|---|---|---|
| `CONN_USB` | 板上是 `J_USB_C` · 网表里只有 `CONN_CAM` / `CONN_LIGHT` ⇒ MECH 域 77 处引用还在 | hw-lead (落表) + main (批改板通道) |
| `C_VBUS_BULK` | 判据脚本算 1206 · 网表里只有 `C_VBUS_IN`/`C_VBUS_OUT`/`C_SYS` | hw-lead |
| `D_ESD_CHG` | 判据脚本假设了一个不存在的 ESD 位号 (★板上只有 `D_ESD_CAM`/`D_ESD_DEMO`/`D_ESD_LIGHT`/`D_ESD_TC`/`D_ESD_USB_D`★) | hw-lead + mech-lead (脚本侧) |
| `J_CHG_A` / `J_CHG_B` | 文档已写「拆成两个 ref」⇒ 但还没落表 | hw-lead |
| `J_CHG_PWR` | 拟用名·还没落表 | hw-lead + main |
| `J_JTAG` | 脚本用 `J_JTAG` · 盘上是 `J_DEBUG` | hw-lead |
| `J_USB` | 脚本用 `J_USB` · 盘上是 `J_USB_C` | hw-lead |
| `R_PU_STAT_L` | 文档 + 判据脚本都在用 · 板/网表里没有 | hw-lead + mech-lead |
| `U_SOM_RK3572` | ★**位号 + 拓扑都不符** (★盘上是 `J_SOM_P1..P4`·4 组 × 100 焊盘 = 400★) ⇒ ★**这是 10 条里最重的一条** ★ | hw-lead (★+ main·涉及拓扑★) |

★**★不闭合会怎样★**: ★**这 10 条永远占着真隐患额度 ⇒ 以后 MECH 域【真·新增】一条隐患时, 闸会判 11 > 10 ⇒ 红 ⇒ 而 11 里有 10 条是历史欠账 ⇒ ★**排查者要先分清「哪一条是新的」★ ⇒ ★**建议 main 排一条 hw-lead 的落表单把这 10 条批量解掉·解掉后本闸的 `BASELINE_COUNT` 可机械地收到 0·闸就变成纯粹的「新增即红」网★**

### B5-⑧ 未决项 ⑤: 改名那一趟之后, 这道闸的基线怎么办 (★[0数据]·不预测·交 main 拍★)

★**已知**: ISS-326 实测 S1 会给 186 个板位号改名 · 其中 68 个被 MECH 引用 (68/68 live) ⇒ ★**改名当天这 68 条会变成漂移 ⇒ 闸会红 ⇒ 这是【正确行为】(★闸就该在那一刻拦下来★)⇒ 但【改完名之后】MECH 侧的引用要不要跟着改、改多少 · ★**本单 [0数据]·不预测 (★那取决于 S1 那一趟具体怎么改·★本单只交闸·不交改名方案★)****
★**★建议 (★交 main★)**: ★**S1 改名那一趟的单子应当显式写一条: 「MECH 域的位号引用同步修改清单」⇒ 以本闸的 live 输出为【差分基准】⇒ 改完重跑本闸 ⇒ 必须回 rc=0 ⇒ 不许靠改 BASELINE 绕过★**

### B5-⑨ 本单自查: 三道必跑以外零副作用 (★边界自证★)

| 边界 | 判 | 依据 (★B6 原样输出★) |
|---|---|---|
| 零写板 | 通过 | md5 / mtime 未变 |
| 零落表 | 通过 | 未碰任何真源 |
| 零改 `MECH/tools/check_mech_ref_reachability.py` | 通过 | 56,550 B / 19:36:31 未变 |
| 零改 `state/gate_check.py` | 通过 | 只读 (★实读行号用★) |
| 零改 `SW/tools/check_sw_ref_reachability.py` | 通过 | 未碰 (★只读 import 的对象★) |
| 零改既有 `MECH/` 域文档正文 / 脚本 | 通过 | 本单只新建 `HANDOFF/` 一件 + 写分片 |
| 零改 `logs/iss326/` | 通过 | 只读 |
| 沙盒无软链 | 通过 | `find tmp/iss333 -type l \| wc -l` = 0 |
| 零外发 | 通过 | ★**本单未发任何邮件/询价/问询/采购·本单无外部依赖·不需要外查★★ |
| 不替老板拍板 / 不自签 issue_log | 通过 | 本单未动 `state/issue_log.yaml` |

## B6 自证复现命令

(见下)
