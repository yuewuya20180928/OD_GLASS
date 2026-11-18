# I2C 地址表 —— demo 主板 I2C_A / I2C_B 两条总线的从设备全表

| 项 | 值 |
|---|---|
| 文件 | `HW/I2C_ADDR_TABLE.md` |
| 版本 | **V1.0 (2026-11-04)** · ISS-153 |
| 作者 | hw-lead (硬件总工) |
| 适用范围 | **ARS45 demo 主板** (`HW/netlist_v1.csv` 的 P2/P4 页) + 整机阶段规划 |
| 门禁 | ★**`state/check_netlist_pins.py` 判据 C9** —— 网表里每个从设备的地址必须与本表一致, 且同总线地址唯一 |

---

## §0 为什么必须有这张表 (本单存在的理由)

★**换 sensor 时 I2C 地址会变** —— IMX415 = `0x1a`, AR0234CS = `0x10`, OV04C10 = `0x36` (这三个是**不同厂商不同器件**, 地址互不相同) ⇒
⇒ **每次换 sensor / 换模组, 必须把整条总线的地址表重核一遍**, 否则两个从设备撞地址 ⇒ **上电后总线全哑 ⇒ 要么改板 (2-4 周 + ¥4-8K), 要么改固件等原厂确认**。

⇒ 所以本表不是"文档", 是**门禁真源**: `state/check_netlist_pins.py` 的 **C9** 会把网表里声明的地址和本表逐条比对, **改了地址忘了改表 ⇒ 门禁直接报红**。

★本表所有地址都**逐个回到原厂 datasheet 核过** (型号 + 表号/页号, 见 §6); 查不到的写"**未查到**" + 试过的 URL + 失败原因 (§7), **不猜**。

---

## §1 判定口径 (门禁 C9 按这套口径实现)

1. **总线归属**: 网表里 net 名含 `I2C_A` ⇒ 总线 A; 含 `I2C_B` ⇒ 总线 B。
   ★`I2C_CHG_SCL/SDA` (充电板本地自闭环) **不含** `I2C_A`/`I2C_B` ⇒ 不属于本表两条总线。
2. **"从设备" (slave) 的认定**: 挂在总线 net 上、且**不是**以下非从件:
   - 上拉电阻 (`R_PU_*`) · 测试点 (`TP_*`) · SoM 座 (`J_SOM_*`) · 网名/轨名伪件 (`NET_*` / `RAIL_*` / `GND` / `SoC[*]`) · 连接器本身只当"远端模组的挂点"看待 (例: `CONN_CAM` = camera 模组里的 sensor)。
3. **地址取法**: 网表行文本里的 **`I2C 地址 0xNN`** 字样 = 该从设备的 7-bit 地址声明 (唯一写法, 门禁按它机械抽取)。
4. **上拉轨 / 电压域**: 记的是**实际 net** (`RAIL_VDD_1V8_IO` / `RAIL_VDD_3V3_IO`), 不是注释里写的。

---

## §2 总线 A (I2C_A) —— camera 侧 · **1.8 V 域**

| 总线 | 位号 | 器件 | 7-bit 地址 | 状态 | 地址来源 (原厂 datasheet + 表号/页号) | 上拉轨 | 电压域 | 与同总线其它设备是否冲突 |
|---|---|---|---|---|---|---|---|---|
| I2C_A | `CONN_CAM` | **IMX415 camera 模组** (Sony IMX415-AAQR-C 裸 sensor + 镜头/IR-cut 模组) | **0x1a** | 本板在挂 | ★**Sony IMX415-AAQR-C Datasheet (Radxa 公开镜像 E19504), PDF p.26 "SLAVE Address" 表**: `SLAMODE1=Low / SLAMODE0=Low` ⇒ 地址位 `0 0 1 1 0 1 0` = **0x1A** (同表另三档: Low/High=`0x10`, High/Low=`0x36`, High/High=`0x2F`) | `RAIL_VDD_1V8_IO` (2.2k) | **1.8 V** (sensor OVDD 域) | ✔ 不冲突 (本板 A 上目前只有它一个从设备; 预留的光机 0x72 见 §4) |

