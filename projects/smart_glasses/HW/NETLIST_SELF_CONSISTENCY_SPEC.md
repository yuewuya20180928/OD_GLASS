# ★★网表自身一致性 · 4 处"自己跟自己打架"的落表规格 (★ISS-211★)★★

> ★**性质**: ★**这是【规格页】, 不是执行记录** ⇒ ★**本文件落笔时, 网表 / 板 / 脚表 / BOM / SPEC.json / 生成器 一个字节都没改** ⇒ ★**凡是"要改成什么"的字样, 都只是"要改成什么", 不是"已经改好"**
> ★**日期**: 2026-11-15 · ★**执行**: 硬件总工 (hw-lead) · ★**单号**: ISS-211 · ★**owner**: hw-lead · ★**verify_by**: main
> ★**门禁**: ★**`HW/check_netlist_selfconsistency.py`** (rc=0 / `--selftest` / `--expect-resolved`)
> ★**受保护 md5 (★交卷前后逐字节不变★)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`

---

## 0. ★一句话 + 边界★★

★**现行网表里有 4 处"同一张表里两行字直接互相否定"的地方**: ① I2C_A 上拉的 **NET 行说 4.7k/3.3V、器件行说 2.2k/1.8V** · ② **BAT_DET 整条分压链全 DNP, 而 SoC 的 ADC 输入脚是必装** (⇒ 悬空输入) · ③ **U_EN_SW 没有器件本体行** ⇒ BOM 里这颗 4 脚 IC 被登记成 NET 行 (value 栏躺着一句脚功能串) · ④ **USB D− 全程没有 ESD, 而那颗器件自称"双通道"**。

★**为什么现在不能改**: ★**整链重出 第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md`) 要把 C/E/D 三项一次合并落表 ⇒ 板只改一次** ⇒ ★**先落表 = 留证链/Gerber/投产包/盖印 白跑两遍** ⇒ ★**所以本单 = 出规格 + 出门禁, 让这 4 条跟着那一趟一起落** (★这套路子在 ISS-191 / ISS-174 已验证过★)。

★**本单不许做的事 (★边界★)**: ★**不改网表 / 不改脚表 / 不改板 / 不改 SPEC.json / 不改任何生成器 / 不改 issue_log / 不改 PROJECT_TRACKER §0 / 不碰别人的分片 / 零外发 (不发邮件·询价·问询·采购)★**。

---

## 1. ★★四条缺陷 · 逐条 6 栏 (★① 现象 ② 为什么是缺陷 ③ 修法 ④ 影响面 ⑤ 落表时机 ⑥ 证据等级★)★★

---

### ★★第 (1) 条 ★★ I2C_A 上拉: ★★网线行说 4.7k/3.3V, 器件行说 2.2k/1.8V★★

#### ① 现象 (★网表原文逐字 + 行号★)

★**表A `HW/netlist_v1.csv`** (★表头 = 第 1 行, 下面行号是物理行号★):

| 行 | 原文 (逐字) |
|---|---|
| ★**L167** | `P2,I2C_A_SCL,J_SOM_P2 pin31,R_PU_I2CA_SCL,NET_I2C_A_SCL,"上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)",NET,必装,[推算],,"方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF); 连接 SoC [待原厂] + sensor/NTC/桥接/充电IC; 测试点 TP_I2CA_SCL",B-01,MAIN_PCB,,` |
| ★**L168** | `P2,I2C_A_SDA,J_SOM_P2 pin33,R_PU_I2CA_SDA,NET_I2C_A_SDA,上拉 4.7k 到 3.3V,NET,必装,[推算],,"方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V; 连接 同上; 测试点 TP_I2CA_SDA",B-02,MAIN_PCB,,` |
| ★**L169** | `P2,VDD_1V8_IO,R_PU_I2CA_SCL,RAIL_VDD_1V8_IO,R_PU_I2CA_SCL,2.2k ±1%,R,必装,[推算],,"[VDD_1V8_IO] I2C_A 上拉 (★★11-04 ISS-153 订正: **实际 net = RAIL_VDD_1V8_IO (1.8V 域)**; ★**旧注释写的『[VDD_3V3_IO] / 3.3V 上拉』与网表相反, 已作废**; 依据 ①: RK3572 的 I2C5 = J_SOM_P2 pin31/pin33 属**1.8V 域** (HW/PCB/FET3572C_PIN_TABLE.csv P2_31/P2_33 电压域列 = 1.8V) ⇒ 3.3V 上拉会把 SoM 的 1.8V 脚灌 3.3V = 过压; …) ",B-01,MAIN_PCB,,` (★note 很长, 此处截断; 完整原文见文件★) |
| ★**L170** | `P2,VDD_1V8_IO,R_PU_I2CA_SDA,RAIL_VDD_1V8_IO,R_PU_I2CA_SDA,2.2k ±1%,R,必装,[推算],,"[VDD_1V8_IO] I2C_A 上拉 (★同 SCL: 实际 net = RAIL_VDD_1V8_IO, **1.8V 域** …)",B-02,MAIN_PCB,,` |
| ★**L171** | `P2,I2C_A_SCL,CONN_CAM pin24,NET_I2C_A_SCL,NET_I2C_A_SCL,"上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, ★camera FPC 标 I2C5 = 1.8V 域)",NET,必装,…,B-01,MAIN_PCB,,` ★**← 自洽对照行: camera 侧已经写对了** |

★**表B `HW/netlist_v1_pins.csv`**: ★**L367** `R_PU_I2CA_SCL.1` net=`I2C_A_SCL` · ★**L368** `R_PU_I2CA_SCL.2` net=`VDD_1V8_IO` · ★**L369/L370** 同款 (SDA) ⇒ ★**脚表是对的**。

★**根源在规格源头 `HW/SCHEMATIC_V1_SPEC.json`** (★`connections` 数组★):
```json
{ "id": "B-01", "signal": "I2C_A_SCL", "level": "3.3V",
  "imp": "上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)", … }
{ "id": "B-02", "signal": "I2C_A_SDA", "level": "3.3V",
  "imp": "上拉 4.7k 到 3.3V", … }
```

#### ② 为什么它是缺陷 (★可判定依据★)

1. ★**同一 ref `R_PU_I2CA_SCL`, 两行字互相否定**: L167 的 NET 行说"上拉 **4.7k 到 3.3V**", L169 的器件行说"**2.2k ±1%** 挂 **RAIL_VDD_1V8_IO**" ⇒ ★**下一个读网表的人 (评审人 / 板厂 / 另一个总工) 会拿到错的那一行**。
2. ★**L169 自己的 note 已经把 3.3V 那句判成作废** (★"旧注释写的『[VDD_3V3_IO] / 3.3V 上拉』与网表相反, 已作废"★) ⇒ ★**L167/L168 还在逐字复述那句"已作废"的话** ⇒ 自我否定的闭环。
3. ★**算术错**: L167 写 `t_r=2.38µs@100pF`, 而 L169 的 note 自己算的是 "t_r=2.2k×100pF×0.847≈**186ns**" ⇒ ★**差 12.8 倍**。★**`SW/SW_TIMING_REVIEW.md` §6 已经把这句翻掉了**: 「★**旧结论翻转** … 2.2k 的实算是 **186ns**, 注记 **2380ns** 差 **12.8 倍**★」(★`SW/SW_TIMING_REVIEW.md:130`★)。
4. ★**灌流也一起错**: L167 的 "灌 702µA" 是按 4.7k@3.3V 算的; 2.2k@1.8V 的真实灌流是 **0.64mA** (L169 note 里已复算)。
5. ★**物理危害 (若照 L167 装)**: ★**SoM 的 P2_31/P2_33 是 1.8V 域** (★`HW/PCB/FET3572C_PIN_TABLE.csv`: `P2,31,AH33,I2C5_SCL_M3,…,1.8V` / `P2,33,AL33,I2C5_SDA_M3,…,1.8V`★) ⇒ **3.3V 上拉会把 SoM 的 1.8V 脚灌到 3.3V = 过压** (★L169 note 依据① 已写明★)。

#### ③ 修法 (★精确到改哪个文件的哪个字段★)

★**真修法 = 改 `HW/SCHEMATIC_V1_SPEC.json`, 不是手改网表** ⇒ ★**手改 CSV 会被下次重跑生成器覆盖 ⇒ 那就是"改在产物上", 老毛病**。

| 改哪个文件 | 改哪个字段 | 从 | 改成 |
|---|---|---|---|
| ★`HW/SCHEMATIC_V1_SPEC.json` ★ | ★`connections[]` 里 `id == "B-01"` 的 `level` ★ | `"3.3V"` | ★`"1.8V"` ★ |
| ★`HW/SCHEMATIC_V1_SPEC.json` ★ | ★`connections[]` 里 `id == "B-01"` 的 `imp` ★ | `"上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"` | ★`"上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)"` (★口径必须是 2.2k / 1.8V / 186ns; 逐字文案由落表那趟定, 但三个数不许再错★) ★ |
| ★`HW/SCHEMATIC_V1_SPEC.json` ★ | ★`connections[]` 里 `id == "B-02"` 的 `level` ★ | `"3.3V"` | ★`"1.8V"` ★ |
| ★`HW/SCHEMATIC_V1_SPEC.json` ★ | ★`connections[]` 里 `id == "B-02"` 的 `imp` ★ | `"上拉 4.7k 到 3.3V"` | ★`"上拉 2.2k 到 1.8V"` ★ |

