# `J_DEBUG` / `J_UART` 排针换 land 后的**固件影响面清单** + `JTAG_TDI` 口径冲突收敛（SoC / SoM 两侧 JTAG 自查证）

> **件号**: ISS-378（sw-lead） · **版次**: v1.0 · **落盘日**: 2026-11-24
> **状态**: **分析件 + 机器判据件**（`SW/tools/check_debug_header_fw_impact.py`） · **零写板 / 零落表 / 零改既有闸 / 零改已签收页 / 零改既有口径页正文 / 零挂链 / 零外发 / 不代拍**
> **上游**: `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md`（ISS-375 · 已签收 verified · **本页只引用，一个字都不许改**） · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md`（ISS-344 口径页 · **本页只追加式引用与指出冲突，不改正文**）
> **本页不代拍**: `J_DEBUG`/`J_UART` 的 pin1 朝向（A/B）、`JTAG_TDI` 口径终裁（①改口径 / ②改网表 / ③换 SoM）—— **两条都归 main / 老板裁**。

---

## §0 一句话结论 + 范围

> ★**一句话结论**: ★**两块排针换 land 对固件的影响 = 【物理针序 / 救砖线序】这一层受影响，【网名→pad 号】映射这一层完全不受影响 ⇒ 固件本体零行要改；要改的是【把针序写死的 SW 侧机器件】与【把线序写死的工装/线序说明】，而这两样都由「pin1 朝向选 A 还是 B」这一个裁决决定 ⇒ 板只改一次 ⇒ 这一个裁决必须在板那一趟开工前落** ★

### §0-1 两层必须分开说（★本单最核心的一句★）

| 层 | 换 land 后变不变 | 依据 | 谁受影响 |
|---|---|---|---|
| ★**A 层：网名 → pad 号 映射**（`J_DEBUG.pin1 = JTAG_TCK` 这类**逻辑**对应） | ★**不变** ★ | 网表 `HW/netlist_v1_pins.csv:202-205`（`J_DEBUG.pin1=JTAG_TCK` / `pin2=TMS` / `pin3=TDI` / `pin4=TDO`）与 `:275-276`（`J_UART.pin1=UART_TX` / `pin2=UART_RX`）写的是**逻辑针号**；两个候选 land 都保持 `pad1=JTAG_TCK` ⇒ 逻辑映射逐字不变 ★ | ★**没有人** ★（固件 / 网表 / BOM / 脚本一律零改动）★ |
| ★**B 层：物理针序 / 救砖线序**（哪个物理位置是 pin1、TX 在左还是在右） | ★**变** ★（候选 A rot90 = 与现状同向；候选 B rot270 = **逆序**） ★ | `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` §1-3/§1-4（ISS-375 实测：两候选 pad 绝对 X 集合逐字相同，**pad→X 序互为逆序**） ★ | ★**排线 / 工装 / 线序说明 + 把针序写死的 SW 侧机器件** ★ |

⇒ ★**所以「换 land 要改固件吗」这个问法本身要拆开**：★**固件本体 = 零行要改**（§1 逐网实读：JTAG 四线与 UART 两线在 `SW/**` 里**零代码引用**）；★**要改的是「针序契约」这一层，不是「网名映射」那一层** ★

### §0-2 范围（本页只做影响面与代价）

- ★**本页做**: ①逐网影响面（§1）②三条救砖链（§2）③`JTAG_TDI` 口径冲突的三条路 + 代价（§3）④SoC / SoM 两侧 JTAG 的官方自查证（§4）⑤未决项（§5）
- ★**本页不做**: ★**不改一行固件本体** · ★**不改网表真源**（`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 全部只读） · ★**不改板** · ★**不改 `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` 与 `SW/tools/check_debug_pin_order_contract.py`**（已签收件） · ★**不改 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 正文**（冲突只登记，订正块归 main） · ★**不挂链** · ★**不签台账** · ★**不外发** · ★**不代拍** ★

---

## §1 逐网影响表（★主表★）

### §1-0 读表说明（三条，★每条都是判据★）

1. ★**「当前落在哪颗件哪个 pad」列里的 pad 写法 = `器件.pinN` 或 `器件.焊盘号`** ⇒ 与 `HW/netlist_v1_pins.csv` 的 `pin_id` 列逐字同形（`J_DEBUG.pin1` / `J_UART.pin2`）★
2. ★**「变化性质」列只有三个合法取值**：`无` / `仅物理针序` / `需改代码` ★
   - `无` = 换 land 对这一条网（**电气映射 + 固件侧用法 + SW 侧代码**）**零影响**
   - `仅物理针序` = 电气映射不变，但**物理线序**变 ⇒ 只有工装 / 线序说明要跟着改，**代码不用改**
   - `需改代码` = 有 **SW 侧机器件**把这一条网的物理状态写死了 ⇒ 换 land 之后它会红 ⇒ 必须改那一行
   - ★**本表取值口径 = 「两个候选里较严的一档」** ⇒ 候选 A（rot90 · 建议）时这些行的实际变化退化为 `无` ⇒ 见 §1-2 候选对照表 ★
3. ★**「若需改」列只写【文件 + 行号 + 函数名】★ —— 本单一个字都不许改**（★`SW/tools/check_debug_pin_order_contract.py` 与 `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` 是 **ISS-375 已签收件** ⇒ 本单只登记「板那一趟要改这里」，**改的授权归 main**★）

### §1-1 逐网表（★19 行 · 覆盖 JTAG 四线 + 四条 `*_SOC` + UART 两线 + BOOT_N + KEY 四条 + RESET 两条 + USB 两条★）

| 网名 | 两端节点 | 当前落在哪颗件哪个 pad | 固件侧当前用法 | 换 land 后是否变化 | 变化性质 | 若需改: 改哪个文件的哪一行 | 证据等级 | 来源 (文件:行号) |
|---|---|---|---|---|---|---|---|---|
| `JTAG_TCK` | `J_DEBUG pin1` / `R_JTAG_TCK` / `TP_JTAG` | `J_DEBUG.pin1` + `R_JTAG_TCK` (100Ω 串阻) + `TP_JTAG` | ★**固件零引用** —— `SW/**` 代码文件 (`.py`/`.sh`/`.json`) 命中 **5 处，全部在 `SW/tools/check_debug_pin_order_contract.py`**（L552 / L742 / L743 / L758 / L759）⇒ 那是**板针序契约闸**，不是固件；文档侧只有 S3 救砖脚手架 | ★电气映射**不变**；B 层物理针序在 rot270 候选下**反转** | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L287** `d1_current_board()` —— 换 land 后 `pad1_x` / `pad_shape` / `pad_attr` / `pad1_marker` 四项读数与页 `current` 块要同步 | [实测] | `HW/netlist_v1.csv:368,389` · `HW/netlist_v1_pins.csv:202` · `SW/tools/check_debug_pin_order_contract.py:287,552` |
| `JTAG_TMS` | `J_DEBUG pin2` / `R_JTAG_TMS` | `J_DEBUG.pin2` + `R_JTAG_TMS` (100Ω 串阻) | ★**固件零引用** —— 同上，代码侧只命中 `check_debug_pin_order_contract.py:552` 的四网元组 | ★电气映射**不变**；rot270 候选下物理针序反转 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L552** `d5_netlist_soc_side()` —— JTAG 四网元组随新板重核 | [实测] | `HW/netlist_v1.csv:391` · `HW/netlist_v1_pins.csv:203` · `SW/tools/check_debug_pin_order_contract.py:520,552` |
| `JTAG_TDI` | `J_DEBUG pin3` / `R_JTAG_TDI` | `J_DEBUG.pin3` + `R_JTAG_TDI` (100Ω 串阻) | ★**固件零引用** —— `grep -rnw JTAG_TDI SW` = **52 行**，但代码侧只有 `check_debug_pin_order_contract.py:552,742,743` 3 处（都是**针序契约闸**，不是固件）；★**`JTAG_TDI` 在板面是 0 段铜**（ISS-375 实测）⇒ 它现在物理上就是断的 ★ | ★电气映射**不变**；rot270 候选下物理针序反转 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L466** `d4_page_matches_computed()` —— `net_by_pad` 读取源 + `order_by_x` 判定源 | [实测] | `HW/netlist_v1.csv:393` · `HW/netlist_v1_pins.csv:204` · `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md:201,270` |
| `JTAG_TDO` | `J_DEBUG pin4` / `R_JTAG_TDO` | `J_DEBUG.pin4` + `R_JTAG_TDO` (100Ω 串阻) | ★**固件零引用**（代码侧只命中 `check_debug_pin_order_contract.py:552,742,743`） | ★电气映射**不变**；rot270 候选下物理针序反转 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L312** `compute_candidate_orders()` —— 候选几何随新 land 重算（pad 绝对 X 集合） | [实测] | `HW/netlist_v1.csv:395` · `HW/netlist_v1_pins.csv:205` · `SW/tools/check_debug_pin_order_contract.py:312` |
| `JTAG_TCK_SOC` | `R_JTAG_TCK` / `SoC_NC` | `R_JTAG_TCK.1` ↔ ★**`SoC_NC`（占位，无实物焊盘）** ★ | ★**固件零引用**；★**SoM 侧端点 = `SoC_NC` ⇒ JTAG 链在 SoM 那一头接不到任何 SoM 引脚** ★ | ★**不变**（`SoC_NC` 与排针 land 无关） | 无 | — | [实测] | `HW/netlist_v1.csv:388` |
| `JTAG_TMS_SOC` | `R_JTAG_TMS` / `SoC_NC` | `R_JTAG_TMS.1` ↔ ★**`SoC_NC`** ★ | ★**固件零引用**；SoM 侧端点 = `SoC_NC` | ★**不变** | 无 | — | [实测] | `HW/netlist_v1.csv:390` |
| `JTAG_TDI_SOC` | `R_JTAG_TDI` / `SoC_NC` | `R_JTAG_TDI.1` ↔ ★**`SoC_NC`** ★ | ★**固件零引用**；★**这一条就是 ISS-344 与本单冲突的落点**（ISS-344 把 `JTAG_TDI` 判「必需 · 板侧不许标 NC」，而网表 SoM 侧就是 `SoC_NC`）★ | ★**不变** | 无 | — | [实测] | `HW/netlist_v1.csv:392` · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:120,152` |
| `JTAG_TDO_SOC` | `R_JTAG_TDO` / `SoC_NC` | `R_JTAG_TDO.1` ↔ ★**`SoC_NC`** ★ | ★**固件零引用**；SoM 侧端点 = `SoC_NC` | ★**不变** | 无 | — | [实测] | `HW/netlist_v1.csv:394` |
| `UART_TX` | `J_UART pin1` / `J_SOM_P2 pin7` / `TP_UART` | `J_UART.pin1` + `J_SOM_P2.pin7` + `TP_UART.pad1` | ★**主机侧只读日志链** —— `SW/tools/s2_board_run.sh` 的 `collect_forensics()` 串口抓取段只做 `timeout "${SECS}" cat "$SERDEV" > "$SER"`（**板→主机**）★；`SW/tools/s2_rescue_config.json:230` 的 `_readme` 明写「板端串口（取日志用）」★ ⇒ **固件侧只把日志吐出来，SW 侧从不往板里写** ★ | ★电气映射**不变**；rot270 候选下**物理 TX/RX 位置互换** ⇒ 工装线序要反 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L231** `read_current_board()` —— `J_UART` 现状读数源（`pad1_x` / `pad_shape` / `pad_attr` / `pad1_marker`） | [实测] | `HW/netlist_v1.csv:369,397` · `HW/netlist_v1_pins.csv:275` · `SW/tools/s2_board_run.sh:243,256` · `SW/tools/s2_rescue_config.json:230` · `SW/tools/check_debug_pin_order_contract.py:231` |
| `UART_RX` | `J_UART pin2` / `J_SOM_P2 pin9` | `J_UART.pin2` + `J_SOM_P2.pin9` | ★**主机→板方向零需求** —— ★**`stty` / `> /dev/tty` / `write..tty` 三个模式在 `SW` 的**代码文件里命中 = 0 行**（唯一 1 处命中是 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:125` 这条口径页自己的记录 ⇒ 自引用）★ ⇒ SW 侧**从不往板里写串口** ★ | ★电气映射**不变**；rot270 候选下物理 RX 位置互换 ⇒ 工装线序要反（**代码本体不用改**）★ | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L231** `read_current_board()` —— `J_UART` 现状读数源（与 `UART_TX` 同一处读数，两行一起改） | [实测] | `HW/netlist_v1.csv:398,399` · `HW/netlist_v1_pins.csv:276` · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:125,156` |
| `BOOT_N` | `J_SOM_P1 pin28` / `R_PU_BOOT_N` / `SW_BOOT` / `TP_BOOT` | `J_SOM_P1.pin28` + `R_PU_BOOT_N` (10k 上拉 1.8V) + `SW_BOOT` + `TP_BOOT` | ★**固件零引用** —— 代码侧只在 `SW/tools/timing_check.py:1654` 与 `:2202` 的**判据文字串**里出现（不是逻辑分支）★ | ★**完全不变** ★ —— ★**`BOOT_N` 一根都不经过 `J_DEBUG` / `J_UART`**（它走 `J_SOM_P1.pin28` + 独立按键 + 独立测试点）★ ⇒ **与本次换 land 零交集** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:367,384,386` · `SW/tools/timing_check.py:1654,2202` |
| `KEY_PWR` | `J_SOM_P1 pin64` / `R_KEY_PWR` / `SW_KEY_PWR` / `C_KEY_PWR` / `TP_KEY_PWR` | `J_SOM_P1.pin64` + `R_KEY_PWR` (10k) + `C_KEY_PWR` (100nF) + `SW_KEY_PWR` + `TP_KEY_PWR` | ★**固件零引用**（`grep -rnw KEY_PWR SW` 代码文件 = 0 行）★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:309,310,313,363` |
| `KEY_VOL_P` | `J_SOM_P2 pin13` / `R_KEY_VP` / `SW_KEY_VP` / `C_KEY_VP` / `TP_KEY_VP` | `J_SOM_P2.pin13` + `R_KEY_VP` (10k) + `C_KEY_VP` (100nF) + `SW_KEY_VP` + `TP_KEY_VP` | ★**固件零引用**（代码文件 = 0 行）★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:314,315,318,364` |
| `KEY_VOL_M` | `J_SOM_P4 pin1` / `R_KEY_VM` / `SW_KEY_VM` / `C_KEY_VM` / `TP_KEY_VM` | `J_SOM_P4.pin1` + `R_KEY_VM` (10k) + `C_KEY_VM` (100nF) + `SW_KEY_VM` + `TP_KEY_VM` | ★**固件零引用**（代码文件 = 0 行）★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:319,320,323,365` |
| `KEY_CAM` | `J_SOM_P4 pin3` / `R_KEY_CAM` / `SW_KEY_CAM` / `C_KEY_CAM` | `J_SOM_P4.pin3` + `R_KEY_CAM` (10k) + `C_KEY_CAM` (100nF) + `SW_KEY_CAM`（★整条 **DNP** ★） | ★**固件零引用**（`grep -rnw KEY_CAM SW` = **0 行**）★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:324,325,328` |
| `RESET_N` | `Q_AND` / `R_PU_RESET_N` / `R_SER_RESET_N` / `SW_RST` / `U_SUPV pin1` / `TP_RESET` | `SW_RST` (按键) + `TP_RESET` + `R_PU_RESET_N` + `R_SER_RESET_N` + `U_SUPV.pin1` + `Q_AND` | ★**固件零引用** ★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:65,366,377,382,409` |
| `RESET_N_SOC` | `R_SER_RESET_N` / `J_SOM_P2 pin100` / `C_RST` | `R_SER_RESET_N` (1k) + `C_RST` (100nF) + `J_SOM_P2.pin100` | ★**固件零引用**；唯一「代码侧出现」是 `SW/tools/timing_check.py:1111` 读 `RESET_N_SOC` 的 note 算 τ（**读网表**，不是驱动这个脚）★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:379,380` · `SW/tools/timing_check.py:1111` |
| `USB_CC1` | `J_USB_C A5` / `R_CC1_D` / `J_TYPE_C A5` / `R_CC1` | `J_USB_C.A5` + `R_CC1_D` (5.1k Rd) + （充电板）`J_TYPE_C.A5` + `R_CC1` | ★**固件零引用**；SW 侧只有 `SW/tools/check_sw_ref_reachability.py:178`/`:185` 与 `check_sw_ref_reachability_v2.py:237`/`:244` 硬编码位号 `"J_TYPE_C"`（★**`J_TYPE_C` 不在官方板上** —— 那是充电板侧的件★）★ | ★**完全不变** ★ —— ★**USB 走板载 Type-C `J_USB_C`（`HW/netlist_v1.csv:428`），与 `J_DEBUG` / `J_UART` 不同束、不同器件** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:293,428,456` · `SW/tools/check_sw_ref_reachability.py:178,185` |
| `USB_CC2` | `J_USB_C B5` / `R_CC2_D` / `J_TYPE_C B5` / `R_CC2` | `J_USB_C.B5` + `R_CC2_D` (5.1k Rd) + （充电板）`J_TYPE_C.B5` + `R_CC2` | ★**固件零引用**（同上，`"J_TYPE_C"` 硬编码在两个可达性闸里）★；★**这是 ISS-344 8 条「必需」里的另一条**，与 `JTAG_TDI` 同属「必需 vs 现实」的对撞候选★ | ★**完全不变** ★ —— ★**与排针不同束** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:294,297,429,457` · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:126,157` |

### §1-2 候选对照表（★A / B 之下每一行的实际变化★）

| 网组 | 候选 A（rot90 · ISS-375 建议） | 候选 B（rot270） | 本表 §1-1 取值 |
|---|---|---|---|
| `JTAG_TCK` / `JTAG_TMS` / `JTAG_TDI` / `JTAG_TDO` | ★**电气映射不变 + 物理针序与现状同向（顺排 TCK→TMS→TDI→TDO）** ⇒ **线序说明零改动** ★ | ★**电气映射不变 + 物理针序反转（逆排 TDO→TDI→TMS→TCK）** ⇒ **全部现有 JTAG 线序描述必须反转** ★ | `需改代码`（取严档；实际只改机器件的读数，不改逻辑映射）★ |
| `UART_TX` / `UART_RX` | ★**电气映射不变 + 物理顺序与现状同向（TX→RX）** ★ | ★**电气映射不变 + 物理顺序反转（RX→TX）** ⇒ 工装线序要反 ★ | `需改代码`（取严档）★ |
| `JTAG_*_SOC` ×4 | ★**不变** ★ | ★**不变** ★ | `无` ★ |
| `BOOT_N` / `KEY_*` ×4 / `RESET_N` / `RESET_N_SOC` / `USB_CC1` / `USB_CC2` | ★**不变**（不经过排针）★ | ★**不变**（不经过排针）★ | `无` ★ |

### §1-3 ★**「固件本体要改几行」的最终答案★**

> ★**0 行。** ★
> ★**依据（三条，逐条可复跑）**: ★
> ① ★**固件侧零网名引用** —— `JTAG_TCK` / `JTAG_TMS` / `JTAG_TDI` / `JTAG_TDO` / `UART_TX` / `UART_RX` 在 `SW/**` 的**代码文件**（`.py`/`.sh`/`.json`）里命中 **0 行**（JTAG 组唯一的 5 处全在 `SW/tools/check_debug_pin_order_contract.py` = 板针序契约闸；UART 组唯一 1 处 `stty|> /dev/tty|write.*tty` 命中是 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:125` 的**自引用记录**）★ → **[实测]** ★
> ② ★**逻辑映射逐字不变** —— `HW/netlist_v1_pins.csv:202-205,275-276` 的 `J_DEBUG.pinN` / `J_UART.pinN` → 网名对应，在两个候选 land 下都不变（两个候选都保持 `pad1=JTAG_TCK` / `pad1=UART_TX`）★ → **[实测]** ★
> ③ ★**要改的是「把物理针序写死」的机器件，不是固件** —— `SW/tools/check_debug_pin_order_contract.py` 的 `read_current_board()` / `d1_current_board()` / `compute_candidate_orders()` / `d4_page_matches_computed()` / `d5_netlist_soc_side()` 五处读的是**板面现状读数** ⇒ 板一换 land，这五处**必然变红** ⇒ ★**改它们是「板那一趟」的活，不是「固件改动」，且该文件是 ISS-375 已签收件 ⇒ 改的授权归 main** ★
>
> ⇒ ★**所以：板只改一次 ⇒ 「pin1 朝向」这一个裁决必须在板那一趟开工前落**（理由 = 它决定那五处读数往哪边写；落晚了 = 板做了还得再改一次机器件 = 违反「板只改一次」）★

---

## §2 救砖链（★硬需求节★）

### §2-0 三条链与 4 级救砖表的对应（`SW/FLASH_AND_VERSION.md:44` + `:336`）

`SW/FLASH_AND_VERSION.md:44`（结论 5）明写 4 级：**S1 看门狗+systemd 自恢复 → S2 BOOT 模式强制重刷 → S3 JTAG → S4 返厂换板**；`:336`（§4.4 表）是 S3 那一行。三条物理链与 4 级的对应：

| 链 | 对应救砖级 | 物理载体（板面） | 现状能不能救 | 换 land 后还能不能救 | 断了会死在哪一步 | 降级路径 |
|---|---|---|---|---|---|---|
| ★**USB 链** ★ | ★**S2**（BOOT 模式 + 厂商下载工具强制重刷）★ | 板载 Type-C `J_USB_C`（`HW/netlist_v1.csv:428/429` USB_CC1/CC2 + `:292` USB 差分 → `J_SOM_P1`）★**不经过 `J_DEBUG` / `J_UART`** ★ | ★**能（工具链侧已自查结案）** —— Rockusb MaskROM/Loader + 官方开源 `rkdeveloptool` 路线（ISS-270 自查结案，登记在 `state/fragments/sw.yaml` 的 `fw_vendor_toolchain` / `fw_usb_boot_phy` / `fw_boot_entry_cond` 三条）★；★**BOOT 态识别判据已有机器件**: `SW/tools/boot_rescue_probe.py`（`enumerate_usb()` / `match_signature()` / `scan_log_for_boot()` / `verdict()`）+ `SW/tools/s2_rescue_config.json:92` 的 `usb_signatures` 块★ | ★**能，且零影响** ★ —— ★**USB 走 `J_USB_C`，与两块排针不同束、不同器件、不同走线 ⇒ 换 land 对 USB 链零影响** ★ | ★**死 S2** —— 进不了 BOOT 模式 或 下载工具认不出设备 ⇒ 刷不回来 ⇒ 直接跳 S4 ★ | ★**S2 不可用 ⇒ S4 返厂**；★**S1（看门狗/systemd 自恢复）只救应用层崩溃，救不了 bootloader 损坏** ★ |
| ★**UART 链** ★ | ★**不属救砖级**（= **日志观测链**）★ | `J_UART` 1×2 排针（`HW/netlist_v1_pins.csv:275-276`）+ `TP_UART`（`:369`）+ `J_SOM_P2.pin7/9`（`:397/398`）★ | ★**能（观测链）** —— `SW/tools/s2_board_run.sh:243-263` 的 `collect_forensics()` 只做 `cat "$SERDEV" > "$SER"`（板→主机）★；`SW/S2_BOARD_TEST_CHECKLIST.md:94` 的工位准备表把它写成「USB-TTL 串口线 + 笔记本 | 能看 U-Boot / kernel 串口输出」★；★**`J_UART` 整件 dnp = 可选** ★ | ★**能** —— 候选 A（rot90）**物理顺序不变** ⇒ 工装零改；候选 B（rot270）**TX/RX 物理位置互换** ⇒ **工装线序要反**（软件侧只读方向，逻辑不变）★ | ★**只丢日志观测** —— ★**UART 链断了不影响任何救砖级**（USB 刷机不依赖串口，JTAG 也不依赖串口）★ ⇒ 现场变成「盲刷」：刷完起不来时**看不到 U-Boot/kernel 输出**，诊断信息少一维 | ★**无降级**（它本来就不是救砖链）★ ⇒ 断链的代价 = **诊断能力下降**，不是救砖能力下降 ★ |
| ★**JTAG 链** ★ | ★**S3**（JTAG 调试器接 SoC）★ | `J_DEBUG` 1×4 排针（`HW/netlist_v1_pins.csv:202-205`）+ 四颗 100Ω 串阻（`R_JTAG_TCK/TMS/TDI/TDO`，`HW/netlist_v1.csv:389,391,393,395`）+ `TP_JTAG`（`:368`）★ | ★**不能** ★ —— ★**SoM 侧不落地**: 四条 `JTAG_*_SOC` 的 SoM 侧端点**全部 = `SoC_NC`**（`HW/netlist_v1.csv:388/390/392/394`）★ + ★**`HW/PCB/FET3572C_PIN_TABLE.csv`（399 数据行）里 `JTAG` 命中 = 0** ★ ⇒ ★**S3 在这一版 SoM 上不存在** ★ | ★**还是不能** ★ —— ★**换 land 只改排针的物理针序与 pad 形状，改不了「SoM 侧没有 JTAG 引出」这个事实** ★ ⇒ ★**S3 不会因为换 land 而活过来，也不会因为换 land 而更死** ★ | ★**死 S3** —— bootloader 损坏时 S2 进不去 ⇒ ★**唯一还能走的一级不存在** ⇒ 直接死 **S4** ★ | ★**降级路径 = S4 返厂换板**（`SW/FLASH_AND_VERSION.md:336` 的 S4 行 = 返厂换存储器件 / 换板）★ ⇒ ★**`SW/EVT_TEMPLATE.md:503` 的硬规则「S2 连续失败 2 次 → 必须升级 S3 (JTAG)」在事实层面无执行对象** ★ |

### §2-1 ★**「最坏只剩哪条链」的一句话结论（★必答★）★★

> ★**最坏情况下只剩 USB（S2）这一条链** —— ★**因为 JTAG（S3）链在本版 SoM 上【根本不存在】、UART 只做日志观测不做救砖** ★；★**而若连 USB（S2）也不可用（BOOT 进不去 / 下载工具不认设备），那就【一条链都不剩】，只剩 S4 返厂换板** ★。
>
> ★**换 land 不改变这个结论** ★ —— ★**换 land 只新增了一种人为失效模式（排线插反）**，它把「USB 链可用」变成「USB 链因插反而不可用」⇒ ★**最坏路径 = 插反 + S2 不可用 ⇒ 直接 S4** ★。
> ★**⇒ 板那一趟必须把 pin1 朝向 + 线序一次写死（ISS-375 §1-5 已备好两套写死值），否则这一种人为失效模式是【无标记、不可见】的** ★（★现状板面 `J_DEBUG` 4 个 pad 全 `RECT`/全 `SMD` ⇒ **看不出哪端是 pin1**；换官方 land 后 pad1 变 `thru_hole rect` ⇒ **第一次变成实物可见**★）。

---

## §3 `JTAG_TDI` 口径冲突收敛（★本单最重要的一节 · 只登记 + 给代价 · 不代拍★）

### §3-1 冲突登记（★事实句 vs 裁决句★）

> ★**一句话（本节机器判定句）**: ★**SoM 侧无 JTAG 引出** ⇒ ★**JTAG 链在板级不落地** ⇒ ★**ISS-344 的「必需」分级在本版 SoM 上【没有物理兑现对象】** ★（★**依据 = §4 的闸自跑实测：SoM 逐针表 399 行 `JTAG` 命中 0 + 网表四条 `JTAG_*_SOC` 的 SoM 侧端点全部 `SoC_NC` + 官方 datasheet 引脚复用表只列 TCK/TMS**★）★

| # | 既有裁决（读，不改） | 本单实读事实 | 冲突性质 |
|---|---|---|---|
| ★**C-1** ★ | `JTAG_TDI` = ★**必需** ★ · ★**进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ —— `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:120`（`JTAG_TDI` 行）+ `:152`（§3 清单行）+ 6 处 `ISS344-CORR` 块 ★ | ★**`JTAG_TDI_SOC` 的 SoM 侧端点 = `SoC_NC`**（`HW/netlist_v1.csv:392`）★ ⇒ ★**裁决的「不许标 NC」与网表的 `SoC_NC` 占位直接对撞** ★ | ★**正面冲突** ★ |
| ★**C-2** ★ | 机器真源 `HW/check_s8_target_list.py:55-56` 把 `JTAG_TDI` 写进 `REQUIRED_SINGLE`（8 条单端脚之一），并在 `:23-24` 逐字沿用 main 2026-11-22 20:5x 口径 ★ | ★**该脚本只判「分级 + 本板有没有铜」，不判「SoM 侧有没有这个脚」** ⇒ ★**分级成立，但它的物理前提（SoC 侧有 JTAG 可接）被本单证伪** ★ | ★**裁决内部自洽 · 前提被证伪** ★ |
| ★**C-3** ★ | `SW/FLASH_AND_VERSION.md:44`（4 级救砖 S3=JTAG）+ `:336`（S3 行）+ `SW/EVT_TEMPLATE.md:503`（硬规则「S2 连续失败 2 次 → 必须升级 S3」）+ `SW/S2_BOARD_TEST_CHECKLIST.md:393`（「S2 失败第 2 次 → 申请升级 S3」）★ | ★**S3 在这一版 SoM 上不存在**（§4 全部实测）★ ⇒ ★**这 4 处硬规则没有执行对象** ★ | ★**执行链断** ★ |
| ★**C-4** ★ | `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:156`（`UART_RX` 行）已被 ISS344-CORR 改判「必需 · 进 S8 布线目标」★ | ★**`UART_RX` 在板面是 0 段铜**（ISS-375 实测）★；★**主机侧只用读方向**（§1-1 `UART_RX` 行）★ ⇒ ★**它的「必需」是可以靠布线补上的（不依赖 SoM 侧）⇒ 与 `JTAG_TDI` 不同类** ★ | ★**同类问题 · 不同解法** ★（★`UART_RX` 缺的是**板上的铜**，`JTAG_TDI` 缺的是**SoM 上那个脚** ⇒ ★**后者不是布线能解决的**★）★ |

### §3-2 三条路（★逐条：依据 / 代价 / 牵连面 / 要谁拍★）

#### ★路线 ① —— 改口径（把 `JTAG_TDI` 从「必需」降级 / 标成板侧 NC）★

| 项 | 内容 |
|---|---|
| ★**依据** ★ | ★**SoM 侧没有 JTAG 可接是既成事实**（§4 实测：399 行脚表 `JTAG` 命中 0；网表 SoM 侧 = `SoC_NC`；官方 datasheet 引脚复用表只有 TCK/TMS）★ ⇒ ★**「必需」这个分级在物理上无法兑现** ★ |
| ★**代价 1（口径层）** ★ | ★**与 ISS-344 终裁正面冲突** ⇒ ★**需 main 重开裁**（★sw-lead 不自行改写既有裁决★）★ |
| ★**代价 2（文件层）** ★ | ★**`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 有 6 处 `ISS344-CORR` 块 + §0/§Q1/§Q2/§3/§3-1/§5/§7 多处投影要连带改**（★**该页正文本单一个字都不许改** ⇒ ★**订正块归 main**★）★ |
| ★**代价 3（救砖层）** ★ | ★**`SW/FLASH_AND_VERSION.md:44` + `:336`（S3 行）+ `SW/EVT_TEMPLATE.md:503` + `SW/S2_BOARD_TEST_CHECKLIST.md:393` 这 4 处硬规则失去执行对象** ⇒ ★**须同步降级为「S3 不可用 ⇒ 直接 S4」** ★ |
| ★**代价 4（板侧，最小）** ★ | ★**`J_DEBUG` 的 4 根线在板那一趟【不用改线序设计】** ⇒ ★**这是三条路里唯一【板那一趟零额外动作】的一条** ★ |
| ★**代价 5（能力）** ★ | ★**救砖能力从「4 级」降为「3 级」**（S1 → S2 → S4）⇒ ★**量产变砖只能返厂** ★ |
| ★**牵连面** ★ | ★**SW 域**: `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md`（6+ 处）· `SW/FLASH_AND_VERSION.md`（2 处）· `SW/EVT_TEMPLATE.md`（1 处）· `SW/S2_BOARD_TEST_CHECKLIST.md`（1 处）★　★**HW 域**: `HW/check_s8_target_list.py` 的 `REQUIRED_SINGLE` 列表 + `EXPECT_REQUIRED = 23`（**该文件属 hw-lead 地界，本单只读**）★　★**板面**: 无 ★ |
| ★**要谁拍** ★ | ★**main**（重开 ISS-344 的分级裁决；**落订正块也归 main**）★ —— ★**不是老板级**（不改产品功能、不改锁死变量，只改「可执行性分级」）★ |

#### ★路线 ② —— 改网表（把 `JTAG_*_SOC` 的 SoM 侧从 `SoC_NC` 改到某个真 SoM 引脚）★

| 项 | 内容 |
|---|---|
| ★**依据** ★ | ★**若 SoM 侧能引出 JTAG，则四级救砖恢复完整** ★ |
| ★**★但这条路当前走不通（决定性事实）★** ★ | ★**`HW/PCB/FET3572C_PIN_TABLE.csv`（1 表头 + 399 数据行）里 `JTAG` 命中 = 0**（★`grep -ic jtag` 实测输出 `0`★）⇒ ★**没有可指向的脚** ★ ⇒ ★**改网表不是「改四行」，是「先要有一个能引出 JTAG 的 SoM」** ★ |
| ★**代价 1（前置）** ★ | ★**必须先出「SoM 侧 JTAG 怎么引出」的方案**（换 SoM 型号 / 原厂加引脚 / 走别的调试口）⇒ ★**这是一件独立的前置工作，不是改网表能单独完成的** ★ |
| ★**代价 2（落表）** ★ | ★**改网表 = 落表动作** ⇒ ★**违反本单「零落表」边界** ⇒ ★**须由 main 在落表窗口内走流程（落表台账 + 三件 md5 全动）★ ⇒ ★**所有既有闸的 md5 基线要跟着前移** ★ |
| ★**代价 3（牵连）** ★ | ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 全变** ⇒ ★**板那一趟之前落表 = 板 md5 不变但表 md5 变（可接受），板那一趟之后落表 = 板改两次（不可接受）** ★ ⇒ ★**⇒ 路线 ② 若被采纳，其落表窗口必须【早于或并入】板那一趟** ★ |
| ★**代价 4（板面）** ★ | ★**要新增 SoM 侧 JTAG 走线 ⇒ 板面布线量增加 ⇒ 可能挤占 `J_DEBUG` 开口窗口（ISS-371 口径，单边间隙 CRIT 0.60）★ ⇒ ★**要重跑一次间隙/DRC** ★ |
| ★**牵连面** ★ | ★**HW 域**: 网表三件 + BOM + `HW/check_s8_target_list.py` + 板面布线 ★　★**SW 域**: 本页 §2/§3 + 救砖 4 级表的 S3 行（**恢复**而非降级）★　★**MECH 域**: 开口窗口可能要重算 ★ |
| ★**要谁拍** ★ | ★**main**（是否启动「SoM 侧 JTAG 引出方案」这条前置工作；若是，**归 hw-lead 出方案、main 决定是否落表**）★ —— ★**若涉及换 SoM 型号 ⇒ 升级到老板级** ★ |

#### ★路线 ③ —— 换 SoM（放弃 S3 软救砖，只留 S4 返厂）★

| 项 | 内容 |
|---|---|
| ★**依据** ★ | ★**若这版 SoM 不引 JTAG 且不打算换 SoM 方案，则 S3 必须被正式放弃** ★ |
| ★**代价 1（最大）** ★ | ★**量产眼镜变砖 ⇒ 只能 S4 返厂换件** ⇒ ★**返修成本与周期全压在产线** ⇒ ★**`SW/FLASH_AND_VERSION.md` 产线硬要求「每台眼镜交付前必须实测走通一次 S2」的压力全部落到 S2 一条链上** ⇒ ★**S2 一次都不许失** ★ |
| ★**代价 2（文档）** ★ | ★**`SW/EVT_TEMPLATE.md:503` + `SW/S2_BOARD_TEST_CHECKLIST.md:393` + `SW/FLASH_AND_VERSION.md:44/336` 全部要改成「S3 不可用 ⇒ 直接 S4」★ ★（★与路线 ① 的代价 3 重叠 ⇒ ★**①与③可以在同一次裁决里一起落**★）★ |
| ★**代价 3（与「板只改一次」冲突）** ★ | ★**换 SoM = 板面 BTB 连接器/走线全变** ⇒ ★**板必须重做** ⇒ ★**若现在不定、板做出来再换 = 板改第二次** ⇒ ★**⇒ 路线 ③ 若被采纳，必须【赶在板那一趟之前定】** ★ |
| ★**代价 4（选型）** ★ | ★**要重跑 SoM 选型打分**（`state/_soc_score_15.py` 一类）★ ⇒ ★**这是本单不做、也不该 SW 侧做的一件** ★ |
| ★**牵连面** ★ | ★**板面**: BTB 连接器 + 全部 SoM 侧走线 + 板层数 + 板框 ★　★**HW 域**: 网表三件 + BOM 全动 ★　★**MECH 域**: 镜脚/镜框结构 + 板框 ★　★**SW 域**: 救砖 4 级表 + 产线流程 ★ |
| ★**要谁拍** ★ | ★**老板级**（换芯片 = 商务/供应链级）★ —— ★**main 转达** ★ |

### §3-3 ★**sw-lead 的建议（★标明：不代拍★）★★

> ★**建议 = 路线 ① + 路线 ③ 的「口径部分」在同一次裁决里一起落，并同时启动路线 ② 的【前置可行性摸底】（不是落表）** ★
>
> ★**理由（按代价从低到高）**: ★**① < ② < ③** ★（与 ISS-375 §3-2 的排序一致，本单独立复算后结论相同）★
> - ★**① 是唯一【板那一趟零额外动作】的一条** ★（`J_DEBUG` 线序设计不用动）★
> - ★**③ 的「口径部分」= 「正式承认 S3 不存在」** —— ★**这条不该拖** ★，因为它决定 `SW/EVT_TEMPLATE.md:503` 的硬规则往哪指；★**但 ③ 的「换 SoM」部分不该现在拍** ★（老板级，且要重跑选型）★
> - ★**② 的【前置可行性摸底】建议现在就做** ★（只查公开资料 + 官方 datasheet + SoM 脚表，**零落表、零采购、零外发**）★　★**但 ② 的【落表】不许现在做** ★（落表窗口必须并入板那一趟，否则板改两次）★
>
> ★**★必须赶在板那一趟之前定死的只有一件事: 「pin1 朝向」(A/B)** —— ★**它不依赖 SoM 侧结论**（纯落点写死）★，★**而它决定 §1-1 那 5 处机器件读数往哪边写** ★ ⇒ ★**落晚了 = 板做了机器件还得再改 = 违反「板只改一次」** ★
>
> ★**不代拍声明**: ★**本单不代 main / 老板拍上述任何一条** ★ —— ★**§3-2 三条路的代价与牵连面已算清，§5 已逐条写明「要谁回答什么」，请 main 裁** ★

---

## §4 官方自查证（★自己查 · 零外发 · 不挂任何外部依赖形态★）

> ★**查证纪律**: ★**零外发**（不发邮件 / 不询价 / 不问原厂 / 不等待任何外部答复）★ —— ★**全部靠本机盘上官方文件实读**；★**本机已有的官网级素材由本单自己实读，未抄任何 agent 报告** ★

### §4-1 闸自己会跑的两条 grep（★本页结论的出处★）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv ; echo "rc=$?"
grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv ; echo "rc=$?"
```

★**实测输出（本单自己跑的，不是抄任务书）**: ★

```
B11,GPIO2_A2,UART,CAN0_RX_M0/JTAG_TCK_M0/SPI0_CSN1_M1/UART5_RTSN_M2/SAI3_LRCK_M1/DSM_AU
1A8,GPIO2_A3,UART,CAN0_TX_M0/JTAG_TMS_M0/UART5_CTSN_M2/SAI3_SDI_M1/DSM_AUD_RN_M0/SDMMC
U33,GPIO0_D4,UART,JTAG_TCK_M1/UART0_TX_M0/GPIO0_D4_u
V32,GPIO0_D5,UART,JTAG_TMS_M1/UART0_RX_M0/GPIO0_D5_u
rc=0
0
rc=1
```

★**逐行实读结论（★4 行全读完再下结论★）**: ★
- ★**`HW/RK3572_PIN_TABLE/rk3572_pins.csv`（表头 `ball,gpio,func,name` · 由官方 PDF 解析而来）里 JTAG 命中 = 4 行** ★（`pins.csv` 行号 **125 / 126 / 167 / 168**）★
- ★**这 4 行的 JTAG mux 名 = `JTAG_TCK_M0` / `JTAG_TMS_M0` / `JTAG_TCK_M1` / `JTAG_TMS_M1`** ★
- ★**⇒ SoC 侧官方引脚复用表里【只有 TCK 和 TMS】，没有 `JTAG_TDI*` / `JTAG_TDO*` 任何一个 mux 名** ★
- ★**`grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv` = `0`** ⇒ ★**SoM 模块逐针表（399 数据行）里 JTAG 命中 = 0 ⇒ 模块侧没有 JTAG 引出** ★（★`rc=1` 是 grep 的「无匹配」退出码，不是错误★）

### §4-2 ★**本单新增的官网级事实（★任务书里没有 · 本单自己实读出来的·比 ISS-375 更进一步★）★★

★**`HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`（官方 PDF 的文本层 · 2921 行 · PDF md5 `c0e3763036e2f6a3e8a2f68f2254851d`）里 JTAG 命中 = 5 处**：★

| 文本层行号 | 原文（逐字） | 读出来的意思 | 证据等级 |
|---|---|---|---|
| ★**L247** ★ | `    JTAG interface for debug` ★（在 §1.2.3 System Component 的 `BUS RISCV MCU` 特性块里） ★ | ★**官方明写：RK3572 芯片【有 JTAG 调试接口】** ★ | ★**[官网]** ★ |
| **L1197** | `CAN0_RX_M0/JTAG_TCK_M0/SPI0_CSN1_M1/UART5_RTSN_M2/SAI3_LRCK_M1/DSM_AU` | `GPIO2_A2` 的 mux 里含 `JTAG_TCK_M0` | [官网] |
| **L1202** | `CAN0_TX_M0/JTAG_TMS_M0/UART5_CTSN_M2/SAI3_SDI_M1/DSM_AUD_RN_M0/SDMMC` | `GPIO2_A3` 的 mux 里含 `JTAG_TMS_M0` | [官网] |
| **L1308** | `JTAG_TCK_M1/UART0_TX_M0/GPIO0_D4_u` | `GPIO0_D4` 的 mux 里含 `JTAG_TCK_M1` | [官网] |
| **L1310** | `JTAG_TMS_M1/UART0_RX_M0/GPIO0_D5_u` | `GPIO0_D5` 的 mux 里含 `JTAG_TMS_M1` | [官网] |

★**并且**: ★**`grep -cE 'JTAG_TDI|JTAG_TDO'` 在这份 2921 行官方文本层上 = `0`** ★ ⇒ ★**整份官方 datasheet 里，`JTAG_TDI` / `JTAG_TDO` 这两个信号名一次都没出现** ★

★**⇒ 本单对 ISS-375 §2-4 的结论推进（★差异必须写清★）**: ★

| | ★**ISS-375（已签收，本单不改）** ★ | ★**ISS-378（本单）** ★ |
|---|---|---|
| 芯片内部有没有 JTAG 功能 | ★**`[0数据]`** —— 原文：「芯片内部是否具备 JTAG 功能，本单未取得证据，不作断言」 ★ | ★**`[官网]`** —— ★**官方 datasheet L247 明写「JTAG interface for debug」⇒ 芯片【有】JTAG 调试接口** ★（★这是本单相对 ISS-375 的推进，不是翻案：ISS-375 当时只查了脚表，脚表覆盖的是模块引出的脚，够不到芯片特性块★）★ |
| `JTAG_TDI` / `JTAG_TDO` 的球位 | ★**`[0数据]`** ★ | ★**`[0数据]`（不变）** —— ★**官方引脚复用表只有 TCK/TMS ⇒ TDI/TDO 的球位在这份官方文档里查不到** ★ |
| SoM 侧有没有 JTAG 引出 | ★**`[实测]` 无**（脚表命中 0 + 网表 `SoC_NC`）★ | ★**`[实测]` 无**（★与 ISS-375 一致，闸自己复跑 grep★）★ |
| ★**可下的结论句（受控表述）** ★ | —— | ★**「RK3572 芯片官方声明有 JTAG 调试接口（[官网]），但官方引脚复用表只暴露 TCK / TMS 两个 mux 名；TDI / TDO 的球位在官方文档中无记载（[0数据]）；FET3572-C 这版 SoM 的 399 行逐针表里 JTAG 命中 = 0（[实测]）⇒ 板级 JTAG 四线在 SoM 侧不落地 ⇒ JTAG 救砖链（S3）在这版 SoM 上不存在。」** ★ |

★**★本单与任务书派活材料的差（★以本机实读为准★）**: ★
| 项 | 任务书给的 | ★**本机实读** ★ | 差在哪 / 为什么 |
|---|---|---|---|
| `grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv` | 命中 4 行，全是 `JTAG_TCK_M0`/`JTAG_TMS_M0`/`JTAG_TCK_M1`/`JTAG_TMS_M1` | ★**一致**（4 行，同 4 个 mux 名，pins.csv 行号 125/126/167/168）★ | 无差 |
| `grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv` | = 0 | ★**一致**（`0`，grep 退出码 rc=1）★ | 无差 |
| ★**官方 datasheet 文本层的 JTAG 事实** ★ | ★**任务书未给** ★ | ★**5 处命中：L247「JTAG interface for debug」+ 4 处 TCK/TMS mux；`JTAG_TDI`/`JTAG_TDO` 全文档 0 命中** ★ | ★**这是本单新增的一层事实**：它把 ISS-375 留的「芯片内部 JTAG = [0数据]」补成了 `[官网]` 级（芯片有 JTAG 接口），同时把「TDI/TDO 球位」明确留在 `[0数据]` ★ |
| ★**datasheet 文本层文件名大小写** ★ | 任务书写 `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.txt`（大写 R） ★ | ★**盘上实际是 `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`（小写 r）** ★ —— ★**本机文件系统大小写敏感 ⇒ 大写路径 `test -f` 判 MISSING** ★ | ★**官方事实闸 `HW/rk3572_official_facts_check.py` 内部引用的是小写路径 ⇒ 本单实跑 `python3 HW/rk3572_official_facts_check.py` ⇒ rc=0 / 文本层断言 22/22 全中 ⇒ **闸本身没坏，是任务书里的路径大小写写错了** ★ |
| ★**ISS-344 口径页里那条「SW 侧 31 次 JTAG 全是 TCK/TMS/M0/M1 ⇒ 无一命中 TDI」** ★ | —— | ★**现已过期** ★ | ★**`SW/tools/check_debug_pin_order_contract.py`（ISS-375 新闸）自己就含 3 处 `JTAG_TDI`**（L552/742/743）⇒ ★**现在 `grep -rnw JTAG_TDI SW` = 52 行**（含 ISS-375 页与 ISS-344 页本身）★ ⇒ ★**旧句仍成立的部分是「无一命中 TDI **的固件/应用代码**」，但「SW 侧没有 TDI 字面量」这句已经不准了** ⇒ ★**本单不改那一页（订正归 main）★ |

### §4-3 ★**其它必须实读的官方/本机素材（★逐条读过了才写★）★★

| 素材 | 实读到的关键内容 | 用在哪 | 证据等级 |
|---|---|---|---|
| ★**`HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行** ★ | ★**`JTAG_TCK` / `JTAG_TDI` / `JTAG_TDO` / `JTAG_TMS` 四行，原话逐字 = 「逐针表里没有同名/后缀相同的信号 ⇒ 要么是 RK3572 内部命名不同，要么该信号在 FET3576-C 上不存在（⇒ 需换引脚或换板）」** ★ | ★**§3-1 C-1 / §3-2 路线② 的依据（★本单把它当【二选一措辞】读，不替它选边★）** ★ | [实测] |
| ★**`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md`** ★ | ★**官方事实卡 §1 封装 = FCCSP550L / 14.3×15.5mm / 550 球；★§「本项目 demo 主板用的是 SoM 模组（FET3572-C）的 BTB（0.4mm pitch），不是裸 SoC 的 FCCSP ⇒ 那条 pitch 约束不适用于当前布线板** ★ | ★**§4-2 的背景（芯片 vs 模组两级分清）★** | [官网] |
| ★**`HW/rk3572_official_facts_check.py`** ★ | ★**本单实跑 ⇒ rc=0 · 文本层断言 22/22 全中 · PDF md5 `c0e3763036e2f6a3e8a2f68f2254851d` · 文本层 2921 行** ★ | ★**§4-2 官方事实的可复核入口** ★ | [实测] |
| ★**`HW/check_s8_target_list.py:22-24,53-63`** ★ | ★**`REQUIRED_SINGLE` = 8 条单端脚，含 `JTAG_TDI`**；`EXPECT_REQUIRED = 23`；★**它只判「分级 + 本板有没有铜」** ★ | ★**§3-1 C-2** | [实测] |
| ★**`HW/netlist_v1.csv:388/390/392/394`** ★ | ★**四条 `JTAG_*_SOC` 的 SoM 侧端点逐条 = `SoC_NC`** ★ | ★**§1-1 + §2-0 + §3-1 C-1** ★ | [实测] |
| ★**`HW/netlist_v1_pins.csv:202-205,275-276`** ★ | ★**`J_DEBUG.pin1=JTAG_TCK` / `pin2=TMS` / `pin3=TDI` / `pin4=TDO`；`J_UART.pin1=UART_TX` / `pin2=UART_RX`** ★ | ★**§0-1 A 层 + §1-3 依据②** ★ | [实测] |

### §4-4 ★**查不到的部分（★`[0数据]` + 降级方案 · 必填项★）★★

| 缺口 | 等级 | ★**降级方案（不许留成外部待回复形态）** ★ |
|---|---|---|
| ★**`JTAG_TDI` / `JTAG_TDO` 在 RK3572 上的球位** ★ | ★**`[0数据]`** ★（官方 datasheet 2921 行文本层 0 命中）★ | ★**降级 = 按「SoM 不引出 JTAG」设计**：JTAG 四线在板上保留 `J_DEBUG` 位（不装贴片，手工可焊），板侧不承诺 JTAG 链可用 ⇒ 救砖按 S1→S2→S4 三级设计；★**若将来拿到官方 TDI/TDO 球位，那是【新增能力】不是【救现有设计】** ★ |
| ★**原厂是否提供 JTAG 调试器 + 转接板** ★ | ★**`[0数据]`** ★ | ★**降级 = 不依赖**：既然 S3 不存在，产线与返修流程按「S2 必须实测走通 + S4 返厂」设计（`SW/FLASH_AND_VERSION.md` §4.4 已有该骨架）★；★**零外发** ★（★**缺口一律自己网上查 + 标证据等级，查不到就写降级方案**★）★ |
| ★**`J_UART` 的 X 向开口窗口** ★ | ★**`[0数据]`** ★（MECH 侧未定义，见 ISS-375 注 2）★ | ★**降级 = 本页不给 `J_UART` 间隙结论** ★；★**只给针序契约** ★（§1-1 两行）★ |
| ★**芯片内部 TDI/TDO 功能是否存在** ★ | ★**`[0数据]`** ★（官方只暴露 TCK/TMS；芯片特性块只说「有 JTAG interface」没说信号集合）★ | ★**降级 = 不作断言** ★；★**只写「SoM 侧不落地」** ★（★这是 ISS-375 §2-4 已定的表述边界，本单沿用★）★ |

---

## §5 未决项（★只登记 · 不代拍 · 逐条写清「要谁回答什么」★）

| # | 未决项 | ★**要谁回答什么** ★ | 为什么现在就要答 |
|---|---|---|---|
| ★**U-1** ★ | ★**`J_DEBUG` / `J_UART` 的 pin1 朝向选 A（rot90 · 建议）还是 B（rot270）** ★ | ★**main 一句话即可** —— ★**ISS-375 §1-5 已备好两套写死值**（A: `J_DEBUG`→`(141.0450, 56.6000)`/90°/顺排 · `J_UART`→`(18.2550, 68.6000)`/90°/顺排；B: `J_DEBUG`→`(144.8550, 56.6000)`/270°/逆排 · `J_UART`→`(19.5250, 68.6000)`/270°/逆排）★ | ★**纯落点写死，不依赖 SoM 侧结论** ★；★**落晚了 = 板做了机器件还得再改 = 板改两次** ★（§1-3）★ |
| ★**U-2** ★ | ★**ISS-344 对 `JTAG_TDI` 的「必需」分级，在「SoM 侧无 JTAG 引出」这个事实下怎么改口径** ★（§3-2 三条路）★ | ★**main 裁**：★**走 ①（改口径）/ ②（改网表）/ ③（换 SoM）哪条，或 ①+③ 组合** ★；★**若走 ②，还须回答「是否启动 SoM 侧 JTAG 引出方案的前置工作；若是，归 hw-lead 出方案、main 决定是否落表」** ★ | ★**它直接决定「板要对着一个不再变的网表画」** ★（★② 是落表 = 板那一趟的前置条件★）★ |
| ★**U-3** ★ | ★**路线 ① 若被采纳：`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的订正块由谁落、什么时候落** ★ | ★**main** —— ★**本单已把冲突与代价写在 §3-1/§3-2，但该页正文一个字都不许由 sw-lead 改** ★ | ★**订正不落 = 口径页与实测事实长期对撞，下游每次读都踩** ★ |
| ★**U-4** ★ | ★**若走路线 ①/③：`SW/FLASH_AND_VERSION.md:44` / `:336`、`SW/EVT_TEMPLATE.md:503`、`SW/S2_BOARD_TEST_CHECKLIST.md:393` 这 4 处硬规则改成什么** ★ | ★**main 派单给 sw-lead 执行**（★**属 SW 域，本单可做但要等裁决**）★ | ★**S3 没有执行对象 ⇒ 「S2 连续失败 2 次 → 必须升级 S3」这条硬规则现在指向一个不存在的东西** ★ |
| ★**U-5** ★ | ★**`HW/check_s8_target_list.py` 的 `REQUIRED_SINGLE` / `EXPECT_REQUIRED` 要不要跟着改** ★ | ★**hw-lead**（★**该文件属 hw-lead 地界，本单只读，零写入**★）★ | ★**它是 ISS-344 分级在机器侧的投影；口径改了它不改 = 机器闸与口径页分叉** ★ |
| ★**U-6** ★ | ★**路线 ③（换 SoM）是否走** ★ | ★**老板级**（★main 转达）★ | ★**它决定板那一趟开不开工**（★换了 SoM = 板面全变★）★ |
| ★**U-7** ★ | ★**新闸 `SW/tools/check_debug_header_fw_impact.py` 挂不挂进 `state/gate_check.py`** ★ | ★**main** —— ★**本单零挂链**（★`grep -c check_debug_header_fw_impact state/gate_check.py` = **0**★）★ | ★**挂不挂归 main；先例 = ISS-309/312/315/318 都是 SW 侧出结论、main 挂** ★ |
| ★**U-8** ★ | ★**ISS-344 口径页那句「SW 侧 31 次 JTAG 全是 TCK/TMS/M0/M1 ⇒ 无一命中 TDI」已被 ISS-375 的闸自身冲掉（现在 `JTAG_TDI` 在 `SW/**` 命中 52 行，其中代码 3 行）—— 要不要一并订正** ★ | ★**main**（★同 U-3，同一块订正块★）★ | ★**这句话现在会被下游当「SW 侧没有 TDI」引用 ⇒ 误读风险** ★ |

---

## §6 复跑命令（★本页全部数字的出处 · 逐条可复现★）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── 本单新闸 (零挂链 · 裸跑)
python3 SW/tools/check_debug_header_fw_impact.py              # rc=0
python3 SW/tools/check_debug_header_fw_impact.py --selftest   # rc=0 · 末行 ALL TESTS PASS

# ── 既有闸 (只跑不改 · 证明零漂移)
bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py   # rc=0 (ISS-375 已签收闸)

# ── §4 官方自查证 (本单自己跑的两条 grep)
grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv              # 4 行 · 全是 TCK/TMS
grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv                    # 0
grep -icE 'JTAG_TDI|JTAG_TDO' HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt   # 0
grep -n 'JTAG interface for debug' HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt  # L247
python3 HW/rk3572_official_facts_check.py                      # rc=0 · 22/22

# ── §1 逐网表 (自己重读网表, 不抄本页)
sed -n '388,395p' HW/netlist_v1.csv
sed -n '202,205p;275,276p' HW/netlist_v1_pins.csv
grep -nE 'JTAG|UART|BOOT_N|KEY_|RESET_N|USB_CC' HW/netlist_v1.csv | head -60

# ── §1-3 固件零引用 (代码文件口径)
grep -rnw JTAG_TCK SW --exclude-dir=__pycache__ --include='*.py' --include='*.sh' --include='*.json'
grep -rnw JTAG_TDI SW --exclude-dir=__pycache__ --include='*.py' --include='*.sh' --include='*.json'
grep -rn "stty\|> /dev/tty\|write.*tty" SW --exclude-dir=__pycache__

# ── §3 既有口径 (读, 不改)
grep -nE "JTAG_TDI|必需" SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md | head -8
sed -n '48,51p' HW/PCB/SOM_PIN_MAPPING.md
sed -n '22,24p;53,63p' HW/check_s8_target_list.py

# ── §7 边界自证
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
grep -c check_debug_header_fw_impact state/gate_check.py        # 必须 0
grep -c check_debug_pin_order_contract state/gate_check.py       # 既有闸的挂链数 (本单不动它)

# ── 状态机
python3 state/merge.py                                            # rc=0
python3 state/gate_check.py                                       # rc=0 · Q1 18/18
```

★**★本机环境事实（★来自任务书 + 本单实跑确认★）**: ★**`/tmp` 用户配额已打满 ⇒ 任何把门禁输出重定向到 `/tmp` 的写法会出假读数（rc=120 / 0 字节）⇒ 本单全部输出落项目盘 `logs/iss378/` 与 `state/.verify/`** ★

---

## §7 边界自证（★十项逐条★）

| # | 边界 | 自证方式 | 结果 |
|---|---|---|---|
| ★**1** ★ | ★**零写板** ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb` + `stat -c '%y %s'`（开工前 / 交卷后各一次）★ | md5 **`611b869e13518c3c023fb178f91a0075`** · mtime **`2026-11-06 07:07:17.362193413`** · size **`4940213`** ★三项与基线一致 ★（★基线取自 ISS-375 已签收页 §4-2 的同一组读数★）★ |
| ★**2** ★ | ★**零落表** ★ | `md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` ★ | **`6aee500e60ba0732f83a9cf557ba90ab`** / **`9174309df1ec9411ac8e8d9e80ee386a`** / **`5b9993992405904a60ac96a020b375d8`** ★三项与基线一致 ★ |
| ★**3** ★ | ★**零改已签收件（ISS-375 的页与闸）** ★ | `md5sum SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md SW/tools/check_debug_pin_order_contract.py` ★ | ★**本单零写入**（★只引用；引用处一律写清来源页 + 行号★）★ |
| ★**4** ★ | ★**零改既有口径页正文** ★ | `md5sum SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` ★ | ★**本单零写入** —— ★**冲突只登记在 §3-1，订正块归 main（§5 U-3）** ★ |
| ★**5** ★ | ★**零改固件本体** ★ | §1-1「若需改」列只给 **文件 + 行号 + 函数名** ★ | ★**本单只写了 6 条「改哪一行」的清单，一个字都没改** ★（★且那 6 条全在 ISS-375 已签收闸里 ⇒ 改动授权归 main★）★ |
| ★**6** ★ | ★**零挂链** ★ | `grep -c check_debug_header_fw_impact state/gate_check.py` ★ | ★**0** ★（★挂不挂归 main —— §5 U-7★）★ |
| ★**7** ★ | ★**零外发** ★ | 本单未发任何邮件 / 询价 / 问询 / 采购 ★ | ★**零外发** ⇒ §4 的全部事实来自本机盘上官方文件实读；缺口写 `[0数据]` + 降级方案（§4-4）★ |
| ★**8** ★ | ★**不代拍** ★ | §3-3 明写「建议 + 不代拍」★ | ★**`JTAG_TDI` 终裁、pin1 朝向、换 SoM 三项全部标「归 main / 老板裁」** ★ |
| ★**9** ★ | ★**沙盒只落 `tmp/iss378_sbx/` + `logs/iss378/`** ★ | 本单新增目录清单 ★ | ★**只落 `tmp/iss378_sbx/`（空占位）+ `logs/iss378/`（本单日志）+ 本页 + 新闸 + 交卷页 + `state/fragments/sw.yaml`** ★ |
| ★**10** ★ | ★**不自签台账** ★ | `state/issue_log.yaml` ★ | ★**本单零写入** ⇒ 由 main 签收 ★ |

---

> ★**本单不做的事（明写，避免下游误读）**: ★**不改板** · ★**不改网表 / 脚表 / BOM** · ★**不改固件本体** · ★**不改已签收件（ISS-375 的页与闸）** · ★**不改既有口径页正文** · ★**不外发** · ★**不挂任何外部待回复形态** · ★**不代拍 `JTAG_TDI` 冲突的终裁** · ★**不签台账** · ★**不挂链** ★
> ★**要 main 回的两件事**: ★**(1) `J_DEBUG` / `J_UART` 的 pin1 朝向选 A 还是 B（§5 U-1，一句话即可，ISS-375 §1-5 已备好两套写死值）** ★; ★**(2) ISS-344 在「SoM 侧无 JTAG 引出」这个事实下怎么改口径 —— 走 §3-2 的 ①/②/③ 哪条（或 ①+③ 组合）（§5 U-2）** ★

---

## 【追加式订正 (2026-11-24 · sw-lead · ISS-378)】机器块（★闸读这一块 · 不写它闸就没法判★）

★**本页正文与本段无冲突**（★板指纹三项未动 · 网表三件未动 · ISS-375 已签收件未动★）★

```json iss378_contract
{
  "net_rows": [
    {"net": "JTAG_TCK",   "pads": ["J_DEBUG.pin1"], "nature": "需改代码", "change_file": "SW/tools/check_debug_pin_order_contract.py", "change_line": 287, "change_func": "d1_current_board"},
    {"net": "JTAG_TMS",   "pads": ["J_DEBUG.pin2"], "nature": "需改代码", "change_file": "SW/tools/check_debug_pin_order_contract.py", "change_line": 552, "change_func": "d5_netlist_soc_side"},
    {"net": "JTAG_TDI",   "pads": ["J_DEBUG.pin3"], "nature": "需改代码", "change_file": "SW/tools/check_debug_pin_order_contract.py", "change_line": 466, "change_func": "d4_page_matches_computed"},
    {"net": "JTAG_TDO",   "pads": ["J_DEBUG.pin4"], "nature": "需改代码", "change_file": "SW/tools/check_debug_pin_order_contract.py", "change_line": 312, "change_func": "compute_candidate_orders"},
    {"net": "JTAG_TCK_SOC", "pads": [], "nature": "无"},
    {"net": "JTAG_TMS_SOC", "pads": [], "nature": "无"},
    {"net": "JTAG_TDI_SOC", "pads": [], "nature": "无"},
    {"net": "JTAG_TDO_SOC", "pads": [], "nature": "无"},
    {"net": "UART_TX",    "pads": ["J_UART.pin1"], "nature": "需改代码", "change_file": "SW/tools/check_debug_pin_order_contract.py", "change_line": 231, "change_func": "read_current_board"},
    {"net": "UART_RX",    "pads": ["J_UART.pin2"], "nature": "需改代码", "change_file": "SW/tools/check_debug_pin_order_contract.py", "change_line": 231, "change_func": "read_current_board"},
    {"net": "BOOT_N",     "pads": [], "nature": "无"},
    {"net": "KEY_PWR",    "pads": [], "nature": "无"},
    {"net": "KEY_VOL_P",  "pads": [], "nature": "无"},
    {"net": "KEY_VOL_M",  "pads": [], "nature": "无"},
    {"net": "KEY_CAM",    "pads": [], "nature": "无"},
    {"net": "RESET_N",    "pads": [], "nature": "无"},
    {"net": "RESET_N_SOC", "pads": [], "nature": "无"},
    {"net": "USB_CC1",    "pads": [], "nature": "无"},
    {"net": "USB_CC2",    "pads": [], "nature": "无"}
  ],
  "rescue_chains": ["USB", "UART", "JTAG"],
  "worst_case_chain": "USB",
  "resolution_routes": ["①改口径", "②改网表", "③换SoM"],
  "soc_side": {
    "pins_csv": "HW/RK3572_PIN_TABLE/rk3572_pins.csv",
    "jtag_hit_lines": 4,
    "mux_names": ["JTAG_TCK_M0", "JTAG_TMS_M0", "JTAG_TCK_M1", "JTAG_TMS_M1"],
    "has_tck": true,
    "has_tms": true,
    "has_tdi": false,
    "has_tdo": false
  },
  "som_side": {
    "pin_table": "HW/PCB/FET3572C_PIN_TABLE.csv",
    "jtag_hits": 0,
    "conclusion": "SoM 侧无 JTAG 引出"
  },
  "netlist_soc_endpoints": {
    "JTAG_TCK_SOC": "SoC_NC",
    "JTAG_TMS_SOC": "SoC_NC",
    "JTAG_TDI_SOC": "SoC_NC",
    "JTAG_TDO_SOC": "SoC_NC"
  },
  "baseline": {
    "board_md5": "611b869e13518c3c023fb178f91a0075",
    "board_mtime": "2026-11-06 07:07:17.362193413",
    "board_size": 4940213,
    "netlist_md5": "6aee500e60ba0732f83a9cf557ba90ab",
    "pins_md5": "9174309df1ec9411ac8e8d9e80ee386a",
    "bom_md5": "5b9993992405904a60ac96a020b375d8"
  }
}
```
