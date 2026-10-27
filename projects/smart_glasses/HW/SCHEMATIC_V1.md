# HW/SCHEMATIC_V1.md —— ARS45 硬件原理图 V1.1 (9 页图页)
> **V1.1 变更 (2026-10-27, 项目总工)**: ① 新增 **P9 跨铰链界面页** (4 组通道 + 板级归属列) ② 补画 **电池 NTC (BQ25896 TS 脚, 安全项)** · **SYS 过铰链后的 π 滤波** · **9 颗供电器件的输入侧接线** · **上电监督链 (PG + RESET)** ③ 修正 **USB 差分跨铰链被短接** 的缺陷 ④ `U_TEMP` 定型 **TMP117** (0x48) ⑤ `U_BRIDGE` 定位统一为 **DP1.4 TX → MIPI DSI TX 桥接** ⑥ 启动存储加 **flash ≥128MB** 硬约束 ⑦ **ISS-082 前提修正** (TPS7A20 只有固定输出, 不是可编程)
> **生成方式**: 器件表由 `state/gen_schematic_pages.py` 从 `HW/netlist_v1.csv` **机械生成** (不会与 netlist 漂移); 每页叙述写在生成脚本的 NARRATIVE 里 (**项目总工起草 + hw-lead 2026-10-27 审校**)。
> **本版不是投板文件** —— SoC 侧球位图未回 (原厂, 第 6 天), 全部写成 `SoC[TBD-01].<信号>` 占位; 原厂回信后**只填球号 + 改 TBD 项**即可进 PCB。
> **门禁**: `python3 state/check_netlist.py` (20 条机械判据, 项目总工的验收器) + 本文件的 9 页完整性由
> `grep -o '^## P[0-9]' HW/SCHEMATIC_V1.md | sort -u` 机械核对。
> **相关**: 图纸规格 `HW/SCHEMATIC_V1_SPEC.json` · netlist `HW/netlist_v1.csv` · KiCad 可导入 `HW/netlist_v1.net` ·
> 顶层接口 `HW/SCHEMATIC_L1.md` · 连接表 `HW/INTERFACE_TABLE.md` · 查证结果 `HW/ONLINE_FINDINGS_2026-10-26.md`
---

## P1 电源树
> 13 电源域 + 2 路 DC-DC + 7 路 LDO + Type-C 充电链 (充电链在充电板=镜框)

### 功能块与判断
**这张页是整个方案的电源账, 也是散热账的起点。**

- 电源链: Type-C 5V → ESD 阵列 → π 滤波 (磁珠 + 10µF/100µF) → `VBUS_5V` (2.0A) → 充电 IC (BQ25896) → 电池保护 (BQ2970 + 2×MOS) → 电池 → `SYS` (3.0-4.2V, 0.55A 上限) → 2 路 DC-DC (TPS62130A) + **7 路 LDO** (TPS7A20 系列) 分出 13 条轨。
- ★**板子分工 (2026-10-27 审校补)**: 充电链 (Type-C / ESD / π 滤波 / BQ25896 / BQ2970 / 2×MOS / 电池) 在**充电板**, 充电板按 ISS-014 决策 5 **挪到镜框**; SoC 在**主 PCB**, 在镜脚 → 两者**跨铰链**。所以 `SYS` / `VBUS_DET` / `BAT_DET` / `CHG_STAT` / `PWR_GOOD` 全部走 `J_CHG` (跨铰链连接器)。→ **USB 差分对也跨铰链**, 见 P6 (本方案最大的未解项)。
- ★**LDO 是 7 路不是 6 路**: `U_LDO_S28` / `U_LDO_S18` / `U_LDO_S12` (sensor 三条) + `U_LDO_L33` / `U_LDO_L18` (光机两条) + `U_LDO_IO33` / `U_LDO_IO18` (IO 两条)。写错路数 = BOM 少一颗/多一颗。
- ★**R-F1 硬伤已裁决**: `SYS` 下限 3.0V 与 3.3V 轨的 dropout (110mV typ [官方]) 冲突 → 放电末段 12-15% 电量时 3.3V 轨失效 = **用户快没电突然黑屏**。**基线方案: UVP 抬到 3.5V + 3.3V 改由 TPS62130A 供** (代价 12-15% 容量不可用 → 电池容量与续航口径要重算)。第三条路 (更低 dropout 的 LDO / IO 轨直吃 SYS / 加 buck-boost) 正在评估 (ISS-067)。
- ★**V_CORE 上界按 1.0V** (网上查证: 工作电压范围 0.65-1V, DVFS [媒体·百科]) → DC-DC 输出范围与压差核算要覆盖 1.0V, 不是我们原假设的 0.9V。
- **散热账**: 满载镜腿内发热量 0.90W → 皮肤侧 **80.1°C** (镜腿内主口径) / 96.1°C (整机上界), vs ISO 13732-1 的 43°C 红线 → **贴皮肤镜腿只能承受 0.15-0.2W**。⇒ 这页的每个电流数字都要跟"按需触发"口径一起看, 不然整机方案会被温度否掉。
- **[待原厂]**: 各电源域的**标称电压 / 典型电流 / 最大电流 / 上电时序 / 是否需外部 LDO** (TBD-02)。`V_CORE` 与 `V_SOC_IO` 的电压现在都还是待定 → DC-DC 只是"IC 可画, 电压待定"。

#### ★V1.1 (2026-10-27) 本页补画 4 处 + 修正 1 个前提

1. **补画 电池 NTC (安全项, V1 漏画)**: 10k NTC (B=3435) 接 `BQ25896` 的 **TS 脚** → 电池过温/欠温时**硬件直接停充** (不依赖 SoC)。⚠️ 这与 P2 的 SoC 侧数字温度计 `U_TEMP` 是**两回事, 不能互相替代** —— V1 只画了后者, 等于把电池过温保护漏了。
2. **补画 SYS 过铰链后的 π 滤波**: 铰链反复开合是机械噪声源 → `SYS` 过 `J_CHG` 后, 在**主 PCB 侧**先过磁珠 + 10µF/10µF 再进 DC-DC 输入。
3. **补画 所有供电器件的输入脚接线** (V1 只画了输出与去耦, **没画 IC 输入接哪条轨** → ERC §B1 "来源" 缺失): 2×DC-DC + 7×LDO 的输入脚统一接 `RAIL_SYS_PCB` (过铰链 + π 滤波后)。
4. **补画 上电时序链 (在 P8)**: 两路 DC-DC 的 **PG** 引到测试点; `RESET_N` 增加一路**电压监督器开漏释放**, 监督窗口用**分压**实现 → 原厂电压定了**只改两颗电阻, 不改板**。
5. **★前提修正 (ISS-082)**: 原方案写"用**可编程** TPS7A20 一颗覆盖 1.2-5.5V" —— **前提是错的** [官方 ti.com/product/TPS7A20]: TPS7A20 只有**固定输出** (30 档 0.8-5.5V) 且上限 **300mA**。→ 正确的吸收方式是 **换料不换板**: ① 7 路 LDO 全部同封装 (X2SON) → 电压回信后换档位料; ② 2 路 DC-DC 用 TPS62130A 的**引脚可选**输出 (标称 ±5%) → 落在档内换料, 落在档外换同封装可调型号 (改 2 颗反馈电阻); ③ 监督器分压位把任何电压轨映射到监控窗口。**不需要可编程器件, 也不需要改板。**

#### ★V1.2 (2026-10-27) 电池位置改了 —— 跨铰链的大电流换人了

- **触发**: 结构总工在 ISS-085 里抛出 **MECH-B7**: "电池在镜框还是镜脚, 两边假设互斥" —— netlist 标充电板侧(镜框)装电池, 而 `MECH_BUDGET` 写"电池 4.12cc **镜框装不下** → 镜脚"。**这是画图才能撞出来的冲突** (两边各画各的, 从没在同一张图上对过)。
- **裁决 (项目总工, 按体积硬约束)**: **电池 + 电池保护 IC (BQ2970 + 2×MOS) 装镜脚主 PCB**; 充电板 (Type-C + ESD + π + BQ25896) 仍按 ISS-014 决策 5 在镜框。→ **SYS 在镜脚本地产生, 不过铰链** ✅
- **代价 (必须讲清)**: 跨铰链的大电流从 **SYS 0.55A** 变成 **充电电流 1.0-1.5A** → `J_CHG` 改成 **1×10** (pin1/pin2 双 pin 并联走充电电流, pin3/pin4 双 pin 走回流), 并加 `TP_BAT_CHG` 测铰链段压降。
- **充电路径上不装 π 滤波** —— 会破坏 BQ25896 的环路稳定性; 充电路径只做 **双 pin 并联 + 载流铜箔 + 压降/发热核算** (核算在 ISS-091, 结构总工出长度与固定方式)。
- **可回退分支 (跟老板的续航口径挂钩)**: 若拍板"按需触发 130mAh" 方案 (体积 1.8cc), 电池**可能装进镜框** → 跨铰链大电流就降回 **SYS 0.55A**, 充电电流完全不过铰链 (铰链发热更小)。⇒ `J_CHG` 的 pin map 留了 3 个预留位, 两种形态**都能落板**, 不用改板。
- **电池 NTC 跟着搬**: NTC 贴电芯 → 在镜脚 → `BQ25896` 的 TS 脚在镜框 → **TS 走线要跨铰链** (高阻, OK) —— 已在图上标出。

