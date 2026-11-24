# ISS-401 · hw-lead 任务书 —— ★★【HW 域外部依赖挂账全量自查收口】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead (硬件总工) · ★**verify_by**: main
> ★**单号**: ISS-401 · ★**job**: cron `fb67af40` (ARS45 队列自动派活 · 每 30 分钟)
> ★**性质**: ★**内部活 · 政策落地 (义务侧) + 需求闭环 / 卫生类** ⇒ ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★
> ★**零写板 · 零落表 · 零改既有闸阈值 · 零改既有页正文 · 零外发 · 不代老板拍板 · 不自签 issue_log** ★
> ★**主线口径**: 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属**纯查证/分析类**, **不动板** ⇒ 合「板只改一次」纪律 ① ★

---

## ★0 · 一句话 ★

★★**HW 域是三个总工里【唯一还没做外部依赖自查收口】的域**: SW 域已做 (ISS-270 / ISS-357 均 verified), MECH 域已做 (ISS-313 verified) ⇒ **HW 域至今仍有 10 条需求路由指着外部 (vendor/jbd) + 6 条 blocker 写着「等原厂」+ 网表里 109 行带 `tbd` 标签 / 36 行 `evidence=[待原厂]`** ⇒ ★**违反老板 2026-11-11 19:31 + 2026-11-12 02:02 口径「不再发信, 全靠自己查资料」的第 ② 半 (义务侧) ⇒ 而板那一趟要对着一个【不再变的网表】画 ⇒ 挂着 `[待原厂]` 的网表行 = 板改第二次的种子** ★★

---

## ★1 · 病灶 (★main 2026-11-24 23:1x 本机实读 + 实算 · 不抄任何 agent 报告★) ★

### ★1-1 · HW 域自己的账 (`state/fragments/hw.yaml` · `needs_from` = **312 条**) ★

| 维度 | 实读分布 |
|---|---|
| `to` | `main` 251 / `mech-lead` 28 / `sw-lead` 16 / `boss` 12 / `落表批次` 3 / ★**`vendor` 1 / `jbd` 1**★ |
| `waiting_on` | `agent` 19 / `boss` 11 / ★**`vendor` 6 / `jbd` 2**★ / `main` 1 |

⇒ ★**8 条需求挂着外部依赖** (waiting_on = vendor 6 + jbd 2) + **2 条 `to` 直接指向外部** (vendor 1 + jbd 1) ⇒ **共 10 条外部路由** ★

★**逐条清单 (★key / to / waiting_on / due / 原 item 摘要★) —— 本单要逐条收口的就是这 10 条 + 下面 6 条 blocker + 13 项 TBD★**:

