# SW/SW_NEEDS_TRIAGE.md —— SW 域 needs 144 条四分类逐条处置 (ISS-357)

> **owner**: sw-lead (软件总工) · **单号**: ISS-357 · **日期**: 2026-11-23 · **job**: cron `fb67af40` (ARS45 队列自动派活)
> **同源**: 本页 + `HANDOFF/2026-11-23_sw-lead_ISS357_SW未答需求分类.md` + `state/fragments/sw.yaml` 三段台账全部由 `logs/iss357/iss357_data.py` 生成 ⇒ 同源不重写。
> **边界 (硬)**: ★零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log★
> **证据分级**: `[官网]` (= 机检标签集里的「官方」, 结构域习惯叫「官网」) / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` —— 四档齐 + 推算/0数据按需追加。

---

## §0 · 口径 (先说清「这一页在算什么」)

★**机检口径** (`state/gate_check.py` 实读, 本单零改闸):

```
real_open = needs_total − needs_answered_incoming − needs_closable_unregistered − needs_waiting_external
needs_waiting_external = waiting_on != 'agent'   (boss / vendor / sw-lead 都算「等外部」, 不算谁的锅)
```

⇒ ★**本单的三个动作, 全部落在口径之内, 一个字不改闸**★:

| # | 动作 | 对机检的作用 | 是否「把 needs 删空」 |
|---|---|---|---|
| 1 | **已结 / 已作废**的 need 从 `needs_from` 移出 ⇒ 进 `needs_closed` (每条带 `reason` + `evidence` + `evidence_level` + `closed_at` + `closed_by`) | `needs_total` 与 `real_open` 同时 −1 | ✗ 不是删空 —— ★**每一条都带依据行, 原 `item` 全文一字未删, 全部留档在 `needs_closed`★** |
| 2 | **其实在等老板**的 need, `waiting_on` 从空/`agent` **订正**为 `boss` | `real_open` −1, `needs_waiting_external` +1 | ✗ 不是删条目 —— ★**条目原样留在 `needs_from`, 只是把「等谁」标对★** (依据 = 条目正文自己写着「等老板, 项目总工转达」) |
| 3 | **真·待答**的 need 留在 `needs_from` ⇒ 逐条写进 `needs_open_ledger` (owner + 一句话问法 + why + evidence + 是否与板那一趟相关) | 不改数, 但★**下轮按 owner 直接派, 不用再逐条读 144 条★** | ✗ 不是删条目 |
★**本单绝不做的三件事**: ① 不改 `state/gate_check.py` / `state/merge.py` / `SW/tools/` 下任何脚本一个字 ② 不改任何 `decision` 字段代老板拍板 ③ 不发任何邮件 / 询价 / 问询 / 采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信, 全靠自己查资料」)。

---

## §1 · 总账 (关 74 / 留 70 / 新答 9)

| 维度 | 数 | 说明 |
|---|---|---|
| ★原 `needs_from`★ | **144** | 本单逐条读过, 一条一条看过, **无抽样** |
| ★关 (移出 `needs_from` ⇒ `needs_closed`)★ | **74** | 每条带 `action` / `reason` / `evidence` / `evidence_level` / `closed_at` / `closed_by` |
| ★留 (仍在 `needs_from` ⇒ `needs_open_ledger`)★ | **70** | 每条带 `owner` / `oneline` (一句话问法) / `why` / `evidence` / `evidence_level` / `board` |
| ★新答 (写进 `answers`)★ | **9** | 8 条外部依赖自查结案 + 1 条器材挂账改判; `to` 一律写「被问的那个 agent」 |
| ★对账★ | **70 + 74 = 144** | = 144 ✔ 平 |
### §1.1 · 四类逐条分布

| 桶 (★按**改分片前**的 `(to, waiting_on)` 原始归属★) | 任务书对应类 | 定义 | 原数 | 关 | 留 | 新答 |
|---|---|---|---|---|---|---|
| **①** | ① 内部等另一个总工 | `to=hw-lead` 17 + `to=mech-lead` 2 + `to=main` 且 `waiting_on=agent` 4 | **23** | 8 | 15 | 0 |
| **②** | ② `waiting_on = boss` | 不代拍 ⇒ 整理成 need key + 决策码一页 | **12** | 4 | 8 | 0 |
| **③** | ③ 外部依赖 | ★按老板政策自查 + 标证据等级 + 写降级方案★ | **8** | 8 | 0 | 8 |
| **④** | ④ `waiting_on` 空 | `to=main` 且 `waiting_on` 空 ⇒ 三选一 (a) 已作废 / (b) 已被覆盖 / (c) 真·待答 | **99** | 52 | 47 | 1 |
| **⑤** | (任务书未单列) | `to=main` 且 `waiting_on=sw-lead` ⇒ ★等的是我自己 ⇒ 我自己答★ | **2** | 2 | 0 | 0 |
| **合计** | | | **144** | **74** | **70** | **9** |
★**与任务书 §2 的口径对照 (两边都对, 只是归类边不同)★**: 任务书把「① 内部等另一个总工」写成 **23 条** (`to=hw-lead` 17 + `to=mech-lead` 2 + `to=main`&`agent` 4), 把「④ `waiting_on` 空」写成 **118 条** (= `to=main` 空 99 + `to=hw-lead` 17 + `to=mech-lead` 2) ⇒ ★**那 17 + 2 在任务书里两边都算 (有意重叠 19 条)**★。
★**本单按【不重复计数】的口径拆桶**: ★**① = 23**★ / ★**④ = 99**★ ⇒ **① + ④ = 122 = 任务书的 ① 23 + ④ 118 − 19 重叠** ⇒ ★**去重后 23 + 99 + 12 + 8 + 2 = 144** ✔
★**⇒ 因此: 任务书「④ 类 118 条」= 本单 §5 的 99 条 + §2.2 里的 19 条 (`to=hw-lead` / `to=mech-lead` 那两桶的留档)★ ⇒ ★**两处都列全了, 一条没漏**★。

### §1.2 · `action` 分布 (关的 74 条)

| action | 条数 | 含义 |
|---|---|---|
| `close` | 63 | 已结 / 已作废 / 已被后续交付覆盖 ⇒ 移出 `needs_from`, 留档在 `needs_closed` |
| `close+answer` | 11 | 同上, 且★**本单把答复写进了自己的 `answers`** (key + to + value + ref) |
### §1.3 · `waiting_on` 字段订正 (6 条: 空/`agent` → `boss`)

★**依据**: 这 6 条的正文自己写着「等老板, 项目总工转达」⇒ 原注册漏了 `waiting_on` 字段 ⇒ 本单**只订正字段, 条目一条不删**。

| need key | 原 `waiting_on` | 新 `waiting_on` | 依据 (条目原文) |
|---|---|---|---|
| `iss191_boss_pick_fix_option` | 空 / agent | `boss` | ★正文原文: 「★ISS-191 拍板 1 (等老板, 项目总工转达; 我不外发)★ ⇒ 复位 P0 走哪条」⇒ 等的是老板, 不是内部总工 ⇒ waiting_on 订正为 boss (★条目保留, 不删★)。 |
| `iss191_boss_q_envc_unify` | 空 / agent | `boss` | ★正文原文: 「★ISS-191 拍板 2 (等老板, 项目总工转达)★ ⇒ Q_ENVC 三行是否同批统一为 DNP」⇒ 等的是老板 ⇒ waiting_on 订正为 boss。 |
| `iss191_boss_r_pg_pull_dnp` | 空 / agent | `boss` | ★正文原文: 「★ISS-191 拍板 3 (等老板, 项目总工转达)★ ⇒ R_PG_PULL 两行是否也改 DNP」⇒ 等的是老板 ⇒ waiting_on 订正为 boss。 |
| `iss234_boss_pick_5q` | 空 / agent | `boss` | ★正文原文: 「ISS-234 给老板的 5 条待拍 (Q1 demo 板要不要关机态 / Q2 负载开关选型 ISS-172 / Q3 关机电流账 108µA 口径 / Q4 demo 关机时充电灯 / Q5 长按10s话术) — 每条带推荐默认值但不代拍, 等老板拍」⇒ 等的是老板 ⇒ waiting_on 订正为 boss。 |
| `iss250_n3_threshold_recheck` | 空 / agent | `boss` | ★正文原文: 「请 main 决定: ① 现在就把 N3/60 ms 降级为观察项 ② 还是等板端实测后按实测重定线 (sw-lead 只列, 不拍, ★这是老板级★)」⇒ 老板级 ⇒ waiting_on 订正为 boss。 |
| `iss250_pick_downgrade_route` | 空 / agent | `boss` | ★正文原文: 「路线①/③ 涉 60ms 生死与换芯片 = 商务决策 ⇒ 老板拍」⇒ 商务决策 = 老板级 ⇒ waiting_on 订正为 boss (★技术上路线②已由 ISS-263/ISS-355 事实选定, 只等老板追认签字★)。 |
★**另一条 `to` 改派**: `iss291_sw_vbus_det_d_digital_caliber` ⇒ `to` 由 `main` 改为 `hw-lead` ⇒ 依据 = SW 侧口径已随 ISS-291/ISS-293 落闸闭合, 剩下三个未决 (①USB_DRD1_VBUSDET 有无内部 40kΩ 下拉 ②IO 域/abs-max ③识别裕量 75mV) 是硬件侧 ⇒ **该谁答归谁**。

---

## §2 · ① 类逐条 (内部活 ⇒ 自己推)

★**口径**: 内部活 ⇒ 必须自己推 ⇒ 逐条判【我能答吗】⇒ ★**能答的直接写进自己的 `answers` (带 key + 出处 + 证据等级)**★ / ★**不能答的写清【该谁答 + 为什么 + 一句话问法】**★。

### §2.1 · 我自己能答的 (已写进 `answers`)

| need key | 动作 | 答复要点 | 出处 | 证据等级 |
|---|---|---|---|---|
| `demo_od_p0_1_rk3572_target` | close (早于本单已答) | rknn-toolkit2 2.3.2 的 target_platform **不含** rk3572 (合法值 11 个, 无 rk3572) ⇒ M1 零转换优势归零; ★但主路线已换★ rknn3-toolkit 1.2.0 **含** rk3572 (config rc=0 / 产物 md5 `97a34fff0b855b92681f26627dba5354` 三次一致) | sw.yaml 既有 `answers[demo_od_p0_1_rk3572_target]` (2026-11-11 sw-lead ISS-196 §1/§4) + `SW/RKNN_BENCH.md:378/382` | [实测]/[官网] |
| `demo_od_p0_3_build_env` | close (早于本单已答) | 构建环境已恢复 ⇒ 原 need 的前提被推翻 ⇒ 「构建环境已恢复 ⇒ 本 need 退休, 不要继续当活账挂着」 | sw.yaml 既有 `answers[demo_od_p0_3_build_env]` (2026-11-11 sw-lead ISS-196 §2) + 本单实跑 `IMPORT_OK` | [实测] |
| `fw_s2_test_gear` | close+answer | ★三样器材里 2 样各有零采购等价物, 只剩逻辑分析仪 1 样且只覆盖 P1 亚毫秒 1 格★ ⇒ 「没有它们 P1/P3 只能等原厂」这个挂账形态撤掉 ⇒ 改判为【板到手即跑的命令清单已备好】 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-1/E-2 + §4 + `SW/tools/boot_rescue_probe.py` 真跑枚举出 8 个设备真实 VID:PID | [实测]/[推算] |
| `model_toolchain_q9_addendum` | close | 【已退休】Art.Galaxy 线 (10 问全围绕它) ⇒ 公开渠道全查无 [0数据] + 主控基线已翻 RK3572 ⇒ 即便原厂给了也不该用 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-4 (ISS-270 verified) | [0数据]/[实测]/[官网] |
| `ars45_art_galaxy_sdk` | close | 【已退休】同上 ⇒ 替代已实测可用 (rknn3-toolkit 1.2.0 IMPORT_OK) | 同上 + `airockchip/rknn3-toolkit` README | [0数据]/[实测]/[官网] |
| `model_yolox_weight_download` | close | 【技术前提已消失】zoo CDN 实测可下 (35,891,401 B / 8.62 MB/s / 4 s) ⇒ 不需要任何人代下 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-3 ⑤ | [实测] |
### §2.2 · 我答不了 / 该谁答的 (留档 + 一句话问法)

| need key | 归属 | 一句话问法 | 为什么不是我答 | 依据 | 级别 | 板那一趟 |
|---|---|---|---|---|---|---|
| `iss190_netlist_reset_n_held_low` | hw-lead (落表批次) | ★P0 未闭合: 按现网表装板 RESET_N 会被永久拉低 (Q_AND 栅=PG_AND, 而 PG_AND 只剩 R_PG_PULL 10k 上拉 ⇒ 栅恒高 ⇒ 漏导通 ⇒ RESET_N 恒低) ⇒ 请按 ISS-191 选项② 把 Q_AND 整颗改 DNP (表A L65/L66/L67 + 表B Q_AND.1/.2/.3), 落表单号回我以便走 H-1 重锚 md5。 | sw-lead 已出方案页 + 机械判据 (timing_check.py --only F1_reset_rc ⇒ q_and_in_netlist False / pullup 读数), 但落表是 hw-lead 地界, sw-lead 不越界改网表 ⇒ 这条是内部活不是外部依赖。 | [实测] HW/netlist_v1.csv L62/63 (R_PG_PULL 必装) + L65/66/67 (Q_AND 必装) + L79/86 (两路 PG 源 dnp=DNP) · [官方] HW/PCB/RESET_P0_FIX_PLAN.md B1/B5 + state/issue_log.yaml ISS-191 (fix_ref: 落表本体 = 等老板拍②后随 RECHAIN_ONEPASS_PLAN §2 步1 一起做) | [实测]/[官方] | Y |
| `iss190_netlist_supv_divider_0R_short` | hw-lead (落表批次) | ★装配级风险未闭合: U_SUPV 三行全 DNP (SoM 内部 PMIC 已做上电复位 ⇒ 主板不装监督器), 但 R_SUPV_DIV1/DIV2 两颗 0Ω 仍标必装 ⇒ 按 BOM 装 0Ω = V_SOC_IO→DIV1→DIV2→GND 短路 (进限流 ⇒ IO 域塌陷 ⇒ 整机不启动 + 器件发热) ⇒ 请把这两颗随 U_SUPV 一起改 dnp=DNP (零成本)。 | 纯网表装配规则问题, hw-lead 地界; sw-lead 只报不改。 | [实测] HW/netlist_v1.csv L404/L405 (R_SUPV_DIV1/DIV2 必装) + L407/L408/L409 (U_SUPV 三行 dnp=DNP) · [官方] state/issue_log.yaml ISS-190 (verified) | [实测]/[官方] | Y |
| `iss190_netlist_q_envc_dnp_mismatch` | hw-lead (落表批次) | ★同一位号两行必装一行 DNP 未修: L71 (Q_ENVC→PG_AND) dnp=DNP 而 L72 (→GND) / L73 (→EN_VCORE) dnp=必装 ⇒ 装配表按「必装」会装上但栅极行不装 ⇒ 装配出来的板与网表意图不一致; 若两颗都不装 ⇒ EN_VCORE 只剩 10k 上拉恒高 ⇒ V1.8 想要的顺序链 (VIO 先起→PG 有效→再使能 VCORE) 被打掉 ⇒ 请三行统一 (全必装 + 补顺序链, 或全 DNP 并在 note 写清「顺序链在 SoM 内部完成」)。 | 这是 ISS-191 拍板 2 的落表本体 (等老板拍 ⇒ 已改判 waiting_on=boss)。 | [实测] HW/netlist_v1.csv L71 (DNP) / L72 / L73 (必装) · [官方] HW/PCB/RESET_P0_FIX_PLAN.md B2 落表清单 | [实测]/[官方] | Y |
| `iss190_netlist_usb_dminus_no_esd` | hw-lead (选型 + 板那一趟) | ★D− 侧 ESD 仍缺: D_ESD_USB_D = TPD1E05U06DPYR 单通道, net 是 NET_USB_D_P_TYPEC↔GND ⇒ 只护 D+ 与地; D_ESD_DEMO 护的是 RAIL_DEMO_5V 与地 ⇒ J_USB_C 的 D− 全网表无 ESD 器件 ⇒ 而 Type-C 是现网表上唯一的刷写口 ⇒ 一次 ESD 打到 D− 就只能拆机 JTAG ⇒ 请换成跨 D+ 与 D− 的双向件 (如 PESD5V0S1BA, 代价 Cd 35pF vs 0.42pF) 或并一颗, 并在 note 写明通道归属。 | 选型轴同时是老板 G1a 的 W-2 那一格 (D− 侧补不补 ESD) ⇒ 与板那一趟同批。 | [实测] HW/netlist_v1.csv L417 (D_ESD_USB_D → NET_USB_D_P_TYPEC) / L418 (→GND) / L420/L421 (D_ESD_DEMO → RAIL_DEMO_5V 与地) · [官方] state/issue_log.yaml ISS-190 / ISS-307 (verified) | [实测]/[官方] | Y |
| `iss234_battery_chain_dnp` | hw-lead (落表批次) | ★整机电池链仍是 DNP: BT_432243 / U_BATPROT / Q1 / Q2 全 DNP ⇒ U_PWR_SW 的 VIN(BAT_SW) 在 demo 装机态无源 ⇒ 整机真断电通路不成立 ⇒ 请给落装时点 + 落表单号, 我这边按 H-1 重锚 md5。 | 落表是 hw-lead 地界; 但关机语义 (真断电) 是 §0 锁死项, 这条不闭合则「关机」在装机态只有口号。 | [实测] HW/netlist_v1.csv (整机电池链 BT_432243 / U_BATPROT / Q1 / Q2 dnp=DNP) · [官方] PROJECT_TRACKER.md §0 L80 (关机语义 = 真断电, 锁死) | [实测]/[官方] | Y |
| `iss241_f1_f2_land_redraw_needed` | hw-lead (板那一趟 · 改 land) | ★板那一趟一起修 3 处 pad 序缺陷: ①D_ESD_CAM 板文件 pad1=GND/pad2=CSI_D0_CK_P 而器件 TPD1E05U06DPYR pin1=I/O/pin2=GND ⇒ 器件脚接错 ESD 不工作 (改法: 重画 land 对调 pad1/pad2, 或换双向件 PESD5V0S1BA 代价 Cd 35pF, 或改板) ②Q_AND 占位 pad 序 D/S/G 而 AO3400A 引脚序 G/S/D ⇒ RESET_N 落 G 脚 ⇒ 硬件 AND 变 OR (重画 land 时必须显式 RESET_N→D / GND→S / PG_AND→G) ③5 件按键 gullwing land 外扩 4.6×3.2mm > 占位 bbox 3.0×3.0 ⇒ 建议 5 个键 land 一次画齐。 | ★只报依据与代价, 本单不落表不改板★; 机检只读: HW/check_part_selection_landed_crosscheck.py --strict (rc=1 即含缺陷)。 | [实测] HW/PCB/demo_mainboard.kicad_pcb (D_ESD_CAM / Q_AND 占位 pad 序) + HW/netlist_v1.csv (器件引脚序 TPD1E05U06DPYR / AO3400A) · [官方] state/issue_log.yaml ISS-241 (verified) | [实测]/[官方] | Y |
| `s2_boot_entry_hw_rk3576` | hw-lead (载板下载态入口) | ★随基线翻到 RK3572 后需重核两问: ①SARADC_VIN0_BOOT 的电压档位门限谁定 (模组厂 parameter.txt / RK3576 同族官方 boot 电阻表; 零外发 ⇒ 自己查) ②专用 MaskROM USB 口在载板上引不引、走哪个 SoM 引脚 —— ★现网表已有 J_USB_C → SoM USB2 OTG1 那条 (L292/L432) ⇒ 请确认「MaskROM 口 = 已有的这条 OTG」还是需要再引一个专用口 (跨铰链救援通道那侧能否进 Maskrom)。 | ★问询清单 (外发形态) 已作废 ⇒ 这条只能走 hw-lead 自己查 SoM 脚表 + 公开 boot 电阻表 ⇒ 属内部活, 不是外部依赖。 | [实测] HW/netlist_v1.csv L292/L432 (SoM USB2 OTG1 → J_USB_C) · [官网] Flipper One docs (RK3576 上电读 SARADC_VIN0_BOOT 电压定启动优先级 + 专用 MaskROM USB 口) + rock-chips.com RK3576 Brief Datasheet | [实测]/[官网] | Y |
★**已答但保留在 `needs_from` 的 ① 类** (由对方登记的答复闭合 ⇒ merge 标 `answered` ⇒ ★**删掉反而丢记录**★):

| need key | 答复方 | 出处 |
|---|---|---|
| `debug_port_form` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/hw.yaml answers[debug_port_form] (to=sw-lead) + SW/SW_REQUIREMENTS.md §11.2 |
| `ntc_placement` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/mech.yaml answers[ntc_placement] (to=sw-lead) + SW/SW_TIMING_REVIEW.md §14 |
| `fw_boot_storage_bom` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/hw.yaml answers[fw_boot_storage_bom] + state/issue_log.yaml ISS-346 / ISS-350 (verified) |
| `fw_boot_mode_hw` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/hw.yaml answers[fw_boot_mode_hw] |
| `sw_reset_hw_changes` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/hw.yaml answers[sw_reset_hw_changes] |
| `sw_temp_mount_point` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/mech.yaml answers[sw_temp_mount_point] |
| `sw_poweroff_gpio_pin` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/hw.yaml answers[sw_poweroff_gpio_pin] |
| `iss137_dsi_payload_caliber` | 见 `answers` 里同 key 的登记 | [官方] state/fragments/hw.yaml answers[iss137_dsi_payload_caliber] + state/issue_log.yaml ISS-186 / ISS-188 (verified) |
---

## §3 · ② 类逐条 (不代拍 ⇒ need key + 决策码)

★**本单没有在分片里写任何 `decision` 字段, 没有替老板拍任何一条** ⇒ 下面每个决策码**只交「选项 + 代价 + 建议默认值 (只作参考) + 不拍的后果」**, 老板回一个码即可, 不用重读 144 条。

### §3.1 · 决策码表

| 决策码 | need key (★回码请带 key, 不要回裸字母★) | 选项 | 代价 | ★建议默认值 (只作参考·不代拍)★ | 不拍的后果 |
|---|---|---|---|---|---|
| **S-B01** | `fw_q3_scope` | ① 维持「只允许 ADB push」 ② 必须无线 | ① 无 OTA 前提, 回滚按 L1 手工 + S1 watchdog ② 本方案「无 OTA」前提失效, 回滚策略要重做 | **①** (与锁死 #11 不冲突, Type-C 已有) | 模型更新链路一直悬着, S2 救砖方案无法定稿 |
| **S-B02** | `fw_sample_ota` | ① 允许「USB 侧 OTA 代理」(PC 跑 agent 经 ADB 下发脚本) ② 不允许 | ① L1 回滚可半自动 ② 维持纯手工 (低优先, 不卡主线) | **①** (这不是无线, 不违反锁死 #11) | 样机段每次升级都要人肉 ⇒ 拖慢调试档期 |
| **S-B03** | `model_license_agpl_ultralytics` | ① 采购 Ultralytics Enterprise License ② 换 Apache-2.0 栈 | ① 官方无公开价 [0数据]·报价制; 立项预算量级 10^4-10^5 USD [推算]; 一次性授权 US$5k-50k + 年费 US$2k-20k/型号; 周期 4-12 周 [推算]; ★老板已定「不再发信」⇒ 采购只能走既有采购流程, SW 侧不询价★ ② 精度换档 (输入 640→320 或换模型), 商用不受阻 | **②** (技术门槛已清零: 许可 [官网] + 权重 [实测] 可下载 + 官方 NPU 配方 [官网]) | ★**不采购 = 商用受阻** (AGPL §6 要求随硬件分发即提供完整对应源码, 与闭源固件冲突) ⇒ 交付集卡在「许可干净候选为空」 |
| **S-B04** | `model_license_stack_decision` | ① Apache-2.0 栈 (首选 YOLOX-s) ② Ultralytics + 采购 ③ 等原厂「许可由原厂承担」的预编译模型 | ① 需用 rknn3-toolkit 1.2.0 + 官方 zoo 配方转 rk3572 `.rknn` (本机已可做) ② 见 S-B03 ③ ★**已退休·不再是路径***: 三条独立理由 (芯片基线已翻 RK3572 / A733 官方 `.nb` 实测类别映射错 ⇒ 官方资产也不省事 / 老板已定「不再发信」⇒ 这一路的**形式**本身被取消) | **①** | 转换链第 3 段没有承载体, 商用清单出不来 |
| **S-B05** | `s2_product_codename` + `s2_version_block_magic_decision` | ① 保持 ARS45 / magic 保持 `RK35` ② 改名 (请给新代号) + 另给 magic | ① 零改动 ② **只改配置一个字段 + 板端 `/etc/version` 生成模板, 代码零改动**; magic 宽度仍 4 字节 ⇒ §3.2 版本块二进制布局零改动; ★本项目尚无板、无已刷镜像 ⇒ 兼容成本 = 0★ | **①** | 版本串前缀与产品真源脱节; 老板 11-02 定的「目标 = 绘制 PCB 图」之后每块板都要带版本号 |
| **S-B06** | `demo_od_model_route_m1_vs_m2` | ① M1 (直接用 A7S 的 yolov5s@640 INT8, 零转换) ② M2 (yolov5n@640, 新拿 ONNX + 重转 + 精度重评) | ① RK3572 推算模式 A 62.67~64.18ms 超 60ms (但★demo 验收判据里没有 60ms 这一条, 60ms 是整机阶段硬指标★) ② 推算模式 A 52.91ms ✅ 但模式 B age=2 仍 ❌ ⇒ 需新拿 ONNX + 重转 + 精度重评 | **①** + 写死三个换模型触发条件 | demo 段卡在「用哪个模型」上, 出不了画面 |
| **S-B07** | `demo_od_path_a_vs_b` | ① 路径 A (AR0234CS 单线) ② 路径 B (先用现成 BSP 驱动 + 现成 IQ 的 IMX415/OV02B10 跑通链路, 再换 AR0234CS) | ① 驱动移植 5~8 人天 + ISP tuning 自写 5~10 人天 (rkaiq 公开 iqfiles 无 ar0234) ② 省 10~14 人天 ≈ 2~3 周; ★sw-lead 判断: 软件 75% 与 sensor 无关但 sensor 承担 ~70% 阻塞风险★ ⇒ **建议 B + AR0234CS 驱动/tuning 三线并行 (不是二选一)** | **②** | 驱动与 tuning 串行 ⇒ demo 段 1~2 人日滑成整机段 1~2 人周 |
| **S-B08** | `iss191_boss_pick_fix_option` + `iss191_boss_q_envc_unify` + `iss191_boss_r_pg_pull_dnp` | ① Q_AND 整颗改 DNP (sw-lead 推荐) ② Q_ENVC 摘掉或必装 ③ 等 SoM 球位 TBD-01 | ① **不改板、不加 IC、不等原厂**; 已在 RC1 反向用例实测否掉 ② (切不断故障链, 且 Q_ENVC 必装会把 EN_VCORE 拉低换成另一个 P0) ③ 首台板等不起 | **①** (三条同批落表) | ★**按现网表装板, RESET_N 会被永久拉低 ⇒ 首台板起不来** (Q_AND 栅=PG_AND 而 PG 只剩 10k 上拉 ⇒ 栅恒高 ⇒ 漏导通); ISS-191 的落表本体正卡在这里 ⇒ **板只改一次 ⇒ 这一拍不落, 复位 P0 就一直挂着** ★ |
| **S-B09** | `iss234_boss_pick_5q` (5 小问) | Q1 demo 板要不要关机态 / Q2 负载开关选型 ISS-172 / Q3 关机电流账 108µA 口径 / Q4 demo 关机时充电灯 / Q5 长按10s话术 | 每条带推荐默认值但不代拍 ⇒ 见交卷页 §3 决策码表 | 见交卷页 | 关机/待机口径有 3 条已锁死 (§0 L80/L84/L86), 剩下 2 条悬着 ⇒ 售后话术写不实 |
| **S-B10** | `iss250_pick_downgrade_route` | ① rk3576-target 维持现状 ② rknn3-toolkit 1.2.0 独立 conda env ③ 降 OD 负载 / 回 RK3576 换 SoC | ★**技术上路线②已被事实选定*** (ISS-263 实测 config('rk3572') rc=0 / 产物 md5 `97a34fff…` 三次一致 / ISS-355 脚本已迁主路线) ⇒ ★现在只等老板追认签字★; 路线①/③ 涉 60ms 生死与换芯片 = 商务决策; 三条共用同一套 N1~N5 判据 ⇒ 换路线不换判据 | **②** (追认签字) | 路线事实上已定但账面没签 ⇒ 下轮又有人重新讨论一遍 |
| **S-S10** | `iss250_n3_threshold_recheck` | ① 现在就把 N3 / 60ms 降级为观察项 ② 等板端实测后按实测重定线 | ① N3 通过线 t_npu ≤ 13.30ms 的基数是「RK3572 ≈ RK3576 的纯 NPU 13.305ms」[推算], 而 RK3576 官方 6 TOPS [官网] vs RK3572 4 TOPS [媒体] ⇒ 算力差 −33% ⇒ 同产物在 RK3572 上纯 NPU 耗时可能 ×1.5 ⇒ 52.91ms 那条模式 A e2e 也要打折; ② 板端取数口径: **纯 NPU 耗时须 C API `RKNN_QUERY_PERF_DETAIL` 取, 拿不到就判 INDET, 不许拿 SDK 总耗时顶 (N4 铁律)** | **②** (等板端实测) | 一条按既定门槛写死的判据, 实际基数已经偏了 ⇒ 板端一测就红 ⇒ 现场第一反应会去改判据 |
### §3.2 · ② 类已结 (老板早已拍完, 不再重复上报)

| need key | 老板原话 (代录出处) | 落点 |
|---|---|---|
| `q1_latency_scope` | 「选口径 A (曝光开始→出光, 最严口径)。不接受用改口径的方式达标。」 (2026-10-25 19:16) | 落到确定状态 |
| `q17_display_fps` | 「60fps 优先。班子到位之后 60 搞不定转 30。」 (2026-10-25 19:16, 19:26 经软件总工核算修正) | 落到确定状态 |
| `q18_highspeed_cam` | 「光机延迟不外部测设备, 改用目测/感官验收 (看有没有眩晕) → 新实测项 M-DIZZY (主观)。」 (2026-10-25 19:23) | 落到确定状态 |
| `demo_od_p0_4_panel_init_code` | 「不再做任何邮件 / 供应商 / 原厂问询」 (2026-11-11 19:31) + ISS-212 已结 (demo 半 = Waveshare 2.8" 官方 [官网]) | 落到确定状态; 整机屏路线仍属老板 ⇒ 已拆到 S-B05/S-B07, **不重复上报** |
---

## §4 · ③ 类逐条 (外部依赖 8 条 ⇒ 全部自查结案, 零外发)

★**老板政策 (2026-11-11 19:31 + 2026-11-12 02:02)**: 不再发信, 全靠自己查资料 ⇒ ★**这 8 条一律不许继续等回信 ⇒ 必须【自己网上查】+ 标证据等级 + 查不到就写降级方案**★ ⇒ ★**降级方案是必须项, 不是可选项**★ ⇒ ★**原措辞里「走 main 发第二轮邮件 / 经 main 转达 / 请并进第二轮邮件」这一类外发字样, 本单一并改掉**★。

| # | need key | ★自查结论★ | 自己查了什么 (可复现) | 证据等级 | ★降级方案 (必须项)★ | 原措辞里的外发字样 |
|---|---|---|---|---|---|---|
| ③-1 | `vendor_q8_q9_scope` | Q8 口径已由本域铁律写死 (纯 NPU 耗时须 C API `RKNN_QUERY_PERF_DETAIL` 取, 拿不到判 INDET, 不许拿 SDK 总耗时顶); Q9 追加 4 问全属 Art.Galaxy / 原厂 SDK 口径 ⇒ 随该线退休 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-3/E-4 (ISS-270 verified); 官方 `airockchip/rknn3-toolkit` README (Supported Platforms 含 RK3572) | [实测·本机文档]/[官网]/[0数据] | ① 权重/配方任一源不通 ⇒ 退化到本机已实测可用的 `ssd_mbv2_fpnlite_320_fp32_head_npu.onnx` (F1@IoU0.5 = 0.4346, 299 张) ② 双源 (fork + zoo CDN) ③ 换栈兜底 PP-YOLOE | ~~走 main 发第二轮邮件, 我不单独对外~~ ⇒ **作废** |
| ③-2 | `fw_vendor_toolchain` | ①下载工具 = 官方 RKDevTool (Win/Linux/macOS) + **开源 rkdeveloptool (GPL-2.0, 可脚本化批量)** ⇒ 「能否脚本化批量」= 是 ②bootloader = U-Boot TPL/SPL + miniloader (打包流程公开) ③无 fastboot ⇒ 等效切槽 = Rockusb Loader/MaskROM + U-Boot bootcount ④官方分区表 = Rockchip `parameter.txt` (rkbin 公开) ⑤烧录+回读文档 = rkdeveloptool README + SDK 文档 | `github.com/rockchip-linux/rkdeveloptool` README (db/wl/rd 逐字命令) · Radxa docs (RKDevTool 三平台) · u-boot `doc/README.rockchip` (miniloader / parameter.txt 打包) | [官网]/[媒体] | ① 工具链任一版不可得 ⇒ 用开源 rkdeveloptool 自编译 ② 分区表拿不到 ⇒ 按 §4.1 推荐 C 分区表 + 显式换算参数固化 (`SW/tools/s2_partition_convert.py --parse`) ③ 脚本化批量不受阻 | ~~经 main 转达, 我不单独对外~~ ⇒ **作废** |
| ③-3 | `fw_usb_boot_phy` | ①**有 USB PHY** (RK3576 官方 Brief Datasheet: USB3.1/Type-C/DP1.4 + USB2.0 OTG/HOST ×2) ⇒ 「若答无 USB PHY 则母座引脚定义要改」的返工风险**不成立** ②fastboot 不提供 ⇒ 等效 = Rockusb ③无 DFU/UF2 ⇒ 用 Rockusb ④★关键订正★: boot 选择脚不是 BOOT GPIO, 是 **SARADC_VIN0_BOOT 电压档位** | rock-chips.com RK3576 Brief Datasheet V1.2-20240311.pdf · Flipper One docs (RK3576 MaskROM 只走专用 MaskROM USB 口, 上电读 SARADC_VIN0_BOOT 电压定启动优先级) | [官网]/[媒体] | 烧录链路按「MaskROM(Rockusb) → Loader(Rockusb) → 正常启动」三态设计, 任一态可用即可救砖; 枚举特征板端 `lsusb -v` 实测回填 (零采购) | ~~经 main 转达~~ ⇒ **作废** |
| ③-4 | `fw_boot_entry_cond` | ①进入条件 = SARADC_VIN0_BOOT 电阻分压档位表 (官方 boot mode 表) + 按键/开关拉地强制 MaskROM ②校验 = Rockchip Secure Boot (HAB: 公钥 hash 存 OTP + RSA2048/SHA-256, 不通过即拒绝启动) ③A/B 自动回滚 = U-Boot bootcount/rollback 可配 ⇒ N=3 阈值可自配 ④secure boot 出厂默认关闭, 密钥管理走 RKTrust/OTP ⇒ 可选开启 | Rockchip Secure Boot Application Note V1.9 §1.4/1.5 · Flipper One docs (RK3576 boot mode 电压档位表) · u-boot bootcount 通用机制 | [官网]/[媒体]/[0数据·同族推断] | ★按「secure boot 关闭 + 板端 sha256 自检脚本」设计, **不依赖原厂** ⇒ 极性/档位未知都不改板 (网表 note: 极性反了只需改 Q_AND 接法) | ~~经 main 转达~~ ⇒ **作废** |
| ③-5 | `model_license_yolov5sim` | ★**ISS-087 本地早已判完, 这条本就不该挂 vendor**★ ⇒ yolov5s-sim 系 = ultralytics/yolov5 v6.0 release 导出物 ⇒ 许可 = **AGPL-3.0** (证据链 7 环) ⇒ 剩余「来源方书面确认」= 商业路径而非技术阻塞, 且**零外发政策已把它排除** ⇒ 唯一合规解 = 走 Apache-2.0 栈 | `SW/MODEL_LICENSE.md` §1.2 证据链 7 环 (第⑥环本机 ultralytics 8.4.80 METADATA `License: AGPL-3.0` + 随包 LICENSE 34,523 B; 第⑦环 `api.github.com/repos/ultralytics/yolov5` ⇒ `license.spdx_id = AGPL-3.0`); 一条命令 `python3 SW/tools/license_probe.py` 可复现 | [实测]/[官方] | ① 权重源不通 ⇒ 退化到本机已实测可用的 `ssd_mbv2_fpnlite_320_fp32_head_npu.onnx` ⇒ **商用不受阻** ② 双源 ③ 换 PP-YOLOE; ★两个重建件 (sha16 `1e2c716bd16ed9d3` / `dfb5d060ca36fc27`) 仍 licensing-hold 禁入 AGPL 交付集, 按换栈处置* | ~~经 main 转达, 我不单独对外~~ ⇒ **作废** |
| ③-6 | `sw_reset_timing_spec` | ①②③ (RESET 释放要求 / 内部上电顺序 / 是否提供 PG) **全在 SoM 内部** (主板不产 SoC 核心轨: 网表 L79 `U_DCDC_VCORE` / L86 `U_DCDC_VIO` 均 `dnp=DNP`) ⇒ 板级不可控 [0数据]; ★但已有兜底★ 网表 note「画法按最通用的『开漏 + 上拉』, 极性反了只需改 Q_AND 接法」⇒ 极性未知**不改板** ④片上温度 = 有 (SoC 内 tsadc + 板载 TMP117 I2C 0x48) ⑤BOOT 有效电平 = SARADC 档位 ⑥RESET/BOOT 电源域 = SoM 侧, 主板只挂焊盘位 | 网表 L79/L86 (dnp=DNP) + L75/L407/L408/L409 (U_SUPV DNP, note = Forlinx 官方载板复位电路 = 按键+100nF+ESD) · TI SNOSD82D TMP117 · `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-5 | [0数据·板级不可控]/[实测·网表]/[官方] | ① SoM 内部时序按「只有 SW_RST 能拉低」设计 ② PG 极性查不到 ⇒ 按开漏+上拉画, 极性反了改接法 ③ 温度改读板载 TMP117, 不等 SoC 内部 tsadc | ~~请项目总工并进第二轮邮件, 我不外发~~ ⇒ **作废** |
| ③-7 | `sw_usb_phy_spec` | ①USB 设备控制器 = USB2.0 OTG (FS 12Mbit/s) + USB3.1 Gen1 (SS 5Gbps) ⇒ ★工程口径★: 本项目**只按 FS 设计** (Type-C 只引 D+/D−/VBUS/GND; ADB + CDC-ACM 足够) ⇒ **原理图零返工** ②★原文结论要改★: 「SoC 侧无任何 VBUS 线 ⇒ 枚举前提缺失」**不成立** —— RK3572 有 `USB_DRD1_VBUSDET` 数字检测脚 (网表 L439 ⇒ `J_SOM_P1` pin100), 主板已按数字检测输入口径分压 (L434/435/436 1M+1M + L438 100nF) ⇒ 枚举前提 = VBUS_DET 数字脚 + VBUS 5V 供电子路 ③BOOT 态 VID:PID = Rockusb 2207 | rock-chips.com RK3576 Brief Datasheet V1.2 · 网表 L434/435/436/438/439 · `SW/SW_TIMING_REVIEW.md` §14 ADC 现值卡 | [官网]/[实测·网表]/[媒体] | ① 速率判不准 ⇒ 只按 FS 设计 (结论不变) ② VID:PID 板端实测 (零采购, 已有 `SW/tools/boot_rescue_probe.py`) ③ 识别裕量只剩 75mV ⇒ 按方案 A 换料 22k+1M (节点 3.18V) 或列 EVT 必测项 | ~~请项目总工并进第二轮邮件~~ ⇒ **作废** |
| ③-8 | `sw_aon_deepsleep_spec` | ①AON 域/常开唤醒脚: RK3576 官方 datasheet 有 Cortex-M0 MCU ×1 + TrustZone, 而 RK3572 是降本版, Forlinx 官方页未列独立 MCU ⇒ RK3572 具体脚号 [0数据] ⇒ ★降级★「关机态长按按键唤醒」**不写进必达路径**, 关机走 U_PWR_SW 真断电, 关机充电灯由充电板本地硬件承担 ②深睡态 DDR 是否保留: SW 侧**已按不可保留设计** (`SW_REQUIREMENTS.md` M7-R10: 进 standby 前落盘 + fsync) ⇒ 不阻塞实现 ③低功耗态 rail 能否真断: rail 全在 SoM 内部 PMIC ⇒ 主板无断电通路 | rock-chips.com RK3576 Brief Datasheet V1.2 (MCU ×1 / TrustZone) · forlinx.net FET3572-C 官方参数页 · `SW/SW_REQUIREMENTS.md` M7-R10 · `PROJECT_TRACKER.md` §0 L80/L84/L86 | [0数据·RK3572 AON 脚号]/[官网]/[实测·本机文档] | ① AON 永远查不到 ⇒ 用户话术**不承诺**「关机后按键唤醒」 ② DDR 不可保留 ⇒ 进 standby 前强制落盘 + fsync (已实现) ③ rail 不可断 ⇒ 「关机」定义为负载开关切 SYS 真断电, 不承诺 SoC 域断电 | ~~经项目总工并进第二轮邮件~~ ⇒ **作废** |
★**本类 8 条 ⇒ `needs_from` 里 `waiting_on=vendor` 的条数 = 0** ⇒ ★**「8 条外发依赖挂着」这笔老账清零**★。
★**本单零外发**: 不发邮件 / 不询价 / 不问询 / 不采购 / 不联系任何厂商; `state/outbox/` 里的草稿 (`s2_rk3576_module_vendor_query.md` 等) ★**一律不发, 只作资料留档**★ ⇒ **没有「批一句可以发」这个选项**。

