# HANDOFF · ISS-293 · sw-lead · ADC 复评文档口径同步

> **owner**: sw-lead (软件总工) · **verify_by**: main · **单号**: ISS-293
> **派活**: 项目总工 (main / moli) · **派活时刻**: 2026-11-17 16:5x · **队列**: cron `fb67af40`
> **性质**: 内部活 · SW 侧复评文档口径收口 + 机器闸类 ⇒ ★**零写板 / 零落表 / 零改网表真源**★
> **模板来源**: `state/dispatch_briefs/ISS-293_sw_adc_fullscale_caliber_review_sync.md`
> **续做说明**: 本单上一趟会话 (`agent:sw-lead:subagent:d5e931dd-ebd6-4945-93da-c32b47897429` · sessionId `cfd5aeac` · 17:05:53→17:18:06 · runtime 733s · status=failed) ★**死在会话层, 不是活干完**★ ⇒ ★**本趟只补 4 件: ① 交卷单填满 ② B1 逐条对账 ③ 回归自己实跑 ④ 分片补完**★ ⇒ ★**大块 (B1 文档订正 / B2 新闸) 已在盘上, 本趟没重做, 一个字节没改那两件**★

---

## ★B0 · 交付物清单 (★4 件 · 全部在盘 + 本趟原样 rc★)

| # | 交付物 | 路径 | 盘上实测 | 本趟原样 rc |
|---|---|---|---|---|
| 1 | ★交卷单 (本文件) ★ | `HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md` | ★**B0~B6 七块全填**★ | — |
| 2 | ★B1 改动的文档 (8 处追加式订正) ★ | `SW/SW_TIMING_REVIEW.md` | ★**90918 B · mtime 2026-11-17 17:11:55**★ | ★**新闸 rc=0 (29/29)**★ |
| 3 | ★B2 新建的闸 + `--selftest` ★ | `SW/tools/check_timing_review_adc_sync.py` | ★**20595 B · mtime 2026-11-17 17:11:12**★ | ★**rc=0 / --selftest rc=0 (4/4)**★ |
| 4 | ★B2 反向用例沙盒日志 (★真件零改动自证★) ★ | `logs/iss293/` | ★**本趟实跑落盘**★ | — |
| 5 | ★分片 (走 `state/frag_write.py` 原子写) ★ | `state/fragments/sw.yaml` | ★**本趟原子写**★ | ★**merge rc=0 / gate_check rc=0**★ |

★**本趟实跑 rc 汇总 (★全部本机自己跑, 不抄任何 agent 报告 / 不抄 main 的读数★)**★

```
### check_timing_review_adc_sync.py            → rc=0   (29/29 项通过)
### check_timing_review_adc_sync.py --selftest → rc=0   (SELFTEST 4/4 通过)
### timing_check.py (全量)                      → rc=0   (SELFTEST 85/85 通过)
### timing_check.py --only F4_adc_det           → rc=0
### timing_check.py --only F4D_usb_vbus_det     → rc=0
### check_demo_panel_spec.py                    → rc=0   (R1~R7 全过)
### check_demo_panel_spec.py --selftest         → rc=0   (SELFTEST 22/22 通过)
### state/merge.py                              → rc=0
### state/gate_check.py                         → rc=0   (Q1 18/18)
### md5sum 受保护 5 件                          → 逐字节不变 (见 §C2)
```

---

## ★B1 · 结论摘要 + ★F2 八条逐条对账表★

### ★B1.1 一句话 (★本单的核心价值★)

★★**`SW/SW_TIMING_REVIEW.md` 这份【手工写的】复评文档, 原先记着一条【假红被当成结论】(「ADC 检测通道可用性 ❌ 不通过 (500kΩ / 451ms / 15.2%FS)」) + 一条【已被推翻的 P0】(§7-4「电量分压整条 DNP / 1M」) ⇒ 本单按【追加式】把 ADC 段按盘面真值 + ISS-291 现行闸整体订正, 并新建一道闸把它钉死 (文档现值 == 闸的实跑读数 ⇒ 不等即红) ⇒ 下一个人不会再照着一条假红去判「ADC 链不合格 ⇒ 改板」⇒ 板不用白改第二遍**★

### ★B1.2 现行 ADC 真值 (★本趟自己实跑 `timing_check.py --only F4_adc_det` 的原样读数★)

```
active_chain        : BAT_DET          active_chain_pin : 38
active_chain_signal : SARADC_VIN5      active_chain_domain : 1.8V
chain_select_mode   : by_landing_pin
full_scale_v        : 1.8        adc_bits : 12      lsb_mv : 0.439
rth_ohm             : 37500.0    tau_ms  : 3.75
t_settle_to_half_lsb_ms : 33.791
leak_offset_v       : 0.0375    leak_offset_pct_fs : 2.1
standby_ua          : 26.25     supply_v : 4.2     node_v_at_supply : 1.575
node_max_abs_v      : 1.98      fs_utilization_pct : 87.5
criteria            : object_ok ✔ / fs_caliber_ok ✔ / settle_ok ✔ / leak_ok ✔ / node_ok ✔ / populated_ok ✔ ⇒ all_ok ✔
```

★**★注意 `verdict` 里那句「老口径 (判 VBUS_DET_D + FS=3.3V) 报的那条红 = 假红 ⇒ 已作废」★ ⇒ ★**文档 L208/L222 那两行「❌ 不通过」原先就是把【一条假红当结论记着】⇒ 这是本单修得最重的一条**★

### ★B1.3 ★F2 八条逐条对账表 (★文档里必须有的现值★)

★**核对方法**: 本机 `grep`/`python3` 逐行实读 `SW/SW_TIMING_REVIEW.md` (★共 599 行★) + 新闸 29 项逐项判 ⇒ ★**不许抄任何 agent 的读数★**

| # | 必须有的现值 | ★文档位置 (行号)★ | ★命中原文 (节录)★ | 判定 |
|---|---|---|---|---|
| 1 | ★判决对象 = `BAT_DET` 的明文 (带订正标记) ★ | ★**L39 / L57 / L208 / L578**★ | ★L39「★**判决对象已改 = `BAT_DET` 链** (网表 L186 ⇒ `J_SOM_P1 pin38` = `SARADC_VIN5`, 1.8V 域; 取链规则 `by_landing_pin`)」★ + §14 卡 `adc_decision_chain = BAT_DET` / `adc_decision_chain_pin = 38`★ | ✔ |
| 2 | ★满量程 `1.8` (V) ★ | ★**L39 / L57 / L208 / L582**★ | ★L208「12bit (LSB 0.439mV, 满量程 1.8V)」+ §14 卡 `adc_full_scale_v = 1.8V`★ | ✔ |
| 3 | ★LSB `0.439` (mV) ★ | ★**L39 / L208 / L584**★ | ★§14 卡 `adc_lsb_mv = 0.439mV`★ | ✔ |
| 4 | ★漏电偏移 `2.1%FS` ★ | ★**L39 / L57 / L208 / L589**★ | ★§14 卡 `adc_leak_offset_pct_fs = 2.1%FS`★ | ✔ |
| 5 | ★`R_th` = `37500` (Ω) ★ | ★**L39 / L57 / L208 / L585**★ | ★§14 卡 `adc_rth_ohm = 37500.0Ω`★ | ✔ |
| 6 | ★建立时间 `33.791` (ms) ★ | ★**L39 / L57 / L208 / L587**★ | ★§14 卡 `adc_t_settle_ms = 33.791ms`★ | ✔ |
| 7 | ★BAT_DET 三颗**必装** 的明文 ★ | ★**L39 / L57 / L223 / L344 / L465 / L593**★ | ★L344「★**现值 = `R_BAT_DET_1` 100k ±1% + `R_BAT_DET_2` 60k ±1% + `C_DET_BAT` 100nF ±10%, 三颗 dnp=必装 (网表 L182/L183/L184/L185 实读)**★ + §14 卡 `adc_populated = 必装`★ | ✔ |
| 8 | ★**活结论里不再残留 3.3V 口径旧数 / ADC ❌ 行 / 「三颗全 DNP」** ★ | ★**全文扫描**★ | ★新闸 4 项判据全绿: `P1-DECISION` (活结论里把 `VBUS_DET_D` 说成 ADC 判决对象的行: 无) + `P2-FS` (活结论里残留 3.3V 口径旧数的行: 无) + `P3-POP` (活结论里还在说 BAT_DET/电量链 DNP 的行: 无) + `P4-VERDICT` (活结论里残留 ADC ❌/无硬件支撑 的行: 无)★ | ✔ |

★**★八条全中 ⇒ 本趟【不需要补任何一处】⇒ 文档一个字节都没动 (★遵守 cont1 派活「只补漏, 不许整份重写」★)★**