★**为什么 I2C_A 上拉在 1.8V 而不是 3.3V** (这是 ISS-159 F3 的 C4 冲突项, 本单收口):

- **RK3572 侧**: 本板 I2C_A 走 **I2C5** = `J_SOM_P2 pin31` (I2C5_SCL_M3) + `J_SOM_P2 pin33` (I2C5_SDA_M3), 二者电源域 **1.8V** —— 出处 `HW/PCB/FET3572C_PIN_TABLE.csv` 第 132/134 行 (P2_31 / P2_33, 列 "电压域" = `1.8V`)。
  ⇒ ★**3.3V 上拉会把 SoM 的 1.8V 脚灌到 3.3V = 过压** ⇒ 必须 1.8V 上拉。
- **camera 模组侧**: IMX415 的 I2C (SCL/SDA) 挂在 **OVDD = 1.8V** 域 —— 出处 `HW/IMX415_DEMO_SENSOR_FACTS.md` §1.4 (p.38 绝对最大额定: `VI` ≤ OVDD+0.3V 且 ≤3.3V)。
- ★**旧网表注释写的是"[VDD_3V3_IO] … 上拉仍留 3.3V" —— 与实际 net (`RAIL_VDD_1V8_IO`) 相反, 已作废** (本次随本单订正, 见 §6 §B)。
- **阻值复算 (1.8V 域)**: VOL(max)=0.4V, IOL(max)=3mA ⇒ R ≥ (1.8-0.4)/3mA = **467Ω** ⇒ 取 **2.2k** ✔; 灌流 (1.8-0.4)/2.2k = **0.64mA ≤ 3mA** ✔; 上升沿 t_r = 2.2k×100pF×0.847 ≈ **186ns** ✔。

---

## §3 总线 B (I2C_B) —— 屏控制 + 温度计 · **3.3 V 域**

| 总线 | 位号 | 器件 | 7-bit 地址 | 状态 | 地址来源 (原厂 datasheet + 表号/页号) | 上拉轨 | 电压域 | 与同总线其它设备是否冲突 |
|---|---|---|---|---|---|---|---|---|
| I2C_B | `U_TEMP` | **TI TMP117** 数字温度计 (DRV0006B / WSON-6, 2×2mm) | **0x48** | 本板在挂 | ★**TI TMP117 Datasheet, SNOSD82D (2018-06, 2022-09 修订), §7.5.3.1.2 + Table 7-2 "Address Pin and Slave Addresses" (印刷页 p.21)**: 地址字节 `1001000x` = **0x48**, 对应 `ADD0` 接 **Ground**; 同表另三档: ADD0→V+ = `1001001x` (0x49) / ADD0→SDA = `1001010x` (0x4A) / ADD0→SCL = `1001011x` (0x4B)。脚号出处: 同 datasheet **Table 5-1 "Pin Functions" (p.4)**: ADD0=4 · ALERT=3 · GND=2 · SCL=1 · SDA=6 · V+=5 —— 与本板网表 `U_TEMP pin1=SCL / pin2=GND / pin3=ALERT / pin4=ADD0 / pin5=V+ / pin6=SDA` **逐脚一致**; 本板 ADD0 接 GND ⇒ 地址锁死 0x48 | `RAIL_VDD_3V3_IO` (4.7k) | **3.3 V** (TMP117 V+ 1.7~5.5V, 出处 SNOSD82D p.1 Features) | ✔ 不冲突 (与 `CONN_LIGHT` 0x45 不同) |
| I2C_B | `CONN_LIGHT` | **Waveshare 2.8" DSI 屏模组内 MCU** (树莓派 Pi5 DISPLAY 座 FH12-22S 走线) | **0x45** | 本板在挂 | ★**Raspberry Pi 官方 firmware overlay `boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo` (raspberrypi/firmware@master)** 内节点 `panel_disp1@45` ⇒ 7-bit **0x45** —— 本项目已实测解 DTB 留档, 见 `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` §证据表 [R2] (该 overlay 同时给触摸 GT911 留 `0x14`, demo 不接) | `RAIL_VDD_3V3_IO` (4.7k) | **3.3 V** (屏内 MCU 3.3V I2C, 与主板上拉同域 ⇒ 无需电平转换) | ✔ 不冲突 (与 `U_TEMP` 0x48 不同) |

