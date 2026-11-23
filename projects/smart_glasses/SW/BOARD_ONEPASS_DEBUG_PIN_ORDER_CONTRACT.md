# `J_DEBUG` / `J_UART` 排针 · 物理针序契约（pin1 朝向 + JTAG 线序）+ JTAG 链 SoM 侧真相

> **件号**: ISS-375（sw-lead） · **版次**: v1.0 · **落盘日**: 2026-11-24
> **状态**: **分析件 + 机器判据件**（`SW/tools/check_debug_pin_order_contract.py`） · **零写板 / 零落表 / 零改既有页 / 零挂链**
> **上游**: `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 未决项第 1 行（「板那一趟必须写死」） · **本页 = 该未决项的 sw 侧输入 + 一条闸**

---

## §0 一句话结论 + 三问回答

> **一句话结论**: ★**换官方 land 会让 `J_DEBUG` 板面【第一次】出现 pin1 方形标记 ⇒ 「哪端是 pin1」从网表约定变成实物事实; 两个候选落点几何【逐字等价】但针序【互为逆序】⇒ 必须选一条写死; 而【无论选哪条】, JTAG 链在 SoM 侧都是断的 ⇒ 「pin1 朝向」救不了救砖链, 这两件事必须一起裁** ★

### Q1 · 那一趟 `J_DEBUG` 的 pin1 朝向选 rot 90 还是 rot 270?

**答**: ★**两个候选都合法（几何等价、单边间隙同为 2.6950mm、CRIT 0.60 全过），但针序互为逆序 ⇒ 物理上必须二选一** ★。
sw-lead 的**建议** = **候选 A（rot 90 @ `(141.0450, 56.6000)`）**，理由三条（详见 §1-4）：

1. ★**现状是顺排**（现状板 `J_DEBUG` pad1 `JTAG_TCK` 在 **X 最小端** 142.2000mm）⇒ 选 A 可**保持顺排**（TCK→TMS→TDI→TDO 自小到大），**选 B 等于把现存的物理约定镜像掉** ⇒ 换 land 那一趟不需要同步改任何调试线序文档/工装/排线定义 ★
2. ★**A 的原点位移在 X 上更小**（锚点 ΔX = **-3.2550** vs B 的 **+0.5550**）⇒ 对既有丝印/装配坐标的扰动更小 ★
3. ★**B 的唯一优势 = 「pin1 在 X 最大端」符合「看装配图从板边往里数」的常见丝印朝向直觉** ⇒ 若 hw-lead 的装配图惯例要求 pin1 在内侧，选 B；**但代价 = 全部现有 JTAG 线序描述必须反转，且现状「顺排」这个已写死的约定被推翻** ★

★**归 main 裁（本单不代拍）** ★

### Q2 · JTAG 链在 SoM 侧到底通不通？

**答**: ★**不通。而且是【不落地】，不是【信号不存在】——这两句必须分开写** ★。

- ★**事实 1（不落地）**: 网表 `HW/netlist_v1.csv` 第 388/390/392/394 行，四条 `JTAG_*_SOC` 网的 **SoM 侧端点全部 = `SoC_NC`** ⇒ 板级 JTAG 链在 SoM 那一头**接不到任何 SoM 引脚**。证据等级 **[实测]** ★
- ★**事实 2（脚表口径）**: 官方逐针表 `HW/PCB/FET3572C_PIN_TABLE.csv`（**399 条数据行**）里 **`JTAG` 命中数 = 0** ⇒ 该模块的引脚表里**没有以 JTAG 命名的引出信号**。证据等级 **[实测]** ★
- ★**不能由脚表推出的那句**: 「`JTAG_TDI` 在 SoC 芯片上根本不存在」——**本单不能这么写**。逐针表覆盖的是**模块引出的引脚**，不是芯片内部信号清单 ⇒ 脚表无 JTAG 只能支持「**该模块未把 JTAG 引出来**」，不能支持「**芯片内部没有 JTAG**」。`HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行自己的原话就是二选一（「要么是 RK3572 内部命名不同，要么该信号在 FET3576-C 上不存在」）⇒ **本单按脚表实读判，只写「不落地」**。证据等级 **[实测]**（事实）+ **[推算]**（表述边界）★

### Q3 · 这跟 `ISS-344` 终裁对不上，怎么办？

**答**: ★**对不上，且是两层对不上**（详见 §3）★。

| # | 对不上的点 | 事实 | 处置 |
|---|---|---|---|
| 1 | 裁决说 `JTAG_TDI` **必需**、**板侧不许标 NC / no-connect** | 网表里 `JTAG_TDI_SOC` 的 SoM 侧就是 `SoC_NC`；且 `JTAG_TDI` 在**板上是 0 段铜**（`JTAG_TCK` 36 段 / `JTAG_TMS` 68 段 / `JTAG_TDO` 67 段） | 三条路见 §3，**只登记不代拍** |
| 2 | 裁决说 JTAG 组进 S8 布线目标 | 即便把 pin1 朝向写死，**SoM 侧仍接不到** ⇒ S3 救砖路径在**这一版 SoM 上不存在** | 见 §3 路线 ③ 的代价 |

★**要 main 回答的两件事**: ★**(a)** pin1 朝向选 A 还是 B；★**(b)** ISS-344 终裁在「SoM 侧无 JTAG 引出」这个事实下怎么改口径（三条路的代价已在 §3 算清）★

---

## §1 物理针序契约表（核心交付物）

### §1-1 逐件总表