### ★B1.4 ★B1 八处订正逐条落点 (★文档侧共 26 行带 `【ISS-293 订正】` 标记★)

★**标记约定 (★写在文档 L572 里, 本闸据此判「历史判据 vs 活结论」★)**: 文中凡是保留了老口径的行, **同一行必须带 `【ISS-293 订正】` 标记** ⇒ ★**标记丢了 = 活结论里出现老口径 ⇒ 闸红**★

| ★任务书要求的 8 处★ | ★文档落点 (行号)★ | ★订正要点★ |
|---|---|---|
| ★L38 (F6 行) ★ | ★**L39** (+ L7 段首订正说明) ★ | ★判决对象 → `BAT_DET` (pin38 / `SARADC_VIN5` / 1.8V 域) · 37500.0Ω · τ=3.75ms · 建立 33.791ms · 2.1%FS · LSB 0.439mV · 节点 1.575V ≤ 1.98V (FS 利用率 87.5%) · 六判据全 ✔; ★「BAT_DET 链三颗全 DNP」→「已改成必装 (V-3=E 落表后, 网表 L182/L183/L184 必装)」★ |
| ★L56 (汇总表) ★ | ★**L57** (+ L67 电量读数判据) ★ | ★整行现值重写 + 老句留痕 + 「500kΩ / 451ms / 15.2%FS」与「BAT_DET 链全 DNP」明写为**老口径 ⇒ 假红 ⇒ 已作废**★ |
| ★L207 (判定表) ★ | ★**L208** (+ L209/L210) ★ | ★「❌ 仍不通过」→「✔ 通过 (37500.0Ω / 33.791ms / 2.1%FS / 节点 1.575V ≤ 1.98V)」+ ★**「老口径报的那条红 = 假红 ⇒ 已作废」**★ |
| ★L222 (判定表) ★ | ★**L222 / L223** ★ | ★L222 = ADC 可用性行同订正; ★L223「❌ 不存在 (三颗全 DNP) ⇒ M7-R6 无硬件支撑」→「✔ 存在 (100k + 60k + 100nF, 三颗必装, 网表 L182~L186 实读)」+ ★**「老结论已被 2026-11-17 09:58:16 落表 (V-3=E) 推翻 ⇒ M7-R6 有硬件支撑」**★ |
| ★L343 (§7-4 P0) ★ | ★**L344** (+ L364 / L371 / L465) ★ | ★整条标【已不成立 / 关闭】+ ★**「1M」→「100k + 60k」真值订正**★ + ★「P0 (需求侧阻塞) 解除」+ ★**老字保留 (一个字节没删) 供追溯**★ |
| ★L370 (CR-4) ★ | ★**L371** ★ | ★「待 hw-lead 决策 (补装 or DNP)」→「★**已决策 = 补装** (V-3=E · 2026-11-17 09:58:16 落表) ⇒ 判据按 §3.2 / §3.3 的 `BAT_DET` 现值」+ ★**M7-R6 属 PM 域 ⇒ sw-lead 不自改, 已登记 need 给 main**★ |
| ★L433 (`adc_det_sampling`) ★ | ★**L434** ★ | ★「`BAT_DET链DNP-电量判据待定`」→「★**`BAT_DET` 链已必装 ⇒ 电量判据按 `BAT_DET` 现值 (2.1%FS, 节点 1.575V, 建立 33.791ms, LSB 0.439mV / 满量程 1.8V)**★」★ |
| ★L556 (复现命令块注释) ★ | ★**L557** ★ | ★「# F6: 电量链 (期望 R_BAT_DET_1/2 + C_DET_BAT 全 DNP ⇒ §7-4)」→「★**# F6: 电量链 (BAT_DET 三颗已必装 ⇒ 判据按 BAT_DET 链 37500Ω / 1.8V 域 ⇒ 见 F4_adc_det)**★」★ ⇒ ★**只改这一行注释, 紧邻的 `grep -nE "R_BAT_DET_|C_DET_BAT" HW/netlist_v1.csv` (L558) 一个字节没动**★ |

★**连带同批订正 (★同一批一次做完, 都在这一份文件里★)**: ★L197/L198 (模拟链拓扑 + `BAT_DET` 链 1M+1M 三颗 DNP → 100k+60k+100nF 必装) · L313/L322/L325 (返工点 6/15/18 严重度降为「不适用 (已消解)」, 老字保留) · L397/L408/L417 (三条汇总行) · L458 · L465 (未决项第 8 条「已关闭」) · L570/L571 (改卡手续 + 留痕约定) · ★**L574~L596 新增 §14「ADC 现值卡」 (17 键) = 机器可读对账面**★★

### ★B1.5 两条【带旧词但无订正标记】的行 —— ★特意说明, 证明闸不是关键词瞎扫★

| 行 | 内容 | 为什么不用打标记 |
|---|---|---|
| ★L141 ★ | ★「EN 内部 **500kΩ** 下拉」(`U_LDO_S28` 的 LDO EN 内部下拉) ★ | ★**这是 LDO 使能脚内部下拉, 跟 ADC 链毫无关系** ★ ⇒ ★不是「3.3V 口径的 ADC 源阻抗」 ⇒ 闸的 `ADC_CLAIM_RE` 前置过滤把它排除了 (不是靠人工豁免)★ |
| ★L196 ★ | ★「【模拟链】VBUS_DET_D: RAIL_DEMO_5V ─ R_VBUS_DET_D1 1M ─┬─ R_VBUS_DET_D2 1M ─ GND」★ | ★**这是该链的拓扑事实描述, 不是「判决对象 = VBUS_DET_D」的主张** ★ ⇒ ★该链的订正在★紧邻的 **L197** (带 `【ISS-293 订正】` 标记, 写明 pin100 = `USB_DRD1_VBUSDET` = 数字脚 ⇒ 不参与 ADC 判决)★ |

---

## ★B2 · 验收标准自评 (★逐条 ✅ / ⚠️ + 依据★)

| # | 验收项 (★任务书逐条★) | 判定 | 依据 (★本趟实跑★) |
|---|---|---|---|
| A-1 | ★**B1 文档 ADC 段按真值订正 (追加式, 老字不删)** ★ | ✅ | ★**26 行带 `【ISS-293 订正】` 标记; 老字逐字保留 (L39 的「500kΩ / 451ms / 15.2%FS」原句仍在, 只是行内追加了作废标注); §14 新增 17 键机器卡**★ |
| A-2 | ★**B1 必改清单 8 处逐条命中** ★ | ✅ | ★**§B1.4 对账表 8 行全 ✔ (§B1.3 F2 八条全 ✔) ★** |
| A-3 | ★**新写的数一律标证据等级** ★ | ✅ | ★**文档行尾沿用既有口径 `[实测]` / `[推算]` / `[0数据]` / `[官网]` (如 L208 行尾 `[实测]+[推算]+[0数据]` + `[官网]` 1.8V 域出处) ★** |
| A-4 | ★**B2 新闸存在 + 三条判据一条不许放宽** ★ | ✅ | ★**`SW/tools/check_timing_review_adc_sync.py` 20595 B; 判据 = P1 判决对象 (不许活结论再把 `VBUS_DET_D` 说成 ADC 链) + P2 满量程 (必须写 1.8 / 0.439 / 2.1%FS / 37500 / 33.791, 不许 15.2%FS / 0.8057 / 500kΩ 出现在活结论里) + P3 BAT_DET 必装 (必须出现「必装」) + P4 活判决不许残留 ADC ❌ + §14 卡 17 键逐键对账 ⇒ 共 29 项**★ |
| A-5 | ★**新闸真值来源 = 上游闸实跑, 不许自己重算** ★ | ✅ | ★**`read_truth()` 用 `subprocess` 跑 `SW/tools/timing_check.py --only F4_adc_det` 取 KV; 上游 rc≠0 / 段缺失 / 字段缺失 / `criteria.all_ok ≠ True` ⇒ ★**一律 fail-closed 报错, 不猜** ★** (实测: 故意改坏上游 → 本闸直接报错红)★ |
| A-6 | ★**新闸一个字节都不改任何文件** ★ | ✅ | ★**闸只读文档 + 只跑上游闸; `--selftest` 全程只写沙盒副本 (本趟实测: 真件读回 **90918 B 未变**) ★** |
| A-7 | ★**反向用例 ≥4 条, 每条贴原样 rc + 期望红组 vs 实际红组** ★ | ✅ | ★**4 条 (case1_revert_fs_pct / case2_revert_chain / case3_revert_populated / case4_baseline) ⇒ SELFTEST 4/4, rc=0; 原样输出见 §B6.2 ★** |
| A-8 | ★**反向用例在沙盒副本上做, 真件零触碰** ★ | ✅ | ★**沙盒 = `tempfile.mkdtemp()` + `_copy_doc()` 副本 + `_edit_text()` 改副本 (照 `MECH/check_onepass_struct_crosscheck.py --selftest` 的沙盒做法); 实测真件 90918 B 未变 ★** |
| A-9 | ★**B3 回归: 别的闸一条不许红** ★ | ✅ | ★**全量 `timing_check.py` rc=0 (SELFTEST 85/85) · `--only F4_adc_det` rc=0 · `--only F4D_usb_vbus_det` rc=0 · `check_demo_panel_spec.py` rc=0 (+ `--selftest` rc=0, 22/22) · `merge.py` rc=0 · `gate_check.py` rc=0 (Q1 18/18) ★** |
| A-10 | ★**零写板 (md5 + mtime 双重自证)** ★ | ✅ | ★**板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 两项均未变 ★** |
| A-11 | ★**零落表 (网表 / 脚表 / BOM 一个字节不许动)** ★ | ✅ | ★**网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ 逐字节不变 ★** |
| A-12 | ★**不许改 `SW/tools/timing_check.py`** ★ | ✅ | ★**本单只读它 (作为真值源) + 跑它; 一个字节没改 (md5 与 ISS-291 复验时的定版值一致) ★** |
| A-13 | ★**不许改 `SW/SW_REQUIREMENTS.md`** ★ | ✅ | ★**没改; 已在 §B5 登记 need `iss293_sw_m7r6_sync_to_main` 给 main (★需求真源 = PM 域★) ★** |
| A-14 | ★**不许碰 `HW/` 与 `MECH/` 的文件与分片** ★ | ✅ | ★**本单只写 `SW/SW_TIMING_REVIEW.md` + `SW/tools/check_timing_review_adc_sync.py` + 本交卷单 + `state/fragments/sw.yaml` + `logs/iss293/` ★** |
| A-15 | ★**零外发** ★ | ✅ | ★**没发任何邮件 / 询价 / 问询 / 采购; 全部靠本机实查 + 本项目盘面取数 ★** |
| A-16 | ★**不自签 issue_log** ★ | ✅ | ★**没签; 签字是 main 的活 ★** |
| A-17 | ★**分片走 `state/frag_write.py` 原子写 (禁止 `open(p,"w")`)** ★ | ✅ | ★**全部经 `python3 state/frag_write.py --agent sw-lead` ⇒ tmp + fsync + os.replace; 没碰 `open(p,"w")` ★** |
| A-18 | ★**只写本任务允许的文件, 不碰别人的分片** ★ | ✅ | ★**只写 `state/fragments/sw.yaml`; `hw.yaml` / `mech.yaml` / `pm.yaml` 一个字节没碰 ★** |