★**I2C_B 不是触控线, 是屏的控制总线** —— 官方驱动靠 I2C `0xAD=0x01` 使能 + `0xAB`/`0xAA` 调背光 ⇒ **不接就屏不亮也调不了光**。

---

## §4 不在本板 I2C_A / I2C_B 总线上的器件 (备注行 · 也要有出处)

| 总线 | 位号 | 器件 | 7-bit 地址 | 状态 | 地址来源 (原厂 datasheet + 表号/页号) | 上拉轨 | 电压域 | 与同总线其它设备是否冲突 |
|---|---|---|---|---|---|---|---|---|
| 无 (充电板自闭环) | `U_CHG` | **TI BQ25896** 充电 IC (WQFN-24) | **0x6b** | 不在本板总线 | ★**TI BQ25896 Datasheet, SLUSC76C (2015-07, 2018-05 修订)**: §6 "Device Comparison Table" (印刷页 p.4) → **"I2C Address: 6BH (1101011B + R/W)"**; §9.2.16.5 "Slave Address and Data Direction Bit" (p.29); §9.4 "Register Maps" → **"I2C Slave Address: 6BH (1101011B + R/W)"** (p.32)。脚号出处: 同 datasheet p.5 "Pin Functions": **pin5 = SCL · pin6 = SDA** · pin3 = PG · pin4 = STAT · pin7 = INT (开漏) | `I2C_CHG_SCL/SDA` 本地 10k 上拉到 **REGN 5V** | 5 V (充电板唯一逻辑轨) | ✔ **不参与** I2C_A/I2C_B 冲突判定 (见下) |
| I2C_A/I2C_B (预留) | (光机 MCU, 位号未定) | **光机 JBD 走鹃Ⅱ** 内 MCU | 0x72 | 预留 (不在本板) | ★**未查到原厂 datasheet 出处** —— `0x72` 是**我方规划并已写入 JBD 问询**的地址, 尚未拿到 JBD 书面确认 (见 §7)。原厂口径出处: `HW/INTERFACE_TABLE.md` §4.2 第 4 行 + §4.3 (两种原厂答案都预留 0x72) + 问询件 `state/outbox/jbd_query_addendum.md` 问题 4 | — (尚未落板) | — | ✔ 不冲突: 0x72 ≠ 0x1a / 0x48 / 0x45 (A、B 两条都预留) |
| 已删除 | `U_BRIDGE` | **DP→DSI 桥接芯片** | 0x50 (作废) | 已删除 | ★**随 RK3572 无 DP TX ⇒ 桥接整条删除** (网表生成器 `state/gen_netlist.py` 方案B 删除段: `BR_LANES` 常量 + `U_BRIDGE` + 12 颗 0Ω 桥接位 + 8 颗 DP 串阻 + 8 颗对地电容 全删) ⇒ **地址 0x50 作废, 不再出现在任何总线** | — | — | — (无此设备) |
| 整机阶段 (demo 不用) | (sensor, 位号未定) | **onsemi AR0234CS** | 0x10 (SADDR 拉高 ⇒ 0x18) | 不在 demo | ★**onsemi AR0234CS Datasheet (公开镜像 AR0234CS-D-Awin), 印刷页 p.10 "TWO-WIRE SERIAL REGISTER INTERFACE"**: "The default slave addresses used by the AR0234CS are **0x20 (write address) and 0x21 (read address)**" ⇒ **7-bit = 0x10**; "Alternate slave addresses of **0x30/0x31** … can be selected by enabling and asserting the **SADDR** input" ⇒ **7-bit = 0x18**; 亦可经 `R0x31FC` 改写 | — | 2.8 V (VDD_IO) | ✔ 不冲突: 0x10 (或 0x18) ≠ 0x1a / 0x48 / 0x45 |

★**BQ25896 到底挂不挂在本板的 I2C 总线上? —— 明确答案: 不挂。**