★**为什么改 SPEC.json 就够**: ★`state/gen_netlist.py:770` 的 `conn_row()` 文档自己写着「★**value 默认取规格 imp (A 组阻抗必须与规格逐字一致 · check_netlist 判据 5)★**」⇒ ★**改完 SPEC.json 重跑 `state/gen_netlist.py`, L167/L168 自动就对了** ⇒ ★**不需要碰 `state/gen_netlist.py` (★本单禁止改生成器★)**。

★**落表那趟还要顺带做 (★都在同一趟里, 不许分批★)**:
- ★**L171/L172 (camera 侧) 已经是对的** ⇒ 不用动, 只需**核一遍重跑后仍是 2.2k/1.8V**。
- ★**`SW/SW_TIMING_REVIEW.md` §6 的"旧结论翻转"那一段要跟着改口径** (★它现在引的是"注记 2380ns", 落表后注记不存在了⇒ 那条要标"已于 ISS-211 落表修正"★) ⇒ ★**归 SW-lead 落, 本单不碰 SW/★**。

#### ④ 影响面 (★逐项写有没有★)

| 项 | 有没有 | 说清楚 |
|---|---|---|
| ★**BOM 备料** ★ | ★**没有 (实物层面)** ★ | ★**BOM 里 `R_PU_I2CA_SCL` (L116) / `R_PU_I2CA_SDA` (L117) 已经是 `2.2k ±1%` 必装 ⇒ 备的料是对的** ⇒ ★**这条缺陷不产生错料, 只产生错账/错工单** |
| ★**装配** ★ | ★**有 (中)** ★ | ★**贴片工单/装配指导书若照 L167 的 "4.7k 到 3.3V" 出, 就会派错料单** ⇒ ★**改完 SPEC.json 重跑即恢复** |
| ★**板** ★ | ★**没有** ★ | ★**焊盘数/封装不变 (0603 同款), 铜箔不变 ⇒ 不需要改板** ★ |
| ★**评审** ★ | ★**有 (高)** ★ | ★**评审人照 L167 会得出"I2C_A 是 3.3V 域" ⇒ 进而判"SoM 1.8V 脚被灌 3.3V = 过压 P0" ⇒ ★**这是最贵的一种错: 一个假 P0 会把评审带偏** ★ |
| ★**投板** ★ | ★**间接有** ★ | ★**投板前不改 ⇒ 错工单 + 错评审 ⇒ 但料是对的 ⇒ 不会烧板, 会返工** ★ |

#### ⑤ 落表时机

