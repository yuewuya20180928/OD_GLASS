# HW/PCB/BOARD_ONEPASS_PREFLIGHT.md · 「板只改一次」那一趟的【板侧项全集】

> ★**派活**: `state/dispatch_briefs/ISS-277_hw_onepass_preflight_coverage.md` (项目总工 2026-11-17 07:3x) ★
> ★**本单性质**: ★**内部活 · 纯分析 + 作业包订正 + 机器闸类** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★
> ★**机器闸**: `python3 HW/check_onepass_preflight_coverage.py` (★P1~P6 + `--selftest` ★) ★
> ★**配套作业包**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (§3-S0 = 本清单的并入摘要) ★

★**一句话口径**: ★**这一页是「板只改一次」那一趟 (S1~S13) 的板侧项全集** ⇒ ★**任何一项只在交卷单里、没进这一页 = 当场红** ★
★**为什么必须有这一页**: ★**板侧项现在散在 ≥6 份交卷单 + 2 个闸 + 1 份作业包里, 没有任何一处是全集** ⇒ ★**漏做一项 = 板 md5 变第二次 = 留证链 / Gerber / 投产包 / 盖章全白跑一遍** ★

---

## §1 · 坐标帧声明 (★三条帧互不混用 ★)

| 帧 id | 含义 | 本页用在哪 |
|---|---|---|
| ★**`B160x100`** ★ | ★**160×100 台架板 (现役板)** · 8 铜层 · 160.10×100.10 · 186 封装 ★ | ★**本页所有坐标与判据一律用它** ★ |
| `F30A` | 60×30 套A 帧 | ★**只作对照, 不可代入** ★ |
| `P60x15` | 60×15 帧 | ★**只作对照, 不可代入** ★ |

★**权威帧表** = `HW/PCB/BOARD_FRAME_CALIBER.md` §6 (ISS-274) · ★**机器闸** = `python3 HW/check_board_frame_caliber.py` ★

---

## §2 · 逐条表 (★每条固定 9 个字段 ★)

★**字段**: `id` / `source_iss` / `title` / `current_state` (★必带证据等级 ★) / `action` / `criterion` (★真命令 + 期望 rc/期望值 ★) / `step` (★∈ S1~S13 ★) / `blocked_by` / `evidence` ★