1. **它不在主板上**: `U_CHG` 的 board 列 = **`CHG_BOARD`** (镜框充电板), 不在 `MAIN_PCB`。
2. **它的 I2C 是充电板本地自闭环**: 网表 P10 页 `I2C_CHG_SCL` / `I2C_CHG_SDA` 两行 —— `U_CHG pin5` / `pin6` 只接本地的 `R_PU_SCL` / `R_PU_SDA` (10k, 上拉到 REGN 5V);
   ★**PM 已裁决"充电 IC 的 I2C 不跨铰链"** ⇒ `J_CHG pin9/pin10` 本版留空不接, **不引到主板** ⇒ **主板的 I2C_A / I2C_B 上没有 BQ25896**。
3. **跨铰链的只有两根 GPIO**: `U_CHG pin3 (PG)` → `J_CHG pin6` → 主板 `PWR_GOOD`; `U_CHG pin4 (STAT)` → `J_CHG pin5` → 主板 `CHG_STAT` —— **是 GPIO, 不是 I2C**。
⇒ ★**结论: `0x6b` 不参与 I2C_A / I2C_B 的地址冲突判定。** 但地址本身必须写对 (软件将来若要在线配置充电参数, 走的是充电板那条自闭环总线) ⇒ 本表保留该行。

---

## §5 冲突检查结论 (逐对比对)

### 总线 A —— 本板在挂的从设备

| # | 位号 | 器件 | 地址 |
|---|---|---|---|
| 1 | `CONN_CAM` | IMX415 camera 模组 | 0x1a |

- **两两比对**: A 上只有 1 个从设备 ⇒ **无同总线两两冲突项**。
- 与"预留但不在本板"的光机 0x72 交叉比对: `0x1a` ≠ `0x72` ⇒ **不冲突** ✔。
- 与"整机阶段才用"的 AR0234CS 0x10 / 0x18 交叉比对: `0x1a` ≠ `0x10`, ≠ `0x18` ⇒ **不冲突** ✔ (⇒ 将来换回 AR0234CS 也无需改地址, **但要改上拉轨**, 见 §2 末尾)。
- 与已删除的桥接 0x50: 设备已不存在 ⇒ 不适用。

### 总线 B —— 本板在挂的从设备

| # | 位号 | 器件 | 地址 |
|---|---|---|---|
| 1 | `U_TEMP` | TI TMP117 | 0x48 |
| 2 | `CONN_LIGHT` | Waveshare 2.8" 屏模组内 MCU | 0x45 |

- **两两比对 (穷举 1 对)**: `U_TEMP 0x48` vs `CONN_LIGHT 0x45` ⇒ **0x48 ≠ 0x45 ⇒ 不冲突** ✔。
- 与预留的光机 0x72 交叉比对: `0x48` ≠ `0x72` ✔ · `0x45` ≠ `0x72` ✔ ⇒ **不冲突**。
- 与不在本板总线的 BQ25896 0x6b: 不同总线 ⇒ 不适用 (若将来把充电板 I2C 跨铰链接到主板 B, `0x6b` 与 `0x48`/`0x45` 仍互不相同 ⇒ 也安全)。

### 总表结论

| 总线 | 从设备数 | 地址集合 | 唯一性 |
|---|---|---|---|
| I2C_A | 1 (+1 预留) | {0x1a} (+0x72 预留) | ✔ 唯一 |
| I2C_B | 2 (+1 预留) | {0x48, 0x45} (+0x72 预留) | ✔ 唯一 |

★**两条总线各自地址唯一, 且 A / B 两条之间即使将来合并也不会撞 (0x1a / 0x48 / 0x45 / 0x72 四个值互不相同)。**

---

## §6 本次改动清单 (ISS-153)

### A. `HW/I2C_ADDR_TABLE.md` (新建)

- 本文件。**门禁 C9 的真源**。

### B. `state/gen_netlist.py` (★**只改注释文字, 不改任何连接关系 / 脚号 / 网名 / 器件值**)

