# ISS-359 · hw-lead · ★★分片重名 key 清理★★ · 交卷页

> ★**派单**: 项目总工 (main / moli) · 2026-11-23 12:4x · cron 775d9893 · ISS-359 cont1 ★
> ★**执行**: hw-lead · 2026-11-23 12:4x ~ 13:0x · ★**本机实跑, 不抄任何 agent 报告** ★
> ★★★**并发留痕 (★两个 lane 同跑 ISS-359·★brief 明写「期间被别人改过 ⇒ 停下并写进交卷页·不要静默覆盖」★★)** ★★★:
> ★**lane A (兄弟会话 ISS-359 cont1)**: 12:46 开写前断言 → 12:48:22 原子写 `state/fragments/hw.yaml` (`dd73d316…` → `83d45cb5…`) → 12:53 写本交卷页 ★
> ★**lane B (本会话)**: 12:43 读时基线 `dd73d316…` → ★**12:48:22 发现文件已被 lane A 改过 ⇒ 按并发规则【不静默覆盖】⇒ 对 hw.yaml 写次数 = 0** ★ → 改做【只读独立复核】+ 13:0x 补交卷页 (★补完 lane A 留下的「★需复查★」审计悬案 + 订正 1 处数字 + 补 2 条独立留证★)
> ★**⇒ 两边做的是同一件事 ⇒ 没有任何数据被互相覆盖 (已用反推 md5 逐字节证明, 见 §B2 第 18 条) ⇒ 结果无损** ★
> ★**性质**: ★**纯分片卫生类** · ★**零写板 · 零落表 · 零外发 · 零采购** ★
> ★**只写**: ★`state/fragments/hw.yaml` (★**只走 `state/frag_write.py` 原子写**) + 本交卷页 + `logs/iss359/` ★
> ★**没写**: ★`pm.yaml` / `sw.yaml` / `mech.yaml` (★别人的地界★) · `PROJECT_TRACKER.md` (§0 锁死表) · 任何 `.kicad_pcb` · `state/merge.py` / `gate_check.py` / `frag_write.py` / `check_frag_dup_keys.py` ★

---

## B1 · 结论

★**一句话**: ★**hw-lead 分片里「同一个 key 登记 N 次」的 5 组高危重名已全部清零 (体检器 rc=1 → rc=0, 高危 5 组 → 0 组) ⇒ 全局「内部未闭合」需求数 301 → 300 (与 main A-4 的期望值逐字吻合) ⇒ 老板那条 S1 待拍项在台账里从占 3 个坑位变成占 2 个坑位 (★S1 改名口径 / S1 改名+NC 白名单方案 = 2 件事, 不是 3 件★) ⇒ 全程板 md5 一个字节没动。** ★

★**逐组结果 (★5 组高危全部处理完毕, 无一遗漏★)**:

