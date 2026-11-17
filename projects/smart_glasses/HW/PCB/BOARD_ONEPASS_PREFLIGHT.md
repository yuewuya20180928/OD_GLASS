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
| ★**`B32_V2_NET_RENAME`** ★ | ★ISS-283 ★ | V-2 网改名 (D_ESD_USB_D pad1: `USB_D_P_SRC` → `NET_USB_D_P_TYPEC`) ⇒ 板面 3 处焊盘网名必须同趟改 (★§③-1★) | ★**S4** ★ | ★**板只改一次那一趟 (★本单零写板★)** ★ | [实测] 网表 L417 已落 `NET_USB_D_P_TYPEC` (★台账 §16.2 链头 L1353 · ISS-283 · 12:16:08★); 板面仍挂旧网名 `USB_D_P_SRC` 的焊盘 **3 处**: `D_ESD_USB_D.pad1` / `R_SER_USB_D_P` 一端 / `J_SOM_P1` 的 USB_D_P 脚 ⇒ 网表与板对不上 | `python3 HW/check_board_frame_caliber.py` ⇒ C6 绿 (★盘上 md5 == 落表台账登记★) |
| ★**`B10_Q_AND_LAND`** ★ | ★ISS-244 ★ | Q_AND 占位 land 的 pad↔pin 与器件引脚序对不上 (硬件 AND 门不成立) | ★**S6** ★ | 落表批次 (AO3400A 已落) | [实测] 板: pad1=RESET_N(D) / pad2=GND(S) / pad3=PG_AND(G) = D/S/G; AO3400A 引脚序 = 1=G / 2=S / 3=D ⇒ 装上去 = 栅极接 RESET_N、漏极接 PG_AND | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_AND'][0].Pads()])" ⇒ pad1 挂 PG_AND / pad3 挂 RESET_N` |
| ★**`B11_Q_PG_LAND`** ★ | ★ISS-244 ★ | Q_PG 占位 land 序错 (开不了机) ★**★网表 note 已落写法A (★ISS-283·12:30:23★) ⇒ 只剩板那一趟重画 land (§③-2)★** ★ | ★**S6** ★ | ★**写法A 已拍 (★老板 2026-11-17 09:49★) + 网表 note 已落表 (★台账 §16.2 链头 L1353·12:30:23★) ⇒ 只剩板那一趟重画这 3 根线** ★ | [实测] 板: pad1=PWR_ON(S) / pad2=BAT_SW(D) / pad3=PWR_GOOD(G) = S/D/G; DMP3098L 引脚序 = 1=G / 2=S / 3=D ⇒ 板上 land 仍是旧接法 ⇒ 写法B ⇒ Vgs=0 不导通, PG 高时 Vgs=+3.3V 反偏 ⇒ 开机路径彻底不通; ★**网表 note 已落写法A: pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D) ⇒ 板面与网表对不上** ★ | `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])" ⇒ pad1 挂 PWR_GOOD / pad3 挂 PWR_ON` |
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
| ★**`B30_LED_BRIGHTNESS`** ★ | ★ISS-271 ★ | LED 亮度档 G-5 **已拍 = 20mA 档** (R_LED_R 68Ω / R_LED_G 55Ω) ★**★已落表 (★ISS-283·12:30:23★) ⇒ 板那一趟只须重出 BOM (footprint 不变 ⇒ 不构成额外板改)★** ★ | ★**S6** ★ | ★**已拍 (★老板 2026-11-17 09:49·A5 = 20mA★) ⇒ 剩【IEC 62471 分级重算】登记给 main (★不代拍★)** ★ | [实测] G-5 已拍「选项 ② = 改 R 到 20 mA 档」⇒ 已落表: R_LED_R = 68Ω ±1% / R_LED_G = 55Ω ±1% ⇒ 单颗 ~20 mA · 功耗 2.2 mW→66 mW (★两颗 ≈ 0.13 W 进电池账★) · 亮度 ×14 ⇒ IEC 62471 分级要重算 (★已登记 need·不代拍★); ★旧 1kΩ + 3.3V ⇒ 1.10 mA ⇒ KP-2012SGC 仅 0.7~0.9 mcd ⇒ 白天看不见 (★已被 20 mA 档取代★) ★ | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不变 (★20mA 档已落表; 板侧项归 §③-1~§③-3★)` |
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
| ★**ISS-283** (hw-lead 2026-11-17 12:16~12:30 真落表后) ★ | ★**V-2 网改名 (A3) + W-4 写法A (A4) + G-5 20mA 档 (A5) 三次落表 ⇒ 板那一趟必须同趟吃掉 3 条板侧同步项 (★见下面 §3-追加 三条★)** ★ | ★`B32_V2_NET_RENAME` (§③-1) · `B11_Q_PG_LAND` (§③-2) · `B07_ESD_USB_D_3PIN` / `B08_ESD_USB_D_NEAR` / `B09_ESD_USB_D_MINUS` (§③-3) · `B30_LED_BRIGHTNESS` (G-5 已落) ★ | ★**本页补入 (追加式) · 板那一趟清掉** ★ |

### ★★§3-追加 · ★★ISS-283 落表带来的板侧同步项 (★3 条 · 追加式 · 上面每一行老字一字未删★) ★★

★**背景 (★main 13:1x 本机实读盘面 + 实跑闸·★不是推测★)**: ★**ISS-283 在 2026-11-17 12:16:08 (A3 / V-2=1) 与 12:30:23 (A4 / W-4 写法A + A5 / G-5 20mA 档) 两次真落表** ★
⇒ ★**网表 / 脚表 / BOM 三件已变 (板一个字节没变)** ⇒ ★**板那一趟 (「板只改一次」那一趟) 必须同趟吃掉下面 3 条, 否则网表与板对不上** ★
★**三条的编号 = 网表 note 里引用的「ISS-283 板侧清单 §③-N」** ★

| 编号 | 板侧项 | 来源 | 落表事实 (★台账出处★) | 板那一趟要做的事 | 判据 (★真命令★) |
|---|---|---|---|---|---|
| ★**§③-1** ★ | ★**V-2 网改名: `D_ESD_USB_D` pad1 网名 `USB_D_P_SRC` → `NET_USB_D_P_TYPEC`** ★ | ★**ISS-283 · A3 (V-2=1)** ★ | ★**网表 L417 的 net 已落 `NET_USB_D_P_TYPEC`** (★台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 · 链头 L1353 · ISS-283 · 12:16:08★) ⇒ ★**板面 3 处焊盘网名还挂旧的 `USB_D_P_SRC`** (★`D_ESD_USB_D.pad1` / `R_SER_USB_D_P` 一端 / `J_SOM_P1` 的 USB_D_P 脚★) ★ | ★**这 3 处焊盘网名同趟改成 `NET_USB_D_P_TYPEC`** (★不改 ⇒ 网表与板对不上★) ⇒ ★**对应条目 = `B32_V2_NET_RENAME`** ★ | ★`python3 HW/check_board_frame_caliber.py` ⇒ ★**C6 绿** (★盘上 md5 == 落表台账登记★) ★ |
| ★**§③-2** ★ | ★**`Q_PG` land 重画 (pad1 ↔ pad3 的网互换)** ★ | ★**ISS-283 · A4 (W-4 写法A)** ★ | ★**网表已落: pad1 = `PWR_GOOD` (G) / pad2 = `BAT_SW` (S) / pad3 = `PWR_ON` (D)** (★台账 §16.2 · 链头 L1353 · ISS-283 · 12:30:23★) ⇒ ★**DMP3098L 引脚序 = 1=G / 2=S / 3=D ⇒ 板上 land 仍是旧接法 (pad1=`PWR_ON` / pad3=`PWR_GOOD`) ⇒ 这 3 根线必须重画** ★ | ★**重画 `Q_PG` 的 3 根线** (★pad1→`PWR_GOOD` / pad2→`BAT_SW` / pad3→`PWR_ON`★) ⇒ ★**对应条目 = `B11_Q_PG_LAND`** ★ | ★`bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])"` ⇒ ★**pad1 挂 `PWR_GOOD` / pad3 挂 `PWR_ON`** ★ |
| ★**§③-3** ★ | ★**D− 侧 ESD 三件仍挂着 (R4×2 + R9)** ★ | ★**ISS-266 (板侧) · ISS-283 (登记)** ★ | ★**落表侧已落, 板侧未清**: ① `D_ESD_USB_D` 板上仍是 **2 焊盘** ② D− 网 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 上 **ESD 位号数 = 0** ③ `D_ESD_USB_D` → `J_USB_C` 板面距离 **47.99 mm** > 3.0 mm 判据 ⇒ ★**这 4 条是 G1a-4 的最后 4 条未落表项 (板侧)** ★ | ★**板那一趟清掉这 4 条** ⇒ ★**对应条目 = `B07_ESD_USB_D_3PIN` / `B08_ESD_USB_D_NEAR` / `B09_ESD_USB_D_MINUS`** ★ | ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★**R4 / R9 转绿** ★ |

