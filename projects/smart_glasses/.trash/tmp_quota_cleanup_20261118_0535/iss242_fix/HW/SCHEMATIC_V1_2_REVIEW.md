# 原理图 V1.4 复审报告 (ISS-088 第 2 轮)

- **复审人**: hw-lead (硬件总工) 🔧
- **日期**: 2026-10-27
- **复审对象**: `HW/netlist_v1.csv` (411 行) / `HW/netlist_v1.net` (1045 行) / `HW/BOM_v1.csv` / `HW/SCHEMATIC_V1.md`
- **基线**: V1.4 (2026-10-27 09:2x 重新生成) —— 已含 F1/F2/F6 与 `.net` 导出器重写
- **上一轮**: 40 分钟超时, 0 落盘; 本轮**以现状为准**, 不复述上一轮结论

---

## 0. 机械验收基线 (先跑, 后判)

```bash
cd projects/smart_glasses
python3 state/check_netlist.py    → rc=0  ✅ 28/28
python3 state/check_kicad_net.py  → rc=0  ✅ 5/5   (提示: 6 个单点网, 已登记 ISS-094)
python3 state/gen_bom.py          → ✅ 自检全过 (位号/qty/采购状态/DNP 数/板级归属)
```

**三条门禁全过 ≠ 设计对**。本轮 5 条 A 级缺陷**全部落在现有门禁的盲区里** (见 §4 F-9)。

---

## 1. 总体结论

| 项 | 结论 |
|---|---|
| 拓扑方向 (SYS 不过铰链 + 充电电流跨铰链) | ✅ **通过** |
| 跨铰链 4 组通道的 **pin 账** | ❌ **不通过** (缺 4 脚 + CONN_LIGHT 无回流地 + 18p/40p 自相矛盾) |
| 电池温度检测链 (NTC → BQ25896 TS) | ❌ **不通过** (分压网络实际不存在 + 跨板无通道) |
| 复位监督链 (U_SUPV → RESET_N) | ❌ **不通过** (分压上臂悬空 → RESET 永不释放) |
| 充电板 ↔ 主 PCB 跨板一致性 | ❌ **不通过** (TS_BAT 跨板断裂, 板级归属把它伪装成单板) |
| BOM 可采购性 | ❌ **不通过** (J_CHG / CONN_USB 被误判为 "DNP-不装") |
| **投板前必须闭环** | **A 级 5 条 + B 级 6 条** |

> **一句话**: V1.4 把上一轮的 3 类结构性缺陷 (F1/F2/F6) 修干净了, 拓扑方向是对的;
> 但**板级归属与 BOM 判定这两个"元数据层"仍是手工填的**, 它们没有随网表一起被机械校验,
> 于是同一个错误 (TS_BAT) 在网表层、板级层、BOM 层被放大了三遍。

---

## 2. A 级缺陷 (投板前必改 —— 会导致功能失效, 不是纸面问题)

### A-1 ★★ `TS_BAT` 跨板断裂: NTC 在镜脚, BQ25896 的 TS 脚在镜框, **跨铰链没有 TS 通道**

| 证据 | 内容 |
|---|---|
| [实测] `netlist_v1.csv` L32 | `net=TS_BAT, n1=U_CHG TS, n2=R_NTC_BAT` — `U_CHG` (BQ25896) 板级 = **CHG_BOARD (镜框)** |
| [实测] `netlist_v1.csv` L33 | `net=TS_BAT, n1=R_NTC_BAT, n2=BAT_PROT_CELL` — 电池侧节点, 板级 = **CHG_BOARD** (见 B-1 归属错) |
| [实测] `gen_netlist.py` J_CHG pin map | `pin1/2=BAT_CHG, pin3/4=GND, pin5=CHG_STAT, pin6=PWR_GOOD, pin7=VBUS_DET, pin8-10=预留` — **没有 TS** |
| [实测] `netlist_v1.net` | TS_BAT net 只有 `U_CHG.TS` + `R_NTC_BAT.pin1` 两个节点, **没有 J_CHG 脚** |

**后果**: 电池在镜脚, NTC 贴电芯也在镜脚, 而 BQ25896 在镜框充电板 → TS 信号**必须**跨铰链,
但 J_CHG 没有 TS pin → 这条连接在物理上不成立。**电池过温/欠温硬件停充 (安全项) 失效。**

**可执行修复 (不换板)**:
1. `J_CHG pin8` 由 "预留 (DNP)" 改为 **`TS_BAT`** (现为 DNP 预留位, 不占成本);
2. `R_NTC_BAT` + `R_TS_PULL` 留在**镜脚主 PCB** (贴电芯侧), TS_BAT 经 J_CHG pin8 到镜框 `U_CHG.TS`;
3. `R_TS_PULL` (10k 下拉) 接在**镜脚 TS_BAT 侧** (BQ25896 TS 脚外部下拉 + NTC 上拉的经典接法),
   跨铰链后仍与 TS 在同一节点 → 阻值不受 FPC 漏电流影响 (FPC 漏电 µA 级, 10k 下拉 ≫ 漏电)。

---

### A-2 ★★★ TS 分压网络**根本没有画出来** → BQ25896 恒判温度异常 → **接上电不充电**

这是 A-1 之外**独立**的第二条缺陷, 即使把 NTC 挪到充电板也照样错。

| 器件 | `netlist_v1.net` 里实际 pin 数 | 应为 | 判定 |
|---|---|---|---|
| `R_NTC_BAT` | **1** (`pin "1"` @ TS_BAT) | 2 | ❌ 第二脚悬空 |
| `R_TS_PULL` | **1** (`pin "1"` @ GND) | 2 | ❌ 第二脚悬空 |

**根因**:
- L33 写成 `net=TS_BAT, n1=R_NTC_BAT, n2=BAT_PROT_CELL` —— 按本版口径 "**一行 = 一根连接,
  net 列 = 这根连接所在的网**", 这行的 `net` 应是 **`BAT_PROT_CELL`** (R_NTC_BAT 的另一端所在网),
  写 `TS_BAT` 等于宣称 "R_NTC_BAT 与 BAT_PROT_CELL 同在 TS_BAT 网" → 导出器把 R_NTC_BAT 塞进
  TS_BAT, 而 `BAT_PROT_CELL` 作为伪网名被丢掉 → **R_NTC_BAT 第二脚不在任何网里**。
- L34 写成 `net=GND, n1=R_TS_PULL, n2=GND` —— 只有 GND 一端, **缺 `net=TS_BAT, n1=R_TS_PULL` 那一行**。

**后果**: BQ25896 的 TS 脚只连着一只"半悬空"的 NTC, 既无有效分压也无下拉 →
按 TI 对 TS 脚的定义 (悬空/超范围 = 温度异常) → **芯片拒绝充电**。
这是"样机插上 Type-C 一点反应都没有"级别的缺陷, 且**在当前所有门禁下都判不出来**
(`check_netlist` 只查 "每行两端齐全", `check_kicad_net` 只查 "同一 (ref,pin) 不重复")。