| 件 | 现状 pad1 位置 | 现状有无**极性**标记 | 官方 land 的 pin1 标记形状 | 候选 **A** = rot 90 @ `(141.0450, 56.6000)` | 候选 **B** = rot 270 @ `(144.8550, 56.6000)` | 要挪原点（锚点 Δ，自现状 `(144.30, 58.00)`） | 裁决建议 | 落点写死值 |
|---|---|---|---|---|---|---|---|---|
| **`J_DEBUG` 1×4** | ★**X 最小端**（pad1 `JTAG_TCK` @ X=**142.2000**）★ | ★**无**（4 个 pad 全 `RECT` / 全 `SMD` / 全 0.275×0.900 ⇒ **四个长得一模一样**，板面**看不出**哪端是 pin1）★ | ★**`thru_hole rect`（pad1）** ★其余 3 个 = `thru_hole circle` ⇒ **方形 pad = 行业标准 pin1 标记** | ★**pin1 在 X 最小端**（pad1 @ X=**141.0450**）★ 四线物理线序 = ★**顺排** ★`JTAG_TCK`→`JTAG_TMS`→`JTAG_TDI`→`JTAG_TDO`（自小到大）★ | ★**pin1 在 X 最大端**（pad1 @ X=**144.8550**）★ 四线物理线序 = ★**逆排** ★`JTAG_TDO`→`JTAG_TDI`→`JTAG_TMS`→`JTAG_TCK`（自小到大）★ | A: ΔX=**-3.2550** · ΔY=**-1.4000**  <br>B: ΔX=**+0.5550** · ΔY=**-1.4000** | ★**建议 A（保持现状顺排）** ★理由见 §1-4 ⇒ **归 main 裁** | ★**`J_DEBUG` → 原点 `(141.0450, 56.6000)` · 旋转 `90°` · pin1 在 **X 最小端** · 顺排** ★（若 main 裁 B 则改为 `(144.8550, 56.6000)` / `270°` / pin1 在 X 最大端 / 逆排） |
| **`J_UART` 1×2** | ★**X 最小端**（pad1 `UART_TX` @ X=**18.6400**）★ | ★**无**（2 个 pad 全 `RECT` / 全 `SMD` / 全 0.275×0.900）★ | ★**`thru_hole rect`（pad1）** ★其余 1 个 = `thru_hole circle` | ★**pin1 在 X 最小端**（pad1 `UART_TX` @ X=**18.2550**）★ 线序 = ★**顺排**（`UART_TX`→`UART_RX`）★ | ★**pin1 在 X 最大端**（pad1 `UART_TX` @ X=**19.5250**）★ 线序 = ★**逆排**（`UART_RX`→`UART_TX`）★ | A: ΔX=**-2.4850** · ΔY=**-1.4000**  <br>B: ΔX=**-1.2150** · ΔY=**-1.4000** | ★**建议 A（保持现状顺排，与 `J_DEBUG` 同向）** ★ ⇒ **归 main 裁** | ★**`J_UART` → 原点 `(18.2550, 68.6000)` · 旋转 `90°` · pin1 在 **X 最小端** · 顺排** ★（若 main 裁 B 则改为 `(19.5250, 68.6000)` / `270°` / pin1 在 X 最大端 / 逆排） |

