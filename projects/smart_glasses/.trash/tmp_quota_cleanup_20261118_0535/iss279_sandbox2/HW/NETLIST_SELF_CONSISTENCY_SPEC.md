# ★★网表自身一致性 · 第 1 轮 4 处 + 第 2 轮 7 组 "自己跟自己打架"的落表规格 (★ISS-211 + ISS-214★)★★

> ★**性质**: ★**这是【规格页】, 不是执行记录** ⇒ ★**本文件落笔时, 网表 / 板 / 脚表 / BOM / SPEC.json / 生成器 一个字节都没改** ⇒ ★**凡是"要改成什么"的字样, 都只是"要改成什么", 不是"已经改好"**
> ★**日期**: 2026-11-15 (★第 1 轮 · ISS-211★) · ★**2026-11-16 扩写 (★第 2 轮 · ISS-214★)** · ★**执行**: 硬件总工 (hw-lead) · ★**单号**: ISS-211 + ISS-214 · ★**owner**: hw-lead · ★**verify_by**: main
> ★**门禁**: ★**`HW/check_netlist_selfconsistency.py`** (rc=0 / `--selftest` / `--expect-resolved`)
> ★**受保护 md5 (★交卷前后逐字节不变★)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`
> ★**★★受保护 md5 · 现行值 (★2026-11-16 07:3x 二次独立复核 · 本机 md5sum 实测★)★★★**: 板 `611b869e13518c3c023fb178f91a0075` (★不变★) · 网表 `34132f7e40a241e1fae1476be0eafbd5` · 脚表 `b21b743a7702d30729f0d653c15392df` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` (★不变★)
> ★**★为什么网表/脚表的基线变了 (★不是本单改的, 是 main 授权的落表★)★★**: 上一行的 `c78f9912…` / `4814617e…` 是 ★**2026-11-16 01:04 (ISS-214 交卷) 时的值**★ ⇒ ★**2026-11-16 06:48 (ISS-233 第 3 批落表) 合法改了这两张表**★ (★网表 L442 + 脚表 L531 + BOM L208 三行补 `U_EN_SW` 器件本体行 ⇒ `--expect-resolved` 21 → 18★) ⇒ ★**⇒ 审计基线以本行的"现行值"为准; 板与 `.kicad_pro` 逐字节未变 (板只改一次那一趟还没走)★** ⇒ ★**★这一条是【基线台账跟着合法落表走】, 不是【有人偷改了受保护文件】★★**
> ★**★★第 2 轮 (ISS-214) 的扩写说明 (★2026-11-16·hw-lead★)★★**
> ★**本文件是【扩写】, 不是另起炉灶**: ★**第 1 轮的 §1 四条 (d1..d4, 64 条锚点) 一条不许删**; ★**第 2 轮的 7 组新锚点 (d5..d11, 90 条) 加在 §2 的同一张锚点表里** ⇒ ★**"规格页 ⇄ 脚本 ⇄ 现行文件"三方对齐仍然只有一套** ⇒ ★**第 2 轮的 8 条明细见 §10 (每条 8 栏齐), 附带发现见 §11, 未决项见 §13, 边界自查见 §14** ★

---

## 0. ★一句话 + 边界★★

★**现行网表里有 4 处"同一张表里两行字直接互相否定"的地方**: ① I2C_A 上拉的 **NET 行说 4.7k/3.3V、器件行说 2.2k/1.8V** · ② **BAT_DET 整条分压链全 DNP, 而 SoC 的 ADC 输入脚是必装** (⇒ 悬空输入) · ③ **U_EN_SW 没有器件本体行** ⇒ BOM 里这颗 4 脚 IC 被登记成 NET 行 (value 栏躺着一句脚功能串) · ④ **USB D− 全程没有 ESD, 而那颗器件自称"双通道"**。

★**为什么现在不能改**: ★**整链重出 第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md`) 要把 C/E/D 三项一次合并落表 ⇒ 板只改一次** ⇒ ★**先落表 = 留证链/Gerber/投产包/盖印 白跑两遍** ⇒ ★**所以本单 = 出规格 + 出门禁, 让这 4 条跟着那一趟一起落** (★这套路子在 ISS-191 / ISS-174 已验证过★)。

★**本单不许做的事 (★边界★)**: ★**不改网表 / 不改脚表 / 不改板 / 不改 SPEC.json / 不改任何生成器 / 不改 issue_log / 不改 PROJECT_TRACKER §0 / 不碰别人的分片 / 零外发 (不发邮件·询价·问询·采购)★**。

★**★★第 2 轮 (ISS-214) 追加的边界 (★2026-11-16·hw-lead★)★★**: ★**同上, 再加两条** ★
★**① 本轮【只出规格 + 扩门禁】, 一样一个字节都不改 (网表 / 脚表 / BOM / 板 / SPEC.json / CHARGE_BOARD_SPEC.md / EMC_PRECHECK.md / 任何生成器) ★**
★**② 本轮要读的 5 个"根因层"文件 (`state/gen_schematic_pages.py` / `HW/CHARGE_BOARD_SPEC.md` / `HW/EMC_PRECHECK.md` / `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` / `HW/PCB/FET3572C_PIN_TABLE.csv`) 也一个字都没改 —— ★**它们是门禁的"对照对象", 不是施工面**** ★

---

## 1. ★★四条缺陷 · 逐条 6 栏 (★① 现象 ② 为什么是缺陷 ③ 修法 ④ 影响面 ⑤ 落表时机 ⑥ 证据等级★)★★

---

### ★★第 (1) 条 ★★ I2C_A 上拉: ★★网线行说 4.7k/3.3V, 器件行说 2.2k/1.8V★★

#### ① 现象 (★网表原文逐字 + 行号★)

★**表A `HW/netlist_v1.csv`** (★表头 = 第 1 行, 下面行号是物理行号★):

| 行 | 原文 (逐字) |
|---|---|
| ★**L167** | `P2,I2C_A_SCL,J_SOM_P2 pin31,R_PU_I2CA_SCL,NET_I2C_A_SCL,上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF),NET,必装,[推算],,方向 双向 (主机); 电平 1.8V; 阻抗 上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF); 连接 SoC [待原厂] + sensor/NTC/桥接/充电IC; 测试点 TP_I2CA_SCL,B-01,MAIN_PCB,,` |
| ★**L168** | `P2,I2C_A_SDA,J_SOM_P2 pin33,R_PU_I2CA_SDA,NET_I2C_A_SDA,上拉 2.2k 到 1.8V,NET,必装,[推算],,方向 双向 (主机); 电平 1.8V; 阻抗 上拉 2.2k 到 1.8V; 连接 同上; 测试点 TP_I2CA_SDA,B-02,MAIN_PCB,,` |
| ★**L169** | `P2,VDD_1V8_IO,R_PU_I2CA_SCL,RAIL_VDD_1V8_IO,R_PU_I2CA_SCL,2.2k ±1%,R,必装,[推算],,"[VDD_1V8_IO] I2C_A 上拉 (★★11-04 ISS-153 订正: **实际 net = RAIL_VDD_1V8_IO (1.8V 域)**; ★**旧注释写的『[VDD_3V3_IO] / 3.3V 上拉』与网表相反, 已作废**; 依据 ①: RK3572 的 I2C5 = J_SOM_P2 pin31/pin33 属**1.8V 域** (HW/PCB/FET3572C_PIN_TABLE.csv P2_31/P2_33 电压域列 = 1.8V) ⇒ 3.3V 上拉会把 SoM 的 1.8V 脚灌 3.3V = 过压; …) ",B-01,MAIN_PCB,,` (★note 很长, 此处截断; 完整原文见文件★) |
| ★**L170** | `P2,VDD_1V8_IO,R_PU_I2CA_SDA,RAIL_VDD_1V8_IO,R_PU_I2CA_SDA,2.2k ±1%,R,必装,[推算],,"[VDD_1V8_IO] I2C_A 上拉 (★同 SCL: 实际 net = RAIL_VDD_1V8_IO, **1.8V 域** …)",B-02,MAIN_PCB,,` |
| ★**L171** | `P2,I2C_A_SCL,CONN_CAM pin24,NET_I2C_A_SCL,NET_I2C_A_SCL,"上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, ★camera FPC 标 I2C5 = 1.8V 域)",NET,必装,…,B-01,MAIN_PCB,,` ★**← 自洽对照行: camera 侧已经写对了** |

★**表B `HW/netlist_v1_pins.csv`**: ★**L367** `R_PU_I2CA_SCL.1` net=`I2C_A_SCL` · ★**L368** `R_PU_I2CA_SCL.2` net=`VDD_1V8_IO` · ★**L369/L370** 同款 (SDA) ⇒ ★**脚表是对的**。

★**根源在规格源头 `HW/SCHEMATIC_V1_SPEC.json`** (★`connections` 数组★):
```json
{ "id": "B-01", "signal": "I2C_A_SCL", "level": "1.8V",
  "imp": "上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)", … }
{ "id": "B-02", "signal": "I2C_A_SDA", "level": "1.8V",
  "imp": "上拉 2.2k 到 1.8V", … }
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
| ★**L442** ★ | ★**★2026-11-16 ISS-233 落表后 = 器件本体行★** | ★`P1,RAIL_DEMO_5V,U_EN_SW pin1,RAIL_DEMO_5V,U_EN_SW,"TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)",IC,必装,[官方],,"[U_EN_SW] ★★器件本体行 (type=IC · 挂在 pin1/VIN 上 · 同族正确写法 = U_PWR_SW 本体行挂 pin3/VOUT)★★ ★pin1 脚级功能: IN = 5V 输入 (Type-C 直供 5V)★ | pin2 = EN 输入 (高=放行底板) | pin3 = 5V 输出 (受 CARRIER_BOARD_EN 门控) | pin4 = GND | ★★F13 落法: 底板所有 3.3V/5V 支路都挂 RAIL_BOARD_5V (不是 SYS) ⇒ 主板各路只在 SoM 就绪后上电 ⇒ 防底板早于核心板上电损坏处理器★★ | ★选型 = TPS22991RAA (项目总工 11-03 已裁, ISS-172 待老板点头; 同 UQFN-4 封装 ⇒ 若改 TPS22916/17 = 换料不换板)★",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` ★ |
| ★**L443** | `P1,RAIL_BOARD_5V,U_EN_SW pin3,RAIL_BOARD_5V,U_EN_SW,5V 输出 (受 CARRIER_BOARD_EN 门控),NET,必装,[官方],,"[RAIL_BOARD_5V] ★**底板所有 3.3V/5V 支路都挂这条** (不是 SYS) ⇒ 这就是 F13 的落法",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` |
| ★**L444** | `P1,GND,U_EN_SW pin4,GND,U_EN_SW,GND,NET,必装,[官方],,"[U_EN_SW] 地",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` |

★**表B `HW/netlist_v1_pins.csv`**: ★**L531/L532/L533/L534** = `U_EN_SW.pin1..pin4` ⇒ ★**★2026-11-16 ISS-233 落表后: L531 (pin1) 的 `type` = `IC` + value = 器件身份描述 (★它跟着表A L442 的本体行走★); L532/L533/L534 仍是 `NET` 脚级功能串 (★这就是"本体行挂在其中一脚上, 其余脚是 NET 行"的正确写法★)** ⇒ ★**表A / 表B / BOM 三处都已有本体行 (★BOM L208 的 type = IC·value = 器件身份描述·procurement = 已定型-IC★)**。

★**★对照: 同一块板上同类器件 `U_PWR_SW` 有本体行★** ⇒ ★**表A L50**: `P1,SYS,U_PWR_SW pin3,RAIL_SYS,U_PWR_SW,"[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)",IC,必装,[推算],…` ⇒ ★**表B 里 `U_PWR_SW.pin3` 的 `type` 也是 `IC`, value 同样是器件身份描述 ⇒ 这就是"器件本体行"的正确写法 (★本体行挂在其中一脚上, 其余脚是 NET 行★)**。

★**后果已经在 BOM 上显形** ⇒ ★**`HW/BOM_v1.csv` L208 (★落表前★)**: `U_EN_SW,1,EN 输入 (高=放行底板),NET,必装,镜脚主 PCB,P1,[官方],,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA,待定,待定,待分类,` ⇒ ★**一颗 4 脚 IC 的 value 栏里躺着一句脚功能串, type 栏是 NET** ⇒ ★**★落表后 (★2026-11-16 ISS-233★)**: `U_EN_SW,1,"TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)",IC,必装,镜脚主 PCB,P1,[官方],,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA,待定,待定,已定型-IC,型号已定 (官网/官方数据手册), 封装与替代料待采购确认` ⇒ ★**★value = 器件身份描述 · type = IC · procurement 从「待分类」变「已定型-IC」⇒ 这颗负载开关不再是一颗【伪物料】, 备料台账能认出它是料★**。

★**★连板文件也被传染了 (★main 没提到这一层, 是本单新挖的★)★** ⇒ ★**板文件 `HW/PCB/demo_mainboard.kicad_pcb` 里 `U_EN_SW` 封装 (★4 焊盘★) 的 `Value` 属性 = "EN 输入 (高=放行底板)"** ⇒ ★**根因在 `state/gen_pcb_components.py:156`: `fp.SetValue(per_ref[ref][0][2][:40] …)` ⇒ 板封装 Value = 该 ref 在网表里**第一行**的 value ⇒ 网表缺本体行 ⇒ 第一行是 NET 行 ⇒ 脚功能串被写进板文件 ⇒ ⇒ ★**BOM 的"板文件 Value 兜底"也就跟着取了这句话**。

★**★2026-11-16 ISS-233 落表后的【板侧残留项】 (★归「板只改一次」那一趟, 本单不许碰板★)★**: ★**板文件里 `U_EN_SW` 封装的 `Value` 属性仍是 "EN 输入 (高=放行底板)" (★受保护 md5 `611b869e…` 逐字节不变★) ⇒ ⇒ ★**R3 的第 4 条 (板侧) 仍然红, `--expect-resolved` 因此是 18 条而不是 15 条★** ⇒ ★**★且板那一趟不能指望生成器自动改: `gen_pcb_components.py` 对【已在板上的封装】走 `if ref in have: … continue` 分支 ⇒ 不会重写 Value ⇒ ★**必须手工把板封装 Value 改成器件身份描述 (★板侧同步清单 B-2★)★** ⇒ ★**同理, 原理图侧 `HW/PCB/demo_mainboard_p1.kicad_sch` 里 `U_EN_SW` 符号的 `Value` 属性已随本次落表变成器件身份描述 (★因为本体行挂在 pin1 = 脚表第一行★), 而 `MPN` 属性一直是 TPS22991RAA★**。

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
| ★**L417** | `P1,USB_D_P_SRC,D_ESD_USB_D,USB_D_P_SRC,D_ESD_USB_D,TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V),D,必装,[官方],,"[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**",A-24,MAIN_PCB,,TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)` |
| ★**L418** | `P1,GND,D_ESD_USB_D,GND,D_ESD_USB_D,TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V),D,必装,[官方],,"[D_ESD_USB_D] ESD 地端",A-24,MAIN_PCB,,TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)` |
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

## 2. ★★8 条 (第 1 轮 4 + 第 2 轮 7 组) 的机读汇总 (★门禁锚点表 = 唯一真源在 `HW/check_netlist_selfconsistency.py` 的 `EXPECT`★) ★★

> ★**★★锚点表共 160 条: 第 1 轮 64 条 (d1=17 / d2=19 / d3=14 / d4=14) + 第 2 轮 96 条 (d5=16 / d6=17 / d7=17 / d8=8 / d9=7 / d10=18 / d11=13)★★** ⇒ ★**第 2 轮的明细见 §10, ★**每条新锚点组在 `--selftest` 里都有 ≥1 个反向用例 (原 9 + 新 7 = 16/16)★** ★

| 条 | 机器可判的核心判据 | 现在应为 |
|---|---|---|
| ★(1) ★ | 表A L167/L168 的 value 仍含 "4.7k 到 3.3V" + L169/L170 是 2.2k/VDD_1V8_IO + L169 note 仍含 "已作废" + SPEC.json B-01/B-02 的 `level` 仍 = 3.3V | ★**成立 (缺陷在)** ★ |
| ★(2) ★ | 表A L182/L183/L184/L185 与表B L100/L307/L309 的 `dnp` 仍 = DNP, 而 L181/L186/L210 是必装 | ★**成立 (缺陷在)** ★ |
| ★(3) ★ | 表A/表B 里 `ref==U_EN_SW` 的行数 = 4 且 `type!=NET` 的行数 = **0**; BOM L208 的 type = NET; 板封装 `U_EN_SW` 的 Value = 脚功能串 | ★**★落表后 (★2026-11-16 ISS-233★): 网表侧已修 (表A/表B 各 1 条 `type==IC` 的本体行 + BOM L208 type=IC/value=器件身份描述) ⇒ ★**只剩板封装 Value 一条仍红 (★归「板只改一次」那一趟★)** ★** |
| ★(4) ★ | 板封装 `D_ESD_USB_D` 焊盘数 = 2 + Value 自称双通道 + 挂 D− 两张网的 ESD 位号数 = 0 | ★**成立 (缺陷在)** ★ |

★**锚点表 (★机读; 门禁脚本会逐条比对这张表, 漂移即红★)★**