---

## §5 · ④ 类逐条 (waiting_on 空 ⇒ 三选一)

### §5.1 · (a) 已作废 (5 条) —— 被哪个 ISS / 哪份文档改写, 必须引证

| need key | 依据 |
|---|---|
| `SW-N-ISS279-R6SELFTEST` | ④(a) 已作废 (重复条目): 本条与 ISS279_R6_SELFTEST_RED_20261117 是同一件事的两条登记 (同日期 11-17、同闸、同红项 R4/R5a) ⇒ 前一条已按「红已消 ⇒ rc=0 实测」结案 ⇒ 本条作废留档, 不再重复派。 |
| `s2_vendor_inquiry_draft` | ④(a) 已作废 (★外发形态作废★): 本条请项目总工把问询清单 v2.0 外发给 RK3576 模组厂 ⇒ 老板 2026-11-11 19:31 + 2026-11-12 02:02 已定「不再发信, 全靠自己查资料」⇒ ★外发这一形态本身被取消★ ⇒ 本条作废; 其技术内容 (Maskrom/Loader 条件 / 下载工具 / USB 下载通路与枚举特征 / 启动存储与分区表 + parameter.txt 单位方言) 已由本单 ③ 类 4 条 (fw_vendor_toolchain / fw_usb_boot_phy / fw_boot_entry_cond / sw_usb_phy_spec) 全部自查结案 ⇒ 留档见 SW/S2_VENDOR_QUESTION_LIST.md, 但不再作为待办挂在 needs_from。 |
| `iss353_need_main_apply_caliber_patch` | ④(a) 已作废 (★补丁已过期, 不许再跑★): 本条请 main 跑 logs/iss353/apply_caliber_dispositions.py --apply 清 15 条越权口径条目 ⇒ ★main 2026-11-23 05:4x 实跑 dry-run: 15 条里 13 条旧片段命中 0 次 ⇒ 那批文档已被 main 的一键补丁清过 ⇒ 再跑 --apply 只会徒增噪声 (旧片段命中 0 次)★ ⇒ 剩下 2 条在 state/fragments/hw.yaml L5226/L5227 ⇒ 属 hw-lead 分片 ⇒ 已由 main 转 hw-lead ⇒ 本条作废, 留档。 |
| `iss355_need_main_note_expired_caliber_patch` | ④(a) 已作废 (★已被 ISS-355 取代·保留作历史留档★): 本条本身已写明「补丁已过期·不再执行」+「已被 ISS-355 (转换脚本已迁 rk3572 主路线) 取代 ⇒ 保留作历史留档 ⇒ 结论不再引用」⇒ 落到确定状态 (留档, 不再引用)。 |
| `SW-MODEL-B2-ISS101-RU5` | ④(a) 已作废 (随 Art.Galaxy 线退休): 5 问里 M1 Art.Galaxy 工具链 / M2 ARS45 chip ID / M5 导出格式 / M6 量化方案 / M7 官方参考 ONNX + M4 head 裁图版三算子是否支持 —— 全是 Art.Galaxy / 酷芯微口径 ⇒ 主控基线 2026-11-02 已翻 RK3572 ⇒ 该线已退休 (ISS-270 §E-4); 剩下的 M3 (uint8 输入 + 板端是否挂 pre-process 节点) 与 M9 (Expand 算子) 属转换链通病 ⇒ 已由 rknn3-toolkit 1.2.0 + 官方 zoo 配方覆盖; M10 (320×320 对检出小目标的影响, 实测 person R=0.532) 已有实测结论 ⇒ 落到确定状态。 |
### §5.2 · (b) 已被后续交付覆盖 —— 指到具体 answers key / ISS