| # | 位置 (改前) | 改后 | 依据 |
|---|---|---|---|
| B1 | `U_TEMP` I2C_B_SCL 行 note: `… 桥接 0x50 / 充电 IC 0x12 / 光机 0x72 都不冲突` | ★`桥接` 改成 **已删除** · ★`充电 IC 0x12` 改成 **0x6b (且注明不在本板总线上)** · 补上 TMP117 的 datasheet 出处 (Table 7-2, p.21) 与 IMX415/AR0234CS 的出处 | §2 §3 §4 §6 |
| B2 | `R_PU_I2CA_SCL` 行 note: `[VDD_3V3_IO] I2C_A 上拉 (… ★**上拉仍留 3.3V** …)` | ★改成 **`[VDD_1V8_IO]` 口径** —— 与实际 net `RAIL_VDD_1V8_IO` 一致, 并写清依据 (RK3572 I2C5 = 1.8V 域 + IMX415 OVDD 1.8V 域) + 1.8V 域下的阻值复算 | §2 |
| B3 | `R_PU_I2CA_SDA` 行 note: `[VDD_3V3_IO] I2C_A 上拉` | 同上 (`[VDD_1V8_IO]`) | §2 |
| B4 | `CONN_CAM` I2C_A_SCL/SDA 附加节点 value: `上拉 2.2k 到 3.3V (★IMX415 IOL≤3mA 重算)` | 改成 `上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO …)` | §2 |
| B5 | `CONN_CAM` I2C_A_SCL/SDA 行 note | ★补上 **`I2C 地址 0x1a`** 字样 (★**网表里从设备的地址必须有这句, 门禁 C9 按它机械抽取**) | §1 口径 3 + 门禁 C9 |
| B6 | `CONN_LIGHT` I2C_B_SCL/SDA 行 note | ★补上 **`I2C 地址 0x45`** 字样 (同上) | 同上 |

### C. `state/check_netlist_pins.py` (★**只加 C9 判据**, 不动 C1~C8)

C9 四步 (全过才算过):
1. `HW/I2C_ADDR_TABLE.md` 存在且能解析出表行;
2. 网表里挂在 I2C_A / I2C_B 的**从设备集合** == 表里 `状态 = 本板在挂` 的行集合 (**双向**: 加了器件忘了加表 ⇒ 报红; 表里写了本板在挂但网表里没有 ⇒ 也报红);
3. 每个从设备**网表里声明的地址** == **表里该位号的地址** (不一致 ⇒ 报红);
4. **同一条总线内地址两两唯一** (表内查一遍 + 网表内查一遍)。

### D. 生成物

- `HW/netlist_v1.csv` ← 重跑 `python3 state/gen_netlist.py`
- `HW/netlist_v1_pins.csv` ← 重跑 `python3 state/gen_netlist_pins.py` (脚级表: TMP117 = 6 脚 / 挂 I2C_B)

---

## §7 出处清单 (型号 + 表号/页号 + URL)

| # | 器件 / 事实 | 原厂文档 | 表号 / 页号 | URL |
|---|---|---|---|---|
| S1 | TMP117 7-bit 地址 `0x48` (ADD0=GND) | **TI TMP117**, datasheet **SNOSD82D** (2018-06, 2022-09 修订) | **§7.5.3.1.2 + Table 7-2 "Address Pin and Slave Addresses" (印刷页 p.21)**; 脚号 **Table 5-1 "Pin Functions" (p.4)**; 供电范围 p.1 | <https://www.ti.com/lit/ds/symlink/tmp117.pdf> |
| S2 | BQ25896 7-bit 地址 `0x6b`; pin5=SCL / pin6=SDA / pin3=PG / pin4=STAT / pin7=INT | **TI BQ25896**, datasheet **SLUSC76C** (2015-07, 2018-05 修订) | **§6 Device Comparison Table (p.4) "I2C Address: 6BH"**; **§9.2.16.5 (p.29)**; **§9.4 Register Maps (p.32) "I2C Slave Address: 6BH"**; **p.5 Pin Functions** | <https://www.ti.com/lit/ds/symlink/bq25896.pdf> |
| S3 | IMX415 7-bit 地址 `0x1a` (SLAMODE1/0 = Low/Low); 另三档 0x10 / 0x36 / 0x2f | **Sony IMX415-AAQR-C** Datasheet (E19504) | **PDF p.26 "SLAVE Address" 表** (SLAMODE1/SLAMODE0 × 地址位); 引脚表另见同文档 SLAMODE0=H10 / SLAMODE1=J10 | <https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf> (Radxa 公开镜像) |
| S4 | AR0234CS 7-bit 地址 `0x10` (写 0x20/读 0x21); SADDR 拉高 ⇒ `0x18` | **onsemi AR0234CS** Datasheet (AR0234CS-D-Awin) | **印刷页 p.10 "TWO-WIRE SERIAL REGISTER INTERFACE"** | <https://sunnywale.com/uploadfile/2022/0222/AR0234CS-D-Awin.PDF> (公开镜像) |
| S5 | 屏模组内 MCU 7-bit 地址 `0x45` | **Raspberry Pi 官方 firmware overlay** `vc4-kms-dsi-waveshare-panel.dtbo` | overlay 内 `panel_disp1@45` | <https://github.com/raspberrypi/firmware/blob/master/boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo> (本项目已实测解 DTB 留档于 `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` §证据 [R2]) |
| S6 | RK3572 的 I2C5 = **1.8V 域** (⇒ I2C_A 必须 1.8V 上拉) | `HW/PCB/FET3572C_PIN_TABLE.csv` (原厂 RK3572 引脚表转录) | P2_31 `I2C5_SCL_M3` / P2_33 `I2C5_SDA_M3`, 电压域列 = `1.8V` | 项目内 (原厂 RK3572 Datasheet) |
| S7 | IMX415 的 I2C 挂 OVDD=1.8V 域; `VI` 绝对最大 ≤ OVDD+0.3V 且 ≤3.3V | `HW/IMX415_DEMO_SENSOR_FACTS.md` §1.4 (源自 S3 同款 datasheet p.3 绝对最大额定 / p.14 DC 特性) | §1.4 | 项目内 |