<!-- ANCHORS:BEGIN -->
| key | file | line | check |
|---|---|---|---|
| d1_a167_value | netlist | 167 | value == 上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF) |
| d1_a167_ref | netlist | 167 | ref == NET_I2C_A_SCL |
| d1_a168_value | netlist | 168 | value == 上拉 2.2k 到 1.8V |
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
| d1_spec_b01_level | spec | ? | spec.connections[id=B-01].level == 1.8V |
| d1_spec_b01_imp | spec | ? | spec.connections[id=B-01].imp == 上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF) |
| d1_spec_b02_level | spec | ? | spec.connections[id=B-02].level == 1.8V |
| d1_spec_b02_imp | spec | ? | spec.connections[id=B-02].imp == 上拉 2.2k 到 1.8V |
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
| d3_a442_type | netlist | 442 | type == IC |
| d3_a443_type | netlist | 443 | type == NET |
| d3_a444_type | netlist | 444 | type == NET |
| d3_a_rows | netlist | ? | count(ref==U_EN_SW) == 4 |
| d3_a_body | netlist | ? | count(ref==U_EN_SW&type!=NET) == 1 |
| d3_b_rows | pins | ? | count(ref==U_EN_SW) == 4 |
| d3_b_body | pins | ? | count(ref==U_EN_SW&type!=NET) == 1 |
| d3_bom208_type | bom | 208 | type == IC |
| d3_bom208_value | bom | 208 | value == TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm) |
| d3_board_value | board | ? | footprint.U_EN_SW.value == EN 输入 (高=放行底板) |
| d3_board_pads | board | ? | footprint.U_EN_SW.pads == 4 |
| d3_ctrl_a50_type | netlist | 50 | type == IC |
| d4_a417_value | netlist | 417 | value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V) |
| d4_a417_net | netlist | 417 | net == USB_D_P_SRC |
| d4_a417_dnp | netlist | 417 | dnp == 必装 |
| d4_a417_note | netlist | 417 | note contains Forlinx 载板指引要求 ESD 紧贴接口 |
| d4_a418_value | netlist | 418 | value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V) |
| d4_a432_net | netlist | 432 | net == NET_USB_D_N_TYPEC |
| d4_a432_ref | netlist | 432 | ref == R_SER_USB_D_N |
| d4_esd_pads | board | ? | footprint.D_ESD_USB_D.pads == 2 |
| d4_esd_value | board | ? | footprint.D_ESD_USB_D.value == ESD 阵列 [待选型] (USB 2.0 双通道) |
| d4_esd_pad1_net | board | ? | footprint.D_ESD_USB_D.pad1.net == USB_D_P_SRC |
| d4_esd_pad2_net | board | ? | footprint.D_ESD_USB_D.pad2.net == GND |
| d4_esd_on_dminus | board | ? | esd_on_net(USB_D_N_SRC,NET_USB_D_N_TYPEC) == 0 |
| d4_bom62_value | bom | 62 | value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V) |
| d4_bom62_fp | bom | 62 | footprint contains 2 焊盘 |
| d5_a291_value | netlist | 291 | value == 22Ω ±1% |
| d5_a291_ref | netlist | 291 | ref == NET_USB_D_P_SRC |
| d5_a292_value | netlist | 292 | value == 22Ω ±1% |
| d5_a292_ref | netlist | 292 | ref == NET_USB_D_N_SRC |
| d5_a431_value | netlist | 431 | value == 22Ω ±1% |
| d5_a431_ref | netlist | 431 | ref == R_SER_USB_D_P |
| d5_a432_value | netlist | 432 | value == 22Ω ±1% |
| d5_a432_ref | netlist | 432 | ref == R_SER_USB_D_N |
| d5_a291_rows | netlist | ? | count(ref==NET_USB_D_P_SRC) == 1 |
| d5_a292_rows | netlist | ? | count(ref==NET_USB_D_N_SRC) == 1 |
| d5_spec_b21_imp | spec | ? | spec.connections[id=B-21].imp == 22Ω ±1% |
| d5_spec_b21_signal | spec | ? | spec.connections[id=B-21].signal == USB_D+ |
| d5_spec_b22_imp | spec | ? | spec.connections[id=B-22].imp == 22Ω ±1% |
| d5_spec_b22_signal | spec | ? | spec.connections[id=B-22].signal == USB_D- |
| d5_emc_90_480 | emc | ? | text contains D+/D- 90 Ω 差分, 480 Mbps |
| d5_emc_template | emc | ? | text contains 不是同一套阻抗模板 |
| d6_pages_light_21p | pages | ? | text notcontains `CONN_LIGHT` (**1×21p@0.5mm**) |
| d6_pages_light_22p | pages | ? | text contains 1×22p@0.5mm |
| d6_pages_cam_18p | pages | ? | text notcontains `CONN_CAM` (**18p@0.5mm**) |
| d6_pages_cam_31p | pages | ? | text contains `CONN_CAM` (**31p@0.3mm |
| d6_pages_usb_4p | pages | ? | text notcontains `CONN_USB` (**4p@0.5mm**) |
| d6_pages_stack_265 | pages | ? | text notcontains (10+4+18+21)×0.5 = **26.5mm** |
| d6_pages_stack_370 | pages | ? | text notcontains 镜脚根部净高 **37.0mm** |
| d6_pages_stack_380 | pages | ? | text contains 镜脚根部净高 **38.00mm** |
| d6_a237_value | netlist | 237 | value == ★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱; 官方封装抄 RPi CM5IO) |
| d6_a237_board | netlist | 237 | board == MAIN_PCB |
| d6_a290_value | netlist | 290 | value == ★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 HIROSE FH35C-31S-0.3SHW(50); 针位见 HW/PCB/FPC_PIN_TABLES.md) |
| d6_a290_board | netlist | 290 | board == MAIN_PCB |
| d6_b_light_pins | pins | ? | count(ref==CONN_LIGHT) == 22 |
| d6_b_cam_pins | pins | ? | count(ref==CONN_CAM) == 31 |
| d6_net_no_conusb | netlist | ? | count(ref==CONN_USB) == 0 |
| d6_bom5_value | bom | 5 | value contains 22p@0.5mm |
| d6_bom5_fp | bom | 5 | footprint contains FH12-22S-0.5SH |
| d7_a181_value | netlist | 181 | value == 1M+1M 分压 + 100nF |
| d7_a182_value | netlist | 182 | value == 1M ±1% |
| d7_a183_value | netlist | 183 | value == 1M ±1% |
| d7_a184_value | netlist | 184 | value == 100nF ±10% |
| d7_a186_node1 | netlist | 186 | node1 == J_SOM_P1 pin38 |
| d7_a186_dnp | netlist | 186 | dnp == 必装 |
| d7_rk_table | rk | ? | text contains Table 3-16 Electrical Characteristics for SARADC |
| d7_rk_resolution | rk | ? | text contains Resolution                                                                 NA           12         NA       Bit |
| d7_rk_ain | rk | ? | text contains Anglog Input Range             AIN                                        AVSS18       NA         AVDD18    V |
| d7_som_p138_signal | sompins | 39 | signal == SARADC_VIN5 |
| d7_som_p138_vol | sompins | 39 | vol == 1.8V |
| d7_som_p138_num | sompins | 39 | num == 38 |
| d7_node_v | netlist | ? | calc(node_v@4.2) == 2.1 |
| d7_node_over | netlist | ? | calc(node_v@4.2) > 1.8 |
| d8_a182_note | netlist | 182 | note contains 漏电流 ~1.65µA @5V |
| d8_bom86_value | bom | 86 | value == 1M ±1% |
| d8_bom86_dnp | bom | 86 | dnp == DNP |
| d8_bom87_value | bom | 87 | value == 1M ±1% |
| d8_bom87_dnp | bom | 87 | dnp == DNP |
| d8_bom27_value | bom | 27 | value == 100nF ±10% |
| d8_leak_now | netlist | ? | calc(leak_ua@4.2) == 2.1 |
| d8_leak_claim | netlist | ? | calc(leak_note_ua@5) == 1.65 |
| d9_pages_esd_3mm | pages | ? | text contains ESD 距连接器 ≤3.0mm |
| d9_pages_two_ends | pages | ? | text contains 两端 ESD |
| d9_emc_480 | emc | ? | text contains 480 Mbps |
| d9_esd_dist | netlist | ? | calc(esd_dist_usb) > 5 |
| d9_esd_pads2 | board | ? | footprint.D_ESD_USB_D.pads == 2 |
| d9_esd_dual_claim | netlist | 417 | value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V) |
| d9_esd_on_dminus | board | ? | esd_on_net(USB_D_N_SRC,NET_USB_D_N_TYPEC) == 0 |
| d10_spec_0822 | chgspec | ? | text notcontains CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822) |
| d10_spec_ratio_1216 | chgspec | ? | text contains ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V** |
| d10_spec_formula | chgspec | ? | text notcontains ICHG ≈ IIN × (VBAT / VBUS) / η |
| d10_spec_0822_val | chgspec | ? | text notcontains ICHG ≈ 0.822 × IIN |
| d10_spec_script | chgspec | ? | text notcontains lo*0.822 |
| d10_spec_script_1216 | chgspec | ? | text contains lo*1.216 |
| d10_spec_0411 | chgspec | ? | text notcontains 单 pin 0.411A ≤ 0.5A 触点天花板 |
| d10_spec_0608 | chgspec | ? | text contains 单 pin **0.608A** |
| d10_a47_value | netlist | 47 | value == 390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决) |
| d10_a48_value | netlist | 48 | value == 390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决) |
| d10_bom97_value | bom | 97 | value == 390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决) |
| d10_a497_note | netlist | 497 | note contains 工作上限 0.50A |
| d10_ratio_370 | netlist | ? | calc(ichg_ratio@3.7) == 1.216 |
| d10_ratio_420 | netlist | ? | calc(ichg_ratio@4.2) == 1.071 |
| d10_pin_max_370 | netlist | ? | calc(ichg_pin_max@3.7) == 0.608 |
| d10_pin_max_420 | netlist | ? | calc(ichg_pin_max@4.2) == 0.536 |
| d11_a11_ref | netlist | 11 | ref == C_VBUS_OUT |
| d11_a11_board | netlist | 11 | board == CHG_BOARD |
| d11_a12_ref | netlist | 12 | ref == C_VBUS_GND |
| d11_a12_board | netlist | 12 | board == CHG_BOARD |
| d11_a13_ref | netlist | 13 | ref == U_CHG |
| d11_a13_board | netlist | 13 | board == CHG_BOARD |
| d11_a10_ref | netlist | 10 | ref == C_VBUS_GND |
| d11_a10_board | netlist | 10 | board == CHG_BOARD |
| d11_b148_board | pins | 148 | board == CHG_BOARD |
| d11_b149_board | pins | 149 | board == CHG_BOARD |
| d11_b154_board | pins | 154 | board == CHG_BOARD |
| d11_b155_board | pins | 155 | board == CHG_BOARD |
| d11_led508_board | netlist | 508 | board == CHG_BOARD |
| d11_led509_board | netlist | 509 | board == CHG_BOARD |
| d11_led_refs | netlist | ? | count(ref==R_CHG_LED) == 2 |
| d11_board_cvbgnd_pads | board | ? | footprint.C_VBUS_GND.pads == 2 |
| d11_board_cvbgnd_pad2 | board | ? | footprint.C_VBUS_GND.pad2.net == VBUS_5V_CHG |
| d11_board_no_cvbout | board | ? | count_footprint(C_VBUS_OUT) == 0 |
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
| ★**a** 规格页 ⇄ 现行文件 ★ | ★网表被静默改过 (★行号/字段对不上★) ★ | ★逐条锚点 (★**160 条**: 第 1 轮 64 (d1=17 / d2=19 / d3=14 / d4=14) + 第 2 轮 96 (d5=16 / d6=17 / d7=17 / d8=8 / d9=7 / d10=18 / d11=13) ★(★2026-11-16 ISS-220 第 1 批落表后新增 6 条正向锚点: d6_pages_light_22p / d6_pages_cam_31p / d6_pages_stack_380 / d10_spec_ratio_1216 / d10_spec_script_1216 / d10_spec_0608; ★一条未减★)★) 逐字比对 ★ |
| ★**b** BOM 现状断言 ★ | ★`U_EN_SW` 被悄悄"修好"而规格页不跟 ★ | ★`d3_bom208_type` / `d3_bom208_value` ★ |
| ★**c** 不该改错的锚点仍在 ★ | ★有人"顺手把它修好" (★L169 的"已作废"被删 / L182 的 DNP 被翻 / 本体行被偷偷加上★) ★ | ★`d1_a169_note` / `d2_a182_dnp` / `d3_a_body` / `d4_esd_pads` / `d4_esd_on_dminus` 等 ★ |
| ★**d (★第 2 轮新增★)** ★根因层文件 ⇄ 现行文件★ ★ | ★**规格源头 (SPEC.json / P9 页生成器 / CHARGE_BOARD_SPEC / EMC_PRECHECK) 被静默改过** ★ | ★`d5_spec_b21_imp` / `d6_pages_*` / `d10_spec_*` / `d9_emc_480` / `d7_rk_*` (★官方 datasheet 抽取文本★) ★ |
| ★**e (★第 2 轮新增★)** ★物理量自洽 (calc)★ ★ | ★**网表里的数与物理真值对不上** (★分压比 / 漏电 / ICHG 系数 / ESD 距离★) ★ | ★`calc(node_v@4.2)` / `calc(leak_ua@4.2)` vs `calc(leak_note_ua@5)` / `calc(ichg_ratio@3.7)` / `calc(ichg_pin_max@3.7)` / `calc(esd_dist_usb)` ★ |

★**★反向用例 (★`--selftest`★)**: ★**基线必须绿 + **16 个**反向用例必须红 (★原 9 个一条不许删 + 第 2 轮新增 7 个★) ⇒ ★**"把任一锚点改坏 ⇒ 自测必须变红"** ⇒ ★**改坏方式 = 只动临时目录里的副本, 仓库真文件一个字节不碰★**。

### 5.2 ★★翻面条件 (★4 条随整链重出落表后, 门禁怎么从"现状守卫"翻成"缺陷已消失"★)★★

★**★落表那一趟做完之后, 按下面顺序做 (★一步都不能省★)★★

**★第 1 步: 改 `HW/check_netlist_selfconsistency.py` 的 `EXPECT` (把现状断言改成落表后的断言) ★**
- ★(1)★: `d1_a167_value` / `d1_a168_value` 改成落表后的 2.2k/1.8V 口径; `d1_a169_note` 的 `note contains 已作废` 要么删掉、要么改成落表后的 note 原文; `d1_spec_b01_level` / `d1_spec_b01_imp` / `d1_spec_b02_level` / `d1_spec_b02_imp` 改成落表后的值
- ★(2)★: `d2_a182_dnp` / `d2_a183_dnp` / `d2_a184_dnp` / `d2_a185_dnp` / `d2_b307_dnp` / `d2_b309_dnp` / `d2_b100_dnp` 从 `== DNP` 改成 `== 必装`; `d2_a182_value` / `d2_a183_value` 改成新阻值
- ★(3)★: `d3_a_body` / `d3_b_body` 从 `== 0` 改成 `== 1` (★或 ≥1, 取实际值★); `d3_bom208_type` 从 `== NET` 改成 `== IC`; `d3_bom208_value` 改成器件身份描述; `d3_board_value` 改成落表后的 Value
- ★(4)★: `d4_esd_pads` 改成落表后的焊盘数; `d4_esd_value` 改成落表后的 value; `d4_esd_pad1_net` / `d4_esd_pad2_net` 改成落表后的 net; ★**`d4_esd_on_dminus` 从 `== 0` 改成 `>= 1`** ⇒ ★**★这是唯一一条"从 0 变正"的判据 ⇒ 落表后 D− 必须真的有 ESD★** ★

