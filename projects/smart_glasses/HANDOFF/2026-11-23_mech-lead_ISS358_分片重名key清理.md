# ISS-358 · mech-lead · 分片重名 key 清理 (cont1) · 纯分片 · 零写板

> 执行者: 结构总工 (mech-lead) · 2026-11-23 09:5x → 10:1x
> 权威 brief: `state/dispatch_briefs/ISS-358_mech_frag_dup_keys_cleanup_cont1.md`
> 续做说明: cont0 (会话 `3cb7cedd-c2af-42ec-adbb-8ece67227c96`) 死于 LLM idle timeout ⇒ 零交付物; 本趟从零做, 按 brief 已订正的口径直接干活, 未重新论证前提
> 边界: 零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 未变) · 零落表 (网表/脚表/BOM/原理图/任何闸一个字没动) · 只写 `state/fragments/mech.yaml` (全程只走 `state/frag_write.py`) · 零外发/零采购 · 不替老板拍板 · 不改 `state/merge.py` / `gate_check.py` / `frag_write.py` / `check_frag_dup_keys.py`

---

## B1 结论

**一句话**: 把 mech.yaml 分片里 4 组高危重名 answers 拆成语义独立的 key (8 条改 key, value/to/ref 一字未改) + 把 31 组同 path 的 artifacts 重复登记并成一条 (47 条被并入, summary 逐字保留, 一字未删) ⇒ **mech-lead 分片高危重名 4 组 → 0 组, 低危 32 组 → 0 组, 体检器 rc=1 → rc=0**; **未闭合需求数我的净影响 = 0** (反事实实测, 见 B2)。

### B1.1 ★机制订正 (本单不作废的那一半)★ — 危害是真的, 但走的不是原 brief 说的那条路

- **已作废**: 「合并器只认第一条 ⇒ 后写的对下游不可见」。本机实读 `state/merge.py:295` = `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]` ⇒ **收集全部匹配的**, 5 条答案一条没丢; 全仓扫「取第一条」的消费者 ⇒ **零命中**。⇒ **本交卷页不写这句话**。
- **真实机制 (2-A) 存在性判定 ⇒ 静默错闭合**: 三处平行实现口径一致 — `state/gate_check.py:440` / `state/stage_gate.py:138` / `state/decision_truth.py:164` 都是 `bool(to) and to in (answers_by_key.get(k) or [])` ⇒ **只要被问的那个 agent 名下存在【任意一条】该 key 的答案, 这条 need 就判「已答」, 哪怕那条答的是完全另一个问题**。本机实证: `hw.yaml` 的 need `pcb_outline_confirm` (to=mech-lead) 问的是「PCB 外形 50x12mm 确认 + 器件发热分布 + NTC 位置 / 散热路径」, 而它能被闭合的那条答案**只答了 PCB 外形**。
- **真实机制 (2-B) 一个 key 装 N 个主题 ⇒ 下游无法分辨哪条答了哪个问题**: `pcb_outline_confirm` 5 条分别讲 ①PCB 50×12mm 厚 0.8/1.0 ②镜脚内腔需求 ③摄像头安装 ④散热接触路径 ⑤M-FIT 结果; `ntc_placement` 3 条讲 ①NTC 贴哪 ②持续功耗上限/结温档位 ③结构侧硬约束 ⇒ 任何「按 key 取答案」的读者拿到的都是一锅粥 ⇒ 这就是「板框口径到处飘」的技术根因之一。
- ⇒ **本单该做, 理由是上面两条, 不是「后写覆盖前写」**。

### B1.2 ★第二处订正 (brief 未提, 但我实测到)★ — artifacts 那 31 组**不是**「同一条登记了两次」