---

## ★B3 · 证据分级 (★本单每个关键数字★)

| ★数/说法★ | ★等级★ | ★依据 (★本机实查, 不抄任何报告★)★ |
|---|---|---|
| ★判决对象 = `BAT_DET` (pin38 / `SARADC_VIN5` / 1.8V 域) ★ | ★**[实测]** ★ | ★`python3 SW/tools/timing_check.py --only F4_adc_det` 实跑 (★本机, 2026-11-17 17:5x, 日志 `logs/iss293/only_f4_adc_det.log`★) ★⇒ `active_chain=BAT_DET` / `active_chain_pin=38` / `active_chain_signal=SARADC_VIN5` / `active_chain_domain=1.8V` / `chain_select_mode=by_landing_pin` ★ |
| ★满量程 1.8V 域 ★ | ★**[官网]** ★ | ★脚表 `HW/PCB/FET3572C_PIN_TABLE.csv` L39 (`SARADC_VIN5` / 1.8V) + `HW/PCB/rk3572_datasheet_V1.1.txt` L2454 (`SARADC_AVDD1V8 = 1.62/1.8/1.98V`) + L2864 (`Analog Input Range = AVSS18~AVDD18`) ★★(★ISS-291 已查证, 本单直接引, 未重查★)★★ |
| ★12bit ⇒ LSB 0.439mV ★ | ★**[推算]** ★ | ★1.8V / 2^12 ⇒ 0.439 mV; ★并由上游闸实跑读数 `lsb_mv: 0.439` 复核一致★ |
| ★R_th = 37500.0Ω / τ = 3.75ms / 建立 33.791ms ★ | ★**[实测]** ★ | ★上游闸实跑读数 (`rth_ohm: 37500.0` / `tau_ms: 3.75` / `t_settle_to_half_lsb_ms: 33.791`); ★τ 由 100k‖60k × 100nF 推出 (★[推算]★), 数值由闸实跑复核 (★[实测]★)★ |
| ★漏电偏移 0.0375V = 2.1%FS ★ | ★**[实测]** ★ | ★上游闸实跑读数 (`leak_offset_v: 0.0375` / `leak_offset_pct_fs: 2.1`); ★并与网表 L182 note 写死的「37.5mV 偏移 (2.1% FS)」逐字对上 (★[实测]★)★ |
| ★@4.2V 节点 1.575V ≤ abs-max 1.98V (FS 利用率 87.5%) ★ | ★**[实测]** ★ | ★上游闸实跑读数 (`node_v_at_supply: 1.575` / `node_max_abs_v: 1.98` / `fs_utilization_pct: 87.5`) ★ |
| ★`BAT_DET` 三颗 = 100k + 60k + 100nF, 必装 ★ | ★**[实测]** ★ | ★`HW/netlist_v1.csv` L182/L183/L184/L185 实读 (★本机 ★`grep`★) ⇒ `R_BAT_DET_1`=100k ±1% / `R_BAT_DET_2`=60k ±1% / `C_DET_BAT`=100nF ±10%, 三颗 dnp=必装 ★ |
| ★`VBUS_DET_D` 落点 = `J_SOM_P1 pin100` = `USB_DRD1_VBUSDET` (数字脚) ★ | ★**[实测]** ★ | ★上游闸 F4D 段实跑读数 (`som_pin: '100'` / `pin_class: 'DIGITAL'` / `pin_signal: 'USB_DRD1_VBUSDET'` / `pin_vol_raw: '——'`) ★ |
| ★V-3=E 于 2026-11-17 09:58:16 落表 (三颗改必装) ★ | ★**[实测]** ★ | ★网表 mtime `2026-11-17 12:30:22` + 网表 L182 note 逐字 (★ISS-283 合法落表依法前移, 非本单所改★)★ |
| ★老口径 (判 `VBUS_DET_D` + FS=3.3V) 报的那条红 = **假红** ★ | ★**[实测]** ★ | ★上游闸 `verdict` 原文 + 本单新闸 `P1/P2/P4` 三项判据全绿 (★活结论里已无该红★)★ |
| ★`VBUS_DET_D` 三个硬件未决 (DRD1 内部 40kΩ 下拉 / IO 域与 abs-max / 识别裕量 75mV) ★ | ★**[0数据]** ★ | ★上游闸 F4D 段 `unresolved` 三条 (★域未知时按手册高电平带上沿 3.3V 降级上界★) ⇒ ★**不随本单闭合**, 仍需 main 转 hw-lead ★ |
| ★板 / 网表 / 脚表 / BOM 的 md5 与 mtime ★ | ★**[实测]** ★ | ★本机 `md5sum` + `stat` 实跑 (见 §C2)★ |

---

## ★B4 · 接口取值声明 (★已登记进自己分片的 `interface_claims`★)

| ★键★ | ★对外口径★ | ★依据★ |
|---|---|---|
| ★`iss293_adc_decision_chain_current` ★ | ★**`BAT_DET`** (判决对象) ★⇒ `J_SOM_P1 pin38` = `SARADC_VIN5` = 1.8V 域 · `by_landing_pin` 取链 ★ | ★[实测] 上游闸实跑 + §14 卡 `adc_decision_chain`★ |
| ★`iss293_adc_current_values` ★ | ★**R_th = 37500.0Ω · τ = 3.75ms · 12bit LSB = 0.439mV · 满量程 1.8V · 建立 33.791ms · 漏电 0.0375V = 2.1%FS · @4.2V 节点 1.575V ≤ abs-max 1.98V · FS 利用率 87.5%** ★ | ★[实测] 上游闸实跑 + §14 卡 17 键逐键对账 (★新闸 29/29 绿★)★ |
| ★`iss293_vbus_det_d_is_digital_not_adc` ★ | ★**`VBUS_DET_D` = USB OTG 插入检测【数字】脚** (pin100) ⇒ 不参与 ADC 判决 ⇒ 按 F4D 数字口径单判 ⇒ ★**不许套 100k/47k** (⇒ 节点 1.60V < 2.3V 阈值 ⇒ USB 插入检测直接死)★ ★ | ★[实测] F4D 段 + `iss291_sw_do_not_apply_vbus_100k47k` 闭环注 + 新闸 `P1-DECISION` 判据钉着★ |
| ★`iss293_bat_det_populated` ★ | ★**`BAT_DET` 三颗必装** (100k + 60k + 100nF) ⇒ 电量检测分压在现网表上**存在** ⇒ ★**M7-R6 有硬件支撑**★ ★ | ★[实测] 网表 L182~L186 + V-3=E 落表记录★ |
| ★`iss293_review_doc_pinned_by_gate` ★ | ★**`SW/SW_TIMING_REVIEW.md` 的 ADC 现值 = §14 机器卡 (17 键)**, 改口径必须【先改闸 → 再改卡 → 再跑新闸】★ ⇒ ★**文档不许再漂**★ ★ | ★[实测] 新闸 `CARD-MISSING` + 17 项 `CARD:*` 判据; 文档 L571 手写「改卡的手续」★ |