### 器件表 (110 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| VBUS_5V | J_TYPE_C A4+A9+B4+B9 | D_ESD_TC | RAIL_VBUS_5V | 5.0V ±5% | RAIL | 必装 | CHG_BOARD | [推算] |  | 电源域: 目标 5.0V ±5% / 最大电流 2.0A (PD 5V/2A); **充电链整条在充电板**, SYS 经 J_CHG 回主 PCB; SoC 侧球位号 TBD-0 |
| VBUS_5V | J_TYPE_C | USB_VBUS_RAW | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | Type-C 入口连接器 (充电板侧, 在镜框); 本表 pin 编号为**逻辑编号** (pin1=VBUS, pin2=CC1, pin3=CC2, pin4=D+, pin5 |
| USB_VBUS_RAW | USB_VBUS_RAW | D_ESD_TC | D_ESD_TC | ESD 阵列 [待选型] | D | 必装 | CHG_BOARD | [推算] |  | Type-C VBUS 入口 ESD 阵列 (规格 C-01 'Type-C 座 + ESD 阵列'); 通道数/钳位电压随 Type-C 座定 |
| VBUS_5V_ESD | D_ESD_TC | FB_VBUS | FB_VBUS | π 滤波磁珠 [待选型] | L | 必装 | CHG_BOARD | [推算] |  | [VBUS_5V_ESD] VBUS 入口 π 滤波磁珠位 (阻抗/电流随充电 IC 环路稳定性定) |
| VBUS_5V_ESD | VBUS_5V_ESD | C_VBUS_IN | C_VBUS_IN | [待选型] 10µF | C | DNP | CHG_BOARD | [推算] |  | π 滤波输入电容位 (值待充电 IC 定; 内置则改 DNP) |
| GND | C_VBUS_IN | GND | C_VBUS_IN | [待选型] 10µF | C | DNP | CHG_BOARD | [推算] |  | π 滤波输入电容 地端 |
| VBUS_5V_F1 | FB_VBUS | C_VBUS_OUT | FB_VBUS | π 滤波磁珠 [待选型] | L | 必装 | CHG_BOARD | [推算] |  | [VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗) |
| VBUS_5V_F1 | VBUS_5V_F1 | C_VBUS_OUT | C_VBUS_OUT | [待选型] 100µF | C | DNP | CHG_BOARD | [推算] |  | π 滤波后级电容位 (BQ25896 建议 ≥100µF) |
| GND | C_VBUS_GND | GND | C_VBUS_GND | [待选型] 100µF | C | DNP | MAIN_PCB | [推算] |  | π 滤波后级**对地**电容 (★V1.6 修正: 原来 C_VBUS_OUT 一颗当两个用 —— 既是 FB·U_CHG 的串联电容, 又是对地电容 · 一颗 2 脚件落进 3  |
| VBUS_5V_CHG | C_VBUS_OUT | U_CHG pin1 | C_VBUS_OUT | [待选型] 100µF | C | DNP | CHG_BOARD | [推算] |  | π 滤波电容 (后级, 串联) 位 |
| VBUS_5V_CHG | C_VBUS_GND | C_VBUS_OUT | C_VBUS_GND | [待选型] 100µF | C | DNP | MAIN_PCB | [推算] |  | π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点) |
| VBUS_5V_CHG | U_CHG | NET_VBUS_5V_CHG | U_CHG | BQ25896 | IC | 必装 | CHG_BOARD | [官方] |  | [VBUS_5V_CHG] 1A 单节锂电充电 IC (TI); 输入接 VBUS_5V_F1, BAT 脚接 BAT 轨, STAT/PG 脚回主 PCB (见 P2) |
| BAT_CHG | U_CHG pin13+pin14 | RAIL_BAT_CHG | NET_BAT_PROT | 单端 | NET | 必装 | CHG_BOARD | [官方] |  | [BAT_CHG] ★V1.2: 充电电流路径 (1.0-1.5A) 镜框充电板 BQ25896 · 跨铰链 · 镜脚电池; **铰链段不加 π 滤波** (会破坏充电 IC 的环 |
| BAT_CHG | RAIL_BAT_CHG | J_CHG pin1 | RAIL_BAT_CHG | 跨铰链 1.5A (双 pin 并联) | NET | 必装 | HINGE | [推算] |  | [BAT_CHG] 充电电流跨铰链 (J_CHG pin1/pin2 并联); 载流/压降/发热核算见 P9 页 |
| BAT_CHG | J_CHG pin1 | J_CHG pin2 | J_CHG | 跨铰链 1.5A (双 pin 并联) | NET | 必装 | HINGE | [推算] |  | [BAT_CHG] 双 pin 并联 (每 pin ≈0.75A, 1.27mm 排线); 铰链段压降与发热按结构实际长度核算 |
| BAT_CHG | J_CHG pin2 | U_BATPROT | NET_BAT_PROT | 单端 | NET | 必装 | HINGE | [官方] |  | [BAT_CHG] 充电电流进镜脚侧电池保护 IC (BQ2970) —— **保护 IC 与电池同板 (镜脚)** |
| HINGE_RSV | J_CHG pin9 | J_CHG pin9 | J_CHG | 预留 (不装) | NET | DNP | HINGE | [推算] |  | [INVENTORY] [HINGE_RSV] J_CHG pin9 预留位 (★V1.5 裁决: 充电 IC 的 I2C **不跨铰链** —— 充电电流靠 R_ILIM 硬件限 |
| HINGE_RSV | J_CHG pin10 | J_CHG pin10 | J_CHG | 预留 (不装) | NET | DNP | HINGE | [推算] |  | [INVENTORY] [HINGE_RSV] J_CHG pin10 预留位 (★V1.5 裁决: 充电 IC 的 I2C **不跨铰链** —— 充电电流靠 R_ILIM 硬件 |
| GND | J_CHG pin3 | J_CHG pin4 | J_CHG | 回流 (双 pin) | NET | 必装 | HINGE | [推算] |  | [GND_CHG] 充电电流回流双 pin (与电源 pin 相邻 · 环路面积最小) |
| GND | J_CHG pin4 | GND | J_CHG | 回流 (双 pin) | NET | 必装 | HINGE | [推算] |  | [GND_CHG] 回流进镜脚侧数字地 |
| BAT | RAIL_BAT | U_BATPROT | RAIL_BAT | 4.2V 满 / 3.0V 截止 | RAIL | 必装 | MAIN_PCB | [官方] |  | 电源域: 目标 4.2V 满 / 3.0V 截止 / 最大电流 1.0-1.5A 充电; 电流路径 电池·Q2·Q1·本轨; ★V1.2: **电池在镜脚主 PCB** (MECH |
| BAT | U_BATPROT | RAIL_BAT | U_BATPROT | BQ2970 | IC | 必装 | MAIN_PCB | [官方] |  | [BAT] 1 节锂电保护 IC (配 2×MOS), **与电池同板 (镜脚)**; 具体型号/封装待选型 (BQ2970 系列为规格原文所指) |
| BAT_CELL_P | BT_432243 B+ | Q1 | BT_432243 | 432243 3.7V ≥420mAh | CONN | 必装 | MAIN_PCB | [推算] |  | [BAT_CELL_P] 电芯正极 · 第 1 只保护 MOS (Q1) 漏极; 尺寸 4.3×2.4mm 级, 焊接方式待结构确认 |
| BAT_PROT_CELL | Q1 | Q2 | Q1 | [待选型] N-MOS | SW | 必装 | MAIN_PCB | [推算] |  | [BAT_PROT_CELL] ★F2 修正: Q1 与 Q2 **串联** (原来两管同网 = 并联, 保护无效); V_DS / 栅压 / R_DS(on) / 封装待 BQ2 |
| BAT_PROT_CELL2 | Q2 | U_BATPROT | Q2 | [待选型] N-MOS | SW | 必装 | MAIN_PCB | [推算] |  | [BAT_PROT_CELL2] 第 2 只保护 MOS · 电池保护 IC (BQ2970) 的 B+ 脚; 参数同 Q1 |
| BAT_GATE | U_BATPROT GATE | Q1 GATE | U_BATPROT | BQ2970 | IC | 必装 | MAIN_PCB | [官方] |  | [BAT_GATE] ★F2 修正: **两管栅极由 BQ2970 同驱** (原来完全没有栅极连接 · MOS 永远不导通/不受控); 栅极网络按 BQ2970 数据手册确认是否 |
| BAT_GATE | Q1 GATE | Q2 GATE | Q1 | [待选型] N-MOS | SW | 必装 | MAIN_PCB | [推算] |  | [BAT_GATE] 两管共栅 (back-to-back 接法, 按 BQ2970 数据手册确认体二极管方向) |
| BAT_CELL_N | BT_432243 B- | U_BATPROT B- | BT_432243 | 432243 3.7V ≥420mAh | CONN | 必装 | MAIN_PCB | [推算] |  | [BAT_CELL_N] ★F2 修正: **电芯负极 · BQ2970 的 B- 脚** (原来电芯只有一个端子 · 电池回路不闭合) |
| SYS | RAIL_SYS | U_BATPROT | RAIL_SYS | 3.0-4.2V | RAIL | 必装 | MAIN_PCB | [推算] |  | 电源域: 目标 3.0-4.2V / 最大电流 0.55A (330mA×1.5 + 瞬态); **R-F1 裁决: SYS 下限抬到 3.5V**; ★V1.2: **SYS 在 |
| BAT_CHG | J_CHG | J_CHG pin1 | J_CHG | 1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流) | CONN | 必装 | HINGE | [推算] |  | [SYS] ★V1.5 定稿 pin map (1×10p@0.5mm): pin1/pin2=BAT_CHG (充电电流**双 pin 并联**), pin3/pin4=GND  |
| TS_BAT | U_CHG pin11 | R_NTC_BAT | NET_TS_BAT | 单端 | NET | 必装 | CHG_BOARD | [官方] |  | [TS_BAT] ★电池温度检测: 103AT NTC 接 BQ25896 的 TS 脚 (过温/欠温时**硬件直接停充**; 分压网络按 datasheet 三件式) (不依赖  |
| TS_BAT | R_NTC_BAT | GND | R_NTC_BAT | 103AT NTC ±1% (贴电芯, 另一端接电芯负极=系统 GND) | R | 必装 | MAIN_PCB | [官方] |  | [TS_BAT] ★V1.5 修正: NTC **贴电芯 ⇒ 在镜脚** (V1.2 电池搬镜脚后), 而 BQ25896 的 TS 脚在镜框充电板 · **TS 必须跨铰链**  |
| TS_BAT | R_TS_PULL | GND | R_TS_PULL | 30.31k ±1% | R | 必装 | MAIN_PCB | [官方] |  | [TS_BAT] TS 对地下拉 = **RT2 30.31k** (BQ25896 datasheet 温度检测分压); ★V1.6 挪到**镜脚** (NTC 侧) —— 下拉 |
| TS_BAT | J_CHG pin8 | R_NTC_BAT | J_CHG | 跨铰链 (高阻) | NET | 必装 | HINGE | [推算] |  | [TS_BAT] ★V1.5 补画: **TS 跨铰链这一段** (V1.2 把电池/NTC 搬镜脚时漏了) · 走 J_CHG pin8 |
| REGN | U_CHG pin22 | R_TS_TOP | U_CHG | BQ25896 内部 5V (REGN) | NET | 必装 | CHG_BOARD | [官方] |  | [REGN] ★V1.6 补: BQ25896 的 **REGN 5V** (内部 LDO 输出, RT1 的参考端) —— 原来 R_TS_TOP 的 REGN 端没有对应节点  |
| REGN | C_REGN | U_CHG pin22 | C_REGN | [待选型] 1µF | C | 必装 | CHG_BOARD | [官方] |  | [REGN] BQ25896 REGN 去耦电容 (datasheet 要求) |
| GND | C_REGN | GND | C_REGN | [待选型] 1µF | C | 必装 | MAIN_PCB | [官方] |  | [REGN] REGN 去耦电容 地端 |
| TS_BAT | R_TS_TOP | U_CHG pin22 | R_TS_TOP | 5.24k ±1% (RT1: REGN 到 TS) | R | 必装 | CHG_BOARD | [官方] |  | [TS_BAT] ★V1.5 补画: **RT1 5.24k (REGN 到 TS)** —— BQ25896 温度检测是 RT1/RT2/NTC 三件式, 原来只画了 NTC + |
| IINLIM | U_CHG pin10 | R_ILIM | R_ILIM | 470Ω ±1% (IINMAX ≈0.71-0.87A → ICHG ≈0.68A) | R | 必装 | CHG_BOARD | [官方] |  | [IINLIM] ★★V1.7 按 ISS-091 结构核算定 **470Ω**: BQ25896 的 IINLIM 复位默认 **2048mA** [官方] (不装 = 铰链吃  |
| GND | R_ILIM | GND | R_ILIM | 470Ω ±1% (IINMAX ≈0.71-0.87A → ICHG ≈0.68A) | R | 必装 | MAIN_PCB | [官方] |  | [IINLIM] 限流电阻 另一端接地 (IINLIM 对地设定输入电流上限) |
| BAT_CHG | J_CHG pin1 | TP_BAT_CHG | TP_BAT_CHG | 跨铰链段压降测点 | TP | 必装 | MAIN_PCB | [推算] |  | [BAT_CHG] ★跨铰链充电电流段压降测点 (1.5A 下压降 = 接触电阻×1.5A); 铰链段发热与压降按结构实际长度核算 (结构总工) |
| V_CORE | RAIL_V_CORE | U_DCDC_VCORE | RAIL_V_CORE | [待原厂] (典型 0.8-0.9V) | RAIL | 必装 | MAIN_PCB | [官方] | TBD-02 | 电源域: 目标 [待原厂] (典型 0.8-0.9V) / 最大电流 ≥2.0A (0.9W/0.8V×1.5=1.69A); IC TPS62130A; SoC 侧球位号 TBD |
| SYS_PCB | RAIL_SYS | U_DCDC_VCORE | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [V_CORE] U_DCDC_VCORE 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| V_CORE | RAIL_V_CORE | U_DCDC_VCORE | U_DCDC_VCORE | TPS62130A | IC | 必装 | MAIN_PCB | [官方] | TBD-02 | [V_CORE] DC-DC (3A) 供 V_CORE; 电压 [待原厂] (典型 0.8-0.9V) / 最大电流 ≥2.0A (0.9W/0.8V×1.5=1.69A); 选 |
| V_CORE | RAIL_V_CORE | C_BULK_V_CORE | C_BULK_V_CORE | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [V_CORE] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_V_CORE | GND | C_BULK_V_CORE | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [V_CORE] 体电容 地端 |
| V_CORE | RAIL_V_CORE | C_HF_V_CORE | C_HF_V_CORE | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [V_CORE] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_V_CORE | GND | C_HF_V_CORE | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [V_CORE] 高频去耦电容 地端 |
| V_SOC_IO | RAIL_V_SOC_IO | U_DCDC_VIO | RAIL_V_SOC_IO | [待原厂] (3.3V / 1.8V / 1.2V) | RAIL | 必装 | MAIN_PCB | [官方] | TBD-02 | 电源域: 目标 [待原厂] (3.3V / 1.8V / 1.2V) / 最大电流 ≥1.0A; IC TPS62130A; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_DCDC_VIO | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [V_SOC_IO] U_DCDC_VIO 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| V_SOC_IO | RAIL_V_SOC_IO | U_DCDC_VIO | U_DCDC_VIO | TPS62130A | IC | 必装 | MAIN_PCB | [官方] | TBD-02 | [V_SOC_IO] DC-DC (3A) 供 V_SOC_IO; 电压 [待原厂] (3.3V / 1.8V / 1.2V) / 最大电流 ≥1.0A; 选型依据 规格 powe |
| V_SOC_IO | RAIL_V_SOC_IO | C_BULK_V_SOC_IO | C_BULK_V_SOC_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [V_SOC_IO] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_V_SOC_IO | GND | C_BULK_V_SOC_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [V_SOC_IO] 体电容 地端 |
| V_SOC_IO | RAIL_V_SOC_IO | C_HF_V_SOC_IO | C_HF_V_SOC_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [V_SOC_IO] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_V_SOC_IO | GND | C_HF_V_SOC_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [V_SOC_IO] 高频去耦电容 地端 |
| SENSOR_AVDD | RAIL_SENSOR_AVDD | U_LDO_S28 | RAIL_SENSOR_AVDD | 2.8V | RAIL | 必装 | MAIN_PCB | [官方] |  | 电源域: 目标 2.8V / 最大电流 30mA; IC TPS7A20-28; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_LDO_S28 | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [SENSOR_AVDD] U_LDO_S28 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| SENSOR_AVDD | RAIL_SENSOR_AVDD | U_LDO_S28 | U_LDO_S28 | TPS7A20-28 | IC | 必装 | MAIN_PCB | [官方] |  | [SENSOR_AVDD] LDO 供 SENSOR_AVDD (2.8V/30mA); 电压 2.8V / 最大电流 30mA; 选型依据 规格 power_rails[SENS |
| SENSOR_AVDD | RAIL_SENSOR_AVDD | C_BULK_SENSOR_AVDD | C_BULK_SENSOR_AVDD | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_AVDD] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_SENSOR_AVDD | GND | C_BULK_SENSOR_AVDD | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_AVDD] 体电容 地端 |
| SENSOR_AVDD | RAIL_SENSOR_AVDD | C_HF_SENSOR_AVDD | C_HF_SENSOR_AVDD | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_AVDD] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_SENSOR_AVDD | GND | C_HF_SENSOR_AVDD | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_AVDD] 高频去耦电容 地端 |
| SENSOR_VDD_IO | RAIL_SENSOR_VDD_IO | U_LDO_S18 | RAIL_SENSOR_VDD_IO | 1.8V | RAIL | 必装 | MAIN_PCB | [官方] |  | 电源域: 目标 1.8V / 最大电流 30mA; IC TPS7A20-18; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_LDO_S18 | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [SENSOR_VDD_IO] U_LDO_S18 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| SENSOR_VDD_IO | RAIL_SENSOR_VDD_IO | U_LDO_S18 | U_LDO_S18 | TPS7A20-18 | IC | 必装 | MAIN_PCB | [官方] |  | [SENSOR_VDD_IO] LDO 供 SENSOR_VDD_IO (1.8V/30mA); 电压 1.8V / 最大电流 30mA; 选型依据 规格 power_rails[ |
| SENSOR_VDD_IO | RAIL_SENSOR_VDD_IO | C_BULK_SENSOR_VDD_IO | C_BULK_SENSOR_VDD_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_VDD_IO] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_SENSOR_VDD_IO | GND | C_BULK_SENSOR_VDD_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_VDD_IO] 体电容 地端 |
| SENSOR_VDD_IO | RAIL_SENSOR_VDD_IO | C_HF_SENSOR_VDD_IO | C_HF_SENSOR_VDD_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_VDD_IO] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_SENSOR_VDD_IO | GND | C_HF_SENSOR_VDD_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_VDD_IO] 高频去耦电容 地端 |
| SENSOR_CORE | RAIL_SENSOR_CORE | U_LDO_S12 | RAIL_SENSOR_CORE | 1.2V | RAIL | 必装 | MAIN_PCB | [官方] |  | 电源域: 目标 1.2V / 最大电流 50mA; IC TPS7A20-12; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_LDO_S12 | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [SENSOR_CORE] U_LDO_S12 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| SENSOR_CORE | RAIL_SENSOR_CORE | U_LDO_S12 | U_LDO_S12 | TPS7A20-12 | IC | 必装 | MAIN_PCB | [官方] |  | [SENSOR_CORE] LDO 供 SENSOR_CORE (1.2V/50mA); 电压 1.2V / 最大电流 50mA; 选型依据 规格 power_rails[SENS |
| SENSOR_CORE | RAIL_SENSOR_CORE | C_BULK_SENSOR_CORE | C_BULK_SENSOR_CORE | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_CORE] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_SENSOR_CORE | GND | C_BULK_SENSOR_CORE | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_CORE] 体电容 地端 |
| SENSOR_CORE | RAIL_SENSOR_CORE | C_HF_SENSOR_CORE | C_HF_SENSOR_CORE | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_CORE] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_SENSOR_CORE | GND | C_HF_SENSOR_CORE | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [SENSOR_CORE] 高频去耦电容 地端 |
| LIGHT_3V3 | RAIL_LIGHT_3V3 | U_LDO_L33 | RAIL_LIGHT_3V3 | 3.3V | RAIL | 必装 | MAIN_PCB | [推算] | TBD-02 | 电源域: 目标 3.3V / 最大电流 150mA; IC TPS7A20-33; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_LDO_L33 | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [LIGHT_3V3] U_LDO_L33 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| LIGHT_3V3 | RAIL_LIGHT_3V3 | U_LDO_L33 | U_LDO_L33 | TPS7A20-33 | IC | 必装 | MAIN_PCB | [推算] | TBD-02 | [LIGHT_3V3] LDO 供 LIGHT_3V3 (3.3V/150mA); 电压 3.3V / 最大电流 150mA; 选型依据 规格 power_rails[LIGHT_ |
| LIGHT_3V3 | RAIL_LIGHT_3V3 | C_BULK_LIGHT_3V3 | C_BULK_LIGHT_3V3 | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [LIGHT_3V3] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_LIGHT_3V3 | GND | C_BULK_LIGHT_3V3 | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [LIGHT_3V3] 体电容 地端 |
| LIGHT_3V3 | RAIL_LIGHT_3V3 | C_HF_LIGHT_3V3 | C_HF_LIGHT_3V3 | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [LIGHT_3V3] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_LIGHT_3V3 | GND | C_HF_LIGHT_3V3 | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [LIGHT_3V3] 高频去耦电容 地端 |
| LIGHT_1V8 | RAIL_LIGHT_1V8 | U_LDO_L18 | RAIL_LIGHT_1V8 | 1.8V | RAIL | DNP | MAIN_PCB | [推算] | TBD-02 | 电源域: 目标 1.8V / 最大电流 50mA; IC TPS7A20-18; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_LDO_L18 | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | DNP | MAIN_PCB | [推算] |  | [LIGHT_1V8] U_LDO_L18 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| LIGHT_1V8 | RAIL_LIGHT_1V8 | U_LDO_L18 | U_LDO_L18 | TPS7A20-18 | IC | DNP | MAIN_PCB | [推算] | TBD-02 | [LIGHT_1V8] LDO 供 LIGHT_1V8 (1.8V/50mA); 电压 1.8V / 最大电流 50mA; 选型依据 规格 power_rails[LIGHT_1V |
| LIGHT_1V8 | RAIL_LIGHT_1V8 | C_BULK_LIGHT_1V8 | C_BULK_LIGHT_1V8 | 10µF | C | DNP | MAIN_PCB | [推算] |  | [LIGHT_1V8] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_LIGHT_1V8 | GND | C_BULK_LIGHT_1V8 | 10µF | C | DNP | MAIN_PCB | [推算] |  | [LIGHT_1V8] 体电容 地端 |
| LIGHT_1V8 | RAIL_LIGHT_1V8 | C_HF_LIGHT_1V8 | C_HF_LIGHT_1V8 | 100nF | C | DNP | MAIN_PCB | [推算] |  | [LIGHT_1V8] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_LIGHT_1V8 | GND | C_HF_LIGHT_1V8 | 100nF | C | DNP | MAIN_PCB | [推算] |  | [LIGHT_1V8] 高频去耦电容 地端 |
| VDD_3V3_IO | RAIL_VDD_3V3_IO | U_LDO_IO33 | RAIL_VDD_3V3_IO | 3.3V | RAIL | 必装 | MAIN_PCB | [推算] |  | 电源域: 目标 3.3V / 最大电流 200mA; IC TPS7A20-33; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_LDO_IO33 | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] U_LDO_IO33 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| VDD_3V3_IO | RAIL_VDD_3V3_IO | U_LDO_IO33 | U_LDO_IO33 | TPS7A20-33 | IC | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] LDO 供 VDD_3V3_IO (3.3V/200mA); 电压 3.3V / 最大电流 200mA; 选型依据 规格 power_rails[VDD_ |
| VDD_3V3_IO | RAIL_VDD_3V3_IO | C_BULK_VDD_3V3_IO | C_BULK_VDD_3V3_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_VDD_3V3_IO | GND | C_BULK_VDD_3V3_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 体电容 地端 |
| VDD_3V3_IO | RAIL_VDD_3V3_IO | C_HF_VDD_3V3_IO | C_HF_VDD_3V3_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_VDD_3V3_IO | GND | C_HF_VDD_3V3_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 高频去耦电容 地端 |
| VDD_1V8_IO | RAIL_VDD_1V8_IO | U_LDO_IO18 | RAIL_VDD_1V8_IO | 1.8V | RAIL | 必装 | MAIN_PCB | [推算] |  | 电源域: 目标 1.8V / 最大电流 100mA; IC TPS7A20-18; SoC 侧球位号 TBD-01 |
| SYS_PCB | RAIL_SYS | U_LDO_IO18 | RAIL_SYS | 3.5-4.2V (R-F1 抬下限后) | NET | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] U_LDO_IO18 输入脚供电 (SYS 镜脚本地产生, 电池保护后); LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方] |
| VDD_1V8_IO | RAIL_VDD_1V8_IO | U_LDO_IO18 | U_LDO_IO18 | TPS7A20-18 | IC | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] LDO 供 VDD_1V8_IO (1.8V/100mA); 电压 1.8V / 最大电流 100mA; 选型依据 规格 power_rails[VDD_ |
| VDD_1V8_IO | RAIL_VDD_1V8_IO | C_BULK_VDD_1V8_IO | C_BULK_VDD_1V8_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02) |
| GND | C_BULK_VDD_1V8_IO | GND | C_BULK_VDD_1V8_IO | 10µF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] 体电容 地端 |
| VDD_1V8_IO | RAIL_VDD_1V8_IO | C_HF_VDD_1V8_IO | C_HF_VDD_1V8_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] 高频去耦电容位 (紧贴 IC 引脚) |
| GND | C_HF_VDD_1V8_IO | GND | C_HF_VDD_1V8_IO | 100nF | C | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] 高频去耦电容 地端 |
| LIGHT_5V | RAIL_LIGHT_5V | CONN_LIGHT pin21 | RAIL_LIGHT_5V | 5.0V | RAIL | DNP | HINGE | [推算] | TBD-02 | 电源域: 目标 [待 JBD] / 最大电流 50mA; 供电方式 [待 JBD] 确认 (VBUS 直供 或 升压); SoC 侧球位号 TBD-01 |
| LIGHT_5V | RAIL_LIGHT_5V | D_ESD_LIGHT | D_ESD_LIGHT | ESD 阵列 [待选型] | D | DNP | MAIN_PCB | [推算] |  | [LIGHT_5V] 光机 5V 供电口 ESD 阵列位 (跨铰链, 随光机接口确认后定) |
| GND | D_ESD_LIGHT | GND | D_ESD_LIGHT | ESD 阵列 [待选型] | D | DNP | MAIN_PCB | [推算] |  | [LIGHT_5V] 光机侧 ESD 地端 |
| GND | RAIL_GND | GND | RAIL_GND | 机壳地 / 数字地 (单点汇流) | RAIL | 必装 | MAIN_PCB | [推算] |  | 电源域: 目标 — / 最大电流 —; 单点汇流位置由结构总工定 (ISS-065); SoC 侧球位号 TBD-01 |
| GND | RAIL_GND | CHG_GND_STAR | CHG_GND_STAR | 单点汇流位 | CONN | 必装 | MAIN_PCB | [推算] |  | [GND] 充电板↔主 PCB 的地单点汇流位 (结构总工定位置, ISS-065) |
| GND | CHG_GND_STAR | GND | CHG_GND_STAR | 单点汇流位 | CONN | 必装 | MAIN_PCB | [推算] |  | [GND] 汇流位 接主板数字地 (与机壳地分开) |

## P2 SoC 主控
> 低速控制 / ADC 检测 / I2C / FSIN — SoC 侧全部 TBD-01 占位

### 功能块与判断
**SoC 侧的脚全是 TBD 占位 —— 这页是"原厂回信后只填球号就能投板"的关键。**

- SoC 侧节点统一写成 `SoC[TBD-01].<信号名>`: **原厂引脚表/球位图未回 (第 5 天)**, 所以本页**不写一个球号**。
- 本页信号: I2C_A (总线 A, 接 sensor / 温度检测位 / 桥接 / 充电IC) · 充电状态回读 (`CHG_STAT` / `PWR_GOOD` / `VBUS_DET` / `BAT_DET`) · `FSIN` 帧同步 (引到测试点, 若 SoC 无此脚则 DNP) · `ID_DETECT` (焊盘跳线, 2 位 GPIO 编码)。
- ★**V1.1 已定型: `U_TEMP` = TI TMP117 数字温度计** [官方 ti.com/product/TMP117] (±0.1°C max, 16bit, 5µA max, 1.7-5.5V, WSON-2 2×2mm), I2C_A **地址 0x48** —— 与 sensor 0x36 / 桥接 0x50 / 充电 IC 0x12 / 光机 0x72 **全部不冲突** (地址表见 `HW/INTERFACE_TABLE.md` §4.2)。若原厂坚持裸 NTC → 改 ADC 分压位, **不换板**。⚠️ 但**"测哪个点"还没定** (SoC die / 镜腿 / 电池): 要 SW 总工确认测点物理位置, 否则 ±0.1°C 测的是错的东西。
- ★**充电状态读回有兜底**: 即使 SoC 读不到充电 IC 状态, 也有 `TP_CHG_STAT` + `TP_VBUS` → "充电时禁 OD" 门禁不会瞎 (M-CHRG 判未验, 但不至于误判)。
- ★**USB PHY 基本确认存在** (官网智能可穿戴页列 USB 3.0) → `USB_D+/D-` 走 Type-C 这条路**有依据了**; 但版本 (2.0/3.0) 与 PHY 数量仍要问 (影响引脚预算 + 连接器 pin 数, 见 P6)。
- **[待原厂]**: 引脚表与球位图 (TBD-01) · USB PHY 版本与引脚数 (TBD-10) · 帧同步能否引出/能否输入 (TBD-07 / TBD-13) · **DDC I2C 是否独立于 SoC 通用 I2C, 以及 DDC 地址是否可配 (TBD-09, 限 DDC 侧)**。