★**★铁律 (★本单口径·★零写板★)**: ★**这 3 条本单【一条都不许在盘上做】** ★ ⇒ ★**板 `611b869e…` 与 `.kicad_pro 3e504d2b…` 逐字节不变** ★ ⇒ ★**Gerber / 投产包一律不许用 (★板现在仍是「旧网表的板」★)** ★ ⇒ ★**板改 = 「板只改一次」那一趟, 由 main 统一开** ★
★**★登记 (★只登记 · 不代拍★)**: ★**G-5 亮度档 ⇒ 亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级要重算 ⇒ 登记成 need 给 main (★hw-lead 不代拍★)** ★

---

## §4 · 归属步分布表 (★S1~S13 每步至少一条, 不许有步没人管 ★)

| 步 | 条数 | 条目 |
|---|---|---|
| ★**S1** ★ | ★1 ★ | ★`B01_REF_SUFFIX` ★ |
| ★**S2** ★ | ★3 ★ | ★`B02_C_VBUS_GND`, `B03_ULDO_S28_PAD3`, `B04_R_SUPV_DIV_DNP` ★ |
| ★**S3** ★ | ★2 ★ | ★`B05_U_EN_SW_VALUE`, `B06_TPS7A20_VALUE` ★ |
| ★**S4** ★ | ★4 ★ | ★`B07_ESD_USB_D_3PIN`, `B08_ESD_USB_D_NEAR`, `B09_ESD_USB_D_MINUS`, `B32_V2_NET_RENAME` ★ |
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
      "id": "B32_V2_NET_RENAME",
      "source_iss": "ISS-283",
      "title": "V-2 网改名: D_ESD_USB_D pad1 网名 USB_D_P_SRC → NET_USB_D_P_TYPEC ⇒ 板面 3 处焊盘网名必须同趟改 (★§③-1★)",
      "current_state": "[实测] 网表 L417 已落 NET_USB_D_P_TYPEC (★台账 §16.2 链头 L1353 · ISS-283 · 12:16:08★); 板面仍挂旧网名 USB_D_P_SRC 的焊盘 3 处: D_ESD_USB_D.pad1 / R_SER_USB_D_P 一端 / J_SOM_P1 的 USB_D_P 脚 ⇒ 网表与板对不上",
      "action": "板那一趟把这 3 处焊盘网名同趟改成 NET_USB_D_P_TYPEC (★不改 ⇒ 网表与板对不上★) ⇒ 见板侧清单 §③-1; ★本单零写板★",
      "criterion": "python3 HW/check_board_frame_caliber.py ⇒ C6 绿 (★盘上 md5 == 落表台账登记★)",
      "step": "S4",
      "blocked_by": "板只改一次那一趟 (★本单零写板★)",
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
      "title": "Q_PG 占位 land 序错 (开不了机) ★**网表 note 已落写法A (★ISS-283·12:30:23★) ⇒ 只剩板那一趟重画 land (★§③-2★)**★",
      "current_state": "[实测] 板: pad1=PWR_ON(S) / pad2=BAT_SW(D) / pad3=PWR_GOOD(G) = S/D/G; DMP3098L 引脚序 = 1=G / 2=S / 3=D ⇒ 板上 land 仍是旧接法 ⇒ 写法B ⇒ Vgs=0 不导通, PG 高时 Vgs=+3.3V 反偏 ⇒ 开机路径彻底不通; ★**网表 note 已落写法A: pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D) (★台账 §16.2 链头 L1353 · ISS-283 · 12:30:23★) ⇒ 板面与网表对不上**★",
      "action": "板那一趟重画 Q_PG 的 3 根线 (★pad1→PWR_GOOD(G) / pad2→BAT_SW(S) / pad3→PWR_ON(D)★) + 网表 note 角色已于 2026-11-17 12:30:23 同批落成写法A (★S=BAT_SW / D=ON / G=PG★)",
      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])\" ⇒ pad1 挂 PWR_GOOD / pad3 挂 PWR_ON",
      "step": "S6",
      "blocked_by": "★**写法A 已拍 (★老板 2026-11-17 09:49★) + 网表 note 已落表 (★台账 §16.2 链头 L1353·12:30:23★) ⇒ 只剩板那一趟重画这 3 根线**★",
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
      "title": "LED 亮度档 G-5 **已拍 = 20mA 档** (R_LED_R 68Ω / R_LED_G 55Ω) ★**已落表 (★ISS-283·12:30:23★) ⇒ 板那一趟只须重出 BOM (footprint 不变 ⇒ 不构成额外板改)**★",
      "current_state": "[实测] G-5 已拍「选项 ② = 改 R 到 20 mA 档」⇒ 已落表: R_LED_R = 68Ω ±1% / R_LED_G = 55Ω ±1% ⇒ 单颗 ~20 mA · 功耗 2.2 mW→66 mW (★两颗 ≈ 0.13 W 进电池账★) · 亮度 ×14 ⇒ IEC 62471 分级要重算 (★已登记 need·不代拍★); ★旧 1kΩ + 3.3V ⇒ 1.10 mA ⇒ KP-2012SGC 仅 0.7~0.9 mcd ⇒ 白天看不见 (★已被 20 mA 档取代★)★",
      "action": "落表已完成 (★R 值写进 BOM ⇒ 台账 §16.2 链头 L1353★) ⇒ 板那一趟只须重出 BOM + 投产包 (★footprint 不变 ⇒ 不构成额外板改★) ⇒ 另: IEC 62471 分级重算登记给 main (★不代拍★)",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不变 (★20mA 档已落表; 板侧项归 §③-1~§③-3★)",
      "step": "S6",
      "blocked_by": "★**已拍 (★老板 2026-11-17 09:49·A5 = 20mA★) ⇒ 剩【IEC 62471 分级重算】登记给 main (★不代拍★)**★",
      "evidence": "[实测]+[官网]"
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