**可执行修复**:
```
新增行: P1, TS_BAT,   R_TS_PULL, U_CHG TS, R_TS_PULL, 10k ±1%, R, 必装, ...
改  行: P1, BAT_PROT_CELL, R_NTC_BAT, Q1,    R_NTC_BAT, 10k NTC B=3435 ±1%, R, 必装, ...
改  行: P1, GND,      R_TS_PULL, GND,      R_TS_PULL, 10k ±1%, R, 必装, ...
```
另: NTC 的参考端语义要明确 —— 现在接的是 **Q1/Q2 中点 (`BAT_PROT_CELL`)**,
应改成 **电芯负极 `BAT_CELL_N`** (L29 `BT_432243 B- ↔ U_BATPROT B-`), 才是"贴电芯、参考电芯负极"的
标准接法, 分压比不受保护管压降影响。

---

### A-3 ★★★ `R_SUPV_DIV1` 的 V_SOC_IO 端悬空 → `U_SUPV.IN ≈ 0V` → **RESET_N 永不释放, SoC 上不了电**

| 证据 | 内容 |
|---|---|
| [实测] `netlist_v1.csv` L390 | `net=SUPV_SENSE, n1=RAIL_V_SOC_IO, n2=R_SUPV_DIV1` —— `RAIL_*` 是**伪网名不是器件**, 导出器丢弃 → `R_SUPV_DIV1` 只有 SUPV_SENSE 一端 |
| [实测] `netlist_v1.net` | `R_SUPV_DIV1` 只有 `pin "1"` (net=SUPV_SENSE) → **第二脚悬空** |
| [实测] `netlist_v1.net` SUPV_SENSE net | 成员 = `R_SUPV_DIV1.pin1`, `R_SUPV_DIV2.pin1`, `U_SUPV.IN`, `U_SUPV.pin1` |
| [实测] `netlist_v1.csv` L392 | `R_SUPV_DIV2` 另一端 → GND |

**推导**: 监督器输入节点 = SUPV_SENSE, 其到 V_SOC_IO 的通路是**悬空的** R_SUPV_DIV1,
到地只有 R_SUPV_DIV2 → **IN ≈ 0V** → 欠压窗口 (TPS3808G01 典型 0.5 V) → **恒判欠压 →
开漏 RESET 恒拉低 → RESET_N 恒低 → SoC 永远停在复位态, 整机不上电**。

**注**: 这条与 ISS-094 ("RAIL_* 别名与网名指同一节点") **同根因但不同后果**:
ISS-094 记的是 "6 个单点网", 这里是"**分压上臂悬空**", 不在那 6 个之列 (SUPV_SENSE 有 4 个节点),
所以**不在 ISS-094 的已知未平账范围内**, 是本轮新发现。

**可执行修复 (两处都要改)**:
1. **网表**: L390 的 `net` 改成 `V_SOC_IO` (分压上臂在 V_SOC_IO 侧), 另加一行
   `net=SUPV_SENSE, n1=R_SUPV_DIV1, n2=R_SUPV_DIV2` 把中点保住;
2. **导出器**: `gen_kicad_net.py` 增加 **网名合并** 步骤 —— 当某 net 的成员里出现 `RAIL_*` 伪网名时,
   把该 net **并入**那个 rail net (或反过来), 而不是丢弃。
   这一步同时会消掉 ISS-094 的 6 个单点网 (USB_VBUS_RAW / VBUS_DET_RAW / BAT_DET_RAW / DSI_BR / DP_TX / XTAL),
   一并把 `BAT_DET` / `VBUS_DET` 两条分压链的上端接回来 (SoC 否则读不到电池电压)。

---

### A-4 ★★★ `CONN_LIGHT` (光机连接器) **21 个脚里一个 GND 都没有** → 跨铰链 DSI 差分无回流路径

| 证据 | 内容 |
|---|---|
| [实测] `netlist_v1.net` | `CONN_LIGHT` 的 21 个 pin 全部是信号/电源: pin1-10 = DSI(方案A) / pin11-16 = BR(方案B) / pin17,18 = I2C_B / pin19,20,21 = LIGHT_3V3 / 1V8 / 5V。**没有任何一脚接 GND** |
| [实测] `check_netlist.py` | "跨铰链连接器无断链 (声明 pin 数 == 实际引用) 全对" —— 该门禁**只数脚数, 不查回流地** |

**后果**: 光机在镜框, SoC 在镜脚, DSI 2 lane 差分跨铰链**没有回流地** →
差分对的回流只能绕远路 → 共模电平漂移 / 眼图闭合失败 / EMI 恶化。
按经验值, 跨铰链高速差分**至少要 1 根紧邻参考地, 4 lane 建议 2 根 + 参考平面连续**。

**可执行修复**: `CONN_LIGHT` 由 21p → **24p**:
```
pin1-10  DSI 差分 (方案A: R_SEL_* 装)
pin11-16 BR 差分 (方案B: BR_* 装, 与 R_SEL_* 互斥)
pin17/18 I2C_B (DDC)
pin19/20/21 LIGHT_3V3 / 1V8 / 5V
pin22/23 GND ×2   ← 新增 (回流地)
pin24    NC / 备用
```
或保持 21p 但把方案B 的 BR 位 (pin11-16, 方案A 下 DNP 空置) 中借 2 个作 GND —— **不推荐**,
因为方案A/方案B 切换时 GND 位置会变。

**同族问题**: `CONN_CAM` 只有 **1 根** GND (pin18), 而它要过 4 lane CSI (8 根 100Ω 差分) + MCLK
→ 同样建议 18p → 20p, 加 2 根 GND。

---

### A-5 ★★ DP 的 4 路 AC 耦合电容**被短路**, 且 4 路的 N 路电容错接到 P 路串阻上

| 行 | 内容 | 判定 |
|---|---|---|
| L242 | `net=DP_TX_A0_P_SRC, n1=SoC.DP_TX_A0_P, n2=R_SER_DP_A0_P` | ✅ 串阻上端在 SRC 网 |
| L243 | `net=DP_TX_A0_P, n1=R_SER_DP_A0_P, n2=U_BRIDGE pin21` | ✅ 串阻下端在桥接侧网 |
| **L244** | `net=DP_TX_A0_P_SRC, n1=C_AC_DP_A0, n2=R_SER_DP_A0_P` | ❌ **电容与串阻同网 → 电容被导线短接, 不起隔直作用** |

**对照 (CSI 写法正确)**: L204 `net=CSI_D0_CK_P_SRC, n1=SoC…, n2=C_AC_CSI_D0_CK_P` +
L205 `net=CSI_D0_CK_P, n1=C_AC_CSI_D0_CK_P, n2=CONN_CAM pin1` —— 电容两端落在**两个不同的网** ✓。