---

## ★B5 · 未决项与卡点 (★需要谁回答什么 · 我不拍★)

| # | ★未决★ | ★归属★ | ★状态★ |
|---|---|---|---|
| ① | ★**`SW/SW_REQUIREMENTS.md` 的 M7-R6 要不要同步改** ★ | ★**PM 域 (main 派单)★** | ★**已登记 need `iss293_sw_m7r6_sync_to_main` 给 main** ★⇒ ★**建议同步改成**: 「按 `BAT_DET` 现值判 (100k+60k+100nF 必装 ⇒ R_th=37500.0Ω · 12bit LSB=0.439mV 满量程 1.8V · 建立 33.791ms ⇒ 采样前丢弃 ≥34ms 的转换 · 漏电偏移 0.0375V = 2.1%FS 可软件标定 · @4.2V 节点 1.575V ≤ abs-max 1.98V)」★ ★**但需求真源是 PM 域 ⇒ sw-lead 只登记, 不自改** ★ |
| ② | ★**`VBUS_DET_D` 三个硬件未决**: DRD1 有无内部 40kΩ 下拉 / IO 域与 abs-max / 识别裕量 75mV ★ | ★**hw-lead (经 main 转)★** | ★**不随本单闭合** ★⇒ ★**闸里已把两种情形都算出来报出 (理想 2.5V / 含下拉 0.185V) ★ ⇒ 见 need `iss291_sw_vbus_det_d_digital_caliber` ★ |
| ③ | ★**「板只改一次」那一趟: 文档口径已钉死 ⇒ 不再因「ADC 链不合格」动板** ★ | ★**main / hw-lead 决策时看这份文档** ★ | ★**本单已提供**: 文档 8 处订正 + 新闸 29/29 ⇒ ★**照着旧文档判「改板」= 白改第二遍** ★ |
| ④ | ★**issue_log 签字** ★ | ★**main** ★ | ★**sw-lead 不自签** ★ |

★**★已随本单实质闭合 (★机器层 closed 仍由 main 签★)★**: ★`iss291_sw_vbus_det_d_digital_caliber` (内容 = `VBUS_DET_D` 改按数字检测输入口径单判 ⇒ ★**ISS-291 已落进 `SW/tools/timing_check.py` 的 F4D 段 + 本单 B1 文档同步**★)★ 与 ★`iss291_sw_do_not_apply_vbus_100k47k` (内容 = ★**不许把 `VBUS_DET_D` 链改成 100k/47k**★ = ★**本单没碰 + 新闸 `P1-DECISION` 钉着**★)★ ⇒ ★**两条闭环注已写进 `state/fragments/sw.yaml` 的对应 need 条目里 (★带依据, 不是自作主张关 need★)★★

---

## ★B6 · 自证复现命令 (★本趟原样 rc + 输出·不写「已清理」★)

### ★B6.1 回归 6 条 (★F3 派活清单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_timing_review_adc_sync.py; echo "rc=$?"
python3 SW/tools/check_timing_review_adc_sync.py --selftest; echo "rc=$?"
python3 SW/tools/timing_check.py; echo "rc=$?"
python3 SW/tools/check_demo_panel_spec.py; echo "rc=$?"
python3 state/merge.py; echo "rc=$?"
python3 state/gate_check.py; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**本趟实跑原样输出** ★:

```
### check_timing_review_adc_sync.py
=== ISS-293 · SW_TIMING_REVIEW.md ADC 口径同步闸 ===
--- 上游实跑真值 (SW/tools/timing_check.py --only F4_adc_det) ---
   active_chain=BAT_DET pin=38 signal=SARADC_VIN5 domain=1.8V
   full_scale=1.8 V  bits=12.0  lsb=0.439 mV  rth=37500.0 ohm  tau=3.75 ms  settle=33.791 ms
   leak=0.0375 V = 2.1 %FS  node@4.2V = 1.575 V (abs-max 1.98 V)  fs_util=87.5 %
   criteria_all_ok = True
--- 对账 (SW/SW_TIMING_REVIEW.md) ---
   [✔] CARD-MISSING                 §14 ADC 现值卡在位 (17 键)
   [✔] CARD:adc_decision_chain      adc_decision_chain = BAT_DET (与上游一致)
   [✔] CARD:adc_decision_chain_pin  adc_decision_chain_pin = 38 (与上游一致)
   [✔] CARD:adc_decision_chain_signal adc_decision_chain_signal = SARADC_VIN5 (与上游一致)
   [✔] CARD:adc_decision_chain_domain adc_decision_chain_domain = 1.8V (与上游一致)
   [✔] CARD:adc_full_scale_v        adc_full_scale_v = 1.8V (与上游一致)
   [✔] CARD:adc_bits                adc_bits = 12 (与上游一致)
   [✔] CARD:adc_lsb_mv              adc_lsb_mv = 0.439mV (与上游一致)
   [✔] CARD:adc_rth_ohm             adc_rth_ohm = 37500.0Ω (与上游一致)
   [✔] CARD:adc_tau_ms              adc_tau_ms = 3.75ms (与上游一致)
   [✔] CARD:adc_t_settle_ms         adc_t_settle_ms = 33.791ms (与上游一致)
   [✔] CARD:adc_leak_offset_v       adc_leak_offset_v = 0.0375V (与上游一致)
   [✔] CARD:adc_leak_offset_pct_fs  adc_leak_offset_pct_fs = 2.1%FS (与上游一致)
   [✔] CARD:adc_node_v_at_supply    adc_node_v_at_supply = 1.575V (与上游一致)
   [✔] CARD:adc_node_max_abs_v      adc_node_max_abs_v = 1.98V (与上游一致)
   [✔] CARD:adc_fs_utilization_pct  adc_fs_utilization_pct = 87.5% (与上游一致)
   [✔] CARD:adc_populated           adc_populated = 必装 (与上游一致)
   [✔] CARD:adc_criteria_all_ok     adc_criteria_all_ok = True (与上游一致)
   [✔] P1-DECISION                  活结论里把 VBUS_DET_D 说成 ADC 判决对象的行: 无
   [✔] P1-DECISION-PRESENT          文档里有「判决对象/装机链 = BAT_DET」的明文 (带订正标记)
   [✔] P2-FS                        活结论里残留 3.3V 口径旧数的行: 无
   [✔] P2-FS-LSB                    文档含现值 `0.439`
   [✔] P2-FS-PCT                    文档含现值 `2.1%FS`
   [✔] P2-FS-RTH                    文档含现值 `37500`
   [✔] P2-FS-SETTLE                 文档含现值 `33.791`
   [✔] P2-FS-VOLTAGE                文档含现值 `1.8`
   [✔] P3-POP                       活结论里还在说 BAT_DET/电量链 DNP 的行: 无
   [✔] P3-POP-PRESENT               文档含「必装」
   [✔] P4-VERDICT                   活结论里残留 ADC ❌/无硬件支撑 的行: 无

OK: 29/29 项通过, rc=0
rc=0
```

```
### check_timing_review_adc_sync.py --selftest
【自检】check_timing_review_adc_sync.py 反向用例 (★沙盒副本上跑, 真件一个字节不碰★)
  [真值] active_chain=BAT_DET pin=38 signal=SARADC_VIN5 fs=1.8 lsb=0.439 rth=37500.0 settle=33.791 pct_fs=2.1 node=1.575/1.98 fs_util=87.5%
  [基线] 29 项判据全绿 (真件)
  ✔ case1_revert_fs_pct: 期望红组 ['CARD:adc_leak_offset_pct_fs'] ⇒ 实际红组 ['CARD:adc_leak_offset_pct_fs', 'P2-FS-PCT'] ⇒ 红 ✔
  ✔ case2_revert_chain: 期望红组 ['CARD:adc_decision_chain'] ⇒ 实际红组 ['CARD:adc_decision_chain', 'P1-DECISION-PRESENT'] ⇒ 红 ✔
  ✔ case3_revert_populated: 期望红组 ['CARD:adc_populated'] ⇒ 实际红组 ['CARD:adc_populated', 'P3-POP-PRESENT'] ⇒ 红 ✔
  ✔ case4_baseline: 正向对照 ⇒ 期望绿 ⇒ 实际红组 [] ⇒ 绿 ✔
  [真件] SW/SW_TIMING_REVIEW.md 读回 90918 B (自检全程只写沙盒副本)

SELFTEST 4/4 通过, rc=0
rc=0
```