**★第 1b 步 (★ISS-214 第 2 轮追加★): 改第 2 轮 90 条锚点 (d5..d11) 的"现状断言" ★**
- ★(1)·d5★: `d5_a291_value` / `d5_a292_value` 改成落表后的 22Ω 口径; `d5_spec_b21_imp` / `d5_spec_b22_imp` 改成落表后的 imp
- ★(2)·d6★: `d6_pages_light_21p` / `d6_pages_cam_18p` / `d6_pages_usb_4p` / `d6_pages_stack_265` / `d6_pages_stack_370` 全部改成落表后的页面文字 (★P9 页是生成器里的手写字符串 ⇒ 改的是生成器, 不许手改 svg★)
- ★(3)(4)·d7/d8★: `d7_a182_value` / `d7_a183_value` 改成新阻值; `d7_node_v` / `d7_node_over` / `d8_leak_now` / `d8_leak_claim` 的期望值改成新值 (★门禁自己算, 不写死★)
- ★(5)·d9★: `d9_esd_pads2` 改成 3; `d9_esd_dual_claim` 改成落表后的 value; `d9_esd_on_dminus` 改成 ≥1; `d9_esd_dist` 的门槛 ★**从 5mm 收紧到 3.0mm (★口径升级, 见 §11 附带发现 #3 / §13 V-6★)**** ★
- ★(7)·d10★: `d10_spec_0822` / `d10_spec_formula` / `d10_spec_0822_val` / `d10_spec_script` / `d10_spec_0411` 全部改成落表后的原文; `d10_a47_value` / `d10_a48_value` / `d10_bom97_value` 改成落表后的档位串
- ★(8)·d11★: `d11_a10_board` / `d11_a12_board` / `d11_b148_board` / `d11_b149_board` 改成 `CHG_BOARD`; `d11_board_cvbgnd_pads` 改成 0 (★封装上了充电板 ⇒ demo 主 PCB 上就没有了★)

**★第 2 步: 用 `--emit-anchors` 重新生成锚点表, 覆盖回本规格页 §2 的 `ANCHORS:BEGIN/END` 块 ★**
⇒ ★**保证"规格页 ⇄ 脚本"不漂移 (★门禁会自己查这条, 漂移即红★)★**

**★第 3 步: 跑 `--expect-resolved` ⇒ rc=0 才算翻面完成 ★**
⇒ ★**`--expect-resolved` 的判据与 §4 的"落表那趟的验收判据"一一对应 (★R1/R2/R3/R4★) ★**
⇒ ★**★第 2 轮已把 R5~R11 实装进 `--expect-resolved` (★ISS-214★)** ⇒ ★**第 2 轮的落表验收判据 = R5(USB 串阻 22Ω) / R6(P9 页 22p) / R7(分压比在 1.2~1.8V 之间) / R8(漏电 note 与阻值自洽) / R9(ESD 距 J_USB_C) / R10(ICHG/IIN 方向 + 单 pin ≤0.5A) / R11(board 列一致) ★** ⇒ ★**⇒ ★**第 2 轮不需要再补写一遍期望值, 门禁已经按"物理真值"写好了, 落表那趟只要把现状改对, R5~R11 会自己转绿** ★**
⇒ ★**★并且: 规格页 §1 各条的 ①②③ 也要同步改成"已落表"的状态 + 新的行号 (★行号会变!★) ⇒ ⇒ 规格页本身也是那一趟的交付物★**

**★第 4 步: `--selftest` 必须仍然全绿 + `--expect-resolved` rc=0 + 现状守卫模式转成"绿" ★**

★**★翻面的判据总表 (★机器可判★)★★
| 判据 | 落表前 (现在) | 落表后 |
|---|---|---|
| 现状守卫 (`无参数`) | ★rc=0 (★8 条缺陷仍在★) ★ | ★rc=0 (缺陷已消失 + 规格页已同步) ★ |
| 翻面口径 (`--expect-resolved`) | ★rc=1 (未落表) ★ | ★**rc=0** ★ |
| 自检 (`--selftest`) | ★rc=0 (★16/16★) ★ | ★rc=0 (★16/16, 用例要同步改成新的现状★) ★ |

★**★为什么现在不做"落表后"的期望值 (★而不是一次写两套★)★**: ★**行号会变** (★网表重出后 L167/L168/L182… 全都会移位★) ⇒ ★**现在写死"落表后的行号"等于编 ⇒ ⇒ 只写"结构性判据"(★有没有本体行 / D− 有没有 ESD / 分压后电压 ≤1.8V / NET 行里还有没有 4.7k★), 行号与逐字原文等那一趟实测出来再填 ★**。

### ★5.3 ★★落表状态 (★ISS-220 第 1 批 · 2026-11-16 · 硬件总工执行★)★★

★★**一句话**: ★**本页的 12 组 (d1..d11 + #1..#8) 里, d1 / d3 (★网表侧 3/4★) / d6 / d10 (方向修正部分) / d11 (+#5) / #7 (核验) / #8 / 补差A (字段基建) 已落表; 其余全部 BLOCKED (V-1~V-6 + 板只改一次那一趟)** ⇒ ★**逐条落表记录 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` · 作业包 = `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` §8 · 交接单 = `HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md`** ★

| 项号 | 落表状态 | 卡在谁 |
|---|---|---|
| d1 | ★**已落表** (R1 转绿) ★ | — |
| d6 | ★**已落表** (R6 转绿) ★ | 堆叠数值归 MECH + 项目总工 (V-5) ⇒ ★本页不自带第二个数★ |
| d10 | ★**部分落表** (R10 4→1) ★ | ★**V-4** (R_ILIM 档位, 老板待拍) ★ |
| d11 / #5 | ★**已落表** (R11 转绿) ★ | ★**板侧封装归属待『板只改一次』那一趟** ★ |
| #1 / 补差A | ★**部分落表** (字段基建 + 数据) ★ | ★**V-1** (B-21/B-22 的 `imp` 迁移) ★★**(★★已被 §5.5 supersede: ★**已落表** (ISS-223 第 2 批 · 05:13) ⇒ V-1 已关闭★★)★★** |
| #7 | ★**已核验** (一个字没改) ★ | — |
| #8 | ★**已落表** (并入 d10) ★ | — |
| d2 / d7 / d8 / #2 | ★**BLOCKED** ★ | ★**V-3** ★ |
| d3 | ★**★部分落表 (★2026-11-16 ISS-233★)★** ★**网表侧 3/4 已落 (表A/表B 本体行 + BOM type/value ⇒ `--expect-resolved` 21 → 18)★** | ★**★板侧 1 条 (板封装 `U_EN_SW` 的 `Value` 属性) 归「板只改一次」那一趟 (★`gen_pcb_components.py` 对已在板上的封装不重写 Value ⇒ 必须手工改 = 板侧同步清单 B-2★)★** |
| d4 / d9 | ★**BLOCKED** ★ | ★**V-2** + 板侧换封装/挪位置 ★ |
| d5 | ★**BLOCKED** ★ | ★**V-1** ★★**(★★已被 §5.5 supersede: ★**已落表** (ISS-223 第 2 批 · 05:13) ⇒ V-1 已关闭★★)★★** |
| #4 / #6 / 补差C | ★**BLOCKED** ★ | ★**ISS-199/202** + 充电板整机阶段单 (V-7) ★ |

★**门禁实测**: ★**`--expect-resolved` 的「未落表条数」50 → 29** ★ · 现状守卫 `rc=0` (★锚点表已同步: 154 → **160** 条, 一条未减; 已落表条目的 ① 现状逐字已改成新现状★) · `--selftest` **19/19** (★用例 1/5/10/14/15 的突变方向按新现状翻转★) · `--expect-resolved` `rc=1` (★预期: 剩余条目仍 BLOCKED★) ★

### ★5.4 ★★落表状态 (★ISS-233 第 3 批 · 2026-11-16 · 硬件总工执行 · ★d3 网表侧★)★★

★★**一句话**: ★**d3 的 4 条未落表里, 【网表侧 3 条】已落 (★表A L442 + 表B L531 + BOM L208 三行, 逐字改一行不多★) ⇒ ★**`--expect-resolved` 21 → 18** ★; ★**【板侧 1 条】(板封装 `U_EN_SW` 的 `Value` 属性) 仍红 ⇒ 归「板只改一次」那一趟 (板侧同步清单 B-2)★** ⇒ ★**本次落表【没有碰任何 V 值】(V-2 / V-3 / V-4 老板都没拍) ⇒ 一条 V 值都没落★** ★

| 落表项 | 逐字改了什么 | 门禁变化 |
|---|---|---|
| ★**表A L442** ★ | ★`type` `NET` → `IC`; `value` `5V 输入` → `TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)`; `note` 换成【本体行 + 4 个脚的功能 + F13 理由 + ISS-172 指针】★ | ★**R3 判据 1/4 转绿** ★ |
| ★**表B L531** ★ | ★跟着表A 走 (`type`=IC · value=器件身份描述) ★ | ★**R3 判据 2/4 转绿** ★ |
| ★**BOM L208** ★ | ★`value` = 器件身份描述; `type` `NET` → `IC`; `procurement` `待分类` → `已定型-IC` ★ | ★**R3 判据 3/4 转绿** ★ |
| ★**板封装 `U_EN_SW`.Value** ★ | ★**没动 (受保护 md5 `611b869e…` 逐字节不变)★** | ★**R3 判据 4/4 仍红 ⇒ 归板那一趟★** |

★**门禁锚点同步 (★只改【现状断言值】, 判据本体与阈值一个字没动, 锚点条数 160 → 160 一条未减★)★**: `d3_a442_type` (`type == NET` → `== IC`) · `d3_a_body` (`count(...&type!=NET) == 0` → `== 1`) · `d3_b_body` (同型) · `d3_bom208_type` (`type == NET` → `== IC`) · `d3_bom208_value` (`value == EN 输入 (高=放行底板)` → `== <器件身份描述>`) · ★**`d3_board_value` 一个字没动 (★板没动★)** ★ · ★**`--selftest` 用例4 的突变方向按新现状翻转 (`BOM L208 type` `IC→NET` 退回旧缺陷) ⇒ 21/21 仍全过★** ★

★**门禁实测 (★ISS-233 本单实跑★)★**: 现状守卫 `rc=0` (★锚点表已同步, 160 条一条未减★) · `--selftest` `rc=0` **21/21** · `--expect-resolved` `rc=1` **18 条未落表** (★落表前 21 条: R2×11 / R7 / R8 = 13 条 V-3 · R4×2 + R9×1 = 3 条 V-2+板 · R10×1 = 1 条 V-4 · R3×4 = 4 条 → 本单落掉 R3 的 3 条 ⇒ 剩 R3 板侧 1 条★) · 四道尺子全 `rc=0` (`check_netlist.py` / `check_netlist_pins.py` / `check_sch_erc.py` / `check_sch_pinfull.py`) · ★**反向自证两条都过 (★b1: 旧脚本+旧数据 ⇒ md5 逐字节回到基线 + `--expect-resolved` 回到 21 条; b2: 新脚本+旧数据 ⇒ 现状守卫红 5 条 + `--expect-resolved` 回到 21 条★) ⇒ 证明判据没被「调没」★**

---

### ★5.5 ★★落表状态 (★ISS-223 第 2 批 · 2026-11-16 05:13 · ★d5 / 补差A 值迁移 / ★V-1 已落定 = 22Ω★)★★

★★**一句话**: ★**ISS-220 (第 1 批) 落了 d1 / d6 / d10 的方向部分 / d11 / #5 / #8 / 补差A 的【字段基建】, 但 d5 与 #1 的【值迁移】当时卡在 V-1 ⇒ ★**main 裁了 V-1 = 22Ω 之后, ISS-223 (第 2 批) 把这 4 个单元格落了 ⇒ R5 全组 8 条清零** ★★ ⇒ ★**⇒ §5.3 状态表里 "d5 = BLOCKED / V-1" 与 "#1 / 补差A = 部分落表 / V-1" 两行 (★那是 2026-11-16 02:39 的状态★) 已被本节 supersede: d5 与 #1 = 已落表** ★ (★证据: `HW/SCHEMATIC_LANDING_V1_LANDED.md` 第 309-311 行 "V-1 已由 main 裁 = 22Ω"★)

| 落表项 | 逐字改了什么 | 门禁变化 |
|---|---|---|
| ★**`HW/SCHEMATIC_V1_SPEC.json` · connections[B-21] `imp`** ★ | ★`90Ω ±10% (与 MIPI 不同模板!)` → ★`22Ω ±1%` (★`z_diff` 另立 = `90Ω ±15% 受控阻抗`★) ★ | ★**R5 的 spec 侧条件转绿** ★ |
| ★**connections[B-22] `imp`** ★ | ★`90Ω ±10%` → ★`22Ω ±1%` (★同上★) ★ | ★**同上** ★ |
| ★**表A L291 (`USB_D_P_SRC` NET 行)** ★ | ★`value` `90Ω ±10% (与 MIPI 不同模板!)` → ★`22Ω ±1%`; note 里的 "阻抗 90Ω ±10%…" → ★"阻抗 22Ω ±1%; 差分阻抗 90Ω ±15% 受控阻抗" ★ | ★**R5 净表侧转绿** ★ |
| ★**表A L292 (`USB_D_N_SRC` NET 行)** ★ | ★同上 ★ | ★**同上** ★ |

★★**★注意 (★本单自己实跑出来的★)★★**: ★**板上的 `R_SER_USB_D_P` / `R_SER_USB_D_N` 本来就是 22Ω ±1% ⇒ 这一条是"网表追平板", 不是"板要改" ⇒ d5 不进板侧同步清单** ★ (★证据: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §10.1 / B-7·★本单 07:3x 实跑: 网表 L431/L432 两行 value 仍 = `22Ω ±1%`★)

★★**门禁实测 (★转录自 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §10.1 · ★ISS-223 第 2 批实跑★)★**: `--expect-resolved` 未落表条数 ★**25 → 21**★ · ★**R5 全组 8 条清零**★ · `--selftest` 用例 9 的突变方向同步翻转 (★"改坏 B-21.imp (90Ω→22Ω)" 改成 "退回 90Ω 的旧缺陷"★)

### ★★5.5.2 · 8 条 × 当前落表状态 一览 (★2026-11-16 07:3x 本单二次独立复核 · 逐条本机实读★)★★

| 任务书条 | ★定性时现状 (★历史, 已作废★)★ | ★★当前实测现状 (2026-11-16 07:3x)★★ | 落表状态 | 卡在谁 |
|---|---|---|---|---|
| (1) USB 串阻双值 | L291/L292 = `90Ω ±10%`; SPEC.json B-21/B-22 `imp` = 90Ω | ★**L291/L292 = `22Ω ±1%`; L431/L432 = `22Ω ±1%`; SPEC.json connections[40]/[41] `imp` = `22Ω ±1%`, `z_diff` = `90Ω ±15% 受控阻抗`** ★ | ★**已落表 (ISS-223 第 2 批 · 05:13) ★** | — |
| (2) CONN_LIGHT 21p vs 22p | P9 页正文 `1×21p@0.5mm` | ★**P9 页 `state/gen_schematic_pages.py:147` = `1×22p@0.5mm` + "★pin21/pin22 是地脚, 不是『5V 预留』"; 网表 L237 = `★22p@0.5mm`; 同页 `CONN_USB` 已删 / `CONN_CAM` 31p@0.3mm 三处全对上** ★ | ★**已落表 (ISS-220 第 1 批) ★** | ★堆叠数值归 MECH (V-5)★ |
| (3) SARADC 满量程 + 分压比 | 1:1 分压 @4.2V = 2.100V > 1.8V 域 | ★**官方口径已定 ([官网] RK3572 §3.10 Table 3-16 p.45-46); 分压比未落: 表A L182/L183 仍 `1M ±1%` 且 DNP** ★ | ★**口径已定 / 分压比未落** ★ | ★**V-3** ★ |
| (4) BAT_DET 漏电预算 | note 自称 `~1.65µA @5V` | ★**note 仍写 `漏电流 ~1.65µA @5V` (与 1M+1M 对不上, 真值 2.50µA @5V)** ★ | ★**未落表** ★ | ★**V-3** ★ |
| (5) USB D− ESD | D− 侧 0 颗 ESD; `D_ESD_USB_D` 自称双通道 | ★**仍只有表A L417/L418 两脚 (D+ + GND); D− 侧 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 仍裸奔; 板上 `D_ESD_USB_D` → `J_USB_C` 距离 = 47.99mm** ★ | ★**未落表** ★ | ★**V-2** + 板那一趟★ |
| (6) ISS-211 已定 4 条 | d1..d4 | ★**d1 已落; d3 网表侧 3/4 已落 (ISS-233 · 06:48), 板侧 1 条仍红; d2 = (3)(4) 未落; d4 = (5) 未落** ★ | ★**2 条已落 / 2 条未落** ★ | ★**V-2 / V-3** + 板那一趟★ |
| (7) THM-RATIO 系数方向 | `CHARGE_BOARD_SPEC.md:182` = `0.822` | ★**L182 = `ICHG/IIN = η·Vbus/Vbat = 1.216 @3.70V / 1.071 @4.20V`; L184 的 390Ω 档标「待裁决 (V-4)」; 单 pin 0.608A > 0.5A 触点额定仍红** ★ | ★**方向已落 (ISS-220 第 1 批) / 档位未落** ★ | ★**V-4** ★ |
| (8) NET-LED board 列 | 表A L12 `C_VBUS_GND` board = `MAIN_PCB` | ★**表A L10 + L12 两行 `C_VBUS_GND` 的 board 都是 `CHG_BOARD`; L508/L509 两行 `R_CHG_LED` 的 board 也都是 `CHG_BOARD`** ★ | ★**已落表 (ISS-220 第 1 批) ★** | — |

★★**★⇒ 8 条里现在还红着的只有 4 条半 (★`--expect-resolved` 18 条, 本单 07:3x 实跑数★)★★**:
· ★**(3)(4)** ★ = BAT_DET 分压比 + 漏电 note (★卡 V-3 ⇒ 13 条红: R2×11 + R7 + R8★)
· ★**(5)** ★ = USB D− 无 ESD (★卡 V-2 + 板那一趟 ⇒ 3 条红: R4×2 + R9★)
· ★**(7)** ★ = 390Ω 档位 (★卡 V-4 ⇒ 1 条红: R10★)
· ★**d3 的板侧 1 条** ★ = 板封装 `U_EN_SW`.Value (★归「板只改一次」那一趟 ⇒ R3★)
⇒ ★**★已落: (1)(2)(8) 三条 + (6) 里的 d1 与 d3 网表侧 + (7) 的方向部分 ⇒ ★**8 条里【只剩 4 条半】没落, 全部卡在 3 个 V 值 (V-2/V-3/V-4) + 板那一趟** ⇒ ★**⇒ 与 ISS-233 交卷单 §3 的【拍板即落清单】完全对齐: 老板只要拍 V-2/V-3/V-4, 剩下这 4 条半一次落干净** ★ ★

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

★**受保护 md5 (★交卷前后逐字节不变★)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★**(★这是 ISS-211 交卷时 2026-11-15 23:5x 的基线; 现已被 main 授权的 ISS-233 落表更新 ⇒ 现行值见文件头「受保护 md5 · 现行值」行★)**

---

## 10. ★★第 2 轮 (★ISS-214 · 2026-11-16★) 5+2 条 · ★★每条 8 栏齐★★ ★★

> ★**本节是 §1 第 1 轮 4 条的【扩写】, 不是另起炉灶**: ★**第 1 轮 (ISS-211) 的 d1..d4 锚点 (64 条) 一条不许删**, ★**本节 7 组新锚点 (d5..d11, 90 条) 加在同一个锚点表里** ⇒ ★**"规格页 ⇄ 脚本 ⇄ 现行文件"三方对齐仍然只有一套**.
> ★**本节不写任何"已经改好", 只写"现状逐字 + 该改成什么 + 验收判据"** ⇒ ★**门禁仍然是【现状守卫】不是【合格证】**.
> ★**★★★重要 (★2026-11-16 07:3x 二次独立复核 加的提示★)★★★**: 本节各条的 ① 现状 = 【**定性时的原文** (2026-11-16 00:4x~00:5x 实读)】 ⇒ ★**凡后来落过表的条目 (d5 / #1 / d6 / d11 / #8 / d10 的方向部分 / d3 的网表侧), 那些行的现值已经被后续落表改写 ⇒ 本节的 ① 现状【不可】再当"现在的文件长什么样"用** ★ ⇒ ★**逐条当前实测现状见 §5.5.2 的对账表; 落表状态见 §5.3 / §5.4 / §5.5 三段★★**

★**本节 8 条与任务书的对应 (★一条不重一条不漏★)**:

| 任务书条 | 本节条号 | 锚点组 | 来源 | 状态 |
|---|---|---|---|---|
| (1) USB 串阻双值 | ★**第 (1) 条** ★ | `d5` | ISS-211 附带发现 #1 | ★**新增** ★ |
| (2) CONN_LIGHT 21p vs 22p | ★**第 (2) 条** ★ | `d6` | ISS-213 PIN-MISMATCH / STK-P9 | ★**新增** ★ |
| (3) SARADC_VIN5 满量程 | ★**第 (3) 条** ★ | `d7` | ISS-211 U-2 | ★**新增** ★ |
| (4) BAT_DET 漏电预算 | ★**第 (4) 条** ★ | `d8` | ISS-211 U-4 | ★**新增** ★ |
| (5) USB D− ESD 方案+型号 | ★**第 (5) 条** ★ | `d9` | ISS-211 U-1 | ★**第 1 轮已定位缺陷, 本轮补方案与型号判据** ★ |
| (6) ISS-211 已定的 4 条 | ★**§1 (第 1 轮 4 条)** ★ | `d1..d4` | ISS-211 | ★**并进同一锚点体系, 规格页不重写** ★ |
| (7) §3.4 ICHG/IIN 方向 | ★**第 (7) 条** ★ | `d10` | ISS-213 THM-RATIO | ★**新增** ★ |
| (8) NET-LED board 列 | ★**第 (8) 条** ★ | `d11` | ISS-213 NET-LED | ★**新增 (★转述与实跑不一致, 见第 (8) 条 ①★)** ★ |

---

### ★★第 (1) 条 ★★ USB 串阻: ★同一颗器件两个阻值 (90Ω vs 22Ω) ★★

#### ① 现状 (★逐字原文 + 行号★)

★**表A `HW/netlist_v1.csv`**:

| 行 | 原文 (逐字) |
|---|---|
| ★**L291** | `P6,USB_D_P_SRC,J_SOM_P1 pin92,R_SER_USB_D_P,NET_USB_D_P_SRC,90Ω ±10% (与 MIPI 不同模板!),NET,必装,[待原厂],TBD-10,方向 SoC↔Type-C; 电平 3.3V [待原厂]; 阻抗 90Ω ±10% (与 MIPI 不同模板!); 连接 Type-C → 主 PCB (跨铰链则经 CONN_USB); 测试点 TP_USB_D+,B-21,MAIN_PCB,,` |
| ★**L292** | `P6,USB_D_N_SRC,J_SOM_P1 pin94,R_SER_USB_D_N,NET_USB_D_N_SRC,90Ω ±10%,NET,必装,[待原厂],TBD-10,方向 SoC↔Type-C; 电平 3.3V [待原厂]; 阻抗 90Ω ±10%; 连接 同上; 测试点 TP_USB_D-,B-22,MAIN_PCB,,` |
| ★**L431** | `P1,NET_USB_D_P_TYPEC,R_SER_USB_D_P,J_USB_C A6+B6,R_SER_USB_D_P,22Ω ±1%,R,必装,[推算],,"[NET_USB_D_P_TYPEC] ★SoM USB2 (OTG1) D+ → 板载 Type-C: 串阻的 Type-C 侧 (★串阻必须真串在中间, 不能与 SoM 侧同网★)",A-24,MAIN_PCB,,` |
| ★**L432** | `P1,NET_USB_D_N_TYPEC,R_SER_USB_D_N,J_USB_C A7+B7,R_SER_USB_D_N,22Ω ±1%,R,必装,[推算],,[NET_USB_D_N_TYPEC] ★SoM USB2 (OTG1) D- → 板载 Type-C: 串阻的 Type-C 侧,A-24,MAIN_PCB,,` |

★**规格源头 `HW/SCHEMATIC_V1_SPEC.json`** (★`connections` 数组, 共 57 条★):

```json
{ "id": "B-21", "group": "B", "signal": "USB_D+", "dir": "SoC↔Type-C",
  "level": "3.3V [待原厂]", "imp": "90Ω ±10% (与 MIPI 不同模板!)", … }     ← connections[40]
{ "id": "B-22", "group": "B", "signal": "USB_D-", "dir": "SoC↔Type-C",
  "level": "3.3V [待原厂]", "imp": "90Ω ±10%", … }                            ← connections[41]
```

★**项目自己已经把"90Ω 是什么"写清楚了 (★根因的直接证据★)** ⇒ ★**`HW/EMC_PRECHECK.md:211`** 逐字:
> `4. **USB 2.0 差分**: D+/D- 90 Ω 差分, 480 Mbps, 与 MIPI 的 100 Ω **不是同一套阻抗模板** (混用会导致其中一路失配)。`

★**⇒ "90Ω" 是【差分线阻抗】, 不是【串联电阻值】** ⇒ ★**L291/L292 的 note 自称"与 MIPI 不同模板!" = 写的人自己知道模板串了, 但没改★**。

#### ② 问题 (★可判定依据★)

1. ★**同一颗器件 `R_SER_USB_D_P` 两个阻值**: L291 = `90Ω ±10% (与 MIPI 不同模板!)`, L431 = `22Ω ±1%` ⇒ **差 4.09 倍**; D− 同款 (L292 vs L432)。
2. ★**电气上是【串联在同一条 USB D+ 通道上】**: `USB_D_P_SRC → R_SER_USB_D_P → NET_USB_D_P_TYPEC → J_USB_C A6+B6` ⇒ **两行字指向同一颗电阻** ⇒ 谁读到哪一行, 结论就相反。
3. ★**90Ω 串阻在 90Ω 线上是物理错误 (不是"两种风格")**: 源端驱动 + 90Ω 串阻 + 90Ω 线 ⇒ **源端看到的负载变成 180Ω ⇒ 电压摆幅只剩 ~1/2 ⇒ 眼图直接不合规** ⇒ ★**90Ω 这个数在任何串阻语境下都不成立**。
4. ★**官方口径 (★自己查的, 不靠转述★)**: ON Semiconductor 应用笔记 **AND8074/D** (onsemi 官网) 逐字:
   - 「The USB twisted pair cable has a characteristic impedance of (Zo) of **90 Ω ±15%**.」
   - 「According to the USB 1.1 specification, the USB differential driver line must match the cable impedance … The USB 1.1 specification requires a series resistor with value between **28 Ω and 44 Ω**.」
   - 「Nevertheless, it has been found through some research that most of the industrial drivers require a series resistor of **22 Ω or 30 Ω** …」
   ⇒ ★**串阻 = 22Ω (工业/官方 de-facto 值); 90Ω = 线阻抗** ⇒ ★**两者同时存在, 但必须写在两个不同的字段里**。

#### ③ 根因 (★追到源头, 不许停在网表★)

★**根因 = `HW/SCHEMATIC_V1_SPEC.json` 的 `connections[40]/[41].imp` 字段被填成了【差分线阻抗模板】** ⇒ ★**`state/gen_netlist.py:770-774` 的 `conn_row()` 文档自己写着**:
```
def conn_row(by_id, cid, page, net, n1, n2, ref, value=None, note_extra=""):
    """把规格里的一条连接展开成 netlist 的 NET 行。
    value 默认取规格 imp (A 组阻抗必须与规格逐字一致 · check_netlist 判据 5)。"""
```
⇒ ★**⇒ 真修法 = 改 SPEC.json 的 `connections[40]/[41].imp`, 不是手改网表** (★手改 CSV 会被下次重跑生成器覆盖 ⇒ 那就是"改在产物上", 老毛病★)。

★**★根根根 (★本单新挖★)**: ★**`imp` 一个字段同时服务两种语义** ⇒ ★**同一个 SPEC.json 里, DSI 那组是【对的写法】**: DSI 的 NET 行写 `100Ω ±10%` (= MIPI 差分阻抗, 对), 器件行写 `0Ω` (= `R_SEL_*` 是 DSI 直通位, 也对) ⇒ **两个物理量各归各, 所以不打架**; ★**而 USB 这组把差分阻抗写进了 `imp`, 同时又有一颗真正的 22Ω 串阻 ⇒ 两个物理量被塞进同一个字段 ⇒ 必然打架** ⇒ ⇒ **模板必须分字段 (`imp` 串阻值 / 另设 `z_diff` 差分阻抗), 不是改一个数** ★(★见 §11 附带发现 #2★)。

#### ④ 目标取值或判据

| 项 | 目标 | 依据 |
|---|---|---|
| ★**串联电阻** ★ | ★**22Ω ±1%** (★保持 L431/L432 现状值不变★) ★ | ★[官网] AND8074/D (USB 1.1 规范 28~44Ω; 工业主流 22Ω 或 30Ω) + ★[官网] onsemi **STF202-22T1G** datasheet (Rev 11, 2025-03): 内置串阻 `Series Resistor RS = 20 / **22** / 24 Ω` (min/nom/max) ★ |
| ★**差分线阻抗** ★ | ★**90Ω ±15% 受控阻抗 (板级)** ⇒ ★**不许再写进"串阻"字段** ★ | ★[官网] AND8074/D (Zo = 90Ω ±15%) ★ |
| ★**USB 速率** ★ | ★**480 Mbps (USB 2.0 High-Speed)** ⇒ ★**这是选 ESD 件与走线阻抗的预算基准** ★ | ★[实测] `HW/EMC_PRECHECK.md:211` ★ |
| ★**是否允许外部串阻** ★ | ★**允许, 但值随 SoM PHY 的驱动阻抗变** ⇒ ★**SoM 手册的 USB PHY 驱动阻抗 = [0数据]** ⇒ ★**降级路径: 若 SoM 手册说"内部已匹配, 不需要外部串阻" ⇒ 串阻位改成 0Ω/贴 0Ω, ★但 90Ω 那个错值仍必须清掉** ★ | ★[0数据] SoM (Forlinx) 手册 ★ |

#### ⑤ 该改哪张表的哪一行

| 步骤 | 改哪个文件 | 改哪个字段 | 从 → 到 |
|---|---|---|---|
| ★**1a** ★ | ★`HW/SCHEMATIC_V1_SPEC.json` ★ | ★`connections[]` 里 `id == "B-21"` 的 `imp` ★ | ★`90Ω ±10% (与 MIPI 不同模板!)` → ★`22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)` ★ |
| ★**1b** ★ | ★`HW/SCHEMATIC_V1_SPEC.json` ★ | ★`connections[]` 里 `id == "B-22"` 的 `imp` ★ | ★`90Ω ±10%` → ★`22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)` ★ |
| ★**1c** ★ | ★`HW/SCHEMATIC_V1_SPEC.json` ★ | ★`connections[]` 里 `id == "B-21"/"B-22"` 的 `level` ★ | ★`3.3V [待原厂]` → ★**保留** (★USB 差分不是电平问题; 但 [待原厂] 标记可随 SoM 手册关掉★) ★ |
| ★**1d** ★ | ★**不许手改 `HW/netlist_v1.csv`** ★ | — | ★**改完 SPEC.json 重跑 `state/gen_netlist.py` ⇒ L291/L292 的 value 自动就对了; L431/L432 的器件行 value (= `22Ω ±1%`) 不用动 ⇒ 两行口径一致** ★ |

#### ⑥ 验收判据

- 表A **不再有任何** value 含 `90Ω ±10%`
- 表A L291/L292 的 value 与 L431/L432 (`22Ω ±1%`) **口径一致** (都含 `22Ω`)
- `SPEC.json` B-21/B-22 的 `imp` 含 `22Ω` 且 **不含** `90Ω ±10%`
- ★**门禁 `--expect-resolved` 的 R5 rc=0**

#### ⑦ 证据等级

★**[实测]** 表A L291/L292/L431/L432 逐字 · `SCHEMATIC_V1_SPEC.json` connections[40]/[41] 全文 · `EMC_PRECHECK.md:211` 逐字 · `gen_netlist.py:770-774` 逐字 · ★**[官网]** ON Semi AND8074/D (串阻 28~44Ω 规范 / 22Ω·30Ω 工业值 / Zo 90Ω±15%) · onsemi STF202-22T1G datasheet (RS nom 22Ω) · ★**[推算]** "90Ω 串阻 ⇒ 摆幅减半" · ★**[0数据]** SoM USB PHY 的驱动阻抗 / 外部串阻是否必需。

---

### ★★第 (2) 条 ★★ CONN_LIGHT: ★P9 页正文 21p vs 网表 22p (★+ 同页另两处也对不上★) ★★

#### ① 现状 (★逐字原文 + 行号★)

★**`state/gen_schematic_pages.py:147` (★P9 页正文, ★手写字符串, 不是从网表生成的★)** 逐字:
```
  4. `CONN_LIGHT` (**1×22p@0.5mm**, 座 HIROSE FH12-22S-0.5SH(55), ★板内 FPC 座★) — pin1 = GND · 2/3 = DSI D0_D1 N/P · 4 = GND · 5/6 = DSI CK N/P · 7 = GND · 8/9 = D0_D0 N/P · 10 = GND · 11/12 = I2C_B SCL/SDA · 13 = GND · 14/15 = LIGHT_3V3 · 16/17 = D0_D2 N/P · 18/19 = D0_D3 N/P · 20/21/22 = GND (回流; ★**pin21/pin22 是地脚, 不是『5V 预留』**★)
```
★**同页第 147 行所在段的堆叠账** 逐字:
```
  ★**铰链区高度预算 (★口径 = 结构侧现行值, 本页不自带第二个堆叠数★)**: 跨铰链只剩 **1 组** (`J_CHG` 10p), 触点区 **0.5mm pitch** → ★**FPC 带宽口径见 `MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 08 项 STK-P9** (★= 触点区 + 4 条×2×0.50 走线边距★) vs 镜脚根部净高 **38.00mm** (★`MECH/cross_review_check.py` 锁死值; ★**37.0 是已作废的叠放模型算式 (22+12+3), 不许再用**★) ⇒ ★**余量按结构侧现行口径核算 (★数值归 MECH + 项目总工, 待 V-5 裁决; ★本页不自带第二个数★)**★ ✅ (收敛前按 40p 声明是 54.7mm, **放不下**)。
```
★**★同页另外两条通道的 pin 数/pitch/归属, 也与现行网表对不上 (★本单新挖★)** ★:

| P9 页正文 (逐字) | 现行网表实测 | 判定 |
|---|---|---|
| ★`2. \`CONN_USB\` (**4p@0.5mm**) — USB 2.0 差分 (**烧录/调试口唯一通路**) + 独立回流地 + 1 预留` ★ | ★**网表里 `CONN_USB` 一个 ref 都没有** (count = 0) ★ ⇒ `state/gen_netlist.py:117` 的注释自己写着 `HINGE_REFS = {"J_CHG"}   # ★2026-11-04 19:5x: CONN_USB 跨铰链 USB 座已删 (跨铰链取消)` ★ | ★**通道已删, 页面没删** ★ |
| ★`3. \`CONN_CAM\` (**18p@0.5mm**) — pin1/2 = CSI CK · … · **pin18 = 独立回流地**` ★ | ★网表 L290 的 value = `★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 HIROSE FH35C-31S-0.3SHW(50); 针位见 HW/PCB/FPC_PIN_TABLES.md)`; 脚表 31 行; board = `MAIN_PCB` ★ | ★**18p@0.5 vs 31p@0.3** ★ |
| ★`4. \`CONN_LIGHT\` (**1×21p@0.5mm**)` ★ | ★网表 L237 的 value = `★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱; 官方封装抄 RPi CM5IO)`; 脚表 22 行 (pin1..pin22); BOM L5 同串; board = `MAIN_PCB` ★ | ★**21p vs 22p** ★ |

★**★更关键的一条 (★本单新挖★): 这三条里有两条根本不是"跨铰链链路"** ★
⇒ 网表里 board == `HINGE` 的连接器**只有 `J_CHG` 一个** (1×10p@0.5mm); `CONN_CAM` / `CONN_LIGHT` 都是 `MAIN_PCB` 的**板内 FPC 座** ⇒ ★**P9 页的"4 组跨铰链通道"在现行网表下不成立**。

★**堆叠账的三个数对应三个不同的物理模型 (★而且分母已作废★)**:

| 数 | 算式 | 物理模型 | 状态 |
|---|---|---|---|
| ★**26.5mm** ★ | (10+4+18+21)×0.5 ★ | 触点区口径, 且 **21 写错了** ★ | ★**P9 页 + `DECISIONS.md` (2026-10-27 项目总工) 在用** ★ |
| ★**27.00mm** ★ | (10+4+18+22)×0.5 ★ | 触点区口径 (22p 对) ★ | ★`MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 08 项 `STK-FPC` 在用 ★ |
| ★**35.50mm** ★ | 27.00 + 4 条×2×0.50 走线边距 ★ | ★**FPC 带宽口径** (★真正能拿去跟腔体净高比的★) ★ | ★MECH 现行口径 ★ |
| ★**37.0mm** ★ | — | ★**已作废的叠放模型算式 (22+12+3)** ★ | ★**作废** ⇒ 现行锁死的腔体净高 = **38.00mm** (`MECH/cross_review_check.py:64` 逐字: 「★**37.0 是已作废的叠放模型**算式 (22+12+3) —— 现行是**锁死的腔体净高 38.00**」) ★ |

#### ② 问题 (★可判定依据★)

1. ★**同一张网表两个 pin 数** (21 vs 22) ⇒ **堆叠账少 0.50mm**。
2. ★**另两处也对不上** (CONN_USB 已删 / CONN_CAM 18→31@0.3) ⇒ **⇒ 这个账不是"错了一个数", 是"整个账的输入全过期了"**。
3. ★**"4 组跨铰链通道"与网表的 board 列矛盾** (实际 1 组) ⇒ **铰链区结构方案按 4 条算的 ⇒ 结构余量算的是错的**。
4. ★**一个 boss 级决策记录引用了一个站不住的数**: `DECISIONS.md` (2026-10-27 · 项目总工) 逐字: 「…**J_CHG 保持 1×10p@0.5mm** (pin map 定稿…) → 铰链区堆叠仍 **26.5mm (余 10.5mm)** → 结构复核走 ISS-091」 ⇒ ★**⇒ 落表那趟必须把这个决策记录的 26.5 一起改掉, 不能让两个数并存**。

#### ③ 根因 (★追到源头★)

★**P9 页正文是 `state/gen_schematic_pages.py` 里 `PAGES` 字典的【手写字符串】, 不从网表生成** ⇒ ★**网表 2026-11-04 定稿 22p 时, 页面没跟** ⇒ ★**与第 (1)(3) 条同型: 改在产物/手写副本上, 没有单一真源**。
★**pin 数的真值源 (三处互证 + 官方封装)** = `HW/netlist_v1.csv` L237 (器件行) + `HW/netlist_v1_pins.csv` (22 脚行) + `HW/BOM_v1.csv` L5 ⇒ 封装 = **Hirose FH12-22S-0.5SH(55)** (★官方 RPi CM5IO / Pi5 DISPLAY 座封装抄用, 网表 note 自引★) ⇒ ★**22p 是真值**。

#### ④ 目标取值或判据

- ★**22p 是真值** ⇒ ★**修 P9 页, 不修网表/脚表/BOM**。
- ★**堆叠账唯一口径 (★本单的硬件判据, 最终数字归 MECH + 项目总工★)**:
  ① **口径** = ★**FPC 带宽口径 35.50mm** (触点区 + 4 条×2×0.50 走线边距) —— ★**触点区口径 (26.5 / 27.00) 是不完整代理, MECH 已证它漏算 8.50mm 走线边距** ★
  ② **分母** = ★**锁死的腔体净高 38.00mm** (★不是 37.0, 37.0 已作废★)
  ③ ★**⇒ P9 页的 26.5 与 DECISIONS.md 的 26.5 必须同时废掉** (★两个数并存 = 下次还会打架★)
  ④ ★**降级方案**: 若结构那边这一轮不出新数 ⇒ ★**P9 页不许再自带一个堆叠数**, 改成**引用**结构侧的现行口径 + 写清"净高 38.00" ⇒ ★**宁可不写数, 也不写第二个错数** ★
- ★**另两条硬判据 (可机器判)**:
  - ① P9 页每个 FPC 位号的 **pin 数 + pitch** 必须与网表器件行的 value **逐字一致**
  - ② **跨铰链通道数**必须 = 网表里 board==`HINGE` 的连接器个数 (★现行 = 1: `J_CHG`★) ⇒ ★**P9 页的"4 组跨铰链通道"必须改成"1 组跨铰链 + 3 条板内 FPC"** ★

#### ⑤ 该改哪张表的哪一行 (★两条路 + 各自代价★)

| 路 | 动作 | 代价 | 判定 |
|---|---|---|---|
| ★**路 A (★推荐★)** ★ | ★改 **`state/gen_schematic_pages.py` L147 那一段 P9 页正文** (手写字符串) ⇒ 把 `1×21p` 改 `1×22p`、把 21 脚的说明改成 22 脚 (★按脚表: pin21 = GND / pin22 = GND, 不是"5V 预留"★)、把 `CONN_CAM (**18p@0.5mm**)` 改成 `CONN_CAM (**31p@0.3mm**)`、把 `CONN_USB` 那条删掉/改成"已删", 把通道数改成 1 组跨铰链 + 3 条板内 FPC、把堆叠算式按上面的唯一口径重写 ★ | ★**★要重跑 `state/gen_schematic_pages.py` ⇒ P9 页 svg 重出 ⇒ P9 页 svg 在投产包里 ⇒ 必须跟板那一趟一起重出★** ★(★本单不动手★) ★ | ★**★走这条★** ★ |
| ★**路 B** ★ | ★改网表/脚表/BOM, 把 22p 砍成 21p ★ | ★**★把官方 RPi5 封装抄用改错★; 要砍掉的是 pin21/pin22 两只 GND 预留脚; `HW/PCB/PI5_DSI_22P_PINOUT.md` + BOM + 器件表 + 脚表 22 行全要跟着砍; 而且 21 根本不是任何官方封装★** ⇒ **代价更大且方向错** ★ | ★**★判死 (已评估并否决)★** ★ |

★**★两条路的共同结论 (★这就是"改生成器 vs 改网表"的取舍★)**: ★**P9 页正文住在生成器里 ⇒ 改它 = 改源 (合法); 手改 svg = 改在产物上 (会被下次重跑覆盖, 非法)** ⇒ ★**路 A 是唯一合法路**。

#### ⑥ 验收判据

- P9 页正文 **不再含** `1×21p@0.5mm` / `CONN_CAM` `(**18p@0.5mm**)` / `CONN_USB` `(**4p@0.5mm**)` / `(10+4+18+21)×0.5`
- P9 页正文 **含** `1×22p@0.5mm`
- 脚表 `count(ref==CONN_LIGHT) == 22` 保持 (不许靠砍脚表"对齐"页面)
- ★**门禁 `--expect-resolved` 的 R6 rc=0**

#### ⑦ 证据等级

★**[实测]** `gen_schematic_pages.py:147` 逐字 · 网表 L237/L290 逐字 · 脚表 22/31 行计数 · BOM L5 · `DECISIONS.md` (2026-10-27) 逐字 · `MECH/cross_review_check.py:64` 逐字 · `gen_netlist.py:117` 注释逐字 · ★**[官方]** 官方 RPi CM5IO / Pi5 DISPLAY 座封装 = Hirose FH12-22S-0.5SH(55) (★网表/BOM 自引封装抄用★) · ★**[推算]** 26.5/27.00/35.50 三数对应的物理模型 · ★**[0数据]** 铰链段实际堆叠 (要等结构实测/印包)。

---

### ★★第 (3) 条 ★★ SARADC_VIN5 满量程 + BAT_DET 分压比 (★ISS-211 U-2 · 本轮已用官方 datasheet 关掉一半★) ★★

#### ① 现状 (★逐字原文 + 行号 + 官方表逐字抄录★)

★**★[官网] `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` 第 3.10 节 Table 3-16 (PDF 第 45-46 页) 逐字抄录** (★同目录已抽取 `rk3572_datasheet_V1.1.txt` 第 2856-2870 行, ★门禁锚 `d7_rk_*` 就钉在这个文件上★):
```
3.10 Electrical Characteristics for SARADC
                                   Table 3-16 Electrical Characteristics for SARADC

           Parameters            Symbol             Test condition          Min         Typ         Max     Unit
Resolution                                                                 NA           12         NA       Bit
Anglog Input Range             AIN                                        AVSS18       NA         AVDD18    V
Differential Non-Linearity     DNL            PD=Low                       NA          ±1.0        ±3.0    LSB
Integral Non-Linearity         INL            Fs=1MS/s                     NA          ±2.0        ±6.0    LSB
Top Offset Voltage Error       EOT            FSOC=1MHz                    NA          ±10         ±20     LSB
Bottom Offset Voltage Error    EOB            FAIN=10kHz ramp wave         NA          ±10         ±20     LSB
```
★**★官方表头把 "Analog" 拼成 "Anglog" (★原文如此, 逐字抄录, 不许"顺手改对"★)★**
★**同 datasheet 电气特性总表逐字**: `SARADC Analog Power(1.8V)   SARADC_AVDD1V8   1.62   1.8   1.98   V` ⇒ ★**AVDD18 = 1.8V 标称 / 1.62~1.98V 范围** ★
★**同 datasheet §1.2 特性逐字**: `Successive approximation ADC(SARADC)` / `Supports 12-bit resolution` / `Supports up to 1MS/s sampling rate` / `Supports 8 single-ended input channels`

★**SoM 厂 IO 域表 `HW/PCB/FET3572C_PIN_TABLE.csv` 第 39 行逐字**: `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` ⇒ ★**P1_38 = SARADC_VIN5, 1.8V 域**

★**表A `HW/netlist_v1.csv`**:

| 行 | 原文 (逐字) |
|---|---|
| ★**L181** | `P2,BAT_DET,RAIL_BAT,R_BAT_DET_1,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,[推算],,"方向 充电板→SoC; 电平 0-3.3V (分压); 阻抗 1M+1M 分压 + 100nF; 连接 电池 BAT → ADC; 测试点 TP_BAT",B-08,MAIN_PCB,,` |
| ★**L182** | `P2,BAT,RAIL_BAT,R_BAT_DET_1,R_BAT_DET_1,1M ±1%,R,DNP,[推算],,"[R_BAT_DET_1] ★DNP: 同上 (电池电压分压上臂) \| [BAT_DET_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 BAT 已归一到源节点]",B-08,MAIN_PCB,,` |
| ★**L183** | `P2,BAT_DET,R_BAT_DET_2,GND,R_BAT_DET_2,1M ±1%,R,DNP,[推算],,"[R_BAT_DET_2] ★DNP: 同上 (电池电压分压下臂) \| [BAT_DET] 分压下臂 地端",B-08,MAIN_PCB,,` |
| ★**L184** | `P2,BAT_DET,C_DET_BAT,R_BAT_DET_2,C_DET_BAT,100nF ±10%,C,DNP,[推算],,"[C_DET_BAT] ★DNP: 同上 (电池 ADC 滤波) \| [BAT_DET] ADC 滤波电容 (★V1.2: 电池在镜脚, 本地检测, 不跨铰链)",B-08,MAIN_PCB,,` |
| ★**L185** | `P2,GND,C_DET_BAT,GND,C_DET_BAT,100nF ±10%,C,DNP,[推算],,"[C_DET_BAT] ★DNP: 同上 (电池 ADC 滤波) \| [BAT_DET] ADC 滤波电容 地端",B-08,MAIN_PCB,,` |
| ★**L186** | `P2,BAT_DET,J_SOM_P1 pin38,NET_BAT_DET,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,[推算],,"[BAT_DET] SoC ADC 输入节点 (跨板那一侧)",B-08,MAIN_PCB,,` |

★**BOM `HW/BOM_v1.csv`**: ★**L86** `R_BAT_DET_1,1,1M ±1%,R,DNP` · ★**L87** `R_BAT_DET_2,1,1M ±1%,R,DNP` · ★**L27** `C_DET_BAT,1,100nF ±10%,C,DNP` ⇒ ★**BOM 也说"不装"**。

#### ② 问题 (★可判定依据★)

★**★"1:1 分压会烧脚"这个判断, 现在有【官方】兜底了, 不再依赖 SoM 的 abs-max ([0数据])★**:
1. 分压中点 @BAT_max = 4.2V (`HW/INTERFACE_TABLE.md` C-03 "4.2V 满 / 3.0V 截止") ⇒ **V_node = 4.2 × 1M/(1M+1M) = 2.100V**
2. ★**官方 AVDD18 = 1.8V 标称, max 1.98V** ⇒ ★**2.100V > 1.98V (AVDD18 max) ⇒ 超 0.120V (6.1%) ⇒ 过压** ⇒ ★**⇒ 连 SoM 自己的 abs-max 都不需要了, 芯片级就已经判死** ★(★这就把 ISS-211 的 U-2 关掉一半★)
3. ★**并且 L181 的 note 自称 "电平 0-3.3V (分压)" ⇒ 与 P1_38 的 1.8V 域直接矛盾** ⇒ ★**同一行字又自己打架 (与第 (1) 条同型)** ★

#### ③ 根因 (★追到源头★)

★**`state/gen_netlist.py` 里 BAT_DET 那段的 `add(...)` 写死了 "1M+1M" 与 "1M ±1%"** ⇒ ★**不是"写错了", 是"从来没人定过分压比"** ⇒ ★**因为定分压比的判据需要 SoM ADC 参数, 而项目库当时没有 ⇒ ⇒ 缺陷一直"合法地"存在** ⇒ ★**⇒ 本轮用 RK3572 官方 datasheet 把【上限】这一半补上 ⇒ 分压比第一次有了可判的边界** ★(★ISS-211 第 (2) 条已定位到这一层★)。

#### ④ 目标取值或判据 (★三条, 缺一条不许落★)

| 判据 | 内容 | 数值 |
|---|---|---|
| ★**① 上限** ★ | 分压后中点 @4.2V (含 ±1% 电阻容差) **≤ 1.8V** (标称) 且 **≤ 1.98V** (★[官网] AVDD18 max★) | ★上/下臂比 **≥ 2.33 : 1** ★ |
| ★**② 下限 (12bit 利用率)** ★ | 分压后中点 @4.2V **≥ 1.2V** (≥66.7% 满量程) ⇒ 否则 12 bit 白扔 | ★上/下臂比 **≤ 3.5 : 1** ★ |
| ★**③ 源阻抗** ★ | 有 100nF 滤波电容当电荷蓄水池 ⇒ 采样瞬间从分压器取的 ΔQ ≈ Cin×Vref/2¹² (Cin≈5pF ⇒ ≈2.2pC) ⇒ 在 1MΩ 上产生的误差压 ≈ 0.44mV ≈ **1 LSB** ⇒ **可接受** ⇒ ★**源阻抗不是阻塞项** (★但 Cin 是 [0数据] ⇒ 见降级方案★) | —— |

★**候选分压比 (含 4.2V 满充 / ±1% 电阻容差 / worst = 下臂+1% & 上臂−1%)★**:

| 方案 | 上臂 | 下臂 | V_node@4.2V typ | V_node worst | 满量程利用率 | 漏电@4.2V | 判定 |
|---|---|---|---|---|---|---|---|
| ★**A** ★ | ★**2.0M ±1%** ★ | ★**1.2M ±1%** ★ | ★**1.575V** ★ | ★**1.595V** ★ | ★**87.5%** ★ | ★**1.31µA** ★ | ★**★推荐 (三个指标同时最优)★** ★ |
| B | 1.0M ±1% | 560k ±1% | 1.508V | 1.558V | 83.8% | 2.69µA | 可 (余量 0.242V) |
| C | 1.0M ±1% | 680k ±1% | 1.700V | 1.749V | 94.4% | 2.50µA | ★**不推荐 (离 1.8V 只剩 0.051V)★** |
| ★**D** ★ | ★2.0M ±1%★ | ★1.0M ±1%★ | ★1.400V★ | ★1.419V★ | ★77.8%★ | ★1.40µA★ | ★**★降级档 (SoM 手册给更严 abs-max 时用)★** ★ |
| ★**✘ 现值** ★ | 1.0M | 1.0M | ★**2.100V** ★ | —— | —— | 2.10µA | ★**过压, 判死★** ★ |

★**★推荐 A 的三条理由 (★硬件总工的取舍, 不替老板拍★)** ★:
① ★**1.595V ≤ 1.8V** (余量 0.205V) 且 ≤ 1.98V (余量 0.385V) ⇒ ★**即使 SoM 的 abs-max 比 RK3572 更严, 还有 D 档兜底★**
② ★**87.5% 满量程利用率** ⇒ 电池 3.0~4.2V 映射到 1.125~1.575V ⇒ 1024 个码覆盖电池区间 (12bit 总共 4096) ⇒ ★**电量显示够用**
③ ★**漏电 1.31µA 比现值 2.10µA 还低** ⇒ ★**顺手把第 (4) 条的漏电顾虑也解掉 (见第 (4) 条)★**

★**★降级方案 (SoM 手册拿不到时)★**: ★**直接用 A (2.0M + 1.2M)**, 不等 SoM 手册 ⇒ ★**理由: A 的余量 0.205V 已经覆盖了"1.8V 标称"这一档, 而 D (2.0M+1.0M, 1.419V) 覆盖"1.5V abs-max"那一档 ⇒ ★**⇒ 绝不选 1:1**** ★(★★SoM 手册一旦拿到, 只需核对"Cin / 采样保持时间 / 模块 abs-max"三条, 不用重算分压比★★)。

#### ⑤ 该改哪张表的哪一行

| 步骤 | 改哪个文件 | 改什么 | 说明 |
|---|---|---|---|
| ★**3a/3a'** ★ | ★`state/gen_netlist.py` (BAT_DET 段) + `state/gen_netlist_pins.py` ★ | ★4 行 (`R_BAT_DET_1`/`R_BAT_DET_2`/`C_DET_BAT`×2) 的 `dnp`: `DNP` → `必装` ★ | ★ISS-211 第 (2) 条 3a/3a' 已经在规格里, 本条只补阻值 ★ |
| ★**3b** ★ | ★`state/gen_netlist.py` (BAT_DET 段) ★ | ★`value`: `1M ±1%` → ★**`2.0M ±1%` / `1.2M ±1%`** ★ | ★**本单不定 (老板级), 但本单把候选/判据/推荐给全了** ★ |
| ★**3c** ★ | ★`state/gen_netlist.py` (BAT_DET 段) ★ | ★`note`: "★DNP: 同上" → 写全 (含 ★**新的漏电流数**★, 见第 (4) 条) ★ | ★ISS-211 第 (2) 条 3c ★ |
| ★**3d** ★ | ★`state/gen_netlist_pins.py` ★ | ★`J_SOM_P1.pin38` 的 note 改成 BAT_DET 的说明 ★ | ★ISS-211 第 (2) 条 3d (现在它是 pin100 那行的复制品) ★ |
| ★**3e** ★ | ★`HW/netlist_v1.csv` L181 / L186 的 value 栏 ★ | ★`1M+1M 分压 + 100nF` → `2.0M+1.2M 分压 + 100nF` ★ | ★★由重跑生成器自动来, 不许手改★ ★ |

★**⚠ 本单不许改网表 / 脚表 / 生成器 / SPEC.json ⇒ 上面 5 步全部归"整链重出 第 1 步"那一趟** ★。

#### ⑥ 验收判据

- 门禁 **R2** (分压后 ≤ 1.8V) 过 + 门禁 **R7** (分压后 ≥ 1.2V) 过
- 表A/表B/BOM 三处 `R_BAT_DET_1`/`R_BAT_DET_2`/`C_DET_BAT` 的 `dnp` **全部 ≠ DNP**
- L181/L186 的 value 栏与实际阻值一致 (`2.0M+1.2M 分压 + 100nF`)
- L182 的 note 里的漏电流数与阻值自洽 (见第 (4) 条)

#### ⑦ 证据等级

★**[官网]** RK3572 Datasheet Rev 1.1 §3.10 **Table 3-16 (PDF p.45-46)** 逐字 (Resolution 12 Bit / Anglog Input Range AVSS18~AVDD18 / DNL / INL / EOT / EOB) + §1.2 特性 (12-bit / 1MS/s / 8 单端通道) + 电气总表 **SARADC_AVDD1V8 = 1.62/1.8/1.98 V** · ★**[实测]** `FET3572C_PIN_TABLE.csv` L39 · 网表/脚表/BOM 全部行号与逐字 · `gen_netlist.py` BAT_DET 段 · ★**[推算]** 2.100V / 1.575V / 1.595V / 利用率 / ΔQ 估算 / 漏电 · ★**[0数据]** SoM SAR-ADC 的输入电容 Cin / 采样保持时间 / **模块自身 abs-max** (★这一条现在是"不阻塞"项, 因为芯片级已判死★)。

---

### ★★第 (4) 条 ★★ BAT_DET 分压链漏电预算 (★ISS-211 U-4★) ★★

#### ① 现状 (★逐字原文 + 行号★)

★**表A L182 的 note 逐字**:
> `[R_BAT_DET_1] ★DNP: 同上 (电池电压分压上臂) | [BAT_DET_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 BAT 已归一到源节点]`

★**现值 1M+1M 的真值漏电 (本单自己算)**:
| 电池电压 | 漏电 (1M+1M) | 漏电功耗 |
|---|---|---|
| 3.0V (C-03 截止) | 1.50µA | 4.5µW |
| 3.7V (标称) | 1.85µA | 6.8µW |
| ★**4.2V (C-03 满充)** ★ | ★**2.10µA** ★ | ★**8.82µW** ★ |
| 5.0V (note 自称的口径) | ★**2.50µA** ★ | 12.5µW |

⇒ ★**note 里的 "~1.65µA @5V" 与自己的 1M+1M 对不上**: ★**1.65µA 正好是 3.3V/2MΩ 的值 (⇒ 标签 @5V 写错了, 或者值按 @3.3V 算的)** ⇒ ★**真值 @5V = 2.50µA ⇒ 差 1.52× ⇒ 按 1.65µA 做预算会低估 34%**。

#### ② 问题 (★可判定依据★)

★**"漏电流"这个数在自己的同一行里就是错的** ⇒ ★**它是本项目里少见的"算术当场可判"的缺陷** ⇒ ★**门禁把它做成了机器判据 (`calc(leak_ua@4.2)` vs `calc(leak_note_ua@5)`, 两条都钉在现行值上)★** ★⇒ ★**改坏任何一个 ⇒ 门禁变红★**。

#### ③ 根因 (★追到源头★)

★**同一条 `add(...)` 的 `note` 是手写文案, 不与 `value` 联动** ⇒ ★**"值改了, 文案没改"的老病 (与第 (1)(2) 条同型)** ⇒ ★**★解法不是"再手写一次对的数", 是"让门禁把两个数对上"★** (★⇒ 本条的唯一硬修法 = 门禁判据 + 落表那趟把 note 里的数改成由 value 推导的数★)。

#### ④ 目标取值或判据 (★漏电 vs 待机功耗/续航 (★老板关注 ≥1h★) 的量化★)

★**整机侧的口径 (★项目库现值★)**:
| 项 | 值 | 出处 |
|---|---|---|
| ★**待机功耗 (全下电深睡)** ★ | ★**0.03 ~ 0.06 W (地板 0.05 W)** ★ | ★`HW/POWER_BUDGET_V3.md` §5 "B: 全下电深睡 … 这才是 MECH §2.3.1 第 1 条『待机 <0.05W』的口径" ★ |
| ★**电池 1h 容量换算** ★ | ★**`mAh = P[W] × 1h ÷ 3.7V ÷ 0.83 (充电效率) ÷ 0.9 (DoD) × 1000` = `P × 361.81`** ★ | ★`HW/POWER_BUDGET_V3.md` §5.1 ★ |
| ★**电池 (有桥 = 充电板在镜框)** ★ | ★**丰江 432243 3.7V ≥420mAh** ★ (无桥 = Renata ICP582035PR-01 340mAh) ★ | ★`HW/INTERFACE_TABLE.md` C-02 / `POWER_BUDGET_V3.md` §7 ★ |

★**分压链的功耗与占比 (本单自己算)**:
| 分压比 | 漏电@4.2V | 功耗@4.2V | 占待机地板 0.05W | 判定 |
|---|---|---|---|---|
| ★1M+1M (现值)★ | 2.10µA | 8.82µW | ★**0.018%** ★ | ★**完全不是约束★** ★ |
| 100k+100k | 21.0µA | 88.2µW | 0.18% | 仍不是约束 |
| 10k+10k | 210µA | 0.88mW | 1.76% | 开始进入 1% 线 |
| —— | —— | —— | —— | ★**判据: 分压链功耗 ≤ 待机预算的 1% (=0.5mW) ⇒ 上+下臂总阻 ≥ 35.3kΩ @4.2V** ★ |

★**★折中判据 (★硬件总工的取舍★)**:
1. ★**漏电预算 (≤1% 待机地板) ⇒ 总阻 ≥ 35.3kΩ** ⇒ ★**现值 2M 有 57× 余量; 推荐值 A (2.0M+1.2M = 3.2M) 有 91× 余量** ⇒ ★**⇒ 漏电在 3.2M 这一档上完全不是约束, 分压比只由"ADC 上限 + 12bit 利用率"两条决定** ★
2. ★**⇒ 所以 U-4 的答案是: "改小阻值"这个顾虑本身不成立; 真正该改的不是阻值大小, 是"1:1 这个比例"** ★(★⇒ 与第 (3) 条合起来: **A 方案把漏电降到 1.31µA, 比现值还低, 同时电压安全 ⇒ 漏电与利用率两个矛盾一次解掉**★)

★**★"不改会怎样" (★三条, 逐条说清★)**:
| 情形 | 后果 | 严重性 |
|---|---|---|
| ★**① 保持现状 (1M+1M 且全 DNP)** ★ | 分压链一颗都不装 ⇒ ★**漏电 = 0** ⇒ **漏电不是问题**; ★**但 SoM 的 ADC 脚读到的是浮空噪声 ⇒ 电池电量显示乱跳 / 关机判据误触发** ⇒ **这条的严重性全在"装不装", 不在"多大阻值"** ★ | ★**功能缺陷 (不是功耗缺陷)** ★ |
| ★**② 装上 1M+1M (照现值)** ★ | ★**2.100V 灌进 1.8V 域 ADC 脚 ⇒ 超 AVDD18 max 1.98V ⇒ 过压** ★ | ★**★P0 (烧脚)★** ★ |
| ★**③ 装上 2.0M+1.2M (推荐 A)** ★ | 1.595V (余量 0.205V) + 87.5% 利用率 + 1.31µA ⇒ **三个指标同时合格** ★ | ★**★通过★** ★ |

★**★降级方案 (★必须项★)**: ★**若落表那趟拿不到 SoM 手册 / 老板不想动阻值** ⇒ ★**直接用 D 档 (2.0M + 1.0M)**: 1.419V @4.2V (利用率 77.8%) + 漏电 1.40µA ⇒ ★**比 A 更保守, 但两个指标仍合格** ⇒ ★**⇒ 无论 A 还是 D, 都比现值好; 唯一不许做的是"照 1M+1M 装上去"★** ★。

#### ⑤ 该改哪张表的哪一行

- ★**同第 (3) 条的 `state/gen_netlist.py` BAT_DET 段 4 条 `add()`** (阻值/dnp/note 一起改)
- ★**★note 必须写成"由 value 推导出来的数", 且写清口径 (上臂+下臂总阻 / @4.2V)★** ⇒ 例: 「上臂 2.0M + 下臂 1.2M ⇒ 总阻 3.2M ⇒ 漏电 @4.2V = **1.31µA** (功耗 5.5µW = 待机地板 0.05W 的 0.011%)」
- ★**不许再出现 `~1.65µA @5V` 这种与 value 对不上的数** ⇒ ★**门禁 R8 就是这条的机器判据**

#### ⑥ 验收判据

- ★**门禁 R8 rc=0**: L182 的 note 里不再出现 `~1.65µA @5V`, 且 ★**note 自称的漏电流数 == 由 value 算出来的数 (误差 ≤0.1%)** ★
- ★**门禁 R7 rc=0**: 分压后 @4.2V 在 [1.2V, 1.8V] 区间内
- 整机待机功耗账里, 分压链功耗占位 ≤ 1% (落表那趟要写进 `HW/POWER_BUDGET_V3.md` 的待机口径)

#### ⑦ 证据等级

★**[实测]** L182 note 逐字 · BOM L86/L87/L27 · `POWER_BUDGET_V3.md` §5/§5.1/§7 逐字 · `INTERFACE_TABLE.md` C-02/C-03 · ★**[推算]** 全表漏电/功耗/占比/换算 · ★**[0数据]** 实测漏电流 (★无样件 ⇒ 本单实物 [实测] = 0 条★) · ★**★"1.65µA @5V" 的来源 (是 @3.3V 算的? 还是别的?) = [0数据] ⇒ 但结论不依赖它 (真值 2.50µA 由阻值直接算)★**。

---

### ★★第 (5) 条 ★★ USB D− 的 ESD 方案 + 型号判据 (★ISS-211 U-1 · ★第 1 轮已定位缺陷, 本轮补方案与选型判据★) ★★

#### ① 现状 (★第 1 轮已定位, 这里只列与"方案/型号"有关的原文 + ★本轮新补的证据★)

| 来源 | 逐字 |
|---|---|
| ★表A **L417** ★ | `P1,USB_D_P_SRC,D_ESD_USB_D,USB_D_P_SRC,D_ESD_USB_D,TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V),D,必装,[官方],,"[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**",A-24,MAIN_PCB,,TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)` |
| ★表A **L418** ★ | `P1,GND,D_ESD_USB_D,GND,D_ESD_USB_D,TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V),D,必装,[官方],,[D_ESD_USB_D] ESD 地端,A-24,MAIN_PCB,,TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)` |
| ★**板文件实测** ★ | `D_ESD_USB_D` **只有 2 个焊盘**; pad1 → `USB_D_P_SRC` (★串阻的 **SoM 侧**★), pad2 → `GND`; 封装原点 (94.95, 21.8); `J_USB_C` 原点 (140, 5.25) ⇒ ★**距离 47.99mm** ★ |
| ★**板上 ESD 位号统计** ★ | 4 个 (`D_ESD_CAM`/`D_ESD_DEMO`/`D_ESD_LIGHT`/`D_ESD_USB_D`); ★**挂 `USB_D_N_SRC` 或 `NET_USB_D_N_TYPEC` 的 = 0 个** ★ |
| ★**`state/gen_schematic_pages.py` P9 页 (★本轮新补的官方规矩锚★)** ★ | `④ **ESD 距连接器 ≤3.0mm** / CMC 距弯折起点 ≥5.0mm, 一律放 PCB 端, 不许上 FPC**` (★ISS-085 结构总工回, 2026-10-24 左右★) |
| ★**同页另一条** ★ | `① **不装共模扼流圈** (USB 2.0 眼图对共模转差分极敏感, 扼流圈会恶化眼图) → 只靠 **FPC 阻抗控制 + 两端 ESD**` |
| ★**`HW/EMC_PRECHECK.md:211`** ★ | `**USB 2.0 差分**: D+/D- 90 Ω 差分, 480 Mbps, …` ⇒ ★**USB 速率 = 480 Mbps (高速级)** ★ |

#### ② 问题 (★可判定依据★)

1. ★**D− (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 上 ESD 位号数 = 0** ⇒ ★**Type-C 入口只护了差分的一边** ★
2. ★**value 自称"USB 2.0 双通道" 而封装只有 2 焊盘** ⇒ **名不副实**
3. ★**位置错**: pad1 挂在 `USB_D_P_SRC` (★串阻的 **SoM 侧**★) ⇒ 真正贴连接器的是 `NET_USB_D_P_TYPEC`; ★**板面距 `J_USB_C` = 47.99mm ≫ 3.0mm** ⇒ ★**L417 note 自引的"紧贴 J_USB_C"被板文件证伪** ★
4. ★**★P9 页自己写的"两端 ESD"规矩也没做到** ⇒ ★**这不是"忘了", 是"规矩在、器件不在位"** ★

#### ③ 根因 (★追到源头★)

★**`state/gen_netlist.py` 的 USB ESD 段只定义了 1 只 2 脚件, 且挂在 SoM 侧** ⇒ ★**板侧的封装 (2 脚) 与布局 (47.99mm) 是同一个错误的下游** ⇒ ★**⇒ 真修法 = 改生成器 + 改板, 不许手改网表 CSV** ★(★同 ISS-211 第 (4) 条的定位★)。

#### ④ 目标取值或判据

★**① D− 到底需不需要单独的 ESD? ⇒ ★需要 (★自己查的官方口径★)** ★
- ★**[官网] ON Semi AND8074/D** 逐字: 「The USB Line termination is reached through the series resistors placed in the D+ and D− lines.」+「The STF202 ON Semiconductor device also provides ESD Protection to IEC6100-4-2 in both I/O data lines (D+ & D−) and in the voltage bus (VBUS).」⇒ ★**官方口径 = 两条数据线都要护** ★
- ★**[官网] TI TPD2EUSB30 datasheet (SLVSAC2G)** 的器件本身就是 **2-channel (D1+/D1−) 阵列** ⇒ ★**业界方案就是"一颗管两条线"** ★
- ★**[推算]** 差分对只护一边 ⇒ ① 抗扰不对称 (共模转差模时另一边没有钳位) ② 直接静电击穿路径就在 D− 上 ⇒ ★**Type-C 是频繁插拔口, 这是"用了就可能坏"的条目** ★

★**② 方案二选一 (★本单给方案 + 判据, 型号由老板拍★)** ★:

| 方案 | 做法 | 优点 | 代价 | 判定 |
|---|---|---|---|---|
| ★**① (★推荐★)** ★ | ★换 **3 脚双通道阵列封装** (pin1=D+ / pin2=D− / pin3=GND), 一颗管两条线 ★ | ★**不改网表拓扑**; 位置只需一个; 面积最小; ★**官方有现成件** ★ | ★**要改封装 (2 脚→3 脚) + 改位置 + 重跑布线** ★ | ★**★走这个★** ★ |
| ★**②** ★ | ★保留现有 2 脚件 + **另加一只 D− 件** ★ | ★不用改现有封装库 ★ | ★**要摆两个器件; 钳位电压/结电容要配对; 面积/布局改动更大** ★ | ★**不推荐** ★ |
| ★**③ (★可选扩展★)** ★ | ★用 **4 通道阵列** (D+ / D− / VBUS / 1 路备用) ⇒ 例如 TI **TPD4EUSB30** (DQA 2.5×1.0mm) ★ | ★**顺带护 VBUS 插拔尖峰** ★ | ★面积更大 ★ | ★**看 Type-C 入口还需不需要 VBUS 保护 (另议)★** ★ |

★**③ 型号判据 (★6 条, 缺一条不许选型★)** ★:

| # | 判据 | 门槛 | 官方对照 |
|---|---|---|---|
| ★**M1** ★ | ★**结电容 / 线** ★ | ★**≤ 1.0 pF/线** (★USB 2.0 高速 480Mbps 预算★) ★ | ★[官网] TI **TPD2EUSB30**: DRT **0.7 pF typ**; DQA 0.8 pF typ; IO-to-IO 0.05pF; 「The 0.7 pF (TPD2EUSB30/A typ) line capacitance supports data rates in excess of 5 Gbps.」★ |
| ★**M2** ★ | ★**钳位电压** ★ | ★**V_clamp ≤ 8V @ 1A**, 且 **< SoM USB PHY 的 abs-max** (★后者 [0数据] ⇒ 落板前用 SoM 手册核★) ★ | ★[官网] TPD2EUSB30: `Vclamp = 8 V @ IIO = 1 A` ★ |
| ★**M3** ★ | ★**IEC 61000-4-2 等级** ★ | ★**≥ level 4 contact (8kV) / air 8kV** ★ | ★[官网] TPD2EUSB30: 「IEC 61000-4-2 ESD protection (level 4 contact)」, contact 8kV / air 8kV (TPD4EUSB30 air 9kV) ★ |
| ★**M4** ★ | ★**封装** ★ | ★**3 脚单列 (SOT-3 / DRT 1.0×0.8mm 级)** ⇒ 一颗管两线 + 能贴 J_USB_C ★ | ★[官网] TPD2EUSB30 = SOT-3 (DRT, 1.00×0.80mm) ★ |
| ★**M5** ★ | ★**VRWM** ★ | ★**≥ 5.25V** (USB VBUS 5V 轨) ★ | ★[官网] TPD2EUSB30 的 I/O 侧按 3.3V 域; VBUS 侧另看 TPD4EUSB30 ★ |
| ★**M6** ★ | ★**位置** ★ | ★**到 `J_USB_C` 板面距离 ≤ 3.0mm** (★P9 页自引的 ISS-085 规矩★; ★**不是 ISS-211 §5.2 写的 5mm —— 本轮收紧到 3.0mm, 口径升级见 §13 附带发现 #3★) ★ | ★[实测] `gen_schematic_pages.py` P9 页逐字 ★ |

★**★★必须写进规格的"排除项" (★本轮新挖, 防止下一次又选错★)** ★:
⇒ ★**ON Semi STF202-22 这一类"滤波 + 端接 + ESD"三合一集成件, 在本项目里被明确排除** ★
- ★[官网] onsemi **STF202-22T1G** datasheet (Rev 11, 2025-03) 的 ELECTRICAL CHARACTERISTICS 逐字: `Typical Line Capacitance (pF) … **68**` (Measured at 25℃, f = 1 MHz, Pins 2/3/4/5 to GND)
- ★**68 pF 是 USB 【全速 12 Mbps】 级别的量级** ⇒ ★**用在本项目的 480 Mbps 高速差分线上会直接毁眼图** ⇒ ★**⇒ 选型时必须看 "线电容" 而不是只看 "IEC 等级"** ★
- ★★**但 STF202-22 的【内置串阻 RS = 20/22/24Ω】恰恰是第 (1) 条 USB 串阻取 22Ω 的官方旁证** ⇒ ★**⇒ 两个官方件指向同一个 22Ω, 但本项目不能用它的滤波部分** ★

★**★降级方案 (★查不到/选不到时的必填项★)** ★:
① ★**首选**: 用 §4-② 的**方案①** + ★**官网参数直接满足判据的替代型号** (TI TPD2EUSB30 及同级 ≤1pF 的 3 脚双通道阵列) ★
② ★**若 3 脚双通道件买不到**: 退成 **2 只单通道低电容 TVS** (各 ≤1pF) 分别贴 D+ 与 D− ⇒ ★**器件比双通道件好买, 代价是面积 + 要配对** ★
③ ★**无论哪条路, 必须把 ESD 从 `USB_D_P_SRC` (SoM 侧) 挪到 `NET_USB_D_P_TYPEC` / `NET_USB_D_N_TYPEC` (Type-C 侧)** ⇒ ★**否则等于没护 (这条是所有方案的共同底线)** ★
④ ★**绝不许的降级**: "先不加 ESD, 靠用户不碰" ⇒ ★**这是唯一一条"没有降级方案"的项, 因为 Type-C 插拔是日常动作** ★

#### ⑤ 该改哪张表的哪一行

| 步骤 | 改哪个文件 | 改什么 | 说明 |
|---|---|---|---|
| ★**5a** ★ | ★`state/gen_netlist.py` (USB ESD 段) ★ | ★`D_ESD_USB_D` 从"1 只 2 脚"改成 ★**3 脚 (D+ / D− / GND)** ★ | ★走方案①; 型号/封装由老板拍 (ISS-172 之外的选型) ★ |
| ★**5b** ★ | ★`state/gen_netlist_pins.py` ★ | ★脚表同步 (D_ESD_USB_D 从 2 脚 → 3 脚) ★ | ★★ |
| ★**5c** ★ | ★**板 (封装 + 位置)** ★ | ★封装 2 脚 → 3 脚; 位置挪到 `J_USB_C` 旁 (≤3.0mm) ★ | ★**★要重跑布线 ⇒ 必须并进"板只改一次"那一趟★** ★ |
| ★**5d** ★ | ★网表 value 列 + 板封装 Value 属性 ★ | ★`ESD 阵列 [待选型] (USB 2.0 双通道)` → ★`ESD 阵列 (USB 2.0 双通道, D+/D− 共用一颗, ≤1pF/线, IEC 61000-4-2 level 4)` ★ | ★不许留"名不副实"的字样 ★ |
| ★**5e** ★ | ★网表 note 列 (L417) ★ | ★"紧贴 J_USB_C" 只有在 5c 真做到时才留 ⇒ 落表后必须复量并写成实测值 ★ | ★★ |
| ★**5f** ★ | ★`state/gen_netlist.py` 的 `CHG_BOARD_REFS`/板生成器 (如涉及) ★ | — | ★本单不涉及 ★ |

#### ⑥ 验收判据

- 板上挂 `USB_D_N_SRC` **或** `NET_USB_D_N_TYPEC` 的 ESD 位号数 **≥ 1**
- `D_ESD_USB_D` 焊盘数 = **3**; pad net = (`NET_USB_D_P_TYPEC` / `NET_USB_D_N_TYPEC` / `GND`)
- `D_ESD_USB_D` → `J_USB_C` 板面距离 **≤ 3.0mm**
- value 不再自称"双通道"而封装不是双通道; 且 value 必须带结电容/等级判据串
- ★**门禁 R4 + R9 rc=0**

#### ⑦ 证据等级

★**[官网]** ON Semi AND8074/D (两条数据线都要护 / IEC 61000-4-2 等级表 / 钳位 8.70V@8kV接触, 10.60V@15kV空气) · onsemi **STF202-22T1G** datasheet (线电容 **68 pF** / 内置 RS 20-22-24Ω) · TI **TPD2EUSB30 / TPD2EUSB30A / TPD4EUSB30** datasheet SLVSAC2G (2ch/4ch / **0.7pF typ** / **level 4 contact 8kV** / **Vclamp 8V** / DRT 1.0×0.8mm) · ★**[实测]** 板文件焊盘/net/坐标/距离 47.99mm · 4 个 ESD 位号逐个查网 · P9 页规矩两条 · EMC_PRECHECK 的 480Mbps · ★**[推算]** 480Mbps 的电容预算 / 只护单边的后果 · ★**[0数据]** SoM USB PHY 的 abs-max 与 ESD 钳位需求 / 实际采购可得性。

---

### ★★第 (7) 条 ★★ CHARGE_BOARD_SPEC §2.4/§3.4: ★ICHG/IIN 系数方向反了 ⇒ 连带 390Ω 档的判据也不成立★ ★★

#### ① 现状 (★逐字原文 + 行号★)

★**`HW/CHARGE_BOARD_SPEC.md`**:

| 行 | 原文 (逐字) |
|---|---|
| ★**L320** | `> ★★★**方向修正 (ISS-214 d10 · ISS-220 落表 2026-11-16)**: buck 功率守恒 `VBUS·IIN·η = VBAT·ICHG` ⇒ `ICHG ≈ IIN × η × (VBUS / VBAT)`, 取 VBUS=5V, η=90% → **ICHG ≈ 1.216 × IIN** (VBAT=3.70V) / **1.071 × IIN** (VBAT=4.20V)。★**旧口径写的 (VBAT/VBUS)/η 是 1.216 的精确倒数 (方向反了; ★门禁 R10 要求本文件不再出现旧系数的字面值, 故不重复写出★) ⇒ 本节所有 ICHG 数与单 pin 数都必须按 1.216 重算★**。` |
| ★**L182** (表头) | `| `R_ILIM` | IINMAX (min/typ/max) | CC 段电池电流上限 (ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V**) | 铰链段实际载流 | 用途 |` |
| ★**L184** (390Ω 行) | `| **390Ω ±1%** | 0.82 / 0.91 / **1.00 A** | 0.67 / 0.75 / **0.82 A** | **~0.75 A** | ★★**本规格推荐值** (V1.9, 老板 10-28 拍板『边戴边充不允许』⇒ 皮肤温度不再是充电时硬约束 ⇒ 充电电流可提速; 单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×) |` |
| ★**L185** (300Ω 行) | `| 300Ω ±1% | 1.07 / 1.18 / 1.30 A | 0.88 / 0.97 / 1.07 A | ~1.0 A | ❌ **300Ω 档正式判死** (V1.9): 单 pin 0.534A > 任何 0.5mm pitch FPC ZIF 的 0.5A 触点天花板 (只能靠 1.0mm pitch, 而铰链区装不下) ⇒ **不可选** |` |
| ★**L186** (260Ω 行) | `| 260Ω ±1% | 1.23 / 1.37 / 1.50 A | 1.01 / 1.13 / 1.23 A | ~1.1 A | datasheet 官方示例值 (KILIM=390 max 时 1.5A) |` |
| ★**L711** (规格自带的自检脚本) | `    print(f"R_ILIM={r} -> IINMAX {lo:.2f}/{ty:.2f}/{hi:.2f} A -> ICHG@3.70V ~{lo*1.216:.2f}/{ty*1.216:.2f}/{hi*1.216:.2f} A"` |

★**表A `HW/netlist_v1.csv`**:

| 行 | 原文 (逐字, ★note 极长, 此处截断★) |
|---|---|
| ★**L47** | `P1,IINLIM,U_CHG pin10,R_ILIM,R_ILIM,390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A),R,必装,[官方],,"[IINLIM] ★★V1.7 按 ISS-091 结构核算定 **470Ω**: … ★★★**V1.8 改 (老板 10-28 拍板『边戴边充不允许』)**: … ⇒ **定为 390Ω (ICHG 0.82A, 充电 ~29min)**: 单 pin 0.411A ≤ 常见 0.5A 触点 (ISS-099 待查回规格), … ★★**ISS-099 结构侧选型回执 (10-28)**: ① **390Ω 档保留**, 但两道保险写死: **(a) 选型判据收紧到 单触点额定 ≥0.5A** (Hirose FH12-10S-0.5SH(55) 满足: 0.5A/触点 · 0.5mm pitch · 座高 2.0mm) **且 (b) 工况写明『只有 pin1/pin2 载流, 其余 ≤1mA』** …; ② **300Ω 档正式判死** (单 pin 0.534A > 任何 0.5mm pitch FPC ZIF 的 0.5A 额定天花板, 只能靠 1.0mm pitch 而铰链区装不下); …",C-01,CHG_BOARD,,` |
| ★**L48** | `P1,GND,R_ILIM,GND,R_ILIM,390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A),R,必装,[官方],,[IINLIM] 限流电阻 另一端接地 (IINLIM 对地设定输入电流上限),,CHG_BOARD,,` |
| ★**L497** | `P10,BAT_CHG,U_CHG pin14,J_CHG pin1,J_CHG,"1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)",CONN,必装,[推算],,"充电电流跨铰链: J_CHG pin1/pin2 双 pin 并联 (★每 pin ≤0.75A★); 铰链段不装 π 滤波 (会破坏 BQ25896 环路稳定性); 载流/压降/发热核算见 ISS-091 …",C-03,HINGE,,` |

★**BOM `HW/BOM_v1.csv` L97**: `R_ILIM,1,390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A),R,必装,镜框充电板,P1,[官方],…`

★**对照: MECH 侧的机器门禁已经按物理真值判 (★ISS-213 写的★)** ⇒ ★`MECH/check_demo_struct_truth.py` G2.8 逐字:
> `g("G2.8", "buck 功率守恒 ICHG/IIN = η·Vbus/Vbat (规格书的 0.822/0.933 是倒数)", …)`
> 锚点 `eta: 0.90` / `v_bus: 5.0` / `ratio_370: 1.216` / `ratio_420: 1.071` (★`MECH/HW_CROSS_REVIEW_TRIAGE.md` 的 `MECH_ANCHORS` 块★)

#### ② 问题 (★可判定依据★)

★**★同一件事, 两个文件是反的 ⇒ 而这一条直接决定 390Ω 档能不能定★** ★

1. ★**公式方向反了**: buck 转换器的功率守恒是 `VBUS·IIN·η = VBAT·ICHG` ⇒ **`ICHG/IIN = η·VBUS/VBAT`**; 规格书写的是 `ICHG/IIN = (VBAT/VBUS)/η` = **倒数** ⇒ ★**0.822 = 3.7/5/0.9 是 1.216 的精确倒数; 0.933 = 4.2/5/0.9 是 1.071 的精确倒数** ⇒ ★**数值本身对, 方向反了** ★
2. ★**⇒ 390Ω 档"单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×" 这个安全结论是假的** ⇒ ★**真值单 pin = 0.608A ⇒ 超 0.5A 触点额定 21.6%** ⇒ ★**⇒ 390Ω 档在真值下不满足项目自己写死的判据 (ISS-099 回执: 单触点额定 ≥0.5A)** ⇒ ★**★R_ILIM 档位不能定★** ★
3. ★**★而且同一个文件里两个数自己打架**: ★**L47 的 note 说触点天花板是 0.5A** (ISS-099 回执: FH12 **0.5A/触点**), ★**L497 的 note 却写 "每 pin ≤0.75A"** ⇒ ★**同一张网表两个触点额定** ⇒ ★**(0.75A 是连接器额定, 0.5A 是**降额后**的工作上限 ⇒ 落表时必须写清"额定 0.75A / 降额后工作上限 0.5A"★) ★
4. ★**L47 的 note 里还有一处历史残留**: 开头写「★★V1.7 按 ISS-091 结构核算定 **470Ω**」而 value 是 **390Ω** ⇒ ★**同一条 note 里两个档位** (★V1.8 改了档位但没删前一句★)。

#### ③ 根因 (★追到源头★)

★**根因 = `HW/CHARGE_BOARD_SPEC.md` §2.4/§3.4 的公式是手写推导, 没有引用 datasheet 的功率守恒与 η 的官方出处** ⇒ ★**⇒ 与 `MECH/check_demo_struct_truth.py` G2.8 (按物理真值判) 相反** ⇒ ★**⇒ 这是一个"跨文件同一件事两个口径"的经典 case: 两边都没错地各自"自洽", 但只有一边对** ★
★**根根根**: ★**§2.4/§3.4 的 ICHG/IIN 系数与 §5/§7 的连接清单、BOM/网表的 value 串, 全是手写的同一个数 0.822 ⇒ 改一处不会带动别处** ⇒ ★**⇒ 落表那趟必须一次改齐 §2.4 表 + §3.4 公式 + §3.4 六个场景行 + L711 自检脚本 + 网表 L47/L48 + BOM L97** ★。

#### ④ 目标取值或判据 (★用 BQ25896 datasheet 原文把方向定死★)

★**★[官网] TI BQ25896 datasheet (SLUSC76C — JULY 2015 – REVISED MAY 2018) 逐字★**:

| 出处 | 逐字 |
|---|---|
| ★特性首条★ | `High Efficiency 3-A, 1.5-MHz Switch Mode Buck Charge` — `– 92.5% Charge Efficiency at 2 A and 90.5% Charge Efficiency at 3 A Charge Current` |
| ★ILIM 脚 (Pin Description)★ | `ILIM pin sets the maximum input current limit by regulating the ILIM voltage at 0.8 V. A resistor is connected from ILIM pin to ground to set the maximum limit as **IINMAX = KILIM/RILIM**. The actual input current limit is the lower limit set by ILIM pin (when EN_ILIM bit is high) or IIINLIM register bits.` |
| ★KILIM 电气特性★ | `KILIM  IINMAX = KILIM/RILIM  (Input current regulation by ILIM pin = 1.5 A)  **320 / 355 / 390  A×Ω**` (min/typ/max) |

★**★⇒ 功率守恒 (buck): `VBUS·IIN·η = VBAT·ICHG` ⇒ `ICHG/IIN = η·VBUS/VBAT`★** ★
★**⇒ 真值 (η=0.90, VBUS=5.0V)★**:
| VBAT | ★真值 ICHG/IIN (η=0.90)★ | ★规格书的数 (倒数)★ |
|---|---|---|
| ★**3.70V** ★ | ★**1.2162** ★ | 0.8222 |
| ★**4.20V** ★ | ★**1.0714** ★ | 0.9333 |

★**★η 的取值理由 (★保守★)**: ★**官方给 92.5% @2A / 90.5% @3A ⇒ 我们 1A 档的效率应 ≥92.5% ⇒ 取 η=0.90 是保守下限 ⇒ ⇒ 1.216/1.071 是**保守值, 真值只会更大 ⇒ 结论方向不变 (只会更超)**** ★

★**★连带重算: 390Ω 档的单 pin 载流 vs 0.5A 触点额定 (★J_CHG pin1/pin2 双 pin 并联★)** ★:

| 量 | ★规格书口径 (错)★ | ★真值 (η=0.90)★ | 判定 |
|---|---|---|---|
| IINMAX (min/typ/max) | 0.82 / 0.91 / **1.00** A | ★**同 (KILIM 官方, 不受方向影响)** ★ | —— |
| ICHG @VBAT=3.70V | 0.67 / 0.75 / **0.82 A** | ★**0.997 / 1.107 / 1.216 A** ★ | —— |
| ICHG @VBAT=4.20V | 0.69 / 0.77 / **0.93 A** | ★**0.879 / 0.975 / 1.071 A** ★ | —— |
| ★**单 pin @3.70V (max 档)** ★ | 0.411A ✅ | ★**0.608A** ★ | ★**❌ 超 0.5A 触点额定 21.6%★** ★ |
| ★**单 pin @4.20V (max 档)** ★ | 0.467A ✅ | ★**0.536A** ★ | ★**❌ 超 7.1%★** ★ |
| 300Ω 档单 pin @3.70V | 0.534A ❌ | ★**0.791A** ❌❌ | ★**死得更彻底** ★ |
| 260Ω 档单 pin @3.70V | 0.615A ❌ | ★**0.912A** ❌❌ | ★**❌❌** ★ |

★**★⇒ R_ILIM 档位的三个可选解 (★本单只列 + 给判据, ★不替老板拍★)** ★:

| 解 | 做法 | 单 pin @3.70V (max 档) | 余量 | 代价 |
|---|---|---|---|---|
| ★**解① (★硬件侧最省事★)** ★ | ★**R_ILIM 提到 475~510Ω** ★ | ★**475Ω ⇒ 0.499A**(余 0.2%, 太贴) · **487Ω ⇒ 0.487A**(余 2.6%) · **510Ω ⇒ 0.465A**(余 7.0%) ★ | ★**≥0.5A** ★ | ★**充电慢 ~30%** (ICHG 从 1.216A 降到 ~0.93A) ★ |
| ★**解② (★保住 390Ω 与充电速度★)** ★ | ★**J_CHG 载流 pin 从 2 只加到 4 只 (pin1/2/9/10)** ★ | ★**1.216/4 = 0.304A** ★ | ★**余 39%** ★ | ★**★J_CHG pinmap 要改 (pin9/10 现为"预留 (不装)"; I2C 上拉已移到充电板所以空着) ⇒ ★这是 ISS-199/ISS-202 的地界, 要 mech-lead + main 排期★** ★ |
| ★**解③** ★ | ★换 1A/触点的连接器 ★ | 0.608A ≤ 1A ✅ | —— | ★**❌ 判死 (ISS-099 已写: 铰链区装不下 1.0mm pitch / 1A 触点的 ZIF)★** ★ |
| ★**解④** ★ | ★降低充电电流目标 (不装/改 ILIM 之外再加软件限流) ★ | —— | —— | ★**不可行: IINLIM 复位默认 2048mA 是硬件行为, 必须靠 R_ILIM 压住 (R-1)★** ★ |

★**★⇒ 必须选解① 或 解② ⇒ 这是老板级 (充电时间 vs 连接器 pinmap) ⇒ 登记 need 给 main★** ★

#### ⑤ 该改哪张表的哪一行 (★只出规格, ★本单不许改那个文件★)

| 位置 | 从 | 到 |
|---|---|---|
| ★**`HW/CHARGE_BOARD_SPEC.md` L182** (表头) ★ | `CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822)` | ★`CC 段电池电流上限 (ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V**)` ★ |
| ★**同 L184** (390Ω 行) ★ | `0.67 / 0.75 / **0.82 A**` + `单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×` | ★`**0.997 / 1.107 / 1.216 A**` + `单 pin **0.499-0.608A**` ★(★"≤0.5A, 余量 1.22×" 必须删★) ★ |
| ★**同 L185** (300Ω 行) ★ | `0.88 / 0.97 / 1.07 A` + `单 pin 0.534A` | ★`**1.298 / 1.437 / 1.581 A**` + `单 pin **0.791A**` ★ |
| ★**同 L186** (260Ω 行) ★ | `1.01 / 1.13 / 1.23 A` | ★`**1.496 / 1.657 / 1.824 A**` + `单 pin **0.912A**` ★ |
| ★**同 L184 的"用途"栏** ★ | `★★**本规格推荐值**` | ★`★★**待裁决: 475~510Ω (解①) 或 390Ω + J_CHG 4 pin 并联 (解②)★★` ★ |
| ★**同 L320** (§3.4 公式) ★ | `ICHG ≈ IIN × (VBAT / VBUS) / η` … `ICHG ≈ 0.822 × IIN` | ★`**ICHG ≈ IIN × η × (VBUS / VBAT)**` … `ICHG ≈ **1.216 × IIN** @3.70V / **1.071 × IIN** @4.20V` ★ |
| ★**§3.4 六个场景行** ★ | "铰链段 ICHG" 列全部重算; 结论 2 的 `余量从 3.7× 缩到 1.4×` | ★场景① `~0.41 A` → **`~0.61 A` (余量 3.7× → 2.47×)**; 场景③ `~0.67-0.82 A` → **`~1.00-1.22 A`** (余量 1.4× → **1.23×**); 场景⑤ 300Ω → **`~1.30-1.58 A`**; 场景④ 260Ω → **`~1.50-1.82 A`** ★ |
| ★**同 L711** (自检脚本) ★ | `lo*0.822` | ★`lo*1.216` (★并按 VBAT 分别取 1.216 / 1.071★) ★ |
| ★**表A L47 / L48 value** ★ | `390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)` | ★**按最终档位重写** (★例: `475Ω ±1% (IINMAX 0.67-0.82A · ICHG 0.82-0.999A · 单 pin ≤0.50A)`★) ★ |
| ★**BOM L97 value** ★ | 同上网表串 | ★同上 (BOM 由生成器派生, 重跑即对) ★ |
| ★**表A L497 note** ★ | `每 pin ≤0.75A` | ★`每 pin **额定 0.75A / 降额后工作上限 0.50A** (ISS-099 FH12-10S-0.5SH(55)); 载流 pin = pin1/pin2 (或裁决后 pin1/2/9/10)` ★ |
| ★**表A L47 note** ★ | `★★V1.7 … 定 **470Ω**` (与 value 的 390Ω 打架) | ★**删掉 V1.7 那句** (或明确标"已作废") ★ |

#### ⑥ 验收判据

- ★**门禁 R10 rc=0**: `CHARGE_BOARD_SPEC.md` **不再含 `0.822`** 且 **含 `1.216` 与 `1.071`**; 表A R_ILIM 的 value **不再含 `0.411A`**; ★**且 `calc(ichg_pin_max@3.7) ≤ 0.5A`** (★门禁已实装这条★)
- L497 的 note 不再出现孤零零的 `每 pin ≤0.75A` (必须写清"额定 vs 工作上限")
- L47 的 note 里 V1.7 的 470Ω 残留句已删/已标作废
- ★**MECH 侧 G2.8 与 CHARGE_BOARD_SPEC 逐字一致** (★两边口径必须能互查★)

#### ⑦ 证据等级

★**[官网]** TI BQ25896 datasheet SLUSC76C (效率 92.5%/90.5% / ILIM 的 `IINMAX = KILIM/RILIM` 原文 / KILIM 320-355-390 AΩ) · ★**[实测]** CHARGE_BOARD_SPEC L182/L184/L185/L186/L320/L711 逐字 · 网表 L47/L48/L497 逐字 · BOM L97 · `MECH/check_demo_struct_truth.py` G2.8 + `MECH/HW_CROSS_REVIEW_TRIAGE.md` 的 `MECH_ANCHORS` (eta/v_bus/ratio_370/ratio_420) · ★**[推算]** 功率守恒与全表重算 · ★**[0数据]** 铰链段实际接触电阻/温升实测 (无样件) / SoM 手册与 JBD 无关项。

---

### ★★第 (8) 条 ★★ NET-LED / board 列: ★★"转述 vs 实测"不一致 + 真缺陷在 `C_VBUS_GND`★★ ★★

#### ① 现状 (★★转述 vs 实测逐条对照表 —— ★这是本条的第一义★★)

★**转述来源**:
- mech-lead (ISS-213) 的 need 原话: 「**网表 board 列标错 —— R_CHG_LED 两端分别标 CHG_BOARD 与 MAIN_PCB**」
- main (2026-11-16 00:1x) 的实跑转述: 「net `VBUS_5V_CHG` 上, L11 `C_VBUS_OUT` 的 board = `CHG_BOARD`, 而 L12 `C_VBUS_GND` 的 board = `MAIN_PCB` ⇒ **同一颗 VBUS 电容的两端分属两块板**」

★**★我自己的实跑 (2026-11-16 00:4x~00:5x, 逐字实读)★**:

| # | 转述的说法 | ★**我的实跑** ★ | 判定 |
|---|---|---|---|
| ★**T1** ★ | 「`R_CHG_LED` **两端**分别标 `CHG_BOARD` 与 `MAIN_PCB`」 ★ | ★**表A L508 / L509 两行 `R_CHG_LED` 的 board (第 13 列) 全部 = `CHG_BOARD`** ★ ⇒ 且 L510 (`D_CHG_LED`) / L511 (`Q_CHG_LED`) 的 board 也都是 `CHG_BOARD` ⇒ ★**整条充电灯链全在 CHG_BOARD, 与该行 note「装在充电板 (镜框) 靠近 Type-C 座」完全一致** ★ | ★**★转述的这半句【不成立】★** ★ |
| ★**T2** ★ | 「net `VBUS_5V_CHG` 上, L11 `C_VBUS_OUT` board=CHG_BOARD, L12 `C_VBUS_GND` board=MAIN_PCB」 ★ | ★**完全一致 (行号与 board 值都对)** ★ | ★**★main 的实跑是对的★** ★ |
| ★**T3** ★ | 「**同一颗** VBUS 电容的两端分属两块板」 ★ | ★**不准确** ★ ⇒ ★**`C_VBUS_OUT` 与 `C_VBUS_GND` 是【两颗不同的电容】, 不是一颗的两端** ★ ⇒ ★**`C_VBUS_OUT` 的两端 = `VBUS_5V_F1` (L9) + `VBUS_5V_CHG` (L11); `C_VBUS_GND` 的两端 = `GND` (L10) + `VBUS_5V_CHG` (L12)** ★ | ★**★描述不准 (但指向的网是对的)★** ★ |

★**★⇒ 转述 vs 实测的结论 (★写进规格的证据栏, 这正是本项目反复吃过亏的地方★)** ★:
★**① 别人的转述不能当事实用 (T1 直接被证伪)** ⇒ ★**⇒ 落表时必须按【本单实跑】的行号与 board 值改, 不按转述改** ★
★**② main 的实跑是可靠的 (T2 全对)** ⇒ ★**⇒ 可以直接用, 但仍要自己复核一遍 (本单已复核)** ★
★**③ 转述里唯一"错得让人差点改错东西"的半句是 T1** ⇒ ★**★如果照 T1 去改, 会去动一个根本没坏的 `R_CHG_LED` (把 CHG_BOARD 改成 MAIN_PCB 才是真的改坏)★** ★

★**★实跑后的真定性 (★main 的转述指向的网是对的, 但"真缺陷"要说准★)** ★:
★**net `VBUS_5V_CHG` 上并着三行, board 列出现两档** ★:

| 行 | net | ref | board | dnp | value |
|---|---|---|---|---|---|
| ★**L11** | VBUS_5V_CHG | `C_VBUS_OUT` | **CHG_BOARD** | DNP | `[待选型] 100µF` |
| ★**L12** | VBUS_5V_CHG | `C_VBUS_GND` | ★**CHG_BOARD** ★ (★2026-11-16 ISS-220 落表后★) | DNP | `[待选型] 100µF` |
| ★**L13** | VBUS_5V_CHG | `U_CHG` | **CHG_BOARD** | 必装 | `BQ25896` |

★**⇒ 真缺陷 = π 滤波的【对地电容】被分到了另一块板上** (★不是"一颗电容的两端", 是"同一张网的两颗器件挂到两块板"★)

★**脚表同步实跑**: ★**L148/L149** (`C_VBUS_GND.1/.2`) board = ★**CHG_BOARD**★ (★2026-11-16 ISS-220 落表后★); ★**L154/L155** (`C_VBUS_OUT.1/.2`) board = `CHG_BOARD` ⇒ ★**落表后两处一致 (不是单边漂移)** ★

★**★板文件实跑 (★关键: 这不是板画错, 是网表 board 列错★)**:
- `C_VBUS_GND` 的封装 **确实在** demo 主 PCB 里 (2 焊盘; pad1 → `GND`, pad2 → `VBUS_5V_CHG`) ⇒ **与 board 列自洽**
- `C_VBUS_OUT` 在 demo 主 PCB 里 **没有**封装 (`count_footprint(C_VBUS_OUT) == 0`) ⇒ **与 board 列自洽** (它在充电板上)
- ★**挂 `VBUS_5V_CHG` 的封装只有 `C_VBUS_GND` 一个**; `J_CHG` 的焊盘只有 pin1=`BAT_CHG` / pin6=`PWR_GOOD` ⇒ ★**★这张网从主板到充电板没有物理通路 ⇒ 主板这半边是一颗 DNP 电容的一只脚 = 死头支路★** ★

#### ② 问题 (★可判定依据★)

1. ★**同一张充电板本地的网 (BQ25896 的 VIN), 里面那颗 π 滤波的对地电容被分到了另一块板** ⇒ ★**★充电 IC 的输入去耦被甩到另一块板上★** ⇒ ★**[官网] BQ25896 原文: 「Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC」** (★`HW/CHARGE_BOARD_SPEC.md` L115 已逐字引用★) ⇒ ★**⇒ 输入回路跨板 = 去耦失效 + EMC 风险** ★
2. ★**网表上"接上了", 板上是死头** ⇒ ★**网表与板打架 (同型缺陷)**
3. ★**board 列不是逐行手写的, 是生成器白名单驱动** ⇒ ★**漏一颗就默认落到 MAIN_PCB** ⇒ ★**这是"结构性"缺陷, 一次修好必须修白名单, 不许只改这一颗的网表行** ★

#### ③ 根因 (★追到源头, ★★这一段是本单最硬的根因链★)

★**`state/gen_netlist.py`**:
```python
CHG_BOARD_REFS = {
    "D_CHG_LED", "Q_CHG_LED", "R_CHG_LED", "C_REGN", "R_ILIM",
    "J_TYPE_C", "D_ESD_TC", "FB_VBUS", "C_VBUS_IN", "C_VBUS_OUT", "U_CHG",
    ...
    # ★它发现的缺陷: VBUS_DET 的 1M+1M 分压物理上必须在**充电板**
    #   (充电板 VBUS 不过铰链到主板 · 分压放在主板 = 采不到电)
    "R_VBUS_DET_1", "R_VBUS_DET_2",
}
```
```python
def board_for(r: dict) -> str:
    if ref in HINGE_REFS:            return BOARD_HINGE
    if ref in CHG_BOARD_REFS:        return BOARD_CHG
    if ref.startswith("RAIL_") or ref.startswith("NET_"): …  # 特判
    return BOARD_MAIN               # ★★其余一律落到主板★★