★**注 1（`J_UART` 候选原点的来源与状态）**: `J_UART` 的两个候选原点 ★**不是 MECH 已定值**★ —— `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 只覆盖 `J_DEBUG`，`MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` 的 F-6/F-7 明写「`J_UART` 的 X 向开口尺寸必须等真实型号/位置定版后重算」⇒ ★**本页的 `J_UART` 候选原点是本单按「与现状铜箔 X 中心 18.89 对齐 + pitch 1.27」推出来的**（18.89 ∓ 0.635 = 18.255 / 19.525；Y 沿用现状 pad 行 68.60），证据等级 **[推算]** ★ ⇒ **须 hw-lead 认可后才成立** ★
★**注 2（`J_UART` 本页不给间隙结论）**: `MECH` 侧 `J_UART` 的开口窗口**未定义** ⇒ 沙盒测出的 `clr_x` 对 `J_UART` **无意义** ⇒ ★**本页只写 `J_UART` 的针序契约，不写 `J_UART` 的间隙结论** ★
★**注 3（锚点 Δ 的可比性）**: 现状 `J_DEBUG` 的封装锚点在 `(144.30, 58.00)` 但 pad 行在 **Y=56.60**（自定义 SMD land，锚点与 pad 行不重合）；官方 land 的锚点 = **pad1 本身** ⇒ ★**锚点 Δ 只是账务数**；真正可比的是 **pad 行 / 铜箔带**：现状铜箔 X 带 = `142.0625..143.8375`（宽 1.7750），候选 A/B 铜箔 X 带 = **`140.5450..145.3550`（宽 4.8100，两候选逐字相同）**，pad 行 Y 现状与候选**都是 56.60** ★

### §1-2 官方 land 实读（盘上 `.kicad_mod`，不抄文档）

`/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod`：

```
(pad "1" thru_hole rect  (at 0 0)     (size 1 1) (drill 0.65) (layers "*.Cu" "*.Mask"))
(pad "2" thru_hole circle (at 0 1.27)  (size 1 1) (drill 0.65) (layers "*.Cu" "*.Mask"))
(pad "3" thru_hole circle (at 0 2.54)  (size 1 1) (drill 0.65) (layers "*.Cu" "*.Mask"))
(pad "4" thru_hole circle (at 0 3.81)  (size 1 1) (drill 0.65) (layers "*.Cu" "*.Mask"))
```

`PinHeader_1x02_P1.27mm_Vertical.kicad_mod`：`pad "1" thru_hole rect (at 0 0)` + `pad "2" thru_hole circle (at 0 1.27)` ⇒ **1×2 同样有方形 pin1**。
证据等级 **[实测]**。复跑：`grep -nE '\(pad "|thru_hole|drill' <land 路径>`

### §1-3 两个候选的逐 pad 实测（沙盒 S1/S2，板副本，真板零改动）

★**S1 = `J_DEBUG` rot 90 @ `(141.0450, 56.6000)`**（`logs/iss375/meas_J_DEBUG_s1_jdebug_rot90.json`）★

| pad | 绝对 X | 绝对 Y | 形状 | 属性 | 尺寸 | 钻孔 | net |
|---|---|---|---|---|---|---|---|
| **1** | **141.0450** | 56.6000 | ★**RECT** ★（pin1 标记） | PTH | 1.0×1.0 | 0.65 | ★`JTAG_TCK` ★ |
| 2 | 142.3150 | 56.6000 | CIRCLE | PTH | 1.0×1.0 | 0.65 | `JTAG_TMS` |
| 3 | 143.5850 | 56.6000 | CIRCLE | PTH | 1.0×1.0 | 0.65 | `JTAG_TDI` |
| 4 | 144.8550 | 56.6000 | CIRCLE | PTH | 1.0×1.0 | 0.65 | `JTAG_TDO` |

★**S2 = `J_DEBUG` rot 270 @ `(144.8550, 56.6000)`**（`logs/iss375/meas_J_DEBUG_s2_jdebug_rot270.json`）★

| pad | 绝对 X | 绝对 Y | 形状 | 属性 | net |
|---|---|---|---|---|---|
| 4 | 141.0450 | 56.6000 | CIRCLE | PTH | `JTAG_TDO` |
| 3 | 142.3150 | 56.6000 | CIRCLE | PTH | `JTAG_TDI` |
| 2 | 143.5850 | 56.6000 | CIRCLE | PTH | `JTAG_TMS` |
| **1** | **144.8550** | 56.6000 | ★**RECT** ★（pin1 标记） | PTH | ★`JTAG_TCK` ★ |

★**S3A/S3B = `J_UART`**（`logs/iss375/meas_J_UART_s3a_juart_rot90.json` / `..._s3b_juart_rot270.json`）★

| 候选 | pad1 | pad2 | 铜箔 X 带 | fab 外框 X | courtyard X |
|---|---|---|---|---|---|
| A (rot 90 @ `18.2550, 68.6000`) | ★`UART_TX` @ X=**18.2550** ★RECT | `UART_RX` @ X=19.5250 | `17.7550..20.0250`（宽 2.2700） | `16.1698..21.6102` | `17.0900..20.6900` |
| B (rot 270 @ `19.5250, 68.6000`) | ★`UART_TX` @ X=**19.5250** ★RECT | `UART_RX` @ X=18.2550 | `17.7550..20.0250`（宽 2.2700） | `16.1698..21.6102` | `17.0900..20.6900` |

### §1-4 S1 ↔ S2 对照：**几何等价** 与 **针序互逆**，是【两件独立的事】

| 量 | S1 (rot 90) | S2 (rot 270) | 结论 |
|---|---|---|---|
| 铜箔 X 带 | `140.5450..145.3550` | `140.5450..145.3550` | ★**逐字相同** ★ |
| 铜箔 X 宽 | **4.8100** | **4.8100** | ★**逐字相同** ★ |
| fab 外框 X | `139.5869..146.3131`（宽 6.7262） | `139.5869..146.3131`（宽 6.7262） | ★**逐字相同** ★ |
| courtyard X | `139.8800..146.0200`（宽 6.1400） | `139.8800..146.0200`（宽 6.1400） | ★**逐字相同** ★ |
| 单边间隙（对 `ISS-371` 开口口径） | 左 **2.6950** / 右 **2.6950** ⇒ 最差 2.3950 ≥ CRIT 0.60 ✔ | 左 **2.6950** / 右 **2.6950** ⇒ 最差 2.3950 ≥ CRIT 0.60 ✔ | ★**逐字相同，两候选都过** ★ |
| pad 绝对 X 集合 | `{141.0450, 142.3150, 143.5850, 144.8550}` | `{141.0450, 142.3150, 143.5850, 144.8550}` | ★**逐字相同** ★ |
| ★**pad→X 序** ★ | `1(TCK) → 2(TMS) → 3(TDI) → 4(TDO)` | `4(TDO) → 3(TDI) → 2(TMS) → 1(TCK)` | ★★**互为逆序** ★★（**不是互等** ⇒ 这才是「必须二选一」的根据）★★ |

⇒ ★**这两件事必须分开证明**: ★**「几何完全等价」⇒ 结构/装配/开口层面选哪条都行**; ★**「针序互为逆序」⇒ 电气/线序层面选哪条都不行，必须选** ★
★**且: 现状板面无 pin1 标记 ⇒ 换 land 之后「哪端是 pin1」第一次变成【实物可见】 ⇒ 选错 = 排线插反 = 实物层面的 JTAG 不通** ★

### §1-5 落点写死值（那一趟直接抄）

> ★**若 main 裁 A（建议）**: ★
> - `J_DEBUG` → 原点 **`(141.0450, 56.6000)`** · 旋转 **`90`** · ★**pin1 在 X 最小端** ★ · 线序 **顺排**（TCK→TMS→TDI→TDO）
> - `J_UART` → 原点 **`(18.2550, 68.6000)`** · 旋转 **`90`** · ★**pin1 在 X 最小端** ★ · 线序 **顺排**（TX→RX）
>
> ★**若 main 裁 B**: ★
> - `J_DEBUG` → 原点 **`(144.8550, 56.6000)`** · 旋转 **`270`** · ★**pin1 在 X 最大端** ★ · 线序 **逆排**
> - `J_UART` → 原点 **`(19.5250, 68.6000)`** · 旋转 **`270`** · ★**pin1 在 X 最大端** ★ · 线序 **逆排**
>
> ★**两候选的「pad1 方形标记」位置必须与「线序」同时写死** ⇒ 只写旋转角不写线序 = 没写死 ★

### §1-6 机器可读契约块（`SW/tools/check_debug_pin_order_contract.py` 解析这一块）

```json iss375_contract
{
  "candidates": {
    "J_DEBUG": {
      "rot90":  {"origin_mm": [141.0450, 56.6000], "pin1_end": "X_MIN", "order_label": "顺排", "order_by_x": ["JTAG_TCK", "JTAG_TMS", "JTAG_TDI", "JTAG_TDO"]},
      "rot270": {"origin_mm": [144.8550, 56.6000], "pin1_end": "X_MAX", "order_label": "逆排", "order_by_x": ["JTAG_TDO", "JTAG_TDI", "JTAG_TMS", "JTAG_TCK"]}
    },
    "J_UART": {
      "rot90":  {"origin_mm": [18.2550, 68.6000], "pin1_end": "X_MIN", "order_label": "顺排", "order_by_x": ["UART_TX", "UART_RX"]},
      "rot270": {"origin_mm": [19.5250, 68.6000], "pin1_end": "X_MAX", "order_label": "逆排", "order_by_x": ["UART_RX", "UART_TX"]}
    }
  },
  "current": {
    "J_DEBUG": {"pads": 4, "pad1_x": 142.2000, "pin1_end": "X_MIN", "pad1_marker": false, "pad_shape": "RECT", "pad_attr": "SMD", "net_by_pad": {"1": "JTAG_TCK", "2": "JTAG_TMS", "3": "JTAG_TDI", "4": "JTAG_TDO"}},
    "J_UART":  {"pads": 2, "pad1_x": 18.6400,  "pin1_end": "X_MIN", "pad1_marker": false, "pad_shape": "RECT", "pad_attr": "SMD", "net_by_pad": {"1": "UART_TX", "2": "UART_RX"}}
  },
  "land": {
    "1x04": {"fp": "PinHeader_1x04_P1.27mm_Vertical", "pad1_shape": "thru_hole rect", "other_shape": "thru_hole circle", "drill": 0.65},
    "1x02": {"fp": "PinHeader_1x02_P1.27mm_Vertical", "pad1_shape": "thru_hole rect", "other_shape": "thru_hole circle", "drill": 0.65}
  },
  "jtag_soc_side": {
    "JTAG_TCK_SOC": "SoC_NC",
    "JTAG_TMS_SOC": "SoC_NC",
    "JTAG_TDI_SOC": "SoC_NC",
    "JTAG_TDO_SOC": "SoC_NC"
  },
  "verdict": {"pin1_orientation": "rot90", "decided_by": "main", "sw_lead_recommendation": "rot90"}
}
```

---

## §2 JTAG 链的 SoM 侧真相

### §2-1 网表侧逐条实读（`HW/netlist_v1.csv`）

| 网表行号 | 网名 | 网表「另一端」列（= SoM 侧端点） | 对端器件 | 证据 |
|---|---|---|---|---|
| **388** | `JTAG_TCK_SOC` | ★**`SoC_NC`** ★ | `R_JTAG_TCK` | **[实测]** |
| **390** | `JTAG_TMS_SOC` | ★**`SoC_NC`** ★ | `R_JTAG_TMS` | **[实测]** |
| **392** | `JTAG_TDI_SOC` | ★**`SoC_NC`** ★ | `R_JTAG_TDI` | **[实测]** |
| **394** | `JTAG_TDO_SOC` | ★**`SoC_NC`** ★ | `R_JTAG_TDO` | **[实测]** |

板侧链（`HW/netlist_v1_pins.csv` 第 202-205 行）：`J_DEBUG.pin1=JTAG_TCK` · `pin2=JTAG_TMS` · `pin3=JTAG_TDI` · `pin4=JTAG_TDO`（**pin1=TCK 的约定写在网表里，这就是现状板面「没有 pin1 标记」时唯一能定 pin1 的依据**）。

复跑：`sed -n '388,395p' HW/netlist_v1.csv`

### §2-2 官方脚表 399 行实读（`HW/PCB/FET3572C_PIN_TABLE.csv`）

- 文件 = **1 行表头 + 399 行数据**（`conn,num,ball,signal,gpio,vol,desc,default_function`）
- ★**`JTAG` 命中数 = 0**（大小写不敏感，全表扫）★ ⇒ **该模块逐针表里没有 JTAG 同名信号**
- 证据等级 **[实测]**。复跑：`grep -icE "JTAG" HW/PCB/FET3572C_PIN_TABLE.csv` ⇒ `0`

### §2-3 `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行原话（读，不改）

