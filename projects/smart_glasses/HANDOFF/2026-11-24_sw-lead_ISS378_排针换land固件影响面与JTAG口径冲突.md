# [sw-lead→PM] ISS-378 · 排针换 land 后的固件影响面 + `JTAG_TDI` 口径冲突 (SoC/SoM 两侧 JTAG 自查证)

- 发起方: sw-lead
- 日期: 2026-11-24 (任务书落款 2026-11-24 · 本单为 **cont1 收尾**)
- 结论: ★**两块排针 (`J_DEBUG` 1×4 / `J_UART` 1×2) 换 land 对固件的影响 = 【物理针序 / 救砖线序】这一层受影响，【网名 → pad 号】映射这一层完全不受影响 ⇒ 固件本体 0 行要改**；★**要改的是「把针序写死的 SW 侧机器件」与「把线序写死的工装/线序说明」，而这两样都由「pin1 朝向选 A 还是 B」这一个裁决决定**；★**`JTAG_TDI` 的「必需」分级与网表现状 (`JTAG_TDI_SOC` 的 SoM 侧端点 = `SoC_NC`) 正面冲突 ⇒ 三条路 (①改口径 / ②改网表 / ③换 SoM) 的代价已算清，但两条裁决都归 main / 老板裁，本单不代拍** ★
- 依据: ★**`SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (55,076 B @11-24 02:45 · 逐网影响面清单页 · 本趟一个字未改)** ★ · ★**`SW/tools/check_debug_header_fw_impact.py` (37,515 B @11-24 02:45 · 新闸 W0~W8)** ★ · `logs/iss378/` (3 份闸日志) · `logs/iss378_official_facts_check.log` (官方事实闸 rc=0 · 22/22) · `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (ISS-375 已签收 · **只引用, 一字未改**)
- ★**本单状态**: ★**cont1 收尾** ⇒ ★**主产物 (清单页 + 新闸 + 闸日志) 已在盘且已被 main 独立复跑验证过 (裸跑 rc=0 / W0~W8 全绿 + `--selftest` rc=0 / 14/14 ALL TESTS PASS) ⇒ ★**本趟只补两件: 交卷页 + 分片登记** ★

---

## B1 结论摘要

### ★B1-① 一句话结论 (★本单最核心的一句★) ★

> ★**换 land 对固件的影响，要拆成两层说，拆完就只有一句：**
> ★**A 层「网名 → pad 号」映射 ⇒ 完全不变 ⇒ 固件本体 0 行要改；B 层「物理针序 / 救砖线序」⇒ 会变 ⇒ 要改的是把针序写死的 SW 侧机器件 + 工装线序说明。**
> ★**而 B 层往哪边写，只由「`J_DEBUG`/`J_UART` 的 pin1 朝向选 A(rot90) 还是 B(rot270)」这一个裁决决定 ⇒ 板只改一次 ⇒ 这一个裁决必须在板那一趟开工前落。** ★

| 层 | 换 land 后变不变 | 依据 | 谁受影响 |
|---|---|---|---|
| ★**A 层：网名 → pad 号 映射** (`J_DEBUG.pin1 = JTAG_TCK` 这类**逻辑**对应) ★ | ★**不变** ★ | 网表 `HW/netlist_v1_pins.csv:202-205` (`J_DEBUG.pin1=JTAG_TCK` / `pin2=TMS` / `pin3=TDI` / `pin4=TDO`) 与 `:275-276` (`J_UART.pin1=UART_TX` / `pin2=UART_RX`) 写的是**逻辑针号**；两个候选 land 都保持 `pad1=JTAG_TCK` ⇒ 逻辑映射逐字不变 ★ | ★**没有人** ★ (固件 / 网表 / BOM / 脚本一律零改动) ★ |
| ★**B 层：物理针序 / 救砖线序** (哪个物理位置是 pin1、TX 在左还是在右) ★ | ★**变** ★ (候选 A rot90 = 与现状同向；候选 B rot270 = **逆序**) ★ | `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` §1-3/§1-4 (ISS-375 实测：两候选 pad 绝对 X 集合逐字相同，**pad→X 序互为逆序**) ★ | ★**排线 / 工装 / 线序说明 + 把针序写死的 SW 侧机器件** ★ |

### ★B1-② 「固件本体要改几行」的最终答案 = ★0 行★ ★