**叠加错误**: L248 / L256 / L264 / L272 (对应 A0/A1/A2/A3 的 **N** 路) 的 `n2` 全部写成
`R_SER_DP_A0_P` (**P 路**串阻) —— 复制粘贴错误, 共 4 处。

**后果**: DP→DSI 桥接链路 (方案B) 的 AC 耦合全部失效 → 桥接芯片收到带直流偏置的差分 →
**方案B 启用即不工作**。方案A 下 DNP 掩盖了它, 所以现有门禁全过。

**可执行修复**: 每路 DP 拆成 3 个网:
```
net=DP_TX_Ax_P_SRC  : SoC.DP_TX_Ax_P ↔ C_AC_DP_Ax        (电容上端)
net=DP_TX_Ax_P_CAP  : C_AC_DP_Ax ↔ R_SER_DP_Ax_P          (电容下端 = 串阻上端) ← 新增
net=DP_TX_Ax_P      : R_SER_DP_Ax_P ↔ U_BRIDGE pin(2x+1)
```
N 路同理, 并把 `n2` 改成对应的 `R_SER_DP_Ax_N`。

---

## 3. B 级缺陷 (不改会返工 / 错料 / 备料买错)

### B-1 ★★ `R_NTC_BAT` / `R_TS_PULL` 板级归属错标 CHG_BOARD (NTC 贴电芯在**镜脚**)

- [实测] `gen_netlist.py` L57-61: `CHG_BOARD_REFS` 里含 `"R_NTC_BAT", "R_TS_PULL"` → `board_for()` 直接判 CHG_BOARD
- [实测] `netlist_v1.csv` L33 `board=CHG_BOARD`; L34 `board=CHG_BOARD`
- [实测] `BOM_v1.csv` L19/L20: `R_NTC_BAT,1,...,镜框充电板` / `R_TS_PULL,1,...,镜框充电板`
- **物理事实**: NTC "贴电芯表面, 引线尽量短" → 电池在镜脚 → **必须在镜脚主 PCB**
- **后果**: BOM 把它排到充电板 → 贴错板 → NTC 不贴电芯 → 与 A-1/A-2 叠加成"三重失效"

### B-2 ★★ `CONN_CAM` 脚数三处自相矛盾: **18p vs 40p**

| 位置 | 写的 |
|---|---|
| `netlist_v1.csv` L240 `value` | `18p@0.5mm 跨铰链连接器` |
| 同一行 `note` | `主 PCB ↔ sensor 板 **40p** 跨铰链连接器` |
| `gen_netlist.py` PAGES["P5"] | `MIPI-CSI 传感器 (CONN_CAM **40p** 跨铰链)` |
| L204 / L207 note | `连接 CONN_CAM **40p** (跨铰链)` |
| `netlist_v1.net` 实际 | 18 个 pin 全用满 (pin1-18) |

- **裁决建议**: 以 **18p 为准** (pin 账已闭合: CK×2 + D0-D3×2 + MCLK + RESET + I2C×2 + rails×3 + GND×1 = 18),
  但按 A-4 建议扩到 **20p** (加 2 根 GND); `PAGES["P5"]` 标题与所有 note 里的 "40p" 全部改成同一个数。

### B-3 ★★ `CONN_LIGHT` 的 pin map 在**三处**互相矛盾, 且 note 引用了超出 21p 的脚号

| 信号 | `P4` INVENTORY note (L203) | `P9` INVENTORY note (L401) | **网表实际** |
|---|---|---|---|
| DSI CK | pin3/4 | pin3/4 | **pin1/2** |
| DSI D0 | pin5/6 | pin5/6 | **pin3/4** |
| DSI D1 | pin7/8 | pin7/8 | **pin5/6** |
| DSI D2 | pin9/10 | (9-12 预留) | **pin7/8** |
| DSI D3 | pin11/12 | (9-12 预留) | **pin9/10** |
| DDC (I2C_B) | pin13/14 | pin13/14 | **pin17/18** |
| 桥接方案 B | pin21..26 | pin21-26 | **pin11..16** |
| 光机电源 | pin27/28/29 | pin27-29 | **pin19/20/21** |

- note 写到 **pin27/28/29** → 超出 21p 连接器物理脚数 → 结构总工若照 note 选型 (30p) 而硬件画 21p → **必返工**
- L197/L198 的 note 写 "连接 CONN_LIGHT pin13/pin14 → 光机", 但**同一行实际用的是 pin17/pin18** → 同一行自相矛盾
- **修复**: 以**网表实际连线**为准 (它自洽且落在 21p 内), 把两处 INVENTORY note 与 L197/L198 的 note 全部改成实际脚号

### B-4 ★★ 导出器给"裸 IC / 裸连接器名"节点分配**幻影脚号** (与 V1.4 声称已修的问题是同一类, 只是换了入口)

- [实测] `netlist_v1.net` 里以下 (ref,pin) 的 pin 号是**按出现顺序编的**, 与真实封装脚号无关:

| 器件 | 幻影 pin | 实际代表的功能 |
|---|---|---|
| `J_TYPE_C` | `pin "1"` | VBUS 入口 (真实脚是 A4/A9/B4/B9) |
| `J_CHG` | `pin "1"` | (与 pin1/pin2 同网) |
| `U_CHG` (BQ25896) | `pin "1"/"2"/"3"` | **VIN / STAT / PG** |
| `U_BATPROT` (BQ2970) | `pin "1"/"2"/"3"/"4"` | **B+ / BAT / B+ / SYS** |
| `U_SUPV` | `pin "1"` | (与 IN 同网) |
| `U_BRIDGE` | `pin "1"/"2"` | DSI 出 / DP 入 |
| `X1` | `pin "3"` | (XTAL 单点网) |
| `J_DEBUG` / `J_UART` | `pin "?"` | 调试/串口 |

- **后果**: 原理图符号一旦按 datasheet 画 (必然发生), 这些脚的编号对不上 → **符号与封装错位** →
  投板后可能直接短路 (BQ25896 的 PG 脚接到 STAT 脚这种), 最坏情况 2-4 周返工 + ¥4-8K 板费
- **门禁缺口**: `check_kicad_net.py` 只查 "同一 (ref,pin) 不出现在 2 个 net", **查不出 pin 号是否真实**
- **修复**: CSV 里所有 IC/连接器的 node 必须写成 `U_CHG STAT` / `U_CHG PG` / `U_BATPROT B+` 这种带脚名的形式
  (V1.4 已经这么改了一部分: `U_CHG TS` / `U_SUPV IN` / `U_SUPV VDD` —— 说明方向对, 只是没改完);
  导出器再加一条硬规则: **多脚器件 (IC/CONN/SW) 出现纯数字 pin → 导出直接报错**

### B-5 ★★ 带 `[INVENTORY]` 前缀的行被导出器**整行跳过** → DNP 预留脚在 `.net` 里**不存在**