### 器件表 (30 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| I2C_A_SCL | SoC[TBD-01].I2C_A_SCL | R_PU_I2CA_SCL | NET_I2C_A_SCL | 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF) | NET | 必装 | MAIN_PCB | [推算] |  | 方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF); 连接 SoC [待原厂] + sensor/ |
| I2C_A_SDA | SoC[TBD-01].I2C_A_SDA | R_PU_I2CA_SDA | NET_I2C_A_SDA | 上拉 4.7k 到 3.3V | NET | 必装 | MAIN_PCB | [推算] |  | 方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V; 连接 同上; 测试点 TP_I2CA_SDA |
| VDD_3V3_IO | R_PU_I2CA_SCL | RAIL_VDD_3V3_IO | R_PU_I2CA_SCL | 4.7k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] I2C_A 上拉 (规格: 4.7k 到 3.3V; 灌 702µA, t_r=2.38µs@100pF) |
| VDD_3V3_IO | R_PU_I2CA_SDA | RAIL_VDD_3V3_IO | R_PU_I2CA_SDA | 4.7k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] I2C_A 上拉 |
| I2C_A_SCL | CONN_CAM pin13 | NET_I2C_A_SCL | NET_I2C_A_SCL | 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF) | NET | 必装 | HINGE | [推算] |  | [I2C_A_SCL] 附加节点 (同 net) |
| I2C_A_SDA | CONN_CAM pin14 | NET_I2C_A_SDA | NET_I2C_A_SDA | 上拉 4.7k 到 3.3V | NET | 必装 | HINGE | [推算] |  | [I2C_A_SDA] 附加节点 (同 net) |
| I2C_A_SCL | U_TEMP pin2 | NET_I2C_A_SCL | U_TEMP | TMP117 数字温度计 (I2C 地址 0x48, ±0.1°C max, 16bit) | IC | 必装 | MAIN_PCB | [官方] |  | [I2C_A_SCL] ★V1.1 定型: 选 TI TMP117 [官方 ti.com/product/TMP117] (1.7-5.5V 供电, 5µA max, WSON-2 |
| I2C_A_SDA | U_TEMP pin1 | NET_I2C_A_SDA | U_TEMP | TMP117 数字温度计 | IC | 必装 | MAIN_PCB | [官方] |  | [I2C_A_SDA] TMP117 SDA |
| VDD_3V3_IO | U_TEMP pin3 | RAIL_VDD_3V3_IO | U_TEMP | TMP117 数字温度计 | IC | 必装 | MAIN_PCB | [官方] |  | [I2C_A_SCL] TMP117 供电 (3.3V, 5µA max) |
| GND | U_TEMP pin4 | GND | U_TEMP | TMP117 数字温度计 | IC | 必装 | MAIN_PCB | [官方] |  | [I2C_A_SCL] TMP117 地脚 |
| VDD_3V3_IO | C_TEMP | RAIL_VDD_3V3_IO | C_TEMP | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [I2C_A_SCL] TMP117 就近去耦 |
| GND | C_TEMP | GND | C_TEMP | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [I2C_A_SCL] TMP117 去耦 地端 |
| VBUS_DET | R_VBUS_DET_1 | R_VBUS_DET_2 | NET_VBUS_DET | 1M+1M 分压 + 100nF | NET | 必装 | MAIN_PCB | [推算] |  | 方向 充电板→SoC; 电平 0-3.3V (分压); 阻抗 1M+1M 分压 + 100nF; 连接 Type-C VBUS → ADC; 测试点 TP_VBUS |
| VBUS_5V | RAIL_VBUS_5V | R_VBUS_DET_1 | R_VBUS_DET_1 | 1M ±1% | R | 必装 | CHG_BOARD | [推算] |  | [VBUS_DET_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 VBUS_5V 已归一到源节点] |
| VBUS_DET | R_VBUS_DET_2 | GND | R_VBUS_DET_2 | 1M ±1% | R | 必装 | CHG_BOARD | [推算] |  | [VBUS_DET] 分压下臂 地端 |
| VBUS_DET | C_DET_VBUS | J_CHG pin7 | C_DET_VBUS | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [VBUS_DET] ADC 滤波电容 (跨铰链侧 (充电板测 VBUS, 高阻分压)) |
| GND | C_DET_VBUS | GND | C_DET_VBUS | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [VBUS_DET] ADC 滤波电容 地端 |
| VBUS_DET | SoC[TBD-01].VBUS_DET | NET_VBUS_DET | NET_VBUS_DET | 1M+1M 分压 + 100nF | NET | 必装 | MAIN_PCB | [推算] |  | [VBUS_DET] SoC ADC 输入节点 (跨板那一侧) |
| BAT_DET | R_BAT_DET_1 | R_BAT_DET_2 | NET_BAT_DET | 1M+1M 分压 + 100nF | NET | 必装 | MAIN_PCB | [推算] |  | 方向 充电板→SoC; 电平 0-3.3V (分压); 阻抗 1M+1M 分压 + 100nF; 连接 电池 BAT → ADC; 测试点 TP_BAT |
| BAT | RAIL_BAT | R_BAT_DET_1 | R_BAT_DET_1 | 1M ±1% | R | 必装 | MAIN_PCB | [推算] |  | [BAT_DET_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 BAT 已归一到源节点] |
| BAT_DET | R_BAT_DET_2 | GND | R_BAT_DET_2 | 1M ±1% | R | 必装 | MAIN_PCB | [推算] |  | [BAT_DET] 分压下臂 地端 |
| BAT_DET | C_DET_BAT | R_BAT_DET_2 | C_DET_BAT | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [BAT_DET] ADC 滤波电容 (★V1.2: 电池在镜脚, 本地检测, 不跨铰链) |
| GND | C_DET_BAT | GND | C_DET_BAT | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [BAT_DET] ADC 滤波电容 地端 |
| BAT_DET | SoC[TBD-01].BAT_DET | NET_BAT_DET | NET_BAT_DET | 1M+1M 分压 + 100nF | NET | 必装 | MAIN_PCB | [推算] |  | [BAT_DET] SoC ADC 输入节点 (跨板那一侧) |
| CHG_STAT | U_CHG | R_PU_CHG_STAT | NET_CHG_STAT | 单端 | NET | 必装 | CHG_BOARD | [推算] |  | 方向 充电IC→SoC; 电平 3.3V (开漏); 阻抗 单端; 连接 BQ25896 STAT 脚 → SoC GPIO; 测试点 TP_CHG_STAT |
| VDD_3V3_IO | R_PU_CHG_STAT | RAIL_VDD_3V3_IO | R_PU_CHG_STAT | 10k ±1% | R | 必装 | CHG_BOARD | [推算] |  | [VDD_3V3_IO] CHG_STAT 开漏上拉 (BQ25896 状态脚) |
| CHG_STAT | J_CHG pin5 | NET_CHG_STAT | NET_CHG_STAT | 单端 | NET | 必装 | HINGE | [推算] |  | [CHG_STAT] 附加节点 (同 net, 经 J_CHG 到主 PCB) |
| PWR_GOOD | U_CHG | R_PU_PG | NET_PWR_GOOD | 单端 | NET | 必装 | CHG_BOARD | [推算] |  | 方向 充电IC→SoC; 电平 3.3V (开漏); 阻抗 单端; 连接 BQ25896 PG 脚 → SoC GPIO; 测试点 TP_PG |
| VDD_3V3_IO | R_PU_PG | RAIL_VDD_3V3_IO | R_PU_PG | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] PWR_GOOD 开漏上拉 (BQ25896 状态脚) |
| PWR_GOOD | J_CHG pin6 | NET_PWR_GOOD | NET_PWR_GOOD | 单端 | NET | 必装 | HINGE | [推算] |  | [PWR_GOOD] 附加节点 (同 net, 经 J_CHG 到主 PCB) |

## P3 启动存储
> ★ 只留焊盘位 + 串阻位, 不画存储芯片 (DRAM 已确认; **启动介质形态**待原厂 Q19)

### 功能块与判断
**这一页故意"空着" —— 但它是有依据的空, 不是漏画。**

- ★**官网已确认 ARS45 内置 512MB DRAM 且已量产** (另有 ARS48 1GB 已送样 / ARS41 128MB Q3 送样) → 所以本页只画 **4 条 SPI 信号 + 串阻位 + 焊盘位**, **不画存储芯片**。
- ★**"内置 DRAM" ≠ "内置 boot storage" (2026-10-27 审校补)**: DRAM 是内存、跟启动介质是两回事; 启动介质是 NOR 还是 eMMC **原厂没答 (Q19)** → 所以本页才"只留焊盘位"。原话说"启动介质必然外挂"是推论不是事实, 已改口径。
- 两种外挂形态的代价差别很大: **SPI-NOR** (小, 省板宽, 兆易创新是酷芯微第二大股东 → 生态顺) vs **eMMC** (容量大但吃板面积 → 我们评估板宽 12→15mm) ⇒ **这个选择直接顶到板宽**, 而板宽又被官网"宽度≤8mm"卡着 (见 §(1.25))。
- 串阻位 (0Ω) 的作用: 让 SoC 的启动介质可以换 NOR/eMMC 而**不改板** —— 两种都留位, 装配时决定。
- **[待原厂]**: 外挂是 SPI-NOR 还是 eMMC (TBD-06) · 挂在哪个接口 (SPI 控制器? eMMC/NAND 控制器?) (TBD-11) · 上电时序要求 (TBD-12)。★V1.1: 容量下限已由 SW 总工锁死 (ISS-080): `rootfs ≤30MB` → **flash ≥128MB** (64MB SPI-NOR 装不下) → 回信后选 ≥128MB 的 SPI-NOR 或 eMMC; 供电走 `VDD_3V3_IO` (200mA 够写入电流)。

### 器件表 (10 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| SPI_SCLK | SoC[TBD-01].SPI_SCLK | R_SER_SPI_SCLK | NET_SPI_SCLK | 0Ω (串阻位) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-06 | 启动存储: **只留焊盘位 + 串阻位, 不画存储芯片** (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +2 |
| SPI_SCLK_BOOT | R_SER_SPI_SCLK | J_BOOT1 pin1 | R_SER_SPI_SCLK | 0Ω (串阻位) | R | 必装 | MAIN_PCB | [待原厂] | TBD-06 | [SPI_SCLK_BOOT] SPI_SCLK 串阻位 (0Ω 调试用) |
| SPI_CSn | SoC[TBD-01].SPI_CSn | R_SER_SPI_CSn | NET_SPI_CSn | 0Ω (串阻位) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-06 | 启动存储: **只留焊盘位 + 串阻位, 不画存储芯片** (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +2 |
| SPI_CSn_BOOT | R_SER_SPI_CSn | J_BOOT1 pin2 | R_SER_SPI_CSn | 0Ω (串阻位) | R | 必装 | MAIN_PCB | [待原厂] | TBD-06 | [SPI_CSn_BOOT] SPI_CSn 串阻位 (0Ω 调试用) |
| SPI_MOSI | SoC[TBD-01].SPI_MOSI | R_SER_SPI_MOSI | NET_SPI_MOSI | 0Ω (串阻位) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-11 | 启动存储: **只留焊盘位 + 串阻位, 不画存储芯片** (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +2 |
| SPI_MOSI_BOOT | R_SER_SPI_MOSI | J_BOOT1 pin3 | R_SER_SPI_MOSI | 0Ω (串阻位) | R | 必装 | MAIN_PCB | [待原厂] | TBD-11 | [SPI_MOSI_BOOT] SPI_MOSI 串阻位 (0Ω 调试用) |
| SPI_MISO | SoC[TBD-01].SPI_MISO | R_SER_SPI_MISO | NET_SPI_MISO | 0Ω (串阻位) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-11 | 启动存储: **只留焊盘位 + 串阻位, 不画存储芯片** (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +2 |
| SPI_MISO_BOOT | R_SER_SPI_MISO | J_BOOT1 pin4 | R_SER_SPI_MISO | 0Ω (串阻位) | R | 必装 | MAIN_PCB | [待原厂] | TBD-11 | [SPI_MISO_BOOT] SPI_MISO 串阻位 (0Ω 调试用) |
| VDD_3V3_IO | J_BOOT1 pin5 | RAIL_VDD_3V3_IO | J_BOOT1 | 启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留) | CONN | 必装 | MAIN_PCB | [待原厂] | TBD-06 | [VDD_3V3_IO] ★内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认 (Q19) -> 只留焊盘位; pin5/pin6 预留外挂 SPI-NOR |
| GND | J_BOOT1 pin6 | GND | J_BOOT1 | 启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留) | CONN | 必装 | MAIN_PCB | [待原厂] | TBD-06 | 焊盘位 GND 预留 (外挂 SPI-NOR 用) |

## P4 显示双出口
> DSI 原生 / 桥接 互斥 8 个**逻辑** 0Ω 位 (P/N 拆开后实物 16 颗 0402); 走鹃Ⅱ 原生 800×600 (上采样 ×1.25)

### 功能块与判断
**这一页决定要不要多一颗桥接芯片 (100-300mW + 4-8 周采购 + PCB 面积)。**

- 走鹃Ⅱ 是 **800×600 原生** (官网+LEDinside+EET 三源一致) → 我们的链路是 **ISP 640×480 → OD letterbox → 640×640 → 显示上采样 ×1.25 → 800×600**, 正好对上; 老板锁的显示分辨率 800×600 与光引擎原生一致 ✅。
- ★**30° 是对角 FOV** (自洽校验: 对角 1000px ÷ 30° = 33.3 PPD) → 显示端原生角分辨率 0.030°/px 对角。显示端映射 (采集 120° → 显示 30°) 是 **Q23** 待老板拍板: (a) 全幅压进 30° (看得广但糊) (b) 30° 中心窗口 (看得清但窄, 但显示侧要 crop)。
- ★**8 个 0Ω 位 = 两条互斥路**: `R_SEL_*` (SoC 原生 DSI TX 直连光机) 与 `BR_*` (经桥接芯片) **不得同时装** (否则两个驱动源打架) → BOM 分两组列, 由装配决定。`R_SEL_D2/D3` 与 `R_TERM_*` 永远 DNP (2 lane 不够时再装; 端接 100Ω 对地, 0402 手工可补)。
- ★**"8 个 0Ω"是逻辑位, 实物是 16 颗 (2026-10-27 审校补)**: 规格 `display_select` 每条 lane 只给了**一颗** 0Ω (R_SEL_CK / R_SEL_D0 / …), 但**一颗 0Ω 串在差分对上会把 P/N 短接** → 每条必须拆 `_P` / `_N` 两颗。网表里已按 16 颗画 (R_SEL 5×2 + BR 3×2), BOM 别按 8 颗下单。
- ★**`U_BRIDGE` 到底是什么还没定 (2026-10-27 审校补)**: 规格 A-21 把这块叫"**redriver 位**", 而 P4 的 `BR_*` 又要求"桥接芯片输出 DSI 到光机" → 两者可能是同一颗 (DP→DSI 桥接) 也可能是两颗。**本版只留位不选型**, 型号随 TBD-04 + JBD 接口定义定。
- ★**显示 TX 的新证据**: 官网原文 "支持端到端 **3-4ms** 超低延迟显示链路" + "多屏异显" → **芯片内部确有显示输出通路**; 官网另有 "集成 Display Port 1.4" (但**没写方向**, 而媒体写 DP1.4 RX) ⇒ **推断: 极可能有显示 TX, 具体接口待定** → 所以**双出口必须都留**。
- **[待原厂]**: 有无 MIPI-DSI TX / DP1.4 是否有 TX / 能否同时工作 / lane 数与速率 (TBD-04) · DSI DDC I2C 是否独立于 SoC 通用 I2C (TBD-09)。

### 器件表 (49 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| DSI_D0_CK_P_SRC | SoC[TBD-01].DSI_TX_CK_P | R_SEL_CK_P | NET_DSI_D0_CK_P_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin3 + R_SEL_CK 0Ω; 测试点 TP_DSI_CK |
| DSI_D0_CK_P | R_SEL_CK_P | CONN_LIGHT pin1 | R_SEL_CK_P | 0Ω | R | 必装 | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_CK_P] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_CK_N_SRC | SoC[TBD-01].DSI_TX_CK_N | R_SEL_CK_N | NET_DSI_D0_CK_N_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin4 + R_SEL_CK 0Ω; 测试点 TP_DSI_CK |
| DSI_D0_CK_N | R_SEL_CK_N | CONN_LIGHT pin2 | R_SEL_CK_N | 0Ω | R | 必装 | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_CK_N] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D0_P_SRC | SoC[TBD-01].DSI_TX_D0_P | R_SEL_D0_P | NET_DSI_D0_D0_P_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin5 + R_SEL_D0; 测试点 TP_DSI_D0_P |
| DSI_D0_D0_P | R_SEL_D0_P | CONN_LIGHT pin3 | R_SEL_D0_P | 0Ω | R | 必装 | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D0_P] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D0_N_SRC | SoC[TBD-01].DSI_TX_D0_N | R_SEL_D0_N | NET_DSI_D0_D0_N_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin6 + R_SEL_D0; 测试点 TP_DSI_D0_N |
| DSI_D0_D0_N | R_SEL_D0_N | CONN_LIGHT pin4 | R_SEL_D0_N | 0Ω | R | 必装 | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D0_N] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D1_P_SRC | SoC[TBD-01].DSI_TX_D1_P | R_SEL_D1_P | NET_DSI_D0_D1_P_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin7 + R_SEL_D1; 测试点 — |
| DSI_D0_D1_P | R_SEL_D1_P | CONN_LIGHT pin5 | R_SEL_D1_P | 0Ω | R | 必装 | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D1_P] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D1_N_SRC | SoC[TBD-01].DSI_TX_D1_N | R_SEL_D1_N | NET_DSI_D0_D1_N_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin8 + R_SEL_D1; 测试点 — |
| DSI_D0_D1_N | R_SEL_D1_N | CONN_LIGHT pin6 | R_SEL_D1_N | 0Ω | R | 必装 | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D1_N] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D2_P_SRC | SoC[TBD-01].DSI_TX_D2_P | R_SEL_D2_P | NET_DSI_D0_D2_P_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin9 + R_SEL_D2 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D2_P | R_SEL_D2_P | CONN_LIGHT pin7 | R_SEL_D2_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D2_P] 4-lane 预留位 (2-lane 不够时再装) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D2_P_SRC | R_TERM_DSI_D0_D2_P | NET_DSI_D0_D2_P_SRC | R_TERM_DSI_D0_D2_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [DSI_D0_D2_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_DSI_D0_D2_P | GND | R_TERM_DSI_D0_D2_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D2_P 才装) |
| DSI_D0_D2_N_SRC | SoC[TBD-01].DSI_TX_D2_N | R_SEL_D2_N | NET_DSI_D0_D2_N_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin10/11/12 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D2_N | R_SEL_D2_N | CONN_LIGHT pin8 | R_SEL_D2_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D2_N] 4-lane 预留位 (2-lane 不够时再装) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D2_N_SRC | R_TERM_DSI_D0_D2_N | NET_DSI_D0_D2_N_SRC | R_TERM_DSI_D0_D2_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [DSI_D0_D2_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_DSI_D0_D2_N | GND | R_TERM_DSI_D0_D2_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D2_N 才装) |
| DSI_D0_D3_P_SRC | SoC[TBD-01].DSI_TX_D3_P | R_SEL_D3_P | NET_DSI_D0_D3_P_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin10/11/12 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D3_P | R_SEL_D3_P | CONN_LIGHT pin9 | R_SEL_D3_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D3_P] 4-lane 预留位 (2-lane 不够时再装) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D3_P_SRC | R_TERM_DSI_D0_D3_P | NET_DSI_D0_D3_P_SRC | R_TERM_DSI_D0_D3_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [DSI_D0_D3_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_DSI_D0_D3_P | GND | R_TERM_DSI_D0_D3_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D3_P 才装) |
| DSI_D0_D3_N_SRC | SoC[TBD-01].DSI_TX_D3_N | R_SEL_D3_N | NET_DSI_D0_D3_N_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin10/11/12 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D3_N | R_SEL_D3_N | CONN_LIGHT pin10 | R_SEL_D3_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_D0_D3_N] 4-lane 预留位 (2-lane 不够时再装) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_D0_D3_N_SRC | R_TERM_DSI_D0_D3_N | NET_DSI_D0_D3_N_SRC | R_TERM_DSI_D0_D3_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [DSI_D0_D3_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_DSI_D0_D3_N | GND | R_TERM_DSI_D0_D3_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D3_N 才装) |
| DSI_BR_CK_P_SRC | U_BRIDGE pin1 | BR_CK_P | BR_CK_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_CK_P_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_CK_P | BR_CK_P | CONN_LIGHT pin11 | BR_CK_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_CK_P] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_CK_N_SRC | U_BRIDGE pin2 | BR_CK_N | BR_CK_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_CK_N_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_CK_N | BR_CK_N | CONN_LIGHT pin12 | BR_CK_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_CK_N] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D0_P_SRC | U_BRIDGE pin3 | BR_D0_P | BR_D0_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D0_P_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D0_P | BR_D0_P | CONN_LIGHT pin13 | BR_D0_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D0_P] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D0_N_SRC | U_BRIDGE pin4 | BR_D0_N | BR_D0_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D0_N_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D0_N | BR_D0_N | CONN_LIGHT pin14 | BR_D0_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D0_N] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D1_P_SRC | U_BRIDGE pin5 | BR_D1_P | BR_D1_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D1_P_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D1_P | BR_D1_P | CONN_LIGHT pin15 | BR_D1_P | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D1_P] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D1_N_SRC | U_BRIDGE pin6 | BR_D1_N | BR_D1_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D1_N_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D1_N | BR_D1_N | CONN_LIGHT pin16 | BR_D1_N | 0Ω | R | DNP | MAIN_PCB | [官方] | TBD-04 | [DSI_BR_D1_N] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR | U_BRIDGE | DSI_BR_CK_P_SRC | U_BRIDGE | [待选型] DP1.4 TX · MIPI DSI TX 桥接芯片 (方案B 专用; 与 P6 同一位) | IC | DNP | MAIN_PCB | [推算] | TBD-04 | [DSI_BR] 方案B 才需要的桥接芯片位 (接口类型/功耗/封装随原厂 TBD-04 结论定; 本版只留位不选型) |
| I2C_B_SCL | SoC[TBD-01].I2C_B_SCL | R_PU_I2CB_SCL | NET_I2C_B_SCL | 上拉 4.7k, 放主板侧 | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 双向; 电平 3.3V; 阻抗 上拉 4.7k, 放主板侧; 连接 CONN_LIGHT pin13 → 光机; 测试点 TP_I2CB_SCL |
| I2C_B_SDA | SoC[TBD-01].I2C_B_SDA | R_PU_I2CB_SDA | NET_I2C_B_SDA | 上拉 4.7k, 放主板侧 | NET | 必装 | MAIN_PCB | [推算] | TBD-04 | 方向 双向; 电平 3.3V; 阻抗 上拉 4.7k, 放主板侧; 连接 CONN_LIGHT pin14 → 光机; 测试点 TP_I2CB_SDA |
| I2C_B_SCL | CONN_LIGHT pin17 | NET_I2C_B_SCL | NET_I2C_B_SCL | 上拉 4.7k, 放主板侧 | NET | 必装 | HINGE | [推算] | TBD-04 | [I2C_B_SCL] 附加节点 (同 net) |
| I2C_B_SDA | CONN_LIGHT pin18 | NET_I2C_B_SDA | NET_I2C_B_SDA | 上拉 4.7k, 放主板侧 | NET | 必装 | HINGE | [推算] | TBD-04 | [I2C_B_SDA] 附加节点 (同 net) |
| VDD_3V3_IO | R_PU_I2CB_SCL | RAIL_VDD_3V3_IO | R_PU_I2CB_SCL | 4.7k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] DSI DDC 上拉 (放主板侧) |
| VDD_3V3_IO | R_PU_I2CB_SDA | RAIL_VDD_3V3_IO | R_PU_I2CB_SDA | 4.7k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] DSI DDC 上拉 |
| CONN_LIGHT | CONN_LIGHT | CONN_LIGHT pin1 | CONN_LIGHT | 1×22p@0.5mm 光机连接器 (板对板/FFC, 待 JBD 确认; 末脚 GND = 差分回流) | CONN | 必装 | HINGE | [待JBD] | TBD-04 | [INVENTORY] [CONN_LIGHT] 光机↔主板连接器; pin3/4=DSI_CK, 5/6=DSI_D0, 7/8=DSI_D1, 9/10=DSI_D2, 11/ |
| GND | CONN_LIGHT pin22 | GND | CONN_LIGHT | 跨铰链回流地 (独立脚) | NET | 必装 | HINGE | [推算] | TBD-04 | [GND] ★V1.6 补: CONN_LIGHT 原来 21 个脚里**一个 GND 都没有** · DSI 差分无回流路径 (跨铰链 100Ω 差分必须与地成对) · 22p  |