---

## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)

> ★**本附录 = 追加式 (★本页上面每一行老字一字未删 ★)** ★
> ★**本页的 items JSON 里那两句已过期的现状值 (★`B01_REF_SUFFIX` 的「零后缀」/ `B26_BASELINE` 的 `e06c1dd6…`★) 按追加式纪律原样留着, 订正写在这里** ★
> ★**机器闸**: `python3 HW/check_workpack_state_values.py` (★V1~V7★) ⇒ ★**「本页 + 作业包里的现状值 == 盘面实测」当场判红 ★** ★

| # | 本页条目 / 位置 | 老字 (★原样保留, 一字未删 ★) | ★**现行值 (★盘面实测★)** ★ |
|---|---|---|---|
| ① | ★**`B17_DNP_43`** ★ | ★**`B17_DNP_43`** ★ | ★**条目 id `B17_DNP_43` 保留 (★老字留痕 · 闸的探针键也用它 ★) ⇒ 现行值 = 40** ★ ⇒ ★**该条的 `current_state` 已是 `MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗` (★落表后已更新★); 本次只补「id 名字里的 43 是历史留痕, 不是现值」这句注解** ★ |
| ② | ★**`B01_REF_SUFFIX`** ★ | `[实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号` | ★**板文件 186 个封装位号里 30 个末字符是数字 (含 1 个已带 `_1` 的 `R_BAT_DET_1`) ⇒ 真正要加 `_1` 的是 156 个** ★ ⇒ ★**「零后缀」那句不成立 (★ISS-287 ②★); 186 是【原理图侧】口径 (★218 − 32★), 板侧是 156** ★ |
| ③ | ★**`B31_P7_TARGET`** · ★**§1 帧声明** ★ | `186 封装` | ★**186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)** ★ ⇒ ★**官方板 186 / 沙盒生成板 185 ⇒ 差 1 = `C_VBUS_GND` (★网表 board 列 = CHG_BOARD·DNP, 但官方板上有实物封装@107.70,42.50★) ⇒ ★★动板那一趟按【官方板的数】走: 开工前 186 / 收工后 185★★ ★** |
| ④ | ★**`B26_BASELINE`** ★ | `网表 e06c1dd6…` | ★**落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07** ★ (★脚表 `a4270120454aedf7a23c92cd8985c8a6` / BOM `5d02bece9477ffce5fbe0193c7d5cce4`·★ISS-283 · 台账 L1353·§16.2★) ⇒ ★**基线走落表台账为准, 不写死** ★ |
| ⑤ | ★**铜层 / 板框四数** ★ | `8 铜层 · 160.10×100.10` | ★**8 铜层 · 160.10×100.10** ★ (★现状=现役帧 B160x100★) |
| ⑥ | ★**`B03_ULDO_S28_PAD3`** (脚表缺陷条数) ★ | ★`脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账` ★ | ★**脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账** ★ (★现状 = 18 · 本闸钉住★) |