- [实测] `gen_kicad_net.py`: `if (r.get("note") or "").startswith("[INVENTORY]"): continue`
- [实测] 受影响的预留位: `J_CHG pin8/9/10` (HINGE_RSV)、`CONN_USB pin4` (HINGE_RSV)
- [实测] `netlist_v1.net` 里 `J_CHG` 只有 `pin1..pin7`; `CONN_USB` 只有 `pin1..pin3`
- **后果**: "预留位" 在 PCB 上**没有焊盘** → 将来要加信号 (USB3 SS / 额外 TS) 得**改板**,
  与"预留"的初衷相反; 而且 `check_netlist` 的 "跨铰链连接器无断链 (声明 pin 数 == 实际引用) 全对"
  是按 **CSV 行**数的, 不是按 `.net` 实际 pin 数的 → 门禁没抓到
- **修复**: 预留脚应当**进 `.net`** (作为 DNP 的独立 net, 例如 `HINGE_RSV`), 只是不接任何东西;
  导出器不应跳过 `[INVENTORY]` 行, 而应把它的 pin 落到一个占位 net 上

### B-6 ★★★ `gen_bom.py` 的 DNP 判定是 **ref 级**的 → **`J_CHG` 与 `CONN_USB` 被判成 "DNP-不装"**

- [实测] `state/gen_bom.py` L99-102:
  ```python
  if r.get("dnp") == "DNP":
      # DNP 从严: 只要有一行标 DNP 就整颗按 DNP
      bom[ref]["dnp"] = "DNP"; bom[ref]["procurement"] = "DNP-不装"
  ```
- [实测] `BOM_v1.csv`:
  - L11 `J_CHG,1,跨铰链 1.5A (双 pin 并联),NET,DNP,跨铰链界面,P1,...,DNP-不装`
  - L193 `CONN_USB,1,4p@0.5mm USB 跨铰链连接器 (D+/D-/GND/预留),CONN,DNP,跨铰链界面,P6,...,DNP-不装`
- **为什么**: `J_CHG` 的 pin8/9/10 是 DNP 预留 → "从严"规则把**整颗连接器**判成不装;
  `CONN_USB` 的 pin4 是 DNP 预留 → 同样整颗不装
- **后果 (致命)**: **整机唯一的主跨铰链通道 (J_CHG, 充电电流走它)** 和 **唯一的 USB 跨铰链烧录口 (CONN_USB)**
  在 BOM 上是"不装" → 备料时不买 → **样机根本装不起来 / 没有烧录口**
- **自检为何没抓到**: `gen_bom.py` L126-129 的自检比较的是 "netlist 里有 DNP 行的 ref 数" vs "BOM 里标 DNP 的 ref 数"
  —— 这两个数**按构造必然相等**, 属于**同义反复的自检**, 查不出"颗级误判"
- **修复 (两处都要改)**:
  1. `gen_bom.py`: DNP 改为**颗级判定** —— 只有当该器件的**所有**连接行都是 DNP (或器件本身是
     "方案二选一" 的可选项) 才整颗 DNP; 建议加一列 `dnp_pins` 列出是哪几个 net DNP;
  2. `gen_bom.py` 自检: 增加断言 "**跨铰链连接器 / 电源链器件不得标 DNP**" (白名单反查)

### B-7 ★ `J_CHG` 在 `.net` 里的 **footprint / value 取错行**

- [实测] `netlist_v1.net` L10: `(comp (ref "J_CHG") (value "跨铰链 1.5A (双 pin 并联)") (footprint "TBD:NET_PLACEHOLDER"))`
- 原因: `gen_kicad_net.py` 的 `comp()` 用**该 ref 在 CSV 里第一次出现的行**的 `value`/`type`;
  而 J_CHG 第一次出现在 `ref` 列是 L15 (`type=NET`) 而不是 L31 (`type=CONN`)
- **后果**: 跨铰链主连接器在 `.net` 里被定义成一个 "NET 类型的占位符", footprint 是 `TBD:NET_PLACEHOLDER`
  → KiCad 导入时不会被当成连接器 → **原理图里 J_CHG 拿不到封装**
- **修复**: `comp()` 取值时**优先用 `type` 属于 CONN/IC 的行**, 或在 CSV 里让器件登记行排在最前

---

## 4. C 级 (一致性 / 待办 / 门禁补强)

| # | 事项 | 证据 | 建议 |
|---|---|---|---|
| C-1 | `RAIL_BAT` / `RAIL_SYS` 被 `board_for()` 硬编码成 CHG_BOARD, 但电池与电池保护 IC 在镜脚 | `gen_netlist.py` L144 (`RAIL_BAT`, `RAIL_SYS` → BOARD_CHG); L22/L30 `board=CHG_BOARD` | 电池侧所有轨 → MAIN_PCB |
| C-2 | `U_BRIDGE` 只画了 14 个脚 (DSI 出 6 + DP 入 8), 缺 DSI D2/D3 输出、I2C、RESET、电源 | `netlist_v1.net` L196/L274 + L184-195 + L243-272 | 方案B 启用时必须补齐 → 否则改板。**决策点: 方案B 到底做不做?** |
| C-3 | `U_TEMP` 只给了 4 个脚 (SDA/SCL/VDD/GND), TMP117 真值 6 脚 (缺 **ADDR0/ADDR1**) | `netlist_v1.csv` L114-117; [0数据] 需按 TI datasheet 核 | 地址 0x48 是 ADDR 全默认 → 地址本身没问题, 但**脚要画出来**; 另需核 SCL/SDA 的脚号顺序 (图上是 pin2=SCL/pin1=SDA) |
| C-4 | `U_SUPV` 的 VDD 挂 `VDD_1V8_IO`, 而 `VDD_1V8_IO` 与被监控的 `V_SOC_IO` 是**同一 SYS 源的兄弟轨** | L393 (`U_SUPV VDD` → `RAIL_VDD_1V8_IO`), 电源树 L85-94 | 掉电时 VDD_1V8_IO 可能先掉 → 监督器掉电 → RESET 变高阻 → 10k 上拉把 RESET_N 拉高 → **电源未稳就放行复位**。建议 `U_SUPV VDD` 改挂 `SYS_PCB` (电池侧常供电) |
| C-5 | `check_kicad_net.py` 5 条门禁的盲区: 不查 ① 多脚器件的 pin 号真实性 ② 器件悬空脚 ③ 跨板 net ④ DNP 预留脚缺失 | 实测 5 条门禁在 A-1~A-5 全存在的情况下**全过** | 建议补 4 条门禁 (见 §6) |
| C-6 | `board_for()` 是**逐行 ref 查表**, 无法表达 "一个 net 跨两块板" | `gen_netlist.py` L122-148 | TS_BAT 这类跨板连接在板级层面完全不可见 → 见 §5 Q7 |
| C-7 | BOM `value` 列混装 "型号" 与 "描述" | `BOM_v1.csv`: `U_TEMP` = "TMP117 数字温度计 (I2C 地址 0x48, ±0.1°C max, 16bit)"; `CONN_CAM` = "18p@0.5mm 跨铰链连接器 (型号待结构确认)" | 拆出独立 `mpn` 列, value 只放可下单型号 |
| C-8 | 41 项采购状态是 "待分类" (占 14%), 48 项待外部 (待原厂 47 + 待JBD 1) | `gen_bom.py` 自检输出 | 投板前 "待分类" 必须归零, 否则 BOM 不可用于采购 |