```
### timing_check.py (全量)
★★(★中间行省略, 只贴与本单相关的尾部★)★★
  [PASS] REV-15 反向: 把 BAT_DET 的下臂 60k 改成 100k ⇒ @4.2V 节点 2.1V > 1.98V abs-max ⇒ 过压判据必须变红
  [PASS] REV-16 反向: 把 VBUS_DET_D 链的两颗电阻改成 10k/10k ⇒ 数字链静态电流判据必须变红 (★数字脚口径也在判, 不是只判 ADC★)
  [PASS] REV-17 反向: 把 VBUS_DET_D 的上臂 1M 改成 10M ⇒ 节点 0.45V < 2.3V 识别阈值 ⇒ 数字链节点电平判据必须变红
SELFTEST 85/85 通过, rc=0
rc=0
```

```
### check_demo_panel_spec.py
✅ ISS-212 demo 显示侧口径门禁: 全过
   R1 demo 屏规格真源 (480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz + 附属必填项) ✅
   R2 demo 规格里整机口径只在「整机路线占位区」内 ✅
   R3 pipeline spec 的 demo 活动口径已重锚 ✅
   R4 整机路线占位仍在且带「整机路线·暂缓」 ✅
   R5 逐处定性表 (22 + 16 = 38 处) 完整 ✅
   R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致 ✅
   R7 已修复 (留痕) 在场 (ISS-220 落表锚点过期, 不是红灯被调没) ✅
rc=0
```

★**★(★R2/R4 两行里的「占位区」是 `check_demo_panel_spec.py` 的原样输出用词 (★指 demo 规格里的「整机路线占位区」★) ⇒ ★**不是本交卷单的占位符**★)★

```
### check_demo_panel_spec.py --selftest
★★(★中间行省略, 只贴尾部与正向用例★)★★
  ✅ REV-21 合法改板: 台账四项齐全 + 锚点原子记录 ⇒ 放行 (★正向★)             ⇒ R6 仍绿 (★合法改板四项齐全 = 放行★)
--- SELFTEST 22/22 通过 ---
rc=0
```

★**`state/merge.py` / `state/gate_check.py` 的原样 rc** ⇒ ★**见 §B6.4 (★在本单分片原子写完之后跑★)★**

### ★B6.2 ★反向用例 4 条 (★期望红组 vs 实际红组, 原样★)

| # | ★构造 (★在沙盒副本上★)★ | ★期望★ | ★实际 (★本趟原样★)★ | 判定 |
|---|---|---|---|---|
| ★① ★ | ★把文档里 `2.1%FS` 改回 `15.2%FS` ★ | ★红★ | ★实际红组 `['CARD:adc_leak_offset_pct_fs', 'P2-FS-PCT']` ⇒ 红★ | ✔ |
| ★② ★ | ★把文档里 `BAT_DET` 改回 `VBUS_DET_D` ★ | ★红★ | ★实际红组 `['CARD:adc_decision_chain', 'P1-DECISION-PRESENT']` ⇒ 红★ | ✔ |
| ★③ ★ | ★把文档里「必装」改回「全 DNP」★ | ★红★ | ★实际红组 `['CARD:adc_populated', 'P3-POP-PRESENT']` ⇒ 红★ | ✔ |
| ★④ ★ | ★正向对照: 一切如常 ★ | ★绿 (★证明闸不是恒红★)★ | ★实际红组 `[]` ⇒ 绿★ | ✔ |

★**★真件零触碰自证**: ★`--selftest` 全程只写 `tempfile.mkdtemp()` 沙盒副本 (★`_copy_doc()` + `_edit_text()` 改副本, 做法照 `MECH/check_onepass_struct_crosscheck.py --selftest`★) ⇒ ★**真件 `SW/SW_TIMING_REVIEW.md` 读回 90918 B 未变 (本趟自检输出末行原文)★ ★**

### ★B6.3 §①-3 那份实跑读数的来源说明 (★不许自编★)

★**读数来源**: ★**本机**★ `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses && python3 SW/tools/timing_check.py --only F4_adc_det` ★**⇒ 落盘 `logs/iss293/only_f4_adc_det.log` ⇒ 上面的 B1.2 那段 KV 就是该日志的原文摘录 (★字段名与值逐字一致★)★**

★**交叉验证**: ★同一次实跑里 `netlist_note_facts` 段从网表 L182 的 note 直接读出 `pct_fs=2.1` / `mv=37.5` / `rth_k=37.5` / `line_no=182` ⇒ ★**闸算的 2.1%FS 与网表 note 写死的数逐字对上** ⇒ ★**不是闸自己编的数**★

★**口径对照**: `SW/ADC_CALIBER_TABLE.md` (★ISS-291 出的口径对照页★) 与 `SW/tools/timing_check.py` 的 `DEVICE["V_DET_FS"] = 1.8` (★L81★) ★**本单只引, 没改** ★

### ★B6.4 分片原子写 (★走 `state/frag_write.py`★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/frag_write.py --agent sw-lead \
  --add-artifact 'path=SW/SW_TIMING_REVIEW.md kind=doc version=v1.0 updated_at=2026-11-17 summary=ISS293订正版' \
  --add-artifact 'path=SW/tools/check_timing_review_adc_sync.py kind=gate version=v1.0 updated_at=2026-11-17 summary=ISS293新闸29项' \
  --add-artifact 'path=HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md kind=handoff version=v1.0 updated_at=2026-11-17 summary=ISS293交卷单B0至B7' \
  --add-claim 'key=iss293_adc_decision_chain_current value=现值串 note=依据 ref=位置' \
  --status 'phase=delivered progress_pct=100 health=green summary=ISS293交卷摘要'
grep -c iss293 state/fragments/sw.yaml
```

★**本趟实跑原样输出 (★写盘后立即校验★)** ★:

```
### state/merge.py            (★分片原子写之后跑★)
✅ STATE.yaml 已刷新 (2026-11-17T17:59:41+08:00)
   产出 522 | 阻塞 43 (高危 33) | 未闭合需求 299 | 冲突 0 | 健康度 red
rc=0

### state/gate_check.py       (★分片原子写之后跑★)
【Q1 交付齐备率】 18/18 个必填验收块齐全
   sw-lead    6/6  缺: 无   交接单: 2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md
【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
【Q3 接口声明率】 全员 interface_claims 共 832 条
   sw-lead    253 条
★★(★中间行省略★)★★
rc=0

### state/issue_check.py      (★只读校验, 没签 issue_log★)
✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)
rc=0

### grep -c iss293 state/fragments/sw.yaml
11
```

★**★`grep -c iss293` = 11 (★任务书要求 ≥ 4★) ⇒ ★**四条新 `interface_claims` (键含 `iss293_*`) + 既有 need `iss293_sw_m7r6_sync_to_main` + status 摘要里的 `iss293` 都在★** ⇒ ★**并已复核: 上一条会话写入的 3 件 ISS-293 artifacts (文档 / 新闸 / 交卷单) 仍在; 两条 iss291 need 的【ISS-293 闭环注】仍在; 本单没删任何既有条目** ★

★**★并发提醒 (★本机实查到的真实情况, 不是猜★)★**: ★写这份分片期间, 本机有【另一条 sw-lead 队列会话 (ISS-288 cont1)】在同时写 `state/fragments/sw.yaml` (★mtime 在本趟期间连续变化★) ⇒ ★**本单的全部写入仍走 `state/frag_write.py` 的原子读改写 (tmp + fsync + os.replace) ⇒ 写完已逐项复核对方的条目 (iss288 相关 17 处命中) 仍在, 没被本单覆盖** ★ ⇒ ★**但 `status` 字段是单值字段, 若对方在本单之后又写 status, 本单的 ISS-293 status 摘要会被对方覆盖 (内容不丢, 在 artifacts/claims/needs 里)★ ★**

### ★B6.5 ★占位符残留自检 (★交卷单自身不许留空★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
F="HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md"
# ★**PAT 用 UTF-8 字节转义写 (★项目口径: 「旋转箭头图案」| 「待」+「填」两字 两型★) ⇒ 免得本文档自己命中自己★**
PAT="$(printf '\360\237\224\204')|$(printf '\345\276\205\345\241\253')"
grep -cE "$PAT" "$F"
```