## P5 MIPI-CSI 传感器
> CONN_CAM 40p 跨铰链; 4-lane 预留; AC 耦合 + 对地端接

### 功能块与判断
**传感器侧: 跨铰链的差分对, 全部 100Ω 差分 + AC 耦合位 + 对地端接位。**

- 4-lane CSI: `A-01..A-10` (CK + D0..D3), 其中 **D2/D3 是 DNP (预留 4-lane)** —— 我们只用 1080p60 单路, 2-lane 就够, 但**预留 4-lane 是为了让"以后换高分辨率 sensor"不用改板**。
- 跨铰链是这里最脆的一环: `CONN_CAM` 40p 走铰链 → 阻抗连续性、AC 耦合电容位置、对地端接位置都要跟结构侧的铰链行程对齐 (ISS-065 的结构建议里提了这一条)。
- 传感器电源 3 条轨 (`SENSOR_AVDD` 2.8V / `SENSOR_VDD_IO` 1.8V / `SENSOR_CORE` 1.2V) 由 3 路 TPS7A20 LDO 供, **都在镜框侧** (不进镜腿皮肤路径) → 这也是散热账里"镜腿内发热量 0.90W"能成立的原因。
- ★**MCLK 的串阻位必留 (2026-10-27 审校补)**: MCLK 是时钟输出, `R_SER_CSI_MCLK` 这个位**必须焊上** (兼做源端匹配/阻尼), 只是**值**待 TBD-03 的 MCLK 电平定 —— 所以这一行标"必装 + 值待原厂", 不是 "DNP"。标错成 DNP = 装板时不焊 → MCLK 裸奔。
- ★**传感器选型还锁着 3 件事** (Q16 宽高比 / Q24 准入线 / sensor 必须支持**全幅**输出模式): 裸 1080p 对 OV04C10 就是 ROI 模式 (对角 FOV 120°→85.61°), 违反我们"禁 ROI"的硬约束 → **只有 1080p ROI 模式的 sensor 一票否决**。
- **[待原厂]**: CSI lane 数 / 每 lane 速率 / 电压域 / AC 耦合是否内置 / MCLK 电压 (TBD-03)。

### 器件表 (38 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| CSI_D0_CK_P_SRC | SoC[TBD-01].CSI_D0_CK_P | C_AC_CSI_D0_CK_P | NET_CSI_D0_CK_P_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 CONN_CAM 40p (跨铰链) + AC 耦合电容位; 测试点 TP_C |
| CSI_D0_CK_P | C_AC_CSI_D0_CK_P | CONN_CAM pin1 | C_AC_CSI_D0_CK_P | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_CK_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_CK_N_SRC | SoC[TBD-01].CSI_D0_CK_N | C_AC_CSI_D0_CK_N | NET_CSI_D0_CK_N_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 TP_CSI_CK_N |
| CSI_D0_CK_N | C_AC_CSI_D0_CK_N | CONN_CAM pin2 | C_AC_CSI_D0_CK_N | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_CK_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D0_P_SRC | SoC[TBD-01].CSI_D0_D0_P | C_AC_CSI_D0_D0_P | NET_CSI_D0_D0_P_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 TP_CSI_D0_P |
| CSI_D0_D0_P | C_AC_CSI_D0_D0_P | CONN_CAM pin3 | C_AC_CSI_D0_D0_P | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D0_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D0_N_SRC | SoC[TBD-01].CSI_D0_D0_N | C_AC_CSI_D0_D0_N | NET_CSI_D0_D0_N_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 TP_CSI_D0_N |
| CSI_D0_D0_N | C_AC_CSI_D0_D0_N | CONN_CAM pin4 | C_AC_CSI_D0_D0_N | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D0_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D1_P_SRC | SoC[TBD-01].CSI_D0_D1_P | C_AC_CSI_D0_D1_P | NET_CSI_D0_D1_P_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 — |
| CSI_D0_D1_P | C_AC_CSI_D0_D1_P | CONN_CAM pin5 | C_AC_CSI_D0_D1_P | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D1_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D1_N_SRC | SoC[TBD-01].CSI_D0_D1_N | C_AC_CSI_D0_D1_N | NET_CSI_D0_D1_N_SRC | 100Ω ±10% | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 — |
| CSI_D0_D1_N | C_AC_CSI_D0_D1_N | CONN_CAM pin6 | C_AC_CSI_D0_D1_N | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D1_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D2_P_SRC | SoC[TBD-01].CSI_D0_D2_P | C_AC_CSI_D0_D2_P | NET_CSI_D0_D2_P_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D2_P | C_AC_CSI_D0_D2_P | CONN_CAM pin7 | C_AC_CSI_D0_D2_P | 100nF ±10% | C | DNP | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D2_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D2_P_SRC | R_TERM_CSI_D0_D2_P | NET_CSI_D0_D2_P_SRC | R_TERM_CSI_D0_D2_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [CSI_D0_D2_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_CSI_D0_D2_P | GND | R_TERM_CSI_D0_D2_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D2_P 才装) |
| CSI_D0_D2_N_SRC | SoC[TBD-01].CSI_D0_D2_N | C_AC_CSI_D0_D2_N | NET_CSI_D0_D2_N_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D2_N | C_AC_CSI_D0_D2_N | CONN_CAM pin8 | C_AC_CSI_D0_D2_N | 100nF ±10% | C | DNP | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D2_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D2_N_SRC | R_TERM_CSI_D0_D2_N | NET_CSI_D0_D2_N_SRC | R_TERM_CSI_D0_D2_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [CSI_D0_D2_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_CSI_D0_D2_N | GND | R_TERM_CSI_D0_D2_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D2_N 才装) |
| CSI_D0_D3_P_SRC | SoC[TBD-01].CSI_D0_D3_P | C_AC_CSI_D0_D3_P | NET_CSI_D0_D3_P_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D3_P | C_AC_CSI_D0_D3_P | CONN_CAM pin9 | C_AC_CSI_D0_D3_P | 100nF ±10% | C | DNP | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D3_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D3_P_SRC | R_TERM_CSI_D0_D3_P | NET_CSI_D0_D3_P_SRC | R_TERM_CSI_D0_D3_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [CSI_D0_D3_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_CSI_D0_D3_P | GND | R_TERM_CSI_D0_D3_P | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D3_P 才装) |
| CSI_D0_D3_N_SRC | SoC[TBD-01].CSI_D0_D3_N | C_AC_CSI_D0_D3_N | NET_CSI_D0_D3_N_SRC | 100Ω ±10% | NET | DNP | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D3_N | C_AC_CSI_D0_D3_N | CONN_CAM pin10 | C_AC_CSI_D0_D3_N | 100nF ±10% | C | DNP | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_D3_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位改 DNP, 未内置必须装 |
| CSI_D0_D3_N_SRC | R_TERM_CSI_D0_D3_N | NET_CSI_D0_D3_N_SRC | R_TERM_CSI_D0_D3_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | [CSI_D0_D3_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| GND | R_TERM_CSI_D0_D3_N | GND | R_TERM_CSI_D0_D3_N | 100Ω ±1% | R | DNP | MAIN_PCB | [推算] |  | 未用差分对 100Ω 对地端接 (D3_N 才装) |
| CSI_MCLK_SRC | SoC[TBD-01].CSI_MCLK | R_SER_CSI_MCLK | NET_CSI_MCLK_SRC | 单端, 需包地 | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 [待原厂]; 阻抗 单端, 需包地; 连接 CONN_CAM; 单独包地, 与电源并行 ≤5mm, 间距 ≥3mm; 测试点 TP_MCLK |
| CSI_MCLK | R_SER_CSI_MCLK | CONN_CAM pin11 | R_SER_CSI_MCLK | [待原厂] | R | 必装 | MAIN_PCB | [待原厂] | TBD-03 | [CSI_MCLK] MCLK 串阻位 (**位必留**: MCLK 是时钟输出, 串阻兼做源端匹配/阻尼); 值随 TBD-03 的 MCLK 电平与速率定, 不写死 |
| CSI_RESET_N | SoC[TBD-01].CSI_RESET_N | R_PU_CSI_RST | NET_CSI_RESET_N | 单端, 10k 上拉 | NET | 必装 | MAIN_PCB | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.8V [待原厂]; 阻抗 单端, 10k 上拉; 连接 CONN_CAM; 测试点 TP_CSI_RST |
| VDD_1V8_IO | R_PU_CSI_RST | RAIL_VDD_1V8_IO | R_PU_CSI_RST | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] CSI_RESET_N 上拉 (1.8V 域) |
| CSI_RESET_N | CONN_CAM pin12 | NET_CSI_RESET_N | NET_CSI_RESET_N | 单端, 10k 上拉 | NET | 必装 | HINGE | [待原厂] | TBD-03 | [CSI_RESET_N] 附加节点 (同 net) |
| SENSOR_AVDD | RAIL_SENSOR_AVDD | CONN_CAM pin15 | NET_SENSOR_AVDD | 2.8V | NET | 必装 | HINGE | [官方] |  | [SENSOR_AVDD] sensor 供电 接 CONN_CAM pin15 (跨铰链, 走线与 MCLK 并行 ≤5mm, 间距 ≥3mm) |
| SENSOR_VDD_IO | RAIL_SENSOR_VDD_IO | CONN_CAM pin16 | NET_SENSOR_VDD_IO | 1.8V | NET | 必装 | HINGE | [官方] |  | [SENSOR_VDD_IO] sensor 供电 接 CONN_CAM pin16 (跨铰链, 走线与 MCLK 并行 ≤5mm, 间距 ≥3mm) |
| SENSOR_CORE | RAIL_SENSOR_CORE | CONN_CAM pin17 | NET_SENSOR_CORE | 1.2V | NET | 必装 | HINGE | [官方] |  | [SENSOR_CORE] sensor 供电 接 CONN_CAM pin17 (跨铰链, 走线与 MCLK 并行 ≤5mm, 间距 ≥3mm) |
| CONN_CAM | CONN_CAM | CONN_CAM pin1 | CONN_CAM | 18p@0.5mm 跨铰链连接器 (型号待结构确认; pin1/2=CK, 3-10=D0-D3, 11=MCLK, 12=RESET, 13/14=I2C_A, 15-17=三条电源, 18=GND) | CONN | 必装 | HINGE | [推算] | TBD-03 | [INVENTORY] [CONN_CAM] 主 PCB ↔ sensor 板 40p 跨铰链连接器; pin1/2=CSI_CK, 3..10=CSI_D0..D3, 11=MC |
| GND | CONN_CAM pin18 | GND | CONN_CAM | 跨铰链回流地 (独立 pin) | NET | 必装 | HINGE | [推算] | TBD-03 | [GND] ★CONN_CAM 18p 的第 18 脚 = 跨铰链回流地 (不与电源共脚 · 环路面积最小); 17 脚电源 16 脚是 SENSOR_CORE 1.2V |

## P6 高速差分与连接器
> DP_TX 4 lane / USB 2.0 (★差分跨铰链) / Type-C CC

### 功能块与判断
**高速差分与连接器: 板宽与 pitch 的风险都集中在这几页, 而且这一页有一个没解的架构冲突。**

- ★★**USB 差分对必然跨铰链 —— 这是本方案最大的未解项 (2026-10-27 审校补)**: Type-C 座在**充电板 (=镜框)**, 而 USB D+/D- 的对端是**主 PCB (=镜脚)** 里的 SoC → 这对差分线**必须跨铰链**。USB 2.0 (以及官网说的 USB 3.0 → 还要 4 根 SS 差分) 跨铰链 = 阻抗不连续 + 摆臂抖动 = 眼图直接废掉, 而 Type-C 恰恰是我们**烧录/调试的唯一外露口**。
  - 两条出路: **(a) 把 Type-C 挪到主 PCB (镜脚) 侧**, 充电 IC 留在充电板, 让**电池大电流线**跨铰链 (低频大电流比高速差分好过得多); **(b) 保持 Type-C 在充电板**, 但调试通道改走板上 `J_DEBUG` (1×4) / `J_UART` (1×2) 排针, Type-C 只做充电不做调试。
  - 本版处理: `CONN_USB` (4p USB 跨铰链连接器) **位必留** (不焊也要留焊盘), 并且 Type-C 座按"在充电板"画。**方案 (a)/(b) 选哪个 → 请项目总工 + 结构总工拍板** (走接口请求, 不直接联系结构总工)。