### ★未查到的项 (不猜)

| # | 项 | 状态 | 试过的 URL / 查法 | 失败原因 | 后果 |
|---|---|---|---|---|---|
| N1 | **光机 JBD 走鹃Ⅱ MCU 的 I2C 地址 `0x72`** | ★**未查到原厂 datasheet 出处** | ① `HW/INTERFACE_TABLE.md` §4.2/§4.3 (自记 `[0数据] — 需 JBD 确认`) ② `state/outbox/jbd_query_addendum.md` 问题 4 (问询件已写明"我们已预留 0x72, 请确认") ③ 项目内 `JBD_QUESTION_LIST.md` / `HW/LENS_SELECTION.md` 无地址条款 | **光机模组型号与内部 MCU 尚未确定, 无原厂 datasheet 可查** ⇒ 0x72 目前只是**我方规划值** | ★**该行不得当作"已核实"**; 换光机时必须回原厂重核 (门禁 C9 只卡本板在挂的设备, 预留行只查状态标注) |
| N2 | Waveshare 屏模组 MCU 的**芯片级** datasheet (不是树莓派 overlay) | 未查到 (地址本身已由 S5 官方 overlay 确认) | Waveshare 官方 wiki / 屏模组 datasheet 检索 | 屏模组内部 MCU 不公开型号 | 不影响: 地址有官方 overlay 出处 |

---

## §8 换料时的执行流程 (★写死, 下次照做)

1. 拿到新 sensor / 模组的**原厂 datasheet** ⇒ 抄下 **7-bit 地址 + 地址选择脚接法** (IMX415: SLAMODE0/1; AR0234CS: SADDR; TMP117: ADD0)。
2. **改 `state/gen_netlist.py` 里该器件那一行的 note 里的 `I2C 地址 0xNN`** (★网表里从设备的地址只有这一种写法, 门禁按它抽)。
3. **改本表对应行** (地址 + 来源 + 地址选择脚接法 + 上拉轨/电压域是否要跟着改)。
4. **重跑** `python3 state/gen_netlist.py` → `python3 state/gen_netlist_pins.py` → `python3 state/check_netlist_pins.py` (★**C9 不过就不许往下走**) → `python3 state/check_netlist.py` → `python3 state/check_kicad_net.py`。
5. ★**换 sensor 必查电平域**: IMX415 = I2C 挂 1.8V (上拉 1.8V) / AR0234CS = VDD_IO 2.8V (⇒ 上拉轨要改, 否则 VIH=0.7×2.8=1.96V > 1.8V 上拉 ⇒ **读不到**) —— **地址对了不代表总线能用**。