★**★【ISS-293 cont2 订正 2026-11-18 05:5x · sw-lead】★**: ★**本块的上一版 (★2026-11-17 17:5x 那趟写的★) 记录「原样输出 = 0」是【不准确的】★** ⇒ ★**原判据把 13 个占位符形态的字面量直接写进了 `grep -nE "…"` 的参数里 ⇒ ★**该命令行自己命中自己 (★自匹配★) ⇒ 而且正文里那句「没有一处是【待】+【填】两字连写的空位」本身也带该字面量 ⇒ ★★真正按项目口径 (★「旋转箭头图案」| 「待」+「填」两字 两型★) 实跑, 上一版是 2 处, 不是 0★** ⇒ ★**本版按 ISS-306 / ISS-300 的同款做法: PAT 改用 UTF-8 字节转义写 (★`printf '\345\276\205\345\241\253'` = 那三个字节 = 「待」+「填」两字, 文档里就不出现它的字面量了★) ⇒ ★**本趟实跑原样输出 = 0 ★ ⇒ 项目口径的占位符残留 = 0 (★真零, 不是自匹配出来的假零★)★** ⇒ ★★上一版的「0」是什么? ★= 用了一条会命中自己的判据跑出来的 ★⇒ ★**教训 (★留给本项目所有交卷单★): 自检命令里不许出现被检形态的字面量 ⇒ 一律用字节转义★****

★**★宽口径复核 (★再加 `…` / `...` / `占位` 三个词★)**: ★**命中行逐行都有正当出处, 没有一处是未填的空位** ★ ⇒ ★① `check_demo_panel_spec.py` 的**原样输出**里的「整机路线占位区」 (★demo 规格里的真实区块名★) ⇒ ★② ★**我自己写的说明行**, 明写「那两行里的『占位区』是脚本原样输出用词, 不是本交卷单的占位符」★ ⇒ ★③ ★**shell 命令里的 `nohup ... > logs/…` 的省略号 (★真实命令行语法★)★ ⇒ ★④ ★**本块的 PAT 字节转义写法本身 (★`printf '\345\276\205\345\241\253'`★)****

---

## ★附 A · ★边界自查 (★违反就是不合格★)★

### ★C1 · 只写允许的文件 (★逐件列出本趟动过的盘★)

| ★文件★ | ★动没动★ | ★说明★ |
|---|---|---|
| `SW/SW_TIMING_REVIEW.md` | ★**本趟没动** (★只有上一趟会话落盘的 90918 B★) ★ | ★本趟只做对账 ⇒ 八条全中 ⇒ 不补 ★ |
| `SW/tools/check_timing_review_adc_sync.py` | ★**本趟没动** (★上一趟落盘的 20595 B★) ★ | ★本趟只跑它 + 它的 `--selftest` ★ |
| `HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md` | ★**本趟填满 (935 B → 全量) ★** | ★本文件 ★ |
| `state/fragments/sw.yaml` | ★**本趟原子写** ★ | ★走 `state/frag_write.py` ⇒ tmp+fsync+os.replace ★ |
| `logs/iss293/*.log` | ★**本趟新增 (实跑日志) ★** | ★只写日志, 不影响任何真源 ★ |
| ★`SW/tools/timing_check.py` ★ | ★**没动** ★ | ★只读 + 只跑 (★ISS-291 定版闸★)★ |
| ★`SW/tools/check_demo_panel_spec.py` ★ | ★**没动** ★ | ★ISS-275 已跑通的链头逻辑原样 ★ |
| ★`SW/SW_REQUIREMENTS.md` ★ | ★**没动** ★ | ★需求真源 = PM 域 ⇒ 只登记 need ★ |
| ★`HW/**` / `MECH/**` (含 `hw.yaml` / `mech.yaml` / `pm.yaml`) ★ | ★**没动** ★ | ★零写板 零落表 零碰别人分片 ★ |

### ★C2 · ★零写板 / 零落表 双重自证 (★本机 `md5sum` + `stat` 原样★)★

```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
37f62ac3f0b81d92ca7d48fdea717f07  HW/netlist_v1.csv
a4270120454aedf7a23c92cd8985c8a6  HW/netlist_v1_pins.csv
5d02bece9477ffce5fbe0193c7d5cce4  HW/BOM_v1.csv

2026-11-06 07:07:17.362193413 +0800  HW/PCB/demo_mainboard.kicad_pcb
2026-11-04 23:47:30.279742515 +0800  HW/PCB/demo_mainboard.kicad_pro
2026-11-17 12:30:22.352463497 +0800  HW/netlist_v1.csv
2026-11-17 12:30:22.488465119 +0800  HW/netlist_v1_pins.csv
2026-11-17 12:30:22.647467015 +0800  HW/BOM_v1.csv
```

★**逐字对上期望值**: ★板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★⇒ ★**板 mtime 仍是 `2026-11-06 07:07:17` ⇒ 零写板双重自证成立**★

★**注 (★ISS-289 交卷单自己发现的副作用★)**: ★`HW/check_onepass_preflight_coverage.py` 每次跑都会重生成 `HW/PCB/` 下 4 个辅助文件 ⇒ ★**判「有没有偷改板」只看官方板那两个文件的 md5 + mtime, 不看目录** ★⇒ ★**本单根本没跑那个脚本** ★

### ★C3 · 纪律自查

| ★纪律★ | ★本单做法★ |
|---|---|
| ★交卷单第一件事就 `write` 建骨架 ★ | ★上一趟会话已建骨架 (935 B) ⇒ 本趟填满, ★**没等文档写完才建** ★ |
| ★长任务 `nohup ... > logs/iss293/x.log 2>&1 &` + 短轮询 ★ | ★`timing_check.py` 全量跑用 nohup 后台 + 短轮询 (`logs/iss293/timing_full.log`)★ |
| ★单条 `exec` ≤ ~120 秒 ★ | ★全部前台命令都加了 `timeout 100~110`, 每条单独跑 ★ |
| ★每落一件交付物就把 rc 追加进交卷单 ★ | ★本文件 §B0 / §B6 逐条贴原样 rc ★ |
| ★分片写完 `grep` 校验 ★ | ★`grep -c iss293 state/fragments/sw.yaml` ≥ 4 ⇒ 原样输出见回复正文 ★ |
| ★文档订正追加式, 老字不许删 ★ | ★26 行带 `【ISS-293 订正】` 标记; 老字逐字保留 (★L39 / L57 / L208 / L222 / L223 / L344 / L371 / L434 的老句都还在★)★ |
| ★不许为了让闸绿而改闸 / 放宽判据 ★ | ★**本趟没碰那个闸一个字节**; ★判据方向与阈值一条没动 ★ |
| ★不许自签 issue_log ★ | ★没签 ★ |

---

## ★C4 · ★★cont2 独立复跑补记 (2026-11-18 05:4x · 本会话自己实跑)★★

> ★**本节是【追加式】补记, 前面 B0~B7 / C1~C3 一个字节没删没改★** ⇒ ★**C2 那段 md5 是 2026-11-17 18:00 交卷时刻的快照, C4 是本趟 (2026-11-18 05:4x) 的现值 ⇒ 两段都留着, 差额由 C4-2 说清 (★不是本单改的★)★**

### ★C4-1 · ★本趟自己实跑的 10 条回归 (★原样 rc·不抄 main 的读数★)★

★**脚本**: `logs/iss293/cont2_verify.sh` (★本趟新写★) · ★**日志**: `logs/iss293/cont2_verify.log` ★
★**本机**: `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` · ★**时刻**: 2026-11-18 05:4x ★

```
### [1] check_timing_review_adc_sync.py
rc=0
### [2] check_timing_review_adc_sync.py --selftest
rc=0
### [3] timing_check.py (全量)
rc=0
### [4] timing_check.py --only F4_adc_det
rc=0
### [5] timing_check.py --only F4D_usb_vbus_det
rc=0
### [6] check_demo_panel_spec.py
rc=0
### [7] check_demo_panel_spec.py --selftest
rc=0
### [8] state/merge.py
rc=0
### [9] state/gate_check.py
rc=0
### [10] state/issue_check.py
rc=0
```

★**⇒ 10/10 全 rc=0** ★ · ★**其中 `timing_check.py` 全量 = `SELFTEST 85/85 通过, rc=0`** (★原样摘录见 `logs/iss293/verify_timing_full.log` 末行★) · ★**`check_demo_panel_spec.py --selftest` = `--- SELFTEST 22/22 通过 ---`** (★原样摘录见 `logs/iss293/verify_demo_selftest.log` 末行★) · ★**`gate_check.py` = `【Q1 交付齐备率】 18/18 个必填验收块齐全` + `✅ 问题闭环门全过`** (★原样摘录见 `logs/iss293/verify_state_gates.log`★) ★