---

## 5. 任务书 8 问 · 逐条判定

> 判定口径: 通过 / 不通过 / 未验, 每条给依据。

### Q1 — P9 的 4 组跨铰链通道与 pin 账是否成立 → ❌ **不通过**

**通道数成立 ✓**: `J_CHG` (充电) / `CONN_USB` (USB) / `CONN_CAM` (CSI) / `CONN_LIGHT` (DSI+光机电源) = 4 组, 与 `check_netlist` 的 "跨铰链 4 个连接器标 HINGE" 一致。

**pin 账不成立 ✗** (逐个连接器):

| 连接器 | 声明脚数 | `.net` 里实际脚数 | 缺口 | 判定 |
|---|---|---|---|---|
| `J_CHG` | 10p | **7** (pin1-7) | pin8/9/10 被 `[INVENTORY]` 跳过 (B-5) | ❌ |
| `CONN_USB` | 4p | **3** (pin1-3) | pin4 被跳过 (B-5) | ❌ |
| `CONN_CAM` | 18p | 18 | 脚数满, 但 note/页标题写 40p (B-2) | ⚠️ |
| `CONN_LIGHT` | 21p | 21 | 脚数满, 但 **0 根 GND** (A-4) + note 脚号错到 27-29 (B-3) | ❌ |

**另外**: 4 组通道里只有 `J_CHG` (2 根) 和 `CONN_USB` (1 根) 有回流地 pin,
`CONN_CAM` 只有 1 根 (要过 8 根差分), `CONN_LIGHT` **0 根** → **pin 账在 "回流地" 这个维度上不成立**。

**依据**: `netlist_v1.net` (见 §2 A-4 / B-2 / B-3 / B-5 各表); `check_netlist.py` 的两条相关门禁存在盲区 (C-5)。

---

### Q2 — `J_CHG` 1×10p@0.5mm 的载流双 pin + 回流双 pin 是否合理 → ⚠️ **部分不通过 (拓扑合理, 载流裕量不足)**

**合理的部分 ✓**:
- 载流 pin1/pin2 与回流 pin3/pin4 **物理相邻** → 环路面积最小, 布局约束正确
- 双 pin 并联分担电流 + 双 pin 并联分担回流 → 拓扑正确
- 充电路径上**不装 π 滤波** (会破坏 BQ25896 环路稳定性) ✓ 这条判断是对的

**不合理的部分 ✗ — 载流裕量** ([推算], 假设 0.5 mm FPC / AWG28 / 铜厚 0.03 mm / 铰链段 50 mm):

| 项 | 计算 | 结果 | 判定 |
|---|---|---|---|
| 单脚载流 | 0.5 mm FPC AWG28 典型 0.5 A/脚 @ ΔT=20°C | 0.75 A/脚 (1.5A ÷ 2) | ❌ **超 50%** |
| 回流脚载流 | 同上, 1.5 A 回流也只走 2 脚 | 0.75 A/脚 | ❌ 同上 |
| 接触压降 | FPC 50 mm ≈ 0.045 Ω/脚 → 并联 0.023 Ω + 连接器接触 2×20 mΩ = **0.063 Ω** | 1.5 A × 0.063 Ω = **94 mV** (3.7 V 的 2.5%) | ✓ 可接受 |
| 发热 | I²R = 1.5² × 0.063 = **142 mW** 总; 接触点占 90 mW → 每脚 45 mW → ΔT ≈ 2-3°C | ✓ 可接受 |
| 铰链段发热 | 142 mW 摊在 FPC 段, 面积大 | ✓ 可接受 |

**结论**: **发热与压降都过, 唯一卡住的是"单脚载流"**。即"发热/压降风险"本身**不成立**,
真正的问题是**电流密度超规格** (铜箔/镀层长期通流能力), 表现为长期高温降额与接触电阻漂移。

**可执行替代 (三选一, 都无需改板拓扑)**:
1. **降充电电流**: BQ25896 充电电流可编程 → 设 **1.0 A** → 0.5 A/脚 (刚好在 0.5 mm FPC 能力内);
2. **加并联脚**: `J_CHG` 10p → **12p**, 把 pin9/pin10 (现 DNP 预留) 也接成 BAT_CHG →
   4 脚并联 → 0.375 A/脚 ✓ (代价: 预留位只剩 pin8 一个);
3. **换连接器规格**: 0.5 mm pitch 但 AWG 更粗 / 或改 0.8 mm pitch / 或改板对板大电流连接器。

**推荐**: 方案 1 (改充电电流寄存器, 零 BOM 成本) + 方案 2 的变体 ——
因为 A-1 已经要求 `pin8` 留给 TS, 所以建议 **J_CHG 10p → 12p**:
```
pin1/2   BAT_CHG (载流, 2 脚并联)
pin3/4   GND (回流, 2 脚并联)
pin5     TS_BAT   ← A-1 新增
pin6     CHG_STAT
pin7     PWR_GOOD
pin8     VBUS_DET
pin9/10  BAT_CHG (第 3/4 脚并联, 方案 2 可选)
pin11/12 预留
```

---

### Q3 — 「SYS 不过铰链 + 充电电流 1.0-1.5A 跨铰链」这个拓扑是否自洽 → ✅ **通过** (含 1 条必改 + 载流见 Q2)

**自洽性论证 ✓**:
1. **方向对**: 跨铰链的是 **1.0-1.5 A 充电电流**; 而 SYS (0.55 A) 在**镜脚本地**由电池保护 IC 产生 → 不跨铰链 ✓
2. **反向方案更差**: 若把 BQ25896 挪到镜脚, 则跨铰链的变成 **VBUS 5V / 2.0 A** (更大电流) → **现状更优** ✓
3. **回流必须过铰链**: 充电电流回路跨铰链, 地回流也必须跨 → `J_CHG pin3/pin4` 双 GND ✓ 正确
4. **充电环路不能跨 π 滤波**: 已画 "铰链段不加 π 滤波" ✓ 正确 (BQ25896 环路稳定性)
5. **电池电压采样不过铰链**: `BAT_DET` 在镜脚本地 ✓ (P1 INVENTORY note 明确写了 "BAT_DET 不再跨铰链")

**发热/压降风险**: 见 Q2 —— **压降 94 mV / 发热 ΔT 2-3°C 都成立, 不是风险点;
真正的风险是单脚电流密度超规格**。