- `A-21` DP_TX 4 lane: 主 PCB 内部走线 + `U_BRIDGE` 位 (0402 串阻 **8 颗** = 4 lane × P/N, 规格写的"×4"是按 lane 算的) + 对地电容位 ×4 —— 走线是 8×10mm 芯片**逃线**的主要出口, 也是"宽度≤8mm 硬约束"最吃紧的地方。
- `USB_D+/D-` 走 Type-C (跨铰链, 见上) + `USB_CC1/CC2` (Rd 5.1k 下拉, 接 PD 控制器时由控制器接管) —— 我们**第一版不上无线**, USB 只做充电/调试通道。
- ★**USB 差分阻抗 90Ω 是对的, 不要改成 100Ω**: USB 2.0 D+/D- 的差分阻抗规范就是 **90Ω ±10%**, 和 MIPI/DSI 的 100Ω ±10% **不是同一个模板**; 规格 B-21/B-22 写的就是 90Ω。统一成 100Ω = 规格被改坏。
- ★**本轮网上查证标红的一条**: 官网说"封装尺寸须压缩至**宽度≤8mm**" + 8×10mm FCCSP **集成 DRAM** 的球间距通常 0.4-0.5mm [推算] → **我们 12mm 板宽 + 4-6 层叠层假设可能过于乐观** ⇒ **ISS-078 (blocker) 要按 pitch 0.3/0.4/0.5mm 三档重算**。这页的走线密度在 pitch 变大时会先崩。
- **[待原厂]**: FCCSP pitch + 完整球位图 + 逃线参考布局 (TBD-05) + AR9481 同 Die 代理资料 · USB PHY 版本与引脚数 (TBD-10) · `U_BRIDGE` 到底是 redriver 还是 DP→DSI 桥接 (TBD-04)。
- ★**V1.1 已把 `U_BRIDGE` 定位统一**: 之前 P4 写"DSI→光机桥接芯片"、P6 写"DP→DSI 桥接芯片" —— **同一颗芯片两种说法 = BOM 会对不上**。现在统一为 **DP1.4 TX → MIPI DSI TX 桥接芯片 (方案B 专用)**, `redriver` 作为候选兼列 (若原厂给的是 DP TX 而光机吃 DSI, 那就得靠它转)。
- ★**V1.1 显示 TX 公开渠道穷举结论 (ISS-083)**: ① 官网产品页对 ARS45 **只字未提显示接口**; ② 官网「智能可穿戴」应用页写"集成 **Display Port 1.4** 与 **USB 3.0**" [官网·方案级, 未说 TX/RX 方向]; ③ 百度百科写"**DP1.4 RX**" [媒体级]; ④ **没有任何官方渠道出现 "DSI" 字样** → ⇒ **"ARS45 原生带 DSI TX" 至今未证实** ⇒ **双出口互斥 (R_SEL_* vs BR_*) 必须保留, 桥接芯片 fallback 不能删** (采购周期 4-8 周, 不能等回信)。⑤ 官网确认"集成 USB 3.0" → 但 **USB 3.0 的 SS 差分绝不能跨铰链** (4 对差分 + 刚度要求) ⇒ Type-C 座按 **16p (USB2 + 充电)** 定, 烧录走 USB 2.0 D+/D− (P6)。

### 器件表 (45 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| DP_TX_A0_P_SRC | SoC[TBD-01].DP_TX_A0_P | R_SER_DP_A0_P | NET_DP_TX_A0_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A0_P | R_SER_DP_A0_P | U_BRIDGE pin21 | R_SER_DP_A0_P | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A0_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A0_P_SRC | C_AC_DP_A0_P | R_SER_DP_A0_P | C_AC_DP_A0_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A0_P_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A0_P | GND | C_AC_DP_A0_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A0_P_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX_A0_N_SRC | SoC[TBD-01].DP_TX_A0_N | R_SER_DP_A0_N | NET_DP_TX_A0_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A0_N | R_SER_DP_A0_N | U_BRIDGE pin22 | R_SER_DP_A0_N | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A0_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A0_N_SRC | C_AC_DP_A0_N | R_SER_DP_A0_N | C_AC_DP_A0_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A0_N_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A0_N | GND | C_AC_DP_A0_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A0_N_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX_A1_P_SRC | SoC[TBD-01].DP_TX_A1_P | R_SER_DP_A1_P | NET_DP_TX_A1_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A1_P | R_SER_DP_A1_P | U_BRIDGE pin23 | R_SER_DP_A1_P | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A1_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A1_P_SRC | C_AC_DP_A1_P | R_SER_DP_A1_P | C_AC_DP_A1_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A1_P_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A1_P | GND | C_AC_DP_A1_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A1_P_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX_A1_N_SRC | SoC[TBD-01].DP_TX_A1_N | R_SER_DP_A1_N | NET_DP_TX_A1_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A1_N | R_SER_DP_A1_N | U_BRIDGE pin24 | R_SER_DP_A1_N | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A1_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A1_N_SRC | C_AC_DP_A1_N | R_SER_DP_A1_N | C_AC_DP_A1_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A1_N_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A1_N | GND | C_AC_DP_A1_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A1_N_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX_A2_P_SRC | SoC[TBD-01].DP_TX_A2_P | R_SER_DP_A2_P | NET_DP_TX_A2_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A2_P | R_SER_DP_A2_P | U_BRIDGE pin25 | R_SER_DP_A2_P | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A2_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A2_P_SRC | C_AC_DP_A2_P | R_SER_DP_A2_P | C_AC_DP_A2_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A2_P_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A2_P | GND | C_AC_DP_A2_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A2_P_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX_A2_N_SRC | SoC[TBD-01].DP_TX_A2_N | R_SER_DP_A2_N | NET_DP_TX_A2_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A2_N | R_SER_DP_A2_N | U_BRIDGE pin26 | R_SER_DP_A2_N | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A2_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A2_N_SRC | C_AC_DP_A2_N | R_SER_DP_A2_N | C_AC_DP_A2_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A2_N_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A2_N | GND | C_AC_DP_A2_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A2_N_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX_A3_P_SRC | SoC[TBD-01].DP_TX_A3_P | R_SER_DP_A3_P | NET_DP_TX_A3_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A3_P | R_SER_DP_A3_P | U_BRIDGE pin27 | R_SER_DP_A3_P | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A3_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A3_P_SRC | C_AC_DP_A3_P | R_SER_DP_A3_P | C_AC_DP_A3_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A3_P_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A3_P | GND | C_AC_DP_A3_P | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A3_P_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX_A3_N_SRC | SoC[TBD-01].DP_TX_A3_N | R_SER_DP_A3_N | NET_DP_TX_A3_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-04 | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A3_N | R_SER_DP_A3_N | U_BRIDGE pin28 | R_SER_DP_A3_N | 100Ω ±10% | R | 必装 | MAIN_PCB | [待原厂] |  | [DP_TX_A3_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A3_N_SRC | C_AC_DP_A3_N | R_SER_DP_A3_N | C_AC_DP_A3_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] | TBD-04 | [DP_TX_A3_N_SRC] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路共用一颗且 N 路错接到 P 路 |
| GND | C_AC_DP_A3_N | GND | C_AC_DP_A3_N | [待选型] | C | DNP | MAIN_PCB | [待原厂] |  | [DP_TX_A3_N_SRC] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上) |
| DP_TX | U_BRIDGE | DP_TX_A0_P_SRC | U_BRIDGE | [待选型] DP1.4 TX · MIPI DSI TX 桥接芯片 (方案B 专用; 候选 redriver 兼列) | IC | DNP | MAIN_PCB | [推算] | TBD-04 | [DP_TX] 方案B 才需要: SoC DP_TX 4 lane 进桥接芯片, DSI 出桥接芯片走 BR_* 到光机; **方案A (SoC 原生 DSI) 下整条链冗余 ·  |
| USB_D_P_SRC | SoC[TBD-01].USB_D_P | R_SER_USB_D_P | NET_USB_D_P_SRC | 90Ω ±10% (与 MIPI 不同模板!) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-10 | 方向 SoC↔Type-C; 电平 3.3V [待原厂]; 阻抗 90Ω ±10% (与 MIPI 不同模板!); 连接 Type-C → 主 PCB (跨铰链则经 CONN_US |
| USB_D_N_SRC | SoC[TBD-01].USB_D_N | R_SER_USB_D_N | NET_USB_D_N_SRC | 90Ω ±10% | NET | 必装 | MAIN_PCB | [待原厂] | TBD-10 | 方向 SoC↔Type-C; 电平 3.3V [待原厂]; 阻抗 90Ω ±10%; 连接 同上; 测试点 TP_USB_D- |
| USB_D_P | R_SER_USB_D_P | CONN_USB pin1 | R_SER_USB_D_P | 22Ω ±1% | R | 必装 | MAIN_PCB | [推算] | TBD-10 | [USB_D_P] USB 2.0 源端串阻 (D+, 22Ω 放在**主板侧 SoC 端**); ★V1.1 修: V1 把 D+ 直接接 J_TYPE_C pin4 = **把 |
| USB_D_N | R_SER_USB_D_N | CONN_USB pin2 | R_SER_USB_D_N | 22Ω ±1% | R | 必装 | MAIN_PCB | [推算] | TBD-10 | [USB_D_N] USB 2.0 源端串阻 (D-, 主板侧); ★V1.1 修: 同上, 改接 CONN_USB pin2 |
| USB_CC1 | J_TYPE_C A5 | R_CC1 | NET_USB_CC1 | Rd 5.1k 到 GND ×2 (PD sink 时由 TPS25730 接管) | NET | 必装 | CHG_BOARD | [推算] | TBD-10 | 方向 Type-C→PD控制器; 电平 —; 阻抗 Rd 5.1k 到 GND ×2 (PD sink 时由 TPS25730 接管); 连接 Type-C; 测试点 — |
| USB_CC2 | J_TYPE_C B5 | R_CC2 | R_CC2 | 5.1k ±1% | R | 必装 | CHG_BOARD | [推算] |  | [USB_CC2] Type-C Rd (非 PD 时下拉; 接 PD 控制器时由控制器接管) |
| GND | R_CC1 | GND | R_CC1 | 5.1k ±1% | R | 必装 | CHG_BOARD | [推算] |  | Type-C Rd 下拉端 |
| GND | R_CC2 | GND | R_CC2 | 5.1k ±1% | R | 必装 | CHG_BOARD | [推算] |  | Type-C Rd 下拉端 |
| USB_CC2 | USB_CC2 | J_TYPE_C B5 | NET_USB_CC2 | 单端 | NET | 必装 | CHG_BOARD | [推算] |  | [USB_CC2] CC2 网节点 (同 net) |
| GND | J_TYPE_C A1+A12+B1+B12 | GND | J_TYPE_C | Type-C 16p 座 (物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | Type-C GND 脚 (★V1.5 修正: USB-IF 16p 的 GND 是 **A1/A12/B1/B12 四个脚**, 原来只接 A1+A12 · B1/B12 悬空  |
| GND | J_TYPE_C shield | GND | J_TYPE_C | Type-C 16p 座 (物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | Type-C 屏蔽壳 接 GND (单点, 与机壳地的接法待结构定) |
| CONN_USB | CONN_USB | CONN_USB pin1 | CONN_USB | 4p@0.5mm USB 跨铰链连接器 (D+/D-/GND/预留) | CONN | 必装 | HINGE | [推算] |  | [INVENTORY] [CONN_USB] ★USB 差分对**必然跨铰链** (Type-C 在充电板=镜框, SoC 在主 PCB=镜脚) · 本位必留; ⚠️ USB 2. |

## P7 板级接口与测试点
> 13 个逻辑 TP (展开 **40 个物理测点**) + 4 个按键位 + 3 LED + ID 跳线

### 功能块与判断
**测试点是这台样机的"仪器接口" —— 测点决定了我们能不能在 G3 测出真数。**

- ★**"13 个 TP" 是逻辑数, 物理是 40 个测点 (2026-10-27 审校补)**: 规格 `testpoints` 只有 13 条, 因为把"差分对/多轨"合并写了 (如 `TP_SENSOR_3V3/1V8/2V8` 展开成 3 个)。实际清单 = **5 条电源** (VBUS / SYS / BAT / VCORE / VIO) + **3 条 sensor 轨** + **1 条光机轨** (TP_LIGHT_3V3) + **6 条 CSI** (CK_P/N, D0_P/N, RST, MCLK) + **4 条 DSI** (CK_P/N, D0_P/N) + **4 条 I2C** (I2C_A/B 各 SCL/SDA) + **2 条 USB** (D_P/N) + FSIN / CHG_STAT / PG / ID / LED×3 / KEY×3 / RESET / BOOT / JTAG / UART → **合计 40 个**。原叙述里"5 电源 + 3 sensor + 3 光机 + 2 DDC"的拆分漏掉了 CSI/DSI/USB/FSIN/CHG/ID/LED/KEY/复位/调试, 已改。
- ★**按键是 4 个位不是 3 个 (2026-10-27 审校补)**: PWR / VOL+ / VOL- 装, **CAM 键焊盘必留不装** (规格 B-18); 另外每个键都加了 **RC 消抖电容** (10k 上拉 + 100nF, τ≈1ms) —— 消抖要不要由 SW 总工定, 但**位先留**, 后加要重来板。
- ★**LED 蓝是 DNP (第一版不上无线)**, 而且**串阻 `R_LED_B` 也一起 DNP** (BOM 干净, 后装时补这两颗); 红/绿必装。
- **每个 TP 都在 §位置 写明"量哪个脚、离多远"**; 形式上只有 `TP_VBUS` 是"测试点 + π 滤波后"取样, 其余是直接取样 —— **不是全部都走 π 滤波** (原叙述写错了)。
- ★**这一页决定了三个硬指标能不能从"推算"变成"实测"**: 端到端 (`TP_FSIN` + 串口打点) · 皮肤温度 (热电偶) · 充电态温度 (`TP_CHG_STAT` + `TP_VBUS`)。**没这些点, EVT 只能写"未验"**。
- 第一台样机不贴这些点会返工 (后续加板要重来), 所以清单里明确标"第一台样机没有这些, 后期加板要重来"。
- **[待原厂]**: 帧同步能否引出 (TBD-07) · 充电状态能否读回 (TBD-08, 已有 TP 兜底, 不卡项目)。

### 器件表 (77 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| ID_DETECT_0 | SoC[TBD-01].ID0 | R_PU_ID0 | NET_ID_DETECT_0 | GPIO 编码 (2 位) | NET | 必装 | MAIN_PCB | [推算] |  | 方向 板级→SoC; 电平 3.3V; 阻抗 GPIO 编码 (2 位); 连接 主 PCB (焊盘跳线); 测试点 TP_ID |
| ID_DETECT_0 | R_ID_JMP0 | NET_ID_DETECT_0 | R_ID_JMP0 | 0Ω (跳线位) | R | DNP | MAIN_PCB | [推算] |  | [ID_DETECT_0] 板级 ID 位 0 跳线位 (焊盘跳线编码 2 位) |
| VDD_3V3_IO | R_PU_ID0 | RAIL_VDD_3V3_IO | R_PU_ID0 | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 板级 ID 位 0 上拉 |
| GND | R_ID_JMP0 | GND | R_ID_JMP0 | 0Ω (跳线位) | R | DNP | MAIN_PCB | [推算] |  | ID 跳线位 0 -> GND (装上 = 该位 0) |
| ID_DETECT_1 | SoC[TBD-01].ID1 | R_PU_ID1 | NET_ID_DETECT_1 | GPIO 编码 (2 位) | NET | 必装 | MAIN_PCB | [推算] |  | 方向 板级→SoC; 电平 3.3V; 阻抗 GPIO 编码 (2 位); 连接 主 PCB (焊盘跳线); 测试点 TP_ID |
| ID_DETECT_1 | R_ID_JMP1 | NET_ID_DETECT_1 | R_ID_JMP1 | 0Ω (跳线位) | R | DNP | MAIN_PCB | [推算] |  | [ID_DETECT_1] 板级 ID 位 1 跳线位 (焊盘跳线编码 2 位) |
| VDD_3V3_IO | R_PU_ID1 | RAIL_VDD_3V3_IO | R_PU_ID1 | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 板级 ID 位 1 上拉 |
| GND | R_ID_JMP1 | GND | R_ID_JMP1 | 0Ω (跳线位) | R | DNP | MAIN_PCB | [推算] |  | ID 跳线位 1 -> GND (装上 = 该位 0) |
| LED_R | SoC[TBD-01].LED_R | R_LED_R | NET_LED_R | 1k 串阻 → LED → GND | NET | 必装 | MAIN_PCB | [推算] |  | 方向 SoC→LED; 电平 3.3V; 阻抗 1k 串阻 → LED → GND; 连接 主 PCB; 测试点 TP_LED_R |
| LED_R_D | R_LED_R | D_LED_R | R_LED_R | 1k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [LED_R_D] LED_R 串阻 (3.3V 驱动; 实际值随 LED Vf 与目标亮度定) |
| GND | D_LED_R | GND | D_LED_R | LED (待选型) | LED | 必装 | MAIN_PCB | [推算] |  | LED_R 阴极 -> GND |
| LED_G | SoC[TBD-01].LED_G | R_LED_G | NET_LED_G | 1k 串阻 → LED → GND | NET | 必装 | MAIN_PCB | [推算] |  | 方向 SoC→LED; 电平 3.3V; 阻抗 1k 串阻 → LED → GND; 连接 主 PCB; 测试点 TP_LED_G |
| LED_G_D | R_LED_G | D_LED_G | R_LED_G | 1k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [LED_G_D] LED_G 串阻 (3.3V 驱动; 实际值随 LED Vf 与目标亮度定) |
| GND | D_LED_G | GND | D_LED_G | LED (待选型) | LED | 必装 | MAIN_PCB | [推算] |  | LED_G 阴极 -> GND |
| LED_B | SoC[TBD-01].LED_B | R_LED_B | NET_LED_B | 1k 串阻 → LED → GND | NET | DNP | MAIN_PCB | [推算] |  | 方向 SoC→LED; 电平 3.3V; 阻抗 1k 串阻 → LED → GND; 连接 主 PCB; 测试点 TP_LED_B |
| LED_B_D | R_LED_B | D_LED_B | R_LED_B | 1k ±1% | R | DNP | MAIN_PCB | [推算] |  | [LED_B_D] LED_B 串阻 (3.3V 驱动; 实际值随 LED Vf 与目标亮度定) |
| GND | D_LED_B | GND | D_LED_B | LED (待选型) | LED | DNP | MAIN_PCB | [推算] |  | LED_B 阴极 -> GND |
| KEY_PWR | SoC[TBD-01].KEY_PWR | R_KEY_PWR | NET_KEY_PWR | 上拉 10k, 按下到 GND, 支持长按 | NET | 必装 | MAIN_PCB | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 上拉 10k, 按下到 GND, 支持长按; 连接 主 PCB; 测试点 TP_KEY_PWR |
| KEY_PWR | SW_KEY_PWR | NET_KEY_PWR | SW_KEY_PWR | 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | [KEY_PWR] 电源键 按键 |
| VDD_3V3_IO | R_KEY_PWR | RAIL_VDD_3V3_IO | R_KEY_PWR | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 电源键 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_PWR | GND | SW_KEY_PWR | 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | 电源键 另一端 -> GND |
| KEY_PWR | C_KEY_PWR | GND | C_KEY_PWR | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [KEY_PWR] 按键 RC 消抖电容 (10k 上拉 + 100nF, τ≈1ms); 是否需要消抖取决于 SoC 驱动方式 (等 SW 总工确认, 不影响本版布线) |
| KEY_VOL_P | SoC[TBD-01].KEY_VOL_P | R_KEY_VP | NET_KEY_VP | 同上 | NET | 必装 | MAIN_PCB | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 同上; 连接 主 PCB; 测试点 TP_KEY_VP |
| KEY_VOL_P | SW_KEY_VP | NET_KEY_VP | SW_KEY_VP | 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | [KEY_VOL_P] 音量+ 键 按键 |
| VDD_3V3_IO | R_KEY_VP | RAIL_VDD_3V3_IO | R_KEY_VP | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 音量+ 键 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_VP | GND | SW_KEY_VP | 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | 音量+ 键 另一端 -> GND |
| KEY_VOL_P | C_KEY_VP | GND | C_KEY_VP | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [KEY_VOL_P] 按键 RC 消抖电容 (10k 上拉 + 100nF, τ≈1ms); 是否需要消抖取决于 SoC 驱动方式 (等 SW 总工确认, 不影响本版布线) |
| KEY_VOL_M | SoC[TBD-01].KEY_VOL_M | R_KEY_VM | NET_KEY_VM | 同上 | NET | 必装 | MAIN_PCB | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 同上; 连接 主 PCB; 测试点 TP_KEY_VM |
| KEY_VOL_M | SW_KEY_VM | NET_KEY_VM | SW_KEY_VM | 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | [KEY_VOL_M] 音量- 键 按键 |
| VDD_3V3_IO | R_KEY_VM | RAIL_VDD_3V3_IO | R_KEY_VM | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] 音量- 键 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_VM | GND | SW_KEY_VM | 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | 音量- 键 另一端 -> GND |
| KEY_VOL_M | C_KEY_VM | GND | C_KEY_VM | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [KEY_VOL_M] 按键 RC 消抖电容 (10k 上拉 + 100nF, τ≈1ms); 是否需要消抖取决于 SoC 驱动方式 (等 SW 总工确认, 不影响本版布线) |
| KEY_CAM | SoC[TBD-01].KEY_CAM | R_KEY_CAM | NET_KEY_CAM | 同上 | NET | DNP | MAIN_PCB | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 同上; 连接 主 PCB (焊盘留, 不装); 测试点 — |
| KEY_CAM | SW_KEY_CAM | NET_KEY_CAM | SW_KEY_CAM | 按键 (待选型) | SW | DNP | MAIN_PCB | [推算] |  | [KEY_CAM] CAM 键 (焊盘必留, 不装) 按键 |
| VDD_3V3_IO | R_KEY_CAM | RAIL_VDD_3V3_IO | R_KEY_CAM | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_3V3_IO] CAM 键 (焊盘必留, 不装) 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_CAM | GND | SW_KEY_CAM | 按键 (待选型) | SW | DNP | MAIN_PCB | [推算] |  | CAM 键 (焊盘必留, 不装) 另一端 -> GND |
| KEY_CAM | C_KEY_CAM | GND | C_KEY_CAM | 100nF ±10% | C | DNP | MAIN_PCB | [推算] |  | [KEY_CAM] 按键 RC 消抖电容 (10k 上拉 + 100nF, τ≈1ms); 是否需要消抖取决于 SoC 驱动方式 (等 SW 总工确认, 不影响本版布线) |
| VBUS_5V | TP_VBUS | J_TYPE_C A4+A9+B4+B9 | TP_VBUS | 测试点 | TP | 必装 | CHG_BOARD | [推算] |  | 测什么: Type-C 入口 5V; 位置: Type-C 出口侧 ≤3mm |
| SYS | TP_SYS | RAIL_SYS | TP_SYS | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 系统 3.7V 主轨; 位置: 电池保护后 (镜脚本地) |
| BAT | TP_BAT | U_BATPROT | TP_BAT | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 电池电压; 位置: BQ25896 BAT 脚 |
| V_CORE | TP_VCORE | U_DCDC_VCORE | TP_VCORE | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: SoC 核心轨; 位置: DC-DC 输出 |
| V_SOC_IO | TP_VIO | U_DCDC_VIO | TP_VIO | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: SoC IO 轨; 位置: DC-DC/LDO 输出 |
| SENSOR_AVDD | TP_SENSOR_2V8 | CONN_CAM pin15 | TP_SENSOR_2V8 | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: sensor 三条轨; 位置: LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8) |
| SENSOR_VDD_IO | TP_SENSOR_1V8 | CONN_CAM pin16 | TP_SENSOR_1V8 | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: sensor 三条轨; 位置: LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8) |
| SENSOR_CORE | TP_SENSOR_1V2 | CONN_CAM pin17 | TP_SENSOR_1V2 | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: sensor 三条轨; 位置: LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8) |
| LIGHT_3V3 | TP_LIGHT_3V3 | CONN_LIGHT pin19 | TP_LIGHT_3V3 | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 光机轨; 位置: LDO 输出 |
| LIGHT_1V8 | TP_LIGHT_1V8 | CONN_LIGHT pin20 | TP_LIGHT_1V8 | 测试点 | TP | DNP | MAIN_PCB | [推算] |  | 测什么: 光机 1.8V 轨 (待 JBD); 位置: LDO 输出 (待 JBD 确认后) |
| CSI_D0_CK_P | TP_CSI_CK_P | CONN_CAM pin1 | TP_CSI_CK_P | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: CSI 时钟差分 (示波器测眼图/摆幅); 位置: 连接器出口 (规格合并名 TP_CSI_D0_CK_P / _N) |
| CSI_D0_CK_N | TP_CSI_CK_N | CONN_CAM pin2 | TP_CSI_CK_N | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: CSI 时钟差分 (规格合并名 TP_CSI_D0_CK_P / _N); 位置: 连接器出口 |
| CSI_D0_D0_P | TP_CSI_D0_P | CONN_CAM pin3 | TP_CSI_D0_P | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: CSI D0 数据差分; 位置: 连接器出口 |
| CSI_D0_D0_N | TP_CSI_D0_N | CONN_CAM pin4 | TP_CSI_D0_N | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: CSI D0 数据差分; 位置: 连接器出口 |
| CSI_RESET_N | TP_CSI_RST | CONN_CAM pin12 | TP_CSI_RST | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: CSI 复位 (10k 上拉点); 位置: 连接器出口 |
| CSI_MCLK | TP_MCLK | CONN_CAM pin11 | TP_MCLK | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: MCLK (包地走线); 位置: 连接器出口 |
| DSI_D0_CK_P | TP_DSI_CK_P | CONN_LIGHT pin1 | TP_DSI_CK_P | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: DSI 时钟差分; 位置: 连接器出口 (规格合并名 TP_DSI_D0_CK_P / _N) |
| DSI_D0_CK_N | TP_DSI_CK_N | CONN_LIGHT pin2 | TP_DSI_CK_N | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: DSI 时钟差分 (规格合并名 TP_DSI_D0_CK_P / _N); 位置: 连接器出口 |
| DSI_D0_D0_P | TP_DSI_D0_P | CONN_LIGHT pin3 | TP_DSI_D0_P | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: DSI D0 数据差分; 位置: 连接器出口 |
| DSI_D0_D0_N | TP_DSI_D0_N | CONN_LIGHT pin4 | TP_DSI_D0_N | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: DSI D0 数据差分; 位置: 连接器出口 |
| I2C_A_SCL | TP_I2CA_SCL | CONN_CAM pin13 | TP_I2CA_SCL | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: I2C_A 时钟; 位置: 连接器出口 |
| I2C_A_SDA | TP_I2CA_SDA | CONN_CAM pin14 | TP_I2CA_SDA | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: I2C_A 数据; 位置: 连接器出口 |
| I2C_B_SCL | TP_I2CB_SCL | CONN_LIGHT pin17 | TP_I2CB_SCL | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: DDC 时钟 (I2C_B); 位置: 连接器出口 |
| I2C_B_SDA | TP_I2CB_SDA | CONN_LIGHT pin18 | TP_I2CB_SDA | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: DDC 数据 (I2C_B); 位置: 连接器出口 |
| USB_D_P | TP_USB_D_P | CONN_USB pin1 | TP_USB_D_P | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: USB 2.0 差分; 位置: Type-C 出口 (规格合并名 TP_USB_D+ / D-) |
| USB_D_N | TP_USB_D_N | CONN_USB pin2 | TP_USB_D_N | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: USB 2.0 差分 (规格合并名 TP_USB_D+ / D-); 位置: Type-C 出口 |
| FSIN_OUT | TP_FSIN | R_SER_FSIN | TP_FSIN | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 帧同步 (FSIN/VSYNC) 引出; 位置: SoC 侧 -> 回答原厂问询 Q4b.3 |
| CHG_STAT | TP_CHG_STAT | R_PU_CHG_STAT | TP_CHG_STAT | 测试点 | TP | 必装 | CHG_BOARD | [推算] |  | 测什么: 充电状态; 位置: BQ25896 STAT 脚 -> 回答 Q4b.4 |
| PWR_GOOD | TP_PG | R_PU_PG | TP_PG | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 电源好 (BQ25896 PG 脚); 位置: 充电板 -> 主 PCB 跨板点 |
| ID_DETECT_0 | TP_ID | R_PU_ID0 | TP_ID | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 板级版本识别 (I2C EEPROM 或 GPIO 编码); 位置: 主 PCB |
| LED_R | TP_LED_R | R_LED_R | TP_LED_R | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: LED 红; 位置: 主 PCB |
| LED_G | TP_LED_G | R_LED_G | TP_LED_G | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: LED 绿; 位置: 主 PCB |
| LED_B | TP_LED_B | R_LED_B | TP_LED_B | 测试点 | TP | DNP | MAIN_PCB | [推算] |  | 测什么: LED 蓝 (无无线 -> DNP); 位置: 主 PCB |
| KEY_PWR | TP_KEY_PWR | R_KEY_PWR | TP_KEY_PWR | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 电源键; 位置: 主 PCB |
| KEY_VOL_P | TP_KEY_VP | R_KEY_VP | TP_KEY_VP | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 音量+ 键; 位置: 主 PCB |
| KEY_VOL_M | TP_KEY_VM | R_KEY_VM | TP_KEY_VM | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 音量- 键; 位置: 主 PCB |
| RESET_N | TP_RESET | R_PU_RESET_N | TP_RESET | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: 复位网; 位置: 主 PCB |
| BOOT_N | TP_BOOT | R_PU_BOOT_N | TP_BOOT | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: BOOT 网; 位置: 主 PCB |
| JTAG_TCK | TP_JTAG | J_DEBUG pin1 | TP_JTAG | 测试点 | TP | 必装 | MAIN_PCB | [推算] |  | 测什么: JTAG 时钟; 位置: 调试排针 |
| UART_TX | TP_UART | J_UART pin1 | TP_UART | 测试点 | TP | 可选 | MAIN_PCB | [推算] |  | 测什么: UART TX (与 USB 二选一); 位置: 调试排针 |