★**依据（三条，逐条可复跑）**: ★
1. ★**固件侧零网名引用** —— `JTAG_TCK` / `JTAG_TMS` / `JTAG_TDI` / `JTAG_TDO` / `UART_TX` / `UART_RX` 在 `SW/**` 的**代码文件** (`.py`/`.sh`/`.json`) 里命中 **0 行** (JTAG 组唯一的 5 处全在 `SW/tools/check_debug_pin_order_contract.py` = **板针序契约闸**，不是固件；UART 组唯一 1 处 `stty|> /dev/tty|write.*tty` 命中是 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:125` 的**自引用记录**) ⇒ **[实测]** ★
2. ★**逻辑映射逐字不变** —— `HW/netlist_v1_pins.csv:202-205,275-276` 的 `J_DEBUG.pinN` / `J_UART.pinN` → 网名对应，在两个候选 land 下都不变 ⇒ **[实测]** ★
3. ★**要改的是「把物理针序写死」的机器件，不是固件** —— `SW/tools/check_debug_pin_order_contract.py` 的 `read_current_board()` / `d1_current_board()` / `compute_candidate_orders()` / `d4_page_matches_computed()` / `d5_netlist_soc_side()` **五处**读的是**板面现状读数** ⇒ 板一换 land，这五处**必然变红** ⇒ ★**改它们是「板那一趟」的活，不是「固件改动」，且该文件是 ISS-375 已签收件 ⇒ 改的授权归 main** ★

### ★B1-③ 逐网影响表（★19 行 · 主表 · 照抄清单页 §1-1·一字不改数值★）★

> ★**读表三条（每条都是判据）**: ①「当前落在哪颗件哪个 pad」列的写法 = `器件.pinN` 或 `器件.焊盘号`，与 `HW/netlist_v1_pins.csv` 的 `pin_id` 列逐字同形；②「变化性质」列只有三个合法取值 `无` / `仅物理针序` / `需改代码`；③「若需改」列只写【文件 + 行号 + 函数名】，★**本单一个字都不许改** ★

| 网名 | 两端节点 | 当前落在哪颗件哪个 pad | 固件侧当前用法 | 换 land 后是否变化 | 变化性质 | 若需改: 改哪个文件的哪一行 | 证据等级 | 来源 (文件:行号) |
|---|---|---|---|---|---|---|---|---|
| `JTAG_TCK` | `J_DEBUG pin1` / `R_JTAG_TCK` / `TP_JTAG` | `J_DEBUG.pin1` + `R_JTAG_TCK` (100Ω 串阻) + `TP_JTAG` | ★**固件零引用** —— `SW/**` 代码文件命中 **5 处，全部在 `SW/tools/check_debug_pin_order_contract.py`** (L552 / L742 / L743 / L758 / L759) ⇒ 那是**板针序契约闸**，不是固件；文档侧只有 S3 救砖脚手架 | ★电气映射**不变**；B 层物理针序在 rot270 候选下**反转** | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L287** `d1_current_board()` —— 换 land 后 `pad1_x` / `pad_shape` / `pad_attr` / `pad1_marker` 四项读数与页 `current` 块要同步 | [实测] | `HW/netlist_v1.csv:368,389` · `HW/netlist_v1_pins.csv:202` · `SW/tools/check_debug_pin_order_contract.py:287,552` |
| `JTAG_TMS` | `J_DEBUG pin2` / `R_JTAG_TMS` | `J_DEBUG.pin2` + `R_JTAG_TMS` (100Ω 串阻) | ★**固件零引用** —— 同上，代码侧只命中 `check_debug_pin_order_contract.py:552` 的四网元组 | ★电气映射**不变**；rot270 候选下物理针序反转 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L552** `d5_netlist_soc_side()` —— JTAG 四网元组随新板重核 | [实测] | `HW/netlist_v1.csv:391` · `HW/netlist_v1_pins.csv:203` · `SW/tools/check_debug_pin_order_contract.py:520,552` |
| `JTAG_TDI` | `J_DEBUG pin3` / `R_JTAG_TDI` | `J_DEBUG.pin3` + `R_JTAG_TDI` (100Ω 串阻) | ★**固件零引用** —— `grep -rnw JTAG_TDI SW` = **52 行**，但代码侧只有 `check_debug_pin_order_contract.py:552,742,743` 3 处 (都是**针序契约闸**)；★**`JTAG_TDI` 在板面是 0 段铜** (ISS-375 实测) ⇒ 它现在物理上就是断的 ★ | ★电气映射**不变**；rot270 候选下物理针序反转 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L466** `d4_page_matches_computed()` —— `net_by_pad` 读取源 + `order_by_x` 判定源 | [实测] | `HW/netlist_v1.csv:393` · `HW/netlist_v1_pins.csv:204` · `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md:201,270` |
| `JTAG_TDO` | `J_DEBUG pin4` / `R_JTAG_TDO` | `J_DEBUG.pin4` + `R_JTAG_TDO` (100Ω 串阻) | ★**固件零引用** (代码侧只命中 `check_debug_pin_order_contract.py:552,742,743`) | ★电气映射**不变**；rot270 候选下物理针序反转 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L312** `compute_candidate_orders()` —— 候选几何随新 land 重算 (pad 绝对 X 集合) | [实测] | `HW/netlist_v1.csv:395` · `HW/netlist_v1_pins.csv:205` · `SW/tools/check_debug_pin_order_contract.py:312` |
| `JTAG_TCK_SOC` | `R_JTAG_TCK` / `SoC_NC` | `R_JTAG_TCK.1` ↔ ★**`SoC_NC`（占位，无实物焊盘）** ★ | ★**固件零引用**；★**SoM 侧端点 = `SoC_NC` ⇒ JTAG 链在 SoM 那一头接不到任何 SoM 引脚** ★ | ★**不变** (`SoC_NC` 与排针 land 无关) | 无 | — | [实测] | `HW/netlist_v1.csv:388` |
| `JTAG_TMS_SOC` | `R_JTAG_TMS` / `SoC_NC` | `R_JTAG_TMS.1` ↔ ★**`SoC_NC`** ★ | ★**固件零引用**；SoM 侧端点 = `SoC_NC` | ★**不变** | 无 | — | [实测] | `HW/netlist_v1.csv:390` |
| `JTAG_TDI_SOC` | `R_JTAG_TDI` / `SoC_NC` | `R_JTAG_TDI.1` ↔ ★**`SoC_NC`** ★ | ★**固件零引用**；★**这一条就是 ISS-344 与本单冲突的落点** (ISS-344 把 `JTAG_TDI` 判「必需 · 板侧不许标 NC」，而网表 SoM 侧就是 `SoC_NC`) ★ | ★**不变** | 无 | — | [实测] | `HW/netlist_v1.csv:392` · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:120,152` |
| `JTAG_TDO_SOC` | `R_JTAG_TDO` / `SoC_NC` | `R_JTAG_TDO.1` ↔ ★**`SoC_NC`** ★ | ★**固件零引用**；SoM 侧端点 = `SoC_NC` | ★**不变** | 无 | — | [实测] | `HW/netlist_v1.csv:394` |
| `UART_TX` | `J_UART pin1` / `J_SOM_P2 pin7` / `TP_UART` | `J_UART.pin1` + `J_SOM_P2.pin7` + `TP_UART.pad1` | ★**主机侧只读日志链** —— `SW/tools/s2_board_run.sh` 的 `collect_forensics()` 串口抓取段只做 `timeout "${SECS}" cat "$SERDEV" > "$SER"` (**板→主机**)；`SW/tools/s2_rescue_config.json:230` 的 `_readme` 明写「板端串口（取日志用）」⇒ **固件侧只把日志吐出来，SW 侧从不往板里写** ★ | ★电气映射**不变**；rot270 候选下**物理 TX/RX 位置互换** ⇒ 工装线序要反 | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L231** `read_current_board()` —— `J_UART` 现状读数源 (`pad1_x` / `pad_shape` / `pad_attr` / `pad1_marker`) | [实测] | `HW/netlist_v1.csv:369,397` · `HW/netlist_v1_pins.csv:275` · `SW/tools/s2_board_run.sh:243,256` · `SW/tools/s2_rescue_config.json:230` · `SW/tools/check_debug_pin_order_contract.py:231` |
| `UART_RX` | `J_UART pin2` / `J_SOM_P2 pin9` | `J_UART.pin2` + `J_SOM_P2.pin9` | ★**主机→板方向零需求** —— ★**`stty` / `> /dev/tty` / `write..tty` 三个模式在 `SW` 的**代码文件**里命中 = 0 行** (唯一 1 处命中是 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:125` 这条口径页自己的记录 ⇒ 自引用) ⇒ SW 侧**从不往板里写串口** ★ | ★电气映射**不变**；rot270 候选下物理 RX 位置互换 ⇒ 工装线序要反 (**代码本体不用改**) ★ | **需改代码** | `SW/tools/check_debug_pin_order_contract.py` : **L231** `read_current_board()` —— `J_UART` 现状读数源 (与 `UART_TX` 同一处读数，两行一起改) | [实测] | `HW/netlist_v1.csv:398,399` · `HW/netlist_v1_pins.csv:276` · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:125,156` |
| `BOOT_N` | `J_SOM_P1 pin28` / `R_PU_BOOT_N` / `SW_BOOT` / `TP_BOOT` | `J_SOM_P1.pin28` + `R_PU_BOOT_N` (10k 上拉 1.8V) + `SW_BOOT` + `TP_BOOT` | ★**固件零引用** —— 代码侧只在 `SW/tools/timing_check.py:1654` 与 `:2202` 的**判据文字串**里出现 (不是逻辑分支) ★ | ★**完全不变** ★ —— ★**`BOOT_N` 一根都不经过 `J_DEBUG` / `J_UART`** (它走 `J_SOM_P1.pin28` + 独立按键 + 独立测试点) ⇒ **与本次换 land 零交集** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:367,384,386` · `SW/tools/timing_check.py:1654,2202` |
| `KEY_PWR` | `J_SOM_P1 pin64` / `R_KEY_PWR` / `SW_KEY_PWR` / `C_KEY_PWR` / `TP_KEY_PWR` | `J_SOM_P1.pin64` + `R_KEY_PWR` (10k) + `C_KEY_PWR` (100nF) + `SW_KEY_PWR` + `TP_KEY_PWR` | ★**固件零引用** (`grep -rnw KEY_PWR SW` 代码文件 = 0 行) ★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:309,310,313,363` |
| `KEY_VOL_P` | `J_SOM_P2 pin13` / `R_KEY_VP` / `SW_KEY_VP` / `C_KEY_VP` / `TP_KEY_VP` | `J_SOM_P2.pin13` + `R_KEY_VP` (10k) + `C_KEY_VP` (100nF) + `SW_KEY_VP` + `TP_KEY_VP` | ★**固件零引用** (代码文件 = 0 行) ★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:314,315,318,364` |
| `KEY_VOL_M` | `J_SOM_P4 pin1` / `R_KEY_VM` / `SW_KEY_VM` / `C_KEY_VM` / `TP_KEY_VM` | `J_SOM_P4.pin1` + `R_KEY_VM` (10k) + `C_KEY_VM` (100nF) + `SW_KEY_VM` + `TP_KEY_VM` | ★**固件零引用** (代码文件 = 0 行) ★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:319,320,323,365` |
| `KEY_CAM` | `J_SOM_P4 pin3` / `R_KEY_CAM` / `SW_KEY_CAM` / `C_KEY_CAM` / `TP_KEY_CAM` | `J_SOM_P4.pin3` + `R_KEY_CAM` (10k) + `C_KEY_CAM` (100nF) + `SW_KEY_CAM` (★整条 **DNP** ★) | ★**固件零引用** (`grep -rnw KEY_CAM SW` = **0 行**) ★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:324,325,328` |
| `RESET_N` | `Q_AND` / `R_PU_RESET_N` / `R_SER_RESET_N` / `SW_RST` / `U_SUPV pin1` / `TP_RESET` | `SW_RST` (按键) + `TP_RESET` + `R_PU_RESET_N` + `R_SER_RESET_N` + `U_SUPV.pin1` + `Q_AND` | ★**固件零引用** ★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:65,366,377,382,409` |
| `RESET_N_SOC` | `R_SER_RESET_N` / `J_SOM_P2 pin100` / `C_RST` | `R_SER_RESET_N` (1k) + `C_RST` (100nF) + `J_SOM_P2.pin100` | ★**固件零引用**；唯一「代码侧出现」是 `SW/tools/timing_check.py:1111` 读 `RESET_N_SOC` 的 note 算 τ (**读网表**，不是驱动这个脚) ★ | ★**完全不变** ★ —— ★**不经过 `J_DEBUG` / `J_UART`** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:379,380` · `SW/tools/timing_check.py:1111` |
| `USB_CC1` | `J_USB_C A5` / `R_CC1_D` / `J_TYPE_C A5` / `R_CC1` | `J_USB_C.A5` + `R_CC1_D` (5.1k Rd) + (充电板) `J_TYPE_C.A5` + `R_CC1` | ★**固件零引用**；SW 侧只有 `SW/tools/check_sw_ref_reachability.py:178`/`:185` 与 `check_sw_ref_reachability_v2.py:237`/`:244` 硬编码位号 `"J_TYPE_C"` (★**`J_TYPE_C` 不在官方板上** —— 那是充电板侧的件) ★ | ★**完全不变** ★ —— ★**USB 走板载 Type-C `J_USB_C` (`HW/netlist_v1.csv:428`)，与 `J_DEBUG` / `J_UART` 不同束、不同器件** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:293,428,456` · `SW/tools/check_sw_ref_reachability.py:178,185` |
| `USB_CC2` | `J_USB_C B5` / `R_CC2_D` / `J_TYPE_C B5` / `R_CC2` | `J_USB_C.B5` + `R_CC2_D` (5.1k Rd) + (充电板) `J_TYPE_C.B5` + `R_CC2` | ★**固件零引用** (同上，`"J_TYPE_C"` 硬编码在两个可达性闸里)；★**这是 ISS-344 8 条「必需」里的另一条**，与 `JTAG_TDI` 同属「必需 vs 现实」的对撞候选 ★ | ★**完全不变** ★ —— ★**与排针不同束** ★ | 无 | — | [实测] | `HW/netlist_v1.csv:294,297,429,457` · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:126,157` |

★**候选对照 (A / B 之下每一行的实际变化 · 照抄清单页 §1-2)★**:

| 网组 | 候选 A（rot90 · ISS-375 建议） | 候选 B（rot270） | §B1-③ 取值 |
|---|---|---|---|
| `JTAG_TCK` / `TMS` / `TDI` / `TDO` | ★**电气映射不变 + 物理针序与现状同向 (顺排 TCK→TMS→TDI→TDO)** ⇒ **线序说明零改动** ★ | ★**电气映射不变 + 物理针序反转 (逆排 TDO→TDI→TMS→TCK)** ⇒ **全部现有 JTAG 线序描述必须反转** ★ | `需改代码` (取严档) ★ |
| `UART_TX` / `UART_RX` | ★**电气映射不变 + 物理顺序与现状同向 (TX→RX)** ★ | ★**电气映射不变 + 物理顺序反转 (RX→TX)** ⇒ 工装线序要反 ★ | `需改代码` (取严档) ★ |
| `JTAG_*_SOC` ×4 | ★**不变** ★ | ★**不变** ★ | `无` ★ |
| `BOOT_N` / `KEY_*` ×4 / `RESET_N` / `RESET_N_SOC` / `USB_CC1` / `USB_CC2` | ★**不变** (不经过排针) ★ | ★**不变** (不经过排针) ★ | `无` ★ |

### ★B1-④ 三条救砖链 (★硬需求节 · 照抄清单页 §2★) ★

`SW/FLASH_AND_VERSION.md:44` (结论 5) 明写 4 级：**S1 看门狗+systemd 自恢复 → S2 BOOT 模式强制重刷 → S3 JTAG → S4 返厂换板**；`:336` (§4.4 表) 是 S3 那一行。

| 链 | 对应救砖级 | 物理载体（板面） | 现状能不能救 | 换 land 后还能不能救 | 断了会死在哪一步 | 降级路径 |
|---|---|---|---|---|---|---|
| ★**USB 链** ★ | ★**S2** (BOOT 模式 + 厂商下载工具强制重刷) ★ | 板载 Type-C `J_USB_C` (`HW/netlist_v1.csv:428/429` USB_CC1/CC2 + `:292` USB 差分 → `J_SOM_P1`) ★**不经过 `J_DEBUG` / `J_UART`** ★ | ★**能（工具链侧已自查结案）** —— Rockusb MaskROM/Loader + 官方开源 `rkdeveloptool` 路线 (ISS-270 自查结案，登记在 `state/fragments/sw.yaml` 的 `fw_vendor_toolchain` / `fw_usb_boot_phy` / `fw_boot_entry_cond` 三条)；★**BOOT 态识别判据已有机器件**: `SW/tools/boot_rescue_probe.py` + `SW/tools/s2_rescue_config.json:92` 的 `usb_signatures` 块 ★ | ★**能，且零影响** ★ —— ★**USB 走 `J_USB_C`，与两块排针不同束、不同器件、不同走线 ⇒ 换 land 对 USB 链零影响** ★ | ★**死 S2** —— 进不了 BOOT 模式 或 下载工具认不出设备 ⇒ 刷不回来 ⇒ 直接跳 S4 ★ | ★**S2 不可用 ⇒ S4 返厂**；★**S1 只救应用层崩溃，救不了 bootloader 损坏** ★ |
| ★**UART 链** ★ | ★**不属救砖级** (= **日志观测链**) ★ | `J_UART` 1×2 排针 (`HW/netlist_v1_pins.csv:275-276`) + `TP_UART` (`:369`) + `J_SOM_P2.pin7/9` (`:397/398`) ★ | ★**能（观测链）** —— `SW/tools/s2_board_run.sh:243-263` 的 `collect_forensics()` 只做 `cat "$SERDEV" > "$SER"` (板→主机)；`SW/S2_BOARD_TEST_CHECKLIST.md:94` 工位准备表写成「USB-TTL 串口线 + 笔记本 | 能看 U-Boot / kernel 串口输出」；★**`J_UART` 整件 dnp = 可选** ★ | ★**能** —— 候选 A 物理顺序不变 ⇒ 工装零改；候选 B TX/RX 物理位置互换 ⇒ **工装线序要反** (软件侧只读方向，逻辑不变) ★ | ★**只丢日志观测** —— ★**UART 链断了不影响任何救砖级** ⇒ 现场变成「盲刷」：刷完起不来时**看不到 U-Boot/kernel 输出**，诊断信息少一维 | ★**无降级** (它本来就不是救砖链) ★ ⇒ 断链的代价 = **诊断能力下降**，不是救砖能力下降 ★ |
| ★**JTAG 链** ★ | ★**S3** (JTAG 调试器接 SoC) ★ | `J_DEBUG` 1×4 排针 (`HW/netlist_v1_pins.csv:202-205`) + 四颗 100Ω 串阻 (`R_JTAG_TCK/TMS/TDI/TDO`) + `TP_JTAG` (`:368`) ★ | ★**不能** ★ —— ★**SoM 侧不落地**: 四条 `JTAG_*_SOC` 的 SoM 侧端点**全部 = `SoC_NC`** (`HW/netlist_v1.csv:388/390/392/394`) ★ + ★**`HW/PCB/FET3572C_PIN_TABLE.csv` (399 数据行) 里 `JTAG` 命中 = 0** ★ ⇒ ★**S3 在这一版 SoM 上不存在** ★ | ★**还是不能** ★ —— ★**换 land 只改排针的物理针序与 pad 形状，改不了「SoM 侧没有 JTAG 引出」这个事实** ⇒ ★**S3 不会因为换 land 而活过来，也不会因为换 land 而更死** ★ | ★**死 S3** —— bootloader 损坏时 S2 进不去 ⇒ ★**唯一还能走的一级不存在** ⇒ 直接死 **S4** ★ | ★**降级路径 = S4 返厂换板** (`SW/FLASH_AND_VERSION.md:336` 的 S4 行) ⇒ ★**`SW/EVT_TEMPLATE.md:503` 的硬规则「S2 连续失败 2 次 → 必须升级 S3 (JTAG)」在事实层面无执行对象** ★ |

★**「最坏只剩哪条链」的一句话结论（★必答★）★**:

> ★**最坏情况下只剩 USB（S2）这一条链** —— ★**因为 JTAG（S3）链在本版 SoM 上【根本不存在】、UART 只做日志观测不做救砖** ★；★**而若连 USB（S2）也不可用 (BOOT 进不去 / 下载工具不认设备)，那就【一条链都不剩】，只剩 S4 返厂换板** ★。
>
> ★**换 land 不改变这个结论** —— ★**换 land 只新增了一种人为失效模式 (排线插反)**，它把「USB 链可用」变成「USB 链因插反而不可用」⇒ ★**最坏路径 = 插反 + S2 不可用 ⇒ 直接 S4** ★。
> ★**⇒ 板那一趟必须把 pin1 朝向 + 线序一次写死 (ISS-375 §1-5 已备好两套写死值)，否则这一种人为失效模式是【无标记、不可见】的** ★（★现状板面 `J_DEBUG` 4 个 pad 全 `RECT`/全 `SMD` ⇒ **看不出哪端是 pin1**；换官方 land 后 pad1 变 `thru_hole rect` ⇒ **第一次变成实物可见**★）。
> ★**代价侧的硬数字**: 排针间距 **1.27 mm** (P1.27mm 官方 land) · 现状 `J_DEBUG` 4 pad 尺寸 0.275 × 0.900 mm · fab 外框 6.7262 × 2.2000 mm ⇒ ★**插反的代价 = 一台眼镜从「可现场救」变成「只能返厂」，总延迟完全压在产线返修上** ★

### ★B1-⑤ `JTAG_TDI` 口径冲突登记 (★事实句 vs 裁决句 · 照抄清单页 §3-1★) ★

> ★**一句话（本节机器判定句）**: ★**SoM 侧无 JTAG 引出** ⇒ ★**JTAG 链在板级不落地** ⇒ ★**ISS-344 的「必需」分级在本版 SoM 上【没有物理兑现对象】** ★（★**依据 = B1-⑥ 的实测：SoM 逐针表 399 行 `JTAG` 命中 0 + 网表四条 `JTAG_*_SOC` 的 SoM 侧端点全部 `SoC_NC` + 官方 datasheet 引脚复用表只列 TCK/TMS**★）★

| # | 既有裁决（读，不改） | 本单实读事实 | 冲突性质 |
|---|---|---|---|
| ★**C-1** ★ | `JTAG_TDI` = ★**必需** ★ · ★**进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ —— `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:120` + `:152` + 6 处 `ISS344-CORR` 块 ★ | ★**`JTAG_TDI_SOC` 的 SoM 侧端点 = `SoC_NC`** (`HW/netlist_v1.csv:392`) ★ ⇒ ★**裁决的「不许标 NC」与网表的 `SoC_NC` 占位直接对撞** ★ | ★**正面冲突** ★ |
| ★**C-2** ★ | 机器真源 `HW/check_s8_target_list.py:55-56` 把 `JTAG_TDI` 写进 `REQUIRED_SINGLE` (8 条单端脚之一)，并在 `:23-24` 逐字沿用 main 2026-11-22 20:5x 口径 ★ | ★**该脚本只判「分级 + 本板有没有铜」，不判「SoM 侧有没有这个脚」** ⇒ ★**分级成立，但它的物理前提 (SoC 侧有 JTAG 可接) 被本单证伪** ★ | ★**裁决内部自洽 · 前提被证伪** ★ |
| ★**C-3** ★ | `SW/FLASH_AND_VERSION.md:44` (4 级救砖 S3=JTAG) + `:336` (S3 行) + `SW/EVT_TEMPLATE.md:503` (硬规则「S2 连续失败 2 次 → 必须升级 S3」) + `SW/S2_BOARD_TEST_CHECKLIST.md:393` ★ | ★**S3 在这一版 SoM 上不存在** (B1-⑥ 全部实测) ★ ⇒ ★**这 4 处硬规则没有执行对象** ★ | ★**执行链断** ★ |
| ★**C-4** ★ | `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md:156` (`UART_RX` 行) 已被 ISS344-CORR 改判「必需 · 进 S8 布线目标」★ | ★**`UART_RX` 在板面是 0 段铜** (ISS-375 实测)；★**主机侧只用读方向** ⇒ ★**它的「必需」是可以靠布线补上的 (不依赖 SoM 侧) ⇒ 与 `JTAG_TDI` 不同类** ★ | ★**同类问题 · 不同解法** ★（★`UART_RX` 缺的是**板上的铜**，`JTAG_TDI` 缺的是**SoM 上那个脚** ⇒ ★**后者不是布线能解决的**★）★ |

### ★B1-⑥ 三条路 (★逐条: 依据 / 代价 / 牵连面 / 要谁拍 · 照抄清单页 §3-2★) ★

#### ★路线 ① —— 改口径（把 `JTAG_TDI` 从「必需」降级 / 标成板侧 NC）★

| 项 | 内容 |
|---|---|
| ★**依据** ★ | ★**SoM 侧没有 JTAG 可接是既成事实** (B1-⑥ 实测：399 行脚表 `JTAG` 命中 0；网表 SoM 侧 = `SoC_NC`；官方 datasheet 引脚复用表只有 TCK/TMS) ⇒ ★**「必需」这个分级在物理上无法兑现** ★ |
| ★**代价 1（口径层）** ★ | ★**与 ISS-344 终裁正面冲突** ⇒ ★**需 main 重开裁** (★sw-lead 不自行改写既有裁决★) ★ |
| ★**代价 2（文件层）** ★ | ★**`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 有 6 处 `ISS344-CORR` 块 + §0/§Q1/§Q2/§3/§3-1/§5/§7 多处投影要连带改** (★**该页正文本单一个字都不许改 ⇒ 订正块归 main**★) ★ |
| ★**代价 3（救砖层）** ★ | ★**`SW/FLASH_AND_VERSION.md:44` + `:336` (S3 行) + `SW/EVT_TEMPLATE.md:503` + `SW/S2_BOARD_TEST_CHECKLIST.md:393` 这 4 处硬规则失去执行对象** ⇒ ★**须同步降级为「S3 不可用 ⇒ 直接 S4」** ★ |
| ★**代价 4（板侧，最小）** ★ | ★**`J_DEBUG` 的 4 根线在板那一趟【不用改线序设计】** ⇒ ★**这是三条路里唯一【板那一趟零额外动作】的一条** ★ |
| ★**代价 5（能力）** ★ | ★**救砖能力从「4 级」降为「3 级」** (S1 → S2 → S4) ⇒ ★**量产变砖只能返厂；变砖到返厂的总延迟没有 SW 侧兜底** ★ |
| ★**牵连面** ★ | ★**SW 域**: `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` (6+ 处) · `SW/FLASH_AND_VERSION.md` (2 处) · `SW/EVT_TEMPLATE.md` (1 处) · `SW/S2_BOARD_TEST_CHECKLIST.md` (1 处)★　★**HW 域**: `HW/check_s8_target_list.py` 的 `REQUIRED_SINGLE` 列表 + `EXPECT_REQUIRED = 23` (**该文件属 hw-lead 地界，本单只读**)★　★**板面**: 无 ★ |
| ★**要谁拍** ★ | ★**main** (重开 ISS-344 的分级裁决；**落订正块也归 main**)★ —— ★**不是老板级** (不改产品功能、不改锁死变量，只改「可执行性分级」) ★ |

#### ★路线 ② —— 改网表（把 `JTAG_*_SOC` 的 SoM 侧从 `SoC_NC` 改到某个真 SoM 引脚）★

| 项 | 内容 |
|---|---|
| ★**依据** ★ | ★**若 SoM 侧能引出 JTAG，则四级救砖恢复完整** ★ |
| ★**★但这条路当前走不通（决定性事实）★** ★ | ★**`HW/PCB/FET3572C_PIN_TABLE.csv` (1 表头 + 399 数据行) 里 `JTAG` 命中 = 0** (★`grep -ic jtag` 实测输出 `0`★) ⇒ ★**没有可指向的脚** ⇒ ★**改网表不是「改四行」，是「先要有一个能引出 JTAG 的 SoM」** ★ |
| ★**代价 1（前置）** ★ | ★**必须先出「SoM 侧 JTAG 怎么引出」的方案** (换 SoM 型号 / 原厂加引脚 / 走别的调试口) ⇒ ★**这是一件独立的前置工作，不是改网表能单独完成的** ★ |
| ★**代价 2（落表）** ★ | ★**改网表 = 落表动作** ⇒ ★**违反本单「零落表」边界** ⇒ ★**须由 main 在落表窗口内走流程 (落表台账 + 三件 md5 全动)** ⇒ ★**所有既有闸的 md5 基线要跟着前移** ★ |
| ★**代价 3（牵连）** ★ | ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 全变** ⇒ ★**板那一趟之前落表 = 板 md5 不变但表 md5 变 (可接受)，板那一趟之后落表 = 板改两次 (不可接受)** ★ ⇒ ★**⇒ 路线 ② 若被采纳，其落表窗口必须【早于或并入】板那一趟** ★ |
| ★**代价 4（板面）** ★ | ★**要新增 SoM 侧 JTAG 走线 ⇒ 板面布线量增加 ⇒ 可能挤占 `J_DEBUG` 开口窗口 (ISS-371 口径，单边间隙 CRIT 0.60 mm) ⇒ ★**要重跑一次间隙/DRC** ★ |
| ★**牵连面** ★ | ★**HW 域**: 网表三件 + BOM + `HW/check_s8_target_list.py` + 板面布线 ★　★**SW 域**: 救砖 4 级表的 S3 行 (**恢复**而非降级)★　★**MECH 域**: 开口窗口可能要重算 ★ |
| ★**要谁拍** ★ | ★**main** (是否启动「SoM 侧 JTAG 引出方案」这条前置工作；若是，**归 hw-lead 出方案、main 决定是否落表**)★ —— ★**若涉及换 SoM 型号 ⇒ 升级到老板级** ★ |

#### ★路线 ③ —— 换 SoM（放弃 S3 软救砖，只留 S4 返厂）★

| 项 | 内容 |
|---|---|
| ★**依据** ★ | ★**若这版 SoM 不引 JTAG 且不打算换 SoM 方案，则 S3 必须被正式放弃** ★ |
| ★**代价 1（最大）** ★ | ★**量产眼镜变砖 ⇒ 只能 S4 返厂换件** ⇒ ★**返修成本与周期全压在产线** ⇒ ★**`SW/FLASH_AND_VERSION.md` 产线硬要求「每台眼镜交付前必须实测走通一次 S2」的压力全部落到 S2 一条链上** ⇒ ★**S2 一次都不许失** ★ |
| ★**代价 2（文档）** ★ | ★**`SW/EVT_TEMPLATE.md:503` + `SW/S2_BOARD_TEST_CHECKLIST.md:393` + `SW/FLASH_AND_VERSION.md:44/336` 全部要改成「S3 不可用 ⇒ 直接 S4」★★ (★与路线 ① 的代价 3 重叠 ⇒ ★**①与③可以在同一次裁决里一起落**★)★ |
| ★**代价 3（与「板只改一次」冲突）** ★ | ★**换 SoM = 板面 BTB 连接器/走线全变** ⇒ ★**板必须重做** ⇒ ★**若现在不定、板做出来再换 = 板改第二次** ⇒ ★**⇒ 路线 ③ 若被采纳，必须【赶在板那一趟之前定】** ★ |
| ★**代价 4（选型）** ★ | ★**要重跑 SoM 选型打分** (`state/_soc_score_15.py` 一类) ⇒ ★**这是本单不做、也不该 SW 侧做的一件** ★ |
| ★**牵连面** ★ | ★**板面**: BTB 连接器 + 全部 SoM 侧走线 + 板层数 + 板框 ★　★**HW 域**: 网表三件 + BOM 全动 ★　★**MECH 域**: 镜脚/镜框结构 + 板框 ★　★**SW 域**: 救砖 4 级表 + 产线流程 ★ |
| ★**要谁拍** ★ | ★**老板级** (换芯片 = 商务/供应链级)★ —— ★**main 转达** ★ |

★**sw-lead 的建议 (★标明: 不代拍★)** ★: ★**建议 = 路线 ① + 路线 ③ 的「口径部分」在同一次裁决里一起落，并同时启动路线 ② 的【前置可行性摸底】(不是落表)** ★（★**① < ② < ③** · 与 ISS-375 §3-2 排序一致，本单独立复算后结论相同★）。★**必须赶在板那一趟之前定死的只有一件事: 「pin1 朝向」(A/B)** —— ★**它不依赖 SoM 侧结论 (纯落点写死)**，★**而它决定 B1-③ 那 5 处机器件读数往哪边写** ⇒ ★**落晚了 = 板做了机器件还得再改 = 违反「板只改一次」** ★。★**不代拍声明**: ★**本单不代 main / 老板拍上述任何一条** ★

### ★B1-⑦ SoC / SoM 两侧 JTAG 自查证 (★零外发 · 全靠本机盘上官方文件实读★) ★

★**两条 grep (闸自己会跑，输出见 B6)★**:

```
grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv ; echo "rc=$?"      → 4 行 (B11/U33/U33/V32) · rc=0
grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv ; echo "rc=$?"             → 0 · rc=1 (grep 的「无匹配」退出码，不是错误)
```

★**逐行实读结论**: ★
- ★**`HW/RK3572_PIN_TABLE/rk3572_pins.csv` (表头 `ball,gpio,func,name` · 由官方 PDF 解析而来) 里 JTAG 命中 = 4 行** ★ (行号 **125 / 126 / 167 / 168**)★
- ★**这 4 行的 JTAG mux 名 = `JTAG_TCK_M0` / `JTAG_TMS_M0` / `JTAG_TCK_M1` / `JTAG_TMS_M1`** ★
- ★**⇒ SoC 侧官方引脚复用表里【只有 TCK 和 TMS】，没有 `JTAG_TDI*` / `JTAG_TDO*` 任何一个 mux 名** ★
- ★**`grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv` = `0`** ⇒ ★**SoM 模块逐针表 (399 数据行) 里 JTAG 命中 = 0 ⇒ 模块侧没有 JTAG 引出** ★

★**本单新增的官网级事实 (★任务书里没有 · 本单自己实读出来 · 比 ISS-375 更进一步★)★**:

★**`HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` (官方 PDF 的文本层 · 2921 行 · PDF md5 `c0e3763036e2f6a3e8a2f68f2254851d`) 里 JTAG 命中 = 5 处**: ★

| 文本层行号 | 原文（逐字） | 读出来的意思 | 证据等级 |
|---|---|---|---|
| ★**L247** ★ | `    JTAG interface for debug` (在 §1.2.3 System Component 的 `BUS RISCV MCU` 特性块里) ★ | ★**官方明写：RK3572 芯片【有 JTAG 调试接口】** ★ | ★**[官网]** ★ |
| L1197 | `CAN0_RX_M0/JTAG_TCK_M0/SPI0_CSN1_M1/UART5_RTSN_M2/SAI3_LRCK_M1/DSM_AU` | `GPIO2_A2` 的 mux 里含 `JTAG_TCK_M0` | [官网] |
| L1202 | `CAN0_TX_M0/JTAG_TMS_M0/UART5_CTSN_M2/SAI3_SDI_M1/DSM_AUD_RN_M0/SDMMC` | `GPIO2_A3` 的 mux 里含 `JTAG_TMS_M0` | [官网] |
| L1308 | `JTAG_TCK_M1/UART0_TX_M0/GPIO0_D4_u` | `GPIO0_D4` 的 mux 里含 `JTAG_TCK_M1` | [官网] |
| L1310 | `JTAG_TMS_M1/UART0_RX_M0/GPIO0_D5_u` | `GPIO0_D5` 的 mux 里含 `JTAG_TMS_M1` | [官网] |

★**并且**: ★**`grep -cE 'JTAG_TDI|JTAG_TDO'` 在这份 2921 行官方文本层上 = `0`** ★ ⇒ ★**整份官方 datasheet 里，`JTAG_TDI` / `JTAG_TDO` 这两个信号名一次都没出现** ★

| | ★**ISS-375（已签收，本单不改）** ★ | ★**ISS-378（本单）** ★ |
|---|---|---|
| 芯片内部有没有 JTAG 功能 | ★**`[0数据]`** —— 原文：「芯片内部是否具备 JTAG 功能，本单未取得证据，不作断言」 ★ | ★**`[官网]`** —— ★**官方 datasheet L247 明写「JTAG interface for debug」⇒ 芯片【有】JTAG 调试接口** ★（★是推进，不是翻案：ISS-375 当时只查了脚表，脚表覆盖的是模块引出的脚，够不到芯片特性块★）★ |
| `JTAG_TDI` / `JTAG_TDO` 的球位 | ★**`[0数据]`** ★ | ★**`[0数据]`（不变）** —— ★**官方引脚复用表只有 TCK/TMS ⇒ TDI/TDO 的球位在这份官方文档里查不到** ★ |
| SoM 侧有没有 JTAG 引出 | ★**`[实测]` 无** ★ | ★**`[实测]` 无** (★与 ISS-375 一致★)★ |
| ★**可下的结论句（受控表述）** ★ | —— | ★**「RK3572 芯片官方声明有 JTAG 调试接口 ([官网])，但官方引脚复用表只暴露 TCK / TMS 两个 mux 名；TDI / TDO 的球位在官方文档中无记载 ([0数据])；FET3572-C 这版 SoM 的 399 行逐针表里 JTAG 命中 = 0 ([实测]) ⇒ 板级 JTAG 四线在 SoM 侧不落地 ⇒ JTAG 救砖链 (S3) 在这版 SoM 上不存在。」** ★ |

★**其它必须实读的官方/本机素材 (★逐条读过了才写★)★**:

| 素材 | 实读到的关键内容 | 用在哪 | 证据等级 |
|---|---|---|---|
| ★**`HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行** ★ | ★**`JTAG_TCK` / `JTAG_TDI` / `JTAG_TDO` / `JTAG_TMS` 四行，原话逐字 = 「逐针表里没有同名/后缀相同的信号 ⇒ 要么是 RK3572 内部命名不同，要么该信号在 FET3576-C 上不存在 (⇒ 需换引脚或换板)」** ★ | ★**B1-⑤ C-1 / B1-⑥ 路线② 的依据 (★本单把它当【二选一措辞】读，不替它选边★)★** | [实测] |
| ★**`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md`** ★ | ★**官方事实卡 §1 封装 = FCCSP550L / 14.3 × 15.5 mm / 550 球；★§「本项目 demo 主板用的是 SoM 模组 (FET3572-C) 的 BTB (0.4 mm pitch)，不是裸 SoC 的 FCCSP ⇒ 那条 pitch 约束不适用于当前布线板」** ★ | ★**B1-⑦ 的背景 (芯片 vs 模组两级分清)★** | [官网] |
| ★**`HW/rk3572_official_facts_check.py`** ★ | ★**本单实跑 ⇒ rc=0 · 文本层断言 22/22 全中 · PDF md5 `c0e3763036e2f6a3e8a2f68f2254851d` · 文本层 2921 行** (日志 `logs/iss378_official_facts_check.log`) ★ | ★**B1-⑦ 官方事实的可复核入口** ★ | [实测] |
| ★**`HW/check_s8_target_list.py:22-24,53-63`** ★ | ★**`REQUIRED_SINGLE` = 8 条单端脚，含 `JTAG_TDI`；`EXPECT_REQUIRED = 23`；★**它只判「分级 + 本板有没有铜」** ★ | ★**B1-⑤ C-2** ★ | [实测] |
| ★**`HW/netlist_v1.csv:388/390/392/394`** ★ | ★**四条 `JTAG_*_SOC` 的 SoM 侧端点逐条 = `SoC_NC`** ★ | ★**B1-③ + B1-④ + B1-⑤ C-1** ★ | [实测] |
| ★**`HW/netlist_v1_pins.csv:202-205,275-276`** ★ | ★**`J_DEBUG.pin1=JTAG_TCK` / `pin2=TMS` / `pin3=TDI` / `pin4=TDO`；`J_UART.pin1=UART_TX` / `pin2=UART_RX`** ★ | ★**B1-① A 层 + B1-② 依据②** ★ | [实测] |

★**查不到的部分 (`[0数据]` + 降级方案 · 必填项)★**:

| 缺口 | 等级 | ★**降级方案（不许留成外部待回复形态）** ★ |
|---|---|---|
| ★**`JTAG_TDI` / `JTAG_TDO` 在 RK3572 上的球位** ★ | ★**`[0数据]`** ★ (官方 datasheet 2921 行文本层 0 命中) ★ | ★**降级 = 按「SoM 不引出 JTAG」设计**：JTAG 四线在板上保留 `J_DEBUG` 位 (不装贴片，手工可焊)，板侧不承诺 JTAG 链可用 ⇒ 救砖按 S1→S2→S4 三级设计；★**若将来拿到官方 TDI/TDO 球位，那是【新增能力】不是【救现有设计】** ★ |
| ★**原厂是否提供 JTAG 调试器 + 转接板** ★ | ★**`[0数据]`** ★ | ★**降级 = 不依赖**：既然 S3 不存在，产线与返修流程按「S2 必须实测走通 + S4 返厂」设计 (`SW/FLASH_AND_VERSION.md` §4.4 已有该骨架)；★**零外发** ★ |
| ★**`J_UART` 的 X 向开口窗口** ★ | ★**`[0数据]`** ★ (MECH 侧未定义，见 ISS-375 注 2) ★ | ★**降级 = 本页不给 `J_UART` 间隙结论** ★；★**只给针序契约** ★ |
| ★**芯片内部 TDI/TDO 功能是否存在** ★ | ★**`[0数据]`** ★ (官方只暴露 TCK/TMS；芯片特性块只说「有 JTAG interface」没说信号集合) ★ | ★**降级 = 不作断言** ★；★**只写「SoM 侧不落地」** ★ (★这是 ISS-375 §2-4 已定的表述边界，本单沿用★) ★ |

---

## B2 验收标准自评

| 验收标准 (任务书 §二/§三/§四) | 自评 | 依据 |
|---|---|---|
| ① 逐网影响面 (覆盖 JTAG 四线 + 四条 `*_SOC` + UART 两线 + BOOT_N + KEY 四条 + RESET 两条 + USB 两条 = **19 行**) | ✅ 通过 | 清单页 `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` §1-1 (闸 **W0** 机器核对 19 行与网表/脚表实读一致 · **W1** 三分类非空) |
| ② 「变化性质」只允许 `无` / `仅物理针序` / `需改代码` 三档 + 「若需改」只写文件+行号+函数名 | ✅ 通过 | 闸 **W1** (三分类齐全且非空) + **W2** (6 条「需改代码」行的 文件/行号/函数名 **全部核实存在**) |
| ③ 三条救砖链 + 「最坏只剩哪条链」结论句 | ✅ 通过 | 闸 **W3** (三条链 + 最坏结论句齐全 · 最坏只剩 USB) |
| ④ `JTAG_TDI` 口径冲突的三条路线 (①改口径 / ②改网表 / ③换 SoM) + 各自代价 | ✅ 通过 | 闸 **W4** (三条路线齐全且各有代价) |
| ⑤ SoC / SoM 两侧 JTAG 自查证 | ✅ 通过 | 闸 **W5** (SoC 实测 4 行 JTAG · TCK/TMS 有 / TDI/TDO 无 + SoM 实测 0 命中 + 网表四条 SoC_NC ⇒ 结论一致) |
| ⑥ 证据分级五级白名单 + 零挂起措辞 + `[0数据]` 处都有降级方案 | ✅ 通过 | 闸 **W6** (五级白名单 + 零挂起措辞 + [0数据] 处都有降级方案) |
| ⑦ 零写板 / 零落表 (板指纹三项 + 网表/脚表/BOM 三件 md5 与基线一致) | ✅ 通过 | 闸 **W7** (板 md5/mtime/size 三项 + 三件 md5 全部与基线一致) |
| ⑧ 零挂链 (`state/gate_check.py` 里 `check_debug_header_fw_impact` 命中 0) | ✅ 通过 | 闸 **W8** (命中 0) |
| ⑨ 新闸 `--selftest` ≥8 条反向用例，每条自证「红的是目标那一条，其余仍绿」 | ✅ 通过 | **14 条反向用例，14/14 PASS，末行 `ALL TESTS PASS`** (REV1~REV13 + REV0 对照组) |
| ⑩ 交卷页 B1~B6 六段齐全 + 六个 `##` 标题含 gate_check 关键词 | ✅ 通过 | 本页 (见 B6) · `state/gate_check.py` Q1 计分 |
| ⑪ 边界: 零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 不代拍 / 不自签台账 / 只写自己分片 | ✅ 通过 | B5-④ 边界自证表 + B6 命令 |
| ⑫ 交卷前必跑 4 条命令 + 板 md5 核对 | ✅ 通过 | ★**原样输出贴在 B6** ★ |
| ⚠️ 本趟性质 | ⚠️ **cont1 收尾** | ★**主产物 (清单页 + 新闸 + 3 份闸日志) 已在盘且已被 main 独立复跑验证 ⇒ 本趟只补交卷页与分片 (详见 B5-①)** ★ |

---

## B3 证据分级

| 结论 | 等级 | 依据 / 复跑 |
|---|---|---|
| `J_DEBUG.pin1=JTAG_TCK` / `pin2=TMS` / `pin3=TDI` / `pin4=TDO`；`J_UART.pin1=UART_TX` / `pin2=UART_RX` (逻辑映射逐字不变) | [实测] | `HW/netlist_v1_pins.csv:202-205,275-276` · 闸 W0 |
| JTAG 四线 + UART 两线在 `SW/**` **代码文件**里命中 0 行 (固件零引用) | [实测] | `grep -rnw JTAG_TCK SW --include='*.py' --include='*.sh' --include='*.json'` 等 · 闸 W0 |
| `stty` / `> /dev/tty` / `write..tty` 在 SW 代码文件命中 0 行 ⇒ SW 侧从不往板里写串口 | [实测] | `grep -rn "stty\|> /dev/tty\|write.*tty" SW` |
| 四条 `JTAG_*_SOC` 的 SoM 侧端点全部 = `SoC_NC` | [实测] | `HW/netlist_v1.csv:388/390/392/394` · 闸 W5 |
| SoM 逐针表 399 数据行里 `JTAG` 命中 = 0 ⇒ SoM 侧无 JTAG 引出 | [实测] | `grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv` → `0` (rc=1) · 闸 W5 |
| SoC 官方引脚复用表里 JTAG 命中 = 4 行，mux 名只有 `JTAG_TCK_M0/M1` + `JTAG_TMS_M0/M1` | [实测] | `grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv` → 4 行 (125/126/167/168) · 闸 W5 |
| 官方 datasheet 文本层 L247 = `JTAG interface for debug` ⇒ 芯片【有】JTAG 调试接口 | [官网] | `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` L247 · PDF md5 `c0e3763036e2f6a3e8a2f68f2254851d` |
| 官方事实闸 22/22 断言全中 (PDF md5 / 文本层行号 / 渲染图尺寸) | [实测] | `python3 HW/rk3572_official_facts_check.py` rc=0 · 日志 `logs/iss378_official_facts_check.log` |
| `JTAG_TDI` / `JTAG_TDO` 的球位 | [0数据] | 官方 datasheet 2921 行文本层 `grep -cE 'JTAG_TDI\|JTAG_TDO'` = **0** ⇒ 降级方案写在 B1-⑦「查不到的部分」 |
| `J_UART` 的 X 向开口窗口 | [0数据] | MECH 侧未定义 (ISS-375 注 2) ⇒ 本页不给间隙结论，只给针序契约 |
| 芯片内部 TDI/TDO 功能是否存在 | [0数据] | 官方只暴露 TCK/TMS；特性块只说「有 JTAG interface」没说信号集合 ⇒ **不作断言** |
| 原厂是否提供 JTAG 调试器 + 转接板 | [0数据] | 降级 = 不依赖，按「S2 必须实测走通 + S4 返厂」设计 |
| 受控结论 = 「SoM 侧未落地 / 板级 JTAG 链不落地」，**不是**「信号不存在」 | [推算] | 由上面三条实读推出；表述边界沿用 ISS-375 §2-4；闸 W5 机器抓「结论与实测不一致」 |
| 换 land 的影响 = A 层不变 / B 层变 ⇒ 固件本体 0 行要改 | [推算] | 逻辑映射逐字不变 (A 层) + 物理针序随 land 变 (B 层) ⇒ 固件引用的是逻辑层 |
| 「最坏只剩 USB(S2) 一条链」 | [推算] | S3 不存在 (SoM 侧不落地) + UART 非救砖级 ⇒ 唯一救砖链是 USB |
| 三条路的代价排序 ① < ② < ③ | [推算] | ① 板那一趟零额外动作；② 需前置方案 + 落表窗口；③ 板面全变 + 老板级 |
| 建议路线 ① + ③ 的口径部分 + ② 的前置摸底 | [推算] | ★**建议，不是裁决；不代拍** ★ |
| 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 三项未动 | [实测] | `md5sum` + `stat -c '%y %s'` · 闸 W7 + B6 |
| 网表三件 md5 未动 (`6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8`) | [实测] | 闸 W7 + B6 |
| `pin1 朝向` 选 A 还是 B / `JTAG_TDI` 口径终裁 / 是否换 SoM | [0数据] | ★**不代拍** ⇒ 走 B5 待裁 ★ |

---

## B4 接口取值声明

★**同时登记进 `state/fragments/sw.yaml` 的 `interface_claims` (key 唯一·★本单新增 8 条★)★**

| key | value (短规范值) | 说明 |
|---|---|---|
| `iss378_fw_body_lines_to_change` | `0` | ★**固件本体要改的行数 = 0** (JTAG 四线 + UART 两线在 SW 代码文件里 0 行引用; 逻辑映射逐字不变) ⇒ **[实测]** |
| `iss378_netname_to_pad_mapping_impact` | `none` | ★**A 层「网名 → pad 号」映射换 land 后不变** (`J_DEBUG.pin1=JTAG_TCK` / `J_UART.pin1=UART_TX` 两个候选都保持) ⇒ **[实测]** |
| `iss378_physical_pin_order_layer_impact` | `rot90=same-order; rot270=reversed` | ★**B 层「物理针序」随 land 变**: 候选 A (rot90) 与现状同向 ⇒ 线序说明零改动; 候选 B (rot270) 逆排 ⇒ 现有 JTAG 线序描述必须反转 ⇒ **[实测]** |
| `iss378_rescue_chains` | `USB(S2); UART(observation-only); JTAG(S3-absent)` | ★**三条链的救砖级归属** (UART = 日志观测链, 不属救砖级) ⇒ **[实测]** |
| `iss378_worst_case_rescue_chain` | `USB` | ★**最坏只剩 USB (S2) 一条链**; 若 S2 也不可用 ⇒ 一条链都不剩 ⇒ S4 返厂 ⇒ **[推算]** |
| `iss378_jtag_tdi_soc_side_endpoint` | `SoC_NC` | ★**`JTAG_TDI_SOC` 的 SoM 侧端点 = `SoC_NC`** (ISS-344 判「必需 · 板侧不许标 NC」与网表直接对撞的落点) ⇒ **[实测]** |
| `iss378_som_jtag_exposure` | `none` | ★**SoM 侧无 JTAG 引出**: FET3572-C 逐针表 399 数据行 `JTAG` 命中 = 0 ⇒ S3 救砖链在这版 SoM 上不存在 ⇒ **[实测]** |
| `iss378_soc_jtag_mux_names` | `JTAG_TCK_M0;JTAG_TMS_M0;JTAG_TCK_M1;JTAG_TMS_M1` | ★**SoC 侧官方引脚复用表只暴露 TCK/TMS 四个 mux 名**; 官方 datasheet L247 另明写「JTAG interface for debug」⇒ 芯片【有】JTAG 接口 ([官网]); TDI/TDO 全文档 0 命中 ([0数据]) ★ |

★**★本单不代拍的三条 (★只登记代价, 不写进 interface_claims 当裁决★): `pin1 朝向 A/B` · `JTAG_TDI` 口径走 ①/②/③ 哪条 · `是否换 SoM` ⇒ ★**全部归 main / 老板裁 (见 B5)** ★**

---

## B5 未决项与卡点

### ★B5-① ★**本趟性质 (必读)★**: 上一趟 cont1 被 16 分钟墙掐死 ⇒ 本趟只补交卷页与分片 ★

> ★**「上一趟 cont1 被 16 分钟墙掐死 (★主产物已在盘★) ⇒ 本趟只补交卷页与分片」** ★
>
> ★**上一趟 (2026-11-24 派) 的子会话被运行时墙掐死** —— 与 ISS-375 cont1 同款症状 (status=timeout / abortedLastRun=true ⇒ 非外部 abort · 非上下文溢出)。
> ★**但两件重产物都已经在盘，且已被 main 独立验过**:
> ① `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (55,076 B @11-24 02:45) ⇒ **本趟一个字未改**;
> ② `SW/tools/check_debug_header_fw_impact.py` (37,515 B @11-24 02:45) ⇒ ★**main 已独立复跑: 裸跑 rc=0 (W0~W8 全绿 · 含 W7 板三项指纹 + W8 零挂链) + `--selftest` rc=0 (14/14 反向用例全过 · 末行 ALL TESTS PASS) ⇒ 这道闸是好的，本趟没碰它** ★;
> ③ `logs/iss378/` 3 份闸日志 + `logs/iss378_official_facts_check.log` ⇒ ★**直接引用，未重跑扫描** ★。
>
> ⇒ ★**本趟只做两件: ① 新建本交卷页 (B1~B6) ② 用 `state/frag_write.py` 登记分片 `state/fragments/sw.yaml`** ★
> ⇒ ★**本趟没做: 重跑扫描 / 重建清单页 / 重建闸 / 改既有闸 / 改既有页面正文 / 写板 / 落表 / 挂链 / 外发 / 签台账** ★

### ★B5-② 要 main 裁的第一件事: `J_DEBUG` / `J_UART` 的 pin1 朝向选 A 还是 B ★
- **要谁回答**: ★**main 一句话即可** ★
- **要回答什么**: `J_DEBUG`/`J_UART` 的落点写死值取 **候选 A (rot90 · ISS-375 建议)** 还是 **候选 B (rot270)**? ★**ISS-375 §1-5 已备好两套写死值**: A: `J_DEBUG`→`(141.0450, 56.6000)`/90°/顺排 · `J_UART`→`(18.2550, 68.6000)`/90°/顺排；B: `J_DEBUG`→`(144.8550, 56.6000)`/270°/逆排 · `J_UART`→`(19.5250, 68.6000)`/270°/逆排 ★
- **sw-lead 的建议 (不代拍)**: ★**候选 A (rot90)** ★ —— 保持现状顺排 (TCK 仍在 X 最小端) ⇒ 换 land 后线序不变 ⇒ 只多一个 pin1 方形标记
- **为什么现在就要答**: ★**纯落点写死，不依赖 SoM 侧结论** ★；★**落晚了 = 板做了机器件还得再改 = 板改两次** ★（B1-② 依据③）

### ★B5-③ 要 main 裁的第二件事: ISS-344 对 `JTAG_TDI` 的「必需」分级怎么改口径 ★
- **要谁回答**: ★**main 裁** ★
- **要回答什么**: 走 B1-⑥ 的哪条 (或组合)? ★**① 改口径** (把 `JTAG_TDI` 从「必需」降级 / 标成板侧 NC · 板那一趟零额外动作 · 代价 = 与 ISS-344 终裁正面冲突 + 6 处 `ISS344-CORR` 块连带改 + 4 处救砖硬规则失去执行对象) ★**② 改网表** (把 `JTAG_*_SOC` 的 SoM 侧从 `SoC_NC` 改到真 SoM 引脚 · ★**当前走不通**: 399 行脚表 `JTAG` 命中 0 ⇒ 须先出「SoM 侧 JTAG 怎么引出」的独立前置方案; 且落表窗口必须早于或并入板那一趟) ★**③ 换 SoM** (放弃 S3 软救砖只留 S4 返厂 · 板面全变 ⇒ 板必须重做 ⇒ 必须赶在板那一趟之前定 · **老板级**) ★
- **若走 ②, 还须回答**: ★**是否启动「SoM 侧 JTAG 引出方案」的前置工作；若是，归 hw-lead 出方案、main 决定是否落表** ★
- **sw-lead 的建议 (不代拍)**: ★**① + ③ 的「口径部分」同一次裁决里一起落 + 同时启动 ② 的前置可行性摸底 (零落表、零采购、零外发)** ★

### ★B5-④ 要 main / 老板回答的其余各条 (逐条「要谁回答什么」·★只登记, 不代拍★)★

| # | 未决项 | ★**要谁回答什么** ★ | 为什么现在就要答 |
|---|---|---|---|
| ★**U-3** ★ | 路线 ① 若被采纳：`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的订正块由谁落、什么时候落 | ★**main** —— ★**本单已把冲突与代价写在 B1-⑤/B1-⑥，但该页正文一个字都不许由 sw-lead 改** ★ | ★**订正不落 = 口径页与实测事实长期对撞，下游每次读都踩** ★ |
| ★**U-4** ★ | 若走路线 ①/③：`SW/FLASH_AND_VERSION.md:44`/`:336`、`SW/EVT_TEMPLATE.md:503`、`SW/S2_BOARD_TEST_CHECKLIST.md:393` 这 4 处硬规则改成什么 | ★**main 派单给 sw-lead 执行** (★**属 SW 域，本单可做但要等裁决**★) ★ | ★**S3 没有执行对象 ⇒ 「S2 连续失败 2 次 → 必须升级 S3」这条硬规则现在指向一个不存在的东西** ★ |
| ★**U-5** ★ | `HW/check_s8_target_list.py` 的 `REQUIRED_SINGLE` / `EXPECT_REQUIRED` 要不要跟着改 | ★**hw-lead** (★**该文件属 hw-lead 地界，本单只读，零写入**★) ★ | ★**它是 ISS-344 分级在机器侧的投影；口径改了它不改 = 机器闸与口径页分叉** ★ |
| ★**U-6** ★ | 路线 ③ (换 SoM) 是否走 | ★**老板级** (★main 转达★) ★ | ★**它决定板那一趟开不开工** (换了 SoM = 板面全变) ★ |
| ★**U-7** ★ | 新闸 `SW/tools/check_debug_header_fw_impact.py` 挂不挂进 `state/gate_check.py` | ★**main** —— ★**本单零挂链** (`grep -c check_debug_header_fw_impact state/gate_check.py` = **0**) ★ | ★**挂不挂归 main；先例 = ISS-309/312/315/318 都是 SW 侧出结论、main 挂** ★ |
| ★**U-8** ★ | ISS-344 口径页那句「SW 侧 31 次 JTAG 全是 TCK/TMS/M0/M1 ⇒ 无一命中 TDI」已被 ISS-375 的闸自身冲掉 (现在 `JTAG_TDI` 在 `SW/**` 命中 52 行，其中代码 3 行) —— 要不要一并订正 | ★**main** (★同 U-3，同一块订正块★) ★ | ★**这句话现在会被下游当「SW 侧没有 TDI」引用 ⇒ 误读风险** ★ |

### ★B5-⑤ 边界自证 (逐条) ★

| 边界 | 自证 |
|---|---|
| 零写板 | 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ 三项逐字未动 (闸 W7 + B6 命令) |
| 零落表 | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` **只读**，三件 md5 未动 (闸 W7 + B6) |
| 零改既有闸 | 那 3 道 SW 闸 + `check_demo_panel_spec` / `timing_check` / `check_shutdown_semantics` / `check_pcb_nets` / `gate_check` / `merge` / `frag_write` / `check_sch_erc` / `check_sch_pinfull` **一字未改** ★**本趟只新建交卷页 + 写自己分片** ★ |
| 零改既有页面正文 | `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (55,076 B) / `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (ISS-375 已签收) / `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` / `SW/SW_MD5_BASELINE_LEDGER.md` 那 13 处 (R6/R7 判决源) **全部一字未动** ⇒ 冲突只登记在本页 B1-⑤/B1-⑥ |
| 零挂链 | `grep -c check_debug_header_fw_impact state/gate_check.py` = **0** (闸 W8 + B6) |
| 只写自己分片 | 只走 `python3 state/frag_write.py --agent sw-lead` 写 `state/fragments/sw.yaml` (★**没有用 `open(p,"w")`** ★); ★**写前 md5 `639a7610a08e895a52122b1db2f33054` → 写后 md5 `21892e983ba60404b1033a248e82fc86`** ★; ★**写前写后逐 key 核过: 旧 key 丢失 = 0** ★ (artifacts 278→281 · interface_claims 325→333 · needs_from 82→84 · answers 71 / blockers 15 / open_questions 5 / risks 2 均不变) ★; ★**写前 md5 复测两次一致 ⇒ 期间无人改过本分片 ⇒ 不触发「已停止」分支** ★ |
| 零外发 | 未发任何邮件 / 询价 / 问询 / 采购 ⇒ §B1-⑦ 的全部事实来自本机盘上官方文件实读 |
| 不代拍 | B5-② / B5-③ / B5-④ 全部标「归 main / 老板裁」; ★**本单只给事实与代价** ★ |
| 不自签台账 | `state/issue_log.yaml` **一字未动** ⇒ 由 main 签收 |
| 未重跑扫描 | ★**本趟未重跑任何扫描** (清单页 §4 的两条 grep 与官方事实闸的读数直接引用 `logs/iss378/` + `logs/iss378_official_facts_check.log`); ★**交卷前只必跑了那 4 条命令** ★ |

### ★B5-⑥ 落盘清单 ★

| 路径 | 动作 | 备注 |
|---|---|---|
| `HANDOFF/2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md` | ★**新建** (本文件) ★ | B1~B6 六段 · 六个 `##` 标题含 gate_check 关键词 |
| `state/fragments/sw.yaml` | ★**登记** (只走 `frag_write.py`) ★ | 3 产出物 + 8 条 `interface_claims` (`iss378_*`) + 2 条 `needs_from` (`iss378_need_main_*`) · ★**写前 md5 `639a7610a08e895a52122b1db2f33054` → 写后 md5 `21892e983ba60404b1033a248e82fc86`** ★ · ★**旧 key 零丢失** ★ |
| `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` | ★**零改动** ★ | 55,076 B @02:45 · 已在盘 · 被 main 独立验过 |
| `SW/tools/check_debug_header_fw_impact.py` | ★**零改动** ★ | 37,515 B @02:45 · 已在盘 · 被 main 独立复跑过 |
| `logs/iss378/` (3 份) + `logs/iss378_official_facts_check.log` | ★**零改动 (直接引用)** ★ | 闸日志 + 官方事实闸 rc=0 |

---

## B6 自证复现命令

★**★交卷前必跑四条 (★原样输出贴在下面·★rc 必须全 0·★Q1 必须 18/18★)★★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 SW/tools/check_debug_header_fw_impact.py
python3 SW/tools/check_debug_header_fw_impact.py --selftest
python3 state/merge.py          # rc=0
python3 state/gate_check.py      # rc=0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```

★**★以下为本次实跑原样输出 (★`TMPDIR=$PWD/tmp`★ · ★本机 `/tmp` 用户配额已打满 ⇒ 不指会 EDQUOT 假红★)★★**

```text
### CMD1: python3 SW/tools/check_debug_header_fw_impact.py
=== ISS-378 · check_debug_header_fw_impact ===
  ✔ W0 : §1 逐网表 19 行与网表/脚表实读一致
  ✔ W1 : 全部 19 行的变化性质都在三分类里且非空
  ✔ W2 : 6 条「需改代码」行的 文件/行号/函数名 全部核实存在
  ✔ W3 : §2 三条链 + 最坏结论句齐全 (最坏只剩 USB)
  ✔ W4 : §3 三条路线 (①改口径/②改网表/③换 SoM) 齐全且各有代价
  ✔ W5 : SoC 实测 4 行 JTAG (TCK/TMS 有 · TDI/TDO 无) + SoM 实测 0 命中 + 网表四条 SoC_NC ⇒ 结论一致
  ✔ W6 : 证据等级五级白名单 + 零挂起措辞 + [0数据] 处都有降级方案
  ✔ W7 : 板 md5/mtime/size 三项 + 网表/脚表/BOM 三件 md5 全部与基线一致
  ✔ W8 : state/gate_check.py 里 check_debug_header_fw_impact 命中 0 ⇒ 零挂链
--- 9/9 绿 ---
rc=0
```

```text
### CMD2: python3 SW/tools/check_debug_header_fw_impact.py --selftest
=== ISS-378 · check_debug_header_fw_impact --selftest ===
  ✔ REV1_route3_deleted                    目标判据 W4 独红 · 其余全绿
  ✔ REV2_som_conclusion_flipped            目标判据 W5 独红 · 其余全绿
  ✔ REV3_change_file_not_exist             目标判据 W2 独红 · 其余全绿
  ✔ REV4_net_row_deleted                   目标判据 W0 独红 · 其余全绿
  ✔ REV5_nature_blank                      目标判据 W1 独红 · 其余全绿
  ✔ REV6_uart_chain_dropped                目标判据 W3 独红 · 其余全绿
  ✔ REV7_worst_case_sentence_dropped       目标判据 W3 独红 · 其余全绿
  ✔ REV8_bad_evidence_tag                  目标判据 W6 独红 · 其余全绿
  ✔ REV9_hanging_wording                   目标判据 W6 独红 · 其余全绿
  ✔ REV10_board_baseline_faked             目标判据 W7 独红 · 其余全绿
  ✔ REV11_gate_hooked                      目标判据 W8 独红 · 其余全绿
  ✔ REV12_netlist_soc_endpoint_broken      目标判据 W5 独红 · 其余全绿
  ✔ REV13_net_name_not_in_netlist          目标判据 W0 独红 · 其余全绿
  ✔ REV0_control                           对照组全绿 (证明不是把灯调没了)
SELFTEST 14/14
ALL TESTS PASS
rc=0
```

```text
### CMD3: python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-24T03:24:39+08:00)
   产出 810 | 阻塞 43 (高危 33) | 未闭合需求 334 | 冲突 0 | 健康度 red
rc=0
```

```text
### CMD4: python3 state/gate_check.py
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1135 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    444 条
   sw-lead    333 条
   mech-lead  358 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 118/503  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 236 条, 其中 58 条真对上了别人的需求 key
   hw-lead    被答 43/268 | 我答 81 条(有效 31) | 产出 314 | 阻塞 7
   sw-lead    被答 29/84 | 我答 71 条(有效 6) | 产出 281 | 阻塞 15
   mech-lead  被答 46/151 | 我答 84 条(有效 21) | 产出 200 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 51 条 | **全局 46 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 334 条**
   ✅ 与 merge.py 自对账一致 (等外部 46 / 等总工 334)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 10 个
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']
      iss105_jchg_rfq_release: 发起方 ['main', 'hw-lead']
      iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice: 发起方 ['main', 'mech-lead']
      iss236_boss_v_decision: 发起方 ['main', 'hw-lead']

【Q5 硬指标覆盖】 2/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    4/5 类: ['功耗(W)', '镜腿/镜脚厚度(mm)', '端到端延迟(ms)', 'FCCSP 球间距(pitch)']
   sw-lead    3/5 类: ['镜腿/镜脚厚度(mm)', '端到端延迟(ms)', 'FCCSP 球间距(pitch)']
   mech-lead  2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 10/10 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ✅ 钉板闸⑩ 板侧项全集重跑幂等闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 205 条需求确实还没人答 (等另一个总工)
   · sw-lead: 41 条需求确实还没人答 (等另一个总工)
   · mech-lead: 88 条需求确实还没人答 (等另一个总工)

==========================================================================
rc=0
```

```text
### MD5: md5sum HW/PCB/demo_mainboard.kicad_pcb
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
### STAT
2026-11-06 07:07:17.362193413 +0800 4940213
### 零落表三件
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
### 零挂链
0
```

★**★读数摘要 (★供 main 一眼核对★)★★**

| 项 | 实跑读数 | 期望 | 判定 |
|---|---|---|---|
| `python3 SW/tools/check_debug_header_fw_impact.py` | **rc=0** · W0~W8 **9/9 绿** | rc=0 | ✅ |
| `python3 SW/tools/check_debug_header_fw_impact.py --selftest` | **rc=0** · **SELFTEST 14/14** · 末行 `ALL TESTS PASS` | rc=0 | ✅ |
| `python3 state/merge.py` | **rc=0** · STATE.yaml 已刷新 (2026-11-24T03:24:39+08:00) | rc=0 | ✅ |
| `python3 state/gate_check.py` | **rc=0** · ★**Q1 = 18/18** ★ · Q2 3/3 · Q3 sw-lead 333 条 · Q6 硬件真源闸 rc=0 · Q7 钉板 md5 闸 10/10 绿 | rc=0 · Q1 18/18 | ✅ |
| ★**sw-lead 交卷页计分** ★ | ★**6/6 · 缺: 无** ★ · 计分页 = ★`2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md` ★ | 6/6 | ✅ |
| `md5sum HW/PCB/demo_mainboard.kicad_pcb` | ★**`611b869e13518c3c023fb178f91a0075`** ★ | 同值 | ✅ 零写板 |
| `stat -c '%y %s'` (板) | ★**`2026-11-06 07:07:17.362193413` / `4940213`** ★ | 同值 | ✅ 零写板 |
| 网表/脚表/BOM 三件 md5 | ★**`6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8`** ★ | 同值 | ✅ 零落表 |
| `grep -c check_debug_header_fw_impact state/gate_check.py` | ★**0** ★ | 0 | ✅ 零挂链 |
| ★**分片写前 / 写后 md5** ★ | ★**写前 `639a7610a08e895a52122b1db2f33054` → 写后 `21892e983ba60404b1033a248e82fc86`** ★ | 只走 `frag_write.py` | ✅ |
| ★**分片增量核对 (零丢失)** ★ | ★**artifacts 278→281 (+3) · interface_claims 325→333 (+8) · needs_from 82→84 (+2) · answers/blockers/open_questions/risks 不变 · 旧 key 丢失 = 0** ★ | 不丢旧数据 | ✅ |


★**★边界自证命令 (★可复跑·★用于核对「零写板 / 零落表 / 零挂链」★)★★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ── 零写板 (三项) ──
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ── 零落表 (三件 md5) ──
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv

# ── 零挂链 (必须 0) ──
grep -c check_debug_header_fw_impact state/gate_check.py

# ── 只写自己分片: 写前 / 写后 md5 ──
md5sum state/fragments/sw.yaml

# ── 状态机 ──
python3 state/merge.py
python3 state/gate_check.py
```

★**★板面基线常量 (★闸 W7 读的就是这组·★交卷后仍须逐字一致★)★★**

| 项 | 基线值 |
|---|---|
| 板 md5 | `611b869e13518c3c023fb178f91a0075` |
| 板 mtime | `2026-11-06 07:07:17.362193413` |
| 板 size | `4940213` |
| 网表 md5 | `6aee500e60ba0732f83a9cf557ba90ab` |
| 脚表 md5 | `9174309df1ec9411ac8e8d9e80ee386a` |
| BOM md5 | `5b9993992405904a60ac96a020b375d8` |

★**★「本趟零改动」逐件 md5 核对 (★交卷后实测 · ★与既有基线逐字一致★)★★**

| 文件 | md5 (交卷后实测) | 本趟是否动过 |
|---|---|---|
| `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (清单页 · 55,076 B) | `c7bbe75c35f8fa6194f74330b32c52ad` | ★**未动** ★ |
| `SW/tools/check_debug_header_fw_impact.py` (新闸 · 37,515 B) | `d78c2446913d5cd3742235d9fd9fef15` | ★**未动** ★ |
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | ★**未动** ★ |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | ★**未动** ★ |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | ★**未动** ★ |
| `state/gate_check.py` | `5f370bb8cf828473e70ccc5d6412da98` | ★**未动** ★ (零挂链 ⇒ 命中 0) |
| `state/merge.py` | `c9191025020fefd9b475e2573a335815` | ★**未动** ★ |
| `state/frag_write.py` | `3b383a52b4fa540f1d16a2c6f3811de8` | ★**未动** ★ |
| `HW/PCB/demo_mainboard.kicad_pcb` (板) | `611b869e13518c3c023fb178f91a0075` | ★**未动** ★ (mtime/size 亦未动) |

★**★本趟唯一动过的两个文件 = 交卷页 (新建) + `state/fragments/sw.yaml` (只走 `frag_write.py`) ★**

★**★本单主产物 (★已在盘·★本趟零改动·★复跑入口在上面)★★**

| 路径 | 大小 / 时间 | 说明 |
|---|---|---|
| `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` | 55,076 B @ 11-24 02:45 | 逐网影响面清单页 (★含机器块 ` ```json iss378_contract ` , 闸 W0~W8 直接读它★) |
| `SW/tools/check_debug_header_fw_impact.py` | 37,515 B @ 11-24 02:45 | 新闸 (裸跑 W0~W8 九条 · `--selftest` 14/14 反向用例) |
| `logs/iss378/01_gate_bare.log` · `02_gate_selftest.log` · `03_iss375_gate.log` | @ 11-24 02:45 | 3 份闸日志 (★直接引用, 本趟未重跑扫描★) |
| `logs/iss378_official_facts_check.log` | 2,900 B @ 11-24 02:40 | 官方事实闸 rc=0 · 22/22 断言全中 |

---

> ★**本单不做的事 (明写，避免下游误读)**: ★**不改板** · ★**不改网表 / 脚表 / BOM** · ★**不改固件本体** · ★**不改已签收件 (ISS-375 的页与闸)** ★ · ★**不改既有口径页正文 (含 `SW/SW_MD5_BASELINE_LEDGER.md` 那 13 处判决源)** ★ · ★**不外发** · ★**不挂链** · ★**不签台账** · ★**不代拍 `JTAG_TDI` 冲突的终裁 / pin1 朝向 / 是否换 SoM** ★
> ★**要 main 回的两件事**: ★**(1) `J_DEBUG` / `J_UART` 的 pin1 朝向选 A 还是 B (B5-②，一句话即可，ISS-375 §1-5 已备好两套写死值)** ★; ★**(2) ISS-344 在「SoM 侧无 JTAG 引出」这个事实下怎么改口径 —— 走 B1-⑥ 的 ①/②/③ 哪条 (或 ①+③ 组合) (B5-③)** ★


---

## B7 续跑留证（★gateway reload 之后 · 2026-11-24 04:18~04:2x · 本页只追加本节·B1~B6 一字未改★）

> ★**为什么有本节**: ★**本单三件交付物已于 2026-11-24 03:26 交卷, main 于 03:4x 独立复核签收 `verified`（★签收闸 `state/_apply_20260724_0345_main_sign_iss377_378.py` · fail-closed · 全绿才签★）★ → ★**本趟 = gateway reload 之后的续跑复现 + 补留证**★ ⇒ ★**① 把任务书「必跑命令」全 11 条在本机原样再跑一遍并贴原样输出; ② 确认签收之后三件交付物与四份真源一字未漂移; ③ 把本趟的分片写入留证补上** ★

### B7-1 必跑命令全表（★任务书 §三 逐条 · 本机实跑 rc 全在下面★）

| # | 命令 | rc | 说明 |
|---|---|---|---|
| 1 | `python3 SW/tools/check_debug_header_fw_impact.py` | **0** | W0~W8 **9/9 绿** |
| 2 | `python3 SW/tools/check_debug_header_fw_impact.py --selftest` | **0** | **SELFTEST 14/14** · 末行 `ALL TESTS PASS` |
| 3 | `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py` | **0** | ISS-375 既有闸 **9/9 PASS**（★只跑不改·证明零漂移★） |
| 4 | `grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv \| head -10` | **0** | ★**4 行命中 · 全是 `JTAG_TCK_M0` / `JTAG_TMS_M0` / `JTAG_TCK_M1` / `JTAG_TMS_M1` ⇒ SoC 侧只有 TCK/TMS, 没有 TDI/TDO 的 mux 名** ★ |
| 5 | `grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv` | **1** | ★**输出 `0`** ★ ⇒ ★**SoM 模块对外脚表 399 数据行里 JTAG 命中 0** ★ ⇒ ★**rc=1 是 grep「无匹配」的标准退出码, 不是错误** ★ |
| 6 | `grep -n "JTAG_TDI_SOC" HW/netlist_v1_pins.csv` | **0** | ★**网表 `JTAG_TDI_SOC` 的 SoM 侧端点 = `SoC_NC`** ★ |
| 7 | `python3 state/merge.py` | **0** | STATE.yaml 已刷新 |
| 8 | `python3 state/gate_check.py` | **0** | ★**Q1 交付齐备率 18/18** ★ |
| 9 | `python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-378_sw_debug_header_fw_impact.md` | **0** | 任务书命令存在性守卫 |
| 10 | `grep -c check_debug_header_fw_impact state/gate_check.py` | **1** | ★**输出 `0`** ★ ⇒ ★**零挂链** ★ ⇒ ★**rc=1 同上 = grep 无匹配退出码** ★ |
| 11 | `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` + `stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb` | **0** | ★**四件 md5 与基线逐字一致 + 板 mtime/size 未动** ★ |

> ★**两个 rc=1 的读数澄清 (★怕下游误判成假红★)**: ★**`grep -c` 在「命中 0 行」时按 POSIX 返回 1** ★ ⇒ ★**第 5 条与第 10 条的 rc=1 是「正是我们要的结果」的退出码, 判据看的是输出值 `0`, 不是 rc** ★

### B7-2 本趟原样输出（★`logs/iss378/20_continuation_rerun.log` 全文 · ★`TMPDIR=$PWD/tmp`·不指 /tmp★）

```text
### CMD: ISS-378 新闸裸跑
$ python3 SW/tools/check_debug_header_fw_impact.py
=== ISS-378 · check_debug_header_fw_impact ===
  ✔ W0 : §1 逐网表 19 行与网表/脚表实读一致
  ✔ W1 : 全部 19 行的变化性质都在三分类里且非空
  ✔ W2 : 6 条「需改代码」行的 文件/行号/函数名 全部核实存在
  ✔ W3 : §2 三条链 + 最坏结论句齐全 (最坏只剩 USB)
  ✔ W4 : §3 三条路线 (①改口径/②改网表/③换 SoM) 齐全且各有代价
  ✔ W5 : SoC 实测 4 行 JTAG (TCK/TMS 有 · TDI/TDO 无) + SoM 实测 0 命中 + 网表四条 SoC_NC ⇒ 结论一致
  ✔ W6 : 证据等级五级白名单 + 零挂起措辞 + [0数据] 处都有降级方案
  ✔ W7 : 板 md5/mtime/size 三项 + 网表/脚表/BOM 三件 md5 全部与基线一致
  ✔ W8 : state/gate_check.py 里 check_debug_header_fw_impact 命中 0 ⇒ 零挂链
--- 9/9 绿 ---
rc=0

### CMD: ISS-378 新闸 selftest
$ python3 SW/tools/check_debug_header_fw_impact.py --selftest
=== ISS-378 · check_debug_header_fw_impact --selftest ===
  ✔ REV1_route3_deleted                    目标判据 W4 独红 · 其余全绿
  ✔ REV2_som_conclusion_flipped            目标判据 W5 独红 · 其余全绿
  ✔ REV3_change_file_not_exist             目标判据 W2 独红 · 其余全绿
  ✔ REV4_net_row_deleted                   目标判据 W0 独红 · 其余全绿
  ✔ REV5_nature_blank                      目标判据 W1 独红 · 其余全绿
  ✔ REV6_uart_chain_dropped                目标判据 W3 独红 · 其余全绿
  ✔ REV7_worst_case_sentence_dropped       目标判据 W3 独红 · 其余全绿
  ✔ REV8_bad_evidence_tag                  目标判据 W6 独红 · 其余全绿
  ✔ REV9_hanging_wording                   目标判据 W6 独红 · 其余全绿
  ✔ REV10_board_baseline_faked             目标判据 W7 独红 · 其余全绿
  ✔ REV11_gate_hooked                      目标判据 W8 独红 · 其余全绿
  ✔ REV12_netlist_soc_endpoint_broken      目标判据 W5 独红 · 其余全绿
  ✔ REV13_net_name_not_in_netlist          目标判据 W0 独红 · 其余全绿
  ✔ REV0_control                           对照组全绿 (证明不是把灯调没了)
SELFTEST 14/14
ALL TESTS PASS
rc=0

### CMD: ISS-375 既有闸 (只跑不改)
$ bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py
=== ISS-375 · check_debug_pin_order_contract ===
  [PASS] D0   官方 land pad1 形状 (盘上实读, 不写死) 1x04: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True; 1x02: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True
  [PASS] D1   现状板面 pad1 位置/极性标记 (实读板, 不写死) J_DEBUG: pad1@X=142.2 (X_MIN) 标记=False 形状=RECT 属性=SMD; J_UART: pad1@X=18.64 (X_MIN) 标记=False 形状=RECT 属性=SMD
  [PASS] D2   两候选 pad→X 序 (KiCad 变换算, 须互为逆序) J_DEBUG rot90 序=['1', '2', '3', '4'] (pad1@X_MIN) / rot270 序=['4', '3', '2', '1'] (pad1@X_MAX); J_UART rot90 序=['1', '2'] (pad1@X_MIN) / rot270 序=['2', '1'] (pad1@X_MAX)
  [PASS] D3   页同时给出两候选+裁决+落点写死值 
  [PASS] D4   页的 pin1 朝向与 D2 实算一致 
  [PASS] D5   网表 JTAG 四线 SoM 侧端点 (现读, 不写死) JTAG_TCK_SOC→SoC_NC; JTAG_TMS_SOC→SoC_NC; JTAG_TDI_SOC→SoC_NC; JTAG_TDO_SOC→SoC_NC
  [PASS] D6   页 §2 与 SOM_PIN_MAPPING.md 结论不冲突 
  [PASS] D7   板指纹三项未动 (零写板自证) md5=611b869e13518c3c023fb178f91a0075 (期望 611b869e13518c3c023fb178f91a0075) / mtime=2026-11-06 07:07:17.362193413 (期望 2026-11-06 07:07:17.362193413) / size=4940213 (期望 4940213)
  [PASS] D8   证据等级白名单+零挂起措辞+判据/事实分开+零挂链 零挂链: state/gate_check.py 命中 0
=== 9/9 PASS ===
ALL CHECKS PASS
rc=0

### CMD: SoC 侧 JTAG 实读 (自己跑)
$ bash -c grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv | head -10
B11,GPIO2_A2,UART,CAN0_RX_M0/JTAG_TCK_M0/SPI0_CSN1_M1/UART5_RTSN_M2/SAI3_LRCK_M1/DSM_AU
1A8,GPIO2_A3,UART,CAN0_TX_M0/JTAG_TMS_M0/UART5_CTSN_M2/SAI3_SDI_M1/DSM_AUD_RN_M0/SDMMC
U33,GPIO0_D4,UART,JTAG_TCK_M1/UART0_TX_M0/GPIO0_D4_u
V32,GPIO0_D5,UART,JTAG_TMS_M1/UART0_RX_M0/GPIO0_D5_u
rc=0

### CMD: SoM 侧 JTAG 实读 (自己跑)
$ bash -c grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv
0
rc=1

### CMD: 网表 JTAG_TDI_SOC 端点实读
$ bash -c grep -n "JTAG_TDI_SOC" HW/netlist_v1_pins.csv | head -4
333:R_JTAG_TDI.1,JTAG_TDI_SOC,R_JTAG_TDI,1,P8,100Ω ±1%,R,必装,MAIN_PCB,B-19,,,[推算],,[JTAG_TDI] JTAG TDI 串阻 (隔离 SoC 调试脚)
rc=0

### CMD: merge
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-24T04:21:23+08:00)
   产出 814 | 阻塞 43 (高危 33) | 未闭合需求 348 | 冲突 0 | 健康度 red
rc=0

### CMD: gate_check
$ python3 state/gate_check.py
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-24_hw-lead_ISS379_JUART排针换land落位可行性.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-24_mech-lead_ISS377_座体净距判据同源化与座体型号自查.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1152 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    445 条
   sw-lead    335 条
   mech-lead  372 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 118/517  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 239 条, 其中 58 条真对上了别人的需求 key
   hw-lead    被答 43/269 | 我答 82 条(有效 31) | 产出 314 | 阻塞 7
   sw-lead    被答 29/87 | 我答 72 条(有效 6) | 产出 283 | 阻塞 15
   mech-lead  被答 46/161 | 我答 85 条(有效 21) | 产出 202 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 51 条 | **全局 46 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 348 条**
   ✅ 与 merge.py 自对账一致 (等外部 46 / 等总工 348)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 10 个
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']
      iss105_jchg_rfq_release: 发起方 ['main', 'hw-lead']
      iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice: 发起方 ['main', 'mech-lead']
      iss236_boss_v_decision: 发起方 ['main', 'hw-lead']

【Q5 硬指标覆盖】 1/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']
   sw-lead    4/5 类: ['功耗(W)', '镜腿/镜脚厚度(mm)', '端到端延迟(ms)', 'FCCSP 球间距(pitch)']
   mech-lead  1/5 类: ['FCCSP 球间距(pitch)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 10/10 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ✅ 钉板闸⑩ 板侧项全集重跑幂等闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 206 条需求确实还没人答 (等另一个总工)
   · sw-lead: 44 条需求确实还没人答 (等另一个总工)
   · mech-lead: 98 条需求确实还没人答 (等另一个总工)

==========================================================================
rc=0

### CMD: brief 命令存在性守卫
$ python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-378_sw_debug_header_fw_impact.md
rc=0

### CMD: 零挂链自证 (必须 0)
$ bash -c grep -c check_debug_header_fw_impact state/gate_check.py
0
rc=1

### CMD: 四份真源 md5
$ bash -c md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
rc=0

### CMD: 板 mtime/size
$ bash -c stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800 4940213
rc=0
```

### B7-3 签收后的漂移自证（★本趟只准写 B7 + 分片·三件交付物与四份真源一字未动★）

| 文件 | 本趟开工前 md5 | 本趟收工后 md5 | 判定 |
|---|---|---|---|
| `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md`（清单页 · 55,076 B） | `c7bbe75c35f8fa6194f74330b32c52ad` | `c7bbe75c35f8fa6194f74330b32c52ad` | ★**未动** ★ |
| `SW/tools/check_debug_header_fw_impact.py`（新闸 · 37,515 B） | `d78c2446913d5cd3742235d9fd9fef15` | `d78c2446913d5cd3742235d9fd9fef15` | ★**未动** ★ |
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba0732f83a9cf557ba90ab` | ★**未动** ★ |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec9411ac8e8d9e80ee386a` | ★**未动** ★ |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | `5b9993992405904a60ac96a020b375d8` | ★**未动** ★ |
| `HW/PCB/demo_mainboard.kicad_pcb`（板） | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**未动** ★（mtime `2026-11-06 07:07:17.362193413` / size `4940213` 亦未动） |
| `state/gate_check.py`（零挂链 ⇒ 未动） | `5f370bb8cf828473e70ccc5d6412da98` | `5f370bb8cf828473e70ccc5d6412da98` | ★**未动** ★ |

### B7-4 本趟分片写入留证（★只走 `python3 state/frag_write.py` 的原子写 · ★禁止 `open(p,"w")`★）

| 时刻 | `state/fragments/sw.yaml` md5 | 谁写的 |
|---|---|---|
| 03:2x | `639a7610a08e895a52122b1db2f33054` → `21892e983ba60404b1033a248e82fc86` | ★**本单 cont1**（B6 已记） ★ |
| 04:16 | `66f84267bd783e0a5d6a81b065def366` | ★**同槽另一趟 (ISS-370 CONT2) 写 status** ★（★不是本单写的 · 本单只追加不覆盖★） |
| ★**04:2x（本趟）** ★ | `66f84267bd783e0a5d6a81b065def366` → ★**`973ec64fee05f764cd88e565f7723204`** ★ | ★**本趟**（★`tmp/iss378_sbx/frag_status_iss378.py` → `state.frag_write.update_fragment()` 原子写·**只改自己分片**★） ★ |

> ★**本趟分片只写了什么（★一条不落台账★）**: ★**`status.phase=fixing` · `progress_pct=95` · `health=green` · `updated_at=2026-11-24` · `summary`（含本单三件产出物 + 全绿读数 + 零边界自证 + 台账侧 main 已签收 verified 的说明）★ ⇒ ★**artifacts 3 条 / interface_claims 8 条 / needs_from 2 条 均为 cont1 已登记, 本趟零重复登记** ★

### B7-5 本趟未决项（★与 B5 一致 · 不增不减 · 只登记不代拍★）

- ★**要 main 回答一句话**: ★**`J_DEBUG` / `J_UART` 的 pin1 朝向选候选 A（rot90 · ISS-375 建议 · 顺排 pad1@X_MIN）还是候选 B（rot270 · 逆排 pad1@X_MAX）** ★ —— ★**这一句话决定 §1-1 里那 6 条「需改代码」的机器件读数往哪边写** ★
- ★**要 main 裁**: ★**ISS-344 对 `JTAG_TDI` 的「必需 · 板侧不许标 NC」分级, 在「SoM 侧无 JTAG 引出」这个实测事实下走 §3 的 ①改口径 / ②改网表 / ③换 SoM 哪一条（或 ①+③ 组合）** ★ —— ★**代价已在 §3-2 与 B1-6 列全 · 本单只给事实与代价, 不代拍** ★

> ★**本趟明确不做的事（★与 §0-2 同款★）**: ★**不动板** · ★**不动网表 / 脚表 / BOM** · ★**不动固件本体** · ★**不改 ISS-375 的页与闸** · ★**不改 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 正文** · ★**不挂链** · ★**不外发** · ★**不签台账** ★

### B7-6 追加 B7 之后的收尾复测（★04:24~04:25 · 状态机与指纹再确认★）

```text
### CMD: merge rc / gate_check Q1
✅ STATE.yaml 已刷新 (2026-11-24T04:24:20+08:00)
   产出 814 | 阻塞 43 (高危 33) | 未闭合需求 348 | 冲突 0 | 健康度 red
merge rc=0
【Q1 交付齐备率】 18/18 个必填验收块齐全
   sw-lead    6/6  缺: 无   交接单: 2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md
gate rc=0
### 四份真源 + 板 (收工时实测)
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
2026-11-06 07:07:17.362193413 +0800 4940213
### 零挂链 (grep -c)
0
### 分片 (本趟写后 · 未被同槽他趟覆盖)
973ec64fee05f764cd88e565f7723204  state/fragments/sw.yaml   phase=fixing progress=95 health=green
```

> ★**★B7 追加之后, 本单再跑一次 main 的签收验收线 (`state/_apply_20260724_0345_main_sign_iss377_378.py --check-only ISS-378`) ⇒ ★**34 项全绿 · 末行「★全绿★」** ★ ⇒ ★**本趟的追加没有破坏 main 的签收判据** ★