**必改 (1 条)**: **A-1 的 TS 跨铰链通道必须加**。当前 J_CHG pin8 是 DNP 预留, 直接拿来用, 零成本。

---

### Q4 — 电池 NTC → BQ25896 TS 脚的网络是否画对 (V1.4 已改: NTC 接到 `BAT_PROT_CELL`) → ❌ **不通过**

**V1.4 改对的部分 ✓**: NTC 从"悬空的 `BAT_PROT` 节点"改到真实的 `BAT_PROT_CELL` → **F1 确实修好了**,
节点名不再悬空。

**仍然错的 3 点 ✗**:

| # | 问题 | 证据 |
|---|---|---|
| 1 | **分压网络实际不存在**: `R_NTC_BAT` 第二脚悬空 (L33 的 `net` 列写错), `R_TS_PULL` 第二脚悬空 (缺 TS_BAT 那一行) | `netlist_v1.net`: 两颗都只有 `pin "1"` |
| 2 | **跨板无通道**: TS_BAT 连接镜脚的 NTC 与镜框的 U_CHG.TS, 但 J_CHG 无 TS pin | L32/L33 + J_CHG pin map |
| 3 | **参考端语义含糊**: NTC 接在 **Q1/Q2 中点 `BAT_PROT_CELL`**, 而非明确的**电芯负极 `BAT_CELL_N`** | L25 (`BAT_PROT_CELL` = Q1/Q2 中点) vs L29 (`BAT_CELL_N` = BT B- ↔ U_BATPROT B-) |

**后果**: BQ25896 TS 悬空 → 按 TI 定义判温度异常 → **不充电** (安全功能失效 + 整机不工作)。

**修复**: 见 §2 A-1 (跨板通道) + A-2 (补两行) + 参考端改接 `BAT_CELL_N`。

---

### Q5 — `TMP117` 接 I2C_A 0x48 是否与其它从设备冲突 → ✅ **通过** (附 3 条注记)

**实测**: I2C_A 网上的器件只有 2 个真实从设备:
- `U_TEMP` (TMP117) — L114/L115
- sensor 侧 (经 `CONN_CAM pin13/14` 跨铰链) — L112/L113

`check_netlist.py` 的 "U_TEMP 已定型 TMP117 (I2C_0x48)" + note 里列的 4 个地址
(sensor 0x36 / 桥接 0x50 / 充电 IC 0x12 / 光机 0x72) **均不等于 0x48** → **不冲突** ✓

**注记 (不改地址, 但要改符号)**:
1. `U_TEMP` 只给了 4 个脚 (SDA/SCL/VDD/GND); TMP117 是 6 脚 (多 **ADDR0/ADDR1**) →
   画符号时必须补, 否则地址跳变机制不存在 (地址 0x48 是 ADDR 全默认, 所以地址本身没问题);
2. 图上 SCL=`pin2` / SDA=`pin1`; **需按 TI datasheet 核对脚号顺序** ([0数据] 未核) —— 若 datasheet 是 1=SCL/2=SDA 则本图 P/N 画反;
3. **桥接芯片的 I2C 没画** (见 C-2) → 方案B 启用时 U_BRIDGE 的 I2C 要挂 I2C_B (0x50 与光机 0x72 同总线, 需再核冲突)。

---

### Q6 — `U_SUPV` 分压监督链是否真能释放 RESET_N → ❌ **不通过**

**RESET_N 网本身画得对 ✓**:
- `R_PU_RESET_N` 10k 上拉 → `VDD_1V8_IO` ✓ (L364)
- `R_SER_RESET_N` 1k + `C_RST` 100nF → τ=100 ms ✓ (L365/L366)
- `SW_RST` 复位键 → GND ✓ (L368)
- `U_SUPV` 开漏 RESET 并入同一网 → **任一路拉低都生效** ✓ (L395)
- `TP_RESET` 测试点 ✓ (L352)

**但分压监督链断了 ✗** → 见 §2 A-3:
`R_SUPV_DIV1` 的 V_SOC_IO 端悬空 → `U_SUPV.IN ≈ 0V` (只经 R_SUPV_DIV2 接地) →
**恒判欠压 → RESET_N 恒低 → SoC 永不复位释放 → 整机不上电**。

**附加风险 (C-4)**: `U_SUPV` 的 VDD 挂 `VDD_1V8_IO` (被监控轨的兄弟轨) → 掉电时序不安全。

**结论**: **❌ 不通过。** 修复 = 补齐 R_SUPV_DIV1 的 V_SOC_IO 端落网 + 导出器加网名合并 (§2 A-3),
并把 `U_SUPV VDD` 改挂 `SYS_PCB`。

---

### Q7 — `board` 板级归属规则有没有漏判 (尤其刚加的 INVENTORY 标记与 V1.4 的网名合并) → ❌ **不通过 (3 处漏判 + 1 处结构缺口)**

**漏判 1 — NTC/TS 下拉挂错板 (B-1)**:
`CHG_BOARD_REFS` 含 `R_NTC_BAT` / `R_TS_PULL` → 判 CHG_BOARD, 但物理上 NTC 贴电芯 (镜脚)。
⇒ **BOM 直接把料排到错板** (`BOM_v1.csv` L19/L20 `镜框充电板`)。

**漏判 2 — 电池侧轨被判到充电板 (C-1)**:
`board_for()` 特判 `RAIL_BAT` / `RAIL_SYS` → CHG_BOARD, 但电池 + 电池保护 IC (U_BATPROT/Q1/Q2)
在**镜脚** → L22 (`RAIL_BAT`, CHG_BOARD) 与 L23 (`U_BATPROT`, MAIN_PCB) 互相矛盾。

**漏判 3 — 跨板 net 被伪装成单板 (C-6, 致命的那一处)**:
`TS_BAT` 的两行都是 CHG_BOARD → **净结果: 板级层面完全看不出 TS_BAT 跨板**。
实测"跨板 net"只有 5 个 (`BAT` / `SYS` / `USB_D_N` / `USB_D_P` / `VDD_3V3_IO`),
而 `TS_BAT` **不在其中** —— 这正是它被判成单板的后果。

**结构缺口**: `board_for()` 是**逐行 ref 查表**, 天生无法表达 "一个 net 跨两块板"。
`check_netlist.py` 的 4 条板级门禁全是**硬编码名单** (hinge_conn / soC / chg_must / bat_must),
所以 TS_BAT 这种"新出现的跨板连接"不在任何名单里 → 门禁判不出来。

**可执行修复**:
1. `gen_netlist.py`: `R_NTC_BAT` / `R_TS_PULL` → MAIN_PCB; `RAIL_BAT` / `RAIL_SYS` → MAIN_PCB;
2. `gen_netlist.py` 新增**跨板 net 检测**: 对每个 net, 统计其各行 board; 若同时出现 CHG_BOARD 与 MAIN_PCB
   (且不是 HINGE), 则**强制要求**该 net 必须经过至少一个跨铰链连接器 pin, 否则报错;