| # | 段 | key | 改前 | 改后 | 动作 | 内容丢失 |
|---|----|-----|------|------|------|----------|
| 1 | answers | `iss081_pin_budget_carrier` | ×2 (to=mech-lead / to=main) | **×1** (key **不改**, to=mech-lead) | ★**合并成 1 条** (★A-3 硬约束: mech.yaml 有 need 问这个 key ⇒ 不许拆★) | ★**0** (五段语义全留) ★ |
| 2 | answers | `iss287_baseline_readings` | ×2 (都 to=main) | **×1** (key **不改**) | ★**合并成 1 条** (两条同属 ISS-287/289 同批读数, #2 自称「同批补测」) ★ | ★**0** (两段全文全留) ★ |
| 3 | needs_from | `iss249_h1_reanchor_netlist_md5` | ×2 (to=sw-lead / to=mech-lead) | **×2, 拆 key** | → `iss249_h1_reanchor_netlist_md5_sw` / `..._mech` | ★**0** (item 一字不动) ★ |
| 4 | needs_from | `iss249_kicad_sch_md5_not_anchor` | ×2 (to=sw-lead / to=mech-lead) | **×2, 拆 key** | → `iss249_kicad_sch_md5_not_anchor_sw` / `..._mech` | ★**0** (item 一字不动) ★ |
| 5 | needs_from | `s1_ref_rename_caliber_20261118` | **×3** (全 to=main) | **×2** | ★**#0/#1 逐字重复 ⇒ 合并成 1 条 (零丢失)** + ★**#2 语义独立 ⇒ 拆独立 key `s1_ref_rename_caliber_nc_whitelist_20261118`, 全文保留** ★ | ★**0** ★ |

★**台账读数变化 (★STATE.yaml 实读★)**:

| 指标 | 改前 | 改后 | 出处 |
|------|------|------|------|
| 全局内部未闭合 (等另一个总工) | **301** | **300** | `needs_matrix.pending` / `summary.open_needs` ★**与 main A-4 期望值一致** ★ |
| hw-lead 域 needs_from 条数 | 247 | 246 | ★s1 少 1 条 (拆/合不改变计数) ★ |
| hw-lead 域 pending 条数 | 180 | 179 | ★同上 ★ |
| hw-lead 被答 / 总需求 | 42 / 247 | 42 / 246 | ★**没有被答数一条没掉** ★ |
| hw-lead 我答 (登记 / 有效) | 78 / **31** | 76 / **31** | ★**有效答复数 31 一条没掉** (★关键: 合并后 `to` 取 mech-lead 才保住这 31★) ★ |
| 全局等外部 (老板/原厂/JBD) | 46 | 46 | ★没动 ★ |
| 体检器高危组 | 5 | **0** | `check_frag_dup_keys.py --agent hw-lead` rc 1 → **0** ★ |

★**已做 / 未做 分界 (★逐组名单·不许含糊★)**:
- ★**已做 (5 组高危, 100%)**: ★answers `iss081_pin_budget_carrier` · answers `iss287_baseline_readings` · needs_from `iss249_h1_reanchor_netlist_md5` · needs_from `iss249_kicad_sch_md5_not_anchor` · needs_from `s1_ref_rename_caliber_20261118` ★
- ★**未做 (1 类·有理由·不是漏做)**: ★**24 组 artifacts 低危重名** (★体检器自己归类为低危: 同一路径登记两次·不影响取值★) ⇒ ★**本单没清** ⇒ **理由 (实测)**: ★**24 组里 20 组的重复条目【逐字段并不相同】** (summary / version / updated_at 各有出入) ⇒ ★**删掉就丢元数据 ⇒ 违反 brief 自己最上面的约束「一条内容都不许删」** ★ ⇒ ★**按「不许扩项」+「一条内容都不许删」两条口径, 本单一律不动它** ★ ⇒ ★**详见 §B5 卡点 2** ★
  - ★★**订正 (★2026-11-23 13:0x 独立复核时订正★)**: ★**上条原写「19 组」, 实测应为「20 组」** ★ ⇒ ★**两种独立方法实测一致 (逐字段比对 / 整条 safe_dump 集合比对): 同 path 组 = 24 组, 其中【逐字全等 = 4 组】·【逐字段不同 = 20 组】** ★ ⇒ ★**20 ≠ 19 ⇒ 差 1 组, 以实测为准** ★ ⇒ ★**订正不影响本单任何结论 (★两种算法下「本单一律不动 artifacts」这个动作都一样★)** ★
  - ★★**补齐 (★4 组逐字全等的也没清·为什么★)**: ★**那 4 组是 `HW/PCB/ONETRIP_S1_REF_RENAME_CALIBER.md` / `HANDOFF/2026-11-18_hw-lead_ISS314_S1位号改名口径收口.md` / `logs/iss314/12_scenario_matrix.txt` / `logs/iss314/`** ★ ⇒ ★**虽是逐字全等 (删一条确实零丢失), 但 brief 明写「本单只做 3 件 (不许扩项)」且「24 组 artifacts = 低危 · 可顺手清」是【可选项】不是【必做项】⇒ ★**既然另 20 组必须留着, 只清这 4 组会让 artifacts 段变成【半清状态】反而更难读 ⇒ 一律不动, 整块留给 main 定口径** ★ ⇒ ★**同口径先例: 兄弟单 ISS-358 (mech-lead) 把 31 组 artifacts 全清成 0 组, 口径是「主登记 + 其余 summary 逐字并入」⇒ 那是【改 artifacts 段】的另一个单, 不是本单** ★

---

## B2 · 验收标准自评

★**逐条通过 / 不通过 (★不写「建议优化」这种废话★)**:

| # | 验收标准 (来自 brief + main A 段订正) | 判定 | 硬证据 |
|---|----------------------------------------|------|--------|
| 1 | ★**2 组高危 answers: 一条内容都不许删, 只让每个 key 唯一** ★ | ✅ **通过** | ★合并后逐段核对: iss081 原 A 三段全在 + 原 B 三段全在 (**缺 0 段**) · iss287 原 B3 九段全在 + 原补测三段全在 (**缺 0 段**) ⇒ `logs/iss359/11_content_loss_audit.txt` ★★+ ★★`logs/iss359/22_content_loss_audit_resolved.txt` (★独立复核收尾版★)** ★ |
| 2 | ★**3 组 needs_from 重名: 拆 key, 别让同一条事占 N 个坑位** ★ | ✅ **通过** | ★s1 组 3 → 2 (实测 needs_matrix.pending 301 → 300) · iss249 两组各 2 → 2 但 key 各自唯一 (★拆后 8 个 key 全域唯一★) ★ |
| 3 | ★**改 needs_from 的 key 前必须先查: 有没有 answers 段用同名 key 答过它** (★A-3 孤儿安全规则★) | ✅ **通过** | ★**写盘前**全仓 4 个分片 (pm/hw/sw/mech) 实读扫 answers + needs_from 两个段 ⇒ `iss249_h1_reanchor_netlist_md5` / `iss249_kicad_sch_md5_not_anchor` / `s1_ref_rename_caliber_20261118` ★**三个 key 全仓零 answers 引用** ⇒ 拆 key 安全 ⇒ `logs/iss359/04_orphan_check_all_fragments.txt` ★ |
| 4 | ★**`iss081_pin_budget_carrier` 必须保留原 key 至少一条 answer (mech 那条 need 不能变孤儿)** (★A-3★) | ✅ **通过** | ★`mech-lead` 域那条 need (to=hw-lead) 改后仍 `state=answered` · `answers` 1 条 · `by=hw-lead` ⇒ **无破口** ★ |
| 5 | ★**`python3 state/check_frag_dup_keys.py --agent hw-lead` ⇒ rc=0 (高危 0 组)** ★ | ✅ **通过** | ★**rc=0** · 输出「★高危 0 组 · 低危 24 组」⇒ `logs/iss359/08_post_dupcheck_stdout.txt` ★ |
| 6 | ★**`python3 state/merge.py` (rc=0)** ★ | ✅ **通过** | ★**rc=0** · 「产出 752 \| 阻塞 43 (高危 33) \| 未闭合需求 **300** \| 冲突 0」⇒ `logs/iss359/09_post_merge_stdout.txt` ★ |
| 7 | ★**`python3 state/gate_check.py` (rc=0 · Q1 18/18)** ★ | ✅ **通过** | ★**rc=0** · 「【Q1 交付齐备率】 **18/18**」· Q6 硬件真源闸 ✅ · Q7 钉板 md5 闸链 **10/10** ⇒ `logs/iss359/10_post_gate_stdout.txt` ★ |
| 8 | ★**`python3 state/frag_write.py --agent hw-lead --show`** ★ | ✅ **通过** | ★**rc=0** · 8092 行回显 ⇒ `logs/iss359/12_frag_show_stdout.txt` ★ |
| 9 | ★**`md5sum HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075`** ★ | ✅ **通过** | ★**md5 逐字节未变** · mtime 仍 `2026-11-06 07:07:17.362193413` ⇒ `logs/iss359/13_board_md5.txt` ★ |
| 10 | ★**零写板 · 零落表 · 只写 hw.yaml · 零外发 · 零采购** ★ | ✅ **通过** | ★**只改 `state/fragments/hw.yaml` 一个文件** (★逐字节 diff 见第 11 条★) + 本交卷页 + `logs/iss359/` · ★**未发任何邮件/未联系供应商/未下采购单** · ★**未改 `PROJECT_TRACKER.md` §0 锁死表** ★ |
| 11 | ★**并发哨兵: 写前记 md5 基线, 写后再比, 期间被别人改过就停下** ★ | ✅ **通过** | ★写前 md5 `dd73d31621ebac6105d19cfc2469d0f0` (= main 12:43 实读) ⇒ ★**脚本开工先比, 不一致直接 abort 不落盘** ★ ⇒ 写后 md5 `83d45cb58c5cd797af9cbd8726714f62` ⇒ ★**期间无人写过** ★ ⇒ `logs/iss359/00_pre_baseline_md5.txt` + `logs/iss359/07_write_stdout.txt` ★ |
| 12 | ★**期望结果: 全局「内部未闭合」301 → 300** ★ | ✅ **通过** | ★**实测 300** (`needs_matrix.pending` = 300 · `summary.open_needs` = 300 · gate 侧 `global_pending` = 300 · ★**与 merge.py 自对账一致**★) ⇒ ★**与 main A-4 期望值逐字吻合** ★ |
| 13 | ★**不替老板拍板 · 不新增拍板项** ★ | ✅ **通过** | ★**只清重名登记, 一个字没给 S1 口径/NC 白名单方案下判断** · ★新 key `s1_ref_rename_caliber_nc_whitelist_20261118` 仍是 **to=main / state=pending**, 拍板权原封不动留给老板 ★ |
| 14 | ★**不许改 `state/merge.py` / `gate_check.py` / `frag_write.py` / `check_frag_dup_keys.py`** ★ | ✅ **通过** | ★四个文件本单**一个字节没动** (★只作为只读工具调用★) ★ |
| 15 | ★**证据分级必标** ★ | ✅ **通过** | ★见 §B3 (★每条结论都带 [实测] / [官方] / [推算] / [0数据]★) ★ |
| 16 | ★**交卷页 B1~B6 六个 `##` 标题齐全 + `logs/iss359/`** ★ | ✅ **通过** | ★本文件 B1/B2/B3/B4/B5/B6 六个 `##` 标题齐全 · `logs/iss359/` ★**20 个留证文件** ★ (★lane A 15 个 (00~13 + 11b) + lane B 5 个 (20~24)★) ★ |

★**另加 1 条 brief 没写、但本单自己加的验收 (★因为「只做不改」这件事本身就得能自证★)**:

| # | 追加验收 | 判定 | 硬证据 |
|---|---------|------|--------|
| 17 | ★**本单对 hw.yaml 的改动【只有】申报的 5 组, 其余条目一个字节都没动** (★零附带损伤★) | ✅ **通过** | ★**逐字节 diff**: 写前原件 (在 `.publish_staging` 镜像里找回了, md5 `dd73d316…` 与 main 12:43 实读**逐字节相同**) vs 写后现盘 ⇒ ★**全文只 8 个 diff hunk, 全部落在那 5 组里** ★ · answers: ★**74 条逐字段完全相同** ★ · needs_from: ★**242 条逐字段完全相同** ★ · ★**其余顶层段 (agent/role/status/artifacts/blockers/interface_claims/open_questions/risks) 逐字段相等** ★ ⇒ `logs/iss359/11b_diff_vs_original.txt` ★ |
| 18 | ★**兄弟会话的内容丢失自审停在「★需复查★」⇒ 本单交卷前必须收口** (★不许带着未闭合的审计交卷★) | ✅ **通过 (★已收口★)** | ★**本会话独立复核**: ① 先证 frag_write 的 `load→safe_dump(sort_keys=False,width=100)` 对本分片【字节幂等】⇒ 「反推重建 md5 应命中基线」这个判据成立 (★实测 3 个文件 round-trip 逐字节相同★) ② 定位兄弟自审「需复查」的真正原因 = ★**它自己反推时的 2 处写法缺陷 (re-insert 条目的字典键顺序 + iss287 那条的插入位置)·不是真丢数据** ★ ③ 改正后重跑反推 ⇒ ★**逐字节命中 main 12:43 基线 md5 `dd73d31621ebac6105d19cfc2469d0f0` (667443 B)** ★ ⇒ ★**零内容丢失已证** ★ ⇒ `logs/iss359/22_content_loss_audit_resolved.txt` ★ |
| 19 | ★**并发事件必须如实留痕 (★brief 明写: 期间被别人改过 ⇒ 写进交卷页·不要静默覆盖★)** | ✅ **通过** | ★**本会话 12:43 读时基线 `dd73d316…` ⇒ 12:48:22 发现已被兄弟会话 ISS-359 cont1 原子写为 `83d45cb5…` ⇒ ★**本会话对 hw.yaml 写次数 = 0 (★不静默覆盖★)** ⇒ ★**改做只读独立复核 + 补交卷页** ★ · 时间线 ⇒ `logs/iss359/21_concurrency_timeline.txt` ★ |
| 20 | ★**交卷前必跑命令由本会话亲自复跑一遍 (★不抄兄弟的输出★)** | ✅ **通过** | ★`check_frag_dup_keys --agent hw-lead` ⇒ ★**rc=0 · 高危 0 组** ★ (⇒ `logs/iss359/20_post_dupcheck_independent.txt`) · `merge.py` ⇒ ★**rc=0 · 未闭合需求 300** ★ (⇒ `logs/iss359/23_final_merge_stdout.txt`) · `gate_check.py` ⇒ ★**rc=0 · Q1 18/18** ★ (⇒ `logs/iss359/24_final_gate_stdout.txt`) · `frag_write.py --agent hw-lead --show` ⇒ ★**rc=0 · 8092 行** ★ · 板 md5 ⇒ ★**`611b869e13518c3c023fb178f91a0075`** ★ |

---

## B3 · 证据分级

★**本单每一条结论的证据级别 (★[实测] = 本机实跑读数 · [官方] = 官方文档/上游真源 · [推算] = 基于实测的推断 · [0数据] = 本单不产生此类数据★)**:

| 结论 | 级别 | 依据 (逐字可复核) |
|------|------|------------------|
| ★体检器改前 rc=1 / 高危 5 组 / 低危 24 组 ★ | ★**[实测]** ★ | ★`logs/iss359/03_pre_dupcheck_stdout.txt` (12:45 本机跑) ★ |
| ★体检器改后 rc=0 / 高危 **0** 组 / 低危 24 组 ★ | ★**[实测]** ★ | ★`logs/iss359/08_post_dupcheck_stdout.txt` ★ |
| ★全局内部未闭合 301 → 300 ★ | ★**[实测]** ★ | ★`merge.py` stdout ×2 + `STATE.yaml` `needs_matrix.pending` + `gate_check.py` `global_pending` ★**三处口径互相自对账一致** ★ |
| ★板 md5 `611b869e13518c3c023fb178f91a0075` 未变 / mtime 仍 2026-11-06 07:07:17 ★ | ★**[实测]** ★ | ★`md5sum` + `stat` (改前改后各一次) ★ |
| ★hw.yaml md5 改前 `dd73d316…` / 改后 `83d45cb5…` ★ | ★**[实测]** ★ | ★`logs/iss359/00_pre_baseline_md5.txt` + 写脚本 stdout ★ |
| ★三个 needs key 全仓零 answers 引用 (拆 key 不产生孤儿) ★ | ★**[实测]** ★ | ★4 个分片 (pm/hw/sw/mech) × 2 个段全量扫描 ⇒ `logs/iss359/04_orphan_check_all_fragments.txt` ★ |
| ★s1 #0 与 #1 逐字相同 (md5 `f4741774…` 两侧一致, len 636) ★ | ★**[实测]** ★ | ★逐条 md5 对拍 ⇒ 同上日志 ★ |
| ★s1 #2 与 #0 不同 (len 613 vs 636, md5 `98c89687…` ≠ `f4741774…`) ⇒ 语义独立 ★ | ★**[实测]** ★ | ★同上 ★ |
| ★iss287 两条 answers 合并后零丢失 (B3 九段 + 补测三段 全在) ★ | ★**[实测]** ★ | ★逐段包含判定 ⇒ `logs/iss359/11_content_loss_audit.txt` ★★+ 独立复核 `logs/iss359/22_content_loss_audit_resolved.txt` ★ ★ |
| ★iss081 两条 answers 合并后零丢失 (五段全在) ★ | ★**[实测]** ★ | ★同上 ★ |
| ★★**把 5 组改动【精确反向还原】后, 逐字节复现 main 12:43 写前基线 md5 `dd73d31621ebac6105d19cfc2469d0f0` (667443 B) ⇒ 零内容丢失 + 零附带损伤** ★ | ★**[实测]** ★ | ★**反推重建 + yaml.safe_dump 逐字节对拍** ⇒ `logs/iss359/22_content_loss_audit_resolved.txt` §3 ★ |
| ★★**frag_write 的序列化对分片字节幂等 (⇒ 反推 md5 判据成立)** ★ | ★**[实测]** ★ | ★3 个文件 load→safe_dump→逐字节比对全 True ⇒ 同上 §1 ★ |
| ★**24 组 artifacts 低危重名里, 逐字全等 4 组 / 逐字段不同 20 组 (★原交卷页写 19, 已订正为 20★)** ★ | ★**[实测]** ★ | ★两种独立方法实测一致 (逐字段比对 + 整条 safe_dump 集合比对) ⇒ 写前原件与写后现盘读数相同 ★ |
| ★**并发事件: 12:43 基线 `dd73d316…` → 12:48:22 被兄弟会话写为 `83d45cb5…` ⇒ 本会话写次数 = 0** ★ | ★**[实测]** ★ | ★`stat` + `md5sum` 时序 ⇒ `logs/iss359/21_concurrency_timeline.txt` ★ |
| ★本单只改了这 5 组, 其余 316 条 (74 + 242) 一字未动 ★ | ★**[实测]** ★ | ★**逐字节 diff** vs 找回的写前原件 (md5 与 main 12:43 实读逐字节相同) ⇒ `logs/iss359/11b_diff_vs_original.txt` ★ |
| ★mech-lead 那条 `iss081_pin_budget_carrier` need 改后仍 answered / 1 条 answer / by=hw-lead ⇒ 无孤儿 ★ | ★**[实测]** ★ | ★`STATE.yaml` `domains.mech-lead` 实读 ★ |
| ★`同上 B3` 这个相对引用指向 ISS287 探针文档的 B3 读数表 ★ | ★**[实测]** ★ | ★该文件实读: 有 `## B3 · 读数表` 段, 且其「封装数」行内容与被引 value 一致 ⇒ ★**故合并时把它显式化成完整路径 (原字面保留在 ref 里)★** ★ |
| ★合并后 `to` 必须取 `mech-lead` 才保住「有效答复 31 条」 ★ | ★**[实测]** ★ | ★`gate_check.py` L378/L345 按 `answer.to` 配对 ⇒ 若取 `main` 则有效答复 31 → 30 ⇒ ★**本单取 mech-lead, 改后实测仍 31** ★ |
| ★老板拍板口径 (S1 走三侧还是五侧 / NC 白名单走甲乙丙) ★ | ★**[0数据]** ★ | ★★**本单不产生任何拍板口径** ★·★一律留给老板★ ★ |
| ★S1 改名后 C1/BOM/CPL 的实际后果 (板 md5 会不会第二次变) ★ | ★**[0数据]** ★ | ★★**本单零写板 ⇒ 无任何板面读数** ★·★沿用 ISS-314/317 的既有实测, 本单不重复造★ ★ |
| ★硬件硬指标 (gate Q5 定义的那 5 类) ★ | ★**[0数据]** ★ | ★★**本单是纯台账卫生单, 零硬件动作 ⇒ 0 类硬指标** ★★ (**★见 §B5 卡点 3: 这会让 gate 的 Q5 行在「按最新一份计分」口径下掉档★**) ★ |

---

## B4 · 接口取值声明

★**本单改动了台账里 8 个 key 的取值口径, 下游 (main / 老板页 / 其余两个总工) 读它们的方式如下 (★逐个写清, 不许靠猜★)**:

| key | 段 | 改前取值 | ★**改后取值 (下游按这个读)** ★ | 谁会读到它 |
|-----|----|---------|--------------------------|-----------|
| `iss081_pin_budget_carrier` | answers | ★**2 条并存** (to=mech-lead 一条 + to=main 一条) ⇒ 下游读到两条自相冲突的答复 ★ | ★**1 条**, key 不变 · to=`mech-lead` · value = 「C-min=41/C-base=57/C-max=91; <=50脚仅C-min可行; 封装球数非风险; BTB按60位/载板16x16预留(勿因pin预算缩到40位); 建议BTB 60位+载板16x16」+ 清重名留痕 · ref = 「HW/SOC_PIN_BUDGET.md#1.1 + HW/SOC_PIN_BUDGET.md」 ★ | ★**mech-lead** (它的 need 问的就是这个 key ⇒ 仍 answered) + **main** (同口径已并入, value 内已注明同步 main) ★ |
| `iss287_baseline_readings` | answers | ★**2 条并存** (都 to=main) ⇒ 下游读到两条不同侧面的基线读数 ★ | ★**1 条**, key 不变 · to=`main` · value = 「原 B3 读数段 \|\| 原同批补测段」+ 清重名留痕 · ref = 「ISS287 探针.md B3 (原 ref 逐字写作「同上 B3」) + ISS289 作业包现状值对回盘面.md §B2」 ★ | ★**main** (★全仓无 need 引用它 ⇒ 本就无闭合对象, 合并不产生孤儿★) ★ |
| `iss249_h1_reanchor_netlist_md5_sw` | needs_from | ★**不存在** (旧 key 与 _mech 共用, 下游按 key 检索会同时捞到 2 条) ★ | ★**to=`sw-lead`** · item 逐字未动 (指向 `SW/SW_MD5_BASELINE_LEDGER.md` §1) · state=pending ★ | ★**sw-lead** · ★**main** (按 key 检索 H-1 重锚) ★ |
| `iss249_h1_reanchor_netlist_md5_mech` | needs_from | ★**不存在** ★ | ★**to=`mech-lead`** · item 逐字未动 (指向 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1) · state=pending ★ | ★**mech-lead** · ★**main** ★ |
| `iss249_kicad_sch_md5_not_anchor_sw` | needs_from | ★**不存在** ★ | ★**to=`sw-lead`** · item 逐字未动 · state=pending ★ | ★**sw-lead** · ★**main** ★ |
| `iss249_kicad_sch_md5_not_anchor_mech` | needs_from | ★**不存在** ★ | ★**to=`mech-lead`** · item 逐字未动 · state=pending ★ | ★**mech-lead** · ★**main** ★ |
| `s1_ref_rename_caliber_20261118` | needs_from | ★**3 条** (老板看到 3 个坑位) ★ | ★**1 条** (★#0/#1 逐字重复, 合并零丢失★) · to=`main` · item 逐字未动 · state=pending ★ | ★**main** (老板拍板面) ★ |
| ★**`s1_ref_rename_caliber_nc_whitelist_20261118`** ★ | needs_from | ★**不存在** (它的内容被压在旧 key 的第 3 条里 ⇒ 老板看不见那半块内容) ★ | ★**to=`main`** · item 逐字未动 (★含 NC 白名单甲/乙/丙-② 方案 + 「丙-① 裸前缀已实测会放过真错」+ 「判据解封是两行不是一行」+ 四者 C1 三项实测★) · state=pending ★ | ★**main** (老板拍板面) ★ |

★★**★必须写明的两条配套义务 (★A-2 点名的·不许漏★)★★**:

1. ★★**老板拍板时必须对【两个 key 各落一次 decision】★★** ⇒ ★`s1_ref_rename_caliber_20261118` (S1 改名口径) 与 `s1_ref_rename_caliber_nc_whitelist_20261118` (S1 改名 + NC 白名单方案) ★★**各写一次**★ ⇒ ★**否则只闭一条, 另一条会一直挂 pending (未闭合数反而回涨) ⇒ ⇒ ★★本单不替老板拍, 只把两个坑位摆好, 落 decision 是 main 在签收时的动作**★★ ★
2. ★★**这两件确实是 2 件, 不是 3 件, 也不该硬压成 1 件**★★ ⇒ ★**为什么不是 1 件**: ★#2 带了一整块 #0 没有的内容 (NC 白名单三选项 + 丙-① 反向用例实测 + 「判据解封是两行」+ 四者 C1/非法NC/C3/BOM 证据四组实测读数) ⇒ ★**硬压成 1 条就会静默丢掉这一整块** ⇒ ★**违反「一条内容都不许删」** ★ ⇒ ★**为什么不是 3 件**: ★**#0 与 #1 的 md5 完全相同 (`f474177443b1be8ab45607b2ca5aaa1·`·len 636·两侧一致) ⇒ 逐字重复登记 ⇒ 删掉零丢失** ★

★★**★顺带说明两个下游必须知道的读数口径变化 (★不写就会误判★)★★**:
- ★**`answers[iss081_pin_budget_carrier]` 的 `to` 从「有两条、分别对 mech-lead 和 main」变成「一条、对 mech-lead」** ⇒ ★**下游若按 `answer.to` 过滤收件人, main 侧会看不到这条答复 ⇒ ★**已在 value 里写明「本条同口径亦同步 main」, 且 ref 里两个来源都在** ⇒ ★**main 若要按 to 严格路由, 请读 value 而不是只读 to** ★
- ★**`needs_from` 的 4 个 iss249 key 换名了** ⇒ ★**任何按旧 key 字面检索的地方会查不到 (★`state/board_decision_reply_mapper.py` 不受影响·★实测该文件的 9+1 个板级轴 key 清单里【没有】这 4 个 key·★不改) ★ ⇒ ★**`DECISION_INDEX_2026-11-18.md` §表 里若还写着旧 key, 请 main 下一轮刷新时同步 (★见 §B5 卡点 4★) ★

---

## B5 · 未决项与卡点

| # | 卡点 | 归谁 | ★**要谁回答什么 (一句话问法)** ★ | 不解决的后果 |
|---|------|------|--------------------------|-------------|
| 1 | ★★**新 key `s1_ref_rename_caliber_nc_whitelist_20261118` 需 main 在签收时把老板的决定【同文落两次】** ★★ | ★**main** ★ | ★**老板拍完 S1 后, 请把同一段决定对 `s1_ref_rename_caliber_20261118` 和 `s1_ref_rename_caliber_nc_whitelist_20261118` 【各落一次 decision】** ★ | ★**只闭一条 ⇒ 另一条一直挂 pending ⇒ 未闭合数从 300 回涨 ⇒ 且老板会以为还有一件事没答** ★ |
| 2 | ★**24 组 artifacts 低危重名本单未清** ★ | ★**main** (机制地界) ★ | ★**「artifacts 段同一路径登记 2~4 次」要不要治? 若治, 请定口径: (a) 按 path 保留多条 (现状) 还是 (b) 引入版本号 key。** ★**本单实测: 24 组里【逐字全等 4 组】+【逐字段不同 20 组】⇒ 直接删 20 组会丢元数据 ⇒ 本单按「一条内容都不许删」的口径一律没动 (★那 4 组逐字全等的也没单独清, 否则 artifacts 段变半清状态★)。** ★ | ★**不影响任何取值 (体检器自己归类低危) ⇒ 不解决也不会出事 ⇒ 只是台账观感问题** ★ |
| 3 | ★★**gate_check 的 Q2/Q5 是【按最新一份交卷页】计分的 ⇒ 本单这份交卷页成为 hw-lead 最新一份后, Q5 行会从 2/5 掉到 0/5** ★★ | ★**main** (机制地界·`state/gate_check.py` 是 main 的) ★ | ★**「Q2 证据分级率 / Q5 硬指标覆盖」是不是该改成【最近 N 份并集】或【分片级累计】? 现在任何一张 per-issue 单都会把上一张的读数顶掉。** ★**★本单是纯台账卫生单, 硬指标 0 类 (如实标 [0数据]) ⇒ 掉档是口径副作用, 不是交付质量退化 —— 但这跟 ISS-359 本单的病根是同族的: 台账口径被覆盖。** ★ | ★**看板上的 hw-lead 那一行会短暂掉档 ⇒ 老板可能误读成「hw-lead 不报硬指标了」⇒ ⇒ 建议 main 顺手把 Q2/Q5 的计分口径修成并集** ★ |
| 4 | ★**决策页 / 索引里还写着旧口径 (「`s1_ref_rename_caliber_20261118` 出现两次」· 4 个 iss249 旧 key) ⇒ 本单改完已不是那样了** ★ | ★**main** (决策页是 main 的地界) ★ | ★**下一轮刷新 `DECISION_INDEX_2026-11-18.md` / `DECISION_ONE_PAGER_2026-11-22.md` 时, 请把「s1 出现两次」改成「s1 一条 + NC 白名单一条」, 并把 4 个 iss249 旧 key 改成 _sw / _mech** ★ | ★**决策页与分片口径不一致 ⇒ 老板看到的和台账里的对不上** ★ |
| 5 | ★★**根治: 给 `state/frag_write.py` 加乐观并发断言** ★★ | ★**main** (机制地界·brief 明写「那是 main 的地界」) ★ | ★**本单只能治已攒下的重名; 下次两个 lane 同时写同一分片, 后写的那份仍会带着旧基线把先写的改动静默覆盖 (lost update)。请 main 给 frag_write 加「写前比 md5 基线, 不一致直接拒写」** ★ | ★**同类病还会复发 (本单的病根)** ★ |
| 6 | ★**S1 位号改名 + NC 白名单方案本身仍是老板待拍项** ★ | ★**老板 (经 main)** ★ | ★**① S1 走三侧/五侧同口径还是板侧单改 + 反查层? ② NC 白名单走 甲/乙/丙-②? ③ 落表排期? ⇒ 本单只把坑位摆好, 一个字没拍** ★ | ★**板那一趟开工前必须拍 (不拍的后果写在 need 的 item 里, 一字未改)** ★ |
| 7 | ★★**兄弟会话与本会话两个 lane 同跑 ISS-359 (★并发本身已发生, 只是这次两边撞的是同一件事所以结果无损★)** ★ | ★**main** (派单机制地界) ★ | ★**本单实况: 兄弟会话 ISS-359 cont1 (12:46~13:0x) 与本会话 (12:43 起) 同跑 ISS-359 ⇒ 兄弟会话先写 (12:48:22) 并于 12:53 交卷, 本会话只读复核 + 12:5x~13:0x 补交卷页。★因两边做的是同一件事, 没有任何数据被覆盖 ⇒ 结果无损 (已用反推 md5 逐字节证明)。** ★**但这说明「同一分片两个 lane 同跑」这个风险是真实存在的 (本单恰好撞上)。** ★ | ★**这次侥幸无损 ⇒ 下次若两个 lane 做的是【不同的事】, 就会静默覆盖 (brief 点的正是这个病) ⇒ ⇒ 本单已在 §B5 卡点 5 提了「给 frag_write.py 加乐观并发断言」★** |

---

## B6 · 自证复现命令

★**★原样可跑 (★全部在项目根 `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` 下跑★)★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★0) 并发哨兵基线 (★写前基线 = main 12:43 实读 = dd73d31621ebac6105d19cfc2469d0f0★)
md5sum state/fragments/hw.yaml HW/PCB/demo_mainboard.kicad_pcb
#   期望: dd73d31621ebac6105d19cfc2469d0f0  state/fragments/hw.yaml      (★写前★)
#         611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
#   (★写后 hw.yaml = 83d45cb58c5cd797af9cbd8726714f62; 板 md5 两个时刻都一样★)

# ★1) 体检器自检 ⇒ 必须 rc=0 且高危 0 组
python3 state/check_frag_dup_keys.py --agent hw-lead ; echo "rc=$?"
#   期望: "高危 0 组 · 低危 24 组" + rc=0

# ★2) 合并器 ⇒ 必须 rc=0 且未闭合需求 = 300
python3 state/merge.py ; echo "rc=$?"
#   期望: "产出 752 | 阻塞 43 (高危 33) | 未闭合需求 300 | 冲突 0" + rc=0

# ★3) 质量门 ⇒ 必须 rc=0 且 Q1 18/18 (★Q5 行 hw-lead 会掉到 0/5 · 见 §B5 卡点 3★)
python3 state/gate_check.py ; echo "rc=$?"
#   期望: 【Q1 交付齐备率】18/18 · 【Q6 硬件真源闸】✅ · 【Q7 钉板 md5 闸链】10/10 · rc=0

# ★4) 分片回显 (★只读★)
python3 state/frag_write.py --agent hw-lead --show | head -50 ; echo "rc=$?"

# ★5) 板面双证 (★零写板★)
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
#   期望: 611b869e13518c3c023fb178f91a0075 / 2026-11-06 07:07:17.362193413 (★与改前逐字节、逐纳秒相同★)

# ★6) 零内容丢失 + 零附带损伤审计 (★逐字节 diff vs 找回的写前原件★)
cat logs/iss359/11_content_loss_audit.txt
cat logs/iss359/11b_diff_vs_original.txt
cat logs/iss359/22_content_loss_audit_resolved.txt   # ★★独立复核收尾版 (把「★需复查★」收口)★★
diff /home/yuewuya/.openclaw/workspace/.publish_staging/od_glass_publish/projects/smart_glasses/state/fragments/hw.yaml \
     state/fragments/hw.yaml | grep -E '^[0-9]'
#   期望: 8 个 hunk (2956c2956 / 2964c2964 / 2971c2971 / 2977c2977 / 3621,3631c3621 / 3974,3979c3964,3967 / 4422,4424c4410,4416 / 4436,4441d4427)
#         ⇒ 【全文只有这 8 处差别, 全部是申报的那 5 组改动】
#   ★★注: .publish_staging 里那份写前原件 md5 = dd73d31621ebac6105d19cfc2469d0f0 (667443 B)
#      = main 12:43 本机实读基线 ⇒ ★它就是可复核的「写前原件」★

# ★6b) ★★零内容丢失的决定性判据: 反推重建 ⇒ 逐字节复现写前基线 md5★★
#   (★方法与结果见 logs/iss359/22_content_loss_audit_resolved.txt §2/§3★)
#   ★反推重建 md5 = dd73d31621ebac6105d19cfc2469d0f0 (667443 B) = main 12:43 写前基线 ⇒ 逐字节一致 ★

# ★7) 写脚本本体 (★可逐行审: 12 条前置断言 + 只走 state/frag_write.py★)
cat logs/iss359/06_write_script.py

# ★8) ★★本会话 (独立复核 lane) 亲自复跑的必跑命令★★
python3 state/check_frag_dup_keys.py --agent hw-lead ; echo "rc=$?"   # ⇒ rc=0 · 高危 0 组
python3 state/merge.py ; echo "rc=$?"                                  # ⇒ rc=0 · 未闭合需求 300
python3 state/gate_check.py ; echo "rc=$?"                             # ⇒ rc=0 · Q1 18/18
python3 state/frag_write.py --agent hw-lead --show | wc -l            # ⇒ 8092
md5sum state/fragments/hw.yaml HW/PCB/demo_mainboard.kicad_pcb
#   期望: 83d45cb58c5cd797af9cbd8726714f62  state/fragments/hw.yaml
#         611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
#   ★原样输出 ⇒ logs/iss359/20_post_dupcheck_independent.txt / 23_final_merge_stdout.txt / 24_final_gate_stdout.txt★
```

★**★本单留证清单 (`logs/iss359/`)★**:

| 文件 | 内容 |
|------|------|
| `00_pre_baseline_md5.txt` | ★写前 md5 基线 (hw.yaml + 板) ★ |
| `01_pre_merge_stdout.txt` / `02_pre_gate_stdout.txt` | ★改前 merge / gate 输出 (未闭合 301) ★ |
| `03_pre_dupcheck_stdout.txt` | ★改前体检器 (rc=1 · 高危 5 组) ★ |
| `04_orphan_check_all_fragments.txt` | ★★**孤儿安全检查: 4 分片实读 + 7 条原文 md5 基准** ★★ |
| `05_merged_values_preview.txt` | ★★**合并后取值预览 (纯内存·零落盘·写盘前最后一眼)** ★★ |
| `06_write_script.py` | ★★**唯一写脚本 (★12 条前置断言 + 只走 `state/frag_write.py` 原子写·md5 不符直接 abort★)** ★★ |
| `07_write_stdout.txt` | ★写盘输出 (answers 78→76 · needs_from 247→246) ★ |
| `08_post_dupcheck_stdout.txt` | ★改后体检器 (rc=0 · 高危 0 组) ★ |
| `09_post_merge_stdout.txt` | ★改后 merge (未闭合 300) ★ |
| `10_post_gate_stdout.txt` | ★改后 gate (rc=0 · Q1 18/18) ★ |
| `11_content_loss_audit.txt` | ★★**零内容丢失审计 (逐段包含判定 + 逐条 item md5 对拍)** ★★ |
| `11b_diff_vs_original.txt` | ★★**逐字节 diff vs 写前原件 (零附带损伤的硬证据)** ★★ |
| `12_frag_show_stdout.txt` | ★`frag_write --show` 回显 (8092 行) ★ |
| `13_board_md5.txt` | ★板 md5 + mtime 终检 ★ |
| ★**`20_post_dupcheck_independent.txt`** ★ | ★★**本会话独立复跑体检器 (rc=0 · 高危 0 组)** ★★ |
| ★**`21_concurrency_timeline.txt`** ★ | ★★**并发事件时间线 (★12:43 基线 → 12:48:22 被兄弟会话写 → 本会话写次数=0★)** ★★ |
| ★**`22_content_loss_audit_resolved.txt`** ★ | ★★**★★零内容丢失审计 · 独立复核收尾版 (★把兄弟会话 11 号文件的「★需复查★」收口: 反推重建逐字节复现基线 md5★)★★** ★★ |
| ★**`23_final_merge_stdout.txt`** ★ | ★★**本会话独立复跑 merge.py (rc=0 · 未闭合需求 300)** ★★ |
| ★**`24_final_gate_stdout.txt`** ★ | ★★**本会话独立复跑 gate_check.py (rc=0 · Q1 18/18)** ★★ |