## P8 时钟 · 复位 · 调试
> XTAL 两套方案 (内部RC不装 / 外部晶振焊盘位不装) + RESET/BOOT + JTAG/UART + ★V1.1 上电监督链

### 功能块与判断
**时钟 / 复位 / 调试 —— 看着不起眼, 但这里有两个"必须双份"的决定。**

- ★**XTAL 双方案**: 参考版**同时**给 "内部 RC (不装)" 与 "外部晶振 (焊盘位 + 2×12pF, **不装**)" 两套 —— 因为**原厂一句话就能定生死** (ARS45 到底要不要外部晶振, 同 Die 的 AR9481 也不能确定)。焊盘位先留, 装配时按原厂确认选。
- `RESET_N` / `BOOT_N` 走按键到 GND (软上电/进下载模式), **释放时序**待原厂 (TBD-12) → 这决定我们按键电容与上电电阻怎么配。
- ★**UART 没有跟 JTAG 复用排针 (2026-10-27 审校补)**: 规格 B-20 写"同 B-19 排针 (复用脚)", 但 B-19 是 1×4 (TCK/TMS/TDI/TDO), 塞不下 2 根 UART 线 → 本版拆成 `J_UART` 1×2 独立排针 (不装贴片, 手工可焊), **原厂若要求复用再合并**。原叙述"JTAG+UART 复用 1×4"与网表不符, 已改。
- **[待原厂]**: 上下电/复位时序要求 (TBD-12, 含 RESET 释放时机与内部 DCDC 同步机制) · 是否有 USB PHY 及其版本 (TBD-10) · 启动介质与挂载接口 (TBD-06/11)。
- ★**V1.1 上电监督链**: 两路 DC-DC 的 **PG** 各引一个测试点 (`TP_PG_VCORE` / `TP_PG_VIO`, 开漏需上拉) → 原厂若要求 PG 参与时序, 在此补上拉位。`RESET_N` 增加一路**监督器开漏释放** (`U_SUPV`, TPS3808G01 类, 挂常供电轨): 监督电压用**分压** (`R_SUPV_DIV1/2`) 实现 → 原厂电压定了**只改两颗电阻**。与已有 10k 上拉 + RC + 复位键共存 (任一路拉低都生效)。