- brief 说这 31 组「key 也全相同 ⇒ 是同一条登记了两次, 不是两条不同登记撞一个 path」。**实测不成立**: `check_frag_dup_keys.py` 对 artifacts 段的 key 取值是 `e.get("key") or e.get("id") or e.get("path")`, 而 mech.yaml 的 230 条 artifacts **一条都没有 `key`/`id` 字段** (字段只有 path/kind/summary/updated_at/version) ⇒ 体检器实际是**按 path 分组**; 逐条比对后: **31 组共 78 条, 按 (path, kind, version, updated_at, summary) 逐字比对 ⇒ 逐字相同的副本 0 条** ⇒ 这 31 组是 **31 组「不同 issue 对同一文件的独立增量登记」撞一个 path**, 不是重复登记。
- ⇒ 我**没有照 brief 的字面做法删掉 47 条** (那会删掉 47 条真内容, 违反「一条内容都不许删 / 不许静默丢」), 而是**合并**: 每个 path 保留 1 条主登记 (summary 最全的那条), 其余条目的 summary **逐字**并入主登记的 summary (带原 #序号 / kind / version / updated_at), **零信息丢失**, 且同 path 组数 31 → 0。**完整可追回清单: `logs/iss358/dedup_list.md` §B (31 组逐组列出, 含每条原文)**。

### B1.3 改 key 映射表 (★value / to / ref 一字未改, 只换 key 名★)

| 原 idx | 原 key | 新 key | to | 主题 | 落点 |
|---|---|---|---|---|---|
| 1 | `pcb_outline_confirm` | `pcb_outline_confirm_2_cavity` | hw-lead | 镜脚内腔需求(下限) | 新 key ⇒ 待 main 在 hw.yaml 建 need |
| 2 | `pcb_outline_confirm` | `pcb_outline_confirm_3_camera_mount` | hw-lead | 摄像头安装 | 同上 |
| 3 | `pcb_outline_confirm` | `pcb_outline_confirm_4_thermal_path` | hw-lead | 散热接触路径 | 同上 (★hw.yaml 那条 need item 也要的「散热路径」⇒ 见 B5 待办-1★) |
| 6 | `pcb_outline_confirm` | `pcb_outline_confirm_5_mfit_result` | hw-lead | M-FIT 结果 | 同上 |
| 5 | `ntc_placement` | `ntc_placement_2_power_budget` | sw-lead | 持续功耗上限 0.16-0.21W / 结温 4 档 / 切档 ≤16.67ms | 新 key ⇒ 待 main 在 sw.yaml 建 need (★sw.yaml 那条 need item 也要的「实测功耗需求」⇒ 见 B5 待办-3★) |
| 7 | `ntc_placement` | `ntc_placement_3_struct_constraint` | sw-lead | 结构侧硬约束 (余量 0.30mm) | 同上 |
| 37 | `iss219_mech_c7_sink_area_confirm` | `iss219_mech_c7_sink_area_confirm_2_live_caliber_threshold` | main | 活口径 W_rim 门槛重算 (22.15mm @0.468W / 25.63mm @0.50W) | 新 key ⇒ 待 main 在 pm.yaml 建 need (见 B5 待办-5) |
| 40 | `iss251_mech_service_port_pad_y_migrate` | `iss264_mech_jd_y0_and_open_y_caliber` | main | ISS-264 落 2/3, 只剩 jd_y0 | ★落到既有 need (mech.yaml, to=main)★ 主题逐字对应 (该 need 正文引用 开口 Y 7.835..12.435 / P-5 3.23 / S2 8.53 三数) ⇒ 无孤儿 key、无 lint 增量 |

**保留在原 key 上的 (按 brief §③ 规则 2, 留「那条 need 真正问到的那条」)**:
- `pcb_outline_confirm` ← idx0 「PCB 50x12mm; 厚 0.8mm(4层)/1.0mm(6层); 固定 2xM1.2 + 1x⌀2.0H7; Type-C 面板开孔 9.5x3.6mm」⇒ **hw.yaml 的 need 闭合靠它, 绝不空**。
- `ntc_placement` ← idx4 「NTC 贴 SoC 背面散热焊盘边缘或铝/铜骨架, 走 I2C, 不贴皮肤侧; 读数粒度 ≥1Hz; 上报 SoC 结温 Tj」⇒ **sw.yaml 的 need 闭合靠它**。
- `iss219_mech_c7_sink_area_confirm` ← idx33 「C-7 面积已实算 (ISS-222): 净可外露 3432mm² ⇒ 面积不是阻塞项, 真正硬门槛换成 W_rim」⇒ **与 mech.yaml 同名 need 同 key**。
- `iss251_mech_service_port_pad_y_migrate` ← idx42 「本单 N1 实质被 ISS-264 接管, 我不代 main 关单」⇒ **与 mech.yaml 同名 need 同 key**。

### B1.4 ★关键安全点★: 我 **一条 need 都没有新增/删除/改 key**

`mech.yaml` 的 `needs_from` 段 **139 条逐字节未动** (md5 比对见 B6) ⇒ 任何一条 need 的「被问方名下有没有同 key 答案」判据结果都不变 ⇒ **不存在「把别的分片的 need 打成未答」的风险**。本单只动 `answers` / `artifacts` / `interface_claims` 三段。

### B1.5 ★板框 U-1 的事与本单无关★

`pcb_outline_confirm` 那 5 条里**没有一条是板框 U-1 的答案** (①是 50×12mm 板外形口径, 不是 U-1 冻结判据) ⇒ 本单不把任何一条当板框答案用, 不新增拍板项。板框 U-1 的真答案仍在 `DECISION_ONE_PAGER_2026-11-22.md` §⑥/§⑦ + `DECISION_INDEX_2026-11-18.md` §R, 本单一个字没动。

---

## B2 验收标准自评

### B2.1 硬指标逐条 (★本单特有的回退闸用反事实法验★)

| # | 验收标准 | 改前 | 改后 | 判定 |
|---|---|---|---|---|
| 1 | `check_frag_dup_keys.py --agent mech-lead` | 高危 **4** 组 · 低危 **32** 组 · rc=**1** | 高危 **0** 组 · 低危 **0** 组 · rc=**0** | ✅ **通过** |
| 2 | `check_frag_dup_keys.py` (全仓) 高危总数 | mech-lead 4 组 | **5 组, 全在 hw-lead** (main 0 / sw-lead 0 / mech-lead 0) | ✅ **通过** (别人的地界, 我没越界改) |
| 3 | `python3 state/merge.py` | rc=0 | rc=**0** | ✅ 通过 |
| 4 | `python3 state/gate_check.py` | rc=0 · Q1 18/18 | rc=**0** · Q1 **18/18** | ✅ 通过 |
| 5 | `python3 state/frag_write.py --agent mech-lead --show` | rc=0 | rc=**0** (输出存档 `logs/iss358/frag_show_after.yaml`) | ✅ 通过 |
| 6 | `md5sum HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` (mtime `2026-11-06 07:07:17.362193413` 未变) | ✅ **零写板** |
| 7 | ★**未闭合需求数不得比改前多**★ | 看板 295 | 看板 301 | ⚠️ 见 B2.2 —— **我的净影响 = 0**, +6 来自别人并发写 |

### B2.2 ★回退闸 (未闭合需求数) 的反事实证明 —— 这是本单最要紧的一条★

看板数字确实从 **295 变成了 301 (+6)**, 但**这 6 条不是我造成的**:

```
【反事实·我的改动前】总需求=514 已答=167 未闭合(pending)=301 等外部=46
【现状·我的改动后】  总需求=514 已答=167 未闭合(pending)=301 等外部=46
⇒ 我的改动对未闭合需求数的净影响 = +0
⇒ 我的改动对已答数的净影响 = +0
⇒ 状态翻转的 need 条数 (我的改动引起) = 0
```

- 反事实做法: 把我的 8 条改 key **原样还原** (old_key 存在 `logs/iss358/renames.json`), 其它三片保持当前状态, 重算闭合台账 ⇒ **301 = 301, 0 条 need 状态翻转**。
- **+6 的真凶**: `state/fragments/hw.yaml` 在 **2026-11-23 10:01:33** 被 hw-lead 并发重写 (651494 B → 667443 B), 期间新增 **6 条 `iss356_*` need** (`iss356_netlist_4rows_gnd_fix` / `iss356_bom_footprint_backfill` / `iss356_charge_board_22_fp_truth` / `iss356_jdebug_mech_clearance_recheck` / `iss356_dup2_and_f15_scope` / `iss356_led_symmetry_and_delete_decisions`), 这 6 条本来就没人答 ⇒ 看板未闭合 +6。**我的 09:5x 基线快照是在旧 hw.yaml 上取的, 所以账面差 6; 隔离掉并发后差 0。**
- ⇒ **结论: 本单对台账是零回退 (0 条 need 状态翻转), 并且未闭合需求数没有因我的改 key 增加。** ★本单没有为了「让数字好看」去动别人的分片, 也没有新增 need 把数字撑上去★。

### B2.3 我确实造成的指标变化 (全部如实上报, 逐条给了收敛办法)

| 指标 | 改前 | 改后 | 差 | 说明 + 收敛办法 |
|---|---|---|---|---|
| `answers` 有效条数 (gate_check 答方视角) | 27 | **21** | **-6** | 6 条跨分片答案 (`pcb_outline_confirm_2/_3/_4/_5` + `ntc_placement_2/_3`) 改 key 后, 对方分片还没有同名 need ⇒ 暂时对不上「别人的需求 key」⇒ 不计入有效。★main 按 B5 待办-1/2/3/4 建完 6 条 need 后即恢复 27★ (实测逻辑: 有效 = ∃同 key 且 to 匹配的 need) |
| `lint` (merge.py 孤儿 answers.key) | 143 | **150** | **+7** | 7 条新 key 暂时没有任何 needs_from 引用 (第 8 条 `iss264_mech_jd_y0_and_open_y_caliber` 落到既有 need ⇒ 不产生 lint)。★main 按 B5 待办-1~7 建完 need 后即回 143★; 合并器 `state/merge.py:371` 这条提示是**软提示**(不 fail 任何闸), 不影响 merge/gate rc |
| `artifacts` 产出条数 | 230 | **183** | **-47** | 47 条同 path 登记被**并入**主登记 (summary 逐字保留, 可按 #序号 追回) ⇒ **不是删内容, 是把 31 组「一文件多 issue 增量登记」并成一条主登记**; 清单见 `logs/iss358/dedup_list.md` §B |
| `interface_claims` 条数 | 340 | **339** | **-1** | 删的是 `mech_temple_thk_mm` 的**逐字完全相同**副本 (key/value/note/ref 四个字段全同) ⇒ **合并后接口取值一个数没变** |
| `needs_from` 条数 | 139 | **139** | 0 | ★一段没动★ |
| `answers` 条数 | 82 | **82** | 0 | 只改 key, 不增不删 |
| merge.py 全仓「产出」 | 795 | 752 | -43 | 其中 **-47 是我** (artifacts 合并), **+4 是 hw-lead 并发新增** |
| 合并冲突 / 健康度 | 冲突 0 · red | 冲突 **0** · red | 0 | 未动任何闸 |
| 阻塞 (高危) | 43 (高危 33) | 43 (高危 33) | 0 | 未动 |

### B2.4 已做 / 未做 分界 (逐组名单)

**✅ 已做**
1. answers 改 key **8 条** (4 组高危全部拆开): `pcb_outline_confirm` ×4 拆出 `_2_cavity` / `_3_camera_mount` / `_4_thermal_path` / `_5_mfit_result`; `ntc_placement` ×2 拆出 `_2_power_budget` / `_3_struct_constraint`; `iss219_mech_c7_sink_area_confirm` ×1 拆出 `_2_live_caliber_threshold`; `iss251_mech_service_port_pad_y_migrate` ×1 迁到既有 need `iss264_mech_jd_y0_and_open_y_caliber`。★value / to / ref 逐字未改 (脚本内置断言 + B6 可复现)★。
2. artifacts 同 path 合并 **31 组 / 47 条并入** (逐字保留 + 逐组可追回清单)。
3. interface_claims 去重 **1 组** (逐字相同副本)。
4. 自证 + 交卷 (零写板、零落表、只动 mech.yaml)。

**❌ 未做 (明确不假装做)**
1. **未新增/未修改任何 need** ⇒ 上面 7 个新 key 暂时是孤儿 (B5 待办交给 main)。理由: brief 的回退闸「未闭合需求数不得比改前多」与「新增 need」直接冲突 (新增 7 条必然 +7 未闭合), 且新增 need 要写别人的分片 (hw.yaml/sw.yaml/pm.yaml) ⇒ 越界。
2. **未动 hw.yaml / sw.yaml / pm.yaml 一个字节** (别人的地界) ⇒ 全仓剩余高危 5 组全在 hw-lead, 我不越界。
3. **未改** `state/merge.py` / `gate_check.py` / `frag_write.py` / `check_frag_dup_keys.py` (并发写的根治 = 给 frag_write.py 加乐观并发断言, 那是 main 的地界)。
4. **未动** 网表 / 脚表 / BOM / 原理图 / 任何闸 / 板面 (板 md5 与 mtime 双不变)。
5. **未替老板拍板**, 未新增拍板项 (板框 U-1 一字未碰)。

---

## B3 证据分级

| 结论 | 证据等级 | 依据 |
|---|---|---|
| `merge.py:295` 收集全部匹配答案 (不是取第一条) | **[实测]** | 逐行读源码 + 实跑 `state/merge.py` |
| 「已答」判定只看存在性 (三处平行实现口径一致) | **[实测]** | `state/gate_check.py:440` / `state/stage_gate.py:138` / `state/decision_truth.py:164` 逐行读 |
| hw.yaml 的 need `pcb_outline_confirm` 是被一条只答 PCB 外形的答案闭合的 | **[实测]** | 实跑合并器 + 四片分片台账 (`logs/iss358/closure_before.json`) |
| mech.yaml 230 条 artifacts 无 `key`/`id` 字段 ⇒ 体检器实为按 path 分组 | **[实测]** | 逐条字段并集 = `{kind,path,summary,updated_at,version}` |
| 31 组共 78 条 artifacts 中逐字相同副本 = 0 条 | **[实测]** | 逐条 (path,kind,version,updated_at,summary) 全字段序列化比对 (`logs/iss358/analysis_before.json`) |
| mech-lead 高危 4 组 → 0 组 / 低危 32 组 → 0 组 | **[实测]** | `python3 state/check_frag_dup_keys.py --agent mech-lead` (rc 1→0) |
| 我的改动对未闭合需求数净影响 = 0, 0 条 need 状态翻转 | **[实测]** | 反事实重算 (`logs/iss358/counterfactual.py` 输出见 B6) |
| 看板 +6 未闭合来自 hw-lead 并发写的 6 条 `iss356_*` need | **[实测]** | `hw.yaml` mtime `2026-11-23 10:01:33` / 651494→667443 B + 逐条列名 |
| 板零写板 | **[实测]** | md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` |
| `pcb_outline_confirm` 5 条里没有一条是板框 U-1 答案 | **[实测]** | 逐条读 value 全文 + 对照 `DECISION_ONE_PAGER_2026-11-22.md` §⑥/§⑦ |
| 改 key 后 8 条答案的 value/to/ref 一字未改 | **[实测]** | 改造脚本内置逐条断言 (`logs/iss358/transform.py`) |
| artifacts 合并后 47 条被并入 summary 逐字仍可检出 | **[实测]** | 合并脚本内置逐条 `assert 原 summary in 新 summary` |
| `mech_temple_thk_mm` 两条 interface_claims 逐字相同 | **[实测]** | 逐字段 JSON 比对 |
| W_rim 活口径 22.15mm @0.468W / 25.63mm @0.50W (被移动的 idx37 的内容) | **[推算]** (鳍模型重算, 原答案自标口径) | value 原文自带口径说明, 我一字未改 |
| 背板质量 m = 0.324 × W_rim g = 7.18-9.72 g ⇒ 整机 57.96-85.08 g (387 mAh) | **[推算]** (同上一行) | value 原文 |
| 镜脚前后厚余量 0.30mm (⇒ 导热垫 0.3mm 与骨架 1.0mm 都加不厚) | **[推算]** (金属骨架厚 v1.1 未给, 按 1.0mm 假设) | value 原文自带假设 |
| 持续功耗上限 0.16-0.21W (贴皮肤 43°C 红线) / 持续满载 1.22W ⇒ 皮肤侧 96.1°C / 82.0°C | **[推算]** (模型敏感性区间) | value 原文 |
| 镜脚前后厚 7.3mm / 电池档 340-575-675mAh / 切档 ≤16.67ms / FCCSP pitch ≤0.3mm | **[实测]** (来自 MECH_BUDGET / fit_check.py 的既有台账, 本单只搬不改) | value 原文 + `MECH/fit_check.py` |
| 30 mm 板宽 / 60×30 板套 A 的实际尺寸 | **[0数据]** (W_rim 为 u8 未定值, 不预扣) | value 原文自标 `[0数据]` |

---

## B4 接口取值声明

1. **本单未新增、未修改、未删除任何 `interface_claims` 的取值 (value)**。
2. 唯一一条删除 (`mech_temple_thk_mm` 的第 2 条) 与保留条 **key / value / note / ref 四字段逐字完全相同** ⇒ **合并后 `interface_claims` 里 `mech_temple_thk_mm = 7.30` 一个数没变**, 冲突判定结果不变 (`merge.py` 冲突数改前 **0** / 改后 **0**)。
3. **本单改的 `answers.key` 不是 `interface_claims`** ⇒ 不进接口冲突检测面; 我**没有**借改 key 的机会新增任何接口声明 (那会新增口径, 超出本单范围)。
4. 声明口径不变的三条既有口径 (供 main 复核用, 数值一字未动):
   - `mech_temple_thk_mm = 7.30` (老板锁死值, 镜腿厚) —— 本单只删了它的逐字副本。
   - 贴皮肤镜腿持续功耗上限 `0.16-0.21 W` (43°C 红线对应, 模型敏感性区间) —— 原文随 `ntc_placement_2_power_budget` 整段搬走, **数值未改**。
   - 结温分档 `<70 / 70-85 / 85-95 / >95 °C` + 切档 `≤16.67 ms` + 充电时禁 OD —— 原文随 `ntc_placement_2_power_budget` 整段搬走, **数值未改**。
5. **未新增接口声明 ⇒ 未制造任何新的跨分片冲突面**; 新拆出的 7 个 key 属 `answers` 段, 待 main 建同 key need 后自然进入配对面 (见 B5)。

---

## B5 未决项与卡点

### B5.1 ★跨分片待办 (交 main, 我不越界写别人的分片)★ —— 建完这 7 条 need, 有效答案 21→27 / lint 150→143 同时恢复

| # | 在哪片建 | key | to | item (可直接抄) | 为什么必须建 |
|---|---|---|---|---|---|
| 1 | `hw.yaml` | `pcb_outline_confirm_4_thermal_path` | mech-lead | 散热接触路径与器件发热分布: SoC 底面散热焊盘 → 0.3mm 导热垫 → 铝/铜骨架 → 石墨(面内扩展到上表面+铰链侧) → 对流; 路径不得有塑料隔断 (打印件 k=0.2 ⇒ 热阻 +94K/W); SoC 必须放远离皮肤侧一侧; 上下分壳 (上壳装 PCB/骨架, 下壳贴皮肤只放电池); 必须加 1 颗 NTC (贴 SoC 背面/骨架, 走 I2C) | ★**必建**: hw.yaml 现在那条 need `pcb_outline_confirm` 的 item 明写「+ 散热路径」, 拆走后那条 need 只看得见 PCB 外形一条 ⇒ 散热路径对 hw-lead 不可见 |
| 2 | `hw.yaml` | `pcb_outline_confirm_2_cavity` | mech-lead | 镜脚内腔需求(下限): 前后厚 ≥7.3mm / 根部净高 ≥38mm / 内腔长 ≥110mm (前提: 充电板挪出镜脚, 长度需求 105.5/110/108mm); 分配: 电池+主PCB+充电板 沿长度串行 (垂直并排放不下: 22+12=34mm); 光机+分光件不在镜脚, 在镜框正中 (光学舱 14×10×6mm, 镜框正中厚需 ≥11.8mm) | 让内腔需求对 hw-lead 可见 |
| 3 | `sw.yaml` | `ntc_placement_2_power_budget` | mech-lead | 持续功耗上限 0.16-0.21W (43°C 红线对应的贴皮肤镜腿上限, 模型敏感性区间; 持续满载 1.22W 会到皮肤侧 96.1°C/82.0°C, 必须按持续满载最保守设计); 结温 4 档 <70/70-85/85-95/>95°C 已登记为 thermal_control_tiers; 切档须 ≤16.67ms; 充电场景 0.8W 充电IC耗散 ⇒ 充电时必须禁 OD | ★**必建**: sw.yaml 那条 need `ntc_placement` 的 item 明写「+ 实测功耗需求 (按需触发 vs 持续满载的 DVFS 策略)」, 拆走后只剩「NTC 贴哪」 |
| 4 | `sw.yaml` | `ntc_placement_3_struct_constraint` | mech-lead | 结构侧本轮新增硬约束 (会限制 SW 的 DVFS 散热方案): 镜脚前后厚余量只有 0.30mm ⇒ 导热垫 (0.3mm) 与金属骨架 (按 1.0mm 假设) 都加不厚; 若要更厚骨架/更多散热面积压结温, 必须同步把镜腿前后厚从 7.3 加到 7.6-7.8mm (需老板拍板形态); 持续满载 1.22W ⇒ 皮肤侧推算 96.1/82.0°C, 43°C 红线只允许持续 0.16-0.21W ⇒ 降温只能靠降功耗不能靠加散热片 | 让结构硬约束对 sw-lead 可见 |
| 5 | `hw.yaml` | `pcb_outline_confirm_3_camera_mount` | mech-lead | 摄像头: 装镜框上沿正中, 光轴俯角 ≤25° (装上沿的 20-32° 偏置不可回避), 水平偏置 ≤10°, 凸出 ≤2.5mm, 凹进 ≤1.5mm; 对角 FOV ≥100° (100° ⇒ H92.2/V60.6, 16:9); 凹进 5mm 吃掉上半视场 31%; 镜框上沿摄像头位需局部加厚 10-12mm | 让摄像头安装口径对 hw-lead 可见 |
| 6 | `hw.yaml` | `pcb_outline_confirm_5_mfit_result` | mech-lead | M-FIT 结果 (设计态计算, MECH/fit_check.py): 镜脚侧 340mAh 档 前后需求 7.00mm vs 可用 7.30 ⇒ 余 0.30mm, 与 FDM 单边公差 ±0.2-0.3 同量级 ⇒ 临界, 建议镜腿做到 7.6-7.8mm; PCB/骨架区仅 4.50mm (4层)/4.70mm (6层) ⇒ 板厚 4层/6层都不卡空间 (但 §1.4.2「电池与PCB同区叠放」模型 ⇒ 前后干涉 0.80mm + 垂直干涉 3.50mm, v1.1 两个排列模型必须锁定一个); 长度: 电池40.5 + PCB50 + 余量15 = 105.5 ≤ 130 (充电板必须挪出镜脚, 否则 +0.50mm 干涉); Type-C 尾端截面宽需 ≥12.5mm (开口9.5 + 两侧1.5 承力壁)、高需 ≥6.6mm (可用 7.3, 余 0.7) | 让 M-FIT 结果对 hw-lead 可见 |
| 7 | `pm.yaml` | `iss219_mech_c7_sink_area_confirm_2_live_caliber_threshold` | mech-lead | 活口径下的 W_rim 门槛 (两档): ISS-227 把 P3 活口径从打印件顶面 (假同温) 改成铝制集热背板 120×W_rim×1.0 后, 同一条 W_rim 门槛在两个口径下不是一个数 ⇒ 鳍模型重算 22.15mm @0.468W (面板功耗) / 25.63mm @0.50W (ISS-216 代表负载) (摄像头凸包让位·u8=30·d=15) ⇒ ISS-222 登记的 23.30mm 只在面板功耗下成立 (0.50W 下 50.67°C ❌) ⇒ 若框截面按 23.30 裁, 必须同时确认峰值功耗 ≤0.468W; 净可外露面积 3432mm² 结论不变; 背板质量 m = 0.324×W_rim g = 7.18-9.72g ⇒ 整机 57.96-85.08g (387mAh), 背板质量不预扣 (W_rim 为 [0数据]) | 让「活口径门槛 + 背板质量」这条后续结论有配对面 (否则它是孤儿 key) |

> ★**规则 4 的二选一, 我选了哪个、为什么**: brief §③ 规则 4 给了两条路 —— (a) 把被拆走的答案**留在原 key 上** (原 key 留 2 条); (b) 在交卷页 B5 写成跨分片待办交给 main 改对方 need。**我选 (b)**, 理由: **(a) 会让体检器继续报 `pcb_outline_confirm ×2` / `ntc_placement ×2` ⇒ 高危组 ≠ 0 ⇒ 体检器 rc ≠ 0 ⇒ 与本单验收标准 #1 直接冲突**。⇒ 规则 4 的两个分支在「高危必须清零」面前不是并列的, (b) 才是唯一同时满足两条约束的解。★对应地, 我在 B2.3 如实上报了 (b) 的代价 (有效 27→21, lint 143→150), 并给 main 一次性补齐的 7 条 need 清单。★

### B5.2 并发事实 (★台账口径, 供 main 判读★)

- `state/fragments/hw.yaml` 在 **2026-11-23 10:01:33** 被并发重写 (651494 → 667443 B), 期间新增 6 条 `iss356_*` need ⇒ 看板未闭合 295 → 301。**这 6 条与本单无关** (反事实见 B2.2)。
- 本单自己写 `mech.yaml` 前后各跑了 md5: 写前基线 `a501815ec90137d849c493c8e749c4b5` (与 brief 给的基线一致 ⇒ **写前无并发**), 写后 `f1083d47cd76c0621766ccb63e8ad48a`。⇒ **本单没有覆盖任何人的并发写** (我的 3 次写都是 `state/frag_write.py` 原子写, 每次写前都核过 md5 基线)。
- ⚠️ **顺带发现 (不属本单, 只报不改)**: hw-lead 新增的那条 `iss356_jdebug_mech_clearance_recheck` (**to = mech-lead**) 是一条**新到 mech-lead 名下的未答需求** (J_DEBUG 板侧 land 改动 0.50 → 1.27mm pitch 引出的结构净距口径差)。本单不扩项, **不代答**, 请 main 另派。

### B5.3 ★预存口径冲突 (只报, 我一条都不代拍)★

1. **TMP117 贴装面 (sw-lead 定的 vs 结构侧答的) 冲突**:
   - `sw.yaml` 的 need `sw_temp_mount_point` (to=mech-lead) 正文写: 「**TMP117 测点我已定 (镜脚主 PCB 贴皮肤面, SoC 投影 ≤10mm)**」;
   - 而 mech-lead 的答案 (原 `ntc_placement` idx4 + `sw_temp_mount_point` idx12) 写: 「贴 SoC 背面散热焊盘边缘或铝/铜骨架, 走 I2C, **不贴皮肤侧** (皮肤侧读数滞后会让降频滞后 = 反而更热)」「TMP117 贴装落点建议放镜脚主 PCB 的**贴皮肤面一侧**、用 0402/0603 贴 **PCB 背面(非皮肤面)**并用 0.3mm 导热垫连到骨架」。
   - ⇒ **两边说的不是一回事 (贴皮肤面 vs 不贴皮肤侧)**, 而且 `sw_temp_mount_point` 因为存在同名答案被判「已答」⇒ **这正是 brief 说的「存在性判定 ⇒ 静默错闭合」的实例**。★我本单只做 key 拆分, **不替任何一方拍板**; 建议 main 单独裁一次贴装面 (属 SW/结构接口口径, 不是我能单方定的)★。
2. **W_rim 门槛两档口径并存**: `iss222_mech_c7b_sink_is_metal_not_print` 的答案 (idx34) 给的是「铝背板装上: 47.77/47.47/47.27°C @0.468W ✅」, 而 `iss219` 的后续答案 (idx37) 给的是「同一条 W_rim 门槛在两个口径下不是一个数 ⇒ 鳍模型重算 22.15mm @0.468W / 25.63mm @0.50W ⇒ ISS-222 登记的 23.30mm 只在面板功耗下成立」。⇒ **23.30mm 与 22.15/25.63mm 两个数并存, 需要一个口径裁决**。本单把两条拆到两个 key (**拆开就是为了让它们不再混在一锅粥里**), 但**裁决我一条都没做** (属老板/项目总工拍板项, 我不新增拍板项)。

### B5.4 本单明确不做的

- 不改 `state/merge.py` / `state/gate_check.py` / `state/frag_write.py` / `state/check_frag_dup_keys.py` (并发写的根治 = 给 frag_write.py 加乐观并发断言, **那是 main 的地界**; 本单只清已攒下的重名)。
- 不碰 `hw.yaml` / `sw.yaml` / `pm.yaml`。
- 不改板 / 不落表 / 不改任何闸 / 不新增拍板项 / 不外发。

---

## B6 自证复现命令

★全部在本仓根目录 (`/home/yuewuya/.openclaw/workspace/projects/smart_glasses`) 下跑; 原始输出存档在 `logs/iss358/`★

```bash
# 0) 写前基线 (brief 给的基线, 证明写前无并发写)
md5sum state/fragments/mech.yaml
#   ⇒ a501815ec90137d849c493c8e749c4b5

# 1) ★本单验收主闸★: mech-lead 分片重名 ⇒ 0
python3 state/check_frag_dup_keys.py --agent mech-lead ; echo "RC=$?"
#   ⇒ ✅ mech-lead  无重名 key        (改前: ⚠️ 高危 4 组 · 低危 32 组, RC=1)

# 2) 全仓重名: 高危只剩 hw-lead 的 (不在我地界)
python3 state/check_frag_dup_keys.py ; echo "RC=$?"
#   ⇒ main ✅0 / hw-lead ⚠️高危 5 组 / sw-lead ✅0 / mech-lead ✅0   (RC=1 来自 hw-lead)

# 3) 合并器 + 质量门
python3 state/merge.py ; echo "RC=$?"
#   ⇒ ✅ STATE.yaml 已刷新 (2026-11-23T10:04:06+08:00)
#     产出 752 | 阻塞 43 (高危 33) | 未闭合需求 301 | 冲突 0 | 健康度 red      RC=0
python3 state/gate_check.py ; echo "RC=$?"
#   ⇒ 【Q1 交付齐备率】 18/18 个必填验收块齐全
#     mech-lead  被答 46/139 | 我答 82 条(有效 21) | 产出 183 | 阻塞 12
#     🔵 等另一个总工 (真·内部未闭合): 全局 301 条   ✅ 与 merge.py 自对账一致      RC=0

# 4) 分片导出 (只读) + 段计数
python3 state/frag_write.py --agent mech-lead --show > logs/iss358/frag_show_after.yaml ; echo "RC=$?"
#   ⇒ answers=82 needs_from=139 artifacts=183 interface_claims=339 risks=8 blockers=12
#     answers 重名 {} / needs_from 重名 {} / artifacts 同 path 重名组数 0 / interface_claims 重名 {}

# 5) ★回退闸: 未闭合需求数 (反事实法)★
python3 logs/iss358/counterfactual.py
#   ⇒ 还原条数(应=8): 8
#     【反事实·我的改动前】总需求=514 已答=167 未闭合(pending)=301 等外部=46
#     【现状·我的改动后】  总需求=514 已答=167 未闭合(pending)=301 等外部=46
#     ⇒ 我的改动对未闭合需求数的净影响 = +0
#     ⇒ 我的改动对已答数的净影响 = +0
#     ⇒ 状态翻转的 need 条数 (我的改动引起) = 0

# 6) 零写板
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
#   ⇒ 611b869e13518c3c023fb178f91a0075   2026-11-06 07:07:17.362193413 +0800   (与基线逐字一致)

# 7) 复算本单改动的产物 (只读, 不写盘)
python3 logs/iss358/transform.py          # 生成 new_*.json + 改名/合并/去重三张日志 (含逐条断言)
python3 logs/iss358/closure_ledger.py > logs/iss358/closure_after.json   # 四片闭合台账
python3 logs/iss358/analyze_dups.py   > logs/iss358/analysis_before.json   # 改前重复全景
```

★存档清单 (`logs/iss358/`)★: `00_skeleton.md` (骨架) · `analysis_before.json` (改前重复全景) · `closure_before.json` / `closure_after.json` (闭合台账前后) · `renames.json` (8 条改 key, 含 value 全文) · `merge_log.json` (31 组 artifacts 合并逐组明细) · `claim_log.json` (interface_claims 去重) · `dedup_list.md` (★已并入/已去重登记清单, 逐组可追回★) · `new_answers.json` / `new_artifacts.json` / `new_interface_claims.json` (写入用的整段, 只走 `frag_write.py --set-json`) · `counterfactual.py` · `transform.py` · `mk_dedup_list.py` · `gate_check_before.txt` / `gate_check_after.txt` / `dup_all_after.txt` / `frag_show_after.yaml`。