★**两部分**: ① **已关闭的** (从 `needs_from` 移出, 进 `needs_closed`) ② **已答但仍留在 `needs_from` 的** (由对方登记的答复闭合 ⇒ merge 标 `answered` ⇒ ★**删掉反而丢记录**★)★

| need key | 依据 (被谁覆盖) | 去向 |
|---|---|---|
| `iss137_r1_r6_fixback` | ④(b) 已被后续交付覆盖: ISS-137 rev0 退��的 6 条 (R1 判据 17.65→16.65 / R2 S9 一名两义 / R3 充分条件改必要条件 / R4 旧口径残留 / R5 板端实测闭合范围 / R6 版本头) 全部已落地 —— rev1 复验 5/5 命中、rev2 又抓第 6 处 F5、rev3 复验判 pass 并签掉 (旧断言整句 count=0 / 新断言整句 count=1 逐字节 / 四个数全在位 / note 里 compose_max_for 7 处全带 TX 语义, 真歧义行=0 / 4 个交付物 md5 与 rev2 逐字节相同 / 181 条逐字段比对只有 ISS-137.note 变了) ⇒ ISS-137 落 verified ⇒ 本条不再挂待办。 | `needs_closed` |
| `iss137_rev1_fixback` | ④(b) 已被后续交付覆盖: 本条 5 处订正全部落地并逐条命中 rev1 点名的原文 (R1 唯一阻塞真闭合), 且 rev3 已判 ISS-137 pass 落 verified ⇒ 原文照留 (历史留档), 本条不再挂待办。 | `needs_closed` |
| `iss137_rev2_f5_fixback` | ④(b) 已被后续交付覆盖: F5 已真闭合 (旧断言整句 count=0 / 新断言整句 count=1 / 四个数全在位且归属正确 / note 里 compose_max_for 7 处全带 TX 语义 / 真歧义行=0 / 4 个交付物 md5 与 rev2 逐字节相同 / 181 条逐字段比对只有 ISS-137.note 变了) ⇒ ISS-137 判 pass ⇒ 落 verified, 本条已签掉 ⇒ 不再挂待办。 | `needs_closed` |
| `iss188_dsi_payload_main_side_grep_dirty` | ④(b) 已被后续交付覆盖: 本条报 main 侧 3 处 (state/_demo_hw_scheme_landing.py:11 + config/agents/main/MEMORY.md:1979 + config/agents/main/memory/2026-11-02.md:26) ⇒ ★本单实测 3/3 均已清零★ ⇒ 落到确定状态。 | `needs_closed` |
| `iss285_sw_apply_after_iss283_verified` | ④(b) 已被后续交付覆盖 (★条目自带 resolved_by = ISS-288★): 前提已满足 (ISS-283 已 verified + ISS-285 补丁已落盘) ⇒ SW/tools/timing_check.py md5 = 68c4becffe6bcd708e388dba9d18a505 = ISS-285 交卷单写死的套用后期望值, 且 python3 SW/tools/timing_check.py ⇒ rc=0 · 72/72 ⇒ 本条 need 的「等 ISS-283 落 verified 后一次性套用」已被 ISS-288 履行完毕 ⇒ 落到确定状态 (机器层 close 由 main 签, 本单只登记)。 | `needs_closed` |
| `iss288_sw_timing_check_patch_landed` | ④(b) 已被后续交付覆盖: ISS-285 的补丁已落地真盘 (9 hunk · +157/-47) ⇒ timing_check.py 由 rc=1 · 68/71 转 rc=0 · 72/72, DPS --selftest 22/22, merge+gate rc=0 (Q1 18/18), 受保护 5 件 md5 逐字节不变 ⇒ 交卷通知已完成, 落到确定状态。 | `needs_closed` |
| `iss288_main_verify_sign_issue_log` | ④(b) 已被后续交付覆盖: 本条是「请 main 验签 + 把 iss285 那条标 closed」的请求 ⇒ ★main 已验签并落 verified★ (ISS-288 status=verified, verify_result=pass, verify_date=2026-11-17) ⇒ 请求已履行完毕, 落到确定状态 (本单不自签 issue_log, 只核对落账结果)。 | `needs_closed` |
| `iss291_sw_do_not_apply_vbus_100k47k` | ④(b) 已被后续交付覆盖 (★ISS-293 闭环注: 已随本单实质闭合★): 本条禁令「板只改一次那一趟不许把 VBUS_DET_D 改成 100k/47k」⇒ ISS-293 没碰 VBUS_DET_D 链任何器件值 (网表 37f62ac3…/脚表 a4270120…/BOM 5d02bece…/板 611b869e… 四个 md5 逐字节不变) ⇒ 且该禁令被新闸 SW/tools/check_timing_review_adc_sync.py 的 P1-DECISION 判据钉住 (谁再把 VBUS_DET_D 说成 ADC 判决对象 ⇒ 当场红) ⇒ 落到确定状态。 | `needs_closed` |
| `ISS279_R6_SELFTEST_RED_20261117` | ④(b) 已被后续交付覆盖: 本条报 check_demo_panel_spec_r6_selftest.py rc=1 (5/7 · R4/R5a/R5b 红), 并把 §4 那条 need 标为已闭环 ⇒ ★本单实跑该闸 rc=0★ ⇒ 红已消 (ISS-309 + ISS-312 + ISS-315 三轮反向用例收口) ⇒ 落到确定状态。 | `needs_closed` |
| `iss270_extdep_selfcheck_closeout` | ④(b) 已被后续交付覆盖: 本条是 ISS-270 的收口请求 (请 main 关闭/降级 4 条: ars45_art_galaxy_sdk / model_toolchain_q9_addendum / model_yolox_weight_download / reset_release_policy 的 PG 源 DNP) ⇒ ★ISS-270 已 verified★ 且其结论已被本单逐条落到确定状态 (前 3 条见本表, 第 4 条 = 待落表批次见 needs_open_ledger) ⇒ 收口完成, 落到确定状态。 | `needs_closed` |
| `iss270_s2_test_gear_zero_cost` | ④(b) 已被后续交付覆盖: 本条给 fw_s2_test_gear 的零采购结论 (USB 协议分析仪不必要 / SPI-NOR 空板不必要 / 逻辑分析仪只覆盖 P1 亚毫秒一格) ⇒ ISS-270 已 verified 且结论已落到 fw_s2_test_gear 的结案行 ⇒ 本条落到确定状态。 | `needs_closed` |
| `fw_s2_test_gear` | ④(b) 已被后续交付覆盖 + ①类自己答: 本条是外部依赖形态的器材挂账 (「没有它们, P1/P3 只能等原厂」) ⇒ ★ISS-270 已把挂账形态撤掉★: 三样器材里 2 样各有零采购等价物 (P3 VID:PID 用 lsusb + /sys/bus/usb/devices + dmesg, 协议层用 usbmon+tshark; P4 分区表用板端 /proc/mtd + JEDEC ID), 只剩逻辑分析仪 1 样且只覆盖 P1 亚毫秒 1 格 (而老板 2026-11-04 19:10 已把 test_equipment_budget 收窄成只剩它 1 项) ⇒ ⇒ 落到确定状态: 「板不可达」不是「等外部」, 本条改判为【板到手即跑的命令清单已备好】(SW/EXTERNAL_DEPENDENCY_SELFCHECK.md §4), 老板那一项仍在 test_equipment_budget 不由本单动。 | `needs_closed` |
| `s2_chip_swap_scope` | ④(b) 已被后续交付覆盖 (★条目自带 decision + decided_at + closed_ref★): 换芯口径三问已全部有答案 —— ①magic/前缀抽成可配置 (ISS-123 已改) ②分区表按 RK3576 模组厂 parameter.txt 重排, 单位差 512 倍做成显式参数 + 机械守卫 (ISS-123 已改) ③问询对象 = RK3576 模组厂 (问询清单整版重写 v2.0) ⇒ 落到确定状态。 | `needs_closed` |
| `iss215_verdict_direction_flip` | ④(b) 已被后续交付覆盖: 本条知会「60ms 判据链第 3 条判定方向翻了 (显示输出侧不再是瓶颈)」并请决定是否同步判据视图 ⇒ ★ISS-215 已 verified 且后续 ISS-221 交付了 demo 口径自己的真源脚本 (SW/tools/demo_e2e_budget.py) + 判据链换到它 (SW/DEMO_OD_TIMING_SPEC.md §3.3.1) ⇒ 判据视图已同步, 落到确定状态。 | `needs_closed` |
| `iss225_reanchor_sw_md5_after_iss223` | ④(b) 已被后续交付覆盖: 本条请在 ISS-223 落表后派 sw-lead 走 H-1 重锚流程 (改 SW/SW_MD5_BASELINE_LEDGER.md §1 entries[].md5 + prev_md5 + by) ⇒ ★该口径已被后续三单取代★: ISS-275 落表台账格式契约 (「单号 \| 文件名 \| 改前 md5 \| 改后 md5」四项同行) + ISS-284 硬保护段改按【落表台账链头】判决 ⇒ 合法落表自动前移, 不用再追锚点 ⇒ 本条落到确定状态 (锚点副本不再是判据源)。 | `needs_closed` |
| `iss226_land_verified_and_reanchor` | ④(b) 已被后续交付覆盖: 本条请落 verified + 确认 ISS-134 的 need 变 answered ⇒ ★ISS-226 已 verified★ (main 实跑 check_brightness_biosafety.py rc=0 + --selftest 13/13 + check_demo_panel_spec.py rc=0 + merge/gate rc=0 Q1 18/18) ⇒ 落到确定状态。 | `needs_closed` |
| `iss228_verify_l` | ④(b) 已被后续交付覆盖: 本条是 ISS-228 的交卷通知 + 两条勘误 + 一条请 main 落 verified + 一条请派 hw-lead 改两处提法 ⇒ ★ISS-228 已 verified★ ⇒ 落到确定状态 (残留 [0数据] 项 SoM 侧 VCCIO rail 网名按 ISS-270 口径 = 待落表/待 hw-lead 网表真源, 不随本条闭合, 已登记在 needs_open_ledger)。 | `needs_closed` |
| `iss221_redispatch_reverify_0730` | ④(b) 已被后续交付覆盖: 本条是 ISS-221 重复派活复验通知 (零重做 + 唯一红项归 ISS-235) ⇒ ★ISS-221 已 verified★ (main 独立复核后签字) ⇒ 落到确定状态 (ISS-235 那 3 条断言也已在 iss234_sw_stale_assertions 一起结案)。 | `needs_closed` |
| `iss245_reverse_demo_stale_agg` | ④(b) 已被后续交付覆盖: 本条报 --reverse-demo 演示聚合行 L1762 仍判 mut2[rail_switching_devices]==0 ⇒ ★ISS-248 已把该演示段口径对齐到权威判据 REV-3 (删掉 U_PWR_SW 后从 2 掉到 1) ⇒ --reverse-demo 恢复 rc=0 ⇒ 本条报的问题已被实际修掉, 落到确定状态。 | `needs_closed` |
| `iss248_verify_close_reverse_demo` | ④(b) 已被后续交付覆盖: 本条请 main ① 落 ISS-248 verified ② 顺带闭掉 iss245_reverse_demo_stale_agg ⇒ ★两项均已完成★ (ISS-248 verified; iss245 那条已在本表结案) ⇒ 落到确定状态 (本单不自签 issue_log, 只核对落账结果)。 | `needs_closed` |
| `iss250_e11_e12_pending_install_test` | ④(b) 已被后续交付覆盖: 本条要求「rknn3-toolkit 1.2.0 本机安装实测 + config(target_platform='rk3572') 实跑, 记 min/avg/max」⇒ ★ISS-263 已做完并落 verified★ (本机 conda env rknn3 已建, config('rk3572') rc=0, 产物 249,360 B md5 97a34fff0b855b92681f26627dba5354 三次一致, t_total 33.389/34.108/41.672 s) ⇒ 落到确定状态。 | `needs_closed` |
| `iss250_sync_compat_v2` | ④(b) 已被后续交付覆盖: 本条请 main 裁决是否把 ISS-250 新查的 5 条官方证据回写进 SW/RK3572_TARGET_COMPAT_V2.md ⇒ ★已回写★ (该文件现有 68 处 rk3572 命中, 含 target_platform='rk3572' / 产物 md5 / 板端接受性 [0数据] 三行) ⇒ 落到确定状态。 | `needs_closed` |
| `iss234_sw_stale_assertions` | ④(b) 已被后续交付覆盖: 本条点名的 3 条 SW 侧过期断言 (①timing_check 断言 U_EN_SW 无器件行 ②REV-3 期望装机开关数 1->0 ③check_demo_panel_spec REV-12 硬编码 ISS-220) ⇒ ★ISS-235 已逐条订正并落 verified★ (main 实跑: timing_check.py rc=0 SELFTEST 71/71 · check_demo_panel_spec.py rc=0 · --selftest 17/17 · check_shutdown_semantics.py rc=0 + selftest 17/17) ⇒ 落到确定状态。 | `needs_closed` |
| `iss139_tisp_timing_point` | ④(b) 已被后续交付覆盖: 本条建议增补 ISP 算法耗时打点 t_isp (不改现有 9 个打点名与 CSV 表头) ⇒ ★已落地★: SW/DEMO_OD_TIMING_SPEC.md 11 段接力表第 12 段已写「t_isp_hw (纯硬件耗时) + t_isp_total (SDK 总耗时 / 管线可见)」, 并明确 ISP 是异步流水、须用驱动/帧统计上报时间戳 ⇒ 落到确定状态。 | `needs_closed` |
| `iss279_sw_to_board_inputs` | ④(b) 已被后续交付覆盖: 本条 3 项 —— ①SW→板 输入清单 9 条转 hw-lead (ISS-277 同批做板侧清单) 已办; ②hard_protected 怎么合法跟上「板只改一次」= ★老板 2026-11-17 09:49 已拍 P10 = 方案② 并由 ISS-284 落地★ (台账 §1 ISS-284 段 + §3 R-12 + check_demo_panel_spec.py REV-16~REV-21); ③SW 侧对板只有 S2/S4/S8/S9/S10 五步有话说 (实测结论) 已写进 SW/BOARD_ONEPASS_SW_SYNC.md §3/§4 ⇒ 落到确定状态。 | `needs_closed` |
| `sw_legal_reboard_landing_row_on_board_trip` | ④(b) 已被后续交付覆盖 (★机制件已完成★): 本条要求「合法改板那一行必须落在落表台账里, 格式 = 单号 \| 文件名 \| 改前 md5 \| 改后 md5, 板与 .kicad_pro 两件必须成对」⇒ ★该机制已由 ISS-284 落地并挂链★ (check_demo_panel_spec.py 的 R6 硬保护段按落表台账链头判决 + 三道 R6 selftest 闸已挂进 state/gate_check.py EXTRA_GATES) ⇒ ★真落那一行归「出板那一趟」, 不是 need ⇒ 本条落到确定状态。 | `needs_closed` |
| `iss298_sw_gate_depends_on_cdps_api` | ④(b) 已被后续交付覆盖 (★本条是登记型 need, 登记动作已完成★): 本条登记「SW/tools/check_onepass_sw_sync.py 与 check_demo_panel_spec.py 之间的代码级依赖 (check_r6_hard_protected / load_sw_anchor / LEDGER_DOC / LEDGER_CANON 四个名字与签名不许改)」⇒ 登记已随 ISS-298 交卷完成 + 两道闸均已挂进 EXTRA_GATES ⇒ 落到确定状态 (耦合关系继续保留, 但不再作为待办挂在 needs_from)。 | `needs_closed` |
| `iss306_sw_g1a_reds_rootcause_done` | ④(b) 已被后续交付覆盖: 本条是 ISS-306 的交卷通知 (G1a 两条红逐条归类完毕 + 老板还差 4 个字母 + 「催拍必须回 need key 不能回裸字母」) ⇒ ★ISS-306 已 verified★ ⇒ 落到确定状态 (那 4 个字母属 pm.yaml 的 need, 不属本条; 本单在决策码页按 need key 重列)。 | `needs_closed` |
| `iss306_rerun_0535_main_actions` | ④(b) 已被后续交付覆盖: 本条是 ISS-306 追加复验交卷 (结论不变 + 请 main 记一条「/tmp 配额 ⇒ 环境红不是设计红」的机器侧口径) ⇒ ★ISS-306 已 verified★ ⇒ 落到确定状态 (该口径已随 ISS-309/ISS-315 落进 gate_check.py 的 EXTRA_GATES TMPDIR 指项目内 tmp/iss318_gates ⇒ 同一口径已生效)。 | `needs_closed` |
| `iss309_r6_selftest_hook_into_gate_chain` | ④(b) 已被后续交付覆盖: 本条请 main 把 check_demo_panel_spec_r6_selftest.py 挂进 state/gate_check.py EXTRA_GATES ⇒ ★已挂★ (本单实读 EXTRA_GATES 列表, 该闸在列, 失败语义与现有 run_external_gate 一致) ⇒ 落到确定状态。 | `needs_closed` |
| `iss312_need_hook_gates` | ④(b) 已被后续交付覆盖: 本条请 main 把 check_demo_panel_spec_r6_chainjudge_selftest.py 与 check_demo_panel_spec_r6_selftest.py 一起挂进 EXTRA_GATES ⇒ ★已挂★ (两闸均在本单实读的 EXTRA_GATES 列表里) ⇒ 落到确定状态。 | `needs_closed` |
| `iss315_gate_wiring` | ④(b) 已被后续交付覆盖: 本条建议把三条闸 (check_landing_trace_obligation.py + check_demo_panel_spec_r6_chainjudge_selftest.py + check_demo_panel_spec_r6_hardprot_iss315_selftest.py) 挂进 EXTRA_GATES ⇒ ★三条全部已挂★ ⇒ 落到确定状态。 | `needs_closed` |
| `iss318_sw_gates_hook_decision` | ④(b) 已被后续交付覆盖: 本条 (ISS-315 N-3 挂闸裁决) 请 main 决定把 ISS-318 新立的两道闸 + ISS-312/ISS-309 两道 selftest + 本单位号引用闸挂不挂 EXTRA_GATES ⇒ ★已挂★ (EXTRA_GATES 里有 check_sw_ref_reachability.py (ISS-318) + check_landing_trace_obligation.py (ISS-315) + 三道 R6 selftest) ⇒ 落到确定状态。 | `needs_closed` |
| `iss309_r6_head_ticket_judge_hole_fix` | ④(b) 已被后续交付覆盖: 本条报「链头落表单号只有非空一道检查 ⇒ 改坏判绿」并给三个修法 ⇒ ★main 已拍板「修法 A+B 都要」并由 ISS-312 落地★ (链头产出单号不唯一 ⇒ 判红 + 链头单号与独立信源 issue_log 对账 + 锚点副本跟到链头) ⇒ 落到确定状态。 | `needs_closed` |
| `iss309_sw_anchor_copy_lag_to_head` | ④(b) 已被后续交付覆盖: 本条请 main 拍「域侧锚点副本要不要每次落表都跟到台账链头」⇒ ★该口径已由 ISS-315 N-2 定为「链头产出单号」判决源口径并落进新闸 check_landing_trace_obligation.py★ ⇒ 落到确定状态 (锚点副本不再是判据源, 故「副本滞后」不再是待决项)。 | `needs_closed` |
| `iss312_need_landing_iss_trace_duty` | ④(b) 已被后续交付覆盖: 本条请给「板那一趟」定一条义务 —— 任何落表 (含合法改板) 的单号都必须在 state/issue_log.yaml 留下【文件名 + 新 md5】留痕 ⇒ ★该义务已生效并做成新闸★ (ISS-312 落表真源路径 + ISS-315 硬保护路径 + check_landing_trace_obligation.py 已挂链) ⇒ 落到确定状态。 | `needs_closed` |
| `iss312_need_hardprotected_crosscheck_B` | ④(b) 已被后续交付覆盖: 本条请把修法 B (独立信源 issue_log 对账) 也铺到硬保护路径 (check_r6_hard_protected ③) ⇒ ★已铺★ (ISS-315 把「修法 B = 链头落表单号 ↔ 独立信源对账」做到硬保护路径上, 并新建 check_demo_panel_spec_r6_hardprot_iss315_selftest.py 反向用例闸, 已挂 EXTRA_GATES) ⇒ 落到确定状态。 | `needs_closed` |
| `iss315_board_trip_trace_duty` | ④(b) 已被后续交付覆盖: 本条说「板那一趟的单号留痕义务现在已经生效」⇒ 已生效且已做成新闸 ⇒ 落到确定状态 (真落那一行归出板那一趟, 由 check_landing_trace_obligation.py 盯着)。 | `needs_closed` |
| `iss315_n2_scope` | ④(b) 已被后续交付覆盖: 本条请 main 拍板认/不认「落表单 = 落表台账链头产出单号」这个口径 ⇒ ★已认并落地★ (该口径成为 check_landing_trace_obligation.py 的判决源, 已挂 EXTRA_GATES) ⇒ 落到确定状态。 | `needs_closed` |
| `iss346_need_board_side_storage_input` | ④(b) 已被后续交付覆盖 (★条目自带【ISS-350 订正 · 本条已闭环】★): 板侧输入 (SPI-NOR ⇒ J_BOOT1 焊盘位已在板 ⇒ 板侧零动作不重出板 / eMMC ⇒ 153-ball TFBGA 11.5×13.0mm ⇒ 板宽 12→15mm ⇒ 产品板档须在板那一趟开工前进网表) 已由 ISS-350 落进同 key 的 needs_from (新措辞 = 4 条 SPI_*_BOOT + 「外挂 SPI-NOR ⇒ 板要重出不成立」+ 问原厂那一句改成问「SoM 侧是否引出这 4 条 SPI boot pin」) ⇒ 本条订正提示闭环, 落到确定状态。 | `needs_closed` |
| `iss353_need_hw_ledger_supersede` | ④(b) 已被后续交付覆盖: 本条请 main 转 hw-lead 在 hw.yaml 里补一条取代标记 (key=iss353_hw_ledger_supersede_rk3572_target, 内容 = RK3572 转换 target = rknn3-toolkit 1.2.0 + target_platform='rk3572') ⇒ ★已登记★ (本单实读 state/fragments/hw.yaml, 该 key 命中 1 处) ⇒ 落到确定状态。 | `needs_closed` |
| `iss353_need_followup_convert_script_rk3572` | ④(b) 已被后续交付覆盖: 本条要求给 SW/tools/rk3572_model_rebuild.sh (L13/L86/L136) 与 SW/RKNN_BENCH.md §5 加 rknn3 分支 ⇒ ★ISS-355 已做完并落 verified★ (脚本 v2.0: 默认路线已迁到 rknn3 + rk3572; rknn3 产物是 .rknn + 同名 .weight 两件套的坑也已在文档里写清) ⇒ 落到确定状态。 | `needs_closed` |
| `iss201_rebuild_model_license` | ④(b) 已被后续交付覆盖: 本条请项目总工在 (a) 向来源方/原厂取得重建件许可结论 与 (b) 改走 Apache-2.0 栈 之间二选一 ⇒ ★路 (a) 已被老板 2026-11-12 02:02「不再发信」政策排除 (不是我能选的) ⇒ 唯一合规解 = 路 (b)★, 而路 (b) 的技术门槛已清零 (ISS-270 §E-3: YOLOX-s Apache-2.0 许可 [官网] + 权重 [实测] 本机可下载 + 官方 NPU 配方 [官网]) ⇒ 重建件的 licensing-hold 状态按「换栈」解除 ⇒ 本条落到确定状态 (两个重建件 sha16 1e2c716bd16ed9d3 / dfb5d060ca36fc27 仍禁入 AGPL-3.0 交付集, 见 needs_open_ledger 的残留行)。 | `needs_closed` |
| `model_od_input_size` | ④(b) 已被后续交付覆盖: 本条请裁决 OD 输入尺寸 (决定 ONNX 静态 shape + 转换产物体积 + 端到端预算) ⇒ ★sw-lead 的默认假设 640x480 现已是全链现值★ (ISP 缩放链 全幅 → 640×480@60; OD 640×480 是 §0 锁死变量, 改动需老板另行拍) ⇒ 裁决结果 = 维持 640×480 ⇒ 本条落到确定状态 (若要改, 由 S-B 决策码另起, 不走本条)。 | `needs_closed` |
| `SW-MODEL-B2-ISS101-RU1` | ④(b) 已被 model_license_stack_decision / model_license_agpl_ultralytics 覆盖: 本条「采购 Ultralytics Enterprise License 还是走 Apache-2.0 栈?」与那两条是同一件事的重复登记 (ISS-101 R-U1) ⇒ ★不再单挂, 统一进决策码 S-B03/S-B04★ ⇒ 落到确定状态 (留档, 不再重复问老板)。 | `needs_closed` |
| `SW-MODEL-B2-ISS101-RU6` | ④(b) 已被后续交付覆盖: 本条写明「不回 = 默认做」⇒ 默认动作已发生; ★实际执行结果比提案更好★ —— 不是用本机 ACUITY (边界里已注明 ACUITY ≠ Art.Galaxy), 而是直接走 ★官方 rknn3-toolkit 1.2.0 + target_platform='rk3572'★ (ISS-263 实测 config rc=0 / 产物 md5 97a34fff… 三次一致), 并于 ISS-355 把脚本迁到主路线 ⇒ 第 3 段风险已从 [0数据] 降成「板端接受性待板」⇒ 落到确定状态。 | `needs_closed` |
| `iss255_ledger_registration_required` | ④(b) 已被后续交付覆盖: 本条要求「hw-lead 每落一次网表, 必须同时在 HW/SCHEMATIC_LANDING_V1_LANDED.md 的 md5 台账里补一行 (单号 \| 文件名 \| 旧 md5 \| 新 md5), 否则必红」⇒ ★该义务已升级为【判决源口径】并做成新闸★: ISS-275 定下格式契约 + ISS-284/ISS-315 把硬保护段与留痕义务都改按【落表台账链头】判决 (合法落表自动前移, 偷换照样红) + check_landing_trace_obligation.py 已挂 EXTRA_GATES ⇒ 落到确定状态。 | `needs_closed` |
| `sw_runtime_recalc` | [官方] state/fragments/pm.yaml answers[sw_runtime_recalc] (to=sw-lead) + SW/POWER_STATE_SEMANTICS.md §6.1 | 留 `needs_from` (merge 标 answered) |
| `iss215_rknn_bench_s9_note_sync` | [官方] state/fragments/pm.yaml answers[iss215_rknn_bench_s9_note_sync] + state/issue_log.yaml ISS-221 (verified) | 留 `needs_from` (merge 标 answered) |
| `iss215_demo_budget_script` | [官方] state/fragments/pm.yaml answers[iss215_demo_budget_script] + state/issue_log.yaml ISS-221 (verified) | 留 `needs_from` (merge 标 answered) |
| `iss221_verify_and_close_iss215_needs` | [官方] state/fragments/pm.yaml answers[iss221_verify_and_close_iss215_needs] + state/issue_log.yaml ISS-221 (verified) | 留 `needs_from` (merge 标 answered) |
| `iss275_sw_ledger_format_contract` | [官方] state/fragments/pm.yaml answers[iss275_sw_ledger_format_contract] + SW/SW_MD5_BASELINE_LEDGER.md | 留 `needs_from` (merge 标 answered) |
| `iss318_sw_ref_impact_gate` | [实测] state/gate_check.py EXTRA_GATES (check_sw_ref_reachability.py 在列) + state/fragments/pm.yaml answers[iss318_sw_ref_impact_gate] | 留 `needs_from` (merge 标 answered) |
| `iss318_sw_ref_baseline3_disposition` | [官方] state/fragments/pm.yaml answers[iss318_sw_ref_baseline3_disposition] + SW/tools/check_sw_ref_reachability.py | 留 `needs_from` (merge 标 answered) |
| `iss327_decide_registry_rebuild_trigger` | [官方] state/fragments/pm.yaml answers[iss327_decide_registry_rebuild_trigger] | 留 `needs_from` (merge 标 answered) |
| `iss327_decide_missing_baseline_mechanism` | [官方] state/fragments/pm.yaml answers[iss327_decide_missing_baseline_mechanism] | 留 `needs_from` (merge 标 answered) |
| `iss327_decide_drift_class_semantics` | [官方] state/fragments/pm.yaml answers[iss327_decide_drift_class_semantics] | 留 `needs_from` (merge 标 answered) |
| `iss327_report_c1_c7_c8_c13_launder_faces` | [官方] state/fragments/pm.yaml answers[iss327_report_c1_c7_c8_c13_launder_faces] | 留 `needs_from` (merge 标 answered) |
| `iss335_ref_gate_v1_or_v2` | [官方] state/fragments/pm.yaml answers[iss335_ref_gate_v1_or_v2] + HANDOFF/2026-11-19_sw-lead_ISS335_*.md §B5-1 | 留 `needs_from` (merge 标 answered) |
| `iss338_need_usbif_cc1_cc2_rule` | [官方] state/fragments/pm.yaml answers[iss338_need_usbif_cc1_cc2_rule] | 留 `needs_from` (merge 标 answered) |
| `iss338_need_boot_storage_answer` | [官方] state/fragments/pm.yaml answers[iss338_need_boot_storage_answer] + state/issue_log.yaml ISS-350 (verified) | 留 `needs_from` (merge 标 answered) |
| `iss338_need_jtag_group_decision` | [官方] state/fragments/pm.yaml answers[iss338_need_jtag_group_decision] | 留 `needs_from` (merge 标 answered) |
### §5.3 · (c) 真·待答 (32 条) —— 给 owner + 处理方式 + 是否与板那一趟相关