> | `JTAG_TCK` | ★**逐针表里没有同名/后缀相同的信号** ⇒ 要么是 RK3572 内部命名不同, 要么该信号在 FET3576-C 上不存在 (⇒ 需换引脚或换板) |
> | `JTAG_TDI` | （同上句） |
> | `JTAG_TDO` | （同上句） |
> | `JTAG_TMS` | （同上句） |

⇒ ★**这四行本身是二选一的措辞（命名不同 vs 信号不存在）⇒ 本单不替它选边；本单只把它【可证的那一半】坐实** ★

### §2-4 ★「不落地」vs「信号不存在」——两句差别很大，本单只写第一句 ★

| 表述 | 本单能不能下 | 依据 |
|---|---|---|
| ★**「JTAG 链在 SoM 侧不落地」**（网表 `SoC_NC` ⇒ 板级接不到任何 SoM 引脚） ★ | ★**能，下** ★ | **[实测]** 网表 388/390/392/394 行 + 脚表 `JTAG` 命中 0 + `HW/PCB/SOM_PIN_MAPPING.md:48-51` |
| ★**「`JTAG_TDI` 在 SoC 芯片上不存在」** ★ | ★**不能，下不得** ★ | 逐针表覆盖的是**模块引出的引脚**，不是芯片内部信号清单 ⇒ 脚表无 JTAG 只支持「**该模块未把 JTAG 引出**」；脚表无法区分「芯片内部命名不同」与「芯片内部没有该功能」 |

★**一句话（可抄进任何一页的合规表述）**: ★**「在 FET3576-C 这版 SoM 上，JTAG 四线在板级网表里落到 `SoC_NC` 占位，且该模块的 399 行逐针表里没有任何 JTAG 同名信号 ⇒ JTAG 链在 SoM 侧不落地；芯片内部是否具备 JTAG 功能，本单未取得证据，不作断言。」** ★

### §2-5 板面铜箔侧的旁证（`JTAG_TDI` 是 0 段）