★**★新闸本趟原样输出 (★`logs/iss293/verify_run.log`★)**:
```
OK: 29/29 项通过, rc=0
SELFTEST 4/4 通过, rc=0
  ✔ case1_revert_fs_pct: 期望红组 ['CARD:adc_leak_offset_pct_fs'] ⇒ 实际红组 ['CARD:adc_leak_offset_pct_fs', 'P2-FS-PCT'] ⇒ 红 ✔
  ✔ case2_revert_chain: 期望红组 ['CARD:adc_decision_chain'] ⇒ 实际红组 ['CARD:adc_decision_chain', 'P1-DECISION-PRESENT'] ⇒ 红 ✔
  ✔ case3_revert_populated: 期望红组 ['CARD:adc_populated'] ⇒ 实际红组 ['CARD:adc_populated', 'P3-POP-PRESENT'] ⇒ 红 ✔
  ✔ case4_baseline: 正向对照 ⇒ 期望绿 ⇒ 实际红组 [] ⇒ 绿 ✔
  [真件] SW/SW_TIMING_REVIEW.md 读回 90918 B (自检全程只写沙盒副本)
```

### ★C4-2 · ★★★【必须给 main 看的】受保护 5 件 md5 现值 vs C2 快照的差额 = ★hw-lead 的 ISS-302 合法落表, 与本单无关★★★★

★**本趟 (2026-11-18 05:4x) 本机 `md5sum` 原样**:
```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv

2026-11-06 07:07:17.362193413 +0800  HW/PCB/demo_mainboard.kicad_pcb
2026-11-18 00:21:08.701116490 +0800  HW/netlist_v1.csv
2026-11-18 00:21:08.806117786 +0800  HW/netlist_v1_pins.csv
2026-11-18 00:21:08.953119015 +0800  HW/BOM_v1.csv
```

★**★与 §C2 快照 (2026-11-17 18:00) 逐件对照★★**:

| 件 | §C2 快照 md5 (11-17 18:00) | ★C4 现值 md5 (11-18 05:4x)★ | 变了? | ★谁改的★ |
|---|---|---|---|---|
| ★板 `demo_mainboard.kicad_pcb` ★ | `611b869e13518c3c023fb178f91a0075` | ★`611b869e13518c3c023fb178f91a0075` ★ | ★**否** ★ | ★**没变** ★ |
| ★`.kicad_pro` ★ | `3e504d2be83152e337949723e909be1b` | ★`3e504d2be83152e337949723e909be1b` ★ | ★**否** ★ | ★**没变** ★ |
| ★网表 `netlist_v1.csv` ★ | `37f62ac3f0b81d92ca7d48fdea717f07` | ★`6aee500e60ba0732f83a9cf557ba90ab` ★ | ★**是** ★ | ★**hw-lead · ISS-302** ★ |
| ★脚表 `netlist_v1_pins.csv` ★ | `a4270120454aedf7a23c92cd8985c8a6` | ★`9174309df1ec9411ac8e8d9e80ee386a` ★ | ★**是** ★ | ★**hw-lead · ISS-302** ★ |
| ★BOM `BOM_v1.csv` ★ | `5d02bece9477ffce5fbe0193c7d5cce4` | ★`5b9993992405904a60ac96a020b375d8` ★ | ★**是** ★ | ★**hw-lead · ISS-302** ★ |

★**★归因依据 (★本机实读, 不是猜★)★**:
- ★**mtime = `2026-11-18 00:21:08`** ⇒ ★**晚于本单交卷时刻 (2026-11-17 18:00) 近 6 小时 ⇒ 不可能是本单 (sw-lead) 干的★**
- ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §19 (§19.3) 逐条登记了这三件的旧 md5 → 新 md5 + 落表时刻 + 单号 = ISS-302** (★台账 L1451 网表 / L1452 脚表 / L1453 BOM / L1454 板 / L1455 `.kicad_pro`★)
- ★**落表真源 = `state/p10_rows.json` (mtime 00:21:04) + 落表脚本 = `state/_apply_iss302_csys_landing.py` (mtime 00:21:02)** ⇒ ★**走的是「改真源 → 重生成」的正路, 不是手改产物★**
- ★**hw-lead 交卷单 = `HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md` §B2-③「落表前后 md5 对照表」逐字对得上** (★旧 37f62ac3… → 新 6aee500e…· mtime 2026-11-18 00:21:08★)
- ★**落表内容 = `C_SYS` / `SYS_CHG` 由 DNP 改必装 + note 追加式订正 + BOM 加 1 颗 20 µF** ⇒ ★**与 ADC 链 / `BAT_DET` / `VBUS_DET_D` 毫无关系** ★
- ★**H-1 重锚链同跳记录在 `HW/check_pin_function_labels.py` 的 `MD5_ANCHOR_CHAIN` 里** (★本机实读, diff 见 `logs/iss302/h1_reanchor_diff.log`★)

★**★⇒ 结论: ★零写板双重自证【依然成立】(板两件 md5 + mtime 逐字节不变 = 2026-11-06 07:07:17)★; ★网表/脚表/BOM 的变动是【别的单的合法落表】, 本单 (sw-lead) 对这三件一个字节都没碰 (★本单全程只写: `SW/SW_TIMING_REVIEW.md` · `SW/tools/check_timing_review_adc_sync.py` · 本交卷单 · `state/fragments/sw.yaml` + `logs/iss293/`★)★ ★ ⇒ ★★main 验签时若拿任务书里那组旧 md5 (37f62ac3… / a4270120… / 5d02bece…) 来对, 对不上是【正常的】, 因为那是 ISS-293 交卷时刻的快照, 盘面已被 ISS-302 合法推进★ ⇒ ★**真正的零写板判据 = 官方板那两件的 md5 + mtime** (★ISS-289 交卷单自己发现的副作用: `HW/check_onepass_preflight_coverage.py` 每次跑都会重生成 `HW/PCB/` 下 4 个辅助文件 ⇒ 不看目录★)★ ★★**

### ★C4-3 · ★本趟自己跑的 F2 八条对账 (★本机逐条 grep 实读, 不抄任何 agent 报告★)★

| # | 必须有的现值 | ★本趟 grep 命中数 (本机实读)★ | 判定 |
|---|---|---|---|
| 1 | ★判决对象 = `BAT_DET` 的明文 ★ | ★`BAT_DET` = 25 处 (含 L39 / L57 / L208 / L223 / L344 / L371 / L434 / §14 卡 L575~L596)★ | ✔ |
| 2 | ★满量程 `1.8` (V) ★ | ★`1.8V` = 33 处 ★ | ✔ |
| 3 | ★LSB `0.439` (mV) ★ | ★`0.439` = 6 处 ★ | ✔ |
| 4 | ★漏电偏移 `2.1%FS` ★ | ★`2.1%FS` = 21 处 ★ | ✔ |
| 5 | ★`R_th` = `37500` (Ω) ★ | ★`37500` = 21 处 ★ | ✔ |
| 6 | ★建立时间 `33.791` (ms) ★ | ★`33.791` = 21 处 ★ | ✔ |
| 7 | ★BAT_DET 三颗**必装** 的明文 ★ | ★`必装` = 52 处 ★ | ✔ |
| 8 | ★**活结论里不再残留 3.3V 口径旧数 / ADC ❌ 行 / 「三颗全 DNP」** ★ | ★**本机实跑 `grep -nE "15\.2%FS\|0\.8057\|500kΩ\|三颗全 DNP\|三颗全部 dnp=DNP" SW/SW_TIMING_REVIEW.md \| grep -v "ISS-293 订正"` ⇒ 唯一命中 L141 = `U_LDO_S28` 的「EN 内部 500kΩ 下拉」 (★LDO 使能脚内部下拉, 与 ADC 链毫无关系 ⇒ 闸的 `ADC_CLAIM_RE` 前置过滤自动排除, 不是人工豁免★) ⇒ ★**活结论残留 = 0** ★; ★另新闸 4 项判据全绿 (`P1-DECISION` / `P2-FS` / `P3-POP` / `P4-VERDICT` 全部「无」)★ ★ | ✔ |

★**★八条全中 ⇒ 本趟【一个字节都没改文档】(★遵守 cont1 派活「只补漏, 不许整份重写」★)★**

### ★C4-4 · ★★一个环境坑 (★留给下一跳 + main 复跑时会撞上★)★★