| id | source_iss | title | step | blocked_by | current_state (★实测值 ★) | criterion (★真命令 ★) |
|---|---|---|---|---|---|---|
| ★**`B01_REF_SUFFIX`** ★ | ★ISS-266 ★ | 186 个封装位号加 _1 数字后缀 (KiCad 问号根因) | ★**S1** ★ | - | [实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号 (HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md §0/§2/§4) | `python3 HW/check_step1_parts_spec.py ⇒ rc=0 (问号行数=0 · 218 位号两两不重名)` |
| ★**`B02_C_VBUS_GND`** ★ | ★ISS-266 ★ | C_VBUS_GND 从 demo 主 PCB 拿掉 (B-1) | ★**S2** ★ | - | [实测] 板上仍在, 且它当下两个带网焊盘挂的是: C_VBUS_GND pad1 = GND / C_VBUS_GND pad2 = VBUS_5V_CHG ⇒ 焊盘级多余 2 | `bash state/pcbnew_py.sh state/check_pcb_nets.py ⇒ C1 缺失 0 · 多余 0 (现状: 多余 2)` |
| ★**`B03_ULDO_S28_PAD3`** ★ | ★ISS-239 ★ | U_LDO_S28 缺 pin3(EN) ⇒ 若走 A 案板须补 pad3 | ★**S2** ★ | 老板/PM 拍 A/B 案 (ISS-239 §4.2) | [实测] 脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账 (★落表后基线过期★); U_LDO_S28 无 pin3 行 ⇒ 板侧无 pad3 ⇒ 焊盘级恰 1 颗不等价 | `python3 HW/check_pin_function_labels.py --expect-known ⇒ rc=0 (★现状: 18 条缺陷 = 15 脚表功能 (14 串号 + 1 缺脚) + 3 md5 台账对账; ★脚表功能缺陷本批未变, 多出的 3 条是落表后基线过期 (KNOWN_DEFECTS 快照同步归 ISS-283)★)` |
| ★**`B04_R_SUPV_DIV_DNP`** ★ | ★ISS-244 ★ | R_SUPV_DIV1/2 = 0Ω 且 dnp=必装, 而 U_SUPV dnp=DNP ⇒ 装 0Ω 等于把 V_SOC_IO 短到地 | ★**S2** ★ | 落表批次 (V-3 归老板 A1) | [实测] 网表: R_SUPV_DIV1 / R_SUPV_DIV2 的 dnp=必装 且 value=0Ω 跳线; U_SUPV 三行 dnp=DNP | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不增 (现状 18 条)` |
| ★**`B05_U_EN_SW_VALUE`** ★ | ★ISS-269 ★ | 板封装 U_EN_SW 的 Value 属性陈旧 (B-2) | ★**S3** ★ | - | [实测] 板封装 Value = 'EN 输入 (高=放行底板)' (脚功能串, 不是器件身份) | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([f.GetValue() for f in b.GetFootprints() if f.GetReference()=='U_EN_SW'])" ⇒ 值含 TPS22991RAA` |
| ★**`B06_TPS7A20_VALUE`** ★ | ★ISS-239 ★ | 7 颗 TPS7A20 的板封装 Value 同为脚功能串 (与 B05 同根因) | ★**S3** ★ | - | [实测] 板上 7 颗 LDO 的 Value = 'EN (pin3)' / 'GND (pin2)' ⇒ 贴片程序里没有 TPS7A20-33 这个料号 | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([f.GetValue() for f in b.GetFootprints() if f.GetReference().startswith('U_LDO_')])" ⇒ 7 颗都含 TPS7A20` |
| ★**`B07_ESD_USB_D_3PIN`** ★ | ★ISS-266 ★ | D_ESD_USB_D 从 2 脚换 3 脚封装 (B-3) | ★**S4** ★ | W-1/W-2 (老板: 一颗双通道 vs 两颗单通道) | [实测] 板上是 2 脚占位 (pad1 / pad2) | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R4: D_ESD_USB_D 焊盘数 = 3` |
| ★**`B08_ESD_USB_D_NEAR`** ★ | ★ISS-266 ★ | D_ESD_USB_D 距 J_USB_C 47.99 mm (B-4) | ★**S4** ★ | W-1/W-2 (老板) | [实测] D_ESD_USB_D @ (94.95, 21.8) · J_USB_C @ (140.00, 5.25) ⇒ 中心距 47.99 mm (要求 ≤ 3.0 mm) | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R9: D_ESD_USB_D ↔ J_USB_C 中心距 ≤ 3.0 mm` |
| ★**`B09_ESD_USB_D_MINUS`** ★ | ★ISS-266 ★ | USB D− 那条路没有 ESD (B-5) | ★**S4** ★ | 落表侧另派 (B-5 两条路都要改网表) | [实测] 板上挂 USB_D_N_SRC / NET_USB_D_N_TYPEC 的 ESD 位号数 = 0 | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R4: D− 两张网的 ESD 位号数 ≥ 1` |
| ★**`B10_Q_AND_LAND`** ★ | ★ISS-244 ★ | Q_AND 占位 land 的 pad↔pin 与器件引脚序对不上 (硬件 AND 门不成立) | ★**S6** ★ | 落表批次 (AO3400A 已落) | [实测] 板: pad1=RESET_N(D) / pad2=GND(S) / pad3=PG_AND(G) = D/S/G; AO3400A 引脚序 = 1=G / 2=S / 3=D ⇒ 装上去 = 栅极接 RESET_N、漏极接 PG_AND | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_AND'][0].Pads()])" ⇒ pad1 挂 PG_AND / pad3 挂 RESET_N` |
| ★**`B11_Q_PG_LAND`** ★ | ★ISS-244 ★ | Q_PG 占位 land 序错 + 网表 note 角色与拓扑相反 (开不了机) | ★**S6** ★ | PM/老板拍写法A (ISS-244 G-1) + 落表批次改 note | [实测] 板: pad1=PWR_ON(S) / pad2=BAT_SW(D) / pad3=PWR_GOOD(G) = S/D/G; DMP3098L 引脚序 = 1=G / 2=S / 3=D; 网表 note 首句写 S=ON / D=BAT_SW ⇒ Vgs=0 不导通, PG 高时 Vgs=+3.3V 反偏 ⇒ 开机路径彻底不通 | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])" ⇒ pad1 挂 PWR_GOOD / pad3 挂 PWR_ON` |
| ★**`B12_Q_ENVC_LAND`** ★ | ★ISS-241 ★ | Q_ENVC 占位 land 序 (天然对上, 但必须核一遍) | ★**S6** ★ | - | [实测] 板: pad1=PG_AND(G) / pad2=GND(S) / pad3=EN_VCORE(D) = G/S/D ⇒ 与 SOT-23 库序一致 (三件 MOS 里唯一天然对上的) | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_ENVC'][0].Pads()])" ⇒ pad1=PG_AND / pad2=GND / pad3=EN_VCORE` |
| ★**`B13_ESD_CAM_PAD`** ★ | ★ISS-244 ★ | D_ESD_CAM 的 pad 序与单向件相反 (ESD 不工作 + CSI 负摆幅被钳到地) | ★**S6** ★ | - | [实测] 板: pad1=GND / pad2=CSI_D0_CK_P; TPD1E05U06DPYR pin1=I/O / pin2=GND ⇒ 正好相反 (另两件 ESD 是 pad1=信号/pad2=GND) | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='D_ESD_CAM'][0].Pads()])" ⇒ pad1 挂 CSI_D0_CK_P` |
| ★**`B14_S6_20_COORDS`** ★ | ★ISS-274 ★ | S6 的 20 个坐标固化钉位 (原文「21 个」是重复计数) | ★**S6** ★ | - | [实测] 20 个 distinct 坐标 (10×R_SEL_* + 10×TP_DSI_*); 其中 19 个现值已等于目标 (固化钉位), 真实位移只有 R_SEL_D3_P 一处 (78.90, 9.50 → 122.30, 5.50) | `python3 HW/check_board_frame_caliber.py ⇒ rc=0 (帧 id B160x100 · 20 个坐标逐个一致 ±0.01 mm)` |
| ★**`B15_SVC_PORT_SPLIT`** ★ | ★ISS-276 ★ | 检修口/调试口开口必须拆成两个独立窗口 (合并不可行) | ★**S6** ★ | P7 (老板) + MECH 侧 [0数据] 座体高度 | [实测] 合并窗口跨 J_UART 罩 X 17.620..20.160 与 J_DEBUG 罩 X 142.063..143.838 ⇒ 并集宽 126.218 mm 装不下; 座体真实高度 [0数据] | `python3 MECH/board_port_opening_s6_check.py ⇒ rc=0 (★属 MECH 域, 本单只登记不跑改 ★)` |
| ★**`B16_LED_G_OPTO`** ★ | ★ISS-276 ★ | D_LED_G 落位与 R_LED_G 分居板两端 (LED_G_D 走线 93.49 mm 横跨全板) | ★**S6** ★ | MECH [0数据] 光孔 + P7 | [实测] 排版器按「功能排」落位 ⇒ D_LED_G 进 Y=56.80 的 LED 行 · R_LED_G 进 X=5.90 的 I2C 上拉列 ⇒ LED_G_D 走线 93.49 mm; 光孔 [0数据] | `python3 MECH/board_port_opening_s6_check.py ⇒ rc=0` |
| ★**`B17_DNP_43`** ★ | ★ISS-269 ★ | 43 颗 DNP 位号在板上零标记 (R3 的 F3) | ★**S7** ★ | - | [实测] R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗 (★2026-11-17 09:58:16 落表 V-3=E 删了 3 行 DNP ⇒ 54/43/43 → 51/40/40, ★本条 3 个数全部随落表变, 变的是颗数不是性质★) | `python3 HW/check_netlist_contradiction_r3.py ⇒ R3-A4 零标记 = 0 颗 (⇒ findings 只剩 F2)` |
| ★**`B18_J_CHG_DISAMB`** ★ | ★ISS-247 ★ | J_CHG 位号双义 + 板侧封装块不可装配 (R3 的 F2) | ★**S7** ★ | 落表批次 | [实测] R3-A3 命中 1 ⇒ F2 在; 板上 J_CHG 是 2 脚封装, 而实物是框侧座 + 脚侧座一对 (位号双义) | `python3 HW/check_netlist_contradiction_r3.py ⇒ findings 只剩 F3 (随 B17 一起转绿)` |
| ★**`B19_BAT_DET`** ★ | ★ISS-266 ★ | R_BAT_DET_1/2 的封装与阻值 (B-8, 条件步) | ★**S5** ★ | 落表批次 (阻值归老板 A1) | [实测] 现值 1M ±1% @ (102.9, 17.5) / (107.7, 17.5); 分压链未落表 (V-3 归老板 A1) | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R8 消失 (现状: R8 在)` |
| ★**`B20_LAND_8ROWS`** ★ | ★ISS-244 ★ | 8 行落表残项的 land 必须同批重画 | ★**S10** ★ | 落表批次 | [实测] 落表残项 8 行: D_CHG_LED / D_LED_G / D_LED_R / SW_BOOT / SW_KEY_PWR / SW_KEY_VM / SW_KEY_VP / SW_RST ⇒ 其中 4 键 + 2 LED 的 land 必须同批重画 | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不增 (现状 18 条)` |
| ★**`B21_C_REGN_4U7`** ★ | ★ISS-241 ★ | C_REGN 判据错: BOM 写 1µF, TI 手册 pin22 要求 4.7µF / 10V | ★**S10** ★ | 落表批次 | [实测] BOM value = 1µF; TI BQ25896 pin22 REGN 明写 Connect a 4.7 uF (10 V rating) ceramic capacitor | `python3 HW/check_part_selection_matrix.py ⇒ rc=0 (8/8)` |
| ★**`B22_CHG_BOARD_FP`** ★ | ★ISS-241 ★ | 6 件充电板器件的 footprint 待定 (不在本板, 但会顶到本板那一趟) | ★**S10** ★ | 充电板那一趟 (不在本板) | [实测] D_ESD_TC / FB_VBUS / D_TVS_VBUS / Q_CHG_LED / D_CHG_LED / C_REGN 六件 footprint = 待定 (板文件里查无此位号) | `python3 HW/check_step1_parts_spec.py ⇒ rc=0` |
| ★**`B23_ESD_TC_4PAD`** ★ | ★ISS-244 ★ | D_ESD_TC 落了 3 通道件却只接 1 通道 ⇒ Type-C 的 D+/D− 仍裸奔 | ★**S10** ★ | 老板 (ESD 架构: 单通道 vs 双通道) | [实测] D_ESD_TC = SP0503BAHT (3 通道) 而网表只接 USB_VBUS_RAW + GND ⇒ 另 2 通道闲置 | `python3 HW/check_part_selection_matrix.py ⇒ rc=0` |
| ★**`B24_Q_PG_PART`** ★ | ★ISS-241 ★ | Q_PG 选漏电档还是栅压耐压档 (影响落料, 不影响 land 目标) | ★**S10** ★ | main/PM (ISS-241 Q-C) | [实测] 候选 DMP3098L (IDSS ≤800 nA, VGS 绝对最大手册未见 [0数据]) vs AO3407A (VGS ±20 V 明写, 高温 IDSS ≤5 µA 差 6 倍) | `python3 HW/check_part_selection_matrix.py ⇒ rc=0` |
| ★**`B25_UNCONNECTED`** ★ | ★ISS-266 ★ | unconnected 归零 (45 → 0) | ★**S8** ★ | W-1/W-2/W-4 + A1 | [实测] unconnected items = 45 · DRC 违规 = 0 (骨架阶段允许未布线) | `python3 state/check_pcb_drc.py ⇒ unconnected items = 0 · DRC 违规 = 0` |
| ★**`B26_BASELINE`** ★ | ★ISS-266 ★ | 换基线 (旧 md5 → 新 md5) | ★**S9** ★ | - | [实测] 现行基线: 板 611b869e… / .kicad_pro 3e504d2b… / 网表 e06c1dd6… / 脚表 287e7861… / BOM 94642d07… | `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv ⇒ 与新基线逐条一致` |
| ★**`B27_CHAINGATE`** ★ | ★ISS-266 ★ | 投产包准入闸 chain_gate 转绿 | ★**S11** ★ | S1~S10 | [实测] chain_gate rc=1 (③ PCB 准入红「板与网表不等价」 + ⑤ 投产资料包红) | `python3 state/chain_gate.py ⇒ rc=0` |
| ★**`B28_RELEASE`** ★ | ★ISS-266 ★ | 留证链 + 盖章 + 发布闸 | ★**S12** ★ | S10 | [实测] Gerber 32 个齐 (C6 通过); 留证链与盖章闸属 S12 | `python3 state/check_pcb_drc.py ⇒ C6 生产文件齐 · rc=0` |
| ★**`B29_WRITEBACK`** ★ | ★ISS-266 ★ | 回写台账 + 决策页 + 分片 | ★**S13** ★ | S9~S12 | [实测] 落表台账 / 决策页 / 分片 三处待回写 (★板级结论必须落决策页 ★) | `python3 state/merge.py ⇒ rc=0 && python3 state/gate_check.py ⇒ rc=0 (Q1 18/18)` |
| ★**`B30_LED_BRIGHTNESS`** ★ | ★ISS-271 ★ | LED 亮度档 G-5 未拍 (改串阻 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位) | ★**S6** ★ | 老板 (G-5 亮度档) | [实测] 1kΩ + 3.3V ⇒ 1.10 mA ⇒ KP-2012SGC 仅 0.7~0.9 mcd ⇒ 白天看不见 | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不变 (档位落表在落表批次)` |
| ★**`B31_P7_TARGET`** ★ | ★ISS-266 ★ | P7: 画哪一块板 (160×100 台架板 vs 产品板) | ★**S6** ★ | 老板 (P7) | [实测] 现役板 = 160×100 台架板 (8 铜层 / 186 封装 / 160.10×100.10); 产品板 = 60×30 套A (★另一坐标帧 F30A, 数不可混用 ★) | `python3 HW/check_board_frame_caliber.py ⇒ rc=0 (三条帧 id B160x100 / F30A / P60x15 互不混用)` |

---

## §3 · 新发现并入表 (★6 个来源单逐条映射 ★)

| 来源单 | 板侧发现 | 本页对应条目 | 状态 |
|---|---|---|---|
| ★**ISS-241** (sw-lead 11-16 22:2x) ★ | ★F-1 `D_ESD_CAM` 器件脚接反 · F-2 `Q_AND` pad 序 D/S/G vs 库 G/S/D · `D_ESD_TC` 3 通道件 ⇒ 充电板 footprint 得给 4 焊盘 · `C_REGN` 判据错 (1µF→4.7µF) · `Q_PG` 漏电档 vs 栅压耐压档 ★ | ★`B13_ESD_CAM_PAD` / `B10_Q_AND_LAND` / `B12_Q_ENVC_LAND` / `B23_ESD_TC_4PAD` / `B21_C_REGN_4U7` / `B24_Q_PG_PART` ★ | ★**作业包缺 → 本页补入** ★ |
| ★**ISS-244** (sw-lead 11-17 00:0x) ★ | ★三条实物级 P0: `Q_PG` 角色错 (开不了机) · `Q_AND` 栅漏对调 · `D_ESD_CAM` 接反 · 另: `R_SUPV_DIV1/2` 0Ω×必装 + `U_SUPV` DNP ⇒ 装 0Ω 短地 · 8 行落表残项 ★ | ★`B11_Q_PG_LAND` / `B10_Q_AND_LAND` / `B13_ESD_CAM_PAD` / `B04_R_SUPV_DIV_DNP` / `B20_LAND_8ROWS` ★ | ★**作业包缺 → 本页补入** ★ |
| ★**ISS-247** (hw-lead 11-17 00:2x) ★ | ★F2 `J_CHG` 位号消歧 · F3 板侧 43 颗 DNP 零标记 ★ | ★`B18_J_CHG_DISAMB` / `B17_DNP_43` ★ | ★F3 ≈ §3-S7 (★**只核对** ★) · ★F2 **作业包缺 → 本页补入** ★ |
| ★**ISS-274** (hw-lead 11-17 06:5x) ★ | ★S6 真实位移只有 `R_SEL_D3_P` 一处 (20 distinct 不是 21) · 坐标帧声明 ★ | ★`B14_S6_20_COORDS` / §1 坐标帧声明 ★ | ★**已并入 (追加式) → 本页只核对** ★ |
| ★**ISS-276** (mech-lead 11-17 07:0x) ★ | ★检修口/调试口开口**必须拆成两条** (合并不可行) · 座体真实高度 **[0数据]** · `D_LED_G` 光孔 **[0数据]** ★ | ★`B15_SVC_PORT_SPLIT` / `B16_LED_G_OPTO` ★ | ★**作业包缺 → 本页补入** ★ |
| ★**ISS-239** (hw-lead 11-16 2x) ★ | ★`U_LDO_S28.pin3` A/B 两案 ⇒ **若走 A 案, 板必须补 pad3** · 7 颗 TPS7A20 板封装 Value = 脚功能串 ★ | ★`B03_ULDO_S28_PAD3` / `B06_TPS7A20_VALUE` ★ | ★**作业包缺 → 本页补入** ★ |
| ★**ISS-269 / ISS-266 / ISS-271** (本轮窗口内) ★ | ★X-3/X-4/B-2 三坑 (生成器侧已修) · S1~S13 作业包本体 · LED 亮度档 G-5 未拍 ★ | ★`B05_U_EN_SW_VALUE` / `B17_DNP_43` / `B01`~`B31` 全表 / `B30_LED_BRIGHTNESS` ★ | ★**作业包已有 (只核对) + 生成器侧已修** ★ |

---

## §4 · 归属步分布表 (★S1~S13 每步至少一条, 不许有步没人管 ★)

| 步 | 条数 | 条目 |
|---|---|---|
| ★**S1** ★ | ★1 ★ | ★`B01_REF_SUFFIX` ★ |
| ★**S2** ★ | ★3 ★ | ★`B02_C_VBUS_GND`, `B03_ULDO_S28_PAD3`, `B04_R_SUPV_DIV_DNP` ★ |
| ★**S3** ★ | ★2 ★ | ★`B05_U_EN_SW_VALUE`, `B06_TPS7A20_VALUE` ★ |
| ★**S4** ★ | ★3 ★ | ★`B07_ESD_USB_D_3PIN`, `B08_ESD_USB_D_NEAR`, `B09_ESD_USB_D_MINUS` ★ |
| ★**S5** ★ | ★1 ★ | ★`B19_BAT_DET` ★ |
| ★**S6** ★ | ★9 ★ | ★`B10_Q_AND_LAND`, `B11_Q_PG_LAND`, `B12_Q_ENVC_LAND`, `B13_ESD_CAM_PAD`, `B14_S6_20_COORDS`, `B15_SVC_PORT_SPLIT`, `B16_LED_G_OPTO`, `B30_LED_BRIGHTNESS`, `B31_P7_TARGET` ★ |
| ★**S7** ★ | ★2 ★ | ★`B17_DNP_43`, `B18_J_CHG_DISAMB` ★ |
| ★**S8** ★ | ★1 ★ | ★`B25_UNCONNECTED` ★ |
| ★**S9** ★ | ★1 ★ | ★`B26_BASELINE` ★ |
| ★**S10** ★ | ★5 ★ | ★`B20_LAND_8ROWS`, `B21_C_REGN_4U7`, `B22_CHG_BOARD_FP`, `B23_ESD_TC_4PAD`, `B24_Q_PG_PART` ★ |
| ★**S11** ★ | ★1 ★ | ★`B27_CHAINGATE` ★ |
| ★**S12** ★ | ★1 ★ | ★`B28_RELEASE` ★ |
| ★**S13** ★ | ★1 ★ | ★`B29_WRITEBACK` ★ |

---

## §5 · 归老板 / 归 main 拍的清单 (★只列, 不代拍 ★)

| # | 事项 | 为什么要先拍 | 谁拍 | 拍了之后板侧要做什么 |
|---|---|---|---|---|
| ★1 ★ | ★**`U_LDO_S28.pin3` A/B 案** ★ | ★**A 案 ⇒ 板必须补 pad3** ⇒ 拍晚了 = 板要改第二次 ★ | ★老板/PM (ISS-239 §4.2) ★ | ★`B03` ⇒ 补 pad3 + 脚表补行 ★ |
| ★2 ★ | ★**LED 亮度档 G-5** ★ | ★**亮度档一改 ⇒ 改串阻 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位** ⇒ 排在 S6 之后 = 板改第二次 ★ | ★老板 (ISS-271) ★ | ★`B30` ⇒ 串阻落表 + 板面落位 ★ |
| ★3 ★ | ★**P7 画哪一块** (160×100 台架板 vs 产品板 60×30) ★ | ★**C4 是唯一不需动板的选项** ⇒ 不拍就动板 = 白改 ★ | ★老板 (ISS-266 §7) ★ | ★`B31` + 全部坐标帧声明 ★ |
| ★4 ★ | ★**`D_ESD_TC` 4 焊盘 footprint 方案** ★ | ★3 通道件只接 1 通道 ⇒ Type-C D+/D− 仍裸奔 ⇒ 架构题 ★ | ★老板 (ESD 单通道 vs 双通道) ★ | ★`B23` ⇒ 充电板那一趟 ★ |
| ★5 ★ | ★**ESD 架构 (W-1/W-2)**: 一颗双通道 vs 两颗单通道 ★ | ★`D_ESD_USB_D` 换 3 脚 = 双通道架构 ⇒ **不拍就动板 = 白改** ★ | ★老板 ★ | ★`B07`/`B08`/`B09` (★S4 是第一个真正卡在老板的步 ★) ★ |
| ★6 ★ | ★**`Q_PG` 写法A (S=BAT_SW / D=ON / G=PG)** + **漏电档 vs 栅压耐压档** ★ | ★**写法B = 开机路径彻底不通** ⇒ land 按错角色排 = 白投一版 ★ | ★PM/老板 + main ★ | ★`B11` / `B24` ★ |
| ★7 ★ | ★**A1 (V-3) 分压最终阻值** ⇒ `R_SUPV_DIV1/2` 与 `R_BAT_DET_1/2` ★ | ★**阻值一改 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位** ⇒ 排在那一趟之后 = 板改第二次 ★ | ★老板 (A1) ★ | ★`B04` / `B19` ★ |

---

## §6 · 覆盖度标记表 (★P4 的判据来源: 从 6 份来源交卷单反查 ★)

★**每个标记都必须在下面 §7 的 JSON 里出现** ⇒ ★**漏一条即红** ★

```text
标记清单 (26 个):
D_ESD_CAM
Q_AND
Q_PG
D_ESD_TC
U_LDO_S28
J_CHG
D_CHG_LED
D_LED_G
D_LED_R
SW_BOOT
SW_KEY_PWR
SW_KEY_VM
SW_KEY_VP
SW_RST
R_SEL_D3_P
J_DEBUG
J_UART
R_SUPV_DIV
U_SUPV
TPS7A20
Q_ENVC
D_ESD_USB_D
C_REGN
C_VBUS_GND
U_EN_SW
R_BAT_DET_1
```

★**来源单全集 (★清单里每条 `source_iss` 必须落在这个集合里 ⇒ 不许有来源不明的项 ★)** ★

```text
ISS-239
ISS-241
ISS-244
ISS-247
ISS-266
ISS-269
ISS-271
ISS-274
ISS-276
```

---

## §7 · 机器可读 JSON 块 (★★闸读它 · ★★本块放最后 ★★)

★**格式**: `schema` = `board-onepass-preflight/v1` · `frame` = `B160x100` · `items[]` 每条固定 9 个字段 ★
★**★不许改格式**: 闸 `HW/check_onepass_preflight_coverage.py` 按这 9 个字段判 (★缺一个即红 ★) ★

```json
{
  "schema": "board-onepass-preflight/v1",
  "frame": "B160x100",
  "items": [
    {
      "id": "B01_REF_SUFFIX",
      "source_iss": "ISS-266",
      "title": "186 个封装位号加 _1 数字后缀 (KiCad 问号根因)",
      "current_state": "[实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号 (HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md §0/§2/§4)",
      "action": "改 HW/SCHEMATIC_V1_SPEC.json 的 186 个 ref + state/gen_kicad_sch.py 三处同步; 板侧 186 个封装位号随 S6 重出自动带",
      "criterion": "python3 HW/check_step1_parts_spec.py ⇒ rc=0 (问号行数=0 · 218 位号两两不重名)",
      "step": "S1",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B02_C_VBUS_GND",
      "source_iss": "ISS-266",
      "title": "C_VBUS_GND 从 demo 主 PCB 拿掉 (B-1)",
      "current_state": "[实测] 板上仍在, 且它当下两个带网焊盘挂的是: C_VBUS_GND pad1 = GND / C_VBUS_GND pad2 = VBUS_5V_CHG ⇒ 焊盘级多余 2",
      "action": "重出板时按网表 board 列过滤 (网表两行已改判 CHG_BOARD) ⇒ 该封装自动消失; 不许手改板",
      "criterion": "bash state/pcbnew_py.sh state/check_pcb_nets.py ⇒ C1 缺失 0 · 多余 0 (现状: 多余 2)",
      "step": "S2",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B03_ULDO_S28_PAD3",
      "source_iss": "ISS-239",
      "title": "U_LDO_S28 缺 pin3(EN) ⇒ 若走 A 案板须补 pad3",
      "current_state": "[实测] 脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账 (★落表后基线过期★); U_LDO_S28 无 pin3 行 ⇒ 板侧无 pad3 ⇒ 焊盘级恰 1 颗不等价",
      "action": "A 案: 板侧给 U_LDO_S28 补 pad3 + 脚表补行; B 案: 不补 (本单不代拍)",
      "criterion": "python3 HW/check_pin_function_labels.py --expect-known ⇒ rc=0 (★现状: 18 条缺陷 = 15 脚表功能 (14 串号 + 1 缺脚) + 3 md5 台账对账; ★脚表功能缺陷本批未变, 多出的 3 条是落表后基线过期 (KNOWN_DEFECTS 快照同步归 ISS-283)★)",
      "step": "S2",
      "blocked_by": "老板/PM 拍 A/B 案 (ISS-239 §4.2)",
      "evidence": "[实测]"
    },
    {
      "id": "B04_R_SUPV_DIV_DNP",
      "source_iss": "ISS-244",
      "title": "R_SUPV_DIV1/2 = 0Ω 且 dnp=必装, 而 U_SUPV dnp=DNP ⇒ 装 0Ω 等于把 V_SOC_IO 短到地",
      "current_state": "[实测] 网表: R_SUPV_DIV1 / R_SUPV_DIV2 的 dnp=必装 且 value=0Ω 跳线; U_SUPV 三行 dnp=DNP",
      "action": "落表批次把 R_SUPV_DIV1/2 一并置 DNP (随 U_SUPV) ⇒ 零成本; 不许在板侧硬改",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不增 (现状 18 条)",
      "step": "S2",
      "blocked_by": "落表批次 (V-3 归老板 A1)",
      "evidence": "[实测]"
    },
    {
      "id": "B05_U_EN_SW_VALUE",
      "source_iss": "ISS-269",
      "title": "板封装 U_EN_SW 的 Value 属性陈旧 (B-2)",
      "current_state": "[实测] 板封装 Value = 'EN 输入 (高=放行底板)' (脚功能串, 不是器件身份)",
      "action": "生成器侧 B-2 已修 (ISS-269) ⇒ 重出板自动刷成含 TPS22991RAA 的器件身份",
      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([f.GetValue() for f in b.GetFootprints() if f.GetReference()=='U_EN_SW'])\" ⇒ 值含 TPS22991RAA",
      "step": "S3",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B06_TPS7A20_VALUE",
      "source_iss": "ISS-239",
      "title": "7 颗 TPS7A20 的板封装 Value 同为脚功能串 (与 B05 同根因)",
      "current_state": "[实测] 板上 7 颗 LDO 的 Value = 'EN (pin3)' / 'GND (pin2)' ⇒ 贴片程序里没有 TPS7A20-33 这个料号",
      "action": "同 B05 一批刷 (生成器本体行优先 ⇒ 板上 22 个封装 Value 一并刷新)",
      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([f.GetValue() for f in b.GetFootprints() if f.GetReference().startswith('U_LDO_')])\" ⇒ 7 颗都含 TPS7A20",
      "step": "S3",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B07_ESD_USB_D_3PIN",
      "source_iss": "ISS-266",
      "title": "D_ESD_USB_D 从 2 脚换 3 脚封装 (B-3)",
      "current_state": "[实测] 板上是 2 脚占位 (pad1 / pad2)",
      "action": "落点 = state/gen_pcb_components.py 封装表 + state/gen_pcb_netlist_board.py 的 make_footprint 分派 ⇒ pad1=D+ / pad2=D− / pad3=GND",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R4: D_ESD_USB_D 焊盘数 = 3",
      "step": "S4",
      "blocked_by": "W-1/W-2 (老板: 一颗双通道 vs 两颗单通道)",
      "evidence": "[实测]"
    },
    {
      "id": "B08_ESD_USB_D_NEAR",
      "source_iss": "ISS-266",
      "title": "D_ESD_USB_D 距 J_USB_C 47.99 mm (B-4)",
      "current_state": "[实测] D_ESD_USB_D @ (94.95, 21.8) · J_USB_C @ (140.00, 5.25) ⇒ 中心距 47.99 mm (要求 ≤ 3.0 mm)",
      "action": "用 PCB_PART_POS 钉位到 J_USB_C 旁 ≤ 3.0 mm (不许手改板坐标)",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R9: D_ESD_USB_D ↔ J_USB_C 中心距 ≤ 3.0 mm",
      "step": "S4",
      "blocked_by": "W-1/W-2 (老板)",
      "evidence": "[实测]"
    },
    {
      "id": "B09_ESD_USB_D_MINUS",
      "source_iss": "ISS-266",
      "title": "USB D− 那条路没有 ESD (B-5)",
      "current_state": "[实测] 板上挂 USB_D_N_SRC / NET_USB_D_N_TYPEC 的 ESD 位号数 = 0",
      "action": "B-3 做完自然满足 (换 3 脚后同时挂 D−); 或新增位号 D_ESD_USB_N (落表侧另派)",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R4: D− 两张网的 ESD 位号数 ≥ 1",
      "step": "S4",
      "blocked_by": "落表侧另派 (B-5 两条路都要改网表)",
      "evidence": "[实测]"
    },
    {
      "id": "B10_Q_AND_LAND",
      "source_iss": "ISS-244",
      "title": "Q_AND 占位 land 的 pad↔pin 与器件引脚序对不上 (硬件 AND 门不成立)",
      "current_state": "[实测] 板: pad1=RESET_N(D) / pad2=GND(S) / pad3=PG_AND(G) = D/S/G; AO3400A 引脚序 = 1=G / 2=S / 3=D ⇒ 装上去 = 栅极接 RESET_N、漏极接 PG_AND",
      "action": "land 目标 = pad1=PG_AND(G) / pad2=GND(S) / pad3=RESET_N(D) (两个外侧 pad 对调) ⇒ 改 make_footprint 的 pin↔net 映射",
      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_AND'][0].Pads()])\" ⇒ pad1 挂 PG_AND / pad3 挂 RESET_N",
      "step": "S6",
      "blocked_by": "落表批次 (AO3400A 已落)",
      "evidence": "[实测]+[官网]"
    },
    {
      "id": "B11_Q_PG_LAND",
      "source_iss": "ISS-244",
      "title": "Q_PG 占位 land 序错 + 网表 note 角色与拓扑相反 (开不了机)",
      "current_state": "[实测] 板: pad1=PWR_ON(S) / pad2=BAT_SW(D) / pad3=PWR_GOOD(G) = S/D/G; DMP3098L 引脚序 = 1=G / 2=S / 3=D; 网表 note 首句写 S=ON / D=BAT_SW ⇒ Vgs=0 不导通, PG 高时 Vgs=+3.3V 反偏 ⇒ 开机路径彻底不通",
      "action": "land 目标 = pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D) (两个外侧 pad 对调) + 网表 note 角色同批改成写法A (S=BAT_SW / D=ON / G=PG)",
      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])\" ⇒ pad1 挂 PWR_GOOD / pad3 挂 PWR_ON",
      "step": "S6",
      "blocked_by": "PM/老板拍写法A (ISS-244 G-1) + 落表批次改 note",
      "evidence": "[实测]+[官网]"
    },
    {
      "id": "B12_Q_ENVC_LAND",
      "source_iss": "ISS-241",
      "title": "Q_ENVC 占位 land 序 (天然对上, 但必须核一遍)",
      "current_state": "[实测] 板: pad1=PG_AND(G) / pad2=GND(S) / pad3=EN_VCORE(D) = G/S/D ⇒ 与 SOT-23 库序一致 (三件 MOS 里唯一天然对上的)",
      "action": "核一遍 pad↔pin; 若落 AO3400A 则不用改 ⇒ 但不许跳过核 (换料就翻)",
      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_ENVC'][0].Pads()])\" ⇒ pad1=PG_AND / pad2=GND / pad3=EN_VCORE",
      "step": "S6",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B13_ESD_CAM_PAD",
      "source_iss": "ISS-244",
      "title": "D_ESD_CAM 的 pad 序与单向件相反 (ESD 不工作 + CSI 负摆幅被钳到地)",
      "current_state": "[实测] 板: pad1=GND / pad2=CSI_D0_CK_P; TPD1E05U06DPYR pin1=I/O / pin2=GND ⇒ 正好相反 (另两件 ESD 是 pad1=信号/pad2=GND)",
      "action": "两个 pad 对调 ⇒ pad1=CSI_D0_CK_P(I/O) / pad2=GND",
      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='D_ESD_CAM'][0].Pads()])\" ⇒ pad1 挂 CSI_D0_CK_P",
      "step": "S6",
      "blocked_by": "-",
      "evidence": "[实测]+[官网]"
    },
    {
      "id": "B14_S6_20_COORDS",
      "source_iss": "ISS-274",
      "title": "S6 的 20 个坐标固化钉位 (原文「21 个」是重复计数)",
      "current_state": "[实测] 20 个 distinct 坐标 (10×R_SEL_* + 10×TP_DSI_*); 其中 19 个现值已等于目标 (固化钉位), 真实位移只有 R_SEL_D3_P 一处 (78.90, 9.50 → 122.30, 5.50)",
      "action": "显式钉 20 个 (不是 21 个) ⇒ 写进 PCB_PART_POS 串",
      "criterion": "python3 HW/check_board_frame_caliber.py ⇒ rc=0 (帧 id B160x100 · 20 个坐标逐个一致 ±0.01 mm)",
      "step": "S6",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B15_SVC_PORT_SPLIT",
      "source_iss": "ISS-276",
      "title": "检修口/调试口开口必须拆成两个独立窗口 (合并不可行)",
      "current_state": "[实测] 合并窗口跨 J_UART 罩 X 17.620..20.160 与 J_DEBUG 罩 X 142.063..143.838 ⇒ 并集宽 126.218 mm 装不下; 座体真实高度 [0数据]",
      "action": "拆调试口罩 (J_DEBUG) 与 UART 罩 (J_UART) 两个窗口, 坐标按现役帧 B160x100 (★不得用 ISS-271 的 F30A 帧数 ★)",
      "criterion": "python3 MECH/board_port_opening_s6_check.py ⇒ rc=0 (★属 MECH 域, 本单只登记不跑改 ★)",
      "step": "S6",
      "blocked_by": "P7 (老板) + MECH 侧 [0数据] 座体高度",
      "evidence": "[实测]+[0数据]"
    },
    {
      "id": "B16_LED_G_OPTO",
      "source_iss": "ISS-276",
      "title": "D_LED_G 落位与 R_LED_G 分居板两端 (LED_G_D 走线 93.49 mm 横跨全板)",
      "current_state": "[实测] 排版器按「功能排」落位 ⇒ D_LED_G 进 Y=56.80 的 LED 行 · R_LED_G 进 X=5.90 的 I2C 上拉列 ⇒ LED_G_D 走线 93.49 mm; 光孔 [0数据]",
      "action": "归一到现役帧的 LED 落位带 (ISS-276 §5 已给两个窗口, 压 SoM 焊盘全 = 0)",
      "criterion": "python3 MECH/board_port_opening_s6_check.py ⇒ rc=0",
      "step": "S6",
      "blocked_by": "MECH [0数据] 光孔 + P7",
      "evidence": "[实测]+[0数据]"
    },
    {
      "id": "B17_DNP_43",
      "source_iss": "ISS-269",
      "title": "43 颗 DNP 位号在板上零标记 (R3 的 F3)",
      "current_state": "[实测] R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗 (★2026-11-17 09:58:16 落表 V-3=E 删了 3 行 DNP ⇒ 54/43/43 → 51/40/40, ★本条 3 个数全部随落表变, 变的是颗数不是性质★)",
      "action": "生成器侧 X-4 已修 (ISS-269) ⇒ 重出板自动打 exclude_from_bom / exclude_from_pos_files / dnp 三件套",
      "criterion": "python3 HW/check_netlist_contradiction_r3.py ⇒ R3-A4 零标记 = 0 颗 (⇒ findings 只剩 F2)",
      "step": "S7",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B18_J_CHG_DISAMB",
      "source_iss": "ISS-247",
      "title": "J_CHG 位号双义 + 板侧封装块不可装配 (R3 的 F2)",
      "current_state": "[实测] R3-A3 命中 1 ⇒ F2 在; 板上 J_CHG 是 2 脚封装, 而实物是框侧座 + 脚侧座一对 (位号双义)",
      "action": "位号消歧 (J_CHG_A / J_CHG_B) ⇒ 落表批次 + 板侧重出",
      "criterion": "python3 HW/check_netlist_contradiction_r3.py ⇒ findings 只剩 F3 (随 B17 一起转绿)",
      "step": "S7",
      "blocked_by": "落表批次",
      "evidence": "[实测]"
    },
    {
      "id": "B19_BAT_DET",
      "source_iss": "ISS-266",
      "title": "R_BAT_DET_1/2 的封装与阻值 (B-8, 条件步)",
      "current_state": "[实测] 现值 1M ±1% @ (102.9, 17.5) / (107.7, 17.5); 分压链未落表 (V-3 归老板 A1)",
      "action": "阻值 1M±1% → 100k / 60k 且封装随之改 ⇒ 只在 A1 拍板后才动",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R8 消失 (现状: R8 在)",
      "step": "S5",
      "blocked_by": "落表批次 (阻值归老板 A1)",
      "evidence": "[实测]"
    },
    {
      "id": "B20_LAND_8ROWS",
      "source_iss": "ISS-244",
      "title": "8 行落表残项的 land 必须同批重画",
      "current_state": "[实测] 落表残项 8 行: D_CHG_LED / D_LED_G / D_LED_R / SW_BOOT / SW_KEY_PWR / SW_KEY_VM / SW_KEY_VP / SW_RST ⇒ 其中 4 键 + 2 LED 的 land 必须同批重画",
      "action": "落表批次落这 8 行 ⇒ 同批重画 land (★不许先改板后落表 ★)",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不增 (现状 18 条)",
      "step": "S10",
      "blocked_by": "落表批次",
      "evidence": "[实测]"
    },
    {
      "id": "B21_C_REGN_4U7",
      "source_iss": "ISS-241",
      "title": "C_REGN 判据错: BOM 写 1µF, TI 手册 pin22 要求 4.7µF / 10V",
      "current_state": "[实测] BOM value = 1µF; TI BQ25896 pin22 REGN 明写 Connect a 4.7 uF (10 V rating) ceramic capacitor",
      "action": "落表批次改 BOM value ⇒ 板侧位置必须贴 U_CHG pin22",
      "criterion": "python3 HW/check_part_selection_matrix.py ⇒ rc=0 (8/8)",
      "step": "S10",
      "blocked_by": "落表批次",
      "evidence": "[官网]+[实测]"
    },
    {
      "id": "B22_CHG_BOARD_FP",
      "source_iss": "ISS-241",
      "title": "6 件充电板器件的 footprint 待定 (不在本板, 但会顶到本板那一趟)",
      "current_state": "[实测] D_ESD_TC / FB_VBUS / D_TVS_VBUS / Q_CHG_LED / D_CHG_LED / C_REGN 六件 footprint = 待定 (板文件里查无此位号)",
      "action": "充电板那一趟定 footprint (C_REGN 位置必须贴 U_CHG pin22) ⇒ 本板不受影响, 但不许与本板那一趟抢同一批落表窗口",
      "criterion": "python3 HW/check_step1_parts_spec.py ⇒ rc=0",
      "step": "S10",
      "blocked_by": "充电板那一趟 (不在本板)",
      "evidence": "[实测]"
    },
    {
      "id": "B23_ESD_TC_4PAD",
      "source_iss": "ISS-244",
      "title": "D_ESD_TC 落了 3 通道件却只接 1 通道 ⇒ Type-C 的 D+/D− 仍裸奔",
      "current_state": "[实测] D_ESD_TC = SP0503BAHT (3 通道) 而网表只接 USB_VBUS_RAW + GND ⇒ 另 2 通道闲置",
      "action": "充电板 footprint 给 4 焊盘 + 决定是否覆盖 D+/D−",
      "criterion": "python3 HW/check_part_selection_matrix.py ⇒ rc=0",
      "step": "S10",
      "blocked_by": "老板 (ESD 架构: 单通道 vs 双通道)",
      "evidence": "[实测]"
    },
    {
      "id": "B24_Q_PG_PART",
      "source_iss": "ISS-241",
      "title": "Q_PG 选漏电档还是栅压耐压档 (影响落料, 不影响 land 目标)",
      "current_state": "[实测] 候选 DMP3098L (IDSS ≤800 nA, VGS 绝对最大手册未见 [0数据]) vs AO3407A (VGS ±20 V 明写, 高温 IDSS ≤5 µA 差 6 倍)",
      "action": "一票交 main/PM; 两颗引脚序都是 1=G / 2=S / 3=D ⇒ 与 B11 的 land 目标一致, 不因选型变化",
      "criterion": "python3 HW/check_part_selection_matrix.py ⇒ rc=0",
      "step": "S10",
      "blocked_by": "main/PM (ISS-241 Q-C)",
      "evidence": "[官网]+[0数据]"
    },
    {
      "id": "B25_UNCONNECTED",
      "source_iss": "ISS-266",
      "title": "unconnected 归零 (45 → 0)",
      "current_state": "[实测] unconnected items = 45 · DRC 违规 = 0 (骨架阶段允许未布线)",
      "action": "布线归零 (S8); 死因见 ISS-265 §6 (A1 / W-1 / W-2 / W-4 / D_LED_G 位置 / FSIN_OUT)",
      "criterion": "python3 state/check_pcb_drc.py ⇒ unconnected items = 0 · DRC 违规 = 0",
      "step": "S8",
      "blocked_by": "W-1/W-2/W-4 + A1",
      "evidence": "[实测]"
    },
    {
      "id": "B26_BASELINE",
      "source_iss": "ISS-266",
      "title": "换基线 (旧 md5 → 新 md5)",
      "current_state": "[实测] 现行基线: 板 611b869e… / .kicad_pro 3e504d2b… / 网表 e06c1dd6… / 脚表 287e7861… / BOM 94642d07…",
      "action": "那一趟跑完后把五件新 md5 写进作业包 §5 基线表 (追加式, 老行不删)",
      "criterion": "md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv ⇒ 与新基线逐条一致",
      "step": "S9",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "B27_CHAINGATE",
      "source_iss": "ISS-266",
      "title": "投产包准入闸 chain_gate 转绿",
      "current_state": "[实测] chain_gate rc=1 (③ PCB 准入红「板与网表不等价」 + ⑤ 投产资料包红)",
      "action": "S1~S10 全跑完后重跑 chain_gate ⇒ 五个环节全绿",
      "criterion": "python3 state/chain_gate.py ⇒ rc=0",
      "step": "S11",
      "blocked_by": "S1~S10",
      "evidence": "[实测]"
    },
    {
      "id": "B28_RELEASE",
      "source_iss": "ISS-266",
      "title": "留证链 + 盖章 + 发布闸",
      "current_state": "[实测] Gerber 32 个齐 (C6 通过); 留证链与盖章闸属 S12",
      "action": "重出 Gerber / 钻孔 / CPL / 装配 / 3D / D356 + 留证链 + 盖章 + 发布闸",
      "criterion": "python3 state/check_pcb_drc.py ⇒ C6 生产文件齐 · rc=0",
      "step": "S12",
      "blocked_by": "S10",
      "evidence": "[实测]"
    },
    {
      "id": "B29_WRITEBACK",
      "source_iss": "ISS-266",
      "title": "回写台账 + 决策页 + 分片",
      "current_state": "[实测] 落表台账 / 决策页 / 分片 三处待回写 (★板级结论必须落决策页 ★)",
      "action": "把新 md5 四字段写进落表台账 + 决策页记板级结论 + 分片登记",
      "criterion": "python3 state/merge.py ⇒ rc=0 && python3 state/gate_check.py ⇒ rc=0 (Q1 18/18)",
      "step": "S13",
      "blocked_by": "S9~S12",
      "evidence": "[实测]"
    },
    {
      "id": "B30_LED_BRIGHTNESS",
      "source_iss": "ISS-271",
      "title": "LED 亮度档 G-5 未拍 (改串阻 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位)",
      "current_state": "[实测] 1kΩ + 3.3V ⇒ 1.10 mA ⇒ KP-2012SGC 仅 0.7~0.9 mcd ⇒ 白天看不见",
      "action": "拍 G-5 亮度档 ⇒ 必须排在 S6 之前 (排在后面 = 板要改第二次)",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不变 (档位落表在落表批次)",
      "step": "S6",
      "blocked_by": "老板 (G-5 亮度档)",
      "evidence": "[实测]"
    },
    {
      "id": "B31_P7_TARGET",
      "source_iss": "ISS-266",
      "title": "P7: 画哪一块板 (160×100 台架板 vs 产品板)",
      "current_state": "[实测] 现役板 = 160×100 台架板 (8 铜层 / 186 封装 / 160.10×100.10); 产品板 = 60×30 套A (★另一坐标帧 F30A, 数不可混用 ★)",
      "action": "只列选项与代价, 不代拍 (★C4 是唯一不需动板的选项 ★)",
      "criterion": "python3 HW/check_board_frame_caliber.py ⇒ rc=0 (三条帧 id B160x100 / F30A / P60x15 互不混用)",
      "step": "S6",
      "blocked_by": "老板 (P7)",
      "evidence": "[实测]"
    }
  ]
}
```

---

★**★本表的每个数字都是本机实读 (★`bash state/pcbnew_py.sh` 读板 / 各闸原始输出 / 来源交卷单原文 ★), 没有一条是估的★★** ★
★**★本页由 `state/_iss277_build_preflight.py` 生成 (★页与 JSON 同源 ⇒ 不会写岔 ★)★** ★