`JTAG_TCK` **36** 段 · `JTAG_TMS` **68** 段 · `JTAG_TDO` **67** 段 · ★**`JTAG_TDI` 0 段** ★ · `UART_TX` 234 段 · `UART_RX` 0 段（**均为 `[实测]`**，实跑 `pcbnew` 数 `GetTracks()`）。
⇒ ★**`JTAG_TDI` 在板上是 0 段铜**，这与 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` ISS-344 终裁「`JTAG_TDI` = 必需 · 进 S8 布线目标 · 板侧不许标 NC」**直接冲突**（§3）。

---

## §3 与既有裁决的关系（只登记 + 给代价 · 不代拍）

### §3-1 冲突登记

| 项 | 既有裁决（`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` ISS-344 终裁块，读，不改） | 本单实测事实 | 冲突性质 |
|---|---|---|---|
| C-1 | `JTAG_TDI` = ★**必需** ★ · 「进 S8 布线目标 · **板侧不许标 NC / no-connect**」 | 网表 `JTAG_TDI_SOC` 的 SoM 侧 = `SoC_NC`；且 `JTAG_TDI` 板面 **0 段铜** | ★**裁决的「不许标 NC」与网表的 `SoC_NC` 占位对不上** ★ |
| C-2 | ISS344-CORR 分级订正把 `JTAG_TDI` 从「可悬空候选」升为「必需」 | ISS-344 自己给的判据订正写明「调试口/预留位不因固件零引用而构成可悬空」 | 裁决内部**逻辑自洽**，但其前提「SoC 侧有 JTAG 可接」**本单证伪** |
| C-3 | `SW/FLASH_AND_VERSION.md` 救砖 4 级：S1→S2→★**S3 = JTAG** ★→S4 返厂 | SoM 侧不落地 ⇒ **S3 在这一版 SoM 上不可执行** | ★**S3 事实上不存在** ★ |

### §3-2 三条路 + 代价 + **要谁回答什么**

| 路线 | 动作 | 代价 | ★**要谁回答什么** ★ |
|---|---|---|---|
| ★**① 改裁决口径** ★ | 把 `JTAG_TDI`（乃至 JTAG 四线组）从「必需」降级为「**悬空候选 / 条件式**」，与脚表一致 | ★**代价 1**: 与 ISS-344 终裁**正面冲突** ⇒ 需 main **重开裁**（不得由 sw-lead 自行改写）<br>★**代价 2**: `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` §0/§Q1/§L 行的分级投影要连带改（该页有 5 处 ISS344-CORR 块）<br>★**代价 3**: `SW/FLASH_AND_VERSION.md` 的 4 级救砖表 + `SW/EVT_TEMPLATE.md:503`「S2 连续失败 2 次 → 必须升级 S3」的硬规则**失去执行对象** ⇒ 须同步降级为「S3 不可用 ⇒ 直接 S4」<br>★**代价 4（最小）**: 板那一趟**不用动** `J_DEBUG` 的线序设计 | ★**要 main 回答**: ★**「在 SoM 侧无 JTAG 引出的事实下，ISS-344 对 `JTAG_TDI` 的『必需』分级是否改口径；若改，改成什么，以及 `SW/FLASH_AND_VERSION.md` 的 S3 条目如何降级」** ★ |
| ★**② 改网表** ★ | 把四条 `JTAG_*_SOC` 的 SoM 侧从 `SoC_NC` 改到某个真 SoM 引脚 | ★**这条路当前走不通** ★: 脚表 399 行里**没有 JTAG 同名信号** ⇒ **没有可指向的脚**<br>★**代价 1**: 必须先定「SoM 侧 JTAG 怎么引出」的前置方案（换 SoM 型号 / 原厂加引脚 / 走别的调试口）⇒ **这不是改网表能单独完成的**<br>★**代价 2**: 改网表 = **落表**动作 ⇒ 违反本单「零落表」边界，须由 main 在落表窗口内走流程<br>★**代价 3**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 全部要动 ⇒ 影响所有既有闸的基线 | ★**要 main 回答**: ★**「是否启动『SoM 侧 JTAG 引出方案』这条前置工作；若是，归 hw-lead 出方案、main 决定是否落表；在方案落地前，`JTAG_TDI` 的分级先按路线 ① 走还是先挂着」** ★ |
| ★**③ 改 SoM 选型 / 换板** ★ | 接受「该 SoM 不引 JTAG」，放弃 S3 软救砖路径 | ★**代价 1（最大）**: 量产眼镜变砖 ⇒ 只能 **S4 返厂换件**，返修成本与周期全压在产线<br>★**代价 2**: `SW/EVT_TEMPLATE.md` 的救砖升级硬规则 + `SW/S2_BOARD_TEST_CHECKLIST.md` 的 S3 步骤全部作废<br>★**代价 3**: 与「板只改一次」的约束**直接冲突** ⇒ 若要走这条路，**必须赶在板那一趟之前定**，否则板做出来还得再改一次<br>★**代价 4**: 需重跑 SoM 选型打分（`state/_soc_score_15.py` 一类） | ★**要 main 回答**: ★**「是否接受『放弃 S3 救砖、只留 S4 返厂』作为本版方案；若不接受，是否用路线 ② 在板那一趟之前把 SoM 侧 JTAG 引出补上」** ★ |

★**sw-lead 的排序建议（供 main 参考，不代拍）**: ★**代价从低到高 = ① < ② < ③** ★；★**且 ① 与 ③ 可以在同一次裁决里一起落**（裁决口径降级 + 同时决定要不要投 ② 的前置工作）★；★**唯一必须在板那一趟之前定死的是「pin1 朝向」（§1），因为它是纯落点写死、不依赖 SoM 侧结论** ★

### §3-3 追加式订正块（**本单不改既有页面一个字**；以下三条供 main 决定是否往既有页面落）

> ★**订正块 A · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 未决项第 1 行的「X 挪 3.2550」只对 rot 90 成立** ★
> 原文写「两条都要求原点从 `(144.30, 58.00)` 挪掉（**X 挪 3.2550** / Y 挪 1.4000）」。
> 本单实算：候选 A 锚点 Δ = **(ΔX -3.2550, ΔY -1.4000)**；候选 B 锚点 Δ = **(ΔX +0.5550, ΔY -1.4000)**。
> ⇒ ★**3.2550 只对应 A**；B 是 **+0.5550**。证据等级 **[实测]**（锚点读数 `144.30, 58.00` / `141.0450, 56.6000` / `144.8550, 56.6000`）。
> ⇒ **另注**：两候选的**铜箔 X 带**逐字相同（`140.5450..145.3550`）⇒ 锚点 Δ 是账务数，真正的结构判据是铜箔带 + 单边间隙（两候选均 2.6950/2.6950，全过）。
> ★**归属**: `MECH` 页，**本单不落**，请 main 决定是否转达 hw-lead 订正 ★

> ★**订正块 B · 沙盒 measure 脚本 `has_polarity_marker` 字段的定义过宽** ★
> `tmp/iss375_sbx/iss375_measure.py` 旧定义 = 「任一 pad 形状 ≠ CIRCLE」⇒ 现状全 `RECT` 的 SMD 板被判成 `True`（**假阳性**）。
> 正确判据 = 「**pad1 的形状与其余 pad 不同**」⇒ 现状板 = `False`（无标记）、官方 land = `True`（pad1 RECT / 其余 CIRCLE）。
> ⇒ ★**本页 §1 表用的就是这个正确判据**；`SW/tools/check_debug_pin_order_contract.py` 的 D0/D1 也按正确判据实现。证据等级 **[实测]** ★

> ★**订正块 C · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` ISS-344 终裁与 §2.4 事实的冲突（§3-1 C-1）** ★
> 终裁原文「`JTAG_TDI` = 必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect」，与本单实测「`JTAG_TDI_SOC` 的 SoM 侧 = `SoC_NC` 且 `JTAG_TDI` 板面 0 段铜」冲突。
> ⇒ **本单不代拍**，按 §3-2 三条路登记代价，等 main 裁。证据等级 **[实测]** ★

---

## §4 证据等级 + 边界自证

### §4-1 判据句（规则）与事实句（数据）分列

★**判据句** ★
- 判据 1: 官方 land 的 **pad1 标记形状**以**盘上 `.kicad_mod` 实读**为准，**不许写死**「pad1 是 rect」。
- 判据 2: 现状板面 pad1 位置与有无极性标记**以脚本实读板**为准，**不许写死**「现状是顺排」。
- 判据 3: 两个候选的 pad→X 序**必须由 KiCad 自己的 `FOOTPRINT.SetOrientationDegrees` 算出**，**不许手算旋转矩阵**；且两序**必须互为逆序**，互等即判红。
- 判据 4: 页里写的 pin1 朝向**必须与判据 3 算出来的**一致。
- 判据 5: 网表侧 JTAG 四线的 SoM 侧端点**必须实读**，`SoC_NC` **不许写死成常量**。
- 判据 6: 页 §2 的表述**不得与 `HW/PCB/SOM_PIN_MAPPING.md` 的结论冲突**。
- 判据 7: 板指纹三项（md5 / mtime / size）**不得变动**。
- 判据 8: 证据等级只用 **五级白名单**（`[官网]` `[实测]` `[媒体]` `[推算]` `[0数据]`）；**零挂起措辞**；判据句与事实句分开；**零挂链**。