★**★本附录的现状值登记表 (★与作业包 §8.2.5 逐字相同★)** ★

```json
{
  "schema": "board-onepass-state-baseline/v1",
  "generated_by": "ISS-289 hw-lead (2026-11-17)",
  "note": "★期望值写在文档里 (不写死在闸里) ⇒ 文档漂了当场红; md5 基线的取值来源 = 落表台账 (HW/landing_md5.py)★",
  "state_baseline": {
    "entries": [
      {
        "id": "W01_S7_HEADING",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "### ★S7 · DNP 标记 (★43 个位号·★生成器侧改代码★) ★",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "S7 · DNP 标记 (★40 个位号·★生成器侧改代码★)",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§3-S7 段标题的老字是 43 ⇒ 现行值 40"
      },
      {
        "id": "W02_S7_QUANT_ZERO",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★现状: **43 个全部零标记**★",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "现状: **40 个全部零标记**",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§3-S7 量化判据第一条"
      },
      {
        "id": "W03_S7_QUANT_TOKEN",
        "category": "dnp_token_count",
        "doc": "workpacket",
        "anchor": "板文件里 \"dnp\" 出现次数应从 3 涨到 3 + 43 = 46",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "板文件里 \"dnp\" 出现次数应从 3 涨到 3 + 40 = 43",
        "expect": "3",
        "probe": [
          "python3",
          "-c",
          "print(open('HW/PCB/demo_mainboard.kicad_pcb',encoding='utf-8',errors='replace').read().lower().count('dnp'))"
        ],
        "probe_regex": "^(\\d+)$",
        "note": "板文件 dnp 出现次数: 现状 3 (三个层设置) ⇒ S7 跑完 = 3 + 40 = 43"
      },
      {
        "id": "W04_S3_TABLE_S7",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★R3-A4: MAIN_PCB且DNP 54 颗 · 在板上 43 颗 · ★**零标记 43 颗** ★",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · ★**零标记 40 颗** ★",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§3 表 S7 行的三个数一起订正 (54/43/43 → 51/40/40)"
      },
      {
        "id": "W05_S4_ACCEPT_ROW",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★**R3-A4 零标记 DNP 数 = 0** ★ (★现状 43★)",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "R3-A4 零标记 DNP 数 = 0** ★ (★现状 40★)",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§4 验收表 S1~S7 行"
      },
      {
        "id": "W06_S2_X2_PIT",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "43 个 DNP 零标记不是「生成器漏刷」",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "40 个 DNP 零标记不是「生成器漏刷」",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§2 的 X-2 坑行"
      },
      {
        "id": "W14_S6_1_S7_ROW",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "DNP 标记 (43 个)",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "DNP 标记 (40 个)",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§6.1 表 S7 行 (同源第三处)"
      },
      {
        "id": "W15_S8_1_3_X4",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★**X-4 修完 ⇒ 板上有 43 个 DNP 标记**",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "X-4 修完 ⇒ 板上有 40 个 DNP 标记",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§8.1.3-3 (同源第三处)"
      },
      {
        "id": "W16_S1_1_F3",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "MAIN_PCB 且 DNP 的位号数 54 · 其中在板文件里真实存在的 43 · 零标记的 43",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "MAIN_PCB 且 DNP 的位号数 51 · 其中在板文件里真实存在的 40 · 零标记的 40",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§1.1 第 1 行 F3 (同源第三处)"
      },
      {
        "id": "W11_FOOTPRINT_COUNT",
        "category": "footprint_count",
        "doc": "workpacket",
        "anchor": "160.10×100.10 mm / 8 铜层 / 186 封装",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)",
        "expect": "186",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "封装 (\\d+)",
        "note": "官方板 186 / 生成板 185 ⇒ 差 1 = C_VBUS_GND (板级归属差, 不是漏数)"
      },
      {
        "id": "W12_S1_BOARD_156",
        "category": "ref_suffix",
        "doc": "workpacket",
        "anchor": "★**③ 板侧 186 个封装位号 = 走 S6 重出自动带** ★",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "板侧真正要加 `_1` 的是 156 个 (★官方板 186 个封装里末字符是字母的只有 156 个, 另 30 个末字符是数字不动★)",
        "expect": "156",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "-c",
          "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');rs=[f.GetReference() for f in b.GetFootprints()];print('板侧末字符是字母(要加_1) = %d' % len([r for r in rs if not r[-1].isdigit()]));print('带 _1 后缀 = %d' % len([r for r in rs if r.endswith('_1')]))"
        ],
        "probe_regex": "要加_1\\) = (\\d+)",
        "note": "§3-S1 的「板侧 186 个封装位号」会被读成「板上有 186 个要改名」⇒ 错"
      },
      {
        "id": "W18_S1_SUFFIX_ONE",
        "category": "ref_suffix",
        "doc": "workpacket",
        "anchor": "★**186 个 `X` → `X_1` (★`C_AC_CSI_D0_CK_N` → `C_AC_CSI_D0_CK_N_1`★) · ★**`RAIL_*` / `NET_*` 保留** (★单点汇流位, 改了 BOM 多假料号★) · ★**32 个本来就数字结尾的不动** ★",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "官方板带 `_1` 后缀的位号 = 1 个 (`R_BAT_DET_1`) ⇒ 改完 = 157 个",
        "expect": "1",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "-c",
          "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');rs=[f.GetReference() for f in b.GetFootprints()];print('板侧末字符是字母(要加_1) = %d' % len([r for r in rs if not r[-1].isdigit()]));print('带 _1 后缀 = %d' % len([r for r in rs if r.endswith('_1')]))"
        ],
        "probe_regex": "带 _1 后缀 = (\\d+)",
        "note": "ISS-287 ②: 官方板带 _1 后缀的位号 = 1 个"
      },
      {
        "id": "W19_S1_SCH_186",
        "category": "ref_suffix",
        "doc": "workpacket",
        "anchor": "★**① 器件位号真源 = `HW/SCHEMATIC_V1_SPEC.json`** (★`devices` 段的 186 个 `ref` ★)",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "原理图 / 网表侧要加 `_1` 的位号 = 186 个 (★218 − 32★) ⇒ 板侧是 156 个, 不是 186 个",
        "expect": "186",
        "probe": [
          "python3",
          "-c",
          "import csv;rs={r['ref'] for r in csv.DictReader(open('HW/BOM_v1.csv'))};print('BOM 位号末字符是字母 = %d' % len([r for r in rs if not r[-1].isdigit()]))"
        ],
        "probe_regex": "= (\\d+)$",
        "note": "186 是原理图侧口径 (BOM 218 − 32); 该 JSON 里没有 devices 键 ⇒ 指针失效 (已登记 need)"
      },
      {
        "id": "W13_COPPER_COUNT",
        "category": "copper_and_frame",
        "doc": "workpacket",
        "anchor": "| ★**铜层数** ★ | ★**8** ★",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "铜层数 = 8",
        "expect": "8",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "铜层 (\\d+)",
        "note": "铜层 / 板框四数之一"
      },
      {
        "id": "W13B_FRAME_BOX",
        "category": "copper_and_frame",
        "doc": "workpacket",
        "anchor": "| ★**板框 (Edge.Cuts)** ★ | ★**160.10 × 100.10 mm** ★ |",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "板框 = 160.10 × 100.10 mm",
        "expect": "160.10 × 100.10 mm",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "板框 \\(含线宽\\) = ([\\d.]+ × [\\d.]+ mm)",
        "note": "铜层 / 板框四数之二 (宽 × 高)"
      },
      {
        "id": "W13C_FRAME_ID",
        "category": "copper_and_frame",
        "doc": "workpacket",
        "anchor": "帧 id `B160x100` · 板 160.00×100.00 / 8 铜层 / 1.60mm / 186 封装",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "现役帧 = B160x100",
        "expect": "B160x100",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "现役帧 (\\S+)",
        "note": "铜层 / 板框四数之三 (现役帧 id)"
      },
      {
        "id": "W07_FINDINGS_2",
        "category": "defect_count",
        "doc": "workpacket",
        "anchor": "★**FINDINGS = 0** ★ (★现状 2 = F2+F3★)",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "FINDINGS = 0** ★ (★现状 2 = F2+F3★",
        "expect": "2",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "FINDINGS: (\\d+)",
        "note": "无漂 (仍 = 2 = F2+F3), 但登记进闸"
      },
      {
        "id": "W08_PINS_DEFECT",
        "category": "defect_count",
        "doc": "workpacket",
        "anchor": "★**15 条** (★14 串号 + 1 缺脚: `U_LDO_S28` 无 pin3★)",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "18 条 (★15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账★)",
        "expect": "18",
        "probe": [
          "python3",
          "HW/check_pin_function_labels.py"
        ],
        "probe_regex": "(\\d+) 条缺陷",
        "note": "脚表语义缺陷 15 → 18 (落表后 md5 台账对账多 3 条)"
      },
      {
        "id": "W09_SAME_PAD_NET",
        "category": "defect_count",
        "doc": "workpacket",
        "anchor": "缺失 0 · 同号异网 0",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "缺失 0 · 同号异网 3",
        "expect": "3",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "state/check_pcb_nets.py"
        ],
        "probe_regex": "同号异网 (\\d+)",
        "note": "落表已改、板还没跟 ⇒ 同号异网 0 → 3 (Q_PG pad1/pad3 + D_ESD_USB_D pad1)"
      },
      {
        "id": "W10_MD5_NETLIST",
        "category": "md5_baseline",
        "doc": "workpacket",
        "anchor": "★**`HW/netlist_v1.csv`** ★ | ★`e06c1dd633566aa44732762c2ff99d1c` ★",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07",
        "expect_mode": "ledger",
        "expect_target": "HW/netlist_v1.csv",
        "probe": [
          "md5sum",
          "HW/netlist_v1.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "网表 md5 基线 ★走落表台账为准, 不写死★ (ISS-283 ⑩-b 的口径)"
      },
      {
        "id": "W10B_MD5_PINS",
        "category": "md5_baseline",
        "doc": "workpacket",
        "anchor": "★**`HW/netlist_v1_pins.csv`** ★ | ★`287e7861a0d1007748d92d9fbecdd490` ★",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "落表台账登记 = a4270120454aedf7a23c92cd8985c8a6",
        "expect_mode": "ledger",
        "expect_target": "HW/netlist_v1_pins.csv",
        "probe": [
          "md5sum",
          "HW/netlist_v1_pins.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "脚表 md5 基线 ★走落表台账为准★"
      },
      {
        "id": "W10C_MD5_BOM",
        "category": "md5_baseline",
        "doc": "workpacket",
        "anchor": "★**`HW/BOM_v1.csv`** ★ | ★`94642d07a69e8d60dd2af57f69b93607` ★",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "落表台账登记 = 5d02bece9477ffce5fbe0193c7d5cce4",
        "expect_mode": "ledger",
        "expect_target": "HW/BOM_v1.csv",
        "probe": [
          "md5sum",
          "HW/BOM_v1.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "BOM md5 基线 ★走落表台账为准★"
      },
      {
        "id": "C01_B17_ZERO_MARK",
        "category": "dnp_zero_mark",
        "doc": "checklist",
        "anchor": "[实测] R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "清单页这条的 current_state 已是 40 (老字保留), 本闸把它钉住"
      },
      {
        "id": "C02_B17_ID_NAME",
        "category": "dnp_zero_mark",
        "doc": "checklist",
        "anchor": "★**`B17_DNP_43`** ★",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "条目 id `B17_DNP_43` 保留 (★老字留痕 · 闸的探针键也用它 ★) ⇒ 现行值 = 40",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "条目 id 名字含 43 ⇒ 改名会打断闸的探针键 ⇒ 只加注, 不改名"
      },
      {
        "id": "C03_B01_REF_SUFFIX",
        "category": "ref_suffix",
        "doc": "checklist",
        "anchor": "[实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "板文件 186 个封装位号里 30 个末字符是数字 (含 1 个已带 `_1` 的 `R_BAT_DET_1`) ⇒ 真正要加 `_1` 的是 156 个",
        "expect": "156",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "-c",
          "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');rs=[f.GetReference() for f in b.GetFootprints()];print('板侧末字符是字母(要加_1) = %d' % len([r for r in rs if not r[-1].isdigit()]));print('带 _1 后缀 = %d' % len([r for r in rs if r.endswith('_1')]))"
        ],
        "probe_regex": "要加_1\\) = (\\d+)",
        "note": "「186 个封装位号零后缀」这句不成立 (ISS-287 ②)"
      },
      {
        "id": "C04_B31_FOOTPRINT_COUNT",
        "category": "footprint_count",
        "doc": "checklist",
        "anchor": "[实测] 现役板 = 160×100 台架板 (8 铜层 / 186 封装 / 160.10×100.10)",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)",
        "expect": "186",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "封装 (\\d+)",
        "note": "官方板 186 / 生成板 185"
      },
      {
        "id": "C05_FRAME_B160X100",
        "category": "copper_and_frame",
        "doc": "checklist",
        "anchor": "★**160×100 台架板 (现役板)** · 8 铜层 · 160.10×100.10 · 186 封装 ★",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "8 铜层 · 160.10×100.10",
        "expect": "8",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "铜层 (\\d+)",
        "note": "铜层 / 板框四数"
      },
      {
        "id": "C06_B03_DEFECT_COUNT",
        "category": "defect_count",
        "doc": "checklist",
        "anchor": "脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账",
        "expect": "18",
        "probe": [
          "python3",
          "HW/check_pin_function_labels.py"
        ],
        "probe_regex": "(\\d+) 条缺陷",
        "note": "脚表缺陷条数 (清单页已更新, 本闸钉住)"
      },
      {
        "id": "C07_B26_MD5_LEDGER",
        "category": "md5_baseline",
        "doc": "checklist",
        "anchor": "网表 e06c1dd6…",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07",
        "expect_mode": "ledger",
        "expect_target": "HW/netlist_v1.csv",
        "probe": [
          "md5sum",
          "HW/netlist_v1.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "B26 的 md5 基线 ★走落表台账为准, 不写死★"
      }
    ]
  }
}
```

★**★本页的每个数字都是本机实读, 没有一条是估的★★** ★