★**整链重出 第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md`) 那一趟, 与 C/E/D 三项合并落表** ⇒ ★**不许单独改 md5** (★板只改一次, 留证链/Gerber/投产包只跑一遍★)。★**翻面条件见 §5★。

#### ⑥ 证据等级

★**[实测]** 全部行号与逐字原文 (2026-11-15 23:5x 实读 `HW/netlist_v1.csv` / `netlist_v1_pins.csv` / `BOM_v1.csv` / `SCHEMATIC_V1_SPEC.json`) · ★**[实测]** `HW/PCB/FET3572C_PIN_TABLE.csv` 里 P2_31/P2_33 的 `vol` 列 = `1.8V` (★SoM 模组厂给的 IO 域表, 是"板级"权威★) · ★**[实测]** `SW/SW_TIMING_REVIEW.md:130` 的"旧结论翻转"原文 · ★**[推算]** t_r / 灌流 (2.2k×100pF×0.847≈186ns; (1.8−0.4)/2.2k=0.64mA) · ★**[推算]** "3.3V 上拉 = 过压"这一步依赖 SoM IO 域表, 不依赖 RK3572 芯片域表 (★见 §6 附带发现 #2★)。

---

### ★★第 (2) 条 ★★ BAT_DET 整条分压链全 DNP, 但 SoC 的 ADC 输入脚是必装 ★★

#### ① 现象 (★网表原文逐字 + 行号★)

★**表A `HW/netlist_v1.csv`**:

| 行 | 原文 (逐字) |
|---|---|
| ★**L181** | `P2,BAT_DET,RAIL_BAT,R_BAT_DET_1,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,[推算],,"方向 充电板→SoC; 电平 0-3.3V (分压); 阻抗 1M+1M 分压 + 100nF; 连接 电池 BAT → ADC; 测试点 TP_BAT",B-08,MAIN_PCB,,` |
| ★**L182** | `P2,BAT,RAIL_BAT,R_BAT_DET_1,R_BAT_DET_1,1M ±1%,R,DNP,[推算],,"[R_BAT_DET_1] ★DNP: 同上 (电池电压分压上臂) | [BAT_DET_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 BAT 已归一到源节点]",B-08,MAIN_PCB,,` |
| ★**L183** | `P2,BAT_DET,R_BAT_DET_2,GND,R_BAT_DET_2,1M ±1%,R,DNP,[推算],,"[R_BAT_DET_2] ★DNP: 同上 (电池电压分压下臂) | [BAT_DET] 分压下臂 地端",B-08,MAIN_PCB,,` |
| ★**L184** | `P2,BAT_DET,C_DET_BAT,R_BAT_DET_2,C_DET_BAT,100nF ±10%,C,DNP,[推算],,"[C_DET_BAT] ★DNP: 同上 (电池 ADC 滤波) | [BAT_DET] ADC 滤波电容 (★V1.2: 电池在镜脚, 本地检测, 不跨铰链)",B-08,MAIN_PCB,,` |
| ★**L185** | `P2,GND,C_DET_BAT,GND,C_DET_BAT,100nF ±10%,C,DNP,[推算],,"[C_DET_BAT] ★DNP: 同上 (电池 ADC 滤波) | [BAT_DET] ADC 滤波电容 地端",B-08,MAIN_PCB,,` |
| ★**L186** | `P2,BAT_DET,J_SOM_P1 pin38,NET_BAT_DET,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,[推算],,"[BAT_DET] SoC ADC 输入节点 (跨板那一侧)",B-08,MAIN_PCB,,` |

★**表B `HW/netlist_v1_pins.csv`**: ★**L307** `R_BAT_DET_1.1` net=`BAT_DET` dnp=**DNP** · ★**L308** `R_BAT_DET_1.2` net=`BAT` · ★**L309** `R_BAT_DET_2.1` net=`BAT_DET` dnp=**DNP** · ★**L310** `R_BAT_DET_2.2` net=`GND` · ★**L100/L101** `C_DET_BAT.1/.2` dnp=**DNP** · ★**L210** `J_SOM_P1.pin38` net=`BAT_DET` dnp=**必装** ⇒ ★**两张表一致地坏 (不是单边漂移)★**。

★**BOM `HW/BOM_v1.csv`**: ★**L86** `R_BAT_DET_1,1,1M ±1%,R,DNP` · ★**L87** `R_BAT_DET_2,…,DNP` · ★**L27** `C_DET_BAT,1,100nF ±10%,C,DNP` ⇒ ★**BOM 也说"不装" ⇒ 装配厂会照做 ⇒ 装出来就是悬空★**。

★**★"同上"指什么, 网表里没写★**: ★**L182/L183/L184/L185 的 note 都写 "★DNP: 同上"** ⇒ ★**"同上"在网表里没有上文 (读者自己猜)** ⇒ ★**这本身也是一处口径洞**。

#### ② 为什么它是缺陷 (★可判定依据★)

1. ★**SoM 的 ADC 输入脚是必装, 而挂在它上面的分压器一颗件都不装** ⇒ ★**= 悬空输入**。★**可判定依据**: ★**L186 (必装) + L181 (必装) vs L182/L183/L184/L185 (全 DNP)**, 且 ★**脚表 L307/L309/L100 (全 DNP) + L210 (必装)** ⇒ ★**同一张表里, 必装的那个脚只连着一颗都不装的器件**。
2. ★**SoM 脚是真的 ADC 输入**: ★**`HW/PCB/FET3572C_PIN_TABLE.csv` → `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5`** ★**(★项目自己的 `HW/PCB/SOM_PIN_ASSIGNMENT.md:9` 也写着 "BAT_DET | SARADC_VIN5 | P1 | 38 | 1AE17 | 1.8V | J_SOM_P1 | 电池电压检测 (1M+1M 分压进 ADC)"★)** ⇒ ★**悬空的是一颗 SAR-ADC 的输入脚, 不是一根无关的测试线**。
3. ★**★再加一层: 就算把 DNP 改成必装, 照 1M+1M 贴上去仍然是过压★**: ★**BAT 满充 4.2V** (★`HW/INTERFACE_TABLE.md` C-03: "4.2V 满 / 3.0V 截止"★) ⇒ ★**1:1 分压中点 = 2.1V**, 而 ★**P1_38 是 1.8V 域** ⇒ ★**2.1V > 1.8V ⇒ 贴上去就是过压** ⇒ ★**所以本条的修法** ★★"把 DNP 翻成必装"是不完整的, 必须同时定分压比★★** (★判据见 §5 R2★)。
4. ★**"同上"没有上文** ⇒ ★**读者无从知道这三只为什么不装** ⇒ ★**要么补上文, 要么把 note 写完整 (★落表那趟一并改★)**。

#### ③ 修法 (★精确到改哪个文件的哪个字段★)

★**修法分两步, 都在整链重出那一趟落**:

| 步骤 | 改哪个文件 | 改哪个字段 | 说明 |
|---|---|---|---|
| ★**3a 装上** ★ | ★`HW/netlist_v1.csv` ★ | ★**L182 / L183 / L184 / L185 的 `dnp` 列 (第 8 列)**: `DNP` → ★`必装` ★ | ★**R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT 三只 (共 4 行) 一起改** ⇒ ★**不许只改一半 (那会造成"一颗装了另一颗没装"的鬼状态)★** |
| ★**3a' 脚表同步** ★ | ★`HW/netlist_v1_pins.csv` ★ | ★**L307 / L309 / L100 (及 L308/L310/L101) 的 `dnp` 列 (第 8 列)**: `DNP` → ★`必装` ★ | ★**表A/表B 必须同改 (★项目老规矩: 漏一边 = 网表和脚表打架★)** |
| ★**3b 分压比** ★ | ★`HW/netlist_v1.csv` ★ | ★**L182 / L183 的 `value` 列 (第 6 列)**: `1M ±1%` → ★新阻值 ★ | ★**判据 (★必须同时满足三条, 缺一条不许落★)**: ① ★**BAT_max = 4.2V 时, 中点 ≤ 1.8V** (⇒ 上/下臂比 ≥ 2.33:1) ★ ② ★**源阻抗满足 SoM ADC 采样要求 (★⚠ 该参数项目库目前没有 ⇒ [0数据] ⇒ 见 §7 未决项 U-2★)** ★ ③ ★**分压后满量程利用率不能太低 (★否则 12bit 分辨率浪费★)** ★ |
| ★**3c note 补上文** ★ | ★`HW/netlist_v1.csv` ★ | ★**L182/L183/L184/L185 的 `note` 列 (第 11 列)** ★ | ★**把 "★DNP: 同上" 换成写全的句子 (★为什么装/为什么曾 DNP/分压比怎么来的★) ⇒ 消掉"读者自己猜"的口径洞** ★ |
| ★**3d 脚表 note 对齐** ★ | ★`HW/netlist_v1_pins.csv` ★ | ★**L210 `J_SOM_P1.pin38` 的 `note` 列** ★ | ★**现在 L210 的 note 是 L206 (`J_SOM_P1.pin100` / VBUS_DET) 的复制品 (★"[VBUS_DET] ★SoM 的 USB_DRD1_VBUSDET (P1_100)…"★) ⇒ ★**同一个脚号写着别的信号的名字 ⇒ 必须改成 BAT_DET 的说明★** (★表A L186 的 note 是对的: "[BAT_DET] SoC ADC 输入节点"★) ★ |

★**⚠ 3b 的阻值本单不定 (★不替老板拍★)**: ★**分压比的上限 (1.8V) 由项目库能定, 但"ADC 满量程 / 源阻抗要求"项目库没有 ⇒ ⇒ 落表前必须先关掉 §7 的 U-2, 否则会把一颗 1.8V 域 ADC 脚烧掉**。

#### ④ 影响面

| 项 | 有没有 | 说清楚 |
|---|---|---|
| ★**BOM 备料** ★ | ★**有 (高)** ★ | ★**现在 BOM 明写 DNP ⇒ 备料单不含这 3 只 ⇒ 落表后要补 1M×2 + 100nF×1 (★若分压比改, 料号也要改★)** ★ |
| ★**装配** ★ | ★**有 (高)** ★ | ★**现在 DNP = 不贴 ⇒ 装出来 SoM 读到的是浮空噪声 ⇒ 电池电量显示乱跳 / 关机判据误触发 (★软件侧那两处必须同步知道"这脚现在才有意义"★)** ★ |
| ★**板** ★ | ★**没有** ★ | ★**3 只件的焊盘/封装都在板上 (★板文件里 DNP 件照样有封装★) ⇒ 不用改板** ★ |
| ★**评审** ★ | ★**有 (高)** ★ | ★**评审人必须知道"这脚是 SARADC_VIN5, 且当前是悬空" ⇒ 不然会把"电池电量读不准"当成软件 bug 去查** ★ |
| ★**投板** ★ | ★**有 (高)** ★ | ★**投板后才发现 = 改板 = 2-4 周 + ¥4-8K** ★ |

#### ⑤ 落表时机

★**整链重出 第 1 步 那一趟 (★与 C/E/D 合并★)**, ★**但 3b 阻值必须先关掉 §7 的 U-2 (★SoM ADC 参数★) ⇒ 若 U-2 在那趟之前关不了 ⇒ 这一条单独拆出去做 (★改板可不做, 改网表要做 ⇒ 会多跑一趟生成器★)**。

#### ⑥ 证据等级

★**[实测]** 全部行号与逐字原文 (表A/表B/BOM 三处) · ★**[实测]** `FET3572C_PIN_TABLE.csv` → P1_38 = `SARADC_VIN5` / 1.8V 域 (★SoM 厂 IO 域表★) · ★**[实测]** `SOM_PIN_ASSIGNMENT.md:9` 的 BAT_DET 归属行 · ★**[实测]** `HW/INTERFACE_TABLE.md` C-03 电池 4.2V 满 / 3.0V 截止 · ★**[推算]** "1:1 分压中点 2.1V > 1.8V ⇒ 过压" (★依赖 SoM ADC 脚的 abs-max 判据, 该判据本身 [0数据] ⇒ 见 §6 附带发现 #3★) · ★**[0数据]** SoM SAR-ADC 的满量程范围 / 源阻抗要求 / abs-max。

---

### ★★第 (3) 条 ★★ U_EN_SW 没有器件本体行 ⇒ BOM 里这颗 IC 被登记成 NET 行 ★★

#### ① 现象 (★网表原文逐字 + 行号★)

★**表A `HW/netlist_v1.csv` 里 `ref == U_EN_SW` 的行只有 4 行, `type` 全是 `NET`**:

| 行 | 原文 (逐字) |
|---|---|
| ★**L441** | `P1,CARRIER_BOARD_EN,U_EN_SW pin2,CARRIER_BOARD_EN,U_EN_SW,EN 输入 (高=放行底板),NET,必装,[官方],,"[U_EN_SW] EN ← CARRIER_BOARD_EN ⇒ 主板各路只在 SoM 就绪后上电",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` |
| ★**L442** | `P1,RAIL_DEMO_5V,U_EN_SW pin1,RAIL_DEMO_5V,U_EN_SW,5V 输入,NET,必装,[官方],,"[U_EN_SW] IN = 5V (Type-C 直供)",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` |
| ★**L443** | `P1,RAIL_BOARD_5V,U_EN_SW pin3,RAIL_BOARD_5V,U_EN_SW,5V 输出 (受 CARRIER_BOARD_EN 门控),NET,必装,[官方],,"[RAIL_BOARD_5V] ★**底板所有 3.3V/5V 支路都挂这条** (不是 SYS) ⇒ 这就是 F13 的落法",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` |
| ★**L444** | `P1,GND,U_EN_SW pin4,GND,U_EN_SW,GND,NET,必装,[官方],,"[U_EN_SW] 地",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` |

★**表B `HW/netlist_v1_pins.csv`**: ★**L531/L532/L533/L534** = `U_EN_SW.pin1..pin4`, ★**`type` 也全是 `NET`** ⇒ ★**两张表都缺本体行**。

★**★对照: 同一块板上同类器件 `U_PWR_SW` 有本体行★** ⇒ ★**表A L50**: `P1,SYS,U_PWR_SW pin3,RAIL_SYS,U_PWR_SW,"[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)",IC,必装,[推算],…` ⇒ ★**表B 里 `U_PWR_SW.pin3` 的 `type` 也是 `IC`, value 同样是器件身份描述 ⇒ 这就是"器件本体行"的正确写法 (★本体行挂在其中一脚上, 其余脚是 NET 行★)**。

★**后果已经在 BOM 上显形** ⇒ ★**`HW/BOM_v1.csv` L208**: `U_EN_SW,1,EN 输入 (高=放行底板),NET,必装,镜脚主 PCB,P1,[官方],,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA,待定,待定,待分类,` ⇒ ★**一颗 4 脚 IC 的 value 栏里躺着一句脚功能串, type 栏是 NET**。

★**★连板文件也被传染了 (★main 没提到这一层, 是本单新挖的★)★** ⇒ ★**板文件 `HW/PCB/demo_mainboard.kicad_pcb` 里 `U_EN_SW` 封装 (★4 焊盘★) 的 `Value` 属性 = "EN 输入 (高=放行底板)"** ⇒ ★**根因在 `state/gen_pcb_components.py:156`: `fp.SetValue(per_ref[ref][0][2][:40] …)` ⇒ 板封装 Value = 该 ref 在网表里**第一行**的 value ⇒ 网表缺本体行 ⇒ 第一行是 NET 行 ⇒ 脚功能串被写进板文件 ⇒ ⇒ ★**BOM 的"板文件 Value 兜底"也就跟着取了这句话**。

#### ② 为什么它是缺陷 (★可判定依据★)

1. ★**可判定依据 (口径写在生成器自己的注释里)**: ★**`state/gen_bom.py:143` `_pick_value()` 文档**: 「★**器件本体行 (type 不是 'NET') 的 value = 器件身份描述**; ★**网节点行 (type='NET') 的 value = 脚级功能串**」⇒ ★**没有本体行 ⇒ BOM 取到的必然是脚级功能串**。
2. ★**同一块板上一颗同类器件有本体行、一颗没有** ⇒ ★**口径不一致 = 板厂/采购/装配三方看 BOM 会对不上**。
3. ★**BOM 的 `type` 栏是 `NET`** ⇒ ★**任何按 type 分组/筛选的工具 (备料台账、SMT 上料单、贴片程序) 都会把 U_EN_SW 当成"网节点"而不是"器件"** ⇒ ★**"待分类" 那一栏就是它** (★BOM L208 的 `procurement` 栏 = `待分类`★)。
4. ★**它同时污染了板文件** (★见 ① 最后一段★) ⇒ ★**改网表不够, 板的封装 Value 也得改 ⇒ 这一条是"要改板"的**。

#### ③ 修法 (★精确到改哪个文件的哪个字段★)

| 步骤 | 改哪个文件 | 改什么 | 说明 |
|---|---|---|---|
| ★**3e 加器件本体行** ★ | ★**`state/gen_netlist.py`** ★ | ★**在 U_EN_SW 那 4 条 `add(...)` (★现 L1474-L1483★) 附近补一条 `type="IC"` 的器件本体行 ★ | ★**这是生成器的改动, 不是网表的手改** ⇒ ★**⚠ 本单禁止改生成器 ⇒ 这一步归"整链重出第 1 步"那一趟做★** ★**写法照抄 `U_PWR_SW` 的本体行 (表A L50): `add(page, net, node, node, "U_EN_SW", "<器件身份描述>", "IC", dnp, ev, tbd, note, conn_id)` ★**★**⚠ 器件身份描述本单不定型号 (★ISS-172 还是 open, 老板级★) ⇒ 先用与 `U_PWR_SW` 同格式的判据串 (★"[待选型] 负载开关 (…)"★), 型号等 ISS-172 落** ★ |
| ★**3f 脚表同步** ★ | ★**`state/gen_netlist_pins.py`** ★ | ★**让脚表里 U_EN_SW 也有一条 `type=IC` 的本体行 ★ | ★**现在脚表 `U_PWR_SW.pin3` 有 `type=IC` ⇒ 照抄它的逻辑即可** ★ |
| ★**3g BOM 修完自动对** ★ | ★**不用改 `state/gen_bom.py`** ★ | — | ★**`_pick_value` 的第①档 (本体行众数) 一旦有本体行就自动取到器件身份描述 ⇒ BOM 的 type 栏由 netlist 行派生 ⇒ 自动变 `IC`** ★ |
| ★**3h 板文件 Value 跟着改** ★ | ★**`HW/PCB/demo_mainboard.kicad_pcb` 里 `U_EN_SW` 封装的 `Value` 属性 ★** ★**⇒ 由 `state/gen_pcb_components.py:156` 在重出板时自动刷 (★它取网表第一行的 value ⇒ 有了本体行且本体行排在前面 ⇒ Value 就对了★)** ★ | — | ★**⚠ 这是"要改板"的一条 ⇒ 必须跟第 1 步那一趟一起改, 不许单独动板** ★ |

★**⚠ 排序坑 (★落表那趟必须注意★)**: ★**`gen_pcb_components.py:156` 取的是"第一行" ⇒ ⇒ 本体行必须排在 U_EN_SW 那 4 条 NET 行之前, 否则板的 Value 还是脚功能串** ⇒ ★**落表后必须核板文件 `U_EN_SW` 封装的 `Value` 属性** (★门禁 §5 R3 已把这一项做成硬判据★)。

#### ④ 影响面

| 项 | 有没有 | 说清楚 |
|---|---|---|
| ★**BOM 备料** ★ | ★**有 (高)** ★ | ★**`type=NET` ⇒ 这颗 IC 在备料台账里被登记成"网节点" ⇒ `procurement=待分类` ⇒ ★**这颗是 F13 的底板上电许可关键件 (★型号待定 ★ ISS-172★) ⇒ 不定类型, 采购台账就漏掉它** ★ |
| ★**装配** ★ | ★**有 (中)** ★ | ★**SMT 上料/贴片程序按 type 分组 ⇒ `NET` 类可能被当成"不上料"的虚拟件** ★ |
| ★**板** ★ | ★**有 (中)** ★ | ★**板封装的 `Value` 属性 = "EN 输入 (高=放行底板)" ⇒ 板上的丝印/属性也是错的 (★这块板要送盖印/投产包 ⇒ 属性错会被板厂看到★)** ★ |
| ★**评审** ★ | ★**有 (中)** ★ | ★**评审人查一颗 4 脚 IC 却找不到器件行 ⇒ 只能靠脚行反推** ★ |
| ★**投板** ★ | ★**有 (中)** ★ | ★**不改板 ⇒ 投产包/盖印里的器件属性是错的; ★**但** ★**注意: 这条的电气本身是对的** (★板文件实测 pad→net: pad1=`RAIL_DEMO_5V` / pad2=`CARRIER_BOARD_EN` / pad3=`RAIL_BOARD_5V` / pad4=`GND`★ ⇒ ★**F13 门控功能不受影响★) ⇒ **不会烧板, 会返工 + 台账漏件** ★ |

#### ⑤ 落表时机

★**整链重出 第 1 步 那一趟 (★C/E/D + 本条合并★)**, ★**因为它要改生成器 + 改板** ⇒ ★**必须并进"板只改一次"那一趟**。

#### ⑥ 证据等级

★**[实测]** 全部行号与逐字原文 (表A/表B/BOM) · ★**[实测]** 板文件 `U_EN_SW` 封装的 `Value` 属性与 4 个焊盘的 net 归属 · ★**[实测]** `state/gen_bom.py:143` 与 `state/gen_pcb_components.py:156` 的注释与代码 · ★**[实测]** `state/gen_netlist.py:1471-1483` 的 4 条 `add(...)` (★★用 `add(...)` 逐脚建 NET 行, 缺一条 `type=IC` 的器件本体行★★) · ★**[官方]** U_EN_SW 的电路功能来源 = Forlinx 载板指引 (F13) (★网表 evidence 列已标 [官方]★) · ★**[0数据]** 具体型号 (★ISS-172, 老板级★)。

---

### ★★第 (4) 条 ★★ USB D− 全程没有 ESD, 而那颗器件自称"双通道" ★★

#### ① 现象 (★网表原文逐字 + 行号★)

★**表A `HW/netlist_v1.csv`**:

| 行 | 原文 (逐字) |
|---|---|
| ★**L417** | `P1,USB_D_P_SRC,D_ESD_USB_D,USB_D_P_SRC,D_ESD_USB_D,ESD 阵列 [待选型] (USB 2.0 双通道),D,必装,[推算],,"[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**",A-24,MAIN_PCB,,` |
| ★**L418** | `P1,GND,D_ESD_USB_D,GND,D_ESD_USB_D,ESD 阵列 [待选型],D,必装,[推算],,"[D_ESD_USB_D] ESD 地端",A-24,MAIN_PCB,,` |
| ★**L432** | `P1,NET_USB_D_N_TYPEC,R_SER_USB_D_N,J_USB_C A7+B7,R_SER_USB_D_N,22Ω ±1%,R,必装,[推算],,"[NET_USB_D_N_TYPEC] ★SoM USB2 (OTG1) D- → 板载 Type-C: 串阻的 Type-C 侧",A-24,MAIN_PCB,,` |
| ★**L431** | `P1,NET_USB_D_P_TYPEC,R_SER_USB_D_P,J_USB_C A6+B6,R_SER_USB_D_P,22Ω ±1%,R,必装,[推算],,"[NET_USB_D_P_TYPEC] ★SoM USB2 (OTG1) D+ → 板载 Type-C: 串阻的 Type-C 侧 (★串阻必须真串在中间, 不能与 SoM 侧同网★)",A-24,MAIN_PCB,,` |

★**板文件封装 (★实测★)**: ★**`D_ESD_USB_D` 只有 2 个焊盘** (`1`, `2`) ⇒ ★**BOM `HW/BOM_v1.csv` L62 的 footprint 栏原文**: `★板文件封装: 2 焊盘 (ESD 阵列 [待选型] (USB 2.0 双通道))` ⇒ ★**"双通道"是 value 栏的一句自称, 封装只有 2 个焊盘**。

★**★板面实测 (★`HW/PCB/demo_mainboard.kicad_pcb` 焊盘→net 实读★)**:
| 位号 | 焊盘 → net | 板面坐标 (mm) | 到 `J_USB_C` 距离 |
|---|---|---|---|
| `D_ESD_USB_D` | pad1 → `USB_D_P_SRC` · pad2 → `GND` | (94.95, 21.80) | ★**47.99 mm** ★ |
| `R_SER_USB_D_P` | pad1 → `USB_D_P_SRC` · pad2 → `NET_USB_D_P_TYPEC` | (89.70, 21.50) | 52.86 mm |
| `R_SER_USB_D_N` | pad1 → `USB_D_N_SRC` · pad2 → `NET_USB_D_N_TYPEC` | (107.70, 23.50) | 37.10 mm |
| `D_ESD_DEMO` (VBUS 用) | pad1 → `RAIL_DEMO_5V` · pad2 → `GND` | (98.75, 9.80) | 41.50 mm |
| `J_USB_C` | — | (140.00, 5.25) | — |

★**★D− 那条路上一个 ESD 位号都没有 (★实测: 板上 4 个 ESD 位号 `D_ESD_CAM` / `D_ESD_DEMO` / `D_ESD_LIGHT` / `D_ESD_USB_D`, 焊盘 net 逐个查过, 挂 `USB_D_N_SRC` 或 `NET_USB_D_N_TYPEC` 的 = 0 个★)**。

#### ② 为什么它是缺陷 (★可判定依据★)

1. ★**名不副实**: value 写「ESD 阵列 [待选型] (USB 2.0 **双通道**)」, ★**封装只有 2 焊盘** ⇒ ★**D+ 一路进了 ESD, GND 是回流不是第二路数据** ⇒ ★**"双通道"这三个字是假的**。
2. ★**Type-C 入口只护了差分的一边**: ★**D− (`NET_USB_D_N_TYPEC` → `R_SER_USB_D_N` → `J_USB_C A7+B7`) 全程无 ESD** ⇒ ★**Type-C 入口只护了 D+**。
3. ★**★讽刺的是 L417 自己的 note 就引了规矩★**: 「★**Forlinx 载板指引要求 ESD 紧贴接口**」⇒ ★**引用了规矩, 自己没照做 (护了一半)**。
4. ★**★而且连"紧贴"也没做到 (★本单实测, 比"护了一半"更差★)**: ★**ESD 的 `pad1` 挂在 `USB_D_P_SRC`, 而 `USB_D_P_SRC` 是 22Ω 串阻的【SoM 侧】; 真正贴连接器的那一侧是 `NET_USB_D_P_TYPEC` (串阻的 Type-C 侧) ⇒ ★**这个 ESD 既不在连接器旁边, 也不在差分对的正确一侧** ⇒ ★**板面实测距 `J_USB_C` 47.99 mm (板上是 60×30 mm 的一角)** ⇒ ★**note 里的"紧贴 J_USB_C"这句话, 板文件实测证伪**。
5. ★**可判定依据 (门禁已做成硬判据)**: ★**① 板封装 `D_ESD_USB_D` 焊盘数 = 2; ② 它的 `Value` 属性自称"双通道"; ③ 板上挂 `USB_D_N_SRC`/`NET_USB_D_N_TYPEC` 的 ESD 位号数 = 0** ⇒ 三条都是机器可判的。

#### ③ 修法 (★精确到改哪个文件的哪个字段★)

★**本条必须动板 ⇒ 只出规格, 不许自己动板★**:

| 步骤 | 改哪个文件 | 改什么 | 说明 |
|---|---|---|---|
| ★**3i 器件行 + 脚行** ★ | ★**`state/gen_netlist.py`** ★ | ★**UEN 段落: 把 `D_ESD_USB_D` 从"1 只 2 脚"改成"★**覆盖 D+ 与 D− 两路的 ESD 阵列 (3 脚: D+ / D− / GND)★**"** ★ | ★**两种落法, ★**老板/总工拍板选一种 (★本单只列选项 + 判据, 不定型号、不定方案★)★**: ① ★**换 3 脚双通道阵列封装 (D_ESD_USB_D 改成 3 焊盘, pin1=D+ / pin2=D− / pin3=GND) ⇒ 改板 + 改封装库** ★ ② ★**保留现有 2 脚件, ★**另加一只** `D_ESD_USB_D_N` (2 脚: D− + GND), 放在 `J_USB_C` 旁边 ⇒ 改板 (加位号) + 网表加 2 行 (L417/L418 同款) ★ |
| ★**3j 位置** ★ | ★**板布局** ★ | ★**ESD 必须落在【连接器侧】: ★**即 `NET_USB_D_P_TYPEC` / `NET_USB_D_N_TYPEC` 那一侧 (★串阻的 Type-C 侧★), ★**不是现在的 `USB_D_P_SRC` (SoM 侧)** ★ | ★**判据: ★**到 `J_USB_C` 的板面距离 ≤ 5 mm (★现在 47.99 mm★) ⇒ 落表那趟必须量** ★ |
| ★**3k value 文案** ★ | ★**网表 value 列 + 板封装 Value 属性** ★ | ★**去掉或兑现"双通道"三个字 ★ | ★**若选方案① ⇒ value 改成"ESD 阵列 (USB 2.0 双通道, D+ / D− 共用一颗)"且封装真的 3 脚; ★**若选方案② ⇒ value 改成"ESD 阵列 (USB 2.0, 单通道 D+)" + 另加 `D_ESD_USB_D_N` 的对应行 ⇒ ★**不许留"名不副实"的字样** ★ |
| ★**3l note** ★ | ★**网表 note 列** ★ | ★**L417 的 note 里 "紧贴 J_USB_C" 只有在 3j 真的做到时才能留** ★ | ★**⇒ 落表后必须复量距离, 量不到 5mm 就把这句话删掉/改成实测值** ★ |
| ★**3m 选型** ★ | ★**—** ★ | ★**型号 / 封装 / 工作电压 / 结电容 (★USB 2.0 ≤ 3 pF 量级★) / IEC 61000-4-2 等级 ★ | ★**★本单不定型号 (★老板级 + 零外发 ⇒ 型号一律 [待选型] + 判据★)★** |

#### ④ 影响面

| 项 | 有没有 | 说清楚 |
|---|---|---|
| ★**BOM 备料** ★ | ★**有 (高)** ★ | ★**现在 BOM 只有 1 只 2 脚的 D_ESD_USB_D, 且 value 自称双通道 ⇒ 采购要么买到 2 脚件 (不保护 D−), 要么买到 3 脚件但封装对不上 (贴不上)** ★ |
| ★**装配** ★ | ★**有 (中)** ★ | ★**"双通道"字样会误导贴片工单/检验单** ★ |
| ★**板** ★ | ★**有 (高)** ★ | ★**★这一条是 4 条里最"必须改板"的: ① 封装从 2 脚 → 3 脚 (方案①) 或加一个新位号 (方案②); ② ★**ESD 位置要挪到 J_USB_C 旁 (现在 47.99 mm) ⇒ 这是布局改动 ⇒ 要重跑布线** ★ ⇒ ★**⇒ 必须并进"板只改一次"那一趟, 不许单独动板★** ★ |
| ★**评审** ★ | ★**有 (中)** ★ | ★**ESD 缺失在评审里通常是"记一笔"的小项, 但它是 Type-C 入口唯一的机械防护 ⇒ 评审结论会记"入口 ESD 不完整"** ★ |
| ★**投板** ★ | ★**有 (高)** ★ | ★**Type-C 插拔是日常动作 ⇒ D− 无 ESD = 一次插拔静电就可能打穿 SoM 的 USB 收发器 ⇒ ★**这是 4 条里唯一的"用了就可能坏"的条目** ★ |

#### ⑤ 落表时机

★**整链重出 第 1 步 那一趟 (★必须与 C/E/D 合并, 因为它要改板 + 重跑布线★)**, ★**但前提是 §7 的 U-1 (ESD 选型/方案二选一) 先落**。

#### ⑥ 证据等级

★**[实测]** 全部行号与逐字原文 (表A) · ★**[实测]** 板文件: `D_ESD_USB_D` 2 焊盘 + `Value` 属性 + 4 个 ESD 位号的焊盘 net 归属 (★D− 上 0 个★) · ★**[实测]** 板面坐标与距离 (`D_ESD_USB_D` → `J_USB_C` = 47.99 mm) · ★**[官方]** "ESD 紧贴接口" 这条规矩 = Forlinx 载板指引 (★L417 的 note 自己引的★) · ★**[0数据]** 具体 ESD 型号 / 结电容 / 钳位电压 / IEC 等级 (★老板级选型 + 零外发★)。

---

## 2. ★★4 条的机读汇总 (★门禁锚点表 = 唯一真源在 `HW/check_netlist_selfconsistency.py` 的 `EXPECT`★) ★★

| 条 | 机器可判的核心判据 | 现在应为 |
|---|---|---|
| ★(1) ★ | 表A L167/L168 的 value 仍含 "4.7k 到 3.3V" + L169/L170 是 2.2k/VDD_1V8_IO + L169 note 仍含 "已作废" + SPEC.json B-01/B-02 的 `level` 仍 = 3.3V | ★**成立 (缺陷在)** ★ |
| ★(2) ★ | 表A L182/L183/L184/L185 与表B L100/L307/L309 的 `dnp` 仍 = DNP, 而 L181/L186/L210 是必装 | ★**成立 (缺陷在)** ★ |
| ★(3) ★ | 表A/表B 里 `ref==U_EN_SW` 的行数 = 4 且 `type!=NET` 的行数 = **0**; BOM L208 的 type = NET; 板封装 `U_EN_SW` 的 Value = 脚功能串 | ★**成立 (缺陷在)** ★ |
| ★(4) ★ | 板封装 `D_ESD_USB_D` 焊盘数 = 2 + Value 自称双通道 + 挂 D− 两张网的 ESD 位号数 = 0 | ★**成立 (缺陷在)** ★ |

★**锚点表 (★机读; 门禁脚本会逐条比对这张表, 漂移即红★)★**

<!-- ANCHORS:BEGIN -->
| key | file | line | check |
|---|---|---|---|
| d1_a167_value | netlist | 167 | value == 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF) |
| d1_a167_ref | netlist | 167 | ref == NET_I2C_A_SCL |
| d1_a168_value | netlist | 168 | value == 上拉 4.7k 到 3.3V |
| d1_a168_ref | netlist | 168 | ref == NET_I2C_A_SDA |
| d1_a169_value | netlist | 169 | value == 2.2k ±1% |
| d1_a169_net | netlist | 169 | net == VDD_1V8_IO |
| d1_a169_ref | netlist | 169 | ref == R_PU_I2CA_SCL |
| d1_a169_note | netlist | 169 | note contains 已作废 |
| d1_a170_value | netlist | 170 | value == 2.2k ±1% |
| d1_a170_net | netlist | 170 | net == VDD_1V8_IO |
| d1_a171_value | netlist | 171 | value contains 上拉 2.2k 到 1.8V |
| d1_b367_net | pins | 367 | net == I2C_A_SCL |
| d1_b368_net | pins | 368 | net == VDD_1V8_IO |
| d1_spec_b01_level | spec | ? | spec.connections[id=B-01].level == 3.3V |
| d1_spec_b01_imp | spec | ? | spec.connections[id=B-01].imp == 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF) |
| d1_spec_b02_level | spec | ? | spec.connections[id=B-02].level == 3.3V |
| d1_spec_b02_imp | spec | ? | spec.connections[id=B-02].imp == 上拉 4.7k 到 3.3V |
| d2_a181_ref | netlist | 181 | ref == NET_BAT_DET |
| d2_a181_dnp | netlist | 181 | dnp == 必装 |
| d2_a182_ref | netlist | 182 | ref == R_BAT_DET_1 |
| d2_a182_dnp | netlist | 182 | dnp == DNP |
| d2_a182_value | netlist | 182 | value == 1M ±1% |
| d2_a182_note | netlist | 182 | note contains DNP: 同上 |
| d2_a183_ref | netlist | 183 | ref == R_BAT_DET_2 |
| d2_a183_dnp | netlist | 183 | dnp == DNP |
| d2_a184_ref | netlist | 184 | ref == C_DET_BAT |
| d2_a184_dnp | netlist | 184 | dnp == DNP |
| d2_a185_ref | netlist | 185 | ref == C_DET_BAT |
| d2_a185_dnp | netlist | 185 | dnp == DNP |
| d2_a186_node1 | netlist | 186 | node1 == J_SOM_P1 pin38 |
| d2_a186_dnp | netlist | 186 | dnp == 必装 |
| d2_a186_note | netlist | 186 | note contains [BAT_DET] SoC ADC 输入节点 |
| d2_b307_dnp | pins | 307 | dnp == DNP |
| d2_b309_dnp | pins | 309 | dnp == DNP |
| d2_b100_dnp | pins | 100 | dnp == DNP |
| d2_b210_net | pins | 210 | net == BAT_DET |
| d3_a441_type | netlist | 441 | type == NET |
| d3_a441_value | netlist | 441 | value == EN 输入 (高=放行底板) |
| d3_a442_type | netlist | 442 | type == NET |
| d3_a443_type | netlist | 443 | type == NET |
| d3_a444_type | netlist | 444 | type == NET |
| d3_a_rows | netlist | ? | count(ref==U_EN_SW) == 4 |
| d3_a_body | netlist | ? | count(ref==U_EN_SW&type!=NET) == 0 |
| d3_b_rows | pins | ? | count(ref==U_EN_SW) == 4 |
| d3_b_body | pins | ? | count(ref==U_EN_SW&type!=NET) == 0 |
| d3_bom208_type | bom | 208 | type == NET |
| d3_bom208_value | bom | 208 | value == EN 输入 (高=放行底板) |
| d3_board_value | board | ? | footprint.U_EN_SW.value == EN 输入 (高=放行底板) |
| d3_board_pads | board | ? | footprint.U_EN_SW.pads == 4 |
| d3_ctrl_a50_type | netlist | 50 | type == IC |
| d4_a417_value | netlist | 417 | value == ESD 阵列 [待选型] (USB 2.0 双通道) |
| d4_a417_net | netlist | 417 | net == USB_D_P_SRC |
| d4_a417_dnp | netlist | 417 | dnp == 必装 |
| d4_a417_note | netlist | 417 | note contains Forlinx 载板指引要求 ESD 紧贴接口 |
| d4_a418_value | netlist | 418 | value == ESD 阵列 [待选型] |
| d4_a432_net | netlist | 432 | net == NET_USB_D_N_TYPEC |
| d4_a432_ref | netlist | 432 | ref == R_SER_USB_D_N |
| d4_esd_pads | board | ? | footprint.D_ESD_USB_D.pads == 2 |
| d4_esd_value | board | ? | footprint.D_ESD_USB_D.value == ESD 阵列 [待选型] (USB 2.0 双通道) |
| d4_esd_pad1_net | board | ? | footprint.D_ESD_USB_D.pad1.net == USB_D_P_SRC |
| d4_esd_pad2_net | board | ? | footprint.D_ESD_USB_D.pad2.net == GND |
| d4_esd_on_dminus | board | ? | esd_on_net(USB_D_N_SRC,NET_USB_D_N_TYPEC) == 0 |
| d4_bom62_value | bom | 62 | value == ESD 阵列 [待选型] (USB 2.0 双通道) |
| d4_bom62_fp | bom | 62 | footprint contains 2 焊盘 |
<!-- ANCHORS:END -->

★**★机器门禁怎么用 (★`HW/check_netlist_selfconsistency.py`★)★★**
```
$ python3 HW/check_netlist_selfconsistency.py                # ★现状守卫★ (现在应 rc=0)
$ python3 HW/check_netlist_selfconsistency.py --verbose      # 逐条锚点明细
$ python3 HW/check_netlist_selfconsistency.py --selftest     # ★反向用例: 改坏任一锚点 ⇒ 必须变红★
$ python3 HW/check_netlist_selfconsistency.py --expect-resolved   # ★翻面口径★ (落表后才 rc=0)
$ python3 HW/check_netlist_selfconsistency.py --emit-anchors # 重新生成上面那张锚点表
```

---

## 3. ★★根因链 (★为什么真修法不在网表里★)★★

| 条 | 现象层 | ★真根因层 (★手改这层 = 改在产物上, 下次重跑生成器就没了★)★★ | 手改网表的后果 |
|---|---|---|---|
| ★(1) ★ | 表A L167/L168 的 value 写错 | ★**`HW/SCHEMATIC_V1_SPEC.json` 的 `connections[B-01/B-02].level` + `.imp`** ★(★`state/gen_netlist.py:770` `conn_row()`: "value 默认取规格 imp"★) | ★重跑 `gen_netlist.py` ⇒ 错值原样回来 ★ |
| ★(2) ★ | 表A/表B/BOM 三处的 `dnp` 全 DNP | ★**`state/gen_netlist.py` 里 BAT_DET 那段的 `add(...)` 源头 (★外加 SoM ADC 参数缺失 ⇒ 没人定过分压比★)** ★ | ★同上 ★ |
| ★(3) ★ | 表A/表B 缺 `type=IC` 本体行 ⇒ BOM 取到脚功能串 | ★**`state/gen_netlist.py:1471-1483` 缺一条 `type=IC` 的器件本体行** ★ ⇒ ★**连锁: `state/gen_netlist_pins.py` 脚表 / `state/gen_bom.py:143` `_pick_value` 无本体行可取 / `state/gen_pcb_components.py:156` 把脚功能串写进板封装 Value** ★ | ★同上 + ★**板封装的 Value 也回错★ ★ |
| ★(4) ★ | `D_ESD_USB_D` 2 脚却自称双通道; D− 无 ESD | ★**`state/gen_netlist.py` 里 USB ESD 那段的器件定义 + 板侧封装/布局** ★ | ★同上 ★ |

★**⇒ 4 条的落表都要动生成器 ⇒ ⇒ 必须并进"整链重出 第 1 步"那一趟 (★`state/RECHAIN_STEP1_LANDING_SPEC.md`★) ⇒ ⇒ 本单只出规格 + 门禁, 一个字节都不动★**。

---

## 4. ★★落表时机总表 (★★全部并进整链重出第 1 步, 不许单独改 md5★)★★

| 条 | 改网表? | 改脚表? | 改板? | 改生成器? | 改 SPEC.json? | ★归哪一趟★ |
|---|---|---|---|---|---|---|
| ★(1) I2C_A 上拉 ★ | ✔ (重跑生成器后自动) | ✔ (自动) | ✘ | ✘ | ★**✔ (B-01/B-02)** ★ | ★**第 1 步 (C/E/D 合并那一趟)** ★ |
| ★(2) BAT_DET 分压链 ★ | ✔ | ✔ | ✘ | ✔ | ✘ | ★**第 1 步, 但 3b 阻值须先关 U-2** ★ |
| ★(3) U_EN_SW 本体行 ★ | ✔ (重跑后) | ✔ (重跑后) | ★**✔ (封装 Value)** ★ | ★**✔** ★ | ✘ | ★**第 1 步 (★要改板 ⇒ 必须合并★)** ★ |
| ★(4) USB D− ESD ★ | ✔ | ✔ | ★**✔ (封装 + 位置)** ★ | ★**✔** ★ | ✘ | ★**第 1 步 (★要改板 + 重跑布线⇒ 必须合并★), 前提 U-1 先落** ★ |

★**★落表那趟的验收判据 (★4 条各自一条, 缺一条不许投板★)★★**
- **(1)** ★表A 不再有任何 value 含 "4.7k 到 3.3V" / "2.38µs"; SPEC.json B-01/B-02 的 level ≠ 3.3V 且 imp 含 2.2k/1.8V; ★**并且** NET 行与器件行逐字一致 (2.2k / RAIL_VDD_1V8_IO) ★
- **(2)** ★`R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` 在表A/表B/BOM 三处的 `dnp` 全部 ≠ DNP; ★**并且** ★**分压后中点电压 @4.2V ≤ 1.8V** (★门禁 R2 会自己算★) ★
- **(3)** ★表A/表B 各有 ≥1 条 `ref==U_EN_SW` 且 `type==IC` 的本体行; BOM 里 U_EN_SW 的 type = IC; ★**板封装 `U_EN_SW` 的 Value 属性不再是脚功能串** ★
- **(4)** ★板上挂 `USB_D_N_SRC` 或 `NET_USB_D_N_TYPEC` 的 ESD 位号数 ≥ 1; ★**且** ESD 到 `J_USB_C` 的板面距离 ≤ 5 mm; ★**且** value 不再自称"双通道"而封装不是双通道 ★

---

## 5. ★★★门禁的 rc 口径 + ★★翻面条件★★ ★★

### 5.1 ★★现在的 rc=0 是什么意思 (★重要, 别误读★)★★

★**`python3 HW/check_netlist_selfconsistency.py` 现在 rc=0 ⇒ 只是说"★现状与本规格页逐字一致★" ⇒ ★★"4 条缺陷仍在"才是预期状态★ ★**
★**⇒ 这个门禁是【现状守卫】, 不是【合格证】** ⇒ ★**它防的是"网表被静默改了而规格页没跟" (★也就是本单最怕的那件事: 下一个读网表的人拿到错的那一行★), 不是防"网表没毛病"★**。

★**⇒ 3 条判据分别防什么 (★与任务书一一对应★)★★
| 判据 | 防的是 | 门禁里的实现 |
|---|---|---|
| ★**a** 规格页 ⇄ 现行文件 ★ | ★网表被静默改过 (★行号/字段对不上★) ★ | ★逐条锚点 (★**64 条**: d1=17 / d2=19 / d3=14 / d4=14★) 逐字比对 ★ |
| ★**b** BOM 现状断言 ★ | ★`U_EN_SW` 被悄悄"修好"而规格页不跟 ★ | ★`d3_bom208_type` / `d3_bom208_value` ★ |
| ★**c** 不该改错的锚点仍在 ★ | ★有人"顺手把它修好" (★L169 的"已作废"被删 / L182 的 DNP 被翻 / 本体行被偷偷加上★) ★ | ★`d1_a169_note` / `d2_a182_dnp` / `d3_a_body` / `d4_esd_pads` / `d4_esd_on_dminus` 等 ★ |

★**★反向用例 (★`--selftest`★)**: ★**基线必须绿 + 8 个反向用例必须红** ⇒ ★**"把任一锚点改坏 ⇒ 自测必须变红"** ⇒ ★**改坏方式 = 只动临时目录里的副本, 仓库真文件一个字节不碰★**。

### 5.2 ★★翻面条件 (★4 条随整链重出落表后, 门禁怎么从"现状守卫"翻成"缺陷已消失"★)★★

★**★落表那一趟做完之后, 按下面顺序做 (★一步都不能省★)★★

**★第 1 步: 改 `HW/check_netlist_selfconsistency.py` 的 `EXPECT` (把现状断言改成落表后的断言) ★**
- ★(1)★: `d1_a167_value` / `d1_a168_value` 改成落表后的 2.2k/1.8V 口径; `d1_a169_note` 的 `note contains 已作废` 要么删掉、要么改成落表后的 note 原文; `d1_spec_b01_level` / `d1_spec_b01_imp` / `d1_spec_b02_level` / `d1_spec_b02_imp` 改成落表后的值
- ★(2)★: `d2_a182_dnp` / `d2_a183_dnp` / `d2_a184_dnp` / `d2_a185_dnp` / `d2_b307_dnp` / `d2_b309_dnp` / `d2_b100_dnp` 从 `== DNP` 改成 `== 必装`; `d2_a182_value` / `d2_a183_value` 改成新阻值
- ★(3)★: `d3_a_body` / `d3_b_body` 从 `== 0` 改成 `== 1` (★或 ≥1, 取实际值★); `d3_bom208_type` 从 `== NET` 改成 `== IC`; `d3_bom208_value` 改成器件身份描述; `d3_board_value` 改成落表后的 Value
- ★(4)★: `d4_esd_pads` 改成落表后的焊盘数; `d4_esd_value` 改成落表后的 value; `d4_esd_pad1_net` / `d4_esd_pad2_net` 改成落表后的 net; ★**`d4_esd_on_dminus` 从 `== 0` 改成 `>= 1`** ⇒ ★**★这是唯一一条"从 0 变正"的判据 ⇒ 落表后 D− 必须真的有 ESD★** ★

**★第 2 步: 用 `--emit-anchors` 重新生成锚点表, 覆盖回本规格页 §2 的 `ANCHORS:BEGIN/END` 块 ★**
⇒ ★**保证"规格页 ⇄ 脚本"不漂移 (★门禁会自己查这条, 漂移即红★)★**

**★第 3 步: 跑 `--expect-resolved` ⇒ rc=0 才算翻面完成 ★**
⇒ ★**`--expect-resolved` 的判据与 §4 的"落表那趟的验收判据"一一对应 (★R1/R2/R3/R4★) ★**
⇒ ★**★并且: 规格页 §1 各条的 ①②③ 也要同步改成"已落表"的状态 + 新的行号 (★行号会变!★) ⇒ ⇒ 规格页本身也是那一趟的交付物★**

**★第 4 步: `--selftest` 必须仍然全绿 + `--expect-resolved` rc=0 + 现状守卫模式转成"绿" ★**

★**★翻面的判据总表 (★机器可判★)★★
| 判据 | 落表前 (现在) | 落表后 |
|---|---|---|
| 现状守卫 (`无参数`) | ★rc=0 (4 条缺陷仍在) ★ | ★rc=0 (缺陷已消失 + 规格页已同步) ★ |
| 翻面口径 (`--expect-resolved`) | ★rc=1 (未落表) ★ | ★**rc=0** ★ |
| 自检 (`--selftest`) | ★rc=0 (9/9) ★ | ★rc=0 (9/9, 用例要同步改成新的现状) ★ |

★**★为什么现在不做"落表后"的期望值 (★而不是一次写两套★)★**: ★**行号会变** (★网表重出后 L167/L168/L182… 全都会移位★) ⇒ ★**现在写死"落表后的行号"等于编 ⇒ ⇒ 只写"结构性判据"(★有没有本体行 / D− 有没有 ESD / 分压后电压 ≤1.8V / NET 行里还有没有 4.7k★), 行号与逐字原文等那一趟实测出来再填 ★**。

---

## 6. ★★附带发现 (★★不属本单这 4 条, 本单不落表, 只登记待判★★) ★★

**★#1 · 同一个 USB 串阻, 网表里有两个互相打架的阻值 (★[实测]★)★**
★**表A L291** (★net `USB_D_P_SRC`, ref=`NET_USB_D_P_SRC`★) 的 value = `90Ω ±10% (与 MIPI 不同模板!)` ⇒ ★**这是 `R_SER_USB_D_P` 的规格阻抗注记**; ★**但表A L431** (★同一颗 `R_SER_USB_D_P`★) 的 value = `22Ω ±1%` ⇒ ★**同一颗电阻, 两行字差 4 倍**。★**D− 同款: L292 = `90Ω ±10%` vs L432 = `22Ω ±1%`** ⇒ ★**与第 (1) 条同型 (规格 imp vs 器件行)**, ⇒ ★**根因很可能也在 SPEC.json 的 B-22/B-23 (或同源的连接条目) 的 `imp` 字段 ⇒ 建议与第 (1) 条同批查一遍**。★**本单不落表 (★范围外★) ⇒ 已登记 needs。

**★#2 · 项目内部关于 I2C_A 上拉轨有 1.8V / 2.8V 两个口径 (★[实测] + [推算]★)★**
★**`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md:95`** (★2026-11-06 hw-lead 自己的结论★) 写: 「★**I2C_A 走 3.3V 上拉在 SoC 侧不违规** … ⇒ ★**最终 I2C_A 上拉 = 2.8V, 但理由只剩 sensor 侧 abs-max 一条**」; ★**但同一份文件 §:97 自己写着**: 「★**datasheet 没有 GPIO bank → VCCIO 组的对应表** … ★**"I2C0 这两根脚能不能上 3.3V" 仍需 SoM 模组 (FET3572-C) 的 IO 域文档或 BSP dtsi 佐证 ⇒ [0数据]★」。
★**⇒ 两句话并不矛盾: 2.8V 那个结论是【RK3572 芯片侧】的推论, 而【板上真正拿到的 IO 域】是 SoM 模组厂给的 `HW/PCB/FET3572C_PIN_TABLE.csv` (★P2_31 / P2_33 = 1.8V★)。★★所以第 (1) 条的落表目标 = 2.2k/1.8V (与器件行 L169/L170 一致) 是站得住的; ★**但"整机换 AR0234CS (VDD_IO=2.8V) 后上拉轨要一起改" 这条已经在 L169 的 note 里挂着 (TBD-05, 等 onsemi 回信 ISS-142) ⇒ ⇒ 那一版不在本单范围。

**★#3 · 第 (2) 条一旦"装上"就会过压 SoM 的 ADC 脚 (★[推算]★)★**
★**1:1 分压 @BAT 4.2V ⇒ 中点 2.1V > P1_38 的 1.8V 域** ⇒ ★**见 §1 第 (2) 条 ②-3**。★**SoM SAR-ADC 的 abs-max 项目库没有 ⇒ [0数据] ⇒ 必须先关掉才能落表 (★U-2★)**。

**★#4 · 表B 的 `J_SOM_P1.pin38` 行, note 是 `pin100` 那行的复制品 (★[实测]★)★**
★**表B L210** (pin38 / net=`BAT_DET`) 的 note 写「[VBUS_DET] ★SoM 的 USB_DRD1_VBUSDET (P1_100) …」⇒ ★**而表A L186 的 note 是对的 ("[BAT_DET] SoC ADC 输入节点")** ⇒ ★**两张表对同一个脚给的 note 不是一回事** ⇒ 已并入第 (2) 条的 3d。

**★#5 · 第 (4) 条的 ESD 不只是"护了一半", 位置也是错的 (★[实测]★)★**
★**`D_ESD_USB_D.pad1` 挂在 `USB_D_P_SRC` = 22Ω 串阻的【SoM 侧】, 而真正贴连接器的是 `NET_USB_D_P_TYPEC` (串阻的 Type-C 侧); 板面实测距 `J_USB_C` = 47.99 mm** ⇒ ★**L417 note 里那句"紧贴 J_USB_C"被板文件证伪**。⇒ 已并入第 (4) 条的 ②-4 / ③3j。

---

## 7. ★★未决项 (★★需要谁回答什么 —— 本单一律不替老板拍★)★★

| # | 未决 | 需要谁回答 | 卡住什么 | 截止口径 |
|---|---|---|---|---|
| ★**U-1** ★ | ★**USB D− 的 ESD 方案二选一 (① 换 3 脚双通道阵列封装 ② 保留 2 脚件 + 另加一只 `D_ESD_USB_D_N`) + 型号 (★结电容 ≤ 3pF 量级 / 钳位电压 / IEC 61000-4-2 等级★)** ★ | ★**老板 (选型是老板级) ★** | ★**第 (4) 条的落表 (★它要改板 + 重跑布线★)** ★ | ★**第 1 步那一趟之前** ★ |
| ★**U-2** ★ | ★**SoM `SARADC_VIN5` (P1_38) 的 ADC 满量程范围 / 采样源阻抗要求 / abs-max** ★ | ★**Forlinx (SoM 手册) 或 BSP dtsi** ★ | ★**第 (2) 条的 3b 分压比 (★不关掉就会把 1.8V 域 ADC 脚烧掉★)** ★ | ★**第 1 步那一趟之前** ★ |
| ★**U-3** ★ | ★**`U_EN_SW` 的具体型号 (★ISS-172 还是 open★)** ★ | ★**老板 / 采购口径** ★ | ★**第 (3) 条的器件身份描述文案 (★型号可先 [待选型] + 判据串, 不阻塞★)** ★ | ★**不阻塞落表** ★ |
| ★**U-4** ★ | ★**第 (2) 条的漏电流预算**: ★**1M+1M 的分压漏电 ~1.65µA @5V (★L182 note 已写★) vs 改小阻值后 (★100k 量级 ⇒ 漏电 ×10↑) 对整机待机功耗 (★续航 ≥1h 是老板关注点★) 的影响** ★ | ★**本单出数 + 老板拍** ★ | ★**不阻塞 (★但落表那趟要一并算★)** ★ | ★**落表那趟** ★ |

★**★零外发纪律 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)★**: ★**U-1 / U-2 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ ★**没有"批一句可以发"这个选项★**。本单未发任何邮件 / 询价 / 问询 / 采购; ★**U-1 / U-2 的具体参数本单未查 (★型号/绝对最大值属需联网查的项, ★**本单在受限环境内完成且查不到, ⇒ 降级方案 = [待选型] + 判据串, 不猜数字★)**。

---

## 8. ★★证据分级汇总 (★按本项目标签口径★)★★

| 等级 | 条目 |
|---|---|
| ★**[实测]** ★ | ★4 条的全部行号与逐字原文 (表A/表B/BOM) · SPEC.json B-01/B-02 字段 · `FET3572C_PIN_TABLE.csv` P2_31/P2_33/P1_38 · `SOM_PIN_ASSIGNMENT.md:9` · 板文件封装属性/焊盘 net/板面坐标/距离 · `gen_bom.py:143` · `gen_pcb_components.py:156` · `gen_netlist.py:770 / 1471-1483` · `SW_TIMING_REVIEW.md:130` · `INTERFACE_TABLE.md` C-03 电池电压 ★ |
| ★**[官方]** ★ | ★"ESD 紧贴接口"这条规矩 = Forlinx 载板指引 (L417 note 自引) · U_EN_SW 的 F13 功能来源 (Forlinx) ★ |
| ★**[推算]** ★ | ★t_r 186ns / 559ns · 灌流 0.64mA · "4.7k@3.3V = 灌 702µA" 这句本身也是推算 · 1:1 分压中点 2.1V @4.2V · 1.8V 域 ADC 过压判定 (依赖 [0数据] 的 abs-max) ★ |
| ★**[0数据]** ★ | ★SoM SAR-ADC 满量程/源阻抗/abs-max (U-2) · ESD 型号/结电容/钳位/等级 (U-1) · `U_EN_SW` 型号 (U-3) · SoM 的 bank→VCCIO 映射 (RK3572 datasheet 没有该表) ★ |

---

## 9. ★★本单边界 (★交卷时逐条自查过★)★★

★**未碰**: ★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · ★`HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard.kicad_pro` · `HW/SCHEMATIC_V1_SPEC.json` · ★`state/gen_netlist.py` · `state/gen_netlist_pins.py` · `state/gen_bom.py` · `state/check_netlist.py` · `state/check_netlist_pins.py` · `state/gen_pcb_components.py` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · 别人的分片 ★

★**只新增**: ★`HW/NETLIST_SELF_CONSISTENCY_SPEC.md` (本文件) · `HW/check_netlist_selfconsistency.py` · `HANDOFF/2026-11-15_hw-lead_ISS211_网表自身一致性4处.md` · ★`state/fragments/hw.yaml` 一条登记 (★走 `state/frag_write.py` 原子写★)

★**受保护 md5 (★交卷前后逐字节不变★)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`