★**事实句** ★
- **[实测]** 现状 `J_DEBUG`: pad1 `JTAG_TCK` @ X=**142.2000**（X 最小端）；4 pad 全 `RECT`/`SMD`/0.275×0.900 ⇒ **无 pin1 极性标记**。
- **[实测]** 现状 `J_UART`: pad1 `UART_TX` @ X=**18.6400**（X 最小端）；2 pad 全 `RECT`/`SMD` ⇒ **无 pin1 极性标记**。
- **[实测]** 官方 1×4 land: `pad "1" thru_hole rect` @ `(0 0)`，`pad "2"/"3"/"4" thru_hole circle` @ `(0 1.27)/(0 2.54)/(0 3.81)`，全 `size 1 1` `drill 0.65`；官方 1×2 land: `pad "1" thru_hole rect` @ `(0 0)`，`pad "2" thru_hole circle` @ `(0 1.27)`。
- **[实测]** 候选 A（rot 90 @ `141.0450, 56.6000`）: pad1 `JTAG_TCK` @ X=**141.0450**（X 最小端）· 顺排 · 铜箔 X 宽 **4.8100**（`140.5450..145.3550`）· fab X `139.5869..146.3131` · courtyard X `139.8800..146.0200` · 单边间隙 **2.6950/2.6950**。
- **[实测]** 候选 B（rot 270 @ `144.8550, 56.6000`）: pad1 `JTAG_TCK` @ X=**144.8550**（X 最大端）· 逆排 · 铜箔 X 宽 **4.8100**（同带）· fab X 同 · courtyard X 同 · 单边间隙 **2.6950/2.6950**。
- **[实测]** `J_UART` 候选 A/B（rot 90 @ `18.2550, 68.6000` / rot 270 @ `19.5250, 68.6000`）: pad1 `UART_TX` @ X=**18.2550** / **19.5250**；铜箔 X 带 `17.7550..20.0250`（宽 2.2700）两候选逐字相同。
- **[实测]** 网表 `HW/netlist_v1.csv` 第 **388/390/392/394** 行: `JTAG_TCK_SOC`/`JTAG_TMS_SOC`/`JTAG_TDI_SOC`/`JTAG_TDO_SOC` 的 SoM 侧端点**全部 = `SoC_NC`**。
- **[实测]** `HW/PCB/FET3572C_PIN_TABLE.csv` = 1 表头 + **399** 数据行，`JTAG` 命中 **0**。
- **[实测]** `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行: JTAG 四信号均为「逐针表里没有同名/后缀相同的信号 ⇒ 要么是 RK3572 内部命名不同，要么该信号在 FET3576-C 上不存在」。
- **[实测]** 板面铜箔段数: `JTAG_TCK` 36 · `JTAG_TMS` 68 · `JTAG_TDO` 67 · ★**`JTAG_TDI` 0** ★ · `UART_TX` 234 · `UART_RX` 0。
- **[推算]** `J_UART` 两个候选原点（`18.2550` / `19.5250`, Y `68.6000`）= 按「与现状铜箔 X 中心 18.89 对齐 + pitch 1.27」推出，**MECH 未定** ⇒ 须 hw-lead 认可。
- **[推算]** 候选 A 的锚点 Δ = **(-3.2550, -1.4000)**；候选 B 的锚点 Δ = **(+0.5550, -1.4000)**（自现状锚点 `(144.30, 58.00)`）。
- **[0数据]** SoC 芯片内部是否具备 JTAG 功能 ⇒ **本单无证据**（逐针表不覆盖芯片内部信号清单）⇒ **不作断言**。
- **[0数据]** `J_UART` 的 X 向开口窗口 ⇒ MECH 侧未定义 ⇒ **本页不给 `J_UART` 间隙结论**。
- **[媒体]** 无（本单未引任何媒体源）。
- **[官网]** 无（本单未引任何官网规格页；官方 land 与官方逐针表均为**盘上本地文件实读**，按 `[实测]` 记）。

### §4-2 边界自证

| 边界 | 自证 | 结果 |
|---|---|---|
| ★**零写板** ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb` + `stat -c '%y %s'`（开工前 / 交卷后各一次） | md5 **`611b869e13518c3c023fb178f91a0075`** · mtime **`2026-11-06 07:07:17.362193413`** · size **`4940213`** —— **三项与基线一致** |
| ★**零落表** ★ | `md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` | **`6aee500e60ba0732f83a9cf557ba90ab`** / **`9174309df1ec9411ac8e8d9e80ee386a`** / **`5b9993992405904a60ac96a020b375d8`** —— **三项与基线一致** |
| ★**零改既有闸** ★ | `SW/tools/timing_check.py` / `SW/tools/check_sw_zero_copper_grade_consistency.py` / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` md5 | 全部与开工前一致（本单只**新建** `SW/tools/check_debug_pin_order_contract.py`，**未改**既有闸一字） |
| ★**零改既有页面正文** ★ | `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` / `SW/FLASH_AND_VERSION.md` / `HW/PCB/SOM_PIN_MAPPING.md` md5 | 全部与开工前一致 ⇒ **订正意见一律走 §3-3 追加式订正块，落在本页** |
| ★**零挂链** ★ | `grep -c check_debug_pin_order_contract state/gate_check.py` | **0** ⇒ 新闸**未**挂进 `state/gate_check.py`（挂不挂归 main） |
| ★**沙盒只落两处** ★ | 本单新增文件清单 | 只落 `tmp/iss375_sbx/` 与 `logs/iss375/`（沙盒）+ 本单三件交付物 + `state/fragments/sw.yaml`（分片） |
| ★**不自签台账** ★ | `state/issue_log.yaml` | **未改** ⇒ 由 main 签收 |
| ★**零外发** ★ | 邮件/询价/问询/采购 | **零外发** ⇒ 全部靠本机盘上实读 + 自查；缺口写 **[0数据]** + 降级方案 |
| ★**不代拍** ★ | 页内所有裁决项 | pin1 朝向、ISS-344 口径修改 ⇒ 均标「归 main 裁」并附代价与「要谁回答什么」 |

### §4-3 复跑命令（本页全部数字的出处）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# 板面逐 pad 实读 (现状)
bash state/pcbnew_py.sh tmp/iss375_sbx/iss375_measure.py HW/PCB/demo_mainboard.kicad_pcb J_DEBUG
bash state/pcbnew_py.sh tmp/iss375_sbx/iss375_measure.py HW/PCB/demo_mainboard.kicad_pcb J_UART

# 两个候选 (板副本, 真板零改动)
bash state/pcbnew_py.sh tmp/iss375_sbx/iss375_build.py tmp/iss375_sbx/s1_jdebug_rot90.kicad_pcb \
     J_DEBUG PinHeader_1x04_P1.27mm_Vertical 141.0450 56.6000 90 1:JTAG_TCK 2:JTAG_TMS 3:JTAG_TDI 4:JTAG_TDO
bash state/pcbnew_py.sh tmp/iss375_sbx/iss375_build.py tmp/iss375_sbx/s2_jdebug_rot270.kicad_pcb \
     J_DEBUG PinHeader_1x04_P1.27mm_Vertical 144.8550 56.6000 270 1:JTAG_TCK 2:JTAG_TMS 3:JTAG_TDI 4:JTAG_TDO
bash state/pcbnew_py.sh tmp/iss375_sbx/iss375_measure.py tmp/iss375_sbx/s1_jdebug_rot90.kicad_pcb  J_DEBUG
bash state/pcbnew_py.sh tmp/iss375_sbx/iss375_measure.py tmp/iss375_sbx/s2_jdebug_rot270.kicad_pcb J_DEBUG

# 官方 land (盘上实读)
grep -nE '\(pad "|thru_hole|drill' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod

# 网表 + 脚表
sed -n '388,395p' HW/netlist_v1.csv
grep -icE "JTAG" HW/PCB/FET3572C_PIN_TABLE.csv

# 既有裁决 (读, 不改)
grep -nE "JTAG_TDI|必需|可悬空" SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md | head -8
sed -n '48,51p' HW/PCB/SOM_PIN_MAPPING.md

# 边界
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
grep -c check_debug_pin_order_contract state/gate_check.py
```