3. `check_netlist.py` 新增门禁: **任何 net 的 CHG_BOARD 行与 MAIN_PCB 行共存时, 必须有跨铰链 pin 在该 net 里**。
   这条门禁一旦加上, **A-1 (TS_BAT 断裂) 会立刻被机械抓出来**。

---

### Q8 — BOM 的采购状态分档 + 板级归属对不对 → ❌ **不通过**

**自检通过的部分 ✓** (`gen_bom.py` 自检全过: 位号集合 / qty / 采购状态 / DNP 数 / 板级归属一致):
- 位号总数 293 = netlist 411 行去重后 ✓
- DNP 位号数 netlist ↔ BOM 一致 ✓ (但见下, 这个一致是**同义反复**)
- 板级归属三档计数与 netlist 一致 ✓

**不通过的部分 ✗**:

| # | 问题 | 证据 | 后果 |
|---|---|---|---|
| 1 | **`J_CHG` 被判成 "DNP-不装"** | `BOM_v1.csv` L11; `gen_bom.py` L99-102 (ref 级从严) | **整机唯一主跨铰链通道不装** → 样机装不起来 |
| 2 | **`CONN_USB` 被判成 "DNP-不装"** | `BOM_v1.csv` L193 (同上原因, pin4 是 DNP 预留) | **没有烧录/调试口** |
| 3 | **DNP 自检是同义反复** | `gen_bom.py` L126-129: "netlist 里有 DNP 行的 ref 数" vs "BOM 标 DNP 的 ref 数" → 按构造必然相等 | 查不出第 1/2 条 |
| 4 | **板级归属继承 netlist 的错标** | `BOM_v1.csv` L19/L20 NTC/TS 下拉 = 镜框充电板 | 贴错板 (与 B-1 同根因) |
| 5 | **跨铰链连接器只列了一侧** | 4 个连接器 qty 全 = 1 | 对插/板对板**物理上要两个** (充电板侧 + 主 PCB 侧) → 备料只买一半。需按实际形态定 (FFC 座要 2 个, 板对板 1 个型号但 2 只) |
| 6 | **value 列混装型号与描述** | `U_TEMP` value = "TMP117 数字温度计 (I2C 地址 0x48, ±0.1°C max, 16bit)" | 采购无法直接下单 |
| 7 | **"待分类" 41 项 (14%) 未归零** | `gen_bom.py` 自检输出 | BOM 不可用于投板采购 |

**采购状态分档现状** (总 293 位号):
`已定型-无源件 69 / DNP-不装 61 / 待原厂 47 / 待分类 41 / 测试点 41 / 已定型-IC 11 / 待选型 9 / 连接器 6 / 已定型-开关 5 / 已定型-LED 2 / 待JBD 1`
⇒ **必装但待外部/待分类 = 89 项 (30%)**; 投板前必须归零。

**板级归属现状**: 镜脚主 PCB 259 / 镜框充电板 24 / 跨铰链界面 10 ✓ 结构合理, 但**归到"跨铰链界面"的 10 个位号里
有 4 个连接器 + 它们的 GND/ESD/预留, 而这 10 个位号里 J_CHG 与 CONN_USB 被误判 DNP** (见上表 1/2)。

---

## 6. 我自己发现、任务书未要求的问题 (≥3 条, 本报告最重要部分)

| # | 问题 | 级别 | 一句话 | 证据锚点 |
|---|---|---|---|---|
| **X-1** | **BOM 的 ref 级 DNP 判定把 J_CHG / CONN_USB 判成 "不装"** | ★★★ | 备料时不买主跨铰链连接器和烧录口 → 样机装不起来 | `gen_bom.py` L99-102; `BOM_v1.csv` L11/L193 |
| **X-2** | **`R_SUPV_DIV1` 悬空 → U_SUPV.IN≈0V → RESET_N 永不释放** | ★★★ | 整机永远停在复位态, 上不了电 | `netlist_v1.net` SUPV_SENSE net; L390/L392 |
| **X-3** | **TS 分压网络根本没画出来** (R_NTC_BAT / R_TS_PULL 各悬空一脚) | ★★★ | BQ25896 TS 悬空 → 接上电不充电 | `netlist_v1.net` 两颗都只有 pin "1"; L33/L34 |
| **X-4** | **`CONN_LIGHT` 21 脚一个 GND 都没有** | ★★★ | 跨铰链 DSI 差分无回流地 → 眼图必炸 | `netlist_v1.net` CONN_LIGHT pin1-21 全是信号/电源 |
| **X-5** | **DP 的 4 路 AC 耦合电容被短路 + N 路错接 P 路串阻** | ★★ | 方案B 的 DP→DSI 链路隔直失效 | L242-244 / L248,256,264,272 vs CSI 的 L204/205 写法 |
| **X-6** | **裸 IC/连接器名被分配幻影脚号** (U_CHG 1/2/3、U_BATPROT 1-4、U_SUPV 1、U_BRIDGE 1/2、J_TYPE_C 1、X1 3) | ★★ | 画符号时脚号对不上 → 可能直接短路 | `netlist_v1.net` 中上述 (ref,pin) |
| **X-7** | **`[INVENTORY]` 行被整行跳过 → DNP 预留脚在 `.net` 里不存在** (J_CHG pin8/9/10、CONN_USB pin4) | ★★ | "预留位" 在 PCB 上没有焊盘 → 将来加信号要改板 | `gen_kicad_net.py` 的 `continue`; `.net` 里 J_CHG 只有 pin1-7 |
| **X-8** | **`J_CHG` 在 `.net` 里 footprint = `TBD:NET_PLACEHOLDER`** (取自 NET 行而非 CONN 行) | ★★ | 跨铰链主连接器在 KiCad 里拿不到连接器封装 | `netlist_v1.net` L10; `gen_kicad_net.py` 的 `comp()` 取首次出现的行 |
| **X-9** | **`CONN_LIGHT` 的 pin map 在 3 处互相矛盾, 且 note 引用了超出 21p 的 pin27/28/29** | ★★ | 结构按 note 选 30p / 硬件画 21p → 必返工 | L203 / L401 vs L157-201 实际连线 |
| **X-10** | **`CONN_CAM` 18p vs 40p 自相矛盾** (value / note / P5 页标题三处) | ★★ | 结构与硬件备料口径不一致 | L240 value vs note; `gen_netlist.py` PAGES["P5"] |
| **X-11** | **7 个器件悬空脚** (C_KEY_CAM/PWR/VM/VP ×1, R_NTC_BAT, R_SUPV_DIV1, R_TS_PULL) | ★★ | 按键去耦与分压链实际不存在 | `netlist_v1.net` 各器件 pin 数 < 2 |
| **X-12** | **`C_KEY_*` 按键去耦电容只有 GND 一端** → 按键 RC 滤波不存在 | ★ | 按键抖动无抑制 | L (GND net) 只有 `n1=C_KEY_x, n2=GND` |
| **X-13** | **`U_SUPV` VDD 挂被监控轨的兄弟轨 → 掉电时序不安全** | ★ | 掉电时可能"电源未稳就放行复位" | L393 + 电源树 L85-94 |
| **X-14** | **`board_for()` 无法表达跨板 net** → 新出现的跨板连接 (TS_BAT) 完全逃过门禁 | ★ | 结构性盲区 | `gen_netlist.py` L122-148 |
| **X-15** | **`check_kicad_net.py` 5 条门禁查不出 pin 号真实性 / 悬空脚 / 跨板 net / DNP 预留缺失** | ★ | A 级 5 条缺陷全部在盲区 | A-1~A-5 全部存在时 5 条门禁全过 |
| **X-16** | **`gen_bom.py` 的 DNP 自检是同义反复** | ★ | 查不出 X-1 | L126-129 |
| **X-17** | **BOM `value` 列混装型号与描述, 无独立 MPN 列** | ★ | 采购不可直接下单 | `BOM_v1.csv` U_TEMP / CONN_CAM 行 |