| # | key | to | waiting_on | due | 原 item 摘要在盘位置 |
|---|---|---|---|---|---|
| 1 | `q16_display_iface` | main | vendor | 2026-10-29 | Q16 显示 TX 接口结论 (DSI TX / DP TX / 两者) + 宽高比 A/B/C 拍板 |
| 2 | `vendor_ars45_paper_q11_q16` | ★vendor★ | vendor | 2026-10-29 | 原厂纸面资料 8 问 (10-21 邮件已发未回): ① FCCSP pitch + 球位图 ② 电源域 ③ 显示 TX ④ USB Device PHY ⑤ 内置 boot storage ⑥ MCLK 源 + sensor RESET 极性 ⑦ SoC 散热焊盘 ⑧ CSI 2/4 lane + 输入电压域 |
| 3 | `jbd_zoushe_dsi_spec` | ★jbd★ | jbd | 2026-10-28 | 走鹃II: ① DSI 几 lane / 最高速率 ② 800×600@60fps 官方验证过没 ③ I2C 做什么用 + 从机地址 ④ 供电电压范围 + 峰值电流 |
| 4 | `rel_vendor_absmax_rating` | main | vendor | 2026-10-30 | 15 个器件 Absolute Maximum Ratings (温度/电压/电流) + 可靠性数据 (FIT/MTBF/降额曲线); 另需 BQ25896 工作温度范围 / TMP117 供电范围 / Type-C 母座温升-电流曲线 |
| 5 | `rel_battery_cell_spec` | main | vendor | 2026-10-30 | 1S LiPo 电芯规格书: 允许充电倍率 + 循环寿命 + 内阻 + 膨胀曲线 + 允许充/放电温度窗口 |
| 6 | `iss067_vendor_r_on_u1` | main | vendor | 2026-10-31 | TPS62130A 高边 R_on + 推荐电感 DCR 合计值 ⇒ 决定 UVP 能不能从 3.50V 压到 3.35V (假设 R_total=100mΩ ⇒ 地板 3.335V ⇒ 方案 A' 成立; >150mΩ ⇒ 退回 3.50V) |
| 7 | `iss067_jbd_vdd_tol_u2` | main | jbd | 2026-10-31 | 光机 3.3V 输入电压容差与下限 (UVP 3.35V 时 buck 输出 ≈3.305V); 假设 ±5% ⇒ 成立; 若要求 ±2% ⇒ 卡边需确认 |
| 8 | `rk3572_isp_throughput_max` | main | vendor | 2026-11-04 | RK3572 官方 ISP 吞吐上限 (MP/s @ 什么位深/几路并发) —— 需求侧已钉死 (1080p60 = 124.4MP/s; 全分辨率 4K60 = 497.7MP/s; 项目一直用的 250MP/s 是媒体口径) |

★**另 2 条 `to=外部` 的** = #2 `vendor_ars45_paper_q11_q16` (`to=vendor`) + #3 `jbd_zoushe_dsi_spec` (`to=jbd`) ⇒ ★**上面表里已经含这 2 条** ⇒ **8 条 waiting_on + 这 2 条 = 10 条** ★

★**★这 8 条 key 在 `state/fragments/hw.yaml` 里各只出现 1 次 (★grep 实测★) ⇒ 只作为 needs 挂着, **没有一条有自查结论 / 没有一条被答** ⇒ ⇒ 老板清单里的「等外部」一直挂着 ★★**

### ★1-2 · HW 域 `blockers` = 7 条, 其中 **6 条写着「等原厂」** ★

| id | severity | needs_from | waiting_since | 摘要 |
|---|---|---|---|---|
| HW-B1 | high | ★**vendor**, main★ | 2026-10-24 | ARS45 显示输出接口未确认 (DSI TX? DP TX? 两者?) |
| HW-B2 | high | ★**vendor**★ | 2026-10-25 | FCCSP 球间距未拿到 → 逃线/叠层结论给不出 (pitch 已升级为 SoC 选型一票否决项) |
| HW-B3 | high | ★**vendor**★ | 2026-10-25 | 电源域电压/电流上限全未知 → 电压域清单写不出来 |
| HW-B4 | high | ★**vendor**, main★ | 2026-10-25 | 启动存储/固件分区: 有无内置 boot storage 未知 |
| HW-B5 | medium | main, ★**vendor**★ | 2026-10-26 | R-F1 3.3V 轨拓扑残留 (含 3 条外部依赖: 原厂 R_on / JBD 容差 / 老板拍板) |
| HW-B6 | high | ★**vendor**, main★ | 2026-10-26 | 可靠性证据缺口 (15/15 器件 Absolute Maximum Ratings 未核) |
| HW-B7 | high | 无 | — | R-GEO 六问 0 答复 (内部/ISP 口径, **不是外部依赖** ⇒ 本单不碰, 但要写明「不是外部依赖, 别混进清单」) |

⇒ ★**6 条 blocker 等原厂 ⇒ 老板清单里的「等外部 46 条」里有相当一部分来自 HW 域** ★

### ★1-3 · 网表侧 (★板要对着它画的那份真源★) ★

`HW/netlist_v1.csv` (实读, 2026-11-24 23:1x):

| 口径 | 数字 | 分布 |
|---|---|---|
| 带 `tbd` 标签的行 | **109** | TBD-01 6 / TBD-02 12 / TBD-03 25 / TBD-04 24 / TBD-06 6 / TBD-10 3 / TBD-11 4 / TBD-12 27 / TBD-13 2 |
| `evidence=[待原厂]` 的行 | **36** | ★**全部 36 行 board=MAIN_PCB**★ |

★**TBD-01..TBD-13 = 「13 项画不了清单」** (口径出处: `HW/ERC_DRC_CHECKLIST.md` §A5「TBD 编号落在 TBD-01..TBD-13 (对应 13 项画不了清单, 编号一致)」· 清单原文在 `HW/SCHEMATIC_L1.md` / `HW/SCHEMATIC_V1_SPEC.json`)
⇒ ★**网表 CSV 里只出现 9 个标签** (TBD-05 / TBD-07 / TBD-08 / TBD-09 不在 CSV 里, 只在文档中) ⇒ ★**收口必须以「13 项」为准, 不能只扫 CSV** ★

### ★1-4 · ★★为什么这条挂在「板只改一次」的关键路径上★★ ★

★**① 网表是板要对着画的那份真源**: ★`HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` INV-1 明确「板 md5 全生命周期内变更次数 ≤ 1」⇒ ★**凡会改网表真源的动作 (含把 `[待原厂]` 落成实值) 必须与板那一趟同批** ⇒ ★**今天挂着 `[待原厂]` 的 36 行 (全 MAIN_PCB) + 109 行 TBD = 板那一趟开工当天仍有 145 行可能动网表** ⇒ ★**动网表 ⇒ 板 md5 第二次变 ⇒ Gerber / 投产包 / 留证链 / 盖章 / 发布全部白跑** ★★

★**② 坏结局只有两种, 都伤「板只改一次」**:
- ★**结局 A**: 板那一趟开工时才发现 `[待原厂]` 的行要落值 ⇒ 网表改 ⇒ 板 md5 第二次变 ⇒ **那一趟作废**
- ★**结局 B**: 带着 36 行 `[待原厂]` 直接投板 ⇒ 板上有 145 行的值没定 (含 TBD-03/04 的高速差分对、TBD-12 的上电时序) ⇒ **这是一张能出厂但不该出厂的板** ★

★**③ 现在没人管**: SW 域 2026-11-17 收到 ISS-270 (5 条) + ISS-357 (needs 144 条四分类); MECH 域 2026-11-18 收到 ISS-313 (needs 184 条四分类 + 16 条外部依赖) ⇒ ★**HW 域 (needs 312 条 + 6 条 blocker) 是三域里唯一没做过的** ★★

### ★1-5 · ★★同型先例 (★照着做, 不用重开脑洞★) ★★

| 单号 | 域 | 形状 | 状态 |
|---|---|---|---|
| ISS-270 | SW | ★5 条「干等原厂 / 等外部回复 / 待确认」逐条换成【自己查的结果 + 证据等级 + 降级方案】★ | verified |
| ISS-357 | SW | ★SW 域 needs 144 条四分类处置 (含 `to=vendor` 8 条)★ | verified |
| ISS-313 | MECH | ★MECH 域 needs 184 条四分类处置 (waiting_on vendor 10 / jbd 6)★ | verified |
| ★**ISS-401 (本单)** ★ | ★**HW**★ | ★**HW 域 needs 312 条四分类 + 10 条外部路由 + 6 条 blocker + 13 项 TBD 收口**★ | ★**本单**★ |

---

## ★2 · 本单要交的 5 件东西 (★交卷物 (5 件)★) ★

1. ★**真相页** `HW/HW_EXTERNAL_DEPENDENCY_SELFCHECK_CLOSURE.md` (★新建★)
   ⇒ ★**逐条** (10 条 needs + 6 条 blocker + 13 项 TBD) 给: ① 自己查的结果 (★官网链接/文档章节/行号★) ② **证据等级五级** ③ 查不到就写**降级方案 (必须项)** ④ ★**现在还卡不卡「板只改一次」那一趟** (卡 / 不卡 / 条件卡 + 判据出处)★ ⑤ 路由改成什么 (needs 的 `to` / `waiting_on` 改到哪 / 或维持) ★
2. ★**新机器闸** `HW/check_hw_external_dep_closed.py` (★新建★)
   ⇒ 判据见 §4; ★**裸跑 rc=1 (★红的是现状★)** + ★`--selftest` rc=0 末行 `ALL TESTS PASS` (★正向 ≥1 + 反向 ≥6★) ★
3. ★**交卷页** `HANDOFF/2026-11-24_hw-lead_ISS401_HW域外部依赖自查收口.md` (★新建★) ⇒ ★**B1~B7 全填**, ★**B2/B3/B4 标题必须用标准口径** (`验收标准自评` / `证据分级` / `接口取值声明`) ⇒ ★**闸只扫标题行** (★`state/gate_check.py` 的 `check_blocks()` + 关键词表 L49-51★) ⇒ ★**标题不合规 ⇒ Q1 掉到 15/18 ⇒ 三张签收闸全卡** ★
4. ★**分片收口** (★只写 `state/fragments/hw.yaml`, 不许碰别的分片★) ⇒ §5 有逐字写法
5. ★**留证** `logs/iss401/` (★裸跑/自测输出 + 关键命令原文★)

---

## ★3 · ★★可直接用的现成结论 (★别重查·★这些是盘上已有结论★) ★★

★**这些是 main 本机实读到的既有结论, 直接引用即可 (★但要自己复核一遍并标 `[实测]`★)★:

| 主题 | 既有结论 | 出处 |
|---|---|---|
| ★**TBD-01 对 demo 板已不阻塞**★ | ★**主板走 RK3572 核心板 (SoM) 路线 ⇒ 主板不碰 SoC 球位号 ⇒ TBD-01 对 demo 板不再是阻塞**★ | `HW/DEMO_BOARD_HW_DECISION.md` (★「TBD-01 对 demo 板不再是阻塞」一句在 L48 附近★) |
| ★**TBD-01 可自查关掉**★ | ★F2: **`J_SOM_P2.pin7` 官方默认功能 = PWM0_CH1_M0, 我们拿它当 UART_TX 用** ⇒ ★**TBD-01 可用官网数据直接关 (TX=O / RX=I / 3.3V / 单端), 不需要问任何人**★ | `HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md` §5 F2 (★ISS-204 已 verified★) |
| ★**TBD-05 = 查不到**★ | ★**FCCSP pitch: 官网 + 百科 + 招股书 + 封装拆解检索 ⇒ 无公开数据 [0数据]**★ | `HW/ONLINE_FINDINGS_2026-10-26.md` §7 |
| ★**存储档 (TBD-06 / TBD-11) 已三档化**★ | ★① 只 ADB push 档 (demo) ⇒ **板侧零动作** ② 外挂 SPI-NOR 档 (≥128 MiB) ⇒ 走 `J_BOOT1` 焊盘位 (6 pad 已在板 @126.3,58) + 4 条 0Ω 串阻位必装 ⇒ **板侧零动作 · 不改板宽 · 不重出板** ③ eMMC 档 ⇒ 板宽 12→15mm ⇒ 台架板档代价 ≈ 0 ⇒ **台架板档与产品板档都不卡** ⇒ ★**只有产品板档卡 (时限型)**★ | ★`state/fragments/hw.yaml` 的 `risks` · `R-hw-boot-storage` (★ISS-346 / ISS-350 机器判决★) |
| ★**ERC 清单里的「原厂 4 项未闭」可能已过期**★ | ★`HW/ERC_DRC_CHECKLIST.md` §表头写「🔴 未闭 (TBD-01/02/04/06/11)」+ §D1 写「原厂 4 项闭合 ⇒ 酷芯微书面答复」⇒ ★**这是 2026-10 的口径, 而 SoM 路线已把 TBD-01 解除** ⇒ 本单要逐条核一遍「现在还闭不闭」★ | ★`HW/ERC_DRC_CHECKLIST.md` ★ |
| ★**SoM 侧球位/脚位真值已有交叉核对件**★ | ★RK3572 模组侧球位核对已做过 (★`HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md` = 老板 2026-11-12 02:2x 那条【自己查掉唯一一条真外部依赖】的范例★) ⇒ ★**这就是本单要复制的形状: 靠官网手册自己查 + 落证据文档**★ | `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md` ★ |
| ★**网表侧已有同型硬缺陷作业包 (★别重复做★)** | ★**4 行接地硬缺陷 + `R_PU_PG` 脚序** 已被 ISS-366 做成逐字改法 + 沙盒 + 新闸 ⇒ ★**本单不碰网表真源, 也不重复做那 4 行**★ | ★`HW/PCB/BOARD_ONEPASS_NETLIST_ROW_FIX.md` + `HW/check_netlist_gnd_rows.py` (★裸跑 rc=1 = 现状★) |

---

## ★4 · ★新闸判据 (★**新建** `HW/check_hw_external_dep_closed.py` · 5 条★) ★

★**设计口径**: ★**裸跑 rc=1 (红的是现状) · `--selftest` rc=0** ⇒ ★**闸不许自证「已经好了」, 只许如实报「还差什么」** ★

| 判据 | 内容 | 现状应红的原因 |
|---|---|---|
| ★**D1**★ | ★**HW 域 `needs_from` 里不许再有 `waiting_on ∈ {vendor, jbd}` 的条目** ⇒ 现状 **8 条** ⇒ 红 | ★现况 6 vendor + 2 jbd★ |
| ★**D2**★ | ★**HW 域 `needs_from` 里不许再有 `to ∈ {vendor, jbd}` 的条目** ⇒ 现状 **2 条** ⇒ 红 | ★`vendor_ars45_paper_q11_q16` / `jbd_zoushe_dsi_spec`★ |
| ★**D3**★ | ★**网表 `HW/netlist_v1.csv` 里 109 行 `tbd` + 36 行 `evidence=[待原厂]` 必须 100% 被真相页的收口条目覆盖** (★覆盖率 = 已登记行数 / 现状行数★) ⇒ 现状 **0%** ⇒ 红 | ★真相页在本单之前不存在★ |
| ★**D4**★ | ★**真相页里每条收口条目必须同时有【证据等级】和【降级方案或结论】** ⇒ 缺一即红 | ★同上★ |
| ★**D5**★ | ★**每条收口条目必须写【还卡不卡板那一趟】(卡 / 不卡 / 条件卡) + 判据出处** ⇒ 缺一即红 | ★同上★ |

★**D1/D2 的收口方式**: ★**改 `state/fragments/hw.yaml` 的 `needs_from`** ⇒ ★**不许删条目 (★删条目 = 把问题藏起来★) ⇒ 只许改 `to` / `waiting_on` / `item` 三栏, 并在 `item` 里写清自查结论 + 证据等级 + 降级方案** ⇒ ★**`to` 改成谁由你按内容定 (自查结论成立 ⇒ `to=main`; 确实还需要外部 ⇒ 明确写「已降级, 不再阻塞」并把 `waiting_on` 清空)** ★★

★**`--selftest` 要求**: ★**正向 ≥1 (现状判定能红) + 反向 ≥6 (每个判据至少一条反向用例: 伪造一个合规样例 ⇒ 判据必须转绿; 伪造一个缺字段样例 ⇒ 判据必须转红)** ⇒ ★**末行必须打 `ALL TESTS PASS`** ★

★**★闸不许做的事★**: ★**不许判 md5** · ★**不许改既有闸的阈值** · ★**不许把"红"当成"闸坏了"** ⇒ ★**裸跑 rc=1 是预期, 交卷时必须说明「红的是现状还是闸故障」** ★

---

## ★5 · ★分片收口写法 (★照抄这个流程, 别自己发明★) ★

★**`state/frag_write.py` 的 `--set` / `--set-json` 与 `--add-*` / `--status` 互斥 (★V1.1 修过的坑: 混用会静默吞掉增量★) ⇒ 必须拆成两条命令★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
mkdir -p tmp/iss401
cp state/fragments/hw.yaml tmp/iss401/hw.yaml.bak          # ★改前备份★
python3 state/frag_write.py --agent hw-lead --show > tmp/iss401/needs_from_before.json
# ★★在 tmp/iss401/needs_from_after.json 里逐字改那 10 条 (★其余 302 条一个字都不许动★)★
python3 state/frag_write.py --agent hw-lead --set-json tmp/iss401/needs_from_after.json --set-field needs_from
python3 state/frag_write.py --agent hw-lead --add-artifact 'path=HW/HW_EXTERNAL_DEPENDENCY_SELFCHECK_CLOSURE.md summary="..." kind=doc'
python3 state/frag_write.py --agent hw-lead --add-claim 'key=iss401_hw_external_dep_closure value="..." note="..."'
python3 state/frag_write.py --agent hw-lead --add-answer 'key=iss401_hw_external_dep_closure to=main value="..." ref=HANDOFF/2026-11-24_hw-lead_ISS401_HW域外部依赖自查收口.md'
```

★**改后自检 (★必做·★否则等于把 312 条分片毁了★)**:
```bash
python3 - <<'PY'
import yaml
a=yaml.safe_load(open('tmp/iss401/hw.yaml.bak'))['needs_from']
b=yaml.safe_load(open('state/fragments/hw.yaml'))['needs_from']
ka={x['key'] for x in a}; kb={x['key'] for x in b}
print('条数', len(a), '->', len(b))
print('丢的 key:', sorted(ka-kb))
print('多的 key:', sorted(kb-ka))
diff=[x['key'] for x,y in zip(a,b) if x!=y]
print('内容有变的条:', diff)
PY
```
⇒ ★**期望: 条数 312 → 312 · 丢的 key = 空 · 多的 key = 空 · 内容有变的条 = 恰好那 10 条 (或写明增减原因)****

★**★另外: `blockers` 段怎么办★**: ★**`blockers` 是 list, `frag_write.py` 没有 `--set-blockers` 之外的细粒度参数** ⇒ ★**优先在真相页里逐条写清结论 (HW-B1~B7) + 用 `--add-claim` 登记「哪些 blocker 已解除 / 哪些已降级」** ⇒ ★**若你确实要改 `blockers` 段, 只能用 `--set-json` + `--set-field blockers`, 且必须逐字保留 7 条里未改的条目 (★并在交卷页 B7 写明改了几条、哪几条、逐字前后★)****

---

## ★6 · ★交卷前必跑 (★跑完把输出原样贴进交卷页 B6★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★本单新建的闸 (★裸跑 rc=1 = 红的是现状; ★--selftest rc=0 末行 ALL TESTS PASS★) ★
GATE=HW/check_hw_external_dep_closed.py
python3 "$GATE"                          # ★裸跑: rc=1 (红的是现状) ★
python3 "$GATE" --selftest               # ★rc=0 · 末行 ALL TESTS PASS ★
python3 state/merge.py                   # ★rc 必须 0 ★
python3 state/gate_check.py              # ★Q1 必须 18/18 ★
```

★**★边界自证 (★必做·★把 md5 前后对比贴进交卷页 B7★)** ★

```bash
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       state/gen_netlist.py state/gen_pcb_netlist_board.py state/land_v_values.py state/decision_truth.py
```
★**收工时这 8 个 md5 必须与开工时逐字相同** ★

| 基准 md5 (2026-11-24 23:1x 实测) | 文件 |
|---|---|
| `611b869e13518c3c023fb178f91a0075` | `HW/PCB/demo_mainboard.kicad_pcb` (★4,940,213 B · mtime 2026-11-06 07:07:17★) |
| `6aee500e60ba0732f83a9cf557ba90ab` | `HW/netlist_v1.csv` |
| `9174309df1ec9411ac8e8d9e80ee386a` | `HW/netlist_v1_pins.csv` |
| `5b9993992405904a60ac96a020b375d8` | `HW/BOM_v1.csv` |
| `aff5a6d98f473c0d65720f653a75fa22` | `state/gen_netlist.py` |
| `e6e7e0b36003f0a129170f5172b1381a` | `state/gen_pcb_netlist_board.py` |
| `4032aaf308d545179a6f8d8b7129c49d` | `state/land_v_values.py` |
| `28254f1d48fd48c17628693aaa3fe0b4` | `state/decision_truth.py` |

---

## ★7 · ★边界 (硬 · 违反即交卷不收★) ★

| # | 边界 | 说明 |
|---|---|---|
| 1 | ★**零写板**★ | `HW/PCB/demo_mainboard.kicad_pcb` 一个字节都不许动 (★md5 见 §6★) |
| 2 | ★**零落表**★ | ★**网表 / 脚表 / BOM / 两个生成器 / `state/land_v_values.py` / `state/decision_truth.py` 一个字节都不许动** ⇒ ★**本单交的是【收口结论 + 改法 + 闸】, 不是【改动】**★ |
| 3 | ★**零改既有闸阈值**★ | ★不许改任何既有 `check_*.py` 的判据/常量★ ⇒ ★**只许新建闸**★ |
| 4 | ★**零改既有页正文**★ | ★既有文档一个字都不许改 (★只许新建真相页 + 交卷页★) ⇒ ★**要改既有文档的, 写成 needs_from 给 main**★ |
| 5 | ★**零外发**★ | ★**不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**没有"批一句可以发"这个选项**★ ⇒ ★**`state/outbox/` 的草稿一律不发**★ |
| 6 | ★**不代老板拍板**★ | ★要 main/老板裁的, 一律登记成 `needs_from` (`to=main`) ★ |
| 7 | ★**不自签 issue_log**★ | ★`state/issue_log.yaml` 你一个字都不许动 (★签收是 main 的地界★) ★ |
| 8 | ★**零挂链**★ | ★**新闸不挂 `state/gate_check.py` / `state/daily_check.py`** (★挂不挂 = main 的地界, 写成 needs_from★) ★ |
| 9 | ★**只写自己的分片**★ | ★只许写 `state/fragments/hw.yaml` (★走 `state/frag_write.py`·★**禁止 `open(p,"w")` 直接改分片★★) ★ |
| 10 | ★**沙盒不写 `/tmp`** ★ | ★系统 `/tmp` 配额已满 (★2026-11-23 04:4x 实测★) ⇒ ★**沙盒落 `tmp/iss401/`** ★ |

---

## ★8 · ★证据等级 (★五级·固定·每条结论都要标★) ★

| 级别 | 含义 |
|---|---|
| ★`[官网]`★ | 厂商官网 / 官方 datasheet / 官方手册 (★**要贴链接或文档章节 + 版本号**★) |
| ★`[实测]`★ | 本机可复现 (★**要贴命令 + 输出原文**★) |
| ★`[媒体]`★ | 媒体 / 二手 / 论坛 |
| ★`[推算]`★ | 由实测数据推得 (★**要写清推理链**★) |
| ★`[0数据]`★ | 查不到 (★**必须同时给降级方案**★) |

★**查不到不是失败, 挂「等原厂」才是失败** ⇒ ★**每条 `[0数据]` 都必须带降级方案 (实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开它 / 板侧零动作)** ★

---

## ★9 · ★留给 main 的问句 (★本单一律不代拍★) ★

① ★**HW-B1~B7 里的哪些条可以正式解除/降级** (★你只给结论 + 判据, 解除动作归 main★) ★
② ★**10 条 needs 的 `to` / `waiting_on` 各自改成什么** (★你给建议 + 代价, 落表归 main★) ★
③ ★**TBD-01..TBD-13 里哪几条还卡「板那一趟」** (★这一条直接决定板那一趟的开工清单★) ★
④ ★**新闸挂不挂链** (★建议: 先落完 D1/D2 再挂, 否则等于往官方链挂一道永久红的闸★) ★
⑤ ★**网表里 36 行 `[待原厂]` 归谁落** (★是同一趟同批, 还是拆批★ ⇒ 直接影响板 md5 变更次数★) ★

---

## ★10 · 一句话纪律 (★抄给收工前最后看一遍★) ★

★★**本单的价值不在"又查了一遍", 在"HW 域这 10 条外部依赖从此不再是阻塞项": 每一条要么自己查掉了 (附官网链接 + 证据等级), 要么写清了降级方案 (附判据) ⇒ 老板清单里的"等外部"能真正减下来, 板那一趟的网表能真正冻结 ⇒ ⇒ 而这一趟板 md5 只许变一次** ★★