★**沙盒留证路径**: `tmp/iss375_sbx/`（`iss375_build.py` · `iss375_measure.py` · `iss375_run.sh` · `s1_jdebug_rot90.kicad_pcb` · `s2_jdebug_rot270.kicad_pcb` · `s3a_juart_rot90.kicad_pcb` · `s3b_juart_rot270.kicad_pcb`）· `logs/iss375/`（6 份 `meas_*.json` + `iss375_sandbox_raw.log`）★

---

> ★**本单不做的事（明写，避免下游误读）**: 不改板 · 不落表 · 不改既有闸 · 不改既有页面正文 · 不挂新闸 · 不签台账 · 不外发 · **不代 main 拍「pin1 朝向」与「ISS-344 口径」两个裁决** ★
> ★**要 main 回的两件事**: ★**(1) `J_DEBUG`/`J_UART` 的 pin1 朝向选 rot 90（建议）还是 rot 270 —— 一句话即可，本页 §1-5 已备好两套写死值** ★; ★**(2) ISS-344 终裁在「SoM 侧无 JTAG 引出」下怎么改口径 —— 走 §3-2 的 ①/②/③ 哪条（或 ①+③ 组合）** ★

---

## 【追加式订正 (2026-11-24 02:5x · sw-lead · ISS-375 cont2)】闸的真 bug 修了 + 两处判据口径精化

★**本页正文一字未改** (本段是纯追加) ★ · ★**页内全部数字与本段无冲突** (板 md5 / mtime / size 三项未动, 板指纹仍为 `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`) ★

★**① 本单新闸 `SW/tools/check_debug_pin_order_contract.py` 的一个真 bug 已修 (修, 不是重写)★**
- **症状**: `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py` ⇒ `AttributeError: 'SwigPyObject' object has no attribute 'FootprintLoad'` ⇒ rc≠0 ⇒ 闸全红。
- **本机实测根因 (与派活材料里记的「`-c` 入口 vs 脚本文件入口」不同, 以本机实测为准)**: 本机 KiCad 10.0.8 的 `pcbnew.py:24225` 实现是 `return plug.FootprintLoad(libname,name,preserveUUID)`, 而 `plug` 是裸 `SwigPyObject` **没有 `FootprintLoad` 成员** ⇒ ★**写成 `.py` 文件再跑也一样炸** ⇒ 入口形式与本故障无关。
- ★**同进程还有第二条退化 (本机实测)**: 同一进程里**第 3 次**插件调用就拿到坏对象 —— `PCB_IO_MGR.FindPlugin()` 返回裸 `SwigPyObject` (不再是 `PCB_IO`), `FootprintLoad()` 拿到的 `FOOTPRINT.Pads()` 不可迭代 ⇒ ⇒ **修法 = ① 改走 `pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP).FootprintLoad(...)`; ② 一个候选一个子进程 (彻底隔离该退化)**, D2 仍是**用 KiCad 自己的 `FOOTPRINT.SetOrientationDegrees`** 算, **没有手算旋转矩阵** ★
- ★**修完**: `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py` ⇒ **rc=0 · D0~D8 全绿 (9/9)**; `--selftest` ⇒ **rc=0 · 11/11 · 末行 `ALL TESTS PASS`** ★

★**② 两处判据口径精化 (判据没被削弱, 是把「假红」与「形同虚设」修成真判据)★**
- **D7 (板指纹)**: 原实现把 mtime 只格式化到**微秒 6 位**, 与任务书给的**纳秒 9 位**常量永远不相等 ⇒ **D7 一直假红** ⇒ 改成 `st_mtime_ns` 纳秒格式化 ⇒ 现在 `mtime=2026-11-06 07:07:17.362193413` 与任务书**逐字相同**。
- **D6 (与 `SOM_PIN_MAPPING.md` 不冲突)**: 「信号…不存在」断言正则原本把**引用块**与**转述映射页原话**一并判红 ⇒ 精化为「**只抓本页自己的断言**: 行首 `>` 的引用块豁免、明写『原话 / 第 48-51 行 / SOM_PIN_MAPPING.md』的转述豁免」⇒ ★**本页 §2-4 里自己的结论句仍然会被抓, 判据没被削弱** ★
- **D8 (证据等级白名单)**: 原本**只收以白名单词开头的 token** ⇒ 白名单外的等级标签 (本段为免触发闸, 写作「猜测」而无方括号) **根本收不到** ⇒ 改成「任何方括号标签 (1~12 字) 都当证据等级候选」⇒ ★**本页实测只有五级白名单标签 (实测 26 / 推算 5 / 0数据 4 / 官网 2 / 媒体 2), 精化后仍全绿** ★