★**`python3 SW/tools/check_demo_panel_spec.py --selftest` 在本机会撞 `OSError: [Errno 122] Disk quota exceeded`** ⇒ ★**rc=1** ★
★**根因**: ★`/tmp` 是 tmpfs (★总 7.5G · 已用 6.0G · 剩 1.6G · 80%★) ⇒ 该自检要在 `/tmp/iss212_gate_*` 下复制整棵 `HW/PCB/` 树 ⇒ 空间不够 ⇒ ★**这不是判据红, 是环境问题** ★
★**正解 (★本趟已用, rc=0 · SELFTEST 22/22★)**: ★**带 `TMPDIR` 指向大盘** ★
```bash
TMPDIR=/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss293_tmp \
  python3 SW/tools/check_demo_panel_spec.py --selftest
# ⇒ --- SELFTEST 22/22 通过 ---
```
★**⇒ ★★main 复跑这 10 条时, 第 7 条务必带 `TMPDIR` (★不然会误判成「别的闸红了」★)★★**

### ★C4-5 · ★本趟分片登记 (★走 `state/frag_write.py` 原子写★)★

★**脚本** = `logs/iss293/frag_cont2.py` (★本趟新写 · 走 `frag_write.py` 的 CLI 路径, 值用 `shlex.quote` 包好★) ⇒ ★**rc=0 · 原样输出**:
```
[frag_write] ✅ sw.yaml 已原子更新 → 再跑 python3 state/merge.py
```
★**落的东西 (★3 处★)**:
1. ★**`interface_claims` 新增 `iss293_cont2_indep_reverify_20261118_0545`** = ★本趟 10 条回归的 rc + F2 八条 grep 命中数 + ISS-302 md5 差额归因 + TMPDIR 坑★
2. ★**`status` 块更新** = ★`phase=delivered` / `progress_pct=100` / `health=green` / summary = 本单交卷摘要 + ISS-302 md5 附注 + 「要 main 拍板的只剩 M7-R6 一件」★
3. ★**`answers` 块里原有的 `ISS293_ADC_REVIEW_SYNC_DELIVERED` 保留未动** ★

★**★原有 3 件 artifacts (★交卷单 / `SW/SW_TIMING_REVIEW.md` / `SW/tools/check_timing_review_adc_sync.py`★) + 原有 5 条 `interface_claims` (`adc_full_scale_caliber_iss293` / `iss293_adc_decision_chain_current` / `iss293_vbus_det_d_is_digital_not_adc` / `iss293_bat_det_populated` / `iss293_review_doc_pinned_by_gate`) + 原有 3 条 needs (`iss291_sw_vbus_det_d_digital_caliber` / `iss291_sw_do_not_apply_vbus_100k47k` / `iss293_sw_m7r6_sync_to_main`) ★全部保留 (★一条没删★)★ ⇒ ★**`grep -c iss293 state/fragments/sw.yaml` 本趟写完 = 14 (★≥ 4 达标★)****

★**★并发安全自证 (★本机实读★)**: ★本单写分片时, 同 agent 的兄弟会话 (ISS-298 / ISS-309) 也在写同一份分片 ⇒ ★**本趟写完复查**: ★`iss298_sw_reboard_channel_wired` = 1 处 / ★`iss309` 相关 = 28 处 / ★`iss293_sw_m7r6_sync_to_main` = 4 处 / ★`iss291_sw_vbus_det_d_digital_caliber` = 3 处 / ★`iss291_sw_do_not_apply_vbus_100k47k` = 2 处 ⇒ ★**兄弟会话的数据一条没丢 (★`frag_write.py` = 读 → 改 → tmp + fsync + `os.replace` 原子写★)★**

### ★C4-6 · ★★★本交卷单的【占位符残留自检】= 项目口径 0 (★且是【真零】, 不是自匹配出来的假零★)★★★

★**★本趟 (cont2) 发现并订正了上一趟 (2026-11-17 17:5x) 的一个【自检口径错误】★** ⇒ ★**见上文 §B6.5 的【订正行】★** ⇒ ★**这里只把【订正后的真零读数】贴出来★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
F="HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md"
PAT="$(printf '\360\237\224\204')|$(printf '\345\276\205\345\241\253')"   # ★项目口径两型 (UTF-8 字节转义, 免得文档自己命中自己★)
grep -cE "$PAT" "$F"
```

★**本趟实跑原样输出**: ★**0** ★ ⇒ ★**项目口径的占位符残留 = 0** ★

★**★交叉验 (★用项目现成的共享闸, 独立口径★)**:
```bash
python3 state/check_report_placeholders.py HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md; echo "rc=$?"
```
★**原样输出**:
```
✔ 无占位符 (★可发)
rc=0
```
★**⇒ 两个独立口径都判 0 ⇒ 真零★**

★**★B0~B6 七块的占位符残留 grep 结果 (★任务书 §⑮ F1 要的那一项★) = ★0★** ★ ⇒ ★**本交卷单 B0 / B1 / B2 / B3 / B4 / B5 / B6 七块全部填满, 没有一处是未填的空位** ★

### ★C4-7 · ★本趟 (cont2) 交卷前最终一遍回归 (★交卷单写完之后重跑, 证明改交卷单没把别的闸带红★)★

★**日志**: `logs/iss293/cont2_final_gates2.log` ★**原样输出**:
```
[SW/tools/check_timing_review_adc_sync.py] rc=0
[SW/tools/check_timing_review_adc_sync.py --selftest] rc=0
[SW/tools/timing_check.py] rc=0
[SW/tools/check_demo_panel_spec.py] rc=0
[SW/tools/check_demo_panel_spec.py --selftest] rc=0
[state/merge.py] rc=0
[state/gate_check.py] rc=0
[state/issue_check.py] rc=0
```
★**⇒ 8/8 全 rc=0** ★

---

## ★附 B · 给 main 的三句话 (★我不拍★)★

1. ★**文档口径已钉死**: `SW/SW_TIMING_REVIEW.md` 的 ADC 段 = `BAT_DET` 链 (37500.0Ω / 33.791ms / 2.1%FS / 节点 1.575V ≤ 1.98V) ⇒ ★**那条「ADC 不通过」是假红, 已作废** ★⇒ ★**「板只改一次」那一趟不必、也不该因为 ADC 链去改板** ★
2. ★**M7-R6 要不要同步改 `SW/SW_REQUIREMENTS.md`** ⇒ ★**建议同步改 (判据按 `BAT_DET` 现值), 但需求真源是 PM 域 ⇒ 我只登记了 need `iss293_sw_m7r6_sync_to_main`, 请你派单** ★
3. ★**`VBUS_DET_D` 的三个硬件未决仍开着** (DRD1 内部 40kΩ 下拉 / IO 域与 abs-max / 识别裕量 75mV) ⇒ ★**要转 hw-lead, 别让它随本单一起被当成已闭合** ★

---

## ★B7 · 交卷后追记 (★签字 / 派活留痕位·★本单不自签 issue_log★)★

| ★项★ | ★内容★ |
|---|---|
| ★交卷时刻★ | ★2026-11-17 17:5x (★本趟 cont1 续做 · 上一趟会话 17:05:53→17:18:06 status=failed ⇒ 本趟只补交卷单 + 对账 + 回归 + 分片, 大块没重做★)★ |
| ★交卷人 / 验签人★ | ★交卷 = sw-lead · ★验签 = main (★**sw-lead 不自签 issue_log**★)★ |
| ★待 main 验签项★ | ★① §B1.3 八条对账表 (★26 行带订正标记 + §14 机器卡 17 键★) ★② §B6.1 回归 8 条原样 rc ★③ §B6.2 反向用例 4 条 (期望红组 vs 实际红组) ★④ §C2 受保护 5 件 md5 + 板 mtime ★⑤ §B5 未决项 4 条 (★M7-R6 是否同步改 = 你拍★) ★ |
| ★本单【没有】做的事 (★留痕, 免得被当成漏做★)★ | ★没改 `SW/tools/timing_check.py` · 没改 `SW/tools/check_demo_panel_spec.py` · 没改 `SW/SW_REQUIREMENTS.md` · 没碰 `HW/` 与 `MECH/` 的任何文件与分片 · 没跑 `HW/check_onepass_preflight_coverage.py` (★它会重生成 `HW/PCB/` 下 4 个辅助文件★) · 没发任何邮件/询价/问询/采购 (★零外发★) · 没签 issue_log ★ |
| ★后续追记位 (★留给下一跳★)★ | ★① 若 main 拍板改 M7-R6 ⇒ 改完跑 `python3 state/merge.py && python3 state/gate_check.py` (★rc 必须 0 / Q1 18/18★) ★② 若「板只改一次」那一趟真要动 `VBUS_DET_D` 链 ⇒ ★**先跑本单新闸确认文档口径没漂** ★③ 若闸的判决源 (脚表 / 网表) 再变 ⇒ ★**改闸 → 改 §14 卡 → 跑新闸** 三步不许省 ★ |