| need key | owner | 一句话问法 | 为什么不是我答 | 依据 | 级别 | 板那一趟 |
|---|---|---|---|---|---|---|
| `iss191_orig_som_pg_reset_spec` | main (落表批次) | ★已改判: 这不是外部依赖, 是【待落表批次】(按 ISS-270 §E-5 口径) ⇒ 网表真源 L79/L86 已写死 dnp=DNP (SoM 自带 PMIC) ⇒ 处置办法 = ISS-191 选项② (Q_AND 整颗改 DNP), 本单一次都没跑 land_v_values.py --apply ⇒ 请 main 排落表批次 (① PG 输出球位+极性 ② RESET 释放要求 ③ 内部复位电路构成 三项里, ②③ 属 SoM 内部, 落表不依赖它们)。 | 零外发 ⇒ 「外发原厂」这一形态已被老板政策取消; 本条改判成内部落表批次。 | [实测] HW/netlist_v1.csv row79/row86 (dnp=DNP, note = SoM 自带 PMIC) · [官方] SW/EXTERNAL_DEPENDENCY_SELFCHECK.md §1 E-5 (ISS-270, verified) | [实测]/[官方] | Y |
| `iss291_sw_vbus_det_d_digital_caliber` | hw-lead (三个硬件侧未决) | ★SW 侧口径已落闸 (ISS-291 F4D 段 + ISS-293 同步 SW/SW_TIMING_REVIEW.md §14 + 新闸 check_timing_review_adc_sync.py), 剩下的是三个硬件侧未决: ①USB_DRD1_VBUSDET (J_SOM_P1 pin100) 有没有内部 40kΩ 下拉 (Forlinx 手册只明写 DRD0) ②该脚 IO 域 / abs-max (脚表 vol 栏 = —— ⇒ 域未知) ③识别裕量 (当前 1M+1M ⇒ 节点 0.185V ≪ 2.3V 阈值; 换 22k+1M ⇒ 3.18V 落在 2.7-3.3V 高电平带内, 静态 82.6µA) ⇒ 请 hw-lead 给这三个数的板端实测或 SoM 脚表真值, 我出改料不换板方案 (A 换料 / B 按手册 4.7k 上拉 / C 不动 + EVT 必测)。 | ★SW 侧那条禁令 (不许套 100k/47k) 已随 ISS-293 闭合并被新闸钉住★; 硬件三问不随本条闭合 ⇒ 仍需 hw-lead。 | [实测] HW/netlist_v1.csv L434/435/436/438/439 (VBUS_DET 1M+1M+100nF) + HW/PCB/FET3572C_PIN_TABLE.csv (P1_100 vol 栏 = ——) · [实测·本机文档] SW/ADC_CALIBER_TABLE.md §1 行15~18 + SW/SW_TIMING_REVIEW.md §14 | [实测]/[0数据] | Y |
| `sw_charge_page_full` | main (ISS-093 · 充电板整页) | ★充电板整页仍未画 ⇒ 我对 CHG_STAT/PWR_GOOD 的评审只覆盖网表现状不是最终电路 ⇒ 请 main 补 BQ25896 的 STAT/PG 极性 (开漏拉低 = 充电中?) + CE/OTG/PSEL/INT 接法 + Type-C 完整页; ★这一页与关机充电灯 (锁死项 §0 L86) 直接相关 ⇒ 补完我才能把「关机时充电灯亮」的判据落到可测。 | ISS-093 (owner=main, verify_by=hw-lead) 至今 status=open ⇒ 不是 SW 侧能自己答的。 | [官方] state/issue_log.yaml ISS-093 (status=open) · [实测·网表] HW/netlist_v1.csv (CHG_BOARD 整页现状) + PROJECT_TRACKER.md §0 L86 | [官方]/[实测] | N |
| `sw_poweroff_semantics` | main (①③) + boss (③ SoC 位置) | ★三项里 ①已答: 关机语义 = 真断电 (老板 10-27 拍板, §0 L80) + 待机口径 (§0 L84) + 关机时充电灯 (§0 L86) 已锁死 ⇒ ②待裁: 量产刷写口是否采纳「镜脚 USB pogo」(与 ISS-092 检修口建议合并裁决, 免得两单各开一条路) ③待裁: 「SoC 在镜脚还是镜框」口径冲突 (ISS-014 决策文字写挪镜框, 而 SCHEMATIC_V1 P1/P9 与 MECH_BUDGET §1.1 都是镜脚; 本单按图上现状 = 镜脚执行 TMP117 测点) ⇒ 请 main 一并裁, ③属老板级。 | ①已由 §0 锁死表闭合; ②③ 需要跨域裁决 (SW 问 hw-lead / mech-lead, 老板拍板) ⇒ 不是 SW 侧能自己答的。 | [官方] PROJECT_TRACKER.md §0 L80 / L84 / L86 · [实测·本机文档] HW/SCHEMATIC_V1 (P1/P9) + MECH/MECH_BUDGET.md §1.1 (镜脚) + HW/PCB/RESET_P0_FIX_PLAN.md | [官方]/[实测] | Y |
| `sw_power_state_naming` | main (PM 域落名) | ★请把 SW 侧电源状态命名 poweroff / standby 补进 §0 锁死表与 INTERFACES.md ⇒ 现状: §0 锁死表 L80/L84 已用「关机语义 / 待机口径」措辞并把旧值标 [旧口径·已作废], 但★两个标识符 poweroff/standby 仍未出现在 PROJECT_TRACKER.md 与 INTERFACES.md 里★ ⇒ SW 侧取值已登记 (sw_power_state_names=poweroff/standby), 请 main 补落名这一步。 | 改需求/锁死表是 PM 域的动作 ⇒ sw-lead 只登记不自改 (ISS-104 已定术语, 只差落名)。 | [实测] 本单 2026-11-23 08:5x 实跑 grep -n 'poweroff\|standby' PROJECT_TRACKER.md INTERFACES.md ⇒ 零命中 · [官方] PROJECT_TRACKER.md §0 L80/L84 (旧值已标 [旧口径·已作废]) + SW/POWER_STATE_SEMANTICS.md | [实测]/[官方] | N |
| `s2_param_fill_backfill` | main (投板前必须定) | ★板端回读通道 + 工厂标定台账时点未定 ⇒ CB-02/CB-06/CB-07 永远判未验: ①板端回读通道走 board_test.verify.readback_cmd / readback_target —— 靠原厂工具回读还是自研? ②factory 标定台账 (board_test.checks.calib_ledger = 该 SN 的标定 ID) 是标定工位出还是返修工位出? ⇒ F6 标定丢失是返修最大的坑, CB-07 判不过等于 BR-01 判不过。 | ★这一趟无法自己查 (标定工位/工装是工厂流程决策) ⇒ 但它是「投板前必须定」, 不是外部依赖 ⇒ 属内部流程决策。 | [官方] SW/S2_BOARD_TEST_CHECKLIST.md (CB-02/CB-06/CB-07) + SW/SW_REQUIREMENTS.md (F6) · [实测·本机文档] SW/tools/s2_rescue_config.json | [官方]/[实测] | Y |
| `display_recompose_1920x1080` | sw-lead (整机阶段) | ★分辨率 800×600 → 1920×1080 (老板 11-02 01:12 拍板) 的 SW 侧四项重做: ①画框/检测结果的分辨率映射与最小线宽判据 (PPD 26.7 → 16 PPD/° ⇒ 1px 细线在 120° FOV 下会被光波导 MTF 吃掉) ②检测框密度与文字字号策略 ③合成/缩放负载 (×4.3 像素) 与 60ms 预算分配 ④ISS-063「120°→30° 映射」前提作废 ⇒ 映射规则重定义 ⇒ ★demo 段用 Waveshare 2.8" 480×640 不受此影响; 整机段做, 归 sw-lead 下一轮排期★。 | ★与板那一趟无关★ (纯软件侧的分辨率映射与判据, 不改板框/板厚/层数/位号/布线) ⇒ 排在整机屏选型之后。 | [官方] PROJECT_TRACKER.md (11-02 01:12 老板拍板 1920×1080) · [实测·本机文档] SW/DEMO_OD_TIMING_SPEC.md (TX 物理下限 7.776ms @1080p) + SW/DEMO_OD_PIPELINE_SPEC.md (demo 口径 480×640) | [官方]/[实测] | N |
| `iss139_f9_sample_window` | main (排样机/设备窗口) | ★请把 HW/STEP1_LANDING_LIST.md F9 (ISP tuning 1080p 档缺 mesh, 现 = 待清) 的状态 + 样机/设备窗口 (灰卡暗室 半天~1 天) + 责任人 写进落地清单与项目计划表 ⇒ 本单不碰 HW/; ★档期提醒★: 标定窗口占的是板回板后的调试档期 (卡出图不卡板) ⇒ 档期被占会让 demo 段 1~2 人日滑成整机段 1~2 人周。 | 排期与责任人 = main 地界 (SW 侧只提供档期影响量级)。 | [官方] HW/STEP1_LANDING_LIST.md F9 · [实测·本机文档] HW/IMX415_DEMO_SENSOR_FACTS.md §3.3 | [官方]/[实测] | N |
| `iss139_pipeline_spec_effort_alignment` | main (口径裁决) | ★口径差待裁: SW/DEMO_OD_PIPELINE_SPEC.md 7.2 第 9 行写路径 B ISP tuning = 0~1 人天(微调), 而既有实测记录 HW/IMX415_DEMO_SENSOR_FACTS.md §3.3 给的是 1~2 人日 (补 1920×1080 mesh + AE 曝光表换算, 含一次灰卡/暗室标定) ⇒ sw-lead 建议取 1~2 人日 ⇒ 裁完请派单改那 1 行 (本单未改: DSI payload 口径 11-11 刚统一, 不许碰)。 | ★口径裁决是 main 地界★ (改了会影响整机排期账)。 | [实测·本机文档] SW/DEMO_OD_PIPELINE_SPEC.md §7.2 + HW/IMX415_DEMO_SENSOR_FACTS.md §3.3 | [实测] | N |
| `iss139_od_input_dist_script` | sw-lead (板可达后) | ★立项书 4.2 B 组的 OD 输入分布统计脚本还没写 (板端 ISP 帧采样 ≥200 帧 → 与板端逐字一致预处理 → 与 calib_yolov5_100 同口径 mean/std/分位/饱和率 → 自采有标注实拍集 F1) ⇒ 板端不可达期间全部 [0数据] ⇒ 请在板可达后另派或授权本单下轮补。 | ★本机物理上做不到 (0 台设备) ⇒ 只能排期, 不能自己完成★。 | [实测] 本单 2026-11-23 08:5x 实跑 list_devices() = [] (0 台设备) · [官方] SW/MODEL_RELEASE_GATE.md (标定集口径) | [实测]/[0数据] | N |
| `iss263_board_acceptance_rk3572` | sw-lead (板到手即跑) + main (排板期) | ★板端接受性仍 [0数据]: 转换链已通 (rknn3-toolkit 1.2.0 + target_platform=rk3572, 3 次 rc=0, 产物 249,360 B md5 97a34fff0b855b92681f26627dba5354, t_total 33.389/34.108/41.672 s), 但本机 list_devices() = [] ⇒ 板端推理起不起得来 / 精度 / 板端 e2e 延迟一个数都没有 ⇒ 板到手后请按 SW/tools/iss263_roundtrip_probe.py 的 init_runtime(target=rk3572, core_mask=RKNN3_NPU_CORE_0) 口径补测 (另可用 SW/tools/rk3572_rknn3_board_smoke.sh 一条命令出 PASS/FAIL) ⇒ 路线①/②/③ 已由 ISS-263/ISS-355 事实选定 ②, 只等老板追认 (见 iss250_pick_downgrade_route)。 | ★这是「板不可达」不是「等外部」⇒ 板到手即跑, 不挂任何人的锅★。 | [实测] SW/RKNN_BENCH.md:378/384 (板端接受性 [0数据] · 板到手一条命令出 PASS/FAIL) + SW/tools/iss263_roundtrip_probe.py + SW/tools/rk3572_rknn3_board_smoke.sh · [实测] 本机 list_devices() = [] | [实测]/[0数据] | Y |
| `iss250_rknn3_board_toolchain` | sw-lead (板到手) + main (准备 adb/ssh) | ★板端 BSP 是否自带 RKNN3 runtime (librknn3_api.so + librknn3_api_native.so, RK3572 专用 native 库; RK3576/RK3588 用 rkcp 库, 不通用) ⇒ 本机 0 台设备 [0数据] 无法查 ⇒ ★官方已给可自带路径★ (rknn3-toolkit 仓的 rknn3-runtime/examples/rknn3_model_test_demo ⇒ ./build-linux.sh -t rk3572 -a aarch64 -b Release → adb push install/rknn3_model_test_Linux /userdata/ → ./rknn3_model_test <rknn> <weight> 0x1 ⇒ 返回 0 即 N1 PASS) ⇒ 请 main 在板可达时准备「adb/ssh 通路 + 可写的 /userdata」, sw-lead 自解板端精度评测器 (lite3 acc) 与 C API perf 采集脚本。 | ★不构成阻塞, 板到手时 sw-lead 可自解★ ⇒ 不挂账, 只登记排期依赖。 | [官网] airockchip/rknn3-toolkit 仓 rknn3-runtime/examples/rknn3_model_test_demo (官方板端命令) · [实测] SW/RKNN_BENCH.md:384 | [官网]/[0数据] | Y |
| `iss272_need_mode_watermark` | main (裁决要不要开单) | ★请 main 裁决: 在 delivery_truth.py 里记一条 mode 变更水位线, 只对水位线之后的 run 套用 mode=none, 之前一律按 announce 判 (宁可多报不可漏报) ⇒ 病灶 = collect() 用 jobs.json 的【当前】delivery.mode 套到全部 12 轮历史 run 上, 而 run 记录里 delivery.mode 字段 3796/3796 全缺 ⇒ announce 时代那批「status=ok + delivered=false = 真投递失败」会被追溯洗成「本来就不投」★ ⇒ sw-lead 建议改水位线而不是补 run 字段 (补字段要动 OpenClaw cron 上游, 周期长得多) ⇒ sw-lead 不代拍。 | ★state/delivery_truth.py 与 delivery_health.py 是 main 域地界★ ⇒ SW 侧只报不改。 | [实测] state/delivery_truth.py L116-123 (classify_run 仍只认 status=='error' + mode=none 归类, 无水位线) · [官方] state/issue_log.yaml ISS-272 (verified) | [实测]/[官方] | N |
| `iss272_need_status_blacklist` | main (裁决要不要开单) | ★请 main 裁决: 把 classify_run 的 status == 'error' 改成黑名单成功态 (status not in (ok, success, completed, None) ⇒ run_error, fail-closed 方向) ⇒ 实测 classify_run(timeout, False, none) = no_delivery / classify_run(cancelled, False, none) = no_delivery ⇒ 真故障被吞成「本来就不投」⇒ 当前风险等级 = 低 (盘上 status 取值全集 = {ok: 1669, error: 2127}, 非 ok/error 的 finished run = 0, 今天不触发) ⇒ ★代价★: 改之前必须先确认上游状态取值全集, 否则 skipped/cancelled-by-user 会被误报成 run_error ⇒ sw-lead 不代拍。 | ★同上, main 域地界★。 | [实测] state/delivery_truth.py L116-123 (精确等于 error 的写法仍在) · [官方] state/issue_log.yaml ISS-272 (verified) | [实测]/[官方] | N |
| `iss272_need_a_class_unknown` | main (裁决要不要开单) | ★请 main 裁决: 把 delivery_health.py 的 classify() 从 A/B 两分改成 A/B/U 三分 (U = unknown), 让 unknown 不受 mode=none 过滤 ⇒ 沙盒实测 E3: 一个 mode=none 的 job 连挂 5 次、错误是「认不出来的错误」⇒ A 类 0 条 / B 类 0 条 ⇒ 一条告警都不出 ⇒ 与 classify() 自己写的兜底「认不出来 ⇒ 按真故障处理 (宁可吵, 不可漏)」直接矛盾 (A 类的 mode=none 排除把这条兜底整个吃掉了) ⇒ ★注意: 这条要改的是 delivery_health.py, 那是 A/B/D 三类的地界, 本单只报不改★。 | ★同上, main 域地界★。 | [实测] state/delivery_health.py (classify() 仍两分, 无 unknown 类) · [官方] state/issue_log.yaml ISS-272 (verified) | [实测]/[官方] | N |
| `iss309_tmp_quota_edu` | main (口径 + 环境) | ★请 main 记一条环境口径: /tmp 是带 usrquota 的 tmpfs, 配额满时拷板报 OSError Errno 122 Disk quota exceeded ⇒ 挂闸后链上闸会出现【假红】⇒ 处置已有两条: ①给链上闸加临时目录退回 (已做: 每道 R6 selftest 带 --tmpdir tmp/iss318_gates) ②给跑门禁的任务固定 TMPDIR ⇒ ★并请记口径★: /tmp 使用率 >80% 时机器闸结果不得直接当设计缺陷 ⇒ 不治的后果: 被误读成「判据坏了」⇒ 更坏: 为了让链绿去改判据。 | ★环境级卡点, 不是判据红★ ⇒ 归 main 的口径地界 (SW 侧已给自己的闸加了三级退回 + 6MB 写探针)。 | [实测] state/gate_check.py EXTRA_GATES 注释 (TMPDIR 指项目内, 明写 /tmp 带 usrquota 且配额已满) + state/issue_log.yaml ISS-306 (追加复验: 环境红不是设计红) | [实测]/[官方] | N |
| `iss321_decide_rename_batch_scope` | main / boss (批不批这 7 件) | ★请 main 拍板「板只改一次」那一趟的 SW 侧同批改动清单 7 件 (①冻结表按改名后盘面重建 ②timing_check 位号解析层 ③onepass SW03/04/05 三条现状探针 ④HW 跨域 16 位号/116 处 ⑤三道 R6 selftest 闸的夹具 ⑥清单 SW01 板 md5 重锚 ⑦SW/*.md 位号字面量) ⇒ ★实测炸点只有 3 道 (timing_check / adc_sync / chainjudge) ⇒ 不做第 2 件这三道当天就红 ⇒ 不批的后果: 那一趟门禁链 day-1 就红 ⇒ 板只改一次变成板改两次 ⇒ ★另: HW 侧 HW/check_netlist_selfconsistency.py 的 16 个位号 (116 处 · hw-lead 的域) 要不要连 hw-lead 的一起改?★ | ★批不批 = 机制取舍, main→老板拍★; sw-lead 已把 7 件逐条做成照着就能干的清单并在沙盒真跑过 rc。 | [实测·本机文档] HANDOFF/2026-11-19_sw-lead_ISS321_*.md (7 件清单 + 沙盒实测 rc) + SW/tools/check_sw_ref_reachability.py (--selftest 7/7) · [官方] state/issue_log.yaml ISS-321 (verified) | [实测]/[官方] | Y |
| `iss321_decide_r6_selftest_fixture_after_reboard` | main (选项甲/乙) | ★请 main 拍: 三道 R6 selftest 闸的夹具假设「硬保护件从没被合法改过 / 链头只有一个产出记录」⇒ 板那一趟做完一次合法改板后它们恒红 ⇒ ★实测已证明这不是改名特有 (S4 vs S8 零改名对照组同红) ⇒ 选项甲 (夹具改成「在已有链上再追加一跳」· sw-lead 建议) vs 选项乙 (把那一趟的期望值登记成已知基线 = 改闸 = 受保护资产, 要 main 拍) ⇒ 不批的后果: 三道闸在那一趟当天就红 ⇒ 掩盖真红 ⇒ 违反 ISS-309 铁律「不许把闸修成永远红」。 | ★选项乙 = 改闸 = 受保护资产 ⇒ 归 main 拍★ (ISS-309/312/315/318 四轮都只交写法没人拍)。 | [实测·本机文档] HANDOFF/2026-11-19_sw-lead_ISS321_*.md (S4 vs S8 零改名对照组实测) + SW/tools/check_demo_panel_spec_r6_selftest.py (rc=0) · [官方] state/issue_log.yaml ISS-309 (铁律「不许把闸修成永远红」) | [实测]/[官方] | Y |
| `iss321_sw_docs_rename_bulk_24files` | main (同批做 vs 单开一单) | ★请 main 拍: SW 侧 41 份 md 里 671 处位号字面量要随改名同步改 (★机器实测口径: 41 份 md / 10 份有命中 / 671 处; ISS-321 的「24 份 md / 834 处」是 (文件,行,位号) 三元组行数口径, 覆盖 30 份 ⇒ 不是数字打架, 是口径差★) ⇒ 跟板那一趟同批做 (sw-lead 建议, 「板只改一次」的前提就是所有前置一次查清) vs 板出之后单开一单 ⇒ 改法一律走机器脚本 (默认 dry-run) 不许裸 sed ⇒ 不批的后果: 跟板同批做而文档没改 ⇒ 板出之后 check_sw_ref_reachability.py 判 58 条改名漂移 (S1 实测) ⇒ 闸红; 单开一单 ⇒ 板出之后有一段时间闸是红的 (但不是假红·是真漂移·符合 ISS-318 的设计意图)。 | ★排期取舍 = main 地界★ (与板那一趟同批 vs 单开)。 | [实测] SW/tools/check_sw_ref_reachability.py (S1 实测 58 条漂移) + HANDOFF/2026-11-19_sw-lead_ISS321_*.md (机器口径 41 份 md / 671 处) · [官方] state/issue_log.yaml ISS-321 (verified) | [实测]/[官方] | Y |
| `iss321_decide_rename_doc_notation` | main (选项丙/闸豁免) | ★请 main 拍: SW 侧任何要写「改名后名」或「形状像位号但不是位号」的文档 (改名方案文档 / 作业包 / 交接页) —— 统一规定「写进 logs/ 不进 SW/」(选项丙 · sw-lead 建议) vs 给 ISS-318 的闸加一条「改名方案文档」显式豁免 (★改闸 = 受保护资产·由 main 拍★) ⇒ ★实测: 留证文档不改 ⇒ 闸判 28 条改名漂移 + 2 条新增真隐患 ⇒ 闸红★ ⇒ 不批的后果: 任何写这类文档的人都会踩同一个坑 (ISS-321 与 ISS-327 各实测踩到一次 rc=1) ⇒ 要么规定写法, 要么闸加豁免。 | ★加豁免 = 改闸 = 受保护资产 ⇒ 归 main 拍★。 | [实测·本机文档] HANDOFF/2026-11-19_sw-lead_ISS321_*.md (场景 K 实测: 28 条漂移 + 2 条真隐患) + SW/tools/check_sw_ref_reachability.py (--selftest 7/7) | [实测]/[官方] | Y |
| `iss327_decide_freeze_count_selfcheck` | main (甲/乙) | ★请 main 拍: 「冻结表条数 == 重建前 dump 的 DESIGNATOR_OK 条数」是【构造上的恒等式】(2026-11-18 树 78==78 · 2026-11-23 树 92==92 · 两次逐字相等) ⇒ 建议把这条做成闸的自检项 (--selftest 加一条夹具: freeze 输出的条数必须 == 当场 dump 的 OK 条数) ⇒ 选项甲 (加自检夹具·只加夹具不改判据逻辑 · sw-lead 建议默认值) vs 选项乙 (不动, 靠 SOP §2 步 2 人工核对) ⇒ 不拍的后果: 贴表贴漏/贴多行时人工核对容易漏, 而 MISSING 只从 3 涨到 4 (红) 或被人为抬上限 (实测 RT-9 洗白通道)。 | ★加自检夹具 = 改闸 ⇒ 归 main 拍★ (前四个 iss327_decide_* main 已答, 这条是同批第 5 条还没答)。 | [实测·本机文档] HANDOFF/2026-11-19_sw-lead_ISS327_*.md (两次逐字相等 78==78 / 92==92) + SW/tools/check_sw_ref_reachability.py | [实测]/[官方] | Y |
| `iss353_need_main_decide_iss155_blocker` | main (ISS-155 的 blocker 定位) | ★交 main 裁 (sw-lead 只交依据 + 残留代价, 不代拍): ISS-155 的 blocker 定位是否从「demo 头号卡点」降为「转换链已通 / 板端待板」⇒ 依据 = 转换链已通 [实测 config rc=0 + 转换 rc=0 + 产物逐字节可复现 md5 97a34fff…] + 官方两工具链平台归属 [官网] + 板端仍 [0数据] ⇒ 残留代价 = 板端 N1~N5 无数据 + 转换脚本已于 ISS-355 切 rknn3 ⇒ 降级后不再阻塞 demo 路线选择 (路线由 main 定, 定路线所需事实已坐实)。 | ★ISS-155 本身 status=open (owner=main, verify_by=sw-lead) ⇒ 状态变更只能 main 做★ ⇒ sw-lead 不自签 issue_log。 | [实测] SW/RKNN_BENCH.md:378 (产物 md5 97a34fff0b855b92681f26627dba5354) + SW/tools/rk3572_model_rebuild.sh --print-route · [官方] state/issue_log.yaml ISS-155 (status=open) / ISS-353 / ISS-355 (verified) | [实测]/[官方] | Y |
| `iss191_boss_pick_fix_option` | boss (决策码 S-B08) | ★复位 P0 三选一 (等老板): ② 把 Q_AND 整颗改 DNP (sw-lead 推荐) / ① Q_ENVC 摘掉或必装 (已用 RC1 反向用例实测否掉: 切不断故障链, 且 Q_ENVC 必装会把 EN_VCORE 拉低换成另一个 P0) / ③ 等 SoM 球位 TBD-01 (首台板等不起) ⇒ ★不改板、不加 IC、不等原厂★ ⇒ 建议默认值 = ② ⇒ 请回一个决策码。 | ★ISS-191 已 verified 但【落表本体 = 等老板拍②后随 RECHAIN_ONEPASS_PLAN §2 步1 一起做】⇒ 板只改一次 ⇒ 这一拍不落, 复位 P0 就一直挂着 ⇒ 这是板那一趟的前置。 | [实测] HW/netlist_v1.csv L62/63 (R_PG_PULL 必装) + L65/66/67 (Q_AND 必装) + L79/86 (PG 源 dnp=DNP) · [官方] HW/PCB/RESET_P0_FIX_PLAN.md B1/B5 + state/issue_log.yaml ISS-191 (fix_ref 明写落表本体等老板拍②) | [实测]/[官方] | Y |
| `iss191_boss_q_envc_unify` | boss (决策码 S-B08) | ★Q_ENVC 三行是否同批统一为 DNP (等老板): 现状 L71 (→PG_AND) = DNP 而 L72 (→GND) / L73 (→EN_VCORE) = 必装 ⇒ BOM 按 ref 级口径 (任一行必装 ⇒ 整颗记必装) 记 Q_ENVC 必装 (要买) ⇒ 网表口径与 BOM 口径打架; 统一 DNP 后 BOM 记 DNP, 与「SoM 自带 PMIC, 顺序链在 SoM 内部完成」的既有结论自洽 ⇒ 建议默认值 = 统一 DNP ⇒ 请回一个决策码。 | 与 S-B08 同一落表批次 (板只改一次 ⇒ 必须一起落)。 | [实测] HW/netlist_v1.csv L71/L72/L73 · [官方] HW/PCB/RESET_P0_FIX_PLAN.md B2 落表清单 | [实测]/[官方] | Y |
| `iss191_boss_r_pg_pull_dnp` | boss (决策码 S-B08) | ★R_PG_PULL 两行是否也改 DNP (等老板): 收益 = PG_AND 上只剩两个测试点时, 10k 上拉挂 1.8V 常流 180µA ⇒ 1.8V 侧 0.324mW / 电池 3.7V 侧 0.666mW ⇒ 420mAh ÷ 180µA ≈ 97 天; 代价 = 将来若按③接真实 PG, 这个上拉要回来 ⇒ ★建议默认值 = ③ 落地前不要动★ ⇒ 请回一个决策码。 | 与 S-B08 同一落表批次; 三条拍板项在 ISS-191 fix_ref 里同批等。 | [实测] HW/netlist_v1.csv L62/L63 (10k ±1% 必装) · [官方] HW/PCB/RESET_P0_FIX_PLAN.md B2 | [实测]/[官方] | Y |
| `iss234_boss_pick_5q` | boss (决策码 S-B09) | ★ISS-234 给老板的 5 条待拍 (每条带推荐默认值但不代拍): Q1 demo 板要不要关机态 / Q2 负载开关选型 ISS-172 / Q3 关机电流账 108µA 口径 / Q4 demo 关机时充电灯 / Q5 长按10s话术 ⇒ 请回 5 个决策码。 | ★老板级 ⇒ 不代拍★; 五条建议默认值见交卷页 §3 决策码表 S-B09-a~e。 | [官方] state/issue_log.yaml ISS-234 (verified) + PROJECT_TRACKER.md §0 L80/L84/L86 (关机语义 / 待机口径 / 关机充电灯 三条已锁死) + [实测·本机文档] HW/POWER_SHUTDOWN_V3.md §6 | [官方]/[实测] | Y |
| `iss234_hw_doc_conflicts` | main (裁) | ★两处 HW 口径冲突请项目总工裁: (1) 待机 0.15W 的皮肤温度 —— POWER_SHUTDOWN_V3 §6 写 41.6-42.6°C 而 POWER_BUDGET_V3 / SW 镜像写 45.9-46.9°C ⇒ sw-lead 取保守侧 (45.9-46.9°C) ② 关机账 —— VBUS_DET 50µA 与文中 100k+100k 算式对不上 (5V/200k = 25µA) 且现行网表是 1M+1M ⇒ 本单不改 HW/, 请项目总工裁。 | ★冲突在 HW/ 文档 ⇒ sw-lead 不越界改 (只读) ⇒ 归 main 裁并派单。 | [实测] HW/netlist_v1.csv L434/435/436 (现行 1M+1M) · [官方] HW/POWER_SHUTDOWN_V3.md §6 + HW/POWER_BUDGET_V3.md (镜像值) | [实测]/[官方] | N |
| `iss250_pick_downgrade_route` | boss (决策码 S-B10 · 追认签字) | ★降级方案选哪条 (B8 路线①/②/③): ① rk3576-target 维持现状 (新增下载 0 B, 板端接受性 [0数据], 失败则整条作废) ② rknn3-toolkit 1.2.0 独立 conda env (需 98 MB wheel + numpy>=2.0/torch>=2.2 与 toolkit2 2.3.2 冲突 + RK3572 仍 Beta) ③ 降 OD 负载 / 回 RK3576 换 SoC (板级改版+重打样, 周级) ⇒ ★技术上路线②已被事实选定★ (ISS-263 实测 config('rk3572') rc=0 / 产物 md5 97a34fff… 三次一致 / ISS-355 脚本已迁主路线) ⇒ ★现在只等老板追认签字★ (路线①/③ 涉 60ms 生死与换芯片 = 商务决策) ⇒ 三条共用同一套 N1~N5 判据 ⇒ 换路线不换判据 ⇒ 请回一个决策码。 | ★老板级 (商务决策) ⇒ 不代拍★; 技术事实已坐实, 只差签字。 | [实测] SW/RKNN_BENCH.md:378/382 + SW/tools/rk3572_model_rebuild.sh --print-route · [官方] state/issue_log.yaml ISS-250 / ISS-263 / ISS-355 (verified) | [实测]/[官方] | Y |
| `iss250_n3_threshold_recheck` | boss (决策码 S-S10 · 观察项/硬门槛) | ★N3 通过线 t_npu ≤ 13.30ms 必须重估, 不可当既定门槛: 该线的基数是「RK3572 ≈ RK3576 的纯 NPU 13.305ms」[推算], 而 RK3576 官方 datasheet = 6 TOPS@INT8 [官网] 而 RK3572 = 4 TOPS [媒体] ⇒ 算力差 −33% ⇒ 同产物在 RK3572 上的纯 NPU 耗时可能 ×1.5 ⇒ 52.91ms 那条模式A e2e 也要打折 ⇒ ★请老板拍: ① 现在就把 N3/60ms 降级为观察项 ② 还是等板端实测后按实测重定线★ ⇒ ★同时给出板端取数口径: 纯 NPU 耗时须 C API RKNN_QUERY_PERF_DETAIL 取, 拿不到就判 INDET, 不许拿 SDK 总耗时顶 (N4 铁律)★ ⇒ sw-lead 只列不拍 (老板级)。 | ★老板级 ⇒ 不代拍★; 与 S-B10 同批 (同一条路线的事实基础)。 | [实测·本机文档] SW/research/ISS250_rknn_toolkit2_target_查证表.md E-19 (RK3576 6 TOPS vs RK3572 4 TOPS) · [官网] rock-chips.com RK3576 Brief Datasheet · [媒体] RK3572 4 TOPS (Forlinx 官方页) | [实测]/[官网]/[媒体]/[推算] | Y |
| `iss255_pcb_exit_vs_full_green` | main (口径) | ★请 main 明确验收口径: 任务书 §⑤「chain_gate --full 准出段也要绿」与硬规矩①「③ 必须保持红」在板侧那趟 (PCB 类) 没排上之前互斥 (③ 的准出 = check_pcb_nets rc=1, 改前改后同色) ⇒ sw-lead 按硬规矩①选 (③ 红) 并如实报, 未为「准出段好看」去调它 ⇒ 请拍以「③ 红 + ②④ 准出绿」为准。 | ★口径裁决 = main 地界★ (sw-lead 只报事实, 不为好看调判据)。 | [官方] state/issue_log.yaml ISS-255 (verified) · [实测] state/chain_gate.py + state/check_pcb_nets.py (口径原文) | [官方]/[实测] | Y |
| `iss255_pcb_anchor_needs_kicad_python` | main (拍板) | ★请 main 拍板: ISS-255 的③判据复用 state/check_pcb_nets.py (走 state/pcbnew_py.sh ⇒ 需 KiCad AppImage 的 python, 本机有, 实测 0.63s 一次) ⇒ 若将来在没有 KiCad 的机器上跑快检, ③ 会走「保守判红」分支 (不许假绿) ⇒ 那台机器上③恒红 ⇒ 是否要一个「纯文本解析 .kicad_pcb」的无 KiCad 兜底实现? ⇒ ★本单没做: 那是另一份工作量且会引入两套解析口径的风险★。 | ★机制取舍 = main 地界★ (两套解析口径的风险由 main 判)。 | [实测] state/pcbnew_py.sh + state/check_pcb_nets.py (本机有 KiCad python, 0.63s 一次) · [官方] state/issue_log.yaml ISS-255 (verified) | [实测]/[官方] | Y |
| `iss293_sw_m7r6_sync_to_main` | main (PM 域派单) | ★请 main 拍板并派单: SW/SW_REQUIREMENTS.md 的 M7-R6 要不要同步改 ⇒ 现状描述仍是旧口径 (「电池过充/过放保护电路验证通过 (硬件, 软件侧确认电量读取正常)」) ⇒ ★建议同步改★: 判据改成「按 BAT_DET 现值判 (100k+60k+100nF 必装 ⇒ R_th=37500.0Ω · 12bit LSB=0.439mV 满量程 1.8V · 建立 33.791ms ⇒ 采样前丢弃 ≥34ms 的转换 · 漏电偏移 0.0375V = 2.1%FS 可软件标定 · @4.2V 节点 1.575V ≤ abs-max 1.98V)」⇒ ★改需求是 PM 域的动作 ⇒ 我只登记, 不自改★ ⇒ ★实测现状仍需改★: 本单实读 SW/SW_REQUIREMENTS.md:471 的 M7-R6 一行仍是旧口径。 | ★改需求真源 = PM 域 (main) ⇒ sw-lead 只登记不自改★。 | [实测] SW/SW_REQUIREMENTS.md:471 (本单 2026-11-23 08:5x 实读, M7-R6 仍是旧口径) + SW/tools/timing_check.py --only F4_adc_det (rc=0, 六判据全 True) + SW/tools/check_timing_review_adc_sync.py (rc=0, --selftest 4/4) + SW/SW_TIMING_REVIEW.md §14 | [实测]/[官方] | Y |
---

## §6 · 对账表 (关 74 / 留 70 / 新答 9)

| 项 | 数 | 对账依据 |
|---|---|---|
| 原 `needs_from` | 144 | `state/fragments/sw.yaml` 改前 md5 `e6ef9324c83efcefd9337fcd432ec5b8` (副本 `logs/iss357/sw.yaml.bak_pre_iss357`) |
| 关 (→ `needs_closed`) | 74 | 每条一行依据 (本页 §5.1/§5.2 + §4 + §3.2) ⇒ **无一条依据为空, 无批量清空, 无把 118 条批量标同一个结论** |
| 留 (仍在 `needs_from` ⇒ `needs_open_ledger`) | 70 | 每条带 owner + 一句话问法 + why + evidence + 级别 + board |
| ★平账★ | **70 + 74 = 144 = 144** | ✔ 由 `logs/iss357/apply_iss357.py` 落盘后自检断言 (`assert tot == 144`) |
| 新答 (写进 `answers`) | 9 | `answers` 49 → 58; ★新写 key 与既有 49 条 key 零相撞 (落盘前自检断言)★ |
| `waiting_on` 字段订正 (空/`agent` → `boss`) | 6 | 条目一条不删, 只订正「等谁」 |
| `to` 改派 (main → hw-lead) | 1 | `iss291_sw_vbus_det_d_digital_caliber` (SW 侧已闭合, 剩三个硬件问) |
---

## §7 · 与板那一趟相关的 SW 侧待答输入清单 (★给「板只改一次」那一趟★)

★**口径**: 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ ★**板只改一次** ⇒ ★**凡与「板框 / 板厚 / 层数 / 镜腿宽度 / 检修口净空 / 重量预算 / 位号改名 / 布线 45→0 / Gerber 投产包重出 / Q3 存储分档」有关的待答条目, 都要标出来**★。
★**本单 `needs_open_ledger` 的 `board` 字段已逐条标好: `Y` = 与板那一趟相关, `N` = 无关 (纯软件 / 纯流程)** ⇒ **board=Y 共 45 条 / board=N 共 25 条**。

### §7.1 · board = Y 的 45 条 (★按 owner 分组★)

| owner | 条数 | need key |
|---|---|---|
| — | 15 | `fw_boot_storage_bom` · `fw_boot_mode_hw` · `sw_reset_hw_changes` · `sw_poweroff_gpio_pin` · `iss275_sw_ledger_format_contract` · `iss318_sw_ref_impact_gate` · `iss318_sw_ref_baseline3_disposition` · `iss327_decide_registry_rebuild_trigger` · `iss327_decide_missing_baseline_mechanism` · `iss327_decide_drift_class_semantics` · `iss327_report_c1_c7_c8_c13_launder_faces` · `iss335_ref_gate_v1_or_v2` · `iss338_need_usbif_cc1_cc2_rule` · `iss338_need_boot_storage_answer` · `iss338_need_jtag_group_decision` |
| hw-lead (落表批次) | 4 | `iss190_netlist_reset_n_held_low` · `iss190_netlist_supv_divider_0R_short` · `iss190_netlist_q_envc_dnp_mismatch` · `iss234_battery_chain_dnp` |
| boss (决策码 S-B08) | 3 | `iss191_boss_pick_fix_option` · `iss191_boss_q_envc_unify` · `iss191_boss_r_pg_pull_dnp` |
| hw-lead (选型 + 板那一趟) | 1 | `iss190_netlist_usb_dminus_no_esd` |
| hw-lead (板那一趟 · 改 land) | 1 | `iss241_f1_f2_land_redraw_needed` |
| main (落表批次) | 1 | `iss191_orig_som_pg_reset_spec` |
| hw-lead (载板下载态入口) | 1 | `s2_boot_entry_hw_rk3576` |
| hw-lead (三个硬件侧未决) | 1 | `iss291_sw_vbus_det_d_digital_caliber` |
| main (①③) + boss (③ SoC 位置) | 1 | `sw_poweroff_semantics` |
| main (投板前必须定) | 1 | `s2_param_fill_backfill` |
| sw-lead (板到手即跑) + main (排板期) | 1 | `iss263_board_acceptance_rk3572` |
| sw-lead (板到手) + main (准备 adb/ssh) | 1 | `iss250_rknn3_board_toolchain` |
| main / boss (批不批这 7 件) | 1 | `iss321_decide_rename_batch_scope` |
| main (选项甲/乙) | 1 | `iss321_decide_r6_selftest_fixture_after_reboard` |
| main (同批做 vs 单开一单) | 1 | `iss321_sw_docs_rename_bulk_24files` |
| main (选项丙/闸豁免) | 1 | `iss321_decide_rename_doc_notation` |
| main (甲/乙) | 1 | `iss327_decide_freeze_count_selfcheck` |
| main (ISS-155 的 blocker 定位) | 1 | `iss353_need_main_decide_iss155_blocker` |
| boss (决策码 S-B03 / S-B04) | 1 | `model_license_stack_decision` |
| boss (决策码 S-B06) | 1 | `demo_od_model_route_m1_vs_m2` |
| boss (决策码 S-B09) | 1 | `iss234_boss_pick_5q` |
| boss (决策码 S-B10 · 追认签字) | 1 | `iss250_pick_downgrade_route` |
| boss (决策码 S-S10 · 观察项/硬门槛) | 1 | `iss250_n3_threshold_recheck` |
| main (口径) | 1 | `iss255_pcb_exit_vs_full_green` |
| main (拍板) | 1 | `iss255_pcb_anchor_needs_kicad_python` |
| main (PM 域派单) | 1 | `iss293_sw_m7r6_sync_to_main` |
### §7.2 · board = Y 里★最要紧的 6 条★ (板那一趟开工前必须有答案)

| # | need key | 为什么卡板那一趟 | 不答的后果 |
|---|---|---|---|
| 1 | `iss191_boss_pick_fix_option` (+ `iss191_boss_q_envc_unify` + `iss191_boss_r_pg_pull_dnp`) | 复位 P0 三选一 (S-B08) ⇒ ISS-191 的**落表本体**正卡在这 ⇒ 落表要改板 md5 ⇒ 必须与位号改名合并成一次整链重出 | ★按现网表装板 RESET_N 恒低 ⇒ **首台板起不来**; 且板 md5 会变第二次 ⇒ 违反「板只改一次」 |
| 2 | `iss241_f1_f2_land_redraw_needed` | 3 处 pad 序缺陷 (D_ESD_CAM 器件脚接错 / Q_AND pad 序 D/S/G vs AO3400A 引脚序 G/S/D ⇒ 硬件 AND 变 OR / 5 件按键 land 外扩超 bbox) | ESD 不工作 + 硬件 AND 变 OR ⇒ **下一轮才炸, 且炸在装配后**; 5 个键 land 要一次画齐 |
| 3 | `iss190_netlist_usb_dminus_no_esd` | D− 侧无 ESD (D_ESD_USB_D 只跨 D+ 与地) ⇒ Type-C 是现网表上**唯一的刷写口** ⇒ 变砖 = 只能拆机 JTAG | 一次 ESD 打到 D− ⇒ **变砖只能拆机**; 与老板 G1a 的 W-2 那一格同批 |
| 4 | `iss190_netlist_supv_divider_0R_short` | U_SUPV 三行全 DNP 但 R_SUPV_DIV1/DIV2 仍必装 ⇒ 按 BOM 装 0Ω = V_SOC_IO 短路 | 进限流 ⇒ IO 域塌陷 ⇒ **整机不启动 + 器件发热** (装配级灾难) |
| 5 | `iss321_decide_rename_batch_scope` (+ `iss321_sw_docs_rename_bulk_24files` + `iss321_decide_r6_selftest_fixture_after_reboard` + `iss321_decide_rename_doc_notation`) | S1 位号改名那 7 件批不批 (S1 同批) ⇒ 不做第 2 件 (timing_check 位号解析层) 三道闸当天就红 | 那一趟门禁链 day-1 就红 ⇒ **板只改一次变成板改两次**; 板出之后 `check_sw_ref_reachability.py` 判 58 条改名漂移 |
| 6 | `iss263_board_acceptance_rk3572` + `iss250_rknn3_board_toolchain` | 板端接受性 [0数据] (0 台设备) ⇒ 板到手即跑的两条命令清单已备好 | 板回来还要重新摸一遍工具链 ⇒ 调试档期白等 |
### §7.3 · ★SW 侧已经定了、可直接用的值 (不用重复讨论)★

| 项 | 现行值 | 出处 |
|---|---|---|
| RK3572 转换 target | `rknn3-toolkit 1.2.0` + `target_platform='rk3572'` (config rc=0 / 产物 md5 `97a34fff0b855b92681f26627dba5354` 三次一致) | `SW/RKNN_BENCH.md:378` |
| 转换脚本入口 | `SW/tools/rk3572_model_rebuild.sh` (v2.0 默认路线已迁 rknn3 + rk3572) | `SW/RKNN_BENCH.md:382` |
| 板端接受性 | **[0数据]** (0 台设备) ⇒ 板到手一条命令出 PASS/FAIL: `SW/tools/rk3572_rknn3_board_smoke.sh` | `SW/RKNN_BENCH.md:384` |
| 启动存储分档 (Q3) | SPI-NOR ⇒ **J_BOOT1 焊盘位已在板** ⇒ 板侧零动作, **不重出板**; eMMC ⇒ 153-ball TFBGA 11.5×13.0mm ⇒ 板宽 12→15mm ⇒ 产品板档须在板那一趟开工前进网表 | `state/issue_log.yaml` ISS-346 / ISS-350 (verified) + 网表 L202/204/206/208 |
| 硬保护 / 留痕 / 反向用例闸链 | 10 道钉板 md5 闸全绿 + EXTRA_GATES 已挂 5 道 SW 侧闸 (ISS-318 位号引用 / ISS-315 落表留痕 / ISS-315 硬保护反向 / ISS-312 链头交叉 / ISS-309 R6 反向) | `state/gate_check.py` EXTRA_GATES (本单实读) |
| 板 md5 (钉板真值) | `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` | 本单交卷前后逐字节相同 |
★**SW 域已交的现成件, 本单不重做 (只读不写)★: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (7 件同批清单) · `SW/ONETRIP_SW_RENAME_SAFETY.md` (闸脚本安全性) · `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (改名后闸链复活 SOP) · `SW/MODEL_LICENSE.md` (许可证据链) ⇒ ★**本单只交「还没答的条目」**★。

---

## §8 · 证据分级 (本单全部结论的级别汇总)

★**标签对照**: 本单用 `[官网]` 表示机检证据标签集里的 **官方** (同一档, 结构域习惯叫「官网」); `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 四档齐。

| 结论 / 数 | 级别 | 来源 |
|---|---|---|
| 机检缺口 sw-lead **98 → 33** / 全局等外部 **50 → 46** / 全局等总工 **356 → 295** | [实测] | `state/gate_check.py` 两次实跑 (`logs/iss357/gate_check_BEFORE.txt` / `gate_check_AFTER.txt`) |
| merge rc=0 · gate rc=0 · Q1 18/18 · 自闭合 0 条 | [实测] | `logs/iss357/merge_AFTER.txt` / `gate_check_AFTER.txt` |
| 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` | [实测] | `md5sum` + `stat`, 交卷前后逐字节相同 |
| 144 条逐条分类, 平账 70 + 74 = 144 | [实测] | `logs/iss357/apply_iss357.py` 落盘后自检 (`assert tot == 144`) |
| 373Mbps / 246Mbps 旧 DSI payload 数字全仓零命中 | [实测] | 本单 08:5x 实跑 `grep -rn '373Mbps\|373 Mbps\|246Mbps\|246 Mbps' HW/ SW/ state/outbox/` |
| `U_EN_SW` 网表 L442 已有 IC 行 (grep count = 1) | [实测] | 本单实跑 `grep -n 'U_EN_SW' HW/netlist_v1.csv \| grep -c ',IC,'` |
| I2C_A 上拉 note 已改 (2.2k/1.8V/0.64mA/186ns) | [实测] | 本单实读网表 L167/L168 |
| BAT_DET 链已补装 (100k+60k+100nF 必装) | [实测] | 本单实读网表 L181~L186 |
| `Q_AND` 仍必装 (L65/66/67) ⇒ RESET_N 恒低风险**仍在** | [实测] | 本单实读网表 |
| `Q_ENVC` 仍 L71=DNP / L72·L73=必装 ⇒ dnp 自相矛盾**仍在** | [实测] | 本单实读网表 |
| `U_SUPV` 三行 DNP 而 `R_SUPV_DIV1/DIV2` 仍必装 ⇒ 短路风险**仍在** | [实测] | 本单实读网表 L404/405 + L407/408/409 |
| `D_ESD_USB_D` 仍只跨 D+ 与地 ⇒ D− 无 ESD **仍在** | [实测] | 本单实读网表 L417/L418/L420/L421 |
| VBUS_DET 仍 1M+1M+100nF ⇒ 节点 0.185V ≪ 2.3V 阈值 | [实测] | 本单实读网表 L434/435/436/438/439 |
| `check_demo_panel_spec_r6_selftest.py` rc=0 (红已消) | [实测] | 本单 08:5x 实跑 (TMPDIR 指项目内) |
| 5 道 SW 侧闸已挂 EXTRA_GATES | [实测] | 本单实读 `state/gate_check.py` EXTRA_GATES |
| `sw.yaml` 改前 md5 `e6ef9324c83efcefd9337fcd432ec5b8` / 改后见交卷单 §B6 | [实测] | `md5sum` + `logs/iss357/sw.yaml.bak_pre_iss357` |
| `SW/MODEL_LICENSE.md` md5 `7641e5d0b0967cf3b1b03f9af9f1a27e` 前后不变 | [实测] | `md5sum` |
| `state/gate_check.py` md5 `5f370bb8cf828473e70ccc5d6412da98` / `state/merge.py` md5 `c9191025020fefd9b475e2573a335815` 前后不变 | [实测] | `md5sum` |
| Rockchip 官方工具链 (RKDevTool Win/Linux/macOS + 开源 rkdeveloptool 可脚本化批量) | [官网] | `github.com/rockchip-linux/rkdeveloptool` README + Radxa docs + u-boot `doc/README.rockchip` |
| RK3576 USB3.1/Type-C + USB2.0 OTG/HOST ×2 · Security(TrustZone / Secure boot / Key ladder / RSA4096·AES256·SHA512) · MCU Cortex-M0 ×1 | [官网] | rock-chips.com `RK3576 Brief Datasheet V1.2-20240311.pdf` |
| RK3576 boot 优先级 = SARADC_VIN0_BOOT 电压档位 + MaskROM 只走专用 MaskROM USB 口 | [官网] | Flipper One docs (引 RK3576) + Rockchip Secure Boot Application Note V1.9 §1.4/1.5 |
| Rockchip Secure Boot 校验链 = OTP 公钥 hash + RSA2048 + SHA-256, 不通过拒绝启动 | [官网] | Rockchip Secure Boot Application Note V1.9 §1.4/1.5 |
| U-Boot bootcount / rollback 可配 (A/B 自动回滚 N=3 可自配) | [官网] | u-boot 通用机制 + `doc/README.rockchip` |
| Rockusb VID 2207 (MaskROM / Loader 枚举特征) | [媒体] | Rockchip 生态公开资料 + 板端 `lsusb` 实测路径 |
| RK3572 = 4 TOPS (Forlinx FET3572-C / OK3572-C 官方页) | [媒体] | forlinx.net 官方参数页 |
| `yolov5s-sim` = ultralytics/yolov5 v6.0 导出物 ⇒ AGPL-3.0 (证据链 7 环, `license_probe.py` 可复现) | [实测] + [官方] | `SW/MODEL_LICENSE.md` §1.2 (第⑥环本机 ultralytics 8.4.80 METADATA / 第⑦环 GitHub API) |
| YOLOX-s Apache-2.0 许可 + 权重本机可下载 (35,891,401 B / sha256 `a39c8476…`) + 官方 NPU 配方 `examples/yolox` | [官网] + [实测] | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-3 |
| RK3572 AON 域 / 常开唤醒脚具体脚号 | [0数据] | 公开渠道查不到 + Forlinx 官方页未列独立 MCU ⇒ **已写降级方案 (§4 ③-8)** |
| SoM 内部 RESET 释放时序 / PG 极性 / 内部复位电路构成 | [0数据·板级不可控] | 属 SoM 内部, 主板不产核心轨 ⇒ **已写降级方案 (改接法不改板)** |
| RK3572 纯 NPU 13.305ms ⇒ RK3572 上的同产物耗时 | [推算] | ISS-250 查证表 (基数来自 RK3576 同族实测 + 4/6 TOPS 算力差) |
| Ultralytics Enterprise 报价与周期 (US$5k-50k / 4-12 周 / 量级 10^4-10^5 USD) | [推算] + [0数据] | `SW/MODEL_LICENSE.md` §3 (官方无公开价 [0数据], 报价制 [官方·定性]) |
---

## §9 · 本单留下的待办 (都不阻塞板那一趟)

| # | 待办 | 谁 | 为什么不是阻塞 |
|---|---|---|---|
| T-1 | 老板回 12 个决策码 (§3.1) | boss | ★技术事实全部坐实, 只差签字★; 每条都给了建议默认值与不拍的后果 |
| T-2 | `needs_open_ledger` 里 owner=hw-lead 的 6 条 (落表批次 + 选型) | hw-lead | 都要与板那一趟同批落表 ⇒ 不单独排 |
| T-3 | `needs_open_ledger` 里 owner=main 的 12 条 (PM 域派单 / 口径裁决 / 排期) | main | 都是流程与口径, 不卡软件实现 |
| T-4 | `needs_open_ledger` 里 owner=sw-lead 的 3 条 (板到手即跑 / 板可达后补脚本) | sw-lead | ★板不可达 ⇒ 不是外部依赖★, 板到手即跑 |
| T-5 | 板端接受性 N1~N5 全部 [0数据] (0 台设备) | sw-lead + main | 同上 |
| T-6 | 两个重建件 (sha16 `1e2c716bd16ed9d3` / `dfb5d060ca36fc27`) 仍 licensing-hold | sw-lead | 按换栈 (S-B03/S-B04) 处置; 禁入 AGPL 交付集 |
---

## §10 · 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss357_tmp          # ★/tmp 带 usrquota 且配额已满 ⇒ 临时目录指大盘★
python3 logs/iss357/apply_iss357.py         # ★重跑会重放本单处置 (幂等: 4 个断言全过 + 平账 144)★
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/MODEL_LICENSE.md state/fragments/sw.yaml
```