★**③ 本页结论未被本段改动** ★: 物理针序契约 (§1)、JTAG 链 SoM 侧「不落地」的受控表述 (§2)、三条路的代价 (§3)、边界自证 (§4) **全部照旧**; ★**pin1 朝向与 ISS-344 口径仍是两个待 main 裁决项, 本单不代拍** ★

---

## 【追加式订正 (2026-11-24 04:3x · sw-lead · ISS-375 cont3)】派活材料 §一③ 那段代码的【口径差】+ 闸的 M2/M3 改成动【判据自己的数据源】

★**本页正文一字未改** (本段是纯追加) ★ · ★**页内全部数字与本段无冲突** (板 md5 / mtime / size 三项未动, 仍为 `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`) ★

### ★① 派活材料 §一③ 那段 pcbnew 代码: 我本机复跑, 数字【逐字相同】, 但它的口径必须写清 ★

★**我本机原样复跑 (2026-11-24 04:1x · 真板只读 · 不写盘 · 留证 `logs/iss375/rerun_brief_sec1_3_current_land.log`)★**:

```
fpid = ''
rot 0   [('1','JTAG_TCK',142.2), ('2','JTAG_TMS',142.7), ('3','JTAG_TDI',143.2), ('4','JTAG_TDO',143.7)]
rot 90  [('1','JTAG_TCK',142.9), ('2','JTAG_TMS',142.9), ('3','JTAG_TDI',142.9), ('4','JTAG_TDO',142.9)]
rot 270 [('1','JTAG_TCK',145.7), ('2','JTAG_TMS',145.7), ('3','JTAG_TDI',145.7), ('4','JTAG_TDO',145.7)]
```

★**⇒ 与派活材料 §一③ 给的三行【逐字相同】, 无差 ★**

★★**但这段代码量的是【现状 SMD land 被旋转】, 不是【两个候选落点】—— 这两件事必须分开, 否则会读出相反的结论** ★★

| | 派活材料 §一③ 那段代码 | 本单 S1/S2 沙盒 |
|---|---|---|
| ★**对象** ★ | ★**现状 `J_DEBUG` 的自定义 SMD land** (`fpid = ''` = 无官方封装 ID) ★ | ★**官方 `PinHeader_1x04_P1.27mm_Vertical` THT land** ★ |
| ★**pad 沿哪个局部轴排开** ★ | ★**局部 X** (实测: pad1 `(−2.1000, −1.4000)` / pad4 `(−0.6000, −1.4000)`, 步距 **0.5**) ★ | ★**局部 Y** (官方 land: pad1 `(0,0)` / pad4 `(0,3.81)`, 步距 **1.27**) ★ |
| ★**转 90°/270° 后 pad 落到哪** ★ | ★**四个 pad 挤到同一 X** (142.9 / 145.7) ⇒ **排针变成竖排** ★ | ★**四个 pad 沿 X 排开** (141.0450/142.3150/143.5850/144.8550) ⇒ **横排** ★ |
| ★**能不能当候选落点读数** ★ | ★**不能** ★ (量的是现状 land, 官方 land 一换, 局部轴就变了) | ★**能** ★ |

⇒ ★**结论不冲突, 但读法必须换**: 派活材料 §一③ 的 `rot 90 → 全挤到 142.9` 是【现状 land 的姿态退化现象】; 本单 §1-3/§1-4 的 S1/S2 才是【候选落点】。★**本单 §1 的针序契约以 S1/S2 为准 (用官方 land + KiCad 自己的 `SetOrientationDegrees` 实摆), 与 §一③ 的三行不冲突** ★
★**复跑命令**: `bash state/pcbnew_py.sh -c "<派活材料 §一③ 那段代码>"` (留证已落 `logs/iss375/rerun_brief_sec1_3_current_land.log`) ★

### ★② 闸的 M2 / M3 改成动【判据自己的数据源】(★原实现只能证明「页与闸对不上」, 证明不了本单的两条命脉★) ★

★**cont2 的 M2/M3 只改了页文本** ⇒ 实测红的是 D4 / D5 的**页↔实读**一致性, ⇒ ★**测不到「D2 真的是用 KiCad 变换算的」与「D5 真的是现读网表的」** ★
★**cont3 改成**: ★**M2 = 变异【本闸自己的源码】, 把 `compute_candidate_orders()` 换成返回写死常数 ⇒ 期望 D2 红; M3 = 在【沙盒网表副本】里把四条 `JTAG_*_SOC` 的 SoM 侧端点 `SoC_NC` 改成别的 ⇒ 期望 D5 红** ★ (★真网表只读, 真闸文件只读, 变异体与网表副本只落沙盒临时目录★)

| 用例 | 动的对象 | 期望红 | cont3 实测 |
|---|---|---|---|
| ★**M2** ★ | ★**闸源码** (`compute_candidate_orders` → 写死常数, 两候选同序) ★ | ★**D2 + D4** ★ | ★**D2 + D4** ✔ ★ |
| ★**M3** ★ | ★**沙盒网表副本** (4 行 `SoC_NC` → `SoC_FAKE`) ★ | ★**D5** ★ | ★**D5** ✔ ★ |

★**为什么 M2 的期望集是 {D2, D4} 而不是 {D2}**: D2 的输出被污染 ⇒ ★**D4 (= 页写序 vs D2 实算序) 必然同时对不上** ⇒ 这两条是【真实耦合】(D4 依赖 D2 的输出) ⇒ ★**如实写成两条, 不是把判据改松** ★
★**M2 的价值**: 变异体让两候选【同序】⇒ 若 D2 没有「互为逆序, 不是互等」这条判据, 变异体就会【全绿混过去】⇒ ★**这条反向用例直接证明「两个候选被当同一个」这个错误必被抓住** ★
★**M3 的价值**: 改的是【网表本体】⇒ 若 D5 把 `SoC_NC` 写死成常量, 网表变了页没改也不会红 ⇒ ★**这条反向用例直接证明 D5 是现读网表的** ★
★**修 bug 一处 (变异体注入点)**: 注入点用 `str.replace` 会命中源码里【前面那处同名字符串字面量】(注入块自己就含那个串) ⇒ **SyntaxError** ⇒ 改用 ★`src.rfind(marker)` 定位【最后】一个 `if __name__ == "__main__":` ★ ★
★**自测结果**: `--selftest` ⇒ ★**rc=0 · 11/11 PASS · 末行 `ALL TESTS PASS`** ★ (★镜像类 3 条: M1 / M2 / M3★) · 裸跑 ⇒ ★**rc=0 · D0~D8 9/9 PASS** ★