### 器件表 (42 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| XTAL_IN | SoC[TBD-01].XTAL_IN | X1 | NET_XTAL_IN | 12pF | NET | DNP | MAIN_PCB | [同Die参考-待官方确认] | TBD-12 | 时钟: 外部晶振位 (XTAL_IN); 参考版**同时**给 内部RC(不装) 与 外部晶振(焊盘位+2×12pF, 不装) 两套 |
| XTAL_IN | C_XTAL_IN | NET_XTAL_IN | C_XTAL_IN | 12pF ±10% | C | DNP | MAIN_PCB | [同Die参考-待官方确认] | TBD-12 | [XTAL_IN] 晶振负载电容 (XTAL_IN 侧) |
| GND | C_XTAL_IN | GND | C_XTAL_IN | 12pF ±10% | C | DNP | MAIN_PCB | [同Die参考-待官方确认] | TBD-12 | 晶振负载电容 地端 |
| XTAL_OUT | SoC[TBD-01].XTAL_OUT | X1 | NET_XTAL_OUT | 12pF | NET | DNP | MAIN_PCB | [同Die参考-待官方确认] | TBD-12 | 时钟: 外部晶振位 (XTAL_OUT); 参考版**同时**给 内部RC(不装) 与 外部晶振(焊盘位+2×12pF, 不装) 两套 |
| XTAL_OUT | C_XTAL_OUT | NET_XTAL_OUT | C_XTAL_OUT | 12pF ±10% | C | DNP | MAIN_PCB | [同Die参考-待官方确认] | TBD-12 | [XTAL_OUT] 晶振负载电容 (XTAL_OUT 侧) |
| GND | C_XTAL_OUT | GND | C_XTAL_OUT | 12pF ±10% | C | DNP | MAIN_PCB | [同Die参考-待官方确认] | TBD-12 | 晶振负载电容 地端 |
| XTAL | X1 | NET_XTAL_IN | X1 | 晶振焊盘位 (不装) | CONN | DNP | MAIN_PCB | [同Die参考-待官方确认] | TBD-12 | [XTAL] 外部晶振**焊盘位** (不装): 频率/负载/封装待原厂确认 (TBD-12); AR9481 同 Die 也不能确定 · 先留位 |
| RESET_N | R_PU_RESET_N | R_SER_RESET_N | NET_RESET_N | 上拉 10k + RC(1k/100nF) | NET | 必装 | MAIN_PCB | [待原厂] | TBD-12 | 方向 双向; 电平 1.8V [待原厂]; 阻抗 上拉 10k + RC(1k/100nF); 连接 SoC RESET_N + 按键到 GND; 测试点 TP_RESET |
| VDD_1V8_IO | R_PU_RESET_N | RAIL_VDD_1V8_IO | R_PU_RESET_N | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] RESET_N 上拉 (1.8V 域) |
| RESET_N_SOC | R_SER_RESET_N | SoC[TBD-01].RESET_N | R_SER_RESET_N | 1k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [RESET_N_SOC] RESET_N RC 串联 (与 C_RST 构成 RC 复位) |
| RESET_N_SOC | C_RST | NET_RESET_N_SOC | C_RST | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [RESET_N_SOC] RESET_N 对地 RC 电容 (τ=100ms; **释放时期待原厂 TBD-12**) |
| GND | C_RST | GND | C_RST | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | RESET RC 电容 地端 |
| RESET_N | SW_RST | NET_RESET_N | SW_RST | 复位按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | [RESET_N] 复位键 -> GND (软上电 / 进下载模式) |
| GND | SW_RST | GND | SW_RST | 复位按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | 复位键 -> GND |
| BOOT_N | SoC[TBD-01].BOOT_N | R_PU_BOOT_N | NET_BOOT_N | 上拉 10k | NET | 必装 | MAIN_PCB | [待原厂] | TBD-12 | 方向 双向; 电平 1.8V [待原厂]; 阻抗 上拉 10k; 连接 SoC BOOT 脚 + 按键到 GND; 测试点 TP_BOOT |
| VDD_1V8_IO | R_PU_BOOT_N | RAIL_VDD_1V8_IO | R_PU_BOOT_N | 10k ±1% | R | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] BOOT_N 上拉 (1.8V 域) |
| BOOT_N | SW_BOOT | NET_BOOT_N | SW_BOOT | BOOT 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | [BOOT_N] BOOT 键 -> GND (进下载模式) |
| GND | SW_BOOT | GND | SW_BOOT | BOOT 按键 (待选型) | SW | 必装 | MAIN_PCB | [推算] |  | BOOT 键 -> GND |
| JTAG_TCK_SOC | SoC[TBD-01].JTAG_TCK | R_JTAG_TCK | NET_JTAG_TCK_SOC | 单端, 100Ω 串阻 | NET | 必装 | MAIN_PCB | [待原厂] | TBD-01 | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TCK | R_JTAG_TCK | J_DEBUG pin1 | R_JTAG_TCK | 100Ω ±1% | R | 必装 | MAIN_PCB | [推算] |  | [JTAG_TCK] JTAG TCK 串阻 (隔离 SoC 调试脚) |
| JTAG_TMS_SOC | SoC[TBD-01].JTAG_TMS | R_JTAG_TMS | NET_JTAG_TMS_SOC | 单端, 100Ω 串阻 | NET | 必装 | MAIN_PCB | [待原厂] | TBD-01 | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TMS | R_JTAG_TMS | J_DEBUG pin2 | R_JTAG_TMS | 100Ω ±1% | R | 必装 | MAIN_PCB | [推算] |  | [JTAG_TMS] JTAG TMS 串阻 (隔离 SoC 调试脚) |
| JTAG_TDI_SOC | SoC[TBD-01].JTAG_TDI | R_JTAG_TDI | NET_JTAG_TDI_SOC | 单端, 100Ω 串阻 | NET | 必装 | MAIN_PCB | [待原厂] | TBD-01 | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TDI | R_JTAG_TDI | J_DEBUG pin3 | R_JTAG_TDI | 100Ω ±1% | R | 必装 | MAIN_PCB | [推算] |  | [JTAG_TDI] JTAG TDI 串阻 (隔离 SoC 调试脚) |
| JTAG_TDO_SOC | SoC[TBD-01].JTAG_TDO | R_JTAG_TDO | NET_JTAG_TDO_SOC | 单端, 100Ω 串阻 | NET | 必装 | MAIN_PCB | [待原厂] | TBD-01 | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TDO | R_JTAG_TDO | J_DEBUG pin4 | R_JTAG_TDO | 100Ω ±1% | R | 必装 | MAIN_PCB | [推算] |  | [JTAG_TDO] JTAG TDO 串阻 (隔离 SoC 调试脚) |
| J_DEBUG | J_DEBUG | J_DEBUG pin1 | J_DEBUG | 1×4 1.27mm 排针 (JTAG) | CONN | 必装 | MAIN_PCB | [推算] |  | [INVENTORY] [J_DEBUG] JTAG 调试排针 (不装贴片, 手工可焊); pin1=TCK, 2=TMS, 3=TDI, 4=TDO |
| UART_TX | SoC[TBD-01].UART_TX | J_UART pin1 | NET_UART_TX | 单端 | NET | 可选 | MAIN_PCB | [待原厂] | TBD-01 | 方向 双向; 电平 3.3V [待原厂]; 阻抗 单端; 连接 同 B-19 排针 (复用脚); 测试点 TP_UART |
| UART_RX | SoC[TBD-01].UART_RX | J_UART pin2 | NET_UART_RX | 单端 | NET | 可选 | MAIN_PCB | [待原厂] | TBD-01 | 方向 双向; 电平 3.3V [待原厂]; 阻抗 单端; 连接 同 B-19 排针 (复用脚); 测试点 TP_UART |
| UART_RX | J_UART | J_UART pin2 | J_UART | 1×2 1.27mm 排针 (UART) | CONN | 可选 | MAIN_PCB | [推算] |  | [UART_RX] 规格: UART 与 JTAG 复用同一排针 -> 本版拆成 1×2 独立排针 (原厂要求复用则再合并) |
| FSIN | SoC[TBD-01].FSIN | R_SER_FSIN | NET_FSIN | 单端, 50Ω 串阻 | NET | 必装 | MAIN_PCB | [待原厂] | TBD-13 | 方向 SoC→外部; 电平 [待原厂]; 阻抗 单端, 50Ω 串阻; 连接 SoC FSIN/VSYNC 脚 → 测试点; 测试点 TP_FSIN |
| FSIN_OUT | R_SER_FSIN | TP_FSIN | R_SER_FSIN | 50Ω ±1% | R | 必装 | MAIN_PCB | [推算] | TBD-13 | [FSIN_OUT] FSIN 引出串阻 (50Ω 源端匹配) |
| PG_VCORE | U_DCDC_VCORE PG | TP_PG_VCORE | TP_PG_VCORE | PG (开漏, 需上拉) | TP | 必装 | MAIN_PCB | [官方] | TBD-12 | [PG_VCORE] V_CORE 轨 PG 状态引出 (开漏, 需上拉到对应域); 若原厂要求 PG 参与上电时序, 在此补上拉电阻位 (R_PG_VCORE, 待原厂确认 TB |
| PG_VIO | U_DCDC_VIO PG | TP_PG_VIO | TP_PG_VIO | PG (开漏, 需上拉) | TP | 必装 | MAIN_PCB | [官方] | TBD-12 | [PG_VIO] V_SOC_IO 轨 PG 状态引出 (开漏, 需上拉); 同上 |
| V_SOC_IO | RAIL_V_SOC_IO | R_SUPV_DIV1 | R_SUPV_DIV1 | [待选型] 分压上臂 (0Ω 跳线位) | R | 必装 | MAIN_PCB | [推算] | TBD-02 | [SUPV_SENSE] ★V1.1: 电压监控分压 (把 V_SOC_IO 的实际电压映射到监控芯片窗口) · **原厂电压定了只改两颗电阻, 不改板** (ISS-082 的正 |
| SUPV_SENSE | R_SUPV_DIV1 | R_SUPV_DIV2 | R_SUPV_DIV2 | [待选型] 分压下臂 (0Ω 跳线位) | R | 必装 | MAIN_PCB | [推算] | TBD-02 | [SUPV_SENSE] 分压下臂 (到地) |
| GND | R_SUPV_DIV2 | GND | R_SUPV_DIV2 | [待选型] 分压下臂 (0Ω 跳线位) | R | 必装 | MAIN_PCB | [推算] | TBD-02 | [SUPV_SENSE] 分压下臂 地端 |
| VDD_1V8_IO | U_SUPV VDD | RAIL_VDD_1V8_IO | U_SUPV | [待选型] 电压监控 + 复位 (TPS3808G01 类) | IC | 必装 | MAIN_PCB | [推算] | TBD-12 | [VDD_1V8_IO] 上电监督器 (挂常供电轨); 监控窗口电压待原厂电源域表定 (TBD-02) |
| SUPV_SENSE | U_SUPV IN | U_SUPV | U_SUPV | [待选型] 电压监控 + 复位 (TPS3808G01 类) | IC | 必装 | MAIN_PCB | [推算] | TBD-02 | [SUPV_SENSE] 监督器采样脚 (经分压) |
| RESET_N | U_SUPV RESET (开漏) | NET_RESET_N | U_SUPV | 开漏释放 | IC | 必装 | MAIN_PCB | [推算] | TBD-12 | [RESET_N] ★V1.1: RESET_N 增加一路监督器开漏释放 (与已有 10k 上拉 + RC + 复位键共存: 任一路拉低都生效) |
| VDD_1V8_IO | C_SUPV | RAIL_VDD_1V8_IO | C_SUPV | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] 监督器 就近去耦 |
| GND | C_SUPV | GND | C_SUPV | 100nF ±10% | C | 必装 | MAIN_PCB | [推算] |  | [VDD_1V8_IO] 监督器 去耦 地端 |

## P9 跨铰链界面
> ★V1.1 新增页: 4 组跨铰链通道 + 保护/滤波件 + **板级归属 (充电板 / 主 PCB / 铰链)**

### 功能块与判断
**这一页是 V1.1 新加的 —— 因为 V1 把跨铰链的东西散在 P1/P5/P6 里, 看图的人数不出"到底有几组跨铰链、走多少 pin"。**

- ★**有两块板, 必然跨铰链**: 充电板 (Type-C + 充电链 + 电池) 在**镜框**, SoC 主 PCB 在**镜脚** (镜腿贴皮肤, 热账决定了 SoC 不能在贴皮肤处长时间满负荷)。⇒ **4 组跨铰链通道**:
  1. `J_CHG` (**1×10p@0.5mm**) — pin1/pin2 = **充电电流 1.0-1.5A 双 pin 并联** · pin3/pin4 = 回流双 pin · pin5 = CHG_STAT · pin6 = PWR_GOOD · pin7 = VBUS_DET · pin8-10 = 预留 (★V1.2: 电池在镜脚 ⇒ **SYS 不过铰链**)
  2. `CONN_USB` (**4p@0.5mm**) — USB 2.0 差分 (**烧录/调试口唯一通路**) + 独立回流地 + 1 预留
  3. `CONN_CAM` (**18p@0.5mm**) — pin1/2 = CSI CK · pin3-10 = D0-D3 (4lane, 8 根 100Ω 差分) · pin11 = MCLK (包地) · pin12 = RESET_N · pin13/14 = I2C_A · pin15/16/17 = sensor 三条电源 · **pin18 = 独立回流地**
  4. `CONN_LIGHT` (**1×21p@0.5mm**) — pin1/2 = DSI CK · 3/4 = D0 · 5/6 = D1 · 7-10 = D2/D3 预留 (DNP) · 11-16 = 桥接位 (方案B) · 17/18 = DDC · 19 = 3V3 · 20 = 1V8 · 21 = 5V 预留 (待 JBD)

  ★**铰链区高度预算 (V1.3 按结构总工 F-3 收敛后)**: 4 条链路触点区**统一 0.5mm pitch** → 堆叠 (10+4+18+21)×0.5 = **26.5mm** vs 镜脚根部净高 **37.0mm** → **余 10.5mm** ✅ (收敛前按 40p 声明是 54.7mm, **放不下**)。⇒ 门禁加了 2 条机械判据: **声明 pin 数 == 网表实际引用** (断链) + **堆叠 ≤ 37.0mm**。
  ★**为什么统一 0.5mm 而不是 1.27mm**: 1.27mm FFC 的动态弯折最小半径 ≥5mm 级, 我们铰链只有 **R=3.0mm** 预算 → 1.27mm 达不到寿命要求。
- ★**板级归属已进 netlist (`board` 列)**: `CHG_BOARD` / `MAIN_PCB` / `HINGE` 三档, 逐行标 → 装配、备料、结构开孔三件事有唯一口径 (V1 没有这一列, 看图的人分不清零件装哪块板)。
- ★**跨铰链 USB 的两条硬规则**: ① **不装共模扼流圈** (USB 2.0 眼图对共模转差分极敏感, 扼流圈会恶化眼图) → 只靠 **FPC 阻抗控制 + 两端 ESD**; ② **电源轨可以加磁珠/π 滤波, 信号轨不行** (SYS 跨铰链后在主板侧加 π 滤波, USB 差分不加)。
- ★**两条电源硬规则 (V1.2)**: ① **充电路径上不装 π 滤波** (会破坏 BQ25896 环路稳定性) → 只做双 pin 并联 + 载流核算; ② **SYS 不跨铰链** (电池在镜脚本地产生) → 镜脚腔体里的低阻大电流走线全在同板, 铰链只承担 1.5A 充电电流 + USB 差分。
- ★**回流路径要求**: 柔性段的 GND 必须走**连续参考面** (不能用细线), 两端各留 **≥2 个 GND pin**, 单点汇流位置由结构总工定 (ISS-065)。
- ★**结构总工已回的 (ISS-085)**: ① 跨铰链 FPC **≥4 层 / 0.5mm pitch / 差分 90Ω±10%** ② 弯折段 **R ≥3.0mm** 且区内只允许连续铜箔 (无过孔/元件/焊点/胶/压点) ③ 应力释放直线段 **≥5.0mm**, 固定夹允许滑移 **≤0.1mm** ④ **ESD 距连接器 ≤3.0mm / CMC 距弯折起点 ≥5.0mm, 一律放 PCB 端, 不许上 FPC** ⑤ **`J_CHG` 必须加机械防呆** (无防呆 → 反插 = SYS 短接 GND = 充电板 MOS 直通, F-6) ⑥ **`J_DEBUG`/`J_UART` 位置不冲突但"够不着"** → 镜脚末端必须开 1 个**可开启检修口** (外侧/下方, 不许开在贴皮肤面), 否则排针装上也用不了。
- ★**还欠结构总工的 2 项**: ① **铰链段 1.5A 载流/压降/发热核算** (ISS-091: 1.27→0.5mm 改后每 pin 载流能力 + 铰链实际长度 → mV@1.5A 与 mW) ② **检修口的开孔尺寸/盖板/磁吸方案** 落地到 MECH 尺寸链。
- ★**Type-C 的双份并联 (V1.3 补的真缺陷)**: USB-C 母座的 D+ 是 **A6+B6 两脚**、D- 是 **A7+B7**、VBUS 是 **A4+A9+B4+B9** → **只接单份的话插头一翻面就不通**。V1 只画了逻辑 pin4/pin5 (单份) ⇒ V1.3 改成物理脚位集合, 充电板那边必须双份并联。
- ★**V1.1 修掉一个真缺陷**: V1 的 netlist 里 `USB_D_P/D_N` **直接接到 `J_TYPE_C` pin4/5** = **把跨铰链短接了** (物理上不可能)。现在改成: SoC → 22Ω 串阻 (主板侧) → `CONN_USB` (跨铰链) → 充电板侧板内走线 → Type-C。门禁加了回归判据 (§A19)。

### 器件表 (18 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| GND | D_ESD_TC | GND | D_ESD_TC | ESD 阵列 [待选型] | D | 必装 | CHG_BOARD | [推算] |  | [GND] ★V1.4 补: Type-C 入口 ESD 阵列 地脚 (原来只有 I/O 脚, 阵列没接地 · ESD 不工作) |
| GND | D_ESD_USB | GND | D_ESD_USB | ESD 阵列 [待选型] | D | 必装 | MAIN_PCB | [推算] |  | [GND] ★V1.4 补: 跨铰链 USB ESD 阵列 地脚 (原来只有 I/O 脚, 阵列没接地 · ESD 不工作) |
| GND | D_ESD_CAM | GND | D_ESD_CAM | ESD 阵列 [待选型] | D | 必装 | MAIN_PCB | [推算] |  | [GND] ★V1.4 补: 跨铰链 CSI ESD 阵列 地脚 (原来只有 I/O 脚, 阵列没接地 · ESD 不工作) |
| HINGE_CHG | J_CHG | J_CHG pin1 | J_CHG | 1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流) | CONN | 必装 | HINGE | [推算] |  | [INVENTORY] [HINGE_CHG] 通道 1/4 **充电电流 + 状态回读** (★V1.2 改: 电池在镜脚 ⇒ 跨铰链的是**充电电流 1.0-1.5A**, * |
| HINGE_USB | CONN_USB | CONN_USB pin1 | CONN_USB | 4p 跨铰链连接器 (D+/D-/GND/预留) | CONN | 必装 | HINGE | [推算] |  | [INVENTORY] [HINGE_USB] 通道 2/4 **USB 2.0 差分**: Type-C 在镜框充电板, SoC 在镜脚主 PCB · **烧录/调试口必然跨铰链 |
| HINGE_CSI | CONN_CAM | CONN_CAM pin1 | CONN_CAM | 18p@0.5mm 跨铰链连接器 (主 PCB ↔ sensor 板; 18 脚 = 独立回流地) | CONN | 必装 | HINGE | [推算] | TBD-03 | [INVENTORY] [HINGE_CSI] 通道 3/4 **MIPI-CSI**: pin1/2=CK, 3-10=D0-D3, 11=MCLK, 12=RESET_N, 1 |
| HINGE_DSI | CONN_LIGHT | CONN_LIGHT pin1 | CONN_LIGHT | 1×22p@0.5mm 光机连接器 (板对板/FFC, 跨铰链到镜框光机; 末脚 GND = 差分回流) | CONN | 必装 | HINGE | [待JBD] | TBD-04 | [INVENTORY] [HINGE_DSI] 通道 4/4 **显示 + 光机供电** (1×22p@0.5mm): pin1/2=CK, 3/4=D0, 5/6=D1, 7-1 |
| USB_D_P | CONN_USB pin1 | D_ESD_USB | D_ESD_USB | ESD 阵列 [待选型] (2 通道 USB) | D | 必装 | MAIN_PCB | [推算] |  | [USB_D_P] ★跨铰链 USB 主板侧 ESD 阵列 (紧贴 CONN_USB); ★**不装共模扼流圈** (USB 2.0 眼图对共模转差分极敏感, 扼流圈会恶化眼图)  |
| USB_D_N | CONN_USB pin2 | D_ESD_USB | D_ESD_USB | ESD 阵列 [待选型] (2 通道 USB) | D | 必装 | MAIN_PCB | [推算] |  | [USB_D_N] USB 主板侧 ESD 阵列 (同一位, 2 通道) |
| USB_D_N | CONN_USB pin3 | GND | NET_USB_GND_H | 单端 | NET | 必装 | HINGE | [推算] |  | [USB_D_N] 跨铰链 USB 回流地 (独立 pin, 不与电源共 pin · 环路面积最小) |
| HINGE_RSV | CONN_USB pin4 | CONN_USB pin4 | CONN_USB | 预留 (不装) | NET | DNP | HINGE | [推算] |  | [INVENTORY] [HINGE_RSV] CONN_USB pin4 预留位 (不装) |
| GND | D_ESD_USB | GND | D_ESD_USB | ESD 阵列 [待选型] | D | 必装 | MAIN_PCB | [推算] |  | [USB_D_P] USB ESD 阵列 地端 |
| CSI_D0_CK_P | CONN_CAM pin1 | D_ESD_CAM | D_ESD_CAM | ESD 阵列 [待选型] (多通道 CSI) | D | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_CK_P] ★跨铰链 CSI 主板侧 ESD 阵列位 (紧贴 CONN_CAM); 通道数随 lane 数定 |
| GND | D_ESD_CAM | GND | D_ESD_CAM | ESD 阵列 [待选型] | D | 必装 | MAIN_PCB | [推算] | TBD-03 | [CSI_D0_CK_P] CSI ESD 地端 |
| USB_D_P | CONN_USB pin1 | J_TYPE_C A6+B6 | NET_USB_D_P_CHG | 板内走线 (充电板侧) | NET | 必装 | CHG_BOARD | [推算] |  | [USB_D_P_CHG] ★V1.1 补画: 充电板侧 USB 差分从跨铰链连接器到 Type-C D+ (板内走线) |
| USB_D_N | CONN_USB pin2 | J_TYPE_C A7+B7 | NET_USB_D_N_CHG | 板内走线 (充电板侧) | NET | 必装 | CHG_BOARD | [推算] |  | [USB_D_N_CHG] 充电板侧 USB 差分从跨铰链连接器到 Type-C D- (板内走线) |
| GND | CHG_GND_STAR | GND | CHG_GND_STAR | 单点汇流位 | CONN | 必装 | MAIN_PCB | [推算] |  | [GND] ★跨铰链回流要求: 柔性段的 GND 必须走**连续参考面**(不能细线), 两端各留 ≥2 个 GND pin; 单点汇流位置由结构总工定 (ISS-065) |
| BAT_CHG | J_CHG pin1 | TP_BAT_CHG | TP_BAT_CHG | 跨铰链段压降测点 | TP | 必装 | MAIN_PCB | [推算] |  | [BAT_CHG] ★跨铰链充电电流段: 双 pin 并联载流 + 压降/发热核算 (1.5A × 接触电阻); **充电路径上不装 π 滤波** (会破坏 BQ25896 环路稳 |

## P10 充电板 (镜框)
> ★V1.5 新增页: Type-C 16p 物理脚位 (USB-IF) + BQ25896 24 脚 + 温度检测三件式 + **R_ILIM 硬件限流**

### 功能块与判断
**这一页是 V1.5 新加的 —— 充电板 (镜框) 之前只作为子集散在 P1/P6, 没有自己的完整页。**

- 规格: `HW/CHARGE_BOARD_SPEC.md` (691 行, USB-IF Type-C Spec 2.0 + TI BQ25896 datasheet 一手核对)。
- ★**Type-C 16p 母座按 USB-IF 物理脚位** (A/B 编号): VBUS = A4+A9+B4+B9 · **D+ = A6+B6 双份并联** · **D− = A7+B7** · CC1 = A5 · CC2 = B5 · **GND = A1+A12+B1+B12** · SBU 不接。★**双份并联是必须的** —— 只接 A6/A7 的话插头一翻面就不通; GND 四个脚都要接, 少接 B1/B12 = 回流路径减半。
- ★**不上 PD 控制器 (TPS25730)**: 充电板没有 3.3V 轨 (TPS25730 VIN_3V3 绝对最大 4V), 我们只要 5V, 25×10mm 板也放不下 QFN-38 + 10 个无源件 → **保留 Rd 5.1k×2**。★而且 **PD 5V/2A 不会把 2A 灌进铰链** —— 铰链走的是充电电流 ICHG ≈ 0.822×IIN。
- ★**R_ILIM 300Ω 必装 (硬件限流)**: BQ25896 的 IINLIM **复位默认 2048mA** → 不装这颗电阻, 铰链段可能被灌 ~1.68A (发热/压降失控)。装 300Ω → ICHG ≈ 0.88-1.07A; 若结构核算 (ISS-091) 判定铰链只吃 1.0A → **换 390Ω** (0.67-0.82A), **换料不换板**。
- ★**温度检测是三件式, 不是两件式**: RT1 5.24k (REGN→TS) + RT2 30.31k (TS→GND) + **103AT NTC ∥ RT2** (datasheet: 0°C→73.25%, 60°C→34.375%)。★并且 **TS 必须跨铰链** —— NTC 贴电芯在镜脚, 而 BQ25896 在镜框充电板 → 走 `J_CHG pin8` (高阻, 无电流)。
- 电池位置**锁镜脚** (V1.2 裁决) → 电池的过充/过放/过温保护 (BQ2970 + 2×MOS) 也在镜脚, 充电板这边不重复画。

### 器件表 (56 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 板 | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| VBUS_5V | J_TYPE_C A4 | D_ESD_TC | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★USB-IF Type-C Cable and Connector Spec R2.0 (2019-08) Table 3-5: A4/A9/B4/B9 四个 VBUS 在座内并 |
| VBUS_5V | J_TYPE_C A9 | D_ESD_TC | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★USB-IF Type-C Cable and Connector Spec R2.0 (2019-08) Table 3-5: A4/A9/B4/B9 四个 VBUS 在座内并 |
| VBUS_5V | J_TYPE_C B4 | D_ESD_TC | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★USB-IF Type-C Cable and Connector Spec R2.0 (2019-08) Table 3-5: A4/A9/B4/B9 四个 VBUS 在座内并 |
| VBUS_5V | J_TYPE_C B9 | D_ESD_TC | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★USB-IF Type-C Cable and Connector Spec R2.0 (2019-08) Table 3-5: A4/A9/B4/B9 四个 VBUS 在座内并 |
| USB_CC1 | J_TYPE_C A5 | R_CC1 | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★CC1 触点: Type-C Rd 5.1kΩ ±20% 到 GND (R_CC1 已在主网表 P6 第 285/287 行画出, 本行只登记触点归属); 本板只做 Rd, 不上 |
| USB_CC2 | J_TYPE_C B5 | R_CC2 | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★CC2 触点: Rd 5.1kΩ ±20% 到 GND (R_CC2 已在主网表 P6 第 286/288 行画出, 本行只登记触点归属) |
| USB_D_P | J_TYPE_C A6 | J_TYPE_C B6 | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★D+ 双份并联 (A6+B6 同一节点): USB-IF Table 3-5 Note 2 要求并联短接线 ≤3.5mm; 跨铰链那一段在 P9 第 416 行, 本行只画 Ty |
| USB_D_N | J_TYPE_C A7 | J_TYPE_C B7 | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★D− 双份并联 (A7+B7 同一节点): 并联短接线 ≤3.5mm; 跨铰链那一段在 P9 第 417 行, 本行只画 Type-C 侧焊盘; 不装共模扼流圈 |
| GND | J_TYPE_C A1 | GND | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★GND 四脚全并联 A1/A12/B1/B12 (USB-IF Table 3-5; 现行网表只写了 A1+A12 的合并写法, B1/B12 两脚没列 = 回流减半); 本页按 |
| GND | J_TYPE_C A12 | GND | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★GND 四脚全并联 A1/A12/B1/B12 (USB-IF Table 3-5; 现行网表只写了 A1+A12 的合并写法, B1/B12 两脚没列 = 回流减半); 本页按 |
| GND | J_TYPE_C B1 | GND | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★GND 四脚全并联 A1/A12/B1/B12 (USB-IF Table 3-5; 现行网表只写了 A1+A12 的合并写法, B1/B12 两脚没列 = 回流减半); 本页按 |
| GND | J_TYPE_C B12 | GND | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | ★GND 四脚全并联 A1/A12/B1/B12 (USB-IF Table 3-5; 现行网表只写了 A1+A12 的合并写法, B1/B12 两脚没列 = 回流减半); 本页按 |
| NC | J_TYPE_C A8 | NC | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | DNP | CHG_BOARD | [官方] |  | ★SBU1 不接: USB-IF Table 3-5 Note 3 'Contacts A8 and B8 (SBU1 and SBU2) shall be not connect |
| NC | J_TYPE_C B8 | NC | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | DNP | CHG_BOARD | [官方] |  | ★SBU2 不接: 同 A8 (USB-IF Table 3-5 Note 3); 本机不做 Alt Mode |
| GND | J_TYPE_C shield | GND | J_TYPE_C | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | CONN | 必装 | CHG_BOARD | [官方] |  | 屏蔽壳 接 GND 单点 (短粗铜皮, 不用细线); 与机壳地的接法待结构总工定 (ISS-065) |
| VBUS_5V_CHG | U_CHG pin1 | C_VBUS_IC | C_VBUS_IC | 1µF X7R 25V | C | 必装 | CHG_BOARD | [官方] |  | ★BQ25896 pin1 VBUS: 'Place a 1-µF ceramic capacitor from VBUS to PGND and place it as clos |
| PGND | C_VBUS_IC | U_CHG pin17+pin18 | C_VBUS_IC | 1µF X7R 25V | C | 必装 | CHG_BOARD | [官方] |  | 去耦地端 = BQ25896 PGND (pin17/18) 同一地网; datasheet 'A single point connection is recommended b |
| PMID | U_CHG pin23 | C_PMID | C_PMID | 10µF X7R 25V | C | 必装 | CHG_BOARD | [官方] |  | ★datasheet: 'put 1µF on VBUS to PGND, and the rest capacitance on PMID to PGND' ⇒ PMID 电容不 |
| PGND | C_PMID | U_CHG pin17+pin18 | C_PMID | 10µF X7R 25V | C | 必装 | CHG_BOARD | [官方] |  | PMID 电容 地端 (PGND) |
| PMID | L_CHG | U_CHG pin23 | L_CHG | 2.2µH Isat≥1.5A DCR≤50mΩ | L | 必装 | CHG_BOARD | [官方] |  | 开关电感 一端接 PMID; IRIPPLE=0.29A (见上) ⇒ Isat 选 ≥1.5A; 型号待选型 (询价经项目总工) |
| SW | U_CHG pin19 | L_CHG | L_CHG | 2.2µH Isat≥1.5A DCR≤50mΩ | L | 必装 | CHG_BOARD | [官方] |  | 开关电感 另一端接 SW 开关节点; 铜箔面积最小化, 远离 TS 分压与 ADC |
| SW | U_CHG pin20 | U_CHG pin19 | U_CHG | BQ25896 | IC | 必装 | CHG_BOARD | [官方] |  | pin19/20 SW 开关节点 (两脚同网); datasheet: 'Connect the 0.047µF bootstrap capacitor from SW to BT |
| BTST | U_CHG pin21 | C_BST | C_BST | 47nF 25V | C | 必装 | CHG_BOARD | [官方] |  | ★自举电容 0.047µF from SW to BTST (datasheet pin21 原文) |
| SW | C_BST | U_CHG pin19 | C_BST | 47nF 25V | C | 必装 | CHG_BOARD | [官方] |  | 自举电容 另一端接 SW |
| REGN | U_CHG pin22 | R_TS_TOP | R_TS_TOP | 5.24k ±1% (RT1: REGN 到 TS) | R | 必装 | CHG_BOARD | [官方] |  | ★TS 分压上臂 RT1 = 5.24k (datasheet Equation 2 原文), 取自 REGN (BQ25896 内部 LDO 5.0V, 4.8-5.5V, 限流 |
| TS_BAT | R_TS_TOP | U_CHG pin11 | R_TS_TOP | 5.24k ±1% (RT1: REGN 到 TS) | R | 必装 | CHG_BOARD | [官方] |  | RT1 下端接 TS 网 (与 U_CHG pin11 同网); ★温度检测三件式: RT1 5.24k (充电板 REGN 到 TS) + RT2 30.31k (镜脚 TS 到 |
| TS_BAT | U_CHG pin11 | J_CHG pin8 | J_CHG | 跨铰链 (高阻) | NET | 必装 | HINGE | [推算] |  | ★TS 跨铰链走 J_CHG pin8 (NTC 在镜脚, BQ25896 在镜框): 源阻抗仅 3-4kΩ ⇒ 跨铰链可用; 安全副产品: TS 线断开时充电板侧只剩 RT1 ⇒ |
| PSEL | U_CHG pin2 | R_PSEL | R_PSEL | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | PSEL 拉低 = 适配器/DCP (本机无 USB PHY 主机; 拉高会锁 500mA); datasheet: 'High indicates a USB host sour |
| PGND | R_PSEL | U_CHG pin17+pin18 | R_PSEL | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | PSEL 下拉 地端 (PGND) |
| PWR_GOOD | U_CHG pin3 | J_CHG pin6 | U_CHG | BQ25896 | IC | 必装 | CHG_BOARD | [官方] |  | ★PG (开漏): LOW = 输入源良好 (VBUS 在 VVBUS_OP 内且 IBATSRC>30mA); 上拉 10k 只放主板侧 (充电板无 3.3V); 主网表 P2  |
| CHG_STAT | U_CHG pin4 | J_CHG pin5 | U_CHG | BQ25896 | IC | 必装 | CHG_BOARD | [官方] |  | ★STAT (开漏): LOW = 充电中, HIGH = 完成或禁用, 1Hz 闪烁 = 故障; 上拉 10k 只放主板侧; 主网表 P2 第 138 行用的是裸 'U_CHG' |
| I2C_CHG_SCL | U_CHG pin5 | R_PU_SCL | R_PU_SCL | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | ★I2C 不跨铰链 (PM 裁决) ⇒ J_CHG pin9/pin10 本版留空不接 (仍在主网表 P1 第 17/18 行占位); 上拉位留在充电板本地 (充电板没有 3.3V |
| REGN | R_PU_SCL | U_CHG pin22 | R_PU_SCL | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | SCL 上拉位的另一端 (REGN 5V; 充电板无 3.3V 逻辑轨) ★裁决 (PM): **必装** —— 充电 IC 的 I2C 本板自闭环 (不跨铰链, 见 J_CHG  |
| I2C_CHG_SDA | U_CHG pin6 | R_PU_SDA | R_PU_SDA | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | ★同 SCL (I2C 不跨铰链, PM 裁决); ⚠️ 待裁决: 上拉装不装, 建议装 10k 上拉到 REGN (datasheet 原文要求) ★裁决 (PM): **必装* |
| REGN | R_PU_SDA | U_CHG pin22 | R_PU_SDA | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | SDA 上拉位的另一端 (REGN 5V) ★裁决 (PM): **必装** —— 充电 IC 的 I2C 本板自闭环 (不跨铰链, 见 J_CHG pin9/10 预留); 上拉 |
| INT_CHG | U_CHG pin7 | R_PU_INT | R_PU_INT | 10k ±1% | R | DNP | CHG_BOARD | [官方] |  | INT 开漏 256µs 脉冲; 本版不跨铰链 (J_CHG 无余量, 状态走 STAT+PG), 留位不装; 若将来要跨铰链, 上拉必须移到主板侧 3.3V 并占用 J_CHG  |
| REGN | R_PU_INT | U_CHG pin22 | R_PU_INT | 10k ±1% | R | DNP | CHG_BOARD | [官方] |  | INT 上拉位的另一端 (REGN 5V; INT 不跨铰链, 拉高只用于把脚定义住) |
| OTG_SET | U_CHG pin8 | R_OTG | R_OTG | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | OTG 拉低 = 关 boost 模式 (本机不做 OTG): 'The boost mode is activated when OTG_CONFIG = 1' |
| PGND | R_OTG | U_CHG pin17+pin18 | R_OTG | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | OTG 下拉 地端 (PGND) |
| CE_SET | U_CHG pin9 | R_CE | R_CE | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | CE 拉低 = 允许充电 (CHG_CONFIG 复位默认 1): 'CE pin must be pulled High or Low' ⇒ 不得悬空; 拉低的好处 = SoC  |
| PGND | R_CE | U_CHG pin17+pin18 | R_CE | 10k ±1% | R | 必装 | CHG_BOARD | [官方] |  | CE 下拉 地端 (PGND) |
| IINLIM | U_CHG pin10 | IINLIM | U_CHG | BQ25896 | IC | 必装 | CHG_BOARD | [官方] |  | ★pin10 ILIM: R_ILIM = 300Ω ±1% 必装 (已在主网表 P1 第 39/40 行画出, 本行不重复画电阻, 只登记引脚归属); IINMAX = KILI |
| NC | U_CHG pin12 | NC | U_CHG | BQ25896 | IC | DNP | CHG_BOARD | [官方] |  | QON 不接: datasheet 'The pin contains an internal pull-up to maintain default high logic'; 按 |
| BAT_CHG | U_CHG pin13 | C_BAT | C_BAT | 10µF X7R 6.3V | C | 必装 | CHG_BOARD | [官方] |  | ★datasheet 'Connect a 10uF closely to the BAT pin' (pin13/14); BAT 脚是跨铰链载流路径起点 |
| PGND | C_BAT | U_CHG pin17+pin18 | C_BAT | 10µF X7R 6.3V | C | 必装 | CHG_BOARD | [官方] |  | BAT 去耦 地端 (PGND) |
| BAT_CHG | U_CHG pin14 | J_CHG pin1 | J_CHG | 1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流) | CONN | 必装 | HINGE | [推算] |  | 充电电流跨铰链: J_CHG pin1/pin2 双 pin 并联 (每 pin ≤0.75A); 铰链段不装 π 滤波 (会破坏 BQ25896 环路稳定性); 载流/压降/发热 |
| SYS_CHG | U_CHG pin15 | U_CHG pin16 | U_CHG | BQ25896 | IC | DNP | CHG_BOARD | [官方] |  | ★pin15/16 SYS: 本板不供电 (SYS 在镜脚由 BQ2970 + 2×MOS 产生); ⚠️ 待裁决: 网名用 SYS_CHG 而不是 SYS — 现行网表的 SYS |
| SYS_CHG | U_CHG pin16 | C_SYS | C_SYS | 20µF 6.3V | C | DNP | CHG_BOARD | [官方] |  | ★C_SYS 留位不装 = 保留 '电池挪镜框' 可回退分支 (将来接 2 根线 + 贴这颗电容即可, 不用改板); 本板 SYS 无负载, 装 20µF 只占 25×10mm 板 |
| PGND | C_SYS | U_CHG pin17+pin18 | C_SYS | 20µF 6.3V | C | DNP | CHG_BOARD | [官方] |  | SYS 电容 地端 (PGND); DNP 时不占板面 |
| PGND | U_CHG pin17 | U_CHG pin18 | U_CHG | BQ25896 | IC | 必装 | CHG_BOARD | [官方] |  | ★pin17/18 PGND 功率地 (开关节点回流); 'connect directly to the PGND'; PowerPAD 同接 PGND + ≥6 过孔 (散热焊 |
| PGND | R_STAR_PGND | U_CHG pin17+pin18 | R_STAR_PGND | 0Ω / 铜皮短接 (PGND 单点星接) | R | 必装 | CHG_BOARD | [官方] |  | ★PGND 与 GND 的单点汇流位 (datasheet: 'A single point connection is recommended between power PGN |
| GND | R_STAR_PGND | J_TYPE_C A1 | R_STAR_PGND | 0Ω / 铜皮短接 (PGND 单点星接) | R | 必装 | CHG_BOARD | [官方] |  | 星接位的 GND 端 (充电板地 = Type-C GND 四脚 + J_CHG pin3/pin4 回流) ★裁决 (PM): **必装** (DNP 会让 PGND 整个悬空  |
| NC | U_CHG pin24 | NC | U_CHG | BQ25896 | IC | DNP | CHG_BOARD | [官方] |  | pin24 NC (datasheet: No Connect); 全 24 脚对照: 1 VBUS / 2 PSEL / 3 PG / 4 STAT / 5 SCL / 6 SD |
| VBUS_5V | D_TVS_VBUS | J_TYPE_C A4 | D_TVS_VBUS | 5V 级单向 TVS [待选型] | D | 必装 | CHG_BOARD | [推算] |  | ⚠️ 待裁决: 规格 §4.3 提到但 §7 连接清单未列的件 (插线尖峰 TVS: VRWM ≥5.0V, 钳位电压 < BQ25896 绝对最大 22V); 位置紧靠 Type |
| GND | D_TVS_VBUS | J_TYPE_C A1 | D_TVS_VBUS | 5V 级单向 TVS [待选型] | D | 必装 | CHG_BOARD | [推算] |  | TVS 地端 (与座侧 GND 同网) ★裁决 (PM): **必装** (Type-C 入口 TVS 是标配); VRWM 5-6V 档, **脉冲电流额定 ≥3A** (PD  |
| TS_BAT | TP_TS | U_CHG pin11 | TP_TS | 测试点 | TP | 必装 | CHG_BOARD | [推算] |  | TS 电压测点 (调 TS 分压 / 验证 NTC 跨铰链通断): 0°C 应读 ~3.663V (73.25% REGN), 60°C 应读 ~1.719V (34.375% R |

---

## 附: 本版与投板版还差什么 (缺口清单)
| # | 缺什么 | 卡住谁 | 怎么解 |
|---|---|---|---|
| 1 | SoC 引脚表 / 球位图 / FCCSP pitch | 原理图定版 + PCB 逃线 + 板宽 (blocker) | 原厂 (TBD-01/05) —— **网上确认拿不到** (官网无下载区) |
| 2 | 各电源域标称电压/最大电流/上电时序 | P1 电源页定版 + DC-DC 选型 | 原厂 (TBD-02) |
| 3 | MIPI-CSI lane 数/速率/AC 耦合是否内置 | P5 传感器页 (AC 耦合位/端接位) | 原厂 (TBD-03) |
| 4 | 显示 TX 接口类型 (DSI / DP / 两者) | P4 显示页 + 要不要桥接芯片 | 原厂 (TBD-04) + **JBD 开发套件接口定义** (可能更快) |
| 5 | 启动存储形态 (SPI-NOR vs eMMC) 与挂载口 | P3 启动存储页 + 板宽 | 原厂 (TBD-06/11) |
| 6 | 球位号 (全部 SoC 侧节点) | 9 页全部 | 原厂 (TBD-01) |
| 7 | ★跨铰链 4 组通道的连接器型号 / pitch / 柔性段长度 / 是否合并成 1 个连接器 | P9 页布线 + 镜脚腔体 + 铰链可靠性 | **结构总工** (P9 页已列通道与 pin 账, ISS-085 在做) |
| 8 | ★`U_BRIDGE` 型号 (定位已定为 DP1.4 TX → MIPI DSI TX 桥接, 但这类芯片极少) | P4/P6 选型 + BOM + PCB 面积 | 原厂 (TBD-04) + JBD 接口定义 + 询价 (外发经项目总工) |
| 9 | ★SoC 侧温度检测的**物理测点** (die / 镜腿 / 电池) —— 器件已定 TMP117 | P2 + SW 热策略 | SW 总工 |
| 10 | ★电池 NTC 的**热敏电阻位置** (贴电芯还是插孔) 与阈值档 | P1 充电链安全 | BQ25896 数据手册 + 结构总工 |

> ★**并行风险**: 官网「宽度≤8mm」+ FCCSP 集成 DRAM 的 pitch 通常 0.4-0.5mm [推算] → **12mm 板宽与 4-6 层假设可能被推翻** (ISS-078, blocker)。