---

## 7. 建议的门禁补强 (可直接进 `state/check_kicad_net.py` / 新建 `state/check_schematic_rules.py`)

```python
# G1 多脚器件不得出现纯数字幻影脚
#    IC/CONN/SW/LED 的 (ref, pin) 中 pin 必须是纯数字 → 报错
#    现状会抓出: J_TYPE_C pin"1" / J_CHG pin"1" / U_CHG 1,2,3 / U_BATPROT 1-4 / U_SUPV 1 / U_BRIDGE 1,2 / X1 3

# G2 器件悬空脚
#    2 脚无源件 (R/C/L/D) 在 .net 里的 pin 数必须 == 2
#    现状会抓出: C_KEY_CAM/PWR/VM/VP, R_NTC_BAT, R_SUPV_DIV1, R_TS_PULL

# G3 跨板 net 必须过跨铰链连接器
#    同一 net 同时含 CHG_BOARD 与 MAIN_PCB 的行 → 该 net 必须含
#    J_CHG / CONN_USB / CONN_CAM / CONN_LIGHT 的 pin
#    现状会抓出: TS_BAT (A-1)

# G4 DNP 预留脚必须进 .net
#    声明 Np 的连接器, .net 里必须恰好有 N 个 pin
#    现状会抓出: J_CHG (声明 10p, 实际 7), CONN_USB (声明 4p, 实际 3)

# G5 BOM 关键器件不得标 DNP
#    跨铰链连接器 / 充电链器件 / 电池链器件 的 dnp 必须 != "DNP"
#    现状会抓出: J_CHG, CONN_USB
```

---

## 8. 自证复现命令

```bash
cd projects/smart_glasses

# ① 三条既有门禁 (基线: 全过)
python3 state/check_netlist.py    ; echo "rc=$?"   # 预期 rc=0 (28/28)
python3 state/check_kicad_net.py  ; echo "rc=$?"   # 预期 rc=0 (5/5)
python3 state/gen_bom.py          ; echo "rc=$?"   # 预期 rc=0 (自检全过)

# ② A-3 悬空脚 (R_SUPV_DIV1 / R_NTC_BAT / R_TS_PULL / C_KEY_*)
python3 - <<'EOF'
import re,collections
t=open('HW/netlist_v1.net',encoding='utf-8').read()
p=collections.defaultdict(set)
for m in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)',t): p[m.group(1)].add(m.group(2))
for r in ("R_NTC_BAT","R_TS_PULL","R_SUPV_DIV1","C_KEY_CAM","C_KEY_PWR","C_KEY_VM","C_KEY_VP"):
    print(f"  {r:14s} .net pin 数 = {len(p[r])}  {sorted(p[r])}")
EOF

# ③ A-4 CONN_LIGHT 无 GND
grep -c 'ref "CONN_LIGHT"' HW/netlist_v1.net
grep 'ref "CONN_LIGHT"' HW/netlist_v1.net | grep -c 'GND'    # 预期 0

# ④ B-6 BOM 把 J_CHG / CONN_USB 判成不装
grep -nE '^(J_CHG|CONN_USB),' HW/BOM_v1.csv
grep -n '只要有一行标 DNP' state/gen_bom.py

# ⑤ B-2 / B-3 pin 数与 pin map 矛盾
grep -n 'CONN_CAM' HW/netlist_v1.csv | grep -oE '[0-9]+p@0\.5mm|[0-9]+p 跨铰链' | sort -u
grep -n 'CONN_LIGHT' state/gen_netlist.py | head -3

# ⑥ 幻影脚 (X-6)
grep -oE '\(ref "(U_CHG|U_BATPROT|U_SUPV|U_BRIDGE|J_TYPE_C|J_CHG|X1)"\) \(pin "[0-9]+"\)' HW/netlist_v1.net | sort -u

# ⑦ A-5 DP 的 AC 电容被短路
grep -n 'C_AC_DP_A' HW/netlist_v1.csv | awk -F',' '{print $1","$2","$3","$4","$5}'
EOF
```

---

## 9. 结论与建议

1. **拓扑方向 (SYS 不过铰链 + 充电电流跨铰链) 通过**, 发热/压降**不是**风险点 (94 mV / ΔT 2-3°C),
   唯一卡点是**单脚电流密度** → 建议充电电流设 1.0 A 或加并联脚 (Q2/Q3);
2. **A 级 5 条必须闭环** 才能进 PCB: TS 跨板通道 (A-1)、TS 分压补齐 (A-2)、R_SUPV_DIV1 落网 (A-3)、
   CONN_LIGHT 加 GND (A-4)、DP AC 耦合改网 (A-5);
3. **BOM 的 DNP 判定必须改成颗级** (B-6), 否则备料会漏掉主跨铰链连接器;
4. **建议本轮先改生成器再重跑** (按项目总工指示: 不许手改生成物):
   `gen_netlist.py` (pin 名 / net 列 / board 归属 / pin map note) ·
   `gen_kicad_net.py` (网名合并 + 幻影脚 + INVENTORY 预留脚) · `gen_bom.py` (DNP 颗级 + MPN 列) ·
   `gen_schematic_pages.py` (P5 标题 40p→20p) —— 重跑后 md5 必须自洽;
5. **投板前必做 pin-centric 重整** (ISS-094 已登记): 把 411 行"连接型"网表重整成"引脚型"网表,
   本报告的 A-1~A-5 与 X-1~X-17 都可以在 pin-centric 化时一次性收敛。

**审查结论: 原理图 V1.4 **不通过**, 需按 §2 (A 级) 与 §3 (B 级) 整改后复审。**