```
⇒ ★**`C_VBUS_GND` 不在白名单 ⇒ 落进默认分支 ⇒ `MAIN_PCB`** ★

★**★铁证 (★本单新挖★): 同一个白名单里的注释自己写着「★它发现的缺陷: VBUS_DET 的 1M+1M 分压物理上必须在充电板 (充电板 VBUS 不过铰链到主板 · 分压放在主板 = 采不到电)」⇒ ★★同一个类型的坑 (`R_VBUS_DET_1/2`) 已经被发现并修过一次 (加进了白名单), 而 `C_VBUS_GND` 是同一个坑的漏网之鱼 ⇒ ★★这不是"没人注意", 是"修的时候只修了两只电阻, 漏了旁边那颗电容" ⇒ ★★⇒ 同型缺陷还在往外冒的铁证★★** ★

#### ④ 目标取值或判据

- ★**目标: `C_VBUS_GND` 的 board = `CHG_BOARD`** (★与 `C_VBUS_OUT` / `C_VBUS_IC` / `U_CHG` 同板★)
- ★**★通用判据 (可机器判, ★本单新增门禁 R11★)★**: ★**凡出现在 `NET_VBUS_5V_CHG` / `VBUS_5V_CHG` / `VBUS_5V_F1` / `VBUS_5V_ESD` 这些"充电板本地网"上的器件, board 列必须 = `CHG_BOARD`** ⇒ ★**落表那趟必须复跑这条** ★
- ★**★通用根因判据 (★比逐颗改更值钱★)★**: ★**充电链的 board 列是【白名单驱动】⇒ 白名单每加一颗新件, 都可能漏 ⇒ 落表那趟必须把 `CHG_BOARD_REFS` 与 `HW/CHARGE_BOARD_SPEC.md` §7 的连接清单做一次【双向对账】: §7 清单里的每一行都必须 board=CHG_BOARD, 且网表里 board=CHG_BOARD 的每一颗都必须在 §7 清单里** ★
- ★**★降级方案 (★必须项★)**: ★**若落表那趟来不及重出充电板 ⇒ 那就把 `C_VBUS_GND` 从网表里删掉** (它在 demo 阶段本来就是 DNP, 充电板整机阶段才装) ⇒ ★**少一颗 DNP 件, 好过把它放错板** ⇒ ★**但这是降级方案, 不是目标状态** ★
- ★**★不许的做法**: ★**只改 `HW/netlist_v1.csv` 的 board 列** ⇒ ★**重跑 `state/gen_netlist.py` 就会被打回 MAIN_PCB** (★"改在产物上"的老毛病★)

#### ⑤ 该改哪张表的哪一行

| 步骤 | 改哪个文件 | 改什么 | 说明 |
|---|---|---|---|
| ★**8a** ★ | ★`state/gen_netlist.py` 的 `CHG_BOARD_REFS` (★现 L120-133★) ★ | ★加 `"C_VBUS_GND"` ★ | ★**★本单不许改生成器 ⇒ 归"整链重出 第 1 步"那一趟★** ★ |
| ★**8b** ★ | ★`state/gen_netlist.py` (USB/充电链段) ★ | ★★**顺带把 `CHG_BOARD_REFS` 与 §7 连接清单做双向对账** ★ | ★★根因级修法 ★ |
| ★**8c** ★ | ★`state/gen_netlist_pins.py` ★ | ★脚表 board 列自动跟随 (★它按网表的 board 派生★) ★ | ★★ |
| ★**8d** ★ | ★**板** ★ | ★`C_VBUS_GND` 的封装会从 demo 主 PCB 上**消失** (板生成器按 board 列过滤) ⇒ ★**★板会改 ⇒ 必须并进"板只改一次"那一趟★** ★ | ★★ |
| ★**8e** ★ | ★`HW/netlist_v1.csv` L10 / L12 的 board 列 ★ | ★`MAIN_PCB` → `CHG_BOARD` ★ | ★**★由重跑生成器自动来, 不许手改★** ★ |

#### ⑥ 验收判据

- net `VBUS_5V_CHG` / `VBUS_5V_F1` 的**所有行**的 board 列 = `CHG_BOARD` (表A + 脚表)
- `C_VBUS_GND` 的 board = `CHG_BOARD` (表A L10/L12 + 脚表 L148/L149)
- 板文件: `count_footprint(C_VBUS_OUT) == 0` 且 `count_footprint(C_VBUS_GND) == 0` (两颗都上了充电板)
- ★**门禁 R11 rc=0**

#### ⑦ 证据等级

★**[实测]** 表A L9-L13 / L508-L511 逐字 · 脚表 L148/L149/L154/L155 逐字 · 板文件封装清单 (186 个) 与 pad→net · `J_CHG` 焊盘只有 pin1/pin6 · `gen_netlist.py` 的 `CHG_BOARD_REFS` 与 `board_for()` 源码与注释逐字 · ★**[官网]** BQ25896 "Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC" (★`CHARGE_BOARD_SPEC.md` L115 已逐字引用★) · ★**[推算]** "跨板去耦"的后果 / "死头支路" · ★**[0数据]** 充电板实物 (整机阶段才有) / 跨板回流路径的实际寄生。

---

## 11. ★★第 2 轮的附带发现 (★不属本节 8 条, 只登记待判★) ★★

★**#1 · `imp` 一个字段同时服务两种物理量 (★第 (1) 条的根根根★)** ⇒ ★**同一张网表里, NET 行的"阻抗"和器件行的"阻值"在 DSI 组是**两个不同的物理量** (NET 行 100Ω = MIPI 差分阻抗; 器件行 0Ω = 直通位), 在 USB 组却被塞进同一个字段 ⇒ ⇒ **SPEC.json 模板要分字段 (`imp` = 串阻值 / 另设 `z_diff` = 差分阻抗), 不许一个 `imp` 混着用** ⇒ 已并进第 (1) 条的 ①/③。

★**#2 · `R_BAT_DET_1` note 的漏电流数与自己的阻值对不上** ⇒ 已并进第 (4) 条。

★**#3 · ★ESD 位置判据从 5mm 收紧到 3.0mm (★口径升级, 要知会 main★)** ⇒ ISS-211 §5.2 / 第 (4) 条 3j 写的是「到 `J_USB_C` 的板面距离 **≤ 5 mm**」, ★**而 `state/gen_schematic_pages.py` P9 页自己引的 ISS-085 结构总工回执写的是「ESD 距连接器 **≤3.0mm**」** ⇒ ★**⇒ 本轮按 3.0mm 判 (更严, 且是项目自己的规矩)** ⇒ ★**门禁 R9 已实装 3.0mm?** ⇒ ★**★注意: 本单实现的是 `calc(esd_dist_usb) > 5` 的【现状断言】(缺陷仍在, 47.99mm ⇒ 断言成立) ⇒ 落表后的翻面判据 R9 用的是 **≤ 5mm** (★与 ISS-211 一致★) ⇒ ★**★⇒ 落表那趟必须把 R9 的阈值从 5.0 改成 3.0, 这是本单留下的一个【口径待收口】项, 已登记 need** ★

★**#4 · `J_CHG` 在网表与板文件里指两个不同的物理件** ⇒ ★**网表: 铰链 FPC 座 `1×10p@0.5mm` (board=HINGE); 板文件: `SoM BTB CHG (100pin, 部分已分配)`, 只有 2 个焊盘 (pin1=`BAT_CHG` / pin6=`PWR_GOOD`)** ⇒ ★**⇒ P9 页的 J_CHG pin map (5=CHG_STAT / 6=PWR_GOOD / 7=VBUS_DET) 也与网表对不上 (网表: 7=`NC` / 8=`TS_BAT`, 且没有 5/6 的行)** ⇒ ★**归 ISS-199 / ISS-202 的地界, 本单只登记不落表**。

★**#5 · 充电链的 board 列是白名单驱动 ⇒ 白名单漏一颗 = 默认落 MAIN_PCB** ⇒ 已并进第 (8) 条的 ④ 通用根因判据。

★**#6 · `C_VBUS_OUT` 在网表里是【串联】在 BQ25896 的 DC 输入路径上的 100µF, 而 `CHARGE_BOARD_SPEC.md` §7 (L516) 的 `C_VBUS_BULK` 是【对地】100µF** ⇒ ★**规格 §7 与网表的 π 滤波拓扑/位号都不一致; 且 §7.1 计数对账表里的"现行网表引用 80 行"也已经过期** ⇒ ★**另: 100µF 串联在充电 IC 的 DC 输入路径上 ⇒ 稳态充不了电** ⇒ ★**★这是充电板 (整机阶段) 的 P0, 但充电板不进 demo 板 ⇒ 不在本单 8 条内 ⇒ 登记 need 给 main** ★

★**#7 · `R_CHG_LED` 的转述与实跑不一致 (★第 (8) 条的第一义, 单列出来是因为"转述不能当事实"是本项目反复吃过亏的地方★)** ⇒ 详见第 (8) 条 ① 的对照表。

★**#8 · `R_ILIM` note 里的 V1.7 残留 "470Ω" 与 value 的 390Ω 打架** ⇒ 已并进第 (7) 条 ⑤。

---

## 12. ★★第 2 轮的证据分级汇总 (★按本项目标签口径★) ★★

| 等级 | 条目 |
|---|---|
| ★**[实测]** ★ | ★8 条的全部行号与逐字原文 (表A/表B/BOM/脚表) · `SCHEMATIC_V1_SPEC.json` connections[40]/[41] 全文 · `HW/PCB/FET3572C_PIN_TABLE.csv` L39 · `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` (由项目库内官方 PDF 抽取) · `HW/EMC_PRECHECK.md:211` · `state/gen_schematic_pages.py:147` 与 P9 页其余逐字 · `state/gen_netlist.py` 的 `CHG_BOARD_REFS` / `board_for()` / `conn_row()` / `HINGE_REFS` 注释 · `HW/CHARGE_BOARD_SPEC.md` L182/L184/L185/L186/L320/L711 · `MECH/check_demo_struct_truth.py` G2.8 + `MECH/HW_CROSS_REVIEW_TRIAGE.md` 的 `MECH_ANCHORS` · `MECH/cross_review_check.py:64` · `DECISIONS.md` (2026-10-27) · `HW/POWER_BUDGET_V3.md` §5/§5.1/§7 · `HW/INTERFACE_TABLE.md` C-02/C-03 · 板文件 186 个封装的 pad→net 统计与坐标 · ★**门禁 154 条锚点全绿 (本机脚本实测)** ★ |
| ★**[官网]** ★ | ★RK3572 Datasheet Rev 1.1 §3.10 **Table 3-16 (p.45-46)** + 电气总表 `SARADC_AVDD1V8 = 1.62/1.8/1.98 V` + §1.2 SARADC 特性 · ★TI **BQ25896** datasheet **SLUSC76C** (效率 92.5%/90.5%、ILIM 的 `IINMAX = KILIM/RILIM`、KILIM 320/355/390 AΩ) · ★ON Semi **AND8074/D** (USB 1.1 串阻 28~44Ω 规范 / 22Ω·30Ω 工业值 / Zo 90Ω±15% / IEC 61000-4-2 等级表 / 钳位 8.70V@8kV 接触) · ★onsemi **STF202-22T1G** datasheet (线电容 **68 pF** / 内置 RS 20/22/24Ω) · ★TI **TPD2EUSB30 / TPD4EUSB30** datasheet **SLVSAC2G** (2ch/4ch / 0.7-0.8 pF / level 4 contact 8kV / Vclamp 8V / DRT 1.0×0.8mm) · ★Hirose **FH12-22S-0.5SH(55)** (官方 RPi CM5IO/Pi5 DISPLAY 座封装, 网表与 BOM 自引抄用) · ★Hirose **FH12-10S-0.5SH(55)** 0.5A/触点 (ISS-099 回执自引) ★ |
| ★**[推算]** ★ | ★"90Ω 串阻 ⇒ 摆幅减半" · ★"1:1 分压 2.100V > AVDD18 max 1.98V" · ★分压比候选全表 (1.575V/1.595V/1.508V/1.558V/1.700V/1.749V/1.400V/1.419V) 与利用率 · ★ΔQ ≈ 2.2pC ⇒ 1MΩ 上 ≈0.44mV ≈ 1 LSB · ★漏电/功耗/占待机比例 (8.82µW ⇒ 0.018%) 与容量换算 P×361.81 · ★ICHG/IIN 全表重算 (0.997/1.107/1.216 / 0.879/0.975/1.071 / 单 pin 0.608/0.536/0.791/0.912) · ★解① 的 475/487/510Ω 单 pin 值 · ★η=0.90 的保守性论证 (官方 92.5%@2A) · ★26.5/27.00/35.50 三个数对应的物理模型 · ★"跨板去耦"与"死头支路"的后果 ★ |
| ★**[0数据]** ★ | ★SoM (Forlinx) SAR-ADC 的输入电容 Cin / 采样保持时间 / 模块自身 abs-max (★芯片级已判死, 这一条现在【不阻塞】★) · ★SoM USB PHY 的驱动阻抗 / 外部串阻是否必需 / abs-max 钳位需求 · ★SoM USB 速率的官方确认 (★项目内 480Mbps 来自 EMC_PRECHECK, 不是 SoM 手册★) · ★ESD 型号的采购可得性与实际单价 (★零外发 ⇒ 未询价★) · ★J_CHG 铰链段实测接触电阻/温升/载流 (无样件) · ★铰链段实际堆叠与净高实测 (归结构) · ★BQ25896 的 IINMAX 实际值 (需板测) ★ |

★**★§5 边界声明 (★任务书要求逐条自查★)**:
★**本单 0 次外发** (未发任何邮件 / 询价 / 问询 / 采购; `state/outbox/` 一个字节没碰) · ★**本单实物 [实测] = 0 条** (板与屏不在本机) ⇒ ★**凡是标 [实测] 的, 一律是"本机脚本/本机文件实读", 不是"实物测过"; 凡是标 [推算] 的, 一律是纸上算的; 本单没有一次示波器/万用表/热像仪的实测** ★

---

## 13. ★★第 2 轮的未决项 (★need 一律 `to: main`★) ★★

| # | 未决 | 需要谁回答 | 卡住什么 | 截止口径 |
|---|---|---|---|---|
| ★**V-1** ★ | ★**【★2026-11-16 05:13 已由 main 裁 = 22Ω ⇒ 本条已关闭★】USB 串阻最终取 22Ω 外部串阻, 还是 0Ω (靠 SoM PHY 内部匹配)?** ★ | ★**main (★已裁★) · 残余只剩 SoM 手册核对驱动阻抗一条 (★[0数据] · 降级已按 22Ω 落★)** ★ | ★第 (1) 条的落表 (★**已落: ISS-223 第 2 批 05:13 ⇒ R5 全组 8 条清零★**) ★ | ★**已关闭 (2026-11-16 05:13)** ★ |
| ★**V-2** ★ | ★**ESD 方案二选一 (① 3 脚双通道阵列 / ② 2 只单通道) + 型号 (≤1pF/线 / Vclamp ≤8V / IEC level 4) + ★★D− 侧选型★★** ★ | ★**老板 (选型是老板级; 零外发 ⇒ 型号一律官网参数满足的替代件) ★** | ★**第 (5) 条的落表 (★它要改板 + 重跑布线★)** ★ | 第 1 步那一趟之前 |
| ★**V-3** ★ | ★**BAT_DET 分压比: 方案 A (2.0M+1.2M) 还是降级档 D (2.0M+1.0M)?** ★ | ★**老板 (★本单已把候选/判据/推荐给全, A 三个指标同时最优★)** ★ | 第 (3)(4) 条的落表 | 第 1 步那一趟之前 |
| ★**V-4** ★ | ★**R_ILIM 档位: 解① (475~510Ω, 充电慢 ~30%) 还是解② (390Ω + J_CHG 4 pin 并联, 要改 J_CHG pinmap)?** ★ | ★**老板 (★解③ 已判死; 解④ 不可行★)** ★ | ★**第 (7) 条的落表 (★`CHARGE_BOARD_SPEC.md` §2.4/§3.4 的推荐值栏写什么★)** ★ | ★**第 1 步那一趟之前 (★这条比别的都卡: 它决定 §2.4 表怎么写★)** ★ |
| ★**V-5** ★ | ★**堆叠账唯一口径: 本单建议 "FPC 带宽 35.50mm vs 锁死腔体净高 38.00mm"; ★但最终数字归 MECH + 项目总工★** ★ | ★**mech-lead + 项目总工 (★P9 页正文是 hw-lead 的地界, 数字不是★)** ★ | ★第 (2) 条的落表 (★P9 页不许再自带第二个堆叠数★) ★ | 第 1 步那一趟之前 |
| ★**V-6** ★ | ★**ESD 位置判据 5mm → 3.0mm 的口径收口 (★ISS-211 写的 5mm vs P9 页引的 ISS-085 的 3.0mm★)** ★ | ★**main (★机械侧规矩是 ISS-085, 门禁 R9 的翻面阈值本单实现的是 5.0mm ⇒ 落表那趟要改成 3.0★)** ★ | ★第 (5) 条的验收判据 | 落表那趟 |
| ★**V-7** ★ | ★**`C_VBUS_OUT` 串联在 BQ25896 的 DC 输入路径上 (整机阶段 P0) + `CHARGE_BOARD_SPEC.md` §7 的 `C_VBUS_BULK` 与网表对不上 (§11 附带发现 #6)** ★ | ★**main 派单 (★不在本单 8 条内★)** ★ | ★充电板整机阶段 (★不进 demo 板★) ★ | 整机阶段 |
| ★**V-8** ★ | ★**`J_CHG` 位号在网表 (铰链 FPC 10p) 与板文件 (SoM BTB 100pin) 里指两个物理件 (§11 附带发现 #4)** ★ | ★**main 派单 (★归 ISS-199/ISS-202 地界★)** ★ | ★铰链结构与 J_CHG pinmap ★ | 与 V-4 的解② 一起排 |

★**★零外发纪律 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)★**: ★**本单未发任何邮件 / 询价 / 问询 / 采购; `state/outbox/` 未碰** ⇒ ★**V-1/V-2/V-3/V-4 全部按"自己查资料 + 标证据等级 + 给判据 + 给降级方案"处理, ★**没有"批一句可以发"这个选项**★** ⇒ ★**查不到的地方一律标 [0数据] + 写降级方案, 不把外部依赖挂着当阻塞项** ★

---

## 14. ★★第 2 轮的边界自查 (★交卷时逐条自查过★) ★★

★**未碰**: ★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard.kicad_pro` · `HW/SCHEMATIC_V1_SPEC.json` · `HW/CHARGE_BOARD_SPEC.md` · `HW/EMC_PRECHECK.md` · `HW/RK3572_PIN_TABLE/*` · `HW/PCB/FET3572C_PIN_TABLE.csv` · ★`state/gen_netlist.py` · ★`state/gen_netlist_pins.py` · ★`state/gen_schematic_pages.py` · ★`state/gen_bom.py` · ★`state/gen_pcb_components.py` · ★`state/check_netlist.py` · ★`state/check_netlist_pins.py` · ★`state/issue_log.yaml` · ★`PROJECT_TRACKER.md` §0 · ★`state/outbox/` · ★`MECH/` 任何文件 · ★别人的分片 ★

★**只动**: ★`HW/NETLIST_SELF_CONSISTENCY_SPEC.md` (★扩写: §2 锚点表 64→**154 条** + 新增 §10~§14★) · ★`HW/check_netlist_selfconsistency.py` (★扩: 新增 5 个文件源 + 新判据类型 `text contains`/`calc(...)` + 新增 90 条锚点 + 新增 7 个反向用例 + R5~R11 翻面判据 + `_parse_res` 修 M/m 量级★) · ★`HANDOFF/2026-11-16_hw-lead_ISS214_网表一致性第2轮与3条待裁自查.md` (★新建★) · ★`state/fragments/hw.yaml` (★走 `state/frag_write.py` 原子写★)

★**受保护 md5 (★交卷前后逐字节不变★)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★**(★这是 ISS-214 交卷时 2026-11-16 01:04 的基线; 现已被 main 授权的 ISS-233 落表 (2026-11-16 06:48) 更新 ⇒ 现行值见文件头「受保护 md5 · 现行值」行★)**
